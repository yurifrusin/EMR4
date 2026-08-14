"""Static admission for bounded Reception One practitioner reassignment."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
META_GRID_JS = ROOT / "docs" / "diary" / "meta-grid.js"
META_GRID_CSS = ROOT / "docs" / "diary" / "meta-grid.css"
APPOINTMENTS_PY = ROOT / "app" / "routers" / "appointments.py"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _between(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def test_bridge_requires_fresh_active_target_and_delegates_zero_deltas() -> None:
    source = _source(DIARY_JS)
    bridge = _between(
        source,
        "async function metaGridReassignAppointmentPractitioner",
        "function setMetaGridLaunchAvailability",
    )

    assert "metaGridReadAppointmentSource(appointmentId)" in bridge
    assert "loadPractitionerDirectory()" in bridge
    assert "normalizePractitionerDirectory(" in bridge
    assert "row.active === true" in bridge
    assert "matches.length !== 1" in bridge
    assert "currentPractitionerId === requestedPractitionerId" in bridge
    assert "handleMoveResize(" in bridge
    assert "\n    0,\n    0,\n    targetColumn," in bridge
    assert "admittedPractitioner: Object.freeze({" in bridge
    assert "id: requestedPractitionerId" in bridge
    assert "displayName: target.display_name" in bridge
    assert "metaGridReadAppointment(appointmentId)" in bridge
    assert 'dialogTitle: "Confirm Appointment Practitioner Change"' in bridge
    assert "apiFetch(" not in bridge
    assert 'method: "POST"' not in bridge
    assert 'method: "PUT"' not in bridge
    assert "confirmPayload" not in bridge
    assert (
        "reassignAppointmentPractitioner: metaGridReassignAppointmentPractitioner"
        in source
    )


def test_existing_move_resize_accepts_exact_id_but_owns_one_command_path() -> None:
    source = _source(DIARY_JS)
    interaction = _between(
        source,
        "async function handleMoveResize",
        "async function applySignedStatusProposal",
    )

    assert "column?.practitioner_id" in interaction
    assert "targetPractitionerId" in interaction
    assert "actionOptions?.admittedPractitioner" in interaction
    assert 'String(admittedPractitioner.id || "") !== targetPractitionerId' in interaction
    assert "directoryTarget?.displayName" in interaction
    assert "`/appointments/proposals/update/${appt.id}`" in interaction
    assert "allowlistedConfirmApiPath(confirmEndpoint)" in interaction
    assert "updateConfirmIdempotencyKey(proposal, confirmPayload)" in interaction
    assert "currentTruthRecheck: true" in interaction
    assert 'method: "PUT"' not in interaction


def test_existing_command_rechecks_changed_target_activity_at_confirmation() -> None:
    source = _source(APPOINTMENTS_PY)
    proposal = _between(
        source,
        "def propose_update_appointment",
        "def _bernie_tool_issue",
    )
    confirmation = _between(
        source,
        "def confirm_update_proposal",
        "def _appointment_status_command_payload",
    )

    assert "practitioner_changed = practitioner_id != appt.practitioner_id" in proposal
    assert "Practitioner.is_active.is_(True)" in proposal
    assert 'code="practitioner_inactive"' in proposal
    assert "revalidated = propose_update_appointment(" in confirmation


def test_action_targets_only_active_distinct_rows_and_reconciles() -> None:
    source = _source(META_GRID_JS)
    targets = _between(
        source,
        "function activePractitionerTargets",
        "function updatePractitionerActionControls",
    )
    action = _between(
        source,
        "async function executeSelectedPractitionerAction",
        "function renderStatusAction",
    )

    assert "practitioner?.active === true" in targets
    assert "id !== currentId" in targets
    assert "counts.get(id) === 1" in targets
    assert "bridge.reassignAppointmentPractitioner(" in action
    assert "clearTrail: true" in action
    assert "preserveSelectedAppointmentId: appointmentId" in action
    assert "applyFreshAppointmentToCurrentProjection(result.appointment)" in action
    assert "bridge.readAppointment(appointmentId)" in action
    assert "requireFreshActionReconciliation(" in action
    assert 'document.getElementById("meta-grid-practitioner-select")' in action
    assert "fetch(" not in action
    assert "/appointments" not in action


def test_panel_is_accessible_provisional_and_four_way_exclusive() -> None:
    source = _source(META_GRID_JS)
    render = _between(
        source,
        "function renderPractitionerAction",
        "function renderActions",
    )

    assert '"New practitioner"' in render
    assert '"Review practitioner change"' in render
    assert "activePractitionerTargets(selected)" in render
    assert 'feedback.setAttribute("aria-live", "polite")' in render
    assert "Current practitioner:" in render
    assert "share one provisional update draft" in render
    assert "Current practitioner activity and Diary truth are checked again" in render
    for busy in (
        "state.statusAction.busy",
        "state.rescheduleAction.busy",
        "state.durationAction.busy",
        "state.practitionerAction.busy",
    ):
        assert busy in source
    assert "if (state.practitionerAction.busy)" in source


def test_practitioner_panel_reuses_responsive_focus_treatment() -> None:
    source = _source(META_GRID_CSS)

    assert ".meta-grid-practitioner-action" in source
    assert ".meta-grid-practitioner-select:focus-visible" in source
    assert ".meta-grid-practitioner-submit:focus-visible" in source
    assert "@media (max-width: 700px)" in source
    assert ".meta-grid-practitioner-action-copy" in source
    assert ".meta-grid-practitioner-feedback" in source
