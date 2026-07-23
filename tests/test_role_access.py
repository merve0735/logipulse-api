def test_driver_cannot_access_admin_endpoint(client, driver_user):
    res = client.get("/api/v1/dashboard/summary", headers=driver_user["headers"])
    assert res.status_code == 403


def test_admin_can_access_admin_endpoint(client, admin_user):
    res = client.get("/api/v1/dashboard/summary", headers=admin_user["headers"])
    assert res.status_code == 200
