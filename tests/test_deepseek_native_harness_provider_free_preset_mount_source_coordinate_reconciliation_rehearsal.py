from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_source_coordinate_reconciliation_rehearsal as subject,
)


CACHE_ROOT = Path.home() / ".cache" / "emr4-native-harness"


def test_contract_and_schema_are_strict() -> None:
    contract = subject.load_contract()
    schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(contract)
    assert schema["additionalProperties"] is False
    assert contract["planning_source"] == (
        "6f67aef39b18ee0d548330dcb5a2492f3e85e22b"
    )
    assert contract["accepted_terminal_source"] == (
        "c66eb82cccd64961f0d99bf9f67803e1a69ebd8a"
    )
    assert len(contract["source_files"]) == 8


def test_exact_pinned_source_bindings_and_versions_pass() -> None:
    contract = subject.load_contract()
    payloads, bindings = subject.verify_source_bindings(contract, CACHE_ROOT)
    assert list(payloads) == [row["path"] for row in contract["source_files"]]
    assert len(bindings) == 8
    assert all(row["passed"] for row in bindings)
    assert {row["version"] for row in bindings} == {"0.1.0-rc.7"}


def test_source_semantics_bind_every_mount_coordinate() -> None:
    contract = subject.load_contract()
    payloads, _ = subject.verify_source_bindings(contract, CACHE_ROOT)
    checks = subject.verify_source_semantics(payloads)
    assert checks == {
        "mount_checks_agent_scope": True,
        "mount_resolves_mountable_roster": True,
        "mount_awaits_standing_scope": True,
        "standing_checks_composition_stamp": True,
        "standing_calls_mount_preset": True,
        "mount_awaits_entry_tree": True,
        "mount_checks_subtree_publication": True,
        "mount_checks_inactive_rows": True,
        "mount_checks_root_service_leaks": True,
        "scope_binding_occurs_after_standing_mount": True,
        "preset_tree_owns_bare_package_resolution": True,
    }


def test_plugin_prerequisites_are_exact_and_host_declared() -> None:
    contract = subject.load_contract()
    payloads, _ = subject.verify_source_bindings(contract, CACHE_ROOT)
    assert subject.verify_plugin_prerequisites(payloads) == {
        "preset_rows": [
            "@deepseek-ai/dsh-tool-fs",
            "@deepseek-ai/dsh-tool-fs-search",
        ],
        "tool_fs_inject": ["tools", "fs", "systemPrompt"],
        "tool_fs_search_inject": ["tools", "systemPrompt", "subprocess"],
        "host_declared_services": ["fs", "subprocess", "systemPrompt", "tools"],
        "all_injected_services_declared_by_host": True,
    }


def test_accepted_terminal_is_preserved_without_raw_detail() -> None:
    terminal = subject.verify_accepted_terminal(subject.load_contract())
    assert terminal == {
        "candidate_source": "c66eb82cccd64961f0d99bf9f67803e1a69ebd8a",
        "result": "preset_composition_failure_attributed",
        "last_admitted_stage": "private_identity_admitted",
        "safe_guard_coordinate": "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
        "safe_guard_detail": None,
        "raw_runtime_detail_retained": False,
    }


def test_evidence_is_schema_closed_and_has_zero_runtime_authority() -> None:
    evidence = subject.build_evidence(CACHE_ROOT)
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["finite_remaining_coordinates"] == subject.FINITE_COORDINATES
    assert evidence["eliminated_coordinates"] == subject.ELIMINATED_COORDINATES
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


def test_source_drift_fails_closed(tmp_path: Path) -> None:
    contract = subject.load_contract()
    source_root = tmp_path / "emr4-native-harness" / subject.PurePosixPath(
        contract["seed_relative_path"]
    ).relative_to("emr4-native-harness")
    for row in contract["source_files"]:
        target = source_root.joinpath(*subject.PurePosixPath(row["path"]).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"drift")
    with pytest.raises(subject.SourceReconciliationError, match="source_bytes_mismatch"):
        subject.verify_source_bindings(contract, tmp_path / "emr4-native-harness")


def test_report_states_static_nonobservation_boundary() -> None:
    report = subject.render_report(subject.build_evidence(CACHE_ROOT))
    assert "finite static candidate set" in report
    assert "not an observed internal runtime" in report
    assert "No raw error was recovered" in report
    assert all(coordinate in report for coordinate in subject.FINITE_COORDINATES)


def test_module_contains_no_native_harness_launch_path() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert "subprocess.Popen" not in source
    assert "lib/bin.js" not in source
    assert "--profile" not in source
    assert "--execute" not in source
