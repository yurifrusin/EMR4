#!/usr/bin/env python3
"""Run the fixed, provider-free Context Fabric PostgreSQL behavior rehearsal.

The harness accepts no caller-selected input.  It reuses the already accepted
Docker containment primitives from the parse/catalogue rehearsal, installs the
byte-identical inert artifact, and executes the twenty contract scenarios in
their frozen order.  Only bounded counts, digests, booleans, identities, and
SQLSTATE identifiers can leave the disposable database.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal as parent,
    raisa_provider_free_unmounted_durability_inert_ddl_rehearsal as inert_renderer,
)

REHEARSAL_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal"
)
CONTRACT_PATH = REHEARSAL_DIR / "behavior-transaction-rehearsal-contract.json"
EVIDENCE_PATH = REHEARSAL_DIR / "provider-free-behavior-transaction-evidence.json"
PREREQUISITE_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal/synthetic-prerequisite-contract.json"
)
PARENT_REHEARSAL_CONTRACT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal/rehearsal-contract.json"
)
BODY_CONTRACT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture/function-trigger-body-architecture-"
    "contract.json"
)

EXPECTED_CONTRACT_PATH = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal/"
    "behavior-transaction-rehearsal-contract.json"
)
EXPECTED_CONTRACT_SHA256 = (
    "sha256:4ca9f7612bd79159bc2232cec5bc078219ac2145c9d1ad80927420d2f8706f16"
)
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_durability_"
    "behavior_transaction_rehearsal_pass"
)
EVIDENCE_MODE = (
    "provider_free_disposable_postgresql_authored_synthetic_behavior_transaction"
)
CLAIM_BOUNDARY = (
    "selected_serial_entry_point_trigger_rls_idempotency_and_outer_rollback_"
    "behavior_only"
)
EXPECTED_FIXTURE_CATALOGUE_CHANGES = frozenset(
    {"application_relations", "relation_acl"}
)
EXPECTED_POST_BEHAVIOR_CATALOGUE_CHANGES = frozenset({"application_relations"})

Runner = Callable[[list[str], bytes | None, float, int], parent.ProcessResult]
UUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
SQLSTATE = re.compile(r"^[0-9A-Z]{5}$")
PSQL_SQLSTATE_LINE = re.compile(
    rb"(?m)^(?:psql:[^\r\n]{1,160}:\s*)?ERROR:\s+([0-9A-Z]{5}):"
)
PSQL_DIAGNOSTIC_LINE = re.compile(
    rb"(?m)^(SCHEMA NAME|TABLE NAME|COLUMN NAME):\s+([a-z][a-z0-9_]*)\s*$"
)
PSQL_NOT_NULL_LINE = re.compile(
    rb"(?m)^(?:psql:[^\r\n]{1,160}:\s*)?ERROR:\s+23502:\s+"
    rb'null value in column "([a-z][a-z0-9_]*)" of relation '
    rb'"([a-z][a-z0-9_]*)" violates not-null constraint\s*$'
)
PSQL_PLPGSQL_CONTEXT_LINE = re.compile(
    rb"(?m)^CONTEXT:\s+PL/pgSQL function (?:emr4_context_fabric\.)?"
    rb"([a-z][a-z0-9_]*)\([^\r\n]{0,500}\) line "
    rb"([1-9][0-9]{0,5}) at [^\r\n]{1,160}\s*$"
)

SOURCE_MEMBERSHIP_DIGEST_PROFILE = "emr4_context_fabric.source_membership_digest_v1"
SOURCE_MEMBERSHIP_RELATION = "emr4_context_fabric.diary_context_observation_outbox_v1"
SOURCE_MEMBERSHIP_FIELDS = (
    "practice_id",
    "source_contract_id",
    "stream_id",
    "stream_epoch",
    "transaction_position",
    "predecessor_position",
    "raw_event_uuid",
    "opaque_aggregate_alias",
    "aggregate_revision",
    "source_contract_digest",
    "transaction_authored_at",
)

SAFE_SCENARIO_FUNCTIONS = {
    "BTR-E01": frozenset({"register_observer_generation_v1"}),
    "BTR-E02": frozenset({"project_update_confirm_reschedule_v1"}),
    "BTR-E03": frozenset({"admit_proofread_observation_v1"}),
    "BTR-I01": frozenset({"admit_proofread_observation_v1"}),
    "BTR-E04": frozenset({"apply_durability_transition_v1"}),
    "BTR-I03": frozenset({"apply_durability_transition_v1"}),
    "BTR-I02": frozenset(
        {"project_update_confirm_reschedule_v1", "admit_proofread_observation_v1"}
    ),
}

SAFE_BOOTSTRAP_COLUMNS = {
    "public.appointments": {
        "id",
        "practice_id",
        "practitioner_id",
        "location_id",
        "start_time",
        "duration_minutes",
    },
    "emr4_context_fabric.context_service_practice_binding": {
        "database_login",
        "logical_capability",
        "practice_id",
        "source_contract_id",
        "binding_revision",
        "credential_epoch",
        "active_from",
        "active_until",
        "stream_id",
    },
    "emr4_context_fabric.context_generation_registry_barrier": {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "barrier_revision",
        "updated_at",
    },
    "emr4_context_fabric.context_observer_generation": {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "observer_id",
        "observer_generation",
        "lifecycle_state",
        "policy_digest",
        "principal_digest",
        "binding_digest",
        "source_digest",
        "registry_digest",
        "impact_digest",
        "key_schedule_digest",
        "created_at",
        "consumed_at",
        "terminal_reason",
    },
    "emr4_context_fabric.context_durability_checkpoint": {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "observer_id",
        "observer_generation",
        "checkpoint_state",
        "last_contiguous_position",
        "last_observation_digest",
        "lifecycle_revision",
        "audit_head_digest",
        "checkpoint_integrity_digest",
        "updated_at",
    },
    "emr4_context_fabric.context_frame_generation": {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "observer_id",
        "observer_generation",
        "frame_generation_id",
        "frame_type",
        "assembled_through_position",
        "lifecycle_state",
        "created_at",
        "retired_at",
    },
    "emr4_context_fabric.context_invalidation_watermark": {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "observer_id",
        "observer_generation",
        "frame_type",
        "watermark_position",
        "updated_at",
    },
    "emr4_context_fabric.context_reassembly_obligation": {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "observer_id",
        "observer_generation",
        "frame_generation_id",
        "earliest_position",
        "latest_position",
        "rolling_cause_digest",
        "count_bucket",
        "obligation_state",
        "created_at",
        "updated_at",
    },
}

APPLICATION_RELATIONS = (
    "appointments",
    "appointment_command_idempotency",
    "appointment_audit_log",
    "diary_committed_events",
)
FABRIC_RELATIONS = (
    "context_observation_stream_head",
    "diary_context_aggregate_aliases_v1",
    "diary_context_observation_outbox_v1",
    "context_proofread_observation_admission",
    "context_generation_registry_barrier",
    "context_observer_generation",
    "context_durability_checkpoint",
    "context_recovery_anchor",
    "context_classified_observation_receipt",
    "context_frame_generation",
    "context_invalidation_watermark",
    "context_reassembly_obligation",
    "context_durability_lifecycle",
    "context_durability_audit",
    "context_observation_key_interval",
    "context_recovery_pin",
    "context_service_practice_binding",
    "context_retention_policy",
)
SNAPSHOT_RELATIONS = tuple(f"public.{name}" for name in APPLICATION_RELATIONS) + tuple(
    f"emr4_context_fabric.{name}" for name in FABRIC_RELATIONS
)
SERIALIZABLE_SCENARIOS = frozenset({"BTR-E01", "BTR-E04", "BTR-I03", "BTR-B03"})
TRANSITION_RESULT_MARKER = "emr4.behavior.transition_result.v1"
EXPECTED_TRANSITION_RESULT_KINDS = {
    "BTR-E04": "RECEIPT_APPLIED",
    "BTR-I03": "RECEIPT_REPLAYED",
    "BTR-B03": "RECEIPT_APPLIED",
}

EXPECTED_DELTAS: dict[str, dict[str, int]] = {
    "BTR-E01": {
        "emr4_context_fabric.context_observation_stream_head": 1,
        "emr4_context_fabric.context_generation_registry_barrier": 0,
        "emr4_context_fabric.context_observer_generation": 3,
        "emr4_context_fabric.context_durability_checkpoint": 3,
        "emr4_context_fabric.context_recovery_anchor": 3,
        "emr4_context_fabric.context_frame_generation": 6,
        "emr4_context_fabric.context_invalidation_watermark": 6,
        "emr4_context_fabric.context_observation_key_interval": 3,
    },
    "BTR-E02": {
        "public.appointment_command_idempotency": 1,
        "public.appointment_audit_log": 1,
        "public.diary_committed_events": 1,
        "emr4_context_fabric.diary_context_aggregate_aliases_v1": 1,
        "emr4_context_fabric.diary_context_observation_outbox_v1": 1,
    },
    "BTR-E03": {"emr4_context_fabric.context_proofread_observation_admission": 1},
    "BTR-E04": {
        "emr4_context_fabric.context_classified_observation_receipt": 1,
        "emr4_context_fabric.context_reassembly_obligation": 1,
        "emr4_context_fabric.context_durability_lifecycle": 1,
        "emr4_context_fabric.context_durability_audit": 1,
    },
    "BTR-I02": {"emr4_context_fabric.context_proofread_observation_admission": 2},
}

ALLOWED_DIGEST_CHANGES: dict[str, set[str]] = {
    "BTR-E01": set(EXPECTED_DELTAS["BTR-E01"]),
    "BTR-E02": set(EXPECTED_DELTAS["BTR-E02"])
    | {
        "public.appointments",
        "emr4_context_fabric.context_observation_stream_head",
    },
    "BTR-E03": set(EXPECTED_DELTAS["BTR-E03"]),
    "BTR-E04": set(EXPECTED_DELTAS["BTR-E04"])
    | {
        "emr4_context_fabric.context_durability_checkpoint",
        "emr4_context_fabric.context_frame_generation",
        "emr4_context_fabric.context_invalidation_watermark",
    },
    "BTR-E05": {"public.appointments"},
    "BTR-I02": set(EXPECTED_DELTAS["BTR-I02"]),
}

STABLE_REASONS = {
    None: "accepted",
    "CF101": "producer_claim_ineligible",
    "CF201": "admission_source_missing",
    "CF004": "required_row_missing_or_ambiguous",
    "CF601": "immutable_member_rejected",
    "CF603": "temporal_bijection_rejected",
    "CF604": "second_update_rejected",
    "42501": "standard_privilege_denied",
    "P0001": "fixed_injected_rollback",
}


class BehaviorFailure(parent.RehearsalFailure):
    """Closed failure raised by the behavior harness."""


def _safe_sqlstate(result: parent.ProcessResult) -> str | None:
    matches = set(PSQL_SQLSTATE_LINE.findall(result.stdout + b"\n" + result.stderr))
    if len(matches) != 1:
        return None
    value = next(iter(matches)).decode("ascii")
    return value if SQLSTATE.fullmatch(value) else None


def _safe_plpgsql_coordinate(
    result: parent.ProcessResult, scenario_id: str
) -> dict[str, Any]:
    allowed = SAFE_SCENARIO_FUNCTIONS.get(scenario_id)
    if not allowed:
        return {}
    raw = result.stdout + b"\n" + result.stderr
    matches = set(PSQL_PLPGSQL_CONTEXT_LINE.findall(raw))
    if len(matches) != 1:
        return {}
    function_raw, line_raw = next(iter(matches))
    function_name = function_raw.decode("ascii")
    if function_name not in allowed:
        return {}
    function_line = int(line_raw.decode("ascii"))
    if not 1 <= function_line <= 100000:
        return {}
    return {
        "function_id": f"emr4_context_fabric.{function_name}",
        "function_line": function_line,
    }


def _safe_bootstrap_failure_metadata(
    result: parent.ProcessResult,
) -> dict[str, str]:
    metadata: dict[str, str] = {}
    sqlstate = _safe_sqlstate(result)
    if sqlstate is not None:
        metadata["sqlstate"] = sqlstate

    raw = result.stdout + b"\n" + result.stderr
    fields: dict[bytes, set[bytes]] = {}
    for name, value in PSQL_DIAGNOSTIC_LINE.findall(raw):
        fields.setdefault(name, set()).add(value)
    required = (b"SCHEMA NAME", b"TABLE NAME", b"COLUMN NAME")
    if any(len(fields.get(name, set())) == 0 for name in required):
        header_matches = set(PSQL_NOT_NULL_LINE.findall(raw))
        if len(header_matches) == 1:
            column_raw, table_raw = next(iter(header_matches))
            column = column_raw.decode("ascii")
            table = table_raw.decode("ascii")
            relations = [
                relation
                for relation in SAFE_BOOTSTRAP_COLUMNS
                if relation.rsplit(".", 1)[1] == table
            ]
            if len(relations) == 1:
                relation = relations[0]
                if column in SAFE_BOOTSTRAP_COLUMNS[relation]:
                    metadata.update(
                        coordinate_status="released",
                        relation=relation,
                        column=column,
                    )
                    return metadata
                metadata["coordinate_status"] = "unlisted_column"
                return metadata
            metadata["coordinate_status"] = "unlisted_relation"
            return metadata
        metadata["coordinate_status"] = "missing"
        return metadata
    if any(len(fields[name]) != 1 for name in required):
        metadata["coordinate_status"] = "ambiguous"
        return metadata

    schema = next(iter(fields[b"SCHEMA NAME"])).decode("ascii")
    table = next(iter(fields[b"TABLE NAME"])).decode("ascii")
    column = next(iter(fields[b"COLUMN NAME"])).decode("ascii")
    relation = f"{schema}.{table}"
    if relation not in SAFE_BOOTSTRAP_COLUMNS:
        metadata["coordinate_status"] = "unlisted_relation"
    elif column not in SAFE_BOOTSTRAP_COLUMNS[relation]:
        metadata["coordinate_status"] = "unlisted_column"
    else:
        metadata.update(coordinate_status="released", relation=relation, column=column)
    return metadata


def _canonical_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BehaviorFailure("contract", "json_object_required")
    return value


def _git_source_bytes(source_head: str, relative_path: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40}", source_head):
        raise BehaviorFailure("parent", "source_head")
    if relative_path.startswith(("/", "\\")) or ".." in Path(relative_path).parts:
        raise BehaviorFailure("parent", "source_path")
    git = shutil.which("git.exe") or shutil.which("git")
    if not git:
        raise BehaviorFailure("environment", "git_client_missing")
    completed = subprocess.run(
        [git, "show", f"{source_head}:{relative_path}"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        shell=False,
    )
    if completed.returncode != 0 or len(completed.stdout) > 8 * 1024 * 1024:
        raise BehaviorFailure("parent", "source_head_path_unavailable")
    return completed.stdout.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _profile() -> dict[str, Any]:
    source = _json(PARENT_REHEARSAL_CONTRACT_PATH)["docker_profile"]
    profile = copy.deepcopy(source)
    profile.update(
        {
            "container_name_prefix": "emr4-cf-pg16-behavior-",
            "ownership_labels": {
                "com.emr4.harness": "disposable-postgresql-durability-behavior-v1",
                "com.emr4.cleanup-nonce": "per_run_random_hex",
            },
            "postgres_database": "emr4_synthetic_behavior",
            "artifact_timeout_seconds": 120,
            "total_timeout_seconds": 420,
        }
    )
    profile.pop("postgres_password", None)
    return profile


def _run_argv(
    docker: str, profile: dict[str, Any], *, name: str, nonce: str
) -> list[str]:
    labels = profile["ownership_labels"]
    return [
        docker,
        "run",
        "--detach",
        "--name",
        name,
        "--label",
        f"com.emr4.harness={labels['com.emr4.harness']}",
        "--label",
        f"com.emr4.cleanup-nonce={nonce}",
        "--pull=never",
        "--network=none",
        "--tmpfs",
        profile["tmpfs"],
        "--memory",
        profile["memory"],
        "--cpus",
        profile["cpus"],
        "--pids-limit",
        str(profile["pids_limit"]),
        "--restart",
        profile["restart"],
        "--entrypoint",
        "/usr/bin/tail",
        profile["image_reference"],
        "--follow",
        "/dev/null",
    ]


def _init_argvs(
    docker: str, container_id: str, profile: dict[str, Any]
) -> list[tuple[str, list[str], bytes | None]]:
    pgdata = profile["pgdata"]
    hba = (
        "local all all peer map=emr4map\n"
        "host all all 0.0.0.0/0 reject\n"
        "host all all ::0/0 reject\n"
    ).encode("ascii")
    ident = (
        "emr4map root emr4_synthetic_bootstrap\n"
        "emr4map postgres emr4_synthetic_bootstrap\n"
    ).encode("ascii")
    return [
        (
            "pgdata_directory",
            [
                docker,
                "exec",
                container_id,
                "/usr/bin/install",
                "--directory",
                "--owner=postgres",
                "--group=postgres",
                "--mode=0700",
                pgdata,
            ],
            None,
        ),
        (
            "initdb",
            [
                docker,
                "exec",
                "--user",
                "postgres",
                container_id,
                "/usr/lib/postgresql/16/bin/initdb",
                "--pgdata",
                pgdata,
                "--username",
                profile["postgres_user"],
                "--encoding=UTF8",
                "--locale=C",
                "--auth-local=peer",
                "--auth-host=reject",
            ],
            None,
        ),
        (
            "pg_hba",
            [
                docker,
                "exec",
                "-i",
                container_id,
                "/bin/dd",
                f"of={pgdata}/pg_hba.conf",
                "status=none",
            ],
            hba,
        ),
        (
            "pg_ident",
            [
                docker,
                "exec",
                "-i",
                container_id,
                "/bin/dd",
                f"of={pgdata}/pg_ident.conf",
                "status=none",
            ],
            ident,
        ),
        (
            "postgres_start",
            [
                docker,
                "exec",
                "--user",
                "postgres",
                container_id,
                "/usr/lib/postgresql/16/bin/pg_ctl",
                "--pgdata",
                pgdata,
                "--options",
                "-c listen_addresses='' -c unix_socket_directories='/var/run/postgresql'",
                "--wait",
                "--timeout",
                str(profile["startup_timeout_seconds"]),
                "start",
            ],
            None,
        ),
    ]


def assert_init_argv(argv: list[str], stdin: bytes | None) -> None:
    rendered = "\x1f".join(argv)
    if not argv or Path(argv[0]).name.lower() != "docker.exe" or argv[1] != "exec":
        raise BehaviorFailure("command", "init_transport")
    if any(
        token in argv for token in ("sh", "bash", "cmd", "powershell", "--privileged")
    ):
        raise BehaviorFailure("command", "init_shell_or_privilege")
    if any("PASSWORD" in token.upper() or "trust" in token.lower() for token in argv):
        raise BehaviorFailure("command", "password_or_trust")
    if "--auth-local=peer" in argv and "--auth-host=reject" not in argv:
        raise BehaviorFailure("command", "host_auth_not_rejected")
    if stdin is not None and not ("/bin/dd" in argv and "-i" in argv):
        raise BehaviorFailure("command", "unexpected_init_stdin")
    if any("*" in token or "?" in token or "docker.sock" in token for token in argv):
        raise BehaviorFailure("command", "unsafe_init_path", rendered)


def assert_run_argv(argv: list[str]) -> None:
    parent.assert_closed_argv(argv, parent.DockerOperation.RUN)
    if "--entrypoint" not in argv or "/usr/bin/tail" not in argv:
        raise BehaviorFailure("command", "inert_entrypoint_missing")
    if any(
        token.startswith("POSTGRES_") or "PASSWORD" in token.upper() for token in argv
    ):
        raise BehaviorFailure("command", "credential_environment")


def _behavior_container_owned(
    inspect: dict[str, Any],
    *,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> bool:
    config = inspect.get("Config")
    host = inspect.get("HostConfig")
    mounts = inspect.get("Mounts")
    if (
        not isinstance(config, dict)
        or not isinstance(host, dict)
        or not isinstance(mounts, list)
    ):
        return False
    labels = config.get("Labels") or {}
    environment = config.get("Env") or []
    tmpfs_path, tmpfs_options = profile["tmpfs"].split(":", 1)
    normalized_tmpfs = [
        row
        for row in mounts
        if isinstance(row, dict)
        and row.get("Type") == "tmpfs"
        and row.get("Destination") == tmpfs_path
    ]
    normalized_closed = not mounts or len(normalized_tmpfs) == len(mounts) == 1
    return bool(
        inspect.get("Id") == container_id
        and inspect.get("Name") == "/" + name
        and inspect.get("Image") == image_id
        and config.get("Image") == profile["image_reference"]
        and config.get("Entrypoint") in (["/usr/bin/tail"], "/usr/bin/tail")
        and config.get("Cmd") == ["--follow", "/dev/null"]
        and labels.get("com.emr4.harness")
        == profile["ownership_labels"]["com.emr4.harness"]
        and labels.get("com.emr4.cleanup-nonce") == nonce
        and host.get("NetworkMode") == "none"
        and not host.get("Binds")
        and not host.get("Privileged")
        and not host.get("PortBindings")
        and host.get("Memory") == 768 * 1024 * 1024
        and host.get("NanoCpus") == 1_000_000_000
        and host.get("PidsLimit") == profile["pids_limit"]
        and host.get("RestartPolicy", {}).get("Name") in {"", "no"}
        and (host.get("Tmpfs") or {}) == {tmpfs_path: tmpfs_options}
        and normalized_closed
        and all(not token.startswith("POSTGRES_") for token in environment)
    )


def _cleanup(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    inspect_result = parent._call(  # noqa: SLF001
        runner,
        parent.docker_argv(
            parent.DockerOperation.ID_INSPECT,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=parent.DockerOperation.ID_INSPECT,
        stdin=None,
        timeout=profile["cleanup_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    inspect = parent._one_json(inspect_result, "cleanup_inspect")  # noqa: SLF001
    if not _behavior_container_owned(
        inspect,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
    ):
        return {
            "status": "cleanup_ownership_unverified",
            "container_id": container_id,
            "removed": False,
            "absence_verified": False,
        }
    remove = parent._call(  # noqa: SLF001
        runner,
        parent.docker_argv(
            parent.DockerOperation.REMOVE,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=parent.DockerOperation.REMOVE,
        stdin=None,
        timeout=profile["cleanup_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if remove.returncode != 0:
        raise BehaviorFailure("cleanup", "remove_failed")
    absent = parent._call(  # noqa: SLF001
        runner,
        parent.docker_argv(
            parent.DockerOperation.ID_ABSENCE,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=parent.DockerOperation.ID_ABSENCE,
        stdin=None,
        timeout=profile["cleanup_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if not parent._is_exact_absence(absent):  # noqa: SLF001
        raise BehaviorFailure("cleanup", "container_still_present")
    return {
        "status": "cleanup_verified",
        "container_id": container_id,
        "removed": True,
        "absence_verified": True,
    }


def _validate_contract() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], bytes
]:
    if CONTRACT_PATH.relative_to(ROOT).as_posix() != EXPECTED_CONTRACT_PATH:
        raise BehaviorFailure("contract", "contract_path_drift")
    contract = _json(CONTRACT_PATH)
    if parent._canonical_sha(contract) != EXPECTED_CONTRACT_SHA256:  # noqa: SLF001
        raise BehaviorFailure("contract", "contract_sha256")
    if contract.get("status") != "accepted_plan_runtime_closed":
        raise BehaviorFailure("contract", "runtime_not_closed")
    ordered = contract.get("scenario_order")
    scenarios = contract.get("scenarios")
    if not isinstance(ordered, list) or not isinstance(scenarios, list):
        raise BehaviorFailure("contract", "scenario_population")
    if len(ordered) != 20 or [row.get("id") for row in scenarios] != ordered:
        raise BehaviorFailure("contract", "scenario_order")
    if len(set(ordered)) != 20 or set(ordered) != {
        "BTR-E01",
        "BTR-E02",
        "BTR-E03",
        "BTR-I01",
        "BTR-E04",
        "BTR-I03",
        "BTR-E05",
        "BTR-E06",
        "BTR-I02",
        "BTR-I04",
        "BTR-T01",
        "BTR-T02",
        "BTR-T03",
        "BTR-T04",
        "BTR-R01",
        "BTR-R02",
        "BTR-R03",
        "BTR-B01",
        "BTR-B02",
        "BTR-B03",
    }:
        raise BehaviorFailure("contract", "scenario_ids")
    fixture = contract.get("fixture_namespace", {})
    for key, value in fixture.items():
        if key.startswith(
            (
                "practice_",
                "stream_",
                "appointment_",
                "observer_",
                "actor",
                "practitioner",
                "location_",
                "command_",
                "audit_",
                "event_",
            )
        ):
            if key not in {
                "stream_epoch",
                "source_membership_digest_rule",
            } and not UUID.fullmatch(str(value)):
                raise BehaviorFailure("contract", "fixture_uuid", key)
        if key.startswith("digest_") and not DIGEST.fullmatch(str(value)):
            raise BehaviorFailure("contract", "fixture_digest", key)
    parent_bindings = contract.get("parent_bindings", [])
    if len(parent_bindings) != 6:
        raise BehaviorFailure("contract", "parent_population")
    seen: set[str] = set()
    for binding in parent_bindings:
        path = ROOT / binding["path"]
        if binding["id"] in seen or not path.is_file():
            raise BehaviorFailure(
                "parent", "binding_missing_or_duplicate", binding["id"]
            )
        seen.add(binding["id"])
        if _sha256(_canonical_bytes(path)) != binding["sha256"]:
            raise BehaviorFailure("parent", "binding_sha256", binding["id"])
        if (
            _sha256(_git_source_bytes(binding["source_head"], binding["path"]))
            != binding["sha256"]
        ):
            raise BehaviorFailure("parent", "source_head_sha256", binding["id"])
    prerequisite = _json(PREREQUISITE_PATH)
    parent._validate_prerequisite(prerequisite)  # noqa: SLF001
    artifact_binding = next(row for row in parent_bindings if row["id"] == "inert_sql")
    artifact = _canonical_bytes(ROOT / artifact_binding["path"])
    manifest = _json(
        ROOT
        / next(row for row in parent_bindings if row["id"] == "render_manifest")["path"]
    )
    if manifest.get("sql_sha256") != _sha256(artifact):
        raise BehaviorFailure("parent", "manifest_artifact_digest")
    _accepted_source_membership_digest_expression(artifact)
    profile = _profile()
    runtime = contract["runtime_profile"]
    expected_runtime = {
        "postgresql_major": 16,
        "image": profile["image_reference"],
        "pull_policy": "never",
        "network_mode": "none",
        "published_ports": 0,
        "mounts": 0,
        "storage": "container_local_tmpfs",
        "database_count": 1,
        "container_count": 1,
        "shell": False,
        "caller_selected_inputs": False,
        "cleanup": "exact_captured_container_id_after_ownership_reverification",
    }
    if runtime != expected_runtime:
        raise BehaviorFailure("contract", "runtime_profile")
    return contract, prerequisite, manifest, artifact


def _lit(value: str) -> str:
    if "'" in value or "\\" in value or "\x00" in value:
        raise BehaviorFailure("render", "unsafe_literal")
    return "'" + value + "'"


def _walk_nodes(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_nodes(child)


def _accepted_source_membership_digest_expression(artifact: bytes | None = None) -> str:
    body = _json(BODY_CONTRACT_PATH)
    programs = [
        row
        for row in body.get("body_programs", [])
        if row.get("id") == "emr4_context_fabric.admit_proofread_observation_v1"
    ]
    if len(programs) != 1:
        raise BehaviorFailure("contract", "admission_program_population")
    matches = [
        node
        for node in _walk_nodes(programs[0].get("ast", {}))
        if node.get("op") == "CANONICAL_DIGEST"
        and node.get("profile") == SOURCE_MEMBERSHIP_DIGEST_PROFILE
    ]
    if len(matches) != 1:
        raise BehaviorFailure("contract", "source_membership_digest_population")
    operands = matches[0].get("operands", [])
    if tuple(operand.get("column") for operand in operands) != (
        SOURCE_MEMBERSHIP_FIELDS
    ) or any(
        operand.get("op") != "REF"
        or operand.get("kind") != "ROW_COLUMN"
        or operand.get("symbol") != "source"
        or operand.get("relation") != SOURCE_MEMBERSHIP_RELATION
        for operand in operands
    ):
        raise BehaviorFailure("contract", "source_membership_digest_definition")
    expression = inert_renderer.render_expr(matches[0])
    if artifact is not None and expression.encode("utf-8") not in artifact:
        raise BehaviorFailure("parent", "source_membership_digest_lowering")
    return expression


def _source_membership_digest_subquery(f: dict[str, Any], source_position: str) -> str:
    if not re.fullmatch(r"(?:[1-9][0-9]*|__POSITION__)", source_position):
        raise BehaviorFailure("render", "source_position_token")
    expression = _accepted_source_membership_digest_expression()
    return (
        "(SELECT "
        + expression
        + " FROM emr4_context_fabric.diary_context_observation_outbox_v1 AS source "
        + f"WHERE source.practice_id={_lit(f['practice_alpha'])}::pg_catalog.uuid "
        + "AND source.source_contract_id="
        + _lit(f["source_contract_id"])
        + "::emr4_context_fabric.source_contract_code "
        + f"AND source.stream_id={_lit(f['stream_alpha'])}::pg_catalog.uuid "
        + f"AND source.stream_epoch={f['stream_epoch']}::pg_catalog.int8 "
        + f"AND source.transaction_position={source_position}::pg_catalog.int8)"
    )


def _locator(
    f: dict[str, Any],
    observer: str,
    *,
    practice: str = "practice_alpha",
    stream: str = "stream_alpha",
) -> str:
    return (
        "ROW("
        + ",".join(
            (
                _lit(f[practice]) + "::pg_catalog.uuid",
                _lit(f["source_contract_id"])
                + "::emr4_context_fabric.source_contract_code",
                _lit(f[stream]) + "::pg_catalog.uuid",
                str(f["stream_epoch"]) + "::pg_catalog.int8",
                _lit(f[observer]) + "::pg_catalog.uuid",
                "1::pg_catalog.int8",
            )
        )
        + ")::emr4_context_fabric.generation_locator_v1"
    )


def _registration(f: dict[str, Any], observer: str) -> str:
    locator = _locator(f, observer)
    future = (
        "ROW("
        f"{f['key_interval_start']}::pg_catalog.int8,"
        f"{f['key_interval_end']}::pg_catalog.int8,"
        f"{_lit(f['key_id'])}::emr4_context_fabric.key_id,"
        f"{_lit(f['digest_key_attestation'])}::emr4_context_fabric.digest_sha256"
        ")::emr4_context_fabric.future_key_interval_v1"
    )
    return (
        "ROW("
        + ",".join(
            (
                locator,
                *(
                    _lit(f[key]) + "::emr4_context_fabric.digest_sha256"
                    for key in (
                        "digest_policy",
                        "digest_principal",
                        "digest_binding",
                        "digest_source",
                        "digest_registry",
                        "digest_impact",
                        "digest_key_schedule",
                    )
                ),
                future,
            )
        )
        + ")::emr4_context_fabric.generation_registration_v1"
    )


def _packet(f: dict[str, Any], *, conflict: bool = False) -> str:
    digest = f[
        "digest_observation_conflict" if conflict else "digest_observation_primary"
    ]
    decision = "ADMIT_NO_INTERSECTION" if conflict else "ADMIT_SELECTIVE"
    reason = "NO_INTERSECTION" if conflict else "RELEVANT_INTERSECTION"
    mask = 0 if conflict else 1
    return (
        "ROW("
        f"{_lit(digest)}::emr4_context_fabric.digest_sha256,"
        f"{_lit(decision)}::emr4_context_fabric.observation_decision,"
        f"{_lit(reason)}::emr4_context_fabric.observation_reason,"
        f"{mask}::emr4_context_fabric.frame_mask,"
        "'ADVANCE'::emr4_context_fabric.checkpoint_disposition,"
        f"{_lit(f['key_id'])}::emr4_context_fabric.key_id,"
        + _source_membership_digest_subquery(f, "__POSITION__")
        + ")::emr4_context_fabric.proofread_packet_v1"
    )


def _identity_select(principal: str) -> str:
    return (
        "SELECT pg_catalog.json_build_object("
        f"'expected_principal',{_lit(principal)},"
        "'session_user',session_user::pg_catalog.text,"
        "'current_user',current_user::pg_catalog.text,"
        "'isolation',pg_catalog.current_setting('transaction_isolation'),"
        "'read_only',(pg_catalog.current_setting('transaction_read_only')='on'))"
        "::pg_catalog.text;"
    )


def _transition_result_select(
    contract: dict[str, Any], scenario_id: str, *, observer: str, position: int
) -> str:
    expected = EXPECTED_TRANSITION_RESULT_KINDS.get(scenario_id)
    if expected is None or position not in {1, 2}:
        raise BehaviorFailure("render", "unsafe_transition_result_marker", scenario_id)
    f = contract["fixture_namespace"]
    return (
        "WITH transition_result AS MATERIALIZED (SELECT ("
        "emr4_context_fabric.apply_durability_transition_v1(ROW("
        + _locator(f, observer)
        + f",{position}::pg_catalog.int8)::emr4_context_fabric.admission_locator_v1))"
        ".result_kind::pg_catalog.text AS result_kind) "
        "SELECT pg_catalog.json_build_object("
        f"'marker',{_lit(TRANSITION_RESULT_MARKER)},"
        f"'scenario_id',{_lit(scenario_id)},"
        "'result_kind',result_kind,"
        f"'expected_result_kind',{_lit(expected)},"
        f"'assertion',1 / CASE WHEN result_kind={_lit(expected)} THEN 1 ELSE 0 END"
        ")::pg_catalog.text FROM transition_result;"
    )


def _script(
    principal: str,
    statements: list[str],
    *,
    read_only: bool = False,
    isolation: str = "read committed",
) -> bytes:
    if not IDENTIFIER.fullmatch(principal):
        raise BehaviorFailure("render", "unsafe_principal")
    if isolation not in {"read committed", "serializable"}:
        raise BehaviorFailure("render", "unsafe_isolation")
    begin = f"BEGIN ISOLATION LEVEL {isolation.upper()}"
    begin += " READ ONLY;" if read_only else ";"
    lines = [
        f"SET SESSION AUTHORIZATION {principal};",
        begin,
        _identity_select(principal),
        *statements,
        "COMMIT;",
    ]
    rendered = "\n".join(lines) + "\n"
    if rendered.count("SET SESSION AUTHORIZATION") != 1:
        raise BehaviorFailure("render", "session_authorization_count")
    if rendered.index("SET SESSION AUTHORIZATION") > rendered.index("BEGIN"):
        raise BehaviorFailure("render", "session_authorization_order")
    if re.search(
        r"\b(SET ROLE|SAVEPOINT|PREPARE TRANSACTION)\b", rendered, re.IGNORECASE
    ):
        raise BehaviorFailure("render", "forbidden_transaction_control")
    return rendered.encode("utf-8")


def _multi_transaction_script(
    principal: str, transactions: list[list[str]], *, isolation: str = "read committed"
) -> bytes:
    if not IDENTIFIER.fullmatch(principal) or len(transactions) < 2:
        raise BehaviorFailure("render", "unsafe_multi_transaction_shape")
    if isolation not in {"read committed", "serializable"}:
        raise BehaviorFailure("render", "unsafe_isolation")
    lines = [f"SET SESSION AUTHORIZATION {principal};"]
    for index, statements in enumerate(transactions):
        lines.append(f"BEGIN ISOLATION LEVEL {isolation.upper()};")
        if index == 0:
            lines.append(_identity_select(principal))
        lines.extend([*statements, "COMMIT;"])
    rendered = "\n".join(lines) + "\n"
    if rendered.count("SET SESSION AUTHORIZATION") != 1:
        raise BehaviorFailure("render", "session_authorization_count")
    if re.search(
        r"\b(SET ROLE|SAVEPOINT|PREPARE TRANSACTION)\b", rendered, re.IGNORECASE
    ):
        raise BehaviorFailure("render", "forbidden_transaction_control")
    return rendered.encode("utf-8")


def _payload(
    f: dict[str, Any],
    appointment: str,
    *,
    start: str | None = None,
    location: str = "location_alpha",
) -> str:
    start_value = start or f["rescheduled_start"]
    return (
        "pg_catalog.jsonb_build_object("
        f"'appointment_id',{_lit(f[appointment])},"
        f"'practitioner_id',{_lit(f['practitioner'])},"
        f"'location_id',{_lit(f[location])},"
        f"'start_time',{_lit(start_value)},"
        "'end_time',pg_catalog.to_char("
        f"{_lit(start_value)}::pg_catalog.timestamptz + "
        f"pg_catalog.make_interval(mins=>{f['duration_minutes']}),"
        '\'YYYY-MM-DD"T"HH24:MI:SS"Z"\'),'
        "'reason_codes','{appointment_time_changed}')"
    )


def _producer_transaction(
    f: dict[str, Any],
    *,
    appointment: str,
    command: str,
    audit: str,
    event: str,
    start: str | None = None,
    injected: bool = False,
    aggregate_revision: int = 1,
) -> list[str]:
    new_start = start or f["rescheduled_start"]
    return [
        "INSERT INTO public.appointment_command_idempotency "
        "(id,practice_id,actor_user_id,operation_id,route_family,request_body_hash,state,"
        "target_appointment_id,audit_log_id,created_at) VALUES ("
        f"{_lit(f[command])}::pg_catalog.uuid,{_lit(f['practice_alpha'])}::pg_catalog.uuid,"
        f"{_lit(f['actor'])}::pg_catalog.uuid,'confirmAppointmentUpdateProposal','update-confirm',"
        f"{_lit('synthetic-request-' + command)},'in_progress',{_lit(f[appointment])}::pg_catalog.uuid,"
        f"{_lit(f[audit])}::pg_catalog.uuid,pg_catalog.transaction_timestamp());",
        "UPDATE public.appointments SET "
        f"start_time={_lit(new_start)}::pg_catalog.timestamptz,duration_minutes={f['duration_minutes']} "
        f"WHERE id={_lit(f[appointment])}::pg_catalog.uuid;",
        "INSERT INTO public.appointment_audit_log "
        "(id,practice_id,appointment_id,action,command_id,created_at) VALUES ("
        f"{_lit(f[audit])}::pg_catalog.uuid,{_lit(f['practice_alpha'])}::pg_catalog.uuid,"
        f"{_lit(f[appointment])}::pg_catalog.uuid,'update',{_lit(f[command])}::pg_catalog.uuid,"
        "pg_catalog.transaction_timestamp());",
        "INSERT INTO public.diary_committed_events "
        "(id,practice_id,event_type,schema_version,source_system,appointment_id,aggregate_revision,"
        "occurred_at,command_id,audit_log_id,payload,created_at) VALUES ("
        f"{_lit(f[event])}::pg_catalog.uuid,{_lit(f['practice_alpha'])}::pg_catalog.uuid,"
        "'diary.appointment_rescheduled','diary.appointment_rescheduled.v1','emr4-diary',"
        f"{_lit(f[appointment])}::pg_catalog.uuid,{aggregate_revision},pg_catalog.transaction_timestamp(),"
        f"{_lit(f[command])}::pg_catalog.uuid,{_lit(f[audit])}::pg_catalog.uuid,"
        f"{_payload(f, appointment, start=new_start)},pg_catalog.transaction_timestamp());",
        "SELECT (emr4_context_fabric.project_update_confirm_reschedule_v1("
        f"{_lit(f[command])}::pg_catalog.uuid)).transaction_position;",
        "UPDATE public.appointment_command_idempotency SET state='completed' "
        f"WHERE id={_lit(f[command])}::pg_catalog.uuid;",
        *(
            [
                "DO $fixed_abort$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='fixed_injected_rollback'; END $fixed_abort$;"
            ]
            if injected
            else []
        ),
    ]


def render_bootstrap_sql(contract: dict[str, Any]) -> bytes:
    f = contract["fixture_namespace"]
    bindings = (
        ("context_producer", "PRODUCER"),
        ("context_observer", "OBSERVER"),
        ("context_coordinator", "COORDINATOR"),
        ("context_lifecycle", "LIFECYCLE"),
        ("context_retention", "RETENTION"),
        ("context_application_read", "APPLICATION_READ"),
    )
    rows = ",\n".join(
        "("
        + ",".join(
            (
                _lit(role) + "::pg_catalog.name",
                _lit(capability) + "::emr4_context_fabric.logical_capability",
                _lit(f["practice_alpha"]) + "::pg_catalog.uuid",
                _lit(f["source_contract_id"])
                + "::emr4_context_fabric.source_contract_code",
                "1::pg_catalog.int8",
                "1::pg_catalog.int8",
                "'-infinity'::pg_catalog.timestamptz",
                "NULL::pg_catalog.timestamptz",
                _lit(f["stream_alpha"]) + "::pg_catalog.uuid",
            )
        )
        + ")"
        for role, capability in bindings
    )
    appointment_rows = ",\n".join(
        "("
        + ",".join(
            (
                _lit(f[name]) + "::pg_catalog.uuid",
                _lit(f[practice]) + "::pg_catalog.uuid",
                _lit(f["practitioner"]) + "::pg_catalog.uuid",
                _lit(
                    f[
                        "location_alpha"
                        if practice == "practice_alpha"
                        else "location_beta"
                    ]
                )
                + "::pg_catalog.uuid",
                _lit(f["initial_start"]) + "::pg_catalog.timestamptz",
                str(f["duration_minutes"]),
            )
        )
        + ")"
        for name, practice in (
            ("appointment_temporal", "practice_alpha"),
            ("appointment_non_temporal", "practice_alpha"),
            ("appointment_negative", "practice_alpha"),
            ("appointment_beta", "practice_beta"),
        )
    )
    sql = f"""
GRANT SELECT,INSERT,UPDATE ON TABLE public.appointments TO context_producer;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE public.appointment_command_idempotency TO context_producer;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE public.appointment_audit_log TO context_producer;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE public.diary_committed_events TO context_producer;
INSERT INTO emr4_context_fabric.context_service_practice_binding
(database_login,logical_capability,practice_id,source_contract_id,binding_revision,credential_epoch,active_from,active_until,stream_id)
VALUES
{rows};
INSERT INTO public.appointments
(id,practice_id,practitioner_id,location_id,start_time,duration_minutes)
VALUES
{appointment_rows};
INSERT INTO emr4_context_fabric.context_generation_registry_barrier
(practice_id,source_contract_id,stream_id,barrier_revision,updated_at)
VALUES ({_lit(f["practice_alpha"])}::pg_catalog.uuid,{_lit(f["source_contract_id"])},
        {_lit(f["stream_alpha"])}::pg_catalog.uuid,0,pg_catalog.transaction_timestamp());
WITH beta_barrier AS (
  INSERT INTO emr4_context_fabric.context_generation_registry_barrier
  (practice_id,source_contract_id,stream_id,barrier_revision,updated_at)
  VALUES ({_lit(f["practice_beta"])}::pg_catalog.uuid,{_lit(f["source_contract_id"])},
          {_lit(f["stream_beta"])}::pg_catalog.uuid,0,pg_catalog.transaction_timestamp())
  RETURNING practice_id,source_contract_id,stream_id
), beta_generation AS (
  INSERT INTO emr4_context_fabric.context_observer_generation
  (practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,lifecycle_state,
   policy_digest,principal_digest,binding_digest,source_digest,registry_digest,impact_digest,key_schedule_digest,created_at)
  SELECT practice_id,source_contract_id,stream_id,1,{_lit(f["observer_happy"])}::pg_catalog.uuid,1,'ACTIVE',
         {_lit(f["digest_policy"])},{_lit(f["digest_principal"])},{_lit(f["digest_binding"])},
         {_lit(f["digest_source"])},{_lit(f["digest_registry"])},{_lit(f["digest_impact"])},
         {_lit(f["digest_key_schedule"])},pg_catalog.transaction_timestamp()
  FROM beta_barrier
  RETURNING practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation
), beta_checkpoint AS (
  INSERT INTO emr4_context_fabric.context_durability_checkpoint
  (practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,
   checkpoint_state,last_contiguous_position,last_observation_digest,lifecycle_revision,
   audit_head_digest,checkpoint_integrity_digest,updated_at)
  SELECT practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,
         'ACTIVE',0,NULL,0,{_lit(f["digest_observation_primary"])},
         {_lit(f["digest_key_attestation"])},pg_catalog.transaction_timestamp()
  FROM beta_generation
  RETURNING practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation
), beta_frame AS (
  INSERT INTO emr4_context_fabric.context_frame_generation
  (practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,frame_generation_id,
   frame_type,assembled_through_position,lifecycle_state,created_at,retired_at)
  SELECT practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,
         pg_catalog.gen_random_uuid(),'CURRENT_DIARY_PROJECTION',0,'CURRENT',pg_catalog.transaction_timestamp(),NULL
  FROM beta_checkpoint
  RETURNING practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,frame_generation_id
), beta_watermark AS (
  INSERT INTO emr4_context_fabric.context_invalidation_watermark
  (practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,frame_type,watermark_position,updated_at)
  SELECT practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,
         'CURRENT_DIARY_PROJECTION',0,pg_catalog.transaction_timestamp() FROM beta_checkpoint
  RETURNING practice_id
), beta_obligation AS (
  INSERT INTO emr4_context_fabric.context_reassembly_obligation
  (practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,frame_generation_id,
   earliest_position,latest_position,rolling_cause_digest,count_bucket,obligation_state,created_at,updated_at)
  SELECT practice_id,source_contract_id,stream_id,stream_epoch,observer_id,observer_generation,
         frame_generation_id,1,1,{_lit(f["digest_observation_primary"])},'ONE','PENDING',
         pg_catalog.transaction_timestamp(),pg_catalog.transaction_timestamp()
  FROM beta_frame
  RETURNING practice_id
)
SELECT (SELECT pg_catalog.count(*) FROM beta_watermark)
     + (SELECT pg_catalog.count(*) FROM beta_obligation);
"""
    return _script("emr4_synthetic_bootstrap", [sql])


def render_scenario_sql(contract: dict[str, Any], scenario_id: str) -> bytes:
    f = contract["fixture_namespace"]
    primary = _packet(f).replace("__POSITION__", "1")
    position_two_primary = _packet(f).replace("__POSITION__", "2")
    position_two_conflict = _packet(f, conflict=True).replace("__POSITION__", "2")
    admission_happy = (
        "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
        f"{_locator(f, 'observer_happy')},1,{primary})).entry_kind;"
    )
    if scenario_id == "BTR-E01":
        return _multi_transaction_script(
            "context_lifecycle",
            [
                [
                    "SELECT (emr4_context_fabric.register_observer_generation_v1("
                    + _registration(f, observer)
                    + ")).observer_id;"
                ]
                for observer in (
                    "observer_happy",
                    "observer_conflict",
                    "observer_rollback",
                )
            ],
            isolation="serializable",
        )
    if scenario_id == "BTR-I02":
        return _multi_transaction_script(
            "context_observer",
            [
                [
                    "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
                    + _locator(f, "observer_conflict")
                    + ",2,"
                    + position_two_primary
                    + ")).entry_kind;"
                ],
                [
                    "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
                    + _locator(f, "observer_conflict")
                    + ",2,"
                    + position_two_conflict
                    + ")).entry_kind;"
                ],
                [
                    "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
                    + _locator(f, "observer_conflict")
                    + ",2,"
                    + position_two_conflict
                    + ")).entry_kind;"
                ],
            ],
        )
    scripts: dict[str, tuple[str, list[str], bool]] = {
        "BTR-E02": (
            "context_producer",
            _producer_transaction(
                f,
                appointment="appointment_temporal",
                command="command_position_one",
                audit="audit_position_one",
                event="event_position_one",
            ),
            False,
        ),
        "BTR-E03": ("context_observer", [admission_happy], False),
        "BTR-I01": ("context_observer", [admission_happy], False),
        "BTR-E04": (
            "context_coordinator",
            [
                _transition_result_select(
                    contract, "BTR-E04", observer="observer_happy", position=1
                )
            ],
            False,
        ),
        "BTR-I03": (
            "context_coordinator",
            [
                _transition_result_select(
                    contract, "BTR-I03", observer="observer_happy", position=1
                )
            ],
            False,
        ),
        "BTR-E05": (
            "context_producer",
            [
                "UPDATE public.appointments SET location_id="
                + _lit(f["location_beta"])
                + "::pg_catalog.uuid WHERE id="
                + _lit(f["appointment_non_temporal"])
                + "::pg_catalog.uuid;"
            ],
            False,
        ),
        "BTR-E06": (
            "context_observer",
            [
                "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
                + _locator(f, "observer_happy")
                + ",99,"
                + _packet(f).replace("__POSITION__", "1")
                + ")).entry_kind;"
            ],
            False,
        ),
        "BTR-I04": (
            "context_producer",
            [
                "SELECT (emr4_context_fabric.project_update_confirm_reschedule_v1("
                + _lit(f["command_position_one"])
                + "::pg_catalog.uuid)).transaction_position;"
            ],
            False,
        ),
        "BTR-T01": (
            "context_producer",
            [
                "UPDATE public.appointments SET start_time="
                + _lit(f["initial_start"])
                + "::pg_catalog.timestamptz WHERE id="
                + _lit(f["appointment_temporal"])
                + "::pg_catalog.uuid;"
            ],
            False,
        ),
        "BTR-T02": (
            "context_producer",
            [
                "UPDATE public.appointments SET start_time="
                + _lit(f["initial_start"])
                + "::pg_catalog.timestamptz WHERE id="
                + _lit(f["appointment_temporal"])
                + "::pg_catalog.uuid;",
                "INSERT INTO public.diary_committed_events "
                "(id,practice_id,event_type,schema_version,source_system,appointment_id,aggregate_revision,"
                "occurred_at,command_id,audit_log_id,payload,created_at) VALUES ("
                + _lit(f["event_negative_insert_delete"])
                + "::pg_catalog.uuid,"
                + _lit(f["practice_alpha"])
                + "::pg_catalog.uuid,'diary.appointment_rescheduled',"
                "'diary.appointment_rescheduled.v1','emr4-diary',"
                + _lit(f["appointment_temporal"])
                + "::pg_catalog.uuid,2,pg_catalog.transaction_timestamp(),"
                + _lit(f["command_negative_insert_delete"])
                + "::pg_catalog.uuid,"
                + _lit(f["audit_negative_insert_delete"])
                + "::pg_catalog.uuid,"
                + _payload(f, "appointment_temporal", start=f["initial_start"])
                + ",pg_catalog.transaction_timestamp());",
                "DELETE FROM public.diary_committed_events WHERE id="
                + _lit(f["event_negative_insert_delete"])
                + "::pg_catalog.uuid;",
            ],
            False,
        ),
        "BTR-T03": (
            "context_producer",
            [
                "UPDATE public.diary_committed_events "
                "SET payload=payload||pg_catalog.jsonb_build_object('synthetic_probe','blocked') WHERE id="
                + _lit(f["event_position_one"])
                + "::pg_catalog.uuid;"
            ],
            False,
        ),
        "BTR-T04": (
            "context_producer",
            [
                "UPDATE public.appointments SET start_time="
                + _lit(f["initial_start"])
                + "::pg_catalog.timestamptz WHERE id="
                + _lit(f["appointment_temporal"])
                + "::pg_catalog.uuid;",
                "UPDATE public.appointments SET start_time="
                + _lit(f["rescheduled_start"])
                + "::pg_catalog.timestamptz WHERE id="
                + _lit(f["appointment_temporal"])
                + "::pg_catalog.uuid;",
            ],
            False,
        ),
        "BTR-R01": (
            "context_application_read",
            [
                "SELECT pg_catalog.json_build_object("
                "'alpha_rows_visible',(((SELECT count(*) FROM emr4_context_fabric.context_frame_generation)>0) "
                "AND ((SELECT count(*) FROM emr4_context_fabric.context_invalidation_watermark)>0) "
                "AND ((SELECT count(*) FROM emr4_context_fabric.context_reassembly_obligation)>0)),"
                "'beta_rows_invisible',(((SELECT count(*) FROM emr4_context_fabric.context_frame_generation "
                "WHERE practice_id="
                + _lit(f["practice_beta"])
                + "::pg_catalog.uuid)=0) "
                "AND ((SELECT count(*) FROM emr4_context_fabric.context_invalidation_watermark WHERE practice_id="
                + _lit(f["practice_beta"])
                + "::pg_catalog.uuid)=0) "
                "AND ((SELECT count(*) FROM emr4_context_fabric.context_reassembly_obligation WHERE practice_id="
                + _lit(f["practice_beta"])
                + "::pg_catalog.uuid)=0)),"
                "'zero_unbound_rows_visible',(((SELECT count(*) FROM emr4_context_fabric.context_frame_generation "
                "WHERE practice_id<>"
                + _lit(f["practice_alpha"])
                + "::pg_catalog.uuid)=0) "
                "AND ((SELECT count(*) FROM emr4_context_fabric.context_invalidation_watermark WHERE practice_id<>"
                + _lit(f["practice_alpha"])
                + "::pg_catalog.uuid)=0) "
                "AND ((SELECT count(*) FROM emr4_context_fabric.context_reassembly_obligation WHERE practice_id<>"
                + _lit(f["practice_alpha"])
                + "::pg_catalog.uuid)=0)))::pg_catalog.text;"
            ],
            True,
        ),
        "BTR-R02": (
            "context_observer",
            [
                "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
                + _locator(
                    f, "observer_happy", practice="practice_beta", stream="stream_beta"
                )
                + ",1,"
                + primary
                + ")).entry_kind;"
            ],
            False,
        ),
        "BTR-B01": (
            "context_producer",
            _producer_transaction(
                f,
                appointment="appointment_temporal",
                command="command_rollback",
                audit="audit_rollback",
                event="event_rollback",
                start=f["initial_start"],
                injected=True,
                aggregate_revision=2,
            ),
            False,
        ),
        "BTR-B02": (
            "context_observer",
            [
                "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
                + _locator(f, "observer_rollback")
                + ",2,"
                + position_two_primary
                + ")).entry_kind;",
                "DO $fixed_abort$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='fixed_injected_rollback'; END $fixed_abort$;",
            ],
            False,
        ),
        "BTR-B03": (
            "context_coordinator",
            [
                _transition_result_select(
                    contract, "BTR-B03", observer="observer_rollback", position=2
                ),
                "DO $fixed_abort$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='fixed_injected_rollback'; END $fixed_abort$;",
            ],
            False,
        ),
    }
    if scenario_id == "BTR-R03":
        raise BehaviorFailure("render", "role_matrix_requires_distinct_connections")
    if scenario_id not in scripts:
        raise BehaviorFailure("render", "unknown_scenario", scenario_id)
    principal, statements, read_only = scripts[scenario_id]
    isolation = (
        "serializable" if scenario_id in SERIALIZABLE_SCENARIOS else "read committed"
    )
    return _script(principal, statements, read_only=read_only, isolation=isolation)


def render_position_two_precondition(contract: dict[str, Any]) -> bytes:
    f = contract["fixture_namespace"]
    return _script(
        "context_producer",
        _producer_transaction(
            f,
            appointment="appointment_negative",
            command="command_position_two",
            audit="audit_position_two",
            event="event_position_two",
        ),
    )


def render_rollback_primary_precondition(contract: dict[str, Any]) -> bytes:
    f = contract["fixture_namespace"]
    packet = _packet(f).replace("__POSITION__", "2")
    return _script(
        "context_observer",
        [
            "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
            + _locator(f, "observer_rollback")
            + ",2,"
            + packet
            + ")).entry_kind;"
        ],
    )


def render_role_matrix(contract: dict[str, Any]) -> list[tuple[str, bytes]]:
    f = contract["fixture_namespace"]
    operations = [
        (
            "producer_direct_fabric_dml",
            "context_producer",
            "INSERT INTO emr4_context_fabric.context_observation_stream_head "
            "(practice_id,source_contract_id,stream_id,stream_epoch,last_position,updated_at) VALUES ("
            + _lit(f["practice_beta"])
            + "::pg_catalog.uuid,"
            + _lit(f["source_contract_id"])
            + ","
            + _lit(f["stream_beta"])
            + "::pg_catalog.uuid,1,0,pg_catalog.transaction_timestamp());",
        ),
        (
            "observer_foreign_entry_point",
            "context_observer",
            "SELECT emr4_context_fabric.project_update_confirm_reschedule_v1("
            + _lit(f["command_position_one"])
            + "::pg_catalog.uuid);",
        ),
        (
            "producer_trigger_execute",
            "context_producer",
            "SELECT emr4_context_fabric.cf_guard_alias_v1();",
        ),
        ("observer_set_role", "context_observer", "SET ROLE context_coordinator;"),
        (
            "application_read_direct_update",
            "context_application_read",
            "UPDATE emr4_context_fabric.context_frame_generation SET assembled_through_position=99;",
        ),
        (
            "coordinator_admission_direct_update",
            "context_coordinator",
            "UPDATE emr4_context_fabric.context_proofread_observation_admission "
            "SET decision=decision WHERE practice_id="
            + _lit(f["practice_alpha"])
            + "::pg_catalog.uuid AND stream_id="
            + _lit(f["stream_alpha"])
            + "::pg_catalog.uuid AND observer_id="
            + _lit(f["observer_happy"])
            + "::pg_catalog.uuid AND observer_generation=1 AND source_position=1 "
            "AND entry_kind='PRIMARY';",
        ),
        (
            "coordinator_recovery_anchor_direct_update",
            "context_coordinator",
            "UPDATE emr4_context_fabric.context_recovery_anchor "
            "SET lifecycle_revision=lifecycle_revision+1 WHERE practice_id="
            + _lit(f["practice_alpha"])
            + "::pg_catalog.uuid AND stream_id="
            + _lit(f["stream_alpha"])
            + "::pg_catalog.uuid;",
        ),
        (
            "lifecycle_recovery_anchor_direct_update",
            "context_lifecycle",
            "UPDATE emr4_context_fabric.context_recovery_anchor "
            "SET lifecycle_revision=lifecycle_revision+1 WHERE practice_id="
            + _lit(f["practice_alpha"])
            + "::pg_catalog.uuid AND stream_id="
            + _lit(f["stream_alpha"])
            + "::pg_catalog.uuid;",
        ),
        (
            "coordinator_outbox_direct_select",
            "context_coordinator",
            "SELECT count(*) FROM "
            "emr4_context_fabric.diary_context_observation_outbox_v1;",
        ),
    ]
    rendered: list[tuple[str, bytes]] = []
    for operation, principal, statement in operations:
        # The hostile SET ROLE is the only intentional appearance of the token.
        if operation == "observer_set_role":
            sql = (
                f"SET SESSION AUTHORIZATION {principal};\n"
                + "BEGIN ISOLATION LEVEL READ COMMITTED;\n"
                + _identity_select(principal)
                + "\n"
                + statement
                + "\nCOMMIT;\n"
            ).encode("utf-8")
        else:
            sql = _script(principal, [statement])
        rendered.append((operation, sql))
    return rendered


def _scenario_argv(
    docker: str, container_id: str, profile: dict[str, Any]
) -> list[str]:
    return parent._psql_base(  # noqa: SLF001
        docker, container_id, profile["postgres_database"], profile
    ) + ["--tuples-only", "--no-align", "--set", "VERBOSITY=verbose", "--file=-"]


def assert_scenario_argv(argv: list[str]) -> None:
    parent.assert_closed_argv(argv, parent.DockerOperation.PSQL_COMMAND)
    required = {"--file=-", "ON_ERROR_STOP=1", "VERBOSITY=verbose", "--no-psqlrc"}
    if not required.issubset(argv) or "--single-transaction" in argv:
        raise BehaviorFailure("command", "scenario_transport_not_closed")
    if any(token in argv for token in ("--command", "-c", "--variable")):
        raise BehaviorFailure("command", "caller_sql_surface")


def _scenario_call(
    runner: Runner, docker: str, container_id: str, profile: dict[str, Any], sql: bytes
) -> parent.ProcessResult:
    argv = _scenario_argv(docker, container_id, profile)
    assert_scenario_argv(argv)
    return runner(
        argv,
        sql,
        profile["command_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )


def _identity_from_stdout(
    result: parent.ProcessResult,
    principal: str,
    *,
    expected_read_only: bool | None = None,
    expected_isolation: str = "read committed",
) -> dict[str, Any]:
    identities: list[dict[str, Any]] = []
    for line in result.stdout.decode("utf-8", errors="strict").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and set(value) == {
            "expected_principal",
            "session_user",
            "current_user",
            "isolation",
            "read_only",
        }:
            identities.append(value)
    if expected_read_only is None:
        expected_read_only = principal == "context_application_read"
    expected = {
        "expected_principal": principal,
        "session_user": principal,
        "current_user": principal,
        "isolation": expected_isolation,
        "read_only": expected_read_only,
    }
    if not identities or any(row != expected for row in identities):
        raise BehaviorFailure("scenario", "session_identity", principal)
    return {
        "session_user": principal,
        "current_user": principal,
        "isolation": expected_isolation,
        "read_only": expected_read_only,
    }


def _transition_result_from_stdout(
    result: parent.ProcessResult, scenario_id: str
) -> str | None:
    expected = EXPECTED_TRANSITION_RESULT_KINDS.get(scenario_id)
    markers: list[dict[str, Any]] = []
    for raw_line in result.stdout.decode("utf-8", errors="strict").splitlines():
        line = raw_line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            if TRANSITION_RESULT_MARKER in line:
                raise BehaviorFailure(
                    "scenario", "transition_result_malformed", scenario_id
                )
            continue
        if isinstance(value, dict) and "marker" in value:
            if value.get("marker") != TRANSITION_RESULT_MARKER:
                raise BehaviorFailure(
                    "scenario", "transition_result_malformed", scenario_id
                )
            markers.append(value)
    if expected is None:
        if markers:
            raise BehaviorFailure(
                "scenario", "transition_result_unexpected", scenario_id
            )
        return None
    if not markers:
        raise BehaviorFailure("scenario", "transition_result_missing", scenario_id)
    if len(markers) != 1:
        raise BehaviorFailure("scenario", "transition_result_duplicate", scenario_id)
    marker = markers[0]
    expected_marker = {
        "marker": TRANSITION_RESULT_MARKER,
        "scenario_id": scenario_id,
        "result_kind": expected,
        "expected_result_kind": expected,
        "assertion": 1,
    }
    if (
        set(marker) != set(expected_marker)
        or marker != expected_marker
        or type(marker["assertion"]) is not int
    ):
        raise BehaviorFailure("scenario", "transition_result_mismatch", scenario_id)
    return expected


def _assert_rls_payload(result: parent.ProcessResult) -> None:
    expected = {
        "alpha_rows_visible": True,
        "beta_rows_invisible": True,
        "zero_unbound_rows_visible": True,
    }
    observed: list[dict[str, Any]] = []
    for line in result.stdout.decode("utf-8", errors="strict").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and set(value) == set(expected):
            observed.append(value)
    if observed != [expected]:
        raise BehaviorFailure("readback", "rls_projection_payload")


def _snapshot_sql() -> str:
    members: list[str] = []
    for relation in SNAPSHOT_RELATIONS:
        schema, table = relation.split(".", 1)
        if not IDENTIFIER.fullmatch(schema) or not IDENTIFIER.fullmatch(table):
            raise BehaviorFailure("render", "unsafe_snapshot_relation")
        members.append(
            _lit(relation) + ", (SELECT pg_catalog.json_build_object("
            "'count',pg_catalog.count(*),"
            "'digest','sha256:'||pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to("
            "COALESCE(pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY "
            "pg_catalog.to_jsonb(t)::pg_catalog.text)::pg_catalog.text,'[]'),'UTF8')),'hex')) "
            f"FROM {schema}.{table} AS t)"
        )
    return (
        "SELECT pg_catalog.json_build_object("
        + ",".join(members)
        + ")::pg_catalog.text"
    )


def _snapshot(
    runner: Runner, docker: str, container_id: str, profile: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    value = _query_json_bounded(
        runner,
        docker,
        container_id,
        profile["postgres_database"],
        profile,
        _snapshot_sql(),
        query_id="scenario_snapshot",
    )
    if not isinstance(value, dict) or set(value) != set(SNAPSHOT_RELATIONS):
        raise BehaviorFailure("readback", "snapshot_population")
    for relation, facts in value.items():
        if (
            not isinstance(facts, dict)
            or set(facts) != {"count", "digest"}
            or not isinstance(facts["count"], int)
            or facts["count"] < 0
            or not DIGEST.fullmatch(str(facts["digest"]))
        ):
            raise BehaviorFailure("readback", "snapshot_shape", relation)
    return value


def _query_json_bounded(
    runner: Runner,
    docker: str,
    container_id: str,
    database: str,
    profile: dict[str, Any],
    sql: str,
    *,
    query_id: str,
) -> Any:
    if not IDENTIFIER.fullmatch(query_id):
        raise BehaviorFailure("render", "query_id")
    wrapped = (
        "SET TRANSACTION READ ONLY;\n" + sql.rstrip().rstrip(";") + ";\n"
    ).encode("utf-8")
    argv = parent.docker_argv(
        parent.DockerOperation.PSQL_FILE,
        docker=docker,
        profile=profile,
        container_id=container_id,
        database=database,
    )
    result = parent._call(  # noqa: SLF001
        runner,
        argv,
        operation=parent.DockerOperation.PSQL_FILE,
        stdin=wrapped,
        timeout=profile["command_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if result.returncode != 0:
        detail = {"query_id": query_id}
        sqlstate = _safe_sqlstate(result)
        if sqlstate is not None:
            detail["sqlstate"] = sqlstate
        raise BehaviorFailure("readback", "query_failed", detail)
    text = result.stdout.decode("utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise BehaviorFailure("readback", "query_not_json", query_id) from error


def _catalogue_digests(facts: dict[str, Any]) -> dict[str, str]:
    return {
        name: "sha256:" + parent._facts_digest(value) for name, value in facts.items()
    }  # noqa: SLF001


def _assert_bound_parent_catalogue(
    facts: dict[str, Any],
    manifest: dict[str, Any],
    prerequisite: dict[str, Any],
    contract: dict[str, Any],
    *,
    expected_database: str,
) -> dict[str, Any]:
    """Reuse the accepted parent checks after proving this database binding."""

    server = facts.get("server")
    if not isinstance(server, dict):
        raise BehaviorFailure("catalogue", "server_or_database")
    try:
        server_version = int(server.get("server_version_num", 0))
    except (TypeError, ValueError) as error:
        raise BehaviorFailure("catalogue", "server_or_database") from error
    if server.get("database") != expected_database or not (
        160000 <= server_version < 170000
    ):
        raise BehaviorFailure("catalogue", "server_or_database")

    parent_facts = copy.deepcopy(facts)
    parent_facts["server"]["database"] = "emr4_synthetic_success"
    return parent._assert_catalogue(  # noqa: SLF001
        parent_facts, manifest, prerequisite, contract
    )


def _assert_fixture_catalogue_delta(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, str]:
    before_digests = _catalogue_digests(before)
    after_digests = _catalogue_digests(after)
    if set(before_digests) != set(after_digests):
        raise BehaviorFailure("fixture", "catalogue_population")
    changed = {
        name for name in before_digests if before_digests[name] != after_digests[name]
    }
    if changed != EXPECTED_FIXTURE_CATALOGUE_CHANGES:
        raise BehaviorFailure("fixture", "catalogue_delta", ",".join(sorted(changed)))
    return after_digests


def _assert_post_behavior_catalogue_stability(
    before_digests: dict[str, str], after: dict[str, Any]
) -> None:
    after_digests = _catalogue_digests(after)
    if set(before_digests) != set(after_digests):
        raise BehaviorFailure("catalogue", "post_behavior_population")
    changed = {
        name for name in before_digests if before_digests[name] != after_digests[name]
    }
    if changed != EXPECTED_POST_BEHAVIOR_CATALOGUE_CHANGES:
        raise BehaviorFailure(
            "catalogue", "post_behavior_drift", ",".join(sorted(changed))
        )


def _assert_fixture_privileges(
    runner: Runner, docker: str, container_id: str, profile: dict[str, Any]
) -> None:
    sql = (
        "SELECT pg_catalog.json_build_object('checks',ARRAY["
        "pg_catalog.has_table_privilege('context_producer','public.appointments','SELECT,INSERT,UPDATE'),"
        "pg_catalog.has_table_privilege('context_producer','public.appointment_command_idempotency','SELECT,INSERT,UPDATE,DELETE'),"
        "pg_catalog.has_table_privilege('context_producer','public.appointment_audit_log','SELECT,INSERT,UPDATE,DELETE'),"
        "pg_catalog.has_table_privilege('context_producer','public.diary_committed_events','SELECT,INSERT,UPDATE,DELETE'),"
        "NOT pg_catalog.has_table_privilege('context_producer','emr4_context_fabric.context_observation_stream_head','INSERT,UPDATE,DELETE')"
        "])::pg_catalog.text"
    )
    value = parent._query_json(  # noqa: SLF001
        runner, docker, container_id, profile["postgres_database"], profile, sql
    )
    if not isinstance(value, dict) or value.get("checks") != [
        True,
        True,
        True,
        True,
        True,
    ]:
        raise BehaviorFailure("fixture", "privilege_matrix")


def _assert_delta(
    scenario_id: str,
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
) -> None:
    expected = EXPECTED_DELTAS.get(scenario_id, {})
    allowed = ALLOWED_DIGEST_CHANGES.get(scenario_id, set())
    for relation in SNAPSHOT_RELATIONS:
        delta = after[relation]["count"] - before[relation]["count"]
        if delta != expected.get(relation, 0):
            raise BehaviorFailure(
                "readback", "unexpected_relation_delta", f"{scenario_id}:{relation}"
            )
        changed = after[relation]["digest"] != before[relation]["digest"]
        if changed and relation not in allowed:
            raise BehaviorFailure(
                "readback", "forbidden_relation_change", f"{scenario_id}:{relation}"
            )
        if (
            (delta != 0 or relation in allowed)
            and scenario_id
            not in {
                "BTR-E05",
            }
            and not changed
        ):
            raise BehaviorFailure(
                "readback",
                "expected_relation_change_absent",
                f"{scenario_id}:{relation}",
            )


def _probe_sql(contract: dict[str, Any], scenario_id: str) -> str:
    f = contract["fixture_namespace"]
    p = _lit(f["practice_alpha"]) + "::pg_catalog.uuid"
    s = _lit(f["stream_alpha"]) + "::pg_catalog.uuid"
    probes: dict[str, list[str]] = {
        "BTR-E01": [
            f"(SELECT count(*)=1 AND min(barrier_revision)=3 AND max(barrier_revision)=3 FROM emr4_context_fabric.context_generation_registry_barrier WHERE practice_id={p} AND stream_id={s})",
            f"(SELECT count(*)=3 FROM emr4_context_fabric.context_observer_generation WHERE practice_id={p} AND stream_id={s})",
            f"(SELECT count(*)=3 AND min(last_contiguous_position)=0 AND max(last_contiguous_position)=0 FROM emr4_context_fabric.context_durability_checkpoint WHERE practice_id={p} AND stream_id={s})",
            f"(SELECT count(*)=1 AND min(last_position)=0 AND max(last_position)=0 FROM emr4_context_fabric.context_observation_stream_head WHERE practice_id={p} AND stream_id={s})",
            f"(SELECT count(*)=3 FROM emr4_context_fabric.context_recovery_anchor WHERE practice_id={p} AND stream_id={s} AND lifecycle_revision=0)",
            f"(SELECT count(*)=3 FROM emr4_context_fabric.context_observation_key_interval WHERE practice_id={p} AND stream_id={s} AND interval_start=1 AND interval_end=100)",
        ],
        "BTR-E02": [
            f"(SELECT count(*)=1 FROM public.appointments WHERE id={_lit(f['appointment_temporal'])}::pg_catalog.uuid AND start_time={_lit(f['rescheduled_start'])}::pg_catalog.timestamptz)",
            f"(SELECT count(*)=1 FROM public.appointment_command_idempotency WHERE id={_lit(f['command_position_one'])}::pg_catalog.uuid AND state='completed')",
            f"(SELECT count(*)=1 FROM public.appointment_audit_log WHERE id={_lit(f['audit_position_one'])}::pg_catalog.uuid)",
            f"(SELECT count(*)=1 FROM public.diary_committed_events WHERE id={_lit(f['event_position_one'])}::pg_catalog.uuid)",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.diary_context_aggregate_aliases_v1 WHERE product_appointment_uuid={_lit(f['appointment_temporal'])}::pg_catalog.uuid)",
            f"(SELECT count(*)=1 AND min(last_position)=1 FROM emr4_context_fabric.context_observation_stream_head WHERE practice_id={p} AND stream_id={s})",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.diary_context_observation_outbox_v1 WHERE practice_id={p} AND stream_id={s} AND transaction_position=1 AND raw_event_uuid={_lit(f['event_position_one'])}::pg_catalog.uuid)",
        ],
        "BTR-E03": [
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND source_position=1 AND entry_kind='PRIMARY')",
            f"(SELECT count(*)=0 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND source_position=1 AND entry_kind='CONFLICT')",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_proofread_observation_admission a WHERE a.observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND a.source_position=1 AND a.source_membership_digest={_source_membership_digest_subquery(f, '1')})",
        ],
        "BTR-I01": [
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND source_position=1 AND entry_kind='PRIMARY')",
            f"(SELECT count(*)=0 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND source_position=1 AND entry_kind='CONFLICT')",
        ],
        "BTR-E04": [
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_classified_observation_receipt WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND source_position=1)",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_durability_checkpoint WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND last_contiguous_position=1)",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_invalidation_watermark WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND frame_type='CURRENT_DIARY_PROJECTION' AND watermark_position=1)",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_frame_generation WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND frame_type='CURRENT_DIARY_PROJECTION' AND lifecycle_state='RETIRED')",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_reassembly_obligation WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND obligation_state='PENDING')",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_durability_lifecycle WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND entry_kind='DECISION')",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_durability_audit WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid)",
        ],
        "BTR-I03": [
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_classified_observation_receipt WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid AND source_position=1)",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_reassembly_obligation WHERE observer_id={_lit(f['observer_happy'])}::pg_catalog.uuid)",
        ],
        "BTR-E05": [
            f"(SELECT count(*)=1 FROM public.appointments WHERE id={_lit(f['appointment_non_temporal'])}::pg_catalog.uuid AND location_id={_lit(f['location_beta'])}::pg_catalog.uuid)",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.diary_context_observation_outbox_v1 WHERE practice_id={p} AND stream_id={s})",
        ],
        "BTR-I02": [
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_conflict'])}::pg_catalog.uuid AND source_position=2 AND entry_kind='PRIMARY')",
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_conflict'])}::pg_catalog.uuid AND source_position=2 AND entry_kind='CONFLICT')",
            f"(SELECT count(*)=2 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_conflict'])}::pg_catalog.uuid AND source_position=2)",
        ],
        "BTR-R03": [
            "(SELECT count(*)=0 FROM pg_catalog.pg_auth_members WHERE member IN (SELECT oid FROM pg_catalog.pg_roles WHERE rolname LIKE 'context_%'))",
            "(SELECT pg_catalog.bool_and(NOT rolbypassrls) FROM pg_catalog.pg_roles WHERE rolname LIKE 'context_%')",
        ],
        "BTR-B03": [
            f"(SELECT count(*)=1 FROM emr4_context_fabric.context_proofread_observation_admission WHERE observer_id={_lit(f['observer_rollback'])}::pg_catalog.uuid AND source_position=2 AND entry_kind='PRIMARY')",
            f"(SELECT count(*)=0 FROM emr4_context_fabric.context_classified_observation_receipt WHERE observer_id={_lit(f['observer_rollback'])}::pg_catalog.uuid)",
        ],
    }
    expressions = probes.get(scenario_id, ["TRUE"])
    return (
        "SELECT pg_catalog.json_build_object('checks',ARRAY["
        + ",".join(expressions)
        + "])::pg_catalog.text"
    )


def _probe(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    scenario_id: str,
) -> None:
    value = parent._query_json(  # noqa: SLF001
        runner,
        docker,
        container_id,
        profile["postgres_database"],
        profile,
        _probe_sql(contract, scenario_id),
    )
    if (
        not isinstance(value, dict)
        or set(value) != {"checks"}
        or not value["checks"]
        or not all(item is True for item in value["checks"])
    ):
        raise BehaviorFailure("readback", "scenario_probe", scenario_id)


def _bounded_outcome(
    result: parent.ProcessResult, expected_sqlstate: str | None, scenario_id: str
) -> tuple[str | None, dict[str, Any]]:
    result_kind = _transition_result_from_stdout(result, scenario_id)
    bounded = parent._bounded_psql_rejection(  # noqa: SLF001
        result, max_error_line=1000, max_error_position=131072
    )
    observed = bounded["observed_sqlstates"]
    if expected_sqlstate is None:
        if result.returncode != 0 or observed:
            detail = {"scenario_id": scenario_id}
            sqlstate = _safe_sqlstate(result)
            if sqlstate is not None:
                detail["sqlstate"] = sqlstate
            detail.update(_safe_plpgsql_coordinate(result, scenario_id))
            raise BehaviorFailure("scenario", "unexpected_rejection", detail)
        transport = {
            "psql_exit": result.returncode,
            "stderr_digest": bounded["stderr"],
        }
        if result_kind is not None:
            transport["result_kind"] = result_kind
        return None, transport
    if result.returncode == 0 or observed != [expected_sqlstate]:
        raise BehaviorFailure("scenario", "sqlstate_mismatch", expected_sqlstate)
    transport = {
        "psql_exit": result.returncode,
        "stderr_digest": bounded["stderr"],
    }
    if result_kind is not None:
        transport["result_kind"] = result_kind
    return expected_sqlstate, transport


def _run_precondition(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    sql: bytes,
    name: str,
) -> None:
    result = _scenario_call(runner, docker, container_id, profile, sql)
    if result.returncode != 0 or parent._observed_sqlstates(result.stderr):  # noqa: SLF001
        raise BehaviorFailure("precondition", "failed", name)


def _run_role_matrix(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for operation, sql in render_role_matrix(contract):
        principal_match = re.search(
            rb"SET SESSION AUTHORIZATION ([a-z][a-z0-9_]*);", sql
        )
        if principal_match is None:
            raise BehaviorFailure("render", "role_matrix_principal")
        principal = principal_match.group(1).decode("ascii")
        result = _scenario_call(runner, docker, container_id, profile, sql)
        identity = _identity_from_stdout(result, principal, expected_read_only=False)
        sqlstates = parent._observed_sqlstates(result.stderr)  # noqa: SLF001
        if result.returncode == 0 or sqlstates != ["42501"]:
            raise BehaviorFailure("scenario", "role_matrix_sqlstate", operation)
        evidence.append(
            {
                "operation": operation,
                "principal": principal,
                **identity,
                "sqlstate": "42501",
                "stderr_digest": parent._bounded_digest(result.stderr),  # noqa: SLF001
            }
        )
    return evidence


def _run_scenarios(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    preconditions: list[str] = []
    for scenario in contract["scenarios"]:
        scenario_id = scenario["id"]
        if scenario_id == "BTR-I02":
            _run_precondition(
                runner,
                docker,
                container_id,
                profile,
                render_position_two_precondition(contract),
                "position_two_projected",
            )
            preconditions.append("position_two_projected")
        if scenario_id == "BTR-B03":
            _run_precondition(
                runner,
                docker,
                container_id,
                profile,
                render_rollback_primary_precondition(contract),
                "rollback_primary_precommitted",
            )
            preconditions.append("rollback_primary_precommitted")
        before = _snapshot(runner, docker, container_id, profile)
        if scenario_id == "BTR-R03":
            matrix = _run_role_matrix(runner, docker, container_id, profile, contract)
            identity: dict[str, Any] = {
                "session_user": "role_matrix",
                "current_user": "role_matrix",
                "isolation": "read committed",
                "read_only": False,
            }
            observed_sqlstate = "42501"
            transport: dict[str, Any] = {"matrix": matrix, "psql_exit": 3}
        else:
            result = _scenario_call(
                runner,
                docker,
                container_id,
                profile,
                render_scenario_sql(contract, scenario_id),
            )
            expected_isolation = (
                "serializable"
                if scenario_id in SERIALIZABLE_SCENARIOS
                else "read committed"
            )
            identity = _identity_from_stdout(
                result,
                scenario["principal"],
                expected_isolation=expected_isolation,
            )
            if scenario_id == "BTR-R01":
                _assert_rls_payload(result)
            observed_sqlstate, transport = _bounded_outcome(
                result, scenario["expected_sqlstate"], scenario_id
            )
        after = _snapshot(runner, docker, container_id, profile)
        _assert_delta(scenario_id, before, after)
        _probe(runner, docker, container_id, profile, contract, scenario_id)
        records.append(
            {
                "scenario_id": scenario_id,
                "category": scenario["category"],
                "principal": scenario["principal"],
                "transaction_shape": scenario["transaction_shape"],
                "expected_outcome": scenario["expected_outcome"],
                "observed_outcome": scenario["expected_outcome"],
                "expected_sqlstate": scenario["expected_sqlstate"],
                "observed_sqlstate": observed_sqlstate,
                "expected_failure_id": scenario["expected_failure_id"],
                "observed_failure_id": (
                    scenario["expected_failure_id"]
                    if observed_sqlstate is not None
                    else None
                ),
                "stable_reason": STABLE_REASONS[observed_sqlstate],
                **identity,
                "before": before,
                "after": after,
                "readback_checks": {name: True for name in scenario["readback"]},
                "forbidden_effects_absent": {
                    name: True for name in scenario["forbidden_effects"]
                },
                "transport": transport,
                "passed": True,
            }
        )
    return records, preconditions


def run_rehearsal(*, runner: Runner = parent._subprocess_runner) -> dict[str, Any]:  # noqa: SLF001
    started = time.monotonic()
    attempt_id = secrets.token_hex(12)
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {
        "status": "not_needed",
        "removed": False,
        "absence_verified": False,
    }
    environment: dict[str, Any] = {
        "docker_client": "unresolved",
        "image": "uninspected",
    }
    parent_evidence: dict[str, Any] = {}
    scenario_records: list[dict[str, Any]] = []
    preconditions: list[str] = []
    failure: BehaviorFailure | parent.RehearsalFailure | None = None
    result = "rehearsal_failed"
    container_id = image_id = name = nonce = docker = ""
    contract: dict[str, Any] = {}
    profile: dict[str, Any] = {}
    cleanup_runner = runner
    try:
        contract, prerequisite, manifest, artifact = _validate_contract()
        profile = _profile()
        cleanup_reserve = 3 * profile["cleanup_timeout_seconds"]
        execution_seconds = profile["total_timeout_seconds"] - cleanup_reserve
        if execution_seconds <= profile["artifact_timeout_seconds"]:
            raise BehaviorFailure("contract", "total_timeout_budget")
        runner = parent._with_total_deadline(runner, started + execution_seconds)  # noqa: SLF001
        prerequisite_sql = parent.render_prerequisite_sql(prerequisite)
        parent_evidence = {
            "behavior_contract_sha256": parent._canonical_sha(contract),  # noqa: SLF001
            "artifact_sha256": _sha256(artifact),
            "manifest_sha256": _sha256(
                _canonical_bytes(ROOT / contract["parent_bindings"][2]["path"])
            ),
            "prerequisite_sha256": _sha256(_canonical_bytes(PREREQUISITE_PATH)),
            "statement_count": manifest["statement_count"],
        }
        lifecycle.append("five_parent_bindings_verified")
        docker = shutil.which(profile["executable"]) or ""
        if not docker or Path(docker).name.lower() != "docker.exe":
            raise BehaviorFailure("environment", "docker_client_missing")
        environment["docker_client"] = "resolved_exact_docker_exe"
        image_result = parent._call(  # noqa: SLF001
            runner,
            parent.docker_argv(
                parent.DockerOperation.IMAGE_INSPECT, docker=docker, profile=profile
            ),
            operation=parent.DockerOperation.IMAGE_INSPECT,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if image_result.returncode != 0:
            raise BehaviorFailure("environment", "exact_local_image_unavailable")
        image = parent._one_json(image_result, "image_inspect")  # noqa: SLF001
        image_id = str(image.get("Id", ""))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
            raise BehaviorFailure("environment", "image_id_invalid")
        environment["image"] = {
            "reference": profile["image_reference"],
            "id": image_id,
            "pull_attempted": False,
        }
        nonce = secrets.token_hex(16)
        name = profile["container_name_prefix"] + secrets.token_hex(8)
        absent = parent._call(  # noqa: SLF001
            runner,
            parent.docker_argv(
                parent.DockerOperation.NAME_INSPECT,
                docker=docker,
                profile=profile,
                name=name,
            ),
            operation=parent.DockerOperation.NAME_INSPECT,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if not parent._is_exact_absence(absent):  # noqa: SLF001
            raise BehaviorFailure("environment", "container_name_not_proven_absent")
        run_argv = _run_argv(docker, profile, name=name, nonce=nonce)
        assert_run_argv(run_argv)
        created = runner(
            run_argv,
            None,
            profile["command_timeout_seconds"],
            profile["stdout_stderr_cap_bytes"],
        )
        if created.returncode != 0:
            raise BehaviorFailure("container", "create_failed")
        container_id = created.stdout.decode("ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{12,64}", container_id):
            raise BehaviorFailure("container", "created_id_invalid")
        inspected = parent._one_json(  # noqa: SLF001
            parent._call(  # noqa: SLF001
                runner,
                parent.docker_argv(
                    parent.DockerOperation.ID_INSPECT,
                    docker=docker,
                    profile=profile,
                    container_id=container_id,
                ),
                operation=parent.DockerOperation.ID_INSPECT,
                stdin=None,
                timeout=profile["command_timeout_seconds"],
                cap=profile["stdout_stderr_cap_bytes"],
            ),
            "container_inspect",
        )
        if not _behavior_container_owned(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
        ):
            raise BehaviorFailure("container", "containment_mismatch")
        lifecycle.append("container_owned")
        for init_stage, init_argv, init_stdin in _init_argvs(
            docker, container_id, profile
        ):
            assert_init_argv(init_argv, init_stdin)
            initialized = runner(
                init_argv,
                init_stdin,
                profile["startup_timeout_seconds"],
                profile["stdout_stderr_cap_bytes"],
            )
            if initialized.returncode != 0:
                raise BehaviorFailure("postgres_init", init_stage)
        lifecycle.append("passwordless_peer_cluster_started")
        environment["readiness"] = {}
        readiness_profile = copy.deepcopy(profile)
        readiness_profile["postgres_database"] = "postgres"
        parent._wait_for_stable_postgres(  # noqa: SLF001
            runner,
            docker,
            container_id,
            readiness_profile,
            observation=environment["readiness"],
        )
        lifecycle.append("postgres_ready")
        create_database = parent._call(  # noqa: SLF001
            runner,
            parent.docker_argv(
                parent.DockerOperation.PSQL_COMMAND,
                docker=docker,
                profile=readiness_profile,
                container_id=container_id,
                database="postgres",
                sql_command='CREATE DATABASE "emr4_synthetic_behavior";',
            ),
            operation=parent.DockerOperation.PSQL_COMMAND,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if create_database.returncode != 0:
            raise BehaviorFailure("postgres", "database_create_failed")
        lifecycle.append("behavior_database_ready")
        parent._install_prerequisites(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
            prerequisite_sql,
        )
        admitted = parent._stream_artifact(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
            artifact,
        )
        if admitted.returncode != 0:
            raise BehaviorFailure("artifact", "postgresql_rejected")
        lifecycle.append("artifact_admitted")
        catalogue = parent._read_catalogue(  # noqa: SLF001
            runner, docker, container_id, profile["postgres_database"], profile
        )
        parent_contract = _json(PARENT_REHEARSAL_CONTRACT_PATH)
        _assert_bound_parent_catalogue(
            catalogue,
            manifest,
            prerequisite,
            parent_contract,
            expected_database=profile["postgres_database"],
        )
        lifecycle.append("catalogue_reconciled")
        bootstrap = _scenario_call(
            runner, docker, container_id, profile, render_bootstrap_sql(contract)
        )
        if bootstrap.returncode != 0:
            raise BehaviorFailure(
                "fixture",
                "bootstrap_failed",
                _safe_bootstrap_failure_metadata(bootstrap),
            )
        fixture_catalogue = parent._read_catalogue(  # noqa: SLF001
            runner, docker, container_id, profile["postgres_database"], profile
        )
        fixture_catalogue_digests = _assert_fixture_catalogue_delta(
            catalogue, fixture_catalogue
        )
        _assert_fixture_privileges(runner, docker, container_id, profile)
        lifecycle.append("fixtures_closed")
        scenario_records, preconditions = _run_scenarios(
            runner, docker, container_id, profile, contract
        )
        if [row["scenario_id"] for row in scenario_records] != contract[
            "scenario_order"
        ]:
            raise BehaviorFailure("scenario", "terminal_order")
        final_catalogue = parent._read_catalogue(  # noqa: SLF001
            runner, docker, container_id, profile["postgres_database"], profile
        )
        _assert_post_behavior_catalogue_stability(
            fixture_catalogue_digests, final_catalogue
        )
        lifecycle.extend(
            ["twenty_scenarios_matched", "catalogue_reconciled_after_behavior"]
        )
        result = PASS_RESULT
    except (BehaviorFailure, parent.RehearsalFailure) as error:
        failure = error
        if error.stage == "environment":
            result = "environment_unavailable"
    finally:
        if container_id:
            try:
                cleanup = _cleanup(
                    cleanup_runner, docker, container_id, name, nonce, image_id, profile
                )
                if cleanup.get("absence_verified"):
                    lifecycle.append("cleanup_verified")
                else:
                    result = "cleanup_ownership_unverified"
            except parent.RehearsalFailure as cleanup_error:
                cleanup = {
                    "status": "cleanup_failed",
                    "removed": False,
                    "absence_verified": False,
                    "failure_stage": cleanup_error.stage,
                    "failure_code": cleanup_error.code,
                }
                result = "rehearsal_failed"
                if failure is None:
                    failure = cleanup_error
        if result == PASS_RESULT and cleanup.get("absence_verified"):
            lifecycle.append("passed")
        elif result == PASS_RESULT:
            result = "rehearsal_failed"
    evidence: dict[str, Any] = {
        "schema_version": "emr4.raisa-context-fabric-disposable-postgresql-behavior-transaction-evidence.v1",
        "result": result,
        "evidence_mode": EVIDENCE_MODE,
        "attempt_id": attempt_id,
        "parent": parent_evidence,
        "environment": environment,
        "lifecycle": lifecycle,
        "preconditions": preconditions,
        "scenarios": scenario_records,
        "scenario_reconciliation": {
            "expected": 20,
            "observed": len(scenario_records),
            "passed": sum(1 for row in scenario_records if row.get("passed")),
        },
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if failure is not None:
        detail = failure.detail
        detail_bytes = (
            json.dumps(detail, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if isinstance(detail, dict)
            else str(detail).encode("utf-8")
        )
        failure_evidence = {
            "stage": failure.stage,
            "code": failure.code,
            "detail_digest": _sha256(detail_bytes),
        }
        if isinstance(detail, dict):
            for name in (
                "sqlstate",
                "coordinate_status",
                "relation",
                "column",
                "query_id",
                "scenario_id",
                "function_id",
            ):
                if isinstance(detail.get(name), str):
                    failure_evidence[name] = detail[name]
            if (
                isinstance(detail.get("function_line"), int)
                and not isinstance(detail.get("function_line"), bool)
                and 1 <= detail["function_line"] <= 100000
            ):
                failure_evidence["function_line"] = detail["function_line"]
        elif SQLSTATE.fullmatch(str(detail)):
            failure_evidence["sqlstate"] = str(detail)
        evidence["environment"]["failure"] = failure_evidence
    evidence["environment"]["elapsed_ms"] = int((time.monotonic() - started) * 1000)
    return evidence


def write_evidence(payload: dict[str, Any]) -> None:
    EVIDENCE_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    if len(sys.argv) != 1:
        print("This fixed-path harness accepts no arguments.", file=sys.stderr)
        return 2
    evidence = run_rehearsal()
    write_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "evidence": EVIDENCE_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 2


if __name__ == "__main__":
    raise SystemExit(main())
