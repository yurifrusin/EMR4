"""Deterministic guards for provider-disabled live-local meta-grid evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs" / "diary"
PLAN = ROOT / "docs" / "bernie-meta-grid-live-local-integration-evaluation-plan.md"
HARNESS = ROOT / "scripts" / "bernie_meta_grid_live_local_harness.py"
RUNNER = ROOT / "scripts" / "bernie_meta_grid_live_local_acceptance.py"
EVIDENCE_DIR = ROOT / "orchestration" / "prototypes" / "bernie-meta-grid-live-local-integration"
EVIDENCE = EVIDENCE_DIR / "browser-acceptance-evidence.json"
CLEANUP_EVIDENCE = EVIDENCE_DIR / "database-cleanup-evidence.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_freezes_live_local_scope_and_closed_gates():
    plan = _read(PLAN)
    for required in (
        "live_local_browser_backend_postgres",
        "gp_pms_meta_grid_live_local_7f3c2a91_20260720",
        "interpreter provider to `disabled`",
        "desktop landscape",
        "tablet landscape",
        "tablet portrait",
        "smartphone portrait",
        "smartphone landscape",
        "Plain-language",
        "painted-content bounding box",
        "bernie_booking_sessions",
        "bernie_session_events",
        "fresh Gemini",
        "Stage 3B",
        "deployment",
        "release",
    ):
        assert required in plan


def test_standalone_office_bootstrap_is_loopback_only_and_preserves_office_loading():
    html = _read(DIARY / "diary.html")
    bootstrap = _read(DIARY / "office-bootstrap.js")
    assert '<script src="office-bootstrap.js?v=2"></script>' in html
    assert "appsforoffice.microsoft.com" not in html
    assert '["127.0.0.1", "localhost"]' in bootstrap
    assert 'params.get("standalone_diary") === "true"' in bootstrap
    assert "window.Office = Object.freeze" in bootstrap
    assert "appsforoffice.microsoft.com/lib/1/hosted/office.js" in bootstrap
    assert "document.write" in bootstrap


def test_interrupted_proposal_recovers_fresh_availability_not_stale_proposal():
    source = _read(DIARY / "meta-grid.js")
    refresh = source[source.index("async function refreshCurrent()") : source.index("async function routeRequest")]
    assert 'current.family === "proposal_review" && practitioners[0]' in refresh
    assert "next = await buildAvailability" in refresh
    assert "Proposal and patient selection are deliberately discarded" in refresh
    assert '<script src="meta-grid.js?v=9" defer>' in _read(DIARY / "diary.html")


def test_harness_is_exact_disposable_synthetic_and_provider_disabled():
    source = _read(HARNESS)
    assert 'LOCKED_DATABASE = "gp_pms_meta_grid_live_local_7f3c2a91_20260720"' in source
    assert '"BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled"' in source
    assert '"BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false"' in source
    assert '"GOOGLE_APPLICATION_CREDENTIALS": ""' in source
    assert "Refusing to reuse existing live-local database" in source
    assert "Refusing cleanup: the exact synthetic ownership marker is absent" in source
    assert "DROP DATABASE" in source
    assert '"bernie_booking_sessions"' in source
    assert '"bernie_session_events"' in source
    assert '"appointment_command_idempotency"' in source
    assert '"fake"' not in source


def test_playwright_runner_has_no_route_interception_or_closed_command_activation():
    source = _read(RUNNER)
    assert "page.route(" not in source
    assert ".route(" not in source
    assert "Continue to booking review\").click" not in source
    assert "meta-grid-proposal-handoff" in source
    assert "to_be_enabled" in source
    assert "window.dispatchEvent(new Event('blur'))" in source
    assert "markInterrupted()" not in source
    assert '"/api/v1/appointments/bernie/sessions' not in source
    assert '"/api/v1/appointments/proposals/create/confirm' not in source


def test_harness_cli_never_logs_database_derived_report_values():
    source = _read(HARNESS)
    assert "print(json.dumps(report" not in source
    assert '"report_values_recorded": False' in source
    assert '"bernie.meta-grid-live-local.cli-status.v1"' in source


def test_disposable_database_cleanup_is_exact_and_marker_verified():
    cleanup = json.loads(_read(CLEANUP_EVIDENCE))
    assert cleanup == {
        "schema_version": "bernie.meta-grid-live-local.database-cleanup.v1",
        "recorded_at": "2026-07-20T17:06:15+10:00",
        "database": "gp_pms_meta_grid_live_local_7f3c2a91_20260720",
        "ownership_marker_verified": True,
        "cleanup": "dropped_exact_verified_disposable_database",
        "recoverable": False,
        "scope": "authored_synthetic_disposable_database_only",
    }


def test_live_local_browser_evidence_is_complete_hashed_and_zero_write():
    evidence_text = _read(EVIDENCE)
    evidence = json.loads(evidence_text)
    assert evidence["result"] == "browser_pass"
    assert evidence["evidence_mode"] == "live_local_browser_backend_postgres"
    assert evidence["route_interception"] is False
    assert evidence["api_interception"] is False
    assert "bernie_session=false" in evidence["route"]
    assert "standalone_diary=true" in evidence["route"]
    assert evidence["runtime"]["provider"] == "disabled"
    assert evidence["runtime"]["cloud_credentials_present"] is False
    assert evidence["runtime"]["credential_recorded"] is False
    assert evidence["runtime"]["token_recorded"] is False
    assert evidence["authority"] == {
        "appointment_write_authority": False,
        "confirmation_control_activated": False,
        "event_runtime_activated": False,
        "operational_receipt_produced": False,
        "proposal_handoff_activated": False,
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

    assert evidence["network"]["only_loopback"] is True
    assert evidence["network"]["forbidden_requests"] == []
    assert evidence["network"]["failed_api_responses"] == []
    observed = {
        (row["method"], row["path"])
        for row in evidence["network"]["api_method_path_counts"]
    }
    assert ("GET", "/api/v1/appointments") in observed
    assert ("GET", "/api/v1/patients/search") in observed
    assert ("POST", "/api/v1/appointments/proposals/slot-search") in observed
    assert (
        "POST",
        "/api/v1/appointments/proposals/bernie/supervised-booking",
    ) in observed
    assert not any("/confirm" in path or "/sessions" in path for _method, path in observed)

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

    assert evidence["keyboard"]["enter_request_submit"].startswith("pass")
    assert evidence["keyboard"]["space_slot_selection"].startswith("pass")
    assert evidence["keyboard"]["escape_explanation_dismissal"].startswith("pass")
    assert evidence["browser_console_warnings_or_errors"] == []
    assert evidence["browser_page_errors"] == []
    assert "Margaret" not in evidence_text
    assert "date_of_birth" not in evidence_text
    assert "patient_id" not in evidence_text

    scripts_path = str(ROOT / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    from bernie_meta_grid_live_local_acceptance import png_painted_width

    expected_files = {
        "desktop-live-local-1440x900.png",
        "tablet-landscape-proposal-1024x768.png",
        "tablet-portrait-back-768x1024.png",
        "phone-portrait-proposal-private-390x844.png",
        "phone-portrait-interruption-390x844.png",
        "phone-landscape-comparison-844x390.png",
    }
    assert {row["file"] for row in evidence["screenshots"]} == expected_files
    for record in evidence["screenshots"]:
        screenshot = EVIDENCE_DIR / record["file"]
        assert screenshot.is_file()
        assert hashlib.sha256(screenshot.read_bytes()).hexdigest() == record["sha256"]
        measured = png_painted_width(screenshot)
        assert measured == record["raster_integrity"]
        assert measured["passes"] is True
    desktop = next(
        row for row in evidence["screenshots"] if row["file"].startswith("desktop-")
    )
    assert desktop["raster_integrity"]["width"] == 1440
    assert desktop["raster_integrity"]["painted_extent_ratio"] >= 0.95
    assert desktop["raster_integrity"]["rightmost_20_percent_nonblack_ratio"] >= 0.1
