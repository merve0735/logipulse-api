from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.dashboard import RouteSummary
from app.models.recommendation import Recommendation


class FinancialSummary(BaseModel):
    total_expected_revenue: float
    total_estimated_cost: float
    total_estimated_profit: float
    average_profit_per_route: float
    most_profitable_route: Optional[RouteSummary] = None
    least_profitable_route: Optional[RouteSummary] = None


class CarbonSummary(BaseModel):
    total_estimated_carbon_kg: float
    average_carbon_per_route: float
    electric_route_count: int
    diesel_route_count: int
    motorcycle_route_count: int


class RiskSummary(BaseModel):
    total_alert_count: int
    high_alert_count: int
    medium_alert_count: int
    low_alert_count: int


class RecommendationSummary(BaseModel):
    total_recommendation_count: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    recommendations: list[Recommendation]


class SustainabilityReport(BaseModel):
    report_title: str
    generated_at: datetime
    executive_summary: str
    financial_summary: FinancialSummary
    carbon_summary: CarbonSummary
    risk_summary: RiskSummary
    recommendation_summary: RecommendationSummary
    business_comment: str
