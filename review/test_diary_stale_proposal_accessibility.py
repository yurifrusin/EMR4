"""
review/test_diary_stale_proposal_accessibility.py — route-intercepted accessibility and UI-contract tests
for stale, failed, and confirmation-pending states.
"""

import json
import sys
import urllib.parse
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

# Make harness importable regardless of pytest's rootdir / cwd.
sys.path.insert(0, str(Path(__file__).parent))
import harness

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
CHECKS = json.loads((Path(__file__).parent / "checks_diary.json").read_text(encoding="utf-8"))

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

def _base_bernie_response(status="blocked", outcome_kind="blocked"):
    return {
        "intent": "bernie_supervised_booking",
        "result": status,
        "safe": False,
        "requires_confirmation": False,
        "autonomy_tier": "blocked",
        "summary": "Mock response",
        "outcome": {
            "kind": outcome_kind,
        },
        "staff_review": {
            "headline": "Mock headline",
            "status": status,
            "staff_action_required": "Mock action",
            "confirmation_ready": False,
            "selected_slot": None,
            "candidate_slots": [],
            "warning_summary": "Mock warning",
            "evidence_summary": "No confirmation evidence was produced.",
            "confirm_endpoint": None,
            "confirm_payload": None,
            "confirm_evidence": [],
            "blocks": []
        }
    }

def trigger_route_intercepted_bernie(page, instruction="Please find practitioner_id:prac-1 patient_id:smoke-pat-1", register_default_mock=True):
    if register_default_mock:
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

@pytest.fixture(scope="function")
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
                content_type="application/javascript",
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

def test_outcome_stale_accessibility(diary_page):
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. Construct stale response using bernie.ui_view_model.v1
    response = _base_bernie_response(status="stale", outcome_kind="blocked")
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="blocked",
        confirmation_state="stale",
        freshness_state="stale",
        copy_mode="technical_details_only",
        primary_copy="This proposal is stale and must be refreshed.",
        secondary_copy="This proposal needs to be refreshed before it can be confirmed.",
        flags={
            "show_stale_warning": True,
            "show_retry_action": True,
            "show_edit_action": True,
            "show_confirm_button": False,
            "enable_confirm_button": False,
            "show_success_copy": False
        }
    )

    confirm_payloads = []
    supervised_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, register_default_mock=True)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        # A. State rendering & machine-readable markers
        assert "stale" in status_locator.get_attribute("class")
        assert status_locator.text_content().strip() == "Stale"

        headline_locator = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline_locator.text_content().strip() == "Review this appointment"

        action_locator = diary_page.locator("[data-testid='bernie-review-action']")
        assert action_locator.text_content().strip() == "This proposal is stale and must be refreshed."

        stale_warning_locator = diary_page.locator("[data-testid='bernie-stale-warning']")
        assert stale_warning_locator.is_visible()
        assert stale_warning_locator.text_content().strip() == "This proposal needs to be refreshed before it can be confirmed."

        # B. Coherent focus / live-region behavior
        assert status_locator.get_attribute("role") == "status"
        assert status_locator.get_attribute("aria-live") == "polite"
        diary_page.wait_for_function(
            "document.activeElement?.getAttribute('data-testid') === 'bernie-review-status'"
        )

        # C. Reachability/activation of next actions via keyboard
        # Focus instruction input textarea, then test tabbing to buttons
        input_textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        input_textarea.focus()
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # Tab to the submit button
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.id") == "btn-bernie-instruction-submit"

        # Tab to retry button
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.getAttribute('data-testid')") == "bernie-retry-button"

        # Tab to edit button
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.getAttribute('data-testid')") == "bernie-edit-button"

        # Activate edit action via keyboard Enter
        diary_page.keyboard.press("Enter")
        # Focus must return to instruction input field
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # D. Absence of confirmation authority
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        assert len(confirm_payloads) == 0

        # E. Clicking retry clears/resets the review panel
        retry_btn = diary_page.locator("[data-testid='bernie-retry-button']")
        retry_btn.click()
        assert diary_page.locator("[data-testid='bernie-review-status']").count() == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")


def test_outcome_failed_accessibility(diary_page):
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. Construct failed response using bernie.ui_view_model.v1
    response = _base_bernie_response(status="failed", outcome_kind="blocked")
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="blocked",
        confirmation_state="failed",
        copy_mode="technical_details_only",
        primary_copy="Confirmation failed due to a backend error.",
        flags={
            "show_retry_action": True,
            "show_edit_action": True,
            "show_confirm_button": False,
            "enable_confirm_button": False,
            "show_success_copy": False
        }
    )

    confirm_payloads = []
    supervised_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, register_default_mock=True)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        # A. State rendering & machine-readable markers
        assert "failed" in status_locator.get_attribute("class")
        assert status_locator.text_content().strip() == "Failed"

        headline_locator = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline_locator.text_content().strip() == "Review this appointment"

        action_locator = diary_page.locator("[data-testid='bernie-review-action']")
        assert action_locator.text_content().strip() == "Confirmation failed due to a backend error."

        # B. Coherent focus / live-region behavior
        assert status_locator.get_attribute("role") == "status"
        assert status_locator.get_attribute("aria-live") == "polite"
        diary_page.wait_for_function(
            "document.activeElement?.getAttribute('data-testid') === 'bernie-review-status'"
        )

        # C. Reachability/activation of next actions via keyboard
        input_textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        input_textarea.focus()
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # Tab to submit, then retry, then edit
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.id") == "btn-bernie-instruction-submit"

        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.getAttribute('data-testid')") == "bernie-retry-button"

        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.getAttribute('data-testid')") == "bernie-edit-button"

        # Activate edit action via keyboard Enter
        diary_page.keyboard.press("Enter")
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # D. Absence of confirmation authority
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        assert len(confirm_payloads) == 0

        # E. Clicking retry clears/resets the review panel
        retry_btn = diary_page.locator("[data-testid='bernie-retry-button']")
        retry_btn.click()
        assert diary_page.locator("[data-testid='bernie-review-status']").count() == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")


def test_outcome_pending_accessibility(diary_page):
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. Construct pending response using bernie.ui_view_model.v1
    response = _base_bernie_response(status="confirmation_pending", outcome_kind="blocked")
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="blocked",
        confirmation_state="pressed",
        copy_mode="technical_details_only",
        primary_copy="Awaiting confirmation response from backend...",
        flags={
            "show_retry_action": False,
            "show_edit_action": False,
            "show_confirm_button": False,
            "enable_confirm_button": False,
            "show_success_copy": False
        }
    )

    confirm_payloads = []
    supervised_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, register_default_mock=True)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        # A. State rendering & machine-readable markers
        assert "confirmation_pending" in status_locator.get_attribute("class")
        assert status_locator.text_content().strip() == "Confirmation Pending"

        headline_locator = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline_locator.text_content().strip() == "Review this appointment"

        action_locator = diary_page.locator("[data-testid='bernie-review-action']")
        assert action_locator.text_content().strip() == "Awaiting confirmation response from backend..."

        # B. Coherent focus / live-region behavior
        assert status_locator.get_attribute("role") == "status"
        assert status_locator.get_attribute("aria-live") == "polite"
        diary_page.wait_for_function(
            "document.activeElement?.getAttribute('data-testid') === 'bernie-review-status'"
        )

        # C. Keyboard reachability - no retry/edit actions should be present
        assert diary_page.locator("[data-testid='bernie-retry-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-edit-button']").count() == 0

        # Focus instruction input textarea, then test tabbing
        input_textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        input_textarea.focus()
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # Tab to the submit button
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.id") == "btn-bernie-instruction-submit"

        # Tabbing again should skip since no other focusable elements are in the review pane
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.id") != "bernie-retry-button"
        assert diary_page.evaluate("document.activeElement.id") != "bernie-edit-button"

        # D. Absence of confirmation authority & pending state does not permit another confirm attempt
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        assert len(confirm_payloads) == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
