from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.domain.product import Product


class ProductNotFound(LookupError):
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Product not found: {product_id!r}")


class GetProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def execute(self, product_id: str) -> Product:
        product = await self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFound(product_id)
        return product
