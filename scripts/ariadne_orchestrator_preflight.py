"""Emit an Ariadne receipt with read-only source-commit resolution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.orchestrator_preflight import build_orchestrator_receipt
from orchestration_harness.git_object_resolution import (
    GitObjectResolutionError,
    failure_projection,
    resolve_commit_source,
)
from orchestration_harness.settings_fingerprint import settings_fingerprint

SETTINGS_DIR = REPO_ROOT / "orchestration" / "harness_settings"


def _yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return payload


def configured_continuation_events(
    settings_dir: Path = SETTINGS_DIR,
) -> tuple[str, ...]:
    """Return the exact configured receipt-event vocabulary in policy order."""
    requirements = _yaml(settings_dir / "orchestrator_requirements.yaml")
    events = requirements.get("continuation_events")
    if (
        not isinstance(events, list)
        or not events
        or any(not isinstance(event, str) or not event for event in events)
        or len(set(events)) != len(events)
    ):
        raise ValueError("configured continuation_events must be unique text values")
    return tuple(events)


def build_receipt(
    *,
    runtime_state_path: Path,
    settings_dir: Path = SETTINGS_DIR,
    repository_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    runtime_state = json.loads(runtime_state_path.read_text(encoding="utf-8"))
    if not isinstance(runtime_state, dict):
        raise ValueError("runtime state must be a JSON object")
    requirements = _yaml(settings_dir / "orchestrator_requirements.yaml")
    current_settings_fingerprint = settings_fingerprint(settings_dir)
    receipt = build_orchestrator_receipt(
        requirements=requirements,
        adapters=_yaml(settings_dir / "transport_adapters.yaml"),
        worker_pool=_yaml(settings_dir / "worker_pool.yaml"),
        runtime_state=runtime_state,
        settings_fingerprint=current_settings_fingerprint,
    )
    runtime_active_operation = runtime_state.get("active_operation")
    if isinstance(runtime_active_operation, dict) and runtime_active_operation:
        checkpoint = runtime_active_operation.get("checkpoint")
        latched_settings_fingerprint = (
            checkpoint.get("settings_fingerprint")
            if isinstance(checkpoint, dict)
            else None
        )
        if latched_settings_fingerprint != current_settings_fingerprint:
            reason = "active_operation_settings_fingerprint_mismatch"
            reasons = receipt.setdefault("reasons", [])
            if reason not in reasons:
                reasons.append(reason)
            receipt["status"] = "revision_required"
            receipt["worker_dispatch_permitted"] = False
    policy = requirements.get("git_object_resolution")
    continuation_event = runtime_state.get("continuation_event")
    required = isinstance(policy, dict) and continuation_event in policy.get(
        "required_events", []
    )
    if not required:
        receipt["git_object_resolution"] = {}
        return receipt

    policy_valid = bool(
        policy.get("schema_version") == "ariadne.git_object_resolution_policy.v1"
        and policy.get("source_field") == "active_operation.source_head"
        and policy.get("require_full_lowercase_object_id") is True
        and policy.get("expected_object_type") == "commit"
        and policy.get("require_ancestor_of_head") is True
        and isinstance(policy.get("timeout_seconds"), int)
    )
    active_operation = receipt.get("active_operation")
    source_head = (
        active_operation.get("source_head")
        if isinstance(active_operation, dict)
        else None
    )
    if not policy_valid:
        reason = "git_object_resolution_policy_invalid"
        resolution = failure_projection(source_head=source_head, reason_code=reason)
    elif not isinstance(active_operation, dict) or not active_operation:
        reason = "git_object_resolution_active_operation_unavailable"
        resolution = failure_projection(source_head=source_head, reason_code=reason)
    else:
        try:
            resolution = resolve_commit_source(
                repo_root=repository_root,
                source_head=source_head,
                timeout_seconds=policy["timeout_seconds"],
                require_ancestor_of_head=policy["require_ancestor_of_head"],
            )
            reason = None
        except GitObjectResolutionError as error:
            reason = error.reason_code
            resolution = failure_projection(
                source_head=source_head,
                reason_code=reason,
            )
    receipt["git_object_resolution"] = resolution
    if reason is not None:
        reasons = receipt.setdefault("reasons", [])
        if reason not in reasons:
            reasons.append(reason)
        receipt["status"] = "revision_required"
        receipt["worker_dispatch_permitted"] = False
    return receipt


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    """Write canonical UTF-8 JSON with LF bytes on every platform."""
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an advisory generic Ariadne orchestrator receipt."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--runtime-state", type=Path)
    source.add_argument(
        "--list-continuation-events",
        action="store_true",
        help="List the exact configured continuation-event vocabulary and exit.",
    )
    parser.add_argument("--settings-dir", type=Path, default=SETTINGS_DIR)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.list_continuation_events:
            events = configured_continuation_events(args.settings_dir)
            print("\n".join(events))
            return 0
        receipt = build_receipt(
            runtime_state_path=args.runtime_state, settings_dir=args.settings_dir
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"ariadne orchestrator preflight failed: {error}", file=sys.stderr)
        return 2
    if args.output:
        write_json_lf(args.output, receipt)
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
