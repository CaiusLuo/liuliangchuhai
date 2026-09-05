from fastapi import APIRouter
from fastapi.responses import JSONResponse

from liuliangchuhai.application.ports.assistant_errors import (
    AssistantUnavailable,
    InvalidAssistantResponse,
)
from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.application.use_cases.reply_to_customer import ReplyToCustomer
from liuliangchuhai.presentation.http.assistant_mappers import to_assistant_response
from liuliangchuhai.presentation.http.assistant_schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantErrorResponse,
)
from liuliangchuhai.presentation.http.schemas import ProductNotFoundResponse


def create_assistant_router(reply_to_customer: ReplyToCustomer) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/assistant/chat",
        response_model=AssistantChatResponse,
        operation_id="reply_to_customer",
        responses={
            404: {"model": ProductNotFoundResponse, "description": "Product not found"},
            502: {
                "model": AssistantErrorResponse,
                "description": "Assistant service returned an invalid response",
            },
            503: {
                "model": AssistantErrorResponse,
                "description": "Assistant service is temporarily unavailable",
            },
        },
    )
    async def assistant_chat(request: AssistantChatRequest) -> AssistantChatResponse | JSONResponse:
        try:
            reply = await reply_to_customer.execute(request.message, request.product_id)
        except ProductNotFound:
            return JSONResponse(
                status_code=404,
                content=ProductNotFoundResponse(
                    code="product_not_found", message="Product not found"
                ).model_dump(),
            )
        except AssistantUnavailable:
            return JSONResponse(
                status_code=503,
                content=AssistantErrorResponse(
                    code="assistant_unavailable",
                    message="Assistant service is temporarily unavailable",
                ).model_dump(),
            )
        except InvalidAssistantResponse:
            return JSONResponse(
                status_code=502,
                content=AssistantErrorResponse(
                    code="invalid_assistant_response",
                    message="Assistant service returned an invalid response",
                ).model_dump(),
            )
        return to_assistant_response(reply)

    return router
