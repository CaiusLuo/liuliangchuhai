from liuliangchuhai.application.ports.assistant import AssistantReply
from liuliangchuhai.presentation.http.assistant_schemas import (
    AssistantChatResponse,
    AssistantSuggestedActionResponse,
)


def to_assistant_response(reply: AssistantReply) -> AssistantChatResponse:
    action = reply.suggested_action
    return AssistantChatResponse(
        message=reply.message,
        suggested_action=AssistantSuggestedActionResponse(
            type=action.type, product_id=action.product_id
        )
        if action is not None
        else None,
    )
