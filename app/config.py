from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional

INSECURE_DEFAULT_SECRET = "change-me-in-production"


class Settings(BaseSettings):
    # "dev" | "staging" | "production" — gates the fail-closed secret check below
    environment: str = "dev"

    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"

    secret_key: str = INSECURE_DEFAULT_SECRET
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours

    # CORS allow-list. Taskpane + Command Centre are served from GitHub Pages;
    # localhost:3000 is the webpack dev-server. NEVER use "*" with credentials.
    cors_origins: list[str] = [
        "https://yurifrusin.github.io",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    gcp_project: str = "scribe-emr4-dev"
    gcp_location: str = "australia-southeast1"
    google_application_credentials: Optional[str] = None

    data_store_id: str = "mbs-search-app_1780903132373"
    data_store_location: str = "global"

    clicksend_username: Optional[str] = None
    clicksend_api_key: Optional[str] = None

    bernie_staff_pilot_enabled: bool = False
    bernie_staff_pilot_practice_ids: str = ""
    bernie_staff_pilot_user_ids: str = ""
    bernie_booking_interpreter_provider: str = "disabled"
    bernie_booking_interpreter_live_temperature: float = 0.0
    bernie_booking_interpreter_fallback_to_deterministic: bool = False

    # Patient file storage. Point this at a OneDrive-synced folder so generated
    # .docx files are immediately accessible via Word Online. The backend creates
    # the directory if it doesn't exist. Production: a SharePoint/Graph path or
    # a cloud-storage mount. Dev: a local path the OneDrive client syncs.
    patient_files_dir: str = "./patient_files"

    # The repo-level .env is shared by the backend and local helper scripts
    # such as WhatsApp operational notifications. Ignore helper-only keys here
    # so adding a local tool secret does not prevent the API from starting.
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def _fail_closed_on_insecure_secret(self):
        """Refuse to start outside dev if the JWT signing key is the public default.
        The repo is AGPL/public, so a default secret_key means anyone can forge
        tokens for any practice."""
        if self.environment.lower() != "dev" and (
            not self.secret_key or self.secret_key == INSECURE_DEFAULT_SECRET
        ):
            raise RuntimeError(
                f"SECRET_KEY must be set to a strong, unique value when "
                f"ENVIRONMENT={self.environment!r}. It is currently the insecure "
                f"public default — refusing to start."
            )
        return self


settings = Settings()
