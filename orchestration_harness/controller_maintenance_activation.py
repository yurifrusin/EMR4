"""Pure parsing of inert controller activation consistency records.

This establishes byte and field consistency only.  Supplied digests and the
claimed activated status do not prove independent review, acceptance,
publication, operation authority, or that activation occurred.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from orchestration_harness.controller_maintenance_record import (
    MaintenanceRecordError,
    parse_maintenance_record,
)


class MaintenanceActivationError(ValueError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


@dataclass(frozen=True, slots=True)
class MaintenanceActivation:
    schema_version: str
    status: str
    generation_id: str
    accepted_manifest_sha256: str
    original_controller_commit: str
    original_controller_tree: str
    governing_transition_commit: str
    maintenance_commit: str
    maintenance_tree: str
    maintenance_parent: str
    source_commit: str
    source_tree: str
    journal_base_commit: str
    publication_receipt_sha256: str
    review_record_sha256: str
    review_subject_sha256: str


_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_GENERATION = re.compile(r"[a-z][a-z0-9-]{1,95}\Z")
_KEYS = {
    "schema_version",
    "status",
    "generation_id",
    "accepted_manifest_sha256",
    "original_controller_commit",
    "original_controller_tree",
    "governing_transition_commit",
    "maintenance_commit",
    "maintenance_tree",
    "maintenance_parent",
    "source_commit",
    "source_tree",
    "journal_base_commit",
    "publication_receipt_sha256",
    "review_record_sha256",
    "review_subject_sha256",
}


def _fail(reason: str) -> None:
    raise MaintenanceActivationError(reason)


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("duplicate_key")
        result[key] = value
    return result


def _text(value: Any, pattern: re.Pattern[str], reason: str) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        _fail(reason)
    return value


def _parse_json(payload: bytes) -> dict[str, Any]:
    if type(payload) is not bytes or len(payload) > 65536:
        _fail("payload_invalid")
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_object,
            parse_constant=lambda _value: _fail("json_constant_forbidden"),
        )
    except MaintenanceActivationError:
        raise
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as error:
        raise MaintenanceActivationError("json_invalid") from error
    if type(value) is not dict or set(value) != _KEYS:
        _fail("top_level_shape_invalid")
    return value


def parse_maintenance_activation(
    payload: bytes, *, expected_sha256: str, manifest_payload: bytes
) -> MaintenanceActivation:
    """Parse consistency evidence; no field or digest establishes authority."""
    return _parse_maintenance_activation_core(
        payload,
        expected_sha256=expected_sha256,
        manifest_payload=manifest_payload,
        original_commit="9334903cbdc7fe04e1c58759ca4babf0fd6d453b",
        original_tree="b78dd45caadad2bee651aaec6601a9072a7edeaa",
        governing_commit="f726021a71e08f81529d3eecd807a695f7ba7e3a",
        governing_tree="e2d41bc658e836587c34bbff201462f45beca8c3",
    )


def _parse_maintenance_activation_core(
    payload: bytes,
    *,
    expected_sha256: str,
    manifest_payload: bytes,
    original_commit: str,
    original_tree: str,
    governing_commit: str,
    governing_tree: str,
) -> MaintenanceActivation:
    """Shared consistency parser. The caller authenticates its lineage inputs."""
    expected_original_commit, expected_original_tree = original_commit, original_tree
    if type(expected_sha256) is not str or _HEX64.fullmatch(expected_sha256) is None:
        _fail("expected_sha256_invalid")
    if type(payload) is not bytes or len(payload) > 65536:
        _fail("payload_invalid")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        _fail("payload_sha256_mismatch")
    value = _parse_json(payload)
    if (
        type(value["schema_version"]) is not str
        or value["schema_version"] != "ariadne.g1b2_controller_activation.v1"
    ):
        _fail("schema_version_invalid")
    if type(value["status"]) is not str or value["status"] != "activated":
        _fail("status_invalid")
    generation = _text(value["generation_id"], _GENERATION, "generation_id_invalid")
    accepted = _text(value["accepted_manifest_sha256"], _HEX64, "manifest_hash_invalid")
    original_commit = _text(
        value["original_controller_commit"],
        _HEX40,
        "original_controller_commit_invalid",
    )
    original_tree = _text(
        value["original_controller_tree"], _HEX40, "original_controller_tree_invalid"
    )
    governing = _text(
        value["governing_transition_commit"],
        _HEX40,
        "governing_transition_commit_invalid",
    )
    maintenance = _text(
        value["maintenance_commit"], _HEX40, "maintenance_commit_invalid"
    )
    maintenance_tree = _text(
        value["maintenance_tree"], _HEX40, "maintenance_tree_invalid"
    )
    parent = _text(value["maintenance_parent"], _HEX40, "maintenance_parent_invalid")
    source_commit = _text(value["source_commit"], _HEX40, "source_commit_invalid")
    source_tree = _text(value["source_tree"], _HEX40, "source_tree_invalid")
    journal = _text(value["journal_base_commit"], _HEX40, "journal_base_commit_invalid")
    receipt = _text(
        value["publication_receipt_sha256"], _HEX64, "publication_receipt_hash_invalid"
    )
    review = _text(value["review_record_sha256"], _HEX64, "review_record_hash_invalid")
    subject = _text(
        value["review_subject_sha256"], _HEX64, "review_subject_hash_invalid"
    )
    if governing != parent or governing != governing_commit:
        _fail("governing_parent_invalid")
    if original_commit != expected_original_commit:
        _fail("original_controller_commit_invalid")
    if original_tree != expected_original_tree:
        _fail("original_controller_tree_invalid")
    if maintenance == parent:
        _fail("maintenance_commit_parent_invalid")
    if journal != maintenance:
        _fail("journal_base_commit_invalid")
    try:
        manifest = parse_maintenance_record(manifest_payload, expected_sha256=accepted)
    except MaintenanceRecordError as error:
        raise MaintenanceActivationError("manifest_invalid") from error
    if generation != manifest.generation_id:
        _fail("generation_id_mismatch")
    if manifest.base_commit != governing or maintenance_tree != manifest.candidate_tree:
        _fail("manifest_identity_mismatch")
    if manifest.base_tree != governing_tree:
        _fail("governing_tree_mismatch")
    if source_commit != manifest.source_commit or source_tree != manifest.source_tree:
        _fail("source_identity_mismatch")
    if (
        review != manifest.review_record_sha256
        or subject != manifest.review_subject_sha256
    ):
        _fail("review_identity_mismatch")
    return MaintenanceActivation(
        value["schema_version"],
        value["status"],
        generation,
        accepted,
        original_commit,
        original_tree,
        governing,
        maintenance,
        maintenance_tree,
        parent,
        source_commit,
        source_tree,
        journal,
        receipt,
        review,
        subject,
    )
