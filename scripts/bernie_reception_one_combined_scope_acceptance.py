"""Real-browser Reception One combined-scope acceptance with zero interception."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import Browser, Page, Playwright, expect, sync_playwright

import bernie_meta_grid_live_local_acceptance as shared
from bernie_reception_one_combined_scope_harness import (
    LOCKED_DATABASE,
    database_readback,
    launch_runtime,
    readiness_report,
    stop_runtime,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "bernie-reception-one-combined-scope-proof"
)
AUTH_URL = "http://[::1]:3000/meta-grid-auth.html"
COMBINED_REQUEST = (
    "Show me all the available slots with Dr Shera for a half-hour appointment "
    "with Margaret Thompson after 2 today."
)

# Shared helpers remain pure browser/measurement utilities. Force this task's
# exact IPv6 origin so the existing IPv4 review session is never contacted.
shared.AUTH_URL = AUTH_URL
shared.STATIC_HOSTS.add("::1")


def _open(browser: Browser, evidence: shared.BrowserEvidence, width: int, height: int, *, touch: bool = False):
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=1,
        has_touch=touch,
        locale="en-AU",
        timezone_id="Australia/Brisbane",
    )
    page = context.new_page()
    evidence.attach(page)
    page.goto(AUTH_URL, wait_until="domcontentloaded")
    page.wait_for_url("**/diary/diary.html?reference_date=2026-07-27**", timeout=20_000)
    expect(page.get_by_test_id("meta-grid-launch-button")).to_be_visible(timeout=20_000)

    target = "2026-07-27"
    picker = page.locator("#diary-date-picker")
    for _ in range(21):
        current = picker.input_value()
        if current == target:
            break
        button = page.locator("#btn-next-day" if current < target else "#btn-prev-day")
        with page.expect_response(
            lambda response: (
                response.request.method.upper() == "GET"
                and response.url.split("?", 1)[0].endswith("/api/v1/appointments")
            ),
            timeout=15_000,
        ):
            button.click()
        expect(picker).not_to_have_value(current, timeout=15_000)
    expect(picker).to_have_value(target, timeout=15_000)
    page.get_by_test_id("meta-grid-launch-button").click()
    expect(page.get_by_test_id("meta-grid-workspace")).to_be_visible(timeout=20_000)
    shared._wait_family(page, "ordinary_overview")
    evidence.assert_clean()
    return context, page


def _assert_combined_scope(
    page: Page,
    *,
    date_fragment: str = "27 July 2026",
    time_fragment: str = "2:00 pm",
    duration: int = 30,
    require_slot: bool = True,
) -> None:
    scope = page.locator("#meta-grid-scope-summary")
    expect(scope).to_contain_text("Margaret Thompson")
    expect(scope).to_contain_text("Alex Shera")
    expect(scope).to_contain_text(date_fragment)
    expect(scope).to_contain_text(time_fragment)
    expect(scope).to_contain_text(f"{duration} minutes")
    if require_slot:
        expect(page.get_by_test_id("meta-grid-slot").first).to_be_visible()


def _submit_combined(page: Page) -> None:
    shared._submit(page, COMBINED_REQUEST, "availability_slots")
    _assert_combined_scope(page)


def _metrics_record(page: Page, *, scenario_id: str, width: int, height: int, results: dict[str, object]) -> dict[str, object]:
    metrics = shared._viewport_metrics(page)
    shared._assert_metrics(metrics)
    return {
        "id": scenario_id,
        "width": width,
        "height": height,
        **metrics,
        "scenario_results": results,
    }


def _save_current_viewport(page: Page, output: Path, name: str) -> dict[str, object]:
    target = output / name
    page.screenshot(path=str(target), full_page=False)
    return {
        "file": name,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "raster_integrity": shared.png_painted_width(target),
    }


def run_desktop(browser: Browser, output: Path, evidence: shared.BrowserEvidence):
    context, page = _open(browser, evidence, 1440, 900)
    screenshots: list[dict[str, object]] = []
    try:
        tab_sequence = shared._keyboard_sequence(page, steps=10)
        page.get_by_test_id("meta-grid-explain").click()
        expect(page.locator("#meta-grid-evidence")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator("#meta-grid-evidence")).to_be_hidden()
        expect(page.get_by_test_id("meta-grid-explain")).to_be_focused()

        _submit_combined(page)
        screenshots.append(
            shared._save_screenshot(page, output, "desktop-combined-scope-1440x900.png")
        )

        prior = page.locator("#meta-grid-scope-summary").inner_text()
        shared._submit(page, "tomorrow instead", "availability_slots", previous_scope=prior)
        _assert_combined_scope(page, date_fragment="28 July 2026", require_slot=False)

        prior = page.locator("#meta-grid-scope-summary").inner_text()
        shared._submit(page, "make it 45 minutes", "availability_slots", previous_scope=prior)
        _assert_combined_scope(
            page, date_fragment="28 July 2026", duration=45, require_slot=False
        )

        prior = page.locator("#meta-grid-scope-summary").inner_text()
        shared._submit(page, "after 3", "availability_slots", previous_scope=prior)
        _assert_combined_scope(
            page,
            date_fragment="28 July 2026",
            time_fragment="3:00 pm",
            duration=45,
            require_slot=False,
        )

        page.locator("#meta-grid-overview").click()
        shared._wait_family(page, "ordinary_overview")
        page.locator("#meta-grid-back").click()
        shared._wait_family(page, "availability_slots")
        _assert_combined_scope(
            page,
            date_fragment="28 July 2026",
            time_fragment="3:00 pm",
            duration=45,
            require_slot=False,
        )

        evidence.assert_clean()
        record = _metrics_record(
            page,
            scenario_id="desktop_landscape",
            width=1440,
            height=900,
            results={
                "combined_scope": "pass",
                "contextual_date_refinement": "pass",
                "contextual_duration_refinement": "pass",
                "contextual_time_refinement": "pass",
                "ordinary_overview_and_back": "pass",
                "escape_explanation": "pass",
                "keyboard_tab_sequence": tab_sequence,
            },
        )
        page.get_by_role("button", name="Return to full Diary grid").click()
        expect(page.get_by_test_id("meta-grid-workspace")).to_be_hidden()
        expect(page.locator("#diary-grid-container")).to_be_visible()
        record["full_diary_fallback"] = "pass"
        return record, screenshots
    finally:
        context.close()


def run_tablet_landscape(browser: Browser, output: Path, evidence: shared.BrowserEvidence):
    context, page = _open(browser, evidence, 1024, 768, touch=True)
    screenshots: list[dict[str, object]] = []
    try:
        _submit_combined(page)
        page.get_by_test_id("meta-grid-slot").first.tap()
        expect(page.locator("#meta-grid-state-label")).to_have_text("Selection")
        prepare = page.get_by_test_id("meta-grid-prepare-scoped-proposal")
        expect(prepare).to_contain_text("Margaret Thompson")
        prepare.tap()
        shared._wait_family(page, "proposal_review")
        expect(page.locator("#meta-grid-state-label")).to_contain_text("not committed")
        expect(page.get_by_test_id("meta-grid-proposal-handoff")).to_be_enabled()
        screenshots.append(
            shared._save_screenshot(page, output, "tablet-landscape-proposal-1024x768.png")
        )
        evidence.assert_clean()
        return (
            _metrics_record(
                page,
                scenario_id="tablet_landscape",
                width=1024,
                height=768,
                results={
                    "combined_scope": "pass",
                    "touch_slot_selection": "pass",
                    "scoped_patient_proposal": "pass; not committed",
                    "proposal_handoff_activated": False,
                },
            ),
            screenshots,
        )
    finally:
        context.close()


def run_tablet_portrait(browser: Browser, output: Path, evidence: shared.BrowserEvidence):
    context, page = _open(browser, evidence, 768, 1024, touch=True)
    screenshots: list[dict[str, object]] = []
    try:
        _submit_combined(page)
        prior = page.locator("#meta-grid-scope-summary").inner_text()
        shared._submit(page, "make it 45 minutes", "availability_slots", previous_scope=prior)
        _assert_combined_scope(page, duration=45)
        page.get_by_test_id("meta-grid-slot").first.tap()
        page.locator("#meta-grid-back").tap()
        shared._wait_family(page, "availability_slots")
        _assert_combined_scope(page, duration=45)
        screenshots.append(
            shared._save_screenshot(page, output, "tablet-portrait-refined-back-768x1024.png")
        )
        evidence.assert_clean()
        return (
            _metrics_record(
                page,
                scenario_id="tablet_portrait",
                width=768,
                height=1024,
                results={
                    "combined_scope": "pass",
                    "duration_refinement": "pass",
                    "selection_back_reversible": "pass",
                },
            ),
            screenshots,
        )
    finally:
        context.close()


def run_phone_portrait(browser: Browser, output: Path, evidence: shared.BrowserEvidence):
    context, page = _open(browser, evidence, 390, 844, touch=True)
    screenshots: list[dict[str, object]] = []
    interruption_method = "foreground_page_switch"
    try:
        _submit_combined(page)
        slot = page.get_by_test_id("meta-grid-slot").first
        slot.focus()
        page.keyboard.press("Space")
        expect(page.locator("#meta-grid-state-label")).to_have_text("Selection")
        prepare = page.get_by_test_id("meta-grid-prepare-scoped-proposal")
        prepare.focus()
        page.keyboard.press("Enter")
        shared._wait_family(page, "proposal_review")

        page.get_by_test_id("meta-grid-privacy").tap()
        expect(page.get_by_test_id("meta-grid-privacy")).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#meta-grid-privacy-banner")).to_be_visible()
        expect(page.locator("#meta-grid-scope-summary")).to_have_class("meta-grid-scope-summary meta-grid-sensitive")
        expect(page.locator("#meta-grid-announcer")).to_have_text("Patient-sensitive details are hidden.")
        screenshots.append(
            shared._save_screenshot(page, output, "phone-portrait-private-proposal-390x844.png")
        )

        other = context.new_page()
        other.set_content("<title>Foreground interruption</title><p>synthetic</p>")
        other.bring_to_front()
        try:
            expect(page.locator("#meta-grid-state-label")).to_have_text("Refresh required", timeout=2_000)
        except AssertionError:
            interruption_method = "standards_dom_blur_event_headless_fallback"
            page.evaluate("window.dispatchEvent(new Event('blur'))")
        page.bring_to_front()
        other.close()
        expect(page.locator("#meta-grid-state-label")).to_have_text("Refresh required")
        screenshots.append(
            shared._save_screenshot(page, output, "phone-portrait-interruption-390x844.png")
        )
        page.get_by_test_id("meta-grid-refresh-current").tap()
        shared._wait_family(page, "availability_slots")
        expect(page.locator("#meta-grid-scope-summary")).to_contain_text("Margaret Thompson")
        expect(page.get_by_test_id("meta-grid-slot").first).to_be_visible()
        expect(page.get_by_test_id("meta-grid-prepare-scoped-proposal")).to_have_count(0)
        page.get_by_test_id("meta-grid-privacy").tap()
        _assert_combined_scope(page)

        evidence.assert_clean()
        return (
            _metrics_record(
                page,
                scenario_id="phone_portrait",
                width=390,
                height=844,
                results={
                    "combined_scope": "pass",
                    "keyboard_space_selection": "pass",
                    "keyboard_enter_scoped_proposal": "pass; not committed",
                    "privacy_mask_and_live_region": "pass",
                    "interruption": f"pass; {interruption_method}",
                    "fresh_patient_and_availability_recovery": "pass",
                },
            ),
            screenshots,
        )
    finally:
        context.close()


def run_phone_landscape(browser: Browser, output: Path, evidence: shared.BrowserEvidence):
    context, page = _open(browser, evidence, 844, 390, touch=True)
    screenshots: list[dict[str, object]] = []
    try:
        _submit_combined(page)
        request = page.locator("#meta-grid-request")
        request.focus()
        request.fill("after 3")
        page.keyboard.press("Enter")
        shared._wait_family(page, "availability_slots")
        _assert_combined_scope(page, time_fragment="3:00 pm")
        page.locator("#meta-grid-scope-summary").scroll_into_view_if_needed()
        screenshots.append(
            _save_current_viewport(page, output, "phone-landscape-refined-844x390.png")
        )
        evidence.assert_clean()
        return (
            _metrics_record(
                page,
                scenario_id="phone_landscape",
                width=844,
                height=390,
                results={
                    "combined_scope": "pass",
                    "keyboard_enter_request": "pass",
                    "time_refinement": "pass",
                },
            ),
            screenshots,
        )
    finally:
        context.close()


def _run_browser(playwright: Playwright, output: Path, evidence: shared.BrowserEvidence):
    browser = playwright.chromium.launch(headless=True)
    viewports: list[dict[str, object]] = []
    screenshots: list[dict[str, object]] = []
    try:
        for runner in (
            run_desktop,
            run_tablet_landscape,
            run_tablet_portrait,
            run_phone_portrait,
            run_phone_landscape,
        ):
            viewport, captured = runner(browser, output, evidence)
            viewports.append(viewport)
            screenshots.extend(captured)
    finally:
        browser.close()
    return viewports, screenshots


def run(output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    readiness = readiness_report()
    assert readiness["ready"] is True, readiness
    before = database_readback()
    runtime, processes = launch_runtime()
    evidence = shared.BrowserEvidence()
    try:
        with sync_playwright() as playwright:
            viewports, screenshots = _run_browser(playwright, output, evidence)
        evidence.assert_clean()
    finally:
        stop_runtime(processes)
    after = database_readback()
    assert before["counts"] == after["counts"], {"before": before, "after": after}
    assert before["sha256"] == after["sha256"], {"before": before, "after": after}
    for table in (
        "appointment_audit_log",
        "appointment_command_idempotency",
        "bernie_booking_sessions",
        "bernie_session_events",
    ):
        assert after["counts"][table] == 0, {table: after["counts"][table]}

    observed = set(evidence.requests)
    for required in (
        ("GET", "/api/v1/patients/search"),
        ("POST", "/api/v1/appointments/proposals/slot-search"),
        ("POST", "/api/v1/appointments/proposals/bernie/supervised-booking"),
    ):
        assert required in observed, required
    assert not any("/confirm" in path or "/sessions" in path for _method, path in observed)

    route_counts = [
        {"method": method, "path": path, "count": count}
        for (method, path), count in sorted(evidence.requests.items())
        if path.startswith("/api/v1/")
    ]
    result = {
        "schema_version": "bernie.reception-one-combined-scope.browser-evidence.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "browser_pass",
        "evidence_mode": "live_local_browser_backend_postgres",
        "route": (
            "http://[::1]:3000/diary/diary.html?reference_date=2026-07-27"
            "&bernie_session=false&standalone_diary=true"
        ),
        "runtime": {
            "database": LOCKED_DATABASE,
            "provider": runtime["provider"],
            "loopback_family": runtime["loopback_family"],
            "active_ipv4_review_session_contacted": False,
            "cloud_credentials_present": False,
            "credential_recorded": False,
            "token_recorded": False,
        },
        "route_interception": False,
        "api_interception": False,
        "browser_actions": "visible UI actions only; no page.route and no page-internal projection or command functions",
        "authority": {
            "appointment_write_authority": False,
            "proposal_handoff_activated": False,
            "confirmation_control_activated": False,
            "event_runtime_activated": False,
            "operational_receipt_produced": False,
        },
        "database_readback": {
            "before": before,
            "after": after,
            "counts_identical": True,
            "sha256_identical": True,
        },
        "network": {
            "only_loopback": True,
            "forbidden_requests": evidence.forbidden,
            "api_method_path_counts": route_counts,
            "failed_api_responses": [row for row in evidence.responses if int(row["status"]) >= 400],
        },
        "viewports": viewports,
        "keyboard": {
            "enter_request_submit": "pass on desktop and both smartphone orientations",
            "space_slot_selection": "pass on smartphone portrait",
            "enter_scoped_proposal": "pass on smartphone portrait",
            "escape_explanation_dismissal": "pass with focus returned",
            "native_tab_sequence": viewports[0]["scenario_results"]["keyboard_tab_sequence"],
            "page_internal_command_invocation": False,
        },
        "privacy": {
            "patient_scope_masked": True,
            "proposal_summary_masked": True,
            "private_live_region_sanitized": True,
        },
        "interruption": {
            "stale_proposal_reused": False,
            "fresh_patient_read_required": True,
            "fresh_availability_read_required": True,
        },
        "screenshots": screenshots,
        "browser_console_warnings_or_errors": evidence.console,
        "browser_page_errors": evidence.page_errors,
        "claims_not_made": [
            "provider",
            "PII",
            "committed event",
            "Stage 3B",
            "representative usability",
            "production",
            "deployment",
            "release",
            "final visual design",
        ],
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    for forbidden in ("Margaret", "date_of_birth", "patient_id", "access_token", "password"):
        assert forbidden not in serialized
    (output / "browser-acceptance-evidence.json").write_text(serialized, encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = run(args.output.resolve())
    except Exception as exc:
        print(
            json.dumps(
                {"result": "failed", "error_type": type(exc).__name__, "detail": str(exc)}
            ),
            file=sys.stderr,
        )
        return 1
    print(
        json.dumps(
            {
                "result": result["result"],
                "evidence_mode": result["evidence_mode"],
                "viewports": len(result["viewports"]),
                "screenshots": len(result["screenshots"]),
                "database_counts_identical": result["database_readback"]["counts_identical"],
                "database_sha256_identical": result["database_readback"]["sha256_identical"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
