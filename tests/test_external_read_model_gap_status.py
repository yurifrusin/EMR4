"""Safe aggregate checker tests for external read-model gaps."""

import json

import pytest

from scripts.external_read_model_gap_status import (
    REQUIRED_CLOSED_GATE_PHRASES,
    assert_gap_inventory_static_and_blocked,
    build_gap_status,
    load_gap_inventory,
)


def test_gap_status_checker_accepts_current_inventory():
    text = load_gap_inventory()

    assert_gap_inventory_static_and_blocked(text)


def test_gap_status_is_safe_aggregate_only():
    status = build_gap_status()
    serialized = json.dumps(status, sort_keys=True).casefold()

    assert status == {
        "schema_version": "api_spine.external_read_model_gap_status.v1",
        "inventory_schema_version": "api_spine.external_read_model_gap_inventory.v1",
        "surface_count": 5,
        "coverage_kind_count": 2,
        "gap_posture_kind_count": 3,
        "model_only_gap_count": 3,
        "no_source_gap_count": 2,
        "missing_route_count": 5,
        "route_gap_count": 1,
        "route_and_shape_gap_count": 2,
        "source_and_licensing_gap_count": 2,
        "closed_gate_count": len(REQUIRED_CLOSED_GATE_PHRASES),
        "graphql_resolver_ready": False,
        "rest_route_ready": False,
        "provider_or_directory_runtime_ready": False,
        "runtime_or_memory_ready": False,
        "write_authority_ready": False,
        "raw_compat_mode_change_ready": False,
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }
    for fragment in [
        "query.",
        "/api/",
        "patient_id",
        "practitioner",
        "reminder",
        "message",
        "racgp",
        "cochrane",
        "local_data",
        "provider calls",
    ]:
        assert fragment not in serialized


def test_gap_status_checker_rejects_added_surface():
    text = load_gap_inventory().replace(
        "| `Query.directorySearch.COCHRANE_LIBRARY` |",
        "| `Query.directorySearch.EXTRA_SOURCE` |",
    )

    with pytest.raises(AssertionError):
        assert_gap_inventory_static_and_blocked(text)


def test_gap_status_checker_rejects_route_source_claim():
    text = load_gap_inventory().replace(
        "| `Query.practice.practitioners` | `app/models/tenancy.py::Practitioner` | `none` |",
        "| `Query.practice.practitioners` | `app/models/tenancy.py::Practitioner` | `GET /api/v1/practice/practitioners` |",
    )

    with pytest.raises(AssertionError):
        assert_gap_inventory_static_and_blocked(text)


def test_gap_status_checker_rejects_coverage_drift():
    text = load_gap_inventory().replace(
        "| `Query.patient.reminders` | `app/models/results.py::Reminder` | `none` | `model_only` |",
        "| `Query.patient.reminders` | `app/models/results.py::Reminder` | `none` | `full` |",
    )

    with pytest.raises(AssertionError):
        assert_gap_inventory_static_and_blocked(text)


def test_gap_status_checker_rejects_gap_posture_drift():
    text = load_gap_inventory().replace(
        "| `Query.patient.messages` | `app/models/messaging.py::InternalMessage`; `app/models/messaging.py::SmsLog` | `none` | `model_only` | `GET /api/v1/patients/{patient_id}/messages` or equivalent patient-scoped read route | `route_and_shape_gap` |",
        "| `Query.patient.messages` | `app/models/messaging.py::InternalMessage`; `app/models/messaging.py::SmsLog` | `none` | `model_only` | `GET /api/v1/patients/{patient_id}/messages` or equivalent patient-scoped read route | `route_gap` |",
    )

    with pytest.raises(AssertionError):
        assert_gap_inventory_static_and_blocked(text)


def test_gap_status_checker_rejects_removed_closed_gate():
    text = load_gap_inventory().replace(
        "- memory/RAG/GraphRAG runtime wiring;\n",
        "",
    )

    with pytest.raises(AssertionError):
        assert_gap_inventory_static_and_blocked(text)
