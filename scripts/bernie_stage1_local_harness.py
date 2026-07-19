"""Local, synthetic-only harness for frozen Bernie Stage 1 acceptance.

This harness creates one explicitly named disposable PostgreSQL database, seeds
the frozen synthetic practice fixtures, reports sanitized readiness/count data,
and serves a loopback authentication bootstrap plus the real ``docs/`` Diary.
It does not intercept or fulfil Diary API requests.
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
from datetime import date, time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
LOCKED_DATABASE = "gp_pms_stage1_2d3fa717_20260719_r2"
REFERENCE_DATE = date(2026, 7, 20)
SYNTHETIC_EMAIL = "stage1.receptionist@example.invalid"
PRACTITIONER_AHPRA = "MED0001234567"
UUID_NAMESPACE = uuid.UUID("9eead9a5-a8b5-4c89-b0c8-63d67c6fc1a0")


def _sha256(value: object) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _database_url() -> str:
    raw = os.environ.get("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("DATABASE_URL is required")
    url = make_url(raw)
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("Stage 1 requires PostgreSQL")
    if url.database != LOCKED_DATABASE:
        raise RuntimeError(f"DATABASE_URL must target {LOCKED_DATABASE}")
    if url.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Stage 1 PostgreSQL must be loopback-only")
    return raw


def _allowlisted_identity() -> tuple[uuid.UUID, uuid.UUID]:
    from app.config import settings

    practice_values = [
        value.strip()
        for value in settings.bernie_staff_pilot_practice_ids.split(",")
        if value.strip()
    ]
    user_values = [
        value.strip()
        for value in settings.bernie_staff_pilot_user_ids.split(",")
        if value.strip()
    ]
    if not settings.bernie_staff_pilot_enabled:
        raise RuntimeError("BERNIE_STAFF_PILOT_ENABLED must be true")
    if not practice_values or not user_values:
        raise RuntimeError("Stage 1 requires explicit practice and user pilot allowlists")
    return uuid.UUID(practice_values[0]), uuid.UUID(user_values[0])


def _fixed_id(label: str) -> uuid.UUID:
    return uuid.uuid5(UUID_NAMESPACE, label)


def _create_database() -> None:
    target = make_url(_database_url())
    maintenance = target.set(database="postgres")
    engine = create_engine(maintenance, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": LOCKED_DATABASE},
            ).scalar()
            if exists:
                raise RuntimeError(
                    f"Refusing to reuse existing Stage 1 database {LOCKED_DATABASE}"
                )
            connection.execute(text(f'CREATE DATABASE "{LOCKED_DATABASE}"'))
    finally:
        engine.dispose()


def inspect_database() -> dict[str, object]:
    engine = create_engine(_database_url())
    try:
        with engine.connect() as connection:
            table_names = connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name"
                )
            ).scalars().all()
            quote = connection.dialect.identifier_preparer.quote
            nonempty_tables = []
            for table_name in table_names:
                row_count = connection.execute(
                    text(f"SELECT count(*) FROM {quote(table_name)}")
                ).scalar_one()
                if row_count:
                    nonempty_tables.append({"table": table_name, "row_count": row_count})
    finally:
        engine.dispose()
    return {
        "database": LOCKED_DATABASE,
        "public_table_count": len(table_names),
        "nonempty_tables": nonempty_tables,
        "safe_empty_setup_cleanup": not nonempty_tables,
    }


def cleanup_empty_setup() -> dict[str, object]:
    inspection = inspect_database()
    if not inspection["safe_empty_setup_cleanup"]:
        raise RuntimeError("Refusing to drop a Stage 1 database that contains rows")
    target = make_url(_database_url())
    engine = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE "{LOCKED_DATABASE}"'))
    finally:
        engine.dispose()
    return {
        "database": LOCKED_DATABASE,
        "cleanup": "dropped_failed_empty_setup",
        "public_table_count_before": inspection["public_table_count"],
        "nonempty_tables_before": inspection["nonempty_tables"],
    }


def _create_schema_and_seed(password: str) -> dict[str, object]:
    if not password:
        raise RuntimeError("STAGE1_SYNTHETIC_PASSWORD is required")

    from app.models import Base
    from app.models.appointments import AppointmentType, PractitionerSchedule
    from app.models.diary import (
        DiaryColumn,
        DiaryRoster,
        DiaryTemplate,
        Room,
        WaitingArea,
    )
    from app.models.patients import Patient
    from app.models.tenancy import (
        Practice,
        PracticeLocation,
        Practitioner,
        User,
        UserRole,
    )
    from app.services.auth_service import hash_password

    practice_id, user_id = _allowlisted_identity()
    location_id = _fixed_id("location-main-clinic")
    practitioner_id = _fixed_id("practitioner-alex-shera")
    patient_id = _fixed_id("patient-margaret-thompson")
    appointment_type_id = _fixed_id("appointment-type-standard")
    template_id = _fixed_id("diary-template-main-clinic")
    room_id = _fixed_id("room-1")

    engine = create_engine(_database_url())
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=engine)
        with Session(engine) as session:
            practice = Practice(
                id=practice_id,
                name="Stage 1 Synthetic Practice",
                timezone="Australia/Brisbane",
                hive_mind_opt_in=False,
            )
            location = PracticeLocation(
                id=location_id,
                practice_id=practice_id,
                name="Main Clinic",
                address_state="QLD",
                is_active=True,
            )
            practitioner = Practitioner(
                id=practitioner_id,
                practice_id=practice_id,
                first_name="Alex",
                last_name="Shera",
                ahpra_number=PRACTITIONER_AHPRA,
                specialty="General Practice",
                default_location_id=location_id,
                is_active=True,
            )
            receptionist = User(
                id=user_id,
                practice_id=practice_id,
                email=SYNTHETIC_EMAIL,
                password_hash=hash_password(password),
                role=UserRole.Receptionist,
                is_active=True,
            )
            patient = Patient(
                id=patient_id,
                practice_id=practice_id,
                first_name="Margaret",
                last_name="Thompson",
                date_of_birth=date(1960, 4, 12),
                sex="Female",
                address_state="QLD",
            )
            appointment_type = AppointmentType(
                id=appointment_type_id,
                practice_id=practice_id,
                name="Standard",
                default_duration=15,
                color_hex="#4F86C6",
                is_bookable_online=False,
            )
            schedule = PractitionerSchedule(
                id=_fixed_id("schedule-alex-shera-monday"),
                practitioner_id=practitioner_id,
                location_id=location_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration_minutes=15,
            )
            template = DiaryTemplate(
                id=template_id,
                practice_id=practice_id,
                location_id=location_id,
                practice_name="Stage 1 Synthetic Practice",
                slot_start=time(9, 0),
                slot_end=time(17, 0),
                slot_interval_minutes=15,
                footer=["Messages:", "Phone Consultations:"],
            )
            column = DiaryColumn(
                id=_fixed_id("diary-column-room-1"),
                template_id=template_id,
                practice_id=practice_id,
                display_order=0,
                room_label="Room 1",
                assignment="Dr Alex Shera",
                practitioner_id=practitioner_id,
                practitioner_ahpra=PRACTITIONER_AHPRA,
                is_active=True,
                slot_interval_minutes=15,
            )
            waiting_area = WaitingArea(
                id=_fixed_id("waiting-area-main"),
                practice_id=practice_id,
                location_id=location_id,
                name="Main Waiting Area",
                display_order=0,
                is_active=True,
            )
            room = Room(
                id=room_id,
                practice_id=practice_id,
                location_id=location_id,
                name="Room 1",
                display_order=0,
                is_active=True,
                default_waiting_area_id=waiting_area.id,
            )
            roster = DiaryRoster(
                id=_fixed_id("roster-room-1-2026-07-20"),
                practice_id=practice_id,
                room_id=room_id,
                roster_date=REFERENCE_DATE,
                practitioner_id=practitioner_id,
                practitioner_ahpra=PRACTITIONER_AHPRA,
                label="Dr Alex Shera",
            )
            session.add(practice)
            session.flush()
            session.add(location)
            session.flush()
            session.add(practitioner)
            session.flush()
            session.add_all(
                [receptionist, patient, appointment_type, template, waiting_area]
            )
            session.flush()
            session.add_all([schedule, column, room])
            session.flush()
            session.add(roster)
            session.commit()
    finally:
        engine.dispose()
    return readiness_report()


def readiness_report() -> dict[str, object]:
    from app.models.appointments import (
        Appointment,
        AppointmentAuditLog,
        AppointmentCommandIdempotency,
        AppointmentType,
        PractitionerSchedule,
    )
    from app.models.diary import DiaryColumn, DiaryRoster, DiaryTemplate, Room, WaitingArea
    from app.models.patients import Patient
    from app.models.tenancy import Practice, PracticeLocation, Practitioner, User
    from app.services.bernie_pilot_gate import evaluate_bernie_pilot_eligibility

    practice_id, user_id = _allowlisted_identity()
    engine = create_engine(_database_url())
    expected_counts = {
        Practice.__tablename__: 1,
        PracticeLocation.__tablename__: 1,
        Practitioner.__tablename__: 1,
        User.__tablename__: 1,
        Patient.__tablename__: 1,
        AppointmentType.__tablename__: 1,
        PractitionerSchedule.__tablename__: 1,
        DiaryTemplate.__tablename__: 1,
        DiaryColumn.__tablename__: 1,
        WaitingArea.__tablename__: 1,
        Room.__tablename__: 1,
        DiaryRoster.__tablename__: 1,
        Appointment.__tablename__: 0,
        AppointmentAuditLog.__tablename__: 0,
        AppointmentCommandIdempotency.__tablename__: 0,
    }
    with Session(engine) as session:
        counts = {
            model.__tablename__: session.query(model).count()
            for model in (
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
                Appointment,
                AppointmentAuditLog,
                AppointmentCommandIdempotency,
            )
        }
        user = session.get(User, user_id)
        practitioner = session.query(Practitioner).one()
        roster = session.query(DiaryRoster).filter_by(roster_date=REFERENCE_DATE).one()
        schedule = session.query(PractitionerSchedule).filter_by(day_of_week=0).one()
        from app.config import settings

        eligibility = (
            evaluate_bernie_pilot_eligibility(
                enabled=settings.bernie_staff_pilot_enabled,
                practice_allowlist=settings.bernie_staff_pilot_practice_ids,
                user_allowlist=settings.bernie_staff_pilot_user_ids,
                current_user=user,
            )
            if user
            else None
        )
        identity_ok = bool(
            user
            and user.practice_id == practice_id
            and practitioner.practice_id == practice_id
            and roster.practitioner_id == practitioner.id
            and schedule.practitioner_id == practitioner.id
            and schedule.start_time <= time(14, 0)
            and schedule.end_time >= time(15, 45)
        )
        result = {
            "schema_version": "bernie.stage1.local-readiness.v1",
            "database": LOCKED_DATABASE,
            "database_target": "127.0.0.1:5434",
            "reference_date_D": REFERENCE_DATE.isoformat(),
            "synthetic_only": counts == expected_counts,
            "counts": counts,
            "expected_counts": expected_counts,
            "identity_and_roster_ready": identity_ok,
            "pilot": {
                "eligible": bool(eligibility and eligibility.eligible),
                "reason": eligibility.reason if eligibility else "missing_user",
                "practice_id_sha256": _sha256(practice_id),
                "user_id_sha256": _sha256(user_id),
            },
            "provider": os.environ.get(
                "BERNIE_BOOKING_INTERPRETER_PROVIDER", ""
            ).lower(),
            "live_provider": False,
            "cloud_credentials_present": bool(
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            ),
            "ready": bool(
                counts == expected_counts
                and identity_ok
                and eligibility
                and eligibility.eligible
                and os.environ.get(
                    "BERNIE_BOOKING_INTERPRETER_PROVIDER", ""
                ).lower()
                == "fake"
                and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            ),
        }
    engine.dispose()
    return result


def rotate_synthetic_password(password: str) -> dict[str, object]:
    if not password:
        raise RuntimeError("STAGE1_SYNTHETIC_PASSWORD is required")
    from app.models.tenancy import User
    from app.services.auth_service import hash_password

    _, user_id = _allowlisted_identity()
    engine = create_engine(_database_url())
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user or user.email != SYNTHETIC_EMAIL:
                raise RuntimeError("Locked synthetic receptionist fixture was not found")
            user.password_hash = hash_password(password)
            session.commit()
    finally:
        engine.dispose()
    return {
        "database": LOCKED_DATABASE,
        "synthetic_receptionist_password_rotated": True,
        "credential_recorded": False,
    }


def start_runtime() -> dict[str, object]:
    password = os.environ.get("STAGE1_SYNTHETIC_PASSWORD") or (
        f"Stage1-{secrets.token_urlsafe(24)}!"
    )
    rotate_synthetic_password(password)
    runtime_dir = Path(tempfile.gettempdir()) / "emr4-stage1-2d3fa717-r2"
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
            "STAGE1_SYNTHETIC_PASSWORD": password,
            "SECRET_KEY": f"Stage1Jwt-{secrets.token_urlsafe(32)}",
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "fake",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "true",
            "GOOGLE_APPLICATION_CREDENTIALS": "",
            "NO_PROXY": "localhost,127.0.0.1",
            "no_proxy": "localhost,127.0.0.1",
        }
    )
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    handles = {key: path.open("w", encoding="utf-8") for key, path in paths.items()}
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

    ready = {"backend": False, "static": False}
    for _ in range(40):
        for name, url in (
            ("backend", "http://127.0.0.1:8001/health"),
            ("static", "http://127.0.0.1:3000/stage1-auth.html"),
        ):
            if ready[name]:
                continue
            try:
                with urlopen(url, timeout=0.5) as response:  # nosec B310 - locked loopback URLs
                    ready[name] = response.status == 200
            except Exception:
                pass
        if all(ready.values()):
            break
        if backend.poll() is not None or static.poll() is not None:
            break
        time_module.sleep(0.25)
    if not all(ready.values()):
        for process in (backend, static):
            if process.poll() is None:
                process.terminate()
        raise RuntimeError(
            f"Stage 1 runtime failed readiness: backend={ready['backend']} "
            f"static={ready['static']}; logs={runtime_dir}"
        )
    return {
        "database": LOCKED_DATABASE,
        "provider": "fake",
        "cloud_credentials_present": False,
        "backend_pid": backend.pid,
        "static_pid": static.pid,
        "backend_ready": ready["backend"],
        "static_ready": ready["static"],
        "runtime_dir": str(runtime_dir),
        "credential_recorded": False,
    }


def probe_interpretation() -> dict[str, object]:
    password = f"Stage1-{secrets.token_urlsafe(24)}!"
    rotate_synthetic_password(password)
    login_request = Request(
        "http://127.0.0.1:8001/api/v1/auth/login",
        data=urlencode({"username": SYNTHETIC_EMAIL, "password": password}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(login_request, timeout=5) as response:  # nosec B310 - locked loopback URL
        token = json.loads(response.read())["access_token"]
    body = {
        "instruction": (
            "Make an appointment for Margaret Thompson with Dr Shera today "
            "after 2 pm but before 3:45."
        ),
        "reference_date": REFERENCE_DATE.isoformat(),
        "context_frames": [
            {
                "type": "visible_diary_page",
                "visible_date": REFERENCE_DATE.isoformat(),
                "diary_date": REFERENCE_DATE.isoformat(),
            }
        ],
    }
    interpret_request = Request(
        "http://127.0.0.1:8001/api/v1/appointments/proposals/bernie/interpret-booking-instruction",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(interpret_request, timeout=10) as response:  # nosec B310 - locked loopback URL
        payload = json.loads(response.read())
        status_code = response.status
    supervised_body = {
        "command": payload.get("command_candidate"),
        "reference_date": REFERENCE_DATE.isoformat(),
        "context_frames": body["context_frames"],
    }
    supervised_request = Request(
        "http://127.0.0.1:8001/api/v1/appointments/proposals/bernie/supervised-booking",
        data=json.dumps(supervised_body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(supervised_request, timeout=10) as response:  # nosec B310 - locked loopback URL
        supervised = json.loads(response.read())
        supervised_status = response.status
    command = payload.get("command_candidate") or {}
    sanitized_command = {
        key: value
        for key, value in command.items()
        if key not in {"patient_id", "practitioner_id", "appointment_type_id"}
    }
    for key in ("patient_id", "practitioner_id", "appointment_type_id"):
        value = command.get(key)
        sanitized_command[f"{key}_present"] = bool(value)
        if value:
            sanitized_command[f"{key}_sha256"] = _sha256(value)
    return {
        "evidence_label": "live_local_backend_postgres",
        "http_status": status_code,
        "result": payload.get("result"),
        "safe": payload.get("safe"),
        "summary": payload.get("summary"),
        "clarifying_question": payload.get("clarifying_question"),
        "blocks": payload.get("blocks", []),
        "warnings": payload.get("warnings", []),
        "command_candidate": sanitized_command,
        "supervised_booking": {
            "http_status": supervised_status,
            "result": supervised.get("result"),
            "safe": supervised.get("safe"),
            "summary": supervised.get("summary"),
            "warnings": supervised.get("warnings", []),
            "blocks": supervised.get("blocks", []),
            "candidate_count": len(
                (supervised.get("search_proposal") or {}).get("candidates", [])
            ),
            "staff_review_candidate_count": len(
                (supervised.get("staff_review") or {}).get("candidate_slots", [])
            ),
            "staff_review_status": (supervised.get("staff_review") or {}).get("status"),
            "confirmation_ready": (supervised.get("staff_review") or {}).get(
                "confirmation_ready"
            ),
            "outcome": supervised.get("outcome"),
            "ui_view_model_flags": (supervised.get("ui_view_model") or {}).get(
                "flags"
            ),
        },
        "credential_recorded": False,
        "token_recorded": False,
    }


class _Stage1StaticHandler(SimpleHTTPRequestHandler):
    server_version = "EMR4Stage1Local/1"

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if urlsplit(self.path).path == "/stage1-auth.html":
            password = os.environ.get("STAGE1_SYNTHETIC_PASSWORD", "")
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

    def log_message(self, fmt: str, *args: object) -> None:
        # Static-server evidence records paths/statuses only. Credentials are
        # never sent to this server and response bodies are never logged.
        super().log_message(fmt, *args)


def _auth_bootstrap_html(password: str) -> str:
    safe_password = json.dumps(password)
    safe_email = json.dumps(SYNTHETIC_EMAIL)
    diary_target = json.dumps(
        "/diary/diary.html?reference_date=2026-07-20"
        "&bernie_open=true&bernie_review=live"
    )
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>EMR4 Stage 1 local authentication</title></head>
<body>
  <main><h1>EMR4 Stage 1</h1><p id="status">Authenticating synthetic receptionist…</p></main>
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
      status.textContent = "Authenticated; opening the real Diary…";
      window.location.replace({diary_target});
    }} catch (error) {{
      status.textContent = `Authentication stopped: ${{error.message}}`;
    }}
  }})();
  </script>
</body>
</html>"""


def serve_static(host: str, port: int) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Static Diary server must be loopback-only")
    handler = partial(_Stage1StaticHandler, directory=str(ROOT / "docs"))
    server = ThreadingHTTPServer((host, port), handler)
    print(json.dumps({"event": "static_ready", "host": host, "port": port}), flush=True)
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup")
    subparsers.add_parser("status")
    subparsers.add_parser("inspect-database")
    subparsers.add_parser("cleanup-empty-setup")
    subparsers.add_parser("rotate-password")
    subparsers.add_parser("start-runtime")
    subparsers.add_parser("probe-interpretation")
    serve_parser = subparsers.add_parser("serve-static")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=3000, type=int)
    args = parser.parse_args()

    try:
        if args.command == "setup":
            _create_database()
            report = _create_schema_and_seed(
                os.environ.get("STAGE1_SYNTHETIC_PASSWORD", "")
            )
        elif args.command == "status":
            report = readiness_report()
        elif args.command == "inspect-database":
            report = inspect_database()
        elif args.command == "cleanup-empty-setup":
            report = cleanup_empty_setup()
        elif args.command == "rotate-password":
            report = rotate_synthetic_password(
                os.environ.get("STAGE1_SYNTHETIC_PASSWORD", "")
            )
        elif args.command == "start-runtime":
            report = start_runtime()
        elif args.command == "probe-interpretation":
            report = probe_interpretation()
        else:
            serve_static(args.host, args.port)
            return 0
    except Exception as exc:
        print(json.dumps({"ready": False, "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ready", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
