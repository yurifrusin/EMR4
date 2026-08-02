"""Disposable live-local PostgreSQL proof for the OIDC operational boundary."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from cryptography.fernet import Fernet
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import DBAPIError, TimeoutError as SQLAlchemyTimeoutError
from sqlalchemy.pool import NullPool


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_identity_oidc_adapter import (  # noqa: E402
    ATTEMPT_TTL_SECONDS,
    ReturnTarget,
    Surface,
)
from app.services.application_identity_oidc_attempt_database_role import (  # noqa: E402
    ATTEMPT_TABLE,
    create_oidc_attempt_deployment_login_statements,
    create_oidc_attempt_runtime_role_statements,
    drop_oidc_attempt_login_role_statement,
    drop_oidc_attempt_runtime_role_statement,
)
from app.services.application_identity_oidc_attempt_operational import (  # noqa: E402
    AuthorizationAttemptKeyReference,
    AuthorizationAttemptRuntimeKeyConfiguration,
    AuthorizationAttemptSecretReference,
    OIDCAttemptOperationalConfiguration,
    OIDCAttemptPoolPolicy,
    build_postgres_authorization_attempt_runtime,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-postgresql-oidc-operational-connection-boundary"
    / "live-local-backend-postgres-operational-evidence.json"
)
RESULT = "postgresql_oidc_operational_connection_boundary_pass"
DATABASE_PATTERN = re.compile(r"^emr4_oidc_operational_acceptance_[0-9a-f]{12}$")
CAPABILITY_PATTERN = re.compile(r"^emr4_oidc_attempt_runtime_[0-9a-f]{12}$")
LOGIN_PATTERN = re.compile(r"^emr4_oidc_attempt_login_[0-9a-f]{12}$")
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
MIGRATION_HEAD = "r7s8t9u0v1w2"
FIXED_NOW = datetime(2026, 8, 2, 7, 0, tzinfo=timezone.utc)
ORIGIN = "https://word-online-operational.synthetic.invalid"
REDIRECT_URI = (
    "https://oidc-operational.synthetic.invalid"
    "/api/v1/application-auth/federation/microsoft/callback"
)


class AcceptanceFailure(RuntimeError):
    pass


class _SyntheticSecretProvider:
    def __init__(self, namespace: str, values: dict[str, bytes]) -> None:
        self._namespace = namespace
        self._values = dict(values)
        self.calls: list[str] = []

    @property
    def provider_namespace(self) -> str:
        return self._namespace

    def resolve_bytes(self, reference: AuthorizationAttemptSecretReference) -> bytes:
        self.calls.append(reference.reference)
        value = self._values.get(reference.reference)
        if value is None:
            raise LookupError("synthetic secret unavailable")
        return value


def _base_database_url() -> URL:
    target = make_url(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
    if target.get_backend_name() != "postgresql":
        raise AcceptanceFailure("postgresql_required")
    if target.host not in {"127.0.0.1", "localhost"} or target.port != 5434:
        raise AcceptanceFailure("exact_loopback_database_required")
    if target.database in {None, "", "postgres"}:
        raise AcceptanceFailure("bounded_source_database_required")
    return target


def _database_exists(maintenance: Engine, name: str) -> bool:
    with maintenance.connect() as connection:
        return bool(
            connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": name},
            ).scalar_one_or_none()
        )


def _create_database(maintenance: Engine, name: str) -> None:
    if not DATABASE_PATTERN.fullmatch(name) or _database_exists(maintenance, name):
        raise AcceptanceFailure("unsafe_or_preexisting_database")
    with maintenance.connect() as connection:
        quoted = connection.dialect.identifier_preparer.quote(name)
        connection.execute(text(f"CREATE DATABASE {quoted}"))


def _drop_database(maintenance: Engine, name: str) -> bool:
    if not DATABASE_PATTERN.fullmatch(name):
        raise AcceptanceFailure("unsafe_database_cleanup_name")
    with maintenance.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :name AND pid <> pg_backend_pid()"
            ),
            {"name": name},
        )
        if _database_exists(maintenance, name):
            quoted = connection.dialect.identifier_preparer.quote(name)
            connection.execute(text(f"DROP DATABASE {quoted}"))
    return not _database_exists(maintenance, name)


def _role_absent(maintenance: Engine, name: str) -> bool:
    with maintenance.connect() as connection:
        return (
            connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
                {"name": name},
            ).scalar_one_or_none()
            is None
        )


def _drop_role(maintenance: Engine, name: str, *, login: bool) -> bool:
    pattern = LOGIN_PATTERN if login else CAPABILITY_PATTERN
    if not pattern.fullmatch(name):
        raise AcceptanceFailure("unsafe_role_cleanup_name")
    with maintenance.begin() as connection:
        present = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
            {"name": name},
        ).scalar_one_or_none()
        if present is not None:
            statement = (
                drop_oidc_attempt_login_role_statement(name)
                if login
                else drop_oidc_attempt_runtime_role_statement(name)
            )
            connection.execute(text(statement))
    return _role_absent(maintenance, name)


def _run_alembic(target: URL, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = target.render_as_string(hide_password=False)
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        shell=False,
    )


def _require_alembic(target: URL, *arguments: str) -> str:
    completed = _run_alembic(target, *arguments)
    if completed.returncode:
        raise AcceptanceFailure(f"alembic_{arguments[0]}_failed")
    return completed.stdout + completed.stderr


def _references() -> dict[str, str]:
    return {
        "enc_v1": "projects/synthetic/secrets/oidc-enc-v1/versions/1",
        "enc_v2": "projects/synthetic/secrets/oidc-enc-v2/versions/1",
        "dig_v1": "projects/synthetic/secrets/oidc-dig-v1/versions/1",
        "dig_v2": "projects/synthetic/secrets/oidc-dig-v2/versions/1",
    }


def _materials() -> dict[str, bytes]:
    return {
        "enc_v1": Fernet.generate_key(),
        "enc_v2": Fernet.generate_key(),
        "dig_v1": secrets.token_bytes(32),
        "dig_v2": secrets.token_bytes(32),
    }


def _key_configuration(
    references: dict[str, str],
    *,
    rotated: bool,
) -> AuthorizationAttemptRuntimeKeyConfiguration:
    namespace = "syntheticvault"
    cipher_ids = ("enc_v1", "enc_v2") if rotated else ("enc_v1",)
    digest_ids = ("dig_v1", "dig_v2") if rotated else ("dig_v1",)
    return AuthorizationAttemptRuntimeKeyConfiguration(
        provider_namespace=namespace,
        active_cipher_key_id="enc_v2" if rotated else "enc_v1",
        cipher_keys=tuple(
            AuthorizationAttemptKeyReference(
                key_id=key_id,
                secret=AuthorizationAttemptSecretReference(
                    provider_namespace=namespace,
                    reference=references[key_id],
                ),
            )
            for key_id in cipher_ids
        ),
        active_digest_key_id="dig_v2" if rotated else "dig_v1",
        digest_keys=tuple(
            AuthorizationAttemptKeyReference(
                key_id=key_id,
                secret=AuthorizationAttemptSecretReference(
                    provider_namespace=namespace,
                    reference=references[key_id],
                ),
            )
            for key_id in digest_ids
        ),
    )


def _operational_configuration(
    *,
    login_role: str,
    capability_role: str,
    references: dict[str, str],
    rotated: bool,
) -> OIDCAttemptOperationalConfiguration:
    return OIDCAttemptOperationalConfiguration(
        login_role=login_role,
        capability_role=capability_role,
        pool=OIDCAttemptPoolPolicy(
            pool_size=1,
            max_overflow=0,
            pool_timeout_seconds=0.25,
            pool_recycle_seconds=60,
            login_connection_limit=1,
        ),
        keys=_key_configuration(references, rotated=rotated),
    )


def _flow(counter: int) -> dict[str, Any]:
    state = f"state-{counter:032d}"
    nonce = f"nonce-{counter:032d}"
    verifier = f"verifier-{counter:035d}"
    query = urlencode(
        {
            "client_id": "22222222-2222-4222-8222-222222222222",
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": "openid profile",
            "state": state,
            "nonce": nonce,
            "response_mode": "form_post",
            "code_challenge": "A" * 43,
            "code_challenge_method": "S256",
        }
    )
    return {
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "scope": ["openid", "profile"],
        "auth_uri": (
            "https://login.microsoftonline.com/"
            "11111111-1111-4111-8111-111111111111/oauth2/v2.0/authorize?"
            f"{query}"
        ),
        "code_verifier": verifier,
        "nonce": nonce,
        "claims_challenge": None,
    }


def _role_contract(
    owner: Engine,
    maintenance: Engine,
    *,
    login_role: str,
    capability_role: str,
) -> dict[str, Any]:
    with maintenance.connect() as connection:
        login = connection.execute(
            text(
                "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
                "rolinherit, rolreplication, rolbypassrls, rolconnlimit "
                "FROM pg_roles WHERE rolname = :name"
            ),
            {"name": login_role},
        ).one()
        capability = connection.execute(
            text(
                "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
                "rolinherit, rolreplication, rolbypassrls "
                "FROM pg_roles WHERE rolname = :name"
            ),
            {"name": capability_role},
        ).one()
        membership = connection.execute(
            text(
                "SELECT 1 FROM pg_auth_members memberships "
                "JOIN pg_roles granted_role ON granted_role.oid = memberships.roleid "
                "JOIN pg_roles member_role ON member_role.oid = memberships.member "
                "WHERE granted_role.rolname = :capability "
                "AND member_role.rolname = :login"
            ),
            {"capability": capability_role, "login": login_role},
        ).scalar_one_or_none()
    with owner.connect() as connection:
        direct_grants = connection.execute(
            text(
                "SELECT privilege_type FROM information_schema.role_table_grants "
                "WHERE grantee = :login"
            ),
            {"login": login_role},
        ).scalars().all()
    result = {
        "login_attributes_exact": tuple(login)
        == (True, False, False, False, False, False, False, 1),
        "capability_non_login_non_bypass": tuple(capability)
        == (False, False, False, False, False, False, False),
        "membership_exact": membership == 1,
        "login_direct_table_grants": sorted(direct_grants),
    }
    result["passed"] = all(
        (
            result["login_attributes_exact"],
            result["capability_non_login_non_bypass"],
            result["membership_exact"],
            result["login_direct_table_grants"] == [],
        )
    )
    return result


def _direct_login_denial(login_target: URL) -> dict[str, Any]:
    engine = create_engine(login_target, poolclass=NullPool, pool_pre_ping=True)
    sqlstate: str | None = None
    try:
        with engine.connect() as connection:
            connection.execute(text(f'SELECT count(*) FROM public."{ATTEMPT_TABLE}"'))
    except DBAPIError as exc:
        sqlstate = getattr(exc.orig, "pgcode", None)
    finally:
        engine.dispose()
    return {"select_sqlstate": sqlstate, "passed": sqlstate == "42501"}


def _pool_and_runtime(
    login_target: URL,
    *,
    login_role: str,
    capability_role: str,
    references: dict[str, str],
    materials: dict[str, bytes],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    provider_values = {
        references[key_id]: material for key_id, material in materials.items()
    }
    provider = _SyntheticSecretProvider("syntheticvault", provider_values)
    initial = build_postgres_authorization_attempt_runtime(
        login_target,
        configuration=_operational_configuration(
            login_role=login_role,
            capability_role=capability_role,
            references=references,
            rotated=False,
        ),
        secret_provider=provider,
    )
    checkin_identities: list[tuple[str, str]] = []

    @event.listens_for(initial.engine, "checkin")
    def _observe_checkin(dbapi_connection, _record) -> None:
        if dbapi_connection is None:
            return
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT session_user, current_user")
            checkin_identities.append(tuple(cursor.fetchone()))
        finally:
            cursor.close()
            dbapi_connection.rollback()

    with initial.engine.connect() as connection:
        first = connection.execute(
            text(
                "SELECT session_user, current_user, pg_backend_pid(), "
                "current_setting('row_security'), "
                "current_setting('statement_timeout'), "
                "current_setting('lock_timeout'), "
                "current_setting('idle_in_transaction_session_timeout')"
            )
        ).one()
        connection.execute(text("RESET ROLE"))
        connection.execute(text("SET statement_timeout = 0"))
        connection.commit()

    with initial.engine.connect() as connection:
        restored = connection.execute(
            text(
                "SELECT session_user, current_user, pg_backend_pid(), "
                "current_setting('row_security'), "
                "current_setting('statement_timeout'), "
                "current_setting('lock_timeout'), "
                "current_setting('idle_in_transaction_session_timeout')"
            )
        ).one()

    held = initial.engine.connect()
    overflow_connection = None
    started = time.monotonic()
    checkout_timed_out = False
    try:
        overflow_connection = initial.engine.connect()
    except SQLAlchemyTimeoutError:
        checkout_timed_out = True
    finally:
        elapsed_ms = round((time.monotonic() - started) * 1000)
        if overflow_connection is not None:
            overflow_connection.close()
        held.close()

    first_flow = _flow(801)
    initial.store.store(
        flow=first_flow,
        surface=Surface.WORD_ONLINE,
        origin=ORIGIN,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=FIXED_NOW,
        ttl_seconds=ATTEMPT_TTL_SECONDS,
    )
    initial.dispose()

    rotated = build_postgres_authorization_attempt_runtime(
        login_target,
        configuration=_operational_configuration(
            login_role=login_role,
            capability_role=capability_role,
            references=references,
            rotated=True,
        ),
        secret_provider=provider,
    )
    consumed = rotated.store.consume(state=first_flow["state"], now=FIXED_NOW)
    active_flow = _flow(802)
    rotated.store.store(
        flow=active_flow,
        surface=Surface.WORD_ONLINE,
        origin=ORIGIN,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=FIXED_NOW,
        ttl_seconds=ATTEMPT_TTL_SECONDS,
    )
    rotated.dispose()

    identities_exact = (
        first[0] == login_role
        and first[1] == capability_role
        and restored[0] == login_role
        and restored[1] == capability_role
    )
    settings_exact = tuple(first[3:]) == ("on", "5s", "2s", "5s") and tuple(
        restored[3:]
    ) == ("on", "5s", "2s", "5s")
    result = {
        "session_and_effective_roles_exact": identities_exact,
        "physical_connection_reused": first[2] == restored[2],
        "settings_restored_after_committed_contamination": settings_exact,
        "checkin_reset_observed": bool(checkin_identities)
        and all(identity == (login_role, login_role) for identity in checkin_identities),
        "pool_size": 1,
        "max_overflow": 0,
        "login_connection_limit": 1,
        "checkout_timeout_configured_ms": 250,
        "checkout_timeout_observed": checkout_timed_out,
        "checkout_timeout_elapsed_ms": elapsed_ms,
        "checkout_timeout_within_bound": 200 <= elapsed_ms < 1500,
        "key_provider_resolution_count": len(provider.calls),
        "unique_secret_reference_count": len(set(provider.calls)),
        "key_resolution_sequence_exact": len(provider.calls) == 6
        and len(set(provider.calls)) == 4,
        "fresh_runtime_consumed_retained_keys": consumed.flow == first_flow,
        "active_rotated_attempt_persisted": True,
    }
    result["passed"] = all(
        (
            result["session_and_effective_roles_exact"],
            result["physical_connection_reused"],
            result["settings_restored_after_committed_contamination"],
            result["checkin_reset_observed"],
            result["checkout_timeout_observed"],
            result["checkout_timeout_within_bound"],
            result["key_resolution_sequence_exact"],
            result["fresh_runtime_consumed_retained_keys"],
        )
    )
    raw_values = (
        first_flow["state"],
        first_flow["nonce"],
        first_flow["code_verifier"],
        first_flow["auth_uri"],
        active_flow["state"],
        active_flow["nonce"],
        active_flow["code_verifier"],
        active_flow["auth_uri"],
        *references.values(),
        *(material.hex() for material in materials.values()),
        *(material.decode("ascii", errors="ignore") for material in materials.values()),
    )
    return result, raw_values


def _raw_database_scan(owner: Engine, raw_values: tuple[str, ...]) -> dict[str, Any]:
    with owner.connect() as connection:
        rows = connection.execute(
            text(
                f'SELECT state_reference_hmac, nonce_reference_hmac, cipher_key_id, '
                f"encode(ciphertext, 'escape'), envelope_version, data_class "
                f'FROM public."{ATTEMPT_TABLE}"'
            )
        ).all()
    serialized = json.dumps([tuple(row) for row in rows], default=str)
    matches = sum(bool(value) and value in serialized for value in raw_values)
    return {
        "active_encrypted_row_present": len(rows) == 1,
        "scanned_sensitive_value_count": len(raw_values),
        "matched_sensitive_value_count": matches,
        "matched_values_recorded": False,
        "passed": len(rows) == 1 and matches == 0,
    }


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_oidc_operational_acceptance_{suffix}"
    capability_role = f"emr4_oidc_attempt_runtime_{suffix}"
    login_role = f"emr4_oidc_attempt_login_{suffix}"
    password = secrets.token_urlsafe(36)
    references = _references()
    materials = _materials()
    base = _base_database_url()
    target = base.set(database=database_name)
    login_target = target.set(username=login_role, password=password)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    database_created = False
    capability_created = False
    login_created = False
    failure_type: str | None = None
    evidence: dict[str, Any] = {
        "schema_version": "emr4.postgresql-oidc-operational-connection-boundary-evidence.v1",
        "result": "revision_required",
        "evidence_label": "live_local_backend_postgres",
        "data_class": "authored_synthetic",
        "database": {
            "loopback_only": True,
            "name_recorded": False,
            "unique_allowlisted_name_used": bool(DATABASE_PATTERN.fullmatch(database_name)),
            "preexisting": False,
        },
        "cleanup": {
            "database_drop_attempted": False,
            "database_absent_after": False,
            "login_role_drop_attempted": False,
            "login_role_absent_after": False,
            "capability_role_drop_attempted": False,
            "capability_role_absent_after": False,
            "role_names_recorded": False,
        },
    }
    stage = "preflight"
    try:
        if not all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                CAPABILITY_PATTERN.fullmatch(capability_role),
                LOGIN_PATTERN.fullmatch(login_role),
            )
        ):
            raise AcceptanceFailure("generated_identifier_invalid")
        _create_database(maintenance, database_name)
        database_created = True
        stage = "migration"
        upgrade = _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        owner = create_engine(target, pool_pre_ping=True)
        stage = "roles"
        with owner.begin() as connection:
            for statement in create_oidc_attempt_runtime_role_statements(
                capability_role
            ):
                connection.execute(text(statement))
            capability_created = True
            for statement in create_oidc_attempt_deployment_login_statements(
                login_role,
                capability_role,
                connection_limit=1,
            ):
                connection.execute(text(statement))
            login_created = True
            connection.execute(text(f'ALTER ROLE "{login_role}" PASSWORD \'{password}\''))

        role_contract = _role_contract(
            owner,
            maintenance,
            login_role=login_role,
            capability_role=capability_role,
        )
        direct_denial = _direct_login_denial(login_target)
        stage = "pool_runtime"
        operational, raw_values = _pool_and_runtime(
            login_target,
            login_role=login_role,
            capability_role=capability_role,
            references=references,
            materials=materials,
        )
        raw_values = (*raw_values, password, login_target.render_as_string(False))
        raw_scan = _raw_database_scan(owner, raw_values)
        migration = {
            "head_revision": MIGRATION_HEAD,
            "upgrade_passed": True,
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": True,
            "upgrade_log_nonempty": bool(upgrade.strip()),
            "migration_log_recorded": False,
        }
        passed = all(
            (
                migration["current_head_exact"],
                role_contract["passed"],
                direct_denial["passed"],
                operational["passed"],
                raw_scan["passed"],
            )
        )
        evidence.update(
            {
                "result": RESULT if passed else "revision_required",
                "migration": migration,
                "role_contract": role_contract,
                "direct_login_denial": direct_denial,
                "operational_runtime": operational,
                "raw_residue_scan": raw_scan,
                "side_effect_counts": {
                    "disposable_database_migrations": 1,
                    "disposable_database_reads": "performed",
                    "disposable_database_writes": "performed",
                    "disposable_cluster_roles": 2,
                    "external_http_or_socket_calls": 0,
                    "provider_calls": 0,
                    "real_identities": 0,
                    "identity_bindings": 0,
                    "application_sessions": 0,
                    "product_data_reads": 0,
                    "patient_or_clinical_reads": 0,
                    "routes_added_or_mounted": 0,
                    "cloud_or_iam_mutations": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "Only a unique disposable loopback PostgreSQL database, one generated LOGIN credential, one exact NOLOGIN capability role and authored-synthetic attempts were exercised.",
                    "No credential or target is recorded; no hosted database, live provider, real identity, route, binding, session, product read, deployment, production or release is established.",
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        prohibited = (
            database_name,
            login_role,
            capability_role,
            password,
            login_target.render_as_string(False),
            *references.values(),
            *raw_values,
        )
        evidence_matches = sum(bool(value) and value in serialized for value in prohibited)
        evidence["evidence_sensitive_match_count"] = evidence_matches
        if evidence_matches:
            raise AcceptanceFailure("sensitive_value_in_evidence")
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        evidence["failure_stage"] = stage
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
    finally:
        if owner is not None:
            owner.dispose()
        if database_created:
            evidence["cleanup"]["database_drop_attempted"] = True
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance, database_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_cleanup_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = not _database_exists(
                maintenance, database_name
            )
        if login_created:
            evidence["cleanup"]["login_role_drop_attempted"] = True
            try:
                evidence["cleanup"]["login_role_absent_after"] = _drop_role(
                    maintenance, login_role, login=True
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["login_cleanup_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["login_role_absent_after"] = _role_absent(
                maintenance, login_role
            )
        if capability_created:
            evidence["cleanup"]["capability_role_drop_attempted"] = True
            try:
                evidence["cleanup"]["capability_role_absent_after"] = _drop_role(
                    maintenance, capability_role, login=False
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["capability_cleanup_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["capability_role_absent_after"] = _role_absent(
                maintenance, capability_role
            )
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(
        (
            evidence["cleanup"]["database_absent_after"],
            evidence["cleanup"]["login_role_absent_after"],
            evidence["cleanup"]["capability_role_absent_after"],
        )
    )
    if not evidence["cleanup"]["passed"]:
        evidence["result"] = "revision_required"
    evidence["passed"] = (
        evidence["result"] == RESULT
        and evidence["cleanup"]["passed"]
        and failure_type is None
    )
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    evidence = run_acceptance(output_path=args.output)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "passed": evidence["passed"],
                "cleanup_passed": evidence["cleanup"]["passed"],
                "failure_type": evidence.get("failure_type"),
                "failure_code": evidence.get("failure_code"),
                "failure_stage": evidence.get("failure_stage"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
