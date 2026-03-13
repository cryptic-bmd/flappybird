import asyncio, time

from socketio.async_server import AsyncServer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import sessionmanager
from src.enums import Events, GameStatus
from src.logger import logger
from src.utils import broadcast


class CrashGame:
    def __init__(self):
        self.state = GameStatus.BETTING

        # Maintenance
        self.maintenance_mode: bool = (
            settings.MAINTENANCE_MODE
        )  # Runtime maintenance flag
        self.m_last_update_ms = 0
        self.m_update_interval_ms = 0

    @property
    def time_in_ms(self) -> int:
        return int((time.time() * 1000))

    async def _run(self, sio: AsyncServer, db: AsyncSession):
        await asyncio.sleep(5)

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
