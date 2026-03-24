import asyncio
import json
import os
import random
from pathlib import Path
from typing import Dict

from loguru import logger
from socketio import AsyncClient, AsyncServer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routers.auth import auth
from src.config import settings
from src.database import sessionmanager
from src.enums import BetSideType, Events, GameStatus
from src.schemas import BetBase, BotUserDetails, GameState
from src.sio_utils.event_handlers import place_bet_handler

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_BALANCE = 100_000_000_000

bot_user_details_dict: Dict[int, BotUserDetails] = {}

with open(os.path.join(BASE_DIR, "users.json"), "r") as file:
    users_raw = json.load(file)


async def auth_bot_users(db: AsyncSession):
    for user in users_raw:
        bot_user_req = BotUserDetails(
            user_id=user["userID"],
            username=user["username"],
            first_name=user["firstname"],
        )
        token = await auth(
            db,
            user_id=bot_user_req.user_id,
            username=bot_user_req.username,
            first_name=bot_user_req.first_name,
            balance=DEFAULT_BALANCE,
            is_bot=True,
        )
        bot_user_req.token = token
        bot_user_details_dict[bot_user_req.user_id] = bot_user_req


def get_sized_bot_users():
    bot_users = list(bot_user_details_dict.values())
    return random.sample(bot_users, min(random.randint(113, 250), len(bot_users)))


def generate_bet_amount():
    rand_dec = random.randint(1, 9) / 10
    expo = int(
        random.expovariate(random.choice((0.01, 0.03, 0.05, 0.1)))
    )  # 0.08, 0.09, 0.1, 0.11

    r_amt = expo + rand_dec  # positive number (x > 1) with decimals in the tenths
    r_amt2 = expo + random.uniform(0.1, 1)  # positive number with random decimals
    r_amt3 = expo + 1  # positive integer
    r_amt4 = rand_dec  # positive number (0 < x < 1) with decimals in the tenths
    r_amt5 = rand_dec / 10  # positive number (0 < x < 0.1) with decimals (hundredths)

    return min(random.choice((r_amt, r_amt2, r_amt3, r_amt4, r_amt5)), 800)


def generate_target(rand: float = 0):
    if rand in (0, 1) and random.choice((True, True, True, False)):
        rand = random.random()
    return round(min(1.1 + int(random.expovariate(0.2)), 30) + rand, 3)


async def place_bet_for_bot_users(sio: AsyncServer, db: AsyncSession):
    bot_users = get_sized_bot_users()
    sleep_time = settings.BETTING_PHASE_DURATION / len(bot_users)

    for user_details in bot_users:
        data = BetBase(
            token=user_details.token,  # type: ignore
            betAmount=generate_bet_amount(),
            target=generate_target(),
            type=BetSideType.F.value,
            autoCashOut=True,
        )
        err_msg = await place_bet_handler(
            sio=sio,
            sid=None,
            data=data.json_(),
            user_id=user_details.user_id,
            db=db,
        )

        if err_msg == "Betting closed":
            return

        await asyncio.sleep(sleep_time)


async def simulate_bot_players(sio: AsyncServer) -> None:
    async with sessionmanager.session() as db:
        await auth_bot_users(db)
        logger.info("Authed users...")

    client = AsyncClient()

    # Register event handlers
    @client.event
    async def connect():
        logger.info(f"Bot client connected to server")

    @client.event
    async def disconnect():
        logger.info(f"Bot client disconnected from server")

    @client.on(Events.GAME_STATE.value)  # type: ignore
    async def on_game_state(data):
        game_state = GameState(**data)
        if game_state.gameState != GameStatus.BETTING.value:
            return

        async with sessionmanager.session() as db:
            await place_bet_for_bot_users(sio, db)

    @client.on(Events.ERROR.value)  # type: ignore
    async def on_error(data):
        logger.error(f"Bot client ws error: {data}")

    try:
        await client.connect(
            settings.BACK_BASE_SOCKET_URL,
            # socketio_path="/socket.io",
            transports=["websocket"],
            # headers={"User-Agent": "python-socketio-client"},
        )
        await client.wait()
    except Exception as e:
        logger.error(f"Bot client ws error: {repr(e)}")
        logger.exception(repr(e))
    finally:
        try:
            await client.disconnect()
            logger.info(f"Bot client ws closed connection cleanly")
        except Exception as e:
            logger.warning(f"Bot client ws failed to close cleanly: {e}")
