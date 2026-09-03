from typing import Protocol

from liuliangchuhai.application.ports.status import ProviderStatus


class DigitalHumanPort(Protocol):
    """Capability boundary for future digital-human providers."""

    async def status(self) -> ProviderStatus:
        """Return provider availability without generating media."""
        ...
