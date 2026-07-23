from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.audit_logs import get_audit_log_service
from app.api.v1.auth import get_user_repository
from app.api.v1.vehicles import get_vehicle_repository
from app.core.deps import CurrentUser, get_current_user, require_role
from app.models.audit_log import AuditAction
from app.models.route import AssignDriverRequest, RouteCreate, RouteOut, RouteStatus
from app.models.route_filter import PaginatedRoutes, RouteFilter, RouteSortField, SortOrder
from app.models.stop import StopDeliverRequest, StopFailRequest, StopOut
from app.models.user import UserRole
from app.models.vehicle import FleetVehicleType
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.services.audit_log_service import AuditLogService
from app.services.route_filter_builder import build_route_query
from app.services.route_rules import route_name
from app.services.route_service import RouteService
from app.services.stop_service import StopService

router = APIRouter(prefix="/routes", tags=["routes"])


def get_route_repository() -> RouteRepository:
    return RouteRepository()


def get_route_service(
    route_repo: RouteRepository = Depends(get_route_repository),
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
) -> RouteService:
    return RouteService(route_repo, vehicle_repo)


def get_stop_service(
    route_repo: RouteRepository = Depends(get_route_repository),
    route_service: RouteService = Depends(get_route_service),
) -> StopService:
    return StopService(route_repo, route_service)


def _to_stop_out(doc: dict) -> StopOut:
    return StopOut(
        id=doc["id"],
        sequence_number=doc["sequence_number"],
        customer_name=doc["customer_name"],
        customer_phone=doc.get("customer_phone"),
        address=doc["address"],
        latitude=doc.get("latitude"),
        longitude=doc.get("longitude"),
        package_weight_kg=doc.get("package_weight_kg"),
        delivery_note=doc.get("delivery_note"),
        status=doc["status"],
        failure_reason=doc.get("failure_reason"),
        delivered_at=doc.get("delivered_at"),
        proof_of_delivery=doc.get("proof_of_delivery"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


def to_route_out(doc: dict) -> RouteOut:
    return RouteOut(
        id=str(doc["_id"]),
        origin=doc["origin"],
        destination=doc["destination"],
        distance_km=doc["distance_km"],
        vehicle_id=doc["vehicle_id"],
        vehicle_plate_number=doc["vehicle_plate_number"],
        vehicle_type=doc["vehicle_type"],
        expected_revenue=doc["expected_revenue"],
        estimated_carbon_kg=doc["estimated_carbon_kg"],
        estimated_cost=doc["estimated_cost"],
        estimated_profit=doc["estimated_profit"],
        status=doc["status"],
        assigned_driver_id=doc.get("assigned_driver_id"),
        stops=[_to_stop_out(s) for s in doc.get("stops", [])],
        created_by=doc["created_by"],
        created_at=doc["created_at"],
    )


@router.post("", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_in: RouteCreate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: RouteService = Depends(get_route_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.create_route(route_in, created_by=current_user.id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.ROUTE_CREATED,
        description=f"Yeni rota oluşturuldu: {route_name(route_doc)}.",
        entity_type="route",
        entity_id=str(route_doc["_id"]),
    )

    return to_route_out(route_doc)


async def _list_routes_paginated(
    repo: RouteRepository, filters: RouteFilter, driver_scope: Optional[str]
) -> PaginatedRoutes:
    query = build_route_query(filters, driver_id=driver_scope)
    sort_direction = 1 if filters.sort_order == SortOrder.ASC else -1
    items, total = await repo.find_filtered(
        query, filters.sort_by.value, sort_direction, filters.limit, filters.offset
    )
    return PaginatedRoutes(
        items=[to_route_out(route) for route in items],
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        has_more=(filters.offset + len(items)) < total,
    )


@router.get("", response_model=PaginatedRoutes)
async def list_routes(
    current_user: CurrentUser = Depends(get_current_user),
    repo: RouteRepository = Depends(get_route_repository),
    status_filter: Optional[RouteStatus] = Query(default=None, alias="status"),
    vehicle_type: Optional[FleetVehicleType] = None,
    vehicle_id: Optional[str] = None,
    assigned_driver_id: Optional[str] = None,
    min_profit: Optional[float] = None,
    max_profit: Optional[float] = None,
    min_carbon: Optional[float] = None,
    max_carbon: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: RouteSortField = RouteSortField.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    is_admin = current_user.role == UserRole.ADMIN
    filters = RouteFilter(
        status=status_filter,
        vehicle_type=vehicle_type,
        vehicle_id=vehicle_id if is_admin else None,
        assigned_driver_id=assigned_driver_id if is_admin else None,
        min_profit=min_profit,
        max_profit=max_profit,
        min_carbon=min_carbon,
        max_carbon=max_carbon,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    driver_scope = None if is_admin else current_user.id
    return await _list_routes_paginated(repo, filters, driver_scope)


@router.get("/my-routes", response_model=PaginatedRoutes)
async def list_my_routes(
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    repo: RouteRepository = Depends(get_route_repository),
    status_filter: Optional[RouteStatus] = Query(default=None, alias="status"),
    vehicle_type: Optional[FleetVehicleType] = None,
    min_profit: Optional[float] = None,
    max_profit: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: RouteSortField = RouteSortField.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    filters = RouteFilter(
        status=status_filter,
        vehicle_type=vehicle_type,
        min_profit=min_profit,
        max_profit=max_profit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return await _list_routes_paginated(repo, filters, current_user.id)


@router.patch("/{route_id}/assign-driver", response_model=RouteOut)
async def assign_driver(
    route_id: str,
    assign_in: AssignDriverRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    user_repo: UserRepository = Depends(get_user_repository),
    service: RouteService = Depends(get_route_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    try:
        driver = await user_repo.find_one({"_id": ObjectId(assign_in.driver_id)})
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz sürücü ID")
    if not driver or driver["role"] != UserRole.DRIVER.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçerli bir sürücü değil")

    route_doc = await service.assign_driver(route_id, assign_in.driver_id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.ROUTE_ASSIGNED,
        description=f"{route_name(route_doc)} rotası sürücüye atandı: {driver['email']}.",
        entity_type="route",
        entity_id=route_id,
        metadata={"driver_id": assign_in.driver_id, "driver_email": driver["email"]},
    )

    return to_route_out(route_doc)


@router.patch("/{route_id}/start", response_model=RouteOut)
async def start_route(
    route_id: str,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: RouteService = Depends(get_route_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.start_route(route_id, driver_id=current_user.id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.ROUTE_STARTED,
        description=f"{route_name(route_doc)} rotası başlatıldı.",
        entity_type="route",
        entity_id=route_id,
    )

    return to_route_out(route_doc)


@router.patch("/{route_id}/deliver", response_model=RouteOut)
async def deliver_route(
    route_id: str,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: RouteService = Depends(get_route_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.deliver_route(route_id, driver_id=current_user.id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.ROUTE_DELIVERED,
        description=f"{route_name(route_doc)} rotası teslim edildi.",
        entity_type="route",
        entity_id=route_id,
    )

    return to_route_out(route_doc)


@router.patch("/{route_id}/cancel", response_model=RouteOut)
async def cancel_route(
    route_id: str,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: RouteService = Depends(get_route_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.cancel_route(route_id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.ROUTE_CANCELLED,
        description=f"{route_name(route_doc)} rotası iptal edildi.",
        entity_type="route",
        entity_id=route_id,
    )

    return to_route_out(route_doc)


@router.get("/{route_id}/stops", response_model=list[StopOut])
async def list_route_stops(
    route_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: StopService = Depends(get_stop_service),
):
    stops = await service.list_stops(route_id, current_user.id, current_user.role == UserRole.ADMIN)
    return [_to_stop_out(s) for s in stops]


@router.patch("/{route_id}/stops/{stop_id}/deliver", response_model=RouteOut)
async def deliver_stop(
    route_id: str,
    stop_id: str,
    proof_in: StopDeliverRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: StopService = Depends(get_stop_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.deliver_stop(route_id, stop_id, current_user.id, proof_in)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.STOP_DELIVERED,
        description=f"Durak teslim edildi olarak işaretlendi: {proof_in.recipient_name}.",
        entity_type="stop",
        entity_id=stop_id,
        metadata={"route_id": route_id, "recipient_name": proof_in.recipient_name},
    )

    return to_route_out(route_doc)


@router.patch("/{route_id}/stops/{stop_id}/fail", response_model=RouteOut)
async def fail_stop(
    route_id: str,
    stop_id: str,
    fail_in: StopFailRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: StopService = Depends(get_stop_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.fail_stop(route_id, stop_id, current_user.id, fail_in.failure_reason)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.STOP_FAILED,
        description=f"Durak başarısız olarak işaretlendi: {fail_in.failure_reason}.",
        entity_type="stop",
        entity_id=stop_id,
        metadata={"route_id": route_id, "failure_reason": fail_in.failure_reason},
    )

    return to_route_out(route_doc)


@router.patch("/{route_id}/stops/{stop_id}/skip", response_model=RouteOut)
async def skip_stop(
    route_id: str,
    stop_id: str,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: StopService = Depends(get_stop_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.skip_stop(route_id, stop_id, current_user.id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.STOP_SKIPPED,
        description="Durak atlandı.",
        entity_type="stop",
        entity_id=stop_id,
        metadata={"route_id": route_id},
    )

    return to_route_out(route_doc)


@router.patch("/{route_id}/stops/{stop_id}/schedule-retry", response_model=RouteOut)
async def schedule_retry_stop(
    route_id: str,
    stop_id: str,
    current_user: CurrentUser = Depends(require_role(UserRole.DRIVER)),
    service: StopService = Depends(get_stop_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    route_doc = await service.schedule_retry_stop(route_id, stop_id, current_user.id)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.STOP_RETRY_SCHEDULED,
        description="Durak için tekrar deneme planlandı.",
        entity_type="stop",
        entity_id=stop_id,
        metadata={"route_id": route_id},
    )

    return to_route_out(route_doc)
