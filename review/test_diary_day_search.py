"""
review/test_diary_day_search.py — Focused test for S8 W2 affordance 3:
same-day client-side appointment search/filter.

A header text input filters or highlights already-rendered appointments by
patient name, provisional name, or reason. The query must survive the silent
60-second refresh without stealing focus or resetting the query, and must not
disturb .appt-active selection preservation.

Run:
    pytest review/test_diary_day_search.py -q
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
REVIEW_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
harness.assert_valid_review_token(REVIEW_AUTH_TOKEN)

SMOKE_APPT_1_ID = "smoke-appt-1"
SMOKE_APPT_5_ID = "smoke-appt-5"


@pytest.fixture(scope="module")
def _base_url():
    with harness.serve_dir(DOCS_DIR) as base_url:
        yield base_url


def _open_smoke_diary(page, base_url):
    page.goto(base_url + "/diary/diary.html?smoke=true")
    page.wait_for_selector(".diary-column", state="visible", timeout=15000)


# ── Test 1: Search input exists and is interactive ──────────────────────────


def test_search_input_exists(_base_url):
    """The search input and clear button should be present in the header."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        search_input = page.locator("#diary-search-input")
        assert search_input.is_visible(), "Expected search input to be visible"
        assert search_input.get_attribute("placeholder") is not None

        clear_btn = page.locator("#btn-diary-search-clear")
        # Clear button starts hidden (display:none) - check it exists in DOM
        assert clear_btn.count() == 1, "Expected clear button to exist in DOM"


# ── Test 2: Search by patient name highlights matching appointments ─────────


def test_search_by_patient_name_highlights(_base_url):
    """Typing a patient name in the search input should add the
    appt-search-match class to matching appointment elements."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        # Type a patient name into the search input
        search_input = page.locator("#diary-search-input")
        search_input.fill("Margaret")
        page.wait_for_timeout(500)

        # Assert at least one appointment has the search-match class
        match_count = page.locator(".appt-search-match").count()
        assert match_count > 0, f"Expected at least 1 search match for 'Margaret', got {match_count}"

        # Clear search
        clear_btn = page.locator("#btn-diary-search-clear")
        clear_btn.click()
        page.wait_for_timeout(200)

        # Assert matches are cleared
        assert page.locator(".appt-search-match").count() == 0, \
            "Expected no search matches after clearing"


# ── Test 3: Search by reason text ───────────────────────────────────────────


def test_search_by_reason_highlights(_base_url):
    """Typing a reason keyword should highlight matching appointments by reason."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        search_input = page.locator("#diary-search-input")
        search_input.fill("Hyper")
        page.wait_for_timeout(500)

        match_count = page.locator(".appt-search-match").count()
        assert match_count > 0, f"Expected at least 1 search match for 'Hyper' (reason text), got {match_count}"

        # Clear with Escape key
        search_input.press("Escape")
        page.wait_for_timeout(200)

        assert page.locator(".appt-search-match").count() == 0, \
            "Expected no search matches after Escape clear"


# ── Test 4: Search survives silent refresh ──────────────────────────────────


def test_search_survives_silent_refresh(_base_url):
    """The search query and highlights should persist after a silent refresh
    (loadDiary(true))."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        # Type a search query
        search_input = page.locator("#diary-search-input")
        search_input.fill("Margaret")
        page.wait_for_timeout(500)

        match_before = page.locator(".appt-search-match").count()
        assert match_before > 0, f"Expected matches before refresh, got {match_before}"

        # Trigger a silent refresh
        page.evaluate("() => loadDiary(true)")
        page.wait_for_timeout(1000)

        # Wait for grid to re-render
        page.wait_for_selector(".diary-column", state="visible", timeout=10000)

        # The search input should still contain the query
        current_query = search_input.input_value()
        assert current_query == "Margaret", \
            f"Expected search query to survive refresh, got '{current_query}'"

        # Matches should be restored after refresh
        match_after = page.locator(".appt-search-match").count()
        assert match_after > 0, f"Expected matches after refresh, got {match_after}"


# ── Test 5: Search does not disturb .appt-active selection ──────────────────


def test_search_preserves_active_selection(_base_url):
    """Using the search should not disturb the .appt-active selection when an
    appointment is already active."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        # Select an appointment
        page.click(f'.appt[data-id="{SMOKE_APPT_1_ID}"]')
        page.wait_for_timeout(300)

        assert page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"].appt-active').count() == 1, \
            "Expected appointment to be active before search"

        # Search for something that might match the same appointment
        search_input = page.locator("#diary-search-input")
        search_input.fill("Margaret")
        page.wait_for_timeout(500)

        # The active appointment should still be active
        assert page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"].appt-active').count() == 1, \
            "Expected appointment to remain active after search"

        # Clear search
        search_input.fill("")
        page.wait_for_timeout(200)
