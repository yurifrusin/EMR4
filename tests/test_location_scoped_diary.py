"""
Tests for location-scoped diary contract (Sprint 16 AU).

Covers:
  - GET /diary/locations — auth + cross-practice isolation + active-only
  - GET /diary/template — location-specific, fallback to practice-wide, cross-practice 404
  - GET /diary/roster   — location filter
  - GET /diary/waiting-areas — location filter
  - GET /appointments   — location filter + cross-practice 404
  - GET /appointments/waiting-room — location filter
  - GET /appointments/{id}/checkin-defaults — multi-location disambiguation
"""
from datetime import date, time

import pytest

from app.models.appointments import (
    Appointment, AppointmentStatus, AppointmentType, BookingChannel,
    PractitionerSchedule,
)
from app.models.diary import DiaryBreak, DiaryColumn, DiaryRoster, DiaryTemplate, Room, WaitingArea
from app.models.tenancy import PracticeLocation
from tests.conftest import make_token

TUESDAY = date(2026, 6, 23)  # real Tuesday — fits Mon-Fri schedule


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_location(db, practice, *, name="Clinic A", active=True):
    loc = PracticeLocation(
        practice_id=practice.id,
        name=name,
        is_active=active,
    )
    db.add(loc)
    db.flush()
    return loc


def _make_room(db, practice, location, *, name="Room A", order=0):
    room = Room(
        practice_id=practice.id,
        location_id=location.id,
        name=name,
        display_order=order,
        is_active=True,
    )
    db.add(room)
    db.flush()
    return room


def _make_area(db, practice, location, *, name="Waiting A", order=0):
    area = WaitingArea(
        practice_id=practice.id,
        location_id=location.id,
        name=name,
        display_order=order,
        is_active=True,
    )
    db.add(area)
    db.flush()
    return area


def _make_template(db, practice, location=None):
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        location_id=location.id if location else None,
        practice_name=practice.name,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    return tmpl


def _make_appt(db, practice, practitioner, patient, appt_type, user, *,
               roster_date=TUESDAY, hour=9, minute=0, location=None):
    local_start = time(hour, minute)
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Australia/Sydney")
    start_utc = datetime.combine(roster_date, local_start).replace(tzinfo=tz).astimezone(timezone.utc)
    appt = Appointment(
        practice_id=practice.id,
        practitioner_id=practitioner.id,
        patient_id=patient.id,
        appointment_type_id=appt_type.id,
        booked_by=user.id,
        start_time=start_utc,
        appointment_date=roster_date,
        start_time_local=local_start,
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
        location_id=location.id if location else None,
    )
    db.add(appt)
    db.flush()
    return appt


def _make_roster(db, practice, room, practitioner, *, roster_date=TUESDAY):
    entry = DiaryRoster(
        practice_id=practice.id,
        room_id=room.id,
        roster_date=roster_date,
        practitioner_id=practitioner.id,
        practitioner_ahpra=practitioner.ahpra_number,
    )
    db.add(entry)
    db.flush()
    return entry


# ─── GET /diary/locations ──────────────────────────────────────────────────────

def test_locations_requires_auth(client):
    r = client.get("/api/v1/diary/locations")
    assert r.status_code == 401


def test_locations_cross_practice_isolation(client, db, practice, practice_b, gp_user, gp_user_b):
    loc_a = _make_location(db, practice, name="Clinic A")
    _make_location(db, practice_b, name="Clinic B")
    db.flush()

    token = make_token(gp_user)
    r = client.get("/api/v1/diary/locations", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    ids = [item["id"] for item in r.json()]
    assert str(loc_a.id) in ids
    assert all(item["id"] != str(practice_b.id) for item in r.json())
    assert len(ids) == 1


def test_locations_active_only(client, db, practice, gp_user):
    active = _make_location(db, practice, name="Active Clinic", active=True)
    _make_location(db, practice, name="Inactive Clinic", active=False)
    db.flush()

    token = make_token(gp_user)
    r = client.get("/api/v1/diary/locations", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    ids = [item["id"] for item in r.json()]
    assert str(active.id) in ids
    assert len(ids) == 1


# ─── GET /diary/template ───────────────────────────────────────────────────────

def test_template_location_specific(client, db, practice, gp_user):
    loc = _make_location(db, practice)
    practice_wide = _make_template(db, practice, location=None)
    loc_specific = _make_template(db, practice, location=loc)
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/diary/template?location_id={loc.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["location_id"] == str(loc_specific.location_id)


def test_template_falls_back_to_practice_wide(client, db, practice, gp_user):
    loc = _make_location(db, practice)
    _make_template(db, practice, location=None)
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/diary/template?location_id={loc.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    # Fallback: location_id in response is None (practice-wide template)
    assert r.json()["location_id"] is None


def test_template_cross_practice_location_returns_404(client, db, practice, practice_b, gp_user):
    loc_b = _make_location(db, practice_b, name="Foreign Clinic")
    _make_template(db, practice, location=None)
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/diary/template?location_id={loc_b.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


# ─── GET /diary/roster ─────────────────────────────────────────────────────────

def test_roster_filtered_by_location(client, db, practice, practitioner, gp_user):
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")
    room_a = _make_room(db, practice, loc_a, name="Room A", order=0)
    room_b = _make_room(db, practice, loc_b, name="Room B", order=1)
    _make_roster(db, practice, room_a, practitioner)
    _make_roster(db, practice, room_b, practitioner)
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/diary/roster?date={TUESDAY}&location_id={loc_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    room_names = [e["room_name"] for e in body["entries"]]
    assert "Room A" in room_names
    assert "Room B" not in room_names


def test_room_display_order_is_location_scoped(db, practice):
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")
    _make_room(db, practice, loc_a, name="Room 1A", order=0)
    _make_room(db, practice, loc_b, name="Room 1B", order=0)

    db.flush()


# ─── GET /diary/waiting-areas ─────────────────────────────────────────────────

def test_waiting_areas_filtered_by_location(client, db, practice, gp_user):
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")
    area_a = _make_area(db, practice, loc_a, name="Waiting A")
    _make_area(db, practice, loc_b, name="Waiting B")
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/diary/waiting-areas?location_id={loc_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    names = [item["name"] for item in r.json()]
    assert "Waiting A" in names
    assert "Waiting B" not in names


# ─── GET /appointments ─────────────────────────────────────────────────────────

def test_appointments_location_filter(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")
    _make_appt(db, practice, practitioner, patient, appt_type, gp_user, location=loc_a)
    _make_appt(db, practice, practitioner, patient, appt_type, gp_user,
               hour=9, minute=30, location=loc_b)
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments?location_id={loc_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    locs = [a["location_id"] for a in r.json()]
    assert all(l == str(loc_a.id) for l in locs)
    assert len(locs) == 1


def test_appointments_single_location_includes_legacy_unscoped(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    loc = _make_location(db, practice, name="Main Clinic")
    legacy = _make_appt(
        db, practice, practitioner, patient, appt_type, gp_user,
        hour=11, minute=35, location=None,
    )
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments?location_id={loc.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    ids = [a["id"] for a in r.json()]
    assert str(legacy.id) in ids


def test_appointments_multi_location_hides_legacy_unscoped(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    loc_a = _make_location(db, practice, name="Clinic A")
    _make_location(db, practice, name="Clinic B")
    legacy = _make_appt(
        db, practice, practitioner, patient, appt_type, gp_user,
        hour=11, minute=35, location=None,
    )
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments?location_id={loc_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    ids = [a["id"] for a in r.json()]
    assert str(legacy.id) not in ids


def test_appointments_cross_practice_location(
    client, db, practice, practice_b, practitioner, patient, appt_type, gp_user, schedule
):
    loc_b = _make_location(db, practice_b, name="Foreign Clinic")
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments?location_id={loc_b.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


# ─── GET /appointments/waiting-room ───────────────────────────────────────────

def test_create_single_location_conflicts_with_legacy_unscoped(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    loc = _make_location(db, practice, name="Main Clinic")
    _make_appt(
        db, practice, practitioner, patient, appt_type, gp_user,
        hour=11, minute=35, location=None,
    )
    db.flush()

    token = make_token(gp_user)
    r = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_type_id": str(appt_type.id),
            "appointment_date": TUESDAY.isoformat(),
            "start_time_local": "11:45:00",
            "duration_minutes": 30,
            "location_id": str(loc.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409


def test_create_allows_same_practitioner_at_different_locations(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")
    _make_appt(
        db, practice, practitioner, patient, appt_type, gp_user,
        hour=11, minute=35, location=loc_b,
    )
    db.flush()

    token = make_token(gp_user)
    r = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_type_id": str(appt_type.id),
            "appointment_date": TUESDAY.isoformat(),
            "start_time_local": "11:45:00",
            "duration_minutes": 30,
            "location_id": str(loc_a.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201


def test_waiting_room_location_filter(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")
    from datetime import date as _date
    today = _date.today()
    # Build appointments for today so the waiting-room endpoint picks them up
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Australia/Sydney")

    def _appt_today(hour, minute, loc):
        local_start = time(hour, minute)
        start_utc = datetime.combine(today, local_start).replace(tzinfo=tz).astimezone(timezone.utc)
        a = Appointment(
            practice_id=practice.id,
            practitioner_id=practitioner.id,
            patient_id=patient.id,
            appointment_type_id=appt_type.id,
            booked_by=gp_user.id,
            start_time=start_utc,
            appointment_date=today,
            start_time_local=local_start,
            duration_minutes=15,
            status=AppointmentStatus.Arrived,
            booked_via=BookingChannel.Receptionist,
            location_id=loc.id,
        )
        db.add(a)
        db.flush()
        return a

    _appt_today(9, 0, loc_a)
    _appt_today(9, 15, loc_b)
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments/waiting-room?location_id={loc_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    locs = [a["location_id"] for a in r.json()]
    assert all(l == str(loc_a.id) for l in locs)
    assert len(locs) == 1


# ─── GET /appointments/{id}/checkin-defaults ──────────────────────────────────

def test_checkin_defaults_disambiguation(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    """Practitioner rostered at two locations on the same day; appointment's
    location_id should select the correct room (and thus waiting area)."""
    loc_a = _make_location(db, practice, name="Clinic A")
    loc_b = _make_location(db, practice, name="Clinic B")

    area_a = _make_area(db, practice, loc_a, name="Waiting A")
    area_b = _make_area(db, practice, loc_b, name="Waiting B")

    room_a = _make_room(db, practice, loc_a, name="Room A", order=0)
    room_a.default_waiting_area_id = area_a.id
    room_b = _make_room(db, practice, loc_b, name="Room B", order=1)
    room_b.default_waiting_area_id = area_b.id
    db.flush()

    _make_roster(db, practice, room_a, practitioner)
    _make_roster(db, practice, room_b, practitioner)
    db.flush()

    # Appointment at location A on TUESDAY
    appt = _make_appt(
        db, practice, practitioner, patient, appt_type, gp_user,
        roster_date=TUESDAY, location=loc_a,
    )
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments/{appt.id}/checkin-defaults",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["suggested_waiting_area_id"] == str(area_a.id)
    assert body["room_name"] == "Room A"


def test_checkin_defaults_no_location_unchanged(
    client, db, practice, practitioner, patient, appt_type, gp_user, schedule
):
    """When appt.location_id is NULL, the roster query falls through to .first()
    and the existing single-location behaviour is unchanged."""
    area = _make_area(db, practice, _make_location(db, practice), name="Main Waiting")
    room = _make_room(db, practice, _make_location(db, practice, name="Clinic A2"), name="Room 1", order=0)
    room.default_waiting_area_id = area.id
    db.flush()
    _make_roster(db, practice, room, practitioner)
    db.flush()

    # Appointment with no location_id
    appt = _make_appt(
        db, practice, practitioner, patient, appt_type, gp_user,
        roster_date=TUESDAY, location=None,
    )
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments/{appt.id}/checkin-defaults",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    # Room has a default — should be suggested
    assert body["suggested_waiting_area_id"] == str(area.id)
