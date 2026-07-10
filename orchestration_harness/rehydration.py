"""Pure, advisory-only context rehydration checks for Ariadne."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ActionClassification, BoundaryClass, Mandate


@dataclass(frozen=True, slots=True)
class GitState:
    branch: str | None
    head: str | None
    dirty: bool


REMEDIATIONS = {
    "dirty_worktree_present": "Resolve or explicitly classify local changes before continuing.",
    "active_mandate_missing": "Restore a schema-valid user-approved mandate file.",
    "checkpoint_missing": "Restore a readable checkpoint describing the active stage and next action.",
    "evidence_ledger_missing_or_unreadable": "Restore a readable evidence ledger before continuing.",
    "next_action_not_classified": "Classify the next action with a boundary class and disposition.",
    "git_state_incomplete": "Restore readable branch and HEAD state before continuing.",
}


def validate_next_action(payload: Any) -> dict[str, str] | None:
    """Return a normalized action only when its typed authority is complete."""

    if not isinstance(payload, dict) or set(payload) != {
        "kind",
        "boundary_class",
        "classification",
    }:
        return None
    if not isinstance(payload["kind"], str) or not payload["kind"].strip():
        return None
    try:
        boundary = BoundaryClass(payload["boundary_class"])
        classification = ActionClassification(payload["classification"])
    except (TypeError, ValueError):
        return None
    return {
        "kind": payload["kind"],
        "boundary_class": boundary.value,
        "classification": classification.value,
    }


def build_rehydration_status(
    *,
    git_state: GitState,
    mandate: Mandate | None,
    checkpoint: dict[str, Any] | None,
    evidence_ledger_readable: bool,
) -> dict[str, Any]:
    """Assess continuation prerequisites from supplied observable state only."""

    reasons: list[str] = []
    if git_state.dirty:
        reasons.append("dirty_worktree_present")
    if not git_state.branch or not git_state.head:
        reasons.append("git_state_incomplete")
    if mandate is None:
        reasons.append("active_mandate_missing")
    if checkpoint is None:
        reasons.append("checkpoint_missing")
    if not evidence_ledger_readable:
        reasons.append("evidence_ledger_missing_or_unreadable")

    next_action = None if checkpoint is None else validate_next_action(checkpoint.get("next_action"))
    if next_action is None:
        reasons.append("next_action_not_classified")

    status: dict[str, Any] = {
        "rehydration_status": "passed" if not reasons else "pause_required",
        "repo_state": {
            "branch": git_state.branch,
            "head": git_state.head,
            "dirty": git_state.dirty,
        },
        "reasons": reasons,
        "remediations": [REMEDIATIONS[reason] for reason in reasons],
    }
    if mandate is not None:
        status["mandate"] = {
            "id": mandate.mandate_id,
            "autonomy": mandate.autonomy,
        }
    if next_action is not None:
        status["next_action"] = next_action
    return status
