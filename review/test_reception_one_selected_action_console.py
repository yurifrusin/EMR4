"""Provider-free route-intercepted browser contract for the Reception One
selected-action console (progressive-disclosure composition).

Specifies: a patient-minimized current-truth summary; four native action
choices (status, time, duration, practitioner) with ``aria-controls`` on the
shared ``meta-grid-selected-action-editor`` and exactly one ``aria-expanded``;
zero-or-one mounted field editor; zero routes on palette open/collapse/switch;
idle draft disposal with a no-change announce; busy/dialog/interruption palette
locks; unchanged status and update proposal/confirm traces with zero raw
PUT/PATCH; fresh rebind or action-specific terminal removal; native keyboard
semantics, a labelled editor with one polite atomic live region, 44-pixel
targets and no horizontal overflow at desktop/tablet/phone widths.

Evidence labels: ``route_intercepted_browser`` and
``authored_synthetic_client_fixture``; never live product operation. The
assertions are intentionally red before Sol's parallel product source lands.
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

APPOINTMENT_ID = "action-console-1"
PATIENT_ID = "patient-console-1"
CURRENT_PRACTITIONER_ID = "practitioner-console-current"
TARGET_PRACTITIONER_ID = "practitioner-console-target"
CURRENT_PRACTITIONER = "Dr Alex Example"
TARGET_PRACTITIONER = "Dr Anika Patel"
CURRENT_AHPRA = "MED0000000001"
TARGET_AHPRA = "MED0000000002"
CURRENT_START = "09:00"
REQUESTED_START = "09:15"
CURRENT_DURATION = 30
REQUESTED_DURATION = 45
APPOINTMENT_DATE = "2026-08-13"
CURRENT_STATUS = "Booked"
REQUESTED_STATUS = "Arrived"
TERMINAL_STATUS = "Cancelled"
AUTH_TOKEN = "e30.eyJyb2xlIjoic3RhZmYiLCJleHAiOjQxMDI0NDQ4MDB9.sig"

WAIT_TIMEOUT = 10000

CONSOLE = "[data-testid='meta-grid-selected-action-console']"
PALETTE = "[data-testid='meta-grid-selected-action-palette']"
EDITOR = "[data-testid='meta-grid-selected-action-editor']"
SUMMARY = "[data-testid='meta-grid-selected-action-summary']"
DIALOG = "[data-testid='status-proposal-dialog']"

FIELDS = ("status", "time", "duration", "practitioner")

def _tid(testid: str) -> str:
    return f"[data-testid='{testid}']"

PANEL_ID = {"status": "meta-grid-status-action", "time": "meta-grid-reschedule-action",
            "duration": "meta-grid-duration-action", "practitioner": "meta-grid-practitioner-action"}
CONTROL_ID = {"status": "meta-grid-status-select", "time": "meta-grid-reschedule-time",
              "duration": "meta-grid-duration-select", "practitioner": "meta-grid-practitioner-select"}
SUBMIT_ID = {"status": "meta-grid-status-submit", "time": "meta-grid-reschedule-submit",
             "duration": "meta-grid-duration-submit", "practitioner": "meta-grid-practitioner-submit"}
FEEDBACK_ID = {"status": "meta-grid-status-feedback", "time": "meta-grid-reschedule-feedback",
               "duration": "meta-grid-duration-feedback", "practitioner": "meta-grid-practitioner-feedback"}
FIELD_PANELS = {field: _tid(PANEL_ID[field]) for field in FIELDS}
CHOICE = {field: _tid(f"meta-grid-action-choice-{field}") for field in FIELDS}
FIELD_CONTROL = {field: _tid(CONTROL_ID[field]) for field in FIELDS}
SUBMIT = {field: _tid(SUBMIT_ID[field]) for field in FIELDS}
FIELD_CURRENT = {"status": CURRENT_STATUS, "time": CURRENT_START,
                 "duration": str(CURRENT_DURATION), "practitioner": ""}
FIELD_REQUESTED = {"status": REQUESTED_STATUS, "time": REQUESTED_START,
                   "duration": str(REQUESTED_DURATION), "practitioner": TARGET_PRACTITIONER_ID}
FIELD_WARNING_REQUESTED = {"status": TERMINAL_STATUS, "time": REQUESTED_START,
                           "duration": str(REQUESTED_DURATION), "practitioner": TARGET_PRACTITIONER_ID}

def _add_minutes(hhmm: str, minutes: int) -> str:
    hours, mins = map(int, hhmm.split(":"))
    total = (hours * 60 + mins + minutes) % 1440
    return f"{total // 60:02d}:{total % 60:02d}"

def appointment(status: str = CURRENT_STATUS, start: str = CURRENT_START,
                duration: int = CURRENT_DURATION,
                practitioner_id: str = CURRENT_PRACTITIONER_ID) -> dict:
    """Authored-synthetic current appointment used by every intercepted read."""
    is_target = practitioner_id == TARGET_PRACTITIONER_ID
    first = "Anika" if is_target else "Alex"
    last = "Patel" if is_target else "Example"
    return {
        "id": APPOINTMENT_ID, "appointment_date": APPOINTMENT_DATE,
        "start_time_local": start, "end_time_local": _add_minutes(start, duration),
        "duration_minutes": duration, "status": status, "waiting_area_id": None,
        "patient_id": PATIENT_ID,
        "patient": {"id": PATIENT_ID, "first_name": "Margaret", "last_name": "Thompson",
                    "date_of_birth": "1952-03-14"},
        "practitioner_id": practitioner_id,
        "practitioner": {"id": practitioner_id, "first_name": first, "last_name": last,
                         "ahpra_number": TARGET_AHPRA if is_target else CURRENT_AHPRA},
        "location_id": "loc-1", "appointment_type_id": "action-console-type-1",
        "reason": "Authored synthetic selected-action-console review",
    }

def template() -> dict:
    return {
        "practice_name": "Authored Synthetic Practice",
        "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
        "columns": [
            {"room_label": "Room 1", "assignment": CURRENT_PRACTITIONER,
             "practitioner_id": CURRENT_PRACTITIONER_ID, "practitioner_ahpra": CURRENT_AHPRA},
            {"room_label": "Room 2", "assignment": TARGET_PRACTITIONER,
             "practitioner_id": TARGET_PRACTITIONER_ID, "practitioner_ahpra": TARGET_AHPRA},
        ],
    }

def directory() -> list:
    def row(pid: str, name: str, active: bool = True) -> dict:
        return {"id": pid, "displayName": name, "roleLabel": "Doctor",
                "active": active, "defaultLocation": {"id": "loc-1", "name": "Main Clinic"}}
    return [row(CURRENT_PRACTITIONER_ID, CURRENT_PRACTITIONER),
            row(TARGET_PRACTITIONER_ID, TARGET_PRACTITIONER),
            row("practitioner-console-inactive", "Dr Inactive Lee", active=False)]

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

def install_routes(page, *, mode: str = "safe") -> tuple[dict, object]:
    """Route-intercepted surface: only the status/update proposal-confirm mutate;
    a raw appointment ``PUT``/``PATCH`` fails closed; other non-reads are counted."""
    state = {
        "status": CURRENT_STATUS,
        "start": CURRENT_START,
        "duration": CURRENT_DURATION,
        "practitioner": CURRENT_PRACTITIONER_ID,
        "proposal_count": 0,
        "confirm_count": 0,
        "raw_count": 0,
        "unexpected_mutation_count": 0,
        "unexpected_mutation_paths": [],
        "proposal_bodies": [],
        "routes": [],
        "exact_read_count": 0,
        "list_read_count": 0,
        "baseline_route_count": 0,
    }

    def appointment_kwargs():
        return {"status": state["status"], "start": state["start"],
                "duration": state["duration"], "practitioner_id": state["practitioner"]}

    def handle(route):
        request = route.request
        path = urlparse(request.url).path
        method = request.method
        state["routes"].append(f"{method} {path}")

        if method == "POST" and path.endswith(f"/appointments/proposals/status/{APPOINTMENT_ID}"):
            state["proposal_count"] += 1
            body = request.post_data_json or {}
            state["proposal_bodies"].append(body)
            requested_status = body.get("status", state["status"])
            warnings = []
            blocks = []
            if requested_status in ("Cancelled", "NoShow", "DNA"):
                warnings = [{"code": "terminal_status", "severity": "warning",
                             "message": "This is an authored-synthetic terminal-status warning."}]
            if mode == "blocked":
                blocks = [{"code": "authored_synthetic_current_truth_block", "severity": "blocked",
                           "message": "The authored-synthetic current appointment cannot accept this change."}]
            proposal = {
                "intent": "update_appointment_status",
                "safe": not blocks,
                "requires_confirmation": bool(warnings or blocks),
                "autonomy_tier": "blocked" if blocks else ("proposal" if warnings else "execute_with_report"),
                "summary": "Review the authored-synthetic status change.",
                "command": {"appointment_id": APPOINTMENT_ID, "status": requested_status,
                            "waiting_area_id": None, "waiting_area_id_supplied": True,
                            "clears_waiting_area": False},
                "warnings": warnings,
                "blocks": blocks,
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                **proposal,
                "confirm_endpoint": "/api/v1/appointments/proposals/status-confirm",
                "confirm_payload": {
                    "confirmed": False, "status_proposal": proposal, "confirmed_warnings": [],
                    "status_proposal_freshness_id": f"action-console-{mode}",
                    "signed_confirmation_evidence": {"schema_version": "bernie.confirmation_evidence.v1",
                                                     "purpose": "diary_confirm_status_proposal",
                                                     "payload": {"fixture": mode},
                                                     "signature": "signed"},
                    "signed_confirmation_evidence_required": True,
                },
            }))
            return

        if method == "POST" and path.endswith("/appointments/proposals/status-confirm"):
            state["confirm_count"] += 1
            confirm_body = request.post_data_json or {}
            command = (confirm_body.get("status_proposal") or {}).get("command") or {}
            requested_status = command.get("status", state["status"])
            if mode == "stale":
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_status_appointment", "safe": False, "requires_confirmation": True,
                    "autonomy_tier": "blocked", "summary": "The authored-synthetic proposal is stale.",
                    "appointment": None, "warnings": [],
                    "blocks": [{"code": "stale_status_proposal_freshness_id", "message": "Stale."}],
                    "audit_evidence": []}))
            else:
                state["status"] = requested_status
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_status_appointment", "safe": True, "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write", "summary": "Updated.",
                    "appointment": appointment(**appointment_kwargs()),
                    "warnings": [], "blocks": [], "audit_evidence": ["diary_confirm_status_proposal"]}))
            return

        if method == "POST" and path.endswith(f"/appointments/proposals/update/{APPOINTMENT_ID}"):
            state["proposal_count"] += 1
            body = request.post_data_json or {}
            state["proposal_bodies"].append(body)
            warnings = []
            blocks = []
            if mode in ("warning", "cancelled", "committed"):
                warnings = [{"code": "update_change_warning", "severity": "warning",
                             "message": "Review this authored-synthetic appointment change."}]
            if mode == "blocked":
                blocks = [{"code": "authored_synthetic_current_truth_block", "severity": "blocked",
                           "message": "Current authored-synthetic truth blocks this change."}]
            proposal = {
                "intent": "update_appointment",
                "safe": not blocks,
                "requires_confirmation": bool(warnings or blocks),
                "autonomy_tier": "blocked" if blocks else ("proposal" if warnings else "execute_with_report"),
                "summary": "Review the authored-synthetic appointment change.",
                "command": {"appointment_id": APPOINTMENT_ID,
                            "appointment_date": body.get("appointment_date", APPOINTMENT_DATE),
                            "start_time_local": body.get("start_time_local", state["start"]),
                            "duration_minutes": body.get("duration_minutes", state["duration"]),
                            "practitioner_id": body.get("practitioner_id", state["practitioner"]),
                            "patient_id": body.get("patient_id", PATIENT_ID)},
                "warnings": warnings,
                "blocks": blocks,
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                **proposal,
                "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                "confirm_payload": {
                    "confirmed": False, "update_proposal": proposal, "confirmed_warnings": [],
                    "update_proposal_freshness_id": f"action-console-{mode}",
                    "signed_confirmation_evidence": {"schema_version": "bernie.confirmation_evidence.v1",
                                                     "purpose": "diary_confirm_update_proposal",
                                                     "payload": {"fixture": mode},
                                                     "signature": "authored-synthetic-signature"},
                    "signed_confirmation_evidence_required": True,
                },
            }))
            return

        if method == "POST" and path.endswith("/appointments/proposals/update/confirm"):
            state["confirm_count"] += 1
            confirm_body = request.post_data_json or {}
            command = (confirm_body.get("update_proposal") or {}).get("command") or {}
            if mode == "stale":
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_update_appointment", "safe": False, "requires_confirmation": True,
                    "autonomy_tier": "blocked", "summary": "The authored-synthetic update proposal is stale.",
                    "appointment": None, "warnings": [],
                    "blocks": [{"code": "stale_update_proposal_freshness_id", "message": "Stale."}],
                    "audit_evidence": []}))
            else:
                state["start"] = command.get("start_time_local", state["start"])
                state["duration"] = command.get("duration_minutes", state["duration"])
                state["practitioner"] = command.get("practitioner_id", state["practitioner"])
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_update_appointment", "safe": True, "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write", "summary": "Updated authored-synthetic truth.",
                    "appointment": appointment(**appointment_kwargs()),
                    "warnings": [], "blocks": [], "audit_evidence": ["diary_confirm_update_proposal"]}))
            return

        if method in ("PUT", "PATCH") and "/appointments/" in path:
            state["raw_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if method == "GET" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["exact_read_count"] += 1
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(appointment(**appointment_kwargs())))
            return
        if method == "GET" and path.endswith("/appointments"):
            state["list_read_count"] += 1
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps([appointment(**appointment_kwargs())]))
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
            state["unexpected_mutation_paths"].append(f"{method} {path}")
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
    return sum(page.locator(FIELD_PANELS[field]).count() for field in FIELDS)

def open_action(page, field: str, via: str = "click") -> None:
    """Activate a palette choice and wait for its existing field editor."""
    choice = page.locator(CHOICE[field])
    choice.scroll_into_view_if_needed()
    if via == "click":
        choice.click()
    elif via == "Enter":
        choice.focus()
        page.keyboard.press("Enter")
    else:
        choice.focus()
        page.keyboard.press("Space")
    page.wait_for_selector(FIELD_PANELS[field], state="visible", timeout=WAIT_TIMEOUT)

def toggle_action(page, field: str, via: str = "click") -> None:
    """Activate the open choice again to collapse its editor."""
    choice = page.locator(CHOICE[field])
    choice.scroll_into_view_if_needed()
    if via == "click":
        choice.click()
    elif via == "Enter":
        choice.focus()
        page.keyboard.press("Enter")
    else:
        choice.focus()
        page.keyboard.press("Space")
    page.wait_for_selector(FIELD_PANELS[field], state="detached", timeout=WAIT_TIMEOUT)

def set_field(page, field: str, value: str) -> None:
    if field == "time":
        page.fill(FIELD_CONTROL[field], value)
    else:
        page.select_option(FIELD_CONTROL[field], value)

def assert_field_value(page, field: str, expected: str) -> None:
    assert page.locator(FIELD_CONTROL[field]).input_value() == expected

def assert_zero_routes(state: dict) -> None:
    assert state["proposal_count"] == 0
    assert state["confirm_count"] == 0
    assert state["raw_count"] == 0
    assert state["unexpected_mutation_count"] == 0

def assert_route_log_unchanged(state: dict) -> None:
    assert len(state["routes"]) == state["baseline_route_count"]

# ─── Behavioural contract (evidence label: route_intercepted_browser) ────────

def test_palette_starts_collapsed_native_and_route_inert(reception_page) -> None:
    """After appointment selection the palette is native, collapsed and inert."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        choices = page.locator(f"{PALETTE} button[data-testid^='meta-grid-action-choice-']")
        assert choices.count() == 4
        for field in FIELDS:
            choice = page.locator(CHOICE[field])
            assert choice.evaluate("el => el.tagName") == "BUTTON"
            assert choice.get_attribute("role") is None
            tabindex = choice.get_attribute("tabindex")
            assert tabindex is None or tabindex in ("0", "-1")
            assert choice.get_attribute("aria-controls") == "meta-grid-selected-action-editor"
            assert choice.get_attribute("aria-expanded") == "false"
        # The first (status) choice is focused after appointment selection.
        page.wait_for_function(
            "() => document.activeElement?.dataset?.testid === 'meta-grid-action-choice-status'",
            timeout=WAIT_TIMEOUT)
        # No field panel is mounted until a choice is activated.
        assert count_mounted_editors(page) == 0
        # Patient-minimized current-truth summary: status, time, duration and
        # practitioner, but never the patient name.
        summary = page.locator(SUMMARY).text_content()
        assert CURRENT_STATUS in summary
        assert "9:00" in summary
        assert "30" in summary
        assert "Alex" in summary
        assert "Margaret" not in summary
        assert "Thompson" not in summary
        # Palette startup produces zero routes after the fixture-startup reads.
        assert_zero_routes(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)

def test_open_collapse_switch_keeps_zero_or_one_editor_and_zero_routes(reception_page) -> None:
    """Open, collapse and switch through all four actions: one editor max."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        assert count_mounted_editors(page) == 0

        # Visible Enter activation opens status.
        open_action(page, "status", via="Enter")
        assert count_mounted_editors(page) == 1
        # Visible Space activation collapses the open action.
        toggle_action(page, "status", via="Space")
        assert count_mounted_editors(page) == 0
        # Visible click activation opens time.
        open_action(page, "time", via="click")
        assert count_mounted_editors(page) == 1
        # Direct switch time -> duration (click).
        open_action(page, "duration", via="click")
        assert count_mounted_editors(page) == 1
        # Direct switch duration -> practitioner (Enter).
        open_action(page, "practitioner", via="Enter")
        assert count_mounted_editors(page) == 1
        # Direct switch practitioner -> status (Space).
        open_action(page, "status", via="Space")
        assert count_mounted_editors(page) == 1
        # Collapse the open status (click).
        toggle_action(page, "status", via="click")
        assert count_mounted_editors(page) == 0

        # The intercepted route log remains empty for every palette transition.
        assert_zero_routes(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize("field", FIELDS)
def test_idle_collapse_discards_each_field_draft(reception_page, field) -> None:
    """Collapsing any action discards its complete provisional draft."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, field, via="click")
        set_field(page, field, FIELD_REQUESTED[field])
        assert not page.locator(SUBMIT[field]).is_disabled()  # a real draft exists
        toggle_action(page, field, via="Enter")
        # The announcer says no new Diary change occurred.
        assert "no new diary change" in page.locator("#meta-grid-announcer").text_content().lower()
        # Reopen: current/default truth is restored and review stays disabled.
        open_action(page, field, via="click")
        assert_field_value(page, field, FIELD_CURRENT[field])
        assert page.locator(SUBMIT[field]).is_disabled()
        assert_zero_routes(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)


def test_same_update_family_switch_retains_shared_draft_but_status_discards_it(
    reception_page,
) -> None:
    """Update-family views share one draft; status remains a hard boundary."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, "time")
        set_field(page, "time", REQUESTED_START)
        open_action(page, "duration")
        set_field(page, "duration", str(REQUESTED_DURATION))
        open_action(page, "practitioner")
        set_field(page, "practitioner", TARGET_PRACTITIONER_ID)

        for field, expected in (
            ("time", REQUESTED_START),
            ("duration", str(REQUESTED_DURATION)),
            ("practitioner", TARGET_PRACTITIONER_ID),
        ):
            open_action(page, field)
            assert_field_value(page, field, expected)
        assert "not current diary truth" in page.locator(
            "[data-testid='meta-grid-update-draft-summary']"
        ).text_content().lower()
        assert "shared appointment draft retained" in page.locator(
            "#meta-grid-announcer"
        ).text_content().lower()
        assert_zero_routes(state)
        assert_route_log_unchanged(state)

        open_action(page, "status")
        open_action(page, "time")
        assert_field_value(page, "time", CURRENT_START)
        open_action(page, "duration")
        assert_field_value(page, "duration", str(CURRENT_DURATION))
        open_action(page, "practitioner")
        assert_field_value(page, "practitioner", "")
        assert_zero_routes(state)
        assert_route_log_unchanged(state)
    finally:
        page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize("field", FIELDS)
def test_each_busy_action_locks_all_four_choices_and_preserves_dialog(reception_page, field) -> None:
    """While the existing confirmation dialog owns focus every palette choice is locked."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="warning")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, field, via="click")
        set_field(page, field, FIELD_WARNING_REQUESTED[field])
        page.locator(SUBMIT[field]).click()
        page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
        dialog = page.locator(DIALOG)
        for other in FIELDS:
            assert page.locator(CHOICE[other]).is_disabled()
        # Only the active panel remains mounted behind the dialog.
        assert count_mounted_editors(page) == 1
        # Tab remains contained by the existing dialog.
        for _ in range(4):
            page.keyboard.press("Tab")
            assert dialog.locator("button:focus").count() == 1
        # Escape cancels and returns focus to the active field's unchanged control.
        page.keyboard.press("Escape")
        page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_function(
            "tid => document.activeElement?.dataset?.testid === tid",
            arg=CONTROL_ID[field], timeout=WAIT_TIMEOUT)
        assert page.evaluate(
            "tid => document.activeElement?.dataset?.testid === tid",
            CONTROL_ID[field])
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert state["status"] == CURRENT_STATUS
        assert state["start"] == CURRENT_START
        assert state["duration"] == CURRENT_DURATION
        assert state["practitioner"] == CURRENT_PRACTITIONER_ID
    finally:
        page.unroute("**/api/v1/**", handler)

def test_interruption_clears_draft_and_requires_fresh_refresh(reception_page) -> None:
    """Window blur before any proposal disables the palette and forces a fresh read."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, "status", via="click")
        set_field(page, "status", TERMINAL_STATUS)
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        # No palette choice remains actionable.
        for field in FIELDS:
            assert page.locator(CHOICE[field]).is_disabled()
        # Only the accepted refresh path is offered.
        refresh = page.locator("[data-testid='meta-grid-refresh-current']")
        assert refresh.is_visible()
        # No proposal/confirm route occurred before interruption.
        assert state["proposal_count"] == 0
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        # After a fresh list read the console is collapsed and the draft is gone.
        initial_list = state["list_read_count"]
        refresh.click()
        # The accepted refresh path re-enables the collapsed palette choices.
        page.wait_for_function(
            "() => { const c = document.querySelector(\"[data-testid='meta-grid-action-choice-status']\"); "
            "return Boolean(c) && !c.disabled; }",
            timeout=WAIT_TIMEOUT)
        assert state["list_read_count"] > initial_list
        assert count_mounted_editors(page) == 0
        for field in FIELDS:
            assert page.locator(CHOICE[field]).get_attribute("aria-expanded") == "false"
        open_action(page, "status", via="click")
        assert_field_value(page, "status", CURRENT_STATUS)
        assert page.locator(SUBMIT["status"]).is_disabled()
    finally:
        page.unroute("**/api/v1/**", handler)

FIELD_FRESH_FRAGMENT = {"status": REQUESTED_STATUS, "time": "9:15",
                        "duration": str(REQUESTED_DURATION), "practitioner": "Patel"}

@pytest.mark.parametrize("action", FIELDS)
def test_field_request_traces_and_fresh_rebind_or_removal(reception_page, action) -> None:
    """Each field uses exactly its existing proposal/confirm family, then rebinds."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        open_selected_appointment(page, base_url, state)
        open_action(page, action, via="click")
        set_field(page, action, FIELD_REQUESTED[action])
        page.locator(SUBMIT[action]).click()
        if action != "status":
            page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
            assert state["confirm_count"] == 0
            page.locator(f"{DIALOG} button:has-text('Confirm & Save')").click()
            page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
        page.wait_for_function(
            "tid => document.querySelector(`[data-testid='${tid}']`)?.textContent.toLowerCase().includes('committed')",
            arg=FEEDBACK_ID[action], timeout=WAIT_TIMEOUT)
        # Exact proposal/confirm traces, zero raw or unexpected mutation.
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 1
        assert state["raw_count"] == 0
        assert state["unexpected_mutation_count"] == 0
        # The proposal body changes only its intended field.
        body = state["proposal_bodies"][0]
        if action == "status":
            assert body["status"] == REQUESTED_STATUS
            assert "start_time_local" not in body
            assert "duration_minutes" not in body
            assert "practitioner_id" not in body
        else:
            assert body["appointment_date"] == APPOINTMENT_DATE
            assert body["patient_id"] == PATIENT_ID
            if action == "time":
                assert body["start_time_local"] == REQUESTED_START
                assert body["duration_minutes"] == CURRENT_DURATION
                assert body["practitioner_id"] == CURRENT_PRACTITIONER_ID
            elif action == "duration":
                assert body["start_time_local"] == CURRENT_START
                assert body["duration_minutes"] == REQUESTED_DURATION
                assert body["practitioner_id"] == CURRENT_PRACTITIONER_ID
            else:  # practitioner
                assert body["start_time_local"] == CURRENT_START
                assert body["duration_minutes"] == CURRENT_DURATION
                assert body["practitioner_id"] == TARGET_PRACTITIONER_ID
        # Retained appointments keep the active action and a fresh summary.
        assert count_mounted_editors(page) == 1
        assert FIELD_FRESH_FRAGMENT[action] in page.locator(SUMMARY).text_content()
        assert state["confirm_count"] == 1
    finally:
        page.unroute("**/api/v1/**", handler)

    if action == "status":
        # One explicit removal outcome renders only its active terminal status.
        state, handler = install_routes(page, mode="warning")
        try:
            open_selected_appointment(page, base_url, state)
            open_action(page, "status", via="click")
            set_field(page, "status", TERMINAL_STATUS)
            page.locator(SUBMIT["status"]).click()
            page.wait_for_selector(DIALOG, state="visible", timeout=WAIT_TIMEOUT)
            page.locator(f"{DIALOG} button:has-text('Confirm & Save')").click()
            page.wait_for_selector(DIALOG, state="detached", timeout=WAIT_TIMEOUT)
            page.wait_for_selector(".meta-grid-status-outcome",
                                   state="visible", timeout=WAIT_TIMEOUT)
            assert count_mounted_editors(page) == 0
            assert page.locator(".meta-grid-status-outcome").count() == 1
            assert page.locator(".meta-grid-reschedule-outcome").count() == 0
            assert page.locator(".meta-grid-duration-outcome").count() == 0
            assert page.locator(".meta-grid-practitioner-outcome").count() == 0
            assert state["proposal_count"] == 1
            assert state["confirm_count"] == 1
            assert state["raw_count"] == 0
        finally:
            page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize(("width", "height"), [(1280, 720), (768, 1024), (390, 844)],
                         ids=["desktop", "tablet", "phone"])
def test_palette_editor_accessibility_and_containment(reception_page, width, height) -> None:
    """Palette targets, overflow, editor labelling and one polite live region."""
    page, base_url = reception_page
    state, handler = install_routes(page, mode="safe")
    try:
        page.set_viewport_size({"width": width, "height": height})
        open_selected_appointment(page, base_url, state)
        # Every palette target is at least 44-by-44 CSS pixels.
        for field in FIELDS:
            box = page.locator(CHOICE[field]).bounding_box()
            assert box is not None
            assert box["width"] >= 44
            assert box["height"] >= 44
        # Open the editor and verify wrapping without horizontal overflow.
        open_action(page, "status", via="click")
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
        # The shared editor is labelled.
        editor = page.locator(EDITOR)
        assert editor.get_attribute("aria-labelledby") or editor.get_attribute("aria-label")
        # Exactly one polite atomic status region exists inside the active editor.
        live = editor.locator("[role='status'][aria-live='polite'][aria-atomic='true']")
        assert live.count() == 1
        assert_zero_routes(state)
    finally:
        page.unroute("**/api/v1/**", handler)
        page.set_viewport_size({"width": 1280, "height": 720})

# ─── Static source guard (evidence label: authored_synthetic_client_fixture) ──

def test_selected_action_console_source_guards_reject_compound_and_raw_writes() -> None:
    """Static guard: single action enum, no compound executor, no raw writes.
    Evidence label: ``authored_synthetic_client_fixture``."""
    meta = (DOCS / "diary/meta-grid.js").read_text(encoding="utf-8")
    diary = (DOCS / "diary/diary.js").read_text(encoding="utf-8")

    # 1. The selected-action console and its four choices exist.
    assert "activeSelectedAction" in meta
    assert "meta-grid-selected-action-console" in meta
    assert "meta-grid-selected-action-palette" in meta
    assert "meta-grid-selected-action-summary" in meta
    assert "meta-grid-selected-action-editor" in meta
    assert "meta-grid-action-choice-${action}" in meta
    for action in FIELDS:
        assert f'["{action}",' in meta

    # 2. No generic action executor map or compound draft is constructed.
    for marker in ("executorMap", "actionExecutors", "compoundDraft", "compound_update",
                   "multiFieldDraft", "executeMany", "runActions", "sequentialRun"):
        assert marker not in meta

    # 3. Palette activation issues no API request (no fetch/route/proposal/confirm)
    #    inside the exact activation slice only (activateSelectedAction up to
    #    statusActionMessage); existing reads elsewhere in meta-grid.js are exempt.
    activation_slice = meta[meta.index("function activateSelectedAction"):
                            meta.index("function statusActionMessage")]
    for marker in ("apiFetch(", "fetch(", "/appointments/proposals/", "confirm_endpoint",
                   "Idempotency-Key"):
        assert marker not in activation_slice

    # 4. No raw compatibility PUT/PATCH fallback appears in the client.
    assert 'method: "PUT"' not in meta
    assert 'method: "PATCH"' not in meta

    # 5. The existing Diary bridge owns only the status and update proposal/confirm
    #    families, with no second write path.
    assert "/appointments/proposals/status/" in diary
    assert "/appointments/proposals/status-confirm" in diary
    assert "/appointments/proposals/update/" in diary
    assert "/appointments/proposals/update/confirm" in diary
    assert "handleMoveResize" in diary

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("This module is a pytest contract; do not run it directly.")
