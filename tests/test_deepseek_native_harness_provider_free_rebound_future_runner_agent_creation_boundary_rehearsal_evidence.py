from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-rebound-future-runner-agent-creation-"
    "boundary-rehearsal"
)
OPERATION_ROOT = ROOT / "orchestration" / "continuity" / OPERATION_ID
EVIDENCE_PATH = OPERATION_ROOT / "native-agent-creation-boundary-evidence.json"
ATTEMPT_PATH = OPERATION_ROOT / "native-attempt-consumed.json"
REPORT_PATH = OPERATION_ROOT / "native-agent-creation-boundary-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
INTERPRETATION_PATH = OPERATION_ROOT / "failure-interpretation.json"
REJECTIONS_PATH = OPERATION_ROOT / "rejected-generated-claims.json"
SUCCESSOR_PLAN = (
    ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-post-hmr-agent-factory-closed-"
    "subcoordinate-diagnostic-rehearsal-plan.md"
)


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_bytes())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_consumed_attempt_is_exact_and_has_no_retry() -> None:
    attempt = _json(ATTEMPT_PATH)
    assert attempt == {
        "candidate_source": "39373fbbde75c7614dfe9c64e0fe1bcb5c5af212",
        "execution_attempt_id": "rebound-agent-creation-boundary-attempt-001",
        "operation_id": OPERATION_ID,
        "resume_permitted": False,
        "retry_count": 0,
        "schema_version": "ariadne.native_harness_agent_creation_boundary_attempt.v1",
        "state": "consumed",
    }


def test_failure_evidence_is_schema_valid() -> None:
    schema = _json(OPERATION_ROOT / "evidence.schema.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(_json(EVIDENCE_PATH))


def test_native_failure_coordinate_and_cleanup_are_exact() -> None:
    evidence = _json(EVIDENCE_PATH)
    assert evidence["result"] == "fail"
    assert evidence["failure_classification"] == "PROCESS_EXIT_REJECTED"
    assert evidence["sidecar"] is None
    assert evidence["controller_terminal"] is None
    assert evidence["launch"] == {
        "duration_ms": 906,
        "exit_code": 2,
        "exit_mode": "self_exited_before_typed_sidecar",
        "hmr_mutation_count": 1,
        "native_process_count": 1,
        "raw_stream_read": False,
        "resume_count": 0,
        "retry_count": 0,
        "started_at_utc": "2026-08-21T16:46:00Z",
        "stderr_retained": False,
        "stdout_retained": False,
    }
    assert evidence["cleanup"] == {
        "disposable_root_absent": True,
        "package_seed_unchanged": True,
        "process_absent": True,
        "raw_environment_retained": False,
        "raw_logs_retained": False,
    }


def test_downstream_and_target_boundaries_remain_zero() -> None:
    evidence = _json(EVIDENCE_PATH)
    provider = evidence["provider_boundary"]
    for name in (
        "broker_process_count",
        "broker_request_count",
        "database_invocation_count",
        "docker_invocation_count",
        "model_request_count",
        "network_attempt_count",
        "occupied_worker_count",
        "provider_request_count",
        "request_count",
        "turn_count",
    ):
        assert provider[name] == 0
    assert evidence["target"] == {
        "absent_after_process": True,
        "file_created": False,
        "used": False,
    }


def test_failure_interpretation_marks_factory_progress_unknown() -> None:
    interpretation = _json(INTERPRETATION_PATH)
    assert interpretation["result"] == "fail"
    assert interpretation["factory_progress"] == {
        "classification": "unknown_without_typed_sidecar",
        "agent_create_invocation_observed": None,
        "private_agent_preparation_observed": None,
        "private_session_preparation_observed": None,
        "setup_commit_observed": None,
        "publication_veto_observed": None,
    }
    assert interpretation["retry_permitted"] is False


def test_generated_success_claims_are_hash_bound_and_rejected() -> None:
    rejections = _json(REJECTIONS_PATH)
    rows = {row["path"]: row for row in rejections["rejected_artifacts"]}
    report_key = REPORT_PATH.relative_to(ROOT).as_posix()
    efficacy_key = EFFICACY_PATH.relative_to(ROOT).as_posix()
    assert rows[report_key]["sha256"] == _sha256(REPORT_PATH)
    assert rows[efficacy_key]["sha256"] == _sha256(EFFICACY_PATH)
    assert "factory reached its synchronous unpublished" in REPORT_PATH.read_text(
        encoding="utf-8"
    )
    assert _json(EFFICACY_PATH)["control_gain"] == (
        "real_factory_prepublication_commit_is_under_typed_orchestrator_veto"
    )


def test_factory_fallback_map_is_explicitly_non_observational() -> None:
    rejections = _json(REJECTIONS_PATH)
    row = rejections["partially_admissible_artifact"]
    assert row["sha256"] == _sha256(EVIDENCE_PATH)
    assert row["inadmissible_as_observed_fields"] == ["factory_boundary"]


def test_successor_is_a_distinct_closed_diagnostic_not_a_retry() -> None:
    text = SUCCESSOR_PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "post-hmr-agent-factory-diagnostic-attempt-001" in text
    assert "It is not an agent-creation" in text
    assert "not a retry of consumed" in text
    assert "Package and guard imports occur sequentially" in normalized
    assert "unclassified_error" in text
    assert "There is no retry, resume" in text


def test_authoritative_artifact_hashes_remain_exact() -> None:
    assert _sha256(ATTEMPT_PATH) == (
        "b3ff5e111b68fc9f8ce66ccf62140dc10852df7412ffaff5452466f1a53d3b37"
    )
    assert _sha256(EVIDENCE_PATH) == (
        "cf674a1759d075a818dfffb2bf1fa9018e35104bf89466fad2beb616bd633696"
    )
    assert _sha256(REPORT_PATH) == (
        "bd83be7d1434a122f262549a23470f6e8276924ed6b6441416ba4d87f3477661"
    )
    assert _sha256(EFFICACY_PATH) == (
        "0e78435e429f0abae4661c723279794510b7aeaf1e37d311d5474b913703c22f"
    )
