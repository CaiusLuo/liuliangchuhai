from liuliangchuhai.application.use_cases.create_content_plan import CreateContentPlanUseCase
from liuliangchuhai.application.use_cases.get_product import GetProduct
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis


class CreateContentPlanByIdUseCase:
    def __init__(
        self, get_product: GetProduct, create_content_plan: CreateContentPlanUseCase
    ) -> None:
        self._get_product = get_product
        self._create_content_plan = create_content_plan

    async def execute(
        self,
        product_id: str,
        market: MarketContext,
        analysis: ProductMarketAnalysis,
        context: ContentContext,
    ) -> ContentGenerationPlan:
        product = await self._get_product.execute(product_id)
        return await self._create_content_plan.execute(product, market, analysis, context)
