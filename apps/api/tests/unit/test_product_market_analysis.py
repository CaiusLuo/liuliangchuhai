import json
from dataclasses import replace

import pytest
from liuliangchuhai.domain.market_analysis import ProductMarketAnalysis, RecommendationLevel


@pytest.fixture
def analysis() -> ProductMarketAnalysis:
    return ProductMarketAnalysis(
        recommendation=RecommendationLevel.FIT,
        score=70,
        summary="Demo heuristic assessment; validate assumptions with customers.",
        target_audiences=("Students",),
        strengths=("Distinctive flavor",),
        risks=("Taste preferences need validation",),
        cultural_advantages=("Guangxi food heritage",),
        marketing_suggestions=("Test small sample packs",),
        content_directions=("Explain preparation and origin",),
    )


def test_recommendation_levels_are_exact_and_string_serializable() -> None:
    expected = {"strong_fit", "fit", "caution", "not_recommended"}

    assert {level.value for level in RecommendationLevel} == expected
    assert all(isinstance(level, str) for level in RecommendationLevel)
    assert set(json.loads(json.dumps(list(RecommendationLevel)))) == expected


def test_valid_complete_analysis(analysis: ProductMarketAnalysis) -> None:
    assert analysis.recommendation is RecommendationLevel.FIT
    assert analysis.score == 70
    assert analysis.summary == "Demo heuristic assessment; validate assumptions with customers."
    assert analysis.target_audiences == ("Students",)
    assert analysis.strengths == ("Distinctive flavor",)
    assert analysis.risks == ("Taste preferences need validation",)
    assert analysis.cultural_advantages == ("Guangxi food heritage",)
    assert analysis.marketing_suggestions == ("Test small sample packs",)
    assert analysis.content_directions == ("Explain preparation and origin",)


def test_all_collections_may_be_empty(analysis: ProductMarketAnalysis) -> None:
    result = replace(
        analysis,
        target_audiences=(),
        strengths=(),
        risks=(),
        cultural_advantages=(),
        marketing_suggestions=(),
        content_directions=(),
    )

    assert result.target_audiences == result.strengths == result.risks == ()
    assert (
        result.cultural_advantages
        == result.marketing_suggestions
        == result.content_directions
        == ()
    )


@pytest.mark.parametrize("score", [0, 100])
def test_score_bounds_are_inclusive(analysis: ProductMarketAnalysis, score: int) -> None:
    assert replace(analysis, score=score).score == score


@pytest.mark.parametrize("score", [-1, 101, 1.5, True, "70"])
def test_invalid_scores_are_rejected(analysis: ProductMarketAnalysis, score: object) -> None:
    with pytest.raises(ValueError):
        replace(analysis, score=score)


@pytest.mark.parametrize("summary", ["", " \t\n"])
def test_blank_summary_is_rejected(analysis: ProductMarketAnalysis, summary: str) -> None:
    with pytest.raises(ValueError):
        replace(analysis, summary=summary)


@pytest.mark.parametrize(
    "field",
    [
        "target_audiences",
        "strengths",
        "risks",
        "cultural_advantages",
        "marketing_suggestions",
        "content_directions",
    ],
)
def test_blank_collection_items_are_rejected(analysis: ProductMarketAnalysis, field: str) -> None:
    with pytest.raises(ValueError):
        replace(analysis, **{field: ("Valid item", " \t\n")})


@pytest.mark.parametrize("recommendation", ["unknown", "fit", None])
def test_analysis_requires_recommendation_enum(
    analysis: ProductMarketAnalysis, recommendation: object
) -> None:
    with pytest.raises(ValueError):
        replace(analysis, recommendation=recommendation)


def test_unknown_recommendation_value_is_rejected() -> None:
    with pytest.raises(ValueError):
        RecommendationLevel("unknown")
