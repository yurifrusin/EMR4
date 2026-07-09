import json
from pathlib import Path


INVENTORY = Path("docs/bernie-ui-derived-state-post-d5-next-slice-inventory.json")
DOC = Path("docs/bernie-ui-derived-state-post-d5-next-slice-inventory.md")
REORIENTATION = Path("docs/sprint-287-next-block-reorientation.json")
D5_REVIEW = Path("docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json")


def _payload() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def test_post_d5_inventory_is_docs_tests_only_and_approved():
    payload = _payload()
    scope = payload["inventory_scope"]

    assert payload["schema_version"] == "bernie.ui_dag.post_d5_next_slice_inventory.v1"
    assert payload["sprint"] == 288
    assert payload["approval_source"].startswith("Yuri approved Sprint 288-289")
    assert payload["decision"] == "inventory_only_no_runtime_or_d5_expansion"
    assert scope == {
        "documentation_and_tests_only": True,
        "runtime_code_changed": False,
        "frontend_javascript_changed": False,
        "backend_route_changed": False,
        "provider_or_live_provider_wiring": False,
        "memory_rag_or_graphrag_wiring": False,
        "h15_h_series_or_historical_diary_runtime_input": False,
        "graphql_delivery_or_readiness": False,
        "appointment_write_behavior_changed": False,
    }


def test_post_d5_inventory_depends_on_sprint287_and_d5_completion():
    payload = _payload()
    reorientation = json.loads(REORIENTATION.read_text(encoding="utf-8"))
    d5 = json.loads(D5_REVIEW.read_text(encoding="utf-8"))

    assert payload["source_reorientation"] == "docs/sprint-287-next-block-reorientation.json"
    assert reorientation["recommended_next_block"]["sprints"][0]["sprint"] == 288
    assert payload["source_d5_completion_review"] == (
        "docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json"
    )
    assert d5["decision"] == "d5_first_slice_complete_pause_expansion"
    assert d5["completed_scope"]["frontend_javascript_expansion_performed"] is False


def test_post_d5_inventory_recommends_cross_reference_only():
    payload = _payload()
    candidates = {item["id"]: item for item in payload["candidate_non_d5_surfaces"]}

    assert set(candidates) == {
        "review_copy_safety_matrix",
        "view_model_contract_cross_reference",
        "ordinary_prompt_release_gate_mapping",
    }
    assert payload["recommended_candidate_for_sprint_289"] == "view_model_contract_cross_reference"
    recommended = candidates[payload["recommended_candidate_for_sprint_289"]]
    assert recommended["allowed_next_action"] == "docs_tests_cross_reference_only"
    assert recommended["requires_new_approval"] is False
    assert "without changing renderer behavior" in candidates["review_copy_safety_matrix"]["candidate_value"]
    assert "existing" in candidates["ordinary_prompt_release_gate_mapping"]["candidate_value"].lower()
    assert "evidence labels" in candidates["ordinary_prompt_release_gate_mapping"]["candidate_value"].lower()


def test_post_d5_inventory_rejects_runtime_expansion_candidates():
    payload = _payload()

    assert {item["id"] for item in payload["not_recommended_now"]} == {
        "additional_backend_response_attachment_point",
        "frontend_javascript_consumption_expansion",
        "graphql_or_provider_delivery",
    }
    assert all(value is True for value in payload["must_remain_closed"].values())
    assert payload["next_recommended_action"].startswith("Sprint 289 should produce")


def test_post_d5_inventory_markdown_matches_json_recommendation():
    payload = _payload()
    text = " ".join(DOC.read_text(encoding="utf-8").split())

    assert payload["recommended_candidate_for_sprint_289"] in text
    assert "documentation and tests only" in text
    assert "does not expand D5" in text
    assert "GraphQL delivery/readiness" in text
    assert "model-to-database writes remain closed" in text
