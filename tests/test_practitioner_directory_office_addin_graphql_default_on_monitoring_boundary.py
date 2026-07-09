import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-monitoring-boundary.json"
)
PACKET_MD = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-monitoring-boundary.md"
)
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
ROLLBACK = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-rollback-packet.json"
)


def _packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_monitoring_boundary_records_no_telemetry_or_readiness_claim():
    payload = _packet()
    diary = DIARY_JS.read_text(encoding="utf-8", errors="replace")

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_default_on_monitoring_boundary.v1"
    )
    assert payload["sprint"] == 285
    assert payload["decision"] == "monitoring_boundary_defined_no_telemetry_or_readiness_claim"
    assert payload["target_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["current_runtime_state"]["feature_gate_default"] is True
    assert payload["current_runtime_state"]["telemetry_endpoint"] is False
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" in diary


def test_monitoring_boundary_observes_only_existing_evidence_and_manual_channels():
    observed = _packet()["observable_without_new_instrumentation"]

    assert observed == {
        "committed_route_intercepted_browser_evidence": True,
        "committed_local_backend_smoke": True,
        "manual_user_report_channels": True,
        "existing_browser_console_warning_path": True,
        "new_backend_or_frontend_telemetry_added": False,
        "production_metrics_claimed": False,
    }


def test_monitoring_boundary_has_operator_checks_and_rollback_dependency():
    payload = _packet()
    rollback = json.loads(ROLLBACK.read_text(encoding="utf-8"))
    checklist = " ".join(payload["operator_checklist"]).lower()

    assert payload["source_rollback_packet"].endswith(
        "practitioner-directory-office-addin-graphql-default-on-rollback-packet.json"
    )
    assert rollback["sprint"] == 284
    for fragment in (
        "selector rows render",
        "selector-empty",
        "401",
        "fallback-to-rest",
        "cross-practice leakage",
        "rollback packet",
    ):
        assert fragment in checklist


def test_monitoring_boundary_keeps_readiness_blockers_and_must_not_claims():
    payload = _packet()

    assert payload["readiness_blockers"] == {
        "production_observability_evidence": True,
        "deployment_environment_validation": True,
        "external_client_policy": True,
        "global_graphql_readiness_review": True,
        "security_review_for_broader_graphql_surface": True,
        "telemetry_privacy_review_if_new_instrumentation_is_proposed": True,
    }
    assert payload["must_not_claim"] == {
        "deployment_ready": True,
        "production_ready": True,
        "telemetry_ready": True,
        "global_graphql_ready": True,
        "external_client_ready": True,
        "write_or_audit_write_ready": True,
        "provider_or_memory_ready": True,
    }
    assert payload["must_remain_false"] == {
        "deployment_ready": False,
        "production_ready": False,
        "global_graphql_readiness": False,
        "external_patient_client_ready": False,
        "write_authority_ready": False,
        "audit_write_ready": False,
        "provider_or_memory_ready": False,
        "h15_h_series_historical_diary_ready": False,
        "mutation_or_subscription_ready": False,
        "telemetry_endpoint_ready": False,
        "schema_field_expansion_ready": False,
    }
    assert payload["next_recommended_work"].startswith("Pause before deployment")


def test_monitoring_boundary_runtime_state_matches_source():
    payload = _packet()
    diary = DIARY_JS.read_text(encoding="utf-8", errors="replace")

    assert payload["current_runtime_state"]["single_consumer_only"] is True
    assert payload["current_runtime_state"]["rest_fallback_retained"] is True
    assert diary.count("ENABLE_GRAPHQL_PRACTITIONERS") >= 3
    assert "fetchPractitionerDirectoryRest" in diary
    assert "return fetchPractitionerDirectoryRest();" in diary


def test_monitoring_boundary_markdown_states_no_telemetry_or_global_readiness():
    text = " ".join(PACKET_MD.read_text(encoding="utf-8").split())

    assert "does not add telemetry" in text
    assert "does not claim deployment readiness" in text
    assert "production observability" in text
    assert "global GraphQL readiness" in text
    assert "field expansion" in text
