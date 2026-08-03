"""Deterministic provider-free advisory proofreader for Davida tranche 2.

This module is the exact typed interpretation/proofreader envelope of the
accepted Davida provider-free practice-administration advisory tranche. It is
a pure, provider-free, unmounted and unoccupied function with no SQLAlchemy,
model, database, network, provider, memory or clock dependency. It consumes
one accepted authored-synthetic ``PracticeAdministrationContextFrame`` and one
bounded canonical candidate envelope that contains selectors only, then
releases a strict structured, deterministically grounded, non-authoritative
advisory draft or an exact closed rejection.

The proofreader never reads a clock: ``evaluated_at`` is always caller-supplied
and timezone-aware, and the ``datetime`` module is used only as a value type
for the half-open freshness range check. No repair, inference, retry, lookup,
generated prose, partial release or mutation of the supplied context is
permitted.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from pydantic import ValidationError

from app.schemas.practice_administration_advisory import (
    ADVISORY_OPERATIONS,
    AdvisoryCandidateAdapter,
    AdvisoryDraftAdapter,
    AUTHORITY_LABEL,
    CONTEXT_SCHEMA_VERSION,
    DRAFT_SCHEMA_VERSION,
    EVIDENCE_MODE,
    OPERATION_EXPLAIN,
    OPERATION_SUMMARIZE,
    PRESENTATION,
    PracticeAdministrationAdvisoryResultAdapter,
    REASON_AUTHORITY_CEILING_INVALID,
    REASON_CANDIDATE_NONCANONICAL,
    REASON_CANDIDATE_SCHEMA_INVALID,
    REASON_CONTEXT_BOUNDARY_INVALID,
    REASON_CONTEXT_FRAME_INVALID,
    REASON_CONTEXT_REVISION_MISMATCH,
    REASON_DANGLING_DEFAULT_LOCATION,
    REASON_DUPLICATE_SUBJECT_REF,
    REASON_EVALUATED_AT_NAIVE,
    REASON_EVALUATED_AT_OUT_OF_RANGE,
    REASON_INPUT_OVER_BOUNDED,
    REASON_OPERATION_NOT_ALLOWED,
    REASON_RELEASED,
    REASON_SCOPE_MISMATCH,
    REASON_SUBJECT_NOT_RESOLVED,
    REASON_WRONG_SUBJECT_KIND,
    RELEASED_AUTHORITY_CEILING,
    RESULT_SCHEMA_VERSION,
    STATUS_ADVISORY_ONLY,
    TEMPLATE_CODE,
    VERDICT_REJECTED,
    VERDICT_RELEASED,
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

MAX_RAW_CANDIDATE_CHARS = 2048

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class AdvisoryProofreaderInvariantError(RuntimeError):
    """Raised when the proofreader's own construction invariant fails.

    This is a programming-error signal only; it is never a candidate rejection
    and is never reachable from valid context rows or candidates.
    """


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _candidate_hash(candidate: Any) -> str:
    try:
        return _canonical_sha256(candidate)
    except (TypeError, ValueError):
        # A non-JSON-serializable raw candidate is noncanonical. The hash is a
        # fixed deterministic digest of that fact, never of a raw candidate.
        return hashlib.sha256(b"noncanonical-candidate").hexdigest()


def _extract_context_revision(context_frame: Any) -> str:
    if isinstance(context_frame, dict):
        value = context_frame.get("content_revision")
        if isinstance(value, str) and _SHA256_RE.fullmatch(value):
            return value
    return ""


def _validate_result(result: dict[str, Any]) -> dict[str, Any]:
    validated = PracticeAdministrationAdvisoryResultAdapter.validate_python(result)
    return validated.model_dump(mode="json")


def _reject(candidate: Any, context_frame: Any, reason: str) -> dict[str, Any]:
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "verdict": VERDICT_REJECTED,
        "reason": reason,
        "candidate_hash": _candidate_hash(candidate),
        "context_revision": _extract_context_revision(context_frame),
        "repair_performed": False,
        "retry_authorized": False,
    }
    return _validate_result(result)


def _recompute_content_revision(context_json: dict[str, Any]) -> str:
    payload = {
        key: value for key, value in context_json.items() if key != "content_revision"
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _context_boundaries_ok(
    parsed: PracticeAdministrationContextFrame,
) -> bool:
    if [source.model_dump() for source in parsed.blocked_sources] != list(
        BLOCKED_SOURCES
    ):
        return False
    if parsed.authority_ceiling.model_dump() != dict(AUTHORITY_CEILING):
        return False
    if parsed.labels.model_dump() != dict(FRAME_LABELS):
        return False
    practitioners = parsed.frames.practitioners
    locations = parsed.frames.locations
    if practitioners.label != "live_api_fact" or practitioners.projection != "pure":
        return False
    if practitioners.active_only is not True:
        return False
    if practitioners.source != PRACTITIONER_SOURCE:
        return False
    if locations.label != "live_api_fact" or locations.projection != "pure":
        return False
    if locations.active_only is not True:
        return False
    if locations.source != LOCATION_SOURCE:
        return False
    if parsed.observed_at.tzinfo is None or parsed.expires_at.tzinfo is None:
        return False
    if parsed.expires_at - parsed.observed_at != OBSERVED_EXPIRY_INTERVAL:
        return False
    if practitioners.count != len(practitioners.rows):
        return False
    if locations.count != len(locations.rows):
        return False
    practitioner_refs = [row.resource_ref for row in practitioners.rows]
    location_refs = [row.resource_ref for row in locations.rows]
    all_refs = practitioner_refs + location_refs
    if len(all_refs) != len(set(all_refs)):
        return False
    location_ref_set = set(location_refs)
    if any(
        row.default_location_ref is not None
        and row.default_location_ref not in location_ref_set
        for row in practitioners.rows
    ):
        return False
    return True


def _validate_context(
    context_frame: Any,
) -> tuple[PracticeAdministrationContextFrame | None, str | None]:
    if not isinstance(context_frame, dict):
        return None, REASON_CONTEXT_FRAME_INVALID
    try:
        parsed = PracticeAdministrationContextFrame.model_validate(context_frame)
    except (ValidationError, ValueError, TypeError):
        return None, REASON_CONTEXT_FRAME_INVALID
    if not _context_boundaries_ok(parsed):
        return None, REASON_CONTEXT_BOUNDARY_INVALID
    context_json = parsed.model_dump(mode="json")
    # Reject Pydantic coercion or default insertion. The accepted context desk
    # emits this exact JSON shape, so a caller cannot broaden it with values
    # that merely coerce into the parent model.
    if _canonical_sha256(context_frame) != _canonical_sha256(context_json):
        return None, REASON_CONTEXT_FRAME_INVALID
    recomputed = _recompute_content_revision(context_json)
    if recomputed != parsed.content_revision:
        return None, REASON_CONTEXT_REVISION_MISMATCH
    return parsed, None


def _build_grounding(
    paths: list[str],
    *,
    context_revision: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    ordered = sorted(paths)
    return {
        "grounding_paths": list(paths),
        "grounding_digest": _canonical_sha256(
            {
                "context_revision": context_revision,
                "grounding_paths": ordered,
                "payload": payload,
            }
        ),
    }


def _build_context_binding(parsed: PracticeAdministrationContextFrame) -> dict[str, Any]:
    return {
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "practice_ref": parsed.practice_ref,
        "principal_ref": parsed.principal_ref,
        "correlation_id": parsed.correlation_id,
        "content_revision": parsed.content_revision,
    }


def _build_draft_base(
    parsed: PracticeAdministrationContextFrame,
    *,
    grounding_paths: list[str],
    grounded_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": DRAFT_SCHEMA_VERSION,
        "authority_label": AUTHORITY_LABEL,
        "evidence_mode": EVIDENCE_MODE,
        "status": STATUS_ADVISORY_ONLY,
        "presentation": PRESENTATION,
        "template_code": TEMPLATE_CODE,
        "practice_ref": parsed.practice_ref,
        "principal_ref": parsed.principal_ref,
        "correlation_id": parsed.correlation_id,
        "content_revision": parsed.content_revision,
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "authority_ceiling": dict(RELEASED_AUTHORITY_CEILING),
        "grounding": _build_grounding(
            grounding_paths,
            context_revision=parsed.content_revision,
            payload=grounded_payload,
        ),
        "context_binding": _build_context_binding(parsed),
    }


def _release_summary(
    *,
    candidate: dict[str, Any],
    context_frame: Any,
    parsed: PracticeAdministrationContextFrame,
    candidate_hash: str,
) -> dict[str, Any]:
    practitioner_rows = [
        row.model_dump(mode="json") for row in parsed.frames.practitioners.rows
    ]
    location_rows = [
        row.model_dump(mode="json") for row in parsed.frames.locations.rows
    ]
    payload = {
        "practitioner_count": len(practitioner_rows),
        "location_count": len(location_rows),
        "practitioners_with_role_count": sum(
            1 for row in practitioner_rows if row.get("role_label") is not None
        ),
        "practitioners_with_default_location_count": sum(
            1
            for row in practitioner_rows
            if row.get("default_location_ref") is not None
        ),
    }
    draft_dict = _build_draft_base(
        parsed,
        grounding_paths=[PRACTITIONER_SOURCE, LOCATION_SOURCE],
        grounded_payload=payload,
    )
    draft_dict.update(
        {
            "draft_kind": "summary",
            "operation": OPERATION_SUMMARIZE,
            "payload": payload,
        }
    )
    return _release_result(
        candidate=candidate,
        context_frame=context_frame,
        parsed=parsed,
        candidate_hash=candidate_hash,
        draft_dict=draft_dict,
    )


def _release_explain_practitioner(
    *,
    candidate: dict[str, Any],
    context_frame: Any,
    parsed: PracticeAdministrationContextFrame,
    candidate_hash: str,
    subject_ref: str,
) -> dict[str, Any]:
    practitioner_rows = [
        row.model_dump(mode="json") for row in parsed.frames.practitioners.rows
    ]
    location_rows = [
        row.model_dump(mode="json") for row in parsed.frames.locations.rows
    ]
    matches = [
        row for row in practitioner_rows if row["resource_ref"] == subject_ref
    ]
    if len(matches) == 0:
        if any(row["resource_ref"] == subject_ref for row in location_rows):
            return _reject(candidate, context_frame, REASON_WRONG_SUBJECT_KIND)
        return _reject(candidate, context_frame, REASON_SUBJECT_NOT_RESOLVED)
    if len(matches) > 1:
        return _reject(candidate, context_frame, REASON_DUPLICATE_SUBJECT_REF)
    row = matches[0]
    default_location_ref = row.get("default_location_ref")
    if default_location_ref is not None:
        location_matches = [
            item
            for item in location_rows
            if item["resource_ref"] == default_location_ref
        ]
        if len(location_matches) != 1:
            return _reject(
                candidate, context_frame, REASON_DANGLING_DEFAULT_LOCATION
            )
    payload = {
        "resource_ref": row["resource_ref"],
        "display_name": row["display_name"],
        "role_label": row.get("role_label"),
        "active": row.get("active"),
        "default_location_ref": default_location_ref,
    }
    grounding_paths = [PRACTITIONER_SOURCE]
    if default_location_ref is not None:
        grounding_paths.append(LOCATION_SOURCE)
    draft_dict = _build_draft_base(
        parsed,
        grounding_paths=grounding_paths,
        grounded_payload=payload,
    )
    draft_dict.update(
        {
            "draft_kind": "practitioner_explain",
            "operation": OPERATION_EXPLAIN,
            "subject_kind": "practitioner",
            "payload": payload,
        }
    )
    return _release_result(
        candidate=candidate,
        context_frame=context_frame,
        parsed=parsed,
        candidate_hash=candidate_hash,
        draft_dict=draft_dict,
    )


def _release_explain_location(
    *,
    candidate: dict[str, Any],
    context_frame: Any,
    parsed: PracticeAdministrationContextFrame,
    candidate_hash: str,
    subject_ref: str,
) -> dict[str, Any]:
    location_rows = [
        row.model_dump(mode="json") for row in parsed.frames.locations.rows
    ]
    practitioner_rows = [
        row.model_dump(mode="json") for row in parsed.frames.practitioners.rows
    ]
    matches = [
        row for row in location_rows if row["resource_ref"] == subject_ref
    ]
    if len(matches) == 0:
        if any(row["resource_ref"] == subject_ref for row in practitioner_rows):
            return _reject(candidate, context_frame, REASON_WRONG_SUBJECT_KIND)
        return _reject(candidate, context_frame, REASON_SUBJECT_NOT_RESOLVED)
    if len(matches) > 1:
        return _reject(candidate, context_frame, REASON_DUPLICATE_SUBJECT_REF)
    row = matches[0]
    payload = {
        "resource_ref": row["resource_ref"],
        "name": row["name"],
    }
    draft_dict = _build_draft_base(
        parsed,
        grounding_paths=[LOCATION_SOURCE],
        grounded_payload=payload,
    )
    draft_dict.update(
        {
            "draft_kind": "location_explain",
            "operation": OPERATION_EXPLAIN,
            "subject_kind": "location",
            "payload": payload,
        }
    )
    return _release_result(
        candidate=candidate,
        context_frame=context_frame,
        parsed=parsed,
        candidate_hash=candidate_hash,
        draft_dict=draft_dict,
    )


def _release_result(
    *,
    candidate: dict[str, Any],
    context_frame: Any,
    parsed: PracticeAdministrationContextFrame,
    candidate_hash: str,
    draft_dict: dict[str, Any],
) -> dict[str, Any]:
    try:
        draft_validated = AdvisoryDraftAdapter.validate_python(draft_dict)
    except ValidationError as error:
        raise AdvisoryProofreaderInvariantError(
            "advisory_proofreader_internal_draft_invalid"
        ) from error
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "verdict": VERDICT_RELEASED,
        "reason": REASON_RELEASED,
        "candidate_hash": candidate_hash,
        "context_revision": parsed.content_revision,
        "repair_performed": False,
        "retry_authorized": False,
        "draft": draft_validated.model_dump(mode="json"),
    }
    return _validate_result(result)


def proofread_advisory_candidate(
    *,
    candidate: dict[str, Any],
    context_frame: dict[str, Any],
) -> dict[str, Any]:
    """Proofread one advisory candidate over one accepted context frame.

    The candidate is a bounded canonical envelope containing selectors only;
    every released field is constructed by this deterministic proofreader from
    the accepted context. The function never reads a clock, performs no
    repair/inference/retry/lookup and never mutates the supplied context. The
    returned dict is always a schema-valid discriminated released/rejected
    result.
    """
    if not isinstance(candidate, dict):
        return _reject(candidate, context_frame, REASON_CANDIDATE_NONCANONICAL)
    try:
        raw_length = len(
            json.dumps(candidate, sort_keys=True, separators=(",", ":"))
        )
    except (TypeError, ValueError):
        return _reject(candidate, context_frame, REASON_CANDIDATE_NONCANONICAL)
    if raw_length > MAX_RAW_CANDIDATE_CHARS:
        return _reject(candidate, context_frame, REASON_INPUT_OVER_BOUNDED)

    candidate_hash = _candidate_hash(candidate)

    # Frozen order 1: exact operation allowlist; proposal/apply/unknown
    # operations terminate before any interpretation.
    operation = candidate.get("operation")
    if operation not in ADVISORY_OPERATIONS:
        return _reject(candidate, context_frame, REASON_OPERATION_NOT_ALLOWED)

    # Frozen order 2: strict candidate schema and extra-field admission.
    try:
        parsed_candidate = AdvisoryCandidateAdapter.validate_python(candidate)
    except (ValidationError, ValueError, TypeError):
        return _reject(candidate, context_frame, REASON_CANDIDATE_SCHEMA_INVALID)
    if _canonical_sha256(candidate) != _canonical_sha256(
        parsed_candidate.model_dump(mode="json")
    ):
        return _reject(candidate, context_frame, REASON_CANDIDATE_NONCANONICAL)

    # Frozen order 3: validate the accepted context frame, exact blocked
    # sources, authority ceiling and labels; independently recompute the
    # accepted SHA-256 content revision without changing the parent algorithm.
    parsed_context, context_error = _validate_context(context_frame)
    if parsed_context is None:
        return _reject(
            candidate,
            context_frame,
            context_error or REASON_CONTEXT_FRAME_INVALID,
        )

    # Frozen order 4: exact practice/principal/correlation/revision equality.
    if (
        parsed_candidate.practice_ref != parsed_context.practice_ref
        or parsed_candidate.principal_ref != parsed_context.principal_ref
        or parsed_candidate.correlation_id != parsed_context.correlation_id
        or parsed_candidate.content_revision != parsed_context.content_revision
    ):
        return _reject(candidate, context_frame, REASON_SCOPE_MISMATCH)

    # Frozen order 5: caller-supplied timezone-aware evaluated_at in the
    # half-open range [observed_at, expires_at). Never read system time.
    evaluated_at = parsed_candidate.evaluated_at
    if evaluated_at.tzinfo is None:
        return _reject(candidate, context_frame, REASON_EVALUATED_AT_NAIVE)
    if not (parsed_context.observed_at <= evaluated_at < parsed_context.expires_at):
        return _reject(candidate, context_frame, REASON_EVALUATED_AT_OUT_OF_RANGE)

    # Frozen order 6: require the literal-false candidate authority ceiling.
    if (
        parsed_candidate.writes_authorized is not False
        or parsed_candidate.proposal_authorized is not False
        or parsed_candidate.confirmation_authorized is not False
    ):
        return _reject(candidate, context_frame, REASON_AUTHORITY_CEILING_INVALID)

    # Frozen orders 7-8: operation-specific resolution/derivation.
    if parsed_candidate.operation == OPERATION_EXPLAIN:
        if parsed_candidate.subject_kind == "practitioner":
            return _release_explain_practitioner(
                candidate=candidate,
                context_frame=context_frame,
                parsed=parsed_context,
                candidate_hash=candidate_hash,
                subject_ref=parsed_candidate.subject_ref,
            )
        return _release_explain_location(
            candidate=candidate,
            context_frame=context_frame,
            parsed=parsed_context,
            candidate_hash=candidate_hash,
            subject_ref=parsed_candidate.subject_ref,
        )
    return _release_summary(
        candidate=candidate,
        context_frame=context_frame,
        parsed=parsed_context,
        candidate_hash=candidate_hash,
    )


__all__ = [
    "AdvisoryProofreaderInvariantError",
    "MAX_RAW_CANDIDATE_CHARS",
    "proofread_advisory_candidate",
]
