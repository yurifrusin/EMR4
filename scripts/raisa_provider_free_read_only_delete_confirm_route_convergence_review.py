"""Deterministic exact-file delete-confirm route-convergence review.

This module reads only the paths bound by its closed contract. It imports no
application module and performs no route, database, provider or network call.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution"
)
CONTRACT_PATH = CONTINUITY / "route-convergence-contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY / "route-convergence-contract.schema.json"
EVIDENCE_PATH = CONTINUITY / "provider-free-read-only-evidence.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY / "provider-free-read-only-evidence.schema.json"

DIMENSION_IDS = (
    "literal_mounting",
    "canonical_identity_and_alias",
    "physical_seam_composition",
    "server_authority_ingress",
    "locked_proposal_readmission",
    "atomic_effect_audit_receipt",
    "response_contract_compatibility",
    "stored_delivery_and_http_mapping",
    "raw_delete_isolation",
    "serial_postgresql_foundation",
)


class ReviewError(RuntimeError):
    """Closed deterministic review failure."""


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReviewError(f"{path.name} must contain a JSON object")
    return value


def _validate(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda item: list(item.path),
    )
    if errors:
        raise ReviewError(f"{label} schema rejected: {errors[0].message}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _function_block(source: str, marker: str, next_marker: str) -> str:
    if marker not in source or next_marker not in source:
        raise ReviewError(f"function boundary missing: {marker}")
    return source.split(marker, 1)[1].split(next_marker, 1)[0]


def evaluate(
    *,
    root: Path = ROOT,
    contract_path: Path = CONTRACT_PATH,
    contract_schema_path: Path = CONTRACT_SCHEMA_PATH,
    evidence_schema_path: Path = EVIDENCE_SCHEMA_PATH,
) -> dict[str, Any]:
    """Return minimized review evidence or fail closed."""
    contract = _json(contract_path)
    _validate(contract, _json(contract_schema_path), "contract")
    if tuple(item["id"] for item in contract["dimensions"]) != DIMENSION_IDS:
        raise ReviewError("dimension order changed")

    texts: dict[str, str] = {}
    observed_hashes: dict[str, str] = {}
    for binding in contract["sources"]:
        relative = binding["path"]
        path = (root / relative).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError as exc:
            raise ReviewError("bound source escapes repository root") from exc
        if not path.is_file():
            raise ReviewError(f"bound source missing: {relative}")
        digest = _sha256(path)
        if digest != binding["sha256"]:
            raise ReviewError(f"bound source hash mismatch: {relative}")
        observed_hashes[relative] = digest
        texts[relative] = path.read_text(encoding="utf-8")

    router = texts["app/routers/appointments.py"]
    main = texts["app/main.py"]
    dependencies = texts["app/dependencies.py"]
    schemas = texts["app/schemas/appointments.py"]
    models = texts["app/models/appointments.py"]
    tenancy = texts["app/models/tenancy.py"]
    physical = texts["app/services/appointment_delete_physical.py"]
    status_adapter = texts["app/services/appointment_status_product_adapter.py"]
    openapi = texts["docs/api-spine/openapi/appointment-commands.yaml"]
    physical_plan = texts[
        "docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-plan.md"
    ]
    physical_closeout = texts[
        "docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-closeout.md"
    ]
    behavior_closeout = texts[
        "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal-closeout.md"
    ]

    confirm_block = _function_block(
        router,
        "def confirm_delete_proposal_route(",
        '@router.post("/proposals/delete/{appointment_id}"',
    )
    raw_delete_block = _function_block(
        router,
        "def cancel_appointment(",
        '@router.post(\n    "/proposals/delete-confirm"',
    )

    checks = {
        "appointments_router_included": "app.include_router(appointments.router)"
        in main,
        "delete_confirm_alias_mounted": '"/proposals/delete-confirm"' in router,
        "canonical_path_documented": "/appointments/proposals/delete/confirm:"
        in openapi,
        "operation_identity_aligned": contract["operation_id"] in router
        and contract["operation_id"] in physical
        and contract["operation_id"] in openapi,
        "canonical_delete_path_not_mounted": '"/proposals/delete/confirm"'
        not in router,
        "physical_service_not_imported_by_router": "appointment_delete_physical"
        not in router,
        "legacy_claim_owned_by_route": "claim_appointment_command(" in confirm_block,
        "legacy_effect_owned_by_route": "_apply_appointment_delete(" in confirm_block,
        "legacy_completion_owned_by_route": "complete_appointment_command("
        in confirm_block
        and "db.commit()" in confirm_block,
        "command_session_available_but_unused": "def get_command_session_factory("
        in dependencies
        and "get_command_session_factory" not in confirm_block,
        "bearer_session_not_bound": "oauth2_scheme" not in confirm_block,
        "delete_version_binding_absent": "delete_proposal_version_binding"
        not in schemas
        and "delete_proposal_version_binding" not in confirm_block,
        "route_appointment_read_not_locked": "_get_appointment(" in confirm_block
        and "with_for_update" not in confirm_block,
        "physical_exact_capability_required": 'DELETE_CONFIRM_CAPABILITY = "appointment.cancel.confirm"'
        in physical
        and "UserCapabilityGrant" in physical,
        "physical_two_authority_checks": physical.count("if not _authority_valid(")
        == 2,
        "physical_complete_write_set_required": "_delete_write_set_complete("
        in physical
        and "DeleteConfirmScaffoldIncomplete" in physical,
        "delete_v1_fields_represented": all(
            token in models
            for token in (
                "completed_receipt_version",
                "response_body_canonical_bytes",
                "audit_contract_version",
                "authority_generation",
            )
        )
        and "authority_generation" in tenancy,
        "six_field_private_response_frozen": "DELETE_CONFIRM_RESPONSE_FIELDS"
        in physical
        and "exactly six fields in frozen order" in physical_plan,
        "full_public_response_remains_distinct": "class AppointmentConfirmDeleteProposalOut"
        in schemas
        and "appointment: Optional[AppointmentOut]" in schemas
        and "not silently relabelled" in physical_closeout,
        "initial_route_response_reconstructed": "response_body = AppointmentConfirmDeleteProposalOut("
        in confirm_block
        and "return response_body" in confirm_block,
        "physical_replay_is_stored_bytes": "response_body_canonical_bytes=record.response_body_canonical_bytes"
        in physical,
        "status_product_adapter_precedent_exists": "def compose_product_status_confirm("
        in status_adapter
        and "status_confirm_locked_transaction" in status_adapter,
        "raw_delete_has_separate_legacy_handler": "_apply_appointment_delete("
        in raw_delete_block
        and "claim_appointment_command(" not in raw_delete_block,
        "serial_behavior_result_consumed": "raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal_pass"
        in behavior_closeout,
    }
    failed = [key for key, value in checks.items() if value is not True]
    if failed:
        raise ReviewError(f"structural checks failed: {','.join(failed)}")

    counts = Counter(item["classification"] for item in contract["dimensions"])
    dimension_counts = {
        "satisfied": counts["satisfied"],
        "partial_gap": counts["partial_gap"],
        "blocking_gap": counts["blocking_gap"],
    }
    expected_verdict = (
        "unmounted_adapter_and_response_transition_required"
        if counts["blocking_gap"]
        else "ready_for_bounded_unmounted_route_candidate"
        if counts["partial_gap"]
        else "ready_for_bounded_route_convergence_candidate"
    )
    if contract["verdict"] != expected_verdict:
        raise ReviewError("verdict does not follow closed dimension rule")
    for item in contract["dimensions"]:
        if (item["classification"] == "satisfied") != (item["prerequisite"] is None):
            raise ReviewError(f"prerequisite mismatch: {item['id']}")

    evidence = {
        "schema_version": "raisa.delete_confirm_route_convergence_evidence.v1",
        "result": "raisa_provider_free_read_only_delete_confirm_route_convergence_review_pass",
        "source_head": contract["source_head"],
        "source_bindings": observed_hashes,
        "checks": checks,
        "dimension_counts": dimension_counts,
        "verdict": expected_verdict,
        "next_candidate": contract["next_candidate"],
        "runtime_boundaries": {
            "app_imported": False,
            "route_called": False,
            "database_opened": False,
            "provider_called": False,
            "product_data_opened": False,
        },
    }
    _validate(evidence, _json(evidence_schema_path), "evidence")
    return evidence


def main() -> int:
    evidence = evaluate()
    EVIDENCE_PATH.write_bytes(
        (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
