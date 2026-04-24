import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_201(anon_client: AsyncClient) -> None:
    r = await anon_client.post(
        "/api/v1/auth/register",
        json={
            "email": "reg@example.com",
            "full_name": "Reg",
            "password": "s3cret!!",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "reg@example.com"


@pytest.mark.asyncio
async def test_register_duplicate(anon_client: AsyncClient) -> None:
    body = {
        "email": "dup@example.com",
        "full_name": "A",
        "password": "p1",
    }
    r1 = await anon_client.post("/api/v1/auth/register", json=body)
    assert r1.status_code == 201
    r2 = await anon_client.post("/api/v1/auth/register", json=body)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_200(anon_client: AsyncClient) -> None:
    await anon_client.post(
        "/api/v1/auth/register",
        json={
            "email": "log@example.com",
            "full_name": "L",
            "password": "mypass",
        },
    )
    r = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": "log@example.com", "password": "mypass"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(anon_client: AsyncClient) -> None:
    await anon_client.post(
        "/api/v1/auth/register",
        json={
            "email": "w@example.com",
            "full_name": "W",
            "password": "right",
        },
    )
    r = await anon_client.post(
        "/api/v1/auth/login",
        json={"email": "w@example.com", "password": "wrong"},
    )
    assert r.status_code == 401
