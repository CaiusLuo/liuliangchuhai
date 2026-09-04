from typing import Protocol

from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo


class DigitalHumanPort(Protocol):
    """Capability boundary for future digital-human providers."""

    async def status(self) -> ProviderStatus:
        """Return provider availability without generating media."""
        ...

    async def generate(self, generation: DigitalHumanGenerationInput) -> GeneratedVideo:
        """Await completed generation within an adapter deadline or raise DigitalHumanError."""
        ...
