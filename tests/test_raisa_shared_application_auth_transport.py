"""Focused provider-free tests for the default-off shared-auth transport."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.routers.application_auth import (
    AUTHENTICATION_FAILED,
    AUTHENTICATION_UNAVAILABLE,
    REQUEST_NOT_ADMITTED,
    TRANSPORT_UNAVAILABLE,
    get_application_auth_operational_hardening,
    get_application_auth_transport,
    router,
)
from app.services.application_auth_role_runtime import RotatedSurfaceSession
from app.services.application_auth_runtime import (
    CreatedApplicationSession,
    IssuedExchangeGrant,
    RedeemedExchangeGrant,
    RequiredAuditUnavailable,
    Surface,
    SyntheticPrincipal,
    ValidatedSurfaceContext,
    pkce_s256_challenge,
)
from app.services.application_auth_transport import (
    ApplicationAuthTransport,
    CSRF_COOKIE_NAME,
    OneUseSyntheticBootstrapRegistry,
    SESSION_COOKIE_NAME,
)
from app.services.application_auth_operational_hardening import (
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
    TransportDenialEvent,
)


ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online.synthetic.invalid",
    Surface.NATIVE_DIARY: "https://diary.synthetic.invalid",
}
BOOTSTRAP = "bootstrap." + "b" * 43
SURFACE_ONE = "surface." + "s" * 43
SURFACE_TWO = "surface." + "t" * 43
DIARY_SURFACE = "surface." + "d" * 43
EXCHANGE_CODE = "exchange." + "e" * 43
CSRF_ONE = "csrf." + "c" * 43
CSRF_TWO = "csrf." + "r" * 43
CSRF_THREE = "csrf." + "q" * 43
VERIFIER = "v" * 43
STATE = "state-authored-synthetic"
NONCE = "nonce-authored-synthetic"
NOW = datetime(2026, 8, 1, 1, 2, 3, tzinfo=timezone.utc)
TEST_CLIENT = ("127.0.0.1", 50000)


class _DenialSink:
    def __init__(self) -> None:
        self.events: list[TransportDenialEvent] = []

    def record(self, event: TransportDenialEvent) -> None:
        self.events.append(event)


def _operational_guard() -> ApplicationAuthOperationalHardening:
    return ApplicationAuthOperationalHardening(
        proxy_policy=ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=10_000,
            max_keys=8,
        ),
        denial_audit_sink=_DenialSink(),
        client_hmac_key=b"authored-synthetic-test-key-0001",
        clock=lambda: NOW,
    )


class _StubRuntime:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.failure: Exception | None = None

    def _before(self, operation: str) -> None:
        self.calls.append(operation)
        if self.failure is not None:
            raise self.failure

    def create_session(self, **_kwargs) -> CreatedApplicationSession:
        self._before("create")
        return CreatedApplicationSession(
            parent_session_value="parent." + "p" * 43,
            surface_session_value=SURFACE_ONE,
            surface=Surface.WORD_ONLINE,
            generation=1,
            parent_expires_at=NOW + timedelta(hours=8),
            surface_idle_expires_at=NOW + timedelta(minutes=30),
        )

    def validate_surface_session(self, **_kwargs) -> ValidatedSurfaceContext:
        self._before("validate")
        return ValidatedSurfaceContext(
            user_id="synthetic-user-one",
            practice_id="synthetic-practice-one",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-one",
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
            audience="emr4-api",
            generation=1,
            parent_expires_at=NOW + timedelta(hours=8),
            surface_idle_expires_at=NOW + timedelta(minutes=30),
        )

    def rotate_surface_session(self, **_kwargs) -> RotatedSurfaceSession:
        self._before("rotate")
        return RotatedSurfaceSession(
            surface_session_value=SURFACE_TWO,
            surface=Surface.WORD_ONLINE,
            parent_generation=1,
            surface_idle_expires_at=NOW + timedelta(minutes=30),
        )

    def revoke_surface_session(self, **_kwargs) -> None:
        self._before("logout")

    def issue_exchange(self, **_kwargs) -> IssuedExchangeGrant:
        self._before("issue")
        return IssuedExchangeGrant(
            exchange_code=EXCHANGE_CODE,
            source_surface=Surface.WORD_ONLINE,
            target_surface=Surface.NATIVE_DIARY,
            expires_at=NOW + timedelta(seconds=60),
        )

    def redeem_exchange(self, **_kwargs) -> RedeemedExchangeGrant:
        self._before("redeem")
        return RedeemedExchangeGrant(
            target_surface_session_value=DIARY_SURFACE,
            target_surface=Surface.NATIVE_DIARY,
            parent_generation=1,
            surface_idle_expires_at=NOW + timedelta(minutes=30),
        )


def _transport() -> tuple[ApplicationAuthTransport, _StubRuntime]:
    runtime = _StubRuntime()
    principal = SyntheticPrincipal(
        user_id="synthetic-user-one",
        practice_id="synthetic-practice-one",
        current_backend_role="GP",
        practitioner_id="synthetic-practitioner-one",
    )
    csrf_values = iter((CSRF_ONE, CSRF_TWO, CSRF_THREE, CSRF_ONE, CSRF_TWO))
    transport = ApplicationAuthTransport(
        runtime=runtime,  # type: ignore[arg-type]
        bootstrap_registry=OneUseSyntheticBootstrapRegistry(
            {BOOTSTRAP: principal}
        ),
        surface_origins=ORIGINS,
        csrf_token_source=lambda: next(csrf_values),
    )
    return transport, runtime


def _app(transport: ApplicationAuthTransport | None = None) -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    if transport is not None:
        application.dependency_overrides[
            get_application_auth_operational_hardening
        ] = _operational_guard
        application.dependency_overrides[get_application_auth_transport] = (
            lambda: transport
        )
    return application


def _assert_no_store(response) -> None:
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["referrer-policy"] == "no-referrer"


def _assert_exact_cookie(header: str, name: str, *, deleted: bool = False) -> None:
    assert header.startswith(f"{name}=")
    lowered = header.lower()
    assert "secure" in lowered
    assert "httponly" in lowered
    assert "partitioned" in lowered
    assert "path=/" in lowered
    assert "samesite=none" in lowered
    assert "domain=" not in lowered
    if deleted:
        assert "max-age=0" in lowered
        assert "expires=" in lowered


def _cookie_headers(response) -> list[str]:
    return response.headers.get_list("set-cookie")


def test_default_application_is_closed_for_every_route() -> None:
    paths = (
        "/csrf",
        "/synthetic/session",
        "/session/validate",
        "/session/rotate",
        "/session/logout",
        "/exchange/issue",
        "/exchange/redeem",
    )
    with TestClient(
        _app(), base_url=ORIGINS[Surface.WORD_ONLINE], client=TEST_CLIENT
    ) as client:
        for path in paths:
            response = client.post(
                f"/api/v1/application-auth{path}", json={}
            )
            assert response.status_code == 404
            assert response.json() == {"detail": TRANSPORT_UNAVAILABLE}
            assert _cookie_headers(response) == []
            _assert_no_store(response)


def test_exact_origins_and_malformed_inputs_fail_before_runtime() -> None:
    transport, runtime = _transport()
    invalid_origins = (
        None,
        "null",
        "http://word-online.synthetic.invalid",
        ORIGINS[Surface.WORD_ONLINE] + "/path",
        "https://foreign.synthetic.invalid",
    )
    with TestClient(
        _app(transport),
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        for origin in invalid_origins:
            headers = {} if origin is None else {"Origin": origin}
            response = client.post(
                "/api/v1/application-auth/csrf",
                headers=headers,
                json={"surface": "word_online"},
            )
            assert response.status_code == 403
            assert response.json() == {"detail": REQUEST_NOT_ADMITTED}
            assert _cookie_headers(response) == []
            _assert_no_store(response)

        malformed = "bootstrap-secret-must-not-echo"
        response = client.post(
            "/api/v1/application-auth/synthetic/session",
            headers={"Origin": ORIGINS[Surface.WORD_ONLINE]},
            json={
                "surface": "word_online",
                "bootstrap_credential": malformed,
                "unexpected": malformed,
            },
        )
        assert response.status_code == 401
        assert response.json() == {"detail": AUTHENTICATION_FAILED}
        assert malformed not in response.text
        _assert_no_store(response)

    assert runtime.calls == []


def test_cookie_lifecycle_and_cross_surface_exchange() -> None:
    transport, runtime = _transport()
    application = _app(transport)

    with TestClient(
        application, base_url=ORIGINS[Surface.WORD_ONLINE], client=TEST_CLIENT
    ) as word:
        csrf = word.post(
            "/api/v1/application-auth/csrf",
            headers={"Origin": ORIGINS[Surface.WORD_ONLINE]},
            json={"surface": "word_online"},
        )
        assert csrf.status_code == 200
        assert csrf.json() == {
            "csrf_token": CSRF_ONE,
            "surface": "word_online",
        }
        csrf_headers = _cookie_headers(csrf)
        assert len(csrf_headers) == 1
        _assert_exact_cookie(csrf_headers[0], CSRF_COOKIE_NAME)
        _assert_no_store(csrf)

        login = word.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": CSRF_ONE,
            },
            json={
                "surface": "word_online",
                "bootstrap_credential": BOOTSTRAP,
                "correlation_id": "correlation-login-one",
            },
        )
        assert login.status_code == 200
        assert login.json()["csrf_token"] == CSRF_TWO
        assert "parent" not in login.text
        assert SURFACE_ONE not in login.text
        login_headers = _cookie_headers(login)
        assert len(login_headers) == 2
        _assert_exact_cookie(login_headers[0], SESSION_COOKIE_NAME)
        _assert_exact_cookie(login_headers[1], CSRF_COOKIE_NAME)
        _assert_no_store(login)

        validate = word.post(
            "/api/v1/application-auth/session/validate",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": CSRF_TWO,
            },
            json={"surface": "word_online"},
        )
        assert validate.status_code == 200
        assert validate.json() == {
            "status": "authenticated",
            "surface": "word_online",
            "current_backend_role": "GP",
            "authority_source": "emr4_backend",
            "data_class": "authored_synthetic",
            "surface_idle_expires_at": "2026-08-01T01:32:03Z",
        }
        assert "synthetic-user" not in validate.text
        assert "synthetic-practice" not in validate.text
        assert _cookie_headers(validate) == []
        _assert_no_store(validate)

        rotate = word.post(
            "/api/v1/application-auth/session/rotate",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": CSRF_TWO,
            },
            json={"surface": "word_online"},
        )
        assert rotate.status_code == 200
        assert rotate.json()["csrf_token"] == CSRF_THREE
        assert SURFACE_TWO not in rotate.text
        assert len(_cookie_headers(rotate)) == 2
        _assert_no_store(rotate)

        issued = word.post(
            "/api/v1/application-auth/exchange/issue",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": CSRF_THREE,
            },
            json={
                "source_surface": "word_online",
                "target_surface": "native_diary",
                "target_origin": ORIGINS[Surface.NATIVE_DIARY],
                "state": STATE,
                "nonce": NONCE,
                "pkce_challenge": pkce_s256_challenge(VERIFIER),
            },
        )
        assert issued.status_code == 200
        assert issued.json()["exchange_code"] == EXCHANGE_CODE
        assert set(issued.json()) == {
            "exchange_code",
            "target_surface",
            "expires_at",
        }
        assert _cookie_headers(issued) == []
        _assert_no_store(issued)

    with TestClient(
        application, base_url=ORIGINS[Surface.NATIVE_DIARY], client=TEST_CLIENT
    ) as diary:
        csrf = diary.post(
            "/api/v1/application-auth/csrf",
            headers={"Origin": ORIGINS[Surface.NATIVE_DIARY]},
            json={"surface": "native_diary"},
        )
        diary_csrf = csrf.json()["csrf_token"]
        redeemed = diary.post(
            "/api/v1/application-auth/exchange/redeem",
            headers={
                "Origin": ORIGINS[Surface.NATIVE_DIARY],
                "X-EMR4-CSRF": diary_csrf,
            },
            json={
                "exchange_code": EXCHANGE_CODE,
                "source_surface": "word_online",
                "target_surface": "native_diary",
                "source_origin": ORIGINS[Surface.WORD_ONLINE],
                "state": STATE,
                "nonce": NONCE,
                "pkce_verifier": VERIFIER,
            },
        )
        assert redeemed.status_code == 200
        assert DIARY_SURFACE not in redeemed.text
        assert len(_cookie_headers(redeemed)) == 2
        assert redeemed.json()["surface"] == "native_diary"
        _assert_no_store(redeemed)

        logout = diary.post(
            "/api/v1/application-auth/session/logout",
            headers={
                "Origin": ORIGINS[Surface.NATIVE_DIARY],
                "X-EMR4-CSRF": redeemed.json()["csrf_token"],
            },
            json={"surface": "native_diary"},
        )
        assert logout.status_code == 204
        assert logout.content == b""
        deleted = _cookie_headers(logout)
        assert len(deleted) == 2
        _assert_exact_cookie(deleted[0], SESSION_COOKIE_NAME, deleted=True)
        _assert_exact_cookie(deleted[1], CSRF_COOKIE_NAME, deleted=True)
        _assert_no_store(logout)

    assert runtime.calls == [
        "create",
        "validate",
        "rotate",
        "issue",
        "redeem",
        "logout",
    ]


@pytest.mark.parametrize(
    ("failure", "status_code", "detail"),
    (
        (RequiredAuditUnavailable(), 503, AUTHENTICATION_UNAVAILABLE),
        (
            OperationalError("SELECT", {}, RuntimeError("database unavailable")),
            503,
            AUTHENTICATION_UNAVAILABLE,
        ),
    ),
)
def test_failed_login_never_sets_authority_cookies(
    failure: Exception,
    status_code: int,
    detail: str,
) -> None:
    transport, runtime = _transport()
    runtime.failure = failure
    with TestClient(
        _app(transport),
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        csrf = client.post(
            "/api/v1/application-auth/csrf",
            headers={"Origin": ORIGINS[Surface.WORD_ONLINE]},
            json={"surface": "word_online"},
        )
        token = csrf.json()["csrf_token"]
        response = client.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": token,
            },
            json={
                "surface": "word_online",
                "bootstrap_credential": BOOTSTRAP,
            },
        )
        assert response.status_code == status_code
        assert response.json() == {"detail": detail}
        assert _cookie_headers(response) == []
        assert BOOTSTRAP not in response.text
        _assert_no_store(response)
        assert transport.bootstrap_registry.state_counts() == {
            "available": 1,
            "reserved": 0,
            "consumed": 0,
        }


def test_bootstrap_replay_and_csrf_mismatch_share_generic_denials() -> None:
    transport, runtime = _transport()
    with TestClient(
        _app(transport),
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        first_csrf = client.post(
            "/api/v1/application-auth/csrf",
            headers={"Origin": ORIGINS[Surface.WORD_ONLINE]},
            json={"surface": "word_online"},
        ).json()["csrf_token"]
        first = client.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": first_csrf,
            },
            json={
                "surface": "word_online",
                "bootstrap_credential": BOOTSTRAP,
            },
        )
        assert first.status_code == 200

        fresh_csrf = client.post(
            "/api/v1/application-auth/csrf",
            headers={"Origin": ORIGINS[Surface.WORD_ONLINE]},
            json={"surface": "word_online"},
        ).json()["csrf_token"]
        replay = client.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": fresh_csrf,
            },
            json={
                "surface": "word_online",
                "bootstrap_credential": BOOTSTRAP,
            },
        )
        assert replay.status_code == 401
        assert replay.json() == {"detail": AUTHENTICATION_FAILED}
        assert _cookie_headers(replay) == []

        before = list(runtime.calls)
        csrf_denial = client.post(
            "/api/v1/application-auth/session/validate",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": "csrf." + "x" * 43,
            },
            json={"surface": "word_online"},
        )
        assert csrf_denial.status_code == 403
        assert csrf_denial.json() == {"detail": REQUEST_NOT_ADMITTED}
        assert runtime.calls == before
        assert _cookie_headers(csrf_denial) == []


def test_exchange_shapes_reject_wrong_surface_roles_before_runtime() -> None:
    transport, runtime = _transport()
    forbidden_cases = (
        {
            "source_surface": "native_diary",
            "target_surface": "native_diary",
            "target_origin": ORIGINS[Surface.NATIVE_DIARY],
            "state": STATE,
            "nonce": NONCE,
            "pkce_challenge": pkce_s256_challenge(VERIFIER),
        },
        {
            "source_surface": "word_online",
            "target_surface": "word_desktop",
            "target_origin": ORIGINS[Surface.WORD_DESKTOP],
            "state": STATE,
            "nonce": NONCE,
            "pkce_challenge": pkce_s256_challenge(VERIFIER),
        },
    )
    with TestClient(
        _app(transport),
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        for payload in forbidden_cases:
            response = client.post(
                "/api/v1/application-auth/exchange/issue",
                headers={"Origin": ORIGINS[Surface.WORD_ONLINE]},
                json=payload,
            )
            assert response.status_code == 401
            assert response.json() == {"detail": AUTHENTICATION_FAILED}
            _assert_no_store(response)
    assert runtime.calls == []
