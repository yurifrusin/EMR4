"""Render the inert Reception One visual-synthesis isolation plan."""

from __future__ import annotations

import copy
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_launcher as base
from scripts import reception_one_visual_synthesis_contracts as contracts


PLAN_PATH = contracts.ARTIFACT_ROOT / "provider-blocked-launch-plan.json"
ISOLATION_PATH = contracts.ARTIFACT_ROOT / "isolation-manifest.json"
DEFAULT_REQUEST_SOURCE = (
    "orchestration/continuity/reception-one-visual-synthesis/"
    "occupied-cell-request.json"
)
ALLOWED_REQUEST_SOURCES = {
    DEFAULT_REQUEST_SOURCE,
    (
        "orchestration/continuity/reception-one-visual-synthesis/"
        "dry-run-cell-request.json"
    ),
    (
        "orchestration/continuity/reception-one-visual-synthesis/"
        "dry-run-002-cell-request.json"
    ),
    (
        "orchestration/continuity/reception-one-visual-synthesis/"
        "dry-run-003-cell-request.json"
    ),
    (
        "orchestration/continuity/reception-one-visual-synthesis/"
        "repair-occupied-cell-request.json"
    ),
}
NETWORK = "reception-one-visual-synthesis-internal"
RELAY_CONTAINER = "reception-one-visual-synthesis-relay"
CELL_CONTAINER = "reception-one-visual-synthesis-cell"
RELAY_IMAGE = "reception-one-visual-synthesis-relay:v1"
CELL_IMAGE = "reception-one-visual-synthesis-cell:v1"
LauncherContractError = base.LauncherContractError


def _replace_runtime_names(value: Any) -> Any:
    replacements = {
        base.NETWORK: NETWORK,
        base.RELAY_CONTAINER: RELAY_CONTAINER,
        base.CELL_CONTAINER: CELL_CONTAINER,
        base.RELAY_IMAGE: RELAY_IMAGE,
        base.CELL_IMAGE: CELL_IMAGE,
    }
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace_runtime_names(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_runtime_names(item)
            for key, item in value.items()
        }
    return value


def build_plan(
    request_source: str = DEFAULT_REQUEST_SOURCE,
) -> dict[str, Any]:
    if request_source not in ALLOWED_REQUEST_SOURCES:
        raise LauncherContractError("request_source_not_allowlisted")
    plan = _replace_runtime_names(copy.deepcopy(base.build_plan()))
    plan["plan_id"] = "reception-one-visual-synthesis-vertex-sydney-v1"
    files = plan["build_context"]["files"]
    files[0]["source"] = (
        "orchestration/continuity/reception-one-visual-synthesis/Dockerfile"
    )
    files[1]["source"] = (
        "scripts/ariadne_vertex_sydney_gemini_25_relay.py"
    )
    files[2]["source"] = (
        "scripts/ariadne_vertex_sydney_gemini_25_cell.py"
    )
    files[3]["source"] = request_source
    files[4]["source"] = (
        "orchestration/continuity/reception-one-visual-synthesis/"
        "design-candidate.schema.json"
    )
    plan["broker_process"]["script"] = (
        "scripts/reception_one_visual_synthesis_broker.py"
    )
    plan["broker_process"]["endpoint_policy"] = (
        "orchestration/continuity/reception-one-visual-synthesis/"
        "broker-policy.json"
    )
    return plan


def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        request_source = plan["build_context"]["files"][3]["source"]
    except (KeyError, IndexError, TypeError):
        return ["launch_plan_request_source_missing"]
    if request_source not in ALLOWED_REQUEST_SOURCES:
        return ["launch_plan_request_source_not_allowlisted"]
    if plan != build_plan(request_source):
        errors.append("launch_plan_not_exact")
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
    if relay.get("networks") != [
        "task_internal_only",
        "bridge_egress",
    ]:
        errors.append("relay_network_manifest_invalid")
    if plan["cell_boundary"]["networks"] != [NETWORK]:
        errors.append("cell_network_plan_invalid")
    environment_allowlist = plan["broker_process"]["environment_allowlist"]
    if environment_allowlist != sorted(environment_allowlist):
        errors.append("broker_environment_allowlist_not_sorted")
    return sorted(set(errors))
