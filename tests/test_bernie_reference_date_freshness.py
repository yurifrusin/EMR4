"""Focused Stage 1 coverage for pinned reference-date freshness."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

import app.routers.appointments as appointment_routes
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.services.auth_service import create_access_token


CLINIC_TODAY = date(2026, 7, 19)
INSTRUCTION = (
    "Make an appointment for Margaret Thompson with Dr Shera today "
    "after 2 pm but before 3:45."
)
REFERENCE_CASES = (
    pytest.param(date(2026, 7, 18), True, id="past"),
    pytest.param(CLINIC_TODAY, False, id="today"),
    pytest.param(date(2026, 7, 20), False, id="future"),
)


def _headers(user) -> dict[str, str]:
    token = create_access_token(
        {
            "sub": str(user.id),
            "practice_id": str(user.practice_id),
            "role": user.role.value,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def _context_frames(reference_date: date) -> list[dict[str, str]]:
    value = reference_date.isoformat()
    return [
        {
            "type": "visible_diary_page",
            "visible_date": value,
            "diary_date": value,
        }
    ]


def _freeze_clinic_today(monkeypatch) -> None:
    clinic_now = datetime(2026, 7, 19, 10, 0, tzinfo=ZoneInfo("Australia/Brisbane"))
    monkeypatch.setattr(appointment_routes, "_clinic_local_now", lambda _tz: clinic_now)
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")


def _interpret(client, user, reference_date: date) -> dict:
    response = client.post(
        "/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        headers=_headers(user),
        json={
            "instruction": INSTRUCTION,
            "reference_date": reference_date.isoformat(),
            "context_frames": _context_frames(reference_date),
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _assert_freshness(payload: dict, *, expected_stale: bool) -> None:
    assert payload["context_freshness"]["stale"] is expected_stale
    reason_codes = payload["outcome"]["reason_codes"]
    assert ("context_reference_date_stale" in reason_codes) is expected_stale


def _assert_no_product_writes(db) -> None:
    assert db.query(Appointment).count() == 0
    assert db.query(AppointmentAuditLog).count() == 0
    assert db.query(AppointmentCommandIdempotency).count() == 0


@pytest.mark.parametrize(("reference_date", "expected_stale"), REFERENCE_CASES)
def test_interpret_context_freshness_allows_today_and_future_but_stales_past(
    client,
    db,
    receptionist_user,
    patient,
    practitioner,
    appt_type,
    schedule,
    monkeypatch,
    reference_date,
    expected_stale,
):
    _freeze_clinic_today(monkeypatch)

    payload = _interpret(client, receptionist_user, reference_date)

    assert payload["result"] == "interpreted"
    _assert_freshness(payload, expected_stale=expected_stale)
    _assert_no_product_writes(db)


@pytest.mark.parametrize(("reference_date", "expected_stale"), REFERENCE_CASES)
def test_supervised_context_freshness_allows_today_and_future_but_stales_past(
    client,
    db,
    receptionist_user,
    patient,
    practitioner,
    appt_type,
    schedule,
    monkeypatch,
    reference_date,
    expected_stale,
):
    _freeze_clinic_today(monkeypatch)
    interpreted = _interpret(client, receptionist_user, reference_date)

    response = client.post(
        "/api/v1/appointments/proposals/bernie/supervised-booking",
        headers=_headers(receptionist_user),
        json={
            "command": interpreted["command_candidate"],
            "reference_date": reference_date.isoformat(),
            "context_frames": _context_frames(reference_date),
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    _assert_freshness(payload, expected_stale=expected_stale)
    _assert_no_product_writes(db)
