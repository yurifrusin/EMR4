"""Build the exact-file, provider-free status-confirm runtime-gap review."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-read-only-status-confirm-"
    "runtime-gap-admission-review"
)
CONTRACT_PATH = PACKET_ROOT / "runtime-gap-review-contract.json"
SCHEMA_PATH = PACKET_ROOT / "runtime-gap-review-contract.schema.json"
EVIDENCE_PATH = PACKET_ROOT / "runtime-gap-review-evidence.json"
REVIEW_PATH = (
    ROOT / "docs/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review.md"
)

EXPECTED_DIMENSIONS = (
    "lock_order",
    "current_authority_and_session",
    "status_only_discrimination",
    "terminal_transition_policy",
    "warning_acknowledgement",
    "evidence_and_freshness",
    "atomic_audit_receipt_correlation",
    "authority_first_replay_disclosure",
    "stored_receipt_delivery",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def _line_for_marker(text: str, marker: str, after: str | None = None) -> int:
    start = text.index(after) if after else 0
    index = text.index(marker, start)
    return text.count("\n", 0, index) + 1


def validate_contract(
    contract: dict[str, Any], schema: dict[str, Any]
) -> dict[str, str]:
    Draft202012Validator(schema).validate(contract)
    dimension_ids = tuple(item["id"] for item in contract["dimensions"])
    if dimension_ids != EXPECTED_DIMENSIONS:
        raise ValueError("review dimensions differ from the exact frozen order")
    if len(set(dimension_ids)) != len(dimension_ids):
        raise ValueError("review dimension ids must be unique")
    allowlist = {item["path"]: item["sha256"] for item in contract["allowlist"]}
    if len(allowlist) != len(contract["allowlist"]):
        raise ValueError("source allowlist paths must be unique")
    for dimension in contract["dimensions"]:
        expected_blocker = dimension["classification"] == "blocking_gap"
        if dimension["admission_blocker"] is not expected_blocker:
            raise ValueError("blocking-gap classification must match admission_blocker")
        for citation in dimension["citations"]:
            if citation["path"] not in allowlist:
                raise ValueError("citation path is outside the exact allowlist")
    return allowlist


def _verify_sources(allowlist: dict[str, str]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in allowlist.items():
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"allowlisted source missing: {relative}")
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"allowlisted source hash mismatch: {relative}")
        observed[relative] = actual
    return observed


def _resolve_citations(
    dimensions: list[dict[str, Any]], source_text: dict[str, str]
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for dimension in dimensions:
        item = copy.deepcopy(dimension)
        resolved_citations = []
        for citation in dimension["citations"]:
            text = source_text[citation["path"]]
            line_start = _line_for_marker(
                text,
                citation["marker"],
                citation.get("after"),
            )
            resolved_citations.append(
                {
                    "path": citation["path"],
                    "line_start": line_start,
                    "line_end": line_start + citation["marker"].count("\n"),
                }
            )
        item["citations"] = resolved_citations
        resolved.append(item)
    return resolved


def _structural_assertions(source_text: dict[str, str]) -> list[dict[str, Any]]:
    router = source_text["app/routers/appointments.py"]
    schemas = source_text["app/schemas/appointments.py"]
    idempotency = source_text["app/services/appointment_idempotency.py"]
    models = source_text["app/models/appointments.py"]

    route = _section(
        router,
        "def confirm_status_proposal_route(",
        "# ── A5.1 Rayleen check-in",
    )
    get_appointment = _section(router, "def _get_appointment(", "def _ensure_patient(")
    proposal = _section(
        router,
        "def propose_status_update(",
        "def propose_waiting_area_update(",
    )
    confirmation_schema = _section(
        schemas,
        "class AppointmentStatusProposalConfirmationIn(BaseModel):",
        "class AppointmentConfirmStatusProposalOut(BaseModel):",
    )
    signed_payload = _section(
        router,
        "def _status_signed_confirmation_payload(",
        "_STATUS_CONFIRM_METADATA_FIELDS =",
    )
    appointment_model = _section(
        models,
        "class Appointment(Base):",
        "class PractitionerSchedule(Base):",
    )
    status_complete_call = _section(
        route,
        "complete_appointment_command(",
        "db.commit()",
    )
    correlation_constraint = _section(
        models,
        'name="ck_appt_cmd_idem_completed_response",',
        'name="ck_appt_cmd_idem_completed_check_in_evidence",',
    )

    checks = {
        "claim_precedes_appointment_load": (
            route.index("decision = claim_appointment_command(")
            < route.index(
                "appt = _get_appointment(command.appointment_id, current_user.practice_id, db)"
            )
        ),
        "mapped_replay_precedes_appointment_load": (
            route.index("if mapped_decision is not None:")
            < route.index(
                "appt = _get_appointment(command.appointment_id, current_user.practice_id, db)"
            )
        ),
        "appointment_load_has_no_for_update": ".with_for_update()" not in get_appointment,
        "route_has_no_server_session_binding": "session_binding" not in route,
        "confirmation_schema_is_union": (
            "AppointmentStatusProposalOut | AppointmentWaitingAreaProposalOut"
            in confirmation_schema
        ),
        "confirmation_schema_has_no_session_binding": (
            "session_binding" not in confirmation_schema
        ),
        "terminal_retransition_is_warning_only": (
            'code="already_terminal"' in proposal
            and "warnings.append" in proposal
            and "transition_policy_deferred" not in proposal
        ),
        "warning_codes_are_concatenated": (
            "*[issue.code for issue in proposal.warnings]" in route
            and "*body.confirmed_warnings" in route
        ),
        "signed_payload_has_no_session": "session" not in signed_payload,
        "appointment_has_no_source_version": (
            "version" not in appointment_model and "updated_at" not in appointment_model
        ),
        "status_completion_omits_audit_id": "audit_log_id=" not in status_complete_call,
        "status_not_in_completed_correlation_constraint": (
            "confirmAppointmentStatusProposal" not in correlation_constraint
        ),
        "completed_replay_returns_stored_json": (
            'if record.state == "completed":' in idempotency
            and "response_body_json=record.response_body_json" in idempotency
        ),
        "stored_response_has_canonical_hash": (
            "record.response_body_hash = sha256_canonical_json(response_body)"
            in idempotency
        ),
        "initial_status_response_is_separate_object": (
            "db.commit()\n    return response_body" in route
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise ValueError("structural review assertion failed: " + ", ".join(failed))
    return [{"id": name, "passed": passed} for name, passed in checks.items()]


def _verdict(dimensions: list[dict[str, Any]], rule: dict[str, str]) -> str:
    if any(item["admission_blocker"] for item in dimensions):
        return rule["any_blocking_gap"]
    if any(item["classification"] == "partial_gap" for item in dimensions):
        return rule["no_blocker_with_partial_gap"]
    return rule["all_satisfied"]


def _hostile_variants(contract: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    variants: list[dict[str, Any]] = []
    for key in schema["required"]:
        candidate = copy.deepcopy(contract)
        candidate.pop(key)
        variants.append(candidate)

    candidate = copy.deepcopy(contract)
    candidate["unexpected"] = True
    variants.append(candidate)
    for key, value in (
        ("schema_version", "wrong"),
        ("source_head", "not-a-head"),
        ("review_mode", "runtime"),
        ("implementation_authorized", True),
    ):
        candidate = copy.deepcopy(contract)
        candidate[key] = value
        variants.append(candidate)

    candidate = copy.deepcopy(contract)
    candidate["allowlist"] = []
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["allowlist"][0]["sha256"] = "0"
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["allowlist"][0]["unexpected"] = True
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"] = []
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][1]["id"] = candidate["dimensions"][0]["id"]
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["unexpected"] = True
    variants.append(candidate)

    dimension_required = schema["properties"]["dimensions"]["items"]["required"]
    for key in dimension_required:
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][0].pop(key)
        variants.append(candidate)

    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["classification"] = "ready"
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["admission_blocker"] = False
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["citations"] = []
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["citations"][0]["unexpected"] = True
    variants.append(candidate)
    for key in ("path", "marker"):
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][0]["citations"][0].pop(key)
        variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["citations"][0]["path"] = "outside.txt"
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["forbidden"]["route_executed"] = True
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["next_candidate"] = "runtime"
    variants.append(candidate)
    if len(variants) != 37:
        raise AssertionError(f"expected 37 hostile variants, got {len(variants)}")
    return variants


def _hostile_results(contract: dict[str, Any], schema: dict[str, Any]) -> dict[str, int]:
    rejected = 0
    for candidate in _hostile_variants(contract, schema):
        try:
            validate_contract(candidate, schema)
        except Exception:
            rejected += 1
    if rejected != 37:
        raise ValueError(f"hostile mutation rejection incomplete: {rejected}/37")
    return {"attempted": 37, "rejected": rejected}


def build_evidence() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    allowlist = validate_contract(contract, schema)
    observed_hashes = _verify_sources(allowlist)
    source_text = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in allowlist
    }
    dimensions = _resolve_citations(contract["dimensions"], source_text)
    verdict = _verdict(dimensions, contract["verdict_rule"])
    counts = {
        status: sum(item["classification"] == status for item in dimensions)
        for status in ("satisfied", "partial_gap", "blocking_gap")
    }
    return {
        "schema_version": "raisa.status-confirm-runtime-gap-review-evidence.v1",
        "result": "raisa_provider_free_read_only_status_confirm_runtime_gap_admission_review_pass",
        "source_head": contract["source_head"],
        "review_mode": contract["review_mode"],
        "verdict": verdict,
        "implementation_authorized": False,
        "dimension_counts": counts,
        "dimensions": dimensions,
        "source_hashes": observed_hashes,
        "structural_assertions": _structural_assertions(source_text),
        "hostile_mutations": _hostile_results(contract, schema),
        "terminal_guard_executed": False,
        "forbidden": contract["forbidden"],
        "next_candidate": contract["next_candidate"],
    }


def render_review(evidence: dict[str, Any]) -> str:
    lines = [
        "# Provider-free read-only status-confirm runtime-gap admission review",
        "",
        "Date: 2026-08-12",
        "",
        f"Source HEAD: `{evidence['source_head']}`",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Runtime verdict: `{evidence['verdict']}`",
        "",
        "## Decision",
        "",
        "The existing status-confirm route is not admitted to receive the accepted",
        "adapter/kernel contract unchanged. Its one-transaction mutation/audit/receipt",
        "shape and signed freshness evidence are useful foundations, but seven blocking",
        "gaps and two partial gaps remain. This decision authorises no implementation.",
        "",
        "## Exact gap matrix",
        "",
        "| Dimension | Classification | Current observation | Narrowest prerequisite |",
        "|---|---|---|---|",
    ]
    for item in evidence["dimensions"]:
        lines.append(
            "| {title} | `{classification}` | {observed_behavior} | "
            "{narrowest_prerequisite} |".format(**item)
        )
    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            f"All {len(evidence['source_hashes'])} exact non-protected source hashes matched; "
            f"all {len(evidence['structural_assertions'])} structural assertions passed; "
            f"all {evidence['hostile_mutations']['rejected']} hostile mutations were rejected.",
            "The out-of-tree terminal guard was read but not executed or counted as passing",
            "evidence because its accepted fixture date is elapsed.",
            "",
            "No application import/edit, route/database execution, provider call, product",
            "or patient data, command, deployment, release, Pages or protected-ref action",
            "occurred.",
            "",
            "## Next safe candidate",
            "",
            "Freeze a provider-free unmounted status-confirm runtime-convergence",
            "architecture for the exact prerequisite set. It must remain non-executing and",
            "must not choose terminal product policy or alter the mounted route.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    evidence = build_evidence()
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    REVIEW_PATH.write_text(render_review(evidence), encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
