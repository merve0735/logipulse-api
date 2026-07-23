def _create_route_with_stop(client, admin_user, active_vehicle, driver_id: str) -> dict:
    payload = {
        "origin": "Istanbul",
        "destination": "Izmir",
        "distance_km": 300,
        "vehicle_id": active_vehicle["id"],
        "expected_revenue": 800,
        "assigned_driver_id": driver_id,
        "stops": [
            {
                "sequence_number": 1,
                "customer_name": "Ayse Yilmaz",
                "address": "Kadikoy, Istanbul",
            }
        ],
    }
    res = client.post("/api/v1/routes", headers=admin_user["headers"], json=payload)
    return res.json()


def test_driver_can_deliver_own_stop(client, admin_user, driver_user, active_vehicle):
    route = _create_route_with_stop(client, admin_user, active_vehicle, driver_user["id"])
    stop_id = route["stops"][0]["id"]

    res = client.patch(
        f"/api/v1/routes/{route['id']}/stops/{stop_id}/deliver",
        headers=driver_user["headers"],
        json={"recipient_name": "Ayse Yilmaz"},
    )
    assert res.status_code == 200
    delivered_stop = next(s for s in res.json()["stops"] if s["id"] == stop_id)
    assert delivered_stop["status"] == "delivered"
    assert delivered_stop["proof_of_delivery"]["recipient_name"] == "Ayse Yilmaz"


def test_deliver_stop_requires_recipient_name(client, admin_user, driver_user, active_vehicle):
    route = _create_route_with_stop(client, admin_user, active_vehicle, driver_user["id"])
    stop_id = route["stops"][0]["id"]

    res = client.patch(
        f"/api/v1/routes/{route['id']}/stops/{stop_id}/deliver",
        headers=driver_user["headers"],
        json={},
    )
    assert res.status_code == 422


def test_driver_cannot_modify_others_stop(client, admin_user, driver_user, another_driver_user, active_vehicle):
    route = _create_route_with_stop(client, admin_user, active_vehicle, driver_user["id"])
    stop_id = route["stops"][0]["id"]

    res = client.patch(
        f"/api/v1/routes/{route['id']}/stops/{stop_id}/deliver",
        headers=another_driver_user["headers"],
        json={"recipient_name": "Someone Else"},
    )
    assert res.status_code == 403
