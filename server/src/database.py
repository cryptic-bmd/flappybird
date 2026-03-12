from contextlib import asynccontextmanager
from typing import AsyncIterator, TypeVar

# from cryptography.fernet import Fernet

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings
from src.logger import logger

# cipher = Fernet(ENCRYPTION_KEY)


class Base(AsyncAttrs, DeclarativeBase):
    __name__: str
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}


T = TypeVar("T", bound=Base)


class DatabaseSessionManager:
    def __init__(self, host: str, **engine_kwargs):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    @property
    def engine_exists(self) -> bool:
        return self._engine is not None

    async def close(self):
        if self._engine is None:
            logger.error("DatabaseSessionManager is not initialized")
            return
            # raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(
    settings.SQLALCHEMY_DATABASE_AIO_URI, echo=settings.SQLALCHEMY_ECHO
)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session


async def init_db():
    # async with sessionmanager.connect() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info(f"Database initialized...")
