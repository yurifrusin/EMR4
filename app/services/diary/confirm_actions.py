"""Diary-domain signed confirmation action descriptors.

This module is the single internal catalog for appointment proposal confirm
routes that already require signed evidence. It deliberately does not execute
or verify anything; routers keep the existing behaviour while reading endpoint
paths, evidence purposes, and blocked-copy contracts from one typed table.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.services.bernie_turn_evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
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
        endpoint="/api/v1/appointments/proposals/status-confirm",
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

from typing import Any, Callable, Optional

from app.services.bernie_turn_evidence import verify_signed_confirmation_evidence


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
    '''Verify signed confirmation evidence and return (audit_tag, blocks).

    Encapsulates the common evidence-verification pattern shared across
    diary confirm routes:

    - If evidence is required but not supplied, returns (None, [block]).
    - If evidence is supplied but verification fails, returns (None, [block]).
    - If evidence is verified, returns (audit_tag, []).

    Args:
        evidence: The raw signed confirmation evidence dict, or None.
        evidence_required: Whether signed evidence was required by the
            proposal.  When True and evidence is None, a block is emitted.
        expected_payload: The expected payload dict for the verify call.
        expected_purpose: The expected evidence purpose string.
        block_builder: Callable that takes (code, message) and returns a
            single block entry (e.g. AppointmentProposalIssue).
        audit_tag: Tag string appended to audit_evidence on success.
        missing_message: Human-readable message for the block emitted when
            evidence is required but missing.
        secret: Optional HMAC signing secret.  Falls back to
            settings.secret_key when omitted.

    Returns:
        (audit_tag_to_append, blocks)
        - audit_tag_to_append is the audit_tag when verification succeeded,
          or None when it failed or evidence was missing.
        - blocks is a list of block entries; always empty on success.
    '''
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
