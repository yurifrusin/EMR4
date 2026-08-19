"""Run the bounded check-in rollback and lost-terminal-response rehearsal."""

from __future__ import annotations

import copy
import json
import multiprocessing
import os
import queue
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.pool import NullPool

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_runtime_role_tenant_isolation_attestation_rehearsal
    as predecessor,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as foundation,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)


BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "default-off-check-in-rollback-unknown-commit-recovery-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
MANIFEST_SCHEMA_PATH = BASE / "transaction-manifest.schema.json"
ATTESTATION_SCHEMA_PATH = BASE / "transaction-attestation.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "rehearsal-evidence.schema.json"
ATTESTATION_PATH = BASE / "transaction-attestation.json"
EVIDENCE_PATH = BASE / "rehearsal-evidence.json"
FAILURE_PATH = BASE / "rehearsal-failure-evidence.json"

PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_default_off_check_in_rollback_"
    "unknown_commit_recovery_rehearsal_pass"
)
EVIDENCE_LABEL = (
    "authored_synthetic_provider_free_disposable_postgresql_check_in_rollback_"
    "unknown_terminal_response_recovery"
)
SOURCE_HEAD = "26402cb8667c2dbf62e86c6eb4c0b000d274559e"
ACCEPTED_RUNTIME_ROLE_SOURCE = "6a2832575e9b4df5c40a13984db7281e79814a94"
CLAIM_BOUNDARY = (
    "One authored-synthetic pre-commit rollback and one caller-level lost complete "
    "terminal response resolved by exact restricted-role PostgreSQL readback only; "
    "no literal in-COMMIT crash, retry, ordinary release, product runtime or "
    "production claim."
)
EXPECTED_SCENARIOS = (
    "RUC-S01",
    "RUC-S02",
    "RUC-S03",
    "RUC-S04",
    "RUC-S05",
    "RUC-S06",
    "RUC-S07",
    "RUC-S08",
    "RUC-S09",
    "RUC-S10",
    "RUC-S11",
    "RUC-S12",
)
RELATIONS = ("command_effect", "command_receipt", "command_audit")
PACKET_KEYS = ("effect", "receipt", "audit")
FORBIDDEN_KEYS = {
    "password",
    "secret_value",
    "database_url",
    "connection_url",
    "dsn",
    "environment_value",
    "private_key",
    "raw_output",
    "raw_exception",
    "server_log",
    "wal",
    "backend_pid",
    "query_text",
    "raw_sql",
    "docker_environment",
    "container_name",
    "network_name",
    "application_name",
    "local_path",
    "secret_material_sha256",
}


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str = "") -> None:
        self.stage = stage
        self.code = code
        self.detail = detail
        super().__init__(f"{stage}:{code}")


class EOFPropagatingDockerExecRelay(foundation.DockerExecRelay):
    """Propagate container-side EOF to the loopback client as a half-close."""

    def _bridge(self, connection: socket.socket) -> None:
        process: subprocess.Popen[bytes] | None = None
        try:
            process = subprocess.Popen(
                self._argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                shell=False,
                bufsize=0,
            )
            assert process.stdin is not None
            assert process.stdout is not None
            with self._lock:
                self._processes.add(process)

            def socket_to_process() -> None:
                try:
                    while not self._stopping.is_set():
                        payload = connection.recv(65536)
                        if not payload:
                            break
                        process.stdin.write(payload)
                        process.stdin.flush()
                except (BrokenPipeError, OSError):
                    pass
                finally:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass

            def process_to_socket() -> None:
                try:
                    while not self._stopping.is_set():
                        payload = os.read(process.stdout.fileno(), 65536)
                        if not payload:
                            break
                        connection.sendall(payload)
                except OSError:
                    pass
                finally:
                    try:
                        connection.shutdown(socket.SHUT_WR)
                    except OSError:
                        pass

            upstream = threading.Thread(target=socket_to_process, daemon=True)
            downstream = threading.Thread(target=process_to_socket, daemon=True)
            upstream.start()
            downstream.start()
            upstream.join()
            downstream.join()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=3)
        except (OSError, subprocess.SubprocessError):
            pass
        finally:
            try:
                connection.close()
            except OSError:
                pass
            with self._lock:
                self._connections.discard(connection)
                if process is not None:
                    self._processes.discard(process)


def _sha256(value: bytes | str) -> str:
    return predecessor._sha256(value)  # noqa: SLF001


def _json_bytes(value: Any) -> bytes:
    return predecessor._json_bytes(value)  # noqa: SLF001


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_source_bytes(path: Path) -> bytes:
    try:
        return predecessor._canonical_source_bytes(path)  # noqa: SLF001
    except predecessor.RehearsalFailure as caught:
        raise RehearsalFailure("preflight", caught.code, caught.detail) from caught


def _leaf_paths(
    value: Any, prefix: tuple[str | int, ...] = ()
) -> list[tuple[str | int, ...]]:
    if isinstance(value, dict):
        return [
            path
            for key, item in value.items()
            for path in _leaf_paths(item, prefix + (key,))
        ]
    if isinstance(value, list):
        return [
            path
            for index, item in enumerate(value)
            for path in _leaf_paths(item, prefix + (index,))
        ]
    return [prefix]


def _value_at(value: Any, path: tuple[str | int, ...]) -> Any:
    cursor = value
    for part in path:
        cursor = cursor[part]
    return cursor


def _replace_leaf(candidate: Any, path: tuple[str | int, ...], value: Any) -> None:
    cursor = candidate
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


def _mutated_values(value: Any) -> tuple[Any, ...]:
    if isinstance(value, bool):
        return (not value, None, "invalid", 7, [])
    if isinstance(value, int):
        return (-1 if value != -1 else -2, None, "invalid", value + 1, [])
    if isinstance(value, str):
        return ("", value + "-invalid", None, 7, [])
    return (None, "invalid", 7, False, [])


def _assert_redacted(value: Any, *, forbidden_values: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise RehearsalFailure("evidence", "forbidden_evidence_field", key)
            _assert_redacted(item, forbidden_values=forbidden_values)
        return
    if isinstance(value, list):
        for item in value:
            _assert_redacted(item, forbidden_values=forbidden_values)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if "postgresql://" in lowered or "postgresql+" in lowered:
            raise RehearsalFailure("evidence", "connection_url_leaked")
        for forbidden in forbidden_values:
            if forbidden and forbidden in value:
                raise RehearsalFailure("evidence", "runtime_value_leaked")


def _validate_contract(value: dict[str, Any], canonical: dict[str, Any]) -> None:
    validator = Draft202012Validator(
        _load_json(CONTRACT_SCHEMA_PATH), format_checker=FormatChecker()
    )
    if list(validator.iter_errors(value)):
        raise RehearsalFailure("preflight", "contract_schema_invalid")
    if tuple(item["id"] for item in value["scenarios"]) != EXPECTED_SCENARIOS:
        raise RehearsalFailure("preflight", "scenario_contract_mismatch")
    if value["source_head"] != SOURCE_HEAD:
        raise RehearsalFailure("preflight", "source_head_mismatch")
    if value["accepted_runtime_role_source"] != ACCEPTED_RUNTIME_ROLE_SOURCE:
        raise RehearsalFailure("preflight", "runtime_role_source_mismatch")
    if value != canonical:
        raise RehearsalFailure("preflight", "contract_noncanonical")


def hostile_contract_mutations_rejected(
    contract: dict[str, Any]
) -> tuple[int, int]:
    attempted = 0
    rejected = 0
    for path in _leaf_paths(contract):
        current = _value_at(contract, path)
        for replacement in _mutated_values(current):
            candidate = copy.deepcopy(contract)
            _replace_leaf(candidate, path, replacement)
            attempted += 1
            try:
                _validate_contract(candidate, contract)
            except RehearsalFailure:
                rejected += 1
    threshold = contract["hostile_thresholds"]["contract"]
    if attempted < threshold or attempted != rejected:
        raise RehearsalFailure("preflight", "hostile_contract_mutation_gate_failed")
    return attempted, rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str], tuple[int, int]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, contract)
    mutations = hostile_contract_mutations_rejected(contract)
    source_hashes: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(_canonical_source_bytes(path))
        source_hashes[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure("preflight", "source_hash_mismatch", binding["path"])
    if len(source_hashes) != 17:
        raise RehearsalFailure("preflight", "source_binding_count_mismatch")
    return contract, source_hashes, mutations


def build_manifest(contract: dict[str, Any], physical_role: str) -> dict[str, Any]:
    transaction = contract["transaction_profile"]
    return {
        "schema_version": transaction["manifest_schema_version"],
        "environment_identifier": transaction["environment_identifier"],
        "practice_scope_reference": transaction["practice_scope_reference"],
        "practice_id": transaction["practice_id"],
        "logical_role_id": contract["role_profile"]["logical_role_id"],
        "physical_role_identifier": physical_role,
        "authority_git_object": contract["accepted_runtime_role_source"],
        "commands": {
            "rollback": copy.deepcopy(transaction["rollback"]),
            "ambiguous_response": copy.deepcopy(transaction["ambiguous_response"]),
        },
        "packet_members": list(contract["database_profile"]["packet_members"]),
        "complete_terminal_response_required_for_success": transaction[
            "complete_terminal_response_required_for_success"
        ],
        "automatic_retry_allowed": transaction["automatic_retry_allowed"],
        "ordinary_admission_release_count": transaction[
            "ordinary_admission_release_count"
        ],
    }


def _validate_manifest(
    value: dict[str, Any], *, physical_role: str, canonical: dict[str, Any]
) -> None:
    validator = Draft202012Validator(
        _load_json(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    if list(validator.iter_errors(value)):
        raise RehearsalFailure("manifest", "manifest_schema_invalid")
    if value["physical_role_identifier"] != physical_role:
        raise RehearsalFailure("manifest", "physical_role_binding_mismatch")
    if value["authority_git_object"] != ACCEPTED_RUNTIME_ROLE_SOURCE:
        raise RehearsalFailure("manifest", "authority_git_object_mismatch")
    _assert_redacted(value)
    if value != canonical:
        raise RehearsalFailure("manifest", "manifest_noncanonical")


def hostile_manifest_mutations_rejected(
    manifest: dict[str, Any], physical_role: str, threshold: int
) -> tuple[int, int]:
    attempted = 0
    rejected = 0
    for path in _leaf_paths(manifest):
        current = _value_at(manifest, path)
        for replacement in _mutated_values(current):
            candidate = copy.deepcopy(manifest)
            _replace_leaf(candidate, path, replacement)
            attempted += 1
            try:
                _validate_manifest(
                    candidate, physical_role=physical_role, canonical=manifest
                )
            except RehearsalFailure:
                rejected += 1
    if attempted < threshold or attempted != rejected:
        raise RehearsalFailure("manifest", "hostile_manifest_mutation_gate_failed")
    return attempted, rejected


def _runtime_profile(contract: dict[str, Any], admin_password: str) -> dict[str, Any]:
    return predecessor._runtime_profile(contract, admin_password)  # noqa: SLF001


def _restricted_engine(
    host_port: int,
    profile: dict[str, Any],
    physical_role: str,
    runtime_password: str,
    application_label: str,
) -> Engine:
    if not re.fullmatch(r"emr4_checkin_(?:ruc|read)_[0-9a-f]{16}", application_label):
        raise RehearsalFailure("role", "application_label_invalid")
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{physical_role}:"
        f"{runtime_password}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        poolclass=NullPool,
        pool_pre_ping=False,
        connect_args={
            "connect_timeout": 5,
            "application_name": application_label,
        },
    )
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT current_user, rolcanlogin, rolsuper, rolcreatedb, "
                "rolcreaterole, rolinherit, rolreplication, rolbypassrls "
                "FROM pg_roles WHERE rolname=current_user"
            )
        ).one()
    expected = (physical_role, True, False, False, False, False, False, False)
    if tuple(row) != expected:
        engine.dispose()
        raise RehearsalFailure("role", "restricted_role_identity_mismatch")
    return engine


def _install_probe(
    admin: Engine,
    *,
    profile: dict[str, Any],
    physical_role: str,
    runtime_password: str,
) -> None:
    if not re.fullmatch(r"emr4_checkin_ruc_[0-9a-f]{16}", physical_role):
        raise RehearsalFailure("role", "physical_role_identifier_invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", runtime_password):
        raise RehearsalFailure("role", "runtime_credential_shape_invalid")
    schema = "check_in_recovery_probe"
    setting = "app.current_practice_id"
    admin_role = profile["postgres_user"]
    sql = f"""
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA {schema} AUTHORIZATION {admin_role};
CREATE TABLE {schema}.command_effect (
  practice_id uuid NOT NULL,
  command_id uuid NOT NULL,
  effect_id uuid NOT NULL,
  idempotency_identity text NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  effect_kind text NOT NULL,
  CONSTRAINT command_effect_pk PRIMARY KEY (practice_id, command_id),
  CONSTRAINT command_effect_id_uq UNIQUE (practice_id, effect_id),
  CONSTRAINT command_effect_packet_uq UNIQUE (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_effect_idempotency_uq UNIQUE (practice_id, idempotency_identity),
  CONSTRAINT command_effect_idem_ck CHECK (idempotency_identity ~ '^idem:authored-synthetic/[a-z0-9-]{{8,80}}$'),
  CONSTRAINT command_effect_digest_ck CHECK (request_sha256 ~ '^[0-9a-f]{{64}}$'),
  CONSTRAINT command_effect_kind_ck CHECK (effect_kind = 'check_in')
);
CREATE TABLE {schema}.command_receipt (
  practice_id uuid NOT NULL,
  command_id uuid NOT NULL,
  effect_id uuid NOT NULL,
  idempotency_identity text NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  outcome text NOT NULL,
  CONSTRAINT command_receipt_pk PRIMARY KEY (practice_id, command_id),
  CONSTRAINT command_receipt_idempotency_uq UNIQUE (practice_id, idempotency_identity),
  CONSTRAINT command_receipt_packet_uq UNIQUE (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_receipt_effect_fk FOREIGN KEY (practice_id, command_id, effect_id, idempotency_identity, request_sha256)
    REFERENCES {schema}.command_effect (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_receipt_idem_ck CHECK (idempotency_identity ~ '^idem:authored-synthetic/[a-z0-9-]{{8,80}}$'),
  CONSTRAINT command_receipt_digest_ck CHECK (request_sha256 ~ '^[0-9a-f]{{64}}$'),
  CONSTRAINT command_receipt_outcome_ck CHECK (outcome = 'committed')
);
CREATE TABLE {schema}.command_audit (
  practice_id uuid NOT NULL,
  command_id uuid NOT NULL,
  effect_id uuid NOT NULL,
  audit_id uuid NOT NULL,
  idempotency_identity text NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  action text NOT NULL,
  CONSTRAINT command_audit_pk PRIMARY KEY (practice_id, audit_id),
  CONSTRAINT command_audit_command_uq UNIQUE (practice_id, command_id),
  CONSTRAINT command_audit_idempotency_uq UNIQUE (practice_id, idempotency_identity),
  CONSTRAINT command_audit_receipt_fk FOREIGN KEY (practice_id, command_id, effect_id, idempotency_identity, request_sha256)
    REFERENCES {schema}.command_receipt (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_audit_idem_ck CHECK (idempotency_identity ~ '^idem:authored-synthetic/[a-z0-9-]{{8,80}}$'),
  CONSTRAINT command_audit_digest_ck CHECK (request_sha256 ~ '^[0-9a-f]{{64}}$'),
  CONSTRAINT command_audit_action_ck CHECK (action = 'check_in_committed')
);
ALTER TABLE {schema}.command_effect ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_effect FORCE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_receipt ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_receipt FORCE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_audit FORCE ROW LEVEL SECURITY;
CREATE POLICY command_effect_tenant ON {schema}.command_effect
  USING (practice_id = nullif(current_setting('{setting}', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('{setting}', true), '')::uuid);
CREATE POLICY command_receipt_tenant ON {schema}.command_receipt
  USING (practice_id = nullif(current_setting('{setting}', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('{setting}', true), '')::uuid);
CREATE POLICY command_audit_tenant ON {schema}.command_audit
  USING (practice_id = nullif(current_setting('{setting}', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('{setting}', true), '')::uuid);
CREATE ROLE {physical_role} LOGIN PASSWORD '{runtime_password}'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
GRANT CONNECT ON DATABASE {profile['postgres_database']} TO {physical_role};
GRANT USAGE ON SCHEMA {schema} TO {physical_role};
GRANT SELECT, INSERT ON {schema}.command_effect, {schema}.command_receipt, {schema}.command_audit TO {physical_role};
"""
    with admin.begin() as connection:
        for statement in [part.strip() for part in sql.split(";") if part.strip()]:
            connection.execute(text(statement))


def _catalogue(
    admin: Engine, *, physical_role: str, profile: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    with admin.connect() as connection:
        role = tuple(
            connection.execute(
                text(
                    "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
                    "rolinherit, rolreplication, rolbypassrls FROM pg_roles "
                    "WHERE rolname=:role"
                ),
                {"role": physical_role},
            ).one()
        )
        memberships = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM pg_auth_members m JOIN pg_roles r "
                    "ON r.oid=m.member WHERE r.rolname=:role"
                ),
                {"role": physical_role},
            ).scalar_one()
        )
        owned_objects = int(
            connection.execute(
                text(
                    "SELECT (SELECT count(*) FROM pg_database d JOIN pg_roles r ON r.oid=d.datdba WHERE r.rolname=:role) + "
                    "(SELECT count(*) FROM pg_namespace n JOIN pg_roles r ON r.oid=n.nspowner WHERE r.rolname=:role) + "
                    "(SELECT count(*) FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner WHERE r.rolname=:role) + "
                    "(SELECT count(*) FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner WHERE r.rolname=:role)"
                ),
                {"role": physical_role},
            ).scalar_one()
        )
        product_privileges = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM information_schema.table_privileges "
                    "WHERE grantee=:role AND table_schema <> 'check_in_recovery_probe'"
                ),
                {"role": physical_role},
            ).scalar_one()
        )
        grants = [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT table_name, privilege_type FROM information_schema.table_privileges "
                    "WHERE grantee=:role AND table_schema='check_in_recovery_probe' "
                    "ORDER BY table_name, privilege_type"
                ),
                {"role": physical_role},
            ).all()
        ]
        relations = [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT c.relname, r.rolname, c.relrowsecurity, c.relforcerowsecurity "
                    "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                    "JOIN pg_roles r ON r.oid=c.relowner "
                    "WHERE n.nspname='check_in_recovery_probe' AND c.relkind='r' "
                    "ORDER BY c.relname"
                )
            ).all()
        ]
        policies = [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT c.relname, p.polname, pg_get_expr(p.polqual,p.polrelid), "
                    "pg_get_expr(p.polwithcheck,p.polrelid) FROM pg_policy p "
                    "JOIN pg_class c ON c.oid=p.polrelid JOIN pg_namespace n ON n.oid=c.relnamespace "
                    "WHERE n.nspname='check_in_recovery_probe' ORDER BY c.relname"
                )
            ).all()
        ]
        constraints = set(
            connection.execute(
                text(
                    "SELECT conname FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
                    "WHERE n.nspname='check_in_recovery_probe'"
                )
            ).scalars()
        )
        public_usage = connection.execute(
            text("SELECT has_schema_privilege(:role, 'public', 'USAGE')"),
            {"role": physical_role},
        ).scalar_one()
    expected_role = (True, False, False, False, False, False, False)
    expected_relations = [
        (name, profile["postgres_user"], True, True)
        for name in ("command_audit", "command_effect", "command_receipt")
    ]
    expected_grants = [
        (name, privilege)
        for name in ("command_audit", "command_effect", "command_receipt")
        for privilege in ("INSERT", "SELECT")
    ]
    expected_constraints = {
        "command_effect_pk", "command_effect_id_uq", "command_effect_packet_uq",
        "command_effect_idempotency_uq", "command_effect_idem_ck",
        "command_effect_digest_ck", "command_effect_kind_ck", "command_receipt_pk",
        "command_receipt_idempotency_uq", "command_receipt_packet_uq",
        "command_receipt_effect_fk", "command_receipt_idem_ck",
        "command_receipt_digest_ck", "command_receipt_outcome_ck", "command_audit_pk",
        "command_audit_command_uq", "command_audit_idempotency_uq",
        "command_audit_receipt_fk", "command_audit_idem_ck",
        "command_audit_digest_ck", "command_audit_action_ck",
    }
    policy_matches = sum(
        int(
            row[2] == row[3]
            and "app.current_practice_id" in str(row[2])
            and row[1] == f"{row[0]}_tenant"
        )
        for row in policies
    )
    if (
        role != expected_role
        or memberships != 0
        or owned_objects != 0
        or product_privileges != 0
        or grants != expected_grants
        or relations != expected_relations
        or len(policies) != 3
        or policy_matches != 3
        or constraints != expected_constraints
        or public_usage is not False
    ):
        raise RehearsalFailure("catalogue", "role_or_relation_contract_mismatch")
    return (
        {
            "login": bool(role[0]),
            "superuser": bool(role[1]),
            "create_database": bool(role[2]),
            "create_role": bool(role[3]),
            "inherit": bool(role[4]),
            "replication": bool(role[5]),
            "bypass_rls": bool(role[6]),
            "memberships": memberships,
            "owned_objects": owned_objects,
            "product_relation_privileges": product_privileges,
            "probe_grants": ["INSERT", "SELECT"],
        },
        {
            "relations": [row[0] for row in relations],
            "admin_owned_count": 3,
            "rls_enabled_count": 3,
            "rls_forced_count": 3,
            "policy_count": len(policies),
            "policy_expression_match_count": policy_matches,
            "constraints_verified": True,
        },
    )


def _set_tenant(connection: Any, practice_id: str) -> None:
    observed = connection.execute(
        text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
        {"practice_id": practice_id},
    ).scalar_one()
    if observed != practice_id:
        raise RehearsalFailure("transaction", "transaction_local_practice_set_failed")


def _insert_packet(connection: Any, practice_id: str, command: dict[str, str]) -> None:
    common = {
        "practice_id": practice_id,
        "command_id": command["command_id"],
        "effect_id": command["effect_id"],
        "idempotency_identity": command["idempotency_identity"],
        "request_sha256": command["request_sha256"],
    }
    connection.execute(
        text(
            "INSERT INTO check_in_recovery_probe.command_effect "
            "(practice_id,command_id,effect_id,idempotency_identity,request_sha256,effect_kind) "
            "VALUES (:practice_id,:command_id,:effect_id,:idempotency_identity,:request_sha256,'check_in')"
        ),
        common,
    )
    connection.execute(
        text(
            "INSERT INTO check_in_recovery_probe.command_receipt "
            "(practice_id,command_id,effect_id,idempotency_identity,request_sha256,outcome) "
            "VALUES (:practice_id,:command_id,:effect_id,:idempotency_identity,:request_sha256,'committed')"
        ),
        common,
    )
    connection.execute(
        text(
            "INSERT INTO check_in_recovery_probe.command_audit "
            "(practice_id,command_id,effect_id,audit_id,idempotency_identity,request_sha256,action) "
            "VALUES (:practice_id,:command_id,:effect_id,:audit_id,:idempotency_identity,:request_sha256,'check_in_committed')"
        ),
        {**common, "audit_id": command["audit_id"]},
    )


def _string_row(row: Any) -> dict[str, Any]:
    return {
        str(key): str(value) if isinstance(value, uuid.UUID) else value
        for key, value in row._mapping.items()
    }


def readback_packet(connection: Any, command: dict[str, str]) -> dict[str, Any]:
    fields = {
        "effect": "practice_id,command_id,effect_id,idempotency_identity,request_sha256,effect_kind",
        "receipt": "practice_id,command_id,effect_id,idempotency_identity,request_sha256,outcome",
        "audit": "practice_id,command_id,effect_id,audit_id,idempotency_identity,request_sha256,action",
    }
    packet: dict[str, Any] = {}
    for member, relation in zip(PACKET_KEYS, RELATIONS, strict=True):
        rows = connection.execute(
            text(
                f"SELECT {fields[member]} FROM check_in_recovery_probe.{relation} "
                "WHERE command_id=:command_id OR idempotency_identity=:idempotency_identity "
                "ORDER BY command_id,idempotency_identity"
            ),
            {
                "command_id": command["command_id"],
                "idempotency_identity": command["idempotency_identity"],
            },
        ).all()
        packet[member] = [_string_row(row) for row in rows]
    return packet


def packet_counts(packet: dict[str, Any]) -> dict[str, int]:
    return {key: len(packet.get(key, [])) for key in PACKET_KEYS}


def _canonical_uuid(value: Any) -> bool:
    try:
        return str(uuid.UUID(str(value))) == value
    except (ValueError, TypeError, AttributeError):
        return False


def classify_readback(packet: Any, expected_request_sha256: str) -> str:
    denied = "unresolved_denied"
    if not isinstance(packet, dict) or set(packet) != set(PACKET_KEYS):
        return denied
    if any(not isinstance(packet[key], list) for key in PACKET_KEYS):
        return denied
    counts = packet_counts(packet)
    if counts == {"effect": 0, "receipt": 0, "audit": 0}:
        return "rolled_back_zero_effect"
    if counts != {"effect": 1, "receipt": 1, "audit": 1}:
        return denied
    effect = packet["effect"][0]
    receipt = packet["receipt"][0]
    audit = packet["audit"][0]
    expected_keys = {
        "effect": {"practice_id", "command_id", "effect_id", "idempotency_identity", "request_sha256", "effect_kind"},
        "receipt": {"practice_id", "command_id", "effect_id", "idempotency_identity", "request_sha256", "outcome"},
        "audit": {"practice_id", "command_id", "effect_id", "audit_id", "idempotency_identity", "request_sha256", "action"},
    }
    rows = {"effect": effect, "receipt": receipt, "audit": audit}
    if any(not isinstance(row, dict) or set(row) != expected_keys[name] for name, row in rows.items()):
        return denied
    shared = ("practice_id", "command_id", "effect_id", "idempotency_identity", "request_sha256")
    if any(effect[key] != receipt[key] or effect[key] != audit[key] for key in shared):
        return denied
    if not all(_canonical_uuid(effect[key]) for key in ("practice_id", "command_id", "effect_id")):
        return denied
    if not _canonical_uuid(audit["audit_id"]):
        return denied
    if (
        effect["request_sha256"] != expected_request_sha256
        or not re.fullmatch(r"[0-9a-f]{64}", expected_request_sha256)
        or not re.fullmatch(r"idem:authored-synthetic/[a-z0-9-]{8,80}", effect["idempotency_identity"])
        or effect["effect_kind"] != "check_in"
        or receipt["outcome"] != "committed"
        or audit["action"] != "check_in_committed"
    ):
        return denied
    return "committed_exactly_once"


def hostile_classifier_packets_rejected(
    packet: dict[str, Any], expected_request_sha256: str, threshold: int
) -> tuple[int, int]:
    candidates: list[dict[str, Any]] = []
    for member in PACKET_KEYS:
        duplicate = copy.deepcopy(packet)
        duplicate[member].append(copy.deepcopy(duplicate[member][0]))
        candidates.append(duplicate)
        missing = copy.deepcopy(packet)
        missing[member] = []
        candidates.append(missing)
    replacements = {
        "practice_id": "44444444-4444-4444-8444-444444444444",
        "command_id": "55555555-5555-4555-8555-555555555555",
        "effect_id": "66666666-6666-4666-8666-666666666666",
        "audit_id": "77777777-7777-4777-8777-777777777777",
        "idempotency_identity": "idem:authored-synthetic/hostile-mismatch-v1",
        "request_sha256": "0" * 64,
        "effect_kind": "status_change",
        "outcome": "unknown",
        "action": "other",
    }
    for member in PACKET_KEYS:
        for field in packet[member][0]:
            if field == "audit_id":
                continue
            candidate = copy.deepcopy(packet)
            candidate[member][0][field] = replacements[field]
            candidates.append(candidate)
    attempted = len(candidates)
    rejected = sum(
        classify_readback(candidate, expected_request_sha256) == "unresolved_denied"
        for candidate in candidates
    )
    if attempted < threshold or attempted != rejected:
        raise RehearsalFailure("classifier", "hostile_classifier_gate_failed")
    return attempted, rejected


def _ambiguous_worker(
    result_queue: Any,
    host_port: int,
    connection_profile: dict[str, Any],
    physical_role: str,
    runtime_password: str,
    application_label: str,
    practice_id: str,
    command: dict[str, str],
    hold_seconds: int,
) -> None:
    engine: Engine | None = None
    try:
        engine = _restricted_engine(
            host_port,
            connection_profile,
            physical_role,
            runtime_password,
            application_label,
        )
        with engine.connect() as connection:
            transaction = connection.begin()
            _set_tenant(connection, practice_id)
            _insert_packet(connection, practice_id, command)
            transaction.commit()
            connection.execute(text("SELECT pg_sleep(:hold_seconds)"), {"hold_seconds": hold_seconds})
        result_queue.put(
            {
                "outcome": "complete_terminal_response",
                "complete_terminal_response": True,
                "success_released": True,
                "retry_count": 0,
            }
        )
    except DBAPIError:
        result_queue.put(
            {
                "outcome": "connection_lost_without_complete_terminal_response",
                "complete_terminal_response": False,
                "success_released": False,
                "retry_count": 0,
            }
        )
    except Exception:
        result_queue.put(
            {
                "outcome": "closed_worker_failure",
                "complete_terminal_response": False,
                "success_released": False,
                "retry_count": 0,
            }
        )
    finally:
        if engine is not None:
            engine.dispose()


def _observe_and_terminate_sleep(
    admin: Engine,
    *,
    application_label: str,
    physical_role: str,
    database_name: str,
    timeout_seconds: int,
) -> str:
    deadline = time.monotonic() + timeout_seconds
    observed_pid: int | None = None
    while time.monotonic() < deadline:
        with admin.connect() as connection:
            rows = connection.execute(
                text(
                    "SELECT pid,state,wait_event_type,wait_event FROM pg_stat_activity "
                    "WHERE application_name=:application_label AND usename=:role "
                    "AND datname=:database_name"
                ),
                {
                    "application_label": application_label,
                    "role": physical_role,
                    "database_name": database_name,
                },
            ).all()
        if len(rows) > 1:
            raise RehearsalFailure("ambiguous_response", "worker_session_not_unique")
        if len(rows) == 1 and tuple(rows[0][1:]) == ("active", "Timeout", "PgSleep"):
            observed_pid = int(rows[0][0])
            break
        time.sleep(0.05)
    if observed_pid is None:
        raise RehearsalFailure("ambiguous_response", "post_commit_sleep_not_observed")
    with admin.begin() as connection:
        terminated = connection.execute(
            text("SELECT pg_terminate_backend(:target_pid)"),
            {"target_pid": observed_pid},
        ).scalar_one()
    if terminated is not True:
        raise RehearsalFailure("ambiguous_response", "exact_backend_termination_failed")
    return "Timeout/PgSleep"


def _drop_role(admin: Engine, physical_role: str) -> bool:
    if not re.fullmatch(r"emr4_checkin_ruc_[0-9a-f]{16}", physical_role):
        return False
    with admin.begin() as connection:
        connection.execute(text(f"DROP OWNED BY {physical_role}"))
        connection.execute(text(f"DROP ROLE {physical_role}"))
        remaining = connection.execute(
            text("SELECT count(*) FROM pg_roles WHERE rolname=:role"),
            {"role": physical_role},
        ).scalar_one()
    return remaining == 0


def _scenario(identifier: str, observed: str | int | bool) -> dict[str, Any]:
    return {"id": identifier, "status": "passed", "observed": observed}


def _failure_evidence(
    error: RehearsalFailure, lifecycle: list[str], cleanup: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.check-in-rollback-unknown-response-rehearsal-failure.v1",
        "result": "rehearsal_failed",
        "evidence_label": EVIDENCE_LABEL,
        "source_head": SOURCE_HEAD,
        "failure": {
            "stage": error.stage,
            "code": error.code,
            "detail_sha256": _sha256(error.detail),
        },
        "lifecycle": lifecycle,
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal() -> tuple[dict[str, Any], dict[str, Any] | None]:
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {"status": "not_needed"}
    contract: dict[str, Any] | None = None
    source_hashes: dict[str, str] = {}
    contract_mutations = (0, 0)
    manifest_mutations = (0, 0)
    classifier_mutations = (0, 0)
    docker = ""
    image_id: str | None = None
    network_id: str | None = None
    container_id: str | None = None
    network_name = ""
    container_name = ""
    nonce = secrets.token_hex(16)
    physical_role = "emr4_checkin_ruc_" + secrets.token_hex(8)
    admin_password = secrets.token_hex(32)
    runtime_password = secrets.token_hex(32)
    role_created = False
    role_absent = False
    admin: Engine | None = None
    application: Engine | None = None
    relay: foundation.DockerExecRelay | None = None
    worker: multiprocessing.Process | None = None
    worker_queue: Any = None
    attestation: dict[str, Any] | None = None
    error: RehearsalFailure | None = None
    profile: dict[str, Any] | None = None
    started = time.monotonic()
    try:
        contract, source_hashes, contract_mutations = verify_contract()
        lifecycle.append("contract_sources_and_hostile_mutations_verified")
        manifest = build_manifest(contract, physical_role)
        _validate_manifest(manifest, physical_role=physical_role, canonical=manifest)
        manifest_mutations = hostile_manifest_mutations_rejected(
            manifest, physical_role, contract["hostile_thresholds"]["manifest"]
        )
        manifest_sha256 = _sha256(_json_bytes(manifest))
        lifecycle.append("closed_transaction_manifest_and_mutations_verified")
        docker = shutil.which(contract["containment_profile"]["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        profile = _runtime_profile(contract, admin_password)
        image_id = foundation._image_id(docker, profile)  # noqa: SLF001
        lifecycle.append("cached_postgresql_16_image_verified")
        suffix = secrets.token_hex(8)
        network_name = profile["network_name_prefix"] + suffix
        container_name = profile["container_name_prefix"] + suffix
        network_result = catalogue._run(  # noqa: SLF001
            foundation.build_network_argv(docker, network_name, nonce, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        network_id = network_result.stdout.decode("utf-8").strip()
        if network_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", network_id):
            raise RehearsalFailure("environment", "network_create_failed")
        network_inspect, inspected_network = foundation._inspect_one(  # noqa: SLF001
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if (
            network_inspect.returncode != 0
            or inspected_network is None
            or not foundation._network_owned(  # noqa: SLF001
                inspected_network,
                network_id=network_id,
                name=network_name,
                nonce=nonce,
                profile=profile,
                require_empty=True,
            )
        ):
            raise RehearsalFailure("environment", "network_profile_mismatch")
        lifecycle.append("owned_internal_network_verified")
        container_result = catalogue._run(  # noqa: SLF001
            foundation.build_container_argv(docker, container_name, nonce, network_id, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        container_id = container_result.stdout.decode("utf-8").strip()
        if container_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("environment", "container_create_failed")
        container_inspect, inspected_container = foundation._inspect_one(  # noqa: SLF001
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        if (
            container_inspect.returncode != 0
            or inspected_container is None
            or not foundation._container_profile(  # noqa: SLF001
                inspected_container,
                container_id=container_id,
                name=container_name,
                nonce=nonce,
                image_id=image_id,
                network_id=network_id,
                profile=profile,
            )
        ):
            raise RehearsalFailure("environment", "container_profile_mismatch")
        lifecycle.append("owned_tmpfs_container_verified")
        foundation._wait_ready(docker, container_id, profile)  # noqa: SLF001
        lifecycle.append("postgresql_16_readiness_verified")
        relay = EOFPropagatingDockerExecRelay(docker, container_id, profile)
        host_port = relay.start()
        lifecycle.append("fixed_loopback_relay_started")
        admin = foundation._engine(host_port, profile)  # noqa: SLF001
        _install_probe(
            admin,
            profile=profile,
            physical_role=physical_role,
            runtime_password=runtime_password,
        )
        role_created = True
        lifecycle.append("admin_owned_three_relation_forced_rls_probe_installed")
        application = _restricted_engine(
            host_port,
            profile,
            physical_role,
            runtime_password,
            "emr4_checkin_read_" + secrets.token_hex(8),
        )
        role_catalogue, relation_catalogue = _catalogue(
            admin, physical_role=physical_role, profile=profile
        )
        lifecycle.append("restricted_role_relation_and_policy_catalogue_verified")
        practice_id = manifest["practice_id"]
        rollback_command = manifest["commands"]["rollback"]
        with application.connect() as connection:
            transaction = connection.begin()
            _set_tenant(connection, practice_id)
            _insert_packet(connection, practice_id, rollback_command)
            staged_packet = readback_packet(connection, rollback_command)
            staged_counts = packet_counts(staged_packet)
            if staged_counts != {"effect": 1, "receipt": 1, "audit": 1}:
                raise RehearsalFailure("rollback", "staged_packet_incomplete")
            transaction.rollback()
        lifecycle.append("rollback_three_member_packet_staged_then_explicitly_rolled_back")
        with application.begin() as connection:
            _set_tenant(connection, practice_id)
            rollback_packet = readback_packet(connection, rollback_command)
        rollback_counts = packet_counts(rollback_packet)
        rollback_classification = classify_readback(
            rollback_packet, rollback_command["request_sha256"]
        )
        if (
            rollback_counts != {"effect": 0, "receipt": 0, "audit": 0}
            or rollback_classification != "rolled_back_zero_effect"
        ):
            raise RehearsalFailure("rollback", "rollback_zero_effect_unproved")
        lifecycle.append("fresh_restricted_role_rollback_zero_effect_readback_verified")
        ambiguous_command = manifest["commands"]["ambiguous_response"]
        application_label = "emr4_checkin_ruc_" + secrets.token_hex(8)
        context = multiprocessing.get_context("spawn")
        worker_queue = context.Queue(maxsize=1)
        connection_profile = {
            "sqlalchemy_driver": profile["sqlalchemy_driver"],
            "relay_host_ip": profile["relay_host_ip"],
            "postgres_database": profile["postgres_database"],
        }
        worker = context.Process(
            target=_ambiguous_worker,
            args=(
                worker_queue,
                host_port,
                connection_profile,
                physical_role,
                runtime_password,
                application_label,
                practice_id,
                ambiguous_command,
                profile["post_commit_hold_seconds"],
            ),
        )
        worker.start()
        wait_observed = _observe_and_terminate_sleep(
            admin,
            application_label=application_label,
            physical_role=physical_role,
            database_name=profile["postgres_database"],
            timeout_seconds=profile["wait_observation_timeout_seconds"],
        )
        lifecycle.append("exact_post_commit_timeout_pgsleep_session_observed")
        try:
            caller_outcome = worker_queue.get(
                timeout=profile["worker_join_timeout_seconds"]
            )
        except queue.Empty as caught:
            raise RehearsalFailure("ambiguous_response", "worker_outcome_missing") from caught
        worker.join(5)
        if worker.is_alive():
            raise RehearsalFailure("ambiguous_response", "worker_exit_timeout")
        if worker.exitcode != 0:
            raise RehearsalFailure("ambiguous_response", "worker_exit_nonzero")
        expected_caller = {
            "outcome": "connection_lost_without_complete_terminal_response",
            "complete_terminal_response": False,
            "success_released": False,
            "retry_count": 0,
        }
        if caller_outcome != expected_caller:
            raise RehearsalFailure("ambiguous_response", "caller_failed_closed_outcome_mismatch")
        lifecycle.append("caller_connection_loss_released_no_success_and_no_retry")
        with application.begin() as connection:
            _set_tenant(connection, practice_id)
            ambiguous_packet = readback_packet(connection, ambiguous_command)
        ambiguous_counts = packet_counts(ambiguous_packet)
        ambiguous_classification = classify_readback(
            ambiguous_packet, ambiguous_command["request_sha256"]
        )
        if (
            ambiguous_counts != {"effect": 1, "receipt": 1, "audit": 1}
            or ambiguous_classification != "committed_exactly_once"
        ):
            raise RehearsalFailure("readback", "committed_exactly_once_unproved")
        lifecycle.append("fresh_restricted_role_complete_packet_readback_verified")
        classifier_mutations = hostile_classifier_packets_rejected(
            ambiguous_packet,
            ambiguous_command["request_sha256"],
            contract["hostile_thresholds"]["classifier"],
        )
        lifecycle.append("hostile_partial_duplicate_and_mismatched_packets_denied")
        application.dispose()
        application = None
        role_absent = _drop_role(admin, physical_role)
        if not role_absent:
            raise RehearsalFailure("cleanup", "role_absence_unverified")
        role_created = False
        lifecycle.append("physical_role_absent_before_teardown")
        scenarios = [
            _scenario("RUC-S01", len(source_hashes)),
            _scenario("RUC-S02", manifest_sha256),
            _scenario("RUC-S03", relation_catalogue["constraints_verified"]),
            _scenario("RUC-S04", sum(staged_counts.values())),
            _scenario("RUC-S05", rollback_classification),
            _scenario("RUC-S06", wait_observed),
            _scenario("RUC-S07", caller_outcome["outcome"]),
            _scenario("RUC-S08", sum(ambiguous_counts.values())),
            _scenario("RUC-S09", ambiguous_classification),
            _scenario("RUC-S10", classifier_mutations[1]),
            _scenario("RUC-S11", 0),
            _scenario("RUC-S12", True),
        ]
        if tuple(item["id"] for item in scenarios) != EXPECTED_SCENARIOS:
            raise RehearsalFailure("scenario", "scenario_release_order_mismatch")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        attestation = {
            "schema_version": "emr4.check-in-rollback-unknown-response-transaction-attestation.v1",
            "evidence_reference": "evidence-ref:authored-synthetic/check-in-rollback-unknown-response-transaction-attestation",
            "evidence_label": EVIDENCE_LABEL,
            "authority_git_object": manifest["authority_git_object"],
            "accepted_runtime_role_source": contract["accepted_runtime_role_source"],
            "environment_identifier": manifest["environment_identifier"],
            "practice_scope_reference": manifest["practice_scope_reference"],
            "manifest_sha256": manifest_sha256,
            "logical_role_id": manifest["logical_role_id"],
            "physical_role_identifier": physical_role,
            "role_catalogue": role_catalogue,
            "relation_catalogue": relation_catalogue,
            "transaction_outcomes": {
                "explicit_rollback": {
                    "staged_counts": staged_counts,
                    "readback_counts": rollback_counts,
                    "packet_sha256": _sha256(_json_bytes(rollback_packet)),
                    "classification": rollback_classification,
                },
                "ambiguous_response": {
                    "caller_outcome": caller_outcome["outcome"],
                    "complete_terminal_response": caller_outcome["complete_terminal_response"],
                    "success_released": caller_outcome["success_released"],
                    "retry_count": caller_outcome["retry_count"],
                    "post_commit_wait": wait_observed,
                    "backend_termination": "exact_observed_session_only",
                    "readback_counts": ambiguous_counts,
                    "packet_sha256": _sha256(_json_bytes(ambiguous_packet)),
                    "classification": ambiguous_classification,
                },
            },
            "hostile_classifier": {
                "attempted": classifier_mutations[0],
                "rejected": classifier_mutations[1],
                "escapes": 0,
            },
            "scenarios": scenarios,
            "role_absent_before_teardown": True,
            "ordinary_admission_release_count": 0,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        _assert_redacted(attestation, forbidden_values=(admin_password, runtime_password))
        Draft202012Validator(_load_json(ATTESTATION_SCHEMA_PATH)).validate(attestation)
    except RehearsalFailure as caught:
        lifecycle.append(f"failed_{caught.stage}_{caught.code}")
        error = caught
    except Exception as caught:
        sqlstate = predecessor._sqlstate(caught)  # noqa: SLF001
        lifecycle.append(f"failed_harness_{type(caught).__name__}_{sqlstate}")
        error = RehearsalFailure(
            "harness", "unexpected_exception", f"{type(caught).__name__}:{sqlstate}"
        )
    finally:
        if worker is not None and worker.is_alive():
            worker.terminate()
            worker.join(5)
            lifecycle.append("failure_path_worker_terminated")
        if worker_queue is not None:
            worker_queue.close()
            worker_queue.join_thread()
        if application is not None:
            application.dispose()
        if admin is not None and role_created:
            try:
                role_absent = _drop_role(admin, physical_role)
                if role_absent:
                    lifecycle.append("failure_path_physical_role_absent")
            except Exception:
                lifecycle.append("failure_path_role_cleanup_unverified")
        if admin is not None:
            admin.dispose()
        if relay is not None:
            relay.stop()
            lifecycle.append("fixed_loopback_relay_stopped")
        if contract is not None and docker and profile is not None:
            cleanup = foundation._cleanup(  # noqa: SLF001
                docker,
                container_id=container_id,
                container_name=container_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
                image_id=image_id,
                profile=profile,
            )
        cleanup["role_absent_before_teardown"] = role_absent
        if cleanup.get("status") == "cleanup_verified":
            lifecycle.append("captured_container_and_network_absent")
        if error is None and (
            cleanup.get("status") != "cleanup_verified" or not role_absent
        ):
            error = RehearsalFailure("cleanup", "exact_cleanup_unverified")
    if error is not None:
        failure = _failure_evidence(error, lifecycle, cleanup)
        _assert_redacted(failure, forbidden_values=(admin_password, runtime_password))
        return failure, None
    assert contract is not None and attestation is not None and image_id is not None
    evidence = {
        "schema_version": "emr4.check-in-rollback-unknown-response-rehearsal-evidence.v1",
        "result": PASS_RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "source_head": contract["source_head"],
        "accepted_runtime_role_source": contract["accepted_runtime_role_source"],
        "contract_sha256": _sha256(_canonical_source_bytes(CONTRACT_PATH)),
        "source_hashes": source_hashes,
        "manifest_sha256": attestation["manifest_sha256"],
        "attestation_artifact": str(ATTESTATION_PATH.relative_to(ROOT)).replace("\\", "/"),
        "attestation_sha256": _sha256(_json_bytes(attestation)),
        "hostile_mutations": {
            "contract_attempted": contract_mutations[0],
            "contract_rejected": contract_mutations[1],
            "manifest_attempted": manifest_mutations[0],
            "manifest_rejected": manifest_mutations[1],
            "classifier_attempted": classifier_mutations[0],
            "classifier_rejected": classifier_mutations[1],
            "escapes": 0,
        },
        "environment": {
            "postgresql_major": 16,
            "image_reference": contract["containment_profile"]["image_reference"],
            "image_id_sha256": _sha256(image_id),
            "network_internal": True,
            "published_ports": False,
            "storage": "container_local_tmpfs",
            "host_transport": "fixed_in_process_ipv4_loopback_relay",
            "provider_calls": 0,
            "product_rows": 0,
            "live_secrets": 0,
            "automatic_retries": 0,
        },
        "lifecycle": lifecycle,
        "cleanup": cleanup,
        "closed_boundaries": contract["closed_boundaries"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _assert_redacted(evidence, forbidden_values=(admin_password, runtime_password))
    Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence, attestation


def write_evidence(
    evidence: dict[str, Any], attestation: dict[str, Any] | None
) -> Path:
    BASE.mkdir(parents=True, exist_ok=True)
    if evidence["result"] == PASS_RESULT:
        assert attestation is not None
        ATTESTATION_PATH.write_bytes(_json_bytes(attestation))
        EVIDENCE_PATH.write_bytes(_json_bytes(evidence))
        return EVIDENCE_PATH
    payload = _json_bytes(evidence)
    attempt_path: Path | None = None
    for attempt in range(1, 100):
        candidate = BASE / f"rehearsal-failure-evidence-attempt-{attempt:03d}.json"
        if not candidate.exists():
            attempt_path = candidate
            break
    if attempt_path is None:
        raise RehearsalFailure("evidence", "failure_attempt_namespace_exhausted")
    attempt_path.write_bytes(payload)
    FAILURE_PATH.write_bytes(payload)
    return attempt_path


def main() -> int:
    if len(sys.argv) != 1:
        print('{"result":"rehearsal_failed","code":"caller_arguments_forbidden"}')
        return 2
    evidence, attestation = run_rehearsal()
    target = write_evidence(evidence, attestation)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cleanup": evidence["cleanup"].get("status"),
                "evidence": str(target.relative_to(ROOT)).replace("\\", "/"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
