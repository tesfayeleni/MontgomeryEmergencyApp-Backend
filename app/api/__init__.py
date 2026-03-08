from app.api.auth import router as auth_router
from app.api.intelligence import router as intelligence_router
from app.api.citizen import router as citizen_router
from app.api.zones import router as zones_router

__all__ = [
    "auth_router",
    "intelligence_router",
    "citizen_router",
    "zones_router",
]
