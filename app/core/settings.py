import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"), extra="ignore"
    )


class DatabaseConfig(BaseConfig):
    HOST: str = Field(..., alias="POSTGRES_HOST")
    PORT: int = Field(..., alias="POSTGRES_PORT")
    USER: str = Field(..., alias="POSTGRES_USER")
    PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    DB: str = Field(..., alias="POSTGRES_DB")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


class RedisConfig(BaseConfig):
    HOST: str = Field(..., alias="REDIS_HOST")
    PORT: int = Field(..., alias="REDIS_PORT")


class AuthSettings(BaseConfig):
    SECRET_KEY: str = Field(..., alias="JWT_SECRET_KEY")
    ALGORITHM: str = Field(..., alias="JWT_ALGORITHM")
    TOKEN_EXPIRE_MINUTES: int = 60


class Auth0Settings(BaseConfig):
    DOMAIN: str = Field(..., alias="AUTH0_DOMAIN")
    AUDIENCE: str = Field(..., alias="AUTH0_AUDIENCE")
    CLIENT_ID: str = Field(..., alias="AUTH0_CLIENT_ID")
    JWKS_URL: str = Field(..., alias="AUTH0_JWKS_URL")


class AppSettings(BaseConfig):
    HOST: str
    PORT: int
    RELOAD: bool
    ALLOW_ORIGINS: list[str]
    ALLOW_METHODS: list[str]
    ALLOW_HEADERS: list[str]
    LOG_LEVEL: str

    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    auth: AuthSettings = AuthSettings()
    auth0: Auth0Settings = Auth0Settings()


settings = AppSettings()
