"""Probe legacy Word ``.doc`` files without extracting text or filenames.

This H2 feasibility probe reads only OLE compound-document structure and the
non-PHI WordDocument binary header. It never emits filenames, raw paths,
document text, document metadata strings, or user-visible diary content.
Detailed JSON output should stay under ignored ``local_data/`` paths.
"""

from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ROOTS = (
    Path("local_data/historical-diary-trove/raw/pilot"),
    Path("local_data/historical-diary-trove/raw/pilot_01"),
)
DEFAULT_OUTPUT = Path("local_data/historical-diary-trove/inventory/doc_probe.json")

OLE_SIGNATURE = bytes.fromhex("d0cf11e0a1b11ae1")
END_OF_CHAIN = 0xFFFFFFFE
FREE_SECTOR = 0xFFFFFFFF
FAT_SECTOR = 0xFFFFFFFD
DIFAT_SECTOR = 0xFFFFFFFC
MAX_CHAIN_LENGTH = 100_000


@dataclass(frozen=True)
class FileCandidate:
    path: Path
    modified_at: datetime


@dataclass(frozen=True)
class DirectoryEntry:
    name: str
    object_type: int
    start_sector: int
    size_bytes: int


class OleProbeError(RuntimeError):
    """Raised when an OLE container cannot be structurally probed."""


def _read_u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _read_u64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def _sector_offset(sector_id: int, sector_size: int) -> int:
    return 512 + sector_id * sector_size


def _read_sector(blob: bytes, sector_id: int, sector_size: int) -> bytes:
    offset = _sector_offset(sector_id, sector_size)
    return blob[offset : offset + sector_size]


def _read_chain(
    blob: bytes,
    fat: list[int],
    start_sector: int,
    sector_size: int,
    *,
    expected_size: int | None = None,
) -> bytes:
    if start_sector in {FREE_SECTOR, END_OF_CHAIN}:
        return b""

    sectors: list[bytes] = []
    seen: set[int] = set()
    sector = start_sector
    while sector not in {END_OF_CHAIN, FREE_SECTOR}:
        if sector in seen:
            raise OleProbeError("OLE FAT chain loop detected")
        if sector < 0 or sector >= len(fat):
            raise OleProbeError("OLE FAT chain references an out-of-range sector")
        if len(seen) > MAX_CHAIN_LENGTH:
            raise OleProbeError("OLE FAT chain exceeded safety limit")
        seen.add(sector)
        sectors.append(_read_sector(blob, sector, sector_size))
        sector = fat[sector]

    data = b"".join(sectors)
    if expected_size is not None:
        return data[:expected_size]
    return data


def _load_fat(blob: bytes) -> tuple[int, list[int], int]:
    if len(blob) < 512 or blob[:8] != OLE_SIGNATURE:
        raise OleProbeError("Not an OLE compound document")

    sector_shift = _read_u16(blob, 30)
    sector_size = 1 << sector_shift
    if sector_size not in {512, 4096}:
        raise OleProbeError(f"Unexpected OLE sector size: {sector_size}")

    fat_sector_count = _read_u32(blob, 44)
    first_directory_sector = _read_u32(blob, 48)
    first_difat_sector = _read_u32(blob, 68)
    difat_sector_count = _read_u32(blob, 72)

    difat: list[int] = [
        sector
        for sector in struct.unpack_from("<109I", blob, 76)
        if sector not in {FREE_SECTOR, END_OF_CHAIN}
    ]

    next_difat = first_difat_sector
    for _ in range(difat_sector_count):
        if next_difat in {FREE_SECTOR, END_OF_CHAIN}:
            break
        sector_data = _read_sector(blob, next_difat, sector_size)
        values = list(struct.unpack_from(f"<{sector_size // 4}I", sector_data, 0))
        difat.extend(
            sector for sector in values[:-1] if sector not in {FREE_SECTOR, END_OF_CHAIN}
        )
        next_difat = values[-1]

    fat_sector_ids = difat[:fat_sector_count]
    if len(fat_sector_ids) != fat_sector_count:
        raise OleProbeError("OLE FAT sector count mismatch")

    fat: list[int] = []
    for sector_id in fat_sector_ids:
        if sector_id in {FAT_SECTOR, DIFAT_SECTOR, FREE_SECTOR, END_OF_CHAIN}:
            raise OleProbeError("Invalid FAT sector id")
        sector_data = _read_sector(blob, sector_id, sector_size)
        fat.extend(struct.unpack_from(f"<{sector_size // 4}I", sector_data, 0))

    return sector_size, fat, first_directory_sector


def _read_directory(blob: bytes) -> list[DirectoryEntry]:
    sector_size, fat, first_directory_sector = _load_fat(blob)
    directory_stream = _read_chain(blob, fat, first_directory_sector, sector_size)
    entries: list[DirectoryEntry] = []
    for offset in range(0, len(directory_stream), 128):
        entry = directory_stream[offset : offset + 128]
        if len(entry) < 128:
            continue
        name_length = _read_u16(entry, 64)
        object_type = entry[66]
        if object_type == 0 or name_length < 2:
            continue
        raw_name = entry[: max(0, name_length - 2)]
        try:
            name = raw_name.decode("utf-16le", errors="strict")
        except UnicodeDecodeError:
            name = "<undecodable>"
        entries.append(
            DirectoryEntry(
                name=name,
                object_type=object_type,
                start_sector=_read_u32(entry, 116),
                size_bytes=_read_u64(entry, 120),
            )
        )
    return entries


def _read_large_stream(blob: bytes, stream_name: str, max_bytes: int) -> bytes:
    sector_size, fat, _ = _load_fat(blob)
    entries = _read_directory(blob)
    matching = next((entry for entry in entries if entry.name == stream_name), None)
    if matching is None:
        return b""
    if matching.size_bytes == 0:
        return b""
    data = _read_chain(
        blob,
        fat,
        matching.start_sector,
        sector_size,
        expected_size=min(matching.size_bytes, max_bytes),
    )
    return data[:max_bytes]


def _candidate_files(root: Path) -> list[FileCandidate]:
    candidates: list[FileCandidate] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        stat = path.stat()
        candidates.append(
            FileCandidate(
                path=path,
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            )
        )
    return sorted(candidates, key=lambda candidate: candidate.modified_at)


def _dense_day_filter(candidates: list[FileCandidate], dense_days: int) -> list[FileCandidate]:
    if dense_days <= 0:
        return candidates
    day_counts = Counter(candidate.modified_at.date().isoformat() for candidate in candidates)
    selected_days = {
        day for day, _ in day_counts.most_common(dense_days)
    }
    return [
        candidate
        for candidate in candidates
        if candidate.modified_at.date().isoformat() in selected_days
    ]


def _probe_file(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    signature = blob[:8].hex()
    if blob[:8] != OLE_SIGNATURE:
        return {
            "is_ole": False,
            "signature_prefix": signature,
            "streams": {},
            "word_header": None,
            "error": None,
        }

    try:
        entries = _read_directory(blob)
        stream_sizes = {
            entry.name: entry.size_bytes
            for entry in entries
            if entry.object_type == 2
            and entry.name
            in {
                "WordDocument",
                "0Table",
                "1Table",
                "Data",
                "SummaryInformation",
                "\x05SummaryInformation",
                "\x05DocumentSummaryInformation",
            }
        }
        word_header_bytes = _read_large_stream(blob, "WordDocument", 32)
        word_header = None
        if len(word_header_bytes) >= 4:
            word_header = {
                "w_ident_hex": word_header_bytes[:2].hex(),
                "n_fib": _read_u16(word_header_bytes, 2),
            }
        return {
            "is_ole": True,
            "signature_prefix": signature,
            "streams": stream_sizes,
            "word_header": word_header,
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001 - report structural probe failure only.
        return {
            "is_ole": True,
            "signature_prefix": signature,
            "streams": {},
            "word_header": None,
            "error": type(exc).__name__,
        }


def _summarize_root(root: Path, sample_size: int, dense_days: int) -> dict[str, Any]:
    all_candidates = _candidate_files(root)
    dense_candidates = _dense_day_filter(all_candidates, dense_days)
    sampled = dense_candidates[:sample_size] if sample_size > 0 else dense_candidates
    probe_results = [_probe_file(candidate.path) for candidate in sampled]

    stream_presence: Counter[str] = Counter()
    stream_sizes: dict[str, list[int]] = {}
    word_ident_values: Counter[str] = Counter()
    n_fib_values: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    ole_count = 0
    non_ole_count = 0

    for result in probe_results:
        if result["is_ole"]:
            ole_count += 1
        else:
            non_ole_count += 1
        for stream_name in result["streams"]:
            stream_presence[stream_name] += 1
            stream_sizes.setdefault(stream_name, []).append(result["streams"][stream_name])
        if result["word_header"]:
            word_ident_values[result["word_header"]["w_ident_hex"]] += 1
            n_fib_values[str(result["word_header"]["n_fib"])] += 1
        if result["error"]:
            errors[result["error"]] += 1

    return {
        "root_label": root.name,
        "total_file_count": len(all_candidates),
        "dense_day_count_used": dense_days,
        "dense_candidate_count": len(dense_candidates),
        "sampled_file_count": len(sampled),
        "sampled_ole_count": ole_count,
        "sampled_non_ole_count": non_ole_count,
        "stream_presence_counts": dict(sorted(stream_presence.items())),
        "stream_size_ranges": {
            stream_name: {
                "min_bytes": min(sizes),
                "max_bytes": max(sizes),
            }
            for stream_name, sizes in sorted(stream_sizes.items())
        },
        "word_header_w_ident_hex_counts": dict(sorted(word_ident_values.items())),
        "word_header_n_fib_counts": dict(sorted(n_fib_values.items())),
        "probe_error_counts": dict(sorted(errors.items())),
    }


def build_probe(roots: list[Path], sample_size: int, dense_days: int) -> dict[str, Any]:
    return {
        "schema_version": "historical_diary_doc_probe.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "privacy_note": (
            "No filenames, raw paths, document text, metadata strings, or "
            "PHI-bearing values are included."
        ),
        "sample_policy": {
            "sample_size_per_root": sample_size,
            "dense_modified_days_per_root": dense_days,
            "ordering": "filesystem_modified_time_within_dense_days",
        },
        "roots": [_summarize_root(root.resolve(), sample_size, dense_days) for root in roots],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, dest="roots")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--dense-days", type=int, default=2)
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()

    roots = args.roots or list(DEFAULT_ROOTS)
    missing = [root for root in roots if not root.exists()]
    if missing:
        raise SystemExit(f"Probe root does not exist: {missing[0]}")

    payload = build_probe(roots, args.sample_size, args.dense_days)
    _write_json(args.output, payload)

    if args.print_summary:
        summary = {
            "schema_version": payload["schema_version"],
            "sample_policy": payload["sample_policy"],
            "roots": payload["roots"],
            "output": str(args.output),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
