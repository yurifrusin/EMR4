"""Route-intercepted browser evidence for ordinary Diary cancellation convergence.

All fixtures are authored synthetic.  No backend, database, provider, patient
record, credential or external network is used.  The contract is deliberately
limited to the ordinary edit-modal consumer: one dedicated delete proposal,
one visible confirmation, one canonical delete-confirm request, strict minimal
public-envelope admission and a fresh authorised Diary read before displaying
terminal or uncertain truth.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import json
import threading
from pathlib import Path
from urllib.parse import urlparse

import pytest

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - optional local review dependency
    pytest.skip(
        "playwright is required (pip install playwright && playwright install chromium)",
        allow_module_level=True,
    )


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
APPOINTMENT_ID = "ordinary-cancel-1"
PATIENT_ID = "ordinary-patient-1"
PRACTITIONER_ID = "ordinary-practitioner-1"
APPOINTMENT_DATE = "2026-08-17"
REASON = "PATIENT_TRANSPORT"
NOTE = "Authored synthetic patient transport note."
AUTH_TOKEN = "e30.eyJyb2xlIjoic3RhZmYiLCJleHAiOjQxMDI0NDQ4MDB9.sig"
WAIT_TIMEOUT = 10000
DIALOG = "[data-testid='status-proposal-dialog']"


def appointment(status: str = "Booked") -> dict:
    return {
        "id": APPOINTMENT_ID,
        "appointment_date": APPOINTMENT_DATE,
        "start_time_local": "09:00:00",
        "end_time_local": "09:30:00",
        "duration_minutes": 30,
        "status": status,
        "waiting_area_id": None,
        "patient_id": PATIENT_ID,
        "patient": {
            "id": PATIENT_ID,
            "first_name": "Margaret",
            "last_name": "Thompson",
            "date_of_birth": "1952-03-14",
        },
        "practitioner_id": PRACTITIONER_ID,
        "practitioner": {
            "id": PRACTITIONER_ID,
            "first_name": "Alex",
            "last_name": "Shera",
            "ahpra_number": "MED0001234567",
        },
        "appointment_type_id": None,
        "location_id": "loc-1",
        "reason": "Authored synthetic review",
    }


def delete_proposal(*, blocked: bool = False) -> dict:
    blocks = []
    if blocked:
        blocks = [
            {
                "code": "authored_synthetic_current_truth_block",
                "severity": "blocked",
                "message": "Current authored-synthetic truth blocks cancellation.",
            }
        ]
    safe = not blocked
    autonomy_tier = "proposal" if safe else "blocked"
    command = {
        "appointment_id": APPOINTMENT_ID,
        "clears_waiting_area": False,
        "cancellation_reason": NOTE,
        "status_reason_code": REASON,
    }
    proposal = {
        "intent": "delete_appointment",
        "safe": safe,
        "requires_confirmation": True,
        "autonomy_tier": autonomy_tier,
        "summary": "Review the authored-synthetic cancellation.",
        "command": command,
        "warnings": [],
        "blocks": blocks,
    }
    if blocked:
        return proposal
    return {
        **proposal,
        "confirm_endpoint": "/api/v1/appointments/proposals/delete/confirm",
        "confirm_payload": {
            "confirmed": False,
            "delete_proposal": proposal,
            "confirmed_warnings": [],
            "delete_proposal_freshness_id": "ordinary-delete-fresh-1",
            "signed_confirmation_evidence": {
                "schema_version": "bernie.confirmation_evidence.v1",
                "purpose": "diary_confirm_delete_proposal",
                "payload": {"fixture": "ordinary-cancellation"},
                "signature": "signed",
            },
            "signed_confirmation_evidence_required": True,
        },
        "delete_proposal_freshness_id": "ordinary-delete-fresh-1",
        "signed_confirmation_evidence": {
            "schema_version": "bernie.confirmation_evidence.v1",
            "purpose": "diary_confirm_delete_proposal",
            "payload": {"fixture": "ordinary-cancellation"},
            "signature": "signed",
        },
        "signed_confirmation_evidence_required": True,
    }


def strict_public_envelope() -> dict:
    return {
        "schema_version": "raisa.delete_confirm_public_envelope.v1",
        "intent": "confirm_delete_appointment",
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "confirmed_write",
        "summary": "The authored-synthetic appointment was cancelled.",
        "receipt": {
            "schema_version": "appointment.delete_confirmation_receipt.v1",
            "appointment_id": APPOINTMENT_ID,
            "status": "Cancelled",
            "status_reason_code": REASON,
            "cancellation_reason": NOTE,
            "waiting_area_id": None,
            "warning_codes": [],
        },
        "warnings": [],
        "blocks": [],
        "audit_evidence": [
            "delete_product_adapter_v1",
            "delete_signed_confirmation_evidence_verified",
            "delete_current_authority_rechecked",
        ],
    }


def blocked_public_envelope() -> dict:
    return {
        "schema_version": "raisa.delete_confirm_public_envelope.v1",
        "intent": "confirm_delete_appointment",
        "safe": False,
        "requires_confirmation": True,
        "autonomy_tier": "blocked",
        "summary": "The authored-synthetic proposal is stale.",
        "receipt": None,
        "warnings": [],
        "blocks": [
            {
                "code": "stale_delete_proposal_freshness_id",
                "severity": "blocked",
                "message": "The delete proposal is stale.",
            }
        ],
        "audit_evidence": [],
    }


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # pragma: no cover - review noise
        pass


@contextlib.contextmanager
def serve_dir(root: Path):
    handler = functools.partial(_QuietHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def stub_office(page) -> None:
    page.add_init_script(
        """() => {
          window.Office = window.Office || {
            onReady: callback => { if (typeof callback === 'function') setTimeout(callback, 0); },
            context: { ui: { messageParent: () => {} } },
            EventType: { DialogParentMessageReceived: 'dialogParentMessageReceived' }
          };
        }"""
    )


@pytest.fixture(scope="module")
def browser_surface():
    with serve_dir(DOCS) as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser, base_url
        browser.close()


def install_routes(page, *, mode: str) -> tuple[dict, object]:
    state = {
        "operation_started": False,
        "removed": False,
        "proposal_count": 0,
        "confirm_count": 0,
        "fresh_read_count": 0,
        "proposal_bodies": [],
        "confirm_bodies": [],
        "confirm_keys": [],
        "forbidden": [],
    }

    def fulfill_json(route, body, status=200):
        route.fulfill(status=status, content_type="application/json", body=json.dumps(body))

    def handle(route):
        request = route.request
        path = urlparse(request.url).path
        method = request.method

        if method == "POST" and path.endswith(f"/appointments/proposals/delete/{APPOINTMENT_ID}"):
            state["operation_started"] = True
            state["proposal_count"] += 1
            state["proposal_bodies"].append(request.post_data_json or {})
            if mode == "proposal_404":
                fulfill_json(route, {"detail": "Dedicated delete proposal unavailable."}, 404)
            else:
                fulfill_json(route, delete_proposal(blocked=mode == "proposal_blocked"))
            return

        if method == "POST" and path.endswith("/appointments/proposals/delete/confirm"):
            state["confirm_count"] += 1
            state["confirm_bodies"].append(request.post_data_json or {})
            state["confirm_keys"].append(request.headers.get("idempotency-key"))
            if mode == "confirm_503":
                fulfill_json(route, {"detail": "Authored-synthetic transport uncertainty."}, 503)
                return
            if mode == "confirm_blocked":
                fulfill_json(route, blocked_public_envelope())
                return
            envelope = strict_public_envelope()
            if mode == "malformed_top_level":
                envelope["appointment"] = {"id": APPOINTMENT_ID, "forbidden": True}
            elif mode == "malformed_receipt":
                envelope["receipt"]["forbidden"] = True
            if mode in {"committed", "replay"}:
                state["removed"] = True
            fulfill_json(route, envelope)
            return

        if method in {"DELETE", "PUT", "PATCH"} or (
            method == "POST"
            and (
                "/appointments/proposals/status/" in path
                or path.endswith("/appointments/proposals/status-confirm")
                or path.endswith("/appointments/proposals/delete-confirm")
            )
        ):
            state["forbidden"].append(f"{method} {path}")
            fulfill_json(route, {"detail": "forbidden compatibility route"}, 500)
            return

        if method == "GET" and path.endswith("/appointments"):
            if state["operation_started"]:
                state["fresh_read_count"] += 1
                if mode == "refresh_failure":
                    fulfill_json(route, {"detail": "Authored-synthetic refresh failure."}, 503)
                    return
            items = [] if state["removed"] else [appointment()]
            fulfill_json(route, items)
            return
        if method == "GET" and path.endswith(f"/appointments/{APPOINTMENT_ID}/audit"):
            fulfill_json(route, [])
            return
        if path.endswith("/auth/me"):
            fulfill_json(route, {"role": "staff"})
            return
        if path.endswith("/diary/template"):
            fulfill_json(
                route,
                {
                    "practice_name": "Authored Synthetic Practice",
                    "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
                    "columns": [
                        {
                            "room_label": "Room 1",
                            "assignment": "Dr Alex Shera",
                            "practitioner_id": PRACTITIONER_ID,
                            "practitioner_ahpra": "MED0001234567",
                        }
                    ],
                },
            )
            return
        if method == "POST" and path.endswith("/graphql"):
            fulfill_json(
                route,
                {
                    "data": {
                        "practice": {
                            "practitioners": [
                                {
                                    "id": PRACTITIONER_ID,
                                    "displayName": "Dr Alex Shera",
                                    "roleLabel": "GP",
                                    "active": True,
                                    "defaultLocation": {"id": "loc-1", "name": "Main Clinic"},
                                }
                            ]
                        }
                    }
                },
            )
            return
        if path.endswith("/diary/locations"):
            fulfill_json(route, [{"id": "loc-1", "name": "Main Clinic", "is_active": True}])
            return
        if path.endswith("/appointments/types") or path.endswith("/diary/waiting-areas"):
            fulfill_json(route, [])
            return
        if path.endswith("/diary/roster"):
            fulfill_json(route, {"entries": []})
            return
        if path.endswith("/appointments/bernie/pilot-eligibility"):
            fulfill_json(route, {"surface": "bernie_staff_review", "enabled": False, "eligible": False})
            return
        if path.endswith("/diary/events/committed"):
            fulfill_json(route, {"enabled": False, "events": [], "cursor": None})
            return
        fulfill_json(route, {})

    page.route("**/api/v1/**", handle)
    return state, handle


@contextlib.contextmanager
def ordinary_cancellation(browser_surface, *, mode: str):
    browser, base_url = browser_surface
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    stub_office(page)
    page.add_init_script(f"localStorage.setItem('emr4_token', {json.dumps(AUTH_TOKEN)});")
    state, handler = install_routes(page, mode=mode)
    try:
        page.goto(base_url + f"/diary/diary.html?reference_date={APPOINTMENT_DATE}")
        page.wait_for_function(
            f"() => typeof openBookingModalForEdit === 'function' && "
            f"activeAppointments.some(item => String(item.id) === {json.dumps(APPOINTMENT_ID)})",
            timeout=15000,
        )
        page.evaluate(
            f"() => openBookingModalForEdit(activeAppointments.find("
            f"item => String(item.id) === {json.dumps(APPOINTMENT_ID)}))"
        )
        page.wait_for_selector("#booking-modal:not(.hidden)", state="visible", timeout=WAIT_TIMEOUT)
        page.evaluate(
            """() => {
              window.__ordinaryDiaryReadEvents = 0;
              window.addEventListener('emr4:diary-read-complete', () => {
                window.__ordinaryDiaryReadEvents += 1;
              });
            }"""
        )
        yield page, state
    finally:
        page.unroute("**/api/v1/**", handler)
        page.close()


def prepare_and_submit(page) -> None:
    button = page.locator("#btn-booking-delete")
    button.click()
    page.fill("#booking-cancel-reason", NOTE)
    page.select_option("[data-testid='booking-status-reason-code']", REASON)
    button.click()


def assert_canonical_request(state: dict) -> None:
    assert state["proposal_count"] == 1
    assert state["proposal_bodies"] == [
        {"intent": "delete_appointment", "cancellation_reason": NOTE, "status_reason_code": REASON}
    ]
    assert state["forbidden"] == []


@pytest.mark.parametrize("mode", ["committed", "replay"], ids=["committed", "replay-equivalent"])
def test_committed_receipt_reconciles_to_fresh_absence(browser_surface, mode) -> None:
    with ordinary_cancellation(browser_surface, mode=mode) as (page, state):
        # The deliberate first click only reveals the provisional reason controls.
        page.locator("#btn-booking-delete").click()
        assert state["proposal_count"] == state["confirm_count"] == 0
        page.fill("#booking-cancel-reason", NOTE)
        page.select_option("[data-testid='booking-status-reason-code']", REASON)
        page.locator("#btn-booking-delete").click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        assert state["confirm_count"] == 0
        page.locator(DIALOG).locator("button:has-text('Confirm & Save')").click()
        page.wait_for_selector("#booking-modal.hidden", state="attached", timeout=WAIT_TIMEOUT)

        assert_canonical_request(state)
        assert state["confirm_count"] == 1
        assert state["confirm_keys"] == ["delete-confirm-ordinary-delete-fresh-1"]
        assert state["confirm_bodies"][0]["confirmed"] is True
        assert state["fresh_read_count"] >= 1
        assert page.evaluate("window.__ordinaryDiaryReadEvents") >= 1
        assert page.locator(f".appt[data-id='{APPOINTMENT_ID}']").count() == 0
        assert "cancelled in the current diary" in page.locator("#diary-status").text_content().lower()


def test_staff_cancels_dialog_without_confirm_then_current_truth_is_refreshed(browser_surface) -> None:
    with ordinary_cancellation(browser_surface, mode="staff_cancel") as (page, state):
        prepare_and_submit(page)
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        page.locator(DIALOG).locator("button:has-text('Cancel')").click()
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_function("() => window.__ordinaryDiaryReadEvents >= 1", timeout=WAIT_TIMEOUT)

        assert_canonical_request(state)
        assert state["confirm_count"] == 0
        assert state["fresh_read_count"] >= 1
        assert page.locator("#booking-modal:not(.hidden)").count() == 1
        assert page.locator(f".appt[data-id='{APPOINTMENT_ID}']").count() == 1
        assert "not confirmed" in page.locator("#diary-status").text_content().lower()


def test_blocked_proposal_is_close_only_and_never_confirms(browser_surface) -> None:
    with ordinary_cancellation(browser_surface, mode="proposal_blocked") as (page, state):
        prepare_and_submit(page)
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        dialog = page.locator(DIALOG)
        assert dialog.locator("button:has-text('Confirm & Save')").count() == 0
        dialog.locator("button:has-text('Close')").click()
        page.wait_for_function("() => window.__ordinaryDiaryReadEvents >= 1", timeout=WAIT_TIMEOUT)

        assert_canonical_request(state)
        assert state["confirm_count"] == 0
        assert state["fresh_read_count"] >= 1
        assert page.locator(f".appt[data-id='{APPOINTMENT_ID}']").count() == 1


@pytest.mark.parametrize(
    "mode",
    ["confirm_blocked", "confirm_503", "malformed_top_level", "malformed_receipt", "contradiction"],
)
def test_confirm_uncertainty_never_assumes_success_and_reconciles(browser_surface, mode) -> None:
    with ordinary_cancellation(browser_surface, mode=mode) as (page, state):
        prepare_and_submit(page)
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        page.locator(DIALOG).locator("button:has-text('Confirm & Save')").click()
        page.wait_for_function("() => window.__ordinaryDiaryReadEvents >= 1", timeout=WAIT_TIMEOUT)

        assert_canonical_request(state)
        assert state["confirm_count"] == 1
        assert state["fresh_read_count"] >= 1
        assert page.locator(f".appt[data-id='{APPOINTMENT_ID}']").count() == 1
        assert page.locator("#booking-modal:not(.hidden)").count() == 1
        feedback = page.locator("#booking-error").text_content().lower()
        assert "successfully" not in feedback
        assert "current diary" in feedback


def test_delete_proposal_404_has_no_status_or_raw_fallback(browser_surface) -> None:
    with ordinary_cancellation(browser_surface, mode="proposal_404") as (page, state):
        prepare_and_submit(page)
        page.wait_for_function("() => window.__ordinaryDiaryReadEvents >= 1", timeout=WAIT_TIMEOUT)

        assert_canonical_request(state)
        assert state["confirm_count"] == 0
        assert state["fresh_read_count"] >= 1
        assert page.locator(f".appt[data-id='{APPOINTMENT_ID}']").count() == 1
        assert "current diary refreshed" in page.locator("#booking-error").text_content().lower()


def test_reconciliation_failure_disables_cancellation_until_refresh(browser_surface) -> None:
    with ordinary_cancellation(browser_surface, mode="refresh_failure") as (page, state):
        prepare_and_submit(page)
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        page.locator(DIALOG).locator("button:has-text('Confirm & Save')").click()
        page.wait_for_function(
            "() => document.querySelector('#btn-booking-delete')?.dataset.refreshRequired === 'true'",
            timeout=WAIT_TIMEOUT,
        )

        assert_canonical_request(state)
        assert state["confirm_count"] == 1
        assert state["fresh_read_count"] >= 1
        button = page.locator("#btn-booking-delete")
        assert button.is_disabled()
        assert button.text_content() == "Refresh Required"
        assert button.get_attribute("aria-disabled") == "true"
        assert page.evaluate("window.__ordinaryDiaryReadEvents") == 0
        feedback = page.locator("#booking-error").text_content().lower()
        assert "no outcome has been assumed" in feedback
        assert page.locator("#booking-modal:not(.hidden)").count() == 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("This module is a pytest contract; do not run it directly.")
