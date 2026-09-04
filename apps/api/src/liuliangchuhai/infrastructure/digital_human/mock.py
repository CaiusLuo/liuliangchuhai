from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo


class MockDigitalHumanAdapter:
    """Deterministic fallback that performs no media generation."""

    async def status(self) -> ProviderStatus:
        return ProviderStatus(provider="mock", available=True)

    async def generate(self, generation: DigitalHumanGenerationInput) -> GeneratedVideo:
        """Return a fixed contract/test/demo placeholder; no video is rendered or hosted."""
        return GeneratedVideo(media_url="mock://digital-human/generated-video.mp4")
