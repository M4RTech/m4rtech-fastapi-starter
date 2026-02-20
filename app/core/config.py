# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "M4RTech API"
    VERSION: str = "0.1.0"

    DATABASE_URL: str = "sqlite:///./app.db"
    LOG_LEVEL: str = "INFO"

    TESTING: bool = False   # ← DODAJ TO
settings = Settings()
