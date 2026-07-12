"""
review/test_diary_note_preview.py — Focused test for S8 W2 affordance 4:
accessible read-only reason/notes preview without opening the edit modal.

Each rendered appointment card includes an .appt-preview-card element that
appears on hover (mouseenter, 400ms delay) or focus (focusin). The preview
exposes reason, notes (if available), and status via a tooltip-like card.
It must NOT contain any mutation controls (buttons, inputs, selects).

Run:
    pytest review/test_diary_note_preview.py -q
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import harness  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
REVIEW_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.e30.c2ln"
harness.assert_valid_review_token(REVIEW_AUTH_TOKEN)

SMOKE_APPT_1_ID = "smoke-appt-1"  # Margaret Thompson - "Hypertension follow-up"


@pytest.fixture(scope="module")
def _base_url():
    with harness.serve_dir(DOCS_DIR) as base_url:
        yield base_url


def _open_smoke_diary(page, base_url):
    page.goto(base_url + "/diary/diary.html?smoke=true")
    page.wait_for_selector(".diary-column", state="visible", timeout=15000)


# ── Test 1: Preview card element exists on each appointment ─────────────────


def test_preview_card_element_exists(_base_url):
    """Each rendered appointment should have a .appt-preview-card child."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        # Check that preview cards exist as children of appointments
        appts = page.locator(".appt")
        count = appts.count()
        assert count > 0, "Expected at least 1 appointment to exist"

        # Each non-cancelled appointment should have a preview-card element
        preview_cards = page.locator(".appt .appt-preview-card")
        assert preview_cards.count() > 0, "Expected at least 1 preview card"


# ── Test 2: Preview card shows on hover ─────────────────────────────────────


def test_preview_card_shows_on_hover(_base_url):
    """Hovering over an appointment should show its preview card."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        appt = page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"]')
        appt.hover()
        page.wait_for_timeout(600)  # longer than the 400ms preview delay

        # The preview card should now be visible
        preview_card = appt.locator(".appt-preview-card")
        assert preview_card.is_visible(), "Expected preview card to be visible on hover"


# ── Test 3: Preview card shows reason text ──────────────────────────────────


def test_preview_card_shows_reason(_base_url):
    """The preview card should display the appointment reason."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        appt = page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"]')
        appt.hover()
        page.wait_for_timeout(600)

        preview_card = appt.locator(".appt-preview-card")
        card_text = preview_card.text_content()
        assert "Hypertension" in card_text or "follow-up" in card_text, \
            f"Expected preview card to show reason text, got: {card_text}"


# ── Test 4: Preview card has no mutation controls ───────────────────────────


def test_preview_card_no_mutation_controls(_base_url):
    """The preview card must not contain buttons, inputs, selects, or other
    mutation affordances."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        preview_cards = page.locator(".appt-preview-card")

        # Check no buttons, inputs, or selects exist inside any preview card
        button_count = preview_cards.locator("button").count()
        input_count = preview_cards.locator("input").count()
        select_count = preview_cards.locator("select").count()
        textarea_count = preview_cards.locator("textarea").count()

        total_mutation = button_count + input_count + select_count + textarea_count
        assert total_mutation == 0, \
            f"Expected 0 mutation controls in preview card, got buttons={button_count}, inputs={input_count}, selects={select_count}, textareas={textarea_count}"


# ── Test 5: Preview card shows status badge ─────────────────────────────────


def test_preview_card_shows_status(_base_url):
    """The preview card should include a status badge."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        harness.stub_office(page)
        _open_smoke_diary(page, _base_url)

        appt = page.locator(f'.appt[data-id="{SMOKE_APPT_1_ID}"]')
        appt.hover()
        page.wait_for_timeout(600)

        preview_card = appt.locator(".appt-preview-card")
        status_badge = preview_card.locator(".preview-card-status")
        assert status_badge.is_visible(), "Expected status badge in preview card"
        assert "Booked" in status_badge.text_content(), \
            f"Expected preview status to show status, got: {status_badge.text_content()}"
