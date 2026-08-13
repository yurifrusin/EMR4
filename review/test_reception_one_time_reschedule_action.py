"""Provider-free route-intercepted browser contract for Reception One time reschedule.

This is a bounded, authored-synthetic test-engineering artifact. It specifies,
for the same-date, same-practitioner, duration-fixed selected-appointment
start-time action:

- a selected-card 15-minute-step time input and a ``Review time change`` action;
- a Reception One bridge that computes a start delta, fixes the duration delta
  at zero and delegates to the ordinary native Diary's existing
  ``handleMoveResize`` interaction (it owns no fetch, route, proposal, confirm,
  signing, idempotency or raw-PUT implementation);
- the existing update-proposal route and the proposal-supplied allowlisted
  confirm route only;
- six paired ``conventional_grid`` / ``reception_one`` outcomes: safe commit,
  warning cancel, blocked, stale confirmation, transport failure and explicit
  warning commit;
- identical fresh normalized appointment identity/coordinates for each pair,
  exact proposal/confirm counts, zero raw PUT and zero unexpected mutation
  routes;
- separate invalid/no-op zero-route, interruption/fresh-reconciliation,
  keyboard/focus/Escape and desktop/tablet/phone no-overflow cases.

Evidence labels:
- Browser cases driven through ``page.route`` interception are labelled
  ``route_intercepted_browser``; they never claim live product operation.
- Static source/fixture checks are labelled ``authored_synthetic_client_fixture``.

The behavioural assertions are intentionally red against the pre-implementation
source. Sol owns product HTML/CSS/JavaScript integration and execution after
this contract is accepted. pytest is not run in the worker worktree.
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
except ImportError:  # pragma: no cover - dependency not installed
    pytest.skip("playwright is required (pip install playwright && playwright install chromium)",
                allow_module_level=True)


APPOINTMENT_ID = "time-reschedule-1"
PATIENT_ID = "patient-time-1"
PRACTITIONER_ID = "practitioner-time-1"
AHPRA = "MED0001234567"
CURRENT_START = "09:00"
REQUESTED_START = "09:15"
DURATION_MINUTES = 30
CURRENT_END = "09:30"
REQUESTED_END = "09:45"
APPOINTMENT_DATE = "2026-08-13"
AUTH_TOKEN = "e30.eyJyb2xlIjoic3RhZmYiLCJleHAiOjQxMDI0NDQ4MDB9.sig"

RENDERERS = ("conventional_grid", "reception_one")
SCENARIOS = ("safe", "cancelled", "blocked", "stale", "failed", "committed")

# Expected kernel truth for each route-intercepted outcome.
# ``start`` is the authoritative fresh-read start after the terminal outcome;
# ``proposal``/``confirm`` are the exact route counts; ``dialog`` records whether
# the shared staff review dialog must be presented (warnings or blocks);
# ``feedback`` is the Reception One live-outcome fragment (a plain-language
# contract for Sol's product implementation).
EXPECTED = {
    "safe":      {"start": REQUESTED_START, "proposal": 1, "confirm": 1, "dialog": False, "feedback": "committed"},
    "cancelled": {"start": CURRENT_START,   "proposal": 1, "confirm": 0, "dialog": True,  "feedback": "cancelled"},
    "blocked":   {"start": CURRENT_START,   "proposal": 1, "confirm": 0, "dialog": True,  "feedback": "blocked"},
    "stale":     {"start": CURRENT_START,   "proposal": 1, "confirm": 1, "dialog": False, "feedback": "not changed"},
    "failed":    {"start": CURRENT_START,   "proposal": 1, "confirm": 0, "dialog": False, "feedback": "not changed"},
    "committed": {"start": REQUESTED_START, "proposal": 1, "confirm": 1, "dialog": True,  "feedback": "committed"},
}


def appointment(start: str = CURRENT_START, status: str = "Booked") -> dict:
    """Authored-synthetic current appointment used by every intercepted read."""
    return {
        "id": APPOINTMENT_ID,
        "appointment_date": APPOINTMENT_DATE,
        "start_time_local": start,
        "end_time_local": _add_minutes(start, DURATION_MINUTES),
        "duration_minutes": DURATION_MINUTES,
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
            "last_name": "Example",
            "ahpra_number": AHPRA,
        },
        "location_id": "loc-1",
        "appointment_type_id": "time-type-1",
        "reason": "Authored synthetic time reschedule review",
    }


def _add_minutes(hhmm: str, minutes: int) -> str:
    hours, mins = map(int, hhmm.split(":"))
    total = (hours * 60 + mins + minutes) % 1440
    return f"{total // 60:02d}:{total % 60:02d}"


def _normalize_parsed_time(raw: str) -> str:
    match = re.search(r"(\d{1,2}):(\d{2})", raw)
    assert match, f"could not parse an HH:MM start time from: {raw!r}"
    return f"{int(match.group(1)):02d}:{match.group(2)}"


# ─── Self-contained browser/static helpers (no mutable test-module import) ───

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


def install_routes(page, *, scenario: str) -> tuple[dict, object]:
    """Route-intercepted API surface for the time-reschedule composition.

    Only the existing update proposal/confirm family mutates; every other
    non-read is counted as an unexpected mutation and returns 200 empty.
    """
    state = {
        "start": CURRENT_START,
        "proposal_count": 0,
        "confirm_count": 0,
        "raw_count": 0,
        "unexpected_mutation_count": 0,
        "unexpected_mutation_paths": [],
        "proposal_bodies": [],
        "exact_read_count": 0,
        "list_read_count": 0,
    }

    def handle(route):
        request = route.request
        path = urlparse(request.url).path

        if request.method == "POST" and path.endswith(f"/appointments/proposals/update/{APPOINTMENT_ID}"):
            state["proposal_count"] += 1
            body = request.post_data_json or {}
            state["proposal_bodies"].append(body)
            if scenario == "failed":
                route.fulfill(status=503, content_type="application/json", body=json.dumps({
                    "detail": "Authored-synthetic update proposal transport unavailable."
                }))
                return
            warnings = []
            blocks = []
            if scenario in ("cancelled", "committed"):
                warnings = [{
                    "code": "time_change_warning",
                    "severity": "warning",
                    "message": "Review this authored-synthetic same-day time change.",
                }]
            if scenario == "blocked":
                blocks = [{
                    "code": "authored_synthetic_current_truth_block",
                    "severity": "blocked",
                    "message": "Current authored-synthetic truth blocks this time change.",
                }]
            proposal = {
                "intent": "update_appointment",
                "safe": not blocks,
                "requires_confirmation": bool(warnings or blocks),
                "autonomy_tier": "blocked" if blocks else ("proposal" if warnings else "execute_with_report"),
                "summary": "Review the authored-synthetic same-day time change.",
                "command": {
                    "appointment_id": APPOINTMENT_ID,
                    "appointment_date": body.get("appointment_date", APPOINTMENT_DATE),
                    "start_time_local": body.get("start_time_local", REQUESTED_START),
                    "duration_minutes": body.get("duration_minutes", DURATION_MINUTES),
                    "practitioner_id": body.get("practitioner_id", PRACTITIONER_ID),
                    "patient_id": body.get("patient_id", PATIENT_ID),
                },
                "warnings": warnings,
                "blocks": blocks,
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                **proposal,
                "confirm_endpoint": "/api/v1/appointments/proposals/update/confirm",
                "confirm_payload": {
                    "confirmed": False,
                    "update_proposal": proposal,
                    "confirmed_warnings": [],
                    "update_proposal_freshness_id": f"time-reschedule-{scenario}",
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "diary_confirm_update_proposal",
                        "payload": {"fixture": scenario},
                        "signature": "authored-synthetic-signature",
                    },
                    "signed_confirmation_evidence_required": True,
                },
            }))
            return

        if request.method == "POST" and path.endswith("/appointments/proposals/update/confirm"):
            state["confirm_count"] += 1
            if scenario == "stale":
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_update_appointment",
                    "safe": False,
                    "requires_confirmation": True,
                    "autonomy_tier": "blocked",
                    "summary": "The authored-synthetic update proposal is stale.",
                    "appointment": None,
                    "warnings": [],
                    "blocks": [{"code": "stale_update_proposal_freshness_id", "message": "Stale."}],
                    "audit_evidence": [],
                }))
            else:
                state["start"] = REQUESTED_START
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "intent": "confirm_update_appointment",
                    "safe": True,
                    "requires_confirmation": False,
                    "autonomy_tier": "confirmed_write",
                    "summary": "Updated authored-synthetic truth.",
                    "appointment": appointment(start=REQUESTED_START),
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["diary_confirm_update_proposal"],
                }))
            return

        if request.method == "PUT" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["raw_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if request.method == "GET" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            state["exact_read_count"] += 1
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointment(start=state["start"])))
            return
        if request.method == "GET" and path.endswith("/appointments"):
            state["list_read_count"] += 1
            route.fulfill(status=200, content_type="application/json", body=json.dumps([appointment(start=state["start"])]))
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
                    "assignment": "Dr Alex Example",
                    "practitioner_id": PRACTITIONER_ID,
                    "practitioner_ahpra": AHPRA,
                }],
            }))
            return
        if path.endswith("/diary/locations"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "loc-1", "name": "Authored Synthetic Practice", "is_active": True}
            ]))
            return
        if path.endswith("/appointments/types") or path.endswith("/diary/waiting-areas"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
            return
        if path.endswith("/diary/roster"):
            route.fulfill(status=200, content_type="application/json", body='{"entries":[]}')
            return
        if path.endswith("/practitioners"):
            route.fulfill(status=200, content_type="application/json", body="[]")
            return
        if path.endswith("/appointments/bernie/pilot-eligibility"):
            route.fulfill(status=200, content_type="application/json", body='{"enabled":true,"eligible":true}')
            return
        if path.endswith("/diary/events/committed"):
            route.fulfill(status=200, content_type="application/json", body='{"enabled":false,"events":[],"cursor":null}')
            return
        if request.method == "POST" and path.endswith("/graphql"):
            # Existing read-only projection surface; HTTP POST transport is not a mutation.
            route.fulfill(status=200, content_type="application/json", body='{"data":{}}')
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
        state="attached",
        timeout=15000,
    )
    page.click(f".appt[data-id='{APPOINTMENT_ID}']")
    page.wait_for_selector(
        f"[data-testid='appointment-status-select'][data-appointment-id='{APPOINTMENT_ID}']",
        state="visible",
    )


def open_reception_one(page) -> None:
    page.click("#btn-meta-grid-launch")
    page.fill("#meta-grid-request", "Show Margaret Thompson's upcoming appointments")
    page.press("#meta-grid-request", "Enter")
    selector = f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)
    page.wait_for_selector("[data-testid='meta-grid-reschedule-action']", state="visible")


def _trigger_time_action(page, *, renderer: str, scenario: str) -> None:
    if renderer == "conventional_grid":
        page.locator(f".appt[data-id='{APPOINTMENT_ID}']").focus()
        page.keyboard.press("Alt+ArrowDown")
    else:
        page.fill("[data-testid='meta-grid-reschedule-time']", REQUESTED_START)
        page.click("[data-testid='meta-grid-reschedule-submit']")
    if EXPECTED[scenario]["dialog"]:
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        dialog = page.locator("[data-testid='status-proposal-dialog']")
        if scenario == "cancelled":
            dialog.locator("button:has-text('Cancel')").click()
        elif scenario == "blocked":
            assert dialog.locator("button:has-text('Confirm & Save')").count() == 0
            dialog.locator("button:has-text('Close')").click()
        else:  # committed -> explicit staff confirmation
            dialog.locator("button:has-text('Confirm & Save')").click()
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")


def _grid_displayed_start(page) -> str:
    title = page.locator(f".appt[data-id='{APPOINTMENT_ID}']").get_attribute("title") or ""
    return _normalize_parsed_time(title)


def _reception_displayed_start(page) -> str:
    text = page.locator(f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}'] h3").text_content() or ""
    return _normalize_parsed_time(text)


def exercise(page, *, renderer: str, scenario: str) -> dict:
    expected = EXPECTED[scenario]
    _trigger_time_action(page, renderer=renderer, scenario=scenario)

    if renderer == "conventional_grid":
        if scenario == "safe":
            page.wait_for_function(
                r"""([id, expectedStart]) => {
                  const el = document.querySelector(`.appt[data-id='${id}']`);
                  if (!el) return false;
                  const title = el.getAttribute('title') || '';
                  const match = title.match(/(\d{1,2}):(\d{2})/);
                  return Boolean(match) && String(match[1]).padStart(2, '0') + ':' + match[2] === expectedStart;
                }""",
                arg=[APPOINTMENT_ID, expected["start"]],
                timeout=10000,
            )
        else:
            page.wait_for_timeout(500)
        displayed_start = _grid_displayed_start(page)
        renderer_local = {
            "layout": "inline_grid_keyboard_alt_arrow",
            "focus_target": "appointment_block",
            "history_behavior": "ordinary_grid_rebuild_without_projection_trail",
        }
    else:
        page.wait_for_function(
            "fragment => document.querySelector('[data-testid=meta-grid-reschedule-feedback]')?.textContent.toLowerCase().includes(fragment)",
            arg=expected["feedback"],
            timeout=10000,
        )
        if expected["start"] == REQUESTED_START:
            page.wait_for_function(
                r"""([id, expectedStart]) => {
                  const heading = document.querySelector(
                    `#meta-grid-content [data-appointment-id='${id}'] h3`
                  );
                  if (!heading) return false;
                  const match = heading.textContent.match(/(\d{1,2}):(\d{2})/);
                  return Boolean(match)
                    && String(match[1]).padStart(2, '0') + ':' + match[2] === expectedStart;
                }""",
                arg=[APPOINTMENT_ID, expected["start"]],
                timeout=10000,
            )
        displayed_start = _reception_displayed_start(page)
        renderer_local = {
            "layout": "selected_card_time_action_panel",
            "focus_target": "meta_grid_time_input",
            "history_behavior": "projection_trail_cleared_only_after_commit",
        }

    return {"displayed_start": displayed_start, "renderer_local": renderer_local}


def _normalized_fresh_truth(state: dict) -> dict:
    start = state["start"]
    return {
        "appointment_id": APPOINTMENT_ID,
        "appointment_date": APPOINTMENT_DATE,
        "start_time_local": start,
        "end_time_local": _add_minutes(start, DURATION_MINUTES),
        "practitioner_id": PRACTITIONER_ID,
        "duration_minutes": DURATION_MINUTES,
        "patient_id": PATIENT_ID,
        "status": "Booked",
    }


def run_matrix() -> dict:
    traces: list[dict] = []
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

                        assert state["start"] == expected["start"], (renderer, scenario, state["start"])
                        assert state["proposal_count"] == expected["proposal"], (renderer, scenario, state)
                        assert state["confirm_count"] == expected["confirm"], (renderer, scenario, state)
                        assert state["raw_count"] == 0, (renderer, scenario, state)
                        assert state["unexpected_mutation_count"] == 0, (renderer, scenario, state["unexpected_mutation_paths"])
                        assert rendered["displayed_start"] == expected["start"], (renderer, scenario, rendered)

                        if state["proposal_bodies"]:
                            body = state["proposal_bodies"][0]
                            assert body["appointment_date"] == APPOINTMENT_DATE
                            assert body["start_time_local"] == REQUESTED_START
                            assert body["duration_minutes"] == DURATION_MINUTES
                            assert body["practitioner_id"] == PRACTITIONER_ID
                            assert body["patient_id"] == PATIENT_ID

                        traces.append({
                            "renderer": renderer,
                            "scenario": scenario,
                            "normalized": _normalized_fresh_truth(state),
                            "route_counts": {
                                "proposal": state["proposal_count"],
                                "confirm": state["confirm_count"],
                                "raw_compatibility": state["raw_count"],
                                "unexpected_mutation": state["unexpected_mutation_count"],
                            },
                            "displayed_terminal_state": {"start_time_local": rendered["displayed_start"]},
                            "renderer_local": rendered["renderer_local"],
                        })
                    finally:
                        page.unroute("**/api/v1/**", handler)
                        page.close()
        finally:
            browser.close()

    pairs = {}
    for trace in traces:
        pairs.setdefault(trace["scenario"], []).append(trace)
    comparisons = []
    for scenario in SCENARIOS:
        left = next(t for t in pairs[scenario] if t["renderer"] == "conventional_grid")
        right = next(t for t in pairs[scenario] if t["renderer"] == "reception_one")
        comparisons.append({
            "scenario": scenario,
            "normalized_equal": left["normalized"] == right["normalized"],
            "route_counts_equal": left["route_counts"] == right["route_counts"],
            "displayed_terminal_equal": left["displayed_terminal_state"] == right["displayed_terminal_state"],
            "raw_compatibility_requests": left["route_counts"]["raw_compatibility"] + right["route_counts"]["raw_compatibility"],
            "unexpected_mutations": left["route_counts"]["unexpected_mutation"] + right["route_counts"]["unexpected_mutation"],
        })
    return {
        "schema_version": "raisa.reception-one-time-reschedule-evidence.v1",
        "evidence_mode": "route_intercepted_browser",
        "traces": traces,
        "comparisons": comparisons,
    }


# ─── Behavioural contract: six paired outcomes ───────────────────────────────

def test_time_reschedule_paired_matrix() -> None:
    """Six paired conventional_grid/reception_one outcomes share identical truth."""
    evidence = run_matrix()
    assert len(evidence["traces"]) == 12
    assert len(evidence["comparisons"]) == 6
    assert all(item["normalized_equal"] for item in evidence["comparisons"])
    assert all(item["route_counts_equal"] for item in evidence["comparisons"])
    assert all(item["displayed_terminal_equal"] for item in evidence["comparisons"])
    assert sum(item["raw_compatibility_requests"] for item in evidence["comparisons"]) == 0
    assert sum(item["unexpected_mutations"] for item in evidence["comparisons"]) == 0
    for trace in evidence["traces"]:
        expected = EXPECTED[trace["scenario"]]
        assert trace["route_counts"]["proposal"] == expected["proposal"]
        assert trace["route_counts"]["confirm"] == expected["confirm"]


# ─── Separate cases: invalid/no-op, interruption, keyboard/focus, layout ─────

def test_invalid_and_no_op_time_input_makes_zero_routes(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="safe")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        time_input = page.locator("[data-testid='meta-grid-reschedule-time']")

        # Unchanged time is a local no-op.
        time_input.fill(CURRENT_START)
        assert page.locator("[data-testid='meta-grid-reschedule-submit']").is_disabled()
        page.wait_for_timeout(250)
        assert state["proposal_count"] == 0
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert state["unexpected_mutation_count"] == 0

        # Off-15-minute-grid time is rejected locally without a request.
        time_input.fill("09:07")
        page.click("[data-testid='meta-grid-reschedule-submit']")
        page.wait_for_timeout(250)
        assert state["proposal_count"] == 0
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert state["unexpected_mutation_count"] == 0
        # No optimistic commit: the field must not have advanced to the requested
        # 15-minute-aligned start.
        assert time_input.input_value() != REQUESTED_START
    finally:
        page.unroute("**/api/v1/**", handler)


def test_interruption_keeps_one_action_and_requires_fresh_reconciliation(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="cancelled")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        initial_list_reads = state["list_read_count"]
        page.fill("[data-testid='meta-grid-reschedule-time']", REQUESTED_START)
        page.click("[data-testid='meta-grid-reschedule-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        assert page.locator("#bernie-meta-grid").get_attribute("class").find("is-private") >= 0
        assert page.locator("[data-testid='status-proposal-dialog']").count() == 1
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        page.locator("[data-testid='status-proposal-dialog'] button:has-text('Cancel')").press("Escape")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        page.wait_for_function(
            "document.querySelector('[data-testid=meta-grid-reschedule-feedback]')?.textContent.toLowerCase().includes('cancelled')"
        )
        page.wait_for_timeout(150)
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
        assert state["list_read_count"] > initial_list_reads
        # The selected input remains provisional staff intent; the rendered
        # appointment coordinate must come from the fresh authoritative read.
        assert _reception_displayed_start(page) == CURRENT_START
        page.wait_for_function(
            "document.activeElement?.dataset?.testid === 'meta-grid-reschedule-time'"
        )
        assert page.locator("[data-testid='meta-grid-reschedule-time']").evaluate("el => document.activeElement === el")
    finally:
        page.unroute("**/api/v1/**", handler)


def test_keyboard_focus_containment_and_escape_return_to_time_input(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="cancelled")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        page.fill("[data-testid='meta-grid-reschedule-time']", REQUESTED_START)
        page.click("[data-testid='meta-grid-reschedule-submit']")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="visible")
        dialog = page.locator("[data-testid='status-proposal-dialog']")

        # Focus containment: repeated Tab never leaves the dialog's buttons.
        for _ in range(4):
            page.keyboard.press("Tab")
            assert dialog.locator("button:focus").count() == 1

        # Escape cancels and deterministically returns focus to the time input;
        # the Reception One workspace stays open behind the dialog.
        page.keyboard.press("Escape")
        page.wait_for_selector("[data-testid='status-proposal-dialog']", state="detached")
        assert page.locator("#bernie-meta-grid").is_visible()
        page.wait_for_function(
            "document.activeElement?.dataset?.testid === 'meta-grid-reschedule-time'"
        )
        assert page.locator("[data-testid='meta-grid-reschedule-time']").evaluate("el => document.activeElement === el")
        assert state["proposal_count"] == 1
        assert state["confirm_count"] == 0
        assert state["raw_count"] == 0
    finally:
        page.unroute("**/api/v1/**", handler)


@pytest.mark.parametrize(
    ("width", "height"),
    [(1280, 720), (768, 1024), (390, 844)],
    ids=["desktop", "tablet", "phone"],
)
def test_time_action_is_usable_without_horizontal_overflow(
    reception_page, width: int, height: int
) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="responsive")
    try:
        page.set_viewport_size({"width": width, "height": height})
        open_diary(page, base_url)
        open_reception_one(page)
        layout = page.locator("[data-testid='meta-grid-reschedule-action']").evaluate("""panel => {
          const host = document.getElementById('bernie-meta-grid');
          const panelRect = panel.getBoundingClientRect();
          const hostRect = host.getBoundingClientRect();
          return {
            overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            withinHost: panelRect.left >= hostRect.left && panelRect.right <= hostRect.right + 1
          };
        }""")
        assert layout == {"overflow": False, "withinHost": True}
        assert page.locator("[data-testid='meta-grid-reschedule-time']").is_visible()
        assert page.locator("[data-testid='meta-grid-reschedule-submit']").is_visible()
        assert page.locator("[data-testid='meta-grid-reschedule-feedback']").is_visible()
        assert state["proposal_count"] == 0
        assert state["confirm_count"] == 0
    finally:
        page.unroute("**/api/v1/**", handler)
        page.set_viewport_size({"width": 1280, "height": 720})


def test_selected_card_time_input_is_15_minute_step(reception_page) -> None:
    page, base_url = reception_page
    state, handler = install_routes(page, scenario="responsive")
    try:
        open_diary(page, base_url)
        open_reception_one(page)
        time_input = page.locator("[data-testid='meta-grid-reschedule-time']")
        assert time_input.get_attribute("type") == "time"
        assert time_input.get_attribute("step") == "900"
        submit = page.locator("[data-testid='meta-grid-reschedule-submit']")
        assert submit.text_content().strip() == "Review time change"
        assert page.locator("[data-testid='meta-grid-reschedule-action']").is_visible()
        assert state["proposal_count"] == 0
    finally:
        page.unroute("**/api/v1/**", handler)


# ─── Static source guard (authored_synthetic_client_fixture) ─────────────────

def test_reception_one_time_action_source_has_no_second_write_path() -> None:
    """The Reception One projection owns no network/write path of its own.

    Evidence label: ``authored_synthetic_client_fixture``. This reads the
    committed product source and asserts the frozen composition boundary.
    """
    meta = (DOCS / "diary/meta-grid.js").read_text(encoding="utf-8")
    diary = (DOCS / "diary/diary.js").read_text(encoding="utf-8")

    # 1. The selected-card time panel is present in Reception One.
    for testid in ("meta-grid-reschedule-action", "meta-grid-reschedule-time", "meta-grid-reschedule-submit", "meta-grid-reschedule-feedback"):
        assert testid in meta, f"missing Reception One time-action testid: {testid}"
    assert "Review time change" in meta

    # 2. Reception One owns no fetch/route/proposal/confirm/signing/idempotency
    #    or raw-PUT implementation. It delegates through the existing bridge.
    forbidden = (
        "apiFetch(",
        "fetch(",
        "/appointments/proposals/",
        "confirm_endpoint",
        "Idempotency-Key",
        'method: "PUT"',
    )
    for marker in forbidden:
        assert marker not in meta, f"Reception One projection owns a forbidden marker: {marker}"

    # 3. The delegation target is the ordinary Diary's existing move/resize
    #    interaction, and only the existing update proposal/confirm routes exist.
    assert "handleMoveResize" in diary
    assert "/appointments/proposals/update/" in diary
    assert "/appointments/proposals/update/confirm" in diary

    # 4. The bridge fixes the duration delta at zero (same-date, duration-fixed).
    assert re.search(
        r"handleMoveResize\(\s*appointment,\s*requestedStartMins\s*-\s*currentStartMins,\s*0,",
        diary,
    ), "duration delta is not fixed at zero"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("This module is a pytest contract; do not run it directly.")
