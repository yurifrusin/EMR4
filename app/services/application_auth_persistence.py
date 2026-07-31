"""Route-free PostgreSQL unit of work for shared application authentication.

The accepted :class:`ApplicationAuthRuntime` remains the only policy engine.
This adapter locks one principal-generation row, hydrates that principal's
hash-only state, executes one runtime operation, and commits the required audit
batch and resulting state in the same PostgreSQL transaction.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Callable, Mapping, Sequence, TypeVar

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.application_auth import (
    ApplicationAuthAuditEvent,
    ApplicationAuthExchangeGrant,
    ApplicationAuthParentSession,
    ApplicationAuthPrincipalGeneration,
    ApplicationAuthSurfaceSession,
)
from app.services.application_auth_runtime import (
    AUTHORED_SYNTHETIC_DATA_CLASS,
    EXCHANGE_AUDIENCE,
    MAX_EXCHANGE_TTL,
    MAX_IDLE_TTL,
    MAX_PARENT_TTL,
    SURFACE_AUDIENCE,
    ApplicationAuthRuntime,
    AuthAuditEvent,
    AuthRuntimeDenied,
    CreatedApplicationSession,
    ExchangeGrantRecord,
    InMemoryAuthoredSyntheticStore,
    IssuedExchangeGrant,
    ParentSessionRecord,
    RedeemedExchangeGrant,
    RequiredAuditUnavailable,
    SessionStatus,
    Surface,
    SurfaceSessionRecord,
    SyntheticPrincipal,
    ValidatedSurfaceContext,
)


_ResultT = TypeVar("_ResultT")
_PrincipalKey = tuple[str, str]


def _hash_opaque_value(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise AuthRuntimeDenied("opaque_value_required")
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


class _TransactionalAuditBuffer:
    """Collect exact runtime batches until the database transaction flushes."""

    def __init__(self) -> None:
        self.events: list[AuthAuditEvent] = []

    def record_batch(self, events: Sequence[AuthAuditEvent]) -> None:
        bounded = tuple(events)
        if not bounded:
            raise ValueError("audit batch must not be empty")
        self.events.extend(bounded)


class PostgresApplicationAuthRuntime:
    """Durable authored-synthetic coordinator with no route or cookie wiring."""

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        surface_origins: Mapping[Surface, str],
        clock: Callable[[], datetime] | None = None,
        token_source: Callable[[str], str] | None = None,
        parent_ttl: timedelta = MAX_PARENT_TTL,
        idle_ttl: timedelta = MAX_IDLE_TTL,
        exchange_ttl: timedelta = MAX_EXCHANGE_TTL,
    ) -> None:
        self._session_factory = session_factory
        self._surface_origins = dict(surface_origins)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_source = token_source
        self._parent_ttl = parent_ttl
        self._idle_ttl = idle_ttl
        self._exchange_ttl = exchange_ttl

        # Validate the frozen construction contract before any database access.
        self._new_runtime(
            InMemoryAuthoredSyntheticStore(
                data_class=AUTHORED_SYNTHETIC_DATA_CLASS
            ),
            _TransactionalAuditBuffer(),
        )

    def create_session(
        self,
        *,
        principal: SyntheticPrincipal,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> CreatedApplicationSession:
        return self._execute(
            explicit_key=(principal.user_id, principal.practice_id),
            operation=lambda runtime: runtime.create_session(
                principal=principal,
                surface=surface,
                origin=origin,
                audience=audience,
                correlation_id=correlation_id,
            ),
        )

    def validate_surface_session(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> ValidatedSurfaceContext:
        surface_hash = _hash_opaque_value(surface_session_value)
        return self._execute(
            key_lookup=lambda db: self._key_for_surface(db, surface_hash),
            operation=lambda runtime: runtime.validate_surface_session(
                surface_session_value=surface_session_value,
                surface=surface,
                origin=origin,
                audience=audience,
                correlation_id=correlation_id,
            ),
        )

    def issue_exchange(
        self,
        *,
        source_surface_session_value: str,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        audience: str = EXCHANGE_AUDIENCE,
        state: str,
        nonce: str,
        pkce_challenge: str,
        correlation_id: str | None = None,
    ) -> IssuedExchangeGrant:
        source_hash = _hash_opaque_value(source_surface_session_value)
        return self._execute(
            key_lookup=lambda db: self._key_for_surface(db, source_hash),
            operation=lambda runtime: runtime.issue_exchange(
                source_surface_session_value=source_surface_session_value,
                source_surface=source_surface,
                target_surface=target_surface,
                source_origin=source_origin,
                target_origin=target_origin,
                audience=audience,
                state=state,
                nonce=nonce,
                pkce_challenge=pkce_challenge,
                correlation_id=correlation_id,
            ),
        )

    def redeem_exchange(
        self,
        *,
        exchange_code: str,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        audience: str = EXCHANGE_AUDIENCE,
        state: str,
        nonce: str,
        pkce_verifier: str,
        correlation_id: str | None = None,
    ) -> RedeemedExchangeGrant:
        grant_hash = _hash_opaque_value(exchange_code)
        return self._execute(
            key_lookup=lambda db: self._key_for_grant(db, grant_hash),
            operation=lambda runtime: runtime.redeem_exchange(
                exchange_code=exchange_code,
                source_surface=source_surface,
                target_surface=target_surface,
                source_origin=source_origin,
                target_origin=target_origin,
                audience=audience,
                state=state,
                nonce=nonce,
                pkce_verifier=pkce_verifier,
                correlation_id=correlation_id,
            ),
        )

    def revoke_parent_session(
        self,
        *,
        parent_session_value: str,
        correlation_id: str | None = None,
        reason: str = "security_reset",
    ) -> None:
        parent_hash = _hash_opaque_value(parent_session_value)
        self._execute(
            key_lookup=lambda db: self._key_for_parent(db, parent_hash),
            operation=lambda runtime: runtime.revoke_parent_session(
                parent_session_value=parent_session_value,
                correlation_id=correlation_id,
                reason=reason,
            ),
        )

    def revoke_surface_session(
        self,
        *,
        surface_session_value: str,
        correlation_id: str | None = None,
        reason: str = "security_reset",
    ) -> None:
        surface_hash = _hash_opaque_value(surface_session_value)
        self._execute(
            key_lookup=lambda db: self._key_for_surface(db, surface_hash),
            operation=lambda runtime: runtime.revoke_surface_session(
                surface_session_value=surface_session_value,
                correlation_id=correlation_id,
                reason=reason,
            ),
        )

    def advance_principal_generation(
        self,
        *,
        principal: SyntheticPrincipal,
        reason: str,
        correlation_id: str | None = None,
    ) -> int:
        return self._execute(
            explicit_key=(principal.user_id, principal.practice_id),
            operation=lambda runtime: runtime.advance_principal_generation(
                principal=principal,
                reason=reason,
                correlation_id=correlation_id,
            ),
        )

    def _execute(
        self,
        *,
        operation: Callable[[ApplicationAuthRuntime], _ResultT],
        explicit_key: _PrincipalKey | None = None,
        key_lookup: Callable[[Session], _PrincipalKey | None] | None = None,
    ) -> _ResultT:
        if (explicit_key is None) == (key_lookup is None):
            raise ValueError("exactly one principal-key source is required")

        denial: AuthRuntimeDenied | None = None
        result: _ResultT | None = None
        with self._session_factory() as db:
            with db.begin():
                self._prepare_transaction(db)
                key = explicit_key if explicit_key is not None else key_lookup(db)
                if key is not None:
                    self._bind_practice_context(db, key)
                    generation_row = self._lock_principal_generation(
                        db,
                        key,
                        create_if_missing=explicit_key is not None,
                    )
                    store = self._load_store(db, key, generation_row)
                else:
                    generation_row = None
                    store = InMemoryAuthoredSyntheticStore(
                        data_class=AUTHORED_SYNTHETIC_DATA_CLASS
                    )

                audit = _TransactionalAuditBuffer()
                runtime = self._new_runtime(store, audit)
                try:
                    result = operation(runtime)
                except AuthRuntimeDenied as exc:
                    denial = exc

                self._persist_audit(db, audit.events)
                if denial is None:
                    if key is None or generation_row is None:
                        raise AuthRuntimeDenied("persistence_principal_required")
                    self._persist_state(db, key, generation_row, store)

        if denial is not None:
            raise denial
        return result  # type: ignore[return-value]

    def _prepare_transaction(self, db: Session) -> None:
        """Hook for a child adapter to apply transaction-local safeguards."""

    def _bind_practice_context(
        self,
        db: Session,
        key: _PrincipalKey,
    ) -> None:
        """Hook for a child adapter to bind forced-RLS practice context."""

    def _new_runtime(
        self,
        store: InMemoryAuthoredSyntheticStore,
        audit: _TransactionalAuditBuffer,
    ) -> ApplicationAuthRuntime:
        return ApplicationAuthRuntime(
            store=store,
            audit_sink=audit,
            surface_origins=self._surface_origins,
            clock=self._clock,
            token_source=self._token_source,
            parent_ttl=self._parent_ttl,
            idle_ttl=self._idle_ttl,
            exchange_ttl=self._exchange_ttl,
        )

    @staticmethod
    def _lock_principal_generation(
        db: Session,
        key: _PrincipalKey,
        *,
        create_if_missing: bool,
    ) -> ApplicationAuthPrincipalGeneration:
        user_ref, practice_ref = key
        if create_if_missing:
            db.execute(
                postgresql_insert(ApplicationAuthPrincipalGeneration)
                .values(
                    practice_ref=practice_ref,
                    user_ref=user_ref,
                    generation=1,
                    data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
                )
                .on_conflict_do_nothing(
                    index_elements=["practice_ref", "user_ref"]
                )
            )
        row = db.execute(
            select(ApplicationAuthPrincipalGeneration)
            .where(
                ApplicationAuthPrincipalGeneration.practice_ref == practice_ref,
                ApplicationAuthPrincipalGeneration.user_ref == user_ref,
            )
            .with_for_update()
        ).scalar_one_or_none()
        if row is None:
            raise AuthRuntimeDenied("persistence_principal_required")
        return row

    @staticmethod
    def _key_for_parent(
        db: Session,
        parent_hash: str,
    ) -> _PrincipalKey | None:
        row = db.execute(
            select(
                ApplicationAuthParentSession.user_ref,
                ApplicationAuthParentSession.practice_ref,
            ).where(
                ApplicationAuthParentSession.session_reference_hash == parent_hash
            )
        ).first()
        return (row.user_ref, row.practice_ref) if row is not None else None

    @staticmethod
    def _key_for_surface(
        db: Session,
        surface_hash: str,
    ) -> _PrincipalKey | None:
        row = db.execute(
            select(
                ApplicationAuthParentSession.user_ref,
                ApplicationAuthParentSession.practice_ref,
            )
            .join(
                ApplicationAuthSurfaceSession,
                and_(
                    ApplicationAuthSurfaceSession.practice_ref
                    == ApplicationAuthParentSession.practice_ref,
                    ApplicationAuthSurfaceSession.parent_session_reference_hash
                    == ApplicationAuthParentSession.session_reference_hash,
                ),
            )
            .where(
                ApplicationAuthSurfaceSession.surface_reference_hash == surface_hash
            )
        ).first()
        return (row.user_ref, row.practice_ref) if row is not None else None

    @staticmethod
    def _key_for_grant(
        db: Session,
        grant_hash: str,
    ) -> _PrincipalKey | None:
        row = db.execute(
            select(
                ApplicationAuthParentSession.user_ref,
                ApplicationAuthParentSession.practice_ref,
            )
            .join(
                ApplicationAuthExchangeGrant,
                and_(
                    ApplicationAuthExchangeGrant.practice_ref
                    == ApplicationAuthParentSession.practice_ref,
                    ApplicationAuthExchangeGrant.parent_session_reference_hash
                    == ApplicationAuthParentSession.session_reference_hash,
                ),
            )
            .where(
                ApplicationAuthExchangeGrant.grant_reference_hash == grant_hash
            )
        ).first()
        return (row.user_ref, row.practice_ref) if row is not None else None

    @staticmethod
    def _load_store(
        db: Session,
        key: _PrincipalKey,
        generation_row: ApplicationAuthPrincipalGeneration,
    ) -> InMemoryAuthoredSyntheticStore:
        user_ref, practice_ref = key
        store = InMemoryAuthoredSyntheticStore(
            data_class=AUTHORED_SYNTHETIC_DATA_CLASS
        )
        store.principal_generations[key] = int(generation_row.generation)

        parent_rows = tuple(
            db.scalars(
                select(ApplicationAuthParentSession)
                .where(
                    ApplicationAuthParentSession.practice_ref == practice_ref,
                    ApplicationAuthParentSession.user_ref == user_ref,
                )
                .order_by(ApplicationAuthParentSession.session_reference_hash)
            )
        )
        parent_hashes: list[str] = []
        for row in parent_rows:
            parent_hashes.append(row.session_reference_hash)
            store.parent_sessions[row.session_reference_hash] = ParentSessionRecord(
                session_reference_hash=row.session_reference_hash,
                principal=SyntheticPrincipal(
                    user_id=row.user_ref,
                    practice_id=row.practice_ref,
                    current_backend_role=row.current_backend_role,
                    practitioner_id=row.practitioner_ref,
                ),
                generation=int(row.generation),
                status=SessionStatus(row.status),
                created_at=row.created_at,
                last_observed_at=row.last_observed_at,
                idle_expires_at=row.idle_expires_at,
                expires_at=row.expires_at,
            )

        if not parent_hashes:
            return store

        for row in db.scalars(
            select(ApplicationAuthSurfaceSession)
            .where(
                ApplicationAuthSurfaceSession.practice_ref == practice_ref,
                ApplicationAuthSurfaceSession.parent_session_reference_hash.in_(
                    parent_hashes
                ),
            )
            .order_by(ApplicationAuthSurfaceSession.surface_reference_hash)
        ):
            store.surface_sessions[row.surface_reference_hash] = (
                SurfaceSessionRecord(
                    surface_reference_hash=row.surface_reference_hash,
                    parent_session_reference_hash=(
                        row.parent_session_reference_hash
                    ),
                    surface=Surface(row.surface),
                    origin=row.origin,
                    audience=row.audience,
                    parent_generation=int(row.parent_generation),
                    status=SessionStatus(row.status),
                    created_at=row.created_at,
                    last_observed_at=row.last_observed_at,
                    idle_expires_at=row.idle_expires_at,
                    expires_at=row.expires_at,
                )
            )

        for row in db.scalars(
            select(ApplicationAuthExchangeGrant)
            .where(
                ApplicationAuthExchangeGrant.practice_ref == practice_ref,
                ApplicationAuthExchangeGrant.parent_session_reference_hash.in_(
                    parent_hashes
                ),
            )
            .order_by(ApplicationAuthExchangeGrant.grant_reference_hash)
        ):
            store.exchange_grants[row.grant_reference_hash] = ExchangeGrantRecord(
                grant_reference_hash=row.grant_reference_hash,
                parent_session_reference_hash=row.parent_session_reference_hash,
                source_surface_reference_hash=row.source_surface_reference_hash,
                parent_generation=int(row.parent_generation),
                source_surface=Surface(row.source_surface),
                target_surface=Surface(row.target_surface),
                source_origin=row.source_origin,
                target_origin=row.target_origin,
                audience=row.audience,
                state_hash=row.state_hash,
                nonce_hash=row.nonce_hash,
                pkce_challenge=row.pkce_challenge,
                issued_at=row.issued_at,
                expires_at=row.expires_at,
                consumed_at=row.consumed_at,
            )
        return store

    @staticmethod
    def _persist_audit(
        db: Session,
        events: Sequence[AuthAuditEvent],
    ) -> None:
        if not events:
            return
        db.add_all(
            ApplicationAuthAuditEvent(
                practice_ref=event.practice_id,
                user_ref=event.user_id,
                current_backend_role=event.current_backend_role,
                event_type=event.event_type.value,
                occurred_at=event.occurred_at,
                correlation_id=event.correlation_id,
                session_reference_hash=event.session_reference_hash,
                surface=event.surface,
                action=event.action,
                resource_type=event.resource_type,
                policy_version=event.policy_version,
                decision=event.decision.value,
                reason_codes=list(event.reason_codes),
                grant_reference_hash=event.grant_reference_hash,
                target_surface=event.target_surface,
                data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
            )
            for event in events
        )
        try:
            db.flush()
        except SQLAlchemyError:
            raise RequiredAuditUnavailable() from None

    def _persist_state(
        self,
        db: Session,
        key: _PrincipalKey,
        generation_row: ApplicationAuthPrincipalGeneration,
        store: InMemoryAuthoredSyntheticStore,
    ) -> None:
        user_ref, practice_ref = key
        snapshot = store.snapshot()
        generations = dict(snapshot.principal_generations)
        if key not in generations:
            raise AuthRuntimeDenied("persistence_generation_required")
        generation_row.generation = generations[key]
        generation_row.updated_at = self._clock()

        parent_practices: dict[str, str] = {}
        for record in snapshot.parent_sessions:
            parent_practices[record.session_reference_hash] = (
                record.principal.practice_id
            )
            db.merge(
                ApplicationAuthParentSession(
                    session_reference_hash=record.session_reference_hash,
                    practice_ref=record.principal.practice_id,
                    user_ref=record.principal.user_id,
                    current_backend_role=record.principal.current_backend_role,
                    practitioner_ref=record.principal.practitioner_id,
                    generation=record.generation,
                    status=record.status.value,
                    data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
                    created_at=record.created_at,
                    last_observed_at=record.last_observed_at,
                    idle_expires_at=record.idle_expires_at,
                    expires_at=record.expires_at,
                )
            )

        for record in snapshot.surface_sessions:
            record_practice = parent_practices[
                record.parent_session_reference_hash
            ]
            db.merge(
                ApplicationAuthSurfaceSession(
                    surface_reference_hash=record.surface_reference_hash,
                    practice_ref=record_practice,
                    parent_session_reference_hash=(
                        record.parent_session_reference_hash
                    ),
                    surface=record.surface.value,
                    origin=record.origin,
                    audience=record.audience,
                    parent_generation=record.parent_generation,
                    status=record.status.value,
                    data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
                    created_at=record.created_at,
                    last_observed_at=record.last_observed_at,
                    idle_expires_at=record.idle_expires_at,
                    expires_at=record.expires_at,
                )
            )

        for record in snapshot.exchange_grants:
            record_practice = parent_practices[
                record.parent_session_reference_hash
            ]
            db.merge(
                ApplicationAuthExchangeGrant(
                    grant_reference_hash=record.grant_reference_hash,
                    practice_ref=record_practice,
                    parent_session_reference_hash=(
                        record.parent_session_reference_hash
                    ),
                    source_surface_reference_hash=(
                        record.source_surface_reference_hash
                    ),
                    parent_generation=record.parent_generation,
                    source_surface=record.source_surface.value,
                    target_surface=record.target_surface.value,
                    source_origin=record.source_origin,
                    target_origin=record.target_origin,
                    audience=record.audience,
                    state_hash=record.state_hash,
                    nonce_hash=record.nonce_hash,
                    pkce_challenge=record.pkce_challenge,
                    issued_at=record.issued_at,
                    expires_at=record.expires_at,
                    consumed_at=record.consumed_at,
                    data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
                )
            )

        try:
            db.flush()
        except SQLAlchemyError:
            raise AuthRuntimeDenied("persistence_write_failed") from None

        if generation_row.practice_ref != practice_ref or generation_row.user_ref != user_ref:
            raise AuthRuntimeDenied("persistence_principal_mismatch")


__all__ = ["PostgresApplicationAuthRuntime"]
