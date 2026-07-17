from fastapi import APIRouter, Depends

from app.api.v1.routes import get_route_repository
from app.core.deps import CurrentUser, require_role
from app.models.dashboard import DashboardSummary
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_dashboard_service(repo: RouteRepository = Depends(get_route_repository)) -> DashboardService:
    return DashboardService(repo)


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.get_summary()
