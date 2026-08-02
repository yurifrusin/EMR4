"""Default-off application-session authorization for one product read."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Callable, Mapping

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.tenancy import Practitioner, User
from app.services.application_auth_role_runtime import (
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (
    SURFACE_AUDIENCE,
    AuthRuntimeDenied,
    RequiredAuditUnavailable,
    Surface,
    SyntheticPrincipal,
    ValidatedSurfaceContext,
)
from app.services.application_auth_transport import (
    ApplicationAuthTransport,
    TransportRequestDenied,
)


_SYNTHETIC_REFERENCE = re.compile(r"^synthetic-[a-z0-9-]{1,64}$")


class ProductReadRequestDenied(RuntimeError):
    """Exact origin or CSRF admission failed."""


class ProductReadAuthenticationFailed(RuntimeError):
    """Session or current product-principal truth failed closed."""


class ProductReadAuthorizationFailed(RuntimeError):
    """An authenticated request is outside the fixed endpoint policy."""


class ProductReadUnavailable(RuntimeError):
    """Required database or audit work was unavailable."""


@dataclass(frozen=True)
class SyntheticProductPrincipalBinding:
    user_ref: str
    practice_ref: str
    user_id: uuid.UUID
    practice_id: uuid.UUID
    practitioner_ref: str | None = None
    practitioner_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        _require_synthetic_reference(self.user_ref, "user_ref")
        _require_synthetic_reference(self.practice_ref, "practice_ref")
        if not isinstance(self.user_id, uuid.UUID):
            raise TypeError("user_id must be a UUID")
        if not isinstance(self.practice_id, uuid.UUID):
            raise TypeError("practice_id must be a UUID")
        if (self.practitioner_ref is None) != (self.practitioner_id is None):
            raise ValueError("practitioner reference and UUID must be paired")
        if self.practitioner_ref is not None:
            _require_synthetic_reference(
                self.practitioner_ref,
                "practitioner_ref",
            )
            if not isinstance(self.practitioner_id, uuid.UUID):
                raise TypeError("practitioner_id must be a UUID")


class SyntheticProductPrincipalRegistry:
    """Immutable process-local mapping; never a real identity registry."""

    def __init__(
        self,
        bindings: tuple[SyntheticProductPrincipalBinding, ...],
    ) -> None:
        entries: dict[tuple[str, str], SyntheticProductPrincipalBinding] = {}
        for binding in bindings:
            key = (binding.user_ref, binding.practice_ref)
            if key in entries:
                raise ValueError("duplicate synthetic product principal binding")
            entries[key] = binding
        if not entries:
            raise ValueError("at least one synthetic product binding is required")
        self._entries: Mapping[
            tuple[str, str],
            SyntheticProductPrincipalBinding,
        ] = entries

    def resolve(
        self,
        *,
        user_ref: str,
        practice_ref: str,
    ) -> SyntheticProductPrincipalBinding | None:
        return self._entries.get((user_ref, practice_ref))


@dataclass
class AuthorizedPractitionerDirectoryContext:
    db: Session
    current_user: User
    session_context: ValidatedSurfaceContext
    fresh_principal: SyntheticPrincipal
    surface_session_value: str
    correlation_id: str | None


class ApplicationSessionPractitionerDirectoryBridge:
    """Authorize one active practitioner-directory read before data access."""

    def __init__(
        self,
        *,
        runtime: RoleScopedPostgresApplicationAuthRuntime,
        product_session_factory: Callable[[], Session],
        principal_registry: SyntheticProductPrincipalRegistry,
        surface_origins: Mapping[Surface, str],
    ) -> None:
        if set(surface_origins) != set(Surface):
            raise ValueError("all three surface origins are required")
        self.runtime = runtime
        self.product_session_factory = product_session_factory
        self.principal_registry = principal_registry
        self.surface_origins = dict(surface_origins)

    def open_context(
        self,
        *,
        surface_session_value: str,
        csrf_cookie: str | None,
        csrf_header: str | None,
        surface: Surface,
        origin: str | None,
        correlation_id: str | None,
    ) -> AuthorizedPractitionerDirectoryContext:
        expected_origin = self.surface_origins[surface]
        if origin != expected_origin:
            raise ProductReadRequestDenied()
        try:
            ApplicationAuthTransport.require_csrf(csrf_cookie, csrf_header)
        except TransportRequestDenied:
            raise ProductReadRequestDenied() from None

        try:
            validated = self.runtime.validate_surface_session(
                surface_session_value=surface_session_value,
                surface=surface,
                origin=expected_origin,
                audience=SURFACE_AUDIENCE,
                correlation_id=correlation_id,
            )
        except RequiredAuditUnavailable:
            try:
                identifiable = self.runtime.is_surface_session_identifiable(
                    surface_session_value
                )
            except (AuthRuntimeDenied, SQLAlchemyError):
                raise ProductReadUnavailable() from None
            if not identifiable:
                raise ProductReadAuthenticationFailed() from None
            raise ProductReadUnavailable() from None
        except SQLAlchemyError:
            raise ProductReadUnavailable() from None
        except AuthRuntimeDenied:
            raise ProductReadAuthenticationFailed() from None

        binding = self.principal_registry.resolve(
            user_ref=validated.user_id,
            practice_ref=validated.practice_id,
        )
        db = self.product_session_factory()
        try:
            current_user, fresh_principal, active = self._load_fresh_principal(
                db=db,
                validated=validated,
                binding=binding,
            )
            authorized = self.runtime.authorize_practitioner_directory_read(
                surface_session_value=surface_session_value,
                surface=surface,
                origin=expected_origin,
                fresh_principal=fresh_principal,
                fresh_user_active=active,
                resource_practice_id=validated.practice_id,
                active_only=True,
                audience=SURFACE_AUDIENCE,
                correlation_id=correlation_id,
            )
        except RequiredAuditUnavailable:
            db.close()
            raise ProductReadUnavailable() from None
        except SQLAlchemyError:
            db.close()
            raise ProductReadUnavailable() from None
        except AuthRuntimeDenied:
            db.close()
            raise ProductReadAuthenticationFailed() from None
        except Exception:
            db.close()
            raise

        if current_user is None or fresh_principal is None:
            db.close()
            raise ProductReadAuthenticationFailed()
        return AuthorizedPractitionerDirectoryContext(
            db=db,
            current_user=current_user,
            session_context=authorized,
            fresh_principal=fresh_principal,
            surface_session_value=surface_session_value,
            correlation_id=correlation_id,
        )

    def require_active_directory(
        self,
        context: AuthorizedPractitionerDirectoryContext,
        *,
        active_only: bool,
    ) -> None:
        if active_only:
            return
        try:
            self.runtime.authorize_practitioner_directory_read(
                surface_session_value=context.surface_session_value,
                surface=context.session_context.surface,
                origin=context.session_context.origin,
                fresh_principal=context.fresh_principal,
                fresh_user_active=True,
                resource_practice_id=context.session_context.practice_id,
                active_only=False,
                audience=SURFACE_AUDIENCE,
                correlation_id=context.correlation_id,
            )
        except RequiredAuditUnavailable:
            raise ProductReadUnavailable() from None
        except SQLAlchemyError:
            raise ProductReadUnavailable() from None
        except AuthRuntimeDenied:
            raise ProductReadAuthorizationFailed() from None
        raise AssertionError("inactive directory policy must deny")

    @staticmethod
    def _load_fresh_principal(
        *,
        db: Session,
        validated: ValidatedSurfaceContext,
        binding: SyntheticProductPrincipalBinding | None,
    ) -> tuple[User | None, SyntheticPrincipal | None, bool]:
        if binding is None:
            return None, None, False
        row = db.execute(
            select(
                User.id,
                User.practice_id,
                User.role,
                User.practitioner_id,
                User.is_active,
            ).where(
                User.id == binding.user_id,
                User.practice_id == binding.practice_id,
            )
        ).one_or_none()
        if row is None:
            return None, None, False
        user = User(
            id=row.id,
            practice_id=row.practice_id,
            role=row.role,
            practitioner_id=row.practitioner_id,
            is_active=row.is_active,
        )
        link_matches = row.practitioner_id == binding.practitioner_id
        if binding.practitioner_id is not None:
            practitioner = db.execute(
                select(Practitioner.id).where(
                    Practitioner.id == binding.practitioner_id,
                    Practitioner.practice_id == binding.practice_id,
                    Practitioner.is_active.is_(True),
                )
            ).one_or_none()
            link_matches = link_matches and practitioner is not None
        fresh = SyntheticPrincipal(
            user_id=binding.user_ref,
            practice_id=binding.practice_ref,
            current_backend_role=row.role.value,
            practitioner_id=(
                binding.practitioner_ref if link_matches else None
            ),
        )
        exact_mapping = (
            validated.user_id == binding.user_ref
            and validated.practice_id == binding.practice_ref
            and validated.practitioner_id == binding.practitioner_ref
            and validated.current_backend_role == row.role.value
            and link_matches
        )
        return user, (fresh if exact_mapping else None), bool(row.is_active)


def _require_synthetic_reference(value: str, label: str) -> None:
    if not isinstance(value, str) or not _SYNTHETIC_REFERENCE.fullmatch(value):
        raise ValueError(f"{label} must be a bounded synthetic reference")


__all__ = [
    "ApplicationSessionPractitionerDirectoryBridge",
    "AuthorizedPractitionerDirectoryContext",
    "ProductReadAuthenticationFailed",
    "ProductReadAuthorizationFailed",
    "ProductReadRequestDenied",
    "ProductReadUnavailable",
    "SyntheticProductPrincipalBinding",
    "SyntheticProductPrincipalRegistry",
]
