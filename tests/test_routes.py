def _route_payload(vehicle_id: str, **overrides) -> dict:
    payload = {
        "origin": "Istanbul",
        "destination": "Ankara",
        "distance_km": 450,
        "vehicle_id": vehicle_id,
        "expected_revenue": 1000,
        "stops": [],
    }
    payload.update(overrides)
    return payload


def test_admin_can_create_route(client, admin_user, active_vehicle):
    res = client.post(
        "/api/v1/routes",
        headers=admin_user["headers"],
        json=_route_payload(active_vehicle["id"]),
    )
    assert res.status_code == 201
    assert res.json()["origin"] == "Istanbul"
    assert res.json()["destination"] == "Ankara"


def test_create_route_requires_existing_vehicle_id(client, admin_user):
    fake_vehicle_id = "0" * 24
    res = client.post(
        "/api/v1/routes",
        headers=admin_user["headers"],
        json=_route_payload(fake_vehicle_id),
    )
    assert res.status_code == 404


def test_route_list_response_format(client, admin_user):
    res = client.get("/api/v1/routes", headers=admin_user["headers"])
    assert res.status_code == 200
    body = res.json()
    assert set(["items", "total", "limit", "offset", "has_more"]).issubset(body.keys())
    assert isinstance(body["items"], list)


def test_driver_sees_only_own_routes(client, admin_user, driver_user, another_driver_user, active_vehicle):
    own_route = client.post(
        "/api/v1/routes",
        headers=admin_user["headers"],
        json=_route_payload(active_vehicle["id"], assigned_driver_id=driver_user["id"]),
    ).json()
    other_route = client.post(
        "/api/v1/routes",
        headers=admin_user["headers"],
        json=_route_payload(active_vehicle["id"], assigned_driver_id=another_driver_user["id"]),
    ).json()

    res = client.get("/api/v1/routes/my-routes", headers=driver_user["headers"])
    assert res.status_code == 200
    route_ids = [r["id"] for r in res.json()["items"]]
    assert own_route["id"] in route_ids
    assert other_route["id"] not in route_ids


def test_admin_can_assign_driver_to_route(client, admin_user, driver_user, active_vehicle):
    route = client.post(
        "/api/v1/routes",
        headers=admin_user["headers"],
        json=_route_payload(active_vehicle["id"]),
    ).json()

    res = client.patch(
        f"/api/v1/routes/{route['id']}/assign-driver",
        headers=admin_user["headers"],
        json={"driver_id": driver_user["id"]},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "assigned"
    assert res.json()["assigned_driver_id"] == driver_user["id"]
