"""Closed-form canonical check-in rollout/kill-switch/rollback contract."""

from __future__ import annotations

import hashlib
import json
from typing import Any


SCHEMA_VERSION = "emr4.api_spine.canonical_check_in_rollout_runbook.v1"
TARGET_RELATIVE_PATH = (
    "docs/api-spine/manifests/"
    "canonical-check-in-rollout-kill-switch-rollback-runbook.json"
)
MAX_CANDIDATE_BYTES = 8_192

DEFAULT_POSTURE: dict[str, Any] = {
    "ordinary_practice_enabled": False,
    "activation_authority": False,
    "authored_synthetic_allowlist_unchanged": True,
    "active_ordinary_practice_records": 0,
}

REQUIRED_RUNBOOK: dict[str, Any] = {
    "status": "prepared_not_authorized",
    "rollout_stages": [
        "preflight",
        "synthetic_canary_planned",
        "kill_switch_engaged",
        "rollback_required",
        "rollback_verified",
        "withdrawn",
    ],
    "admission": {
        "ordinary_activation_permitted": False,
        "feature_flag_change_permitted": False,
        "allowlist_change_permitted": False,
        "route_mount_change_permitted": False,
    },
    "kill_switch": {
        "default_state": "engaged",
        "allowed_transition": "clear_to_engaged_only",
        "unknown_state_releases_command": False,
    },
    "rollback": {
        "unknown_commit_policy": "deny_success_no_blind_retry",
        "triggers": [
            "candidate_validation_failed",
            "authority_or_attestation_stale",
            "non_phi_alert_threshold_crossed",
            "commit_state_unknown",
            "readback_mismatch",
        ],
        "ordered_steps": [
            "engage_kill_switch",
            "stop_new_admissions",
            "classify_commit_state",
            "read_back_source_truth",
            "verify_zero_ordinary_release",
            "record_non_phi_evidence",
        ],
        "source_truth_readback_required": True,
        "ordinary_release_after_rollback": False,
    },
    "audit": {
        "non_phi_only": True,
        "required_identifier_classes": [
            "correlation_id",
            "idempotency_key_digest",
            "command_receipt_id",
            "source_commit_oid",
            "rollback_reason",
        ],
        "full_git_object_id_required": True,
        "secret_values_permitted": False,
    },
    "effects": {
        "product_route_changed": False,
        "feature_flag_changed": False,
        "synthetic_allowlist_changed": False,
        "ordinary_practice_enabled": False,
        "generic_status_arrived_changed": False,
        "waiting_area_changed": False,
        "product_or_patient_data_used": False,
        "live_runtime_or_deployment_changed": False,
        "protected_ref_changed": False,
    },
    "claim": "runbook_contract_present_default_off",
}

REQUIRED_CANDIDATE: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "command": "canonical_check_in",
    "default_posture": DEFAULT_POSTURE,
    "runbook": REQUIRED_RUNBOOK,
}

BASELINE_CANDIDATE: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "command": "canonical_check_in",
    "default_posture": DEFAULT_POSTURE,
    "runbook": None,
}


class RunbookValidationError(ValueError):
    """The occupied candidate is outside the frozen closed form."""


def canonical_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON with one trailing newline."""

    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def baseline_bytes() -> bytes:
    return canonical_bytes(BASELINE_CANDIDATE)


def required_candidate_bytes() -> bytes:
    return canonical_bytes(REQUIRED_CANDIDATE)


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise RunbookValidationError("candidate_duplicate_key")
        value[key] = item
    return value


def parse_candidate_bytes(payload: bytes) -> dict[str, Any]:
    if not payload or len(payload) > MAX_CANDIDATE_BYTES:
        raise RunbookValidationError("candidate_size_invalid")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RunbookValidationError("candidate_utf8_invalid") from error
    if "\r" in text:
        raise RunbookValidationError("candidate_newline_invalid")
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as error:
        raise RunbookValidationError("candidate_json_invalid") from error
    if not isinstance(value, dict):
        raise RunbookValidationError("candidate_root_invalid")
    return value


def validate_candidate_bytes(payload: bytes) -> dict[str, Any]:
    """Admit only the exact semantic object and return its canonical form."""

    value = parse_candidate_bytes(payload)
    if value != REQUIRED_CANDIDATE:
        raise RunbookValidationError("candidate_closed_form_mismatch")
    canonical = required_candidate_bytes()
    return {
        "value": value,
        "input_bytes": len(payload),
        "input_sha256": sha256_bytes(payload),
        "canonical_bytes": canonical,
        "canonical_byte_count": len(canonical),
        "canonical_sha256": sha256_bytes(canonical),
        "ordinary_practice_enabled": False,
        "activation_authority": False,
        "claim": REQUIRED_RUNBOOK["claim"],
    }
