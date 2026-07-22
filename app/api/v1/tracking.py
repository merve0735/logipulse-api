from fastapi import APIRouter, Depends

from app.api.v1.auth import get_user_repository
from app.api.v1.routes import get_route_repository
from app.core.deps import CurrentUser, require_role
from app.models.tracking import DriverLocationOut, LocationUpdateRequest
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
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
):
    await service.update_my_location(current_user.id, location_in.latitude, location_in.longitude)
    return {"message": "Konum güncellendi."}


@router.get("/drivers", response_model=list[DriverLocationOut])
async def list_driver_locations(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: TrackingService = Depends(get_tracking_service),
):
    return await service.list_driver_locations()
