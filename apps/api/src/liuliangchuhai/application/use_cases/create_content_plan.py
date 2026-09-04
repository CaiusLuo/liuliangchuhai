from liuliangchuhai.application.ports.content_planner import ContentPlannerPort
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


class CreateContentPlanUseCase:
    def __init__(self, planner: ContentPlannerPort) -> None:
        self._planner = planner

    async def execute(
        self,
        product: Product,
        market: MarketContext,
        analysis: ProductMarketAnalysis,
        context: ContentContext,
    ) -> ContentGenerationPlan:
        return await self._planner.create_content_plan(product, market, analysis, context)
