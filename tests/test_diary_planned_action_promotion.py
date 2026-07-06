"""Tests for the H39 planned action promotion checklist."""

import inspect

from app.services.diary.action_grammar import DIARY_ACTION_GRAMMAR, DiaryActionVerb
from app.services.diary.action_route_contract import DIARY_ACTION_ROUTE_CONTRACTS, RouteAuthority
from app.services.diary.planned_action_promotion import (
    PLANNED_ACTION_PROMOTION_CHECKLISTS,
    PLANNED_ACTION_VERBS,
    PROMOTION_SCHEMA_VERSION,
    PromotionGate,
    assert_promotion_checklists_consistent,
    get_planned_action_promotion_checklist,
)


def test_promotion_schema_version_pinned():
    assert PROMOTION_SCHEMA_VERSION == "diary.planned_action_promotion.v1"


def test_promotion_checklists_cover_only_planned_action_verbs():
    assert set(PLANNED_ACTION_VERBS) == {
        DiaryActionVerb.check_in,
        DiaryActionVerb.waiting_area_move,
        DiaryActionVerb.link_patient,
    }
    assert set(PLANNED_ACTION_PROMOTION_CHECKLISTS) == set(PLANNED_ACTION_VERBS)


def test_promotion_checklist_consistency_passes():
    assert_promotion_checklists_consistent()


def test_each_planned_action_requires_every_promotion_gate():
    for verb in PLANNED_ACTION_VERBS:
        checklist = get_planned_action_promotion_checklist(verb)
        assert set(checklist.required_gates) == set(PromotionGate)


def test_planned_actions_remain_non_executable_until_promoted():
    for verb in PLANNED_ACTION_VERBS:
        descriptor = DIARY_ACTION_GRAMMAR[verb]
        route_contract = DIARY_ACTION_ROUTE_CONTRACTS[verb]

        assert descriptor.implemented is False
        assert descriptor.confirm_actions == ()
        assert route_contract.authority is RouteAuthority.planned_not_implemented
        assert route_contract.confirm_actions == ()
        assert route_contract.confirm_routes == ()
        assert route_contract.raw_mutation_routes == ()


def test_each_checklist_names_signed_evidence_audit_and_staff_confirmation_tests():
    required_fragments = ("signed_evidence", "audit", "staff_confirmation")
    for verb, checklist in PLANNED_ACTION_PROMOTION_CHECKLISTS.items():
        joined_tests = " ".join(checklist.minimum_tests)
        for fragment in required_fragments:
            assert fragment in joined_tests, f"{verb.value} missing test fragment {fragment!r}"


def test_checklist_module_is_static_and_side_effect_free():
    import app.services.diary.planned_action_promotion as promotion_module

    source = inspect.getsource(promotion_module)
    forbidden = [
        "app.routers",
        "app.models",
        "SessionLocal",
        "get_db",
        "TestClient",
        "google.genai",
        "google.generativeai",
        "vertexai",
        "openai",
        "anthropic",
        "local_data",
        "historical_diary_semantic_candidate_builder",
        "h15_semantic_candidates",
    ]
    for fragment in forbidden:
        assert fragment not in source
