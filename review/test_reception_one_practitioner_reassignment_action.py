"""Provider-free route-intercepted browser contract for Reception One
practitioner-only reassignment (same date/start/duration).

Specifies: a selected-card ``New practitioner`` selector and ``Review
practitioner change`` action; options only from active practice-scoped
directory rows excluding the current practitioner (same, blank, malformed,
inactive, unlisted and duplicate targets make zero proposal/confirm); exact
fresh appointment/directory rechecks before delegation (failure or target
disappearance fails closed); a bridge with literal zero start/duration deltas
delegating once to ``handleMoveResize`` (no bridge-local route/proposal/
confirm/signing/idempotency/raw-PUT); only the existing update proposal/confirm
routes; six paired outcomes; identical fresh normalized truth per pair, exact
route counts, zero raw PUT and zero unexpected mutations; separate
interruption/fresh-read, mutual exclusion, dialog focus/Escape,
time/duration/status regression, 200-row boundary and no-overflow cases.

Evidence labels: ``route_intercepted_browser`` and
``authored_synthetic_client_fixture``; never live product operation.
Assertions are intentionally red against the pre-implementation source.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import json
import re
import threading
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    pytest.skip("playwright is required (pip install playwright && playwright install chromium)",
                allow_module_level=True)

APPOINTMENT_ID = "practitioner-reassignment-1"
PATIENT_ID = "patient-reassignment-1"
CURRENT_PRACTITIONER_ID = "practitioner-reassignment-current"
TARGET_PRACTITIONER_ID = "practitioner-reassignment-target"
INACTIVE_PRACTITIONER_ID = "practitioner-reassignment-inactive"
CURRENT_DISPLAY_NAME = "Dr Alex Example"
TARGET_DISPLAY_NAME = "Dr Anika Patel"
CURRENT_AHPRA = "MED0000000001"
TARGET_AHPRA = "MED0000000002"
APPOINTMENT_DATE = "2026-08-13"
CURRENT_START = "09:00"
DURATION_MINUTES = 30
CURRENT_END = "09:30"
AUTH_TOKEN = "e30.eyJyb2xlIjoic3RhZmYiLCJleHAiOjQxMDI0NDQ4MDB9.sig"

RENDERERS = ("conventional_grid", "reception_one")
SCENARIOS = ("safe", "cancelled", "blocked", "stale", "failed", "committed")
GRID_COLUMN_PRACTITIONER = {"0": CURRENT_PRACTITIONER_ID, "1": TARGET_PRACTITIONER_ID}

EXPECTED = {
    "safe":      {"practitioner": TARGET_PRACTITIONER_ID,   "proposal": 1, "confirm": 1, "dialog": False, "feedback": "committed"},
    "cancelled": {"practitioner": CURRENT_PRACTITIONER_ID,  "proposal": 1, "confirm": 0, "dialog": True,  "feedback": "cancelled"},
    "blocked":   {"practitioner": CURRENT_PRACTITIONER_ID,  "proposal": 1, "confirm": 0, "dialog": True,  "feedback": "blocked"},
    "stale":     {"practitioner": CURRENT_PRACTITIONER_ID,  "proposal": 1, "confirm": 1, "dialog": False, "feedback": "not changed"},
    "failed":    {"practitioner": CURRENT_PRACTITIONER_ID,  "proposal": 1, "confirm": 0, "dialog": False, "feedback": "not changed"},
    "committed": {"practitioner": TARGET_PRACTITIONER_ID,   "proposal": 1, "confirm": 1, "dialog": True,  "feedback": "committed"},
}

def appointment(practitioner_id: str = CURRENT_PRACTITIONER_ID) -> dict:
    is_target = practitioner_id == TARGET_PRACTITIONER_ID
    first = "Anika" if is_target else "Alex"
    last = "Patel" if is_target else "Example"
    return {
        "id": APPOINTMENT_ID,
        "appointment_date": APPOINTMENT_DATE,
        "start_time_local": CURRENT_START,
        "end_time_local": CURRENT_END,
        "duration_minutes": DURATION_MINUTES,
        "status": "Booked",
        "waiting_area_id": None,
        "patient_id": PATIENT_ID,
        "patient": {"id": PATIENT_ID, "first_name": "Margaret", "last_name": "Thompson", "date_of_birth": "1952-03-14"},
        "practitioner_id": practitioner_id,
        "practitioner": {"id": practitioner_id, "first_name": first, "last_name": last,
                         "ahpra_number": TARGET_AHPRA if is_target else CURRENT_AHPRA},
        "location_id": "loc-1",
        "appointment_type_id": "reassignment-type-1",
        "reason": "Authored synthetic practitioner reassignment review",
    }

def directory_row(practitioner_id: str, display_name: str, active: bool = True) -> dict:
    return {"id": practitioner_id, "displayName": display_name, "roleLabel": "Doctor",
            "active": active, "defaultLocation": {"id": "loc-1", "name": "Main Clinic"}}

def default_directory() -> list:
    return [
        directory_row(CURRENT_PRACTITIONER_ID, CURRENT_DISPLAY_NAME),
        directory_row(TARGET_PRACTITIONER_ID, TARGET_DISPLAY_NAME),
        directory_row(INACTIVE_PRACTITIONER_ID, "Dr Inactive Lee", active=False),
    ]

_DUPLICATE_DIRECTORY = [directory_row(CURRENT_PRACTITIONER_ID, CURRENT_DISPLAY_NAME),
                        directory_row(TARGET_PRACTITIONER_ID, TARGET_DISPLAY_NAME),
                        directory_row(TARGET_PRACTITIONER_ID, TARGET_DISPLAY_NAME)]

def template() -> dict:
    return {
        "practice_name": "Authored Synthetic Practice",
        "slot_defaults": {"start": "09:00", "end": "17:00", "interval_minutes": 15},
        "columns": [
            {"room_label": "Room 1", "assignment": CURRENT_DISPLAY_NAME,
             "practitioner_id": CURRENT_PRACTITIONER_ID, "practitioner_ahpra": CURRENT_AHPRA},
            {"room_label": "Room 2", "assignment": TARGET_DISPLAY_NAME,
             "practitioner_id": TARGET_PRACTITIONER_ID, "practitioner_ahpra": TARGET_AHPRA},
        ],
    }

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # pragma: no cover
        pass

@contextlib.contextmanager
def serve_dir(root: Path):
    handler = functools.partial(_QuietHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()

def stub_office(page) -> None:
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

def install_routes(page, *, scenario: str, directory: list | None = None) -> tuple[dict, object]:
    """Route-intercepted surface: only the update proposal/confirm family mutates."""
    rows = directory if directory is not None else default_directory()
    state = {
        "practitioner": CURRENT_PRACTITIONER_ID, "proposal_count": 0, "confirm_count": 0,
        "raw_count": 0, "unexpected_mutation_count": 0, "unexpected_mutation_paths": [],
        "proposal_bodies": [], "exact_read_count": 0, "list_read_count": 0,
        "directory_read_count": 0, "fail_fresh_directory": False, "drop_target_in_fresh": False,
    }
    def fresh_rows():
        return [r for r in rows if not (state["drop_target_in_fresh"] and r["id"] == TARGET_PRACTITIONER_ID)]
    def serve_directory(route, wrapped=False):
        state["directory_read_count"] += 1
        if state["fail_fresh_directory"]:
            route.fulfill(status=503, content_type="application/json",
                          body=json.dumps({"detail": "Authored-synthetic active-practitioner directory unavailable."}))
        else:
            payload = fresh_rows() if not wrapped else {"data": {"practice": {"practitioners": fresh_rows()}}}
            route.fulfill(status=200, content_type="application/json", body=json.dumps(payload))
    def handle(route):
        request = route.request
        path = urlparse(request.url).path
        if request.method == "POST" and path.endswith(f"/appointments/proposals/update/{APPOINTMENT_ID}"):
            state["proposal_count"] += 1
            body = request.post_data_json or {}
            state["proposal_bodies"].append(body)
            if scenario == "failed":
                route.fulfill(status=503, content_type="application/json",
                              body=json.dumps({"detail": "Authored-synthetic update proposal transport unavailable."}))
                return
            warnings = []
            blocks = []
            if scenario in ("cancelled", "committed"):
                warnings = [{"code": "practitioner_change_warning", "severity": "warning",
                             "message": "Review this authored-synthetic same-day practitioner reassignment."}]
            if scenario == "blocked":
                blocks = [{"code": "authored_synthetic_current_truth_block", "severity": "blocked",
                           "message": "Current authored-synthetic truth blocks this practitioner reassignment."}]
            proposal = {
                "intent": "update_appointment", "safe": not blocks,
                "requires_confirmation": bool(warnings or blocks),
                "autonomy_tier": "blocked" if blocks else ("proposal" if warnings else "execute_with_report"),
                "summary": "Review the authored-synthetic same-day practitioner reassignment.",
                "command": {"appointment_id": APPOINTMENT_ID,
                            "appointment_date": body.get("appointment_date", APPOINTMENT_DATE),
                            "start_time_local": body.get("start_time_local", CURRENT_START),
                            "duration_minutes": body.get("duration_minutes", DURATION_MINUTES),
                            "practitioner_id": body.get("practitioner_id", TARGET_PRACTITIONER_ID),
                            "patient_id": body.get("patient_id", PATIENT_ID)},
                "warnings": warnings, "blocks": blocks,
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                **proposal,
                "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                "confirm_payload": {"confirmed": False, "update_proposal": proposal, "confirmed_warnings": [],
                                    "update_proposal_freshness_id": f"practitioner-reassignment-{scenario}",
                                    "signed_confirmation_evidence": {"signature": "authored-synthetic-signature"},
                                    "signed_confirmation_evidence_required": True},
            }))
            return
        if request.method == "POST" and path.endswith("/appointments/proposals/update/confirm"):
            state["confirm_count"] += 1
            if scenario == "stale":
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_update_appointment", "safe": False, "requires_confirmation": True,
                    "autonomy_tier": "blocked", "summary": "The authored-synthetic update proposal is stale.",
                    "appointment": None, "warnings": [],
                    "blocks": [{"code": "stale_update_proposal_freshness_id", "message": "Stale."}],
                    "audit_evidence": []}))
            else:
                state["practitioner"] = TARGET_PRACTITIONER_ID
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_update_appointment", "safe": True, "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write", "summary": "Updated authored-synthetic truth.",
                    "appointment": appointment(practitioner_id=state["practitioner"]),
                    "warnings": [], "blocks": [], "audit_evidence": ["diary_confirm_update_proposal"]}))
            return
        if request.method == "PUT" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["raw_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return
        if request.method == "GET" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["exact_read_count"] += 1
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(appointment(practitioner_id=state["practitioner"])))
            return
        if request.method == "GET" and path.endswith("/appointments"):
            state["list_read_count"] += 1
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps([appointment(practitioner_id=state["practitioner"])]))
            return
        if request.method == "GET" and path.endswith("/patients/search"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([appointment()["patient"]]))
            return
        if path.endswith("/auth/me"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"role": "staff"}))
            return
        if path.endswith("/diary/template"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(template()))
            return
        if path.endswith("/diary/locations"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps([{"id": "loc-1", "name": "Authored Synthetic Practice", "is_active": True}]))
            return
        if path.endswith("/appointments/types") or path.endswith("/diary/waiting-areas"):
            route.fulfill(status=200, content_type="application/json", body="[]")
            return
        if path.endswith("/diary/roster"):
            route.fulfill(status=200, content_type="application/json", body='{"entries":[]}')
            return
        if path.endswith("/practitioners"):
            serve_directory(route)
            return
        if path.endswith("/appointments/bernie/pilot-eligibility"):
            route.fulfill(status=200, content_type="application/json", body='{"enabled":true,"eligible":true}')
            return
        if path.endswith("/diary/events/committed"):
            route.fulfill(status=200, content_type="application/json", body='{"enabled":false,"events":[],"cursor":null}')
            return
        if request.method == "POST" and path.endswith("/graphql"):
            serve_directory(route, wrapped=True)  # read-only projection + directory query
            return
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            state["unexpected_mutation_count"] += 1
            state["unexpected_mutation_paths"].append(f"{request.method} {path}")
        route.fulfill(status=200, content_type="application/json", body="{}")
    page.route("**/api/v1/**", handle)
    return state, handle

def open_diary(page, base_url: str) -> None:
    page.add_init_script(f"localStorage.setItem('emr4_token', {json.dumps(AUTH_TOKEN)});")
    page.goto(base_url + "/diary/diary.html?reference_date=2026-08-13")
    page.wait_for_selector(
        f"[data-testid='appointment-status-select'][data-appointment-id='{APPOINTMENT_ID}']",
        state="attached", timeout=15000)
    page.click(f".appt[data-id='{APPOINTMENT_ID}']")
    page.wait_for_selector(
        f"[data-testid='appointment-status-select'][data-appointment-id='{APPOINTMENT_ID}']", state="visible")

def open_reception_one(page) -> None:
    page.click("#btn-meta-grid-launch")
    page.fill("#meta-grid-request", "Show Margaret Thompson's upcoming appointments")
    page.press("#meta-grid-request", "Enter")
    page.wait_for_selector(f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']", state="visible").click()
    page.wait_for_selector("[data-testid='meta-grid-practitioner-action']", state="visible")

def _grid_drag_to_target(page) -> None:
    box = page.locator(f".appt[data-id='{APPOINTMENT_ID}']").bounding_box()
    assert box is not None
    source_y = box["y"] + min(14, max(6, box["height"] * 0.25))
    target = page.locator(".diary-column-body[data-col-idx='1']").bounding_box()
    assert target is not None
    page.mouse.move(box["x"] + box["width"] * 0.5, source_y)
    page.mouse.down()
    page.mouse.move(target["x"] + target["width"] * 0.5, source_y, steps=8)
    page.mouse.up()

def _trigger_practitioner_action(page, *, renderer: str, scenario: str) -> None:
    if renderer == "conventional_grid":
        _grid_drag_to_target(page)
    else:
        page.select_option("[data-testid='meta-grid-practitioner-select']", TARGET_PRACTITIONER_ID)
        page.click("[data-testid='meta-grid-practitioner-submit']")
    if EXPECTED[scenario]["dialog"]:
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        dialog = page.locator("[data-testid='status-proposal-dialog']")
        if scenario == "cancelled":
            dialog.locator("button:has-text('Cancel')").click()
        elif scenario == "blocked":
            assert dialog.locator("button:has-text('Confirm & Save')").count() == 0
            dialog.locator("button:has-text('Close')").click()
        else:
            dialog.locator("button:has-text('Confirm & Save')").click()
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")

def _grid_displayed_practitioner(page) -> str:
    col_idx = page.evaluate(
        "id => document.querySelector(`.appt[data-id='${id}']`)?.closest('.diary-column-body')?.dataset.colIdx || ''",
        APPOINTMENT_ID)
    return GRID_COLUMN_PRACTITIONER.get(str(col_idx), "")

def _reception_displayed_practitioner(page) -> str:
    text = page.locator(f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']").text_content() or ""
    if TARGET_DISPLAY_NAME in text:
        return TARGET_PRACTITIONER_ID
    if CURRENT_DISPLAY_NAME in text:
        return CURRENT_PRACTITIONER_ID
    return ""

def exercise(page, *, renderer: str, scenario: str) -> str:
    expected = EXPECTED[scenario]
    _trigger_practitioner_action(page, renderer=renderer, scenario=scenario)
    if renderer == "conventional_grid":
        if expected["practitioner"] == TARGET_PRACTITIONER_ID:
            page.wait_for_function(
                "([id, colIdx]) => document.querySelector(`.appt[data-id='${id}']`)?.closest('.diary-column-body')?.dataset.colIdx === colIdx",
                arg=[APPOINTMENT_ID, "1"], timeout=10000)
        else:
            page.wait_for_timeout(500)
        return _grid_displayed_practitioner(page)
    page.wait_for_function(
        "fragment => document.querySelector('[data-testid=meta-grid-practitioner-feedback]')?.textContent.toLowerCase().includes(fragment)",
        arg=expected["feedback"], timeout=10000)
    if expected["practitioner"] == TARGET_PRACTITIONER_ID:
        page.wait_for_function(
            "([id, name]) => document.querySelector(`#meta-grid-content [data-appointment-id='${id}']`)?.textContent.includes(name)",
            arg=[APPOINTMENT_ID, TARGET_DISPLAY_NAME], timeout=10000)
    return _reception_displayed_practitioner(page)

def _normalized_fresh_truth(state: dict) -> dict:
    return {"appointment_id": APPOINTMENT_ID, "appointment_date": APPOINTMENT_DATE,
            "start_time_local": CURRENT_START, "end_time_local": CURRENT_END,
            "practitioner_id": state["practitioner"], "duration_minutes": DURATION_MINUTES,
            "patient_id": PATIENT_ID, "status": "Booked"}

def run_matrix() -> list:
    traces = []
    with serve_dir(DOCS) as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for renderer in RENDERERS:
                for scenario in SCENARIOS:
                    page = browser.new_page(viewport={"width": 1280, "height": 720})
                    stub_office(page)
                    state, handler = install_routes(page, scenario=scenario)
                    try:
                        open_diary(page, base_url)
                        if renderer == "reception_one":
                            open_reception_one(page)
                        rendered = exercise(page, renderer=renderer, scenario=scenario)
                        expected = EXPECTED[scenario]
                        assert (state["practitioner"], state["proposal_count"], state["confirm_count"],
                                state["raw_count"], state["unexpected_mutation_count"], rendered) == (
                            expected["practitioner"], expected["proposal"], expected["confirm"], 0, 0,
                            expected["practitioner"])
                        if state["proposal_bodies"]:
                            body = state["proposal_bodies"][0]
                            assert (body["appointment_date"], body["start_time_local"],
                                    body["duration_minutes"], body["practitioner_id"], body["patient_id"]) == (
                                APPOINTMENT_DATE, CURRENT_START, DURATION_MINUTES, TARGET_PRACTITIONER_ID, PATIENT_ID)
                        traces.append((renderer, scenario, _normalized_fresh_truth(state),
                                       state["proposal_count"], state["confirm_count"],
                                       state["raw_count"], state["unexpected_mutation_count"], rendered))
                    finally:
                        page.unroute("**/api/v1/**", handler)
                        page.close()
        finally:
            browser.close()
    return traces

def test_practitioner_reassignment_paired_matrix() -> None:
    """Six paired conventional_grid/reception_one outcomes share identical truth."""
    traces = run_matrix()
    assert len(traces) == 12
    by_key = {}
    for renderer, scenario, normalized, prop, conf, raw, unexpected, displayed in traces:
        by_key.setdefault(scenario, {})[renderer] = (normalized, prop, conf, raw, unexpected, displayed)
    for scenario in SCENARIOS:
        left = by_key[scenario]["conventional_grid"]
        right = by_key[scenario]["reception_one"]
        assert left[0] == right[0], scenario       # identical normalized fresh truth
        assert left[1:] == right[1:], scenario     # exact route counts + displayed terminal
        assert left[3] == 0 and left[4] == 0, scenario  # zero raw PUT + zero unexpected mutations

def test_closed_practitioner_selector_limits_options_and_makes_zero_routes(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="safe")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        assert page.locator("[data-testid='meta-grid-practitioner-action']").is_visible()
        select = page.locator("[data-testid='meta-grid-practitioner-select']")
        assert select.evaluate("element => element.tagName") == "SELECT"
        assert page.locator("[data-testid='meta-grid-practitioner-submit']").text_content().strip() == "Review practitioner change"
        assert page.locator("[data-testid='meta-grid-practitioner-feedback']").is_visible()
        options = select.locator("option").evaluate_all("opts => opts.map(opt => opt.value)")
        assert options.count(TARGET_PRACTITIONER_ID) == 1 and "" in options  # no duplicates; blank default
        assert CURRENT_PRACTITIONER_ID not in options and INACTIVE_PRACTITIONER_ID not in options
        assert select.input_value() == ""
        assert page.locator("[data-testid='meta-grid-practitioner-submit']").is_disabled()
        page.wait_for_timeout(250)
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"],
                state["unexpected_mutation_count"]) == (0, 0, 0, 0)
    finally:
        page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize(("target", "directory"), [
    (CURRENT_PRACTITIONER_ID, None), ("", None), ("malformed-target", None),
    (INACTIVE_PRACTITIONER_ID, None), ("practitioner-unlisted", None),
    (TARGET_PRACTITIONER_ID, _DUPLICATE_DIRECTORY),
], ids=["same", "blank", "malformed", "inactive", "unlisted", "duplicate"])
def test_invalid_targets_make_zero_routes(reception_page, target: str, directory) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="safe", directory=directory)
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        page.evaluate(
            "([selectTestId, value]) => { const s = document.querySelector(`[data-testid='${selectTestId}']`); s.value = value; s.dispatchEvent(new Event('change', { bubbles: true })); }",
            ["meta-grid-practitioner-select", target])
        submit = page.locator("[data-testid='meta-grid-practitioner-submit']")
        if not submit.is_disabled():  # a disabled submit is already a fail-closed UI stop
            submit.click()
        page.wait_for_timeout(400)
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"],
                state["unexpected_mutation_count"]) == (0, 0, 0, 0), state
    finally:
        page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize("failure_kind", ["directory", "disappearance"], ids=["directory", "disappearance"])
def test_fresh_recheck_fails_closed(reception_page, failure_kind: str) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="safe")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        state["fail_fresh_directory"] = failure_kind == "directory"
        state["drop_target_in_fresh"] = failure_kind == "disappearance"
        page.select_option("[data-testid='meta-grid-practitioner-select']", TARGET_PRACTITIONER_ID)
        page.click("[data-testid='meta-grid-practitioner-submit']")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-practitioner-feedback]')?.textContent.toLowerCase().includes('not changed')")
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"],
                state["unexpected_mutation_count"]) == (0, 0, 0, 0), state
        assert _reception_displayed_practitioner(page) == CURRENT_PRACTITIONER_ID
    finally:
        page.unroute("**/api/v1/**", handler)

def test_interruption_keeps_one_action_and_requires_fresh_reconciliation(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="cancelled")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        before = state["list_read_count"]
        page.select_option("[data-testid='meta-grid-practitioner-select']", TARGET_PRACTITIONER_ID)
        page.click("[data-testid='meta-grid-practitioner-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        assert page.locator("#bernie-meta-grid").get_attribute("class").find("is-private") >= 0
        assert page.locator("[data-testid='status-proposal-dialog']").count() == 1
        assert (state["proposal_count"], state["confirm_count"]) == (1, 0)
        page.locator("[data-testid='status-proposal-dialog'] button:has-text('Cancel')").press("Escape")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-practitioner-feedback]')?.textContent.toLowerCase().includes('cancelled')")
        page.wait_for_timeout(150)
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"]) == (1, 0, 0)
        assert state["list_read_count"] > before
        assert _reception_displayed_practitioner(page) == CURRENT_PRACTITIONER_ID
        page.wait_for_function("document.activeElement?.dataset?.testid === 'meta-grid-practitioner-select'")
    finally:
        page.unroute("**/api/v1/**", handler)

def test_dialog_focus_containment_and_escape_return_to_practitioner_selector(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="cancelled")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        page.select_option("[data-testid='meta-grid-practitioner-select']", TARGET_PRACTITIONER_ID)
        page.click("[data-testid='meta-grid-practitioner-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        dialog = page.locator("[data-testid='status-proposal-dialog']")
        for _ in range(4):
            page.keyboard.press("Tab")
            assert dialog.locator("button:focus").count() == 1
        page.keyboard.press("Escape")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        assert page.locator("#bernie-meta-grid").is_visible()
        page.wait_for_function("document.activeElement?.dataset?.testid === 'meta-grid-practitioner-select'")
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"]) == (1, 0, 0)
    finally:
        page.unroute("**/api/v1/**", handler)

def test_status_time_duration_and_practitioner_actions_share_mutual_exclusion(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="cancelled")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        controls = [page.locator(f"[data-testid='{tid}']") for tid in
                    ("meta-grid-practitioner-select", "meta-grid-status-select",
                     "meta-grid-reschedule-time", "meta-grid-duration-select")]
        page.select_option("[data-testid='meta-grid-practitioner-select']", TARGET_PRACTITIONER_ID)
        page.click("[data-testid='meta-grid-practitioner-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        assert all(c.is_disabled() for c in controls)
        assert (state["proposal_count"], state["confirm_count"]) == (1, 0)
        page.locator("[data-testid='status-proposal-dialog'] button:has-text('Cancel')").click()
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-practitioner-feedback]')?.textContent.toLowerCase().includes('cancelled')")
        assert all(not c.is_disabled() for c in controls)
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"]) == (1, 0, 0)
    finally:
        page.unroute("**/api/v1/**", handler)

def test_time_duration_and_status_actions_remain_registered_with_practitioner_panel(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="safe")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        for testid in ("meta-grid-practitioner-action", "meta-grid-reschedule-action",
                       "meta-grid-duration-action", "meta-grid-status-action"):
            assert page.locator(f"[data-testid='{testid}']").is_visible()
        page.fill("[data-testid='meta-grid-reschedule-time']", "09:15")
        page.click("[data-testid='meta-grid-reschedule-submit']")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-reschedule-feedback]')?.textContent.toLowerCase().includes('committed')")
        assert (state["proposal_count"], state["confirm_count"], state["raw_count"]) == (1, 1, 0)
        assert state["unexpected_mutation_count"] == 0
        assert state["practitioner"] == CURRENT_PRACTITIONER_ID
    finally:
        page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize("row_count", [200, 201], ids=["at_200", "over_200"])
def test_directory_200_row_boundary(reception_page, row_count: int) -> None:
    page, base_url = reception_page
    rows = [directory_row(CURRENT_PRACTITIONER_ID, CURRENT_DISPLAY_NAME),
            directory_row(TARGET_PRACTITIONER_ID, TARGET_DISPLAY_NAME)] + \
        [directory_row(f"practitioner-extra-{i}", f"Dr Extra {i}") for i in range(row_count - 2)]
    state, handler = install_routes(page, scenario="safe", directory=rows)
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        options = page.locator("[data-testid='meta-grid-practitioner-select'] option").evaluate_all(
            "opts => opts.map(opt => opt.value)")
        page.evaluate(
            "([tid, value]) => { const s = document.querySelector(`[data-testid='${tid}']`); s.value = value; s.dispatchEvent(new Event('change', { bubbles: true })); }",
            ["meta-grid-practitioner-select", TARGET_PRACTITIONER_ID])
        submit = page.locator("[data-testid='meta-grid-practitioner-submit']")
        if not submit.is_disabled():
            submit.click()
        page.wait_for_timeout(400)
        if row_count <= 200:
            assert TARGET_PRACTITIONER_ID in options
            assert (state["proposal_count"], state["confirm_count"]) == (1, 1)
        else:
            assert (state["proposal_count"], state["confirm_count"]) == (0, 0)  # cap fails closed
        assert (state["raw_count"], state["unexpected_mutation_count"]) == (0, 0)
    finally:
        page.unroute("**/api/v1/**", handler)

@pytest.mark.parametrize(("width", "height"), [(1280, 720), (768, 1024), (390, 844)],
                         ids=["desktop", "tablet", "phone"])
def test_practitioner_action_is_usable_without_horizontal_overflow(reception_page, width: int, height: int) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="responsive")
    try:
        page.set_viewport_size({"width": width, "height": height})
        open_diary(page, base_url)
        open_reception_one(page)
        layout = page.locator("[data-testid='meta-grid-practitioner-action']").evaluate("""panel => {
          const host = document.getElementById('bernie-meta-grid');
          const panelRect = panel.getBoundingClientRect();
          const hostRect = host.getBoundingClientRect();
          return { overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                   withinHost: panelRect.left >= hostRect.left && panelRect.right <= hostRect.right + 1 };
        }""")
        assert layout == {"overflow": False, "withinHost": True}
        for testid in ("meta-grid-practitioner-select", "meta-grid-practitioner-submit",
                       "meta-grid-practitioner-feedback"):
            assert page.locator(f"[data-testid='{testid}']").is_visible()
        assert (state["proposal_count"], state["confirm_count"]) == (0, 0)
    finally:
        page.unroute("**/api/v1/**", handler)
        page.set_viewport_size({"width": 1280, "height": 720})

def test_reception_one_practitioner_action_source_has_no_second_write_path() -> None:
    """Static source guard (evidence label: ``authored_synthetic_client_fixture``)."""
    meta = (DOCS / "diary/meta-grid.js").read_text(encoding="utf-8")
    diary = (DOCS / "diary/diary.js").read_text(encoding="utf-8")
    for testid in ("meta-grid-practitioner-action", "meta-grid-practitioner-select",
                   "meta-grid-practitioner-submit", "meta-grid-practitioner-feedback"):
        assert testid in meta, f"missing Reception One practitioner-action testid: {testid}"
    assert "Review practitioner change" in meta
    for marker in ("apiFetch(", "fetch(", "/appointments/proposals/", "confirm_endpoint",
                   "Idempotency-Key", 'method: "PUT"'):
        assert marker not in meta, f"Reception One projection owns a forbidden marker: {marker}"
    assert "handleMoveResize" in diary
    assert "/appointments/proposals/update/" in diary
    assert "/appointments/proposals/update/confirm" in diary
    assert re.search(r"handleMoveResize\(\s*appointment,\s*0,\s*0,", diary), \
        "practitioner bridge does not fix both deltas at literal zero"
    assert "reassignAppointmentPractitioner" in diary
    assert "Confirm Appointment Practitioner Change" in diary

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("This module is a pytest contract; do not run it directly.")
