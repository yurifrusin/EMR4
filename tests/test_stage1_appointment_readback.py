"""Selected read-only singleton readback cases for the isolated G4 DB capsule."""

from copy import deepcopy

from sqlalchemy.orm import Session

from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentCommandIdempotency
from app.models.diary_events import DiaryCommittedEvent
from app.models.tenancy import Practice, User, UserRole
from app.services.auth_service import create_access_token, hash_password


MOVE = "/api/v1/appointments/proposals/move-time/{}"
CONFIRM = "/api/v1/appointments/proposals/update/confirm"
READ = "/api/v1/appointments/readback/{}"


def _headers(user, key=None):
    token = create_access_token({
        "sub": str(user.id), "practice_id": str(user.practice_id),
        "role": user.role.value,
    })
    result = {"Authorization": f"Bearer {token}"}
    if key is not None:
        result["Idempotency-Key"] = key
    return result


def _physical(db, practice_id):
    with Session(bind=db.get_bind()) as observer:
        appointment = observer.query(Appointment).filter_by(practice_id=practice_id).one()
        return {
            "id": appointment.id,
            "version": appointment.appointment_state_version,
            "utc_start": appointment.start_time,
            "audit_count": observer.query(AppointmentAuditLog).filter_by(practice_id=practice_id).count(),
            "command_count": observer.query(AppointmentCommandIdempotency).filter_by(practice_id=practice_id).count(),
            "event_count": observer.query(DiaryCommittedEvent).filter_by(practice_id=practice_id).count(),
        }


def _move(client, row, user):
    intent = {
        "schema_version": "appointment.move_time_intent.v1",
        "tenant_id": str(user.practice_id), "actor_id": str(user.id),
        "role": "reception", "source_appointment_id": str(row.id),
        "source_state_version": row.appointment_state_version,
        "source_revision": row.appointment_state_version,
        "target_date": row.appointment_date.isoformat(),
        "target_start_local": "11:00", "authority": "proposal_only",
    }
    proposal = client.post(MOVE.format(row.id), json=intent,
                           headers=_headers(user, "g4-readback-proposal"))
    assert proposal.status_code == 200, proposal.text
    assert proposal.json()["safe"] is True
    payload = deepcopy(proposal.json()["confirm_payload"])
    payload["confirmed"] = True
    confirmed = client.post(CONFIRM, json=payload,
                            headers=_headers(user, "g4-readback-confirm"))
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["safe"] is True


def test_normal_and_fallback_readback_are_same_complete_read_only_source(
    client, db, practice, seeded_appointment, reception_user,
):
    row = seeded_appointment
    before = _physical(db, practice.id)
    assert before["version"] == 1
    _move(client, row, reception_user)
    committed = _physical(db, practice.id)
    assert committed["id"] == row.id and committed["version"] == before["version"] + 1
    assert committed["utc_start"] != before["utc_start"]
    assert (committed["audit_count"], committed["command_count"],
            committed["event_count"]) == (1, 1, 1)

    normal = client.get(READ.format(row.id) + "?mode=normal",
                        headers=_headers(reception_user))
    fallback = client.get(READ.format(row.id) + "?mode=fallback",
                          headers=_headers(reception_user))
    assert normal.status_code == fallback.status_code == 200
    first, second = normal.json(), fallback.json()
    for view in (first, second):
        assert view["schema_version"] == "appointment.list_projection.v2"
        assert view["read_only"] is True
        assert view["affordances"] == {
            "create": False, "update": False, "cancel": False, "confirm": False,
        }
        assert view["source"]["id"] == str(row.id)
        assert view["source"]["revision"] == committed["version"]
        assert view["source"]["total_count"] == 1
        assert view["source"]["is_complete"] is True
        assert len(view["items"]) == 1
        item = view["items"][0]
        assert item["id"] == str(row.id)
        assert item["practice_id"] == str(practice.id)
        assert item["source_version"] == committed["version"]
        assert item["start_time"].startswith(committed["utc_start"].strftime("%Y-%m-%dT%H:%M"))
        assert item["accessibility_label"]
    assert first["items"] == second["items"]
    assert first["source"]["revision"] == second["source"]["revision"]
    assert _physical(db, practice.id) == committed  # GET did not write.


def test_readback_enforces_current_tenant_and_reception_role_without_effect(
    client, db, practice, seeded_appointment, reception_user, gp_user,
):
    row = seeded_appointment
    before = _physical(db, practice.id)
    wrong_role = client.get(READ.format(row.id), headers=_headers(gp_user))
    assert wrong_role.status_code == 403, wrong_role.text

    other = Practice(name="Other authored synthetic practice", timezone="Australia/Brisbane")
    db.add(other)
    db.flush()
    outsider = User(practice_id=other.id, email="other@synthetic.invalid",
                    password_hash=hash_password("Password1!"),
                    role=UserRole.Receptionist)
    db.add(outsider)
    db.commit()
    wrong_tenant = client.get(READ.format(row.id), headers=_headers(outsider))
    assert wrong_tenant.status_code == 404, wrong_tenant.text
    assert _physical(db, practice.id) == before
