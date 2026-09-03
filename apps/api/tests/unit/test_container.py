from unittest.mock import AsyncMock

import pytest
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter


def test_container_wires_mock_providers() -> None:
    container = build_container(Settings(_env_file=None))

    assert isinstance(container.llm, MockLLMAdapter)
    assert isinstance(container.digital_human, MockDigitalHumanAdapter)


@pytest.mark.asyncio
async def test_analysis_reuses_the_containers_llm(
    monkeypatch: pytest.MonkeyPatch, products: tuple[Product, ...]
) -> None:
    container = build_container(Settings(_env_file=None, llm_provider="mock"))
    analyze = AsyncMock(wraps=container.llm.analyze_product_market)
    monkeypatch.setattr(container.llm, "analyze_product_market", analyze)
    market = MarketContext(country="Vietnam")

    result = await container.analyze_product.execute(products[0], market)

    assert isinstance(result, ProductMarketAnalysis)
    analyze.assert_awaited_once_with(products[0], market)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("llm_provider", "unknown"),
        ("digital_human_provider", "unknown"),
    ],
)
def test_container_rejects_unknown_provider(field: str, value: str) -> None:
    settings = Settings(_env_file=None, **{field: value})

    with pytest.raises(ValueError, match=r"Unsupported .* provider"):
        build_container(settings)
