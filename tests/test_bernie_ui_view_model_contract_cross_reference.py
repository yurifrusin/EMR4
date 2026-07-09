import json
from pathlib import Path


CROSS_REFERENCE = Path("docs/bernie-ui-derived-state-view-model-contract-cross-reference.json")
DOC = Path("docs/bernie-ui-derived-state-view-model-contract-cross-reference.md")
INVENTORY = Path("docs/bernie-ui-derived-state-post-d5-next-slice-inventory.json")


def _payload() -> dict:
    return json.loads(CROSS_REFERENCE.read_text(encoding="utf-8"))


def test_view_model_cross_reference_is_docs_tests_only_checkpoint():
    payload = _payload()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "bernie.ui_dag.view_model_contract_cross_reference.v1"
    assert payload["sprint"] == 289
    assert payload["decision"] == "checkpoint_review_packet_docs_tests_only"
    assert payload["approval_source"].startswith("Yuri approved Sprint 288-289")
    assert payload["source_inventory"] == "docs/bernie-ui-derived-state-post-d5-next-slice-inventory.json"
    assert inventory["recommended_candidate_for_sprint_289"] == "view_model_contract_cross_reference"


def test_view_model_cross_reference_maps_required_artifacts():
    payload = _payload()
    by_artifact = {item["artifact"]: item for item in payload["artifact_map"]}

    assert set(by_artifact) == {
        "docs/bernie-ui-derived-state-dag-d3-inventory.md",
        "docs/bernie-ui-derived-state-dag-d4-preflight.md",
        "docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json",
        "docs/bernie-ui-derived-state-dag-evidence-consolidation.md",
        "orchestration/api_spine_adr.md",
    }
    assert by_artifact["docs/bernie-ui-derived-state-dag-d3-inventory.md"]["role"] == (
        "switch_point_inventory"
    )
    assert by_artifact["docs/bernie-ui-derived-state-dag-d4-preflight.md"]["role"] == (
        "route_intercepted_ui_preflight"
    )
    assert by_artifact["docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json"][
        "runtime_authority"
    ] == "display_only_response_contract"
    assert by_artifact["orchestration/api_spine_adr.md"]["runtime_authority"] == (
        "architecture_decision_only"
    )


def test_view_model_cross_reference_answers_reviewer_questions():
    payload = _payload()
    questions = " ".join(payload["reviewer_questions"]).lower()

    for fragment in (
        "display flag",
        "route-intercepted",
        "signed rest confirm commands",
        "separate approval",
    ):
        assert fragment in questions
    assert payload["allowed_followups_without_new_approval"] == [
        "human_review_notes",
        "documentation_cross_reference_cleanup",
        "fixture_label_consistency_checks",
        "safe_copy_matrix_documentation",
    ]


def test_view_model_cross_reference_keeps_all_runtime_gates_closed():
    payload = _payload()

    assert set(payload["requires_separate_approval"]) == {
        "runtime_code_change",
        "d5_scope_expansion",
        "additional_backend_response_attachment_point",
        "frontend_javascript_expansion",
        "graphql_delivery_or_readiness",
        "provider_or_live_provider_wiring",
        "access_ai_invocation",
        "memory_rag_or_graphrag_runtime_access",
        "h15_or_h_series_runtime_input",
        "historical_diary_runtime_input",
        "external_patient_client_exposure",
        "confirm_payload_or_write_behavior_change",
        "model_to_database_write",
        "deployment_or_production_readiness_claim",
    }
    assert all(value is True for value in payload["must_remain_closed"].values())
    assert payload["next_recommended_action"].startswith("Stop after Sprint 289 closeout")


def test_view_model_cross_reference_markdown_matches_boundary():
    payload = _payload()
    text = " ".join(DOC.read_text(encoding="utf-8").split())

    assert payload["cross_reference_goal"] in text
    assert "route-intercepted rather than live-provider evidence" in text
    assert "signed REST confirm commands" in text
    assert "GraphQL delivery/readiness" in text
    assert "model-to-database writes" in text
    assert "Stop after Sprint 289 closeout" in text
