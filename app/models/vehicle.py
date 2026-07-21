from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FleetVehicleType(str, Enum):
    ELECTRIC_VAN = "electric_van"
    DIESEL_VAN = "diesel_van"
    MOTORCYCLE = "motorcycle"


class VehicleCreate(BaseModel):
    plate_number: str
    vehicle_type: FleetVehicleType
    capacity_kg: float = Field(gt=0)
    average_cost_per_km: float = Field(ge=0)
    average_carbon_per_km: float = Field(ge=0)
    is_active: bool = True


class VehicleOut(BaseModel):
    id: str
    plate_number: str
    vehicle_type: FleetVehicleType
    capacity_kg: float
    average_cost_per_km: float
    average_carbon_per_km: float
    is_active: bool
    created_at: datetime


class VehicleRecommendationRequest(BaseModel):
    distance_km: float = Field(gt=0)
    expected_revenue: float = Field(ge=0)
    package_weight_kg: float = Field(ge=0)


class VehicleRecommendationResult(BaseModel):
    id: str
    plate_number: str
    vehicle_type: FleetVehicleType
    estimated_cost: float
    estimated_carbon_kg: float
    estimated_profit: float
    capacity_suitable: bool
    score: float
    reason: str


class VehicleRecommendationResponse(BaseModel):
    recommended_vehicle: VehicleRecommendationResult
    alternatives: list[VehicleRecommendationResult]
