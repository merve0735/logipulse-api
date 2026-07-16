from app.services.carbon.base import CarbonEmissionStrategy


class BicycleEmissionStrategy(CarbonEmissionStrategy):
    EMISSION_FACTOR_KG_PER_KM = 0.0

    def calculate(self, distance_km: float) -> float:
        return round(distance_km * self.EMISSION_FACTOR_KG_PER_KM, 2)


class MotorcycleEmissionStrategy(CarbonEmissionStrategy):
    EMISSION_FACTOR_KG_PER_KM = 0.10

    def calculate(self, distance_km: float) -> float:
        return round(distance_km * self.EMISSION_FACTOR_KG_PER_KM, 2)


class VanEmissionStrategy(CarbonEmissionStrategy):
    EMISSION_FACTOR_KG_PER_KM = 0.20

    def calculate(self, distance_km: float) -> float:
        return round(distance_km * self.EMISSION_FACTOR_KG_PER_KM, 2)


class ElectricVanEmissionStrategy(CarbonEmissionStrategy):
    EMISSION_FACTOR_KG_PER_KM = 0.05

    def calculate(self, distance_km: float) -> float:
        return round(distance_km * self.EMISSION_FACTOR_KG_PER_KM, 2)


class TruckEmissionStrategy(CarbonEmissionStrategy):
    EMISSION_FACTOR_KG_PER_KM = 0.90

    def calculate(self, distance_km: float) -> float:
        return round(distance_km * self.EMISSION_FACTOR_KG_PER_KM, 2)
