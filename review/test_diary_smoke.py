"""
review/test_diary_smoke.py — deterministic diary-grid review against ?smoke=true.

Runs with NO backend, NO auth, NO seeding: the diary's built-in smoke mode
(`?smoke=true`) renders the grid from embedded fixtures, so these assertions are
stable and repeatable. office.js is stubbed so Office.onReady fires offline.

This is the model-OUT-of-the-loop review pattern: pytest executes the checks,
emits JUnit XML, and Ariadne reads only failures.

Prerequisites (one-time):
    pip install playwright pytest
    playwright install chromium

Run:
    pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q

Each row in checks_diary.json becomes one parametrized test case, so the JUnit
report lists every check by name. Add a check = add a row (no code).

Initial ratified scaffold. Selectors/expectations derived from docs/diary/diary.js
smoke mode as of 2026-06-26; re-verify if the diary DOM changes. The
robust long-term fix for selector drift is stable data-testid attributes on the
diary elements (a frontend task), which keeps this harness from needing repair.
"""
import json
import sys
from pathlib import Path

import pytest

# Make harness importable regardless of pytest's rootdir / cwd.
sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency not installed
    pytest.skip("playwright not installed (pip install playwright && playwright install chromium)",
                allow_module_level=True)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
CHECKS = json.loads((Path(__file__).parent / "checks_diary.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def diary_page():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        page.goto(base_url + CHECKS["target"])
        page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        # Open flow panel to ensure the flow lists render
        page.click("#btn-toggle-flow")
        page.wait_for_selector("#diary-flow-panel:not(.hidden)", state="visible", timeout=5000)
        yield page
        browser.close()


@pytest.mark.parametrize("check", CHECKS["checks"], ids=lambda c: c["name"])
def test_diary_check(diary_page, check):
    result = harness.run_check(diary_page, check)
    assert result["passed"], result


def test_booking_audit_history(diary_page):
    # Click Margaret Thompson's appointment on the grid to make it active.
    diary_page.click(".appt:has-text('Margaret Thompson')")
    
    # Wait for the edit button to appear inside the active appointment block, then click it.
    diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt", state="visible", timeout=3000)
    diary_page.click(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt")
    
    # Wait for the booking modal to become visible
    diary_page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)
    
    # The audit section should be visible, but collapsed by default (has class hidden on the content element)
    diary_page.wait_for_selector("#booking-audit-section:not(.hidden)", state="visible", timeout=2000)
    diary_page.wait_for_selector("#booking-audit-content.hidden", state="attached", timeout=2000)
    
    # Click the audit header to expand it
    diary_page.click("#booking-audit-header")
    
    # Now the content should not be hidden
    diary_page.wait_for_selector("#booking-audit-content:not(.hidden)", state="visible", timeout=2000)
    
    # Check that mock events are rendered
    assert diary_page.locator(".booking-audit-item", has_text="Status Change").count() == 1
    assert diary_page.locator(".booking-audit-item", has_text="Create").count() == 1
    
    # Close the modal
    diary_page.click("#btn-booking-close")
    diary_page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=2000)
