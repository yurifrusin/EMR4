import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
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

# Canonical deployment profiles. The configured environment string is
# normalized once (trim/lowercase) into exactly one of these values; blank,
# unknown, and non-string values fail closed instead of falling through to
# either dev or production-like behavior.
CANONICAL_ENVIRONMENTS = ("dev", "staging", "production")

# Preserved development CORS defaults. These apply only when the canonical
# profile is dev and no explicit origin list was supplied.
DEV_DEFAULT_CORS_ORIGINS = [
    "https://yurifrusin.github.io",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Hosts permitted to use plain-http origins in development. These are the
# loopback/localhost development forms; every other dev origin must be https.
DEV_HTTP_HOSTS = frozenset({"localhost", "127.0.0.1", "[::1]"})

_HOST_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
_HOSTNAME_RE = re.compile(rf"(?:{_HOST_LABEL}\.)*{_HOST_LABEL}\.?")


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


def _validate_dev_origin(origin: str) -> str:
    """Validate one explicit development origin for credentialed CORS.

    Returns the canonical browser-origin string used by the effective CORS
    allow-list and duplicate detection. Raises ValueError for anything but a bare
    scheme://host[:port] origin acceptable in development.
    """
    if not isinstance(origin, str):
        raise ValueError(
            "CORS origins must be strings, "
            f"got {type(origin).__name__}: {origin!r}."
        )
    if origin == "" or origin.strip() != origin or any(ch.isspace() for ch in origin):
        raise ValueError(
            f"CORS origin must not be blank or contain whitespace: {origin!r}."
        )
    if "*" in origin:
        raise ValueError(
            "CORS origin must not contain a wildcard "
            f"(allow_credentials=True forbids '*'): {origin!r}."
        )
    # urlsplit removes some leading controls and does not preserve the
    # distinction between an absent and an empty query/fragment. Reject on
    # the raw string before parsing so validation cannot erase bad input.
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in origin) or "?" in origin or "#" in origin or "\\" in origin:
        raise ValueError(f"CORS origin contains a control or delimiter: {origin!r}.")
    try:
        parts = urlsplit(origin)
    except ValueError as exc:
        raise ValueError(f"CORS origin is malformed: {origin!r}.") from exc
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        raise ValueError(
            "CORS origin must use the http or https scheme "
            f"with an explicit host: {origin!r}."
        )
    if not parts.netloc or "@" in parts.netloc or parts.netloc.endswith(":"):
        raise ValueError(
            "CORS origin must be a bare scheme://host[:port] "
            f"with no userinfo: {origin!r}."
        )
    if parts.path or parts.query or parts.fragment:
        raise ValueError(
            "CORS origin must not include a path, query, or fragment "
            f"(including a trailing slash): {origin!r}."
        )
    bracketed = "[" in parts.netloc or "]" in parts.netloc
    if bracketed and re.fullmatch(r"\[[0-9A-Fa-f:.]+\](?::[0-9]+)?", parts.netloc) is None:
        raise ValueError(f"CORS origin bracketed host is malformed: {origin!r}.")
    host = parts.hostname or ""
    if not host:
        raise ValueError(f"CORS origin must include a host: {origin!r}.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if bracketed:
            raise ValueError(f"CORS origin bracketed host must be IPv6: {origin!r}.")
        if (_HOSTNAME_RE.fullmatch(host) is None or host.endswith(".")
                or host.rsplit(".", 1)[-1].isdigit()
                or any(label.lower().startswith("0x") for label in host.split("."))):
            raise ValueError(f"CORS origin host is malformed or ambiguous: {origin!r}.")
        canonical_host = host.lower()
    else:
        if isinstance(address, ipaddress.IPv6Address):
            if not parts.netloc.startswith("[") or "%" in parts.netloc:
                raise ValueError(f"CORS origin IPv6 host is malformed: {origin!r}.")
            canonical_host = f"[{address.compressed}]"
        else:
            if bracketed:
                raise ValueError(f"CORS origin bracketed host must be IPv6: {origin!r}.")
            canonical_host = str(address)
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError(f"CORS origin port is malformed: {origin!r}.") from exc
    if port is not None and (port < 1 or port > 65535):
        raise ValueError(f"CORS origin port is malformed: {origin!r}.")
    if scheme == "http" and canonical_host not in DEV_HTTP_HOSTS:
        raise ValueError(
            "http CORS origins are limited to the loopback/localhost "
            f"development hosts; use https otherwise: {origin!r}."
        )
    default_port = 80 if scheme == "http" else 443
    suffix = f":{port}" if port is not None and port != default_port else ""
    return f"{scheme}://{canonical_host}{suffix}"


def _resolve_cors_origins(
    environment: str, configured: Optional[list[str]]
) -> list[str]:
    """Resolve the effective CORS allow-list for a canonical profile.

    Omitted input (None) resolves to the preserved dev defaults in
    development and to [] in staging/production. An explicit empty list is
    accepted in every profile. An explicit nonempty dev list is validated
    and stored in canonical browser-origin form; any nonempty staging/production list
    is rejected. Nothing is silently discarded.
    """
    if configured is None:
        if environment == "dev":
            return list(DEV_DEFAULT_CORS_ORIGINS)
        return []
    if environment != "dev":
        if len(configured) == 0:
            return []
        raise ValueError(
            "The staging/production CORS allow-list is always empty; an "
            "explicit nonempty cors_origins list is rejected "
            f"(got {configured!r}). A nonempty non-development origin "
            "requires a separately reviewed successor."
        )
    seen: set[str] = set()
    effective = []
    for origin in configured:
        canonical = _validate_dev_origin(origin)
        if canonical in seen:
            raise ValueError(
                "Duplicate CORS origin after canonical "
                f"scheme/host comparison: {origin!r}."
            )
        seen.add(canonical)
        effective.append(canonical)
    return effective


class Settings(BaseSettings):
    # Canonical deployment profile: "dev" | "staging" | "production".
    # Normalized once (trim/lowercase) by _canonicalize_environment; blank,
    # unknown, and non-string values fail closed. Gates the fail-closed
    # secret check below.
    environment: str = "dev"

    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"

    secret_key: str = INSECURE_DEFAULT_SECRET
    # The authentication boundary intentionally supports one audited JWT
    # algorithm.  Keeping this a Literal prevents environment configuration
    # from silently enabling an unreviewed asymmetric implementation.
    algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours

    # CORS allow-list (JSON-list environment representation preserved).
    # The omitted default resolves after profile normalization to the dev
    # defaults or []; explicit null is rejected. Explicit dev lists become
    # canonical browser origins; any nonempty staging/production list is
    # rejected. NEVER use "*" with credentials.
    cors_origins: Optional[list[str]] = Field(default=None, validate_default=False)

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

    # Separate default-off authored-synthetic product-context proposal runtime.
    # This does not enable the legacy Bernie provider/runtime gate. The exact
    # practice allowlist must also contain the authenticated practice id.
    reception_one_product_context_runtime_enabled: bool = False
    reception_one_product_context_synthetic_practice_ids: str = ""
    # Separate exact gate for the isolated Gemini 2.5 Flash Sydney planner.
    # Empty paths fail closed; routine deterministic planning is unaffected.
    reception_one_product_context_vertex_planner_enabled: bool = False
    reception_one_product_context_vertex_authority_path: str = ""
    reception_one_product_context_vertex_preflight_path: str = ""
    reception_one_product_context_vertex_evidence_dir: str = ""
    rayleen_a4_product_read_enabled: bool = False
    rayleen_a4_synthetic_practice_ids: str = ""
    # Default-off A5.1 Rayleen check-in command runtime. This is a dedicated
    # Receptionist-confirmed Booked|Confirmed -> Arrived command path scoped to
    # exactly the authored-synthetic practices in the allowlist below. It never
    # opens the generic status-confirm route, GraphQL mutations, providers,
    # product data, deployment or release.
    rayleen_a5_check_in_enabled: bool = False
    rayleen_a5_check_in_synthetic_practice_ids: str = ""
    rayleen_a4_vertex_selector_enabled: bool = False
    rayleen_a4_vertex_authority_path: str = ""
    rayleen_a4_vertex_preflight_path: str = ""
    rayleen_a4_vertex_evidence_dir: str = ""

    # B4.1 Davida default-location command runtime (default-off). The exact
    # authored-synthetic practice allowlist is separate from every other gate,
    # and a dedicated server-only command secret is required before any B4
    # proposal, evidence or confirm path opens. Missing/invalid configuration
    # fails the whole feature closed before practitioner or location lookup.
    b4_default_location_command_runtime_enabled: bool = False
    b4_default_location_command_synthetic_practice_ids: str = ""
    b4_default_location_command_secret: str = ""

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

    @field_validator("environment", mode="before")
    @classmethod
    def _canonicalize_environment(cls, value):
        """Normalize the configured profile once into its canonical form."""
        if not isinstance(value, str):
            raise ValueError(
                "ENVIRONMENT must be one of 'dev', 'staging', 'production' "
                f"(case-insensitive); got non-string value {value!r}."
            )
        canonical = value.strip().lower()
        if canonical not in CANONICAL_ENVIRONMENTS:
            raise ValueError(
                "ENVIRONMENT must be one of 'dev', 'staging', 'production' "
                f"(case-insensitive); got {value!r}."
            )
        return canonical

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings,
        dotenv_settings, file_secret_settings,
    ):
        # The environment sources discard a decoded JSON null. Reject that
        # explicit input before it can become indistinguishable from omission.
        # Inspect their already loaded values; preserve all original sources,
        # their configuration and their normal precedence.
        field = settings_cls.model_fields["cors_origins"]
        for source in (env_settings, dotenv_settings):
            raw, _, _ = source.get_field_value(field, "cors_origins")
            if isinstance(raw, str) and raw.strip() == "null":
                raise ValueError("Explicit null CORS_ORIGINS is not a list.")
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _validate_raw_cors_list(cls, value):
        # Only this omitted sentinel skips default validation; supplied null does not.
        # This runs before Pydantic can turn bytes into strings.
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError("CORS_ORIGINS must be a JSON list of strings, not null or another type.")
        return value

    @model_validator(mode="after")
    def _fail_closed_on_insecure_secret(self):
        """Resolve profile CORS, then refuse to start on insecure non-dev config.

        CORS resolution runs first so every profile observes its exact
        effective allow-list; the pre-existing insecure-secret and Bernie
        provider fail-closed checks below are preserved unchanged in meaning.
        The environment value consumed here is the canonical profile produced
        by _canonicalize_environment.
        """
        if "cors_origins" in self.model_fields_set and self.cors_origins is None:
            raise ValueError("Explicit null CORS_ORIGINS is not a list.")
        self.cors_origins = _resolve_cors_origins(self.environment, self.cors_origins)
        if self.environment != "dev" and (
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
