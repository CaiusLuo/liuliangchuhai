from collections.abc import Callable
from dataclasses import FrozenInstanceError

import pytest
from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.domain.product import Product


@pytest.mark.asyncio
async def test_repository_lists_and_retrieves_canonical_products(
    repository_factory: Callable[[tuple[Product, ...]], ProductRepository],
    products: tuple[Product, ...],
) -> None:
    repository = repository_factory(products)

    assert await repository.list_products() == products
    assert await repository.list_products() == products
    for product in products:
        result = await repository.get_by_id(product.id)
        assert type(result) is Product
        assert result == product


@pytest.mark.asyncio
async def test_repository_lookup_is_exact_and_missing_is_none(
    repository_factory: Callable[[tuple[Product, ...]], ProductRepository],
    products: tuple[Product, ...],
) -> None:
    repository = repository_factory(products)

    for product_id in ("missing", "", products[0].id.upper(), f" {products[0].id}"):
        assert await repository.get_by_id(product_id) is None


@pytest.mark.asyncio
async def test_repository_supports_empty_catalog(
    repository_factory: Callable[[tuple[Product, ...]], ProductRepository],
) -> None:
    repository = repository_factory(())

    assert await repository.list_products() == ()
    assert await repository.get_by_id("missing") is None


@pytest.mark.asyncio
async def test_repository_results_cannot_mutate_catalog(
    repository_factory: Callable[[tuple[Product, ...]], ProductRepository],
    products: tuple[Product, ...],
) -> None:
    repository = repository_factory(products)
    result = await repository.list_products()

    assert isinstance(result, tuple)
    with pytest.raises(FrozenInstanceError):
        result[0].name = "changed"  # type: ignore[misc]
    assert await repository.get_by_id(products[0].id) == products[0]
