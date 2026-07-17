from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.vehicle import FleetVehicleType


class VehicleType(str, Enum):
    # Artık RouteCreate tarafından kullanılmıyor; sadece app/services/carbon/ Strategy Pattern'i için duruyor.
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    VAN = "van"
    ELECTRIC_VAN = "electric_van"
    TRUCK = "truck"


class RouteStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class RouteCreate(BaseModel):
    origin: str
    destination: str
    distance_km: float = Field(gt=0)
    vehicle_id: str
    expected_revenue: float = Field(ge=0)
    assigned_driver_id: Optional[str] = None


class AssignDriverRequest(BaseModel):
    driver_id: str


class RouteOut(BaseModel):
    id: str
    origin: str
    destination: str
    distance_km: float
    vehicle_id: str
    vehicle_plate_number: str
    vehicle_type: FleetVehicleType
    expected_revenue: float
    estimated_carbon_kg: float
    estimated_cost: float
    estimated_profit: float
    status: RouteStatus
    assigned_driver_id: Optional[str] = None
    created_by: str
    created_at: datetime
