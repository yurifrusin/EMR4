"""Safe aggregate inventory for mounted appointment routes.

This preflight inspects FastAPI route metadata only. It does not issue HTTP
requests, execute handlers, open database sessions, or classify runtime
authority.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from fastapi.routing import APIRoute

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.main import app
from app.services.diary.action_route_contract import DIARY_ACTION_ROUTE_CONTRACTS
from app.services.diary.action_route_contract import RouteAuthority

REPORT_SCHEMA_VERSION = "appointment.route_inventory_preflight.v1"
APPOINTMENT_PREFIX = "/api/v1/appointments"
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _appointment_routes() -> tuple[APIRoute, ...]:
    return tuple(
        route
        for route in app.routes
        if isinstance(route, APIRoute) and route.path.startswith(APPOINTMENT_PREFIX)
    )


def _contract_paths() -> set[str]:
    paths: set[str] = set()
    for contract in DIARY_ACTION_ROUTE_CONTRACTS.values():
        paths.update(contract.read_routes)
        paths.update(contract.proposal_routes)
        paths.update(contract.confirm_routes)
        paths.update(contract.raw_mutation_routes)
    return paths


def _route_methods(route: APIRoute) -> set[str]:
    return set(route.methods or set()) - {"HEAD", "OPTIONS"}


def _mounted_methods_by_path(routes: tuple[APIRoute, ...]) -> dict[str, set[str]]:
    methods_by_path: dict[str, set[str]] = {}
    for route in routes:
        methods_by_path.setdefault(route.path, set()).update(_route_methods(route))
    return methods_by_path


def _contract_method_rows(routes: tuple[APIRoute, ...]) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    methods_by_path = _mounted_methods_by_path(routes)
    grammar_rows: set[tuple[str, str]] = set()
    raw_adjacent_rows: set[tuple[str, str]] = set()

    for contract in DIARY_ACTION_ROUTE_CONTRACTS.values():
        for path in contract.read_routes:
            for method in methods_by_path.get(path, set()):
                grammar_rows.add((method, path))
        for path in contract.proposal_routes + contract.confirm_routes:
            if "POST" in methods_by_path.get(path, set()):
                grammar_rows.add(("POST", path))
        for path in contract.raw_mutation_routes:
            for method in methods_by_path.get(path, set()) & WRITE_METHODS:
                raw_adjacent_rows.add((method, path))

    return grammar_rows, raw_adjacent_rows


def _method_family(methods: set[str]) -> str:
    if methods and methods <= {"GET"}:
        return "read_get"
    if methods and methods <= {"POST"}:
        return "query_or_command_post"
    if methods & {"PUT", "PATCH", "DELETE"}:
        return "mutation_method"
    return "other"


def _route_category(path: str) -> str:
    if path.startswith(f"{APPOINTMENT_PREFIX}/dev/"):
        return "dev"
    if "/bernie/sessions" in path or path.endswith("/bernie/pilot-eligibility"):
        return "bernie_session"
    if "/proposals/slot-search" in path or path.endswith("/slots/{practitioner_id}"):
        return "slot_search"
    if "/proposals/bernie/" in path:
        return "bernie_proposal_support"
    if path.endswith("/audit") or path.endswith("/types"):
        return "core_read"
    return "other_appointment"


def build_appointment_route_inventory_preflight() -> dict[str, Any]:
    routes = _appointment_routes()
    contract_paths = _contract_paths()
    grammar_authority_rows, raw_adjacent_rows = _contract_method_rows(routes)
    contract_rows = grammar_authority_rows | raw_adjacent_rows
    mounted_paths = {route.path for route in routes}
    route_rows = {
        (method, route.path)
        for route in routes
        for method in _route_methods(route)
    }
    covered_rows = route_rows & contract_rows
    uncovered_rows = route_rows - contract_rows

    uncovered_by_method_family = Counter(
        _method_family({method}) for method, _path in uncovered_rows
    )
    uncovered_by_category = Counter(_route_category(path) for _method, path in uncovered_rows)

    route_method_rows = len(route_rows)
    grammar_authority_paths = {path for _method, path in grammar_authority_rows}
    raw_adjacent_paths = {path for _method, path in raw_adjacent_rows}
    uncovered_paths = {path for _method, path in uncovered_rows}
    authority_counts = Counter(
        contract.authority.value for contract in DIARY_ACTION_ROUTE_CONTRACTS.values()
    )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": "static_fastapi_route_table",
        "appointment_prefix": APPOINTMENT_PREFIX,
        "route_table_scope": "mounted_appointment_apiroutes",
        "contract_scope": "diary_action_route_contract_paths",
        "appointment_route_count": len(routes),
        "appointment_distinct_path_count": len(mounted_paths),
        "appointment_route_method_count": route_method_rows,
        "contract_documented_path_count": len(contract_paths),
        "contract_authority_counts": dict(sorted(authority_counts.items())),
        "contract_covered_route_count": len({path for _method, path in covered_rows}),
        "contract_covered_route_method_count": len(covered_rows),
        "grammar_authority_route_count": len(grammar_authority_paths),
        "grammar_authority_route_method_count": len(grammar_authority_rows),
        "raw_adjacent_route_count": len(raw_adjacent_paths),
        "raw_adjacent_route_method_count": len(raw_adjacent_rows),
        "out_of_contract_route_count": len(uncovered_paths),
        "out_of_contract_route_method_count": len(uncovered_rows),
        "out_of_contract_distinct_path_count": len(uncovered_paths),
        "out_of_contract_by_method_family": dict(
            sorted(uncovered_by_method_family.items())
        ),
        "out_of_contract_by_category": dict(sorted(uncovered_by_category.items())),
        "all_contract_paths_mounted": contract_paths <= mounted_paths,
        "contract_is_complete_router_catalogue": False,
        "raw_adjacent_routes_are_grammar_dispatch_authority": False,
        "runtime_or_provider_wiring_ready": False,
        "provider_calls_performed": False,
        "http_requests_performed": False,
        "route_handlers_executed": False,
        "database_access_performed": False,
        "memory_or_rag_access_performed": False,
        "historical_diary_material_access_performed": False,
        "h15_or_h_series_runtime_imports_performed": False,
        "graphql_access_performed": False,
        "writes_performed": False,
    }


def assert_appointment_route_inventory_preflight_safety(report: dict[str, Any]) -> None:
    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["source"] == "static_fastapi_route_table"
    assert report["appointment_prefix"] == APPOINTMENT_PREFIX
    assert report["route_table_scope"] == "mounted_appointment_apiroutes"
    assert report["contract_scope"] == "diary_action_route_contract_paths"
    assert report["appointment_route_count"] > 0
    assert report["appointment_distinct_path_count"] > 0
    assert report["appointment_route_method_count"] >= report["appointment_route_count"]
    assert report["contract_documented_path_count"] > 0
    assert report["contract_authority_counts"][RouteAuthority.signed_confirm.value] > 0
    assert report["contract_covered_route_count"] > 0
    assert report["contract_covered_route_method_count"] > 0
    assert report["grammar_authority_route_count"] > 0
    assert report["grammar_authority_route_count"] <= report["contract_covered_route_count"]
    assert report["grammar_authority_route_method_count"] > 0
    assert report["raw_adjacent_route_count"] > 0
    assert report["raw_adjacent_route_method_count"] > 0
    assert report["out_of_contract_route_count"] > 0
    assert report["out_of_contract_route_count"] < report["appointment_route_count"]
    assert report["out_of_contract_distinct_path_count"] > 0
    assert report["out_of_contract_distinct_path_count"] < report["appointment_distinct_path_count"]
    assert report["out_of_contract_route_method_count"] > 0
    assert report["out_of_contract_by_method_family"]
    assert report["out_of_contract_by_category"]
    assert report["all_contract_paths_mounted"] is True
    assert report["contract_is_complete_router_catalogue"] is False
    assert report["raw_adjacent_routes_are_grammar_dispatch_authority"] is False
    assert report["runtime_or_provider_wiring_ready"] is False
    assert report["provider_calls_performed"] is False
    assert report["http_requests_performed"] is False
    assert report["route_handlers_executed"] is False
    assert report["database_access_performed"] is False
    assert report["memory_or_rag_access_performed"] is False
    assert report["historical_diary_material_access_performed"] is False
    assert report["h15_or_h_series_runtime_imports_performed"] is False
    assert report["graphql_access_performed"] is False
    assert report["writes_performed"] is False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate appointment route inventory preflight."
    )
    parser.parse_args()
    report = build_appointment_route_inventory_preflight()
    assert_appointment_route_inventory_preflight_safety(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
