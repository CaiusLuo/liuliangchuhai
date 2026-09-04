from dataclasses import dataclass


def _require_nonblank_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string")


@dataclass(frozen=True, slots=True)
class ContentContext:
    target_language: str

    def __post_init__(self) -> None:
        _require_nonblank_string(self.target_language, "target_language")


@dataclass(frozen=True, slots=True)
class ContentGenerationPlan:
    """Validated materials for downstream tools; not generated media."""

    key_selling_points: tuple[str, ...]
    image_prompt: str
    short_video_idea: str
    short_video_prompt: str
    live_script: str
    social_caption: str

    def __post_init__(self) -> None:
        if not isinstance(self.key_selling_points, tuple) or not self.key_selling_points:
            raise ValueError("key_selling_points must be a nonempty tuple of nonblank strings")
        for point in self.key_selling_points:
            _require_nonblank_string(point, "key_selling_points")
        for field in (
            "image_prompt",
            "short_video_idea",
            "short_video_prompt",
            "live_script",
            "social_caption",
        ):
            _require_nonblank_string(getattr(self, field), field)
