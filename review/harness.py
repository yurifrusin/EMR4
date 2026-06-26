"""
review/harness.py — reusable Playwright review primitives for EMR4's
cost-conscious sprint review.

Initial ratified scaffold (2026-06-26) for Codex/Ariadne to extend. It implements
the "explore once -> crystallize into a deterministic check -> run free forever"
pattern: the model stays OUT of the execution loop. `pytest` runs these checks and
emits JUnit XML (`--junitxml`); Ariadne reads only the failures.

Each primitive operates on a Playwright `page` and returns a structured result
dict — {name, check, selector, expected, actual, passed} — so the same checks can
drive pytest assertions today and a JSON report later without rewriting them.
"""
from __future__ import annotations

import contextlib
import functools
import http.server
import socketserver
import threading
from pathlib import Path


# ── Static file server ───────────────────────────────────────────────────────
# Serves docs/ so diary.html?smoke=true loads as a real page with NO backend.
@contextlib.contextmanager
def serve_dir(root: Path):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    # Port 0 -> OS assigns a free ephemeral port.
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{port}"
        finally:
            httpd.shutdown()


# ── Office.js stub ───────────────────────────────────────────────────────────
# diary.js runs its init inside Office.onReady(). Outside an Office host we stub
# office.js so onReady fires immediately — making the harness deterministic and
# offline (no Microsoft CDN dependency). Everything else diary.js touches on the
# smoke path is optional-chained (Office.context?.ui?...), so this minimal shim
# is sufficient.
OFFICE_STUB = "window.Office = { onReady: function (cb) { cb({ host: null, platform: null }); } };"


def stub_office(page) -> None:
    page.route(
        "**/office.js",
        lambda route: route.fulfill(
            status=200, content_type="application/javascript", body=OFFICE_STUB
        ),
    )


# ── Primitives ───────────────────────────────────────────────────────────────
def _count(page, selector: str) -> int:
    return page.locator(selector).count()


def assert_count(page, check: dict) -> dict:
    actual = _count(page, check["selector"])
    return {
        "name": check["name"], "check": "count ==", "selector": check["selector"],
        "expected": check["expected"], "actual": actual,
        "passed": actual == check["expected"],
    }


def assert_min_count(page, check: dict) -> dict:
    actual = _count(page, check["selector"])
    return {
        "name": check["name"], "check": "count >=", "selector": check["selector"],
        "expected": f">={check['expected']}", "actual": actual,
        "passed": actual >= check["expected"],
    }


def assert_text_count(page, check: dict) -> dict:
    """Count elements matching `selector` whose text contains `text` (case-insensitive)."""
    actual = page.locator(check["selector"], has_text=check["text"]).count()
    return {
        "name": check["name"], "check": f"count(has_text {check['text']!r}) ==",
        "selector": check["selector"], "text": check["text"],
        "expected": check["expected"], "actual": actual,
        "passed": actual == check["expected"],
    }


PRIMITIVES = {
    "count": assert_count,
    "min_count": assert_min_count,
    "text_count": assert_text_count,
}


def run_check(page, check: dict) -> dict:
    """Dispatch a single data-driven check row to its primitive."""
    try:
        return PRIMITIVES[check["type"]](page, check)
    except KeyError as exc:
        return {"name": check.get("name", "?"), "passed": False,
                "error": f"unknown check type or missing field: {exc}"}
