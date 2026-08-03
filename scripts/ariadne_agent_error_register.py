"""Validate the Ariadne incident register and emit a deterministic pattern report."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError


ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-agent-error-register"
    / "agent-error-register.json"
)
SCHEMA_PATH = REGISTER_PATH.with_name("agent-error-register.schema.json")
REPORT_PATH = REGISTER_PATH.with_name("pattern-report.json")

FORBIDDEN_KEYS = {
    "api_key",
    "access_token",
    "credential",
    "patient_id",
    "raw_model_output",
    "raw_prompt",
    "secret",
    "token",
    "user_prompt",
}

EXPECTED_ORIGIN_BY_CATEGORY = {
    "command_scope_violation": "agent_behavior",
    "evidence_misreport": "agent_behavior",
    "read_only_violation": "agent_behavior",
    "output_contract_violation": "agent_behavior",
    "reasoning_claim_error": "agent_behavior",
    "transport_timeout": "transport",
    "harness_failure": "harness",
    "repository_defect": "repository",
    "operator_error": "operator",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _repository_path(root: Path, raw_path: str) -> Path:
    if "\\" in raw_path:
        raise ValueError(f"evidence path must use forward slashes: {raw_path}")
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"evidence path escapes repository: {raw_path}") from error
    candidate_parts = tuple(part.casefold() for part in candidate.parts)
    branding_parts = tuple(
        part.casefold() for part in (root / "docs" / "branding").resolve().parts
    )
    if candidate_parts[: len(branding_parts)] == branding_parts:
        raise ValueError(f"branding evidence is forbidden: {raw_path}")
    if not candidate.is_file():
        raise ValueError(f"evidence path is missing or not a file: {raw_path}")
    return candidate


def validate_register(
    register: dict[str, Any],
    schema: dict[str, Any],
    *,
    root: Path = ROOT,
) -> None:
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(register)

    forbidden = sorted(set(_walk_keys(register)) & FORBIDDEN_KEYS)
    if forbidden:
        raise ValueError(f"forbidden sensitive/raw keys: {','.join(forbidden)}")

    incidents = register["incidents"]
    incident_ids = [row["incident_id"] for row in incidents]
    if len(incident_ids) != len(set(incident_ids)):
        raise ValueError("duplicate incident_id")
    if incident_ids != sorted(incident_ids):
        raise ValueError("incident_id order is not ascending")

    known_ids = set(incident_ids)
    attempt_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in incidents:
        attempt_groups[row["attempt_id"]].append(row)
    source_cutoff = date.fromisoformat(register["scope"]["source_cutoff_on"])
    for row in incidents:
        incident_id = row["incident_id"]
        if date.fromisoformat(row["observed_on"]) > source_cutoff:
            raise ValueError(f"incident observed after source cutoff: {incident_id}")

        expected_origin = EXPECTED_ORIGIN_BY_CATEGORY[row["category"]]
        if row["origin"] != expected_origin:
            raise ValueError(
                f"origin/category mismatch: {incident_id}:"
                f"{row['origin']}!={expected_origin}"
            )

        related_ids = row.get("related_incident_ids", [])
        if incident_id in related_ids:
            raise ValueError(f"incident cannot relate to itself: {incident_id}")
        unknown = sorted(set(related_ids) - known_ids)
        if unknown:
            raise ValueError(
                f"unknown related incident ids for {incident_id}: {','.join(unknown)}"
            )
        attempt_peer_ids = {
            peer["incident_id"]
            for peer in attempt_groups[row["attempt_id"]]
            if peer["incident_id"] != incident_id
        }
        if set(related_ids) != attempt_peer_ids:
            raise ValueError(
                f"attempt peer linkage mismatch for {incident_id}: "
                f"expected={','.join(sorted(attempt_peer_ids)) or 'none'}"
            )

        for raw_path in row["evidence_paths"]:
            _repository_path(root, raw_path)
        for raw_path in row["correction"]["evidence_paths"]:
            _repository_path(root, raw_path)

        if row["status"] == "open" and row["correction"]["status"] in {
            "corrected_fresh_attempt",
            "recovery_lease_applied",
            "control_added",
        }:
            raise ValueError(f"open incident has completed correction: {incident_id}")

    for attempt_id, rows in attempt_groups.items():
        if len(rows) < 2:
            continue
        stable_fields = (
            "observed_on",
            "tranche",
            "role",
            "resource_id",
            "model",
            "reasoning_level",
            "transport",
            "stage",
        )
        for field in stable_fields:
            if len({row[field] for row in rows}) != 1:
                raise ValueError(
                    f"split attempt identity mismatch: {attempt_id}:{field}"
                )


def _count(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _canonical_sha256(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_pattern_report(
    *,
    register_path: Path = REGISTER_PATH,
    schema_path: Path = SCHEMA_PATH,
    root: Path = ROOT,
) -> dict[str, Any]:
    register = _load_json(register_path)
    schema = _load_json(schema_path)
    validate_register(register, schema, root=root)
    incidents = register["incidents"]

    signatures: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for row in incidents:
        composite = (
            row["origin"],
            row["category"],
            row["role"],
            row["resource_id"],
            row["recurrence_signature"],
        )
        signatures[composite].append(row)

    recurring_patterns: list[dict[str, Any]] = []
    for composite in sorted(signatures):
        rows = signatures[composite]
        if len(rows) < 2:
            continue
        recurring_patterns.append(
            {
                "recurrence_signature": composite[4],
                "incident_count": len(rows),
                "incident_ids": sorted(row["incident_id"] for row in rows),
                "origins": sorted({row["origin"] for row in rows}),
                "categories": sorted({row["category"] for row in rows}),
                "roles": sorted({row["role"] for row in rows}),
                "resource_ids": sorted({row["resource_id"] for row in rows}),
                "prevention_controls": sorted(
                    {row["correction"]["prevention_control"] for row in rows}
                ),
            }
        )

    resource_roles = Counter(
        f"{row['resource_id']}::{row['role']}" for row in incidents
    )
    open_ids = sorted(
        row["incident_id"] for row in incidents if row["status"] == "open"
    )
    return {
        "schema_version": "ariadne.agent-error-pattern-report.v1",
        "register_revision": register["register_revision"],
        "source_cutoff_on": register["scope"]["source_cutoff_on"],
        "coverage": register["scope"]["coverage"],
        "canonical_register_sha256": _canonical_sha256(register),
        "incident_count": len(incidents),
        "open_incident_ids": open_ids,
        "counts": {
            "by_origin": _count(incidents, "origin"),
            "by_category": _count(incidents, "category"),
            "by_role": _count(incidents, "role"),
            "by_process_severity": _count(incidents, "process_severity"),
            "by_candidate_state": _count(incidents, "candidate_state"),
            "by_resource_and_role": dict(sorted(resource_roles.items())),
        },
        "recurring_patterns": recurring_patterns,
        "interpretation_boundary": (
            "A recurring signature is an operational control signal only. "
            "These counts do not prove model, provider or role causation and "
            "are not a comparative quality score."
        ),
    }


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Ariadne incident register and report patterns."
    )
    parser.add_argument("--register", type=Path, default=REGISTER_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = build_pattern_report(
            register_path=args.register,
            schema_path=args.schema,
        )
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        SchemaError,
        ValidationError,
    ) as error:
        print(f"ariadne agent-error register failed: {error}")
        return 2

    if args.output:
        write_json_lf(args.output, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
