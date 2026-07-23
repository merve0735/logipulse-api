from fastapi import APIRouter, Depends, Query

from app.core.deps import CurrentUser, require_role
from app.models.audit_log import AuditAction, AuditLogFilter, PaginatedAuditLogs
from app.models.user import UserRole
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


def get_audit_log_repository() -> AuditLogRepository:
    return AuditLogRepository()


def get_audit_log_service(repo: AuditLogRepository = Depends(get_audit_log_repository)) -> AuditLogService:
    return AuditLogService(repo)


@router.get("", response_model=PaginatedAuditLogs)
async def list_audit_logs(
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
    service: AuditLogService = Depends(get_audit_log_service),
    action: AuditAction | None = None,
    actor_role: UserRole | None = None,
    entity_type: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    filters = AuditLogFilter(
        action=action,
        actor_role=actor_role,
        entity_type=entity_type,
        limit=limit,
        offset=offset,
    )
    return await service.list_logs(filters)
