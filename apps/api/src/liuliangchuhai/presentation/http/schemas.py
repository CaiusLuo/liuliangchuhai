from typing import Literal

from pydantic import BaseModel


class ProviderStatusResponse(BaseModel):
    provider: str
    available: bool


class ProvidersResponse(BaseModel):
    llm: ProviderStatusResponse
    digital_human: ProviderStatusResponse


class HealthResponse(BaseModel):
    status: Literal["ok"]
    providers: ProvidersResponse
