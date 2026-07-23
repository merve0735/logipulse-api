from fastapi import APIRouter, Depends

from app.api.v1.audit_logs import get_audit_log_service
from app.api.v1.auth import get_user_repository
from app.api.v1.routes import get_route_repository
from app.core.deps import CurrentUser, require_role
from app.models.audit_log import AuditAction
from app.models.tracking import DriverLocationOut, LocationUpdateRequest
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_log_service import AuditLogService
from app.services.tracking_service import TrackingService

router = APIRouter(prefix="/tracking", tags=["tracking"])


def get_tracking_service(
    user_repo: UserRepository = Depends(get_user_repository),
    route_repo: RouteRepository = Depends(get_route_repository),
) -> TrackingService:
    return TrackingService(user_repo, route_repo)


@router.patch("/me/location")
async def update_my_location(
    location_in: LocationUpdateRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: TrackingService = Depends(get_tracking_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    await service.update_my_location(current_user.id, location_in.latitude, location_in.longitude)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.DRIVER_LOCATION_UPDATED,
        description=f"{current_user.email} konumunu güncelledi.",
        entity_type="user",
        entity_id=current_user.id,
        metadata={"latitude": location_in.latitude, "longitude": location_in.longitude},
    )

    return {"message": "Konum güncellendi."}


@router.get("/drivers", response_model=list[DriverLocationOut])
async def list_driver_locations(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: TrackingService = Depends(get_tracking_service),
):
    return await service.list_driver_locations()
