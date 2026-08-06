"""Closed contracts and deterministic proofreaders for model-required intent shaping.

This module is provider-aware but performs no network, credential, database,
product, clock or filesystem mutation.  Provider invocation lives in the
separate one-use broker and can release only values admitted here.

The occupied authored-synthetic intent-shaping rehearsal is the first
descendant that places a model between a staff utterance and the accepted
Context Fabric retrieval contract.  The model selects only one closed intent
candidate body.  Deterministic code owns grounding, the trusted parent
``IntentRetrievalCandidate``, the unchanged parent catalog/binding/retrieval,
and the unchanged parent same-packet proofreader.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    canonical_json,
    canonical_sha256,
    seal,
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal import (
    IntentRetrievalViolation,
    build_authored_synthetic_sources,
    build_intent_authority_binding,
    build_intent_candidate,
    build_intent_packet,
    build_source_catalog,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration/continuity"
    / "raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal"
)
REQUEST_SCHEMA_PATH = ARTIFACT_ROOT / "intent-shaping-request.schema.json"
PROVIDER_BODY_SCHEMA_PATH = ARTIFACT_ROOT / "provider-intent-body.schema.json"
CANDIDATE_ENVELOPE_SCHEMA_PATH = (
    ARTIFACT_ROOT / "model-intent-candidate-envelope.schema.json"
)
REQUEST_FIXTURE_PATH = ARTIFACT_ROOT / "authored-synthetic-intent-shaping-request.json"
PARENT_ENGINE_PATH = (
    ROOT
    / "scripts/raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py"
)

PROJECT = "bernie-emr4-dev"
SERVICE_ACCOUNT = (
    "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
)
SCOPE = "https://www.googleapis.com/auth/cloud-platform"
MODEL = "gemini-2.5-flash"
LOCATION = "australia-southeast1"
HOSTNAME = "australia-southeast1-aiplatform.googleapis.com"
PATH = (
    "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
    "publishers/google/models/gemini-2.5-flash:generateContent"
)
POLICY_ID = "raisa-context-fabric-model-required-intent-shaping-sydney-v1"
THINKING_BUDGET = 1024
MAX_OUTPUT_TOKENS = 2048
MAX_PROVIDER_REQUEST_BYTES = 65536
MAX_PROVIDER_RESPONSE_BYTES = 65536
MAX_CELL_REQUEST_BYTES = 32768
MAX_CALLS_TOTAL = 2
MAX_CALLS_PER_LANE = 2
MAX_COST_USD = 0.50
RESERVED_COST_PER_CALL_USD = 0.25
DRY_RUN_MODEL_VERSION = "provider-free-intent-shaping-fixture"

LANE = "rayleen_context_fabric_intent_shaping"
LANES = frozenset({LANE})

SCHEMA_VERSION = "emr4.raisa_intent_shaping.v1"
REQUEST_SCHEMA_VERSION = "emr4.raisa_intent_shaping.request.v1"
BODY_SCHEMA_VERSION = "emr4.raisa_intent_shaping.provider_intent_body.v1"
ENVELOPE_SCHEMA_VERSION = (
    "emr4.raisa_intent_shaping.candidate_envelope.v1"
)
RELEASE_SCHEMA_VERSION = "emr4.raisa_intent_shaping.release.v1"

EVIDENCE_LABEL_PROVIDER_FREE = (
    "provider_free_authored_synthetic_model_intent_shaping"
)
EVIDENCE_LABEL_OCCUPIED = (
    "occupied_authored_synthetic_model_intent_shaping"
)

OCCUPIED_REQUEST_ID = "synthetic:intent-shaping:occupied:rayleen:001"
SYNTHETIC_UTTERANCE = (
    "Compare the current waiting-room operational picture with the earlier "
    "state at 10:30 this morning, using only what was known by 12:30."
)
SYNTHETIC_LABEL = "authored_synthetic"
SYNTHETIC_TIMEZONE = "Australia/Brisbane"
SYNTHETIC_REFERENCE_DATE = "2026-08-06"
SYNTHETIC_COORDINATE_CODE = "SYNTHETIC_1030_VALID_1230_KNOWN"
SYNTHETIC_COORDINATE = {
    "valid_at": "2026-08-06T00:30:00Z",
    "known_at": "2026-08-06T02:30:00Z",
}
OCCUPIED_ISSUED_AT = "2026-08-06T03:00:00Z"
OCCUPIED_EXPIRES_AT = "2026-08-06T03:02:00Z"

INTENT_CODES = (
    "CURRENT_OPERATIONAL_STATUS",
    "RECENT_PRACTICE_WORK",
    "HISTORICAL_OPERATIONAL_STATE",
    "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON",
    "RECENT_OPERATIONAL_REFERENCE",
)
CUE_CODES = (
    "CURRENT_STATE_REQUESTED",
    "PRIOR_STATE_REQUESTED",
    "VALID_TIME_1030",
    "KNOWLEDGE_CUTOFF_1230",
)
AUTHORITY_KEYS = (
    "identity",
    "tenancy",
    "patient",
    "source",
    "provider_tool",
    "database",
    "command",
    "write",
)
CORRECTION_REASON_CODES = frozenset(
    {"provider_body_schema_invalid", "intent_not_grounded"}
)
PREPROOF_TERMINAL_REASON_CODES = frozenset(
    {
        "provider_candidate_count_invalid",
        "provider_parts_count_invalid",
        "provider_part_non_text_invalid",
        "provider_candidate_not_json",
        "provider_candidate_not_object",
        "positive_thinking_evidence_required",
    }
)

# Fixed allowlist of provider-body field labels.  Field-label telemetry may
# name only these keys plus bounded counts; unexpected provider field names or
# values must never be retained in audit/evidence.
BODY_FIELD_ALLOWLIST = frozenset(
    {
        "intent_code",
        "temporal_coordinate_code",
        "cue_codes",
        "response_code",
        *AUTHORITY_KEYS,
    }
)

INTENT_DESCRIPTIONS = {
    "CURRENT_OPERATIONAL_STATUS": (
        "Current coherent operational component only."
    ),
    "RECENT_PRACTICE_WORK": "Bureau Memory component only.",
    "HISTORICAL_OPERATIONAL_STATE": (
        "One bitemporal historical selection only."
    ),
    "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON": (
        "Current plus historical comparison."
    ),
    "RECENT_OPERATIONAL_REFERENCE": (
        "Bounded opaque alternatives from recent-work context."
    ),
}
COORDINATE_DESCRIPTIONS = {
    "NONE": "No temporal coordinate.",
    SYNTHETIC_COORDINATE_CODE: (
        "10:30 valid-time state as known by 12:30."
    ),
}

# Code-owned expected cue sets for provider-free fixtures.  The occupied case
# is grounded independently by :func:`_expected_classification`.
FIXTURE_EXPECTED: dict[str, dict[str, Any]] = {
    "CURRENT_OPERATIONAL_STATUS": {
        "temporal_coordinate_code": "NONE",
        "cue_codes": ["CURRENT_STATE_REQUESTED"],
    },
    "RECENT_PRACTICE_WORK": {
        "temporal_coordinate_code": "NONE",
        "cue_codes": ["CURRENT_STATE_REQUESTED"],
    },
    "HISTORICAL_OPERATIONAL_STATE": {
        "temporal_coordinate_code": SYNTHETIC_COORDINATE_CODE,
        "cue_codes": [
            "PRIOR_STATE_REQUESTED",
            "VALID_TIME_1030",
            "KNOWLEDGE_CUTOFF_1230",
        ],
    },
    "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON": {
        "temporal_coordinate_code": SYNTHETIC_COORDINATE_CODE,
        "cue_codes": list(CUE_CODES),
    },
    "RECENT_OPERATIONAL_REFERENCE": {
        "temporal_coordinate_code": "NONE",
        "cue_codes": ["CURRENT_STATE_REQUESTED"],
    },
}

_COORDINATE_MAPPING: dict[str, dict[str, str] | None] = {
    "NONE": None,
    SYNTHETIC_COORDINATE_CODE: dict(SYNTHETIC_COORDINATE),
}


class ContractError(ValueError):
    """A closed contract or deterministic proofreader rejection."""


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def prefixed_sha256(value: Any) -> str:
    return canonical_sha256(value)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"object_required:{path.name}")
    return value


def validate_instance(schema_path: Path, value: Any) -> None:
    schema = load_object(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        path = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in errors[0].absolute_path
        )
        raise ContractError(f"schema_invalid:{path}")


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ContractError("instant_timezone_required")
    return parsed


def _parent_contract_digest() -> str:
    return "sha256:" + hashlib.sha256(
        PARENT_ENGINE_PATH.read_bytes()
    ).hexdigest()


def _parent_policy_digest() -> str:
    return canonical_sha256("context-fabric-intent-shaped-retrieval.v1")


PARENT_CONTRACT_DIGEST = _parent_contract_digest()
PARENT_POLICY_DIGEST = _parent_policy_digest()


def _all_false(value: dict[str, Any]) -> bool:
    if not isinstance(value, dict):
        return False
    return all(
        key in value and value[key] is False for key in AUTHORITY_KEYS
    )


def _provider_binding() -> dict[str, Any]:
    return {
        "provider": "google_cloud_vertex_ai",
        "model": MODEL,
        "project": PROJECT,
        "service_account": SERVICE_ACCOUNT,
        "authentication": "existing_keyless_impersonated_service_account_adc",
        "oauth_scope": SCOPE,
        "location": LOCATION,
        "endpoint_hostname": HOSTNAME,
        "api_path": PATH,
        "api_key_authentication_used": False,
        "service_account_key_authentication_used": False,
        "fallback_used": False,
        "provider_tools_used": False,
        "grounding_used": False,
        "retrieval_used": False,
        "cached_content_used": False,
    }


def validate_intent_shaping_request(request: dict[str, Any]) -> None:
    validate_instance(REQUEST_SCHEMA_PATH, request)
    try:
        verify_seal(request, "request_digest")
    except ValueError as error:
        raise ContractError("request_digest_mismatch") from error
    generated = _parse_time(request["issued_at"])
    expires = _parse_time(request["expires_at"])
    if not generated < expires:
        raise ContractError("request_expiry_invalid")
    if not _all_false(request["authority_ceiling"]):
        raise ContractError("authority_ceiling_invalid")


def validate_provider_intent_body(body: dict[str, Any]) -> None:
    validate_instance(PROVIDER_BODY_SCHEMA_PATH, body)


def build_intent_shaping_request() -> dict[str, Any]:
    """Return the sealed occupied authored-synthetic request."""
    material = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request_id": OCCUPIED_REQUEST_ID,
        "utterance": SYNTHETIC_UTTERANCE,
        "synthetic_label": SYNTHETIC_LABEL,
        "timezone": SYNTHETIC_TIMEZONE,
        "reference_date": SYNTHETIC_REFERENCE_DATE,
        "intent_codes": [
            {
                "code": code,
                "description": INTENT_DESCRIPTIONS[code],
            }
            for code in INTENT_CODES
        ],
        "temporal_coordinate_codes": [
            {"code": code, "description": COORDINATE_DESCRIPTIONS[code]}
            for code in ("NONE", SYNTHETIC_COORDINATE_CODE)
        ],
        "cue_codes": list(CUE_CODES),
        "parent_contract_digest": PARENT_CONTRACT_DIGEST,
        "parent_policy_digest": PARENT_POLICY_DIGEST,
        "issued_at": OCCUPIED_ISSUED_AT,
        "expires_at": OCCUPIED_EXPIRES_AT,
        "authority_ceiling": {key: False for key in AUTHORITY_KEYS},
    }
    request = seal(material, "request_digest")
    validate_intent_shaping_request(request)
    return request


def provider_response_schema() -> dict[str, Any]:
    """Return the exact closed Vertex response schema for the provider body."""
    ordered = [
        "intent_code",
        "temporal_coordinate_code",
        "cue_codes",
        "response_code",
        *AUTHORITY_KEYS,
    ]
    return {
        "type": "OBJECT",
        "properties": {
            "intent_code": {
                "type": "STRING",
                "enum": list(INTENT_CODES),
            },
            "temporal_coordinate_code": {
                "type": "STRING",
                "enum": ["NONE", SYNTHETIC_COORDINATE_CODE],
            },
            "cue_codes": {
                "type": "ARRAY",
                "items": {"type": "STRING", "enum": list(CUE_CODES)},
                "minItems": 1,
                "maxItems": 4,
                "uniqueItems": True,
            },
            "response_code": {
                "type": "STRING",
                "enum": ["INTENT_CANDIDATE_ONLY"],
            },
            **{key: {"type": "BOOLEAN"} for key in AUTHORITY_KEYS},
        },
        "required": ordered,
        "propertyOrdering": ordered,
    }


def build_prompt(request: dict[str, Any]) -> str:
    validate_intent_shaping_request(request)
    intent_lines = "\n".join(
        f"- {item['code']}: {item['description']}"
        for item in request["intent_codes"]
    )
    coordinate_lines = "\n".join(
        f"- {item['code']}: {item['description']}"
        for item in request["temporal_coordinate_codes"]
    )
    return "\n".join(
        (
            "Interpret the authored-synthetic Context Fabric staff request.",
            "Select exactly one closed intent code, one closed temporal "
            "coordinate code and the closed cue codes that match the request.",
            "AUTHORED_SYNTHETIC_REQUEST:",
            request["utterance"],
            f"SYNTHETIC_LABEL: {request['synthetic_label']}",
            f"TIMEZONE: {request['timezone']}",
            f"REFERENCE_DATE: {request['reference_date']}",
            "INTENT_CODES:",
            intent_lines,
            "TEMPORAL_COORDINATE_CODES:",
            coordinate_lines,
            "CUE_CODES:",
            ", ".join(request["cue_codes"]),
            "Return cue_codes in the canonical CUE_CODES order displayed above.",
            "Return only the selector JSON body matching the response schema.",
            "Never invent an intent, coordinate, cue, identifier, URL, tool, "
            "SQL or command. All authority values must remain false.",
        )
    )


def build_vertex_request(request: dict[str, Any]) -> dict[str, Any]:
    validate_intent_shaping_request(request)
    vertex_request = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": build_prompt(request)}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "candidateCount": 1,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "thinkingConfig": {"thinkingBudget": THINKING_BUDGET},
            "responseMimeType": "application/json",
            "responseSchema": provider_response_schema(),
        },
    }
    if len(canonical_bytes(vertex_request)) > MAX_PROVIDER_REQUEST_BYTES:
        raise ContractError("provider_request_oversized")
    return vertex_request


def correction_request(
    request: dict[str, Any],
    reason_code: str,
    attempt_number: int,
) -> dict[str, Any]:
    if attempt_number != 2 or reason_code not in CORRECTION_REASON_CODES:
        raise ContractError("correction_not_eligible")
    vertex_request = build_vertex_request(request)
    if reason_code == "provider_body_schema_invalid":
        repair_text = (
            "CORRECTION_TICKET: The prior object failed the closed response "
            "contract. Return a complete replacement object using the same "
            "authored-synthetic request and ontology. Do not change meaning, "
            "labels or authority."
        )
    else:
        repair_text = (
            "CORRECTION_TICKET: The prior closed-shape selector was not "
            "grounded. Recompute the exact intent, coordinate and cue codes "
            "directly from the authored-synthetic request without using any "
            "previous candidate content. Keep every authority value false."
        )
    vertex_request["contents"][0]["parts"][0]["text"] = "\n".join(
        (repair_text, vertex_request["contents"][0]["parts"][0]["text"])
    )
    return vertex_request


def provider_request_for_attempt(
    request: dict[str, Any],
    *,
    attempt_number: int,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    if attempt_number == 1 and correction_reason_code is None:
        return build_vertex_request(request)
    if (
        attempt_number == 2
        and correction_reason_code in CORRECTION_REASON_CODES
    ):
        return correction_request(
            request,
            correction_reason_code,
            attempt_number,
        )
    raise ContractError("attempt_contract_invalid")


def extract_provider_candidate(packet: dict[str, Any]) -> dict[str, Any]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise ContractError("provider_candidate_count_invalid")
    candidate = candidates[0]
    content = candidate.get("content") if isinstance(candidate, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise ContractError("provider_parts_count_invalid")
    part = parts[0]
    if not isinstance(part, dict) or part.get("thought") is True:
        raise ContractError("provider_part_non_text_invalid")
    text = part.get("text")
    if not isinstance(text, str) or len(text.encode("utf-8")) > 32768:
        raise ContractError("provider_part_non_text_invalid")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ContractError("provider_candidate_not_json") from error
    if not isinstance(value, dict):
        raise ContractError("provider_candidate_not_object")
    return value


def bounded_provider_metadata(packet: dict[str, Any]) -> dict[str, Any]:
    usage = packet.get("usageMetadata")
    safe_usage = {
        key: value
        for key in (
            "promptTokenCount",
            "candidatesTokenCount",
            "thoughtsTokenCount",
            "totalTokenCount",
        )
        if isinstance(usage, dict)
        and type(value := usage.get(key)) is int
        and value >= 0
    }
    candidates = packet.get("candidates")
    first = candidates[0] if isinstance(candidates, list) and candidates else {}
    finish_reason = first.get("finishReason") if isinstance(first, dict) else None
    if finish_reason not in {
        "STOP",
        "MAX_TOKENS",
        "SAFETY",
        "RECITATION",
        "OTHER",
        "BLOCKLIST",
        "PROHIBITED_CONTENT",
        "SPII",
        "MALFORMED_FUNCTION_CALL",
        "MODEL_ARMOR",
    }:
        finish_reason = "UNRECOGNIZED"
    content = first.get("content") if isinstance(first, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    return {
        "candidate_count": len(candidates) if isinstance(candidates, list) else 0,
        "finish_reason": finish_reason,
        "usage": safe_usage,
        "parts_count": len(parts) if isinstance(parts, list) else 0,
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
    }


def canonical_model_body_fixture(intent_code: str) -> dict[str, Any]:
    """Return the committed code-owned provider body for one closed intent."""
    if intent_code not in FIXTURE_EXPECTED:
        raise ContractError("intent_unknown")
    expected = FIXTURE_EXPECTED[intent_code]
    body = {
        "intent_code": intent_code,
        "temporal_coordinate_code": expected["temporal_coordinate_code"],
        "cue_codes": list(expected["cue_codes"]),
        "response_code": "INTENT_CANDIDATE_ONLY",
        **{key: False for key in AUTHORITY_KEYS},
    }
    validate_provider_intent_body(body)
    return body


def build_dry_run_provider_packet() -> dict[str, Any]:
    """Return the canonical synthetic provider packet used by dry-run."""
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    return {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {"text": canonical_bytes(body).decode("utf-8")}
                    ]
                },
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 0,
            "candidatesTokenCount": 0,
            "thoughtsTokenCount": 0,
            "totalTokenCount": 0,
        },
        "modelVersion": DRY_RUN_MODEL_VERSION,
    }


def _expected_classification(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("request_id") != OCCUPIED_REQUEST_ID:
        raise ContractError("request_case_unknown")
    expected = FIXTURE_EXPECTED["CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"]
    return {
        "intent_code": "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON",
        "temporal_coordinate_code": expected["temporal_coordinate_code"],
        "cue_codes": list(expected["cue_codes"]),
    }


def wrap_provider_body(
    request: dict[str, Any],
    body: dict[str, Any],
    *,
    attempt_id: str,
    ledger_id: str,
    provider_request_hash: str,
    provider_response_hash: str,
    provider_response_shape: dict[str, Any],
) -> dict[str, Any]:
    """Bind selector-only model output into the trusted candidate envelope."""
    validate_intent_shaping_request(request)
    validate_provider_intent_body(body)
    material = {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "candidate_id": (
            "synthetic:intent-shaping-candidate:"
            + body["intent_code"].lower()
        ),
        "request_hash": prefixed_sha256(request),
        "provider_request_hash": provider_request_hash,
        "provider_response_hash": provider_response_hash,
        "provider_response_shape": deepcopy(provider_response_shape),
        "provider_binding": _provider_binding(),
        "attempt_id": attempt_id,
        "ledger_id": ledger_id,
        "candidate_provenance": "untrusted_model",
        "body": deepcopy(body),
        "read_only": True,
        "provider_authority": False,
        "command_authority": False,
    }
    envelope = seal(material, "envelope_digest")
    validate_instance(CANDIDATE_ENVELOPE_SCHEMA_PATH, envelope)
    return envelope


def _build_trusted_parent_packet(
    request: dict[str, Any],
    body: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    coordinate = _COORDINATE_MAPPING.get(
        body["temporal_coordinate_code"]
    )
    valid_at = None if coordinate is None else coordinate["valid_at"]
    known_at = None if coordinate is None else coordinate["known_at"]
    candidate = build_intent_candidate(
        body["intent_code"],
        requesting_bureau="RAYLEEN",
        valid_at=valid_at,
        known_at=known_at,
    )
    sources = build_authored_synthetic_sources()
    catalog = build_source_catalog(sources)
    binding = build_intent_authority_binding(sources, catalog=catalog)
    packet = build_intent_packet(candidate, binding, catalog)
    return candidate, binding, catalog, packet


def _parent_error_reason(error: Exception) -> str:
    if isinstance(error, IntentRetrievalViolation):
        return str(error).split(":", 1)[0]
    return "parent_contract_violation"


def _rejection(
    envelope: dict[str, Any],
    reason: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    reason_code = reason.split(":", 1)[0]
    try:
        candidate_hash = prefixed_sha256(envelope)
    except (TypeError, ValueError):
        candidate_hash = "sha256:" + hashlib.sha256(
            b"noncanonical-envelope"
        ).hexdigest()
    return {
        "verdict": "rejected",
        "lane": LANE,
        "reason_code": reason_code,
        "candidate_hash": candidate_hash,
        "correction_eligible": reason_code in CORRECTION_REASON_CODES,
        "released": None,
    }


def provider_body_rejection(
    body: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    """Structured proofreader rejection for a provider body that cannot wrap.

    A JSON object that fails the closed provider-body schema must not raise
    from ``wrap_provider_body`` and bypass the structured proofreader.  This
    returns the same sealed rejection shape as :func:`_rejection` so the one
    allowed ``provider_body_schema_invalid`` correction remains eligible.  The
    body is hashed for the candidate digest and then discarded by the caller.
    """
    reason_code = reason.split(":", 1)[0]
    if reason_code == "schema_invalid":
        reason_code = "provider_body_schema_invalid"
    return {
        "verdict": "rejected",
        "lane": LANE,
        "reason_code": reason_code,
        "candidate_hash": prefixed_sha256(body),
        "correction_eligible": reason_code in CORRECTION_REASON_CODES,
        "released": None,
    }


def positive_thinking_evidence(metadata: dict[str, Any]) -> bool:
    """Return True only for a positive integer provider-reported thinking count.

    Live occupied acceptance requires positive provider-reported thinking-token
    use.  Missing, non-integer or non-positive counts fail closed.  Provider-free
    dry-run remains eligible with zero thinking tokens.
    """
    usage = metadata.get("usage") if isinstance(metadata, dict) else None
    if not isinstance(usage, dict):
        return False
    return (
        type(usage.get("thoughtsTokenCount")) is int
        and usage["thoughtsTokenCount"] > 0
    )


def bounded_body_field_labels(body: dict[str, Any]) -> dict[str, Any]:
    """Allowlisted field-label telemetry plus bounded counts for a provider body.

    Unexpected provider field names or values must not be retained in
    audit/evidence.  Only the fixed :data:`BODY_FIELD_ALLOWLIST` names may be
    reported as ``known_field_labels``; every other field is folded into a
    bounded ``unknown_field_count``.
    """
    known = {
        key: "untrusted_model"
        for key in body
        if key in BODY_FIELD_ALLOWLIST
    }
    return {
        "known_field_labels": known,
        "known_field_count": len(known),
        "unknown_field_count": sum(
            1 for key in body if key not in BODY_FIELD_ALLOWLIST
        ),
    }


def _admission(
    envelope: dict[str, Any],
    release: dict[str, Any],
) -> dict[str, Any]:
    return {
        "verdict": "admitted",
        "lane": LANE,
        "reason_code": "proofreader_admitted",
        "candidate_hash": prefixed_sha256(envelope),
        "correction_eligible": False,
        "released": release,
    }


def _build_release(
    envelope: dict[str, Any],
    trace: dict[str, Any],
    candidate: dict[str, Any],
    binding: dict[str, Any],
    catalog: dict[str, Any],
    packet: dict[str, Any],
) -> dict[str, Any]:
    body = envelope["body"]
    material = {
        "schema_version": RELEASE_SCHEMA_VERSION,
        "release_id": (
            "synthetic:intent-shaping-release:" + body["intent_code"].lower()
        ),
        "request_hash": envelope["request_hash"],
        "provider_request_hash": envelope["provider_request_hash"],
        "provider_response_hash": envelope["provider_response_hash"],
        "attempt_id": envelope["attempt_id"],
        "ledger_id": envelope["ledger_id"],
        # The release must own immutable/deep-copied nested material.  The
        # broker later zeroises the original envelope and body, and that
        # zeroisation must not change this release or invalidate its digest.
        "model_intent_candidate_envelope": deepcopy(envelope),
        "intent_proofreader_trace": deepcopy(trace),
        "parent_candidate": deepcopy(candidate),
        "parent_binding_digest": binding["binding_digest"],
        "parent_catalog_digest": catalog["catalog_digest"],
        "parent_packet": deepcopy(packet),
        "parent_proofreader_trace": deepcopy(packet["proofreader_trace"]),
        "read_only": True,
        "provider_authority": False,
        "command_authority": False,
    }
    return seal(material, "release_digest")


def proofread_intent_candidate(
    request: dict[str, Any],
    envelope: dict[str, Any],
    *,
    ground_to_case: bool = True,
) -> dict[str, Any]:
    """Deterministically admit or reject one model intent candidate envelope.

    ``ground_to_case=True`` grounds the body against the authored-synthetic
    occupied classification.  Provider-free fixtures use ``ground_to_case=False``
    so each closed intent can be wrapped and sent through the unchanged parent
    retrieval contract.
    """
    try:
        validate_intent_shaping_request(request)
    except ContractError as error:
        return _rejection(envelope, str(error), request)
    try:
        validate_provider_intent_body(envelope["body"])
    except (ContractError, KeyError, TypeError) as error:
        return _rejection(envelope, "provider_body_schema_invalid", request)
    try:
        validate_instance(CANDIDATE_ENVELOPE_SCHEMA_PATH, envelope)
    except ContractError as error:
        return _rejection(envelope, str(error), request)
    try:
        verify_seal(envelope, "envelope_digest")
    except ValueError:
        return _rejection(envelope, "envelope_digest_mismatch", request)
    if not hmac.compare_digest(
        envelope.get("request_hash", ""),
        prefixed_sha256(request),
    ):
        return _rejection(envelope, "request_hash_mismatch", request)
    body = envelope["body"]
    if not _all_false(body):
        return _rejection(envelope, "authority_ceiling_invalid", request)
    if body["response_code"] != "INTENT_CANDIDATE_ONLY":
        return _rejection(envelope, "intent_not_grounded", request)
    if ground_to_case:
        try:
            expected = _expected_classification(request)
        except ContractError as error:
            return _rejection(envelope, str(error), request)
        if body["intent_code"] != expected["intent_code"]:
            return _rejection(envelope, "intent_not_grounded", request)
        if body["temporal_coordinate_code"] != expected[
            "temporal_coordinate_code"
        ]:
            return _rejection(envelope, "intent_not_grounded", request)
        if body["cue_codes"] != expected["cue_codes"]:
            return _rejection(envelope, "intent_not_grounded", request)
    try:
        candidate, binding, catalog, packet = _build_trusted_parent_packet(
            request, body
        )
    except (ContractError, IntentRetrievalViolation, KeyError, TypeError, ValueError) as error:
        return _rejection(envelope, _parent_error_reason(error), request)
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        return _rejection(envelope, "parent_proofreader_blocked", request)
    trace = {
        "schema_version": SCHEMA_VERSION,
        "grounded_to_case": ground_to_case,
        "release_decision": "ADMIT",
        "reason_codes": ["ALL_CHECKS_PASSED"],
        "checked_at": packet["proofreader_trace"]["checked_at"],
    }
    release = _build_release(
        envelope, trace, candidate, binding, catalog, packet
    )
    return _admission(envelope, release)


def proofread(
    request: dict[str, Any],
    envelope: dict[str, Any],
    *,
    ground_to_case: bool = True,
) -> dict[str, Any]:
    return proofread_intent_candidate(
        request, envelope, ground_to_case=ground_to_case
    )


__all__ = [
    "ARTIFACT_ROOT",
    "AUTHORITY_KEYS",
    "BODY_FIELD_ALLOWLIST",
    "BODY_SCHEMA_VERSION",
    "CANDIDATE_ENVELOPE_SCHEMA_PATH",
    "ContractError",
    "CORRECTION_REASON_CODES",
    "CUE_CODES",
    "DRY_RUN_MODEL_VERSION",
    "ENVELOPE_SCHEMA_VERSION",
    "EVIDENCE_LABEL_OCCUPIED",
    "EVIDENCE_LABEL_PROVIDER_FREE",
    "FIXTURE_EXPECTED",
    "HOSTNAME",
    "INTENT_CODES",
    "LANE",
    "LANES",
    "LOCATION",
    "MAX_CALLS_PER_LANE",
    "MAX_CALLS_TOTAL",
    "MAX_CELL_REQUEST_BYTES",
    "MAX_COST_USD",
    "MAX_OUTPUT_TOKENS",
    "MAX_PROVIDER_REQUEST_BYTES",
    "MAX_PROVIDER_RESPONSE_BYTES",
    "MODEL",
    "OCCUPIED_EXPIRES_AT",
    "OCCUPIED_ISSUED_AT",
    "OCCUPIED_REQUEST_ID",
    "PARENT_CONTRACT_DIGEST",
    "PARENT_POLICY_DIGEST",
    "PATH",
    "POLICY_ID",
    "PREPROOF_TERMINAL_REASON_CODES",
    "PROJECT",
    "PROVIDER_BODY_SCHEMA_PATH",
    "REQUEST_FIXTURE_PATH",
    "REQUEST_SCHEMA_PATH",
    "REQUEST_SCHEMA_VERSION",
    "RELEASE_SCHEMA_VERSION",
    "RESERVED_COST_PER_CALL_USD",
    "SCHEMA_VERSION",
    "SCOPE",
    "SERVICE_ACCOUNT",
    "SYNTHETIC_COORDINATE",
    "SYNTHETIC_COORDINATE_CODE",
    "SYNTHETIC_LABEL",
    "SYNTHETIC_REFERENCE_DATE",
    "SYNTHETIC_TIMEZONE",
    "SYNTHETIC_UTTERANCE",
    "THINKING_BUDGET",
    "bounded_provider_metadata",
    "build_dry_run_provider_packet",
    "build_intent_shaping_request",
    "build_prompt",
    "build_vertex_request",
    "bounded_body_field_labels",
    "canonical_bytes",
    "canonical_model_body_fixture",
    "canonical_sha256",
    "correction_request",
    "extract_provider_candidate",
    "load_object",
    "positive_thinking_evidence",
    "prefixed_sha256",
    "proofread",
    "proofread_intent_candidate",
    "provider_body_rejection",
    "provider_request_for_attempt",
    "provider_response_schema",
    "validate_instance",
    "validate_intent_shaping_request",
    "validate_provider_intent_body",
    "wrap_provider_body",
]
