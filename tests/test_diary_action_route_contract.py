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


MUTATING_ROUTE_MARKERS = (
    "/proposals/create",
    "/proposals/update",
    "/proposals/status",
    "/proposals/waiting-area",
    "/proposals/delete",
    "/confirm",
    "-confirm",
    "/api/v1/appointments/{appointment_id}",
)


def _all_contract_routes(contract):
    return (
        contract.read_routes
        + contract.proposal_routes
        + contract.confirm_routes
        + contract.raw_mutation_routes
    )


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


def test_read_only_and_meta_routes_do_not_point_at_mutating_surfaces():
    for verb in (DiaryActionVerb.slot_search, DiaryActionVerb.explain_schedule, DiaryActionVerb.handoff):
        contract = get_action_route_contract(verb)

        for route in _all_contract_routes(contract):
            assert not any(marker in route for marker in MUTATING_ROUTE_MARKERS), (
                f"{verb.value} read-only/meta route {route!r} points at a mutating surface"
            )


def test_signed_confirm_contracts_keep_proposal_and_confirm_paths_separate():
    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        if contract.authority is not RouteAuthority.signed_confirm:
            continue

        assert contract.proposal_routes, f"{verb.value} must retain a proposal route"
        assert contract.confirm_routes, f"{verb.value} must retain a signed confirm route"
        assert contract.raw_mutation_routes, f"{verb.value} should document adjacent raw mutation routes"

        for route in contract.proposal_routes:
            assert "/proposals/" in route
            assert "confirm" not in route
        for route in contract.confirm_routes:
            assert "confirm" in route


def test_mutating_implemented_contracts_do_not_rely_only_on_raw_mutation_routes():
    for verb, descriptor in DIARY_ACTION_GRAMMAR.items():
        contract = get_action_route_contract(verb)
        if descriptor.mutating and descriptor.implemented:
            assert contract.authority is RouteAuthority.signed_confirm
            assert contract.confirm_routes
            assert contract.confirm_actions


def test_planned_mutating_contracts_may_have_proposals_but_not_confirm_or_raw_mutation_routes():
    for verb in (DiaryActionVerb.check_in, DiaryActionVerb.waiting_area_move, DiaryActionVerb.link_patient):
        contract = get_action_route_contract(verb)

        assert contract.authority is RouteAuthority.planned_not_implemented
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
