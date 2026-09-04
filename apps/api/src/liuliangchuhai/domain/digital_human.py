from dataclasses import dataclass


def _require_nonblank_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string")


@dataclass(frozen=True, slots=True)
class DigitalHumanGenerationInput:
    script: str
    language: str

    def __post_init__(self) -> None:
        _require_nonblank_string(self.script, "script")
        _require_nonblank_string(self.language, "language")


@dataclass(frozen=True, slots=True)
class GeneratedVideo:
    media_url: str

    def __post_init__(self) -> None:
        _require_nonblank_string(self.media_url, "media_url")
