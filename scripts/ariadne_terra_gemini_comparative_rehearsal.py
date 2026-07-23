from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import jsonschema

try:
    import ariadne_bounded_cognitive_work_cell as work_cell
except ModuleNotFoundError:
    from scripts import ariadne_bounded_cognitive_work_cell as work_cell


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ID = "ariadne-terra-gemini-comparative-rehearsal"
SOURCE_DIR = (
    ROOT / "orchestration" / "continuity" / "ariadne-terra-gemini-comparison"
)
PRIOR_DIR = ROOT / "orchestration" / "continuity" / "ariadne-deepseek-in-cell"
MANIFEST_PATH = SOURCE_DIR / "comparison-manifest.json"
TERRA_AMENDMENT_PATH = SOURCE_DIR / "terra-only-amendment.json"
TWO_LANE_RESTORATION_PATH = SOURCE_DIR / "two-lane-restoration.json"
FRESH_ATTEMPT_PATH = SOURCE_DIR / "fresh-attempt-002.json"
PROVIDER_SCHEMA_PATH = SOURCE_DIR / "provider-output.schema.json"
DOCKERFILE_PATH = SOURCE_DIR / "Dockerfile"
SOURCE_ATTEMPT_PATH = PRIOR_DIR / "attempt.json"
FULL_SCHEMA_PATH = PRIOR_DIR / "output.schema.json"
LAUNCHER_PATH = ROOT / "scripts" / "ariadne_comparative_work_cell_launcher.mjs"
BROKER_PATH = ROOT / "scripts" / "ariadne_comparative_one_use_broker.mjs"
WORK_CELL_DOCUMENT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-cognitive-work-cell-example.json"
)
PREFLIGHT_EVIDENCE_PATH = SOURCE_DIR / "preflight-evidence.json"
COMPARISON_EVIDENCE_PATH = SOURCE_DIR / "comparison-evidence.json"
TERRA_ONLY_EVIDENCE_PATH = SOURCE_DIR / "terra-only-evidence.json"
FRESH_PREFLIGHT_EVIDENCE_PATH = (
    SOURCE_DIR / "attempt-002-preflight-evidence.json"
)
FRESH_COMPARISON_EVIDENCE_PATH = (
    SOURCE_DIR / "attempt-002-comparison-evidence.json"
)
TERRA_LEDGER_PATH = SOURCE_DIR / "terra-single-use-ledger.json"
GEMINI_LEDGER_PATH = SOURCE_DIR / "gemini-single-use-ledger.json"
FRESH_TERRA_LEDGER_PATH = (
    SOURCE_DIR / "terra-attempt-002-single-use-ledger.json"
)
FRESH_GEMINI_LEDGER_PATH = (
    SOURCE_DIR / "gemini-attempt-002-single-use-ledger.json"
)
NODE_IMAGE = "node:24-bookworm-slim"
IMAGE_TAGS = {
    "terra": {
        "broker": "emr4/ariadne-comparative-terra-broker:attempt2",
        "cell": "emr4/ariadne-comparative-terra-cell:attempt2",
    },
    "gemini": {
        "broker": "emr4/ariadne-comparative-gemini-broker:attempt2",
        "cell": "emr4/ariadne-comparative-gemini-cell:attempt2",
    },
}
PRIMARY_DRAFT_IDS = {
    "draft-ux-primary",
    "draft-human-primary",
    "draft-audit-primary",
    "draft-orchestrator-primary",
    "draft-advisory-primary",
}
PUBLIC_EVENT_FIELDS = {
    "event",
    "lane_id",
    "provider",
    "model_id",
    "provider_call_count",
    "provider_status",
    "request_bytes",
    "request_sha256",
    "response_bytes",
    "response_sha256",
    "maximum_output_tokens",
    "reason_code",
}


class RehearsalError(RuntimeError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalError("json-root-invalid")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def js_json(value: Any) -> str:
    # All sealed inputs are ASCII and retain insertion order after json.loads.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def run_command(
    command: list[str],
    *,
    timeout: int = 120,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    # Fixed argv assembled from sealed policy; no shell or user command input.
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        suffix = command[1] if len(command) > 1 else "unknown"
        raise RehearsalError(f"command-failed:{command[0]}:{suffix}")
    return completed


def docker_json(*arguments: str) -> Any:
    completed = run_command(["docker", *arguments], timeout=60)
    return json.loads(completed.stdout)


def shared_task() -> dict[str, Any]:
    source = load_json(SOURCE_ATTEMPT_PATH)
    source.pop("model_contract", None)
    source["schema_version"] = "ariadne.provider_neutral_comparison_task.v1"
    return source


def provider_neutral_full_schema() -> dict[str, Any]:
    schema = load_json(FULL_SCHEMA_PATH)
    schema["$id"] = (
        "https://emr4.local/schemas/"
        "ariadne-provider-neutral-work-cell-output.schema.json"
    )
    schema["title"] = "Ariadne Provider-Neutral Work-Cell Draft Envelope"
    return schema


def prompt_material() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    task = shared_task()
    full_schema = provider_neutral_full_schema()
    provider_schema = load_json(PROVIDER_SCHEMA_PATH)
    system_prompt = manifest["system_prompt"]
    prompt = "\n".join(
        [
            *manifest["task_prompt_prefix"],
            f"TASK={js_json(task)}",
            f"FULL_OUTPUT_SCHEMA={js_json(full_schema)}",
        ]
    )
    task_bytes = (json.dumps(task, indent=2) + "\n").encode()
    provider_schema_minified = js_json(provider_schema).encode()
    return {
        "task": task,
        "task_bytes": task_bytes,
        "full_schema": full_schema,
        "provider_schema": provider_schema,
        "system_prompt": system_prompt,
        "prompt": prompt,
        "hashes": {
            "shared_task_sha256": sha256_bytes(task_bytes),
            "full_output_schema_sha256": sha256_bytes(
                (json.dumps(full_schema, indent=2) + "\n").encode()
            ),
            "provider_output_schema_sha256": sha256_bytes(
                provider_schema_minified
            ),
            "system_prompt_sha256": sha256_bytes(system_prompt.encode()),
            "prompt_sha256": sha256_bytes(prompt.encode()),
        },
    }


def source_hashes() -> dict[str, str]:
    paths = {
        "Dockerfile": DOCKERFILE_PATH,
        "ariadne_comparative_one_use_broker.mjs": BROKER_PATH,
        "ariadne_comparative_work_cell_launcher.mjs": LAUNCHER_PATH,
        "comparison-manifest.json": MANIFEST_PATH,
        "provider-output.schema.json": PROVIDER_SCHEMA_PATH,
        "source-attempt.json": SOURCE_ATTEMPT_PATH,
        "full-output.schema.json": FULL_SCHEMA_PATH,
    }
    return {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}


def validate_static() -> dict[str, Any]:
    for path in (
        MANIFEST_PATH,
        TERRA_AMENDMENT_PATH,
        TWO_LANE_RESTORATION_PATH,
        FRESH_ATTEMPT_PATH,
        PROVIDER_SCHEMA_PATH,
        DOCKERFILE_PATH,
        SOURCE_ATTEMPT_PATH,
        FULL_SCHEMA_PATH,
        LAUNCHER_PATH,
        BROKER_PATH,
        WORK_CELL_DOCUMENT_PATH,
    ):
        if not path.is_file():
            raise RehearsalError("required-source-missing")
    manifest = load_json(MANIFEST_PATH)
    if manifest.get("protocol_id") != PROTOCOL_ID:
        raise RehearsalError("protocol-id-invalid")
    if (
        sha256_bytes(SOURCE_ATTEMPT_PATH.read_bytes())
        != manifest["shared_task"]["source_sha256"]
        or sha256_bytes(FULL_SCHEMA_PATH.read_bytes())
        != manifest["full_output_schema"]["source_sha256"]
    ):
        raise RehearsalError("referenced-source-hash-mismatch")
    task = shared_task()
    if (
        "model_contract" in task
        or task.get("attempt_id") != "generated-attempt-001"
        or len(task.get("context_frames", [])) != 6
        or any(
            not str(frame.get("authority_label", "")).startswith(
                ("staff-", "authenticated-", "fixture-")
            )
            for frame in task["context_frames"]
        )
    ):
        raise RehearsalError("shared-task-projection-invalid")
    if [lane.get("lane_id") for lane in manifest.get("lanes", [])] != [
        "terra",
        "gemini",
    ]:
        raise RehearsalError("lane-order-invalid")
    if [
        lane.get("model_id") for lane in manifest["lanes"]
    ] != ["gpt-5.6-terra", "gemini-3.5-flash"]:
        raise RehearsalError("model-allowlist-invalid")
    amendment = load_json(TERRA_AMENDMENT_PATH)
    if (
        amendment.get("amendment_id") != "terra-only-2026-07-24"
        or amendment.get("authority")
        != "yuri-explicit-terra-only-live-rehearsal"
        or amendment.get("lane", {}).get("lane_id") != "terra"
        or amendment.get("lane", {}).get("model_id") != "gpt-5.6-terra"
        or amendment.get("lane", {}).get("maximum_provider_calls") != 1
        or amendment.get("lane", {}).get("retry") is not False
        or amendment.get("lane", {}).get("fallback") is not False
        or amendment.get("gemini", {}).get("excluded") is not True
        or amendment.get("gemini", {}).get("provider_call_permitted") is not False
        or amendment.get("gemini", {}).get("ledger_consumption_permitted")
        is not False
    ):
        raise RehearsalError("terra-only-amendment-invalid")
    restoration = load_json(TWO_LANE_RESTORATION_PATH)
    if (
        restoration.get("restoration_id")
        != "two-lane-restoration-2026-07-24"
        or restoration.get("authority")
        != "yuri-explicit-return-to-both-models"
        or restoration.get("status") != "active_before_consumption"
        or restoration.get("run_order") != ["terra", "gemini"]
        or restoration.get("both_credentials_required_before_terra") is not True
        or restoration.get("terra_cleanup_required_before_gemini") is not True
        or restoration.get("retry") is not False
        or restoration.get("fallback") is not False
        or restoration.get("cross_model_input") is not False
    ):
        raise RehearsalError("two-lane-restoration-invalid")
    fresh_attempt = load_json(FRESH_ATTEMPT_PATH)
    if (
        fresh_attempt.get("runtime_attempt_id")
        != "comparative-runtime-attempt-002"
        or fresh_attempt.get("authority")
        != "yuri-explicit-fresh-two-lane-attempt-after-local-correction"
        or fresh_attempt.get("status") != "authorised_preattempt"
        or fresh_attempt.get("run_order") != ["terra", "gemini"]
        or fresh_attempt.get("required_correction", {}).get(
            "five_sealed_hashes_must_match"
        )
        is not True
        or fresh_attempt.get("retry") is not False
        or fresh_attempt.get("fallback") is not False
        or fresh_attempt.get("cross_model_input") is not False
    ):
        raise RehearsalError("fresh-attempt-authority-invalid")
    budgets = manifest.get("budgets", {})
    if (
        budgets.get("maximum_attempts_per_lane") != 1
        or budgets.get("maximum_provider_calls_per_lane") != 1
        or budgets.get("maximum_provider_output_tokens") != 2048
        or manifest.get("sequence_policy", {}).get("retry") is not False
        or manifest.get("sequence_policy", {}).get("fallback") is not False
        or manifest.get("sequence_policy", {}).get("voting") is not False
        or manifest.get("sequence_policy", {}).get("cross_model_input") is not False
    ):
        raise RehearsalError("budget-or-sequence-policy-invalid")
    provider_schema = load_json(PROVIDER_SCHEMA_PATH)
    full_schema = load_json(FULL_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(provider_schema)
    jsonschema.Draft202012Validator.check_schema(full_schema)
    material = prompt_material()
    prompt_bytes = len(material["prompt"].encode())
    if prompt_bytes > budgets["maximum_prompt_bytes"]:
        raise RehearsalError("compiled-prompt-byte-budget-exceeded")
    for lane, ledger_path in (
        ("terra", TERRA_LEDGER_PATH),
        ("gemini", GEMINI_LEDGER_PATH),
        ("terra", FRESH_TERRA_LEDGER_PATH),
        ("gemini", FRESH_GEMINI_LEDGER_PATH),
    ):
        ledger = load_json(ledger_path)
        if (
            ledger.get("lane_id") != lane
            or ledger.get("state") not in {"available", "consumed"}
            or ledger.get("retry_authorised") is not False
        ):
            raise RehearsalError("single-use-ledger-invalid")
    return {
        "status": "passed",
        "protocol_id": PROTOCOL_ID,
        "context_frame_count": 6,
        "prompt_bytes": prompt_bytes,
        "shared_hashes": material["hashes"],
        "source_hashes": source_hashes(),
        "provider_call_performed": False,
        "prompt_transmitted": False,
    }


def _copy_build_context(target: Path) -> None:
    material = prompt_material()
    shutil.copy2(DOCKERFILE_PATH, target / "Dockerfile")
    shutil.copy2(BROKER_PATH, target / "ariadne_comparative_one_use_broker.mjs")
    shutil.copy2(
        LAUNCHER_PATH, target / "ariadne_comparative_work_cell_launcher.mjs"
    )
    shutil.copy2(MANIFEST_PATH, target / "comparison-manifest.json")
    shutil.copy2(PROVIDER_SCHEMA_PATH, target / "provider-output.schema.json")
    (target / "full-output.schema.json").write_bytes(
        (json.dumps(material["full_schema"], indent=2) + "\n").encode("utf-8")
    )
    (target / "shared-task.json").write_bytes(material["task_bytes"])
    expected = {
        "Dockerfile",
        "ariadne_comparative_one_use_broker.mjs",
        "ariadne_comparative_work_cell_launcher.mjs",
        "comparison-manifest.json",
        "provider-output.schema.json",
        "full-output.schema.json",
        "shared-task.json",
    }
    if {path.name for path in target.iterdir()} != expected:
        raise RehearsalError("build-context-allowlist-invalid")


def build_images() -> dict[str, Any]:
    static = validate_static()
    if shutil.which("docker") is None:
        raise RehearsalError("docker-not-found")
    run_command(["docker", "pull", NODE_IMAGE], timeout=600)
    inspection = docker_json("image", "inspect", NODE_IMAGE)
    digest = next(
        (
            item
            for item in inspection[0].get("RepoDigests", [])
            if item.startswith("node@sha256:")
        ),
        None,
    )
    if digest is None:
        raise RehearsalError("node-image-digest-missing")
    with tempfile.TemporaryDirectory(prefix="ariadne-comparison-build-") as raw:
        context = Path(raw)
        _copy_build_context(context)
        for role, target in (("broker", "broker"), ("cell", "work-cell")):
            run_command(
                [
                    "docker",
                    "build",
                    "--build-arg",
                    f"NODE_IMAGE={digest}",
                    "--target",
                    target,
                    "--tag",
                    IMAGE_TAGS["terra"][role],
                    str(context),
                ],
                timeout=900,
            )
            run_command(
                [
                    "docker",
                    "tag",
                    IMAGE_TAGS["terra"][role],
                    IMAGE_TAGS["gemini"][role],
                ]
            )
    evidence = {
        "status": "passed",
        "node_image_resolved": digest,
        "build_context_files": [
            "Dockerfile",
            "ariadne_comparative_one_use_broker.mjs",
            "ariadne_comparative_work_cell_launcher.mjs",
            "comparison-manifest.json",
            "provider-output.schema.json",
            "full-output.schema.json",
            "shared-task.json",
        ],
        "source_hashes": static["source_hashes"],
        "image_ids": {
            lane: {
                role: docker_json("image", "inspect", tag)[0].get("Id")
                for role, tag in tags.items()
            }
            for lane, tags in IMAGE_TAGS.items()
        },
        "provider_secret_in_image": False,
        "provider_call_performed": False,
        "prompt_transmitted": False,
    }
    return evidence


def _secret_file(directory: Path, name: str, value: str) -> Path:
    path = directory / name
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)
    return path


def _mount(source: Path, destination: str) -> str:
    return f"type=bind,src={source.resolve()},dst={destination},readonly"


def _container_policy(value: dict[str, Any]) -> dict[str, Any]:
    host = value.get("HostConfig", {})
    ports = value.get("NetworkSettings", {}).get("Ports", {}) or {}
    return {
        "user": value.get("Config", {}).get("User"),
        "read_only_root": host.get("ReadonlyRootfs"),
        "cap_drop": sorted(host.get("CapDrop") or []),
        "security_opt": sorted(host.get("SecurityOpt") or []),
        "mounts": sorted(
            [
                {
                "type": mount.get("Type"),
                "destination": mount.get("Destination"),
                "read_only": not bool(mount.get("RW")),
                }
                for mount in value.get("Mounts", [])
            ],
            key=lambda item: str(item["destination"]),
        ),
        "published_port_count": sum(len(bindings or []) for bindings in ports.values()),
        "network_mode": host.get("NetworkMode"),
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "environment_keys": sorted(
            item.split("=", 1)[0]
            for item in value.get("Config", {}).get("Env", [])
            if isinstance(item, str)
        ),
    }


def _names(lane: str, suffix: str) -> dict[str, str]:
    return {
        "network": f"ariadne-comparison-{lane}-{suffix}",
        "broker": f"ariadne-comparison-{lane}-broker-{suffix}",
        "cell": f"ariadne-comparison-{lane}-cell-{suffix}",
    }


def _cleanup(names: dict[str, str], *, remove_images: bool, lane: str) -> dict[str, bool]:
    commands = {
        "cell_removed": ["docker", "rm", "--force", names["cell"]],
        "broker_removed": ["docker", "rm", "--force", names["broker"]],
        "network_removed": ["docker", "network", "rm", names["network"]],
    }
    if remove_images:
        commands.update(
            {
                "cell_image_tag_removed": [
                    "docker",
                    "image",
                    "rm",
                    IMAGE_TAGS[lane]["cell"],
                ],
                "broker_image_tag_removed": [
                    "docker",
                    "image",
                    "rm",
                    IMAGE_TAGS[lane]["broker"],
                ],
            }
        )
    return {
        key: run_command(command, timeout=60, check=False).returncode == 0
        for key, command in commands.items()
    }


def _start_skeleton(
    lane: str,
    names: dict[str, str],
    secrets_dir: Path,
    *,
    provider_key: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    material = prompt_material()
    broker_token = _secret_file(
        secrets_dir, f"{lane}-broker-token", secrets.token_urlsafe(32)
    )
    key_file = _secret_file(secrets_dir, f"{lane}-provider-key", provider_key)
    run_command(["docker", "network", "create", "--internal", names["network"]])
    broker_command = [
        "docker",
        "run",
        "--detach",
        "--name",
        names["broker"],
        "--network",
        names["network"],
        "--network-alias",
        "broker",
        "--read-only",
        "--tmpfs",
        # Container-internal memory-only filesystem, not a host temp path.
        "/tmp:rw,noexec,nosuid,nodev,size=33554432",  # nosec B108
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--memory",
        "256m",
        "--memory-swap",
        "256m",
        "--cpus",
        "0.5",
        "--pids-limit",
        "32",
        "--ulimit",
        "nofile=256:256",
        "--mount",
        _mount(broker_token, "/run/secrets/broker_token"),
        "--mount",
        _mount(key_file, "/run/secrets/provider_key"),
        "--env",
        f"ARIADNE_LANE_ID={lane}",
    ]
    for key, value in material["hashes"].items():
        broker_command.extend(["--env", f"EXPECTED_{key.upper()}={value}"])
    broker_command.append(IMAGE_TAGS[lane]["broker"])
    run_command(broker_command)
    run_command(["docker", "network", "connect", "bridge", names["broker"]])
    for _ in range(50):
        events = _broker_events(names["broker"])
        if any(event.get("event") == "broker-ready" for event in events):
            break
        state = docker_json("inspect", names["broker"])[0].get("State", {})
        if state.get("Running") is not True:
            raise RehearsalError("broker-exited-before-ready")
        time.sleep(0.2)
    else:
        raise RehearsalError("broker-readiness-timeout")
    run_command(
        [
            "docker",
            "create",
            "--name",
            names["cell"],
            "--network",
            names["network"],
            "--read-only",
            "--tmpfs",
            # Container-internal memory-only filesystem, not a host temp path.
            "/tmp:rw,noexec,nosuid,nodev,size=67108864",  # nosec B108
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--memory",
            "256m",
            "--memory-swap",
            "256m",
            "--cpus",
            "0.5",
            "--pids-limit",
            "32",
            "--ulimit",
            "nofile=256:256",
            "--mount",
            _mount(broker_token, "/run/secrets/broker_token"),
            IMAGE_TAGS[lane]["cell"],
        ]
    )
    broker = docker_json("inspect", names["broker"])[0]
    cell = docker_json("inspect", names["cell"])[0]
    network = docker_json("network", "inspect", names["network"])[0]
    return (
        _container_policy(broker),
        _container_policy(cell),
        {
            "internal": network.get("Internal"),
            "driver": network.get("Driver"),
            "container_count": len(network.get("Containers") or {}),
        },
    )


def _assert_policy(
    broker: dict[str, Any], cell: dict[str, Any], network: dict[str, Any]
) -> None:
    if (
        cell["user"] != "node"
        or cell["read_only_root"] is not True
        or "ALL" not in cell["cap_drop"]
        or "no-new-privileges" not in cell["security_opt"]
        or cell["published_port_count"] != 0
        or network["internal"] is not True
        or any(
            item in cell["environment_keys"]
            for item in ("OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY")
        )
    ):
        raise RehearsalError("work-cell-effective-policy-invalid")
    if (
        broker["user"] != "node"
        or broker["read_only_root"] is not True
        or "ALL" not in broker["cap_drop"]
        or broker["published_port_count"] != 0
        or "provider_key" not in str(broker["mounts"])
        or "provider_key" in str(cell["mounts"])
    ):
        raise RehearsalError("broker-effective-policy-invalid")


def preflight(
    *,
    evidence_path: Path = PREFLIGHT_EVIDENCE_PATH,
    name_suffix: str = "preflight",
) -> dict[str, Any]:
    static = validate_static()
    build = build_images()
    lane_policies: dict[str, Any] = {}
    cleanup: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="ariadne-comparison-preflight-") as raw:
        secrets_dir = Path(raw)
        for lane in ("terra", "gemini"):
            names = _names(lane, name_suffix)
            try:
                broker, cell, network = _start_skeleton(
                    lane,
                    names,
                    secrets_dir,
                    provider_key=f"synthetic-non-provider-secret-{lane}",
                )
                _assert_policy(broker, cell, network)
                events = _broker_events(names["broker"])
                if any(event.get("event") == "provider-call-started" for event in events):
                    raise RehearsalError("provider-call-during-preflight")
                lane_policies[lane] = {
                    "broker": broker,
                    "cell": cell,
                    "network": network,
                    "broker_events": [
                        {key: value for key, value in event.items() if key in PUBLIC_EVENT_FIELDS}
                        for event in events
                    ],
                }
            finally:
                cleanup[lane] = _cleanup(
                    names, remove_images=False, lane=lane
                )
    passed = all(all(values.values()) for values in cleanup.values())
    if not passed:
        raise RehearsalError("preflight-cleanup-incomplete")
    credentials = {
        "terra": bool(os.environ.get("OPENAI_API_KEY")),
        "gemini": bool(os.environ.get("GEMINI_API_KEY")),
    }
    evidence = {
        "schema_version": "ariadne.terra_gemini_preflight_evidence.v1",
        "protocol_id": PROTOCOL_ID,
        "status": "passed",
        "static": static,
        "build": build,
        "lane_policies": lane_policies,
        "cleanup": cleanup,
        "credential_gates": {
            "both_present": all(credentials.values()),
            "lane_presence": credentials,
            "credential_values_recorded": False,
        },
        "provider_call_performed": False,
        "prompt_transmitted": False,
    }
    write_json(evidence_path, evidence)
    return evidence


def _broker_events(container_name: str) -> list[dict[str, Any]]:
    completed = run_command(
        ["docker", "logs", container_name], timeout=30, check=False
    )
    events = []
    for line in completed.stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def _consume_ledger(
    lane: str, ledger_path: Path | None = None
) -> dict[str, Any]:
    path = ledger_path or (
        TERRA_LEDGER_PATH if lane == "terra" else GEMINI_LEDGER_PATH
    )
    ledger = load_json(path)
    if ledger.get("state") != "available":
        raise RehearsalError(f"{lane}-authority-not-available")
    ledger.update(
        {
            "state": "consumed",
            "consumption_point": "immediately-before-work-cell-start",
            "retry_authorised": False,
        }
    )
    write_json(path, ledger)
    return ledger


def _proofread(drafts: list[dict[str, Any]]) -> dict[str, Any]:
    document = load_json(WORK_CELL_DOCUMENT_PATH)
    by_id = {
        draft.get("id"): draft
        for draft in drafts
        if isinstance(draft, dict) and isinstance(draft.get("id"), str)
    }
    if set(by_id) != PRIMARY_DRAFT_IDS:
        raise RehearsalError("generated-draft-id-set-invalid")
    document["draft_frames"] = [
        copy.deepcopy(by_id[item["id"]])
        if item.get("id") in by_id
        else item
        for item in document["draft_frames"]
    ]
    verification = work_cell._compute_verification(document)  # noqa: SLF001
    case = next(
        item
        for item in verification["case_results"]
        if item.get("case_id") == "case-primary-multi-output"
    )
    return {
        "status": case["status"],
        "disposition": case["disposition"],
        "reason_codes": case["reason_codes"],
        "released_edge_count": len(case["released_edges"]),
        "repair_receipt_count": len(case["repair_receipts"]),
        "frame_verdicts": [
            {
                "draft_id": item["draft_id"],
                "verdict": item["verdict"],
                "disposition": item["disposition"],
                "reason_codes": item["reason_codes"],
            }
            for item in case["frame_results"]
        ],
    }


def _parse_cell(stdout: str) -> dict[str, Any]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RehearsalError("cell-result-line-count-invalid")
    value = json.loads(lines[0])
    if not isinstance(value, dict):
        raise RehearsalError("cell-result-invalid")
    return value


def _lane_price(lane: str, usage: dict[str, Any]) -> dict[str, Any]:
    manifest_lane = next(
        item for item in load_json(MANIFEST_PATH)["lanes"] if item["lane_id"] == lane
    )
    if lane == "terra":
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
    else:
        input_tokens = usage.get("promptTokenCount")
        candidate_tokens = usage.get("candidatesTokenCount")
        thought_tokens = usage.get("thoughtsTokenCount", 0)
        output_tokens = (
            candidate_tokens + thought_tokens
            if isinstance(candidate_tokens, int)
            and isinstance(thought_tokens, int)
            else None
        )
    estimate = None
    if isinstance(input_tokens, int) and isinstance(output_tokens, int):
        estimate = round(
            input_tokens * manifest_lane["input_per_million_usd"] / 1_000_000
            + output_tokens
            * manifest_lane["output_per_million_usd"]
            / 1_000_000,
            8,
        )
    return {
        "currency": "USD",
        "pricing_observed_date": "2026-07-24",
        "input_per_million": manifest_lane["input_per_million_usd"],
        "output_per_million": manifest_lane["output_per_million_usd"],
        "estimated_cost_usd": estimate,
        "estimate_authoritative": False,
        "provider_billing_authoritative": True,
    }


def _run_lane(
    lane: str,
    provider_key: str,
    *,
    ledger_path: Path | None = None,
    name_suffix: str = "live",
) -> dict[str, Any]:
    names = _names(lane, name_suffix)
    reason_codes: list[str] = []
    cell_result: dict[str, Any] | None = None
    proofreader: dict[str, Any] | None = None
    schema_status = "not-presented"
    provider_schema_status = "not-presented"
    broker_policy = None
    cell_policy = None
    network_policy = None
    ledger = None
    events: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix=f"ariadne-{lane}-live-") as raw:
        try:
            broker_policy, cell_policy, network_policy = _start_skeleton(
                lane, names, Path(raw), provider_key=provider_key
            )
            _assert_policy(broker_policy, cell_policy, network_policy)
            ledger = _consume_ledger(lane, ledger_path)
            completed = run_command(
                ["docker", "start", "--attach", names["cell"]],
                timeout=210,
                check=False,
            )
            try:
                cell_result = _parse_cell(completed.stdout)
            except (RehearsalError, json.JSONDecodeError):
                cell_result = {"status": "failed", "reason_code": "cell-result-invalid"}
            events = _broker_events(names["broker"])
            if cell_result.get("status") != "completed":
                reason_codes.append(
                    str(cell_result.get("reason_code", "cell-attempt-failed"))
                )
            else:
                envelope = {"drafts": cell_result.get("drafts")}
                try:
                    jsonschema.Draft202012Validator(
                        load_json(PROVIDER_SCHEMA_PATH)
                    ).validate(envelope)
                    provider_schema_status = "passed"
                except jsonschema.ValidationError:
                    provider_schema_status = "failed"
                    reason_codes.append("provider-schema-invalid")
                try:
                    jsonschema.Draft202012Validator(
                        load_json(FULL_SCHEMA_PATH)
                    ).validate(envelope)
                    schema_status = "passed"
                except jsonschema.ValidationError:
                    schema_status = "failed"
                    reason_codes.append("full-schema-invalid")
                if schema_status == "passed":
                    proofreader = _proofread(cell_result["drafts"])
                    if proofreader["status"] != "passed":
                        reason_codes.append("proofreader-rejected")
            starts = [
                event for event in events if event.get("event") == "provider-call-started"
            ]
            if len(starts) != 1:
                reason_codes.append("provider-call-count-not-exactly-one")
        except RehearsalError as error:
            reason_codes.append(error.reason_code)
            events = _broker_events(names["broker"])
        finally:
            cleanup = _cleanup(names, remove_images=True, lane=lane)
    if not all(cleanup.values()):
        reason_codes.append("cleanup-incomplete")
    drafts = cell_result.get("drafts", []) if isinstance(cell_result, dict) else []
    usage = (
        cell_result.get("usage", {})
        if isinstance(cell_result, dict) and isinstance(cell_result.get("usage"), dict)
        else {}
    )
    return {
        "lane_id": lane,
        "status": "passed" if not reason_codes else "revision_required",
        "reason_codes": sorted(set(reason_codes)),
        "ledger": ledger,
        "shared_hashes": {
            key: cell_result.get(key)
            for key in (
                "shared_task_sha256",
                "full_output_schema_sha256",
                "provider_output_schema_sha256",
                "system_prompt_sha256",
                "prompt_sha256",
            )
        }
        if isinstance(cell_result, dict)
        else {},
        "prompt_bytes": cell_result.get("prompt_bytes")
        if isinstance(cell_result, dict)
        else None,
        "generated_output_sha256": cell_result.get("generated_output_sha256")
        if isinstance(cell_result, dict)
        else None,
        "generated_output_bytes": cell_result.get("generated_output_bytes")
        if isinstance(cell_result, dict)
        else None,
        "generated_draft_count": len(drafts) if isinstance(drafts, list) else 0,
        "draft_hashes": [
            {
                "draft_id": draft.get("id"),
                "draft_sha256": sha256_bytes(canonical_json(draft).encode()),
            }
            for draft in drafts
            if isinstance(draft, dict)
        ],
        "provider_schema_status": provider_schema_status,
        "full_schema_status": schema_status,
        "proofreader": proofreader,
        "usage": usage,
        "cost_estimate": _lane_price(lane, usage),
        "container_policy": {
            "broker": broker_policy,
            "cell": cell_policy,
            "network": network_policy,
        },
        "broker_events": [
            {key: value for key, value in event.items() if key in PUBLIC_EVENT_FIELDS}
            for event in events
        ],
        "cleanup": cleanup,
        "raw_prompt_recorded": False,
        "raw_provider_response_recorded": False,
        "draft_payload_recorded": False,
        "provider_secret_recorded": False,
    }


def run_live(*, authorised: bool) -> dict[str, Any]:
    if not authorised:
        raise RehearsalError("explicit-authorisation-flag-required")
    restoration = load_json(TWO_LANE_RESTORATION_PATH)
    if (
        restoration.get("status") != "active_before_consumption"
        or restoration.get("run_order") != ["terra", "gemini"]
        or restoration.get("both_credentials_required_before_terra") is not True
    ):
        raise RehearsalError("two-lane-restoration-invalid")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not openai_key or not gemini_key:
        raise RehearsalError("both-provider-credentials-required-before-consumption")
    preflight_evidence = load_json(PREFLIGHT_EVIDENCE_PATH)
    if preflight_evidence.get("status") != "passed":
        raise RehearsalError("preflight-not-passed")
    for lane, ledger_path in (
        ("terra", TERRA_LEDGER_PATH),
        ("gemini", GEMINI_LEDGER_PATH),
    ):
        if load_json(ledger_path).get("state") != "available":
            raise RehearsalError("lane-authority-not-available")

    terra = _run_lane("terra", openai_key)
    terra_boundary_stop = (
        not all(terra["cleanup"].values())
        or any(
            code
            in {
                "work-cell-effective-policy-invalid",
                "broker-effective-policy-invalid",
                "sealed-request-mismatch",
                "referenced-source-hash-mismatch",
                "cleanup-incomplete",
            }
            for code in terra["reason_codes"]
        )
    )
    if terra_boundary_stop:
        gemini = {
            "lane_id": "gemini",
            "status": "suppressed",
            "reason_codes": ["terra-boundary-stop"],
            "provider_call_performed": False,
            "authority_consumed": False,
        }
    else:
        gemini = _run_lane("gemini", gemini_key)

    shared_hash_match = (
        terra.get("shared_hashes") == gemini.get("shared_hashes")
        if gemini.get("status") != "suppressed"
        else False
    )
    passed = (
        terra.get("status") == "passed"
        and gemini.get("status") == "passed"
        and shared_hash_match
    )
    evidence = {
        "schema_version": "ariadne.terra_gemini_comparison_evidence.v1",
        "protocol_id": PROTOCOL_ID,
        "result": (
            "ariadne_terra_gemini_comparative_rehearsal_pass"
            if passed
            else "ariadne_terra_gemini_comparative_rehearsal_revision_required"
        ),
        "run_order": ["terra", "gemini"],
        "shared_hash_match": shared_hash_match,
        "cross_model_input": False,
        "voting": False,
        "retry_performed": False,
        "fallback_performed": False,
        "lanes": {"terra": terra, "gemini": gemini},
        "raw_prompt_recorded": False,
        "raw_provider_response_recorded": False,
        "draft_payload_recorded": False,
        "provider_secret_recorded": False,
        "product_or_database_access": False,
        "downstream_delivery": False,
    }
    write_json(COMPARISON_EVIDENCE_PATH, evidence)
    return evidence


def run_terra_only(*, authorised: bool) -> dict[str, Any]:
    if not authorised:
        raise RehearsalError("explicit-terra-authorisation-flag-required")
    amendment = load_json(TERRA_AMENDMENT_PATH)
    if (
        amendment.get("status") != "active"
        or amendment.get("authority")
        != "yuri-explicit-terra-only-live-rehearsal"
        or amendment.get("gemini", {}).get("excluded") is not True
        or amendment.get("gemini", {}).get("ledger_consumption_permitted")
        is not False
    ):
        raise RehearsalError("terra-only-amendment-invalid")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        raise RehearsalError("openai-credential-required-before-consumption")
    preflight_evidence = load_json(PREFLIGHT_EVIDENCE_PATH)
    if (
        preflight_evidence.get("status") != "passed"
        or preflight_evidence.get("provider_call_performed") is not False
        or preflight_evidence.get("prompt_transmitted") is not False
    ):
        raise RehearsalError("preflight-not-passed")
    if load_json(TERRA_LEDGER_PATH).get("state") != "available":
        raise RehearsalError("terra-authority-not-available")
    if load_json(GEMINI_LEDGER_PATH).get("state") != "available":
        raise RehearsalError("gemini-authority-not-available-before-terra-run")

    terra = _run_lane("terra", openai_key)
    gemini_ledger = load_json(GEMINI_LEDGER_PATH)
    gemini_preserved = (
        gemini_ledger.get("state") == "available"
        and gemini_ledger.get("retry_authorised") is False
    )
    if not gemini_preserved:
        terra["reason_codes"] = sorted(
            set([*terra["reason_codes"], "gemini-authority-not-preserved"])
        )
        terra["status"] = "revision_required"
    passed = terra.get("status") == "passed" and gemini_preserved
    evidence = {
        "schema_version": "ariadne.terra_only_rehearsal_evidence.v1",
        "protocol_id": PROTOCOL_ID,
        "amendment_id": amendment["amendment_id"],
        "result": (
            "ariadne_terra_only_rehearsal_pass"
            if passed
            else "ariadne_terra_only_rehearsal_revision_required"
        ),
        "reasoning_level": "high",
        "terra": terra,
        "gemini": {
            "status": "excluded",
            "ledger_state": gemini_ledger.get("state"),
            "authority_consumed": False,
            "credential_checked": False,
            "broker_started": False,
            "work_cell_started": False,
            "prompt_transmitted": False,
            "provider_call_performed": False,
        },
        "retry_performed": False,
        "fallback_performed": False,
        "raw_prompt_recorded": False,
        "raw_provider_response_recorded": False,
        "draft_payload_recorded": False,
        "provider_secret_recorded": False,
        "product_or_database_access": False,
        "downstream_delivery": False,
    }
    write_json(TERRA_ONLY_EVIDENCE_PATH, evidence)
    return evidence


def run_fresh_attempt(*, authorised: bool) -> dict[str, Any]:
    if not authorised:
        raise RehearsalError("explicit-fresh-attempt-authorisation-required")
    authority = load_json(FRESH_ATTEMPT_PATH)
    if (
        authority.get("status") != "authorised_preattempt"
        or authority.get("runtime_attempt_id")
        != "comparative-runtime-attempt-002"
        or authority.get("run_order") != ["terra", "gemini"]
        or authority.get("retry") is not False
        or authority.get("fallback") is not False
    ):
        raise RehearsalError("fresh-attempt-authority-invalid")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not openai_key or not gemini_key:
        raise RehearsalError(
            "both-provider-credentials-required-before-fresh-consumption"
        )
    preflight_evidence = load_json(FRESH_PREFLIGHT_EVIDENCE_PATH)
    if (
        preflight_evidence.get("status") != "passed"
        or preflight_evidence.get("provider_call_performed") is not False
        or preflight_evidence.get("prompt_transmitted") is not False
        or preflight_evidence.get("credential_gates", {}).get("both_present")
        is not True
    ):
        raise RehearsalError("fresh-preflight-not-passed")
    for ledger_path in (
        FRESH_TERRA_LEDGER_PATH,
        FRESH_GEMINI_LEDGER_PATH,
    ):
        if load_json(ledger_path).get("state") != "available":
            raise RehearsalError("fresh-lane-authority-not-available")

    terra = _run_lane(
        "terra",
        openai_key,
        ledger_path=FRESH_TERRA_LEDGER_PATH,
        name_suffix="attempt2-live",
    )
    terra_boundary_stop = (
        not all(terra["cleanup"].values())
        or any(
            code
            in {
                "work-cell-effective-policy-invalid",
                "broker-effective-policy-invalid",
                "sealed-request-mismatch",
                "referenced-source-hash-mismatch",
                "cleanup-incomplete",
            }
            for code in terra["reason_codes"]
        )
    )
    if terra_boundary_stop:
        gemini = {
            "lane_id": "gemini",
            "status": "suppressed",
            "reason_codes": ["terra-boundary-stop"],
            "provider_call_performed": False,
            "authority_consumed": False,
        }
    else:
        gemini = _run_lane(
            "gemini",
            gemini_key,
            ledger_path=FRESH_GEMINI_LEDGER_PATH,
            name_suffix="attempt2-live",
        )
    shared_hash_match = (
        terra.get("shared_hashes") == gemini.get("shared_hashes")
        if gemini.get("status") != "suppressed"
        else False
    )
    passed = (
        terra.get("status") == "passed"
        and gemini.get("status") == "passed"
        and shared_hash_match
    )
    evidence = {
        "schema_version": "ariadne.terra_gemini_comparison_evidence.v2",
        "protocol_id": PROTOCOL_ID,
        "runtime_attempt_id": "comparative-runtime-attempt-002",
        "result": (
            "ariadne_terra_gemini_comparative_rehearsal_attempt2_pass"
            if passed
            else "ariadne_terra_gemini_comparative_rehearsal_attempt2_revision_required"
        ),
        "run_order": ["terra", "gemini"],
        "shared_hash_match": shared_hash_match,
        "cross_model_input": False,
        "voting": False,
        "retry_performed": False,
        "fallback_performed": False,
        "lanes": {"terra": terra, "gemini": gemini},
        "raw_prompt_recorded": False,
        "raw_provider_response_recorded": False,
        "draft_payload_recorded": False,
        "provider_secret_recorded": False,
        "product_or_database_access": False,
        "downstream_delivery": False,
    }
    write_json(FRESH_COMPARISON_EVIDENCE_PATH, evidence)
    return evidence


def public_summary(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("schema_version") == "ariadne.terra_gemini_comparison_evidence.v2":
        return {
            "result": value["result"],
            "shared_hash_match": value["shared_hash_match"],
            "lane_statuses": {
                key: lane.get("status") for key, lane in value["lanes"].items()
            },
        }
    if value.get("schema_version") == "ariadne.terra_only_rehearsal_evidence.v1":
        return {
            "result": value["result"],
            "terra_status": value["terra"]["status"],
            "terra_reason_codes": value["terra"]["reason_codes"],
            "gemini_ledger_state": value["gemini"]["ledger_state"],
            "gemini_provider_call_performed": value["gemini"][
                "provider_call_performed"
            ],
        }
    if "result" in value:
        return {
            "result": value["result"],
            "shared_hash_match": value["shared_hash_match"],
            "lane_statuses": {
                key: lane.get("status") for key, lane in value["lanes"].items()
            },
        }
    return {
        "status": value.get("status"),
        "protocol_id": value.get("protocol_id"),
        "provider_call_performed": value.get("provider_call_performed"),
        "prompt_transmitted": value.get("prompt_transmitted"),
        "credential_gates": value.get("credential_gates"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("preflight")
    subparsers.add_parser("preflight-fresh")
    run = subparsers.add_parser("run")
    run.add_argument("--authorised", action="store_true")
    run_terra = subparsers.add_parser("run-terra")
    run_terra.add_argument("--authorised", action="store_true")
    run_fresh = subparsers.add_parser("run-fresh")
    run_fresh.add_argument("--authorised", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "validate":
            result = validate_static()
        elif arguments.command == "preflight":
            result = preflight()
        elif arguments.command == "preflight-fresh":
            result = preflight(
                evidence_path=FRESH_PREFLIGHT_EVIDENCE_PATH,
                name_suffix="attempt2-preflight",
            )
        elif arguments.command == "run":
            result = run_live(authorised=arguments.authorised)
        elif arguments.command == "run-terra":
            result = run_terra_only(authorised=arguments.authorised)
        else:
            result = run_fresh_attempt(authorised=arguments.authorised)
    except RehearsalError as error:
        print(json.dumps({"status": "failed", "reason_code": error.reason_code}))
        return 2
    print(json.dumps(public_summary(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
