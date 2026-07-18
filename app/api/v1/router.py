from fastapi import APIRouter

from app.api.v1.alerts import router as alerts_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.routes import router as routes_router
from app.api.v1.users import router as users_router
from app.api.v1.vehicles import router as vehicles_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(routes_router)
api_router.include_router(vehicles_router)
api_router.include_router(users_router)
api_router.include_router(dashboard_router)
api_router.include_router(alerts_router)
api_router.include_router(recommendations_router)
