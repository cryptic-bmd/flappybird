import hashlib
from typing import Optional, Sequence

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.enums import GameStatus
from src.models import BetSide, Game, Referral, User
from src.utils import utcnow


async def create_user(
    db: AsyncSession,
    id: int,
    username: Optional[str] = None,
    balance: float = 0,
) -> Optional[User]:

    betside = BetSide(user_id=id, side_name="f")
    user = User(
        id=id,
        username=username,
        balance=balance,
        betsides=[betside],
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
    referrer_id: Optional[int] = None,
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

    if referrer_id:
        await add_referral(db, id, referrer_id, first_name, user)

    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_game(db: AsyncSession, crash_point: float) -> Game:
    while True:
        timestamp = utcnow().isoformat()
        input_string = f"{crash_point}{timestamp}"
        game_hash = hashlib.sha256(input_string.encode("utf-8")).hexdigest()

        result = await db.execute(select(Game).where(Game.hash == game_hash))
        if result.scalars().first() is None:
            break

    db_game = Game(hash=game_hash, crash_point=crash_point)
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game


async def add_referral(
    db: AsyncSession,
    user_id: int,
    referrer_id: int,
    first_name: str,
    user: Optional[User] = None,
) -> Optional[Referral]:
    if not user:
        user = await get_user_by_id(db, user_id)
        if not user:
            return

    referrer = await get_user_by_id(db, referrer_id)
    if not referrer:
        return

    # This prevent self-referral
    if user_id == referrer_id:
        return

    # This prevent double referral
    result = await db.execute(
        select(Referral).where(
            Referral.referred_id == user_id, Referral.referrer_id == referrer_id
        )
    )
    if result.scalars().first():
        return

    referral = Referral(
        referred_id=user_id,
        referrer_id=referrer_id,
        referred_name=first_name,
        referred=user,
        referrer=referrer,
    )
    db.add(referral)
    await db.commit()
    await db.refresh(referral)
    return referral


async def update_user_sid(db: AsyncSession, user: User, sid: str) -> User:
    user.sid = sid
    await db.commit()
    await db.refresh(user)
    return user


async def get_finalized_games(db: AsyncSession, limit: int = 50) -> Sequence[Game]:
    result = await db.execute(
        select(Game)
        .where(Game.status == GameStatus.CRASHED.value)
        .order_by(Game.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_user_by_id_with_betsides(
    db: AsyncSession, user_id: int
) -> Optional[User]:
    result = await db.execute(
        select(User).options(joinedload(User.betsides)).where(User.id == user_id)
    )
    return result.scalars().first()
