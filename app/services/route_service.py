from datetime import datetime, timezone

from bson.errors import InvalidId
from fastapi import HTTPException, status

from app.models.route import RouteCreate, RouteStatus
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.services.stop_builder import build_stop_docs

# Her durumdan hangi durumlara geçilebileceğini tutan merkezi tablo.
# Yeni bir geçiş kuralı eklemek/değiştirmek istendiğinde sadece burası güncellenir.
_ALLOWED_TRANSITIONS: dict[RouteStatus, set[RouteStatus]] = {
    RouteStatus.PENDING: {RouteStatus.ASSIGNED, RouteStatus.CANCELLED},
    RouteStatus.ASSIGNED: {RouteStatus.IN_PROGRESS, RouteStatus.CANCELLED},
    RouteStatus.IN_PROGRESS: {RouteStatus.DELIVERED, RouteStatus.CANCELLED},
    RouteStatus.DELIVERED: set(),
    RouteStatus.CANCELLED: set(),
}


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
            "expected_revenue": route_in.expected_revenue,
            "estimated_carbon_kg": estimated_carbon_kg,
            "estimated_cost": estimated_cost,
            "estimated_profit": estimated_profit,
            "status": RouteStatus.PENDING.value,
            "assigned_driver_id": route_in.assigned_driver_id,
            "stops": build_stop_docs(route_in.stops),
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
        }
        inserted_id = await self.route_repo.create(route_doc)
        route_doc["_id"] = inserted_id
        return route_doc

    async def assign_driver(self, route_id: str, driver_id: str) -> dict:
        route = await self.get_route_or_404(route_id)
        route = await self.transition_status(route_id, route, RouteStatus.ASSIGNED)
        await self.route_repo.assign_driver(route_id, driver_id)
        route["assigned_driver_id"] = driver_id
        return route

    async def start_route(self, route_id: str, driver_id: str) -> dict:
        route = await self.get_route_or_404(route_id)
        self.ensure_own_route(route, driver_id)
        return await self.transition_status(route_id, route, RouteStatus.IN_PROGRESS)

    async def deliver_route(self, route_id: str, driver_id: str) -> dict:
        route = await self.get_route_or_404(route_id)
        self.ensure_own_route(route, driver_id)
        return await self.transition_status(route_id, route, RouteStatus.DELIVERED)

    async def cancel_route(self, route_id: str) -> dict:
        route = await self.get_route_or_404(route_id)
        return await self.transition_status(route_id, route, RouteStatus.CANCELLED)

    async def get_route_or_404(self, route_id: str) -> dict:
        try:
            route = await self.route_repo.get_by_id(route_id)
        except InvalidId:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz rota ID")
        if not route:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rota bulunamadı")
        return route

    def ensure_own_route(self, route: dict, driver_id: str) -> None:
        if route.get("assigned_driver_id") != driver_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rota size atanmamış")

    async def transition_status(self, route_id: str, route: dict, new_status: RouteStatus) -> dict:
        current_status = RouteStatus(route["status"])
        if new_status not in _ALLOWED_TRANSITIONS[current_status]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{current_status.value}' durumundan '{new_status.value}' durumuna geçilemez",
            )
        await self.route_repo.update_status(route_id, new_status.value)
        route["status"] = new_status.value
        return route
