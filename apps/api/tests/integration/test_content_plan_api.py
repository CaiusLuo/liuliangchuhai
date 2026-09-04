from dataclasses import asdict
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.container import Container, build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.infrastructure.content.mock import MockContentPlannerAdapter


@pytest.fixture
def content_request(product_analysis_result: ProductMarketAnalysis) -> dict:
    return {
        "product_id": "liuzhou-luosifen",
        "country": "Vietnam",
        "target_audience": "Students",
        "market_notes": "Sample packs",
        "target_language": "Tiếng Việt",
        "analysis": asdict(product_analysis_result),
    }


@pytest.fixture
def container() -> Container:
    return build_container(Settings(_env_file=None))


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch, container: Container) -> FastAPI:
    monkeypatch.setattr("liuliangchuhai.bootstrap.app.build_container", lambda settings: container)
    return create_app(Settings(_env_file=None))


@pytest.mark.asyncio
async def test_http_maps_supplied_analysis_and_uses_canonical_product_without_llm(
    app: FastAPI,
    container: Container,
    monkeypatch: pytest.MonkeyPatch,
    content_request: dict,
    product_analysis_result: ProductMarketAnalysis,
) -> None:
    assert isinstance(container.content_planner, MockContentPlannerAdapter)
    product = await container.get_product.execute(content_request["product_id"])
    lookup = AsyncMock(wraps=container.get_product.execute)
    planner = AsyncMock(wraps=container.content_planner.create_content_plan)
    llm = AsyncMock(side_effect=AssertionError("Content planning must not rerun analysis"))
    monkeypatch.setattr(container.get_product, "execute", lookup)
    monkeypatch.setattr(container.content_planner, "create_content_plan", planner)
    monkeypatch.setattr(container.llm, "analyze_product_market", llm)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/content-plan", json=content_request)

    assert response.status_code == 200
    lookup.assert_awaited_once_with(product.id)
    planner.assert_awaited_once_with(
        product,
        MarketContext("Vietnam", "Students", "Sample packs"),
        product_analysis_result,
        ContentContext("Tiếng Việt"),
    )
    assert planner.await_args.args[0] is product
    llm.assert_not_called()
    body = response.json()
    assert set(body) == {
        "key_selling_points",
        "image_prompt",
        "short_video_idea",
        "short_video_prompt",
        "live_script",
        "social_caption",
    }
    expected = await MockContentPlannerAdapter().create_content_plan(
        product, MarketContext("Vietnam"), product_analysis_result, ContentContext("Tiếng Việt")
    )
    assert body == {**asdict(expected), "key_selling_points": list(expected.key_selling_points)}


@pytest.mark.asyncio
async def test_missing_product_is_stable_404_without_planning(
    app: FastAPI,
    container: Container,
    monkeypatch: pytest.MonkeyPatch,
    content_request: dict,
) -> None:
    planner = AsyncMock()
    monkeypatch.setattr(container.content_planner, "create_content_plan", planner)
    content_request["product_id"] = "missing-private-id"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/content-plan", json=content_request)
    assert response.status_code == 404
    assert response.json() == {"code": "product_not_found", "message": "Product not found"}
    planner.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [RuntimeError("private provider secret"), ValueError("private invalid output")]
)
async def test_unexpected_failure_is_safe_500(
    app: FastAPI,
    container: Container,
    monkeypatch: pytest.MonkeyPatch,
    content_request: dict,
    failure: Exception,
) -> None:
    planner = AsyncMock(side_effect=failure)
    monkeypatch.setattr(container.content_planner, "create_content_plan", planner)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/content-plan", json=content_request)
    assert response.status_code == 500
    assert response.json() == {
        "code": "content_planning_failed",
        "message": "Unable to create content plan. Please try again.",
    }
    planner.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field,value",
    [
        ("product_id", " "),
        ("country", " "),
        ("target_language", " "),
        ("target_language", 123),
        ("target_audience", " "),
        ("market_notes", False),
        ("product", {"name": "Forged"}),
        ("analysis", {}),
        ("analysis", None),
        ("analysis.score", True),
        ("analysis.score", 101),
        ("analysis.score", -1),
        ("analysis.score", "50"),
        ("analysis.recommendation", "unknown"),
        ("analysis.summary", " "),
        ("analysis.strengths", [" "]),
        ("analysis.risks", "risk"),
        ("analysis.provider", "secret"),
    ],
)
async def test_invalid_request_never_invokes_use_case(
    app: FastAPI,
    container: Container,
    monkeypatch: pytest.MonkeyPatch,
    content_request: dict,
    field: str,
    value: object,
) -> None:
    use_case = AsyncMock()
    monkeypatch.setattr(container.create_content_plan_by_id, "execute", use_case)
    if field.startswith("analysis."):
        content_request["analysis"][field.split(".")[1]] = value
    else:
        content_request[field] = value
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/content-plan", json=content_request)
    assert response.status_code == 422
    use_case.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("optional", [{}, {"target_audience": None, "market_notes": None}])
async def test_optional_context_and_empty_analysis_lists_are_preserved(
    app: FastAPI,
    container: Container,
    monkeypatch: pytest.MonkeyPatch,
    content_request: dict,
    optional: dict,
) -> None:
    del content_request["target_audience"]
    del content_request["market_notes"]
    content_request.update(optional)
    for key, value in content_request["analysis"].items():
        if isinstance(value, tuple):
            content_request["analysis"][key] = []
    plan = ContentGenerationPlan(("Point",), "Image", "Idea", "Video", "Live", "Social")
    use_case = AsyncMock(return_value=plan)
    monkeypatch.setattr(container.create_content_plan_by_id, "execute", use_case)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/content-plan", json=content_request)
    assert response.status_code == 200
    assert use_case.await_args.args[1] == MarketContext("Vietnam")
    assert use_case.await_args.args[2].strengths == ()


@pytest.mark.asyncio
async def test_normal_app_demo_flow_is_repeatable(content_request: dict) -> None:
    app = create_app(Settings(_env_file=None))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        products = (await client.get("/products")).json()["items"]
        content_request["product_id"] = products[0]["id"]
        analysis = await client.post(
            "/product-analysis",
            json={
                key: content_request[key]
                for key in ("product_id", "country", "target_audience", "market_notes")
            },
        )
        assert analysis.status_code == 200
        content_request["analysis"] = analysis.json()
        first = await client.post("/content-plan", json=content_request)
        second = await client.post("/content-plan", json=content_request)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert all(first.json().values())
