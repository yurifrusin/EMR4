"""Provider-free rendered acceptance for Reception One status composition."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest


sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    pytest.skip("playwright is required", allow_module_level=True)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def appointment(status: str = "Booked") -> dict:
    return {
        "id": "route-status-1",
        "appointment_date": "2026-08-13",
        "start_time_local": "09:00",
        "duration_minutes": 30,
        "status": status,
        "waiting_area_id": None,
        "patient_id": "patient-route-1",
        "patient": {
            "id": "patient-route-1",
            "first_name": "Margaret",
            "last_name": "Thompson",
            "date_of_birth": "1952-03-14",
        },
        "practitioner_id": "practitioner-route-1",
        "practitioner": {
            "id": "practitioner-route-1",
            "first_name": "Alex",
            "last_name": "Shera",
            "ahpra_number": "MED0001234567",
        },
        "location_id": "loc-1",
        "reason": "Authored synthetic review",
    }


@pytest.fixture(scope="module")
def reception_page():
    with harness.serve_dir(DOCS) as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        harness.stub_office(page)
        yield page, base_url
        browser.close()


def install_routes(page, *, mode: str) -> tuple[dict, object]:
    state = {
        "status": "Booked",
        "proposal_count": 0,
        "confirm_count": 0,
        "raw_count": 0,
        "exact_read_count": 0,
        "list_read_count": 0,
    }

    def handle(route):
        request = route.request
        parsed = urlparse(request.url)
        path = parsed.path

        if request.method == "POST" and path.endswith("/appointments/proposals/status/route-status-1"):
            state["proposal_count"] += 1
            requested = request.post_data_json["status"]
            warnings = [] if requested == "Arrived" else [{
                "code": "terminal_status",
                "severity": "warning",
                "message": "This is an authored-synthetic terminal-status warning.",
            }]
            blocks = [] if mode != "blocked" else [{
                "code": "authored_synthetic_current_truth_block",
                "severity": "blocked",
                "message": "The authored-synthetic current appointment cannot accept this change.",
            }]
            proposal = {
                "intent": "update_appointment_status",
                "safe": not blocks,
                "requires_confirmation": bool(warnings or blocks),
                "autonomy_tier": "blocked" if blocks else ("proposal" if warnings else "execute_with_report"),
                "summary": "Review the authored-synthetic status change.",
                "command": {
                    "appointment_id": "route-status-1",
                    "status": requested,
                    "waiting_area_id": None,
                    "waiting_area_id_supplied": True,
                    "clears_waiting_area": False,
                },
                "warnings": warnings,
                "blocks": blocks,
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                **proposal,
                "confirm_endpoint": "/api/v1/appointments/proposals/status-confirm",
                "confirm_payload": {
                    "confirmed": False,
                    "status_proposal": proposal,
                    "confirmed_warnings": [],
                    "status_proposal_freshness_id": f"route-status-{mode}",
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "diary_confirm_status_proposal",
                        "payload": {"fixture": mode},
                        "signature": "signed",
                    },
                    "signed_confirmation_evidence_required": True,
                },
            }))
            return

        if request.method == "POST" and path.endswith("/appointments/proposals/status-confirm"):
            state["confirm_count"] += 1
            requested = request.post_data_json["status_proposal"]["command"]["status"]
            if mode == "stale":
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_status_appointment",
                    "safe": False,
                    "requires_confirmation": True,
                    "autonomy_tier": "blocked",
                    "summary": "The authored-synthetic proposal is stale.",
                    "appointment": None,
                    "warnings": [],
                    "blocks": [{"code": "stale_status_proposal_freshness_id", "message": "Stale."}],
                    "audit_evidence": [],
                }))
            else:
                state["status"] = requested
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_status_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Updated.",
                    "appointment": appointment(requested),
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["diary_confirm_status_proposal"],
                }))
            return

        if request.method == "PATCH" and path.endswith("/appointments/route-status-1/status"):
            state["raw_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if request.method == "GET" and path.endswith("/appointments/route-status-1"):
            state["exact_read_count"] += 1
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointment(state["status"])))
            return
        if request.method == "GET" and path.endswith("/appointments"):
            state["list_read_count"] += 1
            route.fulfill(status=200, content_type="application/json", body=json.dumps([appointment(state["status"])]))
            return
        if request.method == "GET" and path.endswith("/patients/search"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([appointment()["patient"]]))
            return
        if path.endswith("/auth/me"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
            return
        if path.endswith("/diary/template"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "practice_name": "Authored Synthetic Practice",
                "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                "columns": [{
                    "room_label": "Room 1",
                    "assignment": "Dr Alex Shera",
                    "practitioner_id": "practitioner-route-1",
                    "practitioner_ahpra": "MED0001234567",
                }],
            }))
            return
        if path.endswith("/diary/locations"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Authored Synthetic Practice", "is_active": True}
            ]))
            return
        if path.endswith("/appointments/types") or path.endswith("/diary/waiting-areas"):
            route.fulfill(status=200, content_type="application/json", body="[]")
            return
        if path.endswith("/diary/roster"):
            route.fulfill(status=200, content_type="application/json", body='{"entries":[]}')
            return
        if path.endswith("/appointments/bernie/pilot-eligibility"):
            route.fulfill(status=200, content_type="application/json", body='{"enabled":false,"eligible":false}')
            return
        if path.endswith("/diary/events/committed"):
            route.fulfill(status=200, content_type="application/json", body='{"enabled":false,"events":[],"cursor":null}')
            return
        route.fulfill(status=200, content_type="application/json", body="{}")

    page.route("**/api/v1/**", handle)
    return state, handle


def open_selected_status_action(page, base_url: str) -> None:
    page.goto(base_url + "/diary/diary.html?smoke=true&reference_date=2026-08-13")
    page.wait_for_selector("#diary-grid", state="visible", timeout=15000)
    page.evaluate("""(appointmentJson) => {
      history.replaceState(null, "", "/diary/diary.html?reference_date=2026-08-13");
      isSmokeMode = () => false;
      activeLocationId = "loc-1";
      activeTemplate = {
        practice_name: "Authored Synthetic Practice",
        slot_defaults: { start: "09:00", end: "17:00", interval_minutes: 15 },
        columns: [{
          room_label: "Room 1",
          assignment: "Dr Alex Shera",
          practitioner_id: "practitioner-route-1",
          practitioner_ahpra: "MED0001234567"
        }]
      };
      activeAppointments = [JSON.parse(appointmentJson)];
    }""", json.dumps(appointment()))
    page.click("#btn-meta-grid-launch")
    page.fill("#meta-grid-request", "Show Margaret Thompson's upcoming appointments")
    page.press("#meta-grid-request", "Enter")
    page.wait_for_selector("[data-appointment-id='route-status-1']", state="visible")
    page.click("[data-appointment-id='route-status-1']")
    page.wait_for_selector("[data-testid='meta-grid-selected-action-console']", state="visible")
    assert page.locator("[data-testid='meta-grid-status-action']").count() == 0
    page.click("[data-testid='meta-grid-action-choice-status']")
    page.wait_for_selector("[data-testid='meta-grid-status-action']", state="visible")


def test_safe_status_composition_uses_one_existing_proposal_confirm_path(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_status_action(page, base_url)
        page.select_option("[data-testid='meta-grid-status-select']", "Arrived")
        page.click("[data-testid='meta-grid-status-submit']")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-status-feedback]')?.textContent.includes('committed')"
        )
        assert state["status"] == "Arrived"
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 1
        assert state["raw_count"] == 0
        assert state["exact_read_count"] >= 1
        assert state["list_read_count"] >= 2
        assert page.locator("[data-testid='status-proposal-dialog']").count() == 0
        assert page.locator("[data-appointment-id='route-status-1'] .meta-grid-appointment-status strong").text_content() == "Arrived"
        assert page.locator("[data-testid='meta-grid-status-select']").input_value() == "Arrived"
        assert page.locator("[data-testid='meta-grid-status-select']").evaluate("el => document.activeElement === el")
        assert page.locator("#meta-grid-back").is_disabled()
        heading = page.locator("#meta-grid-scope-summary").text_content()
        assert heading.startswith("Margaret Thompson")
        assert "appointments's" not in heading
        assert page.locator("[data-appointment-id='route-status-1']").get_attribute("aria-selected") == "true"
    finally:
        page.unroute("**/api/v1/**", handler)


def test_terminal_escape_cancels_without_closing_reception_one(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, mode="cancel")
    try:
        open_selected_status_action(page, base_url)
        page.select_option("[data-testid='meta-grid-status-select']", "Cancelled")
        page.click("[data-testid='meta-grid-status-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        page.locator("[data-testid='status-proposal-dialog'] button:has-text('Cancel')").press("Escape")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        assert state["status"] == "Booked"
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert page.locator("#bernie-meta-grid").is_visible()
        assert page.locator("[data-testid='meta-grid-status-select']").input_value() == "Booked"
        assert "cancelled" in page.locator("[data-testid='meta-grid-status-feedback']").text_content().lower()
        assert page.locator("[data-testid='meta-grid-status-select']").evaluate("el => document.activeElement === el")
    finally:
        page.unroute("**/api/v1/**", handler)


def test_stale_confirm_fails_closed_and_restores_current_status(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, mode="stale")
    try:
        open_selected_status_action(page, base_url)
        page.select_option("[data-testid='meta-grid-status-select']", "Arrived")
        page.click("[data-testid='meta-grid-status-submit']")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-status-feedback]')?.textContent.includes('not changed')"
        )
        assert state["status"] == "Booked"
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 1
        assert state["raw_count"] == 0
        assert state["exact_read_count"] >= 1
        assert page.locator("[data-testid='meta-grid-status-select']").input_value() == "Booked"
        assert page.locator("[data-appointment-id='route-status-1'] .meta-grid-appointment-status strong").text_content() == "Booked"
        assert page.locator("[data-testid='meta-grid-status-select']").evaluate("el => document.activeElement === el")
    finally:
        page.unroute("**/api/v1/**", handler)


def test_blocked_proposal_has_no_confirm_action_and_commits_nothing(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, mode="blocked")
    try:
        open_selected_status_action(page, base_url)
        page.select_option("[data-testid='meta-grid-status-select']", "Arrived")
        page.click("[data-testid='meta-grid-status-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        dialog = page.locator("[data-testid='status-proposal-dialog']")
        assert "Action Blocked" in dialog.text_content()
        assert dialog.locator("button:has-text('Confirm & Save')").count() == 0
        dialog.locator("button:has-text('Close')").click()
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        assert state["status"] == "Booked"
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert page.locator("[data-testid='meta-grid-status-select']").input_value() == "Booked"
        assert "blocked" in page.locator("[data-testid='meta-grid-status-feedback']").text_content().lower()
    finally:
        page.unroute("**/api/v1/**", handler)


def test_interruption_keeps_one_action_and_requires_fresh_reconciliation(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, mode="interrupted")
    try:
        open_selected_status_action(page, base_url)
        initial_list_reads = state["list_read_count"]
        page.select_option("[data-testid='meta-grid-status-select']", "Cancelled")
        page.click("[data-testid='meta-grid-status-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        assert page.locator("#bernie-meta-grid").get_attribute("class").find("is-private") >= 0
        assert page.locator("[data-testid='status-proposal-dialog']").count() == 1
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        page.locator("[data-testid='status-proposal-dialog'] button:has-text('Cancel')").press("Escape")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-status-feedback]')?.textContent.includes('cancelled')"
        )
        page.wait_for_timeout(100)
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert state["list_read_count"] > initial_list_reads
        assert page.locator("[data-testid='meta-grid-status-select']").input_value() == "Booked"
        assert page.locator("[data-testid='meta-grid-status-select']").evaluate("el => document.activeElement === el")
    finally:
        page.unroute("**/api/v1/**", handler)


@pytest.mark.parametrize(
    ("width", "height"),
    [(1280, 720), (768, 1024), (390, 844)],
    ids=["desktop", "tablet", "phone"],
)
def test_status_action_is_usable_without_horizontal_overflow(
    reception_page, width: int, height: int
) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, mode="responsive")
    try:
        page.set_viewport_size({"width": width, "height": height})
        open_selected_status_action(page, base_url)
        layout = page.locator("[data-testid='meta-grid-status-action']").evaluate("""panel => {
          const host = document.getElementById('bernie-meta-grid');
          const panelRect = panel.getBoundingClientRect();
          const hostRect = host.getBoundingClientRect();
          return {
            overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            withinHost: panelRect.left >= hostRect.left && panelRect.right <= hostRect.right + 1
          };
        }""")
        assert layout == {"overflow": False, "withinHost": True}
        assert page.locator("[data-testid='meta-grid-status-select']").is_visible()
        assert page.locator("[data-testid='meta-grid-status-submit']").is_visible()
        assert page.locator("[data-testid='meta-grid-status-feedback']").is_visible()
        assert state["proposal_count"] == 0
        assert state["confirm_count"] == 0
    finally:
        page.unroute("**/api/v1/**", handler)
        page.set_viewport_size({"width": 1280, "height": 720})
