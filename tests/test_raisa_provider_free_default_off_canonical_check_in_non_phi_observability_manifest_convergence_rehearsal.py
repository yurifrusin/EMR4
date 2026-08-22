"""Admission for the canonical default-off check-in observability manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "docs/api-spine/manifests/canonical-check-in-non-phi-observability.json"
)
SOURCE_CONTRACT = ROOT / (
    "orchestration/continuity/raisa-provider-free-default-off-ordinary-"
    "practice-canonical-check-in-admission-control-architecture/contract.json"
)
PLAN = ROOT / (
    "docs/raisa-provider-free-default-off-canonical-check-in-non-phi-"
    "observability-manifest-convergence-rehearsal-plan.md"
)
THREAT_DELTA = ROOT / (
    "docs/security/raisa-provider-free-default-off-canonical-check-in-non-phi-"
    "observability-manifest-convergence-rehearsal-threat-model-delta.md"
)
OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
EXPECTED_BYTES = 6291
EXPECTED_SHA256 = "79d6191e1a499e85bb12be38fd15980c7f1bf7dc54eb15132c607b0c43341d8c"
ARCHITECTURE_SOURCE = "752b521c59f5b44bf46de0cf776a33ac74b8134d"


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _source() -> dict[str, object]:
    return json.loads(SOURCE_CONTRACT.read_text(encoding="utf-8"))


def test_manifest_is_canonical_and_projects_the_exact_accepted_object() -> None:
    payload = MANIFEST.read_bytes()
    value = _manifest()
    canonical = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")

    assert payload == canonical
    assert len(payload) == EXPECTED_BYTES
    assert hashlib.sha256(payload).hexdigest() == EXPECTED_SHA256
    assert value["observability"] == _source()["observability"]


def test_wrapper_is_default_off_declarative_and_source_bound() -> None:
    value = _manifest()

    assert value["schema_version"] == (
        "emr4.api_spine.canonical_check_in_non_phi_observability.v1"
    )
    assert value["status"] == "prepared_not_authorized"
    assert value["claim"] == (
        "non_phi_observability_contract_present_default_off"
    )
    assert value["source"] == {
        "architecture_contract": (
            "orchestration/continuity/raisa-provider-free-default-off-ordinary-"
            "practice-canonical-check-in-admission-control-architecture/"
            "contract.json"
        ),
        "architecture_source_git_object": ARCHITECTURE_SOURCE,
        "projection": "exact_observability_subobject",
    }
    assert value["default_posture"] == {
        "alert_transport_enabled": False,
        "automatic_control_action_enabled": False,
        "instrumentation_enabled": False,
        "ordinary_practice_enabled": False,
    }
    assert set(value["effects"].values()) == {False}


def test_metric_families_and_label_domains_are_exact_and_low_cardinality() -> None:
    observability = _manifest()["observability"]
    metrics = observability["metric_families"]

    assert [metric["name"] for metric in metrics] == [
        "emr4_check_in_admission_decisions_total",
        "emr4_check_in_admission_snapshot_age_seconds",
        "emr4_check_in_admission_kill_switch",
        "emr4_check_in_unknown_commit_total",
        "emr4_check_in_control_commands_total",
    ]
    assert [metric["kind"] for metric in metrics] == [
        "counter",
        "gauge",
        "gauge",
        "counter",
        "counter",
    ]
    for metric in metrics:
        for domain in metric["label_domains"]:
            assert domain["values"]
            assert len(domain["values"]) <= 15
            assert len(domain["values"]) == len(set(domain["values"]))


def test_forbidden_values_alerts_and_feedback_controls_are_exact() -> None:
    observability = _manifest()["observability"]

    assert observability["forbidden_labels_and_values"] == [
        "practice_id",
        "appointment_id",
        "patient_id",
        "practitioner_id",
        "user_id",
        "actor_id",
        "correlation_id",
        "idempotency_key",
        "command_id",
        "record_id",
        "evidence_digest",
        "token",
        "free_text",
        "request_body",
        "response_body",
    ]
    assert [alert["alert_id"] for alert in observability["alerts"]] == [
        "check_in_kill_switch_engaged",
        "check_in_admission_snapshot_invalid_or_stale",
        "check_in_unknown_commit",
        "check_in_active_record_rejected",
        "check_in_control_audit_failure",
        "check_in_rollback_failure",
    ]
    for alert in observability["alerts"]:
        assert alert["severity"] == "critical"
        assert alert["automatic_control_action"] is False
        assert alert["contains_identifier"] is False

    assert observability["raw_request_or_response_allowed"] is False
    assert observability["audit_record_used_as_metric"] is False
    assert observability["telemetry_feedback_to_admission"] is False
    assert observability["automatic_retry_or_control_action"] is False


def test_existing_check_in_openapi_identity_and_plan_boundary_are_unchanged() -> None:
    openapi = OPENAPI.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT_DELTA.read_text(encoding="utf-8")

    assert openapi.count("operationId: proposeAppointmentCheckIn") == 1
    assert openapi.count("operationId: confirmAppointmentCheckInProposal") == 1
    for marker in (
        "6,291 bytes",
        EXPECTED_SHA256,
        "instrumentation, telemetry transport, alert delivery",
        "No `app/**`",
        "explicit-path staging only",
    ):
        assert marker in plan
    for marker in (
        "Alerts contain no identifiers",
        "declarative vocabulary",
        "No metric is emitted",
        "automatic_control_action: false",
    ):
        assert marker in threat
