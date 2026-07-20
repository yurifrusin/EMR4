import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-committed-event-vertical"
)
EVIDENCE = EVIDENCE_DIR / "browser-acceptance-evidence.json"
CLEANUP = EVIDENCE_DIR / "database-cleanup-evidence.json"
HARNESS = ROOT / "scripts" / "reception_one_committed_event_harness.py"
RUNNER = ROOT / "scripts" / "reception_one_committed_event_acceptance.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_harness_is_exact_migrated_synthetic_provider_free_and_cleanup_guarded():
    source = _read(HARNESS)

    assert 'LOCKED_DATABASE = "gp_pms_reception_one_event_runtime_5e2c91a7_20260721"' in source
    assert '[sys.executable, "-m", "alembic", "upgrade", "head"]' in source
    assert '"RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED": "true"' in source
    assert '"BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled"' in source
    assert '"BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false"' in source
    assert '"GOOGLE_APPLICATION_CREDENTIALS": ""' in source
    assert "Refusing to reuse the exact RLS probe role" in source
    assert "base.cleanup_database()" in source
    assert "probe_role_removed" in source


def test_runner_uses_real_browser_and_only_existing_signed_command_support():
    source = _read(RUNNER)

    assert "page.route(" not in source
    assert ".route(" not in source
    assert "markInterrupted()" not in source
    assert "window.dispatchEvent(new Event('blur'))" in source
    assert '"/appointments/proposals/update/confirm"' in source
    assert '"/appointments/proposals/update/' in source
    assert '"confirmed": True' not in source
    assert 'confirm_payload["confirmed"] = True' in source
    for forbidden in (
        "/appointments/proposals/create/confirm",
        "/appointments/proposals/delete",
        "/appointments/proposals/status",
        "/appointments/bernie/sessions",
        "page.evaluate(\"markInterrupted",
    ):
        assert forbidden not in source


def test_browser_database_security_and_responsive_evidence_passes():
    text = _read(EVIDENCE)
    evidence = json.loads(text)

    assert evidence["result"] == "browser_pass"
    assert evidence["evidence_mode"] == "live_local_browser_backend_postgres"
    assert evidence["support_command_evidence_mode"] == "live_local_backend_postgres"
    assert evidence["route_interception"] is False
    assert evidence["api_interception"] is False
    assert evidence["browser_console_warnings_or_errors"] == []
    assert evidence["browser_page_errors"] == []
    assert evidence["network"]["browser_forbidden_requests"] == []
    assert evidence["network"]["browser_failed_api_responses"] == []
    assert evidence["network"]["browser_mutation_requests"] == []
    assert evidence["support_commands"] == {
        "confirmed_reschedules": 2,
        "idempotent_replays": 1,
        "in_scope": 1,
        "other_mutations": 0,
        "out_of_scope": 1,
    }

    counts = evidence["database_readback"]["counts"]
    assert counts == {
        "appointment_audit_log": 2,
        "appointment_command_idempotency": 2,
        "appointments": 6,
        "bernie_booking_sessions": 0,
        "bernie_session_events": 0,
        "diary_committed_events": 2,
    }
    assert evidence["database_readback"]["correlated_event_rows"] == 2
    assert evidence["database_readback"]["payload_keys_exact"] is True
    assert evidence["database_readback"]["prohibited_payload_keys_present"] == []
    security = evidence["database_security"]
    assert security["append_only_update"] == "append_only_rejected"
    assert security["append_only_delete"] == "append_only_rejected"
    assert security["rls_own_practice_event_count"] == 2
    assert security["rls_foreign_practice_event_count"] == 0

    assert [row["id"] for row in evidence["viewports"]] == [
        "desktop_landscape",
        "tablet_landscape",
        "tablet_portrait",
        "smartphone_portrait",
        "smartphone_landscape",
    ]
    for row in evidence["viewports"]:
        assert row["page_horizontal_overflow_px"] == 0
        assert row["host_horizontal_overflow_px"] == 0
        assert row["enabled_controls_below_44px"] == []
        assert row["error_overlay_visible"] is False

    assert evidence["attention"] == {
        "dismiss": True,
        "duplicate_visible_effect": False,
        "mute_until_reload": True,
        "no_auto_focus_or_speech": True,
        "show_changed_appointment": True,
        "snooze_five_minutes": True,
        "unrelated_event_suppressed": True,
    }
    assert all(evidence["privacy"].values())
    assert evidence["interruption"]["fresh_appointment_read"] is True
    assert evidence["interruption"]["fresh_projection_read"] is True
    assert evidence["interruption"]["event_payload_used_as_display_truth"] is False

    for forbidden in (
        "Margaret",
        "Billy",
        "date_of_birth",
        "patient_id",
        "access_token",
        "password",
    ):
        assert forbidden not in text


def test_screenshots_are_hashed_painted_and_include_both_phone_orientations():
    evidence = json.loads(_read(EVIDENCE))
    expected = {
        "desktop-event-cue-1440x900.png",
        "tablet-landscape-event-cue-1024x768.png",
        "tablet-portrait-event-cue-768x1024.png",
        "smartphone-portrait-private-event-390x844.png",
        "smartphone-landscape-interruption-event-844x390.png",
    }
    assert {row["file"] for row in evidence["screenshots"]} == expected
    for row in evidence["screenshots"]:
        image = EVIDENCE_DIR / row["file"]
        assert image.is_file()
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["sha256"]
        assert row["raster_integrity"]["passes"] is True
        assert row["raster_integrity"]["painted_extent_ratio"] >= 0.95


def test_exact_database_and_probe_role_cleanup_is_recorded():
    cleanup = json.loads(_read(CLEANUP))
    assert cleanup == {
        "cleanup": "dropped_exact_verified_disposable_database",
        "database": "gp_pms_reception_one_event_runtime_5e2c91a7_20260721",
        "ownership_marker_verified": True,
        "probe_role_removed": True,
        "recoverable": False,
        "schema_version": "reception-one.committed-event.database-cleanup.v1",
        "scope": "authored_synthetic_disposable_database_and_exact_probe_role_only",
    }
