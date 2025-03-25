from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="password")
    postgres_host: str = Field(default="customer-db")
    postgres_port: str = Field(default="5432")
    postgres_name: str = Field(default="postgres_db")
    ASYNC_DATABASE_URL: str = (
        f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_name}"
    )

    @model_validator(mode="after")
    def db_url(self):
        self.ASYNC_DATABASE_URL = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}"


settings = Settings()
