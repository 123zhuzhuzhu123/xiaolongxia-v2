"""应用配置。"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "小龙虾视频分析平台 V2"
    debug: bool = False

    # Database
    database_url: str = "postgresql://root@localhost:5432/xiaolongxia_v2"

    # Redis
    redis_url: str = "redis://localhost:6379/1"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # LLM
    llm_api_base: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None

    # Crawler
    crawler_base_url: str = "http://127.0.0.1:8205"

    # Media storage
    storage_dir: str = "./storage"


@lru_cache
def get_settings() -> Settings:
    return Settings()
