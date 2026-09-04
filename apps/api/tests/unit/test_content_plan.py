from dataclasses import FrozenInstanceError, fields, replace
from typing import get_type_hints

import pytest
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan

SCALAR_FIELDS = (
    "image_prompt",
    "short_video_idea",
    "short_video_prompt",
    "live_script",
    "social_caption",
)


@pytest.fixture
def plan() -> ContentGenerationPlan:
    return ContentGenerationPlan(
        key_selling_points=("Guangxi heritage", "Easy preparation"),
        image_prompt="Demo product photograph",
        short_video_idea="Demo preparation story",
        short_video_prompt="Demo close-up of preparation",
        live_script="Demo introduction to this product",
        social_caption="Demo taste of Guangxi",
    )


@pytest.mark.parametrize("language", ["English", "中文", "Tiếng Việt", " English "])
def test_context_accepts_nonblank_language(language: str) -> None:
    context = ContentContext(target_language=language)

    assert isinstance(context.target_language, str)
    assert context.target_language.strip() == language.strip()


@pytest.mark.parametrize("language", ["", " \t\n", None, 42, True, b"English", ["English"]])
def test_context_rejects_invalid_language_without_coercion(language: object) -> None:
    with pytest.raises(ValueError):
        ContentContext(target_language=language)


def test_context_has_only_the_frozen_v1_field() -> None:
    assert tuple(field.name for field in fields(ContentContext)) == ("target_language",)
    assert get_type_hints(ContentContext) == {"target_language": str}


def test_context_is_immutable() -> None:
    context = ContentContext(target_language="English")

    with pytest.raises(FrozenInstanceError):
        context.target_language = "Vietnamese"


def test_valid_plan_has_exact_frozen_fields(plan: ContentGenerationPlan) -> None:
    assert tuple(field.name for field in fields(plan)) == ("key_selling_points", *SCALAR_FIELDS)
    assert get_type_hints(ContentGenerationPlan) == {
        "key_selling_points": tuple[str, ...],
        **dict.fromkeys(SCALAR_FIELDS, str),
    }
    assert plan.key_selling_points == ("Guangxi heritage", "Easy preparation")
    assert plan.image_prompt == "Demo product photograph"
    assert plan.short_video_idea == "Demo preparation story"
    assert plan.short_video_prompt == "Demo close-up of preparation"
    assert plan.live_script == "Demo introduction to this product"
    assert plan.social_caption == "Demo taste of Guangxi"


def test_one_selling_point_is_valid(plan: ContentGenerationPlan) -> None:
    assert replace(plan, key_selling_points=("One point",)).key_selling_points == ("One point",)


@pytest.mark.parametrize("field", ["key_selling_points", *SCALAR_FIELDS])
def test_plan_is_immutable(plan: ContentGenerationPlan, field: str) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(plan, field, getattr(plan, field))


@pytest.mark.parametrize(
    "points",
    [
        pytest.param((), id="empty-tuple"),
        pytest.param(["Valid point"], id="list"),
        pytest.param("Valid point", id="bare-string"),
        pytest.param(None, id="none"),
        pytest.param(("Valid point", 123), id="non-string-item"),
        pytest.param(("Valid point", None), id="none-item"),
        pytest.param(("Valid point", True), id="boolean-item"),
        pytest.param(("",), id="empty-item"),
        pytest.param(("Valid point", " \t\n"), id="whitespace-item"),
    ],
)
def test_plan_rejects_invalid_selling_points(plan: ContentGenerationPlan, points: object) -> None:
    with pytest.raises(ValueError):
        replace(plan, key_selling_points=points)


@pytest.mark.parametrize("field", SCALAR_FIELDS)
@pytest.mark.parametrize("value", ["", " \t\n", None, 42, True, b"text", ("text",), ["text"]])
def test_plan_rejects_invalid_scalars_without_coercion(
    plan: ContentGenerationPlan, field: str, value: object
) -> None:
    with pytest.raises(ValueError):
        replace(plan, **{field: value})
