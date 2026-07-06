"""Tests for the H37 diary grammar-to-route contract inventory."""

import inspect

from app.services.diary.action_grammar import DIARY_ACTION_GRAMMAR, DiaryActionVerb
from app.services.diary.action_route_contract import (
    DIARY_ACTION_ROUTE_CONTRACTS,
    ROUTE_CONTRACT_SCHEMA_VERSION,
    RouteAuthority,
    assert_route_contract_consistency,
    get_action_route_contract,
)
from app.services.diary.capabilities import BernieCapabilityTier
from app.services.diary.confirm_actions import DIARY_CONFIRM_ACTIONS


def test_route_contract_schema_version_pinned():
    assert ROUTE_CONTRACT_SCHEMA_VERSION == "diary.action_route_contract.v1"


def test_route_contract_covers_every_grammar_verb_exactly():
    assert set(DIARY_ACTION_ROUTE_CONTRACTS) == set(DiaryActionVerb)
    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        assert contract.verb is verb


def test_route_contract_consistency_passes():
    assert_route_contract_consistency()


def test_implemented_confirm_verbs_map_to_signed_confirm_routes():
    for verb, descriptor in DIARY_ACTION_GRAMMAR.items():
        contract = get_action_route_contract(verb)
        if descriptor.tier is BernieCapabilityTier.confirm and descriptor.implemented:
            assert contract.authority is RouteAuthority.signed_confirm
            assert contract.confirm_actions == descriptor.confirm_actions
            assert contract.proposal_routes
            assert contract.confirm_routes
            for action in descriptor.confirm_actions:
                assert DIARY_CONFIRM_ACTIONS[action].endpoint in contract.confirm_routes


def test_planned_confirm_verbs_have_no_confirm_route_authority():
    planned = {
        DiaryActionVerb.check_in,
        DiaryActionVerb.waiting_area_move,
        DiaryActionVerb.link_patient,
    }
    for verb in planned:
        descriptor = DIARY_ACTION_GRAMMAR[verb]
        contract = get_action_route_contract(verb)

        assert descriptor.tier is BernieCapabilityTier.confirm
        assert descriptor.implemented is False
        assert descriptor.confirm_actions == ()
        assert contract.authority is RouteAuthority.planned_not_implemented
        assert contract.confirm_actions == ()
        assert contract.confirm_routes == ()


def test_adjacent_planned_routes_do_not_make_planned_verbs_executable():
    check_in = get_action_route_contract(DiaryActionVerb.check_in)
    waiting_area = get_action_route_contract(DiaryActionVerb.waiting_area_move)

    assert check_in.read_routes
    assert check_in.proposal_routes
    assert check_in.confirm_routes == ()

    assert waiting_area.read_routes
    assert waiting_area.proposal_routes
    assert waiting_area.confirm_routes == ()


def test_read_only_and_meta_contracts_have_no_write_authority():
    for verb in (DiaryActionVerb.slot_search, DiaryActionVerb.explain_schedule, DiaryActionVerb.handoff):
        descriptor = DIARY_ACTION_GRAMMAR[verb]
        contract = get_action_route_contract(verb)

        assert descriptor.mutating is False
        assert descriptor.requires_staff_confirmation is False
        assert descriptor.confirm_actions == ()
        assert contract.authority in {RouteAuthority.read_only, RouteAuthority.meta}
        assert contract.proposal_routes == ()
        assert contract.confirm_routes == ()
        assert contract.raw_mutation_routes == ()


def test_route_contract_module_is_static_and_side_effect_free():
    import app.services.diary.action_route_contract as route_contract_module

    source = inspect.getsource(route_contract_module)
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
