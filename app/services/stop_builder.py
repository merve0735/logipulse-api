from datetime import datetime, timezone

from bson import ObjectId

from app.models.stop import StopCreate, StopStatus


def build_stop_docs(stops_in: list[StopCreate]) -> list[dict]:
    now = datetime.now(timezone.utc)
    return [
        {
            "id": str(ObjectId()),
            "sequence_number": stop_in.sequence_number,
            "customer_name": stop_in.customer_name,
            "customer_phone": stop_in.customer_phone,
            "address": stop_in.address,
            "latitude": stop_in.latitude,
            "longitude": stop_in.longitude,
            "package_weight_kg": stop_in.package_weight_kg,
            "delivery_note": stop_in.delivery_note,
            "status": StopStatus.PENDING.value,
            "failure_reason": None,
            "delivered_at": None,
            "created_at": now,
            "updated_at": now,
        }
        for stop_in in stops_in
    ]
