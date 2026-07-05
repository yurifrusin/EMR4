"""Sprint R4 adversarial probes: past-date guard surfaces in Bernie slot flow.

The same-day temporal guard (evaluate_same_day_window) only fires when the
resolved date equals clinic-local today. Past absolute dates and stale/backdated
reference_date values pass the normalizer and slot-search without any temporal
block — this file probes every Bernie entry point to document the gap.

Design:
- Pure unit tests (no DB) for the normalizer layer.
- Route-level tests (with DB fixtures, monkeypatched clinic time) for each
  endpoint in the Bernie slot-search pipeline.
- Regression tests verify same-day fully-past-window blocking and D8 collision
  warnings still work.
- xfail tests mark broader mutation surfaces (raw create, propose-create) that
  are outside the new-booking Bernie slot-search scope but still unguarded.

All route tests use the fake interpreter (no live Gemini).
No production code changes.
"""

from datetime import date, datetime, time, timedelta, timezone
import uuid

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.schemas.appointments import SlotSearchCommandIn
from app.services.bernie_slot_normalizer import normalize_slot_search_command
from tests.conftest import make_token


# ── Reference dates ──────────────────────────────────────────────────────────
# "Today" in the test clinic: Monday 2026-07-13, Australia/Sydney (UTC+10)
# Past dates: use 2026-07-06 (previous Monday, one week before "today")
# The "clinic now" is set to 2026-07-13 09:00.

CLINIC_TODAY = date(2026, 7, 13)       # Monday
CLINIC_NOW = datetime(2026, 7, 13, 9, 0, tzinfo=timezone.utc)

PAST_DATE_STR = "2026-07-06"            # Previous Monday
PAST_DATE_OBJ = date(2026, 7, 6)

STALE_REF_DATE = date(2026, 7, 6)       # Backdated reference_date

# Endpoint URLs
SLOT_SEARCH_URL = "/api/v1/appointments/proposals/slot-search"
NORMALIZED_URL = "/api/v1/appointments/proposals/slot-search/normalized"
INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
CREATE_URL = "/api/v1/appointments"
PROPOSE_CREATE_URL = "/api/v1/appointments/proposals/create"

PRAC_ID = uuid.uuid4()


# =============================================================================
# 1.  Pure normalizer tests (no DB)
# =============================================================================

def _cmd(**kwargs) -> SlotSearchCommandIn:
    return SlotSearchCommandIn(**kwargs)


def test_r4_normalizer_accepts_past_absolute_date():
    """The normalizer accepts a past ISO date with no temporal guard."""
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from=PAST_DATE_STR,
    ))
    assert result.safe is True
    assert result.constraint is not None
    assert result.constraint.date_from == PAST_DATE_OBJ
    assert result.blocks == []


def test_r4_normalizer_accepts_past_reference_date_with_today():
    """'today' with a stale/backdated reference_date resolves to a past date."""
    result = normalize_slot_search_command(
        _cmd(practitioner_id=PRAC_ID, date_from="today"),
        reference_date=STALE_REF_DATE,
    )
    assert result.safe is True
    assert result.constraint is not None
    assert result.constraint.date_from == STALE_REF_DATE
    assert result.blocks == []


def test_r4_normalizer_accepts_past_reference_date_with_tomorrow():
    """'tomorrow' with a stale reference_date resolves to stale-future."""
    result = normalize_slot_search_command(
        _cmd(practitioner_id=PRAC_ID, date_from="tomorrow"),
        reference_date=STALE_REF_DATE,
    )
    assert result.safe is True
    assert result.constraint is not None
    assert result.constraint.date_from == STALE_REF_DATE + timedelta(days=1)
    assert result.blocks == []


# =============================================================================
# 2.  Direct slot-search endpoints
# =============================================================================

def test_r4_propose_slot_search_accepts_past_date(
    client, db, gp_user, practice, practitioner, schedule, monkeypatch,
):
    """POST /proposals/slot-search with a past absolute date returns candidates."""
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        SLOT_SEARCH_URL,
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": PAST_DATE_STR,
            "date_to": PAST_DATE_STR,
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True, (
        f"GAP: direct slot-search accepts past date {PAST_DATE_STR} - "
        f"got safe={data['safe']}, blocks={data.get('blocks', [])}. "
        "No temporal past-date guard exists at this layer."
    )


def test_r4_normalized_slot_search_accepts_past_date(
    client, db, gp_user, practice, practitioner, schedule, monkeypatch,
):
    """POST /proposals/slot-search/normalized with past date returns candidates."""
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        NORMALIZED_URL,
        params={"reference_date": CLINIC_TODAY.isoformat()},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": PAST_DATE_STR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True, (
        f"GAP: normalized slot-search accepts past date {PAST_DATE_STR} - "
        f"got safe={data['safe']}, blocks={data.get('blocks', [])}."
    )


# =============================================================================
# 3.  Interpret flow
# =============================================================================

def test_r4_interpret_accepts_past_absolute_date(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """Interpret with a past absolute date runs slot search against that date."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{PAST_DATE_STR} duration:15"
            ),
            "reference_date": CLINIC_TODAY.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] not in ("blocked", "clinic_day_exhausted", "clarification_required"), (
        f"GAP: interpret accepts past absolute date {PAST_DATE_STR} - "
        f"got result={data['result']}."
    )


def test_r4_interpret_with_stale_reference_date(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """Interpret with stale reference_date + 'today' resolves to date in past."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                "date_from:today duration:15"
            ),
            "reference_date": STALE_REF_DATE.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] not in ("blocked", "clinic_day_exhausted"), (
        f"GAP: interpret accepts stale reference_date {STALE_REF_DATE.isoformat()} "
        f"with 'today' token - got result={data['result']}."
    )


# =============================================================================
# 4.  Supervised booking
# =============================================================================

def test_r4_supervised_booking_accepts_past_date(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """Supervised booking endpoint with past absolute date returns candidates."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": CLINIC_TODAY.isoformat(),
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": PAST_DATE_STR,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True, (
        f"GAP: supervised booking accepts past date {PAST_DATE_STR} - "
        f"got safe={data['safe']}."
    )


# =============================================================================
# 5.  Regression: same-day fully-past-window still blocked
# =============================================================================

def test_r4_same_day_fully_past_window_regression(
    client, db, gp_user, practice, practitioner, schedule, monkeypatch,
):
    """Same-day fully-past time window via supervised booking must be blocked."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": CLINIC_TODAY.isoformat(),
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": CLINIC_TODAY.isoformat(),
                "earliest_time": "08:00",
                "latest_time": "08:00",
                "duration_minutes": "15",
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False, (
        f"REGRESSION: same-day fully-past window should be blocked - "
        f"got safe={data['safe']}."
    )


def test_r4_same_day_fully_past_window_interpret_regression(
    client, db, gp_user, practice, practitioner, schedule, monkeypatch,
):
    """Interpret with same-day fully-past time window must be blocked."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} date_from:{CLINIC_TODAY.isoformat()} "
                "earliest_time:08:00 latest_time:08:00 duration:15"
            ),
            "reference_date": CLINIC_TODAY.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] != "interpreted", (
        f"REGRESSION: same-day fully-past window should be blocked via interpret - "
        f"got result={data['result']}."
    )


# =============================================================================
# 6.  Regression: D8 collision semantics preserved
# =============================================================================

def test_r4_d8_collision_warning_still_emitted(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """D8 collision warning must still be emitted for same-day conflicts."""
    from app.models.appointments import AppointmentStatus, BookingChannel

    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    # Create an existing booking on Wednesday 2026-07-15
    collision_date = date(2026, 7, 15)
    collision_date_str = "2026-07-15"
    appt = appointments_router.Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(2026, 7, 15, 11, 0, tzinfo=timezone.utc),
        appointment_date=collision_date,
        start_time_local=time(11, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": CLINIC_TODAY.isoformat(),
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": collision_date_str,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        f"REGRESSION: D8 collision warning not emitted. warnings={warning_codes}"
    )


# =============================================================================
# 7.  Broader mutation surfaces (xfail - outside slot-search scope)
# =============================================================================

@pytest.mark.xfail(strict=False, reason="Outside Bernie slot-search scope: raw create endpoint has no past-date guard")
def test_r4_raw_create_endpoint_accepts_past_date(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """POST /appointments with a past appointment_date succeeds (broad surface)."""
    from app.models.appointments import BookingChannel

    token = make_token(gp_user)
    past_dt = datetime(2026, 7, 6, 10, 0, tzinfo=timezone.utc)

    resp = client.post(
        CREATE_URL,
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": past_dt.isoformat(),
            "duration_minutes": 15,
            "booked_via": BookingChannel.Receptionist.value,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201, resp.text


@pytest.mark.xfail(strict=False, reason="Outside Bernie slot-search scope: propose-create has no past-date guard")
def test_r4_propose_create_accepts_past_date(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """POST /proposals/create with a past appointment_date succeeds (broad surface)."""
    token = make_token(gp_user)
    past_dt = datetime(2026, 7, 6, 10, 0, tzinfo=timezone.utc)

    resp = client.post(
        PROPOSE_CREATE_URL,
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": past_dt.isoformat(),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True, (
        f"GAP: propose-create accepts past date - "
        f"got safe={data['safe']}."
    )
