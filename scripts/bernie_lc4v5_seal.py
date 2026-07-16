"""Sol-only LC4V5 manifest and unconsumed-seal writer."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from app.services.bernie.lc4v5_holdout_framework import (
    V5Corpus,
    build_manifest,
    canonical_hash,
    canonical_json_bytes,
    create_unconsumed_seal,
    file_hash,
)


ROOT = Path(__file__).resolve().parents[1]
PROTECTED = ROOT / "tests" / "fixtures" / "bernie_lc4v5_protected"
CORPUS = PROTECTED / "corpus.json"
MANIFEST = PROTECTED / "manifest.json"
SEAL = PROTECTED / "seal.json"
FRAMEWORK = ROOT / "app" / "services" / "bernie" / "lc4v5_holdout_framework.py"
EVALUATOR = ROOT / "app" / "services" / "bernie" / "lc4v5_production_evaluator.py"
ATTEMPT_ID = "lc4v5-fresh-attempt-001"


def _source_exists(commit: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}:tests/fixtures/bernie_lc4v5_protected/corpus.json"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--created-at", required=True)
    args = parser.parse_args()
    if not _source_exists(args.source_commit):
        raise SystemExit("source commit does not contain the frozen corpus")
    if MANIFEST.exists() or SEAL.exists():
        raise SystemExit("manifest or seal already exists")
    corpus = V5Corpus.model_validate_json(CORPUS.read_text(encoding="utf-8"))
    manifest = build_manifest(
        corpus,
        source_commit=args.source_commit,
        framework_hash=file_hash(FRAMEWORK),
        evaluator_hash=file_hash(EVALUATOR),
        created_at=args.created_at,
    )
    seal = create_unconsumed_seal(
        manifest,
        attempt_id=ATTEMPT_ID,
        created_at=args.created_at,
    )
    with MANIFEST.open("xb") as handle:
        handle.write(canonical_json_bytes(manifest) + b"\n")
    with SEAL.open("xb") as handle:
        handle.write(canonical_json_bytes(seal) + b"\n")
    print((canonical_json_bytes({
        "attempt_id": ATTEMPT_ID,
        "manifest_hash": canonical_hash(manifest),
        "seal_hash": seal.seal_hash,
        "state": seal.state,
    })).decode("utf-8"))


if __name__ == "__main__":
    main()
