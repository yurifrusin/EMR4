"""Server-owned Bernie session append semantics.

This module is intentionally in-memory and pure-Python for N4. It models the
future transactional DB contract without adding a PHI-bearing table yet:

1. sessions are owned by practice + staff + diary surface;
2. every client event echoes the current revision;
3. idempotent replays are safe and conflicting replays fail closed;
4. semantic state advances only through ``session.py`` transition tables;
5. event payloads are PHI-minimised by default.
"""

from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import date, datetime, timezone
from typing import Any, Optional

from app.services.bernie.session import (
    BernieSessionEvent,
    BernieSessionEventRejectionCode,
    BernieSessionEventResult,
    BernieSessionEventType,
    BernieSessionRecord,
    BernieSessionState,
    SERVER_ADVANCE_TARGETS,
    SERVER_OUTCOME_EVENT_TARGETS,
    validate_session_event,
)


PHI_PAYLOAD_KEYWORDS = frozenset({
    "address",
    "chat_transcript",
    "debug",
    "dob",
    "free_text",
    "full_patient_name",
    "ihi",
    "instruction_text",
    "medicare",
    "medicare_number",
    "patient_dob",
    "patient_label",
    "patient_name",
    "phone",
    "raw_instruction",
    "raw_transcript",
    "transcript",
    "utterance",
})


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _contains_phi_payload_key(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key).lower()
            if key_text in PHI_PAYLOAD_KEYWORDS:
                return key_text
            found = _contains_phi_payload_key(nested)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = _contains_phi_payload_key(item)
            if found:
                return found
    return None


def build_session_confirmation_binding(
    session: BernieSessionRecord,
    *,
    candidate_freshness_id: Optional[str] = None,
    proposal_freshness_id: Optional[str] = None,
    appointment_date: Optional[date] = None,
    start_time_local: Optional[str] = None,
    duration_minutes: Optional[int] = None,
) -> dict[str, Any]:
    """Return the session coordinates a signed confirmation envelope must bind."""

    return {
        "practice_id": str(session.practice_id) if session.practice_id is not None else None,
        "staff_user_id": str(session.user_id) if session.user_id is not None else None,
        "surface_id": session.surface_id,
        "session_id": session.session_id,
        "session_revision": session.revision,
        "reference_date": (
            session.request_reference_date.isoformat()
            if session.request_reference_date is not None
            else None
        ),
        "patient_id": str(session.patient_id) if session.patient_id is not None else None,
        "practitioner_id": (
            str(session.practitioner_id) if session.practitioner_id is not None else None
        ),
        "candidate_freshness_id": candidate_freshness_id,
        "proposal_freshness_id": proposal_freshness_id,
        "appointment_date": appointment_date.isoformat() if appointment_date is not None else None,
        "start_time_local": start_time_local,
        "duration_minutes": duration_minutes,
    }


class InMemoryBernieSessionStore:
    """Executable stand-in for a future DB-backed Bernie session store."""

    def __init__(self) -> None:
        self._sessions: dict[str, BernieSessionRecord] = {}
        self._active_sessions: dict[tuple[uuid.UUID, uuid.UUID, str], str] = {}
        self._idempotency_results: dict[tuple[str, str], BernieSessionEventResult] = {}
        self._idempotency_payloads: dict[tuple[str, str], str] = {}

    def create_session(
        self,
        *,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        request_reference_date: Optional[date] = None,
        session_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> BernieSessionRecord:
        timestamp = now or _utcnow()
        record = BernieSessionRecord(
            session_id=session_id or uuid.uuid4().hex,
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
            request_reference_date=request_reference_date,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self._sessions[record.session_id] = record
        self._active_sessions[(practice_id, user_id, surface_id)] = record.session_id
        return record

    def get_session(self, session_id: str) -> Optional[BernieSessionRecord]:
        session = self._sessions.get(session_id)
        return session.model_copy(deep=True) if session is not None else None

    def get_active_session(
        self,
        *,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
    ) -> Optional[BernieSessionRecord]:
        session_id = self._active_sessions.get((practice_id, user_id, surface_id))
        if session_id is None:
            return None
        return self.get_session(session_id)

    def get_or_create_active_session(
        self,
        *,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        request_reference_date: Optional[date] = None,
    ) -> BernieSessionRecord:
        existing = self.get_active_session(
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
        )
        if existing is not None:
            return existing
        return self.create_session(
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
            request_reference_date=request_reference_date,
        )

    def append_client_event(
        self,
        *,
        session_id: str,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        event_type: BernieSessionEventType,
        expected_revision: int,
        event_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
        occurred_at: Optional[datetime] = None,
    ) -> BernieSessionEventResult:
        session = self._sessions.get(session_id)
        if session is None:
            return self._reject(
                BernieSessionEventRejectionCode.session_not_found,
                "Bernie session was not found.",
            )

        if (
            session.practice_id != practice_id
            or session.user_id != user_id
            or session.surface_id != surface_id
        ):
            return self._reject(
                BernieSessionEventRejectionCode.session_owner_mismatch,
                "Bernie session belongs to a different practice, staff user, or diary surface.",
            )

        event_payload = payload or {}
        phi_key = _contains_phi_payload_key(event_payload)
        if phi_key is not None:
            return self._reject(
                BernieSessionEventRejectionCode.phi_payload_not_allowed,
                f"Event payload key {phi_key!r} is not allowed in Bernie session state.",
            )

        identity = idempotency_key or event_id
        canonical = _canonical_payload({
            "event_type": event_type.value,
            "expected_revision": expected_revision,
            "payload": event_payload,
        })
        if identity:
            idem_key = (session_id, identity)
            prior_payload = self._idempotency_payloads.get(idem_key)
            if prior_payload is not None:
                if prior_payload == canonical:
                    return self._idempotency_results[idem_key]
                return self._reject(
                    BernieSessionEventRejectionCode.idempotency_conflict,
                    "Event idempotency key was replayed with a different payload.",
                )

        if expected_revision < session.revision:
            return self._reject(
                BernieSessionEventRejectionCode.stale_session_revision,
                "Bernie session event was based on an older session revision.",
            )
        if expected_revision > session.revision:
            return self._reject(
                BernieSessionEventRejectionCode.future_session_revision,
                "Bernie session event skipped the current session revision.",
            )

        transition = validate_session_event(session.state, event_type)
        if not transition.allowed:
            code = BernieSessionEventRejectionCode(transition.reason_code)
            return self._reject(code, transition.detail or "Event is not allowed.")

        event = BernieSessionEvent(
            event_id=event_id or uuid.uuid4().hex,
            session_id=session_id,
            event_type=event_type,
            turn_index=session.turn_count,
            occurred_at=occurred_at or _utcnow(),
            expected_revision=expected_revision,
            idempotency_key=idempotency_key,
            payload=deepcopy(event_payload),
        )
        updated = self._apply_client_transition(session, event, transition.target_state)
        self._sessions[session_id] = updated
        result = BernieSessionEventResult(
            accepted=True,
            session=updated.model_copy(deep=True),
            event=event,
        )
        if identity:
            idem_key = (session_id, identity)
            self._idempotency_payloads[idem_key] = canonical
            self._idempotency_results[idem_key] = result
        return result

    def advance_server_state(
        self,
        *,
        session_id: str,
        target_state: BernieSessionState,
    ) -> BernieSessionEventResult:
        session = self._sessions.get(session_id)
        if session is None:
            return self._reject(
                BernieSessionEventRejectionCode.session_not_found,
                "Bernie session was not found.",
            )
        allowed_targets = SERVER_ADVANCE_TARGETS.get(session.state, frozenset())
        if target_state not in allowed_targets:
            return self._reject(
                BernieSessionEventRejectionCode.event_not_allowed_in_state,
                f"Server cannot advance {session.state.value} to {target_state.value}.",
            )
        updated = session.model_copy(update={
            "state": target_state,
            "revision": session.revision + 1,
            "updated_at": _utcnow(),
        }, deep=True)
        self._sessions[session_id] = updated
        return BernieSessionEventResult(accepted=True, session=updated.model_copy(deep=True))

    def append_server_outcome_event(
        self,
        *,
        session_id: str,
        event_type: BernieSessionEventType,
        target_state: BernieSessionState,
        expected_revision: Optional[int] = None,
        event_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
        occurred_at: Optional[datetime] = None,
    ) -> BernieSessionEventResult:
        """Append a server-computed outcome event and advance semantic state.

        This is the server-side counterpart to ``append_client_event``. It is
        still process-local and PHI-minimised, but it gives interpreter,
        slot-search, proposal, and confirmation outcomes durable session
        coordinates before a real session table exists.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return self._reject(
                BernieSessionEventRejectionCode.session_not_found,
                "Bernie session was not found.",
            )

        event_payload = payload or {}
        phi_key = _contains_phi_payload_key(event_payload)
        if phi_key is not None:
            return self._reject(
                BernieSessionEventRejectionCode.phi_payload_not_allowed,
                f"Event payload key {phi_key!r} is not allowed in Bernie session state.",
            )

        canonical = _canonical_payload({
            "event_type": event_type.value,
            "target_state": target_state.value,
            "expected_revision": expected_revision,
            "payload": event_payload,
        })
        identity = idempotency_key or event_id
        if identity:
            idem_key = (session_id, identity)
            prior_payload = self._idempotency_payloads.get(idem_key)
            if prior_payload is not None:
                if prior_payload == canonical:
                    return self._idempotency_results[idem_key]
                return self._reject(
                    BernieSessionEventRejectionCode.idempotency_conflict,
                    "Event idempotency key was replayed with a different payload.",
                )

        if expected_revision is not None:
            if expected_revision < session.revision:
                return self._reject(
                    BernieSessionEventRejectionCode.stale_session_revision,
                    "Bernie session outcome was based on an older session revision.",
                )
            if expected_revision > session.revision:
                return self._reject(
                    BernieSessionEventRejectionCode.future_session_revision,
                    "Bernie session outcome skipped the current session revision.",
                )

        allowed_targets = SERVER_OUTCOME_EVENT_TARGETS.get(session.state, {}).get(event_type)
        if allowed_targets is None or target_state not in allowed_targets:
            return self._reject(
                BernieSessionEventRejectionCode.event_not_allowed_in_state,
                (
                    f"Server outcome {event_type.value} cannot advance "
                    f"{session.state.value} to {target_state.value}."
                ),
            )

        event = BernieSessionEvent(
            event_id=event_id or uuid.uuid4().hex,
            session_id=session_id,
            event_type=event_type,
            turn_index=session.turn_count,
            occurred_at=occurred_at or _utcnow(),
            expected_revision=expected_revision,
            idempotency_key=idempotency_key,
            payload=deepcopy(event_payload),
        )
        updated = session.model_copy(update={
            "state": target_state,
            "revision": session.revision + 1,
            "events": [*session.events, event],
            "last_event_id": event.event_id,
            "updated_at": event.occurred_at,
        }, deep=True)
        if event_type is BernieSessionEventType.proposal_outcome:
            candidate_id = event.payload.get("candidate_freshness_id")
            proposal_id = event.payload.get("proposal_freshness_id")
            if isinstance(candidate_id, str):
                updated = updated.model_copy(update={"candidate_freshness_ids": [candidate_id]}, deep=True)
            if isinstance(proposal_id, str):
                updated = updated.model_copy(update={"staged_proposal_freshness_id": proposal_id}, deep=True)

        self._sessions[session_id] = updated
        result = BernieSessionEventResult(
            accepted=True,
            session=updated.model_copy(deep=True),
            event=event,
        )
        if identity:
            idem_key = (session_id, identity)
            self._idempotency_payloads[idem_key] = canonical
            self._idempotency_results[idem_key] = result
        return result

    @staticmethod
    def _reject(
        code: BernieSessionEventRejectionCode,
        detail: str,
    ) -> BernieSessionEventResult:
        return BernieSessionEventResult(accepted=False, code=code, detail=detail)

    @staticmethod
    def _apply_client_transition(
        session: BernieSessionRecord,
        event: BernieSessionEvent,
        target_state: Optional[BernieSessionState],
    ) -> BernieSessionRecord:
        update: dict[str, Any] = {
            "state": target_state or session.state,
            "revision": session.revision + 1,
            "turn_count": session.turn_count + 1,
            "events": [*session.events, event],
            "last_event_id": event.event_id,
            "updated_at": event.occurred_at,
        }
        if event.event_type is BernieSessionEventType.new_session:
            update.update({
                "patient_id": None,
                "patient_band": None,
                "practitioner_id": None,
                "practitioner_band": None,
                "candidate_freshness_ids": [],
                "staged_proposal_freshness_id": None,
                "stale_reason_code": None,
            })
        elif event.event_type is BernieSessionEventType.diary_navigated:
            update["stale_reason_code"] = "diary_context_changed"
            update["candidate_freshness_ids"] = []
            update["staged_proposal_freshness_id"] = None
        elif event.event_type is BernieSessionEventType.refresh_requested:
            update["stale_reason_code"] = "refresh_requested"
            update["candidate_freshness_ids"] = []
            update["staged_proposal_freshness_id"] = None
        elif event.event_type is BernieSessionEventType.candidate_selected:
            candidate_id = event.payload.get("candidate_freshness_id")
            if isinstance(candidate_id, str):
                update["candidate_freshness_ids"] = [candidate_id]
        elif event.event_type is BernieSessionEventType.confirm_submitted:
            proposal_id = event.payload.get("proposal_freshness_id")
            if isinstance(proposal_id, str):
                update["staged_proposal_freshness_id"] = proposal_id
        return session.model_copy(update=update, deep=True)


__all__ = [
    "PHI_PAYLOAD_KEYWORDS",
    "InMemoryBernieSessionStore",
    "build_session_confirmation_binding",
]
