"""Static admission for bounded Reception One duration-only composition."""

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


def test_bridge_validates_duration_only_and_delegates_without_network() -> None:
    source = _source(DIARY_JS)
    bridge = _between(
        source,
        "async function metaGridResizeAppointmentDuration",
        "function setMetaGridLaunchAvailability",
    )

    assert "requestedDuration < 15" in bridge
    assert "requestedDuration > 480" in bridge
    assert "(requestedDuration - currentDuration) % 15 !== 0" in bridge
    assert "currentStartMins + requestedDuration >= 1440" in bridge
    assert "requestedDuration - currentDuration" in bridge
    assert "handleMoveResize(" in bridge
    assert "\n    0,\n    requestedDuration - currentDuration," in bridge
    assert "samePractitionerColumn" in bridge
    assert "metaGridReadAppointment(appointmentId)" in bridge
    assert "metaGridReadAppointmentSource(appointmentId)" in bridge
    assert 'dialogTitle: "Confirm Appointment Duration Change"' in bridge
    assert "apiFetch(" not in bridge
    assert 'method: "POST"' not in bridge
    assert 'method: "PUT"' not in bridge
    assert "confirmPayload" not in bridge
    assert "resizeAppointmentDuration: metaGridResizeAppointmentDuration" in source


def test_existing_interaction_parameterizes_dialog_but_owns_one_command_path() -> None:
    source = _source(DIARY_JS)
    interaction = _between(
        source,
        "async function handleMoveResize",
        "async function applySignedStatusProposal",
    )

    assert 'actionOptions?.dialogTitle || "Confirm Appointment Time Change"' in interaction
    assert "actionOptions?.dialogSummary" in interaction
    assert "actionOptions?.displayTransition" in interaction
    assert "`/appointments/proposals/update/${appt.id}`" in interaction
    assert "allowlistedConfirmApiPath(confirmEndpoint)" in interaction
    assert "updateConfirmIdempotencyKey(proposal, confirmPayload)" in interaction
    assert "currentTruthRecheck: true" in interaction
    assert 'method: "PUT"' not in interaction


def test_reception_one_duration_action_reconciles_and_is_mutually_exclusive() -> None:
    source = _source(META_GRID_JS)
    action = _between(
        source,
        "async function executeSelectedDurationAction",
        "function renderStatusAction",
    )
    render = _between(
        source,
        "function renderDurationAction",
        "function renderActions",
    )

    assert "bridge.resizeAppointmentDuration(" in action
    assert "clearTrail: true" in action
    assert "preserveSelectedAppointmentId: appointmentId" in action
    assert "applyFreshAppointmentToCurrentProjection(result.appointment)" in action
    assert "requireFreshActionReconciliation(" in action
    assert 'document.getElementById("meta-grid-duration-select")' in action
    assert "fetch(" not in action
    assert "/appointments" not in action
    assert "validDurationTargets(selected)" in render
    assert '"Review duration change"' in render
    assert 'feedback.setAttribute("aria-live", "polite")' in render
    assert "state.statusAction.busy || state.rescheduleAction.busy || state.durationAction.busy" in source
    assert "if (state.durationAction.busy)" in source


def test_duration_targets_preserve_non_multiple_current_duration_and_same_day() -> None:
    source = _source(META_GRID_JS)
    targets = _between(
        source,
        "function validDurationTargets",
        "function updateDurationActionControls",
    )

    assert "values = [currentDuration]" in targets
    assert "(target - currentDuration) % 15 !== 0" in targets
    assert "startMinutes + target >= 1440" in targets
    assert "target <= 480" in targets


def test_duration_panel_reuses_responsive_focus_treatment() -> None:
    source = _source(META_GRID_CSS)

    assert ".meta-grid-duration-action" in source
    assert ".meta-grid-duration-select:focus-visible" in source
    assert ".meta-grid-duration-submit:focus-visible" in source
    assert "@media (max-width: 700px)" in source
    assert ".meta-grid-duration-action-copy" in source
    assert ".meta-grid-duration-feedback" in source
