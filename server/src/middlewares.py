from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from src.enums import GameStatus
from src.game import crash_game
from src.logger import logger

__all__ = ["MaintenanceMiddleware"]


class MaintenanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # print(f"request.url.path: {request.url.path}")
        # print(f"path params: {request.path_params}")
        # print(f"query params: {request.query_params}")

        # Process request
        if (
            crash_game.maintenance_mode
            and crash_game.state != GameStatus.RUNNING
            and request.url.path != "/admin/maintenance"
        ):
            return JSONResponse(
                content={"detail": "Maintenance mode"},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(repr(e))
            raise e

        # Process response=
        # response.headers["Content-Type"] = "Application/json"
        return response
