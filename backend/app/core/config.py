from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "PunoTraffic AI"
    VERSION: str = "1.0.0"
    MODEL_PATH: str = "/app/models/traffic_model_latest.joblib"
    CORS_ORIGINS: List[str] = ["*"]
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()