#!/usr/bin/env python3
"""Run the bounded Gemini 2.5 Flash Sydney isolation lifecycle.

The dry-run mode is provider-free. The live mode is available only after the
separate pre-attempt gates have passed. Both modes use the same disposable
cell, exact-path relay, one-use broker and deterministic proofreader path.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts
from scripts import ariadne_vertex_sydney_gemini_25_launcher as launcher


SCHEMA_VERSION = "ariadne.vertex_sydney_isolation_rehearsal_evidence.v1"
DRY_RESULT = "ariadne_vertex_sydney_gemini_25_real_isolation_dry_run_pass"
LIVE_PASS = "ariadne_vertex_sydney_gemini_25_occupied_rehearsal_pass"
LIVE_FAILED = "ariadne_vertex_sydney_gemini_25_occupied_rehearsal_revision_required"
BASE_IMAGE = (
    "docker.io/library/python@sha256:"
    "a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322"
)
TOKEN_DESTINATION = "/run/secrets/broker_token"
BROKER_MODULE = "scripts.ariadne_vertex_sydney_gemini_25_broker"
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
CELL_CREDENTIAL_ENVIRONMENT_NAMES = {
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "OPENAI_API_KEY",
}


class RehearsalError(RuntimeError):
    """A bounded lifecycle failure with no secret-bearing diagnostic."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class Docker:
    """Run exact Docker argument arrays without a shell."""

    def __init__(self) -> None:
        executable = shutil.which("docker")
        if executable is None:
            raise RehearsalError("docker_unavailable")
        self.executable = executable

    def run(
        self,
        arguments: Sequence[str],
        *,
        timeout: int = 120,
        allowed_returncodes: frozenset[int] = frozenset({0}),
    ) -> CommandResult:
        try:
            completed = subprocess.run(
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
            raise RehearsalError("docker_command_failed") from error
        result = CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if result.returncode not in allowed_returncodes:
            operation = arguments[0] if arguments else "unknown"
            target = "unspecified"
            if "--name" in arguments:
                name_index = arguments.index("--name")
                if name_index + 1 < len(arguments):
                    target = arguments[name_index + 1]
            elif operation in {"start", "rm"} and len(arguments) > 1:
                target = arguments[-1]
            raise RehearsalError(
                f"docker_command_failed:{operation}:{target}"
            )
        return result

    def inspect(self, kind: str, reference: str) -> dict[str, Any]:
        result = self.run([kind, "inspect", reference])
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise RehearsalError("docker_inspect_not_json") from error
        if (
            not isinstance(value, list)
            or len(value) != 1
            or not isinstance(value[0], dict)
        ):
            raise RehearsalError("docker_inspect_shape_invalid")
        return value[0]

    def exists(self, kind: str, reference: str) -> bool:
        return (
            self.run(
                [kind, "inspect", reference],
                allowed_returncodes=frozenset({0, 1}),
            ).returncode
            == 0
        )


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _without_docker(command: Sequence[str]) -> list[str]:
    if not command or command[0] != "docker":
        raise RehearsalError("launch_command_invalid")
    return list(command[1:])


def _replace_placeholders(
    command: Sequence[str],
    *,
    context: Path | None = None,
    token: Path | None = None,
    port: int | None = None,
) -> list[str]:
    replaced: list[str] = []
    for item in _without_docker(command):
        current = item
        if context is not None:
            current = current.replace("<temporary_exact_context>", str(context))
        if token is not None:
            current = current.replace("<ephemeral_broker_token>", str(token))
        if port is not None:
            current = current.replace("<ephemeral_port>", str(port))
        if "<" in current or ">" in current:
            raise RehearsalError("launch_placeholder_unresolved")
        replaced.append(current)
    return replaced


def create_exact_context(plan: dict[str, Any], destination: Path) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    hashes: dict[str, str] = {}
    expected_targets: set[str] = set()
    for item in plan["build_context"]["files"]:
        source_relative = item["source"]
        target_relative = item["target"]
        source = ROOT / source_relative
        target = destination / target_relative
        if (
            not source.is_file()
            or Path(target_relative).is_absolute()
            or ".." in Path(target_relative).parts
        ):
            raise RehearsalError("build_context_source_invalid")
        shutil.copy2(source, target)
        if target.is_symlink() or target.read_bytes() != source.read_bytes():
            raise RehearsalError("build_context_copy_invalid")
        hashes[source_relative] = file_hash(source)
        expected_targets.add(target_relative)
    actual_targets = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual_targets != expected_targets:
        raise RehearsalError("build_context_file_set_invalid")
    return hashes


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
    required = {"PATH", "SYSTEMROOT", "TEMP"}
    if os.name == "nt" and not required <= set(environment):
        raise RehearsalError("broker_environment_incomplete")
    return environment


def _wait_for_broker(
    process: subprocess.Popen[bytes], audit_path: Path, timeout: float = 20.0
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RehearsalError("broker_failed_before_ready")
        if audit_path.is_file() and audit_path.stat().st_size > 0:
            try:
                first = json.loads(
                    audit_path.read_text(encoding="utf-8").splitlines()[0]
                )
            except (OSError, json.JSONDecodeError, IndexError) as error:
                raise RehearsalError("broker_ready_audit_invalid") from error
            if first.get("event_type") == "broker_ready":
                return
        time.sleep(0.1)
    raise RehearsalError("broker_ready_timeout")


def _read_audit(path: Path) -> list[dict[str, Any]]:
    try:
        events = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
    except (OSError, json.JSONDecodeError) as error:
        raise RehearsalError("audit_unreadable") from error
    if not events or not all(isinstance(event, dict) for event in events):
        raise RehearsalError("audit_shape_invalid")
    if not contracts.validate_audit_chain(events):
        raise RehearsalError("audit_hash_chain_invalid")
    return events


def _state_summary(container: dict[str, Any]) -> dict[str, Any]:
    state = container.get("State")
    if not isinstance(state, dict):
        raise RehearsalError("container_state_missing")
    return {
        "status": state.get("Status"),
        "running": state.get("Running"),
        "oom_killed": state.get("OOMKilled"),
        "dead": state.get("Dead"),
        "exit_code": state.get("ExitCode"),
        "error_empty": state.get("Error") == "",
    }


def _ulimit_exact(host: dict[str, Any]) -> bool:
    return host.get("Ulimits") == [{"Name": "nofile", "Hard": 64, "Soft": 64}]


def verify_cell(container: dict[str, Any]) -> dict[str, Any]:
    config = container.get("Config")
    host = container.get("HostConfig")
    networks = (container.get("NetworkSettings") or {}).get("Networks")
    if (
        not isinstance(config, dict)
        or not isinstance(host, dict)
        or not isinstance(networks, dict)
    ):
        raise RehearsalError("cell_inspect_missing")
    environment_names = {
        item.split("=", 1)[0]
        for item in config.get("Env") or []
        if isinstance(item, str)
    }
    if environment_names & CELL_CREDENTIAL_ENVIRONMENT_NAMES:
        raise RehearsalError("cell_credential_environment_invalid")
    selected = {
        "user": config.get("User"),
        "hostname": config.get("Hostname"),
        "network_names": sorted(networks),
        "read_only_rootfs": host.get("ReadonlyRootfs"),
        "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [],
        "cap_add": host.get("CapAdd") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "nofile_exact": _ulimit_exact(host),
        "mount_count": len(container.get("Mounts") or []),
        "tmpfs": host.get("Tmpfs") or {},
        "port_binding_count": len(host.get("PortBindings") or {}),
        "publish_all_ports": host.get("PublishAllPorts"),
    }
    expected = {
        "user": "65532:65532",
        "hostname": "ariadne-vertex-cell",
        "network_names": [launcher.NETWORK],
        "read_only_rootfs": True,
        "privileged": False,
        "cap_drop": ["ALL"],
        "cap_add": [],
        "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 134217728,
        "memory_swap_bytes": 134217728,
        "nano_cpus": 500000000,
        "pids_limit": 64,
        "nofile_exact": True,
        "mount_count": 0,
        "tmpfs": {"/tmp": "rw,noexec,nosuid,size=8m"},
        "port_binding_count": 0,
        "publish_all_ports": False,
    }
    if selected != expected:
        raise RehearsalError("cell_effective_policy_invalid")
    return selected


def verify_relay(container: dict[str, Any]) -> dict[str, Any]:
    config = container.get("Config")
    host = container.get("HostConfig")
    networks = (container.get("NetworkSettings") or {}).get("Networks")
    mounts = container.get("Mounts") or []
    if (
        not isinstance(config, dict)
        or not isinstance(host, dict)
        or not isinstance(networks, dict)
    ):
        raise RehearsalError("relay_inspect_missing")
    internal = networks.get(launcher.NETWORK)
    aliases = internal.get("Aliases") if isinstance(internal, dict) else []
    selected = {
        "user": config.get("User"),
        "network_names": sorted(networks),
        "broker_alias_present": "broker" in (aliases or []),
        "read_only_rootfs": host.get("ReadonlyRootfs"),
        "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [],
        "cap_add": host.get("CapAdd") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "nofile_exact": _ulimit_exact(host),
        "mount_count": len(mounts),
        "token_mount_destination_exact": (
            len(mounts) == 1
            and mounts[0].get("Destination") == TOKEN_DESTINATION
            and mounts[0].get("RW") is False
        ),
        "tmpfs": host.get("Tmpfs") or {},
        "port_binding_count": len(host.get("PortBindings") or {}),
        "publish_all_ports": host.get("PublishAllPorts"),
    }
    expected = {
        "user": "65532:65532",
        "network_names": sorted([launcher.NETWORK, "bridge"]),
        "broker_alias_present": True,
        "read_only_rootfs": True,
        "privileged": False,
        "cap_drop": ["ALL"],
        "cap_add": [],
        "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 67108864,
        "memory_swap_bytes": 67108864,
        "nano_cpus": 250000000,
        "pids_limit": 32,
        "nofile_exact": True,
        "mount_count": 1,
        "token_mount_destination_exact": True,
        "tmpfs": {"/tmp": "rw,noexec,nosuid,size=8m"},
        "port_binding_count": 0,
        "publish_all_ports": False,
    }
    if selected != expected:
        raise RehearsalError("relay_effective_policy_invalid")
    return selected


def verify_network(network: dict[str, Any]) -> dict[str, Any]:
    selected = {
        "name": network.get("Name"),
        "driver": network.get("Driver"),
        "internal": network.get("Internal"),
        "attachable": network.get("Attachable"),
        "ingress": network.get("Ingress"),
    }
    if selected != {
        "name": launcher.NETWORK,
        "driver": "bridge",
        "internal": True,
        "attachable": False,
        "ingress": False,
    }:
        raise RehearsalError("internal_network_policy_invalid")
    return selected


def create_ledger(
    path: Path,
    mode: str,
    request_packet: dict[str, Any] | None = None,
) -> None:
    if path.exists():
        raise RehearsalError("ledger_already_exists")
    request_packet = request_packet or contracts.load_object(
        contracts.CELL_REQUEST_PATH
    )
    if contracts.validate_cell_request(request_packet):
        raise RehearsalError("ledger_request_invalid")
    ledger = {
        "schema_version": "ariadne.vertex_sydney_single_use_ledger.v1",
        "ledger_id": request_packet["ledger_id"],
        "attempt_id": request_packet["attempt_id"],
        "policy_id": contracts.POLICY_ID,
        "status": "open",
        "maximum_provider_calls": 0 if mode == "dry-run" else 1,
        "provider_calls_consumed": 0,
        "fallback_permitted": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def close_open_ledger(path: Path, audit_path: Path) -> bool:
    """Consume an opened ledger when the broker could not consume it."""

    if not path.is_file():
        return False
    ledger = contracts.load_object(path)
    if ledger.get("status") != "open":
        return False
    if ledger.get("provider_calls_consumed") != 0:
        raise RehearsalError("open_ledger_has_provider_call")
    consumed = dict(ledger)
    consumed["status"] = "consumed"
    consumed["closure_reason"] = "lifecycle_closed_before_broker_consumption"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(consumed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)
    events = _read_audit(audit_path)
    event = contracts.audit_event(
        sequence=len(events) + 1,
        previous_hash=events[-1]["event_hash"],
        event_type="ledger_consumed",
        fields={
            "ledger_id": ledger["ledger_id"],
            "attempt_id": ledger["attempt_id"],
            "provider_calls_reserved": 0,
            "closure_reason": "lifecycle_closed_before_broker_consumption",
        },
    )
    with audit_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return True


def _terminate_process(process: subprocess.Popen[bytes] | None) -> bool:
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


def run_lifecycle(
    *,
    mode: str,
    evidence_path: Path,
    ledger_path: Path,
    audit_path: Path,
    request_path: Path = contracts.CELL_REQUEST_PATH,
) -> dict[str, Any]:
    if mode not in {"dry-run", "live"}:
        raise RehearsalError("mode_invalid")
    if evidence_path.exists() or audit_path.exists():
        raise RehearsalError("output_already_exists")

    try:
        request_relative = request_path.resolve().relative_to(ROOT).as_posix()
    except ValueError as error:
        raise RehearsalError("request_path_outside_repository") from error
    if request_relative not in launcher.ALLOWED_REQUEST_SOURCES:
        raise RehearsalError("request_path_not_allowlisted")
    request_packet = contracts.load_object(request_path)
    request_errors = contracts.validate_cell_request(request_packet)
    if request_errors:
        raise RehearsalError("request_contract_invalid")
    attempt_id = request_packet["attempt_id"]
    if not contracts.validate_attempt_mode(attempt_id, mode):
        raise RehearsalError("request_attempt_mode_invalid")
    plan = launcher.build_plan(request_relative)
    if launcher.validate_plan(plan):
        raise RehearsalError("launch_plan_invalid")
    docker = Docker()
    collisions = {
        "cell": docker.exists("container", launcher.CELL_CONTAINER),
        "relay": docker.exists("container", launcher.RELAY_CONTAINER),
        "network": docker.exists("network", launcher.NETWORK),
        "cell_image": docker.exists("image", launcher.CELL_IMAGE),
        "relay_image": docker.exists("image", launcher.RELAY_IMAGE),
    }
    if any(collisions.values()):
        raise RehearsalError("task_scoped_runtime_name_collision")
    base_preexisting = docker.exists("image", BASE_IMAGE)

    temporary_root = Path(
        tempfile.mkdtemp(prefix="ariadne-vertex-sydney-gemini-25-")
    )
    context_path = temporary_root / "context"
    token_path = temporary_root / "broker-token"
    process: subprocess.Popen[bytes] | None = None
    cell_created = False
    relay_created = False
    network_created = False
    cell_image_created = False
    relay_image_created = False
    ledger_created = False
    cleanup_errors: list[str] = []
    evidence: dict[str, Any] | None = None
    try:
        context_hashes = create_exact_context(plan, context_path)
        token_path.write_text(secrets.token_urlsafe(48), encoding="utf-8")
        port = _free_port()

        docker.run(
            _replace_placeholders(
                plan["docker_commands"]["build_relay"], context=context_path
            ),
            timeout=300,
        )
        relay_image_created = True
        docker.run(
            _replace_placeholders(
                plan["docker_commands"]["build_cell"], context=context_path
            ),
            timeout=300,
        )
        cell_image_created = True
        create_ledger(ledger_path, mode, request_packet)
        ledger_created = True

        broker_command = [
            sys.executable,
            "-m",
            BROKER_MODULE,
            "--mode",
            mode,
            "--listen-port",
            str(port),
            "--token-file",
            str(token_path),
            "--ledger",
            str(ledger_path),
            "--audit",
            str(audit_path),
            "--policy",
            str(contracts.POLICY_PATH),
            "--request",
            str(request_path),
        ]
        creation_flags = (
            subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
            if os.name == "nt"
            else 0
        )
        process = subprocess.Popen(
            broker_command,
            cwd=ROOT,
            env=_safe_broker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            creationflags=creation_flags,
        )
        _wait_for_broker(process, audit_path)

        docker.run(
            _replace_placeholders(
                plan["docker_commands"]["create_internal_network"]
            )
        )
        network_created = True
        network_policy = verify_network(
            docker.inspect("network", launcher.NETWORK)
        )

        docker.run(
            _replace_placeholders(
                plan["docker_commands"]["create_relay"],
                token=token_path,
                port=port,
            )
        )
        relay_created = True
        docker.run(
            _replace_placeholders(
                plan["docker_commands"]["connect_relay_egress"]
            )
        )
        relay_policy = verify_relay(
            docker.inspect("container", launcher.RELAY_CONTAINER)
        )
        docker.run(["start", launcher.RELAY_CONTAINER])
        relay_deadline = time.monotonic() + 3
        while time.monotonic() < relay_deadline:
            relay_runtime = _state_summary(
                docker.inspect("container", launcher.RELAY_CONTAINER)
            )
            if relay_runtime["running"] is True:
                break
            time.sleep(0.1)
        else:
            raise RehearsalError("relay_not_running")
        time.sleep(0.5)

        docker.run(
            _replace_placeholders(plan["docker_commands"]["create_cell"])
        )
        cell_created = True
        cell_policy = verify_cell(
            docker.inspect("container", launcher.CELL_CONTAINER)
        )
        cell_result = docker.run(
            _replace_placeholders(plan["docker_commands"]["start_cell"]),
            timeout=90,
            allowed_returncodes=frozenset({0, 1, 2}),
        )
        try:
            cell_packet = json.loads(cell_result.stdout)
        except json.JSONDecodeError as error:
            transport_diagnostic = (
                cell_result.stdout + "\n" + cell_result.stderr
            ).casefold()
            if "remote end closed connection" in transport_diagnostic:
                reason = "cell_relay_connection_closed"
            elif "connection refused" in transport_diagnostic:
                reason = "cell_relay_connection_refused"
            elif (
                "name or service not known" in transport_diagnostic
                or "gaierror" in transport_diagnostic
            ):
                reason = "cell_broker_alias_unresolved"
            elif "timed out" in transport_diagnostic:
                reason = "cell_relay_connection_timed_out"
            else:
                reason = "cell_output_not_json"
            raise RehearsalError(reason) from error
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired as error:
            raise RehearsalError("broker_did_not_exit") from error

        events = _read_audit(audit_path)
        event_types = [event["event_type"] for event in events]
        ledger = contracts.load_object(ledger_path)
        cell_state = _state_summary(
            docker.inspect("container", launcher.CELL_CONTAINER)
        )
        relay_state = _state_summary(
            docker.inspect("container", launcher.RELAY_CONTAINER)
        )

        if ledger.get("status") != "consumed":
            raise RehearsalError("ledger_not_consumed")
        if mode == "dry-run":
            if (
                cell_result.returncode != 0
                or process.returncode != 0
                or cell_packet.get("status") != "completed"
                or ledger.get("provider_calls_consumed") != 0
                or event_types.count("provider_call_simulated") != 1
                or any(
                    item
                    in {
                        "provider_call_started",
                        "provider_call_completed",
                        "provider_call_failed",
                    }
                    for item in event_types
                )
            ):
                raise RehearsalError("dry_run_exchange_invalid")
            result = DRY_RESULT
            provider_contacted = False
        else:
            if ledger.get("provider_calls_consumed") != 1:
                raise RehearsalError("occupied_call_not_reserved")
            provider_contacted = "provider_call_started" in event_types
            if not provider_contacted:
                raise RehearsalError("occupied_call_not_started")
            result = (
                LIVE_PASS
                if (
                    cell_result.returncode == 0
                    and process.returncode == 0
                    and cell_packet.get("status") == "completed"
                )
                else LIVE_FAILED
            )

        release = (
            cell_packet.get("release")
            if cell_packet.get("status") == "completed"
            else None
        )
        proofreader = (
            cell_packet.get("proofreader")
            if cell_packet.get("status") == "completed"
            else None
        )
        evidence = {
            "schema_version": SCHEMA_VERSION,
            "result": result,
            "mode": mode,
            "attempt_id": request_packet["attempt_id"],
            "ledger_id": request_packet["ledger_id"],
            "provider_contacted": provider_contacted,
            "provider_call_count_reserved": ledger[
                "provider_calls_consumed"
            ],
            "fallback_performed": False,
            "exact_binding": {
                "provider": "google_vertex_ai",
                "model_id": "gemini-2.5-flash",
                "project": "bernie-emr4-dev",
                "service_account": (
                    "emr4-bernie-ai-dev@bernie-emr4-dev."
                    "iam.gserviceaccount.com"
                ),
                "authentication": (
                    "keyless_impersonated_service_account_adc"
                ),
                "location": "australia-southeast1",
                "endpoint_hostname": (
                    "australia-southeast1-aiplatform.googleapis.com"
                ),
                "api_key_authentication_used": False,
            },
            "build_context": {
                "repository_root_used": False,
                "temporary_exact_allowlist": True,
                "file_count": len(context_hashes),
                "source_hashes": context_hashes,
                "manifest_hash": file_hash(
                    contracts.ARTIFACT_ROOT / "isolation-manifest.json"
                ),
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
                "endpoint_policy_hash": file_hash(contracts.POLICY_PATH),
                "process_exit_code": process.returncode,
            },
            "exchange": {
                "cell_exit_code": cell_result.returncode,
                "cell_state": cell_state,
                "relay_state": relay_state,
                "request_hash": contracts.canonical_hash(
                    request_packet
                ),
                "schema_hash": contracts.canonical_hash(
                    contracts.provider_response_schema()
                ),
                "audit_event_count": len(events),
                "audit_event_types": event_types,
                "audit_hash_chain_valid": True,
                "audit_terminal_hash": events[-1]["event_hash"],
                "release": release,
                "proofreader": proofreader,
            },
            "ledger": ledger,
            "explicit_exclusions": {
                "raw_prompt_recorded": False,
                "raw_provider_response_recorded": False,
                "credential_or_token_recorded": False,
                "api_key_information_recorded": False,
                "chain_of_thought_recorded": False,
                "product_or_database_access": False,
                "command_authority": False,
                "human_or_product_delivery": False,
            },
        }
    finally:
        broker_absent = _terminate_process(process)
        if ledger_created:
            try:
                close_open_ledger(ledger_path, audit_path)
            except (OSError, RehearsalError, contracts.ContractError):
                cleanup_errors.append("open_ledger_close_failed")
        if cell_created:
            try:
                docker.run(["rm", "--force", launcher.CELL_CONTAINER])
            except RehearsalError:
                cleanup_errors.append("cell_remove_failed")
        if relay_created:
            try:
                docker.run(["rm", "--force", launcher.RELAY_CONTAINER])
            except RehearsalError:
                cleanup_errors.append("relay_remove_failed")
        if network_created:
            try:
                docker.run(["network", "rm", launcher.NETWORK])
            except RehearsalError:
                cleanup_errors.append("network_remove_failed")
        if cell_image_created:
            try:
                docker.run(["image", "rm", launcher.CELL_IMAGE])
            except RehearsalError:
                cleanup_errors.append("cell_image_remove_failed")
        if relay_image_created:
            try:
                docker.run(["image", "rm", launcher.RELAY_IMAGE])
            except RehearsalError:
                cleanup_errors.append("relay_image_remove_failed")
        if not base_preexisting and docker.exists("image", BASE_IMAGE):
            try:
                docker.run(["image", "rm", BASE_IMAGE])
            except RehearsalError:
                cleanup_errors.append("base_image_remove_failed")
        try:
            shutil.rmtree(temporary_root)
        except OSError:
            cleanup_errors.append("temporary_root_remove_failed")

    residue = {
        "cell_container_absent": not docker.exists(
            "container", launcher.CELL_CONTAINER
        ),
        "relay_container_absent": not docker.exists(
            "container", launcher.RELAY_CONTAINER
        ),
        "internal_network_absent": not docker.exists(
            "network", launcher.NETWORK
        ),
        "cell_image_absent": not docker.exists("image", launcher.CELL_IMAGE),
        "relay_image_absent": not docker.exists("image", launcher.RELAY_IMAGE),
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
    if evidence is None:
        raise RehearsalError("rehearsal_evidence_missing")
    if cleanup_errors or not all(
        value
        for key, value in residue.items()
        if key != "daemon_wide_prune_performed"
    ):
        raise RehearsalError("task_scoped_cleanup_failed")
    evidence["cleanup"] = residue
    evidence["evidence_hash"] = canonical_hash(evidence)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dry-run", "live"), required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument(
        "--request",
        type=Path,
        default=contracts.CELL_REQUEST_PATH,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        evidence = run_lifecycle(
            mode=arguments.mode,
            evidence_path=arguments.evidence.resolve(),
            ledger_path=arguments.ledger.resolve(),
            audit_path=arguments.audit.resolve(),
            request_path=arguments.request.resolve(),
        )
    except (OSError, RehearsalError, contracts.ContractError) as error:
        reason_code = (
            str(error)
            if isinstance(error, (RehearsalError, contracts.ContractError))
            else "filesystem_operation_failed"
        )
        print(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "revision_required",
                    "result": (
                        "ariadne_vertex_sydney_gemini_25_"
                        "isolation_lifecycle_failed"
                    ),
                    "reason_code": reason_code,
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "passed",
                "result": evidence["result"],
                "evidence_hash": evidence["evidence_hash"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] in {DRY_RESULT, LIVE_PASS} else 2


if __name__ == "__main__":
    raise SystemExit(main())
