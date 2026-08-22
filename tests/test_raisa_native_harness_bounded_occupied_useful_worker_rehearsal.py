from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from orchestration_harness import check_in_rollout_runbook as runbook
from scripts import raisa_native_harness_bounded_occupied_useful_worker_rehearsal as worker


ROOT = Path(__file__).resolve().parents[1]


def test_baseline_is_one_closed_empty_runbook_slot() -> None:
    value = runbook.parse_candidate_bytes(runbook.baseline_bytes())
    assert value == runbook.BASELINE_CANDIDATE
    assert value["runbook"] is None
    assert value["default_posture"] == {
        "ordinary_practice_enabled": False,
        "activation_authority": False,
        "authored_synthetic_allowlist_unchanged": True,
        "active_ordinary_practice_records": 0,
    }


def test_required_candidate_is_exact_closed_form() -> None:
    projection = runbook.validate_candidate_bytes(runbook.required_candidate_bytes())
    assert projection["value"] == runbook.REQUIRED_CANDIDATE
    assert projection["ordinary_practice_enabled"] is False
    assert projection["activation_authority"] is False
    assert projection["claim"] == "runbook_contract_present_default_off"
    assert projection["canonical_bytes"] == runbook.required_candidate_bytes()


def test_json_schema_is_the_same_closed_form() -> None:
    schema = json.loads(worker.CANDIDATE_SCHEMA_PATH.read_bytes())
    assert schema["const"] == runbook.REQUIRED_CANDIDATE
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(runbook.REQUIRED_CANDIDATE)


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("default_posture", "ordinary_practice_enabled"), True),
        (("default_posture", "activation_authority"), True),
        (("runbook", "status"), "active"),
        (("runbook", "admission", "feature_flag_change_permitted"), True),
        (("runbook", "kill_switch", "default_state"), "clear"),
        (("runbook", "rollback", "unknown_commit_policy"), "retry"),
        (("runbook", "audit", "non_phi_only"), False),
        (("runbook", "effects", "protected_ref_changed"), True),
        (("runbook", "claim"), "ordinary_practice_ready"),
    ],
)
def test_every_authority_expansion_fails_closed(
    path: tuple[str, ...], replacement: object
) -> None:
    value = copy.deepcopy(runbook.REQUIRED_CANDIDATE)
    cursor: dict[str, object] = value
    for key in path[:-1]:
        cursor = cursor[key]  # type: ignore[assignment,index]
    cursor[path[-1]] = replacement
    with pytest.raises(runbook.RunbookValidationError, match="closed_form_mismatch"):
        runbook.validate_candidate_bytes(runbook.canonical_bytes(value))


def test_unknown_key_and_stage_fail_closed() -> None:
    unknown = copy.deepcopy(runbook.REQUIRED_CANDIDATE)
    unknown["runbook"]["extra"] = True
    active_stage = copy.deepcopy(runbook.REQUIRED_CANDIDATE)
    active_stage["runbook"]["rollout_stages"].append("active")
    for value in (unknown, active_stage):
        with pytest.raises(runbook.RunbookValidationError, match="closed_form_mismatch"):
            runbook.validate_candidate_bytes(runbook.canonical_bytes(value))


def test_duplicate_keys_crlf_invalid_utf8_and_oversize_fail_closed() -> None:
    with pytest.raises(runbook.RunbookValidationError, match="duplicate_key"):
        runbook.validate_candidate_bytes(b'{"schema_version":"x","schema_version":"y"}\n')
    with pytest.raises(runbook.RunbookValidationError, match="newline_invalid"):
        runbook.validate_candidate_bytes(runbook.required_candidate_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(runbook.RunbookValidationError, match="utf8_invalid"):
        runbook.validate_candidate_bytes(b"\xff")
    with pytest.raises(runbook.RunbookValidationError, match="size_invalid"):
        runbook.validate_candidate_bytes(b"{" + b" " * runbook.MAX_CANDIDATE_BYTES + b"}")


def test_prompt_is_one_literal_member_replacement() -> None:
    target = "C:/disposable/workspace/" + runbook.TARGET_RELATIVE_PATH
    prompt = worker.task_text(target)
    assert prompt.count(target) == 1
    assert prompt.count('"runbook": null,') == 1
    assert prompt.count('"runbook": {') == 1
    assert "exactly one model-requested tool call" in prompt
    assert "Do not call read or glob" in prompt
    replaced = runbook.baseline_bytes().decode().replace(
        '  "runbook": null,', worker._runbook_member_text()
    )
    assert runbook.validate_candidate_bytes(replaced.encode())["value"] == runbook.REQUIRED_CANDIDATE


def test_runner_has_one_request_one_edit_and_accepted_composition() -> None:
    target = "C:/disposable/workspace/" + runbook.TARGET_RELATIVE_PATH
    payload = worker.runner_source(target)
    reading = worker.validate_runner_source(payload, target)
    assert all(reading["checks"].values())
    source = payload.decode()
    assert source.count("await agents.create(") == 1
    assert source.count("agent.followup(") == 1
    assert source.count("exec.concludeTurn()") == 1
    assert "assertEffectiveToolComposition(agentCtx, presets," in source
    assert "PUBLICATION_STOP" not in source
    assert "error.message" not in source
    assert "error.stack" not in source


def test_accepted_complete_guard_graph_is_reused_exactly() -> None:
    sources, inventory = worker.accepted_complete.accepted_module_sources()
    assert inventory == worker.accepted_complete.EXPECTED_SOURCE_INVENTORY
    assert sources["derived_guard"].count(b"presetService") > 0
    assert b"preset-mount-sanitizer-runner-bridge.mjs" in sources["derived_guard"]


def test_disposable_profile_materializes_the_exact_guard_graph(tmp_path: Path) -> None:
    root = tmp_path / "attempt"
    target = root / "workspace" / runbook.TARGET_RELATIVE_PATH
    target.parent.mkdir(parents=True)
    target.write_bytes(runbook.baseline_bytes())
    profile = worker._materialize_profile(root, target.resolve().as_posix())
    accepted, inventory = worker.accepted_complete.accepted_module_sources()
    proof = root / "installation" / "proof"
    assert profile["guard_sha256"] == inventory["derived_guard"]["sha256"]
    assert profile["bridge_sha256"] == inventory["derived_bridge"]["sha256"]
    assert profile["sanitizer_sha256"] == inventory["accepted_sanitizer"]["sha256"]
    assert (proof / "effective-tool-guard.mjs").read_bytes() == accepted["derived_guard"]
    assert (proof / "preset-mount-sanitizer-runner-bridge.mjs").read_bytes() == accepted["derived_bridge"]
    assert worker.validate_runner_source(
        (proof / "runner.mjs").read_bytes(), target.resolve().as_posix()
    )["sha256"] == profile["runner_sha256"]
    initial = worker.accepted_worker.profile_patch(root, 43123, changed=False)
    changed = worker.accepted_worker.profile_patch(root, 43123, changed=True)
    assert worker.accepted_worker.validate_profile_patch(initial, changed=False)[
        "runner_presence_exact"
    ]
    assert worker.accepted_worker.validate_profile_patch(changed, changed=True)[
        "runner_presence_exact"
    ]


def test_contract_is_exact_and_all_effects_closed() -> None:
    contract = worker.validate_contract()
    assert contract == worker.contract_value()
    assert contract["work_package"]["worker_owned_paths"] == [runbook.TARGET_RELATIVE_PATH]
    assert contract["occupied_envelope"]["provider_request_limit"] == 1
    assert contract["occupied_envelope"]["automatic_retry_limit"] == 0
    assert all(value is False for value in contract["protected_boundaries"].values())


def test_plan_freezes_api_spine_and_parallelism_boundaries() -> None:
    text = worker.PLAN_PATH.read_text(encoding="utf-8")
    assert "Timestamp:" in text and "Australia/Brisbane" in text
    assert runbook.TARGET_RELATIVE_PATH in text
    assert "DeepSeek V4 Flash/high: **planned**" in text
    assert "Gemini: **declined**" in text
    assert "Native subagents: **declined**" in text
    assert "declarative control manifest" in text
    assert "No ordinary-practice enablement" in text
    assert "git add ." in text and "git add -A" in text


def test_provider_free_check_starts_no_native_or_provider_process() -> None:
    result = worker.provider_free_check()
    assert result["status"] == "passed"
    assert result["native_process_count"] == 0
    assert result["provider_request_count"] == 0
    assert result["candidate"]["claim"] == "runbook_contract_present_default_off"


def test_validation_runner_receipt_resolves_full_reviewed_git_object() -> None:
    receipt = (
        ROOT
        / "orchestration/agent_inbox/codex/raisa-native-harness-bounded-occupied-useful-worker-deterministic-admission-receipt.json"
    )
    source = worker._review_candidate_source(receipt)
    assert len(source) == 40
    assert subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, "HEAD"],
        cwd=ROOT,
        check=False,
    ).returncode == 0


def test_validation_runner_receipt_rejects_changed_source_digest(tmp_path: Path) -> None:
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/raisa-native-harness-bounded-occupied-useful-worker-deterministic-admission-receipt.json"
        ).read_bytes()
    )
    source_result = next(row for row in receipt["results"] if row["id"] == "C02")
    source_result["stdout_sha256"] = "0" * 64
    changed = tmp_path / "changed-receipt.json"
    changed.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(worker.UsefulWorkerError, match="deterministic_admission_receipt_invalid"):
        worker._review_candidate_source(changed)


def test_terminal_schema_accepts_only_bounded_success() -> None:
    zero_hash = "0" * 64
    terminal = {
        "schema_version": worker.TERMINAL_SCHEMA_VERSION,
        "operation_id": worker.OPERATION_ID,
        "attempt_id": worker.ATTEMPT_ID,
        "candidate_source": "1" * 40,
        "result": "pass",
        "terminal_class": "useful_worker_pass",
        "failure_coordinate": None,
        "process": {
            "native_process_count": 1,
            "harness_exit_code": 0,
            "wall_clock_ms": 1,
            "stdout_bytes": 0,
            "stdout_sha256": zero_hash,
            "stderr_bytes": 0,
            "stderr_sha256": zero_hash,
            "broker_stderr_bytes": 0,
            "broker_stderr_sha256": zero_hash,
        },
        "hmr_events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "runner": {
            "schema_version": worker.RUNNER_TERMINAL_SCHEMA_VERSION,
            "status": "completed",
            "failure_stage": None,
            "session_id_sha256": "sha256:" + zero_hash,
            "provider": "deepseek-official",
            "model": "deepseek-v4-flash",
            "reasoning_effort": "high",
            "allowed_tool_names": ["edit", "glob", "read"],
            "conclusion_marked": True,
            "target_path_sha256": "sha256:" + zero_hash,
            "request_count": 1,
            "tool_names": ["edit"],
            "tool_result_count": 1,
            "turn_kind": "completed",
        },
        "broker": {
            "provider_call_started": 1,
            "provider_call_completed": 1,
            "provider_call_failed": 0,
            "request_rejected": 0,
        },
        "candidate": {
            "changed_paths": [runbook.TARGET_RELATIVE_PATH],
            "admitted": True,
            "canonical_byte_count": len(runbook.required_candidate_bytes()),
            "canonical_sha256": runbook.sha256_bytes(runbook.required_candidate_bytes()),
            "retained_path": worker.CANDIDATE_OUTPUT_PATH.relative_to(ROOT).as_posix(),
            "claim": "runbook_contract_present_default_off",
        },
        "automatic_retry_count": 0,
        "manual_retry_count": 0,
        "resume_count": 0,
        "fallback_count": 0,
        "auxiliary_model_call_count": 0,
        "cleanup": {
            "harness_absent": True,
            "broker_absent": True,
            "attempt_root_absent": True,
            "raw_logs_retained": False,
            "raw_session_retained": False,
            "raw_prompt_response_reasoning_retained": False,
            "provider_key_present_in_worker_environment": False,
        },
    }
    schema = json.loads(worker.TERMINAL_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(terminal)
    mutated = copy.deepcopy(terminal)
    mutated["automatic_retry_count"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(mutated)


def test_fresh_ariadne_receipt_names_all_five_sources_and_parallel_lanes() -> None:
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/raisa-native-harness-bounded-occupied-useful-worker-rehearsal-preplanning-corrected-receipt.json"
        ).read_bytes()
    )
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
        "gemini_verifier": "declined",
        "native_subagents": "declined",
    }


def test_broker_source_parses_without_starting_it() -> None:
    completed = subprocess.run(
        ["node", "--check", str(worker.BROKER_PATH)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
