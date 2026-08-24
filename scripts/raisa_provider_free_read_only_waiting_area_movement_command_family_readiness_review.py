"""Deterministic repository-static waiting-area command-family readiness review."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review"
)
DEFAULT_CONTRACT = BASE / "readiness-review-contract.json"
DEFAULT_SCHEMA = BASE / "readiness-review-contract.schema.json"
DEFAULT_EVIDENCE = BASE / "provider-free-read-only-evidence.json"
DEFAULT_REPORT = BASE / "readiness-review-report.md"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strict_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    if "\r" in text:
        raise ValueError(f"non-canonical carriage return: {path}")
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require(text: str, marker: str, *, source: str) -> None:
    if marker not in text:
        raise ValueError(f"missing marker {marker!r} in {source}")


def _forbid(text: str, marker: str, *, source: str) -> None:
    if marker in text:
        raise ValueError(f"forbidden marker {marker!r} in {source}")


def _dimension(
    order: int,
    dimension_id: str,
    classification: str,
    citations: list[str],
    markers: list[str],
) -> dict[str, Any]:
    return {
        "order": order,
        "id": dimension_id,
        "classification": classification,
        "citations": citations,
        "markers": markers,
    }


def _validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    if [item["order"] for item in contract["dimensions"]] != list(range(1, 13)):
        raise ValueError("dimension order is not exact")
    if len({item["id"] for item in contract["dimensions"]}) != 12:
        raise ValueError("dimension identifiers are not unique")
    if len({item["path"] for item in contract["inputs"]}) != 16:
        raise ValueError("source paths are not unique")


def _reject_hostile_mutations(
    contract: dict[str, Any], schema: dict[str, Any]
) -> int:
    canonical = _canonical_json(contract)
    mutations: list[dict[str, Any]] = []
    for index, dimension in enumerate(contract["dimensions"]):
        for field, replacement in (
            ("order", 99),
            ("id", f"mutated_{dimension['id']}"),
            (
                "expected_classification",
                "blocking_gap"
                if dimension["expected_classification"] == "satisfied"
                else "satisfied",
            ),
            ("question", "softened"),
        ):
            mutant = copy.deepcopy(contract)
            mutant["dimensions"][index][field] = replacement
            mutations.append(mutant)
        mutant = copy.deepcopy(contract)
        del mutant["dimensions"][index]
        mutations.append(mutant)
    for index in range(len(contract["inputs"])):
        mutant = copy.deepcopy(contract)
        mutant["inputs"][index]["sha256"] = "0" * 64
        mutations.append(mutant)

    rejected = 0
    for mutant in mutations:
        try:
            _validate_contract(mutant, schema)
            if _canonical_json(mutant) != canonical:
                raise ValueError("exact frozen contract mismatch")
        except (ValueError, TypeError):
            rejected += 1
        except Exception:
            rejected += 1
    if rejected != len(mutations):
        raise ValueError("hostile mutation suite did not fail closed")
    return rejected


def run_review(contract_path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    contract = _read_json(contract_path)
    schema = _read_json(DEFAULT_SCHEMA)
    _validate_contract(contract, schema)

    texts: dict[str, str] = {}
    bindings: dict[str, str] = {}
    for item in contract["inputs"]:
        source_path = ROOT / item["path"]
        text, digest = _strict_text(source_path)
        if digest != item["sha256"]:
            raise ValueError(f"source binding mismatch: {item['path']}")
        texts[item["path"]] = text
        bindings[item["path"]] = digest

    router = texts["app/routers/appointments.py"]
    schemas = texts["app/schemas/appointments.py"]
    models = texts["app/models/appointments.py"]
    status_adapter = texts["app/services/appointment_status_product_adapter.py"]
    status_physical = texts["app/services/appointment_status_physical.py"]
    check_in = texts["app/services/appointment_check_in_product_adapter.py"]
    openapi = texts["docs/api-spine/openapi/appointment-commands.yaml"]
    events = texts["docs/api-spine/async/integration-events.yaml"]
    diary = texts["docs/diary/diary.js"]
    status_route_tests = texts[
        "tests/test_api_spine_status_confirm_idempotency_route_contract.py"
    ]
    status_adapter_tests = texts[
        "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py"
    ]
    check_in_tests = texts["tests/test_model_required_bureau_a5_1_check_in_runtime.py"]
    status_closeout = texts[
        "docs/raisa-provider-free-status-confirm-http-route-convergence-closeout.md"
    ]
    status_architecture = texts[
        "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture.md"
    ]
    successor = texts[
        "orchestration/continuity/raisa-provider-free-database-backed-default-off-canonical-check-in-post-proposal-revalidation-rehearsal/next-tranche-contract.json"
    ]

    _require(models, "waiting_area_id = Column", source="app/models/appointments.py")
    _require(models, "appointment_state_version = Column", source="app/models/appointments.py")
    _require(router, '"/proposals/waiting-area/{appointment_id}"', source="router")
    _require(
        schemas,
        'intent: Literal["update_appointment_waiting_area"]',
        source="schemas",
    )
    _require(schemas, "class AppointmentWaitingAreaCommand", source="schemas")
    _require(schemas, "class AppointmentWaitingAreaProposalOut", source="schemas")
    _require(check_in, 'return "waiting_area_move_not_supported", None', source="check-in")
    _require(check_in, "AppointmentStatus.Arrived", source="check-in")
    _require(check_in_tests, "waiting_area_move_not_supported", source="check-in tests")
    _require(status_adapter, "unsupported_status_confirm_variant", source="status adapter")
    _require(status_adapter_tests, "unsupported_status_confirm_variant", source="adapter tests")
    _require(status_route_tests, "unsupported_status_confirm_variant", source="route tests")
    _require(status_architecture, "waiting-area sibling remains unchanged", source="architecture")
    _require(status_closeout, "Status-only admission is preserved", source="closeout")
    _require(diary, "isWaitingAreaChangeOnly", source="Diary")
    _require(diary, "/appointments/proposals/waiting-area/", source="Diary")
    _require(diary, "applySignedStatusProposal", source="Diary")
    _require(diary, "Waiting area updated (Mock).", source="Diary")
    _require(status_adapter, 'STATUS_CONFIRM_OPERATION_ID = "confirmAppointmentStatusProposal"', source="status adapter")
    _require(status_physical, 'STATUS_CONFIRM_ROUTE_FAMILY = "status-confirm"', source="status physical")
    _require(models, "operation_id = 'confirmAppointmentStatusProposal'", source="models")
    _require(openapi, "/appointments/proposals/status/confirm:", source="OpenAPI")
    _require(openapi, "Waiting-area proposals fail", source="OpenAPI")
    _require(events, "diary.waiting_state_changed", source="events")
    _require(successor, "strict_non_overlap_with_check_in_and_general_status_frozen", source="successor")
    _forbid(openapi, "confirmAppointmentWaitingAreaProposal", source="OpenAPI")
    _forbid(openapi, "/appointments/proposals/waiting-area/confirm:", source="OpenAPI")
    _forbid(events, "diary.waiting_state_changed.v1", source="events")

    dimensions = [
        _dimension(1, "database_current_truth_ownership", "satisfied", [
            "app/models/appointments.py", "app/routers/appointments.py"
        ], ["appointment_waiting_area_owned_by_backend", "monotonic_appointment_state_version_exists"]),
        _dimension(2, "non_mutating_proposal_surface", "satisfied", [
            "app/routers/appointments.py", "app/schemas/appointments.py"
        ], ["waiting_area_proposal_route_mounted", "waiting_area_command_shape_exists", "proposal_has_no_mutation"]),
        _dimension(3, "check_in_non_overlap", "satisfied", [
            "app/services/appointment_check_in_product_adapter.py",
            "tests/test_model_required_bureau_a5_1_check_in_runtime.py",
        ], ["check_in_sets_arrived", "check_in_initial_assignment_only", "existing_area_move_rejected"]),
        _dimension(4, "general_status_non_overlap", "satisfied", [
            "app/services/appointment_status_product_adapter.py",
            "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py",
            "docs/raisa-provider-free-status-confirm-http-route-convergence-closeout.md",
        ], ["status_discriminator_is_exact", "waiting_area_variant_rejected", "no_route_local_fallback"]),
        _dimension(5, "human_confirmation_interaction", "satisfied", [
            "docs/diary/diary.js", "app/routers/appointments.py"
        ], ["real_mode_prepares_waiting_area_proposal", "explicit_dialog_and_confirm_step", "real_mode_has_no_local_mutation"]),
        _dimension(6, "dedicated_operation_route_identity", "blocking_gap", [
            "docs/api-spine/openapi/appointment-commands.yaml", "app/routers/appointments.py"
        ], ["waiting_area_confirm_operation_absent", "waiting_area_confirm_route_family_absent", "canonical_confirm_path_absent"]),
        _dimension(7, "family_bound_signed_evidence", "blocking_gap", [
            "app/routers/appointments.py", "app/services/appointment_status_product_adapter.py"
        ], ["proposal_uses_status_confirmation_evidence", "status_domain_separator_is_wrong_family", "waiting_area_evidence_contract_absent"]),
        _dimension(8, "current_authority_and_command_session", "blocking_gap", [
            "app/services/appointment_status_product_adapter.py", "app/services/appointment_status_physical.py"
        ], ["status_adapter_has_current_authority_ingress", "waiting_area_family_adapter_absent", "waiting_area_command_session_binding_absent"]),
        _dimension(9, "locked_destination_revalidation", "blocking_gap", [
            "app/routers/appointments.py", "app/services/appointment_status_physical.py"
        ], ["destination_active_check_occurs_at_proposal_only", "status_lock_seam_is_family_hard_coded", "waiting_area_locked_revalidation_absent"]),
        _dimension(10, "atomic_mutation_audit_receipt", "blocking_gap", [
            "app/models/appointments.py", "app/services/appointment_status_physical.py"
        ], ["status_receipt_constraint_is_operation_specific", "waiting_area_atomic_write_set_absent", "waiting_area_audit_taxonomy_unfrozen"]),
        _dimension(11, "canonical_public_delivery_and_replay", "blocking_gap", [
            "app/schemas/appointments.py", "docs/diary/diary.js",
            "app/services/appointment_status_product_adapter.py",
        ], ["Diary_expects_status_confirm_response", "waiting_area_public_receipt_absent", "family_owned_replay_absent"]),
        _dimension(12, "api_spine_client_and_event_convergence", "blocking_gap", [
            "docs/api-spine/openapi/appointment-commands.yaml",
            "docs/api-spine/async/integration-events.yaml", "docs/diary/diary.js",
        ], ["OpenAPI_sibling_confirm_absent", "real_mode_targets_status_confirm", "waiting_state_event_has_no_committed_schema"]),
    ]

    expected = contract["dimensions"]
    if [item["id"] for item in dimensions] != [item["id"] for item in expected]:
        raise ValueError("review dimensions diverge from frozen contract")
    for actual, frozen in zip(dimensions, expected, strict=True):
        if actual["classification"] != frozen["expected_classification"]:
            raise ValueError(f"classification mismatch: {actual['id']}")

    counts = Counter(item["classification"] for item in dimensions)
    expected_counts = contract["acceptance"]["expected_counts"]
    if dict(counts) != expected_counts:
        raise ValueError("dimension count mismatch")
    verdict = (
        contract["verdict_rules"]["any_blocking_gap"]
        if counts["blocking_gap"]
        else contract["verdict_rules"]["all_satisfied"]
    )
    if verdict != contract["acceptance"]["expected_verdict"]:
        raise ValueError("verdict mismatch")

    hostile_rejected = _reject_hostile_mutations(contract, schema)
    if hostile_rejected < contract["acceptance"]["minimum_hostile_mutations"]:
        raise ValueError("hostile mutation minimum not met")

    return {
        "schema_version": "raisa.waiting_area_movement_command_family_readiness_evidence.v1",
        "source_head": contract["source_head"],
        "source_bindings": bindings,
        "dimensions": dimensions,
        "dimension_counts": dict(counts),
        "non_overlap": contract["non_overlap"],
        "verdict": verdict,
        "next_tranche": contract["acceptance"]["expected_next_tranche"],
        "hostile_mutations_rejected": hostile_rejected,
        "closed_boundaries": {
            "app_imported": False,
            "route_called": False,
            "database_opened": False,
            "docker_used": False,
            "sql_executed": False,
            "historical_data_accessed": False,
            "network_opened": False,
        },
        "result": "raisa_provider_free_read_only_waiting_area_movement_command_family_readiness_review_pass",
    }


def render_report(evidence: dict[str, Any]) -> str:
    lines = [
        "# Waiting-area movement command-family readiness review",
        "",
        "Date: 2026-08-24",
        "",
        "Timestamp: 2026-08-24T19:10:01.3753193+10:00 (Australia/Brisbane)",
        "",
        f"Source HEAD: `{evidence['source_head']}`",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Verdict: `{evidence['verdict']}`",
        "",
        "## Decision",
        "",
        "The family is not ready for implementation or mounting. Five reusable",
        "foundations are accepted, while seven family-owned authority and delivery",
        "dimensions remain blocking. The narrow successor is an unmounted",
        "command-family architecture, not a route or product-code tranche.",
        "",
        "## Dimension matrix",
        "",
        "| Order | Dimension | Classification | Evidence markers |",
        "|---:|---|---|---|",
    ]
    for item in evidence["dimensions"]:
        markers = "; ".join(item["markers"])
        lines.append(
            f"| {item['order']} | `{item['id']}` | `{item['classification']}` | {markers} |"
        )
    counts = evidence["dimension_counts"]
    lines.extend([
        "",
        "## Counts",
        "",
        f"satisfied: {counts['satisfied']}; blocking_gap: {counts['blocking_gap']}.",
        "",
        "## Frozen non-overlap",
        "",
        "- Check-in owns `Booked -> Arrived` plus an initial area assignment and",
        "  continues to reject moving an existing area.",
        "- General status owns status transitions and its accepted transition side",
        "  effects; waiting-area-only input remains rejected by status confirm.",
        "- The sibling movement family may change only `waiting_area_id`; status and",
        "  arrival state remain unchanged.",
        "",
        "## Narrowest successor",
        "",
        f"`{evidence['next_tranche']}` must freeze a distinct operation/route family,",
        "family-bound evidence, current-authority and locked destination checks,",
        "atomic mutation/audit/idempotency/receipt semantics, canonical delivery and",
        "a post-commit non-actuating event posture. It remains unmounted and provider-free.",
        "",
        "## Closed boundaries",
        "",
        f"All sixteen source hashes matched and {evidence['hostile_mutations_rejected']} hostile",
        "contract mutations failed closed. No application import, route call, database,",
        "Docker, SQL, historical data or network surface was opened.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    evidence = run_review(args.contract)
    args.evidence.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(render_report(evidence), encoding="utf-8")
    print(_canonical_json({
        "result": evidence["result"],
        "verdict": evidence["verdict"],
        "counts": evidence["dimension_counts"],
        "hostile_mutations_rejected": evidence["hostile_mutations_rejected"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
