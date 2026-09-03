import pytest
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.application.ports.llm_errors import (
    InvalidLLMResponse,
    LLMError,
    LLMUnavailable,
)
from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.application.use_cases.analyze_product import AnalyzeProductUseCase
from liuliangchuhai.domain.market_analysis import (
    MarketContext,
    ProductMarketAnalysis,
    RecommendationLevel,
)
from liuliangchuhai.domain.product import Product


class FakeAnalysisLLM:
    """Test-only deterministic port implementation; never calls a provider."""

    def __init__(self, result: ProductMarketAnalysis, error: LLMError | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[Product, MarketContext]] = []

    async def status(self) -> ProviderStatus:
        return ProviderStatus(provider="fake", available=True)

    async def analyze_product_market(
        self, product: Product, market: MarketContext
    ) -> ProductMarketAnalysis:
        self.calls.append((product, market))
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture
def result() -> ProductMarketAnalysis:
    return ProductMarketAnalysis(
        recommendation=RecommendationLevel.CAUTION,
        score=50,
        summary="Test-only heuristic; market assumptions need validation.",
        target_audiences=(),
        strengths=(),
        risks=(),
        cultural_advantages=(),
        marketing_suggestions=(),
        content_directions=(),
    )


@pytest.mark.asyncio
async def test_analysis_forwards_exact_inputs_once_and_returns_result(
    products: tuple[Product, ...], result: ProductMarketAnalysis
) -> None:
    fake = FakeAnalysisLLM(result)
    llm: LLMPort = fake
    market = MarketContext(country="Vietnam", target_audience="Students")

    actual = await AnalyzeProductUseCase(llm).execute(products[0], market)

    assert actual is result
    assert len(fake.calls) == 1
    assert fake.calls[0][0] is products[0]
    assert fake.calls[0][1] is market


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [LLMUnavailable, InvalidLLMResponse])
async def test_application_failures_remain_visible_without_retry_or_fallback(
    products: tuple[Product, ...], result: ProductMarketAnalysis, error_type: type[LLMError]
) -> None:
    error = error_type("Analysis failed")
    fake = FakeAnalysisLLM(result, error=error)

    with pytest.raises(error_type) as captured:
        await AnalyzeProductUseCase(fake).execute(products[0], MarketContext(country="Vietnam"))

    assert captured.value is error
    assert isinstance(captured.value, LLMError)
    assert len(fake.calls) == 1
