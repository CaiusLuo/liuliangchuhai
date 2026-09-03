from liuliangchuhai.application.ports.status import ProviderStatus


class MockLLMAdapter:
    """Deterministic, key-free adapter used by development and tests."""

    async def status(self) -> ProviderStatus:
        return ProviderStatus(provider="mock", available=True)
