"""Sprint 292 guards for the unapplied Bernie UI D5 next-step draft."""

import json
from pathlib import Path


PAYLOAD_PATH = Path("docs/bernie-ui-derived-state-d5-next-step-approval-payload-draft.json")
DOC_PATH = Path("docs/bernie-ui-derived-state-d5-next-step-approval-payload-draft.md")


def _payload() -> dict:
    return json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))


def test_d5_next_step_payload_is_explicitly_draft_only_and_unapplied():
    payload = _payload()

    assert payload["schema_version"] == "bernie.ui_dag.d5_next_step_approval_payload_draft.v1"
    assert payload["sprint"] == 292
    assert payload["status"] == "draft_only_not_applied"
    assert payload["decision"] == "no_new_d5_approval_applied"
    assert payload["reviewer"] == ""
    assert payload["reviewed_on"] == ""
    assert payload["go_no_go_acknowledged"] is False
    assert payload["current_posture"]["new_d5_runtime_authority"] == "not_granted"


def test_d5_next_step_payload_keeps_all_candidate_scope_fields_false():
    payload = _payload()

    assert all(value is False for value in payload["candidate_scope_if_route_intercepted_evidence_is_later_approved"].values())
    assert payload["candidate_scope_if_route_intercepted_evidence_is_later_approved"]["frontend_javascript_change"] is False
    assert payload["candidate_scope_if_route_intercepted_evidence_is_later_approved"]["confirm_payload_or_write_behavior_change"] is False
    assert payload["candidate_scope_if_route_intercepted_evidence_is_later_approved"]["model_to_database_write"] is False


def test_d5_next_step_payload_requires_explicit_future_decision_and_preserves_forbidden_scope():
    payload = _payload()
    options = {item["option"]: item for item in payload["options_for_future_explicit_decision"]}
    forbidden = set(payload["forbidden_even_if_route_intercepted_evidence_is_later_approved"])

    assert options["keep_d5_closed"]["recommended_now"] is True
    assert options["approve_route_intercepted_copy_conformity_evidence_only"]["requires_future_explicit_user_approval"] is True
    assert options["approve_any_d5_runtime_expansion"]["requires_separate_future_review_and_explicit_user_approval"] is True
    assert "frontend_javascript_change" in forbidden
    assert "backend_route_or_response_change" in forbidden
    assert "confirm_payload_contains_view_model_fields" in forbidden
    assert "database_write_depends_on_view_model_fields" in forbidden


def test_d5_next_step_payload_records_matching_green_advisory_shadow_run():
    payload = _payload()
    shadow = payload["ariadne_s3_shadow_classification"]

    assert shadow["mode"] == "advisory_only"
    assert shadow["boundary_class"] == "green"
    assert shadow["classification"] == "allowed"
    assert shadow["human_boundary_outcome"] == "green_draft_only"
    assert all(
        path == "AGENTS.md" or path.startswith(("docs/", "orchestration/", "tests/"))
        for path in shadow["observed_changed_paths"]
    )


def test_d5_next_step_payload_markdown_does_not_imply_approval():
    text = " ".join(DOC_PATH.read_text(encoding="utf-8").split()).lower()

    for fragment in (
        "status: draft only. no approval is applied",
        "keep d5 closed",
        "does not permit diary javascript",
        "all candidate scope fields remain false",
        "no_new_d5_approval_applied",
    ):
        assert fragment in text
