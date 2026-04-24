import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_task_crud_and_filters(test_client: AsyncClient) -> None:
    c = test_client
    lr = await c.post("/api/v1/lists", json={"name": "L", "description": None})
    lid = lr.json()["id"]
    t = await c.post(
        f"/api/v1/lists/{lid}/tasks",
        json={
            "title": "T",
            "description": None,
            "priority": "low",
        },
    )
    assert t.status_code == 201
    tid = t.json()["id"]
    g = await c.get(f"/api/v1/lists/{lid}/tasks/{tid}")
    assert g.status_code == 200
    st = await c.get(
        f"/api/v1/lists/{lid}/tasks",
        params={"status": "pending"},
    )
    assert st.status_code == 200
    pr = await c.get(
        f"/api/v1/lists/{lid}/tasks",
        params={"priority": "low"},
    )
    assert pr.status_code == 200
    p = await c.patch(
        f"/api/v1/lists/{lid}/tasks/{tid}/status",
        json={"new_status": "in_progress"},
    )
    assert p.status_code == 200
    d = await c.delete(f"/api/v1/lists/{lid}/tasks/{tid}")
    assert d.status_code == 204


@pytest.mark.asyncio
async def test_invalid_status_transition_422(
    test_client: AsyncClient,
) -> None:
    c = test_client
    lr = await c.post("/api/v1/lists", json={"name": "L2", "description": None})
    lid = lr.json()["id"]
    t = await c.post(
        f"/api/v1/lists/{lid}/tasks",
        json={"title": "T", "priority": "low"},
    )
    tid = t.json()["id"]
    r = await c.patch(
        f"/api/v1/lists/{lid}/tasks/{tid}/status",
        json={"new_status": "done"},
    )
    assert r.status_code == 422
