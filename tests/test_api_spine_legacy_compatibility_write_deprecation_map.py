import re
from pathlib import Path

from tests.test_api_spine_appointment_openapi_drift_guard import (
    EXPECTED_ROUTE_INVENTORY,
)


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = (
    ROOT / "docs" / "api-spine" / "legacy-compatibility-write-deprecation-map.md"
)
CONFIG_PATH = ROOT / "app" / "config.py"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"

EXPECTED_COMPATIBILITY_WRITES = [
    (
        "POST /api/v1/appointments",
        "create_appointment",
        "raw_compat_create",
        {
            "POST /api/v1/appointments/proposals/create",
        },
        {
            "POST /api/v1/appointments/proposals/create/confirm",
            "POST /api/v1/appointments/proposals/create/confirm-bernie",
        },
    ),
    (
        "PUT /api/v1/appointments/{appointment_id}",
        "update_appointment",
        "raw_compat_update",
        {
            "POST /api/v1/appointments/proposals/update/{appointment_id}",
            "POST /api/v1/appointments/proposals/bernie/tool-intent",
        },
        {
            "POST /api/v1/appointments/proposals/update/confirm",
        },
    ),
    (
        "PATCH /api/v1/appointments/{appointment_id}/status",
        "update_appointment_status",
        "raw_compat_status",
        {
            "POST /api/v1/appointments/proposals/status/{appointment_id}",
            "POST /api/v1/appointments/proposals/waiting-area/{appointment_id}",
        },
        {
            "POST /api/v1/appointments/proposals/status-confirm",
        },
    ),
    (
        "DELETE /api/v1/appointments/{appointment_id}",
        "cancel_appointment",
        "raw_compat_delete",
        {
            "POST /api/v1/appointments/proposals/delete/{appointment_id}",
        },
        {
            "POST /api/v1/appointments/proposals/delete-confirm",
        },
    ),
]

REQUIRED_PRECONDITIONS = {
    "the human Diary UI path emits the proposal route",
    "explicit staff confirmation",
    "freshness or signed evidence",
    "route-level idempotency posture",
    "default `audit`",
    "audit evidence remains attributable",
    "read-model witnesses",
    "system-level compatibility needs",
    "tests cover the replacement path",
}

REQUIRED_CLOSED_GATES = {
    "removing, renaming, blocking, or changing compatibility write routes",
    "raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement",
    "proposal-only route idempotency expansion",
    "GraphQL mutations",
    "provider prompt wiring or live provider calls",
    "provider dry-run wiring",
    "memory/RAG/GraphRAG runtime wiring",
    "H15/H-series runtime imports",
    "historical diary material access",
    "broad historical diary trove mining",
    "external patient clients",
    "runtime FGA clients",
    "direct database writes by model output",
    "model-to-database writes outside REST command handlers",
}


def _public_route(method: str, route: str) -> str:
    prefix = "/api/v1/appointments"
    return f"{method} {prefix}{route}" if route else f"{method} {prefix}"


def _document_rows() -> list[dict[str, str]]:
    text = MAP_PATH.read_text(encoding="utf-8")
    section = text.split("## Compatibility Write Map", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "compatibility_write": cells[0].strip("`"),
                "handler": cells[1].strip("`"),
                "raw_compat_tag": cells[2].strip("`"),
                "proposal_routes": set(re.findall(r"`([^`]+)`", cells[3])),
                "confirm_routes": set(re.findall(r"`([^`]+)`", cells[4])),
                "read_routes": set(re.findall(r"`([^`]+)`", cells[5])),
                "posture": cells[6].strip("`"),
            }
        )
    return rows


def _route_inventory_by_public_route() -> dict[str, str]:
    return {
        _public_route(method, route): classification
        for method, route, _, classification in EXPECTED_ROUTE_INVENTORY
    }


def test_deprecation_map_covers_exact_compatibility_write_routes():
    expected = {
        (_public_route(method, route), handler)
        for method, route, handler, classification in EXPECTED_ROUTE_INVENTORY
        if classification == "compatibility write"
    }
    actual = {(row["compatibility_write"], row["handler"]) for row in _document_rows()}

    assert actual == expected


def test_deprecation_map_replacements_are_current_non_raw_routes():
    route_inventory = _route_inventory_by_public_route()

    for row in _document_rows():
        assert row["posture"] == "compatibility_supported_native_client_parity_proven"

        for route in row["proposal_routes"]:
            assert route_inventory[route] in {"proposal command", "command-style read"}

        for route in row["confirm_routes"]:
            assert route_inventory[route] == "confirm command"

        for route in row["read_routes"]:
            assert route_inventory[route] == "read-only route"


def test_deprecation_map_matches_expected_replacement_families_and_raw_tags():
    rows = {
        (row["compatibility_write"], row["handler"]): row for row in _document_rows()
    }

    for (
        public_route,
        handler,
        raw_compat_tag,
        proposal_routes,
        confirm_routes,
    ) in EXPECTED_COMPATIBILITY_WRITES:
        row = rows[(public_route, handler)]
        assert row["raw_compat_tag"] == raw_compat_tag
        assert row["proposal_routes"] == proposal_routes
        assert row["confirm_routes"] == confirm_routes


def test_deprecation_map_records_existing_raw_compat_signal_modes():
    text = MAP_PATH.read_text(encoding="utf-8")
    config = CONFIG_PATH.read_text(encoding="utf-8")
    router = APPOINTMENTS_ROUTER.read_text(encoding="utf-8")

    assert 'appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"' in config
    assert "def _raw_compat_evidence_and_headers(" in router
    assert '{"Deprecation": \'true; version="0"\'}' in router

    for mode in ("`audit`", "`header`", "`off`"):
        assert mode in text
    for _, _, raw_compat_tag, _, _ in EXPECTED_COMPATIBILITY_WRITES:
        assert raw_compat_tag in text


def test_deprecation_map_requires_all_retirement_preconditions():
    text = MAP_PATH.read_text(encoding="utf-8")

    assert "The current decision is `native_client_parity_proven_keep_routes_mounted`." in text
    assert "zero raw appointment mutation call sites" in text
    for phrase in REQUIRED_PRECONDITIONS:
        assert phrase in text


def test_deprecation_map_preserves_closed_gate_boundary():
    text = MAP_PATH.read_text(encoding="utf-8")

    assert "This map does not authorize:" in text
    for gate in REQUIRED_CLOSED_GATES:
        assert gate in text


def test_deprecation_map_names_static_source_artifacts():
    text = MAP_PATH.read_text(encoding="utf-8")

    assert "tests/test_api_spine_appointment_openapi_drift_guard.py" in text
    assert "orchestration/api_spine_appointment_command_alignment_inventory.md" in text
    assert "docs/api-spine/appointment-read-model-route-inventory.md" in text
    assert "docs/api-spine/blueprint-first-model-second-boundary.md" in text
