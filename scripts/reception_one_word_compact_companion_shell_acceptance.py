#!/usr/bin/env python3
"""Exercise the provider-free Word companion and native Diary round trip."""

from __future__ import annotations

import hashlib
import json
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import Page, Route, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-compact-companion-shell"
)
EVIDENCE = OUTPUT / "browser-acceptance-evidence.json"
TASKPANE_EMPTY = OUTPUT / "word-companion-empty.png"
TASKPANE_ADMITTED = OUTPUT / "word-companion-admitted.png"
NATIVE_DIARY = OUTPUT / "native-diary-detail.png"
REQUEST = "Show Margaret Thompson's upcoming appointments"
INITIAL_DATE = "2026-07-27"
PROVIDER_HOST_FRAGMENTS = (
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "api.openai.com",
    "deepseek.com",
    "terra",
)
REQUEST_KEYS = {
    "appointment_context_authority",
    "appointment_write_authority",
    "command_authority",
    "contract_version",
    "correlation_id",
    "data_class",
    "evidence_mode",
    "patient_context_authority",
    "planner_mode",
    "projection_intent",
    "provider_authority",
    "reference_date",
    "request_id",
    "request_text",
    "source_surface",
    "target_surface",
    "type",
}
SUMMARY_KEYS = {
    "appointment_context_included",
    "appointment_write_authority",
    "command_authority",
    "contract_version",
    "correlation_id",
    "detail_fields_released",
    "details_surface",
    "evidence_mode",
    "patient_context_included",
    "planner_mode",
    "projection_family",
    "proofreader_disposition",
    "provider_authority",
    "reference_date",
    "request_id",
    "request_text_included",
    "result_count",
    "source_surface",
    "status",
    "summary_code",
    "target_surface",
    "type",
}


OFFICE_STUB = r"""
(() => {
  window.__emr4DialogMessages = [];
  window.__emr4DialogUrl = null;
  window.__emr4DialogOptions = null;
  window.__emr4DialogMessageHandler = null;
  window.__emr4ParentHandler = null;
  window.__emr4ParentMessages = [];

  const EventType = Object.freeze({
    DialogMessageReceived: "DialogMessageReceived",
    DialogEventReceived: "DialogEventReceived",
    DialogParentMessageReceived: "DialogParentMessageReceived",
    DocumentSelectionChanged: "DocumentSelectionChanged"
  });

  window.Office = {
    HostType: Object.freeze({ Word: "Word" }),
    AsyncResultStatus: Object.freeze({
      Failed: "failed",
      Succeeded: "succeeded"
    }),
    EventType,
    actions: Object.freeze({ associate() {} }),
    context: {
      document: Object.freeze({ addHandlerAsync() {} }),
      ui: {
        addHandlerAsync(eventType, handler) {
          if (eventType === EventType.DialogParentMessageReceived) {
            window.__emr4ParentHandler = handler;
          }
        },
        messageParent(message) {
          window.__emr4ParentMessages.push(message);
        },
        displayDialogAsync(url, options, callback) {
          window.__emr4DialogUrl = url;
          window.__emr4DialogOptions = options;
          const handlers = {};
          const dialog = {
            addEventHandler(eventType, handler) {
              handlers[eventType] = handler;
              if (eventType === EventType.DialogMessageReceived) {
                window.__emr4DialogMessageHandler = handler;
                setTimeout(
                  () => handler({ message: JSON.stringify({ type: "ready" }) }),
                  0
                );
              }
            },
            close() {},
            messageChild(message) {
              window.__emr4DialogMessages.push(message);
            }
          };
          callback({
            status: window.Office.AsyncResultStatus.Succeeded,
            value: dialog
          });
        }
      }
    },
    onReady(callback) {
      return Promise.resolve().then(
        () => callback({ host: window.Office.HostType.Word, platform: "web" })
      );
    }
  };
})();
"""


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
            raise RuntimeError("compact companion acceptance server did not stop")


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def write_json(path: Path, value: dict[str, Any]) -> None:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    path.write_text(rendered + "\n", encoding="utf-8", newline="\n")


def install_network_guard(
    page: Page,
    *,
    network: list[dict[str, str]],
    intercepted_external_hosts: set[str],
    blocked_external_hosts: set[str],
) -> None:
    def handle_request(route: Route) -> None:
        request = route.request
        split = urlsplit(request.url)
        hostname = split.hostname or ""
        network.append(
            {
                "method": request.method.upper(),
                "hostname": hostname,
                "port": str(split.port or ""),
                "path": split.path,
            }
        )
        if hostname == "appsforoffice.microsoft.com":
            intercepted_external_hosts.add(hostname)
            route.fulfill(
                status=200,
                content_type="application/javascript",
                body=OFFICE_STUB,
            )
        elif hostname not in {"127.0.0.1", "localhost", ""}:
            blocked_external_hosts.add(hostname)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handle_request)


def run_taskpane_start(page: Page, base_url: str) -> dict[str, Any]:
    page.goto(
        (
            f"{base_url}/taskpane/taskpane.html"
            "?reception_one_companion_demo=true"
        ),
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        "() => typeof document.getElementById('btn-reception-one-prepare')"
        "?.onclick === 'function'"
    )
    page.evaluate("showView('view-app')")
    page.wait_for_function(
        "() => {"
        "const companion = document.getElementById('reception-one-companion');"
        "return companion && !companion.classList.contains('hidden')"
        "&& companion.offsetParent !== null;"
        "}"
    )
    page.locator("#reception-one-companion").screenshot(
        path=str(TASKPANE_EMPTY)
    )
    request = page.locator("#reception-one-companion-request")
    request.fill(REQUEST)
    request_metrics = request.evaluate(
        """element => ({
          client_width: element.clientWidth,
          scroll_width: element.scrollWidth,
          client_height: element.clientHeight,
          scroll_height: element.scrollHeight
        })"""
    )
    page.locator("#btn-reception-one-prepare").click()
    page.wait_for_function(
        "() => window.__emr4DialogMessages?.length === 3"
    )
    captured = page.evaluate(
        """() => ({
          url: window.__emr4DialogUrl,
          options: window.__emr4DialogOptions,
          messages: window.__emr4DialogMessages,
          request_cleared:
            document.getElementById("reception-one-companion-request")
              ?.value === ""
        })"""
    )
    messages = [json.loads(value) for value in captured["messages"]]
    return {
        "dialog_url": captured["url"],
        "dialog_options": captured["options"],
        "message_types": [value.get("type") for value in messages],
        "auth": messages[0],
        "launch": messages[1],
        "request": messages[2],
        "request_cleared": captured["request_cleared"],
        "request_metrics": request_metrics,
    }


def run_native_diary(
    page: Page,
    *,
    base_url: str,
    launch: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    page.goto(
        (
            f"{base_url}/diary/diary.html"
            f"?smoke=true&reference_date={INITIAL_DATE}"
            "&reception_one_companion_demo=true"
        ),
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        "() => typeof window.__emr4ParentHandler === 'function'"
    )
    page.evaluate(
        """() => {
          window.__emr4CompanionTimeline = [];
          window.addEventListener(
            "emr4:diary-read-complete",
            event => window.__emr4CompanionTimeline.push({
              event: "diary_read_complete",
              date: event.detail?.date || null
            })
          );
          window.addEventListener(
            "emr4:reception-one-companion-request",
            () => window.__emr4CompanionTimeline.push({
              event: "companion_request_admitted",
              date:
                document.getElementById("diary-date-picker")?.value || null
            })
          );
        }"""
    )
    page.evaluate(
        "(payload) => window.__emr4ParentHandler({"
        "message: JSON.stringify(payload)"
        "})",
        launch,
    )
    page.evaluate(
        "(payload) => window.__emr4ParentHandler({"
        "message: JSON.stringify(payload)"
        "})",
        request,
    )
    page.wait_for_function(
        """() => window.__emr4ParentMessages
          ?.map(value => JSON.parse(value))
          .some(value => value.type === "reception_one_companion_summary")"""
    )
    result = page.evaluate(
        """() => {
          const messages = window.__emr4ParentMessages
            .map(value => JSON.parse(value));
          const summary = messages.find(
            value => value.type === "reception_one_companion_summary"
          );
          const projection = document.getElementById("bernie-meta-grid");
          return {
            summary,
            displayed_date:
              document.getElementById("diary-date-picker")?.value || null,
            projection_open:
              !projection?.classList.contains("hidden"),
            projection_family: projection?.dataset.family || null,
            projection_state: projection?.dataset.projectionState || null,
            detailed_patient_visible:
              projection?.innerText.includes("Margaret Thompson") || false,
            timeline: window.__emr4CompanionTimeline
          };
        }"""
    )
    page.locator("#bernie-meta-grid").screenshot(path=str(NATIVE_DIARY))
    return result


def complete_taskpane(page: Page, summary: dict[str, Any]) -> dict[str, Any]:
    page.evaluate(
        "(payload) => window.__emr4DialogMessageHandler({"
        "message: JSON.stringify(payload)"
        "})",
        summary,
    )
    page.wait_for_function(
        "() => document.getElementById('reception-one-companion-status')"
        "?.textContent.trim().length > 0"
    )
    result = page.evaluate(
        """() => {
          const companion =
            document.getElementById("reception-one-companion");
          const status =
            document.getElementById("reception-one-companion-status");
          return {
            status_text: status?.textContent || "",
            status_state: status?.dataset.state || "",
            button_enabled:
              !document.getElementById("btn-reception-one-prepare")?.disabled,
            input_cleared:
              document.getElementById("reception-one-companion-request")
                ?.value === "",
            patient_name_visible:
              companion?.innerText.includes("Margaret Thompson") || false
          };
        }"""
    )
    page.locator("#reception-one-companion").screenshot(
        path=str(TASKPANE_ADMITTED)
    )
    return result


def run() -> dict[str, Any]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    network: list[dict[str, str]] = []
    console_errors: list[str] = []
    intercepted_external_hosts: set[str] = set()
    blocked_external_hosts: set[str] = set()

    with static_server() as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        taskpane_context = browser.new_context(
            viewport={"width": 360, "height": 780},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        taskpane = taskpane_context.new_page()
        install_network_guard(
            taskpane,
            network=network,
            intercepted_external_hosts=intercepted_external_hosts,
            blocked_external_hosts=blocked_external_hosts,
        )
        taskpane.on(
            "console",
            lambda message: (
                console_errors.append(f"taskpane: {message.text}")
                if message.type == "error"
                else None
            ),
        )
        word_start = run_taskpane_start(taskpane, base_url)

        diary_context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        diary = diary_context.new_page()
        install_network_guard(
            diary,
            network=network,
            intercepted_external_hosts=intercepted_external_hosts,
            blocked_external_hosts=blocked_external_hosts,
        )
        diary.on(
            "console",
            lambda message: (
                console_errors.append(f"diary: {message.text}")
                if message.type == "error"
                else None
            ),
        )
        native = run_native_diary(
            diary,
            base_url=base_url,
            launch=word_start["launch"],
            request=word_start["request"],
        )
        word_complete = complete_taskpane(taskpane, native["summary"])

        diary_context.close()
        taskpane_context.close()
        browser.close()

    split = urlsplit(word_start["dialog_url"])
    dialog_query = parse_qs(split.query)
    summary_serialized = json.dumps(
        native["summary"],
        ensure_ascii=False,
        sort_keys=True,
    )
    provider_hosts = sorted(
        {
            item["hostname"]
            for item in network
            if any(
                fragment in item["hostname"]
                for fragment in PROVIDER_HOST_FRAGMENTS
            )
        }
    )
    backend_requests = [
        item
        for item in network
        if item["port"] == "8001" or item["path"].startswith("/api/")
    ]
    timeline_events = [item["event"] for item in native["timeline"]]
    read_index = (
        timeline_events.index("diary_read_complete")
        if "diary_read_complete" in timeline_events
        else -1
    )
    request_index = (
        timeline_events.index("companion_request_admitted")
        if "companion_request_admitted" in timeline_events
        else -1
    )
    checks = {
        "companion_default_off_capability_is_only_url_context": (
            dialog_query == {
                "reception_one_companion_demo": ["true"],
                "smoke": ["true"],
            }
        ),
        "auth_launch_and_request_are_distinct_and_ordered": (
            word_start["message_types"]
            == [
                "auth",
                "reception_one_launch_context",
                "reception_one_companion_request",
            ]
        ),
        "request_has_exact_closed_manifest": (
            set(word_start["request"]) == REQUEST_KEYS
        ),
        "request_is_authored_synthetic_deterministic_zero_authority": (
            word_start["request"]["data_class"] == "authored_synthetic"
            and word_start["request"]["planner_mode"] == "deterministic"
            and word_start["request"]["patient_context_authority"] is False
            and word_start["request"]["appointment_context_authority"] is False
            and word_start["request"]["appointment_write_authority"] is False
            and word_start["request"]["command_authority"] is False
            and word_start["request"]["provider_authority"] is False
        ),
        "request_and_launch_are_exactly_bound": (
            word_start["request"]["correlation_id"]
            == word_start["launch"]["correlation_id"]
            and word_start["request"]["reference_date"]
            == word_start["launch"]["reference_date"]
        ),
        "request_absent_from_dialog_url": (
            REQUEST not in word_start["dialog_url"]
            and word_start["request"]["correlation_id"]
            not in word_start["dialog_url"]
            and word_start["request"]["request_id"]
            not in word_start["dialog_url"]
        ),
        "taskpane_input_fits_and_clears_after_send": (
            word_start["request_metrics"]["scroll_width"]
            <= word_start["request_metrics"]["client_width"]
            and word_start["request_metrics"]["scroll_height"]
            <= word_start["request_metrics"]["client_height"]
            and word_start["request_cleared"] is True
        ),
        "diary_date_verified_before_request_admission": (
            0 <= read_index < request_index
            and native["timeline"][read_index]["date"]
            == word_start["request"]["reference_date"]
            and native["timeline"][request_index]["date"]
            == word_start["request"]["reference_date"]
        ),
        "detailed_projection_stays_in_native_diary": (
            native["projection_open"] is True
            and native["detailed_patient_visible"] is True
            and word_complete["patient_name_visible"] is False
        ),
        "summary_has_exact_generic_manifest": (
            set(native["summary"]) == SUMMARY_KEYS
        ),
        "summary_is_proofreader_admitted_and_bound": (
            native["summary"]["status"] == "admitted"
            and native["summary"]["proofreader_disposition"] == "admit"
            and native["summary"]["summary_code"] in {
                "results_ready",
                "no_results",
            }
            and native["summary"]["correlation_id"]
            == word_start["request"]["correlation_id"]
            and native["summary"]["request_id"]
            == word_start["request"]["request_id"]
        ),
        "summary_releases_no_detail_or_authority": (
            native["summary"]["detail_fields_released"] is False
            and native["summary"]["request_text_included"] is False
            and native["summary"]["patient_context_included"] is False
            and native["summary"]["appointment_context_included"] is False
            and native["summary"]["appointment_write_authority"] is False
            and native["summary"]["command_authority"] is False
            and native["summary"]["provider_authority"] is False
            and REQUEST not in summary_serialized
            and "Margaret Thompson" not in summary_serialized
        ),
        "word_renders_only_local_generic_copy": (
            word_complete["status_state"] == "ready"
            and word_complete["button_enabled"] is True
            and word_complete["input_cleared"] is True
            and word_complete["status_text"]
            in {
                (
                    f"{native['summary']['result_count']} results are "
                    "ready in the Diary."
                ),
                (
                    f"{native['summary']['result_count']} result is "
                    "ready in the Diary."
                ),
                "No matching results were found. The Diary view is ready.",
            }
        ),
        "office_bootstrap_was_locally_intercepted": (
            intercepted_external_hosts == {"appsforoffice.microsoft.com"}
        ),
        "no_unexpected_external_host": blocked_external_hosts == set(),
        "no_provider_request": provider_hosts == [],
        "no_backend_or_database_request": backend_requests == [],
        "no_console_error": console_errors == [],
    }
    passed = all(checks.values())
    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.word_compact_companion_acceptance.v1"
        ),
        "result": (
            "reception_one_word_compact_companion_shell_pass"
            if passed
            else "reception_one_word_compact_companion_shell_failed"
        ),
        "data_class": "authored_synthetic",
        "evidence_mode": "route_intercepted_browser",
        "planner_mode": "deterministic",
        "checks": checks,
        "request_hash": canonical_hash({"request": REQUEST}),
        "request_contract_hash": canonical_hash(
            {
                key: value
                for key, value in word_start["request"].items()
                if key != "request_text"
            }
        ),
        "request_field_manifest": sorted(word_start["request"]),
        "request_text_retained": False,
        "summary": native["summary"],
        "summary_hash": canonical_hash(native["summary"]),
        "summary_field_manifest": sorted(native["summary"]),
        "native": {
            "displayed_date": native["displayed_date"],
            "projection_open": native["projection_open"],
            "projection_family": native["projection_family"],
            "projection_state": native["projection_state"],
            "timeline": native["timeline"],
        },
        "word": word_complete,
        "provider_calls": 0,
        "credential_reads": 0,
        "database_reads": 0,
        "database_writes": 0,
        "appointment_commands": 0,
        "provider_hosts": provider_hosts,
        "backend_requests": backend_requests,
        "intercepted_external_hosts": sorted(intercepted_external_hosts),
        "blocked_external_hosts": sorted(blocked_external_hosts),
        "console_errors": console_errors,
        "network_request_count": len(network),
        "screenshots": [
            TASKPANE_EMPTY.relative_to(ROOT).as_posix(),
            NATIVE_DIARY.relative_to(ROOT).as_posix(),
            TASKPANE_ADMITTED.relative_to(ROOT).as_posix(),
        ],
        "explicit_exclusions": [
            "real_or_product_derived_data",
            "patient_context_authority",
            "appointment_context_authority",
            "request_or_name_in_return_summary",
            "raw_draft_return",
            "provider_call",
            "credential_read",
            "backend_or_database_read",
            "database_write",
            "appointment_command",
            "voice",
            "production",
            "deployment",
            "release",
        ],
        "candid_limit": (
            "This provider-free route-intercepted Chromium evidence proves "
            "the local loopback Word companion shell, separate typed "
            "Office-dialog messages, verified-date deterministic native "
            "projection and generic validated return summary over "
            "authored-synthetic fixtures. It does not prove an authenticated "
            "Word Online dialog, a live backend or database, provider "
            "interpretation, real-data safety, representative receptionist "
            "usability, production behavior or release readiness."
        ),
    }
    evidence["evidence_hash"] = canonical_hash(evidence)
    write_json(EVIDENCE, evidence)
    if not passed:
        raise RuntimeError(
            "compact companion acceptance failed: "
            + ",".join(
                key for key, value in checks.items() if not value
            )
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
                        "reception_one_word_compact_companion_shell_failed"
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
                "provider_calls": evidence["provider_calls"],
                "database_writes": evidence["database_writes"],
                "summary_code": evidence["summary"]["summary_code"],
                "result_count": evidence["summary"]["result_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
