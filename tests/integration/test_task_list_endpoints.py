import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_crud(test_client: AsyncClient) -> None:
    c = test_client
    r = await c.post(
        "/api/v1/lists", json={"name": "My list", "description": "d"}
    )
    assert r.status_code == 201
    list_id = r.json()["id"]
    g = await c.get(f"/api/v1/lists/{list_id}")
    assert g.status_code == 200
    u = await c.put(
        f"/api/v1/lists/{list_id}",
        json={"name": "Updated", "description": "x"},
    )
    assert u.status_code == 200
    assert u.json()["name"] == "Updated"
    d = await c.delete(f"/api/v1/lists/{list_id}")
    assert d.status_code == 204
    n = await c.get(f"/api/v1/lists/{list_id}")
    assert n.status_code == 404


@pytest.mark.asyncio
async def test_get_only_owned(
    test_client: AsyncClient, sample_user
) -> None:  # noqa: ANN001
    r = await test_client.get("/api/v1/lists")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_get_missing_list_404(
    test_client: AsyncClient,
) -> None:
    import uuid

    r = await test_client.get(
        f"/api/v1/lists/{uuid.uuid4()}"
    )
    assert r.status_code == 404
