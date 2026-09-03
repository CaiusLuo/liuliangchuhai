import json
from dataclasses import asdict
from pathlib import Path

import pytest
from liuliangchuhai.domain.product import Product
from liuliangchuhai.infrastructure.products.json_repository import JsonProductRepository


@pytest.mark.parametrize("content", ["{", "{}", "null", '["product"]'])
def test_rejects_invalid_catalog_structure(tmp_path: Path, content: str) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=r"invalid\.json"):
        JsonProductRepository(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("unexpected", "field"),
        ("id", ""),
        ("images", "image.jpg"),
        ("ingredients", None),
        ("price", 12.5),
        ("price", True),
        ("price", "not-a-price"),
        ("price", "NaN"),
        ("price", "-1.00"),
    ],
)
def test_rejects_invalid_product_with_context(
    tmp_path: Path, products: tuple[Product, ...], field: str, value: object
) -> None:
    record = asdict(products[0])
    record[field] = value
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps([record], default=str), encoding="utf-8")

    with pytest.raises(ValueError, match=r"invalid.json.*product\[0\]"):
        JsonProductRepository(path)


def test_rejects_missing_required_field(tmp_path: Path, products: tuple[Product, ...]) -> None:
    record = asdict(products[0])
    del record["origin"]
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps([record], default=str), encoding="utf-8")

    with pytest.raises(ValueError, match="origin"):
        JsonProductRepository(path)


def test_rejects_duplicate_ids(tmp_path: Path, products: tuple[Product, ...]) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps([asdict(products[0])] * 2, default=str), encoding="utf-8")

    with pytest.raises(ValueError, match=r"duplicate.*luosifen"):
        JsonProductRepository(path)


def test_missing_catalog_does_not_silently_become_empty(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        JsonProductRepository(tmp_path / "missing.json")


@pytest.mark.asyncio
async def test_snapshot_reads_work_after_source_removed(
    tmp_path: Path, products: tuple[Product, ...]
) -> None:
    path = tmp_path / "products.json"
    path.write_text(json.dumps([asdict(product) for product in products], default=str))
    repository = JsonProductRepository(path)
    path.unlink()

    assert await repository.list_products() == products
    assert await repository.get_by_id(products[0].id) == products[0]


@pytest.mark.asyncio
async def test_optional_fields_can_be_omitted(
    tmp_path: Path, products: tuple[Product, ...]
) -> None:
    record = asdict(products[1])
    del record["price"]
    del record["purchase_url"]
    path = tmp_path / "products.json"
    path.write_text(json.dumps([record]), encoding="utf-8")

    assert await JsonProductRepository(path).get_by_id(products[1].id) == products[1]
