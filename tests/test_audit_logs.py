import uuid


def test_action_creates_audit_log_entry(client, admin_user):
    plate = f"TST{uuid.uuid4().hex[:6].upper()}"
    client.post(
        "/api/v1/vehicles",
        headers=admin_user["headers"],
        json={
            "plate_number": plate,
            "vehicle_type": "electric_van",
            "capacity_kg": 500,
            "average_cost_per_km": 2,
            "average_carbon_per_km": 0.05,
            "is_active": True,
        },
    )

    res = client.get(
        "/api/v1/audit-logs",
        headers=admin_user["headers"],
        params={"action": "vehicle_created"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert any(item["metadata"].get("plate_number") == plate for item in body["items"])


def test_driver_cannot_view_audit_logs(client, driver_user):
    res = client.get("/api/v1/audit-logs", headers=driver_user["headers"])
    assert res.status_code == 403
