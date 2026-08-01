"""Real Office-host compatibility harness backed by disposable PostgreSQL.

The module composes the already accepted seven application-auth routes,
PostgreSQL coordinator, separate LOGIN role, exact capability-role pool and
operational denial audit.  It is task-scoped and mounts no product router.
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
import threading
from pathlib import Path
from typing import Any

import uvicorn
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
from app.services.application_auth_role_runtime import (  # noqa: E402
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (  # noqa: E402
    AUTHORED_SYNTHETIC_DATA_CLASS,
)
from app.services.application_auth_transport import (  # noqa: E402
    OneUseSyntheticBootstrapRegistry,
)
from scripts.raisa_shared_application_auth_office_cookie_compatibility import (  # noqa: E402
    DEVELOPMENT_ORIGIN,
    SURFACES,
    OfficeCookieCompatibilityHarnessBase,
    _SurfaceBoundApplicationAuthTransport,
    build_app,
)
from scripts.raisa_shared_application_auth_operational_hardening_acceptance import (  # noqa: E402
    _apply_login_contract,
    _drop_login_role,
)
from scripts.raisa_shared_application_auth_runtime_role_secure_transport_acceptance import (  # noqa: E402
    MIGRATION_HEAD,
    _apply_role_contract,
    _base_database_url,
    _create_database,
    _database_exists,
    _drop_database,
    _drop_role,
    _require_alembic,
    _role_exists,
)


EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "shared-application-auth-postgresql-office-host-compatibility"
    / "live-office-backend-postgres-evidence.json"
)
RESULT = "raisa_shared_application_auth_postgresql_office_host_compatibility_pass"
IN_PROGRESS = (
    "raisa_shared_application_auth_postgresql_office_host_compatibility_in_progress"
)
TABLE_NAMES = (
    "application_auth_principal_generations",
    "application_auth_parent_sessions",
    "application_auth_surface_sessions",
    "application_auth_exchange_grants",
    "application_auth_audit_events",
)
_HASH_PATTERN = r"^sha256:[0-9a-f]{64}$"


class HarnessSetupFailure(RuntimeError):
    """Bounded setup failure that contains no target or credential."""


class _RecordingOpaqueSource:
    def __init__(self, *, prefix: str = "") -> None:
        self._prefix = prefix
        self._values: list[str] = []
        self._lock = threading.Lock()

    def __call__(self, _kind: str | None = None) -> str:
        value = f"{self._prefix}{secrets.token_urlsafe(32)}"
        with self._lock:
            self._values.append(value)
        return value

    def values(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._values)


class DisposablePostgresOfficeInfrastructure:
    """Own one exact disposable database, LOGIN role and capability role."""

    def __init__(self) -> None:
        suffix = secrets.token_hex(6)
        self.database_name = f"emr4_auth_transport_acceptance_{suffix}"
        self.capability_role = f"emr4_application_auth_runtime_{suffix}"
        self.login_role = f"emr4_application_auth_login_{suffix}"
        self._password = secrets.token_hex(24)
        self._closed = False
        self._database_created = False
        self._capability_created = False
        self._login_created = False
        self.owner_engine: Engine | None = None
        self.bounded_engine: Engine | None = None
        self.session_factory = None
        self.migration_evidence: dict[str, object] = {}
        self.role_evidence: dict[str, object] = {}
        self.cleanup_evidence: dict[str, object] = {
            "database_drop_attempted": False,
            "login_role_drop_attempted": False,
            "capability_role_drop_attempted": False,
            "database_absent_after": False,
            "login_role_absent_after": False,
            "capability_role_absent_after": False,
            "passed": False,
        }

        base = _base_database_url()
        self._target = base.set(database=self.database_name)
        self._maintenance = create_engine(
            base.set(database="postgres"),
            isolation_level="AUTOCOMMIT",
            pool_pre_ping=True,
        )
        try:
            self._prepare()
        except Exception as exc:
            self.cleanup()
            if isinstance(exc, HarnessSetupFailure):
                raise
            raise HarnessSetupFailure("disposable_postgresql_setup_failed") from exc

    def _prepare(self) -> None:
        if _database_exists(self._maintenance, self.database_name):
            raise HarnessSetupFailure("disposable_database_preexisted")
        if _role_exists(self._maintenance, self.capability_role):
            raise HarnessSetupFailure("disposable_capability_role_preexisted")
        if _role_exists(self._maintenance, self.login_role):
            raise HarnessSetupFailure("disposable_login_role_preexisted")

        _create_database(self._maintenance, self.database_name)
        self._database_created = True
        _require_alembic(self._target, "upgrade", "head")
        current = _require_alembic(self._target, "current")
        drift = _require_alembic(self._target, "check")
        self.migration_evidence = {
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": (
                "No new upgrade operations detected" in drift
            ),
        }
        self.migration_evidence["passed"] = all(
            bool(value) for value in self.migration_evidence.values()
        )

        self.owner_engine = create_engine(self._target, pool_pre_ping=True)
        _apply_role_contract(self.owner_engine, self.capability_role)
        self._capability_created = True
        _apply_login_contract(
            self.owner_engine,
            login_role=self.login_role,
            capability_role=self.capability_role,
            password=self._password,
            connection_limit=2,
        )
        self._login_created = True

        login_target = self._target.set(
            username=self.login_role,
            password=self._password,
        )
        policy = ApplicationAuthPoolPolicy(
            pool_size=1,
            max_overflow=1,
            pool_timeout_seconds=0.5,
            pool_recycle_seconds=60,
            login_connection_limit=2,
        )
        self.bounded_engine = create_application_auth_engine(
            login_target.render_as_string(hide_password=False),
            login_role=self.login_role,
            capability_role=self.capability_role,
            policy=policy,
        )
        self.session_factory = create_application_auth_session_factory(
            self.bounded_engine
        )
        with self.bounded_engine.connect() as connection:
            identity = connection.execute(
                text("SELECT session_user, current_user")
            ).one()
        with self.owner_engine.connect() as connection:
            login_direct_select = bool(
                connection.execute(
                    text(
                        "SELECT has_table_privilege(:role, "
                        "'public.application_auth_audit_events', 'SELECT')"
                    ),
                    {"role": self.login_role},
                ).scalar_one()
            )
            role = connection.execute(
                text(
                    "SELECT rolinherit, rolsuper, rolbypassrls, rolconnlimit "
                    "FROM pg_roles WHERE rolname = :role"
                ),
                {"role": self.login_role},
            ).one()
        self.role_evidence = {
            "session_user_is_login": identity.session_user == self.login_role,
            "current_user_is_capability": (
                identity.current_user == self.capability_role
            ),
            "identities_separate": identity.session_user != identity.current_user,
            "login_noinherit": not role.rolinherit,
            "login_not_superuser": not role.rolsuper,
            "login_cannot_bypass_rls": not role.rolbypassrls,
            "login_connection_limit": role.rolconnlimit,
            "pool_maximum": policy.pool_size + policy.max_overflow,
            "login_direct_audit_select_grant": login_direct_select,
            "password_recorded": False,
            "role_names_recorded": False,
        }
        self.role_evidence["passed"] = all(
            (
                self.role_evidence["session_user_is_login"],
                self.role_evidence["current_user_is_capability"],
                self.role_evidence["identities_separate"],
                self.role_evidence["login_noinherit"],
                self.role_evidence["login_not_superuser"],
                self.role_evidence["login_cannot_bypass_rls"],
                self.role_evidence["login_connection_limit"] == 2,
                self.role_evidence["pool_maximum"] == 2,
                not self.role_evidence["login_direct_audit_select_grant"],
                not self.role_evidence["password_recorded"],
                not self.role_evidence["role_names_recorded"],
            )
        )
        if not (
            self.migration_evidence["passed"] and self.role_evidence["passed"]
        ):
            raise HarnessSetupFailure("database_or_role_contract_failed")

    def sensitive_targets(self) -> tuple[str, ...]:
        return (
            self.database_name,
            self.capability_role,
            self.login_role,
            self._password,
        )

    def cleanup(self) -> dict[str, object]:
        if self._closed:
            return dict(self.cleanup_evidence)
        self._closed = True
        if self.bounded_engine is not None:
            self.bounded_engine.dispose()
        if self.owner_engine is not None:
            self.owner_engine.dispose()

        if self._login_created:
            self.cleanup_evidence["login_role_drop_attempted"] = True
            self.cleanup_evidence["login_role_absent_after"] = _drop_login_role(
                self._maintenance,
                self.login_role,
            )
        else:
            self.cleanup_evidence["login_role_absent_after"] = not _role_exists(
                self._maintenance,
                self.login_role,
            )

        if self._database_created:
            self.cleanup_evidence["database_drop_attempted"] = True
            self.cleanup_evidence["database_absent_after"] = _drop_database(
                self._maintenance,
                self.database_name,
            )
        else:
            self.cleanup_evidence["database_absent_after"] = not _database_exists(
                self._maintenance,
                self.database_name,
            )

        if self._capability_created:
            self.cleanup_evidence["capability_role_drop_attempted"] = True
            self.cleanup_evidence["capability_role_absent_after"] = _drop_role(
                self._maintenance,
                self.capability_role,
            )
        else:
            self.cleanup_evidence["capability_role_absent_after"] = not _role_exists(
                self._maintenance,
                self.capability_role,
            )
        self._maintenance.dispose()
        self.cleanup_evidence["passed"] = all(
            (
                self.cleanup_evidence["database_absent_after"],
                self.cleanup_evidence["login_role_absent_after"],
                self.cleanup_evidence["capability_role_absent_after"],
            )
        )
        return dict(self.cleanup_evidence)

    def forget_password(self) -> None:
        self._password = ""


class PostgresOfficeCookieCompatibilityHarness(OfficeCookieCompatibilityHarnessBase):
    """The prior real-Office harness with accepted PostgreSQL dependencies."""

    def __init__(
        self,
        *,
        origin: str = DEVELOPMENT_ORIGIN,
        output_path: Path | None = EVIDENCE_PATH,
    ) -> None:
        self._close_lock = threading.Lock()
        self._closed = False
        self._final_evidence: dict[str, object] | None = None
        self._output_path = output_path
        self._raw_launch_values: list[str] = []
        self._token_source = _RecordingOpaqueSource()
        self._csrf_source = _RecordingOpaqueSource(prefix="csrf.")
        super().__init__(
            origin=origin,
            principal_namespace="office-postgres",
            launch_value_sink=self._raw_launch_values.append,
        )
        try:
            self.infrastructure = DisposablePostgresOfficeInfrastructure()
        except Exception:
            self._raw_launch_values.clear()
            raise
        credentials, bootstrap_surfaces, origins = self._take_initial_auth_material()

        if self.infrastructure.session_factory is None:
            self.infrastructure.cleanup()
            self._raw_launch_values.clear()
            raise HarnessSetupFailure("database_session_factory_unavailable")
        runtime = RoleScopedPostgresApplicationAuthRuntime(
            session_factory=self.infrastructure.session_factory,
            surface_origins=origins,
            token_source=self._token_source,
        )
        self.bootstrap_registry = OneUseSyntheticBootstrapRegistry(credentials)
        self.transport = _SurfaceBoundApplicationAuthTransport(
            runtime=runtime,
            bootstrap_registry=self.bootstrap_registry,
            surface_origins=origins,
            bootstrap_surfaces=bootstrap_surfaces,
            csrf_token_source=self._csrf_source,
        )
        denial_sink = PostgresTransportDenialAuditSink(
            self.infrastructure.session_factory
        )
        self.guard = ApplicationAuthOperationalHardening(
            proxy_policy=ProxyTrustPolicy.from_cidrs(
                ["127.0.0.0/8", "::1/128"]
            ),
            rate_limiter=BoundedFixedWindowRateLimiter(
                requests_per_window=64,
                window_seconds=300,
                max_keys=64,
            ),
            denial_audit_sink=denial_sink,
            client_hmac_key=secrets.token_bytes(32),
        )

    def _raw_values(self) -> tuple[str, ...]:
        return tuple(self._raw_launch_values) + self._token_source.values() + (
            self._csrf_source.values()
        )

    def _database_snapshot(self) -> dict[str, object]:
        owner = self.infrastructure.owner_engine
        bounded = self.infrastructure.bounded_engine
        if owner is None or bounded is None:
            raise HarnessSetupFailure("database_readback_unavailable")
        with owner.connect() as connection:
            counts = {
                table: int(
                    connection.execute(
                        text(f'SELECT count(*) FROM public."{table}"')
                    ).scalar_one()
                )
                for table in TABLE_NAMES
            }
            lifecycle_audit_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM application_auth_audit_events "
                        "WHERE practice_ref <> 'synthetic-transport-audit'"
                    )
                ).scalar_one()
            )
            denial_audit_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM application_auth_audit_events "
                        "WHERE practice_ref = 'synthetic-transport-audit' "
                        "AND event_type = 'auth.authorization_denied'"
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
            non_hash_reference_count = int(
                connection.execute(
                    text(
                        "SELECT "
                        "(SELECT count(*) FROM application_auth_parent_sessions "
                        " WHERE session_reference_hash !~ :pattern) + "
                        "(SELECT count(*) FROM application_auth_surface_sessions "
                        " WHERE surface_reference_hash !~ :pattern "
                        " OR parent_session_reference_hash !~ :pattern) + "
                        "(SELECT count(*) FROM application_auth_exchange_grants "
                        " WHERE grant_reference_hash !~ :pattern "
                        " OR parent_session_reference_hash !~ :pattern)"
                    ),
                    {"pattern": _HASH_PATTERN},
                ).scalar_one()
            )
            practices = tuple(
                row.practice_ref
                for row in connection.execute(
                    text(
                        "SELECT practice_ref "
                        "FROM application_auth_principal_generations "
                        "ORDER BY practice_ref"
                    )
                )
            )
            database_rows: list[dict[str, Any]] = []
            for table in TABLE_NAMES:
                database_rows.extend(
                    dict(row._mapping)
                    for row in connection.execute(
                        text(f'SELECT * FROM public."{table}"')
                    )
                )

        scope_shapes: list[dict[str, int]] = []
        for practice in practices:
            with bounded.connect() as connection:
                with connection.begin():
                    connection.execute(
                        text(
                            "SELECT set_config('app.current_practice_ref', "
                            ":practice_ref, true)"
                        ),
                        {"practice_ref": practice},
                    )
                    scope_shapes.append(
                        {
                            "principal_generations": int(
                                connection.execute(
                                    text(
                                        "SELECT count(*) FROM "
                                        "application_auth_principal_generations"
                                    )
                                ).scalar_one()
                            ),
                            "parent_sessions": int(
                                connection.execute(
                                    text(
                                        "SELECT count(*) FROM "
                                        "application_auth_parent_sessions"
                                    )
                                ).scalar_one()
                            ),
                            "surface_sessions": int(
                                connection.execute(
                                    text(
                                        "SELECT count(*) FROM "
                                        "application_auth_surface_sessions"
                                    )
                                ).scalar_one()
                            ),
                            "exchange_grants": int(
                                connection.execute(
                                    text(
                                        "SELECT count(*) FROM "
                                        "application_auth_exchange_grants"
                                    )
                                ).scalar_one()
                            ),
                            "audit_events": int(
                                connection.execute(
                                    text(
                                        "SELECT count(*) FROM "
                                        "application_auth_audit_events"
                                    )
                                ).scalar_one()
                            ),
                        }
                    )

        serialized_rows = json.dumps(database_rows, default=str, sort_keys=True)
        raw_match_count = sum(
            value in serialized_rows for value in self._raw_values() if value
        )
        exact_counts = {
            "principal_generations": counts[
                "application_auth_principal_generations"
            ],
            "parent_sessions": counts["application_auth_parent_sessions"],
            "surface_sessions": counts["application_auth_surface_sessions"],
            "exchange_grants": counts["application_auth_exchange_grants"],
            "audit_events": counts["application_auth_audit_events"],
        }
        expected_scope = {
            "principal_generations": 1,
            "parent_sessions": 1,
            "surface_sessions": 2,
            "exchange_grants": 0,
            "audit_events": 7,
        }
        result: dict[str, object] = {
            "fresh_session_readback": True,
            "migration": dict(self.infrastructure.migration_evidence),
            "role_and_pool": dict(self.infrastructure.role_evidence),
            "row_counts": exact_counts,
            "lifecycle_audit_event_count": lifecycle_audit_count,
            "retained_post_logout_denial_count": denial_audit_count,
            "revoked_surface_session_count": revoked_surface_count,
            "practice_count": len(practices),
            "practice_scope_shapes": scope_shapes,
            "practice_scope_exact": (
                len(scope_shapes) == 2
                and all(shape == expected_scope for shape in scope_shapes)
            ),
            "opaque_reference_shape_violations": non_hash_reference_count,
            "raw_persisted_value_match_count": raw_match_count,
            "target_names_or_password_recorded": False,
        }
        result["passed"] = all(
            (
                result["migration"]["passed"],  # type: ignore[index]
                result["role_and_pool"]["passed"],  # type: ignore[index]
                exact_counts
                == {
                    "principal_generations": 2,
                    "parent_sessions": 2,
                    "surface_sessions": 4,
                    "exchange_grants": 0,
                    "audit_events": 16,
                },
                lifecycle_audit_count == 14,
                denial_audit_count == 2,
                revoked_surface_count == 4,
                result["practice_scope_exact"],
                non_hash_reference_count == 0,
                raw_match_count == 0,
                not result["target_names_or_password_recorded"],
            )
        )
        return result

    def _compose_evidence(
        self,
        *,
        database: dict[str, object],
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
        registry = self.bootstrap_registry.state_counts()
        hosts_passed = all(
            result.get("terminal_status") == "passed"
            for result in results.values()
        )
        cleanup_passed = bool(cleanup.get("passed"))
        passed = hosts_passed and bool(database.get("passed")) and cleanup_passed
        evidence: dict[str, object] = {
            "schema_version": (
                "emr4.postgresql_office_host_compatibility_evidence.v1"
            ),
            "result": RESULT if passed else IN_PROGRESS,
            "passed": passed,
            "evidence_label": (
                "live_local_office_backend_postgres_capability_role"
            ),
            "data_class": AUTHORED_SYNTHETIC_DATA_CLASS,
            "runtime_class": (
                "provider_free_disposable_postgresql_exact_capability_role"
            ),
            "development_origin_class": "exact_reserved_https_development_origin",
            "results": results,
            "bootstrap_registry_counts": registry,
            "database": database,
            "cleanup": cleanup,
            "side_effects": {
                "provider_calls": 0,
                "external_identity_calls": 0,
                "microsoft_or_office_identity_calls": 0,
                "product_or_source_database_reads": 0,
                "patient_health_or_clinical_reads": 0,
                "document_reads": 0,
                "document_writes": 0,
                "product_commands": 0,
                "cloud_or_iam_mutations": 0,
                "deployments": 0,
                "production_changes": 0,
            },
            "claim_limits": [
                "One installed Word and one Word Online authored-synthetic lifecycle only.",
                "No real identity, Microsoft federation, product data, deployment, production or release is established.",
                "The rate limiter is process-local and proves no distributed abuse resistance.",
            ],
        }
        serialized = json.dumps(evidence, default=str, sort_keys=True)
        prohibited = self.infrastructure.sensitive_targets() + self._raw_values()
        evidence["durable_secret_or_target_match_count"] = sum(
            value in serialized for value in prohibited if value
        )
        if evidence["durable_secret_or_target_match_count"]:
            evidence["result"] = "revision_required"
            evidence["passed"] = False
        return evidence

    def _write_evidence(self, evidence: dict[str, object]) -> None:
        if self._output_path is None:
            return
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def record_result(self, submission):  # type: ignore[no-untyped-def]
        result = super().record_result(submission)
        evidence = self.evidence()
        self._write_evidence(evidence)
        return result

    def evidence(self) -> dict[str, object]:
        if self._final_evidence is not None:
            return json.loads(json.dumps(self._final_evidence))
        database = self._database_snapshot()
        return self._compose_evidence(
            database=database,
            cleanup=dict(self.infrastructure.cleanup_evidence),
        )

    def close(self) -> dict[str, object]:
        with self._close_lock:
            if self._final_evidence is not None:
                return json.loads(json.dumps(self._final_evidence))
            try:
                database = self._database_snapshot()
            except Exception:
                database = {"passed": False, "readback_failed": True}
            cleanup = self.infrastructure.cleanup()
            final = self._compose_evidence(database=database, cleanup=cleanup)
            if final["result"] == IN_PROGRESS:
                final["result"] = (
                    RESULT if final["passed"] else "revision_required"
                )
            self._closed = True
            self._final_evidence = final
            try:
                self._write_evidence(final)
            finally:
                self._raw_launch_values.clear()
                self.infrastructure.forget_password()
            return json.loads(json.dumps(final))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the task-owned PostgreSQL-backed Office cookie compatibility "
            "harness."
        )
    )
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be in 1024..65535")
    harness = PostgresOfficeCookieCompatibilityHarness(output_path=args.output)
    application = build_app(harness)
    application.title = "Raisa PostgreSQL Office cookie compatibility"
    try:
        uvicorn.run(
            application,
            host="127.0.0.1",
            port=args.port,
            proxy_headers=False,
            access_log=False,
            log_level="warning",
        )
    finally:
        harness.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DisposablePostgresOfficeInfrastructure",
    "EVIDENCE_PATH",
    "PostgresOfficeCookieCompatibilityHarness",
    "RESULT",
]
