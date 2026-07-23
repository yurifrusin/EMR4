from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Sequence

import pytest

from scripts import ariadne_real_isolation_rehearsal as isolation


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / isolation.MANIFEST_RELATIVE
DOCKERFILE_PATH = REPO_ROOT / isolation.EXPECTED_CONTEXT_PATHS[0]
HOST_SCRIPT_PATH = REPO_ROOT / "scripts/ariadne_real_isolation_rehearsal.py"
PAYLOAD_SCRIPT_PATH = REPO_ROOT / "scripts/ariadne_real_isolation_payload.py"
EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-real-isolation-rehearsal-evidence.json"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "orchestration/continuity/"
    "ariadne-real-isolation-rehearsal-evidence.schema.json"
)
GRAPH_PATH = REPO_ROOT / "orchestration/continuity/emr4-continuity-graph.json"
NODE_PATH = (
    REPO_ROOT
    / "orchestration/agent_inbox/codex/"
    "ariadne-real-isolation-rehearsal-node.json"
)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def payload_fixture() -> dict:
    return {
        "schema_version": "ariadne.real_isolation_payload.v1",
        "status": "passed",
        "result": "ariadne_real_isolation_payload_pass",
        "evidence_label": (
            "authored_synthetic_disposable_local_container_payload"
        ),
        "isolation_observation": {
            "uid": 65532,
            "gid": 65532,
            "network_interfaces": ["lo"],
            "loopback_only": True,
            "write_probe_blocked": True,
            "write_probe_errno": "EROFS",
            "write_probe_residue": False,
        },
        "allowlisted_source_count": len(isolation.EXPECTED_CONTEXT_PATHS),
        "allowlisted_sources_sha256": "sha256:" + "1" * 64,
        "predecessor_projection_sha256": "sha256:" + "2" * 64,
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


def image_fixture(*, derived: bool) -> dict:
    config = {
        "Env": list(
            isolation.EXPECTED_IMAGE_ENVIRONMENT
            if derived
            else isolation.EXPECTED_IMAGE_ENVIRONMENT[:5]
        ),
    }
    if derived:
        config.update(
            {
                "User": "65532:65532",
                "WorkingDir": "/workspace",
                "Entrypoint": [
                    "python",
                    "/workspace/scripts/ariadne_real_isolation_payload.py",
                ],
                "Cmd": None,
                "Labels": copy.deepcopy(isolation.REQUIRED_IMAGE_LABELS),
                "ExposedPorts": None,
                "Volumes": None,
                "Healthcheck": None,
            }
        )
    return {
        "Os": "linux",
        "Architecture": "amd64",
        "RepoDigests": ["python@" + isolation.BASE_INDEX_DIGEST],
        "Config": config,
    }


def container_fixture(*, exited: bool = False) -> dict:
    return {
        "Name": "/" + isolation.CONTAINER_NAME,
        "Config": {
            "Hostname": isolation.CONTAINER_HOSTNAME,
            "Image": isolation.DERIVED_IMAGE,
            "User": "65532:65532",
            "Entrypoint": [
                "python",
                "/workspace/scripts/ariadne_real_isolation_payload.py",
            ],
            "Cmd": None,
            "Env": list(isolation.EXPECTED_IMAGE_ENVIRONMENT),
            "OpenStdin": False,
            "Tty": False,
            "Volumes": None,
            "ExposedPorts": None,
        },
        "HostConfig": {
            "NetworkMode": "none",
            "ReadonlyRootfs": True,
            "Privileged": False,
            "CapDrop": ["ALL"],
            "CapAdd": None,
            "SecurityOpt": ["no-new-privileges=true"],
            "Memory": 134217728,
            "MemorySwap": 134217728,
            "NanoCpus": 500000000,
            "PidsLimit": 32,
            "Ulimits": [{"Name": "nofile", "Hard": 64, "Soft": 64}],
            "Binds": None,
            "Tmpfs": None,
            "Devices": [],
            "DeviceRequests": None,
            "PortBindings": {},
            "PublishAllPorts": False,
            "RestartPolicy": {"Name": "no"},
            "AutoRemove": False,
        },
        "Mounts": [],
        "State": {
            "Status": "exited" if exited else "created",
            "Running": False,
            "Paused": False,
            "Restarting": False,
            "OOMKilled": False,
            "Dead": False,
            "ExitCode": 0,
            "Error": "",
        },
    }


class FakeDocker:
    def __init__(
        self,
        *,
        mutate_container: tuple[str, object] | None = None,
        fail_start: bool = False,
    ) -> None:
        self.images = {isolation.BASE_REFERENCE}
        self.containers: set[str] = set()
        self.exited = False
        self.calls: list[tuple[str, ...]] = []
        self.mutate_container = mutate_container
        self.fail_start = fail_start

    def run(
        self,
        arguments: Sequence[str],
        *,
        timeout: int = 120,
        allowed_returncodes: frozenset[int] = frozenset({0}),
    ) -> isolation.CommandResult:
        del timeout, allowed_returncodes
        args = tuple(arguments)
        self.calls.append(args)
        if args[:2] == ("container", "inspect"):
            if args[2] not in self.containers:
                return isolation.CommandResult(
                    1, "", f"Error: No such container: {args[2]}"
                )
            value = container_fixture(exited=self.exited)
            if self.mutate_container:
                key, replacement = self.mutate_container
                value["HostConfig"][key] = replacement
            return isolation.CommandResult(0, json.dumps([value]), "")
        if args[:2] == ("image", "inspect"):
            if args[2] not in self.images:
                return isolation.CommandResult(
                    1, "", f"Error: No such image: {args[2]}"
                )
            return isolation.CommandResult(
                0,
                json.dumps(
                    [image_fixture(derived=args[2] == isolation.DERIVED_IMAGE)]
                ),
                "",
            )
        if args[:2] == ("version", "--format"):
            return isolation.CommandResult(
                0,
                json.dumps({"Os": "linux", "Arch": "amd64", "Version": "29.5.3"}),
                "",
            )
        if args[:4] == (
            "buildx",
            "imagetools",
            "inspect",
            isolation.BASE_REFERENCE,
        ):
            index = {
                "manifests": [
                    {
                        "digest": isolation.PLATFORM_MANIFEST_DIGEST,
                        "platform": {"architecture": "amd64", "os": "linux"},
                    }
                ]
            }
            return isolation.CommandResult(0, json.dumps(index), "")
        if args[:4] == (
            "buildx",
            "imagetools",
            "inspect",
            isolation.PLATFORM_MANIFEST_REFERENCE,
        ):
            manifest = {
                "annotations": {
                    "org.opencontainers.image.source": (
                        f"{isolation.SOURCE_URL}#{isolation.SOURCE_REVISION}:"
                        "3.12/alpine3.22"
                    ),
                    "org.opencontainers.image.revision": isolation.SOURCE_REVISION,
                    "org.opencontainers.image.created": isolation.SOURCE_CREATED,
                    "org.opencontainers.image.version": "3.12.13-alpine3.22",
                }
            }
            return isolation.CommandResult(0, json.dumps(manifest), "")
        if args[0] == "build":
            self.images.add(isolation.DERIVED_IMAGE)
            return isolation.CommandResult(0, "", "")
        if args[0] == "create":
            self.containers.add(isolation.CONTAINER_NAME)
            return isolation.CommandResult(0, "opaque-id", "")
        if args[:2] == ("start", "--attach"):
            if self.fail_start:
                raise isolation.RealIsolationError("synthetic_start_failure")
            self.exited = True
            return isolation.CommandResult(0, json.dumps(payload_fixture()), "")
        if args[:3] == ("container", "rm", "--force"):
            self.containers.discard(args[3])
            return isolation.CommandResult(0, "", "")
        if args[:2] == ("image", "rm"):
            self.images.discard(args[2])
            return isolation.CommandResult(0, "", "")
        raise AssertionError(f"unexpected fake Docker command: {args}")


def test_manifest_and_allowlisted_source_hashes_validate() -> None:
    manifest, hashes = isolation.validate_manifest(REPO_ROOT)

    assert manifest == load_manifest()
    assert tuple(hashes) == isolation.EXPECTED_CONTEXT_PATHS
    assert len(hashes) == 14


def test_temporary_context_contains_exactly_allowlisted_synthetic_files(
    tmp_path: Path,
) -> None:
    manifest, hashes = isolation.validate_manifest(REPO_ROOT)
    context = tmp_path / "context"

    isolation.create_context(REPO_ROOT, context, manifest, hashes)

    files = {
        path.relative_to(context).as_posix()
        for path in context.rglob("*")
        if path.is_file()
    }
    assert files == set(isolation.EXPECTED_CONTEXT_PATHS) | {
        isolation.MANIFEST_RELATIVE.as_posix()
    }
    assert not any(path.is_symlink() for path in context.rglob("*"))


def test_dockerfile_is_digest_pinned_and_has_no_executing_instruction() -> None:
    text = DOCKERFILE_PATH.read_text(encoding="utf-8")
    isolation._validate_dockerfile(DOCKERFILE_PATH)

    assert text.splitlines()[0] == f"FROM {isolation.BASE_REFERENCE}"
    assert "\nRUN " not in text
    assert "\nADD " not in text
    assert "\nARG " not in text


def test_create_arguments_are_fixed_default_deny_and_resource_bounded() -> None:
    arguments = isolation.build_create_arguments()

    assert arguments[-1] == isolation.DERIVED_IMAGE
    assert [arguments[index + 1] for index, item in enumerate(arguments) if item == "--network"] == ["none"]
    assert "--read-only" in arguments
    assert "--privileged" not in arguments
    assert "--env" not in arguments
    assert "--env-file" not in arguments
    assert "--mount" not in arguments
    assert "--volume" not in arguments
    assert "--publish" not in arguments
    assert "-p" not in arguments
    assert [arguments[index + 1] for index, item in enumerate(arguments) if item == "--memory"] == ["128m"]
    assert [arguments[index + 1] for index, item in enumerate(arguments) if item == "--pids-limit"] == ["32"]


@pytest.mark.parametrize(
    ("host_key", "replacement"),
    [
        ("NetworkMode", "bridge"),
        ("ReadonlyRootfs", False),
        ("Privileged", True),
        ("CapDrop", []),
        ("CapAdd", ["NET_ADMIN"]),
        ("SecurityOpt", []),
        ("Memory", 0),
        ("MemorySwap", -1),
        ("NanoCpus", 0),
        ("PidsLimit", 0),
        ("Binds", ["/host:/workspace"]),
        ("PortBindings", {"80/tcp": [{"HostPort": "80"}]}),
        ("PublishAllPorts", True),
        ("AutoRemove", True),
    ],
)
def test_effective_policy_drift_fails_closed(
    host_key: str, replacement: object
) -> None:
    value = container_fixture()
    value["HostConfig"][host_key] = replacement

    with pytest.raises(
        isolation.RealIsolationError, match="effective_container_policy_mismatch"
    ):
        isolation._verify_container(value)


def test_payload_static_surface_has_no_outbound_connect_or_subprocess() -> None:
    tree = ast.parse(PAYLOAD_SCRIPT_PATH.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert imports.isdisjoint(
        {"subprocess", "urllib", "http", "requests", "asyncio", "threading"}
    )
    assert called_attributes.isdisjoint(
        {"connect", "connect_ex", "create_connection", "send", "sendall"}
    )


def test_fake_lifecycle_inspects_before_start_and_cleans_every_owned_object() -> None:
    client = FakeDocker()

    evidence = isolation.run_rehearsal(REPO_ROOT, client)

    inspect_index = client.calls.index(
        ("container", "inspect", isolation.CONTAINER_NAME), 2
    )
    start_index = client.calls.index(
        ("start", "--attach", isolation.CONTAINER_NAME)
    )
    assert inspect_index < start_index
    assert evidence["result"] == isolation.RESULT
    assert evidence["payload"]["transition_count"] == 53
    assert evidence["cleanup"]["container_absent"] is True
    assert evidence["cleanup"]["derived_image_absent"] is True
    assert client.containers == set()
    assert client.images == {isolation.BASE_REFERENCE}


def test_bad_prestart_policy_never_starts_and_still_cleans() -> None:
    client = FakeDocker(mutate_container=("NetworkMode", "bridge"))

    with pytest.raises(
        isolation.RealIsolationError, match="effective_container_policy_mismatch"
    ):
        isolation.run_rehearsal(REPO_ROOT, client)

    assert not any(call[:1] == ("start",) for call in client.calls)
    assert client.containers == set()
    assert client.images == {isolation.BASE_REFERENCE}


def test_start_failure_still_removes_container_and_derived_image() -> None:
    client = FakeDocker(fail_start=True)

    with pytest.raises(isolation.RealIsolationError, match="synthetic_start_failure"):
        isolation.run_rehearsal(REPO_ROOT, client)

    assert client.containers == set()
    assert client.images == {isolation.BASE_REFERENCE}


def test_collision_refusal_never_deletes_preexisting_object() -> None:
    client = FakeDocker()
    client.images.add(isolation.DERIVED_IMAGE)

    with pytest.raises(
        isolation.RealIsolationError, match="derived_image_tag_collision"
    ):
        isolation.run_rehearsal(REPO_ROOT, client)

    assert isolation.DERIVED_IMAGE in client.images
    assert not any(call[:2] == ("image", "rm") for call in client.calls)


def test_inconclusive_existence_probe_is_not_laundered_as_absence() -> None:
    class InconclusiveDocker:
        def run(
            self,
            arguments: Sequence[str],
            *,
            timeout: int = 120,
            allowed_returncodes: frozenset[int] = frozenset({0}),
        ) -> isolation.CommandResult:
            del arguments, timeout, allowed_returncodes
            return isolation.CommandResult(1, "", "daemon unavailable")

    with pytest.raises(
        isolation.RealIsolationError,
        match="docker_existence_probe_inconclusive",
    ):
        isolation._object_exists(
            InconclusiveDocker(), "container", isolation.CONTAINER_NAME
        )


def test_committed_real_run_evidence_matches_schema_and_fixed_semantics() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema = pytest.importorskip("jsonschema")

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["manifest_sha256"] == isolation.file_sha256(MANIFEST_PATH)
    _, hashes = isolation.validate_manifest(REPO_ROOT)
    assert evidence["allowlisted_sources_sha256"] == isolation.canonical_sha256(
        hashes
    )
    assert evidence["effective_policy"]["inspect_before_start"] is True
    assert evidence["payload"]["predecessor_runs_byte_identical"] is True
    assert evidence["cleanup"] == {
        "container_absent": True,
        "derived_image_absent": True,
        "base_reference_state_preserved": True,
        "temporary_context_absent": True,
        "daemon_wide_prune_performed": False,
        "possible_unreferenced_layer_cache": True,
    }


def test_continuity_node_is_exact_metadata_only_descendant() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    node = json.loads(NODE_PATH.read_text(encoding="utf-8"))
    graph_node = next(
        item for item in graph["nodes"] if item["id"] == node["id"]
    )

    assert graph["graph_revision"] >= 21
    assert graph_node == node
    assert node["kind"] == "exploration"
    assert node["relationships"] == [
        {
            "node_id": "ariadne-scripted-cognitive-work-cell-rehearsal",
            "relation": "builds_on",
        }
    ]
    assert node["authority"]["authorized_openings"] == [
        {
            "boundary": "container-runtime",
            "source": "docs/ariadne-real-isolation-rehearsal-plan.md",
        }
    ]
    assert node["contract_evidence"] == []


def test_cli_exposes_no_caller_selected_image_path_or_docker_argument() -> None:
    parser = isolation.build_parser()

    assert parser.parse_args(["validate"]).action == "validate"
    assert parser.parse_args(["rehearse"]).action == "rehearse"
    assert parser.parse_args(["trace"]).action == "trace"
    with pytest.raises(SystemExit):
        parser.parse_args(["rehearse", "--image", "untrusted"])


def test_host_script_uses_subprocess_without_shell_and_no_daemon_prune() -> None:
    tree = ast.parse(HOST_SCRIPT_PATH.read_text(encoding="utf-8"))
    source = HOST_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "shell=False" in source
    assert "builder prune" not in source
    assert "system prune" not in source
    assert "container prune" not in source
    assert "image prune" not in source
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "run"
        for node in ast.walk(tree)
    )
