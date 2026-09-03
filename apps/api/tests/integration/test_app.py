import pytest
from httpx import ASGITransport, AsyncClient
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings


@pytest.mark.asyncio
async def test_app_boots_and_health_uses_wired_providers() -> None:
    app = create_app(Settings(_env_file=None))

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "providers": {
            "llm": {"provider": "mock", "available": True},
            "digital_human": {"provider": "mock", "available": True},
        },
    }
