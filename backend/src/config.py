from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.dev', extra="allow")

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage" / "files"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    REDIS_URL: str = Field(alias="CELERY_BROKER_URL")

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"



settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)