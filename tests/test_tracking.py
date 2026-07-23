def test_driver_can_update_own_location(client, driver_user):
    res = client.patch(
        "/api/v1/tracking/me/location",
        headers=driver_user["headers"],
        json={"latitude": 41.0082, "longitude": 28.9784},
    )
    assert res.status_code == 200


def test_admin_can_view_driver_locations(client, admin_user, driver_user):
    client.patch(
        "/api/v1/tracking/me/location",
        headers=driver_user["headers"],
        json={"latitude": 41.0082, "longitude": 28.9784},
    )

    res = client.get("/api/v1/tracking/drivers", headers=admin_user["headers"])
    assert res.status_code == 200
    driver_ids = [d["driver_id"] for d in res.json()]
    assert driver_user["id"] in driver_ids


def test_driver_cannot_view_driver_locations(client, driver_user):
    res = client.get("/api/v1/tracking/drivers", headers=driver_user["headers"])
    assert res.status_code == 403
