import http
from datetime import datetime, timezone
from typing import Any, Optional

import jwt
from fastapi import HTTPException
from socketio import AsyncServer

from src.config import settings
from src.database import get_db_session


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def inject_db_func(sio, async_handler, *args, **kwargs):
    async for db_session in get_db_session():
        kwargs["db"] = db_session
        await async_handler(sio, *args, **kwargs)


def get_admin_key_from_token(token: str) -> str:
    return get_str_from_token(token)


def get_current_user_id_from_token(token: str) -> str:
    return get_str_from_token(token)


def get_str_from_token(token: str) -> str:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    str_ = payload["subb"]
    if str_ is None:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )
    return str_


async def emit(sio: AsyncServer, event: str, data: Any, to: Optional[str] = None):
    if to:
        await sio.emit(event, data, to=to)


async def broadcast(sio: AsyncServer, event: str, data: Any):
    await sio.emit(event, data)
