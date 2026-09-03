from typing import Protocol

from liuliangchuhai.domain.product import Product


class ProductRepository(Protocol):
    """Read-only access to the shared catalog of canonical products."""

    async def list_products(self) -> tuple[Product, ...]:
        """Return an immutable catalog in curated order, or () when empty."""
        ...

    async def get_by_id(self, product_id: str) -> Product | None:
        """Return the exact case-sensitive ID match, or None when absent."""
        ...
