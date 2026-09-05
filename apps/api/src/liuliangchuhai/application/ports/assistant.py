from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from liuliangchuhai.domain.product import Product


class AssistantActionType(StrEnum):
    VIEW_PRODUCT = "view_product"
    START_ANALYSIS = "start_analysis"


@dataclass(frozen=True, slots=True)
class AssistantSuggestedAction:
    type: AssistantActionType
    product_id: str


@dataclass(frozen=True, slots=True)
class AssistantReply:
    message: str
    suggested_action: AssistantSuggestedAction | None = None


class AssistantPort(Protocol):
    async def reply(self, message: str, product: Product | None) -> AssistantReply:
        """Reply using canonical context or raise an application-owned AssistantError."""
        ...
