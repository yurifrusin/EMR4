"""Route-intercepted browser proof of two-projection Diary truth parity."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.parse import urlparse

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402
from scripts.raisa_provider_free_two_projection_truth_parity_conformance_rehearsal import (  # noqa: E402
    RENDERERS,
    SCENARIOS,
    build_trace,
    compare_paired_traces,
    expected_kernel_trace,
)

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    pytest.skip("playwright is required", allow_module_level=True)


DOCS = ROOT / "docs"
APPOINTMENT_ID = "truth-parity-status-1"
PRACTICE_SCOPE = "authored-synthetic-practice"
AUTH_TOKEN = "e30.eyJyb2xlIjoic3RhZmYiLCJleHAiOjQxMDI0NDQ4MDB9.sig"


def appointment(status: str = "Booked") -> dict:
    return {
        "id": APPOINTMENT_ID,
        "appointment_date": "2026-08-13",
        "start_time_local": "09:00",
        "duration_minutes": 30,
        "status": status,
        "waiting_area_id": None,
        "patient_id": "truth-parity-patient-1",
        "patient": {
            "id": "truth-parity-patient-1",
            "first_name": "Avery",
            "last_name": "Example",
            "date_of_birth": "1980-01-01",
        },
        "practitioner_id": "truth-parity-practitioner-1",
        "practitioner": {
            "id": "truth-parity-practitioner-1",
            "first_name": "Alex",
            "last_name": "Example",
            "ahpra_number": "MED0001234567",
        },
        "location_id": "loc-1",
        "reason": "Authored synthetic truth-parity review",
    }


def install_routes(page, *, scenario: str) -> tuple[dict, object]:
    expected = expected_kernel_trace(scenario)
    requested = expected["selected_current_coordinate"]["requested_status"]
    state = {
        "status": "Booked",
        "proposal_count": 0,
        "confirm_count": 0,
        "raw_count": 0,
        "unexpected_mutation_count": 0,
        "unexpected_mutation_paths": [],
    }

    def handle(route):
        request = route.request
        path = urlparse(request.url).path

        if request.method == "POST" and path.endswith(f"/appointments/proposals/status/{APPOINTMENT_ID}"):
            state["proposal_count"] += 1
            assert request.post_data_json["status"] == requested
            if scenario == "failed":
                route.fulfill(status=503, content_type="application/json", body=json.dumps({
                    "detail": "Authored-synthetic proposal transport unavailable."
                }))
                return
            warnings = []
            blocks = []
            if scenario in {"cancelled", "committed"}:
                warnings = [{
                    "code": "terminal_status",
                    "severity": "warning",
                    "message": "Review this authored-synthetic terminal status.",
                }]
            if scenario == "blocked":
                blocks = [{
                    "code": "authored_synthetic_current_truth_block",
                    "severity": "blocked",
                    "message": "Current authored-synthetic truth blocks this change.",
                }]
            proposal = {
                "intent": "update_appointment_status",
                "safe": not blocks,
                "requires_confirmation": bool(warnings or blocks),
                "autonomy_tier": "blocked" if blocks else ("proposal" if warnings else "execute_with_report"),
                "summary": "Review the authored-synthetic status change.",
                "command": {
                    "appointment_id": APPOINTMENT_ID,
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
                    "status_proposal_freshness_id": f"truth-parity-{scenario}",
                    "signed_confirmation_evidence": {
                        "schema_version": "bernie.confirmation_evidence.v1",
                        "purpose": "diary_confirm_status_proposal",
                        "payload": {"fixture": scenario},
                        "signature": "authored-synthetic-signature",
                    },
                    "signed_confirmation_evidence_required": True,
                },
            }))
            return

        if request.method == "POST" and path.endswith("/appointments/proposals/status-confirm"):
            state["confirm_count"] += 1
            assert request.post_data_json["status_proposal"]["command"]["status"] == requested
            if scenario == "stale":
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
                    "summary": "Updated authored-synthetic truth.",
                    "appointment": appointment(requested),
                    "warnings": [],
                    "blocks": [],
                    "audit_evidence": ["diary_confirm_status_proposal"],
                }))
            return

        if request.method == "PATCH" and path.endswith(f"/appointments/{APPOINTMENT_ID}/status"):
            state["raw_count"] += 1
            route.fulfill(status=500, content_type="application/json", body="{}")
            return

        if request.method == "GET" and path.endswith(f"/appointments/{APPOINTMENT_ID}"):
            route.fulfill(status=200, content_type="application/json", body=json.dumps(appointment(state["status"])))
            return
        if request.method == "GET" and path.endswith("/appointments"):
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
                    "assignment": "Dr Alex Example",
                    "practitioner_id": "truth-parity-practitioner-1",
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
            # GraphQL is the existing read-only projection surface. HTTP POST
            # transport does not make this a command mutation.
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
    page.fill("#meta-grid-request", "Show Avery Example's upcoming appointments")
    page.press("#meta-grid-request", "Enter")
    selector = f"#meta-grid-content [data-appointment-id='{APPOINTMENT_ID}']"
    page.wait_for_selector(selector, state="visible")
    page.click(selector)
    page.wait_for_selector("[data-testid='meta-grid-status-action']", state="visible")


def exercise(page, *, renderer: str, scenario: str) -> dict:
    expected = expected_kernel_trace(scenario)
    requested = expected["selected_current_coordinate"]["requested_status"]
    if renderer == "conventional_grid":
        select = page.locator(
            f"[data-testid='appointment-status-select'][data-appointment-id='{APPOINTMENT_ID}']"
        )
        select.select_option(requested)
    else:
        open_reception_one(page)
        select = page.locator("[data-testid='meta-grid-status-select']")
        select.select_option(requested)
        page.click("[data-testid='meta-grid-status-submit']")

    if scenario in {"cancelled", "blocked", "committed"}:
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

    if renderer == "conventional_grid":
        phase = "failed" if scenario == "stale" else expected["kernel_result"].removeprefix("no_commit_")
        page.wait_for_function(
            "([id, phase]) => document.querySelector(`[data-testid=appointment-status-select][data-appointment-id='${id}']`)?.dataset.statusTransactionState === phase",
            arg=[APPOINTMENT_ID, phase],
        )
        terminal_status = page.locator(
            f"[data-testid='appointment-status-select'][data-appointment-id='{APPOINTMENT_ID}']"
        ).input_value()
        renderer_local = {
            "layout": "inline_grid_status_selector",
            "wording": page.locator("#diary-status").text_content().strip(),
            "focus_target": "appointment_status_select",
            "history_behavior": "ordinary_grid_rebuild_without_projection_trail",
        }
    else:
        message_fragment = {
            "safe": "committed",
            "cancelled": "cancelled",
            "blocked": "blocked",
            "stale": "not changed",
            "failed": "not changed",
            "committed": "committed",
        }[scenario]
        page.wait_for_function(
            "fragment => document.querySelector('[data-testid=meta-grid-status-feedback]')?.textContent.toLowerCase().includes(fragment)",
            arg=message_fragment,
        )
        terminal_status = page.locator("[data-testid='meta-grid-status-select']").input_value()
        renderer_local = {
            "layout": "selected_card_status_action_panel",
            "wording": page.locator("[data-testid='meta-grid-status-feedback']").text_content().strip(),
            "focus_target": "meta_grid_status_select",
            "history_behavior": "projection_trail_cleared_only_after_commit",
        }

    return {
        "terminal_status": terminal_status,
        "renderer_local": renderer_local,
    }


def run_matrix() -> dict:
    traces: list[dict] = []
    with harness.serve_dir(DOCS) as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for renderer in RENDERERS:
                for scenario in SCENARIOS:
                    page = browser.new_page(viewport={"width": 1280, "height": 720})
                    harness.stub_office(page)
                    state, handler = install_routes(page, scenario=scenario)
                    try:
                        open_diary(page, base_url)
                        rendered = exercise(page, renderer=renderer, scenario=scenario)
                        expected = expected_kernel_trace(scenario)
                        assert state["status"] == expected["fresh_read_result"]["current_status"]
                        assert rendered["terminal_status"] == expected["displayed_terminal_state"]["status"]
                        assert state["unexpected_mutation_count"] == 0, state["unexpected_mutation_paths"]
                        observed = {
                            **expected,
                            "fresh_read_result": {
                                **expected["fresh_read_result"],
                                "current_status": state["status"],
                            },
                            "displayed_terminal_state": {"status": rendered["terminal_status"]},
                            "route_counts": {
                                "proposal": state["proposal_count"],
                                "confirm": state["confirm_count"],
                                "raw_compatibility": state["raw_count"],
                            },
                        }
                        traces.append(build_trace(
                            renderer=renderer,
                            scenario=scenario,
                            observed=observed,
                            renderer_local=rendered["renderer_local"],
                        ))
                    finally:
                        page.unroute("**/api/v1/**", handler)
                        page.close()
        finally:
            browser.close()
    return {
        "schema_version": "raisa.two-projection-truth-parity-evidence.v1",
        "result": "raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_pass",
        "evidence_mode": "route_intercepted_browser",
        "traces": traces,
        "comparisons": compare_paired_traces(traces),
        "authority_counts": {
            "provider_calls": 0,
            "patient_or_product_records": 0,
            "database_or_source_reads": 0,
            "database_writes": 0,
            "deployments": 0,
            "releases": 0,
            "protected_ref_movements": 0,
        },
    }


def test_two_projection_truth_parity_matrix() -> None:
    evidence = run_matrix()
    assert len(evidence["traces"]) == 12
    assert len(evidence["comparisons"]) == 6
    assert all(item["kernel_fields_equal"] for item in evidence["comparisons"])
    assert sum(item["raw_compatibility_requests"] for item in evidence["comparisons"]) == 0


if __name__ == "__main__":
    print(json.dumps(run_matrix(), indent=2, ensure_ascii=False))
