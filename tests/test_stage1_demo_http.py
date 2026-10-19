"""Authored source-only bridge cases. No app, browser or DB execution here."""

from datetime import datetime, timedelta, timezone
from copy import deepcopy
from dataclasses import replace
import asyncio
import io
from pathlib import Path
import threading
import wave

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import pytest

import stage1_demo_http as bridge
from stage1_demo_http import DemoConfig, DemoSeed, create_stage1_demo_app
from stage1_demo_voice import VoiceRuntimeBinding, MAX_WAV_BYTES


REQ_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
REQ_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
APPT_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
PRACTICE_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
PATIENT_ID = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
PRACTITIONER_ID = "ffffffff-ffff-4fff-8fff-ffffffffffff"
OTHER_PRACTITIONER_ID = "44444444-4444-4444-8444-444444444444"
TYPE_ID = "11111111-1111-4111-8111-111111111111"
LOCATION_ID = "22222222-2222-4222-8222-222222222222"
STAFF_ID = "33333333-3333-4333-8333-333333333333"


@pytest.fixture
def bridge_case():
    backend = FastAPI()
    calls = []
    rows = {REQ_A: {"request_id": REQ_A, "patient_id": PATIENT_ID,
                       "state": "submitted", "request_version": 2,
                       "preference_date": "2026-10-15", "earliest_local": "14:00", "latest_local": "17:00",
                       "practice_timezone": "Australia/Brisbane", "booked_appointment_id": None},
            REQ_B: {"request_id": REQ_B, "patient_id": PATIENT_ID,
                       "state": "draft", "request_version": 1,
                       "preference_date": None, "earliest_local": None, "latest_local": None,
                       "practice_timezone": "Australia/Brisbane", "booked_appointment_id": None}}
    appointment = {"id": APPT_ID, "practice_id": PRACTICE_ID, "patient_id": PATIENT_ID,
                   "practitioner_id": PRACTITIONER_ID, "appointment_type_id": TYPE_ID, "location_id": LOCATION_ID,
                   "patient": {"id": PATIENT_ID, "first_name": "Alex", "last_name": "Chen",
                               "date_of_birth": "1990-01-01"},
                   "practitioner": {"id": PRACTITIONER_ID, "first_name": "Dr", "last_name": "Rao"},
                   "appointment_type": {"id": TYPE_ID, "name": "Follow-up",
                                        "default_duration": 15, "is_bookable_online": False},
                   "appointment_date": "2026-10-15", "start_time_local": "14:00:00",
                   "start_time": "2026-10-15T04:00:00+00:00", "end_time": "2026-10-15T04:15:00+00:00",
                   "created_at": "2026-10-12T00:01:00+00:00", "booked_via": "Receptionist",
                   "status": "Booked", "appointment_state_version": 1, "duration_minutes": 15}
    first_503 = {"enabled": False, "staff_active": True, "receipt_mode": "valid",
                  "move_lost": False, "move_calls": [], "move_raise": False, "move_effects": 0,
                  "create_raise": False, "create_effects": 0,
                  "submit_raise": False, "submit_replay_fail_once": False,
                  "submit_receipt_mode": "valid",
                  "submit_calls": [], "submit_effects": 0, "submit_receipt": None,
                  "patient_read_failures": 0, "validation_status": None}

    @backend.get("/api/v1/appointments/patient-requests/{request_id}")
    async def patient(request_id: str, x_patient_request_capability: str = Header()):
        if x_patient_request_capability != {REQ_A: "cap-a", REQ_B: "cap-b"}.get(request_id):
            raise HTTPException(404)
        if first_503["patient_read_failures"]:
            first_503["patient_read_failures"] -= 1
            raise HTTPException(503)
        return rows[request_id]

    @backend.post("/api/v1/appointments/patient-requests/{request_id}/submit")
    async def submit(request_id: str, request: Request, idempotency_key: str = Header(),
                     x_patient_request_capability: str = Header()):
        if request_id != REQ_B or x_patient_request_capability != "cap-b":
            raise HTTPException(403)
        body = await request.json()
        if first_503["validation_status"] is not None:
            raise HTTPException(first_503["validation_status"], detail="private backend detail")
        first_503["submit_calls"].append((idempotency_key, body))
        if first_503["submit_replay_fail_once"] and len(first_503["submit_calls"]) == 2:
            raise RuntimeError("reply unavailable after prior commit")
        if first_503["submit_receipt"] is None:
            if rows[request_id]["state"] != "draft" or body["request_version"] != rows[request_id]["request_version"]:
                raise HTTPException(409)
            rows[request_id].update({"state": "submitted", "request_version": body["request_version"] + 1,
                "preference_date": body["date"], "earliest_local": body["earliest_local"] + ":00",
                "latest_local": body["latest_local"] + ":00"})
            first_503["submit_effects"] += 1
            first_503["submit_receipt"] = {"request_id": request_id, "state": "submitted",
                "request_version": rows[request_id]["request_version"],
                "message": "Request received for staff review."}
            if first_503["submit_raise"]:
                raise RuntimeError("reply unavailable after commit")
        if first_503["submit_calls"][0] != (idempotency_key, body):
            raise HTTPException(409)
        receipt = dict(first_503["submit_receipt"])
        if first_503["submit_receipt_mode"] == "wrong_version":
            receipt["request_version"] += 1
        return receipt

    @backend.get("/api/v1/appointments/staff/patient-requests/{request_id}")
    async def staff(request_id: str, authorization: str = Header()):
        if authorization != "Bearer staff-token" or not first_503["staff_active"]:
            raise HTTPException(403)
        return rows[request_id]

    @backend.get("/api/v1/appointments/patient-requests/{request_id}/options")
    async def options(request_id: str, request_version: int, x_patient_request_capability: str = Header()):
        if (request_version != rows[request_id]["request_version"] or
                x_patient_request_capability != {REQ_A: "cap-a", REQ_B: "cap-b"}.get(request_id)):
            raise HTTPException(409)
        return [{"date": "2026-10-15", "local_time": "14:00", "zone": "Australia/Brisbane"}]

    @backend.get("/api/v1/appointments/{appointment_id}")
    async def read_appointment(appointment_id: str, authorization: str = Header()):
        if authorization != "Bearer staff-token" or not first_503["staff_active"] or appointment_id != appointment["id"]:
            raise HTTPException(403)
        return appointment

    @backend.post("/api/v1/appointments/staff/patient-requests/{request_id}/proposals/create")
    async def proposal(request_id: str, request: Request, authorization: str = Header()):
        if authorization != "Bearer staff-token" or not first_503["staff_active"] or request_id != REQ_A:
            raise HTTPException(403)
        body = await request.json()
        if body["request_version"] != rows[request_id]["request_version"]:
            raise HTTPException(409)
        return {"safe": True, "confirm_payload": {"confirmed": False, "signed_confirmation_evidence": {"source": "backend"}}}

    @backend.post("/api/v1/appointments/proposals/create/confirm")
    async def confirm(request: Request, idempotency_key: str = Header(), authorization: str = Header()):
        if authorization != "Bearer staff-token" or not first_503["staff_active"]:
            raise HTTPException(403)
        body = await request.json()
        calls.append((idempotency_key, body))
        if first_503["enabled"] and len(calls) == 1:
            return JSONResponse({"error": "reply lost"}, status_code=503)
        if not body["confirmed"] or body["signed_confirmation_evidence"] != {"source": "backend"}:
            raise HTTPException(409)
        if rows[REQ_A]["state"] != "booked":
            rows[REQ_A]["state"] = "booked"
            rows[REQ_A]["booked_appointment_id"] = APPT_ID
            first_503["create_effects"] += 1
        receipt = {
            "schema_version": "appointment.confirmation_receipt.v1", "outcome": "appointment_created",
            "appointment_id": APPT_ID, "patient_display": "Alex Chen",
            "practitioner_display": "Dr Rao", "appointment_date": appointment["appointment_date"],
            "start_time_local": appointment["start_time_local"], "duration_minutes": 15,
            "status": "Booked", "appointment_type": "Follow-up",
            "confirmed_by_display": "Reception One", "confirmed_by_role": "Receptionist",
            "correlation_id": "11111111-1111-4111-8111-111111111111",
            "audit_event_id": "22222222-2222-4222-8222-222222222222",
            "verification": {"actor_authenticated": True, "practice_scope_verified": True,
                "proposal_revalidated": True, "conflict_check_passed": True,
                "idempotency_verified": True, "audit_recorded": True,
                "signed_evidence_verified": True, "visual_diary_check_required": False},
        }
        if first_503["receipt_mode"] == "missing": receipt = None
        elif first_503["receipt_mode"] == "wrong_time": receipt["start_time_local"] = "15:00:00"
        if first_503["create_raise"] and len(calls) == 1:
            raise RuntimeError("reply unavailable after commit")
        return {"safe": True, "appointment": appointment, "confirmation_receipt": receipt}

    @backend.post("/api/v1/appointments/proposals/move-time/{appointment_id}")
    async def move_proposal(appointment_id: str, request: Request, authorization: str = Header()):
        if authorization != "Bearer staff-token" or not first_503["staff_active"]:
            raise HTTPException(403)
        body = await request.json()
        if appointment_id != appointment["id"] or body["source_state_version"] != appointment["appointment_state_version"]:
            raise HTTPException(409)
        return {"safe": True, "confirm_payload": {"confirmed": False,
            "signed_confirmation_evidence": {"source": "backend-move"}}}

    @backend.post("/api/v1/appointments/proposals/update/confirm")
    async def move_confirm(request: Request, idempotency_key: str = Header(), authorization: str = Header()):
        if authorization != "Bearer staff-token" or not first_503["staff_active"]:
            raise HTTPException(403)
        body = await request.json()
        first_503["move_calls"].append((idempotency_key, body))
        if first_503["move_lost"] and len(first_503["move_calls"]) == 1:
            return JSONResponse({"error": "reply lost"}, status_code=503)
        if first_503["move_raise"] and first_503["move_effects"] == 0:
            appointment["start_time_local"] = "15:00:00"
            appointment["appointment_state_version"] = 2
            first_503["move_effects"] += 1
            raise RuntimeError("reply unavailable after commit")
        result = {**appointment, "start_time_local": "15:00:00"}
        return {"safe": True, "appointment": result}

    config = DemoConfig(profile="STAGE1_SYNTHETIC_DEMO", environment="dev",
        listener_origin="http://127.0.0.1:8765", backend_app=backend,
        practice_id=PRACTICE_ID, patient_id=PATIENT_ID, patient_label="Alex Chen",
        practitioner_id=PRACTITIONER_ID, practitioner_label="Dr Rao",
        appointment_type_id=TYPE_ID, appointment_type_label="Follow-up",
        location_id=LOCATION_ID, location_label="Fictional practice",
        timezone="Australia/Brisbane",
        demo_clock="2026-10-12 10:01", seeds=(
            DemoSeed(persona="patient", request_id=REQ_A, patient_capability="cap-a"),
            DemoSeed(persona="patient", request_id=REQ_B, patient_capability="cap-b"),
            DemoSeed(persona="staff", request_id=REQ_A, staff_bearer="staff-token",
                     staff_user_id=STAFF_ID, seeded_appointment_id=APPT_ID)),
        request_capabilities={REQ_A: "cap-a", REQ_B: "cap-b"})
    app, issuer = create_stage1_demo_app(config)
    return app, issuer, config, rows, appointment, calls, first_503


def _cookie(issuer, persona, request_id):
    return dict([issuer.cookie_for(persona, request_id)])


async def _action(client, issuer, persona, request_id, action, body=None, key=None, csrf=None, origin="http://127.0.0.1:8765"):
    cookie = _cookie(issuer, persona, request_id)
    session = await client.get("/demo/stage1/session", cookies=cookie)
    assert session.status_code == 200
    headers = {"Origin": origin, "X-CSRF-Token": csrf or session.json()["csrf"]}
    return await client.post("/demo/stage1/action", cookies=cookie, headers=headers,
        json={"method": "read" if action in {"refresh", "reconcile", "propose_create", "propose_move"} else "write",
              "action": action, "body": body, "idempotency_key": key})


@pytest.mark.anyio
async def test_two_alex_scopes_are_isolated_and_patient_cannot_use_staff_action(bridge_case):
    app, issuer, *_ = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53100)), base_url="http://127.0.0.1:8765") as client:
        a = await _action(client, issuer, "patient", REQ_A, "refresh")
        b = await _action(client, issuer, "patient", REQ_B, "refresh")
        assert a.json()["request"]["request_id"] == REQ_A
        assert b.json()["request"]["request_id"] == REQ_B
        denied = await _action(client, issuer, "patient", REQ_B, "confirm_move",
            {"proposal_ref": "x"}, key="12345678")
        assert denied.status_code == 403


@pytest.mark.anyio
async def test_origin_csrf_and_current_staff_authority_are_required(bridge_case):
    app, issuer, _, _, _, _, control = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53101)), base_url="http://127.0.0.1:8765") as client:
        assert (await _action(client, issuer, "staff", REQ_A, "refresh", origin="http://evil.test")).status_code == 403
        assert (await _action(client, issuer, "staff", REQ_A, "refresh", csrf="wrong")).status_code == 403
        staff = await _action(client, issuer, "staff", REQ_A, "refresh")
        assert staff.status_code == 200 and staff.json()["appointment"]["ref"] == APPT_ID
        control["staff_active"] = False
        assert (await _action(client, issuer, "staff", REQ_A, "refresh")).status_code == 403


@pytest.mark.anyio
async def test_stale_proposal_and_uncertain_replay_keep_original_key(bridge_case):
    app, issuer, _, _, _, calls, first_503 = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53102)), base_url="http://127.0.0.1:8765") as client:
        selected = {"date": "2026-10-15", "local_time": "14:00", "zone": "Australia/Brisbane"}
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_create",
            {"request_version": 2, "selected": selected})
        assert proposed.status_code == 200
        ref = proposed.json()["proposal_ref"]
        token = issuer.cookie_for("staff", REQ_A)[1]
        issuer._sessions[token].proposal["expires"] = datetime.now(timezone.utc) - timedelta(seconds=1)
        stale = await _action(client, issuer, "staff", REQ_A, "confirm_create",
            {"proposal_ref": ref}, key="12345678")
        assert stale.status_code == 409 and calls == []
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_create",
            {"request_version": 2, "selected": selected})
        first_503["enabled"] = True
        lost = await _action(client, issuer, "staff", REQ_A, "confirm_create",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="87654321")
        assert lost.status_code == 503
        reconciled = await _action(client, issuer, "staff", REQ_A, "reconcile")
        assert reconciled.status_code == 200 and reconciled.json()["uncertain"] is False
        assert [item[0] for item in calls] == ["87654321", "87654321"]
        assert calls[0][1] == calls[1][1]


@pytest.mark.anyio
async def test_revoked_staff_confirmation_is_definitive_not_uncertain(bridge_case):
    app, issuer, _, _, _, calls, control = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53103)), base_url="http://127.0.0.1:8765") as client:
        selected = {"date": "2026-10-15", "local_time": "14:00", "zone": "Australia/Brisbane"}
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_create",
            {"request_version": 2, "selected": selected})
        control["staff_active"] = False
        denied = await _action(client, issuer, "staff", REQ_A, "confirm_create",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="aabbccdd-1234")
        assert denied.status_code == 403
        assert denied.json()["detail"] == "BACKEND_ACCESS_DENIED"
        assert issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain is None
        assert calls == []
        assert control["create_effects"] == 0


@pytest.mark.anyio
@pytest.mark.parametrize("receipt_mode", ["missing", "wrong_time"])
async def test_create_never_claims_committed_without_matching_typed_receipt(bridge_case, receipt_mode):
    app, issuer, _, _, _, calls, control = bridge_case
    control["receipt_mode"] = receipt_mode
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53104)), base_url="http://127.0.0.1:8765") as client:
        selected = {"date": "2026-10-15", "local_time": "14:00", "zone": "Australia/Brisbane"}
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_create",
            {"request_version": 2, "selected": selected})
        rejected = await _action(client, issuer, "staff", REQ_A, "confirm_create",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="eeffccdd-1234")
        assert rejected.status_code == 409
        assert issuer._initial_booking == {}
        pending = issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain
        assert pending["family"] == "create" and pending["key"] == "eeffccdd-1234"
        assert pending["payload"] == calls[0][1]
        checked = await _action(client, issuer, "staff", REQ_A, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is True
        assert [item[0] for item in calls] == ["eeffccdd-1234", "eeffccdd-1234"]
        assert calls[0][1] == calls[1][1] == pending["payload"]
        assert issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain == pending
        assert issuer._initial_booking == {}


@pytest.mark.anyio
async def test_same_patient_different_practitioner_is_not_labelled_dr_rao(bridge_case):
    app, issuer, _, rows, appointment, _, _ = bridge_case
    rows[REQ_A]["state"] = "booked"
    rows[REQ_A]["booked_appointment_id"] = APPT_ID
    appointment["practitioner_id"] = OTHER_PRACTITIONER_ID
    appointment["practitioner"] = {"id": OTHER_PRACTITIONER_ID,
                                   "first_name": "Dr", "last_name": "Singh"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53105)), base_url="http://127.0.0.1:8765") as client:
        response = await _action(client, issuer, "staff", REQ_A, "refresh")
        assert response.status_code == 409


@pytest.mark.anyio
async def test_move_replay_matching_id_but_different_current_time_stays_uncertain(bridge_case):
    app, issuer, _, _, appointment, _, control = bridge_case
    control["move_lost"] = True
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53106)), base_url="http://127.0.0.1:8765") as client:
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_move",
            {"appointment_ref": APPT_ID, "source_state_version": 1,
             "target_date": "2026-10-15", "target_start_local": "15:00"})
        assert proposed.status_code == 200
        lost = await _action(client, issuer, "staff", REQ_A, "confirm_move",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="1122aabb-1234")
        assert lost.status_code == 503
        reconciled = await _action(client, issuer, "staff", REQ_A, "reconcile")
        assert reconciled.status_code == 200 and reconciled.json()["uncertain"] is True
        assert appointment["start_time_local"] == "14:00:00"
        assert [item[0] for item in control["move_calls"]] == ["1122aabb-1234", "1122aabb-1234"]


@pytest.mark.anyio
async def test_positive_move_response_with_wrong_readback_keeps_original_action(bridge_case):
    app, issuer, _, _, appointment, _, control = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53107)), base_url="http://127.0.0.1:8765") as client:
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_move",
            {"appointment_ref": APPT_ID, "source_state_version": 1,
             "target_date": "2026-10-15", "target_start_local": "15:00"})
        assert proposed.status_code == 200
        rejected = await _action(client, issuer, "staff", REQ_A, "confirm_move",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="7788ccdd-1234")
        assert rejected.status_code == 409
        pending = issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain
        assert pending["family"] == "move" and pending["appointment_id"] == APPT_ID
        assert pending["key"] == "7788ccdd-1234"
        assert pending["payload"] == control["move_calls"][0][1]
        checked = await _action(client, issuer, "staff", REQ_A, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is True
        assert appointment["start_time_local"] == "14:00:00"
        assert [item[0] for item in control["move_calls"]] == ["7788ccdd-1234", "7788ccdd-1234"]
        assert control["move_calls"][0][1] == control["move_calls"][1][1] == pending["payload"]
        assert issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain == pending


SUBMISSION = {"date": "2026-10-15", "earliest_local": "14:00", "latest_local": "17:00",
              "request_version": 1, "reason_code": "follow_up"}


@pytest.mark.anyio
async def test_patient_positive_submit_then_failed_read_reconciles_original_key(bridge_case):
    app, issuer, _, rows, _, _, control = bridge_case
    control["patient_read_failures"] = 1
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53108)), base_url="http://127.0.0.1:8765") as client:
        first = await _action(client, issuer, "patient", REQ_B, "submit_request",
            SUBMISSION, key="aabbccdd-3344")
        assert first.status_code == 503
        assert rows[REQ_B]["state"] == "submitted" and control["submit_effects"] == 1
        pending = issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain
        assert pending["key"] == "aabbccdd-3344"
        assert pending["payload"]["request_id"] == REQ_B
        assert pending["payload"] == control["submit_calls"][0][1]
        checked = await _action(client, issuer, "patient", REQ_B, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is False
        assert checked.json()["request"]["state"] == "submitted"
        assert [entry[0] for entry in control["submit_calls"]] == ["aabbccdd-3344", "aabbccdd-3344"]
        assert control["submit_calls"][0][1] == control["submit_calls"][1][1]
        assert control["submit_effects"] == 1


@pytest.mark.anyio
async def test_patient_wrong_receipt_stays_pending_through_reconcile(bridge_case):
    app, issuer, _, _, _, _, control = bridge_case
    control["submit_receipt_mode"] = "wrong_version"
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53113)), base_url="http://127.0.0.1:8765") as client:
        first = await _action(client, issuer, "patient", REQ_B, "submit_request",
            SUBMISSION, key="aabbccdd-ddee")
        assert first.status_code == 409
        pending = issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain
        assert pending["key"] == "aabbccdd-ddee"
        checked = await _action(client, issuer, "patient", REQ_B, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is True
        assert issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain == pending
        assert [entry[0] for entry in control["submit_calls"]] == ["aabbccdd-ddee"] * 2
        assert all(entry[1] == pending["payload"] for entry in control["submit_calls"])
        assert control["submit_effects"] == 1


@pytest.mark.anyio
async def test_patient_read_and_replay_failures_keep_pending_original_action(bridge_case):
    app, issuer, _, _, _, _, control = bridge_case
    control["patient_read_failures"] = 2
    control["submit_replay_fail_once"] = True
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53109)), base_url="http://127.0.0.1:8765") as client:
        first = await _action(client, issuer, "patient", REQ_B, "submit_request",
            SUBMISSION, key="aabbccdd-5566")
        assert first.status_code == 503
        pending = issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain
        replay_failure = await _action(client, issuer, "patient", REQ_B, "reconcile")
        assert replay_failure.status_code == 503
        assert issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain == pending
        read_failure = await _action(client, issuer, "patient", REQ_B, "reconcile")
        assert read_failure.status_code == 200 and read_failure.json()["uncertain"] is True
        assert issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain == pending
        verified = await _action(client, issuer, "patient", REQ_B, "reconcile")
        assert verified.status_code == 200 and verified.json()["uncertain"] is False
        assert [entry[0] for entry in control["submit_calls"]] == ["aabbccdd-5566"] * 4
        assert all(entry[1] == pending["payload"] for entry in control["submit_calls"])
        assert control["submit_effects"] == 1


@pytest.mark.anyio
async def test_submit_commit_then_backend_exception_replays_one_effect(bridge_case):
    app, issuer, _, _, _, _, control = bridge_case
    control["submit_raise"] = True
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53110)), base_url="http://127.0.0.1:8765") as client:
        first = await _action(client, issuer, "patient", REQ_B, "submit_request",
            SUBMISSION, key="aabbccdd-7788")
        assert first.status_code == 503 and control["submit_effects"] == 1
        pending = issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain
        assert pending["key"] == "aabbccdd-7788"
        checked = await _action(client, issuer, "patient", REQ_B, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is False
        assert control["submit_effects"] == 1
        assert [entry[0] for entry in control["submit_calls"]] == ["aabbccdd-7788"] * 2
        assert all(entry[1] == pending["payload"] for entry in control["submit_calls"])


@pytest.mark.anyio
async def test_create_commit_then_backend_exception_replays_one_effect(bridge_case):
    app, issuer, _, _, _, calls, control = bridge_case
    control["create_raise"] = True
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53111)), base_url="http://127.0.0.1:8765") as client:
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_create",
            {"request_version": 2, "selected":
             {"date": "2026-10-15", "local_time": "14:00", "zone": "Australia/Brisbane"}})
        first = await _action(client, issuer, "staff", REQ_A, "confirm_create",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="aabbccdd-99aa")
        assert first.status_code == 503 and control["create_effects"] == 1
        pending = issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain
        assert pending["key"] == "aabbccdd-99aa"
        checked = await _action(client, issuer, "staff", REQ_A, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is False
        assert control["create_effects"] == 1
        assert [entry[0] for entry in calls] == ["aabbccdd-99aa"] * 2
        assert all(entry[1] == pending["payload"] for entry in calls)


@pytest.mark.anyio
async def test_move_commit_then_backend_exception_replays_one_effect(bridge_case):
    app, issuer, _, _, appointment, _, control = bridge_case
    control["move_raise"] = True
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53112)), base_url="http://127.0.0.1:8765") as client:
        proposed = await _action(client, issuer, "staff", REQ_A, "propose_move",
            {"appointment_ref": APPT_ID, "source_state_version": 1,
             "target_date": "2026-10-15", "target_start_local": "15:00"})
        first = await _action(client, issuer, "staff", REQ_A, "confirm_move",
            {"proposal_ref": proposed.json()["proposal_ref"]}, key="aabbccdd-bbcc")
        assert first.status_code == 503 and control["move_effects"] == 1
        pending = issuer._sessions[issuer.cookie_for("staff", REQ_A)[1]].uncertain
        assert pending["key"] == "aabbccdd-bbcc"
        checked = await _action(client, issuer, "staff", REQ_A, "reconcile")
        assert checked.status_code == 200 and checked.json()["uncertain"] is False
        assert appointment["start_time_local"] == "15:00:00"
        assert control["move_effects"] == 1
        assert [entry[0] for entry in control["move_calls"]] == ["aabbccdd-bbcc"] * 2
        assert all(entry[1] == pending["payload"] for entry in control["move_calls"])


@pytest.mark.anyio
async def test_backend_validation_status_is_distinct_and_sanitized(bridge_case):
    app, issuer, _, _, _, _, control = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53114)), base_url="http://127.0.0.1:8765") as client:
        for code in (400, 422):
            control["validation_status"] = code
            result = await _action(client, issuer, "patient", REQ_B, "submit_request",
                SUBMISSION, key="aabbccdd-9911")
            assert result.status_code == code
            assert result.json()["detail"] == "BACKEND_VALIDATION_INVALID"
            assert "private" not in result.text
            assert issuer._sessions[issuer.cookie_for("patient", REQ_B)[1]].uncertain is None
        control["validation_status"] = 409
        conflict = await _action(client, issuer, "patient", REQ_B, "submit_request",
            SUBMISSION, key="aabbccdd-9911")
        assert conflict.status_code == 409
        assert conflict.json()["detail"] == "BACKEND_STATE_CHANGED"


def _wav_bytes() -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b"\x00\x00" * 160)
    return out.getvalue()


@pytest.mark.anyio
async def test_precheck_rejections_preserve_voice_nonce_and_concurrent_replay_is_blocked(
        bridge_case, monkeypatch):
    _, _, config, *_ = bridge_case
    binding = VoiceRuntimeBinding(Path("unused"), Path("unused"), Path("unused"),
        Path("unused"), "unused", "unused", "unused")
    monkeypatch.setattr(VoiceRuntimeBinding, "ready", lambda self: True)
    calls = []
    def recognize(raw, selected):
        calls.append(raw)
        return "Thursday 2026-10-15 at 14:30"
    monkeypatch.setattr(bridge, "run_local_recognizer", recognize)
    app, issuer = create_stage1_demo_app(replace(config, voice_runtime=binding))
    cookie = _cookie(issuer, "patient", REQ_B)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53115)), base_url="http://127.0.0.1:8765") as client:
        session = (await client.get("/demo/stage1/session", cookies=cookie)).json()
        nonce = session["voice_nonce"]
        headers = {"Origin": config.listener_origin, "Content-Type": "audio/wav",
            "X-CSRF-Token": session["csrf"], "X-Voice-Target": "patient-words",
            "X-Voice-Nonce": nonce}
        oversized = await client.post("/demo/stage1/voice", cookies=cookie,
            headers=headers, content=b"x" * (MAX_WAV_BYTES + 1))
        malformed = await client.post("/demo/stage1/voice", cookies=cookie,
            headers=headers, content=b"bad wav")
        assert oversized.status_code == 413 and malformed.status_code == 400
        assert (await client.get("/demo/stage1/session", cookies=cookie)).json()["voice_nonce"] == nonce
        valid = _wav_bytes()
        first, second = await asyncio.gather(*(
            client.post("/demo/stage1/voice", cookies=cookie, headers=headers, content=valid)
            for _ in range(2)))
        assert sorted((first.status_code, second.status_code))[0] == 200
        assert sorted((first.status_code, second.status_code))[1] in {403, 409, 429}
        assert len(calls) == 1
        assert (await client.get("/demo/stage1/session", cookies=cookie)).json()["voice_nonce"] != nonce


@pytest.mark.anyio
async def test_busy_precheck_leaves_other_persona_nonce_usable(bridge_case, monkeypatch):
    _, _, config, *_ = bridge_case
    binding = VoiceRuntimeBinding(Path("unused"), Path("unused"), Path("unused"),
        Path("unused"), "unused", "unused", "unused")
    monkeypatch.setattr(VoiceRuntimeBinding, "ready", lambda self: True)
    started, release = threading.Event(), threading.Event()
    calls = []
    def recognize(raw, selected):
        calls.append(raw)
        if len(calls) == 1:
            started.set()
            assert release.wait(2)
        return "Thursday at 14:30"
    monkeypatch.setattr(bridge, "run_local_recognizer", recognize)
    app, issuer = create_stage1_demo_app(replace(config, voice_runtime=binding))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53117)), base_url=config.listener_origin) as client:
        patient_cookie = _cookie(issuer, "patient", REQ_B)
        staff_cookie = _cookie(issuer, "staff", REQ_A)
        patient = (await client.get("/demo/stage1/session", cookies=patient_cookie)).json()
        staff = (await client.get("/demo/stage1/session", cookies=staff_cookie)).json()
        def headers(session, target):
            return {"Origin": config.listener_origin, "Content-Type": "audio/wav",
                "X-CSRF-Token": session["csrf"], "X-Voice-Target": target,
                "X-Voice-Nonce": session["voice_nonce"]}
        first = asyncio.create_task(client.post("/demo/stage1/voice", cookies=patient_cookie,
            headers=headers(patient, "patient-words"), content=_wav_bytes()))
        try:
            assert await asyncio.to_thread(started.wait, 1)
            busy = await client.post("/demo/stage1/voice", cookies=staff_cookie,
                headers=headers(staff, "move-words"), content=_wav_bytes())
            assert busy.status_code == 429
            assert (await client.get("/demo/stage1/session", cookies=staff_cookie)).json()["voice_nonce"] == staff["voice_nonce"]
        finally:
            release.set()
        assert (await first).status_code == 200
        retry = await client.post("/demo/stage1/voice", cookies=staff_cookie,
            headers=headers(staff, "move-words"), content=_wav_bytes())
        assert retry.status_code == 200 and len(calls) == 2


@pytest.mark.anyio
@pytest.mark.parametrize("persona,request_id,kind,words,expected", [
    ("patient", REQ_B, "request", "Follow-up next Thursday between 2 pm and 4 pm.",
     {"date": "2026-10-15", "earliest_local": "14:00", "latest_local": "16:00"}),
    ("staff", REQ_A, "move", "Move this appointment next Thursday at 3 pm.",
     {"target_date": "2026-10-15", "target_start_local": "15:00"}),
])
async def test_visible_note_examples_reach_real_local_interpretation_route(
        bridge_case, persona, request_id, kind, words, expected):
    app, issuer, config, rows, appointment, _, control = bridge_case
    before_rows = deepcopy(rows)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53118)), base_url=config.listener_origin) as client:
        cookie = _cookie(issuer, persona, request_id)
        session = (await client.get("/demo/stage1/session", cookies=cookie)).json()
        result = await client.post("/demo/stage1/interpret", cookies=cookie,
            headers={"Origin": config.listener_origin, "X-CSRF-Token": session["csrf"]},
            json={"kind": kind, "words": words})
        assert result.status_code == 200
        assert result.headers["cache-control"] == "no-store"
        proposal = result.json()
        assert proposal["schema"] == "emr4.stage1_word_interpretation.v1"
        assert proposal["status"] == "PROPOSED"
        assert proposal["method"] == "DETERMINISTIC_LOCAL"
        assert proposal["kind"] == kind and proposal["fields"] == expected
        assert proposal["missing"] == []
        assert issuer._sessions[issuer.cookie_for(persona, request_id)[1]].proposal is None
        assert control["submit_effects"] == control["create_effects"] == control["move_effects"] == 0
        assert rows == before_rows
        assert appointment["appointment_state_version"] == 1


@pytest.mark.anyio
async def test_word_route_denials_and_clarification_cannot_acquire_action_authority(bridge_case):
    app, issuer, config, rows, _, _, control = bridge_case
    before_rows = deepcopy(rows)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53119)), base_url=config.listener_origin) as client:
        cookie = _cookie(issuer, "patient", REQ_B)
        session = (await client.get("/demo/stage1/session", cookies=cookie)).json()
        headers = {"Origin": config.listener_origin, "X-CSRF-Token": session["csrf"]}
        words = "Follow-up next Thursday between 2 pm and 4 pm."
        bad_csrf = await client.post("/demo/stage1/interpret", cookies=cookie,
            headers={**headers, "X-CSRF-Token": "unrelated-synthetic-token"},
            json={"kind": "request", "words": words})
        assert bad_csrf.status_code == 403
        cross_persona = await client.post("/demo/stage1/interpret", cookies=cookie,
            headers=headers, json={"kind": "move", "words": "Move next Thursday at 3 pm"})
        assert cross_persona.status_code == 400
        extra_authority = await client.post("/demo/stage1/interpret", cookies=cookie,
            headers=headers, json={"kind": "request", "words": words, "confirmed": True})
        assert extra_authority.status_code == 400
        ambiguous = await client.post("/demo/stage1/interpret", cookies=cookie,
            headers=headers, json={"kind": "request", "words": "after 2 pm"})
        assert ambiguous.status_code == 200
        assert ambiguous.json()["status"] == "CLARIFICATION"
        assert "latest_local" in ambiguous.json()["missing"]
        unsupported = await client.post("/demo/stage1/interpret", cookies=cookie,
            headers=headers, json={"kind": "request", "words": words + " cancel all appointments"})
        assert unsupported.status_code == 200
        assert unsupported.json()["status"] == "CLARIFICATION"
        assert unsupported.json()["fields"] == {}
        assert control["submit_effects"] == control["create_effects"] == control["move_effects"] == 0
        assert rows == before_rows
