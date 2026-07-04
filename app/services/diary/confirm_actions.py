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


__all__ = [
    "DIARY_CONFIRM_ACTIONS",
    "DiaryConfirmAction",
    "DiaryConfirmActionDescriptor",
    "get_diary_confirm_action",
]
