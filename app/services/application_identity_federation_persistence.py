"""Route-free authored-synthetic PostgreSQL federation persistence.

The repository stores only versioned keyed-HMAC references for external
identity material. It is not mounted in FastAPI or GraphQL and intentionally
has no live identity, session, product, Microsoft, HTTP, or secret-management
integration.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.application_identity_federation import (
    ApplicationIdentityFederationAuditEvent,
    ApplicationIdentityFederationBinding,
)
from app.services.application_identity_federation import (
    AUTHORED_SYNTHETIC_DATA_CLASS,
    FEDERATION_PROVIDER,
    POLICY_VERSION,
    ExternalIdentityBinding,
    FederationReferenceHasher,
)


_SYNTHETIC_REF = re.compile(r"^synthetic-[a-z0-9-]{1,64}$")
_SYNTHETIC_ISSUER = re.compile(
    r"^https://login\.microsoftonline\.invalid/"
    r"(?P<tenant>synthetic-[a-z0-9-]{1,64})/v2\.0$"
)


class FederationPersistenceDenied(RuntimeError):
    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


class FederationPersistenceAuditUnavailable(RuntimeError):
    pass


class PostgresFederationBindingRepository:
    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        reference_hasher: FederationReferenceHasher,
        clock: Callable[[], datetime],
    ) -> None:
        self._session_factory = session_factory
        self._reference_hasher = reference_hasher
        self._clock = clock

    def create_binding(
        self,
        *,
        binding: ExternalIdentityBinding,
        issuer: str,
        subject: str,
        operation_ref: str,
        correlation_ref: str,
    ) -> ExternalIdentityBinding:
        self._validate_operation(operation_ref, correlation_ref)
        self._validate_issuer_subject(
            issuer=issuer,
            tenant_id=binding.tenant_id,
            subject=subject,
        )
        if binding.status != "active" or binding.version != 1:
            raise FederationPersistenceDenied("new_binding_must_be_active_version_one")

        references = self._references(
            provider=binding.provider,
            issuer=issuer,
            tenant_id=binding.tenant_id,
            object_id=binding.object_id,
            subject=subject,
            correlation_ref=correlation_ref,
        )
        now = self._clock()
        try:
            with self._session_factory() as db:
                with db.begin():
                    db.add(
                        ApplicationIdentityFederationBinding(
                            binding_ref=binding.binding_ref,
                            provider=binding.provider,
                            issuer_reference_hmac=references["issuer"],
                            tenant_reference_hmac=references["tenant"],
                            object_reference_hmac=references["object"],
                            subject_reference_hmac=references["subject"],
                            user_ref=binding.user_ref,
                            practice_ref=binding.practice_ref,
                            status="active",
                            version=1,
                            created_at=now,
                            updated_at=now,
                            revoked_at=None,
                            data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
                        )
                    )
                    db.flush()
                    self._persist_audit(
                        db,
                        operation_ref=operation_ref,
                        correlation_reference_hmac=references["correlation"],
                        external_reference_hmac=references["external"],
                        binding_ref=binding.binding_ref,
                        user_ref=binding.user_ref,
                        practice_ref=binding.practice_ref,
                        event_type="federation.binding_created",
                        decision="recorded",
                        reason_code="binding_created",
                        occurred_at=now,
                    )
        except FederationPersistenceAuditUnavailable:
            raise
        except IntegrityError:
            raise FederationPersistenceDenied("binding_conflict") from None
        except SQLAlchemyError:
            raise FederationPersistenceDenied("persistence_unavailable") from None
        return binding

    def resolve_active_binding(
        self,
        *,
        provider: str,
        issuer: str,
        tenant_id: str,
        object_id: str,
        operation_ref: str,
        correlation_ref: str,
    ) -> tuple[ExternalIdentityBinding, ...]:
        self._validate_operation(operation_ref, correlation_ref)
        self._validate_issuer_subject(
            issuer=issuer,
            tenant_id=tenant_id,
            subject="synthetic-lookup-subject",
        )
        _require_synthetic_ref(object_id, "object_id")
        references = self._references(
            provider=provider,
            issuer=issuer,
            tenant_id=tenant_id,
            object_id=object_id,
            subject="synthetic-lookup-subject",
            correlation_ref=correlation_ref,
        )
        now = self._clock()
        try:
            with self._session_factory() as db:
                with db.begin():
                    rows = tuple(
                        db.scalars(
                            select(ApplicationIdentityFederationBinding)
                            .where(
                                ApplicationIdentityFederationBinding.provider
                                == provider,
                                ApplicationIdentityFederationBinding.issuer_reference_hmac
                                == references["issuer"],
                                ApplicationIdentityFederationBinding.tenant_reference_hmac
                                == references["tenant"],
                                ApplicationIdentityFederationBinding.object_reference_hmac
                                == references["object"],
                            )
                            .order_by(ApplicationIdentityFederationBinding.id)
                        )
                    )
                    active = tuple(row for row in rows if row.status == "active")
                    admitted = len(active) == 1 and len(rows) == 1
                    selected = active[0] if admitted else None
                    self._persist_audit(
                        db,
                        operation_ref=operation_ref,
                        correlation_reference_hmac=references["correlation"],
                        external_reference_hmac=references["external"],
                        binding_ref=selected.binding_ref if selected else None,
                        user_ref=selected.user_ref if selected else None,
                        practice_ref=selected.practice_ref if selected else None,
                        event_type=(
                            "federation.binding_resolved"
                            if admitted
                            else "federation.binding_rejected"
                        ),
                        decision="allowed" if admitted else "denied",
                        reason_code=(
                            "active_binding_resolved"
                            if admitted
                            else "active_binding_required"
                        ),
                        occurred_at=now,
                    )
                    if selected is None:
                        return ()
                    return (
                        ExternalIdentityBinding(
                            provider=selected.provider,
                            tenant_id=tenant_id,
                            object_id=object_id,
                            binding_ref=selected.binding_ref,
                            user_ref=selected.user_ref,
                            practice_ref=selected.practice_ref,
                            status=selected.status,
                            version=int(selected.version),
                        ),
                    )
        except FederationPersistenceAuditUnavailable:
            raise
        except SQLAlchemyError:
            raise FederationPersistenceDenied("persistence_unavailable") from None

    def revoke_binding(
        self,
        *,
        binding_ref: str,
        expected_version: int,
        operation_ref: str,
        correlation_ref: str,
    ) -> int:
        _require_synthetic_ref(binding_ref, "binding_ref")
        self._validate_operation(operation_ref, correlation_ref)
        now = self._clock()
        try:
            with self._session_factory() as db:
                with db.begin():
                    row = db.scalar(
                        select(ApplicationIdentityFederationBinding)
                        .where(
                            ApplicationIdentityFederationBinding.binding_ref
                            == binding_ref
                        )
                        .with_for_update()
                    )
                    if row is None:
                        raise FederationPersistenceDenied("binding_not_found")
                    if row.status != "active":
                        raise FederationPersistenceDenied("binding_not_active")
                    if int(row.version) != expected_version:
                        raise FederationPersistenceDenied("binding_version_mismatch")
                    row.status = "revoked"
                    row.version = expected_version + 1
                    row.revoked_at = now
                    row.updated_at = now
                    external_reference = self._reference_hasher.component_reference(
                        label="binding",
                        value=binding_ref,
                    )
                    self._persist_audit(
                        db,
                        operation_ref=operation_ref,
                        correlation_reference_hmac=(
                            self._reference_hasher.component_reference(
                                label="correlation",
                                value=correlation_ref,
                            )
                        ),
                        external_reference_hmac=external_reference,
                        binding_ref=row.binding_ref,
                        user_ref=row.user_ref,
                        practice_ref=row.practice_ref,
                        event_type="federation.binding_revoked",
                        decision="recorded",
                        reason_code="binding_revoked",
                        occurred_at=now,
                    )
                    db.flush()
                    return int(row.version)
        except (FederationPersistenceDenied, FederationPersistenceAuditUnavailable):
            raise
        except SQLAlchemyError:
            raise FederationPersistenceDenied("persistence_unavailable") from None

    def _references(
        self,
        *,
        provider: str,
        issuer: str,
        tenant_id: str,
        object_id: str,
        subject: str,
        correlation_ref: str,
    ) -> dict[str, str]:
        if provider != FEDERATION_PROVIDER:
            raise FederationPersistenceDenied("provider_mismatch")
        return {
            "issuer": self._reference_hasher.component_reference(
                label="issuer", value=issuer
            ),
            "tenant": self._reference_hasher.component_reference(
                label="tenant", value=tenant_id
            ),
            "object": self._reference_hasher.component_reference(
                label="object", value=object_id
            ),
            "subject": self._reference_hasher.component_reference(
                label="subject", value=subject
            ),
            "correlation": self._reference_hasher.component_reference(
                label="correlation", value=correlation_ref
            ),
            "external": self._reference_hasher.reference(
                provider=provider,
                tenant_id=tenant_id,
                object_id=object_id,
            ),
        }

    def _persist_audit(
        self,
        db: Session,
        *,
        operation_ref: str,
        correlation_reference_hmac: str,
        external_reference_hmac: str,
        binding_ref: str | None,
        user_ref: str | None,
        practice_ref: str | None,
        event_type: str,
        decision: str,
        reason_code: str,
        occurred_at: datetime,
    ) -> None:
        db.add(
            ApplicationIdentityFederationAuditEvent(
                operation_ref=operation_ref,
                correlation_reference_hmac=correlation_reference_hmac,
                external_reference_hmac=external_reference_hmac,
                binding_ref=binding_ref,
                user_ref=user_ref,
                practice_ref=practice_ref,
                provider=FEDERATION_PROVIDER,
                event_type=event_type,
                decision=decision,
                reason_code=reason_code,
                policy_version=POLICY_VERSION,
                occurred_at=occurred_at,
                data_class=AUTHORED_SYNTHETIC_DATA_CLASS,
            )
        )
        self._before_audit_flush()
        try:
            db.flush()
        except SQLAlchemyError:
            raise FederationPersistenceAuditUnavailable(
                "required federation persistence audit unavailable"
            ) from None

    def _before_audit_flush(self) -> None:
        """Acceptance seam for proving audit/state transaction rollback."""

    @staticmethod
    def _validate_operation(operation_ref: str, correlation_ref: str) -> None:
        _require_synthetic_ref(operation_ref, "operation_ref")
        _require_synthetic_ref(correlation_ref, "correlation_ref")

    @staticmethod
    def _validate_issuer_subject(
        *,
        issuer: str,
        tenant_id: str,
        subject: str,
    ) -> None:
        _require_synthetic_ref(tenant_id, "tenant_id")
        _require_synthetic_ref(subject, "subject")
        match = _SYNTHETIC_ISSUER.fullmatch(issuer)
        if match is None or match.group("tenant") != tenant_id:
            raise FederationPersistenceDenied("tenant_specific_issuer_required")


def _require_synthetic_ref(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not _SYNTHETIC_REF.fullmatch(value):
        raise ValueError(f"{field_name} must be an authored-synthetic reference")


__all__ = [
    "FederationPersistenceAuditUnavailable",
    "FederationPersistenceDenied",
    "PostgresFederationBindingRepository",
]
