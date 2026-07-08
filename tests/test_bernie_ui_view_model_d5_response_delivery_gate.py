import json
from pathlib import Path


GATE_PATH = Path("docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json")
DOC_PATH = Path("docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.md")


def _gate():
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def test_d5_response_delivery_gate_remains_blocked_by_default():
    gate = _gate()

    assert gate["schema_version"] == "bernie.ui_dag.d5_response_delivery_gate.v1"
    assert gate["decision"] == "blocked"
    assert gate["review_required_before_change"] is True
    assert gate["ui_consumer_first_slice_integrated"] is True
    assert gate["route_intercepted_ui_evidence_only"] is True

    approved_scope_fields = [
        key for key, value in gate.items()
        if (key.endswith("_approved") or key.endswith("_change_approved"))
        and isinstance(value, bool)
    ]
    assert approved_scope_fields
    for field in approved_scope_fields:
        assert gate[field] is False


def test_d5_gate_names_required_backend_delivery_prerequisites():
    gate = _gate()
    required = set(gate["required_before_backend_delivery"])

    assert "explicit_yuri_review" in required
    assert "bernie_interpretation_readiness_check_expected_blocked" in required
    assert "bernie_provider_boundary_readiness_report_expected_disabled" in required
    assert "response_schema_contract_for_bernie_ui_view_model" in required
    assert "server_snapshot_to_view_model_attachment_tests" in required
    assert "no_command_payload_field_leakage_tests" in required
    assert "route_import_and_provider_isolation_tests" in required
    assert "stale_pressed_awaiting_failed_state_contract_tests" in required
    assert "backward_compatibility_absent_when_no_session_snapshot_tests" in required
    assert "non_bernie_router_import_ban_tests" in required


def test_d5_gate_forbids_runtime_delivery_and_write_authority_until_approved():
    gate = _gate()
    forbidden = set(gate["forbidden_until_approved"])

    assert "production_route_emits_bernie_ui_view_model" in forbidden
    assert "graphql_resolver_emits_bernie_ui_view_model" in forbidden
    assert "provider_prompt_uses_bernie_ui_view_model" in forbidden
    assert "confirm_payload_contains_view_model_fields" in forbidden
    assert "database_write_depends_on_view_model_fields" in forbidden
    assert "historical_diary_material_runtime_input" in forbidden
    assert "external_patient_client_exposure" in forbidden
    assert "frontend_javascript_scope_expansion" in forbidden


def test_d5_gate_records_pre_delivery_readiness_commands_and_values():
    gate = _gate()

    assert ".venv\\Scripts\\python.exe scripts\\bernie_interpretation_readiness_check.py" in gate["pre_d5_readiness_commands"]
    assert ".venv\\Scripts\\python.exe scripts\\bernie_provider_boundary_readiness_report.py" in gate["pre_d5_readiness_commands"]
    assert "runtime_or_provider_wiring_ready=false" in gate["expected_pre_d5_values"]
    assert "raw_trove_access_ready=false" in gate["expected_pre_d5_values"]
    assert "runtime_gate_decision=blocked" in gate["expected_pre_d5_values"]
    assert "default_provider=disabled" in gate["expected_pre_d5_values"]
    assert "live_provider_enabled=false" in gate["expected_pre_d5_values"]
    assert "provider_calls_performed=false" in gate["expected_pre_d5_values"]


def test_d5_gate_doc_preserves_no_runtime_delivery_posture():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "Status: blocked" in text
    assert "route-intercepted consumer" in text
    assert "Production routes must not emit or import `BernieUiViewModel`" in text
    assert "scripts\\bernie_interpretation_readiness_check.py" in text
    assert "scripts\\bernie_provider_boundary_readiness_report.py" in text
    assert "does not approve production route emission" in text
