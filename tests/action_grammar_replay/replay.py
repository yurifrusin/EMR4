"""Pure synthetic replay consumer for the R29 diary action grammar."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.services.diary.action_grammar import (
    DiaryActionVerb,
    DiaryActionVerbDescriptor,
    action_verb_for_envelope,
    get_verb_descriptor,
)
from app.services.diary.capabilities import BernieCapabilityTier
from app.services.diary.confirm_gate import ConfirmAffordanceGate, evaluate_confirm_affordance
from app.services.diary.policy import BernieReceptionPolicyDecision


class ConsumerDispatch(str, Enum):
    route_to_confirm = "route_to_confirm"
    route_read_only = "route_read_only"
    route_meta = "route_meta"
    refuse_not_implemented = "refuse_not_implemented"
    refuse_unknown_action = "refuse_unknown_action"


@dataclass(frozen=True)
class ActionResult:
    raw_name: str
    verb: DiaryActionVerb | None
    dispatch: ConsumerDispatch
    mutating: bool | None = None
    implemented: bool | None = None
    requires_staff_confirmation: bool | None = None
    confirm_actions_non_empty: bool = False
    confirm_affordance_allowed: bool | None = None
    confirm_affordance_gate: str | None = None
    invariant_violations: tuple[str, ...] = ()


@dataclass(frozen=True)
class DayScriptResult:
    script_id: str
    action_results: tuple[ActionResult, ...]
    failures: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return not self.failures


def consumer_dispatch_decision(
    descriptor: DiaryActionVerbDescriptor | None,
) -> ConsumerDispatch:
    """Decide how a consumer should route one grammar descriptor."""
    if descriptor is None:
        return ConsumerDispatch.refuse_unknown_action
    if not descriptor.implemented:
        return ConsumerDispatch.refuse_not_implemented
    if descriptor.tier is BernieCapabilityTier.confirm:
        return ConsumerDispatch.route_to_confirm
    if descriptor.tier is BernieCapabilityTier.read_only:
        return ConsumerDispatch.route_read_only
    if descriptor.tier is BernieCapabilityTier.meta:
        return ConsumerDispatch.route_meta
    raise AssertionError(f"Unexpected capability tier: {descriptor.tier!r}")


def consumer_enforce_invariants(descriptor: DiaryActionVerbDescriptor) -> tuple[str, ...]:
    """Return consumer-side invariant violations for one descriptor."""
    violations: list[str] = []
    if descriptor.tier is BernieCapabilityTier.confirm:
        if descriptor.confirm_affordance_notes is None:
            violations.append("confirm tier missing affordance notes")
        if descriptor.implemented and not descriptor.confirm_actions:
            violations.append("implemented confirm verb missing confirm actions")
    if descriptor.mutating and not descriptor.requires_staff_confirmation:
        violations.append("mutating verb does not require staff confirmation")
    if descriptor.tier in {BernieCapabilityTier.read_only, BernieCapabilityTier.meta}:
        if descriptor.mutating:
            violations.append("read-only/meta verb is mutating")
        if descriptor.requires_staff_confirmation:
            violations.append("read-only/meta verb requires staff confirmation")
    return tuple(violations)


def _policy_for_affordance_case(case: str | None) -> tuple[BernieReceptionPolicyDecision, bool]:
    """Build a deterministic policy decision for a synthetic affordance case."""
    base: dict[str, Any] = {
        "availability": "search_ran_with_candidates",
        "can_search_slots": True,
        "must_ask_clarification": False,
        "can_offer_candidates": True,
        "can_prepare_proposal": True,
        "must_block_confirmation": False,
        "advisory_warnings_only": False,
        "roster_unavailable": False,
        "search_ran_no_candidates": False,
        "reason_codes": [],
        "schedule_reason_codes": [],
    }
    has_staged_proposal = True
    if case in (None, "allowed"):
        pass
    elif case == "blocked_guardrail":
        base["availability"] = "blocked"
        base["must_block_confirmation"] = True
        base["reason_codes"] = ["synthetic_guardrail"]
    elif case == "blocked_no_proposal":
        has_staged_proposal = False
    elif case == "blocked_advisory_only":
        base["advisory_warnings_only"] = True
        base["reason_codes"] = ["synthetic_advisory"]
    else:
        raise ValueError(f"Unknown synthetic affordance case: {case!r}")
    return BernieReceptionPolicyDecision(**base), has_staged_proposal


def resolve_action(raw_name: str, *, affordance_case: str | None = None) -> ActionResult:
    """Resolve one raw fixture action through the grammar consumer."""
    verb = action_verb_for_envelope(raw_name)
    if verb is None:
        return ActionResult(raw_name=raw_name, verb=None, dispatch=ConsumerDispatch.refuse_unknown_action)

    descriptor = get_verb_descriptor(verb)
    dispatch = consumer_dispatch_decision(descriptor)
    violations = consumer_enforce_invariants(descriptor)
    affordance_allowed: bool | None = None
    affordance_gate: str | None = None

    if descriptor.tier is BernieCapabilityTier.confirm and descriptor.implemented:
        policy, has_staged_proposal = _policy_for_affordance_case(affordance_case)
        decision = evaluate_confirm_affordance(policy, has_staged_proposal=has_staged_proposal)
        affordance_allowed = decision.confirm_grade_allowed
        affordance_gate = decision.gate.value

    return ActionResult(
        raw_name=raw_name,
        verb=verb,
        dispatch=dispatch,
        mutating=descriptor.mutating,
        implemented=descriptor.implemented,
        requires_staff_confirmation=descriptor.requires_staff_confirmation,
        confirm_actions_non_empty=bool(descriptor.confirm_actions),
        confirm_affordance_allowed=affordance_allowed,
        confirm_affordance_gate=affordance_gate,
        invariant_violations=violations,
    )


def _compare_action(script_id: str, index: int, expected: dict[str, Any], actual: ActionResult) -> list[str]:
    failures: list[str] = []

    checks = {
        "expected_verb": None if actual.verb is None else actual.verb.value,
        "expected_dispatch": actual.dispatch.value,
        "expected_mutating": actual.mutating,
        "expected_implemented": actual.implemented,
        "requires_staff_confirmation": actual.requires_staff_confirmation,
        "confirm_actions_non_empty": actual.confirm_actions_non_empty,
        "expected_affordance_allowed": actual.confirm_affordance_allowed,
        "expected_affordance_gate": actual.confirm_affordance_gate,
    }

    for field_name, actual_value in checks.items():
        if field_name not in expected:
            continue
        if expected[field_name] != actual_value:
            failures.append(
                f"{script_id} action[{index}] {expected['raw_name']!r}: "
                f"{field_name} expected {expected[field_name]!r}, got {actual_value!r}"
            )

    if actual.invariant_violations:
        failures.append(
            f"{script_id} action[{index}] {expected['raw_name']!r}: "
            f"invariant violations {list(actual.invariant_violations)!r}"
        )
    return failures


def run_day_script(script: dict[str, Any]) -> DayScriptResult:
    """Run one authored synthetic day script through the grammar consumer."""
    script_id = str(script["id"])
    action_results: list[ActionResult] = []
    failures: list[str] = []

    for index, action in enumerate(script["actions"]):
        result = resolve_action(
            str(action["raw_name"]),
            affordance_case=action.get("affordance_case"),
        )
        action_results.append(result)
        failures.extend(_compare_action(script_id, index, action, result))

    return DayScriptResult(
        script_id=script_id,
        action_results=tuple(action_results),
        failures=tuple(failures),
    )
