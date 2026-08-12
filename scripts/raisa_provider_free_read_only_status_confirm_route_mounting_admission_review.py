"""Build the exact-file, provider-free status-confirm route-mounting review."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / (
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-"
    "route-mounting-admission-review"
)
CONTRACT_PATH = PACKET_ROOT / "route-mounting-review-contract.json"
SCHEMA_PATH = PACKET_ROOT / "route-mounting-review-contract.schema.json"
EVIDENCE_PATH = PACKET_ROOT / "route-mounting-review-evidence.json"
REVIEW_PATH = ROOT / (
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review.md"
)

EXPECTED_DIMENSIONS = (
    "literal_route_mounting",
    "canonical_api_identity",
    "physical_seam_composition",
    "current_authority_and_session",
    "status_only_discrimination",
    "locked_policy_admission",
    "atomic_audit_private_receipt",
    "canonical_stored_delivery",
    "physical_outcome_mapping",
    "proved_physical_foundation",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _section(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    return text[start_index : text.index(end, start_index)]


def _line_for_marker(text: str, marker: str, after: str | None = None) -> int:
    start = text.index(after) if after else 0
    index = text.index(marker, start)
    return text.count("\n", 0, index) + 1


def validate_contract(
    contract: dict[str, Any], schema: dict[str, Any]
) -> dict[str, str]:
    Draft202012Validator(schema).validate(contract)
    ids = tuple(item["id"] for item in contract["dimensions"])
    if ids != EXPECTED_DIMENSIONS:
        raise ValueError("review dimensions differ from the frozen order")
    if len(set(ids)) != len(ids):
        raise ValueError("review dimension ids must be unique")
    allowlist = {item["path"]: item["sha256"] for item in contract["allowlist"]}
    if len(allowlist) != len(contract["allowlist"]):
        raise ValueError("allowlist paths must be unique")
    for dimension in contract["dimensions"]:
        if dimension["admission_blocker"] is not (
            dimension["classification"] == "blocking_gap"
        ):
            raise ValueError("classification and admission blocker disagree")
        for citation in dimension["citations"]:
            if citation["path"] not in allowlist:
                raise ValueError("citation is outside the exact allowlist")
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
        item["citations"] = []
        for citation in dimension["citations"]:
            line_start = _line_for_marker(
                source_text[citation["path"]],
                citation["marker"],
                citation.get("after"),
            )
            item["citations"].append(
                {
                    "path": citation["path"],
                    "line_start": line_start,
                    "line_end": line_start + citation["marker"].count("\n"),
                }
            )
        resolved.append(item)
    return resolved


def _structural_assertions(source_text: dict[str, str]) -> list[dict[str, Any]]:
    main = source_text["app/main.py"]
    router = source_text["app/routers/appointments.py"]
    dependencies = source_text["app/dependencies.py"]
    schemas = source_text["app/schemas/appointments.py"]
    legacy = source_text["app/services/appointment_idempotency.py"]
    physical = source_text["app/services/appointment_status_physical.py"]
    models = source_text["app/models/appointments.py"]
    api = source_text["docs/api-spine/openapi/appointment-commands.yaml"]
    adapter = source_text[
        "scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py"
    ]
    behavior = json.loads(
        source_text[
            "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
            "status-confirm-behavior-transaction-rehearsal/"
            "provider-free-behavior-transaction-evidence.json"
        ]
    )

    route = _section(
        router,
        "def confirm_status_proposal_route(",
        "def _a5_check_in_gate_open(",
    )
    update = _section(
        router,
        "def _apply_appointment_status_update(",
        "def confirm_status_proposal_route(",
    )
    confirmation_schema = _section(
        schemas,
        "class AppointmentStatusProposalConfirmationIn(BaseModel):",
        "class AppointmentConfirmStatusProposalOut(BaseModel):",
    )
    complete_call = _section(route, "complete_appointment_command(", "db.commit()")

    checks = {
        "appointments_router_included": "app.include_router(appointments.router)" in main,
        "appointments_prefix_exact": (
            'router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])'
            in router
        ),
        "mounted_path_exact": '"/proposals/status-confirm",' in router,
        "canonical_operation_exact": "operationId: confirmAppointmentStatusProposal" in api,
        "current_alias_documented": (
            "current_backend_path: /appointments/proposals/status-confirm" in api
            and "canonical_openapi_path: /appointments/proposals/status/confirm" in api
        ),
        "physical_seam_exists": "def status_confirm_locked_transaction(" in physical,
        "mounted_route_uses_legacy_claim": "claim_appointment_command(" in route,
        "mounted_route_uses_legacy_complete": "complete_appointment_command(" in route,
        "mounted_route_bypasses_physical_seam": (
            "status_confirm_locked_transaction" not in route
            and "appointment_status_physical" not in router
        ),
        "legacy_replay_precedes_target_load": (
            route.index("if mapped_decision is not None:")
            < route.index("appt = _get_appointment(")
        ),
        "dependencies_check_user_and_role": (
            "def get_current_user(" in dependencies
            and "def require_role(*roles: UserRole):" in dependencies
        ),
        "route_has_no_session_binding": "session_binding" not in route,
        "physical_rechecks_authority_twice": (
            physical.count("if not current_authority(practice, appointment):") == 2
        ),
        "confirmation_schema_remains_union": (
            "AppointmentStatusProposalOut | AppointmentWaitingAreaProposalOut"
            in confirmation_schema
        ),
        "adapter_is_status_only": (
            'transport["proposal_intent"] != "update_appointment_status"' in adapter
            and 'transport["command"]["kind"] != "status"' in adapter
        ),
        "durable_state_version_present": "appointment_state_version = Column(" in models,
        "legacy_warnings_are_concatenated": (
            "*[issue.code for issue in proposal.warnings]" in route
            and "*body.confirmed_warnings" in route
        ),
        "adapter_has_fail_closed_policy": (
            'stop("warning_acknowledgement_mismatch"' in adapter
            and 'stop("transition_policy_deferred")' in adapter
        ),
        "update_discards_audit_identity": (
            "_write_audit(" in update and "audit = _write_audit(" not in update
        ),
        "legacy_complete_omits_audit_and_private_v1": (
            "audit_log_id=" not in complete_call
            and "completed_receipt_version" not in complete_call
            and "response_body_canonical_bytes" not in complete_call
        ),
        "private_v1_columns_present": (
            "completed_receipt_version = Column(" in models
            and "response_body_canonical_bytes = Column(" in models
        ),
        "initial_response_is_separate_object": "db.commit()\n    return response_body" in route,
        "physical_canonical_bytes_present": "response_body_canonical_bytes" in physical,
        "physical_outcomes_are_typed": (
            "class StatusConfirmTargetUnavailable(" in physical
            and "class StatusConfirmAuthorityRevoked(" in physical
            and "class StatusConfirmPhysicalDecision:" in physical
        ),
        "behavior_evidence_passes_sixteen_scenarios": (
            behavior["result"]
            == "raisa_provider_free_disposable_postgresql_status_confirm_"
            "behavior_transaction_rehearsal_pass"
            and len(behavior["scenarios"]) == 16
            and behavior["hostile_mutations_rejected"] == 100
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ValueError("structural review assertion failed: " + ", ".join(failed))
    return [{"id": name, "passed": passed} for name, passed in checks.items()]


def _verdict(dimensions: list[dict[str, Any]], rule: dict[str, str]) -> str:
    if any(item["admission_blocker"] for item in dimensions):
        return rule["any_blocking_gap"]
    if any(item["classification"] == "partial_gap" for item in dimensions):
        return rule["no_blocker_with_partial_gap"]
    return rule["all_satisfied"]


def _hostile_variants(
    contract: dict[str, Any], schema: dict[str, Any]
) -> list[dict[str, Any]]:
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
    candidate["allowlist"][1] = copy.deepcopy(candidate["allowlist"][0])
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["allowlist"][0]["sha256"] = "0"
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["allowlist"][0]["unexpected"] = True
    variants.append(candidate)
    for key in ("path", "sha256"):
        candidate = copy.deepcopy(contract)
        candidate["allowlist"][0].pop(key)
        variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"] = []
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][1]["id"] = candidate["dimensions"][0]["id"]
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"].reverse()
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["unexpected"] = True
    variants.append(candidate)
    for key in schema["properties"]["dimensions"]["items"]["required"]:
        candidate = copy.deepcopy(contract)
        candidate["dimensions"][0].pop(key)
        variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["classification"] = "ready"
    variants.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["dimensions"][0]["admission_blocker"] = True
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
    for key in contract["forbidden"]:
        candidate = copy.deepcopy(contract)
        candidate["forbidden"][key] = True
        variants.append(candidate)
    if len(variants) != 45:
        raise AssertionError(f"expected 45 hostile variants, got {len(variants)}")
    return variants


def _hostile_results(contract: dict[str, Any], schema: dict[str, Any]) -> dict[str, int]:
    rejected = 0
    for candidate in _hostile_variants(contract, schema):
        try:
            validate_contract(candidate, schema)
        except Exception:
            rejected += 1
    if rejected != 45:
        raise ValueError(f"hostile mutation rejection incomplete: {rejected}/45")
    return {"attempted": 45, "rejected": rejected}


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
    return {
        "schema_version": "raisa.status-confirm-route-mounting-review-evidence.v1",
        "result": "raisa_provider_free_read_only_status_confirm_route_mounting_admission_review_pass",
        "source_head": contract["source_head"],
        "review_mode": contract["review_mode"],
        "verdict": _verdict(dimensions, contract["verdict_rule"]),
        "implementation_authorized": False,
        "dimension_counts": {
            classification: sum(
                item["classification"] == classification for item in dimensions
            )
            for classification in ("satisfied", "partial_gap", "blocking_gap")
        },
        "dimensions": dimensions,
        "source_hashes": observed_hashes,
        "structural_assertions": _structural_assertions(source_text),
        "hostile_mutations": _hostile_results(contract, schema),
        "forbidden": contract["forbidden"],
        "next_candidate": contract["next_candidate"],
    }


def render_review(evidence: dict[str, Any]) -> str:
    lines = [
        "# Provider-free read-only status-confirm route-mounting admission review",
        "",
        "Date: 2026-08-12",
        "",
        f"Source HEAD: `{evidence['source_head']}`",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Verdict: `{evidence['verdict']}`",
        "",
        "## Decision",
        "",
        "The endpoint is literally mounted, and its exact physical PostgreSQL seam is",
        "already proved. The unchanged mounted handler is nevertheless not admitted",
        "onto that seam: seven composition gaps remain blocking, one API-path matter is",
        "partial, and two foundations are satisfied. No durability work is reopened.",
        "",
        "## Exact admission matrix",
        "",
        "| Dimension | Classification | Observation | Narrowest prerequisite |",
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
            f"All {len(evidence['source_hashes'])} exact source hashes matched; all "
            f"{len(evidence['structural_assertions'])} structural assertions passed; "
            f"all {evidence['hostile_mutations']['rejected']} hostile mutations were "
            "rejected.",
            "",
            "No application import/edit, route or database execution, provider call,",
            "product or patient data, deployment, release, Pages or protected-ref action",
            "occurred.",
            "",
            "## Next safe candidate",
            "",
            "Rehearse one provider-free unmounted composition callable joining the",
            "accepted status-only adapter, server authority/session ingress, physical",
            "transaction seam and closed public-response mapper. It must not edit or mount",
            "the live route.",
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
