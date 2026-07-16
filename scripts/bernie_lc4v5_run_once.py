"""Sol-only entry point for the single LC4V5 production evaluation."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.services.bernie.lc4v5_holdout_framework import (
    OneShotPaths,
    V5Manifest,
    V5Seal,
    canonical_json_bytes,
    execute_one_shot,
)
from app.services.bernie.lc4v5_production_evaluator import evaluate_v5


ROOT = Path(__file__).resolve().parents[1]
PROTECTED = ROOT / "tests" / "fixtures" / "bernie_lc4v5_protected"
PATHS = OneShotPaths(
    corpus=PROTECTED / "corpus.json",
    manifest=PROTECTED / "manifest.json",
    seal=PROTECTED / "seal.json",
    marker=PROTECTED / "attempt.marker.json",
    report=ROOT / "docs" / "bernie-lc4v5-aggregate-report.json",
    receipt=ROOT / "orchestration" / "agent_inbox" / "codex" / "lc4v5-production-run-receipt.json",
    framework=ROOT / "app" / "services" / "bernie" / "lc4v5_holdout_framework.py",
    evaluator=ROOT / "app" / "services" / "bernie" / "lc4v5_production_evaluator.py",
)


def _source_commit_exists(commit: str) -> bool:
    checks = (
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        ["git", "cat-file", "-e", f"{commit}:tests/fixtures/bernie_lc4v5_protected/corpus.json"],
    )
    return all(
        subprocess.run(command, cwd=ROOT, capture_output=True, check=False).returncode == 0
        for command in checks
    )


def main() -> None:
    manifest = V5Manifest.model_validate_json(PATHS.manifest.read_text(encoding="utf-8"))
    seal = V5Seal.model_validate_json(PATHS.seal.read_text(encoding="utf-8"))
    receipt = execute_one_shot(
        PATHS,
        attempt_id=seal.attempt_id,
        source_commit=manifest.source_commit,
        consumed_at=datetime.now(timezone.utc).isoformat(),
        evaluator=evaluate_v5,
        source_commit_validator=_source_commit_exists,
    )
    print(canonical_json_bytes(receipt).decode("utf-8"))


if __name__ == "__main__":
    main()
