"""Pure contracts for the bounded Gemini 2.5 Flash Sydney rehearsal."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
)
POLICY_PATH = ARTIFACT_ROOT / "broker-policy.json"
CELL_REQUEST_PATH = ARTIFACT_ROOT / "cell-request.json"
RELEASE_SCHEMA_PATH = ARTIFACT_ROOT / "release-output.schema.json"

POLICY_ID = "vertex-sydney-gemini-25-authored-synthetic-v1"
EXPECTED_FACTS = {
    "fact_alpha": "Project Lark has 3 blue tiles.",
    "fact_beta": "Project Lark has 2 green tiles.",
}
EXPECTED_SUMMARY = "Project Lark has 5 tiles: 3 blue and 2 green."
RELEASE_FIELDS = ["summary", "total_tiles", "risk_level", "evidence_ids"]
FORBIDDEN_CELL_KEYS = {
    "access_token",
    "api_key",
    "authentication",
    "credential",
    "oauth",
    "project",
    "provider",
    "refresh_token",
    "service_account",
}
COMMAND_WORDS = {
    "approve",
    "book",
    "delete",
    "deploy",
    "execute",
    "prescribe",
    "release",
    "schedule",
    "send",
    "write",
}
ALLOWED_FIELD_VIOLATION_PATHS = {
    "generationConfig",
    "generationConfig.maxOutputTokens",
    "generationConfig.responseMimeType",
    "generationConfig.responseSchema",
    "generationConfig.thinkingConfig",
    "systemInstruction",
    "contents",
}
ADMITTED_ATTEMPT_LEDGER_PAIRS = {
    ("gemini-25-primary-001", "gemini-25-primary-ledger-001"),
    (
        "gemini-25-repair-dry-run-001",
        "gemini-25-repair-dry-run-ledger-001",
    ),
    (
        "gemini-25-repair-dry-run-002",
        "gemini-25-repair-dry-run-ledger-002",
    ),
    (
        "gemini-25-repair-dry-run-003",
        "gemini-25-repair-dry-run-ledger-003",
    ),
    ("gemini-25-repair-001", "gemini-25-repair-ledger-001"),
    ("gemini-25-repair-002", "gemini-25-repair-ledger-002"),
}
PROOFREADER_PASS_DISPOSITIONS = {"released"}


class ContractError(ValueError):
    """Raised when an input or provider draft cannot be admitted."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"{path.name}_must_be_object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def bytes_hash(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key).casefold())
            found.update(_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_keys(child))
    return found


def validate_cell_request(value: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(value) != {
        "protocol_version",
        "policy_id",
        "attempt_id",
        "ledger_id",
        "task",
    }:
        errors.append("request_top_level_fields_invalid")
    if value.get("protocol_version") != "ariadne.vertex_sydney_work_cell.v1":
        errors.append("protocol_version_invalid")
    if value.get("policy_id") != POLICY_ID:
        errors.append("policy_id_invalid")
    attempt_ledger = (value.get("attempt_id"), value.get("ledger_id"))
    if attempt_ledger not in ADMITTED_ATTEMPT_LEDGER_PAIRS:
        errors.append("attempt_ledger_pair_invalid")
    task = value.get("task")
    if not isinstance(task, dict) or set(task) != {
        "task_type",
        "evidence",
        "requested_fields",
    }:
        errors.append("task_fields_invalid")
        return sorted(set(errors))
    if task.get("task_type") != "authored_synthetic_tile_summary":
        errors.append("task_type_invalid")
    evidence = task.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence_array_required")
    else:
        observed = {
            item.get("fact_id"): item.get("value")
            for item in evidence
            if isinstance(item, dict) and set(item) == {"fact_id", "value"}
        }
        if observed != EXPECTED_FACTS or len(evidence) != 2:
            errors.append("authored_synthetic_evidence_not_exact")
    if task.get("requested_fields") != RELEASE_FIELDS:
        errors.append("requested_fields_not_exact")
    forbidden = _keys(value) & FORBIDDEN_CELL_KEYS
    errors.extend(f"cell_forbidden_field:{name}" for name in sorted(forbidden))
    return sorted(set(errors))


def provider_response_schema() -> dict[str, Any]:
    return {
        "type": "OBJECT",
        "properties": {
            "summary": {
                "type": "STRING",
                "description": (
                    "Exactly: Project Lark has 5 tiles: 3 blue and 2 green."
                ),
            },
            # Gemini structured output supports only string-typed enums. Use
            # supported numeric constraints to preserve the exact integer.
            "total_tiles": {"type": "INTEGER", "minimum": 5, "maximum": 5},
            "risk_level": {"type": "STRING", "enum": ["none"]},
            "evidence_ids": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING",
                    "enum": ["fact_alpha", "fact_beta"],
                },
                "minItems": 2,
                "maxItems": 2,
            },
        },
        "required": RELEASE_FIELDS,
        "propertyOrdering": RELEASE_FIELDS,
    }


def build_vertex_request(cell_request: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_cell_request(cell_request)
    if errors:
        raise ContractError("cell_request_invalid:" + ",".join(errors))
    evidence = cell_request["task"]["evidence"]
    evidence_text = "\n".join(
        f"{item['fact_id']}: {item['value']}" for item in evidence
    )
    user_text = (
        "Use only the authored-synthetic evidence below. Return the exact JSON "
        "fields in the supplied schema. Do not add facts, advice, instructions "
        "or commands.\n\n"
        f"{evidence_text}\n\n"
        "The summary must be exactly: "
        f"{EXPECTED_SUMMARY}"
    )
    return {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are a bounded synthetic-data formatter. Emit only "
                        "the schema-admitted JSON value. Do not use tools, make "
                        "decisions, issue commands, or explain reasoning."
                    )
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_text}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 256,
            "responseMimeType": "application/json",
            "responseSchema": provider_response_schema(),
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }


def provider_free_fixture_response() -> dict[str, Any]:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "summary": EXPECTED_SUMMARY,
                                    "total_tiles": 5,
                                    "risk_level": "NONE",
                                    "evidence_ids": [
                                        "fact_beta",
                                        "fact_alpha",
                                    ],
                                }
                            )
                        }
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 0,
            "candidatesTokenCount": 0,
            "totalTokenCount": 0,
        },
        "modelVersion": "provider-free-fixture",
    }


def validate_attempt_mode(attempt_id: str, mode: str) -> bool:
    if attempt_id.startswith("gemini-25-repair-dry-run-"):
        return mode == "dry-run"
    if attempt_id.startswith("gemini-25-repair-"):
        return mode == "live"
    return attempt_id == "gemini-25-primary-001" and mode == "live"


def _normalize_summary(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def proofread(provider_value: Any) -> dict[str, Any]:
    findings: list[str] = []
    repairs: list[str] = []
    if not isinstance(provider_value, dict):
        return {
            "disposition": "edge_aborted",
            "findings": ["draft_not_object"],
            "safe_repairs": [],
            "release": None,
            "released_field_manifest": [],
        }
    if set(provider_value) != set(RELEASE_FIELDS):
        findings.append("draft_fields_not_exact")
    summary = provider_value.get("summary")
    total = provider_value.get("total_tiles")
    risk = provider_value.get("risk_level")
    evidence_ids = provider_value.get("evidence_ids")
    if not isinstance(summary, str):
        findings.append("summary_type_invalid")
    else:
        normalized = _normalize_summary(summary)
        if normalized != summary:
            repairs.append("summary_whitespace_normalized")
        summary = normalized
        if summary != EXPECTED_SUMMARY:
            findings.append("summary_not_exactly_grounded")
    if type(total) is not int or total != 5:
        findings.append("total_tiles_invalid")
    if isinstance(risk, str) and risk.casefold() == "none":
        if risk != "none":
            repairs.append("risk_level_enum_casing_normalized")
        risk = "none"
    else:
        findings.append("risk_level_invalid")
    if (
        isinstance(evidence_ids, list)
        and len(evidence_ids) == 2
        and set(evidence_ids) == set(EXPECTED_FACTS)
        and all(isinstance(item, str) for item in evidence_ids)
    ):
        ordered = sorted(evidence_ids)
        if ordered != evidence_ids:
            repairs.append("evidence_ids_deterministically_ordered")
        evidence_ids = ordered
    else:
        findings.append("evidence_ids_invalid")
    if isinstance(summary, str):
        words = set(re.findall(r"[a-z]+", summary.casefold()))
        if words & COMMAND_WORDS:
            findings.append("command_authority_language_detected")
    if findings:
        return {
            "disposition": "edge_aborted",
            "findings": sorted(set(findings)),
            "safe_repairs": repairs,
            "release": None,
            "released_field_manifest": [],
        }
    release = {
        "summary": summary,
        "total_tiles": total,
        "risk_level": risk,
        "evidence_ids": evidence_ids,
    }
    return {
        "disposition": "released",
        "findings": [],
        "safe_repairs": repairs,
        "release": release,
        "released_field_manifest": RELEASE_FIELDS,
    }


def extract_provider_draft(provider_response: Mapping[str, Any]) -> Any:
    candidates = provider_response.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise ContractError("provider_candidate_count_not_exact")
    content = candidates[0].get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise ContractError("provider_content_parts_not_exact")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str) or len(text.encode("utf-8")) > 8192:
        raise ContractError("provider_text_missing_or_oversized")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError("provider_text_not_json") from exc


def sanitize_provider_error(
    *,
    http_status: int,
    raw: bytes,
    maximum_message_bytes: int = 2048,
    discarded_raw_error_hash: str | None = None,
) -> dict[str, Any]:
    code = http_status
    status = "UNKNOWN"
    field_paths: list[str] = []
    try:
        packet = json.loads(raw)
        error = packet.get("error", {}) if isinstance(packet, dict) else {}
        if isinstance(error, dict):
            raw_code = error.get("code")
            if type(raw_code) is int and 0 <= raw_code <= 999:
                code = raw_code
            raw_status = error.get("status")
            if isinstance(raw_status, str) and re.fullmatch(r"[A-Z_]{2,64}", raw_status):
                status = raw_status
            for detail in error.get("details", []):
                if not isinstance(detail, dict):
                    continue
                for violation in detail.get("fieldViolations", []):
                    if not isinstance(violation, dict):
                        continue
                    field = violation.get("field")
                    if field in ALLOWED_FIELD_VIOLATION_PATHS:
                        field_paths.append(field)
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    # Free-form provider text is never admissible, even if it does not match
    # a known sensitive marker. A constant diagnostic preserves the bounded
    # error shape without turning an upstream message into durable evidence.
    message = "provider_diagnostic_redacted"
    if len(message.encode("utf-8")) > maximum_message_bytes:
        raise ContractError("sanitized_error_message_limit_invalid")
    error_hash = discarded_raw_error_hash or bytes_hash(raw)
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", error_hash):
        raise ContractError("discarded_raw_error_hash_invalid")
    return {
        "http_status": http_status,
        "provider_error_code": code,
        "normalized_status": status,
        "field_violation_paths": sorted(set(field_paths)),
        "sanitized_message": message,
        "discarded_raw_error_hash": error_hash,
    }


def audit_event(
    *,
    sequence: int,
    previous_hash: str,
    event_type: str,
    fields: Mapping[str, Any],
) -> dict[str, Any]:
    event = {
        "sequence": sequence,
        "recorded_at": utc_now(),
        "event_type": event_type,
        "previous_hash": previous_hash,
        "fields": dict(fields),
    }
    event["event_hash"] = canonical_hash(event)
    return event


def validate_audit_chain(events: list[Mapping[str, Any]]) -> bool:
    previous = "sha256:" + "0" * 64
    for sequence, event in enumerate(events, start=1):
        if event.get("sequence") != sequence or event.get("previous_hash") != previous:
            return False
        candidate = dict(event)
        observed = candidate.pop("event_hash", None)
        if observed != canonical_hash(candidate):
            return False
        previous = str(observed)
    return bool(events)
