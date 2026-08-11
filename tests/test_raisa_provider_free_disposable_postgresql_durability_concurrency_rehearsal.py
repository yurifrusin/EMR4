from __future__ import annotations

import copy
import json
import subprocess
import sys
from concurrent.futures import Future
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
)
CONTRACT = json.loads(
    (BASE / "concurrency-rehearsal-contract.json").read_text(encoding="utf-8")
)
EVIDENCE_SCHEMA = json.loads(
    (BASE / "provider-free-durability-concurrency-evidence.schema.json").read_text(
        encoding="utf-8"
    )
)
DIGEST = "sha256:" + "0" * 64


def _snapshot() -> dict[str, dict[str, Any]]:
    return {
        relation: {"count": 0, "digest": DIGEST}
        for relation in rehearsal.serial.SNAPSHOT_RELATIONS
    }


def _transport(*, success: bool) -> dict[str, Any]:
    return {
        "psql_exit": 0 if success else 3,
        "stdout": {"byte_count": 0, "sha256": DIGEST},
        "stderr": {"byte_count": 0, "sha256": DIGEST},
    }


def _outcome(
    principal: str,
    isolation: str,
    *,
    success: bool = True,
    sqlstate: str | None = None,
    lines: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "outcome": "commit" if success else "rollback",
        "sqlstate": None if success else sqlstate,
        "identity": {
            "session_user": principal,
            "current_user": principal,
            "isolation": isolation,
            "read_only": False,
        },
        "result_lines": lines or [],
        "transport": _transport(success=success),
    }


def _passing_evidence() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    outcome_shapes = {
        "CFD1-C01": (True, None, False, "40001"),
        "CFD1-C02": (True, None, True, None),
        "CFD1-C03": (True, None, True, None),
        "CFD1-C04": (True, None, False, "CF004"),
        "CFD1-C05": (True, None, False, "40001"),
        "CFD1-C06": (False, "P0001", True, None),
    }
    for scenario in CONTRACT["scenarios"]:
        leader_ok, leader_state, contender_ok, contender_state = outcome_shapes[
            scenario["id"]
        ]
        records.append(
            {
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "principal": scenario["principal"],
                "isolation": scenario["isolation"],
                "overlap": {
                    "leader_post_function_hold_observed": True,
                    "leader_wait_event_type": "Timeout",
                    "leader_wait_event": "PgSleep",
                    "leader_observed_within_ms": 25,
                    "contender_lock_wait_observed": True,
                    "contender_wait_event_type": "Lock",
                    "contender_observed_within_ms": 25,
                },
                "leader": _outcome(
                    scenario["principal"],
                    scenario["isolation"],
                    success=leader_ok,
                    sqlstate=leader_state,
                ),
                "contender": _outcome(
                    scenario["principal"],
                    scenario["isolation"],
                    success=contender_ok,
                    sqlstate=contender_state,
                ),
                "post_race": [],
                "before": _snapshot(),
                "after": _snapshot(),
                "readback_checks": {name: True for name in scenario["readback"]},
                "forbidden_effects_absent": {
                    name: True for name in scenario["forbidden_effects"]
                },
                "passed": True,
            }
        )
    readiness = {
        "continuous_success_ms": 3000,
        "last_pg_isready_exit": 0,
        "last_pg_isready_stderr_digest": DIGEST,
        "last_sql_failure_class": "none",
        "last_sql_probe_exit": 0,
        "last_sql_stderr_digest": DIGEST,
        "last_sql_stdout_digest": DIGEST,
        "pg_isready_attempts": 7,
        "pg_isready_successes": 7,
        "sql_probe_attempts": 7,
        "sql_probe_successes": 7,
        "status": "stable",
    }
    return {
        "schema_version": (
            "emr4.raisa-context-fabric-disposable-postgresql-"
            "durability-concurrency-evidence.v1"
        ),
        "result": rehearsal.PASS_RESULT,
        "evidence_mode": rehearsal.EVIDENCE_MODE,
        "attempt_id": "0" * 24,
        "parent": {
            "concurrency_contract_sha256": DIGEST,
            "concurrency_contract_schema_sha256": DIGEST,
            "serial_pass_evidence_sha256": DIGEST,
            "inert_sql_sha256": DIGEST,
            "render_manifest_sha256": DIGEST,
            "statement_count": 424,
        },
        "environment": {
            "docker_client": "resolved_exact_docker_exe",
            "image": {
                "reference": "postgres:16-bookworm",
                "id": DIGEST,
                "pull_attempted": False,
            },
            "readiness": readiness,
            "elapsed_ms": 1,
        },
        "lifecycle": [
            "eight_parent_bindings_verified",
            "container_owned",
            "passwordless_peer_cluster_started",
            "postgres_ready",
            "concurrency_database_ready",
            "artifact_admitted",
            "catalogue_reconciled",
            "fixtures_closed",
            "six_concurrency_scenarios_matched",
            "catalogue_reconciled_after_concurrency",
            "cleanup_verified",
            "passed",
        ],
        "preconditions": [
            {
                "name": name,
                "passed": True,
                "outcome": _outcome("context_lifecycle", "serializable"),
            }
            for name in (
                "register_observer_admission_same",
                "register_observer_admission_divergent",
                "register_observer_coordinator_commit",
                "register_observer_coordinator_rollback",
            )
        ]
        + [
            {
                "name": name,
                "passed": True,
                "outcome": _outcome(
                    "context_observer", "read committed", lines=["PRIMARY"]
                ),
            }
            for name in (
                "admit_coordinator_commit_primary",
                "admit_coordinator_rollback_primary",
            )
        ],
        "scenarios": records,
        "scenario_reconciliation": {"expected": 6, "observed": 6, "passed": 6},
        "operation_counts": {
            "participant_transactions": 12,
            "precondition_transactions": 11,
            "participant_retries": 0,
            "docker_containers": 1,
            "provider_calls": 0,
            "product_reads": 0,
            "product_commands": 0,
            "external_network_operations": 0,
        },
        "cleanup": {
            "status": "cleanup_verified",
            "container_id": "a" * 64,
            "removed": True,
            "absence_verified": True,
        },
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }


def _validator() -> Draft202012Validator:
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    return Draft202012Validator(EVIDENCE_SCHEMA)


def test_current_parent_bindings_contract_and_evidence_schema_validate() -> None:
    contract, serial_contract, prerequisite, manifest, artifact = (
        rehearsal._validate_contract()  # noqa: SLF001
    )
    assert contract == CONTRACT
    assert isinstance(serial_contract, dict)
    assert isinstance(prerequisite, dict)
    assert manifest["statement_count"] == 424
    assert rehearsal._sha256_bytes(artifact) == (  # noqa: SLF001
        "sha256:dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7"
    )
    _validator().validate(_passing_evidence())


def test_participant_renderer_is_one_short_bounded_least_privilege_transaction() -> (
    None
):
    script = rehearsal._participant_script(  # noqa: SLF001
        CONTRACT,
        scenario_id="CFD1-C01",
        participant="a",
        principal="context_lifecycle",
        isolation="serializable",
        statements=["SELECT 1;"],
        hold=True,
    ).decode("utf-8")
    assert script.count("SET SESSION AUTHORIZATION context_lifecycle") == 1
    assert script.count("BEGIN ISOLATION LEVEL SERIALIZABLE") == 1
    assert script.count("COMMIT;") == 1
    assert script.count("pg_catalog.pg_sleep(1500::pg_catalog.numeric / 1000)") == 1
    assert "statement_timeout TO '8000ms'" in script
    assert "lock_timeout TO '5000ms'" in script
    assert "idle_in_transaction_session_timeout TO '8000ms'" in script
    assert not any(
        forbidden in script.upper()
        for forbidden in ("SET ROLE", "SAVEPOINT", "PREPARE TRANSACTION")
    )


def test_participant_renderer_rejects_unfrozen_coordinates() -> None:
    with pytest.raises(rehearsal.ConcurrencyFailure, match="participant_coordinate"):
        rehearsal._participant_script(  # noqa: SLF001
            CONTRACT,
            scenario_id="CFD1-C07",
            participant="a",
            principal="context_lifecycle",
            isolation="serializable",
            statements=["SELECT 1;"],
        )
    with pytest.raises(rehearsal.ConcurrencyFailure, match="principal"):
        rehearsal._participant_script(  # noqa: SLF001
            CONTRACT,
            scenario_id="CFD1-C01",
            participant="a",
            principal="postgres",
            isolation="serializable",
            statements=["SELECT 1;"],
        )


def test_transaction_counter_records_started_pair_and_precondition_calls() -> None:
    counts = {"participant_transactions": 0, "precondition_transactions": 0}

    def base_runner(
        _argv: list[str], _stdin: bytes | None, _timeout: int, _cap: int
    ) -> rehearsal.serial.parent.ProcessResult:
        return rehearsal.serial.parent.ProcessResult(0, b"", b"")

    runner = rehearsal._counting_runner(base_runner, counts)  # noqa: SLF001
    runner([], b"SET application_name TO 'emr4_cf_d1_c01_a';\n", 1, 1)
    runner([], b"SET application_name TO 'emr4_cf_d1_c01_b';\n", 1, 1)
    runner([], b"SET application_name TO 'emr4_cf_d1_c01_r';\n", 1, 1)
    runner([], b"SELECT 1;\n", 1, 1)
    assert counts == {
        "participant_transactions": 2,
        "precondition_transactions": 1,
    }


def test_wait_observation_accepts_only_the_exact_classified_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    states = iter(
        [
            {"count": 1, "wait_event_type": "Client", "wait_event": "ClientRead"},
            {"count": 1, "wait_event_type": "Lock", "wait_event": "transactionid"},
        ]
    )
    monkeypatch.setattr(rehearsal, "_activity_state", lambda *args: next(states))
    monkeypatch.setattr(rehearsal.time, "sleep", lambda _seconds: None)
    future: Future[rehearsal.serial.parent.ProcessResult] = Future()
    elapsed = rehearsal._wait_for_state(  # noqa: SLF001
        lambda *_args: rehearsal.serial.parent.ProcessResult(0, b"", b""),
        "docker.exe",
        "a" * 64,
        rehearsal._profile(),  # noqa: SLF001
        CONTRACT,
        "emr4_cf_d1_c01_b",
        event_type="Lock",
        event=None,
        future=future,
    )
    assert 0 <= elapsed <= 1000


def test_wait_observation_rejects_timing_without_a_live_participant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    future: Future[rehearsal.serial.parent.ProcessResult] = Future()
    future.set_result(rehearsal.serial.parent.ProcessResult(0, b"", b""))
    monkeypatch.setattr(
        rehearsal,
        "_activity_state",
        lambda *args: {"count": 1, "wait_event_type": "Lock", "wait_event": "tuple"},
    )
    with pytest.raises(
        rehearsal.ConcurrencyFailure, match="participant_ended_before_state"
    ):
        rehearsal._wait_for_state(  # noqa: SLF001
            lambda *_args: rehearsal.serial.parent.ProcessResult(0, b"", b""),
            "docker.exe",
            "a" * 64,
            rehearsal._profile(),  # noqa: SLF001
            CONTRACT,
            "emr4_cf_d1_c01_b",
            event_type="Lock",
            event=None,
            future=future,
        )


def test_result_release_is_closed_and_transport_is_digest_only() -> None:
    identity = json.dumps(
        {
            "expected_principal": "context_observer",
            "session_user": "context_observer",
            "current_user": "context_observer",
            "isolation": "read committed",
            "read_only": False,
        }
    ).encode("utf-8")
    result = rehearsal.serial.parent.ProcessResult(
        0,
        identity + b"\nPRIMARY\npatient-shaped prose\n",
        b"opaque server prose",
    )
    released = rehearsal._expect_success(  # noqa: SLF001
        result,
        coordinate="CFD1-C03.leader",
        principal="context_observer",
        isolation="read committed",
        expected_lines=["PRIMARY"],
    )
    assert released["result_lines"] == ["PRIMARY"]
    assert set(released["transport"]) == {"psql_exit", "stdout", "stderr"}
    assert "patient" not in json.dumps(released)
    assert "opaque" not in json.dumps(released)


@pytest.mark.parametrize("scenario_id", [f"CFD1-C0{i}" for i in range(1, 7)])
def test_exact_snapshot_effects_and_inert_replay(scenario_id: str) -> None:
    before = _snapshot()
    after = copy.deepcopy(before)
    for relation, count_delta in rehearsal.EXPECTED_CHANGED_RELATIONS[
        scenario_id
    ].items():
        after[relation]["count"] += count_delta
        after[relation]["digest"] = "sha256:" + "1" * 64
    rehearsal._assert_snapshot_effect(scenario_id, before, after)  # noqa: SLF001
    rehearsal._assert_replay_inert(after, copy.deepcopy(after))  # noqa: SLF001


def test_snapshot_effect_rejects_an_unlisted_relation_change() -> None:
    before = _snapshot()
    after = copy.deepcopy(before)
    after["public.appointments"]["digest"] = "sha256:" + "1" * 64
    with pytest.raises(rehearsal.ConcurrencyFailure, match="digest_delta"):
        rehearsal._assert_snapshot_effect("CFD1-C01", before, after)  # noqa: SLF001


def _mutate_extra_top_level(candidate: dict[str, Any]) -> None:
    candidate["raw_query"] = "SELECT *"


def _mutate_scenario_order(candidate: dict[str, Any]) -> None:
    candidate["scenarios"][0], candidate["scenarios"][1] = (
        candidate["scenarios"][1],
        candidate["scenarios"][0],
    )


def _mutate_overlap(candidate: dict[str, Any]) -> None:
    candidate["scenarios"][0]["overlap"]["contender_lock_wait_observed"] = False


def _mutate_pid(candidate: dict[str, Any]) -> None:
    candidate["scenarios"][0]["overlap"]["backend_pid"] = 1234


def _mutate_retry(candidate: dict[str, Any]) -> None:
    candidate["operation_counts"]["participant_retries"] = 1


def _mutate_provider(candidate: dict[str, Any]) -> None:
    candidate["operation_counts"]["provider_calls"] = 1


def _mutate_cleanup(candidate: dict[str, Any]) -> None:
    candidate["cleanup"]["absence_verified"] = False


def _mutate_raw_transport(candidate: dict[str, Any]) -> None:
    candidate["scenarios"][0]["leader"]["transport"]["stderr"]["text"] = "raw"


HOSTILE_MUTATIONS: tuple[Callable[[dict[str, Any]], None], ...] = (
    _mutate_extra_top_level,
    _mutate_scenario_order,
    _mutate_overlap,
    _mutate_pid,
    _mutate_retry,
    _mutate_provider,
    _mutate_cleanup,
    _mutate_raw_transport,
)


@pytest.mark.parametrize("mutate", HOSTILE_MUTATIONS, ids=lambda fn: fn.__name__)
def test_pass_evidence_hostile_mutations_fail_closed(
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    candidate = copy.deepcopy(_passing_evidence())
    mutate(candidate)
    with pytest.raises(ValidationError):
        _validator().validate(candidate)


def test_failure_evidence_remains_closed_without_runtime_claim() -> None:
    evidence = _passing_evidence()
    evidence.update(
        {
            "result": "environment_unavailable",
            "parent": {},
            "lifecycle": [],
            "preconditions": [],
            "scenarios": [],
            "scenario_reconciliation": {"expected": 6, "observed": 0, "passed": 0},
            "cleanup": {
                "status": "not_needed",
                "removed": False,
                "absence_verified": False,
            },
        }
    )
    evidence["environment"] = {
        "docker_client": "unresolved",
        "image": "uninspected",
        "failure": {"stage": "environment", "code": "docker_client_missing"},
        "elapsed_ms": 1,
    }
    evidence["operation_counts"]["docker_containers"] = 0
    _validator().validate(evidence)


def test_source_and_evidence_surface_keep_forbidden_authorities_absent() -> None:
    source = (ROOT / "scripts" / (Path(rehearsal.__file__).name)).read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "google.cloud",
        "vertexai",
        "requests.",
        "subprocess.run(",
        "shell=True",
        "CREATE EXTENSION dblink",
    ):
        assert forbidden not in source
    assert rehearsal.EVIDENCE_PATH.name == (
        "provider-free-durability-concurrency-evidence-attempt-003.json"
    )


def test_direct_script_entrypoint_imports_before_rejecting_caller_input() -> None:
    completed = subprocess.run(  # noqa: S603
        [sys.executable, str(Path(rehearsal.__file__)), "--forbidden-probe"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=15,
    )
    assert completed.returncode == 2
    assert completed.stdout == b""
    assert completed.stderr.decode("utf-8").strip() == (
        "This fixed-path harness accepts no arguments."
    )
    assert not (
        BASE / "provider-free-durability-concurrency-evidence-attempt-003.json"
    ).exists()


def test_result_mismatch_failure_releases_only_closed_diagnostic_fields() -> None:
    identity = json.dumps(
        {
            "expected_principal": "context_lifecycle",
            "session_user": "context_lifecycle",
            "current_user": "context_lifecycle",
            "isolation": "serializable",
            "read_only": False,
        }
    ).encode("utf-8")
    result = rehearsal.serial.parent.ProcessResult(
        0,
        identity + b"\n1\nraw prose that must not leave\n",
        b"raw server detail",
    )
    with pytest.raises(rehearsal.ConcurrencyFailure) as raised:
        rehearsal._expect_success(  # noqa: SLF001
            result,
            coordinate="CFD1-C01.leader",
            principal="context_lifecycle",
            isolation="serializable",
            expected_lines=[],
        )
    bounded = rehearsal._bounded_failure(raised.value)  # noqa: SLF001
    assert bounded == {
        "stage": "scenario",
        "code": "result_marker",
        "coordinate": "CFD1-C01.leader",
        "principal": "context_lifecycle",
        "isolation": "serializable",
        "expected_result_lines": [],
        "observed_result_lines": ["1"],
        "observed_result_count": 1,
    }
    failure = _passing_evidence()
    failure["result"] = "rehearsal_failed"
    failure["environment"]["failure"] = bounded
    _validator().validate(failure)
    assert "raw prose" not in json.dumps(failure)
    assert "raw server" not in json.dumps(failure)
