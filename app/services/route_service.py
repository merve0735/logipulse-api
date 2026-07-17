from datetime import datetime, timezone

from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.models.route import RouteCreate
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository


class RouteService:
    def __init__(self, route_repo: RouteRepository, vehicle_repo: VehicleRepository):
        self.route_repo = route_repo
        self.vehicle_repo = vehicle_repo

    async def create_route(self, route_in: RouteCreate, created_by: str) -> dict:
        try:
            vehicle = await self.vehicle_repo.get_by_id(route_in.vehicle_id)
        except InvalidId:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz araç ID")
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Araç bulunamadı")
        if not vehicle["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Bu araç aktif değil, rota oluşturulamaz"
            )

        estimated_cost = round(route_in.distance_km * vehicle["average_cost_per_km"], 2)
        estimated_carbon_kg = round(route_in.distance_km * vehicle["average_carbon_per_km"], 2)
        estimated_profit = round(route_in.expected_revenue - estimated_cost, 2)

        route_doc = {
            "origin": route_in.origin,
            "destination": route_in.destination,
            "distance_km": route_in.distance_km,
            "vehicle_id": route_in.vehicle_id,
            "vehicle_plate_number": vehicle["plate_number"],
            "vehicle_type": vehicle["vehicle_type"],
            "estimated_carbon_kg": estimated_carbon_kg,
            "estimated_cost": estimated_cost,
            "estimated_profit": estimated_profit,
            "assigned_driver_id": route_in.assigned_driver_id,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
        }
        inserted_id = await self.route_repo.create(route_doc)
        route_doc["_id"] = inserted_id
        return route_doc
