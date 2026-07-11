"""Build an advisory Ariadne Conductor allocation plan from supplied probes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.allocation import AvailabilityProbe, ConductorPlan, GeneralistProfile, RolePreference, WorkerResource
from orchestration_harness.allocator import allocate_roles

SETTINGS_DIR = REPO_ROOT / "orchestration" / "harness_settings"
SETTINGS_FILES = (
    "project.yaml",
    "worker_pool.yaml",
    "role_preferences.yaml",
    "generalist.yaml",
    "user_overrides.yaml",
    "sprint_worker_policy.yaml",
    "transport_adapters.yaml",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return payload


def _settings_fingerprint(settings_dir: Path) -> str:
    digest = hashlib.sha256()
    for name in SETTINGS_FILES:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((settings_dir / name).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _validate_probe_adapters(probes: list[AvailabilityProbe], adapter_payload: dict[str, Any]) -> None:
    adapters = adapter_payload.get("adapters")
    if adapter_payload.get("schema_version") != "ariadne.transport_adapters.v1" or not isinstance(adapters, list):
        raise ValueError("transport adapter settings are invalid")
    allowed_methods: dict[str, set[str]] = {}
    for adapter in adapters:
        if not isinstance(adapter, dict) or not isinstance(adapter.get("resource_ids"), list) or not isinstance(adapter.get("allowed_probe_methods"), list):
            raise ValueError("transport adapter entry is invalid")
        for resource_id in adapter["resource_ids"]:
            allowed_methods.setdefault(resource_id, set()).update(adapter["allowed_probe_methods"])
    for probe in probes:
        if probe.resource_id not in allowed_methods:
            raise ValueError(f"probe resource has no declared transport adapter: {probe.resource_id}")
        if probe.method not in allowed_methods[probe.resource_id]:
            raise ValueError(f"probe method is not declared for {probe.resource_id}: {probe.method}")


def build_allocation_report(*, sprint_id: str, probes_path: Path, settings_dir: Path = SETTINGS_DIR) -> dict[str, Any]:
    """Build a plan from local artifacts only; never probe or invoke a worker."""
    worker_pool = _load_yaml(settings_dir / "worker_pool.yaml")
    role_preferences = _load_yaml(settings_dir / "role_preferences.yaml")
    generalist_payload = _load_yaml(settings_dir / "generalist.yaml")
    worker_policy = _load_yaml(settings_dir / "sprint_worker_policy.yaml")
    adapter_payload = _load_yaml(settings_dir / "transport_adapters.yaml")
    probes_payload = json.loads(probes_path.read_text(encoding="utf-8"))
    if not isinstance(probes_payload, dict) or not isinstance(probes_payload.get("probes"), list):
        raise ValueError("probe input must be a JSON object with a probes list")

    resources = [WorkerResource.from_dict(item) for item in worker_pool["workers"]]
    preferences = [RolePreference.from_dict(item) for item in role_preferences["roles"]]
    generalist = GeneralistProfile.from_dict({key: value for key, value in generalist_payload.items() if key != "schema_version"})
    probes = [AvailabilityProbe.from_dict(item) for item in probes_payload["probes"]]
    _validate_probe_adapters(probes, adapter_payload)
    outcome = allocate_roles(resources=resources, preferences=preferences, probes=probes, generalist=generalist)
    fingerprint = _settings_fingerprint(settings_dir)

    assignments = [
        {
            "role": assignment.role.value,
            "resource_id": assignment.resource_id,
            "model": assignment.model,
            "reasoning": assignment.reasoning,
            "selection_basis": list(assignment.selection_basis),
            "fallback_reason": assignment.fallback_reason,
            "independence_label": assignment.independence_label,
            "user_override_ref": assignment.user_override_ref,
            "orchestrator_substituted": assignment.orchestrator_substituted,
            "unfilled_obligations": list(assignment.unfilled_obligations),
        }
        for assignment in outcome.assignments
    ]
    plan = None
    if assignments:
        conductor_plan = ConductorPlan.from_dict({
            "plan_id": f"{sprint_id}-{fingerprint.split(':', 1)[1][:12]}",
            "sprint_id": sprint_id,
            "settings_fingerprint": fingerprint,
            "assignments": assignments,
        })
        plan = {
            "plan_id": conductor_plan.plan_id,
            "sprint_id": conductor_plan.sprint_id,
            "settings_fingerprint": conductor_plan.settings_fingerprint,
            "assignments": assignments,
        }

    return {
        "schema_version": "ariadne.allocation_plan_report.v1",
        "advisory_only": True,
        "execution_permitted": False,
        "verifier_decision": None,
        "probes_source": str(probes_path),
        "settings_fingerprint": fingerprint,
        "conductor_plan": plan,
        "unfilled_required_roles": [role.value for role in outcome.unfilled_required_roles],
        "worker_execution_requirements": worker_policy["required_plan_fields"],
        "worker_mix_bounds": {
            "antigravity_platform_maximum_instances": worker_policy["worker_mix"]["antigravity"]["maximum_instances"],
            "deepseek_flash_minimum_instances": worker_policy["worker_mix"]["deepseek_flash"]["minimum_instances"],
            "deepseek_flash_maximum_instances": worker_policy["worker_mix"]["deepseek_flash"]["maximum_instances"],
        },
        "probe_transport_adapters": {
            probe.resource_id: probe.method for probe in probes
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an advisory Ariadne allocation plan from local probe JSON.")
    parser.add_argument("--sprint-id", required=True)
    parser.add_argument("--probes", type=Path, required=True, help="Local JSON object containing an authored probes list.")
    parser.add_argument("--settings-dir", type=Path, default=SETTINGS_DIR)
    parser.add_argument("--output", type=Path, help="Optional JSON artifact path; otherwise prints to stdout.")
    args = parser.parse_args()
    try:
        report = build_allocation_report(sprint_id=args.sprint_id, probes_path=args.probes, settings_dir=args.settings_dir)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"ariadne allocation plan failed: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
