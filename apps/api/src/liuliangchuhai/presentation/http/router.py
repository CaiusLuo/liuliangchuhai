from fastapi import APIRouter

from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.application.use_cases.get_system_status import GetSystemStatus
from liuliangchuhai.presentation.http.schemas import (
    HealthResponse,
    ProvidersResponse,
    ProviderStatusResponse,
)


def _map_provider(status: ProviderStatus) -> ProviderStatusResponse:
    return ProviderStatusResponse(provider=status.provider, available=status.available)


def create_router(get_system_status: GetSystemStatus) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse, operation_id="get_health")
    async def get_health() -> HealthResponse:
        result = await get_system_status.execute()
        return HealthResponse(
            status="ok",
            providers=ProvidersResponse(
                llm=_map_provider(result.llm),
                digital_human=_map_provider(result.digital_human),
            ),
        )

    return router
