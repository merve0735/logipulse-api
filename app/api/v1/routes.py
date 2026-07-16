from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, get_current_user, require_role
from app.models.route import RouteCreate, RouteOut
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.services.carbon.calculator import calculate_carbon_emission

router = APIRouter(prefix="/routes", tags=["routes"])


def get_route_repository() -> RouteRepository:
    return RouteRepository()


def _to_route_out(doc: dict) -> RouteOut:
    return RouteOut(
        id=str(doc["_id"]),
        origin=doc["origin"],
        destination=doc["destination"],
        distance_km=doc["distance_km"],
        vehicle_type=doc["vehicle_type"],
        assigned_driver_id=doc.get("assigned_driver_id"),
        estimated_carbon_kg=doc["estimated_carbon_kg"],
        created_by=doc["created_by"],
    )


@router.post("", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_in: RouteCreate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    repo: RouteRepository = Depends(get_route_repository),
):
    estimated_carbon_kg = calculate_carbon_emission(route_in.vehicle_type, route_in.distance_km)

    route_doc = {
        "origin": route_in.origin,
        "destination": route_in.destination,
        "distance_km": route_in.distance_km,
        "vehicle_type": route_in.vehicle_type.value,
        "assigned_driver_id": route_in.assigned_driver_id,
        "estimated_carbon_kg": estimated_carbon_kg,
        "created_by": current_user.id,
    }
    inserted_id = await repo.create(route_doc)
    route_doc["_id"] = inserted_id

    return _to_route_out(route_doc)


@router.get("", response_model=list[RouteOut])
async def list_routes(
    current_user: CurrentUser = Depends(get_current_user),
    repo: RouteRepository = Depends(get_route_repository),
):
    if current_user.role == UserRole.ADMIN:
        routes = await repo.list_all()
    else:
        routes = await repo.list_by_driver(current_user.id)

    return [_to_route_out(route) for route in routes]
