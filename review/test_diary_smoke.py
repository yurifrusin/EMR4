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
        assert status.text_content().strip() == "blocked"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Booking Blocked"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Blocked review payload" in action.text_content()

        # Verify block issues list
        assert diary_page.locator("[data-testid='bernie-review-blocks-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="missing_practitioner_id").count() == 1

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
        assert status.text_content().strip() == "candidate selection required"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Candidate Selection Required"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Candidate slot summaries are review-only" in action.text_content()

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
        assert status.text_content().strip() == "confirmation ready"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Proposal Confirmation Ready"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Confirm payload carries slot-selection" in action.text_content()

        # Verify selected slot
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-selected-slot']").text_content()

        # Verify approval elements
        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")

        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()
        assert success_msg.is_hidden()

        # Checking checkbox enables button
        checkbox.check()
        assert confirm_btn.is_disabled() is False

        # Unchecking checkbox disables button
        checkbox.uncheck()
        assert confirm_btn.is_disabled()

        # Re-checking checkbox and clicking confirm simulates booking
        checkbox.check()
        confirm_btn.click()

        assert confirm_btn.is_disabled()
        assert checkbox.is_disabled()
        assert success_msg.is_visible()
        assert "Booking proposal approved successfully" in success_msg.text_content()
    finally:
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_live_blocked(diary_page):
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

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "blocked"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Booking Blocked"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Blocked review payload" in action.text_content()

        # Verify block issues list
        assert diary_page.locator("[data-testid='bernie-review-blocks-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="missing_practitioner_id").count() == 1

        # Verify confirmation sections/elements are hidden
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    finally:
        # Clean up route
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_review_live_candidate_selection(diary_page):
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

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "candidate selection required"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Candidate Selection Required"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Candidate slot summaries are review-only" in action.text_content()

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


def test_bernie_review_live_confirmation_ready(diary_page):
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

        # Verify status is rendered
        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "confirmation ready"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Proposal Confirmation Ready"

        # Verify selected slot
        assert diary_page.locator("[data-testid='bernie-review-selected-slot']").count() == 1
        assert "09:00:00" in diary_page.locator("[data-testid='bernie-review-selected-slot']").text_content()

        # Verify approval elements
        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")

        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()
        assert success_msg.is_hidden()

        # Checking checkbox enables button
        checkbox.check()
        assert confirm_btn.is_disabled() is False

        # Click confirm simulates booking
        confirm_btn.click()

        assert confirm_btn.is_disabled()
        assert checkbox.is_disabled()
        assert success_msg.is_visible()
        assert "Booking proposal approved successfully" in success_msg.text_content()
    finally:
        # Clean up routes
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_confirm_submit_adapter_success(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    payload_received = []

    def handle_confirm(route):
        req = route.request
        assert req.method == "POST"
        payload_received.append(json.loads(req.post_data))
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"status": "success"}))

    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        # Load with bernie_confirm_adapter=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()
        assert success_msg.is_hidden()
        assert error_msg.is_hidden()

        # No submit before approval
        assert len(payload_received) == 0

        # Check box, button enabled
        checkbox.check()
        assert confirm_btn.is_disabled() is False

        # Click confirm
        confirm_btn.click()

        # UI state after click
        assert confirm_btn.is_disabled()
        assert checkbox.is_disabled()
        assert success_msg.is_visible()
        assert error_msg.is_hidden()
        assert "Booking proposal approved successfully" in success_msg.text_content()

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

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        checkbox.check()
        confirm_btn.click()

        # First attempt (fails)
        assert error_msg.is_visible()
        assert "Database connection lost" in error_msg.text_content()
        assert success_msg.is_hidden()

        # Checkbox and button re-enabled for retry
        assert checkbox.is_disabled() is False
        assert confirm_btn.is_disabled() is False

        # Retry
        confirm_btn.click()

        # Second attempt (succeeds)
        assert success_msg.is_visible()
        assert error_msg.is_hidden()
        assert checkbox.is_disabled()
        assert confirm_btn.is_disabled()
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
        assert diary_page.locator("[data-testid='bernie-review-approval-checkbox']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0

        # Candidate selection state with bernie_confirm_adapter=true
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=candidate_selection_required&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-approval-checkbox']").count() == 0
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
                    "selected_candidate": {
                        "appointment_date": "2026-06-27",
                        "start_time_local": "09:00:00",
                        "end_time_local": "09:15:00",
                        "duration_minutes": 15,
                        "practitioner_id": "prac-1",
                        "location_id": "loc-main"
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


def test_bernie_live_confirm_flow_harness_success(diary_page):
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

        assert len(supervised_requests) == 1
        assert supervised_requests[0]["selected_candidate_index"] == 0

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        assert checkbox.is_visible()
        assert confirm_btn.is_disabled()
        assert success_msg.is_hidden()
        assert error_msg.is_hidden()
        assert len(confirm_payloads) == 0

        checkbox.check()
        assert confirm_btn.is_disabled() is False
        assert len(confirm_payloads) == 0

        confirm_btn.click()

        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True
        assert confirm_payloads[0]["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
        assert confirm_payloads[0]["create_proposal"]["reason"] == "Follow-up"
        assert success_msg.is_visible()
        assert error_msg.is_hidden()
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


@pytest.mark.parametrize(
    ("review_response", "expected_status"),
    [
        (_bernie_live_blocked_response, "blocked"),
        (_bernie_live_candidate_response, "candidate selection required"),
    ],
)
def test_bernie_live_confirm_flow_harness_non_confirmable_states(diary_page, review_response, expected_status):
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

        assert len(supervised_requests) == 1
        assert diary_page.locator("[data-testid='bernie-review-status']").text_content().strip() == expected_status
        assert diary_page.locator("[data-testid='bernie-review-approval-checkbox']").count() == 0
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_live_confirm_flow_harness_supervised_booking_error_no_write(diary_page):
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

        assert len(supervised_requests) == 1
        assert diary_page.locator("[data-testid='bernie-review-status']").text_content().strip() == "blocked"
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="HTTP status 500").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert len(confirm_payloads) == 0
    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)


def test_bernie_live_confirm_flow_harness_no_normal_mode_exposure(diary_page):
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
        diary_page.goto(base_url + "/diary/diary.html")
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

        assert len(supervised_requests) == 1
        assert supervised_requests[0]["selected_candidate_index"] == 0

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        success_msg = diary_page.locator("[data-testid='bernie-review-success-message']")
        error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")

        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()
        assert success_msg.is_hidden()
        assert error_msg.is_hidden()
        assert len(confirm_payloads) == 0

        # Verify explicit approval gating
        checkbox.check()
        assert confirm_btn.is_disabled() is False
        assert len(confirm_payloads) == 0

        confirm_btn.click()

        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True
        assert confirm_payloads[0]["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
        assert success_msg.is_visible()
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

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()

        try:
            confirm_btn.click(timeout=1000, force=True)
        except Exception:
            pass
        assert len(confirm_payloads) == 0

        checkbox.check()
        assert confirm_btn.is_disabled() is False
        confirm_btn.click()
        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["confirmed"] is True

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
        assert status.text_content().strip() == "blocked"

        # 4. Proves dev-review fixture failures are visible and do not silently fall back to mocks
        diary_page.unroute("**/api/v1/appointments/dev/bernie-review-fixtures*")
        diary_page.route(
            "**/api/v1/appointments/dev/bernie-review-fixtures*",
            lambda route: route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "fixture unavailable"}))
        )
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&bernie_review=blocked")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="dev_fixture_unavailable").count() == 1
        diary_page.unroute("**/api/v1/appointments/dev/bernie-review-fixtures*")
        diary_page.route("**/api/v1/appointments/dev/bernie-review-fixtures*", handle_dev_fixtures)

        # 5. Proves dev-review = blocked fetches and renders
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&bernie_review=blocked")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 1
        assert "state=blocked" in dev_fixtures_requests[-1]

        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Booking Blocked"
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="missing_practitioner_id").count() == 1

        # 6. Proves dev-review = candidate_selection_required fetches and renders
        diary_page.goto(base_url + "/diary/diary.html?bernie_dev_review=true&bernie_review=candidate_selection_required")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 2
        assert "state=candidate_selection_required" in dev_fixtures_requests[-1]

        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "candidate selection required"

        # 7. Proves dev-review = confirmation_ready fetches, renders and can confirm (route-intercepted)
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_dev_review=true&bernie_review=confirmation_ready&bernie_confirm_adapter=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        assert len(dev_fixtures_requests) == 3
        assert "state=confirmation_ready" in dev_fixtures_requests[-1]

        status = diary_page.locator("[data-testid='bernie-review-status']")
        assert status.text_content().strip() == "confirmation ready"

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()

        try:
            confirm_btn.click(timeout=1000, force=True)
        except Exception:
            pass
        assert len(confirm_payloads) == 0

        checkbox.check()
        assert confirm_btn.is_disabled() is False
        confirm_btn.click()
        diary_page.wait_for_selector("[data-testid='bernie-review-success-message']:not(.hidden)", state="visible", timeout=5000)
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

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_live_review)
        )
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

        banner = diary_page.locator("[data-testid='bernie-pilot-banner']")
        assert banner.is_visible()
        assert "Supervised Pilot Mode" in banner.text_content()

        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Proposal Confirmation Ready"

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
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

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_live_review)
        )
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

        checkbox = diary_page.locator("[data-testid='bernie-review-approval-checkbox']")
        confirm_btn = diary_page.locator("[data-testid='bernie-review-confirm-button']")
        assert checkbox.is_visible()
        assert checkbox.is_checked() is False
        assert confirm_btn.is_visible()
        assert confirm_btn.is_disabled()

        try:
            confirm_btn.click(timeout=1000, force=True)
        except Exception:
            pass
        assert len(confirm_payloads) == 0

        checkbox.check()
        assert confirm_btn.is_disabled() is False
        confirm_btn.click()
        diary_page.wait_for_selector("[data-testid='bernie-review-success-message']:not(.hidden)", state="visible", timeout=5000)

        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["proposal_id"] == "prop-123"
        assert confirm_payloads[0]["confirmed"] is True

    finally:
        diary_page.unroute("**/api/v1/appointments/bernie/pilot-eligibility")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.goto(base_url + CHECKS["target"])
        diary_page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
