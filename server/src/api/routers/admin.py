from typing import Dict

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from src.config import settings
from src.game import crash_game
from src.schemas import MaintenanceRequest
from src.api.dependencies.auth import get_admin_key

admin_router = APIRouter(
    prefix="/admin",
    tags=["maintenance"],
    responses={404: {"description": "Not found"}},
)


@admin_router.post("/maintenance")
async def toggle_maintenance(
    request: MaintenanceRequest, admin_key: str = Depends(get_admin_key)
) -> Dict[str, str]:
    if admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    crash_game.maintenance_mode = request.maintenance_mode
    logger.info(f"request.maintenance_mode: {request.maintenance_mode}")
    logger.info(f"crash_game.maintenance_mode: {crash_game.maintenance_mode}")

    return {
        "message": f"Maintenance mode {'enabled' if request.maintenance_mode else 'disabled'}"
    }
