"""Disposable provider-disabled runtime for live-local meta-grid acceptance.

The harness owns one exact loopback PostgreSQL database populated only with
newly authored synthetic records.  It serves the ordinary Diary and never
intercepts an API request.  Importable helpers are used by the task-scoped
Playwright runner so that child-process lifetime remains explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
import tempfile
import time as time_module
import uuid
from datetime import date, datetime, time, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCKED_DATABASE = "gp_pms_meta_grid_live_local_7f3c2a91_20260720"
REFERENCE_DATE = date(2026, 7, 27)
SYNTHETIC_EMAIL = "meta-grid.receptionist@example.invalid"
PRACTICE_NAME = "Meta-grid Live-local Synthetic Practice"
UUID_NAMESPACE = uuid.UUID("0fed5148-9537-4bf2-9bad-31511fb76df4")
BRISBANE = ZoneInfo("Australia/Brisbane")


def fixed_id(label: str) -> uuid.UUID:
    return uuid.uuid5(UUID_NAMESPACE, label)


PRACTICE_ID = fixed_id("practice")
USER_ID = fixed_id("receptionist")
LOCATION_ID = fixed_id("main-clinic")


def _sha256(value: object) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _contract_environment() -> None:
    """Set only the local, provider-disabled contract flags before app imports."""

    os.environ.update(
        {
            "ENVIRONMENT": "dev",
            "BERNIE_STAFF_PILOT_ENABLED": "true",
            "BERNIE_STAFF_PILOT_PRACTICE_IDS": str(PRACTICE_ID),
            "BERNIE_STAFF_PILOT_USER_IDS": str(USER_ID),
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false",
            "GOOGLE_APPLICATION_CREDENTIALS": "",
        }
    )


def database_url() -> str:
    raw = os.environ.get("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("DATABASE_URL is required")
    url = make_url(raw)
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("Live-local meta-grid acceptance requires PostgreSQL")
    if url.database != LOCKED_DATABASE:
        raise RuntimeError(f"DATABASE_URL must target {LOCKED_DATABASE}")
    if url.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Live-local meta-grid PostgreSQL must be loopback-only")
    return raw


def create_database() -> None:
    target = make_url(database_url())
    engine = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": LOCKED_DATABASE},
            ).scalar()
            if exists:
                raise RuntimeError(
                    f"Refusing to reuse existing live-local database {LOCKED_DATABASE}"
                )
            quoted = connection.dialect.identifier_preparer.quote(LOCKED_DATABASE)
            connection.execute(text(f"CREATE DATABASE {quoted}"))
    finally:
        engine.dispose()


def _utc_start(day: date, local_time: time) -> datetime:
    return datetime.combine(day, local_time, tzinfo=BRISBANE).astimezone(timezone.utc)


def create_schema_and_seed(password: str) -> None:
    if not password:
        raise RuntimeError("A transient synthetic password is required")
    _contract_environment()

    from app.models import Base
    from app.models.appointments import (
        Appointment,
        AppointmentStatus,
        AppointmentType,
        BookingChannel,
        PractitionerSchedule,
    )
    from app.models.diary import DiaryColumn, DiaryRoster, DiaryTemplate, Room, WaitingArea
    from app.models.patients import Patient
    from app.models.tenancy import Practice, PracticeLocation, Practitioner, User, UserRole
    from app.services.auth_service import hash_password

    practitioner_rows = [
        ("shera", "Alex", "Shera", "MED0001234567", "Room 1"),
        ("patel", "Anika", "Patel", "MED0002345678", "Room 2"),
        ("chen", "Alex", "Chen", "MED0003456789", "Room 3"),
    ]
    patient_rows = [
        ("margaret", "Margaret", "Thompson", date(1960, 4, 12), "Female"),
        ("billy", "Billy", "Fursin", date(1984, 9, 8), "Male"),
    ]
    standard_type_id = fixed_id("appointment-type-standard")

    engine = create_engine(database_url())
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=engine)
        with Session(engine) as session:
            practice = Practice(
                id=PRACTICE_ID,
                name=PRACTICE_NAME,
                timezone="Australia/Brisbane",
                hive_mind_opt_in=False,
            )
            location = PracticeLocation(
                id=LOCATION_ID,
                practice_id=PRACTICE_ID,
                name="Main Clinic",
                address_state="QLD",
                is_active=True,
            )
            session.add(practice)
            session.flush()
            session.add(location)
            session.flush()

            practitioners = {}
            for key, first, last, ahpra, _room_name in practitioner_rows:
                row = Practitioner(
                    id=fixed_id(f"practitioner-{key}"),
                    practice_id=PRACTICE_ID,
                    first_name=first,
                    last_name=last,
                    ahpra_number=ahpra,
                    specialty="General Practice",
                    default_location_id=LOCATION_ID,
                    is_active=True,
                )
                practitioners[key] = row
                session.add(row)
            session.flush()

            receptionist = User(
                id=USER_ID,
                practice_id=PRACTICE_ID,
                email=SYNTHETIC_EMAIL,
                password_hash=hash_password(password),
                role=UserRole.Receptionist,
                is_active=True,
            )
            patients = {}
            for key, first, last, dob, sex in patient_rows:
                row = Patient(
                    id=fixed_id(f"patient-{key}"),
                    practice_id=PRACTICE_ID,
                    first_name=first,
                    last_name=last,
                    date_of_birth=dob,
                    sex=sex,
                    address_state="QLD",
                )
                patients[key] = row
                session.add(row)
            appointment_type = AppointmentType(
                id=standard_type_id,
                practice_id=PRACTICE_ID,
                name="Standard",
                default_duration=30,
                color_hex="#4F86C6",
                is_bookable_online=False,
            )
            waiting_area = WaitingArea(
                id=fixed_id("waiting-area-main"),
                practice_id=PRACTICE_ID,
                location_id=LOCATION_ID,
                name="Main Waiting Area",
                display_order=0,
                is_active=True,
            )
            template = DiaryTemplate(
                id=fixed_id("diary-template-main"),
                practice_id=PRACTICE_ID,
                location_id=LOCATION_ID,
                practice_name=PRACTICE_NAME,
                slot_start=time(8, 0),
                slot_end=time(17, 0),
                slot_interval_minutes=15,
                footer=["Messages:", "Phone Consultations:"],
            )
            session.add_all([receptionist, *patients.values(), appointment_type, waiting_area, template])
            session.flush()

            for display_order, (key, first, last, ahpra, room_name) in enumerate(practitioner_rows):
                practitioner = practitioners[key]
                room = Room(
                    id=fixed_id(f"room-{key}"),
                    practice_id=PRACTICE_ID,
                    location_id=LOCATION_ID,
                    name=room_name,
                    display_order=display_order,
                    is_active=True,
                    default_waiting_area_id=waiting_area.id,
                )
                column = DiaryColumn(
                    id=fixed_id(f"diary-column-{key}"),
                    template_id=template.id,
                    practice_id=PRACTICE_ID,
                    display_order=display_order,
                    room_label=room_name,
                    assignment=f"Dr {first} {last}",
                    practitioner_id=practitioner.id,
                    practitioner_ahpra=ahpra,
                    is_active=True,
                    slot_interval_minutes=15,
                )
                schedule = PractitionerSchedule(
                    id=fixed_id(f"schedule-{key}-monday"),
                    practitioner_id=practitioner.id,
                    location_id=LOCATION_ID,
                    day_of_week=0,
                    start_time=time(8, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=15,
                )
                session.add_all([room, column, schedule])
                session.flush()
                session.add(
                    DiaryRoster(
                        id=fixed_id(f"roster-{key}-{REFERENCE_DATE.isoformat()}"),
                        practice_id=PRACTICE_ID,
                        room_id=room.id,
                        roster_date=REFERENCE_DATE,
                        practitioner_id=practitioner.id,
                        practitioner_ahpra=ahpra,
                        label=f"Dr {first} {last}",
                    )
                )

            appointment_specs = [
                ("margaret-shera-0900", REFERENCE_DATE, time(9, 0), "margaret", "shera", AppointmentStatus.Booked),
                ("billy-shera-1100", REFERENCE_DATE, time(11, 0), "billy", "shera", AppointmentStatus.Booked),
                ("margaret-patel-1000", REFERENCE_DATE, time(10, 0), "margaret", "patel", AppointmentStatus.Arrived),
                ("billy-shera-1430", REFERENCE_DATE, time(14, 30), "billy", "shera", AppointmentStatus.Booked),
                ("margaret-shera-next", date(2026, 8, 3), time(9, 30), "margaret", "shera", AppointmentStatus.Booked),
                ("margaret-chen-sept", date(2026, 9, 7), time(15, 0), "margaret", "chen", AppointmentStatus.Booked),
            ]
            for label, day, starts, patient_key, practitioner_key, status in appointment_specs:
                session.add(
                    Appointment(
                        id=fixed_id(f"appointment-{label}"),
                        practice_id=PRACTICE_ID,
                        location_id=LOCATION_ID,
                        patient_id=patients[patient_key].id,
                        practitioner_id=practitioners[practitioner_key].id,
                        appointment_type_id=standard_type_id,
                        booked_by=USER_ID,
                        start_time=_utc_start(day, starts),
                        appointment_date=day,
                        start_time_local=starts,
                        duration_minutes=30,
                        status=status,
                        reason="Authored synthetic live-local acceptance fixture",
                        booked_via=BookingChannel.Receptionist,
                    )
                )
            session.commit()
    finally:
        engine.dispose()


def rotate_synthetic_password(password: str) -> None:
    _contract_environment()
    from app.models.tenancy import User
    from app.services.auth_service import hash_password

    engine = create_engine(database_url())
    try:
        with Session(engine) as session:
            user = session.get(User, USER_ID)
            if not user or user.email != SYNTHETIC_EMAIL:
                raise RuntimeError("Locked synthetic receptionist fixture was not found")
            user.password_hash = hash_password(password)
            session.commit()
    finally:
        engine.dispose()


def database_readback() -> dict[str, object]:
    """Return sanitized counts and hashes for all forbidden-write surfaces."""

    _contract_environment()
    from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentCommandIdempotency
    from app.models.bernie_sessions import BernieBookingSession, BernieSessionEventRow

    engine = create_engine(database_url())
    try:
        with Session(engine) as session:
            appointment_rows = session.query(Appointment).order_by(Appointment.id).all()
            canonical_appointments = [
                {
                    "id": str(row.id),
                    "practice_id": str(row.practice_id),
                    "location_id": str(row.location_id) if row.location_id else None,
                    "patient_id": str(row.patient_id) if row.patient_id else None,
                    "practitioner_id": str(row.practitioner_id),
                    "appointment_type_id": str(row.appointment_type_id) if row.appointment_type_id else None,
                    "appointment_date": row.appointment_date.isoformat(),
                    "start_time": row.start_time.isoformat(),
                    "start_time_local": row.start_time_local.isoformat(),
                    "duration_minutes": row.duration_minutes,
                    "status": row.status.value,
                }
                for row in appointment_rows
            ]
            appointment_digest = hashlib.sha256(
                json.dumps(canonical_appointments, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            counts = {
                "appointments": len(appointment_rows),
                "appointment_audit_log": session.query(AppointmentAuditLog).count(),
                "appointment_command_idempotency": session.query(AppointmentCommandIdempotency).count(),
                "bernie_booking_sessions": session.query(BernieBookingSession).count(),
                "bernie_session_events": session.query(BernieSessionEventRow).count(),
            }
            empty_digest = hashlib.sha256(b"[]").hexdigest()
            hashes = {
                "appointments": appointment_digest,
                "appointment_audit_log": empty_digest if counts["appointment_audit_log"] == 0 else "nonempty",
                "appointment_command_idempotency": empty_digest if counts["appointment_command_idempotency"] == 0 else "nonempty",
                "bernie_booking_sessions": empty_digest if counts["bernie_booking_sessions"] == 0 else "nonempty",
                "bernie_session_events": empty_digest if counts["bernie_session_events"] == 0 else "nonempty",
            }
    finally:
        engine.dispose()
    return {
        "schema_version": "bernie.meta-grid-live-local.database-readback.v1",
        "database": LOCKED_DATABASE,
        "synthetic_only": True,
        "counts": counts,
        "sha256": hashes,
        "identifiers_recorded": False,
        "patient_details_recorded": False,
    }


def readiness_report() -> dict[str, object]:
    _contract_environment()
    from app.models.appointments import AppointmentType, PractitionerSchedule
    from app.models.diary import DiaryColumn, DiaryRoster, DiaryTemplate, Room, WaitingArea
    from app.models.patients import Patient
    from app.models.tenancy import Practice, PracticeLocation, Practitioner, User
    from app.services.bernie_pilot_gate import evaluate_bernie_pilot_eligibility
    from app.config import settings

    engine = create_engine(database_url())
    expected_counts = {
        "practices": 1,
        "practice_locations": 1,
        "practitioners": 3,
        "users": 1,
        "patients": 2,
        "appointment_types": 1,
        "practitioner_schedules": 3,
        "diary_templates": 1,
        "diary_columns": 3,
        "waiting_areas": 1,
        "rooms": 3,
        "diary_roster": 3,
        "appointments": 6,
    }
    try:
        with Session(engine) as session:
            model_rows = (
                Practice,
                PracticeLocation,
                Practitioner,
                User,
                Patient,
                AppointmentType,
                PractitionerSchedule,
                DiaryTemplate,
                DiaryColumn,
                WaitingArea,
                Room,
                DiaryRoster,
            )
            counts = {model.__tablename__: session.query(model).count() for model in model_rows}
            counts["appointments"] = database_readback()["counts"]["appointments"]
            user = session.get(User, USER_ID)
            practice = session.get(Practice, PRACTICE_ID)
            eligibility = evaluate_bernie_pilot_eligibility(
                enabled=settings.bernie_staff_pilot_enabled,
                practice_allowlist=settings.bernie_staff_pilot_practice_ids,
                user_allowlist=settings.bernie_staff_pilot_user_ids,
                current_user=user,
            )
            invariant_readback = database_readback()
            ready = bool(
                counts == expected_counts
                and practice
                and practice.name == PRACTICE_NAME
                and user
                and user.email == SYNTHETIC_EMAIL
                and eligibility.eligible
                and settings.bernie_booking_interpreter_provider == "disabled"
                and not settings.google_application_credentials
                and all(
                    invariant_readback["counts"][table] == 0
                    for table in (
                        "appointment_audit_log",
                        "appointment_command_idempotency",
                        "bernie_booking_sessions",
                        "bernie_session_events",
                    )
                )
            )
    finally:
        engine.dispose()
    return {
        "schema_version": "bernie.meta-grid-live-local.readiness.v1",
        "database": LOCKED_DATABASE,
        "database_target": "loopback:5434",
        "reference_date": REFERENCE_DATE.isoformat(),
        "synthetic_only": counts == expected_counts,
        "counts": counts,
        "expected_counts": expected_counts,
        "pilot_eligible": bool(eligibility.eligible),
        "practice_id_sha256": _sha256(PRACTICE_ID),
        "user_id_sha256": _sha256(USER_ID),
        "provider": "disabled",
        "live_provider": False,
        "cloud_credentials_present": False,
        "ready": ready,
    }


def _auth_bootstrap_html(password: str) -> str:
    safe_password = json.dumps(password)
    safe_email = json.dumps(SYNTHETIC_EMAIL)
    target = json.dumps(
        f"/diary/diary.html?reference_date={REFERENCE_DATE.isoformat()}"
        "&bernie_session=false&standalone_diary=true"
    )
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>EMR4 meta-grid live-local authentication</title></head>
<body>
  <main><h1>EMR4 meta-grid live-local evaluation</h1><p id="status">Authenticating synthetic receptionist...</p></main>
  <script>
  (async () => {{
    const status = document.getElementById("status");
    try {{
      const form = new URLSearchParams();
      form.set("username", {safe_email});
      form.set("password", {safe_password});
      const response = await fetch("http://localhost:8001/api/v1/auth/login", {{
        method: "POST",
        headers: {{"Content-Type": "application/x-www-form-urlencoded"}},
        body: form.toString()
      }});
      if (!response.ok) throw new Error(`Login failed (${{response.status}})`);
      const payload = await response.json();
      if (!payload.access_token) throw new Error("Login response had no token");
      localStorage.setItem("emr4_token", payload.access_token);
      status.textContent = "Authenticated; opening the real Diary...";
      window.location.replace({target});
    }} catch (error) {{
      status.textContent = `Authentication stopped: ${{error.message}}`;
    }}
  }})();
  </script>
</body>
</html>"""


class _StaticHandler(SimpleHTTPRequestHandler):
    server_version = "EMR4MetaGridLiveLocal/1"

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if urlsplit(self.path).path == "/meta-grid-auth.html":
            password = os.environ.get("META_GRID_SYNTHETIC_PASSWORD", "")
            if not password:
                self.send_error(503, "Synthetic login is not configured")
                return
            body = _auth_bootstrap_html(password).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def serve_static(host: str, port: int) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Static Diary server must be loopback-only")
    handler = partial(_StaticHandler, directory=str(ROOT / "docs"))
    server = ThreadingHTTPServer((host, port), handler)
    print(json.dumps({"event": "static_ready", "host": host, "port": port}), flush=True)
    server.serve_forever()


def launch_runtime() -> tuple[dict[str, object], list[subprocess.Popen[bytes]]]:
    password = f"MetaGrid-{secrets.token_urlsafe(24)}!"
    rotate_synthetic_password(password)
    runtime_dir = Path(tempfile.gettempdir()) / "emr4-meta-grid-live-local-7f3c2a91"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "backend_stdout": runtime_dir / "backend.stdout.log",
        "backend_stderr": runtime_dir / "backend.stderr.log",
        "static_stdout": runtime_dir / "static.stdout.log",
        "static_stderr": runtime_dir / "static.stderr.log",
    }
    child_env = os.environ.copy()
    child_env.update(
        {
            "META_GRID_SYNTHETIC_PASSWORD": password,
            "SECRET_KEY": f"MetaGridJwt-{secrets.token_urlsafe(32)}",
            "ENVIRONMENT": "dev",
            "BERNIE_STAFF_PILOT_ENABLED": "true",
            "BERNIE_STAFF_PILOT_PRACTICE_IDS": str(PRACTICE_ID),
            "BERNIE_STAFF_PILOT_USER_IDS": str(USER_ID),
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false",
            "GOOGLE_APPLICATION_CREDENTIALS": "",
            "GOOGLE_CLOUD_PROJECT": "",
            "NO_PROXY": "localhost,127.0.0.1",
            "no_proxy": "localhost,127.0.0.1",
        }
    )
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    handles = {key: path.open("wb") for key, path in paths.items()}
    try:
        backend = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8001",
                "--log-level",
                "info",
                "--access-log",
            ],
            cwd=ROOT,
            env=child_env,
            stdout=handles["backend_stdout"],
            stderr=handles["backend_stderr"],
            creationflags=creationflags,
        )
        static = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "serve-static",
                "--host",
                "127.0.0.1",
                "--port",
                "3000",
            ],
            cwd=ROOT,
            env=child_env,
            stdout=handles["static_stdout"],
            stderr=handles["static_stderr"],
            creationflags=creationflags,
        )
    finally:
        for handle in handles.values():
            handle.close()

    processes = [backend, static]
    ready = {"backend": False, "static": False}
    for _ in range(60):
        for name, url in (
            ("backend", "http://127.0.0.1:8001/health"),
            ("static", "http://127.0.0.1:3000/meta-grid-auth.html"),
        ):
            if ready[name]:
                continue
            try:
                with urlopen(url, timeout=0.5) as response:  # nosec B310 - locked loopback URLs
                    ready[name] = response.status == 200
            except (OSError, URLError):
                # The bounded readiness loop retries while the local child
                # process starts; the final guard below still fails closed.
                continue
        if all(ready.values()):
            break
        if any(process.poll() is not None for process in processes):
            break
        time_module.sleep(0.25)
    if not all(ready.values()):
        stop_runtime(processes)
        raise RuntimeError(f"Live-local runtime failed readiness; logs={runtime_dir}")
    return (
        {
            "database": LOCKED_DATABASE,
            "provider": "disabled",
            "cloud_credentials_present": False,
            "backend_pid": backend.pid,
            "static_pid": static.pid,
            "backend_ready": True,
            "static_ready": True,
            "runtime_dir": str(runtime_dir),
            "credential_recorded": False,
        },
        processes,
    )


def stop_runtime(processes: list[subprocess.Popen[bytes]]) -> None:
    for process in reversed(processes):
        if process.poll() is None:
            process.terminate()
    deadline = time_module.time() + 8
    for process in reversed(processes):
        remaining = max(0.1, deadline - time_module.time())
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)


def cleanup_database() -> dict[str, object]:
    """Drop only the exact disposable database after verifying its marker."""

    target = make_url(database_url())
    verification_engine = create_engine(target)
    try:
        with verification_engine.connect() as connection:
            marker = connection.execute(
                text(
                    "SELECT count(*) FROM practices WHERE id = :practice_id AND name = :name"
                ),
                {"practice_id": PRACTICE_ID, "name": PRACTICE_NAME},
            ).scalar_one()
            user_marker = connection.execute(
                text("SELECT count(*) FROM users WHERE id = :user_id AND email = :email"),
                {"user_id": USER_ID, "email": SYNTHETIC_EMAIL},
            ).scalar_one()
            practice_count = connection.execute(text("SELECT count(*) FROM practices")).scalar_one()
        if marker != 1 or user_marker != 1 or practice_count != 1:
            raise RuntimeError("Refusing cleanup: the exact synthetic ownership marker is absent")
    finally:
        verification_engine.dispose()

    maintenance = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with maintenance.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": LOCKED_DATABASE},
            )
            quoted = connection.dialect.identifier_preparer.quote(LOCKED_DATABASE)
            connection.execute(text(f"DROP DATABASE {quoted}"))
    finally:
        maintenance.dispose()
    return {
        "database": LOCKED_DATABASE,
        "cleanup": "dropped_exact_verified_disposable_database",
        "recoverable": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup")
    subparsers.add_parser("status")
    subparsers.add_parser("readback")
    subparsers.add_parser("cleanup")
    serve_parser = subparsers.add_parser("serve-static")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=3000, type=int)
    args = parser.parse_args()

    try:
        if args.command == "setup":
            password = f"MetaGrid-{secrets.token_urlsafe(24)}!"
            create_database()
            create_schema_and_seed(password)
            if not readiness_report()["ready"]:
                raise RuntimeError("Live-local database did not pass readiness")
        elif args.command == "status":
            if not readiness_report()["ready"]:
                raise RuntimeError("Live-local database did not pass readiness")
        elif args.command == "readback":
            database_readback()
        elif args.command == "cleanup":
            cleanup_database()
        else:
            serve_static(args.host, args.port)
            return 0
    except Exception as exc:
        print(json.dumps({"ready": False, "error_type": type(exc).__name__}), file=sys.stderr)
        return 1
    # Never serialize database-derived report values through this convenience
    # CLI. The acceptance runner consumes the importable helpers directly and
    # applies its own bounded, hashed evidence schema.
    print(
        json.dumps(
            {
                "schema_version": "bernie.meta-grid-live-local.cli-status.v1",
                "command": args.command,
                "completed": True,
                "report_values_recorded": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
