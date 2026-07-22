from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from app.models.route import RouteStatus
from app.models.tracking import DriverLocationOut
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.services.route_rules import route_name

_ACTIVE_STATUSES = {RouteStatus.ASSIGNED.value, RouteStatus.IN_PROGRESS.value}


class TrackingService:
    def __init__(self, user_repo: UserRepository, route_repo: RouteRepository):
        self.user_repo = user_repo
        self.route_repo = route_repo

    async def update_my_location(self, driver_id: str, latitude: float, longitude: float) -> None:
        await self.user_repo.update_one(
            {"_id": ObjectId(driver_id)},
            {
                "last_location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    async def list_driver_locations(self) -> list[DriverLocationOut]:
        drivers = await self.user_repo.list_by_role("driver")
        results = []

        for driver in drivers:
            driver_id = str(driver["_id"])
            location = driver.get("last_location")
            active_route = await self._find_active_route(driver_id)

            results.append(
                DriverLocationOut(
                    driver_id=driver_id,
                    driver_email=driver["email"],
                    latitude=location["latitude"] if location else None,
                    longitude=location["longitude"] if location else None,
                    updated_at=location["updated_at"] if location else None,
                    active_route_id=str(active_route["_id"]) if active_route else None,
                    active_route_name=route_name(active_route) if active_route else None,
                    route_status=active_route["status"] if active_route else None,
                )
            )

        return results

    async def _find_active_route(self, driver_id: str) -> Optional[dict]:
        routes = await self.route_repo.list_by_driver(driver_id)
        for route in routes:
            if route["status"] in _ACTIVE_STATUSES:
                return route
        return None
