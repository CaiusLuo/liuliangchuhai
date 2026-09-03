import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from liuliangchuhai.domain.product import Product


class JsonProductRepository:
    """Load and validate a catalog once; all subsequent reads use its snapshot."""

    def __init__(self, path: Path) -> None:
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as error:
            raise ValueError(f"{path}: invalid UTF-8 JSON catalog: {error}") from error
        if not isinstance(records, list):
            raise ValueError(f"{path}: catalog must be a JSON array")

        by_id: dict[str, Product] = {}
        for index, record in enumerate(records):
            try:
                product = _parse_product(record)
                if product.id in by_id:
                    raise ValueError(f"duplicate product id: {product.id!r}")
            except (TypeError, ValueError, InvalidOperation) as error:
                raise ValueError(f"{path}: product[{index}]: {error}") from error
            by_id[product.id] = product
        self._by_id = by_id
        self._products = tuple(by_id.values())

    async def list_products(self) -> tuple[Product, ...]:
        return self._products

    async def get_by_id(self, product_id: str) -> Product | None:
        return self._by_id.get(product_id)


def _parse_product(record: object) -> Product:
    if not isinstance(record, dict):
        raise ValueError("product must be a JSON object")
    fields = dict(record)
    for field in ("images", "ingredients"):
        items = fields.get(field)
        if not isinstance(items, list):
            raise ValueError(f"{field} must be a JSON array")
        fields[field] = tuple(items)
    price = fields.get("price")
    if price is not None:
        if not isinstance(price, str):
            raise ValueError("price must be a decimal string or null")
        try:
            fields["price"] = Decimal(price)
        except InvalidOperation as error:
            raise ValueError("price must be a decimal string or null") from error
    return Product(**fields)
