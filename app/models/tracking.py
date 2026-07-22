from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LocationUpdateRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class DriverLocationOut(BaseModel):
    driver_id: str
    driver_email: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    updated_at: Optional[datetime] = None
    active_route_id: Optional[str] = None
    active_route_name: Optional[str] = None
    route_status: Optional[str] = None
