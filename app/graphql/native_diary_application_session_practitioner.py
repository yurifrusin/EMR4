"""Default-off native-Diary application-session composition adapter.

The accepted shared practitioner router (``application_auth_product.py``) is a
deliberately permissive GraphQL surface: it intentionally accepts a client
selected ``practiceId``, display-safe field subsets and bounded pagination
variations.  The accepted native-Diary composition contract instead requires
one fixed request with no client-selected practice, projection or pagination.
This module therefore adds a stricter outer pre-auth admission guard and reuses
the accepted bridge/router unchanged underneath it.

The composition is unmounted and default-off.  ``create_native_diary_application_session_app``
with ``enabled=False`` (the default posture) returns a task-local FastAPI/ASGI
application with no product route, no docs and no OpenAPI, and it opens no
database session.  Only literal explicit enablement (``enabled is True``)
constructs the accepted shared practitioner router bound server-side to exactly
``Surface.NATIVE_DIARY`` and installs the bounded pre-auth guard.

The guard is an ASGI-level admission gate for the exact product path.  It
buffers/replays at most ``MAX_REQUEST_BYTES`` (8192) bytes, requires POST with
``application/json``, the fixed query constant, the exact variables
``{activeOnly: true, limit: 200, offset: 0}`` and no ``practiceId``, alias,
spread syntax, directive, introspection, mutation, field subset/extra field,
pagination drift or extra JSON key.  Any deviation is rejected generically with
403 and ``Cache-Control: no-store`` before the bridge performs any session,
origin, CSRF or product authentication.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from fastapi import FastAPI

from app.graphql.application_auth_product import (
    create_application_session_practitioner_directory_router,
)
from app.services.application_auth_product_read import (
    ApplicationSessionPractitionerDirectoryBridge,
)
from app.services.application_auth_runtime import Surface

PRODUCT_PATH = "/api/v1/application-auth/product/graphql"
MAX_REQUEST_BYTES = 8192

# The one fixed native-Diary request.  No client-selected practice, projection,
# pagination or operation variation is admitted.
FIXED_VARIABLES = {"activeOnly": True, "limit": 200, "offset": 0}
FIXED_QUERY = """\
query NativeDiaryPractitioners($activeOnly: Boolean!, $limit: Int!, $offset: Int!) {
  practice {
    practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) {
      id
      displayName
      roleLabel
      active
      defaultLocation {
        id
        name
      }
    }
  }
}
"""


def create_native_diary_application_session_app(
    *,
    enabled: bool,
    bridge: ApplicationSessionPractitionerDirectoryBridge | None = None,
) -> FastAPI:
    """Return a task-local FastAPI/ASGI application for the native Diary lane.

    When ``enabled`` is not literally ``True`` the returned application has no
    product route, no docs and no OpenAPI, and it opens no database/session.
    Only literal explicit enablement constructs the accepted shared practitioner
    router bound server-side to exactly ``Surface.NATIVE_DIARY`` beneath the
    bounded pre-auth admission guard.
    """

    if enabled is not True:
        return FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    if bridge is None:
        raise ValueError(
            "an explicitly enabled native-Diary application-session app "
            "requires the accepted practitioner-directory bridge"
        )

    application = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    application.include_router(
        create_application_session_practitioner_directory_router(
            bridge=bridge,
            surface=Surface.NATIVE_DIARY,
        )
    )
    application.add_middleware(_PreAuthAdmissionGuard)
    return application


class _PreAuthAdmissionGuard:
    """Bounded ASGI-level pre-auth admission guard for the exact product path.

    The guard is intentionally stricter than the shared router.  It admits only
    the one fixed native-Diary request and rejects everything else generically
    with 403 and ``Cache-Control: no-store`` before the bridge runs.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope.get("type") != "http" or scope.get("path") != PRODUCT_PATH:
            await self.app(scope, receive, send)
            return

        method = scope.get("method")
        headers = _lower_headers(scope.get("headers") or ())
        content_type = headers.get("content-type", "").partition(";")[0]
        if method != "POST" or content_type.strip().lower() != "application/json":
            await _reject(send)
            return
        raw_length = headers.get("content-length")
        if raw_length is not None:
            try:
                if int(raw_length) > MAX_REQUEST_BYTES:
                    await _reject(send)
                    return
            except ValueError:
                await _reject(send)
                return

        body = await _buffer_request(receive)
        if body is None:
            return
        if not body or len(body) > MAX_REQUEST_BYTES:
            await _reject(send)
            return
        if not _admission_allowed(body):
            await _reject(send)
            return

        await self.app(scope, _replaying_receive(body), send)


def _admission_allowed(body: bytes) -> bool:
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict) or set(payload) != {"query", "variables"}:
        return False
    query = payload.get("query")
    variables = payload.get("variables")
    if not isinstance(query, str) or query != FIXED_QUERY:
        return False
    if not isinstance(variables, dict) or variables != FIXED_VARIABLES:
        return False
    return True


async def _buffer_request(receive: Any) -> bytes | None:
    """Read and buffer at most ``MAX_REQUEST_BYTES`` request bytes.

    Returns ``None`` when the client disconnected before a complete body was
    received so the caller can stop without sending.
    """

    body = bytearray()
    more_body = True
    while more_body:
        message = await receive()
        message_type = message.get("type")
        if message_type == "http.disconnect":
            return None
        if message_type != "http.request":
            continue
        body.extend(message.get("body", b""))
        if len(body) > MAX_REQUEST_BYTES:
            return bytes(body)
        more_body = bool(message.get("more_body", False))
    return bytes(body)


def _replaying_receive(body: bytes) -> Callable[[], Any]:
    replayed = False

    async def receive() -> dict[str, Any]:
        nonlocal replayed
        if not replayed:
            replayed = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": False}

    return receive


def _lower_headers(headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
    return {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in headers
    }


async def _reject(send: Any) -> None:
    response_body = b'{"detail":"Forbidden"}'
    await send(
        {
            "type": "http.response.start",
            "status": 403,
            "headers": [
                (b"content-type", b"application/json"),
                (b"cache-control", b"no-store"),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": response_body,
            "more_body": False,
        }
    )


__all__ = [
    "FIXED_QUERY",
    "FIXED_VARIABLES",
    "MAX_REQUEST_BYTES",
    "PRODUCT_PATH",
    "create_native_diary_application_session_app",
]
