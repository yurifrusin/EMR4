"""Run the fixed provider-free CF-D1 PostgreSQL concurrency rehearsal."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal as serial,
)


BASE = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
)
CONTRACT_PATH = BASE / "concurrency-rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = BASE / "concurrency-rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = (
    BASE / "provider-free-durability-concurrency-evidence.schema.json"
)
EVIDENCE_PATH = BASE / "provider-free-durability-concurrency-evidence-attempt-004.json"
EXPECTED_CONTRACT_SHA256 = (
    "sha256:96b3fb92d302206eb757f51203044c2aeeb76248a6844422404d13c79b785391"
)
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_pass"
)
EVIDENCE_MODE = "provider_free_disposable_postgresql_authored_synthetic_concurrency"
CLAIM_BOUNDARY = (
    "six_exact_two_session_postgresql16_concurrency_outcomes_only_no_restart_"
    "unknown_commit_runtime_product_provider_command_deployment_or_production_claim"
)
RESULT_VOCABULARY = frozenset(
    {
        "PRIMARY",
        "CONFLICT",
        "RECEIPT_APPLIED",
        "RECEIPT_REPLAYED",
        "1",
        "2",
    }
)
PARTICIPANT_LABEL = re.compile(r"^emr4_cf_d1_c0[1-6]_[abr]$")
RESULT_COORDINATE = re.compile(
    r"^(?:CFD1-C0[1-6]\.(?:leader|contender)|[a-z][a-z0-9_]{0,63})$"
)
EXPECTED_CHANGED_RELATIONS = {
    "CFD1-C01": {
        "emr4_context_fabric.context_durability_checkpoint": 1,
        "emr4_context_fabric.context_frame_generation": 2,
        "emr4_context_fabric.context_generation_registry_barrier": 0,
        "emr4_context_fabric.context_invalidation_watermark": 2,
        "emr4_context_fabric.context_observation_key_interval": 1,
        "emr4_context_fabric.context_observation_stream_head": 1,
        "emr4_context_fabric.context_observer_generation": 1,
        "emr4_context_fabric.context_recovery_anchor": 1,
    },
    "CFD1-C02": {
        "emr4_context_fabric.context_observation_stream_head": 0,
        "emr4_context_fabric.diary_context_aggregate_aliases_v1": 2,
        "emr4_context_fabric.diary_context_observation_outbox_v1": 2,
        "public.appointment_audit_log": 2,
        "public.appointment_command_idempotency": 2,
        "public.appointments": 0,
        "public.diary_committed_events": 2,
    },
    "CFD1-C03": {
        "emr4_context_fabric.context_proofread_observation_admission": 1,
    },
    "CFD1-C04": {
        "emr4_context_fabric.context_proofread_observation_admission": 2,
    },
    "CFD1-C05": {
        "emr4_context_fabric.context_classified_observation_receipt": 1,
        "emr4_context_fabric.context_durability_audit": 1,
        "emr4_context_fabric.context_durability_checkpoint": 0,
        "emr4_context_fabric.context_durability_lifecycle": 1,
        "emr4_context_fabric.context_frame_generation": 0,
        "emr4_context_fabric.context_invalidation_watermark": 0,
        "emr4_context_fabric.context_reassembly_obligation": 1,
    },
    "CFD1-C06": {
        "emr4_context_fabric.context_classified_observation_receipt": 1,
        "emr4_context_fabric.context_durability_audit": 1,
        "emr4_context_fabric.context_durability_checkpoint": 0,
        "emr4_context_fabric.context_durability_lifecycle": 1,
        "emr4_context_fabric.context_frame_generation": 0,
        "emr4_context_fabric.context_invalidation_watermark": 0,
        "emr4_context_fabric.context_reassembly_obligation": 1,
    },
}

Runner = Callable[[list[str], bytes | None, int, int], serial.parent.ProcessResult]


class ConcurrencyFailure(serial.BehaviorFailure):
    """Bounded CF-D1 failure."""


def _counting_runner(runner: Runner, counts: dict[str, int]) -> Runner:
    lock = threading.Lock()
    marker = re.compile(rb"(?m)^SET application_name TO 'emr4_cf_d1_c0[1-6]_([abr])';$")

    def counted(
        argv: list[str], stdin: bytes | None, timeout: int, cap: int
    ) -> serial.parent.ProcessResult:
        if stdin is not None:
            matches = marker.findall(stdin)
            if len(matches) > 1:
                raise ConcurrencyFailure("counting", "participant_marker_ambiguous")
            if matches:
                key = (
                    "precondition_transactions"
                    if matches[0] == b"r"
                    else "participant_transactions"
                )
                with lock:
                    counts[key] += 1
        return runner(argv, stdin, timeout, cap)

    return counted


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ConcurrencyFailure("contract", "json_object_required")
    return value


def _sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _file_digest(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _profile() -> dict[str, Any]:
    profile = copy.deepcopy(serial._profile())  # noqa: SLF001
    profile.update(
        {
            "container_name_prefix": "emr4-cf-pg16-concurrency-",
            "ownership_labels": {
                "com.emr4.harness": "disposable-postgresql-durability-concurrency-v1",
                "com.emr4.cleanup-nonce": "per_run_random_hex",
            },
            "postgres_database": "emr4_synthetic_concurrency",
            "artifact_timeout_seconds": 120,
            "total_timeout_seconds": 480,
            "command_timeout_seconds": 15,
        }
    )
    return profile


def _validate_contract() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], bytes
]:
    contract = _json(CONTRACT_PATH)
    if _file_digest(CONTRACT_PATH) != EXPECTED_CONTRACT_SHA256:
        raise ConcurrencyFailure("contract", "contract_sha256")
    schema = _json(CONTRACT_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    if contract["status"] != "frozen_provider_free_planning_runtime_closed":
        raise ConcurrencyFailure("contract", "runtime_not_closed")
    if contract["scenario_order"] != [f"CFD1-C0{i}" for i in range(1, 7)]:
        raise ConcurrencyFailure("contract", "scenario_order")
    if [row["id"] for row in contract["scenarios"]] != contract["scenario_order"]:
        raise ConcurrencyFailure("contract", "scenario_population")
    if contract["synchronization_profile"]["participant_retry_count"] != 0:
        raise ConcurrencyFailure("contract", "participant_retry")
    if contract["fixture_authority"]["fabric_direct_grant_changes"] != []:
        raise ConcurrencyFailure("contract", "fabric_grant_change")
    bindings = contract["parent_bindings"]
    if len(bindings) != 8 or len({row["id"] for row in bindings}) != 8:
        raise ConcurrencyFailure("parent", "binding_population")
    for binding in bindings:
        relative = Path(binding["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ConcurrencyFailure("parent", "binding_path", binding["id"])
        path = ROOT / relative
        if not path.is_file() or _file_digest(path) != binding["sha256"]:
            raise ConcurrencyFailure("parent", "binding_sha256", binding["id"])
    serial_contract, prerequisite, manifest, artifact = serial._validate_contract()  # noqa: SLF001
    if _sha256_bytes(artifact) != next(
        row["sha256"] for row in bindings if row["id"] == "inert_sql"
    ):
        raise ConcurrencyFailure("parent", "artifact_identity")
    if manifest["statement_count"] != 424:
        raise ConcurrencyFailure("parent", "statement_count")
    return contract, serial_contract, prerequisite, manifest, artifact


def _facts(serial_contract: dict[str, Any]) -> dict[str, Any]:
    facts = copy.deepcopy(serial_contract["fixture_namespace"])
    facts.update(
        {
            "observer_registration": "40000000-0000-4000-8000-000000000101",
            "observer_admission_same": "40000000-0000-4000-8000-000000000102",
            "observer_admission_divergent": "40000000-0000-4000-8000-000000000103",
            "observer_coordinator_commit": "40000000-0000-4000-8000-000000000104",
            "observer_coordinator_rollback": "40000000-0000-4000-8000-000000000105",
        }
    )
    for key in (
        "observer_registration",
        "observer_admission_same",
        "observer_admission_divergent",
        "observer_coordinator_commit",
        "observer_coordinator_rollback",
    ):
        if not serial.UUID.fullmatch(facts[key]):
            raise ConcurrencyFailure("fixture", "observer_uuid", key)
    return facts


def _application_name(scenario_id: str, participant: str) -> str:
    label = f"emr4_cf_d1_{scenario_id[-3:].lower()}_{participant}"
    if not PARTICIPANT_LABEL.fullmatch(label):
        raise ConcurrencyFailure("render", "application_name")
    return label


def _participant_script(
    contract: dict[str, Any],
    *,
    scenario_id: str,
    participant: str,
    principal: str,
    isolation: str,
    statements: list[str],
    hold: bool = False,
    injected_rollback: bool = False,
) -> bytes:
    if scenario_id not in contract["scenario_order"] or participant not in {
        "a",
        "b",
        "r",
    }:
        raise ConcurrencyFailure("render", "participant_coordinate")
    if principal not in contract["fixture_authority"]["principals"]:
        raise ConcurrencyFailure("render", "principal")
    if isolation not in {"read committed", "serializable"}:
        raise ConcurrencyFailure("render", "isolation")
    sync = contract["synchronization_profile"]
    lines = [
        f"SET application_name TO {serial._lit(_application_name(scenario_id, participant))};",  # noqa: SLF001
        f"SET SESSION AUTHORIZATION {principal};",
        f"BEGIN ISOLATION LEVEL {isolation.upper()};",
        f"SET LOCAL statement_timeout TO {serial._lit(str(sync['statement_timeout_milliseconds']) + 'ms')};",  # noqa: SLF001
        f"SET LOCAL lock_timeout TO {serial._lit(str(sync['lock_timeout_milliseconds']) + 'ms')};",  # noqa: SLF001
        "SET LOCAL idle_in_transaction_session_timeout TO "
        f"{serial._lit(str(sync['idle_in_transaction_timeout_milliseconds']) + 'ms')};",  # noqa: SLF001
        serial._identity_select(principal),  # noqa: SLF001
        *statements,
    ]
    if hold:
        lines.append(
            "SELECT pg_catalog.pg_sleep("
            f"{sync['leader_hold_milliseconds']}::pg_catalog.numeric / 1000);"
        )
    if injected_rollback:
        lines.append(
            "DO $fixed_abort$ BEGIN RAISE EXCEPTION USING ERRCODE='P0001', "
            "MESSAGE='fixed_injected_rollback'; END $fixed_abort$;"
        )
    lines.append("COMMIT;")
    rendered = "\n".join(lines) + "\n"
    if (
        rendered.count("SET SESSION AUTHORIZATION") != 1
        or rendered.count("BEGIN ISOLATION LEVEL") != 1
    ):
        raise ConcurrencyFailure("render", "transaction_shape")
    if re.search(r"\b(SET ROLE|SAVEPOINT|PREPARE TRANSACTION)\b", rendered, re.I):
        raise ConcurrencyFailure("render", "forbidden_transaction_control")
    if hold != ("pg_catalog.pg_sleep" in rendered):
        raise ConcurrencyFailure("render", "hold_shape")
    return rendered.encode("utf-8")


def _scenario_argv(
    docker: str, container_id: str, profile: dict[str, Any]
) -> list[str]:
    argv = serial._scenario_argv(docker, container_id, profile)  # noqa: SLF001
    serial.assert_scenario_argv(argv)
    return argv


def _call_script(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    script: bytes,
) -> serial.parent.ProcessResult:
    return runner(
        _scenario_argv(docker, container_id, profile),
        script,
        profile["command_timeout_seconds"],
        profile["stdout_stderr_cap_bytes"],
    )


def _activity_state(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    if not PARTICIPANT_LABEL.fullmatch(label):
        raise ConcurrencyFailure("observation", "application_name")
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
        query_id="concurrency_activity",
    )
    if (
        not isinstance(value, dict)
        or set(value) != {"count", "wait_event_type", "wait_event"}
        or type(value["count"]) is not int
        or value["count"] not in {0, 1}
        or not isinstance(value["wait_event_type"], str)
        or not isinstance(value["wait_event"], str)
    ):
        raise ConcurrencyFailure("observation", "activity_shape")
    return value


def _wait_for_state(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    label: str,
    *,
    event_type: str,
    event: str | None,
    future: Future[serial.parent.ProcessResult],
) -> int:
    sync = contract["synchronization_profile"]
    started = time.monotonic()
    ceiling = sync["overlap_observation_ceiling_milliseconds"] / 1000
    interval = sync["poll_interval_milliseconds"] / 1000
    while time.monotonic() - started <= ceiling:
        if future.done():
            raise ConcurrencyFailure("observation", "participant_ended_before_state")
        state = _activity_state(runner, docker, container_id, profile, label)
        if state["count"] == 1 and state["wait_event_type"] == event_type:
            if event is None or state["wait_event"] == event:
                return int((time.monotonic() - started) * 1000)
        time.sleep(interval)
    raise ConcurrencyFailure("observation", "required_wait_state_not_observed")


def _run_pair(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    scenario_id: str,
    leader_script: bytes,
    contender_script: bytes,
) -> tuple[serial.parent.ProcessResult, serial.parent.ProcessResult, dict[str, Any]]:
    leader_label = _application_name(scenario_id, "a")
    contender_label = _application_name(scenario_id, "b")
    argv = _scenario_argv(docker, container_id, profile)
    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="cf-d1") as executor:
        leader_future = executor.submit(
            runner,
            argv,
            leader_script,
            profile["command_timeout_seconds"],
            profile["stdout_stderr_cap_bytes"],
        )
        leader_observed_ms = _wait_for_state(
            runner,
            docker,
            container_id,
            profile,
            contract,
            leader_label,
            event_type="Timeout",
            event="PgSleep",
            future=leader_future,
        )
        contender_future = executor.submit(
            runner,
            argv,
            contender_script,
            profile["command_timeout_seconds"],
            profile["stdout_stderr_cap_bytes"],
        )
        contender_observed_ms = _wait_for_state(
            runner,
            docker,
            container_id,
            profile,
            contract,
            contender_label,
            event_type="Lock",
            event=None,
            future=contender_future,
        )
        leader = leader_future.result(timeout=profile["command_timeout_seconds"] + 1)
        contender = contender_future.result(
            timeout=profile["command_timeout_seconds"] + 1
        )
    overlap = {
        "leader_post_function_hold_observed": True,
        "leader_wait_event_type": "Timeout",
        "leader_wait_event": "PgSleep",
        "leader_observed_within_ms": leader_observed_ms,
        "contender_lock_wait_observed": True,
        "contender_wait_event_type": "Lock",
        "contender_observed_within_ms": contender_observed_ms,
    }
    return leader, contender, overlap


def _identity(
    result: serial.parent.ProcessResult, principal: str, isolation: str
) -> dict[str, Any]:
    return serial._identity_from_stdout(  # noqa: SLF001
        result,
        principal,
        expected_read_only=False,
        expected_isolation=isolation,
    )


def _result_lines(result: serial.parent.ProcessResult) -> list[str]:
    lines = [line.strip() for line in result.stdout.decode("utf-8").splitlines()]
    return [line for line in lines if line in RESULT_VOCABULARY]


def _transport(result: serial.parent.ProcessResult) -> dict[str, Any]:
    return {
        "psql_exit": result.returncode,
        "stdout": {
            "byte_count": len(result.stdout),
            "sha256": _sha256_bytes(result.stdout),
        },
        "stderr": {
            "byte_count": len(result.stderr),
            "sha256": _sha256_bytes(result.stderr),
        },
    }


def _expect_success(
    result: serial.parent.ProcessResult,
    *,
    coordinate: str,
    principal: str,
    isolation: str,
    expected_lines: list[str],
) -> dict[str, Any]:
    if not RESULT_COORDINATE.fullmatch(coordinate):
        raise ConcurrencyFailure("scenario", "diagnostic_coordinate")
    if result.returncode != 0:
        raise ConcurrencyFailure(
            "scenario",
            "unexpected_participant_failure",
            {
                "coordinate": coordinate,
                "principal": principal,
                "isolation": isolation,
                "observed_sqlstate": serial._safe_sqlstate(result),  # noqa: SLF001
            },
        )
    identity = _identity(result, principal, isolation)
    observed_lines = _result_lines(result)
    if observed_lines != expected_lines:
        raise ConcurrencyFailure(
            "scenario",
            "result_marker",
            {
                "coordinate": coordinate,
                "principal": principal,
                "isolation": isolation,
                "expected_result_lines": expected_lines,
                "observed_result_lines": observed_lines[:4],
                "observed_result_count": len(observed_lines),
            },
        )
    return {
        "outcome": "commit",
        "sqlstate": None,
        "identity": identity,
        "result_lines": expected_lines,
        "transport": _transport(result),
    }


def _expect_failure(
    result: serial.parent.ProcessResult,
    *,
    coordinate: str,
    principal: str,
    isolation: str,
    sqlstate: str,
    expected_lines: list[str] | None = None,
) -> dict[str, Any]:
    if not RESULT_COORDINATE.fullmatch(coordinate):
        raise ConcurrencyFailure("scenario", "diagnostic_coordinate")
    observed_sqlstate = serial._safe_sqlstate(result)  # noqa: SLF001
    if result.returncode == 0 or observed_sqlstate != sqlstate:
        raise ConcurrencyFailure(
            "scenario",
            "unexpected_sqlstate",
            {
                "coordinate": coordinate,
                "principal": principal,
                "isolation": isolation,
                "expected_sqlstate": sqlstate,
                "observed_sqlstate": observed_sqlstate,
            },
        )
    identity = _identity(result, principal, isolation)
    lines = _result_lines(result)
    if expected_lines is not None and lines != expected_lines:
        raise ConcurrencyFailure(
            "scenario",
            "failure_result_marker",
            {
                "coordinate": coordinate,
                "principal": principal,
                "isolation": isolation,
                "expected_result_lines": expected_lines,
                "observed_result_lines": lines[:4],
                "observed_result_count": len(lines),
            },
        )
    return {
        "outcome": "rollback",
        "sqlstate": sqlstate,
        "identity": identity,
        "result_lines": lines,
        "transport": _transport(result),
    }


def _assert_snapshot_effect(
    scenario_id: str,
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
) -> None:
    expected = EXPECTED_CHANGED_RELATIONS[scenario_id]
    if set(before) != set(serial.SNAPSHOT_RELATIONS) or set(after) != set(before):
        raise ConcurrencyFailure("readback", "snapshot_population")
    for relation in serial.SNAPSHOT_RELATIONS:
        delta = after[relation]["count"] - before[relation]["count"]
        expected_delta = expected.get(relation, 0)
        if delta != expected_delta:
            raise ConcurrencyFailure(
                "readback",
                "count_delta",
                {"scenario_id": scenario_id, "relation": relation},
            )
        changed = after[relation]["digest"] != before[relation]["digest"]
        if changed != (relation in expected):
            raise ConcurrencyFailure(
                "readback",
                "digest_delta",
                {"scenario_id": scenario_id, "relation": relation},
            )


def _assert_replay_inert(
    expected: dict[str, dict[str, Any]], actual: dict[str, dict[str, Any]]
) -> None:
    if actual != expected:
        raise ConcurrencyFailure("readback", "replay_not_inert")


def _register_statements(facts: dict[str, Any], observer: str) -> list[str]:
    return [
        "SELECT (emr4_context_fabric.register_observer_generation_v1("
        + serial._registration(facts, observer)  # noqa: SLF001
        + ")).observer_id;"
    ]


def _admission_statements(
    facts: dict[str, Any], observer: str, position: int, *, conflict: bool = False
) -> list[str]:
    packet = serial._packet(facts, conflict=conflict).replace(  # noqa: SLF001
        "__POSITION__", str(position)
    )
    return [
        "SELECT (emr4_context_fabric.admit_proofread_observation_v1("
        + serial._locator(facts, observer)  # noqa: SLF001
        + f",{position}::pg_catalog.int8,{packet})).entry_kind::pg_catalog.text;"
    ]


def _coordinator_statements(
    facts: dict[str, Any], observer: str, position: int
) -> list[str]:
    return [
        "SELECT (emr4_context_fabric.apply_durability_transition_v1(ROW("
        + serial._locator(facts, observer)  # noqa: SLF001
        + f",{position}::pg_catalog.int8)::emr4_context_fabric.admission_locator_v1))"
        ".result_kind::pg_catalog.text;"
    ]


def _producer_statements(facts: dict[str, Any], *, second: bool) -> list[str]:
    return serial._producer_transaction(  # noqa: SLF001
        facts,
        appointment="appointment_negative" if second else "appointment_temporal",
        command="command_position_two" if second else "command_position_one",
        audit="audit_position_two" if second else "audit_position_one",
        event="event_position_two" if second else "event_position_one",
    )


def _run_precondition(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    *,
    name: str,
    scenario_id: str,
    principal: str,
    isolation: str,
    statements: list[str],
    expected_lines: list[str],
) -> dict[str, Any]:
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
        ),
    )
    outcome = _expect_success(
        result,
        coordinate=name,
        principal=principal,
        isolation=isolation,
        expected_lines=expected_lines,
    )
    return {"name": name, "passed": True, "outcome": outcome}


def _scenario_record(
    contract: dict[str, Any],
    scenario_id: str,
    *,
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
    overlap: dict[str, Any],
    leader: dict[str, Any],
    contender: dict[str, Any],
    post_race: list[dict[str, Any]],
) -> dict[str, Any]:
    spec = next(row for row in contract["scenarios"] if row["id"] == scenario_id)
    return {
        "scenario_id": scenario_id,
        "category": spec["category"],
        "principal": spec["principal"],
        "isolation": spec["isolation"],
        "overlap": overlap,
        "leader": leader,
        "contender": contender,
        "post_race": post_race,
        "before": before,
        "after": after,
        "readback_checks": {name: True for name in spec["readback"]},
        "forbidden_effects_absent": {name: True for name in spec["forbidden_effects"]},
        "passed": True,
    }


def _run_scenarios(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    contract: dict[str, Any],
    serial_contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    facts = _facts(serial_contract)
    records: list[dict[str, Any]] = []
    preconditions: list[dict[str, Any]] = []

    # CFD1-C01 — identical registration.
    scenario_id = "CFD1-C01"
    before = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    leader_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="a",
        principal="context_lifecycle",
        isolation="serializable",
        statements=_register_statements(facts, "observer_registration"),
        hold=True,
    )
    contender_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="b",
        principal="context_lifecycle",
        isolation="serializable",
        statements=_register_statements(facts, "observer_registration"),
    )
    leader_result, contender_result, overlap = _run_pair(
        runner,
        docker,
        container_id,
        profile,
        contract,
        scenario_id,
        leader_script,
        contender_script,
    )
    leader = _expect_success(
        leader_result,
        coordinate="CFD1-C01.leader",
        principal="context_lifecycle",
        isolation="serializable",
        expected_lines=[],
    )
    contender = _expect_failure(
        contender_result,
        coordinate="CFD1-C01.contender",
        principal="context_lifecycle",
        isolation="serializable",
        sqlstate="40001",
        expected_lines=[],
    )
    after_race = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    replay = _run_precondition(
        runner,
        docker,
        container_id,
        profile,
        contract,
        name="c01_exact_registration_replay",
        scenario_id=scenario_id,
        principal="context_lifecycle",
        isolation="serializable",
        statements=_register_statements(facts, "observer_registration"),
        expected_lines=[],
    )
    after = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    _assert_snapshot_effect(scenario_id, before, after_race)
    _assert_replay_inert(after_race, after)
    records.append(
        _scenario_record(
            contract,
            scenario_id,
            before=before,
            after=after,
            overlap=overlap,
            leader=leader,
            contender=contender,
            post_race=[replay],
        )
    )

    # Register the four disjoint observer generations at stream position zero.
    for observer in (
        "observer_admission_same",
        "observer_admission_divergent",
        "observer_coordinator_commit",
        "observer_coordinator_rollback",
    ):
        preconditions.append(
            _run_precondition(
                runner,
                docker,
                container_id,
                profile,
                contract,
                name=f"register_{observer}",
                scenario_id="CFD1-C01",
                principal="context_lifecycle",
                isolation="serializable",
                statements=_register_statements(facts, observer),
                expected_lines=[],
            )
        )

    # CFD1-C02 — distinct producers share one stream head.
    scenario_id = "CFD1-C02"
    before = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    leader_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="a",
        principal="context_producer",
        isolation="read committed",
        statements=_producer_statements(facts, second=False),
        hold=True,
    )
    contender_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="b",
        principal="context_producer",
        isolation="read committed",
        statements=_producer_statements(facts, second=True),
    )
    leader_result, contender_result, overlap = _run_pair(
        runner,
        docker,
        container_id,
        profile,
        contract,
        scenario_id,
        leader_script,
        contender_script,
    )
    leader = _expect_success(
        leader_result,
        coordinate="CFD1-C02.leader",
        principal="context_producer",
        isolation="read committed",
        expected_lines=["1"],
    )
    contender = _expect_success(
        contender_result,
        coordinate="CFD1-C02.contender",
        principal="context_producer",
        isolation="read committed",
        expected_lines=["2"],
    )
    after = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    _assert_snapshot_effect(scenario_id, before, after)
    records.append(
        _scenario_record(
            contract,
            scenario_id,
            before=before,
            after=after,
            overlap=overlap,
            leader=leader,
            contender=contender,
            post_race=[],
        )
    )

    # CFD1-C03 — identical admission.
    scenario_id = "CFD1-C03"
    before = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    leader_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="a",
        principal="context_observer",
        isolation="read committed",
        statements=_admission_statements(facts, "observer_admission_same", 1),
        hold=True,
    )
    contender_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="b",
        principal="context_observer",
        isolation="read committed",
        statements=_admission_statements(facts, "observer_admission_same", 1),
    )
    leader_result, contender_result, overlap = _run_pair(
        runner,
        docker,
        container_id,
        profile,
        contract,
        scenario_id,
        leader_script,
        contender_script,
    )
    leader = _expect_success(
        leader_result,
        coordinate="CFD1-C03.leader",
        principal="context_observer",
        isolation="read committed",
        expected_lines=["PRIMARY"],
    )
    contender = _expect_success(
        contender_result,
        coordinate="CFD1-C03.contender",
        principal="context_observer",
        isolation="read committed",
        expected_lines=["PRIMARY"],
    )
    after = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    _assert_snapshot_effect(scenario_id, before, after)
    records.append(
        _scenario_record(
            contract,
            scenario_id,
            before=before,
            after=after,
            overlap=overlap,
            leader=leader,
            contender=contender,
            post_race=[],
        )
    )

    # CFD1-C04 — divergent admission.
    scenario_id = "CFD1-C04"
    before = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    leader_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="a",
        principal="context_observer",
        isolation="read committed",
        statements=_admission_statements(facts, "observer_admission_divergent", 2),
        hold=True,
    )
    contender_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="b",
        principal="context_observer",
        isolation="read committed",
        statements=_admission_statements(
            facts, "observer_admission_divergent", 2, conflict=True
        ),
    )
    leader_result, contender_result, overlap = _run_pair(
        runner,
        docker,
        container_id,
        profile,
        contract,
        scenario_id,
        leader_script,
        contender_script,
    )
    leader = _expect_success(
        leader_result,
        coordinate="CFD1-C04.leader",
        principal="context_observer",
        isolation="read committed",
        expected_lines=["PRIMARY"],
    )
    contender = _expect_failure(
        contender_result,
        coordinate="CFD1-C04.contender",
        principal="context_observer",
        isolation="read committed",
        sqlstate="CF004",
        expected_lines=[],
    )
    conflict = _run_precondition(
        runner,
        docker,
        container_id,
        profile,
        contract,
        name="c04_fresh_conflict",
        scenario_id=scenario_id,
        principal="context_observer",
        isolation="read committed",
        statements=_admission_statements(
            facts, "observer_admission_divergent", 2, conflict=True
        ),
        expected_lines=["CONFLICT"],
    )
    after_conflict = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    conflict_replay = _run_precondition(
        runner,
        docker,
        container_id,
        profile,
        contract,
        name="c04_exact_conflict_replay",
        scenario_id=scenario_id,
        principal="context_observer",
        isolation="read committed",
        statements=_admission_statements(
            facts, "observer_admission_divergent", 2, conflict=True
        ),
        expected_lines=["CONFLICT"],
    )
    after = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    _assert_snapshot_effect(scenario_id, before, after_conflict)
    _assert_replay_inert(after_conflict, after)
    records.append(
        _scenario_record(
            contract,
            scenario_id,
            before=before,
            after=after,
            overlap=overlap,
            leader=leader,
            contender=contender,
            post_race=[conflict, conflict_replay],
        )
    )

    # Pre-admit the two coordinator generations.
    for observer, name in (
        ("observer_coordinator_commit", "admit_coordinator_commit_primary"),
        ("observer_coordinator_rollback", "admit_coordinator_rollback_primary"),
    ):
        preconditions.append(
            _run_precondition(
                runner,
                docker,
                container_id,
                profile,
                contract,
                name=name,
                scenario_id="CFD1-C03",
                principal="context_observer",
                isolation="read committed",
                statements=_admission_statements(facts, observer, 1),
                expected_lines=["PRIMARY"],
            )
        )

    # CFD1-C05 — identical coordinator application.
    scenario_id = "CFD1-C05"
    before = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    leader_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="a",
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, "observer_coordinator_commit", 1),
        hold=True,
    )
    contender_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="b",
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, "observer_coordinator_commit", 1),
    )
    leader_result, contender_result, overlap = _run_pair(
        runner,
        docker,
        container_id,
        profile,
        contract,
        scenario_id,
        leader_script,
        contender_script,
    )
    leader = _expect_success(
        leader_result,
        coordinate="CFD1-C05.leader",
        principal="context_coordinator",
        isolation="serializable",
        expected_lines=["RECEIPT_APPLIED"],
    )
    contender = _expect_failure(
        contender_result,
        coordinate="CFD1-C05.contender",
        principal="context_coordinator",
        isolation="serializable",
        sqlstate="40001",
        expected_lines=[],
    )
    after_race = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    replay = _run_precondition(
        runner,
        docker,
        container_id,
        profile,
        contract,
        name="c05_exact_coordinator_replay",
        scenario_id=scenario_id,
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, "observer_coordinator_commit", 1),
        expected_lines=["RECEIPT_REPLAYED"],
    )
    after = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    _assert_snapshot_effect(scenario_id, before, after_race)
    _assert_replay_inert(after_race, after)
    records.append(
        _scenario_record(
            contract,
            scenario_id,
            before=before,
            after=after,
            overlap=overlap,
            leader=leader,
            contender=contender,
            post_race=[replay],
        )
    )

    # CFD1-C06 — coordinator rollback with a waiting contender.
    scenario_id = "CFD1-C06"
    before = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    leader_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="a",
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, "observer_coordinator_rollback", 1),
        hold=True,
        injected_rollback=True,
    )
    contender_script = _participant_script(
        contract,
        scenario_id=scenario_id,
        participant="b",
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, "observer_coordinator_rollback", 1),
    )
    leader_result, contender_result, overlap = _run_pair(
        runner,
        docker,
        container_id,
        profile,
        contract,
        scenario_id,
        leader_script,
        contender_script,
    )
    leader = _expect_failure(
        leader_result,
        coordinate="CFD1-C06.leader",
        principal="context_coordinator",
        isolation="serializable",
        sqlstate="P0001",
        expected_lines=["RECEIPT_APPLIED"],
    )
    contender = _expect_success(
        contender_result,
        coordinate="CFD1-C06.contender",
        principal="context_coordinator",
        isolation="serializable",
        expected_lines=["RECEIPT_APPLIED"],
    )
    after_race = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    replay = _run_precondition(
        runner,
        docker,
        container_id,
        profile,
        contract,
        name="c06_exact_coordinator_replay",
        scenario_id=scenario_id,
        principal="context_coordinator",
        isolation="serializable",
        statements=_coordinator_statements(facts, "observer_coordinator_rollback", 1),
        expected_lines=["RECEIPT_REPLAYED"],
    )
    after = serial._snapshot(runner, docker, container_id, profile)  # noqa: SLF001
    _assert_snapshot_effect(scenario_id, before, after_race)
    _assert_replay_inert(after_race, after)
    records.append(
        _scenario_record(
            contract,
            scenario_id,
            before=before,
            after=after,
            overlap=overlap,
            leader=leader,
            contender=contender,
            post_race=[replay],
        )
    )

    return records, preconditions


def _bounded_failure(error: Exception) -> dict[str, Any]:
    if isinstance(error, serial.parent.RehearsalFailure):
        payload: dict[str, Any] = {"stage": error.stage, "code": error.code}
        if isinstance(error.detail, dict):
            for key in (
                "scenario_id",
                "coordinate",
                "principal",
                "isolation",
                "relation",
                "sqlstate",
                "expected_sqlstate",
                "observed_sqlstate",
            ):
                value = error.detail.get(key)
                if isinstance(value, str) and len(value) <= 128:
                    payload[key] = value
                elif (
                    key == "observed_sqlstate" and key in error.detail and value is None
                ):
                    payload[key] = None
            for key in ("expected_result_lines", "observed_result_lines"):
                value = error.detail.get(key)
                if (
                    isinstance(value, list)
                    and len(value) <= 4
                    and all(item in RESULT_VOCABULARY for item in value)
                ):
                    payload[key] = value
            count = error.detail.get("observed_result_count")
            if type(count) is int and 0 <= count <= 65536:
                payload["observed_result_count"] = count
        elif isinstance(error.detail, str) and len(error.detail) <= 128:
            payload["detail"] = error.detail
        return payload
    return {"stage": "unexpected", "code": type(error).__name__}


def run_rehearsal(
    *,
    runner: Runner = serial.parent._subprocess_runner,  # noqa: SLF001
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
    scenarios: list[dict[str, Any]] = []
    preconditions: list[dict[str, Any]] = []
    transaction_counts = {
        "participant_transactions": 0,
        "precondition_transactions": 0,
    }
    failure: Exception | None = None
    result = "rehearsal_failed"
    docker = container_id = image_id = name = nonce = ""
    profile: dict[str, Any] = {}
    cleanup_runner = runner
    try:
        contract, serial_contract, prerequisite, manifest, artifact = (
            _validate_contract()
        )
        profile = _profile()
        cleanup_reserve = 3 * profile["cleanup_timeout_seconds"]
        execution_seconds = profile["total_timeout_seconds"] - cleanup_reserve
        runner = serial.parent._with_total_deadline(  # noqa: SLF001
            runner, started + execution_seconds
        )
        runner = _counting_runner(runner, transaction_counts)
        prerequisite_sql = serial.parent.render_prerequisite_sql(prerequisite)
        parent_evidence = {
            "concurrency_contract_sha256": _file_digest(CONTRACT_PATH),
            "concurrency_contract_schema_sha256": _file_digest(CONTRACT_SCHEMA_PATH),
            "serial_pass_evidence_sha256": _file_digest(
                ROOT / contract["parent_bindings"][0]["path"]
            ),
            "inert_sql_sha256": _sha256_bytes(artifact),
            "render_manifest_sha256": _file_digest(
                ROOT
                / next(
                    row["path"]
                    for row in contract["parent_bindings"]
                    if row["id"] == "render_manifest"
                )
            ),
            "statement_count": manifest["statement_count"],
        }
        lifecycle.append("eight_parent_bindings_verified")
        docker = shutil.which(profile["executable"]) or ""
        if not docker or Path(docker).name.lower() != "docker.exe":
            raise ConcurrencyFailure("environment", "docker_client_missing")
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
            raise ConcurrencyFailure("environment", "exact_local_image_unavailable")
        image = serial.parent._one_json(image_result, "image_inspect")  # noqa: SLF001
        image_id = str(image.get("Id", ""))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
            raise ConcurrencyFailure("environment", "image_id_invalid")
        environment["image"] = {
            "reference": profile["image_reference"],
            "id": image_id,
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
            raise ConcurrencyFailure("environment", "container_name_not_proven_absent")
        run_argv = serial._run_argv(docker, profile, name=name, nonce=nonce)  # noqa: SLF001
        serial.assert_run_argv(run_argv)
        created = runner(
            run_argv,
            None,
            profile["command_timeout_seconds"],
            profile["stdout_stderr_cap_bytes"],
        )
        if created.returncode != 0:
            raise ConcurrencyFailure("container", "create_failed")
        container_id = created.stdout.decode("ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{12,64}", container_id):
            raise ConcurrencyFailure("container", "created_id_invalid")
        inspected = serial.parent._one_json(  # noqa: SLF001
            serial.parent._call(  # noqa: SLF001
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
            ),
            "container_inspect",
        )
        if not serial._behavior_container_owned(  # noqa: SLF001
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
        ):
            raise ConcurrencyFailure("container", "containment_mismatch")
        lifecycle.append("container_owned")
        for init_stage, init_argv, init_stdin in serial._init_argvs(  # noqa: SLF001
            docker, container_id, profile
        ):
            serial.assert_init_argv(init_argv, init_stdin)
            initialized = runner(
                init_argv,
                init_stdin,
                profile["startup_timeout_seconds"],
                profile["stdout_stderr_cap_bytes"],
            )
            if initialized.returncode != 0:
                raise ConcurrencyFailure("postgres_init", init_stage)
        lifecycle.append("passwordless_peer_cluster_started")
        environment["readiness"] = {}
        readiness_profile = copy.deepcopy(profile)
        readiness_profile["postgres_database"] = "postgres"
        serial.parent._wait_for_stable_postgres(  # noqa: SLF001
            runner,
            docker,
            container_id,
            readiness_profile,
            observation=environment["readiness"],
        )
        lifecycle.append("postgres_ready")
        create_database = serial.parent._call(  # noqa: SLF001
            runner,
            serial.parent.docker_argv(
                serial.parent.DockerOperation.PSQL_COMMAND,
                docker=docker,
                profile=readiness_profile,
                container_id=container_id,
                database="postgres",
                sql_command=f'CREATE DATABASE "{profile["postgres_database"]}";',
            ),
            operation=serial.parent.DockerOperation.PSQL_COMMAND,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if create_database.returncode != 0:
            raise ConcurrencyFailure("postgres", "database_create_failed")
        lifecycle.append("concurrency_database_ready")
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
            raise ConcurrencyFailure("artifact", "postgresql_rejected")
        lifecycle.append("artifact_admitted")
        catalogue = serial.parent._read_catalogue(  # noqa: SLF001
            runner, docker, container_id, profile["postgres_database"], profile
        )
        parent_contract = serial._json(serial.PARENT_REHEARSAL_CONTRACT_PATH)  # noqa: SLF001
        serial._assert_bound_parent_catalogue(  # noqa: SLF001
            catalogue,
            manifest,
            prerequisite,
            parent_contract,
            expected_database=profile["postgres_database"],
        )
        lifecycle.append("catalogue_reconciled")
        bootstrap = _call_script(
            runner,
            docker,
            container_id,
            profile,
            serial.render_bootstrap_sql(serial_contract),
        )
        if bootstrap.returncode != 0:
            raise ConcurrencyFailure(
                "fixture",
                "bootstrap_failed",
                serial._safe_bootstrap_failure_metadata(bootstrap),  # noqa: SLF001
            )
        fixture_catalogue = serial.parent._read_catalogue(  # noqa: SLF001
            runner, docker, container_id, profile["postgres_database"], profile
        )
        fixture_catalogue_digests = serial._assert_fixture_catalogue_delta(  # noqa: SLF001
            catalogue, fixture_catalogue
        )
        serial._assert_fixture_privileges(  # noqa: SLF001
            runner, docker, container_id, profile
        )
        lifecycle.append("fixtures_closed")
        scenarios, preconditions = _run_scenarios(
            runner,
            docker,
            container_id,
            profile,
            contract,
            serial_contract,
        )
        if [row["scenario_id"] for row in scenarios] != contract["scenario_order"]:
            raise ConcurrencyFailure("scenario", "terminal_order")
        final_catalogue = serial.parent._read_catalogue(  # noqa: SLF001
            runner, docker, container_id, profile["postgres_database"], profile
        )
        serial._assert_post_behavior_catalogue_stability(  # noqa: SLF001
            fixture_catalogue_digests, final_catalogue
        )
        lifecycle.extend(
            [
                "six_concurrency_scenarios_matched",
                "catalogue_reconciled_after_concurrency",
            ]
        )
        result = PASS_RESULT
    except Exception as error:  # evidence must survive every bounded failure
        failure = error
        if (
            isinstance(error, serial.parent.RehearsalFailure)
            and error.stage == "environment"
        ):
            result = "environment_unavailable"
    finally:
        if container_id:
            try:
                cleanup = serial._cleanup(  # noqa: SLF001
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
            except Exception as cleanup_error:
                cleanup = {
                    "status": "cleanup_failed",
                    "removed": False,
                    "absence_verified": False,
                    "failure": _bounded_failure(cleanup_error),
                }
                result = "rehearsal_failed"
                if failure is None:
                    failure = cleanup_error
        if result == PASS_RESULT and cleanup.get("absence_verified"):
            lifecycle.append("passed")
        elif result == PASS_RESULT:
            result = "rehearsal_failed"
    evidence: dict[str, Any] = {
        "schema_version": "emr4.raisa-context-fabric-disposable-postgresql-durability-concurrency-evidence.v1",
        "result": result,
        "evidence_mode": EVIDENCE_MODE,
        "attempt_id": attempt_id,
        "parent": parent_evidence,
        "environment": environment,
        "lifecycle": lifecycle,
        "preconditions": preconditions,
        "scenarios": scenarios,
        "scenario_reconciliation": {
            "expected": 6,
            "observed": len(scenarios),
            "passed": sum(1 for row in scenarios if row.get("passed")),
        },
        "operation_counts": {
            **transaction_counts,
            "participant_retries": 0,
            "docker_containers": 1 if container_id else 0,
            "provider_calls": 0,
            "product_reads": 0,
            "product_commands": 0,
            "external_network_operations": 0,
        },
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if failure is not None:
        evidence["environment"]["failure"] = _bounded_failure(failure)
    evidence["environment"]["elapsed_ms"] = int((time.monotonic() - started) * 1000)
    return evidence


def write_evidence(payload: dict[str, Any]) -> None:
    schema = _json(EVIDENCE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    EVIDENCE_PATH.write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
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
