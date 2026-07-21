from app.models.stop import StopStatus


def flatten_stops(routes: list[dict]) -> list[dict]:
    flat = []
    for route in routes:
        route_name = f"{route['origin']} → {route['destination']}"
        for stop in route.get("stops", []):
            flat.append({**stop, "route_id": str(route["_id"]), "route_name": route_name})
    return flat


def compute_stop_metrics(flat_stops: list[dict]) -> dict:
    total = len(flat_stops)
    counts = {s.value: 0 for s in StopStatus}
    for stop in flat_stops:
        counts[stop["status"]] = counts.get(stop["status"], 0) + 1

    delivered = counts[StopStatus.DELIVERED.value]
    success_rate = round(delivered / total * 100, 2) if total > 0 else 0

    return {
        "total_stops": total,
        "delivered_stop_count": delivered,
        "failed_stop_count": counts[StopStatus.FAILED.value],
        "skipped_stop_count": counts[StopStatus.SKIPPED.value],
        "retry_scheduled_stop_count": counts[StopStatus.RETRY_SCHEDULED.value],
        "pending_stop_count": counts[StopStatus.PENDING.value],
        "delivery_success_rate": success_rate,
    }
