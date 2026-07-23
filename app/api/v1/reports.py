from fastapi import APIRouter, Depends, Response

from app.api.v1.alerts import get_alert_service
from app.api.v1.audit_logs import get_audit_log_service
from app.api.v1.dashboard import get_dashboard_service
from app.api.v1.recommendations import get_recommendation_service
from app.core.deps import CurrentUser, require_role
from app.models.audit_log import AuditAction
from app.models.report import SustainabilityReport
from app.models.user import UserRole
from app.services.alert_service import AlertService
from app.services.audit_log_service import AuditLogService
from app.services.dashboard_service import DashboardService
from app.services.recommendation_service import RecommendationService
from app.services.report_pdf import build_sustainability_report_pdf
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    alert_service: AlertService = Depends(get_alert_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> ReportService:
    return ReportService(dashboard_service, alert_service, recommendation_service)


@router.get("/sustainability", response_model=SustainabilityReport)
async def get_sustainability_report(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: ReportService = Depends(get_report_service),
):
    return await service.get_sustainability_report()


@router.get("/sustainability/pdf")
async def get_sustainability_report_pdf(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: ReportService = Depends(get_report_service),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    report = await service.get_sustainability_report()
    pdf_bytes = build_sustainability_report_pdf(report)

    await audit_service.record(
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        action=AuditAction.SUSTAINABILITY_PDF_DOWNLOADED,
        description=f"{current_user.email} sürdürülebilirlik raporunu PDF olarak indirdi.",
        entity_type="report",
        entity_id=None,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=logipulse-sustainability-report.pdf"},
    )
