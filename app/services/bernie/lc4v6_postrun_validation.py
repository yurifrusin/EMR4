"""Aggregate-only validation for the permanently consumed LC4V6 attempt."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from app.services.bernie.lc4v6_acceptance_rule import decide_certification
from app.services.bernie.lc4v6_content_blind_framework import (
    ATTEMPT_ID,
    BoundHashes,
    ValidationResult,
    sha256_bytes,
    sha256_payload,
    sha256_text,
    validate_aggregate,
)


def _mapping(path: Path) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def validate_consumed_attempt(root: Path) -> ValidationResult:
    """Validate only aggregate output, receipt, marker, consumed seal, and lock."""
    report_path = root / "lc4v6-aggregate-report.json"
    receipt_path = root / "lc4v6-production-run-receipt.json"
    marker_path = root / "lc4v6-attempt-marker.json"
    seal_path = root / "lc4v6-source-seal.json"
    lock_path = root / "lc4v6-attempt.lock"
    report = _mapping(report_path)
    receipt = _mapping(receipt_path)
    marker = _mapping(marker_path)
    seal = _mapping(seal_path)
    errors: list[str] = []

    if not all(item is not None for item in (report, receipt, marker, seal)):
        return ValidationResult(False, ("required consumed-attempt JSON is absent or malformed",))
    assert report is not None and receipt is not None and marker is not None and seal is not None

    raw_hashes = report.get("hashes")
    try:
        hashes = BoundHashes(**raw_hashes) if isinstance(raw_hashes, Mapping) else None
    except TypeError:
        hashes = None
    if hashes is None or not hashes.valid():
        return ValidationResult(False, ("aggregate bound hashes are malformed",))

    aggregate_validation = validate_aggregate(report, hashes)
    errors.extend(aggregate_validation.errors)
    decision = decide_certification(report, hashes)
    report_hash = sha256_payload(report)
    seal_hash = sha256_payload(seal)

    if seal.get("schema_version") != "lc4v6.source_seal.v1":
        errors.append("consumed seal schema is not exact")
    if seal.get("attempt_id") != ATTEMPT_ID or seal.get("consumed") is not True:
        errors.append("seal is not permanently consumed for the exact attempt")
    if seal.get("hashes") != asdict(hashes) or seal.get("report_hash") != report_hash:
        errors.append("consumed seal bindings are not exact")
    source_commit = seal.get("source_commit")
    if not isinstance(source_commit, str) or sha256_text(source_commit) != hashes.source:
        errors.append("consumed seal source binding is invalid")

    expected_marker = {
        "schema_version": "lc4v6.attempt_marker.v1",
        "attempt_id": ATTEMPT_ID,
        "report_hash": report_hash,
        "consumed_seal_hash": seal_hash,
    }
    if marker != expected_marker:
        errors.append("attempt marker bindings are not exact")

    expected_receipt = {
        "schema_version": "lc4v6.production_run_receipt.v1",
        "attempt_id": ATTEMPT_ID,
        "decision": decision.decision,
        "evidence_gates": dict(decision.evidence_gates),
        "product_gates": dict(decision.product_gates),
        "worst_slice_rate": decision.worst_slice_rate,
        "report_hash": report_hash,
        "marker_file_hash": sha256_bytes(marker_path.read_bytes()),
        "consumed_seal_file_hash": sha256_bytes(seal_path.read_bytes()),
        "hashes": asdict(hashes),
    }
    if receipt != expected_receipt:
        errors.append("production receipt is not an exact recomputation")
    try:
        if lock_path.read_text(encoding="utf-8") != ATTEMPT_ID + "\n":
            errors.append("durable attempt lock is malformed")
    except OSError:
        errors.append("durable attempt lock is absent")
    return ValidationResult(not errors, tuple(dict.fromkeys(errors)))


__all__ = ["validate_consumed_attempt"]
