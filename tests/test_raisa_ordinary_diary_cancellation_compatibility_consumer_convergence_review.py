from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY = ROOT / "docs/diary/diary.js"
ROUTER = ROOT / "app/routers/appointments.py"
SCHEMAS = ROOT / "app/schemas/appointments.py"
PLAN = ROOT / "docs/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-plan.md"
REPORT = ROOT / "docs/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review.md"
THREAT = ROOT / "docs/security/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-threat-model-delta.md"


def _between(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    return text[start_index : text.index(end, start_index)]


def test_current_ordinary_delete_consumer_has_converged_on_canonical_family() -> None:
    source = DIARY.read_text(encoding="utf-8")
    delete_booking = _between(
        source,
        "async function deleteBooking()",
        "// ─── PATIENT FLOW WORKBENCH",
    )

    assert "/appointments/proposals/delete/${encodeURIComponent(appointmentId)}" in delete_booking
    assert "/appointments/proposals/status/${editingAppointmentId}" not in delete_booking
    assert "Fallback to status proposal" not in delete_booking
    assert 'err.message.includes("404")' not in delete_booking
    assert "validateDeleteProposalForConfirmation" in delete_booking
    assert "await applySignedDeleteProposal(" in delete_booking
    assert "reconcileOrdinaryCancellation(appointmentId)" in delete_booking
    assert "setOrdinaryCancellationRefreshRequired" in delete_booking
    assert "method: \"DELETE\"" not in delete_booking


def test_current_dispatcher_accepts_only_canonical_minimal_public_envelope() -> None:
    source = DIARY.read_text(encoding="utf-8")
    dispatcher = _between(
        source,
        "async function applySignedDeleteProposal(",
        "async function setAppointmentStatus(",
    )

    assert "validateDeleteProposalForConfirmation(proposal, expected)" in dispatcher
    assert 'normalizeApiPath(confirmEndpoint) !== "/appointments/proposals/delete/confirm"' in dispatcher
    assert 'apiFetch("/appointments/proposals/delete/confirm"' in dispatcher
    assert "allowlistedConfirmApiPath(confirmEndpoint)" not in dispatcher
    assert "statusConfirmIdempotencyKey" not in dispatcher
    assert "deleteConfirmIdempotencyKey(proposal, confirmPayload)" in dispatcher
    assert "confirmResult.appointment" not in dispatcher
    assert "validateDeleteConfirmPublicEnvelope" in dispatcher
    assert "return publicEnvelope" in dispatcher


def test_canonical_bridge_and_backend_public_contract_are_exact_controls() -> None:
    diary = DIARY.read_text(encoding="utf-8")
    bridge = _between(
        diary,
        "async function metaGridCancelAppointment(",
        "window.EMR4DiaryMetaGridBridge",
    )
    router = ROUTER.read_text(encoding="utf-8")
    schemas = SCHEMAS.read_text(encoding="utf-8")

    assert bridge.count("/appointments/proposals/delete/confirm") >= 2
    assert "validateDeleteProposalForConfirmation" in bridge
    assert "/appointments/proposals/status/" not in bridge
    assert "validateDeleteConfirmPublicEnvelope" in bridge
    assert '"/proposals/delete/confirm"' in router
    assert "canonical_delete_confirm_envelope_bytes(result.body)" in router
    assert "class AppointmentConfirmDeleteProposalOut" in schemas
    public_schema = _between(
        schemas,
        "class AppointmentConfirmDeleteProposalOut",
        "class ScheduleSlot",
    )
    assert "receipt:" in public_schema
    assert "appointment:" not in public_schema
    assert 'model_config = ConfigDict(extra="forbid")' in public_schema


def test_review_freezes_one_client_only_fail_closed_convergence() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    joined = "\n".join((plan, report, threat))

    assert "Date: 2026-08-17" in plan
    assert "Timestamp:" in plan and "Australia/Brisbane" in plan
    assert "repository_static_authored_synthetic" in report
    assert "remove the 404-to-status semantic fallback" in report
    assert "raisa.delete_confirm_public_envelope.v1" in report
    assert "fresh authorised Diary read after every terminal or uncertain result" in report
    assert "docs/diary/diary.js" in report
    assert "Open Yuri decision: none" in report
    assert "No product or API source changes" in threat
    assert "no_raw_compatibility_delete_or_status_cancel_fallback_call" not in joined
    assert "docs/branding/" in joined
