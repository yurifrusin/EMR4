from __future__ import annotations

import json
from pathlib import Path

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_source_coordinate_reconciliation_rehearsal as subject,
)


def _load(path: Path):
    return json.loads(path.read_bytes())


def test_evidence_binds_exact_candidate_and_terminal() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["candidate_source"] == (
        "2c0e24e6b59263129ec59e948f17a18203015b67"
    )
    assert evidence["result"] == "pass"
    assert evidence["accepted_terminal"] == {
        "candidate_source": "c66eb82cccd64961f0d99bf9f67803e1a69ebd8a",
        "result": "preset_composition_failure_attributed",
        "last_admitted_stage": "private_identity_admitted",
        "safe_guard_coordinate": "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
        "safe_guard_detail": None,
        "raw_runtime_detail_retained": False,
    }


def test_eight_source_and_manifest_bindings_pass() -> None:
    bindings = _load(subject.EVIDENCE_PATH)["source_bindings"]
    assert len(bindings) == 8
    assert all(row["passed"] for row in bindings)
    assert {row["version"] for row in bindings} == {"0.1.0-rc.7"}
    assert len({row["path"] for row in bindings}) == 8


def test_plugin_prerequisites_are_declared_without_runtime_claim() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["plugin_prerequisites"] == {
        "preset_rows": [
            "@deepseek-ai/dsh-tool-fs",
            "@deepseek-ai/dsh-tool-fs-search",
        ],
        "tool_fs_inject": ["tools", "fs", "systemPrompt"],
        "tool_fs_search_inject": ["tools", "systemPrompt", "subprocess"],
        "host_declared_services": ["fs", "subprocess", "systemPrompt", "tools"],
        "all_injected_services_declared_by_host": True,
    }
    assert evidence["claim_boundary"]["exact_internal_coordinate_observed"] is False


def test_candidate_set_and_eliminations_are_exact() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["finite_remaining_coordinates"] == subject.FINITE_COORDINATES
    assert evidence["eliminated_coordinates"] == subject.ELIMINATED_COORDINATES
    assert evidence["claim_boundary"]["source_reachable_candidate_set_only"] is True
    assert evidence["claim_boundary"]["repair_selected"] is False


def test_every_runtime_and_effect_counter_is_zero() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["zero_counters"] == {name: 0 for name in subject.ZERO_COUNTERS}
    assert evidence["claim_boundary"] == {
        "source_reachable_candidate_set_only": True,
        "exact_internal_coordinate_observed": False,
        "raw_runtime_error_recovered": False,
        "repair_selected": False,
        "second_native_process_authorized": False,
        "worker_launch_authorized": False,
        "occupied_model_launch_authorized": False,
    }


def test_report_preserves_static_nonobservation_boundary() -> None:
    report = subject.REPORT_PATH.read_text(encoding="utf-8")
    assert "Timestamp: 2026-08-22T04:49:02.031481+10:00" in report
    assert "finite static candidate set" in report
    assert "not an observed internal runtime" in report
    assert "No raw error was recovered" in report
    assert all(coordinate in report for coordinate in subject.FINITE_COORDINATES)
