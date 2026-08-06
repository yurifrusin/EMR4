"""Run a bounded Gemini verifier in an explicitly bound Antigravity project."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MODEL = "gemini-3.6-flash-high"
MODEL_EFFORTS = {
    "gemini-3.5-flash-low": "low",
    "gemini-3.5-flash-medium": "medium",
    "gemini-3.5-flash-high": "high",
    "gemini-3.6-flash-low": "low",
    "gemini-3.6-flash-medium": "medium",
    "gemini-3.6-flash-high": "high",
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
        raise ValueError(f"Antigravity refuses protected or detached branch: {branch!r}")
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
        "30m",
    ]
    if structured_decision:
        command.extend(
            [
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(
                    STRUCTURED_DECISION_SCHEMA,
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            ]
        )
    if os_sandbox:
        command.append("--sandbox")
    return command


def _as_structured_decision(value: object) -> dict[str, str] | None:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None
    if not isinstance(value, dict) or set(value) != {"decision", "review"}:
        return None
    decision = value.get("decision")
    review = value.get("review")
    if decision not in {"pass", "revision_required"}:
        return None
    if not isinstance(review, str) or not review.strip() or len(review) > 40000:
        return None
    if DECISION_PATTERN.search(review):
        return None
    return {"decision": decision, "review": review.strip()}


def parse_structured_decision(stdout: str) -> dict[str, str]:
    try:
        root = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Antigravity structured output was not one JSON value") from error

    candidates: list[dict[str, str]] = []
    direct = _as_structured_decision(root)
    if direct is not None:
        candidates.append(direct)
    if isinstance(root, dict):
        for key in ("structured_output", "result", "response", "output"):
            candidate = _as_structured_decision(root.get(key))
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


def run_worker(
    *,
    packet_path: Path,
    cwd: Path,
    output_path: Path,
    model: str,
    os_sandbox: bool,
    structured_decision: bool = True,
) -> dict:
    packet = packet_path.read_text(encoding="utf-8")
    if not packet.strip():
        raise ValueError("worker packet must not be empty")
    before = inspect_worktree(cwd, require_clean=True)
    canonical_model = LEGACY_MODEL_ALIASES.get(model, model)
    reasoning_effort = MODEL_EFFORTS.get(canonical_model)
    if reasoning_effort is None:
        raise ValueError(f"unsupported Antigravity model: {model}")
    completed = subprocess.run(
        build_command(
            packet=packet,
            state=before,
            model=model,
            os_sandbox=os_sandbox,
            structured_decision=structured_decision,
        ),
        cwd=before.root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Antigravity transport failed ({completed.returncode}): "
            f"{completed.stderr.strip()}"
        )
    after = inspect_worktree(before.root, require_clean=False)
    if after.root != before.root or after.branch != before.branch:
        raise RuntimeError("Antigravity changed or escaped its bound worktree/branch")
    if after.head != before.head or after.dirty:
        raise RuntimeError("Antigravity verifier modified its read-only candidate worktree")
    if structured_decision:
        decision_envelope = parse_structured_decision(completed.stdout)
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
        "result": result,
    }
    if decision_envelope is not None:
        receipt["decision_envelope"] = decision_envelope
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a worktree-bound Gemini verifier.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
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
        receipt = run_worker(
            packet_path=args.packet.resolve(),
            cwd=args.cwd.resolve(),
            output_path=args.output.resolve(),
            model=args.model,
            os_sandbox=args.os_sandbox,
            structured_decision=not args.legacy_text_decision,
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Antigravity transport failed: {error}", file=sys.stderr)
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
