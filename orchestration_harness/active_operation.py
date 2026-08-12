"""Pure validation and interruption decisions for Ariadne active operations."""

from __future__ import annotations

import re
from typing import Any


SCHEMA_VERSION = "ariadne.active_operation_latch.v1"
STATUS_VALUES = {"in_progress", "complete", "blocked", "paused", "replaced"}
PROMPT_CLASSES = {
    "none",
    "side_question",
    "status_request",
    "scope_addition",
    "explicit_pause",
    "explicit_redirect",
    "user_decision_response",
}
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def _object(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], *, label: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{label} keys must be exact")


def _text(value: object, *, label: str, maximum: int = 500) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or len(value) > maximum
        or "\r" in value
        or "\n" in value
    ):
        raise ValueError(f"{label} must be bounded non-empty text")
    return value


def _optional_reason(value: object, *, required: bool, label: str) -> str | None:
    if required:
        return _text(value, label=label)
    if value is not None:
        raise ValueError(f"{label} must be null")
    return None


def validate_active_operation(value: object) -> dict[str, Any]:
    """Return a normalized exact active-operation latch or fail closed."""
    latch = _object(value, label="active operation latch")
    _exact_keys(
        latch,
        {
            "schema_version",
            "operation_id",
            "active_tranche",
            "objective",
            "status",
            "source_head",
            "authority_source",
            "checkpoint",
            "interruption_policy",
            "resume_after_compaction",
            "user_attention",
            "terminal_response",
            "protected_boundaries",
        },
        label="active operation latch",
    )
    if latch["schema_version"] != SCHEMA_VERSION:
        raise ValueError("active operation schema version is not admitted")
    operation_id = latch["operation_id"]
    if not isinstance(operation_id, str) or _IDENTIFIER.fullmatch(operation_id) is None:
        raise ValueError("operation_id is invalid")
    active_tranche = _text(latch["active_tranche"], label="active_tranche", maximum=240)
    objective = _text(latch["objective"], label="objective", maximum=1000)
    status = latch["status"]
    if status not in STATUS_VALUES:
        raise ValueError("status is not admitted")
    source_head = latch["source_head"]
    if not isinstance(source_head, str) or _SHA1.fullmatch(source_head) is None:
        raise ValueError("source_head must be a lowercase full Git object id")
    authority_source = _text(
        latch["authority_source"], label="authority_source", maximum=500
    )

    checkpoint = _object(latch["checkpoint"], label="checkpoint")
    _exact_keys(
        checkpoint,
        {
            "completed_stage",
            "next_executable_stage",
            "retry_counters",
            "settings_fingerprint",
        },
        label="checkpoint",
    )
    completed_stage = _text(
        checkpoint["completed_stage"], label="completed_stage", maximum=500
    )
    next_stage = checkpoint["next_executable_stage"]
    if next_stage is not None:
        next_stage = _text(next_stage, label="next_executable_stage", maximum=500)
    counters = _object(checkpoint["retry_counters"], label="retry_counters")
    if len(counters) > 32:
        raise ValueError("retry_counters is too large")
    normalized_counters: dict[str, int] = {}
    for key, count in counters.items():
        if not isinstance(key, str) or _IDENTIFIER.fullmatch(key) is None:
            raise ValueError("retry counter key is invalid")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("retry counter values must be nonnegative integers")
        normalized_counters[key] = count
    fingerprint = checkpoint["settings_fingerprint"]
    if not isinstance(fingerprint, str) or _SHA256.fullmatch(fingerprint) is None:
        raise ValueError("settings_fingerprint is invalid")

    interruption = _object(latch["interruption_policy"], label="interruption_policy")
    _exact_keys(
        interruption,
        {
            "chronological_last_prompt_is_controlling_authority",
            "side_question_behavior",
            "status_request_behavior",
            "scope_addition_behavior",
            "replacement_requires_explicit_pause_or_redirect",
        },
        label="interruption_policy",
    )
    if interruption != {
        "chronological_last_prompt_is_controlling_authority": False,
        "side_question_behavior": "answer_then_resume",
        "status_request_behavior": "answer_then_resume",
        "scope_addition_behavior": "merge_then_resume",
        "replacement_requires_explicit_pause_or_redirect": True,
    }:
        raise ValueError("interruption_policy does not preserve operation precedence")

    resume = latch["resume_after_compaction"]
    if not isinstance(resume, bool):
        raise ValueError("resume_after_compaction must be boolean")
    attention = _object(latch["user_attention"], label="user_attention")
    _exact_keys(attention, {"required", "reason"}, label="user_attention")
    attention_required = attention["required"]
    if not isinstance(attention_required, bool):
        raise ValueError("user_attention.required must be boolean")
    attention_reason = _optional_reason(
        attention["reason"],
        required=attention_required,
        label="user_attention.reason",
    )
    terminal = _object(latch["terminal_response"], label="terminal_response")
    _exact_keys(terminal, {"permitted", "reason"}, label="terminal_response")
    terminal_permitted = terminal["permitted"]
    if not isinstance(terminal_permitted, bool):
        raise ValueError("terminal_response.permitted must be boolean")
    terminal_reason = _text(
        terminal["reason"], label="terminal_response.reason", maximum=500
    )

    boundaries = latch["protected_boundaries"]
    if not isinstance(boundaries, list) or not 1 <= len(boundaries) <= 64:
        raise ValueError("protected_boundaries must contain 1..64 values")
    normalized_boundaries = [
        _text(item, label="protected_boundary", maximum=200) for item in boundaries
    ]
    if len(set(normalized_boundaries)) != len(normalized_boundaries):
        raise ValueError("protected_boundaries must be unique")

    if status == "in_progress":
        if not resume:
            raise ValueError("in_progress requires resume_after_compaction")
        if next_stage is None:
            raise ValueError("in_progress requires next_executable_stage")
        if attention_required:
            raise ValueError("in_progress cannot simultaneously require user attention")
        if terminal_permitted:
            raise ValueError("in_progress forbids terminal response")
        if terminal_reason != "unfinished_authorized_operation":
            raise ValueError("in_progress terminal reason is invalid")
    elif status == "complete":
        if (
            resume
            or next_stage is not None
            or attention_required
            or not terminal_permitted
        ):
            raise ValueError("complete state is internally inconsistent")
    elif status == "blocked":
        if not attention_required or not terminal_permitted:
            raise ValueError("blocked requires user attention and terminal permission")
    elif status == "paused":
        if attention_required or not terminal_permitted:
            raise ValueError(
                "paused requires explicit terminal permission without a fork"
            )
    elif status == "replaced":
        if (
            resume
            or next_stage is not None
            or attention_required
            or not terminal_permitted
        ):
            raise ValueError("replaced state is internally inconsistent")

    return {
        "schema_version": SCHEMA_VERSION,
        "operation_id": operation_id,
        "active_tranche": active_tranche,
        "objective": objective,
        "status": status,
        "source_head": source_head,
        "authority_source": authority_source,
        "checkpoint": {
            "completed_stage": completed_stage,
            "next_executable_stage": next_stage,
            "retry_counters": normalized_counters,
            "settings_fingerprint": fingerprint,
        },
        "interruption_policy": dict(interruption),
        "resume_after_compaction": resume,
        "user_attention": {
            "required": attention_required,
            "reason": attention_reason,
        },
        "terminal_response": {
            "permitted": terminal_permitted,
            "reason": terminal_reason,
        },
        "protected_boundaries": normalized_boundaries,
    }


def assess_interruption(
    value: object, *, prompt_class: str, terminal_intent: bool = False
) -> dict[str, Any]:
    """Classify an interruption without allowing chronology to replace authority."""
    latch = validate_active_operation(value)
    if prompt_class not in PROMPT_CLASSES:
        raise ValueError("prompt_class is not admitted")
    if not isinstance(terminal_intent, bool):
        raise ValueError("terminal_intent must be boolean")

    if latch["status"] != "in_progress":
        return {
            "schema_version": "ariadne.active_operation_decision.v1",
            "status": "passed",
            "operation_id": latch["operation_id"],
            "decision": "terminal_handback_permitted"
            if latch["terminal_response"]["permitted"]
            else "continue_operation",
            "terminal_handback_permitted": latch["terminal_response"]["permitted"],
            "next_executable_stage": latch["checkpoint"]["next_executable_stage"],
            "reasons": [],
        }

    if prompt_class in {"explicit_pause", "explicit_redirect"}:
        decision = "update_latch_before_terminal_or_replacement"
    elif prompt_class in {"scope_addition", "user_decision_response"}:
        decision = "merge_then_resume"
    elif prompt_class in {"side_question", "status_request"}:
        decision = "answer_then_resume"
    else:
        decision = "resume_operation"

    reasons = ["unfinished_authorized_operation"] if terminal_intent else []
    return {
        "schema_version": "ariadne.active_operation_decision.v1",
        "status": "revision_required" if terminal_intent else "passed",
        "operation_id": latch["operation_id"],
        "decision": decision,
        "terminal_handback_permitted": False,
        "next_executable_stage": latch["checkpoint"]["next_executable_stage"],
        "reasons": reasons,
    }


def receipt_projection(value: object) -> dict[str, Any]:
    """Return the small exact latch projection carried by continuation receipts."""
    latch = validate_active_operation(value)
    return {
        "operation_id": latch["operation_id"],
        "active_tranche": latch["active_tranche"],
        "status": latch["status"],
        "source_head": latch["source_head"],
        "completed_stage": latch["checkpoint"]["completed_stage"],
        "next_executable_stage": latch["checkpoint"]["next_executable_stage"],
        "resume_after_compaction": latch["resume_after_compaction"],
        "user_attention_required": latch["user_attention"]["required"],
        "terminal_handback_permitted": latch["terminal_response"]["permitted"],
    }
