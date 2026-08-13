"""Run one exact-artifact CF-D2 PostgreSQL 16 parse/catalogue rehearsal.

The harness accepts no caller-selected inputs.  It creates one labelled,
networkless, tmpfs-backed container from an exact cached image, streams the
hash-bound inert artifact unchanged, inspects only fixed catalogue projections,
proves zero rows, and removes only the captured container ID after revalidating
ownership.
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

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_DIR = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal"
)
CONTRACT_PATH = CONTINUITY_DIR / "rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_DIR / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_DIR / "provider-free-parse-catalogue-evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-parse-catalogue-evidence.json"
FAILURE_EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-parse-catalogue-failure-evidence.json"
MANIFEST_PATH = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/inert-ddl-manifest.json"
)
ARTIFACT_PATH = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/event-cue-schema.sql.inert"
)
EXPECTED_CONTRACT_DIGEST = (
    "ef20494a38b005ea2e1fa92b31c71a7c374224e3f5ef22ab7328333c4950d506"
)
PASS_RESULT = "raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_pass"
FAIL_RESULT = "rehearsal_failed"
EVIDENCE_SCHEMA_VERSION = (
    "raisa.context_fabric.cf_d2_event_cue_parse_catalogue_evidence.v1"
)
CLAIM_BOUNDARY = (
    "Exact inert artifact parses and creates the frozen PostgreSQL 16 catalogue "
    "shape with zero rows in one destroyed networkless tmpfs container; no "
    "transaction-protocol behavior, runtime durability or product authority is proved."
)


CATALOGUE_SQL = r"""
WITH target_namespace AS (
    SELECT oid, nspname, nspowner, nspacl
    FROM pg_catalog.pg_namespace
    WHERE nspname = 'emr4_context_fabric_cue'
),
domains AS (
    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'name', t.typname,
                'base_type', pg_catalog.format_type(t.typbasetype, t.typtypmod),
                'not_null', t.typnotnull,
                'acl_is_null', t.typacl IS NULL,
                'constraints', (
                    SELECT COALESCE(
                        jsonb_agg(
                            jsonb_build_object(
                                'name', con.conname,
                                'validated', con.convalidated,
                                'definition', pg_catalog.pg_get_constraintdef(con.oid, true)
                            ) ORDER BY con.conname
                        ),
                        '[]'::jsonb
                    )
                    FROM pg_catalog.pg_constraint con
                    WHERE con.contypid = t.oid
                )
            ) ORDER BY t.typname
        ),
        '[]'::jsonb
    ) AS value
    FROM pg_catalog.pg_type t
    JOIN target_namespace n ON n.oid = t.typnamespace
    WHERE t.typtype = 'd'
),
tables AS (
    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'name', c.relname,
                'kind', c.relkind,
                'row_security', c.relrowsecurity,
                'force_row_security', c.relforcerowsecurity,
                'acl_is_null', c.relacl IS NULL
            ) ORDER BY CASE c.relname
                WHEN 'event_partition' THEN 1
                WHEN 'observer_coordinate' THEN 2
                WHEN 'terminal_receipt' THEN 3
                WHEN 'cue_obligation' THEN 4
                WHEN 'consumer_checkpoint' THEN 5
                WHEN 'dispatch_attempt' THEN 6
                WHEN 'reconciliation_receipt' THEN 7
                ELSE 99 END
        ),
        '[]'::jsonb
    ) AS value
    FROM pg_catalog.pg_class c
    JOIN target_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind = 'r'
),
columns AS (
    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'table', c.relname,
                'ordinal', a.attnum,
                'name', a.attname,
                'type', pg_catalog.format_type(a.atttypid, a.atttypmod),
                'not_null', a.attnotnull,
                'default', pg_catalog.pg_get_expr(d.adbin, d.adrelid),
                'identity', a.attidentity,
                'generated', a.attgenerated
            ) ORDER BY CASE c.relname
                WHEN 'event_partition' THEN 1
                WHEN 'observer_coordinate' THEN 2
                WHEN 'terminal_receipt' THEN 3
                WHEN 'cue_obligation' THEN 4
                WHEN 'consumer_checkpoint' THEN 5
                WHEN 'dispatch_attempt' THEN 6
                WHEN 'reconciliation_receipt' THEN 7
                ELSE 99 END, a.attnum
        ),
        '[]'::jsonb
    ) AS value
    FROM pg_catalog.pg_attribute a
    JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
    JOIN target_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_catalog.pg_attrdef d
      ON d.adrelid = a.attrelid AND d.adnum = a.attnum
    WHERE c.relkind = 'r' AND a.attnum > 0 AND NOT a.attisdropped
),
table_constraints AS (
    SELECT COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'name', con.conname,
                'type', con.contype,
                'table', c.relname,
                'columns', COALESCE((
                    SELECT jsonb_agg(a.attname ORDER BY u.ordinality)
                    FROM unnest(con.conkey) WITH ORDINALITY AS u(attnum, ordinality)
                    JOIN pg_catalog.pg_attribute a
                      ON a.attrelid = con.conrelid AND a.attnum = u.attnum
                ), '[]'::jsonb),
                'referenced_table', rc.relname,
                'referenced_columns', COALESCE((
                    SELECT jsonb_agg(a.attname ORDER BY u.ordinality)
                    FROM unnest(con.confkey) WITH ORDINALITY AS u(attnum, ordinality)
                    JOIN pg_catalog.pg_attribute a
                      ON a.attrelid = con.confrelid AND a.attnum = u.attnum
                ), '[]'::jsonb),
                'deferrable', con.condeferrable,
                'initially_deferred', con.condeferred,
                'validated', con.convalidated,
                'definition', pg_catalog.pg_get_constraintdef(con.oid, true)
            ) ORDER BY con.conname
        ),
        '[]'::jsonb
    ) AS value
    FROM pg_catalog.pg_constraint con
    JOIN pg_catalog.pg_class c ON c.oid = con.conrelid
    JOIN target_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_catalog.pg_class rc ON rc.oid = con.confrelid
    WHERE con.contype IN ('p', 'u', 'c', 'f')
),
object_absence AS (
    SELECT jsonb_build_object(
        'functions', (SELECT count(*) FROM pg_catalog.pg_proc p JOIN target_namespace n ON n.oid = p.pronamespace),
        'triggers', (
            SELECT count(*) FROM pg_catalog.pg_trigger tg
            JOIN pg_catalog.pg_class c ON c.oid = tg.tgrelid
            JOIN target_namespace n ON n.oid = c.relnamespace
            WHERE NOT tg.tgisinternal
        ),
        'views', (SELECT count(*) FROM pg_catalog.pg_class c JOIN target_namespace n ON n.oid = c.relnamespace WHERE c.relkind = 'v'),
        'materialized_views', (SELECT count(*) FROM pg_catalog.pg_class c JOIN target_namespace n ON n.oid = c.relnamespace WHERE c.relkind = 'm'),
        'sequences', (SELECT count(*) FROM pg_catalog.pg_class c JOIN target_namespace n ON n.oid = c.relnamespace WHERE c.relkind = 'S'),
        'policies', (
            SELECT count(*) FROM pg_catalog.pg_policy p
            JOIN pg_catalog.pg_class c ON c.oid = p.polrelid
            JOIN target_namespace n ON n.oid = c.relnamespace
        ),
        'non_internal_rules', (
            SELECT count(*) FROM pg_catalog.pg_rewrite r
            JOIN pg_catalog.pg_class c ON c.oid = r.ev_class
            JOIN target_namespace n ON n.oid = c.relnamespace
            WHERE r.rulename <> '_RETURN'
        ),
        'row_security_tables', (SELECT count(*) FROM pg_catalog.pg_class c JOIN target_namespace n ON n.oid = c.relnamespace WHERE c.relrowsecurity OR c.relforcerowsecurity),
        'explicit_object_acls', (
            (SELECT CASE WHEN nspacl IS NULL THEN 0 ELSE 1 END FROM target_namespace)
            + (SELECT count(*) FROM pg_catalog.pg_class c JOIN target_namespace n ON n.oid = c.relnamespace WHERE c.relacl IS NOT NULL)
            + (SELECT count(*) FROM pg_catalog.pg_type t JOIN target_namespace n ON n.oid = t.typnamespace WHERE t.typtype = 'd' AND t.typacl IS NOT NULL)
        )
    ) AS value
)
SELECT jsonb_build_object(
    'schema', (
        SELECT jsonb_build_object(
            'name', nspname,
            'owner', nspowner::pg_catalog.regrole::text,
            'acl_is_null', nspacl IS NULL
        ) FROM target_namespace
    ),
    'domains', (SELECT value FROM domains),
    'tables', (SELECT value FROM tables),
    'columns', (SELECT value FROM columns),
    'constraints', (SELECT value FROM table_constraints),
    'absence', (SELECT value FROM object_absence)
)::text;
""".strip() + "\n"


ROW_COUNTS_SQL = r"""
SELECT jsonb_build_object(
    'event_partition', (SELECT count(*) FROM emr4_context_fabric_cue.event_partition),
    'observer_coordinate', (SELECT count(*) FROM emr4_context_fabric_cue.observer_coordinate),
    'terminal_receipt', (SELECT count(*) FROM emr4_context_fabric_cue.terminal_receipt),
    'cue_obligation', (SELECT count(*) FROM emr4_context_fabric_cue.cue_obligation),
    'consumer_checkpoint', (SELECT count(*) FROM emr4_context_fabric_cue.consumer_checkpoint),
    'dispatch_attempt', (SELECT count(*) FROM emr4_context_fabric_cue.dispatch_attempt),
    'reconciliation_receipt', (SELECT count(*) FROM emr4_context_fabric_cue.reconciliation_receipt)
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


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _canonical_digest(value: Any) -> str:
    return _sha256(_canonical_bytes(value))


def _run(argv: list[str], stdin: bytes | None, timeout: int, cap: int) -> ProcessResult:
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


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalFailure("preflight", "json_root_not_object", str(path))
    return value


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


def _validate_contract_candidate(candidate: dict[str, Any]) -> None:
    schema = _load_json(CONTRACT_SCHEMA_PATH)
    Draft202012Validator(schema).validate(candidate)
    if _canonical_digest(candidate) != EXPECTED_CONTRACT_DIGEST:
        raise RehearsalFailure("preflight", "contract_digest_mismatch")


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    target = contract["hostile_mutation_target"]
    paths = _leaf_paths(contract)
    if len(paths) < target:
        raise RehearsalFailure("preflight", "insufficient_hostile_leaves")
    rejected = 0
    for path in paths[:target]:
        candidate = copy.deepcopy(contract)
        parent = candidate
        for component in path[:-1]:
            parent = parent[component]
        parent[path[-1]] = _mutate_leaf(parent[path[-1]])
        try:
            _validate_contract_candidate(candidate)
        except Exception:  # every changed closed contract must fail
            rejected += 1
    return rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str], bytes, dict[str, Any]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract_candidate(contract)
    if contract["result"] != PASS_RESULT or contract["claim_boundary"] != CLAIM_BOUNDARY:
        raise RehearsalFailure("preflight", "contract_semantics_mismatch")
    rejected = hostile_mutations_rejected(contract)
    if rejected != contract["hostile_mutation_target"]:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")

    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(path.read_bytes())
        observed[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure("preflight", "source_hash_mismatch", binding["path"])

    artifact = ARTIFACT_PATH.read_bytes()
    expected_artifact = contract["artifact"]
    if _sha256(artifact) != expected_artifact["sha256"]:
        raise RehearsalFailure("preflight", "artifact_hash_mismatch")
    if len(artifact) != expected_artifact["byte_count"]:
        raise RehearsalFailure("preflight", "artifact_byte_count_mismatch")
    if b"\r" in artifact or artifact.count(b";") != expected_artifact["statement_count"]:
        raise RehearsalFailure("preflight", "artifact_statement_shape_mismatch")

    manifest = _load_json(MANIFEST_PATH)
    if manifest["sql_artifact_sha256"] != "sha256:" + expected_artifact["sha256"]:
        raise RehearsalFailure("preflight", "manifest_artifact_binding_mismatch")
    if manifest["sql_byte_count"] != len(artifact):
        raise RehearsalFailure("preflight", "manifest_byte_count_mismatch")
    if manifest["statement_count"] != expected_artifact["statement_count"]:
        raise RehearsalFailure("preflight", "manifest_statement_count_mismatch")
    return contract, observed, artifact, manifest


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
    result = runner([docker, "container", "inspect", target], None, timeout, 256_000)
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
        expected_tmpfs = host["Tmpfs"].get(profile["data_destination"])
        mount_ok = mounts == [] or (
            len(mounts) == 1
            and mounts[0].get("Type") == "tmpfs"
            and mounts[0].get("Destination") == profile["data_destination"]
        )
        return bool(
            inspect["Id"] == container_id
            and inspect["Name"] == "/" + name
            and inspect["Image"] == profile["image_id"]
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
            and set(expected_tmpfs.split(",")) == set(profile["tmpfs_options"].split(","))
            and required_env <= env
            and "POSTGRES_HOST_AUTH_METHOD=trust" not in env
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
    if result.returncode != 0:
        raise RehearsalFailure("psql", "unexpected_sql_failure", result.stderr)
    return result


def _stdout_value(result: ProcessResult) -> str:
    values = [line.strip() for line in result.stdout.decode("utf-8").splitlines() if line.strip()]
    if len(values) != 1:
        raise RehearsalFailure("psql", "unexpected_result_shape")
    return values[0]


def _query_json(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    sql: str,
) -> dict[str, Any]:
    result = _psql(
        runner,
        docker,
        container_id,
        profile,
        sql,
        tuples_only=True,
    )
    try:
        value = json.loads(_stdout_value(result))
    except json.JSONDecodeError:
        raise RehearsalFailure("catalogue", "catalogue_json_invalid") from None
    if not isinstance(value, dict):
        raise RehearsalFailure("catalogue", "catalogue_json_root_invalid")
    return value


def _expected_columns(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    physical_types = {
        "digest": "emr4_context_fabric_cue.digest_v1",
        "nullable_digest": "emr4_context_fabric_cue.digest_v1",
        "opaque_id": "emr4_context_fabric_cue.opaque_id_v1",
        "positive_integer": "emr4_context_fabric_cue.positive_integer_v1",
        "nullable_positive_integer": "emr4_context_fabric_cue.positive_integer_v1",
        "boolean": "boolean",
        "enum": "text",
        "nullable_enum": "text",
    }
    expected: list[dict[str, Any]] = []
    for relation in manifest["relations"]:
        for ordinal, field in enumerate(relation["fields"], 1):
            expected.append(
                {
                    "table": relation["name"],
                    "ordinal": ordinal,
                    "name": field["name"],
                    "type": physical_types[field["type"]],
                    "not_null": not field["nullable"],
                    "default": None,
                    "identity": "",
                    "generated": "",
                }
            )
    return expected


def _constraint_expectations(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalogue = contract["catalogue"]
    expected: dict[str, dict[str, Any]] = {}
    for name, values in catalogue["primary_keys"].items():
        expected[name] = {
            "type": "p",
            "table": values[0],
            "columns": values[1:],
            "referenced_table": None,
            "referenced_columns": [],
            "deferrable": False,
            "initially_deferred": False,
            "validated": True,
        }
    for name, values in catalogue["unique_keys"].items():
        expected[name] = {
            "type": "u",
            "table": values[0],
            "columns": values[1:],
            "referenced_table": None,
            "referenced_columns": [],
            "deferrable": False,
            "initially_deferred": False,
            "validated": True,
        }
    for name, table in catalogue["table_checks"].items():
        expected[name] = {
            "type": "c",
            "table": table,
            "referenced_table": None,
            "referenced_columns": [],
            "deferrable": False,
            "initially_deferred": False,
            "validated": True,
        }
    for name, value in catalogue["foreign_keys"].items():
        expected[name] = {
            "type": "f",
            "table": value["table"],
            "columns": value["columns"],
            "referenced_table": value["referenced_table"],
            "referenced_columns": value["referenced_columns"],
            "deferrable": value["deferrable"],
            "initially_deferred": value["initially_deferred"],
            "validated": True,
        }
    return expected


def _assert_catalogue(
    facts: dict[str, Any], contract: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    expected = contract["catalogue"]
    schema = facts.get("schema")
    if schema != {
        "name": expected["schema_name"],
        "owner": contract["docker_profile"]["postgres_user"],
        "acl_is_null": True,
    }:
        raise RehearsalFailure("catalogue", "schema_shape_mismatch")

    domains = facts.get("domains")
    if not isinstance(domains, list) or len(domains) != 3:
        raise RehearsalFailure("catalogue", "domain_count_mismatch")
    domain_names: list[str] = []
    domain_constraint_digests: dict[str, str] = {}
    for domain in domains:
        name = domain.get("name")
        domain_names.append(name)
        if (
            domain.get("base_type") != expected["domain_base_types"].get(name)
            or domain.get("not_null") is not False
            or domain.get("acl_is_null") is not True
        ):
            raise RehearsalFailure("catalogue", "domain_shape_mismatch", str(name))
        constraints = domain.get("constraints")
        if not isinstance(constraints, list) or len(constraints) != 1:
            raise RehearsalFailure("catalogue", "domain_constraint_count_mismatch")
        constraint = constraints[0]
        if constraint.get("validated") is not True or not isinstance(
            constraint.get("definition"), str
        ):
            raise RehearsalFailure("catalogue", "domain_constraint_shape_mismatch")
        domain_constraint_digests[constraint["name"]] = _sha256(
            constraint["definition"].encode("utf-8")
        )
    if domain_names != sorted(expected["domain_names"]):
        raise RehearsalFailure("catalogue", "domain_names_mismatch")
    if sorted(domain_constraint_digests) != sorted(expected["domain_constraint_names"]):
        raise RehearsalFailure("catalogue", "domain_constraint_names_mismatch")

    tables = facts.get("tables")
    if not isinstance(tables, list) or [item.get("name") for item in tables] != expected["relation_order"]:
        raise RehearsalFailure("catalogue", "relation_order_mismatch")
    for table in tables:
        if table != {
            "name": table["name"],
            "kind": "r",
            "row_security": False,
            "force_row_security": False,
            "acl_is_null": True,
        }:
            raise RehearsalFailure("catalogue", "table_shape_mismatch", table["name"])

    columns = facts.get("columns")
    if columns != _expected_columns(manifest):
        raise RehearsalFailure("catalogue", "column_shape_mismatch")

    constraints = facts.get("constraints")
    if not isinstance(constraints, list):
        raise RehearsalFailure("catalogue", "constraints_not_array")
    expected_constraints = _constraint_expectations(contract)
    if [item.get("name") for item in constraints] != sorted(expected_constraints):
        raise RehearsalFailure("catalogue", "constraint_name_set_mismatch")
    definition_digests: dict[str, str] = {}
    type_counts = {"p": 0, "u": 0, "c": 0, "f": 0}
    for actual in constraints:
        name = actual["name"]
        definition = actual.pop("definition", None)
        if not isinstance(definition, str):
            raise RehearsalFailure("catalogue", "constraint_definition_missing", name)
        expected_item = expected_constraints[name]
        for key, value in expected_item.items():
            if actual.get(key) != value:
                raise RehearsalFailure("catalogue", "constraint_shape_mismatch", name)
        if actual["type"] == "c":
            # conkey is informative for checks and need not restate semantic text.
            pass
        elif set(actual) != set(expected_item) | {"name"}:
            raise RehearsalFailure("catalogue", "constraint_extra_field", name)
        definition_digests[name] = _sha256(definition.encode("utf-8"))
        type_counts[actual["type"]] += 1
    count_expectations = expected["expected_counts"]
    if type_counts != {
        "p": count_expectations["primary_keys"],
        "u": count_expectations["unique_keys"],
        "c": count_expectations["table_checks"],
        "f": count_expectations["foreign_keys"],
    }:
        raise RehearsalFailure("catalogue", "constraint_type_count_mismatch")

    absence = facts.get("absence")
    expected_absence = {
        key: count_expectations[key]
        for key in (
            "functions",
            "triggers",
            "views",
            "materialized_views",
            "sequences",
            "policies",
            "non_internal_rules",
            "row_security_tables",
            "explicit_object_acls",
        )
    }
    if absence != expected_absence:
        raise RehearsalFailure("catalogue", "object_absence_mismatch")

    return {
        "status": "exact_match",
        "schema": expected["schema_name"],
        "domains": len(domains),
        "domain_checks": len(domain_constraint_digests),
        "tables": len(tables),
        "fields": len(columns),
        "primary_keys": type_counts["p"],
        "unique_keys": type_counts["u"],
        "table_checks": type_counts["c"],
        "foreign_keys": type_counts["f"],
        "domain_definition_digests_sha256": _canonical_digest(domain_constraint_digests),
        "constraint_definition_digests_sha256": _canonical_digest(definition_digests),
        "facts_sha256": _canonical_digest(facts),
        "absence": absence,
    }


def _assert_row_counts(row_counts: dict[str, Any], contract: dict[str, Any]) -> dict[str, int]:
    expected_names = contract["catalogue"]["relation_order"]
    if set(row_counts) != set(expected_names) or len(row_counts) != len(expected_names):
        raise RehearsalFailure("rows", "row_count_relation_set_mismatch")
    if any(type(value) is not int or value != 0 for value in row_counts.values()):
        raise RehearsalFailure("rows", "nonzero_row_count")
    return {name: row_counts[name] for name in expected_names}


def _is_exact_absence(result: ProcessResult) -> bool:
    if result.returncode == 0:
        return False
    text = result.stderr.decode("utf-8", errors="replace").lower()
    return "no such object" in text or "no such container" in text


def _cleanup(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
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
    absent, _ = _inspect(runner, docker, container_id, profile["command_timeout_seconds"])
    if not _is_exact_absence(absent):
        return {"status": "cleanup_absence_unproved", "container_id": container_id}
    return {
        "status": "cleanup_verified",
        "container_id_sha256": _sha256(container_id.encode("ascii")),
    }


def _base_evidence(contract: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": FAIL_RESULT,
        "evidence_label": (
            contract["evidence_label"]
            if contract is not None
            else "authored_synthetic_provider_free_disposable_postgresql_16_parse_catalogue"
        ),
        "planning_baseline": (
            contract["planning_baseline"] if contract is not None else "0" * 40
        ),
        "accepted_inert_ddl_source": (
            contract["accepted_inert_ddl_source"] if contract is not None else "0" * 40
        ),
        "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
        "source_hashes": {},
        "hostile_mutations_rejected": 0,
        "environment": {},
        "artifact": {},
        "catalogue": {},
        "row_counts": {},
        "lifecycle": [],
        "cleanup": {"status": "not_needed"},
        "effects": {},
        "failure": None,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal(runner: Runner = _run) -> dict[str, Any]:
    contract: dict[str, Any] | None = None
    evidence = _base_evidence(contract)
    lifecycle: list[str] = []
    docker = ""
    container_id = ""
    name = ""
    nonce = ""
    deadline = time.monotonic() + 300
    try:
        contract, source_hashes, artifact, manifest = verify_contract()
        evidence = _base_evidence(contract)
        evidence["source_hashes"] = source_hashes
        evidence["hostile_mutations_rejected"] = contract["hostile_mutation_target"]
        lifecycle.append("contract_sources_and_exact_artifact_verified")
        profile = contract["docker_profile"]
        deadline = time.monotonic() + profile["total_timeout_seconds"]

        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image_result = runner(
            [docker, "image", "inspect", profile["image_reference"]],
            None,
            profile["command_timeout_seconds"],
            256_000,
        )
        if image_result.returncode != 0:
            raise RehearsalFailure("environment", "local_image_unavailable")
        try:
            images = json.loads(image_result.stdout.decode("utf-8"))
            image = images[0]
            image_id = image["Id"]
            repo_digests = image["RepoDigests"]
        except (UnicodeDecodeError, json.JSONDecodeError, IndexError, KeyError, TypeError):
            raise RehearsalFailure("environment", "image_inspect_invalid") from None
        if image_id != profile["image_id"] or profile["repo_digest"] not in repo_digests:
            raise RehearsalFailure("environment", "local_image_identity_mismatch")
        lifecycle.append("exact_cached_image_verified")

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
        lifecycle.append("owned_container_created")

        inspected_result, inspected = _inspect(
            runner, docker, container_id, profile["command_timeout_seconds"]
        )
        if inspected_result.returncode != 0 or inspected is None or not _container_owned(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            profile=profile,
        ):
            raise RehearsalFailure("container", "ownership_or_profile_mismatch")
        lifecycle.append("container_profile_verified")

        readiness_deadline = min(
            deadline, time.monotonic() + profile["startup_timeout_seconds"]
        )
        observations = 0
        while time.monotonic() < readiness_deadline and observations < profile["readiness_observations"]:
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
            version = runner(
                _psql_argv(
                    docker,
                    container_id,
                    profile,
                    tuples_only=True,
                ),
                b"SELECT current_setting('server_version_num')::integer / 10000;\n",
                5,
                4096,
            )
            if version.returncode != 0:
                observations = 0
                time.sleep(1)
                continue
            try:
                observed_major = _stdout_value(version)
            except RehearsalFailure:
                observations = 0
                time.sleep(1)
                continue
            if observed_major != "16":
                observations = 0
                time.sleep(1)
                continue
            observations += 1
            if observations < profile["readiness_observations"]:
                time.sleep(1)
        if observations != profile["readiness_observations"]:
            raise RehearsalFailure("readiness", "postgresql_16_not_ready")
        lifecycle.append("postgresql_16_ready")

        if time.monotonic() >= deadline:
            raise RehearsalFailure("bounds", "total_timeout_exceeded")
        _psql(
            runner,
            docker,
            container_id,
            profile,
            artifact,
            single_transaction=True,
        )
        lifecycle.append("exact_artifact_installed")

        facts = _query_json(runner, docker, container_id, profile, CATALOGUE_SQL)
        catalogue_summary = _assert_catalogue(facts, contract, manifest)
        lifecycle.append("exact_catalogue_verified")
        row_counts = _assert_row_counts(
            _query_json(runner, docker, container_id, profile, ROW_COUNTS_SQL),
            contract,
        )
        lifecycle.append("zero_rows_verified")

        evidence.update(
            {
                "result": PASS_RESULT,
                "environment": {
                    "postgresql_major": 16,
                    "image_reference": profile["image_reference"],
                    "image_id_sha256": _sha256(image_id.encode("ascii")),
                    "repo_digest_sha256": _sha256(profile["repo_digest"].encode("ascii")),
                    "network_mode": "none",
                    "storage": "container_local_tmpfs",
                },
                "artifact": {
                    "sha256": _sha256(artifact),
                    "byte_count": len(artifact),
                    "statement_count": contract["artifact"]["statement_count"],
                    "streamed_unchanged": True,
                    "installation_wrapper_claim": "containment_only",
                },
                "catalogue": catalogue_summary,
                "row_counts": row_counts,
                "effects": contract["effects"],
                "failure": None,
            }
        )
    except RehearsalFailure as error:
        evidence["failure"] = {
            "stage": error.stage,
            "code": error.code,
            "detail_sha256": _sha256(error.detail),
        }
    finally:
        cleanup = {"status": "not_needed"}
        if container_id and contract is not None:
            cleanup = _cleanup(
                runner,
                docker,
                container_id,
                name,
                nonce,
                contract["docker_profile"],
            )
            if cleanup["status"] != "cleanup_verified":
                evidence["result"] = FAIL_RESULT
                evidence["failure"] = {
                    "stage": "cleanup",
                    "code": cleanup["status"],
                    "detail_sha256": _sha256(b""),
                }
            else:
                lifecycle.append("cleanup_verified")
        evidence["cleanup"] = cleanup
        evidence["lifecycle"] = lifecycle
    return evidence


def validate_evidence(evidence: dict[str, Any]) -> None:
    schema = _load_json(EVIDENCE_SCHEMA_PATH)
    Draft202012Validator(schema).validate(evidence)
    if evidence["result"] == PASS_RESULT:
        if evidence["cleanup"]["status"] != "cleanup_verified":
            raise RehearsalFailure("evidence", "passing_cleanup_not_verified")
        if evidence["failure"] is not None:
            raise RehearsalFailure("evidence", "passing_failure_not_null")


def write_evidence(evidence: dict[str, Any]) -> Path:
    validate_evidence(evidence)
    target = EVIDENCE_PATH if evidence["result"] == PASS_RESULT else FAILURE_EVIDENCE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


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
