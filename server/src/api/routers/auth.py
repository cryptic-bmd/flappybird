from typing import Dict, Optional

import jwt
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from telegram_webapp_auth.auth import WebAppUser

from src.config import settings
from src.crud import get_or_create_user
from src.api.dependencies.auth import get_current_telegram_user
from src.api.dependencies.core import DBSessionDep

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


async def auth(
    db: AsyncSession,
    user_id: int,
    first_name: str,
    username: Optional[str] = None,
    balance: float = 0,
    is_bot: bool = False,
) -> str:
    user = await get_or_create_user(
        db=db,
        id=user_id,
        first_name=first_name,
        username=username or first_name,
        balance=balance,
        is_bot=is_bot,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = jwt.encode(
        {"subb": str(user.id)}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return token


@auth_router.post("/telegram")
async def auth_telegram(
    db: DBSessionDep,
    telegram_user: WebAppUser = Depends(get_current_telegram_user),
) -> Dict[str, str]:
    token = await auth(
        db=db,
        user_id=telegram_user.id,
        first_name=telegram_user.first_name,
        username=telegram_user.username,
    )
    return {"token": token}
