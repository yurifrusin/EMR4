"""Guards for the bounded Reception One combined-scope product proof."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs" / "diary"
PLAN = ROOT / "docs" / "bernie-reception-one-combined-scope-proof-plan.md"
HARNESS = ROOT / "scripts" / "bernie_reception_one_combined_scope_harness.py"
RUNNER = ROOT / "scripts" / "bernie_reception_one_combined_scope_acceptance.py"
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "bernie-reception-one-combined-scope-proof"
)
EVIDENCE = EVIDENCE_DIR / "browser-acceptance-evidence.json"
CLEANUP = EVIDENCE_DIR / "database-cleanup-evidence.json"
CONTINUITY = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_freezes_exact_interaction_evidence_and_closed_boundaries():
    plan = _read(PLAN)
    for required in (
        "Show me all the available slots with Dr Shera for a half-hour appointment",
        "with Margaret Thompson after 2 today",
        "tomorrow instead",
        "make it 45 minutes",
        "after 3",
        "live_local_browser_backend_postgres",
        "desktop landscape 1440×900",
        "tablet landscape 1024×768",
        "tablet portrait 768×1024",
        "smartphone portrait 390×844",
        "smartphone landscape 844×390",
        "No API, Pydantic, GraphQL, OpenAPI or database artifact changes",
        "Stage 3B",
        "production, deployment and release remain",
    ):
        assert required in plan


def test_combined_scope_parser_retains_explicit_patient_without_root_reuse():
    source = _read(DIARY / "meta-grid.js")

    assert "function parseDuration(" in source
    assert "half[- ]hour" in source
    assert "duration_minutes: ${value}" in source
    assert "unqualified one-through-six means afternoon" in source
    assert "const patientQuery = patientNameFromRequest(text);" in source
    assert "patient = rememberPatient(patientResolution.patient);" in source
    assert "patient: patientForProjection(current)" in source
    assert "if (patient) scope.patient_ids = [patient.id];" in source
    assert "patient_display: patient?.display_name || null" in source
    assert "state.patientContexts.get(String(id))" in source
    assert "const id = projection?.scope?.patient_ids?.[0];" in source
    assert 'if (!["selection_only", "proposal_not_committed"].includes(projection.state))' in source
    assert "state.selectedItem = null;" in source
    assert "state.proposalResult = null;" in source


def test_scoped_selection_prepares_proposal_without_retyping_or_writing():
    source = _read(DIARY / "meta-grid.js")

    assert "Prepare proposal for ${patient.display_name}" in source
    assert '"meta-grid-prepare-scoped-proposal"' in source
    assert "submitRequest(`Prepare proposal for ${patient.display_name}`)" in source
    assert 'projectionState: "proposal_not_committed"' in source
    assert "appointment_write_authority: false" in source
    assert "No appointment has been created" in source
    assert "Confirmation is not available inside the meta-grid" in source


def test_refinement_privacy_and_interruption_require_fresh_scoped_reads():
    source = _read(DIARY / "meta-grid.js")

    assert "dateRequested" in source
    assert "duration: duration.value" in source
    assert "patient: patientForProjection(current)" in source
    assert "const refreshedPatient = await resolvePatient(patient.display_name);" in source
    assert "after fresh patient resolution and a fresh backend availability read" in source
    assert 'elements.announcer.textContent = "Patient-sensitive details are hidden."' in source
    assert 'elements.scope.classList.toggle("meta-grid-sensitive"' in source
    assert 'if (root.sensitive) button.classList.add("meta-grid-sensitive")' in source


def test_client_opens_no_new_api_persistence_event_provider_voice_or_confirmation_surface():
    meta_source = _read(DIARY / "meta-grid.js")
    diary_source = _read(DIARY / "diary.js")
    forbidden = {
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
    assert not sorted(fragment for fragment in forbidden if fragment in meta_source)

    for route in (
        "/appointments?${params.toString()}",
        "/patients/search?q=${encodeURIComponent(normalized)}",
        "/appointments/proposals/slot-search",
        "/appointments/proposals/bernie/supervised-booking",
    ):
        assert route in diary_source
    assert "confirm_endpoint: null" in diary_source


def test_ipv6_harness_is_exact_disposable_provider_disabled_and_preserves_live_review():
    source = _read(HARNESS)
    runner = _read(RUNNER)

    assert 'LOCKED_DATABASE = "gp_pms_reception_one_combined_scope_9c41b7e2_20260721"' in source
    assert 'IPV6_HOST = "::1"' in source
    assert '"--host",\n                IPV6_HOST' in source
    assert '"CORS_ORIGINS": \'["http://[::1]:3000"]\'' in source
    assert '"BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled"' in source
    assert '"BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false"' in source
    assert '"GOOGLE_APPLICATION_CREDENTIALS": ""' in source
    assert "base.cleanup_database()" in source
    assert 'AUTH_URL = "http://[::1]:3000/meta-grid-auth.html"' in runner
    assert "active_ipv4_review_session_contacted\": False" in runner


def test_playwright_uses_visible_ui_without_route_interception_or_handoff_activation():
    source = _read(RUNNER)

    assert "page.route(" not in source
    assert ".route(" not in source
    assert "meta-grid-proposal-handoff\").click" not in source
    assert "meta-grid-prepare-scoped-proposal" in source
    assert "page.keyboard.press(\"Space\")" in source
    assert "page.keyboard.press(\"Enter\")" in source
    assert "window.dispatchEvent(new Event('blur'))" in source
    assert "markInterrupted()" not in source
    assert '"/api/v1/appointments/bernie/sessions' not in source
    assert '"/api/v1/appointments/proposals/create/confirm' not in source


def test_live_local_browser_evidence_is_responsive_sanitized_and_zero_write():
    evidence_text = _read(EVIDENCE)
    evidence = json.loads(evidence_text)

    assert evidence["result"] == "browser_pass"
    assert evidence["evidence_mode"] == "live_local_browser_backend_postgres"
    assert evidence["route_interception"] is False
    assert evidence["api_interception"] is False
    assert evidence["runtime"]["database"] == (
        "gp_pms_reception_one_combined_scope_9c41b7e2_20260721"
    )
    assert evidence["runtime"]["provider"] == "disabled"
    assert evidence["runtime"]["loopback_family"] == "ipv6"
    assert evidence["runtime"]["active_ipv4_review_session_contacted"] is False
    assert evidence["authority"] == {
        "appointment_write_authority": False,
        "proposal_handoff_activated": False,
        "confirmation_control_activated": False,
        "event_runtime_activated": False,
        "operational_receipt_produced": False,
    }
    readback = evidence["database_readback"]
    assert readback["counts_identical"] is True
    assert readback["sha256_identical"] is True
    assert readback["before"] == readback["after"]
    assert readback["after"]["counts"]["appointments"] == 6
    for table in (
        "appointment_audit_log",
        "appointment_command_idempotency",
        "bernie_booking_sessions",
        "bernie_session_events",
    ):
        assert readback["after"]["counts"][table] == 0

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
        assert row["error_overlay_visible"] is False
        assert row["window_inner_width"] == row["width"]
        assert row["host_width"] == row["width"]
        assert row["scenario_results"]["combined_scope"] == "pass"
    tablet_portrait = next(
        row for row in evidence["viewports"] if row["id"] == "tablet_portrait"
    )
    assert tablet_portrait["scenario_results"]["refinement_clears_stale_selection"] == "pass"

    assert evidence["keyboard"]["space_slot_selection"].startswith("pass")
    assert evidence["keyboard"]["enter_scoped_proposal"].startswith("pass")
    assert evidence["privacy"] == {
        "patient_scope_masked": True,
        "proposal_summary_masked": True,
        "private_live_region_sanitized": True,
    }
    assert evidence["interruption"]["stale_proposal_reused"] is False
    assert evidence["interruption"]["fresh_patient_read_required"] is True
    assert evidence["interruption"]["fresh_availability_read_required"] is True
    assert evidence["browser_console_warnings_or_errors"] == []
    assert evidence["browser_page_errors"] == []
    for forbidden in ("Margaret", "date_of_birth", "patient_id", "access_token", "password"):
        assert forbidden not in evidence_text

    observed = {
        (row["method"], row["path"])
        for row in evidence["network"]["api_method_path_counts"]
    }
    assert ("GET", "/api/v1/patients/search") in observed
    assert ("POST", "/api/v1/appointments/proposals/slot-search") in observed
    assert (
        "POST",
        "/api/v1/appointments/proposals/bernie/supervised-booking",
    ) in observed
    assert not any("/confirm" in path or "/sessions" in path for _method, path in observed)

    for record in evidence["screenshots"]:
        screenshot = EVIDENCE_DIR / record["file"]
        assert screenshot.is_file()
        assert hashlib.sha256(screenshot.read_bytes()).hexdigest() == record["sha256"]
        assert record["raster_integrity"]["passes"] is True


def test_disposable_database_cleanup_is_marker_verified_and_exact():
    cleanup = json.loads(_read(CLEANUP))

    assert cleanup["database"] == (
        "gp_pms_reception_one_combined_scope_9c41b7e2_20260721"
    )
    assert cleanup["ownership_marker_verified"] is True
    assert cleanup["cleanup"] == "dropped_exact_verified_disposable_database"
    assert cleanup["recoverable"] is False
    assert cleanup["scope"] == "authored_synthetic_disposable_database_only"


def test_continuity_contract_tracks_gap_then_requires_linked_test_evidence():
    graph = json.loads(_read(CONTINUITY))
    node = next(
        row for row in graph["nodes"] if row["id"] == "reception-one-combined-scope-proof"
    )
    contract = next(
        row
        for row in node["contract_evidence"]
        if row["contract_id"]
        == "combined-patient-practitioner-time-duration-intent"
    )

    assert node["status"] in {"active", "accepted"}
    if node["status"] == "active":
        assert contract["status"] == "gap"
        assert "docs/bernie-reception-one-combined-scope-proof-plan.md" in contract["evidence"]
    else:
        assert contract["status"] == "satisfied"
        assert "tests/test_bernie_reception_one_combined_scope.py" in contract["evidence"]
        assert "tests/test_bernie_reception_one_combined_scope.py" in node["evidence"]["tests"]
