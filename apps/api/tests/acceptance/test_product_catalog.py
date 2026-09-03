from pathlib import Path

import pytest
from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.product import Product


@pytest.mark.asyncio
async def test_bundled_catalog_is_available_without_keys_from_any_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    container = build_container(
        Settings(_env_file=None, llm_provider="mock", digital_human_provider="mock")
    )

    products = await container.list_products.execute()
    assert len(products) >= 3
    assert len({product.id for product in products}) == len(products)
    assert {"广西柳州", "广西梧州", "广西桂林"} <= {product.origin for product in products}
    for product in products:
        assert type(product) is Product
        assert await container.get_product.execute(product.id) == product
        assert product.price is None
        assert product.purchase_url is None

    with pytest.raises(ProductNotFound):
        await container.get_product.execute("unknown-product")
