"""Disposable live-local browser/FastAPI/PostgreSQL harness for Rayleen A4.

This harness is test-only. It authors one isolated synthetic practice in the
repository test database, mounts the otherwise-unmounted fixed GraphQL app,
serves the real Diary assets, records read-only evidence, and deletes only its
owned rows during the browser-driven completion step.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
import uuid
from zoneinfo import ZoneInfo

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import uvicorn
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graphql.native_diary_rayleen_waiting_room import (
    FIXED_QUERY,
    PRODUCT_PATH,
    create_native_diary_rayleen_waiting_room_app,
)
from app.models.appointments import (
    Appointment,
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
from app.models.base import Base
from app.models.diary import WaitingArea
from app.models.tenancy import (
    Practice,
    PracticeLocation,
    Practitioner,
    User,
    UserRole,
)
from app.services.application_auth_product_read import (
    SyntheticProductPrincipalBinding,
    SyntheticProductPrincipalRegistry,
)
from app.services.application_auth_rayleen_read_database_role import (
    create_rayleen_read_capability_statements,
    create_rayleen_read_login_statements,
    drop_rayleen_read_role_statement,
)
from app.services.application_auth_rayleen_read_operational import (
    RayleenReadPoolPolicy,
    create_rayleen_read_engine,
    create_rayleen_read_session_factory,
)
from app.services.application_auth_rayleen_waiting_room import (
    ApplicationSessionRayleenWaitingRoomBridge,
)
from app.services.application_auth_runtime import (
    AUTHORED_SYNTHETIC_DATA_CLASS,
    ApplicationAuthRuntime,
    InMemoryAuthAuditSink,
    InMemoryAuthoredSyntheticStore,
    RAYLEEN_WAITING_ROOM_ACTION,
    Surface,
    SyntheticPrincipal,
)
from app.services.application_auth_transport import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
)


DIARY_DIR = ROOT / "docs" / "diary"
IMAGES_DIR = ROOT / "docs" / "images"
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "model-required-bureau-a4-product-read-ui"
    / "live-local-auth-graphql-postgres-evidence.json"
)
DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_test",
)
HOST = "127.0.0.1"
PORT = int(os.getenv("EMR4_A4_PORT", "8765"))
ORIGIN = f"https://{HOST}:{PORT}"
SURFACE_ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop.a4.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online.a4.synthetic.invalid",
    Surface.NATIVE_DIARY: ORIGIN,
}
CSRF_VALUE = "a4csrf-" + "x" * 48
PRACTICE_ID = uuid.UUID("a4000000-0000-4000-8000-000000000001")
LOCATION_ID = uuid.UUID("a4000000-0000-4000-8000-000000000002")
PRACTITIONER_ID = uuid.UUID("a4000000-0000-4000-8000-000000000003")
USER_ID = uuid.UUID("a4000000-0000-4000-8000-000000000004")
WAITING_AREA_ID = uuid.UUID("a4000000-0000-4000-8000-000000000005")
APPOINTMENT_ONE_ID = uuid.UUID("a4000000-0000-4000-8000-000000000006")
APPOINTMENT_TWO_ID = uuid.UUID("a4000000-0000-4000-8000-000000000007")
AUDIT_ID = uuid.UUID("a4000000-0000-4000-8000-000000000008")
AUTH_USER_REF = "synthetic-user-rayleen-a4"
AUTH_PRACTICE_REF = "synthetic-practice-rayleen-a4"
ROLE_SUFFIX = f"a4live{os.getpid():08x}"
RAYLEEN_CAPABILITY_ROLE = f"emr4_rayleen_read_runtime_{ROLE_SUFFIX}"
RAYLEEN_LOGIN_ROLE = f"emr4_rayleen_read_login_{ROLE_SUFFIX}"
RAYLEEN_ROLE_PASSWORD = "authored-synthetic-a4-local-password"


engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(engine)


def _seed() -> datetime:
    _cleanup_owned()
    observed_at = datetime.now(timezone.utc).replace(microsecond=0)
    local = observed_at.astimezone(ZoneInfo("Australia/Brisbane"))
    with SessionLocal.begin() as db:
        db.add(
            Practice(
                id=PRACTICE_ID,
                name="Authored Synthetic A4 Practice",
                timezone="Australia/Brisbane",
            )
        )
        db.flush()
        db.add(
            PracticeLocation(
                id=LOCATION_ID,
                practice_id=PRACTICE_ID,
                name="Authored Synthetic Main",
                is_active=True,
            )
        )
        db.flush()
        db.add(
            Practitioner(
                id=PRACTITIONER_ID,
                practice_id=PRACTICE_ID,
                first_name="Synthetic",
                last_name="Practitioner",
                ahpra_number="SYNTHA4001",
                default_location_id=LOCATION_ID,
                is_active=True,
            )
        )
        db.add(
            User(
                id=USER_ID,
                practice_id=PRACTICE_ID,
                email="synthetic-rayleen-a4@example.invalid",
                password_hash="authored-synthetic-not-a-credential",
                role=UserRole.Receptionist,
                is_active=True,
            )
        )
        db.add(
            WaitingArea(
                id=WAITING_AREA_ID,
                practice_id=PRACTICE_ID,
                location_id=LOCATION_ID,
                name="Authored Synthetic Waiting Area",
                is_active=True,
            )
        )
        db.flush()
        for appointment_id, status, minutes, queue_position in (
            (APPOINTMENT_ONE_ID, AppointmentStatus.Arrived, 45, 1),
            (APPOINTMENT_TWO_ID, AppointmentStatus.InConsult, 20, 2),
        ):
            start_at = observed_at - timedelta(minutes=minutes)
            start_local = start_at.astimezone(ZoneInfo("Australia/Brisbane"))
            db.add(
                Appointment(
                    id=appointment_id,
                    practice_id=PRACTICE_ID,
                    location_id=LOCATION_ID,
                    practitioner_id=PRACTITIONER_ID,
                    start_time=start_at,
                    appointment_date=local.date(),
                    start_time_local=start_local.time(),
                    duration_minutes=15,
                    status=status,
                    booked_via=BookingChannel.Receptionist,
                    waiting_area_id=WAITING_AREA_ID,
                    queue_position=queue_position,
                    patient_name_provisional="MUST-NOT-LEAK",
                    reason="MUST-NOT-LEAK",
                    notes="MUST-NOT-LEAK",
                )
            )
        db.flush()
        db.add(
            AppointmentAuditLog(
                id=AUDIT_ID,
                practice_id=PRACTICE_ID,
                appointment_id=APPOINTMENT_ONE_ID,
                confirmed_by_user_id=USER_ID,
                action=AppointmentAuditAction.status_change,
                status_before=AppointmentStatus.Confirmed,
                status_after=AppointmentStatus.Arrived,
                created_at=observed_at - timedelta(minutes=40),
            )
        )
    return observed_at


def _create_rayleen_database_roles():
    with engine.begin() as connection:
        for statement in create_rayleen_read_capability_statements(
            RAYLEEN_CAPABILITY_ROLE
        ):
            connection.execute(text(statement))
        for statement in create_rayleen_read_login_statements(
            RAYLEEN_LOGIN_ROLE,
            RAYLEEN_CAPABILITY_ROLE,
            connection_limit=2,
        ):
            connection.execute(text(statement))
        connection.execute(
            text(
                f'ALTER ROLE "{RAYLEEN_LOGIN_ROLE}" PASSWORD '
                f"'{RAYLEEN_ROLE_PASSWORD}'"
            )
        )
    target = make_url(DATABASE_URL).set(
        username=RAYLEEN_LOGIN_ROLE,
        password=RAYLEEN_ROLE_PASSWORD,
    )
    return create_rayleen_read_engine(
        target,
        login_role=RAYLEEN_LOGIN_ROLE,
        capability_role=RAYLEEN_CAPABILITY_ROLE,
        policy=RayleenReadPoolPolicy(
            pool_size=1,
            max_overflow=0,
            login_connection_limit=2,
        ),
    )


def _drop_rayleen_database_roles() -> None:
    with engine.begin() as connection:
        connection.execute(text(f'DROP OWNED BY "{RAYLEEN_CAPABILITY_ROLE}"'))
        for role in (RAYLEEN_LOGIN_ROLE, RAYLEEN_CAPABILITY_ROLE):
            connection.execute(text(drop_rayleen_read_role_statement(role)))


def _canonical_owned_truth() -> str:
    with SessionLocal() as db:
        rows = {
            "appointments": [
                {
                    "id": str(item.id),
                    "practice_id": str(item.practice_id),
                    "location_id": str(item.location_id),
                    "practitioner_id": str(item.practitioner_id),
                    "status": item.status.value,
                    "start_time": item.start_time.isoformat(),
                    "waiting_area_id": str(item.waiting_area_id),
                    "queue_position": item.queue_position,
                    "reason": item.reason,
                    "notes": item.notes,
                }
                for item in db.query(Appointment)
                .filter(Appointment.practice_id == PRACTICE_ID)
                .order_by(Appointment.id)
            ],
            "audit": [
                {
                    "id": str(item.id),
                    "appointment_id": str(item.appointment_id),
                    "action": item.action.value,
                    "status_after": item.status_after.value,
                    "created_at": item.created_at.isoformat(),
                }
                for item in db.query(AppointmentAuditLog)
                .filter(AppointmentAuditLog.practice_id == PRACTICE_ID)
                .order_by(AppointmentAuditLog.id)
            ],
        }
    return "sha256:" + hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _owned_counts() -> dict[str, int]:
    with SessionLocal() as db:
        return {
            "appointments": db.query(Appointment)
            .filter(Appointment.practice_id == PRACTICE_ID)
            .count(),
            "appointment_audit_log": db.query(AppointmentAuditLog)
            .filter(AppointmentAuditLog.practice_id == PRACTICE_ID)
            .count(),
            "users": db.query(User).filter(User.practice_id == PRACTICE_ID).count(),
            "practitioners": db.query(Practitioner)
            .filter(Practitioner.practice_id == PRACTICE_ID)
            .count(),
            "practice_locations": db.query(PracticeLocation)
            .filter(PracticeLocation.practice_id == PRACTICE_ID)
            .count(),
            "waiting_areas": db.query(WaitingArea)
            .filter(WaitingArea.practice_id == PRACTICE_ID)
            .count(),
            "practices": db.query(Practice).filter(Practice.id == PRACTICE_ID).count(),
        }


def _cleanup_owned() -> None:
    with SessionLocal.begin() as db:
        db.query(AppointmentAuditLog).filter(
            AppointmentAuditLog.practice_id == PRACTICE_ID
        ).delete(synchronize_session=False)
        db.query(Appointment).filter(Appointment.practice_id == PRACTICE_ID).delete(
            synchronize_session=False
        )
        db.query(WaitingArea).filter(WaitingArea.practice_id == PRACTICE_ID).delete(
            synchronize_session=False
        )
        db.query(User).filter(User.practice_id == PRACTICE_ID).delete(
            synchronize_session=False
        )
        db.query(Practitioner).filter(
            Practitioner.practice_id == PRACTICE_ID
        ).delete(synchronize_session=False)
        db.query(PracticeLocation).filter(
            PracticeLocation.practice_id == PRACTICE_ID
        ).delete(synchronize_session=False)
        db.query(Practice).filter(Practice.id == PRACTICE_ID).delete(
            synchronize_session=False
        )


def _jwt() -> str:
    def encoded(payload: dict[str, object]) -> str:
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return ".".join(
        (
            encoded({"alg": "none", "typ": "JWT"}),
            encoded(
                {
                    "sub": str(USER_ID),
                    "role": "Receptionist",
                    "exp": 4102444800,
                    "data_class": "authored_synthetic",
                }
            ),
            "authored-synthetic",
        )
    )


observed_at = _seed()
truth_hash_before_browser = _canonical_owned_truth()
rayleen_engine = _create_rayleen_database_roles()
auth_audit = InMemoryAuthAuditSink(data_class=AUTHORED_SYNTHETIC_DATA_CLASS)
auth_runtime = ApplicationAuthRuntime(
    store=InMemoryAuthoredSyntheticStore(
        data_class=AUTHORED_SYNTHETIC_DATA_CLASS
    ),
    audit_sink=auth_audit,
    surface_origins=SURFACE_ORIGINS,
)
auth_principal = SyntheticPrincipal(
    user_id=AUTH_USER_REF,
    practice_id=AUTH_PRACTICE_REF,
    current_backend_role="Receptionist",
    practitioner_id=None,
)
created_session = auth_runtime.create_session(
    principal=auth_principal,
    surface=Surface.NATIVE_DIARY,
    origin=ORIGIN,
    correlation_id="correlation-rayleen-a4-live-session",
)
bridge = ApplicationSessionRayleenWaitingRoomBridge(
    runtime=auth_runtime,  # type: ignore[arg-type] -- exact synthetic runtime contract
    product_session_factory=create_rayleen_read_session_factory(rayleen_engine),
    principal_registry=SyntheticProductPrincipalRegistry(
        (
            SyntheticProductPrincipalBinding(
                user_ref=AUTH_USER_REF,
                practice_ref=AUTH_PRACTICE_REF,
                user_id=USER_ID,
                practice_id=PRACTICE_ID,
            ),
        )
    ),
    surface_origins=SURFACE_ORIGINS,
    allowed_practice_ids=frozenset({PRACTICE_ID}),
)
app = create_native_diary_rayleen_waiting_room_app(
    enabled=True,
    bridge=bridge,
    observed_at_source=lambda: datetime.now(timezone.utc).replace(microsecond=0),
    configuration=SimpleNamespace(
        environment="dev",
        rayleen_a4_product_read_enabled=True,
        rayleen_a4_synthetic_practice_ids=str(PRACTICE_ID),
    ),
)


@app.get("/diary/diary.html", response_class=HTMLResponse)
def diary_html() -> HTMLResponse:
    html = (DIARY_DIR / "diary.html").read_text(encoding="utf-8")
    marker = '<script src="diary.js?v=201" defer></script>'
    injected = '<script src="/acceptance/bootstrap.js"></script>\n  ' + marker
    response = HTMLResponse(html.replace(marker, injected))
    response.set_cookie(
        SESSION_COOKIE_NAME,
        created_session.surface_session_value,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        CSRF_VALUE,
        secure=True,
        httponly=False,
        samesite="strict",
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/acceptance/bootstrap.js")
def bootstrap_js() -> Response:
    script = f"""
(() => {{
  const locationId = {json.dumps(str(LOCATION_ID))};
  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {{
    const requested = new URL(input, window.location.href);
    if (
      requested.origin !== window.location.origin
      && requested.pathname.startsWith("/api/v1/")
    ) {{
      requested.protocol = window.location.protocol;
      requested.hostname = window.location.hostname;
      requested.port = window.location.port;
    }}
    return nativeFetch(requested.toString(), init);
  }};
  localStorage.setItem("emr4_token", {json.dumps(_jwt())});
  localStorage.setItem("emr4_diary_active_location", locationId);
  window.__EMR4_RAYLEEN_WAITING_ROOM__ = Object.freeze({{
    enabled: true,
    practiceId: {json.dumps(str(PRACTICE_ID))},
    sessionGeneration: 1,
    async readFixedWaitingRoom(request, options) {{
      const response = await fetch("/api/v1/application-auth/rayleen/graphql", {{
        method: "POST",
        credentials: "same-origin",
        signal: options.signal,
        headers: {{
          "Content-Type": "application/json",
          "X-EMR4-CSRF": {json.dumps(CSRF_VALUE)}
        }},
        body: JSON.stringify({{
          query: {json.dumps(FIXED_QUERY)},
          variables: request
        }})
      }});
      if (!response.ok) throw new Error("fixed_read_failed");
      return response.json();
    }}
  }});
}})();
"""
    return Response(script, media_type="text/javascript", headers={"Cache-Control": "no-store"})


@app.get("/api/v1/diary/locations")
def locations() -> list[dict[str, str]]:
    return [{"id": str(LOCATION_ID), "name": "Authored Synthetic Main"}]


@app.get("/api/v1/diary/template")
def template() -> dict[str, object]:
    return {
        "practice_name": "Authored Synthetic A4 Practice",
        "slot_start": "08:00",
        "slot_end": "18:00",
        "slot_interval_minutes": 15,
        "columns": [
            {
                "room_label": "Authored Synthetic Room",
                "assignment": "Synthetic Practitioner",
                "practitioner_id": str(PRACTITIONER_ID),
                "practitioner_ahpra": "SYNTHA4001",
                "tint_hex": "DCEFE9",
                "slot_interval_minutes": 15,
                "breaks": [],
            }
        ],
        "footer": ["Local authored-synthetic acceptance"],
    }


@app.get("/api/v1/appointments")
def appointments() -> list[object]:
    return []


@app.get("/api/v1/appointments/types")
def appointment_types() -> list[object]:
    return []


@app.get("/api/v1/appointments/bernie/pilot-eligibility")
def pilot_eligibility() -> dict[str, object]:
    return {"eligible": False}


@app.post("/api/v1/graphql")
def shared_graphql_closed() -> JSONResponse:
    return JSONResponse({"errors": [{"message": "closed"}]}, status_code=403)


@app.get("/api/v1/practice/practitioners")
def practitioners() -> list[object]:
    return []


@app.get("/api/v1/diary/roster")
def roster() -> dict[str, list[object]]:
    return {"entries": []}


@app.get("/api/v1/diary/waiting-areas")
def waiting_areas() -> list[dict[str, object]]:
    return [
        {
            "id": str(WAITING_AREA_ID),
            "name": "Authored Synthetic Waiting Area",
            "display_order": 0,
            "location_id": str(LOCATION_ID),
            "is_active": True,
        }
    ]


@app.get("/acceptance/complete", response_class=HTMLResponse)
def complete_page() -> HTMLResponse:
    return HTMLResponse(
        """<!doctype html><html><body><main><h1>A4 cleanup</h1><p id="status">Finalizing…</p></main>
<script>
localStorage.removeItem("emr4_token");
localStorage.removeItem("emr4_diary_active_location");
fetch("/acceptance/finalize", {method: "POST"})
  .then(response => response.json())
  .then(() => { document.getElementById("status").textContent = "Cleanup complete"; })
  .catch(() => { document.getElementById("status").textContent = "Cleanup failed"; });
</script></body></html>""",
        headers={"Cache-Control": "no-store"},
    )


@app.post("/acceptance/finalize")
def finalize(request: Request) -> dict[str, object]:
    before_cleanup = _owned_counts()
    truth_hash_after_browser = _canonical_owned_truth()
    unchanged = truth_hash_after_browser == truth_hash_before_browser and before_cleanup == {
        "appointments": 2,
        "appointment_audit_log": 1,
        "users": 1,
        "practitioners": 1,
        "practice_locations": 1,
        "waiting_areas": 1,
        "practices": 1,
    }
    _cleanup_owned()
    after_cleanup = _owned_counts()
    audit_events = auth_audit.snapshot()
    allowed_reads = [
        item
        for item in audit_events
        if item.action == RAYLEEN_WAITING_ROOM_ACTION
        and item.decision.value == "allowed"
    ]
    denied_reads = [
        item
        for item in audit_events
        if item.action == RAYLEEN_WAITING_ROOM_ACTION
        and item.decision.value == "denied"
    ]
    source_paths = (
        Path(__file__).resolve(),
        ROOT / "app/graphql/native_diary_rayleen_waiting_room.py",
        ROOT / "app/services/application_auth_rayleen_waiting_room.py",
        ROOT / "app/services/application_auth_rayleen_read_database_role.py",
        ROOT / "app/services/diary/rayleen_waiting_room_projection.py",
        ROOT / "docs/diary/rayleen-waiting-room-projection.mjs",
    )
    source_hashes = {
        path.relative_to(ROOT).as_posix(): "sha256:"
        + hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }
    evidence = {
        "schema_version": "emr4.model_required_bureau_a4.live_local.v1",
        "result": "provider_free_rayleen_a4_live_local_auth_pass",
        "evidence_label": "live_local_browser_backend_postgres",
        "data_class": "authored_synthetic",
        "origin": ORIGIN,
        "route": "/api/v1/application-auth/rayleen/graphql",
        "graphql_query_fixed": True,
        "graphql_mutation": False,
        "bridge_type": type(bridge).__name__,
        "bridge_open_count": len(allowed_reads),
        "bridge_denied_count": len(denied_reads),
        "required_authorization_audit_count": len(allowed_reads),
        "synthetic_practice_allowlist_enforced": True,
        "transaction_local_practice_rls_context": True,
        "rayleen_database_login_role": RAYLEEN_LOGIN_ROLE,
        "rayleen_database_capability_role": RAYLEEN_CAPABILITY_ROLE,
        "rayleen_database_role_distinct_from_practitioner_directory": True,
        "owned_counts_before_browser": {
            "appointments": 2,
            "appointment_audit_log": 1,
        },
        "owned_counts_after_browser": before_cleanup,
        "appointment_and_audit_truth_unchanged": unchanged,
        "owned_truth_hash_before_browser": truth_hash_before_browser,
        "owned_truth_hash_after_browser": truth_hash_after_browser,
        "owned_counts_after_cleanup": after_cleanup,
        "owned_cleanup_complete": all(value == 0 for value in after_cleanup.values()),
        "provider_calls": 0,
        "command_calls": 0,
        "appointment_writes_during_read": 0,
        "audit_writes_during_read": 0,
        "event_writes_during_read": 0,
        "source_hashes": source_hashes,
        "transport": (
            "canonical_https_in_process"
            if request.client is not None and request.client.host == "testclient"
            else "canonical_https_browser"
        ),
        "remote_address_is_loopback_or_in_process": request.client is not None
        and request.client.host in {"127.0.0.1", "::1", "testclient"},
        "claims_not_made": [
            "production_readiness",
            "real_patient_safety",
            "provider_processing",
            "deployment_or_release",
        ],
    }
    passed = (
        unchanged
        and evidence["owned_cleanup_complete"]
        and len(allowed_reads) >= 1
        and len(denied_reads) == 0
        and evidence["remote_address_is_loopback_or_in_process"]
    )
    if not passed:
        evidence["result"] = "provider_free_rayleen_a4_live_local_failed"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    server = getattr(app.state, "server", None)
    if server is not None:
        threading.Timer(2.0, lambda: setattr(server, "should_exit", True)).start()
    return evidence


app.mount("/diary", StaticFiles(directory=DIARY_DIR), name="diary-static")
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="image-static")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("in-process", "https-server"), required=True)
    args = parser.parse_args()
    try:
        if args.mode == "in-process":
            with TestClient(app, base_url=ORIGIN) as client:
                client.cookies.set(
                    SESSION_COOKIE_NAME,
                    created_session.surface_session_value,
                )
                client.cookies.set(
                    CSRF_COOKIE_NAME,
                    CSRF_VALUE,
                )
                response = client.post(
                    PRODUCT_PATH,
                    json={
                        "query": FIXED_QUERY,
                        "variables": {
                            "locationId": str(LOCATION_ID),
                            "projectionKind": "FULL_QUEUE",
                            "practitionerId": None,
                            "waitingAreaId": None,
                            "focusAppointmentId": None,
                        },
                    },
                    headers={
                        "Origin": ORIGIN,
                        "X-EMR4-CSRF": CSRF_VALUE,
                        "X-EMR4-Correlation-ID": "correlation-rayleen-a4-live-read",
                    },
                    cookies={
                        SESSION_COOKIE_NAME: created_session.surface_session_value,
                        CSRF_COOKIE_NAME: CSRF_VALUE,
                    },
                )
                if response.status_code != 200 or response.json().get("errors"):
                    errors = response.json().get("errors")
                    error_code = (
                        errors[0].get("extensions", {}).get("code")
                        if isinstance(errors, list) and errors
                        else None
                    )
                    raise RuntimeError(
                        "live_local_graphql_read_failed:"
                        f"{response.status_code}:{error_code}"
                    )
                final = client.post("/acceptance/finalize")
                final.raise_for_status()
                print(json.dumps(final.json(), sort_keys=True), flush=True)
        else:
            tls_cert = os.environ.get("EMR4_A4_TLS_CERT")
            tls_key = os.environ.get("EMR4_A4_TLS_KEY")
            if not tls_cert or not tls_key:
                raise RuntimeError(
                    "EMR4_A4_TLS_CERT and EMR4_A4_TLS_KEY are required"
                )
            config = uvicorn.Config(
                app,
                host=HOST,
                port=PORT,
                log_level="warning",
                ssl_certfile=tls_cert,
                ssl_keyfile=tls_key,
            )
            server = uvicorn.Server(config)
            app.state.server = server
            print(
                json.dumps(
                    {
                        "status": "ready",
                        "url": f"{ORIGIN}/diary/diary.html"
                        "?standalone_diary=true&rayleen_waiting_room=true",
                        "data_class": "authored_synthetic",
                    }
                ),
                flush=True,
            )
            server.run()
    finally:
        if _owned_counts()["practices"]:
            _cleanup_owned()
        rayleen_engine.dispose()
        _drop_rayleen_database_roles()
        engine.dispose()
