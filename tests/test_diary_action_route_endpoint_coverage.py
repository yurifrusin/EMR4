"""Route-table coverage checks for the Diary action route contract."""

from fastapi.routing import APIRoute
from fastapi.dependencies.utils import get_flat_dependant

from app.dependencies import get_current_user
from app.main import app
from app.services.diary.action_grammar import DiaryActionVerb
from app.services.diary.action_route_contract import (
    DIARY_ACTION_ROUTE_CONTRACTS,
    RouteAuthority,
)
from scripts.appointment_route_inventory_preflight import (
    APPOINTMENT_PREFIX,
    build_appointment_route_inventory_preflight,
)


def _ordered_api_routes() -> tuple[APIRoute, ...]:
    return tuple(route for route in app.routes if isinstance(route, APIRoute))


def _mounted_routes() -> dict[str, set[str]]:
    mounted: dict[str, set[str]] = {}
    for route in _ordered_api_routes():
        mounted.setdefault(route.path, set()).update(
            set(route.methods or set()) - {"HEAD", "OPTIONS"}
        )
    return mounted


def _route_method_rows(path: str, methods: set[str]) -> tuple[APIRoute, ...]:
    return tuple(
        route
        for route in _ordered_api_routes()
        if route.path == path and _route_methods(route) & methods
    )


def _route_methods(route: APIRoute) -> set[str]:
    return set(route.methods or set()) - {"HEAD", "OPTIONS"}


def _route_dependency_calls(route: APIRoute) -> tuple[object, ...]:
    flat = get_flat_dependant(route.dependant)
    return tuple(
        dependency.call
        for dependency in flat.dependencies
        if dependency.call is not None
    )


def _has_get_current_user_dependency(route: APIRoute) -> bool:
    return any(call is get_current_user for call in _route_dependency_calls(route))


def _has_require_role_dependency(route: APIRoute) -> bool:
    return any(
        getattr(call, "__qualname__", "") == "require_role.<locals>.checker"
        for call in _route_dependency_calls(route)
    )


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


def _segments(path: str) -> tuple[str, ...]:
    return tuple(segment for segment in path.split("/") if segment)


def _is_path_parameter(segment: str) -> bool:
    return segment.startswith("{") and segment.endswith("}")


def _parametric_route_would_capture(route_path: str, literal_path: str) -> bool:
    route_segments = _segments(route_path)
    literal_segments = _segments(literal_path)
    if len(route_segments) != len(literal_segments):
        return False
    if not any(_is_path_parameter(segment) for segment in route_segments):
        return False
    return all(
        _is_path_parameter(route_segment) or route_segment == literal_segment
        for route_segment, literal_segment in zip(route_segments, literal_segments)
    )


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


def test_contract_paths_have_no_duplicate_method_mounts():
    seen: dict[tuple[str, str], list[str]] = {}
    contract_paths = {path for _verb, _group_name, path in _all_contract_routes()}

    for route in _ordered_api_routes():
        if route.path not in contract_paths:
            continue
        for method in route.methods or set():
            seen.setdefault((route.path, method), []).append(route.name)

    duplicates = {
        f"{method} {path}: {names}"
        for (path, method), names in seen.items()
        if len(names) > 1
    }

    assert not duplicates


def test_contract_literal_paths_are_not_shadowed_by_earlier_parametric_routes():
    routes = _ordered_api_routes()
    route_indexes: dict[str, int] = {}
    for index, route in enumerate(routes):
        route_indexes.setdefault(route.path, index)

    shadowed = []
    for verb, group_name, path in _all_contract_routes():
        if "{" in path:
            continue
        route_index = route_indexes[path]
        target_methods = _mounted_routes()[path]
        for earlier in routes[:route_index]:
            overlapping_methods = target_methods & (earlier.methods or set())
            if not overlapping_methods:
                continue
            if _parametric_route_would_capture(earlier.path, path):
                shadowed.append(
                    f"{verb.value}:{group_name}:{path} shadowed by "
                    f"{sorted(overlapping_methods)} {earlier.path}"
                )

    assert not shadowed


def test_proposal_and_confirm_contract_routes_are_post_only():
    mounted = _mounted_routes()

    extra_methods = []
    for verb, group_name, path in _all_contract_routes():
        if group_name not in {"proposal_routes", "confirm_routes"}:
            continue
        methods = mounted[path] - {"HEAD", "OPTIONS"}
        if methods != {"POST"}:
            extra_methods.append(f"{verb.value}:{group_name}:{path}:{sorted(methods)}")

    assert not extra_methods


def test_read_contract_routes_do_not_expose_update_or_delete_methods():
    mounted = _mounted_routes()
    mutation_methods = {"PUT", "PATCH", "DELETE"}

    unsafe_read_routes = []
    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        for path in contract.read_routes:
            exposed = mounted[path] & mutation_methods
            if exposed:
                unsafe_read_routes.append(f"{verb.value}:{path}:{sorted(exposed)}")

    assert not unsafe_read_routes


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


def test_planned_proposal_routes_do_not_overlap_executable_targets():
    executable_targets = set()
    planned_verbs = []

    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        if contract.authority is RouteAuthority.signed_confirm:
            executable_targets.update(contract.confirm_routes)
            executable_targets.update(contract.raw_mutation_routes)
        if contract.authority is RouteAuthority.planned_not_implemented:
            planned_verbs.append(verb)

    overlaps = []
    for verb in planned_verbs:
        contract = DIARY_ACTION_ROUTE_CONTRACTS[verb]
        for route in contract.proposal_routes:
            if route in executable_targets:
                overlaps.append(f"{verb.value}:{route}")

    assert not overlaps


def test_contract_route_surfaces_remain_disjoint_by_behavior_role():
    overlaps = []

    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        read_routes = set(contract.read_routes)
        proposal_routes = set(contract.proposal_routes)
        confirm_routes = set(contract.confirm_routes)
        raw_mutation_routes = set(contract.raw_mutation_routes)
        write_routes = proposal_routes | confirm_routes | raw_mutation_routes

        if read_routes & write_routes:
            overlaps.append(f"{verb.value}:read/write:{sorted(read_routes & write_routes)}")
        if contract.authority is RouteAuthority.signed_confirm:
            if confirm_routes & raw_mutation_routes:
                overlaps.append(
                    f"{verb.value}:confirm/raw:{sorted(confirm_routes & raw_mutation_routes)}"
                )
            if proposal_routes & confirm_routes:
                overlaps.append(
                    f"{verb.value}:proposal/confirm:{sorted(proposal_routes & confirm_routes)}"
                )

    assert not overlaps


def test_out_of_contract_post_sub_family_counts_match_route_table_gaps():
    mounted = _mounted_routes()
    route_rows = {
        (method, path)
        for path, methods in mounted.items()
        if path.startswith(APPOINTMENT_PREFIX)
        for method in methods
    }
    contract_rows: set[tuple[str, str]] = set()

    for contract in DIARY_ACTION_ROUTE_CONTRACTS.values():
        for path in contract.read_routes:
            for method in mounted.get(path, set()):
                contract_rows.add((method, path))
        for path in contract.proposal_routes + contract.confirm_routes:
            if "POST" in mounted.get(path, set()):
                contract_rows.add(("POST", path))
        for path in contract.raw_mutation_routes:
            for method in mounted.get(path, set()) & {"POST", "PUT", "PATCH", "DELETE"}:
                contract_rows.add((method, path))

    uncovered_post_paths = {
        path
        for method, path in route_rows - contract_rows
        if method == "POST"
    }
    proposal_support_count = sum(
        1 for path in uncovered_post_paths if "/proposals/" in path
    )
    state_tracking_count = sum(
        1 for path in uncovered_post_paths if "/bernie/sessions" in path
    )
    ambiguous_count = (
        len(uncovered_post_paths) - proposal_support_count - state_tracking_count
    )

    report = build_appointment_route_inventory_preflight()
    sub_family_counts = report["out_of_contract_post_by_sub_family"]

    assert proposal_support_count == sub_family_counts["proposal_support_post"]
    assert state_tracking_count == sub_family_counts["state_tracking_post"]
    assert ambiguous_count == sub_family_counts.get("ambiguous_post", 0)
    assert len(uncovered_post_paths) == report["out_of_contract_post_route_method_count"]


def test_documented_write_contract_routes_are_auth_and_role_gated():
    write_methods = {"POST", "PUT", "PATCH", "DELETE"}
    missing_mounts = []
    missing_auth = []
    missing_role_gate = []

    for verb, contract in DIARY_ACTION_ROUTE_CONTRACTS.items():
        for group_name in ("proposal_routes", "confirm_routes"):
            for path in getattr(contract, group_name):
                routes = _route_method_rows(path, {"POST"})
                if not routes:
                    missing_mounts.append(f"{verb.value}:{group_name}:POST:{path}")
                    continue
                for route in routes:
                    if not _has_get_current_user_dependency(route):
                        missing_auth.append(f"{verb.value}:{group_name}:POST:{path}")
                    if not _has_require_role_dependency(route):
                        missing_role_gate.append(f"{verb.value}:{group_name}:POST:{path}")

        for path in contract.raw_mutation_routes:
            routes = _route_method_rows(path, write_methods)
            if not routes:
                missing_mounts.append(f"{verb.value}:raw_mutation_routes:{path}")
                continue
            for route in routes:
                methods = sorted(_route_methods(route) & write_methods)
                row = f"{verb.value}:raw_mutation_routes:{methods}:{path}"
                if not _has_get_current_user_dependency(route):
                    missing_auth.append(row)
                if not _has_require_role_dependency(route):
                    missing_role_gate.append(row)

    assert not missing_mounts
    assert not missing_auth
    assert not missing_role_gate


def test_contract_route_table_scan_does_not_issue_requests_or_grant_authority():
    mounted = _mounted_routes()

    assert mounted
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].read_routes == ()
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].proposal_routes == ()
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].confirm_routes == ()
    assert DIARY_ACTION_ROUTE_CONTRACTS[DiaryActionVerb.handoff].raw_mutation_routes == ()
