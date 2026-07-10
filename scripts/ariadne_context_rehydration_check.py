"""Read-only context rehydration gate for the Ariadne sidecar harness."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.models import Mandate
from orchestration_harness.rehydration import GitState, build_rehydration_status

DEFAULT_MANDATE_PATH = REPO_ROOT / "orchestration" / "harness_mandates" / "ariadne-sidecar.json"
DEFAULT_CHECKPOINT_PATH = REPO_ROOT / "orchestration" / "harness_checkpoints" / "ariadne-s0.json"
DEFAULT_EVIDENCE_PATH = REPO_ROOT / "orchestration" / "harness_evidence" / "ariadne-s0.json"


def load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_mandate(path: Path) -> Mandate | None:
    payload = load_json_object(path)
    if payload is None:
        return None
    try:
        return Mandate.from_dict(payload)
    except ValueError:
        return None


def inspect_git_state(repo_root: Path) -> GitState:
    def git_output(arguments: list[str]) -> str | None:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip() if completed.returncode == 0 else None

    branch = git_output(["branch", "--show-current"])
    head = git_output(["rev-parse", "HEAD"])
    porcelain = git_output(["status", "--porcelain"])
    return GitState(branch=branch, head=head, dirty=bool(porcelain))


def build_status(
    repo_root: Path,
    mandate_path: Path,
    checkpoint_path: Path,
    evidence_path: Path,
) -> dict[str, Any]:
    return build_rehydration_status(
        git_state=inspect_git_state(repo_root),
        mandate=load_mandate(mandate_path),
        checkpoint=load_json_object(checkpoint_path),
        evidence_ledger_readable=load_json_object(evidence_path) is not None,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Ariadne continuation prerequisites.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--mandate", type=Path, default=DEFAULT_MANDATE_PATH)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT_PATH)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE_PATH)
    args = parser.parse_args()
    status = build_status(args.repo_root, args.mandate, args.checkpoint, args.evidence)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if status["rehydration_status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
