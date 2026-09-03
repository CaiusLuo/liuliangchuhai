from liuliangchuhai.bootstrap.settings import Settings


def test_provider_defaults_are_mock() -> None:
    settings = Settings(_env_file=None)

    assert settings.llm_provider == "mock"
    assert settings.digital_human_provider == "mock"


def test_provider_settings_use_project_prefix(monkeypatch) -> None:
    monkeypatch.setenv("LIULIANGCHUHAI_LLM_PROVIDER", "mock")
    monkeypatch.setenv("LIULIANGCHUHAI_DIGITAL_HUMAN_PROVIDER", "mock")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "mock"
    assert settings.digital_human_provider == "mock"
