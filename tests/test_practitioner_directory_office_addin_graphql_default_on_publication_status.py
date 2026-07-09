import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-default-on-publication-status.json"
STATUS_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-default-on-publication-status.md"
RUNTIME = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-default-on-runtime.json"
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
SPRINT_CLOSEOUT = ROOT / "orchestration" / "sprint_closeout.md"


def _status() -> dict:
    return json.loads(STATUS.read_text(encoding="utf-8"))


def _runtime() -> dict:
    return json.loads(RUNTIME.read_text(encoding="utf-8"))


def test_publication_status_records_pushed_commit_and_clean_refs():
    payload = _status()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_default_on_publication_status.v1"
    )
    assert payload["sprint"] == 282
    assert payload["published_runtime_commit"] == "d3dda16e657a4eb51b845a509c5cff071f530c43"
    assert payload["published_refs"] == {"master": True, "handoff_current": True}
    assert payload["integration_worktree_clean_after_publication"] is True


def test_publication_status_matches_runtime_scope_and_flag():
    payload = _status()
    runtime = _runtime()
    diary = DIARY_JS.read_text(encoding="utf-8", errors="replace")

    assert payload["target_consumer"] == runtime["target_consumer"]
    assert payload["target_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["runtime_posture"]["feature_gate_default"] is True
    assert runtime["runtime_posture"]["feature_gate_default"] is True
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" in diary
    assert payload["runtime_posture"]["rest_fallback_retained"] is True
    assert runtime["runtime_posture"]["rest_fallback_retained"] is True
    assert payload["runtime_posture"]["runtime_user_override"] is False
    assert payload["runtime_posture"]["server_config_endpoint"] is False


def test_publication_status_preserves_closed_gates_and_evidence_labels():
    payload = _status()

    assert payload["evidence_status"]["route_intercepted_browser_evidence_passed"] is True
    assert payload["evidence_status"]["deepseek_review_passed"] is True
    assert payload["evidence_status"]["antigravity_review"] == "timed_out"
    assert payload["evidence_status"]["claude_required"] is False
    assert all(value is False for value in payload["must_remain_false"].values())


def test_publication_markdown_and_closeout_no_longer_pending():
    text = " ".join(STATUS_MD.read_text(encoding="utf-8").split())
    closeout = " ".join(SPRINT_CLOSEOUT.read_text(encoding="utf-8", errors="replace").split())

    assert "Published runtime commit" in text
    assert "deployment readiness" in text
    assert "global GraphQL readiness" in text
    assert "field expansion" in text
    assert "| Batch | Sprint 281 Practitioner Directory Office Add-in GraphQL Default-On Runtime |" in closeout
    assert "| Status | Published to `origin/master` and `handoff/current`; worktree clean |" in closeout
