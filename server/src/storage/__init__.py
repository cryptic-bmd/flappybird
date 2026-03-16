from src.config import settings
from src.storage.redis_storage import StateRedisStorage
from src.storage.base_storage import StateDataContext, StateStorageBase


__all__ = [
    "StateStorageBase",
    "StateDataContext",
    "StateRedisStorage",
]

storage = StateRedisStorage(redis_url=settings.REDIS_URL)
