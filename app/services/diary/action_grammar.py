"""Native diary/reception action grammar — versioned verb vocabulary.

Defines a typed superset of diary action verbs and binds each to:
- Its ``BernieCapabilityTier`` (using the existing vocabulary only)
- Whether it is mutating and requires staff confirmation
- Which ``DiaryConfirmAction`` entries back it when implemented
- Which ``BERNIE_CAPABILITY_REGISTRY`` capability it corresponds to
- Whether it is implemented (False = planned-not-implemented scaffold)
- For confirm-tier verbs: a ``confirm_affordance_notes`` string that
  documents the ``evaluate_confirm_affordance``/session-state gate
  expectations callers must satisfy before reaching the confirm endpoint

This module is a pure backend/domain contract.  It has no routes, no UI
surface, no write authority, no envelope strictness changes, no provider
calls, and no migration.  ``action_name`` free-string behaviour in existing
envelopes is unchanged.  The grammar drives registered-envelope authority
validation through ``envelope_capability_policy.validate_envelope_authority``
and the deterministic action-grammar replay harness; it is not yet wired into
live route dispatch.

Schema version
--------------
``GRAMMAR_SCHEMA_VERSION = "diary.action_grammar.v1"``

All additive changes within v1 (new verbs, updated notes) must keep the
existing verb bindings unchanged.  Rename or remove a verb in a new version.

Invariants (statically checked by ``assert_grammar_consistency``):
- Every confirm-tier descriptor has a non-None ``confirm_affordance_notes``.
- Every mutating verb has ``requires_staff_confirmation=True``.
- Every implemented confirm-tier verb has at least one ``confirm_action``
  that exists in ``DIARY_CONFIRM_ACTIONS``.
- Every planned-not-implemented confirm-tier verb has ``confirm_actions=()``.
- Every ``capability_name`` resolves in ``BERNIE_CAPABILITY_REGISTRY``.
- All verbs in ``DIARY_ACTION_GRAMMAR`` have a corresponding key.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapabilityTier,
    get_bernie_capability,
)
from app.services.diary.confirm_actions import DIARY_CONFIRM_ACTIONS, DiaryConfirmAction

GRAMMAR_SCHEMA_VERSION = "diary.action_grammar.v1"


class DiaryActionVerb(str, Enum):
    """Canonical typed verbs for diary/reception actions.

    Mutating verbs (implemented — signed confirm action exists):
    - create, move, resize, cancel, status_change

    Mutating verbs (planned-not-implemented — no signed confirm action yet):
    - check_in, waiting_area_move, link_patient

    Read-only verbs:
    - slot_search, explain_schedule

    Meta verbs (session/flow control, no diary mutation):
    - handoff
    """

    # --- mutating: implemented ---
    create = "create"
    move = "move"
    resize = "resize"
    cancel = "cancel"
    status_change = "status_change"

    # --- mutating: planned-not-implemented (no signed confirm action) ---
    check_in = "check_in"
    waiting_area_move = "waiting_area_move"
    link_patient = "link_patient"

    # --- read-only ---
    slot_search = "slot_search"
    explain_schedule = "explain_schedule"

    # --- meta ---
    handoff = "handoff"


@dataclass(frozen=True)
class DiaryActionVerbDescriptor:
    """Static binding from a DiaryActionVerb to its domain contracts.

    Fields
    ------
    verb:
        The canonical verb this descriptor describes.
    tier:
        BernieCapabilityTier from the existing vocabulary.  Callers should
        gate confirm-tier verbs behind ``evaluate_confirm_affordance`` before
        reaching any confirm endpoint.
    mutating:
        True when the verb will alter diary state on confirmation.
    requires_staff_confirmation:
        True for all mutating verbs.  Confirm-tier verbs also require a
        passing ``evaluate_confirm_affordance`` result before proceeding.
    confirm_actions:
        Tuple of DiaryConfirmAction entries that back this verb.  Empty for
        read-only, meta, and planned-not-implemented verbs.
    capability_name:
        Name of the matching BERNIE_CAPABILITY_REGISTRY entry, or None.
    implemented:
        False = planned scaffold; no signed confirm endpoint exists yet.
        confirm_actions must be empty when implemented is False.
    confirm_affordance_notes:
        Required (non-None) for every confirm-tier descriptor.  Documents
        what ``evaluate_confirm_affordance`` and session-state conditions
        must hold before the verb's confirm_actions endpoint may be called.
        Callers must enforce these conditions; the grammar table cannot.
    """

    verb: DiaryActionVerb
    tier: BernieCapabilityTier
    mutating: bool
    requires_staff_confirmation: bool
    confirm_actions: tuple[DiaryConfirmAction, ...]
    capability_name: Optional[str]
    implemented: bool
    confirm_affordance_notes: Optional[str]


DIARY_ACTION_GRAMMAR: dict[DiaryActionVerb, DiaryActionVerbDescriptor] = {
    DiaryActionVerb.create: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.create,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(
            DiaryConfirmAction.staff_create,
            DiaryConfirmAction.bernie_create,
        ),
        capability_name="confirm_booking",
        implemented=True,
        confirm_affordance_notes=(
            "evaluate_confirm_affordance must return confirm_grade_allowed=True "
            "before any confirm-grade create UI may be shown or the endpoint called. "
            "For the bernie_create path the session must additionally be in "
            "proposal_preview state and have a non-None staged_proposal_freshness_id. "
            "Routes: staff_create → /proposals/create/confirm; "
            "bernie_create → /proposals/create/confirm-bernie."
        ),
    ),
    DiaryActionVerb.move: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.move,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(DiaryConfirmAction.update,),
        capability_name="propose_edit",
        implemented=True,
        confirm_affordance_notes=(
            "evaluate_confirm_affordance must return confirm_grade_allowed=True. "
            "Routes to DiaryConfirmAction.update → /proposals/update/confirm. "
            "Kept as a distinct verb from resize in v1; both resolve to the update "
            "confirm action until a dedicated move endpoint is warranted. "
            "A move proposal must carry valid start_time and practitioner_id; "
            "the confirm route re-validates collision and freshness before writing."
        ),
    ),
    DiaryActionVerb.resize: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.resize,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(DiaryConfirmAction.update,),
        capability_name="propose_edit",
        implemented=True,
        confirm_affordance_notes=(
            "evaluate_confirm_affordance must return confirm_grade_allowed=True. "
            "Routes to DiaryConfirmAction.update → /proposals/update/confirm. "
            "Kept as a distinct verb from move in v1; both resolve to the update "
            "confirm action until a dedicated resize endpoint is warranted. "
            "A resize proposal must carry valid duration_minutes; the confirm "
            "route re-validates that the extended slot remains collision-free."
        ),
    ),
    DiaryActionVerb.cancel: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.cancel,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(DiaryConfirmAction.delete,),
        capability_name="propose_cancel",
        implemented=True,
        confirm_affordance_notes=(
            "evaluate_confirm_affordance must return confirm_grade_allowed=True. "
            "Routes to DiaryConfirmAction.delete → /proposals/delete-confirm. "
            "Staff must supply a valid cancellation reason before confirmation; "
            "the confirm route requires signed evidence."
        ),
    ),
    DiaryActionVerb.status_change: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.status_change,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(DiaryConfirmAction.status,),
        capability_name="propose_status",
        implemented=True,
        confirm_affordance_notes=(
            "evaluate_confirm_affordance must return confirm_grade_allowed=True. "
            "Routes to DiaryConfirmAction.status → /proposals/status-confirm. "
            "Status transitions must be valid per the appointment lifecycle model; "
            "the confirm route validates the transition and requires signed evidence."
        ),
    ),
    DiaryActionVerb.check_in: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.check_in,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(),
        capability_name=None,
        implemented=False,
        confirm_affordance_notes=(
            "Planned-not-implemented. No signed confirm action or endpoint exists yet. "
            "When promoted to implemented: evaluate_confirm_affordance must return "
            "confirm_grade_allowed=True, a DiaryConfirmAction entry must be registered, "
            "and confirm_actions must be populated before any confirm-grade UI is shown."
        ),
    ),
    DiaryActionVerb.waiting_area_move: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.waiting_area_move,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(),
        capability_name=None,
        implemented=False,
        confirm_affordance_notes=(
            "Planned-not-implemented. No signed confirm action or endpoint exists yet. "
            "When promoted to implemented: evaluate_confirm_affordance must return "
            "confirm_grade_allowed=True, a DiaryConfirmAction entry must be registered, "
            "and confirm_actions must be populated before any confirm-grade UI is shown."
        ),
    ),
    DiaryActionVerb.link_patient: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.link_patient,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(),
        capability_name=None,
        implemented=False,
        confirm_affordance_notes=(
            "Planned-not-implemented. No signed confirm action or endpoint exists yet. "
            "When promoted to implemented: evaluate_confirm_affordance must return "
            "confirm_grade_allowed=True, a DiaryConfirmAction entry must be registered, "
            "and confirm_actions must be populated before any confirm-grade UI is shown."
        ),
    ),
    DiaryActionVerb.slot_search: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.slot_search,
        tier=BernieCapabilityTier.read_only,
        mutating=False,
        requires_staff_confirmation=False,
        confirm_actions=(),
        capability_name="find_slots",
        implemented=True,
        confirm_affordance_notes=None,
    ),
    DiaryActionVerb.explain_schedule: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.explain_schedule,
        tier=BernieCapabilityTier.read_only,
        mutating=False,
        requires_staff_confirmation=False,
        confirm_actions=(),
        capability_name="explain_schedule",
        implemented=True,
        confirm_affordance_notes=None,
    ),
    DiaryActionVerb.handoff: DiaryActionVerbDescriptor(
        verb=DiaryActionVerb.handoff,
        tier=BernieCapabilityTier.meta,
        mutating=False,
        requires_staff_confirmation=False,
        confirm_actions=(),
        capability_name="handoff_to_receptionist",
        implemented=True,
        confirm_affordance_notes=None,
    ),
}


def get_verb_descriptor(verb: DiaryActionVerb) -> DiaryActionVerbDescriptor:
    """Return the grammar descriptor for a verb. Always present."""
    return DIARY_ACTION_GRAMMAR[verb]


def action_verb_for_envelope(action_name: str) -> Optional[DiaryActionVerb]:
    """Map a free-string envelope action_name to a DiaryActionVerb.

    Non-breaking bridge: returns None for unknown or propose-only names so
    that callers using free-string action_name continue to work without
    modification.  The grammar does not make action_name a strict enum.
    """
    return _ACTION_NAME_TO_VERB.get(action_name)


_ACTION_NAME_TO_VERB: dict[str, DiaryActionVerb] = {
    "create": DiaryActionVerb.create,
    "create_appointment": DiaryActionVerb.create,
    "confirm_booking": DiaryActionVerb.create,
    "move": DiaryActionVerb.move,
    "move_appointment": DiaryActionVerb.move,
    "resize": DiaryActionVerb.resize,
    "resize_appointment": DiaryActionVerb.resize,
    "cancel": DiaryActionVerb.cancel,
    "cancel_appointment": DiaryActionVerb.cancel,
    "status_change": DiaryActionVerb.status_change,
    "check_in": DiaryActionVerb.check_in,
    "waiting_area_move": DiaryActionVerb.waiting_area_move,
    "link_patient": DiaryActionVerb.link_patient,
    "find_slots": DiaryActionVerb.slot_search,
    "slot_search": DiaryActionVerb.slot_search,
    "explain_schedule": DiaryActionVerb.explain_schedule,
    "handoff": DiaryActionVerb.handoff,
    "handoff_to_receptionist": DiaryActionVerb.handoff,
}


def assert_grammar_consistency() -> None:
    """Assert that DIARY_ACTION_GRAMMAR is internally consistent.

    Raises AssertionError on the first violation found.  Intended to be called
    from tests and import-time guards; it is a pure in-process check with no
    side effects.
    """
    assert set(DIARY_ACTION_GRAMMAR) == set(DiaryActionVerb), (
        "DIARY_ACTION_GRAMMAR must have exactly one entry per DiaryActionVerb. "
        f"Missing: {set(DiaryActionVerb) - set(DIARY_ACTION_GRAMMAR)}; "
        f"Extra: {set(DIARY_ACTION_GRAMMAR) - set(DiaryActionVerb)}"
    )

    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        assert desc.verb is verb, (
            f"{verb.value}: descriptor.verb ({desc.verb!r}) does not match the table key"
        )

        # confirm-tier must document affordance gate expectations
        if desc.tier is BernieCapabilityTier.confirm:
            assert desc.confirm_affordance_notes is not None, (
                f"{verb.value}: confirm-tier descriptor must have non-None "
                "confirm_affordance_notes documenting evaluate_confirm_affordance "
                "and session-state gate expectations."
            )

        # mutating => requires_staff_confirmation
        if desc.mutating:
            assert desc.requires_staff_confirmation, (
                f"{verb.value}: mutating verb must have requires_staff_confirmation=True"
            )

        # implemented confirm-tier must have ≥1 confirm_action in DIARY_CONFIRM_ACTIONS
        if desc.tier is BernieCapabilityTier.confirm and desc.implemented:
            assert desc.confirm_actions, (
                f"{verb.value}: implemented confirm-tier verb must list at least one "
                "confirm_action in DIARY_CONFIRM_ACTIONS"
            )
            for ca in desc.confirm_actions:
                assert ca in DIARY_CONFIRM_ACTIONS, (
                    f"{verb.value}: confirm_action {ca!r} not found in DIARY_CONFIRM_ACTIONS"
                )

        # planned-not-implemented confirm-tier must have empty confirm_actions
        if desc.tier is BernieCapabilityTier.confirm and not desc.implemented:
            assert desc.confirm_actions == (), (
                f"{verb.value}: planned-not-implemented confirm-tier verb must have "
                "confirm_actions=()"
            )

        # read-only and meta verbs must not be mutating
        if desc.tier in (BernieCapabilityTier.read_only, BernieCapabilityTier.meta):
            assert not desc.mutating, (
                f"{verb.value}: read_only/meta verb must have mutating=False"
            )
            assert not desc.requires_staff_confirmation, (
                f"{verb.value}: read_only/meta verb must have requires_staff_confirmation=False"
            )

        # capability_name must resolve in BERNIE_CAPABILITY_REGISTRY when set.
        # Note: a capability may span propose+confirm steps (e.g. propose_edit covers
        # both the edit proposal and the update-confirm path); the capability tier need
        # not match the verb tier, which describes the specific verb's action class.
        if desc.capability_name is not None:
            cap = get_bernie_capability(desc.capability_name)
            assert cap is not None, (
                f"{verb.value}: capability_name '{desc.capability_name}' not found "
                "in BERNIE_CAPABILITY_REGISTRY"
            )


__all__ = [
    "GRAMMAR_SCHEMA_VERSION",
    "DiaryActionVerb",
    "DiaryActionVerbDescriptor",
    "DIARY_ACTION_GRAMMAR",
    "get_verb_descriptor",
    "action_verb_for_envelope",
    "assert_grammar_consistency",
]
