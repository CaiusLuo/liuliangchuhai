from unittest.mock import AsyncMock

import pytest
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo
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


@pytest.mark.asyncio
async def test_analysis_by_id_reuses_the_containers_use_cases(
    monkeypatch: pytest.MonkeyPatch,
    products: tuple[Product, ...],
    product_analysis_result: ProductMarketAnalysis,
) -> None:
    container = build_container(Settings(_env_file=None, llm_provider="mock"))
    lookup = AsyncMock(return_value=products[0])
    analyze = AsyncMock(return_value=product_analysis_result)
    monkeypatch.setattr(container.get_product, "execute", lookup)
    monkeypatch.setattr(container.analyze_product, "execute", analyze)
    market = MarketContext(country="Vietnam")

    result = await container.analyze_product_by_id.execute(products[0].id, market)

    lookup.assert_awaited_once_with(products[0].id)
    analyze.assert_awaited_once_with(products[0], market)
    assert analyze.await_args.args[0] is products[0]
    assert analyze.await_args.args[1] is market
    assert result is product_analysis_result


@pytest.mark.asyncio
async def test_generation_reuses_the_containers_digital_human(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    container = build_container(Settings(_env_file=None, digital_human_provider="mock"))
    expected = GeneratedVideo("mock://test/container-video.mp4")
    generate = AsyncMock(return_value=expected)
    monkeypatch.setattr(container.digital_human, "generate", generate)
    generation = DigitalHumanGenerationInput(script="Demo script", language="English")

    result = await container.generate_digital_human.execute(generation)

    generate.assert_awaited_once_with(generation)
    assert generate.await_args.args[0] is generation
    assert result is expected
