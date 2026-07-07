"""Route-table coverage checks for the Diary action route contract."""

from fastapi.routing import APIRoute

from app.main import app
from app.services.diary.action_grammar import DiaryActionVerb
from app.services.diary.action_route_contract import (
    DIARY_ACTION_ROUTE_CONTRACTS,
    RouteAuthority,
)


def _mounted_routes() -> dict[str, set[str]]:
    mounted: dict[str, set[str]] = {}
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        mounted.setdefault(route.path, set()).update(route.methods or set())
    return mounted


def _all_contract_routes() -> tuple[tuple[DiaryActionVerb, str, str], ...]:
    rows: list[tuple[DiaryActionVerb, str, str]] = []
    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        for group_name in (
            "read_routes",
            "proposal_routes",
            "confirm_routes",
            "raw_mutation_routes",
        ):
            for path in getattr(contract, group_name):
                rows.append((verb, group_name, path))
    return tuple(rows)


def test_all_documented_action_contract_routes_are_mounted():
    mounted = _mounted_routes()

    missing = [
        f"{verb.value}:{group_name}:{path}"
        for verb, group_name, path in _all_contract_routes()
        if path not in mounted
    ]

    assert not missing


def test_documented_action_contract_route_methods_match_authority():
    mounted = _mounted_routes()

    for _verb, group_name, path in _all_contract_routes():
        methods = mounted[path]
        if group_name in {"proposal_routes", "confirm_routes"}:
            assert "POST" in methods, f"{group_name} {path!r} must be POST-mounted"
        if group_name == "read_routes":
            assert "GET" in methods or "POST" in methods
        if group_name == "raw_mutation_routes":
            assert methods & {"POST", "PUT", "PATCH", "DELETE"}


def test_planned_actions_remain_without_confirm_route_authority():
    planned = {
        DiaryActionVerb.check_in,
        DiaryActionVerb.waiting_area_move,
        DiaryActionVerb.link_patient,
    }
    mounted = _mounted_routes()

    for verb in planned:
        contract = DIARY_ACTION_ROUTE_CONTRACTS[verb]
        assert contract.authority is RouteAuthority.planned_not_implemented
        assert contract.confirm_routes == ()
        assert contract.raw_mutation_routes == ()
        for route in contract.proposal_routes + contract.read_routes:
            assert route in mounted


def test_contract_route_table_scan_does_not_issue_requests_or_grant_authority():
    mounted = _mounted_routes()

    assert mounted
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].read_routes == ()
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].proposal_routes == ()
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].confirm_routes == ()
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].raw_mutation_routes == ()
