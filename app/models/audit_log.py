from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.user import UserRole


class AuditAction(str, Enum):
    USER_REGISTERED = "user_registered"
    USER_LOGGED_IN = "user_logged_in"
    VEHICLE_CREATED = "vehicle_created"
    ROUTE_CREATED = "route_created"
    ROUTE_ASSIGNED = "route_assigned"
    ROUTE_STARTED = "route_started"
    ROUTE_DELIVERED = "route_delivered"
    ROUTE_CANCELLED = "route_cancelled"
    STOP_DELIVERED = "stop_delivered"
    STOP_FAILED = "stop_failed"
    STOP_SKIPPED = "stop_skipped"
    STOP_RETRY_SCHEDULED = "stop_retry_scheduled"
    PROOF_OF_DELIVERY_ADDED = "proof_of_delivery_added"
    DRIVER_LOCATION_UPDATED = "driver_location_updated"
    CSV_ROUTE_IMPORTED = "csv_route_imported"
    SUSTAINABILITY_PDF_DOWNLOADED = "sustainability_pdf_downloaded"


class AuditLogOut(BaseModel):
    id: str
    actor_user_id: Optional[str]
    actor_email: Optional[str]
    actor_role: Optional[UserRole]
    action: AuditAction
    entity_type: Optional[str]
    entity_id: Optional[str]
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AuditLogFilter(BaseModel):
    action: Optional[AuditAction] = None
    actor_role: Optional[UserRole] = None
    entity_type: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogOut]
    total: int
    limit: int
    offset: int
    has_more: bool
