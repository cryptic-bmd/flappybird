import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api import routers
from src.bot import async_bot
from src.bot.handlers import *
from src.bot_users import simulate_bot_players
from src.config import settings
from src.database import sessionmanager
from src.game import crash_game
from src.middlewares import *
from src.sio_utils import sio, socketio_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    task1 = asyncio.create_task(crash_game.run(sio))
    await asyncio.sleep(3)
    task2 = asyncio.create_task(simulate_bot_players(sio))
    task3 = asyncio.create_task(async_bot.infinity_polling())

    yield

    if sessionmanager.engine_exists:
        # Close the DB connection
        await sessionmanager.close()

    await asyncio.wait_for(asyncio.gather(task1, task2, task3), timeout=10)


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=[settings.FRONT_BASE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MaintenanceMiddleware)

for router in routers.all_:
    app.include_router(router)

app.mount(settings.SIO_MOUNTPOINT, socketio_app)
