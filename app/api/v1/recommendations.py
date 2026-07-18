from fastapi import APIRouter, Depends

from app.api.v1.routes import get_route_repository
from app.core.deps import CurrentUser, require_role
from app.models.recommendation import Recommendation
from app.models.user import UserRole
from app.repositories.route_repository import RouteRepository
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_recommendation_service(repo: RouteRepository = Depends(get_route_repository)) -> RecommendationService:
    return RecommendationService(repo)


@router.get("", response_model=list[Recommendation])
async def get_recommendations(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: RecommendationService = Depends(get_recommendation_service),
):
    return await service.get_recommendations()
