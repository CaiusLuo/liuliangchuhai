from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


class AnalyzeProductUseCase:
    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    async def execute(self, product: Product, market: MarketContext) -> ProductMarketAnalysis:
        return await self._llm.analyze_product_market(product, market)
