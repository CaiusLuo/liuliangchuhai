from __future__ import annotations

import ast
import inspect
import socket
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest
from liuliangchuhai.domain.market_analysis import (
    MarketContext,
    ProductMarketAnalysis,
    RecommendationLevel,
)
from liuliangchuhai.domain.product import Product
from liuliangchuhai.infrastructure.content import mock as content_mock

if TYPE_CHECKING:
    from liuliangchuhai.application.ports.content_planner import ContentPlannerPort
    from liuliangchuhai.domain.content_plan import ContentGenerationPlan


def test_mock_has_no_random_or_clock_dependencies() -> None:
    # Repeat equality alone can miss a seeded RNG or a clock rounded to seconds.
    # This check is scoped to the demo adapter, not the repository or event loop.
    forbidden = {"random", "secrets", "time", "datetime"}
    for node in ast.walk(ast.parse(inspect.getsource(content_mock))):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module or ""]
        else:
            continue
        assert not forbidden.intersection(module.split(".")[0] for module in modules), (
            f"Mock content planner imports randomness or a clock at line {node.lineno}"
        )


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_call(*args: object, **kwargs: object) -> None:
        pytest.fail("MockContentPlannerAdapter attempted an external network call")

    monkeypatch.setattr(socket, "create_connection", unexpected_call)
    monkeypatch.setattr(socket, "getaddrinfo", unexpected_call)
    monkeypatch.setattr(socket.socket, "connect", unexpected_call)
    monkeypatch.setattr(socket.socket, "connect_ex", unexpected_call)


@pytest.fixture
def analysis() -> ProductMarketAnalysis:
    return ProductMarketAnalysis(
        recommendation=RecommendationLevel.CAUTION,
        score=50,
        summary="Test analysis without verified market claims.",
        target_audiences=(),
        strengths=(),
        risks=(),
        cultural_advantages=(),
        marketing_suggestions=(),
        content_directions=(),
    )


def assert_valid_demo_plan(plan: ContentGenerationPlan) -> None:
    from liuliangchuhai.domain.content_plan import ContentGenerationPlan

    assert isinstance(plan, ContentGenerationPlan)
    assert isinstance(plan.key_selling_points, tuple)
    assert len(plan.key_selling_points) >= 1
    materials = [
        *plan.key_selling_points,
        plan.image_prompt,
        plan.short_video_idea,
        plan.short_video_prompt,
        plan.live_script,
        plan.social_caption,
    ]
    assert all(isinstance(value, str) and value.strip() for value in materials)
    combined = " ".join(materials).casefold()
    assert "demo" in combined or "mock" in combined


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "product_index, country, language", [(0, "Vietnam", "Tiếng Việt"), (1, "Thailand", "Thai")]
)
async def test_mock_returns_valid_repeatable_demo_plan_without_network(
    products: tuple[Product, ...],
    analysis: ProductMarketAnalysis,
    product_index: int,
    country: str,
    language: str,
) -> None:
    from liuliangchuhai.domain.content_plan import ContentContext

    adapter: ContentPlannerPort = content_mock.MockContentPlannerAdapter()
    product = products[product_index]
    market = MarketContext(country=country)
    context = ContentContext(target_language=language)

    first = await adapter.create_content_plan(product, market, analysis, context)
    second = await adapter.create_content_plan(product, market, analysis, context)
    fresh = await content_mock.MockContentPlannerAdapter().create_content_plan(
        product, market, analysis, context
    )

    assert_valid_demo_plan(first)
    assert first == second == fresh


@pytest.mark.asyncio
async def test_mock_does_not_rank_or_branch_on_analysis_score_and_recommendation(
    products: tuple[Product, ...], analysis: ProductMarketAnalysis
) -> None:
    from liuliangchuhai.domain.content_plan import ContentContext

    adapter = content_mock.MockContentPlannerAdapter()
    market = MarketContext(country="Vietnam")
    context = ContentContext(target_language="English")
    baseline = await adapter.create_content_plan(products[0], market, analysis, context)

    for recommendation in RecommendationLevel:
        for score in (0, 50, 100):
            varied = replace(analysis, recommendation=recommendation, score=score)
            assert (
                await adapter.create_content_plan(products[0], market, varied, context) == baseline
            )
