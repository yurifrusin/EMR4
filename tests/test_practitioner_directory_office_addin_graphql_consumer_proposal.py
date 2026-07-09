import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-consumer-proposal.json"
PROPOSAL_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-consumer-proposal.md"
TASKPANE_JS = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"


def _payload() -> dict:
    return json.loads(PROPOSAL.read_text(encoding="utf-8"))


def test_office_addin_graphql_consumer_proposal_is_proposal_only():
    payload = _payload()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_consumer_proposal.v1"
    )
    assert payload["sprint"] == 274
    assert payload["decision"] == "proposal_only_no_runtime_switch"
    assert payload["target_consumer"] == "Office add-in taskpane practitioner selector"
    assert payload["target_field"] == "Query.practice.practitioners"
    assert payload["approval_expires_on"] == "2026-08-06"
    assert payload["scope"] == {
        "proposal_only": True,
        "comparison_design_only": True,
        "runtime_taskpane_switch": False,
        "taskpane_code_change": False,
        "backend_route_change": False,
        "schema_change": False,
        "readiness_flag_change": False,
        "deployment_or_production_exposure": False,
        "external_or_patient_client_exposure": False,
    }


def test_office_addin_graphql_consumer_projection_is_exact_ceiling():
    query = _payload()["authorized_query"]

    assert query["operation"] == "query"
    assert query["root"] == "practice"
    assert query["field"] == "practitioners"
    assert query["variables"] == {
        "activeOnly": "Boolean",
        "limit": "Int",
        "offset": "Int",
    }
    assert query["approved_projection"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation.id",
        "defaultLocation.name",
    ]
    assert query["field_expansion_allowed"] is False


def test_office_addin_graphql_consumer_error_model_separates_transport_and_graphql():
    model = _payload()["consumer_error_model"]

    assert model["http_401_transport"] == "same_logout_path_as_rest"
    assert model["graphql_forbidden_extensions_code"] == "consumer_layer_access_denied_no_logout"
    assert model["graphql_bad_user_input_extensions_code"] == "developer_argument_error_no_logout"
    assert model["practice_id_mismatch"] == "practice_null_without_data_leak"
    assert model["raw_graphql_error_copy_user_visible"] is False


def test_office_addin_graphql_comparison_methodology_avoids_runtime_and_readiness_claims():
    comparison = _payload()["comparison_methodology"]

    assert comparison["mode"] == "future_developer_or_staging_shadow_comparison_only"
    assert comparison["render_source_during_comparison"] == "REST"
    assert comparison["graphql_result_use_during_comparison"] == "contract_drift_detection_only"
    assert comparison["telemetry_in_sprint_274"] == "none"
    assert comparison["telemetry_before_switch"] == "local_browser_console_only_unless_separately_approved"
    assert comparison["data_content_values_in_committed_artifacts"] is False
    assert comparison["latency_or_throughput_claims"] is False
    assert comparison["readiness_claims"] is False


def test_office_addin_graphql_consumer_forbidden_runtime_posture_is_explicit():
    payload = _payload()

    assert all(value is True for value in payload["forbidden_in_sprint_274"].values())
    assert all(value is False for value in payload["must_remain_false"].values())
    assert "runtime_shadow_fetch" in payload["forbidden_in_sprint_274"]
    assert "client_logging_endpoint" in payload["forbidden_in_sprint_274"]
    assert "provider_access_ai_memory_rag_graphrag_h15_trove" in payload["forbidden_in_sprint_274"]


def test_office_addin_graphql_consumer_worker_reviews_are_distinct():
    reviews = _payload()["worker_reviews"]

    assert reviews["antigravity_consumer_ux"]["verdict"] == "PASS"
    assert "consumer_ux" in "antigravity_consumer_ux"
    assert reviews["deepseek_api_static"]["verdict"] == "PASS"
    assert reviews["claude"] == {
        "used": False,
        "reason": (
            "No API contract or resolver shape changed in Sprint 274; Claude remains stood down "
            "rather than duplicating Antigravity/DeepSeek review."
        ),
    }


def test_office_addin_graphql_consumer_markdown_names_boundaries():
    text = " ".join(PROPOSAL_MD.read_text(encoding="utf-8").split())

    assert "proposal-only" in text
    assert "does not change `taskpane.js`" in text
    assert "2026-08-06" in text
    assert "HTTP `401` remains the transport-layer auth failure" in text
    assert "GraphQL `extensions.code` errors are response-body errors" in text
    assert "REST remains the render source" in text
    assert "no live practitioner values" in text
    assert "local browser-console-only drift reporting" in text
    assert "separate approval" in text


def test_sprint_274_does_not_wire_taskpane_to_graphql_practitioner_query():
    source = TASKPANE_JS.read_text(encoding="utf-8", errors="replace")
    lowered = source.lower()

    assert "/api/v1/graphql" not in lowered
    assert "query getpractitioners" not in lowered
    assert "query.practice.practitioners" not in lowered
    assert "practitioners(activeonly" not in lowered
    assert "emr4_flag_graphql_practitioners" not in lowered
