from loguru import logger

from src.enums import Events, GameStatus
from src.game import crash_game
from src.utils import get_current_user_id_from_token
from src.sio_utils.base import BaseSocket
from src.sio_utils.event_handlers import *


class ExtendedSocket(BaseSocket):
    def __init__(self):
        super().__init__()
        sio = self.sio

        @sio.on(Events.ENTER_ROOM.value)  # type: ignore
        async def enter_room(sid, data):
            logger.info(f"{sid} entered room")
            await self.handle_event(enter_room_handler, sid, data)

        @sio.on(Events.PING.value)  # type: ignore
        async def ping(sid):
            # logger.info(f"{sid} pinged")
            await sio.emit(Events.PONG.value)

        @sio.on(Events.PLACE_BET.value)  # type: ignore
        async def place_bet(sid, data):
            await self.handle_event(place_bet_handler, sid, data)

        @sio.on(Events.CASH_OUT.value)  # type: ignore
        async def cash_out(sid, data):
            await self.handle_event(cash_out_handler, sid, data, inject_db=False)

    async def handle_event(self, async_handler, sid, data, inject_db=True):
        if crash_game.maintenance_mode and crash_game.state != GameStatus.RUNNING:
            await self.sio.emit(
                "error", {"message": "Server is under maintenance"}, to=sid
            )
            return

        user_id = int(get_current_user_id_from_token(data["token"]))
        if not user_id:
            logger.error(f"User with id {user_id} not found")
            return

        await self._handle_event(async_handler, sid, data, user_id, inject_db=inject_db)
