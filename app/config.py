import json
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Literal, Optional

INSECURE_DEFAULT_SECRET = "change-me-in-production"
REPO_ROOT = Path(__file__).resolve().parents[1]
BERNIE_RUNTIME_GATE_PATH = REPO_ROOT / "docs" / "bernie-interpretation-harness-runtime-gate.json"
LIVE_BERNIE_INTERPRETER_PROVIDERS = {
    "gemini",
    "gemini_vertex",
    "vertex",
    "vertex_gemini",
}


def assert_bernie_provider_allowed_by_runtime_gate(
    provider: str,
    gate_path: Path = BERNIE_RUNTIME_GATE_PATH,
) -> None:
    """Fail closed if live Bernie provider config appears while the gate is blocked."""

    normalized_provider = (provider or "").strip().lower()
    if normalized_provider not in LIVE_BERNIE_INTERPRETER_PROVIDERS:
        return

    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Bernie live-provider configuration is blocked because the "
            "runtime/provider gate could not be read."
        ) from exc

    scope = gate.get("scope")
    provider_scope_enabled = (
        isinstance(scope, dict)
        and (
            scope.get("provider_dry_run_wiring") is True
            or scope.get("route_integration") is True
        )
    )
    if gate.get("decision") == "blocked" or not provider_scope_enabled:
        raise RuntimeError(
            "Bernie live-provider configuration is blocked by "
            "docs/bernie-interpretation-harness-runtime-gate.json. "
            "Keep BERNIE_BOOKING_INTERPRETER_PROVIDER disabled or fake until "
            "Yuri approves a scoped provider gate change."
        )


class Settings(BaseSettings):
    # "dev" | "staging" | "production" — gates the fail-closed secret check below
    environment: str = "dev"

    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"

    secret_key: str = INSECURE_DEFAULT_SECRET
    # The authentication boundary intentionally supports one audited JWT
    # algorithm.  Keeping this a Literal prevents environment configuration
    # from silently enabling an unreviewed asymmetric implementation.
    algorithm: Literal["HS256"] = "HS256"
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
    bernie_booking_interpreter_fallback_to_deterministic: bool = True
    # Emit raw debug_score and internal codes in the 'debug' field only when True.
    # Ordinary reception staff should never see raw scores or snake_case codes.
    bernie_interpreter_debug_disclosure: bool = False

    # Default-off local Reception One committed-event proof. This does not
    # authorize a production event runtime or any event beyond reschedule.
    reception_one_committed_event_runtime_enabled: bool = False

    # Raw appointment compatibility endpoint guard.
    #   "audit" - attach raw_compat_* audit evidence tags only.
    #   "header" - attach raw_compat_* audit evidence tags AND set
    #              deprecation response headers.
    #   "off"    - suppress both raw_compat_* tags and deprecation headers.
    appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"

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
        assert_bernie_provider_allowed_by_runtime_gate(
            self.bernie_booking_interpreter_provider
        )
        return self


settings = Settings()
