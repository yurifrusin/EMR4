"""Integrity checks for immutable AGENTS.md handover snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / "docs"
    / "handover-archive"
    / "AGENTS-2026-07-15-pre-compaction.manifest.json"
)


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 -- Git identity


def test_pre_compaction_snapshot_matches_immutable_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    archive_path = ROOT / manifest["archive_path"]
    payload = archive_path.read_bytes()

    assert manifest["schema_version"] == "emr4.agents_archive_manifest.v1"
    assert manifest["immutable"] is True
    assert len(payload) == manifest["byte_count"]
    assert len(payload.decode("utf-8").splitlines()) == manifest["line_count"]
    assert hashlib.sha256(payload).hexdigest() == manifest["sha256"]
    assert _git_blob_sha1(payload) == manifest["git_blob_sha1"]


def test_archive_index_names_snapshot_and_manifest() -> None:
    index = (ROOT / "docs" / "handover-archive" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "AGENTS-2026-07-15-pre-compaction.md" in index
    assert "AGENTS-2026-07-15-pre-compaction.manifest.json" in index
