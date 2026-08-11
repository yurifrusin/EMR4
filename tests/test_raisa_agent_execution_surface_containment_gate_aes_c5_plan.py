import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-plan.md"
THREAT = ROOT / "docs/security/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-threat-model-delta.md"
BASE = ROOT / "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5"
ENVELOPE = BASE / "product-runtime-envelope.json"
SCHEMA = BASE / "product-runtime-envelope.schema.json"
LEGACY_ROUTE_APPROVAL = ROOT / "docs/api-spine/practitioner-directory-rest-route-readiness-approval.json"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_plan_freezes_exact_source_purpose_and_final_named_descendant():
    text = PLAN.read_text(encoding="utf-8")
    assert "GET /api/v1/practice/practitioners" in text
    assert "supply active practitioner choices for Reception One booking" in text
    assert "AES-C5 completes the finite AES-C0 through AES-C5 sequence" in text
    assert "No AES-C6 or later" in text


def test_envelope_is_closed_and_schema_valid():
    schema = _json(SCHEMA)
    envelope = _json(ENVELOPE)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(envelope))
    assert not errors
    assert envelope["schema_version"] == "emr4.aes_c5.product_runtime_envelope.v1"
    assert envelope["status"] == "frozen_pending_exact_head_preexecution_gates"


def test_source_boundary_is_one_exact_authenticated_active_directory_read():
    envelope = _json(ENVELOPE)
    source = envelope["source_boundary"]
    assert source == {
        "source_class": "authored_synthetic_product_runtime",
        "evidence_mode": "live_local_backend_postgres",
        "method": "GET",
        "route": "/api/v1/practice/practitioners",
        "query": "activeOnly=true&limit=4&offset=0",
        "maximum_route_calls": 1,
        "maximum_route_retries": 0,
        "maximum_admitted_rows": 3,
        "overflow_detection_limit": 4,
        "watcher_or_subscription": False,
        "detail_route": False,
        "runtime_readiness_fixture_consumed": False,
        "global_readiness_changed": False,
    }


def test_principal_tenant_and_synthetic_data_are_fail_closed():
    envelope = _json(ENVELOPE)
    identity = envelope["principal_and_tenant_boundary"]
    data = envelope["data_and_retention_boundary"]
    assert identity["human_role"] == "Receptionist"
    assert identity["ordinary_bearer_auth_dependency_required"] is True
    assert identity["token_user_practice_equality_required"] is True
    assert identity["operational_database_or_practice"] is False
    assert identity["work_cell_receives_jwt_database_credential_or_lease"] is False
    assert data["classification"] == "authored_synthetic_product_runtime_derived_non_phi"
    assert data["real_person_or_operational_practice_data"] is False
    assert data["patient_or_health_information"] is False
    assert data["appointment_or_clinical_information"] is False
    assert data["platform_wide_zero_retention_claimed"] is False


def test_field_minimization_drops_ids_locations_and_authority():
    boundary = _json(ENVELOPE)["field_and_freshness_boundary"]
    assert boundary["route_response_fields"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation",
    ]
    assert boundary["work_cell_fields"] == [
        "practitioner_ref",
        "display_name",
        "role_label",
    ]
    assert boundary["broker_only_fields"] == [
        "id",
        "active",
        "defaultLocation",
        "alias_map",
    ]
    assert boundary["provider_prescriber_ahpra_hpii_contact_or_location_fields"] is False
    assert boundary["patient_appointment_or_clinical_fields"] is False
    assert boundary["command_authority"] is False


def test_freshness_target_and_release_are_exact():
    envelope = _json(ENVELOPE)
    fields = envelope["field_and_freshness_boundary"]
    release = envelope["proofreader_and_release_boundary"]
    assert fields["maximum_source_to_dispatch_age_seconds"] == 30
    assert fields["context_frame_ttl_seconds"] == 60
    assert fields["target_display_name"] == "Marlow Quill"
    assert fields["expected_target_alias"] == "practitioner-choice-002"
    assert release["release_fields"] == [
        "decision_code",
        "selected_practitioner_ref",
        "context_frame_set_digest",
        "command_authority",
    ]
    assert release["command_authority"] is False
    assert release["repair_call_permitted"] is False


def test_provider_cost_and_feature_boundary_is_one_call_no_retry():
    envelope = _json(ENVELOPE)
    provider = envelope["provider_binding"]
    request = envelope["request_contract"]
    cost = envelope["call_and_cost_boundary"]
    assert provider["model_id"] == "gemini-2.5-flash"
    assert provider["project"] == provider["quota_project"] == "bernie-emr4-dev"
    assert provider["location"] == "australia-southeast1"
    assert provider["endpoint_hostname"] == "australia-southeast1-aiplatform.googleapis.com"
    assert provider["published_retirement_on"] == "2026-10-20"
    assert request["thinking_budget_tokens"] == 1024
    for blocked in (
        "provider_tools",
        "function_calling",
        "grounding",
        "retrieval",
        "code_execution",
        "session_resumption",
        "explicit_context_cache",
        "automatic_fallback",
    ):
        assert request[blocked] is False
    assert cost["maximum_provider_calls"] == 1
    assert cost["maximum_provider_retries"] == 0
    assert cost["maximum_product_route_calls"] == 1
    assert cost["maximum_product_route_retries"] == 0
    assert cost["application_cost_ceiling_usd"] == 0.25


def test_two_capabilities_never_open_command_or_reusable_runtime():
    envelope = _json(ENVELOPE)
    broker = envelope["broker_and_isolation_boundary"]
    claim = envelope["claim_boundary"]
    assert broker["capability_classes"] == ["authoritative_read", "provider_inference"]
    assert broker["distinct_single_use_leases"] == 2
    assert broker["broker_operations"] == 2
    assert broker["product_mutations"] == 0
    assert broker["command_confirmations"] == 0
    assert broker["work_cell_selects_operation_identity"] is False
    assert claim["reusable_runtime_or_command_authorised"] is False
    assert claim["aes_c6_or_later_planned_or_authorised"] is False


def test_static_readiness_and_interpretation_gates_remain_closed():
    text = PLAN.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "runtime_or_provider_wiring_ready=false" in text
    assert "raw_trove_access_ready=false" in text
    assert "runtime_gate_decision=blocked" in text
    assert "route readiness approval has expired" in text
    assert "not import or consume the static route-readiness fixture" in lowered
    assert "global" in text and "readiness flags remain unchanged and false" in text


def test_legacy_general_route_approval_is_expired_not_extended():
    approval = _json(LEGACY_ROUTE_APPROVAL)
    envelope = _json(ENVELOPE)
    assert approval["approval_expires_on"] == "2026-08-08"
    assert envelope["authority_source"]["decided_on"] == "2026-08-11"
    assert envelope["source_boundary"]["runtime_readiness_fixture_consumed"] is False
    assert envelope["source_boundary"]["global_readiness_changed"] is False


def test_threat_delta_names_new_crossings_and_core_stops():
    text = THREAT.read_text(encoding="utf-8")
    for required in (
        "FastAPI route",
        "PostgreSQL schema",
        "Cross-practice or inactive row leak",
        "Sensitive route field reaches model",
        "Database write during measured read",
        "Provider retention exceeds claim",
        "Schema-valid but wrong practitioner selection",
        "command_authority: false",
    ):
        assert required in text
