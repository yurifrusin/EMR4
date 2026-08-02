"""Disposable live-local PostgreSQL acceptance for the OIDC attempt store."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier, Lock
from typing import Any, Callable
from urllib.parse import urlencode

from cryptography.fernet import Fernet
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.application_identity_oidc_attempt import (  # noqa: E402
    ApplicationIdentityOIDCAuthorizationAttempt,
)
from app.services.application_identity_oidc_adapter import (  # noqa: E402
    ATTEMPT_TTL_SECONDS,
    InMemoryOIDCAdapterAuditSink,
    MicrosoftOIDCAdapterConfig,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    ReturnTarget,
    Surface,
    TwoComponentOIDCAdapter,
    VerifiedMicrosoftPrincipal,
)
from app.services.application_identity_oidc_attempt_database_role import (  # noqa: E402
    ATTEMPT_TABLE,
    create_oidc_attempt_runtime_role_statements,
    drop_oidc_attempt_runtime_role_statement,
)
from app.services.application_identity_oidc_attempt_store import (  # noqa: E402
    AuthorizationAttemptDigestKeyring,
    ENVELOPE_VERSION,
    FernetAuthorizationAttemptCipher,
    PostgresAuthorizationAttemptStore,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-postgresql-oidc-authorization-attempt-store"
    / "live-local-backend-postgres-evidence.json"
)
RESULT = "postgresql_oidc_authorization_attempt_store_pass"
DATABASE_PATTERN = re.compile(
    r"^emr4_oidc_attempt_acceptance_[0-9a-f]{12}$"
)
ROLE_PATTERN = re.compile(
    r"^emr4_oidc_attempt_runtime_[0-9a-f]{12}$"
)
OUTSIDER_PATTERN = re.compile(
    r"^emr4_oidc_attempt_outsider_[0-9a-f]{12}$"
)
MIGRATION_BASE = "q6r7s8t9u0v1"
MIGRATION_HEAD = "r7s8t9u0v1w2"
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
FIXED_NOW = datetime(2026, 8, 2, 6, 0, tzinfo=timezone.utc)
TENANT_ID = "11111111-1111-4111-8111-111111111111"
CLIENT_ID = "22222222-2222-4222-8222-222222222222"
REDIRECT_URI = (
    "https://oidc-authored-synthetic.example.invalid"
    "/api/v1/application-auth/federation/microsoft/callback"
)
ORIGIN = "https://word-online-authored-synthetic.example.invalid"


class AcceptanceFailure(RuntimeError):
    pass


class _ProtocolClient:
    def __init__(self) -> None:
        self._counter = 0
        self._exchange_count = 0
        self._lock = Lock()

    def create_authorization_flow(self) -> dict[str, Any]:
        with self._lock:
            self._counter += 1
            counter = self._counter
        return _flow(counter)

    def redeem_authorization_flow(
        self,
        stored_flow: dict[str, Any],
        auth_response: dict[str, str],
    ) -> dict[str, Any]:
        assert stored_flow["state"] == auth_response["state"]
        with self._lock:
            self._exchange_count += 1
        return {
            "id_token": "synthetic.raw.id.token",
            "id_token_claims": {
                "tid": TENANT_ID,
                "oid": "untrusted-msal-claim",
            },
        }

    @property
    def exchange_count(self) -> int:
        with self._lock:
            return self._exchange_count


class _Verifier:
    def __init__(self) -> None:
        self._count = 0
        self._lock = Lock()

    def verify_id_token(
        self, raw_id_token: str, *, expected_nonce: str, now: datetime
    ) -> VerifiedMicrosoftPrincipal:
        assert raw_id_token == "synthetic.raw.id.token"
        assert expected_nonce.startswith("nonce-")
        assert now.tzinfo is not None
        with self._lock:
            self._count += 1
        return VerifiedMicrosoftPrincipal(
            tenant_id=TENANT_ID,
            object_id="synthetic-object-verified",
            subject="synthetic-subject-verified",
        )

    @property
    def count(self) -> int:
        with self._lock:
            return self._count


def _base_database_url() -> URL:
    target = make_url(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
    if target.get_backend_name() != "postgresql":
        raise AcceptanceFailure("postgresql_required")
    if target.host not in {"127.0.0.1", "localhost"}:
        raise AcceptanceFailure("loopback_database_required")
    if target.port != 5434:
        raise AcceptanceFailure("expected_local_postgresql_port_required")
    if target.database in {None, "", "postgres"}:
        raise AcceptanceFailure("bounded_source_database_required")
    return target


def _database_exists(maintenance: Engine, database_name: str) -> bool:
    with maintenance.connect() as connection:
        return bool(
            connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            ).scalar_one_or_none()
        )


def _create_database(maintenance: Engine, database_name: str) -> None:
    if not DATABASE_PATTERN.fullmatch(database_name):
        raise AcceptanceFailure("unsafe_database_name")
    if _database_exists(maintenance, database_name):
        raise AcceptanceFailure("disposable_database_preexisted")
    with maintenance.connect() as connection:
        quoted = connection.dialect.identifier_preparer.quote(database_name)
        connection.execute(text(f"CREATE DATABASE {quoted}"))


def _drop_database(maintenance: Engine, database_name: str) -> bool:
    if not DATABASE_PATTERN.fullmatch(database_name):
        raise AcceptanceFailure("unsafe_database_cleanup_name")
    with maintenance.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :name AND pid <> pg_backend_pid()"
            ),
            {"name": database_name},
        )
        if _database_exists(maintenance, database_name):
            quoted = connection.dialect.identifier_preparer.quote(database_name)
            connection.execute(text(f"DROP DATABASE {quoted}"))
    return not _database_exists(maintenance, database_name)


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
    if completed.returncode != 0:
        raise AcceptanceFailure(f"alembic_{arguments[0]}_failed")
    return completed.stdout + completed.stderr


def _role_engine(target: URL, role_name: str) -> Engine:
    if not ROLE_PATTERN.fullmatch(role_name):
        raise AcceptanceFailure("unsafe_role_name")
    engine = create_engine(target, poolclass=NullPool, pool_pre_ping=True)

    @event.listens_for(engine, "checkout")
    def _set_role(dbapi_connection, _record, _proxy) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f'SET ROLE "{role_name}"')
        finally:
            cursor.close()

    return engine


def _factory(engine: Engine) -> Callable[[], Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def _keys() -> dict[str, Any]:
    return {
        "enc_v1": Fernet.generate_key(),
        "enc_v2": Fernet.generate_key(),
        "dig_v1": secrets.token_bytes(32),
        "dig_v2": secrets.token_bytes(32),
    }


def _store(
    factory: Callable[[], Session],
    keys: dict[str, Any],
    *,
    active_cipher: str = "enc-v1",
    active_digest: str = "dig-v1",
    retain_cipher_v1: bool = True,
    retain_digest_v1: bool = True,
    max_attempts: int = 128,
) -> PostgresAuthorizationAttemptStore:
    cipher_keys = {"enc-v2": keys["enc_v2"]}
    digest_keys = {"dig-v2": keys["dig_v2"]}
    if retain_cipher_v1:
        cipher_keys["enc-v1"] = keys["enc_v1"]
    if retain_digest_v1:
        digest_keys["dig-v1"] = keys["dig_v1"]
    return PostgresAuthorizationAttemptStore(
        session_factory=factory,
        cipher=FernetAuthorizationAttemptCipher(
            active_key_id=active_cipher,
            keys=cipher_keys,
        ),
        digest_keyring=AuthorizationAttemptDigestKeyring(
            active_key_id=active_digest,
            keys=digest_keys,
        ),
        max_attempts=max_attempts,
    )


def _config() -> MicrosoftOIDCAdapterConfig:
    return MicrosoftOIDCAdapterConfig(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        surface_origins={
            Surface.WORD_DESKTOP: "https://word-desktop-authored-synthetic.example.invalid",
            Surface.WORD_ONLINE: ORIGIN,
            Surface.NATIVE_DIARY: "https://diary-authored-synthetic.example.invalid",
        },
        enabled=True,
    )


def _flow(counter: int) -> dict[str, Any]:
    state = f"state-{counter:016d}"
    nonce = f"nonce-{counter:026d}"
    verifier = f"verifier-{counter:034d}"
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile",
        "state": state,
        "response_mode": "form_post",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "nonce": hashlib.sha256(nonce.encode("ascii")).hexdigest(),
        "client_info": "1",
    }
    return {
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "scope": ["openid", "profile"],
        "auth_uri": (
            f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?"
            + urlencode(params)
        ),
        "code_verifier": verifier,
        "nonce": nonce,
        "claims_challenge": None,
    }


def _put(store: PostgresAuthorizationAttemptStore, flow: dict[str, Any], now: datetime) -> str:
    reference, _ = store.store(
        flow=flow,
        surface=Surface.WORD_ONLINE,
        origin=ORIGIN,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=now,
        ttl_seconds=ATTEMPT_TTL_SECONDS,
    )
    return reference


def _reason(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except (OIDCAuthenticationFailed, OIDCTemporarilyUnavailable) as exc:
        return exc.reason_code
    return None


def _schema_and_role_contract(owner: Engine, role_engine: Engine, role_name: str) -> dict[str, Any]:
    inspector = inspect(owner)
    model_columns = {
        column.name
        for column in ApplicationIdentityOIDCAuthorizationAttempt.__table__.columns
    }
    database_columns = {
        column["name"] for column in inspector.get_columns(ATTEMPT_TABLE)
    }
    with owner.connect() as connection:
        rls = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = :table"
            ),
            {"table": ATTEMPT_TABLE},
        ).one()
        policies = set(
            connection.execute(
                text("SELECT policyname FROM pg_policies WHERE tablename = :table"),
                {"table": ATTEMPT_TABLE},
            ).scalars()
        )
        privileges = set(
            connection.execute(
                text(
                    "SELECT privilege_type FROM information_schema.role_table_grants "
                    "WHERE grantee = :role AND table_name = :table"
                ),
                {"role": role_name, "table": ATTEMPT_TABLE},
            ).scalars()
        )
        public_access = bool(
            connection.execute(
                text("SELECT has_table_privilege('public', :table, 'SELECT')"),
                {"table": f"public.{ATTEMPT_TABLE}"},
            ).scalar_one()
        )
    with role_engine.connect() as connection:
        session_user, current_user = connection.execute(
            text("SELECT session_user, current_user")
        ).one()
    expected_policies = {
        "app_id_oidc_attempt_runtime_select",
        "app_id_oidc_attempt_runtime_insert",
        "app_id_oidc_attempt_runtime_delete",
    }
    passed = (
        model_columns == database_columns
        and bool(rls[0] and rls[1])
        and policies == expected_policies
        and privileges == {"SELECT", "INSERT", "DELETE"}
        and not public_access
        and session_user != current_user == role_name
    )
    return {
        "model_database_column_match": model_columns == database_columns,
        "forced_rls": bool(rls[0] and rls[1]),
        "policies": sorted(policies),
        "capability_privileges": sorted(privileges),
        "public_select": public_access,
        "session_and_effective_role_separated": session_user != current_user,
        "effective_role_allowlisted": current_user == role_name,
        "role_name_recorded": False,
        "passed": passed,
    }


def _outsider_and_update_probe(owner: Engine, role_engine: Engine) -> dict[str, Any]:
    outsider = f"emr4_oidc_attempt_outsider_{secrets.token_hex(6)}"
    if not OUTSIDER_PATTERN.fullmatch(outsider):
        raise AcceptanceFailure("unsafe_outsider_role")
    outsider_select = None
    outsider_insert_state = None
    with owner.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(f'CREATE ROLE "{outsider}" NOLOGIN NOBYPASSRLS'))
            connection.execute(
                text(
                    f'GRANT SELECT, INSERT, DELETE ON TABLE "{ATTEMPT_TABLE}" '
                    f'TO "{outsider}"'
                )
            )
            connection.execute(text(f'SET LOCAL ROLE "{outsider}"'))
            outsider_select = int(
                connection.execute(text(f'SELECT count(*) FROM "{ATTEMPT_TABLE}"')).scalar_one()
            )
            try:
                connection.execute(
                    text(
                        f'INSERT INTO "{ATTEMPT_TABLE}" '
                        "(state_reference_hmac, nonce_reference_hmac, cipher_key_id, "
                        "ciphertext, envelope_version, created_at, expires_at, data_class) "
                        "VALUES (:state, :nonce, 'enc-v1', :ciphertext, :version, "
                        ":created, :expires, 'authored_synthetic')"
                    ),
                    {
                        "state": "hmac-sha256:dig-v1:" + "1" * 64,
                        "nonce": "hmac-sha256:dig-v1:" + "2" * 64,
                        "ciphertext": b"synthetic-ciphertext",
                        "version": ENVELOPE_VERSION,
                        "created": FIXED_NOW,
                        "expires": FIXED_NOW + timedelta(minutes=5),
                    },
                )
            except DBAPIError as exc:
                outsider_insert_state = getattr(
                    exc.orig, "sqlstate", None
                ) or getattr(exc.orig, "pgcode", None)
        finally:
            transaction.rollback()
    with owner.connect() as connection:
        outsider_absent = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": outsider},
        ).scalar_one_or_none() is None
    update_state = None
    try:
        with role_engine.begin() as connection:
            connection.execute(
                text(f'UPDATE "{ATTEMPT_TABLE}" SET data_class = data_class')
            )
    except DBAPIError as exc:
        update_state = getattr(exc.orig, "sqlstate", None) or getattr(
            exc.orig, "pgcode", None
        )
    passed = (
        outsider_select == 0
        and outsider_insert_state == "42501"
        and outsider_absent
        and update_state == "42501"
    )
    return {
        "outsider_visible_rows": outsider_select,
        "outsider_insert_sqlstate": outsider_insert_state,
        "outsider_role_absent_after_rollback": outsider_absent,
        "capability_update_sqlstate": update_state,
        "passed": passed,
    }


def _exercise(
    owner: Engine,
    factory: Callable[[], Session],
    keys: dict[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    raw_values: list[str] = []
    store = _store(factory, keys)

    durable_flow = _flow(100)
    raw_values.extend(_raw_flow_values(durable_flow))
    durable_reference = _put(store, durable_flow, FIXED_NOW)
    durable = _store(factory, keys).consume(
        state=durable_flow["state"], now=FIXED_NOW + timedelta(seconds=1)
    )

    protocol = _ProtocolClient()
    verifier = _Verifier()
    adapter_store = _store(factory, keys)
    adapter = TwoComponentOIDCAdapter(
        config=_config(),
        protocol_client=protocol,
        verifier=verifier,
        attempt_store=adapter_store,
        audit_sink=InMemoryOIDCAdapterAuditSink(),
    )
    start = adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=FIXED_NOW,
    )
    adapter_flow = _flow(1)
    raw_values.extend(_raw_flow_values(adapter_flow))
    barrier = Barrier(2)

    def complete(_index: int) -> str:
        barrier.wait(timeout=10)
        try:
            result = adapter.complete_authorization_flow(
                auth_response={"state": adapter_flow["state"], "code": "synthetic-code"},
                now=FIXED_NOW + timedelta(seconds=2),
            )
            return result.principal.object_id
        except (OIDCAuthenticationFailed, OIDCTemporarilyUnavailable) as exc:
            return exc.reason_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        concurrency = sorted(executor.map(complete, (1, 2)))
    replay = _reason(
        lambda: adapter.complete_authorization_flow(
            auth_response={"state": adapter_flow["state"], "code": "synthetic-code"},
            now=FIXED_NOW + timedelta(seconds=3),
        )
    )

    expiry_flow = _flow(200)
    raw_values.extend(_raw_flow_values(expiry_flow))
    _put(store, expiry_flow, FIXED_NOW)
    expiry_reason = _reason(
        lambda: store.consume(
            state=expiry_flow["state"], now=FIXED_NOW + timedelta(minutes=5)
        )
    )
    expiry_replay = _reason(
        lambda: store.consume(
            state=expiry_flow["state"], now=FIXED_NOW + timedelta(minutes=5)
        )
    )

    capacity = _store(factory, keys, max_attempts=2)
    cap_flows = (_flow(300), _flow(301), _flow(302), _flow(303))
    for flow in cap_flows:
        raw_values.extend(_raw_flow_values(flow))
    _put(capacity, cap_flows[0], FIXED_NOW)
    _put(capacity, cap_flows[1], FIXED_NOW)
    capacity_reason = _reason(lambda: _put(capacity, cap_flows[2], FIXED_NOW))
    _put(capacity, cap_flows[3], FIXED_NOW + timedelta(minutes=6))
    capacity_after_purge = capacity.active_count(
        now=FIXED_NOW + timedelta(minutes=6)
    )
    capacity.discard(state=cap_flows[3]["state"])
    discard_count = capacity.active_count(now=FIXED_NOW + timedelta(minutes=6))

    collision_flow = _flow(400)
    raw_values.extend(_raw_flow_values(collision_flow))
    _put(store, collision_flow, FIXED_NOW)
    collision_reason = _reason(lambda: _put(store, collision_flow, FIXED_NOW))
    store.discard(state=collision_flow["state"])

    rotation_flow = _flow(500)
    raw_values.extend(_raw_flow_values(rotation_flow))
    old_store = _store(factory, keys)
    rotation_reference = _put(old_store, rotation_flow, FIXED_NOW)
    rotated = _store(
        factory,
        keys,
        active_cipher="enc-v2",
        active_digest="dig-v2",
    ).consume(state=rotation_flow["state"], now=FIXED_NOW + timedelta(seconds=1))

    missing_key_flow = _flow(501)
    raw_values.extend(_raw_flow_values(missing_key_flow))
    _put(old_store, missing_key_flow, FIXED_NOW)
    no_old_cipher = _store(
        factory,
        keys,
        active_cipher="enc-v2",
        active_digest="dig-v2",
        retain_cipher_v1=False,
    )
    missing_key_reason = _reason(
        lambda: no_old_cipher.consume(
            state=missing_key_flow["state"], now=FIXED_NOW + timedelta(seconds=1)
        )
    )
    missing_key_replay = _reason(
        lambda: no_old_cipher.consume(
            state=missing_key_flow["state"], now=FIXED_NOW + timedelta(seconds=2)
        )
    )

    tamper_flow = _flow(600)
    raw_values.extend(_raw_flow_values(tamper_flow))
    tamper_reference = _put(store, tamper_flow, FIXED_NOW)
    with owner.begin() as connection:
        connection.execute(
            text(
                f'UPDATE "{ATTEMPT_TABLE}" SET ciphertext = :ciphertext '
                "WHERE state_reference_hmac = :reference"
            ),
            {"ciphertext": b"tampered-ciphertext", "reference": tamper_reference},
        )
    tamper_reason = _reason(
        lambda: store.consume(
            state=tamper_flow["state"], now=FIXED_NOW + timedelta(seconds=1)
        )
    )
    tamper_replay = _reason(
        lambda: store.consume(
            state=tamper_flow["state"], now=FIXED_NOW + timedelta(seconds=2)
        )
    )

    audit_protocol = _ProtocolClient()
    audit_adapter = TwoComponentOIDCAdapter(
        config=_config(),
        protocol_client=audit_protocol,
        verifier=_Verifier(),
        attempt_store=store,
        audit_sink=InMemoryOIDCAdapterAuditSink(available=False),
    )
    audit_reason = _reason(
        lambda: audit_adapter.create_authorization_flow(
            surface=Surface.WORD_ONLINE,
            return_target=ReturnTarget.CLINICIAN_ONE,
            now=FIXED_NOW,
        )
    )
    audit_flow = _flow(1)
    audit_cleanup = _reason(
        lambda: store.consume(state=audit_flow["state"], now=FIXED_NOW)
    )

    residue_flow = _flow(700)
    raw_values.extend(_raw_flow_values(residue_flow))
    _put(store, residue_flow, FIXED_NOW)

    runtime = {
        "durability": {
            "fresh_store_instance_consumed": durable.flow == durable_flow,
            "reference_preserved": durable.attempt_reference == durable_reference,
        },
        "adapter_concurrency": {
            "authorization_start_returned": start.status == "authorization_required",
            "independent_database_sessions": 2,
            "results": concurrency,
            "exactly_one_exchange": protocol.exchange_count == 1,
            "exactly_one_verification": verifier.count == 1,
            "replay_reason": replay,
        },
        "expiry": {
            "boundary_reason": expiry_reason,
            "replay_reason": expiry_replay,
        },
        "capacity_and_discard": {
            "capacity_reason": capacity_reason,
            "active_after_expiry_purge": capacity_after_purge,
            "active_after_discard": discard_count,
        },
        "collision_reason": collision_reason,
        "key_rotation": {
            "retained_cipher_and_digest_consumed": rotated.flow == rotation_flow,
            "old_reference_preserved": rotated.attempt_reference == rotation_reference,
            "missing_cipher_reason": missing_key_reason,
            "missing_cipher_replay_reason": missing_key_replay,
        },
        "tamper": {
            "reason": tamper_reason,
            "replay_reason": tamper_replay,
        },
        "audit_cleanup": {
            "audit_reason": audit_reason,
            "attempt_after_failed_start": audit_cleanup,
            "provider_exchange_count": audit_protocol.exchange_count,
        },
    }
    runtime["passed"] = (
        all(runtime["durability"].values())
        and runtime["adapter_concurrency"]["results"]
        == ["authorization_attempt_required", "synthetic-object-verified"]
        and runtime["adapter_concurrency"]["exactly_one_exchange"]
        and runtime["adapter_concurrency"]["exactly_one_verification"]
        and replay == "authorization_attempt_required"
        and expiry_reason == "authorization_attempt_expired"
        and expiry_replay == "authorization_attempt_required"
        and capacity_reason == "authorization_attempt_capacity"
        and capacity_after_purge == 1
        and discard_count == 0
        and collision_reason == "authorization_state_collision"
        and runtime["key_rotation"]["retained_cipher_and_digest_consumed"]
        and runtime["key_rotation"]["old_reference_preserved"]
        and missing_key_reason == "authorization_attempt_key_unavailable"
        and missing_key_replay == "authorization_attempt_required"
        and tamper_reason == "authorization_attempt_unreadable"
        and tamper_replay == "authorization_attempt_required"
        and audit_reason == "required_audit_unavailable"
        and audit_cleanup == "authorization_attempt_required"
        and audit_protocol.exchange_count == 0
    )
    return runtime, tuple(raw_values)


def _raw_flow_values(flow: dict[str, Any]) -> tuple[str, ...]:
    return (
        flow["state"],
        flow["nonce"],
        flow["code_verifier"],
        flow["auth_uri"],
        flow["redirect_uri"],
        ORIGIN,
    )


def _raw_scan(owner: Engine, values: tuple[str, ...], keys: dict[str, Any]) -> dict[str, Any]:
    with owner.connect() as connection:
        rows = tuple(
            connection.execute(
                text(f'SELECT to_jsonb(t)::text FROM "{ATTEMPT_TABLE}" AS t')
            ).scalars()
        )
    key_values = (
        keys["enc_v1"].decode("ascii"),
        keys["enc_v2"].decode("ascii"),
        keys["dig_v1"].hex(),
        keys["dig_v2"].hex(),
    )
    joined = "\n".join(rows)
    matched = [value for value in (*values, *key_values) if value in joined]
    return {
        "persisted_row_count": len(rows),
        "active_encrypted_row_present": len(rows) == 1,
        "scanned_sensitive_value_count": len(values) + len(key_values),
        "matched_sensitive_value_count": len(matched),
        "matched_values_recorded": False,
        "passed": len(rows) == 1 and not matched,
    }


def _drop_role(maintenance: Engine, role_name: str) -> bool:
    if not ROLE_PATTERN.fullmatch(role_name):
        raise AcceptanceFailure("unsafe_role_cleanup_name")
    with maintenance.begin() as connection:
        present = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": role_name},
        ).scalar_one_or_none()
        if present is not None:
            connection.execute(text(drop_oidc_attempt_runtime_role_statement(role_name)))
    with maintenance.connect() as connection:
        return connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": role_name},
        ).scalar_one_or_none() is None


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    database_name = f"emr4_oidc_attempt_acceptance_{secrets.token_hex(6)}"
    role_name = f"emr4_oidc_attempt_runtime_{secrets.token_hex(6)}"
    base = _base_database_url()
    target = base.set(database=database_name)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    runtime_engine: Engine | None = None
    database_created = False
    role_created = False
    failure_type: str | None = None
    evidence: dict[str, Any] = {
        "schema_version": "emr4.postgresql-oidc-authorization-attempt-store-evidence.v1",
        "result": "revision_required",
        "evidence_label": "live_local_backend_postgres",
        "data_class": "authored_synthetic",
        "database": {
            "name_recorded": False,
            "unique_allowlisted_name_used": DATABASE_PATTERN.fullmatch(database_name) is not None,
            "loopback_only": True,
            "preexisting": False,
        },
        "cleanup": {
            "database_drop_attempted": False,
            "database_absent_after": False,
            "role_drop_attempted": False,
            "role_absent_after": False,
            "role_name_recorded": False,
        },
    }
    try:
        if not DATABASE_PATTERN.fullmatch(database_name) or not ROLE_PATTERN.fullmatch(role_name):
            raise AcceptanceFailure("generated_identifier_invalid")
        _create_database(maintenance, database_name)
        database_created = True
        upgrade = _require_alembic(target, "upgrade", MIGRATION_HEAD)
        _require_alembic(target, "downgrade", MIGRATION_BASE)
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        owner = create_engine(target, pool_pre_ping=True)
        with owner.begin() as connection:
            for statement in create_oidc_attempt_runtime_role_statements(role_name):
                connection.execute(text(statement))
        role_created = True
        runtime_engine = _role_engine(target, role_name)
        factory = _factory(runtime_engine)
        keys = _keys()
        schema_role = _schema_and_role_contract(owner, runtime_engine, role_name)
        rls_probe = _outsider_and_update_probe(owner, runtime_engine)
        runtime, raw_values = _exercise(owner, factory, keys)
        raw_scan = _raw_scan(owner, raw_values, keys)
        migration = {
            "base_revision": MIGRATION_BASE,
            "head_revision": MIGRATION_HEAD,
            "upgrade_passed": True,
            "downgrade_passed": True,
            "reupgrade_passed": True,
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": True,
            "initial_upgrade_log_nonempty": bool(upgrade.strip()),
            "migration_log_recorded": False,
        }
        passed = (
            migration["current_head_exact"]
            and schema_role["passed"]
            and rls_probe["passed"]
            and runtime["passed"]
            and raw_scan["passed"]
        )
        evidence.update(
            {
                "result": RESULT if passed else "revision_required",
                "migration": migration,
                "schema_and_role_contract": schema_role,
                "rls_and_privilege_probe": rls_probe,
                "runtime": runtime,
                "raw_residue_scan": raw_scan,
                "side_effect_counts": {
                    "disposable_database_migrations": 3,
                    "disposable_database_reads": "performed",
                    "disposable_database_writes": "performed",
                    "disposable_cluster_roles": 1,
                    "provider_calls": 0,
                    "external_http_or_socket_calls": 0,
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
                    "Only a uniquely named disposable loopback PostgreSQL database, one exact NOLOGIN capability role and authored-synthetic attempts were exercised.",
                    "No live Microsoft/provider call, real identity, route, binding, session, product read, deployment, production or release authority is established.",
                ],
            }
        )
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
    finally:
        if runtime_engine is not None:
            runtime_engine.dispose()
        if owner is not None:
            owner.dispose()
        if database_created:
            evidence["cleanup"]["database_drop_attempted"] = True
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance, database_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_cleanup_failure_type"] = type(cleanup_exc).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = not _database_exists(
                maintenance, database_name
            )
        if role_created:
            evidence["cleanup"]["role_drop_attempted"] = True
            try:
                evidence["cleanup"]["role_absent_after"] = _drop_role(
                    maintenance, role_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["role_cleanup_failure_type"] = type(cleanup_exc).__name__
        else:
            with maintenance.connect() as connection:
                evidence["cleanup"]["role_absent_after"] = connection.execute(
                    text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
                    {"role": role_name},
                ).scalar_one_or_none() is None
        maintenance.dispose()
    evidence["cleanup"]["passed"] = bool(
        evidence["cleanup"]["database_absent_after"]
        and evidence["cleanup"]["role_absent_after"]
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
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
