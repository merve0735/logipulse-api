from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.alerts import get_alert_service
from app.api.v1.audit_logs import get_audit_log_service
from app.api.v1.dashboard import get_dashboard_service
from app.api.v1.recommendations import get_recommendation_service
from app.api.v1.reports import get_report_service
from app.core.deps import CurrentUser, require_role
from app.models.ai import AiAdvisorRequest, AiAdvisorResponse
from app.models.audit_log import AuditAction
from app.models.user import UserRole
from app.services.ai_advisor_service import (
    AiAdvisorService,
    GeminiNotConfiguredError,
    GeminiRequestError,
)
from app.services.alert_service import AlertService
from app.services.audit_log_service import AuditLogService
from app.services.dashboard_service import DashboardService
from app.services.recommendation_service import RecommendationService
from app.services.report_service import ReportService

router = APIRouter(prefix="/ai", tags=["ai"])


def get_ai_advisor_service(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    alert_service: AlertService = Depends(get_alert_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    report_service: ReportService = Depends(get_report_service),
) -> AiAdvisorService:
    return AiAdvisorService(dashboard_service, alert_service, recommendation_service, report_service)


@router.post("/advisor", response_model=AiAdvisorResponse)
async def ask_ai_advisor(
    request_in: AiAdvisorRequest,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: AiAdvisorService = Depends(get_ai_advisor_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    try:
        result = await service.ask(request_in.question)
    except GeminiNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key is not configured.",
        )
    except GeminiRequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LogiPulse AI Advisor şu anda yanıt veremedi. Lütfen daha sonra tekrar deneyin.",
        )

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.AI_ADVISOR_ASKED,
        description="Admin asked LogiPulse AI Advisor a question.",
        entity_type="ai",
        metadata={"question": request_in.question[:200], "model": result.model},
    )

    return result
