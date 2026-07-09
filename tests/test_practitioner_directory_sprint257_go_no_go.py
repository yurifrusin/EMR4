import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "api-spine" / "practitioner-directory-sprint257-go-no-go.json"
PACKET_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-sprint257-go-no-go.md"
SNAPSHOT = ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"


def _packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_sprint257_decision_is_no_go_and_does_not_flip_readiness():
    payload = _packet()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_sprint257_go_no_go.v1"
    assert payload["decision"] == "no_go_blocker_closure_required_before_readiness_approval_request"
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["target_readiness_flag"] == "rest_route_ready"
    assert payload["current_readiness_value"] is False
    assert payload["approved_value_after_this_packet"] is False
    assert payload["must_remain_false"]["rest_route_ready"] is False
    assert snapshot["rest_route_ready"] is False


def test_sprint257_worker_lanes_have_distinct_artifacts_and_recommendations():
    payload = _packet()

    assert payload["worker_lanes"]["claude"]["role"] == "independent_readiness_safety_veto"
    assert payload["worker_lanes"]["claude"]["recommendation"] == "no_go"
    assert payload["worker_lanes"]["antigravity"]["role"] == "consumer_api_boundary_review"
    assert payload["worker_lanes"]["antigravity"]["recommendation"] == "go_for_internal_consumer_contract"
    assert payload["worker_lanes"]["deepseek"]["role"] == "mechanical_static_sweep"
    assert payload["worker_lanes"]["deepseek"]["recommendation"] == "no_mechanical_blockers"


def test_sprint257_records_blockers_before_yuri_approval_request():
    payload = _packet()

    blockers = set(payload["blocking_items_before_requesting_yuri_readiness_approval"])
    assert blockers == {
        "record isolated runtime route test pass",
        "record API-spine artifact test pass",
        "record rate-limit or deferred-rate-limit decision",
        "name deployment surface",
        "record practitioner-directory-specific RLS or RLS-equivalent gap",
        "record practitioner-directory-specific field-encryption gap",
        "record explicit external-client scope decision",
        "create separate Yuri approval payload for rest_route_ready=true",
    }
    assert payload["criteria_status"]["rate_limit_or_deferred_rate_limit_decision_recorded"] == "missing"
    assert payload["criteria_status"]["deployment_surface_explicitly_named"] == "missing"
    assert payload["criteria_status"]["rls_or_rls_equivalent_gap_recorded"] == "missing"
    assert payload["criteria_status"]["field_encryption_gap_recorded"] == "missing"
    assert payload["criteria_status"]["separate_yuri_approval_payload_exists"] == "missing"


def test_sprint257_keeps_adjacent_gates_closed():
    payload = _packet()

    assert payload["consumer_contract_posture"] == {
        "internal_staff_consumer_contract": "passes_worker_review",
        "external_patient_client_ready": False,
        "public_exposure_ready": False,
    }
    assert all(value is False for value in payload["must_remain_false"].values())


def test_sprint257_markdown_names_useful_worker_disagreement():
    text = " ".join(PACKET_MD.read_text(encoding="utf-8").split())

    assert "The disagreement is useful" in text
    assert "Ariadne adopts the stricter conclusion" in text
    assert "does not approve, request, or implement a readiness-flag flip" in text
    assert "Sprint 258" in text
    assert "must not change without explicit approval" in text
