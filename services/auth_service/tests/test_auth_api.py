import pytest
from faker import Faker


pytestmark = pytest.mark.anyio

BASE = "/api/v1/auth"


async def test_register_success(client):
    fake = Faker()

    payload = {
        "email": fake.unique.email(),
        "password": "StrongPassw0rd!",
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    resp = await client.post(f"{BASE}/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "doctor"
    assert data["is_active"] is True
    assert "id" in data


async def test_register_duplicate_email(client):
    fake = Faker()

    email = fake.unique.email()
    payload = {
        "email": email,
        "password": "StrongPassw0rd!",
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    first = await client.post(f"{BASE}/register", json=payload)
    assert first.status_code == 201, first.text

    second = await client.post(f"{BASE}/register", json=payload)
    assert second.status_code == 400, second.text
    assert second.json().get("detail") == "Email already registered"


async def test_login_success(client):
    fake = Faker()

    email = fake.unique.email()
    password = "StrongPassw0rd!"
    # register first
    payload = {
        "email": email,
        "password": password,
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    r = await client.post(f"{BASE}/register", json=payload)
    assert r.status_code == 201, r.text

    # login
    form = {"username": email, "password": password}
    resp = await client.post(f"{BASE}/login", data=form)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data and data["access_token"]
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    fake = Faker()

    email = fake.unique.email()
    password = "StrongPassw0rd!"
    # register first
    payload = {
        "email": email,
        "password": password,
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    r = await client.post(f"{BASE}/register", json=payload)
    assert r.status_code == 201, r.text

    # login with wrong password
    form = {"username": email, "password": "WrongPassword!"}
    resp = await client.post(f"{BASE}/login", data=form)
    assert resp.status_code == 401, resp.text
    assert resp.json().get("detail") == "Incorrect email or password"


async def test_me_with_valid_token(client):
    fake = Faker()

    email = fake.unique.email()
    password = "StrongPassw0rd!"
    # register first
    payload = {
        "email": email,
        "password": password,
        "full_name": fake.name(),
        "workspace_name": f"{fake.last_name()} Clinic",
    }
    r = await client.post(f"{BASE}/register", json=payload)
    assert r.status_code == 201, r.text

    # login
    form = {"username": email, "password": password}
    resp = await client.post(f"{BASE}/login", data=form)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]

    # call /me
    headers = {"Authorization": f"Bearer {token}"}
    me = await client.get(f"{BASE}/me", headers=headers)
    assert me.status_code == 200, me.text
    data = me.json()
    assert data["email"] == email
    assert data["is_active"] is True


async def test_me_without_token(client):
    me = await client.get(f"{BASE}/me")
    assert me.status_code == 401, me.text
    assert me.json().get("detail") in ("Not authenticated", "Invalid authentication credentials")
