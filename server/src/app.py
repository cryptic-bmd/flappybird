import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.bot import async_bot
from src.bot.handlers import *
from src.config import settings
from src.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(async_bot.infinity_polling())

    yield

    if sessionmanager.engine_exists:
        # Close the DB connection
        await sessionmanager.close()

    await asyncio.wait_for(asyncio.gather(task), timeout=10)


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
