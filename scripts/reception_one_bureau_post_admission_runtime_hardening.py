#!/usr/bin/env python3
"""Provider-free browser proof for shared proposal provenance and clearing."""

from __future__ import annotations

import hashlib
import json
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

from playwright.sync_api import Browser, Route, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-post-admission-runtime-hardening"
)
EVIDENCE = OUTPUT / "browser-acceptance-evidence.json"
STANDARD_SCREENSHOT = OUTPUT / "standard-admitted.png"
ISOLATED_SCREENSHOT = OUTPUT / "isolated-admitted.png"
CLEARED_SCREENSHOT = OUTPUT / "planner-change-cleared.png"
REFERENCE_DATE = "2026-07-27"
REQUEST = (
    "Make an appointment for Margaret Thompson with Dr Alex Shera "
    "today morning"
)
COMPOSE_PATH = "/api/v1/appointments/proposals/reception-one/compose"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


@contextmanager
def static_server() -> Iterator[str]:
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args,
        directory=str(DOCS),
        **kwargs,
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError("post-admission evidence server did not stop")


def canonical_hash(value: Any) -> str:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(rendered).hexdigest()}"


def admitted_fixture(
    *,
    planner_mode: str,
    provider_calls: int,
    runtime_audit_ref: str | None,
    proofreader_disposition: str = "admit",
) -> dict[str, Any]:
    return {
        "contract_version": "reception.one.product-context-proposal.v1",
        "result": "proposal_ready",
        "safe": proofreader_disposition == "admit",
        "summary": (
            "Prepared two current authored-synthetic options for staff "
            "review. Nothing has been booked."
        ),
        "request_id": "synthetic-post-admission-browser-fixture",
        "correlation_id": "synthetic-correlation-browser-fixture",
        "context_revision": 1,
        "data_class": "authored_synthetic",
        "patient_handle": "synthetic-patient-browser-fixture",
        "patient_display": "Margaret Thompson",
        "practitioner_handle": "synthetic-practitioner-browser-fixture",
        "practitioner_display": "Dr Alex Shera",
        "goal": "create",
        "operation_id": "proposeAppointmentCreate",
        "candidate_slots": [
            {
                "slot_handle": "synthetic-slot-browser-0930",
                "appointment_date": REFERENCE_DATE,
                "start_time_local": "09:30",
                "duration_minutes": 15,
                "warning_codes": ["no_reservation"],
            },
            {
                "slot_handle": "synthetic-slot-browser-0945",
                "appointment_date": REFERENCE_DATE,
                "start_time_local": "09:45",
                "duration_minutes": 15,
                "warning_codes": ["no_reservation"],
            },
        ],
        "warning_codes": [
            "staff_confirmation_required",
            "staff_selection_required",
        ],
        "review": {
            "disposition": proofreader_disposition,
            "plan_hash": "synthetic-post-admission-plan-hash",
            "operator_ids": [
                "resolve_patient_reference",
                "resolve_practitioner_reference",
                "resolve_date_expression",
                "search_available_slots",
                "prepare_create_proposal",
            ],
            "safe_repairs": [],
            "violation_paths": (
                [] if proofreader_disposition == "admit"
                else ["$.proofreader_disposition"]
            ),
            "context_revision": 1,
        },
        "requires_confirmation": True,
        "proposal_only": True,
        "write_performed": False,
        "confirmation_performed": False,
        "provider_calls": provider_calls,
        "planner_mode": planner_mode,
        "runtime_audit_ref": runtime_audit_ref,
        "model_database_access": False,
        "database_reads_performed": True,
        "legacy_interpreter_gate_changed": False,
    }


def run_case(
    browser: Browser,
    *,
    base_url: str,
    requested_mode: str,
    fixture: dict[str, Any],
    switch_to: str | None = None,
    screenshot: Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    network: list[dict[str, str]] = []
    submitted_modes: list[str] = []
    blocked_external_hosts: set[str] = set()
    context = browser.new_context(
        viewport={"width": 1280, "height": 820},
        locale="en-AU",
        timezone_id="Australia/Brisbane",
    )
    page = context.new_page()

    def route_request(route: Route) -> None:
        request = route.request
        split = urlsplit(request.url)
        hostname = split.hostname or ""
        network.append(
            {
                "method": request.method.upper(),
                "hostname": hostname,
                "path": split.path,
            }
        )
        if request.method.upper() == "POST" and split.path == COMPOSE_PATH:
            body = request.post_data_json or {}
            submitted_modes.append(str(body.get("planner_mode", "")))
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(fixture),
            )
            return
        if hostname not in {"127.0.0.1", "localhost", ""}:
            blocked_external_hosts.add(hostname)
            route.abort()
            return
        route.continue_()

    page.route("**/*", route_request)
    page.goto(
        (
            f"{base_url}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            "&bureau_runtime_ui=true"
            "&product_context_live_local=true"
            f"&reference_date={REFERENCE_DATE}"
        ),
        wait_until="domcontentloaded",
    )
    page.locator("#bernie-meta-grid:not(.hidden)").wait_for(state="visible")
    planner = page.get_by_test_id("meta-grid-planner-mode")
    planner.wait_for(state="visible")
    if requested_mode != "deterministic":
        planner.select_option(requested_mode)
    request_box = page.get_by_label(
        "What would you like to find or prepare?",
        exact=True,
    )
    request_box.fill(REQUEST)
    request_box.press("Enter")
    page.wait_for_function(
        """() => {
          const host = document.getElementById("bernie-meta-grid");
          return ["answer", "blocked"].includes(
            host?.dataset.projectionState
          );
        }"""
    )
    provenance = page.get_by_test_id("meta-grid-planner-provenance")
    projection_state = page.locator("#bernie-meta-grid").get_attribute(
        "data-projection-state"
    )
    result: dict[str, Any] = {
        "requested_mode": requested_mode,
        "submitted_modes": submitted_modes,
        "projection_state": projection_state,
        "proposal_visible": page.locator(
            '[data-testid="meta-grid-slot"]'
        ).count() > 0,
        "provenance_visible": provenance.is_visible(),
        "provenance_text": (
            provenance.inner_text() if provenance.is_visible() else ""
        ),
        "audit_visible": page.get_by_test_id(
            "meta-grid-planner-provenance-audit"
        ).is_visible(),
        "blocked_external_hosts": sorted(blocked_external_hosts),
    }
    if screenshot is not None:
        page.screenshot(path=str(screenshot), full_page=True)
    if switch_to is not None:
        planner.select_option(switch_to)
        page.wait_for_function(
            """() => document.getElementById("bernie-meta-grid")
              ?.dataset.projectionState === "planner_reselection_required" """
        )
        result["after_switch"] = {
            "selected_mode": planner.input_value(),
            "proposal_visible": page.locator(
                '[data-testid="meta-grid-slot"]'
            ).count() > 0,
            "provenance_visible": provenance.is_visible(),
            "audit_visible": page.get_by_test_id(
                "meta-grid-planner-provenance-audit"
            ).is_visible(),
            "request_retained": request_box.input_value() == REQUEST,
            "announcement": page.locator(
                "#meta-grid-announcer"
            ).inner_text(),
        }
        if screenshot is not None:
            page.screenshot(path=str(CLEARED_SCREENSHOT), full_page=True)
    context.close()
    return result, network


def run() -> dict[str, Any]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with static_server() as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        standard, standard_network = run_case(
            browser,
            base_url=base_url,
            requested_mode="deterministic",
            fixture=admitted_fixture(
                planner_mode="deterministic",
                provider_calls=0,
                runtime_audit_ref=None,
            ),
            switch_to="isolated_vertex",
            screenshot=STANDARD_SCREENSHOT,
        )
        isolated, isolated_network = run_case(
            browser,
            base_url=base_url,
            requested_mode="isolated_vertex",
            fixture=admitted_fixture(
                planner_mode="isolated_vertex",
                provider_calls=1,
                runtime_audit_ref="runtime-synthetic-admitted-001",
            ),
            switch_to="deterministic",
            screenshot=ISOLATED_SCREENSHOT,
        )
        mismatch_cases: dict[str, dict[str, Any]] = {}
        mismatch_fixtures = {
            "planner_mismatch": admitted_fixture(
                planner_mode="deterministic",
                provider_calls=0,
                runtime_audit_ref=None,
            ),
            "proofreader_mismatch": admitted_fixture(
                planner_mode="isolated_vertex",
                provider_calls=1,
                runtime_audit_ref="runtime-synthetic-admitted-002",
                proofreader_disposition="revision_required",
            ),
            "call_count_mismatch": admitted_fixture(
                planner_mode="isolated_vertex",
                provider_calls=0,
                runtime_audit_ref="runtime-synthetic-admitted-003",
            ),
            "audit_reference_mismatch": admitted_fixture(
                planner_mode="isolated_vertex",
                provider_calls=1,
                runtime_audit_ref="not allowed whitespace",
            ),
        }
        all_network = standard_network + isolated_network
        for name, fixture in mismatch_fixtures.items():
            outcome, case_network = run_case(
                browser,
                base_url=base_url,
                requested_mode="isolated_vertex",
                fixture=fixture,
            )
            mismatch_cases[name] = outcome
            all_network.extend(case_network)
        browser.close()

    compose_requests = [
        item
        for item in all_network
        if item["method"] == "POST" and item["path"] == COMPOSE_PATH
    ]
    provider_hosts = sorted(
        {
            item["hostname"]
            for item in all_network
            if (
                "aiplatform.googleapis.com" in item["hostname"]
                or "generativelanguage.googleapis.com" in item["hostname"]
                or "api.openai.com" in item["hostname"]
            )
        }
    )
    mismatch_fail_closed = all(
        outcome["projection_state"] == "blocked"
        and outcome["proposal_visible"] is False
        and outcome["provenance_visible"] is False
        and outcome["audit_visible"] is False
        for outcome in mismatch_cases.values()
    )
    blocked_external_hosts = sorted(
        {
            host
            for outcome in [standard, isolated, *mismatch_cases.values()]
            for host in outcome["blocked_external_hosts"]
        }
    )
    checks = {
        "standard_uses_shared_admitted_renderer": (
            standard["projection_state"] == "answer"
            and standard["proposal_visible"] is True
            and standard["provenance_visible"] is True
            and "Standard planner" in standard["provenance_text"]
            and "Proofreader admitted" in standard["provenance_text"]
            and "0 provider calls" in standard["provenance_text"]
            and standard["audit_visible"] is False
        ),
        "isolated_uses_shared_admitted_renderer": (
            isolated["projection_state"] == "answer"
            and isolated["proposal_visible"] is True
            and isolated["provenance_visible"] is True
            and "Isolated model" in isolated["provenance_text"]
            and "Proofreader admitted" in isolated["provenance_text"]
            and "1 provider call" in isolated["provenance_text"]
            and isolated["audit_visible"] is True
        ),
        "standard_switch_clears_stale_state": all(
            [
                standard["after_switch"]["proposal_visible"] is False,
                standard["after_switch"]["provenance_visible"] is False,
                standard["after_switch"]["audit_visible"] is False,
                standard["after_switch"]["request_retained"] is True,
            ]
        ),
        "isolated_switch_clears_stale_state": all(
            [
                isolated["after_switch"]["proposal_visible"] is False,
                isolated["after_switch"]["provenance_visible"] is False,
                isolated["after_switch"]["audit_visible"] is False,
                isolated["after_switch"]["request_retained"] is True,
            ]
        ),
        "mismatched_contracts_fail_closed": mismatch_fail_closed,
        "one_local_fixture_response_per_case": len(compose_requests) == 6,
        "no_provider_request": provider_hosts == [],
        "only_office_bootstrap_was_blocked": (
            blocked_external_hosts == ["appsforoffice.microsoft.com"]
        ),
    }
    passed = all(checks.values())
    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.bureau_post_admission_runtime_hardening.v1"
        ),
        "result": (
            "reception_one_bureau_post_admission_runtime_hardening_pass"
            if passed
            else "reception_one_bureau_post_admission_runtime_hardening_failed"
        ),
        "evidence_label": "route_intercepted_browser",
        "data_class": "authored_synthetic",
        "request_text_retained": False,
        "request_hash": canonical_hash({"request": REQUEST}),
        "checks": checks,
        "standard": standard,
        "isolated": isolated,
        "mismatch_cases": mismatch_cases,
        "local_fixture_response_count": len(compose_requests),
        "provider_hosts": provider_hosts,
        "blocked_external_hosts": blocked_external_hosts,
        "provider_calls": 0,
        "credential_reads": 0,
        "database_reads": 0,
        "database_writes": 0,
        "appointment_confirmation_performed": False,
        "appointment_write_performed": False,
        "screenshots": [
            STANDARD_SCREENSHOT.relative_to(ROOT).as_posix(),
            ISOLATED_SCREENSHOT.relative_to(ROOT).as_posix(),
            CLEARED_SCREENSHOT.relative_to(ROOT).as_posix(),
        ],
        "candid_limit": (
            "This route-intercepted authored-synthetic fixture proves only "
            "client-side planner/proofreader/provenance binding, shared typed "
            "presentation and stale-state clearing. It is not a new backend "
            "or provider result."
        ),
    }
    evidence["evidence_hash"] = canonical_hash(evidence)
    EVIDENCE.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not passed:
        raise RuntimeError(
            "post-admission runtime hardening failed: "
            + ",".join(key for key, value in checks.items() if not value)
        )
    return evidence


def main() -> int:
    try:
        evidence = run()
    except (OSError, RuntimeError) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_bureau_post_admission_"
                        "runtime_hardening_failed"
                    ),
                    "reason": str(error),
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "fixture_responses": evidence[
                    "local_fixture_response_count"
                ],
                "provider_calls": 0,
                "writes": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
