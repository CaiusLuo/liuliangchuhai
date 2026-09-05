import asyncio
import json
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path

import httpx
import pytest
from liuliangchuhai.application.ports.content_planner import ContentPlannerPort
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.domain.content_plan import ContentContext
from liuliangchuhai.domain.market_analysis import MarketContext
from liuliangchuhai.infrastructure.content.deepseek import DeepSeekContentPlannerAdapter
from liuliangchuhai.infrastructure.content.mock import MockContentPlannerAdapter


@pytest.fixture
def package():
    # Reviewed response fixture; live model quality is checked separately.
    return json.loads(
        (Path(__file__).parents[1] / "fixtures/content_plans/mango_indonesia.json").read_text()
    )


def envelope(content, finish="stop"):
    return {"choices": [{"finish_reason": finish, "message": {"content": content}}]}


def adapter(handler, timeout=4.5):
    return DeepSeekContentPlannerAdapter(
        api_key="test-key",
        model="deepseek-test",
        timeout_seconds=timeout,
        transport=httpx.MockTransport(handler),
    )


async def generate(handler, products, analysis, language="English", timeout=4.5):
    return await adapter(handler, timeout).create_content_plan(
        products[0], MarketContext(country="Indonesia"), analysis, ContentContext(language)
    )


@pytest.mark.asyncio
async def test_structured_canonical_context_and_existing_analysis(
    package, products, product_analysis_result
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=envelope(json.dumps(package)))

    port: ContentPlannerPort = adapter(handler)
    market = MarketContext("Indonesia", "Young families", "Explore weekend fruit sharing")
    result = await port.create_content_plan(
        products[0], market, product_analysis_result, ContentContext("English")
    )
    assert asdict(result) == {**package, "key_selling_points": tuple(package["key_selling_points"])}
    assert len(requests) == 1
    request = requests[0]
    assert str(request.url) == "https://api.deepseek.com/chat/completions"
    assert request.headers["authorization"] == "Bearer test-key"
    assert request.extensions["timeout"] == dict.fromkeys(["connect", "read", "write", "pool"], 4.5)
    payload = json.loads(request.content)
    assert payload["model"] == "deepseek-test"
    assert payload["stream"] is False
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["max_tokens"] == 3072
    assert "tools" not in payload
    assert len(payload["messages"]) == 2
    context = json.loads(payload["messages"][1]["content"].split("Context JSON:\n", 1)[1])
    assert context == {
        "product": {
            key: value
            for key, value in json.loads(json.dumps(asdict(products[0]), default=str)).items()
            if key
            in {
                "name",
                "category",
                "origin",
                "description",
                "cultural_background",
                "usage",
                "ingredients",
            }
        },
        "market": {**asdict(market), "target_language": "English"},
        "analysis_hypotheses": {
            key: value
            for key, value in json.loads(json.dumps(asdict(product_analysis_result))).items()
            if key
            in {
                "recommendation",
                "target_audiences",
                "risks",
            }
        },
    }
    prompt = payload["messages"][0]["content"]
    for requirement in (
        "strategist",
        "consumer",
        "hypotheses",
        "camera",
        "English",
        "certifications",
    ):
        assert requirement in prompt


@pytest.mark.parametrize(
    "provider,expected",
    [("mock", MockContentPlannerAdapter), ("deepseek", DeepSeekContentPlannerAdapter)],
)
def test_content_selection_reuses_existing_llm_configuration(provider, expected):
    settings = Settings(
        _env_file=None,
        llm_provider=provider,
        deepseek_api_key="test-key" if provider == "deepseek" else None,
    )
    assert isinstance(build_container(settings).content_planner, expected)


def test_default_content_planner_needs_no_credentials():
    assert isinstance(
        build_container(Settings(_env_file=None)).content_planner, MockContentPlannerAdapter
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field",
    [
        "key_selling_points",
        "image_prompt",
        "short_video_idea",
        "short_video_prompt",
        "live_script",
        "social_caption",
    ],
)
@pytest.mark.parametrize(
    "bad",
    [
        "",
        "Too short",
        "Demo launch package " * 30,
        "An example campaign " * 30,
        "A test product story " * 30,
        "芒果 for the family " * 30,
        "Halo selamat datang mangga segar untuk keluarga kita hari ini " * 10,
    ],
)
async def test_rejects_low_quality_or_mixed_english_in_every_section(
    package, products, product_analysis_result, field, bad
):
    package[field] = [bad] if field == "key_selling_points" else bad
    with pytest.raises(ValueError, match="Invalid content plan response"):
        await generate(
            lambda _: httpx.Response(200, json=envelope(json.dumps(package))),
            products,
            product_analysis_result,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["English", " english ", "en", "en-US", "en_GB"])
async def test_english_aliases_reject_untranslated_product_names(
    package, products, product_analysis_result, language
):
    package["social_caption"] += " 百色芒果"
    with pytest.raises(ValueError):
        await generate(
            lambda _: httpx.Response(200, json=envelope(json.dumps(package))),
            products,
            product_analysis_result,
            language,
        )


@pytest.mark.asyncio
async def test_does_not_reject_latin_accents_or_other_requested_languages(
    package, products, product_analysis_result
):
    package["social_caption"] += " A café conversation."
    await generate(
        lambda _: httpx.Response(200, json=envelope(json.dumps(package))),
        products,
        product_analysis_result,
    )
    package["social_caption"] = (
        "来自广西百色的芒果,让周末的家庭餐桌多一个产地故事。成熟后切片分享,或按实际说明制作饮品与甜品。你最想与家人一起尝试哪种吃法?欢迎分享你的周末水果创意。"
    )
    await generate(
        lambda _: httpx.Response(200, json=envelope(json.dumps(package))),
        products,
        product_analysis_result,
        "Chinese",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "extra",
        "array",
        "null",
        "wrong_type",
        "empty_points",
        "number_point",
        "duplicate",
        "nan",
        "json",
        "truncated",
        "envelope",
    ],
)
async def test_rejects_malformed_successful_output(
    package, products, product_analysis_result, mutation
):
    data = deepcopy(package)
    if mutation == "missing":
        del data["live_script"]
    if mutation == "extra":
        data["market_insight"] = "Unrequested field"
    if mutation == "wrong_type":
        data["image_prompt"] = [data["image_prompt"]]
    if mutation == "empty_points":
        data["key_selling_points"] = []
    if mutation == "number_point":
        data["key_selling_points"] = [42]
    content = json.dumps(data)
    if mutation == "array":
        content = json.dumps([data])
    if mutation == "null":
        content = "null"
    if mutation == "duplicate":
        content = content[:-1] + ', "live_script": "duplicate"}'
    if mutation == "nan":
        content = content.replace(json.dumps(data["image_prompt"]), "NaN")
    if mutation == "json":
        content = "```json\n" + content + "\n```"
    body = envelope(content, "length" if mutation == "truncated" else "stop")
    if mutation == "envelope":
        body = {"choices": []}
    with pytest.raises(ValueError, match=r"^Invalid content plan response$"):
        await generate(lambda _: httpx.Response(200, json=body), products, product_analysis_result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [httpx.ReadTimeout, httpx.ConnectError, httpx.ReadError, 401, 402, 429, 500, 503]
)
async def test_provider_failures_are_safe_and_bounded(products, product_analysis_result, failure):
    calls = []

    def handler(request):
        calls.append(request)
        if isinstance(failure, int):
            return httpx.Response(failure, text="private provider detail")
        raise failure("private provider detail")

    with pytest.raises(RuntimeError, match=r"^Content planning service unavailable$"):
        await generate(handler, products, product_analysis_result)
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_total_deadline(products, product_analysis_result):
    async def handler(request):
        await asyncio.sleep(1)
        return httpx.Response(200)

    with pytest.raises(RuntimeError, match="unavailable"):
        await generate(handler, products, product_analysis_result, timeout=0.01)


@pytest.mark.asyncio
async def test_reviewed_product_and_market_regression_packages(product_analysis_result):
    """Exercise realistic response fixtures and exact inputs, not a live model quality score."""
    from liuliangchuhai.domain.product import Product

    container = build_container(Settings(_env_file=None))
    mango = await container.get_product.execute("baise-mango")
    tea = await container.get_product.execute("wuzhou-liubao-tea")
    # Test-only context: the current catalog has no brocade entry.
    brocade = Product(
        id="fixture-zhuang-brocade",
        name="壮锦",
        category="织锦",
        description="广西壮族织锦文化商品。",
        origin="广西",
        cultural_background="壮族传统织锦文化。",
        usage="装饰或礼赠。",
        ingredients=(),
        images=(),
    )
    cases = [
        (mango, "Indonesia", "Young families", "mango_indonesia", "family"),
        (mango, "Singapore", "Home hosts", "mango_singapore", "hosting"),
        (tea, "Vietnam", "Tea gift buyers", "tea_vietnam", "gift"),
        (brocade, "Singapore", "Design enthusiasts", "brocade_singapore", "heritage"),
    ]
    outputs = []
    inputs = []
    for product, country, audience, fixture, positioning in cases:
        expected = json.loads(
            (Path(__file__).parents[1] / f"fixtures/content_plans/{fixture}.json").read_text()
        )
        analysis = replace(product_analysis_result, target_audiences=(audience,))

        def handler(request, expected=expected):
            inputs.append(
                json.loads(
                    json.loads(request.content)["messages"][1]["content"].split(
                        "Context JSON:\n", 1
                    )[1]
                )
            )
            return httpx.Response(200, json=envelope(json.dumps(expected)))

        result = await adapter(handler).create_content_plan(
            product, MarketContext(country, audience), analysis, ContentContext("English")
        )
        output = asdict(result)
        assert output == {**expected, "key_selling_points": tuple(expected["key_selling_points"])}
        assert positioning in " ".join(result.key_selling_points).lower()
        assert inputs[-1]["product"]["name"] == product.name
        assert inputs[-1]["market"]["country"] == country
        assert inputs[-1]["analysis_hypotheses"]["target_audiences"] == [audience]
        outputs.append(output)
    # Same canonical product, different market/audience is conveyed without a catalog or reanalysis.
    assert inputs[0]["product"] == inputs[1]["product"]
    assert inputs[0]["market"] != inputs[1]["market"]
    for field in outputs[0]:
        assert len({str(output[field]) for output in outputs}) == len(cases)


@pytest.mark.asyncio
async def test_provider_reasoning_is_not_part_of_content_plan(
    package, products, product_analysis_result
):
    body = envelope(json.dumps(package))
    body["choices"][0]["message"]["reasoning_content"] = "Private provider reasoning"
    result = await generate(
        lambda _: httpx.Response(200, json=body), products, product_analysis_result
    )
    assert set(asdict(result)) == set(package)
    assert "Private provider reasoning" not in str(asdict(result))


@pytest.mark.asyncio
async def test_padding_does_not_satisfy_meaningful_length(
    package, products, product_analysis_result
):
    package["image_prompt"] = "A" + " " * 200 + "photo"
    with pytest.raises(ValueError, match="Invalid content plan response"):
        await generate(
            lambda _: httpx.Response(200, json=envelope(json.dumps(package))),
            products,
            product_analysis_result,
        )
