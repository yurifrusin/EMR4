"""Default-off authored-synthetic shared application-auth transport.

The routes are always present for one stable OpenAPI surface, but their sole
transport dependency fails closed unless a task-scoped authored-synthetic
transport is explicitly injected. No environment setting enables this router.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from app.schemas.application_auth_transport import (
    CsrfResponse,
    ExchangeIssueRequest,
    ExchangeIssueResponse,
    ExchangeRedeemRequest,
    SessionResponse,
    SurfaceRequest,
    SyntheticSessionRequest,
    ValidatedSessionResponse,
)
from app.services.application_auth_transport import (
    ApplicationAuthTransport,
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    PREAUTH_CSRF_MAX_AGE_SECONDS,
    SESSION_COOKIE_NAME,
    TransportAuthenticationFailed,
    TransportAuthenticationUnavailable,
    TransportRequestDenied,
)
from app.services.application_auth_operational_hardening import (
    ApplicationAuthOperationalHardening,
    RequiredTransportDenialAuditUnavailable,
    TransportRateLimited,
)


AUTHENTICATION_FAILED = "application_authentication_failed"
REQUEST_NOT_ADMITTED = "request_not_admitted"
AUTHENTICATION_UNAVAILABLE = "authentication_temporarily_unavailable"
TRANSPORT_UNAVAILABLE = "application_auth_transport_unavailable"
REQUEST_RATE_LIMITED = "request_rate_limited"

_NO_STORE_HEADERS = {
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
    "Referrer-Policy": "no-referrer",
}


def _error_response(
    status_code: int,
    detail: str,
    *,
    extra_headers: dict[str, str] | None = None,
) -> JSONResponse:
    headers = dict(_NO_STORE_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
        headers=headers,
    )


def _denied_response(
    request: Request,
    *,
    status_code: int,
    detail: str,
    reason_code: str,
    extra_headers: dict[str, str] | None = None,
) -> JSONResponse:
    guard = getattr(
        request.state,
        "application_auth_operational_hardening",
        None,
    )
    if not isinstance(guard, ApplicationAuthOperationalHardening):
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            AUTHENTICATION_UNAVAILABLE,
        )
    try:
        guard.record_denial(request, reason_code)
    except RequiredTransportDenialAuditUnavailable:
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            AUTHENTICATION_UNAVAILABLE,
        )
    return _error_response(
        status_code,
        detail,
        extra_headers=extra_headers,
    )


class _ApplicationAuthRoute(APIRoute):
    """Collapse route failures without logging or returning supplied values."""

    def get_route_handler(self) -> Callable[[Request], Awaitable[Response]]:
        original = super().get_route_handler()

        async def guarded(request: Request) -> Response:
            try:
                return await original(request)
            except RequestValidationError:
                return _denied_response(
                    request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=AUTHENTICATION_FAILED,
                    reason_code="transport_request_invalid",
                )
            except TransportRequestDenied:
                return _denied_response(
                    request,
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=REQUEST_NOT_ADMITTED,
                    reason_code="transport_request_not_admitted",
                )
            except TransportRateLimited as exc:
                return _denied_response(
                    request,
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=REQUEST_RATE_LIMITED,
                    reason_code="transport_rate_limited",
                    extra_headers={"Retry-After": str(exc.retry_after_seconds)},
                )
            except TransportAuthenticationUnavailable:
                return _error_response(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    AUTHENTICATION_UNAVAILABLE,
                )
            except TransportAuthenticationFailed:
                return _denied_response(
                    request,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=AUTHENTICATION_FAILED,
                    reason_code="transport_authentication_failed",
                )
        return guarded


def get_application_auth_transport() -> ApplicationAuthTransport:
    """Fail closed until an authored-synthetic transport is explicitly injected."""

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=TRANSPORT_UNAVAILABLE,
        headers=_NO_STORE_HEADERS,
    )


def get_application_auth_operational_hardening(
) -> ApplicationAuthOperationalHardening:
    """Fail closed until the bounded operational guard is explicitly injected."""

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=TRANSPORT_UNAVAILABLE,
        headers=_NO_STORE_HEADERS,
    )


def require_application_auth_operational_admission(
    request: Request,
    guard: ApplicationAuthOperationalHardening = Depends(
        get_application_auth_operational_hardening
    ),
) -> None:
    guard.admit(request)


def _apply_no_store(response: Response) -> None:
    for name, value in _NO_STORE_HEADERS.items():
        response.headers[name] = value


def _set_cookie(
    response: Response,
    *,
    name: str,
    value: str,
    max_age: int | None = None,
) -> None:
    response.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
        partitioned=True,
    )


def _expire_cookie(response: Response, *, name: str) -> None:
    response.set_cookie(
        key=name,
        value="",
        max_age=0,
        expires=0,
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
        partitioned=True,
    )


router = APIRouter(
    prefix="/api/v1/application-auth",
    tags=["application-auth"],
    route_class=_ApplicationAuthRoute,
    dependencies=[Depends(require_application_auth_operational_admission)],
)


@router.post("/csrf", response_model=CsrfResponse)
def issue_csrf(
    body: SurfaceRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> CsrfResponse:
    transport.require_origin(body.surface, origin)
    csrf_token = transport.new_csrf_token()
    _set_cookie(
        response,
        name=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=PREAUTH_CSRF_MAX_AGE_SECONDS,
    )
    _apply_no_store(response)
    return CsrfResponse(csrf_token=csrf_token, surface=body.surface)


@router.post("/synthetic/session", response_model=SessionResponse)
def create_synthetic_session(
    body: SyntheticSessionRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE_NAME),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> SessionResponse:
    admitted_origin = transport.require_origin(body.surface, origin)
    transport.require_csrf(csrf_cookie, csrf_header)
    created, csrf_token = transport.login(
        bootstrap_credential=body.bootstrap_credential,
        surface=body.surface,
        origin=admitted_origin,
        correlation_id=body.correlation_id,
    )
    _set_cookie(
        response,
        name=SESSION_COOKIE_NAME,
        value=created.surface_session_value,
    )
    _set_cookie(response, name=CSRF_COOKIE_NAME, value=csrf_token)
    _apply_no_store(response)
    return SessionResponse(
        surface=created.surface,
        csrf_token=csrf_token,
        surface_idle_expires_at=created.surface_idle_expires_at,
    )


@router.post("/session/validate", response_model=ValidatedSessionResponse)
def validate_session(
    body: SurfaceRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE_NAME),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> ValidatedSessionResponse:
    admitted_origin = transport.require_origin(body.surface, origin)
    transport.require_csrf(csrf_cookie, csrf_header)
    validated = transport.validate(
        surface_session_value=session_cookie or "",
        surface=body.surface,
        origin=admitted_origin,
        correlation_id=body.correlation_id,
    )
    _apply_no_store(response)
    return ValidatedSessionResponse(
        surface=validated.surface,
        current_backend_role=validated.current_backend_role,
        surface_idle_expires_at=validated.surface_idle_expires_at,
    )


@router.post("/session/rotate", response_model=SessionResponse)
def rotate_session(
    body: SurfaceRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE_NAME),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> SessionResponse:
    admitted_origin = transport.require_origin(body.surface, origin)
    transport.require_csrf(csrf_cookie, csrf_header)
    rotated, csrf_token = transport.rotate(
        surface_session_value=session_cookie or "",
        surface=body.surface,
        origin=admitted_origin,
        correlation_id=body.correlation_id,
    )
    _set_cookie(
        response,
        name=SESSION_COOKIE_NAME,
        value=rotated.surface_session_value,
    )
    _set_cookie(response, name=CSRF_COOKIE_NAME, value=csrf_token)
    _apply_no_store(response)
    return SessionResponse(
        surface=rotated.surface,
        csrf_token=csrf_token,
        surface_idle_expires_at=rotated.surface_idle_expires_at,
    )


@router.post("/session/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_session(
    body: SurfaceRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE_NAME),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> Response:
    transport.require_origin(body.surface, origin)
    transport.require_csrf(csrf_cookie, csrf_header)
    transport.logout(
        surface_session_value=session_cookie or "",
        correlation_id=body.correlation_id,
    )
    _expire_cookie(response, name=SESSION_COOKIE_NAME)
    _expire_cookie(response, name=CSRF_COOKIE_NAME)
    _apply_no_store(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/exchange/issue", response_model=ExchangeIssueResponse)
def issue_exchange(
    body: ExchangeIssueRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE_NAME),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> ExchangeIssueResponse:
    source_origin = transport.require_origin(body.source_surface, origin)
    transport.require_csrf(csrf_cookie, csrf_header)
    issued = transport.issue_exchange(
        source_surface_session_value=session_cookie or "",
        source_surface=body.source_surface,
        target_surface=body.target_surface,
        source_origin=source_origin,
        target_origin=body.target_origin,
        state=body.state,
        nonce=body.nonce,
        pkce_challenge=body.pkce_challenge,
        correlation_id=body.correlation_id,
    )
    _apply_no_store(response)
    return ExchangeIssueResponse(
        exchange_code=issued.exchange_code,
        target_surface=issued.target_surface,
        expires_at=issued.expires_at,
    )


@router.post("/exchange/redeem", response_model=SessionResponse)
def redeem_exchange(
    body: ExchangeRedeemRequest,
    response: Response,
    origin: str | None = Header(default=None, alias="Origin"),
    csrf_header: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
    csrf_cookie: str | None = Cookie(default=None, alias=CSRF_COOKIE_NAME),
    transport: ApplicationAuthTransport = Depends(get_application_auth_transport),
) -> SessionResponse:
    target_origin = transport.require_origin(body.target_surface, origin)
    transport.require_csrf(csrf_cookie, csrf_header)
    redeemed, csrf_token = transport.redeem_exchange(
        exchange_code=body.exchange_code,
        source_surface=body.source_surface,
        target_surface=body.target_surface,
        source_origin=body.source_origin,
        target_origin=target_origin,
        state=body.state,
        nonce=body.nonce,
        pkce_verifier=body.pkce_verifier,
        correlation_id=body.correlation_id,
    )
    _set_cookie(
        response,
        name=SESSION_COOKIE_NAME,
        value=redeemed.target_surface_session_value,
    )
    _set_cookie(response, name=CSRF_COOKIE_NAME, value=csrf_token)
    _apply_no_store(response)
    return SessionResponse(
        surface=redeemed.target_surface,
        csrf_token=csrf_token,
        surface_idle_expires_at=redeemed.surface_idle_expires_at,
    )


__all__ = [
    "AUTHENTICATION_FAILED",
    "AUTHENTICATION_UNAVAILABLE",
    "REQUEST_RATE_LIMITED",
    "REQUEST_NOT_ADMITTED",
    "TRANSPORT_UNAVAILABLE",
    "get_application_auth_operational_hardening",
    "get_application_auth_transport",
    "router",
]
