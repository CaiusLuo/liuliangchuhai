from unittest.mock import AsyncMock

import pytest
from liuliangchuhai.application.use_cases.create_content_plan import CreateContentPlanUseCase
from liuliangchuhai.application.use_cases.create_content_plan_by_id import (
    CreateContentPlanByIdUseCase,
)
from liuliangchuhai.application.use_cases.get_product import GetProduct, ProductNotFound
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


@pytest.mark.asyncio
async def test_lookup_forwards_canonical_product_and_exact_inputs(
    products: tuple[Product, ...], product_analysis_result: ProductMarketAnalysis
) -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = products[0]
    planner = AsyncMock()
    expected = ContentGenerationPlan(("Selling point",), "Image", "Idea", "Video", "Live", "Social")
    planner.create_content_plan.return_value = expected
    use_case = CreateContentPlanByIdUseCase(
        GetProduct(repository), CreateContentPlanUseCase(planner)
    )
    market = MarketContext("Vietnam", "Students", "Sample packs")
    context = ContentContext("Tiếng Việt")

    result = await use_case.execute(" exact-id ", market, product_analysis_result, context)

    repository.get_by_id.assert_awaited_once_with(" exact-id ")
    planner.create_content_plan.assert_awaited_once()
    assert all(
        actual is supplied
        for actual, supplied in zip(
            planner.create_content_plan.await_args.args,
            (products[0], market, product_analysis_result, context),
            strict=True,
        )
    )
    assert result is expected


@pytest.mark.asyncio
async def test_missing_product_never_calls_planner(
    product_analysis_result: ProductMarketAnalysis,
) -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = None
    planner = AsyncMock()
    use_case = CreateContentPlanByIdUseCase(
        GetProduct(repository), CreateContentPlanUseCase(planner)
    )

    with pytest.raises(ProductNotFound) as error:
        await use_case.execute(
            "missing", MarketContext("Vietnam"), product_analysis_result, ContentContext("English")
        )

    assert error.value.product_id == "missing"
    repository.get_by_id.assert_awaited_once_with("missing")
    planner.create_content_plan.assert_not_called()
