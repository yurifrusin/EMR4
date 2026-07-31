"""Provider-free live-local acceptance for Bureau planner UI wiring.

The harness drives a real browser through the ordinary Diary, FastAPI and one
exact disposable authored-synthetic PostgreSQL database. It performs one
deterministic proposal request and one isolated-planner gate-closed request.
No route interception, provider credential or provider call is permitted.
"""

from __future__ import annotations

import json
import secrets
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

import reception_one_product_context_live_local_acceptance as runtime


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-bureau-runtime-ui-wiring"
)
EVIDENCE = OUTPUT / "live-local-browser-backend-postgres-evidence.json"
DATABASE_CLEANUP = OUTPUT / "database-cleanup-evidence.json"
DESKTOP_SCREENSHOT = OUTPUT / "deterministic-admitted-desktop.png"
COMPACT_SCREENSHOT = OUTPUT / "deterministic-admitted-compact.png"
GATE_CLOSED_SCREENSHOT = OUTPUT / "isolated-gate-closed.png"
LOCKED_DATABASE = "gp_pms_reception_one_bureau_ui_8f03a9c2_20260730"
RUNTIME_TAG = "reception-one-bureau-ui-8f03a9c2"
REFERENCE_DATE = "2026-07-27"
INSTRUCTION = (
    "Make an appointment for Margaret Thompson with Dr Alex Shera "
    "today morning"
)


def _configure_runtime() -> None:
    runtime.LOCKED_DATABASE = LOCKED_DATABASE
    runtime.RUNTIME_TAG = RUNTIME_TAG
    runtime.OUTPUT = OUTPUT
    runtime.base.LOCKED_DATABASE = LOCKED_DATABASE
    runtime.base.RUNTIME_TAG = RUNTIME_TAG
    runtime._configure_database()


def _browser_proof() -> tuple[dict[str, object], list[dict[str, str]]]:
    network: list[dict[str, str]] = []
    submitted_modes: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        page = context.new_page()

        def record_request(request) -> None:
            path = urlsplit(request.url).path
            network.append(
                {
                    "method": request.method.upper(),
                    "hostname": urlsplit(request.url).hostname or "",
                    "path": path,
                }
            )
            if (
                request.method.upper() == "POST"
                and path
                == "/api/v1/appointments/proposals/reception-one/compose"
            ):
                body = request.post_data_json or {}
                submitted_modes.append(str(body.get("planner_mode", "")))

        page.on("request", record_request)
        page.goto(
            f"{runtime.STATIC_URL}/meta-grid-auth.html",
            wait_until="domcontentloaded",
        )
        page.wait_for_url("**/diary/diary.html?reference_date=2026-07-27**")

        ordinary_url = (
            f"{runtime.STATIC_URL}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            "&standalone_diary=true"
            f"&reference_date={REFERENCE_DATE}"
            "&product_context_live_local=true"
        )
        page.goto(ordinary_url, wait_until="networkidle")
        page.locator("#bernie-meta-grid:not(.hidden)").wait_for(
            state="visible"
        )
        ordinary_control_hidden = page.locator(
            "#meta-grid-planner-control"
        ).evaluate("node => node.classList.contains('hidden')")

        gated_url = f"{ordinary_url}&bureau_runtime_ui=true"
        page.goto(gated_url, wait_until="networkidle")
        planner = page.get_by_test_id("meta-grid-planner-mode")
        planner.wait_for(state="visible")
        default_mode = planner.input_value()
        request_box = page.get_by_label(
            "What would you like to find or prepare?",
            exact=True,
        )
        request_box.fill(INSTRUCTION)
        with page.expect_response(
            lambda response: (
                response.request.method.upper() == "POST"
                and response.url.split("?", 1)[0].endswith(
                    "/api/v1/appointments/proposals/reception-one/compose"
                )
            ),
            timeout=20_000,
        ) as deterministic_response_info:
            request_box.press("Enter")
        deterministic_response = deterministic_response_info.value
        deterministic_payload = deterministic_response.json()
        provenance = page.get_by_test_id("meta-grid-planner-provenance")
        provenance.wait_for(state="visible", timeout=20_000)
        desktop_provenance = provenance.inner_text()
        page.screenshot(path=str(DESKTOP_SCREENSHOT), full_page=True)

        page.set_viewport_size({"width": 640, "height": 820})
        provenance.wait_for(state="visible")
        compact_control_visible = planner.is_visible()
        page.screenshot(path=str(COMPACT_SCREENSHOT), full_page=True)

        page.set_viewport_size({"width": 1440, "height": 900})
        planner.select_option("isolated_vertex")
        request_box.fill(INSTRUCTION)
        with page.expect_response(
            lambda response: (
                response.request.method.upper() == "POST"
                and response.url.split("?", 1)[0].endswith(
                    "/api/v1/appointments/proposals/reception-one/compose"
                )
            ),
            timeout=20_000,
        ) as isolated_response_info:
            request_box.press("Enter")
        isolated_response = isolated_response_info.value
        page.get_by_role(
            "heading",
            name="I couldn’t prepare that view",
            exact=True,
        ).wait_for(state="visible", timeout=20_000)
        stale_provenance_visible = provenance.is_visible()
        page.screenshot(path=str(GATE_CLOSED_SCREENSHOT), full_page=True)

        result = {
            "ordinary_control_hidden": ordinary_control_hidden,
            "development_control_visible": planner.is_visible(),
            "default_mode": default_mode,
            "submitted_modes": submitted_modes,
            "deterministic": {
                "http_status": deterministic_response.status,
                "result": deterministic_payload["result"],
                "planner_mode": deterministic_payload["planner_mode"],
                "provider_calls": deterministic_payload["provider_calls"],
                "proofreader_disposition": deterministic_payload["review"][
                    "disposition"
                ],
                "requires_confirmation": deterministic_payload[
                    "requires_confirmation"
                ],
                "proposal_only": deterministic_payload["proposal_only"],
                "write_performed": deterministic_payload["write_performed"],
                "confirmation_performed": deterministic_payload[
                    "confirmation_performed"
                ],
                "model_database_access": deterministic_payload[
                    "model_database_access"
                ],
                "runtime_audit_ref": deterministic_payload[
                    "runtime_audit_ref"
                ],
                "rendered_provenance": desktop_provenance,
            },
            "compact_control_visible": compact_control_visible,
            "isolated_gate_closed": {
                "http_status": isolated_response.status,
                "stale_provenance_visible": stale_provenance_visible,
            },
        }
        context.close()
        browser.close()
    return result, network


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _configure_runtime()
    processes: list[subprocess.Popen[bytes]] = []
    runtime_dir: Path | None = None
    database_created = False
    try:
        runtime.base.create_database()
        database_created = True
        runtime.base.create_schema_and_seed(
            f"BureauUiSeed-{secrets.token_urlsafe(24)}!"
        )
        before = runtime.base.database_readback()
        processes, runtime_dir = runtime._launch_runtime()
        browser_result, network = _browser_proof()
        after = runtime.base.database_readback()

        route_calls = [
            item
            for item in network
            if (
                item["method"] == "POST"
                and item["path"]
                == "/api/v1/appointments/proposals/reception-one/compose"
            )
        ]
        external_hosts = sorted(
            {
                item["hostname"]
                for item in network
                if item["hostname"]
                not in {"::1", "127.0.0.1", "localhost", ""}
            }
        )
        deterministic = browser_result["deterministic"]
        gate_closed = browser_result["isolated_gate_closed"]
        checks = {
            "ordinary_control_hidden": (
                browser_result["ordinary_control_hidden"] is True
            ),
            "development_control_visible": (
                browser_result["development_control_visible"] is True
            ),
            "deterministic_default": (
                browser_result["default_mode"] == "deterministic"
            ),
            "closed_modes_submitted": browser_result["submitted_modes"]
            == ["deterministic", "isolated_vertex"],
            "deterministic_http_200": deterministic["http_status"] == 200,
            "deterministic_admitted": (
                deterministic["proofreader_disposition"] == "admit"
            ),
            "deterministic_zero_provider_calls": (
                deterministic["provider_calls"] == 0
            ),
            "proposal_only": (
                deterministic["requires_confirmation"] is True
                and deterministic["proposal_only"] is True
                and deterministic["write_performed"] is False
                and deterministic["confirmation_performed"] is False
                and deterministic["model_database_access"] is False
            ),
            "provenance_rendered": (
                "Standard planner" in deterministic["rendered_provenance"]
                and "Proofreader admitted"
                in deterministic["rendered_provenance"]
                and "0 provider calls"
                in deterministic["rendered_provenance"]
            ),
            "compact_control_visible": (
                browser_result["compact_control_visible"] is True
            ),
            "isolated_gate_closed_before_provider": (
                gate_closed["http_status"] == 403
            ),
            "failure_clears_provenance": (
                gate_closed["stale_provenance_visible"] is False
            ),
            "exact_route_call_count": len(route_calls) == 2,
            "loopback_only": not external_hosts,
            "database_unchanged": (
                before["counts"] == after["counts"]
                and before["sha256"] == after["sha256"]
            ),
        }
        if not all(checks.values()):
            failed = sorted(key for key, value in checks.items() if not value)
            raise RuntimeError(
                f"Bureau runtime UI acceptance failed: {failed}"
            )

        evidence = {
            "schema_version": (
                "reception.one.bureau_runtime_ui.live_local_acceptance.v1"
            ),
            "result": (
                "reception_one_bureau_runtime_ui_provider_free_pass"
            ),
            "evidence_label": "live_local_browser_backend_postgres",
            "data_class": "authored_synthetic",
            "request_interception_used": False,
            "browser_result": browser_result,
            "network": {
                "route_call_count": len(route_calls),
                "external_host_count": len(external_hosts),
                "allowed_hosts": ["::1", "127.0.0.1", "localhost"],
            },
            "checks": checks,
            "database_before": before,
            "database_after": after,
            "provider_calls": 0,
            "credential_reads": 0,
            "api_key_authentication_used": False,
            "provider_environment_forwarded": False,
            "appointment_confirmation_performed": False,
            "appointment_write_performed": False,
            "screenshots": [
                str(DESKTOP_SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                str(COMPACT_SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
                str(GATE_CLOSED_SCREENSHOT.relative_to(ROOT)).replace(
                    "\\", "/"
                ),
            ],
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
            runtime.base.stop_runtime(processes)
        if runtime_dir is not None:
            runtime._remove_runtime_dir(runtime_dir)
        if database_created:
            cleanup = runtime.base.cleanup_database()
            DATABASE_CLEANUP.write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "reception.one.bureau_runtime_ui."
                            "database_cleanup.v1"
                        ),
                        "ownership_marker_verified": True,
                        "scope": (
                            "exact_disposable_authored_synthetic_database"
                        ),
                        "cleanup": cleanup,
                        "runtime_processes_absent": all(
                            process.poll() is not None
                            for process in processes
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
