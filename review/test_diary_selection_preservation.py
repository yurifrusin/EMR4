"""
review/test_diary_selection_preservation.py — Failing-first regression test for
appointment selection preservation across silent diary refreshes.

The defect: every silent auto-refresh (scheduleRefresh -> loadDiary(true))
rebuilds the grid via renderGrid(), which clears grid.innerHTML. The active
appointment selection (.appt-active) is destroyed mid-action without general
preservation.

This test follows the route-intercepted smoke-mode pattern from
review/test_diary_smoke.py but uses a dedicated full-page lifecycle per test
to avoid cross-test state contamination from the shared diary_page fixture.
"""

import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    pytest.skip("playwright not installed", allow_module_level=True)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
REVIEW_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
harness.assert_valid_review_token(REVIEW_AUTH_TOKEN)

# Known smoke-mode appointment IDs from getMockAppointments()
SMOKE_APPT_1_ID = "smoke-appt-1"
SMOKE_APPT_5_ID = "smoke-appt-5"


def _open_smoke_diary(page, base_url):
    """Navigate to smoke-mode diary and wait for columns to render."""
    page.goto(base_url + "/diary/diary.html?smoke=true")
    page.wait_for_selector(".diary-column", state="visible", timeout=15000)


def _select_appointment_by_id(page, appt_id):
    """Click a specific appointment by data-id to make it active."""
    selector = f'.appt[data-id="{appt_id}"]'
    page.wait_for_selector(selector, state="visible", timeout=5000)
    page.click(selector)
    page.wait_for_timeout(200)  # Let click handler complete
    # Verify selection was applied
    assert page.locator(f"{selector}.appt-active").count() == 1, \
        f"Expected {appt_id} to carry .appt-active after click"


def _trigger_silent_refresh(page):
    """Invoke loadDiary(true) directly to simulate a silent auto-refresh."""
    page.evaluate("() => loadDiary(true)")
    page.wait_for_timeout(500)  # Allow async render to complete


@pytest.fixture(scope="module")
def _base_url():
    """Module-scoped static file server so each test can open a fresh page."""
    with harness.serve_dir(DOCS_DIR) as base_url:
        yield base_url


# ── Test: selection is preserved across a silent refresh ──────────────


def test_selection_preserved_across_silent_refresh(_base_url):
    """
    Select a smoke-mode appointment, trigger a silent refresh (loadDiary(true)),
    and assert the same appointment still carries .appt-active.
    This is expected to FAIL against unfixed code.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        _open_smoke_diary(page, _base_url)
        _select_appointment_by_id(page, SMOKE_APPT_1_ID)

        # Confirm .appt-active exists before refresh
        assert page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"].appt-active').count() == 1

        # Trigger the silent refresh that destroys the grid
        _trigger_silent_refresh(page)

        # THE DEFECT: selection is gone after refresh in unfixed code.
        # This assertion should FAIL before the fix and PASS after.
        assert page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"].appt-active').count() == 1, \
            "Selection was lost after silent refresh — this is the expected failure in unfixed code"

        browser.close()


def test_selection_preserved_for_different_appointment(_base_url):
    """
    Same test with a different smoke-mode appointment (Arrived status)
    to ensure the fix works across appointment types.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        _open_smoke_diary(page, _base_url)
        _select_appointment_by_id(page, SMOKE_APPT_5_ID)

        assert page.locator(f'.appt[data-id="{SMOKE_APPT_5_ID}"].appt-active').count() == 1

        _trigger_silent_refresh(page)

        assert page.locator(f'.appt[data-id="{SMOKE_APPT_5_ID}"].appt-active').count() == 1, \
            "Selection was lost after silent refresh — expected failure in unfixed code"

        browser.close()


def test_selection_not_fabricated_when_none_active_before_refresh(_base_url):
    """
    If there was no active selection before the silent refresh, one must not
    be fabricated by the restoration logic.  Smoke-mode fixtures always return
    the same appointments regardless of date, so we test the no-prior-selection
    case directly rather than the "appointment removed" case.
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        _open_smoke_diary(page, _base_url)
        _select_appointment_by_id(page, SMOKE_APPT_1_ID)

        # Clear all active selections before refresh
        page.evaluate("() => document.querySelectorAll('.appt-active').forEach(el => el.classList.remove('appt-active'))")

        # No .appt-active should exist before refresh
        assert page.locator(".appt-active").count() == 0

        _trigger_silent_refresh(page)

        # The fix must NOT fabricate a selection when none was active before
        assert page.locator(".appt-active").count() == 0, \
            "Selection was fabricated when none existed before refresh"

        browser.close()
