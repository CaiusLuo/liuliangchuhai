from dataclasses import asdict, replace
from decimal import Decimal

import pytest
from liuliangchuhai.domain.product import Product
from liuliangchuhai.presentation.http.product_mappers import (
    to_product_list_response,
    to_product_response,
)
from liuliangchuhai.presentation.http.schemas import ProductListResponse, ProductResponse


def test_maps_every_field_and_preserves_product(products: tuple[Product, ...]) -> None:
    product = replace(products[0], images=("second.jpg", "first.jpg"))
    before = asdict(product)

    response = to_product_response(product)

    assert isinstance(response, ProductResponse)
    assert set(type(response).model_fields) == set(before)
    for field in (
        "id",
        "name",
        "category",
        "description",
        "origin",
        "cultural_background",
        "usage",
        "purchase_url",
    ):
        assert getattr(response, field) == getattr(product, field)
    assert type(response.images) is list
    assert response.images == ["second.jpg", "first.jpg"]
    assert type(response.ingredients) is list
    assert response.ingredients == list(product.ingredients)
    assert response.price == "12.50"
    assert asdict(product) == before
    # Response list mutation cannot affect the immutable domain collections.
    response.images.append("extra.jpg")
    response.ingredients.clear()
    assert asdict(product) == before


@pytest.mark.parametrize(
    ("price", "expected"),
    [(Decimal("12.50"), "12.50"), (Decimal("0"), "0"), (None, None)],
)
def test_price_is_exact_decimal_text_or_null(
    products: tuple[Product, ...], price: Decimal | None, expected: str | None
) -> None:
    response = to_product_response(replace(products[0], price=price, purchase_url=None))

    assert response.price == expected
    assert response.model_dump(mode="json")["price"] == expected
    assert response.purchase_url is None


def test_empty_domain_collections_map_to_lists(products: tuple[Product, ...]) -> None:
    response = to_product_response(replace(products[0], images=(), ingredients=()))

    assert response.images == []
    assert response.ingredients == []


@pytest.mark.parametrize("empty", [False, True])
def test_collection_maps_same_response_contract_in_order(
    products: tuple[Product, ...], empty: bool
) -> None:
    source = () if empty else tuple(reversed(products))
    before = tuple(asdict(product) for product in source)

    response = to_product_list_response(source)

    assert isinstance(response, ProductListResponse)
    assert set(type(response).model_fields) == {"items"}
    assert type(response.items) is list
    assert [item.id for item in response.items] == [product.id for product in source]
    for item, product in zip(response.items, source, strict=True):
        assert isinstance(item, ProductResponse)
        assert item == to_product_response(product)
        assert item.images == list(product.images)
        assert item.ingredients == list(product.ingredients)
    assert tuple(asdict(product) for product in source) == before
