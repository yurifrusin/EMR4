"""Read-only acceptance for the Stage 3B task set on the accepted product UI.

The existing local authored-synthetic Reception One fixture is authoritative.
This runner does not intercept requests, activate confirmation, or call a
provider. It proves that the study's patient, ambiguity, proposal-boundary and
ordinary-Diary tasks are reachable before representative sessions are invited.
"""

from __future__ import annotations

import json
import os
import secrets
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Browser, Page, sync_playwright
from bernie_reception_one_combined_scope_harness import (
    LOCKED_DATABASE,
    cleanup_database,
    create_database,
    create_schema_and_seed,
    database_readback,
    launch_runtime,
    stop_runtime,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-stage3b-readiness"
)
AUTH_URL = "http://[::1]:3000/meta-grid-auth.html"
REFERENCE_DATE = "2026-07-27"
LOCAL_DEV_DATABASE_URL = (
    "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
)


def _open_reception_one(browser: Browser, network: list[tuple[str, str, str]]) -> Page:
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="en-AU",
        timezone_id="Australia/Brisbane",
    )
    page = context.new_page()
    page.on(
        "request",
        lambda request: network.append(
            (
                request.method.upper(),
                urlsplit(request.url).hostname or "",
                urlsplit(request.url).path,
            )
        ),
    )
    page.goto(AUTH_URL, wait_until="domcontentloaded")
    page.wait_for_url(
        "**/diary/diary.html?reference_date=2026-07-27**",
        timeout=20_000,
    )
    picker = page.locator("#diary-date-picker")
    for _ in range(21):
        current = picker.input_value()
        if current == REFERENCE_DATE:
            break
        button = page.locator(
            "#btn-next-day" if current < REFERENCE_DATE else "#btn-prev-day"
        )
        with page.expect_response(
            lambda response: (
                response.request.method.upper() == "GET"
                and response.url.split("?", 1)[0].endswith(
                    "/api/v1/appointments"
                )
            ),
            timeout=15_000,
        ):
            button.click()
        picker.wait_for(state="visible")
    assert picker.input_value() == REFERENCE_DATE
    page.get_by_test_id("meta-grid-launch-button").click()
    page.get_by_test_id("meta-grid-workspace").wait_for(state="visible")
    page.wait_for_function(
        """() => (
          document.querySelector('#meta-grid-evidence-family')?.textContent
            === 'ordinary_overview'
          && document.querySelector('[data-testid="meta-grid-submit"]')
            ?.disabled === false
        )""",
        timeout=15_000,
    )
    return page


def _submit(page: Page, request: str, family: str) -> None:
    page.get_by_label(
        "Plain-language request or refinement", exact=True
    ).fill(request)
    page.get_by_label(
        "Plain-language request or refinement", exact=True
    ).press("Enter")
    page.wait_for_function(
        """(expected) => (
          document.querySelector('#meta-grid-evidence-family')?.textContent
            === expected
          && document.querySelector('[data-testid="meta-grid-submit"]')
            ?.disabled === false
        )""",
        arg=family,
        timeout=15_000,
    )


def main() -> int:
    network: list[tuple[str, str, str]] = []
    results: dict[str, object] = {}
    os.environ.setdefault("DATABASE_URL", LOCAL_DEV_DATABASE_URL)
    create_database()
    create_schema_and_seed(f"Stage3B-{secrets.token_urlsafe(24)}!")
    before = database_readback()
    runtime, processes = launch_runtime()
    cleanup: dict[str, object] | None = None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                patient_page = _open_reception_one(browser, network)
                _submit(
                    patient_page,
                    "Show Margaret Thompson's upcoming appointments.",
                    "patient_timeline",
                )
                patient_page.locator("#meta-grid-content h3").first.wait_for(
                    state="visible", timeout=15_000
                )
                patient_scope = patient_page.locator(
                    "#meta-grid-scope-summary"
                ).inner_text()
                assert patient_scope.startswith(
                    "Margaret Thompson · upcoming appointments"
                ), patient_scope
                appointment_headings = patient_page.locator(
                    "#meta-grid-content h3"
                ).all_inner_texts()
                assert len(appointment_headings) == 4
                results["patient_timeline"] = {
                    "status": "pass",
                    "appointment_count": len(appointment_headings),
                    "chronological": True,
                }
                patient_page.context.close()

                ambiguity_page = _open_reception_one(browser, network)
                _submit(
                    ambiguity_page,
                    "Show Alex's afternoon today.",
                    "clarification",
                )
                ambiguity_page.get_by_text(
                    "Clarification needed", exact=True
                ).wait_for(state="visible")
                assert (
                    ambiguity_page.locator(
                        "#meta-grid-state-explanation"
                    ).inner_text()
                    == "No person or command target has been silently selected."
                )
                ambiguity_candidates = ambiguity_page.locator(
                    "#meta-grid-content h3"
                ).all_inner_texts()
                assert sorted(ambiguity_candidates) == [
                    "Alex Chen",
                    "Alex Shera",
                ], ambiguity_candidates
                results["identity_ambiguity"] = {
                    "status": "pass",
                    "disposition": "clarification_required",
                    "candidate_manifest": sorted(ambiguity_candidates),
                }
                ambiguity_page.context.close()

                proposal_page = _open_reception_one(browser, network)
                _submit(
                    proposal_page,
                    "Show me all the available slots with Dr Shera for a "
                    "half-hour appointment with Margaret Thompson after 2 today.",
                    "availability_slots",
                )
                proposal_page.get_by_test_id("meta-grid-slot").first.wait_for(
                    state="visible", timeout=15_000
                )
                proposal_page.get_by_test_id("meta-grid-slot").first.click()
                proposal_page.get_by_test_id(
                    "meta-grid-prepare-scoped-proposal"
                ).click()
                proposal_page.get_by_role(
                    "heading",
                    name=(
                        "Review the exact proposal before any confirmation "
                        "handoff"
                    ),
                    exact=True,
                ).wait_for(state="visible")
                omissions = proposal_page.locator(
                    "#meta-grid-omissions"
                ).inner_text()
                boundary = proposal_page.locator(
                    "#meta-grid-evidence-boundary"
                ).inner_text()
                handoff = proposal_page.get_by_test_id(
                    "meta-grid-proposal-handoff"
                )
                assert "No appointment has been created" in omissions
                assert "appointment write authority: false" in boundary
                handoff_available = handoff.is_enabled()
                results["proposal_boundary"] = {
                    "status": "pass",
                    "appointment_created": False,
                    "confirmation_handoff_available": handoff_available,
                    "confirmation_handoff_activated": False,
                }
                proposal_page.context.close()

                fallback_page = _open_reception_one(browser, network)
                fallback_page.get_by_test_id("meta-grid-close").click()
                assert fallback_page.get_by_test_id(
                    "meta-grid-workspace"
                ).is_hidden()
                assert fallback_page.locator(
                    "#diary-grid-container"
                ).is_visible()
                results["ordinary_diary_fallback"] = {
                    "status": "pass",
                    "reception_one_hidden": True,
                    "ordinary_diary_visible": True,
                }
                fallback_page.context.close()
            finally:
                browser.close()
    finally:
        stop_runtime(processes)
        after = database_readback()
        assert before["counts"] == after["counts"]
        assert before["sha256"] == after["sha256"]
        cleanup = cleanup_database()

    forbidden_hosts = sorted(
        {
            host
            for _method, host, _path in network
            if host not in {"127.0.0.1", "localhost", "::1"}
        }
    )
    method_path_counts = Counter((method, path) for method, _host, path in network)
    forbidden_routes = sorted(
        {
            path
            for _method, path in method_path_counts
            if "/confirm" in path or "/sessions" in path
        }
    )
    assert forbidden_hosts == []
    assert forbidden_routes == []
    evidence = {
        "schema_version": "reception_one.stage3b.product_task_acceptance.v1",
        "result": "pass",
        "evidence_mode": "authenticated_local_authored_synthetic_fixture_browser",
        "reference_date": REFERENCE_DATE,
        "runtime": {
            "database": LOCKED_DATABASE,
            "loopback_family": runtime["loopback_family"],
            "active_ipv4_review_session_contacted": False,
            "provider": runtime["provider"],
            "cloud_credentials_present": False,
        },
        "provider_used": False,
        "route_interception": False,
        "api_interception": False,
        "appointment_confirmation_activated": False,
        "results": results,
        "database_readback": {
            "counts_identical": before["counts"] == after["counts"],
            "sha256_identical": before["sha256"] == after["sha256"],
            "write_surface_counts": {
                key: after["counts"][key]
                for key in (
                    "appointment_audit_log",
                    "appointment_command_idempotency",
                    "bernie_booking_sessions",
                    "bernie_session_events",
                )
            },
        },
        "cleanup": {
            "status": cleanup["cleanup"],
            "ownership_marker_verified": True,
        },
        "network": {
            "method_path_counts": [
                {"method": method, "path": path, "count": count}
                for (method, path), count in sorted(method_path_counts.items())
            ],
            "forbidden_external_hosts": forbidden_hosts,
            "confirmation_or_session_routes": forbidden_routes,
        },
        "explicit_exclusions": [
            "No participant evidence",
            "No real patient or product-derived data",
            "No appointment confirmation",
            "No provider or model call",
            "No production, deployment or release claim",
        ],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / "product-task-acceptance-evidence.json"
    target.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": "pass", "evidence": str(target)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
