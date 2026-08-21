from __future__ import annotations

import json

from scripts import (
    deepseek_native_harness_provider_free_preset_composition_safe_terminal_bridge_rehearsal as subject,
)


def _load(path):
    return json.loads(path.read_bytes())


def test_consumed_attempt_is_exact_and_nonrepeatable() -> None:
    assert _load(subject.ATTEMPT_CONSUMED_PATH) == {
        "schema_version": "ariadne.native_harness_agent_factory_diagnostic_attempt.v1",
        "operation_id": subject.OPERATION_ID,
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": "c66eb82cccd64961f0d99bf9f67803e1a69ebd8a",
        "state": "consumed",
        "retry_count": 0,
        "resume_permitted": False,
    }


def test_typed_terminal_attributes_the_mount_failure() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["result"] == "pass"
    assert evidence["candidate_source"] == (
        "c66eb82cccd64961f0d99bf9f67803e1a69ebd8a"
    )
    assert evidence["controller_terminal"] == {
        "result": "preset_composition_failure_attributed",
        "last_admitted_stage": "private_identity_admitted",
        "error_class": None,
        "factory_boundary": {
            "agent_create_invocation_count": 1,
            "private_agent_preparation_count": 1,
            "private_session_preparation_count": 1,
            "live_agent_count": 0,
            "live_session_count": 0,
            "session_created_event_count": 0,
            "agent_created_event_count": 0,
            "agent_session_start_event_count": 0,
        },
        "raw_runtime_detail_retained": False,
        "safe_guard_coordinate": "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
        "safe_guard_detail": None,
    }


def test_no_downstream_activity_or_residue_exists() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["provider_boundary"] == {
        "credential_environment_names_removed_count": 3,
        "network_attempt_count": 0,
        "network_ledger_valid": True,
        "turn_count": 0,
        "request_count": 0,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "occupied_worker_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
    }
    assert evidence["target"] == {
        "file_created": False,
        "used": False,
        "absent_after_process": True,
    }
    assert evidence["cleanup"] == {
        "process_absent": True,
        "disposable_root_absent": True,
        "raw_environment_retained": False,
        "raw_logs_retained": False,
        "package_seed_unchanged": True,
    }


def test_execution_is_one_process_one_terminal_and_no_retry() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["readiness"] == {
        "events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "valid": True,
        "exact_expected_order": True,
    }
    assert evidence["launch"]["native_process_count"] == 1
    assert evidence["launch"]["retry_count"] == 0
    assert evidence["launch"]["resume_count"] == 0
    assert evidence["launch"]["hmr_mutation_count"] == 1
    assert evidence["launch"]["exit_code"] == 3
    assert evidence["launch"]["exit_mode"] == "self_exited_after_typed_sidecar"
    assert evidence["composition"]["runner_copy_equal"] is True
    assert evidence["composition"]["bundle_manifest_unchanged"] is True


def test_sidecar_retains_only_closed_safe_coordinate() -> None:
    sidecar = _load(subject.EVIDENCE_PATH)["sidecar"]
    assert sidecar["safe_guard_coordinate"] in subject.SAFE_GUARD_COORDINATES
    assert sidecar["safe_guard_detail"] is None
    assert sidecar["raw_error_retained"] is False
    assert sidecar["preset_mounted"] is False
    assert sidecar["model_selection_installed"] is False
    forbidden = {
        "message",
        "stack",
        "code",
        "cause",
        "stream",
        "prompt",
        "response",
        "credential",
        "path",
    }
    assert forbidden.isdisjoint(sidecar)


def test_report_timestamp_is_derived_from_typed_launch_time() -> None:
    report = subject.REPORT_PATH.read_text(encoding="utf-8")
    assert "Timestamp: 2026-08-22T04:26:11+10:00" in report
    assert "Diagnostic terminal: `preset_composition_failure_attributed`" in report
    assert "Safe guard coordinate: `EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED`" in report


def test_source_interpretation_is_finite_and_does_not_select_a_repair() -> None:
    interpretation = _load(
        subject.OPERATION_ROOT / "preset-mount-source-coordinate-interpretation.json"
    )
    assert interpretation["terminal"]["safe_guard_coordinate"] == (
        "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED"
    )
    assert interpretation["admitted_static_prerequisites"][
        "host_declares_required_services"
    ] is True
    assert interpretation["finite_remaining_coordinates"] == [
        "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
        "PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE",
        "PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED",
        "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
        "PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT",
        "PRESET_MOUNT_ROOT_SERVICE_LEAK",
    ]
    assert interpretation["claim_boundary"] == {
        "exact_internal_coordinate_observed": False,
        "raw_runtime_error_retained": False,
        "repair_selected": False,
        "second_native_process_authorized": False,
        "worker_launch_authorized": False,
        "occupied_model_launch_authorized": False,
    }
