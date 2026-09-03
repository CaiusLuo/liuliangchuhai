from typing import Protocol

from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


class LLMPort(Protocol):
    """Application-owned availability and product-market analysis capabilities."""

    async def status(self) -> ProviderStatus:
        """Return provider availability without performing business behavior."""
        ...

    async def analyze_product_market(
        self, product: Product, market: MarketContext
    ) -> ProductMarketAnalysis:
        """Return validated analysis or raise LLMUnavailable / InvalidLLMResponse."""
        ...
