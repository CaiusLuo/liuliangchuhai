import pytest
from liuliangchuhai.application.ports.llm_errors import (
    InvalidLLMResponse,
    LLMError,
    LLMUnavailable,
)
from liuliangchuhai.application.use_cases.analyze_product_by_id import AnalyzeProductByIdUseCase
from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


class FakeGetProduct:
    def __init__(
        self,
        product: Product,
        error: ProductNotFound | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.product = product
        self.error = error
        self.calls: list[str] = []
        self.events = events if events is not None else []

    async def execute(self, product_id: str) -> Product:
        self.calls.append(product_id)
        self.events.append("lookup")
        if self.error is not None:
            raise self.error
        return self.product


class FakeAnalyzeProduct:
    def __init__(
        self,
        result: ProductMarketAnalysis,
        error: LLMError | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[Product, MarketContext]] = []
        self.events = events if events is not None else []

    async def execute(self, product: Product, market: MarketContext) -> ProductMarketAnalysis:
        self.calls.append((product, market))
        self.events.append("analysis")
        if self.error is not None:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_by_id_forwards_exact_values_once_and_returns_same_result(
    products: tuple[Product, ...], product_analysis_result: ProductMarketAnalysis
) -> None:
    events: list[str] = []
    lookup = FakeGetProduct(products[0], events=events)
    analyze = FakeAnalyzeProduct(product_analysis_result, events=events)
    market = MarketContext(country="Vietnam", target_audience="Students")
    # No trimming/normalization belongs in this orchestrator.
    product_id = " Exact-Catalog-ID "

    result = await AnalyzeProductByIdUseCase(lookup, analyze).execute(product_id, market)

    assert lookup.calls == [product_id]
    assert len(analyze.calls) == 1
    assert analyze.calls[0][0] is lookup.product
    assert analyze.calls[0][1] is market
    assert result is product_analysis_result
    assert events == ["lookup", "analysis"]


@pytest.mark.asyncio
async def test_missing_product_propagates_without_calling_analysis(
    products: tuple[Product, ...], product_analysis_result: ProductMarketAnalysis
) -> None:
    error = ProductNotFound("missing")
    lookup = FakeGetProduct(products[0], error)
    analyze = FakeAnalyzeProduct(product_analysis_result)

    with pytest.raises(ProductNotFound) as captured:
        await AnalyzeProductByIdUseCase(lookup, analyze).execute(
            "missing", MarketContext(country="Vietnam")
        )

    assert captured.value is error
    assert lookup.calls == ["missing"]
    assert analyze.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [LLMUnavailable, InvalidLLMResponse])
async def test_analysis_failure_propagates_without_retry_or_fallback(
    products: tuple[Product, ...],
    product_analysis_result: ProductMarketAnalysis,
    error_type: type[LLMError],
) -> None:
    error = error_type("Application-visible failure")
    lookup = FakeGetProduct(products[0])
    analyze = FakeAnalyzeProduct(product_analysis_result, error)
    market = MarketContext(country="Vietnam")

    with pytest.raises(error_type) as captured:
        await AnalyzeProductByIdUseCase(lookup, analyze).execute(products[0].id, market)

    assert captured.value is error
    assert lookup.calls == [products[0].id]
    assert len(analyze.calls) == 1
    assert analyze.calls[0][0] is products[0]
    assert analyze.calls[0][1] is market
