from abc import ABC, abstractmethod


class CarbonEmissionStrategy(ABC):
    @abstractmethod
    def calculate(self, distance_km: float) -> float:
        ...
