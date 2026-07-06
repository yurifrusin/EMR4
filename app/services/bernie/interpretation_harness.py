"""Provider-free Bernie interpretation harness over the native diary grammar.

This module is a deterministic scaffold for authored receptionist utterance
fixtures. It maps small synthetic utterances to ``DiaryActionVerb`` decisions
without routes, database access, provider calls, memory, or write authority.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum

from app.services.diary.action_grammar import DiaryActionVerb
from app.services.diary.action_route_contract import (
    RouteAuthority,
    get_action_route_contract,
)

INTERPRETATION_HARNESS_SCHEMA_VERSION = "bernie.interpretation_harness.v1"


class InterpretationDispatch(str, Enum):
    route_to_confirm = "route_to_confirm"
    route_read_only = "route_read_only"
    route_meta = "route_meta"
    refuse_planned_not_implemented = "refuse_planned_not_implemented"
    refuse_unsafe_instruction = "refuse_unsafe_instruction"
    refuse_unknown_utterance = "refuse_unknown_utterance"


@dataclass(frozen=True)
class InterpretationResult:
    utterance: str
    verb: DiaryActionVerb | None
    authority: RouteAuthority | None
    dispatch: InterpretationDispatch
    rationale: str


@dataclass(frozen=True)
class _UtteranceRule:
    verb: DiaryActionVerb
    pattern: re.Pattern[str]
    rationale: str


_UTTERANCE_RULES: tuple[_UtteranceRule, ...] = (
    _UtteranceRule(
        DiaryActionVerb.waiting_area_move,
        re.compile(r"\b(waiting area|move .* waiting|send .* waiting)\b", re.I),
        "waiting-area movement is a planned native diary action",
    ),
    _UtteranceRule(
        DiaryActionVerb.link_patient,
        re.compile(r"\b(link patient|attach patient|match patient)\b", re.I),
        "patient-linking is a planned native diary action",
    ),
    _UtteranceRule(
        DiaryActionVerb.check_in,
        re.compile(r"\b(check in|check-in|arrived at reception|is here|arrived at the desk)\b", re.I),
        "check-in is a planned native diary action",
    ),
    _UtteranceRule(
        DiaryActionVerb.status_change,
        re.compile(r"\b(mark .* (arrived|completed|dna|no show)|change .* status)\b", re.I),
        "status change maps to the signed status proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.cancel,
        re.compile(
            r"\b((cancel|delete|remove) (the )?(booking|appointment)|"
            r"patient cancelled|take .* (booking|appointment) out|remove .* diary)\b",
            re.I,
        ),
        "cancel maps to the signed delete proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.resize,
        re.compile(
            r"\b(make .* (longer|shorter)|extend .* appointment|change .* duration|"
            r"double appointment|give them \d+ minutes)\b",
            re.I,
        ),
        "duration changes map to the signed update proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.move,
        re.compile(
            r"\b((move|shift|reschedule) (the )?(booking|appointment)|"
            r"push .* back|bring .* forward)\b",
            re.I,
        ),
        "move maps to the signed update proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.create,
        re.compile(r"\b((book|create|make) (an? )?(booking|appointment)|put them in)\b", re.I),
        "create maps to the signed create proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.slot_search,
        re.compile(
            r"\b(look for|available|availability|slots?|gaps?|free times?|openings?|"
            r"fit them in|squeeze them in|find (an? )?(available|open|free)? "
            r"(appointment|slot|time)|show .* (free|available|open).*(time|slot|appointment))\b",
            re.I,
        ),
        "availability language maps to read-only slot search",
    ),
    _UtteranceRule(
        DiaryActionVerb.explain_schedule,
        re.compile(r"\b(explain|why|what happened|schedule pattern|diary pattern)\b", re.I),
        "schedule explanation is read-only",
    ),
    _UtteranceRule(
        DiaryActionVerb.handoff,
        re.compile(r"\b(handoff|hand off|ask the receptionist|manual review)\b", re.I),
        "handoff is meta workflow control",
    ),
)

_UNSAFE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(ignore|bypass|override) (the )?(rules|guardrails|confirmation)\b", re.I),
    re.compile(r"\b(bypass|skip) (the )?(confirm|confirmation|approval)( step)?\b", re.I),
    re.compile(r"\b(no confirmation needed|no need for confirmation|confirm not needed)\b", re.I),
    re.compile(r"\b(don't|do not) (ask for confirmation|confirm)\b", re.I),
    re.compile(r"\b(auto-confirm|autoconfirm|just do it)\b", re.I),
    re.compile(r"\b(confirm endpoint|call .* endpoint|post .* /api)\b", re.I),
    re.compile(r"\b(database|db|sql|raw write|write .* directly)\b", re.I),
    re.compile(r"\b(use|call) (gemini|openai|anthropic|provider|llm)\b", re.I),
    re.compile(r"\bwithout (staff )?confirmation\b", re.I),
    re.compile(r"\b(pretend|act as if) .* (booked|done|confirmed)\b", re.I),
    re.compile(r"\b(already confirmed|just go ahead and confirm|just execute|mark it as done)\b", re.I),
)

_FORMAT_CHARS = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
}


def _normalize_utterance(utterance: str) -> str:
    normalized = unicodedata.normalize("NFKC", utterance)
    normalized = "".join(ch for ch in normalized if ch not in _FORMAT_CHARS)
    return " ".join(normalized.strip().split())


def _dispatch_for_authority(authority: RouteAuthority) -> InterpretationDispatch:
    if authority is RouteAuthority.signed_confirm:
        return InterpretationDispatch.route_to_confirm
    if authority is RouteAuthority.read_only:
        return InterpretationDispatch.route_read_only
    if authority is RouteAuthority.meta:
        return InterpretationDispatch.route_meta
    if authority is RouteAuthority.planned_not_implemented:
        return InterpretationDispatch.refuse_planned_not_implemented
    raise AssertionError(f"Unexpected route authority: {authority!r}")


def interpret_receptionist_utterance(utterance: str) -> InterpretationResult:
    """Map one authored synthetic receptionist utterance to a grammar action."""

    normalized = _normalize_utterance(utterance)
    if not normalized:
        return InterpretationResult(
            utterance=utterance,
            verb=None,
            authority=None,
            dispatch=InterpretationDispatch.refuse_unknown_utterance,
            rationale="empty utterance",
        )

    if any(pattern.search(normalized) for pattern in _UNSAFE_PATTERNS):
        return InterpretationResult(
            utterance=utterance,
            verb=None,
            authority=None,
            dispatch=InterpretationDispatch.refuse_unsafe_instruction,
            rationale="unsafe instruction attempted to bypass harness boundaries",
        )

    for rule in _UTTERANCE_RULES:
        if rule.pattern.search(normalized):
            contract = get_action_route_contract(rule.verb)
            return InterpretationResult(
                utterance=utterance,
                verb=rule.verb,
                authority=contract.authority,
                dispatch=_dispatch_for_authority(contract.authority),
                rationale=rule.rationale,
            )

    return InterpretationResult(
        utterance=utterance,
        verb=None,
        authority=None,
        dispatch=InterpretationDispatch.refuse_unknown_utterance,
        rationale="no deterministic authored rule matched",
    )


def assert_interpretation_result_consistency(result: InterpretationResult) -> None:
    """Assert one harness result preserves dispatch/authority invariants."""

    if result.dispatch is InterpretationDispatch.route_to_confirm:
        assert result.verb is not None
        assert result.authority is RouteAuthority.signed_confirm
    elif result.dispatch is InterpretationDispatch.route_read_only:
        assert result.verb is not None
        assert result.authority is RouteAuthority.read_only
    elif result.dispatch is InterpretationDispatch.route_meta:
        assert result.verb is not None
        assert result.authority is RouteAuthority.meta
    elif result.dispatch is InterpretationDispatch.refuse_planned_not_implemented:
        assert result.verb is not None
        assert result.authority is RouteAuthority.planned_not_implemented
    elif result.dispatch in {
        InterpretationDispatch.refuse_unsafe_instruction,
        InterpretationDispatch.refuse_unknown_utterance,
    }:
        assert result.verb is None
        assert result.authority is None
    else:
        raise AssertionError(f"Unexpected interpretation dispatch: {result.dispatch!r}")


def interpretation_result_to_frame(result: InterpretationResult) -> dict[str, object]:
    """Project a deterministic harness result into a fake-provider frame shape."""

    assert_interpretation_result_consistency(result)

    if result.dispatch is InterpretationDispatch.route_to_confirm:
        return {
            "frame_kind": "proposal",
            "proposed_action": result.verb.value if result.verb else None,
            "requires_staff_confirmation": True,
            "writes_authorized": False,
            "interpretation_dispatch": result.dispatch.value,
            "refusal_reason_kind": None,
            "copy": "I can stage this diary proposal for staff review.",
        }
    if result.dispatch is InterpretationDispatch.route_read_only:
        return {
            "frame_kind": "read_request",
            "proposed_action": result.verb.value if result.verb else None,
            "requires_backend_check": True,
            "writes_authorized": False,
            "interpretation_dispatch": result.dispatch.value,
            "refusal_reason_kind": None,
            "copy": "I can ask the backend to check the diary before showing options.",
        }
    reason_kind = {
        InterpretationDispatch.route_meta: "meta_handoff",
        InterpretationDispatch.refuse_planned_not_implemented: "planned_not_implemented",
        InterpretationDispatch.refuse_unsafe_instruction: "unsafe_instruction",
        InterpretationDispatch.refuse_unknown_utterance: "unknown_utterance",
    }[result.dispatch]
    return {
        "frame_kind": "refusal",
        "reason": result.rationale,
        "blocked": True,
        "writes_authorized": False,
        "interpretation_dispatch": result.dispatch.value,
        "refusal_reason_kind": reason_kind,
        "refused_action": result.verb.value if result.verb else None,
        "copy": "I cannot complete that request from this harness.",
    }


def assert_interpretation_frame_consistency(frame: dict[str, object]) -> None:
    """Assert one projected fake-provider frame keeps interpretation invariants."""

    dispatch_value = frame.get("interpretation_dispatch")
    assert isinstance(dispatch_value, str)
    dispatch = InterpretationDispatch(dispatch_value)
    frame_kind = frame.get("frame_kind")
    copy = frame.get("copy")

    assert frame.get("writes_authorized") is False
    assert isinstance(copy, str)
    assert copy.strip() == copy
    assert copy

    if dispatch is InterpretationDispatch.route_to_confirm:
        assert frame_kind == "proposal"
        assert frame.get("requires_staff_confirmation") is True
        assert frame.get("refusal_reason_kind") is None
        assert frame.get("refused_action") is None
        assert isinstance(frame.get("proposed_action"), str)
        assert "stage" in copy.casefold()
        assert "staff review" in copy.casefold()
    elif dispatch is InterpretationDispatch.route_read_only:
        assert frame_kind == "read_request"
        assert frame.get("requires_backend_check") is True
        assert frame.get("refusal_reason_kind") is None
        assert frame.get("refused_action") is None
        assert isinstance(frame.get("proposed_action"), str)
        assert "backend" in copy.casefold()
        assert "check" in copy.casefold()
    else:
        expected_reason_kind = {
            InterpretationDispatch.route_meta: "meta_handoff",
            InterpretationDispatch.refuse_planned_not_implemented: "planned_not_implemented",
            InterpretationDispatch.refuse_unsafe_instruction: "unsafe_instruction",
            InterpretationDispatch.refuse_unknown_utterance: "unknown_utterance",
        }[dispatch]
        assert frame_kind == "refusal"
        assert frame.get("blocked") is True
        assert frame.get("refusal_reason_kind") == expected_reason_kind
        assert isinstance(frame.get("reason"), str)
        assert "cannot" in copy.casefold()
        if dispatch in {
            InterpretationDispatch.refuse_unsafe_instruction,
            InterpretationDispatch.refuse_unknown_utterance,
        }:
            assert frame.get("refused_action") is None


__all__ = [
    "INTERPRETATION_HARNESS_SCHEMA_VERSION",
    "InterpretationDispatch",
    "InterpretationResult",
    "assert_interpretation_frame_consistency",
    "assert_interpretation_result_consistency",
    "interpret_receptionist_utterance",
    "interpretation_result_to_frame",
]
