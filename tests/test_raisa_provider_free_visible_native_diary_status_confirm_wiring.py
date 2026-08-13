from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "docs/diary/diary.js"
CSS = ROOT / "docs/diary/diary.css"
HTML = ROOT / "docs/diary/diary.html"
PLAN = ROOT / "docs/raisa-provider-free-visible-native-diary-status-confirm-wiring-plan.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-visible-native-diary-status-confirm-wiring-threat-model-delta.md"
)
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
EVIDENCE_DIR = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-visible-native-diary-status-confirm-wiring"
)
EVIDENCE_SCHEMA = EVIDENCE_DIR / "visible-status-confirm-evidence.schema.json"
EVIDENCE = EVIDENCE_DIR / "visible-status-confirm-evidence.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_and_threat_delta_freeze_the_bounded_staff_only_slice() -> None:
    plan = _text(PLAN)
    threat = _text(THREAT)
    for document in (plan, threat):
        head = "\n".join(document.splitlines()[:12])
        assert "Date:** 2026-08-13" in head
        assert "Timestamp:** 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
    assert "routine safe change proceeds\nwithout an extra dialog" in plan
    assert "route_intercepted_browser" in plan
    assert "No wider Diary redesign" in plan
    assert "The server remains the sole owner" in threat
    assert "Event\ncues may later accelerate refresh" in threat


def test_visible_status_and_error_surfaces_are_accessible_live_regions() -> None:
    html = _text(HTML)
    assert (
        'id="diary-status" role="status" aria-live="polite" '
        'aria-atomic="true"'
    ) in html
    assert (
        'id="diary-error" class="hidden" role="alert" '
        'aria-live="assertive" aria-atomic="true"'
    ) in html


def test_status_selector_exposes_one_bounded_transaction_state_contract() -> None:
    source = _text(JS)
    for token in (
        'statusChanger.dataset.testid = "appointment-status-control"',
        'statusSelect.dataset.testid = "appointment-status-select"',
        'selectEl.setAttribute("aria-busy", "true")',
        '"Checking current Diary…"',
        '"Checking current Diary and saving…"',
        '"Appointment change cancelled. No change made."',
        '"Status change blocked. No change made."',
        '"Status not changed. Refresh the Diary before trying again."',
        'transactionState = "committed"',
    ):
        assert token in source
    assert 'currentSelect.focus({ preventScroll: true })' in source


def test_warning_terminal_dialog_names_transition_and_current_truth_boundary() -> None:
    source = _text(JS)
    css = _text(CSS)
    for token in (
        'overlay.setAttribute("aria-labelledby", `${dialogId}-title`)',
        'overlay.setAttribute("aria-describedby", `${dialogId}-body`)',
        'overlay.dataset.testid = "status-proposal-dialog"',
        'transition.dataset.testid = "status-confirm-transition"',
        'recheck.dataset.testid = "status-confirm-current-truth-boundary"',
        "The Diary will check current authority and current booking truth again",
        'if (event.key !== "Tab") return',
        'if (event.key === "Escape")',
    ):
        assert token in source
    assert ".status-confirm-transition" in css
    assert ".status-confirm-recheck" in css
    assert "@media (max-width: 480px)" in css


def test_existing_signed_confirm_and_no_raw_fallback_boundary_is_unchanged() -> None:
    source = _text(JS)
    assert '"/appointments/proposals/status-confirm"' in source
    assert "applySignedStatusProposal(appt, proposal, newStatus, waitingAreaId)" in source
    assert "fetch(`/api/v1/appointments/${appt.id}/status`" not in source
    assert 'const needsConfirm = (' in source
    assert '(isStatusChange && TERMINAL_STATUSES.includes(newStatus))' in source


def test_active_latch_resumes_this_exact_ui_operation() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    assert latch["operation_id"] == (
        "raisa-provider-free-visible-native-diary-status-confirm-wiring"
    )
    assert latch["status"] == "in_progress"
    assert latch["terminal_response"]["permitted"] is False
    assert "explicit_path_commit_and_push_the_verified_ui_source" in (
        latch["checkpoint"]["next_executable_stage"]
    )


def test_evidence_is_closed_typed_and_candid_about_browser_modes() -> None:
    schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(evidence),
        key=lambda error: list(error.path),
    )
    assert errors == []
    assert evidence["evidence_modes"] == [
        "authored_synthetic_client_fixture",
        "route_intercepted_browser",
        "repository_static_and_regression",
    ]
    assert set(evidence["zero_authority_counts"].values()) == {0}
    assert "without a live backend" in evidence["candid_limit"]
