from typing import Any, Dict

from socketio.async_server import AsyncServer

from src.game import crash_game
from src.utils.cash_out import cash_out


async def cash_out_handler(
    sio: AsyncServer, sid: str, data: Dict[str, Any], user_id: int
):
    await cash_out(sio, sid, data, user_id, crash_game)
