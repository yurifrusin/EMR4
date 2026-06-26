"""
review/test_diary_smoke.py — deterministic diary-grid review against ?smoke=true.

Runs with NO backend, NO auth, NO seeding: the diary's built-in smoke mode
(`?smoke=true`) renders the grid from embedded fixtures, so these assertions are
stable and repeatable. office.js is stubbed so Office.onReady fires offline.

This is the model-OUT-of-the-loop review pattern: pytest executes the checks,
emits JUnit XML, and Ariadne reads only failures.

Prerequisites (one-time):
    pip install playwright pytest
    playwright install chromium

Run:
    pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q

Each row in checks_diary.json becomes one parametrized test case, so the JUnit
report lists every check by name. Add a check = add a row (no code).

Initial ratified scaffold. Selectors/expectations derived from docs/diary/diary.js
smoke mode as of 2026-06-26; re-verify if the diary DOM changes. The
robust long-term fix for selector drift is stable data-testid attributes on the
diary elements (a frontend task), which keeps this harness from needing repair.
"""
import json
import sys
from pathlib import Path

import pytest

# Make harness importable regardless of pytest's rootdir / cwd.
sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency not installed
    pytest.skip("playwright not installed (pip install playwright && playwright install chromium)",
                allow_module_level=True)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
CHECKS = json.loads((Path(__file__).parent / "checks_diary.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def diary_page():
    with harness.serve_dir(DOCS_DIR) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        page.goto(base_url + CHECKS["target"])
        page.wait_for_selector(CHECKS["wait_for"], state="visible", timeout=15000)
        # Open flow panel to ensure the flow lists render
        page.click("#btn-toggle-flow")
        page.wait_for_selector("#diary-flow-panel:not(.hidden)", state="visible", timeout=5000)
        yield page
        browser.close()


@pytest.mark.parametrize("check", CHECKS["checks"], ids=lambda c: c["name"])
def test_diary_check(diary_page, check):
    result = harness.run_check(diary_page, check)
    assert result["passed"], result
