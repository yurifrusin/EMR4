"""Closed contracts and deterministic proofreaders for Bureau A3/B3.

The module is provider-aware but performs no network, credential, database,
product, clock or filesystem mutation.  Provider invocation lives in the
separate one-use broker and can release only values admitted here.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT / "orchestration/continuity/model-required-bureau-a3-b3"
)
CONTRACT_PATH = ARTIFACT_ROOT / "a3-b3-contract.json"
RAYLEEN_CONTEXT_PATH = ARTIFACT_ROOT / "rayleen-a3-context.example.json"
RAYLEEN_CONTEXT_SCHEMA_PATH = ARTIFACT_ROOT / "rayleen-a3-context.schema.json"
RAYLEEN_CANDIDATE_SCHEMA_PATH = ARTIFACT_ROOT / "rayleen-a3-candidate.schema.json"
RAYLEEN_MODEL_BODY_SCHEMA_PATH = ARTIFACT_ROOT / "rayleen-a3-model-body.schema.json"
RAYLEEN_RELEASE_SCHEMA_PATH = ARTIFACT_ROOT / "rayleen-a3-release.schema.json"
RAYLEEN_CANDIDATE_PATH = ARTIFACT_ROOT / "rayleen-a3-candidate.example.json"
DAVIDA_CONTEXT_PATH = ARTIFACT_ROOT / "davida-b3-context.example.json"
DAVIDA_CONTEXT_SCHEMA_PATH = ARTIFACT_ROOT / "davida-b3-context.schema.json"
DAVIDA_CANDIDATE_SCHEMA_PATH = ARTIFACT_ROOT / "davida-b3-candidate.schema.json"
DAVIDA_MODEL_BODY_SCHEMA_PATH = ARTIFACT_ROOT / "davida-b3-model-body.schema.json"
DAVIDA_RELEASE_SCHEMA_PATH = ARTIFACT_ROOT / "davida-b3-release.schema.json"
DAVIDA_CANDIDATE_PATH = ARTIFACT_ROOT / "davida-b3-candidate.example.json"

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
POLICY_ID = "emr4-model-required-bureau-a3-b3-sydney-v1"
MAX_PROVIDER_REQUEST_BYTES = 65536
MAX_PROVIDER_RESPONSE_BYTES = 65536
MAX_CELL_REQUEST_BYTES = 32768
MAX_CALLS_TOTAL = 4
MAX_CALLS_PER_LANE = 2
MAX_COST_USD = 1.0
RESERVED_COST_PER_CALL_USD = 0.25

LANE_RAYLEEN = "rayleen_a3"
LANE_DAVIDA = "davida_b3"
LANES = frozenset({LANE_RAYLEEN, LANE_DAVIDA})


class ContractError(ValueError):
    """A closed contract or deterministic proofreader rejection."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def prefixed_sha256(value: Any) -> str:
    return "sha256:" + canonical_sha256(value)


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
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_rayleen_context(context: dict[str, Any]) -> None:
    validate_instance(RAYLEEN_CONTEXT_SCHEMA_PATH, context)
    generated = _parse_time(context["generated_at"])
    expires = _parse_time(context["expires_at"])
    if expires <= generated:
        raise ContractError("context_expiry_invalid")
    facts = {item["appointment_id"]: item for item in context["facts"]}
    signals = {item["appointment_id"]: item for item in context["derived_signals"]}
    if set(facts) != set(signals):
        raise ContractError("derived_signal_coverage_invalid")
    for appointment_id, fact in facts.items():
        elapsed = int(
            (generated - _parse_time(fact["arrived_at"])).total_seconds() // 60
        )
        if elapsed < 0 or signals[appointment_id]["value"] != elapsed:
            raise ContractError("derived_signal_invalid")


def validate_davida_context(context: dict[str, Any]) -> None:
    validate_instance(DAVIDA_CONTEXT_SCHEMA_PATH, context)
    material = {
        key: value for key, value in context.items() if key != "content_revision"
    }
    if canonical_sha256(material) != context["content_revision"]:
        raise ContractError("context_revision_invalid")
    if _parse_time(context["expires_at"]) <= _parse_time(context["observed_at"]):
        raise ContractError("context_expiry_invalid")
    practitioner_refs = [item["resource_ref"] for item in context["practitioners"]]
    location_refs = [item["resource_ref"] for item in context["locations"]]
    if len(practitioner_refs) != len(set(practitioner_refs)):
        raise ContractError("duplicate_practitioner_ref")
    if len(location_refs) != len(set(location_refs)):
        raise ContractError("duplicate_location_ref")
    if set(practitioner_refs) & set(location_refs):
        raise ContractError("cross_kind_resource_ref")
    if any(
        item["default_location_ref"] not in set(location_refs)
        for item in context["practitioners"]
    ):
        raise ContractError("dangling_default_location")
    dry_run = context["dry_run"]
    dry_run_material = {
        key: value for key, value in dry_run.items() if key != "dry_run_hash"
    }
    if canonical_sha256(dry_run_material) != dry_run["dry_run_hash"]:
        raise ContractError("dry_run_hash_invalid")
    practitioners = {
        item["resource_ref"]: item for item in context["practitioners"]
    }
    locations = {item["resource_ref"]: item for item in context["locations"]}
    practitioner = practitioners.get(dry_run["practitioner_ref"])
    location = locations.get(dry_run["requested_location_ref"])
    if practitioner is None or location is None:
        raise ContractError("dry_run_resource_not_grounded")
    expected_before = {
        "practitioner_ref": practitioner["resource_ref"],
        "default_location_ref": practitioner["default_location_ref"],
    }
    expected_after = {
        "practitioner_ref": practitioner["resource_ref"],
        "default_location_ref": location["resource_ref"],
    }
    if dry_run["before_state"] != expected_before:
        raise ContractError("dry_run_before_state_invalid")
    if dry_run["after_state"] != expected_after:
        raise ContractError("dry_run_after_state_invalid")


def proofread_rayleen(
    candidate: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    try:
        validate_rayleen_context(context)
        validate_instance(RAYLEEN_CANDIDATE_SCHEMA_PATH, candidate)
    except ContractError as error:
        return _rejection(LANE_RAYLEEN, candidate, str(error))
    if candidate["context_revision"] != context["context_revision"]:
        return _rejection(LANE_RAYLEEN, candidate, "context_revision_mismatch")
    practitioner = candidate["practitioner_id"]
    matching = [
        item for item in context["facts"] if item["practitioner_id"] == practitioner
    ]
    if not matching:
        return _rejection(LANE_RAYLEEN, candidate, "practitioner_not_grounded")
    expected_evidence = sorted(item["appointment_id"] for item in matching)
    if sorted(candidate["evidence_appointment_ids"]) != expected_evidence:
        return _rejection(LANE_RAYLEEN, candidate, "evidence_set_not_grounded")
    signal_by_appointment = {
        item["appointment_id"]: item["value"]
        for item in context["derived_signals"]
    }
    maximum = max(signal_by_appointment[item] for item in expected_evidence)
    longest = sorted(
        item
        for item in expected_evidence
        if signal_by_appointment[item] == maximum
    )
    if (
        len(longest) != 1
        or candidate["focus_appointment_id"] != longest[0]
    ):
        return _rejection(LANE_RAYLEEN, candidate, "longest_wait_not_grounded")
    release = {
        "schema_version": "emr4.rayleen.a3.release.v1",
        "lane": LANE_RAYLEEN,
        "case_id": context["case_id"],
        "evidence_mode": "authored_synthetic_occupied_provider_advisory_rehearsal",
        "status": "advisory_only",
        "candidate_provenance": candidate["candidate_provenance"],
        "context_binding": {
            "frame_id": context["frame_id"],
            "practice_id": context["practice_id"],
            "location_id": context["location_id"],
            "context_revision": context["context_revision"],
            "expires_at": context["expires_at"],
        },
        "projection": {
            "intent": candidate["intent"],
            "projection_kind": candidate["projection_kind"],
            "secondary_projection": candidate["secondary_projection"],
            "practitioner_id": practitioner,
            "focus_appointment_id": longest[0],
            "evidence_appointment_ids": expected_evidence,
            "response_code": candidate["response_code"],
        },
        "authority_ceiling": _released_authority(),
    }
    try:
        validate_instance(RAYLEEN_RELEASE_SCHEMA_PATH, release)
    except ContractError as error:
        return _rejection(LANE_RAYLEEN, candidate, str(error))
    return _admission(LANE_RAYLEEN, candidate, release)


def proofread_davida(
    candidate: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    try:
        validate_davida_context(context)
        validate_instance(DAVIDA_CANDIDATE_SCHEMA_PATH, candidate)
    except ContractError as error:
        return _rejection(LANE_DAVIDA, candidate, str(error))
    if candidate["content_revision"] != context["content_revision"]:
        return _rejection(LANE_DAVIDA, candidate, "context_revision_mismatch")
    dry_run = context["dry_run"]
    if candidate["dry_run_proposal_hash"] != dry_run["dry_run_hash"]:
        return _rejection(LANE_DAVIDA, candidate, "dry_run_hash_mismatch")
    practitioners = {
        item["resource_ref"]: item for item in context["practitioners"]
    }
    locations = {item["resource_ref"]: item for item in context["locations"]}
    practitioner = practitioners.get(candidate["practitioner_ref"])
    if practitioner is None:
        if candidate["practitioner_ref"] in locations:
            return _rejection(LANE_DAVIDA, candidate, "wrong_resource_kind")
        return _rejection(LANE_DAVIDA, candidate, "practitioner_not_grounded")
    location = locations.get(candidate["location_ref"])
    if location is None:
        if candidate["location_ref"] in practitioners:
            return _rejection(LANE_DAVIDA, candidate, "wrong_resource_kind")
        return _rejection(LANE_DAVIDA, candidate, "location_not_grounded")
    if practitioner["default_location_ref"] == location["resource_ref"]:
        return _rejection(LANE_DAVIDA, candidate, "no_change")
    if (
        dry_run["practitioner_ref"] != practitioner["resource_ref"]
        or dry_run["requested_location_ref"] != location["resource_ref"]
    ):
        return _rejection(LANE_DAVIDA, candidate, "dry_run_selection_mismatch")
    release = {
        "schema_version": "emr4.davida.b3.release.v1",
        "lane": LANE_DAVIDA,
        "case_id": context["case_id"],
        "evidence_mode": "authored_synthetic_occupied_provider_advisory_rehearsal",
        "status": "dry_run_advisory_only",
        "candidate_provenance": candidate["candidate_provenance"],
        "context_binding": {
            "practice_ref": context["practice_ref"],
            "principal_ref": context["principal_ref"],
            "correlation_id": context["correlation_id"],
            "content_revision": context["content_revision"],
            "expires_at": context["expires_at"],
        },
        "proposal": {
            "intent": candidate["intent"],
            "operation": candidate["operation"],
            "practitioner_ref": practitioner["resource_ref"],
            "location_ref": location["resource_ref"],
            "reason_code": candidate["reason_code"],
            "risk_tier": candidate["risk_tier"],
            "response_code": candidate["response_code"],
            "human_confirmation_required": True,
            "dry_run_proposal_hash": dry_run["dry_run_hash"],
            "changed_paths": deepcopy(dry_run["changed_paths"]),
            "before_state": deepcopy(dry_run["before_state"]),
            "after_state": deepcopy(dry_run["after_state"]),
            "source_paths": [
                practitioner["source_path"],
                location["source_path"],
            ],
            "source_label": "authored_synthetic_fixture",
        },
        "authority_ceiling": _released_authority(),
    }
    try:
        validate_instance(DAVIDA_RELEASE_SCHEMA_PATH, release)
    except ContractError as error:
        return _rejection(LANE_DAVIDA, candidate, str(error))
    return _admission(LANE_DAVIDA, candidate, release)


def _released_authority() -> dict[str, bool]:
    return {
        "confirmation": False,
        "apply": False,
        "write": False,
        "database": False,
        "product_read": False,
        "command": False,
        "actuator": False,
        "success": False,
    }


def _rejection(
    lane: str, candidate: Any, reason: str
) -> dict[str, Any]:
    try:
        candidate_hash = prefixed_sha256(candidate)
    except (TypeError, ValueError):
        candidate_hash = "sha256:" + hashlib.sha256(
            b"noncanonical-candidate"
        ).hexdigest()
    return {
        "verdict": "rejected",
        "lane": lane,
        "reason_code": reason.split(":", 1)[0],
        "candidate_hash": candidate_hash,
        "correction_eligible": reason.startswith("schema_invalid:"),
        "released": None,
    }


def _admission(
    lane: str, candidate: dict[str, Any], release: dict[str, Any]
) -> dict[str, Any]:
    return {
        "verdict": "admitted",
        "lane": lane,
        "reason_code": "proofreader_admitted",
        "candidate_hash": prefixed_sha256(candidate),
        "correction_eligible": False,
        "released": release,
    }


def proofread(
    lane: str, candidate: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    if lane == LANE_RAYLEEN:
        return proofread_rayleen(candidate, context)
    if lane == LANE_DAVIDA:
        return proofread_davida(candidate, context)
    raise ContractError("lane_invalid")


def provider_response_schema(lane: str) -> dict[str, Any]:
    if lane == LANE_RAYLEEN:
        ordered = [
            "intent", "projection_kind", "secondary_projection",
            "practitioner_id", "focus_appointment_id",
            "evidence_appointment_ids", "response_code",
        ]
        properties: dict[str, Any] = {
            "intent": {"type": "STRING", "enum": ["filter"]},
            "projection_kind": {"type": "STRING", "enum": ["practitioner_group"]},
            "secondary_projection": {"type": "STRING", "enum": ["longest_wait"]},
            "practitioner_id": {"type": "STRING"},
            "focus_appointment_id": {"type": "STRING"},
            "evidence_appointment_ids": {"type": "ARRAY", "items": {"type": "STRING"}, "minItems": 1, "maxItems": 8},
            "response_code": {"type": "STRING", "enum": ["FILTERED_PRACTITIONER_LONGEST_WAIT"]},
        }
    elif lane == LANE_DAVIDA:
        ordered = [
            "intent", "operation", "practitioner_ref", "location_ref",
            "dry_run_proposal_hash", "reason_code", "response_code",
        ]
        properties = {
            "intent": {"type": "STRING", "enum": ["dry_run"]},
            "operation": {"type": "STRING", "enum": ["PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION"]},
            "practitioner_ref": {"type": "STRING"},
            "location_ref": {"type": "STRING"},
            "dry_run_proposal_hash": {"type": "STRING", "enum": ["0ff669489dfe35156b3e64bc9c925a97b4f4dc05686bff1c0164cc8b38ea677e"]},
            "reason_code": {"type": "STRING", "enum": ["PRACTICE_ASSIGNMENT_UPDATE"]},
            "response_code": {"type": "STRING", "enum": ["DRY_RUN_REQUIRES_HUMAN_CONFIRMATION"]},
        }
    else:
        raise ContractError("lane_invalid")
    return {
        "type": "OBJECT",
        "properties": properties,
        "required": ordered,
        "propertyOrdering": ordered,
    }


def wrap_provider_body(
    lane: str,
    body: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Bind selector-only model output to broker-owned context and authority."""
    if lane == LANE_RAYLEEN:
        validate_rayleen_context(context)
        validate_instance(RAYLEEN_MODEL_BODY_SCHEMA_PATH, body)
        return {
            "schema_version": "emr4.rayleen.a3.candidate.v1",
            "case_id": context["case_id"],
            "candidate_provenance": "untrusted_model",
            **deepcopy(body),
            "context_revision": context["context_revision"],
            "confirmation_authorized": False,
            "writes_authorized": False,
            "success_claimed": False,
        }
    if lane == LANE_DAVIDA:
        validate_davida_context(context)
        validate_instance(DAVIDA_MODEL_BODY_SCHEMA_PATH, body)
        return {
            "schema_version": "emr4.davida.b3.candidate.v1",
            "case_id": context["case_id"],
            "candidate_provenance": "untrusted_model",
            **deepcopy(body),
            "content_revision": context["content_revision"],
            "risk_tier": "admin_proposal",
            "human_confirmation_required": True,
            "confirmation_authorized": False,
            "apply_authorized": False,
            "writes_authorized": False,
            "success_claimed": False,
        }
    raise ContractError("lane_invalid")


def canonical_model_body_fixture(lane: str) -> dict[str, Any]:
    """Return the committed selector-only fixture for provider-free execution."""
    if lane == LANE_RAYLEEN:
        schema_path = RAYLEEN_MODEL_BODY_SCHEMA_PATH
        candidate_path = RAYLEEN_CANDIDATE_PATH
    elif lane == LANE_DAVIDA:
        schema_path = DAVIDA_MODEL_BODY_SCHEMA_PATH
        candidate_path = DAVIDA_CANDIDATE_PATH
    else:
        raise ContractError("lane_invalid")
    schema = load_object(schema_path)
    candidate = load_object(candidate_path)
    body = {key: deepcopy(candidate[key]) for key in schema["required"]}
    validate_instance(schema_path, body)
    return body


def provider_request_for_attempt(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    if attempt_number == 1 and correction_reason_code is None:
        return build_vertex_request(lane, context)
    if attempt_number == 2 and correction_reason_code == "schema_invalid":
        return correction_request(
            lane,
            context,
            correction_reason_code,
            attempt_number,
        )
    raise ContractError("attempt_contract_invalid")


def build_prompt(lane: str, context: dict[str, Any]) -> str:
    if lane == LANE_RAYLEEN:
        instruction = (
            "Interpret the authored-synthetic Rayleen request. Select the exact "
            "practitioner group and the one longest-wait appointment using only "
            "the supplied facts and deterministic elapsed-wait signals."
        )
    elif lane == LANE_DAVIDA:
        instruction = (
            "Interpret the authored-synthetic Davida request. Form only the exact "
            "default-location dry-run candidate using active resources supplied "
            "in the frame and preserve mandatory human confirmation."
        )
    else:
        raise ContractError("lane_invalid")
    policy = (
        "Return only the selector JSON body matching the response schema. The "
        "host broker owns case bindings, revisions, authority and dry-run truth. "
        "Never invent an identifier or fact. No prose, tools, URLs, commands, "
        "shell or SQL."
    )
    return "\n".join(
        (
            instruction,
            policy,
            "AUTHORED_SYNTHETIC_CONTEXT_JSON:",
            canonical_bytes(context).decode("utf-8"),
        )
    )


def build_vertex_request(lane: str, context: dict[str, Any]) -> dict[str, Any]:
    prompt = build_prompt(lane, context)
    request = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0,
            "candidateCount": 1,
            "maxOutputTokens": 512,
            "responseMimeType": "application/json",
            "responseSchema": provider_response_schema(lane),
        },
    }
    if len(canonical_bytes(request)) > MAX_PROVIDER_REQUEST_BYTES:
        raise ContractError("provider_request_oversized")
    return request


def extract_provider_candidate(packet: dict[str, Any]) -> dict[str, Any]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise ContractError("provider_candidate_count_invalid")
    candidate = candidates[0]
    content = candidate.get("content") if isinstance(candidate, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise ContractError("provider_content_invalid")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str) or len(text.encode("utf-8")) > 32768:
        raise ContractError("provider_text_invalid")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ContractError("provider_candidate_not_json") from error
    if not isinstance(value, dict):
        raise ContractError("provider_candidate_not_object")
    return value


def bounded_provider_metadata(packet: dict[str, Any]) -> dict[str, Any]:
    usage = packet.get("usageMetadata")
    safe_usage: dict[str, int] = {}
    if isinstance(usage, dict):
        for key in (
            "promptTokenCount",
            "candidatesTokenCount",
            "thoughtsTokenCount",
            "totalTokenCount",
        ):
            value = usage.get(key)
            if type(value) is int and value >= 0:
                safe_usage[key] = value
    candidates = packet.get("candidates")
    first = candidates[0] if isinstance(candidates, list) and candidates else {}
    finish_reason = first.get("finishReason") if isinstance(first, dict) else None
    if finish_reason not in {
        "STOP", "MAX_TOKENS", "SAFETY", "RECITATION", "OTHER",
        "BLOCKLIST", "PROHIBITED_CONTENT", "SPII", "MALFORMED_FUNCTION_CALL",
        "MODEL_ARMOR",
    }:
        finish_reason = "UNRECOGNIZED"
    return {
        "candidate_count": len(candidates) if isinstance(candidates, list) else 0,
        "finish_reason": finish_reason,
        "usage": safe_usage,
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
    }


def correction_request(
    lane: str,
    context: dict[str, Any],
    reason_code: str,
    attempt_number: int,
) -> dict[str, Any]:
    if attempt_number != 2 or reason_code != "schema_invalid":
        raise ContractError("correction_not_eligible")
    request = build_vertex_request(lane, context)
    repair_text = (
        "CORRECTION_TICKET: The prior object failed the closed response contract. "
        "Return a complete replacement object using the same context and task. "
        "Do not change identifiers, meaning or authority."
    )
    request = deepcopy(request)
    request["contents"][0]["parts"][0]["text"] = "\n".join(
        (repair_text, request["contents"][0]["parts"][0]["text"])
    )
    return request


__all__ = [
    "ARTIFACT_ROOT",
    "ContractError",
    "DAVIDA_CANDIDATE_PATH",
    "DAVIDA_CONTEXT_PATH",
    "DAVIDA_MODEL_BODY_SCHEMA_PATH",
    "DAVIDA_RELEASE_SCHEMA_PATH",
    "HOSTNAME",
    "LANES",
    "LANE_DAVIDA",
    "LANE_RAYLEEN",
    "LOCATION",
    "MAX_CALLS_PER_LANE",
    "MAX_CALLS_TOTAL",
    "MAX_CELL_REQUEST_BYTES",
    "MAX_COST_USD",
    "MAX_PROVIDER_REQUEST_BYTES",
    "MAX_PROVIDER_RESPONSE_BYTES",
    "MODEL",
    "PATH",
    "POLICY_ID",
    "PROJECT",
    "RAYLEEN_CANDIDATE_PATH",
    "RAYLEEN_CONTEXT_PATH",
    "RAYLEEN_MODEL_BODY_SCHEMA_PATH",
    "RAYLEEN_RELEASE_SCHEMA_PATH",
    "RESERVED_COST_PER_CALL_USD",
    "SCOPE",
    "SERVICE_ACCOUNT",
    "bounded_provider_metadata",
    "build_prompt",
    "build_vertex_request",
    "canonical_bytes",
    "canonical_model_body_fixture",
    "canonical_sha256",
    "correction_request",
    "extract_provider_candidate",
    "load_object",
    "prefixed_sha256",
    "proofread",
    "proofread_davida",
    "proofread_rayleen",
    "provider_request_for_attempt",
    "provider_response_schema",
    "validate_davida_context",
    "validate_instance",
    "validate_rayleen_context",
    "wrap_provider_body",
]
