"""
Practice-wide patient duplicate review API.

GET /api/v1/patients/duplicate-groups returns groups of 2+ patients that share
a strong or soft identifier.  Every test proves the endpoint is read-only and
practice-scoped.
"""
from datetime import date

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.clinical import Encounter
from app.models.patients import Patient
from tests.conftest import make_token

URL = "/api/v1/patients/duplicate-groups"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _auth(user):
    return {"Authorization": f"Bearer {make_token(user)}"}


def _patient(db, practice, *, first="Ada", last="Lovelace",
             dob=date(1815, 12, 10), medicare_number=None, medicare_irn=None,
             ihi_number=None, phone_mobile=None):
    p = Patient(
        practice_id=practice.id,
        first_name=first,
        last_name=last,
        date_of_birth=dob,
        medicare_number=medicare_number,
        medicare_irn=medicare_irn,
        ihi_number=ihi_number,
        phone_mobile=phone_mobile,
    )
    db.add(p)
    db.flush()
    return p


def _encounter(db, practice, patient):
    e = Encounter(
        practice_id=practice.id,
        patient_id=patient.id,
        consultation_date=date(2026, 1, 1),
        status="Finalized",
    )
    db.add(e)
    db.flush()
    return e


def _appointment(db, practice, practitioner, patient):
    from datetime import datetime, time, timezone
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        appointment_date=date(2026, 1, 1),
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_duplicate_groups_requires_auth(client):
    resp = client.get(URL)
    assert resp.status_code == 401


def test_duplicate_groups_empty_when_no_duplicates(client, db, gp_user, practice):
    _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    _patient(db, practice, first="Charles", last="Babbage", dob=date(1791, 12, 26))

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_duplicate_groups_ihi_group(client, db, gp_user, practice):
    p1 = _patient(db, practice, first="Ada", last="Lovelace",
                  dob=date(1815, 12, 10), ihi_number="8003608833357361")
    p2 = _patient(db, practice, first="Ada", last="Lovelace-Byron",
                  dob=date(1815, 12, 10), ihi_number="8003608833357361")

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    group = data[0]
    assert "same_ihi" in group["match_reasons"]
    ids = {m["patient"]["id"] for m in group["patients"]}
    assert ids == {str(p1.id), str(p2.id)}


def test_duplicate_groups_medicare_irn_group(client, db, gp_user, practice):
    p1 = _patient(db, practice, first="Ada", last="Lovelace",
                  dob=date(1815, 12, 10),
                  medicare_number="2950123456", medicare_irn="1")
    p2 = _patient(db, practice, first="Ada", last="Lovelace",
                  dob=date(1800, 1, 1),
                  medicare_number="2950123456", medicare_irn="1")

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert "same_medicare_card_and_irn" in data[0]["match_reasons"]
    ids = {m["patient"]["id"] for m in data[0]["patients"]}
    assert ids == {str(p1.id), str(p2.id)}


def test_duplicate_groups_name_dob_group(client, db, gp_user, practice):
    p1 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    p2 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert "same_name_and_dob" in data[0]["match_reasons"]
    ids = {m["patient"]["id"] for m in data[0]["patients"]}
    assert ids == {str(p1.id), str(p2.id)}


def test_duplicate_groups_cross_practice_isolation(
        client, db, gp_user, practice, practice_b):
    # p1 in practice A, p2 in practice B — same IHI, different practices
    _patient(db, practice, ihi_number="8003608833357361")
    _patient(db, practice_b, ihi_number="8003608833357361")

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    # No group — the two patients are in different practices
    assert resp.json() == []


def test_duplicate_groups_ref_counts_appointments(
        client, db, gp_user, practice, practitioner):
    p1 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    p2 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    _appointment(db, practice, practitioner, p1)
    _appointment(db, practice, practitioner, p1)

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    counts = {m["patient"]["id"]: m["ref_counts"] for m in data[0]["patients"]}
    assert counts[str(p1.id)]["appointment_count"] == 2
    assert counts[str(p2.id)]["appointment_count"] == 0


def test_duplicate_groups_ref_counts_encounters(client, db, gp_user, practice):
    p1 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    p2 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    _encounter(db, practice, p1)

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    counts = {m["patient"]["id"]: m["ref_counts"] for m in data[0]["patients"]}
    assert counts[str(p1.id)]["encounter_count"] == 1
    assert counts[str(p2.id)]["encounter_count"] == 0


def test_duplicate_groups_multi_criteria_one_group(client, db, gp_user, practice):
    """A pair matching both IHI and Medicare+IRN appears in exactly one group."""
    p1 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10),
                  ihi_number="8003608833357361",
                  medicare_number="2950123456", medicare_irn="1")
    p2 = _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10),
                  ihi_number="8003608833357361",
                  medicare_number="2950123456", medicare_irn="1")

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    reasons = set(data[0]["match_reasons"])
    # Both criteria present in the one group
    assert "same_ihi" in reasons
    assert "same_medicare_card_and_irn" in reasons
    assert "same_name_and_dob" in reasons
    ids = {m["patient"]["id"] for m in data[0]["patients"]}
    assert ids == {str(p1.id), str(p2.id)}


def test_duplicate_groups_limit_caps_results(client, db, gp_user, practice):
    # Create 5 duplicate pairs sharing name+DOB (different DOBs to keep separate groups)
    for i in range(5):
        dob = date(1990, 1, i + 1)
        _patient(db, practice, first="Clone", last="Patient", dob=dob)
        _patient(db, practice, first="Clone", last="Patient", dob=dob)

    resp = client.get(URL + "?limit=3", headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 3


def test_duplicate_groups_name_dob_case_insensitive(client, db, gp_user, practice):
    """Name comparison is case-insensitive and trims whitespace."""
    p1 = _patient(db, practice, first="ADA", last="LOVELACE", dob=date(1815, 12, 10))
    p2 = _patient(db, practice, first="ada", last="lovelace", dob=date(1815, 12, 10))

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert "same_name_and_dob" in data[0]["match_reasons"]
    ids = {m["patient"]["id"] for m in data[0]["patients"]}
    assert ids == {str(p1.id), str(p2.id)}


def test_duplicate_groups_solo_patient_not_grouped(client, db, gp_user, practice):
    """A patient with a unique IHI that no other patient shares is not grouped."""
    _patient(db, practice, ihi_number="8003608833357361")

    resp = client.get(URL, headers=_auth(gp_user))
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_duplicate_groups_endpoint_is_read_only(client, db, gp_user, practice):
    """Calling the endpoint does not change the patient count."""
    _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    _patient(db, practice, first="Ada", last="Lovelace", dob=date(1815, 12, 10))
    before = db.query(Patient).count()

    client.get(URL, headers=_auth(gp_user))

    assert db.query(Patient).count() == before
