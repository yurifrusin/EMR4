from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-reception-one-selected-appointment-status-action-composition-plan.md"
THREAT = (
    ROOT
    / "docs/security/raisa-reception-one-selected-appointment-status-action-composition-threat-model-delta.md"
)
DIARY_JS = ROOT / "docs/diary/diary.js"
META_GRID_JS = ROOT / "docs/diary/meta-grid.js"
META_GRID_CSS = ROOT / "docs/diary/meta-grid.css"
DIARY_HTML = ROOT / "docs/diary/diary.html"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_and_threat_delta_freeze_the_narrow_existing_command_composition() -> None:
    plan = _text(PLAN)
    threat = _text(THREAT)
    for document in (plan, threat):
        head = "\n".join(document.splitlines()[:12])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head

    for token in (
        "existing `setAppointmentStatus`",
        "one current\n   non-synthetic-placeholder appointment",
        "no `fetch`, proposal, confirm",
        "discard stale Back history",
        "route_intercepted_browser",
        "authored_synthetic_client_fixture",
        "No FastAPI, GraphQL, OpenAPI, database/migration/RLS",
    ):
        assert token in plan

    for token in (
        "does not\nadd write authority",
        "calls `setAppointmentStatus`",
        "Suppress the workspace-level Escape close",
        "GraphQL remains read-only",
        "Events\nremain optional acceleration hints",
    ):
        assert token in threat


def test_exact_accepted_source_remains_in_current_lineage() -> None:
    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            "b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33",
            "HEAD",
        ],
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0


def test_shared_status_vocabulary_and_bridge_delegate_to_the_existing_interaction() -> None:
    diary = _text(DIARY_JS)
    assert "const APPOINTMENT_STATUS_OPTIONS = Object.freeze([" in diary
    for value in ("Booked", "Arrived", "InConsult", "Completed", "Cancelled", "NoShow", "DNA"):
        assert f'Object.freeze({{ value: "{value}"' in diary
    assert 'if (currentStatus === "Confirmed")' in diary
    assert "const selectOptions = appointmentStatusOptions(a.status);" in diary
    assert "const options = appointmentStatusOptions(currentStatus);" in diary

    bridge_start = diary.index("async function metaGridSetAppointmentStatus")
    bridge_end = diary.index("function setMetaGridLaunchAvailability", bridge_start)
    bridge = diary[bridge_start:bridge_end]
    assert "setAppointmentStatus(" in bridge
    assert "metaGridReadAppointment(appointmentId)" in bridge
    for forbidden in ("fetch(", "apiFetch(", "/appointments/proposals/", "status-confirm"):
        assert forbidden not in bridge


def test_reception_one_action_is_modeless_fail_closed_and_freshly_reconciled() -> None:
    source = _text(META_GRID_JS)
    css = _text(META_GRID_CSS)
    html = _text(DIARY_HTML)
    for token in (
        'panel.dataset.testid = "meta-grid-status-action"',
        'select.dataset.testid = "meta-grid-status-select"',
        'submit.dataset.testid = "meta-grid-status-submit"',
        'feedback.setAttribute("aria-live", "polite")',
        "state.statusAction.busy",
        "preserveSelectedAppointmentId: appointmentId",
        "clearTrail: true",
        'document.querySelector(\'[data-testid="status-proposal-dialog"]\')',
        "The appointment is no longer in this current projection.",
    ):
        assert token in source
    assert "bridge.setAppointmentStatus(" in source
    assert "fetch(" not in source
    assert "apiFetch(" not in source
    assert ".meta-grid-status-action" in css
    assert "@media (max-width: 700px)" in css
    assert 'meta-grid.css?v=13' in html
    assert 'meta-grid.js?v=18' in html
