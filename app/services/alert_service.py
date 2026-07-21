from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.stop import StopStatus
from app.repositories.route_repository import RouteRepository
from app.services.route_rules import (
    is_cancelled,
    is_diesel_high_emission,
    is_high_carbon,
    is_negative_profit,
    route_name,
)
from app.services.stop_metrics import flatten_stops


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

        for stop in flatten_stops(routes):
            if stop["status"] == StopStatus.FAILED.value:
                alerts.append(
                    Alert(
                        type=AlertType.FAILED_DELIVERY,
                        severity=AlertSeverity.MEDIUM,
                        message="Başarısız teslimat kaydı var.",
                        route_id=stop["route_id"],
                        route_name=stop["route_name"],
                        stop_id=stop["id"],
                        customer_name=stop["customer_name"],
                        value=stop.get("failure_reason") or "",
                    )
                )
            elif stop["status"] == StopStatus.SKIPPED.value:
                alerts.append(
                    Alert(
                        type=AlertType.SKIPPED_STOP,
                        severity=AlertSeverity.LOW,
                        message="Atlanan teslimat durağı var.",
                        route_id=stop["route_id"],
                        route_name=stop["route_name"],
                        stop_id=stop["id"],
                        customer_name=stop["customer_name"],
                        value=stop["status"],
                    )
                )
            elif stop["status"] == StopStatus.RETRY_SCHEDULED.value:
                alerts.append(
                    Alert(
                        type=AlertType.RETRY_SCHEDULED,
                        severity=AlertSeverity.LOW,
                        message="Tekrar denenecek teslimat var.",
                        route_id=stop["route_id"],
                        route_name=stop["route_name"],
                        stop_id=stop["id"],
                        customer_name=stop["customer_name"],
                        value=stop["status"],
                    )
                )

        return alerts
