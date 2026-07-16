"""Create the committed unconsumed LC4V7 manifest and seal without evaluation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.lc4v7_content_blind_framework import (
    ACCEPTANCE_RULE_PATH,
    CONTRACT_PATH,
    CREATED_BY,
    MANIFEST_SCHEMA,
    SEAL_SCHEMA,
    canonical_sha256,
    expected_framework_hashes,
    file_sha256,
    load_json_object,
    population_summary,
    validate_corpus,
    validate_manifest,
    validate_seal_envelope,
)


ATTEMPT_ID = "lc4v7-fresh-certification-001"
HOLDOUT_DIR = ROOT / "tests" / "fixtures" / "bernie_lc4v7_holdout"
CORPUS_PATH = HOLDOUT_DIR / "corpus.json"
MANIFEST_PATH = HOLDOUT_DIR / "manifest.json"
SEAL_PATH = HOLDOUT_DIR / "seal.json"


def _committed_corpus(source_commit: str) -> dict:
    relative = CORPUS_PATH.relative_to(ROOT).as_posix()
    completed = subprocess.run(
        ["git", "show", f"{source_commit}:{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("committed corpus must be an object")
    return payload


def build_manifest_and_seal(source_commit: str) -> tuple[dict, dict]:
    corpus = load_json_object(CORPUS_PATH)
    errors = validate_corpus(corpus)
    if errors:
        raise ValueError("live corpus is structurally invalid")
    committed = _committed_corpus(source_commit)
    corpus_hash = canonical_sha256(corpus)
    if canonical_sha256(committed) != corpus_hash:
        raise ValueError("committed corpus hash does not match live corpus")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=ROOT,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        raise ValueError("corpus source is not an ancestor of HEAD")
    population = population_summary(corpus["scenarios"])
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "attempt_id": ATTEMPT_ID,
        "source_commit": source_commit,
        "contract_hash": file_sha256(ROOT / CONTRACT_PATH),
        "acceptance_rule_hash": file_sha256(ROOT / ACCEPTANCE_RULE_PATH),
        "framework_hashes": expected_framework_hashes(),
        "corpus_hash": corpus_hash,
        "corpus_population": population,
        "created_by": CREATED_BY,
    }
    if validate_manifest(
        manifest,
        corpus_hash=corpus_hash,
        source_commit=source_commit,
        population=population,
    ):
        raise ValueError("generated manifest failed exact validation")
    seal = {
        "schema_version": SEAL_SCHEMA,
        "attempt_id": ATTEMPT_ID,
        "source_commit": source_commit,
        "manifest_hash": canonical_sha256(manifest),
        "corpus_hash": corpus_hash,
        "state": "unconsumed",
        "consumed_at": None,
        "consumed_reason": None,
    }
    if validate_seal_envelope(seal):
        raise ValueError("generated seal failed exact validation")
    return manifest, seal


def write_manifest_and_seal(source_commit: str) -> tuple[dict, dict]:
    if MANIFEST_PATH.exists() or SEAL_PATH.exists():
        raise ValueError("manifest or seal already exists; overwrite refused")
    manifest, seal = build_manifest_and_seal(source_commit)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    SEAL_PATH.write_text(
        json.dumps(seal, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest, seal


def main() -> int:
    parser = argparse.ArgumentParser(description="Seal the committed fresh LC4V7 corpus.")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        manifest, seal = (
            write_manifest_and_seal(args.source_commit)
            if args.write
            else build_manifest_and_seal(args.source_commit)
        )
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"LC4V7 seal refused: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "attempt_id": ATTEMPT_ID,
                "corpus_hash": manifest["corpus_hash"],
                "manifest_hash": canonical_sha256(manifest),
                "seal_state": seal["state"],
                "source_commit": args.source_commit,
                "wrote": args.write,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
