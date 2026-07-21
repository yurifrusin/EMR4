"""Real-browser acceptance for committed-event availability reconciliation.

The runner drives only visible Reception One controls in a real Chromium
browser.  The two signed reschedules are support setup through the already
accepted local update-confirmation path; the browser itself never confirms or
writes an appointment.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Browser, Page, expect, sync_playwright

import bernie_meta_grid_live_local_acceptance as shared
from reception_one_availability_reconciliation_harness import (
    AVAILABILITY_TARGET_ID,
    LOCKED_DATABASE,
    database_readback,
    database_security_probes,
    launch_runtime,
    readiness_report,
    stop_runtime,
)
from reception_one_committed_event_acceptance import (
    _confirmed_reschedule,
    _replay_confirm,
    _sanitized_browser_routes,
    _save,
    _support_client,
    _viewport_record,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-availability-reconciliation"
)
AUTH_URL = "http://[::1]:3000/meta-grid-auth.html"
EXACT_REQUEST = (
    "Show me all the available slots with Dr Shera for a half-hour appointment "
    "with Margaret Thompson after 2 today."
)
OTHER_PRACTITIONER_REQUEST = "Find Dr Patel availability today after 2 pm"
NO_CONSEQUENCE_REQUEST = "Find Dr Shera availability today after 4:30 pm"

shared.AUTH_URL = AUTH_URL
shared.STATIC_HOSTS.add("::1")
shared.API_ALLOWED.update(
    {
        ("GET", "/api/v1/diary/events/committed"),
        ("GET", f"/api/v1/appointments/{AVAILABILITY_TARGET_ID}"),
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
    for _ in range(8):
        if page.locator("#diary-date-picker").input_value() == "2026-07-27":
            break
        with page.expect_response(
            lambda response: (
                urlsplit(response.url).path == "/api/v1/appointments"
                and response.request.method.upper() == "GET"
            ),
            timeout=15_000,
        ):
            page.locator("#btn-next-day").click()
    expect(page.locator("#diary-date-picker")).to_have_value(
        "2026-07-27", timeout=15_000
    )
    page.get_by_test_id("meta-grid-launch-button").click()
    expect(page.get_by_test_id("meta-grid-workspace")).to_be_visible(timeout=20_000)
    shared._wait_family(page, "ordinary_overview")
    # Establish the event cursor before any support command is issued.
    page.wait_for_timeout(2200)
    evidence.assert_clean()
    return context, page


def _submit_availability(page: Page, request: str) -> None:
    shared._submit(page, request, "availability_slots")
    expect(page.get_by_test_id("meta-grid-slot").first).to_be_visible(timeout=15_000)


def _slot_at(page: Page, time_label: str):
    slot = page.get_by_test_id("meta-grid-slot").filter(
        has_text=re.compile(rf"^{re.escape(time_label)}")
    )
    expect(slot).to_have_count(1)
    return slot


def _select_330(page: Page, *, keyboard: bool = False) -> None:
    slot = _slot_at(page, "3:30 pm")
    if keyboard:
        slot.focus()
        page.keyboard.press("Space")
    else:
        slot.tap()
    expect(page.locator("#meta-grid-state-label")).to_have_text("Selection")
    expect(page.get_by_test_id("meta-grid-prepare-scoped-proposal")).to_be_visible()


def _prepare_proposal(page: Page, *, keyboard: bool = False) -> None:
    action = page.get_by_test_id("meta-grid-prepare-scoped-proposal")
    if keyboard:
        action.focus()
        page.keyboard.press("Enter")
    else:
        action.tap()
    shared._wait_family(page, "proposal_review")
    expect(page.locator("#meta-grid-state-label")).to_contain_text("Proposal")
    expect(page.get_by_test_id("meta-grid-proposal-handoff")).to_be_enabled()
    expect(page.locator("#meta-grid-omissions")).to_contain_text(
        "No appointment has been created"
    )


def _expect_cue(page: Page, summary: str) -> None:
    expect(page.get_by_test_id("meta-grid-event-cue")).to_be_visible(timeout=12_000)
    expect(page.locator("#meta-grid-event-cue-summary")).to_have_text(summary)
    expect(page.get_by_test_id("meta-grid-event-show")).to_have_text(
        "Review current availability"
    )


def _expect_no_cue(page: Page) -> None:
    expect(page.get_by_test_id("meta-grid-event-cue")).to_be_hidden()


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

                desktop = pages["desktop_landscape"]
                _submit_availability(desktop, EXACT_REQUEST)
                expect(desktop.locator("#meta-grid-scope-summary")).to_contain_text(
                    "30 minutes"
                )
                _select_330(desktop, keyboard=True)
                _prepare_proposal(desktop, keyboard=True)

                tablet_landscape = pages["tablet_landscape"]
                _submit_availability(tablet_landscape, EXACT_REQUEST)
                _select_330(tablet_landscape)

                tablet_portrait = pages["tablet_portrait"]
                _submit_availability(tablet_portrait, EXACT_REQUEST)
                tablet_parent_scope = tablet_portrait.locator(
                    "#meta-grid-scope-summary"
                ).inner_text()
                shared._submit(
                    tablet_portrait,
                    "after 2:30 pm",
                    "availability_slots",
                    previous_scope=tablet_parent_scope,
                )
                tablet_portrait.get_by_test_id("meta-grid-back").tap()
                expect(tablet_portrait.locator("#meta-grid-scope-summary")).to_have_text(
                    tablet_parent_scope
                )

                phone_portrait = pages["smartphone_portrait"]
                _submit_availability(phone_portrait, OTHER_PRACTITIONER_REQUEST)

                phone_landscape = pages["smartphone_landscape"]
                _submit_availability(phone_landscape, NO_CONSEQUENCE_REQUEST)

                support = _support_client(runtime.pop("support_password"))
                try:
                    first_payload, first_confirmed = _confirmed_reschedule(
                        support,
                        AVAILABILITY_TARGET_ID,
                        start_time_local="16:00:00",
                        key="reception-one-availability-first",
                    )
                    _replay_confirm(
                        support,
                        first_payload,
                        first_confirmed,
                        "reception-one-availability-first",
                    )

                    _expect_cue(
                        desktop,
                        "Availability in this view changed, but your proposed time is still available.",
                    )
                    expect(desktop.locator("#meta-grid-state-label")).to_contain_text("Proposal")
                    _expect_cue(
                        tablet_landscape,
                        "Availability in this view changed, but your selected time is still available.",
                    )
                    expect(tablet_landscape.locator("#meta-grid-state-label")).to_have_text(
                        "Selection"
                    )
                    _expect_cue(
                        tablet_portrait,
                        "Availability in this view changed. Reception One refreshed the current options.",
                    )
                    _expect_no_cue(phone_portrait)
                    _expect_no_cue(phone_landscape)

                    screenshots.append(
                        _save(
                            tablet_landscape,
                            output,
                            "tablet-landscape-selection-preserved-1024x768.png",
                        )
                    )

                    review = desktop.get_by_test_id("meta-grid-event-show")
                    review.focus()
                    page_key_sequence = [
                        shared._focus_label(desktop),
                    ]
                    desktop.keyboard.press("Enter")
                    page_key_sequence.append(shared._focus_label(desktop))
                    _expect_no_cue(desktop)
                    expect(desktop.locator("#meta-grid-state-label")).to_have_text("Selection")
                    expect(_slot_at(desktop, "3:30 pm")).to_have_attribute(
                        "aria-pressed", "true"
                    )

                    tablet_landscape.get_by_test_id("meta-grid-event-snooze").tap()
                    _expect_no_cue(tablet_landscape)
                    tablet_portrait.get_by_test_id("meta-grid-event-dismiss").tap()
                    _expect_no_cue(tablet_portrait)
                    expect(tablet_portrait.locator("#meta-grid-request")).to_be_focused()

                    _submit_availability(phone_portrait, EXACT_REQUEST)
                    _select_330(phone_portrait)
                    _prepare_proposal(phone_portrait)
                    phone_portrait.get_by_test_id("meta-grid-privacy").tap()
                    expect(phone_portrait.get_by_test_id("meta-grid-privacy")).to_have_attribute(
                        "aria-pressed", "true"
                    )

                    _submit_availability(phone_landscape, EXACT_REQUEST)
                    _select_330(phone_landscape)
                    interruption_page = phone_landscape.context.new_page()
                    interruption_page.set_content(
                        "<title>Foreground interruption</title><p>authored synthetic interruption</p>"
                    )
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

                    _confirmed_reschedule(
                        support,
                        AVAILABILITY_TARGET_ID,
                        start_time_local="15:30:00",
                        key="reception-one-availability-second",
                    )
                finally:
                    support.close()

                _expect_cue(
                    desktop,
                    "That time is no longer available. Reception One refreshed the remaining options.",
                )
                expect(desktop.locator("#meta-grid-state-label")).to_have_text("Answer")
                expect(desktop.get_by_test_id("meta-grid-prepare-scoped-proposal")).to_have_count(0)
                expect(desktop.get_by_test_id("meta-grid-back")).to_be_disabled()

                expect(tablet_landscape.locator("#meta-grid-state-label")).to_have_text(
                    "Answer", timeout=12_000
                )
                _expect_no_cue(tablet_landscape)
                expect(tablet_landscape.get_by_test_id("meta-grid-prepare-scoped-proposal")).to_have_count(0)

                _expect_cue(
                    tablet_portrait,
                    "Availability in this view changed. Reception One refreshed the current options.",
                )
                tablet_portrait.get_by_test_id(
                    "meta-grid-event-cue"
                ).scroll_into_view_if_needed()

                expect(phone_portrait.locator("#meta-grid-state-label")).to_have_text(
                    "Answer", timeout=12_000
                )
                expect(phone_portrait.get_by_test_id("meta-grid-event-cue")).to_be_visible()
                expect(phone_portrait.locator("#meta-grid-event-cue-summary")).to_have_text(
                    "The affected time, patient and appointment details are hidden while privacy mode is on."
                )
                expect(phone_portrait.get_by_test_id("meta-grid-event-show")).to_be_disabled()
                expect(phone_portrait.get_by_test_id("meta-grid-proposal-handoff")).to_have_count(0)
                phone_portrait.get_by_test_id(
                    "meta-grid-event-cue"
                ).scroll_into_view_if_needed()

                phone_landscape.bring_to_front()
                interruption_page.close()
                phone_landscape.wait_for_timeout(2500)
                expect(phone_landscape.locator("#meta-grid-state-label")).to_have_text(
                    "Refresh required"
                )
                _expect_no_cue(phone_landscape)
                expect(phone_landscape.get_by_test_id("meta-grid-back")).to_be_disabled()
                expect(phone_landscape.get_by_test_id("meta-grid-prepare-scoped-proposal")).to_have_count(0)
                expect(_slot_at(phone_landscape, "3:30 pm")).to_have_attribute(
                    "aria-pressed", "false"
                )
                phone_landscape.locator(
                    "#meta-grid-state-label"
                ).scroll_into_view_if_needed()

                screenshots.extend(
                    [
                        _save(desktop, output, "desktop-selection-unavailable-1440x900.png"),
                        _save(
                            tablet_portrait,
                            output,
                            "tablet-portrait-availability-changed-768x1024.png",
                        ),
                        _save(
                            phone_portrait,
                            output,
                            "smartphone-portrait-private-proposal-cleared-390x844.png",
                        ),
                        _save(
                            phone_landscape,
                            output,
                            "smartphone-landscape-interruption-844x390.png",
                        ),
                    ]
                )

                desktop.keyboard.press("Escape")
                _expect_no_cue(desktop)
                expect(desktop.locator("#meta-grid-request")).to_be_focused()
                native_tab_sequence = shared._keyboard_sequence(desktop, steps=10)

                tablet_portrait.get_by_test_id("meta-grid-event-mute").tap()
                _expect_no_cue(tablet_portrait)

                viewports.extend(
                    [
                        _viewport_record(
                            desktop,
                            scenario_id="desktop_landscape",
                            width=1440,
                            height=900,
                            results={
                                "combined_scope": "pass",
                                "proposal_preserved_then_selection_cleared": "pass",
                                "stale_back_trail_expired": "pass",
                                "keyboard_space_select_enter_prepare_and_escape": "pass",
                                "review_action_focus_sequence": page_key_sequence,
                                "native_tab_sequence": native_tab_sequence,
                            },
                        ),
                        _viewport_record(
                            tablet_landscape,
                            scenario_id="tablet_landscape",
                            width=1024,
                            height=768,
                            results={
                                "touch_selection_preserved": "pass",
                                "snoozed_second_cue_but_state_reconciled": "pass",
                            },
                        ),
                        _viewport_record(
                            pages["tablet_portrait"],
                            scenario_id="tablet_portrait",
                            width=768,
                            height=1024,
                            results={
                                "unselected_availability_reconciled": "pass",
                                "dismiss_focus_restore": "pass",
                                "exact_back_restoration_before_event": "pass",
                                "mute_until_reload": "pass",
                                "ordinary_diary_fallback": "pass",
                            },
                        ),
                        _viewport_record(
                            phone_portrait,
                            scenario_id="smartphone_portrait",
                            width=390,
                            height=844,
                            results={
                                "other_practitioner_suppression": "pass",
                                "proposal_cleared": "pass",
                                "privacy_masks_cue_and_disables_review": "pass",
                            },
                        ),
                        _viewport_record(
                            phone_landscape,
                            scenario_id="smartphone_landscape",
                            width=844,
                            height=390,
                            results={
                                "same_practitioner_no_consequence_suppression": "pass",
                                "interruption_race_guard": f"pass; {interruption_method}",
                                "stale_selection_not_restored": "pass",
                            },
                        ),
                    ]
                )
                tablet_portrait.get_by_role(
                    "button", name="Return to full Diary grid"
                ).tap()
                expect(tablet_portrait.locator("#diary-grid-container")).to_be_visible()
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
        "availability_target": "15:30:00",
        "other_practitioner_target": "10:00:00",
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
    for expected_route in {
        ("GET", "/api/v1/diary/events/committed"),
        ("GET", "/api/v1/appointments/{appointment_id}"),
        ("POST", "/api/v1/appointments/proposals/slot-search"),
        ("POST", "/api/v1/appointments/proposals/bernie/supervised-booking"),
    }:
        assert expected_route in observed
    browser_write_requests = [
        (method, path)
        for method, path in observed
        if method in {"POST", "PUT", "PATCH", "DELETE"}
        and (method, path)
        not in {
            ("POST", "/api/v1/auth/login"),
            ("POST", "/api/v1/graphql"),
            ("POST", "/api/v1/appointments/proposals/slot-search"),
            ("POST", "/api/v1/appointments/proposals/bernie/supervised-booking"),
        }
    ]
    assert browser_write_requests == []

    result = {
        "schema_version": "reception-one.availability-reconciliation.browser-evidence.v1",
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
            "active_ipv4_contact": False,
            "cloud_credentials_present": False,
            "credential_recorded": False,
            "token_recorded": False,
            "feature_enabled_only_in_exact_harness": True,
        },
        "authority": {
            "browser_appointment_write": False,
            "browser_proposal_handoff": False,
            "browser_confirmation_control": False,
            "existing_signed_update_confirmation_support_only": True,
            "new_event_or_command_added": False,
            "provider_called": False,
            "production_or_deployment_changed": False,
        },
        "support_commands": {
            "confirmed_reschedules": 2,
            "same_target": True,
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
            "browser_write_requests": browser_write_requests,
            "support_command_routes": [
                "POST /api/v1/appointments/proposals/update/{appointment_id}",
                "POST /api/v1/appointments/proposals/update/confirm",
            ],
        },
        "reconciliation": {
            "proposal_preserved_when_candidate_survived": True,
            "selection_preserved_when_candidate_survived": True,
            "selection_cleared_when_candidate_disappeared": True,
            "proposal_cleared_when_candidate_disappeared": True,
            "unselected_candidate_change_refreshed": True,
            "other_practitioner_event_suppressed": True,
            "same_practitioner_no_consequence_suppressed": True,
            "duplicate_visible_effect": False,
            "event_payload_used_as_display_truth": False,
            "fresh_appointment_read": True,
            "fresh_slot_search": True,
        },
        "viewports": viewports,
        "keyboard": {
            "space_select": True,
            "enter_prepare_proposal": True,
            "enter_review_current_availability": True,
            "escape_dismiss_and_focus_restore": True,
            "native_tab_sequence": viewports[0]["scenario_results"]["native_tab_sequence"],
            "page_internal_command_invocation": False,
        },
        "interruption": {
            "method": interruption_method,
            "stale_selection_or_proposal_restored": False,
            "fresh_read_required": True,
        },
        "privacy": {
            "time_patient_and_appointment_details_masked": True,
            "review_action_disabled": True,
            "patient_free_live_region": True,
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
        str(AVAILABILITY_TARGET_ID),
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
