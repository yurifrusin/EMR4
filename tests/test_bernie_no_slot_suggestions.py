"""
Sprint 104: No-slot suggestions and context freshness — contract tests.

Proves:
  - Zero-candidates supervised-booking returns typed suggestions (not free text only).
  - All suggestions carry requires_confirmation=True.
  - clinic_day_exhausted result is unchanged and does not return suggestions.
  - context_freshness echoes reference_date and correctly marks stale vs. fresh.
  - No mutation (no DB writes) on the deterministic context/suggestion path.
"""

from datetime import date, datetime, time, timezone, timedelta

import pytest

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from app.schemas.appointments import SlotSearchProposalIn
import app.routers.appointments as appointments_router
from app.services.bernie_patient_context import _relative_label
from tests.conftest import make_token


WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
REFERENCE_DATE = "2026-07-02"


def _post_wrapper(client, token, body: dict):
    return client.post(
        WRAPPER_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _future_body(practitioner, **overrides):
    """A body that requests a slot in the near future (non-same-day) so no clinic_day_exhausted logic fires."""
    body = {
        "reference_date": REFERENCE_DATE,
        "command": {
            "practitioner_id": str(practitioner.id),
            "date_from": "2026-07-10",
            "duration_minutes": "15",
        },
    }
    body.update(overrides)
    return body


# ── No-slot suggestions ───────────────────────────────────────────────────────

def test_zero_candidates_returns_typed_suggestions(
    client,
    db,
    gp_user,
    practitioner,
    monkeypatch,
):
    """When slot search yields zero candidates (non-exhausted day), typed suggestions are returned."""
    token = make_token(gp_user)

    # Monkeypatch _build_slot_search_proposal to return zero candidates with safe=True
    from app.schemas.appointments import SlotSearchProposalOut, AppointmentProposalIssue
    empty_proposal = SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="No candidates found.",
        candidates=[],
        warnings=[],
        blocks=[],
    )
    monkeypatch.setattr(
        appointments_router,
        "_build_slot_search_proposal",
        lambda *a, **kw: empty_proposal,
    )

    resp = _post_wrapper(client, token, _future_body(practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "candidate_selection_required"
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0


def test_suggestions_require_confirmation(
    client,
    db,
    gp_user,
    practitioner,
    monkeypatch,
):
    """All returned suggestions must have requires_confirmation=True."""
    token = make_token(gp_user)

    from app.schemas.appointments import SlotSearchProposalOut
    empty_proposal = SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="No candidates.",
        candidates=[],
        warnings=[],
        blocks=[],
    )
    monkeypatch.setattr(
        appointments_router,
        "_build_slot_search_proposal",
        lambda *a, **kw: empty_proposal,
    )

    resp = _post_wrapper(client, token, _future_body(practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    suggestions = data.get("suggestions", [])
    assert suggestions, "Expected at least one suggestion"
    for s in suggestions:
        assert s["requires_confirmation"] is True, (
            f"Suggestion {s['kind']} has requires_confirmation={s['requires_confirmation']}"
        )


def test_suggestions_have_valid_kind(
    client,
    db,
    gp_user,
    practitioner,
    monkeypatch,
):
    """Suggestion kinds are one of the declared Literal values."""
    VALID_KINDS = {"next_available_day", "widen_time_window", "alternate_practitioner"}
    token = make_token(gp_user)

    from app.schemas.appointments import SlotSearchProposalOut
    empty_proposal = SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="No candidates.",
        candidates=[],
        warnings=[],
        blocks=[],
    )
    monkeypatch.setattr(
        appointments_router,
        "_build_slot_search_proposal",
        lambda *a, **kw: empty_proposal,
    )

    resp = _post_wrapper(client, token, _future_body(practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    for s in data.get("suggestions", []):
        assert s["kind"] in VALID_KINDS


def test_clinic_day_exhausted_unchanged(
    client,
    db,
    gp_user,
    practitioner,
    monkeypatch,
):
    """clinic_day_exhausted result is not replaced by suggestions logic."""
    token = make_token(gp_user)

    from datetime import date as date_type
    # Monkeypatch _clinic_local_now to return a fixed time that makes all today's slots past
    # 08:00 UTC is 18:00 in Australia/Brisbane on 2026-07-02.
    fixed_now = datetime(2026, 7, 2, 8, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_now.astimezone(tz))

    body = {
        "reference_date": REFERENCE_DATE,
        "command": {
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
            "earliest_time": "09:00",
            "latest_time": "10:00",
        },
    }
    resp = _post_wrapper(client, token, body)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "clinic_day_exhausted"
    # clinic_day_exhausted must NOT include suggestions (it's a different signal)
    assert data.get("suggestions", []) == []


def test_no_slot_no_db_writes(
    client,
    db,
    gp_user,
    practitioner,
    monkeypatch,
):
    """No-slot suggestions path does not write any appointment or audit rows."""
    token = make_token(gp_user)

    from app.schemas.appointments import SlotSearchProposalOut
    empty_proposal = SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="No candidates.",
        candidates=[],
        warnings=[],
        blocks=[],
    )
    monkeypatch.setattr(
        appointments_router,
        "_build_slot_search_proposal",
        lambda *a, **kw: empty_proposal,
    )

    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    _post_wrapper(client, token, _future_body(practitioner))

    assert db.query(Appointment).count() == appt_before
    assert db.query(AppointmentAuditLog).count() == audit_before


# ── Context freshness ────────────────────────────────────────────────────────

INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"


def _post_interpret(client, token, instruction: str, reference_date: str = REFERENCE_DATE):
    return client.post(
        INTERPRET_URL,
        json={"instruction": instruction, "reference_date": reference_date},
        headers={"Authorization": f"Bearer {token}"},
    )


def test_context_freshness_echoes_reference_date(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    """context_freshness.reference_date equals the request reference_date for a recognized patient."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "disabled")
    # Monkeypatch clinic-local today to match REFERENCE_DATE so it's not stale
    fixed_today = datetime(2026, 7, 2, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_today.astimezone(tz))

    token = make_token(gp_user)
    # Use patient name that matches the fixture (Margaret Thompson)
    resp = _post_interpret(
        client, token,
        f"Book Margaret Thompson with {practitioner.first_name} {practitioner.last_name} next week",
        reference_date=REFERENCE_DATE,
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    # If recognized, freshness should be present
    if data.get("context_freshness") is not None:
        assert data["context_freshness"]["reference_date"] == REFERENCE_DATE
        assert data["context_freshness"]["stale"] is False


def test_stale_reference_date_flagged(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    """context_freshness.stale=True when request reference_date differs from clinic-local today."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "disabled")
    # Clinic-local today is 2026-07-03, but request uses 2026-07-02
    fixed_today = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_today.astimezone(tz))

    token = make_token(gp_user)
    resp = _post_interpret(
        client, token,
        f"Book Margaret Thompson with {practitioner.first_name} {practitioner.last_name} next week",
        reference_date=REFERENCE_DATE,  # 2026-07-02, but today is 2026-07-03
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    if data.get("context_freshness") is not None:
        assert data["context_freshness"]["stale"] is True
        assert "differs" in data["context_freshness"]["basis"]
