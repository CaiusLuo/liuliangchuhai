import json
from collections.abc import Callable

import httpx
import pytest
from liuliangchuhai.application.ports.llm_errors import InvalidLLMResponse, LLMUnavailable
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product
from liuliangchuhai.infrastructure.llm.deepseek import DeepSeekLLMAdapter

_VALID_ANALYSIS = {
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


def _response(content: object) -> httpx.Response:
    return httpx.Response(
        200,
        json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]},
    )


@pytest.fixture
def analysis_json(product_analysis_result: ProductMarketAnalysis) -> dict[str, object]:
    return {
        "recommendation": product_analysis_result.recommendation.value,
        "score": product_analysis_result.score,
        "summary": product_analysis_result.summary,
        "target_audiences": list(product_analysis_result.target_audiences),
        "strengths": list(product_analysis_result.strengths),
        "risks": list(product_analysis_result.risks),
        "cultural_advantages": list(product_analysis_result.cultural_advantages),
        "marketing_suggestions": list(product_analysis_result.marketing_suggestions),
        "content_directions": list(product_analysis_result.content_directions),
    }


def _adapter(handler: Callable[[httpx.Request], httpx.Response]) -> DeepSeekLLMAdapter:
    return DeepSeekLLMAdapter(
        api_key="test-key",
        model="deepseek-test",
        timeout_seconds=4.5,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_valid_response_maps_exact_analysis_and_sends_canonical_inputs(
    products: tuple[Product, ...],
    product_analysis_result: ProductMarketAnalysis,
    analysis_json: dict[str, object],
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _response(json.dumps(analysis_json))

    result = await _adapter(handler).analyze_product_market(
        products[0], MarketContext(country="Vietnam", target_audience="Students")
    )

    assert result == product_analysis_result
    assert len(requests) == 1
    request = requests[0]
    assert request.url == "https://api.deepseek.com/chat/completions"
    assert request.headers["authorization"] == "Bearer test-key"
    assert request.extensions["timeout"] == {
        "connect": 4.5,
        "read": 4.5,
        "write": 4.5,
        "pool": 4.5,
    }
    payload = json.loads(request.content)
    assert payload["model"] == "deepseek-test"
    assert payload["stream"] is False
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["thinking"] == {"type": "disabled"}
    prompt = json.loads(payload["messages"][1]["content"])
    assert prompt["product"] == {
        "id": products[0].id,
        "name": products[0].name,
        "category": products[0].category,
        "description": products[0].description,
        "origin": products[0].origin,
        "cultural_background": products[0].cultural_background,
        "images": list(products[0].images),
        "usage": products[0].usage,
        "ingredients": list(products[0].ingredients),
        "price": str(products[0].price),
        "purchase_url": products[0].purchase_url,
    }
    assert prompt["market_context"] == {
        "country": "Vietnam",
        "target_audience": "Students",
        "market_notes": None,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("content", ["", "not-json"], ids=["empty", "invalid-json"])
async def test_unparseable_content_raises_invalid_llm_response(content: str) -> None:
    with pytest.raises(InvalidLLMResponse):
        await _adapter(lambda _request: _response(content)).analyze_product_market(
            _product(), MarketContext(country="Vietnam")
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("summary", None),
        ("recommendation", "maybe"),
        ("score", 101),
        ("risks", ["valid", 3]),
    ],
    ids=["missing-field", "invalid-recommendation", "invalid-score", "invalid-array"],
)
async def test_schema_invalid_content_raises_invalid_llm_response(
    field: str, value: object
) -> None:
    analysis = dict(_VALID_ANALYSIS)
    if value is None:
        analysis.pop(field)
    else:
        analysis[field] = value

    with pytest.raises(InvalidLLMResponse):
        await _adapter(lambda _request: _response(json.dumps(analysis))).analyze_product_market(
            _product(), MarketContext(country="Vietnam")
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [
        httpx.ReadTimeout("timed out"),
        httpx.ConnectError("connection failed"),
        500,
        503,
        401,
    ],
    ids=["timeout", "connection", "http-500", "http-503", "auth"],
)
async def test_provider_failure_is_normalized(failure: Exception | int) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        if isinstance(failure, Exception):
            raise failure
        return httpx.Response(failure)

    with pytest.raises(LLMUnavailable):
        await _adapter(handler).analyze_product_market(_product(), MarketContext(country="Vietnam"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [httpx.ReadTimeout("timed out"), httpx.ConnectError("failed"), 500, 503]
)
async def test_transient_failure_retries_once(
    failure: Exception | int, analysis_json: dict[str, object]
) -> None:
    attempts = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            if isinstance(failure, Exception):
                raise failure
            return httpx.Response(failure)
        return _response(json.dumps(analysis_json))

    await _adapter(handler).analyze_product_market(_product(), MarketContext(country="Vietnam"))

    assert attempts == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [400, 401, 402, 429])
async def test_nontransient_http_failure_is_not_retried(status_code: int) -> None:
    attempts = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(status_code)

    with pytest.raises(LLMUnavailable):
        await _adapter(handler).analyze_product_market(_product(), MarketContext(country="Vietnam"))

    assert attempts == 1


@pytest.mark.asyncio
async def test_nonconnection_network_failure_is_not_retried() -> None:
    attempts = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadError("read failed")

    with pytest.raises(LLMUnavailable):
        await _adapter(handler).analyze_product_market(_product(), MarketContext(country="Vietnam"))

    assert attempts == 1


@pytest.mark.asyncio
async def test_malformed_response_is_not_retried() -> None:
    attempts = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return _response("not-json")

    with pytest.raises(InvalidLLMResponse):
        await _adapter(handler).analyze_product_market(_product(), MarketContext(country="Vietnam"))

    assert attempts == 1


@pytest.mark.asyncio
async def test_status_failure_is_reported_without_raising() -> None:
    adapter = _adapter(lambda _request: httpx.Response(401))

    status = await adapter.status()

    assert status.provider == "deepseek"
    assert status.available is False


@pytest.mark.asyncio
async def test_status_reports_configured_model_availability() -> None:
    adapter = _adapter(
        lambda _request: httpx.Response(200, json={"data": [{"id": "deepseek-test"}]})
    )

    status = await adapter.status()

    assert status.provider == "deepseek"
    assert status.available is True


def _product() -> Product:
    return Product(
        id="test",
        name="Test",
        category="Test",
        description="Test",
        origin="Test",
        cultural_background="Test",
        images=(),
        usage="Test",
        ingredients=(),
    )
