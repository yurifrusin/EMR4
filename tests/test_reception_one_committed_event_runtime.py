from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary_events import DiaryCommittedEvent
from app.schemas.diary_events import AppointmentRescheduledEventPayload
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
EVENT_URL = "/api/v1/diary/events/committed"
REFERENCE_DATE = date(2026, 7, 27)


@pytest.fixture(autouse=True)
def _event_runtime(monkeypatch):
    monkeypatch.setattr(settings, "reception_one_committed_event_runtime_enabled", True)
    monkeypatch.setattr(
        appointments_router,
        "_clinic_local_now",
        lambda tz: datetime(2026, 7, 21, 8, 0, tzinfo=tz),
    )


def _auth(user, key=None):
    headers = {"Authorization": f"Bearer {make_token(user)}"}
    if key is not None:
        headers["Idempotency-Key"] = key
    return headers


def _appointment(db, practice, practitioner, patient, *, hour=9):
    appointment = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(
            REFERENCE_DATE,
            time(hour),
            tzinfo=timezone(timedelta(hours=10)),
        ).astimezone(timezone.utc),
        appointment_date=REFERENCE_DATE,
        start_time_local=time(hour),
        duration_minutes=30,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
        reason="Authored synthetic review",
    )
    db.add(appointment)
    db.flush()
    return appointment


def _proposal(client, user, appointment_id, *, hour=10, reason=None):
    body = {}
    if hour is not None:
        body.update(
            appointment_date=REFERENCE_DATE.isoformat(),
            start_time_local=f"{hour:02d}:00:00",
        )
    if reason is not None:
        body["reason"] = reason
    response = client.post(
        f"/api/v1/appointments/proposals/update/{appointment_id}",
        json=body,
        headers=_auth(user, f"proposal-{appointment_id}-{hour}-{reason}"),
    )
    assert response.status_code == 200, response.text
    payload = response.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _confirm(client, user, payload, key):
    return client.post(CONFIRM_URL, json=payload, headers=_auth(user, key))


def test_event_payload_is_exact_and_rejects_phi_or_free_text():
    base = {
        "appointment_id": "e3f72270-63c2-4c8a-a524-bb8668970242",
        "practitioner_id": "cc8793c4-6af2-41ea-a143-e0545441d639",
        "location_id": None,
        "start_time": "2026-07-27T10:00:00+00:00",
        "end_time": "2026-07-27T10:30:00+00:00",
        "reason_codes": ["appointment_time_changed"],
    }
    validated = AppointmentRescheduledEventPayload.model_validate(base)
    assert set(validated.model_dump(mode="json")) == set(base)

    for prohibited in ("patient_id", "patient_name", "reason", "notes", "instruction"):
        with pytest.raises(ValidationError):
            AppointmentRescheduledEventPayload.model_validate(
                {**base, prohibited: "must-not-persist"}
            )


def test_disabled_runtime_writes_no_event_and_feed_is_inert(
    monkeypatch, client, db, gp_user, practice, practitioner, patient
):
    monkeypatch.setattr(settings, "reception_one_committed_event_runtime_enabled", False)
    appointment = _appointment(db, practice, practitioner, patient)
    payload = _proposal(client, gp_user, appointment.id)

    response = _confirm(client, gp_user, payload, "disabled-event-runtime")

    assert response.status_code == 200, response.text
    assert db.query(DiaryCommittedEvent).count() == 0
    feed = client.get(EVENT_URL, headers=_auth(gp_user))
    assert feed.status_code == 200
    assert feed.json() == {
        "schema_version": "diary.committed_event_feed.v1",
        "enabled": False,
        "baseline_established": False,
        "cursor": None,
        "events": [],
    }


def test_confirmed_time_change_atomically_correlates_command_audit_and_event(
    client, db, gp_user, practice, practitioner, patient
):
    appointment = _appointment(db, practice, practitioner, patient)
    payload = _proposal(client, gp_user, appointment.id, hour=10)

    response = _confirm(client, gp_user, payload, "event-correlation")

    assert response.status_code == 200, response.text
    event = db.query(DiaryCommittedEvent).one()
    audit = db.query(AppointmentAuditLog).one()
    command = db.query(AppointmentCommandIdempotency).one()
    assert event.practice_id == appointment.practice_id
    assert event.appointment_id == appointment.id
    assert event.aggregate_revision == 1
    assert event.command_id == command.id == audit.command_id
    assert event.audit_log_id == audit.id == command.audit_log_id
    assert event.correlation_id == command.id
    assert event.actor_user_id == gp_user.id
    assert set(event.payload) == {
        "appointment_id",
        "practitioner_id",
        "location_id",
        "start_time",
        "end_time",
        "reason_codes",
    }
    assert not ({"patient_id", "patient_name", "reason", "notes"} & set(event.payload))


def test_idempotent_replay_creates_no_second_event(
    client, db, gp_user, practice, practitioner, patient
):
    appointment = _appointment(db, practice, practitioner, patient)
    payload = _proposal(client, gp_user, appointment.id, hour=10)
    first = _confirm(client, gp_user, payload, "event-replay")
    counts = (
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
        db.query(DiaryCommittedEvent).count(),
    )

    second = _confirm(client, gp_user, payload, "event-replay")

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert counts == (1, 1, 1)
    assert counts == (
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
        db.query(DiaryCommittedEvent).count(),
    )


def test_event_insert_failure_rolls_back_update_audit_command_and_event(
    monkeypatch, client, db, gp_user, practice, practitioner, patient
):
    appointment = _appointment(db, practice, practitioner, patient)
    original_window = appointment.start_time_local
    db.commit()
    payload = _proposal(client, gp_user, appointment.id, hour=10)
    original = appointments_router.record_appointment_rescheduled_event

    def insert_then_fail(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("injected committed-event failure")

    monkeypatch.setattr(
        appointments_router,
        "record_appointment_rescheduled_event",
        insert_then_fail,
    )
    response = _confirm(client, gp_user, payload, "event-rollback")
    assert response.status_code == 500
    db.rollback()

    db.refresh(appointment)
    assert appointment.start_time_local == original_window
    assert db.query(AppointmentAuditLog).count() == 0
    assert db.query(AppointmentCommandIdempotency).count() == 0
    assert db.query(DiaryCommittedEvent).count() == 0


def test_confirmed_non_time_update_does_not_emit_reschedule_event(
    client, db, gp_user, practice, practitioner, patient
):
    appointment = _appointment(db, practice, practitioner, patient)
    payload = _proposal(
        client,
        gp_user,
        appointment.id,
        hour=None,
        reason="Changed authored-synthetic reason",
    )

    response = _confirm(client, gp_user, payload, "non-time-update")

    assert response.status_code == 200, response.text
    assert db.query(AppointmentAuditLog).count() == 1
    assert db.query(DiaryCommittedEvent).count() == 0


def test_empty_history_baseline_delivers_first_later_event_without_history(
    client, db, gp_user, practice, practitioner, patient
):
    appointment = _appointment(db, practice, practitioner, patient)
    baseline = client.get(EVENT_URL, headers=_auth(gp_user))
    assert baseline.status_code == 200
    baseline_body = baseline.json()
    assert baseline_body["baseline_established"] is True
    assert baseline_body["cursor"]
    assert baseline_body["events"] == []

    payload = _proposal(client, gp_user, appointment.id, hour=10)
    assert _confirm(client, gp_user, payload, "first-after-empty-baseline").status_code == 200
    delivered = client.get(
        EVENT_URL,
        params={"cursor": baseline_body["cursor"]},
        headers=_auth(gp_user),
    )

    assert delivered.status_code == 200, delivered.text
    body = delivered.json()
    assert body["baseline_established"] is False
    assert len(body["events"]) == 1
    event = body["events"][0]
    assert event["event_type"] == "diary.appointment_rescheduled"
    assert event["aggregate_id"] == str(appointment.id)
    assert event["payload"]["appointment_id"] == str(appointment.id)
    assert event["received_at"]
    assert body["cursor"] != baseline_body["cursor"]


def test_foreign_practice_or_tampered_cursor_rebaselines_without_history(
    client, db, gp_user, gp_user_b
):
    baseline = client.get(EVENT_URL, headers=_auth(gp_user)).json()["cursor"]

    foreign = client.get(
        EVENT_URL,
        params={"cursor": baseline},
        headers=_auth(gp_user_b),
    )
    tampered = client.get(
        EVENT_URL,
        params={"cursor": f"{baseline}x"},
        headers=_auth(gp_user),
    )

    for response in (foreign, tampered):
        assert response.status_code == 200
        assert response.json()["baseline_established"] is True
        assert response.json()["events"] == []
        assert response.json()["cursor"] != baseline


def test_migration_enforces_forced_rls_append_only_and_payload_allowlist():
    migration = (
        ROOT
        / "alembic"
        / "versions"
        / "n3o4p5q6r7s8_add_reception_one_committed_events.py"
    ).read_text(encoding="utf-8")
    for fragment in (
        'ALTER TABLE "diary_committed_events" ENABLE ROW LEVEL SECURITY',
        'ALTER TABLE "diary_committed_events" FORCE ROW LEVEL SECURITY',
        "FOR SELECT",
        "USING (",
        "FOR INSERT",
        "WITH CHECK",
        "BEFORE UPDATE OR DELETE ON diary_committed_events",
        "payload - ARRAY",
        "appointment_time_changed",
        "correlation_id = command_id",
    ):
        assert fragment in migration
