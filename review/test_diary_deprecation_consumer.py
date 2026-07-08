"""
review/test_diary_deprecation_consumer.py - browser execution proof for the
Diary apiFetch Deprecation-header consumer.

This stays route-intercepted and provider-free. It proves the browser-side
consumer emits the developer warning when a response exposes Deprecation, and
does not warn when the header is absent.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency not installed
    pytest.skip(
        "playwright not installed (pip install playwright && playwright install chromium)",
        allow_module_level=True,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
REVIEW_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
harness.assert_valid_review_token(REVIEW_AUTH_TOKEN)


def _cors_headers(*, deprecation: bool) -> dict[str, str]:
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "Deprecation",
    }
    if deprecation:
        headers["Deprecation"] = 'true; version="0"'
    return headers


def test_api_fetch_warns_only_when_deprecation_header_is_exposed():
    warnings = []

    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        page.on(
            "console",
            lambda msg: warnings.append(msg.text) if msg.type == "warning" else None,
        )

        def handle_deprecated(route):
            route.fulfill(
                status=200,
                headers=_cors_headers(deprecation=True),
                content_type="application/json",
                body=json.dumps({"ok": True}),
            )

        def handle_plain(route):
            route.fulfill(
                status=200,
                headers=_cors_headers(deprecation=False),
                content_type="application/json",
                body=json.dumps({"ok": True}),
            )

        page.route("**/api/v1/appointments/deprecated-consumer-proof", handle_deprecated)
        page.route("**/api/v1/appointments/plain-consumer-proof", handle_plain)

        page.goto(base_url + "/diary/diary.html?smoke=true")
        harness.bootstrap_auth(page, REVIEW_AUTH_TOKEN)
        page.wait_for_function("() => typeof apiFetch === 'function'")

        page.evaluate("() => apiFetch('/appointments/plain-consumer-proof')")
        assert not [
            warning for warning in warnings
            if "[EMR4 Deprecation Warning]" in warning
        ]

        page.evaluate("() => apiFetch('/appointments/deprecated-consumer-proof')")

        matching_warnings = [
            warning for warning in warnings
            if "[EMR4 Deprecation Warning]" in warning
        ]
        assert matching_warnings == [
            '[EMR4 Deprecation Warning] Deprecated route: '
            '/appointments/deprecated-consumer-proof (true; version="0")'
        ]

        browser.close()
