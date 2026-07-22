from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from app.models.route import RouteCreate
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.services.csv_route_import import CsvValidationError, parse_csv_rows, validate_csv_rows
from app.services.route_service import RouteService


class ImportService:
    def __init__(self, route_service: RouteService, user_repo: UserRepository):
        self.route_service = route_service
        self.user_repo = user_repo

    async def import_routes_csv(
        self,
        csv_bytes: bytes,
        route_name: str,
        vehicle_id: str,
        expected_revenue: float,
        distance_km: float,
        assigned_driver_id: Optional[str],
        created_by: str,
    ) -> dict:
        raw_rows = parse_csv_rows(csv_bytes)
        stops = validate_csv_rows(raw_rows)

        if assigned_driver_id:
            await self._ensure_valid_driver(assigned_driver_id)

        route_in = RouteCreate(
            origin=route_name,
            destination=route_name,
            distance_km=distance_km,
            vehicle_id=vehicle_id,
            expected_revenue=expected_revenue,
            assigned_driver_id=assigned_driver_id,
            stops=stops,
        )
        route_doc = await self.route_service.create_route(route_in, created_by=created_by)

        if assigned_driver_id:
            route_doc = await self.route_service.assign_driver(str(route_doc["_id"]), assigned_driver_id)

        return route_doc

    async def _ensure_valid_driver(self, driver_id: str) -> None:
        try:
            driver = await self.user_repo.find_one({"_id": ObjectId(driver_id)})
        except InvalidId:
            raise CsvValidationError([{"row": 0, "field": "assigned_driver_id", "message": "Geçersiz sürücü ID."}])
        if not driver or driver["role"] != UserRole.DRIVER.value:
            raise CsvValidationError(
                [{"row": 0, "field": "assigned_driver_id", "message": "Geçerli bir sürücü değil."}]
            )
