"""Pure parsing for inert controller maintenance records.

The supplied digest is an integrity comparison only.  It does not confer
review acceptance, operation admission, or authority; callers must establish
those properties independently before using this inert record.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


class MaintenanceRecordError(ValueError):
    """A maintenance record failed a structural or integrity check."""

    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class MaintenanceFile:
    path: str
    mode: str
    before_sha256: str | None
    after_sha256: str


@dataclass(frozen=True, slots=True)
class MaintenanceRecord:
    schema_version: str
    generation_id: str
    base_commit: str
    base_tree: str
    source_commit: str
    source_tree: str
    candidate_tree: str
    destination_ref: str
    review_record_sha256: str
    review_subject_sha256: str
    changed_files: tuple[MaintenanceFile, ...]
    frozen_files: tuple[MaintenanceFile, ...]


_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_GENERATION = re.compile(r"[a-z][a-z0-9-]{1,95}\Z")
_PATH = re.compile(r"[A-Za-z0-9_./-]+\Z")
_TOP_KEYS = {
    "schema_version",
    "generation_id",
    "base_commit",
    "base_tree",
    "source_commit",
    "source_tree",
    "candidate_tree",
    "destination_ref",
    "review_record_sha256",
    "review_subject_sha256",
    "changed_files",
    "frozen_files",
}
_FILE_KEYS = {"path", "mode", "before_sha256", "after_sha256"}
_DEVICE = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _error(reason: str) -> None:
    raise MaintenanceRecordError(reason)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _error("duplicate_key")
        result[key] = value
    return result


def _string(value: Any, pattern: re.Pattern[str], reason: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        _error(reason)
    return value


def _path(value: Any) -> str:
    if type(value) is not str or len(value) > 512 or _PATH.fullmatch(value) is None:
        _error("path_invalid")
    parts = value.split("/")
    if len(parts) > 32:
        _error("path_invalid")
    prefixes: dict[str, str] = {}
    for index, part in enumerate(parts):
        if part in {"", ".", ".."} or part.lower() == ".git" or part.endswith("."):
            _error("path_invalid")
        if part.split(".", 1)[0].upper() in _DEVICE:
            _error("path_invalid")
        prefix = "/".join(parts[: index + 1])
        prior = prefixes.setdefault(prefix.casefold(), prefix)
        if prior != prefix:
            _error("path_case_alias")
    return value


def _file(value: Any, *, frozen: bool) -> MaintenanceFile:
    if type(value) is not dict or set(value) != _FILE_KEYS:
        _error("file_shape_invalid")
    path = _path(value["path"])
    if type(value["mode"]) is not str or value["mode"] != "100644":
        _error("file_mode_invalid")
    before = value["before_sha256"]
    if before is not None:
        before = _string(before, _HEX64, "file_before_hash_invalid")
    elif frozen:
        _error("frozen_before_hash_invalid")
    after = _string(value["after_sha256"], _HEX64, "file_after_hash_invalid")
    if frozen and before != after:
        _error("frozen_file_changed")
    if not frozen and before == after:
        _error("changed_file_unchanged")
    return MaintenanceFile(path, "100644", before, after)


def _files(value: Any, *, frozen: bool) -> tuple[MaintenanceFile, ...]:
    limit = 128 if frozen else 32
    if type(value) is not list or not value or len(value) > limit:
        _error("file_list_invalid")
    return tuple(_file(item, frozen=frozen) for item in value)


def _check_path_relationships(
    changed: tuple[MaintenanceFile, ...], frozen: tuple[MaintenanceFile, ...]
) -> None:
    seen: dict[str, str] = {}
    paths = [(item.path, "changed") for item in changed] + [
        (item.path, "frozen") for item in frozen
    ]
    full_paths: set[str] = set()
    for path, _kind in paths:
        if path.casefold() in full_paths:
            _error("path_duplicate_or_overlap")
        full_paths.add(path.casefold())
        components = path.split("/")
        for index in range(1, len(components) + 1):
            spelling = "/".join(components[:index])
            key = spelling.casefold()
            prior = seen.get(key)
            if prior is not None and prior != spelling:
                _error("path_case_alias")
            seen[key] = spelling
    for path, _kind in paths:
        parts = path.casefold().split("/")
        for index in range(1, len(parts)):
            if "/".join(parts[:index]) in full_paths:
                _error("path_duplicate_or_overlap")


def parse_maintenance_record(
    payload: bytes, *, expected_sha256: str
) -> MaintenanceRecord:
    """Parse an inert record; the caller-supplied digest grants no authority."""
    if type(expected_sha256) is not str or _HEX64.fullmatch(expected_sha256) is None:
        _error("expected_sha256_invalid")
    if type(payload) is not bytes or len(payload) > 65536:
        _error("payload_invalid")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        _error("payload_sha256_mismatch")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=lambda _value: _error("json_constant_forbidden"),
        )
    except MaintenanceRecordError:
        raise
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as error:
        raise MaintenanceRecordError("json_invalid") from error
    if type(value) is not dict or set(value) != _TOP_KEYS:
        _error("top_level_shape_invalid")
    schema = value["schema_version"]
    if (
        type(schema) is not str
        or schema != "ariadne.g1b2_controller_maintenance_manifest.v1"
    ):
        _error("schema_version_invalid")
    generation = _string(value["generation_id"], _GENERATION, "generation_id_invalid")
    base_commit = _string(value["base_commit"], _HEX40, "base_commit_invalid")
    base_tree = _string(value["base_tree"], _HEX40, "base_tree_invalid")
    source_commit = _string(value["source_commit"], _HEX40, "source_commit_invalid")
    source_tree = _string(value["source_tree"], _HEX40, "source_tree_invalid")
    candidate_tree = _string(value["candidate_tree"], _HEX40, "candidate_tree_invalid")
    destination = value["destination_ref"]
    if (
        type(destination) is not str
        or destination != "refs/heads/codex/raisa-ariadne-recovery-g0"
    ):
        _error("destination_ref_invalid")
    review_record = _string(
        value["review_record_sha256"], _HEX64, "review_record_hash_invalid"
    )
    review_subject = _string(
        value["review_subject_sha256"], _HEX64, "review_subject_hash_invalid"
    )
    changed = _files(value["changed_files"], frozen=False)
    frozen = _files(value["frozen_files"], frozen=True)
    _check_path_relationships(changed, frozen)
    return MaintenanceRecord(
        schema,
        generation,
        base_commit,
        base_tree,
        source_commit,
        source_tree,
        candidate_tree,
        destination,
        review_record,
        review_subject,
        changed,
        frozen,
    )
