import asyncio
from collections.abc import Callable

import pytest
from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter


@pytest.mark.parametrize("adapter_factory", [MockDigitalHumanAdapter])
def test_digital_human_adapter_contract(
    adapter_factory: Callable[[], DigitalHumanPort],
) -> None:
    adapter = adapter_factory()

    status = asyncio.run(adapter.status())

    assert status.provider == "mock"
    assert status.available is True


@pytest.mark.parametrize("adapter_factory", [MockDigitalHumanAdapter])
@pytest.mark.asyncio
async def test_digital_human_generation_contract(
    adapter_factory: Callable[[], DigitalHumanPort],
) -> None:
    adapter = adapter_factory()
    generation = DigitalHumanGenerationInput(script="Demo script", language="English")
    before = await adapter.status()

    first = await adapter.generate(generation)
    repeated = await adapter.generate(generation)
    fresh = await adapter_factory().generate(generation)

    assert type(first) is GeneratedVideo
    assert isinstance(first.media_url, str) and first.media_url.strip()
    assert GeneratedVideo(media_url=first.media_url) == first
    assert first == repeated == fresh
    assert await adapter.status() == before


@pytest.mark.asyncio
async def test_mock_returns_only_a_fixed_placeholder() -> None:
    result = await MockDigitalHumanAdapter().generate(
        DigitalHumanGenerationInput(script="Demo script", language="English")
    )

    assert result == GeneratedVideo(media_url="mock://digital-human/generated-video.mp4")
