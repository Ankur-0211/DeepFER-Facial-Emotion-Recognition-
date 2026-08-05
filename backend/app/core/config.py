from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"  # backend/.env, regardless of cwd


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    APP_NAME: str = "DeepFER Backend"
    ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg2://deepfer:deepfer_dev_password@localhost:5432/deepfer"
    JWT_SECRET_KEY: str = "change-me-in-env"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()