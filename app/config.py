from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "舆情预警服务"
    DATABASE_URL: str = "sqlite:///./sentiment_warning.db"
    MAX_CONTENT_LENGTH: int = 100000

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
