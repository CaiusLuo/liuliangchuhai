import asyncio
import json
from dataclasses import asdict

import httpx
import pytest
from liuliangchuhai.application.ports.assistant import (
    AssistantActionType,
    AssistantPort,
    AssistantReply,
    AssistantSuggestedAction,
)
from liuliangchuhai.application.ports.assistant_errors import (
    AssistantUnavailable,
    InvalidAssistantResponse,
)
from liuliangchuhai.infrastructure.assistant.deepseek import DeepSeekAssistantAdapter


def envelope(content):
    return {"choices": [{"finish_reason": "stop", "message": {"content": content}}]}


def adapter(handler, timeout=4.5):
    return DeepSeekAssistantAdapter(
        api_key="test-key",
        model="deepseek-test",
        timeout_seconds=timeout,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("scoped", [False, True])
async def test_one_completion_with_exact_context_and_shared_configuration(products, scoped):
    requests = []
    reply = {"message": "A concise answer to this question.", "suggested_action": None}

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=envelope(json.dumps(reply)))

    port: AssistantPort = adapter(handler)
    product = products[0] if scoped else None
    assert await port.reply("Actual question", product) == AssistantReply(reply["message"])
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.deepseek.com/chat/completions"
    assert request.headers["authorization"] == "Bearer test-key"
    assert request.extensions["timeout"] == dict.fromkeys(["connect", "read", "write", "pool"], 4.5)
    payload = json.loads(request.content)
    assert payload["model"] == "deepseek-test"
    assert payload["stream"] is False
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["thinking"] == {"type": "disabled"}
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "system"
    prompt = payload["messages"][0]["content"]
    assert "桂品 AI 助手" in prompt
    assert "其他问题暂时无法回答" in prompt
    context = json.loads(payload["messages"][1]["content"])
    assert context == {
        "message": "Actual question",
        "product": json.loads(json.dumps(asdict(product), default=str)) if product else None,
    }
    assert "tools" not in payload


@pytest.mark.asyncio
@pytest.mark.parametrize("action_type", list(AssistantActionType))
async def test_valid_action_uses_canonical_id(products, action_type):
    product = products[0]
    data = {
        "message": "Next step",
        "suggested_action": {"type": action_type, "product_id": product.id},
    }
    result = await adapter(lambda _: httpx.Response(200, json=envelope(json.dumps(data)))).reply(
        "Next step?", product
    )
    assert result == AssistantReply("Next step", AssistantSuggestedAction(action_type, product.id))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action",
    [
        {"type": "view_product", "product_id": "invented"},
        {"type": "start_analysis", "product_id": " liubao-tea "},
        {"type": "buy", "product_id": "liubao-tea"},
        {"type": "view_product", "product_id": 123},
        {"type": "view_product"},
        {"type": "view_product", "product_id": "liubao-tea", "href": "/products/tea"},
        [{"type": "view_product", "product_id": "liubao-tea"}],
        "view_product",
        False,
    ],
)
async def test_invalid_actions_are_rejected(products, action):
    data = {"message": "Answer", "suggested_action": action}
    with pytest.raises(InvalidAssistantResponse):
        await adapter(lambda _: httpx.Response(200, json=envelope(json.dumps(data)))).reply(
            "Question", products[1]
        )


@pytest.mark.asyncio
async def test_generic_context_never_allows_action():
    data = {"message": "Answer", "suggested_action": {"type": "view_product", "product_id": "tea"}}
    with pytest.raises(InvalidAssistantResponse):
        await adapter(lambda _: httpx.Response(200, json=envelope(json.dumps(data)))).reply(
            "Q", None
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content",
    [
        "",
        "not JSON",
        "null",
        "[]",
        "{}",
        '{"message":"Answer"}',
        '{"message":" \\n\\t","suggested_action":null}',
        '{"message":null,"suggested_action":null}',
        '{"message":123,"suggested_action":null}',
        '{"message":"Answer","suggested_action":null,"provider":"private"}',
        '{"message":"Answer","message":"Duplicate","suggested_action":null}',
        '{"message":NaN,"suggested_action":null}',
        '{"message":"Answer","suggested_action":{"type":"view_product","type":"start_analysis","product_id":"tea"}}',
        None,
        {},
    ],
)
async def test_malformed_content_is_private_and_not_retried(content):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=envelope(content))

    with pytest.raises(InvalidAssistantResponse) as error:
        await adapter(handler).reply("Question", None)
    assert str(error.value) == "Assistant returned invalid output"
    assert error.value.__suppress_context__
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body",
    [
        "not JSON",
        "null",
        "[]",
        "{}",
        '{"choices":[]}',
        '{"choices":{}}',
        '{"choices":[null]}',
        '{"choices":[{}]}',
        '{"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}',
        '{"choices":[{"finish_reason":"content_filter","message":{"content":"{}"}}]}',
        '{"choices":[{"finish_reason":"stop","message":null}]}',
        '{"choices":[{"finish_reason":"stop","message":{}}]}',
        '{"choices":[],"choices":[]}',
    ],
)
async def test_malformed_or_incomplete_envelope(body):
    with pytest.raises(InvalidAssistantResponse):
        await adapter(lambda _: httpx.Response(200, text=body)).reply("Question", None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [
        httpx.ReadTimeout("private diagnostic"),
        httpx.ConnectError("private diagnostic"),
        httpx.ReadError("private diagnostic"),
        httpx.RemoteProtocolError("private diagnostic"),
        301,
        400,
        401,
        402,
        429,
        500,
        503,
    ],
)
async def test_transport_failures_are_private_and_never_retried(failure):
    calls = []

    def handler(request):
        calls.append(request)
        if isinstance(failure, Exception):
            raise failure
        return httpx.Response(failure, text="private provider body")

    with pytest.raises(AssistantUnavailable) as error:
        await adapter(handler).reply("Question", None)
    assert str(error.value) == "Assistant request failed"
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_total_deadline_bounds_even_a_stalled_transport():
    calls = []

    async def handler(request):
        calls.append(request)
        await asyncio.sleep(1)
        pytest.fail("deadline should cancel the transport")

    with pytest.raises(AssistantUnavailable):
        await adapter(handler, timeout=0.01).reply("Question", None)
    assert len(calls) == 1
