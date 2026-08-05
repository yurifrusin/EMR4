"""A5.1 Rayleen check-in command runtime tests.

Dedicated, default-off, authored-synthetic-practice-only,
Receptionist-confirmed check-in proposal/confirm command for the exact
Booked|Confirmed -> Arrived transition. Rayleen is proposal provenance only.
All evidence is authored-synthetic local; there are zero provider/product calls.
"""

import hashlib
import threading
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary import WaitingArea
from app.models.diary_events import DiaryCommittedEvent
from app.models.tenancy import PracticeLocation, User, UserRole
from app.schemas.appointments import (
    AppointmentCheckInCommand,
    AppointmentCheckInProposalConfirmationIn,
    AppointmentCheckInProposalOut,
    AppointmentProposalIssue,
)
from app.services.appointment_idempotency import (
    claim_appointment_check_in_command,
    mint_check_in_evidence_token,
)
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
CONFIRM_URL = "/api/v1/appointments/proposals/check-in/confirm"
EVENT_URL = "/api/v1/diary/events/committed"
UPDATE_CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
REFERENCE_DATE = date(2026, 8, 5)


@pytest.fixture(autouse=True)
def _a5_runtime(monkeypatch, practice):
    monkeypatch.setattr(settings, "rayleen_a5_check_in_enabled", True)
    monkeypatch.setattr(
        settings,
        "rayleen_a5_check_in_synthetic_practice_ids",
        str(practice.id),
    )
    monkeypatch.setattr(
        settings, "reception_one_committed_event_runtime_enabled", True
    )
    monkeypatch.setattr(
        appointments_router,
        "_clinic_local_now",
        lambda tz: datetime(2026, 8, 5, 9, 0, 0, tzinfo=tz),
    )


def _auth(user, key=None):
    headers = {"Authorization": f"Bearer {make_token(user)}"}
    if key is not None:
        headers["Idempotency-Key"] = key
    return headers


def _make_location(db, practice, *, name="Main Clinic"):
    loc = PracticeLocation(
        practice_id=practice.id, name=name, is_active=True
    )
    db.add(loc)
    db.flush()
    return loc


def _make_area(db, practice, location=None, *, name="Main Waiting", active=True):
    area = WaitingArea(
        practice_id=practice.id,
        location_id=location.id if location else None,
        name=name,
        is_active=active,
    )
    db.add(area)
    db.flush()
    return area


def _make_appt(
    db,
    practice,
    practitioner,
    patient,
    *,
    status=AppointmentStatus.Booked,
    location=None,
    waiting_area=None,
    hour=9,
):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        location_id=location.id if location else None,
        start_time=datetime.combine(
            REFERENCE_DATE,
            time(hour),
            tzinfo=timezone(timedelta(hours=10)),
        ).astimezone(timezone.utc),
        appointment_date=REFERENCE_DATE,
        start_time_local=time(hour),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
        waiting_area_id=waiting_area.id if waiting_area else None,
    )
    db.add(appt)
    db.flush()
    # The HTTP route owns and may roll back its transaction. Persist the
    # authored-synthetic setup first so a rejected or injected-failure request
    # cannot expunge the baseline appointment used for zero-effect readback.
    db.commit()
    db.refresh(appt)
    return appt


def _proposal(client, user, appt_id, *, waiting_area_id=None, key=None):
    body = {}
    if waiting_area_id is not None:
        body["waiting_area_id"] = str(waiting_area_id)
    response = client.post(
        f"/api/v1/appointments/proposals/check-in/{appt_id}",
        json=body,
        headers=_auth(user, key or f"ci-proposal-{appt_id}"),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if not data.get("confirm_payload"):
        return None, data
    payload = data["confirm_payload"]
    payload["confirmed"] = True
    return payload, data


def _confirm(client, user, payload, key):
    return client.post(
        CONFIRM_URL, json=payload, headers=_auth(user, key)
    )


def _receptionist(db, practice, email):
    u = User(
        practice_id=practice.id,
        email=email,
        password_hash="x",
        role=UserRole.Receptionist,
    )
    db.add(u)
    db.flush()
    return u


def _reschedule_payload(client, user, appointment_id, *, hour=10, key=None):
    body = {
        "appointment_date": REFERENCE_DATE.isoformat(),
        "start_time_local": f"{hour:02d}:00:00",
    }
    response = client.post(
        f"/api/v1/appointments/proposals/update/{appointment_id}",
        json=body,
        headers=_auth(user, key or f"ci-resched-{appointment_id}-{hour}"),
    )
    assert response.status_code == 200, response.text
    payload = response.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _row_counts(db):
    return (
        db.query(AppointmentAuditLog).count(),
        db.query(DiaryCommittedEvent).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


# ── Valid source states and assignment/preservation ──────────────────────────


def test_booked_to_arrived_without_assignment(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, data = _proposal(client, receptionist_user, appt.id)
    assert data["safe"] is True
    assert data["autonomy_tier"] == "execute_with_report"
    assert isinstance(data["signed_confirmation_evidence"], str)
    assert data["signed_confirmation_evidence_required"] is True

    resp = _confirm(client, receptionist_user, payload, "ci-booked-arrived")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["safe"] is True
    assert body["autonomy_tier"] == "confirmed_write"
    receipt = body["receipt"]
    assert receipt["appointment_id"] == str(appt.id)
    assert receipt["status"] == "Arrived"
    assert receipt["waiting_area_id"] is None
    assert receipt["audit_log_id"] and receipt["event_id"] and receipt["command_id"]
    assert set(receipt) == {
        "schema_version",
        "appointment_id",
        "status",
        "waiting_area_id",
        "audit_log_id",
        "event_id",
        "command_id",
        "commit_time",
    }
    assert not ({"patient_id", "patient_name", "reason", "notes"} & set(receipt))
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived
    assert appt.waiting_area_id is None
    assert _row_counts(db) == (1, 1, 1)


def test_confirmed_to_arrived_with_assignment(
    client, db, receptionist_user, practice, practitioner, patient
):
    loc = _make_location(db, practice)
    area = _make_area(db, practice, loc)
    appt = _make_appt(
        db,
        practice,
        practitioner,
        patient,
        status=AppointmentStatus.Confirmed,
        location=loc,
    )
    payload, data = _proposal(
        client, receptionist_user, appt.id, waiting_area_id=area.id
    )
    assert data["safe"] is True
    assert data["command"]["waiting_area_id"] == str(area.id)
    assert data["command"]["waiting_area_id_supplied"] is True

    resp = _confirm(client, receptionist_user, payload, "ci-confirmed-area")
    assert resp.status_code == 200, resp.text
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived
    assert appt.waiting_area_id == area.id
    event = db.query(DiaryCommittedEvent).one()
    assert event.payload["waiting_area_id_before"] is None
    assert event.payload["waiting_area_id_after"] == str(area.id)
    assert event.payload["status_before"] == "Confirmed"


def test_preserves_existing_area_when_omitted(
    client, db, receptionist_user, practice, practitioner, patient
):
    loc = _make_location(db, practice)
    area = _make_area(db, practice, loc)
    appt = _make_appt(
        db,
        practice,
        practitioner,
        patient,
        status=AppointmentStatus.Booked,
        location=loc,
        waiting_area=area,
    )
    payload, data = _proposal(client, receptionist_user, appt.id)
    assert data["safe"] is True
    assert data["command"]["waiting_area_id_supplied"] is False

    resp = _confirm(client, receptionist_user, payload, "ci-preserve-area")
    assert resp.status_code == 200, resp.text
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived
    assert appt.waiting_area_id == area.id
    event = db.query(DiaryCommittedEvent).one()
    assert event.payload["waiting_area_id_before"] == str(area.id)
    assert event.payload["waiting_area_id_after"] == str(area.id)


def test_assign_area_when_area_already_set_is_blocked(
    client, db, receptionist_user, practice, practitioner, patient
):
    loc = _make_location(db, practice)
    area1 = _make_area(db, practice, loc, name="Area One")
    area2 = _make_area(db, practice, loc, name="Area Two")
    appt = _make_appt(
        db,
        practice,
        practitioner,
        patient,
        location=loc,
        waiting_area=area1,
    )
    _, data = _proposal(
        client, receptionist_user, appt.id, waiting_area_id=area2.id
    )
    assert data["safe"] is False
    assert any(
        b["code"] == "waiting_area_move_not_supported" for b in data["blocks"]
    )
    assert data["signed_confirmation_evidence"] is None


# ── Non-mutating proposal, gate and authority ────────────────────────────────


def test_proposal_is_non_mutating(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    before = _row_counts(db)
    payload, data = _proposal(client, receptionist_user, appt.id)
    assert payload is not None
    assert data["safe"] is True
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_default_off_and_non_allowlisted_rejection(
    monkeypatch,
    client,
    db,
    receptionist_user,
    practice,
    practice_b,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    monkeypatch.setattr(settings, "rayleen_a5_check_in_enabled", False)
    resp = client.post(
        f"/api/v1/appointments/proposals/check-in/{appt.id}",
        json={},
        headers=_auth(receptionist_user, "ci-off-prop"),
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "check_in_runtime_disabled"
    valid_body = AppointmentCheckInProposalConfirmationIn(
        confirmed=True,
        check_in_proposal=AppointmentCheckInProposalOut(
            safe=True,
            requires_confirmation=True,
            autonomy_tier="execute_with_report",
            summary="x",
            command=AppointmentCheckInCommand(
                appointment_id=appt.id, waiting_area_id_supplied=False
            ),
        ),
    ).model_dump(mode="json")
    resp = client.post(
        CONFIRM_URL, json=valid_body, headers=_auth(receptionist_user, "ci-off-confirm")
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "check_in_runtime_disabled"

    monkeypatch.setattr(settings, "rayleen_a5_check_in_enabled", True)
    monkeypatch.setattr(
        settings, "rayleen_a5_check_in_synthetic_practice_ids", str(practice_b.id)
    )
    resp = client.post(
        f"/api/v1/appointments/proposals/check-in/{appt.id}",
        json={},
        headers=_auth(receptionist_user, "ci-not-allowed"),
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "check_in_practice_not_allowlisted"
    assert _row_counts(db) == (0, 0, 0)


def test_receptionist_only_authority(
    client, db, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    for role in (UserRole.GP, UserRole.Nurse, UserRole.Admin, UserRole.PracticeOwner):
        u = User(
            practice_id=practice.id,
            email=f"{role.value.lower()}@test.local",
            password_hash="x",
            role=role,
        )
        db.add(u)
        db.flush()
        resp = client.post(
            f"/api/v1/appointments/proposals/check-in/{appt.id}",
            json={},
            headers=_auth(u, f"ci-role-{role.value}"),
        )
        assert resp.status_code == 403, (role, resp.status_code)
        assert resp.json()["detail"] == "Insufficient permissions"
    rec = _receptionist(db, practice, "rec-ok@test.local")
    resp = client.post(
        f"/api/v1/appointments/proposals/check-in/{appt.id}",
        json={},
        headers=_auth(rec, "ci-role-rec"),
    )
    assert resp.status_code == 200, resp.text
    assert _row_counts(db) == (0, 0, 0)


# ── Evidence tamper/expiry/purpose/actor/practice failures ───────────────────


def test_tampered_evidence_rejected_without_effects(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    encoded, signature = payload["signed_confirmation_evidence"].rsplit(".", 1)
    tampered = encoded + "." + ("0" if signature[0] != "0" else "1") + signature[1:]
    payload["signed_confirmation_evidence"] = tampered

    resp = _confirm(client, receptionist_user, payload, "ci-tamper")
    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(
        b["code"] == "signed_evidence_tampered" for b in resp.json()["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_expired_evidence_rejected_without_effects(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    freshness = payload["check_in_proposal_freshness_id"]
    expired_token = mint_check_in_evidence_token(
        practice_id=practice.id,
        actor_user_id=receptionist_user.id,
        appointment_id=appt.id,
        status_before="Booked",
        waiting_area_id_before=None,
        waiting_area_id_target=None,
        check_in_proposal_freshness_id=freshness,
        secret=settings.secret_key.encode("utf-8"),
        issued_at=datetime.now(timezone.utc) - timedelta(seconds=200),
        ttl_seconds=120,
    )
    payload["signed_confirmation_evidence"] = expired_token
    payload["signed_confirmation_evidence_required"] = True

    resp = _confirm(client, receptionist_user, payload, "ci-expired")
    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(
        b["code"] == "signed_evidence_expired" for b in resp.json()["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_wrong_purpose_evidence_rejected_without_effects(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    freshness = payload["check_in_proposal_freshness_id"]
    wrong_token = mint_check_in_evidence_token(
        practice_id=practice.id,
        actor_user_id=receptionist_user.id,
        appointment_id=appt.id,
        status_before="Booked",
        waiting_area_id_before=None,
        waiting_area_id_target=None,
        check_in_proposal_freshness_id=freshness,
        secret=settings.secret_key.encode("utf-8"),
        purpose="some_other_purpose",
    )
    payload["signed_confirmation_evidence"] = wrong_token
    payload["signed_confirmation_evidence_required"] = True

    resp = _confirm(client, receptionist_user, payload, "ci-purpose")
    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(
        b["code"] == "signed_evidence_wrong_purpose"
        for b in resp.json()["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_wrong_actor_evidence_rejected_without_effects(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    other = _receptionist(db, practice, "rec-other@test.local")

    resp = _confirm(client, other, payload, "ci-wrong-actor")
    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(
        b["code"] == "signed_evidence_mismatch" for b in resp.json()["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_wrong_practice_rejects_without_effects(
    monkeypatch,
    client,
    db,
    receptionist_user,
    practice,
    practice_b,
    practitioner,
    patient,
):
    monkeypatch.setattr(
        settings,
        "rayleen_a5_check_in_synthetic_practice_ids",
        f"{practice.id},{practice_b.id}",
    )
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    foreign_rec = _receptionist(db, practice_b, "rec-foreign@test.local")

    resp = _confirm(client, foreign_rec, payload, "ci-wrong-practice")
    assert resp.status_code == 404, resp.text
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


# ── Location and active-area checks ──────────────────────────────────────────


def test_inactive_area_rejected(
    client, db, receptionist_user, practice, practitioner, patient
):
    loc = _make_location(db, practice)
    inactive = _make_area(db, practice, loc, name="Closed", active=False)
    appt = _make_appt(db, practice, practitioner, patient, location=loc)
    _, data = _proposal(
        client, receptionist_user, appt.id, waiting_area_id=inactive.id
    )
    assert data["safe"] is False
    assert any(
        b["code"] == "waiting_area_not_active" for b in data["blocks"]
    )
    assert data["signed_confirmation_evidence"] is None


def test_cross_practice_area_rejected(
    client, db, receptionist_user, practice, practice_b, practitioner, patient
):
    loc = _make_location(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, location=loc)
    foreign_loc = _make_location(db, practice_b, name="Foreign")
    foreign_area = _make_area(db, practice_b, foreign_loc, name="Foreign Area")
    _, data = _proposal(
        client, receptionist_user, appt.id, waiting_area_id=foreign_area.id
    )
    assert data["safe"] is False
    assert any(
        b["code"] == "waiting_area_not_active" for b in data["blocks"]
    )


def test_location_mismatch_area_rejected(
    client, db, receptionist_user, practice, practitioner, patient
):
    loc1 = _make_location(db, practice, name="Loc One")
    loc2 = _make_location(db, practice, name="Loc Two")
    area = _make_area(db, practice, loc2)
    appt = _make_appt(db, practice, practitioner, patient, location=loc1)
    _, data = _proposal(
        client, receptionist_user, appt.id, waiting_area_id=area.id
    )
    assert data["safe"] is False
    assert any(
        b["code"] == "waiting_area_location_mismatch" for b in data["blocks"]
    )


def test_null_location_appointment_cannot_assign_area(
    client, db, receptionist_user, practice, practitioner, patient
):
    loc = _make_location(db, practice)
    area = _make_area(db, practice, loc)
    appt = _make_appt(db, practice, practitioner, patient)
    _, data = _proposal(
        client, receptionist_user, appt.id, waiting_area_id=area.id
    )
    assert data["safe"] is False
    assert any(
        b["code"] == "waiting_area_location_required" for b in data["blocks"]
    )


# ── Stale, no-op and terminal-state denial ───────────────────────────────────


def test_stale_state_denied_without_effects(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(
        db, practice, practitioner, patient, status=AppointmentStatus.Booked
    )
    payload, _ = _proposal(client, receptionist_user, appt.id)
    appt.status = AppointmentStatus.Confirmed
    db.commit()

    resp = _confirm(client, receptionist_user, payload, "ci-stale")
    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(
        b["code"] == "stale_check_in_proposal_freshness_id"
        for b in resp.json()["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == (0, 0, 0)


def test_noop_arrived_denied_at_proposal(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(
        db, practice, practitioner, patient, status=AppointmentStatus.Arrived
    )
    _, data = _proposal(client, receptionist_user, appt.id)
    assert data["safe"] is False
    assert any(b["code"] == "already_arrived" for b in data["blocks"])
    assert data["signed_confirmation_evidence"] is None
    assert _row_counts(db) == (0, 0, 0)


def test_terminal_source_denied_at_proposal(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(
        db, practice, practitioner, patient, status=AppointmentStatus.Cancelled
    )
    _, data = _proposal(client, receptionist_user, appt.id)
    assert data["safe"] is False
    assert any(b["code"] == "invalid_source_status" for b in data["blocks"])
    assert data["signed_confirmation_evidence"] is None
    assert _row_counts(db) == (0, 0, 0)


def test_confirm_of_blocked_noop_has_zero_effects(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(
        db, practice, practitioner, patient, status=AppointmentStatus.Arrived
    )
    blocked_proposal = AppointmentCheckInProposalOut(
        safe=False,
        requires_confirmation=True,
        autonomy_tier="blocked",
        summary="x",
        command=AppointmentCheckInCommand(
            appointment_id=appt.id, waiting_area_id_supplied=False
        ),
        blocks=[
            AppointmentProposalIssue(
                code="already_arrived", severity="blocked", message="x"
            )
        ],
    )
    body = AppointmentCheckInProposalConfirmationIn(
        confirmed=True, check_in_proposal=blocked_proposal
    ).model_dump(mode="json")
    resp = client.post(
        CONFIRM_URL, json=body, headers=_auth(receptionist_user, "ci-blocked-noop")
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(
        b["code"] == "check_in_proposal_not_safe" for b in resp.json()["blocks"]
    )
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived
    assert _row_counts(db) == (0, 0, 0)


# ── Idempotency: replay, conflict, in-progress, evidence reuse ───────────────


def test_same_key_replay_returns_stored_receipt_without_second_effect(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    first = _confirm(client, receptionist_user, payload, "ci-replay")
    assert first.status_code == 200, first.text
    counts = _row_counts(db)

    second = _confirm(client, receptionist_user, payload, "ci-replay")
    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    assert _row_counts(db) == counts
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived


def test_same_key_changed_body_conflicts_without_effect(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    first = _confirm(client, receptionist_user, payload, "ci-conflict")
    assert first.status_code == 200, first.text
    counts = _row_counts(db)

    modified = dict(payload)
    modified["confirmed_warnings"] = ["extra-warning"]
    second = _confirm(client, receptionist_user, modified, "ci-conflict")
    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    assert _row_counts(db) == counts


def test_in_progress_denial_fails_closed(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    canonical = AppointmentCheckInProposalConfirmationIn(
        **payload
    ).model_dump(mode="json")
    evidence_hash = hashlib.sha256(
        payload["signed_confirmation_evidence"].encode("utf-8")
    ).hexdigest()
    claim = claim_appointment_check_in_command(
        db,
        practice_id=receptionist_user.practice_id,
        actor_user_id=str(receptionist_user.id),
        actor_role="Receptionist",
        operation_id="confirmAppointmentCheckInProposal",
        route_family="check-in-confirm",
        raw_idempotency_key="ci-inprogress",
        request_body=canonical,
        secret=settings.secret_key.encode("utf-8"),
        confirmation_evidence_hash=evidence_hash,
        stale_after=timedelta(minutes=10),
    )
    assert claim.kind == "started"
    db.commit()
    before = _row_counts(db)

    resp = _confirm(client, receptionist_user, payload, "ci-inprogress")
    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_in_progress"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_different_key_evidence_replay_rejected_after_state_restoration(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    first = _confirm(client, receptionist_user, payload, "ci-key-a")
    assert first.status_code == 200, first.text

    db.refresh(appt)
    appt.status = AppointmentStatus.Booked
    appt.waiting_area_id = None
    db.commit()
    counts = _row_counts(db)

    second = _confirm(client, receptionist_user, payload, "ci-key-b")
    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "confirmation_replay_rejected"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == counts


def test_concurrent_distinct_key_evidence_claim_single_winner(
    engine, db, practice, receptionist_user
):
    practice_id = receptionist_user.practice_id
    actor_user_id = str(receptionist_user.id)
    # The two workers use independent database sessions, so their referenced
    # practice and actor must be visible outside the fixture session.
    db.commit()
    Session_ = sessionmaker(bind=engine)
    evidence_hash = hashlib.sha256(b"same-evidence-token").hexdigest()
    results = []
    barrier = threading.Barrier(2)

    def run(key):
        session = Session_()
        try:
            barrier.wait()
            decision = claim_appointment_check_in_command(
                session,
                practice_id=practice_id,
                actor_user_id=actor_user_id,
                actor_role="Receptionist",
                operation_id="confirmAppointmentCheckInProposal",
                route_family="check-in-confirm",
                raw_idempotency_key=key,
                request_body={},
                secret=settings.secret_key.encode("utf-8"),
                confirmation_evidence_hash=evidence_hash,
                stale_after=timedelta(minutes=10),
            )
            if decision.kind == "started":
                session.commit()
            results.append(decision.kind)
        finally:
            session.close()

    threads = [
        threading.Thread(target=run, args=(key,))
        for key in ("ci-concurrent-a", "ci-concurrent-b")
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(results) == ["evidence_replay_rejected", "started"]


# ── Atomic rollback injection ────────────────────────────────────────────────


def test_evidence_claim_failure_rolls_back_every_member(
    monkeypatch, client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)

    def fail_claim(*args, **kwargs):
        raise RuntimeError("injected claim failure")

    monkeypatch.setattr(
        appointments_router, "claim_appointment_check_in_command", fail_claim
    )
    resp = _confirm(client, receptionist_user, payload, "ci-claim-fail")
    assert resp.status_code == 500
    db.rollback()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_audit_write_failure_rolls_back_every_member(
    monkeypatch, client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    original = appointments_router._write_audit

    def fail_audit(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("injected audit failure")

    monkeypatch.setattr(appointments_router, "_write_audit", fail_audit)
    resp = _confirm(client, receptionist_user, payload, "ci-audit-fail")
    assert resp.status_code == 500
    db.rollback()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_event_write_failure_rolls_back_every_member(
    monkeypatch, client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    original = appointments_router.record_appointment_checked_in_event

    def fail_event(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("injected event failure")

    monkeypatch.setattr(
        appointments_router, "record_appointment_checked_in_event", fail_event
    )
    resp = _confirm(client, receptionist_user, payload, "ci-event-fail")
    assert resp.status_code == 500
    db.rollback()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


def test_idempotency_completion_failure_rolls_back_every_member(
    monkeypatch, client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)

    def fail_complete(*args, **kwargs):
        raise RuntimeError("injected completion failure")

    monkeypatch.setattr(
        appointments_router, "complete_appointment_command", fail_complete
    )
    resp = _confirm(client, receptionist_user, payload, "ci-complete-fail")
    assert resp.status_code == 500
    db.rollback()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == (0, 0, 0)


# ── Exact audit and event payload ────────────────────────────────────────────


def test_exact_audit_and_event_payload(
    client, db, receptionist_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    resp = _confirm(client, receptionist_user, payload, "ci-exact")
    assert resp.status_code == 200, resp.text

    event = db.query(DiaryCommittedEvent).one()
    audit = db.query(AppointmentAuditLog).one()
    command = db.query(AppointmentCommandIdempotency).one()
    assert event.event_type == "diary.appointment_checked_in"
    assert event.schema_version == "diary.appointment_checked_in.v1"
    assert event.source_system == "emr4-diary"
    assert event.evidence_mode == "authored_synthetic_local"
    assert set(event.payload) == {
        "appointment_id",
        "practitioner_id",
        "location_id",
        "status_before",
        "status_after",
        "waiting_area_id_before",
        "waiting_area_id_after",
        "reason_codes",
    }
    assert event.payload["reason_codes"] == ["appointment_checked_in"]
    assert event.payload["status_before"] == "Booked"
    assert event.payload["status_after"] == "Arrived"
    assert not (
        {"patient_id", "patient_name", "reason", "notes"} & set(event.payload)
    )
    assert event.command_id == command.id == audit.command_id
    assert event.audit_log_id == audit.id == command.audit_log_id
    assert event.correlation_id == command.id
    assert audit.action.value == "status_change"
    assert audit.status_before == AppointmentStatus.Booked
    assert audit.status_after == AppointmentStatus.Arrived
    assert command.state == "completed"
    assert command.operation_id == "confirmAppointmentCheckInProposal"
    assert command.route_family == "check-in-confirm"
    assert command.confirmation_evidence_hash
    assert command.confirmation_evidence_consumed_at is not None
    assert command.target_appointment_id == appt.id

    receipt = resp.json()["receipt"]
    assert receipt["event_id"] == str(event.id)
    assert receipt["audit_log_id"] == str(audit.id)
    assert receipt["command_id"] == str(command.id)


# ── Reschedule-feed isolation ────────────────────────────────────────────────


def test_check_in_event_never_enters_reschedule_feed(
    client, db, receptionist_user, practice, practitioner, patient
):
    baseline = client.get(EVENT_URL, headers=_auth(receptionist_user)).json()
    assert baseline["baseline_established"] is True

    appt = _make_appt(db, practice, practitioner, patient)
    payload, _ = _proposal(client, receptionist_user, appt.id)
    assert _confirm(
        client, receptionist_user, payload, "ci-feed-isolation"
    ).status_code == 200

    delivered = client.get(
        EVENT_URL,
        params={"cursor": baseline["cursor"]},
        headers=_auth(receptionist_user),
    ).json()
    assert delivered["events"] == []


def test_interleaved_check_in_row_does_not_corrupt_reschedule_feed(
    client, db, receptionist_user, practice, practitioner, patient
):
    baseline = client.get(EVENT_URL, headers=_auth(receptionist_user)).json()
    appt = _make_appt(db, practice, practitioner, patient)
    reschedule_payload = _reschedule_payload(
        client, receptionist_user, appt.id, hour=10, key="ci-feed-resched"
    )
    resched_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=reschedule_payload,
        headers=_auth(receptionist_user, "ci-feed-resched-confirm"),
    )
    assert resched_resp.status_code == 200, resched_resp.text
    check_in_payload, _ = _proposal(client, receptionist_user, appt.id)
    assert _confirm(
        client, receptionist_user, check_in_payload, "ci-feed-checkin"
    ).status_code == 200

    delivered = client.get(
        EVENT_URL,
        params={"cursor": baseline["cursor"]},
        headers=_auth(receptionist_user),
    ).json()
    assert len(delivered["events"]) == 1
    event = delivered["events"][0]
    assert event["event_type"] == "diary.appointment_rescheduled"
    assert event["payload"]["reason_codes"] == ["appointment_time_changed"]
    assert "status_before" not in event["payload"]
    assert delivered["cursor"] != baseline["cursor"]


# ── Migration constraints and one Alembic head ───────────────────────────────


def test_migration_adds_columns_constraints_and_unique_index():
    migration = (
        ROOT
        / "alembic"
        / "versions"
        / "v1w2x3y4z5a6_add_a5_check_in_runtime.py"
    ).read_text(encoding="utf-8")
    for fragment in (
        "confirmation_evidence_hash",
        "confirmation_evidence_consumed_at",
        "uq_appt_cmd_idem_evidence_hash",
        "ck_appt_cmd_idem_completed_check_in_evidence",
        "diary.appointment_checked_in",
        "diary.appointment_checked_in.v1",
        "appointment_checked_in",
        "waiting_area_id_before",
        "waiting_area_id_after",
        'down_revision: Union[str, Sequence[str], None] = "u0v1w2x3y4z5"',
    ):
        assert fragment in migration
    for fragment in (
        "_PRIOR_TYPE",
        "_PRIOR_SCHEMA",
        "_PRIOR_PAYLOAD",
        "appointment_time_changed",
    ):
        assert fragment in migration


def test_migration_keeps_one_alembic_head():
    import alembic.config
    import alembic.script

    cfg = alembic.config.Config(str(ROOT / "alembic.ini"))
    script = alembic.script.ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert heads == ["v1w2x3y4z5b6"]
    assert len(heads) == 1


def test_model_declares_check_in_evidence_columns_and_index():
    table = AppointmentCommandIdempotency.__table__
    assert "confirmation_evidence_hash" in table.columns
    assert "confirmation_evidence_consumed_at" in table.columns
    assert table.c.confirmation_evidence_hash.nullable is True
    assert table.c.confirmation_evidence_consumed_at.nullable is True
    indexes = {index.name for index in table.indexes}
    assert "uq_appt_cmd_idem_evidence_hash" in indexes


# ── Zero patient-bearing fields and zero product-provider calls ──────────────


def test_zero_patient_fields_and_zero_provider_calls_in_check_in_path():
    router = (
        ROOT / "app" / "routers" / "appointments.py"
    ).read_text(encoding="utf-8")
    start = router.index("── A5.1 Rayleen check-in")
    end = router.index('@router.get("/waiting-room"', start)
    section = router[start:end]
    for forbidden in (
        "vertex",
        "gemini",
        "run_isolated_vertex_planner",
        "access_ai",
        "provider_call",
    ):
        assert forbidden not in section.lower()

    event_service = (
        ROOT / "app" / "services" / "diary_committed_events.py"
    ).read_text(encoding="utf-8")
    assert "patient_id" not in event_service
    for forbidden in ("vertex", "gemini", "provider"):
        assert forbidden not in event_service.lower()

    receipt_schema = (
        ROOT / "app" / "schemas" / "appointments.py"
    ).read_text(encoding="utf-8")
    receipt_block = receipt_schema[
        receipt_schema.index("class AppointmentCheckInReceipt") :
        receipt_schema.index("class AppointmentConfirmCheckInProposalOut")
    ]
    for forbidden in (
        "patient_id",
        "patient_name",
        "reason",
        "notes",
        "clinical",
        "dob",
    ):
        assert forbidden not in receipt_block.lower()
