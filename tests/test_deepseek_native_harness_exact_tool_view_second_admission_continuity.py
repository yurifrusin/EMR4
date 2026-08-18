from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-"
    "development-admission"
)
PARENT = (
    "deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission"
)
SOURCE_HEAD = "00d4f8d6065ab09b5faf5501c979edd2fa59943c"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_exact_tool_view_second_admission_is_preserved_under_successor_repair() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 322
    assert compass["map_revision"] == 304
    assert compass["source_graph_revision"] == 322
    assert compass["current_position"]["node_id"] == (
        "ariadne-post-native-harness-successor-resolution-repair"
    )
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert [row["contract_id"] for row in node["contract_evidence"]] == [
        "combined-patient-practitioner-time-duration-intent",
        "committed-reschedule-availability-reconciliation",
    ]


def test_provider_free_exact_view_and_occupied_negative_result_are_preserved() -> None:
    proof = _load(
        "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-"
        "provider-free-composed-request-evidence.json"
    )
    occupied = _load(
        "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-"
        "second-monitored-development-occupied-negative-evidence.json"
    )
    assert proof["provider_free_phase_2_passed"] is True
    assert proof["accepted_isolated_capture"]["declared_tool_names"] == [
        "edit",
        "glob",
        "read",
    ]
    assert proof["accepted_isolated_capture"]["external_provider_calls"] == 0
    assert occupied["terminal"]["classification"] == "pre_session_harness_boot_failure"
    assert occupied["broker"]["provider_call_count"] == 0
    assert occupied["candidate"]["changed_path_count"] == 0
    assert occupied["cleanup"]["status"] == "complete"
    assert occupied["authority_disposition"]["retry_permitted"] is False


def test_compass_advances_to_read_only_admission_readiness() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "admission readiness" in current["strategic_role"]
    assert "without enabling it" in current["strategic_role"]
    assert "default-off and empty-allowlist posture" in current["outcome"]
    assert "no product or data change" in current["outcome"]
    assert "c82c3a741053a9c8da260aa62e1a968af22bb54e" in current["why_now"]
    assert "No provider" in " ".join(current["does_not_solve"])
    assert "Continuity 322 / Compass 304" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-development-admission-closeout.md",
        "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-second-monitored-development-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-exact-tool-view-second-monitored-development.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
