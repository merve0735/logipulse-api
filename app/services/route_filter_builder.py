import re
from typing import Optional

from app.models.route_filter import RouteFilter


def build_route_query(filters: RouteFilter, driver_id: Optional[str] = None) -> dict:
    query: dict = {}

    if driver_id is not None:
        query["assigned_driver_id"] = driver_id
    elif filters.assigned_driver_id is not None:
        query["assigned_driver_id"] = filters.assigned_driver_id

    if filters.status is not None:
        query["status"] = filters.status.value

    if filters.vehicle_type is not None:
        query["vehicle_type"] = filters.vehicle_type.value

    if filters.vehicle_id is not None:
        query["vehicle_id"] = filters.vehicle_id

    profit_range = {}
    if filters.min_profit is not None:
        profit_range["$gte"] = filters.min_profit
    if filters.max_profit is not None:
        profit_range["$lte"] = filters.max_profit
    if profit_range:
        query["estimated_profit"] = profit_range

    carbon_range = {}
    if filters.min_carbon is not None:
        carbon_range["$gte"] = filters.min_carbon
    if filters.max_carbon is not None:
        carbon_range["$lte"] = filters.max_carbon
    if carbon_range:
        query["estimated_carbon_kg"] = carbon_range

    if filters.search:
        pattern = re.escape(filters.search)
        query["$or"] = [
            {"origin": {"$regex": pattern, "$options": "i"}},
            {"destination": {"$regex": pattern, "$options": "i"}},
            {"vehicle_plate_number": {"$regex": pattern, "$options": "i"}},
            {"stops.customer_name": {"$regex": pattern, "$options": "i"}},
            {"stops.address": {"$regex": pattern, "$options": "i"}},
        ]

    return query
