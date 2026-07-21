from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, require_role
from app.models.user import UserRole
from app.models.vehicle import (
    VehicleCreate,
    VehicleOut,
    VehicleRecommendationRequest,
    VehicleRecommendationResponse,
)
from app.repositories.vehicle_repository import VehicleRepository
from app.services.vehicle_recommendation_service import VehicleRecommendationService
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def get_vehicle_repository() -> VehicleRepository:
    return VehicleRepository()


def get_vehicle_service(repo: VehicleRepository = Depends(get_vehicle_repository)) -> VehicleService:
    return VehicleService(repo)


def get_vehicle_recommendation_service(
    repo: VehicleRepository = Depends(get_vehicle_repository),
) -> VehicleRecommendationService:
    return VehicleRecommendationService(repo)


def _to_vehicle_out(doc: dict) -> VehicleOut:
    return VehicleOut(
        id=str(doc["_id"]),
        plate_number=doc["plate_number"],
        vehicle_type=doc["vehicle_type"],
        capacity_kg=doc["capacity_kg"],
        average_cost_per_km=doc["average_cost_per_km"],
        average_carbon_per_km=doc["average_carbon_per_km"],
        is_active=doc["is_active"],
        created_at=doc["created_at"],
    )


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: VehicleService = Depends(get_vehicle_service),
):
    vehicle_doc = await service.create_vehicle(vehicle_in)
    return _to_vehicle_out(vehicle_doc)


@router.get("", response_model=list[VehicleOut])
async def list_vehicles(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: VehicleService = Depends(get_vehicle_service),
):
    vehicles = await service.list_vehicles()
    return [_to_vehicle_out(v) for v in vehicles]


@router.post("/recommend-best", response_model=VehicleRecommendationResponse)
async def recommend_best_vehicle(
    request_in: VehicleRecommendationRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: VehicleRecommendationService = Depends(get_vehicle_recommendation_service),
):
    return await service.recommend_best(request_in)
