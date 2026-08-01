"""Real browser -> FastAPI -> PostgreSQL proof for product-context proposals.

The harness owns one exact IPv6-loopback database and two child processes.
It uses only newly authored synthetic records, performs no request
interception, disables every provider path, verifies forbidden-write surfaces
before and after the browser request, and removes every owned resource.
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time as time_module
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

import bernie_reception_one_combined_scope_harness as base


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-product-context-proposal-runtime"
)
EVIDENCE = OUTPUT / "live-local-browser-backend-postgres-evidence.json"
SCREENSHOT = OUTPUT / "live-local-browser-backend-postgres.png"
LOCKED_DATABASE = (
    "gp_pms_reception_one_product_context_4e731ad9_20260729"
)
RUNTIME_TAG = "reception-one-product-context-4e731ad9"
PRACTICE_ID = base.base.PRACTICE_ID
BACKEND_URL = "http://[::1]:8001"
STATIC_URL = "http://[::1]:3000"
REFERENCE_DATE = "2026-07-27"
INSTRUCTION = (
    "Make an appointment for Margaret Thompson with Dr Alex Shera "
    "today morning"
)


def _configure_database() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev",
    )
    base.LOCKED_DATABASE = LOCKED_DATABASE
    base.RUNTIME_TAG = RUNTIME_TAG
    base._prepare_database_target()


def _safe_child_environment(password: str) -> dict[str, str]:
    """Build an allowlisted child environment without reading provider keys."""

    inherited_names = (
        "COMSPEC",
        "LANG",
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "WINDIR",
    )
    child = {
        name: os.environ[name]
        for name in inherited_names
        if name in os.environ
    }
    child.update(
        {
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "META_GRID_SYNTHETIC_PASSWORD": password,
            "SECRET_KEY": f"ProductContextJwt-{secrets.token_urlsafe(32)}",
            "ENVIRONMENT": "dev",
            "BERNIE_STAFF_PILOT_ENABLED": "true",
            "BERNIE_STAFF_PILOT_PRACTICE_IDS": str(PRACTICE_ID),
            "BERNIE_STAFF_PILOT_USER_IDS": str(base.base.USER_ID),
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": "false",
            "RECEPTION_ONE_PRODUCT_CONTEXT_RUNTIME_ENABLED": "true",
            "RECEPTION_ONE_PRODUCT_CONTEXT_SYNTHETIC_PRACTICE_IDS": str(
                PRACTICE_ID
            ),
            "GOOGLE_APPLICATION_CREDENTIALS": "",
            "GOOGLE_CLOUD_PROJECT": "",
            "CORS_ORIGINS": '["http://[::1]:3000"]',
            "NO_PROXY": "localhost,127.0.0.1,::1,[::1]",
            "no_proxy": "localhost,127.0.0.1,::1,[::1]",
        }
    )
    return child


def _launch_runtime() -> tuple[list[subprocess.Popen[bytes]], Path]:
    password = f"ProductContext-{secrets.token_urlsafe(24)}!"
    base.base.rotate_synthetic_password(password)
    runtime_dir = Path(tempfile.gettempdir()) / f"emr4-{RUNTIME_TAG}"
    if runtime_dir.exists():
        _remove_runtime_dir(runtime_dir)
    runtime_dir.mkdir(parents=True, exist_ok=False)
    paths = {
        "backend_stdout": runtime_dir / "backend.stdout.log",
        "backend_stderr": runtime_dir / "backend.stderr.log",
        "static_stdout": runtime_dir / "static.stdout.log",
        "static_stderr": runtime_dir / "static.stderr.log",
    }
    child_env = _safe_child_environment(password)
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
                "::1",
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
                str(base.__file__),
                "serve-static",
                "--host",
                "::1",
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
    for _ in range(80):
        for name, url in (
            ("backend", f"{BACKEND_URL}/health"),
            ("static", f"{STATIC_URL}/meta-grid-auth.html"),
        ):
            if ready[name]:
                continue
            try:
                with urlopen(url, timeout=0.5) as response:  # nosec B310
                    ready[name] = response.status == 200
            except (OSError, URLError):
                continue
        if all(ready.values()):
            break
        if any(process.poll() is not None for process in processes):
            break
        time_module.sleep(0.25)
    if not all(ready.values()):
        base.stop_runtime(processes)
        raise RuntimeError("Live-local product-context runtime failed readiness")
    return processes, runtime_dir


def _remove_runtime_dir(runtime_dir: Path) -> None:
    resolved = runtime_dir.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if resolved.parent != temp_root or resolved.name != f"emr4-{RUNTIME_TAG}":
        raise RuntimeError("Refusing to remove an unexpected runtime directory")
    for attempt in range(20):
        if not resolved.exists():
            return
        try:
            shutil.rmtree(resolved)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time_module.sleep(0.1)


def _browser_proof() -> tuple[dict[str, object], list[dict[str, str]]]:
    network: list[dict[str, str]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        page = context.new_page()
        page.on(
            "request",
            lambda request: network.append(
                {
                    "method": request.method.upper(),
                    "hostname": urlsplit(request.url).hostname or "",
                    "path": urlsplit(request.url).path,
                }
            ),
        )
        page.goto(
            f"{STATIC_URL}/meta-grid-auth.html",
            wait_until="domcontentloaded",
        )
        page.wait_for_url("**/diary/diary.html?reference_date=2026-07-27**")
        page.goto(
            f"{STATIC_URL}/diary/diary.html"
            "?smoke=true"
            "&meta_grid_open=true"
            "&reception_one_demo=appointment_sheet"
            "&standalone_diary=true"
            f"&reference_date={REFERENCE_DATE}"
            "&product_context_live_local=true",
            wait_until="networkidle",
        )
        request_box = page.get_by_label(
            "What would you like to find or prepare?",
            exact=True,
        )
        request_box.fill(INSTRUCTION)
        with page.expect_response(
            lambda response: (
                response.request.method.upper() == "POST"
                and response.url.split("?", 1)[0].endswith(
                    "/api/v1/appointments/proposals/reception-one/compose"
                )
            ),
            timeout=20_000,
        ) as response_info:
            request_box.press("Enter")
        response = response_info.value
        if response.status != 200:
            raise RuntimeError(
                f"Product-context route returned HTTP {response.status}"
            )
        payload = response.json()
        first_slot = page.get_by_test_id("meta-grid-slot").first
        first_slot.wait_for(state="visible", timeout=20_000)
        first_slot.click()
        page.get_by_text(
            "Selected · not reserved",
            exact=False,
        ).first.wait_for(state="visible", timeout=20_000)
        page.screenshot(path=str(SCREENSHOT), full_page=True)
        result = {
            "http_status": response.status,
            "contract_version": payload["contract_version"],
            "result": payload["result"],
            "goal": payload["goal"],
            "operation_id": payload["operation_id"],
            "candidate_slot_count": len(payload["candidate_slots"]),
            "proofreader_disposition": payload["review"]["disposition"],
            "requires_confirmation": payload["requires_confirmation"],
            "proposal_only": payload["proposal_only"],
            "write_performed": payload["write_performed"],
            "provider_calls": payload["provider_calls"],
            "database_reads_performed": payload[
                "database_reads_performed"
            ],
            "model_database_access": payload["model_database_access"],
        }
        context.close()
        browser.close()
    return result, network


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _configure_database()
    processes: list[subprocess.Popen[bytes]] = []
    runtime_dir: Path | None = None
    database_created = False
    try:
        base.create_database()
        database_created = True
        base.create_schema_and_seed(
            f"ProductContextSeed-{secrets.token_urlsafe(24)}!"
        )
        before = base.database_readback()
        processes, runtime_dir = _launch_runtime()
        browser_result, network = _browser_proof()
        after = base.database_readback()
        route_calls = [
            item
            for item in network
            if (
                item["method"] == "POST"
                and item["path"]
                == "/api/v1/appointments/proposals/reception-one/compose"
            )
        ]
        external_hosts = sorted(
            {
                item["hostname"]
                for item in network
                if item["hostname"]
                not in {"::1", "127.0.0.1", "localhost", ""}
            }
        )
        invariants_unchanged = (
            before["counts"] == after["counts"]
            and before["sha256"] == after["sha256"]
        )
        if len(route_calls) != 1:
            raise RuntimeError("Expected exactly one product-context API call")
        if external_hosts:
            raise RuntimeError(
                f"Unexpected non-loopback browser traffic: {external_hosts}"
            )
        if not invariants_unchanged:
            raise RuntimeError("Forbidden-write surfaces changed")
        if browser_result["provider_calls"] != 0:
            raise RuntimeError("Provider-free runtime reported a provider call")
        evidence = {
            "schema_version": (
                "reception.one.product_context.live_local_acceptance.v1"
            ),
            "result": "live_local_browser_backend_postgres_provider_free_pass",
            "data_class": "authored_synthetic",
            "database": LOCKED_DATABASE,
            "loopback_family": "ipv6",
            "request_interception_used": False,
            "browser_result": browser_result,
            "network": {
                "route_call_count": len(route_calls),
                "external_host_count": 0,
                "allowed_hosts": ["::1", "127.0.0.1", "localhost"],
            },
            "database_before": before,
            "database_after": after,
            "forbidden_write_surfaces_unchanged": True,
            "api_key_authentication_used": False,
            "provider_environment_forwarded": False,
            "provider_calls": 0,
            "appointment_confirmation_performed": False,
            "appointment_write_performed": False,
            "legacy_interpreter_gate_changed": False,
            "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace(
                "\\", "/"
            ),
        }
        EVIDENCE.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            json.dumps(
                {
                    "result": evidence["result"],
                    "route_call_count": len(route_calls),
                    "provider_calls": 0,
                    "writes": 0,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        if processes:
            base.stop_runtime(processes)
        if runtime_dir is not None:
            _remove_runtime_dir(runtime_dir)
        if database_created:
            database_cleanup = base.cleanup_database()
            cleanup_path = (
                OUTPUT / "live-local-database-cleanup-evidence.json"
            )
            cleanup_path.write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "reception.one.product_context."
                            "live_local_database_cleanup.v1"
                        ),
                        "ownership_marker_verified": True,
                        "scope": (
                            "exact_disposable_authored_synthetic_database"
                        ),
                        "cleanup": database_cleanup,
                        "runtime_processes_absent": all(
                            process.poll() is not None
                            for process in processes
                        ),
                        "runtime_temporary_root_absent": (
                            runtime_dir is None or not runtime_dir.exists()
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )


if __name__ == "__main__":
    raise SystemExit(main())
