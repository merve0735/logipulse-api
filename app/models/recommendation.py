from enum import Enum

from pydantic import BaseModel


class RecommendationType(str, Enum):
    PROFIT_OPTIMIZATION = "profit_optimization"
    CARBON_REDUCTION = "carbon_reduction"
    FLEET_TRANSITION = "fleet_transition"
    OPERATION_QUALITY = "operation_quality"


class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(BaseModel):
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    message: str
    affected_route_count: int
    potential_impact: str
