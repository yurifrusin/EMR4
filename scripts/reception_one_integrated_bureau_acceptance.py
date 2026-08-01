#!/usr/bin/env python3
"""Capture provider-free authored-synthetic Reception One Bureau evidence."""

from __future__ import annotations

import hashlib
import json
import threading
from collections import Counter
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator
from urllib.parse import urlsplit

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-integrated-bureau"
)
REFERENCE_DATE = "2026-07-27"
TARGET_DATE = "2026-07-28"
REQUEST = "Show Dr Shera tomorrow"
REFERENCE_PRESENTATION_REQUEST = "Show Margaret Thompson's upcoming appointments"
VIEWPORTS = (
    ("desktop", 1440, 900),
    ("tablet", 834, 1112),
    ("phone", 390, 844),
)
PROVIDER_HOST_FRAGMENTS = (
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "api.openai.com",
    "deepseek.com",
    "terra",
)
EXPECTED_OFFICE_WARNING_PREFIX = (
    "warning:A parser-blocking, cross site (i.e. different eTLD+1) script, "
    "https://appsforoffice.microsoft.com/lib/1/hosted/office.js"
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


@contextmanager
def static_server() -> Iterator[str]:
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(DOCS), **kwargs
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
            raise RuntimeError("static evidence server did not stop")


def png_dimensions(payload: bytes) -> tuple[int, int]:
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("Screenshot is not a PNG")
    return (
        int.from_bytes(payload[16:20], "big"),
        int.from_bytes(payload[20:24], "big"),
    )


def open_bureau(page: Page, base_url: str) -> None:
    page.goto(
        (
            f"{base_url}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            f"&reference_date={REFERENCE_DATE}"
        ),
        wait_until="domcontentloaded",
    )
    page.locator("#bernie-meta-grid:not(.hidden)").wait_for(state="visible")
    page.locator("#meta-grid-bureau-status").wait_for(state="attached")
    page.wait_for_function(
        "(expected) => document.querySelector('#diary-date-label')?.textContent?.trim() === expected",
        arg="Monday 27 July 2026",
    )
    page.get_by_placeholder(
        "What would you like to find or prepare?", exact=True
    ).fill(REFERENCE_PRESENTATION_REQUEST)
    page.get_by_role("button", name="Find or prepare", exact=True).click()
    page.wait_for_function(
        "() => document.getElementById('bernie-meta-grid')?.dataset.family === 'patient_timeline'"
    )
    page.wait_for_function(
        "() => document.querySelectorAll('.meta-grid-appointment-card').length > 0"
    )


def layout_metrics(page: Page, viewport_id: str) -> dict[str, object]:
    metrics = page.evaluate(
        """(viewportId) => {
          const host = document.getElementById("bernie-meta-grid");
          const shell = host.querySelector(".meta-grid-shell");
          const diary = document.getElementById("diary-grid-container");
          const close = document.getElementById("meta-grid-close");
          const returnButton = document.getElementById("meta-grid-return");
          const shellRect = shell.getBoundingClientRect();
          const closeRect = close.getBoundingClientRect();
          const returnRect = returnButton.getBoundingClientRect();
          return {
            id: viewportId,
            width: innerWidth,
            height: innerHeight,
            reference_date_label:
              document.getElementById("diary-date-label")?.textContent?.trim(),
            bureau_status:
              document.getElementById("meta-grid-bureau-status")?.textContent?.trim(),
            aria_modal: host.getAttribute("aria-modal"),
            diary_visible: getComputedStyle(diary).display !== "none",
            visible_bureau_copy_contains_grid:
              host.innerText.toLowerCase().includes("grid"),
            horizontal_overflow_px:
              Math.max(0, document.documentElement.scrollWidth - innerWidth),
            shell_scroll_top: shell.scrollTop,
            shell: {
              x: Math.round(shellRect.x),
              y: Math.round(shellRect.y),
              width: Math.round(shellRect.width),
              height: Math.round(shellRect.height),
              right: Math.round(shellRect.right),
              bottom: Math.round(shellRect.bottom),
            },
            close_control: {
              width: Math.round(closeRect.width),
              height: Math.round(closeRect.height),
            },
            return_control: {
              width: Math.round(returnRect.width),
              height: Math.round(returnRect.height),
            },
          };
        }""",
        viewport_id,
    )
    assert metrics["reference_date_label"] == "Monday 27 July 2026"
    assert metrics["bureau_status"] == "Checked against the Diary"
    assert metrics["aria_modal"] == "false"
    assert metrics["diary_visible"] is True
    assert metrics["visible_bureau_copy_contains_grid"] is False
    assert metrics["horizontal_overflow_px"] == 0
    assert metrics["shell_scroll_top"] == 0
    shell = metrics["shell"]
    assert 0 <= shell["x"] < shell["right"] <= metrics["width"]
    assert 0 <= shell["y"] < shell["bottom"] <= metrics["height"]
    for control in ("close_control", "return_control"):
        assert metrics[control]["width"] >= 44
        assert metrics[control]["height"] >= 44
    return metrics


def date_first_flow(page: Page) -> dict[str, object]:
    page.get_by_placeholder(
        "What would you like to find or prepare?", exact=True
    ).fill(REQUEST)
    page.get_by_role("button", name="Find or prepare", exact=True).click()
    page.wait_for_function(
        "(expected) => document.querySelector('#diary-date-label')?.textContent?.trim() === expected",
        arg="Tuesday 28 July 2026",
    )
    page.wait_for_function(
        "() => document.querySelector('#meta-grid-bureau-status')?.textContent?.trim() === 'Checked against the Diary'"
    )
    result = page.evaluate(
        """() => {
          const shell = document.querySelector(".meta-grid-shell");
          const bar = document.querySelector(".meta-grid-window-bar");
          const shellRect = shell.getBoundingClientRect();
          const barRect = bar.getBoundingClientRect();
          return {
            diary_date: document.getElementById("diary-date-label")?.textContent?.trim(),
            scope: document.getElementById("meta-grid-scope-summary")?.textContent?.trim(),
            bureau_status:
              document.getElementById("meta-grid-bureau-status")?.textContent?.trim(),
            shell_scroll_top: shell.scrollTop,
            titlebar_inside_shell:
              barRect.top >= shellRect.top && barRect.bottom <= shellRect.bottom,
            active_element: document.activeElement?.id,
          };
        }"""
    )
    assert result["diary_date"] == "Tuesday 28 July 2026"
    assert "Tue, 28 July 2026" in result["scope"]
    assert result["bureau_status"] == "Checked against the Diary"
    assert result["shell_scroll_top"] == 0
    assert result["titlebar_inside_shell"] is True
    assert result["active_element"] == "meta-grid-canvas"

    page.locator("#meta-grid-return").click()
    page.wait_for_function(
        "() => document.getElementById('bernie-meta-grid')?.classList.contains('hidden')"
    )
    focus_after_return = page.evaluate("document.activeElement?.id")
    assert focus_after_return == "btn-meta-grid-launch"

    page.get_by_role("button", name="Project view", exact=True).click()
    page.get_by_placeholder(
        "What would you like to find or prepare?", exact=True
    ).press("Escape")
    page.wait_for_function(
        "() => document.getElementById('bernie-meta-grid')?.classList.contains('hidden')"
    )
    focus_after_escape = page.evaluate("document.activeElement?.id")
    assert focus_after_escape == "btn-meta-grid-launch"
    return {
        **result,
        "focus_after_return": focus_after_return,
        "focus_after_escape": focus_after_escape,
        "date_turn_direction": "forward",
        "date_set_before_projection": True,
    }


def expanded_bureau_flow(page: Page, compact_width: int) -> dict[str, object]:
    control = page.locator("#meta-grid-expand")
    control.click()
    page.wait_for_function(
        "() => document.getElementById('bernie-meta-grid')?.classList.contains('is-expanded')"
    )
    expanded = page.evaluate(
        """() => {
          const host = document.getElementById("bernie-meta-grid");
          const shell = host.querySelector(".meta-grid-shell");
          const rail = host.querySelector(".meta-grid-rail");
          const rect = shell.getBoundingClientRect();
          return {
            aria_pressed:
              document.getElementById("meta-grid-expand")?.getAttribute("aria-pressed"),
            accessible_name:
              document.getElementById("meta-grid-expand")?.getAttribute("aria-label"),
            shell_width: Math.round(rect.width),
            shell_right: Math.round(rect.right),
            rail_visible: getComputedStyle(rail).display !== "none",
            diary_visible:
              getComputedStyle(document.getElementById("diary-grid-container")).display !== "none",
            horizontal_overflow_px:
              Math.max(0, document.documentElement.scrollWidth - innerWidth),
          };
        }"""
    )
    assert expanded["aria_pressed"] == "true"
    assert expanded["accessible_name"] == "Return to compact view"
    assert expanded["shell_width"] > compact_width
    assert expanded["shell_right"] <= 1440
    assert expanded["rail_visible"] is True
    assert expanded["diary_visible"] is True
    assert expanded["horizontal_overflow_px"] == 0

    control.click()
    page.wait_for_function(
        "() => !document.getElementById('bernie-meta-grid')?.classList.contains('is-expanded')"
    )
    collapsed = page.evaluate(
        """() => {
          const control = document.getElementById("meta-grid-expand");
          const shell = document.querySelector(".meta-grid-shell");
          return {
            aria_pressed: control?.getAttribute("aria-pressed"),
            accessible_name: control?.getAttribute("aria-label"),
            shell_width: Math.round(shell.getBoundingClientRect().width),
            rail_visible:
              getComputedStyle(document.querySelector(".meta-grid-rail")).display !== "none",
          };
        }"""
    )
    assert collapsed == {
        "aria_pressed": "false",
        "accessible_name": "Expand Bureau",
        "shell_width": compact_width,
        "rail_visible": False,
    }
    return {"expanded": expanded, "collapsed": collapsed}


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    screenshots: list[dict[str, object]] = []
    viewports: list[dict[str, object]] = []
    requests: list[tuple[str, str, str]] = []
    console_findings: list[str] = []
    page_errors: list[str] = []
    date_flow: dict[str, object] | None = None
    expanded_flow: dict[str, object] | None = None

    with static_server() as base_url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for viewport_id, width, height in VIEWPORTS:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    locale="en-AU",
                    timezone_id="Australia/Brisbane",
                )
                page = context.new_page()
                page.on(
                    "request",
                    lambda request: requests.append(
                        (
                            request.method.upper(),
                            urlsplit(request.url).hostname or "",
                            urlsplit(request.url).path,
                        )
                    ),
                )
                page.on(
                    "console",
                    lambda message: console_findings.append(
                        f"{message.type}:{message.text}"
                    )
                    if message.type in {"warning", "error"}
                    else None,
                )
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                open_bureau(page, base_url)
                viewports.append(layout_metrics(page, viewport_id))

                filename = f"{viewport_id}-{width}x{height}.png"
                payload = page.screenshot(path=str(OUTPUT / filename), full_page=False)
                assert png_dimensions(payload) == (width, height)
                screenshots.append(
                    {
                        "file": filename,
                        "width": width,
                        "height": height,
                        "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    }
                )
                if viewport_id == "desktop":
                    compact_width = viewports[-1]["shell"]["width"]
                    expanded_flow = expanded_bureau_flow(page, compact_width)
                    page.locator("#meta-grid-expand").click()
                    page.wait_for_function(
                        "() => document.getElementById('bernie-meta-grid')?.classList.contains('is-expanded')"
                    )
                    expanded_filename = "desktop-expanded-1440x900.png"
                    expanded_payload = page.screenshot(
                        path=str(OUTPUT / expanded_filename),
                        full_page=False,
                    )
                    assert png_dimensions(expanded_payload) == (width, height)
                    screenshots.append(
                        {
                            "file": expanded_filename,
                            "width": width,
                            "height": height,
                            "bytes": len(expanded_payload),
                            "sha256": hashlib.sha256(expanded_payload).hexdigest(),
                        }
                    )
                    page.locator("#meta-grid-expand").click()
                    page.wait_for_function(
                        "() => !document.getElementById('bernie-meta-grid')?.classList.contains('is-expanded')"
                    )
                    date_flow = date_first_flow(page)
                context.close()
        finally:
            browser.close()

    provider_hosts = sorted(
        {
            host
            for _method, host, _path in requests
            if any(fragment in host for fragment in PROVIDER_HOST_FRAGMENTS)
        }
    )
    expected_office_warnings = [
        finding
        for finding in console_findings
        if finding.startswith(EXPECTED_OFFICE_WARNING_PREFIX)
    ]
    unexpected_console = [
        finding
        for finding in console_findings
        if not finding.startswith(EXPECTED_OFFICE_WARNING_PREFIX)
    ]
    assert provider_hosts == []
    assert page_errors == [], page_errors
    assert unexpected_console == [], unexpected_console
    assert date_flow is not None
    assert expanded_flow is not None

    request_counts = Counter((method, host, path) for method, host, path in requests)
    evidence = {
        "schema_version": "reception.one.integrated-bureau.browser-evidence.v1",
        "result": "browser_pass",
        "evidence_mode": "authored_synthetic_client_fixture_browser",
        "reference_date": REFERENCE_DATE,
        "target_date": TARGET_DATE,
        "request": REQUEST,
        "viewports": viewports,
        "date_first_flow": date_flow,
        "expanded_bureau_flow": expanded_flow,
        "screenshots": screenshots,
        "network": {
            "provider_hosts_observed": provider_hosts,
            "requests": [
                {"method": method, "host": host, "path": path, "count": count}
                for (method, host, path), count in sorted(request_counts.items())
            ],
        },
        "expected_office_bootstrap_warning_count": len(expected_office_warnings),
        "console_warnings_or_errors": unexpected_console,
        "page_errors": page_errors,
        "authority": {
            "provider_runtime_in_ui": False,
            "appointment_write_authority": False,
            "command_authority": False,
            "product_delivery_enabled": False,
        },
        "explicit_exclusions": [
            "No provider call",
            "No credential discovery or refresh",
            "No API interception",
            "No database or product data",
            "No appointment mutation",
            "No representative usability claim",
            "No production, deployment or release claim",
        ],
    }
    (OUTPUT / "browser-acceptance-evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "screenshots": len(screenshots),
                "viewports": len(viewports),
                "provider_hosts_observed": provider_hosts,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
