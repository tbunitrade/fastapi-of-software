# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # .../app/core/config.py -> .../ (root)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_ignore_empty=True, extra="ignore")

    PROJECT_NAME: str = "OF API V1 Campaing Manager"
    API_V1_STR: str = "/api/v1"

    # DB
    POSTGRES_HOST:  str = "localhost"
    POSTGRES_PORT:  int = 5432
    POSTGRES_USER:  str = "postgres"
    POSTGRES_PASSWORD:  str = "postgres"
    POSTGRES_DB:    str = "of_campaings"

    # Auth (если шаблон уже даёт JWT — просто свяжешь)
    SECRET_KEY: str = Field(default="change-me", description="JWT/crypto secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int =  60 * 24

    # Crypto for api_key_encrypted (v1 можно Fernet)
    FERNET_KEY : str = Field(default="", description="Base63-encoded fernet key; generate in ops")

    # Dev helpers
    CREATE_TABLES_ON_STARTUP: bool = True

    #Limits thresholds (v1)
    RATE_LIMIT_MINUTE_LOW: int = 50
    RATE_LIMIT_DAY_LOW: int = 500

    # External API (all from .env)
    PROVIDER_BASE_URL: str = "https://api.provider.example"
    PROVIDER_TIMEOUT_SECONDS: int = 25
    PROVIDER_API_KEY_HEADER: str = "Authorization"
    PROVIDER_API_KEY_PREFIX: str = "Bearer"

    # Secrets (do NOT hardcode; keep in .env)
    PROVIDER_API_KEY: str = Field(default="", repr=False)
    PROVIDER_CLIENT_ID: str = Field(default="", repr=False)
    PROVIDER_CLIENT_SECRET: str = Field(default="", repr=False)

    # Финализация /provider/{account_id}/send под новый DTO
    PROVIDER_SEND_PATH_TEMPLATE: str = "/api/{account}/mass-messaging"
    PROVIDER_OVERVIEW_PATH_TEMPLATE: str = "/api/{account}/mass-messaging/overview"

    @property
    def DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()