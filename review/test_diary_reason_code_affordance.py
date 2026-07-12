"""
review/test_diary_reason_code_affordance.py — Focused test for S8 W2 affordance 1:
terminal-status reason-code reveal, emphasis, and inline validation.

When Cancelled/NoShow/DNA is selected in the booking modal, the
booking-status-reason-code-container must be immediately revealed with visual
emphasis (reason-code-highlight) and inline validation (reason-code-error) if
the select is left empty. Save-time validation remains the backstop.

Run:
    pytest review/test_diary_reason_code_affordance.py -q
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

SMOKE_APPT_7_ID = "smoke-appt-7"  # Cancelled appt


@pytest.fixture(scope="module")
def _base_url():
    with harness.serve_dir(DOCS_DIR) as base_url:
        yield base_url


def _open_smoke_diary(page, base_url):
    page.goto(base_url + "/diary/diary.html?smoke=true")
    page.wait_for_selector(".diary-column", state="visible", timeout=15000)


def _open_create_modal_via_js(page):
    """Open the booking create modal via JS to avoid click interception."""
    page.evaluate("""
        const col = activeTemplate.columns[0];
        openBookingModalForCreate(col, "09:30");
    """)
    page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)


# ── Test 1: Reason-code container revealed on terminal status selection ─────


def test_reason_code_container_revealed_on_cancelled(_base_url):
    """Open edit modal for a cancelled appointment; verify reason-code container
    is visible with highlight."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        # Open edit modal for the cancelled appointment via JS
        page.evaluate(f"""
            var appt = activeAppointments.find(a => a.id === '{SMOKE_APPT_7_ID}');
            if (appt) openBookingModalForEdit(appt);
        """)
        page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)

        # Assert the reason-code container is visible
        container = page.locator("[data-testid='booking-status-reason-code-container']")
        assert container.is_visible(), "Expected reason-code container visible for Cancelled"

        # Assert data-revealed attribute
        assert container.get_attribute("data-revealed") == "true", \
            "Expected reason-code container data-revealed=true"

        page.click("#btn-booking-close")
        page.wait_for_timeout(200)


# ── Test 2: Inline validation on empty reason-code select ──────────────────


def test_reason_code_inline_validation_on_empty(_base_url):
    """Empty reason-code select should show reason-code-error class."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        _open_create_modal_via_js(page)

        # Select Cancelled status
        page.locator("#booking-status").select_option("Cancelled")
        page.wait_for_timeout(300)

        container = page.locator("[data-testid='booking-status-reason-code-container']")
        assert container.is_visible(), "Expected reason-code container visible"

        # Trigger inline validation
        page.evaluate("highlightReasonCodeIfEmpty()")
        page.wait_for_timeout(100)

        has_error = page.evaluate(
            "document.getElementById('booking-status-reason-code-container')"
            ".classList.contains('reason-code-error')"
        )
        assert has_error, "Expected reason-code-error class on empty select"

        # Select a reason code
        page.locator("[data-testid='booking-status-reason-code']").select_option("PATIENT_CANCELLED")
        page.wait_for_timeout(100)

        has_error_after = page.evaluate(
            "document.getElementById('booking-status-reason-code-container')"
            ".classList.contains('reason-code-error')"
        )
        assert not has_error_after, "Expected reason-code-error class removed after selection"

        page.click("#btn-booking-close")
        page.wait_for_timeout(200)


# ── Test 3: Save-time validation backstop ──────────────────────────────────


def test_save_time_reason_code_validation_backstop(_base_url):
    """Save with a terminal status and no reason code shows save-time error."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        _open_create_modal_via_js(page)

        # Select a provisional patient
        page.fill("#booking-patient-search", "Test")
        page.wait_for_timeout(500)
        prov_item = page.locator(".search-result-provisional")
        if prov_item.is_visible():
            prov_item.click()
            page.wait_for_timeout(200)

        # Set Cancelled status
        page.locator("#booking-status").select_option("Cancelled")
        page.wait_for_timeout(300)

        # Try to save without reason code
        page.locator("#btn-booking-save").click()
        page.wait_for_timeout(500)

        # Save-time error should be visible
        error_el = page.locator("#booking-error:not(.hidden)")
        assert error_el.is_visible(), "Expected save-time error for missing reason code"
        assert "reason code" in error_el.text_content().lower(), \
            "Save-time error must mention reason code"

        page.click("#btn-booking-close")
        page.wait_for_timeout(200)
