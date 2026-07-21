from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StopStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY_SCHEDULED = "retry_scheduled"


class StopCreate(BaseModel):
    sequence_number: int
    customer_name: str
    customer_phone: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    package_weight_kg: Optional[float] = None
    delivery_note: Optional[str] = None


class ProofOfDelivery(BaseModel):
    recipient_name: str
    recipient_signature_text: Optional[str] = None
    delivery_photo_url: Optional[str] = None
    delivered_latitude: Optional[float] = None
    delivered_longitude: Optional[float] = None
    delivery_note: Optional[str] = None
    delivered_at: datetime


class StopOut(BaseModel):
    id: str
    sequence_number: int
    customer_name: str
    customer_phone: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    package_weight_kg: Optional[float] = None
    delivery_note: Optional[str] = None
    status: StopStatus
    failure_reason: Optional[str] = None
    delivered_at: Optional[datetime] = None
    proof_of_delivery: Optional[ProofOfDelivery] = None
    created_at: datetime
    updated_at: datetime


class StopFailRequest(BaseModel):
    failure_reason: str = Field(min_length=1)


class StopDeliverRequest(BaseModel):
    recipient_name: str = Field(min_length=1)
    recipient_signature_text: Optional[str] = None
    delivery_photo_url: Optional[str] = None
    delivered_latitude: Optional[float] = None
    delivered_longitude: Optional[float] = None
    delivery_note: Optional[str] = None
