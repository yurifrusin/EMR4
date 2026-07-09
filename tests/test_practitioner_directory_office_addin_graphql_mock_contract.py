import ast
import json
from pathlib import Path

from tests.practitioner_directory_office_addin_graphql_mock_contract import (
    MockFetchResponse,
    consume_mock_practitioner_graphql_response,
)


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tests" / "practitioner_directory_office_addin_graphql_mock_contract.py"
DRIFT = ROOT / "tests" / "practitioner_directory_office_addin_graphql_mock_contract" / "DRIFT.md"
PLAN = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-fetch-wrapper-test-plan.json"
EVIDENCE = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-mock-contract-scaffold.json"
TASKPANE_JS = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"


def _success_body(rows):
    return {"data": {"practice": {"practitioners": rows}}}


def test_mock_contract_consumes_success_with_exact_projection_and_discards_extra_fields():
    raw = {
        "id": "practitioner-1",
        "displayName": "Dr Alice Example",
        "roleLabel": "GP",
        "active": True,
        "defaultLocation": {
            "id": "location-1",
            "name": "Main Clinic",
            "phone": "SHOULD_NOT_SURFACE",
        },
        "email": "SHOULD_NOT_SURFACE",
        "ahpraNumber": "SHOULD_NOT_SURFACE",
    }

    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(status_code=200, body=_success_body([raw]))
    )

    assert result.error_kind == "NONE"
    assert result.logout_requested is False
    assert result.graphql_fetch_attempted is True
    assert result.rows == [
        {
            "id": "practitioner-1",
            "displayName": "Dr Alice Example",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": {"id": "location-1", "name": "Main Clinic"},
        }
    ]
    assert "email" not in json.dumps(result.rows)
    assert "ahpra" not in json.dumps(result.rows).lower()
    assert "phone" not in json.dumps(result.rows).lower()


def test_mock_contract_consumes_empty_practitioner_list():
    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(status_code=200, body=_success_body([]))
    )

    assert result.rows == []
    assert result.error_kind == "NONE"
    assert result.logout_requested is False


def test_mock_contract_http_401_requests_logout():
    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(status_code=401, body={"detail": "Not authenticated"})
    )

    assert result.error_kind == "HTTP_401"
    assert result.logout_requested is True
    assert result.graphql_fetch_attempted is True


def test_mock_contract_graphql_forbidden_does_not_logout():
    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(
            status_code=200,
            body={"errors": [{"extensions": {"code": "FORBIDDEN"}}]},
        )
    )

    assert result.error_kind == "GRAPHQL_FORBIDDEN"
    assert result.logout_requested is False
    assert result.graphql_fetch_attempted is True


def test_mock_contract_graphql_bad_user_input_does_not_logout():
    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(
            status_code=200,
            body={"errors": [{"extensions": {"code": "BAD_USER_INPUT"}}]},
        )
    )

    assert result.error_kind == "GRAPHQL_BAD_USER_INPUT"
    assert result.logout_requested is False


def test_mock_contract_practice_null_is_empty_without_practice_field_leak():
    body = {
        "data": {"practice": None},
        "extensions": {
            "practice": {
                "id": "SHOULD_NOT_SURFACE",
                "name": "SHOULD_NOT_SURFACE",
            }
        },
    }

    result = consume_mock_practitioner_graphql_response(MockFetchResponse(status_code=200, body=body))

    assert result.rows == []
    assert result.error_kind == "NONE"
    assert "SHOULD_NOT_SURFACE" not in json.dumps(result.rows)


def test_mock_contract_default_location_null_keeps_row_without_rendering_copy():
    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(
            status_code=200,
            body=_success_body(
                [
                    {
                        "id": "practitioner-2",
                        "displayName": "Dr Bob Example",
                        "roleLabel": "GP",
                        "active": True,
                        "defaultLocation": None,
                    }
                ]
            ),
        )
    )

    assert len(result.rows) == 1
    assert result.rows[0]["defaultLocation"] is None
    assert "No location" not in json.dumps(result.rows)


def test_mock_contract_disabled_gate_skips_graphql_fetch_without_using_dates():
    result = consume_mock_practitioner_graphql_response(None, gate_disabled=True)

    assert result.error_kind == "GRAPHQL_DISABLED"
    assert result.graphql_fetch_attempted is False
    assert result.logout_requested is False


def test_mock_contract_future_rest_fallback_is_event_only():
    result = consume_mock_practitioner_graphql_response(
        MockFetchResponse(status_code=503, body={"detail": "unavailable"})
    )

    assert result.error_kind == "NETWORK_OR_SYSTEM"
    assert result.future_rest_fallback_requested is True
    assert result.rows == []


def test_mock_contract_helper_is_app_free_and_stdlib_only():
    tree = ast.parse(HELPER.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    assert sorted(imports) == ["__future__", "dataclasses", "typing"]
    assert all(not name.startswith("app") for name in imports)


def test_mock_contract_plan_records_discard_behavior():
    payload = json.loads(PLAN.read_text(encoding="utf-8"))

    assert payload["projection_drift_behavior"] == "discard"
    assert "projection_drift_extra_field_discarded" in payload["required_mock_cases"]
    assert "projection_drift_extra_field_rejected" not in payload["required_mock_cases"]


def test_mock_contract_evidence_keeps_runtime_gates_closed():
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_mock_contract_scaffold.v1"
    )
    assert payload["sprint"] == 276
    assert payload["decision"] == "tests_only_mock_contract_scaffold_added"
    assert payload["scaffold"]["runtime_taskpane_wrapper"] is False
    assert payload["scaffold"]["live_graphql_fetch"] is False
    assert payload["scaffold"]["app_imports"] is False
    assert payload["contract_behavior"]["projection_drift_behavior"] == "discard"
    assert payload["contract_behavior"]["future_rest_fallback"] == "event classification only, no orchestration"
    assert all(value is False for value in payload["must_remain_false"].values())
    assert payload["worker_reviews"]["antigravity_ux_contract"]["verdict"] == "PASS"
    assert payload["worker_reviews"]["deepseek_static_contract"]["verdict"] == "PASS"
    assert payload["worker_reviews"]["claude"]["used"] is False


def test_mock_contract_drift_doc_and_taskpane_runtime_boundary():
    drift = " ".join(DRIFT.read_text(encoding="utf-8").lower().split())
    taskpane = TASKPANE_JS.read_text(encoding="utf-8", errors="replace").lower()

    assert "not the office add-in runtime fetch wrapper" in drift
    assert "separate consumer switch approval" in drift
    assert "/api/v1/graphql" not in taskpane
    assert "query getpractitioners" not in taskpane
