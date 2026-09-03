import asyncio
from dataclasses import dataclass

from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.application.ports.status import ProviderStatus


@dataclass(frozen=True, slots=True)
class SystemStatus:
    llm: ProviderStatus
    digital_human: ProviderStatus


class GetSystemStatus:
    """Report wiring health; this intentionally contains no product behavior."""

    def __init__(self, llm: LLMPort, digital_human: DigitalHumanPort) -> None:
        self._llm = llm
        self._digital_human = digital_human

    async def execute(self) -> SystemStatus:
        llm_status, digital_human_status = await asyncio.gather(
            self._llm.status(),
            self._digital_human.status(),
        )
        return SystemStatus(llm=llm_status, digital_human=digital_human_status)
