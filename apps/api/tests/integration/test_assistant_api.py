from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from liuliangchuhai.application.ports.assistant import AssistantPort
from liuliangchuhai.application.ports.assistant_errors import (
    AssistantUnavailable,
    InvalidAssistantResponse,
)
from liuliangchuhai.application.use_cases.get_product import GetProduct
from liuliangchuhai.application.use_cases.reply_to_customer import ReplyToCustomer
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.presentation.http.assistant_router import create_assistant_router


@pytest.mark.asyncio
@pytest.mark.parametrize("product_id", [None, "wuzhou-liubao-tea"])
async def test_default_mock_success(product_id):
    app = create_app(Settings.model_validate({}))
    payload = {"message": "这个产品有什么文化背景?"}
    if product_id:
        payload["product_id"] = product_id
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/assistant/chat", json=payload)
        repeat = await client.post("/assistant/chat", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert repeat.json() == body
    assert set(body) == {"message", "suggested_action"}
    assert body["message"].strip()
    if product_id:
        assert "梧州六堡茶" in body["message"]
        assert "六堡茶与梧州地方茶文化相联系" in body["message"]
        assert body["suggested_action"] == {"type": "view_product", "product_id": product_id}
    else:
        assert body["suggested_action"] is None


@pytest.mark.asyncio
async def test_unknown_product():
    async with AsyncClient(
        transport=ASGITransport(app=create_app(Settings.model_validate({}))),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/assistant/chat", json={"message": "Question", "product_id": "missing"}
        )
    assert response.status_code == 404
    assert response.json() == {"code": "product_not_found", "message": "Product not found"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error_type", "status", "code", "message"),
    [
        (
            AssistantUnavailable,
            503,
            "assistant_unavailable",
            "Assistant service is temporarily unavailable",
        ),
        (
            InvalidAssistantResponse,
            502,
            "invalid_assistant_response",
            "Assistant service returned an invalid response",
        ),
    ],
)
async def test_stable_error_mapping(error_type, status, code, message):
    assistant = AsyncMock(spec=AssistantPort)
    assistant.reply.side_effect = error_type("Private provider diagnostic")
    app = FastAPI()
    app.include_router(create_assistant_router(ReplyToCustomer(GetProduct(AsyncMock()), assistant)))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/assistant/chat", json={"message": "Question"})
    assert response.status_code == status
    assert response.json() == {"code": code, "message": message}
    assistant.reply.assert_awaited_once_with("Question", None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": ""},
        {"message": " \t\n"},
        {"message": None},
        {"message": 42},
        {"message": "Question", "product_id": " "},
        {"message": "Question", "product_id": 42},
        {"message": "Question", "product": {"name": "Forged"}},
        {"message": "Question", "messages": []},
    ],
)
async def test_invalid_input_uses_existing_422_without_invoking_use_case(payload):
    use_case = AsyncMock(spec=ReplyToCustomer)
    app = FastAPI()
    app.include_router(create_assistant_router(use_case))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/assistant/chat", json=payload)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    use_case.execute.assert_not_called()
