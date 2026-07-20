"""Guards for bounded Reception One availability reconciliation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs" / "diary"
PLAN = ROOT / "docs" / "bernie-reception-one-availability-reconciliation-plan.md"
THREAT_DELTA = (
    ROOT
    / "docs"
    / "security"
    / "bernie-reception-one-availability-reconciliation-threat-model-delta.md"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
NODE = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "reception-one-availability-reconciliation-node.json"
)
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-availability-reconciliation"
)
EVIDENCE = EVIDENCE_DIR / "browser-acceptance-evidence.json"
CLEANUP = EVIDENCE_DIR / "database-cleanup-evidence.json"
HARNESS = ROOT / "scripts" / "reception_one_availability_reconciliation_harness.py"
RUNNER = ROOT / "scripts" / "reception_one_availability_reconciliation_acceptance.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_freezes_exact_path_result_and_closed_boundaries():
    plan = _read(PLAN)

    for required in (
        "reception_one_availability_reconciliation_pass",
        "Show me all the available slots with Dr Shera for a half-hour appointment",
        "with Margaret Thompson after 2 today",
        "diary.appointment_rescheduled",
        "fresh appointment and exact availability reads",
        "candidate-set comparison",
        "gp_pms_reception_one_availability_reconcile_7c8e4f21_20260721",
        "live_local_browser_backend_postgres",
        "Stage 3B",
        "production, deployment and release",
    ):
        assert required in plan

    assert "RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED` remains false by default" in plan
    assert "It adds no\nevent family, command, API route, database model, migration" in plan


def test_candidate_identity_uses_slot_coordinates_not_freshness_token():
    source = _read(DIARY / "meta-grid.js")
    identity = source[
        source.index("function availabilitySlotIdentity") :
        source.index("function availabilityCandidateMap")
    ]

    for coordinate in (
        "item.practitioner_id",
        "item.location_id",
        "item.starts_at",
        "item.duration_minutes",
    ):
        assert coordinate in identity
    assert "freshness_token" not in identity
    assert "function availabilitySignature" in source
    assert 'sort().join("\\n")' in source


def test_reconciliation_requires_one_scoped_practitioner_and_fresh_reads():
    source = _read(DIARY / "meta-grid.js")
    consumer = source[
        source.index("async function consumeCommittedEvent") :
        source.index("function stopEventPolling")
    ]

    for required in (
        "currentAvailabilityProjectionEligible(current)",
        "current.scope?.practitioner_ids?.length === 1",
        "await bridge.readAppointment(aggregateId)",
        "freshAppointment.practitioner_id || \"\") !== scopedPractitionerId",
        "await freshAvailabilityForCommittedEvent(current)",
        "availabilityCandidateMap(next)",
        "availabilitySignature(next)",
    ):
        assert required in source or required in consumer
    assert "event.payload.start_time" not in consumer
    assert "event.payload.end_time" not in consumer


def test_surviving_and_invalid_selection_or_proposal_have_explicit_outcomes():
    source = _read(DIARY / "meta-grid.js")

    assert "const freshSelection = previousSelectionIdentity" in source
    assert "nextCandidates.get(previousSelectionIdentity) || null" in source
    assert "state.selectedItem = freshSelection" in source
    assert "state.proposalResult = null" in source
    assert "if (candidateSetChanged) {" in source
    assert "state.trail = [];" in source
    for outcome in (
        'cueOutcome = "availability_changed"',
        'cueOutcome = "selection_preserved"',
        'cueOutcome = "proposal_preserved"',
        '? "proposal_unavailable"',
        ': "selection_unavailable"',
    ):
        assert outcome in source
    for copy in (
        "Availability in this view changed. Reception One refreshed the current options.",
        "Availability in this view changed, but your selected time is still available.",
        "Availability in this view changed, but your proposed time is still available.",
        "That time is no longer available. Reception One refreshed the remaining options.",
        "That proposed time is no longer available. Reception One cleared the proposal",
        "Review current availability",
    ):
        assert copy in source


def test_async_result_cannot_overwrite_newer_root_close_or_interruption():
    source = _read(DIARY / "meta-grid.js")
    consumer = source[
        source.index("async function consumeCommittedEvent") :
        source.index("function stopEventPolling")
    ]

    assert "const initiatingProjectionId = current?.projection_id" in consumer
    assert consumer.count("state.current?.projection_id !== initiatingProjectionId") >= 2
    assert "!state.isOpen ||" in consumer
    assert "state.interrupted ||" in consumer
    assert 'items: (state.current.items || []).map(item => ({ ...item, selected: false }))' in source
    interruption = source[source.index("function markInterrupted") : source.index("function renderRootHistory")]
    assert "state.trail = [];" in interruption


def test_attention_remains_nonmodal_private_keyboard_safe_and_read_only():
    source = _read(DIARY / "meta-grid.js")
    html = _read(DIARY / "diary.html")

    assert "meta-grid.js?v=10" in html
    assert 'elements.eventShow.disabled = state.private' in source
    assert 'elements.announcer.textContent = "Availability in the current view changed.' in source
    assert "showEventContext" in source
    assert "if (dismissEventCue() || closeExplanation())" in source
    assert "appointment_write_authority: false" in source
    for forbidden in (
        "fetch(",
        "page.route(",
        "new WebSocket",
        "new EventSource",
        "serviceWorker",
        "localStorage",
        "sessionStorage",
        "SpeechRecognition",
        "webkitSpeechRecognition",
        "/confirm",
    ):
        assert forbidden not in source


def test_api_spine_declares_fresh_comparison_without_event_command_authority():
    async_contract = yaml.safe_load(
        _read(ROOT / "docs" / "api-spine" / "async" / "integration-events.yaml")
    )
    charter = yaml.safe_load(
        _read(ROOT / "docs" / "api-spine" / "manifests" / "agent-capability-charters.yaml")
    )

    exception = async_contract["source_safety"]["bounded_local_runtime_exception"]
    assert (
        exception["consumer_reconciliation"]
        == "exact_active_practitioner_availability_selection_proposal"
    )
    diary_family = next(
        row for row in async_contract["event_families"] if row["family_id"] == "diary"
    )
    subset = diary_family["authorised_runtime_subset"]
    assert subset["availability_reconciliation"] == "fresh_slot_search_candidate_comparison"
    attention = diary_family["attention_boundary"]
    assert attention["unchanged_availability_silent"] is True
    assert attention["invalid_selected_or_proposed_slot_cleared"] is True
    assert diary_family["command_boundary"]["automatic_proposal_from_event"] is False

    bernie = next(row for row in charter["agents"] if row["agent_id"] == "bernie")
    runtime = bernie["bounded_runtime_authority"]
    assert runtime["relevance"] == (
        "deterministic_appointment_membership_or_active_practitioner_availability"
    )
    assert runtime["availability_reconciliation"] == "fresh_backend_candidate_comparison"
    assert runtime["automatic_proposal_from_event"] is False
    assert runtime["appointment_write_authority"] is False


def test_threat_delta_covers_stale_state_noise_races_privacy_and_escalation():
    threat = _read(THREAT_DELTA)

    for required in (
        "Event payload is treated as availability truth",
        "Other-practitioner or same-practitioner irrelevant changes create alert noise",
        "Freshness-token churn is mistaken for a changed slot",
        "Occupied selected or proposed slot remains actionable",
        "Slow reconciliation overwrites a newer root",
        "Shared-screen cue reveals patient or time",
        "Availability attention becomes a command tunnel",
    ):
        assert required in threat


def test_ariadne_records_open_descendant_contract_until_evidence_exists():
    graph = json.loads(_read(GRAPH))
    node = json.loads(_read(NODE))

    assert graph["graph_revision"] == 13
    contract = next(
        row
        for row in graph["contracts"]
        if row["id"] == "committed-reschedule-availability-reconciliation"
    )
    assert contract["source_node"] == "reception-one-committed-event-vertical"
    assert contract["required_evidence_types"] == ["tests", "closeouts"]
    assert node["status"] == "active"
    assert node["relationships"] == [
        {"node_id": "reception-one-committed-event-vertical", "relation": "builds_on"}
    ]
    reconciliation = next(
        row
        for row in node["contract_evidence"]
        if row["contract_id"] == "committed-reschedule-availability-reconciliation"
    )
    assert reconciliation["status"] == "gap"


def test_exact_harness_and_runner_preserve_runtime_and_write_boundaries():
    harness = _read(HARNESS)
    runner = _read(RUNNER)

    assert (
        'LOCKED_DATABASE = "gp_pms_reception_one_availability_reconcile_7c8e4f21_20260721"'
        in harness
    )
    assert 'RUNTIME_TAG = "reception-one-availability-reconcile-7c8e4f21"' in harness
    assert "event_base.create_schema_and_seed(password)" in harness
    assert "event_base.cleanup_database()" in harness
    assert 'AUTH_URL = "http://[::1]:3000/meta-grid-auth.html"' in runner
    assert "page.route(" not in runner
    assert ".route(" not in runner
    assert "markInterrupted()" not in runner
    assert 'window.dispatchEvent(new Event(\'blur\'))' in runner
    assert "meta-grid-proposal-handoff\").click" not in runner
    assert runner.count("_confirmed_reschedule(") == 2
    for forbidden in (
        "/appointments/proposals/create/confirm",
        "/appointments/bernie/sessions",
        "page.evaluate(\"consumeCommittedEvent",
        "page.evaluate(\"markInterrupted",
    ):
        assert forbidden not in runner


def test_live_browser_database_and_responsive_evidence_passes():
    evidence_text = _read(EVIDENCE)
    evidence = json.loads(evidence_text)

    assert evidence["result"] == "browser_pass"
    assert evidence["evidence_mode"] == "live_local_browser_backend_postgres"
    assert evidence["support_command_evidence_mode"] == "live_local_backend_postgres"
    assert evidence["route_interception"] is False
    assert evidence["api_interception"] is False
    assert evidence["runtime"] == {
        "active_ipv4_contact": False,
        "cloud_credentials_present": False,
        "credential_recorded": False,
        "database": "gp_pms_reception_one_availability_reconcile_7c8e4f21_20260721",
        "feature_enabled_only_in_exact_harness": True,
        "loopback_family": "ipv6",
        "provider": "disabled",
        "token_recorded": False,
    }
    assert evidence["network"]["browser_forbidden_requests"] == []
    assert evidence["network"]["browser_failed_api_responses"] == []
    assert evidence["network"]["browser_write_requests"] == []
    assert evidence["browser_console_warnings_or_errors"] == []
    assert evidence["browser_page_errors"] == []
    assert evidence["support_commands"] == {
        "confirmed_reschedules": 2,
        "idempotent_replays": 1,
        "other_mutations": 0,
        "same_target": True,
    }

    assert evidence["database_readback"]["counts"] == {
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
    assert evidence["database_security"]["append_only_update"] == "append_only_rejected"
    assert evidence["database_security"]["append_only_delete"] == "append_only_rejected"
    assert evidence["database_security"]["rls_own_practice_event_count"] == 2
    assert evidence["database_security"]["rls_foreign_practice_event_count"] == 0

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

    reconciliation = evidence["reconciliation"]
    assert reconciliation["event_payload_used_as_display_truth"] is False
    assert reconciliation["duplicate_visible_effect"] is False
    assert all(
        value
        for key, value in reconciliation.items()
        if key not in {"event_payload_used_as_display_truth", "duplicate_visible_effect"}
    )
    keyboard = evidence["keyboard"]
    assert keyboard["page_internal_command_invocation"] is False
    assert keyboard["native_tab_sequence"]
    assert all(
        value
        for key, value in keyboard.items()
        if key not in {"page_internal_command_invocation", "native_tab_sequence"}
    )
    assert all(evidence["privacy"].values())
    assert evidence["interruption"]["stale_selection_or_proposal_restored"] is False
    assert evidence["interruption"]["fresh_read_required"] is True
    for forbidden in (
        "Margaret",
        "Billy",
        "date_of_birth",
        "patient_id",
        "access_token",
        "password",
    ):
        assert forbidden not in evidence_text


def test_screenshots_are_current_hashed_painted_and_cover_all_viewports():
    evidence = json.loads(_read(EVIDENCE))
    assert {row["file"] for row in evidence["screenshots"]} == {
        "desktop-selection-unavailable-1440x900.png",
        "tablet-landscape-selection-preserved-1024x768.png",
        "tablet-portrait-availability-changed-768x1024.png",
        "smartphone-portrait-private-proposal-cleared-390x844.png",
        "smartphone-landscape-interruption-844x390.png",
    }
    for row in evidence["screenshots"]:
        image = EVIDENCE_DIR / row["file"]
        assert image.is_file()
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["sha256"]
        assert row["raster_integrity"]["passes"] is True
        assert row["raster_integrity"]["painted_extent_ratio"] >= 0.95


def test_exact_marker_verified_database_and_probe_role_cleanup_is_recorded():
    assert json.loads(_read(CLEANUP)) == {
        "cleanup": "dropped_exact_verified_disposable_database",
        "database": "gp_pms_reception_one_availability_reconcile_7c8e4f21_20260721",
        "ownership_marker_verified": True,
        "probe_role_removed": True,
        "recoverable": False,
        "schema_version": "reception-one.availability-reconciliation.database-cleanup.v1",
        "scope": "authored_synthetic_disposable_database_and_exact_probe_role_only",
    }
