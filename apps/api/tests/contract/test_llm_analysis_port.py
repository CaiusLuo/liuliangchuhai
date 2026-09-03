import inspect

import pytest
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.domain.product import Product
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter


@pytest.mark.parametrize("owner", [LLMPort, MockLLMAdapter])
def test_llm_port_and_mock_expose_only_business_analysis_inputs(owner: type) -> None:
    assert inspect.iscoroutinefunction(owner.status)
    assert tuple(inspect.signature(owner.status).parameters) == ("self",)
    analyze = getattr(owner, "analyze_product_market", None)
    assert inspect.iscoroutinefunction(analyze), (
        f"{owner.__name__} lacks async analyze_product_market"
    )
    assert tuple(inspect.signature(analyze).parameters) == ("self", "product", "market")


@pytest.mark.asyncio
async def test_mock_preserves_status_and_produces_valid_deterministic_analysis(
    products: tuple[Product, ...],
) -> None:
    # Local import keeps the missing-method checks runnable during the RED phase.
    from liuliangchuhai.domain.market_analysis import (
        MarketContext,
        ProductMarketAnalysis,
        RecommendationLevel,
    )

    adapter: LLMPort = MockLLMAdapter()
    market = MarketContext(country="Vietnam")
    expected_status = ProviderStatus(provider="mock", available=True)
    assert await adapter.status() == expected_status

    first = await adapter.analyze_product_market(products[0], market)
    second = await adapter.analyze_product_market(products[0], market)
    fresh = await MockLLMAdapter().analyze_product_market(products[0], market)

    assert isinstance(first, ProductMarketAnalysis)
    assert first == second == fresh
    assert isinstance(first.recommendation, RecommendationLevel)
    assert type(first.score) is int and 0 <= first.score <= 100
    assert isinstance(first.summary, str) and first.summary.strip()
    for field in (
        "target_audiences",
        "strengths",
        "risks",
        "cultural_advantages",
        "marketing_suggestions",
        "content_directions",
    ):
        items = getattr(first, field)
        assert isinstance(items, tuple)
        assert all(isinstance(item, str) and item.strip() for item in items)
    assert await adapter.status() == expected_status
