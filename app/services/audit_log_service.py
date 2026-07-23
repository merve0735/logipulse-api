import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.models.audit_log import AuditAction, AuditLogFilter, AuditLogOut, PaginatedAuditLogs
from app.models.user import UserRole
from app.repositories.audit_log_repository import AuditLogRepository

logger = logging.getLogger(__name__)


def _to_audit_log_out(doc: dict) -> AuditLogOut:
    return AuditLogOut(
        id=str(doc["_id"]),
        actor_user_id=doc.get("actor_user_id"),
        actor_email=doc.get("actor_email"),
        actor_role=doc.get("actor_role"),
        action=doc["action"],
        entity_type=doc.get("entity_type"),
        entity_id=doc.get("entity_id"),
        description=doc["description"],
        metadata=doc.get("metadata") or {},
        created_at=doc["created_at"],
    )


class AuditLogService:
    def __init__(self, repo: AuditLogRepository):
        self.repo = repo

    async def record(
        self,
        actor_user_id: Optional[str],
        actor_email: Optional[str],
        actor_role: Optional[UserRole],
        action: AuditAction,
        description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        try:
            log_doc = {
                "actor_user_id": actor_user_id,
                "actor_email": actor_email,
                "actor_role": actor_role.value if actor_role else None,
                "action": action.value,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "description": description,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
            }
            await self.repo.create(log_doc)
        except Exception:
            logger.exception("Audit log kaydı oluşturulamadı: action=%s", action.value)

    async def list_logs(self, filters: AuditLogFilter) -> PaginatedAuditLogs:
        query: dict[str, Any] = {}
        if filters.action:
            query["action"] = filters.action.value
        if filters.actor_role:
            query["actor_role"] = filters.actor_role.value
        if filters.entity_type:
            query["entity_type"] = filters.entity_type

        items, total = await self.repo.find_filtered(query, filters.limit, filters.offset)
        return PaginatedAuditLogs(
            items=[_to_audit_log_out(doc) for doc in items],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
            has_more=(filters.offset + len(items)) < total,
        )
