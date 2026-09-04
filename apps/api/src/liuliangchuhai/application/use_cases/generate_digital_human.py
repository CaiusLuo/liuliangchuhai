from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo


class GenerateDigitalHumanUseCase:
    def __init__(self, digital_human: DigitalHumanPort) -> None:
        self._digital_human = digital_human

    async def execute(self, generation: DigitalHumanGenerationInput) -> GeneratedVideo:
        return await self._digital_human.generate(generation)
