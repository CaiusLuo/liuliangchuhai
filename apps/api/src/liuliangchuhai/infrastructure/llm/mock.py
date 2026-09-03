from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.domain.market_analysis import (
    MarketContext,
    ProductMarketAnalysis,
    RecommendationLevel,
)
from liuliangchuhai.domain.product import Product


class MockLLMAdapter:
    """Deterministic, key-free adapter used by development and tests."""

    async def status(self) -> ProviderStatus:
        return ProviderStatus(provider="mock", available=True)

    async def analyze_product_market(
        self, product: Product, market: MarketContext
    ) -> ProductMarketAnalysis:
        """Use fixed demo indicators without evaluating market fit."""
        return ProductMarketAnalysis(
            recommendation=RecommendationLevel.CAUTION,
            score=50,
            summary=(
                f"Demo analysis of {product.name} for {market.country}. "
                "Fixed mock heuristic only; not a prediction of market fit or sales."
            ),
            target_audiences=(market.target_audience,)
            if market.target_audience is not None
            else (),
            strengths=(),
            risks=("Mock output only; market assumptions have not been validated.",),
            cultural_advantages=(product.cultural_background,),
            marketing_suggestions=(),
            content_directions=(),
        )
