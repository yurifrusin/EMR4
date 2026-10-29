"""Inert source candidate: trusted isolated Account HTTP composition only.

No caller in this file launches an app or creates an engine. The reviewed host
owns the exact engine, session lifetime and disposal, including cleanup proof.
Not a production app and not an admission or execution binding.
"""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def build_account_appointments_app(*, enabled=False, auth_engine=None,
                                   expected_database=None, expected_port=None,
                                   local_bootstrap_enabled=False):
    """Compose the existing narrow app, optionally exposing four Account routes.

    Only a trusted isolated harness may supply these arguments. Never populate
    them from HTTP input. With the default, Account is absent and no engine is
    retained. The caller owns auth_engine and must close all sessions and dispose
    it after serving; this helper never assumes ownership or closes it.
    """
    from stage1_runtime_adapter import build_narrow_appointments_app

    if type(local_bootstrap_enabled) is not bool:
        raise ValueError("invalid bootstrap flag")
    if local_bootstrap_enabled and enabled is not True:
        raise ValueError("bootstrap requires account composition")

    if enabled is not True:
        if enabled is not False or auth_engine is not None or expected_database is not None or expected_port is not None:
            raise ValueError("account composition disabled")
        return build_narrow_appointments_app()

    from app.config import settings
    if (settings.environment != "dev" or not isinstance(auth_engine, Engine)
            or not isinstance(auth_engine.pool, NullPool)
            or auth_engine.hide_parameters is not True or auth_engine.echo
            or auth_engine.url.get_backend_name() != "postgresql"
            or auth_engine.url.username != "raisa_local_account_auth"
            or auth_engine.url.host != "127.0.0.1"
            or type(expected_port) is not int or not 1 <= expected_port <= 65535
            or auth_engine.url.port != expected_port
            or type(expected_database) is not str or not expected_database
            or auth_engine.url.database != expected_database
            or bool(auth_engine.url.query)):
        raise ValueError("account composition unavailable")

    # Import only after all trusted host-supplied guard checks. The router and
    # get_account_auth_db retain signature, row-current and DB identity checks.
    from app.routers.auth import router as account_router
    app = build_narrow_appointments_app()
    allowed = {
        ("POST", "/api/v1/auth/login"),
        ("GET", "/api/v1/auth/memberships"),
        ("POST", "/api/v1/auth/select-membership"),
        ("GET", "/api/v1/auth/me"),
    }
    if local_bootstrap_enabled:
        allowed.update({("POST", "/api/v1/auth/register"),
                        ("POST", "/api/v1/auth/practices")})
    # Validate whole paths and complete method sets before copying anything.
    from fastapi import APIRouter
    from fastapi.routing import APIRoute
    expected = {path: method for method, path in allowed}
    selected = []
    for route in account_router.routes:
        path = getattr(route, "path", None)
        if path not in expected:
            continue
        if (not isinstance(route, APIRoute)
                or route.methods != {expected[path]}):
            raise ValueError("account route set changed")
        selected.append(route)
    if (len(selected) != len(expected)
            or {route.path for route in selected} != set(expected)):
        raise ValueError("account route set changed")
    # Reject any existing destination route at an Account path, regardless of
    # method or route class, so no earlier route can shadow the selected one.
    if any(getattr(route, "path", None) in expected for route in app.router.routes):
        raise ValueError("account route collision")

    # include_router recreates APIRoutes on the destination app. This preserves
    # each route's endpoint, dependencies, response model and security metadata
    # while binding FastAPI dependency overrides to the destination app.
    subset = APIRouter()
    subset.routes.extend(selected)
    app.include_router(subset)
    app.state.account_auth_session_factory = sessionmaker(
        bind=auth_engine, autocommit=False, autoflush=False)
    if local_bootstrap_enabled:
        app.state.local_account_bootstrap_enabled = True
    return app
