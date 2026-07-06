"""Provider-free Bernie interpretation harness over the native diary grammar.

This module is a deterministic scaffold for authored receptionist utterance
fixtures. It maps small synthetic utterances to ``DiaryActionVerb`` decisions
without routes, database access, provider calls, memory, or write authority.
"""

from __future__ import annotations

import re
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
        re.compile(r"\b(check in|check-in|arrived at reception)\b", re.I),
        "check-in is a planned native diary action",
    ),
    _UtteranceRule(
        DiaryActionVerb.status_change,
        re.compile(r"\b(mark .* (arrived|completed|dna|no show)|change .* status)\b", re.I),
        "status change maps to the signed status proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.cancel,
        re.compile(r"\b(cancel|delete) (the )?(booking|appointment)\b", re.I),
        "cancel maps to the signed delete proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.resize,
        re.compile(r"\b(make .* (longer|shorter)|extend .* appointment|change .* duration)\b", re.I),
        "duration changes map to the signed update proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.move,
        re.compile(r"\b(move|shift|reschedule) (the )?(booking|appointment)\b", re.I),
        "move maps to the signed update proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.create,
        re.compile(r"\b(book|create|make) (an? )?(booking|appointment)\b", re.I),
        "create maps to the signed create proposal/confirm path",
    ),
    _UtteranceRule(
        DiaryActionVerb.slot_search,
        re.compile(r"\b(find|show|look for|available|availability|slots?)\b", re.I),
        "availability language maps to read-only slot search",
    ),
    _UtteranceRule(
        DiaryActionVerb.explain_schedule,
        re.compile(r"\b(explain|why|what happened|schedule pattern|diary pattern)\b", re.I),
        "schedule explanation is read-only",
    ),
    _UtteranceRule(
        DiaryActionVerb.handoff,
        re.compile(r"\b(handoff|hand off|receptionist|manual review)\b", re.I),
        "handoff is meta workflow control",
    ),
)


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

    normalized = " ".join(utterance.strip().split())
    if not normalized:
        return InterpretationResult(
            utterance=utterance,
            verb=None,
            authority=None,
            dispatch=InterpretationDispatch.refuse_unknown_utterance,
            rationale="empty utterance",
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


__all__ = [
    "INTERPRETATION_HARNESS_SCHEMA_VERSION",
    "InterpretationDispatch",
    "InterpretationResult",
    "interpret_receptionist_utterance",
]
