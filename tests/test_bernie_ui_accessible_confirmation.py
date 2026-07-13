import json
import sys
from copy import deepcopy
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


MOCK_PROPOSAL_PAYLOAD = {
    "status": "confirmation_ready",
    "outcome": {
        "kind": "confirmation_ready",
        "can_confirm": True
    },
    "selected_slot": {
        "appointment_date": "2026-06-25",
        "start_time_local": "09:00:00",
        "duration_minutes": 15
    },
    "patient_evidence": {
        "patient_label": "Margaret Thatcher",
        "date_of_birth": "1925-10-13"
    },
    "practitioner_evidence": {
        "display_name": "Dr Alex Shera"
    },
    "confirm_endpoint": "/api/v1/appointments/proposals/create/confirm-bernie",
    "confirm_payload": {
        "confirmed": True,
        "selection_proposal": {
            "selected_candidate": {
                "appointment_date": "2026-06-25",
                "start_time_local": "09:00:00",
                "duration_minutes": 15
            }
        }
    },
    "confirm_affordance": {
        "can_show_confirm_ui": True,
        "confirm_grade_allowed": True
    }
}

MOCK_SUCCESS_RECEIPT_RESPONSE = {
    "safe": True,
    "autonomy_tier": "confirmed_write",
    "appointment": {
        "id": "appt-12345",
        "appointment_date": "2026-06-25",
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
        "status": "Booked"
    },
    "confirmation_receipt": {
        "schema_version": "appointment.confirmation_receipt.v1",
        "outcome": "appointment_created",
        "appointment_id": "appt-12345",
        "patient_display": "Margaret Thatcher (Different)",
        "practitioner_display": "Dr Alex Shera (Different)",
        "appointment_date": "2026-06-25",
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
        "status": "Booked",
        "appointment_type": "Standard Consult",
        "confirmed_by_display": "Dr Gregory House",
        "confirmed_by_role": "Practitioner",
        "verification": {
            "actor_authenticated": True,
            "practice_scope_verified": True,
            "proposal_revalidated": True,
            "conflict_check_passed": True,
            "idempotency_verified": True,
            "audit_recorded": True,
            "signed_evidence_verified": True,
            "visual_diary_check_required": False
        }
    }
}

MOCK_BLOCKED_RESPONSE = {
    "safe": False,
    "autonomy_tier": "blocked",
    "summary": "This slot was booked by another practitioner in the last 2 seconds.",
    "appointment": None,
    "confirmation_receipt": None,
    "blocks": [
        {
            "code": "slot_already_taken",
            "severity": "blocked",
            "message": "This slot was booked by another practitioner in the last 2 seconds."
        }
    ]
}


@pytest.fixture(scope="function")
def diary_page():
    with harness.serve_dir(REPO_ROOT / "docs") as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)

        page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_open=true&bernie_confirm_adapter=true")
        page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=15000)
        yield page
        browser.close()


def test_keyboard_activation_submits_confirm_enter(diary_page):
    """Proves that focusing and pressing Enter keyboard activation submits the confirm command."""
    # Reset page routes
    diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
    
    # Intercept with success response
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_SUCCESS_RECEIPT_RESPONSE)
        )
    )

    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_PROPOSAL_PAYLOAD
    )

    confirm_btn = diary_page.locator("#btn-bernie-confirm")
    confirm_btn.wait_for(state="visible", timeout=5000)

    # Focus and press Enter
    confirm_btn.focus()
    diary_page.keyboard.press("Enter")

    # Wait for success status
    status_badge = diary_page.locator("[data-testid='bernie-review-status']")
    status_badge.wait_for(state="visible", timeout=5000)

    # Check receipt group is rendered
    receipt_group = diary_page.locator("[data-testid='bernie-receipt-group']")
    receipt_group.wait_for(state="visible", timeout=5000)

    # Verify that the returned receipt (deliberately different values) is what's displayed
    patient_detail = diary_page.locator("[data-testid='receipt-patient'] dd")
    practitioner_detail = diary_page.locator("[data-testid='receipt-practitioner'] dd")
    
    assert patient_detail.text_content().strip() == "Margaret Thatcher (Different)"
    assert practitioner_detail.text_content().strip() == "Dr Alex Shera (Different)"


def test_keyboard_activation_submits_confirm_space(diary_page):
    """Proves that focusing and pressing Space keyboard activation submits the confirm command."""
    # Reset page routes
    diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
    
    # Intercept with success response
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_SUCCESS_RECEIPT_RESPONSE)
        )
    )

    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_PROPOSAL_PAYLOAD
    )

    confirm_btn = diary_page.locator("#btn-bernie-confirm")
    confirm_btn.wait_for(state="visible", timeout=5000)

    # Focus and press Space
    confirm_btn.focus()
    diary_page.keyboard.press("Space")

    # Wait for success status
    status_badge = diary_page.locator("[data-testid='bernie-review-status']")
    status_badge.wait_for(state="visible", timeout=5000)

    # Check receipt group is rendered
    receipt_group = diary_page.locator("[data-testid='bernie-receipt-group']")
    receipt_group.wait_for(state="visible", timeout=5000)


def test_success_status_and_receipt_semantics(diary_page):
    """Proves success status live-region and receipt group semantics."""
    diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_SUCCESS_RECEIPT_RESPONSE)
        )
    )

    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_PROPOSAL_PAYLOAD
    )

    confirm_btn = diary_page.locator("#btn-bernie-confirm")
    confirm_btn.wait_for(state="visible", timeout=5000)
    
    # Assert informative accessible name is present and contains key booking details
    aria_label = confirm_btn.get_attribute("aria-label")
    assert "Margaret Thatcher" in aria_label
    assert "Dr Alex Shera" in aria_label
    assert "2026-06-25" in aria_label
    assert "09:00" in aria_label

    confirm_btn.click()

    status_message = diary_page.locator("[data-testid='bernie-review-headline']")
    status_message.wait_for(state="visible", timeout=5000)

    # role="status" and aria-live="polite"
    assert status_message.get_attribute("role") == "status"
    assert status_message.get_attribute("aria-live") == "polite"
    assert "Margaret Thatcher (Different)" in status_message.text_content()

    receipt_group = diary_page.locator("[data-testid='bernie-receipt-group']")
    assert receipt_group.get_attribute("role") == "group"
    assert receipt_group.get_attribute("aria-label") == "Booking confirmation receipt"

    # verification/no-visual-check copy
    info = diary_page.locator("[data-testid='bernie-receipt-verification-info']")
    info.wait_for(state="visible", timeout=5000)
    assert info.text_content().strip() == "Deterministic checks passed. No visual diary check is required."


def test_http_200_blocked_body(diary_page):
    """Proves that an HTTP 200 blocked body produces no confirmed state or receipt claim, and returns to preview."""
    # Route intercept for blocked response
    diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(MOCK_BLOCKED_RESPONSE)
        )
    )

    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_PROPOSAL_PAYLOAD
    )

    confirm_btn = diary_page.locator("#btn-bernie-confirm")
    confirm_btn.wait_for(state="visible", timeout=5000)

    confirm_btn.click()

    # The error message should be displayed with backend block message
    error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")
    error_msg.wait_for(state="visible", timeout=5000)
    assert "This slot was booked by another practitioner in the last 2 seconds." in error_msg.text_content()

    # Assert no confirmed state (reset/success badges are not rendered, confirm button is still enabled)
    assert diary_page.locator("[data-testid='bernie-receipt-group']").count() == 0
    assert diary_page.locator("[data-testid='bernie-review-reset-button']").count() == 0
    assert confirm_btn.is_enabled()


def test_http_200_incomplete_receipt_cannot_claim_success(diary_page):
    """A nominal success body must fail closed when core receipt checks are absent."""
    incomplete = deepcopy(MOCK_SUCCESS_RECEIPT_RESPONSE)
    incomplete["confirmation_receipt"]["verification"]["audit_recorded"] = False
    diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
    diary_page.route(
        "**/api/v1/appointments/proposals/create/confirm-bernie",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(incomplete),
        ),
    )

    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_PROPOSAL_PAYLOAD,
    )
    confirm_btn = diary_page.locator("#btn-bernie-confirm")
    confirm_btn.click()

    error_msg = diary_page.locator("[data-testid='bernie-review-error-message']")
    error_msg.wait_for(state="visible", timeout=5000)
    assert diary_page.locator("[data-testid='bernie-receipt-group']").count() == 0
    assert diary_page.locator("[data-testid='bernie-review-reset-button']").count() == 0
    assert confirm_btn.is_enabled()


def test_simulated_offline_confirm_does_not_render_receipt_group(diary_page):
    """Proves simulated confirmation renders a simulated group, not a real receipt group, and does not claim deterministic checks passed."""
    # Navigate to a URL without bernie_confirm_adapter=true
    url = diary_page.url.replace("&bernie_confirm_adapter=true", "")
    diary_page.goto(url)
    diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

    diary_page.evaluate(
        "(payload) => { isBerniePilotActive = true; renderBernieReview(payload); }",
        MOCK_PROPOSAL_PAYLOAD
    )

    confirm_btn = diary_page.locator("#btn-bernie-confirm")
    confirm_btn.wait_for(state="visible", timeout=5000)
    confirm_btn.click()

    status_badge = diary_page.locator("[data-testid='bernie-review-status']")
    status_badge.wait_for(state="visible", timeout=5000)

    # Check simulated group is rendered, not the real receipt group
    assert diary_page.locator("[data-testid='bernie-simulated-group']").count() == 1
    assert diary_page.locator("[data-testid='bernie-receipt-group']").count() == 0
    assert diary_page.locator("[data-testid='bernie-receipt-verification-info']").count() == 0
