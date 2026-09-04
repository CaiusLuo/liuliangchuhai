from dataclasses import FrozenInstanceError, fields, replace
from typing import get_type_hints

import pytest
from liuliangchuhai.domain.digital_human import DigitalHumanGenerationInput, GeneratedVideo


@pytest.mark.parametrize("value", ["English", "中文", "Tiếng Việt", " text "])
def test_generation_values_accept_nonblank_strings_unchanged(value: str) -> None:
    generation = DigitalHumanGenerationInput(script=value, language=value)
    video = GeneratedVideo(media_url=value)

    assert generation.script == generation.language == video.media_url == value


@pytest.mark.parametrize(
    ("value", "expected_fields"),
    [
        (DigitalHumanGenerationInput("Demo script", "English"), ("script", "language")),
        (GeneratedVideo("mock://digital-human/generated-video.mp4"), ("media_url",)),
    ],
)
def test_generation_values_have_only_frozen_slotted_contract_fields(
    value: DigitalHumanGenerationInput | GeneratedVideo, expected_fields: tuple[str, ...]
) -> None:
    assert tuple(field.name for field in fields(value)) == expected_fields
    assert get_type_hints(type(value)) == dict.fromkeys(expected_fields, str)
    assert not hasattr(value, "__dict__")
    for field in expected_fields:
        with pytest.raises(FrozenInstanceError):
            setattr(value, field, "changed")


@pytest.mark.parametrize(
    ("value", "field"),
    [
        (DigitalHumanGenerationInput("Demo script", "English"), "script"),
        (DigitalHumanGenerationInput("Demo script", "English"), "language"),
        (GeneratedVideo("mock://digital-human/generated-video.mp4"), "media_url"),
    ],
)
@pytest.mark.parametrize("invalid", ["", " \t\n", None, 42, True, b"text", ["text"]])
def test_generation_values_reject_invalid_fields_without_coercion(
    value: DigitalHumanGenerationInput | GeneratedVideo, field: str, invalid: object
) -> None:
    with pytest.raises(ValueError, match=f"^{field} must be a nonblank string$"):
        replace(value, **{field: invalid})
