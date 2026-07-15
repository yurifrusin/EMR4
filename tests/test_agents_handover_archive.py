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


def test_compact_live_handover_retains_required_authority_and_boundaries() -> None:
    live_path = ROOT / "AGENTS.md"
    live = live_path.read_text(encoding="utf-8")

    assert len(live.splitlines()) < 500
    for required in [
        "## 2. Mandatory Rehydration",
        "## 3. Current Baton",
        "## 4. Authority Allocation",
        "## 5. Protected Evidence and Closed Gates",
        "## 6. User Decision Boundaries",
        "GPT Sol",
        "DeepSeek V4 Flash/high via Claude Code `--bare`",
        "DeepSeek Pro is not the Conductor",
        "Protected holdouts v1 and v2 remain sealed",
        "T3.1-T3.4 remain intact and blocked by default",
        "lc4v2-sol-acceptance.md",
        "lc4v2r1-sol-contract.md",
        "lc4v2r1-sol-acceptance.md",
        "complete `0/576`",
    ]:
        assert required in live


def test_live_handover_names_every_required_rehydration_source() -> None:
    live = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for source in [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]:
        assert source in live


def test_live_handover_routes_removed_history_to_verified_snapshot_and_ledgers() -> None:
    live = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["archive_path"] in live
    assert manifest["sha256"] in live
    assert manifest["git_blob_sha1"] in live
    assert manifest["source_commit"] in live

    ledgers = [
        "docs/handover-ledgers/README.md",
        "docs/handover-ledgers/bernie-language-evaluation.md",
        "docs/handover-ledgers/orchestration-and-agent-runtime.md",
        "docs/handover-ledgers/historical-diary-and-interpretation.md",
        "docs/handover-ledgers/product-platform-api-and-security.md",
    ]
    for relative_path in ledgers:
        assert relative_path in live
        assert (ROOT / relative_path).is_file()
