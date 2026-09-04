import pytest
from liuliangchuhai.application.use_cases.create_content_plan import CreateContentPlanUseCase
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import (
    MarketContext,
    ProductMarketAnalysis,
    RecommendationLevel,
)
from liuliangchuhai.domain.product import Product


class SpyContentPlanner:
    """Only the planning capability is available; no LLM, repository, or media API."""

    def __init__(self, result: ContentGenerationPlan) -> None:
        self.result = result
        self.calls: list[tuple[Product, MarketContext, ProductMarketAnalysis, ContentContext]] = []

    async def create_content_plan(
        self,
        product: Product,
        market: MarketContext,
        analysis: ProductMarketAnalysis,
        context: ContentContext,
    ) -> ContentGenerationPlan:
        self.calls.append((product, market, analysis, context))
        return self.result


@pytest.mark.asyncio
@pytest.mark.parametrize("recommendation", list(RecommendationLevel))
@pytest.mark.parametrize("score", [0, 50, 100])
async def test_use_case_forwards_all_exact_objects_once_and_returns_exact_plan(
    products: tuple[Product, ...], recommendation: RecommendationLevel, score: int
) -> None:
    product = products[0]
    market = MarketContext(country="Vietnam", target_audience="Students")
    analysis = ProductMarketAnalysis(
        recommendation=recommendation,
        score=score,
        summary="Test analysis; no relationship between score and recommendation is assumed.",
        target_audiences=(),
        strengths=(),
        risks=(),
        cultural_advantages=(),
        marketing_suggestions=(),
        content_directions=(),
    )
    context = ContentContext(target_language="Tiếng Việt")
    result = ContentGenerationPlan(
        key_selling_points=("Test selling point",),
        image_prompt="Test image material",
        short_video_idea="Test video concept",
        short_video_prompt="Test video material",
        live_script="Test spoken material",
        social_caption="Test caption",
    )
    planner = SpyContentPlanner(result)

    actual = await CreateContentPlanUseCase(planner).execute(product, market, analysis, context)

    assert actual is result
    assert len(planner.calls) == 1
    forwarded = planner.calls[0]
    assert forwarded[0] is product
    assert forwarded[1] is market
    assert forwarded[2] is analysis
    assert forwarded[3] is context
