"""Least-privilege PostgreSQL adapter and atomic surface-token rotation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.application_auth_persistence import (
    PostgresApplicationAuthRuntime,
    _TransactionalAuditBuffer,
)
from app.services.application_auth_runtime import (
    SURFACE_AUDIENCE,
    ApplicationAuthRuntime,
    AuthAuditDecision,
    AuthAuditEventType,
    AuthRuntimeDenied,
    InMemoryAuthoredSyntheticStore,
    SessionStatus,
    Surface,
    SurfaceSessionRecord,
    SyntheticPrincipal,
    CreatedApplicationSession,
)


_PrincipalKey = tuple[str, str]


def _hash_reference(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise AuthRuntimeDenied("opaque_value_required")
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


@dataclass(frozen=True)
class RotatedSurfaceSession:
    surface_session_value: str
    surface: Surface
    parent_generation: int
    surface_idle_expires_at: datetime


class ApplicationAuthTransportRuntime(ApplicationAuthRuntime):
    """Narrow child policy for atomic same-surface bearer rotation."""

    def rotate_surface_session(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> RotatedSurfaceSession:
        now = self._now()
        current_hash = _hash_reference(surface_session_value)
        with self._store.lock:
            try:
                self._require_surface_binding(surface, origin, audience)
                parent, current = self._active_surface_records(
                    surface_hash=current_hash,
                    expected_surface=surface,
                    expected_origin=origin,
                    expected_audience=audience,
                    now=now,
                )
            except AuthRuntimeDenied as exc:
                self._record_surface_denial(
                    surface_hash=current_hash,
                    requested_surface=surface,
                    now=now,
                    correlation_id=correlation_id,
                    reason=exc.reason_code,
                )
                raise

            replacement_value = self._new_opaque_value("surface")
            replacement_hash = _hash_reference(replacement_value)
            if replacement_hash in self._store.surface_sessions:
                raise AuthRuntimeDenied("opaque_value_collision")

            replacement_idle_expires = min(
                parent.expires_at,
                now + self._idle_ttl,
            )
            refreshed_parent, _ = self._refreshed_records(parent, current, now)
            revoked_current = replace(
                current,
                status=SessionStatus.REVOKED,
                last_observed_at=now,
            )
            replacement = SurfaceSessionRecord(
                surface_reference_hash=replacement_hash,
                parent_session_reference_hash=parent.session_reference_hash,
                surface=surface,
                origin=origin,
                audience=audience,
                parent_generation=parent.generation,
                status=SessionStatus.ACTIVE,
                created_at=now,
                last_observed_at=now,
                idle_expires_at=replacement_idle_expires,
                expires_at=replacement_idle_expires,
            )
            bounded_correlation_id = self._bounded_correlation_id(correlation_id)
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.SESSION_REFRESHED,
                        now=now,
                        correlation_id=bounded_correlation_id,
                        parent=parent,
                        surface=surface.value,
                        action="auth.session.rotate",
                        resource_type="surface_session",
                        decision=AuthAuditDecision.ALLOWED,
                        reason="surface_session_rotated",
                    ),
                    self._event(
                        AuthAuditEventType.SURFACE_BOUND,
                        now=now,
                        correlation_id=bounded_correlation_id,
                        parent=parent,
                        surface=surface.value,
                        action="auth.surface.rotate",
                        resource_type="surface_session",
                        decision=AuthAuditDecision.RECORDED,
                        reason="replacement_surface_bound",
                    ),
                )
            )
            self._store.parent_sessions[parent.session_reference_hash] = (
                refreshed_parent
            )
            self._store.surface_sessions[current_hash] = revoked_current
            self._store.surface_sessions[replacement_hash] = replacement

        return RotatedSurfaceSession(
            surface_session_value=replacement_value,
            surface=surface,
            parent_generation=parent.generation,
            surface_idle_expires_at=replacement_idle_expires,
        )


class RoleScopedPostgresApplicationAuthRuntime(PostgresApplicationAuthRuntime):
    """Use the exact resolver and transaction-local RLS context."""

    def _prepare_transaction(self, db: Session) -> None:
        for setting, value in (
            ("statement_timeout", "5s"),
            ("lock_timeout", "2s"),
            ("idle_in_transaction_session_timeout", "5s"),
            ("row_security", "on"),
        ):
            db.execute(
                text("SELECT set_config(:setting, :value, true)"),
                {"setting": setting, "value": value},
            )

    def _bind_practice_context(
        self,
        db: Session,
        key: _PrincipalKey,
    ) -> None:
        _, practice_ref = key
        db.execute(
            text(
                "SELECT set_config('app.current_practice_ref', :practice_ref, true)"
            ),
            {"practice_ref": practice_ref},
        )

    @staticmethod
    def _resolve_key(
        db: Session,
        reference_kind: str,
        reference_hash: str,
    ) -> _PrincipalKey | None:
        row = db.execute(
            text(
                "SELECT user_ref, practice_ref "
                "FROM public.emr4_resolve_application_auth_principal("
                ":reference_kind, :reference_hash)"
            ),
            {
                "reference_kind": reference_kind,
                "reference_hash": reference_hash,
            },
        ).first()
        return (row.user_ref, row.practice_ref) if row is not None else None

    @classmethod
    def _key_for_parent(
        cls,
        db: Session,
        parent_hash: str,
    ) -> _PrincipalKey | None:
        return cls._resolve_key(db, "parent", parent_hash)

    @classmethod
    def _key_for_surface(
        cls,
        db: Session,
        surface_hash: str,
    ) -> _PrincipalKey | None:
        return cls._resolve_key(db, "surface", surface_hash)

    @classmethod
    def _key_for_grant(
        cls,
        db: Session,
        grant_hash: str,
    ) -> _PrincipalKey | None:
        return cls._resolve_key(db, "exchange", grant_hash)

    def _new_runtime(
        self,
        store: InMemoryAuthoredSyntheticStore,
        audit: _TransactionalAuditBuffer,
    ) -> ApplicationAuthTransportRuntime:
        return ApplicationAuthTransportRuntime(
            store=store,
            audit_sink=audit,
            surface_origins=self._surface_origins,
            clock=self._clock,
            token_source=self._token_source,
            parent_ttl=self._parent_ttl,
            idle_ttl=self._idle_ttl,
            exchange_ttl=self._exchange_ttl,
        )

    def create_session_in_transaction(
        self,
        db: Session,
        *,
        principal: SyntheticPrincipal,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> CreatedApplicationSession:
        """Create one session inside an enclosing security transaction."""

        return self._execute_in_transaction(
            db,
            explicit_key=(principal.user_id, principal.practice_id),
            operation=lambda runtime: runtime.create_session(
                principal=principal,
                surface=surface,
                origin=origin,
                audience=audience,
                correlation_id=correlation_id,
            ),
        )

    def rotate_surface_session(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> RotatedSurfaceSession:
        surface_hash = _hash_reference(surface_session_value)

        def operation(runtime: ApplicationAuthRuntime) -> RotatedSurfaceSession:
            if not isinstance(runtime, ApplicationAuthTransportRuntime):
                raise AuthRuntimeDenied("transport_runtime_required")
            return runtime.rotate_surface_session(
                surface_session_value=surface_session_value,
                surface=surface,
                origin=origin,
                audience=audience,
                correlation_id=correlation_id,
            )

        return self._execute(
            key_lookup=lambda db: self._key_for_surface(db, surface_hash),
            operation=operation,
        )


__all__ = [
    "ApplicationAuthTransportRuntime",
    "RoleScopedPostgresApplicationAuthRuntime",
    "RotatedSurfaceSession",
]
