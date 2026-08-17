from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs/diary/diary.js"
HTML = ROOT / "docs/diary/diary.html"


def _between(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    return text[start_index : text.index(end, start_index)]


def test_shared_delete_proposal_admission_binds_both_clients() -> None:
    source = DIARY.read_text(encoding="utf-8")
    validator = _between(
        source,
        "function validateDeleteProposalForConfirmation(",
        "function validateDeleteConfirmPublicEnvelope(",
    )
    bridge = _between(
        source,
        "async function metaGridCancelAppointment(",
        "window.EMR4DiaryMetaGridBridge",
    )
    ordinary = _between(
        source,
        "async function deleteBooking()",
        "// ─── PATIENT FLOW WORKBENCH",
    )

    for binding in (
        "appointment_id",
        "status_reason_code",
        "cancellation_reason",
        'intent === "delete_appointment"',
        'autonomy_tier === "blocked"',
        'autonomy_tier === "proposal"',
        '"/appointments/proposals/delete/confirm"',
    ):
        assert binding in validator
    assert "validateDeleteProposalForConfirmation" in bridge
    assert "validateDeleteProposalForConfirmation" in ordinary


def test_ordinary_consumer_is_delete_only_and_never_optimistic() -> None:
    source = DIARY.read_text(encoding="utf-8")
    ordinary = _between(
        source,
        "async function deleteBooking()",
        "// ─── PATIENT FLOW WORKBENCH",
    )

    assert "/appointments/proposals/delete/${encodeURIComponent(appointmentId)}" in ordinary
    assert "/appointments/proposals/status/" not in ordinary
    assert "status-confirm" not in ordinary
    assert 'method: "DELETE"' not in ordinary
    assert "mockAppointmentsCache = mockAppointmentsCache.filter" not in ordinary
    assert "Cancellation is not simulated in built-in smoke mode" in ordinary
    assert "showStatusProposalDialog(proposal)" in ordinary
    assert "reconcileOrdinaryCancellation(appointmentId)" in ordinary


def test_delete_dispatcher_accepts_only_minimal_public_receipt() -> None:
    source = DIARY.read_text(encoding="utf-8")
    dispatcher = _between(
        source,
        "async function applySignedDeleteProposal(",
        "async function setAppointmentStatus(",
    )

    assert "validateDeleteProposalForConfirmation(proposal, expected)" in dispatcher
    assert 'normalizeApiPath(confirmEndpoint) !== "/appointments/proposals/delete/confirm"' in dispatcher
    assert 'apiFetch("/appointments/proposals/delete/confirm"' in dispatcher
    assert "deleteConfirmIdempotencyKey(proposal, confirmPayload)" in dispatcher
    assert "validateDeleteConfirmPublicEnvelope" in dispatcher
    assert "confirmResult.appointment" not in dispatcher
    assert "statusConfirmIdempotencyKey" not in dispatcher
    assert "allowlistedConfirmApiPath" not in dispatcher


def test_reconciliation_exposes_success_and_fail_closed_results() -> None:
    source = DIARY.read_text(encoding="utf-8")
    loader = _between(
        source,
        "async function loadAuthenticatedDiary(",
        "// ─── DATE NAVIGATION",
    )
    controls = _between(
        source,
        "function resetOrdinaryCancellationControls(",
        "async function deleteBooking()",
    )

    assert "return true;" in loader
    assert loader.count("return false;") >= 3
    assert "refreshed !== true" in controls
    assert 'dataset.refreshRequired = "true"' in controls
    assert 'textContent = "Refresh Required"' in controls
    assert "deleteBtn.disabled = true" in controls
    assert "no outcome has been assumed" in controls


def test_diary_cache_reference_advances_with_client_change() -> None:
    html = HTML.read_text(encoding="utf-8")

    assert '<script src="diary.js?v=205" defer></script>' in html
