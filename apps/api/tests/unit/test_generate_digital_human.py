import pytest
from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.application.ports.digital_human_errors import (
    DigitalHumanDeadlineExceeded,
    DigitalHumanError,
    DigitalHumanRejected,
    DigitalHumanUnavailable,
    InvalidDigitalHumanResponse,
)
from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.application.use_cases.generate_digital_human import GenerateDigitalHumanUseCase
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo


class FakeDigitalHuman:
    def __init__(self, result: GeneratedVideo, error: DigitalHumanError | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[DigitalHumanGenerationInput] = []

    async def status(self) -> ProviderStatus:
        raise AssertionError("Generation must not query status")

    async def generate(self, generation: DigitalHumanGenerationInput) -> GeneratedVideo:
        self.calls.append(generation)
        if self.error is not None:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_generation_forwards_exact_input_once_and_returns_exact_result() -> None:
    expected = GeneratedVideo("mock://test/video.mp4")
    fake = FakeDigitalHuman(expected)
    port: DigitalHumanPort = fake
    generation = DigitalHumanGenerationInput(script="Demo script", language="English")

    actual = await GenerateDigitalHumanUseCase(port).execute(generation)

    assert actual is expected
    assert len(fake.calls) == 1
    assert fake.calls[0] is generation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_type",
    [
        DigitalHumanUnavailable,
        DigitalHumanRejected,
        InvalidDigitalHumanResponse,
        DigitalHumanDeadlineExceeded,
    ],
)
async def test_normalized_failures_propagate_unchanged_without_retry_or_fallback(
    error_type: type[DigitalHumanError],
) -> None:
    error = error_type("Generation failed")
    fake = FakeDigitalHuman(GeneratedVideo("mock://test/video.mp4"), error=error)
    generation = DigitalHumanGenerationInput(script="Demo script", language="English")

    with pytest.raises(error_type) as captured:
        await GenerateDigitalHumanUseCase(fake).execute(generation)

    assert captured.value is error
    assert isinstance(captured.value, DigitalHumanError)
    assert len(fake.calls) == 1
    assert fake.calls[0] is generation
