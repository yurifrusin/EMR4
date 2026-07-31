"""Capture exact-raster, authored-synthetic Reception One visual evidence.

This runner exercises only the existing local authenticated fixture, read
surfaces and non-mutating slot-search proposal. It does not intercept routes,
activate a confirmation handoff or call a model/provider.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-visual-synthesis"
)
AUTH_URL = "http://127.0.0.1:3000/meta-grid-auth.html"
REFERENCE_DATE = "2026-07-27"
REQUEST = (
    "Show me all the available slots with Dr Shera for a half-hour appointment "
    "after 2 today"
)
VIEWPORTS = (
    ("desktop_landscape", 1440, 900),
    ("tablet_landscape", 1024, 768),
    ("tablet_portrait", 768, 1024),
    ("phone_portrait", 390, 844),
)


def _png_dimensions(payload: bytes) -> tuple[int, int]:
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("Screenshot is not a PNG.")
    return (
        int.from_bytes(payload[16:20], "big"),
        int.from_bytes(payload[20:24], "big"),
    )


def _open_selected_state(page: Page) -> None:
    page.goto(AUTH_URL, wait_until="domcontentloaded")
    page.wait_for_url("**/diary/diary.html?reference_date=2026-07-27**", timeout=20_000)
    page.get_by_test_id("meta-grid-launch-button").click()
    page.get_by_test_id("meta-grid-workspace").wait_for(state="visible")

    picker = page.locator("#diary-date-picker")
    picker.fill(REFERENCE_DATE)
    page.wait_for_function(
        "(expected) => document.querySelector('#diary-date-picker')?.value === expected",
        arg=REFERENCE_DATE,
    )

    page.get_by_label("Plain-language request or refinement", exact=True).fill(REQUEST)
    page.get_by_test_id("meta-grid-submit").click()
    page.get_by_test_id("meta-grid-slot").first.wait_for(state="visible", timeout=15_000)
    page.get_by_role(
        "button",
        name="Select 3:00 pm–3:30 pm with Alex Shera",
        exact=True,
    ).click()
    page.get_by_role("complementary", name="Selected time", exact=True).wait_for(
        state="visible"
    )
    page.locator("#bernie-meta-grid").evaluate("(element) => { element.scrollTop = 0; }")


def _metrics(page: Page, *, viewport_id: str) -> dict[str, object]:
    result = page.evaluate(
        """(viewportId) => {
          const host = document.getElementById("bernie-meta-grid");
          const cards = [...document.querySelectorAll('[data-testid="meta-grid-slot"]')];
          const visibleButtons = [
            ...document.querySelectorAll('#bernie-meta-grid button:not(:disabled)')
          ].filter((button) => {
            const style = getComputedStyle(button);
            const rect = button.getBoundingClientRect();
            return style.visibility !== "hidden" && style.display !== "none"
              && rect.width > 0 && rect.height > 0;
          });
          return {
            id: viewportId,
            width: window.innerWidth,
            height: window.innerHeight,
            page_horizontal_overflow_px:
              Math.max(0, document.body.scrollWidth - window.innerWidth),
            host_horizontal_overflow_px:
              Math.max(0, host.scrollWidth - host.clientWidth),
            enabled_controls_below_44px: visibleButtons
              .filter((button) => {
                const rect = button.getBoundingClientRect();
                return rect.width < 44 || rect.height < 44;
              })
              .map((button) => button.textContent.trim()),
            slot_count: cards.length,
            distinct_card_tops:
              new Set(cards.map((card) => Math.round(card.getBoundingClientRect().top))).size,
            selected_count:
              document.querySelectorAll(
                '[data-testid="meta-grid-slot"][aria-pressed="true"]'
              ).length,
            selection_panel_visible:
              Boolean(document.querySelector(".meta-grid-selection-panel")),
            appointment_write_authority:
              document.querySelector("#meta-grid-evidence-boundary")
                ?.textContent.includes("appointment write authority: false") === true,
          };
        }""",
        viewport_id,
    )
    assert result["page_horizontal_overflow_px"] == 0
    assert result["host_horizontal_overflow_px"] == 0
    assert result["enabled_controls_below_44px"] == []
    assert result["slot_count"] == 8
    assert result["distinct_card_tops"] == 8
    assert result["selected_count"] == 1
    assert result["selection_panel_visible"] is True
    assert result["appointment_write_authority"] is True
    return result


def _keyboard_and_escape(page: Page) -> dict[str, object]:
    selected = page.get_by_role(
        "button",
        name="Selected 3:00 pm–3:30 pm with Alex Shera",
        exact=True,
    )
    selected.press("ArrowDown")
    active_label = page.evaluate("document.activeElement?.getAttribute('aria-label')")
    assert active_label == "Select 3:15 pm–3:45 pm with Alex Shera"
    page.get_by_role(
        "button",
        name="Select 3:15 pm–3:45 pm with Alex Shera",
        exact=True,
    ).press("Enter")
    selected_label = page.locator(
        '[data-testid="meta-grid-slot"][aria-pressed="true"]'
    ).get_attribute("aria-label")
    scope = page.locator("#meta-grid-scope-summary").inner_text()
    assert selected_label == "Selected 3:15 pm–3:45 pm with Alex Shera"
    assert scope.endswith("· 3:15 pm selected")
    assert scope.count(" selected") == 1

    page.get_by_test_id("meta-grid-workspace").press("Escape")
    workspace_hidden = page.get_by_test_id("meta-grid-workspace").evaluate(
        "(element) => element.classList.contains('hidden')"
    )
    diary_visible = page.locator("#diary-grid-container").is_visible()
    assert workspace_hidden is True
    assert diary_visible is True
    return {
        "arrow_moved_to_next_candidate": True,
        "enter_selected_focused_candidate": True,
        "selection_suffix_not_accumulated": True,
        "escape_returned_to_ordinary_diary": True,
    }


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    viewports: list[dict[str, object]] = []
    screenshots: list[dict[str, object]] = []
    console_findings: list[str] = []
    page_errors: list[str] = []
    response_findings: list[dict[str, object]] = []
    network: list[tuple[str, str, str]] = []
    keyboard: dict[str, object] | None = None

    with sync_playwright() as playwright:
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
                    "console",
                    lambda message: console_findings.append(
                        f"{message.type}:{message.text}"
                    )
                    if message.type in {"warning", "error"}
                    else None,
                )
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.on(
                    "response",
                    lambda response: response_findings.append(
                        {
                            "status": response.status,
                            "method": response.request.method.upper(),
                            "host": urlsplit(response.url).hostname or "",
                            "path": urlsplit(response.url).path,
                        }
                    )
                    if response.status >= 400
                    else None,
                )
                page.on(
                    "request",
                    lambda request: network.append(
                        (
                            request.method.upper(),
                            urlsplit(request.url).hostname or "",
                            urlsplit(request.url).path,
                        )
                    ),
                )
                _open_selected_state(page)
                viewports.append(_metrics(page, viewport_id=viewport_id))

                filename = (
                    f"{viewport_id.replace('_', '-')}-selected-{width}x{height}.png"
                )
                payload = page.screenshot(
                    path=str(OUTPUT / filename),
                    full_page=False,
                )
                observed_width, observed_height = _png_dimensions(payload)
                assert (observed_width, observed_height) == (width, height)
                screenshots.append(
                    {
                        "file": filename,
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "width": observed_width,
                        "height": observed_height,
                        "bytes": len(payload),
                    }
                )
                if viewport_id == "desktop_landscape":
                    keyboard = _keyboard_and_escape(page)
                context.close()
        finally:
            browser.close()

    forbidden_hosts = sorted(
        {
            host
            for _method, host, _path in network
            if host not in {"127.0.0.1", "localhost"}
        }
    )
    request_counts = Counter((method, path) for method, _host, path in network)
    network_manifest = [
        {"method": method, "path": path, "count": count}
        for (method, path), count in sorted(request_counts.items())
    ]
    assert forbidden_hosts == []
    assert not any("/confirm" in path or "/sessions" in path for _, path in request_counts)
    expected_default_off_probes = [
        finding
        for finding in response_findings
        if finding
        == {
            "status": 404,
            "method": "GET",
            "host": "localhost",
            "path": "/api/v1/diary/events/committed",
        }
    ]
    unexpected_responses = [
        finding
        for finding in response_findings
        if finding not in expected_default_off_probes
    ]
    expected_console_message = (
        "error:Failed to load resource: the server responded with a status of 404 "
        "(Not Found)"
    )
    unexpected_console = [
        finding
        for finding in console_findings
        if finding != expected_console_message
    ]
    assert len(expected_default_off_probes) == len(VIEWPORTS)
    assert unexpected_responses == [], unexpected_responses
    assert len(console_findings) == len(expected_default_off_probes)
    assert unexpected_console == [], unexpected_console
    assert page_errors == [], page_errors
    assert keyboard is not None

    evidence = {
        "schema_version": "reception_one.visual_synthesis.browser_evidence.v1",
        "result": "browser_pass",
        "evidence_mode": "authenticated_local_authored_synthetic_fixture_browser",
        "route_interception": False,
        "api_interception": False,
        "reference_date": REFERENCE_DATE,
        "request_class": "authored_synthetic",
        "viewports": viewports,
        "screenshots": screenshots,
        "keyboard": keyboard,
        "network": {
            "method_path_counts": network_manifest,
            "forbidden_external_hosts": forbidden_hosts,
            "confirmation_or_session_routes_observed": False,
            "expected_default_off_committed_event_feed_404_count": len(
                expected_default_off_probes
            ),
            "unexpected_http_responses": unexpected_responses,
        },
        "authority": {
            "appointment_write_authority": False,
            "proposal_handoff_activated": False,
            "confirmation_control_activated": False,
            "provider_runtime_in_ui": False,
            "operational_receipt_produced": False,
        },
        "browser_console_expected_default_off_probe_count": len(console_findings),
        "browser_console_unexpected_warnings_or_errors": unexpected_console,
        "browser_page_errors": page_errors,
        "database_readback_performed": False,
        "explicit_exclusions": [
            "No provider call from the UI",
            "No appointment confirmation",
            "No command-shaped release",
            "No production, deployment or release claim",
            "No representative-staff usability claim",
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
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
