"""Inventory local historical diary trove files without exposing PHI.

The raw historical diary trove is expected to live under ignored local paths
such as ``local_data/historical-diary-trove/raw/pilot``. This script deliberately
does not emit filenames, raw paths, document text, document metadata strings, or
other potentially identifying values. It reports only aggregate counts, sizes,
timestamp ranges, extension distributions, and non-reversible content hash
prefixes for deduplication diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PILOT_ROOT = Path("local_data/historical-diary-trove/raw/pilot")
DEFAULT_OUTPUT = Path("local_data/historical-diary-trove/inventory/pilot_inventory.json")


@dataclass(frozen=True)
class FileFacts:
    extension: str
    size_bytes: int
    modified_at: datetime
    digest_prefix: str
    signature_prefix: str


def _hash_prefix(path: Path, *, prefix_chars: int = 12) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:prefix_chars]


def _signature_prefix(path: Path, *, bytes_to_read: int = 8) -> str:
    with path.open("rb") as handle:
        return handle.read(bytes_to_read).hex()


def _iter_file_facts(root: Path) -> list[FileFacts]:
    facts: list[FileFacts] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        stat = path.stat()
        facts.append(
            FileFacts(
                extension=path.suffix.lower() or "<none>",
                size_bytes=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                digest_prefix=_hash_prefix(path),
                signature_prefix=_signature_prefix(path),
            )
        )
    return facts


def _size_buckets(facts: list[FileFacts]) -> dict[str, int]:
    buckets = {
        "0_bytes": 0,
        "1_to_10kb": 0,
        "10kb_to_100kb": 0,
        "100kb_to_1mb": 0,
        "over_1mb": 0,
    }
    for fact in facts:
        if fact.size_bytes == 0:
            buckets["0_bytes"] += 1
        elif fact.size_bytes <= 10 * 1024:
            buckets["1_to_10kb"] += 1
        elif fact.size_bytes <= 100 * 1024:
            buckets["10kb_to_100kb"] += 1
        elif fact.size_bytes <= 1024 * 1024:
            buckets["100kb_to_1mb"] += 1
        else:
            buckets["over_1mb"] += 1
    return buckets


def _timestamp_gap_summary(facts: list[FileFacts]) -> dict[str, Any]:
    ordered = sorted(facts, key=lambda fact: fact.modified_at)
    gaps_seconds = [
        int((later.modified_at - earlier.modified_at).total_seconds())
        for earlier, later in zip(ordered, ordered[1:])
    ]
    if not gaps_seconds:
        return {
            "count": 0,
            "min_seconds": None,
            "max_seconds": None,
            "median_seconds": None,
            "over_1_hour": 0,
            "over_1_day": 0,
        }

    sorted_gaps = sorted(gaps_seconds)
    median = sorted_gaps[len(sorted_gaps) // 2]
    return {
        "count": len(gaps_seconds),
        "min_seconds": sorted_gaps[0],
        "max_seconds": sorted_gaps[-1],
        "median_seconds": median,
        "over_1_hour": sum(1 for gap in gaps_seconds if gap > 60 * 60),
        "over_1_day": sum(1 for gap in gaps_seconds if gap > 24 * 60 * 60),
    }


def _files_per_modified_day(facts: list[FileFacts]) -> dict[str, int]:
    per_day: Counter[str] = Counter()
    for fact in facts:
        per_day[fact.modified_at.date().isoformat()] += 1
    return dict(sorted(per_day.items()))


def _duplicate_digest_prefixes(facts: list[FileFacts]) -> dict[str, int]:
    counts: Counter[str] = Counter(fact.digest_prefix for fact in facts)
    return dict(sorted((digest, count) for digest, count in counts.items() if count > 1))


def _signature_counts(facts: list[FileFacts]) -> dict[str, int]:
    counts: Counter[str] = Counter(fact.signature_prefix for fact in facts)
    return dict(sorted(counts.items()))


def build_inventory(root: Path) -> dict[str, Any]:
    resolved = root.resolve()
    facts = _iter_file_facts(resolved)
    extensions: Counter[str] = Counter(fact.extension for fact in facts)
    total_bytes = sum(fact.size_bytes for fact in facts)
    modified_times = [fact.modified_at for fact in facts]
    extension_sizes: defaultdict[str, int] = defaultdict(int)
    for fact in facts:
        extension_sizes[fact.extension] += fact.size_bytes

    return {
        "schema_version": "historical_diary_inventory.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root_label": resolved.name,
        "privacy_note": (
            "No filenames, raw paths, document text, metadata strings, or PHI-bearing "
            "values are included."
        ),
        "file_count": len(facts),
        "total_bytes": total_bytes,
        "extension_counts": dict(sorted(extensions.items())),
        "extension_total_bytes": dict(sorted(extension_sizes.items())),
        "size_buckets": _size_buckets(facts),
        "modified_time_range_utc": {
            "min": min(modified_times).isoformat() if modified_times else None,
            "max": max(modified_times).isoformat() if modified_times else None,
        },
        "files_per_modified_day": _files_per_modified_day(facts),
        "timestamp_gap_summary": _timestamp_gap_summary(facts),
        "file_signature_prefix_counts": _signature_counts(facts),
        "duplicate_digest_prefixes": _duplicate_digest_prefixes(facts),
    }


def _write_json(path: Path, inventory: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_PILOT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--print-summary",
        action="store_true",
        help="Print a non-PHI JSON summary to stdout.",
    )
    args = parser.parse_args()

    if not args.root.exists():
        raise SystemExit(f"Inventory root does not exist: {args.root}")

    inventory = build_inventory(args.root)
    _write_json(args.output, inventory)

    if args.print_summary:
        summary = {
            "file_count": inventory["file_count"],
            "total_bytes": inventory["total_bytes"],
            "extension_counts": inventory["extension_counts"],
            "modified_time_range_utc": inventory["modified_time_range_utc"],
            "timestamp_gap_summary": inventory["timestamp_gap_summary"],
            "file_signature_prefix_counts": inventory["file_signature_prefix_counts"],
            "duplicate_digest_prefix_count": len(inventory["duplicate_digest_prefixes"]),
            "output": str(args.output),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
