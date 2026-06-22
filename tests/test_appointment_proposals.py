"""
Non-mutating appointment proposal contract.

These endpoints let Bernie or another agent prepare a typed command for staff
review without writing to the diary.
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate
from tests.conftest import make_token

PROPOSAL_URL = "/api/v1/appointments/proposals/create"
TODAY = date.today()
THURSDAY = date(2026, 6, 25)


def _base_body(patient, practitioner) -> dict:
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": THURSDAY.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }


def _post_proposal(client, token, body: dict):
    return client.post(
        PROPOSAL_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _make_appt(db, practice, practitioner, patient, start_h=9, start_m=0, duration=15):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TODAY, time(start_h, start_m), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(start_h, start_m),
        duration_minutes=duration,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


@pytest.fixture()
def diary_with_break(db, practice, practitioner):
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    col = DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=0,
        room_label="Room 1",
        assignment=f"Dr {practitioner.last_name}",
        practitioner_id=practitioner.id,
        practitioner_ahpra=practitioner.ahpra_number,
    )
    db.add(col)
    db.flush()
    db.add(DiaryBreak(
        column_id=col.id,
        display_order=0,
        label="MORNING TEA",
        from_time=time(10, 45),
        to_time=time(11, 0),
    ))
    db.flush()


def test_create_proposal_requires_auth(client, patient, practitioner):
    resp = client.post(PROPOSAL_URL, json=_base_body(patient, practitioner))
    assert resp.status_code == 401


def test_create_proposal_returns_typed_command_without_mutating(
        client, db, gp_user, patient, practitioner):
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = _post_proposal(client, token, _base_body(patient, practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "create_appointment"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["patient_identity"] == "linked"
    assert data["warnings"] == []
    assert data["blocks"] == []
    assert data["command"]["patient_id"] == str(patient.id)
    assert data["command"]["appointment_date"] == THURSDAY.isoformat()
    assert db.query(Appointment).count() == before


def test_create_proposal_reports_conflict_without_409(
        client, db, gp_user, practice, patient, practitioner):
    existing = _make_appt(db, practice, practitioner, patient, start_h=9, duration=30)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = _post_proposal(client, token, {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": TODAY.isoformat(),
        "start_time_local": "09:15:00",
        "duration_minutes": 15,
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["blocks"][0]["code"] == "appointment_conflict"
    assert data["conflict"]["appointment_id"] == str(existing.id)
    assert data["conflict"]["patient_name"] == "Margaret Thompson"
    assert db.query(Appointment).count() == before


def test_create_proposal_warns_for_break_overlap(
        client, gp_user, patient, practitioner, diary_with_break):
    token = make_token(gp_user)

    resp = _post_proposal(client, token, {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": THURSDAY.isoformat(),
        "start_time_local": "10:45:00",
        "duration_minutes": 15,
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "proposal"
    assert "MORNING TEA" in data["breaks_overlap"]
    assert data["warnings"][0]["code"] == "break_overlap"


def test_create_proposal_warns_for_break_overlap_when_column_matches_ahpra_only(
        client, db, gp_user, patient, practitioner):
    tmpl = DiaryTemplate(
        practice_id=gp_user.practice_id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    col = DiaryColumn(
        template_id=tmpl.id,
        practice_id=gp_user.practice_id,
        display_order=0,
        room_label="Room 1",
        assignment=f"Dr {practitioner.last_name}",
        practitioner_id=None,
        practitioner_ahpra=practitioner.ahpra_number,
    )
    db.add(col)
    db.flush()
    db.add(DiaryBreak(
        column_id=col.id,
        display_order=0,
        label="MORNING TEA",
        from_time=time(10, 45),
        to_time=time(11, 0),
    ))
    db.flush()

    token = make_token(gp_user)
    resp = _post_proposal(client, token, {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": THURSDAY.isoformat(),
        "start_time_local": "10:40:00",
        "duration_minutes": 30,
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert "MORNING TEA" in data["breaks_overlap"]
    assert any(w["code"] == "break_overlap" for w in data["warnings"])


def test_create_proposal_warns_for_provisional_patient(
        client, gp_user, practitioner):
    token = make_token(gp_user)

    resp = _post_proposal(client, token, {
        "patient_name_provisional": "Walk-in Patient",
        "practitioner_id": str(practitioner.id),
        "appointment_date": THURSDAY.isoformat(),
        "start_time_local": "11:30:00",
        "duration_minutes": 15,
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["patient_identity"] == "provisional"
    assert data["warnings"][0]["code"] == "provisional_patient"
    assert data["command"]["patient_name_provisional"] == "Walk-in Patient"
