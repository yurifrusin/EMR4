"""Promotion checklist for planned diary grammar actions.

This module defines the gates that must be satisfied before a planned
``DiaryActionVerb`` may become implemented. It is static metadata only: no
dispatch, routes, database access, provider calls, or write authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.services.diary.action_grammar import DIARY_ACTION_GRAMMAR, DiaryActionVerb
from app.services.diary.action_route_contract import DIARY_ACTION_ROUTE_CONTRACTS, RouteAuthority
from app.services.diary.capabilities import BernieCapabilityTier

PROMOTION_SCHEMA_VERSION = "diary.planned_action_promotion.v1"

PLANNED_ACTION_VERBS = (
    DiaryActionVerb.check_in,
    DiaryActionVerb.waiting_area_move,
    DiaryActionVerb.link_patient,
)


class PromotionGate(str, Enum):
    route_contract = "route_contract"
    signed_confirm_action = "signed_confirm_action"
    signed_evidence = "signed_evidence"
    audit_contract = "audit_contract"
    staff_confirmation_affordance = "staff_confirmation_affordance"
    role_and_tenancy_policy = "role_and_tenancy_policy"
    ui_affordance = "ui_affordance"
    regression_tests = "regression_tests"


@dataclass(frozen=True)
class PlannedActionPromotionChecklist:
    verb: DiaryActionVerb
    required_gates: tuple[PromotionGate, ...]
    minimum_tests: tuple[str, ...]
    notes: str


_COMMON_GATES = (
    PromotionGate.route_contract,
    PromotionGate.signed_confirm_action,
    PromotionGate.signed_evidence,
    PromotionGate.audit_contract,
    PromotionGate.staff_confirmation_affordance,
    PromotionGate.role_and_tenancy_policy,
    PromotionGate.ui_affordance,
    PromotionGate.regression_tests,
)


PLANNED_ACTION_PROMOTION_CHECKLISTS: dict[DiaryActionVerb, PlannedActionPromotionChecklist] = {
    DiaryActionVerb.check_in: PlannedActionPromotionChecklist(
        verb=DiaryActionVerb.check_in,
        required_gates=_COMMON_GATES,
        minimum_tests=(
            "check_in_proposal_is_non_mutating",
            "check_in_confirm_requires_signed_evidence",
            "check_in_confirm_writes_status_and_waiting_area_atomically",
            "check_in_confirm_audits_actor_route_and_evidence",
            "check_in_rejects_cross_practice_or_inactive_waiting_area",
            "bernie_check_in_cannot_bypass_staff_confirmation",
        ),
        notes=(
            "Promotion requires a dedicated signed check-in confirm action or an explicitly "
            "reviewed status-confirm binding that records check-in semantics."
        ),
    ),
    DiaryActionVerb.waiting_area_move: PlannedActionPromotionChecklist(
        verb=DiaryActionVerb.waiting_area_move,
        required_gates=_COMMON_GATES,
        minimum_tests=(
            "waiting_area_proposal_is_non_mutating",
            "waiting_area_confirm_requires_signed_evidence",
            "waiting_area_confirm_rejects_cross_practice_or_inactive_area",
            "waiting_area_confirm_audits_previous_and_new_area",
            "terminal_status_cannot_reenter_active_waiting_area",
            "bernie_waiting_area_move_cannot_bypass_staff_confirmation",
        ),
        notes="Promotion requires a signed confirm action for waiting-area movement.",
    ),
    DiaryActionVerb.link_patient: PlannedActionPromotionChecklist(
        verb=DiaryActionVerb.link_patient,
        required_gates=_COMMON_GATES,
        minimum_tests=(
            "link_patient_proposal_is_non_mutating",
            "link_patient_confirm_requires_signed_evidence",
            "link_patient_confirm_rejects_cross_practice_patient",
            "link_patient_confirm_preserves_existing_appointment_time_and_status",
            "link_patient_confirm_audits_previous_identity_state",
            "bernie_link_patient_cannot_bypass_staff_confirmation",
        ),
        notes="Promotion requires identity-specific role policy and audit wording before any write path.",
    ),
}


def get_planned_action_promotion_checklist(
    verb: DiaryActionVerb,
) -> PlannedActionPromotionChecklist:
    return PLANNED_ACTION_PROMOTION_CHECKLISTS[verb]


def assert_promotion_checklists_consistent() -> None:
    assert set(PLANNED_ACTION_PROMOTION_CHECKLISTS) == set(PLANNED_ACTION_VERBS)

    for verb, checklist in PLANNED_ACTION_PROMOTION_CHECKLISTS.items():
        descriptor = DIARY_ACTION_GRAMMAR[verb]
        route_contract = DIARY_ACTION_ROUTE_CONTRACTS[verb]

        assert checklist.verb is verb
        assert descriptor.tier is BernieCapabilityTier.confirm
        assert descriptor.mutating is True
        assert descriptor.requires_staff_confirmation is True
        assert descriptor.implemented is False
        assert descriptor.confirm_actions == ()
        assert route_contract.authority is RouteAuthority.planned_not_implemented
        assert route_contract.confirm_actions == ()
        assert route_contract.confirm_routes == ()
        assert route_contract.raw_mutation_routes == ()
        assert set(checklist.required_gates) == set(PromotionGate)
        assert len(checklist.minimum_tests) >= 5


__all__ = [
    "PROMOTION_SCHEMA_VERSION",
    "PLANNED_ACTION_VERBS",
    "PromotionGate",
    "PlannedActionPromotionChecklist",
    "PLANNED_ACTION_PROMOTION_CHECKLISTS",
    "get_planned_action_promotion_checklist",
    "assert_promotion_checklists_consistent",
]
