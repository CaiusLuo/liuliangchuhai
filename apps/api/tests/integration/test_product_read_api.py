from collections.abc import Iterator, Sequence
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.routing import APIRoute, iter_route_contexts
from httpx import ASGITransport, AsyncClient
from liuliangchuhai.application.use_cases.analyze_product_by_id import AnalyzeProductByIdUseCase
from liuliangchuhai.application.use_cases.get_product import GetProduct, ProductNotFound
from liuliangchuhai.application.use_cases.list_products import ListProducts
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.product import Product
from pydantic import BaseModel
from starlette.routing import BaseRoute

TEXT_FIELDS = {
    "id",
    "name",
    "category",
    "description",
    "origin",
    "cultural_background",
    "usage",
}
PRODUCT_FIELDS = TEXT_FIELDS | {"images", "ingredients", "price", "purchase_url"}


def assert_product_contract(body: dict, product: Product) -> None:
    assert set(body) == PRODUCT_FIELDS
    for field in TEXT_FIELDS:
        assert isinstance(body[field], str)
        assert body[field] == getattr(product, field)
    for field in ("images", "ingredients"):
        assert isinstance(body[field], list)
        assert body[field] == list(getattr(product, field))
        assert all(isinstance(item, str) for item in body[field])
    assert body["price"] is None or type(body["price"]) is str
    assert body["price"] == (None if product.price is None else str(product.price))
    assert body["purchase_url"] == product.purchase_url


@pytest.fixture
def read_boundary(
    monkeypatch: pytest.MonkeyPatch, products: tuple[Product, ...]
) -> SimpleNamespace:
    real = build_container(Settings(_env_file=None))
    reads = SimpleNamespace(
        list_products=Mock(spec=ListProducts),
        get_product=Mock(spec=GetProduct),
        analyze_product_by_id=Mock(spec=AnalyzeProductByIdUseCase),
        get_system_status=real.get_system_status,
    )
    # Non-alphabetical order and non-null Decimal expose accidental sorting/coercion.
    reads.list_products.execute.return_value = products
    reads.get_product.execute.return_value = products[0]
    monkeypatch.setattr("liuliangchuhai.bootstrap.app.build_container", lambda settings: reads)
    return SimpleNamespace(app=create_app(Settings(_env_file=None)), use_cases=reads)


@pytest.mark.asyncio
async def test_list_calls_only_list_once_and_maps_in_order(
    read_boundary: SimpleNamespace, products: tuple[Product, ...]
) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=read_boundary.app), base_url="http://test"
    ) as client:
        response = await client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items"}
    assert [item["id"] for item in body["items"]] == [product.id for product in products]
    for item, product in zip(body["items"], products, strict=True):
        assert_product_contract(item, product)
    read_boundary.use_cases.list_products.execute.assert_awaited_once_with()
    read_boundary.use_cases.get_product.execute.assert_not_called()
    read_boundary.use_cases.analyze_product_by_id.execute.assert_not_called()


@pytest.mark.asyncio
async def test_empty_catalog_returns_only_empty_items(read_boundary: SimpleNamespace) -> None:
    read_boundary.use_cases.list_products.execute.return_value = ()
    async with AsyncClient(
        transport=ASGITransport(app=read_boundary.app), base_url="http://test"
    ) as client:
        response = await client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"items": []}
    read_boundary.use_cases.list_products.execute.assert_awaited_once_with()
    read_boundary.use_cases.get_product.execute.assert_not_called()
    read_boundary.use_cases.analyze_product_by_id.execute.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("index", [0, 1])
async def test_detail_calls_only_get_once_with_exact_id(
    read_boundary: SimpleNamespace, products: tuple[Product, ...], index: int
) -> None:
    product = products[index]
    read_boundary.use_cases.get_product.execute.return_value = product
    async with AsyncClient(
        transport=ASGITransport(app=read_boundary.app), base_url="http://test"
    ) as client:
        response = await client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert_product_contract(response.json(), product)
    read_boundary.use_cases.get_product.execute.assert_awaited_once_with(product.id)
    read_boundary.use_cases.list_products.execute.assert_not_called()
    read_boundary.use_cases.analyze_product_by_id.execute.assert_not_called()


@pytest.mark.asyncio
async def test_unknown_product_has_stable_private_error_translation(
    read_boundary: SimpleNamespace,
) -> None:
    unknown_id = "private-missing-id"
    error = ProductNotFound(unknown_id)
    error.args = (f"{error}; JsonProductRepository /private/catalog.json; Traceback diagnostic",)
    read_boundary.use_cases.get_product.execute.side_effect = error
    async with AsyncClient(
        transport=ASGITransport(app=read_boundary.app), base_url="http://test"
    ) as client:
        response = await client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {"code": "product_not_found", "message": "Product not found"}
    for private in (unknown_id, str(error), "JsonProductRepository", "/private/", "Traceback"):
        assert private not in response.text
    read_boundary.use_cases.get_product.execute.assert_awaited_once_with(unknown_id)
    read_boundary.use_cases.list_products.execute.assert_not_called()
    read_boundary.use_cases.analyze_product_by_id.execute.assert_not_called()


@pytest.mark.asyncio
async def test_real_demo_catalog_and_detail_match_existing_use_cases() -> None:
    settings = Settings(_env_file=None)
    container = build_container(settings)
    products = await container.list_products.execute()
    assert products, "Existing demo catalog must be nonempty"
    async with AsyncClient(
        transport=ASGITransport(app=create_app(settings)), base_url="http://test"
    ) as client:
        response = await client.get("/products")
        assert response.status_code == 200
        assert set(response.json()) == {"items"}
        items = response.json()["items"]
        assert [item["id"] for item in items] == [product.id for product in products]
        for item, product in zip(items, products, strict=True):
            assert_product_contract(item, product)
            detail = await client.get(f"/products/{product.id}")
            assert detail.status_code == 200
            assert_product_contract(detail.json(), await container.get_product.execute(product.id))
            assert detail.json() == item


@pytest.mark.asyncio
async def test_real_unknown_product_returns_frozen_404() -> None:
    unknown_id = "nonexistent-private-product-17"
    async with AsyncClient(
        transport=ASGITransport(app=create_app(Settings(_env_file=None))), base_url="http://test"
    ) as client:
        response = await client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {"code": "product_not_found", "message": "Product not found"}
    assert unknown_id not in response.text
    assert str(ProductNotFound(unknown_id)) not in response.text


def iter_api_routes(routes: Sequence[BaseRoute]) -> Iterator[APIRoute]:
    # Same generic traversal as Issue #3: no private wrapper or fixed-depth assumptions.
    for context in iter_route_contexts(routes):
        route = context.original_route
        if isinstance(route, APIRoute):
            yield route
        yield from iter_api_routes(getattr(route, "routes", ()))


@pytest.mark.parametrize(
    ("path", "model_name"),
    [("/products", "ProductListResponse"), ("/products/{product_id}", "ProductResponse")],
)
def test_explicit_presentation_response_models(path: str, model_name: str) -> None:
    app = create_app(Settings(_env_file=None))
    route = next(
        (
            route
            for route in iter_api_routes(app.routes)
            if route.path == path and "GET" in route.methods
        ),
        None,
    )
    assert route is not None, f"GET {path} is missing"
    from liuliangchuhai.presentation.http import schemas

    assert route.response_model is getattr(schemas, model_name)
    assert isinstance(route.response_model, type)
    assert issubclass(route.response_model, BaseModel)
    assert route.response_model.__module__.startswith("liuliangchuhai.presentation.")


@pytest.mark.asyncio
async def test_health_regression() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app(Settings(_env_file=None))), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_product_analysis_regression() -> None:
    settings = Settings(_env_file=None)
    products = await build_container(settings).list_products.execute()
    async with AsyncClient(
        transport=ASGITransport(app=create_app(settings)), base_url="http://test"
    ) as client:
        response = await client.post(
            "/product-analysis", json={"product_id": products[0].id, "country": "Vietnam"}
        )
    assert response.status_code == 200
    assert isinstance(response.json()["summary"], str)
