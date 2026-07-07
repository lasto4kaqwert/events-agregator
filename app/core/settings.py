from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import EventProviderClientType


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_connection_string: str

    postgres_database_name: str
    postgres_host: str
    postgres_port: int

    postgres_username: str
    postgres_password: str

    event_provider_api_key: str

    event_provider_host: str
    capashino_host: str

    sync_init_year: int
    sync_init_month: int
    sync_init_day: int

    env_client_type: EventProviderClientType = EventProviderClientType.HTTP

    sentry_dsn: str | None

    environment: str = "local"
    sentry_traces_sample_rate: float = 0.0

    @property
    def async_engine_connection_string(
        self,
    ) -> str:
        return self.postgres_connection_string.replace(
            "postgres://", "postgresql+asyncpg://"
        )

    @property
    def alembic_postgres_connection_string(
        self,
    ) -> str:
        return self.postgres_connection_string.replace(
            "postgres://", "postgresql://"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()
