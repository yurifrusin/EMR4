from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-post-cf-d2-compass-baton-orientation-plan.md"
REPORT = ROOT / "docs/raisa-post-cf-d2-compass-baton-orientation.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_orientation_selects_existing_status_family_without_new_authority() -> None:
    plan = " ".join(_text(PLAN).lower().split())
    report = " ".join(_text(REPORT).lower().split())
    assert "reception one selected-appointment status-action composition" in report
    assert "existing appointment-status proposal/confirm family" in report
    assert "no change to fastapi, graphql, openapi, postgresql" in report
    assert "a new appointment command family is ineligible" in plan
    assert "provider-free" in plan


def test_repository_evidence_exposes_exact_composition_gap() -> None:
    diary = _text(ROOT / "docs/diary/diary.js")
    meta_grid = _text(ROOT / "docs/diary/meta-grid.js")
    plan = _text(ROOT / "implementation_plan.md")
    assert "async function setAppointmentStatus(" in diary
    assert '"/appointments/proposals/status-confirm"' in diary
    bridge = diary.split("window.EMR4DiaryMetaGridBridge = Object.freeze({", 1)[1]
    bridge = bridge.split("});", 1)[0]
    assert "readAppointment: metaGridReadAppointment" in bridge
    assert "changeAppointmentStatus" not in bridge
    assert 'createElement("strong", "", item.status || "Scheduled")' in meta_grid
    assert "Reception One" in plan
    assert "Action proposals" in plan


def test_user_owned_or_runtime_candidates_remain_closed() -> None:
    report = _text(REPORT).lower()
    for phrase in (
        "yuri must reopen",
        "first external patient channel",
        "another diary event family",
        "operational cf-d2 watcher",
        "real identity",
        "deployment",
        "protected refs",
    ):
        assert phrase in report


def test_orientation_documents_have_brisbane_timestamps() -> None:
    for path in (PLAN, REPORT):
        head = "\n".join(_text(path).splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
