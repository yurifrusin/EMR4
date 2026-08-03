"""Task-scoped Office consumer of the accepted application-session directory.

The harness is deliberately absent from ``app.main``. It creates disposable
authored-synthetic PostgreSQL truth, two independent surface sessions and two
surface-bound instances of the accepted GraphQL factory.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import secrets
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graphql.application_auth_product import (  # noqa: E402
    create_application_session_practitioner_directory_router,
)
from app.models.tenancy import (  # noqa: E402
    Practice,
    PracticeLocation,
    Practitioner,
    User,
    UserRole,
)
from app.routers.application_auth import (  # noqa: E402
    get_application_auth_operational_hardening,
    get_application_auth_transport,
    router as application_auth_router,
)
from app.services.application_auth_database_role import (  # noqa: E402
    create_deployment_login_role_statements,
    create_runtime_role_statements,
)
from app.services.application_auth_operational_database import (  # noqa: E402
    ApplicationAuthPoolPolicy,
    create_application_auth_engine,
    create_application_auth_session_factory,
)
from app.services.application_auth_operational_hardening import (  # noqa: E402
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    PostgresTransportDenialAuditSink,
    ProxyTrustPolicy,
)
from app.services.application_auth_product_read import (  # noqa: E402
    ApplicationSessionPractitionerDirectoryBridge,
    SyntheticProductPrincipalBinding,
    SyntheticProductPrincipalRegistry,
)
from app.services.application_auth_product_read_database_role import (  # noqa: E402
    create_product_read_capability_statements,
    create_product_read_login_statements,
)
from app.services.application_auth_product_read_operational import (  # noqa: E402
    ProductReadPoolPolicy,
    create_product_read_engine,
    create_product_read_session_factory,
)
from app.services.application_auth_role_runtime import (  # noqa: E402
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (  # noqa: E402
    AUTHORED_SYNTHETIC_DATA_CLASS,
    Surface,
    SyntheticPrincipal,
)
from app.services.application_auth_transport import (  # noqa: E402
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    ApplicationAuthTransport,
    OneUseSyntheticBootstrapRegistry,
    TransportAuthenticationFailed,
)
from app.services.auth_service import hash_password  # noqa: E402
from scripts.raisa_postgresql_oidc_operational_connection_boundary_acceptance import (  # noqa: E402
    DATABASE_PATTERN,
    _base_database_url,
    _create_database,
    _drop_database,
    _require_alembic,
)
from scripts.raisa_provider_free_session_practitioner_directory_read_bridge_acceptance import (  # noqa: E402
    _drop_role,
)


DEVELOPMENT_ORIGIN = "https://property-cinch-backfield.ngrok-free.dev"
LOCAL_BROWSER_PREVIEW_ORIGIN = "https://localhost:8001"
SURFACES = (Surface.WORD_DESKTOP, Surface.WORD_ONLINE)
MIGRATION_HEAD = "u0v1w2x3y4z5"
RESULT = "provider_free_office_practitioner_directory_consumer_pass"
IN_PROGRESS = "provider_free_office_practitioner_directory_consumer_in_progress"
TASK_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-office-practitioner-directory-consumer"
)
TASKPANE_SCRIPT = TASK_ROOT / "taskpane.js"
TASKPANE_CSS = TASK_ROOT / "taskpane.css"
OFFICE_HOST_STUB = TASK_ROOT / "office-host-stub.js"
EVIDENCE_PATH = TASK_ROOT / "live-office-backend-postgres-evidence.json"
ASSET_ROOT = ROOT / "EMR4 Sidebar" / "assets"

_AUTH_LOGIN = re.compile(r"^emr4_application_auth_login_[0-9a-f]{12}$")
_AUTH_CAPABILITY = re.compile(r"^emr4_application_auth_runtime_[0-9a-f]{12}$")
_PRODUCT_LOGIN = re.compile(r"^emr4_product_read_login_[0-9a-f]{12}$")
_PRODUCT_CAPABILITY = re.compile(r"^emr4_product_read_runtime_[0-9a-f]{12}$")
_NO_STORE_HEADERS = {
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}
_TASKPANE_CSP = (
    "default-src 'none'; "
    "script-src 'self' https://appsforoffice.microsoft.com; "
    "style-src 'self'; img-src 'self'; connect-src 'self'; "
    "base-uri 'none'; form-action 'none'; frame-ancestors "
    "https://*.office.com https://*.officeapps.live.com "
    "https://onedrive.live.com https://*.microsoft.com"
)


class HarnessSetupFailure(RuntimeError):
    """Bounded setup failure containing no generated target or secret."""


class DirectoryResultSubmission(BaseModel):
    """Closed browser result; the raw nonce is never retained."""

    model_config = ConfigDict(extra="forbid")

    evidence_nonce: str
    surface: Literal[Surface.WORD_DESKTOP, Surface.WORD_ONLINE]
    host_class: Literal["installed_word", "word_online"]
    terminal_status: Literal["passed", "failed"]
    directory_read_passed: bool
    exact_projection_passed: bool
    active_practitioner_count: int = Field(ge=0, le=2)
    logout_passed: bool
    result_submitted: bool = True
    failure_code: Literal[
        "none",
        "office_unavailable",
        "office_host_mismatch",
        "launch_unavailable",
        "directory_unavailable",
        "directory_count_invalid",
        "projection_invalid",
        "logout_failed",
        "network_unavailable",
        "unexpected_response",
    ]


class SanitizedDirectoryResult(BaseModel):
    """Durable-safe result with no principal, target or product identifier."""

    model_config = ConfigDict(extra="forbid")

    surface: Literal[Surface.WORD_DESKTOP, Surface.WORD_ONLINE]
    host_class: Literal["installed_word", "word_online"]
    terminal_status: Literal["passed", "failed"]
    directory_read_passed: bool
    exact_projection_passed: bool
    active_practitioner_count: int
    logout_passed: bool
    post_logout_session_denied: bool
    result_submitted: bool
    failure_code: str


@dataclass
class _SurfaceLaunch:
    session_value: str
    csrf_value: str | None
    evidence_nonce: str | None
    evidence_nonce_hash: str
    page_delivered: bool = False


class OfficePractitionerDirectoryHarness:
    """Own the exact temporary auth, product-read and Office UI boundary."""

    def __init__(
        self,
        *,
        origin: str = DEVELOPMENT_ORIGIN,
        output_path: Path | None = EVIDENCE_PATH,
        allow_local_browser_preview: bool = False,
    ) -> None:
        if origin != DEVELOPMENT_ORIGIN and not (
            allow_local_browser_preview and origin == LOCAL_BROWSER_PREVIEW_ORIGIN
        ):
            raise ValueError("the Office directory origin is frozen")
        self.origin = origin
        self.allow_local_browser_preview = allow_local_browser_preview
        self._output_path = output_path
        self._lock = threading.Lock()
        self._close_lock = threading.Lock()
        self._closed = False
        self._results: dict[Surface, SanitizedDirectoryResult] = {}
        self._launches: dict[Surface, _SurfaceLaunch] = {}
        self._raw_values: list[str] = []
        self._sensitive_targets: list[str] = []
        self._created_roles: list[tuple[str, str]] = []
        self._database_created = False
        self._database_name = ""
        self._maintenance: Engine | None = None
        self.owner_engine: Engine | None = None
        self.auth_engine: Engine | None = None
        self.product_engine: Engine | None = None
        self.auth_runtime: RoleScopedPostgresApplicationAuthRuntime | None = None
        self.transport: ApplicationAuthTransport | None = None
        self.guard: ApplicationAuthOperationalHardening | None = None
        self.bridge: ApplicationSessionPractitionerDirectoryBridge | None = None
        self.migration_evidence: dict[str, object] = {}
        self.role_evidence: dict[str, object] = {}
        self.cleanup_evidence: dict[str, object] = {
            "database_absent_after": False,
            "four_task_roles_absent_after": False,
            "pools_disposed": False,
            "passed": False,
        }
        self._final_evidence: dict[str, object] | None = None
        try:
            self._prepare()
        except Exception as exc:
            self._cleanup_resources()
            if isinstance(exc, HarnessSetupFailure):
                raise
            raise HarnessSetupFailure("office_directory_setup_failed") from exc

    @staticmethod
    def _hash(value: str) -> str:
        return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _expected_host(surface: Surface) -> str:
        return "installed_word" if surface is Surface.WORD_DESKTOP else "word_online"

    def _prepare(self) -> None:
        suffix = secrets.token_hex(6)
        database_name = f"emr4_oidc_operational_acceptance_{suffix}"
        auth_login = f"emr4_application_auth_login_{suffix}"
        auth_capability = f"emr4_application_auth_runtime_{suffix}"
        product_login = f"emr4_product_read_login_{suffix}"
        product_capability = f"emr4_product_read_runtime_{suffix}"
        auth_password = secrets.token_urlsafe(36)
        product_password = secrets.token_urlsafe(36)
        identifiers_valid = all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                _AUTH_LOGIN.fullmatch(auth_login),
                _AUTH_CAPABILITY.fullmatch(auth_capability),
                _PRODUCT_LOGIN.fullmatch(product_login),
                _PRODUCT_CAPABILITY.fullmatch(product_capability),
            )
        )
        if not identifiers_valid:
            raise HarnessSetupFailure("generated_identifier_invalid")
        self._database_name = database_name
        self._sensitive_targets.extend(
            (
                database_name,
                auth_login,
                auth_capability,
                product_login,
                product_capability,
                auth_password,
                product_password,
            )
        )
        base = _base_database_url()
        target = base.set(database=database_name)
        auth_target = target.set(username=auth_login, password=auth_password)
        product_target = target.set(username=product_login, password=product_password)
        self._maintenance = create_engine(
            base.set(database="postgres"),
            isolation_level="AUTOCOMMIT",
            pool_pre_ping=True,
        )
        _create_database(self._maintenance, database_name)
        self._database_created = True
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        self.migration_evidence = {
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": True,
            "passed": MIGRATION_HEAD in current,
        }

        self.owner_engine = create_engine(target, pool_pre_ping=True)
        with self.owner_engine.begin() as connection:
            for statement in create_runtime_role_statements(auth_capability):
                connection.execute(text(statement))
            self._created_roles.append((auth_capability, "auth_capability"))
            for statement in create_deployment_login_role_statements(
                auth_login,
                auth_capability,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            self._created_roles.append((auth_login, "auth_login"))
            connection.execute(
                text(f'ALTER ROLE "{auth_login}" PASSWORD \'{auth_password}\'')
            )
            for statement in create_product_read_capability_statements(
                product_capability
            ):
                connection.execute(text(statement))
            self._created_roles.append((product_capability, "product_capability"))
            for statement in create_product_read_login_statements(
                product_login,
                product_capability,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            self._created_roles.append((product_login, "product_login"))
            connection.execute(
                text(
                    f'ALTER ROLE "{product_login}" PASSWORD '
                    f"'{product_password}'"
                )
            )

        owner_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=self.owner_engine,
        )
        principals = {
            surface: SyntheticPrincipal(
                user_id=(
                    "synthetic-user-office-directory-"
                    f"{surface.value.replace('_', '-')}"
                ),
                practice_id=(
                    "synthetic-practice-office-directory-"
                    f"{surface.value.replace('_', '-')}"
                ),
                current_backend_role="GP",
                practitioner_id=(
                    "synthetic-practitioner-office-directory-"
                    f"{surface.value.replace('_', '-')}"
                ),
            )
            for surface in SURFACES
        }
        bindings = self._seed_products(owner_factory, principals)
        origins = {surface: self.origin for surface in Surface}

        self.auth_engine = create_application_auth_engine(
            auth_target.render_as_string(hide_password=False),
            login_role=auth_login,
            capability_role=auth_capability,
            policy=ApplicationAuthPoolPolicy(
                pool_size=1,
                max_overflow=1,
                login_connection_limit=2,
            ),
        )
        auth_factory = create_application_auth_session_factory(self.auth_engine)
        self.auth_runtime = RoleScopedPostgresApplicationAuthRuntime(
            session_factory=auth_factory,
            surface_origins=origins,
        )
        self.transport = ApplicationAuthTransport(
            runtime=self.auth_runtime,
            bootstrap_registry=OneUseSyntheticBootstrapRegistry({}),
            surface_origins=origins,
        )
        self.guard = ApplicationAuthOperationalHardening(
            proxy_policy=ProxyTrustPolicy.from_cidrs(
                []
                if self.allow_local_browser_preview
                else ["127.0.0.0/8", "::1/128"]
            ),
            rate_limiter=BoundedFixedWindowRateLimiter(
                requests_per_window=64,
                window_seconds=300,
                max_keys=64,
            ),
            denial_audit_sink=PostgresTransportDenialAuditSink(auth_factory),
            client_hmac_key=secrets.token_bytes(32),
        )

        self.product_engine = create_product_read_engine(
            product_target,
            login_role=product_login,
            capability_role=product_capability,
            policy=ProductReadPoolPolicy(
                pool_size=1,
                max_overflow=1,
                login_connection_limit=2,
            ),
        )
        self.bridge = ApplicationSessionPractitionerDirectoryBridge(
            runtime=self.auth_runtime,
            product_session_factory=create_product_read_session_factory(
                self.product_engine
            ),
            principal_registry=SyntheticProductPrincipalRegistry(tuple(bindings)),
            surface_origins=origins,
        )

        with self.auth_engine.connect() as auth_connection, self.product_engine.connect() as product_connection:
            auth_identity = auth_connection.execute(
                text("SELECT session_user, current_user")
            ).one()
            product_identity = product_connection.execute(
                text("SELECT session_user, current_user")
            ).one()
        self.role_evidence = {
            "auth_identity_split": auth_identity.session_user != auth_identity.current_user,
            "product_identity_split": (
                product_identity.session_user != product_identity.current_user
            ),
            "separate_capabilities": (
                auth_identity.current_user != product_identity.current_user
            ),
            "pool_maximum_each": 2,
        }
        self.role_evidence["passed"] = all(self.role_evidence.values())
        if not self.role_evidence["passed"]:
            raise HarnessSetupFailure("role_contract_failed")

        for surface, principal in principals.items():
            created = self.auth_runtime.create_session(
                principal=principal,
                surface=surface,
                origin=self.origin,
                correlation_id=(
                    "correlation-office-directory-"
                    f"{surface.value.replace('_', '-')}"
                ),
            )
            csrf_value = f"csrf.{secrets.token_urlsafe(32)}"
            nonce = secrets.token_urlsafe(32)
            self._raw_values.extend(
                (
                    created.parent_session_value,
                    created.surface_session_value,
                    csrf_value,
                    nonce,
                )
            )
            self._launches[surface] = _SurfaceLaunch(
                session_value=created.surface_session_value,
                csrf_value=csrf_value,
                evidence_nonce=nonce,
                evidence_nonce_hash=self._hash(nonce),
            )

    def _seed_products(
        self,
        owner_factory: sessionmaker[Session],
        principals: dict[Surface, SyntheticPrincipal],
    ) -> list[SyntheticProductPrincipalBinding]:
        bindings: list[SyntheticProductPrincipalBinding] = []
        with owner_factory() as db, db.begin():
            for surface, principal in principals.items():
                label = "Desktop" if surface is Surface.WORD_DESKTOP else "Online"
                practice = Practice(name=f"Authored Synthetic {label} Practice")
                db.add(practice)
                db.flush()
                location = PracticeLocation(
                    practice_id=practice.id,
                    name=f"Synthetic {label} Clinic",
                    is_active=True,
                )
                db.add(location)
                db.flush()
                linked = Practitioner(
                    practice_id=practice.id,
                    first_name="Avery",
                    last_name=f"{label} Synthetic",
                    specialty="GP",
                    default_location_id=location.id,
                    is_active=True,
                    provider_number=(
                        "SYNTH-WD-001"
                        if surface is Surface.WORD_DESKTOP
                        else "SYNTH-WO-001"
                    ),
                )
                second = Practitioner(
                    practice_id=practice.id,
                    first_name="Morgan",
                    last_name=f"{label} Synthetic",
                    specialty="GP",
                    is_active=True,
                )
                inactive = Practitioner(
                    practice_id=practice.id,
                    first_name="Inactive",
                    last_name=f"{label} Synthetic",
                    specialty="GP",
                    is_active=False,
                )
                db.add_all((linked, second, inactive))
                db.flush()
                user = User(
                    practice_id=practice.id,
                    email=f"gp-{surface.value}@authored-synthetic.invalid",
                    password_hash=hash_password("AuthoredSyntheticOnly1!"),
                    role=UserRole.GP,
                    practitioner_id=linked.id,
                    is_active=True,
                )
                db.add(user)
                db.flush()
                bindings.append(
                    SyntheticProductPrincipalBinding(
                        user_ref=principal.user_id,
                        practice_ref=principal.practice_id,
                        user_id=user.id,
                        practice_id=practice.id,
                        practitioner_ref=principal.practitioner_id,
                        practitioner_id=linked.id,
                    )
                )
        return bindings

    def deliver_taskpane(
        self,
        surface: Surface,
    ) -> tuple[str, str, str]:
        with self._lock:
            launch = self._launches[surface]
            if launch.page_delivered:
                csrf_value = ""
                nonce = ""
                session_value = ""
            else:
                csrf_value = launch.csrf_value or ""
                nonce = launch.evidence_nonce or ""
                session_value = launch.session_value
                launch.csrf_value = None
                launch.evidence_nonce = None
                launch.page_delivered = True
        endpoint = (
            f"/office-practitioner-directory/{surface.value}"
            "/api/v1/application-auth/product/graphql"
        )
        expected_host = self._expected_host(surface)
        page = f"""<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Raisa active practitioners</title>
  <link rel="stylesheet" href="/office-practitioner-directory/taskpane.css">
</head>
<body>
  <main id="directory-root"
        data-surface="{html.escape(surface.value, quote=True)}"
        data-expected-host="{html.escape(expected_host, quote=True)}"
        data-directory-endpoint="{html.escape(endpoint, quote=True)}"
        data-csrf="{html.escape(csrf_value, quote=True)}"
        data-evidence-nonce="{html.escape(nonce, quote=True)}">
    <p class="eyebrow">Authored-synthetic · development only</p>
    <h1><strong>Raisa</strong><i aria-hidden="true"></i> medical office</h1>
    <p class="lede">Show the active practitioners your current application session is allowed to see.</p>
    <dl>
      <div><dt>Expected surface</dt><dd>{html.escape(surface.value)}</dd></div>
      <div><dt>Office host</dt><dd id="host-label">Waiting for Office</dd></div>
      <div><dt>Session</dt><dd id="session-label">Ready for one read</dd></div>
    </dl>
    <button id="load-directory" type="button" disabled>Show active practitioners</button>
    <p id="status" role="status" aria-live="polite">Confirming the Office host…</p>
    <ul id="practitioner-list" aria-label="Active practitioners" hidden></ul>
    <p class="boundary">No document, patient, clinical, provider or real identity data is used.</p>
  </main>
  <script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>
  <script src="/office-practitioner-directory/taskpane.js"></script>
</body>
</html>"""
        return page, session_value, csrf_value

    def record_result(
        self,
        submission: DirectoryResultSubmission,
    ) -> SanitizedDirectoryResult:
        if self.transport is None:
            raise HTTPException(status_code=503, detail="result_not_admitted")
        surface = Surface(submission.surface)
        if submission.host_class != self._expected_host(surface):
            raise HTTPException(status_code=400, detail="result_not_admitted")
        supplied_hash = self._hash(submission.evidence_nonce)
        with self._lock:
            launch = self._launches[surface]
            if not secrets.compare_digest(
                supplied_hash,
                launch.evidence_nonce_hash,
            ):
                raise HTTPException(status_code=400, detail="result_not_admitted")
            if surface in self._results:
                raise HTTPException(status_code=409, detail="result_already_recorded")

        if submission.terminal_status == "failed":
            try:
                self.transport.logout(
                    surface_session_value=launch.session_value,
                    correlation_id=(
                        "correlation-directory-failure-"
                        f"{surface.value.replace('_', '-')}"
                    ),
                )
            except RuntimeError as cleanup_error:
                # The failed terminal result remains fail-closed; the direct
                # post-logout validation below still proves whether authority
                # survived this best-effort cleanup attempt.
                _ = cleanup_error

        post_logout_denied = False
        try:
            self.transport.validate(
                surface_session_value=launch.session_value,
                surface=surface,
                origin=self.origin,
                correlation_id=(
                    "correlation-directory-residue-"
                    f"{surface.value.replace('_', '-')}"
                ),
            )
        except TransportAuthenticationFailed:
            post_logout_denied = True

        passed_shape = all(
            (
                submission.directory_read_passed,
                submission.exact_projection_passed,
                submission.active_practitioner_count == 2,
                submission.logout_passed,
                submission.result_submitted,
                post_logout_denied,
            )
        )
        if (submission.terminal_status == "passed") != passed_shape:
            raise HTTPException(status_code=400, detail="result_not_admitted")
        if (submission.failure_code == "none") != passed_shape:
            raise HTTPException(status_code=400, detail="result_not_admitted")
        result = SanitizedDirectoryResult(
            **submission.model_dump(exclude={"evidence_nonce"}),
            post_logout_session_denied=post_logout_denied,
        )
        with self._lock:
            self._results[surface] = result
        self._write_evidence(self.evidence())
        return result

    def _database_snapshot(self) -> dict[str, object]:
        if self.owner_engine is None:
            return {"passed": False, "readback_failed": True}
        with self.owner_engine.connect() as connection:
            allowed_audit_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM application_auth_audit_events "
                        "WHERE event_type = 'auth.authorization_allowed' "
                        "AND policy_version = "
                        "'practice-practitioner-directory-read.v1'"
                    )
                ).scalar_one()
            )
            revoked_surface_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM application_auth_surface_sessions "
                        "WHERE status = 'revoked'"
                    )
                ).scalar_one()
            )
            serialized = json.dumps(
                [
                    dict(row._mapping)
                    for row in connection.execute(
                        text(
                            "SELECT event_type, action, resource_type, "
                            "policy_version, decision, reason_codes, "
                            "session_reference_hash, correlation_id "
                            "FROM application_auth_audit_events ORDER BY id"
                        )
                    )
                ],
                default=str,
                sort_keys=True,
            )
        raw_match_count = sum(value in serialized for value in self._raw_values)
        return {
            "fresh_owner_readback": True,
            "authorization_allowed_audit_count": allowed_audit_count,
            "revoked_surface_session_count": revoked_surface_count,
            "raw_session_or_csrf_match_count": raw_match_count,
            "target_or_product_identifier_recorded": False,
            "passed": (
                allowed_audit_count == 2
                and revoked_surface_count == 2
                and raw_match_count == 0
            ),
        }

    @staticmethod
    def _probe_sqlstate(engine: Engine, statement: str) -> str | None:
        try:
            with engine.connect() as connection:
                connection.execute(text(statement)).first()
        except DBAPIError as exc:
            return getattr(exc.orig, "sqlstate", None) or getattr(
                exc.orig,
                "pgcode",
                None,
            )
        return None

    def _role_snapshot(self) -> dict[str, object]:
        if self.auth_engine is None or self.product_engine is None:
            return {"passed": False, "readback_failed": True}
        probes = {
            "auth_cannot_read_product": self._probe_sqlstate(
                self.auth_engine,
                "SELECT id FROM practitioners LIMIT 1",
            ),
            "product_cannot_read_auth": self._probe_sqlstate(
                self.product_engine,
                "SELECT session_reference_hash FROM application_auth_parent_sessions LIMIT 1",
            ),
            "product_cannot_read_provider": self._probe_sqlstate(
                self.product_engine,
                "SELECT provider_number FROM practitioners LIMIT 1",
            ),
            "product_cannot_write": self._probe_sqlstate(
                self.product_engine,
                "UPDATE practitioners SET is_active = false",
            ),
        }
        return {
            "four_direct_privilege_denials": len(probes) == 4,
            "all_denials_insufficient_privilege": set(probes.values()) == {"42501"},
            "role_names_recorded": False,
            "passed": len(probes) == 4 and set(probes.values()) == {"42501"},
        }

    def _compose_evidence(
        self,
        *,
        database: dict[str, object],
        role_probes: dict[str, object],
        cleanup: dict[str, object],
    ) -> dict[str, object]:
        with self._lock:
            results = {
                surface.value: (
                    self._results[surface].model_dump(mode="json")
                    if surface in self._results
                    else {"terminal_status": "pending"}
                )
                for surface in SURFACES
            }
        hosts_passed = all(
            result.get("terminal_status") == "passed"
            for result in results.values()
        )
        cleanup_passed = bool(cleanup.get("passed"))
        passed = all(
            (
                hosts_passed,
                bool(database.get("passed")),
                bool(role_probes.get("passed")),
                cleanup_passed,
            )
        )
        evidence: dict[str, object] = {
            "schema_version": "emr4.provider-free-office-practitioner-directory-consumer-evidence.v1",
            "result": RESULT if passed else IN_PROGRESS,
            "passed": passed,
            "evidence_label": (
                "route_intercepted_browser"
                if self.allow_local_browser_preview
                else "live_local_office_backend_postgres_product_read"
            ),
            "data_class": AUTHORED_SYNTHETIC_DATA_CLASS,
            "default_off": True,
            "development_origin_class": (
                "exact_reserved_https_development_origin"
                if self.origin == DEVELOPMENT_ORIGIN
                else "loopback_browser_preview_origin"
            ),
            "migration": dict(self.migration_evidence),
            "role_and_pool": dict(self.role_evidence),
            "results": results,
            "database": database,
            "role_probes": role_probes,
            "cleanup": cleanup,
            "side_effects": {
                "provider_calls": 0,
                "external_identity_calls": 0,
                "microsoft_or_office_identity_calls": 0,
                "product_reads": sum(
                    result.get("active_practitioner_count", 0) == 2
                    for result in results.values()
                ),
                "patient_health_or_clinical_reads": 0,
                "document_reads": 0,
                "document_writes": 0,
                "product_commands_or_writes": 0,
                "deployments": 0,
                "production_changes": 0,
            },
            "claim_limits": [
                "Two supervised authored-synthetic Office active-practitioner renders only.",
                "No real identity, patient or clinical data, document access, general product mount, deployment, production or release is established.",
            ],
        }
        serialized = json.dumps(evidence, default=str, sort_keys=True)
        prohibited = tuple(self._sensitive_targets) + tuple(self._raw_values)
        evidence["durable_secret_or_target_match_count"] = sum(
            value in serialized for value in prohibited if value
        )
        if evidence["durable_secret_or_target_match_count"]:
            evidence["result"] = "revision_required"
            evidence["passed"] = False
        return evidence

    def evidence(self) -> dict[str, object]:
        if self._final_evidence is not None:
            return json.loads(json.dumps(self._final_evidence))
        return self._compose_evidence(
            database=self._database_snapshot(),
            role_probes=self._role_snapshot(),
            cleanup=dict(self.cleanup_evidence),
        )

    def _write_evidence(self, evidence: dict[str, object]) -> None:
        if self._output_path is None:
            return
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _cleanup_resources(self) -> dict[str, object]:
        for launch in self._launches.values():
            if self.transport is not None:
                try:
                    self.transport.logout(
                        surface_session_value=launch.session_value,
                        correlation_id="correlation-office-directory-closeout",
                    )
                except RuntimeError as cleanup_error:
                    # Cleanup continues so the disposable database and roles
                    # are removed even when a session is already unavailable.
                    _ = cleanup_error
        for engine in (self.product_engine, self.auth_engine, self.owner_engine):
            if engine is not None:
                engine.dispose()
        self.cleanup_evidence["pools_disposed"] = True
        if self._maintenance is not None and self._database_created:
            self.cleanup_evidence["database_absent_after"] = _drop_database(
                self._maintenance,
                self._database_name,
            )
        elif self._maintenance is not None and self._database_name:
            self.cleanup_evidence["database_absent_after"] = not DATABASE_PATTERN.fullmatch(
                self._database_name
            ) or _drop_database(self._maintenance, self._database_name)
        else:
            self.cleanup_evidence["database_absent_after"] = True
        role_absence: list[bool] = []
        if self._maintenance is not None:
            for role_name, kind in reversed(self._created_roles):
                try:
                    role_absence.append(_drop_role(self._maintenance, role_name, kind=kind))
                except Exception:
                    role_absence.append(False)
            self._maintenance.dispose()
        self.cleanup_evidence["four_task_roles_absent_after"] = (
            len(role_absence) == len(self._created_roles) and all(role_absence)
        ) if self._created_roles else True
        self.cleanup_evidence["passed"] = all(
            (
                self.cleanup_evidence["database_absent_after"],
                self.cleanup_evidence["four_task_roles_absent_after"],
                self.cleanup_evidence["pools_disposed"],
            )
        )
        return dict(self.cleanup_evidence)

    def close(self) -> dict[str, object]:
        with self._close_lock:
            if self._final_evidence is not None:
                return json.loads(json.dumps(self._final_evidence))
            try:
                database = self._database_snapshot()
                role_probes = self._role_snapshot()
            except Exception:
                database = {"passed": False, "readback_failed": True}
                role_probes = {"passed": False, "readback_failed": True}
            cleanup = self._cleanup_resources()
            final = self._compose_evidence(
                database=database,
                role_probes=role_probes,
                cleanup=cleanup,
            )
            if final["result"] == IN_PROGRESS:
                final["result"] = RESULT if final["passed"] else "revision_required"
            self._final_evidence = final
            try:
                self._write_evidence(final)
            finally:
                self._raw_values.clear()
                self._sensitive_targets.clear()
            return json.loads(json.dumps(final))


def _set_task_cookie(response: Response, *, name: str, value: str) -> None:
    response.set_cookie(
        key=name,
        value=value,
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
        partitioned=True,
    )


def build_app(
    harness: OfficePractitionerDirectoryHarness | None = None,
) -> FastAPI:
    selected = harness or OfficePractitionerDirectoryHarness()
    if selected.transport is None or selected.guard is None or selected.bridge is None:
        raise HarnessSetupFailure("office_directory_runtime_unavailable")
    application = FastAPI(
        title="Raisa authored-synthetic Office practitioner directory",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    application.state.office_practitioner_directory = selected
    application.include_router(application_auth_router)
    application.dependency_overrides[get_application_auth_transport] = (
        lambda: selected.transport
    )
    application.dependency_overrides[get_application_auth_operational_hardening] = (
        lambda: selected.guard
    )
    for surface in SURFACES:
        surface_app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
        surface_app.include_router(
            create_application_session_practitioner_directory_router(
                bridge=selected.bridge,
                surface=surface,
            )
        )
        application.mount(
            f"/office-practitioner-directory/{surface.value}",
            surface_app,
        )

    def taskpane_response(surface: Surface, *, office_host_stub: bool) -> HTMLResponse:
        page, session_value, csrf_value = selected.deliver_taskpane(surface)
        if office_host_stub:
            page = page.replace(
                '<script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>',
                '<script src="/office-practitioner-directory/office-host-stub.js"></script>',
            )
        response = HTMLResponse(
            page,
            headers={**_NO_STORE_HEADERS, "Content-Security-Policy": _TASKPANE_CSP},
        )
        if session_value and csrf_value:
            _set_task_cookie(response, name=SESSION_COOKIE_NAME, value=session_value)
            _set_task_cookie(response, name=CSRF_COOKIE_NAME, value=csrf_value)
        return response

    @application.get(
        "/office-practitioner-directory/taskpane",
        response_class=HTMLResponse,
    )
    def taskpane(surface: Surface = Query(...)) -> HTMLResponse:
        if surface not in SURFACES:
            raise HTTPException(status_code=404, detail="surface_not_available")
        return taskpane_response(surface, office_host_stub=False)

    @application.get(
        "/office-practitioner-directory/browser-preview",
        response_class=HTMLResponse,
    )
    def browser_preview(surface: Surface = Query(...)) -> HTMLResponse:
        if surface not in SURFACES:
            raise HTTPException(status_code=404, detail="surface_not_available")
        return taskpane_response(surface, office_host_stub=True)

    @application.get("/office-practitioner-directory/taskpane.js")
    def taskpane_script() -> FileResponse:
        return FileResponse(
            TASKPANE_SCRIPT,
            media_type="text/javascript",
            headers=_NO_STORE_HEADERS,
        )

    @application.get("/office-practitioner-directory/taskpane.css")
    def taskpane_css() -> FileResponse:
        return FileResponse(
            TASKPANE_CSS,
            media_type="text/css",
            headers=_NO_STORE_HEADERS,
        )

    @application.get("/office-practitioner-directory/office-host-stub.js")
    def office_host_stub() -> FileResponse:
        return FileResponse(
            OFFICE_HOST_STUB,
            media_type="text/javascript",
            headers=_NO_STORE_HEADERS,
        )

    @application.get("/office-practitioner-directory/icon/{size}.png")
    def icon(size: str) -> FileResponse:
        if size not in {"16", "32", "64", "80"}:
            raise HTTPException(status_code=404, detail="icon_not_available")
        return FileResponse(
            ASSET_ROOT / f"icon-{size}.png",
            media_type="image/png",
            headers=_NO_STORE_HEADERS,
        )

    @application.post(
        "/office-practitioner-directory/result",
        response_model=SanitizedDirectoryResult,
        status_code=status.HTTP_201_CREATED,
    )
    def record_result(
        submission: DirectoryResultSubmission,
        origin: str | None = Header(default=None, alias="Origin"),
    ) -> SanitizedDirectoryResult:
        if origin != selected.origin:
            raise HTTPException(status_code=403, detail="result_not_admitted")
        return selected.record_result(submission)

    @application.get("/office-practitioner-directory/evidence")
    def evidence(request: Request) -> JSONResponse:
        forwarded = any(
            name in request.headers
            for name in ("x-forwarded-for", "x-forwarded-host", "x-forwarded-proto")
        )
        if (
            request.client is None
            or request.client.host not in {"127.0.0.1", "::1", "testclient"}
            or request.url.hostname not in {"127.0.0.1", "::1", "localhost"}
            or forwarded
        ):
            raise HTTPException(status_code=404, detail="evidence_not_available")
        return JSONResponse(selected.evidence(), headers=_NO_STORE_HEADERS)

    @application.post("/office-practitioner-directory/cleanup")
    def cleanup(request: Request) -> JSONResponse:
        forwarded = any(
            name in request.headers
            for name in ("x-forwarded-for", "x-forwarded-host", "x-forwarded-proto")
        )
        if (
            request.client is None
            or request.client.host not in {"127.0.0.1", "::1", "testclient"}
            or request.url.hostname not in {"127.0.0.1", "::1", "localhost"}
            or forwarded
        ):
            raise HTTPException(status_code=404, detail="cleanup_not_available")
        return JSONResponse(selected.close(), headers=_NO_STORE_HEADERS)

    return application


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    parser.add_argument("--local-browser-preview", action="store_true")
    args = parser.parse_args()
    harness = OfficePractitionerDirectoryHarness(
        origin=(
            LOCAL_BROWSER_PREVIEW_ORIGIN
            if args.local_browser_preview
            else DEVELOPMENT_ORIGIN
        ),
        output_path=args.output,
        allow_local_browser_preview=args.local_browser_preview,
    )
    try:
        uvicorn.run(
            build_app(harness),
            host=args.host,
            port=args.port,
            log_level="warning",
            # The application guard, not uvicorn, owns the exact one-hop
            # forwarded-client contract and must observe the direct relay peer.
            proxy_headers=False,
            ssl_keyfile=(
                str(Path.home() / ".office-addin-dev-certs" / "localhost.key")
                if args.local_browser_preview
                else None
            ),
            ssl_certfile=(
                str(Path.home() / ".office-addin-dev-certs" / "localhost.crt")
                if args.local_browser_preview
                else None
            ),
        )
    finally:
        final = harness.close()
        print(json.dumps(final, indent=2, sort_keys=True))
    return 0 if final["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEVELOPMENT_ORIGIN",
    "LOCAL_BROWSER_PREVIEW_ORIGIN",
    "DirectoryResultSubmission",
    "OfficePractitionerDirectoryHarness",
    "SanitizedDirectoryResult",
    "build_app",
]
