from app.models.dashboard import DashboardSummary, RouteSummary
from app.repositories.route_repository import RouteRepository
from app.services.stop_metrics import compute_stop_metrics, flatten_stops


def _to_route_summary(route: dict) -> RouteSummary:
    return RouteSummary(
        id=str(route["_id"]),
        name=f"{route['origin']} → {route['destination']}",
        vehicle_plate_number=route["vehicle_plate_number"],
        estimated_profit=route["estimated_profit"],
        estimated_carbon_kg=route["estimated_carbon_kg"],
    )


class DashboardService:
    def __init__(self, route_repo: RouteRepository):
        self.route_repo = route_repo

    async def get_summary(self) -> DashboardSummary:
        routes = await self.route_repo.list_all()
        total_routes = len(routes)

        if total_routes == 0:
            return DashboardSummary(
                total_routes=0,
                total_distance_km=0,
                total_expected_revenue=0,
                total_estimated_cost=0,
                total_estimated_profit=0,
                total_estimated_carbon_kg=0,
                average_profit_per_route=0,
                average_carbon_per_route=0,
                electric_route_count=0,
                diesel_route_count=0,
                motorcycle_route_count=0,
                total_stops=0,
                delivered_stop_count=0,
                failed_stop_count=0,
                skipped_stop_count=0,
                retry_scheduled_stop_count=0,
                pending_stop_count=0,
                delivery_success_rate=0,
            )

        total_distance_km = sum(r["distance_km"] for r in routes)
        total_expected_revenue = sum(r["expected_revenue"] for r in routes)
        total_estimated_cost = sum(r["estimated_cost"] for r in routes)
        total_estimated_profit = sum(r["estimated_profit"] for r in routes)
        total_estimated_carbon_kg = sum(r["estimated_carbon_kg"] for r in routes)

        most_profitable = max(routes, key=lambda r: r["estimated_profit"])
        least_profitable = min(routes, key=lambda r: r["estimated_profit"])
        stop_metrics = compute_stop_metrics(flatten_stops(routes))

        return DashboardSummary(
            total_routes=total_routes,
            total_distance_km=round(total_distance_km, 2),
            total_expected_revenue=round(total_expected_revenue, 2),
            total_estimated_cost=round(total_estimated_cost, 2),
            total_estimated_profit=round(total_estimated_profit, 2),
            total_estimated_carbon_kg=round(total_estimated_carbon_kg, 2),
            average_profit_per_route=round(total_estimated_profit / total_routes, 2),
            average_carbon_per_route=round(total_estimated_carbon_kg / total_routes, 2),
            most_profitable_route=_to_route_summary(most_profitable),
            least_profitable_route=_to_route_summary(least_profitable),
            electric_route_count=sum(1 for r in routes if r["vehicle_type"] == "electric_van"),
            diesel_route_count=sum(1 for r in routes if r["vehicle_type"] == "diesel_van"),
            motorcycle_route_count=sum(1 for r in routes if r["vehicle_type"] == "motorcycle"),
            **stop_metrics,
        )
