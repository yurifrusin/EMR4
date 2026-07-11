"""Strict, portable schemas for Ariadne conductor/verifier allocation data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any


class Transport(StrEnum):
    CLI_HEADLESS = "cli_headless"
    CLI_PRINT = "cli_print"
    BRIDGE_SUBAGENT = "bridge_subagent"
    FILESYSTEM_PACKET = "filesystem_packet"
    MANUAL = "manual"


class Reachability(StrEnum):
    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


class Availability(StrEnum):
    AVAILABLE = "available"
    QUOTA_LIMITED = "quota_limited"
    QUOTA_EXHAUSTED = "quota_exhausted"
    UNKNOWN = "unknown"


class Role(StrEnum):
    CONDUCTOR = "conductor"
    VERIFIER = "verifier"
    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    TEST_ENGINEER = "test_engineer"
    SECURITY_REVIEWER = "security_reviewer"
    CODE_REVIEWER = "code_reviewer"
    DOCS_HANDOVER_AUDITOR = "docs_handover_auditor"
    GENERALIST = "generalist"


class VerifierDecision(StrEnum):
    PASS = "pass"
    REVISION_REQUIRED = "revision_required"


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _date_string(value: Any, field: str) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return _string(value, field)


def _string_list(value: Any, field: str, *, empty_allowed: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not empty_allowed):
        raise ValueError(f"{field} must be a string list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{field} must be a string list")
    return tuple(value)


@dataclass(frozen=True, slots=True)
class WorkerResource:
    resource_id: str
    provider: str
    account_id: str
    access_mode: str
    transport: Transport
    transport_quirks: tuple[str, ...]
    default_model: str
    default_reasoning: str
    max_instances: int
    quota_scope: str
    quota_class: str
    capabilities: tuple[Role, ...]
    cost_tier: int

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkerResource":
        required = {
            "resource_id", "provider", "account_id", "access_mode", "transport",
            "transport_quirks", "default_model", "default_reasoning", "max_instances",
            "quota_scope", "quota_class", "capabilities", "cost_tier",
        }
        if set(payload) != required:
            raise ValueError("WorkerResource fields must exactly match the schema")
        instances = payload["max_instances"]
        cost_tier = payload["cost_tier"]
        if not isinstance(instances, int) or instances < 1:
            raise ValueError("max_instances must be a positive integer")
        if not isinstance(cost_tier, int) or cost_tier < 0:
            raise ValueError("cost_tier must be a non-negative integer")
        capabilities = _string_list(payload["capabilities"], "capabilities")
        return cls(
            resource_id=_string(payload["resource_id"], "resource_id"),
            provider=_string(payload["provider"], "provider"),
            account_id=_string(payload["account_id"], "account_id"),
            access_mode=_string(payload["access_mode"], "access_mode"),
            transport=Transport(payload["transport"]),
            transport_quirks=_string_list(payload["transport_quirks"], "transport_quirks", empty_allowed=True),
            default_model=_string(payload["default_model"], "default_model"),
            default_reasoning=_string(payload["default_reasoning"], "default_reasoning"),
            max_instances=instances,
            quota_scope=_string(payload["quota_scope"], "quota_scope"),
            quota_class=_string(payload["quota_class"], "quota_class"),
            capabilities=tuple(Role(item) for item in capabilities),
            cost_tier=cost_tier,
        )


@dataclass(frozen=True, slots=True)
class AvailabilityProbe:
    resource_id: str
    probed_at: str
    method: str
    reachability: Reachability
    availability: Availability
    ttl_seconds: int
    evidence: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AvailabilityProbe":
        required = {"resource_id", "probed_at", "method", "reachability", "availability", "ttl_seconds", "evidence"}
        if set(payload) != required:
            raise ValueError("AvailabilityProbe fields must exactly match the schema")
        ttl = payload["ttl_seconds"]
        if not isinstance(ttl, int) or ttl < 1:
            raise ValueError("ttl_seconds must be a positive integer")
        return cls(
            resource_id=_string(payload["resource_id"], "resource_id"),
            probed_at=_date_string(payload["probed_at"], "probed_at"),
            method=_string(payload["method"], "method"),
            reachability=Reachability(payload["reachability"]),
            availability=Availability(payload["availability"]),
            ttl_seconds=ttl,
            evidence=_string_list(payload["evidence"], "evidence"),
        )


@dataclass(frozen=True, slots=True)
class RolePreference:
    role: Role
    required: bool
    preferences: tuple[str, ...]
    preference_rationale: str
    review_by: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RolePreference":
        required = {"role", "required", "preferences", "preference_rationale", "review_by"}
        if set(payload) != required or not isinstance(payload["required"], bool):
            raise ValueError("RolePreference fields must exactly match the schema")
        return cls(
            role=Role(payload["role"]),
            required=payload["required"],
            preferences=_string_list(payload["preferences"], "preferences"),
            preference_rationale=_string(payload["preference_rationale"], "preference_rationale"),
            review_by=_date_string(payload["review_by"], "review_by"),
        )


@dataclass(frozen=True, slots=True)
class UserOverride:
    override_id: str
    scope: str
    target: str
    value: str
    expiry: str
    recorded_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "UserOverride":
        required = {"override_id", "scope", "target", "value", "expiry", "recorded_at"}
        if set(payload) != required:
            raise ValueError("UserOverride fields must exactly match the schema")
        return cls(**{field: _string(payload[field], field) for field in required})


@dataclass(frozen=True, slots=True)
class GeneralistProfile:
    resource_id: str
    covers: tuple[Role, ...]
    independence: str
    required_compensating_controls: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GeneralistProfile":
        required = {"resource_id", "covers", "independence", "required_compensating_controls"}
        if set(payload) != required:
            raise ValueError("GeneralistProfile fields must exactly match the schema")
        covers = tuple(Role(item) for item in _string_list(payload["covers"], "covers"))
        required_roles = set(Role) - {Role.GENERALIST}
        if not required_roles.issubset(covers):
            raise ValueError("GeneralistProfile must cover every SSDLC role")
        return cls(
            resource_id=_string(payload["resource_id"], "resource_id"),
            covers=covers,
            independence=_string(payload["independence"], "independence"),
            required_compensating_controls=_string_list(payload["required_compensating_controls"], "required_compensating_controls"),
        )


@dataclass(frozen=True, slots=True)
class AssignmentRecord:
    role: Role
    resource_id: str
    model: str
    reasoning: str
    selection_basis: tuple[str, ...]
    fallback_reason: str
    independence_label: str
    user_override_ref: str
    orchestrator_substituted: bool
    unfilled_obligations: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AssignmentRecord":
        required = {
            "role", "resource_id", "model", "reasoning", "selection_basis",
            "fallback_reason", "independence_label", "user_override_ref",
            "orchestrator_substituted", "unfilled_obligations",
        }
        if set(payload) != required or not isinstance(payload["orchestrator_substituted"], bool):
            raise ValueError("AssignmentRecord fields must exactly match the schema")
        return cls(
            role=Role(payload["role"]),
            resource_id=_string(payload["resource_id"], "resource_id"),
            model=_string(payload["model"], "model"),
            reasoning=_string(payload["reasoning"], "reasoning"),
            selection_basis=_string_list(payload["selection_basis"], "selection_basis"),
            fallback_reason=payload["fallback_reason"] if isinstance(payload["fallback_reason"], str) else "",
            independence_label=_string(payload["independence_label"], "independence_label"),
            user_override_ref=payload["user_override_ref"] if isinstance(payload["user_override_ref"], str) else "",
            orchestrator_substituted=payload["orchestrator_substituted"],
            unfilled_obligations=_string_list(payload["unfilled_obligations"], "unfilled_obligations", empty_allowed=True),
        )


@dataclass(frozen=True, slots=True)
class ConductorPlan:
    plan_id: str
    sprint_id: str
    settings_fingerprint: str
    assignments: tuple[AssignmentRecord, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ConductorPlan":
        required = {"plan_id", "sprint_id", "settings_fingerprint", "assignments"}
        if set(payload) != required or not isinstance(payload["assignments"], list) or not payload["assignments"]:
            raise ValueError("ConductorPlan fields must exactly match the schema")
        return cls(
            plan_id=_string(payload["plan_id"], "plan_id"),
            sprint_id=_string(payload["sprint_id"], "sprint_id"),
            settings_fingerprint=_string(payload["settings_fingerprint"], "settings_fingerprint"),
            assignments=tuple(AssignmentRecord.from_dict(item) for item in payload["assignments"]),
        )


@dataclass(frozen=True, slots=True)
class VerifierResult:
    plan_id: str
    settings_fingerprint: str
    decision: VerifierDecision
    reasons: tuple[str, ...]
    verified_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "VerifierResult":
        required = {"plan_id", "settings_fingerprint", "decision", "reasons", "verified_at"}
        if set(payload) != required:
            raise ValueError("VerifierResult fields must exactly match the schema")
        return cls(
            plan_id=_string(payload["plan_id"], "plan_id"),
            settings_fingerprint=_string(payload["settings_fingerprint"], "settings_fingerprint"),
            decision=VerifierDecision(payload["decision"]),
            reasons=_string_list(payload["reasons"], "reasons"),
            verified_at=_string(payload["verified_at"], "verified_at"),
        )
