from typing import Any, Dict, Optional

from loguru import logger
from socketio.async_server import AsyncServer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.crud import create_bet, get_user_by_id_with_betsides
from src.enums import Events, GameStatus
from src.game import crash_game
from src.schemas import (
    BetBase,
    BetSideSchema,
    BetSideStorage,
    BetState,
    BetStorage,
    BettedUserInfo,
    UserSchema,
    UserStorage,
)
from src.storage import storage
from src.utils import broadcast, emit

ERROR = Events.ERROR.value


async def place_bet_handler(
    sio: AsyncServer,
    sid: Optional[str],
    data: Dict[str, Any],
    user_id: int,
    db: AsyncSession,
) -> Optional[str]:
    if user_id in crash_game.invokers:
        err_msg = f"Invoker {user_id} cannot place bet"
        logger.error(err_msg)
        await emit(sio, ERROR, {"message": "Cannot place bet"}, to=sid)
        return err_msg

    crash_game.invokers.add(user_id)
    try:
        await _place_bet(sio, sid, data, user_id, db)
    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        await emit(sio, ERROR, {"message": "Failed to place bet"}, to=sid)
        return str(e)
    finally:
        crash_game.invokers.discard(user_id)


async def _place_bet(
    sio: AsyncServer,
    sid: Optional[str],
    data: Dict[str, Any],
    user_id: int,
    db: AsyncSession,
) -> Optional[str]:
    # Implementation of the bet placement logic
    if crash_game.state != GameStatus.BETTING:
        err_msg = "Betting closed"
        if sid:
            logger.error(f"{err_msg}, user_id: {user_id}")
        await emit(sio, ERROR, {"message": err_msg}, to=sid)
        return err_msg

    # logger.info(f"place_bet_handler called with data: {data}")
    bet_data = BetBase(**data)

    if bet_data.betAmount <= 0 or bet_data.betAmount > settings.MAX_BET:
        err_msg = "Invalid bet amount"
        logger.error(f"{err_msg}, user_id: {user_id}")
        await emit(sio, ERROR, {"message": err_msg}, to=sid)
        return err_msg

    # No UserStorage validation here cause data might not be present
    # Just a quick check if user already has an active bet
    user_data = storage.get_data(user_id=user_id)
    if user_data and (bet_ := user_data["bet"]):
        if bet_["game_id"] != crash_game.game_id:
            err_msg = "User has an active bet in a different game"
            logger.error(f"{err_msg}, user_id: {user_id}")
            storage.reset_data(user_id=user_id)
            await emit(sio, ERROR, {"message": "An error occurred"}, to=sid)
            return err_msg

        err_msg = "User already has an active bet"
        logger.error(f"{err_msg}, user_id: {user_id}")
        await emit(sio, ERROR, {"message": "You already have an active bet"}, to=sid)
        return err_msg

    # user_id = get_current_user_id_from_token(data["token"])
    user = await get_user_by_id_with_betsides(db, user_id)
    if not user:
        err_msg = f"User not found"
        logger.error(f"{err_msg}, user_id: {user_id}")
        await emit(sio, ERROR, {"message": "An error occurred"}, to=sid)
        return err_msg

    if user.balance < bet_data.betAmount:
        err_msg = f"User has insufficient balance"
        logger.error(f"{err_msg}, user_id: {user_id}")
        await emit(sio, ERROR, {"message": "Insufficient balance"}, to=sid)
        return err_msg

    user_store = UserStorage(
        id=user.id,
        hash=user.hash or "",
        sid=sid,
        username=user.username or "",
        balance=user.balance,
        is_bot=False,  # user.is_bot or False,
        betsides=[BetSideStorage(**betside.__dict__) for betside in user.betsides],
        bet=None,
    )
    # logger.info(f"user_store: {user_store}")

    if user_store.sid != sid:
        # user = await update_user_sid(db, user_store, sid=sid)
        user_store.sid = sid

    # bet = await get_bet(db, crash_game.game_id, user.id)

    # Update user balance and betside
    # user_store = await update_user_balance(db, user_store, -bet_data.betAmount)
    # user = await update_user_betside(
    #     db,
    #     user,
    #     betside_data=BetSideSchema(
    #         auto=bet_data.autoCashOut,
    #         betted=True,
    #         cashedOut=False,
    #         cashOutAmount=0,
    #         betAmount=bet_data.betAmount,
    #         target=bet_data.target,
    #     ),
    # )
    user_store.balance -= bet_data.betAmount

    betside_store = user_store.betsides[0]
    user_store.betsides[0] = BetSideStorage(
        id=betside_store.id,
        user_id=betside_store.user_id,
        side_name=betside_store.side_name,
        auto=bet_data.autoCashOut,
        betted=True,
        cashed_out=False,
        cashout_amount=0,
        bet_amount=bet_data.betAmount,
        target=bet_data.target,
    )

    auto_cashout = False  # bet_data.autoCashOut
    bet = await create_bet(
        db=db,
        user_id=user_store.id,
        game_id=crash_game.game_id,
        amount=bet_data.betAmount,
        auto_cashout=auto_cashout,
        target=bet_data.target,
        # refresh_with_user=True,
    )
    if bet is None:
        err_msg = "Failed to create bet"
        logger.error(f"{err_msg}, user_id: {user_id}")
        await emit(sio, ERROR, {"message": err_msg}, to=sid)
        return err_msg

    bet_store = BetStorage(**bet.__dict__)
    user_store.bet = bet_store
    storage.save(data=user_store.json_(), user_id=user_id)

    # Setup auto cashout
    if bet_store.target > 0:
        crash_game.auto_cashout_users[user_id] = user_store

    betted_user_state = crash_game.betted_user_states.get(user_store.id)
    if betted_user_state:
        raise ValueError("User already has an active bet (fatal error)")

    betted_user_state = BetState(
        fBetted=True,
        sBetted=False,
    )
    crash_game.betted_user_states[user_store.id] = betted_user_state

    await emit(
        sio,
        Events.MY_BET_STATE.value,
        betted_user_state.json_(),
        to=sid,
    )

    betside = user_store.betsides[0]
    f = BetSideSchema(
        auto=betside.auto,
        betted=betside.betted,
        cashedOut=betside.cashed_out,
        cashOutAmount=betside.cashout_amount,
        betAmount=betside.bet_amount,
        target=betside.target,
    )
    await emit(
        sio,
        Events.MY_INFO.value,
        UserSchema(
            id=user_store.id,
            username=user_store.username,
            img=user_store.username,
            balance=user_store.balance,
            f=f,
            s=BetSideSchema(),
        ).json_(),
        to=sid,
    )
    crash_game.betted_user_stats.noOfBets += 1
    crash_game.betted_user_stats.totalBetAmount += bet_store.amount
    await broadcast(
        sio,
        Events.BETTED_USER_STATS.value,
        crash_game.betted_user_stats.json_(),
    )
    betted_user_info = BettedUserInfo(
        userID=user_store.id,
        userHash=user_store.hash,
        betAmount=bet_data.betAmount,
        cashOut=None,
        cashedOut=False,
        target=bet_data.target,
    )
    crash_game.betted_user_infos[user_store.id] = betted_user_info
    await broadcast(
        sio,
        Events.BETTED_USER_INFO.value,
        betted_user_info.json_(),
    )
