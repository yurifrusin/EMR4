"""Run one fixed disposable PostgreSQL delete-confirm catalogue rehearsal.

The harness accepts no caller-selected input. It can operate only one uniquely
named, labelled, networkless, tmpfs-backed local PostgreSQL 16 container and
removes only the exact captured container ID after ownership re-verification.

This rehearsal proves empty-instance representation only: exact offline
lowering, one atomic installation, exact catalogue/function/trigger shape and
zero-row authority relations. It runs no behavior probe, inserts no user,
capability grant, receipt, audit or appointment row and grants no capability.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-scaffold-parse-catalogue-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-disposable-postgresql-evidence.json"
FAILURE_EVIDENCE_PATH = BASE / (
    "provider-free-disposable-postgresql-failure-evidence.json"
)
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_delete_confirm_scaffold_"
    "parse_catalogue_rehearsal_pass"
)
EXPECTED_CONTRACT_DIGEST = (
    "31c6f814ba5fbdd1a9c1e5ddc15c5446ffa2197f101aa6e0deee5072406be288"
)
HOSTILE_MUTATION_TARGET = 80
CLAIM_BOUNDARY = (
    "Exact delete-confirm migration parse/catalogue and empty authored-synthetic "
    "database invariants only; no full application schema, route, command, "
    "behavior probe, product data, concurrency, restart, unknown-commit, "
    "deployment or production claim."
)

SOURCE_HEAD = "38f2fbb054736cbd63627daea6951d676907461c"
EVIDENCE_SCHEMA_VERSION = "raisa.delete_confirm_scaffold_parse_catalogue_evidence.v1"

PREREQUISITE_SQL = """
CREATE TABLE public.users (
    id uuid PRIMARY KEY,
    practice_id uuid NOT NULL,
    role text NOT NULL,
    is_active boolean NOT NULL
);
CREATE TABLE public.appointment_command_idempotency (
    id uuid PRIMARY KEY,
    practice_id uuid NOT NULL,
    actor_user_id varchar(64) NOT NULL,
    actor_role varchar(64) NOT NULL,
    operation_id varchar(100) NOT NULL,
    route_family varchar(100) NOT NULL,
    idempotency_key_hash varchar(128) NOT NULL,
    request_body_hash varchar(128) NOT NULL,
    request_body_canonicalization_version integer NOT NULL DEFAULT 1,
    state varchar(32) NOT NULL,
    response_status_code integer,
    response_body_hash varchar(128),
    response_body_json jsonb,
    result_kind varchar(50),
    target_appointment_id uuid,
    audit_log_id uuid,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz,
    completed_receipt_version smallint,
    session_binding_digest bytea,
    pre_state_version bigint,
    post_state_version bigint,
    response_body_canonical_bytes bytea,
    CONSTRAINT ck_appt_cmd_idem_receipt_version CHECK (
        completed_receipt_version IS NULL OR completed_receipt_version = 1
    ),
    CONSTRAINT ck_appt_cmd_idem_status_receipt_v1_complete CHECK (
        completed_receipt_version IS NULL OR
        (state = 'completed' AND
         operation_id = 'confirmAppointmentStatusProposal' AND
         route_family = 'status-confirm' AND
         result_kind = 'confirmed_write' AND
         session_binding_digest IS NOT NULL AND
         octet_length(session_binding_digest) = 32 AND
         pre_state_version IS NOT NULL AND pre_state_version >= 1 AND
         post_state_version IS NOT NULL AND
         post_state_version = pre_state_version + 1 AND
         response_body_canonical_bytes IS NOT NULL AND
         octet_length(response_body_canonical_bytes) > 0 AND
         target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND
         response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND
         response_body_json IS NOT NULL)
    )
);
CREATE TABLE public.appointment_audit_log (
    id uuid PRIMARY KEY,
    action text NOT NULL,
    command_id uuid,
    status_after text,
    status_reason_code varchar(50),
    confirmed_warnings jsonb
);
CREATE TABLE public.alembic_version (
    version_num varchar(32) NOT NULL PRIMARY KEY
);
INSERT INTO public.alembic_version(version_num) VALUES ('w2x3y4z5a6b7');
""".strip() + "\n"


CATALOGUE_SQL = """
SELECT json_build_object(
  'head', (SELECT version_num FROM public.alembic_version),
  'columns', (
    SELECT json_agg(row_to_json(x) ORDER BY x.table_name, x.ordinal)
    FROM (
      SELECT c.relname AS table_name, a.attnum AS ordinal, a.attname AS name,
             t.typname AS type, NOT a.attnotnull AS nullable,
             pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default
      FROM pg_catalog.pg_attribute a
      JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
      JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
      JOIN pg_catalog.pg_type t ON t.oid = a.atttypid
      LEFT JOIN pg_catalog.pg_attrdef d
        ON d.adrelid = a.attrelid AND d.adnum = a.attnum
      WHERE n.nspname = 'public'
        AND ((c.relname = 'users'
              AND a.attname = 'authority_generation')
          OR (c.relname = 'user_capability_grants'
              AND a.attname IN ('practice_id', 'user_id', 'capability_code'))
          OR (c.relname = 'appointment_command_idempotency'
              AND a.attname = 'authority_generation')
          OR (c.relname = 'appointment_audit_log'
              AND a.attname IN ('audit_contract_version',
                                'authority_generation',
                                'pre_state_version', 'post_state_version',
                                'waiting_area_before_id',
                                'waiting_area_after_id',
                                'audit_evidence_codes')))
        AND a.attnum > 0 AND NOT a.attisdropped
    ) x
  ),
  'constraints', (
    SELECT json_agg(row_to_json(x) ORDER BY x.name)
    FROM (
      SELECT c.relname AS table_name, con.conname AS name,
             pg_catalog.pg_get_constraintdef(con.oid, true) AS definition
      FROM pg_catalog.pg_constraint con
      JOIN pg_catalog.pg_class c ON c.oid = con.conrelid
      JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
      WHERE n.nspname = 'public'
        AND con.conname IN ('ck_users_authority_generation_positive',
          'uq_users_practice_id_id', 'pk_user_capability_grants',
          'fk_user_capability_grants_user',
          'ck_user_capability_grants_capability_code',
          'ck_appt_cmd_idem_status_receipt_v1_complete',
          'ck_appt_audit_log_delete_v1_complete')
    ) x
  ),
  'index', (
    SELECT json_agg(row_to_json(x) ORDER BY x.name)
    FROM (
      SELECT c.relname AS name,
             pg_catalog.pg_get_indexdef(i.indexrelid, 0, true) AS definition
      FROM pg_catalog.pg_index i
      JOIN pg_catalog.pg_class c ON c.oid = i.indexrelid
      JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
      JOIN pg_catalog.pg_class t ON t.oid = i.indrelid
      JOIN pg_catalog.pg_namespace tn ON tn.oid = t.relnamespace
      WHERE n.nspname = 'public' AND tn.nspname = 'public'
        AND c.relname = 'ix_user_capability_grants_user'
    ) x
  ),
  'functions', (
    SELECT json_agg(row_to_json(x) ORDER BY x.name)
    FROM (
      SELECT n.nspname AS schema, p.proname AS name,
             pg_catalog.pg_get_function_identity_arguments(p.oid) AS arguments,
             pg_catalog.pg_get_function_result(p.oid) AS result,
             l.lanname AS language, p.prosecdef AS security_definer,
             p.provolatile AS volatility,
             pg_catalog.pg_get_functiondef(p.oid) AS definition
      FROM pg_catalog.pg_proc p
      JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
      JOIN pg_catalog.pg_language l ON l.oid = p.prolang
      WHERE n.nspname = 'public'
        AND p.proname IN ('emr4_user_authority_generation_guard',
          'emr4_user_capability_grant_generation_guard',
          'emr4_reject_user_capability_grant_update')
        AND pg_catalog.pg_get_function_identity_arguments(p.oid) = ''
    ) x
  ),
  'triggers', (
    SELECT json_agg(row_to_json(x) ORDER BY x.name)
    FROM (
      SELECT tg.tgname AS name, tg.tgenabled AS enabled,
             tg.tgisinternal AS internal, c.relname AS table_name,
             pg_catalog.pg_get_triggerdef(tg.oid, true) AS definition
      FROM pg_catalog.pg_trigger tg
      JOIN pg_catalog.pg_class c ON c.oid = tg.tgrelid
      JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
      WHERE n.nspname = 'public'
        AND tg.tgname IN ('trg_users_authority_generation_guard',
          'trg_user_capability_grants_generation',
          'trg_user_capability_grants_reject_update')
        AND NOT tg.tgisinternal
    ) x
  ),
  'unexpected_function_count', (
    SELECT count(*) FROM pg_catalog.pg_proc p
    JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
      AND p.proname LIKE 'emr4\\_user\\_%'
      AND p.proname NOT IN ('emr4_user_authority_generation_guard',
        'emr4_user_capability_grant_generation_guard',
        'emr4_reject_user_capability_grant_update')
  ),
  'unexpected_trigger_count', (
    SELECT count(*) FROM pg_catalog.pg_trigger tg
    JOIN pg_catalog.pg_class c ON c.oid = tg.tgrelid
    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND c.relname IN ('users', 'user_capability_grants')
      AND NOT tg.tgisinternal
      AND tg.tgname NOT IN ('trg_users_authority_generation_guard',
        'trg_user_capability_grants_generation',
        'trg_user_capability_grants_reject_update')
  ),
  'zero_rows', (
    SELECT json_build_object(
      'users', (SELECT count(*) FROM public.users),
      'user_capability_grants', (SELECT count(*) FROM public.user_capability_grants),
      'appointment_command_idempotency', (SELECT count(*) FROM public.appointment_command_idempotency),
      'appointment_audit_log', (SELECT count(*) FROM public.appointment_audit_log)
    )
  )
)::text;
""".strip() + "\n"


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: bytes | str = b"") -> None:
        super().__init__(f"{stage}:{code}")
        self.stage = stage
        self.code = code
        self.detail = detail.encode("utf-8") if isinstance(detail, str) else detail


Runner = Callable[[list[str], bytes | None, int, int], ProcessResult]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return _sha256(payload)


def _run(
    argv: list[str], stdin: bytes | None, timeout: int, cap: int
) -> ProcessResult:
    completed = subprocess.run(
        argv,
        input=stdin,
        cwd=ROOT,
        env=os.environ.copy(),
        shell=False,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return ProcessResult(
        completed.returncode,
        completed.stdout[:cap],
        completed.stderr[:cap],
    )


def _load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    if isinstance(value, dict):
        return [
            path
            for key, child in value.items()
            for path in _leaf_paths(child, (*prefix, key))
        ]
    if isinstance(value, list):
        return [
            path
            for index, child in enumerate(value)
            for path in _leaf_paths(child, (*prefix, index))
        ]
    return [prefix]


def _mutate_leaf(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return value + "-hostile"
    if value is None:
        return "hostile"
    raise TypeError(type(value).__name__)


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    rejected = 0
    for path in _leaf_paths(contract)[:HOSTILE_MUTATION_TARGET]:
        candidate = copy.deepcopy(contract)
        parent = candidate
        for component in path[:-1]:
            parent = parent[component]
        parent[path[-1]] = _mutate_leaf(parent[path[-1]])
        if _canonical_digest(candidate) != EXPECTED_CONTRACT_DIGEST:
            rejected += 1
    return rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str]]:
    contract = _load_contract()
    if _canonical_digest(contract) != EXPECTED_CONTRACT_DIGEST:
        raise RehearsalFailure("preflight", "contract_digest_mismatch")
    if contract.get("result") != PASS_RESULT:
        raise RehearsalFailure("preflight", "contract_result_mismatch")
    if hostile_mutations_rejected(contract) != HOSTILE_MUTATION_TARGET:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(path.read_bytes())
        observed[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure(
                "preflight", "source_hash_mismatch", binding["path"]
            )
    return contract, observed


def _generate_offline_sql(contract: dict[str, Any]) -> bytes:
    env = os.environ.copy()
    env["DATABASE_URL"] = contract["alembic"]["synthetic_url"]
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "upgrade",
            contract["alembic"]["offline_range"],
            "--sql",
        ],
        cwd=ROOT,
        env=env,
        shell=False,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise RehearsalFailure("offline_sql", "alembic_generation_failed")
    sql = completed.stdout.replace(b"\r\n", b"\n")
    if b"\r" in sql:
        raise RehearsalFailure("offline_sql", "lone_carriage_return")
    start = b"BEGIN;\n\n"
    end = b"COMMIT;\n\n"
    if not sql.startswith(start) or not sql.endswith(end):
        raise RehearsalFailure("offline_sql", "outer_transaction_shape_invalid")
    if sql.count(b"BEGIN;") != 1 or sql.count(b"COMMIT;") != 1:
        raise RehearsalFailure("offline_sql", "transaction_token_count_invalid")
    body = sql[len(start) : -len(end)]
    required = (
        b"-- Running upgrade w2x3y4z5a6b7 -> x3y4z5a6b7c8",
        b"ALTER TABLE users ADD COLUMN authority_generation BIGINT",
        b"UPDATE public.users SET authority_generation = 1",
        b"ck_users_authority_generation_positive",
        b"uq_users_practice_id_id",
        b"CREATE TABLE user_capability_grants",
        b"pk_user_capability_grants",
        b"fk_user_capability_grants_user",
        b"ck_user_capability_grants_capability_code",
        b"CREATE INDEX ix_user_capability_grants_user",
        b"CREATE FUNCTION public.emr4_user_authority_generation_guard()",
        b"CREATE TRIGGER trg_users_authority_generation_guard",
        b"CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()",
        b"CREATE TRIGGER trg_user_capability_grants_generation",
        b"CREATE FUNCTION public.emr4_reject_user_capability_grant_update()",
        b"CREATE TRIGGER trg_user_capability_grants_reject_update",
        b"ALTER TABLE appointment_command_idempotency ADD COLUMN authority_generation BIGINT",
        b"ck_appt_cmd_idem_status_receipt_v1_complete",
        b"confirmAppointmentDeleteProposal",
        b"route_family = 'delete-confirm'",
        b"ALTER TABLE appointment_audit_log ADD COLUMN audit_contract_version SMALLINT",
        b"ck_appt_audit_log_delete_v1_complete",
        b"jsonb_typeof(confirmed_warnings) = 'array'",
        b"UPDATE alembic_version SET version_num='x3y4z5a6b7c8'",
    )
    if any(token not in body for token in required):
        raise RehearsalFailure("offline_sql", "required_statement_missing")
    if b"DROP TABLE" in body or b"CREATE DATABASE" in body:
        raise RehearsalFailure("offline_sql", "unexpected_statement")
    return body


def build_container_argv(
    docker: str, name: str, nonce: str, contract: dict[str, Any]
) -> list[str]:
    profile = contract["docker_profile"]
    return [
        docker,
        "run",
        "--detach",
        "--pull",
        "never",
        "--network",
        "none",
        "--name",
        name,
        "--label",
        f"com.emr4.harness={profile['harness_label']}",
        "--label",
        f"com.emr4.cleanup-nonce={nonce}",
        "--tmpfs",
        f"{profile['data_destination']}:{profile['tmpfs_options']}",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--pids-limit",
        str(profile["pids_limit"]),
        "--restart",
        "no",
        "--env",
        f"POSTGRES_USER={profile['postgres_user']}",
        "--env",
        f"POSTGRES_PASSWORD={profile['postgres_password']}",
        "--env",
        f"POSTGRES_DB={profile['postgres_database']}",
        "--env",
        f"PGDATA={profile['pgdata']}",
        profile["image_reference"],
    ]


def _inspect(
    runner: Runner, docker: str, target: str, timeout: int
) -> tuple[ProcessResult, dict[str, Any] | None]:
    result = runner(
        [docker, "container", "inspect", target], None, timeout, 256_000
    )
    if result.returncode != 0:
        return result, None
    try:
        payload = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return result, None
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        return result, None
    return result, payload[0]


def _container_owned(
    inspect: dict[str, Any],
    *,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> bool:
    try:
        config = inspect["Config"]
        host = inspect["HostConfig"]
        mounts = inspect["Mounts"]
        labels = config["Labels"]
        env = set(config["Env"])
        required_env = {
            f"POSTGRES_USER={profile['postgres_user']}",
            f"POSTGRES_PASSWORD={profile['postgres_password']}",
            f"POSTGRES_DB={profile['postgres_database']}",
            f"PGDATA={profile['pgdata']}",
        }
        tmpfs = host["Tmpfs"]
        expected_tmpfs = tmpfs.get(profile["data_destination"])
        mount_ok = mounts == [] or (
            len(mounts) == 1
            and mounts[0].get("Type") == "tmpfs"
            and mounts[0].get("Destination") == profile["data_destination"]
        )
        return bool(
            inspect["Id"] == container_id
            and inspect["Name"] == "/" + name
            and inspect["Image"] == image_id
            and config["Image"] == profile["image_reference"]
            and labels["com.emr4.harness"] == profile["harness_label"]
            and labels["com.emr4.cleanup-nonce"] == nonce
            and host["NetworkMode"] == "none"
            and not host.get("Binds")
            and not host.get("PortBindings")
            and host.get("Privileged") is False
            and host["Memory"] == profile["memory_bytes"]
            and host["NanoCpus"] == profile["nano_cpus"]
            and host["PidsLimit"] == profile["pids_limit"]
            and host["RestartPolicy"]["Name"] == profile["restart_policy"]
            and isinstance(expected_tmpfs, str)
            and set(expected_tmpfs.split(","))
            == set(profile["tmpfs_options"].split(","))
            and required_env <= env
            and not any(item == "POSTGRES_HOST_AUTH_METHOD=trust" for item in env)
            and mount_ok
        )
    except (KeyError, TypeError, AttributeError):
        return False


def _psql_argv(
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    *,
    single_transaction: bool = False,
    tuples_only: bool = False,
) -> list[str]:
    argv = [
        docker,
        "exec",
        "-i",
        "--env",
        f"PGPASSWORD={profile['postgres_password']}",
        container_id,
        "psql",
        "-X",
        "--no-psqlrc",
        "--quiet",
        "--set",
        "ON_ERROR_STOP=1",
        "--username",
        profile["postgres_user"],
        "--dbname",
        profile["postgres_database"],
        "--host",
        "/var/run/postgresql",
    ]
    if tuples_only:
        argv.extend(["--tuples-only", "--no-align"])
    if single_transaction:
        argv.append("--single-transaction")
    argv.append("--file=-")
    return argv


def _psql(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    sql: str | bytes,
    *,
    expect_success: bool = True,
    single_transaction: bool = False,
    tuples_only: bool = False,
) -> ProcessResult:
    payload = sql.encode("utf-8") if isinstance(sql, str) else sql
    result = runner(
        _psql_argv(
            docker,
            container_id,
            profile,
            single_transaction=single_transaction,
            tuples_only=tuples_only,
        ),
        payload,
        profile["command_timeout_seconds"],
        256_000,
    )
    if expect_success and result.returncode != 0:
        raise RehearsalFailure("psql", "unexpected_sql_failure", result.stderr)
    if not expect_success and result.returncode == 0:
        raise RehearsalFailure("psql", "expected_sql_failure_missing")
    return result


def _stdout_value(result: ProcessResult) -> str:
    lines = [line.strip() for line in result.stdout.decode("utf-8").splitlines()]
    values = [line for line in lines if line]
    if len(values) != 1:
        raise RehearsalFailure("psql", "unexpected_result_shape")
    return values[0]


def _strip_presentation(value: str) -> str:
    """Remove whitespace, parentheses and presentation-only casts.

    pg_get_constraintdef() and pg_get_triggerdef() render column references with
    explicit casts such as ``(action)::text`` and literals as ``'delete'::text``.
    The bound migration source fixes the executable DDL, so these presentation
    decorations are removed before checking every frozen invariant token.
    """
    stripped = re.sub(r"[\s()\"]", "", value)
    return (
        stripped.replace("::text", "")
        .replace("::charactervarying", "")
        .replace("::character", "")
    )


def _assert_catalogue(facts: dict[str, Any], contract: dict[str, Any]) -> None:
    expected = contract["catalogue"]
    if facts.get("head") != expected["head"]:
        raise RehearsalFailure("catalogue", "head_mismatch")

    observed_columns = {
        (item["table_name"], item["name"]): item for item in facts.get("columns", [])
    }
    for column in expected["columns"]:
        item = observed_columns.get((column["table"], column["name"]))
        if item is None:
            raise RehearsalFailure("catalogue", "column_missing")
        if item["type"] != column["type"] or item["nullable"] != column["nullable"]:
            raise RehearsalFailure("catalogue", "column_shape_mismatch")
        if column["default"] is None:
            if item["default"] is not None:
                raise RehearsalFailure("catalogue", "column_default_mismatch")
        elif item["default"] not in ("1", "'1'::bigint"):
            raise RehearsalFailure("catalogue", "column_default_mismatch")
    if len(observed_columns) != len(expected["columns"]):
        raise RehearsalFailure("catalogue", "unexpected_column")

    constraints = {item["name"]: item for item in facts["constraints"]}
    if set(constraints) != set(expected["constraints"]):
        raise RehearsalFailure("catalogue", "constraint_set_mismatch")
    for name, tokens in expected["constraints"].items():
        # pg_get_constraintdef() inserts presentation-only parentheses and
        # explicit casts around comparisons and column references.  The bound
        # migration source fixes the executable DDL, so this catalogue check
        # deliberately removes whitespace, parentheses and presentation casts
        # before checking every frozen invariant token; it does not rewrite
        # operators, names, or literals.
        observed_definition = _strip_presentation(constraints[name]["definition"])
        if any(
            _strip_presentation(token) not in observed_definition
            for token in tokens
        ):
            raise RehearsalFailure(
                "catalogue", "constraint_definition_mismatch", name
            )

    index_rows = facts.get("index") or []
    if len(index_rows) != 1:
        raise RehearsalFailure("catalogue", "index_shape_mismatch")
    index_item = index_rows[0]
    if index_item.get("name") != expected["index"]["name"]:
        raise RehearsalFailure("catalogue", "index_name_mismatch")
    observed_index = _strip_presentation(
        index_item.get("definition", "")
    ).replace("public.", "")
    for token in expected["index"]["tokens"]:
        if _strip_presentation(token) not in observed_index:
            raise RehearsalFailure("catalogue", "index_definition_mismatch")

    functions = {item["name"]: item for item in facts.get("functions", [])}
    if set(functions) != {item["name"] for item in expected["functions"]}:
        raise RehearsalFailure("catalogue", "function_set_mismatch")
    for expected_fn in expected["functions"]:
        item = functions[expected_fn["name"]]
        if (
            item.get("schema") != "public"
            or item.get("name") != expected_fn["name"]
            or item.get("arguments") != expected_fn["arguments"]
            or item.get("result") != expected_fn["result"]
            or item.get("language") != expected_fn["language"]
            or item.get("security_definer") is not expected_fn["security_definer"]
            or item.get("volatility") != expected_fn["volatility"]
        ):
            raise RehearsalFailure(
                "catalogue", "function_attributes_mismatch", expected_fn["name"]
            )
        function_definition = item.get("definition", "")
        for token in expected_fn["tokens"]:
            if token not in function_definition:
                raise RehearsalFailure(
                    "catalogue", "function_definition_mismatch", expected_fn["name"]
                )

    triggers = {item["name"]: item for item in facts.get("triggers", [])}
    if set(triggers) != {item["name"] for item in expected["triggers"]}:
        raise RehearsalFailure("catalogue", "trigger_set_mismatch")
    for expected_tg in expected["triggers"]:
        item = triggers[expected_tg["name"]]
        definition = re.sub(r"[\s\"]", "", item.get("definition", "")).replace(
            "public.", ""
        )
        if (
            item.get("name") != expected_tg["name"]
            or item.get("table_name") != expected_tg["table"]
            or item.get("enabled") != expected_tg["enabled"]
            or item.get("internal") is not False
        ):
            raise RehearsalFailure(
                "catalogue", "trigger_attributes_mismatch", expected_tg["name"]
            )
        for token in expected_tg["tokens"]:
            normalized = re.sub(r"[\s\"]", "", token).replace("public.", "")
            if normalized not in definition:
                raise RehearsalFailure(
                    "catalogue", "trigger_definition_mismatch", expected_tg["name"]
                )

    if facts.get("unexpected_function_count") != expected["unexpected_function_count"]:
        raise RehearsalFailure("catalogue", "unexpected_function")
    if facts.get("unexpected_trigger_count") != expected["unexpected_trigger_count"]:
        raise RehearsalFailure("catalogue", "unexpected_trigger")

    zero_rows = facts.get("zero_rows") or {}
    for table, expected_count in expected["zero_rows"].items():
        if zero_rows.get(table) != expected_count:
            raise RehearsalFailure("catalogue", "zero_row_mismatch", table)


def _is_exact_absence(result: ProcessResult) -> bool:
    if result.returncode == 0:
        return False
    text_value = result.stderr.decode("utf-8", errors="replace").lower()
    return "no such object" in text_value or "no such container" in text_value


def _cleanup(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    inspected_result, inspected = _inspect(
        runner, docker, container_id, profile["command_timeout_seconds"]
    )
    if inspected_result.returncode != 0 or inspected is None:
        return {"status": "cleanup_ownership_unverified", "container_id": container_id}
    if not _container_owned(
        inspected,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
    ):
        return {"status": "cleanup_ownership_unverified", "container_id": container_id}
    removed = runner(
        [docker, "container", "rm", "--force", container_id],
        None,
        profile["command_timeout_seconds"],
        16_384,
    )
    if removed.returncode != 0:
        return {"status": "cleanup_remove_failed", "container_id": container_id}
    absent, _ = _inspect(
        runner, docker, container_id, profile["command_timeout_seconds"]
    )
    if not _is_exact_absence(absent):
        return {"status": "cleanup_absence_unproved", "container_id": container_id}
    return {"status": "cleanup_verified", "container_id_sha256": _sha256(container_id.encode())}


def _failure_evidence(
    error: RehearsalFailure,
    *,
    lifecycle: list[str],
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": "rehearsal_failed",
        "evidence_label": "authored_synthetic_provider_free_disposable_postgresql_parse_catalogue",
        "source_head": SOURCE_HEAD,
        "lifecycle": lifecycle,
        "failure": {
            "stage": error.stage,
            "code": error.code,
            "detail_sha256": _sha256(error.detail),
        },
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_evidence(evidence: dict[str, Any]) -> Path:
    target = EVIDENCE_PATH if evidence["result"] == PASS_RESULT else FAILURE_EVIDENCE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def run_rehearsal(runner: Runner = _run) -> dict[str, Any]:
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {"status": "not_needed"}
    docker = ""
    container_id = ""
    name = ""
    nonce = ""
    image_id = ""
    contract: dict[str, Any] | None = None
    try:
        contract, source_hashes = verify_contract()
        lifecycle.append("contract_and_sources_verified")
        offline_sql = _generate_offline_sql(contract)
        lifecycle.append("offline_sql_generated")
        profile = contract["docker_profile"]
        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image = runner(
            [docker, "image", "inspect", profile["image_reference"]],
            None,
            profile["command_timeout_seconds"],
            256_000,
        )
        if image.returncode != 0:
            raise RehearsalFailure("environment", "local_image_unavailable")
        try:
            images = json.loads(image.stdout.decode("utf-8"))
            image_id = images[0]["Id"]
        except (UnicodeDecodeError, json.JSONDecodeError, IndexError, KeyError, TypeError):
            raise RehearsalFailure("environment", "image_inspect_invalid") from None
        if not isinstance(image_id, str) or not image_id.startswith("sha256:"):
            raise RehearsalFailure("environment", "image_identity_invalid")
        lifecycle.append("local_image_verified")

        nonce = secrets.token_hex(16)
        name = profile["container_name_prefix"] + secrets.token_hex(8)
        created = runner(
            build_container_argv(docker, name, nonce, contract),
            None,
            profile["command_timeout_seconds"],
            16_384,
        )
        if created.returncode != 0:
            raise RehearsalFailure("container", "create_failed", created.stderr)
        container_id = created.stdout.decode("ascii", errors="strict").strip()
        if not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("container", "captured_id_invalid")
        lifecycle.append("container_created")

        inspected_result, inspected = _inspect(
            runner, docker, container_id, profile["command_timeout_seconds"]
        )
        if inspected_result.returncode != 0 or inspected is None or not _container_owned(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
        ):
            raise RehearsalFailure("container", "ownership_or_profile_mismatch")
        lifecycle.append("container_profile_verified")

        deadline = time.monotonic() + profile["startup_timeout_seconds"]
        observations = 0
        while time.monotonic() < deadline and observations < profile["readiness_observations"]:
            ready = runner(
                [
                    docker,
                    "exec",
                    "--env",
                    f"PGPASSWORD={profile['postgres_password']}",
                    container_id,
                    "pg_isready",
                    "--quiet",
                    "--username",
                    profile["postgres_user"],
                    "--dbname",
                    profile["postgres_database"],
                    "--host",
                    "/var/run/postgresql",
                ],
                None,
                5,
                4096,
            )
            if ready.returncode != 0:
                observations = 0
                time.sleep(1)
                continue
            version = _psql(
                runner,
                docker,
                container_id,
                profile,
                "SELECT current_setting('server_version_num')::integer / 10000;\n",
                tuples_only=True,
            )
            if _stdout_value(version) != "16":
                observations = 0
                time.sleep(1)
                continue
            observations += 1
            if observations < profile["readiness_observations"]:
                time.sleep(1)
        if observations != profile["readiness_observations"]:
            raise RehearsalFailure("readiness", "postgresql_16_not_ready")
        lifecycle.append("postgresql_16_ready")

        _psql(
            runner,
            docker,
            container_id,
            profile,
            PREREQUISITE_SQL,
            single_transaction=True,
        )
        lifecycle.append("synthetic_prerequisites_installed")
        _psql(
            runner,
            docker,
            container_id,
            profile,
            offline_sql,
            single_transaction=True,
        )
        lifecycle.append("migration_installed")

        catalogue_result = _psql(
            runner,
            docker,
            container_id,
            profile,
            CATALOGUE_SQL,
            tuples_only=True,
        )
        try:
            facts = json.loads(_stdout_value(catalogue_result))
        except json.JSONDecodeError:
            raise RehearsalFailure("catalogue", "catalogue_json_invalid") from None
        _assert_catalogue(facts, contract)
        lifecycle.append("catalogue_verified")

        evidence = {
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "result": PASS_RESULT,
            "evidence_label": contract["evidence_label"],
            "source_head": contract["source_head"],
            "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
            "source_hashes": source_hashes,
            "hostile_mutations_rejected": HOSTILE_MUTATION_TARGET,
            "environment": {
                "postgresql_major": 16,
                "image_reference": profile["image_reference"],
                "image_id_sha256": _sha256(image_id.encode()),
                "network_mode": "none",
                "storage": "container_local_tmpfs",
            },
            "offline_sql": {
                "range": contract["alembic"]["offline_range"],
                "body_sha256": _sha256(offline_sql),
                "body_bytes": len(offline_sql),
            },
            "catalogue": {
                "status": "exact_match",
                "facts_sha256": _canonical_digest(facts),
                "columns": len(facts["columns"]),
                "constraints": len(facts["constraints"]),
                "functions": [item["name"] for item in facts["functions"]],
                "triggers": [item["name"] for item in facts["triggers"]],
                "head": facts["head"],
                "zero_rows": facts["zero_rows"],
            },
            "lifecycle": lifecycle,
            "cleanup": {"status": "pending"},
            "claim_boundary": CLAIM_BOUNDARY,
        }
    except RehearsalFailure as error:
        evidence = _failure_evidence(error, lifecycle=lifecycle, cleanup=cleanup)
    finally:
        if container_id and contract is not None:
            cleanup = _cleanup(
                runner,
                docker,
                container_id,
                name,
                nonce,
                image_id,
                contract["docker_profile"],
            )
            if cleanup["status"] != "cleanup_verified":
                evidence = _failure_evidence(
                    RehearsalFailure("cleanup", cleanup["status"]),
                    lifecycle=lifecycle,
                    cleanup=cleanup,
                )
            else:
                evidence["cleanup"] = cleanup
                evidence["lifecycle"] = [*lifecycle, "cleanup_verified"]
    return evidence


def main() -> int:
    if len(sys.argv) != 1:
        print("This fixed-path harness accepts no caller-selected arguments.")
        return 2
    evidence = run_rehearsal()
    target = write_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "evidence": target.relative_to(ROOT).as_posix(),
                "cleanup": evidence["cleanup"]["status"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
