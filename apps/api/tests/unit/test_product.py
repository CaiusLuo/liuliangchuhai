from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest
from liuliangchuhai.domain.product import Product


def test_product_preserves_values_and_optional_defaults(products: tuple[Product, ...]) -> None:
    assert products[0].name == "柳州螺蛳粉"
    assert products[0].price == Decimal("12.50")
    assert products[1].price is None
    assert products[1].purchase_url is None
    assert replace(products[0], price=Decimal("0")).price == Decimal("0")


def test_product_is_immutable(products: tuple[Product, ...]) -> None:
    with pytest.raises(FrozenInstanceError):
        products[0].name = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        products[0].ingredients[0] = "changed"  # type: ignore[index]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", ""),
        ("id", " luosifen"),
        ("id", "luosifen "),
        ("name", "  "),
        ("category", None),
        ("description", 123),
        ("origin", ""),
        ("cultural_background", ""),
        ("usage", ""),
        ("images", ["image.jpg"]),
        ("images", ("",)),
        ("ingredients", "tea"),
        ("ingredients", (1,)),
        ("purchase_url", " "),
        ("price", 12.5),
        ("price", Decimal("-0.01")),
        ("price", Decimal("NaN")),
        ("price", Decimal("Infinity")),
        ("price", Decimal("0.001")),
    ],
)
def test_product_rejects_invalid_values(
    products: tuple[Product, ...], field: str, value: object
) -> None:
    with pytest.raises(ValueError, match=field):
        replace(products[0], **{field: value})
