"""Read-only Bernie Diary Capability Manifest.

The manifest is a compact, source-derived description of the native diary
language that Bernie may read when translating receptionist instructions. It is
not executable policy, not an authorization layer, and not a prompt that grants
write authority. Runtime guards remain in the diary domain, signed confirmation
routes, RBAC, and audit logging.
"""

from __future__ import annotations

from typing import Any, Literal

from app.models.appointments import AppointmentStatus, BookingChannel
from app.schemas.appointments import STATUS_REASON_CODES, STATUS_SPECIFIC_REASON_CODE_POLICY
from app.services.bernie.session import (
    CLIENT_EVENT_TRANSITIONS,
    SERVER_ADVANCE_TARGETS,
    TERMINAL_STATES,
    TRANSIENT_STATES,
    BernieSessionEventType,
    BernieSessionState,
)
from app.services.diary.capabilities import BERNIE_CAPABILITY_REGISTRY, BernieCapabilityTier
from app.services.diary.confirm_actions import DIARY_CONFIRM_ACTIONS
from app.services.diary.envelopes import (
    DiaryActionAuthor,
    DiaryActionChannel,
    DiaryActionConfirmation,
    DiaryActionIntent,
    DiaryActionProposal,
    DiaryActionSuggestion,
)
from app.services.diary.frames import BernieFrameSource, BernieFrameStatus, BernieFrameType
from app.services.diary.outcomes import BernieBookingOutcomeKind, OUTCOME_SESSION_STATE, OutcomeFamily
from app.services.diary.policy import BernieAvailabilityClassification
from app.services.diary.schedule_explanations import (
    DIARY_SCHEDULE_REASON_ALIASES,
    DiaryScheduleExplanationReason,
)


MANIFEST_SCHEMA_VERSION = "bernie.diary_capability_manifest.v1"

AuthorityKind = Literal[
    "read_only_context",
    "source_of_truth",
    "deterministic_guard",
    "staff_confirmation_required",
    "frontend_display_only",
    "declared_not_enforced",
]


def _enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


def _sorted_values(values: list[str] | tuple[str, ...] | set[str] | frozenset[str]) -> list[str]:
    return sorted(str(value) for value in values)


def _transition_map() -> dict[str, dict[str, str]]:
    return {
        state.value: {
            event.value: target.value
            for event, target in transitions.items()
        }
        for state, transitions in CLIENT_EVENT_TRANSITIONS.items()
    }


def _server_advance_map() -> dict[str, list[str]]:
    return {
        state.value: _sorted_values([target.value for target in targets])
        for state, targets in SERVER_ADVANCE_TARGETS.items()
    }


def _outcome_session_map() -> dict[str, list[str]]:
    return {
        outcome.value: _sorted_values(states)
        for outcome, states in OUTCOME_SESSION_STATE.items()
    }


def _capability_rows() -> list[dict[str, Any]]:
    return [
        {
            "name": capability.name,
            "tier": capability.tier.value,
            "summary": capability.summary,
            "implemented_as": capability.implemented_as,
            "requires_staff_confirmation": capability.requires_staff_confirmation,
            "allowed_authors": [author.value for author in capability.allowed_authors],
            "authority": (
                "staff_confirmation_required"
                if capability.tier in {BernieCapabilityTier.propose, BernieCapabilityTier.confirm}
                else "read_only_context"
            ),
        }
        for capability in BERNIE_CAPABILITY_REGISTRY
    ]


def build_bernie_diary_capability_manifest() -> dict[str, Any]:
    """Return Bernie's read-only view of the native Diary language.

    The returned dict is intentionally JSON-serializable and stable enough for
    golden tests. It may be passed into a future model prompt, but the manifest
    itself carries no credentials, no PHI, no DB rows, and no write grants.
    """

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "name": "Bernie Diary Capability Manifest",
        "authority_statement": (
            "This manifest is read-only context. Bernie may use it to translate "
            "staff language into typed diary intents and explanations, but it "
            "cannot authorize writes. The backend validates availability, "
            "freshness, permissions, evidence, and confirmation."
        ),
        "principles": [
            "Bernie is schema-literate, not code-authoritative.",
            "The diary domain owns availability, collision, roster, reason-code, evidence, and write policy.",
            "Bernie may propose or explain; staff-confirmed signed confirmation routes perform mutations.",
            "Frontend display copy is helpful but never authoritative.",
        ],
        "entities": {
            "appointment_statuses": {
                "values": _enum_values(AppointmentStatus),
                "source": "app.models.appointments.AppointmentStatus",
                "authority": "source_of_truth",
                "note": "Confirmed renders like Booked in parts of the UI, but remains a backend status value.",
            },
            "booking_channels": {
                "values": _enum_values(BookingChannel),
                "source": "app.models.appointments.BookingChannel",
                "authority": "source_of_truth",
            },
            "diary_template": {
                "fields": [
                    "practice_name",
                    "location_id",
                    "slot_start",
                    "slot_end",
                    "slot_interval_minutes",
                    "columns",
                    "breaks",
                ],
                "source": "app.schemas.diary.DiaryTemplateOut",
                "authority": "source_of_truth",
                "note": "slot_interval_minutes must be a multiple of five.",
            },
            "waiting_area": {
                "fields": ["id", "name", "display_order", "is_active", "location_id"],
                "source": "app.schemas.diary.WaitingAreaOut",
                "authority": "source_of_truth",
            },
        },
        "session_state": {
            "states": _enum_values(BernieSessionState),
            "events": _enum_values(BernieSessionEventType),
            "transient_states": _sorted_values([state.value for state in TRANSIENT_STATES]),
            "terminal_states": _sorted_values([state.value for state in TERMINAL_STATES]),
            "client_event_transitions": _transition_map(),
            "server_advance_targets": _server_advance_map(),
            "source": "app.services.bernie.session",
            "authority": "deterministic_guard",
        },
        "capabilities": {
            "tiers": _enum_values(BernieCapabilityTier),
            "authors": _enum_values(DiaryActionAuthor),
            "channels": _enum_values(DiaryActionChannel),
            "items": _capability_rows(),
            "source": "app.services.diary.capabilities.BERNIE_CAPABILITY_REGISTRY",
            "authority": "declared_not_enforced",
            "note": (
                "allowed_authors is a declared contract in the registry skeleton; "
                "route-level author enforcement is future work."
            ),
        },
        "outcomes": {
            "kinds": _enum_values(BernieBookingOutcomeKind),
            "families": list(OutcomeFamily.__args__),
            "outcome_session_states": _outcome_session_map(),
            "availability_classifications": list(BernieAvailabilityClassification.__args__),
            "source": "app.services.diary.outcomes and app.services.diary.policy",
            "authority": "deterministic_guard",
            "note": "can_confirm is report-only; the confirm affordance and signed evidence gate remain authoritative.",
        },
        "reason_codes": {
            "appointment_status_reason_codes": _sorted_values(STATUS_REASON_CODES),
            "status_specific_reason_code_policy": {
                status.value: _sorted_values(codes)
                for status, codes in STATUS_SPECIFIC_REASON_CODE_POLICY.items()
            },
            "schedule_reason_codes": _enum_values(DiaryScheduleExplanationReason),
            "schedule_reason_aliases": {
                alias: reason.value
                for alias, reason in sorted(DIARY_SCHEDULE_REASON_ALIASES.items())
            },
            "source": "app.schemas.appointments.STATUS_REASON_CODES, STATUS_SPECIFIC_REASON_CODE_POLICY, and app.services.diary.schedule_explanations",
            "authority": "source_of_truth",
            "drift_note": (
                "Frontend status-specific reason-code options must mirror STATUS_SPECIFIC_REASON_CODE_POLICY. "
                "Null reason codes remain allowed for grandfathering until a later migration tightens requiredness."
            ),
        },
        "frames": {
            "frame_types": list(BernieFrameType.__args__),
            "frame_statuses": list(BernieFrameStatus.__args__),
            "frame_sources": list(BernieFrameSource.__args__),
            "source": "app.services.diary.frames",
            "authority": "deterministic_guard",
            "note": "Model-sourced uncertainty frames can request clarification, but model output cannot create slot, roster, or guardrail truth.",
        },
        "confirmation_boundaries": {
            "confirm_actions": {
                action.value: {
                    "endpoint": descriptor.endpoint,
                    "evidence_purpose": descriptor.evidence_purpose,
                    "blocked_summary": descriptor.blocked_summary,
                }
                for action, descriptor in DIARY_CONFIRM_ACTIONS.items()
            },
            "envelope_sequence": [
                {
                    "type": "intent",
                    "schema_version": DiaryActionIntent.model_fields["schema_version"].default,
                    "writes_authorized": False,
                },
                {
                    "type": "proposal",
                    "schema_version": DiaryActionProposal.model_fields["schema_version"].default,
                    "writes_authorized": False,
                    "requires_staff_confirmation": True,
                },
                {
                    "type": "suggestion",
                    "schema_version": DiaryActionSuggestion.model_fields["schema_version"].default,
                    "writes_authorized": False,
                    "requires_staff_confirmation": False,
                },
                {
                    "type": "confirmation",
                    "schema_version": DiaryActionConfirmation.model_fields["schema_version"].default,
                    "writes_authorized": True,
                    "requires_staff_confirmation": True,
                },
            ],
            "source": "app.services.diary.confirm_actions and app.services.diary.envelopes",
            "authority": "staff_confirmation_required",
            "note": "Only confirmation envelopes may carry write authorization, and only after staff confirmation plus signed evidence validation.",
        },
        "non_authority_boundaries": [
            "The manifest must not be used as RBAC.",
            "The manifest must not be used to infer appointment availability.",
            "The manifest must not be used to bypass signed confirmation evidence.",
            "The manifest must not be used to convert display copy into write authority.",
            "The manifest must not expose raw patient data or live diary rows.",
        ],
        "drift_watch": [
            "Keep frontend Bernie copy keys aligned with backend outcome kinds.",
            "Promote frontend-only status-specific reason-code option lists into backend policy before treating them as authoritative.",
            "Do not present capability allowed_authors as enforced until route/envelope enforcement exists.",
            "Replace untyped patient/practitioner confidence bands with a shared enum before exposing them as authoritative manifest facts.",
        ],
    }


__all__ = [
    "MANIFEST_SCHEMA_VERSION",
    "build_bernie_diary_capability_manifest",
]
