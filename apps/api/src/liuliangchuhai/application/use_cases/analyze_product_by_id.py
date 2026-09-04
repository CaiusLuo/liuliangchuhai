from liuliangchuhai.application.use_cases.analyze_product import AnalyzeProductUseCase
from liuliangchuhai.application.use_cases.get_product import GetProduct
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis


class AnalyzeProductByIdUseCase:
    def __init__(self, get_product: GetProduct, analyze_product: AnalyzeProductUseCase) -> None:
        self._get_product = get_product
        self._analyze_product = analyze_product

    async def execute(self, product_id: str, market: MarketContext) -> ProductMarketAnalysis:
        product = await self._get_product.execute(product_id)
        return await self._analyze_product.execute(product, market)
