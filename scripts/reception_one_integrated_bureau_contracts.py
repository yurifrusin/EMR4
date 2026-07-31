#!/usr/bin/env python3
"""Repository-only verifier for the Reception One provider-blocked typed lane."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "orchestration" / "continuity" / "reception-one-integrated-bureau"
CASE_PATH = CONTRACT_DIR / "authored-synthetic-case.json"
POLICY_PATH = CONTRACT_DIR / "provider-blocked-policy.json"
SCHEMA_PATHS = {
    "input": CONTRACT_DIR / "intent-input.schema.json",
    "draft": CONTRACT_DIR / "intent-draft.schema.json",
    "proofreader": CONTRACT_DIR / "proofreader-result.schema.json",
    "typesetter": CONTRACT_DIR / "typesetter-instruction.schema.json",
}

ADMITTED_DRAFT_FIELDS = [
    "$.family",
    "$.operation",
    "$.date_relation",
    "$.target_date",
    "$.practitioner_ids",
    "$.time_window",
    "$.duration_minutes",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def schema_errors(value: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(
        f"{'/'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in validator.iter_errors(value)
    )


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def minutes(value: str) -> int:
    hour, minute = value.split(":", 1)
    return int(hour) * 60 + int(minute)


def normalize_draft(draft: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Apply only allowlisted mechanical normalization."""

    normalized = copy.deepcopy(draft)
    repairs: set[str] = set()

    for field in ("request_id", "context_revision", "family", "operation", "date_relation"):
        value = normalized.get(field)
        if not isinstance(value, str):
            continue
        trimmed = value.strip()
        if trimmed != value:
            repairs.add("trim_whitespace")
        if field in {"family", "operation", "date_relation"}:
            cased = trimmed.lower()
            if cased != trimmed:
                repairs.add("canonical_enum_casing")
            trimmed = cased
        normalized[field] = trimmed

    window = normalized.get("time_window")
    if isinstance(window, dict):
        for field in ("from", "to"):
            value = window.get(field)
            if isinstance(value, str) and value.strip() != value:
                window[field] = value.strip()
                repairs.add("trim_whitespace")

    for field in ("practitioner_ids", "source_evidence_paths"):
        values = normalized.get(field)
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            continue
        trimmed = [value.strip() for value in values]
        if trimmed != values:
            repairs.add("trim_whitespace")
        ordered = sorted(trimmed)
        if ordered != trimmed:
            repairs.add("deterministic_ordering")
        normalized[field] = ordered

    return normalized, sorted(repairs)


def expected_target_date(input_frame: dict[str, Any], draft: dict[str, Any]) -> str | None:
    reference = date.fromisoformat(input_frame["context"]["reference_date"])
    relation = draft.get("date_relation")
    if relation == "same_day":
        return reference.isoformat()
    if relation == "tomorrow":
        return (reference + timedelta(days=1)).isoformat()
    if relation == "explicit_date":
        target = draft.get("target_date")
        return target if isinstance(target, str) and target in input_frame["utterance"] else None
    return None


def proofread(
    input_frame: dict[str, Any],
    draft: dict[str, Any],
    *,
    now: datetime,
) -> tuple[dict[str, Any], dict[str, Any]]:
    schemas = {name: load_json(path) for name, path in SCHEMA_PATHS.items()}
    normalized, repairs = normalize_draft(draft)
    input_failures = schema_errors(input_frame, schemas["input"])
    draft_failures = schema_errors(normalized, schemas["draft"])

    allowed_ids = {
        practitioner["id"] for practitioner in input_frame.get("context", {}).get("allowed_practitioners", [])
    }
    requested_ids = set(normalized.get("practitioner_ids", []))
    context = input_frame.get("context", {})

    try:
        observed_at = parse_datetime(context["observed_at"])
        expires_at = parse_datetime(context["expires_at"])
        fresh_context = observed_at <= now < expires_at
    except (KeyError, TypeError, ValueError):
        fresh_context = False

    try:
        window = normalized["time_window"]
        bounded_time_window = minutes(window["from"]) < minutes(window["to"])
    except (KeyError, TypeError, ValueError):
        bounded_time_window = False

    expected_date = None
    try:
        expected_date = expected_target_date(input_frame, normalized)
    except (KeyError, TypeError, ValueError):
        pass

    authority = input_frame.get("authority", {})
    checks = {
        "schema_exact": not input_failures and not draft_failures,
        "authored_synthetic": input_frame.get("data_class") == "authored_synthetic",
        "request_binding": normalized.get("request_id") == input_frame.get("request_id"),
        "context_revision_binding": normalized.get("context_revision") == context.get("context_revision"),
        "fresh_context": fresh_context,
        "grounded_date": expected_date is not None and normalized.get("target_date") == expected_date,
        "grounded_practitioners": bool(requested_ids) and requested_ids.issubset(allowed_ids),
        "bounded_time_window": bounded_time_window,
        "no_command_authority": (
            normalized.get("operation") == "view"
            and authority.get("appointment_write_authority") is False
            and authority.get("command_authority") is False
            and authority.get("product_delivery_enabled") is False
        ),
        "no_unknown_fields": not input_failures and not draft_failures,
    }

    reason_by_check = {
        "schema_exact": "schema-invalid",
        "authored_synthetic": "data-class-not-admitted",
        "request_binding": "request-binding-mismatch",
        "context_revision_binding": "context-revision-mismatch",
        "fresh_context": "stale-context",
        "grounded_date": "ungrounded-date",
        "grounded_practitioners": "ungrounded-practitioner",
        "bounded_time_window": "invalid-time-window",
        "no_command_authority": "command-authority-rejected",
        "no_unknown_fields": "unknown-field-rejected",
    }
    reason_codes = sorted({reason_by_check[name] for name, passed in checks.items() if not passed})
    admitted = not reason_codes
    rejected_paths = sorted(
        {
            *(f"input:{failure}" for failure in input_failures),
            *(f"draft:{failure}" for failure in draft_failures),
        }
    )

    result = {
        "contract_version": "reception.one.proofreader-result.v1",
        "request_id": input_frame.get("request_id", "synthetic-request-invalid"),
        "context_revision": context.get("context_revision", "synthetic-diary-revision-invalid"),
        "decision": "admit" if admitted else "reject",
        "checks": checks,
        "safe_repairs": repairs,
        "admitted_field_paths": ADMITTED_DRAFT_FIELDS if admitted else [],
        "rejected_field_paths": rejected_paths,
        "reason_codes": reason_codes,
    }
    proofreader_failures = schema_errors(result, schemas["proofreader"])
    if proofreader_failures:
        raise ValueError(f"proofreader emitted an invalid result: {proofreader_failures}")
    return result, normalized


def typeset(
    input_frame: dict[str, Any],
    normalized_draft: dict[str, Any],
    proofreader_result: dict[str, Any],
) -> dict[str, Any]:
    if proofreader_result["decision"] != "admit" or not all(proofreader_result["checks"].values()):
        raise ValueError("typesetter rejects every non-admitted proofreader result")
    instruction = {
        "contract_version": "reception.one.typesetter-instruction.v1",
        "request_id": input_frame["request_id"],
        "context_revision": input_frame["context"]["context_revision"],
        "source_draft_sha256": canonical_sha256(normalized_draft),
        "proofreader_sha256": canonical_sha256(proofreader_result),
        "projection_family": normalized_draft["family"],
        "diary_target_date": normalized_draft["target_date"],
        "set_diary_date_before_projection": True,
        "scope": {
            "practitioner_ids": normalized_draft["practitioner_ids"],
            "time_from": normalized_draft["time_window"]["from"],
            "time_to": normalized_draft["time_window"]["to"],
            "duration_minutes": normalized_draft["duration_minutes"],
        },
        "read_action": "authorised_diary_read",
        "action_boundary": {
            "appointment_write_authority": False,
            "command_authority": False,
            "product_delivery_enabled": False,
        },
        "released_field_paths": proofreader_result["admitted_field_paths"],
        "evidence_mode": "provider_blocked_repository_contract",
    }
    failures = schema_errors(instruction, load_json(SCHEMA_PATHS["typesetter"]))
    if failures:
        raise ValueError(f"typesetter emitted an invalid instruction: {failures}")
    return instruction


def verify_policy(policy: dict[str, Any]) -> None:
    required_false = (
        "execution_enabled",
        "credentials_requested",
        "network_requested",
        "raw_prompt_persisted",
        "raw_response_persisted",
        "product_delivery_enabled",
        "provider_runtime_imports_allowed",
    )
    if any(policy.get(field) is not False for field in required_false):
        raise ValueError("provider-blocked policy opened a forbidden execution path")
    if policy.get("provider_call_count") != 0:
        raise ValueError("provider-blocked policy does not prove a zero call count")
    lane = policy.get("future_lane_reference_only", {})
    exact_coordinates = {
        "provider": "google_vertex_ai",
        "model": "gemini-2.5-flash",
        "project": "bernie-emr4-dev",
        "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com",
        "authentication_class": "keyless_impersonated_service_account_adc",
        "location": "australia-southeast1",
        "endpoint": "https://australia-southeast1-aiplatform.googleapis.com",
        "data_class": "authored_synthetic",
    }
    if any(lane.get(field) != value for field, value in exact_coordinates.items()):
        raise ValueError("future-lane coordinates changed")
    for field in ("provider_fallback", "regional_fallback", "command_authority"):
        if lane.get(field) is not False:
            raise ValueError(f"future-lane {field} must remain false")


def build_evidence() -> dict[str, Any]:
    case = load_json(CASE_PATH)
    policy = load_json(POLICY_PATH)
    schemas = {name: load_json(path) for name, path in SCHEMA_PATHS.items()}
    verify_policy(policy)

    input_failures = schema_errors(case["input"], schemas["input"])
    draft_failures = schema_errors(case["draft"], schemas["draft"])
    if input_failures or draft_failures:
        raise ValueError({"input": input_failures, "draft": draft_failures})

    evidence_now = datetime(2026, 7, 28, tzinfo=timezone.utc)
    proofreader, normalized = proofread(case["input"], case["draft"], now=evidence_now)
    instruction = typeset(case["input"], normalized, proofreader)

    negative_cases: list[dict[str, Any]] = []
    mutations = {
        "unknown-authority-field": lambda value: value.update({"confirm_appointment": True}),
        "ungrounded-practitioner": lambda value: value.update(
            {"practitioner_ids": ["synthetic-practitioner-not-in-context"]}
        ),
        "write-shaped-operation": lambda value: value.update({"operation": "book"}),
        "nonallowlisted-date-repair": lambda value: value.update({"target_date": " 2026-07-28 "}),
    }
    for case_id, mutate in mutations.items():
        changed = copy.deepcopy(case["draft"])
        mutate(changed)
        result, _ = proofread(case["input"], changed, now=evidence_now)
        negative_cases.append(
            {
                "case_id": case_id,
                "decision": result["decision"],
                "reason_codes": result["reason_codes"],
            }
        )

    stale_result, _ = proofread(
        case["input"],
        case["draft"],
        now=datetime(2026, 7, 30, tzinfo=timezone.utc),
    )
    negative_cases.append(
        {
            "case_id": "stale-context",
            "decision": stale_result["decision"],
            "reason_codes": stale_result["reason_codes"],
        }
    )

    if proofreader["decision"] != "admit":
        raise ValueError("positive authored-synthetic case was not admitted")
    if any(item["decision"] != "reject" for item in negative_cases):
        raise ValueError("one or more negative cases failed open")

    return {
        "evidence_version": "reception.one.integrated-bureau-provider-blocked-evidence.v1",
        "evidence_mode": "provider_blocked_repository_contract",
        "status": "pass",
        "schema_files": {name: str(path.relative_to(ROOT)).replace("\\", "/") for name, path in SCHEMA_PATHS.items()},
        "policy_sha256": canonical_sha256(policy),
        "input_sha256": canonical_sha256(case["input"]),
        "normalized_draft_sha256": canonical_sha256(normalized),
        "proofreader_sha256": canonical_sha256(proofreader),
        "typesetter_sha256": canonical_sha256(instruction),
        "provider_boundary": {
            "execution_enabled": policy["execution_enabled"],
            "provider_call_count": policy["provider_call_count"],
            "credentials_requested": policy["credentials_requested"],
            "network_requested": policy["network_requested"],
            "raw_prompt_persisted": policy["raw_prompt_persisted"],
            "raw_response_persisted": policy["raw_response_persisted"],
            "product_delivery_enabled": policy["product_delivery_enabled"],
        },
        "positive_case": {
            "request_id": case["input"]["request_id"],
            "decision": proofreader["decision"],
            "safe_repairs": proofreader["safe_repairs"],
            "admitted_field_paths": proofreader["admitted_field_paths"],
            "typesetter_instruction": instruction,
        },
        "negative_cases": negative_cases,
        "explicit_exclusions": [
            "provider execution",
            "credential discovery or refresh",
            "network access",
            "raw provider prompt or response",
            "product delivery",
            "appointment write",
            "command authority",
            "patient, health, clinical or product-derived data",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
