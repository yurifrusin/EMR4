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
