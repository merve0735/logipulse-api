from app.models.recommendation import Recommendation, RecommendationPriority, RecommendationType
from app.models.stop import StopStatus
from app.repositories.route_repository import RouteRepository
from app.services.route_rules import is_cancelled, is_diesel, is_electric, is_high_carbon, is_negative_profit
from app.services.stop_metrics import flatten_stops


class RecommendationService:
    def __init__(self, route_repo: RouteRepository):
        self.route_repo = route_repo

    async def get_recommendations(self) -> list[Recommendation]:
        routes = await self.route_repo.list_all()
        recommendations: list[Recommendation] = []

        negative_profit_count = sum(1 for r in routes if is_negative_profit(r))
        if negative_profit_count > 0:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.PROFIT_OPTIMIZATION,
                    priority=RecommendationPriority.HIGH,
                    title="Zarar Eden Rotaları Optimize Et",
                    message=(
                        "Bazı rotalar beklenen gelirden daha yüksek maliyet üretiyor. "
                        "Bu rotalarda mesafe, araç seçimi veya teslimat fiyatı yeniden değerlendirilmeli."
                    ),
                    affected_route_count=negative_profit_count,
                    potential_impact="Kârlılık artışı",
                )
            )

        high_carbon_count = sum(1 for r in routes if is_high_carbon(r))
        if high_carbon_count > 0:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.CARBON_REDUCTION,
                    priority=RecommendationPriority.MEDIUM,
                    title="Yüksek Karbonlu Rotaları Azalt",
                    message=(
                        "Karbon salımı yüksek rotalarda elektrikli araç veya daha kısa rota seçimi "
                        "değerlendirilebilir."
                    ),
                    affected_route_count=high_carbon_count,
                    potential_impact="Karbon salımı azalır",
                )
            )

        diesel_count = sum(1 for r in routes if is_diesel(r))
        electric_count = sum(1 for r in routes if is_electric(r))
        if diesel_count > electric_count:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.FLEET_TRANSITION,
                    priority=RecommendationPriority.MEDIUM,
                    title="Elektrikli Araç Kullanımını Artır",
                    message=(
                        "Dizel araç kullanımı elektrikli araç kullanımından fazla görünüyor. Uygun rotalarda "
                        "elektrikli araçlara öncelik verilmesi yakıt maliyeti ve karbon salımını azaltabilir."
                    ),
                    affected_route_count=diesel_count,
                    potential_impact="Yakıt maliyeti ve karbon azalır",
                )
            )

        cancelled_count = sum(1 for r in routes if is_cancelled(r))
        if cancelled_count > 0:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.OPERATION_QUALITY,
                    priority=RecommendationPriority.LOW,
                    title="İptal Edilen Rotaları İncele",
                    message=(
                        "İptal edilen rotalar operasyonel planlama sorunlarına işaret edebilir. "
                        "İptal nedenleri takip edilerek süreç iyileştirilebilir."
                    ),
                    affected_route_count=cancelled_count,
                    potential_impact="Operasyon kalitesi artar",
                )
            )

        stops = flatten_stops(routes)

        failed_stop_count = sum(1 for s in stops if s["status"] == StopStatus.FAILED.value)
        if failed_stop_count > 0:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.DELIVERY_QUALITY,
                    priority=RecommendationPriority.MEDIUM,
                    title="Başarısız Teslimat Nedenlerini İncele",
                    message=(
                        "Başarısız teslimatlar müşteri memnuniyetini ve operasyon verimliliğini düşürebilir. "
                        "Failure reason kayıtları düzenli analiz edilmelidir."
                    ),
                    affected_route_count=failed_stop_count,
                    potential_impact="Teslimat başarı oranı artar",
                )
            )

        retry_stop_count = sum(1 for s in stops if s["status"] == StopStatus.RETRY_SCHEDULED.value)
        if retry_stop_count > 0:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.RETRY_OPTIMIZATION,
                    priority=RecommendationPriority.LOW,
                    title="Tekrar Denenecek Teslimatları Planla",
                    message=(
                        "Tekrar denenecek teslimatlar ayrı bir rota planına alınarak zaman kaybı azaltılabilir."
                    ),
                    affected_route_count=retry_stop_count,
                    potential_impact="Operasyon planlaması iyileşir",
                )
            )

        return recommendations
