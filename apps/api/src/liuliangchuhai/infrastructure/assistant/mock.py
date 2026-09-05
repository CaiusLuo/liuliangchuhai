from liuliangchuhai.application.ports.assistant import (
    AssistantActionType,
    AssistantReply,
    AssistantSuggestedAction,
)
from liuliangchuhai.domain.product import Product


class MockAssistantAdapter:
    """Deterministic, credential-free product information; no actions are executed."""

    async def reply(self, message: str, product: Product | None) -> AssistantReply:
        boundary = "这是演示商品信息助手, 仅提供信息和浏览建议, 不执行购买、订单或退款等操作。"
        if product is None:
            return AssistantReply(
                message=f"{boundary}选择一个广西特色演示商品后, 我可以介绍其用途、配料和文化背景。"
            )
        ingredients = "、".join(product.ingredients) if product.ingredients else "暂无配料信息"
        return AssistantReply(
            message=(
                f"{product.name}: {product.description}\n"
                f"文化背景: {product.cultural_background}\n"
                f"用途: {product.usage}\n配料: {ingredients}\n{boundary}"
            ),
            suggested_action=AssistantSuggestedAction(AssistantActionType.VIEW_PRODUCT, product.id),
        )
