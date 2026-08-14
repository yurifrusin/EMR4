"""Provider-free route-intercepted browser contract for the Reception One
combined appointment-update editor (same-update-family multi-change
composition).

Specifies: time, duration and practitioner are three views of one provisional
appointment-update draft; same-family switching preserves every valid pending
value with zero routes; a visible provisional shared-draft summary names only
the changed dimensions; collapse and status crossover discard the whole update
draft; one visible update Review control emits exactly one existing update
proposal containing all three effective values and always stops at the existing
confirmation dialog (even in ``safe`` fixture mode); only the visible
``Confirm & Save`` control emits one confirm and a fresh reconciled truth
summary; Escape cancels with zero confirms, unchanged truth and focus returned
to the active update field; and four native palette buttons, exactly one
expanded value, one mounted editor, one polite atomic live region and no
horizontal overflow hold at desktop, tablet and phone widths.

Evidence labels: ``route_intercepted_browser`` and
``authored_synthetic_client_fixture``; never live product operation. The
combined-editor assertions are intentionally red before Sol's parallel product
source lands.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REVIEW_DIR = Path(__file__).resolve().parent
if str(_REVIEW_DIR) not in sys.path:
    sys.path.insert(0, str(_REVIEW_DIR))

from test_reception_one_selected_action_console import (  # noqa: E402, F401
    CHOICE,
    CONSOLE,
    CONTROL_ID,
    CURRENT_DURATION,
    CURRENT_PRACTITIONER_ID,
    CURRENT_START,
    DIALOG,
    EDITOR,
    FIELDS,
    PALETTE,
    REQUESTED_DURATION,
    REQUESTED_START,
    SUMMARY,
    TARGET_PRACTITIONER_ID,
    WAIT_TIMEOUT,
    assert_field_value,
    assert_route_log_unchanged,
    assert_zero_routes,
    count_mounted_editors,
    install_routes,
    open_action,
    open_selected_appointment,
    reception_page,
    set_field,
    toggle_action,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Combined update editor surface: the provisional shared-draft summary and the
# single update-family Review control mounted inside the one labelled editor.
DRAFT_SUMMARY = "[data-testid='meta-grid-update-draft-summary']"
REVIEW = "[data-testid='meta-grid-update-review']"


# ─── Behavioural contract (evidence label: route_intercepted_browser) ────────


def test_same_family_switching_preserves_shared_update_draft(reception_page) -> None:
    """Time/duration/practitioner are one shared update draft kept across switches."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        # Time -> 09:15
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        # Switch to duration -> 45
        open_action(page, "duration", via="click")
        set_field(page, "duration", str(REQUESTED_DURATION))
        # Switch to practitioner -> the existing active target
        open_action(page, "practitioner", via="click")
        set_field(page, "practitioner", TARGET_PRACTITIONER_ID)
        # Revisit each field view: every valid pending value is preserved.
        open_action(page, "time", via="click")
        assert_field_value(page, "time", REQUESTED_START)
        open_action(page, "duration", via="click")
        assert_field_value(page, "duration", str(REQUESTED_DURATION))
        open_action(page, "practitioner", via="click")
        assert_field_value(page, "practitioner", TARGET_PRACTITIONER_ID)
        # A visibly provisional shared-draft summary names the changed dimensions
        # and stays patient-minimized.
        draft = page.locator(DRAFT_SUMMARY)
        assert draft.is_visible()
        text = draft.text_content()
        assert "9:15" in text or "09:15" in text
        assert "45" in text
        assert "Patel" in text
        assert "Margaret" not in text
        # Same-family switching issues zero mutation routes.
        assert_zero_routes(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_collapse_and_status_crossing_discard_whole_update_draft(
    reception_page,
) -> None:
    """Collapse and status crossover discard the complete unsubmitted update draft."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)

        # Build a combined update draft: time + duration.
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        open_action(page, "duration", via="click")
        set_field(page, "duration", str(REQUESTED_DURATION))
        draft = page.locator(DRAFT_SUMMARY)
        assert draft.is_visible()
        text = draft.text_content()
        assert "9:15" in text or "09:15" in text
        assert "45" in text

        # Collapse discards the whole unsubmitted update draft.
        toggle_action(page, "duration", via="Enter")
        assert not page.locator(DRAFT_SUMMARY).is_visible()
        assert page.locator(REVIEW).is_disabled()

        # A fresh combined draft is also discarded when crossing to status.
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        open_action(page, "duration", via="click")
        set_field(page, "duration", str(REQUESTED_DURATION))
        open_action(page, "status", via="click")
        assert not page.locator(DRAFT_SUMMARY).is_visible()
        assert page.locator(REVIEW).is_disabled()
        # Status never enters an update payload and no route was issued.
        assert_zero_routes(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_combined_review_emits_one_proposal_and_opens_existing_dialog(
    reception_page,
) -> None:
    """One Review click emits one combined update proposal and stops at the dialog."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        open_action(page, "duration", via="click")
        set_field(page, "duration", str(REQUESTED_DURATION))
        open_action(page, "practitioner", via="click")
        set_field(page, "practitioner", TARGET_PRACTITIONER_ID)
        # The visible update Review control exists.
        assert page.locator(REVIEW).is_visible()
        page.locator(REVIEW).click()
        # Even a safe/no-warning proposal stops at the existing dialog.
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert state["unexpected_mutation_count"] == 0
        body = state["proposal_bodies"][0]
        assert body["start_time_local"] == REQUESTED_START
        assert body["duration_minutes"] == REQUESTED_DURATION
        assert body["practitioner_id"] == TARGET_PRACTITIONER_ID
    finally:
        page.unroute("**/api/v1/**", handler)


def test_visible_confirm_and_save_emits_one_confirm_and_fresh_summary(
    reception_page,
) -> None:
    """Only the visible Confirm & Save emits one confirm and fresh reconciled truth."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        open_action(page, "duration", via="click")
        set_field(page, "duration", str(REQUESTED_DURATION))
        open_action(page, "practitioner", via="click")
        set_field(page, "practitioner", TARGET_PRACTITIONER_ID)
        assert page.locator(REVIEW).is_visible()
        page.locator(REVIEW).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        # Only the visible Confirm & Save control may cause one confirm request.
        page.locator(f"{DIALOG} button:has-text('Confirm & Save')").click()
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        # One freshly reconciled truth summary contains all three effective values.
        page.wait_for_function(
            """() => {
              const s = document.querySelector("[data-testid='meta-grid-selected-action-summary']");
              return Boolean(s) && s.textContent.includes('9:15') && s.textContent.includes('Patel');
            }""",
            timeout=WAIT_TIMEOUT,
        )
        summary = page.locator(SUMMARY).text_content()
        assert "9:15" in summary
        assert "45" in summary
        assert "Patel" in summary
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 1
        assert state["raw_count"] == 0
        assert state["unexpected_mutation_count"] == 0
    finally:
        page.unroute("**/api/v1/**", handler)


def test_escape_from_safe_dialog_zero_confirms_and_restores_focus(
    reception_page,
) -> None:
    """Escape from a safe dialog produces zero confirms and unchanged current truth."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        open_action(page, "duration", via="click")
        set_field(page, "duration", str(REQUESTED_DURATION))
        open_action(page, "practitioner", via="click")
        set_field(page, "practitioner", TARGET_PRACTITIONER_ID)
        assert page.locator(REVIEW).is_visible()
        page.locator(REVIEW).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        # Escape cancels the safe dialog.
        page.keyboard.press("Escape")
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        # Focus returns to the active update field (practitioner).
        page.wait_for_function(
            "tid => document.activeElement?.dataset?.testid === tid",
            arg=CONTROL_ID["practitioner"],
            timeout=WAIT_TIMEOUT,
        )
        # Zero confirms and current truth remains unchanged.
        assert state["confirm_count"] == 0
        assert state["start"] == CURRENT_START
        assert state["duration"] == CURRENT_DURATION
        assert state["practitioner"] == CURRENT_PRACTITIONER_ID
    finally:
        page.unroute("**/api/v1/**", handler)


@pytest.mark.parametrize(
    ("width", "height"),
    [(1280, 720), (768, 1024), (390, 844)],
    ids=["desktop", "tablet", "phone"],
)
def test_combined_editor_accessibility_responsive_and_single_live_region(
    reception_page, width, height
) -> None:
    """Native palette, one expanded value, one editor, one live region, no overflow."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        page.set_viewport_size({"width": width, "height": height})
        open_selected_appointment(page, base_url, state)
        # Four native palette targets, each at least 44-by-44 CSS pixels.
        choices = page.locator(
            f"{PALETTE} button[data-testid^='meta-grid-action-choice-']"
        )
        assert choices.count() == 4
        for field in FIELDS:
            box = page.locator(CHOICE[field]).bounding_box()
            assert box is not None
            assert box["width"] >= 44
            assert box["height"] >= 44
        # Open one update-family field editor and build a small draft.
        open_action(page, "time", via="click")
        set_field(page, "time", REQUESTED_START)
        # Exactly one expanded palette value and one mounted editor.
        expanded = [
            field
            for field in FIELDS
            if page.locator(CHOICE[field]).get_attribute("aria-expanded") == "true"
        ]
        assert expanded == ["time"]
        assert count_mounted_editors(page) == 1
        # The shared editor is labelled and contains one polite atomic live region.
        editor = page.locator(EDITOR)
        assert editor.get_attribute("aria-labelledby") or editor.get_attribute(
            "aria-label"
        )
        live = editor.locator("[role='status'][aria-live='polite'][aria-atomic='true']")
        assert live.count() == 1
        # No horizontal overflow at this width.
        layout = page.locator(CONSOLE).evaluate("""consoleEl => {
          const host = document.getElementById('bernie-meta-grid');
          const editor = consoleEl.querySelector('[data-testid="meta-grid-selected-action-editor"]');
          return {
            docOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            hostOverflow: host.scrollWidth > host.clientWidth,
            consoleOverflow: consoleEl.scrollWidth > consoleEl.clientWidth,
            editorOverflow: editor ? editor.scrollWidth > editor.clientWidth : false
          };
        }""")
        assert layout == {
            "docOverflow": False,
            "hostOverflow": False,
            "consoleOverflow": False,
            "editorOverflow": False,
        }
        assert_zero_routes(state)
    finally:
        page.unroute("**/api/v1/**", handler)
        page.set_viewport_size({"width": 1280, "height": 720})


# ─── Static source guard (evidence label: authored_synthetic_client_fixture) ──


def test_combined_update_editor_source_guards_reject_loops_raw_and_status() -> None:
    """Static guard: one combined bridge entry, one handleMoveResize, no loops,
    no raw writes, no status in the update input and no new route spelling.
    Evidence label: ``authored_synthetic_client_fixture``."""
    meta = (DOCS / "diary/meta-grid.js").read_text(encoding="utf-8")
    diary = (DOCS / "diary/diary.js").read_text(encoding="utf-8")

    # 1. One combined update bridge entry exists on both sides of the bridge.
    assert "metaGridProposeCombinedUpdate" in diary
    assert "proposeCombinedUpdate" in meta

    # 2. The combined client renders the shared draft summary and Review control.
    assert "meta-grid-update-draft-summary" in meta
    assert "meta-grid-update-review" in meta

    # 3. The combined bridge delegates to the existing Diary command exactly once.
    combined_start = diary.index("async function metaGridProposeCombinedUpdate")
    boundaries = []
    for boundary in (
        "\nfunction ",
        "\nasync function ",
        "\nwindow.EMR4DiaryMetaGridBridge",
    ):
        pos = diary.find(boundary, combined_start + 1)
        if pos != -1:
            boundaries.append(pos)
    combined_end = min(boundaries) if boundaries else len(diary)
    combined = diary[combined_start:combined_end]
    assert combined.count("handleMoveResize(") == 1

    # 4. No sequential proposal loop or batch executor inside the combined entry.
    for marker in (
        "for (",
        "while (",
        ".forEach(",
        "Promise.all",
        "sequentialRun",
        "executeMany",
        "runActions",
        "executorMap",
    ):
        assert marker not in combined

    # 5. The combined entry owns no raw compatibility write.
    assert 'method: "PUT"' not in combined
    assert 'method: "PATCH"' not in combined

    # 6. Status never enters the combined update input.
    assert "statusAction" not in combined
    assert "requestedStatus" not in combined
    assert "setAppointmentStatus" not in combined
    assert "/appointments/proposals/status/" not in combined

    # 7. The combined entry adds no new route spelling: it delegates to the
    #    existing command path and never constructs a proposal/confirm route.
    for marker in (
        "proposals/",
        "confirm_endpoint",
        "allowlistedConfirmApiPath",
        "apiFetch(",
    ):
        assert marker not in combined

    # 8. No raw PUT/PATCH fallback anywhere in the client.
    assert 'method: "PUT"' not in meta
    assert 'method: "PATCH"' not in meta
    assert 'method: "PUT"' not in diary
    assert 'method: "PATCH"' not in diary

    # 9. No new update-family proposal/confirm route spelling.
    for marker in (
        "proposals/update-bulk",
        "proposals/bulk-update",
        "proposals/multi-update",
        "proposals/update-multi",
        "proposals/combined-update",
        "proposals/update-combined",
        "proposals/multi-change",
        "proposals/confirm-bulk",
        "proposals/bulk-confirm",
        "proposals/combined-confirm",
        "proposals/multi-confirm",
        "proposals/confirm-multi",
    ):
        assert marker not in diary


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("This module is a pytest contract; do not run it directly.")
