"""Emit an Ariadne receipt with read-only source-commit resolution."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.orchestrator_preflight import (
    build_orchestrator_receipt,
    materialize_serial_continuation_runtime_state,
)
from orchestration_harness.git_object_resolution import (
    GitObjectResolutionError,
    failure_projection,
    resolve_commit_source,
)
from orchestration_harness.git_refs_snapshot import (
    GitRefsSnapshotError,
    build_git_refs_snapshot,
    failure_projection as git_refs_failure_projection,
)
from orchestration_harness.programme_admission import (
    admission_payload,
    evaluate_programme_admission,
)
from orchestration_harness.settings_fingerprint import settings_fingerprint

SETTINGS_DIR = REPO_ROOT / "orchestration" / "harness_settings"
_FULL_COMMIT_ID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")


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


def unresolved_git_ref_evidence_commit(
    runtime_state: dict[str, Any],
    *,
    repository_root: Path,
) -> str | None:
    """Return the first full Git-ref evidence ID that is not a local commit."""
    for object_id in git_ref_evidence_commit_ids(runtime_state):
        try:
            completed = subprocess.run(  # noqa: S603
                ["git", "cat-file", "-e", f"{object_id}^{{commit}}"],
                cwd=repository_root,
                check=False,
                capture_output=True,
                shell=False,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            return object_id
        if completed.returncode != 0:
            return object_id
    return None


def git_ref_evidence_commit_ids(runtime_state: dict[str, Any]) -> tuple[str, ...]:
    """Return manually authored full IDs from the narrative Git evidence field."""
    source_evidence = runtime_state.get("source_evidence")
    if not isinstance(source_evidence, dict):
        return ()
    evidence = source_evidence.get("git_refs_and_worktree")
    if not isinstance(evidence, str):
        return ()
    return tuple(sorted(set(_FULL_COMMIT_ID.findall(evidence))))


def _build_receipt_from_runtime_state(
    *,
    runtime_state: dict[str, Any],
    settings_dir: Path = SETTINGS_DIR,
    repository_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    requirements = _yaml(settings_dir / "orchestrator_requirements.yaml")
    current_settings_fingerprint = settings_fingerprint(settings_dir)
    receipt = build_orchestrator_receipt(
        requirements=requirements,
        adapters=_yaml(settings_dir / "transport_adapters.yaml"),
        worker_pool=_yaml(settings_dir / "worker_pool.yaml"),
        runtime_state=runtime_state,
        settings_fingerprint=current_settings_fingerprint,
    )
    programme_decision = evaluate_programme_admission(
        repo_root=repository_root,
        manifest=runtime_state.get("programme_task_manifest"),
        entrypoint="worker_dispatch",
    )
    receipt["programme_admission"] = admission_payload(programme_decision)
    receipt["admission_classification"] = (
        "advisory_receipt_only_not_executable_admission"
    )
    receipt["admission_usable"] = False
    if programme_decision.mode == "recovery" and programme_decision.gate == "G0":
        receipt["worker_dispatch_permitted"] = False
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
    unresolved_evidence_commit = unresolved_git_ref_evidence_commit(
        runtime_state,
        repository_root=repository_root,
    )
    if unresolved_evidence_commit is not None:
        reason = "git_refs_evidence_object_unresolvable"
        reasons = receipt.setdefault("reasons", [])
        if reason not in reasons:
            reasons.append(reason)
        receipt["status"] = "revision_required"
        receipt["worker_dispatch_permitted"] = False
    manual_evidence_ids = git_ref_evidence_commit_ids(runtime_state)
    manual_binding_reason = (
        "git_refs_evidence_manual_object_id_forbidden"
        if manual_evidence_ids
        else None
    )
    receipt["git_ref_evidence_binding"] = {
        "schema_version": "ariadne.git_ref_evidence_binding.v1",
        "status": "revision_required" if manual_binding_reason else "passed",
        "policy": "machine_snapshot_only",
        "manually_supplied_object_id_count": len(manual_evidence_ids),
        "reason_codes": [manual_binding_reason] if manual_binding_reason else [],
    }
    if manual_binding_reason is not None:
        reasons = receipt.setdefault("reasons", [])
        if manual_binding_reason not in reasons:
            reasons.append(manual_binding_reason)
        receipt["status"] = "revision_required"
        receipt["worker_dispatch_permitted"] = False
    snapshot_policy = requirements.get("git_refs_snapshot")
    if not isinstance(snapshot_policy, dict):
        snapshot_reason = "git_refs_snapshot_policy_missing"
        snapshot = git_refs_failure_projection(snapshot_reason)
    else:
        try:
            snapshot = build_git_refs_snapshot(
                repo_root=repository_root,
                expected_protected_commit=snapshot_policy["expected_protected_commit"],
                protected_refs=snapshot_policy["protected_refs"],
                preserved_untracked_paths=snapshot_policy["preserved_untracked_paths"],
                timeout_seconds=snapshot_policy["timeout_seconds"],
            )
            snapshot_reason = (
                None
                if snapshot["status"] == "passed"
                else snapshot["reason_codes"][0]
            )
        except (GitRefsSnapshotError, KeyError, TypeError) as error:
            snapshot_reason = (
                error.reason_code
                if isinstance(error, GitRefsSnapshotError)
                else "git_refs_snapshot_policy_invalid"
            )
            snapshot = git_refs_failure_projection(snapshot_reason)
    receipt["git_refs_snapshot"] = snapshot
    if snapshot_reason is not None:
        reasons = receipt.setdefault("reasons", [])
        if snapshot_reason not in reasons:
            reasons.append(snapshot_reason)
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


def _json_object(path: Path, *, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def build_receipt(
    *,
    runtime_state_path: Path,
    settings_dir: Path = SETTINGS_DIR,
    repository_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build a receipt from the historical complete runtime-state input."""
    return _build_receipt_from_runtime_state(
        runtime_state=_json_object(runtime_state_path, label="runtime state"),
        settings_dir=settings_dir,
        repository_root=repository_root,
    )


def build_serial_continuation_receipt(
    *,
    intent_path: Path,
    settings_dir: Path = SETTINGS_DIR,
    repository_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build the ordinary receipt from one compact observed-empty serial intent."""
    requirements = _yaml(settings_dir / "orchestrator_requirements.yaml")
    latch_policy = requirements.get("active_operation_latch")
    latch_relative = (
        latch_policy.get("current_state") if isinstance(latch_policy, dict) else None
    )
    if (
        not isinstance(latch_relative, str)
        or not latch_relative
        or "\\" in latch_relative
    ):
        raise ValueError("active operation current-state path is invalid")
    root = repository_root.resolve()
    latch_path = (root / latch_relative).resolve()
    try:
        latch_path.relative_to(root)
    except ValueError as error:
        raise ValueError("active operation current-state path escapes repo") from error
    runtime_state = materialize_serial_continuation_runtime_state(
        intent=_json_object(intent_path, label="serial continuation intent"),
        requirements=requirements,
        adapters=_yaml(settings_dir / "transport_adapters.yaml"),
        worker_pool=_yaml(settings_dir / "worker_pool.yaml"),
        active_operation=_json_object(latch_path, label="active operation latch"),
        repo_root=root,
    )
    return _build_receipt_from_runtime_state(
        runtime_state=runtime_state,
        settings_dir=settings_dir,
        repository_root=root,
    )


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
    source.add_argument("--continuation-intent", type=Path)
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
        if args.continuation_intent:
            receipt = build_serial_continuation_receipt(
                intent_path=args.continuation_intent,
                settings_dir=args.settings_dir,
            )
        else:
            receipt = build_receipt(
                runtime_state_path=args.runtime_state,
                settings_dir=args.settings_dir,
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
