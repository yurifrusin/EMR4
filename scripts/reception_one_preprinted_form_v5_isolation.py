#!/usr/bin/env python3
"""Provider-free real-isolation rehearsal for both v5 form turns."""

from __future__ import annotations

import argparse
import copy
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

from scripts import reception_one_bureau_model_text_lane as legacy_lane
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_structured_source_plan_language as structured


IMAGES = (
    "reception-one-preprinted-form-v5-turn-1:v1",
    "reception-one-preprinted-form-v5-turn-2:v1",
)
CONTAINERS = (
    "reception-one-preprinted-form-v5-turn-1",
    "reception-one-preprinted-form-v5-turn-2",
)
DOCKERFILE = legacy_lane.ARTIFACT_DIR / "Dockerfile"
CELL_SCRIPT = ROOT / "scripts" / "reception_one_preprinted_form_v5_cell.py"
FRAME = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-extended-proposal-runtime"
    / "occupied-move-frame.json"
)
FIXTURE = structured.ARTIFACT_DIR / "provider-free-program-fixture.json"


class IsolationError(RuntimeError):
    """A bounded two-turn isolation failure."""


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


def _context(
    destination: Path,
    *,
    turn_input: dict[str, Any],
    body: dict[str, Any],
) -> dict[str, str]:
    destination.mkdir(parents=True, exist_ok=False)
    for name, source in {
        "Dockerfile": DOCKERFILE,
        "cell.py": CELL_SCRIPT,
    }.items():
        source = source.resolve()
        if not source.is_file() or source.is_symlink():
            raise IsolationError("source_invalid")
        shutil.copy2(source, destination / name)
    for name, value in {
        "turn-input.json": turn_input,
        "model-form-body.json": body,
    }.items():
        (destination / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual != {
        "Dockerfile",
        "cell.py",
        "turn-input.json",
        "model-form-body.json",
    }:
        raise IsolationError("context_not_exact")
    return {
        path.relative_to(destination).as_posix(): file_hash(path)
        for path in destination.rglob("*")
        if path.is_file()
    }


def _inspect(docker: str, container: str) -> dict[str, bool]:
    raw = run_command(docker, ["container", "inspect", container]).stdout
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


def _run_turn(
    docker: str,
    *,
    index: int,
    context: Path,
) -> tuple[dict[str, Any], dict[str, bool]]:
    image = IMAGES[index - 1]
    container = CONTAINERS[index - 1]
    run_command(
        docker,
        [
            "build",
            "--pull=false",
            "--network",
            "none",
            "--tag",
            image,
            str(context),
        ],
        timeout=240,
    )
    run_command(
        docker,
        [
            "create",
            "--name",
            container,
            "--hostname",
            f"reception-one-preprinted-form-v5-turn-{index}",
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
            image,
        ],
    )
    checks = _inspect(docker, container)
    result = run_command(
        docker,
        ["start", "--attach", container],
        timeout=60,
    )
    try:
        packet = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise IsolationError("cell_output_invalid") from error
    if not isinstance(packet, dict) or packet.get("status") != "completed":
        raise IsolationError("cell_not_completed")
    return packet, checks


def run_isolation() -> dict[str, Any]:
    docker = shutil.which("docker")
    if docker is None:
        raise IsolationError("docker_unavailable")
    if any(
        exists(docker, kind, reference)
        for kind, references in (
            ("container", CONTAINERS),
            ("image", IMAGES),
        )
        for reference in references
    ):
        raise IsolationError("owned_residue_preexisted")

    frame = structured.load_object(FRAME)
    corrected_program = structured.load_object(FIXTURE)
    typed_plan.validate_schema(frame, "input")
    structured.validate_exact(
        corrected_program, structured.PLAN_PROGRAM_SCHEMA_PATH
    )
    corrected_body = preprinted.model_form_body(corrected_program)
    first_body = copy.deepcopy(corrected_body)
    changed = False
    for step in first_body["steps"]:
        for source in step["source_refs"]:
            if source["kind"] != "prior_output":
                continue
            exposed = {
                output["name"]
                for output in structured.operator_table()[
                    first_body["steps"][source["prior_step_index"]][
                        "operator_code"
                    ]
                ]["output_slots"]
            }
            source["prior_output_name"] = next(
                name for name in structured.OUTPUT_NAMES if name not in exposed
            )
            changed = True
            break
        if changed:
            break
    if not changed:
        raise IsolationError("first_turn_defect_not_constructed")
    first_input = preprinted.build_turn_input(frame)
    packets: list[dict[str, Any]] = []
    checks: list[dict[str, bool]] = []
    manifests: list[dict[str, str]] = []
    cleanup_errors: list[str] = []
    with tempfile.TemporaryDirectory(
        prefix="reception-one-preprinted-form-v5-"
    ) as raw:
        root = Path(raw)
        first_context = root / "turn-1"
        manifests.append(
            _context(
                first_context,
                turn_input=first_input,
                body=first_body,
            )
        )
        ticket: dict[str, Any] | None = None
        try:
            packet, inspection = _run_turn(
                docker,
                index=1,
                context=first_context,
            )
            packets.append(packet)
            checks.append(inspection)
            first_program = preprinted.assemble_program(
                packet["model_form_body"]
            )
            evaluation = preprinted.evaluate_program(
                frame,
                first_program,
                turn_code=1,
            )
            ticket = preprinted.build_correction_ticket(
                first_program,
                evaluation,
            )
            second_input = preprinted.build_turn_input(
                frame,
                correction_ticket=ticket,
            )
            second_context = root / "turn-2"
            manifests.append(
                _context(
                    second_context,
                    turn_input=second_input,
                    body=corrected_body,
                )
            )
            packet, inspection = _run_turn(
                docker,
                index=2,
                context=second_context,
            )
            packets.append(packet)
            checks.append(inspection)
        finally:
            for container in CONTAINERS:
                if exists(docker, "container", container):
                    result = run_command(
                        docker,
                        ["rm", "--force", container],
                        allowed=frozenset({0, 1}),
                    )
                    if result.returncode != 0:
                        cleanup_errors.append("container_cleanup_failed")
            for image in IMAGES:
                if exists(docker, "image", image):
                    result = run_command(
                        docker,
                        ["image", "rm", image],
                        allowed=frozenset({0, 1}),
                    )
                    if result.returncode != 0:
                        cleanup_errors.append("image_cleanup_failed")
    if len(packets) != 2 or ticket is None:
        raise IsolationError("two_turn_packets_missing")
    residue = {
        "containers_present": any(
            exists(docker, "container", item) for item in CONTAINERS
        ),
        "images_present": any(exists(docker, "image", item) for item in IMAGES),
        "temporary_context_present": False,
    }
    if cleanup_errors or any(residue.values()):
        raise IsolationError("cleanup_or_residue_failed")
    first_program = preprinted.assemble_program(packets[0]["model_form_body"])
    second_program = preprinted.assemble_program(packets[1]["model_form_body"])
    first_evaluation = preprinted.evaluate_program(
        frame,
        first_program,
        turn_code=1,
    )
    second_evaluation = preprinted.evaluate_program(
        frame,
        second_program,
        turn_code=2,
    )
    if (
        first_evaluation["disposition"] != "revision_required"
        or packets[1]["correction_ticket_sha256"]
        != preprinted.canonical_hash(ticket)
        or second_evaluation["disposition"] != "admit"
    ):
        raise IsolationError("isolated_dialogue_not_admitted")
    execution = typed_plan.execute_plan(
        frame,
        second_evaluation["normalized_plan"],
        second_evaluation["semantic_review"],
    )
    if execution["final_output"]["write_performed"] is not False:
        raise IsolationError("isolated_execution_effect_violation")
    return {
        "schema_version": (
            "reception.one.preprinted_form_v5.isolation_evidence.v1"
        ),
        "result": "reception_one_preprinted_form_v5_real_isolation_pass",
        "evidence_mode": "authored_synthetic_provider_free_two_turn_fixture",
        "source_manifest_sha256": preprinted.canonical_hash(manifests),
        "task_sha256": first_input["task_sha256"],
        "preprinted_fields": preprinted.PREPRINTED_FIELDS,
        "model_authored_fields": list(preprinted.MODEL_AUTHORED_FIELDS),
        "first_model_form_body_sha256": preprinted.canonical_hash(
            packets[0]["model_form_body"]
        ),
        "first_program_sha256": preprinted.canonical_hash(first_program),
        "first_disposition": first_evaluation["disposition"],
        "correction_ticket_sha256": preprinted.canonical_hash(ticket),
        "second_model_form_body_sha256": preprinted.canonical_hash(
            packets[1]["model_form_body"]
        ),
        "second_program_sha256": preprinted.canonical_hash(second_program),
        "second_disposition": second_evaluation["disposition"],
        "normalized_plan_sha256": preprinted.canonical_hash(
            second_evaluation["normalized_plan"]
        ),
        "execution_status": execution["status"],
        "released_proposal_family": execution["final_output"][
            "proposal_family"
        ],
        "container_policy_checks": checks,
        "cell_isolation_observations": [
            packet["isolation"] for packet in packets
        ],
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
            "proofreader_selected_replacement": False,
            "broker_judgement_repair": False,
            "operator_note_product_delivered": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        evidence = run_isolation()
    except IsolationError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_preprinted_form_v5_"
                        "real_isolation_blocked"
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
