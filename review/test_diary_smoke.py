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
        assert status.text_content().strip() == "Needs details"

        # Verify headline
        headline = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline.text_content().strip() == "Add the missing details"

        # Verify action description
        action = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Nothing is booked yet" in action.text_content()

        # Verify block issues list
        assert diary_page.locator("[data-testid='bernie-review-blocks-list']").count() == 1
        assert diary_page.locator("[data-testid='bernie-review-block-item']", has_text="Please select a practitioner.").count() == 1
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

        assert confirm_btn.is_disabled()
        assert success_msg.is_visible()
        assert "Booking confirmed" in success_msg.text_content()
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

        assert confirm_btn.is_disabled()
        assert success_msg.is_visible()
        assert "Booking confirmed" in success_msg.text_content()
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

        # Wait for success message
        success_msg.wait_for(state="visible", timeout=5000)

        # UI state after click
        assert confirm_btn.is_disabled()
        assert success_msg.is_visible()
        assert error_msg.is_hidden()
        assert "Booking confirmed" in success_msg.text_content()

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
        success_msg.wait_for(state="visible", timeout=5000)
        assert success_msg.is_visible()
        assert error_msg.is_hidden()
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
        success_msg.wait_for(state="visible", timeout=5000)

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
        success_msg.wait_for(state="visible", timeout=5000)

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
        diary_page.wait_for_selector("[data-testid='bernie-review-success-message']:not(.hidden)", state="visible", timeout=5000)
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
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
        diary_page.wait_for_selector("[data-testid='bernie-review-success-message']:not(.hidden)", state="visible", timeout=5000)
        assert len(confirm_payloads) == 1
        assert confirm_payloads[0]["proposal_id"] == "prop-70"
        assert confirm_payloads[0]["confirmed"] is True
    finally:
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
        diary_page.goto(base_url + "/diary/diary.html")
        diary_page.wait_for_selector("#diary-grid", state="visible", timeout=5000)
        diary_page.click(".appt:has-text('Margaret Thompson')")
        diary_page.click("[data-testid='bernie-pilot-launch-button']")
        diary_page.click("[data-testid='bernie-pilot-use-selected']")
        diary_page.fill("[data-testid='bernie-instruction-input']", "Use the typed other practitioner")
        diary_page.click("[data-testid='btn-bernie-instruction-submit']")
        diary_page.wait_for_selector(
            "[data-testid='bernie-review-block-item']:has-text('The practitioner found does not match the diary context.')",
            state="visible",
            timeout=5000,
        )

        assert len(interpret_requests) == 1
        assert len(supervised_requests) == 0
    finally:
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        assert "No free slots were found" in empty_text
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
        diary_page.goto(base_url + "/diary/diary.html")
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
        diary_page.goto(base_url + "/diary/diary.html")
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
        assert "medicare/card" in staged_text.lower()
        assert "is-fresh" in (staged_card.get_attribute("class") or "")
        assert staged_card.evaluate("el => getComputedStyle(el).animationName") == "bernie-staged-pulse"
        diary_page.emulate_media(reduced_motion="reduce")
        assert staged_card.evaluate("el => getComputedStyle(el).animationName") == "none"
        diary_page.emulate_media(reduced_motion="no-preference")
        assert supervised_requests[0].get("selected_candidate_index") is None
        assert supervised_requests[1]["selected_candidate_index"] == 0
    finally:
        diary_page.emulate_media(reduced_motion="no-preference")
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
        diary_page.goto(base_url + "/diary/diary.html")
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
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
        assert status_copy.text_content() == "Ready to search. Nothing is booked until you confirm."

        # 3. Clear textarea and verify status copy is hidden
        textarea.fill("")
        assert status_copy.is_visible() is False or status_copy.text_content().strip() == ""

        # 4. Type instruction and verify typed readiness copy
        textarea.fill("Book next Friday")
        assert status_copy.is_visible() is True
        assert status_copy.text_content() == "Ready to search. Nothing is booked until you confirm."
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        diary_page.evaluate("localStorage.setItem('emr4_token', 'ordinary-staff-token')")
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
        diary_page.evaluate("localStorage.removeItem('emr4_token')")
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
        assert block_items.first.text_content().strip() == "I can't proceed with this booking because please select a practitioner."

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
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)
        trigger_route_intercepted_bernie(diary_page)

        # Verify first-person date prompt displays
        block_item = diary_page.locator("[data-testid='bernie-review-block-item']")
        block_item.wait_for(state="visible", timeout=5000)
        assert block_item.count() == 1
        assert "I can't proceed with this booking because please select a date." in block_item.text_content()

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
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
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
                { "id": "11111111-1111-1111-1111-111111111111", "first_name": "Margaret", "last_name": "Thompson", "date_of_birth": "1960-01-01" },
                { "id": "22222222-2222-2222-2222-222222222222", "first_name": "Margaret", "last_name": "Smith", "date_of_birth": "1975-05-10" }
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


def test_sprint99_bernie_details_toggle_and_dob(diary_page):
    import json
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. High/medium confidence - details collapsed, DOB compact prompts render
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
            "warning_summary": "DOB verification required.",
            "evidence_summary": "High confidence but DOB verification required.",
            "warnings": [],
            "blocks": [],
            "identity_evidence": {
                "patient_label": "Margaret Thompson",
                "confidence": "high",
                "verification_status": "requires_staff_verification",
                "staff_prompt": "Please confirm Date of Birth"
            }
        }
    }

    # 2. Low confidence - details expanded
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
                "verification_status": "requires_staff_verification",
                "staff_prompt": "Verify patient details."
            }
        }
    }

    try:
        # Check High Confidence Case (Collapsed details, compact DOB prompt visible)
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

        dob_prompt = diary_page.locator("[data-testid='bernie-compact-dob-prompt']")
        dob_prompt.wait_for(state="visible", timeout=5000)
        assert "Please confirm the patient's date of birth before booking." in dob_prompt.text_content()

        # Check Low Confidence Case (Expanded details)
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


def test_sprint99_bernie_asset_version_checks():
    import re
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[1]
    html_path = repo_root / "docs" / "diary" / "diary.html"
    html_content = html_path.read_text(encoding="utf-8")

    # Assert that scripts and style assets are loaded with cache-busting version query parameters
    assert re.search(r'diary\.css\?v=\d+', html_content) is not None
    assert re.search(r'diary\.js\?v=\d+', html_content) is not None
