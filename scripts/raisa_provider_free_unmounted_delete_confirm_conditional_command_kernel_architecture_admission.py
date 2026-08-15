"""Pure authored-synthetic delete-confirm conditional-command kernel rehearsal.

This module is a provider-free, unmounted, authored-synthetic protocol. It
imports no application route, database driver, provider client, browser tooling
or runtime command code. It builds one closed contract and JSON Schema, binds
exact SHA-256 hashes for the frozen tranche sources, and deterministically
rehearses the future dedicated ``confirmAppointmentDeleteProposal`` /
``delete-confirm`` transaction.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission"
)
PACKET_PATH = PACKET_DIR / "contract.json"
SCHEMA_PATH = PACKET_DIR / "contract.schema.json"
EVIDENCE_PATH = PACKET_DIR / "provider-free-acceptance-evidence.json"

GLOBAL_LOCK_ORDER = ["practice", "schedule_domain", "appointment", "idempotency_record"]
LOCK_ORDER = ["practice", "appointment", "idempotency_record"]
UNUSED_LOCK_RULE = "skip_schedule_domain_without_reordering"
CANONICAL_OPERATION_ID = "confirmAppointmentDeleteProposal"
CANONICAL_INGRESS = "delete-confirm"
MAX_FREE_TEXT_LENGTH = 500
FICTIONAL_CANCELLATION_TEXT = "Patient requested cancellation due to a schedule change"

# Current ``Cancelled`` reason-code allowlist for new dedicated ingress.
# ``DID_NOT_ATTEND`` / ``LEFT_WITHOUT_SEEN`` are status-family codes and
# ``LEGACY_UNCLASSIFIED`` is a compatibility code; none may weaken new ingress.
CANCELLED_REASON_CODES = [
    "PATIENT_CANCELLED",
    "PATIENT_RESCHEDULED",
    "PATIENT_UNWELL",
    "PATIENT_TRANSPORT",
    "PRACTITIONER_UNAVAILABLE",
    "CLINIC_OPERATIONAL",
    "CLINIC_RESCHEDULED",
    "ADMIN_ERROR",
    "DUPLICATE_BOOKING",
    "OTHER",
]

ALLOWED_ACTOR_ROLES = [
    "Receptionist",
    "GP",
    "Nurse",
    "Admin",
    "PracticeOwner",
]

OUTCOMES = [
    "committed",
    "idempotent_replay",
    "stale_precondition",
    "authority_revoked",
    "confirmation_required",
    "validation_rejected",
    "idempotency_conflict",
]

SOURCE_BINDINGS = [
    {
        "path": "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-plan.md",
        "sha256": "8c9551a08751c9596e131f88d17bf2503be555955b4ab36de7c163874f8067b3",
    },
    {
        "path": "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md",
        "sha256": "8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91",
    },
    {
        "path": "docs/security/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-threat-model-delta.md",
        "sha256": "011b107fa7e42ea7fa6e025b68f1c6fe7321f384af964c3cce2cfc201c5d0005",
    },
    {
        "path": "docs/raisa-reception-one-cancellation-command-path-readiness-review-closeout.md",
        "sha256": "0e65d8ac307613c8a53b652225cd6b3d310a393158ab2ff9ada14aad7da4000e",
    },
    {
        "path": "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-sol-acceptance.md",
        "sha256": "66b9bad4d1ee6fe71afd0f56eb7f32eeedc6458b141b2585ef0c5656d0d1997c",
    },
    {
        "path": "orchestration/api_spine_adr.md",
        "sha256": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
    },
    {
        "path": "docs/api-spine/openapi/appointment-commands.yaml",
        "sha256": "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a",
    },
]

TRACE_STEPS = [
    "lock:practice",
    "lock:appointment",
    "check:authority_after_target_lock",
    "lock:idempotency_record",
    "check:authority_all_locks_held",
    "classify:bindings",
    "inspect:idempotency",
    "validate:confirmation_and_evidence",
    "recheck:appointment_state",
    "validate:reason_policy",
    "stage:appointment_mutation",
    "stage:delete_audit",
    "stage:completed_receipt",
    "commit:atomic",
    "serialize:response",
    "readback:separate_authorisation",
]

FIXED_TIMESTAMPS_UTC = {
    "proposal_generated_at": "2026-08-15T01:50:49Z",
    "signed_at": "2026-08-15T01:50:49Z",
    "expires_at": "2026-08-15T02:10:49Z",
    "confirmed_at": "2026-08-15T01:55:04Z",
    "committed_at": "2026-08-15T01:55:04Z",
}

EFFECT_BOUNDARY = {
    "application_route_imported": False,
    "application_model_imported": False,
    "database_driver_imported": False,
    "database_or_source_opened": False,
    "watcher_or_event_consumed": False,
    "provider_or_network_used": False,
    "real_lock_acquired": False,
    "mutation_audit_or_receipt_written": False,
    "command_executed": False,
    "product_or_patient_data_used": False,
}

CONFIRMATION_STATES = [
    "valid",
    "missing",
    "false",
    "warning_unacknowledged",
    "evidence_tampered",
    "evidence_expired",
    "evidence_binding_mismatch",
]
SOURCE_STATES = [
    "current",
    "stale_version",
    "stale_status",
    "stale_waiting_area",
    "stale_existing_reason",
    "stale_proposed_reason",
]
REASON_STATES = [
    "current_cancelled_code",
    "missing",
    "status_family_code",
    "legacy_unclassified",
    "allowlist_invalid",
]
CANCELLATION_TEXT_STATES = [
    "present",
    "null",
    "too_long",
]
IDEMPOTENCY_STATES = [
    "absent",
    "missing",
    "same_digest_completed",
    "different_digest",
]
BINDING_STATES = [
    "exact",
    "session_mismatch",
    "practice_mismatch",
    "actor_mismatch",
    "operation_mismatch",
    "target_mismatch",
    "state_mismatch",
    "waiting_area_mismatch",
    "existing_reason_mismatch",
    "proposed_reason_mismatch",
    "digest_mismatch",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixed_digest(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


FIXED_DIGESTS = {
    "proposal_digest": _fixed_digest("delete-confirm:proposal:syn-appointment-001"),
    "session_digest": _fixed_digest("delete-confirm:session:syn-session-001"),
    "evidence_payload_hash": _fixed_digest(
        "delete-confirm:evidence:syn-practice-001:syn-actor-001:syn-session-001"
    ),
    "command_digest": _fixed_digest(
        "delete-confirm:command:syn-key-delete-confirm-001"
    ),
    "receipt_digest": _fixed_digest(
        "delete-confirm:receipt:syn-receipt-delete-confirm-001"
    ),
}

AUTHORITY_CONTRACT = {
    "pretransaction_authentication_is_final_authority": False,
    "authority_source": "authenticated_server_session_and_current_authority_store",
    "authority_fence": "practice_authority_generation_held_for_entire_transaction",
    "server_owned_identity_fields": [
        "practice_id",
        "actor_user_id",
        "actor_role",
        "authenticated_session_id",
    ],
    "request_body_authority_fields_accepted": [],
    "allowed_actor_roles": list(ALLOWED_ACTOR_ROLES),
    "required_capability": "appointment.cancel.confirm",
    "current_checks": [
        "actor_active",
        "practice_active",
        "actor_practice_binding_exact",
        "actor_role_current_and_allowed",
        "appointment_cancel_confirm_capability_current",
    ],
    "check_points": [
        "after_practice_scoped_appointment_lock",
        "while_practice_appointment_and_idempotency_locks_held",
    ],
    "authority_and_practice_scoped_target_precede_receipt_disclosure": True,
}

SIGNED_EVIDENCE_CONTRACT = {
    "schema_version": "raisa.delete_confirmation_evidence.v1",
    "purpose": "appointment_delete_confirm",
    "required_fields": [
        "schema_version",
        "purpose",
        "key_id",
        "practice_id",
        "actor_user_id",
        "authenticated_session_digest",
        "operation_id",
        "route_family",
        "target_appointment_id",
        "proposal_nonce",
        "proposal_generated_at",
        "signed_at",
        "expires_at",
        "pre_state_version",
        "pre_status",
        "pre_waiting_area_id",
        "pre_cancellation_reason",
        "pre_status_reason_code",
        "proposed_status_reason_code",
        "proposed_cancellation_reason",
        "required_warning_codes",
        "proposal_freshness_id",
        "command_digest",
        "signature",
    ],
    "authenticity": "backend_signature_exact_payload_and_purpose",
    "freshness_interval": "proposal_generated_at_le_signed_at_le_confirmed_at_le_expires_at",
    "warning_acknowledgement": "exact_set_equality",
    "event_or_model_evidence_accepted": False,
}

REASON_POLICY = {
    "status_reason_code": {
        "required_for_new_dedicated_ingress": True,
        "allowed_values": list(CANCELLED_REASON_CODES),
        "legacy_unclassified_allowed": False,
        "status_family_codes_allowed": False,
    },
    "cancellation_reason": {
        "required": False,
        "nullable": True,
        "maximum_characters": MAX_FREE_TEXT_LENGTH,
        "preservation": "exact_admitted_json_value",
    },
    "confirmed_warnings_are_reasons": False,
}

IDEMPOTENCY_CONTRACT = {
    "identity_fields": [
        "practice_id",
        "actor_user_id",
        "operation_id",
        "idempotency_key_hash",
    ],
    "request_binding_fields": [
        "authenticated_session_digest",
        "route_family",
        "target_appointment_id",
        "request_body_digest",
    ],
    "claim_order": "after_practice_appointment_and_first_authority_check",
    "same_key_same_digest": "return_integrity_valid_completed_receipt_only",
    "same_key_different_digest": "non_disclosing_idempotency_conflict",
    "in_progress_on_rollback": "discarded_with_transaction",
    "receipt_disclosure_requires_current_authority": True,
}

TRANSACTION_CONTRACT = {
    "owner": "backend_delete_confirm_kernel",
    "single_command_owned_transaction": True,
    "global_lock_order": list(GLOBAL_LOCK_ORDER),
    "kernel_lock_plan": list(LOCK_ORDER),
    "unused_lock_rule": UNUSED_LOCK_RULE,
    "decision_trace": list(TRACE_STEPS),
    "authority_fence_physical_mapping_proven": False,
    "physical_mapping_next_gate": "provider-free-unmounted-delete-confirm-physical-representability-review",
}

ATOMIC_EFFECT_CONTRACT = {
    "appointment_required_fields": [
        "practice_id",
        "appointment_id",
        "status",
        "waiting_area_id",
        "cancellation_reason",
        "status_reason_code",
        "pre_state_version",
        "post_state_version",
    ],
    "audit_required_fields": [
        "audit_id",
        "practice_id",
        "appointment_id",
        "confirmed_by_user_id",
        "actor_role",
        "authenticated_session_digest",
        "action",
        "status_before",
        "status_after",
        "waiting_area_id_after",
        "cancellation_reason",
        "status_reason_code",
        "confirmed_warning_codes",
        "correlation_id",
        "command_digest",
        "pre_state_version",
        "post_state_version",
    ],
    "receipt_required_fields": [
        "receipt_id",
        "practice_id",
        "actor_user_id",
        "operation_id",
        "target_appointment_id",
        "audit_id",
        "status",
        "waiting_area_id",
        "cancellation_reason",
        "status_reason_code",
        "pre_state_version",
        "post_state_version",
        "canonical_response_digest",
    ],
    "publish_together": [
        "appointment_soft_cancel",
        "attributable_delete_audit",
        "completed_idempotency_receipt",
    ],
    "precommit_failure": "rollback_all_three_and_in_progress_claim",
    "postcommit_delivery_loss": "retry_same_key_for_stored_receipt",
    "post_state_version_rule": "pre_state_version_plus_one",
}

READBACK_CONTRACT = {
    "timing": "after_atomic_commit",
    "transaction_proof": False,
    "purpose": "fresh_display_reconciliation",
    "requires_fresh_authorisation": [
        "practice_scope",
        "appointment_read_action",
        "appointment_resource",
    ],
    "later_revocation": "deny_readback_without_undoing_committed_receipt",
    "source": "authoritative_appointment_read",
}

COMPATIBILITY_INGRESS_POLICY = {
    "admitted_ingress": ["delete-confirm"],
    "rejected_direct_ingress": [
        "raw-delete",
        "status-fallback",
        "event-evidence",
        "model-channel-confirmation",
    ],
    "adapter_may_weaken_confirmation": False,
    "second_cancellation_kernel_allowed": False,
}


def _rejected(reason: str) -> dict[str, Any]:
    return {
        "admission": "admission_rejected",
        "outcome": None,
        "reason": reason,
        "receipt_disclosed": False,
        "planned_effect": False,
    }


def _loser(outcome: str, reason: str) -> dict[str, Any]:
    return {
        "admission": "admitted",
        "outcome": outcome,
        "reason": reason,
        "receipt_disclosed": False,
        "planned_effect": False,
    }


def evaluate_decision(scenario: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one closed decision scenario against the exact precedence."""
    if scenario["ingress"] != "delete_confirm":
        return _rejected("non_dedicated_ingress")
    if scenario["structure"] != "valid":
        return _rejected("structure_invalid")
    if scenario["binding"] != "exact":
        return _rejected(f"binding_mismatch:{scenario['binding']}")
    if scenario["idempotency"] == "missing":
        return _rejected("idempotency_identity_missing")
    if scenario["lock_plan"] != LOCK_ORDER:
        return _rejected("lock_plan_invalid")

    # Target non-disclosure precedes authority and replay disclosure.
    if scenario["target"] in {"missing", "cross_practice"}:
        return _loser("validation_rejected", "target_unavailable")

    # Both current-authority checks: after target lock and with all locks held.
    if not scenario["authority_after_target_lock"]:
        return _loser(
            "authority_revoked",
            f"authority_revoked_after_target_lock:{scenario['authority_loss']}",
        )
    if not scenario["authority_all_locks_held"]:
        return _loser(
            "authority_revoked",
            f"authority_revoked_all_locks_held:{scenario['authority_loss']}",
        )

    # Replay/conflict classification occurs only after authority/target checks.
    if scenario["idempotency"] == "same_digest_completed":
        return {
            "admission": "admitted",
            "outcome": "idempotent_replay",
            "reason": "same_digest_completed",
            "receipt_disclosed": True,
            "planned_effect": False,
        }
    if scenario["idempotency"] == "different_digest":
        return _loser("idempotency_conflict", "same_key_different_digest")

    # First-effect evidence and confirmation checks.
    if scenario["confirmation"] == "missing":
        return _loser("confirmation_required", "separate_confirmation_missing")
    if scenario["confirmation"] == "false":
        return _loser("confirmation_required", "separate_confirmation_false")
    if scenario["confirmation"] == "warning_unacknowledged":
        return _loser("confirmation_required", "warning_acknowledgement_missing")
    if scenario["confirmation"] == "evidence_tampered":
        return _loser("validation_rejected", "signed_evidence_invalid")
    if scenario["confirmation"] == "evidence_expired":
        return _loser("validation_rejected", "signed_evidence_expired")
    if scenario["confirmation"] == "evidence_binding_mismatch":
        return _loser("validation_rejected", "signed_evidence_binding_mismatch")

    # Locked source-state checks.
    if scenario["source"] != "current":
        return _loser(
            "stale_precondition", f"appointment_source_stale:{scenario['source']}"
        )

    # Reason policy for new dedicated ingress.
    if scenario["reason"] == "missing":
        return _loser("validation_rejected", "structured_reason_required")
    if scenario["reason"] == "status_family_code":
        return _loser("validation_rejected", "status_family_reason_rejected")
    if scenario["reason"] == "legacy_unclassified":
        return _loser("validation_rejected", "legacy_reason_code_rejected")
    if scenario["reason"] == "allowlist_invalid":
        return _loser("validation_rejected", "reason_allowlist_invalid")
    if scenario["cancellation_text"] == "too_long":
        return _loser("validation_rejected", "cancellation_reason_too_long")

    return {
        "admission": "admitted",
        "outcome": "committed",
        "reason": "first_effect_planned",
        "receipt_disclosed": False,
        "planned_effect": True,
    }


def _base_state(waiting_area_present: bool = False) -> dict[str, Any]:
    return {
        "appointment_status": "Booked",
        "appointment_version": 7,
        "waiting_area_id": "syn-waiting-area-001" if waiting_area_present else None,
        "status_reason_code": None,
        "cancellation_reason": None,
        "mutation_count": 0,
        "audit_count": 0,
        "completed_receipt_count": 0,
        "receipt_id": None,
        "claim_state": "none",
        "artifacts": None,
    }


def _committed_state(
    cancellation_text: str = "present",
    waiting_area_present: bool = False,
) -> dict[str, Any]:
    cancellation_reason = (
        None if cancellation_text == "null" else FICTIONAL_CANCELLATION_TEXT
    )
    return {
        "appointment_status": "Cancelled",
        "appointment_version": 8,
        "waiting_area_id": None,
        "status_reason_code": "PATIENT_CANCELLED",
        "cancellation_reason": cancellation_reason,
        "mutation_count": 1,
        "audit_count": 1,
        "completed_receipt_count": 1,
        "receipt_id": "syn-receipt-delete-confirm-001",
        "claim_state": "completed",
        "artifacts": {
            "appointment": {
                "practice_id": "syn-practice-001",
                "appointment_id": "syn-appointment-001",
                "status": "Cancelled",
                "waiting_area_id": None,
                "status_reason_code": "PATIENT_CANCELLED",
                "cancellation_reason": cancellation_reason,
                "pre_state_version": 7,
                "post_state_version": 8,
            },
            "audit": {
                "audit_id": "syn-audit-delete-confirm-001",
                "practice_id": "syn-practice-001",
                "appointment_id": "syn-appointment-001",
                "confirmed_by_user_id": "syn-actor-001",
                "actor_role": "Receptionist",
                "authenticated_session_digest": FIXED_DIGESTS["session_digest"],
                "action": "delete",
                "status_before": "Booked",
                "status_after": "Cancelled",
                "waiting_area_id_after": None,
                "status_reason_code": "PATIENT_CANCELLED",
                "cancellation_reason": cancellation_reason,
                "confirmed_warning_codes": (
                    ["waiting_area_cleared"] if waiting_area_present else []
                ),
                "correlation_id": "syn-correlation-delete-confirm-001",
                "command_digest": FIXED_DIGESTS["command_digest"],
                "pre_state_version": 7,
                "post_state_version": 8,
            },
            "receipt": {
                "receipt_id": "syn-receipt-delete-confirm-001",
                "practice_id": "syn-practice-001",
                "actor_user_id": "syn-actor-001",
                "operation_id": CANONICAL_OPERATION_ID,
                "target_appointment_id": "syn-appointment-001",
                "audit_id": "syn-audit-delete-confirm-001",
                "status": "Cancelled",
                "waiting_area_id": None,
                "status_reason_code": "PATIENT_CANCELLED",
                "cancellation_reason": cancellation_reason,
                "pre_state_version": 7,
                "post_state_version": 8,
                "canonical_response_digest": FIXED_DIGESTS["receipt_digest"],
            },
        },
    }


def simulate_schedule(schedule: dict[str, Any]) -> dict[str, Any]:
    """Simulate one transaction schedule with atomic copy/discard semantics."""
    kind = schedule["kind"]
    injection = schedule["injection"]
    trace = list(schedule["trace"])
    waiting_area_present = schedule.get("waiting_area_present", False)
    cancellation_text = schedule.get("cancellation_text", "present")

    if kind == "single_first_effect":
        if injection in {
            "before_locks",
            "after_staged_mutation",
            "after_staged_audit",
            "after_staged_receipt",
        }:
            return {
                "durable_state": _base_state(waiting_area_present),
                "participant_results": ["transaction_rolled_back"],
                "response_delivered": False,
                "readback": {
                    "authorised": False,
                    "status": None,
                    "state_version": None,
                },
                "trace": trace,
            }
        response_delivered = injection != "after_commit_before_response"
        return {
            "durable_state": _committed_state(cancellation_text, waiting_area_present),
            "participant_results": ["committed"],
            "response_delivered": response_delivered,
            "readback": {
                "authorised": True,
                "status": "Cancelled",
                "state_version": 8,
            },
            "trace": trace,
        }

    if kind == "retry_after_lost_response":
        return {
            "durable_state": _committed_state(cancellation_text, waiting_area_present),
            "participant_results": ["committed", "idempotent_replay"],
            "response_delivered": True,
            "readback": {
                "authorised": True,
                "status": "Cancelled",
                "state_version": 8,
            },
            "trace": trace,
        }

    if kind in {
        "concurrent_same_digest",
        "concurrent_different_digest",
        "concurrent_different_key",
        "concurrent_authority_loss",
    }:
        results = {
            "concurrent_same_digest": ["committed", "idempotent_replay"],
            "concurrent_different_digest": ["committed", "idempotency_conflict"],
            "concurrent_different_key": ["committed", "stale_precondition"],
            "concurrent_authority_loss": ["committed", "authority_revoked"],
        }[kind]
        return {
            "durable_state": _committed_state(cancellation_text, waiting_area_present),
            "participant_results": results,
            "response_delivered": True,
            "readback": {
                "authorised": True,
                "status": "Cancelled",
                "state_version": 8,
            },
            "trace": trace,
        }

    if kind == "post_commit_readback":
        policy = schedule.get("readback_policy", "current_authority")
        if policy == "later_revoked":
            readback = {"authorised": False, "status": None, "state_version": None}
        else:
            readback = {
                "authorised": True,
                "status": "Cancelled",
                "state_version": 8,
            }
        return {
            "durable_state": _committed_state(cancellation_text, waiting_area_present),
            "participant_results": ["committed"],
            "response_delivered": True,
            "readback": readback,
            "trace": trace,
        }

    raise ValueError(f"unknown schedule kind: {kind}")


def _decision(
    scenario_id: str,
    *,
    ingress: str = "delete_confirm",
    structure: str = "valid",
    binding: str = "exact",
    lock_plan: list[str] | None = None,
    authority_after_target_lock: bool = True,
    authority_all_locks_held: bool = True,
    authority_loss: str = "none",
    target: str = "exists",
    idempotency: str = "absent",
    confirmation: str = "valid",
    source: str = "current",
    reason: str = "current_cancelled_code",
    cancellation_text: str = "present",
    waiting_area: str = "none",
) -> dict[str, Any]:
    scenario = {
        "id": scenario_id,
        "ingress": ingress,
        "structure": structure,
        "binding": binding,
        "lock_plan": list(lock_plan) if lock_plan is not None else list(LOCK_ORDER),
        "authority_after_target_lock": authority_after_target_lock,
        "authority_all_locks_held": authority_all_locks_held,
        "authority_loss": authority_loss,
        "target": target,
        "idempotency": idempotency,
        "confirmation": confirmation,
        "source": source,
        "reason": reason,
        "cancellation_text": cancellation_text,
        "waiting_area": waiting_area,
    }
    scenario["expected"] = evaluate_decision(scenario)
    return scenario


def _schedule(
    schedule_id: str,
    kind: str,
    injection: str,
    participant_count: int,
    *,
    waiting_area_present: bool = False,
    readback_policy: str = "current_authority",
    cancellation_text: str = "present",
) -> dict[str, Any]:
    schedule = {
        "id": schedule_id,
        "kind": kind,
        "injection": injection,
        "participant_count": participant_count,
        "lock_plan": list(LOCK_ORDER),
        "waiting_area_present": waiting_area_present,
        "readback_policy": readback_policy,
        "cancellation_text": cancellation_text,
        "trace": list(TRACE_STEPS),
    }
    schedule["expected"] = simulate_schedule(schedule)
    return schedule


def build_packet() -> dict[str, Any]:
    decisions = [
        # Clean cancellations with and without a waiting-area assignment.
        _decision("ddc-001-clean-commit-no-waiting-area", waiting_area="none"),
        _decision("ddc-002-clean-commit-with-waiting-area", waiting_area="assigned"),
        # Structured-reason policy and optional free-text bound.
        _decision("ddc-003-reason-missing", reason="missing"),
        _decision("ddc-004-reason-allowlist-invalid", reason="allowlist_invalid"),
        _decision("ddc-005-reason-status-family", reason="status_family_code"),
        _decision("ddc-006-reason-legacy-unclassified", reason="legacy_unclassified"),
        _decision("ddc-007-optional-text-too-long", cancellation_text="too_long"),
        # Confirmation and signed-evidence states.
        _decision("ddc-008-confirmation-missing", confirmation="missing"),
        _decision("ddc-009-confirmation-false", confirmation="false"),
        _decision("ddc-010-confirmation-tampered", confirmation="evidence_tampered"),
        _decision("ddc-011-confirmation-expired", confirmation="evidence_expired"),
        _decision(
            "ddc-012-confirmation-binding-mismatch",
            confirmation="evidence_binding_mismatch",
        ),
        _decision(
            "ddc-013-warning-unacknowledged",
            confirmation="warning_unacknowledged",
        ),
        # Stale source state.
        _decision("ddc-014-stale-version", source="stale_version"),
        _decision("ddc-015-stale-status", source="stale_status"),
        _decision("ddc-016-stale-waiting-area", source="stale_waiting_area"),
        _decision("ddc-017-stale-existing-reason", source="stale_existing_reason"),
        _decision("ddc-018-stale-proposed-reason", source="stale_proposed_reason"),
        # Authority revocation variants before receipt disclosure.
        _decision(
            "ddc-019-inactive-actor",
            authority_after_target_lock=False,
            authority_loss="inactive_actor",
        ),
        _decision(
            "ddc-020-revoked-role",
            authority_all_locks_held=False,
            authority_loss="revoked_role",
        ),
        _decision(
            "ddc-021-revoked-capability",
            authority_all_locks_held=False,
            authority_loss="revoked_capability",
        ),
        # Cross-practice / absent targets, non-disclosing.
        _decision("ddc-022-cross-practice-target", target="cross_practice"),
        _decision("ddc-023-target-absent", target="missing"),
        # Authority loss while waiting precedes replay disclosure.
        _decision(
            "ddc-024-authority-before-replay",
            idempotency="same_digest_completed",
            authority_after_target_lock=False,
            authority_loss="waiting_revoked",
        ),
        # Replay and conflict classification.
        _decision(
            "ddc-025-same-key-same-digest-replay", idempotency="same_digest_completed"
        ),
        _decision("ddc-026-same-key-different-digest", idempotency="different_digest"),
        _decision("ddc-027-idempotency-identity-missing", idempotency="missing"),
        # Non-dedicated ingress families rejected before command evaluation.
        _decision("ddc-028-raw-delete-rejected", ingress="raw_delete"),
        _decision("ddc-029-status-fallback-rejected", ingress="status_fallback"),
        _decision("ddc-030-event-evidence-rejected", ingress="event_evidence"),
        _decision(
            "ddc-031-model-channel-confirmation-rejected",
            ingress="model_channel_confirmation",
        ),
        _decision(
            "ddc-032-raw-delete-target-missing", ingress="raw_delete", target="missing"
        ),
        # Lock-order violations.
        _decision(
            "ddc-033-reordered-locks",
            lock_plan=["practice", "idempotency_record", "appointment"],
        ),
        _decision(
            "ddc-034-schedule-domain-not-skipped",
            lock_plan=[
                "practice",
                "schedule_domain",
                "appointment",
                "idempotency_record",
            ],
        ),
        # Structural and binding failures.
        _decision("ddc-035-structure-rejected", structure="invalid"),
        _decision("ddc-036-binding-session-mismatch", binding="session_mismatch"),
        _decision("ddc-037-binding-practice-mismatch", binding="practice_mismatch"),
        _decision("ddc-038-binding-actor-mismatch", binding="actor_mismatch"),
        _decision("ddc-039-binding-operation-mismatch", binding="operation_mismatch"),
        _decision("ddc-040-binding-target-mismatch", binding="target_mismatch"),
        _decision("ddc-041-binding-state-mismatch", binding="state_mismatch"),
        _decision(
            "ddc-042-binding-waiting-area-mismatch", binding="waiting_area_mismatch"
        ),
        _decision(
            "ddc-043-binding-existing-reason-mismatch",
            binding="existing_reason_mismatch",
        ),
        _decision(
            "ddc-044-binding-proposed-reason-mismatch",
            binding="proposed_reason_mismatch",
        ),
        _decision("ddc-045-binding-digest-mismatch", binding="digest_mismatch"),
        _decision("ddc-046-optional-null-text-commit", cancellation_text="null"),
    ]
    schedules = [
        _schedule(
            "ddt-001-clean-commit-no-waiting-area", "single_first_effect", "none", 1
        ),
        _schedule(
            "ddt-002-clean-commit-with-waiting-area",
            "single_first_effect",
            "none",
            1,
            waiting_area_present=True,
        ),
        _schedule(
            "ddt-003-failure-before-locks", "single_first_effect", "before_locks", 1
        ),
        _schedule(
            "ddt-004-failure-after-mutation",
            "single_first_effect",
            "after_staged_mutation",
            1,
        ),
        _schedule(
            "ddt-005-failure-after-audit",
            "single_first_effect",
            "after_staged_audit",
            1,
        ),
        _schedule(
            "ddt-006-failure-after-receipt",
            "single_first_effect",
            "after_staged_receipt",
            1,
        ),
        _schedule(
            "ddt-007-response-loss-after-commit",
            "single_first_effect",
            "after_commit_before_response",
            1,
        ),
        _schedule(
            "ddt-008-retry-after-lost-response", "retry_after_lost_response", "none", 2
        ),
        _schedule("ddt-009-same-key-same-digest", "concurrent_same_digest", "none", 2),
        _schedule(
            "ddt-010-same-key-different-digest",
            "concurrent_different_digest",
            "none",
            2,
        ),
        _schedule(
            "ddt-011-different-key-overlap", "concurrent_different_key", "none", 2
        ),
        _schedule(
            "ddt-012-authority-loss-while-waiting",
            "concurrent_authority_loss",
            "none",
            2,
        ),
        _schedule(
            "ddt-013-readback-current-authority",
            "post_commit_readback",
            "none",
            1,
            readback_policy="current_authority",
        ),
        _schedule(
            "ddt-014-readback-denied-after-revocation",
            "post_commit_readback",
            "none",
            1,
            readback_policy="later_revoked",
        ),
        _schedule(
            "ddt-015-clean-commit-null-cancellation-text",
            "single_first_effect",
            "none",
            1,
            cancellation_text="null",
        ),
    ]
    return {
        "schema_version": "raisa.delete_confirm_conditional_command_kernel.v1",
        "artifact_kind": "provider_free_unmounted_authored_synthetic_contract",
        "source_bindings": copy.deepcopy(SOURCE_BINDINGS),
        "canonical_operation_id": CANONICAL_OPERATION_ID,
        "canonical_ingress": CANONICAL_INGRESS,
        "global_lock_order": list(GLOBAL_LOCK_ORDER),
        "kernel_lock_plan": list(LOCK_ORDER),
        "unused_lock_rule": UNUSED_LOCK_RULE,
        "cancelled_reason_codes": list(CANCELLED_REASON_CODES),
        "max_cancellation_reason_length": MAX_FREE_TEXT_LENGTH,
        "outcome_vocabulary": list(OUTCOMES),
        "fixed_timestamps_utc": copy.deepcopy(FIXED_TIMESTAMPS_UTC),
        "fixed_digests": copy.deepcopy(FIXED_DIGESTS),
        "authority_contract": copy.deepcopy(AUTHORITY_CONTRACT),
        "signed_evidence_contract": copy.deepcopy(SIGNED_EVIDENCE_CONTRACT),
        "reason_policy": copy.deepcopy(REASON_POLICY),
        "idempotency_contract": copy.deepcopy(IDEMPOTENCY_CONTRACT),
        "transaction_contract": copy.deepcopy(TRANSACTION_CONTRACT),
        "atomic_effect_contract": copy.deepcopy(ATOMIC_EFFECT_CONTRACT),
        "readback_contract": copy.deepcopy(READBACK_CONTRACT),
        "compatibility_ingress_policy": copy.deepcopy(COMPATIBILITY_INGRESS_POLICY),
        "next_gate": "provider-free-unmounted-delete-confirm-physical-representability-review",
        "decision_scenarios": decisions,
        "transaction_schedules": schedules,
        "effect_boundary": copy.deepcopy(EFFECT_BOUNDARY),
    }


def _string_array() -> dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}}


def _expected_decision_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "admission",
            "outcome",
            "reason",
            "receipt_disclosed",
            "planned_effect",
        ],
        "properties": {
            "admission": {"enum": ["admitted", "admission_rejected"]},
            "outcome": {"type": ["string", "null"]},
            "reason": {"type": "string"},
            "receipt_disclosed": {"type": "boolean"},
            "planned_effect": {"type": "boolean"},
        },
    }


def _artifact_schema(required_fields: list[str]) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "practice_id": {"const": "syn-practice-001"},
        "appointment_id": {"const": "syn-appointment-001"},
        "status": {"const": "Cancelled"},
        "waiting_area_id": {"const": None},
        "cancellation_reason": {
            "enum": [None, FICTIONAL_CANCELLATION_TEXT],
        },
        "status_reason_code": {"const": "PATIENT_CANCELLED"},
        "pre_state_version": {"const": 7},
        "post_state_version": {"const": 8},
        "audit_id": {"const": "syn-audit-delete-confirm-001"},
        "confirmed_by_user_id": {"const": "syn-actor-001"},
        "actor_role": {"const": "Receptionist"},
        "authenticated_session_digest": {"const": FIXED_DIGESTS["session_digest"]},
        "action": {"const": "delete"},
        "status_before": {"const": "Booked"},
        "status_after": {"const": "Cancelled"},
        "waiting_area_id_after": {"const": None},
        "confirmed_warning_codes": {
            "enum": [[], ["waiting_area_cleared"]],
        },
        "correlation_id": {"const": "syn-correlation-delete-confirm-001"},
        "command_digest": {"const": FIXED_DIGESTS["command_digest"]},
        "receipt_id": {"const": "syn-receipt-delete-confirm-001"},
        "actor_user_id": {"const": "syn-actor-001"},
        "operation_id": {"const": CANONICAL_OPERATION_ID},
        "target_appointment_id": {"const": "syn-appointment-001"},
        "canonical_response_digest": {"const": FIXED_DIGESTS["receipt_digest"]},
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(required_fields),
        "minProperties": len(required_fields),
        "maxProperties": len(required_fields),
        "properties": properties,
    }


def _state_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "appointment_status",
            "appointment_version",
            "waiting_area_id",
            "status_reason_code",
            "cancellation_reason",
            "mutation_count",
            "audit_count",
            "completed_receipt_count",
            "receipt_id",
            "claim_state",
            "artifacts",
        ],
        "properties": {
            "appointment_status": {"type": "string"},
            "appointment_version": {"type": "integer"},
            "waiting_area_id": {"type": ["string", "null"]},
            "status_reason_code": {"type": ["string", "null"]},
            "cancellation_reason": {"type": ["string", "null"]},
            "mutation_count": {"type": "integer"},
            "audit_count": {"type": "integer"},
            "completed_receipt_count": {"type": "integer"},
            "receipt_id": {"type": ["string", "null"]},
            "claim_state": {"type": "string"},
            "artifacts": {
                "oneOf": [
                    {"type": "null"},
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["appointment", "audit", "receipt"],
                        "properties": {
                            "appointment": _artifact_schema(
                                ATOMIC_EFFECT_CONTRACT["appointment_required_fields"]
                            ),
                            "audit": _artifact_schema(
                                ATOMIC_EFFECT_CONTRACT["audit_required_fields"]
                            ),
                            "receipt": _artifact_schema(
                                ATOMIC_EFFECT_CONTRACT["receipt_required_fields"]
                            ),
                        },
                    },
                ]
            },
        },
    }


def _expected_schedule_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "durable_state",
            "participant_results",
            "response_delivered",
            "readback",
            "trace",
        ],
        "properties": {
            "durable_state": _state_schema(),
            "participant_results": _string_array(),
            "response_delivered": {"type": "boolean"},
            "readback": {
                "type": "object",
                "additionalProperties": False,
                "required": ["authorised", "status", "state_version"],
                "properties": {
                    "authorised": {"type": "boolean"},
                    "status": {"type": ["string", "null"]},
                    "state_version": {"type": ["integer", "null"]},
                },
            },
            "trace": _string_array(),
        },
    }


def build_schema() -> dict[str, Any]:
    string_array = _string_array()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "artifact_kind",
            "source_bindings",
            "canonical_operation_id",
            "canonical_ingress",
            "global_lock_order",
            "kernel_lock_plan",
            "unused_lock_rule",
            "cancelled_reason_codes",
            "max_cancellation_reason_length",
            "outcome_vocabulary",
            "fixed_timestamps_utc",
            "fixed_digests",
            "authority_contract",
            "signed_evidence_contract",
            "reason_policy",
            "idempotency_contract",
            "transaction_contract",
            "atomic_effect_contract",
            "readback_contract",
            "compatibility_ingress_policy",
            "next_gate",
            "decision_scenarios",
            "transaction_schedules",
            "effect_boundary",
        ],
        "properties": {
            "schema_version": {
                "const": "raisa.delete_confirm_conditional_command_kernel.v1"
            },
            "artifact_kind": {
                "const": "provider_free_unmounted_authored_synthetic_contract"
            },
            "source_bindings": {
                "type": "array",
                "minItems": 7,
                "maxItems": 7,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["path", "sha256"],
                    "properties": {
                        "path": {"type": "string"},
                        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    },
                },
            },
            "canonical_operation_id": {"const": CANONICAL_OPERATION_ID},
            "canonical_ingress": {"const": CANONICAL_INGRESS},
            "global_lock_order": string_array,
            "kernel_lock_plan": string_array,
            "unused_lock_rule": {"const": UNUSED_LOCK_RULE},
            "cancelled_reason_codes": string_array,
            "max_cancellation_reason_length": {"const": MAX_FREE_TEXT_LENGTH},
            "outcome_vocabulary": string_array,
            "fixed_timestamps_utc": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "proposal_generated_at",
                    "signed_at",
                    "expires_at",
                    "confirmed_at",
                    "committed_at",
                ],
                "properties": {
                    "proposal_generated_at": {"const": "2026-08-15T01:50:49Z"},
                    "signed_at": {"const": "2026-08-15T01:50:49Z"},
                    "expires_at": {"const": "2026-08-15T02:10:49Z"},
                    "confirmed_at": {"const": "2026-08-15T01:55:04Z"},
                    "committed_at": {"const": "2026-08-15T01:55:04Z"},
                },
            },
            "fixed_digests": {
                "type": "object",
                "additionalProperties": False,
                "minProperties": len(FIXED_DIGESTS),
                "maxProperties": len(FIXED_DIGESTS),
                "patternProperties": {
                    "^[a-z_]+$": {"type": "string", "pattern": "^[0-9a-f]{64}$"}
                },
            },
            "authority_contract": {"const": AUTHORITY_CONTRACT},
            "signed_evidence_contract": {"const": SIGNED_EVIDENCE_CONTRACT},
            "reason_policy": {"const": REASON_POLICY},
            "idempotency_contract": {"const": IDEMPOTENCY_CONTRACT},
            "transaction_contract": {"const": TRANSACTION_CONTRACT},
            "atomic_effect_contract": {"const": ATOMIC_EFFECT_CONTRACT},
            "readback_contract": {"const": READBACK_CONTRACT},
            "compatibility_ingress_policy": {"const": COMPATIBILITY_INGRESS_POLICY},
            "next_gate": {
                "const": "provider-free-unmounted-delete-confirm-physical-representability-review"
            },
            "decision_scenarios": {
                "type": "array",
                "minItems": 24,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "ingress",
                        "structure",
                        "binding",
                        "lock_plan",
                        "authority_after_target_lock",
                        "authority_all_locks_held",
                        "authority_loss",
                        "target",
                        "idempotency",
                        "confirmation",
                        "source",
                        "reason",
                        "cancellation_text",
                        "waiting_area",
                        "expected",
                    ],
                    "properties": {
                        "id": {"type": "string", "pattern": "^ddc-[0-9]{3}-"},
                        "ingress": {
                            "enum": [
                                "delete_confirm",
                                "raw_delete",
                                "status_fallback",
                                "event_evidence",
                                "model_channel_confirmation",
                            ]
                        },
                        "structure": {"enum": ["valid", "invalid"]},
                        "binding": {"enum": BINDING_STATES},
                        "lock_plan": string_array,
                        "authority_after_target_lock": {"type": "boolean"},
                        "authority_all_locks_held": {"type": "boolean"},
                        "authority_loss": {
                            "enum": [
                                "none",
                                "inactive_actor",
                                "revoked_role",
                                "revoked_capability",
                                "waiting_revoked",
                            ]
                        },
                        "target": {"enum": ["exists", "missing", "cross_practice"]},
                        "idempotency": {"enum": IDEMPOTENCY_STATES},
                        "confirmation": {"enum": CONFIRMATION_STATES},
                        "source": {"enum": SOURCE_STATES},
                        "reason": {"enum": REASON_STATES},
                        "cancellation_text": {"enum": CANCELLATION_TEXT_STATES},
                        "waiting_area": {"enum": ["none", "assigned"]},
                        "expected": _expected_decision_schema(),
                    },
                },
            },
            "transaction_schedules": {
                "type": "array",
                "minItems": 12,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "kind",
                        "injection",
                        "participant_count",
                        "lock_plan",
                        "waiting_area_present",
                        "readback_policy",
                        "cancellation_text",
                        "trace",
                        "expected",
                    ],
                    "properties": {
                        "id": {"type": "string", "pattern": "^ddt-[0-9]{3}-"},
                        "kind": {
                            "enum": [
                                "single_first_effect",
                                "retry_after_lost_response",
                                "concurrent_same_digest",
                                "concurrent_different_digest",
                                "concurrent_different_key",
                                "concurrent_authority_loss",
                                "post_commit_readback",
                            ]
                        },
                        "injection": {
                            "enum": [
                                "none",
                                "before_locks",
                                "after_staged_mutation",
                                "after_staged_audit",
                                "after_staged_receipt",
                                "after_commit_before_response",
                            ]
                        },
                        "participant_count": {"type": "integer", "minimum": 1},
                        "lock_plan": string_array,
                        "waiting_area_present": {"type": "boolean"},
                        "readback_policy": {
                            "enum": ["current_authority", "later_revoked"]
                        },
                        "cancellation_text": {"enum": ["present", "null"]},
                        "trace": string_array,
                        "expected": _expected_schedule_schema(),
                    },
                },
            },
            "effect_boundary": {
                "type": "object",
                "additionalProperties": False,
                "minProperties": 10,
                "maxProperties": 10,
                "patternProperties": {"^[a-z_]+$": {"const": False}},
            },
        },
    }


def validate_packet(packet: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [
        error.message for error in Draft202012Validator(schema).iter_errors(packet)
    ]
    if errors:
        return sorted(errors)

    if packet["source_bindings"] != SOURCE_BINDINGS:
        errors.append("source_binding_set_mismatch")
    for binding in packet["source_bindings"]:
        try:
            actual = _sha256(ROOT / binding["path"])
        except OSError:
            errors.append(f"source_unreadable:{binding['path']}")
            continue
        if actual != binding["sha256"]:
            errors.append(f"source_hash_mismatch:{binding['path']}")
    if packet["global_lock_order"] != GLOBAL_LOCK_ORDER:
        errors.append("global_lock_order_mismatch")
    if packet["kernel_lock_plan"] != LOCK_ORDER:
        errors.append("kernel_lock_plan_mismatch")
    if packet["unused_lock_rule"] != UNUSED_LOCK_RULE:
        errors.append("unused_lock_rule_mismatch")
    if packet["cancelled_reason_codes"] != CANCELLED_REASON_CODES:
        errors.append("cancelled_reason_codes_mismatch")
    if packet["max_cancellation_reason_length"] != MAX_FREE_TEXT_LENGTH:
        errors.append("max_cancellation_reason_length_mismatch")
    if packet["outcome_vocabulary"] != OUTCOMES:
        errors.append("outcome_vocabulary_mismatch")
    if packet["fixed_digests"] != FIXED_DIGESTS:
        errors.append("fixed_digests_mismatch")
    closed_contracts = {
        "authority_contract": AUTHORITY_CONTRACT,
        "signed_evidence_contract": SIGNED_EVIDENCE_CONTRACT,
        "reason_policy": REASON_POLICY,
        "idempotency_contract": IDEMPOTENCY_CONTRACT,
        "transaction_contract": TRANSACTION_CONTRACT,
        "atomic_effect_contract": ATOMIC_EFFECT_CONTRACT,
        "readback_contract": READBACK_CONTRACT,
        "compatibility_ingress_policy": COMPATIBILITY_INGRESS_POLICY,
    }
    for name, expected_contract in closed_contracts.items():
        if packet[name] != expected_contract:
            errors.append(f"{name}_mismatch")
    try:
        timestamps = {
            name: datetime.fromisoformat(value.replace("Z", "+00:00"))
            for name, value in packet["fixed_timestamps_utc"].items()
        }
        if not (
            timestamps["proposal_generated_at"]
            <= timestamps["signed_at"]
            <= timestamps["confirmed_at"]
            <= timestamps["expires_at"]
        ):
            errors.append("evidence_freshness_interval_invalid")
        if timestamps["committed_at"] < timestamps["confirmed_at"]:
            errors.append("commit_precedes_confirmation")
    except (KeyError, TypeError, ValueError):
        errors.append("fixed_timestamp_parse_invalid")
    if any(packet["effect_boundary"].values()):
        errors.append("effect_boundary_open")

    decision_ids = [scenario["id"] for scenario in packet["decision_scenarios"]]
    if len(decision_ids) != len(set(decision_ids)):
        errors.append("decision_id_duplicate")
    has_after_target_failure = False
    has_all_locks_failure = False
    for scenario in packet["decision_scenarios"]:
        if not scenario["authority_after_target_lock"]:
            has_after_target_failure = True
        if not scenario["authority_all_locks_held"]:
            has_all_locks_failure = True
        if evaluate_decision(scenario) != scenario["expected"]:
            errors.append(f"decision_mismatch:{scenario['id']}")
        expected = scenario["expected"]
        if (
            expected["admission"] == "admission_rejected"
            and expected["outcome"] is not None
        ):
            errors.append(f"rejected_decision_has_outcome:{scenario['id']}")
        if expected["planned_effect"] != (expected["outcome"] == "committed"):
            errors.append(f"effect_not_commit_only:{scenario['id']}")
        if (
            not scenario["authority_after_target_lock"]
            or not scenario["authority_all_locks_held"]
        ):
            if expected["receipt_disclosed"]:
                errors.append(f"revoked_authority_receipt_disclosed:{scenario['id']}")
        if scenario["ingress"] != "delete_confirm":
            if expected["admission"] != "admission_rejected":
                errors.append(f"nondedicated_ingress_admitted:{scenario['id']}")
            if expected["planned_effect"]:
                errors.append(f"nondedicated_ingress_effect:{scenario['id']}")
    if not has_after_target_failure:
        errors.append("missing_authority_after_target_lock_failure_scenario")
    if not has_all_locks_failure:
        errors.append("missing_authority_all_locks_held_failure_scenario")

    null_text = next(
        (
            scenario
            for scenario in packet["decision_scenarios"]
            if scenario["id"] == "ddc-046-optional-null-text-commit"
        ),
        None,
    )
    if null_text is None or null_text["expected"]["outcome"] != "committed":
        errors.append("missing_optional_null_text_commit_scenario")

    replay = next(
        (
            s
            for s in packet["decision_scenarios"]
            if s["id"] == "ddc-024-authority-before-replay"
        ),
        None,
    )
    if replay is None:
        errors.append("missing_authority_before_replay_scenario")
    elif replay["expected"]["outcome"] != "authority_revoked":
        errors.append("authority_before_replay_not_revoked")
    elif replay["expected"]["receipt_disclosed"]:
        errors.append("authority_before_replay_disclosed_receipt")

    schedule_ids = [schedule["id"] for schedule in packet["transaction_schedules"]]
    if len(schedule_ids) != len(set(schedule_ids)):
        errors.append("schedule_id_duplicate")
    for schedule in packet["transaction_schedules"]:
        if schedule["lock_plan"] != LOCK_ORDER:
            errors.append(f"schedule_lock_plan_mismatch:{schedule['id']}")
        if simulate_schedule(schedule) != schedule["expected"]:
            errors.append(f"schedule_mismatch:{schedule['id']}")
        trace = schedule["trace"]
        try:
            positions = [trace.index(step) for step in TRACE_STEPS[:6]]
            if positions != sorted(positions):
                errors.append(f"schedule_trace_order:{schedule['id']}")
        except ValueError:
            errors.append(f"schedule_trace_incomplete:{schedule['id']}")
        state = schedule["expected"]["durable_state"]
        if state["claim_state"] == "completed":
            artifacts = state["artifacts"]
            if artifacts is None:
                errors.append(f"completed_without_artifacts:{schedule['id']}")
                continue
            exact_field_sets = {
                "appointment": set(
                    ATOMIC_EFFECT_CONTRACT["appointment_required_fields"]
                ),
                "audit": set(ATOMIC_EFFECT_CONTRACT["audit_required_fields"]),
                "receipt": set(ATOMIC_EFFECT_CONTRACT["receipt_required_fields"]),
            }
            for artifact_name, expected_fields in exact_field_sets.items():
                if set(artifacts[artifact_name]) != expected_fields:
                    errors.append(
                        f"artifact_field_set_mismatch:{schedule['id']}:{artifact_name}"
                    )
            reasons = {
                artifacts["appointment"]["cancellation_reason"],
                artifacts["audit"]["cancellation_reason"],
                artifacts["receipt"]["cancellation_reason"],
            }
            if len(reasons) != 1:
                errors.append(f"cross_artifact_reason_mismatch:{schedule['id']}")
            codes = {
                artifacts["appointment"]["status_reason_code"],
                artifacts["audit"]["status_reason_code"],
                artifacts["receipt"]["status_reason_code"],
            }
            if len(codes) != 1:
                errors.append(f"cross_artifact_reason_code_mismatch:{schedule['id']}")
            if (
                artifacts["appointment"]["waiting_area_id"] is not None
                or artifacts["audit"]["waiting_area_id_after"] is not None
                or artifacts["receipt"]["waiting_area_id"] is not None
            ):
                errors.append(f"waiting_area_not_cleared:{schedule['id']}")
            if not (
                artifacts["appointment"]["practice_id"]
                == artifacts["audit"]["practice_id"]
                == artifacts["receipt"]["practice_id"]
                == "syn-practice-001"
            ):
                errors.append(f"cross_artifact_practice_mismatch:{schedule['id']}")
            if not (
                artifacts["appointment"]["appointment_id"]
                == artifacts["audit"]["appointment_id"]
                == artifacts["receipt"]["target_appointment_id"]
                == "syn-appointment-001"
            ):
                errors.append(f"cross_artifact_target_mismatch:{schedule['id']}")
            if artifacts["audit"]["audit_id"] != artifacts["receipt"]["audit_id"]:
                errors.append(
                    f"cross_artifact_audit_identity_mismatch:{schedule['id']}"
                )
            pre_versions = {
                artifacts[name]["pre_state_version"]
                for name in ("appointment", "audit", "receipt")
            }
            post_versions = {
                artifacts[name]["post_state_version"]
                for name in ("appointment", "audit", "receipt")
            }
            if len(pre_versions) != 1 or len(post_versions) != 1:
                errors.append(f"cross_artifact_version_mismatch:{schedule['id']}")
            elif next(iter(post_versions)) != next(iter(pre_versions)) + 1:
                errors.append(f"post_state_version_not_incremented:{schedule['id']}")
            if (
                artifacts["appointment"]["status"] != "Cancelled"
                or artifacts["audit"]["status_before"] != "Booked"
                or artifacts["audit"]["status_after"] != "Cancelled"
                or artifacts["audit"]["action"] != "delete"
                or artifacts["receipt"]["status"] != "Cancelled"
            ):
                errors.append(f"atomic_status_or_action_mismatch:{schedule['id']}")

    null_text_schedule = next(
        (
            schedule
            for schedule in packet["transaction_schedules"]
            if schedule["id"] == "ddt-015-clean-commit-null-cancellation-text"
        ),
        None,
    )
    if null_text_schedule is None:
        errors.append("missing_optional_null_text_transaction_schedule")
    else:
        artifacts = null_text_schedule["expected"]["durable_state"]["artifacts"]
        if artifacts is None or any(
            artifacts[name]["cancellation_reason"] is not None
            for name in ("appointment", "audit", "receipt")
        ):
            errors.append("optional_null_text_not_preserved")

    return sorted(set(errors))


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str, path: tuple[Any, ...], value: Any) -> None:
        candidate = copy.deepcopy(packet)
        cursor: Any = candidate
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = value
        mutations.append((name, candidate))

    def decision_index(scenario_id: str) -> int:
        for index, scenario in enumerate(packet["decision_scenarios"]):
            if scenario["id"] == scenario_id:
                return index
        raise KeyError(scenario_id)

    def schedule_index(schedule_id: str) -> int:
        for index, schedule in enumerate(packet["transaction_schedules"]):
            if schedule["id"] == schedule_id:
                return index
        raise KeyError(schedule_id)

    # Packet-level constants and source bindings.
    mutate("operation_id", ("canonical_operation_id",), "rawDeleteAppointment")
    mutate("ingress_family", ("canonical_ingress",), "status-confirm")
    mutate(
        "global_order",
        ("global_lock_order",),
        list(reversed(packet["global_lock_order"])),
    )
    mutate(
        "kernel_lock_plan",
        ("kernel_lock_plan",),
        ["practice", "idempotency_record", "appointment"],
    )
    mutate("unused_lock_rule", ("unused_lock_rule",), "include_schedule_domain")
    mutate("outcome_vocabulary", ("outcome_vocabulary",), OUTCOMES[:-1])
    mutate(
        "reason_codes",
        ("cancelled_reason_codes",),
        CANCELLED_REASON_CODES + ["LEGACY_UNCLASSIFIED"],
    )
    mutate("max_reason_length", ("max_cancellation_reason_length",), 501)
    mutate("next_gate", ("next_gate",), "runtime-convergence-review")
    mutate("source_hash", ("source_bindings", 0, "sha256"), "0" * 64)
    mutate("source_path", ("source_bindings", 0, "path"), "app/routers/appointments.py")
    mutate(
        "expiry_before_confirmation",
        ("fixed_timestamps_utc", "expires_at"),
        "2026-08-15T01:52:49Z",
    )
    mutate(
        "authority_roles_widened",
        ("authority_contract", "allowed_actor_roles"),
        ALLOWED_ACTOR_ROLES + ["ExternalDelegate"],
    )
    mutate(
        "authority_capability_widened",
        ("authority_contract", "required_capability"),
        "appointment.*",
    )
    evidence_fields = SIGNED_EVIDENCE_CONTRACT["required_fields"]
    mutate(
        "evidence_session_binding_removed",
        ("signed_evidence_contract", "required_fields"),
        [field for field in evidence_fields if field != "authenticated_session_digest"],
    )
    mutate(
        "optional_text_made_required",
        ("reason_policy", "cancellation_reason", "required"),
        True,
    )
    mutate(
        "receipt_disclosure_without_authority",
        ("idempotency_contract", "receipt_disclosure_requires_current_authority"),
        False,
    )
    mutate(
        "authority_fence_claimed_physical",
        ("transaction_contract", "authority_fence_physical_mapping_proven"),
        True,
    )
    mutate(
        "atomic_audit_identity_removed",
        ("atomic_effect_contract", "audit_required_fields"),
        [
            field
            for field in ATOMIC_EFFECT_CONTRACT["audit_required_fields"]
            if field != "authenticated_session_digest"
        ],
    )
    mutate(
        "readback_made_transaction_proof",
        ("readback_contract", "transaction_proof"),
        True,
    )
    mutate(
        "status_fallback_admitted",
        ("compatibility_ingress_policy", "admitted_ingress"),
        ["delete-confirm", "status-fallback"],
    )
    for key in packet["effect_boundary"]:
        mutate(f"effect_{key}", ("effect_boundary", key), True)

    # Decision expected-outcome and admission mutations.
    i = decision_index("ddc-001-clean-commit-no-waiting-area")
    mutate(
        "commit_expected_replay",
        ("decision_scenarios", i, "expected", "outcome"),
        "idempotent_replay",
    )
    mutate(
        "commit_no_effect",
        ("decision_scenarios", i, "expected", "planned_effect"),
        False,
    )
    i = decision_index("ddc-025-same-key-same-digest-replay")
    mutate(
        "replay_effect", ("decision_scenarios", i, "expected", "planned_effect"), True
    )
    mutate(
        "replay_hidden",
        ("decision_scenarios", i, "expected", "receipt_disclosed"),
        False,
    )
    i = decision_index("ddc-024-authority-before-replay")
    mutate(
        "authority_replay",
        ("decision_scenarios", i, "expected", "outcome"),
        "idempotent_replay",
    )
    mutate(
        "authority_disclosure",
        ("decision_scenarios", i, "expected", "receipt_disclosed"),
        True,
    )
    i = decision_index("ddc-003-reason-missing")
    mutate(
        "reason_missing_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-004-reason-allowlist-invalid")
    mutate(
        "reason_allowlist_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-006-reason-legacy-unclassified")
    mutate(
        "reason_legacy_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-007-optional-text-too-long")
    mutate(
        "reason_text_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-008-confirmation-missing")
    mutate(
        "confirmation_missing_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-010-confirmation-tampered")
    mutate(
        "confirmation_tampered_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-011-confirmation-expired")
    mutate(
        "confirmation_expired_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-012-confirmation-binding-mismatch")
    mutate(
        "confirmation_binding_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-014-stale-version")
    mutate(
        "stale_version_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-022-cross-practice-target")
    mutate(
        "cross_practice_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-023-target-absent")
    mutate(
        "target_absent_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-027-idempotency-identity-missing")
    mutate(
        "idem_missing_admitted",
        ("decision_scenarios", i, "expected", "admission"),
        "admitted",
    )
    i = decision_index("ddc-028-raw-delete-rejected")
    mutate(
        "raw_delete_admitted",
        ("decision_scenarios", i, "expected", "admission"),
        "admitted",
    )
    mutate(
        "raw_delete_commit",
        ("decision_scenarios", i, "expected", "outcome"),
        "committed",
    )
    i = decision_index("ddc-033-reordered-locks")
    mutate(
        "reordered_locks_admitted",
        ("decision_scenarios", i, "expected", "admission"),
        "admitted",
    )
    i = decision_index("ddc-034-schedule-domain-not-skipped")
    mutate(
        "schedule_domain_admitted",
        ("decision_scenarios", i, "expected", "admission"),
        "admitted",
    )

    # Schedule durable-state and participant-result mutations.
    i = schedule_index("ddt-003-failure-before-locks")
    mutate(
        "rollback_mutation",
        ("transaction_schedules", i, "expected", "durable_state", "mutation_count"),
        1,
    )
    i = schedule_index("ddt-004-failure-after-mutation")
    mutate(
        "rollback_audit",
        ("transaction_schedules", i, "expected", "durable_state", "audit_count"),
        1,
    )
    i = schedule_index("ddt-005-failure-after-audit")
    mutate(
        "rollback_receipt",
        (
            "transaction_schedules",
            i,
            "expected",
            "durable_state",
            "completed_receipt_count",
        ),
        1,
    )
    i = schedule_index("ddt-006-failure-after-receipt")
    mutate(
        "rollback_claim",
        ("transaction_schedules", i, "expected", "durable_state", "claim_state"),
        "completed",
    )
    i = schedule_index("ddt-007-response-loss-after-commit")
    mutate(
        "lost_response_rollback",
        ("transaction_schedules", i, "expected", "durable_state", "mutation_count"),
        0,
    )
    i = schedule_index("ddt-008-retry-after-lost-response")
    mutate(
        "retry_second_mutation",
        ("transaction_schedules", i, "expected", "durable_state", "mutation_count"),
        2,
    )
    mutate(
        "retry_second_audit",
        ("transaction_schedules", i, "expected", "durable_state", "audit_count"),
        2,
    )
    i = schedule_index("ddt-009-same-key-same-digest")
    mutate(
        "same_digest_second_audit",
        ("transaction_schedules", i, "expected", "durable_state", "audit_count"),
        2,
    )
    i = schedule_index("ddt-010-same-key-different-digest")
    mutate(
        "different_digest_second_commit",
        ("transaction_schedules", i, "expected", "participant_results", 1),
        "committed",
    )
    i = schedule_index("ddt-011-different-key-overlap")
    mutate(
        "different_key_second_commit",
        ("transaction_schedules", i, "expected", "participant_results", 1),
        "committed",
    )
    i = schedule_index("ddt-012-authority-loss-while-waiting")
    mutate(
        "authority_loss_second_replay",
        ("transaction_schedules", i, "expected", "participant_results", 1),
        "idempotent_replay",
    )
    i = schedule_index("ddt-014-readback-denied-after-revocation")
    mutate(
        "readback_denied_reversed",
        ("transaction_schedules", i, "expected", "readback", "authorised"),
        True,
    )
    i = schedule_index("ddt-002-clean-commit-with-waiting-area")
    mutate(
        "waiting_area_not_cleared",
        (
            "transaction_schedules",
            i,
            "expected",
            "durable_state",
            "artifacts",
            "appointment",
            "waiting_area_id",
        ),
        "syn-waiting-area-001",
    )
    i = schedule_index("ddt-015-clean-commit-null-cancellation-text")
    mutate(
        "optional_null_text_materialized",
        (
            "transaction_schedules",
            i,
            "expected",
            "durable_state",
            "artifacts",
            "receipt",
            "cancellation_reason",
        ),
        FICTIONAL_CANCELLATION_TEXT,
    )

    return mutations


def build_report(packet: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    canonical_errors = validate_packet(packet, schema)
    admitted_mutations = [
        name
        for name, candidate in hostile_mutations(packet)
        if not validate_packet(candidate, schema)
    ]
    return {
        "schema_version": "raisa.delete_confirm_conditional_command_kernel.evidence.v1",
        "status": "passed"
        if not canonical_errors and not admitted_mutations
        else "failed",
        "canonical_errors": canonical_errors,
        "decision_scenario_count": len(packet["decision_scenarios"]),
        "transaction_schedule_count": len(packet["transaction_schedules"]),
        "hostile_mutation_count": len(hostile_mutations(packet)),
        "admitted_hostile_mutations": admitted_mutations,
        "effect_boundary": packet["effect_boundary"],
        "runtime_or_command_authority_granted": False,
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    packet = build_packet()
    schema = build_schema()
    report = build_report(packet, schema)
    if args.write:
        _write(PACKET_PATH, packet)
        _write(SCHEMA_PATH, schema)
        _write(EVIDENCE_PATH, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
