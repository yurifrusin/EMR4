#!/usr/bin/env python3
"""Run one visible-browser Reception One request through isolated Vertex.

The harness owns an exact disposable authored-synthetic database and IPv6
loopback runtime. It selects the default-off model lane in the real Diary UI,
submits exactly one request, verifies the retained broker/proofreader evidence,
and removes every owned process, database, container, network, image and
temporary runtime directory. It never retries.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import bernie_reception_one_combined_scope_harness as database
from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_live as live


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-live-isolated-planner-evaluation"
)
AUTHORITY_PATH = OUTPUT / "occupied-authority.json"
PREFLIGHT_PATH = OUTPUT / "occupied-preflight-evidence.json"
PROVIDER_FREE_PATH = OUTPUT / "provider-free-evidence.json"
ISOLATION_PATH = OUTPUT / "real-isolation-evidence.json"
PRE_RESIDUE_PATH = OUTPUT / "pre-attempt-residue-evidence.json"
EVIDENCE_PATH = OUTPUT / "occupied-ui-route-evidence.json"
FAILURE_PATH = OUTPUT / "occupied-ui-route-failure-evidence.json"
CLEANUP_PATH = OUTPUT / "occupied-ui-cleanup-evidence.json"
POST_RESIDUE_PATH = OUTPUT / "occupied-final-residue-evidence.json"
SCREENSHOT_PATH = OUTPUT / "occupied-isolated-planner-result.png"
LOCKED_DATABASE = (
    "gp_pms_reception_one_bureau_isolated_9c6f41e7_20260731"
)
RUNTIME_TAG = "reception-one-bureau-isolated-9c6f41e7"
RUNTIME_DIR = Path(tempfile.gettempdir()) / f"emr4-{RUNTIME_TAG}"
BACKEND_HOST = "::1"
BACKEND_PORT = 8001
STATIC_HOST = "::1"
STATIC_PORT = 3000
BACKEND_URL = f"http://[{BACKEND_HOST}]:{BACKEND_PORT}"
STATIC_URL = f"http://[{STATIC_HOST}]:{STATIC_PORT}"
REFERENCE_DATE = "2026-08-03"
INSTRUCTION = (
    "Extend Margaret Thompson's appointment with Dr Alex Shera "
    "to 45 minutes."
)
GRAPH_REVISION = 158
COMPASS_REVISION = 139
EXPECTED_BINDING = {
    "api_key_authentication_used": False,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": (
        "australia-southeast1-aiplatform.googleapis.com"
    ),
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": (
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    ),
}
OWNED_CONTAINERS = (live.RELAY_CONTAINER, live.CELL_CONTAINER)
OWNED_IMAGES = (live.RELAY_IMAGE, live.CELL_IMAGE)
OWNED_NETWORK = live.NETWORK


class OccupiedUiError(RuntimeError):
    """A sanitized browser, route, evidence or lifecycle failure."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise OccupiedUiError(f"control_artifact_invalid:{path.name}") from error
    if not isinstance(value, dict):
        raise OccupiedUiError(f"control_artifact_invalid:{path.name}")
    return value


def _canonical_hash(value: Any) -> str:
    return lane.canonical_hash(value)


def _configure_database() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev",
    )
    database.LOCKED_DATABASE = LOCKED_DATABASE
    database.RUNTIME_TAG = RUNTIME_TAG
    database._prepare_database_target()


def _database_exists() -> bool:
    target = make_url(os.environ["DATABASE_URL"])
    engine = create_engine(
        target.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
    )
    try:
        with engine.connect() as connection:
            return bool(
                connection.execute(
                    text(
                        "SELECT 1 FROM pg_database "
                        "WHERE datname = :database_name"
                    ),
                    {"database_name": LOCKED_DATABASE},
                ).scalar()
            )
    finally:
        engine.dispose()


def _docker_exists(kind: str, reference: str) -> bool:
    docker = shutil.which("docker")
    if docker is None:
        raise OccupiedUiError("docker_unavailable")
    result = subprocess.run(
        [docker, kind, "inspect", reference],
        cwd=ROOT,
        check=False,
        capture_output=True,
        timeout=20,
        shell=False,
    )
    return result.returncode == 0


def _port_available(host: str, port: int) -> bool:
    probe = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        probe.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        probe.close()


def _residue_snapshot(*, phase: str) -> dict[str, Any]:
    containers = {
        name: _docker_exists("container", name)
        for name in OWNED_CONTAINERS
    }
    images = {
        name: _docker_exists("image", name)
        for name in OWNED_IMAGES
    }
    request_artifacts = sorted(
        path.name for path in OUTPUT.glob("runtime-*") if path.is_dir()
    )
    unexpected = request_artifacts if phase == "pre_attempt" else []
    value = {
        "schema_version": (
            "reception.one.bureau_live_isolated_planner.residue.v1"
        ),
        "recorded_at": _utc_now(),
        "phase": phase,
        "owned_containers_present": containers,
        "owned_images_present": images,
        "owned_network_present": _docker_exists(
            "network",
            OWNED_NETWORK,
        ),
        "owned_runtime_directory_present": RUNTIME_DIR.exists(),
        "owned_database_present": _database_exists(),
        "backend_port_available": _port_available(
            BACKEND_HOST,
            BACKEND_PORT,
        ),
        "static_port_available": _port_available(
            STATIC_HOST,
            STATIC_PORT,
        ),
        "request_artifact_directories": request_artifacts,
        "unexpected_request_artifact_directories": unexpected,
    }
    value["clear"] = (
        not any(containers.values())
        and not any(images.values())
        and value["owned_network_present"] is False
        and value["owned_runtime_directory_present"] is False
        and value["owned_database_present"] is False
        and value["backend_port_available"] is True
        and value["static_port_available"] is True
        and unexpected == []
    )
    return value


def run_pre_attempt_residue() -> dict[str, Any]:
    _configure_database()
    if any(
        path.exists()
        for path in (
            PRE_RESIDUE_PATH,
            EVIDENCE_PATH,
            FAILURE_PATH,
            CLEANUP_PATH,
            POST_RESIDUE_PATH,
            SCREENSHOT_PATH,
        )
    ):
        raise OccupiedUiError("occupied_output_preexisted")
    value = _residue_snapshot(phase="pre_attempt")
    if value["clear"] is not True:
        raise OccupiedUiError("pre_attempt_residue_not_clear")
    _write_json(PRE_RESIDUE_PATH, value)
    return value


def _safe_child_environment(password: str) -> dict[str, str]:
    """Allow only runtime, database and existing ADC-discovery environment."""

    inherited_names = (
        "APPDATA",
        "COMSPEC",
        "LANG",
        "LOCALAPPDATA",
        "PATH",
        "PATHEXT",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "USERPROFILE",
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
            "SECRET_KEY": f"BureauIsolatedJwt-{secrets.token_urlsafe(32)}",
            "ENVIRONMENT": "dev",
            "BERNIE_STAFF_PILOT_ENABLED": "true",
            "BERNIE_STAFF_PILOT_PRACTICE_IDS": str(
                database.base.PRACTICE_ID
            ),
            "BERNIE_STAFF_PILOT_USER_IDS": str(database.base.USER_ID),
            "BERNIE_BOOKING_INTERPRETER_PROVIDER": "disabled",
            "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC": (
                "false"
            ),
            "RECEPTION_ONE_PRODUCT_CONTEXT_RUNTIME_ENABLED": "true",
            "RECEPTION_ONE_PRODUCT_CONTEXT_SYNTHETIC_PRACTICE_IDS": str(
                database.base.PRACTICE_ID
            ),
            "RECEPTION_ONE_PRODUCT_CONTEXT_VERTEX_PLANNER_ENABLED": "true",
            "RECEPTION_ONE_PRODUCT_CONTEXT_VERTEX_AUTHORITY_PATH": str(
                AUTHORITY_PATH
            ),
            "RECEPTION_ONE_PRODUCT_CONTEXT_VERTEX_PREFLIGHT_PATH": str(
                PREFLIGHT_PATH
            ),
            "RECEPTION_ONE_PRODUCT_CONTEXT_VERTEX_EVIDENCE_DIR": str(
                OUTPUT
            ),
            "CORS_ORIGINS": f'["{STATIC_URL}"]',
            "NO_PROXY": "localhost,127.0.0.1,::1,[::1]",
            "no_proxy": "localhost,127.0.0.1,::1,[::1]",
        }
    )
    return child


def _remove_runtime_dir() -> None:
    resolved = RUNTIME_DIR.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if resolved.parent != temp_root or resolved.name != f"emr4-{RUNTIME_TAG}":
        raise OccupiedUiError("runtime_directory_scope_invalid")
    for attempt in range(30):
        if not resolved.exists():
            return
        try:
            shutil.rmtree(resolved)
            return
        except PermissionError:
            if attempt == 29:
                raise OccupiedUiError(
                    "runtime_directory_cleanup_failed"
                )
            time.sleep(0.1)


def _launch_runtime(password: str) -> list[subprocess.Popen[bytes]]:
    if RUNTIME_DIR.exists():
        raise OccupiedUiError("runtime_directory_preexisted")
    RUNTIME_DIR.mkdir(parents=True, exist_ok=False)
    paths = {
        "backend_stdout": RUNTIME_DIR / "backend.stdout.log",
        "backend_stderr": RUNTIME_DIR / "backend.stderr.log",
        "static_stdout": RUNTIME_DIR / "static.stdout.log",
        "static_stderr": RUNTIME_DIR / "static.stderr.log",
    }
    handles = {name: path.open("wb") for name, path in paths.items()}
    child = _safe_child_environment(password)
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        backend = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                BACKEND_HOST,
                "--port",
                str(BACKEND_PORT),
                "--log-level",
                "warning",
                "--no-access-log",
            ],
            cwd=ROOT,
            env=child,
            stdout=handles["backend_stdout"],
            stderr=handles["backend_stderr"],
            creationflags=creationflags,
        )
        static = subprocess.Popen(
            [
                sys.executable,
                str(database.__file__),
                "serve-static",
                "--host",
                STATIC_HOST,
                "--port",
                str(STATIC_PORT),
            ],
            cwd=ROOT,
            env=child,
            stdout=handles["static_stdout"],
            stderr=handles["static_stderr"],
            creationflags=creationflags,
        )
    finally:
        for handle in handles.values():
            handle.close()
    processes = [backend, static]
    ready = {"backend": False, "static": False}
    for _ in range(120):
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
            return processes
        if any(process.poll() is not None for process in processes):
            break
        time.sleep(0.25)
    database.base.stop_runtime(processes)
    raise OccupiedUiError("runtime_readiness_failed")


def _browser_request() -> tuple[dict[str, Any], dict[str, Any]]:
    network: list[dict[str, str]] = []
    route_request_hashes: list[str] = []
    submitted_modes: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
        )
        page = context.new_page()

        def record_request(request) -> None:
            parsed = urlsplit(request.url)
            network.append(
                {
                    "method": request.method.upper(),
                    "hostname": parsed.hostname or "",
                    "path": parsed.path,
                }
            )
            if (
                request.method.upper() == "POST"
                and parsed.path
                == "/api/v1/appointments/proposals/reception-one/compose"
            ):
                body = request.post_data_json or {}
                submitted_modes.append(str(body.get("planner_mode", "")))
                route_request_hashes.append(_canonical_hash(body))

        page.on("request", record_request)
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
            "&product_context_live_local=true"
            "&bureau_runtime_ui=true",
            wait_until="networkidle",
        )
        planner = page.get_by_test_id("meta-grid-planner-mode")
        planner.wait_for(state="visible")
        planner.select_option("isolated_vertex")
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
            timeout=240_000,
        ) as response_info:
            request_box.press("Enter")
        response = response_info.value
        try:
            payload = response.json()
        except ValueError as error:
            raise OccupiedUiError("route_response_invalid") from error
        if not isinstance(payload, dict):
            raise OccupiedUiError("route_response_invalid")

        provenance_text = None
        if (
            response.status == 200
            and payload.get("result") == "proposal_ready"
        ):
            provenance = page.get_by_test_id("meta-grid-planner-provenance")
            provenance.wait_for(state="visible", timeout=20_000)
            provenance_text = provenance.inner_text()
        page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)
        context.close()
        browser.close()

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
    browser_evidence = {
        "http_status": response.status,
        "submitted_modes": submitted_modes,
        "route_call_count": len(route_calls),
        "route_request_hashes": route_request_hashes,
        "external_hosts": external_hosts,
        "request_interception_used": False,
        "rendered_provenance": provenance_text,
    }
    return payload, browser_evidence


def _validate_hash_chain(path: Path) -> dict[str, Any]:
    events = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    previous = "sha256:" + "0" * 64
    for sequence, event in enumerate(events, start=1):
        if (
            event.get("sequence") != sequence
            or event.get("previous_hash") != previous
        ):
            raise OccupiedUiError("parent_audit_hash_chain_invalid")
        claimed = event.get("event_hash")
        unsigned = dict(event)
        unsigned.pop("event_hash", None)
        if claimed != _canonical_hash(unsigned):
            raise OccupiedUiError("parent_audit_hash_chain_invalid")
        previous = claimed
    if not events:
        raise OccupiedUiError("parent_audit_hash_chain_invalid")
    return {
        "valid": True,
        "event_count": len(events),
        "terminal_hash": previous,
    }


def _runtime_audit(payload: dict[str, Any]) -> dict[str, Any]:
    audit_ref = payload.get("runtime_audit_ref")
    if not isinstance(audit_ref, str) or not audit_ref.startswith("runtime-"):
        raise OccupiedUiError("runtime_audit_ref_invalid")
    artifact_dir = OUTPUT / audit_ref
    if not artifact_dir.is_dir():
        raise OccupiedUiError("runtime_audit_directory_missing")
    parent = _load(artifact_dir / "occupied-dialogue-evidence.json")
    first = _load(artifact_dir / "occupied-turn-001-evidence.json")
    ledger = _load(artifact_dir / "occupied-turn-001-ledger.json")
    external = _load(
        artifact_dir / "occupied-turn-001-external-audit.json"
    )
    manifest = _load(artifact_dir / "runtime-frame-manifest.json")
    exchange = first.get("exchange")
    proofreader = (
        exchange.get("proofreader")
        if isinstance(exchange, dict)
        else None
    )
    cleanup = first.get("cleanup")
    if (
        parent.get("actual_provider_call_count") != 1
        or parent.get("absolute_provider_call_ceiling") != 1
        or len(parent.get("turns", [])) != 1
        or (artifact_dir / "occupied-turn-002-ledger.json").exists()
        or ledger.get("status") != "consumed"
        or ledger.get("provider_calls_consumed") != 1
        or first.get("exact_binding") != EXPECTED_BINDING
        or external.get("durable_hash_chain", {}).get("valid") is not True
        or not isinstance(proofreader, dict)
        or not isinstance(cleanup, dict)
        or not all(
            value is True
            for key, value in cleanup.items()
            if key != "daemon_wide_prune_performed"
        )
        or (artifact_dir / "runtime-frame.json").exists()
        or manifest.get("raw_frame_retained") is not False
        or manifest.get("raw_prompt_retained") is not False
    ):
        raise OccupiedUiError("runtime_audit_contract_invalid")
    for path in artifact_dir.rglob("*"):
        if (
            path.is_file()
            and INSTRUCTION
            in path.read_text(encoding="utf-8", errors="replace")
        ):
            raise OccupiedUiError("raw_prompt_retained")
    return {
        "audit_ref": audit_ref,
        "attempt_ids": parent.get("attempt_ids"),
        "ledger_ids": parent.get("ledger_ids"),
        "actual_provider_call_count": 1,
        "absolute_provider_call_ceiling": 1,
        "terminal_status": parent.get("terminal_status"),
        "release_present": parent.get("release") is not None,
        "proofreader": {
            "disposition": proofreader.get("disposition"),
            "violations": proofreader.get("violations"),
            "safe_repairs": proofreader.get("safe_repairs"),
            "admitted_operator_ids": proofreader.get(
                "admitted_operator_ids"
            ),
        },
        "exact_binding": first.get("exact_binding"),
        "cleanup": cleanup,
        "parent_hash_chain": _validate_hash_chain(
            artifact_dir / "occupied-dialogue-parent-audit.jsonl"
        ),
        "external_audit_hash_chain_valid": True,
        "raw_frame_retained": False,
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "chain_of_thought_retained": False,
        "credential_material_retained": False,
    }


def _runtime_local_failure_code() -> str | None:
    diagnostics = sorted(
        OUTPUT.glob("runtime-*/runtime-local-failure-diagnostic.json")
    )
    if len(diagnostics) != 1:
        return None
    diagnostic = _load(diagnostics[0])
    code = diagnostic.get("reason_code")
    if (
        not isinstance(code, str)
        or not code
        or diagnostic.get("raw_exception_retained") is not False
        or diagnostic.get("raw_prompt_retained") is not False
        or diagnostic.get("raw_provider_response_retained") is not False
        or diagnostic.get("credential_material_retained") is not False
    ):
        raise OccupiedUiError("runtime_local_failure_diagnostic_invalid")
    return code


def _controls() -> dict[str, Any]:
    authority = _load(AUTHORITY_PATH)
    preflight = _load(PREFLIGHT_PATH)
    provider_free = _load(PROVIDER_FREE_PATH)
    isolation = _load(ISOLATION_PATH)
    expected_revision = {
        "graph_revision": GRAPH_REVISION,
        "compass_revision": COMPASS_REVISION,
        "compass_source_graph_revision": GRAPH_REVISION,
    }
    if (
        authority.get("authority_granted") is not True
        or authority.get("absolute_call_ceiling") != 1
        or authority.get("terminal_correction_call_ceiling") != 0
        or authority.get("continuity_binding") != expected_revision
        or preflight.get("result")
        != "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
        or not all(preflight.get("checks", {}).values())
        or provider_free.get("result")
        != "reception_one_default_off_dual_planner_provider_free_pass"
        or isolation.get("result")
        != "reception_one_receptionist_first_v68_real_isolation_pass"
        or isolation.get("boundary", {}).get("provider_calls_performed") != 0
    ):
        raise OccupiedUiError("occupied_controls_not_exact")
    return {
        "authority_sha256": _canonical_hash(authority),
        "preflight_sha256": _canonical_hash(preflight),
        "provider_free_sha256": _canonical_hash(provider_free),
        "isolation_sha256": _canonical_hash(isolation),
        "continuity_binding": expected_revision,
    }


def run_occupied() -> dict[str, Any]:
    _configure_database()
    controls = _controls()
    pre_residue = _load(PRE_RESIDUE_PATH)
    if pre_residue.get("clear") is not True:
        raise OccupiedUiError("pre_attempt_residue_not_clear")

    password = f"BureauIsolated-{secrets.token_urlsafe(24)}!"
    processes: list[subprocess.Popen[bytes]] = []
    database_created = False
    cleanup: dict[str, Any] | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    payload: dict[str, Any] | None = None
    browser: dict[str, Any] | None = None
    runtime_audit: dict[str, Any] | None = None
    failure: Exception | None = None
    try:
        database.create_database()
        database_created = True
        database.create_schema_and_seed(password)
        before = database.database_readback()
        processes = _launch_runtime(password)
        payload, browser = _browser_request()
        after = database.database_readback()
        if (
            before.get("counts") != after.get("counts")
            or before.get("sha256") != after.get("sha256")
        ):
            raise OccupiedUiError("database_truth_changed")
        if browser.get("http_status") != 200:
            raise OccupiedUiError(
                _runtime_local_failure_code()
                or "occupied_route_http_error"
            )
        runtime_audit = _runtime_audit(payload)
    except Exception as error:
        failure = error
    finally:
        if processes:
            database.base.stop_runtime(processes)
        try:
            _remove_runtime_dir()
        except Exception as error:
            failure = failure or error
        if database_created:
            try:
                cleanup = database.cleanup_database()
            except Exception as error:
                failure = failure or error

    post_residue = _residue_snapshot(phase="post_attempt")
    _write_json(POST_RESIDUE_PATH, post_residue)
    _write_json(
        CLEANUP_PATH,
        {
            "schema_version": (
                "reception.one.bureau_live_isolated_planner.cleanup.v1"
            ),
            "ownership_marker_verified": database_created,
            "database_cleanup": cleanup,
            "runtime_processes_absent": all(
                process.poll() is not None for process in processes
            ),
            "runtime_directory_absent": not RUNTIME_DIR.exists(),
            "post_attempt_residue_clear": post_residue["clear"],
        },
    )
    reason = (
        str(failure).split(":", 1)[0]
        if failure is not None
        else None
    )
    if failure is not None or post_residue["clear"] is not True:
        _write_json(
            FAILURE_PATH,
            {
                "schema_version": (
                    "reception.one.bureau_live_isolated_planner."
                    "occupied_failure.v1"
                ),
                "result": (
                    "reception_one_bureau_live_isolated_planner_"
                    "failed_closed"
                ),
                "reason_code": reason or "post_attempt_residue_not_clear",
                "provider_calls_performed": (
                    runtime_audit.get("actual_provider_call_count")
                    if runtime_audit
                    else None
                ),
                "retry_performed": False,
                "fallback_performed": False,
                "appointment_write_performed": False,
                "raw_prompt_retained": False,
                "raw_provider_response_retained": False,
                "credential_material_retained": False,
                "post_attempt_residue_clear": post_residue["clear"],
            },
        )
        raise OccupiedUiError(
            reason or "post_attempt_residue_not_clear"
        ) from failure

    assert payload is not None
    assert browser is not None
    assert runtime_audit is not None
    assert before is not None and after is not None
    admitted = (
        browser["http_status"] == 200
        and browser["submitted_modes"] == ["isolated_vertex"]
        and browser["route_call_count"] == 1
        and browser["external_hosts"] == []
        and payload.get("result") == "proposal_ready"
        and payload.get("goal") == "resize"
        and payload.get("planner_mode") == "isolated_vertex"
        and payload.get("provider_calls") == 1
        and payload.get("proposed_duration_minutes") == 45
        and payload.get("requires_confirmation") is True
        and payload.get("proposal_only") is True
        and payload.get("write_performed") is False
        and payload.get("confirmation_performed") is False
        and payload.get("model_database_access") is False
        and payload.get("review", {}).get("disposition") == "admit"
        and runtime_audit["proofreader"]["disposition"] == "admit"
        and runtime_audit["release_present"] is True
        and browser["rendered_provenance"] is not None
        and "Isolated model" in browser["rendered_provenance"]
        and "Proofreader admitted" in browser["rendered_provenance"]
        and "1 provider call" in browser["rendered_provenance"]
    )
    result = (
        "reception_one_bureau_live_isolated_planner_occupied_pass"
        if admitted
        else "reception_one_bureau_live_isolated_planner_failed_closed"
    )
    evidence = {
        "schema_version": (
            "reception.one.bureau_live_isolated_planner."
            "occupied_ui_route_evidence.v1"
        ),
        "result": result,
        "recorded_at": _utc_now(),
        "evidence_label": (
            "live_local_browser_backend_postgres_and_live_provider"
        ),
        "data_class": "authored_synthetic",
        "controls": controls,
        "browser": browser,
        "route_release": {
            "result": payload.get("result"),
            "goal": payload.get("goal"),
            "operation_id": payload.get("operation_id"),
            "planner_mode": payload.get("planner_mode"),
            "provider_calls": payload.get("provider_calls"),
            "proofreader_disposition": payload.get("review", {}).get(
                "disposition"
            ),
            "proposed_duration_minutes": payload.get(
                "proposed_duration_minutes"
            ),
            "requires_confirmation": payload.get(
                "requires_confirmation"
            ),
            "proposal_only": payload.get("proposal_only"),
            "write_performed": payload.get("write_performed"),
            "confirmation_performed": payload.get(
                "confirmation_performed"
            ),
            "runtime_audit_ref": payload.get("runtime_audit_ref"),
        },
        "runtime_audit": runtime_audit,
        "database_before": before,
        "database_after": after,
        "database_unchanged": True,
        "api_key_authentication_used": False,
        "provider_environment_forwarded_to_cell": False,
        "retry_performed": False,
        "fallback_performed": False,
        "appointment_write_performed": False,
        "appointment_confirmation_performed": False,
        "post_attempt_residue_clear": True,
        "screenshot": str(SCREENSHOT_PATH.relative_to(ROOT)).replace(
            "\\",
            "/",
        ),
        "candid_limit": (
            "This evidence can establish one authored-synthetic UI-to-route-"
            "to-proofreader exchange through the configured and observed "
            "Sydney Vertex locational endpoint. It does not establish "
            "Australian physical or sovereign processing, production "
            "fitness, or authority for real patient, health or clinical data."
        ),
    }
    evidence["evidence_hash"] = _canonical_hash(evidence)
    _write_json(EVIDENCE_PATH, evidence)
    if not admitted:
        _write_json(
            FAILURE_PATH,
            {
                "schema_version": (
                    "reception.one.bureau_live_isolated_planner."
                    "occupied_failure.v1"
                ),
                "result": result,
                "reason_code": "proofreader_or_route_not_admitted",
                "provider_calls_performed": 1,
                "retry_performed": False,
                "fallback_performed": False,
                "appointment_write_performed": False,
                "post_attempt_residue_clear": True,
            },
        )
        raise OccupiedUiError("proofreader_or_route_not_admitted")
    return evidence


def main() -> int:
    try:
        if not PRE_RESIDUE_PATH.exists():
            run_pre_attempt_residue()
        evidence = run_occupied()
    except OccupiedUiError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_bureau_live_isolated_planner_"
                        "failed_closed"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                    "retry_performed": False,
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_calls": 1,
                "proofreader": "admit",
                "writes": 0,
                "retry_performed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
