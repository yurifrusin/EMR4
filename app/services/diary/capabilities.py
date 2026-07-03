"""Typed capability/tool registry skeleton for the Bernie reception domain.

One vocabulary for what Bernie can do, shared by the diary panel today and any
future runtime (voice lanes, Davida handover) - mirroring ``AiCapability`` on
the Access AI side. The registry is data plus typed contracts, not a
framework: a module-level table that routers and future session runtimes read.

This slice records the map only. It does not change routing, add endpoints,
or gate anything; per-capability typed input/output models and audit-code
wiring are later-sprint work.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.services.diary.envelopes import DiaryActionAuthor


class BernieCapabilityTier(str, Enum):
    """Autonomy tier of a capability.

    read_only  - observes and interprets; never mutates.
    propose    - prepares a typed, non-mutating proposal; staff must confirm.
    confirm    - executes a previously proposed mutation after staff
                 confirmation and evidence/freshness gating.
    meta       - session/flow control, no diary effect.
    """

    read_only = "read_only"
    propose = "propose"
    confirm = "confirm"
    meta = "meta"


@dataclass(frozen=True)
class BernieCapability:
    """One entry in the Bernie capability registry."""

    name: str
    tier: BernieCapabilityTier
    summary: str
    implemented_as: Optional[str]  # current code location/endpoint; None = planned
    requires_staff_confirmation: bool
    allowed_authors: tuple[DiaryActionAuthor, ...]


BERNIE_CAPABILITY_REGISTRY: tuple[BernieCapability, ...] = (
    BernieCapability(
        name="interpret_instruction",
        tier=BernieCapabilityTier.read_only,
        summary="Translate a staff booking instruction into a typed slot-search command candidate.",
        implemented_as="POST /appointments/proposals/bernie/interpret-booking-instruction",
        requires_staff_confirmation=False,
        allowed_authors=(DiaryActionAuthor.bernie,),
    ),
    BernieCapability(
        name="resolve_patient",
        tier=BernieCapabilityTier.read_only,
        summary="Resolve a patient reference from instruction text and diary context.",
        implemented_as="app/routers/appointments.py inline (extraction pending)",
        requires_staff_confirmation=False,
        allowed_authors=(DiaryActionAuthor.bernie,),
    ),
    BernieCapability(
        name="resolve_practitioner",
        tier=BernieCapabilityTier.read_only,
        summary="Resolve a practitioner reference from instruction text and roster context.",
        implemented_as="app/routers/appointments.py inline (extraction pending)",
        requires_staff_confirmation=False,
        allowed_authors=(DiaryActionAuthor.bernie,),
    ),
    BernieCapability(
        name="get_patient_booking_context",
        tier=BernieCapabilityTier.read_only,
        summary="Fetch the compact recognized-patient booking context (recent/future bookings).",
        implemented_as="app.services.bernie.context.build_patient_booking_context",
        requires_staff_confirmation=False,
        allowed_authors=(
            DiaryActionAuthor.staff_ui,
            DiaryActionAuthor.bernie,
            DiaryActionAuthor.rayleen,
            DiaryActionAuthor.davida,
        ),
    ),
    BernieCapability(
        name="find_slots",
        tier=BernieCapabilityTier.read_only,
        summary="Deterministic slot search over roster/schedule; never LLM-driven.",
        implemented_as="POST /appointments/proposals/slot-search + supervised wrapper",
        requires_staff_confirmation=False,
        allowed_authors=(
            DiaryActionAuthor.staff_ui,
            DiaryActionAuthor.bernie,
            DiaryActionAuthor.rayleen,
            DiaryActionAuthor.davida,
        ),
    ),
    BernieCapability(
        name="explain_schedule",
        tier=BernieCapabilityTier.read_only,
        summary="Explain why a day has no slots (no roster row, day off, breaks, fully booked).",
        implemented_as=None,
        requires_staff_confirmation=False,
        allowed_authors=(
            DiaryActionAuthor.staff_ui,
            DiaryActionAuthor.bernie,
            DiaryActionAuthor.rayleen,
            DiaryActionAuthor.davida,
        ),
    ),
    BernieCapability(
        name="suggest_next_actions",
        tier=BernieCapabilityTier.read_only,
        summary="Offer typed next-step suggestion chips after no-slot/exhausted outcomes.",
        implemented_as="app/routers/appointments.py _build_no_slot_suggestions + selection endpoint",
        requires_staff_confirmation=False,
        allowed_authors=(
            DiaryActionAuthor.staff_ui,
            DiaryActionAuthor.bernie,
            DiaryActionAuthor.rayleen,
            DiaryActionAuthor.davida,
            DiaryActionAuthor.system,
        ),
    ),
    BernieCapability(
        name="propose_booking",
        tier=BernieCapabilityTier.propose,
        summary="Prepare a typed booking proposal for staff review; writes nothing.",
        implemented_as="supervised-booking wrapper (app/routers/appointments.py)",
        requires_staff_confirmation=True,
        allowed_authors=(DiaryActionAuthor.staff_ui, DiaryActionAuthor.bernie),
    ),
    BernieCapability(
        name="propose_edit",
        tier=BernieCapabilityTier.propose,
        summary="Prepare a typed appointment-edit proposal for staff review.",
        implemented_as="existing appointment update/move/resize proposal endpoints",
        requires_staff_confirmation=True,
        allowed_authors=(DiaryActionAuthor.staff_ui, DiaryActionAuthor.bernie),
    ),
    BernieCapability(
        name="propose_cancel",
        tier=BernieCapabilityTier.propose,
        summary="Prepare a typed appointment-cancellation proposal for staff review.",
        implemented_as="existing appointment cancel proposal endpoint",
        requires_staff_confirmation=True,
        allowed_authors=(DiaryActionAuthor.staff_ui, DiaryActionAuthor.bernie),
    ),
    BernieCapability(
        name="propose_status",
        tier=BernieCapabilityTier.propose,
        summary="Prepare a typed appointment status-change proposal for staff review.",
        implemented_as="existing appointment status proposal endpoints",
        requires_staff_confirmation=True,
        allowed_authors=(
            DiaryActionAuthor.staff_ui,
            DiaryActionAuthor.bernie,
            DiaryActionAuthor.rayleen,
        ),
    ),
    BernieCapability(
        name="confirm_booking",
        tier=BernieCapabilityTier.confirm,
        summary="Create the appointment from a staff-confirmed proposal behind the evidence/freshness gate.",
        implemented_as="POST /appointments/proposals/create/confirm-bernie",
        requires_staff_confirmation=True,
        allowed_authors=(DiaryActionAuthor.staff_ui,),
    ),
    BernieCapability(
        name="handoff_to_receptionist",
        tier=BernieCapabilityTier.meta,
        summary="End Bernie involvement and hand the request to reception staff.",
        implemented_as=None,
        requires_staff_confirmation=False,
        allowed_authors=(
            DiaryActionAuthor.staff_ui,
            DiaryActionAuthor.bernie,
            DiaryActionAuthor.rayleen,
            DiaryActionAuthor.davida,
            DiaryActionAuthor.system,
        ),
    ),
)


def get_bernie_capability(name: str) -> Optional[BernieCapability]:
    """Look up a capability by name; None when unregistered."""
    for capability in BERNIE_CAPABILITY_REGISTRY:
        if capability.name == name:
            return capability
    return None


__all__ = [
    "BernieCapability",
    "BernieCapabilityTier",
    "BERNIE_CAPABILITY_REGISTRY",
    "get_bernie_capability",
]
