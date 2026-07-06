from pathlib import Path
import re

import pytest

from tests.test_api_spine_appointment_openapi_drift_guard import (
    EXPECTED_ROUTE_INVENTORY,
)


ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"


def _openapi_doc():
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed.")
    return yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))


def test_openapi_records_current_backend_alignment_extension():
    doc = _openapi_doc()
    alignment = doc["x-emr4-current-backend-alignment"]

    assert alignment["sprint"] == 123
    assert alignment["status"] == "documentation_only_no_runtime_aliases"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", alignment["reviewed_on"])
    assert alignment["backend_prefix"] == "/api/v1"
    assert alignment["source_inventory"] == (
        "orchestration/api_spine_appointment_command_alignment_inventory.md"
    )
    assert alignment["guard_test"] == "tests/test_api_spine_appointment_openapi_drift_guard.py"


def test_openapi_records_canonical_path_drift_without_adding_runtime_aliases():
    alignment = _openapi_doc()["x-emr4-current-backend-alignment"]

    drift = {
        entry["current_backend_path"]: entry
        for entry in alignment["canonical_path_drift"]
    }
    assert set(drift) == {
        "/appointments/proposals/status-confirm",
        "/appointments/proposals/delete-confirm",
        "/appointments/proposals/slot-search/selection",
    }
    assert drift["/appointments/proposals/status-confirm"]["canonical_openapi_path"] == (
        "/appointments/proposals/status/confirm"
    )
    assert drift["/appointments/proposals/delete-confirm"]["canonical_openapi_path"] == (
        "/appointments/proposals/delete/confirm"
    )
    assert drift["/appointments/proposals/slot-search/selection"]["canonical_openapi_path"] == (
        "/appointments/proposals/slot-search/select"
    )
    assert all(
        entry["disposition"] == "documented_current_backend_alias_candidate"
        for entry in drift.values()
    )


def test_openapi_records_compatibility_writes_as_outside_proposal_confirm():
    alignment = _openapi_doc()["x-emr4-current-backend-alignment"]

    compatibility = {
        (entry["method"], entry["current_backend_path"]): entry
        for entry in alignment["compatibility_write_routes"]
    }
    assert set(compatibility) == {
        ("POST", "/appointments"),
        ("PUT", "/appointments/{appointment_id}"),
        ("PATCH", "/appointments/{appointment_id}/status"),
        ("DELETE", "/appointments/{appointment_id}"),
    }
    for entry in compatibility.values():
        assert entry["posture"] == "legacy_compatibility_write_outside_proposal_confirm_envelope"


def test_openapi_records_bernie_variants_without_provider_or_write_authority():
    alignment = _openapi_doc()["x-emr4-current-backend-alignment"]

    variants = {
        (entry["method"], entry["current_backend_path"]): entry
        for entry in alignment["bernie_backend_variants"]
    }
    assert set(variants) == {
        ("POST", "/appointments/proposals/bernie/tool-intent"),
        ("POST", "/appointments/proposals/bernie/interpret-booking-instruction"),
        ("POST", "/appointments/proposals/bernie/supervised-booking"),
        ("POST", "/appointments/proposals/create/confirm-bernie"),
        ("POST", "/appointments/proposals/bernie/no-slot-suggestion-selection"),
        ("GET", "/appointments/bernie/pilot-eligibility"),
        ("GET", "/appointments/bernie/sessions/active"),
        ("POST", "/appointments/bernie/sessions/new"),
        ("POST", "/appointments/bernie/sessions/{session_id}/events"),
    }
    assert variants[
        ("POST", "/appointments/proposals/bernie/interpret-booking-instruction")
    ]["posture"] == "command_style_read_default_disabled_provider_boundary"
    assert variants[
        ("POST", "/appointments/proposals/create/confirm-bernie")
    ]["posture"] == "create_confirm_family_variant"
    assert all("model_to_database" not in entry["posture"] for entry in variants.values())


def test_openapi_backend_alignment_keeps_blocked_gates_closed():
    alignment = _openapi_doc()["x-emr4-current-backend-alignment"]

    assert set(alignment["blocked_gates"]) == {
        "live_providers",
        "runtime_fga_clients",
        "external_patient_clients",
        "graphql_mutations",
        "broad_historical_diary_trove_mining",
        "h15_h_series_runtime_imports",
        "memory_rag_graphrag_runtime_wiring",
        "model_to_database_writes",
    }


def test_openapi_backend_alignment_handlers_match_router_inventory_guard():
    alignment = _openapi_doc()["x-emr4-current-backend-alignment"]
    expected = {
        (method, f"/appointments{route}" if route else "/appointments"): handler
        for method, route, handler, _classification in EXPECTED_ROUTE_INVENTORY
    }

    extension_entries = [
        *alignment["compatibility_write_routes"],
        *alignment["bernie_backend_variants"],
    ]
    for entry in extension_entries:
        key = (entry["method"], entry["current_backend_path"])
        assert key in expected
        assert entry["handler"] == expected[key]

    for entry in alignment["canonical_path_drift"]:
        key = ("POST", entry["current_backend_path"])
        assert key in expected
