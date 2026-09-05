from unittest.mock import AsyncMock

import pytest
from liuliangchuhai.application.ports.assistant import (
    AssistantActionType,
    AssistantPort,
    AssistantReply,
    AssistantSuggestedAction,
)
from liuliangchuhai.application.ports.assistant_errors import (
    AssistantError,
    AssistantUnavailable,
    InvalidAssistantResponse,
)
from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.application.use_cases.get_product import GetProduct, ProductNotFound
from liuliangchuhai.application.use_cases.reply_to_customer import ReplyToCustomer


@pytest.mark.asyncio
@pytest.mark.parametrize("scoped", [False, True])
@pytest.mark.parametrize("action_type", [None, *AssistantActionType])
async def test_resolves_only_selected_product_and_preserves_reply(products, scoped, action_type):
    repository = AsyncMock(spec=ProductRepository)
    repository.get_by_id.return_value = products[0]
    assistant = AsyncMock(spec=AssistantPort)
    action = AssistantSuggestedAction(action_type, products[0].id) if action_type else None
    reply = AssistantReply("Answer", action)
    assistant.reply.return_value = reply
    message = "  What is this product?  "

    result = await ReplyToCustomer(GetProduct(repository), assistant).execute(
        message, products[0].id if scoped else None
    )

    assert result is reply
    assistant.reply.assert_awaited_once_with(message, products[0] if scoped else None)
    if scoped:
        assert assistant.reply.call_args.args[1] is products[0]
        repository.get_by_id.assert_awaited_once_with(products[0].id)
    else:
        repository.get_by_id.assert_not_called()
    repository.list_products.assert_not_called()


@pytest.mark.asyncio
async def test_unknown_product_preserves_not_found():
    repository = AsyncMock(spec=ProductRepository)
    repository.get_by_id.return_value = None
    assistant = AsyncMock(spec=AssistantPort)
    with pytest.raises(ProductNotFound) as error:
        await ReplyToCustomer(GetProduct(repository), assistant).execute("Question", "missing")
    assert error.value.product_id == "missing"
    assistant.reply.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["", " \n\t", None, 42])
async def test_message_validation_precedes_lookup_and_assistant(message):
    repository = AsyncMock(spec=ProductRepository)
    assistant = AsyncMock(spec=AssistantPort)
    with pytest.raises(ValueError, match="message must be a nonblank string"):
        await ReplyToCustomer(GetProduct(repository), assistant).execute(message, "missing")
    repository.get_by_id.assert_not_called()
    assistant.reply.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [AssistantUnavailable, InvalidAssistantResponse])
async def test_assistant_errors_propagate_unchanged(error_type):
    error = error_type("Private diagnostic")
    assert isinstance(error, AssistantError)
    assistant = AsyncMock(spec=AssistantPort)
    assistant.reply.side_effect = error
    with pytest.raises(error_type) as captured:
        await ReplyToCustomer(GetProduct(AsyncMock()), assistant).execute("Question", None)
    assert captured.value is error
    assistant.reply.assert_awaited_once()
