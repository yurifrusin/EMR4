from __future__ import annotations

import ast
import asyncio
from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime, time
import hashlib
import inspect
from pathlib import Path
from typing import Any
import uuid

import pytest
from fastapi import HTTPException

import app.routers.appointments as appointments_router
from app.main import app
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.shadow_instrumentation import ShadowAfterSendMiddleware
from app.models.appointments import AppointmentAuditLog, AppointmentStatus
from app.services.diary.shadow_instrumentation import (
    DEFAULT_DISABLED_SHADOW_GENERATION,
    RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID,
    RAW_COMPAT_DELETE_SHADOW_ADAPTER_ID,
    RAW_COMPAT_STATUS_SHADOW_ADAPTER_ID,
    RAW_COMPAT_UPDATE_SHADOW_ADAPTER_ID,
    SHADOW_ROUTE_ADAPTER_IDS,
    ClosedShadowOfferPort,
    ExternalShadowDisableLatch,
    ServerOwnedShadowRequestContext,
    ShadowInstrumentationClosed,
    ShadowInstrumentationGeneration,
    ShadowInstrumentationRuntime,
    ShadowProjectionMaterial,
    ShadowRequestCell,
    ShadowRouteProjection,
    StaticShadowGenerationReader,
    build_shadow_route_projection,
    shadow_instrumentation_runtime,
)
from fastapi.middleware.cors import CORSMiddleware
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTER_PATH = ROOT / "app/routers/appointments.py"
SERVICE_PATH = ROOT / "app/services/diary/shadow_instrumentation.py"


class SyntheticDigestPort:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def digest(self, *, domain: str, tokens: tuple[str, ...]) -> str:
        self.calls.append((domain, tokens))
        payload = (domain + "|" + "|".join(tokens)).encode("ascii")
        return hashlib.sha256(payload).hexdigest()


class RecordingOfferPort:
    def __init__(self, events: list[str] | None = None) -> None:
        self.calls: list[ShadowRouteProjection] = []
        self.events = events

    def offer_nowait(self, projection: ShadowRouteProjection) -> None:
        self.calls.append(projection)
        if self.events is not None:
            self.events.append("offer")


def _projection() -> ShadowRouteProjection:
    digest = SyntheticDigestPort()
    return build_shadow_route_projection(
        generation=DEFAULT_DISABLED_SHADOW_GENERATION,
        context=ServerOwnedShadowRequestContext(
            practice_id="practice-synthetic-001",
            actor_id="actor-synthetic-001",
            actor_role="Receptionist",
            authenticated_session_reference="session-synthetic-001",
            server_correlation_reference="correlation-synthetic-001",
        ),
        material=ShadowProjectionMaterial(
            route_adapter_id="raw_compat_status",
            canonical_operation_id="confirmAppointmentStatusProposal",
            purpose="reception_one_booking_context",
            target_shape="appointment",
            target_tokens=("appointment-synthetic-001",),
            conflict_domain_tokens=("appointment-synthetic-001", "version-7"),
            command_tokens=("status", "Confirmed"),
            precondition_version=7,
            precondition_tokens=("version-7",),
            confirmation_mode="staff_explicit",
            confirmation_reference_tokens=("confirmation-synthetic-001",),
            idempotency_key_tokens=("idempotency-synthetic-001",),
            canonicalization_version="shadow-v1",
            request_shape_tokens=("status:enum", "confirmed_warnings:list"),
        ),
        digest_port=digest,
    )


def test_generation_is_immutable_and_structurally_unenableable() -> None:
    generation = DEFAULT_DISABLED_SHADOW_GENERATION
    assert generation.status == "current"
    assert generation.global_enabled is False
    assert generation.practice_scope_digests == ()
    assert generation.route_adapter_ids == ()
    assert generation.digest_key_reference is None
    with pytest.raises(FrozenInstanceError):
        generation.global_enabled = True  # type: ignore[misc]
    for kwargs in (
        {"global_enabled": True},
        {"practice_scope_digests": ("practice",)},
        {"route_adapter_ids": ("raw_compat_status",)},
        {"digest_key_reference": "key-reference"},
        {"status": "stale"},
    ):
        with pytest.raises(ValueError):
            ShadowInstrumentationGeneration(**kwargs)


def test_external_latch_is_disable_only() -> None:
    latch = ExternalShadowDisableLatch()
    assert latch.disabled is False
    latch.disable()
    assert latch.disabled is True
    latch.disable()
    assert latch.disabled is True
    assert not hasattr(latch, "enable")


def test_disabled_stage_calls_zero_context_projection_digest_or_cell() -> None:
    calls = {"context": 0, "projection": 0, "digest": 0}

    def context_supplier() -> ServerOwnedShadowRequestContext:
        calls["context"] += 1
        raise AssertionError("disabled stage read context")

    def projection_supplier(*args: Any) -> ShadowRouteProjection:
        del args
        calls["projection"] += 1
        raise AssertionError("disabled stage built projection")

    runtime = ShadowInstrumentationRuntime(
        generation_reader=StaticShadowGenerationReader(),
        disable_latch=ExternalShadowDisableLatch(),
        offer_port=ClosedShadowOfferPort(),
    )
    runtime.try_stage(
        "raw_compat_status",
        context_supplier=context_supplier,
        projection_supplier=projection_supplier,
    )
    assert calls == {"context": 0, "projection": 0, "digest": 0}
    assert runtime.current_request_cell() is None


def test_generation_reader_failure_is_contained() -> None:
    class FailingReader:
        def current(self) -> ShadowInstrumentationGeneration:
            raise RuntimeError("synthetic reader failure")

    runtime = ShadowInstrumentationRuntime(
        generation_reader=FailingReader(),
        disable_latch=ExternalShadowDisableLatch(),
        offer_port=ClosedShadowOfferPort(),
    )
    assert runtime.is_globally_enabled() is False
    assert runtime.try_stage("raw_compat_create") is None


def test_projection_factory_emits_exact_twenty_four_minimized_fields() -> None:
    projection = _projection()
    assert [field.name for field in fields(ShadowRouteProjection)] == [
        "schema_version", "architecture_generation_digest", "route_adapter_id",
        "canonical_operation_id", "practice_scope_digest", "actor_digest",
        "actor_role", "session_digest", "purpose", "target_shape",
        "target_digest", "conflict_domain_digest", "command_digest",
        "precondition_present", "precondition_version", "precondition_digest",
        "confirmation_present", "confirmation_mode",
        "confirmation_reference_digest", "idempotency_present",
        "idempotency_key_digest", "canonicalization_version",
        "correlation_digest", "request_shape_digest",
    ]
    assert projection.precondition_present is True
    assert projection.confirmation_present is True
    assert projection.idempotency_present is True
    assert projection.actor_role == "Receptionist"
    assert not any("synthetic-001" in str(value) for value in (
        projection.practice_scope_digest,
        projection.actor_digest,
        projection.session_digest,
        projection.target_digest,
        projection.correlation_digest,
    ))


def test_projection_input_has_no_free_text_response_token_or_credential_surface() -> None:
    parameters = set(inspect.signature(ShadowProjectionMaterial).parameters)
    forbidden = {
        "reason", "note", "patient_name", "patient_id", "raw_request_body",
        "raw_response_body", "response_headers", "bearer_token", "credential",
        "database_value", "audit_receipt", "mutation_receipt",
    }
    assert parameters.isdisjoint(forbidden)
    with pytest.raises(ValueError, match="non-structural token"):
        build_shadow_route_projection(
            generation=DEFAULT_DISABLED_SHADOW_GENERATION,
            context=ServerOwnedShadowRequestContext(
                "practice-1", "actor-1", "Receptionist", "session-1", "correlation-1"
            ),
            material=ShadowProjectionMaterial(
                route_adapter_id="raw_compat_update",
                canonical_operation_id="confirmAppointmentUpdateProposal",
                purpose="reception_one_booking_context",
                target_shape="appointment",
                target_tokens=("appointment-1",),
                conflict_domain_tokens=("appointment-1",),
                command_tokens=("this is free text",),
                precondition_version=None,
                precondition_tokens=(),
                confirmation_mode=None,
                confirmation_reference_tokens=(),
                idempotency_key_tokens=(),
                canonicalization_version="shadow-v1",
                request_shape_tokens=("reason:string",),
            ),
            digest_port=SyntheticDigestPort(),
        )


def test_request_cell_is_single_assignment_take_and_clear() -> None:
    cell = ShadowRequestCell()
    projection = _projection()
    assert cell.assigned is False
    assert cell.take() is None
    cell.store(projection)
    assert cell.assigned is True
    with pytest.raises(ShadowInstrumentationClosed):
        cell.store(projection)
    assert cell.take() == projection
    assert cell.take() is None
    with pytest.raises(ShadowInstrumentationClosed):
        cell.store(projection)


def test_closed_offer_port_rejects_direct_use() -> None:
    with pytest.raises(ShadowInstrumentationClosed, match="offer port is closed"):
        ClosedShadowOfferPort().offer_nowait(_projection())


def test_disabled_middleware_delegates_exact_messages_and_never_offers() -> None:
    offer = RecordingOfferPort()
    runtime = ShadowInstrumentationRuntime(
        generation_reader=StaticShadowGenerationReader(),
        disable_latch=ExternalShadowDisableLatch(),
        offer_port=offer,
    )
    expected = [
        {"type": "http.response.start", "status": 204, "headers": []},
        {"type": "http.response.body", "body": b"", "more_body": False},
    ]
    observed: list[dict[str, Any]] = []

    async def inner(scope: dict, receive: Any, send: Any) -> None:
        del scope, receive
        for message in expected:
            await send(message)

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        observed.append(message)

    middleware = ShadowAfterSendMiddleware(inner, runtime=runtime)
    asyncio.run(middleware({"type": "http"}, receive, send))
    assert observed == expected
    assert offer.calls == []
    assert runtime.current_request_cell() is None


def test_finalizer_orders_send_before_offer_and_contains_offer_failure() -> None:
    events: list[str] = []

    class ProbeRuntime:
        def __init__(self) -> None:
            self.cell = ShadowRequestCell()
            self.cell.store(_projection())

        def is_globally_enabled(self) -> bool:
            return True

        def bind_request_cell(self) -> tuple[str, ShadowRequestCell]:
            events.append("bind")
            return "token", self.cell

        def offer_staged_after_send(self, cell: ShadowRequestCell) -> None:
            assert cell.take() is not None
            events.append("offer")
            raise RuntimeError("synthetic contained offer failure")

        def reset_request_cell(self, token: str) -> None:
            assert token == "token"
            events.append("reset")

    async def inner(scope: dict, receive: Any, send: Any) -> None:
        del scope, receive
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        events.append("send:" + message["type"])

    middleware = ShadowAfterSendMiddleware(inner, runtime=ProbeRuntime())  # type: ignore[arg-type]
    asyncio.run(middleware({"type": "http"}, receive, send))
    assert events == [
        "bind", "send:http.response.start", "send:http.response.body", "offer", "reset"
    ]


def test_application_middleware_order_is_shadow_cors_error() -> None:
    assert [row.cls for row in app.user_middleware[:3]] == [
        ShadowAfterSendMiddleware,
        CORSMiddleware,
        ErrorHandlerMiddleware,
    ]
    assert shadow_instrumentation_runtime.is_globally_enabled() is False


def test_ast_binds_exact_post_helper_stage_and_return_forms() -> None:
    tree = ast.parse(ROUTER_PATH.read_text(encoding="utf-8"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    expected = {
        "create_appointment": (
            "_create_appointment_from_body",
            "RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID",
            True,
        ),
        "update_appointment": (
            "_apply_appointment_update",
            "RAW_COMPAT_UPDATE_SHADOW_ADAPTER_ID",
            True,
        ),
        "update_appointment_status": (
            "_apply_appointment_status_update",
            "RAW_COMPAT_STATUS_SHADOW_ADAPTER_ID",
            True,
        ),
        "cancel_appointment": (
            "_apply_appointment_delete",
            "RAW_COMPAT_DELETE_SHADOW_ADAPTER_ID",
            False,
        ),
    }
    for handler, (helper, adapter, explicit_return) in expected.items():
        node = functions[handler]
        helper_statements = [
            index
            for index, statement in enumerate(node.body)
            if helper in ast.unparse(statement)
        ]
        stage_statements = [
            (index, statement)
            for index, statement in enumerate(node.body)
            if "shadow_instrumentation_runtime.try_stage" in ast.unparse(statement)
        ]
        assert len(helper_statements) == 1
        assert len(stage_statements) == 1
        stage_index, stage = stage_statements[0]
        assert helper_statements[0] < stage_index
        calls = [child for child in ast.walk(stage) if isinstance(child, ast.Call)]
        assert len(calls) == 1
        assert len(calls[0].args) == 1 and calls[0].keywords == []
        assert isinstance(calls[0].args[0], ast.Name)
        assert calls[0].args[0].id == adapter
        later_returns = [
            statement for statement in node.body[stage_index + 1 :]
            if isinstance(statement, ast.Return)
        ]
        assert bool(later_returns) is explicit_return
        if explicit_return:
            assert isinstance(later_returns[0].value, ast.Name)
            assert later_returns[0].value.id == "result"


def test_service_imports_no_database_network_provider_process_or_application_route() -> None:
    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {
        "__future__", "collections", "contextvars", "dataclasses", "hashlib",
        "re", "typing",
    }
    assert imports.isdisjoint(
        {"sqlalchemy", "psycopg", "requests", "httpx", "google", "socket", "subprocess"}
    )


def test_four_authored_synthetic_raw_routes_preserve_result_audit_and_zero_offer(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    monkeypatch,
) -> None:
    today = date.today()
    monkeypatch.setattr(
        appointments_router,
        "_clinic_local_now",
        lambda tz: datetime.combine(today, time(8, 0), tzinfo=tz),
    )
    offer = RecordingOfferPort()
    monkeypatch.setattr(shadow_instrumentation_runtime, "_offer_port", offer)
    stage_calls: list[tuple[str, dict[str, Any]]] = []
    original_stage = ShadowInstrumentationRuntime.try_stage

    def record_stage(
        runtime: ShadowInstrumentationRuntime,
        route_adapter_id: str,
        **kwargs: Any,
    ) -> None:
        stage_calls.append((route_adapter_id, kwargs))
        return original_stage(runtime, route_adapter_id, **kwargs)

    monkeypatch.setattr(ShadowInstrumentationRuntime, "try_stage", record_stage)
    token = make_token(gp_user)
    headers = {"Authorization": f"Bearer {token}"}
    create = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_date": today.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 15,
        },
        headers=headers,
    )
    assert create.status_code == 201
    assert create.headers.get("deprecation") is None
    created = create.json()
    appointment_id = uuid.UUID(created["id"])
    assert created["patient_id"] == str(patient.id)
    assert created["practitioner_id"] == str(practitioner.id)

    update = client.put(
        f"/api/v1/appointments/{appointment_id}",
        json={"reason": "Synthetic follow-up"},
        headers=headers,
    )
    assert update.status_code == 200
    assert update.headers.get("deprecation") is None
    assert update.json()["id"] == str(appointment_id)

    status = client.patch(
        f"/api/v1/appointments/{appointment_id}/status",
        json={"status": "Confirmed"},
        headers=headers,
    )
    assert status.status_code == 200
    assert status.headers.get("deprecation") is None
    assert status.json()["status"] == AppointmentStatus.Confirmed.value

    delete = client.delete(
        f"/api/v1/appointments/{appointment_id}", headers=headers
    )
    assert delete.status_code == 204
    assert delete.content == b""
    assert delete.headers.get("deprecation") is None

    db.expire_all()
    audits = (
        db.query(AppointmentAuditLog)
        .filter(
            AppointmentAuditLog.practice_id == practice.id,
            AppointmentAuditLog.appointment_id == appointment_id,
        )
        .order_by(AppointmentAuditLog.created_at)
        .all()
    )
    assert len(audits) == 4
    assert [audit.action.value for audit in audits] == [
        "create", "update", "status_change", "delete"
    ]
    assert [
        next(
            tag
            for tag in (audit.confirmed_warnings or [])
            if tag.startswith("raw_compat_")
        )
        for audit in audits
    ] == [
        "raw_compat_create", "raw_compat_update", "raw_compat_status",
        "raw_compat_delete",
    ]
    assert stage_calls == [
        ("raw_compat_create", {}), ("raw_compat_update", {}),
        ("raw_compat_status", {}), ("raw_compat_delete", {}),
    ]
    assert offer.calls == []
    assert shadow_instrumentation_runtime.current_request_cell() is None


def test_auth_and_validation_failures_produce_no_stage_or_offer(
    client, monkeypatch
) -> None:
    stage_calls: list[str] = []
    offer = RecordingOfferPort()
    monkeypatch.setattr(shadow_instrumentation_runtime, "_offer_port", offer)

    def record_stage(
        runtime: ShadowInstrumentationRuntime, route_adapter_id: str, **kwargs: Any
    ) -> None:
        del runtime, kwargs
        stage_calls.append(route_adapter_id)

    monkeypatch.setattr(ShadowInstrumentationRuntime, "try_stage", record_stage)
    unauthenticated = client.post("/api/v1/appointments", json={})
    assert unauthenticated.status_code == 401
    assert stage_calls == []
    assert offer.calls == []


def test_validation_conflict_helper_and_serialization_failures_emit_no_offer(
    client,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
) -> None:
    stage_calls: list[str] = []
    offer = RecordingOfferPort()
    monkeypatch.setattr(shadow_instrumentation_runtime, "_offer_port", offer)

    def record_stage(
        runtime: ShadowInstrumentationRuntime, route_adapter_id: str, **kwargs: Any
    ) -> None:
        del runtime, kwargs
        stage_calls.append(route_adapter_id)

    monkeypatch.setattr(ShadowInstrumentationRuntime, "try_stage", record_stage)
    headers = {"Authorization": f"Bearer {make_token(gp_user)}"}
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": date.today().isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }

    validation = client.post(
        "/api/v1/appointments",
        json={"patient_id": "not-a-uuid"},
        headers=headers,
    )
    assert validation.status_code == 422
    assert stage_calls == []

    def conflict(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise HTTPException(status_code=409, detail="authored-synthetic conflict")

    monkeypatch.setattr(appointments_router, "_create_appointment_from_body", conflict)
    conflict_response = client.post(
        "/api/v1/appointments", json=body, headers=headers
    )
    assert conflict_response.status_code == 409
    assert stage_calls == []

    def helper_failure(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise RuntimeError("authored-synthetic helper failure")

    monkeypatch.setattr(
        appointments_router, "_create_appointment_from_body", helper_failure
    )
    helper_response = client.post(
        "/api/v1/appointments", json=body, headers=headers
    )
    assert helper_response.status_code == 500
    assert stage_calls == []

    def invalid_result(*args: Any, **kwargs: Any) -> object:
        del args, kwargs
        return object()

    monkeypatch.setattr(
        appointments_router, "_create_appointment_from_body", invalid_result
    )
    serialization = client.post(
        "/api/v1/appointments", json=body, headers=headers
    )
    assert serialization.status_code == 500
    assert stage_calls == [RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID]
    assert offer.calls == []
    assert shadow_instrumentation_runtime.current_request_cell() is None


def test_route_adapter_population_is_exactly_four() -> None:
    assert SHADOW_ROUTE_ADAPTER_IDS == {
        RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID,
        RAW_COMPAT_UPDATE_SHADOW_ADAPTER_ID,
        RAW_COMPAT_STATUS_SHADOW_ADAPTER_ID,
        RAW_COMPAT_DELETE_SHADOW_ADAPTER_ID,
    }
