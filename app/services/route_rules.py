HIGH_CARBON_THRESHOLD_KG = 50
DIESEL_HIGH_EMISSION_THRESHOLD_KG = 30


def is_negative_profit(route: dict) -> bool:
    return route["estimated_profit"] < 0


def is_high_carbon(route: dict) -> bool:
    return route["estimated_carbon_kg"] > HIGH_CARBON_THRESHOLD_KG


def is_cancelled(route: dict) -> bool:
    return route["status"] == "cancelled"


def is_diesel(route: dict) -> bool:
    return route["vehicle_type"] == "diesel_van"


def is_electric(route: dict) -> bool:
    return route["vehicle_type"] == "electric_van"


def is_diesel_high_emission(route: dict) -> bool:
    return is_diesel(route) and route["estimated_carbon_kg"] > DIESEL_HIGH_EMISSION_THRESHOLD_KG


def route_name(route: dict) -> str:
    return f"{route['origin']} → {route['destination']}"
