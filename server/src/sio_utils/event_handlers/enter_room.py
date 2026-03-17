import asyncio, time

from loguru import logger
from socketio.async_server import AsyncServer
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import (
    get_finalized_games,
    get_user_by_id_with_betsides,
    update_user_sid,
)
from src.enums import Events
from src.game import crash_game
from src.schemas import BetSideSchema, GameHistory, GameState, UserSchema
from src.storage import storage

ERROR = Events.ERROR.value


async def enter_room_handler(
    sio: AsyncServer, sid, data, user_id: int, db: AsyncSession
):
    while user_id in crash_game.invokers:
        await asyncio.sleep(3)
        crash_game.invokers.discard(user_id)

    crash_game.invokers.add(user_id)
    try:
        await _enter_room_handler(sio, sid, data, user_id, db)
    except Exception as e:
        logger.exception(repr(e))
        logger.error(f"Error in _enter_room_handler: {e}")
        await sio.emit(ERROR, {"message": "An error occurred"}, to=sid)
    finally:
        crash_game.invokers.discard(user_id)


async def _enter_room_handler(
    sio: AsyncServer, sid, data, user_id: int, db: AsyncSession
):
    user = await get_user_by_id_with_betsides(db, user_id)
    if user is None:
        # logger.info(f"Creating new user with id {user_id}")
        # user = await create_user(db, id=user_id, sid=sid)

        logger.error(f"User with id {user_id} not found")
        await sio.emit(ERROR, {"message": "User not found"}, to=sid)
        crash_game.invokers.discard(user_id)
        return
    else:
        logger.info(f"Updating user {user_id}'s sid from {user.sid} to {sid}")
        user = await update_user_sid(db, user, sid=sid)

    betted_user_state = crash_game.betted_user_states.get(user.id)
    if betted_user_state:
        await sio.emit(
            Events.MY_BET_STATE.value,
            betted_user_state.json_(),
            to=sid,
        )

    user_data = storage.get_data(user_id=user_id)
    balance = user_data.get("balance")
    # logger.info(f"balance: {balance}")
    betside = user.betsides[0]
    # logger.info(f"betside: {betside.__dict__}")
    f = BetSideSchema(
        auto=betside.auto,
        betted=betside.betted,
        cashedOut=betside.cashed_out,
        cashOutAmount=betside.cashout_amount,
        betAmount=betside.bet_amount,
        target=betside.target,
    )
    await sio.emit(
        Events.MY_INFO.value,
        UserSchema(
            id=user.id,
            username=user.username,
            img=user.username,
            balance=balance or user.balance,
            f=f,
            s=BetSideSchema(),
        ).json_(),
        to=sid,
    )
    await sio.emit(
        Events.GAME_STATE.value,
        GameState(
            gameState=crash_game.state.value,
            currentMultiplier=crash_game.current_multiplier,
            serverTimeElapsed=int(time.time() * 1000) - crash_game.start_time_in_ms,
        ).json_(),
        to=sid,
    )
    await sio.emit(
        Events.BETTED_USER_STATS.value,
        crash_game.betted_user_stats.json_(),
        to=sid,
    )
    await sio.emit(
        Events.BETTED_USER_INFOS.value,
        [info.json_() for info in crash_game.betted_user_infos.values()],
        to=sid,
    )
    await sio.emit(
        Events.GAME_HISTORY.value,
        [
            GameHistory(
                gameID=game.id, gameHash=game.hash, crashPoint=game.crash_point  # type: ignore
            ).json_()
            for game in await get_finalized_games(db)
        ],
        to=sid,
    )
