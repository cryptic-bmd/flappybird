from decimal import Decimal
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from src.bot.async_bot import bot_username
from src.crud import get_bets_by_user_id, get_user_by_id
from src.schemas import BetSchema, UserSchema
from src.storage import storage
from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.core import DBSessionDep

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/info")
async def get_user(
    db: DBSessionDep, user_id: str = Depends(get_current_user_id)
) -> UserSchema:
    user_id_int = int(user_id)
    user = await get_user_by_id(db, user_id_int)
    if not user:
        logger.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    user_data = storage.get_data(user_id=user_id_int)
    # Getting the total balance from here means user is in a game session
    # and that there is a high chance balance has changed within the session
    balance = user_data.get("balance")
    # logger.info(f"balance: {balance}")

    total_balance = balance or user.balance
    return UserSchema(
        id=user.id,
        balance=total_balance,
        availableBalance=float(
            Decimal(str(total_balance)) - Decimal(str(user.unwagered_balance))
        ),
        referralLink=f"{bot_username}?start=r-{user_id}",  # prefix will be added in the frontend
    )


@user_router.get("/bets")
async def get_bets(
    db: DBSessionDep, user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    logger.info(f"Getting user bets with id {user_id}")
    bets = await get_bets_by_user_id(db, int(user_id))
    if not bets:
        logger.error(f"User bets with id {user_id} not found")
        return []

    return [
        BetSchema(
            hash=bet.hash[:8],  # type: ignore
            betAmount=bet.amount,
            cashOutMultiplier=bet.cashout_multiplier,
            winnings=bet.winnings,
        ).json_()
        for bet in bets
    ]
