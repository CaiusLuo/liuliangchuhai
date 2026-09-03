from dataclasses import dataclass
from enum import StrEnum


class RecommendationLevel(StrEnum):
    STRONG_FIT = "strong_fit"
    FIT = "fit"
    CAUTION = "caution"
    NOT_RECOMMENDED = "not_recommended"


def _require_nonblank_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string")


@dataclass(frozen=True, slots=True)
class MarketContext:
    country: str
    target_audience: str | None = None
    market_notes: str | None = None

    def __post_init__(self) -> None:
        _require_nonblank_string(self.country, "country")
        for field in ("target_audience", "market_notes"):
            value = getattr(self, field)
            if value is not None:
                _require_nonblank_string(value, field)


@dataclass(frozen=True, slots=True)
class ProductMarketAnalysis:
    """AI-assisted decision support; score is a heuristic, not a forecast or probability."""

    recommendation: RecommendationLevel
    score: int
    summary: str
    target_audiences: tuple[str, ...]
    strengths: tuple[str, ...]
    risks: tuple[str, ...]
    cultural_advantages: tuple[str, ...]
    marketing_suggestions: tuple[str, ...]
    content_directions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.recommendation, RecommendationLevel):
            raise ValueError("recommendation must be a RecommendationLevel")
        if type(self.score) is not int or not 0 <= self.score <= 100:
            raise ValueError("score must be an integer between 0 and 100 inclusive")
        _require_nonblank_string(self.summary, "summary")
        for field in (
            "target_audiences",
            "strengths",
            "risks",
            "cultural_advantages",
            "marketing_suggestions",
            "content_directions",
        ):
            items = getattr(self, field)
            if not isinstance(items, tuple):
                raise ValueError(f"{field} must be a tuple of nonblank strings")
            for item in items:
                _require_nonblank_string(item, field)
