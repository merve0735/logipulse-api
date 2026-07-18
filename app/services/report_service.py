from datetime import datetime, timezone

from app.models.alert import AlertSeverity
from app.models.dashboard import DashboardSummary
from app.models.recommendation import RecommendationPriority
from app.models.report import (
    CarbonSummary,
    FinancialSummary,
    RecommendationSummary,
    RiskSummary,
    SustainabilityReport,
)
from app.services.alert_service import AlertService
from app.services.dashboard_service import DashboardService
from app.services.recommendation_service import RecommendationService


class ReportService:
    def __init__(
        self,
        dashboard_service: DashboardService,
        alert_service: AlertService,
        recommendation_service: RecommendationService,
    ):
        self.dashboard_service = dashboard_service
        self.alert_service = alert_service
        self.recommendation_service = recommendation_service

    async def get_sustainability_report(self) -> SustainabilityReport:
        summary = await self.dashboard_service.get_summary()
        alerts = await self.alert_service.get_alerts()
        recommendations = await self.recommendation_service.get_recommendations()

        financial_summary = FinancialSummary(
            total_expected_revenue=summary.total_expected_revenue,
            total_estimated_cost=summary.total_estimated_cost,
            total_estimated_profit=summary.total_estimated_profit,
            average_profit_per_route=summary.average_profit_per_route,
            most_profitable_route=summary.most_profitable_route,
            least_profitable_route=summary.least_profitable_route,
        )

        carbon_summary = CarbonSummary(
            total_estimated_carbon_kg=summary.total_estimated_carbon_kg,
            average_carbon_per_route=summary.average_carbon_per_route,
            electric_route_count=summary.electric_route_count,
            diesel_route_count=summary.diesel_route_count,
            motorcycle_route_count=summary.motorcycle_route_count,
        )

        risk_summary = RiskSummary(
            total_alert_count=len(alerts),
            high_alert_count=sum(1 for a in alerts if a.severity == AlertSeverity.HIGH),
            medium_alert_count=sum(1 for a in alerts if a.severity == AlertSeverity.MEDIUM),
            low_alert_count=sum(1 for a in alerts if a.severity == AlertSeverity.LOW),
        )

        recommendation_summary = RecommendationSummary(
            total_recommendation_count=len(recommendations),
            high_priority_count=sum(1 for r in recommendations if r.priority == RecommendationPriority.HIGH),
            medium_priority_count=sum(1 for r in recommendations if r.priority == RecommendationPriority.MEDIUM),
            low_priority_count=sum(1 for r in recommendations if r.priority == RecommendationPriority.LOW),
            recommendations=recommendations,
        )

        return SustainabilityReport(
            report_title="LogiPulse Sustainability & Profitability Report",
            generated_at=datetime.now(timezone.utc),
            executive_summary="Bu rapor, mevcut rota operasyonlarının kârlılık ve karbon etkisini özetler.",
            financial_summary=financial_summary,
            carbon_summary=carbon_summary,
            risk_summary=risk_summary,
            recommendation_summary=recommendation_summary,
            business_comment=self._build_business_comment(summary, risk_summary),
        )

    def _build_business_comment(self, summary: DashboardSummary, risk_summary: RiskSummary) -> str:
        comments = []

        if summary.total_estimated_profit < 0:
            comments.append(
                "Operasyon genelinde zarar görülüyor. Fiyatlandırma ve araç seçimi yeniden değerlendirilmeli."
            )

        if summary.diesel_route_count > summary.electric_route_count:
            comments.append(
                "Dizel araç kullanımı elektrikli araç kullanımından yüksek. "
                "Uygun rotalarda elektrikli araç önceliklendirilebilir."
            )

        if risk_summary.total_alert_count == 0:
            comments.append("Mevcut operasyonlarda kritik risk görünmüyor.")

        if not comments:
            return "Operasyonlar genel olarak dengeli görünüyor."

        return " ".join(comments)
