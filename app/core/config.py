# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env" , env_ignore_empty=True, extra="ignore")

    PROJECT_NAME: str = "OF API V1 Campaing Manager"
    API_V1_STR: str = "/api/v1"

    # DB
    POSTGRES_HOST:  str = "localhost"
    POSTGRES_PORT:  int = 5432
    POSTGRES_USER:  str = "postgres"
    POSTGRES_PASSWORD:  str = "postgres"
    POSTGRES_DB:    str = "of_compaings"

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

    @property
    def DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@self{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()