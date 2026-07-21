def calculate_vehicle_economics(vehicle: dict, distance_km: float, expected_revenue: float) -> dict:
    estimated_cost = round(distance_km * vehicle["average_cost_per_km"], 2)
    estimated_carbon_kg = round(distance_km * vehicle["average_carbon_per_km"], 2)
    estimated_profit = round(expected_revenue - estimated_cost, 2)
    return {
        "estimated_cost": estimated_cost,
        "estimated_carbon_kg": estimated_carbon_kg,
        "estimated_profit": estimated_profit,
    }
