"""
review/test_diary_duplicate_booking.py — Focused Playwright acceptance test
for duplicate booking receptionist flow.

This test proves the receptionist sequence:
1. First booking request is interpreted and supervised.
2. Receptionist reviews the candidate slot and clicks "Confirm booking".
3. Authoritative confirmation success is returned and rendered.
4. Receptionist clicks "Start new booking" and enters the duplicate booking instruction again.
5. Bernie presents the existing-booking outcome and does not offer a confirmation action.
6. Accessible suggestions (next actions) are verified and keyboard-activated.
7. Confirm request count is monitored to prove no second confirm API call is made.
"""

import json
import sys
from pathlib import Path
import pytest

# Make harness importable regardless of pytest's rootdir / cwd.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "review"))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)


@pytest.fixture(scope="function")
def diary_page():
    with harness.serve_dir(REPO_ROOT / "docs") as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        # Set up a page with the correct query flags
        page.goto(
            base_url
            + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_confirm_adapter=true"
        )
        page.wait_for_selector(
            "[data-testid='bernie-review-panel']", state="visible", timeout=15000
        )
        yield page
        browser.close()


def test_duplicate_booking_receptionist_flow(diary_page):
    """
    Stateful duplicate booking browser acceptance check.
    Proves first request confirmed, second identical request displays existing booking outcome,
    confirm buttons are absent, keyboard suggestions can be activated, and no second confirmation
    request is fired.
    """
    interpret_count = 0
    supervised_count = 0
    confirm_count = 0

    # Define mock response payloads
    mock_interpret_response = {
        "safe": True,
        "result": "interpreted",
        "command_candidate": {
            "practitioner_id": "prac-1",
            "patient_id": "smoke-pat-1",
            "date_from": "2026-07-14",
            "duration_minutes": "15",
        },
    }

    mock_supervised_first = {
        "intent": "bernie_supervised_booking",
        "result": "confirmation_ready",
        "safe": True,
        "requires_confirmation": True,
        "autonomy_tier": "proposal",
        "summary": "Proposal Confirmation Ready",
        "turn_ref": {
            "session_id": "session-duplicate-1",
            "turn_id": "turn-duplicate-first",
            "turn_index": 1,
            "reference_date": "2026-07-13",
            "state": "proposal_preview",
        },
        "staff_review": {
            "headline": "Proposal Confirmation Ready",
            "status": "confirmation_ready",
            "staff_action_required": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
            "confirmation_ready": True,
            "patient_evidence": {
                "patient_label": "Margaret Thompson",
                "confidence": "high"
            },
            "practitioner_evidence": {
                "display_name": "Dr Alex Shera"
            },
            "selected_slot": {
                "appointment_date": "2026-07-14",
                "start_time_local": "15:00:00",
                "end_time_local": "15:15:00",
                "practitioner_name": "Dr Alex Shera",
                "room_name": "Room 1",
            },
            "candidate_slots": [],
            "warning_summary": "No warnings or blocked issues.",
            "evidence_summary": "Confirm payload carries slot-selection and create-proposal evidence.",
            "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
            "confirm_payload": {
                "confirmed": False,
                "selection_proposal": {
                    "intent": "select_slot_for_create_proposal",
                    "selected_candidate_index": 0,
                    "proposal_freshness_id": "proposal-freshness-dup-1",
                    "selected_candidate": {
                        "appointment_date": "2026-07-14",
                        "start_time_local": "15:00:00",
                        "end_time_local": "15:15:00",
                        "duration_minutes": 15,
                        "practitioner_id": "prac-1",
                        "location_id": "loc-main",
                        "candidate_freshness_id": "candidate-freshness-dup-1",
                    },
                },
                "create_proposal": {
                    "intent": "create_appointment",
                    "patient_id": "smoke-pat-1",
                    "practitioner_id": "prac-1",
                    "appointment_date": "2026-07-14",
                    "start_time": "15:00:00",
                    "duration_minutes": 15,
                    "reason": "Standard appointment",
                },
            },
        },
    }

    mock_supervised_second = {
        "intent": "bernie_supervised_booking",
        "result": "existing_booking_found",
        "status": "existing_booking_found",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "execute_with_report",
        "summary": "This appointment already exists and no new booking was created. Use a suggestion below to find an alternative time or day.",
        "turn_ref": {
            "session_id": "session-duplicate-1",
            "turn_id": "turn-duplicate-second",
            "turn_index": 2,
            "reference_date": "2026-07-13",
            "state": "proposal_preview",
        },
        "existing_booking": {
            "appointment_date": "2026-07-14",
            "start_time_local": "15:00:00",
            "practitioner_display": "Dr Alex Shera",
            "status": "Booked",
            "appointment_type_name": "Standard Consult",
            "duration_minutes": 15,
        },
        "suggestions": [
            {
                "kind": "widen_time_window",
                "summary": "The requested time already has a booking. Choose a different time to find available slots.",
                "requires_confirmation": True,
            },
            {
                "kind": "next_available_day",
                "summary": "Search the next day for available slots.",
                "requires_confirmation": True,
            },
        ],
        "staff_review": {
            "headline": "Appointment already exists",
            "status": "existing_booking_found",
            "staff_action_required": "Choose another time or day if wanted.",
            "confirmation_ready": False,
            "patient_evidence": {
                "patient_label": "Margaret Thompson",
                "confidence": "high"
            },
            "practitioner_evidence": {
                "display_name": "Dr Alex Shera"
            },
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "No warnings.",
            "evidence_summary": "Existing booking details found.",
        },
    }

    mock_confirm_response = {
        "safe": True,
        "autonomy_tier": "confirmed_write",
        "appointment": {
            "id": "appt-dup-1",
            "appointment_date": "2026-07-14",
            "start_time_local": "15:00:00",
            "duration_minutes": 15,
            "status": "Booked",
        },
        "confirmation_receipt": {
            "schema_version": "appointment.confirmation_receipt.v1",
            "outcome": "appointment_created",
            "appointment_id": "appt-dup-1",
            "patient_display": "Margaret Thompson",
            "practitioner_display": "Dr Alex Shera",
            "appointment_date": "2026-07-14",
            "start_time_local": "15:00:00",
            "duration_minutes": 15,
            "status": "Booked",
            "appointment_type": "Standard Consult",
            "confirmed_by_display": "Reception Staff",
            "confirmed_by_role": "Receptionist",
            "verification": {
                "actor_authenticated": True,
                "practice_scope_verified": True,
                "proposal_revalidated": True,
                "conflict_check_passed": True,
                "idempotency_verified": True,
                "audit_recorded": True,
                "signed_evidence_verified": True,
                "visual_diary_check_required": False,
            },
        },
    }

    # Route interceptors
    def handle_interpret(route):
        nonlocal interpret_count
        interpret_count += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_interpret_response),
        )

    def handle_supervised(route):
        nonlocal supervised_count
        supervised_count += 1
        if supervised_count == 1:
            body = mock_supervised_first
        else:
            body = mock_supervised_second
        route.fulfill(
            status=200, content_type="application/json", body=json.dumps(body)
        )

    def handle_confirm(route):
        nonlocal confirm_count
        confirm_count += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_confirm_response),
        )

    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        handle_interpret,
    )
    diary_page.route(
        "**/api/v1/appointments/proposals/bernie/supervised-booking",
        handle_supervised,
    )
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm
    )

    # 1. Trigger first request
    instruction = "Make an appointment for Margaret Thompson with Dr Shera tomorrow after 3 but before 4.30 for 15 minutes"
    textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
    textarea.wait_for(state="visible", timeout=5000)
    textarea.fill(instruction)

    submit_btn = diary_page.locator(
        "[data-testid='btn-bernie-instruction-submit']"
    )
    submit_btn.click()

    # 2. Wait for proposal to be reviewed
    confirm_btn = diary_page.locator(
        "[data-testid='bernie-review-confirm-button']"
    )
    confirm_btn.wait_for(state="visible", timeout=5000)

    assert interpret_count == 1
    assert supervised_count == 1
    assert confirm_count == 0

    # Check that confirm button accessible properties match the booking detail
    aria_label = confirm_btn.get_attribute("aria-label")
    assert "Margaret Thompson" in aria_label
    assert "Dr Alex Shera" in aria_label
    assert "2026-07-14" in aria_label
    assert "15:00" in aria_label

    # 3. Confirm first request
    confirm_btn.click()

    # Wait for the confirmed state card to show
    diary_page.wait_for_selector(
        "[data-testid='bernie-confirmed-container']",
        state="visible",
        timeout=5000,
    )
    assert confirm_count == 1

    # Assert Criterion 3: after first confirmation, the authoritative receipt/status is exposed to AT
    status_headline = diary_page.locator("[data-testid='bernie-review-headline']")
    assert status_headline.get_attribute("role") == "status"
    assert status_headline.get_attribute("aria-live") == "polite"
    assert "Booking confirmed successfully" in status_headline.text_content()
    assert "Margaret Thompson" in status_headline.text_content()

    receipt_group = diary_page.locator("[data-testid='bernie-receipt-group']")
    assert receipt_group.get_attribute("role") == "group"
    assert (
        receipt_group.get_attribute("aria-label") == "Booking confirmation receipt"
    )

    # 4. Trigger duplicate request
    reset_btn = diary_page.locator("[data-testid='bernie-review-reset-button']")
    reset_btn.click()

    # Ensure focus returned to the textarea after resetting
    textarea.wait_for(state="visible", timeout=5000)
    diary_page.wait_for_timeout(100)  # Wait for JS setTimeout focus handler
    assert textarea.evaluate("el => el === document.activeElement")

    # Fill and submit same instruction
    textarea.fill(instruction)
    submit_btn.click()

    # 5. Wait for existing booking outcome to be presented
    existing_booking_card = diary_page.locator(
        "[data-testid='bernie-review-existing-booking']"
    )
    existing_booking_card.wait_for(state="visible", timeout=5000)

    # Assert Criterion 4: repeated request exposes existing booking details and has NO confirmation button
    assert "2026-07-14" in existing_booking_card.text_content()
    assert "15:00" in existing_booking_card.text_content()
    assert "Dr Alex Shera" in existing_booking_card.text_content()
    assert "Booked" in existing_booking_card.text_content()

    assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    assert diary_page.locator("#btn-bernie-confirm").count() == 0

    # Assert Criterion 5: assert useful accessible next actions where UI contract supplies them
    # Locate suggestion buttons (next actions) by role and name
    suggestion_1 = diary_page.get_by_role(
        "button",
        name="The requested time already has a booking. Choose a different time to find available slots.",
    )
    suggestion_2 = diary_page.get_by_role(
        "button", name="Search the next day for available slots."
    )

    assert suggestion_1.count() == 1
    assert suggestion_2.count() == 1

    # Verify keyboard activation on suggestion 2
    diary_page.wait_for_timeout(100)
    suggestion_2 = diary_page.get_by_role(
        "button", name="Search the next day for available slots."
    )
    suggestion_2.focus()
    assert suggestion_2.evaluate("el => el === document.activeElement")
    diary_page.keyboard.press("Enter")

    # Activating the suggestion chip should trigger a new interpretation request
    diary_page.wait_for_timeout(500)
    assert interpret_count == 2 + 1  # 2 original instructions + 1 suggestion instruction

    # Assert Criterion 6: prove the duplicate path made no additional confirmation request
    assert confirm_count == 1

    # Assert Criterion 7: check focus coherence after outcome transition and no actionable control hidden only in visual copy
    # The textarea should have focus returned during re-render
    assert textarea.evaluate("el => el === document.activeElement")
    # Ensure no hidden/inactive confirm controls are accessible in the DOM
    assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
