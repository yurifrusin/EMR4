"""Integrity checks for the compact Current Baton acceptance lookup ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import compact_agents_acceptance_index

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT / "docs" / "handover-ledgers" / "current-baton-acceptance-index.manifest.json"
)


def _row_labels(markdown: str, *, after_header: str) -> list[str]:
    lines = markdown.splitlines()
    header = lines.index(after_header)
    return [
        line.split("|", 2)[1].strip()
        for line in lines[header + 2 :]
        if line.startswith("| ")
    ]


def test_acceptance_index_matches_hash_bound_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    ledger_path = ROOT / manifest["ledger_path"]
    payload = ledger_path.read_bytes()

    assert (
        manifest["schema_version"] == "emr4.current_baton_acceptance_index_manifest.v1"
    )
    assert manifest["source_agents_path"] == "AGENTS.md"
    assert manifest["source_git_head"] == ("bc066a1b639c5c57cc72f2697c063c5842511840")
    assert manifest["source_agents_sha256"] == (
        "cf98f5bef0b2ff1f9f309fc919d47e97fc45786a017f6f201843526ca6613ce3"
    )
    assert manifest["source_agents_byte_count"] == 74538
    assert manifest["source_agents_line_count"] == 482
    assert len(payload) == manifest["ledger_byte_count"]
    assert len(payload.decode("utf-8").splitlines()) == manifest["ledger_line_count"]
    assert hashlib.sha256(payload).hexdigest() == manifest["ledger_sha256"]

    ledger_labels = _row_labels(
        payload.decode("utf-8"),
        after_header="| Item | Indexed acceptance artifacts |",
    )
    assert ledger_labels == manifest["moved_labels"]
    assert len(ledger_labels) == manifest["moved_row_count"] == 161


def test_live_baton_keeps_active_rows_and_routes_every_moved_row_to_index() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    live_bytes = (ROOT / "AGENTS.md").read_bytes()
    live = live_bytes.decode("utf-8")
    baton = live.split("### Compact historical evaluation", 1)[0]
    live_labels = _row_labels(baton, after_header="| Item | Current value |")

    # Keep only current authority, active acceptance and future-direction rows
    # in the live rehydration surface; historical acceptance remains hash-bound.
    assert len(live_bytes) < 75_000
    assert len(live.splitlines()) < 500
    assert "Current Baton acceptance index" in live_labels
    for label in manifest["active_labels"]:
        assert label in live_labels
    assert not set(manifest["moved_labels"]).intersection(live_labels)
    assert "artifact lookup authority only" in live
    assert "current-baton-acceptance-index.manifest.json" in live


def test_compaction_check_rejects_an_unclassified_new_live_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    live_path = tmp_path / "AGENTS.md"
    live = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    live = live.replace(
        "### Compact historical evaluation",
        "| Unexpected future row | unclassified |\n### Compact historical evaluation",
        1,
    )
    live_path.write_text(live, encoding="utf-8")
    monkeypatch.setattr(compact_agents_acceptance_index, "AGENTS_PATH", live_path)

    with pytest.raises(ValueError, match="unclassified live Current Baton rows"):
        compact_agents_acceptance_index.check_compaction()


def test_compaction_refresh_replaces_an_existing_indexed_label(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    live_path = tmp_path / "AGENTS.md"
    ledger_path = tmp_path / "current-baton-acceptance-index.md"
    manifest_path = tmp_path / "current-baton-acceptance-index.manifest.json"
    live_path.write_bytes((ROOT / "AGENTS.md").read_bytes())
    ledger_path.write_bytes(
        (ROOT / "docs/handover-ledgers/current-baton-acceptance-index.md").read_bytes()
    )
    monkeypatch.setattr(compact_agents_acceptance_index, "AGENTS_PATH", live_path)
    monkeypatch.setattr(compact_agents_acceptance_index, "LEDGER_PATH", ledger_path)
    monkeypatch.setattr(compact_agents_acceptance_index, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(compact_agents_acceptance_index, "ROOT", tmp_path)
    monkeypatch.setattr(
        compact_agents_acceptance_index,
        "_source_head",
        lambda: "a" * 40,
    )

    manifest = compact_agents_acceptance_index.write_compaction()
    ledger = ledger_path.read_text(encoding="utf-8")
    label = "| Reception One same-update-family multi-change editor composition acceptance |"

    assert ledger.count(label) == 1
    assert "revision-280.md" in next(
        line for line in ledger.splitlines() if line.startswith(label)
    )
    assert (
        manifest["moved_labels"].count(
            "Reception One same-update-family multi-change editor composition acceptance"
        )
        == 1
    )
