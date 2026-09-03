from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LIULIANGCHUHAI_",
        extra="ignore",
    )

    llm_provider: str = "mock"
    digital_human_provider: str = "mock"
