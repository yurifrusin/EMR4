"""Static admission for the bounded Reception One time-reschedule composition."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
META_GRID_JS = ROOT / "docs" / "diary" / "meta-grid.js"
META_GRID_CSS = ROOT / "docs" / "diary" / "meta-grid.css"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _between(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def test_bridge_delegates_time_only_change_without_network_or_write_path() -> None:
    source = _source(DIARY_JS)
    bridge = _between(
        source,
        "async function metaGridRescheduleAppointmentTime",
        "async function metaGridResizeAppointmentDuration",
    )

    assert "requestedStartMins % 15 !== 0" in bridge
    assert "requestedStartMins + duration > 1440" in bridge
    assert "requestedStartMins - currentStartMins" in bridge
    assert "handleMoveResize(" in bridge
    assert "\n    0,\n    samePractitionerColumn," in bridge
    assert "metaGridReadAppointment(appointmentId)" in bridge
    assert "apiFetch(" not in bridge
    assert 'method: "POST"' not in bridge
    assert 'method: "PUT"' not in bridge
    assert "confirmPayload" not in bridge
    assert "rescheduleAppointmentTime: metaGridRescheduleAppointmentTime" in source


def test_existing_move_resize_path_owns_proposal_confirm_and_typed_phases() -> None:
    source = _source(DIARY_JS)
    interaction = _between(
        source,
        "async function handleMoveResize",
        "async function applySignedStatusProposal",
    )

    assert "deltaDuration" in interaction
    assert "notify(\"checking\", true)" in interaction
    assert "notify(\"awaiting_confirmation\", true)" in interaction
    assert "notify(\"saving\", true)" in interaction
    assert "notify(\"committed\", false)" in interaction
    assert "notify(\"failed\", false)" in interaction
    assert "`/appointments/proposals/update/${appt.id}`" in interaction
    assert "allowlistedConfirmApiPath(confirmEndpoint)" in interaction
    assert "updateConfirmIdempotencyKey(proposal, confirmPayload)" in interaction
    assert 'actionOptions?.dialogTitle || "Confirm Appointment Time Change"' in interaction
    assert "currentTruthRecheck: true" in interaction
    assert 'method: "PUT"' not in interaction


def test_reception_one_owns_presentation_reconciliation_and_interruption_only() -> None:
    source = _source(META_GRID_JS)
    action = _between(
        source,
        "async function executeSelectedRescheduleAction",
        "function renderStatusAction",
    )
    render = _between(
        source,
        "function renderRescheduleAction",
        "function renderDurationAction",
    )

    assert "bridge.rescheduleAppointmentTime(" in action
    assert "clearTrail: true" in action
    assert "preserveSelectedAppointmentId: appointmentId" in action
    assert "applyFreshAppointmentToCurrentProjection(result.appointment)" in action
    assert 'document.getElementById("meta-grid-reschedule-time")' in action
    assert "fetch(" not in action
    assert "/appointments" not in action
    assert 'input.step = "900"' in render
    assert '"Review time change"' in render
    assert 'feedback.setAttribute("aria-live", "polite")' in render
    for busy in (
        "state.statusAction.busy",
        "state.rescheduleAction.busy",
        "state.durationAction.busy",
        "state.practitionerAction.busy",
    ):
        assert busy in source
    assert "if (state.rescheduleAction.busy)" in source


def test_fresh_projection_patch_replaces_coordinates_without_optimism() -> None:
    source = _source(META_GRID_JS)
    patch = _between(
        source,
        "function applyFreshAppointmentToCurrentProjection",
        "async function executeSelectedStatusAction",
    )

    for field in (
        "appointment.appointment_date",
        "appointment.start_time_local",
        "appointment.end_time_local",
        "appointment.duration_minutes",
        "appointment.practitioner_id",
        "appointment.status",
    ):
        assert field in patch
    assert "requestedStart" not in patch
    assert "Fresh exact appointment read after selected appointment action" in patch


def test_reschedule_panel_has_bounded_responsive_and_focus_treatment() -> None:
    source = _source(META_GRID_CSS)

    assert ".meta-grid-reschedule-action" in source
    assert ".meta-grid-reschedule-time:focus-visible" in source
    assert ".meta-grid-reschedule-submit:focus-visible" in source
    assert "@media (max-width: 700px)" in source
    assert ".meta-grid-reschedule-action-copy" in source
    assert ".meta-grid-reschedule-feedback" in source
