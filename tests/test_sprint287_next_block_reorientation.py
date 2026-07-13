import json
from pathlib import Path


PACKET = Path("docs/sprint-287-next-block-reorientation.json")
DOC = Path("docs/sprint-287-next-block-reorientation.md")
D5_REVIEW = Path("docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json")
AGENTS = Path("AGENTS.md")


def _payload() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_sprint287_pauses_graphql_readiness_track():
    payload = _payload()
    graphql = payload["current_graphql_track_state"]

    assert payload["schema_version"] == "emr4.sprint_287_next_block_reorientation.v1"
    assert payload["decision"] == "pause_graphql_readiness_and_select_non_runtime_checkpoint_block"
    assert payload["preceded_by"] == {
        "sprint": 286,
        "commit": "7e2dd6e71a5ff6d5d1aadc9fa6f137e1beedb833",
        "title": "correct publication state",
    }
    assert graphql["office_addin_graphql_default_on"] is True
    assert graphql["single_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert graphql["monitoring_boundary_complete"] is True
    assert graphql["rollback_packet_complete"] is True
    assert graphql["deployment_readiness_claim_allowed"] is False
    assert graphql["production_readiness_claim_allowed"] is False
    assert graphql["telemetry_expansion_allowed"] is False
    assert graphql["global_graphql_readiness_allowed"] is False


def test_sprint287_uses_d5_completion_without_expanding_d5():
    payload = _payload()
    d5 = payload["bernie_d5_state"]
    source = json.loads(D5_REVIEW.read_text(encoding="utf-8"))

    assert d5 == {
        "first_slice_complete": True,
        "d5_expansion_allowed_without_review": False,
        "source": "docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json",
    }
    assert source["decision"] == "d5_first_slice_complete_pause_expansion"
    assert source["next_recommended_move"] == (
        "leave_d5_closed_and_select_a_separate_bounded_non_d5_sprint_or_human_review_checkpoint"
    )


def test_sprint287_recommends_only_documentation_and_tests_block():
    payload = _payload()
    block = payload["recommended_next_block"]

    assert block["name"] == "Bernie UI derived-state non-D5 checkpoint block"
    assert [item["sprint"] for item in block["sprints"]] == [288, 289]
    assert all(item["allowed_scope"] == "documentation_and_tests_only" for item in block["sprints"])
    assert "without expanding D5" in block["why_this_block"]
    assert "unapproved readiness/deployment" in block["why_this_block"]


def test_sprint287_keeps_runtime_and_expansion_gates_closed():
    payload = _payload()

    assert payload["must_remain_closed"] == {
        "graphql_deployment_or_production_readiness": True,
        "graphql_telemetry_expansion": True,
        "global_graphql_readiness": True,
        "d5_scope_expansion": True,
        "provider_or_live_provider_wiring": True,
        "access_ai_invocation": True,
        "memory_rag_or_graphrag_runtime_access": True,
        "h15_or_h_series_runtime_input": True,
        "historical_diary_runtime_input": True,
        "external_patient_client_exposure": True,
        "confirm_payload_or_write_behavior_change": True,
        "model_to_database_write": True,
    }
    stop_text = " ".join(payload["stop_conditions"]).lower()
    for fragment in (
        "deployment or production readiness",
        "telemetry",
        "graphql beyond the approved office add-in practitioner selector",
        "expand d5",
        "provider",
        "memory/rag/graphrag",
        "h15/h-series",
        "historical diary runtime input",
        "external client exposure",
        "write authority",
    ):
        assert fragment in stop_text
    assert payload["next_recommended_action"].startswith("Run Sprint 288 only if Yuri agrees")


def test_sprint287_markdown_is_preserved_while_handover_advances():
    text = " ".join(DOC.read_text(encoding="utf-8").split())
    agents = AGENTS.read_text(encoding="utf-8", errors="replace")

    assert "pause the practitioner-directory GraphQL default-on track" in text
    assert "Sprint 288: post-D5 next-slice inventory" in text
    assert "documentation/tests-only" in text
    assert "Stop before any work that adds telemetry" in text
    assert "T1 Stateful Diary Scenario Laboratory is underway" in agents
    assert "Continue without pause to T1.2" in agents
    assert "docs/bernie-consultant-triage-implementation-roadmap.md" in agents


def test_sprint287_json_and_markdown_stay_aligned():
    payload = _payload()
    text = " ".join(DOC.read_text(encoding="utf-8").split())

    assert payload["preceded_by"]["commit"] in text
    assert "pause the practitioner-directory GraphQL default-on track" in text
    assert payload["recommended_next_block"]["name"] in text
    assert "Sprint 288: post-D5 next-slice inventory" in text
    assert "Sprint 289: checkpoint review packet" in text
