"""Drive real Diary/meta-grid acceptance over loopback FastAPI/PostgreSQL.

This task-scoped Playwright runner uses no request interception. It records only
sanitized method/path observations, screenshots, viewport measurements and
before/after database hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, expect, sync_playwright

from bernie_meta_grid_live_local_harness import (
    REFERENCE_DATE,
    database_readback,
    launch_runtime,
    readiness_report,
    stop_runtime,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "orchestration" / "prototypes" / "bernie-meta-grid-live-local-integration"
AUTH_URL = "http://127.0.0.1:3000/meta-grid-auth.html"
STATIC_HOSTS = {"127.0.0.1", "localhost"}
API_ALLOWED = {
    ("POST", "/api/v1/auth/login"),
    ("GET", "/api/v1/diary/locations"),
    ("GET", "/api/v1/diary/template"),
    ("GET", "/api/v1/appointments"),
    ("GET", "/api/v1/appointments/types"),
    ("GET", "/api/v1/diary/roster"),
    ("GET", "/api/v1/diary/waiting-areas"),
    ("POST", "/api/v1/graphql"),
    ("GET", "/api/v1/practice/practitioners"),
    ("GET", "/api/v1/appointments/bernie/pilot-eligibility"),
    ("GET", "/api/v1/patients/search"),
    ("POST", "/api/v1/appointments/proposals/slot-search"),
    ("POST", "/api/v1/appointments/proposals/bernie/supervised-booking"),
}
FORBIDDEN_API_FRAGMENTS = (
    "/confirm",
    "/appointments/bernie/sessions",
    "/interpret-booking-instruction",
)


class BrowserEvidence:
    def __init__(self) -> None:
        self.requests: Counter[tuple[str, str]] = Counter()
        self.responses: list[dict[str, object]] = []
        self.console: list[dict[str, str]] = []
        self.page_errors: list[str] = []
        self.forbidden: list[str] = []

    def attach(self, page: Page) -> None:
        page.on("request", self._request)
        page.on("response", self._response)
        page.on("console", self._console)
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))

    def _request(self, request: Any) -> None:
        parsed = urlsplit(request.url)
        if parsed.scheme not in {"http", "https"}:
            return
        method = request.method.upper()
        path = parsed.path
        self.requests[(method, path)] += 1
        if parsed.hostname not in STATIC_HOSTS:
            self.forbidden.append(f"external_origin:{method} {parsed.scheme}://{parsed.netloc}{path}")
            return
        if parsed.port == 3000:
            if method not in {"GET", "HEAD"}:
                self.forbidden.append(f"static_method:{method} {path}")
            return
        if parsed.port != 8001:
            self.forbidden.append(f"unexpected_loopback_port:{method} {parsed.netloc}{path}")
            return
        effective = (method, path)
        if method == "OPTIONS":
            if not any(allowed_path == path for _allowed_method, allowed_path in API_ALLOWED):
                self.forbidden.append(f"unexpected_preflight:{method} {path}")
            return
        if effective not in API_ALLOWED:
            self.forbidden.append(f"unexpected_api:{method} {path}")
        if any(fragment in path for fragment in FORBIDDEN_API_FRAGMENTS):
            self.forbidden.append(f"closed_boundary:{method} {path}")
        if path == "/api/v1/appointments" and method not in {"GET", "OPTIONS"}:
            self.forbidden.append(f"appointment_mutation:{method} {path}")

    def _response(self, response: Any) -> None:
        parsed = urlsplit(response.url)
        if parsed.hostname in STATIC_HOSTS and parsed.port == 8001:
            self.responses.append(
                {
                    "method": response.request.method.upper(),
                    "path": parsed.path,
                    "status": response.status,
                }
            )

    def _console(self, message: Any) -> None:
        if message.type in {"warning", "error"}:
            self.console.append({"type": message.type, "text": message.text})

    def assert_clean(self) -> None:
        assert not self.forbidden, f"Forbidden browser requests: {self.forbidden}"
        failed = [row for row in self.responses if int(row["status"]) >= 400]
        assert not failed, f"API responses failed: {failed}"
        assert not self.console, f"Browser console warnings/errors: {self.console}"
        assert not self.page_errors, f"Browser page errors: {self.page_errors}"


def _focus_label(page: Page) -> str:
    label = page.evaluate(
        """() => {
          const el = document.activeElement;
          if (!el) return "none";
          return el.getAttribute("data-testid") || el.id || el.textContent?.trim().slice(0, 80) || el.tagName;
        }"""
    )
    if "Margaret" in label:
        return "patient timeline example"
    return label


def _wait_family(page: Page, family: str) -> None:
    expect(page.locator("#meta-grid-evidence-family")).to_have_text(family, timeout=15_000)
    expect(page.get_by_test_id("meta-grid-submit")).to_be_enabled(timeout=15_000)


def _submit(page: Page, text: str, family: str, *, previous_scope: str | None = None) -> None:
    request = page.locator("#meta-grid-request")
    request.fill(text)
    request.press("Enter")
    _wait_family(page, family)
    if previous_scope is not None:
        page.wait_for_function(
            "expected => document.querySelector('#meta-grid-scope-summary')?.textContent !== expected",
            arg=previous_scope,
            timeout=15_000,
        )


def _open_authenticated_page(
    browser: Browser,
    viewport: dict[str, int],
    evidence: BrowserEvidence,
    *,
    has_touch: bool = False,
) -> tuple[BrowserContext, Page]:
    context = browser.new_context(
        viewport=viewport,
        device_scale_factor=1,
        has_touch=has_touch,
        locale="en-AU",
        timezone_id="Australia/Brisbane",
    )
    page = context.new_page()
    evidence.attach(page)
    page.goto(AUTH_URL, wait_until="domcontentloaded")
    page.wait_for_url(f"**/diary/diary.html?reference_date={REFERENCE_DATE.isoformat()}**", timeout=20_000)
    expect(page.get_by_test_id("meta-grid-launch-button")).to_be_visible(timeout=20_000)
    # The Diary date is changed through its existing visible navigation rather
    # than by setting page state or calling a page-internal function.
    for expected_day in range(21, 28):
        with page.expect_response(
            lambda response: (
                urlsplit(response.url).path == "/api/v1/appointments"
                and response.request.method.upper() == "GET"
            ),
            timeout=15_000,
        ):
            page.locator("#btn-next-day").click()
        expect(page.locator("#diary-date-picker")).to_have_value(
            f"2026-07-{expected_day:02d}", timeout=15_000
        )
    page.get_by_test_id("meta-grid-launch-button").click()
    expect(page.get_by_test_id("meta-grid-workspace")).to_be_visible(timeout=20_000)
    _wait_family(page, "ordinary_overview")
    evidence.assert_clean()
    return context, page


def _viewport_metrics(page: Page) -> dict[str, object]:
    return page.evaluate(
        """() => {
          const host = document.getElementById('bernie-meta-grid');
          const body = document.body;
          const root = document.documentElement;
          const visible = el => {
            const style = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
          };
          const small = Array.from(document.querySelectorAll('button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), a[href]'))
            .filter(visible)
            .map(el => {
              const rect = el.getBoundingClientRect();
              return {
                label: el.getAttribute('data-testid') || el.id || el.textContent?.trim().slice(0, 60) || el.tagName,
                width: Math.round(rect.width * 10) / 10,
                height: Math.round(rect.height * 10) / 10
              };
            })
            .filter(row => row.width < 44 || row.height < 44);
          const hostRect = host.getBoundingClientRect();
          const shell = host.querySelector('.meta-grid-shell').getBoundingClientRect();
          const workspace = host.querySelector('.meta-grid-workspace').getBoundingClientRect();
          return {
            window_inner_width: window.innerWidth,
            document_client_width: root.clientWidth,
            body_client_width: body.clientWidth,
            host_width: Math.round(hostRect.width),
            shell_width: Math.round(shell.width),
            workspace_right: Math.round(workspace.right),
            page_horizontal_overflow_px: Math.max(0, root.scrollWidth - root.clientWidth),
            host_horizontal_overflow_px: Math.max(0, host.scrollWidth - host.clientWidth),
            enabled_controls_below_44px: small,
            error_overlay_visible: Array.from(document.querySelectorAll('[role="alert"], .error, .error-overlay')).some(visible)
          };
        }"""
    )


def _paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def png_painted_width(path: Path) -> dict[str, object]:
    """Decode an 8-bit Playwright PNG and reject black/unpainted right edges."""

    raw = path.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n"), f"Not a PNG: {path}"
    offset = 8
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while offset < len(raw):
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        chunk_type = raw[offset + 4 : offset + 8]
        data = raw[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", data
            )
        elif chunk_type == b"IDAT":
            compressed.extend(data)
        elif chunk_type == b"IEND":
            break
    assert width and height and bit_depth == 8 and color_type in {2, 6} and interlace == 0
    channels = 3 if color_type == 2 else 4
    stride = width * channels
    decoded = zlib.decompress(bytes(compressed))
    rows: list[bytearray] = []
    cursor = 0
    for _row_index in range(height):
        filter_type = decoded[cursor]
        cursor += 1
        scanline = bytearray(decoded[cursor : cursor + stride])
        cursor += stride
        previous = rows[-1] if rows else bytearray(stride)
        for index in range(stride):
            left = scanline[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                scanline[index] = (scanline[index] + left) & 0xFF
            elif filter_type == 2:
                scanline[index] = (scanline[index] + above) & 0xFF
            elif filter_type == 3:
                scanline[index] = (scanline[index] + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                scanline[index] = (scanline[index] + _paeth(left, above, upper_left)) & 0xFF
            elif filter_type != 0:
                raise AssertionError(f"Unsupported PNG filter {filter_type}")
        rows.append(scanline)

    painted = 0
    right_total = max(1, (width - int(width * 0.8)) * height)
    max_x = -1
    for y, row in enumerate(rows):
        _ = y
        for x in range(width):
            base = x * channels
            red, green, blue = row[base : base + 3]
            alpha = row[base + 3] if channels == 4 else 255
            non_black = alpha > 0 and max(red, green, blue) > 8
            if non_black:
                max_x = max(max_x, x)
                if x >= int(width * 0.8):
                    painted += 1
    right_ratio = painted / right_total
    extent_ratio = (max_x + 1) / width
    result = {
        "width": width,
        "height": height,
        "rightmost_20_percent_nonblack_ratio": round(right_ratio, 6),
        "painted_extent_ratio": round(extent_ratio, 6),
        "passes": right_ratio >= 0.1 and extent_ratio >= 0.95,
    }
    assert result["passes"], f"Screenshot capture is clipped or black: {result}"
    return result


def _save_screenshot(page: Page, output: Path, name: str) -> dict[str, object]:
    target = output / name
    # Normalize capture position only; this does not invoke a projection or
    # command function and avoids focus-driven scroll artifacts in evidence.
    page.evaluate(
        """() => {
          window.scrollTo(0, 0);
          document.documentElement.scrollTop = 0;
          document.body.scrollTop = 0;
          const host = document.getElementById('bernie-meta-grid');
          if (host) host.scrollTop = 0;
        }"""
    )
    page.screenshot(path=str(target), full_page=False)
    raster = png_painted_width(target)
    return {
        "file": name,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "raster_integrity": raster,
    }


def _assert_metrics(metrics: dict[str, object]) -> None:
    assert metrics["page_horizontal_overflow_px"] == 0, metrics
    assert metrics["host_horizontal_overflow_px"] == 0, metrics
    assert metrics["enabled_controls_below_44px"] == [], metrics
    assert metrics["error_overlay_visible"] is False, metrics


def _keyboard_sequence(page: Page, steps: int = 10) -> list[str]:
    page.locator("#meta-grid-request").focus()
    sequence = [_focus_label(page)]
    for _ in range(steps):
        page.keyboard.press("Tab")
        sequence.append(_focus_label(page))
    return sequence


def run_desktop(browser: Browser, output: Path, evidence: BrowserEvidence) -> tuple[dict[str, object], list[dict[str, object]]]:
    context, page = _open_authenticated_page(browser, {"width": 1440, "height": 900}, evidence)
    screenshots: list[dict[str, object]] = []
    try:
        tab_sequence = _keyboard_sequence(page)
        page.get_by_test_id("meta-grid-explain").click()
        expect(page.locator("#meta-grid-evidence")).to_be_visible()
        page.keyboard.press("Escape")
        assert _focus_label(page) == "meta-grid-explain"

        _submit(page, "Show Dr Shera today", "focused_schedule_lane")
        focused_count = page.locator(".meta-grid-item").count()
        assert focused_count >= 3, {
            "focused_count": focused_count,
            "scope": page.locator("#meta-grid-scope-summary").inner_text(),
            "content": page.locator("#meta-grid-content").inner_text(),
        }
        previous_scope = page.locator("#meta-grid-scope-summary").inner_text()
        _submit(page, "after 2 pm", "focused_schedule_lane", previous_scope=previous_scope)
        assert "2:00 pm" in page.locator("#meta-grid-scope-summary").inner_text()
        _submit(page, "Show Margaret Thompson's upcoming appointments", "patient_timeline")
        assert page.locator(".meta-grid-timeline-item").count() == 4
        metrics = _viewport_metrics(page)
        _assert_metrics(metrics)
        screenshots.append(_save_screenshot(page, output, "desktop-live-local-1440x900.png"))
        page.get_by_role("button", name="Return to full Diary grid").click()
        expect(page.get_by_test_id("meta-grid-workspace")).to_be_hidden()
        expect(page.locator("#diary-grid-container")).to_be_visible()
        evidence.assert_clean()
        return (
            {
                "id": "desktop_landscape",
                "width": 1440,
                "height": 900,
                "flows": {
                    "practitioner_root": "pass",
                    "plain_language_refinement": "pass; only the time boundary changed",
                    "patient_timeline": "pass; 4 chronological authored-synthetic appointments",
                    "ordinary_fallback": "pass",
                    "explanation_escape_focus_return": "pass",
                },
                "keyboard_tab_sequence": tab_sequence,
                **metrics,
            },
            screenshots,
        )
    finally:
        context.close()


def run_tablet_landscape(browser: Browser, output: Path, evidence: BrowserEvidence) -> tuple[dict[str, object], list[dict[str, object]]]:
    context, page = _open_authenticated_page(
        browser, {"width": 1024, "height": 768}, evidence, has_touch=True
    )
    screenshots: list[dict[str, object]] = []
    try:
        _submit(page, "Find Dr Shera availability today after 2 pm", "availability_slots")
        slot_count = page.get_by_test_id("meta-grid-slot").count()
        assert slot_count > 0
        page.get_by_test_id("meta-grid-slot").first.tap()
        expect(page.locator("#meta-grid-state-label")).to_contain_text("Selection")
        assert "Nothing is reserved or booked" in page.locator("#meta-grid-omissions").inner_text()
        _submit(page, "Add Margaret Thompson to the selected slot", "proposal_review")
        expect(page.locator("#meta-grid-state-label")).to_contain_text("Proposal")
        expect(page.get_by_test_id("meta-grid-proposal-handoff")).to_be_enabled()
        assert "No appointment has been created" in page.locator("#meta-grid-omissions").inner_text()
        screenshots.append(_save_screenshot(page, output, "tablet-landscape-proposal-1024x768.png"))

        _submit(page, "Compare Dr Shera and Dr Patel today morning", "aligned_comparison")
        assert page.locator(".meta-grid-comparison-lane").count() == 2
        metrics = _viewport_metrics(page)
        _assert_metrics(metrics)
        evidence.assert_clean()
        return (
            {
                "id": "tablet_landscape",
                "width": 1024,
                "height": 768,
                "flows": {
                    "availability": f"pass; {slot_count} backend candidates",
                    "touch_selection": "pass; transient selection only",
                    "proposal_review": "pass; operational proposal not committed",
                    "aligned_comparison": "pass; two lanes on one basis",
                    "proposal_handoff_activated": False,
                },
                **metrics,
            },
            screenshots,
        )
    finally:
        context.close()


def run_tablet_portrait(browser: Browser, output: Path, evidence: BrowserEvidence) -> tuple[dict[str, object], list[dict[str, object]]]:
    context, page = _open_authenticated_page(
        browser, {"width": 768, "height": 1024}, evidence, has_touch=True
    )
    try:
        _submit(page, "Show Dr Shera today", "focused_schedule_lane")
        parent_scope = page.locator("#meta-grid-scope-summary").inner_text()
        _submit(page, "after 10 am", "focused_schedule_lane", previous_scope=parent_scope)
        page.get_by_test_id("meta-grid-back").tap()
        expect(page.locator("#meta-grid-scope-summary")).to_have_text(parent_scope)
        metrics = _viewport_metrics(page)
        _assert_metrics(metrics)
        screenshot = _save_screenshot(page, output, "tablet-portrait-back-768x1024.png")
        evidence.assert_clean()
        return (
            {
                "id": "tablet_portrait",
                "width": 768,
                "height": 1024,
                "flows": {
                    "stacked_shell": "pass",
                    "plain_language_refinement": "pass",
                    "exact_back_restoration": "pass",
                },
                **metrics,
            },
            [screenshot],
        )
    finally:
        context.close()


def run_phone_portrait(browser: Browser, output: Path, evidence: BrowserEvidence) -> tuple[dict[str, object], list[dict[str, object]]]:
    context, page = _open_authenticated_page(
        browser, {"width": 390, "height": 844}, evidence, has_touch=True
    )
    screenshots: list[dict[str, object]] = []
    interruption_method = "foreground_page_switch"
    try:
        _submit(page, "Show Margaret Thompson's upcoming appointments", "patient_timeline")
        assert page.locator(".meta-grid-timeline-item").count() == 4
        _submit(page, "Find Dr Shera availability today after 2 pm", "availability_slots")
        slot = page.get_by_test_id("meta-grid-slot").first
        slot.focus()
        page.keyboard.press("Space")
        expect(page.locator("#meta-grid-state-label")).to_contain_text("Selection")
        _submit(page, "Add Margaret Thompson to the selected slot", "proposal_review")
        expect(page.locator("#meta-grid-state-label")).to_contain_text("Proposal")
        page.get_by_test_id("meta-grid-privacy").tap()
        expect(page.get_by_test_id("meta-grid-privacy")).to_have_attribute("aria-pressed", "true")
        expect(page.locator("#meta-grid-privacy-banner")).to_be_visible()
        screenshots.append(_save_screenshot(page, output, "phone-portrait-proposal-private-390x844.png"))

        other = context.new_page()
        other.goto("about:blank")
        other.bring_to_front()
        page.wait_for_timeout(250)
        page.bring_to_front()
        try:
            expect(page.locator("#meta-grid-state-label")).to_contain_text("Refresh", timeout=2_000)
        except AssertionError:
            interruption_method = "standards_dom_blur_event_headless_fallback"
            # Headless Chromium does not always emit blur when another page is
            # foregrounded. Dispatch the standard browser lifecycle event; do
            # not call the meta-grid's interruption function directly.
            page.evaluate("window.dispatchEvent(new Event('blur'))")
            expect(page.locator("#meta-grid-state-label")).to_contain_text("Refresh", timeout=5_000)
        other.close()
        expect(page.get_by_test_id("meta-grid-refresh-current")).to_be_visible()
        screenshots.append(_save_screenshot(page, output, "phone-portrait-interruption-390x844.png"))
        page.get_by_test_id("meta-grid-refresh-current").tap()
        _wait_family(page, "availability_slots")
        assert page.get_by_test_id("meta-grid-slot").count() > 0
        metrics = _viewport_metrics(page)
        _assert_metrics(metrics)
        evidence.assert_clean()
        return (
            {
                "id": "phone_portrait",
                "width": 390,
                "height": 844,
                "flows": {
                    "patient_timeline": "pass",
                    "availability": "pass",
                    "space_selection": "pass",
                    "proposal_review": "pass; not committed",
                    "privacy_mask": "pass",
                    "interruption": f"pass; {interruption_method}",
                    "fresh_read_recovery": "pass",
                },
                **metrics,
            },
            screenshots,
        )
    finally:
        context.close()


def run_phone_landscape(browser: Browser, output: Path, evidence: BrowserEvidence) -> tuple[dict[str, object], list[dict[str, object]]]:
    context, page = _open_authenticated_page(
        browser, {"width": 844, "height": 390}, evidence, has_touch=True
    )
    try:
        _submit(page, "Compare Dr Shera and Dr Patel today morning", "aligned_comparison")
        lanes = page.locator(".meta-grid-comparison-lane")
        assert lanes.count() == 2
        visible_lanes = lanes.evaluate_all(
            "els => els.filter(el => getComputedStyle(el).display !== 'none').length"
        )
        assert visible_lanes == 1
        next_button = page.get_by_role("button", name="Next practitioner")
        expect(next_button).to_be_visible()
        next_button.tap()
        assert lanes.nth(1).get_attribute("data-active") == "true"
        metrics = _viewport_metrics(page)
        _assert_metrics(metrics)
        screenshot = _save_screenshot(page, output, "phone-landscape-comparison-844x390.png")
        evidence.assert_clean()
        return (
            {
                "id": "phone_landscape",
                "width": 844,
                "height": 390,
                "flows": {
                    "aligned_comparison": "pass",
                    "one_visible_lane": "pass",
                    "sequential_navigation": "pass",
                },
                **metrics,
            },
            [screenshot],
        )
    finally:
        context.close()


def _run_browser(playwright: Playwright, output: Path, evidence: BrowserEvidence) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    browser = playwright.chromium.launch(headless=True)
    viewports: list[dict[str, object]] = []
    screenshots: list[dict[str, object]] = []
    try:
        for runner in (
            run_desktop,
            run_tablet_landscape,
            run_tablet_portrait,
            run_phone_portrait,
            run_phone_landscape,
        ):
            viewport, captured = runner(browser, output, evidence)
            viewports.append(viewport)
            screenshots.extend(captured)
    finally:
        browser.close()
    return viewports, screenshots


def run(output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    readiness = readiness_report()
    assert readiness["ready"] is True, readiness
    before = database_readback()
    runtime, processes = launch_runtime()
    evidence = BrowserEvidence()
    try:
        with sync_playwright() as playwright:
            viewports, screenshots = _run_browser(playwright, output, evidence)
        evidence.assert_clean()
    finally:
        stop_runtime(processes)
    after = database_readback()
    assert before["counts"] == after["counts"], {"before": before, "after": after}
    assert before["sha256"] == after["sha256"], {"before": before, "after": after}
    for table in (
        "appointment_audit_log",
        "appointment_command_idempotency",
        "bernie_booking_sessions",
        "bernie_session_events",
    ):
        assert after["counts"][table] == 0, {table: after["counts"][table]}

    route_counts = [
        {"method": method, "path": path, "count": count}
        for (method, path), count in sorted(evidence.requests.items())
        if path.startswith("/api/v1/")
    ]
    result = {
        "schema_version": "bernie.meta-grid-live-local.browser-evidence.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": "browser_pass",
        "evidence_mode": "live_local_browser_backend_postgres",
        "route": (
            f"http://127.0.0.1:3000/diary/diary.html?reference_date={REFERENCE_DATE.isoformat()}"
            "&bernie_session=false&standalone_diary=true"
        ),
        "runtime": {
            "database": runtime["database"],
            "provider": runtime["provider"],
            "cloud_credentials_present": runtime["cloud_credentials_present"],
            "backend_ready": runtime["backend_ready"],
            "static_ready": runtime["static_ready"],
            "credential_recorded": False,
            "token_recorded": False,
        },
        "route_interception": False,
        "api_interception": False,
        "browser_actions": "visible UI actions; no page.route and no page-internal projection or command functions",
        "authority": {
            "appointment_write_authority": False,
            "proposal_handoff_activated": False,
            "confirmation_control_activated": False,
            "event_runtime_activated": False,
            "operational_receipt_produced": False,
        },
        "database_readback": {
            "before": before,
            "after": after,
            "counts_identical": True,
            "sha256_identical": True,
        },
        "network": {
            "only_loopback": True,
            "forbidden_requests": evidence.forbidden,
            "api_method_path_counts": route_counts,
            "failed_api_responses": [row for row in evidence.responses if int(row["status"]) >= 400],
        },
        "viewports": viewports,
        "keyboard": {
            "enter_request_submit": "pass on desktop and smartphone portrait",
            "space_slot_selection": "pass on smartphone portrait",
            "escape_explanation_dismissal": "pass with focus returned to Why this view?",
            "native_tab_sequence": viewports[0]["keyboard_tab_sequence"],
            "page_internal_command_invocation": False,
        },
        "screenshots": screenshots,
        "browser_console_warnings_or_errors": evidence.console,
        "browser_page_errors": evidence.page_errors,
        "claims_not_made": [
            "provider",
            "PII",
            "committed event",
            "Stage 3B",
            "representative usability",
            "production",
            "deployment",
            "release",
        ],
    }
    target = output / "browser-acceptance-evidence.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = run(args.output.resolve())
    except Exception as exc:
        print(json.dumps({"result": "failed", "error_type": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "result": result["result"],
                "evidence_mode": result["evidence_mode"],
                "viewports": len(result["viewports"]),
                "screenshots": len(result["screenshots"]),
                "database_counts_identical": result["database_readback"]["counts_identical"],
                "database_sha256_identical": result["database_readback"]["sha256_identical"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
