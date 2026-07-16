"""Pre-execution binding checks for the sole LC4V10 attempt."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from app.services.bernie.lc4v10_content_blind_framework import (
    MANIFEST_KEYS,
    MANIFEST_SCHEMA,
    SEAL_KEYS,
    SEAL_SCHEMA,
)
from app.services.bernie import lc4v10_protected_sealing as sealing

ROOT = Path(__file__).resolve().parents[1]


def test_source_commit_is_ancestor_and_every_bound_blob_is_exact() -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert subprocess.run(
        ["git", "merge-base", "--is-ancestor", sealing.SOURCE_COMMIT, head],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    manifest = sealing.build_manifest(ROOT)
    assert set(manifest) == MANIFEST_KEYS
    assert manifest["schema_version"] == MANIFEST_SCHEMA
    assert manifest["corpus_source_commit"] == sealing.SOURCE_COMMIT


def test_durable_manifest_and_unconsumed_seal_are_exact() -> None:
    manifest_bytes = (ROOT / sealing.MANIFEST_PATH).read_bytes()
    seal_bytes = (ROOT / sealing.SEAL_PATH).read_bytes()
    manifest = json.loads(manifest_bytes)
    seal = json.loads(seal_bytes)
    assert manifest == sealing.build_manifest(ROOT)
    assert seal == sealing.build_seal(ROOT, manifest)
    assert set(seal) == SEAL_KEYS
    assert seal["schema_version"] == SEAL_SCHEMA
    assert seal["state"] == "unconsumed"
    canonical_manifest = json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"
    assert seal["manifest_sha256"] == hashlib.sha256(canonical_manifest).hexdigest()


def test_marker_and_report_are_absent_before_the_one_shot() -> None:
    assert not (ROOT / sealing.MARKER_PATH).exists()
    assert not (ROOT / sealing.REPORT_PATH).exists()
