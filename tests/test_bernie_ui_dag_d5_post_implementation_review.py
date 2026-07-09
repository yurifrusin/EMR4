import json
from pathlib import Path

from scripts.bernie_ui_dag_d5_readiness_snapshot import build_d5_readiness_snapshot


ROOT = Path(__file__).resolve().parents[1]
REVIEW_JSON = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-post-implementation-review.json"
REVIEW_MD = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-post-implementation-review.md"


def _review() -> dict:
    return json.loads(REVIEW_JSON.read_text(encoding="utf-8"))


def test_post_implementation_review_records_implemented_first_slice_only():
    review = _review()

    assert review["schema_version"] == "bernie.ui_dag.d5_post_implementation_review.v1"
    assert review["decision"] == "implemented_first_slice_reviewed_scope_blocked"
    assert review["implemented_commit"] == "098b92a7"
    assert review["approval_contract_commit"] == "b0e255c8"
    assert review["approval_decision"] == "approved_for_backend_response_delivery_first_slice"
    assert review["approval_expires_on"] == "2026-07-23"

    scope = review["implemented_scope"]
    assert scope["single_response_assembly_point"] is True
    assert scope["response_field"] == "staff_review.ui_view_model"
    assert scope["source_snapshot_required"] is True
    assert scope["no_server_session_field_null"] is True
    assert scope["confirm_payload_unchanged"] is True
    assert scope["appointment_write_behavior_unchanged"] is True
    assert scope["frontend_javascript_unchanged"] is True


def test_post_implementation_review_matches_safe_readiness_snapshot():
    review = _review()
    snapshot = build_d5_readiness_snapshot()

    for key, expected in review["readiness_snapshot_expected"].items():
        assert snapshot[key] == expected


def test_post_implementation_review_keeps_all_expansion_scope_closed():
    review = _review()

    closed_scope = review["closed_scope"]
    assert closed_scope
    assert all(value is False for value in closed_scope.values())
    assert closed_scope["additional_response_assembly_points"] is False
    assert closed_scope["graphql_delivery"] is False
    assert closed_scope["provider_or_live_provider_wiring"] is False
    assert closed_scope["memory_or_rag_wiring"] is False
    assert closed_scope["confirm_payload_change"] is False
    assert closed_scope["appointment_write_behavior_change"] is False
    assert closed_scope["external_patient_client_exposure"] is False
    assert closed_scope["model_to_database_write"] is False


def test_post_implementation_review_allows_only_evidence_work_without_new_approval():
    review = _review()

    assert review["allowed_next_without_new_approval"] == [
        "post_implementation_review_artifacts",
        "backend_response_shape_evidence_reports",
        "route_intercepted_frontend_consumption_evidence",
        "manual_frontend_verification_notes",
    ]
    assert "additional_backend_response_attachment_point" in review[
        "requires_separate_review"
    ]
    assert "provider_or_live_provider_wiring" in review["requires_separate_review"]
    assert "confirm_payload_or_write_behavior_change" in review[
        "requires_separate_review"
    ]


def test_post_implementation_review_markdown_says_scope_expansion_blocked():
    text = REVIEW_MD.read_text(encoding="utf-8")

    assert "Status: implemented first slice reviewed; scope expansion blocked." in text
    assert "`staff_review.ui_view_model`" in text
    assert "Confirm payloads" in text
    assert "runtime_or_provider_wiring_ready=false" in text
    assert "provider_calls_performed=false" in text
    assert "requires a separate review" in text
