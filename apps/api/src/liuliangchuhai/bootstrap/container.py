from dataclasses import dataclass

from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.application.use_cases.get_system_status import GetSystemStatus
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter


@dataclass(frozen=True, slots=True)
class Container:
    llm: LLMPort
    digital_human: DigitalHumanPort
    get_system_status: GetSystemStatus


def _build_llm(provider: str) -> LLMPort:
    if provider == "mock":
        return MockLLMAdapter()
    raise ValueError(f"Unsupported LLM provider: {provider!r}")


def _build_digital_human(provider: str) -> DigitalHumanPort:
    if provider == "mock":
        return MockDigitalHumanAdapter()
    raise ValueError(f"Unsupported digital-human provider: {provider!r}")


def build_container(settings: Settings) -> Container:
    llm = _build_llm(settings.llm_provider)
    digital_human = _build_digital_human(settings.digital_human_provider)
    return Container(
        llm=llm,
        digital_human=digital_human,
        get_system_status=GetSystemStatus(llm=llm, digital_human=digital_human),
    )
