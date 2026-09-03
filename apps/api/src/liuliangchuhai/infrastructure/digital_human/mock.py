from liuliangchuhai.application.ports.status import ProviderStatus


class MockDigitalHumanAdapter:
    """Deterministic fallback that performs no media generation."""

    async def status(self) -> ProviderStatus:
        return ProviderStatus(provider="mock", available=True)
