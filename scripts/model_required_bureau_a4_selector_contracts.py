"""Closed A4 Rayleen selector contracts and deterministic proofreader.

Only :func:`build_vertex_request` serializes provider material.  It sends one
request-scoped opaque model context, never the trusted source frame or mapping
salt.  The model is selector-only and its output has no authority until the
deterministic proofreader grounds it against the trusted authored-synthetic
frame.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / (
    "orchestration/continuity/model-required-bureau-a4-product-read-ui"
)
CONTEXT_PATH = ARTIFACT_ROOT / "authored-synthetic-selector-context.json"
RAYLEEN_CONTEXT_PATH = CONTEXT_PATH
DAVIDA_CONTEXT_PATH = CONTEXT_PATH
TRUSTED_CONTEXT_SCHEMA_PATH = ARTIFACT_ROOT / "selector-context.schema.json"
MODEL_BODY_SCHEMA_PATH = ARTIFACT_ROOT / "selector-model-body.schema.json"
CANDIDATE_SCHEMA_PATH = ARTIFACT_ROOT / "selector-candidate.schema.json"

PROJECT = "bernie-emr4-dev"
SERVICE_ACCOUNT = "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
SCOPE = "https://www.googleapis.com/auth/cloud-platform"
MODEL = "gemini-2.5-flash"
LOCATION = "australia-southeast1"
HOSTNAME = "australia-southeast1-aiplatform.googleapis.com"
PATH = (
    "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
    "publishers/google/models/gemini-2.5-flash:generateContent"
)
POLICY_ID = "emr4-model-required-bureau-a4-sydney-selector-v1"
THINKING_BUDGET = 1024
MAX_OUTPUT_TOKENS = 2048
MAX_PROVIDER_REQUEST_BYTES = 65536
MAX_PROVIDER_RESPONSE_BYTES = 65536
MAX_CELL_REQUEST_BYTES = 32768
MAX_CALLS_TOTAL = 2
MAX_CALLS_PER_LANE = 2
MAX_COST_USD = 0.50
RESERVED_COST_PER_CALL_USD = 0.25

LANE_RAYLEEN = "rayleen_a4_selector"
LANE_DAVIDA = "closed_not_allocated"
LANES = frozenset({LANE_RAYLEEN})
AUTHORITY_KEYS = (
    "confirmation",
    "command",
    "database",
    "product_read",
    "tool",
    "write",
)
CORRECTION_REASON_CODES = frozenset({"schema_invalid", "selector_not_grounded"})


class ContractError(ValueError):
    """A closed contract or proofreader rejection."""


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


def _opaque_ref(kind: str, raw_id: str, salt: str) -> str:
    digest = hmac.new(
        salt.encode("utf-8"),
        f"{kind}:{raw_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:24]
    return f"{kind}_{digest}"


def _all_false(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and tuple(sorted(value)) == tuple(sorted(AUTHORITY_KEYS))
        and all(value[key] is False for key in AUTHORITY_KEYS)
    )


def validate_rayleen_context(context: dict[str, Any]) -> None:
    validate_instance(TRUSTED_CONTEXT_SCHEMA_PATH, context)
    generated = _parse_time(context["generated_at"])
    evaluation = _parse_time(context["evaluation_time"])
    expires = _parse_time(context["expires_at"])
    if not generated <= evaluation < expires:
        raise ContractError("context_expiry_invalid")
    source = context["source_response"]["data"]["rayleenWaitingRoom"]
    if (
        source["contextRevision"] != context["context_revision"]
        or source["generatedAt"] != context["generated_at"]
        or source["expiresAt"] != context["expires_at"]
        or source["projection"]["selectorProvenance"]
        != "deterministic_product_read"
    ):
        raise ContractError("source_frame_binding_invalid")
    fact_ids = [item["appointmentId"] for item in source["backendFacts"]]
    if len(fact_ids) != len(set(fact_ids)) or not fact_ids:
        raise ContractError("source_fact_ids_invalid")
    if not _all_false(context["authority_ceiling"]):
        raise ContractError("authority_ceiling_invalid")


def validate_davida_context(_context: dict[str, Any]) -> None:
    raise ContractError("lane_closed")


def materialize_execution_context(
    template: dict[str, Any], *, observed_at: datetime
) -> dict[str, Any]:
    """Bind the reviewed authored-synthetic template to one fresh two-minute lease."""
    validate_rayleen_context(template)
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ContractError("observed_at_timezone_required")
    generated = observed_at.astimezone(timezone.utc).replace(microsecond=0)
    expires = generated + timedelta(minutes=2)

    def timestamp(value: datetime) -> str:
        return value.isoformat().replace("+00:00", "Z")

    context = deepcopy(template)
    generated_value = timestamp(generated)
    expires_value = timestamp(expires)
    context["generated_at"] = generated_value
    context["evaluation_time"] = generated_value
    context["expires_at"] = expires_value
    frame = context["source_response"]["data"]["rayleenWaitingRoom"]
    frame["generatedAt"] = generated_value
    frame["expiresAt"] = expires_value
    frame["backendFacts"][0]["scheduledAt"] = timestamp(
        generated - timedelta(minutes=45)
    )
    frame["backendFacts"][0]["arrivedAt"] = timestamp(
        generated - timedelta(minutes=40)
    )
    frame["backendFacts"][1]["scheduledAt"] = timestamp(
        generated - timedelta(minutes=30)
    )
    for item in (*frame["backendFacts"], *frame["derivedSignals"]):
        item["label"]["observedAt"] = generated_value
        item["label"]["expiresAt"] = expires_value
    validate_rayleen_context(context)
    return context


def model_context(context: dict[str, Any]) -> dict[str, Any]:
    """Return the only context that may cross the provider boundary."""
    validate_rayleen_context(context)
    source = context["source_response"]["data"]["rayleenWaitingRoom"]
    salt = context["request_scope_salt"]
    practice_ref = _opaque_ref("practice", source["practiceId"], salt)
    location_ref = _opaque_ref("location", source["locationId"], salt)
    facts = []
    signals_by_appointment: dict[str, list[dict[str, Any]]] = {}
    for signal in source["derivedSignals"]:
        signals_by_appointment.setdefault(signal["appointmentId"], []).append(signal)
    for fact in source["backendFacts"]:
        signals = signals_by_appointment.get(fact["appointmentId"], [])
        values: dict[str, Any] = {
            "elapsed_wait_minutes": None,
            "threshold_band": None,
            "flow_exception": None,
        }
        for signal in signals:
            if signal["kind"] == "elapsed_wait_minutes":
                values["elapsed_wait_minutes"] = signal["integerValue"]
            elif signal["kind"] == "threshold_band":
                values["threshold_band"] = signal["textValue"]
            elif signal["kind"] == "flow_exception":
                values["flow_exception"] = signal["textValue"]
        facts.append(
            {
                "appointment_ref": _opaque_ref(
                    "appointment", fact["appointmentId"], salt
                ),
                "practitioner_ref": _opaque_ref(
                    "practitioner", fact["practitionerId"], salt
                ),
                "waiting_area_ref": _opaque_ref(
                    "waiting_area", fact["waitingAreaId"], salt
                ),
                "status": fact["status"],
                **values,
            }
        )
    return {
        "schema_version": "emr4.rayleen.a4.model_context.v1",
        "context_revision": context["context_revision"],
        "generated_at": context["generated_at"],
        "expires_at": context["expires_at"],
        "staff_utterance": context["staff_utterance"],
        "practice_ref": practice_ref,
        "location_ref": location_ref,
        "allowed_projection_kinds": ["longest_wait"],
        "facts": facts,
        "authority_ceiling": deepcopy(context["authority_ceiling"]),
    }


def provider_response_schema(lane: str) -> dict[str, Any]:
    if lane != LANE_RAYLEEN:
        raise ContractError("lane_invalid")
    ordered = [
        "intent",
        "projection_kind",
        "practitioner_ref",
        "waiting_area_ref",
        "focus_appointment_ref",
        "evidence_appointment_refs",
        "context_revision",
        "response_code",
        "authority_ceiling",
    ]
    authority = {
        "type": "OBJECT",
        "properties": {key: {"type": "BOOLEAN"} for key in AUTHORITY_KEYS},
        "required": list(AUTHORITY_KEYS),
        "propertyOrdering": list(AUTHORITY_KEYS),
    }
    return {
        "type": "OBJECT",
        "properties": {
            "intent": {"type": "STRING", "enum": ["select_projection"]},
            "projection_kind": {"type": "STRING", "enum": ["longest_wait"]},
            "practitioner_ref": {"type": "STRING"},
            "waiting_area_ref": {"type": "STRING"},
            "focus_appointment_ref": {"type": "STRING"},
            "evidence_appointment_refs": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "minItems": 1,
                "maxItems": 8,
            },
            "context_revision": {
                "type": "INTEGER",
                "minimum": 1836412047,
                "maximum": 1836412047,
            },
            "response_code": {
                "type": "STRING",
                "enum": ["LONGEST_WAIT_MODEL_SELECTED"],
            },
            "authority_ceiling": authority,
        },
        "required": ordered,
        "propertyOrdering": ordered,
    }


def build_prompt(lane: str, context: dict[str, Any]) -> str:
    if lane != LANE_RAYLEEN:
        raise ContractError("lane_invalid")
    bounded = model_context(context)
    return "\n".join(
        (
            "Interpret this newly authored synthetic Reception One request.",
            "Select exactly one longest-wait display projection using only the "
            "opaque references and deterministic signals supplied.",
            "Return only the selector JSON body matching the response schema. "
            "Never invent a reference or fact. All authority values must remain "
            "false. No prose, tools, URLs, commands, shell, SQL or action.",
            "AUTHORED_SYNTHETIC_OPAQUE_CONTEXT_JSON:",
            canonical_bytes(bounded).decode("utf-8"),
        )
    )


def build_vertex_request(lane: str, context: dict[str, Any]) -> dict[str, Any]:
    request = {
        "contents": [
            {"role": "user", "parts": [{"text": build_prompt(lane, context)}]}
        ],
        "generationConfig": {
            "temperature": 0,
            "candidateCount": 1,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "thinkingConfig": {"thinkingBudget": THINKING_BUDGET},
            "responseMimeType": "application/json",
            "responseSchema": provider_response_schema(lane),
        },
    }
    if len(canonical_bytes(request)) > MAX_PROVIDER_REQUEST_BYTES:
        raise ContractError("provider_request_oversized")
    return request


def correction_request(
    lane: str,
    context: dict[str, Any],
    reason_code: str,
    attempt_number: int,
) -> dict[str, Any]:
    if attempt_number != 2 or reason_code not in CORRECTION_REASON_CODES:
        raise ContractError("correction_not_eligible")
    request = build_vertex_request(lane, context)
    correction_instruction = (
        "The previous selector failed only the closed response shape. Return a "
        "complete replacement; do not change references, evidence, meaning, "
        "freshness or authority."
        if reason_code == "schema_invalid"
        else (
            "The previous closed-shape selector was not grounded. Recompute it "
            "without using any previous candidate content: consider only facts "
            "whose status is arrived and whose elapsed_wait_minutes is an "
            "integer; choose the unique maximum. Copy practitioner_ref, "
            "waiting_area_ref and focus_appointment_ref from that same fact. "
            "evidence_appointment_refs must be a singleton containing only that "
            "same appointment_ref. Use the exact context_revision and required "
            "enum values, and keep every authority value false."
        )
    )
    request["contents"][0]["parts"][0]["text"] = "\n".join(
        (
            f"CORRECTION_TICKET: {correction_instruction}",
            request["contents"][0]["parts"][0]["text"],
        )
    )
    return request


def provider_request_for_attempt(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    if attempt_number == 1 and correction_reason_code is None:
        return build_vertex_request(lane, context)
    if (
        attempt_number == 2
        and correction_reason_code in CORRECTION_REASON_CODES
    ):
        return correction_request(
            lane,
            context,
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


def canonical_model_body_fixture(lane: str) -> dict[str, Any]:
    if lane != LANE_RAYLEEN:
        raise ContractError("lane_invalid")
    context = load_object(CONTEXT_PATH)
    bounded = model_context(context)
    eligible = [
        fact
        for fact in bounded["facts"]
        if fact["status"] == "arrived"
        and type(fact["elapsed_wait_minutes"]) is int
    ]
    focus = max(eligible, key=lambda item: item["elapsed_wait_minutes"])
    value = {
        "intent": "select_projection",
        "projection_kind": "longest_wait",
        "practitioner_ref": focus["practitioner_ref"],
        "waiting_area_ref": focus["waiting_area_ref"],
        "focus_appointment_ref": focus["appointment_ref"],
        "evidence_appointment_refs": [focus["appointment_ref"]],
        "context_revision": bounded["context_revision"],
        "response_code": "LONGEST_WAIT_MODEL_SELECTED",
        "authority_ceiling": {key: False for key in AUTHORITY_KEYS},
    }
    validate_instance(MODEL_BODY_SCHEMA_PATH, value)
    return value


def wrap_provider_body(
    lane: str,
    body: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    if lane != LANE_RAYLEEN:
        raise ContractError("lane_invalid")
    validate_rayleen_context(context)
    validate_instance(MODEL_BODY_SCHEMA_PATH, body)
    candidate = {
        "schema_version": "emr4.rayleen.a4.selector_candidate.v1",
        "case_id": context["case_id"],
        "candidate_provenance": "untrusted_model",
        **deepcopy(body),
        "writes_authorized": False,
        "success_claimed": False,
    }
    validate_instance(CANDIDATE_SCHEMA_PATH, candidate)
    return candidate


def _rejection(candidate: Any, reason: str) -> dict[str, Any]:
    reason_code = reason.split(":", 1)[0]
    return {
        "verdict": "rejected",
        "lane": LANE_RAYLEEN,
        "reason_code": reason_code,
        "candidate_hash": prefixed_sha256(candidate),
        "correction_eligible": reason_code in CORRECTION_REASON_CODES,
        "released": None,
    }


def _raw_id_for_ref(
    *, kind: str, opaque_ref: str, raw_values: list[str], salt: str
) -> str | None:
    for raw in raw_values:
        expected = _opaque_ref(kind, raw, salt)
        if hmac.compare_digest(expected, opaque_ref):
            return raw
    return None


def proofread_rayleen(
    candidate: dict[str, Any],
    context: dict[str, Any],
    *,
    proof_time: datetime | None = None,
) -> dict[str, Any]:
    try:
        validate_rayleen_context(context)
        validate_instance(CANDIDATE_SCHEMA_PATH, candidate)
    except ContractError as error:
        return _rejection(candidate, str(error))
    evaluated = proof_time or datetime.now(timezone.utc)
    if evaluated.tzinfo is None or evaluated.utcoffset() is None:
        return _rejection(candidate, "proof_time_timezone_required")
    evaluated = evaluated.astimezone(timezone.utc)
    generated = _parse_time(context["generated_at"])
    expires = _parse_time(context["expires_at"])
    if not generated <= evaluated < expires:
        return _rejection(candidate, "context_not_fresh")
    bounded = model_context(context)
    if candidate["context_revision"] != bounded["context_revision"]:
        return _rejection(candidate, "context_revision_mismatch")
    if not _all_false(candidate["authority_ceiling"]):
        return _rejection(candidate, "authority_ceiling_invalid")
    eligible = [
        fact
        for fact in bounded["facts"]
        if fact["status"] == "arrived"
        and type(fact["elapsed_wait_minutes"]) is int
    ]
    if not eligible:
        return _rejection(candidate, "eligible_fact_missing")
    maximum = max(item["elapsed_wait_minutes"] for item in eligible)
    longest = [item for item in eligible if item["elapsed_wait_minutes"] == maximum]
    if len(longest) != 1:
        return _rejection(candidate, "longest_wait_ambiguous")
    focus = longest[0]
    if (
        candidate["intent"] != "select_projection"
        or candidate["projection_kind"] != "longest_wait"
        or candidate["practitioner_ref"] != focus["practitioner_ref"]
        or candidate["waiting_area_ref"] != focus["waiting_area_ref"]
        or candidate["focus_appointment_ref"] != focus["appointment_ref"]
        or candidate["evidence_appointment_refs"] != [focus["appointment_ref"]]
        or candidate["response_code"] != "LONGEST_WAIT_MODEL_SELECTED"
    ):
        return _rejection(candidate, "selector_not_grounded")

    source = deepcopy(context["source_response"])
    frame = source["data"]["rayleenWaitingRoom"]
    salt = context["request_scope_salt"]
    appointment_ids = [item["appointmentId"] for item in frame["backendFacts"]]
    focus_id = _raw_id_for_ref(
        kind="appointment",
        opaque_ref=candidate["focus_appointment_ref"],
        raw_values=appointment_ids,
        salt=salt,
    )
    if focus_id is None:
        return _rejection(candidate, "focus_reference_not_grounded")
    selected = [item for item in frame["backendFacts"] if item["appointmentId"] == focus_id]
    if len(selected) != 1:
        return _rejection(candidate, "focus_source_fact_not_grounded")
    frame["backendFacts"] = selected
    frame["derivedSignals"] = [
        item for item in frame["derivedSignals"] if item["appointmentId"] == focus_id
    ]
    frame["projection"] = {
        "kind": "LONGEST_WAIT",
        "selectedCount": 1,
        "practitionerId": selected[0]["practitionerId"],
        "waitingAreaId": selected[0]["waitingAreaId"],
        "focusAppointmentId": focus_id,
        "selectorProvenance": "model_selected_proofreader_admitted",
        "authorityCeiling": "data_only",
        "writesAuthorized": False,
    }
    release = {
        "schema_version": "emr4.rayleen.a4.selector_release.v1",
        "evidence_mode": "proofreader_admitted_display_projection",
        "status": "display_projection_only",
        "response": source,
        "authority_ceiling": {key: False for key in AUTHORITY_KEYS},
    }
    return {
        "verdict": "admitted",
        "lane": LANE_RAYLEEN,
        "reason_code": "proofreader_admitted",
        "candidate_hash": prefixed_sha256(candidate),
        "correction_eligible": False,
        "released": release,
    }


def proofread_davida(
    candidate: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    return _rejection(candidate, "lane_closed")


def proofread(
    lane: str,
    candidate: dict[str, Any],
    context: dict[str, Any],
    *,
    proof_time: datetime | None = None,
) -> dict[str, Any]:
    if lane != LANE_RAYLEEN:
        raise ContractError("lane_invalid")
    return proofread_rayleen(candidate, context, proof_time=proof_time)
