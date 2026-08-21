from __future__ import annotations

import json

from scripts import (
    deepseek_native_harness_provider_free_post_hmr_agent_factory_closed_subcoordinate_diagnostic_rehearsal as subject,
)


def _load(path):
    return json.loads(path.read_bytes())


def test_consumed_attempt_is_exactly_one_and_has_no_retry() -> None:
    attempt = _load(subject.ATTEMPT_CONSUMED_PATH)
    assert attempt == {
        "schema_version": "ariadne.native_harness_agent_factory_diagnostic_attempt.v1",
        "operation_id": subject.OPERATION_ID,
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": "33b4e061b1385abc91ecd170e4abdb563396c3ef",
        "state": "consumed",
        "retry_count": 0,
        "resume_permitted": False,
    }


def test_evidence_accepts_the_finite_failure_subcoordinate() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    assert evidence["result"] == "pass"
    assert evidence["failure_classification"] is None
    assert evidence["candidate_source"] == (
        "33b4e061b1385abc91ecd170e4abdb563396c3ef"
    )
    assert evidence["controller_terminal"] == {
        "result": "closed_subcoordinate_failure",
        "last_admitted_stage": "private_identity_admitted",
        "error_class": "unclassified_error",
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
    }


def test_evidence_narrows_failure_to_preset_composition_interval() -> None:
    evidence = _load(subject.EVIDENCE_PATH)
    sidecar = evidence["sidecar"]
    assert sidecar["last_admitted_stage"] == "private_identity_admitted"
    assert sidecar["preset_mounted"] is False
    assert sidecar["model_selection_installed"] is False
    assert sidecar["veto_exact"] is False
    assert sidecar["veto_rejected"] is False
    assert subject.STAGES.index(sidecar["last_admitted_stage"]) + 1 == (
        subject.STAGES.index("preset_composition_admitted")
    )


def test_downstream_activity_publication_and_target_remain_zero() -> None:
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


def test_readiness_hmr_exit_and_bundle_are_exact() -> None:
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
    assert evidence["launch"]["exit_code"] == 2
    assert evidence["launch"]["exit_mode"] == "self_exited_after_typed_sidecar"
    assert evidence["composition"]["runner_copy_equal"] is True
    assert evidence["composition"]["bundle_manifest_unchanged"] is True


def test_report_and_efficacy_do_not_claim_factory_success() -> None:
    report = subject.REPORT_PATH.read_text(encoding="utf-8")
    efficacy = _load(subject.EFFICACY_PATH)
    assert "Diagnostic terminal: `closed_subcoordinate_failure`" in report
    assert "Last admitted stage: `private_identity_admitted`" in report
    assert "prepublication_veto_diagnosed" not in report
    assert efficacy["factory_boundary_observed"] is True
    assert efficacy["control_gain"] == (
        "finite_post_hmr_subcoordinate_or_exact_link_apply_absence"
    )
    assert efficacy["worker_launch_authorized"] is False
    assert efficacy["occupied_model_launch_authorized"] is False


def test_sidecar_contains_no_raw_runtime_detail() -> None:
    sidecar = _load(subject.EVIDENCE_PATH)["sidecar"]
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
    assert sidecar["raw_error_retained"] is False


def test_generated_future_timestamp_is_rejected_without_rejecting_result() -> None:
    rejection = _load(
        subject.OPERATION_ROOT / "generated-report-metadata-rejection.json"
    )
    assert rejection["rejected_field"] == "Timestamp"
    assert rejection["rejected_value"] == "2026-08-22T04:15:00+10:00"
    assert rejection["artifact"]["sha256"] == subject.sha256_file(
        subject.REPORT_PATH
    )
    assert rejection["accepted_report_claims_unchanged"] is True
    assert rejection["raw_runtime_detail_added"] is False
