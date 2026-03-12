from typing import Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models import User


async def create_user(
    db: AsyncSession,
    id: int,
    username: Optional[str] = None,
    balance: float = 0,
) -> Optional[User]:

    user = User(
        id=id,
        username=username,
        balance=balance,
    )

    db.add(user)
    await db.commit()
    return user


async def get_or_create_user(
    db: AsyncSession,
    id: int,
    first_name: str,
    username: Optional[str] = None,
    balance: float = 0,
) -> Optional[User]:
    user = await get_user_by_id(db, id)
    if user:
        if user.username is None or username and user.username != username:
            user.username = username or first_name
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    user = await create_user(
        db=db,
        id=id,
        username=username or first_name,
        balance=balance,
    )
    if not user:
        logger.error(f"User does not exist: {id}")
        raise ValueError("User does not exist")

    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
