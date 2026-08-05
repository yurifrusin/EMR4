"""Application-session bridge for one default-off Rayleen product read."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping
import uuid

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.tenancy import User
from app.services.application_auth_product_read import (
    ApplicationSessionPractitionerDirectoryBridge,
    ProductReadAuthenticationFailed,
    ProductReadAuthorizationFailed,
    ProductReadRequestDenied,
    ProductReadUnavailable,
    SyntheticProductPrincipalRegistry,
)
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


@dataclass
class AuthorizedRayleenWaitingRoomContext:
    db: Session
    current_user: User
    session_context: ValidatedSurfaceContext
    fresh_principal: SyntheticPrincipal
    surface_session_value: str
    correlation_id: str | None


class ApplicationSessionRayleenWaitingRoomBridge:
    """Authorize one Receptionist-only native-Diary read before row access."""

    def __init__(
        self,
        *,
        runtime: RoleScopedPostgresApplicationAuthRuntime,
        product_session_factory: Callable[[], Session],
        principal_registry: SyntheticProductPrincipalRegistry,
        surface_origins: Mapping[Surface, str],
        allowed_practice_ids: frozenset[uuid.UUID],
    ) -> None:
        if set(surface_origins) != set(Surface):
            raise ValueError("all three surface origins are required")
        if not allowed_practice_ids:
            raise ValueError("at least one authored-synthetic practice is required")
        self.runtime = runtime
        self.product_session_factory = product_session_factory
        self.principal_registry = principal_registry
        self.surface_origins = dict(surface_origins)
        self.allowed_practice_ids = allowed_practice_ids

    def open_context(
        self,
        *,
        surface_session_value: str,
        csrf_cookie: str | None,
        csrf_header: str | None,
        surface: Surface,
        origin: str | None,
        correlation_id: str | None,
    ) -> AuthorizedRayleenWaitingRoomContext:
        expected_origin = self.surface_origins[surface]
        if surface is not Surface.NATIVE_DIARY or origin != expected_origin:
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
        if binding is None:
            raise ProductReadAuthenticationFailed()
        if binding.practice_id not in self.allowed_practice_ids:
            raise ProductReadAuthorizationFailed()

        db = self.product_session_factory()
        try:
            current_user, fresh_principal, active = (
                ApplicationSessionPractitionerDirectoryBridge
                ._load_fresh_principal(
                    db=db,
                    validated=validated,
                    binding=binding,
                )
            )
            authorized = self.runtime.authorize_rayleen_waiting_room_read(
                surface_session_value=surface_session_value,
                surface=surface,
                origin=expected_origin,
                fresh_principal=fresh_principal,
                fresh_user_active=active,
                resource_practice_id=validated.practice_id,
                audience=SURFACE_AUDIENCE,
                correlation_id=correlation_id,
            )
            if current_user is None or fresh_principal is None:
                raise ProductReadAuthenticationFailed()
            db.execute(
                text(
                    "SELECT set_config("
                    "'app.current_practice_id', :practice_id, true)"
                ),
                {"practice_id": str(current_user.practice_id)},
            )
        except RequiredAuditUnavailable:
            db.close()
            raise ProductReadUnavailable() from None
        except SQLAlchemyError:
            db.close()
            raise ProductReadUnavailable() from None
        except AuthRuntimeDenied as exc:
            db.close()
            if exc.reason_code in {
                "receptionist_role_required",
                "native_diary_surface_required",
                "resource_practice_mismatch",
            }:
                raise ProductReadAuthorizationFailed() from None
            raise ProductReadAuthenticationFailed() from None
        except Exception:
            db.close()
            raise

        return AuthorizedRayleenWaitingRoomContext(
            db=db,
            current_user=current_user,
            session_context=authorized,
            fresh_principal=fresh_principal,
            surface_session_value=surface_session_value,
            correlation_id=correlation_id,
        )


__all__ = [
    "ApplicationSessionRayleenWaitingRoomBridge",
    "AuthorizedRayleenWaitingRoomContext",
]
