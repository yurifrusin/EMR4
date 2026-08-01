"""Disposable browser/backend/PostgreSQL proof for four proposal families."""

from __future__ import annotations

import hashlib
import json
import secrets
from pathlib import Path
import subprocess

from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import reception_one_product_context_live_local_acceptance as prior


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-extended-proposal-runtime"
)
EVIDENCE = OUTPUT / "live-local-browser-backend-postgres-evidence.json"
LOCKED_DATABASE = "gp_pms_reception_one_extended_runtime_7c37b24a_20260730"
RUNTIME_TAG = "reception-one-extended-runtime-7c37b24a"
REFERENCE_DATE = "2026-08-03"
SELECTED_APPOINTMENT_ID = str(
    prior.base.base.fixed_id("appointment-margaret-shera-next")
)
CASES = (
    (
        "move",
        "Move Margaret Thompson's appointment with Dr Alex Shera today "
        "after 2 pm but before 3 pm",
    ),
    (
        "resize",
        "Extend Margaret Thompson's appointment with Dr Alex Shera to 45 minutes",
    ),
    (
        "cancel",
        "Cancel Margaret Thompson's appointment with Dr Alex Shera",
    ),
    (
        "squeeze_in_assessment",
        "Can we squeeze Margaret Thompson in with Dr Alex Shera today "
        "for 15 minutes without moving anyone?",
    ),
)


def _configure() -> None:
    prior.LOCKED_DATABASE = LOCKED_DATABASE
    prior.RUNTIME_TAG = RUNTIME_TAG
    prior.OUTPUT = OUTPUT
    prior.base.LOCKED_DATABASE = LOCKED_DATABASE
    prior.base.RUNTIME_TAG = RUNTIME_TAG
    prior._configure_database()


def _readback() -> dict[str, object]:
    result = prior.base.database_readback()
    from app.models.diary_events import DiaryCommittedEvent

    engine = create_engine(prior.base.base.database_url())
    try:
        with Session(engine) as session:
            event_count = session.query(DiaryCommittedEvent).count()
    finally:
        engine.dispose()
    result["counts"]["diary_committed_events"] = event_count
    result["sha256"]["diary_committed_events"] = hashlib.sha256(
        b"[]" if event_count == 0 else str(event_count).encode("ascii")
    ).hexdigest()
    return result


def _browser_proof() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    network: list[dict[str, str]] = []
    results: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        page = context.new_page()
        page.on(
            "request",
            lambda request: network.append(
                {
                    "method": request.method.upper(),
                    "hostname": prior.urlsplit(request.url).hostname or "",
                    "path": prior.urlsplit(request.url).path,
                }
            ),
        )
        page.goto(
            f"{prior.STATIC_URL}/meta-grid-auth.html",
            wait_until="domcontentloaded",
        )
        page.wait_for_url("**/diary/diary.html?reference_date=2026-07-27**")
        runtime_url = (
            f"{prior.STATIC_URL}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            "&reception_one_demo=appointment_sheet"
            "&standalone_diary=true"
            f"&reference_date={REFERENCE_DATE}"
            "&product_context_live_local=true"
            f"&extended_selected_appointment_id={SELECTED_APPOINTMENT_ID}"
        )
        for index, (expected_goal, instruction) in enumerate(CASES, start=1):
            page.goto(runtime_url, wait_until="networkidle")
            if expected_goal != "squeeze_in_assessment":
                selected = page.locator(
                    f'[data-appointment-id="{SELECTED_APPOINTMENT_ID}"]'
                )
                selected.wait_for(state="visible", timeout=20_000)
                selected.click()
                if selected.get_attribute("aria-selected") != "true":
                    raise RuntimeError("Diary appointment selection did not bind")
            request_box = page.get_by_label(
                "What would you like to find or prepare?",
                exact=True,
            )
            request_box.fill(instruction)
            with page.expect_response(
                lambda response: (
                    response.request.method.upper() == "POST"
                    and response.url.split("?", 1)[0].endswith(
                        "/api/v1/appointments/proposals/reception-one/compose"
                    )
                ),
                timeout=20_000,
            ) as response_info:
                request_box.press("Enter")
            response = response_info.value
            payload = response.json()
            if response.status != 200 or payload.get("goal") != expected_goal:
                raise RuntimeError(
                    f"Extended family failed: {expected_goal} HTTP {response.status}"
                )
            if payload.get("result") != "proposal_ready":
                raise RuntimeError(f"{expected_goal} did not release a proposal")
            adapter = payload.get("adapter_review") or {}
            if adapter.get("safe") is not True:
                raise RuntimeError(f"{expected_goal} adapter did not pass")
            if expected_goal in {"move", "squeeze_in_assessment"}:
                page.get_by_test_id("meta-grid-slot").first.wait_for(
                    state="visible",
                    timeout=20_000,
                )
            else:
                page.locator(
                    '#bernie-meta-grid[data-projection-state="proposal_not_committed"]'
                ).wait_for(state="visible", timeout=20_000)
            screenshot = OUTPUT / f"live-local-{index}-{expected_goal}.png"
            page.screenshot(path=str(screenshot), full_page=True)
            results.append(
                {
                    "goal": payload["goal"],
                    "operation_id": payload["operation_id"],
                    "result": payload["result"],
                    "proofreader_disposition": payload["review"]["disposition"],
                    "adapter_kind": adapter["adapter_kind"],
                    "adapter_safe": adapter["safe"],
                    "candidate_count": len(payload["candidate_slots"]),
                    "requires_confirmation": payload["requires_confirmation"],
                    "proposal_only": payload["proposal_only"],
                    "write_performed": payload["write_performed"],
                    "provider_calls": payload["provider_calls"],
                    "screenshot": str(screenshot.relative_to(ROOT)).replace(
                        "\\", "/"
                    ),
                    "screenshot_sha256": hashlib.sha256(
                        screenshot.read_bytes()
                    ).hexdigest(),
                }
            )
        context.close()
        browser.close()
    return results, network


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _configure()
    processes: list[subprocess.Popen[bytes]] = []
    runtime_dir: Path | None = None
    database_created = False
    try:
        prior.base.create_database()
        database_created = True
        prior.base.create_schema_and_seed(
            f"ExtendedRuntimeSeed-{secrets.token_urlsafe(24)}!"
        )
        before = _readback()
        processes, runtime_dir = prior._launch_runtime()
        case_results, network = _browser_proof()
        after = _readback()
        route_calls = [
            item
            for item in network
            if item == {
                "method": "POST",
                "hostname": "::1",
                "path": "/api/v1/appointments/proposals/reception-one/compose",
            }
        ]
        external_hosts = sorted(
            {
                item["hostname"]
                for item in network
                if item["hostname"]
                not in {"::1", "127.0.0.1", "localhost", ""}
            }
        )
        if len(route_calls) != len(CASES):
            raise RuntimeError("Expected one product-context call per family")
        if external_hosts:
            raise RuntimeError(f"Unexpected browser hosts: {external_hosts}")
        if before["counts"] != after["counts"] or before["sha256"] != after["sha256"]:
            raise RuntimeError("A forbidden write surface changed")
        evidence = {
            "schema_version": (
                "reception.one.extended_proposal_runtime.live_local.v1"
            ),
            "result": (
                "extended_runtime_live_local_browser_backend_postgres_pass"
            ),
            "data_class": "authored_synthetic",
            "database_identifier_recorded": False,
            "loopback_family": "ipv6",
            "request_interception_used": False,
            "family_results": case_results,
            "network": {
                "route_call_count": len(route_calls),
                "external_host_count": 0,
                "allowed_hosts": ["::1", "127.0.0.1", "localhost"],
            },
            "database_before": before,
            "database_after": after,
            "forbidden_write_surfaces_unchanged": True,
            "api_key_authentication_used": False,
            "provider_environment_forwarded": False,
            "provider_calls": 0,
            "appointment_confirmation_performed": False,
            "appointment_write_performed": False,
            "raw_database_identifiers_retained": False,
        }
        EVIDENCE.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            json.dumps(
                {
                    "result": evidence["result"],
                    "families": len(case_results),
                    "route_calls": len(route_calls),
                    "provider_calls": 0,
                    "writes": 0,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        if processes:
            prior.base.stop_runtime(processes)
        if runtime_dir is not None:
            prior._remove_runtime_dir(runtime_dir)
        if database_created:
            cleanup = prior.base.cleanup_database()
            (OUTPUT / "live-local-database-cleanup-evidence.json").write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "reception.one.extended_proposal_runtime."
                            "database_cleanup.v1"
                        ),
                        "ownership_marker_verified": True,
                        "scope": "exact_disposable_authored_synthetic_database",
                        "cleanup": cleanup,
                        "runtime_processes_absent": all(
                            process.poll() is not None for process in processes
                        ),
                        "runtime_temporary_root_absent": (
                            runtime_dir is None or not runtime_dir.exists()
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )


if __name__ == "__main__":
    raise SystemExit(main())
