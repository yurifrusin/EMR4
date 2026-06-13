from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours

    gcp_project: str = "emr4-copilot"
    gcp_location: str = "us-central1"
    google_application_credentials: Optional[str] = "gcp-key.json"

    data_store_id: str = "mbs-search-app_1780903132373"
    data_store_location: str = "global"

    clicksend_username: Optional[str] = None
    clicksend_api_key: Optional[str] = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


settings = Settings()
