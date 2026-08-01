#!/usr/bin/env python3
"""Render and validate the provider-blocked Gemini 2.5 Sydney launch plan.

This module deliberately has no process, Docker, socket, credential, network
or environment access. It freezes the exact commands a later real-isolation
gate may execute, but cannot execute them itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts


PLAN_PATH = contracts.ARTIFACT_ROOT / "provider-blocked-launch-plan.json"
ISOLATION_PATH = contracts.ARTIFACT_ROOT / "isolation-manifest.json"
DEFAULT_REQUEST_SOURCE = (
    "orchestration/continuity/"
    "ariadne-vertex-sydney-gemini-25/cell-request.json"
)
ALLOWED_REQUEST_SOURCES = {
    DEFAULT_REQUEST_SOURCE,
    (
        "orchestration/continuity/"
        "ariadne-vertex-sydney-gemini-25/"
        "repair-dry-run-cell-request.json"
    ),
    (
        "orchestration/continuity/"
        "ariadne-vertex-sydney-gemini-25/"
        "repair-occupied-cell-request.json"
    ),
    (
        "orchestration/continuity/"
        "ariadne-vertex-sydney-gemini-25/"
        "repair-dry-run-002-cell-request.json"
    ),
    (
        "orchestration/continuity/"
        "ariadne-vertex-sydney-gemini-25/"
        "repair-dry-run-003-cell-request.json"
    ),
    (
        "orchestration/continuity/"
        "ariadne-vertex-sydney-gemini-25/"
        "repair-occupied-002-cell-request.json"
    ),
}

NETWORK = "ariadne-vertex-sydney-gemini-25-internal"
RELAY_CONTAINER = "ariadne-vertex-sydney-gemini-25-relay"
CELL_CONTAINER = "ariadne-vertex-sydney-gemini-25-cell"
RELAY_IMAGE = "ariadne-vertex-sydney-gemini-25-relay:v1"
CELL_IMAGE = "ariadne-vertex-sydney-gemini-25-cell:v1"


class LauncherContractError(ValueError):
    """Raised when the inert launcher plan is not exact."""


def build_plan(
    request_source: str = DEFAULT_REQUEST_SOURCE,
) -> dict[str, Any]:
    if request_source not in ALLOWED_REQUEST_SOURCES:
        raise LauncherContractError("request_source_not_allowlisted")
    return {
        "schema_version": "ariadne.vertex_sydney_blocked_launch_plan.v1",
        "plan_id": "ariadne-vertex-sydney-gemini-25-provider-blocked-v1",
        "execution_performed": False,
        "provider_contacted": False,
        "credential_read": False,
        "build_context": {
            "kind": "temporary_exact_allowlist",
            "repository_root_is_context": False,
            "files": [
                {
                    "source": (
                        "orchestration/continuity/"
                        "ariadne-vertex-sydney-gemini-25/Dockerfile"
                    ),
                    "target": "Dockerfile",
                },
                {
                    "source": (
                        "scripts/"
                        "ariadne_vertex_sydney_gemini_25_relay.py"
                    ),
                    "target": "relay.py",
                },
                {
                    "source": "scripts/ariadne_vertex_sydney_gemini_25_cell.py",
                    "target": "cell.py",
                },
                {
                    "source": request_source,
                    "target": "cell-request.json",
                },
                {
                    "source": (
                        "orchestration/continuity/"
                        "ariadne-vertex-sydney-gemini-25/"
                        "release-output.schema.json"
                    ),
                    "target": "release-output.schema.json",
                },
            ],
        },
        "docker_commands": {
            "build_relay": [
                "docker",
                "build",
                "--target",
                "relay",
                "--tag",
                RELAY_IMAGE,
                "<temporary_exact_context>",
            ],
            "build_cell": [
                "docker",
                "build",
                "--target",
                "work-cell",
                "--tag",
                CELL_IMAGE,
                "<temporary_exact_context>",
            ],
            "create_internal_network": [
                "docker",
                "network",
                "create",
                "--internal",
                NETWORK,
            ],
            "create_relay": [
                "docker",
                "create",
                "--name",
                RELAY_CONTAINER,
                "--network",
                NETWORK,
                "--network-alias",
                "broker",
                "--read-only",
                "--user",
                "65532:65532",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=8m",  # nosec B108 -- container tmpfs
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
                    "type=bind,src=<ephemeral_broker_token>,"
                    "dst=/run/secrets/broker_token,readonly"
                ),
                "--env",
                "BROKER_HOST_PORT=<ephemeral_port>",
                RELAY_IMAGE,
            ],
            "connect_relay_egress": [
                "docker",
                "network",
                "connect",
                "bridge",
                RELAY_CONTAINER,
            ],
            "create_cell": [
                "docker",
                "create",
                "--name",
                CELL_CONTAINER,
                "--hostname",
                "ariadne-vertex-cell",
                "--network",
                NETWORK,
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
                "64",
                "--ulimit",
                "nofile=64:64",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges=true",
                CELL_IMAGE,
            ],
            "start_cell": [
                "docker",
                "start",
                "--attach",
                CELL_CONTAINER,
            ],
            "cleanup": [
                ["docker", "rm", "--force", CELL_CONTAINER],
                ["docker", "rm", "--force", RELAY_CONTAINER],
                ["docker", "network", "rm", NETWORK],
                ["docker", "image", "rm", CELL_IMAGE, RELAY_IMAGE],
            ],
        },
        "broker_process": {
            "runtime": "host_purpose_built_one_use_process",
            "script": "scripts/ariadne_vertex_sydney_gemini_25_broker.py",
            "environment_allowlist": [
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
            ],
            "api_key_environment_forwarded": False,
            "google_application_credentials_forwarded": False,
            "mode": "<dry-run-or-live-after-gate>",
            "one_use_ledger_required": True,
            "endpoint_policy": (
                "orchestration/continuity/"
                "ariadne-vertex-sydney-gemini-25/broker-policy.json"
            ),
        },
        "cell_boundary": {
            "networks": [NETWORK],
            "published_ports": 0,
            "environment": [],
            "mounts": [],
            "credential_material": False,
            "provider_or_service_account_details": False,
        },
        "relay_boundary": {
            "networks": [NETWORK, "bridge"],
            "published_ports": 0,
            "mounts": ["/run/secrets/broker_token:read_only"],
            "forward_host": "host.docker.internal",
            "forward_path": "/v1/execute",
            "arbitrary_proxy": False,
        },
        "negative_routes": {
            "unapproved_provider": "broker_reject",
            "unapproved_identity": "broker_reject",
            "unapproved_project": "broker_reject",
            "unapproved_model": "broker_reject",
            "unapproved_hostname": "broker_reject",
            "unapproved_region": "broker_reject",
            "global_endpoint": "broker_reject",
            "automatic_fallback": "broker_reject",
        },
    }


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        request_source = plan["build_context"]["files"][3]["source"]
    except (KeyError, IndexError, TypeError):
        errors.append("launch_plan_request_source_missing")
        return errors
    if request_source not in ALLOWED_REQUEST_SOURCES:
        errors.append("launch_plan_request_source_not_allowlisted")
        return errors
    if plan != build_plan(request_source):
        errors.append("launch_plan_not_exact")
        return errors
    isolation = contracts.load_object(ISOLATION_PATH)
    cell = isolation.get("cell", {})
    relay = isolation.get("relay", {})
    if (
        cell.get("network") != "task_internal_only"
        or cell.get("credential_mount") is not False
        or cell.get("docker_socket") is not False
        or cell.get("host_network") is not False
    ):
        errors.append("cell_isolation_manifest_invalid")
    if relay.get("networks") != ["task_internal_only", "bridge_egress"]:
        errors.append("relay_network_manifest_invalid")
    if plan["cell_boundary"]["networks"] != [NETWORK]:
        errors.append("cell_network_plan_invalid")
    if plan["broker_process"]["environment_allowlist"] != sorted(
        plan["broker_process"]["environment_allowlist"]
    ):
        errors.append("broker_environment_allowlist_not_sorted")
    return sorted(set(errors))


def check_committed() -> dict[str, Any]:
    plan = contracts.load_object(PLAN_PATH)
    errors = validate_plan(plan)
    if errors:
        raise LauncherContractError(",".join(errors))
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--format", choices=("json",), default="json")
    arguments = parser.parse_args()
    try:
        plan = check_committed() if arguments.check else build_plan()
    except (LauncherContractError, OSError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {"status": "revision_required", "reason_code": str(error)},
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
