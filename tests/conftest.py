import os
import uuid

# Testler gerçek "logipulse" veritabanına asla dokunmasın diye .env/CI ayarları
# ne olursa olsun burada zorla ayrı bir test veritabanı kullanılır.
os.environ["MONGO_DB_NAME"] = "logipulse_test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@logipulse.demo"


def register_and_login(client: TestClient, role: str) -> dict:
    email = unique_email(role)
    password = "Test1234"
    register_res = client.post(
        "/api/v1/auth/register",
        json={"full_name": f"Test {role.title()}", "email": email, "password": password, "role": role},
    )
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    return {
        "id": register_res.json()["id"],
        "email": email,
        "password": password,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture(scope="session")
def admin_user(client):
    return register_and_login(client, "admin")


@pytest.fixture(scope="session")
def driver_user(client):
    return register_and_login(client, "driver")


@pytest.fixture
def another_driver_user(client):
    return register_and_login(client, "driver")


@pytest.fixture
def email_factory():
    return unique_email


@pytest.fixture
def active_vehicle(client, admin_user):
    plate = f"TST{uuid.uuid4().hex[:6].upper()}"
    res = client.post(
        "/api/v1/vehicles",
        headers=admin_user["headers"],
        json={
            "plate_number": plate,
            "vehicle_type": "electric_van",
            "capacity_kg": 500,
            "average_cost_per_km": 2.5,
            "average_carbon_per_km": 0.05,
            "is_active": True,
        },
    )
    return res.json()
