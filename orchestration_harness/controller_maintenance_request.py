"""Pure parsing of externally verified, inert maintenance requests."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from orchestration_harness.controller_maintenance_record import (
    MaintenanceRecord,
    MaintenanceRecordError,
    _path as _record_path,
    parse_maintenance_record,
)


class MaintenanceRequestError(ValueError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class ControllerFile:
    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class OriginalController:
    root: Path
    commit: str
    tree: str
    files: tuple[ControllerFile, ...]


@dataclass(frozen=True, slots=True)
class MaintenanceRequest:
    schema_version: str
    operation: str
    target_root: Path
    scratch_parent: Path
    receipt_directory: Path
    manifest: MaintenanceRecord
    manifest_payload: bytes
    manifest_sha256: str
    review_payload: bytes
    review_id: str
    owner_approval_sha256: str
    remote_policy: MappingProxyType
    protected_refs: MappingProxyType
    preservation_paths: tuple[Path, ...]
    original_controller: OriginalController
    preserved_files: tuple[ControllerFile, ...]


_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_SLUG = re.compile(r"[a-z][a-z0-9-]{0,95}\Z")
_TOP = {
    "schema_version",
    "operation",
    "target_root",
    "scratch_parent",
    "receipt_directory",
    "manifest",
    "manifest_sha256",
    "review",
    "owner_approval_sha256",
    "remote_policy",
    "protected_refs",
    "preservation_paths",
    "original_controller",
    "preserved_files",
}
_REVIEW = {"schema_version", "review_id", "verdict", "findings", "subject_sha256"}
_CONTROLLER = {"root", "commit", "tree", "files"}
_FILE = {"path", "sha256"}
_PROTECTED = frozenset(
    {
        "refs/heads/master",
        "refs/heads/handoff/current",
        "refs/remotes/origin/master",
        "refs/remotes/origin/handoff/current",
    }
)


def _fail(reason: str) -> None:
    raise MaintenanceRequestError(reason)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("duplicate_key")
        value[key] = item
    return value


def canonical_bytes(value: Any) -> bytes:
    """Encode a JSON value with compact sorted keys and UTF-8 bytes."""
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise MaintenanceRequestError("canonical_json_invalid") from error


def _json(payload: bytes) -> dict[str, Any]:
    if type(payload) is not bytes or len(payload) > 65536:
        _fail("payload_invalid")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_object,
            parse_constant=lambda _value: _fail("json_constant_forbidden"),
        )
    except MaintenanceRequestError:
        raise
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as error:
        raise MaintenanceRequestError("json_invalid") from error
    if type(value) is not dict:
        _fail("top_level_shape_invalid")
    return value


def _text(value: Any, pattern: re.Pattern[str], reason: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        _fail(reason)
    return value


def _absolute(value: Any, reason: str) -> Path:
    if type(value) is not str or not value or len(value) > 512 or "\0" in value:
        _fail(reason)
    parts = value.replace("\\", "/").split("/")
    if any(part in {".", ".."} for part in parts) or not Path(value).is_absolute():
        _fail(reason)
    return Path(value)


def _freeze(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if type(value) is list:
        return tuple(_freeze(item) for item in value)
    if type(value) in {str, int, float, bool} or value is None:
        return value
    _fail("remote_policy_value_invalid")


def _files(
    value: Any, *, relative: bool, limit: int, reason: str
) -> tuple[ControllerFile, ...]:
    if type(value) is not list or not 1 <= len(value) <= limit:
        _fail(reason)
    result: list[ControllerFile] = []
    seen: set[str] = set()
    for item in value:
        if type(item) is not dict or set(item) != _FILE:
            _fail(reason)
        path = item["path"]
        if relative:
            try:
                path = _record_path(path)
            except MaintenanceRecordError as error:
                raise MaintenanceRequestError("controller_file_path_invalid") from error
        else:
            path = _absolute(path, "preserved_file_path_invalid").as_posix()
        key = path.casefold()
        if key in seen:
            _fail("controller_file_duplicate")
        seen.add(key)
        result.append(
            ControllerFile(path, _text(item["sha256"], _HEX64, "file_hash_invalid"))
        )
    return tuple(result)


def parse_request(payload: bytes) -> MaintenanceRequest:
    """Parse caller-verified request bytes; parsing grants no authority."""
    value = _json(payload)
    if set(value) != _TOP:
        _fail("top_level_shape_invalid")
    schema = value["schema_version"]
    if type(schema) is not str or schema != "ariadne.maintenance_operation_request.v1":
        _fail("schema_version_invalid")
    operation = value["operation"]
    if type(operation) is not str or operation not in {"evaluate", "execute"}:
        _fail("operation_invalid")
    target = _absolute(value["target_root"], "target_root_invalid")
    scratch = _absolute(value["scratch_parent"], "scratch_parent_invalid")
    receipt = _absolute(value["receipt_directory"], "receipt_directory_invalid")
    manifest_digest = _text(value["manifest_sha256"], _HEX64, "manifest_hash_invalid")
    manifest_payload = canonical_bytes(value["manifest"])
    try:
        manifest = parse_maintenance_record(
            manifest_payload, expected_sha256=manifest_digest
        )
    except (MaintenanceRecordError, TypeError, ValueError) as error:
        raise MaintenanceRequestError("manifest_invalid") from error
    review = value["review"]
    if type(review) is not dict or set(review) != _REVIEW:
        _fail("review_shape_invalid")
    if (
        review["schema_version"] != "ariadne.maintenance_operational_review.v1"
        or review["verdict"] != "PASS"
    ):
        _fail("review_invalid")
    if type(review["schema_version"]) is not str or type(review["verdict"]) is not str:
        _fail("review_invalid")
    review_id = _text(review["review_id"], _SLUG, "review_id_invalid")
    if type(review["findings"]) is not list or review["findings"]:
        _fail("review_findings_invalid")
    subject = _text(review["subject_sha256"], _HEX64, "review_subject_hash_invalid")
    review_payload = canonical_bytes(review)
    if hashlib.sha256(review_payload).hexdigest() != manifest.review_record_sha256:
        _fail("review_record_hash_mismatch")
    if subject != manifest.review_subject_sha256:
        _fail("review_subject_hash_mismatch")
    owner = _text(value["owner_approval_sha256"], _HEX64, "owner_approval_hash_invalid")
    remote = value["remote_policy"]
    if type(remote) is not dict:
        _fail("remote_policy_invalid")
    remote_frozen = _freeze(remote)
    protected = value["protected_refs"]
    if type(protected) is not dict or set(protected) != _PROTECTED:
        _fail("protected_refs_invalid")
    protected_values = {
        key: _text(item, _HEX40, "protected_ref_invalid")
        for key, item in protected.items()
    }
    if len(set(protected_values.values())) != 1:
        _fail("protected_refs_mismatch")
    preservation = value["preservation_paths"]
    if type(preservation) is not list or not 1 <= len(preservation) <= 8:
        _fail("preservation_paths_invalid")
    preservation_paths = tuple(
        _absolute(item, "preservation_path_invalid") for item in preservation
    )
    if len({item.casefold() for item in map(str, preservation_paths)}) != len(
        preservation_paths
    ):
        _fail("preservation_path_duplicate")
    controller = value["original_controller"]
    if type(controller) is not dict or set(controller) != _CONTROLLER:
        _fail("original_controller_invalid")
    original = OriginalController(
        _absolute(controller["root"], "controller_root_invalid"),
        _text(controller["commit"], _HEX40, "controller_commit_invalid"),
        _text(controller["tree"], _HEX40, "controller_tree_invalid"),
        _files(
            controller["files"],
            relative=True,
            limit=16,
            reason="controller_files_invalid",
        ),
    )
    preserved = _files(
        value["preserved_files"],
        relative=False,
        limit=16,
        reason="preserved_files_invalid",
    )
    return MaintenanceRequest(
        schema,
        operation,
        target,
        scratch,
        receipt,
        manifest,
        manifest_payload,
        manifest_digest,
        review_payload,
        review_id,
        owner,
        remote_frozen,
        MappingProxyType(protected_values),
        preservation_paths,
        original,
        preserved,
    )
