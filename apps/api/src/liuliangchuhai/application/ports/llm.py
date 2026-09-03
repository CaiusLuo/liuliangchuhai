from typing import Protocol

from liuliangchuhai.application.ports.status import ProviderStatus


class LLMPort(Protocol):
    """Capability boundary for future language-model providers."""

    async def status(self) -> ProviderStatus:
        """Return provider availability without performing business behavior."""
        ...
