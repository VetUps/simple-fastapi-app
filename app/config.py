from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env"
    )

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str

    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: PostgresDsn

    REDIS_HOST: str
    REDIS_PORT: int

settings = Settings()