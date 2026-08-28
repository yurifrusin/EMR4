"""Run a bounded Gemini verifier in an explicitly bound Antigravity project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ariadne_evidence_gate import (
    admit_command_results,
    command_manifest_sha256,
    load_command_manifest,
)
from orchestration_harness.programme_admission import require_programme_admission


DEFAULT_MODEL = "gemini-3.7-flash-high"
PRINT_TIMEOUT_SECONDS = 45 * 60
PRINT_TIMEOUT_ARGUMENT = "45m"
MODEL_EFFORTS = {
    "gemini-3.5-flash-low": "low",
    "gemini-3.5-flash-medium": "medium",
    "gemini-3.5-flash-high": "high",
    "gemini-3.6-flash-low": "low",
    "gemini-3.6-flash-medium": "medium",
    "gemini-3.6-flash-high": "high",
    "gemini-3.7-flash-low": "low",
    "gemini-3.7-flash-medium": "medium",
    "gemini-3.7-flash-high": "high",
}
LEGACY_MODEL_ALIASES = {
    "Gemini 3.5 Flash (Low)": "gemini-3.5-flash-low",
    "Gemini 3.5 Flash (Medium)": "gemini-3.5-flash-medium",
    "Gemini 3.5 Flash (High)": "gemini-3.5-flash-high",
}
MODELS = set(MODEL_EFFORTS) | set(LEGACY_MODEL_ALIASES)
PROTECTED_BRANCHES = {"master", "handoff/current"}
DECISION_PATTERN = re.compile(r"(?m)^DECISION: (pass|revision_required)\s*$")
STRUCTURED_DECISION_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["decision", "review"],
    "properties": {
        "decision": {"enum": ["pass", "revision_required"]},
        "review": {"type": "string", "minLength": 1, "maxLength": 40000},
    },
}
REHYDRATION_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def structured_decision_schema(
    command_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the exact verifier egress schema for the selected command gate."""
    from orchestration_harness.verdict import ReviewVerdict

    schema: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["decision", "review"],
        "properties": {
            "decision": {"enum": [verdict.value for verdict in ReviewVerdict]},
            "review": {"type": "string", "minLength": 1, "maxLength": 40000},
        },
    }
    if command_manifest is not None:
        commands = command_manifest["commands"]
        schema["required"].append("command_results")
        schema["properties"]["command_results"] = {
            "type": "array",
            "minItems": len(commands),
            "maxItems": len(commands),
            # The provider tool-schema dialect requires an explicit `items`
            # schema and does not admit tuple-only `prefixItems`. Exact id,
            # argv and ordering remain enforced locally by
            # `admit_command_results` after structured output returns.
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "argv", "exit_code"],
                "properties": {
                    "id": {"enum": [command["id"] for command in commands]},
                    "argv": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 128,
                        "items": {"type": "string"},
                    },
                    "exit_code": {"type": "integer"},
                },
            },
        }
    return schema


@dataclass(frozen=True)
class WorktreeState:
    root: Path
    branch: str
    head: str
    dirty: bool


def _git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8"
    )
    if completed.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def inspect_worktree(cwd: Path, *, require_clean: bool) -> WorktreeState:
    resolved = cwd.resolve()
    if not resolved.is_dir():
        raise ValueError("Antigravity cwd must be an existing directory")
    root = Path(_git(resolved, "rev-parse", "--show-toplevel")).resolve()
    if root != resolved:
        raise ValueError(f"Antigravity cwd must equal the Git worktree root: {root}")
    branch = _git(resolved, "branch", "--show-current")
    if not branch or branch in PROTECTED_BRANCHES:
        raise ValueError(
            f"Antigravity refuses protected or detached branch: {branch!r}"
        )
    dirty = bool(_git(resolved, "status", "--porcelain"))
    if require_clean and dirty:
        raise ValueError("Antigravity worktree must be clean before dispatch")
    return WorktreeState(
        root=root,
        branch=branch,
        head=_git(resolved, "rev-parse", "HEAD"),
        dirty=dirty,
    )


def build_command(
    *,
    packet: str,
    state: WorktreeState,
    model: str,
    os_sandbox: bool,
    structured_decision: bool = True,
    command_manifest: dict[str, Any] | None = None,
) -> list[str]:
    if model not in MODELS:
        raise ValueError(f"unsupported Antigravity model: {model}")
    canonical_model = LEGACY_MODEL_ALIASES.get(model, model)
    reasoning_effort = MODEL_EFFORTS[canonical_model]
    bound_packet = (
        f"BOUND WORKTREE: {state.root}\n"
        f"BOUND BRANCH: {state.branch}\n"
        "Use only this worktree. First verify the exact root and branch. "
        "Do not inspect or reuse any historical Antigravity project.\n\n"
        f"{packet}"
    )
    if command_manifest is not None:
        bound_packet += (
            "\n\nBOUND COMMAND MANIFEST: Execute exactly these structured argv "
            "commands in order. Do not substitute, widen, omit, wrap or combine "
            "them. Return each exact id, argv and integer exit_code in "
            f"command_results: {json.dumps(command_manifest, sort_keys=True)}"
        )
    if structured_decision:
        bound_packet += (
            "\n\nSTRUCTURED OUTPUT OVERRIDE: Complete and wait for every command and "
            "notification. Return one schema-constrained object only. Put all evidence "
            "and findings in `review`, set `decision` exactly once, and do not write any "
            "DECISION: marker inside `review`."
        )
    command = [
        "agy",
        "-p",
        bound_packet,
        "--new-project",
        "--add-dir",
        str(state.root),
        "--model",
        canonical_model,
        "--effort",
        reasoning_effort,
        "--mode",
        "plan",
        "--dangerously-skip-permissions",
        "--print-timeout",
        PRINT_TIMEOUT_ARGUMENT,
    ]
    if structured_decision:
        command.extend(
            [
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(
                    structured_decision_schema(command_manifest),
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            ]
        )
    if os_sandbox:
        command.append("--sandbox")
    return command


def _as_structured_decision(
    value: object,
    command_manifest: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    from orchestration_harness.verdict import (
        ArtifactKind,
        ReviewVerdict,
        parse_artifact_verdict,
    )

    if isinstance(value, str):

        class DuplicateJsonMemberError(ValueError):
            pass

        def reject_duplicate_members(
            pairs: list[tuple[str, object]],
        ) -> dict[str, object]:
            decoded: dict[str, object] = {}
            for key, item in pairs:
                if key in decoded:
                    raise DuplicateJsonMemberError(key)
                decoded[key] = item
            return decoded

        try:
            value = json.loads(value, object_pairs_hook=reject_duplicate_members)
        except (json.JSONDecodeError, DuplicateJsonMemberError):
            return None
    expected_keys = {"decision", "review"}
    if command_manifest is not None:
        expected_keys.add("command_results")
    if not isinstance(value, dict) or set(value) != expected_keys:
        return None
    decision = value.get("decision")
    review = value.get("review")
    if not isinstance(decision, str):
        return None
    try:
        canonical_decision = ReviewVerdict(decision)
    except ValueError:
        return None
    if not isinstance(review, str) or not review.strip() or len(review) > 40000:
        return None
    normalized_review = review.strip()
    review_assessment = parse_artifact_verdict(
        normalized_review,
        ArtifactKind.DECISION,
    )
    if review_assessment.reason_code != "missing_authoritative_marker":
        return None

    canonical_marker = f"DECISION: {canonical_decision.value.upper()}"
    assessment = parse_artifact_verdict(canonical_marker, ArtifactKind.DECISION)
    expected_integration_authority = canonical_decision is ReviewVerdict.PASS
    if (
        assessment.artifact_kind is not ArtifactKind.DECISION
        or not assessment.artifact_valid
        or assessment.review_verdict is not canonical_decision
        or assessment.integration_authorized is not expected_integration_authority
        or assessment.canonical_marker != canonical_marker
        or assessment.reason_code != "terminal_marker_observed"
    ):
        return None

    canonical_decision_value = canonical_decision.value
    admitted: dict[str, Any] = {
        "decision": canonical_decision_value,
        "review": normalized_review,
        "verdict_assessment": assessment.to_dict(),
    }
    if command_manifest is not None:
        try:
            admitted["command_results"] = admit_command_results(
                manifest=command_manifest,
                results=value["command_results"],
                decision=canonical_decision_value,
            )
        except ValueError:
            return None
    return admitted


def parse_structured_decision(
    stdout: str,
    command_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    class DuplicateJsonMemberError(ValueError):
        pass

    def reject_duplicate_members(
        pairs: list[tuple[str, object]],
    ) -> dict[str, object]:
        decoded: dict[str, object] = {}
        for key, value in pairs:
            if key in decoded:
                raise DuplicateJsonMemberError(key)
            decoded[key] = value
        return decoded

    try:
        root = json.loads(stdout, object_pairs_hook=reject_duplicate_members)
    except DuplicateJsonMemberError:
        root = None
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Antigravity structured output was not one JSON value"
        ) from error

    wrapper_keys = ("structured_output", "result", "response", "output")
    candidates: list[dict[str, Any]] = []
    direct_source = root
    if isinstance(root, dict):
        if "verdict_assessment" in root:
            direct_source = None
            wrapper_keys = ()
        else:
            direct_keys = {"decision", "review"}
            if command_manifest is not None:
                direct_keys.add("command_results")
            if direct_keys.issubset(root):
                if set(root).issubset(direct_keys | set(wrapper_keys)):
                    direct_source = {key: root[key] for key in direct_keys}
                else:
                    direct_source = None
                    wrapper_keys = ()
    direct = _as_structured_decision(direct_source, command_manifest)
    if direct is not None:
        candidates.append(direct)
    if isinstance(root, dict):
        for key in wrapper_keys:
            candidate = _as_structured_decision(root.get(key), command_manifest)
            if candidate is not None:
                candidates.append(candidate)

    unique = {
        json.dumps(item, sort_keys=True, separators=(",", ":")): item
        for item in candidates
    }
    if len(unique) != 1:
        raise RuntimeError(
            "Antigravity verifier must return exactly one schema-valid decision "
            f"envelope; observed {len(unique)}"
        )
    return next(iter(unique.values()))


def admit_orchestrator_receipt(path: Path) -> str:
    raw = path.read_bytes()
    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("orchestrator receipt must be valid JSON") from error
    if not isinstance(receipt, dict):
        raise ValueError("orchestrator receipt must be a JSON object")
    if receipt.get("schema_version") != "ariadne.orchestrator_receipt.v1":
        raise ValueError("orchestrator receipt schema is not admitted")
    if receipt.get("status") != "passed":
        raise ValueError("orchestrator receipt did not pass")
    if receipt.get("worker_dispatch_permitted") is not True:
        raise ValueError("orchestrator receipt does not permit worker dispatch")
    sources = receipt.get("rehydration_sources")
    if not isinstance(sources, list) or set(sources) != REHYDRATION_SOURCES:
        raise ValueError(
            "orchestrator receipt lacks the exact five rehydration sources"
        )
    return hashlib.sha256(raw).hexdigest()


def _atomic_receipt_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _output_evidence(value: str) -> dict[str, Any]:
    encoded = value.encode("utf-8")
    return {
        "bytes": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "empty": not encoded,
    }


def run_worker(
    *,
    packet_path: Path,
    cwd: Path,
    output_path: Path,
    orchestrator_receipt_path: Path,
    model: str,
    os_sandbox: bool,
    structured_decision: bool = True,
    command_manifest_path: Path | None = None,
    programme_task_manifest: Path | None = None,
) -> dict:
    require_programme_admission(
        repo_root=REPO_ROOT,
        manifest_path=programme_task_manifest,
        entrypoint="provider_invocation",
    )
    orchestrator_receipt_sha256 = admit_orchestrator_receipt(orchestrator_receipt_path)
    if command_manifest_path is not None and not structured_decision:
        raise ValueError("command manifests require structured verifier decisions")
    packet = packet_path.read_text(encoding="utf-8")
    if not packet.strip():
        raise ValueError("worker packet must not be empty")
    before = inspect_worktree(cwd, require_clean=True)
    command_manifest = (
        load_command_manifest(command_manifest_path)
        if command_manifest_path is not None
        else None
    )
    canonical_model = LEGACY_MODEL_ALIASES.get(model, model)
    reasoning_effort = MODEL_EFFORTS.get(canonical_model)
    if reasoning_effort is None:
        raise ValueError(f"unsupported Antigravity model: {model}")
    started = time.monotonic()
    completed = subprocess.run(
        build_command(
            packet=packet,
            state=before,
            model=model,
            os_sandbox=os_sandbox,
            structured_decision=structured_decision,
            command_manifest=command_manifest,
        ),
        cwd=before.root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    elapsed_ms = round((time.monotonic() - started) * 1000)
    if completed.returncode != 0:
        after = inspect_worktree(before.root, require_clean=False)
        failure_receipt: dict[str, Any] = {
            "schema_version": "ariadne.transport-failure-receipt.v1",
            "status": "transport_failed_without_terminal_decision",
            "transport": "antigravity_new_project_bound_readonly_worktree",
            "model": canonical_model,
            "requested_model": model,
            "reasoning_effort": reasoning_effort,
            "worktree": str(before.root),
            "branch": before.branch,
            "head_before": before.head,
            "head_after": after.head,
            "dirty_after": after.dirty,
            "worktree_identity_unchanged": (
                after.root == before.root
                and after.branch == before.branch
                and after.head == before.head
                and not after.dirty
            ),
            "os_sandbox": os_sandbox,
            "orchestrator_receipt_sha256": orchestrator_receipt_sha256,
            "exit_code": completed.returncode,
            "elapsed_ms": elapsed_ms,
            "print_timeout_seconds": PRINT_TIMEOUT_SECONDS,
            "print_timeout_boundary_reached": (
                elapsed_ms >= (PRINT_TIMEOUT_SECONDS * 1000 - 5000)
            ),
            "stdout": _output_evidence(completed.stdout or ""),
            "stderr": _output_evidence(completed.stderr or ""),
            "terminal_decision_returned": False,
            "candidate_review_admitted": False,
        }
        if command_manifest is not None:
            failure_receipt["command_manifest_sha256"] = command_manifest_sha256(
                command_manifest
            )
        _atomic_receipt_write(output_path, failure_receipt)
        raise RuntimeError(
            f"Antigravity transport failed ({completed.returncode}); "
            f"digest-only diagnostics written to {output_path}"
        )
    after = inspect_worktree(before.root, require_clean=False)
    worktree_identity_unchanged = (
        after.root == before.root
        and after.branch == before.branch
        and after.head == before.head
        and not after.dirty
    )
    if not worktree_identity_unchanged:
        escaped_binding = after.root != before.root or after.branch != before.branch
        error = (
            "Antigravity changed or escaped its bound worktree/branch"
            if escaped_binding
            else "Antigravity verifier modified its read-only candidate worktree"
        )
        failure_receipt = {
            "schema_version": "ariadne.egress-failure-receipt.v1",
            "status": "egress_failed_without_admitted_terminal_decision",
            "transport": "antigravity_new_project_bound_readonly_worktree",
            "model": canonical_model,
            "requested_model": model,
            "reasoning_effort": reasoning_effort,
            "worktree": str(before.root),
            "branch": before.branch,
            "head_before": before.head,
            "head_after": after.head,
            "dirty_after": after.dirty,
            "worktree_identity_unchanged": False,
            "os_sandbox": os_sandbox,
            "orchestrator_receipt_sha256": orchestrator_receipt_sha256,
            "exit_code": completed.returncode,
            "elapsed_ms": elapsed_ms,
            "stdout": _output_evidence(completed.stdout or ""),
            "stderr": _output_evidence(completed.stderr or ""),
            "decision_contract": (
                "schema_constrained_json_v1"
                if structured_decision
                else "legacy_terminal_line_v1"
            ),
            "reason_code": (
                "bound_worktree_or_branch_changed"
                if escaped_binding
                else "read_only_worktree_postcondition_failed"
            ),
            "terminal_decision_admitted": False,
            "candidate_review_admitted": False,
        }
        if command_manifest is not None:
            failure_receipt["command_manifest_sha256"] = command_manifest_sha256(
                command_manifest
            )
        _atomic_receipt_write(output_path, failure_receipt)
        raise RuntimeError(f"{error}; digest-only diagnostics written to {output_path}")
    try:
        if structured_decision:
            decision_envelope = parse_structured_decision(
                completed.stdout,
                command_manifest,
            )
            decision = decision_envelope["decision"]
            result = decision_envelope["review"]
            decision_contract = "schema_constrained_json_v1"
        else:
            decisions = DECISION_PATTERN.findall(completed.stdout)
            if len(decisions) != 1:
                raise RuntimeError(
                    "Antigravity verifier must return exactly one terminal decision; "
                    f"observed {len(decisions)}"
                )
            decision = decisions[0]
            result = completed.stdout.strip()
            decision_envelope = None
            decision_contract = "legacy_terminal_line_v1"
    except RuntimeError as error:
        failure_receipt = {
            "schema_version": "ariadne.egress-failure-receipt.v1",
            "status": "egress_failed_without_admitted_terminal_decision",
            "transport": "antigravity_new_project_bound_readonly_worktree",
            "model": canonical_model,
            "requested_model": model,
            "reasoning_effort": reasoning_effort,
            "worktree": str(before.root),
            "branch": before.branch,
            "head_before": before.head,
            "head_after": after.head,
            "dirty_after": after.dirty,
            "worktree_identity_unchanged": True,
            "os_sandbox": os_sandbox,
            "orchestrator_receipt_sha256": orchestrator_receipt_sha256,
            "exit_code": completed.returncode,
            "elapsed_ms": elapsed_ms,
            "stdout": _output_evidence(completed.stdout or ""),
            "stderr": _output_evidence(completed.stderr or ""),
            "decision_contract": (
                "schema_constrained_json_v1"
                if structured_decision
                else "legacy_terminal_line_v1"
            ),
            "reason_code": (
                "structured_decision_envelope_not_admitted"
                if structured_decision
                else "legacy_terminal_decision_not_admitted"
            ),
            "terminal_decision_admitted": False,
            "candidate_review_admitted": False,
        }
        if command_manifest is not None:
            failure_receipt["command_manifest_sha256"] = command_manifest_sha256(
                command_manifest
            )
        _atomic_receipt_write(output_path, failure_receipt)
        raise RuntimeError(
            f"{error}; digest-only diagnostics written to {output_path}"
        ) from error
    receipt = {
        "schema_version": "ariadne.worker_receipt.v1",
        "status": "completed",
        "transport": "antigravity_new_project_bound_readonly_worktree",
        "model": canonical_model,
        "requested_model": model,
        "reasoning_effort": reasoning_effort,
        "decision": decision,
        "decision_contract": decision_contract,
        "worktree": str(before.root),
        "branch": before.branch,
        "head_before": before.head,
        "head_after": after.head,
        "dirty_after": after.dirty,
        "os_sandbox": os_sandbox,
        "orchestrator_receipt_sha256": orchestrator_receipt_sha256,
        "result": result,
    }
    if decision_envelope is not None:
        receipt["decision_envelope"] = decision_envelope
    if command_manifest is not None:
        receipt["command_manifest_sha256"] = command_manifest_sha256(command_manifest)
        receipt["command_results"] = decision_envelope["command_results"]
    _atomic_receipt_write(output_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a worktree-bound Gemini verifier."
    )
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--orchestrator-receipt", type=Path, required=True)
    parser.add_argument("--programme-task-manifest", type=Path)
    parser.add_argument(
        "--command-manifest",
        type=Path,
        help="Optional exact structured argv manifest bound into review egress.",
    )
    parser.add_argument("--model", choices=sorted(MODELS), default=DEFAULT_MODEL)
    parser.add_argument(
        "--os-sandbox",
        action="store_true",
        help="Enable agy OS sandboxing; Windows may request elevation.",
    )
    parser.add_argument(
        "--legacy-text-decision",
        action="store_true",
        help="Use historical terminal-line admission instead of structured JSON.",
    )
    args = parser.parse_args()
    try:
        require_programme_admission(
            repo_root=REPO_ROOT,
            manifest_path=args.programme_task_manifest,
            entrypoint="provider_invocation",
        )
        receipt = run_worker(
            packet_path=args.packet.resolve(),
            cwd=args.cwd.resolve(),
            output_path=args.output.resolve(),
            orchestrator_receipt_path=args.orchestrator_receipt.resolve(),
            model=args.model,
            os_sandbox=args.os_sandbox,
            structured_decision=not args.legacy_text_decision,
            command_manifest_path=(
                args.command_manifest.resolve()
                if args.command_manifest is not None
                else None
            ),
            programme_task_manifest=args.programme_task_manifest,
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Antigravity verifier failed: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                key: receipt[key]
                for key in (
                    "status",
                    "transport",
                    "model",
                    "reasoning_effort",
                    "decision",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
