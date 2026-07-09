import json
from pathlib import Path


PACKET = Path("docs/bernie-ui-derived-state-d5-reopening-decision-packet.json")
DOC = Path("docs/bernie-ui-derived-state-d5-reopening-decision-packet.md")
CROSS_REFERENCE = Path("docs/bernie-ui-derived-state-view-model-contract-cross-reference.json")
D5_REVIEW = Path("docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json")


def _payload() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_d5_reopening_decision_keeps_runtime_closed():
    payload = _payload()

    assert payload["schema_version"] == "bernie.ui_dag.d5_reopening_decision_packet.v1"
    assert payload["sprint"] == 290
    assert payload["decision"] == "do_not_reopen_d5_runtime_yet"
    assert payload["recommended_next_block"]["runtime_reopening_allowed"] is False
    assert all(value is True for value in payload["must_remain_closed"].values())


def test_d5_reopening_decision_depends_on_completed_checkpoint_artifacts():
    payload = _payload()
    cross_ref = json.loads(CROSS_REFERENCE.read_text(encoding="utf-8"))
    d5 = json.loads(D5_REVIEW.read_text(encoding="utf-8"))

    assert payload["source_cross_reference"] == (
        "docs/bernie-ui-derived-state-view-model-contract-cross-reference.json"
    )
    assert cross_ref["decision"] == "checkpoint_review_packet_docs_tests_only"
    assert cross_ref["next_recommended_action"].startswith("Stop after Sprint 289")
    assert d5["decision"] == "d5_first_slice_complete_pause_expansion"
    assert d5["completed_scope"]["frontend_javascript_expansion_performed"] is False


def test_d5_reopening_options_are_explicitly_decided():
    payload = _payload()
    options = {item["option"]: item for item in payload["options_reviewed"]}

    assert options["keep_d5_closed"]["decision"] == "recommended_now"
    assert options["approve_route_intercepted_frontend_evidence_slice"]["decision"] == (
        "defer_until_safe_copy_matrix_exists"
    )
    assert options["approve_tiny_runtime_expansion"]["decision"] == "not_recommended"


def test_d5_reopening_next_block_is_docs_and_draft_only():
    payload = _payload()
    sprints = payload["recommended_next_block"]["sprints"]

    assert [item["sprint"] for item in sprints] == [291, 292]
    assert sprints[0] == {
        "sprint": 291,
        "title": "Bernie UI derived-state safe-copy matrix",
        "scope": "docs_tests_only",
    }
    assert sprints[1] == {
        "sprint": 292,
        "title": "D5 next-step approval payload draft",
        "scope": "draft_only_no_approval_application",
    }
    assert payload["next_recommended_action"].endswith(
        "Do not apply approval or reopen D5 runtime in this block."
    )


def test_d5_reopening_records_deepseek_worker_retirement():
    payload = _payload()

    assert payload["worker_plan"] == {
        "claude": "strategic_gate_review",
        "antigravity": "product_workflow_review",
        "deepseek": "retired_not_used",
    }
    assert payload["worker_cleanup"] == {
        "deepseek_worker_agent_config": "deleted_local_unused_agent_definition",
        "deleted_path": "C:/Users/sarashera/.codex/agents/deepseek-worker.toml",
        "historical_review_artifacts_preserved": True,
        "replacement_static_review": "ariadne_local_guard_tests",
    }


def test_d5_reopening_markdown_matches_closed_gate_posture():
    text = " ".join(DOC.read_text(encoding="utf-8").split())

    assert "Decision: do not reopen D5 runtime yet" in text
    assert "Keep D5 closed" in text
    assert "draft-only approval payload" in text
    assert "DeepSeek is retired for this packet" in text
    assert "old local unused `deepseek-worker` agent definition was deleted" in text
    assert "Do not apply an approval or reopen D5 runtime" in text
    assert "GraphQL delivery/readiness" in text
    assert "production readiness claims remain closed" in text
