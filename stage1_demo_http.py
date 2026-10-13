"""Source-only standalone Stage 1 demo bridge; never include in production main.

The trusted isolated harness constructs this app with a pinned backend ASGI app,
fictional seeded request sessions and one real backend Receptionist bearer. It
sets a cookie out of band via `DemoIssuer.cookie_for`; there is deliberately no
public role/bootstrap endpoint. No application modules are imported here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
import asyncio
import re
import secrets
from typing import Any
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import httpx

from stage1_demo_adapter_core import AdapterRejected, MAX_BODY_BYTES, SessionBinding, admit_action
from stage1_demo_voice import (MAX_WAV_BYTES, VoiceInputRejected, VoiceRecognitionUnavailable,
                               VoiceRuntimeBinding, run_local_recognizer, target_for_persona,
                               validate_wav)


BASE = "/api/v1/appointments"
COOKIE = "stage1_demo_session"
STATIC = Path(__file__).parent / "static" / "demo"
LOCAL_MINUTE = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d(?::00(?:\.0+)?)?\Z")


def local_minute(value: Any) -> str | None:
    return value[:5] if isinstance(value, str) and LOCAL_MINUTE.fullmatch(value) else None


@dataclass(frozen=True, repr=False)
class DemoSeed:
    persona: str
    request_id: str
    patient_capability: str | None = None
    staff_bearer: str | None = None
    staff_user_id: str | None = None
    seeded_appointment_id: str | None = None


@dataclass(frozen=True, repr=False)
class DemoConfig:
    profile: str
    environment: str
    listener_origin: str
    backend_app: Any
    practice_id: str
    patient_id: str
    patient_label: str
    practitioner_id: str
    practitioner_label: str
    appointment_type_id: str
    appointment_type_label: str
    location_id: str | None
    location_label: str
    timezone: str
    demo_clock: str
    seeds: tuple[DemoSeed, ...]
    # Trusted server fixture map. Staff never receives a patient capability in
    # its own session; the bridge uses the exact request's separate seed.
    request_capabilities: dict[str, str] = field(repr=False)
    # None until actual local installation, model and execution evidence are
    # independently bound by the trusted isolated harness.
    voice_runtime: VoiceRuntimeBinding | None = field(default=None, repr=False)


@dataclass(repr=False)
class _Session:
    binding: SessionBinding
    staff_bearer: str | None
    seeded_appointment_id: str | None
    expires_at: datetime
    proposal: dict[str, Any] | None = None
    uncertain: dict[str, Any] | None = None
    voice_nonce: str = field(default_factory=lambda: secrets.token_urlsafe(24), repr=False)


class DemoIssuer:
    """Trusted harness handle, not an HTTP endpoint or client role selector."""

    def __init__(self, config: DemoConfig):
        if (config.profile != "STAGE1_SYNTHETIC_DEMO" or config.environment != "dev"
                or not config.listener_origin.startswith("http://127.0.0.1:")
                or not config.seeds or len(config.seeds) > 3):
            raise ValueError("DEMO_PROFILE_CLOSED")
        patient_seeds = [s for s in config.seeds if s.persona == "patient"]
        staff_seeds = [s for s in config.seeds if s.persona == "staff"]
        if (len(patient_seeds) != 2 or len(staff_seeds) != 1
                or patient_seeds[0].request_id == patient_seeds[1].request_id
                or any(not s.patient_capability or s.staff_bearer for s in patient_seeds)
                or any(not s.staff_bearer or not s.staff_user_id or s.patient_capability for s in staff_seeds)
                or set(config.request_capabilities) != {s.request_id for s in patient_seeds}
                or any(config.request_capabilities[s.request_id] != s.patient_capability for s in patient_seeds)):
            raise ValueError("DEMO_SEEDS_INVALID")
        self.config = config
        self._sessions: dict[str, _Session] = {}
        self._initial_booking: dict[str, dict[str, str]] = {}
        for seed in config.seeds:
            token = secrets.token_urlsafe(32)
            binding = SessionBinding(
                persona=seed.persona, session_id=secrets.token_urlsafe(24),
                csrf=secrets.token_urlsafe(24), practice_id=config.practice_id,
                patient_id=config.patient_id, request_id=seed.request_id,
                patient_capability=seed.patient_capability,
                staff_user_id=seed.staff_user_id if seed.persona == "staff" else None,
            )
            self._sessions[token] = _Session(binding, seed.staff_bearer,
                seed.seeded_appointment_id, datetime.now(timezone.utc) + timedelta(hours=2))

    def cookie_for(self, persona: str, request_id: str) -> tuple[str, str]:
        """Return name/value only to the reviewed local harness; do not log it."""
        for token, session in self._sessions.items():
            b = session.binding
            if b.persona == persona and b.request_id == request_id:
                return COOKIE, token
        raise ValueError("SESSION_NOT_CONFIGURED")

    def issue_cookie(self, response: JSONResponse, persona: str, request_id: str) -> None:
        """Trusted fixture calls this out of band; no public issuance route."""
        name, value = self.cookie_for(persona, request_id)
        response.set_cookie(name, value, max_age=7200, httponly=True,
                            samesite="strict", secure=False, path="/demo/stage1")

    def session_for(self, request: Request) -> _Session:
        token = request.cookies.get(COOKIE)
        session = self._sessions.get(token or "")
        if session is None or datetime.now(timezone.utc) >= session.expires_at:
            raise HTTPException(status_code=404, detail="DEMO_SESSION_UNAVAILABLE")
        return session


def create_stage1_demo_app(config: DemoConfig) -> tuple[FastAPI, DemoIssuer]:
    """Create an isolated loopback ASGI app; caller owns listener binding."""
    issuer = DemoIssuer(config)
    app = FastAPI(title="Stage 1 synthetic local demo", docs_url=None, redoc_url=None,
                  openapi_url=None)
    voice_lock = asyncio.Lock()

    def local(request: Request) -> None:
        server = request.scope.get("server")
        client = request.client
        if (not server or server[0] != "127.0.0.1" or client is None
                or client.host != "127.0.0.1" or request.headers.get("host") !=
                config.listener_origin.removeprefix("http://")):
            raise HTTPException(status_code=404, detail="DEMO_UNAVAILABLE")

    def no_store(data: Any, code: int = 200) -> JSONResponse:
        return JSONResponse(data, status_code=code,
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    async def backend(method: str, path: str, session: _Session, *, body=None,
                      key: str | None = None, patient: bool = False) -> Any:
        headers = {"Cache-Control": "no-store"}
        if patient:
            capability = config.request_capabilities.get(session.binding.request_id)
            if not capability:
                raise HTTPException(status_code=404, detail="REQUEST_UNAVAILABLE")
            headers["X-Patient-Request-Capability"] = capability
        else:
            if not session.staff_bearer:
                raise HTTPException(status_code=403, detail="STAFF_UNAVAILABLE")
            headers["Authorization"] = "Bearer " + session.staff_bearer
        if key:
            headers["Idempotency-Key"] = key
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=config.backend_app,
                client=("127.0.0.1", 12345), raise_app_exceptions=False), base_url="http://127.0.0.1",
                follow_redirects=False, timeout=10) as client:
            response = await client.request(method, BASE + path, headers=headers, json=body)
        if response.status_code >= 400:
            # A current-authority refusal is definitive, never a lost reply.
            # Keep its body opaque and consistent with other stale/denied
            # backend outcomes at this demo boundary.
            raise HTTPException(status_code=409 if response.status_code in {400, 401, 403, 404, 409, 422} else 503,
                                detail="BACKEND_ACTION_UNAVAILABLE")
        try:
            return response.json()
        except ValueError:
            raise HTTPException(status_code=503, detail="BACKEND_READBACK_UNAVAILABLE") from None

    async def patient_read(session: _Session) -> dict[str, Any]:
        return await backend("GET", f"/patient-requests/{session.binding.request_id}", session, patient=True)

    async def staff_request(session: _Session) -> dict[str, Any]:
        return await backend("GET", f"/staff/patient-requests/{session.binding.request_id}", session)

    async def appointment(session: _Session, appointment_id: str) -> dict[str, Any]:
        row = await backend("GET", f"/{appointment_id}", session)
        if row.get("id") != appointment_id or row.get("practice_id") != config.practice_id or row.get("patient_id") != config.patient_id:
            raise HTTPException(status_code=409, detail="APPOINTMENT_SCOPE_CHANGED")
        return row

    def present_appointment(row: dict[str, Any]) -> dict[str, Any]:
        if type(row.get("appointment_state_version")) is not int or row["appointment_state_version"] < 1:
            raise HTTPException(status_code=409, detail="APPOINTMENT_VERSION_UNAVAILABLE")
        practitioner = row.get("practitioner")
        kind = row.get("appointment_type")
        patient = row.get("patient")
        if (row.get("practitioner_id") != config.practitioner_id or
                row.get("appointment_type_id") != config.appointment_type_id or
                row.get("location_id") != config.location_id or
                not isinstance(practitioner, dict) or practitioner.get("id") != config.practitioner_id or
                not isinstance(kind, dict) or kind.get("id") != config.appointment_type_id or
                not isinstance(patient, dict) or patient.get("id") != config.patient_id):
            raise HTTPException(status_code=409, detail="APPOINTMENT_DIMENSIONS_CHANGED")
        patient_name = " ".join(part for part in (patient.get("first_name"), patient.get("last_name")) if part)
        practitioner_name = " ".join(part for part in (practitioner.get("first_name"), practitioner.get("last_name")) if part)
        type_name = kind.get("name")
        clock = local_minute(row.get("start_time_local"))
        if (not clock or patient_name != config.patient_label or
                practitioner_name != config.practitioner_label or
                type_name != config.appointment_type_label or not isinstance(type_name, str)
                or not type_name.strip() or not config.location_label.strip()):
            raise HTTPException(status_code=409, detail="APPOINTMENT_LABELS_UNAVAILABLE")
        return {"ref": row["id"], "date": row["appointment_date"],
                "start_local": clock, "zone": config.timezone,
                "status": row["status"], "state_version": row["appointment_state_version"],
                "patient_label": patient_name, "practitioner_label": practitioner_name,
                "type_label": type_name, "duration_minutes": row["duration_minutes"],
                "location_label": config.location_label if config.location_id else "No location assigned"}

    async def refreshed(session: _Session) -> dict[str, Any]:
        if session.binding.persona == "patient":
            request = await patient_read(session)
            options = (await backend("GET", f"/patient-requests/{session.binding.request_id}/options"
                       f"?request_version={request['request_version']}", session, patient=True)
                       if request.get("state") == "draft" else [])
            captured = issuer._initial_booking.get(session.binding.request_id)
            original = captured if (request.get("state") == "booked" and captured and
                captured["appointment_id"] == request.get("booked_appointment_id")) else None
            return {"request": request, "options": options, "original_booking": original}
        request = await staff_request(session)
        options: list[dict[str, Any]] = []
        if request.get("state") == "submitted":
            capability = config.request_capabilities.get(session.binding.request_id)
            if not capability:
                raise HTTPException(status_code=404, detail="REQUEST_UNAVAILABLE")
            # Dedicated request capability belongs to trusted fixture, not the
            # staff browser session. Backend is the only option source.
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=config.backend_app,
                    client=("127.0.0.1", 12345), raise_app_exceptions=False), base_url="http://127.0.0.1",
                    follow_redirects=False, timeout=10) as client:
                response = await client.get(BASE + f"/patient-requests/{session.binding.request_id}/options",
                    params={"request_version": request["request_version"]},
                    headers={"X-Patient-Request-Capability": capability})
            if response.status_code == 200:
                options = response.json()
        appointment_id = request.get("booked_appointment_id") or session.seeded_appointment_id
        current = present_appointment(await appointment(session, appointment_id)) if appointment_id else None
        captured = issuer._initial_booking.get(session.binding.request_id)
        original = captured if (request.get("state") == "booked" and captured and
            captured["appointment_id"] == request.get("booked_appointment_id")) else None
        return {"request": request, "options": options, "appointment": current,
                "original_booking": original}

    async def record_initial_create(session: _Session, result: dict[str, Any]) -> dict[str, Any]:
        result_id = result.get("appointment", {}).get("id")
        if not result_id:
            raise HTTPException(status_code=409, detail="CREATE_RESULT_UNAVAILABLE")
        current = present_appointment(await appointment(session, result_id))
        linked_request = await staff_request(session)
        receipt = result.get("confirmation_receipt")
        verification = receipt.get("verification") if isinstance(receipt, dict) else None
        try:
            correlation_valid = (isinstance(receipt["correlation_id"], str)
                and str(uuid.UUID(receipt["correlation_id"])) == receipt["correlation_id"])
            audit_valid = (isinstance(receipt["audit_event_id"], str)
                and str(uuid.UUID(receipt["audit_event_id"])) == receipt["audit_event_id"])
        except (KeyError, TypeError, ValueError, AttributeError):
            correlation_valid = audit_valid = False
        verified = isinstance(verification, dict) and all(
            verification.get(name) is True for name in (
                "actor_authenticated", "practice_scope_verified", "proposal_revalidated",
                "conflict_check_passed", "idempotency_verified", "audit_recorded",
                "signed_evidence_verified",
            )
        ) and verification.get("visual_diary_check_required") is False
        if (linked_request.get("state") != "booked" or
                linked_request.get("booked_appointment_id") != result_id or
                current["date"] != result["appointment"].get("appointment_date") or
                current["start_local"] != local_minute(result["appointment"].get("start_time_local")) or
                not isinstance(receipt, dict) or
                receipt.get("schema_version") != "appointment.confirmation_receipt.v1" or
                receipt.get("outcome") != "appointment_created" or
                receipt.get("appointment_id") != result_id or
                receipt.get("appointment_date") != current["date"] or
                local_minute(receipt.get("start_time_local")) != current["start_local"] or
                receipt.get("duration_minutes") != current["duration_minutes"] or
                receipt.get("status") != current["status"] or
                receipt.get("patient_display") != current["patient_label"] or
                receipt.get("practitioner_display") != current["practitioner_label"] or
                receipt.get("appointment_type") != current["type_label"] or
                not isinstance(receipt.get("confirmed_by_display"), str) or
                not receipt["confirmed_by_display"].strip() or
                (receipt.get("confirmed_by_role") is not None and
                 not isinstance(receipt.get("confirmed_by_role"), str)) or
                (receipt.get("session_id") is not None and
                 not isinstance(receipt.get("session_id"), str)) or
                not correlation_valid or not audit_valid or not verified):
            raise HTTPException(status_code=409, detail="REQUEST_COMMAND_LINK_MISMATCH")
        issuer._initial_booking[session.binding.request_id] = {
            "appointment_id": result_id, "date": current["date"],
            "start_local": current["start_local"], "zone": current["zone"],
            "source": "completed_create_command_result",
        }
        return current

    async def verified_submission(session: _Session, result: Any,
                                  payload: dict[str, Any]) -> dict[str, Any]:
        # The backend receipt is the outcome of the exact original submit.
        # Its readback may already have advanced to booked, but the request
        # identity, submitted version and preferences must still agree.
        expected_version = payload["request_version"] + 1
        if (not isinstance(result, dict) or
                result.get("request_id") != session.binding.request_id or
                result.get("state") != "submitted" or
                type(result.get("request_version")) is not int or
                result["request_version"] != expected_version):
            raise HTTPException(status_code=409, detail="REQUEST_RECEIPT_MISMATCH")
        snapshot = await refreshed(session)
        current = snapshot["request"]
        if (current.get("request_id") != session.binding.request_id or
                current.get("state") not in {"submitted", "booked"} or
                type(current.get("request_version")) is not int or
                current["request_version"] < expected_version or
                current.get("preference_date") != payload["date"] or
                local_minute(current.get("earliest_local")) != payload["earliest_local"] or
                local_minute(current.get("latest_local")) != payload["latest_local"]):
            raise HTTPException(status_code=409, detail="REQUEST_READBACK_MISMATCH")
        return snapshot

    async def uncertain_snapshot(session: _Session) -> JSONResponse:
        try:
            return no_store({**(await refreshed(session)), "uncertain": True})
        except HTTPException:
            return no_store({"uncertain": True})

    @app.get("/demo/stage1/session")
    async def session_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        voice_ready = config.voice_runtime is not None and config.voice_runtime.ready()
        return no_store({"persona": session.binding.persona, "csrf": session.binding.csrf,
            "zone": config.timezone, "demo_clock": config.demo_clock,
            "voice_available": voice_ready, "voice_nonce": session.voice_nonce if voice_ready else None})

    @app.get("/demo/stage1/")
    async def page(request: Request):
        local(request); issuer.session_for(request)
        return FileResponse(STATIC / "stage1-interactive.html", headers={"Cache-Control": "no-store"})

    @app.get("/demo/stage1/{asset}")
    async def asset(request: Request, asset: str):
        local(request); issuer.session_for(request)
        if asset not in {"stage1-interactive.css", "stage1-interactive.js",
                         "stage1-local-voice.js"}:
            raise HTTPException(status_code=404)
        return FileResponse(STATIC / asset, headers={"Cache-Control": "no-store"})

    @app.post("/demo/stage1/voice")
    async def voice_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        binding = config.voice_runtime
        if binding is None or not binding.ready():
            return no_store({"error": "VOICE_UNAVAILABLE"}, 503)
        target = target_for_persona(session.binding.persona)
        if (request.headers.get("origin") != config.listener_origin
                or request.headers.get("content-type") != "audio/wav"
                or request.headers.get("x-voice-target") != target
                or not secrets.compare_digest(request.headers.get("x-csrf-token", ""),
                                               session.binding.csrf)
                or not secrets.compare_digest(request.headers.get("x-voice-nonce", ""),
                                               session.voice_nonce)):
            return no_store({"error": "VOICE_SCOPE_UNAVAILABLE"}, 403)
        # A nonce authorises exactly one bounded clip, never a domain action.
        session.voice_nonce = secrets.token_urlsafe(24)
        next_nonce = session.voice_nonce
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_WAV_BYTES:
                return no_store({"error": "VOICE_TOO_LARGE"}, 413)
            parts.append(chunk)
        raw = b"".join(parts)
        try:
            validate_wav(raw)
        except VoiceInputRejected:
            return no_store({"error": "VOICE_FORMAT_UNAVAILABLE"}, 400)
        if voice_lock.locked():
            return no_store({"error": "VOICE_BUSY"}, 429)
        try:
            async with voice_lock:
                transcript = await asyncio.to_thread(run_local_recognizer, raw, binding)
        except (VoiceInputRejected, VoiceRecognitionUnavailable):
            return no_store({"error": "VOICE_RECOGNITION_UNAVAILABLE"}, 503)
        if (datetime.now(timezone.utc) >= session.expires_at
                or issuer.session_for(request) is not session
                or session.voice_nonce != next_nonce):
            return no_store({"error": "VOICE_SESSION_CHANGED"}, 409)
        return no_store({"text": transcript, "target": target})

    @app.post("/demo/stage1/action")
    async def action_route(request: Request):
        local(request)
        session = issuer.session_for(request)
        parts: list[bytes] = []
        size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_BODY_BYTES:
                raise HTTPException(status_code=413, detail="BODY_TOO_LARGE")
            parts.append(chunk)
        raw = b"".join(parts)
        try:
            admitted = admit_action(profile=config.profile, enabled=True,
                listener_host=request.scope["server"][0], request_host=request.client.host,
                origin=request.headers.get("origin"), expected_origin=config.listener_origin,
                content_type=request.headers.get("content-type", ""),
                csrf_header=request.headers.get("x-csrf-token"), body_bytes=raw,
                binding=session.binding)
        except AdapterRejected:
            raise HTTPException(status_code=403, detail="DEMO_ACTION_UNAVAILABLE") from None
        action, body, key = admitted.action, admitted.body, admitted.idempotency_key
        if action == "refresh":
            return no_store({**(await refreshed(session)), "uncertain": session.uncertain is not None})
        if action == "reconcile":
            pending = session.uncertain
            if pending is None:
                return no_store({**(await refreshed(session)), "uncertain": False})
            # Explicit human check reuses the exact payload and key. Backend
            # request/command idempotency owns the replay decision; no new key
            # or alternate proposal is minted here.
            family = pending["family"]
            path = (f"/patient-requests/{session.binding.request_id}/submit" if family == "submit_request"
                    else "/proposals/create/confirm" if family == "create"
                    else "/proposals/update/confirm")
            try:
                result = await backend("POST", path, session, body=pending["payload"],
                    key=pending["key"], patient=family == "submit_request")
            except (httpx.TimeoutException, httpx.TransportError):
                return await uncertain_snapshot(session)
            if family != "submit_request" and (result.get("safe") is not True
                    or not isinstance(result.get("appointment"), dict)):
                return await uncertain_snapshot(session)
            if family == "move" and result["appointment"].get("id") != pending["appointment_id"]:
                return await uncertain_snapshot(session)
            if family == "move":
                try:
                    current = present_appointment(await appointment(session, pending["appointment_id"]))
                except HTTPException:
                    return await uncertain_snapshot(session)
                if (current["ref"] != result["appointment"].get("id") or
                        current["date"] != result["appointment"].get("appointment_date") or
                        current["start_local"] != local_minute(result["appointment"].get("start_time_local"))):
                    return await uncertain_snapshot(session)
            if family == "create":
                try:
                    await record_initial_create(session, result)
                except HTTPException:
                    return await uncertain_snapshot(session)
            try:
                snapshot = (await verified_submission(session, result, pending["payload"])
                    if family == "submit_request" else await refreshed(session))
            except HTTPException:
                return await uncertain_snapshot(session)
            session.uncertain = None
            session.proposal = None
            return no_store({**snapshot, "uncertain": False})
        if session.uncertain is not None:
            raise HTTPException(status_code=409, detail="COMMAND_OUTCOME_UNCERTAIN")
        if action == "submit_request":
            if set(body) != {"date", "earliest_local", "latest_local", "request_version", "reason_code"}:
                raise HTTPException(status_code=400, detail="REQUEST_BODY_INVALID")
            payload = {**body, "schema_version": "patient.request_submission.v1",
                "request_id": session.binding.request_id, "authority": "request_only"}
            pending = {"family": "submit_request", "key": key, "payload": payload}
            try:
                result = await backend("POST", f"/patient-requests/{session.binding.request_id}/submit",
                    session, body=payload, key=key, patient=True)
            except (httpx.TimeoutException, httpx.TransportError):
                session.uncertain = pending
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except HTTPException as exc:
                if exc.status_code == 503:
                    session.uncertain = pending
                raise
            session.uncertain = pending
            snapshot = await verified_submission(session, result, payload)
            response = no_store(snapshot)
            session.uncertain = None
            return response
        if action == "propose_create":
            if set(body) != {"request_version", "selected"}:
                raise HTTPException(status_code=400, detail="CREATE_BODY_INVALID")
            proposal = await backend("POST",
                f"/staff/patient-requests/{session.binding.request_id}/proposals/create",
                session, body=body)
            if proposal.get("safe") is not True or not isinstance(proposal.get("confirm_payload"), dict):
                return no_store({"safe": False})
            ref = secrets.token_urlsafe(24)
            session.proposal = {"family": "create", "ref": ref, "payload": proposal["confirm_payload"],
                "request_version": body["request_version"], "expires": datetime.now(timezone.utc) + timedelta(minutes=4)}
            return no_store({"safe": True, "proposal_ref": ref,
                "patient_label": config.patient_label, "practitioner_label": config.practitioner_label})
        if action == "propose_move":
            if set(body) != {"appointment_ref", "source_state_version", "target_date", "target_start_local"}:
                raise HTTPException(status_code=400, detail="MOVE_BODY_INVALID")
            current = await refreshed(session)
            appt = current.get("appointment")
            if not appt or body["appointment_ref"] != appt["ref"] or body["source_state_version"] != appt["state_version"]:
                raise HTTPException(status_code=409, detail="MOVE_SOURCE_CHANGED")
            payload = {"schema_version": "appointment.move_time_intent.v1",
                "tenant_id": config.practice_id, "actor_id": session.binding.staff_user_id,
                "role": "reception", "source_appointment_id": appt["ref"],
                "source_state_version": appt["state_version"], "source_revision": appt["state_version"],
                "target_date": body["target_date"], "target_start_local": body["target_start_local"],
                "authority": "proposal_only"}
            proposal = await backend("POST", f"/proposals/move-time/{appt['ref']}", session, body=payload)
            if proposal.get("safe") is not True or not isinstance(proposal.get("confirm_payload"), dict):
                return no_store({"safe": False})
            ref = secrets.token_urlsafe(24)
            session.proposal = {"family": "move", "ref": ref, "payload": proposal["confirm_payload"],
                "appointment_id": appt["ref"], "source_state_version": appt["state_version"],
                "expires": datetime.now(timezone.utc) + timedelta(minutes=4)}
            return no_store({"safe": True, "proposal_ref": ref})
        if action in {"confirm_create", "confirm_move"}:
            proposal = session.proposal
            family = "create" if action == "confirm_create" else "move"
            if (set(body) != {"proposal_ref"} or proposal is None or proposal["family"] != family
                    or body["proposal_ref"] != proposal["ref"]
                    or datetime.now(timezone.utc) >= proposal["expires"]):
                raise HTTPException(status_code=409, detail="PROPOSAL_STALE")
            # The signed payload is backend-authored. Only the deliberate human
            # confirmation flag changes; all domain checks occur in backend.
            payload = {**proposal["payload"], "confirmed": True}
            route = "/proposals/create/confirm" if family == "create" else "/proposals/update/confirm"
            pending = {"family": family, "key": key, "payload": payload,
                "appointment_id": proposal.get("appointment_id")}
            try:
                result = await backend("POST", route, session, body=payload, key=key)
            except (httpx.TimeoutException, httpx.TransportError):
                session.uncertain = pending
                raise HTTPException(status_code=503, detail="COMMAND_OUTCOME_UNCERTAIN") from None
            except HTTPException as exc:
                if exc.status_code == 503:
                    session.uncertain = pending
                raise
            # A positive HTTP response is not proof of the effect. Retain the
            # original key and backend-authored payload until typed receipt and
            # fresh scoped readback both establish the committed outcome.
            session.uncertain = pending
            if result.get("safe") is not True or not isinstance(result.get("appointment"), dict):
                raise HTTPException(status_code=409, detail="CONFIRMATION_BLOCKED")
            result_id = result["appointment"].get("id")
            if family == "move" and result_id != proposal["appointment_id"]:
                raise HTTPException(status_code=409, detail="MOVE_IDENTITY_CHANGED")
            current = present_appointment(await appointment(session, result_id))
            if (current["date"] != result["appointment"].get("appointment_date")
                    or current["start_local"] != local_minute(result["appointment"].get("start_time_local"))):
                raise HTTPException(status_code=409, detail="COMMITTED_READBACK_MISMATCH")
            if family == "create":
                await record_initial_create(session, result)
            response = no_store({"outcome": "committed", "appointment": current})
            session.uncertain = None
            session.proposal = None
            return response
        raise HTTPException(status_code=404, detail="ACTION_UNAVAILABLE")

    return app, issuer
