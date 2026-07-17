from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.vehicle import VehicleCreate
from app.repositories.vehicle_repository import VehicleRepository


class VehicleService:
    def __init__(self, repo: VehicleRepository):
        self.repo = repo

    async def create_vehicle(self, vehicle_in: VehicleCreate) -> dict:
        existing = await self.repo.get_by_plate_number(vehicle_in.plate_number)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu plaka zaten kayıtlı")

        vehicle_doc = {
            "plate_number": vehicle_in.plate_number,
            "vehicle_type": vehicle_in.vehicle_type.value,
            "capacity_kg": vehicle_in.capacity_kg,
            "average_cost_per_km": vehicle_in.average_cost_per_km,
            "average_carbon_per_km": vehicle_in.average_carbon_per_km,
            "is_active": vehicle_in.is_active,
            "created_at": datetime.now(timezone.utc),
        }
        inserted_id = await self.repo.create(vehicle_doc)
        vehicle_doc["_id"] = inserted_id
        return vehicle_doc

    async def list_vehicles(self) -> list[dict]:
        return await self.repo.list_all()
