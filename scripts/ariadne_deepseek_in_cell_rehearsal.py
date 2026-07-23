"""Build and run one bounded DeepSeek V4 Flash generated-draft rehearsal."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import jsonschema

try:
    import ariadne_bounded_cognitive_work_cell as work_cell
except ModuleNotFoundError:  # Imported as scripts.* by the test suite.
    from scripts import ariadne_bounded_cognitive_work_cell as work_cell


PROTOCOL_ID = "ariadne-deepseek-in-cell-generated-draft-rehearsal"
PASS_RESULT = "ariadne_deepseek_in_cell_generated_draft_rehearsal_pass"
REVISION_RESULT = (
    "ariadne_deepseek_in_cell_generated_draft_rehearsal_revision_required"
)
MODEL_ID = "deepseek-v4-flash"
CLAUDE_CODE_VERSION = "2.1.201"
NODE_IMAGE_TAG = "node:24-bookworm-slim"
BROKER_IMAGE = "emr4/ariadne-deepseek-broker:tranche1"
CELL_IMAGE = "emr4/ariadne-deepseek-cell:tranche1"
BROKER_NAME = "ariadne-deepseek-broker-tranche1"
CELL_NAME = "ariadne-deepseek-cell-tranche1"
NETWORK_NAME = "ariadne-deepseek-internal-tranche1"

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "orchestration" / "continuity" / "ariadne-deepseek-in-cell"
ATTEMPT_PATH = SOURCE_DIR / "attempt.json"
OUTPUT_SCHEMA_PATH = SOURCE_DIR / "output.schema.json"
DOCKERFILE_PATH = SOURCE_DIR / "Dockerfile"
LAUNCHER_PATH = ROOT / "scripts" / "ariadne_deepseek_work_cell_launcher.mjs"
BROKER_PATH = ROOT / "scripts" / "ariadne_deepseek_one_use_broker.mjs"
WORK_CELL_DOCUMENT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-cognitive-work-cell-example.json"
)
LEDGER_PATH = SOURCE_DIR / "single-use-ledger.json"
BUILD_EVIDENCE_PATH = SOURCE_DIR / "image-build-evidence.json"
EVIDENCE_PATH = SOURCE_DIR / "rehearsal-evidence.json"

BUILD_CONTEXT_ALLOWLIST = {
    "Dockerfile": DOCKERFILE_PATH,
    "ariadne_deepseek_work_cell_launcher.mjs": LAUNCHER_PATH,
    "ariadne_deepseek_one_use_broker.mjs": BROKER_PATH,
    "attempt.json": ATTEMPT_PATH,
    "output.schema.json": OUTPUT_SCHEMA_PATH,
}
PORT_ORDER = [
    "port-ux",
    "port-human-review",
    "port-audit",
    "port-orchestrator",
    "port-advisory",
]
FRAME_TYPES = [
    "synthetic-request-scope.v1",
    "principal-scope.v1",
    "patient-candidate-context.v1",
    "practitioner-context.v1",
    "availability-context.v1",
    "evaluated-appointment-policy.v1",
]
PRIMARY_DRAFT_IDS = [
    "draft-ux-primary",
    "draft-human-primary",
    "draft-audit-primary",
    "draft-orchestrator-primary",
    "draft-advisory-primary",
]


class RehearsalError(RuntimeError):
    """Sanitised bounded-rehearsal failure."""

    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalError("json-root-must-be-object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run_command(
    command: list[str],
    *,
    timeout: int = 120,
    environment: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if check and completed.returncode != 0:
        raise RehearsalError(f"command-failed:{command[0]}:{command[1]}")
    return completed


def docker_json(*args: str) -> Any:
    completed = run_command(["docker", *args], timeout=60)
    return json.loads(completed.stdout)


def source_hashes() -> dict[str, str]:
    return {
        name: sha256_bytes(path.read_bytes())
        for name, path in sorted(BUILD_CONTEXT_ALLOWLIST.items())
    }


def _payload_bytes(frame: dict[str, Any]) -> int:
    return len(canonical_json(frame.get("payload", {})).encode("utf-8"))


def validate_static() -> dict[str, Any]:
    missing = [
        str(path.relative_to(ROOT))
        for path in BUILD_CONTEXT_ALLOWLIST.values()
        if not path.is_file()
    ]
    if missing:
        raise RehearsalError("build-context-source-missing")
    attempt = load_json(ATTEMPT_PATH)
    schema = load_json(OUTPUT_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    if attempt.get("attempt_id") != "generated-attempt-001":
        raise RehearsalError("attempt-id-invalid")
    model = attempt.get("model_contract", {})
    if (
        model.get("model_id") != MODEL_ID
        or model.get("claude_code_version") != CLAUDE_CODE_VERSION
        or model.get("tools") != []
        or model.get("fallback_model") is not None
        or model.get("session_persistence") is not False
        or model.get("output_authority") != "draft-only"
    ):
        raise RehearsalError("model-contract-invalid")
    budgets = attempt.get("budgets", {})
    expected_budgets = {
        "maximum_attempts": 1,
        "maximum_provider_calls": 1,
        "maximum_context_frames": 8,
        "maximum_context_payload_bytes": 4096,
        "maximum_prompt_bytes": 32768,
        "maximum_provider_request_bytes": 65536,
        "maximum_provider_output_tokens": 2048,
        "maximum_output_drafts": 5,
        "maximum_output_bytes": 8192,
        "deadline_seconds": 180,
    }
    if budgets != expected_budgets:
        raise RehearsalError("budget-contract-invalid")
    frames = attempt.get("context_frames")
    if not isinstance(frames, list) or len(frames) != 6:
        raise RehearsalError("context-frame-count-invalid")
    if [frame.get("frame_type") for frame in frames] != FRAME_TYPES:
        raise RehearsalError("context-frame-type-order-invalid")
    scope = attempt.get("scope", {})
    for frame in frames:
        if (
            frame.get("practice_id") != scope.get("practice_id")
            or frame.get("principal_id") != scope.get("principal_id")
            or frame.get("correlation_id") != scope.get("correlation_id")
            or frame.get("context_revision") != scope.get("context_revision")
            or frame.get("freshness", {}).get("status") != "current"
        ):
            raise RehearsalError("context-scope-or-freshness-invalid")
    context_payload_bytes = sum(_payload_bytes(frame) for frame in frames)
    if context_payload_bytes > budgets["maximum_context_payload_bytes"]:
        raise RehearsalError("context-payload-byte-budget-exceeded")
    output_contract = attempt.get("output_contract", {})
    if (
        output_contract.get("exact_port_order") != PORT_ORDER
        or output_contract.get("direct_downstream_delivery") is not False
        or output_contract.get("direct_human_gate_delivery") is not False
        or output_contract.get("command_authority") is not False
    ):
        raise RehearsalError("output-contract-invalid")

    attempt_text = json.dumps(attempt, ensure_ascii=False, separators=(",", ":"))
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    prompt = "\n".join(
        [
            "Apply every selection rule to the supplied context and complete the locked five-port form.",
            "Do not copy this instruction into the output.",
            f"ATTEMPT={attempt_text}",
            f"OUTPUT_SCHEMA={schema_text}",
        ]
    )
    prompt_bytes = len(prompt.encode("utf-8"))
    if prompt_bytes > budgets["maximum_prompt_bytes"]:
        raise RehearsalError("compiled-prompt-byte-budget-exceeded")

    forbidden_sources = {
        ".env",
        ".git",
        "AGENTS.md",
        "DEEPSEEK_API_KEY",
    }
    if forbidden_sources.intersection(BUILD_CONTEXT_ALLOWLIST):
        raise RehearsalError("build-context-forbidden-source")
    return {
        "status": "passed",
        "protocol_id": PROTOCOL_ID,
        "context_frame_count": len(frames),
        "context_payload_bytes": context_payload_bytes,
        "compiled_prompt_bytes": prompt_bytes,
        "output_port_count": len(PORT_ORDER),
        "source_hashes": source_hashes(),
    }


def _resolve_node_image() -> str:
    run_command(["docker", "pull", NODE_IMAGE_TAG], timeout=600)
    inspection = docker_json("image", "inspect", NODE_IMAGE_TAG)
    if not isinstance(inspection, list) or len(inspection) != 1:
        raise RehearsalError("node-image-inspection-invalid")
    repo_digests = inspection[0].get("RepoDigests", [])
    digest = next(
        (
            value
            for value in repo_digests
            if isinstance(value, str) and value.startswith("node@sha256:")
        ),
        None,
    )
    if digest is None:
        raise RehearsalError("node-image-repodigest-missing")
    return digest


def _copy_build_context(target: Path) -> None:
    for name, source in BUILD_CONTEXT_ALLOWLIST.items():
        shutil.copy2(source, target / name)
    actual = {path.name for path in target.iterdir() if path.is_file()}
    if actual != set(BUILD_CONTEXT_ALLOWLIST):
        raise RehearsalError("build-context-allowlist-mismatch")


def build_images() -> dict[str, Any]:
    static = validate_static()
    if shutil.which("docker") is None:
        raise RehearsalError("docker-not-found")
    node_image = _resolve_node_image()
    with tempfile.TemporaryDirectory(prefix="ariadne-deepseek-build-") as raw:
        context = Path(raw)
        _copy_build_context(context)
        common = [
            "docker",
            "build",
            "--build-arg",
            f"NODE_IMAGE={node_image}",
            "--file",
            str(context / "Dockerfile"),
        ]
        run_command(
            [
                *common,
                "--target",
                "broker",
                "--tag",
                BROKER_IMAGE,
                str(context),
            ],
            timeout=900,
        )
        run_command(
            [
                *common,
                "--build-arg",
                f"CLAUDE_CODE_VERSION={CLAUDE_CODE_VERSION}",
                "--target",
                "work-cell",
                "--tag",
                CELL_IMAGE,
                str(context),
            ],
            timeout=900,
        )

    broker_inspect = docker_json("image", "inspect", BROKER_IMAGE)[0]
    cell_inspect = docker_json("image", "inspect", CELL_IMAGE)[0]
    evidence = {
        "schema_version": "ariadne.deepseek_in_cell_image_build_evidence.v1",
        "protocol_id": PROTOCOL_ID,
        "status": "passed",
        "build_context_files": sorted(BUILD_CONTEXT_ALLOWLIST),
        "build_context_source_hashes": static["source_hashes"],
        "node_image_resolved": node_image,
        "claude_code_package": "@anthropic-ai/claude-code",
        "claude_code_version": CLAUDE_CODE_VERSION,
        "broker_image": {
            "tag": BROKER_IMAGE,
            "image_id": broker_inspect.get("Id"),
            "role_label": broker_inspect.get("Config", {})
            .get("Labels", {})
            .get("emr4.ariadne.role"),
        },
        "cell_image": {
            "tag": CELL_IMAGE,
            "image_id": cell_inspect.get("Id"),
            "role_label": cell_inspect.get("Config", {})
            .get("Labels", {})
            .get("emr4.ariadne.role"),
            "claude_code_version_label": cell_inspect.get("Config", {})
            .get("Labels", {})
            .get("emr4.ariadne.claude-code-version"),
        },
        "provider_call_performed": False,
        "prompt_transmitted": False,
        "provider_secret_in_image": False,
    }
    if (
        evidence["broker_image"]["role_label"] != "broker"
        or evidence["cell_image"]["role_label"] != "work-cell"
        or evidence["cell_image"]["claude_code_version_label"]
        != CLAUDE_CODE_VERSION
    ):
        raise RehearsalError("built-image-label-invalid")
    write_json(BUILD_EVIDENCE_PATH, evidence)
    return evidence


def _environment_keys(container: dict[str, Any]) -> list[str]:
    values = container.get("Config", {}).get("Env", []) or []
    return sorted(
        item.split("=", 1)[0] for item in values if isinstance(item, str)
    )


def _container_policy(container: dict[str, Any]) -> dict[str, Any]:
    host = container.get("HostConfig", {})
    ports = container.get("NetworkSettings", {}).get("Ports", {}) or {}
    return {
        "user": container.get("Config", {}).get("User"),
        "read_only_root": host.get("ReadonlyRootfs"),
        "cap_drop": sorted(host.get("CapDrop") or []),
        "security_opt": sorted(host.get("SecurityOpt") or []),
        "mount_count": len(container.get("Mounts") or []),
        "published_port_count": sum(
            len(bindings or []) for bindings in ports.values()
        ),
        "network_mode": host.get("NetworkMode"),
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "environment_keys": _environment_keys(container),
    }


def _broker_events() -> list[dict[str, Any]]:
    completed = run_command(
        ["docker", "logs", BROKER_NAME], timeout=30, check=False
    )
    events: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def _wait_for_broker() -> None:
    for _ in range(50):
        events = _broker_events()
        if any(item.get("event") == "broker-ready" for item in events):
            return
        state = docker_json("inspect", BROKER_NAME)[0].get("State", {})
        if state.get("Running") is not True:
            raise RehearsalError("broker-exited-before-ready")
        time.sleep(0.2)
    raise RehearsalError("broker-readiness-timeout")


def _consume_attempt_ledger() -> dict[str, Any]:
    if LEDGER_PATH.exists():
        existing = load_json(LEDGER_PATH)
        if existing.get("state") == "consumed":
            raise RehearsalError("single-use-attempt-already-consumed")
        raise RehearsalError("single-use-ledger-state-invalid")
    ledger = {
        "schema_version": "ariadne.deepseek_in_cell_single_use_ledger.v1",
        "protocol_id": PROTOCOL_ID,
        "attempt_id": "generated-attempt-001",
        "state": "consumed",
        "authority": "yuri-one-authored-synthetic-model-attempt",
        "model_id": MODEL_ID,
        "maximum_provider_calls": 1,
        "retry_authorised": False,
        "consumption_point": "immediately-before-work-cell-model-process-start",
    }
    write_json(LEDGER_PATH, ledger)
    return ledger


def _parse_cell_result(stdout: str) -> dict[str, Any]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RehearsalError("cell-result-line-count-invalid")
    value = json.loads(lines[0])
    if not isinstance(value, dict):
        raise RehearsalError("cell-result-root-invalid")
    return value


def _proofread_generated(drafts: list[dict[str, Any]]) -> dict[str, Any]:
    document = load_json(WORK_CELL_DOCUMENT_PATH)
    by_id = {
        item.get("id"): item
        for item in drafts
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if set(by_id) != set(PRIMARY_DRAFT_IDS):
        raise RehearsalError("generated-draft-id-set-invalid")
    document["draft_frames"] = [
        copy.deepcopy(by_id[item["id"]])
        if item.get("id") in by_id
        else item
        for item in document["draft_frames"]
    ]
    verification = work_cell._compute_verification(document)  # noqa: SLF001
    case = next(
        (
            item
            for item in verification["case_results"]
            if item.get("case_id") == "case-primary-multi-output"
        ),
        None,
    )
    if case is None:
        raise RehearsalError("proofreader-primary-case-missing")
    return {
        "status": case["status"],
        "disposition": case["disposition"],
        "reason_codes": case["reason_codes"],
        "frame_verdicts": [
            {
                "draft_id": item["draft_id"],
                "verdict": item["verdict"],
                "disposition": item["disposition"],
                "reason_codes": item["reason_codes"],
            }
            for item in case["frame_results"]
        ],
        "released_edge_count": len(case["released_edges"]),
        "repair_receipt_count": len(case["repair_receipts"]),
    }


def _usage_estimate(usage: dict[str, Any]) -> dict[str, Any]:
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    estimate = None
    if isinstance(input_tokens, int) and isinstance(output_tokens, int):
        estimate = round(input_tokens * 0.14 / 1_000_000 + output_tokens * 0.28 / 1_000_000, 8)
    return {
        "pricing_observed_date": "2026-07-23",
        "currency": "USD",
        "cache_miss_input_per_million": 0.14,
        "output_per_million": 0.28,
        "conservative_adapter_estimate_usd": estimate,
        "adapter_estimate_authoritative": False,
        "provider_billing_authoritative": True,
    }


def _cleanup_exact() -> dict[str, bool]:
    results: dict[str, bool] = {}
    for label, command in (
        ("cell_removed", ["docker", "rm", "--force", CELL_NAME]),
        ("broker_removed", ["docker", "rm", "--force", BROKER_NAME]),
        ("internal_network_removed", ["docker", "network", "rm", NETWORK_NAME]),
        ("cell_image_tag_removed", ["docker", "image", "rm", CELL_IMAGE]),
        ("broker_image_tag_removed", ["docker", "image", "rm", BROKER_IMAGE]),
    ):
        completed = run_command(command, timeout=60, check=False)
        results[label] = completed.returncode == 0
    return results


def rehearse(*, authorised: bool) -> dict[str, Any]:
    if not authorised:
        raise RehearsalError("provider-call-authorisation-flag-required")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise RehearsalError("deepseek-api-key-not-present")
    static = validate_static()
    build_evidence = load_json(BUILD_EVIDENCE_PATH)
    if build_evidence.get("status") != "passed":
        raise RehearsalError("image-build-evidence-not-passed")
    if LEDGER_PATH.exists():
        raise RehearsalError("single-use-attempt-already-consumed")
    for name in (BROKER_NAME, CELL_NAME):
        existing = run_command(
            ["docker", "container", "inspect", name], timeout=30, check=False
        )
        if existing.returncode == 0:
            raise RehearsalError("target-container-name-already-exists")
    existing_network = run_command(
        ["docker", "network", "inspect", NETWORK_NAME], timeout=30, check=False
    )
    if existing_network.returncode == 0:
        raise RehearsalError("target-network-name-already-exists")

    token = secrets.token_urlsafe(32)
    runtime_environment = os.environ.copy()
    runtime_environment["BROKER_TOKEN"] = token
    cell_result: dict[str, Any] | None = None
    broker_policy: dict[str, Any] | None = None
    cell_policy: dict[str, Any] | None = None
    network_policy: dict[str, Any] | None = None
    broker_events: list[dict[str, Any]] = []
    proofreader: dict[str, Any] | None = None
    schema_status = "not-presented"
    result_reason_codes: list[str] = []
    cleanup: dict[str, bool] = {}
    ledger: dict[str, Any] | None = None
    model_process_started = False

    try:
        run_command(["docker", "network", "create", "--internal", NETWORK_NAME])
        run_command(
            [
                "docker",
                "run",
                "--detach",
                "--name",
                BROKER_NAME,
                "--network",
                NETWORK_NAME,
                "--network-alias",
                "broker",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,nodev,size=33554432",
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
                "--env",
                "BROKER_TOKEN",
                "--env",
                "DEEPSEEK_API_KEY",
                BROKER_IMAGE,
            ],
            environment=runtime_environment,
        )
        run_command(["docker", "network", "connect", "bridge", BROKER_NAME])
        _wait_for_broker()
        run_command(
            [
                "docker",
                "create",
                "--name",
                CELL_NAME,
                "--network",
                NETWORK_NAME,
                "--read-only",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,nodev,size=67108864",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--memory",
                "768m",
                "--memory-swap",
                "768m",
                "--cpus",
                "1",
                "--pids-limit",
                "64",
                "--ulimit",
                "nofile=256:256",
                "--env",
                "BROKER_TOKEN",
                CELL_IMAGE,
            ],
            environment=runtime_environment,
        )

        broker_inspect = docker_json("inspect", BROKER_NAME)[0]
        cell_inspect = docker_json("inspect", CELL_NAME)[0]
        network_inspect = docker_json("network", "inspect", NETWORK_NAME)[0]
        broker_policy = _container_policy(broker_inspect)
        cell_policy = _container_policy(cell_inspect)
        network_policy = {
            "internal": network_inspect.get("Internal"),
            "driver": network_inspect.get("Driver"),
            "container_count": len(network_inspect.get("Containers") or {}),
        }
        if "DEEPSEEK_API_KEY" in cell_policy["environment_keys"]:
            raise RehearsalError("provider-key-present-in-cell")
        if (
            cell_policy["read_only_root"] is not True
            or "ALL" not in cell_policy["cap_drop"]
            or cell_policy["mount_count"] != 0
            or cell_policy["published_port_count"] != 0
            or cell_policy["network_mode"] != NETWORK_NAME
            or network_policy["internal"] is not True
        ):
            raise RehearsalError("work-cell-effective-policy-invalid")
        if (
            "DEEPSEEK_API_KEY" not in broker_policy["environment_keys"]
            or broker_policy["mount_count"] != 0
            or broker_policy["published_port_count"] != 0
        ):
            raise RehearsalError("broker-effective-policy-invalid")

        ledger = _consume_attempt_ledger()
        model_process_started = True
        completed = run_command(
            ["docker", "start", "--attach", CELL_NAME],
            timeout=210,
            check=False,
        )
        try:
            cell_result = _parse_cell_result(completed.stdout)
        except (RehearsalError, json.JSONDecodeError):
            cell_result = {
                "status": "failed",
                "reason_code": "cell-result-invalid",
            }
        broker_events = _broker_events()

        if cell_result.get("status") != "completed":
            result_reason_codes.append(
                str(cell_result.get("reason_code", "cell-attempt-failed"))
            )
        else:
            drafts = cell_result.get("drafts")
            envelope = {"drafts": drafts}
            try:
                jsonschema.Draft202012Validator(
                    load_json(OUTPUT_SCHEMA_PATH)
                ).validate(envelope)
                schema_status = "passed"
            except jsonschema.ValidationError:
                schema_status = "failed"
                result_reason_codes.append("generated-output-schema-invalid")
            if schema_status == "passed" and isinstance(drafts, list):
                proofreader = _proofread_generated(drafts)
                if proofreader["status"] != "passed":
                    result_reason_codes.append("proofreader-rejected-generated-draft")

        starts = [
            item
            for item in broker_events
            if item.get("event") == "provider-call-started"
        ]
        if len(starts) != 1:
            result_reason_codes.append("provider-call-count-not-exactly-one")
    except RehearsalError as error:
        result_reason_codes.append(error.reason_code)
        broker_events = _broker_events()
    finally:
        cleanup = _cleanup_exact()

    cleanup_complete = all(cleanup.values())
    if not cleanup_complete:
        result_reason_codes.append("cleanup-incomplete")
    passed = (
        cell_result is not None
        and cell_result.get("status") == "completed"
        and schema_status == "passed"
        and proofreader is not None
        and proofreader.get("status") == "passed"
        and not result_reason_codes
        and cleanup_complete
    )
    usage = (
        cell_result.get("usage", {})
        if isinstance(cell_result, dict)
        and isinstance(cell_result.get("usage"), dict)
        else {}
    )
    generated_hashes = []
    if isinstance(cell_result, dict) and isinstance(cell_result.get("drafts"), list):
        generated_hashes = [
            {
                "draft_id": draft.get("id"),
                "draft_sha256": sha256_json(draft),
            }
            for draft in cell_result["drafts"]
            if isinstance(draft, dict)
        ]
    sanitised_events = [
        {
            key: value
            for key, value in item.items()
            if key
            in {
                "event",
                "reason_code",
                "provider_call_count",
                "model_id",
                "request_bytes",
                "request_sha256",
                "maximum_output_tokens",
                "token_cap_applied",
                "provider_status",
                "response_bytes",
                "response_sha256",
                "maximum_provider_calls",
                "maximum_request_bytes",
                "allowed_path",
                "listen_port",
            }
        }
        for item in broker_events
    ]
    provider_call_count = sum(
        item.get("event") == "provider-call-started" for item in broker_events
    )
    provider_call_completed = any(
        item.get("event") == "provider-call-completed"
        and item.get("provider_status") == 200
        for item in broker_events
    )
    evidence = {
        "schema_version": "ariadne.deepseek_in_cell_rehearsal_evidence.v1",
        "protocol_id": PROTOCOL_ID,
        "result": PASS_RESULT if passed else REVISION_RESULT,
        "status": "passed" if passed else "revision_required",
        "reason_codes": sorted(set(result_reason_codes)),
        "evidence_label": (
            "live_provider_authored_synthetic_generated_draft_rehearsal"
            if provider_call_count == 1
            else "provider_transport_attempt_authored_synthetic_no_provider_call"
        ),
        "source_hashes": static["source_hashes"],
        "image_build_evidence_sha256": sha256_json(build_evidence),
        "topology": {
            "topology_id": "in_cell_claude_code_remote_provider_broker_v1",
            "model_process_location": "work-cell-container",
            "selected_inference_location": "deepseek-remote-provider",
            "provider_request_forwarded": provider_call_count == 1,
            "provider_inference_completed": provider_call_completed,
            "provider_key_present_in_cell": False,
            "cell_general_internet_access": False,
            "broker_host_ports": 0,
        },
        "model": {
            "provider": "deepseek",
            "provider_declared_model_id": MODEL_ID,
            "immutable_provider_weights_proved": False,
            "transport": "claude_code_bare",
            "claude_code_version": CLAUDE_CODE_VERSION,
        },
        "attempt": {
            "attempt_id": "generated-attempt-001",
            "authority_consumed": ledger is not None,
            "model_process_started": model_process_started,
            "provider_call_count": provider_call_count,
            "retry_authorised": False,
            "launcher_status": (
                cell_result.get("status")
                if isinstance(cell_result, dict)
                else "not-started"
            ),
            "launcher_reason_code": (
                cell_result.get("reason_code")
                if isinstance(cell_result, dict)
                else None
            ),
            "prompt_sha256": (
                cell_result.get("prompt_sha256")
                if isinstance(cell_result, dict)
                else None
            ),
            "prompt_bytes": (
                cell_result.get("prompt_bytes")
                if isinstance(cell_result, dict)
                else None
            ),
            "generated_output_sha256": (
                cell_result.get("generated_output_sha256")
                if isinstance(cell_result, dict)
                else None
            ),
            "generated_output_bytes": (
                cell_result.get("generated_output_bytes")
                if isinstance(cell_result, dict)
                else None
            ),
            "generated_draft_count": (
                cell_result.get("generated_draft_count")
                if isinstance(cell_result, dict)
                else None
            ),
        },
        "broker_events": sanitised_events,
        "usage": usage,
        "cost_context": _usage_estimate(usage),
        "generated_draft_hashes": generated_hashes,
        "generated_draft_bodies_committed": False,
        "raw_prompt_committed": False,
        "raw_provider_response_committed": False,
        "chain_of_thought_committed": False,
        "schema_validation": schema_status,
        "proofreader": proofreader,
        "effective_policy": {
            "broker": broker_policy,
            "work_cell": cell_policy,
            "internal_network": network_policy,
        },
        "cleanup": cleanup,
        "product_connections": {
            "postgresql": False,
            "graphql": False,
            "rest_openapi": False,
            "product_api": False,
            "event_feed": False,
            "mailbox": False,
            "human_action": False,
            "command": False,
        },
        "claim_limits": [
            "one-provider-labelled-model-attempt",
            "authored-synthetic-context-only",
            "no-immutable-provider-weight-claim",
            "no-general-model-quality-claim",
            "no-product-runtime-claim",
            "no-command-or-autonomous-action-claim",
        ],
    }
    write_json(EVIDENCE_PATH, evidence)
    return evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded Ariadne DeepSeek in-cell rehearsal."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("build")
    rehearse_parser = subparsers.add_parser("rehearse")
    rehearse_parser.add_argument(
        "--authorize-provider-call",
        action="store_true",
        help="Consume the single authorised model attempt.",
    )
    subparsers.add_parser("trace")
    return parser


def public_summary(value: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "status",
        "result",
        "protocol_id",
        "context_frame_count",
        "context_payload_bytes",
        "compiled_prompt_bytes",
        "output_port_count",
        "node_image_resolved",
        "claude_code_version",
    )
    return {key: value[key] for key in keys if key in value}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == "validate":
            result = validate_static()
        elif args.action == "build":
            result = build_images()
        elif args.action == "rehearse":
            result = rehearse(authorised=args.authorize_provider_call)
        else:
            result = load_json(EVIDENCE_PATH)
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.SchemaError,
        RehearsalError,
        subprocess.TimeoutExpired,
    ) as error:
        reason = (
            error.reason_code
            if isinstance(error, RehearsalError)
            else "bounded-rehearsal-operation-failed"
        )
        print(
            json.dumps({"status": "failed", "reason_code": reason}),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(public_summary(result), sort_keys=True))
    return 0 if result.get("status") == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
