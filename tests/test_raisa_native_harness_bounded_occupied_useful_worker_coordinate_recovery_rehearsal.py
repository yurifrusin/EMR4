from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import check_in_rollout_runbook as runbook
from scripts import (
    raisa_native_harness_bounded_occupied_useful_worker_coordinate_recovery_rehearsal
    as worker,
)


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR_TERMINAL = (
    ROOT
    / "orchestration/continuity/raisa-native-harness-bounded-occupied-useful-worker-rehearsal/attempt-001/occupied-terminal.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _runner_terminal(*, passed: bool) -> dict[str, object]:
    zero = "0" * 64
    return {
        "schema_version": worker.RUNNER_TERMINAL_SCHEMA_VERSION,
        "status": "completed" if passed else "failed",
        "failure_stage": None if passed else "loader",
        "session_id_sha256": "sha256:" + zero if passed else None,
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "allowed_tool_names": ["edit", "glob", "read"],
        "target_path_sha256": "sha256:" + zero,
        "tool_lifecycle": (
            {
                "input_result_kind": "success",
                "post_execute_decision_kind": "accept",
                "conclusion_request_stage": "pre_execute_after_boundary_accept",
                "authoritative_final_result_kind": "success_concluding",
                "coordinate": "edit_success_accept_concluded",
            }
            if passed
            else None
        ),
        "request_count": 1 if passed else 0,
        "tool_names": ["edit"] if passed else [],
        "tool_result_count": 1 if passed else 0,
        "turn_kind": "completed" if passed else None,
    }


def test_contract_is_canonical_schema_valid_and_exactly_bound() -> None:
    contract = json.loads(worker.CONTRACT_PATH.read_bytes())
    schema = json.loads(worker.CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(contract)
    assert contract == worker.contract_value()
    assert worker.CONTRACT_PATH.read_bytes() == worker.canonical_bytes(contract)
    assert contract["operation_id"] == worker.OPERATION_ID
    assert contract["attempt"]["attempt_id"] == worker.ATTEMPT_ID
    assert contract["source_bindings"]["accepted_coordinate_runner"] == {
        "bytes": 9542,
        "sha256": "33e4ceefc612ac2410c95b71d80ccc42e913976379e8c088f0b8eff966853282",
        "source_commit": "f2d420ce9637081d08ef7d8241b588258d4ddc6a",
    }
    assert contract["occupied_envelope"]["provider_request_limit"] == 1
    assert all(
        contract["occupied_envelope"][name] == 0
        for name in (
            "automatic_retry_limit",
            "manual_retry_limit",
            "resume_limit",
            "fallback_limit",
            "auxiliary_model_call_limit",
        )
    )


def test_attempt_identity_is_disjoint_and_predecessor_is_immutable() -> None:
    assert worker.ATTEMPT_ID.endswith("coordinate-recovery-002")
    assert worker.ATTEMPT_ROOT != Path(
        "C:/Users/sarashera/EMR4-worktrees/deepseek-native-check-in-runbook-worker-001"
    )
    assert _sha256(PREDECESSOR_TERMINAL) == (
        "2c66b7de93b25579347d0e9199437fdc8c7ebf5d21f6d59dc2f73dda602970a5"
    )


def test_runner_is_the_narrow_accepted_coordinate_derivative() -> None:
    target = (worker.ATTEMPT_ROOT / "workspace" / worker.TARGET_RELATIVE_PATH).as_posix()
    payload = worker.runner_source(target)
    result = worker.validate_runner_source(payload, target)
    assert all(result["checks"].values())
    source = payload.decode("utf-8")
    assert source.count("exec.concludeTurn()") == 1
    assert source.index("exec.concludeTurn()") < source.index("return next()")
    assert 'agentCtx.on("tools/result"' in source
    assert "tool_lifecycle: null" in source
    assert "conclusion_marked" not in source
    assert "ariadne.native_harness_useful_worker_runner_terminal.v1" not in source


def test_runner_schema_accepts_success_and_typed_pre_lifecycle_failure() -> None:
    outer = json.loads(worker.TERMINAL_SCHEMA_PATH.read_bytes())
    runner_schema = outer["properties"]["runner"]
    jsonschema.Draft202012Validator(runner_schema).validate(
        _runner_terminal(passed=True)
    )
    jsonschema.Draft202012Validator(runner_schema).validate(
        _runner_terminal(passed=False)
    )


def test_runner_schema_rejects_free_form_coordinate() -> None:
    outer = json.loads(worker.TERMINAL_SCHEMA_PATH.read_bytes())
    runner_schema = outer["properties"]["runner"]
    terminal = _runner_terminal(passed=True)
    lifecycle = terminal["tool_lifecycle"]
    assert isinstance(lifecycle, dict)
    lifecycle["coordinate"] = "looks_good_enough"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(runner_schema).validate(terminal)


def test_only_exact_runbook_candidate_is_admissible() -> None:
    projection = runbook.validate_candidate_bytes(runbook.required_candidate_bytes())
    assert projection["claim"] == "runbook_contract_present_default_off"
    assert projection["value"]["default_posture"]["ordinary_practice_enabled"] is False
    assert projection["value"]["runbook"]["status"] == "prepared_not_authorized"
    mutated = copy.deepcopy(projection["value"])
    mutated["runbook"]["admission"]["ordinary_activation_permitted"] = True
    with pytest.raises(runbook.RunbookValidationError):
        runbook.validate_candidate_bytes(runbook.canonical_bytes(mutated))


def test_provider_free_check_starts_no_worker_or_provider() -> None:
    result = worker.provider_free_check()
    assert result["status"] == "passed"
    assert result["native_process_count"] == 0
    assert result["provider_request_count"] == 0
    assert result["runner"]["checks"]["typed_success_coordinate"] is True


def test_fresh_receipt_has_five_sources_and_serial_lane_ownership() -> None:
    path = (
        ROOT
        / "orchestration/agent_inbox/codex/raisa-native-harness-bounded-occupied-useful-worker-coordinate-recovery-preplanning-receipt.json"
    )
    receipt = json.loads(path.read_bytes())
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert {
        row["lane_id"]: row["disposition"]
        for row in receipt["parallelism_assessment"]["lanes"]
    } == {
        "deepseek_flash": "planned",
        "gemini_verifier": "reserved",
        "native_subagents": "declined",
    }
    assert receipt["parallelism_assessment"]["parallel_work_packages"] == []


def test_attempt_root_is_absent_before_consumption() -> None:
    assert not worker.ATTEMPT_ROOT.exists()
