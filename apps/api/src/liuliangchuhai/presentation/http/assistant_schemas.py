from typing import Literal

from pydantic import BaseModel, ConfigDict

from liuliangchuhai.application.ports.assistant import AssistantActionType
from liuliangchuhai.presentation.http.schemas import NonBlankString


class AssistantChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: NonBlankString
    product_id: NonBlankString | None = None


class AssistantSuggestedActionResponse(BaseModel):
    type: AssistantActionType
    product_id: str


class AssistantChatResponse(BaseModel):
    message: NonBlankString
    suggested_action: AssistantSuggestedActionResponse | None


class AssistantErrorResponse(BaseModel):
    code: Literal["assistant_unavailable", "invalid_assistant_response"]
    message: str
