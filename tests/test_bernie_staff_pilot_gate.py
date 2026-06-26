import inspect

import app.routers.appointments as appointments_router
import app.services.bernie_pilot_gate as bernie_pilot_gate
from app.models.appointments import Appointment, AppointmentAuditLog
from tests.conftest import make_token


PILOT_URL = "/api/v1/appointments/bernie/pilot-eligibility"


def _get(client, token=None):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    return client.get(PILOT_URL, headers=headers)


def _set_gate(monkeypatch, *, enabled=False, practice_ids="", user_ids=""):
    monkeypatch.setattr(appointments_router.settings, "bernie_staff_pilot_enabled", enabled)
    monkeypatch.setattr(appointments_router.settings, "bernie_staff_pilot_practice_ids", practice_ids)
    monkeypatch.setattr(appointments_router.settings, "bernie_staff_pilot_user_ids", user_ids)


def test_pilot_eligibility_requires_auth(client):
    resp = _get(client)

    assert resp.status_code == 401


def test_pilot_eligibility_defaults_off_even_when_allowlisted(client, gp_user, monkeypatch):
    _set_gate(
        monkeypatch,
        enabled=False,
        practice_ids=str(gp_user.practice_id),
        user_ids=str(gp_user.id),
    )
    resp = _get(client, make_token(gp_user))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data == {
        "surface": "bernie_staff_review",
        "enabled": False,
        "eligible": False,
        "reason": "pilot_disabled",
        "practice_allowed": True,
        "user_allowed": True,
    }


def test_enabled_without_allowlist_fails_closed(client, gp_user, monkeypatch):
    _set_gate(monkeypatch, enabled=True)
    resp = _get(client, make_token(gp_user))

    assert resp.status_code == 200, resp.text
    assert resp.json() == {
        "surface": "bernie_staff_review",
        "enabled": True,
        "eligible": False,
        "reason": "no_allowlist_match",
        "practice_allowed": False,
        "user_allowed": False,
    }


def test_practice_allowlist_enables_only_matching_practice(
    client,
    gp_user,
    gp_user_b,
    monkeypatch,
):
    _set_gate(monkeypatch, enabled=True, practice_ids=str(gp_user.practice_id))

    allowed = _get(client, make_token(gp_user)).json()
    blocked = _get(client, make_token(gp_user_b)).json()

    assert allowed["eligible"] is True
    assert allowed["reason"] == "allowlist_match"
    assert allowed["practice_allowed"] is True
    assert allowed["user_allowed"] is False
    assert blocked["eligible"] is False
    assert blocked["reason"] == "no_allowlist_match"
    assert blocked["practice_allowed"] is False
    assert blocked["user_allowed"] is False


def test_user_allowlist_enables_only_matching_user(client, gp_user, gp_user_b, monkeypatch):
    _set_gate(monkeypatch, enabled=True, user_ids=str(gp_user.id))

    allowed = _get(client, make_token(gp_user)).json()
    blocked = _get(client, make_token(gp_user_b)).json()

    assert allowed["eligible"] is True
    assert allowed["reason"] == "allowlist_match"
    assert allowed["practice_allowed"] is False
    assert allowed["user_allowed"] is True
    assert blocked["eligible"] is False
    assert blocked["reason"] == "no_allowlist_match"
    assert blocked["practice_allowed"] is False
    assert blocked["user_allowed"] is False


def test_malformed_allowlists_are_ignored_and_fail_closed(client, gp_user, monkeypatch):
    _set_gate(
        monkeypatch,
        enabled=True,
        practice_ids="not-a-uuid,also-not-a-uuid",
        user_ids="bad-user-id",
    )
    resp = _get(client, make_token(gp_user))

    assert resp.status_code == 200, resp.text
    assert resp.json()["eligible"] is False
    assert resp.json()["reason"] == "no_allowlist_match"


def test_pilot_eligibility_route_writes_no_appointments_or_audits(
    client,
    db,
    gp_user,
    monkeypatch,
):
    _set_gate(monkeypatch, enabled=True, practice_ids=str(gp_user.practice_id))
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _get(client, make_token(gp_user))

    assert resp.status_code == 200, resp.text
    db.expire_all()
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_pilot_eligibility_source_has_no_provider_or_mutation_calls():
    route_source = inspect.getsource(appointments_router.get_bernie_pilot_eligibility)
    service_source = inspect.getsource(bernie_pilot_gate)
    source = f"{route_source}\n{service_source}"

    for forbidden in [
        "google.genai",
        "google.generativeai",
        "vertexai",
        "openai",
        "anthropic",
        "generate_content",
        "Gemini",
        "AiService",
        "_get_default_provider",
        "_build_slot_search_proposal",
        "confirm_bernie_create_proposal",
        "_create_appointment_from_body",
        "_write_audit",
        "db.add",
        "db.commit",
    ]:
        assert forbidden not in source, f"Forbidden call/import found: {forbidden!r}"
