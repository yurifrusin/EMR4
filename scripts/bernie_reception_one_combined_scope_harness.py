"""Exact disposable IPv6-loopback runtime for Reception One combined-scope proof.

The accepted meta-grid live-local harness owns the authored-synthetic schema,
fixtures, readback and marker-verified cleanup. This task wrapper gives the new
tranche a distinct locked database and IPv6 loopback servers, leaving Yuri's
active IPv4 review session untouched.
"""

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
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from sqlalchemy.engine import make_url

import bernie_meta_grid_live_local_harness as base


ROOT = Path(__file__).resolve().parents[1]
LOCKED_DATABASE = "gp_pms_reception_one_combined_scope_9c41b7e2_20260721"
RUNTIME_TAG = "reception-one-combined-scope-9c41b7e2"
IPV6_HOST = "::1"
STATIC_PORT = 3000
BACKEND_PORT = 8001

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
        raise RuntimeError("Reception One acceptance requires PostgreSQL")
    if url.host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Reception One acceptance requires loopback PostgreSQL")
    os.environ["DATABASE_URL"] = url.set(database=LOCKED_DATABASE).render_as_string(
        hide_password=False
    )
    os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1,[::1]"
    os.environ["no_proxy"] = "localhost,127.0.0.1,::1,[::1]"
    base.LOCKED_DATABASE = LOCKED_DATABASE


def create_database() -> None:
    _prepare_database_target()
    base.create_database()


def create_schema_and_seed(password: str) -> None:
    _prepare_database_target()
    base.create_schema_and_seed(password)


def readiness_report() -> dict[str, object]:
    _prepare_database_target()
    return base.readiness_report()


def database_readback() -> dict[str, object]:
    _prepare_database_target()
    return base.database_readback()


def cleanup_database() -> dict[str, object]:
    _prepare_database_target()
    return base.cleanup_database()


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
    password = f"ReceptionOne-{secrets.token_urlsafe(24)}!"
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
            "SECRET_KEY": f"ReceptionOneJwt-{secrets.token_urlsafe(32)}",
            "ENVIRONMENT": "dev",
            "BERNIE_STAFF_PILOT_ENABLED": "true",
            "BERNIE_STAFF_PILOT_PRACTICE_IDS": str(base.PRACTICE_ID),
            "BERNIE_STAFF_PILOT_USER_IDS": str(base.USER_ID),
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false",
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
        raise RuntimeError(f"Reception One runtime failed readiness; logs={runtime_dir}")
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
            "loopback_family": "ipv6",
        },
        processes,
    )


def stop_runtime(processes: list[subprocess.Popen[bytes]]) -> None:
    base.stop_runtime(processes)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup")
    subparsers.add_parser("status")
    subparsers.add_parser("readback")
    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.add_argument("--output", type=Path, default=None)
    serve_parser = subparsers.add_parser("serve-static")
    serve_parser.add_argument("--host", default=IPV6_HOST)
    serve_parser.add_argument("--port", default=STATIC_PORT, type=int)
    args = parser.parse_args()

    try:
        if args.command == "setup":
            password = f"ReceptionOne-{secrets.token_urlsafe(24)}!"
            create_database()
            create_schema_and_seed(password)
            if not readiness_report()["ready"]:
                raise RuntimeError("Reception One database did not pass readiness")
        elif args.command == "status":
            if not readiness_report()["ready"]:
                raise RuntimeError("Reception One database did not pass readiness")
        elif args.command == "readback":
            database_readback()
        elif args.command == "cleanup":
            cleanup = cleanup_database()
            cleanup["schema_version"] = (
                "bernie.reception-one-combined-scope.database-cleanup.v1"
            )
            cleanup["ownership_marker_verified"] = True
            cleanup["scope"] = "authored_synthetic_disposable_database_only"
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
                "schema_version": "bernie.reception-one-combined-scope.cli-status.v1",
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
