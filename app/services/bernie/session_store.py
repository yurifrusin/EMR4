"""Server-owned Bernie session append semantics.

The in-memory store remains a pure transition reference for focused unit tests.
The database store is the Stage 2 runtime implementation:

1. sessions are owned by practice + staff + diary surface;
2. every client event echoes the current revision;
3. idempotent replays are safe and conflicting replays fail closed;
4. semantic state advances only through ``session.py`` transition tables;
5. event payloads are PHI-minimised by default.
"""

from __future__ import annotations

import json
import hashlib
import hmac
import re
import uuid
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.bernie_sessions import BernieBookingSession, BernieSessionEventRow
from app.models.tenancy import User

from app.services.bernie.session import (
    BernieSessionEvent,
    BernieSessionEventRejectionCode,
    BernieSessionEventResult,
    BernieSessionEventType,
    BernieSessionRecord,
    BernieSessionState,
    SERVER_ADVANCE_TARGETS,
    SERVER_OUTCOME_EVENT_TARGETS,
    TERMINAL_STATES,
    validate_session_event,
)


PHI_PAYLOAD_KEYWORDS = frozenset({
    "access_token",
    "address",
    "authorization",
    "bearer",
    "chat_transcript",
    "credential",
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
    "password",
    "phone",
    "raw_instruction",
    "raw_transcript",
    "secret",
    "transcript",
    "utterance",
})

MAX_EVENT_PAYLOAD_BYTES = 16_384
INCOMPLETE_SESSION_RECOVERY = timedelta(hours=24)
COMPLETED_SESSION_RETENTION = timedelta(days=30)

_STRUCTURED_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/+\-]{0,255}$")
_DURABLE_EVENT_PAYLOAD_KEYS: dict[BernieSessionEventType, frozenset[str]] = {
    BernieSessionEventType.staff_instruction: frozenset({"intent_ref"}),
    BernieSessionEventType.clarification_reply: frozenset({
        "clarification_ref",
        "answer_ref",
    }),
    BernieSessionEventType.candidate_selected: frozenset({"candidate_freshness_id"}),
    BernieSessionEventType.suggestion_selected: frozenset({
        "suggestion_kind",
        "date_from",
        "date_to",
    }),
    BernieSessionEventType.diary_navigated: frozenset({"visible_diary_date"}),
    BernieSessionEventType.refresh_requested: frozenset({"reason_code"}),
    BernieSessionEventType.confirm_submitted: frozenset({"proposal_freshness_id"}),
    BernieSessionEventType.new_session: frozenset(),
    BernieSessionEventType.interpretation_outcome: frozenset({
        "result",
        "safe",
        "missing_field_count",
        "warning_codes",
        "block_codes",
        "safety_flags",
        "has_command_candidate",
    }),
    BernieSessionEventType.context_outcome: frozenset({
        "result",
        "safe",
        "warning_codes",
        "block_codes",
        "date_from",
        "date_to",
        "duration_minutes",
    }),
    BernieSessionEventType.slot_search_outcome: frozenset({
        "result",
        "safe",
        "candidate_count",
        "reason_code",
        "warning_codes",
        "block_codes",
        "suggestion_kinds",
    }),
    BernieSessionEventType.proposal_outcome: frozenset({
        "result",
        "safe",
        "candidate_freshness_id",
        "proposal_freshness_id",
        "patient_id",
        "practitioner_id",
        "appointment_date",
        "start_time_local",
        "duration_minutes",
        "warning_codes",
        "block_codes",
    }),
    BernieSessionEventType.confirmation_outcome: frozenset({
        "result",
        "confirmed",
        "appointment_id",
        "block_codes",
        "warning_codes",
        "audit_evidence_codes",
    }),
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hmac_identity(value: str, secret: bytes) -> str:
    return hmac.new(secret, value.encode("utf-8"), hashlib.sha256).hexdigest()


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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


def _is_structured_payload_value(value: Any) -> bool:
    if value is None or isinstance(value, (bool, int)):
        return True
    if isinstance(value, str):
        return bool(_STRUCTURED_TOKEN_RE.fullmatch(value))
    if isinstance(value, list):
        return len(value) <= 128 and all(
            isinstance(item, str) and bool(_STRUCTURED_TOKEN_RE.fullmatch(item))
            for item in value
        )
    return False


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
    """Pure executable reference for the durable session statechart."""

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

        This is the process-local reference counterpart to
        ``append_client_event``. Runtime durability is owned by
        ``DatabaseBernieSessionStore``.
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
            patient_id = event.payload.get("patient_id")
            practitioner_id = event.payload.get("practitioner_id")
            if isinstance(candidate_id, str):
                updated = updated.model_copy(update={"candidate_freshness_ids": [candidate_id]}, deep=True)
            if isinstance(proposal_id, str):
                updated = updated.model_copy(update={"staged_proposal_freshness_id": proposal_id}, deep=True)
            identity_updates: dict[str, Any] = {}
            if isinstance(patient_id, str) and patient_id:
                try:
                    identity_updates["patient_id"] = uuid.UUID(patient_id)
                except ValueError:
                    pass
            if isinstance(practitioner_id, str) and practitioner_id:
                try:
                    identity_updates["practitioner_id"] = uuid.UUID(practitioner_id)
                except ValueError:
                    pass
            if identity_updates:
                updated = updated.model_copy(update=identity_updates, deep=True)

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


class DatabaseBernieSessionStore:
    """Transactional PostgreSQL Bernie session store scoped to one practice."""

    def __init__(
        self,
        db: Session,
        *,
        practice_id: uuid.UUID,
        secret: bytes,
    ) -> None:
        self.db = db
        self.practice_id = practice_id
        self.secret = secret

    def _session_query(self, session_id: str, *, for_update: bool = False):
        query = self.db.query(BernieBookingSession).filter(
            BernieBookingSession.session_id == session_id,
            BernieBookingSession.practice_id == self.practice_id,
        )
        return query.with_for_update() if for_update else query

    def _events(self, session_id: str) -> list[BernieSessionEventRow]:
        return (
            self.db.query(BernieSessionEventRow)
            .filter(
                BernieSessionEventRow.practice_id == self.practice_id,
                BernieSessionEventRow.session_id == session_id,
            )
            .order_by(BernieSessionEventRow.session_revision)
            .all()
        )

    @staticmethod
    def _event_from_row(row: BernieSessionEventRow) -> BernieSessionEvent:
        return BernieSessionEvent(
            event_id=row.event_id,
            session_id=row.session_id,
            event_type=BernieSessionEventType(row.event_type),
            turn_index=row.turn_index,
            occurred_at=_as_aware_utc(row.occurred_at),
            expected_revision=row.expected_revision,
            idempotency_key=None,
            payload=deepcopy(row.payload or {}),
        )

    def _record_from_row(self, row: BernieBookingSession) -> BernieSessionRecord:
        return BernieSessionRecord(
            session_id=row.session_id,
            practice_id=row.practice_id,
            user_id=row.staff_user_id,
            surface_id=row.surface_id,
            state=BernieSessionState(row.state),
            revision=row.revision,
            request_reference_date=row.request_reference_date,
            patient_id=row.patient_id,
            patient_band=row.patient_band,
            practitioner_id=row.practitioner_id,
            practitioner_band=row.practitioner_band,
            candidate_freshness_ids=list(row.candidate_freshness_ids or []),
            staged_proposal_freshness_id=row.staged_proposal_freshness_id,
            turn_count=row.turn_count,
            events=[self._event_from_row(event) for event in self._events(row.session_id)],
            last_event_id=row.last_event_id,
            stale_reason_code=row.stale_reason_code,
            created_at=_as_aware_utc(row.created_at),
            updated_at=_as_aware_utc(row.updated_at),
        )

    @staticmethod
    def _apply_record_to_row(
        row: BernieBookingSession,
        record: BernieSessionRecord,
        *,
        timestamp: datetime,
    ) -> None:
        row.state = record.state.value
        row.revision = record.revision
        row.request_reference_date = record.request_reference_date
        row.patient_id = record.patient_id
        row.patient_band = record.patient_band
        row.practitioner_id = record.practitioner_id
        row.practitioner_band = record.practitioner_band
        row.candidate_freshness_ids = list(record.candidate_freshness_ids)
        row.staged_proposal_freshness_id = record.staged_proposal_freshness_id
        row.turn_count = record.turn_count
        row.last_event_id = record.last_event_id
        row.stale_reason_code = record.stale_reason_code
        row.updated_at = timestamp
        if record.state in TERMINAL_STATES:
            row.completed_at = timestamp
            row.expires_at = timestamp + COMPLETED_SESSION_RETENTION
        else:
            row.completed_at = None
            row.expires_at = timestamp + INCOMPLETE_SESSION_RECOVERY

    def get_session(self, session_id: str) -> Optional[BernieSessionRecord]:
        row = self._session_query(session_id).one_or_none()
        return self._record_from_row(row) if row is not None else None

    def get_active_session(
        self,
        *,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        now: Optional[datetime] = None,
        for_update: bool = False,
    ) -> Optional[BernieSessionRecord]:
        if practice_id != self.practice_id:
            return None
        timestamp = now or _utcnow()
        query = self.db.query(BernieBookingSession).filter(
            BernieBookingSession.practice_id == practice_id,
            BernieBookingSession.staff_user_id == user_id,
            BernieBookingSession.surface_id == surface_id,
            BernieBookingSession.is_active.is_(True),
            BernieBookingSession.expires_at > timestamp,
        )
        if for_update:
            query = query.with_for_update()
        row = query.one_or_none()
        return self._record_from_row(row) if row is not None else None

    def _lock_owner(self, practice_id: uuid.UUID, user_id: uuid.UUID) -> None:
        owner = (
            self.db.query(User)
            .filter(User.id == user_id, User.practice_id == practice_id)
            .with_for_update()
            .one_or_none()
        )
        if owner is None:
            raise ValueError("Bernie session owner does not belong to the practice.")

    def _create_after_owner_lock(
        self,
        *,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        request_reference_date: Optional[date],
        session_id: Optional[str],
        timestamp: datetime,
    ) -> BernieSessionRecord:
        (
            self.db.query(BernieBookingSession)
            .filter(
                BernieBookingSession.practice_id == practice_id,
                BernieBookingSession.staff_user_id == user_id,
                BernieBookingSession.surface_id == surface_id,
                BernieBookingSession.is_active.is_(True),
            )
            .update({BernieBookingSession.is_active: False}, synchronize_session=False)
        )
        row = BernieBookingSession(
            session_id=session_id or uuid.uuid4().hex,
            practice_id=practice_id,
            staff_user_id=user_id,
            surface_id=surface_id,
            state=BernieSessionState.instruction_entry.value,
            revision=0,
            request_reference_date=request_reference_date,
            candidate_freshness_ids=[],
            turn_count=0,
            is_active=True,
            expires_at=timestamp + INCOMPLETE_SESSION_RECOVERY,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.db.add(row)
        self.db.flush()
        return self._record_from_row(row)

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
        if practice_id != self.practice_id:
            raise ValueError("Bernie session practice does not match the store scope.")
        timestamp = now or _utcnow()
        self._lock_owner(practice_id, user_id)
        return self._create_after_owner_lock(
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
            request_reference_date=request_reference_date,
            session_id=session_id,
            timestamp=timestamp,
        )

    def get_or_create_active_session(
        self,
        *,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        request_reference_date: Optional[date] = None,
        now: Optional[datetime] = None,
    ) -> BernieSessionRecord:
        if practice_id != self.practice_id:
            raise ValueError("Bernie session practice does not match the store scope.")
        timestamp = now or _utcnow()
        self._lock_owner(practice_id, user_id)
        existing = self.get_active_session(
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
            now=timestamp,
            for_update=True,
        )
        if existing is not None:
            return existing
        return self._create_after_owner_lock(
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
            request_reference_date=request_reference_date,
            session_id=None,
            timestamp=timestamp,
        )

    @staticmethod
    def _reject(
        code: BernieSessionEventRejectionCode,
        detail: str,
    ) -> BernieSessionEventResult:
        return BernieSessionEventResult(accepted=False, code=code, detail=detail)

    def _payload_rejection(
        self,
        event_type: BernieSessionEventType,
        payload: dict[str, Any],
    ) -> Optional[BernieSessionEventResult]:
        phi_key = _contains_phi_payload_key(payload)
        if phi_key is not None:
            return self._reject(
                BernieSessionEventRejectionCode.phi_payload_not_allowed,
                f"Event payload key {phi_key!r} is not allowed in Bernie session state.",
            )
        if len(_canonical_payload(payload).encode("utf-8")) > MAX_EVENT_PAYLOAD_BYTES:
            return self._reject(
                BernieSessionEventRejectionCode.event_payload_too_large,
                "Event payload exceeds the bounded Bernie session evidence size.",
            )
        allowed_keys = _DURABLE_EVENT_PAYLOAD_KEYS[event_type]
        unexpected_keys = sorted(set(payload) - allowed_keys)
        if unexpected_keys or not all(
            _is_structured_payload_value(value) for value in payload.values()
        ):
            return self._reject(
                BernieSessionEventRejectionCode.event_payload_not_structured,
                "Event payload must contain only bounded structured codes and coordinates.",
            )
        return None

    def _existing_event_result(
        self,
        *,
        session_row: BernieBookingSession,
        event_id: Optional[str],
        idempotency_key_hash: Optional[str],
        payload_hash: str,
    ) -> Optional[BernieSessionEventResult]:
        conditions = []
        if idempotency_key_hash is not None:
            conditions.append(
                BernieSessionEventRow.idempotency_key_hash == idempotency_key_hash
            )
        if event_id is not None:
            conditions.append(BernieSessionEventRow.event_id == event_id)
        if not conditions:
            return None
        existing = (
            self.db.query(BernieSessionEventRow)
            .filter(
                BernieSessionEventRow.session_id == session_row.session_id,
                or_(*conditions),
            )
            .order_by(BernieSessionEventRow.session_revision)
            .first()
        )
        if existing is None:
            return None
        idempotent_match = (
            idempotency_key_hash is not None
            and existing.idempotency_key_hash == idempotency_key_hash
        ) or (
            idempotency_key_hash is None
            and event_id is not None
            and existing.event_id == event_id
        )
        if idempotent_match and hmac.compare_digest(existing.payload_hash, payload_hash):
            return BernieSessionEventResult(
                accepted=True,
                session=self._record_from_row(session_row),
                event=self._event_from_row(existing),
            )
        return self._reject(
            BernieSessionEventRejectionCode.idempotency_conflict,
            "Event idempotency identity was replayed with a different payload.",
        )

    def _locked_owned_session(
        self,
        *,
        session_id: str,
        practice_id: uuid.UUID,
        user_id: uuid.UUID,
        surface_id: str,
        timestamp: datetime,
    ) -> tuple[Optional[BernieBookingSession], Optional[BernieSessionEventResult]]:
        row = self._session_query(session_id, for_update=True).one_or_none()
        if row is None:
            return None, self._reject(
                BernieSessionEventRejectionCode.session_not_found,
                "Bernie session was not found.",
            )
        if row.practice_id != practice_id or row.staff_user_id != user_id or row.surface_id != surface_id:
            return None, self._reject(
                BernieSessionEventRejectionCode.session_owner_mismatch,
                "Bernie session belongs to a different practice, staff user, or diary surface.",
            )
        if _as_aware_utc(row.expires_at) <= timestamp:
            return None, self._reject(
                BernieSessionEventRejectionCode.session_expired,
                "Bernie session recovery window has expired.",
            )
        return row, None

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
        timestamp = occurred_at or _utcnow()
        row, rejection = self._locked_owned_session(
            session_id=session_id,
            practice_id=practice_id,
            user_id=user_id,
            surface_id=surface_id,
            timestamp=timestamp,
        )
        if rejection is not None or row is None:
            return rejection

        event_payload = payload or {}
        payload_rejection = self._payload_rejection(event_type, event_payload)
        if payload_rejection is not None:
            return payload_rejection
        canonical_hash = _sha256_text(_canonical_payload({
            "event_type": event_type.value,
            "expected_revision": expected_revision,
            "payload": event_payload,
        }))
        identity_hash = _hmac_identity(idempotency_key, self.secret) if idempotency_key else None
        existing = self._existing_event_result(
            session_row=row,
            event_id=event_id,
            idempotency_key_hash=identity_hash,
            payload_hash=canonical_hash,
        )
        if existing is not None:
            return existing

        if expected_revision < row.revision:
            return self._reject(
                BernieSessionEventRejectionCode.stale_session_revision,
                "Bernie session event was based on an older session revision.",
            )
        if expected_revision > row.revision:
            return self._reject(
                BernieSessionEventRejectionCode.future_session_revision,
                "Bernie session event skipped the current session revision.",
            )
        transition = validate_session_event(BernieSessionState(row.state), event_type)
        if not transition.allowed:
            return self._reject(
                BernieSessionEventRejectionCode(transition.reason_code),
                transition.detail or "Event is not allowed.",
            )

        event = BernieSessionEvent(
            event_id=event_id or uuid.uuid4().hex,
            session_id=session_id,
            event_type=event_type,
            turn_index=row.turn_count,
            occurred_at=timestamp,
            expected_revision=expected_revision,
            idempotency_key=None,
            payload=deepcopy(event_payload),
        )
        current = self._record_from_row(row)
        updated = InMemoryBernieSessionStore._apply_client_transition(
            current,
            event,
            transition.target_state,
        )
        self.db.add(BernieSessionEventRow(
            practice_id=practice_id,
            session_id=session_id,
            event_id=event.event_id,
            event_type=event.event_type.value,
            session_revision=updated.revision,
            turn_index=event.turn_index,
            occurred_at=timestamp,
            expected_revision=expected_revision,
            idempotency_key_hash=identity_hash,
            payload_hash=canonical_hash,
            payload=deepcopy(event_payload),
        ))
        self._apply_record_to_row(row, updated, timestamp=timestamp)
        self.db.flush()
        return BernieSessionEventResult(
            accepted=True,
            session=self._record_from_row(row),
            event=event,
        )

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
        timestamp = occurred_at or _utcnow()
        row = self._session_query(session_id, for_update=True).one_or_none()
        if row is None:
            return self._reject(
                BernieSessionEventRejectionCode.session_not_found,
                "Bernie session was not found.",
            )
        if _as_aware_utc(row.expires_at) <= timestamp:
            return self._reject(
                BernieSessionEventRejectionCode.session_expired,
                "Bernie session recovery window has expired.",
            )
        event_payload = payload or {}
        payload_rejection = self._payload_rejection(event_type, event_payload)
        if payload_rejection is not None:
            return payload_rejection
        canonical_hash = _sha256_text(_canonical_payload({
            "event_type": event_type.value,
            "target_state": target_state.value,
            "expected_revision": expected_revision,
            "payload": event_payload,
        }))
        identity_hash = _hmac_identity(idempotency_key, self.secret) if idempotency_key else None
        existing = self._existing_event_result(
            session_row=row,
            event_id=event_id,
            idempotency_key_hash=identity_hash,
            payload_hash=canonical_hash,
        )
        if existing is not None:
            return existing

        if expected_revision is not None:
            if expected_revision < row.revision:
                return self._reject(
                    BernieSessionEventRejectionCode.stale_session_revision,
                    "Bernie session outcome was based on an older session revision.",
                )
            if expected_revision > row.revision:
                return self._reject(
                    BernieSessionEventRejectionCode.future_session_revision,
                    "Bernie session outcome skipped the current session revision.",
                )
        current_state = BernieSessionState(row.state)
        allowed_targets = SERVER_OUTCOME_EVENT_TARGETS.get(current_state, {}).get(event_type)
        if allowed_targets is None or target_state not in allowed_targets:
            return self._reject(
                BernieSessionEventRejectionCode.event_not_allowed_in_state,
                f"Server outcome {event_type.value} cannot advance {current_state.value} to {target_state.value}.",
            )

        event = BernieSessionEvent(
            event_id=event_id or uuid.uuid4().hex,
            session_id=session_id,
            event_type=event_type,
            turn_index=row.turn_count,
            occurred_at=timestamp,
            expected_revision=expected_revision,
            idempotency_key=None,
            payload=deepcopy(event_payload),
        )
        current = self._record_from_row(row)
        updated = current.model_copy(update={
            "state": target_state,
            "revision": current.revision + 1,
            "events": [*current.events, event],
            "last_event_id": event.event_id,
            "updated_at": timestamp,
        }, deep=True)
        if event_type is BernieSessionEventType.proposal_outcome:
            candidate_id = event.payload.get("candidate_freshness_id")
            proposal_id = event.payload.get("proposal_freshness_id")
            identity_updates: dict[str, Any] = {}
            if isinstance(candidate_id, str):
                identity_updates["candidate_freshness_ids"] = [candidate_id]
            if isinstance(proposal_id, str):
                identity_updates["staged_proposal_freshness_id"] = proposal_id
            for payload_key, record_key in (
                ("patient_id", "patient_id"),
                ("practitioner_id", "practitioner_id"),
            ):
                value = event.payload.get(payload_key)
                if isinstance(value, str) and value:
                    try:
                        identity_updates[record_key] = uuid.UUID(value)
                    except ValueError:
                        pass
            if identity_updates:
                updated = updated.model_copy(update=identity_updates, deep=True)

        self.db.add(BernieSessionEventRow(
            practice_id=self.practice_id,
            session_id=session_id,
            event_id=event.event_id,
            event_type=event.event_type.value,
            session_revision=updated.revision,
            turn_index=event.turn_index,
            occurred_at=timestamp,
            expected_revision=expected_revision,
            idempotency_key_hash=identity_hash,
            payload_hash=canonical_hash,
            payload=deepcopy(event_payload),
        ))
        self._apply_record_to_row(row, updated, timestamp=timestamp)
        self.db.flush()
        return BernieSessionEventResult(
            accepted=True,
            session=self._record_from_row(row),
            event=event,
        )

    def advance_server_state(
        self,
        *,
        session_id: str,
        target_state: BernieSessionState,
    ) -> BernieSessionEventResult:
        row = self._session_query(session_id, for_update=True).one_or_none()
        if row is None:
            return self._reject(
                BernieSessionEventRejectionCode.session_not_found,
                "Bernie session was not found.",
            )
        timestamp = _utcnow()
        if _as_aware_utc(row.expires_at) <= timestamp:
            return self._reject(
                BernieSessionEventRejectionCode.session_expired,
                "Bernie session recovery window has expired.",
            )
        current_state = BernieSessionState(row.state)
        if target_state not in SERVER_ADVANCE_TARGETS.get(current_state, frozenset()):
            return self._reject(
                BernieSessionEventRejectionCode.event_not_allowed_in_state,
                f"Server cannot advance {current_state.value} to {target_state.value}.",
            )
        row.state = target_state.value
        row.revision += 1
        row.updated_at = timestamp
        if target_state in TERMINAL_STATES:
            row.completed_at = timestamp
            row.expires_at = timestamp + COMPLETED_SESSION_RETENTION
        else:
            row.expires_at = timestamp + INCOMPLETE_SESSION_RECOVERY
        self.db.flush()
        return BernieSessionEventResult(accepted=True, session=self._record_from_row(row))

    def purge_expired_sessions(
        self,
        *,
        now: Optional[datetime] = None,
        limit: int = 500,
    ) -> int:
        if limit < 1 or limit > 1000:
            raise ValueError("Bernie session purge limit must be between 1 and 1000.")
        timestamp = now or _utcnow()
        rows = (
            self.db.query(BernieBookingSession)
            .filter(
                BernieBookingSession.practice_id == self.practice_id,
                BernieBookingSession.expires_at <= timestamp,
            )
            .order_by(BernieBookingSession.expires_at, BernieBookingSession.session_id)
            .with_for_update(skip_locked=True)
            .limit(limit)
            .all()
        )
        for row in rows:
            self.db.delete(row)
        self.db.flush()
        return len(rows)


__all__ = [
    "COMPLETED_SESSION_RETENTION",
    "DatabaseBernieSessionStore",
    "INCOMPLETE_SESSION_RECOVERY",
    "MAX_EVENT_PAYLOAD_BYTES",
    "PHI_PAYLOAD_KEYWORDS",
    "InMemoryBernieSessionStore",
    "build_session_confirmation_binding",
]
