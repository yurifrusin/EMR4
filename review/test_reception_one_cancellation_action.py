"""Provider-free route-intercepted browser contract for the Reception One
selected-appointment cancellation action.

Evidence labels: ``route_intercepted_browser`` and
``authored_synthetic_client_fixture``; never live backend/database operation.

Specifies: a fifth native danger ``Cancel appointment`` palette choice wired to
the shared ``meta-grid-selected-action-editor``; open/collapse/reopen and draft
that issue zero proposal/confirm/raw/status routes; one dedicated
``POST /api/v1/appointments/proposals/delete/{appointment_id}`` proposal; the
existing contained ``status-proposal-dialog`` for every admissible proposal;
one canonical ``POST /api/v1/appointments/proposals/delete/confirm`` after a
visible explicit staff confirmation; strict
``raisa.delete_confirm_public_envelope.v1`` admission with one exact
``appointment.delete_confirmation_receipt.v1``; a fresh scoped list read before
every terminal/uncertain truth display; fail-closed handling for blocked,
stale/revoked and malformed/widened responses; busy/interruption palette and
selection locks; and native keyboard/labelled-live-region/44-pixel/no-overflow
contract at desktop/tablet/phone widths.

Product implementation is intentionally absent at this source; behavioural
assertions remain red until the parallel Sol source is integrated. Do not
weaken the contract to fit the baseline.
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

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency not installed
    pytest.skip("playwright is required (pip install playwright && playwright install chromium)",
                allow_module_level=True)

# ── Frozen authored-synthetic client fixture ──────────────────────────────────
APPOINTMENT_ID = "cancel-action-1"
PATIENT_ID = "patient-cancel-1"
PRACTITIONER_ID = "practitioner-cancel-1"
APPOINTMENT_DATE = "2026-08-13"
CURRENT_START = "09:00"
CURRENT_END = "09:30"
CURRENT_DURATION = 30
CURRENT_STATUS = "Booked"
CANCEL_REASON = "PATIENT_CANCELLED"
CANCEL_NOTE = "Authored synthetic cancellation administrative note for the reception one contract."
AUTH_TOKEN = "e30.eyJyb2xlIjoic3RhZmYiLCJleHAiOjQxMDI0NDQ4MDB9.sig"
WAIT_TIMEOUT = 10000
LEAK_TOKEN = "UNTRUSTED_RECEIPT_LEAK_9981"

CANCELLATION_REASON_CODES = (
    "PATIENT_CANCELLED",
    "PATIENT_RESCHEDULED",
    "PATIENT_UNWELL",
    "PATIENT_TRANSPORT",
    "PRACTITIONER_UNAVAILABLE",
    "CLINIC_OPERATIONAL",
    "CLINIC_RESCHEDULED",
    "ADMIN_ERROR",
    "DUPLICATE_BOOKING",
    "OTHER",
)

MALFORMED_KINDS = (
    "unknown_top_level_appointment",
    "unknown_receipt_field",
    "mismatched_appointment_id",
    "mismatched_reason",
    "non_null_waiting_area",
    "unknown_warning_code",
)

ALL_ACTIONS = ("status", "time", "duration", "practitioner", "cancel")

CONSOLE = "[data-testid='meta-grid-selected-action-console']"
PALETTE = "[data-testid='meta-grid-selected-action-palette']"
EDITOR = "[data-testid='meta-grid-selected-action-editor']"
DIALOG = "[data-testid='status-proposal-dialog']"
CANCEL_CHOICE = "[data-testid='meta-grid-action-choice-cancel']"
CANCEL_PANEL = "[data-testid='meta-grid-cancellation-action']"
REASON_SELECT = "[data-testid='meta-grid-cancellation-reason-code']"
NOTE_INPUT = "[data-testid='meta-grid-cancellation-reason']"
CANCEL_SUBMIT = "[data-testid='meta-grid-cancellation-submit']"
CANCEL_FEEDBACK = "[data-testid='meta-grid-cancellation-feedback']"
CANCEL_OUTCOME = ".meta-grid-cancellation-outcome"

FIELD_PANELS = {
    "status": "[data-testid='meta-grid-status-action']",
    "time": "[data-testid='meta-grid-reschedule-action']",
    "duration": "[data-testid='meta-grid-duration-action']",
    "practitioner": "[data-testid='meta-grid-practitioner-action']",
    "cancel": CANCEL_PANEL,
}
CHOICE = {
    "status": "[data-testid='meta-grid-action-choice-status']",
    "time": "[data-testid='meta-grid-action-choice-time']",
    "duration": "[data-testid='meta-grid-action-choice-duration']",
    "practitioner": "[data-testid='meta-grid-action-choice-practitioner']",
    "cancel": CANCEL_CHOICE,
}


def appointment(status: str = CURRENT_STATUS) -> dict:
    """Authored-synthetic current appointment used by every intercepted read."""
    return {
        "id": APPOINTMENT_ID, "appointment_date": APPOINTMENT_DATE,
        "start_time_local": CURRENT_START, "end_time_local": CURRENT_END,
        "duration_minutes": CURRENT_DURATION, "status": status, "waiting_area_id": None,
        "patient_id": PATIENT_ID,
        "patient": {"id": PATIENT_ID, "first_name": "Margaret", "last_name": "Thompson",
                    "date_of_birth": "1952-03-14"},
        "practitioner_id": PRACTITIONER_ID,
        "practitioner": {"id": PRACTITIONER_ID, "first_name": "Alex", "last_name": "Shera",
                         "ahpra_number": "MED0001234567"},
        "location_id": "loc-1", "appointment_type_id": "cancel-action-type-1",
        "reason": "Authored synthetic cancellation-action review",
    }


def template() -> dict:
    return {
        "practice_name": "Authored Synthetic Practice",
        "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
        "columns": [{"room_label": "Room 1", "assignment": "Dr Alex Shera",
                     "practitioner_id": PRACTITIONER_ID, "practitioner_ahpra": "MED0001234567"}],
    }


def directory() -> list:
    return [{"id": PRACTITIONER_ID, "displayName": "Dr Alex Shera", "roleLabel": "Doctor",
             "active": True, "defaultLocation": {"id": "loc-1", "name": "Main Clinic"}}]


def strict_confirm_envelope(reason: str, note: str) -> dict:
    """Strict minimal public delete-confirm envelope (route_intercepted_browser)."""
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
            "status_reason_code": reason,
            "cancellation_reason": note,
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


def malformed_confirm_envelope(reason: str, note: str, kind: str) -> dict:
    """Widen/inject one untrusted defect into an otherwise strict envelope."""
    base = strict_confirm_envelope(reason, note)
    receipt = dict(base["receipt"])
    if kind == "unknown_top_level_appointment":
        base["appointment"] = {"id": APPOINTMENT_ID, "status": "Cancelled", "leak_probe": LEAK_TOKEN}
    elif kind == "unknown_receipt_field":
        receipt["leak_probe"] = LEAK_TOKEN
    elif kind == "mismatched_appointment_id":
        receipt["appointment_id"] = "cancel-action-other-9981"
        receipt["leak_probe"] = LEAK_TOKEN
    elif kind == "mismatched_reason":
        receipt["status_reason_code"] = "ADMIN_ERROR"
        receipt["leak_probe"] = LEAK_TOKEN
    elif kind == "non_null_waiting_area":
        receipt["waiting_area_id"] = "wa-9981"
        receipt["leak_probe"] = LEAK_TOKEN
    elif kind == "unknown_warning_code":
        receipt["warning_codes"] = ["unknown_warning_9981"]
        receipt["leak_probe"] = LEAK_TOKEN
    base["receipt"] = receipt
    return base


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # pragma: no cover - harness noise
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
    """Provider-free offline Office.js stub so diary/meta-grid boot offline."""
    page.add_init_script("""() => {
      if (!window.Office) {
        window.Office = {
          onReady: (callback) => { if (typeof callback === 'function') setTimeout(callback, 0); },
          context: { ui: { messageParent: () => {} } },
          EventType: { DialogParentMessageReceived: 'dialogParentMessageReceived' }
        };
      }
    }""")


@pytest.fixture(scope="module")
def reception_page():
    with serve_dir(DOCS) as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        stub_office(page)
        yield page, base_url
        browser.close()


def install_routes(page, *, mode: str = "safe", malformed_kind: str = None):
    """Route-intercepted surface: only the delete proposal/confirm may mutate;
    raw DELETE, status proposals and non-canonical delete confirms fail closed."""
    state = {
        "status": CURRENT_STATUS,
        "removed": False,
        "proposal_count": 0,
        "confirm_count": 0,
        "raw_count": 0,
        "status_fallback_count": 0,
        "non_canonical_confirm_count": 0,
        "unexpected_mutation_count": 0,
        "mutation_paths": [],
        "proposal_bodies": [],
        "confirm_bodies": [],
        "exact_read_count": 0,
        "list_read_count": 0,
        "routes": [],
        "baseline_route_count": 0,
    }

    def handle(route):
        request = route.request
        path = urlparse(request.url).path
        method = request.method
        state["routes"].append(f"{method} {path}")

        if method == "POST" and path.endswith(f"/appointments/proposals/delete/{APPOINTMENT_ID}"):
            state["proposal_count"] += 1
            body = request.post_data_json or {}
            state["proposal_bodies"].append(body)
            reason = body.get("status_reason_code") or ""
            note = body.get("cancellation_reason") or ""
            blocks = []
            if mode == "blocked":
                blocks = [{"code": "authored_synthetic_current_truth_block", "severity": "blocked",
                           "message": "The authored-synthetic current appointment cannot be cancelled."}]
            safe = not blocks
            autonomy = "blocked" if blocks else "proposal"
            proposal = {
                "intent": "delete_appointment",
                "safe": safe,
                "requires_confirmation": True,
                "autonomy_tier": autonomy,
                "summary": "Review the authored-synthetic appointment cancellation.",
                "command": {
                    "appointment_id": APPOINTMENT_ID,
                    "clears_waiting_area": False,
                    "cancellation_reason": note,
                    "status_reason_code": reason,
                },
                "warnings": [],
                "blocks": blocks,
                "confirm_endpoint": "/api/v1/appointments/proposals/delete/confirm",
                "confirm_payload": {
                    "confirmed": False,
                    "delete_proposal": {
                        "intent": "delete_appointment",
                        "safe": safe,
                        "requires_confirmation": True,
                        "autonomy_tier": autonomy,
                        "summary": "Review the authored-synthetic appointment cancellation.",
                        "command": {
                            "appointment_id": APPOINTMENT_ID,
                            "clears_waiting_area": False,
                            "cancellation_reason": note,
                            "status_reason_code": reason,
                        },
                        "warnings": [],
                        "blocks": blocks,
                    },
                    "confirmed_warnings": [],
                    "delete_proposal_freshness_id": f"cancel-action-{mode}",
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "diary_confirm_delete_proposal",
                        "payload": {"fixture": mode},
                        "signature": "signed",
                    },
                    "signed_confirmation_evidence_required": True,
                },
                "delete_proposal_freshness_id": f"cancel-action-{mode}",
                "signed_confirmation_evidence": {
                    "schema_version": "bernie.confirmation_evidence.v1",
                    "purpose": "diary_confirm_delete_proposal",
                    "payload": {"fixture": mode},
                    "signature": "signed",
                },
                "signed_confirmation_evidence_required": True,
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(proposal))
            return

        if method == "POST" and path.endswith("/appointments/proposals/delete/confirm"):
            state["confirm_count"] += 1
            confirm_body = request.post_data_json or {}
            state["confirm_bodies"].append(confirm_body)
            command = (confirm_body.get("delete_proposal") or {}).get("command") or {}
            reason = command.get("status_reason_code", CANCEL_REASON)
            note = command.get("cancellation_reason") or ""
            if mode == "stale":
                envelope = {
                    "schema_version": "raisa.delete_confirm_public_envelope.v1",
                    "intent": "confirm_delete_appointment",
                    "safe": False,
                    "requires_confirmation": True,
                    "autonomy_tier": "blocked",
                    "summary": "The authored-synthetic delete proposal is stale.",
                    "receipt": None,
                    "warnings": [],
                    "blocks": [{"code": "stale_delete_proposal_freshness_id", "severity": "blocked",
                                "message": "The delete proposal is stale."}],
                    "audit_evidence": [],
                }
                route.fulfill(status=200, content_type="application/json", body=json.dumps(envelope))
                return
            if mode == "malformed":
                envelope = malformed_confirm_envelope(reason, note, malformed_kind)
                route.fulfill(status=200, content_type="application/json", body=json.dumps(envelope))
                return
            state["removed"] = True
            envelope = strict_confirm_envelope(reason, note)
            route.fulfill(status=200, content_type="application/json", body=json.dumps(envelope))
            return

        if method == "DELETE" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["raw_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if method == "POST" and (
            "/appointments/proposals/status/" in path
            or path.endswith("/appointments/proposals/status-confirm")
            or "/appointments/proposals/update/" in path
            or path.endswith("/appointments/proposals/update/confirm")
        ):
            state["status_fallback_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if method == "POST" and path.endswith("/appointments/proposals/delete-confirm"):
            state["non_canonical_confirm_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if method == "GET" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["exact_read_count"] += 1
            if state["removed"]:
                route.fulfill(status=404, content_type="application/json", body="{}")
            else:
                route.fulfill(status=200, content_type="application/json",
                              body=json.dumps(appointment(state["status"])))
            return
        if method == "GET" and path.endswith("/appointments"):
            state["list_read_count"] += 1
            items = [] if state["removed"] else [appointment(state["status"])]
            route.fulfill(status=200, content_type="application/json", body=json.dumps(items))
            return
        if method == "GET" and path.endswith("/patients/search"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps([appointment()["patient"]]))
            return
        if path.endswith("/auth/me"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"role": "staff"}))
            return
        if path.endswith("/diary/template"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(template()))
            return
        if path.endswith("/diary/locations"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps([{"id": "loc-1", "name": "Authored Synthetic Practice", "is_active": True}]))
            return
        if path.endswith("/appointments/types") or path.endswith("/diary/waiting-areas"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
            return
        if path.endswith("/diary/roster"):
            route.fulfill(status=200, content_type="application/json", body='{"entries":[]}')
            return
        if path.endswith("/practitioners"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(directory()))
            return
        if path.endswith("/appointments/bernie/pilot-eligibility"):
            route.fulfill(status=200, content_type="application/json",
                          body='{"enabled":true,"eligible":true}')
            return
        if path.endswith("/diary/events/committed"):
            route.fulfill(status=200, content_type="application/json",
                          body='{"enabled":false,"events":[],"cursor":null}')
            return
        if method == "POST" and path.endswith("/graphql"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"data": {"practice": {"practitioners": directory()}}}))
            return
        if method not in {"GET", "HEAD", "OPTIONS"}:
            state["unexpected_mutation_count"] += 1
            state["mutation_paths"].append(f"{method} {path}")
            route.fulfill(status=500, content_type="application/json", body="{}")
            return
        route.fulfill(status=200, content_type="application/json", body="{}")

    page.route("**/api/v1/**", handle)
    return state, handle


def open_diary(page, base_url: str) -> None:
    """Open the native Diary grid and select the authored-synthetic appointment."""
    page.add_init_script(f"localStorage.setItem('emr4_token', {json.dumps(AUTH_TOKEN)});")
    page.goto(base_url + "/diary/diary.html?reference_date=2026-08-13")
    status_selector = f"[data-testid='appointment-status-select'][data-appointment-id='{APPOINTMENT_ID}']"
    page.wait_for_selector(status_selector, state="attached", timeout=15000)
    page.click(f".appt[data-id='{APPOINTMENT_ID}']")
    page.wait_for_selector(status_selector, state="visible")


def open_reception_one(page) -> None:
    """Open Reception One and select the appointment card (route-inert palette)."""
    page.click("#btn-meta-grid-launch")
    page.fill("#meta-grid-request", "Show Margaret Thompson's upcoming appointments")
    page.press("#meta-grid-request", "Enter")
    card = f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']"
    page.wait_for_selector(card, state="visible")
    page.click(card)
    page.wait_for_selector(CONSOLE, state="visible", timeout=WAIT_TIMEOUT)


def open_selected_appointment(page, base_url: str, state: dict) -> None:
    """Full open sequence; afterwards the fixture-startup route log is frozen."""
    open_diary(page, base_url)
    open_reception_one(page)
    page.wait_for_timeout(150)  # let startup event polling settle into the baseline
    state["baseline_route_count"] = len(state["routes"])


def count_mounted_editors(page) -> int:
    return sum(page.locator(FIELD_PANELS[action]).count() for action in ALL_ACTIONS)


def open_cancellation(page, *, reason: str = None, note: str = None) -> None:
    """Activate the cancellation choice and populate the provisional draft."""
    choice = page.locator(CANCEL_CHOICE)
    choice.scroll_into_view_if_needed()
    choice.click()
    page.wait_for_selector(CANCEL_PANEL, state="visible", timeout=WAIT_TIMEOUT)
    if reason:
        page.select_option(REASON_SELECT, reason)
    if note:
        page.fill(NOTE_INPUT, note)


def assert_zero_fallbacks(state: dict) -> None:
    assert state["proposal_count"] == 0
    assert state["confirm_count"] == 0
    assert state["raw_count"] == 0
    assert state["status_fallback_count"] == 0
    assert state["non_canonical_confirm_count"] == 0
    assert state["unexpected_mutation_count"] == 0


def assert_no_forbidden_fallbacks(state: dict) -> None:
    assert state["raw_count"] == 0
    assert state["status_fallback_count"] == 0
    assert state["non_canonical_confirm_count"] == 0
    assert state["unexpected_mutation_count"] == 0


def assert_route_log_unchanged(state: dict) -> None:
    assert len(state["routes"]) == state["baseline_route_count"]


def assert_appointment_still_present(page) -> None:
    card = page.locator(f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']")
    assert card.count() == 1
    assert card.get_attribute("aria-selected") == "true"
    assert page.locator(
        f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}'] .meta-grid-appointment-status strong"
    ).text_content() == CURRENT_STATUS


# ─── Behavioural contract (evidence label: route_intercepted_browser) ────────

def test_cancellation_palette_and_draft_are_route_inert(reception_page) -> None:
    """The fifth native danger choice opens a draft that issues zero routes."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        choices = page.locator(f"{PALETTE} button[data-testid^='meta-grid-action-choice-']")
        assert choices.count() == 5
        assert choices.nth(4).get_attribute("data-testid") == "meta-grid-action-choice-cancel"

        cancel_choice = page.locator(CANCEL_CHOICE)
        assert cancel_choice.evaluate("el => el.tagName") == "BUTTON"
        assert cancel_choice.get_attribute("role") is None
        tabindex = cancel_choice.get_attribute("tabindex")
        assert tabindex is None or tabindex in ("0", "-1")
        assert cancel_choice.get_attribute("aria-controls") == "meta-grid-selected-action-editor"
        assert cancel_choice.get_attribute("aria-expanded") == "false"
        box = cancel_choice.bounding_box()
        assert box is not None and box["width"] >= 44 and box["height"] >= 44
        assert count_mounted_editors(page) == 0

        # Open: ten exact reason options, optional 500-character note.
        open_cancellation(page, reason=None, note=None)
        assert page.locator(CANCEL_PANEL).count() == 1
        option_values = page.locator(f"{REASON_SELECT} option").evaluate_all(
            "els => els.map(el => el.value)"
        )
        assert tuple(option_values) == ("", *CANCELLATION_REASON_CODES)
        assert page.locator(CANCEL_SUBMIT).is_disabled()
        page.select_option(REASON_SELECT, CANCEL_REASON)
        assert not page.locator(CANCEL_SUBMIT).is_disabled()
        note = "x" * 500
        page.fill(NOTE_INPUT, note)
        assert page.locator(NOTE_INPUT).input_value() == note

        # Collapse discards the draft; reopen restores current/default truth.
        page.locator(CANCEL_CHOICE).click()
        page.wait_for_selector(CANCEL_PANEL, state="detached", timeout=WAIT_TIMEOUT)
        assert count_mounted_editors(page) == 0
        open_cancellation(page, reason=None, note=None)
        assert page.locator(REASON_SELECT).input_value() == ""
        assert page.locator(NOTE_INPUT).input_value() == ""
        assert page.locator(CANCEL_SUBMIT).is_disabled()

        assert_zero_fallbacks(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_safe_cancellation_requires_dialog_and_fresh_removal(reception_page) -> None:
    """One dedicated proposal, one canonical visible confirm, strict public
    receipt, then a fresh list read removes the appointment."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_cancellation(page, reason=CANCEL_REASON, note=CANCEL_NOTE)
        page.locator(CANCEL_SUBMIT).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        dialog = page.locator(DIALOG)
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert dialog.locator("button:has-text('Confirm & Save')").count() == 1
        assert dialog.locator("button:has-text('Cancel')").count() == 1
        assert dialog.locator("[data-testid='status-confirm-current-truth-boundary']").count() == 1

        initial_list = state["list_read_count"]
        dialog.locator("button:has-text('Confirm & Save')").click()
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_selector(CANCEL_OUTCOME, state="visible", timeout=WAIT_TIMEOUT)

        assert state["confirm_count"] == 1
        assert state["removed"] is True
        assert state["list_read_count"] > initial_list
        # The confirm used the proposal's exact canonical endpoint + prepared payload.
        body = state["confirm_bodies"][0]
        assert body.get("confirmed") is True
        command = (body.get("delete_proposal") or {}).get("command") or {}
        assert command.get("appointment_id") == APPOINTMENT_ID
        assert command.get("status_reason_code") == CANCEL_REASON
        assert command.get("cancellation_reason") == CANCEL_NOTE
        # Fresh projection removed the appointment; only the cancellation outcome shows.
        assert page.locator(f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']").count() == 0
        assert page.locator(CANCEL_OUTCOME).count() == 1
        assert "cancelled and removed" in page.locator(CANCEL_OUTCOME).text_content().lower()
        for other in ("status", "reschedule", "duration", "practitioner"):
            assert page.locator(f".meta-grid-{other}-outcome").count() == 0
        assert page.locator(CANCEL_PANEL).count() == 0
        assert_no_forbidden_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_staff_escape_cancels_without_confirm_and_retains_truth(reception_page) -> None:
    """Escape sends no confirm, runs a fresh list read, retains current truth."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_cancellation(page, reason=CANCEL_REASON, note=CANCEL_NOTE)
        page.locator(CANCEL_SUBMIT).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        initial_list = state["list_read_count"]
        page.locator(DIALOG).press("Escape")
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)

        assert state["confirm_count"] == 0
        assert state["list_read_count"] > initial_list
        assert state["removed"] is False
        assert_appointment_still_present(page)
        assert page.locator(REASON_SELECT).input_value() == CANCEL_REASON
        assert page.locator(NOTE_INPUT).input_value() == CANCEL_NOTE
        page.wait_for_function(
            "() => { const el = document.activeElement; return Boolean(el && ("
            "el.dataset.testid === 'meta-grid-action-choice-cancel' || "
            "el.dataset.testid === 'meta-grid-cancellation-reason-code')); }",
            timeout=WAIT_TIMEOUT,
        )
        assert_no_forbidden_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_blocked_proposal_is_close_only_and_never_confirms(reception_page) -> None:
    """Typed block: close-only dialog, no confirm request, fresh reconciliation."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="blocked")
    try:
        open_selected_appointment(page, base_url, state)
        open_cancellation(page, reason=CANCEL_REASON, note=CANCEL_NOTE)
        page.locator(CANCEL_SUBMIT).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        dialog = page.locator(DIALOG)
        assert "Action Blocked" in dialog.text_content()
        assert dialog.locator("button:has-text('Confirm & Save')").count() == 0
        assert dialog.locator("button:has-text('Cancel')").count() == 0
        assert state["confirm_count"] == 0

        initial_list = state["list_read_count"]
        dialog.locator("button:has-text('Close')").click()
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)

        assert state["list_read_count"] > initial_list
        assert state["removed"] is False
        assert_appointment_still_present(page)
        assert page.locator(REASON_SELECT).input_value() == CANCEL_REASON
        assert page.locator(NOTE_INPUT).input_value() == CANCEL_NOTE
        assert page.locator(CANCEL_OUTCOME).count() == 0
        assert_no_forbidden_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_stale_or_revoked_confirm_fails_closed_without_fallback(reception_page) -> None:
    """Typed blocked confirm: no optimistic removal, one fresh list read, no fallback."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="stale")
    try:
        open_selected_appointment(page, base_url, state)
        open_cancellation(page, reason=CANCEL_REASON, note=CANCEL_NOTE)
        page.locator(CANCEL_SUBMIT).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        initial_list = state["list_read_count"]
        page.locator(DIALOG).locator("button:has-text('Confirm & Save')").click()
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_function(
            "() => { const f = document.querySelector('[data-testid=meta-grid-cancellation-feedback]'); "
            "return Boolean(f && /blocked|not changed|not confirmed|restored|stale/i.test(f.textContent)); }",
            timeout=WAIT_TIMEOUT)

        assert state["confirm_count"] == 1
        assert state["list_read_count"] > initial_list
        assert state["removed"] is False
        assert_appointment_still_present(page)
        assert page.locator(CANCEL_OUTCOME).count() == 0
        assert page.locator(REASON_SELECT).input_value() == CANCEL_REASON
        assert page.locator(NOTE_INPUT).input_value() == CANCEL_NOTE
        assert_no_forbidden_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)


@pytest.mark.parametrize("malformed_kind", MALFORMED_KINDS)
def test_malformed_or_widened_public_receipt_fails_closed(reception_page, malformed_kind) -> None:
    """Unknown/widened public receipt: fresh reconciliation, never untrusted render."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="malformed", malformed_kind=malformed_kind)
    try:
        open_selected_appointment(page, base_url, state)
        open_cancellation(page, reason=CANCEL_REASON, note=CANCEL_NOTE)
        page.locator(CANCEL_SUBMIT).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        initial_list = state["list_read_count"]
        page.locator(DIALOG).locator("button:has-text('Confirm & Save')").click()
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_timeout(200)

        assert state["confirm_count"] == 1
        assert state["list_read_count"] > initial_list
        assert state["removed"] is False
        assert_appointment_still_present(page)
        assert page.locator(CANCEL_OUTCOME).count() == 0
        assert LEAK_TOKEN not in page.locator("#bernie-meta-grid").text_content()
        feedback = page.locator(CANCEL_FEEDBACK).text_content().lower()
        assert "committed" not in feedback
        assert page.locator(REASON_SELECT).input_value() == CANCEL_REASON
        assert page.locator(NOTE_INPUT).input_value() == CANCEL_NOTE
        assert_no_forbidden_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_busy_confirmation_locks_palette_reselection_and_interruption(reception_page) -> None:
    """While the confirmation dialog is busy every choice and reselection locks;
    interruption creates no second command and a fresh result is required."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_cancellation(page, reason=CANCEL_REASON, note=CANCEL_NOTE)
        page.locator(CANCEL_SUBMIT).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        dialog = page.locator(DIALOG)
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0

        for action in ALL_ACTIONS:
            assert page.locator(CHOICE[action]).is_disabled()
        assert count_mounted_editors(page) == 1
        assert page.locator(CANCEL_PANEL).count() == 1
        card = page.locator(f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']")
        assert card.get_attribute("aria-selected") == "true"
        for _ in range(4):
            page.keyboard.press("Tab")
            assert dialog.locator("button:focus").count() == 1

        page.evaluate("window.dispatchEvent(new Event('blur'))")
        assert page.locator(DIALOG).count() == 1
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0

        initial_list = state["list_read_count"]
        page.keyboard.press("Escape")
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_function(
            "() => { const c = document.querySelector(\"[data-testid='meta-grid-action-choice-cancel']\"); "
            "return Boolean(c) && !c.disabled; }",
            timeout=WAIT_TIMEOUT)
        assert state["list_read_count"] > initial_list
        assert state["confirm_count"] == 0
        assert state["removed"] is False
        assert page.locator(REASON_SELECT).input_value() == CANCEL_REASON
        assert page.locator(NOTE_INPUT).input_value() == CANCEL_NOTE
        assert_no_forbidden_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)


@pytest.mark.parametrize(("width", "height"), [(1280, 720), (768, 1024), (390, 844)],
                         ids=["desktop", "tablet", "phone"])
def test_cancellation_accessibility_and_responsive_contract(reception_page, width, height) -> None:
    """Native keyboard activation, labelled editor, one live region, 44px, no overflow."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        page.set_viewport_size({"width": width, "height": height})
        open_selected_appointment(page, base_url, state)
        cancel_choice = page.locator(CANCEL_CHOICE)
        box = cancel_choice.bounding_box()
        assert box is not None and box["width"] >= 44 and box["height"] >= 44
        cancel_choice.focus()
        page.keyboard.press("Enter")
        page.wait_for_selector(CANCEL_PANEL, state="visible", timeout=WAIT_TIMEOUT)

        editor = page.locator(EDITOR)
        assert editor.get_attribute("aria-labelledby") or editor.get_attribute("aria-label")
        panel = page.locator(CANCEL_PANEL)
        assert panel.get_attribute("aria-labelledby") or panel.get_attribute("aria-label")
        live = editor.locator("[role='status'][aria-live='polite'][aria-atomic='true']")
        assert live.count() == 1

        layout = page.locator(CONSOLE).evaluate("""consoleEl => {
          const host = document.getElementById('bernie-meta-grid');
          const editor = consoleEl.querySelector('[data-testid="meta-grid-selected-action-editor"]');
          return {
            docOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            hostOverflow: host.scrollWidth > host.clientWidth,
            consoleOverflow: consoleEl.scrollWidth > consoleEl.clientWidth,
            editorOverflow: editor ? editor.scrollWidth > editor.clientWidth : false
          };
        }""")
        assert layout == {"docOverflow": False, "hostOverflow": False,
                          "consoleOverflow": False, "editorOverflow": False}
        assert_zero_fallbacks(state)
    finally:
        page.unroute("**/api/v1/**", handler)
        page.set_viewport_size({"width": 1280, "height": 720})


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("This module is a pytest contract; do not run it directly.")
