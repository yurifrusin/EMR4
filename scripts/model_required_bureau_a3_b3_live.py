#!/usr/bin/env python3
"""Run the isolated provider-free or occupied Bureau A3/B3 tranche."""

from __future__ import annotations

import argparse
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

from scripts import model_required_bureau_a3_b3_contracts as contracts


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
DOCKERFILE = ARTIFACT_ROOT / "Dockerfile"
RELAY_SOURCE = ROOT / "scripts/ariadne_vertex_sydney_gemini_25_relay.py"
CELL_SOURCE = ROOT / "scripts/ariadne_vertex_sydney_gemini_25_cell.py"
PREFLIGHT_SCRIPT = ROOT / "scripts/ariadne_vertex_sydney_gemini_25_preflight.py"
CELL_REQUEST_SCHEMA = ARTIFACT_ROOT / "cell-request.schema.json"
ATTEMPT_LEDGER_SCHEMA = ARTIFACT_ROOT / "single-use-ledger.schema.json"
COST_LEDGER_SCHEMA = ARTIFACT_ROOT / "cost-ledger.schema.json"
BLOCKED_PREFLIGHT_SCHEMA = ARTIFACT_ROOT / "occupied-preflight-blocked.schema.json"
TERMINAL_INTERRUPTION_SCHEMA = (
    ARTIFACT_ROOT / "occupied-terminal-interruption.schema.json"
)
SOURCE_REVIEW_RECEIPT = (
    ROOT
    / "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-a3-b3-review-6-receipt.json"
)
BASE_IMAGE = (
    "docker.io/library/python@sha256:"
    "a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322"
)
TOKEN_DESTINATION = "/run/secrets/broker_token"
BROKER_ENVIRONMENT_ALLOWLIST = (
    "APPDATA", "COMSPEC", "LOCALAPPDATA", "PATH", "PATHEXT",
    "SYSTEMDRIVE", "SYSTEMROOT", "TEMP", "TMP", "USERPROFILE", "WINDIR",
)
CREDENTIAL_ENV_NAMES = {
    "GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS",
    "OPENAI_API_KEY", "CLOUDSDK_CONFIG",
}
ZERO_HASH = "sha256:" + "0" * 64
PREPROOF_TERMINAL_REASON_CODES = frozenset(
    {
        "provider_candidate_count_invalid",
        "provider_content_invalid",
        "provider_text_invalid",
        "provider_candidate_not_json",
        "provider_candidate_not_object",
    }
)


class LiveError(RuntimeError):
    """A fail-closed local lifecycle error."""


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
        return self.run(
            [kind, "inspect", reference], allowed=frozenset({0, 1})
        ).returncode == 0

    def inspect(self, kind: str, reference: str) -> dict[str, Any]:
        try:
            value = json.loads(self.run([kind, "inspect", reference]).stdout)
        except json.JSONDecodeError as error:
            raise LiveError("docker_inspect_invalid") from error
        if not isinstance(value, list) or len(value) != 1:
            raise LiveError("docker_inspect_invalid")
        return value[0]


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _file_hash(path: Path) -> str:
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


def _names(lane: str, attempt_number: int) -> dict[str, str]:
    short_lane = "rayleen" if lane == contracts.LANE_RAYLEEN else "davida"
    suffix = f"{short_lane}-{attempt_number}"
    return {
        "network": f"emr4-a3-b3-{suffix}-internal",
        "relay_container": f"emr4-a3-b3-{suffix}-relay",
        "cell_container": f"emr4-a3-b3-{suffix}-cell",
        "relay_image": f"emr4-a3-b3-{suffix}-relay:v1",
        "cell_image": f"emr4-a3-b3-{suffix}-cell:v1",
    }


def _attempt_paths(
    lane: str,
    attempt_number: int,
    *,
    mode: str,
) -> dict[str, Path]:
    lane_stem = lane.replace("_", "-")
    attempt_stem = f"{lane_stem}-attempt-{attempt_number}"
    execution_stem = (
        attempt_stem if mode == "dry-run" else attempt_stem + "-occupied"
    )
    return {
        "ledger": ARTIFACT_ROOT / f"{execution_stem}-ledger.json",
        "audit": ARTIFACT_ROOT / f"{execution_stem}-audit.jsonl",
        "evidence": ARTIFACT_ROOT
        / (
            f"{attempt_stem}-dry-run-evidence.json"
            if mode == "dry-run"
            else f"{execution_stem}-evidence.json"
        ),
        "preflight": ARTIFACT_ROOT / f"{attempt_stem}-preflight.json",
    }


def _request_packet(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_of: str | None,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    kind = "primary" if attempt_number == 1 else "correction"
    lane_id = "rayleen-a3" if lane == contracts.LANE_RAYLEEN else "davida-b3"
    request = contracts.provider_request_for_attempt(
        lane,
        context,
        attempt_number=attempt_number,
        correction_reason_code=correction_reason_code,
    )
    packet = {
        "schema_version": "emr4.model_required_bureau_a3_b3.cell_request.v1",
        "lane": lane,
        "attempt_id": f"a3-b3-{lane_id}-{kind}-{attempt_number:03d}",
        "ledger_id": f"ledger-a3-b3-{lane_id}-{kind}-{attempt_number:03d}",
        "policy_id": contracts.POLICY_ID,
        "context_hash": contracts.prefixed_sha256(context),
        "provider_request_hash": contracts.prefixed_sha256(request),
        "attempt_number": attempt_number,
        "correction_of": correction_of,
        "correction_reason_code": correction_reason_code,
    }
    contracts.validate_instance(CELL_REQUEST_SCHEMA, packet)
    return packet


def _attempt_ledger(packet: dict[str, Any], *, mode: str) -> dict[str, Any]:
    live = mode == "live"
    ledger = {
        "schema_version": "emr4.model_required_bureau_a3_b3.single_use_ledger.v1",
        "ledger_id": packet["ledger_id"],
        "attempt_id": packet["attempt_id"],
        "lane": packet["lane"],
        "policy_id": packet["policy_id"],
        "status": "open",
        "maximum_provider_calls": 1 if live else 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": contracts.RESERVED_COST_PER_CALL_USD if live else 0,
        "fallback_permitted": False,
    }
    contracts.validate_instance(ATTEMPT_LEDGER_SCHEMA, ledger)
    return ledger


def _initial_cost_ledger() -> dict[str, Any]:
    ledger = {
        "schema_version": "emr4.model_required_bureau_a3_b3.cost_ledger.v1",
        "tranche_id": "model-required-bureau-a3-b3-occupied-001",
        "status": "open",
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "provider_calls_reserved": 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": 0,
        "lane_calls": {contracts.LANE_RAYLEEN: 0, contracts.LANE_DAVIDA: 0},
        "fallback_permitted": False,
    }
    contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
    return ledger


def _reserve_cost(
    ledger: dict[str, Any], lane: str, *, mode: str
) -> dict[str, Any]:
    updated = json.loads(json.dumps(ledger))
    if mode == "dry-run":
        return updated
    if updated["status"] != "open":
        raise LiveError("cost_ledger_closed")
    if updated["lane_calls"][lane] >= contracts.MAX_CALLS_PER_LANE:
        raise LiveError("lane_call_ceiling_exceeded")
    if updated["provider_calls_reserved"] >= contracts.MAX_CALLS_TOTAL:
        raise LiveError("tranche_call_ceiling_exceeded")
    next_cost = updated["reserved_cost_usd"] + contracts.RESERVED_COST_PER_CALL_USD
    if next_cost > contracts.MAX_COST_USD:
        raise LiveError("tranche_cost_ceiling_exceeded")
    updated["provider_calls_reserved"] += 1
    updated["lane_calls"][lane] += 1
    updated["reserved_cost_usd"] = next_cost
    contracts.validate_instance(COST_LEDGER_SCHEMA, updated)
    return updated


def _reconcile_parent_consumption(
    ledger: dict[str, Any], lane_results: list[dict[str, Any]]
) -> dict[str, Any]:
    updated = json.loads(json.dumps(ledger))
    consumed_values = [item.get("provider_call_count") for item in lane_results]
    if not all(type(value) is int and value in {0, 1} for value in consumed_values):
        raise LiveError("attempt_provider_call_count_invalid")
    consumed = sum(consumed_values)
    if consumed > updated["provider_calls_reserved"]:
        raise LiveError("parent_cost_consumption_exceeds_reservation")
    updated["provider_calls_consumed"] = consumed
    contracts.validate_instance(COST_LEDGER_SCHEMA, updated)
    return updated


def _resume_preflight_blocked_cost_ledger(
    *,
    cost_ledger_path: Path,
    blocked_evidence_path: Path,
) -> dict[str, Any]:
    if not cost_ledger_path.exists() or not blocked_evidence_path.exists():
        raise LiveError("preflight_resume_evidence_missing")
    ledger = contracts.load_object(cost_ledger_path)
    blocked = contracts.load_object(blocked_evidence_path)
    contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
    contracts.validate_instance(BLOCKED_PREFLIGHT_SCHEMA, blocked)
    expected = _reserve_cost(
        _initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
    )
    expected_ledger_path = (
        "orchestration/continuity/model-required-bureau-a3-b3/"
        "occupied-rehearsal-cost-ledger.json"
    )
    if (
        ledger != expected
        or blocked["cost_ledger_path"] != expected_ledger_path
        or cost_ledger_path.resolve()
        != (ROOT / expected_ledger_path).resolve()
        or blocked["cost_ledger_sha256"] != _file_hash(cost_ledger_path)
        or blocked["source_head"] != blocked["source_review_head"]
    ):
        raise LiveError("preflight_resume_binding_invalid")
    occupied_paths = _attempt_paths(
        contracts.LANE_RAYLEEN, 1, mode="live"
    )
    if any(path.exists() for path in occupied_paths.values()):
        raise LiveError("preflight_resume_attempt_artifact_present")
    return ledger


def _read_events(path: Path) -> list[dict[str, Any]]:
    try:
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    except (OSError, json.JSONDecodeError) as error:
        raise LiveError("audit_unreadable") from error
    if not events or not all(isinstance(item, dict) for item in events):
        raise LiveError("audit_empty_or_invalid")
    previous_hash = ZERO_HASH
    for sequence, event in enumerate(events, start=1):
        observed_hash = event.get("event_hash")
        material = {key: value for key, value in event.items() if key != "event_hash"}
        if (
            event.get("sequence") != sequence
            or event.get("previous_hash") != previous_hash
            or observed_hash != contracts.prefixed_sha256(material)
        ):
            raise LiveError("audit_hash_chain_invalid")
        previous_hash = observed_hash
    return events


def _classify_attempt_events(
    events: list[dict[str, Any]], *, mode: str
) -> dict[str, Any]:
    event_types = [event.get("event_type") for event in events]
    if event_types.count("request_admitted") != 1:
        raise LiveError("audit_event_cardinality_invalid")
    expected_calls = 1 if mode == "live" else 0
    if event_types.count("provider_call_started") != expected_calls:
        raise LiveError("provider_call_cardinality_invalid")
    if mode == "dry-run" and "broker_rejected" in event_types:
        raise LiveError("provider_free_broker_rejected")

    proofreader_count = event_types.count("proofreader_completed")
    rejection_events = [
        event for event in events if event.get("event_type") == "broker_rejected"
    ]
    if proofreader_count == 1 and not rejection_events:
        return {
            "terminal_preproof_rejection": False,
            "reason_code": None,
            "correction_eligible": None,
            "provider_metadata": None,
        }
    if proofreader_count != 0 or len(rejection_events) != 1 or mode != "live":
        raise LiveError("audit_event_cardinality_invalid")

    fields = rejection_events[0].get("fields")
    if not isinstance(fields, dict):
        raise LiveError("broker_rejection_evidence_invalid")
    reason_code = fields.get("reason_code")
    if (
        reason_code not in PREPROOF_TERMINAL_REASON_CODES
        or fields.get("provider_contacted") is not True
        or fields.get("provider_retry") is not False
        or fields.get("correction_eligible", False) is not False
        or "release_committed" in event_types
    ):
        raise LiveError("broker_rejection_evidence_invalid")
    completed = [
        event for event in events if event.get("event_type") == "provider_call_completed"
    ]
    if len(completed) > 1:
        raise LiveError("provider_completion_cardinality_invalid")
    provider_metadata = None
    if completed:
        provider_metadata = completed[0].get("fields")
    elif isinstance(fields.get("provider_metadata"), dict):
        provider_metadata = fields["provider_metadata"]
    return {
        "terminal_preproof_rejection": True,
        "reason_code": reason_code,
        "correction_eligible": False,
        "provider_metadata": provider_metadata,
    }


def _exact_runtime_absence(lane: str, attempt_number: int) -> dict[str, bool]:
    docker = Docker()
    names = _names(lane, attempt_number)
    return {
        "cell_container_absent": not docker.exists(
            "container", names["cell_container"]
        ),
        "relay_container_absent": not docker.exists(
            "container", names["relay_container"]
        ),
        "internal_network_absent": not docker.exists(
            "network", names["network"]
        ),
        "cell_image_absent": not docker.exists("image", names["cell_image"]),
        "relay_image_absent": not docker.exists("image", names["relay_image"]),
    }


def _wait_broker(process: subprocess.Popen[bytes], audit_path: Path) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise LiveError("broker_failed_before_ready")
        if audit_path.is_file() and audit_path.stat().st_size:
            if _read_events(audit_path)[0].get("event_type") == "broker_ready":
                return
        time.sleep(0.1)
    raise LiveError("broker_ready_timeout")


def _wait_relay(docker: Docker, relay_container: str) -> None:
    probe = (
        "from pathlib import Path; rows=Path('/proc/net/tcp').read_text().splitlines()[1:]; "
        "assert any(parts[1].endswith(':1F90') and parts[3]=='0A' "
        "for row in rows if (parts:=row.split()))"
    )
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = docker.run(
            ["exec", relay_container, "python", "-c", probe],
            timeout=5,
            allowed=frozenset({0, 1}),
        )
        if result.returncode == 0:
            return
        time.sleep(0.1)
    raise LiveError("relay_ready_timeout")


def _verify_network(value: dict[str, Any], name: str) -> dict[str, Any]:
    selected = {
        "name": value.get("Name"), "driver": value.get("Driver"),
        "internal": value.get("Internal"), "attachable": value.get("Attachable"),
        "ingress": value.get("Ingress"),
    }
    if selected != {"name": name, "driver": "bridge", "internal": True, "attachable": False, "ingress": False}:
        raise LiveError("internal_network_policy_invalid")
    return selected


def _verify_cell(value: dict[str, Any], network: str) -> dict[str, Any]:
    config = value.get("Config", {})
    host = value.get("HostConfig", {})
    networks = (value.get("NetworkSettings") or {}).get("Networks") or {}
    environment_names = {
        item.split("=", 1)[0] for item in config.get("Env") or [] if isinstance(item, str)
    }
    selected = {
        "user": config.get("User"), "network_names": sorted(networks),
        "read_only_rootfs": host.get("ReadonlyRootfs"), "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [], "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"), "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"), "pids_limit": host.get("PidsLimit"),
        "mount_count": len(value.get("Mounts") or []),
        "credential_environment_present": bool(environment_names & CREDENTIAL_ENV_NAMES),
        "port_binding_count": len(host.get("PortBindings") or {}),
    }
    expected = {
        "user": "65532:65532", "network_names": [network], "read_only_rootfs": True,
        "privileged": False, "cap_drop": ["ALL"], "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 134217728, "memory_swap_bytes": 134217728,
        "nano_cpus": 500000000, "pids_limit": 64, "mount_count": 0,
        "credential_environment_present": False, "port_binding_count": 0,
    }
    if selected != expected:
        raise LiveError("cell_effective_policy_invalid")
    return selected


def _verify_relay(value: dict[str, Any], network: str) -> dict[str, Any]:
    config = value.get("Config", {})
    host = value.get("HostConfig", {})
    networks = (value.get("NetworkSettings") or {}).get("Networks") or {}
    mounts = value.get("Mounts") or []
    internal = networks.get(network) or {}
    selected = {
        "user": config.get("User"), "network_names": sorted(networks),
        "broker_alias_present": "broker" in (internal.get("Aliases") or []),
        "read_only_rootfs": host.get("ReadonlyRootfs"), "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [], "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"), "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"), "pids_limit": host.get("PidsLimit"),
        "mount_count": len(mounts),
        "token_mount_exact": len(mounts) == 1 and mounts[0].get("Destination") == TOKEN_DESTINATION and mounts[0].get("RW") is False,
        "port_binding_count": len(host.get("PortBindings") or {}),
    }
    expected = {
        "user": "65532:65532", "network_names": sorted([network, "bridge"]),
        "broker_alias_present": True, "read_only_rootfs": True, "privileged": False,
        "cap_drop": ["ALL"], "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 67108864, "memory_swap_bytes": 67108864,
        "nano_cpus": 250000000, "pids_limit": 32, "mount_count": 1,
        "token_mount_exact": True, "port_binding_count": 0,
    }
    if selected != expected:
        raise LiveError("relay_effective_policy_invalid")
    return selected


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


def _run_preflight(path: Path) -> dict[str, Any]:
    if path.exists():
        raise LiveError("preflight_output_already_exists")
    result = subprocess.run(
        [sys.executable, "-B", str(PREFLIGHT_SCRIPT), "--output", str(path)],
        cwd=ROOT,
        env=_safe_broker_environment(),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        shell=False,
    )
    if result.returncode != 0:
        raise LiveError("read_only_preflight_blocked")
    evidence = contracts.load_object(path)
    if (
        evidence.get("result") != "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
        or evidence.get("project") != contracts.PROJECT
        or evidence.get("service_account") != contracts.SERVICE_ACCOUNT
        or evidence.get("location") != contracts.LOCATION
        or evidence.get("endpoint_hostname") != contracts.HOSTNAME
        or evidence.get("model_id") != contracts.MODEL
        or evidence.get("provider_prompt_transmitted") is not False
        or evidence.get("model_inference_called") is not False
        or not isinstance(evidence.get("checks"), dict)
        or not all(evidence["checks"].values())
    ):
        raise LiveError("read_only_preflight_not_exact")
    return evidence


def _validate_source_review(path: Path) -> dict[str, Any]:
    receipt = contracts.load_object(path)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8", shell=False,
    ).stdout.strip()
    if (
        receipt.get("status") != "completed"
        or receipt.get("transport") != "antigravity_new_project_bound_readonly_worktree"
        or receipt.get("model") != "gemini-3.6-flash-high"
        or receipt.get("reasoning_effort") != "high"
        or receipt.get("decision") != "pass"
        or receipt.get("head_before") != head
        or receipt.get("head_after") != head
        or receipt.get("dirty_after") is not False
    ):
        raise LiveError("independent_source_review_not_exact")
    return receipt


def _run_attempt(
    *, lane: str, mode: str, attempt_number: int,
    correction_of: str | None, correction_reason_code: str | None,
    preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    context_path = (
        contracts.RAYLEEN_CONTEXT_PATH if lane == contracts.LANE_RAYLEEN
        else contracts.DAVIDA_CONTEXT_PATH
    )
    context_value = contracts.load_object(context_path)
    packet = _request_packet(
        lane, context_value, attempt_number=attempt_number,
        correction_of=correction_of,
        correction_reason_code=correction_reason_code,
    )
    names = _names(lane, attempt_number)
    docker = Docker()
    collisions = {
        "network": docker.exists("network", names["network"]),
        "relay": docker.exists("container", names["relay_container"]),
        "cell": docker.exists("container", names["cell_container"]),
        "relay_image": docker.exists("image", names["relay_image"]),
        "cell_image": docker.exists("image", names["cell_image"]),
    }
    if any(collisions.values()):
        raise LiveError("task_scoped_runtime_name_collision")
    base_preexisting = docker.exists("image", BASE_IMAGE)
    if not base_preexisting:
        docker.run(["pull", BASE_IMAGE], timeout=300)
        if not docker.exists("image", BASE_IMAGE):
            raise LiveError("pinned_base_image_unavailable")
    paths = _attempt_paths(lane, attempt_number, mode=mode)
    ledger_path = paths["ledger"]
    audit_path = paths["audit"]
    evidence_path = paths["evidence"]
    if any(path.exists() for path in (ledger_path, audit_path, evidence_path)):
        raise LiveError("attempt_output_already_exists")
    temporary_root = Path(tempfile.mkdtemp(prefix="emr4-a3-b3-"))
    build_context = temporary_root / "context"
    token_path = temporary_root / "broker-token"
    request_path = temporary_root / "request.json"
    context_copy = temporary_root / "context.json"
    process: subprocess.Popen[bytes] | None = None
    flags = {"network": False, "relay": False, "cell": False, "relay_image": False, "cell_image": False}
    cleanup_errors: list[str] = []
    result_packet: dict[str, Any] | None = None
    network_policy: dict[str, Any] | None = None
    relay_policy: dict[str, Any] | None = None
    cell_policy: dict[str, Any] | None = None
    build_hashes: dict[str, str] = {}
    try:
        build_context.mkdir()
        for target, source in (("Dockerfile", DOCKERFILE), ("relay.py", RELAY_SOURCE), ("cell.py", CELL_SOURCE)):
            shutil.copy2(source, build_context / target)
            build_hashes[source.relative_to(ROOT).as_posix()] = _file_hash(source)
        (build_context / "cell-request.json").write_bytes(contracts.canonical_bytes(packet))
        build_hashes["generated:cell-request.json"] = _file_hash(build_context / "cell-request.json")
        actual = {path.name for path in build_context.iterdir() if path.is_file()}
        if actual != {"Dockerfile", "relay.py", "cell.py", "cell-request.json"}:
            raise LiveError("build_context_not_exact")
        token_path.write_text(secrets.token_urlsafe(48), encoding="utf-8")
        request_path.write_bytes(contracts.canonical_bytes(packet))
        context_copy.write_bytes(contracts.canonical_bytes(context_value))
        _write_json(ledger_path, _attempt_ledger(packet, mode=mode))

        docker.run(["build", "--pull=false", "--network", "none", "--target", "relay", "--tag", names["relay_image"], str(build_context)], timeout=300)
        flags["relay_image"] = True
        docker.run(["build", "--pull=false", "--network", "none", "--target", "work-cell", "--tag", names["cell_image"], str(build_context)], timeout=300)
        flags["cell_image"] = True
        port = _free_port()
        creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0  # type: ignore[attr-defined]
        process = subprocess.Popen(
            [sys.executable, "-B", "-m", "scripts.model_required_bureau_a3_b3_broker",
             "--mode", mode, "--listen-port", str(port), "--token-file", str(token_path),
             "--ledger", str(ledger_path), "--audit", str(audit_path),
             "--request", str(request_path), "--context", str(context_copy), "--lane", lane],
            cwd=ROOT, env=_safe_broker_environment(), stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False,
            creationflags=creation_flags,
        )
        _wait_broker(process, audit_path)
        docker.run(["network", "create", "--internal", names["network"]])
        flags["network"] = True
        network_policy = _verify_network(docker.inspect("network", names["network"]), names["network"])
        docker.run([
            "create", "--name", names["relay_container"], "--network", "bridge", "--read-only",
            "--user", "65532:65532", "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=8m",  # nosec B108 -- container-internal tmpfs
            "--memory", "64m", "--memory-swap", "64m", "--cpus", "0.25", "--pids-limit", "32",
            "--ulimit", "nofile=64:64", "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true",
            "--mount", f"type=bind,src={token_path},dst={TOKEN_DESTINATION},readonly",
            "--env", f"BROKER_HOST_PORT={port}", names["relay_image"],
        ])
        flags["relay"] = True
        docker.run(["network", "connect", "--alias", "broker", names["network"], names["relay_container"]])
        relay_policy = _verify_relay(docker.inspect("container", names["relay_container"]), names["network"])
        docker.run(["start", names["relay_container"]])
        _wait_relay(docker, names["relay_container"])
        docker.run([
            "create", "--name", names["cell_container"], "--hostname", "emr4-a3-b3-model-cell",
            "--network", names["network"], "--read-only", "--user", "65532:65532",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=8m",  # nosec B108 -- container-internal tmpfs
            "--memory", "128m", "--memory-swap", "128m",
            "--cpus", "0.50", "--pids-limit", "64", "--ulimit", "nofile=64:64",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true", names["cell_image"],
        ])
        flags["cell"] = True
        cell_policy = _verify_cell(docker.inspect("container", names["cell_container"]), names["network"])
        cell_result = docker.run(["start", "--attach", names["cell_container"]], timeout=90, allowed=frozenset({0, 1, 2}))
        try:
            result_packet = json.loads(cell_result.stdout)
        except json.JSONDecodeError as error:
            raise LiveError("cell_output_not_json") from error
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired as error:
            raise LiveError("broker_did_not_exit") from error
        ledger = contracts.load_object(ledger_path)
        contracts.validate_instance(ATTEMPT_LEDGER_SCHEMA, ledger)
        expected_calls = 1 if mode == "live" else 0
        if ledger.get("status") != "consumed" or ledger.get("provider_calls_consumed") != expected_calls:
            raise LiveError("attempt_ledger_not_consumed")
        events = _read_events(audit_path)
        event_classification = _classify_attempt_events(events, mode=mode)
        if event_classification["terminal_preproof_rejection"]:
            if (
                result_packet.get("status") != "edge_aborted"
                or result_packet.get("reason")
                != event_classification["reason_code"]
                or result_packet.get("broker_status") != 409
            ):
                raise LiveError("cell_terminal_rejection_mismatch")
    finally:
        broker_absent = _terminate(process)
        for enabled, arguments, label in (
            (flags["cell"], ["rm", "--force", names["cell_container"]], "cell"),
            (flags["relay"], ["rm", "--force", names["relay_container"]], "relay"),
            (flags["network"], ["network", "rm", names["network"]], "network"),
            (flags["cell_image"], ["image", "rm", names["cell_image"]], "cell_image"),
            (flags["relay_image"], ["image", "rm", names["relay_image"]], "relay_image"),
        ):
            if enabled:
                try:
                    docker.run(arguments, allowed=frozenset({0, 1}))
                except LiveError:
                    cleanup_errors.append(label)
        if not base_preexisting and docker.exists("image", BASE_IMAGE):
            try:
                docker.run(["image", "rm", BASE_IMAGE], allowed=frozenset({0, 1}))
            except LiveError:
                cleanup_errors.append("base_image")
        try:
            shutil.rmtree(temporary_root)
        except OSError:
            cleanup_errors.append("temporary_root")
    cleanup = {
        "cell_container_absent": not docker.exists("container", names["cell_container"]),
        "relay_container_absent": not docker.exists("container", names["relay_container"]),
        "internal_network_absent": not docker.exists("network", names["network"]),
        "cell_image_absent": not docker.exists("image", names["cell_image"]),
        "relay_image_absent": not docker.exists("image", names["relay_image"]),
        "base_image_state_preserved": docker.exists("image", BASE_IMAGE) if base_preexisting else not docker.exists("image", BASE_IMAGE),
        "temporary_context_absent": not temporary_root.exists(),
        "broker_process_absent": broker_absent,
        "daemon_wide_prune_performed": False,
    }
    cleanup_passed = not cleanup_errors and all(value for key, value in cleanup.items() if key != "daemon_wide_prune_performed")
    if result_packet is None:
        raise LiveError("attempt_result_missing")
    terminal_preproof = event_classification["terminal_preproof_rejection"]
    proofreader = (
        result_packet.get("proofreader")
        if isinstance(result_packet, dict) and not terminal_preproof
        else None
    )
    verdict = (
        "not_reached"
        if terminal_preproof
        else proofreader.get("verdict") if isinstance(proofreader, dict) else None
    )
    reason_code = (
        event_classification["reason_code"]
        if terminal_preproof
        else proofreader.get("reason_code")
        if isinstance(proofreader, dict)
        else None
    )
    correction_eligible = (
        False
        if terminal_preproof
        else proofreader.get("correction_eligible")
        if isinstance(proofreader, dict)
        else False
    )
    admitted = result_packet.get("status") == "completed" and verdict == "admitted"
    attempt_result = (
        "attempt_pass"
        if admitted and cleanup_passed
        else "attempt_terminal_rejection"
        if terminal_preproof and cleanup_passed
        else "attempt_revision_required"
    )
    evidence = {
        "schema_version": "emr4.model_required_bureau_a3_b3.attempt_evidence.v1",
        "result": attempt_result,
        "mode": mode,
        "lane": lane,
        "attempt_id": packet["attempt_id"],
        "attempt_number": attempt_number,
        "provider_contacted": mode == "live",
        "provider_call_count": 1 if mode == "live" else 0,
        "request_binding": {key: packet[key] for key in ("policy_id", "context_hash", "provider_request_hash")},
        "preflight_hash": _file_hash(paths["preflight"]) if preflight is not None else None,
        "proofreader_verdict": verdict,
        "proofreader_reason_code": reason_code,
        "correction_eligible": correction_eligible,
        "release": result_packet.get("release") if admitted else None,
        "provider_metadata": (
            event_classification["provider_metadata"]
            if terminal_preproof
            else result_packet.get("provider_metadata")
            if mode == "live"
            else None
        ),
        "provider_metadata_status": (
            "not_durably_recorded"
            if terminal_preproof
            and event_classification["provider_metadata"] is None
            else "sanitized_allowlist"
            if mode == "live"
            else "provider_free_fixture"
        ),
        "build_context": {
            "repository_root_used": False,
            "temporary_exact_allowlist": True,
            "pinned_base_image": BASE_IMAGE,
            "base_image_pulled_for_attempt": not base_preexisting,
            "source_hashes": build_hashes,
        },
        "network": network_policy,
        "relay_policy": relay_policy,
        "cell_policy": cell_policy,
        "cleanup": cleanup,
        "cleanup_passed": cleanup_passed,
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "credential_or_token_retained": False,
        "product_read_count": 0,
        "database_access_count": 0,
        "command_count": 0,
        "write_count": 0,
        "actuator_count": 0,
    }
    evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
    _write_json(evidence_path, evidence)
    if not cleanup_passed:
        raise LiveError("attempt_cleanup_failed")
    return evidence


def _tranche_evidence(
    *,
    mode: str,
    result_name: str,
    lane_results: list[dict[str, Any]],
    ledger: dict[str, Any],
    review: dict[str, Any] | None,
    combined_pass: bool,
) -> dict[str, Any]:
    evidence = {
        "schema_version": "emr4.model_required_bureau_a3_b3.tranche_evidence.v1",
        "result": result_name,
        "mode": mode,
        "combined_pass": combined_pass,
        "lane_results": lane_results,
        "rayleen_a3_admitted": any(
            item.get("lane") == contracts.LANE_RAYLEEN
            and item.get("proofreader_verdict") == "admitted"
            for item in lane_results
        ),
        "davida_b3_admitted": any(
            item.get("lane") == contracts.LANE_DAVIDA
            and item.get("proofreader_verdict") == "admitted"
            for item in lane_results
        ),
        "davida_b3_started": any(
            item.get("lane") == contracts.LANE_DAVIDA for item in lane_results
        ),
        "candidate_runtime_provider_call_count": ledger[
            "provider_calls_consumed"
        ],
        "source_review_transport_nonzero": mode == "live",
        "source_review_model": review.get("model") if review else None,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "reserved_cost_usd": ledger["reserved_cost_usd"],
        "patient_or_clinical_data_count": 0,
        "product_read_count": 0,
        "database_access_count": 0,
        "command_count": 0,
        "write_count": 0,
        "actuator_count": 0,
        "cloud_or_iam_mutation_count": 0,
        "deployment_count": 0,
        "protected_ref_movement_count": 0,
    }
    evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
    return evidence


def run_tranche(
    *, mode: str, output_path: Path, cost_ledger_path: Path,
    source_review_path: Path | None,
    resume_preflight_blocked_evidence_path: Path | None = None,
) -> dict[str, Any]:
    if output_path.exists():
        raise LiveError("tranche_output_already_exists")
    if resume_preflight_blocked_evidence_path is not None and mode != "live":
        raise LiveError("preflight_resume_live_only")
    lock_path = cost_ledger_path.with_suffix(cost_ledger_path.suffix + ".run.lock")
    try:
        lock_descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise LiveError("tranche_run_already_active") from error
    try:
        if cost_ledger_path.exists():
            if resume_preflight_blocked_evidence_path is None:
                raise LiveError("tranche_output_already_exists")
            ledger = _resume_preflight_blocked_cost_ledger(
                cost_ledger_path=cost_ledger_path,
                blocked_evidence_path=resume_preflight_blocked_evidence_path,
            )
            reserved_rayleen_primary = True
        else:
            if resume_preflight_blocked_evidence_path is not None:
                raise LiveError("preflight_resume_cost_ledger_missing")
            ledger = _initial_cost_ledger()
            _write_json(cost_ledger_path, ledger)
            reserved_rayleen_primary = False
        review = (
            _validate_source_review(source_review_path)
            if mode == "live" and source_review_path
            else None
        )
        if mode == "live" and review is None:
            raise LiveError("source_review_required")
        lane_results: list[dict[str, Any]] = []
        for lane in (contracts.LANE_RAYLEEN, contracts.LANE_DAVIDA):
            correction_of: str | None = None
            correction_reason: str | None = None
            for attempt_number in (1, 2):
                if attempt_number == 2 and correction_reason != "schema_invalid":
                    break
                if (
                    reserved_rayleen_primary
                    and lane == contracts.LANE_RAYLEEN
                    and attempt_number == 1
                ):
                    reserved_rayleen_primary = False
                else:
                    ledger = _reserve_cost(ledger, lane, mode=mode)
                    _write_json(cost_ledger_path, ledger)
                preflight = None
                if mode == "live":
                    preflight = _run_preflight(
                        _attempt_paths(
                            lane, attempt_number, mode=mode
                        )["preflight"]
                    )
                attempt = _run_attempt(
                    lane=lane, mode=mode, attempt_number=attempt_number,
                    correction_of=correction_of,
                    correction_reason_code=correction_reason,
                    preflight=preflight,
                )
                lane_results.append(attempt)
                if mode == "live":
                    ledger = _reconcile_parent_consumption(ledger, lane_results)
                    _write_json(cost_ledger_path, ledger)
                if attempt["proofreader_verdict"] == "admitted":
                    break
                if attempt.get("correction_eligible") is True:
                    correction_of = attempt["attempt_id"]
                    correction_reason = "schema_invalid"
                    continue
                break
            if (
                not lane_results
                or lane_results[-1].get("lane") != lane
                or lane_results[-1].get("proofreader_verdict") != "admitted"
            ):
                if mode != "live":
                    raise LiveError("lane_not_admitted")
                ledger["status"] = "consumed"
                contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
                _write_json(cost_ledger_path, ledger)
                evidence = _tranche_evidence(
                    mode=mode,
                    result_name=(
                        "model_required_bureau_a3_b3_occupied_terminal_rejection"
                    ),
                    lane_results=lane_results,
                    ledger=ledger,
                    review=review,
                    combined_pass=False,
                )
                _write_json(output_path, evidence)
                return evidence
        ledger["status"] = "consumed"
        contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
        _write_json(cost_ledger_path, ledger)
        result_name = (
            "model_required_bureau_a3_b3_provider_free_dry_run_pass"
            if mode == "dry-run"
            else "model_required_bureau_a3_b3_occupied_advisory_rehearsal_pass"
        )
        evidence = _tranche_evidence(
            mode=mode,
            result_name=result_name,
            lane_results=lane_results,
            ledger=ledger,
            review=review,
            combined_pass=True,
        )
        _write_json(output_path, evidence)
        return evidence
    finally:
        os.close(lock_descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    ).stdout.strip()


def _tracked_worktree_clean() -> bool:
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )
    return not status.stdout.strip()


def _paths_match_head(paths: Sequence[Path]) -> bool:
    for path in paths:
        try:
            relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            return False
        if not path.is_file():
            return False
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=False,
        )
        if tracked.returncode != 0:
            return False
        head_blob = subprocess.run(
            ["git", "rev-parse", f"HEAD:{relative}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=False,
        )
        working_blob = subprocess.run(
            ["git", "hash-object", f"--path={relative}", str(path)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=False,
        )
        if (
            head_blob.returncode != 0
            or working_blob.returncode != 0
            or head_blob.stdout.strip() != working_blob.stdout.strip()
        ):
            return False
    return True


def _reconciliation_source_hashes() -> dict[str, str]:
    paths = (
        ROOT / "scripts/model_required_bureau_a3_b3_contracts.py",
        ROOT / "scripts/model_required_bureau_a3_b3_broker.py",
        ROOT / "scripts/model_required_bureau_a3_b3_live.py",
        ROOT / "scripts/model_required_bureau_a3_b3_acceptance.py",
        ROOT / "tests/test_model_required_bureau_a3_b3.py",
        COST_LEDGER_SCHEMA,
        TERMINAL_INTERRUPTION_SCHEMA,
    )
    return {
        path.relative_to(ROOT).as_posix(): _file_hash(path)
        for path in paths
    }


def _historical_source_review(path: Path, *, current_head: str) -> dict[str, Any]:
    review = contracts.load_object(path)
    review_head = review.get("head_before")
    if (
        review.get("status") != "completed"
        or review.get("transport")
        != "antigravity_new_project_bound_readonly_worktree"
        or review.get("model") != "gemini-3.6-flash-high"
        or review.get("reasoning_effort") != "high"
        or review.get("decision") != "pass"
        or not isinstance(review_head, str)
        or review.get("head_after") != review_head
        or review.get("dirty_after") is not False
    ):
        raise LiveError("historical_source_review_not_exact")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", review_head, current_head],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )
    if ancestry.returncode != 0:
        raise LiveError("historical_source_review_not_ancestor")
    return review


def _exact_preflight_evidence(path: Path) -> dict[str, Any]:
    evidence = contracts.load_object(path)
    if (
        evidence.get("result")
        != "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
        or evidence.get("project") != contracts.PROJECT
        or evidence.get("service_account") != contracts.SERVICE_ACCOUNT
        or evidence.get("location") != contracts.LOCATION
        or evidence.get("endpoint_hostname") != contracts.HOSTNAME
        or evidence.get("model_id") != contracts.MODEL
        or evidence.get("provider_prompt_transmitted") is not False
        or evidence.get("model_inference_called") is not False
        or evidence.get("external_state_changed") is not False
        or not isinstance(evidence.get("checks"), dict)
        or not all(evidence["checks"].values())
    ):
        raise LiveError("terminal_reconciliation_preflight_invalid")
    return evidence


def reconcile_terminal_failure(
    *,
    output_path: Path,
    cost_ledger_path: Path,
    source_review_path: Path,
) -> dict[str, Any]:
    canonical_output_path = ARTIFACT_ROOT / "occupied-rehearsal-evidence.json"
    canonical_cost_ledger_path = (
        ARTIFACT_ROOT / "occupied-rehearsal-cost-ledger.json"
    )
    if (
        output_path.resolve() != canonical_output_path.resolve()
        or cost_ledger_path.resolve() != canonical_cost_ledger_path.resolve()
        or source_review_path.resolve() != SOURCE_REVIEW_RECEIPT.resolve()
    ):
        raise LiveError("terminal_reconciliation_path_binding_invalid")
    lock_path = cost_ledger_path.with_suffix(cost_ledger_path.suffix + ".run.lock")
    try:
        lock_descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise LiveError("tranche_run_already_active") from error
    try:
        current_head = _git_head()
        if not _tracked_worktree_clean():
            raise LiveError("terminal_reconciliation_source_not_committed_clean")
        interruption_path = (
            ARTIFACT_ROOT / "occupied-terminal-interruption-evidence.json"
        )
        paths = _attempt_paths(contracts.LANE_RAYLEEN, 1, mode="live")
        authoritative_paths = (
            SOURCE_REVIEW_RECEIPT,
            contracts.RAYLEEN_CONTEXT_PATH,
            CELL_REQUEST_SCHEMA,
            ATTEMPT_LEDGER_SCHEMA,
            COST_LEDGER_SCHEMA,
            BLOCKED_PREFLIGHT_SCHEMA,
            TERMINAL_INTERRUPTION_SCHEMA,
            ARTIFACT_ROOT / "occupied-preflight-blocked-evidence.json",
            interruption_path,
            cost_ledger_path,
            paths["preflight"],
            paths["ledger"],
            paths["audit"],
            ROOT / "scripts/model_required_bureau_a3_b3_contracts.py",
            ROOT / "scripts/model_required_bureau_a3_b3_broker.py",
            ROOT / "scripts/model_required_bureau_a3_b3_live.py",
            ROOT / "scripts/model_required_bureau_a3_b3_acceptance.py",
            ROOT / "tests/test_model_required_bureau_a3_b3.py",
        )
        if not _paths_match_head(authoritative_paths):
            raise LiveError("terminal_reconciliation_inputs_not_exact_head")
        interruption = contracts.load_object(interruption_path)
        contracts.validate_instance(
            TERMINAL_INTERRUPTION_SCHEMA, interruption
        )
        review = _historical_source_review(
            source_review_path, current_head=current_head
        )
        review_head = review["head_before"]
        if review_head != interruption.get("provider_call_source_head"):
            raise LiveError("historical_source_review_head_not_exact")
        context = contracts.load_object(contracts.RAYLEEN_CONTEXT_PATH)
        packet = _request_packet(
            contracts.LANE_RAYLEEN,
            context,
            attempt_number=1,
            correction_of=None,
            correction_reason_code=None,
        )
        for required in (paths["preflight"], paths["ledger"], paths["audit"]):
            if not required.is_file():
                raise LiveError("terminal_reconciliation_artifact_missing")
        _exact_preflight_evidence(paths["preflight"])
        attempt_ledger = contracts.load_object(paths["ledger"])
        contracts.validate_instance(ATTEMPT_LEDGER_SCHEMA, attempt_ledger)
        expected_attempt_ledger = _attempt_ledger(packet, mode="live")
        expected_attempt_ledger["status"] = "consumed"
        expected_attempt_ledger["provider_calls_consumed"] = 1
        if attempt_ledger != expected_attempt_ledger:
            raise LiveError("terminal_reconciliation_attempt_ledger_invalid")
        events = _read_events(paths["audit"])
        classification = _classify_attempt_events(events, mode="live")
        if (
            not classification["terminal_preproof_rejection"]
            or classification["reason_code"] != "provider_content_invalid"
        ):
            raise LiveError("terminal_reconciliation_reason_invalid")
        admitted_event = next(
            event for event in events if event.get("event_type") == "request_admitted"
        )
        admitted_fields = admitted_event.get("fields")
        if not isinstance(admitted_fields, dict) or any(
            admitted_fields.get(key) != packet[key]
            for key in (
                "lane",
                "attempt_id",
                "ledger_id",
                "policy_id",
                "context_hash",
                "provider_request_hash",
            )
        ):
            raise LiveError("terminal_reconciliation_request_binding_invalid")
        permitted_occupied_attempt_paths = {
            paths["preflight"],
            paths["ledger"],
            paths["audit"],
            paths["evidence"],
        }
        observed_occupied_attempt_paths = {
            *ARTIFACT_ROOT.glob("*-attempt-*-occupied-*"),
            *ARTIFACT_ROOT.glob("*-attempt-*-preflight.json"),
        }
        if (
            observed_occupied_attempt_paths
            - permitted_occupied_attempt_paths
        ):
            raise LiveError("terminal_reconciliation_later_attempt_present")

        ledger = contracts.load_object(cost_ledger_path)
        contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
        initial_reserved = _reserve_cost(
            _initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
        )
        final_ledger = json.loads(json.dumps(initial_reserved))
        final_ledger["provider_calls_consumed"] = 1
        final_ledger["status"] = "consumed"
        contracts.validate_instance(COST_LEDGER_SCHEMA, final_ledger)
        if ledger not in (initial_reserved, final_ledger):
            raise LiveError("terminal_reconciliation_parent_ledger_invalid")
        blocked_path = ARTIFACT_ROOT / "occupied-preflight-blocked-evidence.json"
        blocked = contracts.load_object(blocked_path)
        contracts.validate_instance(BLOCKED_PREFLIGHT_SCHEMA, blocked)
        if (
            blocked.get("cost_ledger_sha256")
            != "sha256:303088b2a840bc162ba4f3270bf4a8ec5e09f5ec7469cf3114ae816a795d24f1"
            or (
                ledger == initial_reserved
                and _file_hash(cost_ledger_path) != blocked["cost_ledger_sha256"]
            )
        ):
            raise LiveError("terminal_reconciliation_original_ledger_hash_invalid")

        runtime_absence = _exact_runtime_absence(contracts.LANE_RAYLEEN, 1)
        if not all(runtime_absence.values()):
            raise LiveError("terminal_reconciliation_runtime_residue_present")
        source_hashes = {
            "preflight": _file_hash(paths["preflight"]),
            "attempt_ledger": _file_hash(paths["ledger"]),
            "audit": _file_hash(paths["audit"]),
            "prior_parent_cost_ledger": blocked["cost_ledger_sha256"],
            "blocked_preflight_evidence": _file_hash(blocked_path),
            "terminal_interruption_evidence": _file_hash(interruption_path),
        }
        reconciliation_source_hashes = _reconciliation_source_hashes()
        if (
            interruption.get("reason_code") != "provider_content_invalid"
            or interruption.get("provider_call_count") != 1
            or interruption.get("proofreader_reached") is not False
            or interruption.get("correction_eligible") is not False
            or interruption.get("release_created") is not False
            or interruption.get("davida_b3_started") is not False
            or interruption.get("source_artifact_hashes")
            != {
                "parent_cost_ledger": source_hashes[
                    "prior_parent_cost_ledger"
                ],
                "read_only_preflight": source_hashes["preflight"],
                "attempt_ledger": source_hashes["attempt_ledger"],
                "audit_chain": source_hashes["audit"],
            }
        ):
            raise LiveError("terminal_reconciliation_interruption_invalid")
        attempt_evidence = {
            "schema_version": "emr4.model_required_bureau_a3_b3.attempt_evidence.v1",
            "result": "attempt_terminal_rejection",
            "mode": "live",
            "lane": contracts.LANE_RAYLEEN,
            "attempt_id": packet["attempt_id"],
            "attempt_number": 1,
            "provider_contacted": True,
            "provider_call_count": 1,
            "request_binding": {
                key: packet[key]
                for key in (
                    "policy_id",
                    "context_hash",
                    "provider_request_hash",
                )
            },
            "preflight_hash": source_hashes["preflight"],
            "proofreader_verdict": "not_reached",
            "proofreader_reason_code": "provider_content_invalid",
            "correction_eligible": False,
            "release": None,
            "provider_metadata": None,
            "provider_metadata_status": "not_durably_recorded",
            "current_runtime_absence": {
                **runtime_absence,
                "daemon_wide_prune_performed": False,
            },
            "current_runtime_residue_absent": True,
            "original_attempt_cleanup_evidence_status": (
                "not_durably_recorded_beyond_immutable_interruption_assertion"
            ),
            "reconciled_after_interrupted_harness": True,
            "source_artifact_hashes": source_hashes,
            "raw_prompt_retained": False,
            "raw_provider_response_retained": False,
            "credential_or_token_retained": False,
            "product_read_count": 0,
            "database_access_count": 0,
            "command_count": 0,
            "write_count": 0,
            "actuator_count": 0,
        }
        attempt_evidence["evidence_hash"] = contracts.prefixed_sha256(
            attempt_evidence
        )
        if paths["evidence"].exists():
            if contracts.load_object(paths["evidence"]) != attempt_evidence:
                raise LiveError("terminal_reconciliation_attempt_evidence_drift")
        else:
            _write_json(paths["evidence"], attempt_evidence)

        if ledger == initial_reserved:
            _write_json(cost_ledger_path, final_ledger)
        evidence = _tranche_evidence(
            mode="live",
            result_name="model_required_bureau_a3_b3_occupied_terminal_rejection",
            lane_results=[attempt_evidence],
            ledger=final_ledger,
            review=review,
            combined_pass=False,
        )
        evidence.update(
            {
                "terminal_lane": contracts.LANE_RAYLEEN,
                "terminal_reason_code": "provider_content_invalid",
                "correction_eligible": False,
                "provider_call_source_head": review_head,
                "reconciliation_source_head": current_head,
                "reconciliation_was_provider_free": True,
                "source_artifact_hashes": source_hashes,
                "reconciliation_source_hashes": reconciliation_source_hashes,
            }
        )
        evidence.pop("evidence_hash")
        evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
        if output_path.exists():
            if contracts.load_object(output_path) != evidence:
                raise LiveError("terminal_reconciliation_output_drift")
        else:
            _write_json(output_path, evidence)
        return evidence
    finally:
        os.close(lock_descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("dry-run", "live", "reconcile-terminal"), required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-ledger", type=Path, required=True)
    parser.add_argument("--source-review", type=Path)
    parser.add_argument("--resume-preflight-blocked-evidence", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "reconcile-terminal":
            if args.source_review is None or args.resume_preflight_blocked_evidence:
                raise LiveError("terminal_reconciliation_arguments_invalid")
            evidence = reconcile_terminal_failure(
                output_path=args.output,
                cost_ledger_path=args.cost_ledger,
                source_review_path=args.source_review,
            )
        else:
            evidence = run_tranche(
                mode=args.mode,
                output_path=args.output,
                cost_ledger_path=args.cost_ledger,
                source_review_path=args.source_review,
                resume_preflight_blocked_evidence_path=(
                    args.resume_preflight_blocked_evidence
                ),
            )
    except (LiveError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"result": "model_required_bureau_a3_b3_tranche_blocked", "reason_code": str(error).split(":", 1)[0]}, sort_keys=True))
        return 2
    print(json.dumps({"result": evidence["result"], "provider_call_count": evidence["candidate_runtime_provider_call_count"], "lane_count": len(evidence["lane_results"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
