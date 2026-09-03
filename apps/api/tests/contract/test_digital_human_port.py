import asyncio
from collections.abc import Callable

import pytest
from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter


@pytest.mark.parametrize("adapter_factory", [MockDigitalHumanAdapter])
def test_digital_human_adapter_contract(
    adapter_factory: Callable[[], DigitalHumanPort],
) -> None:
    adapter = adapter_factory()

    status = asyncio.run(adapter.status())

    assert status.provider == "mock"
    assert status.available is True
