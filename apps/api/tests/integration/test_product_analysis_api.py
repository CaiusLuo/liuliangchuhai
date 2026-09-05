from collections.abc import Iterator, Sequence
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts
from httpx import ASGITransport, AsyncClient
from liuliangchuhai.application.ports.llm_errors import InvalidLLMResponse, LLMUnavailable
from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.application.use_cases.get_system_status import SystemStatus
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from pydantic import BaseModel
from starlette.routing import BaseRoute


@pytest.fixture
def product_analysis_json() -> dict[str, object]:
    return {
        "recommendation": "caution",
        "score": 50,
        "summary": "Test heuristic only; market assumptions need validation.",
        "target_audiences": ["Students", "Home cooks"],
        "strengths": ["Distinctive flavor"],
        "risks": ["Taste preferences need validation"],
        "cultural_advantages": ["Guangxi food heritage"],
        "marketing_suggestions": ["Test small sample packs"],
        "content_directions": ["Explain preparation"],
    }


class FakeAnalyzeProductById:
    def __init__(self, result: ProductMarketAnalysis) -> None:
        self.result = result
        self.error: Exception | None = None
        self.calls: list[tuple[str, MarketContext]] = []

    async def execute(self, product_id: str, market: MarketContext) -> ProductMarketAnalysis:
        self.calls.append((product_id, market))
        if self.error is not None:
            raise self.error
        return self.result


class FakeGetSystemStatus:
    async def execute(self) -> SystemStatus:
        return SystemStatus(
            llm=ProviderStatus(provider="mock", available=True),
            digital_human=ProviderStatus(provider="mock", available=True),
        )


@pytest.fixture
def analysis_use_case(product_analysis_result: ProductMarketAnalysis) -> FakeAnalyzeProductById:
    return FakeAnalyzeProductById(product_analysis_result)


@pytest.fixture
def analysis_app(
    monkeypatch: pytest.MonkeyPatch, analysis_use_case: FakeAnalyzeProductById
) -> FastAPI:
    # Supply app-level read dependencies, but fail if analysis invokes them.
    # No repository or lower-level analysis use case is exposed.
    container = SimpleNamespace(
        get_system_status=FakeGetSystemStatus(),
        reply_to_customer=SimpleNamespace(
            execute=AsyncMock(side_effect=AssertionError("Analysis must not invoke assistant"))
        ),
        analyze_product_by_id=analysis_use_case,
        create_content_plan_by_id=SimpleNamespace(execute=AsyncMock()),
        list_products=SimpleNamespace(
            execute=AsyncMock(side_effect=AssertionError("Analysis must not list products"))
        ),
        get_product=SimpleNamespace(
            execute=AsyncMock(side_effect=AssertionError("Analysis must use its orchestrator"))
        ),
    )
    monkeypatch.setattr("liuliangchuhai.bootstrap.app.build_container", lambda settings: container)
    return create_app(Settings(_env_file=None))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "optional",
    [
        {},
        {"target_audience": None, "market_notes": None},
        {"target_audience": "Students", "market_notes": "Test sample packs"},
    ],
)
async def test_post_analysis_maps_input_and_calls_one_use_case(
    analysis_app: FastAPI,
    analysis_use_case: FakeAnalyzeProductById,
    product_analysis_json: dict[str, object],
    optional: dict[str, str | None],
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=analysis_app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/product-analysis", json={"product_id": "luosifen", "country": "Vietnam", **optional}
        )

    assert response.status_code == 200
    assert response.json() == product_analysis_json
    assert analysis_use_case.calls == [("luosifen", MarketContext(country="Vietnam", **optional))]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "status", "code", "message"),
    [
        (ProductNotFound("private-id"), 404, "product_not_found", "Product not found"),
        (
            LLMUnavailable("Private provider SDK failure: secret diagnostic"),
            503,
            "llm_unavailable",
            "Analysis service is temporarily unavailable",
        ),
        (
            InvalidLLMResponse("Private malformed provider payload: secret diagnostic"),
            502,
            "invalid_llm_response",
            "Analysis service returned an invalid response",
        ),
    ],
)
async def test_application_errors_have_stable_public_bodies(
    analysis_app: FastAPI,
    analysis_use_case: FakeAnalyzeProductById,
    error: Exception,
    status: int,
    code: str,
    message: str,
) -> None:
    analysis_use_case.error = error
    async with AsyncClient(
        transport=ASGITransport(app=analysis_app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/product-analysis", json={"product_id": "private-id", "country": "Vietnam"}
        )

    assert response.status_code == status
    assert response.json() == {"code": code, "message": message}
    assert len(analysis_use_case.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"country": "Vietnam"},
        {"product_id": "luosifen"},
        {"product_id": " ", "country": "Vietnam"},
        {"product_id": "luosifen", "country": " "},
        {"product_id": 123, "country": "Vietnam"},
        {"product_id": "luosifen", "country": False},
        {"product_id": None, "country": "Vietnam"},
        {"product_id": "luosifen", "country": "Vietnam", "target_audience": " "},
        {"product_id": "luosifen", "country": "Vietnam", "market_notes": ["notes"]},
        {"product_id": "luosifen", "country": "Vietnam", "product": {"name": "Forged"}},
    ],
)
async def test_invalid_http_input_returns_422_without_invoking_analysis(
    analysis_app: FastAPI, analysis_use_case: FakeAnalyzeProductById, payload: dict[str, object]
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=analysis_app), base_url="http://test"
    ) as client:
        response = await client.post("/product-analysis", json=payload)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert "code" not in response.json()
    assert analysis_use_case.calls == []


@pytest.mark.asyncio
async def test_malformed_json_returns_422_without_invoking_analysis(
    analysis_app: FastAPI, analysis_use_case: FakeAnalyzeProductById
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=analysis_app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/product-analysis", content="{", headers={"Content-Type": "application/json"}
        )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert "code" not in response.json()
    assert analysis_use_case.calls == []


def iter_api_routes(routes: Sequence[BaseRoute]) -> Iterator[APIRoute]:
    # Let FastAPI resolve included routers without depending on private wrapper types.
    for context in iter_route_contexts(routes):
        route = context.original_route
        if isinstance(route, APIRoute):
            yield route
        yield from iter_api_routes(getattr(route, "routes", ()))


def test_route_uses_a_presentation_response_model(analysis_app: FastAPI) -> None:
    route = next(
        (
            route
            for route in iter_api_routes(analysis_app.routes)
            if isinstance(route, APIRoute)
            and route.path == "/product-analysis"
            and "POST" in route.methods
        ),
        None,
    )

    assert route is not None, "POST /product-analysis is missing"
    assert isinstance(route.response_model, type)
    assert issubclass(route.response_model, BaseModel)
    assert route.response_model.__name__ == "ProductMarketAnalysisResponse"
    assert route.response_model.__module__.startswith("liuliangchuhai.presentation.")


@pytest.mark.asyncio
async def test_health_remains_unchanged(
    analysis_app: FastAPI, analysis_use_case: FakeAnalyzeProductById
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=analysis_app), base_url="http://test"
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
    assert analysis_use_case.calls == []
