from datetime import date, datetime, time, timedelta, timezone

import pytest

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentAuditAction,
    AppointmentStatus,
    BookingChannel,
)
from app.schemas.appointments import STATUS_REASON_CODES
from tests.conftest import make_token


TODAY = date.today() + timedelta(days=14)
PAST_DATE = date(2026, 4, 15)
APPT_URL = "/api/v1/appointments"
DELETE_CONFIRM_URL = f"{APPT_URL}/proposals/delete-confirm"
STATUS_CONFIRM_URL = f"{APPT_URL}/proposals/status-confirm"


def _make_appt(
    db,
    practice,
    practitioner,
    patient,
    status=AppointmentStatus.Booked,
    appt_date=None,
    start_h=9,
):
    appt_date = appt_date if appt_date is not None else TODAY
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_reason_code_taxonomy_contains_expected_codes():
    assert {
        "PATIENT_CANCELLED",
        "DID_NOT_ATTEND",
        "LEFT_WITHOUT_SEEN",
        "LEGACY_UNCLASSIFIED",
    }.issubset(STATUS_REASON_CODES)


def test_raw_patch_status_persists_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled", "status_reason_code": "PATIENT_CANCELLED"},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_reason_code"] == "PATIENT_CANCELLED"
    db.refresh(appt)
    assert appt.status_reason_code == "PATIENT_CANCELLED"

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].action == AppointmentAuditAction.status_change
    assert entries[0].status_reason_code == "PATIENT_CANCELLED"


def test_raw_patch_status_rejects_invalid_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled", "status_reason_code": "patient_cancelled"},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_raw_patch_status_omitted_reason_code_stays_null(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled"},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_reason_code"] is None
    db.refresh(appt)
    assert appt.status_reason_code is None


def test_status_proposal_confirm_persists_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    proposal_resp = client.post(
        f"{APPT_URL}/proposals/status/{appt.id}",
        json={"status": "NoShow", "status_reason_code": "DID_NOT_ATTEND"},
        headers=_auth(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    assert proposal_resp.json()["command"]["status_reason_code"] == "DID_NOT_ATTEND"
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(STATUS_CONFIRM_URL, json=payload, headers=_auth(token))
    assert confirm_resp.status_code == 200, confirm_resp.text
    assert confirm_resp.json()["appointment"]["status_reason_code"] == "DID_NOT_ATTEND"

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].status_after == AppointmentStatus.NoShow
    assert entries[0].status_reason_code == "DID_NOT_ATTEND"


def test_delete_proposal_confirm_persists_status_reason_code_and_text_reason(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)

    proposal_resp = client.post(
        f"{APPT_URL}/proposals/delete/{appt.id}",
        json={
            "cancellation_reason": "Duplicate booking",
            "status_reason_code": "DUPLICATE_BOOKING",
        },
        headers=_auth(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    assert proposal_resp.json()["command"]["status_reason_code"] == "DUPLICATE_BOOKING"
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
    assert confirm_resp.status_code == 200, confirm_resp.text
    appointment = confirm_resp.json()["appointment"]
    assert appointment["status_reason_code"] == "DUPLICATE_BOOKING"
    assert appointment["cancellation_reason"] == "Duplicate booking"

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].action == AppointmentAuditAction.delete
    assert entries[0].status_reason_code == "DUPLICATE_BOOKING"
    assert entries[0].cancellation_reason == "Duplicate booking"


@pytest.mark.parametrize("path_builder,payload", [
    (
        lambda appt_id: f"{APPT_URL}/proposals/status/{appt_id}",
        {"status": "Cancelled", "status_reason_code": "COVID_SYMPTOMS"},
    ),
    (
        lambda appt_id: f"{APPT_URL}/proposals/delete/{appt_id}",
        {
            "cancellation_reason": "Patient called",
            "status_reason_code": "COVID_SYMPTOMS",
        },
    ),
])
def test_proposals_reject_invalid_status_reason_code(
    path_builder, payload, client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.post(path_builder(appt.id), json=payload, headers=_auth(token))
    assert resp.status_code == 422


def test_past_date_status_and_delete_allow_null_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    status_appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE, start_h=9)
    delete_appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE, start_h=10)

    status_resp = client.patch(
        f"{APPT_URL}/{status_appt.id}/status",
        json={"status": "DNA"},
        headers=_auth(token),
    )
    assert status_resp.status_code == 200, status_resp.text
    assert status_resp.json()["status_reason_code"] is None

    delete_resp = client.request(
        "DELETE",
        f"{APPT_URL}/{delete_appt.id}",
        json={"cancellation_reason": "Historical correction"},
        headers=_auth(token),
    )
    assert delete_resp.status_code == 204
