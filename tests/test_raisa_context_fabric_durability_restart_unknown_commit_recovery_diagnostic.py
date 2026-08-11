from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
RECOVERY_CONTRACT = json.loads(
    rehearsal.RECOVERY_CONTRACT_PATH.read_text(encoding="utf-8")
)
DIAGNOSTIC_SCHEMA = json.loads(
    rehearsal.DIAGNOSTIC_EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8")
)
DIGEST = "sha256:" + "0" * 64


def _passing_diagnostic() -> dict[str, Any]:
    preconditions = [
        *(f"register_observer_r0{number}" for number in range(1, 5)),
        "produce_position_one",
        "produce_position_two",
        *(f"admit_observer_r0{number}_position_1" for number in range(1, 5)),
    ]
    return {
        "schema_version": "emr4.raisa-context-fabric-disposable-postgresql-durability-restart-unknown-commit-recovery-diagnostic-evidence.v1",
        "result": rehearsal.DIAGNOSTIC_PASS_RESULT,
        "evidence_mode": rehearsal.DIAGNOSTIC_EVIDENCE_MODE,
        "attempt_id": "0" * 24,
        "parent": {
            "source_head": "0" * 40,
            "contract_sha256": rehearsal.EXPECTED_CONTRACT_SHA256,
            "recovery_contract_sha256": rehearsal.EXPECTED_RECOVERY_CONTRACT_SHA256,
            "artifact_sha256": DIGEST,
            "manifest_sha256": DIGEST,
            "statement_count": 424,
        },
        "environment": {
            "docker_client": "resolved_exact_docker_exe",
            "image": {
                "reference": "postgres:16-bookworm",
                "identity_digest": DIGEST,
                "pull_attempted": False,
            },
            "container": {
                "identity_digest": DIGEST,
                "network_mode": "none",
                "published_ports": 0,
                "bind_mounts": 0,
                "named_volumes": 0,
                "anonymous_volumes": 0,
                "declared_volume_shield": "tmpfs",
                "actual_pgdata_storage": "owned_container_writable_layer",
            },
            "durability": {
                "cluster_identity_digest": DIGEST,
                "postgresql_major": 16,
                "fsync": "on",
                "synchronous_commit": "on",
                "full_page_writes": "on",
                "data_checksums": "on",
            },
            "elapsed_ms": 100,
        },
        "lifecycle": [
            "eight_parent_bindings_verified",
            "container_owned_and_storage_closed",
            "postgres16_artifact_and_durability_reconciled",
            "four_disjoint_generations_prepared",
            "no_crash_r01_apply_anchor_matched",
            "catalogue_reconciled",
            "cleanup_verified",
            "passed",
        ],
        "preconditions": preconditions,
        "terminal_observations": [
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
        ],
        "operation_counters": {
            "sigkill": 0,
            "restart": 0,
            "participant_retry": 0,
            "provider_calls": 0,
            "product_reads": 0,
            "product_commands": 0,
            "external_network_operations": 0,
        },
        "cleanup": {
            "status": "cleanup_verified",
            "removed": True,
            "absence_verified": True,
        },
        "claim_boundary": rehearsal.DIAGNOSTIC_CLAIM_BOUNDARY,
    }


def test_recovery_contract_and_diagnostic_schema_are_closed() -> None:
    contract = rehearsal._validate_recovery_contract()
    Draft202012Validator.check_schema(DIAGNOSTIC_SCHEMA)
    assert contract == RECOVERY_CONTRACT
    assert rehearsal._canonical_sha(contract) == (
        rehearsal.EXPECTED_RECOVERY_CONTRACT_SHA256
    )
    assert len(contract["terminal_coordinates"]) == 27
    assert contract["diagnostic_profile"]["sigkill_count"] == 0
    assert contract["diagnostic_profile"]["restart_count"] == 0
    assert rehearsal.DIAGNOSTIC_EVIDENCE_PATH.name.endswith("attempt-002.json")


def test_second_anchor_uses_current_lifecycle_revision_one() -> None:
    sql = rehearsal.serial.inert_renderer.SQL_INERT_PATH.read_text(encoding="utf-8")
    assert "checkpoint.lifecycle_revision + 1::pg_catalog.int8" in sql
    assert "cf_arg_lifecycle_revision = checkpoint.lifecycle_revision" in sql
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    anchor_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_anchor_statements"
    ]
    assert len(anchor_calls) == 5
    assert all(
        isinstance(call.args[2], ast.Constant) and call.args[2].value == 1
        for call in anchor_calls
    )
    with pytest.raises(rehearsal.RestartFailure) as raised:
        rehearsal._anchor_statements({}, "observer_r01", 2)
    assert (raised.value.stage, raised.value.code) == ("render", "anchor_revision")


def test_every_participant_call_has_one_closed_coordinate() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_execute"
    ]
    assert len(calls) == 22
    coordinates = [
        next(
            (keyword.value for keyword in call.keywords if keyword.arg == "coordinate"),
            None,
        )
        for call in calls
    ]
    assert all(value is not None for value in coordinates)
    literal_coordinates = {
        value.value
        for value in coordinates
        if isinstance(value, ast.Constant) and isinstance(value.value, str)
    }
    assert literal_coordinates == set(RECOVERY_CONTRACT["terminal_coordinates"][10:])


def test_terminal_failure_is_coordinate_specific_and_output_minimized() -> None:
    result = rehearsal.serial.parent.ProcessResult(
        returncode=0,
        stdout=b"RECEIPT_REPLAYED\nraw-not-admitted\n",
        stderr=b"sensitive raw error",
    )
    with pytest.raises(rehearsal.TerminalFailure) as raised:
        rehearsal._expect_success(
            result,
            coordinate="cfd2_r01_apply_position_1",
            principal="context_coordinator",
            isolation="serializable",
            expected_lines=["RECEIPT_APPLIED"],
        )
    assert raised.value.stage == "cfd2_r01_apply_position_1"
    assert raised.value.terminal_evidence == {
        "coordinate": "cfd2_r01_apply_position_1",
        "code": "unexpected_terminal_success",
        "returncode_class": "zero",
        "sqlstate": None,
        "result_lines": ["RECEIPT_REPLAYED"],
    }
    assert "raw-not-admitted" not in json.dumps(raised.value.terminal_evidence)
    assert "sensitive raw error" not in json.dumps(raised.value.terminal_evidence)


def test_unknown_coordinate_fails_before_participant_call() -> None:
    with pytest.raises(rehearsal.RestartFailure) as raised:
        rehearsal._assert_terminal_coordinate("cfd2_unknown", RECOVERY_CONTRACT)
    assert (raised.value.stage, raised.value.code) == (
        "terminal_coordinate",
        "not_allowlisted",
    )


def test_recovery_contract_digest_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    candidate = copy.deepcopy(RECOVERY_CONTRACT)
    candidate["planning_baseline_head"] = "0" * 40
    path = tmp_path / "mutated-recovery-contract.json"
    path.write_text(json.dumps(candidate), encoding="utf-8")
    monkeypatch.setattr(rehearsal, "RECOVERY_CONTRACT_PATH", path)
    with pytest.raises(rehearsal.RestartFailure) as raised:
        rehearsal._validate_recovery_contract()
    assert (raised.value.stage, raised.value.code) == (
        "recovery_contract",
        "digest_mismatch",
    )


def test_no_crash_sequence_stops_before_anchor_after_apply_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(rehearsal, "_recovery_packet", lambda *args: {"packet": 0})
    monkeypatch.setattr(rehearsal, "_coordinator_statements", lambda *args: [])

    def fail_execute(*args: Any, coordinate: str, **kwargs: Any) -> dict[str, Any]:
        calls.append(coordinate)
        raise rehearsal.RestartFailure(coordinate, "stopped")

    monkeypatch.setattr(rehearsal, "_execute", fail_execute)
    with pytest.raises(rehearsal.RestartFailure):
        rehearsal._run_no_crash_first_sequence(
            lambda *args: None,
            "docker.exe",
            "a" * 64,
            {},
            {},
            {},
        )
    assert calls == ["cfd2_r01_apply_position_1"]


def test_no_crash_sequence_runs_exact_apply_then_anchor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    packets = iter(({"packet": 0}, {"packet": 1}, {"packet": 2}))
    monkeypatch.setattr(rehearsal, "_recovery_packet", lambda *args: next(packets))
    monkeypatch.setattr(rehearsal, "_coordinator_statements", lambda *args: [])
    monkeypatch.setattr(rehearsal, "_anchor_statements", lambda *args: [])
    monkeypatch.setattr(rehearsal, "_assert_transition_delta", lambda *args: None)
    monkeypatch.setattr(rehearsal, "_assert_anchor_delta", lambda *args: None)

    def pass_execute(*args: Any, coordinate: str, **kwargs: Any) -> dict[str, Any]:
        calls.append(coordinate)
        return {
            "outcome": "commit",
            "sqlstate": None,
            "result_lines": ["RECEIPT_APPLIED"] if len(calls) == 1 else ["1"],
            "identity": {},
        }

    monkeypatch.setattr(rehearsal, "_execute", pass_execute)
    observations = rehearsal._run_no_crash_first_sequence(
        lambda *args: None,
        "docker.exe",
        "a" * 64,
        {},
        {},
        {},
    )
    assert calls == [
        "cfd2_r01_apply_position_1",
        "cfd2_r01_append_anchor_2",
    ]
    assert [row["coordinate"] for row in observations] == calls


def test_passing_diagnostic_validates_as_one_minimized_document() -> None:
    payload = _passing_diagnostic()
    rehearsal.validate_diagnostic_evidence(payload)
    Draft202012Validator(DIAGNOSTIC_SCHEMA).validate(payload)


def test_immutable_failed_diagnostic_attempt_one_remains_admissible() -> None:
    path = rehearsal.BASE / (
        "provider-free-durability-restart-unknown-commit-recovery-"
        "diagnostic-evidence-attempt-001.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result"] == "rehearsal_failed"
    assert payload["terminal_failure"]["coordinate"] == ("cfd2_r01_append_anchor_2")
    rehearsal.validate_diagnostic_evidence(payload)
    Draft202012Validator(DIAGNOSTIC_SCHEMA).validate(payload)


Mutation = Callable[[dict[str, Any]], None]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["operation_counters"].update(sigkill=1),
        lambda value: value["operation_counters"].update(restart=1),
        lambda value: value["operation_counters"].update(participant_retry=1),
        lambda value: value["operation_counters"].update(provider_calls=1),
        lambda value: value["parent"].update(contract_sha256=DIGEST),
        lambda value: value["lifecycle"].reverse(),
        lambda value: value["terminal_observations"].reverse(),
        lambda value: value["terminal_observations"][0].update(
            result_lines=["PRIMARY"]
        ),
        lambda value: value["terminal_observations"][0].update(
            coordinate="cfd2_r01_replay_position_1"
        ),
        lambda value: value["terminal_observations"][0].update(stdout="forbidden"),
        lambda value: value["cleanup"].update(absence_verified=False),
        lambda value: value.update(claim_boundary="restart_proved"),
        lambda value: value.update(failure={"stage": "scenario", "code": "unexpected"}),
    ],
)
def test_hostile_diagnostic_mutations_fail_closed(mutate: Mutation) -> None:
    candidate = copy.deepcopy(_passing_diagnostic())
    mutate(candidate)
    with pytest.raises((rehearsal.RestartFailure, ValidationError)):
        rehearsal.validate_diagnostic_evidence(candidate)
        Draft202012Validator(DIAGNOSTIC_SCHEMA).validate(candidate)


def test_diagnostic_wrapper_has_no_argument_or_runtime_broadening() -> None:
    wrapper = (
        ROOT
        / "scripts/raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py"
    ).read_text(encoding="utf-8")
    assert "run_recovery_diagnostic" in wrapper
    assert "write_diagnostic_evidence" in wrapper
    for forbidden in (
        "_restart_same_cluster",
        "_kill_argv",
        "docker container kill",
        "--network=bridge",
        "--pull=always",
        "google.genai",
        "vertexai",
        "requests.",
    ):
        assert forbidden not in wrapper
