from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.route import RouteOut, RouteStatus
from app.models.vehicle import FleetVehicleType


class RouteSortField(str, Enum):
    CREATED_AT = "created_at"
    DISTANCE_KM = "distance_km"
    ESTIMATED_PROFIT = "estimated_profit"
    ESTIMATED_CARBON_KG = "estimated_carbon_kg"
    STATUS = "status"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class RouteFilter(BaseModel):
    status: Optional[RouteStatus] = None
    vehicle_type: Optional[FleetVehicleType] = None
    vehicle_id: Optional[str] = None
    assigned_driver_id: Optional[str] = None
    min_profit: Optional[float] = None
    max_profit: Optional[float] = None
    min_carbon: Optional[float] = None
    max_carbon: Optional[float] = None
    search: Optional[str] = None
    sort_by: RouteSortField = RouteSortField.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedRoutes(BaseModel):
    items: list[RouteOut]
    total: int
    limit: int
    offset: int
    has_more: bool
