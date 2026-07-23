import uuid


def test_admin_can_create_vehicle(client, admin_user):
    plate = f"TST{uuid.uuid4().hex[:6].upper()}"
    res = client.post(
        "/api/v1/vehicles",
        headers=admin_user["headers"],
        json={
            "plate_number": plate,
            "vehicle_type": "diesel_van",
            "capacity_kg": 800,
            "average_cost_per_km": 3,
            "average_carbon_per_km": 0.2,
            "is_active": True,
        },
    )
    assert res.status_code == 201
    assert res.json()["plate_number"] == plate


def test_driver_cannot_create_vehicle(client, driver_user):
    plate = f"TST{uuid.uuid4().hex[:6].upper()}"
    res = client.post(
        "/api/v1/vehicles",
        headers=driver_user["headers"],
        json={
            "plate_number": plate,
            "vehicle_type": "diesel_van",
            "capacity_kg": 800,
            "average_cost_per_km": 3,
            "average_carbon_per_km": 0.2,
            "is_active": True,
        },
    )
    assert res.status_code == 403


def test_recommend_best_vehicle_returns_result_when_active_vehicles_exist(client, admin_user, active_vehicle):
    res = client.post(
        "/api/v1/vehicles/recommend-best",
        headers=admin_user["headers"],
        json={"distance_km": 50, "expected_revenue": 500, "package_weight_kg": 100},
    )
    assert res.status_code == 200
    assert "recommended_vehicle" in res.json()
    assert res.json()["recommended_vehicle"]["id"] is not None
