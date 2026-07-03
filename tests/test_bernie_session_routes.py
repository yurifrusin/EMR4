import uuid

from tests.conftest import make_token


BASE = "/api/v1/appointments/bernie/sessions"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _surface() -> str:
    return f"diary-{uuid.uuid4().hex}"


def _active_session(client, token: str, surface_id: str, reference_date: str = "2026-07-03") -> dict:
    resp = client.get(
        f"{BASE}/active",
        params={"surface_id": surface_id, "reference_date": reference_date},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["session"]


def _append_event(client, token: str, session_id: str, body: dict):
    return client.post(f"{BASE}/{session_id}/events", json=body, headers=_auth(token))


def test_active_session_requires_auth(client):
    resp = client.get(f"{BASE}/active", params={"surface_id": _surface()})

    assert resp.status_code == 401


def test_active_session_is_auth_owned_and_reused(client, gp_user):
    token = make_token(gp_user)
    surface_id = _surface()

    first = _active_session(client, token, surface_id)
    second = _active_session(client, token, surface_id)

    assert first["session_id"] == second["session_id"]
    assert first["surface_id"] == surface_id
    assert first["state"] == "instruction_entry"
    assert first["revision"] == 0
    assert first["request_reference_date"] == "2026-07-03"
    assert "practice_id" not in first
    assert "user_id" not in first


def test_new_session_replaces_active_surface_session(client, gp_user):
    token = make_token(gp_user)
    surface_id = _surface()
    first = _active_session(client, token, surface_id)

    resp = client.post(
        f"{BASE}/new",
        json={"surface_id": surface_id, "reference_date": "2026-07-04"},
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    second = resp.json()["session"]
    assert second["session_id"] != first["session_id"]
    assert second["surface_id"] == surface_id
    assert second["request_reference_date"] == "2026-07-04"
    assert _active_session(client, token, surface_id, "2026-07-05")["session_id"] == second["session_id"]


def test_append_event_advances_revision_and_event_tail(client, gp_user):
    token = make_token(gp_user)
    surface_id = _surface()
    session = _active_session(client, token, surface_id)

    resp = _append_event(
        client,
        token,
        session["session_id"],
        {
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "event_id": "event-1",
            "payload": {"intent_ref": "intent-1"},
        },
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["accepted"] is True
    assert data["session"]["revision"] == 1
    assert data["session"]["state"] == "recognition"
    assert data["event"]["event_id"] == "event-1"
    assert data["event"]["payload"] == {"intent_ref": "intent-1"}


def test_stale_revision_returns_409_without_duplicate_append(client, gp_user):
    token = make_token(gp_user)
    surface_id = _surface()
    session = _active_session(client, token, surface_id)
    accepted = _append_event(
        client,
        token,
        session["session_id"],
        {
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "event_id": "event-1",
            "payload": {"intent_ref": "intent-1"},
        },
    )
    assert accepted.status_code == 200

    stale = _append_event(
        client,
        token,
        session["session_id"],
        {
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "event_id": "event-2",
            "payload": {"intent_ref": "intent-2"},
        },
    )

    assert stale.status_code == 409
    data = stale.json()
    assert data["accepted"] is False
    assert data["code"] == "stale_session_revision"
    current = _active_session(client, token, surface_id)
    assert current["revision"] == 1
    assert [event["event_id"] for event in current["events"]] == ["event-1"]


def test_idempotent_replay_is_safe_and_conflicting_replay_rejects(client, gp_user):
    token = make_token(gp_user)
    surface_id = _surface()
    session = _active_session(client, token, surface_id)
    body = {
        "surface_id": surface_id,
        "event_type": "staff_instruction",
        "expected_revision": 0,
        "event_id": "event-1",
        "idempotency_key": "idem-1",
        "payload": {"intent_ref": "intent-1"},
    }

    first = _append_event(client, token, session["session_id"], body)
    replay = _append_event(client, token, session["session_id"], body)
    changed = dict(body)
    changed["payload"] = {"intent_ref": "changed"}
    conflict = _append_event(client, token, session["session_id"], changed)

    assert first.status_code == 200
    assert replay.status_code == 200
    assert replay.json()["session"] == first.json()["session"]
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "idempotency_conflict"


def test_cross_user_and_wrong_surface_reject(client, gp_user, receptionist_user):
    token = make_token(gp_user)
    other_token = make_token(receptionist_user)
    surface_id = _surface()
    session = _active_session(client, token, surface_id)

    other_user = _append_event(
        client,
        other_token,
        session["session_id"],
        {
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "payload": {"intent_ref": "intent-1"},
        },
    )
    wrong_surface = _append_event(
        client,
        token,
        session["session_id"],
        {
            "surface_id": f"{surface_id}-other",
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "payload": {"intent_ref": "intent-1"},
        },
    )

    assert other_user.status_code == 409
    assert other_user.json()["code"] == "session_owner_mismatch"
    assert wrong_surface.status_code == 409
    assert wrong_surface.json()["code"] == "session_owner_mismatch"
    assert _active_session(client, token, surface_id)["revision"] == 0


def test_phi_payload_rejects(client, gp_user):
    token = make_token(gp_user)
    surface_id = _surface()
    session = _active_session(client, token, surface_id)

    resp = _append_event(
        client,
        token,
        session["session_id"],
        {
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "payload": {"raw_instruction": "Make an appointment for Margaret Thompson"},
        },
    )

    assert resp.status_code == 409
    assert resp.json()["code"] == "phi_payload_not_allowed"
    current = _active_session(client, token, surface_id)
    assert current["revision"] == 0
    assert current["events"] == []
