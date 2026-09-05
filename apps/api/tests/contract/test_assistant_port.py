from dataclasses import FrozenInstanceError, replace

import pytest
from liuliangchuhai.application.ports.assistant import (
    AssistantActionType,
    AssistantPort,
    AssistantReply,
    AssistantSuggestedAction,
)
from liuliangchuhai.infrastructure.assistant.mock import MockAssistantAdapter


@pytest.mark.asyncio
async def test_mock_is_deterministic_product_aware_and_stateless(products):
    adapter: AssistantPort = MockAssistantAdapter()
    product = replace(
        products[0], name="Canonical test product", cultural_background="Test culture"
    )
    original = replace(product)
    reply = await adapter.reply("文化背景?请下单并退款", product)
    assert reply == await adapter.reply("文化背景?请下单并退款", product)
    for value in (product.name, product.description, product.cultural_background, product.usage):
        assert value in reply.message
    assert all(value in reply.message for value in product.ingredients)
    assert reply.suggested_action == AssistantSuggestedAction(
        AssistantActionType.VIEW_PRODUCT, product.id
    )
    assert "不执行" in reply.message
    generic = await adapter.reply("介绍一下", None)
    assert generic.suggested_action is None
    assert "演示商品" in generic.message
    assert product.name not in generic.message
    assert len(generic.message) < 300
    assert generic == await MockAssistantAdapter().reply("介绍一下", None)
    assert product == original
    assert reply == await adapter.reply("文化背景?请下单并退款", product)


def test_reply_and_action_are_frozen_slotted_values():
    action = AssistantSuggestedAction(AssistantActionType.START_ANALYSIS, "tea")
    reply = AssistantReply("Answer", action)
    assert AssistantReply("Generic").suggested_action is None
    for value, field in ((reply, "message"), (action, "product_id")):
        assert not hasattr(value, "__dict__")
        with pytest.raises(FrozenInstanceError):
            setattr(value, field, "changed")
