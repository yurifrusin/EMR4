#!/usr/bin/env python3
"""Verify content-aware Reception One sizing and bounded canvas scrolling."""

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
    / "reception-one-bureau-cost-bounded-occupied-retry"
)
EVIDENCE = OUTPUT / "projection-overflow-evidence.json"
DESKTOP_SCREENSHOT = OUTPUT / "projection-overflow-desktop.png"
BOUNDED_SCREENSHOT = OUTPUT / "projection-overflow-bounded-scroll.png"
REFERENCE_DATE = "2026-07-27"
REQUEST = "Find Dr Shera availability after 2 pm"
PROVIDER_HOST_FRAGMENTS = (
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "api.openai.com",
    "deepseek.com",
    "terra",
)


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
            raise RuntimeError("projection evidence server did not stop")


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


def open_availability(page: Page, base_url: str) -> None:
    page.goto(
        (
            f"{base_url}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            f"&reference_date={REFERENCE_DATE}"
            "&projection_overflow_acceptance=true"
        ),
        wait_until="domcontentloaded",
    )
    page.locator("#bernie-meta-grid:not(.hidden)").wait_for(
        state="visible"
    )
    request = page.get_by_placeholder(
        "What would you like to find or prepare?",
        exact=True,
    )
    request.fill(REQUEST)
    page.get_by_role(
        "button",
        name="Find or prepare",
        exact=True,
    ).click()
    page.wait_for_function(
        "() => document.getElementById('bernie-meta-grid')"
        "?.dataset.family === 'availability_slots'"
    )
    page.locator('[data-testid="meta-grid-slot"]').first.wait_for(
        state="visible"
    )


def layout_metrics(page: Page, *, scroll_to_end: bool) -> dict[str, Any]:
    return page.evaluate(
        """(scrollToEnd) => {
          const shell = document.querySelector(".meta-grid-shell");
          const canvas = document.querySelector(".meta-grid-canvas");
          const form = document.querySelector(".meta-grid-request-form");
          const slots = [
            ...document.querySelectorAll('[data-testid="meta-grid-slot"]')
          ];
          if (scrollToEnd) canvas.scrollTop = canvas.scrollHeight;
          const shellRect = shell.getBoundingClientRect();
          const canvasRect = canvas.getBoundingClientRect();
          const formRect = form.getBoundingClientRect();
          const firstRect = slots[0]?.getBoundingClientRect();
          const lastRect = slots.at(-1)?.getBoundingClientRect();
          return {
            viewport: { width: innerWidth, height: innerHeight },
            family:
              document.getElementById("bernie-meta-grid")?.dataset.family,
            slot_count: slots.length,
            shell: {
              top: Math.round(shellRect.top),
              bottom: Math.round(shellRect.bottom),
              height: Math.round(shellRect.height),
            },
            canvas: {
              top: Math.round(canvasRect.top),
              bottom: Math.round(canvasRect.bottom),
              client_height: canvas.clientHeight,
              scroll_height: canvas.scrollHeight,
              scroll_top: canvas.scrollTop,
              overflow_y: getComputedStyle(canvas).overflowY,
              scrollbar_color: getComputedStyle(canvas).scrollbarColor,
              scrollbar_gutter: getComputedStyle(canvas).scrollbarGutter,
            },
            first_slot_visible:
              Boolean(firstRect)
              && firstRect.top >= canvasRect.top - 1
              && firstRect.bottom <= canvasRect.bottom + 1,
            last_slot_visible:
              Boolean(lastRect)
              && lastRect.top >= canvasRect.top - 1
              && lastRect.bottom <= canvasRect.bottom + 1,
            form_visible:
              formRect.top >= 0 && formRect.bottom <= innerHeight,
            canvas_clear_of_form:
              canvasRect.bottom <= formRect.top + 1,
            horizontal_overflow_px:
              Math.max(0, document.documentElement.scrollWidth - innerWidth),
          };
        }""",
        scroll_to_end,
    )


def run() -> dict[str, Any]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    network: list[dict[str, str]] = []
    console_errors: list[str] = []
    blocked_external_hosts: set[str] = set()
    with static_server() as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        page = context.new_page()

        def record_request(route: Route) -> None:
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
            if hostname not in {"127.0.0.1", "localhost", ""}:
                blocked_external_hosts.add(hostname)
                route.abort()
            else:
                route.continue_()

        page.route("**/*", record_request)
        page.on(
            "console",
            lambda message: (
                console_errors.append(message.text)
                if message.type == "error"
                and "office.js" not in message.text.lower()
                else None
            ),
        )
        open_availability(page, base_url)
        desktop_initial = layout_metrics(page, scroll_to_end=False)
        page.screenshot(path=str(DESKTOP_SCREENSHOT), full_page=True)
        desktop_end = layout_metrics(page, scroll_to_end=True)

        page.set_viewport_size({"width": 1024, "height": 650})
        bounded_initial = layout_metrics(page, scroll_to_end=False)
        bounded_end = layout_metrics(page, scroll_to_end=True)
        page.screenshot(path=str(BOUNDED_SCREENSHOT), full_page=True)
        context.close()
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
    relevant_console_errors = [
        message
        for message in console_errors
        if message != "Failed to load resource: net::ERR_FAILED"
    ]
    checks = {
        "availability_family_rendered": (
            desktop_initial["family"] == "availability_slots"
        ),
        "result_cohort_is_scroll_worthy": (
            desktop_initial["slot_count"] >= 8
        ),
        "desktop_projection_grew_beyond_old_690px_cap": (
            690 < desktop_initial["shell"]["height"] <= 760
        ),
        "desktop_projection_within_viewport": (
            0 <= desktop_initial["shell"]["top"]
            < desktop_initial["shell"]["bottom"]
            <= desktop_initial["viewport"]["height"]
        ),
        "canvas_owns_vertical_overflow": (
            desktop_initial["canvas"]["overflow_y"] == "auto"
            and desktop_initial["canvas"]["scrollbar_color"]
            != "auto"
            and desktop_initial["canvas"]["scrollbar_gutter"] == "stable"
        ),
        "desktop_scroll_is_available_when_needed": (
            desktop_initial["canvas"]["scroll_height"]
            > desktop_initial["canvas"]["client_height"]
        ),
        "desktop_last_result_reachable": (
            desktop_end["last_slot_visible"] is True
            and desktop_end["canvas"]["scroll_top"] > 0
        ),
        "bounded_scroll_is_available": (
            bounded_initial["canvas"]["scroll_height"]
            > bounded_initial["canvas"]["client_height"]
        ),
        "bounded_last_result_reachable": (
            bounded_end["last_slot_visible"] is True
            and bounded_end["canvas"]["scroll_top"] > 0
        ),
        "composer_remains_visible_and_separate": (
            desktop_end["form_visible"] is True
            and desktop_end["canvas_clear_of_form"] is True
            and bounded_end["form_visible"] is True
            and bounded_end["canvas_clear_of_form"] is True
        ),
        "no_horizontal_overflow": (
            desktop_end["horizontal_overflow_px"] == 0
            and bounded_end["horizontal_overflow_px"] == 0
        ),
        "no_provider_request": provider_hosts == [],
        "only_office_bootstrap_was_blocked": (
            blocked_external_hosts == {"appsforoffice.microsoft.com"}
        ),
        "no_relevant_console_error": relevant_console_errors == [],
    }
    passed = all(checks.values())
    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.projection_overflow_acceptance.v1"
        ),
        "result": (
            "reception_one_projection_overflow_acceptance_pass"
            if passed
            else "reception_one_projection_overflow_acceptance_failed"
        ),
        "data_class": "authored_synthetic",
        "browser_path": (
            "repository_playwright_after_in_app_browser_dom_"
            "inspection_timeout"
        ),
        "request_text_retained": False,
        "request_hash": canonical_hash({"request": REQUEST}),
        "checks": checks,
        "desktop_initial": desktop_initial,
        "desktop_after_scroll": desktop_end,
        "bounded_initial": bounded_initial,
        "bounded_after_scroll": bounded_end,
        "provider_hosts": provider_hosts,
        "provider_calls": 0,
        "credential_reads": 0,
        "database_reads": 0,
        "database_writes": 0,
        "blocked_external_hosts": sorted(blocked_external_hosts),
        "expected_aborted_resource_error_count": (
            len(console_errors) - len(relevant_console_errors)
        ),
        "relevant_console_errors": relevant_console_errors,
        "network_request_count": len(network),
        "screenshots": [
            DESKTOP_SCREENSHOT.relative_to(ROOT).as_posix(),
            BOUNDED_SCREENSHOT.relative_to(ROOT).as_posix(),
        ],
        "candid_limit": (
            "This provider-free fixture proves only projection sizing, "
            "bounded internal scrolling and result reachability in Chromium. "
            "It does not prove provider, production or clinical behavior."
        ),
    }
    evidence["evidence_hash"] = canonical_hash(evidence)
    write_json(EVIDENCE, evidence)
    if not passed:
        raise RuntimeError(
            "projection overflow acceptance failed: "
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
                        "reception_one_projection_overflow_"
                        "acceptance_failed"
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
                "slot_count": evidence["desktop_initial"]["slot_count"],
                "desktop_shell_height": (
                    evidence["desktop_initial"]["shell"]["height"]
                ),
                "provider_calls": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
