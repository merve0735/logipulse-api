from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.route import RouteStatus
from app.models.stop import StopStatus
from app.repositories.route_repository import RouteRepository
from app.services.route_service import RouteService


class StopService:
    def __init__(self, route_repo: RouteRepository, route_service: RouteService):
        self.route_repo = route_repo
        self.route_service = route_service

    async def list_stops(self, route_id: str, current_user_id: str, is_admin: bool) -> list[dict]:
        route = await self.route_service.get_route_or_404(route_id)
        if not is_admin:
            self.route_service.ensure_own_route(route, current_user_id)
        return route.get("stops", [])

    async def deliver_stop(self, route_id: str, stop_id: str, driver_id: str) -> dict:
        route, _ = await self._get_own_route_and_stop(route_id, stop_id, driver_id)
        return await self._apply_update(
            route,
            route_id,
            stop_id,
            {
                "status": StopStatus.DELIVERED.value,
                "delivered_at": datetime.now(timezone.utc),
                "failure_reason": None,
            },
        )

    async def fail_stop(self, route_id: str, stop_id: str, driver_id: str, failure_reason: str) -> dict:
        route, _ = await self._get_own_route_and_stop(route_id, stop_id, driver_id)
        return await self._apply_update(
            route, route_id, stop_id, {"status": StopStatus.FAILED.value, "failure_reason": failure_reason}
        )

    async def skip_stop(self, route_id: str, stop_id: str, driver_id: str) -> dict:
        route, _ = await self._get_own_route_and_stop(route_id, stop_id, driver_id)
        return await self._apply_update(route, route_id, stop_id, {"status": StopStatus.SKIPPED.value})

    async def schedule_retry_stop(self, route_id: str, stop_id: str, driver_id: str) -> dict:
        route, _ = await self._get_own_route_and_stop(route_id, stop_id, driver_id)
        return await self._apply_update(route, route_id, stop_id, {"status": StopStatus.RETRY_SCHEDULED.value})

    async def _get_own_route_and_stop(self, route_id: str, stop_id: str, driver_id: str) -> tuple[dict, dict]:
        route = await self.route_service.get_route_or_404(route_id)
        self.route_service.ensure_own_route(route, driver_id)
        stop = next((s for s in route.get("stops", []) if s["id"] == stop_id), None)
        if not stop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Durak bulunamadı")
        return route, stop

    async def _apply_update(self, route: dict, route_id: str, stop_id: str, fields: dict) -> dict:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self.route_repo.update_stop(route_id, stop_id, fields)

        for stop in route.get("stops", []):
            if stop["id"] == stop_id:
                stop.update(fields)
                break

        if fields.get("status") == StopStatus.DELIVERED.value:
            await self._maybe_auto_deliver_route(route, route_id)

        return route

    async def _maybe_auto_deliver_route(self, route: dict, route_id: str) -> None:
        stops = route.get("stops", [])
        all_delivered = bool(stops) and all(s["status"] == StopStatus.DELIVERED.value for s in stops)
        if all_delivered and route["status"] == RouteStatus.IN_PROGRESS.value:
            await self.route_service.transition_status(route_id, route, RouteStatus.DELIVERED)
