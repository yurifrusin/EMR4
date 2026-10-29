"""Inert source candidate: trusted isolated Account HTTP composition only.

No caller in this file launches an app or creates an engine. The reviewed host
owns the exact engine, session lifetime and disposal, including cleanup proof.
Not a production app and not an admission or execution binding.
"""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


from dataclasses import dataclass
import re
import uuid


@dataclass(frozen=True, repr=False)
class LocalSyntheticInvitationBinding:
    """Private trusted harness input; never HTTP input or fixture provisioning."""
    run_id: str
    target_handle: str
    practice_id: uuid.UUID
    owner_account_id: uuid.UUID
    recipient_account_id: uuid.UUID
    fixture_binding_id: uuid.UUID


def _validate_invitation_binding(binding):
    if (type(binding) is not LocalSyntheticInvitationBinding
            or type(binding.run_id) is not str or re.fullmatch(r"[A-Za-z0-9_-]{1,80}", binding.run_id) is None
            or type(binding.target_handle) is not str
            or re.fullmatch(r"synthetic:[a-z0-9-]{1,64}", binding.target_handle) is None
            or any(type(value) is not uuid.UUID or value.int == 0 for value in
                   (binding.practice_id, binding.owner_account_id, binding.recipient_account_id, binding.fixture_binding_id))
            or binding.owner_account_id == binding.recipient_account_id):
        raise ValueError("invalid invitation binding")


def build_account_appointments_app(*, enabled=False, auth_engine=None,
                                   expected_database=None, expected_port=None,
                                   local_bootstrap_enabled=False,
                                   local_invitation_enabled=False, invitation_binding=None):
    """Compose the existing narrow app, optionally exposing four Account routes.

    Only a trusted isolated harness may supply these arguments. Never populate
    them from HTTP input. With the default, Account is absent and no engine is
    retained. The caller owns auth_engine and must close all sessions and dispose
    it after serving; this helper never assumes ownership or closes it.
    """
    from stage1_runtime_adapter import build_narrow_appointments_app

    if type(local_invitation_enabled) is not bool:
        raise ValueError("invalid invitation flag")
    if local_invitation_enabled:
        if enabled is not True or local_bootstrap_enabled is not True:
            raise ValueError("invitation requires local bootstrap composition")
        _validate_invitation_binding(invitation_binding)
    elif invitation_binding is not None:
        raise ValueError("invitation composition disabled")

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
    if local_invitation_enabled:
        _mount_local_invitation_bridge(app, auth_engine, invitation_binding, local_invitation_enabled)
    return app


def _mount_local_invitation_bridge(app, auth_engine, binding, enabled):
    """Private one-target restriction cache; service/DB remain command authority."""
    import ipaddress
    import json
    import re
    import threading
    import uuid
    from fastapi import HTTPException, Request
    from fastapi.responses import JSONResponse
    from app.config import settings
    from app.services import auth_service
    from app.services.local_synthetic_invitation import LocalSyntheticInvitationService

    paths = {"/api/v1/local-invitations/issue", "/api/v1/local-invitations/accept",
             "/api/v1/local-invitations/revoke"}
    if any(getattr(route, "path", None) in paths for route in app.router.routes):
        raise ValueError("invitation route collision")
    service = LocalSyntheticInvitationService(auth_engine)
    lock = threading.Lock()
    # Only these two non-secret derived identifiers survive a command. They
    # restrict calls; they never replace service authentication or DB current rows.
    reserved_key = None
    invitation_id = None
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}

    def denied(code=400):
        return HTTPException(status_code=code, detail="Invitation unavailable", headers=headers)

    def guard(request):
        try:
            local = request.client is not None and ipaddress.ip_address(request.client.host).is_loopback
        except ValueError:
            local = False
        if enabled is not True or settings.environment != "dev" or not local:
            raise denied(404)
        if request.query_params or request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            raise denied()

    def token(request):
        values = request.headers.getlist("authorization")
        if len(values) != 1 or re.fullmatch(r"Bearer [A-Za-z0-9_.-]{1,4096}", values[0]) is None:
            raise denied(401)
        return values[0][7:]

    async def body(request, keys):
        def pairs(items):
            value = {}
            for key, item in items:
                if key in value:
                    raise ValueError()
                value[key] = item
            return value
        try:
            raw = bytearray()
            async for chunk in request.stream():
                if len(raw) + len(chunk) > 2048:
                    raise ValueError()
                raw.extend(chunk)
            value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                               parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            if (type(value) is not dict or set(value) != keys
                    or value["confirm"] is not True
                    or type(value["target"]) is not str or value["target"] != binding.target_handle):
                raise ValueError()
            return value
        except Exception:
            raise denied() from None

    def canonical_uuid(value):
        if type(value) is not str:
            raise denied()
        try:
            parsed = uuid.UUID(value)
            if str(parsed) != value:
                raise ValueError()
            return parsed
        except ValueError:
            raise denied() from None

    def owner_matches(bearer):
        claims = auth_service.verify_token(bearer)
        if (claims.account_id != binding.owner_account_id or claims.practice_id != binding.practice_id
                or claims.role != "PracticeOwner"):
            raise denied()

    async def issue(request: Request):
        nonlocal reserved_key, invitation_id
        guard(request)
        data = await body(request, {"target", "confirm", "idempotency_key"})
        key = canonical_uuid(data["idempotency_key"])
        bearer = token(request)
        with lock:
            try:
                owner_matches(bearer)
                if reserved_key is not None and reserved_key != key:
                    raise denied()
                # Reserve before service call, retain on every ambiguous failure.
                reserved_key = key
                receipt, secret = service.issue(bearer, binding.fixture_binding_id, "Receptionist", 300, key)
                returned = receipt["invitation_id"]
                if type(returned) is not uuid.UUID or (invitation_id is not None and invitation_id != returned):
                    raise denied()
                if type(receipt["created"]) is not bool:
                    raise denied()
                if type(receipt["state"]) is not str or receipt["state"] not in ("pending", "accepted", "revoked"):
                    raise denied()
                result = {"state": receipt["state"], "created": receipt["created"]}
                if receipt["created"] is True:
                    if type(secret) is not str or re.fullmatch(r"[A-Za-z0-9_-]{43}", secret) is None:
                        raise denied()
                    result["secret"] = secret
                elif secret is not None:
                    raise denied()
                # Service returns only after commit; never serialize receipt/service
                # generically. Secret occurs only in the successful first response.
                response = JSONResponse(result, headers=headers)
                # Publish only a fully validated committed receipt. Failed first
                # receipts keep the key reserved but cannot enable accept/revoke.
                invitation_id = returned
                return response
            except Exception:
                raise denied() from None

    async def accept(request: Request):
        guard(request)
        data = await body(request, {"target", "confirm", "secret"})
        bearer = token(request)
        if type(data["secret"]) is not str or re.fullmatch(r"[A-Za-z0-9_-]{43}", data["secret"]) is None:
            raise denied()
        with lock:
            try:
                account = auth_service.verify_bootstrap_token(bearer)
                if account.account_id != binding.recipient_account_id or invitation_id is None:
                    raise denied()
                receipt = service.accept(bearer, invitation_id, data["secret"])
                if (type(receipt["membership_id"]) is not uuid.UUID
                        or receipt["practice_id"] != binding.practice_id or receipt["role"] != "Receptionist"):
                    raise denied()
                return JSONResponse({"membership_id": str(receipt["membership_id"]),
                                     "practice_id": str(binding.practice_id), "role": "Receptionist"}, headers=headers)
            except Exception:
                raise denied() from None

    async def revoke(request: Request):
        guard(request)
        await body(request, {"target", "confirm"})
        bearer = token(request)
        with lock:
            try:
                owner_matches(bearer)
                if invitation_id is None:
                    raise denied()
                receipt = service.revoke(bearer, invitation_id)
                if (receipt["invitation_id"] != invitation_id or type(receipt["state"]) is not str
                        or receipt["state"] not in ("revoked", "accepted")):
                    raise denied()
                return JSONResponse({"state": receipt["state"]}, headers=headers)
            except Exception:
                raise denied() from None

    app.add_api_route("/api/v1/local-invitations/issue", issue, methods=["POST"], include_in_schema=False)
    app.add_api_route("/api/v1/local-invitations/accept", accept, methods=["POST"], include_in_schema=False)
    app.add_api_route("/api/v1/local-invitations/revoke", revoke, methods=["POST"], include_in_schema=False)
