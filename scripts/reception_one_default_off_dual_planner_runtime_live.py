#!/usr/bin/env python3
"""Exercise one exact occupied synthetic Reception One product route."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
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

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import bernie_reception_one_combined_scope_harness as database
from scripts import reception_one_bureau_model_text_lane_live as live


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-default-off-dual-planner-runtime"
)
AUTHORITY_PATH = OUTPUT / "occupied-authority.json"
PREFLIGHT_PATH = OUTPUT / "occupied-preflight-evidence.json"
PROVIDER_FREE_PATH = OUTPUT / "provider-free-evidence.json"
PRE_RESIDUE_PATH = OUTPUT / "pre-attempt-residue-evidence.json"
POST_RESIDUE_PATH = OUTPUT / "occupied-final-residue-evidence.json"
OCCUPIED_EVIDENCE_PATH = OUTPUT / "occupied-route-evidence.json"
FAILURE_PATH = OUTPUT / "occupied-route-failure-evidence.json"
CLEANUP_PATH = OUTPUT / "live-local-database-cleanup-evidence.json"
LOCKED_DATABASE = (
    "gp_pms_reception_one_dual_planner_6f4e29c1_20260730"
)
RUNTIME_TAG = "reception-one-dual-planner-6f4e29c1"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8012
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
REFERENCE_DATE = "2026-08-03"
SELECTED_APPOINTMENT_ID = str(
    database.base.fixed_id("appointment-margaret-shera-next")
)
RUNTIME_DIR = Path(tempfile.gettempdir()) / f"emr4-{RUNTIME_TAG}"
OWNED_CONTAINERS = (live.RELAY_CONTAINER, live.CELL_CONTAINER)
OWNED_IMAGES = (live.RELAY_IMAGE, live.CELL_IMAGE)
OWNED_NETWORK = live.NETWORK
GRAPH_REVISION = 152
COMPASS_REVISION = 133


class OccupiedRouteError(RuntimeError):
    """A sanitized local, control, route or lifecycle failure."""


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
        raise OccupiedRouteError(
            f"control_artifact_invalid:{path.name}"
        ) from error
    if not isinstance(value, dict):
        raise OccupiedRouteError(f"control_artifact_invalid:{path.name}")
    return value


def _canonical_hash(value: Any) -> str:
    rendered = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(rendered).hexdigest()


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
        raise OccupiedRouteError("docker_unavailable")
    result = subprocess.run(
        [docker, kind, "inspect", reference],
        cwd=ROOT,
        check=False,
        capture_output=True,
        timeout=20,
        shell=False,
    )
    return result.returncode == 0


def _port_available() -> bool:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.bind((BACKEND_HOST, BACKEND_PORT))
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
    network_present = _docker_exists("network", OWNED_NETWORK)
    request_artifacts = sorted(
        path.name for path in OUTPUT.glob("runtime-*") if path.is_dir()
    )
    unexpected_request_artifacts = (
        request_artifacts if phase == "pre_attempt" else []
    )
    snapshot = {
        "schema_version": (
            "reception.one.default_off_dual_planner.residue.v1"
        ),
        "recorded_at": _utc_now(),
        "phase": phase,
        "owned_containers_present": containers,
        "owned_images_present": images,
        "owned_network_present": network_present,
        "owned_runtime_directory_present": RUNTIME_DIR.exists(),
        "owned_database_present": _database_exists(),
        "owned_backend_port_available": _port_available(),
        "request_artifact_directories": request_artifacts,
        "unexpected_request_artifact_directories": (
            unexpected_request_artifacts
        ),
    }
    snapshot["clear"] = (
        not any(containers.values())
        and not any(images.values())
        and network_present is False
        and snapshot["owned_runtime_directory_present"] is False
        and snapshot["owned_database_present"] is False
        and snapshot["owned_backend_port_available"] is True
        and unexpected_request_artifacts == []
    )
    return snapshot


def run_pre_attempt_residue() -> dict[str, Any]:
    _configure_database()
    if any(
        path.exists()
        for path in (
            OCCUPIED_EVIDENCE_PATH,
            FAILURE_PATH,
            POST_RESIDUE_PATH,
            CLEANUP_PATH,
        )
    ):
        raise OccupiedRouteError("occupied_output_preexisted")
    snapshot = _residue_snapshot(phase="pre_attempt")
    if snapshot["clear"] is not True:
        raise OccupiedRouteError("pre_attempt_residue_not_clear")
    _write_json(PRE_RESIDUE_PATH, snapshot)
    return snapshot


def _safe_child_environment(password: str) -> dict[str, str]:
    allowed = (
        "APPDATA",
        "COMSPEC",
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
        for name in allowed
        if name in os.environ
    }
    child.update(
        {
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "META_GRID_SYNTHETIC_PASSWORD": password,
            "SECRET_KEY": f"DualPlannerJwt-{secrets.token_urlsafe(32)}",
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
            "NO_PROXY": "localhost,127.0.0.1,::1,[::1]",
            "no_proxy": "localhost,127.0.0.1,::1,[::1]",
        }
    )
    return child


def _remove_runtime_dir() -> None:
    resolved = RUNTIME_DIR.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if resolved.parent != temp_root or resolved.name != f"emr4-{RUNTIME_TAG}":
        raise OccupiedRouteError("runtime_directory_scope_invalid")
    for attempt in range(30):
        if not resolved.exists():
            return
        try:
            shutil.rmtree(resolved)
            return
        except PermissionError:
            if attempt == 29:
                raise OccupiedRouteError(
                    "runtime_directory_cleanup_failed"
                )
            time.sleep(0.1)


def _launch_backend(password: str) -> subprocess.Popen[bytes]:
    if RUNTIME_DIR.exists():
        raise OccupiedRouteError("runtime_directory_preexisted")
    RUNTIME_DIR.mkdir(parents=True, exist_ok=False)
    stdout_path = RUNTIME_DIR / "backend.stdout.log"
    stderr_path = RUNTIME_DIR / "backend.stderr.log"
    stdout = stdout_path.open("wb")
    stderr = stderr_path.open("wb")
    try:
        process = subprocess.Popen(
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
            env=_safe_child_environment(password),
            stdout=stdout,
            stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    finally:
        stdout.close()
        stderr.close()
    for _ in range(120):
        if process.poll() is not None:
            raise OccupiedRouteError("backend_failed_before_ready")
        try:
            with httpx.Client(
                timeout=0.5,
                trust_env=False,
            ) as client:
                response = client.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                return process
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    raise OccupiedRouteError("backend_readiness_timeout")


def _stop_backend(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _request_body(planner_mode: str) -> dict[str, Any]:
    return {
        "contract_version": "reception.one.product-context-request.v1",
        "instruction": (
            "Extend Margaret Thompson's appointment with Dr Alex Shera "
            "to 45 minutes."
        ),
        "reference_date": REFERENCE_DATE,
        "surface_id": "diary-main",
        "correlation_id": "synthetic-dual-planner-occupied-001",
        "data_class": "authored_synthetic",
        "selected_appointment_id": SELECTED_APPOINTMENT_ID,
        "planner_mode": planner_mode,
    }


def _make_request(
    password: str,
    *,
    planner_mode: str = "isolated_vertex",
) -> tuple[dict[str, Any], str]:
    request = _request_body(planner_mode)
    with httpx.Client(
        base_url=BACKEND_URL,
        timeout=httpx.Timeout(240),
        trust_env=False,
    ) as client:
        login = client.post(
            "/api/v1/auth/login",
            data={
                "username": database.base.SYNTHETIC_EMAIL,
                "password": password,
            },
        )
        if login.status_code != 200:
            raise OccupiedRouteError("synthetic_login_failed")
        token = login.json().get("access_token")
        if not isinstance(token, str) or not token:
            raise OccupiedRouteError("synthetic_login_failed")
        response = client.post(
            "/api/v1/appointments/proposals/reception-one/compose",
            headers={"Authorization": f"Bearer {token}"},
            json=request,
        )
    if response.status_code != 200:
        code = "route_failed"
        try:
            detail = response.json().get("detail")
            if isinstance(detail, dict) and isinstance(
                detail.get("code"), str
            ):
                code = detail["code"]
        except (ValueError, AttributeError):
            pass
        raise OccupiedRouteError(code)
    value = response.json()
    if not isinstance(value, dict):
        raise OccupiedRouteError("route_response_invalid")
    return value, _canonical_hash(request)


def _validate_provider_free_replay(value: dict[str, Any]) -> None:
    adapter = value.get("adapter_review")
    if (
        value.get("result") != "proposal_ready"
        or value.get("safe") is not True
        or value.get("goal") != "resize"
        or value.get("operation_id") != "proposeAppointmentUpdate"
        or value.get("planner_mode") != "deterministic"
        or value.get("provider_calls") != 0
        or value.get("runtime_audit_ref") is not None
        or value.get("proposed_duration_minutes") != 45
        or value.get("requires_confirmation") is not True
        or value.get("proposal_only") is not True
        or value.get("write_performed") is not False
        or value.get("confirmation_performed") is not False
        or not isinstance(adapter, dict)
        or adapter.get("adapter_kind") != "update_proposal"
        or adapter.get("safe") is not True
        or adapter.get("freshness_verified") is not True
        or adapter.get("confirmation_evidence_released") is not False
        or adapter.get("write_performed") is not False
    ):
        raise OccupiedRouteError("provider_free_route_replay_invalid")


def _validate_route_result(
    value: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    if (
        value.get("contract_version")
        != "reception.one.product-context-proposal.v1"
        or value.get("result") != "proposal_ready"
        or value.get("safe") is not True
        or value.get("goal") != "resize"
        or value.get("operation_id") != "proposeAppointmentUpdate"
        or value.get("planner_mode") != "isolated_vertex"
        or value.get("provider_calls") not in {1, 2}
        or value.get("proposed_duration_minutes") != 45
        or value.get("requires_confirmation") is not True
        or value.get("proposal_only") is not True
        or value.get("write_performed") is not False
        or value.get("confirmation_performed") is not False
        or value.get("model_database_access") is not False
        or value.get("database_reads_performed") is not True
        or value.get("legacy_interpreter_gate_changed") is not False
    ):
        raise OccupiedRouteError("route_release_contract_invalid")
    adapter = value.get("adapter_review")
    if (
        not isinstance(adapter, dict)
        or adapter.get("adapter_kind") != "update_proposal"
        or adapter.get("safe") is not True
        or adapter.get("freshness_verified") is not True
        or adapter.get("confirmation_evidence_released") is not False
        or adapter.get("write_performed") is not False
    ):
        raise OccupiedRouteError("route_adapter_contract_invalid")
    audit_ref = value.get("runtime_audit_ref")
    if (
        not isinstance(audit_ref, str)
        or not audit_ref.startswith("runtime-")
    ):
        raise OccupiedRouteError("runtime_audit_ref_invalid")
    artifact_dir = OUTPUT / audit_ref
    if not artifact_dir.is_dir():
        raise OccupiedRouteError("runtime_audit_directory_missing")
    manifest = _load(artifact_dir / "runtime-frame-manifest.json")
    if (
        (artifact_dir / "runtime-frame.json").exists()
        or manifest.get("raw_frame_retained") is not False
        or manifest.get("raw_prompt_retained") is not False
        or not isinstance(manifest.get("request_sha256"), str)
    ):
        raise OccupiedRouteError("raw_frame_cleanup_invalid")
    return artifact_dir, manifest


def _validate_runtime_audit(
    artifact_dir: Path,
    provider_calls: int,
) -> dict[str, Any]:
    ledgers = sorted(artifact_dir.glob("occupied-turn-*-ledger.json"))
    if len(ledgers) != provider_calls:
        raise OccupiedRouteError("ledger_count_invalid")
    for path in ledgers:
        ledger = _load(path)
        if (
            ledger.get("status") != "consumed"
            or ledger.get("provider_calls_consumed") != 1
        ):
            raise OccupiedRouteError("ledger_not_consumed")
    final_evidence = _load(
        artifact_dir / f"occupied-turn-{provider_calls:03d}-evidence.json"
    )
    binding = final_evidence.get("exact_binding")
    cleanup = final_evidence.get("cleanup")
    exchange = final_evidence.get("exchange")
    proofreader = (
        exchange.get("proofreader")
        if isinstance(exchange, dict)
        else None
    )
    if (
        binding
        != {
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
                "emr4-bernie-ai-dev@bernie-emr4-dev."
                "iam.gserviceaccount.com"
            ),
        }
        or not isinstance(cleanup, dict)
        or not all(
            result is True
            for key, result in cleanup.items()
            if key != "daemon_wide_prune_performed"
        )
        or not isinstance(proofreader, dict)
        or proofreader.get("disposition") != "admit"
    ):
        raise OccupiedRouteError("runtime_audit_contract_invalid")
    forbidden_text = (
        "Extend Margaret Thompson's appointment with Dr Alex Shera "
        "to 45 minutes."
    )
    for path in artifact_dir.rglob("*"):
        if path.is_file() and forbidden_text in path.read_text(
            encoding="utf-8",
            errors="replace",
        ):
            raise OccupiedRouteError("raw_prompt_retained")
    return {
        "ledger_count": len(ledgers),
        "all_ledgers_consumed": True,
        "proofreader_disposition": proofreader["disposition"],
        "proofreader_violation_paths": [
            item.get("path")
            for item in proofreader.get("violations", [])
            if isinstance(item, dict)
        ],
        "safe_repairs": proofreader.get("safe_repairs", []),
        "exact_binding": binding,
        "cleanup": cleanup,
        "raw_prompt_scan_passed": True,
        "raw_response_retained": False,
        "chain_of_thought_retained": False,
    }


def run_occupied() -> dict[str, Any]:
    _configure_database()
    controls = (
        _load(AUTHORITY_PATH),
        _load(PREFLIGHT_PATH),
        _load(PROVIDER_FREE_PATH),
        _load(PRE_RESIDUE_PATH),
    )
    if (
        controls[0].get("authority_granted") is not True
        or controls[0].get("continuity_binding")
        != {
            "graph_revision": GRAPH_REVISION,
            "compass_revision": COMPASS_REVISION,
            "compass_source_graph_revision": GRAPH_REVISION,
        }
        or controls[1].get("result")
        != "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
        or not all(controls[1].get("checks", {}).values())
        or controls[2].get("result")
        != "reception_one_default_off_dual_planner_provider_free_pass"
        or controls[3].get("clear") is not True
    ):
        raise OccupiedRouteError("occupied_controls_not_exact")

    password = f"DualPlanner-{secrets.token_urlsafe(24)}!"
    process: subprocess.Popen[bytes] | None = None
    database_created = False
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    value: dict[str, Any] | None = None
    request_sha256: str | None = None
    artifact_dir: Path | None = None
    frame_manifest: dict[str, Any] | None = None
    runtime_audit: dict[str, Any] | None = None
    cleanup: dict[str, Any] | None = None
    failure: OccupiedRouteError | None = None
    try:
        database.create_database()
        database_created = True
        database.create_schema_and_seed(password)
        before = database.database_readback()
        process = _launch_backend(password)
        value, request_sha256 = _make_request(password)
        after = database.database_readback()
        if (
            before.get("counts") != after.get("counts")
            or before.get("sha256") != after.get("sha256")
        ):
            raise OccupiedRouteError("database_truth_changed")
        artifact_dir, frame_manifest = _validate_route_result(value)
        runtime_audit = _validate_runtime_audit(
            artifact_dir,
            int(value["provider_calls"]),
        )
    except OccupiedRouteError as error:
        failure = error
    except Exception as error:
        failure = OccupiedRouteError("occupied_route_unexpected_failure")
        failure.__cause__ = error
    finally:
        _stop_backend(process)
        try:
            _remove_runtime_dir()
        except OccupiedRouteError as error:
            failure = failure or error
        if database_created:
            try:
                cleanup = database.cleanup_database()
            except Exception:
                failure = failure or OccupiedRouteError(
                    "database_cleanup_failed"
                )

    post_residue = _residue_snapshot(phase="post_attempt")
    _write_json(POST_RESIDUE_PATH, post_residue)
    _write_json(
        CLEANUP_PATH,
        {
            "schema_version": (
                "reception.one.default_off_dual_planner.cleanup.v1"
            ),
            "ownership_marker_verified": database_created,
            "database_cleanup": cleanup,
            "backend_process_absent": (
                process is None or process.poll() is not None
            ),
            "runtime_directory_absent": not RUNTIME_DIR.exists(),
            "post_attempt_residue_clear": post_residue["clear"],
        },
    )
    if failure is not None or post_residue["clear"] is not True:
        reason = (
            str(failure).split(":", 1)[0]
            if failure is not None
            else "post_attempt_residue_not_clear"
        )
        _write_json(
            FAILURE_PATH,
            {
                "schema_version": (
                    "reception.one.default_off_dual_planner."
                    "occupied_failure.v1"
                ),
                "result": (
                    "reception_one_default_off_dual_planner_"
                    "occupied_failed_closed"
                ),
                "reason_code": reason,
                "raw_prompt_retained": False,
                "raw_provider_response_retained": False,
                "credential_material_retained": False,
                "post_attempt_residue_clear": post_residue["clear"],
            },
        )
        raise OccupiedRouteError(reason)

    assert value is not None
    assert before is not None
    assert after is not None
    assert request_sha256 is not None
    assert artifact_dir is not None
    assert frame_manifest is not None
    assert runtime_audit is not None
    evidence = {
        "schema_version": (
            "reception.one.default_off_dual_planner.occupied_route.v1"
        ),
        "result": (
            "reception_one_default_off_dual_planner_occupied_route_pass"
        ),
        "recorded_at": _utc_now(),
        "data_class": "authored_synthetic",
        "continuity_binding": {
            "graph_revision": GRAPH_REVISION,
            "compass_revision": COMPASS_REVISION,
            "compass_source_graph_revision": GRAPH_REVISION,
        },
        "request_sha256": request_sha256,
        "request_prompt_retained": False,
        "http_status": 200,
        "route": {
            "operation_id": "composeReceptionOneProductContextProposal",
            "planner_mode": value["planner_mode"],
            "result": value["result"],
            "goal": value["goal"],
            "api_spine_operation_id": value["operation_id"],
            "proposed_duration_minutes": value[
                "proposed_duration_minutes"
            ],
            "provider_calls": value["provider_calls"],
            "runtime_audit_ref": value["runtime_audit_ref"],
            "proofreader_disposition": value["review"]["disposition"],
            "admitted_output_fields": [
                "proposal_family",
                "patient_ref",
                "practitioner_ref",
                "duration_minutes",
                "api_spine_operation_id",
                "requires_human_confirmation",
                "write_performed",
            ],
            "requires_confirmation": value["requires_confirmation"],
            "proposal_only": value["proposal_only"],
            "write_performed": value["write_performed"],
            "confirmation_performed": value["confirmation_performed"],
        },
        "proposal_adapter": {
            "adapter_kind": value["adapter_review"]["adapter_kind"],
            "safe": value["adapter_review"]["safe"],
            "freshness_verified": value["adapter_review"][
                "freshness_verified"
            ],
            "confirmation_evidence_released": value["adapter_review"][
                "confirmation_evidence_released"
            ],
            "write_performed": value["adapter_review"][
                "write_performed"
            ],
        },
        "provider": runtime_audit["exact_binding"],
        "runtime_audit": runtime_audit,
        "frame_audit": {
            "request_sha256": frame_manifest["request_sha256"],
            "context_revision": frame_manifest["context_revision"],
            "raw_frame_retained": False,
            "raw_prompt_retained": False,
        },
        "database": {
            "trusted_backend_reads_performed": True,
            "model_database_access": False,
            "truth_counts_unchanged": (
                before["counts"] == after["counts"]
            ),
            "truth_hashes_unchanged": (
                before["sha256"] == after["sha256"]
            ),
            "appointment_write_performed": False,
            "confirmation_performed": False,
            "database_identifier_retained": False,
        },
        "call_budget": {
            "actual_provider_calls": value["provider_calls"],
            "absolute_call_ceiling": 2,
            "application_cost_ceiling_usd": 1,
            "further_call_after_success": False,
        },
        "explicit_exclusions": {
            "api_key_authentication_used": False,
            "service_account_key_used": False,
            "global_endpoint_used": False,
            "regional_or_provider_fallback_used": False,
            "deterministic_planner_fallback_used": False,
            "provider_tools_used": False,
            "grounding_or_retrieval_used": False,
            "cache_created": False,
            "raw_prompt_retained": False,
            "raw_provider_response_retained": False,
            "chain_of_thought_retained": False,
            "real_or_product_data_used": False,
            "product_delivery_performed": False,
            "appointment_write_or_confirmation_performed": False,
        },
        "cleanup": {
            "database_removed": post_residue[
                "owned_database_present"
            ]
            is False,
            "backend_process_removed": (
                process is None or process.poll() is not None
            ),
            "runtime_directory_removed": not RUNTIME_DIR.exists(),
            "containers_removed": not any(
                post_residue["owned_containers_present"].values()
            ),
            "images_removed": not any(
                post_residue["owned_images_present"].values()
            ),
            "network_removed": (
                post_residue["owned_network_present"] is False
            ),
            "post_attempt_residue_clear": post_residue["clear"],
        },
        "claim_limits": [
            "This proves one authored-synthetic product-route path through the configured Sydney locational endpoint, not Australian physical or sovereign processing.",
            "It does not prove real-data, production, general reliability, appointment-write, deployment or release suitability.",
        ],
    }
    evidence["evidence_hash"] = _canonical_hash(evidence)
    _write_json(OCCUPIED_EVIDENCE_PATH, evidence)
    return evidence


def recover_after_cleanup_race() -> dict[str, Any]:
    """Close the first call without another provider invocation.

    The first occupied dialogue completed and admitted before Windows retained
    the closed backend log handle. Recovery verifies that immutable provider
    audit, replays only the deterministic route/adapter, then removes the
    disposable database and all owned runtime residue.
    """

    _configure_database()
    if OCCUPIED_EVIDENCE_PATH.exists():
        raise OccupiedRouteError("occupied_evidence_already_exists")
    artifact_dirs = sorted(
        path for path in OUTPUT.glob("runtime-*") if path.is_dir()
    )
    if len(artifact_dirs) != 1:
        raise OccupiedRouteError("recovery_audit_directory_not_exact")
    artifact_dir = artifact_dirs[0]
    dialogue = _load(artifact_dir / "occupied-dialogue-evidence.json")
    provider_calls = dialogue.get("actual_provider_call_count")
    release = dialogue.get("release")
    if (
        dialogue.get("result")
        != "reception_one_receptionist_first_v68_runtime_occupied_pass"
        or dialogue.get("terminal_status") != "admitted"
        or provider_calls != 1
        or dialogue.get("no_call_after_admission") is not True
        or not isinstance(release, dict)
        or release.get("proposal_family") != "resize"
        or release.get("duration_minutes") != 45
        or release.get("api_spine_operation_id")
        != "proposeAppointmentUpdate"
        or release.get("requires_human_confirmation") is not True
        or release.get("write_performed") is not False
    ):
        raise OccupiedRouteError("recovery_dialogue_not_admitted")
    runtime_audit = _validate_runtime_audit(
        artifact_dir,
        provider_calls,
    )
    external_audit = _load(
        artifact_dir / "occupied-turn-001-external-audit.json"
    )
    provider_outcome = external_audit.get("provider_outcome")
    if (
        not isinstance(provider_outcome, dict)
        or provider_outcome.get("http_status") != 200
        or provider_outcome.get("status") != "completed"
        or external_audit.get("freshness") != "fresh"
        or external_audit.get("release", {}).get("atomic_release") is not True
        or external_audit.get("retry", {}).get("performed") is not False
    ):
        raise OccupiedRouteError("recovery_external_audit_invalid")
    manifest = _load(artifact_dir / "runtime-frame-manifest.json")
    if (
        (artifact_dir / "runtime-frame.json").exists()
        or manifest.get("raw_frame_retained") is not False
        or manifest.get("raw_prompt_retained") is not False
    ):
        raise OccupiedRouteError("recovery_raw_frame_cleanup_invalid")
    if not _database_exists():
        raise OccupiedRouteError("recovery_database_missing")

    canonical_path = (
        ROOT
        / "orchestration"
        / "continuity"
        / "reception-one-product-context-proposal-runtime"
        / "live-local-browser-backend-postgres-evidence.json"
    )
    canonical = _load(canonical_path).get("database_before")
    before_replay = database.database_readback()
    if (
        not isinstance(canonical, dict)
        or canonical.get("counts") != before_replay.get("counts")
        or canonical.get("sha256") != before_replay.get("sha256")
    ):
        raise OccupiedRouteError("recovery_database_not_canonical")

    password = f"DualPlannerRecovery-{secrets.token_urlsafe(24)}!"
    process: subprocess.Popen[bytes] | None = None
    cleanup: dict[str, Any] | None = None
    replay: dict[str, Any] | None = None
    replay_request_sha256: str | None = None
    after_replay: dict[str, Any] | None = None
    failure: OccupiedRouteError | None = None
    try:
        _remove_runtime_dir()
        database.base.rotate_synthetic_password(password)
        process = _launch_backend(password)
        audit_dirs_before = sorted(
            path.name
            for path in OUTPUT.glob("runtime-*")
            if path.is_dir()
        )
        replay, replay_request_sha256 = _make_request(
            password,
            planner_mode="deterministic",
        )
        _validate_provider_free_replay(replay)
        audit_dirs_after = sorted(
            path.name
            for path in OUTPUT.glob("runtime-*")
            if path.is_dir()
        )
        if audit_dirs_after != audit_dirs_before:
            raise OccupiedRouteError(
                "provider_free_replay_created_provider_audit"
            )
        after_replay = database.database_readback()
        if (
            before_replay["counts"] != after_replay["counts"]
            or before_replay["sha256"] != after_replay["sha256"]
        ):
            raise OccupiedRouteError("recovery_replay_changed_truth")
    except OccupiedRouteError as error:
        failure = error
    except Exception as error:
        failure = OccupiedRouteError("recovery_unexpected_failure")
        failure.__cause__ = error
    finally:
        _stop_backend(process)
        try:
            _remove_runtime_dir()
        except OccupiedRouteError as error:
            failure = failure or error
        try:
            cleanup = database.cleanup_database()
        except Exception:
            failure = failure or OccupiedRouteError(
                "recovery_database_cleanup_failed"
            )

    post_residue = _residue_snapshot(phase="post_attempt")
    _write_json(POST_RESIDUE_PATH, post_residue)
    _write_json(
        CLEANUP_PATH,
        {
            "schema_version": (
                "reception.one.default_off_dual_planner.cleanup.v1"
            ),
            "recovery_kind": "provider_free_cleanup_and_adapter_replay",
            "ownership_marker_verified": True,
            "database_cleanup": cleanup,
            "backend_process_absent": (
                process is None or process.poll() is not None
            ),
            "runtime_directory_absent": not RUNTIME_DIR.exists(),
            "post_attempt_residue_clear": post_residue["clear"],
        },
    )
    if (
        failure is not None
        or post_residue["clear"] is not True
        or replay is None
        or replay_request_sha256 is None
        or after_replay is None
    ):
        reason = (
            str(failure).split(":", 1)[0]
            if failure is not None
            else "recovery_incomplete"
        )
        _write_json(
            FAILURE_PATH,
            {
                "schema_version": (
                    "reception.one.default_off_dual_planner."
                    "occupied_failure.v1"
                ),
                "result": (
                    "reception_one_default_off_dual_planner_"
                    "occupied_recovery_failed_closed"
                ),
                "reason_code": reason,
                "additional_provider_calls": 0,
                "raw_prompt_retained": False,
                "raw_provider_response_retained": False,
                "credential_material_retained": False,
                "post_attempt_residue_clear": post_residue["clear"],
            },
        )
        raise OccupiedRouteError(reason)

    provider_usage = provider_outcome.get("usage")
    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.default_off_dual_planner.occupied_route.v1"
        ),
        "result": (
            "reception_one_default_off_dual_planner_"
            "occupied_model_and_recovered_route_pass"
        ),
        "recorded_at": _utc_now(),
        "data_class": "authored_synthetic",
        "continuity_binding": {
            "graph_revision": GRAPH_REVISION,
            "compass_revision": COMPASS_REVISION,
            "compass_source_graph_revision": GRAPH_REVISION,
        },
        "occupied_attempt": {
            "runtime_audit_ref": artifact_dir.name,
            "provider_http_status": provider_outcome["http_status"],
            "provider_status": provider_outcome["status"],
            "provider_latency_ms": provider_outcome.get("latency_ms"),
            "provider_usage": provider_usage,
            "provider_calls": 1,
            "terminal_status": dialogue["terminal_status"],
            "proofreader_disposition": (
                runtime_audit["proofreader_disposition"]
            ),
            "proofreader_violation_paths": runtime_audit[
                "proofreader_violation_paths"
            ],
            "safe_repairs": runtime_audit["safe_repairs"],
            "proposal_family": release["proposal_family"],
            "api_spine_operation_id": release[
                "api_spine_operation_id"
            ],
            "duration_minutes": release["duration_minutes"],
            "requires_human_confirmation": release[
                "requires_human_confirmation"
            ],
            "write_performed": release["write_performed"],
            "provider_request_hash": external_audit["request_hash"],
            "schema_hash": external_audit["schema_hash"],
            "raw_outer_http_response_retained": False,
            "outer_harness_interruption": (
                "windows_closed_log_handle_cleanup_race"
            ),
        },
        "provider": runtime_audit["exact_binding"],
        "runtime_audit": runtime_audit,
        "frame_audit": {
            "request_sha256": manifest["request_sha256"],
            "context_revision": manifest["context_revision"],
            "raw_frame_retained": False,
            "raw_prompt_retained": False,
        },
        "provider_free_route_recovery": {
            "purpose": (
                "verify_authenticated_http_route_and_existing_"
                "proposal_only_adapter_without_another_provider_call"
            ),
            "request_sha256": replay_request_sha256,
            "http_status": 200,
            "planner_mode": replay["planner_mode"],
            "provider_calls": replay["provider_calls"],
            "result": replay["result"],
            "goal": replay["goal"],
            "api_spine_operation_id": replay["operation_id"],
            "proposed_duration_minutes": replay[
                "proposed_duration_minutes"
            ],
            "adapter_kind": replay["adapter_review"]["adapter_kind"],
            "adapter_safe": replay["adapter_review"]["safe"],
            "freshness_verified": replay["adapter_review"][
                "freshness_verified"
            ],
            "requires_confirmation": replay[
                "requires_confirmation"
            ],
            "proposal_only": replay["proposal_only"],
            "write_performed": replay["write_performed"],
            "confirmation_performed": replay[
                "confirmation_performed"
            ],
            "new_provider_audit_created": False,
        },
        "database": {
            "trusted_backend_reads_performed": True,
            "model_database_access": False,
            "post_occupied_state_matched_prior_canonical_seed": True,
            "provider_free_replay_counts_unchanged": (
                before_replay["counts"] == after_replay["counts"]
            ),
            "provider_free_replay_hashes_unchanged": (
                before_replay["sha256"] == after_replay["sha256"]
            ),
            "appointment_write_performed": False,
            "confirmation_performed": False,
            "database_identifier_retained": False,
        },
        "call_budget": {
            "actual_provider_calls": 1,
            "absolute_call_ceiling": 2,
            "application_cost_ceiling_usd": 1,
            "additional_call_during_recovery": False,
            "further_call_after_admission": False,
        },
        "explicit_exclusions": {
            "api_key_authentication_used": False,
            "service_account_key_used": False,
            "global_endpoint_used": False,
            "regional_or_provider_fallback_used": False,
            "deterministic_planner_fallback_used": False,
            "provider_tools_used": False,
            "grounding_or_retrieval_used": False,
            "cache_created": False,
            "raw_prompt_retained": False,
            "raw_provider_response_retained": False,
            "chain_of_thought_retained": False,
            "real_or_product_data_used": False,
            "product_delivery_performed": False,
            "appointment_write_or_confirmation_performed": False,
        },
        "cleanup": {
            "database_removed": (
                post_residue["owned_database_present"] is False
            ),
            "backend_process_removed": (
                process is None or process.poll() is not None
            ),
            "runtime_directory_removed": not RUNTIME_DIR.exists(),
            "containers_removed": not any(
                post_residue["owned_containers_present"].values()
            ),
            "images_removed": not any(
                post_residue["owned_images_present"].values()
            ),
            "network_removed": (
                post_residue["owned_network_present"] is False
            ),
            "post_attempt_residue_clear": post_residue["clear"],
        },
        "candid_limit": (
            "The occupied model, proofreader, one-use ledger and Sydney "
            "provider response passed. The first harness did not durably "
            "retain its outer HTTP response because Windows held a closed "
            "backend log handle during post-response cleanup. A zero-provider "
            "authenticated replay then proved the same route and proposal-only "
            "adapter. This composed evidence is not a second occupied call."
        ),
        "claim_limits": [
            "This proves one authored-synthetic provider completion through the configured Sydney locational endpoint plus a zero-provider route/adapter recovery, not Australian physical or sovereign processing.",
            "It does not prove real-data, production, general reliability, appointment-write, deployment or release suitability.",
        ],
    }
    evidence["evidence_hash"] = _canonical_hash(evidence)
    _write_json(OCCUPIED_EVIDENCE_PATH, evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("preflight", "occupied", "recover"),
    )
    args = parser.parse_args()
    try:
        evidence = (
            run_pre_attempt_residue()
            if args.command == "preflight"
            else recover_after_cleanup_race()
            if args.command == "recover"
            else run_occupied()
        )
    except OccupiedRouteError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_default_off_dual_planner_"
                        f"{args.command}_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence.get("result", "residue_clear"),
                "provider_calls": evidence.get("route", {}).get(
                    "provider_calls",
                    0,
                ),
                "write_performed": evidence.get("route", {}).get(
                    "write_performed",
                    False,
                ),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
