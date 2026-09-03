import json
from collections.abc import Callable
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

import pytest
from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.domain.product import Product
from liuliangchuhai.infrastructure.products.json_repository import JsonProductRepository


class FakeProductRepository:
    def __init__(self, products: tuple[Product, ...]) -> None:
        self._products = products

    async def list_products(self) -> tuple[Product, ...]:
        return self._products

    async def get_by_id(self, product_id: str) -> Product | None:
        return next((product for product in self._products if product.id == product_id), None)


@pytest.fixture
def products() -> tuple[Product, ...]:
    return (
        Product(
            id="luosifen",
            name="柳州螺蛳粉",
            category="米粉",
            description="广西风味米粉演示商品。",
            origin="广西柳州",
            cultural_background="柳州地方饮食文化。",
            images=("https://example.invalid/noodle.jpg",),
            usage="煮制后食用。",
            ingredients=("米粉", "酸笋"),
            price=Decimal("12.50"),
            purchase_url="https://example.invalid/product",
        ),
        Product(
            id="liubao-tea",
            name="六堡茶",
            category="茶叶",
            description="广西茶叶演示商品。",
            origin="广西梧州",
            cultural_background="梧州地方茶文化。",
            images=(),
            usage="冲泡饮用。",
            ingredients=("茶叶",),
        ),
    )


@pytest.fixture(params=["fake", "json"])
def repository_factory(
    request: pytest.FixtureRequest, tmp_path: Path
) -> Callable[[tuple[Product, ...]], ProductRepository]:
    def create(products: tuple[Product, ...]) -> ProductRepository:
        if request.param == "fake":
            return FakeProductRepository(products)
        path = tmp_path / "products.json"
        path.write_text(
            json.dumps([asdict(product) for product in products], ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        return JsonProductRepository(path)

    return create
