def test_register_success(client, email_factory):
    email = email_factory("register")
    res = client.post(
        "/api/v1/auth/register",
        json={"full_name": "New User", "email": email, "password": "Test1234", "role": "driver"},
    )
    assert res.status_code == 201
    assert res.json()["email"] == email
    assert res.json()["role"] == "driver"


def test_login_success(client, email_factory):
    email = email_factory("login")
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Login User", "email": email, "password": "Test1234", "role": "driver"},
    )
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "Test1234"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_fails(client, email_factory):
    email = email_factory("wrongpass")
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Wrong Pass User", "email": email, "password": "Test1234", "role": "driver"},
    )
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "IncorrectPassword"})
    assert res.status_code == 401


def test_protected_endpoint_without_token_fails(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code in (401, 403)


def test_update_profile_changes_full_name(client, email_factory):
    email = email_factory("update-profile")
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Old Name", "email": email, "password": "Test1234", "role": "driver"},
    )
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Test1234"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = client.patch("/api/v1/auth/me", headers=headers, json={"full_name": "New Name"})
    assert res.status_code == 200
    assert res.json()["full_name"] == "New Name"
    assert res.json()["email"] == email

    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.json()["full_name"] == "New Name"


def test_update_profile_requires_auth(client):
    res = client.patch("/api/v1/auth/me", json={"full_name": "No Auth"})
    assert res.status_code in (401, 403)
