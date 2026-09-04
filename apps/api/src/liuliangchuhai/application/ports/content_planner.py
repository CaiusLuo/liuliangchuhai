from typing import Protocol

from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


class ContentPlannerPort(Protocol):
    """Application-owned capability for planning downstream content materials."""

    async def create_content_plan(
        self,
        product: Product,
        market: MarketContext,
        analysis: ProductMarketAnalysis,
        context: ContentContext,
    ) -> ContentGenerationPlan: ...
