"""Rendered, provider-free acceptance for the Reception One Stage 3B sidecar.

This is an automated protocol rehearsal, never participant evidence. It opens
only the repository-local study sidecar, performs the anonymous consent and
structured-record path, and captures exact responsive rasters.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-stage3b-readiness"
)
STUDY_URL = "http://127.0.0.1:8765/stage3b/"
VIEWPORTS = (
    ("desktop", 1440, 900),
    ("tablet", 768, 1024),
    ("phone", 390, 844),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png_dimensions(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return (
        int.from_bytes(payload[16:20], "big"),
        int.from_bytes(payload[20:24], "big"),
    )


def _metrics(page: Page) -> dict[str, object]:
    return page.evaluate(
        """() => {
          const visible = (element) => {
            const style = getComputedStyle(element);
            const rect = element.getBoundingClientRect();
            return style.display !== "none" && style.visibility !== "hidden"
              && rect.width > 0 && rect.height > 0;
          };
          const controls = [
            ...document.querySelectorAll(
              'button, a.product-link, select, input:not([type="checkbox"])'
            )
          ].filter(visible);
          return {
            width: window.innerWidth,
            height: window.innerHeight,
            horizontal_overflow_px: Math.max(
              0,
              document.documentElement.scrollWidth
                - document.documentElement.clientWidth
            ),
            controls_below_44px: controls
              .filter((element) => {
                const rect = element.getBoundingClientRect();
                return rect.width < 44 || rect.height < 44;
              })
              .map((element) => ({
                tag: element.tagName.toLowerCase(),
                id: element.id || null,
                text: (element.textContent || element.getAttribute("aria-label") || "")
                  .trim().slice(0, 80),
                width: Math.round(element.getBoundingClientRect().width * 10) / 10,
                height: Math.round(element.getBoundingClientRect().height * 10) / 10
              })),
            consent_visible: visible(document.getElementById("consent-panel")),
            workspace_visible: visible(document.getElementById("workspace"))
          };
        }"""
    )


def _start_session(page: Page) -> None:
    page.get_by_role("combobox", name="Participant code", exact=True).select_option(
        "P01"
    )
    page.get_by_role("combobox", name="Practice bucket", exact=True).select_option(
        "practice-a"
    )
    page.get_by_role(
        "combobox", name="Counterbalance arm", exact=True
    ).select_option("A")
    page.get_by_label(
        "Participation is voluntary and may stop at any time.", exact=True
    ).check()
    page.get_by_label(
        "Every displayed name and appointment is authored-synthetic.", exact=True
    ).check()
    page.get_by_label(
        "No typed words, free text, audio, video or screen recording will be retained.",
        exact=True,
    ).check()
    page.get_by_label(
        "This session cannot create or alter an appointment.", exact=True
    ).check()
    page.get_by_role(
        "button", name="Begin anonymous session", exact=True
    ).click()
    page.get_by_role("heading", name="P01", exact=True).wait_for(state="visible")


def _exercise_structured_record(page: Page) -> dict[str, object]:
    page.get_by_role("button", name="Start task timer", exact=True).click()
    page.get_by_role(
        "button", name="Mark assigned surface visited", exact=True
    ).click()
    page.get_by_role("button", name="Record this task", exact=True).click()
    assert page.locator("#record-count").inner_text() == "1 / 8"
    assert (
        page.locator("#observation-status").inner_text()
        == "S3B-01 recorded without free text."
    )
    page.get_by_role(
        "button", name="S3B-06 Identity ambiguity Not recorded", exact=True
    ).click()
    assert page.locator("#safe-ambiguity").input_value() == "safe_clarification"
    return {
        "record_count": "1 / 8",
        "active_task": page.locator("#task-id").inner_text(),
        "assigned_route": page.locator("#task-route").inner_text(),
        "safe_ambiguity_default": page.locator("#safe-ambiguity").input_value(),
        "score_summary": page.locator("#score-summary").inner_text(),
    }


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    viewport_evidence: list[dict[str, object]] = []
    screenshots: list[dict[str, object]] = []
    all_requests: set[str] = set()
    console_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for viewport_id, width, height in VIEWPORTS:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    locale="en-AU",
                    timezone_id="Australia/Brisbane",
                )
                page = context.new_page()
                page.on(
                    "request",
                    lambda request: all_requests.add(
                        f"{request.method} {urlsplit(request.url).scheme}://"
                        f"{urlsplit(request.url).netloc}{urlsplit(request.url).path}"
                    ),
                )
                page.on(
                    "console",
                    lambda message: console_errors.append(message.text)
                    if message.type == "error"
                    else None,
                )
                page.goto(STUDY_URL, wait_until="networkidle")

                before = _metrics(page)
                assert before["consent_visible"] is True
                assert before["workspace_visible"] is False
                assert before["horizontal_overflow_px"] == 0
                assert before["controls_below_44px"] == []

                consent_path = OUTPUT / f"{viewport_id}-{width}x{height}-consent.png"
                page.screenshot(path=consent_path, full_page=True)
                _start_session(page)
                record = _exercise_structured_record(page)
                after = _metrics(page)
                assert after["consent_visible"] is False
                assert after["workspace_visible"] is True
                assert after["horizontal_overflow_px"] == 0
                assert after["controls_below_44px"] == [], after

                active_path = OUTPUT / f"{viewport_id}-{width}x{height}-active.png"
                page.screenshot(path=active_path, full_page=True)
                viewport_evidence.append(
                    {
                        "id": viewport_id,
                        "configured_width": width,
                        "configured_height": height,
                        "before_consent": before,
                        "after_consent": after,
                        "structured_record_rehearsal": record,
                    }
                )
                for state, path in (
                    ("consent", consent_path),
                    ("active", active_path),
                ):
                    png_width, png_height = _png_dimensions(path)
                    screenshots.append(
                        {
                            "viewport": viewport_id,
                            "state": state,
                            "path": path.relative_to(ROOT).as_posix(),
                            "sha256": _sha256(path),
                            "width": png_width,
                            "height": png_height,
                        }
                    )
                context.close()
        finally:
            browser.close()

    allowed_prefix = "http://127.0.0.1:8765/stage3b/"
    unexpected_requests = sorted(
        request for request in all_requests if allowed_prefix not in request
    )
    assert unexpected_requests == []
    assert console_errors == []

    evidence = {
        "schema_version": "reception_one.stage3b.browser_acceptance.v1",
        "result": "pass",
        "evidence_mode": "automated_authored_synthetic_protocol_rehearsal",
        "automated_rehearsal_is_participant_evidence": False,
        "provider_used": False,
        "product_write_exercised": False,
        "real_patient_data_used": False,
        "study_url": STUDY_URL,
        "network_contract": {
            "allowed_origin": "http://127.0.0.1:8765",
            "observed_requests": sorted(all_requests),
            "unexpected_requests": unexpected_requests,
        },
        "console_errors": console_errors,
        "viewports": viewport_evidence,
        "screenshots": screenshots,
        "claims": [
            "Consent hides the study workspace until every attestation is present.",
            "The structured observation path records no free text.",
            "The safety-sensitive ambiguity task defaults to clarification.",
            "Desktop, tablet and phone layouts have no horizontal overflow.",
            "This automated rehearsal does not measure representative-staff usability.",
        ],
    }
    target = OUTPUT / "browser-acceptance-evidence.json"
    target.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"result": "pass", "evidence": str(target)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
