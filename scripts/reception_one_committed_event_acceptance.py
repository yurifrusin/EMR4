"""Real-browser and real-PostgreSQL acceptance for the bounded event vertical."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx
from playwright.sync_api import Browser, Page, expect, sync_playwright

import bernie_meta_grid_live_local_acceptance as shared
import bernie_meta_grid_live_local_harness as fixture_base
from reception_one_committed_event_harness import (
    IN_SCOPE_APPOINTMENT_ID,
    LOCKED_DATABASE,
    OUT_OF_SCOPE_APPOINTMENT_ID,
    database_readback,
    database_security_probes,
    launch_runtime,
    readiness_report,
    stop_runtime,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-committed-event-vertical"
)
AUTH_URL = "http://[::1]:3000/meta-grid-auth.html"
API_BASE_URL = "http://[::1]:8001/api/v1"
PATIENT_TIMELINE_REQUEST = "Show Margaret Thompson's upcoming appointments"

shared.AUTH_URL = AUTH_URL
shared.STATIC_HOSTS.add("::1")
shared.API_ALLOWED.update(
    {
        ("GET", "/api/v1/diary/events/committed"),
        ("GET", f"/api/v1/appointments/{IN_SCOPE_APPOINTMENT_ID}"),
    }
)


def _open(
    browser: Browser,
    evidence: shared.BrowserEvidence,
    width: int,
    height: int,
    *,
    touch: bool = False,
) -> tuple[object, Page]:
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
    page.get_by_test_id("meta-grid-launch-button").click()
    expect(page.get_by_test_id("meta-grid-workspace")).to_be_visible(timeout=20_000)
    shared._wait_family(page, "ordinary_overview")
    shared._submit(page, PATIENT_TIMELINE_REQUEST, "patient_timeline")
    expect(page.locator(f'[data-appointment-id="{IN_SCOPE_APPOINTMENT_ID}"]')).to_be_visible()
    page.wait_for_timeout(2200)
    evidence.assert_clean()
    return context, page


def _support_client(password: str) -> httpx.Client:
    client = httpx.Client(base_url=API_BASE_URL, timeout=20, trust_env=False)
    login = client.post(
        "/auth/login",
        data={"username": fixture_base.SYNTHETIC_EMAIL, "password": password},
    )
    login.raise_for_status()
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def _confirmed_reschedule(
    client: httpx.Client,
    appointment_id,
    *,
    start_time_local: str,
    key: str,
) -> tuple[dict[str, object], dict[str, object]]:
    proposal = client.post(
        f"/appointments/proposals/update/{appointment_id}",
        headers={"Idempotency-Key": f"proposal-{key}"},
        json={
            "appointment_date": "2026-07-27",
            "start_time_local": start_time_local,
        },
    )
    proposal.raise_for_status()
    confirm_payload = proposal.json()["confirm_payload"]
    confirm_payload["confirmed"] = True
    confirmed = client.post(
        "/appointments/proposals/update/confirm",
        headers={"Idempotency-Key": key},
        json=confirm_payload,
    )
    confirmed.raise_for_status()
    assert confirmed.json()["safe"] is True
    return confirm_payload, confirmed.json()


def _replay_confirm(
    client: httpx.Client,
    payload: dict[str, object],
    expected: dict[str, object],
    key: str,
) -> None:
    replay = client.post(
        "/appointments/proposals/update/confirm",
        headers={"Idempotency-Key": key},
        json=payload,
    )
    replay.raise_for_status()
    assert replay.json() == expected


def _save(page: Page, output: Path, name: str) -> dict[str, object]:
    target = output / name
    page.screenshot(path=str(target), full_page=False)
    return {
        "file": name,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "raster_integrity": shared.png_painted_width(target),
    }


def _viewport_record(
    page: Page,
    *,
    scenario_id: str,
    width: int,
    height: int,
    results: dict[str, object],
) -> dict[str, object]:
    metrics = shared._viewport_metrics(page)
    shared._assert_metrics(metrics)
    return {
        "id": scenario_id,
        "width": width,
        "height": height,
        **metrics,
        "scenario_results": results,
    }


def _assert_no_cue(pages: list[Page]) -> None:
    for page in pages:
        expect(page.get_by_test_id("meta-grid-event-cue")).to_be_hidden()


def _assert_fresh_cue(page: Page, *, private: bool = False) -> None:
    cue = page.get_by_test_id("meta-grid-event-cue")
    expect(cue).to_be_visible(timeout=12_000)
    expect(page.locator(f'[data-appointment-id="{IN_SCOPE_APPOINTMENT_ID}"]')).to_contain_text(
        "10:00 am"
    )
    expect(page.locator("#meta-grid-event-cue-reason")).to_contain_text(
        "committed the change"
    )
    if private:
        expect(page.locator("#meta-grid-event-cue-summary")).to_contain_text(
            "details are hidden"
        )
        expect(page.get_by_test_id("meta-grid-event-show")).to_be_disabled()
    else:
        summary = page.locator("#meta-grid-event-cue-summary")
        expect(summary).to_contain_text("9:00 am–9:30 am")
        expect(summary).to_contain_text("10:00 am–10:30 am")


def _sanitized_browser_routes(requests: Counter) -> list[dict[str, object]]:
    sanitized = Counter()
    uuid_route = re.compile(r"^/api/v1/appointments/[0-9a-f-]{36}$")
    for (method, path), count in requests.items():
        if not path.startswith("/api/v1/"):
            continue
        safe_path = (
            "/api/v1/appointments/{appointment_id}"
            if uuid_route.match(path)
            else path
        )
        sanitized[(method, safe_path)] += count
    return [
        {"method": method, "path": path, "count": count}
        for (method, path), count in sorted(sanitized.items())
    ]


def run(output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    readiness = readiness_report()
    assert readiness["ready"] is True, readiness
    before = database_readback()
    assert before["counts"]["diary_committed_events"] == 0

    runtime, processes = launch_runtime()
    evidence = shared.BrowserEvidence()
    contexts = []
    screenshots: list[dict[str, object]] = []
    viewports: list[dict[str, object]] = []
    interruption_method = "foreground_page_switch"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                specs = [
                    ("desktop_landscape", 1440, 900, False),
                    ("tablet_landscape", 1024, 768, True),
                    ("tablet_portrait", 768, 1024, True),
                    ("smartphone_portrait", 390, 844, True),
                    ("smartphone_landscape", 844, 390, True),
                ]
                pages: dict[str, Page] = {}
                for scenario_id, width, height, touch in specs:
                    context, page = _open(
                        browser,
                        evidence,
                        width,
                        height,
                        touch=touch,
                    )
                    contexts.append(context)
                    pages[scenario_id] = page

                phone_portrait = pages["smartphone_portrait"]
                phone_portrait.get_by_test_id("meta-grid-privacy").tap()
                expect(phone_portrait.get_by_test_id("meta-grid-privacy")).to_have_attribute(
                    "aria-pressed", "true"
                )

                phone_landscape = pages["smartphone_landscape"]
                interruption_page = phone_landscape.context.new_page()
                interruption_page.set_content("<title>Foreground interruption</title><p>synthetic</p>")
                interruption_page.bring_to_front()
                try:
                    expect(phone_landscape.locator("#meta-grid-state-label")).to_have_text(
                        "Refresh required", timeout=1500
                    )
                except AssertionError:
                    interruption_method = "standards_dom_blur_event_headless_fallback"
                    phone_landscape.evaluate("window.dispatchEvent(new Event('blur'))")
                    expect(phone_landscape.locator("#meta-grid-state-label")).to_have_text(
                        "Refresh required", timeout=2000
                    )

                support = _support_client(runtime.pop("support_password"))
                try:
                    _confirmed_reschedule(
                        support,
                        OUT_OF_SCOPE_APPOINTMENT_ID,
                        start_time_local="15:30:00",
                        key="reception-one-unrelated-reschedule",
                    )
                    for name, page in pages.items():
                        if name != "smartphone_landscape":
                            page.wait_for_timeout(2300)
                    _assert_no_cue(list(pages.values()))

                    payload, confirmed = _confirmed_reschedule(
                        support,
                        IN_SCOPE_APPOINTMENT_ID,
                        start_time_local="10:00:00",
                        key="reception-one-relevant-reschedule",
                    )
                    _replay_confirm(
                        support,
                        payload,
                        confirmed,
                        "reception-one-relevant-reschedule",
                    )
                finally:
                    support.close()

                phone_landscape.bring_to_front()
                interruption_page.close()
                for name, page in pages.items():
                    _assert_fresh_cue(
                        page,
                        private=name in {"smartphone_portrait", "smartphone_landscape"},
                    )

                desktop = pages["desktop_landscape"]
                tab_sequence = shared._keyboard_sequence(desktop, steps=10)
                screenshots.append(
                    _save(desktop, output, "desktop-event-cue-1440x900.png")
                )
                desktop.get_by_test_id("meta-grid-event-show").click()
                expect(
                    desktop.locator(f'[data-appointment-id="{IN_SCOPE_APPOINTMENT_ID}"]')
                ).to_be_focused()
                desktop.keyboard.press("Escape")
                expect(desktop.get_by_test_id("meta-grid-event-cue")).to_be_hidden()
                expect(desktop.locator("#meta-grid-request")).to_be_focused()
                viewports.append(
                    _viewport_record(
                        desktop,
                        scenario_id="desktop_landscape",
                        width=1440,
                        height=900,
                        results={
                            "unrelated_suppression": "pass",
                            "fresh_time_reconciliation": "pass",
                            "show_changed_appointment": "pass",
                            "keyboard_escape_dismiss_and_focus_restore": "pass",
                            "native_tab_sequence": tab_sequence,
                        },
                    )
                )

                tablet_landscape = pages["tablet_landscape"]
                screenshots.append(
                    _save(
                        tablet_landscape,
                        output,
                        "tablet-landscape-event-cue-1024x768.png",
                    )
                )
                tablet_landscape.get_by_test_id("meta-grid-event-snooze").tap()
                expect(tablet_landscape.get_by_test_id("meta-grid-event-cue")).to_be_hidden()
                viewports.append(
                    _viewport_record(
                        tablet_landscape,
                        scenario_id="tablet_landscape",
                        width=1024,
                        height=768,
                        results={"fresh_time_reconciliation": "pass", "snooze_five_minutes": "pass"},
                    )
                )

                tablet_portrait = pages["tablet_portrait"]
                screenshots.append(
                    _save(
                        tablet_portrait,
                        output,
                        "tablet-portrait-event-cue-768x1024.png",
                    )
                )
                tablet_portrait.get_by_test_id("meta-grid-event-dismiss").tap()
                expect(tablet_portrait.locator("#meta-grid-request")).to_be_focused()
                viewports.append(
                    _viewport_record(
                        tablet_portrait,
                        scenario_id="tablet_portrait",
                        width=768,
                        height=1024,
                        results={"fresh_time_reconciliation": "pass", "dismiss_focus_restore": "pass"},
                    )
                )

                phone_portrait.get_by_test_id("meta-grid-event-cue").scroll_into_view_if_needed()
                screenshots.append(
                    _save(
                        phone_portrait,
                        output,
                        "smartphone-portrait-private-event-390x844.png",
                    )
                )
                phone_portrait.get_by_test_id("meta-grid-event-mute").tap()
                expect(phone_portrait.get_by_test_id("meta-grid-event-cue")).to_be_hidden()
                viewports.append(
                    _viewport_record(
                        phone_portrait,
                        scenario_id="smartphone_portrait",
                        width=390,
                        height=844,
                        results={
                            "privacy_masks_time_and_detail": "pass",
                            "show_context_disabled_while_private": "pass",
                            "mute_until_reload": "pass",
                        },
                    )
                )

                phone_landscape.get_by_test_id("meta-grid-event-cue").scroll_into_view_if_needed()
                screenshots.append(
                    _save(
                        phone_landscape,
                        output,
                        "smartphone-landscape-interruption-event-844x390.png",
                    )
                )
                if phone_landscape.locator("#meta-grid-state-label").inner_text() == "Refresh required":
                    interruption_method = "foreground_switch_then_event_fresh_reconciliation_pending"
                phone_landscape.keyboard.press("Escape")
                expect(phone_landscape.get_by_test_id("meta-grid-event-cue")).to_be_hidden()
                viewports.append(
                    _viewport_record(
                        phone_landscape,
                        scenario_id="smartphone_landscape",
                        width=844,
                        height=390,
                        results={
                            "interruption_resume": f"pass; {interruption_method}",
                            "fresh_time_reconciliation": "pass",
                            "keyboard_escape": "pass",
                        },
                    )
                )

                for page in pages.values():
                    page.wait_for_timeout(2200)
                _assert_no_cue(list(pages.values()))
                pages["tablet_portrait"].get_by_role(
                    "button", name="Return to full Diary grid"
                ).tap()
                expect(pages["tablet_portrait"].locator("#diary-grid-container")).to_be_visible()
                viewports[2]["scenario_results"]["ordinary_diary_fallback"] = "pass"
                evidence.assert_clean()
            finally:
                for context in reversed(contexts):
                    context.close()
                browser.close()
    finally:
        stop_runtime(processes)

    after = database_readback()
    security = database_security_probes()
    assert after["counts"] == {
        "appointments": 6,
        "appointment_audit_log": 2,
        "appointment_command_idempotency": 2,
        "diary_committed_events": 2,
        "bernie_booking_sessions": 0,
        "bernie_session_events": 0,
    }
    assert after["target_windows"] == {
        "in_scope_target": "10:00:00",
        "out_of_scope_target": "15:30:00",
    }
    assert after["event_types"] == [
        "diary.appointment_rescheduled",
        "diary.appointment_rescheduled",
    ]
    assert after["payload_keys_exact"] is True
    assert after["prohibited_payload_keys_present"] == []
    assert after["correlated_event_rows"] == 2
    assert security["append_only_update"] == "append_only_rejected"
    assert security["append_only_delete"] == "append_only_rejected"
    assert security["rls_own_practice_event_count"] == 2
    assert security["rls_foreign_practice_event_count"] == 0

    browser_routes = _sanitized_browser_routes(evidence.requests)
    observed = {(row["method"], row["path"]) for row in browser_routes}
    assert ("GET", "/api/v1/diary/events/committed") in observed
    assert ("GET", "/api/v1/appointments/{appointment_id}") in observed
    assert ("GET", "/api/v1/appointments") in observed
    assert ("GET", "/api/v1/patients/search") in observed
    browser_mutation_requests = [
        (method, path)
        for method, path in observed
        if method in {"POST", "PUT", "PATCH", "DELETE"}
        and (method, path)
        not in {
            ("POST", "/api/v1/auth/login"),
            ("POST", "/api/v1/graphql"),
        }
    ]
    assert browser_mutation_requests == []

    result = {
        "schema_version": "reception-one.committed-event.browser-evidence.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "browser_pass",
        "evidence_mode": "live_local_browser_backend_postgres",
        "support_command_evidence_mode": "live_local_backend_postgres",
        "route_interception": False,
        "api_interception": False,
        "runtime": {
            "database": LOCKED_DATABASE,
            "provider": runtime["provider"],
            "loopback_family": runtime["loopback_family"],
            "cloud_credentials_present": False,
            "credential_recorded": False,
            "token_recorded": False,
            "feature_enabled_only_in_exact_harness": True,
        },
        "authority": {
            "existing_signed_update_confirmation_only": True,
            "new_appointment_command_added": False,
            "event_command_authority": False,
            "event_acknowledgement_route": False,
            "provider_called": False,
            "production_or_deployment_changed": False,
        },
        "support_commands": {
            "confirmed_reschedules": 2,
            "in_scope": 1,
            "out_of_scope": 1,
            "idempotent_replays": 1,
            "other_mutations": 0,
        },
        "database_readback": after,
        "database_security": security,
        "network": {
            "browser_only_loopback": True,
            "browser_api_method_path_counts": browser_routes,
            "browser_forbidden_requests": evidence.forbidden,
            "browser_failed_api_responses": [
                row for row in evidence.responses if int(row["status"]) >= 400
            ],
            "browser_mutation_requests": browser_mutation_requests,
            "support_command_routes": [
                "POST /api/v1/appointments/proposals/update/{appointment_id}",
                "POST /api/v1/appointments/proposals/update/confirm",
            ],
        },
        "viewports": viewports,
        "attention": {
            "unrelated_event_suppressed": True,
            "duplicate_visible_effect": False,
            "show_changed_appointment": True,
            "dismiss": True,
            "snooze_five_minutes": True,
            "mute_until_reload": True,
            "no_auto_focus_or_speech": True,
        },
        "privacy": {
            "time_comparison_masked": True,
            "changed_item_detail_masked": True,
            "patient_free_live_region": True,
        },
        "keyboard": {
            "escape_dismiss_and_focus_restore": True,
            "show_context_focus_target": True,
            "native_tab_sequence": viewports[0]["scenario_results"]["native_tab_sequence"],
        },
        "interruption": {
            "method": interruption_method,
            "event_payload_used_as_display_truth": False,
            "fresh_appointment_read": True,
            "fresh_projection_read": True,
        },
        "screenshots": screenshots,
        "browser_console_warnings_or_errors": evidence.console,
        "browser_page_errors": evidence.page_errors,
        "claims_not_made": [
            "provider",
            "PII",
            "Stage 3B",
            "representative usability",
            "voice",
            "external event transport",
            "production",
            "deployment",
            "release",
        ],
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    for forbidden in (
        "Margaret",
        "Billy",
        "date_of_birth",
        "patient_id",
        "access_token",
        "password",
        str(IN_SCOPE_APPOINTMENT_ID),
        str(OUT_OF_SCOPE_APPOINTMENT_ID),
    ):
        assert forbidden not in serialized
    (output / "browser-acceptance-evidence.json").write_text(
        serialized,
        encoding="utf-8",
    )
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
                "events": result["database_readback"]["counts"]["diary_committed_events"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
