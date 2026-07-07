"""Read-only inventory linking diary grammar verbs to current route authority.

This module is documentation-as-code for the current bridge between
``DiaryActionVerb`` and backend routes. It does not dispatch, import routers,
touch the database, call providers, or grant write authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.services.diary.action_grammar import DIARY_ACTION_GRAMMAR, DiaryActionVerb
from app.services.diary.capabilities import BernieCapabilityTier
from app.services.diary.confirm_actions import DIARY_CONFIRM_ACTIONS, DiaryConfirmAction

ROUTE_CONTRACT_SCHEMA_VERSION = "diary.action_route_contract.v1"


class RouteAuthority(str, Enum):
    """Current implementation authority for a grammar verb."""

    signed_confirm = "signed_confirm"
    read_only = "read_only"
    meta = "meta"
    planned_not_implemented = "planned_not_implemented"


@dataclass(frozen=True)
class DiaryActionRouteContract:
    """Static route inventory for one DiaryActionVerb."""

    verb: DiaryActionVerb
    authority: RouteAuthority
    confirm_actions: tuple[DiaryConfirmAction, ...] = ()
    read_routes: tuple[str, ...] = ()
    proposal_routes: tuple[str, ...] = ()
    confirm_routes: tuple[str, ...] = ()
    raw_mutation_routes: tuple[str, ...] = ()
    notes: str = ""


DIARY_ACTION_ROUTE_CONTRACTS: dict[DiaryActionVerb, DiaryActionRouteContract] = {
    DiaryActionVerb.create: DiaryActionRouteContract(
        verb=DiaryActionVerb.create,
        authority=RouteAuthority.signed_confirm,
        confirm_actions=(DiaryConfirmAction.staff_create, DiaryConfirmAction.bernie_create),
        proposal_routes=("/api/v1/appointments/proposals/create",),
        confirm_routes=(
            DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.staff_create].endpoint,
            DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.bernie_create].endpoint,
        ),
        raw_mutation_routes=("/api/v1/appointments",),
        notes="Create is executable only through proposal plus signed confirmation for grammar dispatch.",
    ),
    DiaryActionVerb.move: DiaryActionRouteContract(
        verb=DiaryActionVerb.move,
        authority=RouteAuthority.signed_confirm,
        confirm_actions=(DiaryConfirmAction.update,),
        proposal_routes=("/api/v1/appointments/proposals/update/{appointment_id}",),
        confirm_routes=(DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.update].endpoint,),
        raw_mutation_routes=("/api/v1/appointments/{appointment_id}",),
        notes="Move shares the update proposal/confirm route with resize.",
    ),
    DiaryActionVerb.resize: DiaryActionRouteContract(
        verb=DiaryActionVerb.resize,
        authority=RouteAuthority.signed_confirm,
        confirm_actions=(DiaryConfirmAction.update,),
        proposal_routes=("/api/v1/appointments/proposals/update/{appointment_id}",),
        confirm_routes=(DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.update].endpoint,),
        raw_mutation_routes=("/api/v1/appointments/{appointment_id}",),
        notes="Resize shares the update proposal/confirm route with move.",
    ),
    DiaryActionVerb.cancel: DiaryActionRouteContract(
        verb=DiaryActionVerb.cancel,
        authority=RouteAuthority.signed_confirm,
        confirm_actions=(DiaryConfirmAction.delete,),
        proposal_routes=("/api/v1/appointments/proposals/delete/{appointment_id}",),
        confirm_routes=(DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.delete].endpoint,),
        raw_mutation_routes=("/api/v1/appointments/{appointment_id}",),
        notes="Cancel/delete is executable only through signed delete confirmation for grammar dispatch.",
    ),
    DiaryActionVerb.status_change: DiaryActionRouteContract(
        verb=DiaryActionVerb.status_change,
        authority=RouteAuthority.signed_confirm,
        confirm_actions=(DiaryConfirmAction.status,),
        proposal_routes=("/api/v1/appointments/proposals/status/{appointment_id}",),
        confirm_routes=(DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.status].endpoint,),
        raw_mutation_routes=("/api/v1/appointments/{appointment_id}/status",),
        notes="Status changes include waiting-area side-effect checks in the proposal/confirm path.",
    ),
    DiaryActionVerb.check_in: DiaryActionRouteContract(
        verb=DiaryActionVerb.check_in,
        authority=RouteAuthority.planned_not_implemented,
        read_routes=("/api/v1/appointments/{appointment_id}/checkin-defaults",),
        proposal_routes=("/api/v1/appointments/proposals/status/{appointment_id}",),
        notes="Adjacent status proposal and check-in default routes exist, but no check-in confirm action exists.",
    ),
    DiaryActionVerb.waiting_area_move: DiaryActionRouteContract(
        verb=DiaryActionVerb.waiting_area_move,
        authority=RouteAuthority.planned_not_implemented,
        read_routes=("/api/v1/appointments/waiting-room",),
        proposal_routes=("/api/v1/appointments/proposals/waiting-area/{appointment_id}",),
        notes="A non-mutating waiting-area proposal exists, but no signed waiting-area confirm action exists.",
    ),
    DiaryActionVerb.link_patient: DiaryActionRouteContract(
        verb=DiaryActionVerb.link_patient,
        authority=RouteAuthority.planned_not_implemented,
        notes="No signed patient-link confirm action exists for diary grammar dispatch.",
    ),
    DiaryActionVerb.slot_search: DiaryActionRouteContract(
        verb=DiaryActionVerb.slot_search,
        authority=RouteAuthority.read_only,
        read_routes=("/api/v1/appointments/proposals/bernie/interpret-booking-instruction",),
        notes="Slot search may read availability through existing Bernie interpretation/proposal flow only.",
    ),
    DiaryActionVerb.explain_schedule: DiaryActionRouteContract(
        verb=DiaryActionVerb.explain_schedule,
        authority=RouteAuthority.read_only,
        read_routes=("/api/v1/appointments/dev/h15-read-only-explanation-preview",),
        notes="The H15 preview route is dev-only static metadata and not live diary authority.",
    ),
    DiaryActionVerb.handoff: DiaryActionRouteContract(
        verb=DiaryActionVerb.handoff,
        authority=RouteAuthority.meta,
        notes="Meta workflow control only; no diary mutation route.",
    ),
}


def get_action_route_contract(verb: DiaryActionVerb) -> DiaryActionRouteContract:
    """Return the static route contract for one grammar verb."""

    return DIARY_ACTION_ROUTE_CONTRACTS[verb]


def assert_route_contract_consistency() -> None:
    """Assert that the route inventory matches the current grammar contract."""

    assert set(DIARY_ACTION_ROUTE_CONTRACTS) == set(DiaryActionVerb)

    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        descriptor = DIARY_ACTION_GRAMMAR[verb]
        assert contract.verb is verb

        if contract.authority is RouteAuthority.signed_confirm:
            assert descriptor.tier is BernieCapabilityTier.confirm
            assert descriptor.implemented is True
            assert descriptor.confirm_actions == contract.confirm_actions
            assert contract.confirm_routes
            for action in contract.confirm_actions:
                assert DIARY_CONFIRM_ACTIONS[action].endpoint in contract.confirm_routes

        if contract.authority is RouteAuthority.planned_not_implemented:
            assert descriptor.tier is BernieCapabilityTier.confirm
            assert descriptor.implemented is False
            assert descriptor.confirm_actions == ()
            assert contract.confirm_actions == ()
            assert contract.confirm_routes == ()

        if contract.authority in (RouteAuthority.read_only, RouteAuthority.meta):
            assert descriptor.mutating is False
            assert descriptor.requires_staff_confirmation is False
            assert descriptor.confirm_actions == ()
            assert contract.confirm_actions == ()
            assert contract.confirm_routes == ()


__all__ = [
    "ROUTE_CONTRACT_SCHEMA_VERSION",
    "RouteAuthority",
    "DiaryActionRouteContract",
    "DIARY_ACTION_ROUTE_CONTRACTS",
    "get_action_route_contract",
    "assert_route_contract_consistency",
]
