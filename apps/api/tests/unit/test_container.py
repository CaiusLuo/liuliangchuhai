import pytest
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter


def test_container_wires_mock_providers() -> None:
    container = build_container(Settings(_env_file=None))

    assert isinstance(container.llm, MockLLMAdapter)
    assert isinstance(container.digital_human, MockDigitalHumanAdapter)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("llm_provider", "unknown"),
        ("digital_human_provider", "unknown"),
    ],
)
def test_container_rejects_unknown_provider(field: str, value: str) -> None:
    settings = Settings(_env_file=None, **{field: value})

    with pytest.raises(ValueError, match=r"Unsupported .* provider"):
        build_container(settings)
