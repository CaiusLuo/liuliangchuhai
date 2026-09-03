import asyncio
from collections.abc import Callable

import pytest
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter


@pytest.mark.parametrize("adapter_factory", [MockLLMAdapter])
def test_llm_adapter_contract(adapter_factory: Callable[[], LLMPort]) -> None:
    adapter = adapter_factory()

    status = asyncio.run(adapter.status())

    assert status.provider == "mock"
    assert status.available is True
