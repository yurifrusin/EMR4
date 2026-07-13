"""
review/test_diary_outcome_accessibility.py — route-intercepted accessibility and UI-contract tests.

Verifies:
- heading, copy, and status badge live-region attributes
- keyboard navigation / tabbing order and activation of next useful actions
- focus coherence (expected gaps and focus loss)
- absence of confirmation authority (no confirm buttons, receipts, or confirm payloads)
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

def test_outcome_no_slots_accessibility(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Construct no_slots response
    response = _base_bernie_response(status="no_slots", outcome_kind="no_matching_times")
    response["reception_policy"] = {
        "search_ran_no_candidates": True,
        "must_block_confirmation": True
    }
    response["suggestions"] = [
        {"summary": "Try tomorrow morning"},
        {"summary": "Try next Monday"}
    ]
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="blocked",
        confirmation_state="blocked",
        copy_mode="no_slots",
        primary_copy="I could not find matching free times in that window. Tell me another day or time to try.",
        flags={"show_no_slot_suggestions": True}
    )

    confirm_payloads = []
    supervised_requests = []
    interpret_requests = []

    def handle_supervised_booking(route):
        supervised_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps(response))

    def handle_confirm(route):
        confirm_payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=500, content_type="application/json", body=json.dumps({"detail": "unexpected write"}))

    def handle_interpret(route):
        interpret_requests.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(
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

    diary_page.route("**/api/v1/appointments/proposals/bernie/supervised-booking", handle_supervised_booking)
    diary_page.route("**/api/v1/appointments/proposals/create/confirm-bernie", handle_confirm)
    diary_page.route("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction", handle_interpret)

    try:
        diary_page.goto(base_url + "/diary/diary.html?smoke=true&bernie_review=live&bernie_dev_review=true&bernie_confirm_adapter=true&practitioner_id=prac-1")
        diary_page.wait_for_selector("[data-testid='bernie-review-panel']", state="visible", timeout=5000)

        trigger_route_intercepted_bernie(diary_page, register_default_mock=False)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        # 1. Heading/copy & machine-readable marker
        assert "no_slots" in status_locator.get_attribute("class")
        assert status_locator.text_content().strip() == "Try another time"

        headline_locator = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline_locator.text_content().strip() == "No matching times found"

        action_locator = diary_page.locator("[data-testid='bernie-review-action']")
        assert "I could not find matching free times" in action_locator.text_content()

        empty_locator = diary_page.locator("[data-testid='bernie-review-candidates-empty']")
        assert empty_locator.is_visible()
        assert "I could not find matching free times" in empty_locator.text_content()

        # 2. Live-region assertion
        assert status_locator.get_attribute("role") == "status"
        assert status_locator.get_attribute("aria-live") == "polite"

        # 3. Next useful action (suggestion chips) and tabbing
        suggestions_container = diary_page.locator("[data-testid='bernie-no-slot-suggestions']")
        assert suggestions_container.is_visible()

        suggestion_0 = diary_page.locator("[data-testid='bernie-no-slot-suggestion-0']")
        suggestion_1 = diary_page.locator("[data-testid='bernie-no-slot-suggestion-1']")
        assert suggestion_0.text_content() == "Try tomorrow morning"
        assert suggestion_1.text_content() == "Try next Monday"

        # Focus instruction input textarea, then test tabbing
        input_textarea = diary_page.locator("[data-testid='bernie-instruction-input']")
        input_textarea.focus()
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # Tab to the submit button
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.id") == "btn-bernie-instruction-submit"

        # Tab to first suggestion chip
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.getAttribute('data-testid')") == "bernie-no-slot-suggestion-0"

        # Tab to second suggestion chip
        diary_page.keyboard.press("Tab")
        assert diary_page.evaluate("document.activeElement.getAttribute('data-testid')") == "bernie-no-slot-suggestion-1"

        # Activate second suggestion chip via keyboard (Enter)
        diary_page.keyboard.press("Enter")

        # Verify new request was fired and loader displayed
        diary_page.wait_for_selector(".bernie-loading", state="visible", timeout=3000)
        assert len(interpret_requests) == 2
        assert "Please find practitioner_id" in interpret_requests[0]["instruction"]
        assert interpret_requests[1]["instruction"] == "Try next Monday"

        # 4. Absence of confirmation authority
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        assert len(confirm_payloads) == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/interpret-booking-instruction")

def test_outcome_roster_unavailable_accessibility(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Construct roster_unavailable response
    response = _base_bernie_response(status="roster_unavailable", outcome_kind="roster_unavailable")
    response["reception_policy"] = {
        "roster_unavailable": True,
        "must_block_confirmation": True
    }
    response["staff_review"]["blocks"] = []
    response["ui_view_model"] = _bernie_ui_view_model(
        proposal_state="blocked",
        confirmation_state="blocked",
        copy_mode="blocked",
        primary_copy="There is no bookable session configured for that request.",
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

        trigger_route_intercepted_bernie(diary_page)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        # 1. Heading/copy & machine-readable marker
        assert "roster_unavailable" in status_locator.get_attribute("class")
        assert status_locator.text_content().strip() == "Roster/schedule unavailable"

        headline_locator = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline_locator.text_content().strip() == "Roster/schedule unavailable"

        action_locator = diary_page.locator("[data-testid='bernie-review-action']")
        assert "There is no bookable session configured" in action_locator.text_content()

        empty_locator = diary_page.locator("[data-testid='bernie-review-candidates-empty']")
        assert empty_locator.is_visible()
        assert "There is no bookable session configured" in empty_locator.text_content()

        # 2. Live-region assertion
        assert status_locator.get_attribute("role") == "status"
        assert status_locator.get_attribute("aria-live") == "polite"

        # 3. Absence of confirmation authority
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        assert len(confirm_payloads) == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")

def test_outcome_clarification_accessibility(diary_page):
    import urllib.parse
    parsed = urllib.parse.urlparse(diary_page.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Construct clarification response
    response = _base_bernie_response(status="clarification", outcome_kind="clarification_required")
    response["clarifying_question"] = "Which practitioner should I check before searching?"
    response["ui_view_model"] = _bernie_ui_view_model(
        clarification_state="required",
        proposal_state="blocked",
        confirmation_state="blocked",
        copy_mode="ask",
        primary_copy="Which practitioner should I check before searching?",
        flags={
            "show_clarification_prompt": True,
            "show_edit_action": True
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

        # Focus submit button and click it to submit
        submit_btn = diary_page.locator("[data-testid='btn-bernie-instruction-submit']")
        submit_btn.focus()
        assert diary_page.evaluate("document.activeElement.id") == "btn-bernie-instruction-submit"

        trigger_route_intercepted_bernie(diary_page, register_default_mock=True)

        status_locator = diary_page.locator("[data-testid='bernie-review-status']")
        status_locator.wait_for(state="visible", timeout=5000)

        # 1. Heading/copy & machine-readable marker
        assert "clarification" in status_locator.get_attribute("class")
        assert status_locator.text_content().strip() == "Clarification required"

        headline_locator = diary_page.locator("[data-testid='bernie-review-headline']")
        assert headline_locator.text_content().strip() == "Clarification required"

        action_locator = diary_page.locator("[data-testid='bernie-review-action']")
        assert "Which practitioner should I check" in action_locator.text_content()

        # 2. Live-region assertion
        assert status_locator.get_attribute("role") == "status"
        assert status_locator.get_attribute("aria-live") == "polite"

        # 3. The completed async result receives coherent keyboard focus.
        diary_page.wait_for_function(
            "document.activeElement?.getAttribute('data-testid') === 'bernie-review-status'"
        )

        # 4. Edit action returns focus to the actual instruction field.
        edit_btn = diary_page.locator("[data-testid='bernie-edit-button']")
        assert edit_btn.is_visible()
        edit_btn.click()
        assert diary_page.evaluate("document.activeElement.id") == "bernie-instruction-input"

        # 5. Absence of confirmation authority
        assert diary_page.locator("[data-testid='bernie-review-confirm-button']").count() == 0
        assert diary_page.locator("[data-testid='bernie-success-copy']").count() == 0
        assert len(confirm_payloads) == 0

    finally:
        diary_page.unroute("**/api/v1/appointments/proposals/bernie/supervised-booking")
        diary_page.unroute("**/api/v1/appointments/proposals/create/confirm-bernie")
