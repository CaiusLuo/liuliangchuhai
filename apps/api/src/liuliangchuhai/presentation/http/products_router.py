from fastapi import APIRouter
from fastapi.responses import JSONResponse

from liuliangchuhai.application.use_cases.get_product import GetProduct, ProductNotFound
from liuliangchuhai.application.use_cases.list_products import ListProducts
from liuliangchuhai.presentation.http.product_mappers import (
    to_product_list_response,
    to_product_response,
)
from liuliangchuhai.presentation.http.schemas import (
    ProductListResponse,
    ProductNotFoundResponse,
    ProductResponse,
)


def create_products_router(list_products: ListProducts, get_product: GetProduct) -> APIRouter:
    router = APIRouter()

    @router.get("/products", response_model=ProductListResponse, operation_id="list_products")
    async def list_catalog() -> ProductListResponse:
        products = await list_products.execute()
        return to_product_list_response(products)

    @router.get(
        "/products/{product_id}",
        response_model=ProductResponse,
        operation_id="get_product",
        responses={404: {"model": ProductNotFoundResponse, "description": "Product not found"}},
    )
    async def get_catalog_product(product_id: str) -> ProductResponse | JSONResponse:
        try:
            product = await get_product.execute(product_id)
        except ProductNotFound:
            return JSONResponse(
                status_code=404,
                content=ProductNotFoundResponse(
                    code="product_not_found", message="Product not found"
                ).model_dump(),
            )
        return to_product_response(product)

    return router
