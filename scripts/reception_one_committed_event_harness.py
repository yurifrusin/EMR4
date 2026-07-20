"""Exact disposable runtime for the bounded Reception One event vertical."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time as time_module
import uuid
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

import bernie_meta_grid_live_local_harness as base


ROOT = Path(__file__).resolve().parents[1]
LOCKED_DATABASE = "gp_pms_reception_one_event_runtime_5e2c91a7_20260721"
RUNTIME_TAG = "reception-one-event-runtime-5e2c91a7"
PROBE_ROLE = "emr4_reception_one_event_probe_5e2c91a7"
IPV6_HOST = "::1"
STATIC_PORT = 3000
BACKEND_PORT = 8001

IN_SCOPE_APPOINTMENT_ID = base.fixed_id("appointment-margaret-shera-0900")
OUT_OF_SCOPE_APPOINTMENT_ID = base.fixed_id("appointment-billy-shera-1430")

_ORIGINAL_AUTH_BOOTSTRAP_HTML = base._auth_bootstrap_html


def _auth_bootstrap_html(password: str) -> str:
    return _ORIGINAL_AUTH_BOOTSTRAP_HTML(password).replace(
        "http://localhost:8001", "http://[::1]:8001"
    )


base._auth_bootstrap_html = _auth_bootstrap_html


def _prepare_database_target() -> None:
    raw = os.environ.get("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("DATABASE_URL is required")
    url = make_url(raw)
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("Reception One event acceptance requires PostgreSQL")
    if url.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Reception One event PostgreSQL must be loopback-only")
    os.environ["DATABASE_URL"] = url.set(database=LOCKED_DATABASE).render_as_string(
        hide_password=False
    )
    os.environ.update(
        {
            "ENVIRONMENT": "dev",
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false",
            "GOOGLE_APPLICATION_CREDENTIALS": "",
            "RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED": "true",
            "NO_PROXY": "localhost,127.0.0.1,::1,[::1]",
            "no_proxy": "localhost,127.0.0.1,::1,[::1]",
        }
    )
    base.LOCKED_DATABASE = LOCKED_DATABASE


def create_database() -> None:
    _prepare_database_target()
    base.create_database()


def _create_probe_role() -> None:
    target = make_url(os.environ["DATABASE_URL"])
    maintenance = create_engine(
        target.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        with maintenance.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
                {"name": PROBE_ROLE},
            ).scalar_one_or_none()
            if exists:
                raise RuntimeError("Refusing to reuse the exact RLS probe role")
            connection.execute(text(f'CREATE ROLE "{PROBE_ROLE}" NOLOGIN'))
    finally:
        maintenance.dispose()


def _run_migrations() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("Alembic upgrade failed for the exact disposable database")


def create_schema_and_seed(password: str) -> None:
    _prepare_database_target()
    _create_probe_role()
    _run_migrations()
    base.create_schema_and_seed(password)
    engine = create_engine(os.environ["DATABASE_URL"])
    try:
        with engine.begin() as connection:
            connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{PROBE_ROLE}"'))
            connection.execute(
                text(f'GRANT SELECT ON diary_committed_events TO "{PROBE_ROLE}"')
            )
    finally:
        engine.dispose()


def readiness_report() -> dict[str, object]:
    _prepare_database_target()
    report = base.readiness_report()
    engine = create_engine(os.environ["DATABASE_URL"])
    try:
        with engine.connect() as connection:
            migration_head = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            event_table = connection.execute(
                text("SELECT to_regclass('public.diary_committed_events') IS NOT NULL")
            ).scalar_one()
            forced_rls = connection.execute(
                text(
                    "SELECT relrowsecurity AND relforcerowsecurity FROM pg_class "
                    "WHERE oid = 'public.diary_committed_events'::regclass"
                )
            ).scalar_one()
            append_trigger = connection.execute(
                text(
                    "SELECT count(*) FROM pg_trigger WHERE tgrelid = "
                    "'public.diary_committed_events'::regclass AND "
                    "tgname = 'trg_diary_committed_events_append_only' AND NOT tgisinternal"
                )
            ).scalar_one()
    finally:
        engine.dispose()
    report.update(
        {
            "schema_version": "reception-one.committed-event.readiness.v1",
            "migration_head": migration_head,
            "event_table_present": bool(event_table),
            "forced_rls": bool(forced_rls),
            "append_only_trigger": append_trigger == 1,
            "event_runtime_enabled_in_harness": True,
        }
    )
    report["ready"] = bool(
        report["ready"]
        and migration_head == "n3o4p5q6r7s8"
        and event_table
        and forced_rls
        and append_trigger == 1
    )
    return report


def database_readback() -> dict[str, object]:
    _prepare_database_target()
    engine = create_engine(os.environ["DATABASE_URL"])
    prohibited = {
        "patient_id",
        "patient_name",
        "date_of_birth",
        "phone_number",
        "medicare_number",
        "appointment_reason_text",
        "appointment_note",
        "raw_instruction",
        "free_text_transcript",
        "provider_output",
        "credential",
        "reason",
        "notes",
    }
    try:
        with engine.connect() as connection:
            counts = {
                table: connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one()
                for table in (
                    "appointments",
                    "appointment_audit_log",
                    "appointment_command_idempotency",
                    "diary_committed_events",
                    "bernie_booking_sessions",
                    "bernie_session_events",
                )
            }
            event_rows = connection.execute(
                text(
                    "SELECT event_type, schema_version, aggregate_revision, payload "
                    "FROM diary_committed_events ORDER BY occurred_at, id"
                )
            ).mappings().all()
            correlation_count = connection.execute(
                text(
                    "SELECT count(*) FROM diary_committed_events e "
                    "JOIN appointment_command_idempotency c "
                    "ON c.practice_id=e.practice_id AND c.id=e.command_id "
                    "JOIN appointment_audit_log a "
                    "ON a.practice_id=e.practice_id AND a.id=e.audit_log_id "
                    "WHERE c.state='completed' AND c.audit_log_id=a.id "
                    "AND a.command_id=c.id AND c.target_appointment_id=e.appointment_id "
                    "AND e.correlation_id=c.id"
                )
            ).scalar_one()
            target_windows = {
                label: connection.execute(
                    text(
                        "SELECT start_time_local::text FROM appointments WHERE id=:id"
                    ),
                    {"id": appointment_id},
                ).scalar_one()
                for label, appointment_id in (
                    ("in_scope_target", IN_SCOPE_APPOINTMENT_ID),
                    ("out_of_scope_target", OUT_OF_SCOPE_APPOINTMENT_ID),
                )
            }
    finally:
        engine.dispose()
    allowed_keys = {
        "appointment_id",
        "practitioner_id",
        "location_id",
        "start_time",
        "end_time",
        "reason_codes",
    }
    return {
        "schema_version": "reception-one.committed-event.database-readback.v1",
        "database": LOCKED_DATABASE,
        "synthetic_only": True,
        "counts": counts,
        "target_windows": target_windows,
        "event_types": [row["event_type"] for row in event_rows],
        "event_schema_versions": [row["schema_version"] for row in event_rows],
        "aggregate_revisions_positive": all(
            row["aggregate_revision"] > 0 for row in event_rows
        ),
        "payload_keys_exact": all(set(row["payload"]) == allowed_keys for row in event_rows),
        "prohibited_payload_keys_present": sorted(
            set().union(*(set(row["payload"]) for row in event_rows)) & prohibited
        ) if event_rows else [],
        "correlated_event_rows": correlation_count,
        "identifiers_recorded": False,
        "patient_details_recorded": False,
    }


def database_security_probes() -> dict[str, object]:
    _prepare_database_target()
    engine = create_engine(os.environ["DATABASE_URL"])
    mutation_results = {}
    for operation, statement in (
        ("update", "UPDATE diary_committed_events SET actor_role=actor_role"),
        ("delete", "DELETE FROM diary_committed_events"),
    ):
        try:
            with engine.begin() as connection:
                connection.execute(text(statement))
        except Exception as exc:
            mutation_results[operation] = "append_only_rejected" if "append-only" in str(exc) else "unexpected_rejection"
        else:
            mutation_results[operation] = "unexpectedly_allowed"
    foreign_practice = uuid.uuid5(base.UUID_NAMESPACE, "foreign-practice-probe")
    try:
        with engine.begin() as connection:
            connection.execute(text(f'SET LOCAL ROLE "{PROBE_ROLE}"'))
            connection.execute(
                text("SELECT set_config('app.current_practice_id', :value, true)"),
                {"value": str(base.PRACTICE_ID)},
            )
            own_count = connection.execute(
                text("SELECT count(*) FROM diary_committed_events")
            ).scalar_one()
            connection.execute(
                text("SELECT set_config('app.current_practice_id', :value, true)"),
                {"value": str(foreign_practice)},
            )
            foreign_count = connection.execute(
                text("SELECT count(*) FROM diary_committed_events")
            ).scalar_one()
    finally:
        engine.dispose()
    return {
        "schema_version": "reception-one.committed-event.database-security.v1",
        "append_only_update": mutation_results["update"],
        "append_only_delete": mutation_results["delete"],
        "rls_own_practice_event_count": own_count,
        "rls_foreign_practice_event_count": foreign_count,
        "non_bypass_probe_role": True,
        "role_name_recorded": False,
    }


class _IPv6ThreadingHTTPServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6


def serve_static(host: str, port: int) -> None:
    if host != IPV6_HOST:
        raise RuntimeError("Reception One static server is locked to IPv6 loopback")
    handler = partial(base._StaticHandler, directory=str(ROOT / "docs"))
    server = _IPv6ThreadingHTTPServer((host, port), handler)
    print(json.dumps({"event": "static_ready", "host": host, "port": port}), flush=True)
    server.serve_forever()


def launch_runtime() -> tuple[dict[str, object], list[subprocess.Popen[bytes]]]:
    _prepare_database_target()
    password = f"ReceptionOneEvent-{secrets.token_urlsafe(24)}!"
    base.rotate_synthetic_password(password)
    runtime_dir = Path(tempfile.gettempdir()) / f"emr4-{RUNTIME_TAG}"
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
            "SECRET_KEY": f"ReceptionOneEventJwt-{secrets.token_urlsafe(32)}",
            "ENVIRONMENT": "dev",
            "BERNIE_STAFF_PILOT_ENABLED": "true",
            "BERNIE_STAFF_PILOT_PRACTICE_IDS": str(base.PRACTICE_ID),
            "BERNIE_STAFF_PILOT_USER_IDS": str(base.USER_ID),
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false",
            "RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED": "true",
            "GOOGLE_APPLICATION_CREDENTIALS": "",
            "GOOGLE_CLOUD_PROJECT": "",
            "CORS_ORIGINS": '["http://[::1]:3000"]',
            "NO_PROXY": "localhost,127.0.0.1,::1,[::1]",
            "no_proxy": "localhost,127.0.0.1,::1,[::1]",
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
                IPV6_HOST,
                "--port",
                str(BACKEND_PORT),
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
                IPV6_HOST,
                "--port",
                str(STATIC_PORT),
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
    for _ in range(80):
        for name, url in (
            ("backend", "http://[::1]:8001/health"),
            ("static", "http://[::1]:3000/meta-grid-auth.html"),
        ):
            if ready[name]:
                continue
            try:
                with urlopen(url, timeout=0.5) as response:  # nosec B310 - exact loopback
                    ready[name] = response.status == 200
            except (OSError, URLError):
                continue
        if all(ready.values()):
            break
        if any(process.poll() is not None for process in processes):
            break
        time_module.sleep(0.25)
    if not all(ready.values()):
        stop_runtime(processes)
        raise RuntimeError(f"Reception One event runtime failed readiness; logs={runtime_dir}")
    return (
        {
            "database": LOCKED_DATABASE,
            "provider": "disabled",
            "cloud_credentials_present": False,
            "runtime_dir": str(runtime_dir),
            "loopback_family": "ipv6",
            "support_password": password,
            "credential_recorded": False,
        },
        processes,
    )


def stop_runtime(processes: list[subprocess.Popen[bytes]]) -> None:
    base.stop_runtime(processes)


def cleanup_database() -> dict[str, object]:
    _prepare_database_target()
    cleanup = base.cleanup_database()
    target = make_url(os.environ["DATABASE_URL"])
    maintenance = create_engine(
        target.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    try:
        with maintenance.connect() as connection:
            connection.execute(text(f'DROP ROLE IF EXISTS "{PROBE_ROLE}"'))
    finally:
        maintenance.dispose()
    return {
        **cleanup,
        "schema_version": "reception-one.committed-event.database-cleanup.v1",
        "ownership_marker_verified": True,
        "probe_role_removed": True,
        "scope": "authored_synthetic_disposable_database_and_exact_probe_role_only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup")
    subparsers.add_parser("status")
    subparsers.add_parser("readback")
    subparsers.add_parser("serve-runtime")
    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.add_argument("--output", type=Path, default=None)
    serve_parser = subparsers.add_parser("serve-static")
    serve_parser.add_argument("--host", default=IPV6_HOST)
    serve_parser.add_argument("--port", default=STATIC_PORT, type=int)
    args = parser.parse_args()
    try:
        if args.command == "setup":
            password = f"ReceptionOneEvent-{secrets.token_urlsafe(24)}!"
            create_database()
            create_schema_and_seed(password)
            if not readiness_report()["ready"]:
                raise RuntimeError("Reception One event database did not pass readiness")
        elif args.command == "status":
            if not readiness_report()["ready"]:
                raise RuntimeError("Reception One event database did not pass readiness")
        elif args.command == "readback":
            database_readback()
        elif args.command == "serve-runtime":
            runtime, processes = launch_runtime()
            print(
                json.dumps(
                    {
                        "event": "runtime_ready",
                        "database": runtime["database"],
                        "loopback_family": runtime["loopback_family"],
                    }
                ),
                flush=True,
            )
            try:
                while all(process.poll() is None for process in processes):
                    time_module.sleep(1)
            finally:
                stop_runtime(processes)
            return 0
        elif args.command == "cleanup":
            cleanup = cleanup_database()
            if args.output is not None:
                target = args.output.resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    json.dumps(cleanup, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
        else:
            serve_static(args.host, args.port)
            return 0
    except Exception as exc:
        print(json.dumps({"ready": False, "error_type": type(exc).__name__}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "schema_version": "reception-one.committed-event.cli-status.v1",
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
