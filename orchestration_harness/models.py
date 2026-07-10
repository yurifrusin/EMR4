"""Schema spine for the portable Ariadne harness core.

This module deliberately has no EMR4 runtime imports or execution adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class BoundaryClass(StrEnum):
    """Authority boundary for a proposed orchestration action."""

    GREEN = "green"
    BLUE = "blue"
    AMBER = "amber"
    RED = "red"
    BLACK = "black"


class ActionClassification(StrEnum):
    """Deterministic disposition of a proposed action."""

    ALLOWED = "allowed"
    ALLOWED_WITH_EVIDENCE = "allowed_with_evidence"
    REQUIRES_USER_APPROVAL = "requires_user_approval"
    BLOCKED = "blocked"
    UNDERSPECIFIED = "underspecified"


@dataclass(frozen=True, slots=True)
class Mandate:
    """A user-approved operating envelope, expressed as portable JSON data."""

    mandate_id: str
    objective: str
    autonomy: str
    allowed: tuple[str, ...]
    requires_user_approval: tuple[str, ...]
    stop_conditions: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Mandate":
        required_fields = {
            "mandate_id",
            "objective",
            "autonomy",
            "allowed",
            "requires_user_approval",
            "stop_conditions",
        }
        if set(payload) != required_fields:
            raise ValueError("Mandate fields must exactly match the schema")

        values: dict[str, Any] = {}
        for field in ("mandate_id", "objective", "autonomy"):
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Mandate field {field!r} must be a non-empty string")
            values[field] = value

        for field in ("allowed", "requires_user_approval", "stop_conditions"):
            value = payload[field]
            if not isinstance(value, list) or not value:
                raise ValueError(f"Mandate field {field!r} must be a non-empty list")
            if not all(isinstance(item, str) and item.strip() for item in value):
                raise ValueError(f"Mandate field {field!r} must contain non-empty strings")
            values[field] = tuple(value)

        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mandate_id": self.mandate_id,
            "objective": self.objective,
            "autonomy": self.autonomy,
            "allowed": list(self.allowed),
            "requires_user_approval": list(self.requires_user_approval),
            "stop_conditions": list(self.stop_conditions),
        }


@dataclass(frozen=True, slots=True)
class Evidence:
    """Portable verification evidence with a fingerprint for freshness checks."""

    evidence_id: str
    state_fingerprint: str
    command: tuple[str, ...]
    scope: tuple[str, ...]
    recorded_by: str
    limitations: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Evidence":
        required_fields = {
            "evidence_id",
            "state_fingerprint",
            "command",
            "scope",
            "recorded_by",
            "limitations",
        }
        if set(payload) != required_fields:
            raise ValueError("Evidence fields must exactly match the schema")
        string_fields = ("evidence_id", "state_fingerprint", "recorded_by")
        values: dict[str, Any] = {}
        for field in string_fields:
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Evidence field {field!r} must be a non-empty string")
            values[field] = value
        for field in ("command", "scope", "limitations"):
            value = payload[field]
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                raise ValueError(f"Evidence field {field!r} must be a string list")
            values[field] = tuple(value)
        if not values["command"] or not values["scope"]:
            raise ValueError("Evidence command and scope must be non-empty")
        shell_fragments = ("&&", "||", ";", "\n", "\r", "$(")
        if any(
            fragment in argument
            for argument in values["command"]
            for fragment in shell_fragments
        ):
            raise ValueError("Evidence command must be an argument array, not a shell contract")
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "state_fingerprint": self.state_fingerprint,
            "command": list(self.command),
            "scope": list(self.scope),
            "recorded_by": self.recorded_by,
            "limitations": list(self.limitations),
        }
