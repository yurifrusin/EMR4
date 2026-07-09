import json
from pathlib import Path


REVIEW = Path("docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json")
DOC = Path("docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.md")


def _payload() -> dict:
    return json.loads(REVIEW.read_text(encoding="utf-8"))


def test_d5_first_slice_completion_review_marks_slice_complete_without_expansion():
    payload = _payload()

    assert payload["schema_version"] == "bernie.ui_dag.d5_first_slice_completion_review.v1"
    assert payload["decision"] == "d5_first_slice_complete_pause_expansion"
    assert payload["implemented_backend_commit"] == "098b92a7"
    assert payload["approval_contract_commit"] == "b0e255c8"
    assert payload["completed_scope"]["response_field"] == "staff_review.ui_view_model"
    assert payload["completed_scope"]["single_backend_response_assembly_point"] is True
    assert payload["completed_scope"]["existing_frontend_consumer_verified"] is True
    assert payload["completed_scope"]["frontend_javascript_expansion_performed"] is False
    assert payload["completed_scope"]["confirm_payload_unchanged"] is True
    assert payload["completed_scope"]["appointment_write_behavior_unchanged"] is True


def test_d5_first_slice_completion_review_preserves_api_spine_boundary():
    payload = _payload()
    spine = payload["api_spine_classification"]

    assert spine == {
        "surface": "read_display_response_contract",
        "graphql_mutation": False,
        "rest_command_mutation": False,
        "write_authority": False,
        "command_authority_source": "existing_signed_rest_confirm_command_only",
    }


def test_d5_first_slice_completion_review_keeps_all_expansion_gates_closed():
    payload = _payload()

    assert set(payload["closed_scope"]) == {
        "additional_backend_response_attachment_points",
        "additional_route_delivery",
        "graphql_delivery",
        "graphql_mutation",
        "provider_or_live_provider_wiring",
        "access_ai_invocation",
        "memory_rag_or_graphrag_wiring",
        "h15_or_h_series_runtime_inputs",
        "historical_diary_runtime_inputs",
        "external_patient_client_exposure",
        "confirm_payload_change",
        "appointment_write_behavior_change",
        "model_to_database_writes",
        "frontend_javascript_expansion",
    }
    assert all(value is False for value in payload["closed_scope"].values())
    assert "any_d5_scope_expansion" in payload["requires_separate_review"]
    assert payload["next_recommended_move"] == (
        "leave_d5_closed_and_select_a_separate_bounded_non_d5_sprint_or_human_review_checkpoint"
    )


def test_d5_first_slice_completion_markdown_states_pause_not_approval_to_expand():
    text = DOC.read_text(encoding="utf-8")
    folded = " ".join(text.split())

    assert "Decision: `d5_first_slice_complete_pause_expansion`" in text
    assert "`staff_review.ui_view_model`" in text
    assert "This is a read/display response contract" in folded
    assert "The only appointment write authority remains the existing signed REST confirm command" in folded
    assert "Do not continue expanding D5 by default" in folded
    assert "require separate review" in folded
