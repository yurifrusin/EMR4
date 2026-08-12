"""Compact inactive Current Baton lookup rows into a hash-bound ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = ROOT / "AGENTS.md"
LEDGER_PATH = ROOT / "docs" / "handover-ledgers" / "current-baton-acceptance-index.md"
MANIFEST_PATH = (
    ROOT / "docs" / "handover-ledgers" / "current-baton-acceptance-index.manifest.json"
)

TABLE_HEADING = "## 3. Current Baton"
TABLE_HEADER = "| Item | Current value |"
TABLE_END = "### Compact historical evaluation and transition state"
INDEX_LABEL = "Current Baton acceptance index"
ACTIVE_LABELS = (
    "Current protected-integration result",
    "Mode",
    "Baton ref",
    "Active development worktree",
    "Worker worktree root",
    "Required Git relation",
    "Conductor/integrator",
    "Implementation/test worker",
    "Independent worker/reviewer",
    "Active Ariadne descendant",
    "Active product track",
    "Antigravity independent-verifier allocation",
    "Ariadne agent error and correction register acceptance",
    "Model-required Bureau architecture and paused development plan",
    "Model-required Bureau C4 allowlisted-actuator simulator acceptance",
    "Model-required Bureau C5 plan and recovery state",
    "Provider-free unmounted durability inert DDL rehearsal acceptance",
    "Agent Execution Surface AES-C4 acceptance",
    "Agent Execution Surface AES-C5 acceptance",
    "Context Fabric CF-D1 concurrency rehearsal acceptance",
    "Ariadne CF-D2 workflow incident diagnosis and fluidity repair acceptance",
    "Provider-free disposable PostgreSQL status-confirm scaffold parse/catalogue rehearsal acceptance",
    "Provider-free read-only status-confirm route-mounting admission review acceptance",
    "Status-confirm preflight idempotency expectation repair acceptance",
    "Current result",
    "Next implementation",
    "Future Consultant clinical direction",
    "Raisa Practice Context Fabric direction",
    "Agent Execution Surface and Containment Gate direction",
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(  # noqa: S324 -- Git object identity, not security
        header + payload,
        usedforsecurity=False,
    ).hexdigest()


def _row_label(line: str) -> str:
    if not line.startswith("| "):
        raise ValueError(f"not a Current Baton row: {line!r}")
    return line.split("|", 2)[1].strip()


def _table_bounds(lines: list[str]) -> tuple[int, int]:
    try:
        section = next(
            i for i, line in enumerate(lines) if line.rstrip() == TABLE_HEADING
        )
        header = next(
            i
            for i in range(section + 1, len(lines))
            if lines[i].rstrip() == TABLE_HEADER
        )
        end = next(
            i for i in range(header + 2, len(lines)) if lines[i].rstrip() == TABLE_END
        )
    except StopIteration as error:
        raise ValueError("Current Baton table markers are incomplete") from error
    return header, end


def _table_rows(lines: list[str], header: int, end: int) -> list[str]:
    rows = [line for line in lines[header + 2 : end] if line.startswith("| ")]
    if not rows:
        raise ValueError("Current Baton table contains no rows")
    labels = [_row_label(row) for row in rows]
    if len(labels) != len(set(labels)):
        raise ValueError("Current Baton row labels must be unique")
    return rows


def _source_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _build_ledger(
    *, moved_rows: list[str], source_head: str, source_hash: str
) -> bytes:
    intro = [
        "# Current Baton acceptance index\n",
        "\n",
        "Date: 2026-08-03\n",
        "\n",
        "Status: hash-bound artifact lookup ledger\n",
        "\n",
        "This ledger preserves historical and inactive acceptance lookup rows moved\n",
        "verbatim from the Current Baton table. It has artifact lookup authority only.\n",
        "Live authority, protected boundaries, active acceptance and next work remain\n",
        "controlled by `AGENTS.md`; this ledger cannot override them.\n",
        "\n",
        f"Source HEAD: `{source_head}`\n",
        f"Source `AGENTS.md` SHA-256: `{source_hash}`\n",
        "\n",
        "| Item | Indexed acceptance artifacts |\n",
        "|---|---|\n",
    ]
    return "".join([*intro, *moved_rows]).encode("utf-8")


def _pointer_row() -> str:
    return (
        "| Current Baton acceptance index | Historical and inactive acceptance "
        "lookup rows are preserved verbatim in "
        "`docs/handover-ledgers/current-baton-acceptance-index.md` and bound by "
        "`docs/handover-ledgers/current-baton-acceptance-index.manifest.json`. "
        "The index has artifact lookup authority only and cannot override this live "
        "authority, protected boundaries, active acceptance or next work. |\n"
    )


def write_compaction() -> dict[str, Any]:
    source_bytes = AGENTS_PATH.read_bytes()
    source_text = source_bytes.decode("utf-8")
    lines = source_text.splitlines(keepends=True)
    header, end = _table_bounds(lines)
    rows = _table_rows(lines, header, end)
    labels = [_row_label(row) for row in rows]
    missing_active = [label for label in ACTIVE_LABELS if label not in labels]
    if missing_active:
        raise ValueError(f"active Current Baton rows missing: {missing_active}")

    active = set(ACTIVE_LABELS)
    kept_rows = [row for row in rows if _row_label(row) in active]
    newly_moved_rows = [
        row
        for row in rows
        if _row_label(row) not in active and _row_label(row) != INDEX_LABEL
    ]
    if INDEX_LABEL in labels:
        ledger_lines = LEDGER_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
        ledger_header = next(
            i for i, line in enumerate(ledger_lines) if line.startswith("| Item |")
        )
        existing_moved_rows = [
            line
            for line in ledger_lines[ledger_header + 2 :]
            if line.startswith("| ") and _row_label(line) not in active
        ]
        moved_rows = [*existing_moved_rows, *newly_moved_rows]
    else:
        moved_rows = newly_moved_rows
    moved_labels = [_row_label(row) for row in moved_rows]
    if len(moved_labels) != len(set(moved_labels)):
        raise ValueError("acceptance-index refresh would duplicate moved labels")
    source_hash = _sha256(source_bytes)
    source_head = _source_head()
    ledger_bytes = _build_ledger(
        moved_rows=moved_rows,
        source_head=source_head,
        source_hash=source_hash,
    )

    manifest = {
        "active_labels": list(ACTIVE_LABELS),
        "generated_date": "2026-08-03",
        "ledger_byte_count": len(ledger_bytes),
        "ledger_line_count": len(ledger_bytes.decode("utf-8").splitlines()),
        "ledger_path": LEDGER_PATH.relative_to(ROOT).as_posix(),
        "ledger_sha256": _sha256(ledger_bytes),
        "moved_labels": moved_labels,
        "moved_row_count": len(moved_rows),
        "schema_version": "emr4.current_baton_acceptance_index_manifest.v1",
        "source_agents_byte_count": len(source_bytes),
        "source_agents_git_blob_sha1": _git_blob_sha1(source_bytes),
        "source_agents_line_count": len(source_text.splitlines()),
        "source_agents_path": AGENTS_PATH.relative_to(ROOT).as_posix(),
        "source_agents_sha256": source_hash,
        "source_git_head": source_head,
    }

    insertion = (
        next(
            i
            for i, row in enumerate(kept_rows)
            if _row_label(row) == "Antigravity independent-verifier allocation"
        )
        + 1
    )
    kept_rows.insert(insertion, _pointer_row())
    replacement = [lines[header], lines[header + 1], *kept_rows]
    compacted_lines = [*lines[:header], *replacement, *lines[end:]]

    LEDGER_PATH.write_bytes(ledger_bytes)
    MANIFEST_PATH.write_bytes(_canonical_json(manifest))
    AGENTS_PATH.write_bytes("".join(compacted_lines).encode("utf-8"))
    return manifest


def check_compaction() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version")
        != "emr4.current_baton_acceptance_index_manifest.v1"
    ):
        raise ValueError("acceptance-index manifest schema is invalid")

    ledger_bytes = LEDGER_PATH.read_bytes()
    if len(ledger_bytes) != manifest.get("ledger_byte_count"):
        raise ValueError("acceptance-index byte count differs from manifest")
    if len(ledger_bytes.decode("utf-8").splitlines()) != manifest.get(
        "ledger_line_count"
    ):
        raise ValueError("acceptance-index line count differs from manifest")
    if _sha256(ledger_bytes) != manifest.get("ledger_sha256"):
        raise ValueError("acceptance-index SHA-256 differs from manifest")

    ledger_lines = ledger_bytes.decode("utf-8").splitlines(keepends=True)
    ledger_header = next(
        i for i, line in enumerate(ledger_lines) if line.startswith("| Item |")
    )
    ledger_rows = [
        line for line in ledger_lines[ledger_header + 2 :] if line.startswith("| ")
    ]
    ledger_labels = [_row_label(row) for row in ledger_rows]
    if ledger_labels != manifest.get("moved_labels"):
        raise ValueError("acceptance-index labels differ from manifest")
    if len(ledger_rows) != manifest.get("moved_row_count"):
        raise ValueError("acceptance-index row count differs from manifest")

    live_lines = AGENTS_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    header, end = _table_bounds(live_lines)
    live_rows = _table_rows(live_lines, header, end)
    live_labels = [_row_label(row) for row in live_rows]
    if INDEX_LABEL not in live_labels:
        raise ValueError("live Current Baton does not point to the acceptance index")
    for label in manifest.get("active_labels", []):
        if label not in live_labels:
            raise ValueError(f"active Current Baton row missing: {label}")
    unexpected_live = sorted(
        set(live_labels) - set(manifest.get("active_labels", [])) - {INDEX_LABEL}
    )
    if unexpected_live:
        raise ValueError(
            "unclassified live Current Baton rows require a deliberate manifest "
            f"revision: {unexpected_live}"
        )
    overlap = sorted(set(ledger_labels).intersection(live_labels))
    if overlap:
        raise ValueError(f"indexed rows remain duplicated in the live Baton: {overlap}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        manifest = write_compaction() if args.write else check_compaction()
    except (
        OSError,
        ValueError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
    ) as error:
        print(f"Current Baton acceptance-index compaction failed: {error}")
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
