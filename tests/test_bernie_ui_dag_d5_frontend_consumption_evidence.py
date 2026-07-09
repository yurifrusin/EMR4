import json
from pathlib import Path


EVIDENCE = Path("docs/bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.json")
DOC = Path("docs/bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.md")
DIARY_JS = Path("docs/diary/diary.js")
SMOKE = Path("review/test_diary_smoke.py")


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_frontend_consumption_evidence_records_staff_review_shape():
    payload = _evidence()

    assert payload["schema_version"] == "bernie.ui_dag.d5_frontend_consumption_evidence.v1"
    assert payload["status"] == "route_intercepted_frontend_consumption_verified"
    assert payload["view_model_source_under_test"] == "staff_review.ui_view_model"
    assert payload["legacy_top_level_view_model_required"] is False
    assert payload["frontend_javascript_changed"] is False
    assert payload["production_backend_called"] is False
    assert payload["provider_called"] is False
    assert payload["appointment_write_performed"] is False


def test_frontend_consumption_evidence_points_to_real_consumer_and_smoke_case():
    payload = _evidence()
    diary_js = DIARY_JS.read_text(encoding="utf-8")
    smoke = SMOKE.read_text(encoding="utf-8")

    assert payload["existing_consumer_function"] == "attachBernieUiViewModelToStaffReview"
    assert payload["static_evidence"]["consumer_expression"] == "data?.staff_review?.ui_view_model"
    assert "data?.staff_review?.ui_view_model" in diary_js
    assert "function attachBernieUiViewModelToStaffReview" in diary_js
    assert payload["playwright_evidence"]["test"] in smoke
    assert 'assert "ui_view_model" not in response' in smoke
    assert 'response["staff_review"]["ui_view_model"] = _bernie_ui_view_model(' in smoke


def test_frontend_consumption_evidence_keeps_expansion_scope_closed():
    payload = _evidence()

    assert set(payload["closed_scope"]) == {
        "frontend_javascript_expansion",
        "additional_route_delivery",
        "graphql_delivery",
        "provider_or_live_provider_wiring",
        "access_ai_invocation",
        "memory_rag_or_graphrag_wiring",
        "h15_or_h_series_runtime_inputs",
        "historical_diary_runtime_inputs",
        "external_patient_client_exposure",
        "confirm_payload_change",
        "appointment_write_behavior_change",
        "model_to_database_writes",
    }
    assert all(value is False for value in payload["closed_scope"].values())
    assert payload["next_required_decision"] == "separate_review_for_any_scope_expansion"


def test_frontend_consumption_markdown_restates_route_intercepted_boundary():
    text = DOC.read_text(encoding="utf-8")
    folded = " ".join(text.split())

    assert "Status: route-intercepted frontend consumption verified" in folded
    assert "`staff_review.ui_view_model`" in text
    assert "route-intercepted Playwright evidence only" in folded
    assert "No production JavaScript changed" in folded
    assert "No backend route/schema/service behavior changed beyond" in folded
    assert "model-to-database write gate is opened" in folded
