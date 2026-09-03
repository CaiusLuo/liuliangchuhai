from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.domain.product import Product


class ListProducts:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def execute(self) -> tuple[Product, ...]:
        return await self._repository.list_products()
