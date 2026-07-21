from fastapi import HTTPException, status

from app.models.vehicle import (
    VehicleRecommendationRequest,
    VehicleRecommendationResponse,
    VehicleRecommendationResult,
)
from app.repositories.vehicle_repository import VehicleRepository
from app.services.vehicle_economics import calculate_vehicle_economics

_CARBON_PENALTY_PER_KG = 2
_CAPACITY_PENALTY = 10000


class VehicleRecommendationService:
    def __init__(self, vehicle_repo: VehicleRepository):
        self.vehicle_repo = vehicle_repo

    async def recommend_best(self, request_in: VehicleRecommendationRequest) -> VehicleRecommendationResponse:
        vehicles = await self.vehicle_repo.list_all()
        active_vehicles = [v for v in vehicles if v["is_active"]]
        if not active_vehicles:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aktif araç bulunamadı.")

        results = [self._evaluate(v, request_in) for v in active_vehicles]
        results.sort(key=lambda r: r.score, reverse=True)
        results[0].reason += " En yüksek skora sahip."

        return VehicleRecommendationResponse(recommended_vehicle=results[0], alternatives=results[1:])

    def _evaluate(self, vehicle: dict, request_in: VehicleRecommendationRequest) -> VehicleRecommendationResult:
        economics = calculate_vehicle_economics(vehicle, request_in.distance_km, request_in.expected_revenue)
        capacity_suitable = vehicle["capacity_kg"] >= request_in.package_weight_kg

        score = economics["estimated_profit"] - economics["estimated_carbon_kg"] * _CARBON_PENALTY_PER_KG
        if not capacity_suitable:
            score -= _CAPACITY_PENALTY

        return VehicleRecommendationResult(
            id=str(vehicle["_id"]),
            plate_number=vehicle["plate_number"],
            vehicle_type=vehicle["vehicle_type"],
            estimated_cost=economics["estimated_cost"],
            estimated_carbon_kg=economics["estimated_carbon_kg"],
            estimated_profit=economics["estimated_profit"],
            capacity_suitable=capacity_suitable,
            score=round(score, 2),
            reason=self._build_reason(capacity_suitable, economics),
        )

    def _build_reason(self, capacity_suitable: bool, economics: dict) -> str:
        if not capacity_suitable:
            return "Bu araç paket ağırlığı için yetersiz kapasiteye sahip."
        profit_desc = "kârlı" if economics["estimated_profit"] >= 0 else "zararlı"
        return f"Bu araç kapasiteye uygun ve bu rotada {profit_desc} görünüyor."
