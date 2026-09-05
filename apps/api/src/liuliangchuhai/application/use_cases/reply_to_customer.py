from liuliangchuhai.application.ports.assistant import AssistantPort, AssistantReply
from liuliangchuhai.application.use_cases.get_product import GetProduct


class ReplyToCustomer:
    def __init__(self, get_product: GetProduct, assistant: AssistantPort) -> None:
        self._get_product = get_product
        self._assistant = assistant

    async def execute(self, message: str, product_id: str | None) -> AssistantReply:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a nonblank string")
        product = await self._get_product.execute(product_id) if product_id is not None else None
        return await self._assistant.reply(message, product)
