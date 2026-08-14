from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/raisa-post-combined-editor-compass-baton-orientation.md"
DIARY = ROOT / "docs/diary/diary.js"
META_GRID = ROOT / "docs/diary/meta-grid.js"
OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_orientation_identifies_a_genuine_fork_and_recommends_readiness_first() -> None:
    report = _text(REPORT)
    normalized = " ".join(report.lower().split())
    head = "\n".join(report.splitlines()[:14])
    assert "Date: 2026-08-15" in head
    assert "Timestamp: 2026-08-15T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    for phrase in (
        "genuine Yuri-owned fork",
        "Reception One appointment cancellation",
        "provider-free read-only cancellation command-path readiness review",
        "Yuri attention required: **yes",
        "no honest, materially useful automatic successor",
    ):
        assert phrase.lower() in normalized


def test_repository_contains_the_exact_cancellation_gap() -> None:
    diary = _text(DIARY)
    meta_grid = _text(META_GRID)
    spec = _text(OPENAPI)

    bridge = diary.split("window.EMR4DiaryMetaGridBridge = Object.freeze({", 1)[1]
    bridge = bridge.split("});", 1)[0]
    assert "setAppointmentStatus: metaGridSetAppointmentStatus" in bridge
    assert "updateAppointmentDetails: metaGridUpdateAppointmentDetails" in bridge
    assert "delete" not in bridge.lower()
    assert 'if (["resize", "cancel"].includes(payload.goal) && selected)' in meta_grid
    assert 'posture: "proposal_only"' in meta_grid
    assert "operationalCommandAvailable: false" in meta_grid
    assert "async function deleteBooking()" in diary
    assert "Fallback to status proposal (omitting cancellation_reason)" in diary
    assert "normalizedConfirmPath.endsWith(\"/appointments/proposals/status-confirm\")" in diary
    assert "operationId: proposeAppointmentDelete" in spec
    assert "operationId: confirmAppointmentDeleteProposal" in spec


def test_candidate_matrix_preserves_every_recorded_gate() -> None:
    report = _text(REPORT)
    for phrase in (
        "Reception One check-in/waiting-area",
        "External patient channel, identity or delegated assistant",
        "Representative Stage 3B sessions",
        "Another typed Diary event family",
        "Operational durable-cue delivery or restart/unknown-commit work",
        "General visual polish",
        "`user_decision`",
        "`human_action`",
        "`authority_closed`",
        "`lower_leverage`",
    ):
        assert phrase in report


def test_delegation_revocation_does_not_rewrite_committed_truth() -> None:
    report = " ".join(_text(REPORT).lower().split())
    for phrase in (
        "separate, narrow and revocable delegation",
        "revoking it invalidates future use",
        "revocation is not retroactive database editing",
        "separately authorised cancellation or rescheduling command",
        "message address is neither the delegation nor proof of patient identity",
    ):
        assert phrase in report
