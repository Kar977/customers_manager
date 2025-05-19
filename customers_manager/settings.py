from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent / ".env")
    postgres_user: str = Field()
    postgres_password: str = Field()
    postgres_host: str = Field()
    postgres_port: str = Field()
    postgres_name: str = Field()
    ASYNC_DATABASE_URL: str = ""

    @model_validator(mode="after")
    def db_url(self):
        self.ASYNC_DATABASE_URL = (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
                                   f"{self.postgres_host}:{self.postgres_port}/{self.postgres_name}")
        return self


settings = Settings()
