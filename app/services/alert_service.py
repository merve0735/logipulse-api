from app.models.alert import Alert, AlertSeverity, AlertType
from app.repositories.route_repository import RouteRepository
from app.services.route_rules import (
    is_cancelled,
    is_diesel_high_emission,
    is_high_carbon,
    is_negative_profit,
    route_name,
)


class AlertService:
    def __init__(self, route_repo: RouteRepository):
        self.route_repo = route_repo

    async def get_alerts(self) -> list[Alert]:
        routes = await self.route_repo.list_all()
        alerts: list[Alert] = []

        for route in routes:
            route_id = str(route["_id"])
            name = route_name(route)

            if is_negative_profit(route):
                alerts.append(
                    Alert(
                        type=AlertType.NEGATIVE_PROFIT,
                        severity=AlertSeverity.HIGH,
                        message="Bu rota zarar ediyor.",
                        route_id=route_id,
                        route_name=name,
                        value=route["estimated_profit"],
                    )
                )

            if is_high_carbon(route):
                alerts.append(
                    Alert(
                        type=AlertType.HIGH_CARBON,
                        severity=AlertSeverity.MEDIUM,
                        message="Bu rota yüksek karbon salımı üretiyor.",
                        route_id=route_id,
                        route_name=name,
                        value=route["estimated_carbon_kg"],
                    )
                )

            if is_cancelled(route):
                alerts.append(
                    Alert(
                        type=AlertType.CANCELLED_ROUTE,
                        severity=AlertSeverity.LOW,
                        message="Bu rota iptal edildi.",
                        route_id=route_id,
                        route_name=name,
                        value=route["status"],
                    )
                )

            if is_diesel_high_emission(route):
                alerts.append(
                    Alert(
                        type=AlertType.DIESEL_HIGH_EMISSION,
                        severity=AlertSeverity.MEDIUM,
                        message="Dizel araçla yapılan bu rota yüksek emisyon üretiyor.",
                        route_id=route_id,
                        route_name=name,
                        value=route["estimated_carbon_kg"],
                    )
                )

        return alerts
