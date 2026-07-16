from app.models.route import VehicleType
from app.services.carbon.base import CarbonEmissionStrategy
from app.services.carbon.strategies import (
    BicycleEmissionStrategy,
    ElectricVanEmissionStrategy,
    MotorcycleEmissionStrategy,
    TruckEmissionStrategy,
    VanEmissionStrategy,
)

_STRATEGIES: dict[VehicleType, CarbonEmissionStrategy] = {
    VehicleType.BICYCLE: BicycleEmissionStrategy(),
    VehicleType.MOTORCYCLE: MotorcycleEmissionStrategy(),
    VehicleType.VAN: VanEmissionStrategy(),
    VehicleType.ELECTRIC_VAN: ElectricVanEmissionStrategy(),
    VehicleType.TRUCK: TruckEmissionStrategy(),
}


def calculate_carbon_emission(vehicle_type: VehicleType, distance_km: float) -> float:
    strategy = _STRATEGIES[vehicle_type]
    return strategy.calculate(distance_km)
