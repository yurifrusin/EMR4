import json
from pathlib import Path


GATE_PATH = Path("docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json")
DOC_PATH = Path("docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.md")
CHECKLIST_PATH = Path("docs/bernie-ui-derived-state-dag-d5-implementation-checklist.md")
ROUTER_IMPORT_PLAN_PATH = Path("docs/bernie-ui-derived-state-dag-d5-router-import-guard-plan.md")


def _gate():
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def test_d5_response_delivery_gate_json_has_no_duplicate_keys():
    duplicates = []

    def hook(pairs):
        seen = set()
        result = {}
        for key, value in pairs:
            if key in seen:
                duplicates.append(key)
            seen.add(key)
            result[key] = value
        return result

    json.loads(GATE_PATH.read_text(encoding="utf-8"), object_pairs_hook=hook)

    assert duplicates == []


def test_d5_response_delivery_gate_records_narrow_first_slice_approval():
    gate = _gate()

    assert gate["schema_version"] == "bernie.ui_dag.d5_response_delivery_gate.v1"
    assert gate["decision"] == "approved_for_backend_response_delivery_first_slice"
    assert gate["reviewer"] == "yuri"
    assert gate["review_required_before_change"] is True
    assert gate["approved_contract_commit"] == "b0e255c8"
    assert gate["approval_expires_on"] == "2026-07-23"
    assert gate["ui_consumer_first_slice_integrated"] is True
    assert gate["route_intercepted_ui_evidence_only"] is False
    assert gate["backend_response_delivery_approved"] is True
    assert gate["rest_or_fastapi_route_change_approved"] is True
    assert gate["graphql_delivery_approved"] is False
    assert gate["provider_or_live_provider_wiring_approved"] is False
    assert gate["memory_or_rag_wiring_approved"] is False
    assert gate["h15_or_h_series_runtime_input_approved"] is False
    assert gate["appointment_write_behavior_change_approved"] is False
    assert gate["model_to_database_write_approved"] is False


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


def test_d5_gate_forbids_non_first_slice_delivery_and_write_authority_after_approval():
    gate = _gate()
    forbidden = set(gate["forbidden_after_first_slice_approval"])

    assert "additional_production_routes_emit_bernie_ui_view_model" in forbidden
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


def test_d5_gate_doc_preserves_narrow_first_slice_posture():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "Status: approved for the narrow D5 backend response-delivery first slice" in text
    assert "route-intercepted consumer" in text
    assert "one reviewed Bernie response assembly point" in text
    assert "scripts\\bernie_interpretation_readiness_check.py" in text
    assert "scripts\\bernie_provider_boundary_readiness_report.py" in text
    assert "It does not approve" in text
    assert "GraphQL delivery" in text


def test_d5_implementation_checklist_stays_static_and_gate_bound():
    text = CHECKLIST_PATH.read_text(encoding="utf-8")

    assert "Status: first-slice checklist" in text
    assert "does not approve providers" in text
    assert "approved_for_backend_response_delivery_first_slice" in text
    assert "optional response field only" in text
    assert "one response assembly attachment point" in text
    assert "Response without a server session snapshot leaves the field null or absent" in text
    assert "Confirm payload serialization excludes" in text
    assert "Non-Bernie production routers do not import" in text
    assert "Stop and return to review" in text


def test_d5_router_import_guard_plan_preserves_fine_grained_ban():
    text = ROUTER_IMPORT_PLAN_PATH.read_text(encoding="utf-8")

    assert "Status: approved first slice" in text
    assert "production-router import ban" in text
    assert "approved first slice" in text
    assert "test_only_approved_bernie_route_imports_selector_after_d5_approval" in text
    assert "Do not delete the guard" in text
    assert "allows only the reviewed Bernie response-delivery attachment point" in text
    assert "app/routers/appointments.py" in text
    assert "keeps all non-Bernie production routers blocked" in text
    assert "requires a new approval" in text
