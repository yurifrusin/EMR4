#!/usr/bin/env python3
"""Exercise the default-off Diary practitioner composition in real Chromium.

The browser loads the ordinary static Diary and its real ES modules from a
loopback static server. Every application API request is intercepted with a
closed authored-synthetic fixture; every other non-loopback request is blocked.
No backend application, database, provider, or real identity is used.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-native-diary-application-session-route-intercepted-browser"
)
EVIDENCE = OUTPUT / "route-intercepted-browser-evidence.json"
DIARY_FILES = (
    ROOT / "docs" / "diary" / "diary.html",
    ROOT / "docs" / "diary" / "diary.js",
    ROOT / "docs" / "diary" / "application-session-practitioner-directory.mjs",
    ROOT / "docs" / "diary" / "application-session-practitioner-reconciler.mjs",
)
HOSTING_POLICY = ROOT / "docs" / "taskpane" / "hosting-policy.js"
API_HOST = "property-cinch-backfield.ngrok-free.dev"
BOOTSTRAP_GLOBAL = "__EMR4_NATIVE_DIARY_APPLICATION_SESSION_PRACTITIONERS__"
EVIDENCE_MODE = "route_intercepted_browser"
EXPECTED_MODULE_PATHS = (
    "/diary/application-session-practitioner-directory.mjs",
    "/diary/application-session-practitioner-reconciler.mjs",
)
PROVIDER_HOST_FRAGMENTS = (
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "api.openai.com",
    "deepseek.com",
    "anthropic.com",
)
ALLOWED_API_METHODS = {
    "/api/v1/diary/locations": "GET",
    "/api/v1/diary/template": "GET",
    "/api/v1/appointments": "GET",
    "/api/v1/appointments/types": "GET",
    "/api/v1/diary/roster": "GET",
    "/api/v1/diary/waiting-areas": "GET",
    "/api/v1/graphql": "POST",
    "/api/v1/appointments/bernie/pilot-eligibility": "GET",
}


def _api_fixture_admission(method: str, path: str) -> str:
    expected_method = ALLOWED_API_METHODS.get(path)
    if expected_method is None:
        return "unknown_path"
    normalized_method = method.upper()
    if normalized_method == "OPTIONS":
        return "cors_preflight"
    if normalized_method != expected_method:
        return "wrong_method"
    return "admitted"

FIXED_ROWS = [
    {
        "id": "practitioner-browser-fixed-001",
        "displayName": "Avery Browser Synthetic",
        "roleLabel": "GP",
        "active": True,
        "defaultLocation": {
            "id": "location-browser-synthetic-001",
            "name": "Browser Synthetic Clinic",
        },
    },
    {
        "id": "practitioner-browser-fixed-002",
        "displayName": "Morgan Browser Synthetic",
        "roleLabel": "GP",
        "active": True,
        "defaultLocation": None,
    },
]
LEGACY_ROWS = [
    {
        "id": "practitioner-browser-fixed-001",
        "displayName": "Legacy Browser Synthetic",
        "roleLabel": "GP",
        "active": True,
        "defaultLocation": {
            "id": "location-browser-synthetic-001",
            "name": "Browser Synthetic Clinic",
        },
    }
]
STALE_ROWS = [
    {
        "id": "practitioner-browser-stale-001",
        "displayName": "Stale Browser Synthetic",
        "roleLabel": "GP",
        "active": True,
        "defaultLocation": None,
    }
]
TEMPLATE = {
    "practice_name": "Browser Synthetic Practice",
    "slot_start": "09:00",
    "slot_end": "10:00",
    "slot_interval_minutes": 15,
    "columns": [
        {
            "room_label": "Browser Room One",
            "assignment": "Synthetic Roster Assignment",
            "practitioner_id": "practitioner-browser-fixed-001",
            "practitioner_ahpra": "MED0000000001",
            "tint_hex": "E8F0FE",
            "slot_interval_minutes": 15,
            "breaks": [],
        }
    ],
    "footer": ["Authored-synthetic route-intercepted browser rehearsal"],
}


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
            raise RuntimeError("route-intercepted Diary static server did not stop")


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _json_response(route: Route, value: Any, *, status: int = 200) -> None:
    route.fulfill(
        status=status,
        content_type="application/json; charset=utf-8",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": (
                "authorization,content-type,ngrok-skip-browser-warning"
            ),
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
        body=json.dumps(value, ensure_ascii=False, separators=(",", ":")),
    )


def _synthetic_token() -> str:
    def encode(value: dict[str, Any]) -> str:
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return ".".join(
        (
            encode({"alg": "none", "typ": "JWT"}),
            encode({"role": "Receptionist", "exp": 4102444800}),
            "authored-synthetic-signature",
        )
    )


def _init_script(mode: str) -> str:
    token = json.dumps(_synthetic_token())
    fixed_rows = json.dumps(FIXED_ROWS, ensure_ascii=False)
    stale_rows = json.dumps(STALE_ROWS, ensure_ascii=False)
    install_bootstrap = mode != "feature_off"
    initial_mode = "reject" if mode == "reject" else "success"
    bootstrap = ""
    if install_bootstrap:
        bootstrap = f"""
        window.{BOOTSTRAP_GLOBAL} = {{
          enabled: true,
          readFixedPractitionerDirectory: window.__EMR4_ROUTE_INTERCEPTED_READER__,
          sessionGeneration: 1
        }};
        """
    return f"""
    (() => {{
      localStorage.setItem("emr4_token", {token});
      window.__EMR4_ROUTE_INTERCEPTED_READER_CALLS__ = 0;
      window.__EMR4_ROUTE_INTERCEPTED_READER_MODE__ = {json.dumps(initial_mode)};
      window.__EMR4_ROUTE_INTERCEPTED_PENDING_RESOLVE__ = null;
      window.__EMR4_ROUTE_INTERCEPTED_FIXED_ROWS__ = {fixed_rows};
      window.__EMR4_ROUTE_INTERCEPTED_STALE_ROWS__ = {stale_rows};
      window.__EMR4_ROUTE_INTERCEPTED_READER__ = async () => {{
        window.__EMR4_ROUTE_INTERCEPTED_READER_CALLS__ += 1;
        if (window.__EMR4_ROUTE_INTERCEPTED_READER_MODE__ === "reject") {{
          throw new Error("raw_reader_failure_must_not_escape");
        }}
        if (window.__EMR4_ROUTE_INTERCEPTED_READER_MODE__ === "deferred") {{
          return await new Promise((resolve) => {{
            window.__EMR4_ROUTE_INTERCEPTED_PENDING_RESOLVE__ = resolve;
          }});
        }}
        return {{
          status: "success",
          rows: window.__EMR4_ROUTE_INTERCEPTED_FIXED_ROWS__
        }};
      }};
      {bootstrap}
    }})();
    """


def _fixture_for(path: str, *, graphql_rows: list[dict[str, Any]]) -> Any:
    if path == "/api/v1/diary/locations":
        return [
            {
                "id": "location-browser-synthetic-001",
                "name": "Browser Synthetic Clinic",
            }
        ]
    if path == "/api/v1/diary/template":
        return TEMPLATE
    if path == "/api/v1/appointments":
        return []
    if path == "/api/v1/appointments/types":
        return []
    if path == "/api/v1/diary/roster":
        return {"entries": []}
    if path == "/api/v1/diary/waiting-areas":
        return []
    if path == "/api/v1/graphql":
        return {"data": {"practice": {"practitioners": graphql_rows}}}
    if path == "/api/v1/appointments/bernie/pilot-eligibility":
        return {"eligible": False}
    raise KeyError(path)


def _install_routes(
    page: Page,
    *,
    network: list[dict[str, str]],
    graphql_rows: list[dict[str, Any]],
    unknown_api_paths: set[str],
    unexpected_api_requests: set[str],
    blocked_external_hosts: set[str],
) -> None:
    def handle(route: Route) -> None:
        request = route.request
        split = urlsplit(request.url)
        host = split.hostname or ""
        path = split.path
        network.append(
            {
                "host": host,
                "method": request.method.upper(),
                "path": path,
                "resource_type": request.resource_type,
            }
        )

        if host in {"127.0.0.1", "localhost", ""} and path == "/hosting-policy.js":
            route.fulfill(
                status=200,
                content_type="application/javascript; charset=utf-8",
                body=HOSTING_POLICY.read_text(encoding="utf-8"),
            )
            return
        if host in {"127.0.0.1", "localhost", ""} and path == "/favicon.ico":
            route.fulfill(status=204, body="")
            return
        if host in {"127.0.0.1", "localhost", ""}:
            route.continue_()
            return
        if host == API_HOST and path.startswith("/api/v1/"):
            method = request.method.upper()
            admission = _api_fixture_admission(method, path)
            if admission == "unknown_path":
                unknown_api_paths.add(path)
                unexpected_api_requests.add(f"{method} {path}")
                _json_response(route, {"detail": "fixture_not_allowlisted"}, status=404)
                return
            if admission == "cors_preflight":
                _json_response(route, {})
                return
            if admission == "wrong_method":
                unexpected_api_requests.add(f"{method} {path}")
                _json_response(route, {"detail": "fixture_method_not_allowlisted"}, status=405)
                return
            try:
                value = _fixture_for(path, graphql_rows=graphql_rows)
            except KeyError:
                unknown_api_paths.add(path)
                unexpected_api_requests.add(f"{method} {path}")
                _json_response(route, {"detail": "fixture_not_allowlisted"}, status=404)
                return
            _json_response(route, value)
            return

        blocked_external_hosts.add(host)
        route.abort()

    page.route("**/*", handle)


def _new_case_page(
    browser: Browser,
    *,
    mode: str,
    graphql_rows: list[dict[str, Any]],
) -> tuple[
    BrowserContext,
    Page,
    list[dict[str, str]],
    list[str],
    set[str],
    set[str],
    set[str],
]:
    context = browser.new_context(
        viewport={"width": 1120, "height": 760},
        locale="en-AU",
        timezone_id="Australia/Brisbane",
    )
    context.add_init_script(script=_init_script(mode))
    page = context.new_page()
    network: list[dict[str, str]] = []
    console_errors: list[str] = []
    unknown_api_paths: set[str] = set()
    unexpected_api_requests: set[str] = set()
    blocked_external_hosts: set[str] = set()
    page.on(
        "console",
        lambda message: (
            console_errors.append(message.text)
            if message.type == "error"
            else None
        ),
    )
    _install_routes(
        page,
        network=network,
        graphql_rows=graphql_rows,
        unknown_api_paths=unknown_api_paths,
        unexpected_api_requests=unexpected_api_requests,
        blocked_external_hosts=blocked_external_hosts,
    )
    return (
        context,
        page,
        network,
        console_errors,
        unknown_api_paths,
        unexpected_api_requests,
        blocked_external_hosts,
    )


def _goto(page: Page, base_url: str) -> None:
    page.goto(
        f"{base_url}/diary/diary.html?standalone_diary=true",
        wait_until="domcontentloaded",
    )


def _wait_for_success(page: Page) -> None:
    page.wait_for_function(
        """() => {
          const status = document.getElementById("diary-status")?.textContent || "";
          const grid = document.getElementById("diary-grid-container");
          return status.startsWith("0 appointments")
            && grid && !grid.classList.contains("hidden");
        }"""
    )


def _open_practitioner_dropdown(page: Page) -> list[str]:
    targets = page.locator("button.booking-gap-target")
    target_count = targets.count()
    if target_count != 1:
        raise AssertionError(f"expected one booking gap target, got {target_count}")
    targets.click()
    page.locator("#booking-modal").wait_for(state="visible")
    options = page.locator("#booking-practitioner option").all_text_contents()
    return [value.strip() for value in options]


def _close_booking_modal(page: Page) -> None:
    close = page.locator("#btn-booking-close")
    if close.count() != 1:
        raise AssertionError("booking close control is not unique")
    close.click()
    page.locator("#booking-modal").wait_for(state="hidden")


def _request_summary(network: list[dict[str, str]]) -> dict[str, Any]:
    local_module_paths = sorted(
        {
            item["path"]
            for item in network
            if item["path"].endswith(".mjs")
        }
    )
    api_paths = sorted(
        {
            item["path"]
            for item in network
            if item["host"] == API_HOST and item["method"] != "OPTIONS"
        }
    )
    return {
        "api_paths": api_paths,
        "api_request_tuples": sorted(
            {
                f"{item['method']} {item['path']}"
                for item in network
                if item["host"] == API_HOST and item["method"] != "OPTIONS"
            }
        ),
        "graphql_request_count": sum(
            item["host"] == API_HOST
            and item["path"] == "/api/v1/graphql"
            and item["method"] == "POST"
            for item in network
        ),
        "legacy_rest_practitioner_request_count": sum(
            item["host"] == API_HOST
            and item["path"] == "/api/v1/practice/practitioners"
            and item["method"] == "GET"
            for item in network
        ),
        "local_module_paths": local_module_paths,
        "local_paths": sorted(
            {
                item["path"]
                for item in network
                if item["host"] in {"127.0.0.1", "localhost", ""}
            }
        ),
    }


def _run_enabled_success_and_transition(
    browser: Browser,
    base_url: str,
) -> dict[str, Any]:
    (
        context,
        page,
        network,
        console_errors,
        unknown_api_paths,
        unexpected_api_requests,
        blocked_external_hosts,
    ) = _new_case_page(browser, mode="success", graphql_rows=LEGACY_ROWS)
    try:
        _goto(page, base_url)
        _wait_for_success(page)
        fixed_options = _open_practitioner_dropdown(page)
        _close_booking_modal(page)
        pre_transition_request_summary = _request_summary(network)

        page.evaluate(
            "window.__EMR4_ROUTE_INTERCEPTED_READER_MODE__ = 'deferred'"
        )
        refresh = page.locator("#btn-refresh")
        if refresh.count() != 1:
            raise AssertionError("refresh control is not unique")
        refresh.click()
        page.wait_for_function(
            "() => window.__EMR4_ROUTE_INTERCEPTED_READER_CALLS__ === 2"
            " && typeof window.__EMR4_ROUTE_INTERCEPTED_PENDING_RESOLVE__"
            " === 'function'"
        )

        page.evaluate(
            f"window.{BOOTSTRAP_GLOBAL}.enabled = false"
        )
        page.evaluate(
            """() => {
              window.__EMR4_ROUTE_INTERCEPTED_READ_COMPLETE_COUNT__ = 0;
              window.addEventListener("emr4:diary-read-complete", () => {
                window.__EMR4_ROUTE_INTERCEPTED_READ_COMPLETE_COUNT__ += 1;
              });
            }"""
        )
        refresh.click()
        page.wait_for_function(
            "() => window.__EMR4_ROUTE_INTERCEPTED_READ_COMPLETE_COUNT__ === 1"
        )
        post_disable_request_summary = _request_summary(network)
        legacy_options_before_stale = _open_practitioner_dropdown(page)
        _close_booking_modal(page)

        page.evaluate(
            """() => {
              const resolve = window.__EMR4_ROUTE_INTERCEPTED_PENDING_RESOLVE__;
              window.__EMR4_ROUTE_INTERCEPTED_PENDING_RESOLVE__ = null;
              resolve({
                status: "success",
                rows: window.__EMR4_ROUTE_INTERCEPTED_STALE_ROWS__
              });
            }"""
        )
        page.wait_for_function(
            "() => document.getElementById('diary-status')?.textContent"
            "?.includes('application_session_practitioner_directory_failure')"
        )
        stale_name_count = page.get_by_text(
            "Stale Browser Synthetic", exact=True
        ).count()

        refresh.click()
        page.wait_for_function(
            "() => window.__EMR4_ROUTE_INTERCEPTED_READ_COMPLETE_COUNT__ === 2"
        )
        _wait_for_success(page)
        legacy_options_after_recovery = _open_practitioner_dropdown(page)
        _close_booking_modal(page)

        request_summary = _request_summary(network)
        return {
            "case_id": "enabled_success_and_disable_transition",
            "fixed_reader_call_count": page.evaluate(
                "window.__EMR4_ROUTE_INTERCEPTED_READER_CALLS__"
            ),
            "fixed_reader_options": fixed_options,
            "pre_transition_graphql_request_count": (
                pre_transition_request_summary["graphql_request_count"]
            ),
            "pre_transition_legacy_rest_practitioner_request_count": (
                pre_transition_request_summary[
                    "legacy_rest_practitioner_request_count"
                ]
            ),
            "post_disable_graphql_request_count": (
                post_disable_request_summary["graphql_request_count"]
            ),
            "post_disable_legacy_rest_practitioner_request_count": (
                post_disable_request_summary[
                    "legacy_rest_practitioner_request_count"
                ]
            ),
            "legacy_options_before_stale_resolution": legacy_options_before_stale,
            "legacy_options_after_recovery": legacy_options_after_recovery,
            "stale_row_visible_count": stale_name_count,
            "late_stale_failure_marker_observed": True,
            "module_paths_loaded": request_summary["local_module_paths"],
            "api_request_tuples": request_summary["api_request_tuples"],
            "local_paths": request_summary["local_paths"],
            "graphql_request_count": request_summary["graphql_request_count"],
            "legacy_rest_practitioner_request_count": request_summary[
                "legacy_rest_practitioner_request_count"
            ],
            "unknown_api_paths": sorted(unknown_api_paths),
            "unexpected_api_requests": sorted(unexpected_api_requests),
            "blocked_external_hosts": sorted(blocked_external_hosts),
            "console_errors": console_errors,
        }
    finally:
        context.close()


def _run_enabled_failure(
    browser: Browser,
    base_url: str,
) -> dict[str, Any]:
    (
        context,
        page,
        network,
        console_errors,
        unknown_api_paths,
        unexpected_api_requests,
        blocked_external_hosts,
    ) = _new_case_page(browser, mode="reject", graphql_rows=LEGACY_ROWS)
    try:
        _goto(page, base_url)
        page.wait_for_function(
            "() => document.getElementById('diary-status')?.textContent"
            "?.includes('application_session_practitioner_directory_failure')"
        )
        error = page.locator("#diary-error")
        error.wait_for(state="visible")
        request_summary = _request_summary(network)
        return {
            "case_id": "enabled_reader_failure",
            "error_text": error.inner_text(),
            "grid_container_hidden": page.locator(
                "#diary-grid-container"
            ).evaluate("element => element.classList.contains('hidden')"),
            "grid_child_count": page.locator("#diary-grid").evaluate(
                "element => element.childElementCount"
            ),
            "fixed_reader_call_count": page.evaluate(
                "window.__EMR4_ROUTE_INTERCEPTED_READER_CALLS__"
            ),
            "graphql_request_count": request_summary["graphql_request_count"],
            "legacy_rest_practitioner_request_count": request_summary[
                "legacy_rest_practitioner_request_count"
            ],
            "module_paths_loaded": request_summary["local_module_paths"],
            "api_request_tuples": request_summary["api_request_tuples"],
            "local_paths": request_summary["local_paths"],
            "unknown_api_paths": sorted(unknown_api_paths),
            "unexpected_api_requests": sorted(unexpected_api_requests),
            "blocked_external_hosts": sorted(blocked_external_hosts),
            "console_errors": console_errors,
        }
    finally:
        context.close()


def _run_feature_off_legacy(browser: Browser, base_url: str) -> dict[str, Any]:
    (
        context,
        page,
        network,
        console_errors,
        unknown_api_paths,
        unexpected_api_requests,
        blocked_external_hosts,
    ) = _new_case_page(browser, mode="feature_off", graphql_rows=LEGACY_ROWS)
    try:
        _goto(page, base_url)
        _wait_for_success(page)
        options = _open_practitioner_dropdown(page)
        _close_booking_modal(page)
        request_summary = _request_summary(network)
        return {
            "case_id": "feature_off_legacy_graphql",
            "legacy_options": options,
            "bootstrap_present": page.evaluate(
                f"Object.prototype.hasOwnProperty.call(window, '{BOOTSTRAP_GLOBAL}')"
            ),
            "graphql_request_count": request_summary["graphql_request_count"],
            "legacy_rest_practitioner_request_count": request_summary[
                "legacy_rest_practitioner_request_count"
            ],
            "module_paths_loaded": request_summary["local_module_paths"],
            "api_request_tuples": request_summary["api_request_tuples"],
            "local_paths": request_summary["local_paths"],
            "unknown_api_paths": sorted(unknown_api_paths),
            "unexpected_api_requests": sorted(unexpected_api_requests),
            "blocked_external_hosts": sorted(blocked_external_hosts),
            "console_errors": console_errors,
        }
    finally:
        context.close()


def build_evidence() -> dict[str, Any]:
    with static_server() as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            enabled = _run_enabled_success_and_transition(
                browser, base_url
            )
            failure = _run_enabled_failure(browser, base_url)
            feature_off = _run_feature_off_legacy(browser, base_url)
        finally:
            browser.close()

    provider_hosts = sorted(
        {
            host
            for case in (enabled, failure, feature_off)
            for host in case["blocked_external_hosts"]
            if any(fragment in host for fragment in PROVIDER_HOST_FRAGMENTS)
        }
    )
    checks = {
        "real_es_modules_loaded_in_enabled_cases": all(
            set(EXPECTED_MODULE_PATHS).issubset(case["module_paths_loaded"])
            for case in (enabled, failure)
        ),
        "fixed_reader_rendered_authored_synthetic_directory": enabled[
            "fixed_reader_options"
        ]
        == [
            "Avery Browser Synthetic (Browser Synthetic Clinic)",
            "Morgan Browser Synthetic",
        ],
        "enabled_path_never_used_legacy_graphql_or_rest": (
            enabled["pre_transition_graphql_request_count"] == 0
            and enabled[
                "pre_transition_legacy_rest_practitioner_request_count"
            ]
            == 0
            and failure["graphql_request_count"] == 0
            and failure["legacy_rest_practitioner_request_count"] == 0
        ),
        "disable_transition_invalidated_late_result": (
            enabled["stale_row_visible_count"] == 0
            and enabled["post_disable_graphql_request_count"] == 1
            and enabled[
                "post_disable_legacy_rest_practitioner_request_count"
            ]
            == 0
            and enabled["legacy_options_before_stale_resolution"]
            == ["Legacy Browser Synthetic (Browser Synthetic Clinic)"]
            and enabled["legacy_options_after_recovery"]
            == ["Legacy Browser Synthetic (Browser Synthetic Clinic)"]
        ),
        "enabled_failure_had_no_partial_grid_render": (
            failure["grid_container_hidden"] is True
            and failure["grid_child_count"] == 0
            and failure["error_text"]
            == "Failed to load diary: "
            "application_session_practitioner_directory_failure"
        ),
        "enabled_failure_released_no_raw_reader_error": (
            "raw_reader_failure_must_not_escape" not in failure["error_text"]
        ),
        "feature_off_preserved_legacy_graphql": (
            feature_off["bootstrap_present"] is False
            and feature_off["graphql_request_count"] == 1
            and feature_off["legacy_rest_practitioner_request_count"] == 0
            and feature_off["legacy_options"]
            == ["Legacy Browser Synthetic (Browser Synthetic Clinic)"]
            and feature_off["module_paths_loaded"] == []
        ),
        "closed_api_fixture_allowlist": all(
            not case["unknown_api_paths"]
            and not case["unexpected_api_requests"]
            and all(
                ALLOWED_API_METHODS.get(request_tuple.split(" ", 1)[1])
                == request_tuple.split(" ", 1)[0]
                for request_tuple in case["api_request_tuples"]
            )
            for case in (enabled, failure, feature_off)
        ),
        "no_unexpected_external_or_provider_hosts": all(
            not case["blocked_external_hosts"]
            for case in (enabled, failure, feature_off)
        )
        and not provider_hosts,
        "no_browser_console_errors": all(
            not case["console_errors"]
            for case in (enabled, failure, feature_off)
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        diagnostic = json.dumps(
            {"failed": failed, "cases": [enabled, failure, feature_off]},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        raise AssertionError(
            f"route-intercepted browser checks failed:\n{diagnostic}"
        )

    return {
        "schema_version": (
            "raisa.native-diary-application-session-"
            "route-intercepted-browser-evidence.v1"
        ),
        "candidate_result": "candidate_ready",
        "evidence_mode": EVIDENCE_MODE,
        "data_class": "authored_synthetic",
        "browser": {
            "engine": "chromium",
            "headless": True,
            "ordinary_ui_actions": [
                "open_booking_gap",
                "close_booking_modal",
                "refresh_diary",
            ],
            "fixture_control_actions": [
                "install_bootstrap_before_document_script",
                "hold_and_release_fixed_reader_result",
                "disable_bootstrap_before_visible_refresh",
            ],
            "static_route_fixture_paths": ["/hosting-policy.js"],
        },
        "browser_skill_path": {
            "availability": "available",
            "baseline_page_identity": "EMR — Diary",
            "baseline_smoke_render": "passed",
            "baseline_refresh_interaction": "passed",
            "baseline_console_health": "passed",
            "fallback": "repository_playwright",
            "fallback_reason": (
                "The Browser runtime exposes page inspection and interaction "
                "but no request-routing or pre-document init-script API; the "
                "frozen rehearsal requires both to establish the closed "
                "route-intercepted bootstrap boundary."
            ),
        },
        "source_hashes": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*DIARY_FILES, HOSTING_POLICY)
        },
        "cases": [enabled, failure, feature_off],
        "checks": checks,
        "authority": {
            "provider": False,
            "model": False,
            "real_identity": False,
            "real_or_product_data": False,
            "backend": False,
            "database": False,
            "command": False,
            "write": False,
            "default_on": False,
            "app_main_mounted": False,
            "deployment": False,
            "production": False,
            "release": False,
        },
        "claims_not_made": [
            "live_browser_backend_postgres",
            "real_application_session_injection",
            "cross_tab_lifecycle_delivery",
            "browser_matrix",
            "usability",
            "default_on",
            "production_or_release",
        ],
    }


def _write_evidence(value: dict[str, Any]) -> None:
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    EVIDENCE.write_text(rendered + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="reproduce in a temporary directory and compare committed JSON",
    )
    args = parser.parse_args()

    if args.check:
        candidate = build_evidence()
        expected = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        if candidate != expected:
            raise SystemExit("committed route-intercepted evidence is stale")
        print(json.dumps({"status": "passed", "evidence": str(EVIDENCE)}))
        return 0

    evidence = build_evidence()
    _write_evidence(evidence)
    print(json.dumps({"status": "passed", "evidence": str(EVIDENCE)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
