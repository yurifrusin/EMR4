"""Diary-domain signed confirmation action descriptors.

This module is the single internal catalog for appointment proposal confirm
routes that already require signed evidence. It also owns the small shared
verification helper used by those routes, keeping endpoint paths, evidence
purposes, blocked-copy contracts, and evidence block construction in one place.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from app.services.bernie_turn_evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
    verify_signed_confirmation_evidence,
)


class DiaryConfirmAction(str, Enum):
    """Signed-confirm action names for current diary write proposals."""

    staff_create = "staff_create"
    bernie_create = "bernie_create"
    update = "update"
    status = "status"
    delete = "delete"


@dataclass(frozen=True)
class DiaryConfirmActionDescriptor:
    """Stable contract for one signed proposal-confirm endpoint."""

    action: DiaryConfirmAction
    endpoint: str
    evidence_purpose: str
    blocked_summary: str

    def blocked_issue_payload(self, code: str, message: str) -> dict[str, str]:
        return {
            "code": code,
            "severity": "blocked",
            "message": message,
        }


DIARY_CONFIRM_ACTIONS: dict[DiaryConfirmAction, DiaryConfirmActionDescriptor] = {
    DiaryConfirmAction.staff_create: DiaryConfirmActionDescriptor(
        action=DiaryConfirmAction.staff_create,
        endpoint="/api/v1/appointments/proposals/create/confirm",
        evidence_purpose=SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
        blocked_summary="Cannot confirm create proposal. See blocked issues.",
    ),
    DiaryConfirmAction.bernie_create: DiaryConfirmActionDescriptor(
        action=DiaryConfirmAction.bernie_create,
        endpoint="/api/v1/appointments/proposals/create/confirm-bernie",
        evidence_purpose=SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
        blocked_summary="Cannot confirm Bernie create proposal. See blocked issues.",
    ),
    DiaryConfirmAction.update: DiaryConfirmActionDescriptor(
        action=DiaryConfirmAction.update,
        endpoint="/api/v1/appointments/proposals/update/confirm",
        evidence_purpose=SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
        blocked_summary="The update proposal could not be confirmed.",
    ),
    DiaryConfirmAction.status: DiaryConfirmActionDescriptor(
        action=DiaryConfirmAction.status,
        endpoint="/api/v1/appointments/proposals/status/confirm",
        evidence_purpose=SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
        blocked_summary="Cannot confirm status proposal. See blocked issues.",
    ),
    DiaryConfirmAction.delete: DiaryConfirmActionDescriptor(
        action=DiaryConfirmAction.delete,
        endpoint="/api/v1/appointments/proposals/delete-confirm",
        evidence_purpose=SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
        blocked_summary="Cannot confirm delete proposal. See blocked issues.",
    ),
}


def get_diary_confirm_action(action: DiaryConfirmAction) -> DiaryConfirmActionDescriptor:
    """Return the descriptor for a known diary confirm action."""

    return DIARY_CONFIRM_ACTIONS[action]



def verify_signed_confirmation_evidence_block(
    evidence: Optional[dict[str, Any]],
    evidence_required: bool,
    expected_payload: dict[str, Any],
    expected_purpose: str,
    block_builder: Callable[[str, str], dict[str, str]],
    audit_tag: str,
    *,
    missing_message: str = "Signed confirmation evidence is required.",
    secret: Optional[str] = None,
) -> tuple[Optional[str], list[dict[str, str]]]:
    """Verify signed confirmation evidence and return an audit tag plus blocks.

    Encapsulates the common evidence-verification pattern shared across
    diary confirm routes:

    - If evidence is optional and absent, returns a signed-evidence-required block.
    - Otherwise delegates to the signed evidence verifier.
    - If evidence is verified, returns (audit_tag, []).
    - If verification fails, returns (None, [block]).

    Args:
        evidence: The raw signed confirmation evidence dict, or None.
        evidence_required: Whether signed evidence was required by the proposal.
        expected_payload: The expected payload dict for the verify call.
        expected_purpose: The expected evidence purpose string.
        block_builder: Callable that takes (code, message) and returns a single block entry.
        audit_tag: Tag string appended to audit_evidence on success.
        missing_message: Human-readable message for the optional-and-missing block.
        secret: Optional HMAC signing secret. Falls back to settings.secret_key when omitted.

    Returns:
        A tuple of (audit_tag_to_append, blocks). The audit tag is present only
        on successful verification; blocks is empty on success.
    """
    signed_evidence_present = evidence is not None
    if not (evidence_required or signed_evidence_present):
        return None, [block_builder("signed_evidence_required", missing_message)]

    signed_result = verify_signed_confirmation_evidence(
        evidence,
        expected_payload,
        expected_purpose=expected_purpose,
        secret=secret,
    )
    if signed_result.verified:
        return audit_tag, []
    return None, [block_builder(signed_result.code, signed_result.detail)]


__all__ = [
    "DIARY_CONFIRM_ACTIONS",
    "DiaryConfirmAction",
    "DiaryConfirmActionDescriptor",
    "get_diary_confirm_action",
    "verify_signed_confirmation_evidence_block",
]
