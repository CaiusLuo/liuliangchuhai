import pytest
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.presentation.http.product_analysis_mappers import (
    to_analysis_response,
    to_market_context,
)
from liuliangchuhai.presentation.http.schemas import (
    ProductAnalysisRequest,
    ProductMarketAnalysisResponse,
)
from pydantic import BaseModel, ValidationError


@pytest.mark.parametrize(
    "optional",
    [
        {},
        {"target_audience": None, "market_notes": None},
        {"target_audience": "Students", "market_notes": "Test sample packs"},
    ],
)
def test_request_maps_to_market_context(optional: dict[str, str | None]) -> None:
    request = ProductAnalysisRequest.model_validate(
        {"product_id": " Catalog-ID ", "country": "Vietnam", **optional}
    )

    market = to_market_context(request)

    assert isinstance(market, MarketContext)
    assert market == MarketContext(country="Vietnam", **optional)
    assert request.product_id == " Catalog-ID "


@pytest.mark.parametrize("field", ["product_id", "country", "target_audience", "market_notes"])
@pytest.mark.parametrize("value", ["", " \t\n", 123, False, ["text"]])
def test_request_rejects_blank_or_nonstring_fields(field: str, value: object) -> None:
    payload = {"product_id": "luosifen", "country": "Vietnam", field: value}

    with pytest.raises(ValidationError):
        ProductAnalysisRequest.model_validate(payload)


@pytest.mark.parametrize("field", ["product_id", "country"])
@pytest.mark.parametrize("missing", [True, False], ids=["omitted", "null"])
def test_required_fields_cannot_be_missing_or_null(field: str, missing: bool) -> None:
    payload: dict[str, object] = {"product_id": "luosifen", "country": "Vietnam"}
    if missing:
        del payload[field]
    else:
        payload[field] = None

    with pytest.raises(ValidationError):
        ProductAnalysisRequest.model_validate(payload)


def test_request_rejects_client_supplied_product() -> None:
    with pytest.raises(ValidationError):
        ProductAnalysisRequest.model_validate(
            {"product_id": "luosifen", "country": "Vietnam", "product": {"name": "Client product"}}
        )


def test_analysis_maps_to_explicit_presentation_response(
    product_analysis_result: ProductMarketAnalysis,
) -> None:
    response = to_analysis_response(product_analysis_result)

    assert isinstance(response, ProductMarketAnalysisResponse)
    assert isinstance(response, BaseModel)
    assert response.model_dump(mode="json") == {
        "recommendation": "caution",
        "score": 50,
        "summary": "Test heuristic only; market assumptions need validation.",
        "target_audiences": ["Students", "Home cooks"],
        "strengths": ["Distinctive flavor"],
        "risks": ["Taste preferences need validation"],
        "cultural_advantages": ["Guangxi food heritage"],
        "marketing_suggestions": ["Test small sample packs"],
        "content_directions": ["Explain preparation"],
    }
