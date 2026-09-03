from liuliangchuhai.bootstrap.settings import Settings


def test_provider_defaults_are_mock() -> None:
    settings = Settings(_env_file=None)

    assert settings.llm_provider == "mock"
    assert settings.digital_human_provider == "mock"


def test_provider_settings_use_project_prefix(monkeypatch) -> None:
    monkeypatch.setenv("LIULIANGCHUHAI_LLM_PROVIDER", "env-test-llm")
    monkeypatch.setenv("LIULIANGCHUHAI_DIGITAL_HUMAN_PROVIDER", "env-test-digital-human")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "env-test-llm"
    assert settings.digital_human_provider == "env-test-digital-human"


def test_explicit_env_file_is_below_os_environment_and_above_defaults(
    monkeypatch, tmp_path
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LIULIANGCHUHAI_LLM_PROVIDER=file-llm\n"
        "LIULIANGCHUHAI_DIGITAL_HUMAN_PROVIDER=file-digital-human\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LIULIANGCHUHAI_LLM_PROVIDER", "os-llm")
    monkeypatch.delenv("LIULIANGCHUHAI_DIGITAL_HUMAN_PROVIDER", raising=False)

    settings = Settings(_env_file=env_file)

    assert settings.llm_provider == "os-llm"
    assert settings.digital_human_provider == "file-digital-human"
