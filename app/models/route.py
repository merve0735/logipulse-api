from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VehicleType(str, Enum):
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    VAN = "van"
    ELECTRIC_VAN = "electric_van"
    TRUCK = "truck"


class RouteCreate(BaseModel):
    origin: str
    destination: str
    distance_km: float = Field(gt=0)
    vehicle_type: VehicleType
    assigned_driver_id: Optional[str] = None


class RouteOut(BaseModel):
    id: str
    origin: str
    destination: str
    distance_km: float
    vehicle_type: VehicleType
    assigned_driver_id: Optional[str] = None
    estimated_carbon_kg: float
    created_by: str
