from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env"
    )

    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    ALGORITHM: str

    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: PostgresDsn

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_CAHCE_DB: int
    REDIS_BROKER_DB: int
    CACHE_TTL: int

settings = Settings()