"""Provider-free acceptance for the default-off Rayleen A4 product read."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import uuid
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from graphql import parse
import pytest

import app.graphql.native_diary_rayleen_waiting_room as adapter
from app.graphql.native_diary_rayleen_waiting_room import (
    FIXED_QUERY,
    PRODUCT_PATH,
    RAYLEEN_SCHEMA,
    create_native_diary_rayleen_waiting_room_app,
)
from app.models.appointments import (
    Appointment,
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary import WaitingArea
from app.models.tenancy import PracticeLocation, UserRole
from app.services.application_auth_runtime import (
    RAYLEEN_WAITING_ROOM_ACTION,
    RAYLEEN_WAITING_ROOM_POLICY_VERSION,
    RAYLEEN_WAITING_ROOM_RESOURCE_TYPE,
    AuthAuditEventType,
    AuthRuntimeDenied,
    Surface,
    SyntheticPrincipal,
)
from app.services.application_auth_product_read_database_role import (
    create_product_read_capability_statements,
)
from app.services.application_auth_rayleen_read_database_role import (
    create_rayleen_read_capability_statements,
)
from app.services.application_auth_rayleen_waiting_room import (
    ApplicationSessionRayleenWaitingRoomBridge,
)
from app.services.diary.rayleen_waiting_room_projection import (
    EXCLUDED_FIELD_CLASSES,
    ProjectionKind,
    WaitingRoomReadDenied,
    read_waiting_room_projection,
)
from tests.test_raisa_shared_application_auth_runtime_foundation import (
    ORIGINS,
    runtime_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/emr4-model-required-bureau-a4-product-read-ui-plan.md"
THREAT = ROOT / "docs/security/emr4-model-required-bureau-a4-product-read-ui-threat-model-delta.md"
OBSERVED_AT = datetime(2026, 8, 5, 2, 0, tzinfo=timezone.utc)


def _location(db, practice, *, name: str = "Authored Synthetic Main"):
    location = PracticeLocation(
        practice_id=practice.id,
        name=name,
        is_active=True,
    )
    db.add(location)
    db.flush()
    return location


def _appointment(
    db,
    *,
    practice,
    location,
    practitioner,
    status: AppointmentStatus,
    start_at: datetime,
    waiting_area_id: uuid.UUID | None = None,
    queue_position: int | None = None,
):
    item = Appointment(
        practice_id=practice.id,
        location_id=location.id,
        practitioner_id=practitioner.id,
        start_time=start_at,
        appointment_date=start_at.astimezone(ZoneInfo(practice.timezone)).date(),
        start_time_local=start_at.astimezone(ZoneInfo(practice.timezone)).time(),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
        waiting_area_id=waiting_area_id,
        queue_position=queue_position,
        patient_name_provisional="MUST-NOT-LEAK",
        reason="MUST-NOT-LEAK",
        notes="MUST-NOT-LEAK",
    )
    db.add(item)
    db.flush()
    return item


def _arrival_audit(db, *, appointment, user, arrived_at: datetime) -> None:
    db.add(
        AppointmentAuditLog(
            practice_id=appointment.practice_id,
            appointment_id=appointment.id,
            confirmed_by_user_id=user.id,
            action=AppointmentAuditAction.status_change,
            status_before=AppointmentStatus.Confirmed,
            status_after=AppointmentStatus.Arrived,
            created_at=arrived_at,
        )
    )
    db.flush()


def _frame(db, receptionist_user, location, **overrides):
    arguments = {
        "db": db,
        "current_user": receptionist_user,
        "location_id": location.id,
        "observed_at": OBSERVED_AT,
    }
    arguments.update(overrides)
    return read_waiting_room_projection(**arguments)


def test_plan_and_threat_model_bind_the_closed_a4_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for marker in (
        "default-off",
        "Receptionist only",
        "GraphQL",
        "no Mutation",
        "live_local_browser_backend_postgres",
        "gemini-2.5-flash",
        "thinkingBudget: 1024",
    ):
        assert marker in plan
    for marker in (
        "Cross-practice",
        "Missing arrival timestamp",
        "GraphQL becomes a command/provider tunnel",
        "Stale or out-of-order response",
    ):
        assert marker in threat


def test_schema_is_query_only_and_request_is_fixed() -> None:
    assert RAYLEEN_SCHEMA._schema.mutation_type is None
    document = parse(FIXED_QUERY)
    assert len(document.definitions) == 1
    operation = document.definitions[0]
    assert operation.operation.value == "query"
    assert operation.name is not None
    assert operation.name.value == "RayleenWaitingRoom"
    assert "mutation" not in FIXED_QUERY.casefold()
    assert "patientName" not in FIXED_QUERY
    assert "reason" not in FIXED_QUERY
    assert "notes" not in FIXED_QUERY


def test_product_read_role_grants_only_the_a4_minimal_waiting_room_columns() -> None:
    sql = "\n".join(
        create_rayleen_read_capability_statements(
            "emr4_rayleen_read_runtime_rayleen_a4"
        )
    ).casefold()
    for required in (
        "select (id, timezone) on table public.practices",
        "appointment_date, start_time_local, waiting_area_id, queue_position",
        "on table public.appointments",
        "select (practice_id, appointment_id, action, status_after, created_at)",
        "on table public.appointment_audit_log",
    ):
        assert required in sql
    for prohibited in (
        "patient_id",
        "patient_name_provisional",
        "reason",
        "notes",
        "cancellation_reason",
        "confirmed_by_user_id",
        "confirmed_warnings",
        "insert on",
        "update on",
        "delete on",
    ):
        assert prohibited not in sql

    shared_sql = "\n".join(
        create_product_read_capability_statements(
            "emr4_product_read_runtime_shared_a4"
        )
    ).casefold()
    assert "public.appointments" not in shared_sql
    assert "public.appointment_audit_log" not in shared_sql


def test_receptionist_read_is_minimized_deterministic_and_write_free(
    db,
    practice,
    practitioner,
    receptionist_user,
) -> None:
    practice.timezone = "Australia/Brisbane"
    location = _location(db, practice)
    waiting_area = WaitingArea(
        practice_id=practice.id,
        location_id=location.id,
        name="Authored Synthetic Waiting Area",
    )
    db.add(waiting_area)
    db.flush()
    arrived = _appointment(
        db,
        practice=practice,
        location=location,
        practitioner=practitioner,
        status=AppointmentStatus.Arrived,
        start_at=datetime(2026, 8, 5, 1, 15, tzinfo=timezone.utc),
        waiting_area_id=waiting_area.id,
        queue_position=1,
    )
    missing = _appointment(
        db,
        practice=practice,
        location=location,
        practitioner=practitioner,
        status=AppointmentStatus.InConsult,
        start_at=datetime(2026, 8, 5, 1, 30, tzinfo=timezone.utc),
        waiting_area_id=waiting_area.id,
        queue_position=2,
    )
    _arrival_audit(
        db,
        appointment=arrived,
        user=receptionist_user,
        arrived_at=datetime(2026, 8, 5, 1, 20, tzinfo=timezone.utc),
    )
    before = (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )

    result = _frame(db, receptionist_user, location)
    frame = result.frame

    assert frame.schema_version == "emr4.waiting_room_context_frame.v1"
    assert result.projection.kind is ProjectionKind.full_queue
    assert result.projection.writes_authorized is False
    assert frame.excluded_field_classes == EXCLUDED_FIELD_CLASSES
    assert {fact.appointment_id for fact in frame.backend_facts} == {
        arrived.id,
        missing.id,
    }
    assert len({fact.patient_display_token for fact in frame.backend_facts}) == 2
    assert all(
        fact.patient_display_token.startswith("synthetic:patient-")
        and len(fact.patient_display_token) == len("synthetic:patient-") + 12
        for fact in frame.backend_facts
    )
    serialized = repr(frame)
    assert "MUST-NOT-LEAK" not in serialized
    assert "patient_name" not in serialized
    assert "reason=" not in serialized
    assert "notes=" not in serialized
    arrived_signals = {
        signal.kind: signal.value
        for signal in frame.derived_signals
        if signal.appointment_id == arrived.id
    }
    assert arrived_signals == {
        "elapsed_wait_minutes": 40,
        "threshold_band": "30_minutes_or_more",
        "longest_wait_rank": 1,
    }
    missing_signals = {
        signal.kind: signal.value
        for signal in frame.derived_signals
        if signal.appointment_id == missing.id
    }
    assert missing_signals == {"flow_exception": "missing_arrival_timestamp"}
    assert (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    ) == before


def test_practice_timezone_controls_today_at_utc_date_boundary(
    db,
    practice,
    practitioner,
    receptionist_user,
) -> None:
    practice.timezone = "Australia/Brisbane"
    location = _location(db, practice)
    observed = datetime(2026, 8, 5, 14, 30, tzinfo=timezone.utc)
    tomorrow_local = _appointment(
        db,
        practice=practice,
        location=location,
        practitioner=practitioner,
        status=AppointmentStatus.Booked,
        start_at=datetime(2026, 8, 5, 23, 0, tzinfo=timezone.utc),
    )
    tomorrow_local.appointment_date = date(2026, 8, 6)
    yesterday_local = _appointment(
        db,
        practice=practice,
        location=location,
        practitioner=practitioner,
        status=AppointmentStatus.Booked,
        start_at=datetime(2026, 8, 5, 8, 0, tzinfo=timezone.utc),
    )
    yesterday_local.appointment_date = date(2026, 8, 5)
    db.flush()

    result = read_waiting_room_projection(
        db,
        current_user=receptionist_user,
        location_id=location.id,
        observed_at=observed,
    )

    assert [item.appointment_id for item in result.frame.backend_facts] == [
        tomorrow_local.id
    ]


@pytest.mark.parametrize(
    "role",
    [UserRole.GP, UserRole.Nurse, UserRole.Admin, UserRole.PracticeOwner],
)
def test_non_reception_roles_fail_closed_before_release(
    db,
    practice,
    practitioner,
    receptionist_user,
    role,
) -> None:
    location = _location(db, practice)
    receptionist_user.role = role
    db.flush()
    with pytest.raises(WaitingRoomReadDenied, match="role_not_authorized"):
        _frame(db, receptionist_user, location)


def test_foreign_location_and_foreign_selector_fail_closed(
    db,
    practice,
    practice_b,
    practitioner,
    receptionist_user,
) -> None:
    own_location = _location(db, practice)
    foreign_location = _location(db, practice_b, name="Foreign")
    _appointment(
        db,
        practice=practice,
        location=own_location,
        practitioner=practitioner,
        status=AppointmentStatus.Booked,
        start_at=datetime(2026, 8, 5, 1, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(WaitingRoomReadDenied, match="location_not_authorized"):
        _frame(db, receptionist_user, foreign_location)
    with pytest.raises(WaitingRoomReadDenied, match="practitioner_not_authorized"):
        _frame(
            db,
            receptionist_user,
            own_location,
            projection_kind=ProjectionKind.practitioner_group,
            practitioner_id=uuid.uuid4(),
        )


def _receptionist_principal() -> SyntheticPrincipal:
    return SyntheticPrincipal(
        user_id="synthetic-user-reception-001",
        practice_id="synthetic-practice-001",
        current_backend_role="Receptionist",
        practitioner_id=None,
    )


def test_runtime_authorizes_receptionist_diary_read_and_audits_before_release() -> None:
    runtime, _store, audit, _clock = runtime_bundle()
    principal = _receptionist_principal()
    created = runtime.create_session(
        principal=principal,
        surface=Surface.NATIVE_DIARY,
        origin=ORIGINS[Surface.NATIVE_DIARY],
    )

    context = runtime.authorize_rayleen_waiting_room_read(
        surface_session_value=created.surface_session_value,
        surface=Surface.NATIVE_DIARY,
        origin=ORIGINS[Surface.NATIVE_DIARY],
        fresh_principal=principal,
        fresh_user_active=True,
        resource_practice_id=principal.practice_id,
        correlation_id="correlation-rayleen-a4",
    )

    assert context.current_backend_role == "Receptionist"
    event = audit.snapshot()[-1]
    assert event.event_type is AuthAuditEventType.AUTHORIZATION_ALLOWED
    assert event.action == RAYLEEN_WAITING_ROOM_ACTION
    assert event.resource_type == RAYLEEN_WAITING_ROOM_RESOURCE_TYPE
    assert event.policy_version == RAYLEEN_WAITING_ROOM_POLICY_VERSION


def test_runtime_denies_other_role_and_wrong_practice_with_required_audit() -> None:
    for principal, resource_practice_id, reason in (
        (
            SyntheticPrincipal(
                user_id="synthetic-user-gp-a4",
                practice_id="synthetic-practice-001",
                current_backend_role="GP",
                practitioner_id="synthetic-practitioner-a4",
            ),
            "synthetic-practice-001",
            "receptionist_role_required",
        ),
        (
            _receptionist_principal(),
            "synthetic-practice-other",
            "resource_practice_mismatch",
        ),
    ):
        runtime, _store, audit, _clock = runtime_bundle()
        created = runtime.create_session(
            principal=principal,
            surface=Surface.NATIVE_DIARY,
            origin=ORIGINS[Surface.NATIVE_DIARY],
        )
        with pytest.raises(AuthRuntimeDenied) as caught:
            runtime.authorize_rayleen_waiting_room_read(
                surface_session_value=created.surface_session_value,
                surface=Surface.NATIVE_DIARY,
                origin=ORIGINS[Surface.NATIVE_DIARY],
                fresh_principal=principal,
                fresh_user_active=True,
                resource_practice_id=resource_practice_id,
            )
        assert caught.value.reason_code == reason
        event = audit.snapshot()[-1]
        assert event.event_type is AuthAuditEventType.AUTHORIZATION_DENIED
        assert event.reason_codes == (reason,)


class _FakeDB:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _FakeBridge(ApplicationSessionRayleenWaitingRoomBridge):
    def __init__(self) -> None:
        self.db = _FakeDB()
        self.open_calls: list[dict[str, object]] = []
        self.allowed_practice_ids = frozenset(
            {uuid.UUID("11111111-1111-4111-8111-111111111111")}
        )

    def open_context(self, **kwargs):
        self.open_calls.append(kwargs)
        return SimpleNamespace(
            db=self.db,
            current_user=SimpleNamespace(
                practice_id=uuid.UUID("11111111-1111-4111-8111-111111111111")
            ),
        )


def _configuration(*, enabled: bool = True, environment: str = "dev"):
    return SimpleNamespace(
        environment=environment,
        rayleen_a4_product_read_enabled=enabled,
        rayleen_a4_synthetic_practice_ids=(
            "11111111-1111-4111-8111-111111111111"
        ),
    )


def test_disabled_app_exposes_no_route_docs_or_database() -> None:
    bridge = _FakeBridge()
    app = create_native_diary_rayleen_waiting_room_app(
        enabled=False,
        bridge=bridge,
        configuration=_configuration(enabled=False),
    )
    with TestClient(app) as client:
        assert client.post(PRODUCT_PATH, json={"query": FIXED_QUERY}).status_code == 404
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
    assert bridge.open_calls == []


def test_fixed_guard_rejects_extra_query_or_variables_before_bridge() -> None:
    bridge = _FakeBridge()
    app = create_native_diary_rayleen_waiting_room_app(
        enabled=True,
        bridge=bridge,
        configuration=_configuration(),
    )
    exact_variables = {
        "locationId": "11111111-1111-4111-8111-111111111111",
        "projectionKind": "FULL_QUEUE",
        "practitionerId": None,
        "waitingAreaId": None,
        "focusAppointmentId": None,
    }
    with TestClient(app) as client:
        assert client.post(
            PRODUCT_PATH,
            json={"query": FIXED_QUERY + "\n", "variables": exact_variables},
        ).status_code == 403
        assert client.post(
            PRODUCT_PATH,
            json={
                "query": FIXED_QUERY,
                "variables": {**exact_variables, "practiceId": str(uuid.uuid4())},
            },
        ).status_code == 403
    assert bridge.open_calls == []


def test_exact_graphql_request_releases_only_the_closed_frame(monkeypatch) -> None:
    bridge = _FakeBridge()
    frame = SimpleNamespace(
        schema_version="emr4.waiting_room_context_frame.v1",
        frame_id=uuid.UUID("22222222-2222-4222-8222-222222222222"),
        practice_id=uuid.UUID("11111111-1111-4111-8111-111111111111"),
        location_id=uuid.UUID("33333333-3333-4333-8333-333333333333"),
        context_revision=7,
        generated_at=OBSERVED_AT,
        expires_at=datetime(2026, 8, 5, 2, 2, tzinfo=timezone.utc),
        reader="authorized_reception_surface",
        backend_facts=(),
        derived_signals=(),
        excluded_field_classes=EXCLUDED_FIELD_CLASSES,
    )
    projection = SimpleNamespace(
            kind=ProjectionKind.full_queue,
            selected_count=0,
            practitioner_id=None,
            waiting_area_id=None,
            focus_appointment_id=None,
            selector_provenance="deterministic_product_read",
            authority_ceiling="data_only",
            writes_authorized=False,
    )
    result = SimpleNamespace(frame=frame, projection=projection)
    monkeypatch.setattr(
        adapter,
        "read_waiting_room_projection",
        lambda *args, **kwargs: result,
    )
    app = create_native_diary_rayleen_waiting_room_app(
        enabled=True,
        bridge=bridge,
        configuration=_configuration(),
    )
    variables = {
        "locationId": str(frame.location_id),
        "projectionKind": "FULL_QUEUE",
        "practitionerId": None,
        "waitingAreaId": None,
        "focusAppointmentId": None,
    }
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={"query": FIXED_QUERY, "variables": variables},
            headers={"Origin": ORIGINS[Surface.NATIVE_DIARY]},
        )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    released = response.json()["data"]["rayleenWaitingRoom"]
    assert released["contextRevision"] == 7
    assert released["backendFacts"] == []
    assert released["derivedSignals"] == []
    assert released["projection"]["writesAuthorized"] is False
    assert set(released) == {
        "schemaVersion",
        "frameId",
        "practiceId",
        "locationId",
        "contextRevision",
        "generatedAt",
        "expiresAt",
        "reader",
        "excludedFieldClasses",
        "projection",
        "backendFacts",
        "derivedSignals",
    }
    assert bridge.db.closed is True
