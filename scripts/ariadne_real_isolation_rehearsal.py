#!/usr/bin/env python3
"""Run one fixed, disposable Ariadne real-isolation rehearsal."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol, Sequence


SCHEMA_VERSION = "ariadne.real_isolation_rehearsal.v1"
EVIDENCE_VERSION = "ariadne.real_isolation_rehearsal_evidence.v1"
RESULT = "ariadne_real_isolation_rehearsal_pass"
MANIFEST_RELATIVE = Path(
    "orchestration/continuity/ariadne-real-isolation-rehearsal-manifest.json"
)
BASE_REFERENCE = (
    "docker.io/library/python@sha256:"
    "a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322"
)
BASE_INDEX_DIGEST = (
    "sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322"
)
PLATFORM_MANIFEST_DIGEST = (
    "sha256:9381e50cc82f4279b949fcd2d2f5e57cf97b1da2399eb956502364ceea2f4e83"
)
PLATFORM_MANIFEST_REFERENCE = (
    "docker.io/library/python@" + PLATFORM_MANIFEST_DIGEST
)
SOURCE_REVISION = "3362634339580d3232e65a66dd5a36c47ae7ff14"
SOURCE_URL = "https://github.com/docker-library/python.git"
SOURCE_CREATED = "2026-04-17T00:30:54Z"
DERIVED_IMAGE = "ariadne-real-isolation-rehearsal:v1"
CONTAINER_NAME = "ariadne-real-isolation-rehearsal-v1"
CONTAINER_HOSTNAME = "ariadne-rehearsal"
EXPECTED_CONTEXT_PATHS = (
    "orchestration/continuity/ariadne-real-isolation/Dockerfile",
    "scripts/ariadne_real_isolation_payload.py",
    "scripts/ariadne_scripted_cognitive_work_cell_rehearsal.py",
    "scripts/ariadne_bounded_cognitive_work_cell.py",
    "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-example.json",
    "orchestration/continuity/ariadne-bounded-cognitive-work-cell-example.json",
    "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-evidence.json",
    "docs/ariadne-scripted-cognitive-work-cell-rehearsal-plan.md",
    "docs/ariadne-scripted-cognitive-work-cell-rehearsal-design.md",
    "docs/security/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-threat-model-delta.md",
    "docs/ariadne-bounded-cognitive-work-cell-protocol-closeout.md",
    "docs/ariadne-bounded-cognitive-work-cell-protocol-design.md",
    "docs/ariadne-bounded-cognitive-work-cell-protocol-plan.md",
    "docs/security/ariadne-bounded-cognitive-work-cell-threat-model-delta.md",
)
EXPECTED_IMAGE_ENVIRONMENT = (
    "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG=C.UTF-8",
    "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
    "PYTHON_VERSION=3.12.13",
    "PYTHON_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONUNBUFFERED=1",
)
REQUIRED_IMAGE_LABELS = {
    "org.opencontainers.image.title": "Ariadne Real-Isolation Rehearsal",
    "org.opencontainers.image.description": (
        "Disposable authored-synthetic isolation rehearsal"
    ),
    "org.opencontainers.image.source": SOURCE_URL,
    "org.opencontainers.image.revision": SOURCE_REVISION,
    "org.opencontainers.image.base.name": BASE_REFERENCE,
    "ariadne.rehearsal.id": CONTAINER_NAME,
}
REQUIRED_CLOSED_CONNECTIONS = (
    "adaptive-agent",
    "appointment-command",
    "database",
    "event-feed",
    "human-gate-runtime",
    "live-mailbox",
    "model",
    "network-egress",
    "persistence",
    "product-api",
    "provider",
    "secret",
    "writable-input",
)


class RealIsolationError(RuntimeError):
    """Raised when the bounded lifecycle fails closed."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    def run(
        self,
        arguments: Sequence[str],
        *,
        timeout: int = 120,
        allowed_returncodes: frozenset[int] = frozenset({0}),
    ) -> CommandResult: ...


class DockerClient:
    """Invoke only fixed Docker argument arrays without a shell."""

    def __init__(self, repo_root: Path) -> None:
        executable = shutil.which("docker")
        if executable is None:
            raise RealIsolationError("docker_unavailable")
        self.executable = executable
        self.repo_root = repo_root

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
                cwd=self.repo_root,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RealIsolationError("docker_command_failed") from error
        result = CommandResult(
            completed.returncode, completed.stdout, completed.stderr
        )
        if result.returncode not in allowed_returncodes:
            raise RealIsolationError("docker_command_failed")
        return result


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RealIsolationError("fixed_json_unreadable") from error
    if not isinstance(value, dict):
        raise RealIsolationError("fixed_json_not_object")
    return value


def _safe_relative_path(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def validate_manifest(repo_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    manifest_path = repo_root / MANIFEST_RELATIVE
    manifest = _load_object(manifest_path)
    expected_top_level = {
        "schema_version",
        "rehearsal_id",
        "result",
        "evidence_label",
        "authority",
        "base_image",
        "derived_image",
        "build_context",
        "container",
        "resources",
        "cleanup",
        "closed_connections",
    }
    if set(manifest) != expected_top_level:
        raise RealIsolationError("manifest_shape_mismatch")
    if manifest.get("schema_version") != "ariadne.real_isolation_manifest.v1":
        raise RealIsolationError("manifest_version_mismatch")
    if manifest.get("rehearsal_id") != CONTAINER_NAME:
        raise RealIsolationError("manifest_identity_mismatch")
    if manifest.get("result") != RESULT:
        raise RealIsolationError("manifest_result_mismatch")
    authority = manifest.get("authority")
    if authority != {
        "one_container_run": True,
        "adaptive_agent_attached": False,
        "generated_drafts": False,
        "product_connections": False,
        "command_authority": False,
    }:
        raise RealIsolationError("manifest_authority_mismatch")
    base = manifest.get("base_image", {})
    expected_base = {
        "observed_tag": "python:3.12.13-alpine3.22",
        "reference": BASE_REFERENCE,
        "index_digest": BASE_INDEX_DIGEST,
        "platform": "linux/amd64",
        "platform_manifest_digest": PLATFORM_MANIFEST_DIGEST,
        "source": SOURCE_URL,
        "source_revision": SOURCE_REVISION,
        "created": SOURCE_CREATED,
    }
    if base != expected_base:
        raise RealIsolationError("manifest_base_image_mismatch")
    derived = manifest.get("derived_image", {})
    if derived != {
        "tag": DERIVED_IMAGE,
        "dockerfile": EXPECTED_CONTEXT_PATHS[0],
        "working_dir": "/workspace",
        "user": "65532:65532",
        "entrypoint": [
            "python",
            "/workspace/scripts/ariadne_real_isolation_payload.py",
        ],
        "environment": list(EXPECTED_IMAGE_ENVIRONMENT),
    }:
        raise RealIsolationError("manifest_derived_image_mismatch")
    if manifest.get("closed_connections") != list(REQUIRED_CLOSED_CONNECTIONS):
        raise RealIsolationError("manifest_closed_connections_mismatch")

    context = manifest.get("build_context", {})
    if (
        context.get("kind") != "temporary_exact_allowlist"
        or context.get("repository_root_is_context") is not False
        or context.get("manifest_path") != MANIFEST_RELATIVE.as_posix()
    ):
        raise RealIsolationError("manifest_context_policy_mismatch")
    entries = context.get("allowlist")
    if not isinstance(entries, list):
        raise RealIsolationError("manifest_allowlist_invalid")
    if [entry.get("path") for entry in entries if isinstance(entry, dict)] != list(
        EXPECTED_CONTEXT_PATHS
    ):
        raise RealIsolationError("manifest_allowlist_paths_mismatch")
    observed: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise RealIsolationError("manifest_allowlist_entry_invalid")
        relative = entry["path"]
        if not isinstance(relative, str) or not _safe_relative_path(relative):
            raise RealIsolationError("manifest_allowlist_path_unsafe")
        path = repo_root / Path(relative)
        if not path.is_file() or path.is_symlink():
            raise RealIsolationError("manifest_allowlisted_source_invalid")
        observed[relative] = file_sha256(path)
        if observed[relative] != entry["sha256"]:
            raise RealIsolationError("manifest_allowlisted_source_hash_mismatch")
    _validate_dockerfile(repo_root / Path(EXPECTED_CONTEXT_PATHS[0]))
    _validate_policy_manifest(manifest)
    return manifest, observed


def _validate_dockerfile(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines or lines[0] != f"FROM {BASE_REFERENCE}":
        raise RealIsolationError("dockerfile_base_mismatch")
    instructions = [line.split(maxsplit=1)[0].upper() for line in lines]
    forbidden = {
        "ADD",
        "ARG",
        "CMD",
        "EXPOSE",
        "HEALTHCHECK",
        "ONBUILD",
        "RUN",
        "SHELL",
        "STOPSIGNAL",
        "VOLUME",
    }
    if forbidden.intersection(instructions):
        raise RealIsolationError("dockerfile_instruction_forbidden")
    if instructions.count("FROM") != 1 or instructions.count("COPY") != 1:
        raise RealIsolationError("dockerfile_instruction_count_mismatch")
    if lines[-2:] != [
        "USER 65532:65532",
        'ENTRYPOINT ["python", "/workspace/scripts/ariadne_real_isolation_payload.py"]',
    ]:
        raise RealIsolationError("dockerfile_terminal_config_mismatch")


def _validate_policy_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("container") != {
        "name": CONTAINER_NAME,
        "hostname": CONTAINER_HOSTNAME,
        "network_mode": "none",
        "read_only_rootfs": True,
        "user": "65532:65532",
        "cap_drop": ["ALL"],
        "cap_add": [],
        "security_opt": ["no-new-privileges=true"],
        "privileged": False,
        "mounts": [],
        "published_ports": [],
        "host_environment_forwarded": False,
        "secrets": [],
        "restart_policy": "no",
    }:
        raise RealIsolationError("manifest_container_policy_mismatch")
    if manifest.get("resources") != {
        "memory_bytes": 134217728,
        "memory_swap_bytes": 134217728,
        "nano_cpus": 500000000,
        "pids_limit": 32,
        "nofile_soft": 64,
        "nofile_hard": 64,
    }:
        raise RealIsolationError("manifest_resource_policy_mismatch")
    if manifest.get("cleanup") != {
        "remove_container": True,
        "remove_derived_image": True,
        "remove_base_reference_if_acquired": True,
        "remove_temporary_context": True,
        "daemon_wide_prune": False,
        "possible_unreferenced_layer_cache": True,
    }:
        raise RealIsolationError("manifest_cleanup_policy_mismatch")


def create_context(
    repo_root: Path,
    destination: Path,
    manifest: dict[str, Any],
    source_hashes: dict[str, str],
) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for relative in EXPECTED_CONTEXT_PATHS:
        source = repo_root / Path(relative)
        target = destination / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if target.is_symlink() or file_sha256(target) != source_hashes[relative]:
            raise RealIsolationError("temporary_context_copy_mismatch")
    manifest_target = destination / MANIFEST_RELATIVE
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_root / MANIFEST_RELATIVE, manifest_target)
    expected = set(EXPECTED_CONTEXT_PATHS) | {MANIFEST_RELATIVE.as_posix()}
    actual = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        raise RealIsolationError("temporary_context_file_set_mismatch")
    copied_manifest = _load_object(manifest_target)
    if copied_manifest != manifest:
        raise RealIsolationError("temporary_context_manifest_mismatch")


def build_create_arguments() -> list[str]:
    return [
        "create",
        "--name",
        CONTAINER_NAME,
        "--hostname",
        CONTAINER_HOSTNAME,
        "--network",
        "none",
        "--read-only",
        "--user",
        "65532:65532",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges=true",
        "--memory",
        "128m",
        "--memory-swap",
        "128m",
        "--cpus",
        "0.5",
        "--pids-limit",
        "32",
        "--ulimit",
        "nofile=64:64",
        "--label",
        f"ariadne.rehearsal.id={CONTAINER_NAME}",
        "--label",
        "ariadne.rehearsal.disposable=true",
        DERIVED_IMAGE,
    ]


def _parse_json_output(result: CommandResult) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RealIsolationError("docker_json_invalid") from error


def _inspect_object(
    client: CommandRunner, kind: str, reference: str
) -> dict[str, Any]:
    value = _parse_json_output(client.run([kind, "inspect", reference]))
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        raise RealIsolationError("docker_inspect_shape_invalid")
    return value[0]


def _object_exists(client: CommandRunner, kind: str, reference: str) -> bool:
    result = client.run(
        [kind, "inspect", reference],
        allowed_returncodes=frozenset({0, 1}),
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        diagnostic = (result.stdout + result.stderr).casefold()
        missing_marker = (
            "no such container" if kind == "container" else "no such image"
        )
        if missing_marker in diagnostic:
            return False
        raise RealIsolationError("docker_existence_probe_inconclusive")
    raise RealIsolationError("docker_existence_probe_failed")


def _verify_registry_provenance(client: CommandRunner) -> None:
    index = _parse_json_output(
        client.run(
            ["buildx", "imagetools", "inspect", BASE_REFERENCE, "--raw"],
            timeout=180,
        )
    )
    manifests = index.get("manifests") if isinstance(index, dict) else None
    if not isinstance(manifests, list):
        raise RealIsolationError("registry_index_invalid")
    matching = [
        item
        for item in manifests
        if isinstance(item, dict)
        and item.get("digest") == PLATFORM_MANIFEST_DIGEST
        and item.get("platform") == {
            "architecture": "amd64",
            "os": "linux",
        }
    ]
    if len(matching) != 1:
        raise RealIsolationError("registry_platform_manifest_mismatch")
    platform_manifest = _parse_json_output(
        client.run(
            [
                "buildx",
                "imagetools",
                "inspect",
                PLATFORM_MANIFEST_REFERENCE,
                "--raw",
            ],
            timeout=180,
        )
    )
    annotations = (
        platform_manifest.get("annotations")
        if isinstance(platform_manifest, dict)
        else None
    )
    if not isinstance(annotations, dict):
        raise RealIsolationError("registry_annotations_missing")
    expected_source = f"{SOURCE_URL}#{SOURCE_REVISION}:3.12/alpine3.22"
    if (
        annotations.get("org.opencontainers.image.source") != expected_source
        or annotations.get("org.opencontainers.image.revision") != SOURCE_REVISION
        or annotations.get("org.opencontainers.image.created") != SOURCE_CREATED
        or annotations.get("org.opencontainers.image.version")
        != "3.12.13-alpine3.22"
    ):
        raise RealIsolationError("registry_provenance_mismatch")


def _verify_engine(client: CommandRunner) -> dict[str, Any]:
    value = _parse_json_output(
        client.run(["version", "--format", "{{json .Server}}"])
    )
    if not isinstance(value, dict) or value.get("Os") != "linux" or value.get(
        "Arch"
    ) != "amd64":
        raise RealIsolationError("docker_engine_platform_mismatch")
    version = value.get("Version")
    if not isinstance(version, str) or not version:
        raise RealIsolationError("docker_engine_version_missing")
    return {
        "os": "linux",
        "architecture": "amd64",
        "version_major_minor": ".".join(version.split(".")[:2]),
    }


def _verify_base_image(image: dict[str, Any]) -> None:
    if image.get("Os") != "linux" or image.get("Architecture") != "amd64":
        raise RealIsolationError("base_image_platform_mismatch")
    repo_digests = image.get("RepoDigests")
    if not isinstance(repo_digests, list) or not any(
        item.endswith("@" + BASE_INDEX_DIGEST) for item in repo_digests
    ):
        raise RealIsolationError("base_image_digest_mismatch")
    config = image.get("Config", {})
    if config.get("Env") != list(EXPECTED_IMAGE_ENVIRONMENT[:5]):
        raise RealIsolationError("base_image_environment_mismatch")


def _verify_derived_image(image: dict[str, Any]) -> dict[str, Any]:
    if image.get("Os") != "linux" or image.get("Architecture") != "amd64":
        raise RealIsolationError("derived_image_platform_mismatch")
    config = image.get("Config")
    if not isinstance(config, dict):
        raise RealIsolationError("derived_image_config_missing")
    selected = {
        "user": config.get("User"),
        "working_dir": config.get("WorkingDir"),
        "entrypoint": config.get("Entrypoint"),
        "cmd": config.get("Cmd"),
        "environment": config.get("Env"),
        "labels": {
            key: (config.get("Labels") or {}).get(key)
            for key in sorted(REQUIRED_IMAGE_LABELS)
        },
        "exposed_ports": config.get("ExposedPorts"),
        "volumes": config.get("Volumes"),
        "healthcheck": config.get("Healthcheck"),
    }
    if selected != {
        "user": "65532:65532",
        "working_dir": "/workspace",
        "entrypoint": [
            "python",
            "/workspace/scripts/ariadne_real_isolation_payload.py",
        ],
        "cmd": None,
        "environment": list(EXPECTED_IMAGE_ENVIRONMENT),
        "labels": dict(sorted(REQUIRED_IMAGE_LABELS.items())),
        "exposed_ports": None,
        "volumes": None,
        "healthcheck": None,
    }:
        raise RealIsolationError("derived_image_config_mismatch")
    return selected


def _verify_container(container: dict[str, Any]) -> dict[str, Any]:
    config = container.get("Config")
    host = container.get("HostConfig")
    if not isinstance(config, dict) or not isinstance(host, dict):
        raise RealIsolationError("container_inspect_missing")
    ulimits = host.get("Ulimits")
    if ulimits != [{"Name": "nofile", "Hard": 64, "Soft": 64}]:
        raise RealIsolationError("container_ulimit_mismatch")
    selected = {
        "name": str(container.get("Name", "")).lstrip("/"),
        "hostname": config.get("Hostname"),
        "image": config.get("Image"),
        "user": config.get("User"),
        "entrypoint": config.get("Entrypoint"),
        "cmd": config.get("Cmd"),
        "environment": config.get("Env"),
        "network_mode": host.get("NetworkMode"),
        "read_only_rootfs": host.get("ReadonlyRootfs"),
        "privileged": host.get("Privileged"),
        "cap_drop": host.get("CapDrop") or [],
        "cap_add": host.get("CapAdd") or [],
        "security_opt": host.get("SecurityOpt") or [],
        "memory_bytes": host.get("Memory"),
        "memory_swap_bytes": host.get("MemorySwap"),
        "nano_cpus": host.get("NanoCpus"),
        "pids_limit": host.get("PidsLimit"),
        "binds": host.get("Binds") or [],
        "mounts": container.get("Mounts") or [],
        "tmpfs": host.get("Tmpfs") or {},
        "devices": host.get("Devices") or [],
        "device_requests": host.get("DeviceRequests") or [],
        "port_bindings": host.get("PortBindings") or {},
        "publish_all_ports": host.get("PublishAllPorts"),
        "restart_policy": (host.get("RestartPolicy") or {}).get("Name"),
        "auto_remove": host.get("AutoRemove"),
        "open_stdin": config.get("OpenStdin"),
        "tty": config.get("Tty"),
        "volumes": config.get("Volumes"),
        "exposed_ports": config.get("ExposedPorts"),
    }
    expected = {
        "name": CONTAINER_NAME,
        "hostname": CONTAINER_HOSTNAME,
        "image": DERIVED_IMAGE,
        "user": "65532:65532",
        "entrypoint": [
            "python",
            "/workspace/scripts/ariadne_real_isolation_payload.py",
        ],
        "cmd": None,
        "environment": list(EXPECTED_IMAGE_ENVIRONMENT),
        "network_mode": "none",
        "read_only_rootfs": True,
        "privileged": False,
        "cap_drop": ["ALL"],
        "cap_add": [],
        "security_opt": ["no-new-privileges=true"],
        "memory_bytes": 134217728,
        "memory_swap_bytes": 134217728,
        "nano_cpus": 500000000,
        "pids_limit": 32,
        "binds": [],
        "mounts": [],
        "tmpfs": {},
        "devices": [],
        "device_requests": [],
        "port_bindings": {},
        "publish_all_ports": False,
        "restart_policy": "no",
        "auto_remove": False,
        "open_stdin": False,
        "tty": False,
        "volumes": None,
        "exposed_ports": None,
    }
    if selected != expected:
        raise RealIsolationError("effective_container_policy_mismatch")
    return selected


def _verify_payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RealIsolationError("payload_shape_invalid")
    required = {
        "schema_version": "ariadne.real_isolation_payload.v1",
        "status": "passed",
        "result": "ariadne_real_isolation_payload_pass",
        "evidence_label": "authored_synthetic_disposable_local_container_payload",
        "predecessor_runs_byte_identical": True,
        "predecessor_result": (
            "ariadne_scripted_cognitive_work_cell_rehearsal_pass"
        ),
        "scenario_count": 8,
        "transition_count": 53,
        "released_edge_count": 8,
        "human_gate_delivery_count": 4,
        "aborted_edge_count": 2,
        "supersession_count": 1,
        "adaptive_agent_attached": False,
        "external_effects_enabled": False,
        "command_authority": False,
    }
    for key, expected in required.items():
        if value.get(key) != expected:
            raise RealIsolationError("payload_result_mismatch")
    if value.get("allowlisted_source_count") != len(EXPECTED_CONTEXT_PATHS):
        raise RealIsolationError("payload_source_count_mismatch")
    observation = value.get("isolation_observation")
    if observation != {
        "uid": 65532,
        "gid": 65532,
        "network_interfaces": ["lo"],
        "loopback_only": True,
        "write_probe_blocked": True,
        "write_probe_errno": "EROFS",
        "write_probe_residue": False,
    }:
        raise RealIsolationError("payload_isolation_observation_mismatch")
    for key in ("allowlisted_sources_sha256", "predecessor_projection_sha256"):
        digest = value.get(key)
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            raise RealIsolationError("payload_digest_invalid")
    return value


def _verify_stopped(container: dict[str, Any]) -> dict[str, Any]:
    state = container.get("State")
    if not isinstance(state, dict):
        raise RealIsolationError("container_state_missing")
    selected = {
        "status": state.get("Status"),
        "running": state.get("Running"),
        "paused": state.get("Paused"),
        "restarting": state.get("Restarting"),
        "oom_killed": state.get("OOMKilled"),
        "dead": state.get("Dead"),
        "exit_code": state.get("ExitCode"),
        "error_empty": state.get("Error") == "",
    }
    if selected != {
        "status": "exited",
        "running": False,
        "paused": False,
        "restarting": False,
        "oom_killed": False,
        "dead": False,
        "exit_code": 0,
        "error_empty": True,
    }:
        raise RealIsolationError("container_stopped_state_mismatch")
    return selected


def run_rehearsal(repo_root: Path, client: CommandRunner) -> dict[str, Any]:
    manifest, source_hashes = validate_manifest(repo_root)
    if _object_exists(client, "container", CONTAINER_NAME):
        raise RealIsolationError("container_name_collision")
    if _object_exists(client, "image", DERIVED_IMAGE):
        raise RealIsolationError("derived_image_tag_collision")

    base_preexisting = _object_exists(client, "image", BASE_REFERENCE)
    container_created = False
    image_created = False
    base_acquired = False
    temporary_root = Path(
        tempfile.mkdtemp(prefix="ariadne-real-isolation-rehearsal-")
    )
    context_path = temporary_root / "context"
    cleanup_errors: list[str] = []
    evidence: dict[str, Any] | None = None
    try:
        create_context(repo_root, context_path, manifest, source_hashes)
        engine = _verify_engine(client)
        _verify_registry_provenance(client)
        if not base_preexisting:
            client.run(
                ["pull", "--platform", "linux/amd64", BASE_REFERENCE],
                timeout=300,
            )
            base_acquired = True
        base_image = _inspect_object(client, "image", BASE_REFERENCE)
        _verify_base_image(base_image)

        dockerfile_path = context_path / Path(EXPECTED_CONTEXT_PATHS[0])
        client.run(
            [
                "build",
                "--platform",
                "linux/amd64",
                "--network",
                "none",
                "--pull=false",
                "--no-cache",
                "--tag",
                DERIVED_IMAGE,
                "--file",
                str(dockerfile_path),
                str(context_path),
            ],
            timeout=300,
        )
        image_created = True
        derived_config = _verify_derived_image(
            _inspect_object(client, "image", DERIVED_IMAGE)
        )
        client.run(build_create_arguments())
        container_created = True
        effective_policy = _verify_container(
            _inspect_object(client, "container", CONTAINER_NAME)
        )
        payload_result = client.run(
            ["start", "--attach", CONTAINER_NAME], timeout=120
        )
        payload = _verify_payload(_parse_json_output(payload_result))
        stopped = _verify_stopped(
            _inspect_object(client, "container", CONTAINER_NAME)
        )
        evidence = {
            "schema_version": EVIDENCE_VERSION,
            "result": RESULT,
            "evidence_label": manifest["evidence_label"],
            "manifest_sha256": file_sha256(repo_root / MANIFEST_RELATIVE),
            "allowlisted_source_count": len(source_hashes),
            "allowlisted_sources_sha256": canonical_sha256(source_hashes),
            "engine": engine,
            "image": {
                "base_reference": BASE_REFERENCE,
                "base_index_digest": BASE_INDEX_DIGEST,
                "platform": "linux/amd64",
                "platform_manifest_digest": PLATFORM_MANIFEST_DIGEST,
                "source_revision": SOURCE_REVISION,
                "registry_provenance_verified": True,
                "base_reference_preexisting": base_preexisting,
                "derived_selected_config_sha256": canonical_sha256(
                    derived_config
                ),
            },
            "effective_policy": {
                "inspect_before_start": True,
                "selected_config_sha256": canonical_sha256(effective_policy),
                "network_mode": "none",
                "read_only_rootfs": True,
                "user": "65532:65532",
                "all_capabilities_dropped": True,
                "no_new_privileges": True,
                "privileged": False,
                "mount_count": 0,
                "secret_count": 0,
                "published_port_count": 0,
                "host_environment_forwarded": False,
                "memory_bytes": 134217728,
                "memory_swap_bytes": 134217728,
                "nano_cpus": 500000000,
                "pids_limit": 32,
                "nofile_soft": 64,
                "nofile_hard": 64,
            },
            "payload": payload,
            "stopped_state": stopped,
            "closed_connections": list(REQUIRED_CLOSED_CONNECTIONS),
        }
    finally:
        if container_created:
            try:
                client.run(["container", "rm", "--force", CONTAINER_NAME])
            except RealIsolationError:
                cleanup_errors.append("container_remove_failed")
        if image_created:
            try:
                client.run(["image", "rm", DERIVED_IMAGE])
            except RealIsolationError:
                cleanup_errors.append("derived_image_remove_failed")
        if base_acquired:
            try:
                client.run(["image", "rm", BASE_REFERENCE])
            except RealIsolationError:
                cleanup_errors.append("base_reference_remove_failed")
        try:
            shutil.rmtree(temporary_root)
        except OSError:
            cleanup_errors.append("temporary_context_remove_failed")

    container_absent = not _object_exists(client, "container", CONTAINER_NAME)
    image_absent = not _object_exists(client, "image", DERIVED_IMAGE)
    base_state_preserved = (
        _object_exists(client, "image", BASE_REFERENCE)
        if base_preexisting
        else not _object_exists(client, "image", BASE_REFERENCE)
    )
    context_absent = not temporary_root.exists()
    if evidence is None:
        raise RealIsolationError("rehearsal_evidence_missing")
    cleanup = {
        "container_absent": container_absent,
        "derived_image_absent": image_absent,
        "base_reference_state_preserved": base_state_preserved,
        "temporary_context_absent": context_absent,
        "daemon_wide_prune_performed": False,
        "possible_unreferenced_layer_cache": True,
    }
    if cleanup_errors or not all(
        cleanup[key]
        for key in (
            "container_absent",
            "derived_image_absent",
            "base_reference_state_preserved",
            "temporary_context_absent",
        )
    ):
        raise RealIsolationError("scoped_cleanup_failed")
    evidence["cleanup"] = cleanup
    return evidence


def render_trace() -> str:
    return "\n".join(
        [
            "# Ariadne Real-Isolation Rehearsal",
            "",
            "One disposable local container: **authorised**",
            "",
            "Network: **none**",
            "",
            "Root filesystem: **read-only**",
            "",
            "Agent, model, provider and product connections: **none**",
            "",
            "The unchanged authored-synthetic tape is the only workload.",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect or run the fixed Ariadne real-isolation rehearsal."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("validate", help="Validate fixed sources without Docker.")
    subparsers.add_parser("rehearse", help="Run the one authorised Docker lifecycle.")
    subparsers.add_parser("trace", help="Render the fixed isolation posture.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    try:
        if args.action == "validate":
            manifest, hashes = validate_manifest(repo_root)
            print(
                canonical_json(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "status": "passed",
                        "rehearsal_id": manifest["rehearsal_id"],
                        "allowlisted_source_count": len(hashes),
                        "docker_command_executed": False,
                    }
                ),
                end="",
            )
            return 0
        if args.action == "trace":
            validate_manifest(repo_root)
            print(render_trace(), end="")
            return 0
        if args.action == "rehearse":
            print(
                canonical_json(run_rehearsal(repo_root, DockerClient(repo_root))),
                end="",
            )
            return 0
    except RealIsolationError:
        print(
            canonical_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "revision_required",
                    "result": "ariadne_real_isolation_rehearsal_failed",
                }
            ),
            end="",
        )
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
