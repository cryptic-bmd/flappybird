import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.bot import async_bot
from src.bot.handlers import *
from src.config import settings
from src.database import sessionmanager
from src.game import crash_game
from src.sio_utils import sio, socketio_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    task1 = asyncio.create_task(crash_game.run(sio))
    await asyncio.sleep(3)
    task2 = asyncio.create_task(async_bot.infinity_polling())

    yield

    if sessionmanager.engine_exists:
        # Close the DB connection
        await sessionmanager.close()

    await asyncio.wait_for(asyncio.gather(task1, task2), timeout=10)


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.mount(settings.SIO_MOUNTPOINT, socketio_app)
