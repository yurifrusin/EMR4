"""Default-off fixed GraphQL surface for the Rayleen A4 product read."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum
import json
from typing import Any, Callable
import uuid

from fastapi import FastAPI, HTTPException, Request, Response, status
import strawberry
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.config import settings
from app.services.application_auth_product_read import (
    ProductReadAuthenticationFailed,
    ProductReadAuthorizationFailed,
    ProductReadRequestDenied,
    ProductReadUnavailable,
)
from app.services.application_auth_rayleen_waiting_room import (
    ApplicationSessionRayleenWaitingRoomBridge,
)
from app.services.application_auth_runtime import Surface
from app.services.application_auth_transport import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
)
from app.services.diary.rayleen_waiting_room_projection import (
    ProjectionKind,
    WaitingRoomContextFrame,
    WaitingRoomProjection,
    WaitingRoomReadDenied,
    read_waiting_room_projection,
)


PRODUCT_PATH = "/api/v1/application-auth/rayleen/graphql"
CORRELATION_HEADER_NAME = "X-EMR4-Correlation-ID"
MAX_REQUEST_BYTES = 8192
FIXED_QUERY = """\
query RayleenWaitingRoom(
  $locationId: ID!
  $projectionKind: RayleenProjectionKind!
  $practitionerId: ID
  $waitingAreaId: ID
  $focusAppointmentId: ID
) {
  rayleenWaitingRoom(
    locationId: $locationId
    projectionKind: $projectionKind
    practitionerId: $practitionerId
    waitingAreaId: $waitingAreaId
    focusAppointmentId: $focusAppointmentId
  ) {
    schemaVersion
    frameId
    practiceId
    locationId
    contextRevision
    generatedAt
    expiresAt
    reader
    excludedFieldClasses
    projection {
      kind
      selectedCount
      practitionerId
      waitingAreaId
      focusAppointmentId
      selectorProvenance
      authorityCeiling
      writesAuthorized
    }
    backendFacts {
      appointmentId
      patientDisplayToken
      practitionerId
      status
      scheduledAt
      waitingAreaId
      arrivedAt
      label {
        sourceIds
        integrityPrincipals
        confidentialityReaders
        observedAt
        expiresAt
        freshnessState
        authorityCeiling
      }
    }
    derivedSignals {
      kind
      appointmentId
      integerValue
      textValue
      booleanValue
      derivedBy
      label {
        sourceIds
        integrityPrincipals
        confidentialityReaders
        observedAt
        expiresAt
        freshnessState
        authorityCeiling
      }
    }
  }
}
"""


@strawberry.enum(name="RayleenProjectionKind")
class RayleenProjectionKind(Enum):
    FULL_QUEUE = "full_queue"
    PRACTITIONER_GROUP = "practitioner_group"
    WAITING_AREA_GROUP = "waiting_area_group"
    LONGEST_WAIT = "longest_wait"


@strawberry.type
class RayleenFactLabel:
    source_ids: list[str]
    integrity_principals: list[str]
    confidentiality_readers: list[str]
    observed_at: datetime
    expires_at: datetime
    freshness_state: str
    authority_ceiling: str


@strawberry.type
class RayleenWaitingRoomFact:
    appointment_id: strawberry.ID
    patient_display_token: str
    practitioner_id: strawberry.ID
    status: str
    scheduled_at: datetime
    waiting_area_id: strawberry.ID | None
    arrived_at: datetime | None
    label: RayleenFactLabel


@strawberry.type
class RayleenWaitingRoomSignal:
    kind: str
    appointment_id: strawberry.ID
    integer_value: int | None
    text_value: str | None
    boolean_value: bool | None
    derived_by: str
    label: RayleenFactLabel


@strawberry.type
class RayleenProjection:
    kind: RayleenProjectionKind
    selected_count: int
    practitioner_id: strawberry.ID | None
    waiting_area_id: strawberry.ID | None
    focus_appointment_id: strawberry.ID | None
    selector_provenance: str
    authority_ceiling: str
    writes_authorized: bool


@strawberry.type
class RayleenWaitingRoomFrame:
    schema_version: str
    frame_id: strawberry.ID
    practice_id: strawberry.ID
    location_id: strawberry.ID
    context_revision: int
    generated_at: datetime
    expires_at: datetime
    reader: str
    backend_facts: list[RayleenWaitingRoomFact]
    derived_signals: list[RayleenWaitingRoomSignal]
    excluded_field_classes: list[str]
    projection: RayleenProjection


@strawberry.type
class RayleenQuery:
    @strawberry.field
    def rayleen_waiting_room(
        self,
        info: Info,
        location_id: strawberry.ID,
        projection_kind: RayleenProjectionKind,
        practitioner_id: strawberry.ID | None = None,
        waiting_area_id: strawberry.ID | None = None,
        focus_appointment_id: strawberry.ID | None = None,
    ) -> RayleenWaitingRoomFrame:
        try:
            result = read_waiting_room_projection(
                info.context["db"],
                current_user=info.context["current_user"],
                location_id=_uuid(location_id),
                projection_kind=ProjectionKind(projection_kind.value),
                practitioner_id=_optional_uuid(practitioner_id),
                waiting_area_id=_optional_uuid(waiting_area_id),
                focus_appointment_id=_optional_uuid(focus_appointment_id),
                observed_at=info.context.get("observed_at"),
            )
        except (ValueError, WaitingRoomReadDenied) as exc:
            raise StrawberryGraphQLError(
                "Forbidden",
                extensions={"code": "FORBIDDEN"},
            ) from exc
        except Exception as exc:
            raise StrawberryGraphQLError(
                "Service unavailable",
                extensions={"code": "SERVICE_UNAVAILABLE"},
            ) from exc
        return _frame_out(result.frame, result.projection)


RAYLEEN_SCHEMA = strawberry.Schema(query=RayleenQuery)


def create_native_diary_rayleen_waiting_room_app(
    *,
    enabled: bool | None = None,
    bridge: ApplicationSessionRayleenWaitingRoomBridge | None = None,
    observed_at_source: Callable[[], datetime] | None = None,
    configuration: Any = settings,
) -> FastAPI:
    """Return an unmounted, task-local app for one fixed A4 query."""

    configured_enabled = (
        getattr(configuration, "rayleen_a4_product_read_enabled", False) is True
    )
    requested_enabled = configured_enabled if enabled is None else (
        enabled is True and configured_enabled
    )
    configured_practices = {
        item.strip().lower()
        for item in str(
            getattr(configuration, "rayleen_a4_synthetic_practice_ids", "")
        ).split(",")
        if item.strip()
    }
    if (
        not requested_enabled
        or str(getattr(configuration, "environment", "")).lower() != "dev"
        or not configured_practices
    ):
        return FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    if bridge is None or not isinstance(
        bridge, ApplicationSessionRayleenWaitingRoomBridge
    ):
        raise ValueError("enabled Rayleen A4 app requires its exact bridge")
    bridge_practices = {str(value).lower() for value in bridge.allowed_practice_ids}
    if bridge_practices != configured_practices:
        raise ValueError("Rayleen A4 bridge/config practice allowlist mismatch")

    async def context_getter(
        request: Request,
        response: Response,
    ) -> AsyncIterator[dict[str, object]]:
        try:
            context = bridge.open_context(
                surface_session_value=request.cookies.get(SESSION_COOKIE_NAME) or "",
                csrf_cookie=request.cookies.get(CSRF_COOKIE_NAME),
                csrf_header=request.headers.get(CSRF_HEADER_NAME),
                surface=Surface.NATIVE_DIARY,
                origin=request.headers.get("Origin"),
                correlation_id=request.headers.get(CORRELATION_HEADER_NAME),
            )
        except ProductReadRequestDenied:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
        except ProductReadAuthenticationFailed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None
        except ProductReadAuthorizationFailed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
        except ProductReadUnavailable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            ) from None

        response.headers["Cache-Control"] = "no-store"
        try:
            yield {
                "current_user": context.current_user,
                "db": context.db,
                "observed_at": (
                    observed_at_source() if observed_at_source is not None else None
                ),
            }
        finally:
            context.db.close()

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(
        GraphQLRouter(
            RAYLEEN_SCHEMA,
            path=PRODUCT_PATH,
            context_getter=context_getter,
            graphql_ide=None,
            allow_queries_via_get=False,
            tags=["rayleen-a4-product-read"],
        )
    )
    app.add_middleware(_FixedRayleenQueryGuard)
    return app


class _FixedRayleenQueryGuard:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope.get("type") != "http" or scope.get("path") != PRODUCT_PATH:
            await self.app(scope, receive, send)
            return
        headers = _lower_headers(scope.get("headers") or ())
        content_type = headers.get("content-type", "").partition(";")[0]
        if (
            scope.get("method") != "POST"
            or content_type.strip().lower() != "application/json"
        ):
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
        if not body or len(body) > MAX_REQUEST_BYTES or not _admission_allowed(body):
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
    if payload.get("query") != FIXED_QUERY:
        return False
    variables = payload.get("variables")
    if not isinstance(variables, dict) or set(variables) != {
        "locationId",
        "projectionKind",
        "practitionerId",
        "waitingAreaId",
        "focusAppointmentId",
    }:
        return False
    if variables.get("projectionKind") not in RayleenProjectionKind.__members__:
        return False
    try:
        _uuid_value(variables.get("locationId"))
        for name in ("practitionerId", "waitingAreaId", "focusAppointmentId"):
            value = variables.get(name)
            if value is not None:
                _uuid_value(value)
    except (TypeError, ValueError):
        return False
    return True


def _frame_out(
    frame: WaitingRoomContextFrame,
    projection: WaitingRoomProjection,
) -> RayleenWaitingRoomFrame:
    return RayleenWaitingRoomFrame(
        schema_version=frame.schema_version,
        frame_id=strawberry.ID(str(frame.frame_id)),
        practice_id=strawberry.ID(str(frame.practice_id)),
        location_id=strawberry.ID(str(frame.location_id)),
        context_revision=frame.context_revision,
        generated_at=frame.generated_at,
        expires_at=frame.expires_at,
        reader=frame.reader,
        backend_facts=[
            RayleenWaitingRoomFact(
                appointment_id=strawberry.ID(str(item.appointment_id)),
                patient_display_token=item.patient_display_token,
                practitioner_id=strawberry.ID(str(item.practitioner_id)),
                status=item.status,
                scheduled_at=item.scheduled_at,
                waiting_area_id=(
                    strawberry.ID(str(item.waiting_area_id))
                    if item.waiting_area_id is not None
                    else None
                ),
                arrived_at=item.arrived_at,
                label=_label_out(item.label),
            )
            for item in frame.backend_facts
        ],
        derived_signals=[_signal_out(item) for item in frame.derived_signals],
        excluded_field_classes=list(frame.excluded_field_classes),
        projection=RayleenProjection(
            kind=RayleenProjectionKind(projection.kind.value),
            selected_count=projection.selected_count,
            practitioner_id=_id_or_none(projection.practitioner_id),
            waiting_area_id=_id_or_none(projection.waiting_area_id),
            focus_appointment_id=_id_or_none(
                projection.focus_appointment_id
            ),
            selector_provenance=projection.selector_provenance,
            authority_ceiling=projection.authority_ceiling,
            writes_authorized=projection.writes_authorized,
        ),
    )


def _signal_out(item: Any) -> RayleenWaitingRoomSignal:
    value = item.value
    return RayleenWaitingRoomSignal(
        kind=item.kind,
        appointment_id=strawberry.ID(str(item.appointment_id)),
        integer_value=(
            value if isinstance(value, int) and not isinstance(value, bool) else None
        ),
        text_value=value if isinstance(value, str) else None,
        boolean_value=value if isinstance(value, bool) else None,
        derived_by=item.derived_by,
        label=_label_out(item.label),
    )


def _label_out(item: Any) -> RayleenFactLabel:
    return RayleenFactLabel(
        source_ids=list(item.source_ids),
        integrity_principals=list(item.integrity_principals),
        confidentiality_readers=list(item.confidentiality_readers),
        observed_at=item.observed_at,
        expires_at=item.expires_at,
        freshness_state=item.freshness_state,
        authority_ceiling=item.authority_ceiling,
    )


def _uuid(value: strawberry.ID) -> uuid.UUID:
    return _uuid_value(str(value))


def _optional_uuid(value: strawberry.ID | None) -> uuid.UUID | None:
    return _uuid(value) if value is not None else None


def _uuid_value(value: Any) -> uuid.UUID:
    if not isinstance(value, str):
        raise TypeError("UUID value must be a string")
    return uuid.UUID(value)


def _id_or_none(value: uuid.UUID | None) -> strawberry.ID | None:
    return strawberry.ID(str(value)) if value is not None else None


async def _buffer_request(receive: Any) -> bytes | None:
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
    body = b'{"detail":"Forbidden"}'
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
            "body": body,
            "more_body": False,
        }
    )


__all__ = [
    "FIXED_QUERY",
    "MAX_REQUEST_BYTES",
    "PRODUCT_PATH",
    "RAYLEEN_SCHEMA",
    "RayleenProjectionKind",
    "create_native_diary_rayleen_waiting_room_app",
]
