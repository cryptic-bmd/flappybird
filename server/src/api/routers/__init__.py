from src.api.routers.auth import auth_router
from src.api.routers.admin import admin_router

all_ = [
    admin_router,
    auth_router,
]
