import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-agent-execution-surface-containment-gate-aes-c4-"
    "bounded-occupied-provider-proof-plan.md"
)
THREAT_MODEL = ROOT / "docs" / "security" / (
    "raisa-agent-execution-surface-containment-gate-aes-c4-"
    "bounded-occupied-provider-proof-threat-model-delta.md"
)
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-agent-execution-surface-containment-gate-aes-c4"
)
ENVELOPE = CONTINUITY / "provider-envelope.json"
SCHEMA = CONTINUITY / "provider-envelope.schema.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_aes_c4_envelope_is_closed_and_schema_valid():
    envelope = _load(ENVELOPE)
    schema = _load(SCHEMA)

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(envelope)
    assert schema["additionalProperties"] is False
    assert envelope["schema_version"] == "emr4.aes_c4.provider_envelope.v1"
    assert envelope["status"] == "frozen_pending_exact_head_preexecution_gates"


def test_aes_c4_exact_sydney_vertex_identity_and_path_are_frozen():
    envelope = _load(ENVELOPE)
    binding = envelope["provider_binding"]

    assert binding == {
        "provider": "google_vertex_ai",
        "model_id": "gemini-2.5-flash",
        "launch_stage": "GA",
        "published_retirement_on": "2026-10-20",
        "project": "bernie-emr4-dev",
        "quota_project": "bernie-emr4-dev",
        "service_account": (
            "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
        ),
        "authentication": "keyless_impersonated_service_account_adc",
        "oauth_scope": "https://www.googleapis.com/auth/cloud-platform",
        "required_permission": "aiplatform.endpoints.predict",
        "location": "australia-southeast1",
        "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
        "request_path": (
            "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
            "publishers/google/models/gemini-2.5-flash:generateContent"
        ),
        "allowed_identity_hosts": [
            "oauth2.googleapis.com",
            "iamcredentials.googleapis.com",
        ],
        "allowed_data_plane_hosts": [
            "australia-southeast1-aiplatform.googleapis.com"
        ],
    }


def test_standing_model_choice_does_not_become_call_or_scope_authority():
    selection = _load(ENVELOPE)["standing_model_selection"]

    assert selection["provider"] == "google_vertex_ai"
    assert selection["model_id"] == "gemini-2.5-flash"
    assert selection["effective_until_user_changes"] is True
    assert selection["routine_model_selection_pause_required"] is False
    assert selection["provider_call_authority"] is False
    assert selection["per_descendant_data_call_cost_and_effect_envelope_required"]
    assert selection["current_lifecycle_and_regional_support_recheck_required"]


def test_aes_c4_is_one_call_no_retry_and_cost_limited():
    envelope = _load(ENVELOPE)
    request = envelope["request_contract"]
    cost = envelope["call_and_cost_boundary"]

    assert request["candidate_count"] == 1
    assert request["temperature"] == 0
    assert request["thinking_budget_tokens"] == 1024
    assert request["maximum_output_tokens"] == 2048
    assert request["maximum_request_bytes"] == 8192
    assert request["maximum_provider_response_bytes"] == 16384
    assert request["provider_http_timeout_seconds"] == 45
    assert request["provider_tools"] is False
    assert request["function_calling"] is False
    assert request["grounding"] is False
    assert request["retrieval"] is False
    assert request["code_execution"] is False
    assert request["explicit_context_cache"] is False
    assert request["automatic_fallback"] is False

    assert cost["maximum_provider_calls"] == 1
    assert cost["maximum_retries"] == 0
    assert cost["call_after_any_provider_attempt"] is False
    assert cost["call_after_admission"] is False
    assert cost["application_cost_ceiling_usd"] == 0.25
    assert cost["reserved_cost_per_call_usd"] == 0.25
    assert cost["published_input_price_per_million_tokens_usd"] == 0.3
    assert (
        cost[
            "published_text_output_including_reasoning_price_per_million_tokens_usd"
        ]
        == 2.5
    )


def test_data_broker_and_command_boundaries_fail_closed():
    envelope = _load(ENVELOPE)
    data = envelope["data_boundary"]
    broker = envelope["broker_and_isolation_boundary"]
    release = envelope["proofreader_and_release_boundary"]
    claim = envelope["claim_boundary"]

    assert data["classification"] == "newly_authored_synthetic_only"
    for field, value in data.items():
        if field != "classification":
            assert value is False, field

    assert broker["capability_class"] == "provider_inference"
    assert broker["external_broker_owns_adc_and_short_lived_token"] is True
    assert broker["work_cell_receives_adc_or_token"] is False
    assert broker["generic_network"] is False
    assert broker["redirects"] == 0
    assert broker["distinct_data_plane_destinations"] == 1
    assert broker["provider_executed_tools"] is False
    assert broker["product_database_filesystem_command_or_runtime_adapter"] is False
    assert broker["generation_manifest_immutable"] is True
    assert broker["current_authority_recheck_before_dispatch"] is True
    assert broker["external_kill_switch"] is True
    assert broker["generation_wide_revocation"] is True

    assert release["release_fields"] == [
        "decision_code",
        "synthetic_nonce",
        "summary_code",
        "command_authority",
    ]
    assert release["command_authority"] is False
    assert release["repair_call_permitted"] is False
    assert release["invalid_or_unproved_output_state"] == "intelligence_unavailable"
    assert claim["product_data_or_runtime_safety_proved"] is False
    assert claim["reusable_provider_runtime_authorised"] is False
    assert (
        claim[
            "product_read_database_source_tool_command_write_deployment_"
            "production_release_or_protected_ref_authorised"
        ]
        is False
    )


def test_aer_0029_human_adc_commands_and_separate_store_rule_are_frozen():
    plan = PLAN.read_text(encoding="utf-8")
    checks = _load(ENVELOPE)["preexecution_checks"]

    assert "gcloud auth login --force" in plan
    assert (
        "gcloud auth application-default login "
        "--impersonate-service-account="
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com "
        "--project=bernie-emr4-dev "
        "--scopes=https://www.googleapis.com/auth/cloud-platform"
    ) in plan.replace("\n", " ")
    assert "--account=" not in plan
    assert checks["gcloud_cli_and_adc_stores_verified_separately"] is True
    assert checks["impersonated_adc_refresh_required"] is True
    assert checks["no_cloud_iam_or_configuration_mutation"] is True
    assert checks["provider_prompt_transmitted_during_preflight"] is False


def test_plan_and_threat_model_keep_api_spine_and_claims_narrow():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT_MODEL.read_text(encoding="utf-8")

    for text in (plan, threat):
        normalized = " ".join(text.split())
        assert "GraphQL remains read-only" in text
        assert "command_authority" in text
        assert "Australian physical or sovereign processing" in normalized
        assert "docs/branding/" in plan

    assert "exactly one" in plan
    assert "no retry" in plan.lower()
    assert "AES-C5 remains separately closed" in plan
    assert "AER-0029" in plan
