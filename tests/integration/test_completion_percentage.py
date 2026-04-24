import pytest
from httpx import AsyncClient

from app.domain.value_objects.status import TaskStatus


@pytest.mark.asyncio
async def test_completion_50(
    test_client: AsyncClient,
) -> None:
    c = test_client
    lr = await c.post(
        "/api/v1/lists", json={"name": "C", "description": None}
    )
    lid = lr.json()["id"]
    for _i, st in enumerate(
        [
            TaskStatus.DONE,
            TaskStatus.DONE,
            TaskStatus.IN_PROGRESS,
            TaskStatus.PENDING,
        ]
    ):
        r = await c.post(
            f"/api/v1/lists/{lid}/tasks",
            json={
                "title": f"t{_i}",
                "priority": "medium",
                "status": st.value,
            },
        )
        assert r.status_code == 201
    r2 = await c.get(f"/api/v1/lists/{lid}/tasks")
    assert r2.status_code == 200
    data = r2.json()
    assert data["completion_percentage"] == 50.0
