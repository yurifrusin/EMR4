import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "api-spine" / "practitioner-directory-sprint258-blocker-closure.json"
PACKET_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-sprint258-blocker-closure.md"
SNAPSHOT = ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"


def _packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_sprint258_closes_blockers_without_readiness_flip():
    payload = _packet()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_sprint258_blocker_closure.v1"
    assert payload["decision"] == "readiness_blockers_closed_except_separate_yuri_approval"
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["readiness_value_after_this_packet"] is False
    assert snapshot["rest_route_ready"] is False
    assert payload["must_remain_false"]["rest_route_ready"] is False


def test_sprint258_records_required_test_pass_evidence():
    blockers = _packet()["closes_sprint257_blockers"]

    assert blockers["record_isolated_runtime_route_test_pass"] == {
        "status": "closed",
        "command": ".venv\\Scripts\\python.exe -m pytest tests\\test_practitioner_directory_route.py -q",
        "result": "31 passed",
        "execution_mode": "isolated_local_pytest",
    }
    assert blockers["record_api_spine_artifact_test_pass"] == {
        "status": "closed",
        "command": ".venv\\Scripts\\python.exe -m pytest tests\\test_api_spine_artifacts.py -q",
        "result": "31 passed",
        "execution_mode": "isolated_local_pytest",
    }


def test_sprint258_records_rate_limit_deployment_rls_encryption_and_external_scope():
    blockers = _packet()["closes_sprint257_blockers"]

    assert blockers["record_rate_limit_or_deferred_rate_limit_decision"]["status"] == (
        "closed_deferred_internal_route"
    )
    assert blockers["record_rate_limit_or_deferred_rate_limit_decision"][
        "required_before_external_or_public_exposure"
    ] is True
    assert "compromised or malicious authenticated staff credential" in blockers[
        "record_rate_limit_or_deferred_rate_limit_decision"
    ]["accepted_risk"]
    assert any(
        "Cloud Run request concurrency as a soft ceiling" in control
        for control in blockers["record_rate_limit_or_deferred_rate_limit_decision"][
            "current_controls"
        ]
    )
    assert blockers["name_deployment_surface"]["status"] == "closed"
    assert blockers["name_deployment_surface"]["deployment_ready_after_this_packet"] is False
    assert blockers["name_deployment_surface"]["production_ready_after_this_packet"] is False
    assert "Cloud Run" in blockers["name_deployment_surface"]["future_surface"]
    assert blockers["record_rls_or_rls_equivalent_gap"]["status"] == "closed_gap_recorded"
    assert blockers["record_rls_or_rls_equivalent_gap"]["production_follow_up_required"] is True
    assert blockers["record_rls_or_rls_equivalent_gap"]["not_equivalent_to_rls"] is True
    assert "raw SQL path" in blockers["record_rls_or_rls_equivalent_gap"]["residual_risk"]
    assert blockers["record_field_encryption_gap"]["status"] == "closed_gap_recorded"
    assert blockers["record_field_encryption_gap"]["production_follow_up_required"] is True
    assert set(blockers["record_field_encryption_gap"]["regulated_fields"]) == {
        "provider_number",
        "prescriber_number",
        "ahpra_number",
        "hpi_i",
    }
    assert "plaintext" in blockers["record_field_encryption_gap"]["residual_risk"]
    assert blockers["record_explicit_external_client_scope_decision"]["decision"] == "internal_staff_only"
    assert blockers["record_explicit_external_client_scope_decision"]["external_patient_client_ready"] is False
    assert "external-surface CORS and CSRF review" in blockers[
        "record_explicit_external_client_scope_decision"
    ]["future_external_exposure_requires"]


def test_sprint258_does_not_create_yuri_approval_payload():
    payload = _packet()
    blockers = payload["closes_sprint257_blockers"]

    assert blockers["create_separate_yuri_approval_payload_for_rest_route_ready_true"]["status"] == (
        "not_created_requires_explicit_yuri_approval"
    )
    assert payload["criteria_status_after_sprint258"]["separate_yuri_approval_payload_exists"] == (
        "missing_requires_explicit_yuri_approval"
    )
    assert payload["next_required_decision"] == (
        "Yuri must explicitly decide whether to authorize a separate rest_route_ready=true "
        "approval payload for this route only"
    )


def test_sprint258_markdown_restates_stop_before_approval_payload():
    text = " ".join(PACKET_MD.read_text(encoding="utf-8").split())

    assert "does not create a Yuri approval payload" in text
    assert "does not change `rest_route_ready`" in text
    assert "internal-staff-only" in text
    assert "Cloud Run concurrency is not per-user rate limiting" in text
    assert "not equivalent to PostgreSQL RLS" in text
    assert "API schema exclusion does not mitigate that storage risk" in text
    assert "The next decision is Yuri's" in text
    assert "No route, schema, read-service" in text
