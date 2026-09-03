from unittest.mock import AsyncMock

import pytest
from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.application.use_cases.get_product import GetProduct, ProductNotFound
from liuliangchuhai.application.use_cases.list_products import ListProducts
from liuliangchuhai.domain.product import Product


@pytest.mark.asyncio
async def test_list_products_delegates_to_port(products: tuple[Product, ...]) -> None:
    repository = AsyncMock(spec=ProductRepository)
    repository.list_products.return_value = products

    assert await ListProducts(repository).execute() == products
    repository.list_products.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_product_delegates_exact_id_to_port(products: tuple[Product, ...]) -> None:
    repository = AsyncMock(spec=ProductRepository)
    repository.get_by_id.return_value = products[0]

    assert await GetProduct(repository).execute(products[0].id) is products[0]
    repository.get_by_id.assert_awaited_once_with(products[0].id)


@pytest.mark.asyncio
async def test_unknown_product_is_explicit() -> None:
    repository = AsyncMock(spec=ProductRepository)
    repository.get_by_id.return_value = None

    with pytest.raises(ProductNotFound, match="missing") as error:
        await GetProduct(repository).execute("missing")

    assert error.value.product_id == "missing"
    repository.get_by_id.assert_awaited_once_with("missing")


@pytest.mark.asyncio
async def test_repository_failure_is_not_reported_as_unknown_or_empty() -> None:
    repository = AsyncMock(spec=ProductRepository)
    repository.list_products.side_effect = RuntimeError("unavailable")
    repository.get_by_id.side_effect = RuntimeError("unavailable")

    with pytest.raises(RuntimeError, match="unavailable"):
        await ListProducts(repository).execute()
    with pytest.raises(RuntimeError, match="unavailable"):
        await GetProduct(repository).execute("missing")
