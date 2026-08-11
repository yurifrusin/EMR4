#!/usr/bin/env python3
"""Run the fixed CF-D2 provider-free restart and unknown-commit rehearsal."""

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
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal as serial,
)
from scripts import (  # noqa: E402
    raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal as concurrency,
)


BASE = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal"
)
CONTRACT_PATH = BASE / "restart-unknown-commit-rehearsal-contract.json"
EVIDENCE_SCHEMA_PATH = (
    BASE / "provider-free-durability-restart-unknown-commit-evidence.schema.json"
)
RECOVERY_CONTRACT_PATH = (
    BASE / "restart-unknown-commit-recovery-descendant-contract.json"
)
RECOVERY_CONTRACT_SCHEMA_PATH = (
    BASE / "restart-unknown-commit-recovery-descendant-contract.schema.json"
)
DIAGNOSTIC_EVIDENCE_SCHEMA_PATH = BASE / (
    "provider-free-durability-restart-unknown-commit-recovery-diagnostic-evidence.schema.json"
)
DIAGNOSTIC_EVIDENCE_PATH = BASE / (
    "provider-free-durability-restart-unknown-commit-recovery-diagnostic-evidence-attempt-002.json"
)
EVIDENCE_PATH = (
    BASE / "provider-free-durability-restart-unknown-commit-evidence-attempt-003.json"
)
EXPECTED_CONTRACT_SHA256 = (
    "sha256:40bb9f341c183c84bee96f63d000282b149b0b55f4a0a1e9ab49308b4e843c99"
)
EXPECTED_RECOVERY_CONTRACT_SHA256 = (
    "sha256:2535884cad0cb4789396f2ae12989c1448cc74c5cba80c8fc3ec7a708d1f9ec7"
)
PASS_RESULT = "raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_pass"
DIAGNOSTIC_PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_"
    "no_crash_first_sequence_diagnostic_pass"
)
EVIDENCE_MODE = "provider_free_disposable_postgresql_authored_synthetic_restart_unknown_commit_recovery"
DIAGNOSTIC_EVIDENCE_MODE = (
    "provider_free_disposable_postgresql_authored_synthetic_no_crash_"
    "first_sequence_diagnostic"
)
CLAIM_BOUNDARY = (
    "four_fixed_postgresql16_sigkill_same_cluster_restart_outcomes_only_no_literal_"
    "wal_ack_boundary_power_loss_driver_pool_operational_runtime_product_provider_"
    "command_deployment_production_release_or_protected_ref_claim"
)
DIAGNOSTIC_CLAIM_BOUNDARY = (
    "exact_r01_position_one_apply_and_lifecycle_revision_one_anchor_sequence_without_crash_"
    "only_no_restart_unknown_commit_wal_driver_pool_operational_runtime_product_"
    "provider_command_deployment_production_release_or_protected_ref_claim"
)
SCENARIO_ORDER = ("CFD2-R01", "CFD2-R02", "CFD2-R03", "CFD2-R04")
RESULT_VOCABULARY = frozenset(
    {"PRIMARY", "RECEIPT_APPLIED", "RECEIPT_REPLAYED", "1", "2"}
)
ALLOWED_SQLSTATES = frozenset({"P0001", "CF303"})
APPLICATION_LABEL = re.compile(r"^emr4_cf_d2_r0[1-4]_[cru]$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]{0,62}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
Runner = Callable[[list[str], bytes | None, float, int], serial.parent.ProcessResult]

PACKET_RELATIONS = (
    "admission",
    "receipt",
    "checkpoint",
    "lifecycle",
    "audit",
    "watermark",
    "frame",
    "obligation",
    "anchor",
)
TRANSITION_INSERTS = frozenset({"receipt", "lifecycle", "audit", "obligation"})
TRANSITION_UPDATES = frozenset({"checkpoint", "watermark", "frame"})
TRANSITION_UNCHANGED = frozenset({"admission", "anchor"})


class RestartFailure(serial.BehaviorFailure):
    """Closed failure for the CF-D2 harness."""


class TerminalFailure(RestartFailure):
    """Closed coordinate-specific participant terminal failure."""

    def __init__(
        self,
        coordinate: str,
        code: str,
        result: serial.parent.ProcessResult,
    ) -> None:
        super().__init__(coordinate, code)
        observed_sqlstate = serial._safe_sqlstate(result)  # noqa: SLF001
        self.terminal_evidence = {
            "coordinate": coordinate,
            "code": code,
            "returncode_class": "zero" if result.returncode == 0 else "nonzero",
            "sqlstate": (
                observed_sqlstate if observed_sqlstate in ALLOWED_SQLSTATES else None
            ),
            "result_lines": _result_lines(result)[:2],
        }


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_recovery_contract() -> dict[str, Any]:
    contract = _json(RECOVERY_CONTRACT_PATH)
    schema = _json(RECOVERY_CONTRACT_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(contract),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise RestartFailure("recovery_contract", "schema_validation")
    if _canonical_sha(contract) != EXPECTED_RECOVERY_CONTRACT_SHA256:
        raise RestartFailure("recovery_contract", "digest_mismatch")
    coordinates = contract.get("terminal_coordinates")
    if not isinstance(coordinates, list) or len(coordinates) != 27:
        raise RestartFailure("recovery_contract", "terminal_coordinates")
    return contract


def _assert_terminal_coordinate(coordinate: str, contract: dict[str, Any]) -> None:
    coordinates = contract.get("terminal_coordinates", [])
    if not IDENTIFIER.fullmatch(coordinate) or coordinate not in coordinates:
        raise RestartFailure("terminal_coordinate", "not_allowlisted")


def _source_head() -> str:
    git = shutil.which("git.exe") or shutil.which("git") or ""
    if not git:
        raise RestartFailure("source", "git_missing")
    result = subprocess.run(
        [git, "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        timeout=5,
        shell=False,
    )
    value = result.stdout.decode("ascii", errors="ignore").strip()
    if result.returncode != 0 or not HEX40.fullmatch(value):
        raise RestartFailure("source", "head_unavailable")
    return value


def _validate_contract() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], bytes
]:
    contract = _json(CONTRACT_PATH)
    if _canonical_sha(contract) != EXPECTED_CONTRACT_SHA256:
        raise RestartFailure("contract", "contract_sha256")
    if contract.get("status") != "frozen_provider_free_planning_runtime_closed":
        raise RestartFailure("contract", "status")
    if tuple(contract.get("scenario_order", ())) != SCENARIO_ORDER:
        raise RestartFailure("contract", "scenario_order")
    scenarios = contract.get("scenarios")
    if (
        not isinstance(scenarios, list)
        or tuple(row.get("id") for row in scenarios if isinstance(row, dict))
        != SCENARIO_ORDER
    ):
        raise RestartFailure("contract", "scenario_population")
    bindings = contract.get("parent_bindings")
    if not isinstance(bindings, list) or len(bindings) != 8:
        raise RestartFailure("parent", "binding_population")
    if len({row.get("id") for row in bindings if isinstance(row, dict)}) != 8:
        raise RestartFailure("parent", "binding_ids")
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"id", "path", "sha256"}:
            raise RestartFailure("parent", "binding_shape")
        relative = Path(binding["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RestartFailure("parent", "binding_path")
        path = ROOT / relative
        if not path.is_file() or _file_digest(path) != binding["sha256"]:
            raise RestartFailure("parent", "binding_sha256", str(binding["id"]))
    concurrency_contract, serial_contract, prerequisite, manifest, artifact = (
        concurrency._validate_contract()  # noqa: SLF001
    )
    expected_concurrency = next(
        row["sha256"] for row in bindings if row["id"] == "current_concurrency_contract"
    )
    if _file_digest(
        concurrency.CONTRACT_PATH
    ) != expected_concurrency or concurrency_contract != _json(
        concurrency.CONTRACT_PATH
    ):
        raise RestartFailure("parent", "concurrency_contract_identity")
    if manifest.get("statement_count") != 424:
        raise RestartFailure("parent", "statement_count")
    return contract, serial_contract, prerequisite, manifest, artifact


def _profile() -> dict[str, Any]:
    profile = copy.deepcopy(serial._profile())  # noqa: SLF001
    profile.update(
        {
            "container_name_prefix": "emr4-cf-pg16-restart-",
            "ownership_labels": {
                "com.emr4.harness": "disposable-postgresql-durability-restart-v1",
                "com.emr4.cleanup-nonce": "per_run_random_hex",
            },
            "postgres_database": "emr4_synthetic_restart",
            "pgdata": "/var/lib/postgresql/cf_d2_pgdata",
            "tmpfs": "/var/lib/postgresql/data:rw,noexec,nosuid,nodev,size=67108864",
            "startup_timeout_seconds": 15,
            "readiness_stability_seconds": 1,
            "artifact_timeout_seconds": 120,
            "total_timeout_seconds": 600,
        }
    )
    return profile


def _run_argv(
    docker: str, profile: dict[str, Any], *, name: str, nonce: str
) -> list[str]:
    argv = serial._run_argv(docker, profile, name=name, nonce=nonce)  # noqa: SLF001
    serial.assert_run_argv(argv)
    if any(token in argv for token in ("--volume", "-v", "--publish", "-p", "--mount")):
        raise RestartFailure("command", "persistent_or_port_mount")
    if argv.count("--network=none") != 1 or argv.count("--pull=never") != 1:
        raise RestartFailure("command", "containment_flag")
    return argv


def _init_argvs(
    docker: str, container_id: str, profile: dict[str, Any]
) -> list[tuple[str, list[str], bytes | None]]:
    rendered = serial._init_argvs(docker, container_id, profile)  # noqa: SLF001
    result: list[tuple[str, list[str], bytes | None]] = []
    for stage, argv, stdin in rendered:
        argv = list(argv)
        if stage == "initdb":
            if "--data-checksums" in argv:
                raise RestartFailure("command", "duplicate_checksum_flag")
            argv.append("--data-checksums")
        serial.assert_init_argv(argv, stdin)
        result.append((stage, argv, stdin))
    if sum("--data-checksums" in argv for _, argv, _ in result) != 1:
        raise RestartFailure("command", "checksum_flag_missing")
    return result


def _postgres_start_argv(
    docker: str, container_id: str, profile: dict[str, Any]
) -> list[str]:
    rows = _init_argvs(docker, container_id, profile)
    matches = [
        argv
        for stage, argv, stdin in rows
        if stage == "postgres_start" and stdin is None
    ]
    if len(matches) != 1:
        raise RestartFailure("command", "postgres_start_shape")
    return matches[0]


def _kill_argv(docker: str, container_id: str) -> list[str]:
    if not re.fullmatch(r"[0-9a-f]{12,64}", container_id):
        raise RestartFailure("command", "container_id")
    return [docker, "container", "kill", "--signal=KILL", container_id]


def _start_argv(docker: str, container_id: str) -> list[str]:
    if not re.fullmatch(r"[0-9a-f]{12,64}", container_id):
        raise RestartFailure("command", "container_id")
    return [docker, "container", "start", container_id]


def _label_absence_argv(docker: str, profile: dict[str, Any], nonce: str) -> list[str]:
    if not re.fullmatch(r"[0-9a-f]{32}", nonce):
        raise RestartFailure("command", "cleanup_nonce")
    label = profile["ownership_labels"]["com.emr4.harness"]
    if not re.fullmatch(r"[a-z0-9-]{1,95}", label):
        raise RestartFailure("command", "cleanup_label")
    return [
        docker,
        "container",
        "ls",
        "--all",
        "--no-trunc",
        "--quiet",
        "--filter",
        f"label=com.emr4.harness={label}",
        "--filter",
        f"label=com.emr4.cleanup-nonce={nonce}",
    ]


def _inspect_container(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    result = serial.parent._call(  # noqa: SLF001
        runner,
        serial.parent.docker_argv(
            serial.parent.DockerOperation.ID_INSPECT,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=serial.parent.DockerOperation.ID_INSPECT,
        stdin=None,
        timeout=profile["command_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    return serial.parent._one_json(result, "restart_container_inspect")  # noqa: SLF001


def _assert_owned_container(
    inspect: dict[str, Any],
    *,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
    running: bool,
) -> str:
    if not serial._behavior_container_owned(  # noqa: SLF001
        inspect,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
    ):
        raise RestartFailure("container", "ownership_or_containment")
    state = inspect.get("State")
    network = inspect.get("NetworkSettings")
    if not isinstance(state, dict) or state.get("Running") is not running:
        raise RestartFailure("container", "state")
    if state.get("OOMKilled") is not False:
        raise RestartFailure("container", "oom_state")
    if inspect.get("RestartCount") not in (None, 0):
        raise RestartFailure("container", "automatic_restart")
    if not isinstance(network, dict) or network.get("Ports") not in ({}, None):
        raise RestartFailure("container", "published_port")
    networks = network.get("Networks")
    if not isinstance(networks, dict) or set(networks) not in (set(), {"none"}):
        raise RestartFailure("container", "network_join")
    if "none" in networks:
        none_network = networks["none"]
        if not isinstance(none_network, dict) or any(
            none_network.get(key) not in (None, "")
            for key in ("IPAddress", "GlobalIPv6Address", "Gateway", "MacAddress")
        ):
            raise RestartFailure("container", "network_endpoint")
    tmpfs_path = profile["tmpfs"].split(":", 1)[0]
    if profile["pgdata"] == tmpfs_path or profile["pgdata"].startswith(
        tmpfs_path + "/"
    ):
        raise RestartFailure("container", "pgdata_not_durable_across_restart")
    for mount in inspect.get("Mounts", []):
        destination = mount.get("Destination") if isinstance(mount, dict) else None
        if destination == profile["pgdata"] or (
            isinstance(destination, str)
            and profile["pgdata"].startswith(destination.rstrip("/") + "/")
        ):
            raise RestartFailure("container", "pgdata_mounted")
    return "running" if running else "stopped_after_sigkill"


def _facts(serial_contract: dict[str, Any]) -> dict[str, Any]:
    facts = copy.deepcopy(serial_contract["fixture_namespace"])
    facts.update(
        {
            "observer_r01": "50000000-0000-4000-8000-000000000101",
            "observer_r02": "50000000-0000-4000-8000-000000000102",
            "observer_r03": "50000000-0000-4000-8000-000000000103",
            "observer_r04": "50000000-0000-4000-8000-000000000104",
        }
    )
    for key in ("observer_r01", "observer_r02", "observer_r03", "observer_r04"):
        if not serial.UUID.fullmatch(facts[key]):
            raise RestartFailure("fixture", "observer_uuid", key)
    return facts


def _application_name(scenario_id: str, participant: str) -> str:
    if scenario_id not in SCENARIO_ORDER or participant not in {"c", "r", "u"}:
        raise RestartFailure("render", "participant_coordinate")
    label = f"emr4_cf_d2_{scenario_id[-3:].lower()}_{participant}"
    if not APPLICATION_LABEL.fullmatch(label):
        raise RestartFailure("render", "application_name")
    return label


def _participant_script(
    contract: dict[str, Any],
    *,
    scenario_id: str,
    participant: str,
    principal: str,
    isolation: str,
    statements: list[str],
    hold: str | None = None,
    injected_rollback: bool = False,
) -> bytes:
    if principal not in contract["fixture_authority"]["principals"]:
        raise RestartFailure("render", "principal")
    if isolation not in {"read committed", "serializable"}:
        raise RestartFailure("render", "isolation")
    if hold not in {None, "pre_commit", "post_commit"}:
        raise RestartFailure("render", "hold")
    durability = contract["durability_profile"]
    lines = [
        f"SET application_name TO {serial._lit(_application_name(scenario_id, participant))};",  # noqa: SLF001
        f"SET SESSION AUTHORIZATION {principal};",
        f"BEGIN ISOLATION LEVEL {isolation.upper()};",
        "SET LOCAL statement_timeout TO "
        f"{serial._lit(str(durability['statement_timeout_milliseconds']) + 'ms')};",  # noqa: SLF001
        "SET LOCAL idle_in_transaction_session_timeout TO "
        f"{serial._lit(str(durability['idle_in_transaction_timeout_milliseconds']) + 'ms')};",  # noqa: SLF001
        serial._identity_select(principal),  # noqa: SLF001
        *statements,
    ]
    if injected_rollback:
        lines.append(
            "DO $fixed_abort$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001', "
            "MESSAGE='fixed_injected_rollback'; END $fixed_abort$;"
        )
    if hold == "pre_commit":
        lines.extend(["SELECT pg_catalog.pg_sleep(5);", "COMMIT;"])
    elif hold == "post_commit":
        lines.extend(["COMMIT;", "SELECT pg_catalog.pg_sleep(5);"])
    else:
        lines.append("COMMIT;")
    rendered = "\n".join(lines) + "\n"
    if rendered.count("SET SESSION AUTHORIZATION") != 1:
        raise RestartFailure("render", "session_authorization_count")
    if rendered.count("BEGIN ISOLATION LEVEL") != 1 or rendered.count("COMMIT;") != 1:
        raise RestartFailure("render", "transaction_shape")
    if re.search(r"\b(SET ROLE|SAVEPOINT|PREPARE TRANSACTION)\b", rendered, re.I):
        raise RestartFailure("render", "forbidden_transaction_control")
    if hold is None and "pg_catalog.pg_sleep" in rendered:
        raise RestartFailure("render", "unexpected_hold")
    return rendered.encode("utf-8")


def _call_script(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    script: bytes,
) -> serial.parent.ProcessResult:
    argv = serial._scenario_argv(docker, container_id, profile)  # noqa: SLF001
    serial.assert_scenario_argv(argv)
    return runner(
        argv,
        script,
        profile["command_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )


def _result_lines(result: serial.parent.ProcessResult) -> list[str]:
    rows = [line.strip() for line in result.stdout.decode("utf-8").splitlines()]
    return [line for line in rows if line in RESULT_VOCABULARY]


def _closed_identity(
    result: serial.parent.ProcessResult, principal: str, isolation: str
) -> dict[str, Any]:
    identity = serial._identity_from_stdout(  # noqa: SLF001
        result,
        principal,
        expected_read_only=False,
        expected_isolation=isolation,
    )
    return {
        "session_user_matches_expected": identity["session_user"] == principal,
        "current_user_matches_expected": identity["current_user"] == principal,
        "isolation": identity["isolation"],
        "read_only": identity["read_only"],
    }


def _expect_success(
    result: serial.parent.ProcessResult,
    *,
    coordinate: str,
    principal: str,
    isolation: str,
    expected_lines: list[str],
) -> dict[str, Any]:
    if result.returncode != 0 or _result_lines(result) != expected_lines:
        raise TerminalFailure(coordinate, "unexpected_terminal_success", result)
    return {
        "outcome": "commit",
        "sqlstate": None,
        "result_lines": expected_lines,
        "identity": _closed_identity(result, principal, isolation),
    }


def _expect_failure(
    result: serial.parent.ProcessResult,
    *,
    coordinate: str,
    principal: str,
    isolation: str,
    sqlstate: str,
) -> dict[str, Any]:
    observed = serial._safe_sqlstate(result)  # noqa: SLF001
    if result.returncode == 0 or observed != sqlstate:
        raise TerminalFailure(coordinate, "unexpected_terminal_sqlstate", result)
    return {
        "outcome": "rollback",
        "sqlstate": sqlstate,
        "result_lines": _result_lines(result),
        "identity": _closed_identity(result, principal, isolation),
    }


def _execute(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    *,
    coordinate: str,
    scenario_id: str,
    principal: str,
    isolation: str,
    statements: list[str],
    expected_lines: list[str] | None = None,
    expected_sqlstate: str | None = None,
    injected_rollback: bool = False,
) -> dict[str, Any]:
    recovery_contract = _validate_recovery_contract()
    _assert_terminal_coordinate(coordinate, recovery_contract)
    result = _call_script(
        runner,
        docker,
        container_id,
        profile,
        _participant_script(
            contract,
            scenario_id=scenario_id,
            participant="r",
            principal=principal,
            isolation=isolation,
            statements=statements,
            injected_rollback=injected_rollback,
        ),
    )
    if expected_sqlstate is not None:
        return _expect_failure(
            result,
            coordinate=coordinate,
            principal=principal,
            isolation=isolation,
            sqlstate=expected_sqlstate,
        )
    if expected_lines is None:
        raise RestartFailure("scenario", "expected_result_missing")
    return _expect_success(
        result,
        coordinate=coordinate,
        principal=principal,
        isolation=isolation,
        expected_lines=expected_lines,
    )


def _activity_state(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    if not APPLICATION_LABEL.fullmatch(label):
        raise RestartFailure("observation", "application_name")
    sql = (
        "SELECT pg_catalog.json_build_object("
        "'count',pg_catalog.count(*),"
        "'wait_event_type',COALESCE(pg_catalog.min(wait_event_type),''),"
        "'wait_event',COALESCE(pg_catalog.min(wait_event),''))::pg_catalog.text "
        "FROM pg_catalog.pg_stat_activity WHERE datname=pg_catalog.current_database() "
        f"AND application_name={serial._lit(label)}"  # noqa: SLF001
    )
    value = serial._query_json_bounded(  # noqa: SLF001
        runner,
        docker,
        container_id,
        profile["postgres_database"],
        profile,
        sql,
        query_id="restart_activity",
    )
    if (
        not isinstance(value, dict)
        or set(value) != {"count", "wait_event_type", "wait_event"}
        or type(value["count"]) is not int
        or value["count"] not in {0, 1}
        or not isinstance(value["wait_event_type"], str)
        or not isinstance(value["wait_event"], str)
    ):
        raise RestartFailure("observation", "activity_shape")
    return value


def _wait_for_sleep(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    label: str,
    future: Future[serial.parent.ProcessResult],
) -> int:
    started = time.monotonic()
    while time.monotonic() - started <= 3:
        if future.done():
            raise RestartFailure("observation", "client_ended_before_cutpoint")
        state = _activity_state(runner, docker, container_id, profile, label)
        if (
            state["count"] == 1
            and state["wait_event_type"] == "Timeout"
            and state["wait_event"] == "PgSleep"
        ):
            return int((time.monotonic() - started) * 1000)
        time.sleep(0.025)
    raise RestartFailure("observation", "pg_sleep_not_observed")


def _coordinate_where(facts: dict[str, Any], observer: str) -> str:
    return " AND ".join(
        (
            f"practice_id={serial._lit(facts['practice_alpha'])}::pg_catalog.uuid",  # noqa: SLF001
            "source_contract_id="
            f"{serial._lit(facts['source_contract_id'])}::emr4_context_fabric.source_contract_code",  # noqa: SLF001
            f"stream_id={serial._lit(facts['stream_alpha'])}::pg_catalog.uuid",  # noqa: SLF001
            f"stream_epoch={facts['stream_epoch']}::pg_catalog.int8",
            f"observer_id={serial._lit(facts[observer])}::pg_catalog.uuid",  # noqa: SLF001
            "observer_generation=1::pg_catalog.int8",
        )
    )


def _member_sql(label: str, relation: str, where: str) -> str:
    if label not in PACKET_RELATIONS or not re.fullmatch(
        r"emr4_context_fabric\.[a-z][a-z0-9_]{0,62}", relation
    ):
        raise RestartFailure("render", "packet_relation")
    return (
        serial._lit(label)  # noqa: SLF001
        + ",(SELECT pg_catalog.json_build_object("
        "'count',pg_catalog.count(*),"
        "'digest','sha256:'||pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to("
        "COALESCE(pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY "
        "pg_catalog.to_jsonb(t)::pg_catalog.text)::pg_catalog.text,'[]'),'UTF8')),'hex')) "
        f"FROM {relation} AS t WHERE {where})"
    )


def _recovery_packet_sql(facts: dict[str, Any], observer: str, position: int) -> str:
    if observer not in {"observer_r01", "observer_r02", "observer_r03", "observer_r04"}:
        raise RestartFailure("render", "observer")
    if position not in {1, 2}:
        raise RestartFailure("render", "position")
    coordinate = _coordinate_where(facts, observer)
    positioned = coordinate + f" AND source_position={position}::pg_catalog.int8"
    relations = {
        "admission": (
            "emr4_context_fabric.context_proofread_observation_admission",
            positioned,
        ),
        "receipt": (
            "emr4_context_fabric.context_classified_observation_receipt",
            positioned,
        ),
        "checkpoint": (
            "emr4_context_fabric.context_durability_checkpoint",
            coordinate,
        ),
        "lifecycle": (
            "emr4_context_fabric.context_durability_lifecycle",
            coordinate,
        ),
        "audit": ("emr4_context_fabric.context_durability_audit", coordinate),
        "watermark": (
            "emr4_context_fabric.context_invalidation_watermark",
            coordinate,
        ),
        "frame": ("emr4_context_fabric.context_frame_generation", coordinate),
        "obligation": (
            "emr4_context_fabric.context_reassembly_obligation",
            coordinate,
        ),
        "anchor": ("emr4_context_fabric.context_recovery_anchor", coordinate),
    }
    return (
        "SELECT pg_catalog.json_build_object("
        + ",".join(_member_sql(label, *relations[label]) for label in PACKET_RELATIONS)
        + ")::pg_catalog.text"
    )


def _validate_packet(packet: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(packet, dict) or set(packet) != set(PACKET_RELATIONS):
        raise RestartFailure("recovery", "packet_population")
    for label, member in packet.items():
        if (
            not isinstance(member, dict)
            or set(member) != {"count", "digest"}
            or type(member["count"]) is not int
            or member["count"] < 0
            or not DIGEST.fullmatch(str(member["digest"]))
        ):
            raise RestartFailure("recovery", "packet_shape", label)
    return packet


def _recovery_packet(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    facts: dict[str, Any],
    observer: str,
    position: int,
) -> dict[str, dict[str, Any]]:
    value = serial._query_json_bounded(  # noqa: SLF001
        runner,
        docker,
        container_id,
        profile["postgres_database"],
        profile,
        _recovery_packet_sql(facts, observer, position),
        query_id="recovery_packet",
    )
    return _validate_packet(value)


def _assert_transition_delta(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> None:
    _validate_packet(before)
    _validate_packet(after)
    if before["receipt"]["count"] != 0 or after["receipt"]["count"] != 1:
        raise RestartFailure("recovery", "receipt_population")
    for label in TRANSITION_INSERTS:
        if after[label]["count"] - before[label]["count"] != 1:
            raise RestartFailure("recovery", "atomic_insert_delta", label)
        if after[label]["digest"] == before[label]["digest"]:
            raise RestartFailure("recovery", "atomic_insert_digest", label)
    for label in TRANSITION_UPDATES:
        if after[label]["count"] != before[label]["count"]:
            raise RestartFailure("recovery", "atomic_update_count", label)
        if after[label]["digest"] == before[label]["digest"]:
            raise RestartFailure("recovery", "atomic_update_digest", label)
    for label in TRANSITION_UNCHANGED:
        if after[label] != before[label]:
            raise RestartFailure("recovery", "atomic_unchanged_member", label)


def classify_recovery(
    expected_pretransition: dict[str, dict[str, Any]],
    postrestart: dict[str, dict[str, Any]],
) -> str:
    """Classify only complete canonical durable packets; never use schedule hints."""

    before = _validate_packet(expected_pretransition)
    after = _validate_packet(postrestart)
    if after == before:
        return "ROLLED_BACK_RECOVERED"
    try:
        _assert_transition_delta(before, after)
    except RestartFailure as error:
        raise RestartFailure("recovery", "recovery_unresolved") from error
    return "COMMITTED_RECOVERED"


def _assert_anchor_delta(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> None:
    _validate_packet(before)
    _validate_packet(after)
    for label in PACKET_RELATIONS:
        if label == "anchor":
            if after[label]["count"] - before[label]["count"] != 1:
                raise RestartFailure("readback", "anchor_count")
            if after[label]["digest"] == before[label]["digest"]:
                raise RestartFailure("readback", "anchor_digest")
        elif after[label] != before[label]:
            raise RestartFailure("readback", "anchor_side_effect", label)


def _assert_next_transition_delta(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> None:
    _validate_packet(before)
    _validate_packet(after)
    for label in ("receipt", "lifecycle", "audit"):
        if after[label]["count"] - before[label]["count"] != 1:
            raise RestartFailure("readback", "next_insert_delta", label)
        if after[label]["digest"] == before[label]["digest"]:
            raise RestartFailure("readback", "next_insert_digest", label)
    for label in ("checkpoint", "watermark", "obligation"):
        if after[label]["count"] != before[label]["count"]:
            raise RestartFailure("readback", "next_update_count", label)
        if after[label]["digest"] == before[label]["digest"]:
            raise RestartFailure("readback", "next_update_digest", label)
    for label in ("admission", "anchor", "frame"):
        if after[label] != before[label]:
            raise RestartFailure("readback", "next_unchanged_member", label)


def _durability_facts(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    sql = (
        "SELECT pg_catalog.json_build_object("
        "'postgresql_major',(pg_catalog.current_setting('server_version_num')::pg_catalog.int4 / 10000),"
        "'fsync',pg_catalog.current_setting('fsync'),"
        "'synchronous_commit',pg_catalog.current_setting('synchronous_commit'),"
        "'full_page_writes',pg_catalog.current_setting('full_page_writes'),"
        "'data_checksums',pg_catalog.current_setting('data_checksums'),"
        "'cluster_identity_digest','sha256:'||pg_catalog.encode(pg_catalog.sha256("
        "pg_catalog.convert_to((SELECT system_identifier::pg_catalog.text "
        "FROM pg_catalog.pg_control_system()),'UTF8')),'hex'))::pg_catalog.text"
    )
    value = serial._query_json_bounded(  # noqa: SLF001
        runner,
        docker,
        container_id,
        profile["postgres_database"],
        profile,
        sql,
        query_id="durability_profile",
    )
    expected = {
        "postgresql_major": 16,
        "fsync": "on",
        "synchronous_commit": "on",
        "full_page_writes": "on",
        "data_checksums": "on",
    }
    if not isinstance(value, dict) or set(value) != set(expected) | {
        "cluster_identity_digest"
    }:
        raise RestartFailure("durability", "profile_shape")
    if any(value[key] != expected[key] for key in expected):
        raise RestartFailure("durability", "setting")
    if not DIGEST.fullmatch(str(value["cluster_identity_digest"])):
        raise RestartFailure("durability", "cluster_identity")
    return value


def _restart_same_cluster(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
    baseline_durability: dict[str, Any],
    fixture_catalogue_digests: dict[str, str],
) -> dict[str, Any]:
    before = _inspect_container(runner, docker, container_id, profile)
    _assert_owned_container(
        before,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
        running=True,
    )
    killed = runner(
        _kill_argv(docker, container_id),
        None,
        profile["command_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )
    if killed.returncode != 0 or killed.stdout.decode(
        "ascii", errors="ignore"
    ).strip() not in {
        container_id,
        container_id[:12],
    }:
        raise RestartFailure("restart", "sigkill_failed")
    stopped = _inspect_container(runner, docker, container_id, profile)
    stopped_state = _assert_owned_container(
        stopped,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
        running=False,
    )
    started_at = time.monotonic()
    started = runner(
        _start_argv(docker, container_id),
        None,
        profile["command_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )
    if started.returncode != 0 or started.stdout.decode(
        "ascii", errors="ignore"
    ).strip() not in {
        container_id,
        container_id[:12],
    }:
        raise RestartFailure("restart", "container_start_failed")
    running = _inspect_container(runner, docker, container_id, profile)
    running_state = _assert_owned_container(
        running,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
        running=True,
    )
    postgres = runner(
        _postgres_start_argv(docker, container_id, profile),
        None,
        profile["startup_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )
    if postgres.returncode != 0:
        raise RestartFailure("restart", "postgres_recovery_start_failed")
    observation: dict[str, Any] = {}
    serial.parent._wait_for_stable_postgres(  # noqa: SLF001
        runner,
        docker,
        container_id,
        profile,
        observation=observation,
    )
    ready_ms = int((time.monotonic() - started_at) * 1000)
    if ready_ms > 15000:
        raise RestartFailure("restart", "startup_ceiling")
    durability = _durability_facts(runner, docker, container_id, profile)
    if durability != baseline_durability:
        raise RestartFailure("restart", "cluster_or_setting_drift")
    catalogue = serial.parent._read_catalogue(  # noqa: SLF001
        runner,
        docker,
        container_id,
        profile["postgres_database"],
        profile,
    )
    serial._assert_post_behavior_catalogue_stability(  # noqa: SLF001
        fixture_catalogue_digests, catalogue
    )
    return {
        "crash_method": "docker_kill_sigkill_exact_captured_container",
        "stopped_state": stopped_state,
        "started_state": running_state,
        "same_container": True,
        "same_cluster": True,
        "startup_ms": ready_ms,
        "durability": durability,
    }


def _register_statements(facts: dict[str, Any], observer: str) -> list[str]:
    return concurrency._register_statements(facts, observer)  # noqa: SLF001


def _producer_statements(facts: dict[str, Any], *, second: bool) -> list[str]:
    return concurrency._producer_statements(facts, second=second)  # noqa: SLF001


def _admission_statements(
    facts: dict[str, Any], observer: str, position: int
) -> list[str]:
    return concurrency._admission_statements(  # noqa: SLF001
        facts, observer, position, conflict=False
    )


def _coordinator_statements(
    facts: dict[str, Any], observer: str, position: int
) -> list[str]:
    return concurrency._coordinator_statements(facts, observer, position)  # noqa: SLF001


def _anchor_statements(
    facts: dict[str, Any], observer: str, revision: int
) -> list[str]:
    if revision != 1:
        raise RestartFailure("render", "anchor_revision")
    return [
        "SELECT (emr4_context_fabric.append_recovery_anchor_v1("
        + serial._locator(facts, observer)  # noqa: SLF001
        + f",{revision}::pg_catalog.int8)).lifecycle_revision::pg_catalog.text;"
    ]


def _setup_fixtures(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    facts: dict[str, Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for observer in ("observer_r01", "observer_r02", "observer_r03", "observer_r04"):
        records.append(
            {
                "name": f"register_{observer}",
                "outcome": _execute(
                    runner,
                    docker,
                    container_id,
                    profile,
                    contract,
                    coordinate=f"fixture_register_{observer}",
                    scenario_id="CFD2-R01",
                    principal="context_lifecycle",
                    isolation="serializable",
                    statements=_register_statements(facts, observer),
                    expected_lines=[],
                ),
            }
        )
    for second, expected in ((False, ["1"]), (True, ["2"])):
        records.append(
            {
                "name": "produce_position_two" if second else "produce_position_one",
                "outcome": _execute(
                    runner,
                    docker,
                    container_id,
                    profile,
                    contract,
                    coordinate=f"fixture_produce_position_{2 if second else 1}",
                    scenario_id="CFD2-R01",
                    principal="context_producer",
                    isolation="read committed",
                    statements=_producer_statements(facts, second=second),
                    expected_lines=expected,
                ),
            }
        )
    for observer in ("observer_r01", "observer_r02", "observer_r03", "observer_r04"):
        records.append(
            {
                "name": f"admit_{observer}_position_1",
                "outcome": _execute(
                    runner,
                    docker,
                    container_id,
                    profile,
                    contract,
                    coordinate=f"fixture_admit_{observer}_position_1",
                    scenario_id="CFD2-R01",
                    principal="context_observer",
                    isolation="read committed",
                    statements=_admission_statements(facts, observer, 1),
                    expected_lines=["PRIMARY"],
                ),
            }
        )
    if len(records) != 10:
        raise RestartFailure("fixture", "precondition_count")
    return records


def _snapshot(
    runner: Runner, docker: str, container_id: str, profile: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    return serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001


def _unknown_client(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    facts: dict[str, Any],
    observer: str,
    scenario_id: str,
    hold: str,
    baseline_durability: dict[str, Any],
    fixture_catalogue_digests: dict[str, str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    label = _application_name(scenario_id, "u")
    script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="u",
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, observer, 1),
        hold=hold,
    )
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            _call_script, runner, docker, container_id, profile, script
        )
        observed_ms = _wait_for_sleep(
            runner, docker, container_id, profile, label, future
        )
        pre_crash_snapshot = _snapshot(runner, docker, container_id, profile)
        state = _activity_state(runner, docker, container_id, profile, label)
        if state != {"count": 1, "wait_event_type": "Timeout", "wait_event": "PgSleep"}:
            raise RestartFailure("observation", "cutpoint_not_stable")
        restart = _restart_same_cluster(
            runner,
            docker,
            container_id,
            name,
            nonce,
            image_id,
            profile,
            baseline_durability,
            fixture_catalogue_digests,
        )
        try:
            client = future.result(timeout=5)
        except FutureTimeoutError as error:
            raise RestartFailure("observation", "client_did_not_terminate") from error
    if client.returncode == 0:
        raise RestartFailure("observation", "normal_terminal_result_after_sigkill")
    observation = {
        "client_observation": "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT",
        "wait_event_type": "Timeout",
        "wait_event": "PgSleep",
        "cutpoint_observed_ms": observed_ms,
        "normal_process_exit": False,
        "partial_output_parsed_or_retained": False,
    }
    return observation, pre_crash_snapshot, restart


def _scenario_spec(contract: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    matches = [row for row in contract["scenarios"] if row["id"] == scenario_id]
    if len(matches) != 1:
        raise RestartFailure("contract", "scenario_lookup")
    return matches[0]


def _record(
    contract: dict[str, Any],
    scenario_id: str,
    *,
    client_observation: str,
    cutpoint: str,
    recovery_classification: str,
    pre_transition_packet: dict[str, dict[str, Any]],
    post_restart_packet: dict[str, dict[str, Any]],
    pre_crash_snapshot: dict[str, dict[str, Any]],
    post_restart_snapshot: dict[str, dict[str, Any]],
    restart: dict[str, Any],
    actions: list[dict[str, Any]],
) -> dict[str, Any]:
    spec = _scenario_spec(contract, scenario_id)
    return {
        "scenario_id": scenario_id,
        "category": spec["category"],
        "client_observation": client_observation,
        "cutpoint": cutpoint,
        "recovery_classification": recovery_classification,
        "pre_transition_packet": pre_transition_packet,
        "post_restart_packet": post_restart_packet,
        "pre_crash_snapshot": pre_crash_snapshot,
        "post_restart_snapshot": post_restart_snapshot,
        "restart_exact_match": pre_crash_snapshot == post_restart_snapshot,
        "restart": restart,
        "actions": actions,
        "readback_checks": {name: True for name in spec["readback"]},
        "forbidden_effects_absent": {name: True for name in spec["forbidden_effects"]},
        "passed": True,
    }


def _diagnostic_terminal_observation(
    coordinate: str, outcome: dict[str, Any]
) -> dict[str, Any]:
    return {
        "coordinate": coordinate,
        "code": "matched_expected_terminal",
        "returncode_class": "zero",
        "sqlstate": outcome["sqlstate"],
        "result_lines": outcome["result_lines"],
        "passed": True,
    }


def _run_no_crash_first_sequence(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    facts: dict[str, Any],
) -> list[dict[str, Any]]:
    observer = "observer_r01"
    pre_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    apply_coordinate = "cfd2_r01_apply_position_1"
    applied_outcome = _execute(
        runner,
        docker,
        container_id,
        profile,
        contract,
        coordinate=apply_coordinate,
        scenario_id="CFD2-R01",
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, observer, 1),
        expected_lines=["RECEIPT_APPLIED"],
    )
    applied = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_transition_delta(pre_packet, applied)

    anchor_coordinate = "cfd2_r01_append_anchor_2"
    anchor_outcome = _execute(
        runner,
        docker,
        container_id,
        profile,
        contract,
        coordinate=anchor_coordinate,
        scenario_id="CFD2-R01",
        principal="context_lifecycle",
        isolation="serializable",
        statements=_anchor_statements(facts, observer, 1),
        expected_lines=["1"],
    )
    anchored = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_anchor_delta(applied, anchored)
    return [
        _diagnostic_terminal_observation(apply_coordinate, applied_outcome),
        _diagnostic_terminal_observation(anchor_coordinate, anchor_outcome),
    ]


def _run_scenarios(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    facts: dict[str, Any],
    baseline_durability: dict[str, Any],
    fixture_catalogue_digests: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    restarts: list[dict[str, Any]] = []

    # R01: confirmed commit and its independent anchor survive restart.
    scenario_id = "CFD2-R01"
    observer = "observer_r01"
    pre_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    actions = [
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r01_apply_position_1",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_APPLIED"],
        )
    ]
    applied = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_transition_delta(pre_packet, applied)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r01_append_anchor_2",
            scenario_id=scenario_id,
            principal="context_lifecycle",
            isolation="serializable",
            statements=_anchor_statements(facts, observer, 1),
            expected_lines=["1"],
        )
    )
    anchored = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_anchor_delta(applied, anchored)
    pre_crash = _snapshot(runner, docker, container_id, profile)
    restart = _restart_same_cluster(
        runner,
        docker,
        container_id,
        name,
        nonce,
        image_id,
        profile,
        baseline_durability,
        fixture_catalogue_digests,
    )
    restarts.append(restart)
    post_restart = _snapshot(runner, docker, container_id, profile)
    post_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    if post_restart != pre_crash or post_packet != anchored:
        raise RestartFailure("readback", "confirmed_commit_restart_drift")
    before_replay = _snapshot(runner, docker, container_id, profile)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r01_replay_position_1",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_REPLAYED"],
        )
    )
    if _snapshot(runner, docker, container_id, profile) != before_replay:
        raise RestartFailure("readback", "confirmed_replay_not_inert")
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r01_admit_position_2",
            scenario_id=scenario_id,
            principal="context_observer",
            isolation="read committed",
            statements=_admission_statements(facts, observer, 2),
            expected_lines=["PRIMARY"],
        )
    )
    position_two_before = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 2
    )
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r01_apply_position_2",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 2),
            expected_lines=["RECEIPT_APPLIED"],
        )
    )
    position_two_after = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 2
    )
    _assert_next_transition_delta(position_two_before, position_two_after)
    records.append(
        _record(
            contract,
            scenario_id,
            client_observation="COMMIT_ACKNOWLEDGED",
            cutpoint="after_confirmed_anchor_commit",
            recovery_classification="COMMITTED_CONFIRMED",
            pre_transition_packet=pre_packet,
            post_restart_packet=post_packet,
            pre_crash_snapshot=pre_crash,
            post_restart_snapshot=post_restart,
            restart=restart,
            actions=actions,
        )
    )

    # R02: an acknowledged outer rollback leaves exact zero residue.
    scenario_id = "CFD2-R02"
    observer = "observer_r02"
    pre_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    pre_transition = _snapshot(runner, docker, container_id, profile)
    actions = [
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r02_rollback_position_1",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_sqlstate="P0001",
            injected_rollback=True,
        )
    ]
    pre_crash = _snapshot(runner, docker, container_id, profile)
    if pre_crash != pre_transition:
        raise RestartFailure("readback", "confirmed_rollback_residue")
    restart = _restart_same_cluster(
        runner,
        docker,
        container_id,
        name,
        nonce,
        image_id,
        profile,
        baseline_durability,
        fixture_catalogue_digests,
    )
    restarts.append(restart)
    post_restart = _snapshot(runner, docker, container_id, profile)
    post_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    if post_restart != pre_transition or post_packet != pre_packet:
        raise RestartFailure("readback", "confirmed_rollback_restart_residue")
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r02_apply_position_1_after_rollback",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_APPLIED"],
        )
    )
    applied = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_transition_delta(pre_packet, applied)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r02_append_anchor_2",
            scenario_id=scenario_id,
            principal="context_lifecycle",
            isolation="serializable",
            statements=_anchor_statements(facts, observer, 1),
            expected_lines=["1"],
        )
    )
    anchored = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_anchor_delta(applied, anchored)
    before_replay = _snapshot(runner, docker, container_id, profile)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r02_replay_position_1",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_REPLAYED"],
        )
    )
    if _snapshot(runner, docker, container_id, profile) != before_replay:
        raise RestartFailure("readback", "rollback_replay_not_inert")
    records.append(
        _record(
            contract,
            scenario_id,
            client_observation="ROLLBACK_SQLSTATE_P0001_ACKNOWLEDGED",
            cutpoint="after_confirmed_rollback",
            recovery_classification="ROLLED_BACK_CONFIRMED",
            pre_transition_packet=pre_packet,
            post_restart_packet=post_packet,
            pre_crash_snapshot=pre_crash,
            post_restart_snapshot=post_restart,
            restart=restart,
            actions=actions,
        )
    )

    # R03: no client terminal result; complete state proves commit.
    scenario_id = "CFD2-R03"
    observer = "observer_r03"
    pre_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    observation, pre_crash, restart = _unknown_client(
        runner,
        docker,
        container_id,
        name,
        nonce,
        image_id,
        profile,
        contract,
        facts,
        observer,
        scenario_id,
        "post_commit",
        baseline_durability,
        fixture_catalogue_digests,
    )
    restarts.append(restart)
    post_restart = _snapshot(runner, docker, container_id, profile)
    if post_restart != pre_crash:
        raise RestartFailure("readback", "unknown_commit_restart_drift")
    post_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    classification = classify_recovery(pre_packet, post_packet)
    if classification != "COMMITTED_RECOVERED":
        raise RestartFailure("recovery", "unexpected_committed_classification")
    actions = [{"outcome": "indeterminate", **observation}]
    before_replay = _snapshot(runner, docker, container_id, profile)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r03_replay_position_1",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_REPLAYED"],
        )
    )
    if _snapshot(runner, docker, container_id, profile) != before_replay:
        raise RestartFailure("readback", "recovered_replay_not_inert")
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r03_admit_position_2",
            scenario_id=scenario_id,
            principal="context_observer",
            isolation="read committed",
            statements=_admission_statements(facts, observer, 2),
            expected_lines=["PRIMARY"],
        )
    )
    position_two_before = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 2
    )
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r03_reject_position_2_before_anchor",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 2),
            expected_sqlstate="CF303",
        )
    )
    if (
        _recovery_packet(runner, docker, container_id, profile, facts, observer, 2)
        != position_two_before
    ):
        raise RestartFailure("readback", "cf303_not_inert")
    anchor_before = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r03_append_anchor_2",
            scenario_id=scenario_id,
            principal="context_lifecycle",
            isolation="serializable",
            statements=_anchor_statements(facts, observer, 1),
            expected_lines=["1"],
        )
    )
    anchor_after = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_anchor_delta(anchor_before, anchor_after)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r03_apply_position_2",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 2),
            expected_lines=["RECEIPT_APPLIED"],
        )
    )
    _assert_next_transition_delta(
        position_two_before,
        _recovery_packet(runner, docker, container_id, profile, facts, observer, 2),
    )
    records.append(
        _record(
            contract,
            scenario_id,
            client_observation=observation["client_observation"],
            cutpoint="observed_post_commit_pg_sleep_then_sigkill",
            recovery_classification=classification,
            pre_transition_packet=pre_packet,
            post_restart_packet=post_packet,
            pre_crash_snapshot=pre_crash,
            post_restart_snapshot=post_restart,
            restart=restart,
            actions=actions,
        )
    )

    # R04: no client terminal result; exact prior state proves rollback.
    scenario_id = "CFD2-R04"
    observer = "observer_r04"
    pre_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    pre_transition = _snapshot(runner, docker, container_id, profile)
    observation, pre_crash, restart = _unknown_client(
        runner,
        docker,
        container_id,
        name,
        nonce,
        image_id,
        profile,
        contract,
        facts,
        observer,
        scenario_id,
        "pre_commit",
        baseline_durability,
        fixture_catalogue_digests,
    )
    restarts.append(restart)
    if pre_crash != pre_transition:
        raise RestartFailure("readback", "unknown_rollback_visible_uncommitted_state")
    post_restart = _snapshot(runner, docker, container_id, profile)
    if post_restart != pre_transition or post_restart != pre_crash:
        raise RestartFailure("readback", "unknown_rollback_restart_residue")
    post_packet = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    classification = classify_recovery(pre_packet, post_packet)
    if classification != "ROLLED_BACK_RECOVERED":
        raise RestartFailure("recovery", "unexpected_rollback_classification")
    actions = [{"outcome": "indeterminate", **observation}]
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r04_apply_position_1_after_recovery",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_APPLIED"],
        )
    )
    applied = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_transition_delta(pre_packet, applied)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r04_append_anchor_2",
            scenario_id=scenario_id,
            principal="context_lifecycle",
            isolation="serializable",
            statements=_anchor_statements(facts, observer, 1),
            expected_lines=["1"],
        )
    )
    anchored = _recovery_packet(
        runner, docker, container_id, profile, facts, observer, 1
    )
    _assert_anchor_delta(applied, anchored)
    before_replay = _snapshot(runner, docker, container_id, profile)
    actions.append(
        _execute(
            runner,
            docker,
            container_id,
            profile,
            contract,
            coordinate="cfd2_r04_replay_position_1",
            scenario_id=scenario_id,
            principal="context_coordinator",
            isolation="serializable",
            statements=_coordinator_statements(facts, observer, 1),
            expected_lines=["RECEIPT_REPLAYED"],
        )
    )
    if _snapshot(runner, docker, container_id, profile) != before_replay:
        raise RestartFailure("readback", "recovered_rollback_replay_not_inert")
    records.append(
        _record(
            contract,
            scenario_id,
            client_observation=observation["client_observation"],
            cutpoint="observed_pre_commit_pg_sleep_then_sigkill",
            recovery_classification=classification,
            pre_transition_packet=pre_packet,
            post_restart_packet=post_packet,
            pre_crash_snapshot=pre_crash,
            post_restart_snapshot=post_restart,
            restart=restart,
            actions=actions,
        )
    )

    if tuple(row["scenario_id"] for row in records) != SCENARIO_ORDER:
        raise RestartFailure("scenario", "terminal_order")
    if len(restarts) != 4:
        raise RestartFailure("restart", "crash_count")
    return records, restarts


def _bounded_failure(error: serial.parent.RehearsalFailure) -> dict[str, str]:
    stage = error.stage if IDENTIFIER.fullmatch(error.stage) else "bounded_failure"
    code = error.code if IDENTIFIER.fullmatch(error.code) else "bounded_failure"
    return {"stage": stage, "code": code}


def _cleanup_evidence(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": value.get("status", "cleanup_failed"),
        "removed": value.get("removed") is True,
        "absence_verified": value.get("absence_verified") is True,
    }


def _cleanup(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    cleanup = serial._cleanup(  # noqa: SLF001
        runner,
        docker,
        container_id,
        name,
        nonce,
        image_id,
        profile,
    )
    if not cleanup.get("absence_verified"):
        return cleanup
    scoped_absence = runner(
        _label_absence_argv(docker, profile, nonce),
        None,
        profile["cleanup_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )
    if scoped_absence.returncode != 0 or scoped_absence.stdout.strip():
        raise RestartFailure("cleanup", "scoped_label_absence_failed")
    return cleanup


def run_rehearsal(
    *,
    runner: Runner = serial.parent._subprocess_runner,  # noqa: SLF001
    diagnostic_mode: bool = False,
) -> dict[str, Any]:
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
    preconditions: list[dict[str, Any]] = []
    scenarios: list[dict[str, Any]] = []
    restarts: list[dict[str, Any]] = []
    diagnostic_observations: list[dict[str, Any]] = []
    result = "rehearsal_failed"
    failure: serial.parent.RehearsalFailure | None = None
    container_id = image_id = name = nonce = docker = ""
    profile: dict[str, Any] = {}
    cleanup_runner = runner
    try:
        contract, serial_contract, prerequisite, manifest, artifact = (
            _validate_contract()
        )
        recovery_contract = _validate_recovery_contract()
        source_head = _source_head()
        profile = _profile()
        cleanup_reserve = 3 * profile["cleanup_timeout_seconds"]
        runner = serial.parent._with_total_deadline(  # noqa: SLF001
            runner, started + profile["total_timeout_seconds"] - cleanup_reserve
        )
        parent_evidence = {
            "source_head": source_head,
            "contract_sha256": _canonical_sha(contract),
            "artifact_sha256": "sha256:" + hashlib.sha256(artifact).hexdigest(),
            "manifest_sha256": _file_digest(
                ROOT
                / "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json"
            ),
            "statement_count": manifest["statement_count"],
        }
        if diagnostic_mode:
            parent_evidence["recovery_contract_sha256"] = _canonical_sha(
                recovery_contract
            )
        lifecycle.append("eight_parent_bindings_verified")
        docker = shutil.which(profile["executable"]) or ""
        if not docker or Path(docker).name.lower() != "docker.exe":
            raise RestartFailure("environment", "docker_client_missing")
        environment["docker_client"] = "resolved_exact_docker_exe"
        image_result = serial.parent._call(  # noqa: SLF001
            runner,
            serial.parent.docker_argv(
                serial.parent.DockerOperation.IMAGE_INSPECT,
                docker=docker,
                profile=profile,
            ),
            operation=serial.parent.DockerOperation.IMAGE_INSPECT,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if image_result.returncode != 0:
            raise RestartFailure("environment", "exact_local_image_unavailable")
        image = serial.parent._one_json(image_result, "image_inspect")  # noqa: SLF001
        image_id = str(image.get("Id", ""))
        if not DIGEST.fullmatch(image_id):
            raise RestartFailure("environment", "image_id_invalid")
        environment["image"] = {
            "reference": profile["image_reference"],
            "identity_digest": image_id,
            "pull_attempted": False,
        }
        nonce = secrets.token_hex(16)
        name = profile["container_name_prefix"] + secrets.token_hex(8)
        absent = serial.parent._call(  # noqa: SLF001
            runner,
            serial.parent.docker_argv(
                serial.parent.DockerOperation.NAME_INSPECT,
                docker=docker,
                profile=profile,
                name=name,
            ),
            operation=serial.parent.DockerOperation.NAME_INSPECT,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if not serial.parent._is_exact_absence(absent):  # noqa: SLF001
            raise RestartFailure("environment", "container_name_not_proven_absent")
        created = runner(
            _run_argv(docker, profile, name=name, nonce=nonce),
            None,
            profile["command_timeout_seconds"],
            profile["stdout_stderr_cap_bytes"],
        )
        if created.returncode != 0:
            raise RestartFailure("container", "create_failed")
        container_id = created.stdout.decode("ascii", errors="ignore").strip()
        if not re.fullmatch(r"[0-9a-f]{12,64}", container_id):
            raise RestartFailure("container", "created_id_invalid")
        owned = _inspect_container(runner, docker, container_id, profile)
        _assert_owned_container(
            owned,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
            running=True,
        )
        environment["container"] = {
            "identity_digest": "sha256:"
            + hashlib.sha256(container_id.encode("ascii")).hexdigest(),
            "network_mode": "none",
            "published_ports": 0,
            "bind_mounts": 0,
            "named_volumes": 0,
            "anonymous_volumes": 0,
            "declared_volume_shield": "tmpfs",
            "actual_pgdata_storage": "owned_container_writable_layer",
        }
        lifecycle.append("container_owned_and_storage_closed")
        for stage, argv, stdin in _init_argvs(docker, container_id, profile):
            initialized = runner(
                argv,
                stdin,
                profile["startup_timeout_seconds"],
                profile["stdout_stderr_cap_bytes"],
            )
            if initialized.returncode != 0:
                raise RestartFailure("postgres_init", stage)
        readiness_profile = copy.deepcopy(profile)
        readiness_profile["postgres_database"] = "postgres"
        readiness: dict[str, Any] = {}
        serial.parent._wait_for_stable_postgres(  # noqa: SLF001
            runner,
            docker,
            container_id,
            readiness_profile,
            observation=readiness,
        )
        create_database = serial.parent._call(  # noqa: SLF001
            runner,
            serial.parent.docker_argv(
                serial.parent.DockerOperation.PSQL_COMMAND,
                docker=docker,
                profile=readiness_profile,
                container_id=container_id,
                database="postgres",
                sql_command='CREATE DATABASE "emr4_synthetic_restart";',
            ),
            operation=serial.parent.DockerOperation.PSQL_COMMAND,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if create_database.returncode != 0:
            raise RestartFailure("postgres", "database_create_failed")
        prerequisite_sql = serial.parent.render_prerequisite_sql(prerequisite)
        serial.parent._install_prerequisites(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
            prerequisite_sql,
        )
        admitted = serial.parent._stream_artifact(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
            artifact,
        )
        if admitted.returncode != 0:
            raise RestartFailure("artifact", "postgresql_rejected")
        catalogue = serial.parent._read_catalogue(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
        )
        serial._assert_bound_parent_catalogue(  # noqa: SLF001
            catalogue,
            manifest,
            prerequisite,
            serial._json(serial.PARENT_REHEARSAL_CONTRACT_PATH),  # noqa: SLF001
            expected_database=profile["postgres_database"],
        )
        bootstrap = serial._scenario_call(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile,
            serial.render_bootstrap_sql(serial_contract),
        )
        if bootstrap.returncode != 0:
            raise RestartFailure("fixture", "bootstrap_failed")
        fixture_catalogue = serial.parent._read_catalogue(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
        )
        fixture_catalogue_digests = serial._assert_fixture_catalogue_delta(  # noqa: SLF001
            catalogue, fixture_catalogue
        )
        serial._assert_fixture_privileges(  # noqa: SLF001
            runner, docker, container_id, profile
        )
        baseline_durability = _durability_facts(runner, docker, container_id, profile)
        environment["durability"] = baseline_durability
        lifecycle.append("postgres16_artifact_and_durability_reconciled")
        facts = _facts(serial_contract)
        preconditions = _setup_fixtures(
            runner, docker, container_id, profile, contract, facts
        )
        lifecycle.append("four_disjoint_generations_prepared")
        if diagnostic_mode:
            diagnostic_observations = _run_no_crash_first_sequence(
                runner,
                docker,
                container_id,
                profile,
                contract,
                facts,
            )
        else:
            scenarios, restarts = _run_scenarios(
                runner,
                docker,
                container_id,
                name,
                nonce,
                image_id,
                profile,
                contract,
                facts,
                baseline_durability,
                fixture_catalogue_digests,
            )
        final_catalogue = serial.parent._read_catalogue(  # noqa: SLF001
            runner,
            docker,
            container_id,
            profile["postgres_database"],
            profile,
        )
        serial._assert_post_behavior_catalogue_stability(  # noqa: SLF001
            fixture_catalogue_digests, final_catalogue
        )
        if diagnostic_mode:
            lifecycle.extend(
                ["no_crash_r01_apply_anchor_matched", "catalogue_reconciled"]
            )
            result = DIAGNOSTIC_PASS_RESULT
        else:
            lifecycle.extend(
                ["four_sigkill_same_cluster_restarts_matched", "catalogue_reconciled"]
            )
            result = PASS_RESULT
    except (
        RestartFailure,
        serial.BehaviorFailure,
        serial.parent.RehearsalFailure,
    ) as error:
        failure = error
        if error.stage == "environment":
            result = "environment_unavailable"
    finally:
        if container_id:
            try:
                cleanup = _cleanup(
                    cleanup_runner,
                    docker,
                    container_id,
                    name,
                    nonce,
                    image_id,
                    profile,
                )
                if cleanup.get("absence_verified"):
                    lifecycle.append("cleanup_verified")
                else:
                    result = "cleanup_ownership_unverified"
            except serial.parent.RehearsalFailure as cleanup_error:
                cleanup = {
                    "status": "cleanup_failed",
                    "removed": False,
                    "absence_verified": False,
                }
                if failure is None:
                    failure = cleanup_error
                result = "rehearsal_failed"
        if result in {PASS_RESULT, DIAGNOSTIC_PASS_RESULT} and cleanup.get(
            "absence_verified"
        ):
            lifecycle.append("passed")
        elif result in {PASS_RESULT, DIAGNOSTIC_PASS_RESULT}:
            result = "rehearsal_failed"
    operation_counters = {
        "sigkill": len(restarts),
        "participant_retry": 0,
        "provider_calls": 0,
        "product_reads": 0,
        "product_commands": 0,
        "external_network_operations": 0,
    }
    if diagnostic_mode:
        evidence = {
            "schema_version": "emr4.raisa-context-fabric-disposable-postgresql-durability-restart-unknown-commit-recovery-diagnostic-evidence.v1",
            "result": result,
            "evidence_mode": DIAGNOSTIC_EVIDENCE_MODE,
            "attempt_id": attempt_id,
            "parent": parent_evidence,
            "environment": environment,
            "lifecycle": lifecycle,
            "preconditions": [row["name"] for row in preconditions],
            "terminal_observations": diagnostic_observations,
            "operation_counters": {**operation_counters, "restart": 0},
            "cleanup": _cleanup_evidence(cleanup),
            "claim_boundary": DIAGNOSTIC_CLAIM_BOUNDARY,
        }
        if failure is not None:
            evidence["failure"] = _bounded_failure(failure)
            if isinstance(failure, TerminalFailure):
                evidence["terminal_failure"] = failure.terminal_evidence
    else:
        evidence = {
            "schema_version": "emr4.raisa-context-fabric-disposable-postgresql-durability-restart-unknown-commit-evidence.v1",
            "result": result,
            "evidence_mode": EVIDENCE_MODE,
            "attempt_id": attempt_id,
            "parent": parent_evidence,
            "environment": environment,
            "lifecycle": lifecycle,
            "preconditions": preconditions,
            "restarts": restarts,
            "scenarios": scenarios,
            "scenario_reconciliation": {
                "expected": 4,
                "observed": len(scenarios),
                "passed": sum(1 for row in scenarios if row.get("passed")),
            },
            "operation_counters": operation_counters,
            "cleanup": _cleanup_evidence(cleanup),
            "claim_boundary": CLAIM_BOUNDARY,
        }
        if failure is not None:
            evidence["environment"]["failure"] = _bounded_failure(failure)
    evidence["environment"]["elapsed_ms"] = int((time.monotonic() - started) * 1000)
    return evidence


def validate_evidence(payload: dict[str, Any]) -> None:
    schema = _json(EVIDENCE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise RestartFailure("evidence", "schema_validation")
    if payload.get("result") != PASS_RESULT:
        return
    contract = _json(CONTRACT_PATH)
    scenarios = payload["scenarios"]
    if tuple(row["scenario_id"] for row in scenarios) != SCENARIO_ORDER:
        raise RestartFailure("evidence", "scenario_order")
    expected = {row["id"]: row for row in contract["scenarios"]}
    for row in scenarios:
        spec = expected[row["scenario_id"]]
        if (
            row["category"] != spec["category"]
            or row["client_observation"] != spec["client_observation"]
            or row["recovery_classification"] != spec["post_restart_classification"]
            or row["restart_exact_match"] is not True
            or row["pre_crash_snapshot"] != row["post_restart_snapshot"]
            or set(row["readback_checks"]) != set(spec["readback"])
            or set(row["forbidden_effects_absent"]) != set(spec["forbidden_effects"])
        ):
            raise RestartFailure("evidence", "scenario_semantics")
        indeterminate = [
            action for action in row["actions"] if action["outcome"] == "indeterminate"
        ]
        if row["scenario_id"] in {"CFD2-R03", "CFD2-R04"}:
            if len(indeterminate) != 1:
                raise RestartFailure("evidence", "indeterminate_observation")
        elif indeterminate:
            raise RestartFailure("evidence", "unexpected_indeterminate_observation")
    if (
        classify_recovery(
            scenarios[2]["pre_transition_packet"], scenarios[2]["post_restart_packet"]
        )
        != "COMMITTED_RECOVERED"
    ):
        raise RestartFailure("evidence", "committed_recovery_packet")
    if (
        classify_recovery(
            scenarios[3]["pre_transition_packet"], scenarios[3]["post_restart_packet"]
        )
        != "ROLLED_BACK_RECOVERED"
    ):
        raise RestartFailure("evidence", "rollback_recovery_packet")
    if scenarios[1]["pre_transition_packet"] != scenarios[1]["post_restart_packet"]:
        raise RestartFailure("evidence", "confirmed_rollback_packet")
    if payload["restarts"] != [row["restart"] for row in scenarios]:
        raise RestartFailure("evidence", "restart_reconciliation")
    expected_preconditions = [
        *(f"register_observer_r0{number}" for number in range(1, 5)),
        "produce_position_one",
        "produce_position_two",
        *(f"admit_observer_r0{number}_position_1" for number in range(1, 5)),
    ]
    if [row["name"] for row in payload["preconditions"]] != expected_preconditions:
        raise RestartFailure("evidence", "precondition_order")
    forbidden_keys = {
        "stdout",
        "stderr",
        "query",
        "raw_sql",
        "server_log",
        "wal",
        "backend_pid",
        "lock_key",
        "credential",
        "database_url",
    }

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if forbidden_keys.intersection(value):
                raise RestartFailure("evidence", "forbidden_key")
            for member in value.values():
                visit(member)
        elif isinstance(value, list):
            for member in value:
                visit(member)

    visit(payload)


def validate_diagnostic_evidence(payload: dict[str, Any]) -> None:
    schema = _json(DIAGNOSTIC_EVIDENCE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise RestartFailure("diagnostic_evidence", "schema_validation")

    terminal_failure = payload.get("terminal_failure")
    failure = payload.get("failure")
    if terminal_failure is not None:
        if failure is None or (
            terminal_failure["coordinate"] != failure["stage"]
            or terminal_failure["code"] != failure["code"]
        ):
            raise RestartFailure("diagnostic_evidence", "failure_reconciliation")

    forbidden_keys = {
        "stdout",
        "stderr",
        "query",
        "query_text",
        "raw_sql",
        "error_text",
        "server_log",
        "wal",
        "backend_pid",
        "lock_key",
        "credential",
        "database_url",
        "environment_value",
    }

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if forbidden_keys.intersection(value):
                raise RestartFailure("diagnostic_evidence", "forbidden_key")
            for member in value.values():
                visit(member)
        elif isinstance(value, list):
            for member in value:
                visit(member)

    visit(payload)
    if payload.get("result") != DIAGNOSTIC_PASS_RESULT:
        return
    if (
        payload["parent"]["contract_sha256"] != EXPECTED_CONTRACT_SHA256
        or payload["parent"]["recovery_contract_sha256"]
        != EXPECTED_RECOVERY_CONTRACT_SHA256
    ):
        raise RestartFailure("diagnostic_evidence", "parent_contract_digest")
    if payload["lifecycle"] != [
        "eight_parent_bindings_verified",
        "container_owned_and_storage_closed",
        "postgres16_artifact_and_durability_reconciled",
        "four_disjoint_generations_prepared",
        "no_crash_r01_apply_anchor_matched",
        "catalogue_reconciled",
        "cleanup_verified",
        "passed",
    ]:
        raise RestartFailure("diagnostic_evidence", "lifecycle_order")
    expected_preconditions = [
        *(f"register_observer_r0{number}" for number in range(1, 5)),
        "produce_position_one",
        "produce_position_two",
        *(f"admit_observer_r0{number}_position_1" for number in range(1, 5)),
    ]
    if payload["preconditions"] != expected_preconditions:
        raise RestartFailure("diagnostic_evidence", "precondition_order")
    if payload["terminal_observations"] != [
        {
            "coordinate": "cfd2_r01_apply_position_1",
            "code": "matched_expected_terminal",
            "returncode_class": "zero",
            "sqlstate": None,
            "result_lines": ["RECEIPT_APPLIED"],
            "passed": True,
        },
        {
            "coordinate": "cfd2_r01_append_anchor_2",
            "code": "matched_expected_terminal",
            "returncode_class": "zero",
            "sqlstate": None,
            "result_lines": ["1"],
            "passed": True,
        },
    ]:
        raise RestartFailure("diagnostic_evidence", "terminal_order")
    if any(payload["operation_counters"].values()):
        raise RestartFailure("diagnostic_evidence", "external_operation")
    if payload["cleanup"] != {
        "status": "cleanup_verified",
        "removed": True,
        "absence_verified": True,
    }:
        raise RestartFailure("diagnostic_evidence", "cleanup")
    if failure is not None or terminal_failure is not None:
        raise RestartFailure("diagnostic_evidence", "passing_failure")


def run_recovery_diagnostic(
    *,
    runner: Runner = serial.parent._subprocess_runner,  # noqa: SLF001
) -> dict[str, Any]:
    return run_rehearsal(runner=runner, diagnostic_mode=True)


def write_diagnostic_evidence(payload: dict[str, Any]) -> None:
    validate_diagnostic_evidence(payload)
    if DIAGNOSTIC_EVIDENCE_PATH.exists():
        raise RestartFailure("diagnostic_evidence", "immutable_attempt_exists")
    DIAGNOSTIC_EVIDENCE_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_evidence(payload: dict[str, Any]) -> None:
    validate_evidence(payload)
    if EVIDENCE_PATH.exists():
        raise RestartFailure("evidence", "immutable_attempt_exists")
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
