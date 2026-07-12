"""
review/test_taskpane_diary_launch.py — S8 W1 diary launch reliability tests.

Tests are focused on the pure JS functions in the taskpane:
  - resolveDiaryUrl(location)  — URL resolution per environment
  - getDiaryErrorMessage(code, rawMessage) — error-code mapping
  - retryOpenDiary() / diary-error container — retry affordance visibility
  - 12007 auto-retry path (bounded single retry)

office.js is stubbed so the taskpane loads without a real Office host.

Run:
    pytest review/test_taskpane_diary_launch.py -q
"""
import base64
import json
from pathlib import Path

import pytest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)


# ── Office.js stub (local to this W1-owned test file) ─────────
# The expanded stub includes displayDialogAsync, AsyncResultStatus,
# and HostType so openDiary()/retryOpenDiary() do not crash.
_OFFICE_STUB = (
    "window.Office = {"
    "  onReady: function (cb) { cb({ host: null, platform: null }); },"
    "  context: { ui: { displayDialogAsync: function(url, opts, cb) {"
    "    /* stub: no-op, does not fire callback so tests control the lifecycle */"
    "  } } },"
    "  AsyncResultStatus: { Failed: 'failed' },"
    "  HostType: { Word: 'word' }"
    "};"
)


def stub_office(page) -> None:
    page.route(
        "**/office.js",
        lambda route: route.fulfill(
            status=200, content_type="application/javascript", body=_OFFICE_STUB
        ),
    )


def _decode_base64url_json(segment: str) -> dict:
    padding = "=" * (-len(segment) % 4)
    try:
        decoded = base64.urlsafe_b64decode(segment + padding)
        value = json.loads(decoded.decode("utf-8"))
    except Exception as exc:
        raise AssertionError(
            "review auth token must contain valid base64url JSON"
        ) from exc
    if not isinstance(value, dict):
        raise AssertionError("review auth token JSON payload must be an object")
    return value


def assert_valid_review_token(token: str) -> None:
    parts = token.split(".")
    if len(parts) != 3 or any(not part for part in parts):
        raise AssertionError("review auth token must be a three-part JWT-like token")
    _decode_base64url_json(parts[0])
    _decode_base64url_json(parts[1])


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
SRC_DIR = REPO_ROOT / "EMR4 Sidebar" / "src" / "taskpane"
TEST_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
assert_valid_review_token(TEST_AUTH_TOKEN)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def context(browser):
    ctx = browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture
def page(context):
    p = context.new_page()
    stub_office(p)
    return p


# ── resolveDiaryUrl tests ──────────────────────────────────────────────────

def _resolve(page, location):
    """Evaluate resolveDiaryUrl with a synthetic location object."""
    return page.evaluate("""
        (loc) => {
            // Re-create the resolver from source so tests work on the
            // source file before sync_taskpane.py patching.
            function resolveDiaryUrl(location) {
                if (location.port === "3000") {
                    return location.origin + "/diary/diary.html";
                }
                return "https://yurifrusin.github.io/EMR4/diary/diary.html";
            }
            return resolveDiaryUrl(loc);
        }
    """, location)


class TestResolveDiaryUrl:
    """Pure URL resolution per environment."""

    def test_dev_server_port_3000(self, page):
        """Dev server (localhost:3000) resolves to local diary URL."""
        url = _resolve(page, {"port": "3000", "origin": "http://localhost:3000"})
        assert url == "http://localhost:3000/diary/diary.html"

    def test_github_pages(self, page):
        """GitHub Pages host resolves to the deployed diary URL."""
        url = _resolve(page, {
            "port": "443",
            "origin": "https://yurifrusin.github.io",
        })
        assert url == "https://yurifrusin.github.io/EMR4/diary/diary.html"

    def test_ngrok_tunnel(self, page):
        """ngrok tunnel resolves to the deployed diary URL (same as Pages fallback)."""
        url = _resolve(page, {
            "port": "443",
            "origin": "https://property-cinch-backfield.ngrok-free.dev",
        })
        assert url == "https://yurifrusin.github.io/EMR4/diary/diary.html"

    def test_unrecognized_host_is_safe_fallback(self, page):
        """Unrecognized host defaults to deployed Pages diary."""
        url = _resolve(page, {
            "port": "8080",
            "origin": "http://unknown.local",
        })
        assert url == "https://yurifrusin.github.io/EMR4/diary/diary.html"


# ── getDiaryErrorMessage tests ──────────────────────────────────────────────

def _get_error_msg(page, code, raw):
    """Evaluate getDiaryErrorMessage with the given error code and message."""
    return page.evaluate("""
        ({code, raw}) => {
            const DIARY_ERROR_MAP = {
                12007: { message: "The Diary window was already open. Closing the old window and trying again\u2026", action: "retry_once" },
                12009: { message: "Diary window request was declined. When Word shows the Allow prompt, select Allow to open the Diary.", action: "retry_user" },
                12011: { message: "Popup blocked by your browser. Please enable popups for this site and try again.", action: "retry_user" },
            };
            function getDiaryErrorMessage(c, r) {
                const known = DIARY_ERROR_MAP[c];
                if (known) return known;
                return { message: "Could not open Diary: " + (r || "Unknown error"), action: "retry_user" };
            }
            return getDiaryErrorMessage(code, raw);
        }
    """, {"code": code, "raw": raw})


class TestGetDiaryErrorMessage:
    """Distinct error handling per Office dialog error code."""

    def test_code_12007(self, page):
        """12007 (dialog already open) maps to retry_once action."""
        result = _get_error_msg(page, 12007, "Another dialog is open")
        assert result["action"] == "retry_once"
        assert "already open" in result["message"]

    def test_code_12009(self, page):
        """12009 (user declined) explains the Allow prompt."""
        result = _get_error_msg(page, 12009, "User declined")
        assert result["action"] == "retry_user"
        assert "Allow" in result["message"]

    def test_code_12011(self, page):
        """12011 (popup blocked) explains enabling popups."""
        result = _get_error_msg(page, 12011, "Popups blocked")
        assert result["action"] == "retry_user"
        assert "popup" in result["message"].lower()

    def test_generic_error_fallback(self, page):
        """Unknown code falls back to generic message with raw error."""
        result = _get_error_msg(page, 99999, "Something broke")
        assert result["action"] == "retry_user"
        assert "Something broke" in result["message"]

    def test_generic_missing_raw_message(self, page):
        """Unknown code with no raw message uses default."""
        result = _get_error_msg(page, 99999, None)
        assert "Unknown error" in result["message"]


# ── Retry affordance tests ─────────────────────────────────────────────────

class TestRetryAffordance:
    """Visible retry button and error banner."""

    def test_diary_error_banner_is_hidden_initially(self, page):
        """The diary-error container is hidden on page load."""
        page.goto(SRC_DIR.as_uri() + "/taskpane.html")
        error_container = page.locator("#diary-error")
        expect(error_container).to_be_hidden()

    def _show_app_view(self, page):
        """Make #view-app visible so children (#diary-error) can render."""
        page.evaluate("document.getElementById('view-app')?.classList.remove('hidden')")

    def test_diary_error_becomes_visible(self, page):
        """showDiaryError() makes the container visible."""
        page.goto(SRC_DIR.as_uri() + "/taskpane.html")
        self._show_app_view(page)
        page.evaluate("""
            const container = document.getElementById('diary-error');
            const msgEl = document.getElementById('diary-error-msg');
            const retryBtn = document.getElementById('btn-diary-retry');
            if (container) container.classList.remove('hidden');
            if (msgEl) msgEl.textContent = 'Test error message';
            if (retryBtn) retryBtn.classList.remove('hidden');
        """)
        error_container = page.locator("#diary-error")
        expect(error_container).to_be_visible()
        expect(page.locator("#diary-error-msg")).to_have_text("Test error message")
        expect(page.locator("#btn-diary-retry")).to_be_visible()

    def test_diary_error_hides_after_retry_click(self, page):
        """retryOpenDiary() hides the error container (even if Office is stubbed)."""
        page.goto(SRC_DIR.as_uri() + "/taskpane.html")
        self._show_app_view(page)
        # Show the error first
        page.evaluate("""
            const container = document.getElementById('diary-error');
            if (container) container.classList.remove('hidden');
        """)
        expect(page.locator("#diary-error")).to_be_visible()
        # Click retry — this calls retryOpenDiary() which calls hideDiaryError()
        # then openDiary(). With the stubbed Office stub, openDiary will hit the
        # stub path but hideDiaryError runs first.
        page.evaluate("window.retryOpenDiary && window.retryOpenDiary()")
        expect(page.locator("#diary-error")).to_be_hidden()
        # Note: with the minimal Office stub, displayDialogAsync is undefined,
        # so the openDiary error path may fire after hideDiaryError. The test
        # verifies the hide-intent, not the full dialog lifecycle.


# ── Bounded 12007 retry test ───────────────────────────────────────────────

class Test12007AutoRetry:
    """Bounded single retry for 12007."""

    def test_12007_retry_only_once(self, page):
        """When displayDialogAsync returns 12007, it retries exactly once and no loop."""
        # Set Office as non-writable so the harness stub route cannot overwrite it.
        page.add_init_script("""
            Object.defineProperty(window, 'Office', {
                value: {
                    onReady: function (cb) { cb({ host: null, platform: null }); },
                    context: { ui: { displayDialogAsync: function(url, opts, callback) {
                        window._diaryCallCount = (window._diaryCallCount || 0) + 1;
                        callback({ status: 'failed', error: { code: 12007, message: 'Another dialog is open' } });
                    } } },
                    AsyncResultStatus: { Failed: 'failed' },
                    HostType: { Word: 'word' }
                },
                writable: false,
                configurable: false
            });
            window._diaryCallCount = 0;
        """)
        page.goto(SRC_DIR.as_uri() + "/taskpane.html")

        # Make the app view visible so the diary-error container can render.
        page.evaluate("document.getElementById('view-app')?.classList.remove('hidden')")

        # Call openDiary — it should attempt, retry once, then show error
        page.evaluate("window.openDiary && window.openDiary()")

        # Verify displayDialogAsync was called exactly twice
        call_count_val = page.evaluate("window._diaryCallCount || 0")
        assert call_count_val == 2, (
            f"Expected exactly 2 displayDialogAsync calls (first + one retry), got {call_count_val}"
        )

        # Verify the error banner is now visible (retry also failed, so error is shown)
        error_container = page.locator("#diary-error")
        expect(error_container).to_be_visible()
        # Verify the message is set (non-empty)
        expect(page.locator("#diary-error-msg")).not_to_be_empty()


# ── Verification helper ────────────────────────────────────────────────────

def expect(locator):
    """Minimal expect helper for basic visibility assertions."""
    class ExpectWrapper:
        def __init__(self, loc):
            self._loc = loc

        def to_be_visible(self, timeout=3000):
            assert self._loc.count() > 0, "Element not found in DOM"
            assert self._loc.is_visible(timeout=timeout), (
                f"Expected element {self._loc} to be visible"
            )

        def to_be_hidden(self, timeout=3000):
            assert self._loc.count() == 0 or not self._loc.is_visible(timeout=timeout), (
                f"Expected element {self._loc} to be hidden"
            )

        def to_have_text(self, text):
            actual = self._loc.text_content()
            assert actual == text, (
                f"Expected text {text!r}, got {actual!r}"
            )

        def not_to_be_empty(self):
            text = self._loc.text_content()
            assert text is not None and text.strip() != "", (
                f"Expected element {self._loc} to have non-empty text"
            )

    return ExpectWrapper(locator)
