from typing import Optional

from pydantic import BaseModel


class RouteSummary(BaseModel):
    id: str
    name: str
    vehicle_plate_number: str
    estimated_profit: float
    estimated_carbon_kg: float


class DashboardSummary(BaseModel):
    total_routes: int
    total_distance_km: float
    total_expected_revenue: float
    total_estimated_cost: float
    total_estimated_profit: float
    total_estimated_carbon_kg: float
    average_profit_per_route: float
    average_carbon_per_route: float
    most_profitable_route: Optional[RouteSummary] = None
    least_profitable_route: Optional[RouteSummary] = None
    electric_route_count: int
    diesel_route_count: int
    motorcycle_route_count: int
