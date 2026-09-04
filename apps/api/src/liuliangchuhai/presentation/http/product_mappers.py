from liuliangchuhai.domain.product import Product
from liuliangchuhai.presentation.http.schemas import ProductListResponse, ProductResponse


def to_product_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        description=product.description,
        origin=product.origin,
        cultural_background=product.cultural_background,
        images=list(product.images),
        usage=product.usage,
        ingredients=list(product.ingredients),
        price=str(product.price) if product.price is not None else None,
        purchase_url=product.purchase_url,
    )


def to_product_list_response(products: tuple[Product, ...]) -> ProductListResponse:
    return ProductListResponse(items=[to_product_response(product) for product in products])
