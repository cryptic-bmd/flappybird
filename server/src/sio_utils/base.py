import socketio

from loguru import logger

from src.config import settings
from src.utils import inject_db_func


class BaseSocket:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode=settings.SIO_MODE,
            cors_allowed_origins=settings.SIO_CORS,
            logger=False,
            engineio_logger=False,
        )

        # For ease of use and referencing
        sio = self.sio

        # Need to call this in FastAPI
        self.socketio_app = socketio.ASGIApp(socketio_server=sio)

        @sio.event
        async def connect(sid, env):
            logger.info(f"{sid} connected")

        @sio.event
        async def disconnect(sid):
            logger.info(f"{sid}: disconnected")

        @sio.event
        async def echo(sid, data):
            logger.info(f"BaseSocket heard session id <{sid}> say: '{data}'")

    async def _handle_event(self, async_handler, *args, inject_db=True, **kwargs):
        try:
            if inject_db:
                await inject_db_func(self.sio, async_handler, *args, **kwargs)
            else:
                await async_handler(self.sio, *args, **kwargs)
        except Exception as e:
            logger.exception(repr(e))
