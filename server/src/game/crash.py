import asyncio, random, time
from typing import Dict, Tuple

from socketio.async_server import AsyncServer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.crud import create_game
from src.database import sessionmanager
from src.enums import Events, GameStatus
from src.logger import logger
from src.schemas import BettedUserInfo, BettedUserStats, GameState
from src.utils import broadcast


class CrashGame:
    def __init__(self):
        self.state = GameStatus.BETTING
        self.game_id = 0
        self.current_multiplier = 1.0
        self.crash_point: float = 0
        self.next_crash_point: float = 0
        self.start_time_in_ms: int = 0

        self.betted_user_infos: Dict[int, BettedUserInfo] = {}
        self.betted_user_stats = BettedUserStats()

        # Maintenance
        self.maintenance_mode: bool = (
            settings.MAINTENANCE_MODE
        )  # Runtime maintenance flag
        self.m_last_update_ms = 0
        self.m_update_interval_ms = 0

    @property
    def time_in_ms(self) -> int:
        return int((time.time() * 1000))

    @property
    def elapsed_time_ms(self) -> int:
        return self.time_in_ms - self.start_time_in_ms

    def generate_crash_point(self) -> Tuple[float, float]:
        r = lambda: random.random()

        def cp():
            # Applies instant bust
            if r() < settings.HOUSE_EDGE:
                return 1.00
            raw = 1 / (1 - r())
            return round(max(1.0, raw * settings.PAYOUT_FACTOR), 2)

        crash_point = cp() if self.next_crash_point == 0 else self.next_crash_point
        next_crash_point = cp()

        # logger.info(f"\nRandom number: {round(r, 2)}")
        logger.info(f"Crash point: {crash_point}")
        logger.info(f"Next crash point: {next_crash_point}\n")

        return crash_point, next_crash_point

    async def _run(self, sio: AsyncServer, db: AsyncSession):
        # Main game loop
        self.crash_point, self.next_crash_point = self.generate_crash_point()
        game = await create_game(db, self.crash_point)
        self.game_id = game.id

        logger.info(f"\nGame {game.id} started")

        # BETTING phase - Users can now place their bets (in BETTING_PHASE_DURATION seconds)
        self.state = GameStatus.BETTING
        self.current_multiplier = 1.0
        self.start_time_in_ms = self.time_in_ms

        self.betted_user_infos = {}
        self.betted_user_states = {}

        self.betted_user_stats = BettedUserStats()
        await broadcast(
            sio,
            Events.BETTED_USER_STATS.value,
            self.betted_user_stats.json_(),
        )
        await broadcast(
            sio,
            Events.GAME_STATE.value,
            GameState(
                gameState=self.state.value,
                currentMultiplier=self.current_multiplier,
                serverTimeElapsed=self.elapsed_time_ms,
            ).json_(),
        )
        await asyncio.sleep(settings.BETTING_PHASE_DURATION)
        ...

    async def run(self, sio: AsyncServer):
        while True:
            try:
                in_maintenance = await self.check_maintenance(sio)
                if in_maintenance:
                    continue

                async with sessionmanager.session() as db:
                    await self._run(sio, db)
            except Exception as e:
                logger.error(repr(e))
                logger.exception(repr(e))
                break

    async def check_maintenance(self, sio: AsyncServer) -> bool:
        # Check for maintenance mode first before starting a new game session
        if self.maintenance_mode:
            logger.info("Maintenance mode enabled")
            if (self.time_in_ms - self.m_last_update_ms) < self.m_update_interval_ms:
                await asyncio.sleep(5)
                return True
            # In maintenance mode, pause game loop and notify clients
            await broadcast(
                sio,
                Events.MAINTENANCE.value,
                {"message": "Server is under maintenance. Betting is disabled."},
            )
            self.m_update_interval_ms += min(self.m_update_interval_ms + 5000, 60000)
            self.m_last_update_ms = self.time_in_ms
            await asyncio.sleep(5)
            return True
        else:
            self.m_update_interval_ms = 0
            self.m_last_update_ms = 0

        return False
