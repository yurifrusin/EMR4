"""Admission for the canonical default-off check-in rollout runbook manifest."""

from __future__ import annotations

import json
from pathlib import Path

from orchestration_harness import check_in_rollout_runbook as runbook


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / runbook.TARGET_RELATIVE_PATH
PLAN = ROOT / (
    "docs/raisa-provider-free-default-off-canonical-check-in-rollout-kill-"
    "switch-rollback-runbook-convergence-rehearsal-plan.md"
)
THREAT_DELTA = ROOT / (
    "docs/security/raisa-provider-free-default-off-canonical-check-in-rollout-"
    "kill-switch-rollback-runbook-convergence-rehearsal-threat-model-delta.md"
)
OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
EXPECTED_BYTES = 2_331
EXPECTED_SHA256 = "dbd765ef3afe2ffe283a07befff44f745b21a8ec474c58d5a6d944fe3a9c8448"


def test_manifest_is_the_exact_frozen_closed_form() -> None:
    payload = MANIFEST.read_bytes()

    assert payload == runbook.required_candidate_bytes()
    assert len(payload) == EXPECTED_BYTES
    assert runbook.sha256_bytes(payload) == EXPECTED_SHA256

    projection = runbook.validate_candidate_bytes(payload)
    assert projection["canonical_bytes"] == payload
    assert projection["canonical_byte_count"] == EXPECTED_BYTES
    assert projection["canonical_sha256"] == EXPECTED_SHA256
    assert projection["ordinary_practice_enabled"] is False
    assert projection["activation_authority"] is False
    assert projection["claim"] == "runbook_contract_present_default_off"


def test_manifest_keeps_activation_kill_switch_and_recovery_fail_closed() -> None:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    posture = value["default_posture"]
    policy = value["runbook"]

    assert posture == {
        "activation_authority": False,
        "active_ordinary_practice_records": 0,
        "authored_synthetic_allowlist_unchanged": True,
        "ordinary_practice_enabled": False,
    }
    assert policy["status"] == "prepared_not_authorized"
    assert policy["admission"] == {
        "allowlist_change_permitted": False,
        "feature_flag_change_permitted": False,
        "ordinary_activation_permitted": False,
        "route_mount_change_permitted": False,
    }
    assert policy["kill_switch"] == {
        "allowed_transition": "clear_to_engaged_only",
        "default_state": "engaged",
        "unknown_state_releases_command": False,
    }
    assert policy["rollback"]["unknown_commit_policy"] == (
        "deny_success_no_blind_retry"
    )
    assert policy["rollback"]["source_truth_readback_required"] is True
    assert policy["rollback"]["ordinary_release_after_rollback"] is False


def test_manifest_audit_and_effects_are_non_phi_and_non_actuating() -> None:
    policy = json.loads(MANIFEST.read_text(encoding="utf-8"))["runbook"]

    assert policy["audit"]["non_phi_only"] is True
    assert policy["audit"]["secret_values_permitted"] is False
    assert policy["audit"]["full_git_object_id_required"] is True
    assert policy["audit"]["required_identifier_classes"] == [
        "correlation_id",
        "idempotency_key_digest",
        "command_receipt_id",
        "source_commit_oid",
        "rollback_reason",
    ]
    assert set(policy["effects"].values()) == {False}


def test_existing_check_in_openapi_command_identity_is_unchanged() -> None:
    text = OPENAPI.read_text(encoding="utf-8")

    assert text.count("operationId: proposeAppointmentCheckIn") == 1
    assert text.count("operationId: confirmAppointmentCheckInProposal") == 1
    assert "type Mutation" not in text


def test_plan_and_threat_delta_freeze_declarative_only_scope() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT_DELTA.read_text(encoding="utf-8")

    required_plan_markers = (
        "2,331 bytes",
        EXPECTED_SHA256,
        "declarative API-Spine manifest",
        "not rollout execution",
        "No `app/**`",
        "explicit-path staging only",
    )
    for marker in required_plan_markers:
        assert marker in plan

    required_threat_markers = (
        "Ordinary practice remains disabled",
        "Unknown commit state never releases success",
        "full Git object",
        "declarative policy evidence",
        "does not itself enforce runtime behavior",
    )
    for marker in required_threat_markers:
        assert marker in threat
