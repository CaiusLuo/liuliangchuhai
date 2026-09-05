from unittest.mock import AsyncMock, Mock

import pytest
from liuliangchuhai.application.ports.assistant_errors import AssistantUnavailable
from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.infrastructure.assistant.deepseek import DeepSeekAssistantAdapter
from liuliangchuhai.infrastructure.assistant.mock import MockAssistantAdapter
from liuliangchuhai.infrastructure.llm.deepseek import DeepSeekLLMAdapter
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter
from pydantic import ValidationError


def test_default_assistant_needs_no_credentials():
    settings = Settings(_env_file=None)
    assert settings.assistant_provider == "mock"
    assert settings.deepseek_api_key is None
    assert isinstance(build_container(settings).assistant, MockAssistantAdapter)


@pytest.mark.parametrize("assistant", ["mock", "deepseek"])
@pytest.mark.parametrize("analysis", ["mock", "deepseek"])
def test_capability_selection_is_independent(assistant, analysis):
    container = build_container(
        Settings(
            _env_file=None,
            assistant_provider=assistant,
            llm_provider=analysis,
            deepseek_api_key="test-key",
        )
    )
    assert isinstance(
        container.assistant,
        DeepSeekAssistantAdapter if assistant == "deepseek" else MockAssistantAdapter,
    )
    assert isinstance(
        container.llm, DeepSeekLLMAdapter if analysis == "deepseek" else MockLLMAdapter
    )


@pytest.mark.parametrize("field", ["assistant_provider", "llm_provider"])
@pytest.mark.parametrize("key", [None, "", "   "])
def test_either_deepseek_capability_requires_shared_key(field, key):
    with pytest.raises(ValidationError, match="DEEPSEEK_API_KEY"):
        Settings(_env_file=None, deepseek_api_key=key, **{field: "deepseek"})


def test_assistant_selector_uses_project_environment_prefix(monkeypatch):
    monkeypatch.setenv("LIULIANGCHUHAI_ASSISTANT_PROVIDER", "deepseek")
    monkeypatch.setenv("LIULIANGCHUHAI_DEEPSEEK_API_KEY", "test-key")
    assert Settings(_env_file=None).assistant_provider == "deepseek"


def test_unknown_assistant_provider_fails_configuration():
    with pytest.raises(ValueError, match="Unsupported assistant provider"):
        build_container(Settings(_env_file=None, assistant_provider="unknown"))


def test_shared_vendor_configuration_is_forwarded(monkeypatch):
    factory = Mock(return_value=MockAssistantAdapter())
    monkeypatch.setattr("liuliangchuhai.bootstrap.container.DeepSeekAssistantAdapter", factory)
    build_container(
        Settings(
            _env_file=None,
            assistant_provider="deepseek",
            deepseek_api_key="test-key",
            deepseek_model="configured-model",
            deepseek_timeout_seconds=7,
        )
    )
    factory.assert_called_once_with(api_key="test-key", model="configured-model", timeout_seconds=7)


@pytest.mark.asyncio
async def test_selected_failure_does_not_fall_back_to_mock(monkeypatch):
    container = build_container(
        Settings(_env_file=None, assistant_provider="deepseek", deepseek_api_key="test-key")
    )
    reply = AsyncMock(side_effect=AssistantUnavailable("Assistant request failed"))
    monkeypatch.setattr(container.assistant, "reply", reply)
    with pytest.raises(AssistantUnavailable):
        await container.reply_to_customer.execute("Question", None)
    reply.assert_awaited_once_with("Question", None)
