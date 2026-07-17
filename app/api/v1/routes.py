from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.auth import get_user_repository
from app.api.v1.vehicles import get_vehicle_repository
from app.core.deps import CurrentUser, get_current_user, require_role
from app.models.route import AssignDriverRequest, RouteCreate, RouteOut
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["routes"])


def get_route_repository() -> RouteRepository:
    return RouteRepository()


def get_route_service(
    route_repo: RouteRepository = Depends(get_route_repository),
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
) -> RouteService:
    return RouteService(route_repo, vehicle_repo)


def _to_route_out(doc: dict) -> RouteOut:
    return RouteOut(
        id=str(doc["_id"]),
        origin=doc["origin"],
        destination=doc["destination"],
        distance_km=doc["distance_km"],
        vehicle_id=doc["vehicle_id"],
        vehicle_plate_number=doc["vehicle_plate_number"],
        vehicle_type=doc["vehicle_type"],
        estimated_carbon_kg=doc["estimated_carbon_kg"],
        estimated_cost=doc["estimated_cost"],
        estimated_profit=doc["estimated_profit"],
        assigned_driver_id=doc.get("assigned_driver_id"),
        created_by=doc["created_by"],
        created_at=doc["created_at"],
    )


@router.post("", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_in: RouteCreate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: RouteService = Depends(get_route_service),
):
    route_doc = await service.create_route(route_in, created_by=current_user.id)
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


@router.get("/my-routes", response_model=list[RouteOut])
async def list_my_routes(
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    repo: RouteRepository = Depends(get_route_repository),
):
    routes = await repo.list_by_driver(current_user.id)
    return [_to_route_out(route) for route in routes]


@router.patch("/{route_id}/assign-driver", response_model=RouteOut)
async def assign_driver(
    route_id: str,
    assign_in: AssignDriverRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    route_repo: RouteRepository = Depends(get_route_repository),
    user_repo: UserRepository = Depends(get_user_repository),
):
    try:
        route = await route_repo.get_by_id(route_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz rota ID")
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rota bulunamadı")

    try:
        driver = await user_repo.find_one({"_id": ObjectId(assign_in.driver_id)})
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz sürücü ID")
    if not driver or driver["role"] != UserRole.DRIVER.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçerli bir sürücü değil")

    await route_repo.assign_driver(route_id, assign_in.driver_id)
    route["assigned_driver_id"] = assign_in.driver_id

    return _to_route_out(route)
