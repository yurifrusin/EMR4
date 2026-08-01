#!/usr/bin/env python3
"""Run the provider-free real-isolation fixture for the Bureau model text lane."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan


IMAGE = "reception-one-bureau-model-text-lane-cell:v1"
CONTAINER = "reception-one-bureau-model-text-lane-cell-v1"
DOCKERFILE = lane.ARTIFACT_DIR / "Dockerfile"
CELL_SCRIPT = ROOT / "scripts" / "reception_one_bureau_model_text_lane_cell.py"
FIXTURE = lane.FIXTURE_PATH


class IsolationError(RuntimeError):
    """A bounded real-isolation lifecycle failure."""


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(
    executable: str,
    arguments: Sequence[str],
    *,
    timeout: int = 180,
    allowed: frozenset[int] = frozenset({0}),
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            [executable, *arguments],
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
        raise IsolationError("docker_command_failed") from error
    if result.returncode not in allowed:
        raise IsolationError("docker_command_failed:" + arguments[0])
    return result


def exists(docker: str, kind: str, reference: str) -> bool:
    return (
        run_command(
            docker,
            [kind, "inspect", reference],
            allowed=frozenset({0, 1}),
        ).returncode
        == 0
    )


def _squeeze_frame() -> dict[str, Any]:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(
        item for item in document["cases"] if item["case_id"] == "novel-squeeze-in"
    )
    return typed_plan.expand_case(document, case)


def _copy_exact_context(
    destination: Path,
    model_input: dict[str, Any],
    *,
    fixture_path: Path = FIXTURE,
) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    sources = {
        "Dockerfile": DOCKERFILE,
        "cell.py": CELL_SCRIPT,
        "model-output-fixture.json": fixture_path,
    }
    hashes: dict[str, str] = {}
    for target_name, source in sources.items():
        source = source.resolve()
        if not source.is_file() or source.is_symlink():
            raise IsolationError("source_invalid")
        shutil.copy2(source, destination / target_name)
        hashes[source.relative_to(ROOT).as_posix()] = file_hash(source)
    input_path = destination / "model-input.json"
    input_path.write_text(
        json.dumps(model_input, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    hashes["generated:model-input.json"] = file_hash(input_path)
    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual != {
        "Dockerfile",
        "cell.py",
        "model-input.json",
        "model-output-fixture.json",
    }:
        raise IsolationError("context_not_exact")
    return hashes


def _inspect_exact(docker: str) -> dict[str, Any]:
    raw = run_command(docker, ["container", "inspect", CONTAINER]).stdout
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise IsolationError("container_inspect_invalid") from error
    if not isinstance(value, list) or len(value) != 1:
        raise IsolationError("container_inspect_invalid")
    inspected = value[0]
    host = inspected.get("HostConfig", {})
    config = inspected.get("Config", {})
    checks = {
        "non_root_user": config.get("User") == "65532:65532",
        "network_none": host.get("NetworkMode") == "none",
        "read_only_rootfs": host.get("ReadonlyRootfs") is True,
        "capabilities_dropped": host.get("CapDrop") == ["ALL"],
        "no_new_privileges": "no-new-privileges=true"
        in (host.get("SecurityOpt") or []),
        "memory_bounded": host.get("Memory") == 134217728,
        "memory_swap_bounded": host.get("MemorySwap") == 134217728,
        "cpu_bounded": host.get("NanoCpus") == 500000000,
        "pids_bounded": host.get("PidsLimit") == 32,
        "no_mounts": inspected.get("Mounts") == [],
        "no_published_ports": config.get("ExposedPorts") in (None, {}),
        "privileged_false": host.get("Privileged") is False,
    }
    if not all(checks.values()):
        raise IsolationError("container_policy_mismatch")
    return checks


def run_isolation(
    *,
    frame_path: Path | None = None,
    fixture_path: Path = FIXTURE,
) -> dict[str, Any]:
    docker = shutil.which("docker")
    if docker is None:
        raise IsolationError("docker_unavailable")
    if exists(docker, "container", CONTAINER) or exists(docker, "image", IMAGE):
        raise IsolationError("owned_residue_preexisted")

    frame = (
        lane.load_object(frame_path)
        if frame_path is not None
        else _squeeze_frame()
    )
    typed_plan.validate_schema(frame, "input")
    lane.validate_exact(lane.load_object(fixture_path), lane.CANDIDATE_SCHEMA_PATH)
    model_input = lane.build_model_input(frame)
    source_hashes: dict[str, str] = {}
    inspect_checks: dict[str, bool] = {}
    packet: dict[str, Any] | None = None
    cleanup_errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="reception-one-model-cell-") as raw:
        context = Path(raw) / "context"
        source_hashes = _copy_exact_context(
            context,
            model_input,
            fixture_path=fixture_path,
        )
        try:
            run_command(
                docker,
                [
                    "build",
                    "--pull=false",
                    "--network",
                    "none",
                    "--tag",
                    IMAGE,
                    str(context),
                ],
                timeout=240,
            )
            run_command(
                docker,
                [
                    "create",
                    "--name",
                    CONTAINER,
                    "--hostname",
                    "reception-one-model-cell",
                    "--network",
                    "none",
                    "--read-only",
                    "--user",
                    "65532:65532",
                    "--tmpfs",
                    "/tmp:rw,noexec,nosuid,size=8m",  # nosec B108 -- container tmpfs
                    "--memory",
                    "128m",
                    "--memory-swap",
                    "128m",
                    "--cpus",
                    "0.50",
                    "--pids-limit",
                    "32",
                    "--ulimit",
                    "nofile=64:64",
                    "--cap-drop",
                    "ALL",
                    "--security-opt",
                    "no-new-privileges=true",
                    IMAGE,
                ],
            )
            inspect_checks = _inspect_exact(docker)
            result = run_command(
                docker,
                ["start", "--attach", CONTAINER],
                timeout=60,
            )
            try:
                parsed = json.loads(result.stdout)
            except json.JSONDecodeError as error:
                raise IsolationError("cell_output_invalid") from error
            if not isinstance(parsed, dict) or parsed.get("status") != "completed":
                raise IsolationError("cell_not_completed")
            packet = parsed
        finally:
            if exists(docker, "container", CONTAINER):
                result = run_command(
                    docker,
                    ["rm", "--force", CONTAINER],
                    allowed=frozenset({0, 1}),
                )
                if result.returncode != 0:
                    cleanup_errors.append("container_cleanup_failed")
            if exists(docker, "image", IMAGE):
                result = run_command(
                    docker,
                    ["image", "rm", IMAGE],
                    allowed=frozenset({0, 1}),
                )
                if result.returncode != 0:
                    cleanup_errors.append("image_cleanup_failed")

    if packet is None:
        raise IsolationError("cell_packet_missing")
    residue = {
        "container_present": exists(docker, "container", CONTAINER),
        "image_present": exists(docker, "image", IMAGE),
        "temporary_context_present": False,
    }
    if cleanup_errors or any(residue.values()):
        raise IsolationError("cleanup_or_residue_failed")
    candidate = packet.get("candidate")
    if not isinstance(candidate, dict):
        raise IsolationError("candidate_missing")
    review, normalized, _ = lane.proofread_candidate(frame, candidate)
    if review["disposition"] != "admit":
        raise IsolationError("isolated_candidate_not_admitted")
    execution = typed_plan.execute_plan(frame, normalized, review)
    if execution["final_output"]["write_performed"] is not False:
        raise IsolationError("isolated_execution_effect_violation")
    return {
        "schema_version": "reception.one.bureau.model_text_isolation_evidence.v1",
        "result": "reception_one_bureau_model_text_lane_real_isolation_pass",
        "evidence_mode": "authored_synthetic_provider_free_fixture",
        "source_manifest_sha256": lane.canonical_hash(source_hashes),
        "model_input_sha256": lane.canonical_hash(model_input),
        "candidate_sha256": lane.canonical_hash(candidate),
        "normalized_plan_sha256": lane.canonical_hash(normalized),
        "review_disposition": review["disposition"],
        "execution_status": execution["status"],
        "released_proposal_family": execution["final_output"]["proposal_family"],
        "container_policy_checks": inspect_checks,
        "cell_isolation_observation": packet["isolation"],
        "residue": residue,
        "boundary": {
            "provider_calls_performed": 0,
            "credential_reads_performed": 0,
            "api_key_authentication_used": False,
            "network_access_performed": False,
            "database_access_performed": False,
            "appointment_writes_performed": 0,
            "confirmation_performed": False,
            "product_delivery_performed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--frame", type=Path)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    args = parser.parse_args()
    try:
        evidence = run_isolation(
            frame_path=args.frame,
            fixture_path=args.fixture,
        )
    except IsolationError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_bureau_model_text_lane_real_isolation_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
