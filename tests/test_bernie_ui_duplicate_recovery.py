import json
import sys
from pathlib import Path
import pytest

# Make harness importable regardless of pytest's rootdir / cwd.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "review"))
import harness

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)


MOCK_DUPLICATE_PAYLOAD = {
    "result": "existing_booking_found",
    "status": "existing_booking_found",
    "safe": True,
    "requires_confirmation": False,
    "outcome": {
        "kind": "existing_booking_found",
        "family": "advisory",
        "session_state": "no_slot",
        "is_terminal": False,
        "requires_confirmation": False,
        "can_confirm": False
    },
    "existing_booking": {
        "appointment_date": "2026-07-13",
        "start_time_local": "10:30:00",
        "practitioner_display": "Dr Alex Shera",
        "status": "Booked",
        "appointment_type_name": "Standard Consult",
        "duration_minutes": 15
    },
    "suggestions": [
        {
            "kind": "next_available_day",
            "summary": "Try tomorrow at 10:30",
            "params": {"date": "2026-07-14"}
        },
        {
            "kind": "widen_time_window",
            "summary": "Try afternoon",
            "params": {"start": "12:00", "end": "17:00"}
        }
    ]
}


@pytest.fixture(scope="module")
def diary_page():
    with harness.serve_dir(REPO_ROOT / "docs") as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        # Mock the suggestion click endpoint
        page.route(
            "**/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "safe": True,
                    "result": "interpreted",
                    "command_candidate": {
                        "practitioner_id": "prac-1",
                        "patient_id": "smoke-pat-1",
                        "date_from": "tomorrow",
                        "duration_minutes": "15"
                    }
                })
            )
        )

        page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true")
        page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=15000)
        yield page
        browser.close()


def test_existing_booking_found_transition_and_copy(diary_page):
    """Proves explicit transition, status announcement, headline, and action copy."""
    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_DUPLICATE_PAYLOAD
    )

    status_badge = diary_page.locator("[data-testid='bernie-review-status']")
    status_badge.wait_for(state="visible", timeout=5000)

    # 1. Semantic live-region status announcement
    assert status_badge.get_attribute("role") == "status"
    assert status_badge.get_attribute("aria-live") == "polite"
    assert status_badge.text_content().strip() == "Existing booking found"

    # 2. Headline and action copy
    headline = diary_page.locator("[data-testid='bernie-review-headline']")
    assert headline.text_content().strip() == "Appointment already exists"

    action = diary_page.locator("[data-testid='bernie-review-action']")
    assert "no new booking was made" in action.text_content()
    assert "choose another time/day" in action.text_content().lower() or "choose another time or day" in action.text_content().lower()


def test_no_confirm_or_candidate_affordance(diary_page):
    """Proves that neither confirm nor candidate selection cards/buttons are displayed."""
    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_DUPLICATE_PAYLOAD
    )

    # Asserts no confirmation buttons/shortcuts or staged/provisional proposal displays
    assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
    assert diary_page.locator("[data-testid='bernie-review-candidate-item']").count() == 0
    assert diary_page.locator("#btn-bernie-confirm").count() == 0


def test_existing_booking_fields_rendered(diary_page):
    """Proves that existing booking details (date, time, practitioner, status, type, duration) are read back."""
    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_DUPLICATE_PAYLOAD
    )

    card = diary_page.locator("[data-testid='bernie-review-existing-booking']")
    card.wait_for(state="visible", timeout=5000)

    # Check detail rows using helper structure
    rows = card.locator(".bernie-detail-row")
    assert rows.count() >= 4

    # Extract texts
    row_texts = [r.text_content().strip() for r in rows.all()]

    # Verify key details are present
    assert any("Date2026-07-13" in text for text in row_texts)
    assert any("Time10:30" in text for text in row_texts)
    assert any("PractitionerDr Alex Shera" in text for text in row_texts)
    assert any("StatusBooked" in text for text in row_texts)
    assert any("TypeStandard Consult" in text for text in row_texts)
    assert any("Duration15 mins" in text for text in row_texts)


def test_alternative_search_suggestions_remain_available(diary_page):
    """Proves that alternative-search suggestions are rendered using standard chips."""
    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_DUPLICATE_PAYLOAD
    )

    suggestions_list = diary_page.locator("[data-testid='bernie-no-slot-suggestions']")
    suggestions_list.wait_for(state="visible", timeout=5000)

    chips = suggestions_list.locator(".bernie-suggestion-chip")
    assert chips.count() == 2

    assert chips.nth(0).text_content().strip() == "Try tomorrow at 10:30"
    assert chips.nth(1).text_content().strip() == "Try afternoon"
