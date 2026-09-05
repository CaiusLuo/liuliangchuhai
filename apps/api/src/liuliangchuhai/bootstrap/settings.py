from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LIULIANGCHUHAI_",
        env_file=".env",
        extra="ignore",
    )

    llm_provider: str = "mock"
    deepseek_api_key: SecretStr | None = None
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_timeout_seconds: float = Field(default=20, gt=0)
    digital_human_provider: str = "mock"
    cors_origins: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def require_selected_provider_credentials(self) -> Self:
        if self.llm_provider == "deepseek" and (
            self.deepseek_api_key is None or not self.deepseek_api_key.get_secret_value().strip()
        ):
            raise ValueError(
                "LIULIANGCHUHAI_DEEPSEEK_API_KEY is required when the LLM provider is deepseek"
            )
        return self
