from enum import Enum
from typing import Union

from pydantic import BaseModel


class AlertType(str, Enum):
    NEGATIVE_PROFIT = "negative_profit"
    HIGH_CARBON = "high_carbon"
    CANCELLED_ROUTE = "cancelled_route"
    DIESEL_HIGH_EMISSION = "diesel_high_emission"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Alert(BaseModel):
    type: AlertType
    severity: AlertSeverity
    message: str
    route_id: str
    route_name: str
    value: Union[float, str]
