def test_admin_can_get_dashboard_summary(client, admin_user):
    res = client.get("/api/v1/dashboard/summary", headers=admin_user["headers"])
    assert res.status_code == 200
    assert "total_routes" in res.json()


def test_driver_cannot_get_dashboard_summary(client, driver_user):
    res = client.get("/api/v1/dashboard/summary", headers=driver_user["headers"])
    assert res.status_code == 403
