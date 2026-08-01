#!/usr/bin/env python3
"""Exercise the provider-free Word-to-Reception One contextual launch."""

from __future__ import annotations

import hashlib
import json
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

from playwright.sync_api import Page, Route, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-word-hybrid-contextual-launch"
)
EVIDENCE = OUTPUT / "browser-acceptance-evidence.json"
TASKPANE_SCREENSHOT = OUTPUT / "word-companion-launcher.png"
DESKTOP_SCREENSHOT = OUTPUT / "contextual-launch-desktop.png"
NARROW_SCREENSHOT = OUTPUT / "contextual-launch-narrow.png"
INITIAL_DATE = "2026-07-27"
REQUEST = "Make an appointment for Margaret Thompson with Dr Shera"
LONG_REQUEST = (
    "Please find Margaret Thompson a longer appointment with Dr Shera "
    "late next week, avoiding Monday morning, and show the available choices."
)
PROVIDER_HOST_FRAGMENTS = (
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "api.openai.com",
    "deepseek.com",
    "terra",
)
EXPECTED_CONTEXT_KEYS = {
    "command_authority",
    "contract_version",
    "correlation_id",
    "evidence_mode",
    "open_projection",
    "patient_context_authority",
    "planner_mode",
    "provider_authority",
    "reference_date",
    "source_surface",
    "target_surface",
    "type",
}


OFFICE_STUB = r"""
(() => {
  const dialogMessages = [];
  window.__emr4DialogMessages = dialogMessages;
  window.__emr4DialogUrl = null;
  window.__emr4DialogOptions = null;
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
                setTimeout(
                  () => handler({ message: JSON.stringify({ type: "ready" }) }),
                  0
                );
              }
            },
            close() {},
            messageChild(message) {
              dialogMessages.push(message);
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
            raise RuntimeError("hybrid contextual-launch server did not stop")


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


def run_word_launcher(
    page: Page,
    *,
    base_url: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    page.goto(
        (
            f"{base_url}/taskpane/taskpane.html"
            "?word_hybrid_contextual_launch_acceptance=true"
        ),
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        "() => typeof document.getElementById('btn-reception-one')"
        "?.onclick === 'function'"
    )
    page.evaluate("showView('view-app')")
    page.locator("#btn-reception-one").wait_for(state="visible")
    page.screenshot(path=str(TASKPANE_SCREENSHOT), full_page=True)
    page.locator("#btn-reception-one").click()
    page.wait_for_function(
        "() => window.__emr4DialogMessages?.length === 2"
    )
    captured = page.evaluate(
        """() => ({
          url: window.__emr4DialogUrl,
          options: window.__emr4DialogOptions,
          messages: window.__emr4DialogMessages
        })"""
    )
    decoded = [json.loads(message) for message in captured["messages"]]
    auth_message = decoded[0]
    launch_context = decoded[1]
    launcher = {
        "dialog_url": captured["url"],
        "dialog_options": captured["options"],
        "message_types": [message.get("type") for message in decoded],
        "auth_message_has_null_token": (
            auth_message == {"type": "auth", "token": None}
        ),
        "context_separate_from_auth": (
            launch_context.get("type") == "reception_one_launch_context"
            and "token" not in launch_context
        ),
        "context_absent_from_url": not any(
            field in captured["url"]
            for field in (
                "reference_date",
                "reception_one_launch_context",
                "patient",
                "request_text",
                "token",
            )
        ),
    }
    return launch_context, launcher


def textarea_metrics(page: Page) -> dict[str, Any]:
    return page.locator(
        "#meta-grid-request"
    ).evaluate(
        """element => {
          const style = getComputedStyle(element);
          const rect = element.getBoundingClientRect();
          return {
            height: Math.round(rect.height),
            width: Math.round(rect.width),
            client_height: element.clientHeight,
            scroll_height: element.scrollHeight,
            line_height: style.lineHeight,
            padding_top: style.paddingTop,
            padding_bottom: style.paddingBottom,
            overflow_y: style.overflowY
          };
        }"""
    )


def run_native_diary(
    page: Page,
    *,
    base_url: str,
    launch_context: dict[str, Any],
) -> dict[str, Any]:
    page.goto(
        (
            f"{base_url}/diary/diary.html"
            "?smoke=true"
            f"&reference_date={INITIAL_DATE}"
            "&word_hybrid_contextual_launch_acceptance=true"
        ),
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        "() => typeof window.__emr4ParentHandler === 'function'"
    )
    page.evaluate(
        """() => {
          window.__emr4LaunchTimeline = [];
          window.addEventListener(
            "emr4:diary-read-complete",
            event => window.__emr4LaunchTimeline.push({
              event: "diary_read_complete",
              date: event.detail?.date || null
            })
          );
          const projection = document.getElementById("bernie-meta-grid");
          new MutationObserver(() => {
            if (
              !projection.classList.contains("hidden")
              && !window.__emr4LaunchTimeline.some(
                item => item.event === "projection_open"
              )
            ) {
              window.__emr4LaunchTimeline.push({
                event: "projection_open",
                date: document.getElementById("diary-date-picker")?.value || null
              });
            }
          }).observe(projection, { attributes: true });
        }"""
    )
    page.evaluate(
        "(context) => window.__emr4ParentHandler({"
        "message: JSON.stringify(context)"
        "})",
        launch_context,
    )
    page.wait_for_function(
        """date => (
          document.getElementById("diary-date-picker")?.value === date
          && !document.getElementById("bernie-meta-grid")
            ?.classList.contains("hidden")
        )""",
        arg=launch_context["reference_date"],
    )
    page.wait_for_function(
        "correlationId => "
        "window.EMR4ReceptionOneLaunchContext?.correlation_id"
        " === correlationId",
        arg=launch_context["correlation_id"],
    )

    request = page.get_by_placeholder(
        "What would you like to find or prepare?",
        exact=True,
    )
    request.fill(REQUEST)
    desktop_input = textarea_metrics(page)
    page.screenshot(path=str(DESKTOP_SCREENSHOT), full_page=True)

    page.set_viewport_size({"width": 390, "height": 844})
    narrow_input = textarea_metrics(page)
    page.screenshot(path=str(NARROW_SCREENSHOT), full_page=True)

    request.fill(LONG_REQUEST)
    long_input = textarea_metrics(page)
    result = page.evaluate(
        """() => ({
          displayed_date:
            document.getElementById("diary-date-picker")?.value || null,
          projection_open:
            !document.getElementById("bernie-meta-grid")
              ?.classList.contains("hidden"),
          timeline: window.__emr4LaunchTimeline,
          stored_context: window.EMR4ReceptionOneLaunchContext
        })"""
    )
    result.update(
        {
            "desktop_input": desktop_input,
            "narrow_input": narrow_input,
            "long_input": long_input,
        }
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
            viewport={"width": 390, "height": 844},
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
        launch_context, launcher = run_word_launcher(
            taskpane,
            base_url=base_url,
        )
        taskpane_context.close()

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
            launch_context=launch_context,
        )
        diary_context.close()
        browser.close()

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
    timeline_events = [item["event"] for item in native["timeline"]]
    read_index = (
        timeline_events.index("diary_read_complete")
        if "diary_read_complete" in timeline_events
        else -1
    )
    projection_index = (
        timeline_events.index("projection_open")
        if "projection_open" in timeline_events
        else -1
    )
    context_has_exact_zero_authority_shape = (
        set(launch_context) == EXPECTED_CONTEXT_KEYS
        and launch_context["patient_context_authority"] is False
        and launch_context["command_authority"] is False
        and launch_context["provider_authority"] is False
        and launch_context["planner_mode"] == "deterministic"
    )
    checks = {
        "word_launcher_opened_native_diary_contract": (
            launcher["message_types"]
            == ["auth", "reception_one_launch_context"]
        ),
        "auth_and_context_are_separate": (
            launcher["auth_message_has_null_token"] is True
            and launcher["context_separate_from_auth"] is True
        ),
        "context_not_disclosed_in_url": (
            launcher["context_absent_from_url"] is True
        ),
        "context_has_exact_zero_authority_shape": (
            context_has_exact_zero_authority_shape
        ),
        "native_diary_accepted_exact_context": (
            native["stored_context"] == launch_context
        ),
        "diary_moved_to_requested_date": (
            native["displayed_date"] == launch_context["reference_date"]
            and native["displayed_date"] != INITIAL_DATE
        ),
        "diary_read_verified_before_projection_open": (
            0 <= read_index < projection_index
            and native["timeline"][read_index]["date"]
            == launch_context["reference_date"]
            and native["timeline"][projection_index]["date"]
            == launch_context["reference_date"]
        ),
        "projection_opened_only_after_context_admission": (
            native["projection_open"] is True
        ),
        "desktop_input_not_clipped": (
            52 <= native["desktop_input"]["height"] <= 96
            and native["desktop_input"]["scroll_height"]
            <= native["desktop_input"]["client_height"] + 1
        ),
        "narrow_input_not_clipped": (
            52 <= native["narrow_input"]["height"] <= 96
            and native["narrow_input"]["scroll_height"]
            <= native["narrow_input"]["client_height"] + 1
        ),
        "long_input_growth_is_bounded": (
            52 < native["long_input"]["height"] <= 96
            and native["long_input"]["scroll_height"]
            > native["long_input"]["client_height"]
            and native["long_input"]["overflow_y"] == "auto"
        ),
        "office_bootstrap_was_locally_intercepted": (
            intercepted_external_hosts
            == {"appsforoffice.microsoft.com"}
        ),
        "no_unexpected_external_host": blocked_external_hosts == set(),
        "no_provider_request": provider_hosts == [],
        "no_console_error": console_errors == [],
    }
    passed = all(checks.values())
    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.word_hybrid_contextual_launch_acceptance.v1"
        ),
        "result": (
            "reception_one_word_hybrid_contextual_launch_pass"
            if passed
            else "reception_one_word_hybrid_contextual_launch_failed"
        ),
        "data_class": "authored_synthetic",
        "planner_mode": "deterministic",
        "checks": checks,
        "launch_context_hash": canonical_hash(launch_context),
        "launch_context_field_manifest": sorted(launch_context),
        "launch_reference_date": launch_context["reference_date"],
        "launcher": launcher,
        "native": native,
        "request_text_retained_in_json": False,
        "request_hashes": [
            canonical_hash({"request": REQUEST}),
            canonical_hash({"request": LONG_REQUEST}),
        ],
        "provider_calls": 0,
        "credential_reads": 0,
        "database_reads": 0,
        "database_writes": 0,
        "provider_hosts": provider_hosts,
        "intercepted_external_hosts": sorted(intercepted_external_hosts),
        "blocked_external_hosts": sorted(blocked_external_hosts),
        "console_errors": console_errors,
        "network_request_count": len(network),
        "screenshots": [
            TASKPANE_SCREENSHOT.relative_to(ROOT).as_posix(),
            DESKTOP_SCREENSHOT.relative_to(ROOT).as_posix(),
            NARROW_SCREENSHOT.relative_to(ROOT).as_posix(),
        ],
        "explicit_exclusions": [
            "patient_context",
            "appointment_context",
            "request_text_in_launch_context",
            "access_token_in_launch_context",
            "command_authority",
            "provider_authority",
            "provider_call",
            "database_read",
            "database_write",
            "production",
            "deployment",
            "release",
        ],
        "candid_limit": (
            "This provider-free route-intercepted Chromium evidence proves "
            "the local Word taskpane launcher contract, date-before-projection "
            "ordering, and responsive request-input layout. It does not prove "
            "the Office dialog in an authenticated Word Online session, a "
            "provider path, production behavior, or authority over patient, "
            "appointment, clinical, command, or database data."
        ),
    }
    evidence["evidence_hash"] = canonical_hash(evidence)
    write_json(EVIDENCE, evidence)
    if not passed:
        raise RuntimeError(
            "hybrid contextual launch acceptance failed: "
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
                        "reception_one_word_hybrid_contextual_launch_failed"
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
                "launch_reference_date": evidence["launch_reference_date"],
                "provider_calls": evidence["provider_calls"],
                "database_writes": evidence["database_writes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
