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
REVIEW_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
harness.assert_valid_review_token(REVIEW_AUTH_TOKEN)
SPRINT98_FORBIDDEN_ORDINARY_COPY = [
    "missing_practitioner_id",
    "practitioner_id",
    "Practitioner ID is required",
    "Not Found",
    "123e4567-e89b-12d3-a456-426614174000",
]


def assert_bernie_confirmed_state(page):
    """Sprint 100: confirmation clears the action controls and renders a compact terminal state."""
    page.wait_for_selector("[data-testid='bernie-confirmed-container']", state="visible", timeout=5000)
    status = page.locator("[data-testid='bernie-review-status']")
    assert "Confirmed" in status.text_content()
    headline = page.locator("[data-testid='bernie-review-headline']")
    assert "Booking confirmed successfully" in headline.text_content()
    assert page.locator("[data-testid='bernie-review-confirm-button']").count() == 0


def route_minimal_diary_api(page):
    """Route enough non-smoke API calls for deterministic diary auth tests."""
    def handle_api(route):
        url = route.request.url
        if "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-auth",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "surface": "bernie_staff_review",
                "enabled": False,
                "eligible": False,
                "reason": "review_auth_fixture"
            }))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    page.route("**/api/v1/**", handle_api)


@pytest.fixture(scope="module")
def diary_page():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        # Default mock for interpret-booking-instruction
        mock_default_interpret = {
            "safe": True,
            "result": "interpreted",
            "command_candidate": {
                "practitioner_id": "prac-1",
                "patient_id": "smoke-pat-1",
                "date_from": "today",
                "duration_minutes": "15"
            }
        }
        page.route(
            "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_default_interpret)
            )
        )

        page.goto(base_url + CHECKS["target"])
        page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        # Open flow panel to ensure the flow lists render
        page.click("#btn-toggle-flow")
        page.wait_for_selector("#diary-flow-panel:not(.hidden)", state="visible", timeout=5000)
        yield page
        browser.close()


def trigger_route_intercepted_bernie(page, instruction="Please find practitioner_id:prac-1 patient_id:smoke-pat-1", register_default_mock=True):
    if register_default_mock:
        import json
        mock_default_interpret = {
            "safe": True,
            "result": "interpreted",
            "command_candidate": {
                "practitioner_id": "prac-1",
                "patient_id": "smoke-pat-1",
                "date_from": "today",
                "duration_minutes": "15"
            }
        }
        page.route(
            "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_default_interpret)
            )
        )
    page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
    page.locator("[data-testid='bernie-instruction-input']").fill(instruction)
    page.locator("[data-testid='btn-bernie-instruction-submit']").click()


@pytest.mark.parametrize("check", CHECKS["checks"], ids=lambda c: c["name"])
def test_diary_check(diary_page, check):
    result = harness.run_check(diary_page, check)
    assert result["passed"], result


def test_auth_banner_shows_when_token_missing(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    route_minimal_diary_api(diary_page)
    harness.clear_auth(diary_page)

    try:
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("[data-testid='diary-auth-banner']:not(.hidden)", state="visible", timeout=5000)
        assert "Please sign in again" in diary_page.locator("[data-testid='diary-auth-banner']").text_content()
        assert diary_page.locator("#diary-grid-container.hidden").count() == 1
    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_auth_banner_shows_and_clears_expired_local_token(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    route_minimal_diary_api(diary_page)

    try:
        diary_page.evaluate("() => localStorage.setItem('emr4_token', 'eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjF9.sig')")
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("[data-testid='diary-auth-banner']:not(.hidden)", state="visible", timeout=5000)
        assert diary_page.evaluate("() => localStorage.getItem('emr4_token')") is None
    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_auth_banner_shows_and_clears_token_after_backend_401(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    diary_page.route(
        "**/api/v1/**",
        lambda route: route.fulfill(status=401, content_type="application/json", body=json.dumps({"detail": "expired"}))
    )

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("[data-testid='diary-auth-banner']:not(.hidden)", state="visible", timeout=5000)
        assert diary_page.evaluate("() => localStorage.getItem('emr4_token')") is None
        assert diary_page.locator("#diary-error:not(.hidden)").count() == 0
    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_booking_audit_history(diary_page):
    # Click Margaret Thompson's appointment on the grid to make it active.
    diary_page.click(".appt:has-text('Margaret Thompson')")

    # Wait for the edit button to appear inside the active appointment block, then click it.
    diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt", state="visible", timeout=3000)
    diary_page.click(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt")

    # Wait for the booking modal to become visible
    diary_page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)

    # The audit section should be visible, but collapsed by default (has class hidden on the content element)
    diary_page.wait_for_selector("[data-testid='booking-audit-section']:not(.hidden)", state="visible", timeout=2000)
    diary_page.wait_for_selector("[data-testid='booking-audit-content'].hidden", state="attached", timeout=2000)

    # Check accessibility/ARIA attributes
    header = diary_page.locator("[data-testid='booking-audit-header']")
    assert header.get_attribute("role") == "button"
    assert header.get_attribute("tabindex") == "0"
    assert header.get_attribute("aria-controls") == "booking-audit-content"
    assert header.get_attribute("aria-expanded") == "false"

    # Test keyboard toggle with Enter
    header.focus()
    diary_page.keyboard.press("Enter")
    diary_page.wait_for_selector("[data-testid='booking-audit-content']:not(.hidden)", state="visible", timeout=2000)
    assert header.get_attribute("aria-expanded") == "true"

    # Test keyboard toggle with Space
    diary_page.keyboard.press("Space")
    diary_page.wait_for_selector("[data-testid='booking-audit-content'].hidden", state="attached", timeout=2000)
    assert header.get_attribute("aria-expanded") == "false"

    # Click the audit header to expand it again and verify standard click
    header.click()
    diary_page.wait_for_selector("[data-testid='booking-audit-content']:not(.hidden)", state="visible", timeout=2000)
    assert header.get_attribute("aria-expanded") == "true"

    # Check that mock events are rendered
    assert diary_page.locator("[data-testid='booking-audit-item']", has_text="Status Changed by Dr. Practice Owner").count() == 1
    assert diary_page.locator("[data-testid='booking-audit-item']", has_text="Created by Staff (11111111)").count() == 1

    # Check status transitions and formatting
    assert diary_page.locator("[data-testid='booking-audit-item']", has_text="Changed from Booked to Confirmed").count() == 1

    # Check warnings and warning summary
    assert diary_page.locator("[data-testid='booking-audit-warnings']", has_text="Warnings: [DOUBLE_BOOKING]").count() == 1
    assert diary_page.locator("[data-testid='booking-audit-warning-summary']", has_text="Warning Summary: Double-booked with another appointment").count() == 1

    # Close the modal
    diary_page.click("#btn-booking-close")
    diary_page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=2000)

    # Open again to verify reset of aria-expanded
    # Click to deactivate the active appointment
    diary_page.click(".appt:has-text('Margaret Thompson')")
    # Click again to activate it
    diary_page.click(".appt:has-text('Margaret Thompson')")
    diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt", state="visible", timeout=3000)
    diary_page.click(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt")
    diary_page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)

    header = diary_page.locator("[data-testid='booking-audit-header']")
    assert header.get_attribute("aria-expanded") == "false"

    diary_page.click("#btn-booking-close")
    diary_page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=2000)


def test_reason_code_dropdown_no_default_and_ui_required(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    diary_page.goto(base_url + CHECKS["target"])
    diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    diary_page.click(".appt:has-text('Margaret Thompson')")
    diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt", state="visible", timeout=3000)
    diary_page.click(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt")
    diary_page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)

    reason_container = diary_page.locator("[data-testid='booking-status-reason-code-container']")
    assert "hidden" in (reason_container.get_attribute("class") or "")

    future_date = diary_page.evaluate("() => { const d = new Date(); d.setDate(d.getDate() + 1); return localDateKey(d); }")
    diary_page.fill("#booking-date", future_date)
    diary_page.fill("#booking-time", "09:00")
    diary_page.select_option("#booking-status", "Cancelled")
    diary_page.wait_for_selector("[data-testid='booking-status-reason-code-container']:not(.hidden)", state="visible", timeout=2000)
    reason_select = diary_page.locator("[data-testid='booking-status-reason-code']")
    assert reason_select.input_value() == ""
    assert reason_select.locator("option[value='LEGACY_UNCLASSIFIED']").count() == 0
    assert reason_select.locator("option[value='PATIENT_CANCELLED']").count() == 1
    assert reason_select.locator("option[value='PATIENT_RESCHEDULED']").count() == 1
    assert reason_select.locator("option[value='PATIENT_UNWELL']").count() == 1
    assert reason_select.locator("option[value='CLINIC_RESCHEDULED']").count() == 1
    assert reason_select.locator("option[value='DID_NOT_ATTEND']").count() == 0
    assert reason_select.locator("option[value='LEFT_WITHOUT_SEEN']").count() == 0

    note = diary_page.locator("[data-testid='booking-cancel-reason']")
    assert int(note.get_attribute("maxlength")) <= 150
    warning = diary_page.locator("[data-testid='booking-reason-privacy-warning']")
    assert "do not enter symptoms" in warning.text_content().lower()

    diary_page.select_option("#booking-status", "Booked")
    diary_page.click("#btn-booking-delete")
    diary_page.click("#btn-booking-delete")
    error = diary_page.locator("#booking-error")
    assert "select an administrative reason code" in error.text_content()

    diary_page.click("#btn-booking-close")
    diary_page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=2000)


def test_reason_code_retrospective_options_are_prioritized(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    diary_page.goto(base_url + CHECKS["target"])
    diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    diary_page.click(".appt:has-text('Margaret Thompson')")
    diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt", state="visible", timeout=3000)
    diary_page.click(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt")
    diary_page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)

    past_date = diary_page.evaluate("() => { const d = new Date(); d.setDate(d.getDate() - 1); return localDateKey(d); }")
    diary_page.fill("#booking-date", past_date)
    diary_page.fill("#booking-time", "09:00")
    diary_page.select_option("#booking-status", "DNA")
    diary_page.wait_for_selector("[data-testid='booking-status-reason-code-container']:not(.hidden)", state="visible", timeout=2000)

    option_values = diary_page.locator("[data-testid='booking-status-reason-code'] option").evaluate_all(
        "(options) => options.map((option) => option.value)"
    )
    assert option_values == ["", "DID_NOT_ATTEND", "LEFT_WITHOUT_SEEN", "ADMIN_ERROR", "DUPLICATE_BOOKING", "OTHER"]
    assert "PATIENT_CANCELLED" not in option_values
    assert "PATIENT_UNWELL" not in option_values

    diary_page.click("#btn-booking-close")
    diary_page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=2000)


def test_reason_code_noshow_options_match_attendance_housekeeping(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    diary_page.goto(base_url + CHECKS["target"])
    diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    diary_page.click(".appt:has-text('Margaret Thompson')")
    diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt", state="visible", timeout=3000)
    diary_page.click(".appt.appt-active:has-text('Margaret Thompson') .btn-edit-appt")
    diary_page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=5000)

    diary_page.select_option("#booking-status", "NoShow")
    diary_page.wait_for_selector("[data-testid='booking-status-reason-code-container']:not(.hidden)", state="visible", timeout=2000)

    option_values = diary_page.locator("[data-testid='booking-status-reason-code'] option").evaluate_all(
        "(options) => options.map((option) => option.value)"
    )
    assert option_values == ["", "DID_NOT_ATTEND", "LEFT_WITHOUT_SEEN", "ADMIN_ERROR", "DUPLICATE_BOOKING", "OTHER"]
    assert "PATIENT_CANCELLED" not in option_values
    assert "PATIENT_UNWELL" not in option_values

    diary_page.click("#btn-booking-close")
    diary_page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=2000)


def test_reason_code_payload_threading_present_in_diary_source():
    source = (DOCS_DIR / "diary" / "diary.js").read_text(encoding="utf-8")
    assert "status_reason_code: statusReasonCode" in source
    assert "bookingStatusReasonCodeValue()" in source
    assert "LEGACY_UNCLASSIFIED" not in source


def test_slot_search_preview_harness_active(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        # Navigate with both smoke=true and slot_preview=true parameters
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&slot_preview=true")
        diary_page.wait_for_selector(".diary-column", state="visible", timeout=15000)

        # Assert count of preview slots matches the expected mock count (2 slots)
        assert diary_page.locator(".slot-preview-candidate").count() == 2

        # Assert correct room rendering/positions by verifying data-id attributes exist
        assert diary_page.locator(".slot-preview-candidate[data-id='slot-preview-1']").count() == 1
        assert diary_page.locator(".slot-preview-candidate[data-id='slot-preview-2']").count() == 1

        # Verify visual labels contain candidate information
        assert "Available Slot Preview 1" in diary_page.locator(".slot-preview-candidate[data-id='slot-preview-1']").text_content()
        assert "Available Slot Preview 2" in diary_page.locator(".slot-preview-candidate[data-id='slot-preview-2']").text_content()

        # Verify non-interactivity: click the slot-preview block and assert booking modal does not open
        diary_page.click(".slot-preview-candidate[data-id='slot-preview-1']")
        diary_page.wait_for_timeout(500)  # Wait briefly to ensure no modal opens asynchronously
        assert diary_page.locator("#booking-modal").is_hidden()

    finally:
        # Restore page to original smoke target for other tests
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        # Ensure flow panel is open
        if diary_page.locator("#diary-flow-panel.hidden").count() > 0:
            diary_page.click("#btn-toggle-flow")
            diary_page.wait_for_selector("#diary-flow-panel:not(.hidden)", state="visible", timeout=5000)


def test_bernie_review_blocked(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=blocked")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Needs details"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Add the missing details"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Nothing is booked yet" in action.text_content()

        # Verify block issues list
        assert diary_page.locator("[data-testid='bernie-review-blocks-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="I need a practitioner before I can search.").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="Missing Practitioner Id").count() == 0

        # Verify confirmation sections/elements are hidden
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

def test_bernie_review_candidate_selection(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=candidate_selection_required")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Choose a time"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Bernie found these times"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Nothing is booked until you confirm" in action.text_content()

        # Verify candidates list
        assert diary_page.locator("[data-testid='bernie-review-candidates-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-candidate-item']").text_content()

        # Verify confirmation/selected sections/elements are hidden
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_confirmation_ready(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Ready to book"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert "Would you like to confirm?" in headline.text_content()

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Review the details before confirming" in action.text_content()

        # Verify selected slot
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-selected-slot']").text_content()

        # Verify explicit confirm action
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")

        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert success_msg.is_hidden()

        confirm_btn.click()

        assert_bernie_confirmed_state(diary_page)
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_confirmation_ready_stale_gate_suppresses_confirm(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready_stale")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Needs details"

        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert "Would you like to confirm?" not in headline.text_content()

        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_schedule_reason_codes(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    cases = [
        {
            "param": "practitioner_day_off",
            "expected_status": "Practitioner away",
            "expected_headline": "Practitioner is away",
            "expected_action": "Choose another practitioner or another date."
        },
        {
            "param": "fully_booked",
            "expected_status": "Fully booked",
            "expected_headline": "Fully booked",
            "expected_action": "Choose another time, practitioner, or date."
        },
        {
            "param": "breaks_only",
            "expected_status": "Break time",
            "expected_headline": "Break time",
            "expected_action": "Choose a time outside the break window."
        },
        {
            "param": "outside_hours",
            "expected_status": "Outside hours",
            "expected_headline": "Requested time is outside rostered hours",
            "expected_action": "Choose a time within the practitioner's rostered hours."
        },
        {
            "param": "elapsed_same_day",
            "expected_status": "Clinic day exhausted",
            "expected_headline": "No times left today",
            "expected_action": "Choose another date."
        },
        {
            "param": "searched_no_candidates",
            "expected_status": "No slots",
            "expected_headline": "No matching slots found",
            "expected_action": "Try a wider time window, another practitioner, or another date."
        }
    ]

    for case in cases:
        try:
            diary_page.goto(base_url + f"/diary/diary.html?smoke=true&bernie_review={case['param']}")
            diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

            # Verify status is rendered
            status = diary_page.locator("[data-testid='bernie-review-status']")
            assert status.text_content().strip() == case["expected_status"]

            # Verify headline
            headline = diary_page.locator("[data-testid='bernie-review-headline']")
            assert headline.text_content().strip() == case["expected_headline"]

            # Verify action description
            action = diary_page.locator("[data-testid='bernie-review-action']")
            assert action.text_content().strip() == case["expected_action"]

            # Verify empty candidate message matches the action text
            empty = diary_page.locator("[data-testid='bernie-review-candidates-empty']")
            assert empty.text_content().strip() == case["expected_action"]

        finally:
            diary_page.goto(base_url + CHECKS["target"])
            diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_route_intercepted_blocked(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "intent": "bernie_supervised_booking",
        "result": "blocked",
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Practitioner ID is required.",
        "normalization": {
            "safe": False,
            "constraint": None,
            "warnings": [],
            "blocks": [
                { "code": "missing_practitioner_id", "severity": "blocked", "message": "Practitioner ID is required." }
            ],
            "summary": "Normalization failed."
        },
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Practitioner ID is required.",
            "status": "blocked",
            "staff_action_required": "Review blocked issues before retrying; no booking can be confirmed from this payload.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "0 warning(s), 1 blocked issue(s).",
            "evidence_summary": "Blocked review payload; no confirm evidence is available.",
            "warnings": [],
            "blocks": [
                { "code": "missing_practitioner_id", "severity": "blocked", "message": "Practitioner ID is required." }
            ],
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": [
            { "code": "missing_practitioner_id", "severity": "blocked", "message": "Practitioner ID is required." }
        ]
    }

    # Intercept route
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)
        assert status.text_content().strip() == "Needs details"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Add the missing details"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Nothing is booked yet" in action.text_content()

        # Verify block issues list
        assert diary_page.locator("[data-testid='bernie-review-blocks-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="Missing Practitioner Id").count() == 1

        # Verify confirmation sections/elements are hidden
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        # Clean up route
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_route_intercepted_candidate_selection(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "intent": "bernie_supervised_booking",
        "result": "candidate_selection_required",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "Candidate selection required.",
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "date_from": "2026-06-27",
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalization success."
        },
        "search_proposal": {
            "intent": "search_slots",
            "candidates": [
                {
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00:00",
                    "duration_minutes": 15,
                    "warnings": []
                }
            ]
        },
        "selection_proposal": None,
        "staff_review": {
            "headline": "Candidate selection required.",
            "status": "candidate_selection_required",
            "staff_action_required": "Select one candidate slot before preparing confirmation evidence.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [
                {
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00:00",
                    "duration_minutes": 15,
                    "warnings": []
                }
            ],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Candidate slot summaries are review-only until staff selects one slot.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    # Intercept route
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)
        assert status.text_content().strip() == "Choose a time"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Bernie found these times"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Choose a time to show it on the diary" in action.text_content()

        # Verify candidates list
        assert diary_page.locator("[data-testid='bernie-review-candidates-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-candidate-item']").text_content()

        # Verify confirmation/selected sections/elements are hidden
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        # Clean up route
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_route_intercepted_confirmation_ready(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "summary": "Confirmation ready.",
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "date_from": "2026-06-27",
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalization success."
        },
        "search_proposal": {
            "intent": "search_slots",
            "candidates": []
        },
        "selection_proposal": {
            "intent": "select_slot_for_create_proposal",
            "safe": True,
            "requires_confirmation": True,
            "autonomy_tier": "proposal",
            "selected_candidate": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "create_proposal": {
                "intent": "create_appointment",
                "command": {
                    "patient_id": "smoke-pat-1",
                    "practitioner_id": "prac-1",
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00:00",
                    "reason": "Follow-up"
                }
            }
        },
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence for explicit staff approval.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False,
                "selection_proposal": {
                    "intent": "select_slot_for_create_proposal",
                    "safe": True,
                    "create_proposal": {
                        "intent": "create_appointment",
                        "command": {
                            "patient_id": "smoke-pat-1",
                            "practitioner_id": "prac-1",
                            "appointment_date": "2026-06-27",
                            "start_time_local": "09:00:00",
                            "reason": "Follow-up"
                        }
                    }
                }
            },
            "confirm_evidence": [
                "bernie_confirm_create_proposal",
                "source_slot_selection_proposal",
                "source_create_proposal"
            ]
        },
        "warnings": [],
        "blocks": []
    }

    # Intercept route
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    # Fail on confirm-bernie write attempts
    def fail_on_confirm(route):
        raise AssertionError("Write path to confirm-bernie must not be called")

    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        fail_on_confirm
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)
        assert status.text_content().strip() == "Ready to book"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert "Would you like to confirm?" in headline.text_content()

        # Verify selected slot
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-selected-slot']").text_content()

        # Verify explicit confirm action
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")

        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert success_msg.is_hidden()

        # Click confirm simulates booking
        confirm_btn.click()

        assert_bernie_confirmed_state(diary_page)
    finally:
        # Clean up routes
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_interpret_preview_renders_before_supervised_review(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    interpret_requests = []
    supervised_requests = []
    confirm_payloads = []

    mock_interpret = {
        "intent": "interpret_booking_instruction",
        "safe": True,
        "result": "interpreted",
        "autonomy_tier": "execute_with_report",
        "summary": "Find a 15 minute follow-up for this patient with prac-1 today.",
        "confidence": 0.9,
        "command_candidate": {
            "practitioner_id": "prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "today",
            "duration_minutes": "15",
            "earliest_time": "09:00",
            "latest_time": "11:00"
        },
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "patient_id": "smoke-pat-1",
                "date_from": "2026-06-27",
                "duration_minutes": 15,
                "earliest_time": "09:00:00",
                "latest_time": "11:00:00"
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully."
        },
        "warnings": [],
        "blocks": [],
        "provider_metadata": {
            "provider": "fake",
            "mode": "mocked",
            "live_provider": False
        }
    }
    mock_review = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "supervised",
        "summary": "Proposal confirmation ready",
        "normalization": mock_interpret["normalization"],
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": {
                "id": "slot-65",
                "appointment_date": "2026-06-27",
                "start_time_local": "09:30:00",
                "duration_minutes": 15
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Supervised review prepared from interpreted intent.",
            "warnings": [],
            "blocks": [],
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": { "proposal_id": "prop-65" },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    def handle_interpret(route):
        interpret_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))

    def handle_supervised(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_review))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected confirm"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction", handle_interpret)
    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_interpret=true&practitioner_id=prac-1&patient_id=smoke-pat-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, "Please find practitioner_id:prac-1 patient_id:smoke-pat-1 date_from:today duration:15 earliest_time:09:00 latest_time:11:00", register_default_mock=False)

        diary_page.wait_for_selector("[data-testid='bernie-interpret-preview']", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)

        assert len(interpret_requests) == 1
        assert len(interpret_requests[0]["reference_date"]) == 10 and "-" in interpret_requests[0]["reference_date"]
        assert "practitioner_id:prac-1" in interpret_requests[0]["instruction"]
        assert len(supervised_requests) == 1
        assert len(confirm_payloads) == 0

        assert diary_page.locator("[data-testid='bernie-interpret-status']").text_content().strip() == "Understood"
        assert "Find a 15 minute follow-up" in diary_page.locator("[data-testid='bernie-interpret-summary']").text_content()
        assert "Date:" in diary_page.locator("[data-testid='bernie-interpret-command']").text_content()
        assert diary_page.locator("[data-testid='bernie-interpret-provider']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-status']").text_content().strip() == "Ready to book"
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").is_disabled() is False
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


@pytest.mark.parametrize(
    "result,expected_status,expected_detail",
    [
        ("clarification_required", "Clarification Required", "Please tell Bernie which practitioner before searching for times."),
        ("blocked", "Needs details", "Autonomous booking language is blocked."),
    ],
)
def test_bernie_interpret_preview_holds_supervised_review_until_safe(diary_page, result, expected_status, expected_detail):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    interpret_requests = []
    supervised_requests = []
    confirm_payloads = []
    mock_interpret = {
        "intent": "interpret_booking_instruction",
        "safe": False,
        "result": result,
        "autonomy_tier": "blocked",
        "summary": "Bernie needs more review before supervised booking.",
        "confidence": 0.2,
        "command_candidate": None,
        "missing_fields": ["practitioner_id"] if result == "clarification_required" else [],
        "safety_flags": ["autonomous_booking_language"] if result == "blocked" else [],
        "clarifying_question": expected_detail if result == "clarification_required" else None,
        "normalization": None,
        "warnings": [],
        "blocks": [
            {
                "code": "booking_interpreter_blocked" if result == "blocked" else "missing_practitioner_id",
                "severity": "blocked",
                "message": expected_detail
            }
        ],
        "provider_metadata": {
            "provider": "fake",
            "mode": "mocked",
            "live_provider": False
        }
    }

    def handle_interpret(route):
        interpret_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))

    def handle_supervised(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected supervised call"}))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected confirm call"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction", handle_interpret)
    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_interpret=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, register_default_mock=False)

        diary_page.wait_for_selector("[data-testid='bernie-interpret-preview']", state="visible", timeout=5000)

        assert len(interpret_requests) == 1
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0
        assert diary_page.locator("[data-testid='bernie-interpret-status']").text_content().strip() == expected_status
        assert diary_page.locator("[data-testid='bernie-interpret-issue']", has_text=expected_detail).count() == 1
        assert diary_page.locator("[data-testid='bernie-interpret-hold']").is_visible()
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_interpret_request_requires_explicit_gate(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    interpret_requests = []
    supervised_requests = []
    mock_review = {
        "intent": "bernie_supervised_booking",
        "result": "blocked",
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Blocked review payload",
        "normalization": None,
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Blocked",
            "status": "blocked",
            "staff_action_required": "Review blocked issues.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Blocked.",
            "evidence_summary": "Existing review path still works without interpretation.",
            "warnings": [],
            "blocks": [
                { "code": "existing_review_gate", "severity": "blocked", "message": "Existing review route." }
            ],
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    def handle_interpret(route):
        interpret_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected interpret call"}))

    def handle_supervised(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_review))

    diary_page.route("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction", handle_interpret)
    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        assert len(interpret_requests) == 0
        assert len(supervised_requests) == 0
        assert diary_page.locator("[data-testid='bernie-instruction-input']").is_visible()
        assert diary_page.locator("[data-testid='bernie-interpret-preview']").count() == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_confirm_submit_adapter_success(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    payload_received = []

    def handle_confirm(route):
        try:
            req = route.request
            print(f"ROUTE INTERCEPT: method={req.method}, url={req.url}", file=sys.stderr)
            assert req.method == "POST"
            assert "/api/v1/api/v1/" not in req.url
            post_data = req.post_data or "{}"
            print(f"ROUTE INTERCEPT: post_data={post_data}", file=sys.stderr)
            payload_received.append(json.loads(post_data))
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))
        except Exception as e:
            print(f"ROUTE INTERCEPT EXCEPTION: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            route.abort()

    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        # Load with bernie_confirm_adapter=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert success_msg.is_hidden()
        assert error_msg.is_hidden()

        # No submit before approval
        assert len(payload_received) == 0

        # Click confirm
        confirm_btn.click()

        # UI state after click
        assert_bernie_confirmed_state(diary_page)
        assert error_msg.is_hidden()

        # Verify POST payload
        assert len(payload_received) == 1
        assert payload_received[0]["confirmed"] is True
        assert payload_received[0]["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_confirm_submit_adapter_error_and_retry(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    request_count = 0

    def handle_confirm(route):
        nonlocal request_count
        request_count += 1
        if request_count == 1:
            # First attempt fails with 500
            route.fulfill(
                status=500,
                content_type="application/json",
                body=json.dumps({"detail": "Database connection lost"})
            )
        else:
            # Second attempt succeeds
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))

    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        # Load with bernie_confirm_adapter=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        confirm_btn.click()

         # First attempt (fails)
        error_msg.wait_for(state="visible", timeout=5000)
        assert error_msg.is_visible()
        assert "We couldn't confirm this booking. Please try again or select another time." in error_msg.text_content()
        assert success_msg.is_hidden()

        # Button re-enabled for retry
        assert confirm_btn.is_disabled() is False

        # Retry
        confirm_btn.click()

        # Second attempt (succeeds)
        assert_bernie_confirmed_state(diary_page)
        assert error_msg.is_hidden()
        assert request_count == 2
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_confirm_submit_adapter_disabled_for_non_confirmable_states(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        # Blocked state with bernie_confirm_adapter=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=blocked&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0

        # Candidate selection state with bernie_confirm_adapter=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=candidate_selection_required&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def _bernie_live_confirmation_response():
    return {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "summary": "Confirmation ready.",
        "turn_ref": {
            "session_id": "session-smoke-105",
            "turn_id": "turn-smoke-105-preview",
            "turn_index": 2,
            "reference_date": "2026-06-27",
            "state": "proposal_preview",
        },
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "end_time_local": "09:15:00",
                "practitioner_name": "Dr Alex Shera",
                "room_name": "Room 1"
            },
            "candidate_slots": [],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence for explicit staff approval.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False,
                "selection_proposal": {
                    "intent": "select_slot_for_create_proposal",
                    "selected_candidate_index": 0,
                    "proposal_freshness_id": "proposal-freshness-smoke-105",
                    "selected_candidate": {
                        "appointment_date": "2026-06-27",
                        "start_time_local": "09:00:00",
                        "end_time_local": "09:15:00",
                        "duration_minutes": 15,
                        "practitioner_id": "prac-1",
                        "location_id": "loc-main",
                        "candidate_freshness_id": "candidate-freshness-smoke-105"
                    }
                },
                "create_proposal": {
                    "intent": "create_appointment",
                    "patient_id": "smoke-pat-1",
                    "practitioner_id": "prac-1",
                    "appointment_date": "2026-06-27",
                    "start_time": "09:00:00",
                    "duration_minutes": 15,
                    "reason": "Follow-up"
                }
            },
            "confirm_evidence": [
                "bernie_confirm_create_proposal",
                "source_slot_selection_proposal",
                "source_create_proposal"
            ],
            "blocks": []
        }
    }


def _bernie_live_blocked_response():
    return {
        "intent": "bernie_supervised_booking",
        "result": "blocked",
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Practitioner ID is required.",
        "staff_review": {
            "headline": "Practitioner ID is required.",
            "status": "blocked",
            "staff_action_required": "Review blocked issues before retrying; no booking can be confirmed from this payload.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Blocked issues require staff correction.",
            "evidence_summary": "No confirmation evidence was produced.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": [],
            "blocks": [
                {"code": "missing_practitioner_id", "message": "Practitioner ID is required."}
            ]
        }
    }


def _bernie_live_candidate_response():
    return {
        "intent": "bernie_supervised_booking",
        "result": "candidate_selection_required",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "Candidate selection required.",
        "staff_review": {
            "headline": "Candidate selection required.",
            "status": "candidate_selection_required",
            "staff_action_required": "Select one candidate slot before preparing confirmation evidence.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [
                {
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00:00",
                    "end_time_local": "09:15:00",
                    "practitioner_name": "Dr Alex Shera",
                    "room_name": "Room 1"
                }
            ],
            "warning_summary": "Select a candidate before confirming.",
            "evidence_summary": "Candidate selection is required.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": [],
            "blocks": []
        }
    }


def _bernie_ui_node(value, source="derived"):
    return {"value": value, "source": source}


def _bernie_ui_view_model(
    *,
    candidate_state="absent",
    proposal_state="absent",
    confirmation_state="not_applicable",
    freshness_state="fresh",
    identity_state="recognized",
    clarification_state="none",
    copy_mode="technical_details_only",
    primary_copy="Review the booking details. No appointment has been made.",
    secondary_copy=None,
    flags=None,
):
    default_flags = {
        "show_clarification_prompt": False,
        "show_candidate_slots": False,
        "show_no_slot_suggestions": False,
        "show_pending_proposal_card": False,
        "show_confirm_button": False,
        "enable_confirm_button": False,
        "show_choose_another_time": False,
        "show_identity_verification_panel": False,
        "show_success_copy": False,
        "show_stale_warning": False,
        "show_retry_action": False,
        "show_edit_action": False,
        "show_technical_details": False,
    }
    if flags:
        default_flags.update(flags)
    return {
        "schema_version": "bernie.ui_view_model.v1",
        "session_phase": _bernie_ui_node("proposal_preview", "server_snapshot"),
        "clarification_state": _bernie_ui_node(clarification_state),
        "candidate_state": _bernie_ui_node(candidate_state),
        "proposal_state": _bernie_ui_node(proposal_state),
        "confirmation_state": _bernie_ui_node(confirmation_state),
        "freshness_state": _bernie_ui_node(freshness_state),
        "identity_state": _bernie_ui_node(identity_state),
        "copy_mode": _bernie_ui_node(copy_mode),
        "flags": default_flags,
        "primary_copy": primary_copy,
        "secondary_copy": secondary_copy,
    }


def _bernie_session_snapshot(session_id="server-session-n6", revision=0, state="instruction_entry", stale_reason_code=None):
    return {
        "session_id": session_id,
        "surface_id": "diary-main",
        "state": state,
        "request_reference_date": "2026-07-03",
        "revision": revision,
        "last_event_id": None,
        "stale_reason_code": stale_reason_code,
        "events": []
    }


def test_bernie_session_endpoint_active_load_and_phi_minimized_append(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    active_requests = []
    append_requests = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/sessions/active" in url:
            active_requests.append(url)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"session": _bernie_session_snapshot()})
            )
            return
        if "/api/v1/appointments/bernie/sessions/" in url and "/events" in url:
            body = json.loads(route.request.post_data or "{}")
            append_requests.append(body)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "accepted": True,
                    "session": _bernie_session_snapshot(revision=1, state="recognition"),
                    "event": {
                        "event_id": body.get("event_id"),
                        "event_type": body.get("event_type"),
                        "payload": body.get("payload", {})
                    }
                })
            )
            return
        if "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "interpret_booking_instruction",
                    "safe": True,
                    "result": "interpreted",
                    "autonomy_tier": "execute_with_report",
                    "summary": "Find a routine appointment tomorrow.",
                    "confidence": 0.9,
                    "command_candidate": {
                        "practitioner_id": "prac-1",
                        "patient_id": "smoke-pat-1",
                        "date_from": "2026-06-28",
                        "duration_minutes": 15
                    },
                    "missing_fields": [],
                    "safety_flags": [],
                    "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False}
                })
            )
            return
        if "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(_bernie_live_blocked_response()))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"eligible": True}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_session=true&practitioner_id=prac-1&patient_id=smoke-pat-1")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        assert active_requests

        raw_instruction = "Make an appointment for Margaret Thompson with Dr Shera after 3 tomorrow"
        diary_page.fill("[data-testid='bernie-instruction-input']", raw_instruction)
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        for _ in range(30):
            if append_requests:
                break
            diary_page.wait_for_timeout(100)
        assert append_requests

        body = append_requests[0]
        assert body["surface_id"] == "diary-main"
        assert body["event_type"] == "staff_instruction"
        assert body["expected_revision"] == 0
        assert body["idempotency_key"]
        assert body["payload"]["source"] == "diary_bernie_panel"
        assert body["payload"]["has_staff_text"] is True
        serialized_body = json.dumps(body)
        assert "Margaret" not in serialized_body
        assert "Thompson" not in serialized_body
        assert "Dr Shera" not in serialized_body
        assert "raw_instruction" not in serialized_body
        assert "instruction" not in body["payload"]

        storage_values = diary_page.evaluate(
            """() => {
                const values = [];
                for (let i = 0; i < localStorage.length; i += 1) values.push(localStorage.getItem(localStorage.key(i)));
                for (let i = 0; i < sessionStorage.length; i += 1) values.push(sessionStorage.getItem(sessionStorage.key(i)));
                return values.join("\\n");
            }"""
        )
        assert "Margaret Thompson" not in storage_values
        assert raw_instruction not in storage_values
        assert "server-session-n6" not in storage_values
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_session_stale_conflict_disables_confirm_until_refresh(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    confirm_payloads = []
    append_requests = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/sessions/active" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"session": _bernie_session_snapshot()})
            )
            return
        if "/api/v1/appointments/bernie/sessions/" in url and "/events" in url:
            append_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(
                status=409,
                content_type="application/json",
                body=json.dumps({
                    "accepted": False,
                    "code": "stale_session_revision",
                    "detail": "Expected revision 0 but current revision is 1.",
                    "session": _bernie_session_snapshot(revision=1, state="proposal_preview")
                })
            )
            return
        if "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "interpret_booking_instruction",
                    "safe": True,
                    "result": "interpreted",
                    "autonomy_tier": "execute_with_report",
                    "summary": "Find a routine appointment tomorrow.",
                    "confidence": 0.9,
                    "command_candidate": {
                        "practitioner_id": "prac-1",
                        "patient_id": "smoke-pat-1",
                        "date_from": "2026-06-28",
                        "duration_minutes": 15
                    },
                    "missing_fields": [],
                    "safety_flags": [],
                    "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False}
                })
            )
            return
        if "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(_bernie_live_confirmation_response()))
            return
        if "/api/v1/appointments/proposals/create/confirm-bernie" in url:
            confirm_payloads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "unexpected"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"eligible": True}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_session=true&bernie_confirm_adapter=true&practitioner_id=prac-1&patient_id=smoke-pat-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        diary_page.fill("[data-testid='bernie-instruction-input']", "Make an appointment tomorrow after 3")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        for _ in range(30):
            if append_requests:
                break
            diary_page.wait_for_timeout(100)
        assert append_requests

        diary_page.wait_for_selector("[data-testid='bernie-session-stale-banner']", state="visible", timeout=5000)
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        confirm_btn.wait_for(state="visible", timeout=5000)
        assert confirm_btn.is_disabled()
        confirm_btn.click(force=True)
        assert len(confirm_payloads) == 0
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_route_calls_carry_server_session_coordinates_and_binding(diary_page):
    import copy
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    append_requests = []
    interpret_requests = []
    supervised_requests = []
    confirm_payloads = []
    binding = {
        "practice_id": "practice-smoke",
        "staff_user_id": "staff-smoke",
        "surface_id": "diary-main",
        "session_id": "server-session-n9",
        "session_revision": 5,
        "reference_date": "2026-07-03",
        "patient_id": "smoke-pat-1",
        "practitioner_id": "prac-1",
        "candidate_freshness_id": "candidate-freshness-smoke-105",
        "proposal_freshness_id": "proposal-freshness-smoke-105",
        "appointment_date": "2026-06-27",
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/sessions/active" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"session": _bernie_session_snapshot(session_id="server-session-n9")})
            )
            return
        if "/api/v1/appointments/bernie/sessions/" in url and "/events" in url:
            body = json.loads(route.request.post_data or "{}")
            append_requests.append(body)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "accepted": True,
                    "session": _bernie_session_snapshot(session_id="server-session-n9", revision=1, state="recognition"),
                    "event": {"event_id": body.get("event_id"), "event_type": body.get("event_type"), "payload": body.get("payload", {})}
                })
            )
            return
        if "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            body = json.loads(route.request.post_data or "{}")
            interpret_requests.append(body)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "interpret_booking_instruction",
                    "safe": True,
                    "result": "interpreted",
                    "autonomy_tier": "execute_with_report",
                    "summary": "Find a routine appointment tomorrow.",
                    "confidence": 0.9,
                    "command_candidate": {
                        "practitioner_id": "prac-1",
                        "patient_id": "smoke-pat-1",
                        "date_from": "2026-07-04",
                        "duration_minutes": 15
                    },
                    "missing_fields": [],
                    "safety_flags": [],
                    "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False},
                    "turn_ref": {
                        "session_id": "turn-session-n9",
                        "turn_id": "turn-session-n9:1",
                        "turn_index": 1,
                        "event_kind": "staff_instruction",
                        "reference_date": body.get("reference_date"),
                    },
                    "server_session": _bernie_session_snapshot(session_id="server-session-n9", revision=2, state="context_enrichment")
                })
            )
            return
        if "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            body = json.loads(route.request.post_data or "{}")
            supervised_requests.append(body)
            response = copy.deepcopy(_bernie_live_confirmation_response())
            response["server_session"] = _bernie_session_snapshot(session_id="server-session-n9", revision=5, state="proposal_preview")
            response["staff_review"]["confirm_payload"]["session_binding"] = binding
            response["staff_review"]["confirm_payload"]["signed_confirmation_evidence"] = {
                "payload": {"session_binding": binding}
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(response))
            return
        if "/api/v1/appointments/proposals/create/confirm-bernie" in url:
            confirm_payloads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "confirmed"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"eligible": True}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_session=true&bernie_confirm_adapter=true&practitioner_id=prac-1&patient_id=smoke-pat-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        diary_page.fill("[data-testid='bernie-instruction-input']", "Make an appointment tomorrow after 3")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")

        for _ in range(50):
            if interpret_requests and supervised_requests:
                break
            diary_page.wait_for_timeout(100)

        assert append_requests, "expected staff instruction append"
        assert interpret_requests, "expected interpret request"
        assert supervised_requests, "expected supervised booking request"

        interpret_body = interpret_requests[0]
        assert interpret_body["server_session_id"] == "server-session-n9"
        assert interpret_body["server_session_surface_id"] == "diary-main"
        assert interpret_body["server_session_expected_revision"] == 1
        assert interpret_body["server_session_idempotency_key"]

        supervised_body = supervised_requests[0]
        assert supervised_body["server_session_id"] == "server-session-n9"
        assert supervised_body["server_session_surface_id"] == "diary-main"
        assert supervised_body["server_session_expected_revision"] == 2
        assert supervised_body["server_session_idempotency_key"]
        assert supervised_body["server_session_idempotency_key"] != interpret_body["server_session_idempotency_key"]

        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)
        diary_page.click("[data-testid='bernie-review-confirm-button']")
        for _ in range(30):
            if confirm_payloads:
                break
            diary_page.wait_for_timeout(100)

        assert confirm_payloads, "expected confirm payload"
        assert confirm_payloads[0]["session_binding"] == binding
        assert confirm_payloads[0]["confirmed"] is True
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_route_intercepted_confirm_flow_harness_success(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    supervised_requests = []
    confirm_payloads = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(_bernie_live_confirmation_response())
        )

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data))
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        confirm_btn.wait_for(state="visible", timeout=5000)
        assert len(supervised_requests) == 1
        assert supervised_requests[0]["selected_candidate_index"] == 0

        assert confirm_btn.is_disabled() is False
        assert success_msg.is_hidden()
        assert error_msg.is_hidden()
        assert len(confirm_payloads) == 0

        confirm_btn.click()

        # Wait for success message
        assert_bernie_confirmed_state(diary_page)

        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True
        assert confirm_payloads[0]["turn_ref"]["turn_id"] == "turn-smoke-105-preview"
        assert confirm_payloads[0]["candidate_freshness_id"] == "candidate-freshness-smoke-105"
        assert confirm_payloads[0]["proposal_freshness_id"] == "proposal-freshness-smoke-105"
        assert confirm_payloads[0]["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
        assert confirm_payloads[0]["create_proposal"]["reason"] == "Follow-up"
        assert error_msg.is_hidden()
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_ui_view_model_proposal_ready_drives_display_without_payload_leak(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    response = _bernie_live_confirmation_response()
    response["evidence_label"] = "route_intercepted"
    response["staff_review"]["headline"] = "Legacy status disagrees with UI view model"
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="ready",
        confirmation_state="ready",
        copy_mode="not_booked_yet",
        primary_copy="Review the booking details before confirming. No appointment has been made.",
        flags={
            "show_pending_proposal_card": True,
            "show_confirm_button": True,
            "enable_confirm_button": True,
            "show_choose_another_time": True,
        },
    )

    confirm_payloads = []

    def handle_supervised_booking(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data))
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)
        diary_page.locator("[data-testid='bernie-review-status']").wait_for(state="visible", timeout=5000)

        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 1
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        confirm_btn.wait_for(state="visible", timeout=5000)
        assert confirm_btn.is_enabled()
        assert "No appointment has been made" in diary_page.locator("[data-testid='bernie-review-action']").text_content()

        confirm_btn.click()
        assert_bernie_confirmed_state(diary_page)

        assert len(confirm_payloads) == 1
        serialized_payload = json.dumps(confirm_payloads[0])
        forbidden_view_model_fields = [
            "copy_mode",
            "confirmation_state",
            "freshness_state",
            "flags",
            "primary_copy",
            "secondary_copy",
            "show_confirm_button",
            "show_success_copy",
        ]
        for field in forbidden_view_model_fields:
            assert field not in serialized_payload
        assert confirm_payloads[0]["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
        assert confirm_payloads[0]["create_proposal"]["reason"] == "Follow-up"
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_ui_view_model_candidate_slots_win_over_legacy_blocked_status(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    response = _bernie_live_candidate_response()
    response["evidence_label"] = "route_intercepted"
    response["staff_review"]["status"] = "blocked"
    response["staff_review"]["blocks"] = []
    response["ui_view_model"] = _bernie_ui_view_model(
        candidate_state="available",
        copy_mode="offer",
        primary_copy="Choose an available time. No appointment has been made.",
        flags={"show_candidate_slots": True},
    )

    confirm_payloads = []

    def handle_supervised_booking(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)
        diary_page.locator("[data-testid='bernie-review-status']").wait_for(state="visible", timeout=5000)

        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-candidate-item']").text_content()
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


@pytest.mark.parametrize(
    ("confirmation_state", "expected_marker"),
    [
        ("pressed", None),
        ("awaiting_backend", None),
        ("stale", "bernie-stale-warning"),
        ("failed", "bernie-retry-button"),
    ],
)
def test_bernie_ui_view_model_non_ready_states_do_not_show_confirm_or_success(diary_page, confirmation_state, expected_marker):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    response = _bernie_live_confirmation_response()
    response["evidence_label"] = "route_intercepted"
    flags = {
        "show_retry_action": confirmation_state in {"stale", "failed"},
        "show_edit_action": confirmation_state in {"stale", "failed"},
        "show_stale_warning": confirmation_state == "stale",
    }
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="ready",
        confirmation_state=confirmation_state,
        freshness_state="stale" if confirmation_state == "stale" else "fresh",
        copy_mode="stale_or_retry" if confirmation_state in {"stale", "failed"} else "not_booked_yet",
        primary_copy="Review the booking details. No appointment has been made.",
        secondary_copy="Refresh this proposal before confirming.",
        flags=flags,
    )

    confirm_payloads = []

    def handle_supervised_booking(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)
        diary_page.locator("[data-testid='bernie-review-status']").wait_for(state="visible", timeout=5000)

        action_text = diary_page.locator("[data-testid='bernie-review-action']").text_content().lower()
        assert "booked" not in action_text
        assert "confirmed" not in action_text
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        if expected_marker:
            assert diary_page.locator(f"[data-testid='{expected_marker}']").is_visible()
            assert diary_page.locator("[data-testid='bernie-edit-button']").is_visible()
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


@pytest.mark.parametrize(
    ("review_response", "expected_status"),
    [
        (_bernie_live_blocked_response, "Needs details"),
        (_bernie_live_candidate_response, "Choose a time"),
    ],
)
def test_bernie_route_intercepted_confirm_flow_harness_non_confirmable_states(diary_page, review_response, expected_status):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    supervised_requests = []
    confirm_payloads = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(review_response()))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        assert len(supervised_requests) == 1
        assert status_locator.text_content().strip() == expected_status
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_route_intercepted_confirm_flow_harness_supervised_booking_error_no_write(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    supervised_requests = []
    confirm_payloads = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "backend unavailable"}))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        assert len(supervised_requests) == 1
        assert status_locator.text_content().strip() == "Needs details"
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="HTTP status 500").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_route_intercepted_confirm_flow_harness_no_normal_mode_exposure(diary_page):
    import urllib.parse
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    supervised_requests = []
    confirm_payloads = []

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: (
            supervised_requests.append(json.loads(route.request.post_data)),
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected supervised call"}))
        )
    )
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: (
            confirm_payloads.append(json.loads(route.request.post_data)),
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected confirm call"}))
        )
    )

    try:
        # Case 1: Pure ordinary mode (no query parameters)
        diary_page.goto(base_url + "/diary/diary.html?practitioner_id=real-prac-query&patient_id=real-patient-query")
        diary_page.wait_for_load_state("domcontentloaded")
        assert diary_page.locator("[data-testid='bernie-review-panel']:not(.hidden)").count() == 0
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0

        # Case 2: bernie_review=live alone (no dev flag) in ordinary mode
        diary_page.goto(base_url + "/diary/diary.html?bernie_review=live&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_load_state("domcontentloaded")
        assert diary_page.locator("[data-testid='bernie-review-panel']:not(.hidden)").count() == 0
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0

        # Case 3: smoke=true & bernie_review=live (no dev flag) in smoke mode
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_load_state("domcontentloaded")
        assert diary_page.locator("[data-testid='bernie-review-panel']:not(.hidden)").count() == 0
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_dev_mode_review_feature_flag_success(diary_page):
    import urllib.parse
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    supervised_requests = []
    confirm_payloads = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(_bernie_live_confirmation_response())
        )

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data))
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        # Load with bernie_review=live & bernie_dev_review=true (non-smoke mode)
        diary_page.goto(base_url + "/diary/diary.html?bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1&selected_candidate_index=0")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        confirm_btn.wait_for(state="visible", timeout=5000)
        assert len(supervised_requests) == 1
        assert supervised_requests[0]["selected_candidate_index"] == 0

        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert success_msg.is_hidden()
        assert error_msg.is_hidden()
        assert len(confirm_payloads) == 0

        # Verify explicit staff confirmation is the only write trigger.
        assert len(confirm_payloads) == 0

        confirm_btn.click()

        # Wait for success message
        assert_bernie_confirmed_state(diary_page)

        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True
        assert confirm_payloads[0]["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
        assert error_msg.is_hidden()
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_dev_review_launcher_and_gating(diary_page):
    import urllib.parse
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    dev_fixtures_requests = []
    confirm_requests = []
    confirm_payloads = []

    def handle_dev_fixtures(route):
        dev_fixtures_requests.append(route.request.url)
        parsed_url = urllib.parse.urlparse(route.request.url)
        params = urllib.parse.parse_qs(parsed_url.query)
        state = params.get("state", [None])[0]
        fixtures = {
            "blocked": _bernie_live_blocked_response(),
            "candidate_selection_required": _bernie_live_candidate_response(),
            "confirmation_ready": _bernie_live_confirmation_response()
        }
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({state: fixtures[state]})
        )

    diary_page.route("**/api/v1/appointments/dev/bernie-review-fixtures*", handle_dev_fixtures)
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: (
            confirm_requests.append(route.request.url),
            confirm_payloads.append(json.loads(route.request.post_data)),
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_load_state("domcontentloaded")
        tools = diary_page.locator("[data-testid='bernie-review-dev-tools']")
        selector = diary_page.locator("[data-testid='bernie-review-dev-state-select']")
        help_panel = diary_page.locator("[data-testid='bernie-review-dev-state-help']")
        assert tools.is_hidden()
        assert selector.is_hidden()
        assert help_panel.is_hidden()
        assert len(dev_fixtures_requests) == 0
        assert len(confirm_payloads) == 0

        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&smoke=true&bernie_confirm_adapter=true&practitioner_id=prac-1&selected_candidate_index=0")
        diary_page.wait_for_load_state("domcontentloaded")
        assert tools.is_visible()
        assert selector.is_visible()
        assert help_panel.is_visible()
        assert help_panel.text_content().count("blocked") >= 1
        assert "candidate_selection_required" in help_panel.text_content()
        assert "confirmation_ready" in help_panel.text_content()
        assert selector.locator("option").evaluate_all("(options) => options.map((option) => option.value)") == [
            "blocked",
            "candidate_selection_required",
            "confirmation_ready"
        ]
        assert len(dev_fixtures_requests) == 0
        assert len(confirm_payloads) == 0
        help_panel.locator("summary").click()
        assert help_panel.locator("dd", has_text="Bernie cannot safely propose or continue yet.").is_visible()
        assert help_panel.locator("dd", has_text="Staff must choose one candidate slot before review can continue.").is_visible()
        assert help_panel.locator("dd", has_text="explicit confirm-Bernie approval").is_visible()
        assert len(dev_fixtures_requests) == 0
        assert len(confirm_payloads) == 0

        selector.select_option("candidate_selection_required")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        current_params = urllib.parse.parse_qs(urllib.parse.urlparse(diary_page.url).query)
        assert current_params["bernie_dev_review"] == ["true"]
        assert current_params["bernie_review"] == ["candidate_selection_required"]
        assert current_params["smoke"] == ["true"]
        assert current_params["bernie_confirm_adapter"] == ["true"]
        assert current_params["practitioner_id"] == ["prac-1"]
        assert current_params["selected_candidate_index"] == ["0"]
        assert len(dev_fixtures_requests) == 1
        assert "state=candidate_selection_required" in dev_fixtures_requests[-1]
        assert len(confirm_payloads) == 0

        selector = diary_page.locator("[data-testid='bernie-review-dev-state-select']")
        assert selector.is_visible()
        selector.select_option("confirmation_ready")
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 2
        assert "state=confirmation_ready" in dev_fixtures_requests[-1]
        assert len(confirm_payloads) == 0

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert len(confirm_payloads) == 0
        confirm_btn.click()
        assert_bernie_confirmed_state(diary_page)
        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True
        assert "/api/v1/api/v1/" not in confirm_requests[-1]

    finally:
        diary_page.unroute("**/api/v1/appointments/dev/bernie-review-fixtures*")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_dev_review_fixture_route(diary_page):
    import urllib.parse
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    dev_fixtures_requests = []
    confirm_payloads = []

    def handle_dev_fixtures(route):
        url = route.request.url
        dev_fixtures_requests.append(url)
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        state = params.get("state", [None])[0]

        fixtures = {
            "blocked": _bernie_live_blocked_response(),
            "candidate_selection_required": _bernie_live_candidate_response(),
            "confirmation_ready": _bernie_live_confirmation_response()
        }

        if state in fixtures:
            body_dict = {state: fixtures[state]}
        else:
            body_dict = fixtures

        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(body_dict)
        )

    diary_page.route("**/api/v1/appointments/dev/bernie-review-fixtures*", handle_dev_fixtures)

    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: (
            confirm_payloads.append(json.loads(route.request.post_data)),
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))
        )
    )

    try:
        # 1. Proves default mode makes no calls
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_load_state("domcontentloaded")
        assert len(dev_fixtures_requests) == 0

        # 2. Proves dev flag without bernie_review makes no calls
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true")
        diary_page.wait_for_load_state("domcontentloaded")
        assert len(dev_fixtures_requests) == 0

        # 3. Proves offline smoke without dev flag makes no calls
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=blocked")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 0
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Needs details"

        # 4. Proves dev-review fixture failures are visible and do not silently fall back to mocks
        diary_page.unroute("**/api/v1/appointments/dev/bernie-review-fixtures*")
        diary_page.route(
            "**/api/v1/appointments/dev/bernie-review-fixtures*",
            lambda route: route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "fixture unavailable"}))
        )
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&bernie_review=blocked")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="Dev Fixture Unavailable").count() == 1
        diary_page.unroute("**/api/v1/appointments/dev/bernie-review-fixtures*")
        diary_page.route("**/api/v1/appointments/dev/bernie-review-fixtures*", handle_dev_fixtures)

        # 5. Proves dev-review = blocked fetches and renders
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&bernie_review=blocked")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 1
        assert "state=blocked" in dev_fixtures_requests[-1]

        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Add the missing details"
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="Missing Practitioner Id").count() == 1

        # 6. Proves dev-review = candidate_selection_required fetches and renders
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&bernie_review=candidate_selection_required")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 2
        assert "state=candidate_selection_required" in dev_fixtures_requests[-1]

        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Choose a time"

        # 7. Proves dev-review = confirmation_ready fetches, renders and can confirm (route-intercepted)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_dev_review=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 3
        assert "state=confirmation_ready" in dev_fixtures_requests[-1]

        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "Ready to book"

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert len(confirm_payloads) == 0
        confirm_btn.click()
        assert_bernie_confirmed_state(diary_page)
        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True

    finally:
        diary_page.unroute("**/api/v1/appointments/dev/bernie-review-fixtures*")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_eligibility_default_off(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": False,
        "eligible": False,
        "reason": "pilot_disabled",
        "practice_allowed": False,
        "user_allowed": False
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        launch_btn = diary_page.locator("[data-testid='bernie-pilot-launch-button']")
        assert launch_btn.count() == 1
        assert "hidden" in launch_btn.get_attribute("class")

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_eligibility_eligible(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_live_review = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "supervised",
        "summary": "Proposal confirmation ready",
        "normalization": {
            "safe": True,
            "constraint": { "practitioner_id": "prac-1" },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully"
        },
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": {
                "id": "slot-1",
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Verification details look correct.",
            "warnings": [],
            "blocks": [],
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": { "proposal_id": "prop-123" },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    supervised_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_live_review)
        )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        handle_supervised_booking
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        launch_btn = diary_page.locator("[data-testid='bernie-pilot-launch-button']")
        assert launch_btn.count() == 1
        assert "hidden" not in launch_btn.get_attribute("class")

        panel = diary_page.locator("[data-testid='bernie-review-panel']")
        assert "hidden" in panel.get_attribute("class")

        launch_btn.click()
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        banner = diary_page.locator("[data-testid='bernie-pilot-banner']")
        banner.wait_for(state="visible", timeout=5000)

        assert len(supervised_requests) == 1
        assert supervised_requests[0]["command"]["practitioner_id"] == "prac-1"
        assert supervised_requests[0]["reference_date"] == "2026-06-27"

        banner = diary_page.locator("[data-testid='bernie-pilot-banner']")
        assert banner.is_visible()
        assert "Review the details before confirming." in banner.text_content()

        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert "Would you like to confirm?" in headline.text_content()

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_ordinary_mode_requires_real_context(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }
    supervised_requests = []
    confirm_payloads = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            supervised_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected supervised call"}))
        elif "/api/v1/appointments/proposals/create/confirm-bernie" in url:
            confirm_payloads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected confirm call"}))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-70",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {
                    "id": "staff-visible-appt-70",
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00",
                    "start_time": "09:00",
                    "duration_minutes": 15,
                    "status": "Booked",
                    "appointment_type_id": None,
                    "patient_id": "real-patient-70",
                    "patient": {
                        "id": "real-patient-70",
                        "first_name": "Margaret",
                        "last_name": "Thompson",
                        "date_of_birth": "1955-03-24"
                    },
                    "practitioner_id": "real-prac-70",
                    "practitioner": {
                        "id": "real-prac-70",
                        "first_name": "Alex",
                        "last_name": "Shera",
                        "ahpra_number": "MED0001234567"
                    },
                    "room_id": None,
                    "location_id": "loc-1",
                    "notes": ""
                }
            ]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("[data-testid='bernie-pilot-launch-button']:not(.hidden)", state="visible", timeout=5000)

        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-pilot-context-form']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-context-warning']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-practitioner-id']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-patient-id']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-context-submit']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-status']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-block-item']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_ordinary_mode_explicit_context_posts_and_confirm_gated(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_live_review = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "supervised",
        "summary": "Proposal confirmation ready",
        "normalization": {
            "safe": True,
            "constraint": { "practitioner_id": "real-prac-70" },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully"
        },
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": {
                "id": "slot-70",
                "appointment_date": "2026-06-27",
                "start_time_local": "10:15:00",
                "duration_minutes": 15
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Selected appointment context accepted.",
            "warnings": [],
            "blocks": [],
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": { "proposal_id": "prop-70" },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    supervised_requests = []
    confirm_payloads = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "safe": True,
                    "result": "interpreted",
                    "command_candidate": {
                        "practitioner_id": "real-prac-70",
                        "patient_id": "real-patient-70"
                    }
                })
            )
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            supervised_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_live_review))
        elif "/api/v1/appointments/proposals/create/confirm-bernie" in url:
            confirm_payloads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-70",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {
                    "id": "staff-visible-appt-70",
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00",
                    "start_time": "09:00",
                    "duration_minutes": 15,
                    "status": "Booked",
                    "appointment_type_id": None,
                    "patient_id": "real-patient-70",
                    "patient": {
                        "id": "real-patient-70",
                        "first_name": "Margaret",
                        "last_name": "Thompson",
                        "date_of_birth": "1955-03-24"
                    },
                    "practitioner_id": "real-prac-70",
                    "practitioner": {
                        "id": "real-prac-70",
                        "first_name": "Alex",
                        "last_name": "Shera",
                        "ahpra_number": "MED0001234567"
                    },
                    "room_id": None,
                    "location_id": "loc-1",
                    "notes": ""
                }
            ]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("[data-testid='bernie-pilot-launch-button']:not(.hidden)", state="visible", timeout=5000)
        diary_page.wait_for_selector(".appt:has-text('Margaret Thompson')", state="visible", timeout=5000)

        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson')", state="visible", timeout=5000)
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-pilot-practitioner-id']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-patient-id']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-context-submit']").count() == 0
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']", state="visible", timeout=5000)
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0

        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)
        details = diary_page.locator("[data-testid='bernie-context-summary-details']")
        assert "Patient: Margaret Thompson" in details.text_content()
        assert "Practitioner: Alex Shera" in details.text_content()

        # Trigger staff instruction submit
        trigger_route_intercepted_bernie(diary_page, register_default_mock=False)

        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)

        assert len(supervised_requests) == 1
        assert supervised_requests[0]["command"]["practitioner_id"] == "real-prac-70"
        assert supervised_requests[0]["command"]["patient_id"] == "real-patient-70"
        assert supervised_requests[0]["reference_date"]
        assert len(confirm_payloads) == 0

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert len(confirm_payloads) == 0

        confirm_btn.click()
        assert_bernie_confirmed_state(diary_page)
        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["proposal_id"] == "prop-70"
        assert confirm_payloads[0]["confirmed"] is True
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_imported_context_stales_when_selection_changes(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    supervised_requests = []
    appointments = [
        {
            "id": "appt-margaret-72",
            "appointment_date": "2026-06-27",
            "start_time_local": "09:00",
            "start_time": "09:00",
            "duration_minutes": 15,
            "status": "Booked",
            "appointment_type_id": None,
            "patient_id": "patient-margaret-72",
            "patient": {"id": "patient-margaret-72", "first_name": "Margaret", "last_name": "Thompson"},
            "practitioner_id": "prac-72",
            "practitioner": {"id": "prac-72", "first_name": "Alex", "last_name": "Shera", "ahpra_number": "MED0001234567"},
            "room_id": None,
            "location_id": "loc-1",
            "notes": ""
        },
        {
            "id": "appt-samuel-72",
            "appointment_date": "2026-06-27",
            "start_time_local": "09:30",
            "start_time": "09:30",
            "duration_minutes": 15,
            "status": "Booked",
            "appointment_type_id": None,
            "patient_id": "patient-samuel-72",
            "patient": {"id": "patient-samuel-72", "first_name": "Samuel", "last_name": "Lee"},
            "practitioner_id": "prac-72",
            "practitioner": {"id": "prac-72", "first_name": "Alex", "last_name": "Shera", "ahpra_number": "MED0001234567"},
            "room_id": None,
            "location_id": "loc-1",
            "notes": ""
        }
    ]

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "safe": True,
                    "result": "interpreted",
                    "command_candidate": {
                        "practitioner_id": "prac-72",
                        "patient_id": "patient-samuel-72"
                    }
                })
            )
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            supervised_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "bernie_supervised_booking",
                    "result": "blocked",
                    "safe": False,
                    "requires_confirmation": False,
                    "autonomy_tier": "blocked",
                    "staff_review": {
                        "headline": "Blocked",
                        "status": "blocked",
                        "staff_action_required": "No booking action prepared.",
                        "confirmation_ready": False,
                        "selected_slot": None,
                        "candidate_slots": [],
                        "warning_summary": "Blocked.",
                        "evidence_summary": "Harness response.",
                        "warnings": [],
                        "blocks": [{"code": "harness_block", "message": "Harness block"}],
                        "confirm_payload": None
                    },
                    "warnings": [],
                    "blocks": [{"code": "harness_block", "message": "Harness block"}]
                })
            )
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "prac-72",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointments))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("[data-testid='bernie-pilot-launch-button']:not(.hidden)", state="visible", timeout=5000)
        diary_page.wait_for_selector(".appt:has-text('Margaret Thompson')", state="visible", timeout=5000)

        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']", state="visible", timeout=5000)
        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-suggested-instructions']", state="visible", timeout=5000)

        diary_page.click(".appt:has-text('Samuel Lee')")
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']:has-text('Samuel Lee')", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-block-item']:has-text('stale_selected_appointment_context')").count() == 0
        assert diary_page.locator("[data-testid='bernie-instruction-input']").is_enabled()
        assert diary_page.locator("[data-testid='btn-bernie-instruction-submit']").is_enabled()
        assert len(supervised_requests) == 0

        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary-details']:has-text('Samuel Lee')", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, instruction="Please find an appointment for Samuel", register_default_mock=False)
        diary_page.wait_for_selector("[data-testid='bernie-review-block-item']:has-text('Harness Block')", state="visible", timeout=5000)
        assert len(supervised_requests) == 1
        assert supervised_requests[0]["command"]["patient_id"] == "patient-samuel-72"
        assert supervised_requests[0]["command"]["practitioner_id"] == "prac-72"
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_eligibility_confirm_gated(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_live_review = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "supervised",
        "summary": "Proposal confirmation ready",
        "normalization": {
            "safe": True,
            "constraint": { "practitioner_id": "prac-1" },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully"
        },
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": {
                "id": "slot-1",
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Verification details look correct.",
            "warnings": [],
            "blocks": [],
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": { "proposal_id": "prop-123" },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    confirm_payloads = []

    def handle_confirm(route):
        req = route.request
        confirm_payloads.append(json.loads(req.post_data))
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    supervised_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_live_review)
        )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        handle_supervised_booking
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        handle_confirm
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page)

        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        confirm_btn.wait_for(state="visible", timeout=5000)

        assert len(supervised_requests) == 1
        assert supervised_requests[0]["command"]["practitioner_id"] == "prac-1"
        assert supervised_requests[0]["reference_date"] == "2026-06-27"

        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled() is False
        assert len(confirm_payloads) == 0

        confirm_btn.click()
        assert_bernie_confirmed_state(diary_page)

        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["proposal_id"] == "prop-123"
        assert confirm_payloads[0]["confirmed"] is True

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_selected_appointment_context(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_live_review = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "supervised",
        "summary": "Proposal confirmation ready",
        "normalization": {
            "safe": True,
            "constraint": { "practitioner_id": "smoke-prac-1" },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully"
        },
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": {
                "id": "slot-1",
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Verification details look correct.",
            "warnings": [],
            "blocks": [],
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": { "proposal_id": "prop-123" },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    supervised_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_live_review)
        )

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        handle_supervised_booking
    )

    # Route interpretation request specifically for our test
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "safe": True,
                "result": "interpreted",
                "command_candidate": {
                    "practitioner_id": "smoke-prac-1",
                    "patient_id": "smoke-pat-1",
                    "date_from": "today",
                    "duration_minutes": "15"
                }
            })
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_context_form=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        # Launch Bernie Pilot sidebar
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # 1. No appointment is selected initially, but instruction-first Bernie is usable.
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-pilot-use-selected']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-selected-status-info']").count() == 0

        # 2. Select a linked appointment (Margaret Thompson)
        diary_page.click(".appt:has-text('Margaret Thompson')")
        # Should now show the Use selected button
        use_selected_btn = diary_page.locator("[data-testid='bernie-pilot-use-selected']")
        use_selected_btn.wait_for(state="visible", timeout=5000)
        assert "Margaret Thompson" in use_selected_btn.text_content()

        # 3. Clear the selection
        diary_page.locator(".col-room-label").first.click()
        assert diary_page.locator("[data-testid='bernie-pilot-selected-status-info']").count() == 0

        # 4. Select a provisional appointment (Nora Patel)
        diary_page.click(".appt:has-text('Nora Patel')")
        assert diary_page.locator("[data-testid='bernie-pilot-selected-status-error']").count() == 0

        # 5. Select Margaret Thompson again, and click the Use selected button
        diary_page.click(".appt:has-text('Margaret Thompson')")
        use_selected_btn.wait_for(state="visible", timeout=5000)

        # Click "Use Selected" and check if it populates the text fields and submits context form
        use_selected_btn.click()

        # When Use Selected is clicked, it populates fields, sets context values, and calls loadBernieLiveReview
        # Since it is a valid context, it should transition to the instruction input.
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)

        # Submit the instruction text
        trigger_route_intercepted_bernie(diary_page, instruction="Please find earliest_time:09:00", register_default_mock=False)

        # Wait for confirm button to show
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)

        # Verify supervised booking request was sent with resolved practitioner and patient IDs
        assert len(supervised_requests) == 1
        assert supervised_requests[0]["command"]["practitioner_id"] == "smoke-prac-1"
        assert supervised_requests[0]["command"]["patient_id"] == "smoke-pat-1"

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_context_readiness_and_summary_flow(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    try:
        # Load with the historical context-form flag; ordinary Bernie now starts instruction-first.
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_context_form=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        # Launch Bernie Pilot sidebar
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # The instruction input textarea and submit button are usable without manual IDs.
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        submit_btn = diary_page.locator("[data-testid='btn-bernie-instruction-submit']")

        assert textarea.is_disabled() is False
        assert submit_btn.is_disabled() is False

        # No context form or context summary is shown until staff imports context.
        assert diary_page.locator("[data-testid='bernie-pilot-context-form']").count() == 0
        assert diary_page.locator("[data-testid='bernie-context-summary']").count() == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_context_summary_import_from_selected(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    try:
        # Load with bernie_context_form=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_context_form=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        # Launch Bernie Pilot sidebar
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # Click Margaret Thompson's appointment on the grid to make it active.
        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson')", state="visible", timeout=3000)

        # The import button should now appear in the apptPanel
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']", state="visible", timeout=3000)

        # Click the import button
        diary_page.click("[data-testid='bernie-pilot-use-selected']")

        # The context summary should appear
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)

        # The instruction input textarea and submit button should now be enabled
        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        submit_btn = diary_page.locator("[data-testid='btn-bernie-instruction-submit']")
        assert textarea.is_disabled() is False
        assert submit_btn.is_disabled() is False

        # Verify summary details contain the appointment's details (patient name/time, practitioner label)
        details = diary_page.locator("[data-testid='bernie-context-summary-details']")
        assert "Patient: Margaret Thompson" in details.text_content()
        assert "@ 09:00" in details.text_content()
        assert "Practitioner: Alex Shera" in details.text_content()

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_selected_appointment_instruction_affordances(diary_page):
    import urllib.parse
    import datetime
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    appointments = [
        {
            "id": "staff-visible-appt-73",
            "appointment_date": today_str,
            "start_time_local": "09:00",
            "start_time": "09:00",
            "duration_minutes": 15,
            "status": "Booked",
            "appointment_type_id": None,
            "patient_id": "real-patient-73",
            "patient": {
                "id": "real-patient-73",
                "first_name": "Margaret",
                "last_name": "Thompson",
                "date_of_birth": "1955-03-24"
            },
            "practitioner_id": "real-prac-73",
            "practitioner": {
                "id": "real-prac-73",
                "first_name": "Alex",
                "last_name": "Shera",
                "ahpra_number": "MED0001234567"
            },
            "room_id": None,
            "location_id": "loc-1",
            "notes": ""
        }
    ]

    mock_interpret = {
        "intent": "interpret_booking_instruction",
        "safe": True,
        "result": "interpreted",
        "autonomy_tier": "execute_with_report",
        "summary": "Find next available with this practitioner",
        "confidence": 0.9,
        "command_candidate": {
            "practitioner_id": "real-prac-73",
            "patient_id": "real-patient-73",
            "date_from": "today",
            "duration_minutes": 15
        },
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "real-prac-73",
                "patient_id": "real-patient-73",
                "date_from": today_str,
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully."
        },
        "warnings": [],
        "blocks": [],
        "provider_metadata": {
            "provider": "fake",
            "mode": "mocked",
            "live_provider": False
        }
    }

    mock_review = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "supervised",
        "summary": "Proposal confirmation ready",
        "normalization": mock_interpret["normalization"],
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": {
                "id": "slot-65",
                "appointment_date": today_str,
                "start_time_local": "09:30:00",
                "duration_minutes": 15
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Supervised review prepared from interpreted intent.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {"session_id": "session-123"},
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    interpret_requests = []
    supervised_requests = []
    confirm_payloads = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            interpret_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            supervised_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_review))
        elif "/api/v1/appointments/proposals/create/confirm-bernie" in url:
            confirm_payloads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected confirm"}))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-73",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointments))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson')", state="visible", timeout=3000)
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-pilot-practitioner-id']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-patient-id']").count() == 0
        assert diary_page.locator("[data-testid='bernie-pilot-context-submit']").count() == 0
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']", state="visible", timeout=3000)
        diary_page.click("[data-testid='bernie-pilot-use-selected']")

        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)

        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        assert textarea.is_disabled() is False

        suggestions_container = diary_page.locator("[data-testid='bernie-suggested-instructions']")
        suggestions_container.wait_for(state="visible", timeout=3000)

        chips = diary_page.locator(".bernie-suggestion-chip")
        assert chips.count() == 4
        assert chips.nth(0).text_content() == "Find earlier options for this patient"
        assert chips.nth(1).text_content() == "Find later options for this patient"
        assert chips.nth(2).text_content() == "Find next available with this practitioner"
        assert chips.nth(3).text_content() == "Check another day for this practitioner"

        assert len(interpret_requests) == 0
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0
        assert "instruction" not in diary_page.url

        diary_page.click("[data-testid='bernie-suggestion-chip-0']")
        assert textarea.input_value() == "Find earlier options for this patient"

        assert len(interpret_requests) == 0
        assert len(supervised_requests) == 0
        assert len(confirm_payloads) == 0
        assert "instruction" not in diary_page.url
        storage_values = diary_page.evaluate("""() => {
            const values = [];
            for (let i = 0; i < localStorage.length; i += 1) values.push(localStorage.getItem(localStorage.key(i)));
            for (let i = 0; i < sessionStorage.length; i += 1) values.push(sessionStorage.getItem(sessionStorage.key(i)));
            return values.filter(Boolean);
        }""")
        assert all("Find earlier options for this patient" not in value for value in storage_values)

        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector("[data-testid='bernie-review-status']", state="visible", timeout=5000)

        assert len(interpret_requests) == 1
        assert interpret_requests[0]["instruction"] == "Find earlier options for this patient"
        assert interpret_requests[0]["reference_date"]
        assert len(supervised_requests) == 1
        assert supervised_requests[0]["command"]["practitioner_id"] == "real-prac-73"
        assert supervised_requests[0]["command"]["patient_id"] == "real-patient-73"
        assert len(confirm_payloads) == 0

    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_blocks_interpreted_practitioner_mismatch_before_supervised_call(diary_page):
    import urllib.parse
    import datetime
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    appointments = [{
        "id": "staff-visible-appt-mismatch",
        "appointment_date": today_str,
        "start_time_local": "09:00",
        "start_time": "09:00",
        "duration_minutes": 15,
        "status": "Booked",
        "appointment_type_id": None,
        "patient_id": "real-patient-mismatch",
        "patient": {
            "id": "real-patient-mismatch",
            "first_name": "Margaret",
            "last_name": "Thompson",
            "date_of_birth": "1955-03-24"
        },
        "practitioner_id": "context-prac",
        "practitioner": {
            "id": "context-prac",
            "first_name": "Alex",
            "last_name": "Shera",
            "ahpra_number": "MED0001234567"
        },
        "room_id": None,
        "location_id": "loc-1",
        "notes": ""
    }]

    interpret_requests = []
    supervised_requests = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "surface": "bernie_staff_review",
                "enabled": True,
                "eligible": True,
                "reason": "allowlist_match",
                "practice_allowed": True,
                "user_allowed": True
            }))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            interpret_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "intent": "interpret_booking_instruction",
                "safe": True,
                "result": "interpreted",
                "autonomy_tier": "execute_with_report",
                "summary": "Mismatched practitioner instruction",
                "confidence": 0.9,
                "command_candidate": {
                    "practitioner_id": "typed-other-prac",
                    "patient_id": "real-patient-mismatch",
                    "date_from": "today",
                    "duration_minutes": 15
                },
                "missing_fields": [],
                "safety_flags": [],
                "clarifying_question": None,
                "warnings": [],
                "blocks": [],
                "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False}
            }))
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            supervised_requests.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected"}))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "context-prac",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointments))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.fill("[data-testid='bernie-instruction-input']", "Use the typed other practitioner")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector(
            "[data-testid='bernie-review-block-item']:has-text('I found a different practitioner from the diary context. Please check the practitioner before continuing.')",
            state="visible",
            timeout=5000,
        )

        assert len(interpret_requests) == 1
        assert len(supervised_requests) == 0
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_candidate_selection_empty_state(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "intent": "bernie_supervised_booking",
        "result": "candidate_selection_required",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "Candidate selection required.",
        "normalization": {"safe": True, "constraint": {}, "warnings": [], "blocks": []},
        "search_proposal": {"intent": "search_slots", "candidates": []},
        "selection_proposal": None,
        "staff_review": {
            "headline": "Candidate selection required.",
            "status": "candidate_selection_required",
            "staff_action_required": "Select one candidate slot before preparing confirmation evidence.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "No free slots found in the requested window.",
            "evidence_summary": "Candidate slot summaries are review-only until staff selects one slot.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true")
        trigger_route_intercepted_bernie(diary_page)
        diary_page.wait_for_selector("[data-testid='bernie-review-candidates-empty']", state="visible", timeout=5000)

        empty_text = diary_page.locator("[data-testid='bernie-review-candidates-empty']").text_content()
        assert "free times" in empty_text.lower()
        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_instruction_first_without_selected_appointment(diary_page):
    import urllib.parse
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-74",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?bernie_auto_preview=false")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)

        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        submit_btn = diary_page.locator("[data-testid='btn-bernie-instruction-submit']")
        assert textarea.is_enabled()
        assert submit_btn.is_enabled()
        assert diary_page.locator("[data-testid='bernie-pilot-context-warning']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-block-item']:has-text('stale_selected_appointment_context')").count() == 0

        textarea.fill("Make an appointment for Margaret Thompson with Dr Shera this afternoon")
        assert diary_page.locator("[data-testid='bernie-instruction-status-copy']").is_visible()
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_candidate_click_stages_provisional_diary_preview(diary_page):
    import urllib.parse
    import datetime
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }
    mock_interpret = {
        "intent": "interpret_booking_instruction",
        "safe": True,
        "result": "interpreted",
        "autonomy_tier": "execute_with_report",
        "summary": "Resolved appointment request.",
        "confidence": 0.9,
        "command_candidate": {
            "practitioner_id": "real-prac-93",
            "patient_id": "real-patient-93",
            "date_from": "today",
            "duration_minutes": 15
        },
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
        "warnings": [],
        "blocks": [],
        "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False}
    }
    candidate_review = {
        "intent": "bernie_supervised_booking",
        "result": "candidate_selection_required",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "Select one candidate.",
        "normalization": {"safe": True, "constraint": mock_interpret["command_candidate"], "warnings": [], "blocks": [], "summary": "ok"},
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "status": "candidate_selection_required",
            "staff_action_required": "Select a candidate.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [{
                "appointment_date": today_str,
                "start_time_local": "14:30:00",
                "duration_minutes": 15,
                "warnings": []
            }],
            "identity_evidence": {
                "patient_id": "real-patient-93",
                "patient_label": "Margaret Thompson",
                "confidence": "medium",
                "verification_status": "requires_staff_verification",
                "matched_fields": ["patient_id", "name", "date_of_birth"],
                "supporting_context": ["selected_diary_appointment"],
                "warnings": ["medicare_not_on_record"],
                "staff_prompt": "Confirm DOB and check Medicare/card details before confirming."
            },
            "warning_summary": "No warnings.",
            "evidence_summary": "Candidate slot summaries are review-only until staff selects one slot.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": [],
            "blocks": []
        },
        "warnings": [],
        "blocks": []
    }
    confirmation_review = {
        **candidate_review,
        "result": "confirmation_ready",
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "staff_review": {
            **candidate_review["staff_review"],
            "status": "confirmation_ready",
            "staff_action_required": "Review and confirm booking.",
            "confirmation_ready": True,
            "selected_slot": candidate_review["staff_review"]["candidate_slots"][0],
            "candidate_slots": [],
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence for explicit staff approval.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {"proposal_id": "prop-93", "confirmed": False},
            "confirm_evidence": []
        }
    }

    supervised_requests = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            body = json.loads(route.request.post_data or "{}")
            supervised_requests.append(body)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(confirmation_review if "selected_candidate_index" in body else candidate_review)
            )
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-93",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?bernie_auto_preview=false")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.fill("[data-testid='bernie-instruction-input']", "Make appointment for Margaret Thompson with Dr Shera at 2:30")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector("[data-testid='bernie-review-candidate-item']", state="visible", timeout=5000)
        identity_text = diary_page.locator("[data-testid='bernie-identity-evidence']").text_content()
        assert "Margaret Thompson" in identity_text
        assert "Medium confidence" in identity_text
        assert "Medicare Not On Record" in identity_text

        diary_page.click("[data-testid='bernie-review-candidate-item']")
        diary_page.wait_for_selector("[data-testid='bernie-staged-booking-card']", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)

        staged_card = diary_page.locator("[data-testid='bernie-staged-booking-card']")
        staged_text = staged_card.text_content()
        assert "Proposed appointment" in staged_text
        assert "Margaret Thompson" in staged_text
        assert "14:30:00" in staged_text
        assert "medicare/card" not in staged_text.lower()
        assert "is-fresh" in (staged_card.get_attribute("class") or "")
        assert staged_card.evaluate("el => getComputedStyle(el).animationName") == "bernie-staged-pulse"
        diary_page.emulate_media(reduced_motion="reduce")
        assert staged_card.evaluate("el => getComputedStyle(el).animationName") == "none"
        diary_page.emulate_media(reduced_motion="no-preference")
        assert supervised_requests[0].get("selected_candidate_index") is None
        assert supervised_requests[1]["selected_candidate_index"] == 0
    finally:
        diary_page.emulate_media(reduced_motion="no-preference")
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_route_intercepted_selected_slot_can_return_to_candidates(diary_page):
    import urllib.parse
    import datetime
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    candidate_slots = [
        {
            "appointment_date": today_str,
            "start_time_local": "14:30:00",
            "duration_minutes": 15,
            "warnings": []
        },
        {
            "appointment_date": today_str,
            "start_time_local": "15:00:00",
            "duration_minutes": 15,
            "warnings": []
        }
    ]
    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }
    mock_interpret = {
        "intent": "interpret_booking_instruction",
        "safe": True,
        "result": "interpreted",
        "autonomy_tier": "execute_with_report",
        "summary": "Resolved Margaret Thompson with Dr Shera.",
        "confidence": 0.9,
        "command_candidate": {
            "practitioner_id": "real-prac-98",
            "patient_id": "real-patient-98",
            "date_from": "today",
            "duration_minutes": 15,
            "earliest_time": "14:00",
            "latest_time": "15:45"
        },
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
        "warnings": [
            {"code": "practitioner_name_resolved", "message": "Dr Shera resolved."},
            {"code": "patient_name_resolved_verify_identity", "message": "Margaret Thompson resolved; verify identity."}
        ],
        "blocks": [],
        "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False}
    }
    candidate_review = {
        "intent": "bernie_supervised_booking",
        "result": "candidate_selection_required",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "Select one candidate.",
        "normalization": {"safe": True, "constraint": mock_interpret["command_candidate"], "warnings": [], "blocks": [], "summary": "ok"},
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "status": "candidate_selection_required",
            "staff_action_required": "Select a candidate.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": candidate_slots,
            "identity_evidence": {
                "patient_id": "real-patient-98",
                "patient_label": "Margaret Thompson",
                "confidence": "medium",
                "verification_status": "requires_staff_verification",
                "matched_fields": ["patient_id", "name", "date_of_birth"],
                "supporting_context": [],
                "warnings": ["medicare_not_on_record"],
                "staff_prompt": "Confirm DOB and check Medicare/card details before confirming."
            },
            "patient_evidence": {
                "patient_id": "real-patient-98",
                "patient_label": "Margaret Thompson",
                "date_of_birth": "1955-03-24",
                "masked_phone": None,
                "confidence": "medium",
                "is_provisional": False
            },
            "warning_summary": "No warnings.",
            "evidence_summary": "Candidate slot summaries are review-only until staff selects one slot.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": [],
            "blocks": []
        },
        "warnings": [],
        "blocks": []
    }

    def confirmation_review_for(index):
        return {
            **candidate_review,
            "result": "confirmation_ready",
            "requires_confirmation": True,
            "autonomy_tier": "proposal",
            "staff_review": {
                **candidate_review["staff_review"],
                "status": "confirmation_ready",
                "staff_action_required": "Review and confirm booking.",
                "confirmation_ready": True,
                "selected_slot": candidate_slots[index],
                "candidate_slots": [],
                "practitioner_evidence": {
                    "practitioner_id": "real-prac-98",
                    "display_name": "Alex Shera",
                    "provider_number": "2345678A",
                    "location_label": "Main Clinic"
                },
                "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence for explicit staff approval.",
                "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
                "confirm_payload": {"proposal_id": f"prop-98-{index}", "confirmed": False},
                "confirm_evidence": []
            }
        }

    supervised_requests = []
    confirm_payloads = []

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            body = json.loads(route.request.post_data or "{}")
            supervised_requests.append(body)
            selected = body.get("selected_candidate_index")
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(candidate_review if selected is None else confirmation_review_for(selected))
            )
        elif "/api/v1/appointments/proposals/create/confirm-bernie" in url:
            confirm_payloads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-98",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?bernie_auto_preview=false")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.fill(
            "[data-testid='bernie-instruction-input']",
            "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45"
        )
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector("[data-testid='bernie-review-candidate-item']", state="visible", timeout=5000)

        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 2
        panel_text = diary_page.locator("[data-testid='bernie-review-panel']").text_content()
        assert "Margaret Thompson" in panel_text
        assert "missing_practitioner_id" not in panel_text
        assert "practitioner_id" not in panel_text
        assert "Not Found" not in panel_text

        diary_page.locator("[data-testid='bernie-review-candidate-item']").first.click()
        diary_page.wait_for_selector("[data-testid='bernie-staged-booking-card']", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)
        assert supervised_requests[-1]["selected_candidate_index"] == 0
        assert "14:30:00" in diary_page.locator("[data-testid='bernie-staged-booking-card']").text_content()

        change_slot = diary_page.locator(
            "[data-testid='bernie-review-change-slot-button'], "
            "button:has-text('Choose another time'), "
            "button:has-text('Change time'), "
            "button:has-text('Back to times')"
        )
        assert change_slot.count() > 0, (
            "Selected Bernie slot state must provide a path back to the "
            "candidate booking slots before release closeout."
        )
        change_slot.first.click()

        diary_page.wait_for_selector("[data-testid='bernie-review-candidate-item']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 2
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0

        diary_page.locator("[data-testid='bernie-review-candidate-item']").nth(1).click()
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)
        assert supervised_requests[-1]["selected_candidate_index"] == 1
        assert "15:00:00" in diary_page.locator("[data-testid='bernie-staged-booking-card']").text_content()
        assert len(confirm_payloads) == 0
    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint100_bernie_tomorrow_reference_date_survives_diary_navigation(diary_page):
    """Selecting a tomorrow candidate must not re-resolve tomorrow after the diary jumps."""
    import json
    import urllib.parse

    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    supervised_requests = []

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "request_reference_date": "2026-07-01",
        "command_candidate": {
            "practitioner_id": "smoke-prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "tomorrow",
            "duration_minutes": "15",
            "earliest_time": "15:00"
        },
        "warnings": [],
        "blocks": []
    }
    candidate_payload = {
        "staff_review": {
            "status": "candidate_selection_required",
            "confirmation_ready": False,
            "candidate_slots": [
                {"appointment_date": "2026-07-02", "start_time_local": "15:00:00", "duration_minutes": 15},
                {"appointment_date": "2026-07-02", "start_time_local": "15:15:00", "duration_minutes": 15}
            ],
            "selected_slot": None,
            "identity_evidence": {"confidence": "medium", "patient_label": "Margaret Thompson", "staff_prompt": "Confirm DOB."},
            "patient_evidence": {"confidence": "medium", "patient_label": "Margaret Thompson", "date_of_birth": "1952-03-14"},
            "warnings": [],
            "blocks": []
        }
    }

    def confirmation_payload(index):
        slot = candidate_payload["staff_review"]["candidate_slots"][index]
        return {
            "staff_review": {
                **candidate_payload["staff_review"],
                "status": "confirmation_ready",
                "confirmation_ready": True,
                "candidate_slots": [],
                "selected_slot": slot,
                "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
                "confirm_payload": {"confirmed": False, "selection_proposal": {"intent": "select_slot_for_create_proposal"}}
            }
        }

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"eligible": True, "reasons": []}))
        elif "/api/v1/appointments/proposals/bernie/interpret-booking-instruction" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))
        elif "/api/v1/appointments/proposals/bernie/supervised-booking" in url:
            body = json.loads(route.request.post_data or "{}")
            supervised_requests.append(body)
            selected = body.get("selected_candidate_index")
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(candidate_payload if selected is None else confirmation_payload(int(selected)))
            )
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        diary_page.goto(
            base_url
            + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true"
            + "&bernie_dev_review=true&practitioner_id=smoke-prac-1&patient_id=smoke-pat-1&reference_date=2026-07-01"
        )
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        diary_page.fill("[data-testid='bernie-instruction-input']", "Make an appointment tomorrow after 3 with Dr Shera")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector("[data-testid='bernie-review-candidate-item']", state="visible", timeout=5000)

        assert supervised_requests[0]["reference_date"] == "2026-07-01"
        diary_page.locator("[data-testid='bernie-review-candidate-item']").first.click()
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)
        assert supervised_requests[-1]["reference_date"] == "2026-07-01"
        assert supervised_requests[-1]["selected_candidate_index"] == 0
        assert "2026-07-02" in diary_page.locator("[data-testid='bernie-staged-booking-card']").text_content()

        before_choose_again = len(supervised_requests)
        diary_page.click("[data-testid='bernie-review-change-slot-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-candidate-item']", state="visible", timeout=5000)
        assert len(supervised_requests) == before_choose_again

        diary_page.locator("[data-testid='bernie-review-candidate-item']").nth(1).click()
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)
        assert supervised_requests[-1]["reference_date"] == "2026-07-01"
        assert supervised_requests[-1]["selected_candidate_index"] == 1
        assert "2026-07-02" in diary_page.locator("[data-testid='bernie-staged-booking-card']").text_content()
    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_pilot_selected_appointment_instruction_readiness_and_resets(diary_page):
    import urllib.parse
    import datetime
    import json
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    appointments = [
        {
            "id": "staff-visible-appt-74a",
            "appointment_date": today_str,
            "start_time_local": "09:00",
            "start_time": "09:00",
            "duration_minutes": 15,
            "status": "Booked",
            "appointment_type_id": None,
            "patient_id": "real-patient-74",
            "patient": {
                "id": "real-patient-74",
                "first_name": "Margaret",
                "last_name": "Thompson",
                "date_of_birth": "1955-03-24"
            },
            "practitioner_id": "real-prac-74",
            "practitioner": {
                "id": "real-prac-74",
                "first_name": "Alex",
                "last_name": "Shera",
                "ahpra_number": "MED0001234567"
            },
            "room_id": None,
            "location_id": "loc-1",
            "notes": ""
        },
        {
            "id": "staff-visible-appt-74b",
            "appointment_date": today_str,
            "start_time_local": "10:00",
            "start_time": "10:00",
            "duration_minutes": 15,
            "status": "Booked",
            "appointment_type_id": None,
            "patient_id": "real-patient-74b",
            "patient": {
                "id": "real-patient-74b",
                "first_name": "Bob",
                "last_name": "Builder",
                "date_of_birth": "1960-05-15"
            },
            "practitioner_id": "real-prac-74",
            "practitioner": {
                "id": "real-prac-74",
                "first_name": "Alex",
                "last_name": "Shera",
                "ahpra_number": "MED0001234567"
            },
            "room_id": None,
            "location_id": "loc-1",
            "notes": ""
        }
    ]

    def handle_api(route):
        url = route.request.url
        if "/api/v1/appointments/bernie/pilot-eligibility" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_eligibility))
        elif "/api/v1/auth/me" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
        elif "/api/v1/diary/template" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Smoke Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "real-prac-74",
                    "practitioner_ahpra": "MED0001234567"
                }]
            }))
        elif "/api/v1/appointments/types" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        elif "/api/v1/appointments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointments))
        elif "/api/v1/diary/locations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Main Clinic", "is_active": True}
            ]))
        elif "/api/v1/diary/roster" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"entries": []}))
        elif "/api/v1/diary/waiting-areas" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    diary_page.route("**/api/v1/**", handle_api)

    try:
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        # Select first appointment
        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.wait_for_selector(".appt.appt-active:has-text('Margaret Thompson')", state="visible", timeout=3000)
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']", state="visible", timeout=5000)

        # Import context from selected
        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)

        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        status_copy = diary_page.locator("[data-testid='bernie-instruction-status-copy']")

        # 1. Assert status copy is hidden initially
        assert status_copy.is_visible() is False or status_copy.text_content().strip() == ""

        # 2. Click suggestion chip and verify chip readiness copy
        diary_page.wait_for_selector("[data-testid='bernie-suggestion-chip-0']", state="visible", timeout=3000)
        diary_page.click("[data-testid='bernie-suggestion-chip-0']")
        assert textarea.input_value() == "Find earlier options for this patient"
        assert status_copy.is_visible() is True
        assert status_copy.text_content() == "Ready to ask. Nothing is booked or changed until you confirm."

        # 3. Clear textarea and verify status copy is hidden
        textarea.fill("")
        assert status_copy.is_visible() is False or status_copy.text_content().strip() == ""

        # 4. Type instruction and verify typed readiness copy
        textarea.fill("Book next Friday")
        assert status_copy.is_visible() is True
        assert status_copy.text_content() == "Ready to ask. Nothing is booked or changed until you confirm."
        diary_page.evaluate("loadBernieLiveReview()")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)
        assert textarea.input_value() == "Book next Friday"
        assert status_copy.is_visible() is True

        # 5. Click "Change" and verify reset behavior (clears context, inputs, instructions)
        diary_page.click("[data-testid='bernie-pilot-context-change']")
        diary_page.wait_for_selector("[data-testid='bernie-pilot-use-selected']", state="visible", timeout=5000)
        # Re-import context to verify everything was reset
        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)
        assert textarea.input_value() == ""
        assert status_copy.is_visible() is False or status_copy.text_content().strip() == ""

        # 6. Type again, click the other appointment (which stales out the first context) and verify fallback to instruction-first mode
        textarea.fill("Some instruction")
        assert status_copy.is_visible() is True

        # Click other appointment (Bob Builder)
        diary_page.click(".appt:has-text('Bob Builder')")
        diary_page.wait_for_selector("[data-testid='bernie-instruction-input']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-block-item']:has-text('stale_selected_appointment_context')").count() == 0

        # Verify that instructions are reset and chips/readiness copy are absent/hidden
        assert status_copy.is_visible() is False or status_copy.text_content().strip() == ""
        assert diary_page.locator("[data-testid='bernie-suggested-instructions']").count() == 0

        # 7. Re-import context on the new appointment and verify it is clean (re-import reset)
        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.wait_for_selector("[data-testid='bernie-context-summary']", state="visible", timeout=5000)
        assert textarea.input_value() == ""
        assert status_copy.is_visible() is False or status_copy.text_content().strip() == ""

    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_ordinary_mode_readiness_and_diagnostics(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_provider_unavailable = {
        "intent": "bernie_supervised_booking",
        "result": "blocked",
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Interpretation failed closed",
        "normalization": None,
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Interpretation failed closed",
            "status": "blocked",
            "staff_action_required": "Please use structured booking fields.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Provider unavailable",
            "evidence_summary": "Live interpreter is unavailable",
            "confirm_payload": None,
            "blocks": [
                { "code": "booking_interpreter_provider_unavailable", "message": "Live booking-instruction interpreter provider is unavailable." }
            ]
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_provider_unavailable)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "safe": True,
                "result": "interpreted",
                "command_candidate": {
                    "practitioner_id": "smoke-prac-1",
                    "patient_id": "smoke-pat-1",
                    "date_from": "today",
                    "duration_minutes": "15"
                }
            })
        )
    )

    try:
        # 1. Test ordinary mode (stay calm, useful, and show friendly error without diagnostics)
        harness.bootstrap_auth(diary_page, REVIEW_AUTH_TOKEN)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_context_form=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        # Launch panel
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # Enter instruction and submit
        trigger_route_intercepted_bernie(diary_page, instruction="Find slot", register_default_mock=False)

        # Wait for the status badge
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)
        assert status.text_content().strip() == "Unavailable"

        # Check headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Bernie is temporarily unavailable"

        # Check action
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert action.text_content().strip() == "Bernie could not search just now. Nothing was booked. Try again in a moment."

        # Check block message
        block_items = diary_page.locator("[data-testid='bernie-review-block-item']")
        assert block_items.count() == 1
        assert block_items.first.text_content().strip() == "Bernie could not search just now. Nothing was booked. Try again in a moment."

        # Verify developer diagnostic container is ABSENT
        assert diary_page.locator("[data-testid='bernie-dev-diagnostic']").count() == 0

        # 2. Test Developer / Debug mode (show setup diagnostics)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # Enter instruction and submit
        trigger_route_intercepted_bernie(diary_page, instruction="Find slot", register_default_mock=False)

        # Wait for status badge
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)

        # In dev mode, block item shows technical details
        block_items = diary_page.locator("[data-testid='bernie-review-block-item']")
        assert block_items.count() == 1
        assert "Booking Interpreter Provider Unavailable" in block_items.first.text_content()

        # Verify developer diagnostic container IS visible
        diag = diary_page.locator("[data-testid='bernie-dev-diagnostic']")
        assert diag.count() == 1
        assert "Developer Setup Diagnostics" in diag.text_content()
        assert "Block [booking_interpreter_provider_unavailable]" in diag.text_content()

    finally:
        harness.clear_auth(diary_page)
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_ordinary_mode_no_raw_codes(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_blocked = {
        "intent": "bernie_supervised_booking",
        "result": "blocked",
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Practitioner ID is required.",
        "normalization": None,
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Practitioner ID is required.",
            "status": "blocked",
            "staff_action_required": "Please select a practitioner.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "0 warning(s), 1 blocked issue(s).",
            "evidence_summary": "Missing practitioner ID",
            "confirm_payload": None,
            "blocks": [
                { "code": "missing_practitioner_id", "message": "Please select a practitioner." }
            ]
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_blocked)
        )
    )

    try:
        # Ordinary mode: no debug parameters
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_context_form=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)

        # Launch panel
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # Enter instruction and submit
        trigger_route_intercepted_bernie(diary_page, instruction="Find slot", register_default_mock=True)

        # Wait for the status badge
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)

        # Check block message
        block_items = diary_page.locator("[data-testid='bernie-review-block-item']")
        assert block_items.count() == 1
        assert block_items.first.text_content().strip() == "I need a practitioner before I can search."

        # Verify developer diagnostic container is ABSENT
        assert diary_page.locator("[data-testid='bernie-dev-diagnostic']").count() == 0

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_dev_mode_diagnostics(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_blocked = {
        "intent": "bernie_supervised_booking",
        "result": "blocked",
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Practitioner ID is required.",
        "normalization": None,
        "search_proposal": None,
        "selection_proposal": None,
        "staff_review": {
            "headline": "Practitioner ID is required.",
            "status": "blocked",
            "staff_action_required": "Please select a practitioner.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "0 warning(s), 1 blocked issue(s).",
            "evidence_summary": "Missing practitioner ID",
            "confirm_payload": None,
            "blocks": [
                { "code": "missing_practitioner_id", "message": "Please select a practitioner." }
            ]
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_blocked)
        )
    )

    try:
        # Dev mode: bernie_dev_review=true query parameter
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # Enter instruction and submit
        trigger_route_intercepted_bernie(diary_page, instruction="Find slot", register_default_mock=True)

        # Wait for status badge
        status = diary_page.locator("[data-testid='bernie-review-status']")
        status.wait_for(state="visible", timeout=5000)

        # In dev mode, block item shows technical prefix "Missing Practitioner Id: Please select a practitioner."
        block_items = diary_page.locator("[data-testid='bernie-review-block-item']")
        assert block_items.count() == 1
        assert block_items.first.text_content().strip() == "Missing Practitioner Id: Please select a practitioner."

        # Verify developer diagnostic container IS visible
        diag = diary_page.locator("[data-testid='bernie-dev-diagnostic']")
        assert diag.count() == 1
        assert "Developer Setup Diagnostics" in diag.text_content()
        assert "Block [missing_practitioner_id]" in diag.text_content()

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_choose_different_time_restores_candidates(diary_page):
    import json
    import urllib.parse
    import datetime
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_candidate_selection_response = {
        "intent": "bernie_supervised_booking",
        "result": "candidate_selection_required",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "Candidate selection required.",
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "date_from": today_str,
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalization success."
        },
        "search_proposal": {
            "intent": "search_slots",
            "candidates": [
                {
                    "appointment_date": today_str,
                    "start_time_local": "09:00:00",
                    "duration_minutes": 15,
                    "warnings": []
                }
            ]
        },
        "selection_proposal": None,
        "staff_review": {
            "headline": "Candidate selection required.",
            "status": "candidate_selection_required",
            "staff_action_required": "Select one candidate slot before preparing confirmation evidence.",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [
                {
                    "appointment_date": "2026-06-27",
                    "start_time_local": "09:00:00",
                    "duration_minutes": 15,
                    "warnings": []
                }
            ],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Candidate slot summaries are review-only until staff selects one slot.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    mock_confirmation_ready_response = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "summary": "Confirmation ready.",
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "date_from": today_str,
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalization success."
        },
        "search_proposal": {
            "intent": "search_slots",
            "candidates": []
        },
        "selection_proposal": {
            "intent": "select_slot_for_create_proposal",
            "safe": True,
            "requires_confirmation": True,
            "autonomy_tier": "proposal",
            "selected_candidate": {
                "appointment_date": today_str,
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "create_proposal": {
                "intent": "create_appointment",
                "command": {
                    "patient_id": "smoke-pat-1",
                    "practitioner_id": "prac-1",
                    "appointment_date": today_str,
                    "start_time_local": "09:00:00",
                    "reason": "Follow-up"
                }
            }
        },
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False
            },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    calls = []
    def handle_supervised_booking(route):
        req = route.request
        body = json.loads(req.post_data)
        calls.append(body)
        if "selected_candidate_index" in body:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_confirmation_ready_response)
            )
        else:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_candidate_selection_response)
            )

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        handle_supervised_booking
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(status=500, body="Should not confirm early")
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']:not(.hidden)", state="visible", timeout=5000)

        # Enter instruction and submit
        trigger_route_intercepted_bernie(diary_page, instruction="Find slot", register_default_mock=True)

        # Verify candidate list rendered
        candidates_list = diary_page.locator("[data-testid='bernie-review-candidates-list']")
        candidates_list.wait_for(state="visible", timeout=5000)
        assert candidates_list.count() == 1

        # Check staged preview card on grid
        assert diary_page.locator("[data-testid='bernie-staged-booking-card']").count() == 0

        # Click candidate item
        diary_page.click("[data-testid='bernie-review-candidate-item']")

        # Verify confirmation ready
        diary_page.wait_for_selector("[data-testid='bernie-review-selected-slot']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").is_visible()

        # The grid preview is covered by the dedicated visual smoke test. This
        # check is about the review-loop contract: candidate -> selected slot ->
        # choose another time, with no confirm call.
        assert len(calls) == 2

        # Click "Choose another time"
        diary_page.click("[data-testid='bernie-review-change-slot-button']")

        # Wait for candidates list to be restored
        diary_page.wait_for_selector("[data-testid='bernie-review-candidates-list']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0

        # No confirm call was made while returning to candidate selection.
        assert len(calls) == 2

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_generic_confirm_not_found_calm_copy(diary_page):
    import json
    import urllib.parse
    import datetime
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_confirmation_ready_response = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "summary": "Confirmation ready.",
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "date_from": today_str,
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalization success."
        },
        "search_proposal": {
            "intent": "search_slots",
            "candidates": []
        },
        "selection_proposal": {
            "intent": "select_slot_for_create_proposal",
            "safe": True,
            "requires_confirmation": True,
            "autonomy_tier": "proposal",
            "selected_candidate": {
                "appointment_date": today_str,
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "create_proposal": {
                "intent": "create_appointment",
                "command": {
                    "patient_id": "smoke-pat-1",
                    "practitioner_id": "prac-1",
                    "appointment_date": today_str,
                    "start_time_local": "09:00:00",
                    "reason": "Follow-up"
                }
            }
        },
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": today_str,
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False
            },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_confirmation_ready_response)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=404,
            content_type="application/json",
            body=json.dumps({"detail": "Not Found"})
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Verify confirmation ready
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)

        # Click confirm button
        diary_page.click("[data-testid='bernie-review-confirm-button']")

        # Verify calm 404 message
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")
        error_msg.wait_for(state="visible", timeout=5000)
        assert error_msg.text_content().strip() == "This slot is no longer available. Please choose a different time."

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_generic_confirm_other_error_calm_copy(diary_page):
    import json
    import urllib.parse
    import datetime
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    today_str = datetime.date.today().isoformat()

    mock_eligibility = {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": True,
        "reason": "allowlist_match",
        "practice_allowed": True,
        "user_allowed": True
    }

    mock_confirmation_ready_response = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "summary": "Confirmation ready.",
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "date_from": today_str,
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalization success."
        },
        "search_proposal": {
            "intent": "search_slots",
            "candidates": []
        },
        "selection_proposal": {
            "intent": "select_slot_for_create_proposal",
            "safe": True,
            "requires_confirmation": True,
            "autonomy_tier": "proposal",
            "selected_candidate": {
                "appointment_date": today_str,
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "create_proposal": {
                "intent": "create_appointment",
                "command": {
                    "patient_id": "smoke-pat-1",
                    "practitioner_id": "prac-1",
                    "appointment_date": today_str,
                    "start_time_local": "09:00:00",
                    "reason": "Follow-up"
                }
            }
        },
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": today_str,
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False
            },
            "confirm_evidence": []
        },
        "warnings": [],
        "blocks": []
    }

    diary_page.route(
        "**/api/v1/appointments/bernie/pilot-eligibility",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_eligibility)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_confirmation_ready_response)
        )
    )

    # Intercept confirm-bernie to fail with 500
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({"detail": "Internal Server Error"})
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Verify confirmation ready
        diary_page.wait_for_selector("[data-testid='bernie-review-confirm-button']", state="visible", timeout=5000)

        # Click confirm button
        diary_page.click("[data-testid='bernie-review-confirm-button']")

        # Verify calm generic error message
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")
        error_msg.wait_for(state="visible", timeout=5000)
        assert error_msg.text_content().strip() == "We couldn't confirm this booking. Please try again or select another time."

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_inferred_today(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "Inferred date warning.",
            "evidence_summary": "Date was inferred as today.",
            "warnings": [
                { "code": "date_inferred_today", "severity": "warning", "message": "Inferred date is today." }
            ],
            "blocks": [],
            "patient_evidence": {
                "patient_label": "Margaret Thompson",
                "confidence": "high"
            }
        }
    }

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "command_candidate": {
            "practitioner_id": "smoke-prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "today",
            "duration_minutes": "15"
        }
    }
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&practitioner_id=smoke-prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page, instruction="Please find practitioner_id:smoke-prac-1 patient_id:smoke-pat-1", register_default_mock=False)

        # 1. Inferred Today warning notice renders
        notice = diary_page.locator("[data-testid='bernie-notice-alert']")
        notice.wait_for(state="visible", timeout=5000)
        assert "I've assumed today for the booking date since you didn't mention a date." in notice.text_content()

        # 2. Provisional slot card renders on the grid
        grid_card = diary_page.locator("[data-testid='bernie-staged-booking-card']")
        grid_card.wait_for(state="visible", timeout=5000)
        assert grid_card.count() == 1

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_no_reference_date_clarification(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "blocked",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Missing date.",
            "evidence_summary": "Blocked by missing reference date.",
            "warnings": [],
            "blocks": [
                { "code": "missing_reference_date", "severity": "blocked", "message": "Reference date is missing." }
            ]
        }
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_reanchor_visible_date=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        # Verify first-person date prompt displays
        block_item = diary_page.locator("[data-testid='bernie-review-block-item']")
        block_item.wait_for(state="visible", timeout=5000)
        assert block_item.count() == 1
        assert "I need a date before I can search." in block_item.text_content()

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_practitioner_typo(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "Typo warning.",
            "evidence_summary": "Resolved practitioner typo.",
            "warnings": [
                { "code": "practitioner_typo_resolved", "severity": "warning", "message": "Resolved practitioner typo for entry Sheraa" }
            ],
            "blocks": [],
            "practitioner_evidence": {
                "practitioner_id": "8b5f3964-b52b-42fa-90f7-b4d21e8e2fa5",
                "display_name": "Shera"
            }
        }
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_reanchor_visible_date=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        # Verify notice matches Dr. Shera and entry Sheraa
        notice = diary_page.locator("[data-testid='bernie-notice-alert']")
        notice.wait_for(state="visible", timeout=5000)
        assert "Do you mean Dr Shera (for your entry 'Sheraa')?" in notice.text_content()

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_patient_candidate_ambiguity(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "blocked",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Ambiguous patient.",
            "evidence_summary": "Multiple patient candidates.",
            "warnings": [],
            "blocks": [],
            "identity_evidence": {
                "patient_label": "Margaret",
                "confidence": "ambiguous",
                "verification_status": "requires_staff_verification",
                "staff_prompt": "Multiple patients matching Margaret."
            },
            "patient_candidates": [
                { "candidate_key": "11111111-1111-1111-1111-111111111111", "display_name": "Margaret Thompson", "dob_masked": "1960-**-**", "match_kind": "fuzzy", "requires_identifier": True },
                { "candidate_key": "22222222-2222-2222-2222-222222222222", "display_name": "Margaret Smith", "dob_masked": "1975-**-**", "match_kind": "fuzzy", "requires_identifier": True }
            ]
        }
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_reanchor_visible_date=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        # Verify first-person choice prompt
        notice = diary_page.locator("[data-testid='bernie-notice-alert']")
        notice.wait_for(state="visible", timeout=5000)
        assert "I found multiple patients matching 'Margaret'. Please select the correct patient." in notice.text_content()

        # Verify candidate items render
        candidates = diary_page.locator("[data-testid='bernie-patient-candidate-item']")
        assert candidates.count() == 2
        assert "Margaret Thompson" in candidates.nth(0).text_content()
        assert "Margaret Smith" in candidates.nth(1).text_content()

        # Verify that the auto-preview slot is NOT rendered on the grid
        assert diary_page.locator("[data-testid='bernie-staged-booking-card']").count() == 0

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint101_bernie_details_toggle_and_recognition_prompt(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. High/medium confidence recognised patient - details collapsed, no routine DOB prompt
    mock_high_conf = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "Patient recognised.",
            "evidence_summary": "High confidence recognised patient.",
            "warnings": [],
            "blocks": [],
            "identity_evidence": {
                "patient_label": "Margaret Thompson",
                "confidence": "high",
                "recognition_status": "recognized",
                "details_verification_status": "not_required_for_booking",
                "verification_status": "not_applicable",
                "staff_prompt": "Patient recognised from the practice register."
            }
        }
    }

    # 2. Low confidence / not recognised - details expanded and prompt visible
    mock_low_conf = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "Low confidence details.",
            "evidence_summary": "Low confidence detail.",
            "warnings": [],
            "blocks": [],
            "identity_evidence": {
                "patient_label": "Margaret Thompson",
                "confidence": "low",
                "recognition_status": "not_recognized",
                "details_verification_status": "requires_follow_up",
                "verification_status": "requires_staff_verification",
                "staff_prompt": "Recognise the patient before booking."
            }
        }
    }

    try:
        # Check high-confidence recognised case: collapsed details, no routine prompt.
        diary_page.route(
            "**/api/v1/appointments/proposals/bernie/supervised-booking",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_high_conf)
            )
        )
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        details = diary_page.locator("[data-testid='bernie-evidence-details']")
        details.wait_for(state="visible", timeout=5000)
        assert details.evaluate("el => el.open") is False

        assert diary_page.locator("[data-testid='bernie-compact-recognition-prompt']").count() == 0

        # Check low-confidence case: expanded details and recognition prompt visible.
        diary_page.route(
            "**/api/v1/appointments/proposals/bernie/supervised-booking",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_low_conf)
            )
        )
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        details_low = diary_page.locator("[data-testid='bernie-evidence-details']")
        details_low.wait_for(state="visible", timeout=5000)
        assert details_low.evaluate("el => el.open") is True

        recognition_prompt = diary_page.locator("[data-testid='bernie-compact-recognition-prompt']")
        recognition_prompt.wait_for(state="visible", timeout=5000)
        assert "Recognise the patient before booking." in recognition_prompt.text_content()

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_raw_code_exclusion(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "blocked",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Blocked by practitioner.",
            "evidence_summary": "Technical code checks.",
            "warnings": [],
            "blocks": [
                { "code": "missing_practitioner_id", "severity": "blocked", "message": "Practitioner ID is required." }
            ]
        }
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        # Assert no snake_case or raw technical codes rendered in ordinary mode
        review_panel_text = diary_page.locator("[data-testid='bernie-review-panel']").text_content()
        assert "missing_practitioner_id" not in review_panel_text
        assert "UUID" not in review_panel_text

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint98_ordinary_block_copy_scrubs_raw_booking_internals(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "command_candidate": {
            "practitioner_label": "Dr Shera",
            "patient_label": "Margaret Thompson",
            "date_from": "today",
            "duration_minutes": 15
        }
    }
    mock_response = {
        "staff_review": {
            "status": "blocked",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Blocked by booking evidence.",
            "evidence_summary": "Technical detail should not reach ordinary staff copy.",
            "warnings": [],
            "blocks": [
                {
                    "code": "booking_detail_missing",
                    "severity": "blocked",
                    "message": "Not Found: missing_practitioner_id practitioner_id 123e4567-e89b-12d3-a456-426614174000 Practitioner ID is required."
                }
            ]
        }
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret)
        )
    )
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(
            diary_page,
            instruction="Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45",
            register_default_mock=False
        )

        diary_page.locator("[data-testid='bernie-review-block-item']").wait_for(state="visible", timeout=5000)
        panel_text = diary_page.locator("[data-testid='bernie-review-panel']").text_content()

        assert "I need a practitioner before I can search." in panel_text
        for forbidden in SPRINT98_FORBIDDEN_ORDINARY_COPY:
            assert forbidden not in panel_text

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_no_write_before_confirm(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Ready to confirm.",
            "warnings": [],
            "blocks": []
        }
    }

    confirm_hits = []
    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "command_candidate": {
            "practitioner_id": "smoke-prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "today",
            "duration_minutes": "15"
        }
    }
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )
    diary_page.route(
        "**/confirm-bernie",
        lambda route: (confirm_hits.append(True), route.fulfill(status=200, body=b"{}"))
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&practitioner_id=smoke-prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page, instruction="Please find practitioner_id:smoke-prac-1 patient_id:smoke-pat-1", register_default_mock=False)

        # Staged preview is rendered, but confirm endpoint is never hit until Confirm is clicked
        diary_page.wait_for_selector("[data-testid='bernie-staged-booking-card']", state="visible", timeout=5000)
        assert len(confirm_hits) == 0

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint103_bernie_compact_request_card_and_sensitive_details(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "summary": "Bernie needs one more detail before it can search.",
        "command_candidate": {
            "practitioner_id": "smoke-prac-1",
            "practitioner_label": "Alex Shera",
            "patient_id": "smoke-pat-1",
            "patient_label": "Margaret Thompson",
            "date_from": "2026-07-03",
            "duration_minutes": 15,
            "earliest_time": "15:00:00",
            "latest_time": "16:30:00"
        },
        "warnings": [
            {"code": "date_assumed_from_visible_diary", "message": "Date assumed from the open diary page."}
        ],
        "blocks": []
    }

    mock_response = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-07-03",
                "start_time_local": "15:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Ready to confirm.",
            "warnings": [],
            "blocks": [],
            "identity_evidence": {
                "patient_id": "smoke-pat-1",
                "patient_label": "Margaret Thompson",
                "confidence": "high",
                "recognition_status": "recognized",
                "medicare_number": "12345678901",
                "ihi_number": "8003608333333333"
            },
            "patient_evidence": {
                "patient_label": "Margaret Thompson",
                "date_of_birth": "1952-03-14",
                "masked_phone": "******5678",
                "confidence": "high"
            }
        }
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret)
        )
    )
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&practitioner_id=smoke-prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page, instruction="Make an appointment for Margaret Thompson with Dr Shera after 3 tomorrow and before 4.30.", register_default_mock=False)

        diary_page.wait_for_selector("[data-testid='bernie-review-selected-slot']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-interpret-status']").text_content().strip() == "Understood"
        assert diary_page.locator("[data-testid='bernie-interpret-summary']").count() == 0
        assert diary_page.locator("[data-testid='bernie-interpret-command']").count() == 0
        assert diary_page.locator("[data-testid='bernie-interpret-details'] summary").text_content().strip() == "Need to clarify anything?"

        sensitive = diary_page.locator("[data-testid='bernie-appointment-sensitive-details']")
        sensitive.wait_for(state="visible", timeout=5000)
        assert sensitive.evaluate("el => el.open") is False
        assert "12345678901" not in diary_page.locator("[data-testid='bernie-review-panel']").inner_text()
        sensitive.locator("summary").click()
        assert "12345678901" in sensitive.inner_text()
        assert "8003608333333333" in sensitive.inner_text()

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint103_bernie_auto_stages_best_candidate_in_ordinary_mode(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "summary": "Find appointment slots.",
        "command_candidate": {
            "practitioner_id": "smoke-prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "2026-07-03",
            "duration_minutes": 15,
            "earliest_time": "15:00:00",
            "latest_time": "16:30:00"
        },
        "warnings": [],
        "blocks": []
    }
    mock_candidate_response = {
        "staff_review": {
            "status": "candidate_selection_required",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [
                {
                    "appointment_date": "2026-07-03",
                    "start_time_local": "15:00:00",
                    "duration_minutes": 15,
                    "warnings": []
                },
                {
                    "appointment_date": "2026-07-03",
                    "start_time_local": "15:15:00",
                    "duration_minutes": 15,
                    "warnings": []
                }
            ],
            "warning_summary": "Choose a time.",
            "evidence_summary": "Candidates only.",
            "warnings": [],
            "blocks": []
        }
    }
    mock_confirmation_response = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-07-03",
                "start_time_local": "15:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Ready.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False,
                "selection_proposal": {
                    "selected_candidate": {
                        "appointment_date": "2026-07-03",
                        "start_time_local": "15:00:00",
                        "duration_minutes": 15
                    }
                }
            },
            "confirm_affordance": {
                "confirm_grade_allowed": True,
                "can_show_confirm_ui": True,
                "gate": "allowed"
            },
            "warnings": [],
            "blocks": [],
            "identity_evidence": {
                "patient_id": "smoke-pat-1",
                "patient_label": "Margaret Thompson",
                "confidence": "high",
                "recognition_status": "recognized"
            },
            "patient_evidence": {
                "patient_label": "Margaret Thompson",
                "date_of_birth": "1952-03-14",
                "confidence": "high"
            }
        }
    }

    calls = []

    def handle_supervised(route):
        body = json.loads(route.request.post_data)
        calls.append(body)
        if "selected_candidate_index" in body:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_confirmation_response))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_candidate_response))

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_interpret))
    )
    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&practitioner_id=smoke-prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page, instruction="Find Margaret Thompson after 3 tomorrow.", register_default_mock=False)

        diary_page.wait_for_selector("[data-testid='bernie-review-selected-slot']", state="visible", timeout=5000)
        diary_page.wait_for_selector("[data-testid='bernie-staged-booking-card']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").is_visible()
        assert len(calls) == 2
        assert calls[1]["selected_candidate_index"] == 0

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_choose_another_time_suppression(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_response = {
        "staff_review": {
            "status": "confirmation_ready",
            "confirmation_ready": True,
            "selected_slot": {
                "appointment_date": "2026-06-27",
                "start_time_local": "09:00:00",
                "duration_minutes": 15,
                "warnings": []
            },
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Staged candidate.",
            "warnings": [],
            "blocks": []
        }
    }

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "command_candidate": {
            "practitioner_id": "smoke-prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "today",
            "duration_minutes": "15"
        }
    }
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret)
        )
    )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_response)
        )
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&practitioner_id=smoke-prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page, instruction="Please find practitioner_id:smoke-prac-1 patient_id:smoke-pat-1", register_default_mock=False)

        # Assert staged provisional card is rendered
        grid_card = diary_page.locator("[data-testid='bernie-staged-booking-card']")
        grid_card.wait_for(state="visible", timeout=5000)
        assert grid_card.count() == 1

        # Click Choose another time
        diary_page.click("[data-testid='bernie-review-change-slot-button']")

        # Assert staged card is removed from the grid
        assert diary_page.locator("[data-testid='bernie-staged-booking-card']").count() == 0

    finally:
        diary_page.unroute("**/api/v1/**")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint102_bernie_interpret_request_includes_visible_diary_context(diary_page):
    import re
    import urllib.parse

    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_requests = []
    mock_interpret = {
        "safe": False,
        "result": "clarification_required",
        "summary": "Which day would you like me to check?",
        "clarifying_question": "Which day would you like me to check?",
        "command_candidate": None,
        "normalization": None,
        "blocks": [],
        "warnings": [],
        "assumptions": [],
        "provider_metadata": {"mode": "mocked", "live_provider": False},
    }

    def capture_interpret(route):
        captured_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret),
        )

    diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        capture_interpret,
    )

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(
            diary_page,
            instruction="Make an appointment for Junior Atkinson at 11:15 with Dr Shera.",
            register_default_mock=False,
        )
        diary_page.wait_for_selector("[data-testid='bernie-interpret-preview']", state="visible", timeout=5000)

        assert captured_requests, "expected a Bernie interpret request"
        frames = captured_requests[0].get("context_frames", [])
        visible_frames = [frame for frame in frames if frame.get("type") == "visible_diary_page"]
        assert len(visible_frames) == 1
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", visible_frames[0].get("visible_date", ""))
        assert visible_frames[0]["visible_date"] == visible_frames[0]["diary_date"]
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_sprint99_bernie_asset_version_checks():
    import re
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[1]
    html_path = repo_root / "docs" / "diary" / "diary.html"
    html_content = html_path.read_text(encoding="utf-8")

    # Assert that scripts and style assets are loaded with cache-busting version query parameters
    assert re.search(r'diary\.css\?v=\d+', html_content) is not None
    assert re.search(r'diary\.js\?v=\d+', html_content) is not None


def test_bernie_turns_and_typed_event_payloads(diary_page):
    """Verify that turns are correctly logged as typed event objects and serialized."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_requests = []

    mock_interpret = {
        "safe": True,
        "result": "clarification_required",
        "summary": "Which date?",
        "clarifying_question": "Which date?",
        "command_candidate": None,
        "normalization": None,
        "blocks": [],
        "warnings": [],
        "assumptions": [],
        "provider_metadata": {"mode": "mocked", "live_provider": False},
    }

    def capture_interpret(route):
        captured_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret),
        )

    diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        capture_interpret,
    )

    try:
        # Start fresh session
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # We start a new session to clear any previous turns
        diary_page.evaluate("bernieSession.startNewSession()")

        # Enter an instruction
        trigger_route_intercepted_bernie(
            diary_page,
            instruction="Book appointment for smoke-pat-1 with practitioner prac-1",
            register_default_mock=False,
        )
        diary_page.wait_for_selector("[data-testid='bernie-chat-transcript']", state="visible", timeout=5000)

        # Get session state
        turns = diary_page.evaluate("bernieSession.turns")
        assert len(turns) >= 2

        # The first event should be staff_instruction
        event0 = turns[0]
        assert event0["kind"] == "staff_instruction"
        assert event0["payload"]["instruction"] == "Book appointment for smoke-pat-1 with practitioner prac-1"
        assert "id" in event0
        assert "timestamp" in event0

        # The second event should be bernie_clarification
        event1 = turns[1]
        assert event1["kind"] == "bernie_clarification"
        assert event1["payload"]["text"] == "Which date?"
        assert event1["payload"]["type"] == "clarification_question"

        # Now reply to clarification
        captured_requests.clear()

        # Enter a reply
        diary_page.locator("[data-testid='bernie-instruction-input']").fill("Tomorrow")
        diary_page.locator("[data-testid='btn-bernie-instruction-submit']").click()
        diary_page.wait_for_timeout(500)

        turns_after_reply = diary_page.evaluate("bernieSession.turns")
        assert len(turns_after_reply) >= 3

        # The third event should be clarification_reply
        event2 = turns_after_reply[2]
        assert event2["kind"] == "clarification_reply"
        assert event2["payload"]["reply"] == "Tomorrow"

        # Check that the turns array is sent properly in request
        assert captured_requests, "expected a Bernie interpret request"
        req_turns = captured_requests[0].get("turns", [])
        assert len(req_turns) >= 3
        assert req_turns[2]["kind"] == "clarification_reply"
        assert req_turns[2]["payload"]["reply"] == "Tomorrow"

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_composer_clearing_and_no_slot_suggestions(diary_page):
    """Verify that clicking a no-slot suggestion chip clears composer and includes original turn ID."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_interpret_requests = []

    mock_interpret = {
        "safe": True,
        "result": "interpreted",
        "command_candidate": {
            "practitioner_id": "prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "today",
            "duration_minutes": "15"
        }
    }

    mock_supervised_booking = {
        "staff_review": {
            "status": "candidate_selection_required",
            "confirmation_ready": False,
            "candidate_slots": [],
            "selected_slot": None,
            "identity_evidence": None,
            "patient_evidence": None,
            "warnings": [],
            "blocks": [],
            "suggestions": [
                {"summary": "Try tomorrow instead"}
            ]
        }
    }

    def capture_interpret(route):
        captured_interpret_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret),
        )

    def capture_supervised(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_supervised_booking),
        )

    diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        capture_interpret,
    )
    diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        capture_supervised,
    )

    try:
        # Start fresh session
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate("bernieSession.startNewSession()")

        # Trigger interpretation that yields no slot but suggestions
        trigger_route_intercepted_bernie(
            diary_page,
            instruction="Book slot",
            register_default_mock=False,
        )
        # Wait for the suggestions container
        diary_page.wait_for_selector("[data-testid='bernie-no-slot-suggestions']", state="visible", timeout=5000)

        # Save turn info. The no-slot state may have a Bernie turn in some
        # flows, but the typed suggestion event must still work without one.
        turns_before_click = diary_page.evaluate("bernieSession.turns")
        last_clarification = next(
            (t for t in reversed(turns_before_click) if t["kind"] == "bernie_clarification"),
            None,
        )
        expected_original_turn_id = last_clarification["id"] if last_clarification else None

        # Focus/check input textarea values
        diary_page.locator("[data-testid='bernie-instruction-input']").fill("stale text in composer")

        # Click suggestion chip
        captured_interpret_requests.clear()
        diary_page.locator(".bernie-suggestion-chip:has-text('Try tomorrow instead')").click()
        diary_page.wait_for_timeout(500)

        # Composer textarea must be cleared
        post_click_textarea_val = diary_page.locator("[data-testid='bernie-instruction-input']").input_value()
        assert post_click_textarea_val == ""

        # Check logged events
        turns_after_click = diary_page.evaluate("bernieSession.turns")
        # Should have a 'no_slot_suggestion_click' event
        suggestion_event = next(t for t in turns_after_click if t["kind"] == "no_slot_suggestion_click")
        assert suggestion_event["payload"]["suggestion"] == "Try tomorrow instead"
        assert suggestion_event["payload"]["original_turn_id"] == expected_original_turn_id

        # The subsequent request must send the new turns list with the event
        assert captured_interpret_requests, "expected a Bernie interpret request"
        req_body = captured_interpret_requests[0]
        assert req_body["instruction"] == "Try tomorrow instead"
        assert req_body["turns"][-1]["kind"] == "no_slot_suggestion_click"

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)



def test_bernie_stale_navigation_clearing(diary_page):
    """Verify that date navigation clears stale Bernie state and logs date_navigation_clear event."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Ensure we have active context
        diary_page.evaluate("bernieSession.init('prac-1', 'smoke-pat-1')")
        diary_page.evaluate("bernieSession.state = 'SLOT_PREVIEW'")
        diary_page.evaluate("bernieSession.stagedBookingPreview = { test: 123 }")

        # Click next day
        diary_page.click("#btn-next-day")
        diary_page.wait_for_timeout(500)

        # Verify stale fields cleared
        staged = diary_page.evaluate("bernieSession.stagedBookingPreview")
        assert staged is None

        # State should reset to INSTRUCTION_ENTRY (since practitioner/patient context is preserved in form/legacy state)
        state = diary_page.evaluate("bernieSession.state")
        assert state in ("INSTRUCTION_ENTRY", "CONTEXT_SELECTION")

        # Check event logging
        turns = diary_page.evaluate("bernieSession.turns")
        nav_event = next(t for t in turns if t["kind"] == "date_navigation_clear")
        assert nav_event["payload"]["reason"] == "next_day"
        assert "old_date" in nav_event["payload"]
        assert "new_date" in nav_event["payload"]

        # Test today button click
        diary_page.evaluate("bernieSession.state = 'SLOT_PREVIEW'")
        diary_page.evaluate("bernieSession.stagedBookingPreview = { test: 456 }")

        diary_page.click("#btn-today")
        diary_page.wait_for_timeout(500)

        # Verify cleared again
        assert diary_page.evaluate("bernieSession.stagedBookingPreview") is None

        turns_today = diary_page.evaluate("bernieSession.turns")
        today_event = next(t for t in reversed(turns_today) if t["kind"] == "date_navigation_clear")
        assert today_event["payload"]["reason"] == "today_click"

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_render_guard_prevents_false_found_or_no_slot_copy(diary_page):
    """Informational notes must not masquerade as candidate or no-slot truth."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "candidate_selection_required",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [{
                  code: "existing_future_follow_up",
                  severity: "warning",
                  message: "This patient already has a future appointment booked. Check whether a new booking is still needed."
                }],
                blocks: [],
                suggestions: [],
                warning_summary: "Patient recognised.",
                evidence_summary: "Review-only payload.",
                confirm_payload: null
              }, {
                result: "interpreted",
                safe: true,
                summary: "Request understood.",
                warnings: [{
                  code: "existing_future_follow_up",
                  severity: "warning",
                  message: "This patient already has a future appointment booked. Check whether a new booking is still needed."
                }],
                blocks: [],
                assumptions: [],
                provider_metadata: { mode: "mocked", live_provider: false }
              });
            }"""
        )

        panel_text = diary_page.locator("[data-testid='bernie-review-panel']").text_content()
        assert "Bernie found these times" not in panel_text
        assert "I could not find any free times for that request" not in panel_text
        assert "This patient already has a future appointment booked. Check whether a new booking is still needed." in panel_text
        assert diary_page.locator("[data-testid='bernie-review-status']").text_content().strip() == "Try another time"
        assert "I could not find matching free times in that window" in panel_text
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_composer_general_and_history_latest_visible(diary_page):
    """Composer stays generic/empty while latest chat remains visible and older turns collapse."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              bernieSession.startNewSession();
              bernieSession.addEvent("staff_instruction", { instruction: "Make an appointment for Margaret Thompson." });
              bernieSession.addEvent("bernie_clarification", { text: "Which day should I check?", type: "clarification_question" });
              updateBernieChatTranscriptUI();
              const contentEl = document.getElementById("bernie-review-content");
              contentEl.innerHTML = "";
              renderBernieInstructionInput(contentEl);
            }"""
        )

        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        assert textarea.input_value() == ""
        assert textarea.get_attribute("placeholder") == "Reply to Bernie..."
        assert diary_page.locator("[data-testid='btn-bernie-instruction-submit']").text_content().strip() == "Ask Bernie"
        assert diary_page.locator("[data-testid='bernie-chat-history']").count() == 1
        assert "Which day should I check?" in diary_page.locator("[data-testid='bernie-chat-transcript']").text_content()
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_tool_intent_extension_proposal_renders_and_confirms(diary_page):
    """Ask Bernie can route an appointment-extension request to the typed tool-intent proposal contract."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_tool_intent = []
    captured_update = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/bernie/tool-intent"):
            body = request.post_data_json
            captured_tool_intent.append(body)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "bernie_tool_intent",
                    "safe": True,
                    "result": "proposal_ready",
                    "tool_intent": "extend_appointment",
                    "autonomy_tier": "proposal",
                    "requires_confirmation": True,
                    "summary": "I've prepared a proposal to change this appointment to 30 minutes. Nothing is changed until staff confirm.",
                    "proposal": {
                        "intent": "update_appointment",
                        "safe": True,
                        "autonomy_tier": "proposal",
                        "requires_confirmation": True,
                        "issues": [],
                        "warnings": [],
                        "blocks": [],
                        "command": {
                            "appointment_id": "appt-tool-1",
                            "practitioner_id": "practitioner-123",
                            "appointment_type_id": "type-1",
                            "appointment_date": "2026-07-03",
                            "start_time_local": "15:00:00",
                            "duration_minutes": 30,
                            "reason": "Review",
                            "patient_id": "patient-123",
                            "patient_name_provisional": None,
                            "location_id": "loc-1",
                        },
                        "patient_identity": "linked",
                    },
                    "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "update_proposal": {
                            "intent": "update_appointment",
                            "safe": True,
                            "autonomy_tier": "proposal",
                            "requires_confirmation": True,
                            "warnings": [],
                            "blocks": [],
                            "command": {
                                "appointment_id": "appt-tool-1",
                                "practitioner_id": "practitioner-123",
                                "appointment_type_id": "type-1",
                                "appointment_date": "2026-07-03",
                                "start_time": "2026-07-03T05:00:00Z",
                                "start_time_local": "15:00:00",
                                "duration_minutes": 30,
                                "reason": "Review",
                                "patient_id": "patient-123",
                                "patient_name_provisional": None,
                                "location_id": "loc-1",
                            },
                            "patient_identity": "linked",
                        },
                        "update_proposal_freshness_id": "fresh-tool-1",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "bernie_confirm_update_proposal",
                            "payload": {"fixture": "tool-intent"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                    "update_proposal_freshness_id": "fresh-tool-1",
                    "signed_confirmation_evidence_required": True,
                    "warnings": [],
                    "blocks": [],
                    "source_attribution": {
                        "intent_source": "deterministic_text_parser",
                        "appointment_source": "visible_diary_context",
                        "proposal_authority": "appointment_update_proposal",
                        "write_authority": "signed_update_confirm_endpoint",
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/bernie/interpret-booking-instruction"):
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected booking interpreter"}))
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/confirm"):
            captured_update.append({
                "body": request.post_data_json,
                "idempotency_key": request.headers.get("idempotency-key"),
            })
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_update_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Updated.",
                    "appointment": {"id": "appt-tool-1", "duration_minutes": 30},
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["bernie_confirm_update_proposal"],
                }),
            )
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        diary_page.evaluate(
            """() => {
              diaryDate = new Date(2026, 6, 3);
              isBerniePilotActive = true;
              activeAppointments = [{
                id: "appt-tool-1",
                appointment_date: "2026-07-03",
                start_time_local: "15:00:00",
                duration_minutes: 15,
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson" },
                practitioner_id: "practitioner-123",
                practitioner: { first_name: "Alex", last_name: "Shera" },
                appointment_type_id: "type-1",
                location_id: "loc-1",
                status: "Booked"
              }];
              const contentEl = document.getElementById("bernie-review-content");
              contentEl.innerHTML = "";
              renderBernieInstructionInput(contentEl);
            }"""
        )

        diary_page.fill("[data-testid='bernie-instruction-input']", "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector("[data-testid='bernie-tool-intent-proposal']", state="visible", timeout=5000)

        panel_text = diary_page.locator("[data-testid='bernie-review-panel']").text_content()
        assert "Appointment change proposal" in panel_text
        assert "Current duration" in panel_text
        assert "30 mins" in panel_text
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='btn-bernie-tool-intent-confirm']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-candidates-empty']").count() == 0

        diary_page.evaluate("() => { isSmokeMode = () => false; }")
        diary_page.click("[data-testid='btn-bernie-tool-intent-confirm']")
        diary_page.wait_for_function("updates => updates.length > 0", arg=captured_update, timeout=5000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_tool_intent, "Expected tool-intent request"
    assert captured_tool_intent[0]["context_frames"], "Expected visible diary context frames"
    assert any(frame.get("appointment_id") == "appt-tool-1" for frame in captured_tool_intent[0]["context_frames"])
    assert captured_update[0]["idempotency_key"] == "update-confirm-fresh-tool-1"
    assert captured_update[0]["body"]["confirmed"] is True
    assert captured_update[0]["body"]["update_proposal"]["command"]["appointment_id"] == "appt-tool-1"
    assert captured_update[0]["body"]["update_proposal"]["command"]["duration_minutes"] == 30


def test_human_drag_resize_uses_signed_update_confirm_route(diary_page):
    """Human move/resize uses the G2 signed update-confirm route instead of raw PUT."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_proposals = []
    captured_confirms = []
    captured_raw_puts = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/appt-human-1"):
            body = request.post_data_json
            captured_proposals.append(body)
            command = {
                "appointment_id": "appt-human-1",
                "practitioner_id": body["practitioner_id"],
                "appointment_type_id": body.get("appointment_type_id"),
                "location_id": body.get("location_id"),
                "appointment_date": body["appointment_date"],
                "start_time": "2026-07-03T05:15:00Z",
                "start_time_local": body["start_time_local"],
                "duration_minutes": body["duration_minutes"],
                "reason": body.get("reason") or "",
                "notes": None,
                "patient_id": body.get("patient_id"),
                "patient_name_provisional": body.get("patient_name_provisional"),
            }
            proposal = {
                "intent": "update_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Update booking for linked patient to 2026-07-03 at 15:15, 15 min.",
                "command": command,
                "warnings": [],
                "blocks": [],
                "conflict": None,
                "breaks_overlap": [],
                "patient_identity": "linked",
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "update_proposal": proposal,
                        "confirmed_warnings": [],
                        "update_proposal_freshness_id": "human-fresh-1",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "bernie_confirm_update_proposal",
                            "payload": {"fixture": "human-move"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                    "update_proposal_freshness_id": "human-fresh-1",
                    "signed_confirmation_evidence_required": True,
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "bernie_confirm_update_proposal",
                        "payload": {"fixture": "human-move"},
                        "signature": "signed",
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/confirm"):
            captured_confirms.append({
                "body": request.post_data_json,
                "idempotency_key": request.headers.get("idempotency-key"),
            })
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_update_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Updated.",
                    "appointment": {"id": "appt-human-1", "start_time_local": "15:15:00", "duration_minutes": 15},
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["bernie_confirm_update_proposal"],
                }),
            )
            return
        if request.method == "PUT" and request.url.endswith("/appointments/appt-human-1"):
            captured_raw_puts.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw PUT should not be used"}))
            return
        route.continue_()

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              isSmokeMode = () => false;
              diaryDate = new Date(2026, 6, 3);
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera"
                }]
              };
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              activeAppointments = [{
                id: "appt-human-1",
                appointment_date: "2026-07-03",
                start_time_local: "15:00:00",
                duration_minutes: 15,
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson" },
                practitioner_id: "practitioner-123",
                practitioner: { id: "practitioner-123", first_name: "Alex", last_name: "Shera", ahpra_number: "MED0001234567" },
                appointment_type_id: "type-1",
                location_id: "loc-1",
                reason: "Review",
                status: "Booked"
              }];
              window.__g2MovePromise = handleMoveResize(activeAppointments[0], 15, 0, activeTemplate.columns[0]);
            }"""
        )
        diary_page.wait_for_selector(".identity-confirm-panel", state="visible", timeout=5000)
        diary_page.get_by_text("Confirm & Save").click()
        diary_page.wait_for_function("payloads => payloads.length > 0", arg=captured_confirms, timeout=5000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_proposals, "Expected update proposal request"
    assert captured_confirms, "Expected signed update confirm request"
    assert captured_raw_puts == []
    assert captured_confirms[0]["idempotency_key"] == "update-confirm-human-fresh-1"
    assert captured_confirms[0]["body"]["confirmed"] is True
    assert captured_confirms[0]["body"]["update_proposal"]["command"]["appointment_id"] == "appt-human-1"
    assert captured_confirms[0]["body"]["update_proposal"]["command"]["start_time_local"] == "15:15"


def test_edit_modal_uses_signed_update_confirm_before_status_patch(diary_page):
    """Edit modal detail changes use the signed update-confirm route, then patch status separately."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_proposals = []
    captured_confirms = []
    captured_status_patches = []
    captured_raw_puts = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/appt-edit-1"):
            body = request.post_data_json
            captured_proposals.append(body)
            command = {
                "appointment_id": "appt-edit-1",
                "practitioner_id": body["practitioner_id"],
                "appointment_type_id": body.get("appointment_type_id"),
                "location_id": body.get("location_id"),
                "appointment_date": body["appointment_date"],
                "start_time": "2026-07-03T05:00:00Z",
                "start_time_local": body["start_time_local"],
                "duration_minutes": body["duration_minutes"],
                "reason": body.get("reason") or "",
                "notes": None,
                "patient_id": body.get("patient_id"),
                "patient_name_provisional": body.get("patient_name_provisional"),
            }
            proposal = {
                "intent": "update_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Update booking for linked patient to 2026-07-03 at 15:00, 30 min.",
                "command": command,
                "warnings": [],
                "blocks": [],
                "conflict": None,
                "breaks_overlap": [],
                "patient_identity": "linked",
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "update_proposal": proposal,
                        "confirmed_warnings": [],
                        "update_proposal_freshness_id": "edit-fresh-1",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "bernie_confirm_update_proposal",
                            "payload": {"fixture": "edit-modal"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                    "update_proposal_freshness_id": "edit-fresh-1",
                    "signed_confirmation_evidence_required": True,
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "bernie_confirm_update_proposal",
                        "payload": {"fixture": "edit-modal"},
                        "signature": "signed",
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/confirm"):
            captured_confirms.append({
                "body": request.post_data_json,
                "idempotency_key": request.headers.get("idempotency-key"),
            })
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_update_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Updated.",
                    "appointment": {"id": "appt-edit-1", "duration_minutes": 30},
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["bernie_confirm_update_proposal"],
                }),
            )
            return
        if request.method == "PATCH" and request.url.endswith("/appointments/appt-edit-1/status"):
            captured_status_patches.append(request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"id": "appt-edit-1", "status": request.post_data_json.get("status")}),
            )
            return
        if request.method == "PUT" and request.url.endswith("/appointments/appt-edit-1"):
            captured_raw_puts.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw PUT should not be used"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              diaryDate = new Date(2026, 6, 3);
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera"
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              const appt = {
                id: "appt-edit-1",
                appointment_date: "2026-07-03",
                start_time_local: "15:00:00",
                duration_minutes: 15,
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" },
                practitioner_id: "practitioner-123",
                practitioner: { id: "practitioner-123", first_name: "Alex", last_name: "Shera", ahpra_number: "MED0001234567" },
                appointment_type_id: "type-1",
                location_id: "loc-1",
                reason: "Review",
                status: "Booked"
              };
              todayAppointments = [appt];
              activeAppointments = [appt];
              openBookingModalForEdit(appt);
              document.getElementById("booking-duration").value = "30";
              document.getElementById("booking-status").value = "Arrived";
              window.__g3SavePromise = saveBooking();
            }"""
        )
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_proposals, "Expected edit modal update proposal request"
    assert captured_confirms, "Expected signed update confirm request"
    assert captured_status_patches, "Expected separate status PATCH after detail confirm"
    assert captured_raw_puts == []
    assert captured_confirms[0]["idempotency_key"] == "update-confirm-edit-fresh-1"
    assert captured_confirms[0]["body"]["confirmed"] is True
    assert captured_confirms[0]["body"]["update_proposal"]["command"]["appointment_id"] == "appt-edit-1"
    assert captured_confirms[0]["body"]["update_proposal"]["command"]["duration_minutes"] == 30
    assert captured_status_patches[0]["status"] == "Arrived"


def test_edit_modal_does_not_patch_status_when_signed_update_confirm_fails(diary_page):
    """A rejected signed detail update must stop before the separate status transition."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_confirms = []
    captured_status_patches = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/appt-edit-fail"):
            body = request.post_data_json
            proposal = {
                "intent": "update_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Update booking.",
                "command": {
                    "appointment_id": "appt-edit-fail",
                    "practitioner_id": body["practitioner_id"],
                    "appointment_type_id": body.get("appointment_type_id"),
                    "appointment_date": body["appointment_date"],
                    "start_time": "2026-07-03T05:00:00Z",
                    "start_time_local": body["start_time_local"],
                    "duration_minutes": body["duration_minutes"],
                    "reason": body.get("reason") or "",
                    "patient_id": body.get("patient_id"),
                    "patient_name_provisional": body.get("patient_name_provisional"),
                },
                "warnings": [],
                "blocks": [],
                "patient_identity": "linked",
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "update_proposal": proposal,
                        "confirmed_warnings": [],
                        "update_proposal_freshness_id": "edit-fresh-fail",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "bernie_confirm_update_proposal",
                            "payload": {"fixture": "edit-modal-fail"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/update/confirm"):
            captured_confirms.append(request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_update_appointment",
                    "safe": False,
                    "requires_confirmation": False,
                    "autonomy_tier": "blocked",
                    "summary": "Update no longer matches current diary state.",
                    "blocks": [{"code": "stale_update", "message": "Update no longer matches current diary state."}],
                    "warnings": [],
                }),
            )
            return
        if request.method == "PATCH" and request.url.endswith("/appointments/appt-edit-fail/status"):
            captured_status_patches.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "status should not be patched"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              diaryDate = new Date(2026, 6, 3);
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera"
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              const appt = {
                id: "appt-edit-fail",
                appointment_date: "2026-07-03",
                start_time_local: "15:00:00",
                duration_minutes: 15,
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" },
                practitioner_id: "practitioner-123",
                practitioner: { id: "practitioner-123", first_name: "Alex", last_name: "Shera", ahpra_number: "MED0001234567" },
                appointment_type_id: "type-1",
                location_id: "loc-1",
                reason: "Review",
                status: "Booked"
              };
              todayAppointments = [appt];
              activeAppointments = [appt];
              openBookingModalForEdit(appt);
              document.getElementById("booking-duration").value = "30";
              document.getElementById("booking-status").value = "Arrived";
              window.__g3SavePromise = saveBooking();
            }"""
        )
        diary_page.wait_for_timeout(1000)
        diary_page.wait_for_timeout(250)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_confirms, "Expected signed update confirm request"
    assert captured_status_patches == []


def test_create_modal_uses_signed_create_confirm_before_status_patch(diary_page):
    """Create modal writes through signed create-confirm, then patches non-Booked status separately."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_proposals = []
    captured_confirms = []
    captured_status_patches = []
    captured_raw_posts = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/create"):
            body = request.post_data_json
            captured_proposals.append(body)
            command = {
                "patient_id": body.get("patient_id"),
                "patient_name_provisional": body.get("patient_name_provisional"),
                "practitioner_id": body["practitioner_id"],
                "appointment_type_id": body.get("appointment_type_id"),
                "location_id": body.get("location_id"),
                "appointment_date": body["appointment_date"],
                "start_time": "2026-07-03T05:00:00Z",
                "start_time_local": body["start_time_local"],
                "duration_minutes": body["duration_minutes"],
                "reason": body.get("reason") or "",
                "notes": None,
                "booked_via": "Receptionist",
            }
            proposal = {
                "intent": "create_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Create booking.",
                "command": command,
                "warnings": [],
                "blocks": [],
                "conflict": None,
                "breaks_overlap": [],
                "patient_identity": "linked",
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "create_proposal": proposal,
                        "confirmed_warnings": [],
                        "create_proposal_freshness_id": "create-fresh-1",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "staff_confirm_create_proposal",
                            "payload": {"fixture": "create-modal"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                    "create_proposal_freshness_id": "create-fresh-1",
                    "signed_confirmation_evidence_required": True,
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "staff_confirm_create_proposal",
                        "payload": {"fixture": "create-modal"},
                        "signature": "signed",
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/create/confirm"):
            captured_confirms.append(request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_create_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Created.",
                    "appointment": {"id": "appt-create-1", "status": "Booked"},
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["staff_confirm_create_proposal"],
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments"):
            captured_raw_posts.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw POST should not be used"}))
            return
        if request.method == "PATCH" and request.url.endswith("/appointments/appt-create-1/status"):
            captured_status_patches.append(request.post_data_json)
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"id": "appt-create-1", "status": request.post_data_json.get("status")}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              diaryDate = new Date(2026, 6, 3);
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera",
                  slot_interval_minutes: 15
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              activeLocationId = "loc-1";
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              openBookingModalForCreate(activeTemplate.columns[0], "15:00");
              selectedPatient = { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" };
              document.getElementById("booking-type").value = "type-1";
              document.getElementById("booking-status").value = "Arrived";
              window.__g4SavePromise = saveBooking();
            }"""
        )
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_proposals, "Expected create proposal request"
    assert captured_confirms, "Expected signed create-confirm request"
    assert captured_raw_posts == []
    assert captured_status_patches, "Expected status PATCH after confirmed create"
    assert captured_confirms[0]["confirmed"] is True
    assert captured_confirms[0]["create_proposal"]["command"]["duration_minutes"] == 15
    assert captured_status_patches[0]["status"] == "Arrived"


def test_create_modal_does_not_patch_status_when_signed_create_confirm_fails(diary_page):
    """A rejected signed create-confirm must stop before status-after-create."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_confirms = []
    captured_status_patches = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/create"):
            body = request.post_data_json
            proposal = {
                "intent": "create_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Create booking.",
                "command": {
                    "patient_id": body.get("patient_id"),
                    "patient_name_provisional": body.get("patient_name_provisional"),
                    "practitioner_id": body["practitioner_id"],
                    "appointment_type_id": body.get("appointment_type_id"),
                    "location_id": body.get("location_id"),
                    "appointment_date": body["appointment_date"],
                    "start_time": "2026-07-03T05:00:00Z",
                    "start_time_local": body["start_time_local"],
                    "duration_minutes": body["duration_minutes"],
                    "reason": body.get("reason") or "",
                    "notes": None,
                    "booked_via": "Receptionist",
                },
                "warnings": [],
                "blocks": [],
                "patient_identity": "linked",
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "create_proposal": proposal,
                        "confirmed_warnings": [],
                        "create_proposal_freshness_id": "create-fresh-fail",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "staff_confirm_create_proposal",
                            "payload": {"fixture": "create-modal-fail"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/create/confirm"):
            captured_confirms.append(request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_create_appointment",
                    "safe": False,
                    "requires_confirmation": True,
                    "autonomy_tier": "blocked",
                    "summary": "Create no longer matches current diary state.",
                    "appointment": None,
                    "blocks": [{"code": "stale_create_proposal_freshness_id", "message": "Create no longer matches current diary state."}],
                    "warnings": [],
                }),
            )
            return
        if request.method == "PATCH" and "/appointments/" in request.url and request.url.endswith("/status"):
            captured_status_patches.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "status should not be patched"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              diaryDate = new Date(2026, 6, 3);
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera",
                  slot_interval_minutes: 15
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              activeLocationId = "loc-1";
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              openBookingModalForCreate(activeTemplate.columns[0], "15:00");
              selectedPatient = { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" };
              document.getElementById("booking-type").value = "type-1";
              document.getElementById("booking-status").value = "Arrived";
              window.__g4SavePromise = saveBooking();
            }"""
        )
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_confirms, "Expected signed create-confirm request"
    assert captured_status_patches == []


def test_status_control_uses_signed_status_confirm_without_raw_patch(diary_page):
    """Status-only controls write through signed status-confirm when evidence is present."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_proposals = []
    captured_confirms = []
    captured_raw_patches = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/status/appt-status-1"):
            body = request.post_data_json
            captured_proposals.append(body)
            proposal = {
                "intent": "update_appointment_status",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "execute_with_report",
                "summary": "Change status.",
                "command": {
                    "appointment_id": "appt-status-1",
                    "status": body["status"],
                    "waiting_area_id": body.get("waiting_area_id"),
                    "waiting_area_id_supplied": "waiting_area_id" in body,
                    "clears_waiting_area": False,
                },
                "warnings": [],
                "blocks": [],
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/status-confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "status_proposal": proposal,
                        "confirmed_warnings": [],
                        "status_proposal_freshness_id": "status-fresh-1",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "diary_confirm_status_proposal",
                            "payload": {"fixture": "status-control"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                    "status_proposal_freshness_id": "status-fresh-1",
                    "signed_confirmation_evidence_required": True,
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "diary_confirm_status_proposal",
                        "payload": {"fixture": "status-control"},
                        "signature": "signed",
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/status-confirm"):
            captured_confirms.append(request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_status_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Updated.",
                    "appointment": {
                        "id": "appt-status-1",
                        "status": "Arrived",
                        "waiting_area_id": None,
                    },
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["diary_confirm_status_proposal"],
                }),
            )
            return
        if request.method == "PATCH" and request.url.endswith("/appointments/appt-status-1/status"):
            captured_raw_patches.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw PATCH should not be used"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              const appt = {
                id: "appt-status-1",
                status: "Booked",
                waiting_area_id: null,
                patient_id: "patient-123",
                patient: { first_name: "Margaret", last_name: "Thompson" }
              };
              window.__g5StatusPromise = setAppointmentStatus(appt, "Arrived");
            }"""
        )
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_proposals, "Expected status proposal request"
    assert captured_confirms, "Expected signed status-confirm request"
    assert captured_confirms[0]["confirmed"] is True
    assert captured_confirms[0]["status_proposal"]["command"]["status"] == "Arrived"
    assert captured_raw_patches == []


def test_status_control_failed_signed_confirm_does_not_raw_patch(diary_page):
    """A rejected signed status-confirm must not fall back to raw PATCH."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_confirms = []
    captured_confirm_keys = []
    captured_raw_patches = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/status/appt-status-fail"):
            proposal = {
                "intent": "update_appointment_status",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "execute_with_report",
                "summary": "Change status.",
                "command": {
                    "appointment_id": "appt-status-fail",
                    "status": "Arrived",
                    "waiting_area_id": None,
                    "waiting_area_id_supplied": False,
                    "clears_waiting_area": False,
                },
                "warnings": [],
                "blocks": [],
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/status-confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "status_proposal": proposal,
                        "confirmed_warnings": [],
                        "status_proposal_freshness_id": "status-fresh-fail",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "diary_confirm_status_proposal",
                            "payload": {"fixture": "status-control-fail"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/status-confirm"):
            captured_confirms.append(request.post_data_json)
            captured_confirm_keys.append(request.headers.get("idempotency-key"))
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_status_appointment",
                    "safe": False,
                    "requires_confirmation": True,
                    "autonomy_tier": "blocked",
                    "summary": "Status proposal is stale.",
                    "appointment": None,
                    "warnings": [],
                    "blocks": [{"code": "stale_status_proposal_freshness_id", "message": "Status proposal is stale."}],
                    "audit_evidence": [],
                }),
            )
            return
        if request.method == "PATCH" and request.url.endswith("/appointments/appt-status-fail/status"):
            captured_raw_patches.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw PATCH should not be used"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              const appt = {
                id: "appt-status-fail",
                status: "Booked",
                waiting_area_id: null,
                patient_id: "patient-123",
                patient: { first_name: "Margaret", last_name: "Thompson" }
              };
              window.__g5StatusPromise = setAppointmentStatus(appt, "Arrived");
            }"""
        )
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_confirms, "Expected signed status-confirm request"
    assert captured_confirm_keys == ["status-confirm-status-fresh-fail"]
    assert captured_raw_patches == []


def test_cancel_flow_uses_signed_delete_confirm_without_raw_delete(diary_page):
    """Appointment cancel posts signed delete-confirm when proposal evidence is present."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_proposals = []
    captured_confirms = []
    captured_confirm_keys = []
    captured_raw_deletes = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/delete/appt-delete-1"):
            body = request.post_data_json
            captured_proposals.append(body)
            proposal = {
                "intent": "delete_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Cancel and remove Margaret Thompson's appointment.",
                "command": {
                    "appointment_id": "appt-delete-1",
                    "clears_waiting_area": True,
                    "cancellation_reason": body.get("cancellation_reason"),
                },
                "warnings": [{
                    "code": "waiting_area_cleared",
                    "severity": "warning",
                    "message": "Deleting this appointment will remove the patient from the waiting area.",
                }],
                "blocks": [],
            }
            signed_evidence = {
                "schema_version": "bernie.confirmation_evidence.v1",
                "purpose": "diary_confirm_delete_proposal",
                "payload": {"fixture": "delete-control"},
                "signature": "signed",
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/delete-confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "delete_proposal": proposal,
                        "confirmed_warnings": ["waiting_area_cleared"],
                        "delete_proposal_freshness_id": "delete-fresh-1",
                        "signed_confirmation_evidence": signed_evidence,
                        "signed_confirmation_evidence_required": True,
                    },
                    "delete_proposal_freshness_id": "delete-fresh-1",
                    "signed_confirmation_evidence_required": True,
                    "signed_confirmation_evidence": signed_evidence,
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/delete-confirm"):
            captured_confirms.append(request.post_data_json)
            captured_confirm_keys.append(request.headers.get("idempotency-key"))
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_delete_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Cancelled.",
                    "appointment": {
                        "id": "appt-delete-1",
                        "status": "Cancelled",
                        "waiting_area_id": None,
                        "cancellation_reason": "Patient had transport issues",
                    },
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": [
                        "diary_confirm_delete_proposal",
                        "delete_signed_confirmation_evidence_verified",
                    ],
                }),
            )
            return
        if request.method == "DELETE" and request.url.endswith("/appointments/appt-delete-1"):
            captured_raw_deletes.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw DELETE should not be used"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps([]))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera",
                  slot_interval_minutes: 15
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              const appt = {
                id: "appt-delete-1",
                status: "Booked",
                waiting_area_id: "area-1",
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" },
                practitioner: { id: "practitioner-123", first_name: "Alex", last_name: "Shera", ahpra_number: "MED0001234567" },
                practitioner_id: "practitioner-123",
                appointment_type_id: "type-1",
                appointment_date: "2026-07-03",
                start_time_local: "09:00:00",
                duration_minutes: 15,
                reason: "Follow-up"
              };
              todayAppointments = [appt];
              openBookingModalForEdit(appt);
            }"""
        )
        diary_page.click("#btn-booking-delete")
        diary_page.fill("#booking-cancel-reason", "Patient had transport issues")
        diary_page.select_option("[data-testid='booking-status-reason-code']", "PATIENT_TRANSPORT")
        diary_page.click("#btn-booking-delete")
        diary_page.wait_for_selector(".identity-confirm-overlay", state="visible", timeout=5000)
        diary_page.click(".identity-confirm-overlay button:has-text('Confirm & Save')")
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_proposals, "Expected delete proposal request"
    assert captured_proposals[0]["cancellation_reason"] == "Patient had transport issues"
    assert captured_proposals[0]["status_reason_code"] == "PATIENT_TRANSPORT"
    assert captured_confirms, "Expected signed delete-confirm request"
    assert captured_confirm_keys == ["delete-confirm-delete-fresh-1"]
    assert captured_confirms[0]["confirmed"] is True
    assert captured_confirms[0]["delete_proposal"]["command"]["cancellation_reason"] == "Patient had transport issues"
    assert captured_raw_deletes == []


def test_cancel_flow_failed_signed_confirm_does_not_raw_delete(diary_page):
    """A rejected signed delete-confirm must not fall back to raw DELETE."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_confirms = []
    captured_raw_deletes = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/delete/appt-delete-fail"):
            proposal = {
                "intent": "delete_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Cancel and remove Margaret Thompson's appointment.",
                "command": {
                    "appointment_id": "appt-delete-fail",
                    "clears_waiting_area": False,
                    "cancellation_reason": "Patient had transport issues",
                    "status_reason_code": "PATIENT_TRANSPORT",
                },
                "warnings": [],
                "blocks": [],
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    **proposal,
                    "confirm_endpoint": "/api/v1/appointments/proposals/delete-confirm",
                    "confirm_payload": {
                        "confirmed": False,
                        "delete_proposal": proposal,
                        "confirmed_warnings": [],
                        "delete_proposal_freshness_id": "delete-fresh-fail",
                        "signed_confirmation_evidence": {
                            "schema_version": "bernie.confirmation_evidence.v1",
                            "purpose": "diary_confirm_delete_proposal",
                            "payload": {"fixture": "delete-control-fail"},
                            "signature": "signed",
                        },
                        "signed_confirmation_evidence_required": True,
                    },
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/delete-confirm"):
            captured_confirms.append(request.post_data_json)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "confirm_delete_appointment",
                    "safe": False,
                    "requires_confirmation": True,
                    "autonomy_tier": "blocked",
                    "summary": "Delete proposal is stale.",
                    "appointment": None,
                    "warnings": [],
                    "blocks": [{"code": "stale_delete_proposal_freshness_id", "message": "Delete proposal is stale."}],
                    "audit_evidence": [],
                }),
            )
            return
        if request.method == "DELETE" and request.url.endswith("/appointments/appt-delete-fail"):
            captured_raw_deletes.append(request.post_data_json)
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "raw DELETE should not be used"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps([]))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera",
                  slot_interval_minutes: 15
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              const appt = {
                id: "appt-delete-fail",
                status: "Booked",
                waiting_area_id: null,
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" },
                practitioner: { id: "practitioner-123", first_name: "Alex", last_name: "Shera", ahpra_number: "MED0001234567" },
                practitioner_id: "practitioner-123",
                appointment_type_id: "type-1",
                appointment_date: "2026-07-03",
                start_time_local: "09:00:00",
                duration_minutes: 15,
                reason: "Follow-up"
              };
              todayAppointments = [appt];
              openBookingModalForEdit(appt);
            }"""
        )
        diary_page.click("#btn-booking-delete")
        diary_page.fill("#booking-cancel-reason", "Patient had transport issues")
        diary_page.select_option("[data-testid='booking-status-reason-code']", "PATIENT_TRANSPORT")
        diary_page.click("#btn-booking-delete")
        diary_page.wait_for_selector(".identity-confirm-overlay", state="visible", timeout=5000)
        diary_page.click(".identity-confirm-overlay button:has-text('Confirm & Save')")
        diary_page.wait_for_timeout(1000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured_confirms, "Expected signed delete-confirm request"
    assert captured_confirms[0]["confirmed"] is True
    assert captured_raw_deletes == []


def test_bernie_tool_intent_clarification_has_no_confirm_or_stale_no_slot(diary_page):
    """Incomplete tool-intent responses render as clarification, not stale booking/no-slot UI."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/bernie/tool-intent"):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "bernie_tool_intent",
                    "safe": False,
                    "result": "clarification_required",
                    "tool_intent": "extend_appointment",
                    "autonomy_tier": "blocked",
                    "requires_confirmation": False,
                    "summary": "I need the new appointment duration before I can prepare that change.",
                    "proposal": None,
                    "warnings": [],
                    "blocks": [{
                        "code": "target_duration_required",
                        "severity": "blocked",
                        "message": "Tell me the total appointment duration, for example 30 minutes.",
                    }],
                    "source_attribution": {"write_authority": "none"},
                }),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/bernie/interpret-booking-instruction"):
            route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected booking interpreter"}))
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              const contentEl = document.getElementById("bernie-review-content");
              contentEl.innerHTML = "";
              contentEl.innerHTML = '<div data-testid="bernie-review-candidates-empty">I could not find matching free times in that window.</div>';
              renderBernieInstructionInput(contentEl);
            }"""
        )

        diary_page.fill("[data-testid='bernie-instruction-input']", "Bernie extend Margaret Thompson's booking.")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector("[data-testid='bernie-tool-intent-issue']", state="visible", timeout=5000)

        panel_text = diary_page.locator("[data-testid='bernie-review-panel']").text_content()
        assert "Tell me the total appointment duration" in panel_text
        assert "I could not find matching free times in that window" not in panel_text
        assert diary_page.locator("[data-testid='bernie-tool-intent-proposal']").count() == 0
        assert diary_page.locator("[data-testid='btn-bernie-tool-intent-confirm']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_new_staff_instruction_reanchors_to_visible_diary_date(diary_page):
    """A new instruction should use the visible diary date, not a stale session date."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured = []

    def handle_api(route):
        request = route.request
        if (
            request.method == "POST"
            and request.url.endswith("/appointments/proposals/bernie/interpret-booking-instruction")
        ):
            body = request.post_data_json
            captured.append(body)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "intent": "interpret_booking_instruction",
                    "safe": False,
                    "result": "clarification_required",
                    "autonomy_tier": "blocked",
                    "summary": "Need one more detail.",
                    "confidence": 0.8,
                    "request_reference_date": body["reference_date"],
                    "command_candidate": None,
                    "missing_fields": ["date_from"],
                    "safety_flags": [],
                    "clarifying_question": "Which day should I check?",
                    "normalization": None,
                    "warnings": [],
                    "blocks": [],
                    "provider_metadata": {"provider": "fake", "mode": "mocked", "live_provider": False},
                    "confidence_axes": [],
                    "decision": None,
                    "assumptions": [],
                    "staff_checks": [],
                    "patient_candidates": [],
                    "debug": None,
                    "patient_booking_context": None,
                    "context_freshness": None,
                    "turn_ref": {
                        "session_id": "s-visible",
                        "turn_id": "s-visible:0",
                        "turn_index": 0,
                        "event_kind": "staff_instruction",
                        "reference_date": body["reference_date"],
                    },
                }),
            )
            return
        route.continue_()

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_reanchor_visible_date=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        diary_page.evaluate(
            """() => {
              diaryDate = new Date(2026, 6, 3);
              bernieSession.referenceDate = "2026-07-02";
              bernieSession.turnRef = {
                session_id: "stale-session",
                turn_id: "stale-session:4",
                turn_index: 4,
                event_kind: "candidate_selection",
                reference_date: "2026-07-02"
              };
              isBerniePilotActive = true;
              const contentEl = document.getElementById("bernie-review-content");
              contentEl.innerHTML = "";
              renderBernieInstructionInput(contentEl);
            }"""
        )
        textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        textarea.fill("Make an appointment for Margaret Thompson with Dr Shera after 3 tomorrow and before 4.30")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_function("captured => captured.length > 0", arg=captured, timeout=3000)
    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

    assert captured, "Expected interpret request"
    assert captured[0]["reference_date"] == "2026-07-03"
    assert "turn_ref" not in captured[0]


def test_bernie_reception_policy_roster_unavailable(diary_page):
    """Roster unavailable mapped state should render appropriate status, headline, action and empty message."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [],
                reception_policy: {
                  availability: "roster_unavailable",
                  roster_unavailable: true,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        action_text = diary_page.locator("[data-testid='bernie-review-action']").text_content().strip()
        empty_text = diary_page.locator("[data-testid='bernie-review-candidates-empty']").text_content().strip()

        assert status_text == "Roster/schedule unavailable"
        assert headline_text == "Roster/schedule unavailable"
        assert "I could not find a bookable session for that request" in action_text
        assert "There is no bookable session configured for that request" in empty_text

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_outcome_reason_codes_drive_roster_copy(diary_page):
    """Typed outcome reason codes should drive roster copy even before legacy issue fallback."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [],
                outcome: {
                  kind: "roster_unavailable",
                  family: "roster_gap",
                  session_state: "no_slot",
                  requires_confirmation: false,
                  can_confirm: false,
                  is_terminal: false,
                  reason_codes: ["slot_search_skipped_no_schedule"],
                  basis: "No roster row exists."
                },
                reception_policy: {
                  availability: "roster_unavailable",
                  roster_unavailable: true,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        empty_text = diary_page.locator("[data-testid='bernie-review-candidates-empty']").text_content().strip()

        assert status_text == "Roster unavailable"
        assert headline_text == "No roster found"
        assert empty_text == "Check the practitioner's roster or choose another day."

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_outcome_schedule_explanation_payload_drives_copy(diary_page):
    """Typed display-only schedule explanation payload drives copy without issue fallbacks."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [],
                outcome: {
                  kind: "roster_unavailable",
                  family: "roster_gap",
                  session_state: "no_slot",
                  requires_confirmation: false,
                  can_confirm: false,
                  is_terminal: false,
                  reason_codes: [],
                  basis: "No roster row exists.",
                  schedule_explanation: {
                    reason_code: "outside_request_window",
                    title: "Requested time is outside rostered hours",
                    staff_prompt: "Choose a time within the practitioner's rostered hours.",
                    authority: "display_only"
                  }
                },
                reception_policy: {
                  availability: "roster_unavailable",
                  roster_unavailable: true,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        empty_text = diary_page.locator("[data-testid='bernie-review-candidates-empty']").text_content().strip()

        assert status_text == "Outside hours"
        assert headline_text == "Requested time is outside rostered hours"
        assert empty_text == "Choose a time within the practitioner's rostered hours."

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_search_ran_no_candidates(diary_page):
    """True search_ran_no_candidates shows matching free times unavailable messages."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "candidate_selection_required",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [],
                reception_policy: {
                  availability: "search_ran_no_candidates",
                  roster_unavailable: false,
                  can_offer_candidates: false,
                  search_ran_no_candidates: true
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        action_text = diary_page.locator("[data-testid='bernie-review-action']").text_content().strip()

        assert status_text == "Try another time"
        assert headline_text == "No matching times found"
        assert "I could not find matching free times in that window" in action_text

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_search_ran_no_candidates_false(diary_page):
    """When search_ran_no_candidates is false, no 'no matching times' copy appears."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [{ code: "missing_practitioner_id", message: "Missing practitioner" }],
                reception_policy: {
                  availability: "blocked",
                  roster_unavailable: false,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        action_text = diary_page.locator("[data-testid='bernie-review-action']").text_content().strip()

        assert "Try another time" not in status_text
        assert "No matching times found" not in headline_text
        assert "I could not find matching free times in that window" not in action_text

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_advisory_future_bookings(diary_page):
    """Advisory future bookings must still show candidates list successfully."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_auto_preview=false")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "candidate_selection_required",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [
                  {
                    appointment_date: "2026-06-27",
                    start_time_local: "09:00:00",
                    duration_minutes: 15,
                    warnings: []
                  }
                ],
                warnings: [{
                  code: "existing_future_follow_up",
                  severity: "warning",
                  message: "Patient already has a future booking."
                }],
                blocks: [],
                reception_policy: {
                  availability: "search_ran_with_candidates",
                  roster_unavailable: false,
                  can_offer_candidates: true,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        # Verify candidate item is visible
        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-candidate-item']").text_content()

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_legacy_fallback(diary_page):
    """Legacy response without reception_policy fallback rules should behave correctly for roster unavailable."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        # Legacy payload lacks reception_policy, has no_practitioner_schedule block
        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [{ code: "no_practitioner_schedule", message: "No practitioner schedule" }]
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        empty_text = diary_page.locator("[data-testid='bernie-review-candidates-empty']").text_content().strip()

        assert status_text == "Roster/schedule unavailable"
        assert headline_text == "Roster/schedule unavailable"
        assert "There is no bookable session configured for that request" in empty_text

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_clarification(diary_page):
    """Clarification required state should render appropriate status, headline, and action copy."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [],
                clarifying_question: "Which day next week did you want to book?",
                reception_policy: {
                  availability: "blocked",
                  must_ask_clarification: true,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        action_text = diary_page.locator("[data-testid='bernie-review-action']").text_content().strip()

        assert status_text == "Clarification required"
        assert headline_text == "Clarification required"
        assert action_text == "Which day next week did you want to book?"

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_advisory_warnings_only(diary_page):
    """Advisory warnings only allows confirmation and shows confirm button."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "confirmation_ready",
                confirmation_ready: true,
                selected_slot: {
                  appointment_date: "2026-07-06",
                  start_time_local: "10:00:00",
                  duration_minutes: 15,
                  practitioner_id: "e44d3200-9ef2-4ab8-912f-b4df4492bfd4",
                  patient_id: "a33d3200-9ef2-4ab8-912f-b4df4492bfd4"
                },
                candidate_slots: [],
                warnings: [{ code: "existing_future_follow_up", message: "Patient has future booking." }],
                blocks: [],
                confirm_payload: {
                  selection_proposal: {
                    selected_candidate: {
                      appointment_date: "2026-07-06",
                      start_time_local: "10:00:00"
                    }
                  }
                },
                confirm_affordance: {
                  can_show_confirm_ui: true,
                  confirm_grade_allowed: true
                },
                reception_policy: {
                  availability: "search_ran_with_candidates",
                  must_ask_clarification: false,
                  must_block_confirmation: false,
                  advisory_warnings_only: true,
                  can_offer_candidates: true,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        assert status_text == "Ready to book"
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").is_enabled()

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_advisory_outcome_without_slot_does_not_become_blocked(diary_page):
    """Advisory-only is a warning state, not a generic blocked/no-slot state."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [{ code: "existing_future_follow_up", message: "Patient has a future booking." }],
                blocks: [],
                outcome: {
                  kind: "advisory_warnings_present",
                  family: "advisory",
                  session_state: "context_enrichment",
                  requires_confirmation: false,
                  can_confirm: false,
                  is_terminal: false,
                  reason_codes: ["existing_future_follow_up"],
                  basis: "Only advisory warnings are present."
                },
                reception_policy: {
                  availability: "not_evaluated",
                  must_ask_clarification: false,
                  must_block_confirmation: false,
                  advisory_warnings_only: true,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        status_text = diary_page.locator("[data-testid='bernie-review-status']").text_content().strip()
        headline_text = diary_page.locator("[data-testid='bernie-review-headline']").text_content().strip()
        action_text = diary_page.locator("[data-testid='bernie-review-action']").text_content().strip()

        assert status_text == "Ready to book"
        assert headline_text == "Ready to book this appointment"
        assert "Add the missing details" not in action_text
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_practice_reference_renders_without_confirm_authority(diary_page):
    """Practice-knowledge frames render as reference cards and cannot create confirm UI."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "blocked",
                confirmation_ready: false,
                selected_slot: null,
                candidate_slots: [],
                warnings: [],
                blocks: [],
                reception_context: {
                  schema_version: "bernie.reception_context.v1",
                  reference_date: "2026-07-03",
                  frames: [{
                    frame_type: "advisory_warning",
                    status: "advisory",
                    source: "server_resolver",
                    basis: "practice_knowledge_retrieval",
                    reference_date: "2026-07-03",
                    reason_code: "practice_knowledge_retrieval",
                    payload: {
                      schema_version: "practice.knowledge.result.v1",
                      retrieval_basis: "deterministic_in_memory",
                      staff_copy: "[policy] New patient appointment duration: New patient appointments are 30 minutes.",
                      advisory_only: true,
                      cannot_affect_slots: true,
                      cannot_affect_policy: true,
                      cannot_affect_confirm: true,
                      fact_snapshots: [{
                        fact_id: "policy-001",
                        kind: "policy",
                        subject: "New patient appointment duration",
                        body: "New patient appointments are 30 minutes. Standard follow-up appointments are 15 minutes.",
                        match_basis: "body_keyword",
                        rank: 1,
                        provenance: {
                          source_kind: "staff_authored",
                          source_ref: "booking-policy-2026",
                          author: "dr.shera@emr4dev.local",
                          review_status: "current"
                        }
                      }]
                    }
                  }]
                },
                reception_policy: {
                  availability: "not_evaluated",
                  must_ask_clarification: false,
                  must_block_confirmation: false,
                  advisory_warnings_only: true,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                },
                outcome: {
                  kind: "advisory_warnings_present",
                  family: "advisory",
                  session_state: "context_enrichment",
                  requires_confirmation: false,
                  can_confirm: false,
                  is_terminal: false,
                  reason_codes: ["practice_knowledge_retrieval"],
                  basis: "Only advisory warnings are present."
                }
              });
            }"""
        )

        assert diary_page.locator("[data-testid='bernie-practice-reference']").count() == 1
        assert "New patient appointment duration" in diary_page.locator("[data-testid='bernie-practice-reference']").text_content()
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-candidates-empty']").count() == 0

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_context_frames_include_visible_appointment_id(diary_page):
    """Visible diary booking frames expose appointment ids for typed tool intents."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="attached", timeout=5000)

        frame = diary_page.evaluate(
            """() => {
              const visibleDate = localDateKey(diaryDate);
              activeAppointments = [{
                id: "appt-visible-123",
                appointment_date: visibleDate,
                start_time_local: "15:00:00",
                duration_minutes: 15,
                patient_id: "patient-123",
                patient: { id: "patient-123", first_name: "Margaret", last_name: "Thompson" },
                practitioner_id: "practitioner-123",
                practitioner: { first_name: "Alex", last_name: "Shera" },
                status: "Booked"
              }];
              const frames = buildBernieContextFrames({ command: {} });
              return frames.find(item => item.type === "diary_day_booking");
            }"""
        )

        assert frame["appointment_id"] == "appt-visible-123"
        assert frame["patient_label"] == "Margaret Thompson"

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_confirmation_ready_without_confirm_evidence_hides_confirm(diary_page):
    """Friendly/status payloads cannot create a confirm affordance without backend evidence."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "confirmation_ready",
                confirmation_ready: true,
                selected_slot: {
                  appointment_date: "2026-07-06",
                  start_time_local: "10:00:00",
                  duration_minutes: 15,
                  practitioner_id: "e44d3200-9ef2-4ab8-912f-b4df4492bfd4",
                  patient_id: "a33d3200-9ef2-4ab8-912f-b4df4492bfd4"
                },
                candidate_slots: [],
                warnings: [],
                blocks: [],
                outcome: {
                  kind: "confirmation_ready",
                  family: "proceed",
                  session_state: "proposal_preview",
                  requires_confirmation: true,
                  can_confirm: true,
                  is_terminal: false,
                  reason_codes: [],
                  basis: "Display-only test"
                },
                reception_policy: {
                  availability: "search_ran_with_candidates",
                  must_ask_clarification: false,
                  must_block_confirmation: false,
                  advisory_warnings_only: false,
                  can_offer_candidates: true,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_stale_conflict_disables_confirm(diary_page):
    """When stale conflict is present in reception policy, confirmation is blocked."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "confirmation_ready",
                confirmation_ready: true,
                selected_slot: {
                  appointment_date: "2026-07-06",
                  start_time_local: "10:00:00",
                  duration_minutes: 15,
                  practitioner_id: "e44d3200-9ef2-4ab8-912f-b4df4492bfd4",
                  patient_id: "a33d3200-9ef2-4ab8-912f-b4df4492bfd4"
                },
                candidate_slots: [],
                warnings: [],
                blocks: [],
                reception_policy: {
                  availability: "blocked",
                  must_ask_clarification: false,
                  must_block_confirmation: true,
                  advisory_warnings_only: false,
                  can_offer_candidates: false,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_reception_policy_no_phi_in_storage(diary_page):
    """Ensure that loading Bernie review panel leaves zero PHI in localStorage/sessionStorage."""
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        diary_page.evaluate(
            """() => {
              isBerniePilotActive = true;
              renderBernieReview({
                status: "confirmation_ready",
                confirmation_ready: true,
                selected_slot: {
                  appointment_date: "2026-07-06",
                  start_time_local: "10:00:00",
                  duration_minutes: 15,
                  practitioner_id: "e44d3200-9ef2-4ab8-912f-b4df4492bfd4",
                  patient_id: "a33d3200-9ef2-4ab8-912f-b4df4492bfd4"
                },
                patient_evidence: {
                  patient_id: "a33d3200-9ef2-4ab8-912f-b4df4492bfd4",
                  first_name: "John",
                  last_name: "Doe",
                  date_of_birth: "1980-01-01"
                },
                candidate_slots: [],
                warnings: [],
                blocks: [],
                reception_policy: {
                  availability: "search_ran_with_candidates",
                  must_ask_clarification: false,
                  must_block_confirmation: false,
                  advisory_warnings_only: true,
                  can_offer_candidates: true,
                  search_ran_no_candidates: false
                }
              });
            }"""
        )

        storage_values = diary_page.evaluate(
            """() => {
                const values = [];
                for (let i = 0; i < localStorage.length; i += 1) {
                    const key = localStorage.key(i);
                    if (key !== 'emr4_token') {
                        values.push(localStorage.getItem(key));
                    }
                }
                for (let i = 0; i < sessionStorage.length; i += 1) {
                    values.push(sessionStorage.getItem(sessionStorage.key(i)));
                }
                return values.join("\\n");
            }"""
        )
        assert "John" not in storage_values
        assert "Doe" not in storage_values
        assert "1980-01-01" not in storage_values

    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


@pytest.mark.parametrize(
    "provider_info,expected_text",
    [
        (
            {"provider": "fake", "mode": "mocked", "live_provider": False},
            "Provider: fake (mode: mocked; live_provider: false)",
        ),
        (
            {"provider": "gemini_vertex", "mode": "live", "live_provider": True},
            "Provider: gemini_vertex (mode: live; live_provider: true)",
        ),
    ],
)
def test_bernie_debug_provider_metadata_honest(diary_page, provider_info, expected_text):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    mock_interpret = {
        "intent": "interpret_booking_instruction",
        "safe": True,
        "result": "interpreted",
        "autonomy_tier": "execute_with_report",
        "summary": "Find a 15 minute follow-up for this patient with prac-1 today.",
        "confidence": 0.9,
        "command_candidate": {
            "practitioner_id": "prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "today",
            "duration_minutes": "15"
        },
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
        "normalization": {
            "safe": True,
            "constraint": {
                "practitioner_id": "prac-1",
                "patient_id": "smoke-pat-1",
                "date_from": "2026-06-27",
                "duration_minutes": 15
            },
            "warnings": [],
            "blocks": [],
            "summary": "Normalized successfully."
        },
        "warnings": [],
        "blocks": [],
        "provider_metadata": provider_info
    }

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret)
        )
    )

    try:
        # Navigate with bernie_debug=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_interpret=true&bernie_debug=true&practitioner_id=prac-1&patient_id=smoke-pat-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, "Find time for patient", register_default_mock=False)

        # Wait for the preview and check provider info
        diary_page.wait_for_selector("[data-testid='bernie-interpret-preview']", state="visible", timeout=5000)
        provider_el = diary_page.locator("[data-testid='bernie-interpret-provider']")
        provider_el.wait_for(state="visible", timeout=5000)

        assert provider_el.text_content().strip() == expected_text

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_create_proposal_idempotency_header(diary_page):
    """Verify that create-proposal POST carries an 8+ character Idempotency-Key header,
    keeps it stable during confirm/warning retries, and changes it when inputs are modified.
    """
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    captured_keys = []
    captured_confirm_keys = []

    def handle_api(route):
        request = route.request
        if request.method == "POST" and request.url.endswith("/appointments/proposals/create/confirm"):
            captured_confirm_keys.append(request.headers.get("idempotency-key"))
            route.fulfill(
                status=500,
                content_type="application/json",
                body=json.dumps({"detail": "captured confirm header"}),
            )
            return
        if request.method == "POST" and request.url.endswith("/appointments/proposals/create"):
            key = request.headers.get("idempotency-key")
            captured_keys.append(key)

            body = request.post_data_json
            command = {
                "patient_id": body.get("patient_id"),
                "patient_name_provisional": body.get("patient_name_provisional"),
                "practitioner_id": body["practitioner_id"],
                "appointment_type_id": body.get("appointment_type_id"),
                "location_id": body.get("location_id"),
                "appointment_date": body["appointment_date"],
                "start_time": "2026-07-03T05:00:00Z",
                "start_time_local": body["start_time_local"],
                "duration_minutes": body["duration_minutes"],
                "reason": body.get("reason") or "",
                "notes": None,
                "booked_via": "Receptionist",
            }
            proposal = {
                "intent": "create_appointment",
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "Create booking.",
                "command": command,
                "warnings": [{"code": "overlapping_break", "message": "Overlaps with break"}],
                "blocks": [],
                "conflict": None,
                "breaks_overlap": [],
                "patient_identity": "linked",
                "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm",
                "confirm_payload": {
                    "confirmed": False,
                    "create_proposal": {"command": command},
                    "create_proposal_freshness_id": "fresh-create-smoke",
                    "confirmed_warnings": [],
                    "signed_confirmation_evidence": {
                        "scheme": "emr4-hmac-sha256-v1",
                        "signature": "signed",
                    },
                },
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(proposal),
            )
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True}))

    try:
        diary_page.route("**/api/v1/**", handle_api)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true")
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)

        # Open create modal and fill details
        diary_page.evaluate(
            """() => {
              history.replaceState(null, "", "/diary/diary.html");
              diaryDate = new Date(2026, 6, 3);
              activeTemplate = {
                columns: [{
                  practitioner_ahpra: "MED0001234567",
                  room_label: "Room 1",
                  assignment: "Dr Alex Shera",
                  slot_interval_minutes: 15
                }],
                slot_defaults: { interval_minutes: 15 }
              };
              activeTypes = [{ id: "type-1", name: "Standard", default_duration: 15 }];
              activeLocationId = "loc-1";
              ahpraToPractitionerMap["MED0001234567"] = {
                id: "practitioner-123",
                first_name: "Alex",
                last_name: "Shera",
                ahpra_number: "MED0001234567"
              };
              openBookingModalForCreate(activeTemplate.columns[0], "15:00");
              selectedPatient = { id: "patient-123", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" };
              document.getElementById("booking-type").value = "type-1";
            }"""
        )

        # First save attempt: will trigger warning, button changes to 'Confirm & Save'
        diary_page.click("#btn-booking-save")
        diary_page.wait_for_timeout(500)

        # Verify first call key is valid
        assert len(captured_keys) == 1
        key1 = captured_keys[0]
        assert key1 is not None
        assert len(key1) >= 8

        # Second save attempt (confirming warning, no input change): key must be stable
        diary_page.click("#btn-booking-save")
        diary_page.wait_for_timeout(500)

        assert len(captured_keys) == 2
        key2 = captured_keys[1]
        assert key2 == key1, "Idempotency-Key should be stable for the same proposal attempt"
        assert len(captured_confirm_keys) == 1
        confirm_key = captured_confirm_keys[0]
        assert confirm_key is not None
        assert len(confirm_key) >= 8
        assert confirm_key != key1, "Confirm Idempotency-Key should be distinct from proposal key"

        # Now simulate changing input field to reset proposal confirmation and clear key
        diary_page.evaluate(
            """() => {
              const reasonInput = document.getElementById("booking-reason");
              reasonInput.value = "New reason";
              // Dispatch input event to trigger resetProposalConfirmation
              reasonInput.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        diary_page.wait_for_timeout(200)

        # Third save attempt after input change: key must change
        diary_page.click("#btn-booking-save")
        diary_page.wait_for_timeout(500)

        assert len(captured_keys) == 3
        key3 = captured_keys[2]
        assert key3 is not None
        assert len(key3) >= 8
        assert key3 != key1, "Idempotency-Key should be refreshed when input changes"

    finally:
        diary_page.unroute("**/api/v1/**", handle_api)
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
