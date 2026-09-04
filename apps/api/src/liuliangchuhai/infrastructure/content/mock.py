from liuliangchuhai.application.ports.content_planner import ContentPlannerPort
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


class MockContentPlannerAdapter(ContentPlannerPort):
    """Deterministic demo materials without provider calls or analysis interpretation."""

    async def create_content_plan(
        self,
        product: Product,
        market: MarketContext,
        analysis: ProductMarketAnalysis,
        context: ContentContext,
    ) -> ContentGenerationPlan:
        subject = f"{product.name} in {market.country} (target language: {context.target_language})"
        return ContentGenerationPlan(
            key_selling_points=(f"Demo selling point for {subject}",),
            image_prompt=f"Demo product image prompt for {subject}",
            short_video_idea=f"Demo product introduction concept for {subject}",
            short_video_prompt=f"Demo product introduction video prompt for {subject}",
            live_script=f"Demo spoken introduction for {subject}",
            social_caption=f"Demo social caption for {subject}",
        )
