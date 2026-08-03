"""Pure deterministic default-location dry-run for Davida.

This component consumes one already accepted authored-synthetic context frame
and one canonical selector-only candidate. It performs no read, command,
confirmation, apply, write, provider, model, database, network or clock action.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from pydantic import ValidationError

from app.schemas.practice_administration_default_location_proposal import (
    ALLOWED_OPERATIONS,
    ARTIFACT_TYPE,
    CHANGED_PATH,
    CONTEXT_SCHEMA_VERSION,
    DATA_CLASS,
    DefaultLocationProposal,
    DefaultLocationProposalCandidate,
    DefaultLocationProposalResultAdapter,
    EVIDENCE_MODE,
    OPERATION,
    PROPOSAL_SCHEMA_VERSION,
    REASON_CODE,
    REASON_RELEASED,
    RESULT_SCHEMA_VERSION,
    RISK_TIER,
    STATUS,
)
from app.services.practice.practice_administration_context_desk import (
    AUTHORITY_CEILING,
    BLOCKED_SOURCES,
    FRAME_LABELS,
    LOCATION_SOURCE,
    OBSERVED_EXPIRY_INTERVAL,
    PRACTITIONER_SOURCE,
    PracticeAdministrationContextFrame,
)

MAX_RAW_CANDIDATE_CHARS = 3072
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

PROPOSAL_AUTHORITY_CEILING = {
    "command_ready": False,
    "confirmation_authorized": False,
    "apply_authorized": False,
    "writes_authorized": False,
    "provider_executed": False,
    "model_executed": False,
    "database_used": False,
    "network_used": False,
    "model_to_database": False,
}


class DefaultLocationDryRunInvariantError(RuntimeError):
    """Trusted-code construction failed after candidate admission."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _candidate_hash(candidate: Any) -> str:
    try:
        return _sha256(candidate)
    except (TypeError, ValueError):
        return hashlib.sha256(b"noncanonical-candidate").hexdigest()


def _context_revision(context_frame: Any) -> str:
    if isinstance(context_frame, dict):
        revision = context_frame.get("content_revision")
        if isinstance(revision, str) and _SHA256_RE.fullmatch(revision):
            return revision
    return ""


def _validate_result(value: dict[str, Any]) -> dict[str, Any]:
    return DefaultLocationProposalResultAdapter.validate_python(value).model_dump(
        mode="json"
    )


def _reject(candidate: Any, context_frame: Any, reason: str) -> dict[str, Any]:
    return _validate_result(
        {
            "schema_version": RESULT_SCHEMA_VERSION,
            "verdict": "rejected",
            "reason": reason,
            "candidate_hash": _candidate_hash(candidate),
            "context_revision": _context_revision(context_frame),
            "repair_performed": False,
            "retry_authorized": False,
        }
    )


def _context_boundaries_ok(frame: PracticeAdministrationContextFrame) -> bool:
    if [item.model_dump() for item in frame.blocked_sources] != list(BLOCKED_SOURCES):
        return False
    if frame.authority_ceiling.model_dump() != dict(AUTHORITY_CEILING):
        return False
    if frame.labels.model_dump() != dict(FRAME_LABELS):
        return False
    practitioners = frame.frames.practitioners
    locations = frame.frames.locations
    if (
        practitioners.label != "live_api_fact"
        or practitioners.source != PRACTITIONER_SOURCE
        or practitioners.projection != "pure"
        or practitioners.active_only is not True
        or locations.label != "live_api_fact"
        or locations.source != LOCATION_SOURCE
        or locations.projection != "pure"
        or locations.active_only is not True
    ):
        return False
    if frame.observed_at.tzinfo is None or frame.expires_at.tzinfo is None:
        return False
    if frame.expires_at - frame.observed_at != OBSERVED_EXPIRY_INTERVAL:
        return False
    if practitioners.count != len(practitioners.rows):
        return False
    if locations.count != len(locations.rows):
        return False
    practitioner_refs = [row.resource_ref for row in practitioners.rows]
    location_refs = [row.resource_ref for row in locations.rows]
    if len(practitioner_refs) != len(set(practitioner_refs)):
        return False
    if len(location_refs) != len(set(location_refs)):
        return False
    if set(practitioner_refs) & set(location_refs):
        return False
    location_set = set(location_refs)
    if any(
        row.default_location_ref is not None
        and row.default_location_ref not in location_set
        for row in practitioners.rows
    ):
        return False
    return True


def _validate_context(
    context_frame: Any,
) -> tuple[PracticeAdministrationContextFrame | None, str | None]:
    if not isinstance(context_frame, dict):
        return None, "context_frame_invalid"
    try:
        parsed = PracticeAdministrationContextFrame.model_validate(context_frame)
    except (ValidationError, ValueError, TypeError):
        return None, "context_frame_invalid"
    canonical = parsed.model_dump(mode="json")
    if _sha256(context_frame) != _sha256(canonical):
        return None, "context_frame_invalid"
    if not _context_boundaries_ok(parsed):
        return None, "context_boundary_invalid"
    material = {key: value for key, value in canonical.items() if key != "content_revision"}
    if _sha256(material) != parsed.content_revision:
        return None, "context_revision_mismatch"
    return parsed, None


def dry_run_default_location_proposal(
    *, candidate: dict[str, Any], context_frame: dict[str, Any]
) -> dict[str, Any]:
    """Return exactly one dry-run proposal candidate or one closed rejection."""
    if not isinstance(candidate, dict):
        return _reject(candidate, context_frame, "candidate_noncanonical")
    try:
        raw_size = len(_canonical(candidate))
    except (TypeError, ValueError):
        return _reject(candidate, context_frame, "candidate_noncanonical")
    if raw_size > MAX_RAW_CANDIDATE_CHARS:
        return _reject(candidate, context_frame, "input_over_bounded")
    if candidate.get("operation") not in ALLOWED_OPERATIONS:
        return _reject(candidate, context_frame, "operation_not_allowed")
    try:
        parsed_candidate = DefaultLocationProposalCandidate.model_validate(candidate)
    except (ValidationError, ValueError, TypeError):
        return _reject(candidate, context_frame, "candidate_schema_invalid")
    if _sha256(candidate) != _sha256(parsed_candidate.model_dump(mode="json")):
        return _reject(candidate, context_frame, "candidate_noncanonical")

    parsed_context, context_error = _validate_context(context_frame)
    if parsed_context is None:
        return _reject(candidate, context_frame, context_error or "context_frame_invalid")
    if (
        parsed_candidate.practice_ref != parsed_context.practice_ref
        or parsed_candidate.principal_ref != parsed_context.principal_ref
        or parsed_candidate.correlation_id != parsed_context.correlation_id
        or parsed_candidate.content_revision != parsed_context.content_revision
    ):
        return _reject(candidate, context_frame, "scope_mismatch")
    if parsed_candidate.evaluated_at.tzinfo is None:
        return _reject(candidate, context_frame, "evaluated_at_naive")
    if not (
        parsed_context.observed_at
        <= parsed_candidate.evaluated_at
        < parsed_context.expires_at
    ):
        return _reject(candidate, context_frame, "evaluated_at_out_of_range")
    practitioner_rows = parsed_context.frames.practitioners.rows
    location_rows = parsed_context.frames.locations.rows
    practitioner_matches = [
        row
        for row in practitioner_rows
        if row.resource_ref == parsed_candidate.practitioner_ref
    ]
    if not practitioner_matches:
        if any(
            row.resource_ref == parsed_candidate.practitioner_ref
            for row in location_rows
        ):
            return _reject(candidate, context_frame, "wrong_resource_kind")
        return _reject(candidate, context_frame, "practitioner_not_resolved")
    location_matches = [
        row for row in location_rows if row.resource_ref == parsed_candidate.location_ref
    ]
    if not location_matches:
        if any(
            row.resource_ref == parsed_candidate.location_ref
            for row in practitioner_rows
        ):
            return _reject(candidate, context_frame, "wrong_resource_kind")
        return _reject(candidate, context_frame, "location_not_resolved")
    practitioner = practitioner_matches[0]
    if practitioner.default_location_ref == parsed_candidate.location_ref:
        return _reject(candidate, context_frame, "no_change")

    before_state = {
        "practitioner_ref": practitioner.resource_ref,
        "default_location_ref": practitioner.default_location_ref,
    }
    after_state = {
        "practitioner_ref": practitioner.resource_ref,
        "default_location_ref": parsed_candidate.location_ref,
    }
    source_paths = [PRACTITIONER_SOURCE, LOCATION_SOURCE]
    candidate_json = parsed_candidate.model_dump(mode="json")
    proposal_material = {
        "canonical_candidate": candidate_json,
        "context_revision": parsed_context.content_revision,
        "source_paths": source_paths,
        "before_state": before_state,
        "after_state": after_state,
    }
    grounding_material = {
        "canonical_candidate": candidate_json,
        "context_revision": parsed_context.content_revision,
        "source_paths": sorted(source_paths),
        "before_state": before_state,
        "after_state": after_state,
    }
    proposal = {
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "status": STATUS,
        "evidence_mode": EVIDENCE_MODE,
        "data_class": DATA_CLASS,
        "operation": OPERATION,
        "reason_code": REASON_CODE,
        "risk_tier": RISK_TIER,
        "human_confirmation_required": True,
        "context_binding": {
            "context_schema_version": CONTEXT_SCHEMA_VERSION,
            "practice_ref": parsed_context.practice_ref,
            "principal_ref": parsed_context.principal_ref,
            "correlation_id": parsed_context.correlation_id,
            "content_revision": parsed_context.content_revision,
        },
        "evaluated_at": parsed_candidate.evaluated_at,
        "expires_at": parsed_context.expires_at,
        "practitioner_ref": parsed_candidate.practitioner_ref,
        "location_ref": parsed_candidate.location_ref,
        "source_paths": source_paths,
        "changed_paths": [CHANGED_PATH],
        "before_state": before_state,
        "after_state": after_state,
        "proposal_hash": _sha256(proposal_material),
        "grounding_hash": _sha256(grounding_material),
        "authority_ceiling": dict(PROPOSAL_AUTHORITY_CEILING),
    }
    try:
        validated_proposal = DefaultLocationProposal.model_validate(proposal)
    except ValidationError as error:
        raise DefaultLocationDryRunInvariantError(
            "default_location_dry_run_internal_proposal_invalid"
        ) from error
    return _validate_result(
        {
            "schema_version": RESULT_SCHEMA_VERSION,
            "verdict": "released",
            "reason": REASON_RELEASED,
            "candidate_hash": _sha256(candidate_json),
            "context_revision": parsed_context.content_revision,
            "repair_performed": False,
            "retry_authorized": False,
            "proposal_candidate": validated_proposal.model_dump(mode="json"),
        }
    )


__all__ = [
    "DefaultLocationDryRunInvariantError",
    "MAX_RAW_CANDIDATE_CHARS",
    "PROPOSAL_AUTHORITY_CEILING",
    "dry_run_default_location_proposal",
]
