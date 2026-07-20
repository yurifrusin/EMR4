"""Protected-safe guards for the bounded functional meta-grid client tranche."""

import hashlib
import json

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs" / "diary"
HTML = DIARY / "diary.html"
DIARY_JS = DIARY / "diary.js"
META_JS = DIARY / "meta-grid.js"
META_CSS = DIARY / "meta-grid.css"
PLAN = ROOT / "docs" / "bernie-functional-meta-grid-client-plan.md"
EVIDENCE_DIR = (
    ROOT / "orchestration" / "prototypes" / "bernie-functional-meta-grid"
)
BROWSER_EVIDENCE = EVIDENCE_DIR / "browser-acceptance-evidence.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_functional_meta_grid_files_are_wired_into_the_existing_diary():
    html = _read(HTML)

    assert '<link rel="stylesheet" href="meta-grid.css?v=5"' in html
    assert '<script src="diary.js?v=189" defer>' in html
    assert '<script src="meta-grid.js?v=8" defer>' in html
    assert 'id="btn-meta-grid-launch"' in html
    assert 'id="bernie-meta-grid"' in html
    assert 'id="meta-grid-request-form"' in html
    assert 'id="meta-grid-canvas"' in html


def test_smoke_meta_grid_visibility_does_not_bypass_legacy_pilot_eligibility():
    source = _read(DIARY_JS)

    assert "if (isSmoke) setMetaGridLaunchAvailability(true);" in source
    assert "if (!token && !isSmoke)" in source
    assert "if (isSmoke) {\n    isBerniePilotEligible = true;" not in source


def test_projection_contract_has_all_accepted_functional_families_and_reversible_state():
    source = _read(META_JS)
    expected_families = {
        'family: "ordinary_overview"',
        'family: "focused_schedule_lane"',
        'family: "patient_timeline"',
        'family: "availability_slots"',
        'family: "aligned_comparison"',
        'family: "proposal_review"',
        'family: "clarification"',
    }

    assert 'const CONTRACT_VERSION = "bernie.meta-grid-projection.v1"' in source
    assert not sorted(fragment for fragment in expected_families if fragment not in source)
    assert "state.trail.push(state.current)" in source
    assert "state.trail.pop()" in source
    assert "state.recentRoots = state.recentRoots.slice(0, 5)" in source
    assert "state.selectedItem = null" in source
    assert "state.proposalResult = null" in source


def test_meta_grid_opens_no_api_persistence_event_or_provider_runtime():
    source = _read(META_JS)
    forbidden_fragments = {
        "fetch(",
        "XMLHttpRequest",
        "new WebSocket",
        "new EventSource",
        "sendBeacon(",
        "localStorage",
        "sessionStorage",
        "document.cookie",
        "serviceWorker",
        "confirm-bernie",
        "SpeechRecognition",
        "webkitSpeechRecognition",
        "navigator.mediaDevices",
    }

    hits = sorted(fragment for fragment in forbidden_fragments if fragment in source)
    assert not hits, f"Functional meta-grid opened a forbidden runtime: {hits}"
    assert ".innerHTML" not in source
    assert "appointment_write_authority: false" in source


def test_bridge_reuses_only_existing_read_and_proposal_boundaries():
    source = _read(DIARY_JS)

    for route in (
        "/appointments?${params.toString()}",
        "/patients/search?q=${encodeURIComponent(normalized)}",
        "/appointments/proposals/slot-search",
        "/appointments/proposals/bernie/supervised-booking",
    ):
        assert route in source

    bridge = source[source.index("window.EMR4DiaryMetaGridBridge"):]
    assert "readAppointments: metaGridReadAppointments" in bridge
    assert "searchPatients: metaGridSearchPatients" in bridge
    assert "readAvailability: metaGridReadAvailability" in bridge
    assert "prepareProposal: metaGridPrepareProposal" in bridge
    assert "handoffProposal: metaGridHandoffProposal" in bridge
    assert "confirm_endpoint: null" in source


def test_plain_language_supports_roots_refinements_and_safe_clarification():
    source = _read(META_JS)

    for phrase in (
        "Ordinary Diary",
        "upcoming",
        "availability",
        "compare",
        "after",
        "before",
        "morning",
        "afternoon",
        "whole day",
        "only booked",
        "show all",
    ):
        assert phrase.lower() in source.lower()

    assert "More than one patient matches" in source
    assert "Choose exactly two practitioners" in source
    assert "No person or command target has been silently selected" in source
    assert "Plain-language refinement:" in source
    assert '!["Cancelled", "NoShow", "DNA"].includes(item.status)' in source


def test_proposal_review_is_not_committed_and_smoke_handoff_is_inoperable():
    source = _read(META_JS)

    assert 'projectionState: "proposal_not_committed"' in source
    assert "No appointment has been created" in source
    assert "Confirmation is not available inside the meta-grid" in source
    assert "handoff.disabled = !projection.action_boundary.operational_command_available" in source
    assert "no operational booking review or confirmation handoff is available" in source
    assert "no receipt can be produced" in source


def test_privacy_interruption_and_freshness_require_reconciliation():
    source = _read(META_JS)
    html = _read(HTML)

    assert 'projectionState: "reconciliation_required"' in source or 'state: "reconciliation_required"' in source
    assert "togglePrivacy(true)" in source
    assert "state.interrupted = true" in source
    assert "state.selectedItem = null" in source
    assert "state.proposalResult = null" in source
    assert 'trigger: "system_freshness"' in source
    assert "Refresh current view" in source
    assert 'window.addEventListener("blur", markInterrupted)' in source
    assert 'document.addEventListener("visibilitychange"' in source
    assert 'id="meta-grid-interruption-test" class="hidden"' in html
    assert 'params.get("smoke") === "true" && params.get("meta_grid_acceptance") === "true"' in source
    assert 'elements.interruptionTest.addEventListener("click", markInterrupted)' in source


def test_semantic_controls_support_keyboard_and_accessible_status():
    html = _read(HTML)
    source = _read(META_JS)

    assert 'aria-live="polite"' in html
    assert 'aria-atomic="true"' in html
    assert 'tabindex="-1"' in html
    assert 'aria-pressed="false"' in html
    assert 'aria-expanded="false"' in html
    assert 'type="submit"' in html
    assert 'event.key !== "Escape"' in source
    assert "function closeExplanation()" in source
    assert '["Enter", " "].includes(event.key)' in source
    assert "elements.form.addEventListener(\"submit\"" in source


def test_tablet_phone_keyboard_and_privacy_layout_contract_is_explicit():
    css = _read(META_CSS)
    source = _read(META_JS)

    assert "min-height: 44px" in css
    assert "min-width: 44px" in css
    assert "@media (max-width: 900px)" in css
    assert "@media (max-width: 620px)" in css
    assert "@media (max-height: 470px) and (orientation: landscape)" in css
    assert '.meta-grid-comparison-lane[data-active="true"]' in css
    assert "grid-template-columns: 1fr" in css
    assert "--meta-grid-keyboard-inset" in css
    assert "window.visualViewport" in source
    assert "Previous practitioner" in source
    assert "Next practitioner" in source
    assert ".meta-grid.is-private .meta-grid-sensitive" in css


def test_frozen_plan_preserves_all_closed_authority_boundaries():
    plan = _read(PLAN).lower()

    for boundary in (
        "no api, pydantic, graphql, openapi or database artifact changes",
        "no provider, event-runtime, persistence",
        "pii, real patient/practice data",
        "stage 3b",
        "production, deployment or release",
        "authored_synthetic_client_fixture_browser",
        "desktop 1440×900",
        "tablet landscape",
        "tablet portrait",
        "phone portrait",
        "phone landscape",
        "native-keyboard evidence",
    ):
        assert boundary in plan


def test_browser_evidence_is_complete_hashed_and_strictly_synthetic():
    evidence = json.loads(_read(BROWSER_EVIDENCE))

    assert evidence["result"] == "browser_pass"
    assert evidence["evidence_mode"] == "authored_synthetic_client_fixture_browser"
    assert evidence["route_interception"] is False
    assert evidence["api_interception"] is False
    assert evidence["authority"] == {
        "appointment_write_authority": False,
        "proposal_handoff_enabled_in_smoke": False,
        "confirmation_control_in_meta_grid": False,
        "operational_receipt_produced": False,
    }
    assert [row["id"] for row in evidence["viewports"]] == [
        "desktop_landscape",
        "tablet_landscape",
        "tablet_portrait",
        "phone_portrait",
        "phone_landscape",
    ]
    for row in evidence["viewports"]:
        assert row["page_horizontal_overflow_px"] == 0
        assert row["host_horizontal_overflow_px"] == 0
        assert row["enabled_controls_below_44px"] == []
        assert row["console_warnings_or_errors"] == []

    for record in evidence["screenshots"]:
        screenshot = EVIDENCE_DIR / record["file"]
        assert screenshot.is_file()
        assert hashlib.sha256(screenshot.read_bytes()).hexdigest() == record["sha256"]

    assert evidence["browser_console_final"] == []
    assert evidence["browser_error_overlay"] is False
