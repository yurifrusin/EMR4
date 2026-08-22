from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import (
    deepseek_native_harness_provider_free_stock_headless_to_custom_runner_boot_proof
    as proof,
)


def test_frozen_plan_distinguishes_roots_reads_and_hooks() -> None:
    plan = proof.PLAN_PATH.read_text(encoding="utf-8")
    assert "four reads of `presets.roots` and five hook" in plan
    assert "not four distinct roots" in plan
    assert "A pass ends provider-free Harness boot testing" in plan
    assert "There is no automatic or\nmanual retry" in plan


def test_historical_latch_equality_selection_is_exact() -> None:
    selection = (
        proof.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-boot-proof-historical-test-selection.md"
    ).read_text(encoding="utf-8")
    assert "test_active_latch_is_the_exact_in_progress_operation" in selection
    assert "All other predecessor plan, implementation, evidence, package" in selection


def test_expected_observation_is_the_closed_diagnosed_vector() -> None:
    observation = proof.EXPECTED_OBSERVATION
    assert observation["result"] == proof.PASS_RESULT
    assert observation["distinct_preset_root_count"] == 2
    assert observation["preset_root_reads"] == 4
    assert observation["hook_installations"] == 5
    assert observation["structured_coordinate"] == "EFFECTIVE_TOOL_COMPOSITION_PASSED"
    assert observation["old_input_invalid_observed"] is False
    assert observation["runner_request_count"] == 0
    assert observation["stock_app_exit_requested"] is True


def test_adapter_is_closed_and_calls_the_exact_runner() -> None:
    payload = proof.ADAPTER_PATH.read_bytes()
    assert proof.validate_adapter_source(payload) == {
        "bytes": len(payload),
        "sha256": proof.sha256_bytes(payload),
    }
    with pytest.raises(proof.StockHeadlessCustomRunnerBootError, match="adapter_closed_shape_rejected"):
        proof.validate_adapter_source(payload.replace(b"stockExit(0)", b"stockExit(1)"))


def test_patch_pair_adds_probe_only_after_stock_readiness(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    initial, changed = proof.build_patch_pair(
        profile_dir=profile,
        readiness_path=tmp_path / "readiness.jsonl",
        observation_path=tmp_path / "observation.json",
        terminal_path=tmp_path / "terminal.json",
    )
    initial_direct, initial_inserted = proof._patch_rows(initial)
    changed_direct, changed_inserted = proof._patch_rows(changed)
    assert initial_direct == changed_direct
    assert [row["id"] for row in initial_inserted] == [
        "provider-free-accepted-guard-graph-hmr-sentinel"
    ]
    assert [row["id"] for row in changed_inserted] == [
        "provider-free-accepted-guard-graph-hmr-sentinel",
        "provider-free-accepted-guard-graph-boot-probe",
    ]


def test_observation_reader_rejects_counter_drift(tmp_path: Path) -> None:
    path = tmp_path / "observation.json"
    path.write_text(json.dumps(proof.EXPECTED_OBSERVATION), encoding="utf-8")
    assert proof.read_observation(path) == proof.EXPECTED_OBSERVATION
    drift = dict(proof.EXPECTED_OBSERVATION)
    drift["hook_installations"] = 3
    path.write_text(json.dumps(drift), encoding="utf-8")
    assert proof.read_observation(path) is None


def test_terminal_reader_accepts_only_closed_factory_stop(tmp_path: Path) -> None:
    terminal = {
        "schema_version": "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1",
        "status": "failed",
        "failure_stage": "factory",
        "session_id_sha256": None,
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "allowed_tool_names": ["edit", "glob", "read"],
        "conclusion_marked": False,
        "target_path_sha256": "sha256:" + "1" * 64,
        "tool_lifecycle": {
            "input_result_kind": "unobserved",
            "post_execute_decision_kind": "unobserved",
            "conclusion_request_stage": "not_requested",
            "authoritative_final_result_kind": "unobserved",
            "coordinate": None,
        },
        "edit_argument_result": {"pre_dispatch_decision": "not_observed", "coordinate": None},
        "request_count": 0,
        "tool_names": [],
        "tool_result_count": 0,
        "turn_kind": None,
    }
    path = tmp_path / "terminal.json"
    path.write_text(json.dumps(terminal), encoding="utf-8")
    assert proof.read_terminal(path) == terminal
    terminal["request_count"] = 1
    path.write_text(json.dumps(terminal), encoding="utf-8")
    assert proof.read_terminal(path) is None


def test_failure_coordinate_is_exact_and_fail_closed() -> None:
    arguments = {
        "process_started": True,
        "readiness_events": proof.READINESS_EVENTS,
        "hmr_mutation_count": 1,
        "observation": proof.EXPECTED_OBSERVATION,
        "terminal": {"status": "failed"},
        "exit_code": 0,
        "network_attempt_count": 0,
        "network_ledger_valid": True,
        "source_copies_equal": True,
        "canonical_sources_unchanged": True,
        "seed_unchanged": True,
        "process_absent": True,
        "root_absent": True,
    }
    assert proof._failure_coordinate(**arguments) is None
    arguments["observation"] = None
    assert proof._failure_coordinate(**arguments) == "TYPED_OBSERVATION_REJECTED"


def test_contract_and_provider_free_preflight() -> None:
    projection = proof.deterministic_check()
    assert projection["contract"]["expected_observation"] == proof.EXPECTED_OBSERVATION
    assert projection["import_closure"] == {
        "module_count": 5,
        "relative_edge_count": 4,
        "bare_edge_count": 8,
        "builtin_edge_count": 4,
        "bare_target_count": 6,
        "all_targets_present": True,
    }
    assert not proof.EVIDENCE_PATH.exists()
    assert not proof.CONSUMED_PATH.exists()
