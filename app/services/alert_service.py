from app.models.alert import Alert, AlertSeverity, AlertType
from app.repositories.route_repository import RouteRepository

_HIGH_CARBON_THRESHOLD_KG = 50
_DIESEL_HIGH_EMISSION_THRESHOLD_KG = 30


def _route_name(route: dict) -> str:
    return f"{route['origin']} → {route['destination']}"


class AlertService:
    def __init__(self, route_repo: RouteRepository):
        self.route_repo = route_repo

    async def get_alerts(self) -> list[Alert]:
        routes = await self.route_repo.list_all()
        alerts: list[Alert] = []

        for route in routes:
            route_id = str(route["_id"])
            route_name = _route_name(route)

            if route["estimated_profit"] < 0:
                alerts.append(
                    Alert(
                        type=AlertType.NEGATIVE_PROFIT,
                        severity=AlertSeverity.HIGH,
                        message="Bu rota zarar ediyor.",
                        route_id=route_id,
                        route_name=route_name,
                        value=route["estimated_profit"],
                    )
                )

            if route["estimated_carbon_kg"] > _HIGH_CARBON_THRESHOLD_KG:
                alerts.append(
                    Alert(
                        type=AlertType.HIGH_CARBON,
                        severity=AlertSeverity.MEDIUM,
                        message="Bu rota yüksek karbon salımı üretiyor.",
                        route_id=route_id,
                        route_name=route_name,
                        value=route["estimated_carbon_kg"],
                    )
                )

            if route["status"] == "cancelled":
                alerts.append(
                    Alert(
                        type=AlertType.CANCELLED_ROUTE,
                        severity=AlertSeverity.LOW,
                        message="Bu rota iptal edildi.",
                        route_id=route_id,
                        route_name=route_name,
                        value=route["status"],
                    )
                )

            if (
                route["vehicle_type"] == "diesel_van"
                and route["estimated_carbon_kg"] > _DIESEL_HIGH_EMISSION_THRESHOLD_KG
            ):
                alerts.append(
                    Alert(
                        type=AlertType.DIESEL_HIGH_EMISSION,
                        severity=AlertSeverity.MEDIUM,
                        message="Dizel araçla yapılan bu rota yüksek emisyon üretiyor.",
                        route_id=route_id,
                        route_name=route_name,
                        value=route["estimated_carbon_kg"],
                    )
                )

        return alerts
