from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="password")
    postgres_host: str = Field(default="customer-db")
    postgres_port: str = Field(default="5432")
    postgres_name: str = Field(default="postgres_db")


settings = Settings()
