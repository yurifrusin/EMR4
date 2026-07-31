#!/usr/bin/env python3
"""Run one ledger-bound Reception One Sydney Vertex model-text attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_proofreader_dialogue_v4 as dialogue
from scripts import reception_one_receptionist_first_v6 as receptionist_v6
from scripts import reception_one_receptionist_first_v61 as receptionist_v61
from scripts import reception_one_receptionist_first_v62 as receptionist_v62
from scripts import reception_one_receptionist_first_v63 as receptionist_v63
from scripts import reception_one_receptionist_first_v64 as receptionist_v64
from scripts import reception_one_receptionist_first_v65 as receptionist_v65
from scripts import reception_one_receptionist_first_v66 as receptionist_v66
from scripts import reception_one_receptionist_first_v67 as receptionist_v67
from scripts import reception_one_receptionist_first_v68 as receptionist_v68
from scripts import (
    reception_one_receptionist_first_v68_runtime as receptionist_v68_runtime,
)
from scripts import reception_one_shared_typed_plan_language as shared
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = lane.ARTIFACT_DIR
PREFLIGHT_PATH = ARTIFACT_DIR / "occupied-preflight-evidence.json"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority-request.json"
ITERATIVE_AUTHORITY_PATH = ARTIFACT_DIR / "iterative-retry-authority.json"
GRAPH_PATH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
DOCKERFILE = ARTIFACT_DIR / "LiveDockerfile"
RELAY_SOURCE = ROOT / "scripts" / "ariadne_vertex_sydney_gemini_25_relay.py"
CELL_SOURCE = ROOT / "scripts" / "ariadne_vertex_sydney_gemini_25_cell.py"
BASE_IMAGE = (
    "docker.io/library/python@sha256:"
    "a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322"
)
NETWORK = "reception-one-model-text-vertex-internal"
RELAY_CONTAINER = "reception-one-model-text-vertex-relay"
CELL_CONTAINER = "reception-one-model-text-vertex-cell"
RELAY_IMAGE = "reception-one-model-text-vertex-relay:v1"
CELL_IMAGE = "reception-one-model-text-vertex-cell:v1"
TOKEN_DESTINATION = "/run/secrets/broker_token"
BROKER_ENVIRONMENT_ALLOWLIST = (
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
CREDENTIAL_ENV_NAMES = {
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "OPENAI_API_KEY",
    "CLOUDSDK_CONFIG",
}


class LiveError(RuntimeError):
    """A bounded occupied-lifecycle failure."""


class Docker:
    def __init__(self) -> None:
        executable = shutil.which("docker")
        if executable is None:
            raise LiveError("docker_unavailable")
        self.executable = executable

    def run(
        self,
        arguments: Sequence[str],
        *,
        timeout: int = 180,
        allowed: frozenset[int] = frozenset({0}),
    ) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                [self.executable, *arguments],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise LiveError("docker_command_failed") from error
        if result.returncode not in allowed:
            raise LiveError("docker_command_failed:" + arguments[0])
        return result

    def exists(self, kind: str, reference: str) -> bool:
        return (
            self.run(
                [kind, "inspect", reference],
                allowed=frozenset({0, 1}),
            ).returncode
            == 0
        )

    def inspect(self, kind: str, reference: str) -> dict[str, Any]:
        raw = self.run([kind, "inspect", reference]).stdout
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LiveError("docker_inspect_invalid") from error
        if not isinstance(value, list) or len(value) != 1:
            raise LiveError("docker_inspect_invalid")
        return value[0]


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _safe_broker_environment() -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in BROKER_ENVIRONMENT_ALLOWLIST
        if name in os.environ
    }
    if os.name == "nt" and not {"PATH", "SYSTEMROOT", "TEMP"} <= set(environment):
        raise LiveError("broker_environment_incomplete")
    return environment


def _squeeze_frame() -> dict[str, Any]:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(
        item for item in document["cases"] if item["case_id"] == "novel-squeeze-in"
    )
    return typed_plan.expand_case(document, case)


def _precall_gate(
    *,
    preflight_path: Path = PREFLIGHT_PATH,
    authority_path: Path = AUTHORITY_PATH,
    expected_graph_revision: int = 65,
    expected_compass_revision: int = 52,
) -> dict[str, Any]:
    preflight = lane.load_object(preflight_path)
    authority = lane.load_object(authority_path)
    graph = lane.load_object(GRAPH_PATH)
    compass = lane.load_object(COMPASS_PATH)
    if (
        authority.get("authority_granted") is not True
        or authority.get("decision") != "authorised_by_yuri"
    ):
        raise LiveError("occupied_authority_missing")
    boundary = authority.get("requested_exact_boundary")
    if not isinstance(boundary, dict):
        boundary = authority.get("exact_boundary")
    exact_authority = {
        "provider": "google_cloud_vertex_ai",
        "model": broker.MODEL,
        "project": broker.PROJECT,
        "service_account": broker.SERVICE_ACCOUNT,
        "authentication": "keyless_impersonated_service_account_adc",
        "location": broker.LOCATION,
        "endpoint_hostname": broker.HOSTNAME,
    }
    if not isinstance(boundary, dict) or any(
        boundary.get(key) != value for key, value in exact_authority.items()
    ):
        raise LiveError("occupied_authority_not_exact")
    if (
        boundary.get("api_key_authentication") is True
        or boundary.get("fallback") is True
        or boundary.get("automatic_regional_fallback") is True
        or boundary.get("global_endpoint") is True
        or boundary.get("provider_tools") is True
        or boundary.get("database_access") is True
        or boundary.get("product_delivery") is True
        or boundary.get("appointment_write_authority") is True
    ):
        raise LiveError("occupied_authority_not_exact")
    if (
        preflight.get("result")
        != "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
        or not isinstance(preflight.get("checks"), dict)
        or not all(preflight["checks"].values())
        or preflight.get("project") != "bernie-emr4-dev"
        or preflight.get("service_account") != broker.SERVICE_ACCOUNT
        or preflight.get("authentication")
        != "keyless_impersonated_service_account_adc"
        or preflight.get("location") != broker.LOCATION
        or preflight.get("endpoint_hostname") != broker.HOSTNAME
        or preflight.get("model_id") != broker.MODEL
    ):
        raise LiveError("occupied_preflight_not_exact")
    if (
        graph.get("graph_revision") != expected_graph_revision
        or compass.get("map_revision") != expected_compass_revision
    ):
        raise LiveError("revision_binding_invalid")
    if compass.get("source_graph_revision") != graph.get("graph_revision"):
        raise LiveError("revision_binding_invalid")
    return {
        "authority_sha256": file_hash(authority_path),
        "preflight_sha256": file_hash(preflight_path),
        "continuity_graph_revision": graph["graph_revision"],
        "compass_map_revision": compass["map_revision"],
        "compass_source_graph_revision": compass["source_graph_revision"],
        "all_cloud_controls_passed": True,
    }


def _cell_request(
    frame: dict[str, Any],
    *,
    attempt_id: str = broker.HISTORICAL_ATTEMPT_ID,
    ledger_id: str = broker.HISTORICAL_LEDGER_ID,
    contract_mode: str = "legacy",
    proofreader_feedback: dict[str, Any] | None = None,
    correction_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
    except broker.BrokerError as error:
        raise LiveError(str(error)) from error
    if contract_mode == "legacy":
        if proofreader_feedback is not None or correction_ticket is not None:
            raise LiveError("proofreader_feedback_requires_shared_contract")
        protocol_version = "reception.one.bureau.model-text-cell.v1"
        policy_id = broker.POLICY_ID
        model_input = lane.build_model_input(frame)
    elif contract_mode == "shared-v2":
        if correction_ticket is not None:
            raise LiveError("correction_ticket_requires_dialogue_contract")
        protocol_version = "reception.one.bureau.shared-typed-cell.v2"
        policy_id = broker.SHARED_POLICY_ID
        model_input = shared.build_model_input(
            frame,
            proofreader_feedback=proofreader_feedback,
        )
    elif contract_mode == "structured-v3":
        if proofreader_feedback is not None or correction_ticket is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_structured_contract"
            )
        protocol_version = structured.PROTOCOL_VERSION
        policy_id = broker.STRUCTURED_POLICY_ID
        model_input = structured.build_model_input(frame)
    elif contract_mode == "dialogue-v4":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_dialogue_contract"
            )
        protocol_version = dialogue.PROTOCOL_VERSION
        policy_id = broker.DIALOGUE_POLICY_ID
        model_input = dialogue.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "preprinted-v5":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_preprinted_contract"
            )
        protocol_version = preprinted.PROTOCOL_VERSION
        policy_id = broker.PREPRINTED_POLICY_ID
        model_input = preprinted.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v6":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v6.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V6_POLICY_ID
        model_input = receptionist_v6.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v61":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v61.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V61_POLICY_ID
        model_input = receptionist_v61.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v62":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v62.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V62_POLICY_ID
        model_input = receptionist_v62.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v63":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v63.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V63_POLICY_ID
        model_input = receptionist_v63.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v64":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v64.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V64_POLICY_ID
        model_input = receptionist_v64.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v65":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v65.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V65_POLICY_ID
        model_input = receptionist_v65.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v66":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v66.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V66_POLICY_ID
        model_input = receptionist_v66.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v67":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v67.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V67_POLICY_ID
        model_input = receptionist_v67.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v68-runtime":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v68_runtime.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V68_RUNTIME_POLICY_ID
        model_input = receptionist_v68_runtime.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    elif contract_mode == "receptionist-v68":
        if proofreader_feedback is not None:
            raise LiveError(
                "proofreader_feedback_not_authorised_for_receptionist_contract"
            )
        protocol_version = receptionist_v68.PROTOCOL_VERSION
        policy_id = broker.RECEPTIONIST_V68_POLICY_ID
        model_input = receptionist_v68.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )
    else:
        raise LiveError("contract_mode_invalid")
    return {
        "protocol_version": protocol_version,
        "policy_id": policy_id,
        "attempt_id": attempt_id,
        "ledger_id": ledger_id,
        "model_input": model_input,
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_compact_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(broker.canonical_bytes(value))


def _create_context(
    destination: Path, request_packet: dict[str, Any]
) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    files = {
        "Dockerfile": DOCKERFILE,
        "relay.py": RELAY_SOURCE,
        "cell.py": CELL_SOURCE,
    }
    hashes = {}
    for target_name, source in files.items():
        shutil.copy2(source, destination / target_name)
        hashes[source.relative_to(ROOT).as_posix()] = file_hash(source)
    request_path = destination / "cell-request.json"
    _write_compact_json(request_path, request_packet)
    hashes["generated:cell-request.json"] = file_hash(request_path)
    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual != {"Dockerfile", "relay.py", "cell.py", "cell-request.json"}:
        raise LiveError("build_context_not_exact")
    return hashes


def _create_ledger(path: Path, request_packet: dict[str, Any]) -> None:
    if path.exists():
        raise LiveError("ledger_already_exists")
    _write_json(
        path,
        {
            "schema_version": (
                "reception.one.bureau.model_text_single_use_ledger.v1"
            ),
            "ledger_id": request_packet["ledger_id"],
            "attempt_id": request_packet["attempt_id"],
            "policy_id": request_packet["policy_id"],
            "status": "open",
            "maximum_provider_calls": 1,
            "provider_calls_consumed": 0,
            "fallback_permitted": False,
        },
    )


def _close_open_ledger(path: Path) -> None:
    if not path.is_file():
        return
    ledger = lane.load_object(path)
    if ledger.get("status") != "open":
        return
    if ledger.get("provider_calls_consumed") != 0:
        raise LiveError("open_ledger_call_count_invalid")
    ledger["status"] = "consumed"
    ledger["closure_reason"] = "lifecycle_closed_before_broker_consumption"
    _write_json(path, ledger)


def _validate_audit(path: Path) -> list[dict[str, Any]]:
    try:
        events = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
    except (OSError, json.JSONDecodeError) as error:
        raise LiveError("audit_unreadable") from error
    previous = broker.ZERO_HASH
    for sequence, event in enumerate(events, start=1):
        if (
            not isinstance(event, dict)
            or event.get("sequence") != sequence
            or event.get("previous_hash") != previous
        ):
            raise LiveError("audit_chain_invalid")
        observed_hash = event.get("event_hash")
        without_hash = {key: value for key, value in event.items() if key != "event_hash"}
        if observed_hash != broker.event_hash(without_hash):
            raise LiveError("audit_chain_invalid")
        previous = observed_hash
    if not events:
        raise LiveError("audit_empty")
    return events


def _wait_broker(
    process: subprocess.Popen[bytes], audit_path: Path, timeout: float = 20
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise LiveError("broker_failed_before_ready")
        if audit_path.exists() and audit_path.stat().st_size:
            events = _validate_audit(audit_path)
            if events[0].get("event_type") == "broker_ready":
                return
        time.sleep(0.1)
    raise LiveError("broker_ready_timeout")


def _wait_relay_ready(
    docker: Docker,
    *,
    timeout: float = 15,
) -> None:
    """Prove the one-use relay is listening without consuming its connection."""

    deadline = time.monotonic() + timeout
    probe = (
        "from pathlib import Path; "
        "rows=Path('/proc/net/tcp').read_text().splitlines()[1:]; "
        "assert any("
        "parts[1].endswith(':1F90') and parts[3]=='0A' "
        "for row in rows if (parts:=row.split())"
        ")"
    )
    while time.monotonic() < deadline:
        result = docker.run(
            [
                "exec",
                RELAY_CONTAINER,
                "python",
                "-c",
                probe,
            ],
            timeout=5,
            allowed=frozenset({0, 1}),
        )
        if result.returncode == 0:
            return
        time.sleep(0.1)
    raise LiveError("relay_ready_timeout")


def _safe_local_code(value: object) -> str:
    if (
        isinstance(value, str)
        and len(value) <= 128
        and re.fullmatch(r"[a-z0-9_.:-]+", value)
    ):
        return value
    return "unavailable"


def _write_local_failure_diagnostic(
    path: Path,
    *,
    docker: Docker,
    cell_result: subprocess.CompletedProcess[str],
    cell_packet: dict[str, Any],
    ledger_path: Path,
    audit_path: Path,
) -> None:
    stdout_bytes = cell_result.stdout.encode("utf-8", errors="replace")
    stderr_bytes = cell_result.stderr.encode("utf-8", errors="replace")
    ledger = lane.load_object(ledger_path)
    events = _validate_audit(audit_path)
    relay_result = docker.run(
        ["logs", RELAY_CONTAINER],
        allowed=frozenset({0, 1}),
    )
    relay_log = (relay_result.stdout + relay_result.stderr).encode(
        "utf-8",
        errors="replace",
    )
    relay_failure_class = "unclassified"
    for signature, classification in (
        ("ConnectionRefusedError", "host_connection_refused"),
        ("RemoteDisconnected", "host_remote_disconnected"),
        ("ConnectionResetError", "host_connection_reset"),
        ("TimeoutError", "host_timeout"),
        ("BrokenPipeError", "relay_client_broken_pipe"),
        ("PermissionError", "relay_permission_error"),
    ):
        if signature.encode("utf-8") in relay_log:
            relay_failure_class = classification
            break
    _write_json(
        path,
        {
            "schema_version": (
                "reception.one.bureau.local_failure_diagnostic.v1"
            ),
            "result": "broker_did_not_exit",
            "phase": "cell_relay_broker_exchange",
            "cell_returncode": cell_result.returncode,
            "cell_status_code": _safe_local_code(
                cell_packet.get("status")
            ),
            "cell_reason_code": _safe_local_code(
                cell_packet.get("reason")
            ),
            "cell_stdout_bytes": len(stdout_bytes),
            "cell_stdout_sha256": (
                "sha256:" + hashlib.sha256(stdout_bytes).hexdigest()
            ),
            "cell_stderr_bytes": len(stderr_bytes),
            "cell_stderr_sha256": (
                "sha256:" + hashlib.sha256(stderr_bytes).hexdigest()
            ),
            "relay_failure_class": relay_failure_class,
            "relay_log_bytes": len(relay_log),
            "relay_log_sha256": (
                "sha256:" + hashlib.sha256(relay_log).hexdigest()
            ),
            "ledger_status": ledger.get("status"),
            "provider_calls_consumed": ledger.get(
                "provider_calls_consumed"
            ),
            "audit_event_types": [
                event.get("event_type") for event in events
            ],
            "raw_cell_output_retained": False,
            "raw_cell_error_retained": False,
            "raw_relay_log_retained": False,
        },
    )


def _terminate(process: subprocess.Popen[bytes] | None) -> bool:
    if process is None:
        return True
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    return process.poll() is not None


def _verify_network(value: dict[str, Any]) -> dict[str, Any]:
    selected = {
        "name": value.get("Name"),
        "driver": value.get("Driver"),
        "internal": value.get("Internal"),
        "attachable": value.get("Attachable"),
        "ingress": value.get("Ingress"),
    }
    if selected != {
        "name": NETWORK,
        "driver": "bridge",
        "internal": True,
        "attachable": False,
        "ingress": False,
    }:
        raise LiveError("internal_network_policy_invalid")
    return selected


def _verify_cell(value: dict[str, Any]) -> dict[str, Any]:
    config = value.get("Config", {})
    host = value.get("HostConfig", {})
    networks = (value.get("NetworkSettings") or {}).get("Networks") or {}
    environment_names = {
        item.split("=", 1)[0]
        for item in config.get("Env") or []
        if isinstance(item, str)
    }
    selected = {
        "user": config.get("User"),
        "network_names": sorted(networks),
        "read_only_rootfs": host.get("ReadonlyRootfs"),
        "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "mount_count": len(value.get("Mounts") or []),
        "credential_environment_present": bool(
            environment_names & CREDENTIAL_ENV_NAMES
        ),
        "port_binding_count": len(host.get("PortBindings") or {}),
    }
    expected = {
        "user": "65532:65532",
        "network_names": [NETWORK],
        "read_only_rootfs": True,
        "privileged": False,
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 134217728,
        "memory_swap_bytes": 134217728,
        "nano_cpus": 500000000,
        "pids_limit": 64,
        "mount_count": 0,
        "credential_environment_present": False,
        "port_binding_count": 0,
    }
    if selected != expected:
        raise LiveError("cell_effective_policy_invalid")
    return selected


def _verify_relay(value: dict[str, Any]) -> dict[str, Any]:
    config = value.get("Config", {})
    host = value.get("HostConfig", {})
    networks = (value.get("NetworkSettings") or {}).get("Networks") or {}
    mounts = value.get("Mounts") or []
    internal = networks.get(NETWORK) or {}
    selected = {
        "user": config.get("User"),
        "network_names": sorted(networks),
        "broker_alias_present": "broker" in (internal.get("Aliases") or []),
        "read_only_rootfs": host.get("ReadonlyRootfs"),
        "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "mount_count": len(mounts),
        "token_mount_exact": (
            len(mounts) == 1
            and mounts[0].get("Destination") == TOKEN_DESTINATION
            and mounts[0].get("RW") is False
        ),
        "port_binding_count": len(host.get("PortBindings") or {}),
    }
    expected = {
        "user": "65532:65532",
        "network_names": sorted([NETWORK, "bridge"]),
        "broker_alias_present": True,
        "read_only_rootfs": True,
        "privileged": False,
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 67108864,
        "memory_swap_bytes": 67108864,
        "nano_cpus": 250000000,
        "pids_limit": 32,
        "mount_count": 1,
        "token_mount_exact": True,
        "port_binding_count": 0,
    }
    if selected != expected:
        raise LiveError("relay_effective_policy_invalid")
    return selected


def run_live(
    *,
    evidence_path: Path,
    ledger_path: Path,
    audit_path: Path,
    attempt_id: str = broker.HISTORICAL_ATTEMPT_ID,
    ledger_id: str = broker.HISTORICAL_LEDGER_ID,
    preflight_path: Path = PREFLIGHT_PATH,
    authority_path: Path = AUTHORITY_PATH,
    expected_graph_revision: int = 65,
    expected_compass_revision: int = 52,
    frame_path: Path | None = None,
    contract_mode: str = "legacy",
    proofreader_feedback_path: Path | None = None,
    correction_ticket_path: Path | None = None,
) -> dict[str, Any]:
    if evidence_path.exists() or ledger_path.exists() or audit_path.exists():
        raise LiveError("occupied_output_already_exists")
    gate = _precall_gate(
        preflight_path=preflight_path,
        authority_path=authority_path,
        expected_graph_revision=expected_graph_revision,
        expected_compass_revision=expected_compass_revision,
    )
    docker = Docker()
    names = {
        "cell": docker.exists("container", CELL_CONTAINER),
        "relay": docker.exists("container", RELAY_CONTAINER),
        "network": docker.exists("network", NETWORK),
        "cell_image": docker.exists("image", CELL_IMAGE),
        "relay_image": docker.exists("image", RELAY_IMAGE),
    }
    if any(names.values()):
        raise LiveError("task_scoped_runtime_name_collision")
    base_preexisting = docker.exists("image", BASE_IMAGE)

    frame = (
        lane.load_object(frame_path)
        if frame_path is not None
        else _squeeze_frame()
    )
    typed_plan.validate_schema(frame, "input")
    proofreader_feedback = (
        lane.load_object(proofreader_feedback_path)
        if proofreader_feedback_path is not None
        else None
    )
    correction_ticket = (
        lane.load_object(correction_ticket_path)
        if correction_ticket_path is not None
        else None
    )
    request_packet = _cell_request(
        frame,
        attempt_id=attempt_id,
        ledger_id=ledger_id,
        contract_mode=contract_mode,
        proofreader_feedback=proofreader_feedback,
        correction_ticket=correction_ticket,
    )
    temporary_root = Path(tempfile.mkdtemp(prefix="reception-one-vertex-"))
    context = temporary_root / "context"
    token_path = temporary_root / "broker-token"
    frame_path = temporary_root / "input-frame.json"
    request_path = temporary_root / "cell-request.json"
    process: subprocess.Popen[bytes] | None = None
    flags = {
        "network": False,
        "relay": False,
        "cell": False,
        "relay_image": False,
        "cell_image": False,
        "ledger": False,
    }
    cleanup_errors: list[str] = []
    lifecycle: dict[str, Any] | None = None
    try:
        context_hashes = _create_context(context, request_packet)
        token_path.write_text(secrets.token_urlsafe(48), encoding="utf-8")
        _write_json(frame_path, frame)
        _write_json(request_path, request_packet)
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        _create_ledger(ledger_path, request_packet)
        flags["ledger"] = True

        docker.run(
            [
                "build",
                "--pull=false",
                "--network",
                "none",
                "--target",
                "relay",
                "--tag",
                RELAY_IMAGE,
                str(context),
            ],
            timeout=300,
        )
        flags["relay_image"] = True
        docker.run(
            [
                "build",
                "--pull=false",
                "--network",
                "none",
                "--target",
                "work-cell",
                "--tag",
                CELL_IMAGE,
                str(context),
            ],
            timeout=300,
        )
        flags["cell_image"] = True

        port = _free_port()
        creation_flags = (
            subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
            if os.name == "nt"
            else 0
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "scripts.reception_one_bureau_model_text_lane_broker",
                "--listen-port",
                str(port),
                "--token-file",
                str(token_path),
                "--ledger",
                str(ledger_path),
                "--audit",
                str(audit_path),
                "--profile",
                str(lane.PROFILE_PATH),
                "--request",
                str(request_path),
                "--frame",
                str(frame_path),
            ],
            cwd=ROOT,
            env=_safe_broker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            creationflags=creation_flags,
        )
        _wait_broker(process, audit_path)

        docker.run(["network", "create", "--internal", NETWORK])
        flags["network"] = True
        network_policy = _verify_network(docker.inspect("network", NETWORK))
        docker.run(
            [
                "create",
                "--name",
                RELAY_CONTAINER,
                "--network",
                "bridge",
                "--read-only",
                "--user",
                "65532:65532",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=8m",
                "--memory",
                "64m",
                "--memory-swap",
                "64m",
                "--cpus",
                "0.25",
                "--pids-limit",
                "32",
                "--ulimit",
                "nofile=64:64",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges=true",
                "--mount",
                (
                    f"type=bind,src={token_path},"
                    f"dst={TOKEN_DESTINATION},readonly"
                ),
                "--env",
                f"BROKER_HOST_PORT={port}",
                RELAY_IMAGE,
            ]
        )
        flags["relay"] = True
        docker.run(
            [
                "network",
                "connect",
                "--alias",
                "broker",
                NETWORK,
                RELAY_CONTAINER,
            ]
        )
        relay_policy = _verify_relay(
            docker.inspect("container", RELAY_CONTAINER)
        )
        docker.run(["start", RELAY_CONTAINER])
        _wait_relay_ready(docker)

        docker.run(
            [
                "create",
                "--name",
                CELL_CONTAINER,
                "--hostname",
                "reception-one-model-cell",
                "--network",
                NETWORK,
                "--read-only",
                "--user",
                "65532:65532",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=8m",
                "--memory",
                "128m",
                "--memory-swap",
                "128m",
                "--cpus",
                "0.50",
                "--pids-limit",
                "64",
                "--ulimit",
                "nofile=64:64",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges=true",
                CELL_IMAGE,
            ]
        )
        flags["cell"] = True
        cell_policy = _verify_cell(docker.inspect("container", CELL_CONTAINER))
        cell_result = docker.run(
            ["start", "--attach", CELL_CONTAINER],
            timeout=90,
            allowed=frozenset({0, 1, 2}),
        )
        try:
            cell_packet = json.loads(cell_result.stdout)
        except json.JSONDecodeError:
            cell_packet = {
                "status": "edge_aborted",
                "reason": "cell_output_not_json",
            }
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired as error:
            _write_local_failure_diagnostic(
                audit_path.with_name(
                    audit_path.stem + "-local-failure.json"
                ),
                docker=docker,
                cell_result=cell_result,
                cell_packet=cell_packet,
                ledger_path=ledger_path,
                audit_path=audit_path,
            )
            raise LiveError("broker_did_not_exit") from error

        events = _validate_audit(audit_path)
        ledger = lane.load_object(ledger_path)
        event_types = [event["event_type"] for event in events]
        if (
            ledger.get("status") != "consumed"
            or ledger.get("provider_calls_consumed") != 1
            or event_types.count("provider_call_started") != 1
        ):
            raise LiveError("occupied_ledger_or_call_count_invalid")
        if contract_mode in {
            "shared-v2",
            "structured-v3",
            "dialogue-v4",
            "preprinted-v5",
            "receptionist-v6",
            "receptionist-v61",
            "receptionist-v62",
            "receptionist-v63",
            "receptionist-v64",
            "receptionist-v65",
            "receptionist-v66",
            "receptionist-v67",
            "receptionist-v68",
            "receptionist-v68-runtime",
        }:
            required_success_events = {
                "provider_call_completed": 1,
                "operator_note_evaluated": 1,
                "proofreader_completed": 1,
                "release_committed": 1,
            }
            if contract_mode in {
                "receptionist-v6",
                "receptionist-v61",
                "receptionist-v62",
                "receptionist-v63",
                "receptionist-v64",
                "receptionist-v65",
                "receptionist-v66",
                "receptionist-v67",
                "receptionist-v68",
                "receptionist-v68-runtime",
            }:
                required_success_events[
                    "receptionist_response_evaluated"
                ] = 1
        else:
            required_success_events = {
                "provider_call_completed": 1,
                "proofreader_completed": 1,
                "release_committed": 1,
            }
        success = (
            cell_result.returncode == 0
            and process.returncode == 0
            and cell_packet.get("status") == "completed"
            and all(
                event_types.count(event_type) == expected_count
                for event_type, expected_count in required_success_events.items()
            )
        )
        note_event = next(
            (
                event
                for event in events
                if event.get("event_type") == "operator_note_evaluated"
            ),
            None,
        )
        proof_event = next(
            (
                event
                for event in events
                if event.get("event_type") == "proofreader_completed"
            ),
            None,
        )
        ticket_event = next(
            (
                event
                for event in events
                if event.get("event_type") == "correction_ticket_issued"
            ),
            None,
        )
        receptionist_event = next(
            (
                event
                for event in events
                if event.get("event_type")
                == "receptionist_response_evaluated"
            ),
            None,
        )
        schema = (
            receptionist_v68_runtime.vertex_response_schema()
            if contract_mode == "receptionist-v68-runtime"
            else receptionist_v68.vertex_response_schema()
            if contract_mode == "receptionist-v68"
            else receptionist_v67.vertex_response_schema()
            if contract_mode == "receptionist-v67"
            else receptionist_v66.vertex_response_schema()
            if contract_mode == "receptionist-v66"
            else receptionist_v65.vertex_response_schema()
            if contract_mode == "receptionist-v65"
            else receptionist_v64.vertex_response_schema()
            if contract_mode == "receptionist-v64"
            else receptionist_v63.vertex_response_schema()
            if contract_mode == "receptionist-v63"
            else receptionist_v62.vertex_response_schema()
            if contract_mode == "receptionist-v62"
            else receptionist_v61.vertex_response_schema()
            if contract_mode == "receptionist-v61"
            else receptionist_v6.vertex_response_schema()
            if contract_mode == "receptionist-v6"
            else preprinted.vertex_response_schema()
            if contract_mode == "preprinted-v5"
            else dialogue.vertex_response_schema()
            if contract_mode == "dialogue-v4"
            else structured.vertex_response_schema()
            if contract_mode == "structured-v3"
            else shared.vertex_response_schema()
            if contract_mode == "shared-v2"
            else lane.vertex_response_schema()
        )
        lifecycle = {
            "schema_version": (
                "reception.one.receptionist_first_v68_runtime.turn_evidence.v1"
                if contract_mode == "receptionist-v68-runtime"
                else "reception.one.receptionist_first_v68.turn_evidence.v1"
                if contract_mode == "receptionist-v68"
                else "reception.one.receptionist_first_v67.turn_evidence.v1"
                if contract_mode == "receptionist-v67"
                else "reception.one.receptionist_first_v66.turn_evidence.v1"
                if contract_mode == "receptionist-v66"
                else "reception.one.receptionist_first_v65.turn_evidence.v1"
                if contract_mode == "receptionist-v65"
                else "reception.one.receptionist_first_v64.turn_evidence.v1"
                if contract_mode == "receptionist-v64"
                else "reception.one.receptionist_first_v63.turn_evidence.v1"
                if contract_mode == "receptionist-v63"
                else "reception.one.receptionist_first_v62.turn_evidence.v1"
                if contract_mode == "receptionist-v62"
                else "reception.one.receptionist_first_v61.turn_evidence.v1"
                if contract_mode == "receptionist-v61"
                else "reception.one.receptionist_first_v6.turn_evidence.v1"
                if contract_mode == "receptionist-v6"
                else "reception.one.preprinted_form_v5.turn_evidence.v1"
                if contract_mode == "preprinted-v5"
                else "reception.one.proofreader_dialogue_v4.turn_evidence.v1"
                if contract_mode == "dialogue-v4"
                else "reception.one.structured_source_occupied_evidence.v1"
                if contract_mode == "structured-v3"
                else "reception.one.shared_typed_occupied_evidence.v1"
                if contract_mode == "shared-v2"
                else "reception.one.bureau.model_text_occupied_evidence.v1"
            ),
            "result": (
                "reception_one_receptionist_first_v68_runtime_turn_pass"
                if success and contract_mode == "receptionist-v68-runtime"
                else "reception_one_receptionist_first_v68_turn_pass"
                if success and contract_mode == "receptionist-v68"
                else "reception_one_receptionist_first_v67_turn_pass"
                if success and contract_mode == "receptionist-v67"
                else "reception_one_receptionist_first_v66_turn_pass"
                if success and contract_mode == "receptionist-v66"
                else "reception_one_receptionist_first_v65_turn_pass"
                if success and contract_mode == "receptionist-v65"
                else "reception_one_receptionist_first_v64_turn_pass"
                if success and contract_mode == "receptionist-v64"
                else "reception_one_receptionist_first_v63_turn_pass"
                if success and contract_mode == "receptionist-v63"
                else "reception_one_receptionist_first_v62_turn_pass"
                if success and contract_mode == "receptionist-v62"
                else "reception_one_receptionist_first_v61_turn_pass"
                if success and contract_mode == "receptionist-v61"
                else "reception_one_receptionist_first_v6_turn_pass"
                if success and contract_mode == "receptionist-v6"
                else "reception_one_preprinted_form_v5_turn_pass"
                if success and contract_mode == "preprinted-v5"
                else "reception_one_proofreader_dialogue_v4_turn_pass"
                if success and contract_mode == "dialogue-v4"
                else "reception_one_structured_source_language_occupied_pass"
                if success and contract_mode == "structured-v3"
                else "reception_one_shared_typed_language_occupied_pass"
                if success and contract_mode == "shared-v2"
                else "reception_one_bureau_model_text_lane_occupied_pass"
                if success
                else (
                    "reception_one_receptionist_first_v68_turn_"
                    "revision_required"
                )
                if contract_mode in {
                    "receptionist-v68",
                    "receptionist-v68-runtime",
                }
                else (
                    "reception_one_receptionist_first_v67_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v67"
                else (
                    "reception_one_receptionist_first_v66_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v66"
                else (
                    "reception_one_receptionist_first_v65_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v65"
                else (
                    "reception_one_receptionist_first_v64_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v64"
                else (
                    "reception_one_receptionist_first_v63_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v63"
                else (
                    "reception_one_receptionist_first_v62_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v62"
                else (
                    "reception_one_receptionist_first_v61_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v61"
                else (
                    "reception_one_receptionist_first_v6_turn_"
                    "revision_required"
                )
                if contract_mode == "receptionist-v6"
                else (
                    "reception_one_preprinted_form_v5_turn_"
                    "revision_required"
                )
                if contract_mode == "preprinted-v5"
                else (
                    "reception_one_proofreader_dialogue_v4_turn_"
                    "revision_required"
                )
                if contract_mode == "dialogue-v4"
                else (
                    "reception_one_structured_source_language_"
                    "occupied_revision_required"
                )
                if contract_mode == "structured-v3"
                else "reception_one_shared_typed_language_occupied_revision_required"
                if contract_mode == "shared-v2"
                else "reception_one_bureau_model_text_lane_occupied_revision_required"
            ),
            "attempt_id": request_packet["attempt_id"],
            "ledger_id": request_packet["ledger_id"],
            "provider_contacted": True,
            "provider_call_count": 1,
            "fallback_performed": False,
            "precall_gate": gate,
            "exact_binding": {
                "provider": "google_vertex_ai",
                "model_id": broker.MODEL,
                "project": broker.PROJECT,
                "service_account": broker.SERVICE_ACCOUNT,
                "authentication": "keyless_impersonated_service_account_adc",
                "location": broker.LOCATION,
                "endpoint_hostname": broker.HOSTNAME,
                "api_key_authentication_used": False,
            },
            "build_context": {
                "repository_root_used": False,
                "temporary_exact_allowlist": True,
                "source_hashes": context_hashes,
            },
            "network": network_policy,
            "cell_effective_policy": cell_policy,
            "relay_effective_policy": relay_policy,
            "broker": {
                "host_purpose_built_one_use_process": True,
                "environment_forwarded_names": list(
                    BROKER_ENVIRONMENT_ALLOWLIST
                ),
                "api_key_authentication_used": False,
                "google_application_credentials_forwarded": False,
                "process_exit_code": process.returncode,
            },
            "exchange": {
                "contract_mode": contract_mode,
                "cell_exit_code": cell_result.returncode,
                "cell_status": cell_packet.get("status"),
                "model_input_hash": lane.canonical_hash(
                    request_packet["model_input"]
                ),
                "proofreader_feedback_hash": (
                    lane.canonical_hash(proofreader_feedback)
                    if proofreader_feedback is not None
                    else None
                ),
                "correction_ticket_hash": (
                    lane.canonical_hash(correction_ticket)
                    if correction_ticket is not None
                    else None
                ),
                "schema_hash": lane.canonical_hash(
                    schema
                ),
                "audit_event_count": len(events),
                "audit_event_types": event_types,
                "audit_hash_chain_valid": True,
                "audit_terminal_hash": events[-1]["event_hash"],
                "release": (
                    cell_packet.get("release")
                    if cell_packet.get("status") == "completed"
                    else None
                ),
                "proofreader": (
                    cell_packet.get("proofreader")
                    if cell_packet.get("status") == "completed"
                    else proof_event["fields"]
                    if proof_event
                    else None
                ),
                "correction_ticket": (
                    ticket_event["fields"]["ticket"]
                    if ticket_event
                    else None
                ),
                "correction_ticket_hash": (
                    ticket_event["fields"]["ticket_hash"]
                    if ticket_event
                    else None
                ),
                "operator_note": (
                    {
                        key: note_event["fields"].get(key)
                        for key in (
                            "disposition",
                            "reason_codes",
                            "note_sha256",
                            "retained_utf8_bytes",
                            "audit_only",
                            "parsed_into_plan",
                            "product_delivered",
                        )
                    }
                    if note_event
                    else None
                ),
                "receptionist_output": (
                    {
                        key: receptionist_event["fields"].get(key)
                        for key in (
                            "disposition",
                            "violations",
                            "receptionist_response",
                            "decision_note",
                            "evidence_utterance_indices",
                            "natural_response_parsed_into_form",
                            "product_delivered",
                        )
                    }
                    if receptionist_event
                    else None
                ),
            },
            "ledger": ledger,
            "explicit_exclusions": {
                "raw_prompt_recorded": False,
                "raw_provider_response_recorded": False,
                "credential_or_token_recorded": False,
                "api_key_information_recorded": False,
                "chain_of_thought_recorded": False,
                "thought_summary_requested": False,
                "thinking_token_count_only": (
                    contract_mode
                    in {
                        "receptionist-v6",
                        "receptionist-v61",
                        "receptionist-v62",
                        "receptionist-v63",
                        "receptionist-v64",
                        "receptionist-v65",
                        "receptionist-v66",
                        "receptionist-v67",
                        "receptionist-v68",
                        "receptionist-v68-runtime",
                    }
                ),
                "operator_note_parsed_into_plan": False,
                "operator_note_product_delivered": False,
                "product_or_database_access": False,
                "command_authority": False,
                "human_or_product_delivery": False,
            },
        }
    finally:
        broker_absent = _terminate(process)
        if flags["ledger"]:
            try:
                _close_open_ledger(ledger_path)
            except (OSError, LiveError, json.JSONDecodeError):
                cleanup_errors.append("ledger_close_failed")
        for enabled, arguments, name in (
            (flags["cell"], ["rm", "--force", CELL_CONTAINER], "cell"),
            (flags["relay"], ["rm", "--force", RELAY_CONTAINER], "relay"),
            (flags["network"], ["network", "rm", NETWORK], "network"),
            (
                flags["cell_image"],
                ["image", "rm", CELL_IMAGE],
                "cell_image",
            ),
            (
                flags["relay_image"],
                ["image", "rm", RELAY_IMAGE],
                "relay_image",
            ),
        ):
            if enabled:
                try:
                    docker.run(arguments, allowed=frozenset({0, 1}))
                except LiveError:
                    cleanup_errors.append(name + "_cleanup_failed")
        if not base_preexisting and docker.exists("image", BASE_IMAGE):
            try:
                docker.run(["image", "rm", BASE_IMAGE], allowed=frozenset({0, 1}))
            except LiveError:
                cleanup_errors.append("base_image_cleanup_failed")
        try:
            shutil.rmtree(temporary_root)
        except OSError:
            cleanup_errors.append("temporary_root_cleanup_failed")

    residue = {
        "cell_container_absent": not docker.exists("container", CELL_CONTAINER),
        "relay_container_absent": not docker.exists(
            "container", RELAY_CONTAINER
        ),
        "internal_network_absent": not docker.exists("network", NETWORK),
        "cell_image_absent": not docker.exists("image", CELL_IMAGE),
        "relay_image_absent": not docker.exists("image", RELAY_IMAGE),
        "base_image_state_preserved": (
            docker.exists("image", BASE_IMAGE)
            if base_preexisting
            else not docker.exists("image", BASE_IMAGE)
        ),
        "temporary_token_absent": not token_path.exists(),
        "temporary_context_absent": not temporary_root.exists(),
        "broker_process_absent": broker_absent,
        "daemon_wide_prune_performed": False,
    }
    if lifecycle is None:
        raise LiveError("occupied_evidence_missing")
    if cleanup_errors or not all(
        value
        for key, value in residue.items()
        if key != "daemon_wide_prune_performed"
    ):
        raise LiveError("task_scoped_cleanup_failed")
    lifecycle["cleanup"] = residue
    lifecycle["evidence_hash"] = lane.canonical_hash(lifecycle)
    _write_json(evidence_path, lifecycle)
    return lifecycle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--ledger-id", required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--graph-revision", type=int, required=True)
    parser.add_argument("--compass-revision", type=int, required=True)
    parser.add_argument("--frame", type=Path)
    parser.add_argument("--proofreader-feedback", type=Path)
    parser.add_argument("--correction-ticket", type=Path)
    parser.add_argument(
        "--contract-mode",
        choices=(
            "legacy",
            "shared-v2",
            "structured-v3",
            "dialogue-v4",
            "preprinted-v5",
            "receptionist-v6",
            "receptionist-v61",
            "receptionist-v62",
            "receptionist-v63",
            "receptionist-v64",
            "receptionist-v65",
            "receptionist-v66",
            "receptionist-v67",
            "receptionist-v68",
            "receptionist-v68-runtime",
        ),
        default="legacy",
    )
    args = parser.parse_args()
    try:
        evidence = run_live(
            evidence_path=args.evidence,
            ledger_path=args.ledger,
            audit_path=args.audit,
            attempt_id=args.attempt_id,
            ledger_id=args.ledger_id,
            preflight_path=args.preflight,
            authority_path=args.authority,
            expected_graph_revision=args.graph_revision,
            expected_compass_revision=args.compass_revision,
            frame_path=args.frame,
            contract_mode=args.contract_mode,
            proofreader_feedback_path=args.proofreader_feedback,
            correction_ticket_path=args.correction_ticket,
        )
    except LiveError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_bureau_model_text_lane_occupied_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_call_count": evidence["provider_call_count"],
                "proofreader_disposition": (
                    (evidence["exchange"].get("proofreader") or {}).get(
                        "disposition"
                    )
                ),
                "cleanup_passed": all(
                    value
                    for key, value in evidence["cleanup"].items()
                    if key != "daemon_wide_prune_performed"
                ),
            },
            sort_keys=True,
        )
    )
    return (
        0
        if evidence["result"]
        in {
            "reception_one_bureau_model_text_lane_occupied_pass",
            "reception_one_shared_typed_language_occupied_pass",
            "reception_one_structured_source_language_occupied_pass",
            "reception_one_proofreader_dialogue_v4_turn_pass",
            "reception_one_preprinted_form_v5_turn_pass",
            "reception_one_receptionist_first_v6_turn_pass",
        }
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
