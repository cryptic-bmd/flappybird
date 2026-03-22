from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from loguru import logger
from socketio.async_server import AsyncServer

from src.enums import BetStatus, Events, GameStatus
from src.schemas import (
    BetSideSchema,
    BetSideStorage,
    BettedUserInfo,
    BetSchema,
    CashOutBase,
    UserSchema,
    UserStorage,
)
from src.storage import storage
from src.utils import broadcast, emit

if TYPE_CHECKING:
    from src.game import CrashGame

ERROR = Events.ERROR.value


async def cash_out(
    sio: AsyncServer,
    sid: Optional[str],
    data: Dict[str, Any],
    user_id: int,
    crash_game: CrashGame,
) -> bool:
    if user_id in crash_game.invokers:
        logger.error(f"Invoker cannot cash out, user_id: {user_id}")
        await emit(sio, ERROR, {"message": "Cannot cash out"}, to=sid)
        return False

    crash_game.invokers.add(user_id)
    try:
        return await _cash_out(sio, sid, data, user_id, crash_game)
    except Exception as e:
        logger.error(f"Error in _cash_out: {e}")
        await emit(sio, ERROR, {"message": "Internal server error"}, to=sid)
    finally:
        crash_game.invokers.discard(user_id)
    return False


async def _cash_out(
    sio: AsyncServer,
    sid: Optional[str],
    data: Dict[str, Any],
    user_id: int,
    crash_game: CrashGame,
) -> bool:
    if crash_game.state != GameStatus.RUNNING:
        logger.error(f"Not in PLAYING phase, user_id: {user_id}")
        await emit(sio, ERROR, {"message": "Not in PLAYING phase"}, to=sid)
        return False

    cashout_data = CashOutBase(**data)
    # user = await get_user_by_id_with_betsides(db, int(user_id))
    try:
        user_store = UserStorage(**storage.get_data(user_id=user_id))
    except Exception as e:
        logger.error(f"Error in _cash_out: {e}")
        logger.error(f"User store with id {user_id} not found")
        # logger.exception(repr(e))
        await emit(sio, ERROR, {"message": "An error occurred"}, to=sid)
        return False

    # bet = await get_bet(db, crash_game.game_id, user.id)
    if not (bet_store := user_store.bet):
        logger.error(
            "No active bet or already cashed out "
            f"for game with id {crash_game.game_id} "
            f"and user with id {user_store.id}"
        )
        await emit(
            sio, ERROR, {"message": "No active bet or already cashed out"}, to=sid
        )
        return False

    if bet_store.status == BetStatus.CASHED_OUT.value:
        logger.error(f"Already cashed out, user_id: {user_id}")
        await emit(sio, ERROR, {"message": "Already cashed out"}, to=sid)

        if user_id in crash_game.auto_cashout_users:
            del crash_game.auto_cashout_users[user_id]

        return False

    # Update
    multiplier = crash_game.current_multiplier
    winnings = bet_store.amount * multiplier

    if not str(user_id).endswith("00000"):  # A bot user has suffix 00000 in its id
        logger.info(f"winnings: {winnings} for user with id {user_id}")

    # Update bet
    # bet = await update_bet_cashout(db, bet, winnings, multiplier)
    bet_store.cashout_multiplier = multiplier
    bet_store.winnings = winnings
    bet_store.status = BetStatus.CASHED_OUT.value

    # Update user balance
    # betside_data = BetSideSchema(
    #     auto=bet_store.auto_cashout,
    #     betted=False,
    #     cashedOut=True,
    #     cashOutAmount=winnings,
    #     betAmount=bet_store.amount,
    #     target=user_store.betsides[0].target,
    # )
    # user = await update_user_balance(db, user, winnings)
    # user = await update_user_betside(db, user, betside_data=betside_data)
    # if user is None:
    #     logger.error(f"User with id {user_id} and betsides not found")
    #     await emit(sio, ERROR, {"message": "User not found"}, to=sid)
    #     # Do not need to return, cause we can afford to do this

    user_store.bet = bet_store
    user_store.balance += winnings

    betside_store = user_store.betsides[0]
    user_store.betsides[0] = BetSideStorage(
        id=betside_store.id,
        user_id=betside_store.user_id,
        side_name=betside_store.side_name,
        auto=bet_store.auto_cashout,
        betted=False,
        cashed_out=True,
        cashout_amount=winnings,
        bet_amount=bet_store.amount,
        target=betside_store.target,
    )

    if user_id in crash_game.auto_cashout_users:
        if not str(user_id).endswith("00000"):  # A bot user has suffix 00000 in its id
            logger.info(f"Removing user with id {user_id} from auto cashout users")
        del crash_game.auto_cashout_users[user_id]

    storage.save(data=user_store.json_(), user_id=user_id)

    betted_user_state = crash_game.betted_user_states.get(user_store.id)
    if not betted_user_state:
        raise ValueError(f"Betted user state not found, user_id: {user_id}")

    betted_user_state.fBetted = False
    crash_game.betted_user_states[user_store.id] = betted_user_state

    await emit(
        sio,
        Events.MY_BET_STATE.value,
        betted_user_state.json_(),
        to=sid,
    )
    await emit(
        sio,
        Events.MY_FINALIZED_BET.value,
        BetSchema(
            hash=bet_store.hash[:8],
            betAmount=bet_store.amount,
            cashOutMultiplier=bet_store.cashout_multiplier,
            cashedOut=True,
            winnings=bet_store.winnings,
        ).json_(),
        to=sid,
    )
    f = BetSideSchema(
        auto=betside_store.auto,
        betted=betside_store.betted,
        cashedOut=betside_store.cashed_out,
        cashOutAmount=betside_store.cashout_amount,
        betAmount=betside_store.bet_amount,
        target=betside_store.target,
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
    crash_game.update_betted_user_stats(user_store, winnings)
    await broadcast(
        sio,
        Events.BETTED_USER_STATS.value,
        crash_game.betted_user_stats.json_(),
    )
    betted_user_info = BettedUserInfo(
        userID=user_store.id,
        userHash=user_store.hash,
        betAmount=bet_store.amount,
        cashOut=winnings,
        cashedOut=True,
        target=multiplier,
    )
    crash_game.betted_user_infos[user_store.id] = betted_user_info
    await broadcast(
        sio,
        Events.BETTED_USER_INFO.value,
        betted_user_info.json_(),
    )
    return True
