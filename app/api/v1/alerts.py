from fastapi import APIRouter, Depends

from app.api.v1.routes import get_route_repository
from app.core.deps import CurrentUser, require_role
from app.models.alert import Alert
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(repo: RouteRepository = Depends(get_route_repository)) -> AlertService:
    return AlertService(repo)


@router.get("", response_model=list[Alert])
async def get_alerts(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: AlertService = Depends(get_alert_service),
):
    return await service.get_alerts()
