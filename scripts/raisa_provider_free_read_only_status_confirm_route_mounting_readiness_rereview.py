"""Deterministic text-only status-confirm route-mounting readiness re-review."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview"
)
CONTRACT_PATH = OUT / "route-mounting-readiness-rereview-contract.json"
SCHEMA_PATH = OUT / "route-mounting-readiness-rereview-contract.schema.json"
EVIDENCE_PATH = OUT / "route-mounting-readiness-rereview-evidence.json"
REPORT_PATH = OUT / "route-mounting-readiness-rereview-report.md"
TIMESTAMP = "2026-08-13T09:46:25+10:00"

SOURCE_HASHES = {
    "app/main.py": "0e0f42290688943bc9dd7d5711826acf10430133be0b309eae94bad15da46ca2",
    "app/routers/appointments.py": "59c2923f9cb4dcad75e727fd7614231a0ac5888d30a79f3d1b7949e4fb483ddb",
    "app/dependencies.py": "d44f777f742074f0ee4717d599d7ee71dd6343c7096c87793149c727c1c4b0a9",
    "app/schemas/appointments.py": "d721c94dece8a60fec9f36a542a3c9cc3e6964ef394da8d76f099332c1c6806d",
    "app/services/appointment_idempotency.py": "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
    "app/services/appointment_status_physical.py": "4ab9d0ff3816d85d7eb374e97fec7618e0b922354b104766b2898b0989e56f1b",
    "app/services/appointment_status_composition.py": "42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a",
    "app/models/appointments.py": "d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915",
    "docs/api-spine/openapi/appointment-commands.yaml": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6",
    "scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py": "a45b601a375c7dec7ee08e46be53e23991542cf9699a9ac75798c2e70d2865d8",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json": "00b094830c5f1a0cea19be40cb6761ed5350b6b2ed3fecb53e37ae255333eadd",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-route-mounting-admission-review/route-mounting-review-evidence.json": "7577dfa31cc52ecdb194facca7fc8640116dfc66f412f7c9ae40cd30521b12f1",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal/provider-free-composition-evidence.json": "694d8bc0302feb9b8b99013634ab80b9b60ce0919759dad8f16c1a2382c3e306",
    "docs/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal-closeout.md": "517356cf818818fed927f0937c375d8594365034dba9e6b652e3942306111ab8",
}

SOURCE_ASSERTIONS = {
    "app/main.py": ["app.include_router(appointments.router)"],
    "app/routers/appointments.py": [
        '"/proposals/status-confirm"',
        "decision = claim_appointment_command(",
        "complete_appointment_command(",
        "return response_body",
    ],
    "app/dependencies.py": [
        "def get_current_user(",
        "set_config('app.current_practice_id', :practice_id, true)",
        "def require_role(*roles: UserRole):",
    ],
    "app/schemas/appointments.py": [
        "class AppointmentStatusProposalConfirmationIn",
        "class AppointmentConfirmStatusProposalOut",
    ],
    "app/services/appointment_idempotency.py": [
        "def claim_appointment_command(",
        "def complete_appointment_command(",
    ],
    "app/services/appointment_status_physical.py": [
        "def status_confirm_locked_transaction(",
        "current_authority",
        "response_body_canonical_bytes",
    ],
    "app/services/appointment_status_composition.py": [
        "class StatusConfirmServerIngress:",
        "def compose_status_confirm(",
        "locked_server_factory",
        "effect = stage_effect(decision, locked_request)",
        "response_bytes = _validated_stored_response(decision)",
        "transaction_factory: TransactionFactory = status_confirm_locked_transaction",
    ],
    "app/models/appointments.py": [
        "appointment_state_version = Column(BigInteger",
        "completed_receipt_version = Column(SmallInteger",
        "response_body_canonical_bytes = Column(LargeBinary",
    ],
    "docs/api-spine/openapi/appointment-commands.yaml": [
        "current_backend_path: /appointments/proposals/status-confirm",
        "canonical_openapi_path: /appointments/proposals/status/confirm",
        "operationId: confirmAppointmentStatusProposal",
    ],
    "scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py": [
        'transport["proposal_intent"] != "update_appointment_status"',
        'transport["command"]["kind"] != "status"',
        'server["authority_current"]',
    ],
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json": [
        '"raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal_pass"',
        '"sixteen_serial_scenarios_verified"',
    ],
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-route-mounting-admission-review/route-mounting-review-evidence.json": [
        '"mounted_legacy_route_not_admitted_for_physical_convergence"',
        '"blocking_gap": 7',
    ],
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal/provider-free-composition-evidence.json": [
        '"raisa_provider_free_unmounted_status_confirm_route_convergence_composition_rehearsal_pass"',
        '"mounted_route_imports_composition": false',
    ],
    "docs/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal-closeout.md": [
        "Provider-free unmounted status-confirm route-convergence composition rehearsal closeout",
        "No model, migration, database constraint, route or API Spine schema changed.",
    ],
}


def citation(path: str, start: int, end: int | None = None) -> dict[str, Any]:
    return {"path": path, "line_start": start, "line_end": end or start}


def dimensions() -> list[dict[str, Any]]:
    return [
        {
            "id": "literal_route_mounting",
            "title": "Literal route mounting",
            "prior_classification": "satisfied",
            "classification": "satisfied",
            "admission_blocker": False,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": False,
            "dependency_type": "none",
            "observed_behavior": "The application still includes the appointments router and exposes POST /api/v1/appointments/proposals/status-confirm.",
            "change_from_first_review": "None.",
            "narrowest_prerequisite": "None.",
            "citations": [citation("app/main.py", 39), citation("app/routers/appointments.py", 2920, 2929)],
        },
        {
            "id": "canonical_api_identity",
            "title": "Canonical API identity and current alias",
            "prior_classification": "partial_gap",
            "classification": "partial_gap",
            "admission_blocker": False,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "policy_decision",
            "observed_behavior": "The composition preserves confirmAppointmentStatusProposal, while the mounted hyphenated path remains only a documented alias candidate for the canonical slash path.",
            "change_from_first_review": "The composition now preserves the exact operation and route-family identity; the alias policy is unchanged.",
            "narrowest_prerequisite": "Defer the alias/migration choice until a separately authorised route tranche.",
            "citations": [citation("docs/api-spine/openapi/appointment-commands.yaml", 24, 35), citation("docs/api-spine/openapi/appointment-commands.yaml", 254, 274)],
        },
        {
            "id": "physical_seam_composition",
            "title": "Physical transaction-seam composition",
            "prior_classification": "blocking_gap",
            "classification": "satisfied",
            "admission_blocker": False,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "route_integration",
            "observed_behavior": "The accepted unmounted composition defaults to status_confirm_locked_transaction and enters it with the exact admitted digest, session digest and callbacks; the mounted handler still uses the legacy sequence.",
            "change_from_first_review": "The exact unmounted composition prerequisite requested by the first review now exists and passed.",
            "narrowest_prerequisite": "No further composition contract; later route integration must call the accepted composition without bypass.",
            "citations": [citation("app/services/appointment_status_composition.py", 345, 398), citation("app/routers/appointments.py", 2931, 2945)],
        },
        {
            "id": "current_authority_and_session",
            "title": "Current authority and server-session ingress",
            "prior_classification": "blocking_gap",
            "classification": "blocking_gap",
            "admission_blocker": True,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "product_adapter",
            "observed_behavior": "The composition accepts server-owned session and current-authority inputs and the physical seam rechecks authority, but no application-owned adapter derives a server session or supplies the current-authority callback from authenticated product state.",
            "change_from_first_review": "The injection contract exists; the concrete product adapter does not.",
            "narrowest_prerequisite": "One unmounted application-owned ingress adapter deriving practice, actor, role and server session and supplying fail-closed current-authority checks with no client authority fields.",
            "citations": [citation("app/services/appointment_status_composition.py", 39, 68), citation("app/services/appointment_status_composition.py", 345, 360), citation("app/routers/appointments.py", 2924, 2929)],
        },
        {
            "id": "status_only_discrimination",
            "title": "Status-only discrimination",
            "prior_classification": "blocking_gap",
            "classification": "blocking_gap",
            "admission_blocker": True,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "product_adapter",
            "observed_behavior": "The pure adapter rejects waiting-area variants and the composition accepts an injected admission adapter, but the product route still accepts the status/waiting-area union and does not own that discriminator.",
            "change_from_first_review": "The composition consumes the accepted discriminator; an application-owned adapter remains absent.",
            "narrowest_prerequisite": "An unmounted application-owned admission adapter that admits only update_appointment_status/status and returns waiting-area commands to the unchanged legacy path.",
            "citations": [citation("scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py", 81, 84), citation("app/services/appointment_status_composition.py", 352, 375), citation("app/routers/appointments.py", 2947, 2950)],
        },
        {
            "id": "locked_policy_admission",
            "title": "Locked source version, warnings and terminal policy",
            "prior_classification": "blocking_gap",
            "classification": "blocking_gap",
            "admission_blocker": True,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "product_adapter",
            "observed_behavior": "The composition re-runs admission against an injected locked-server mapping and rejects digest changes, but no product factory recomputes the accepted current-state, warning and terminal policy from the locked appointment.",
            "change_from_first_review": "The locked re-admission mechanism exists; its application-owned state factory does not.",
            "narrowest_prerequisite": "An unmounted locked-state factory that reconstructs exact source version, current fields, warnings and terminal policy solely from the locked appointment and server facts.",
            "citations": [citation("app/services/appointment_status_composition.py", 399, 423), citation("app/models/appointments.py", 71), citation("scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py", 103, 107)],
        },
        {
            "id": "atomic_audit_private_receipt",
            "title": "Atomic audit and private-receipt correlation",
            "prior_classification": "blocking_gap",
            "classification": "blocking_gap",
            "admission_blocker": True,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "product_adapter",
            "observed_behavior": "The composition atomically binds target, audit identity, versions, session digest and canonical bytes, but its stage_effect is injected; the current product helper discards the audit identity and legacy completion omits the v1 fields.",
            "change_from_first_review": "The correlation contract is implemented inside the composition; the concrete status mutation/audit effect adapter is absent.",
            "narrowest_prerequisite": "An unmounted application-owned effect adapter that stages only the locked status mutation and attributable audit and returns that audit identity to the accepted composition.",
            "citations": [citation("app/services/appointment_status_composition.py", 270, 331), citation("app/routers/appointments.py", 2880, 2917), citation("app/routers/appointments.py", 3048, 3055)],
        },
        {
            "id": "canonical_stored_delivery",
            "title": "Canonical stored-receipt delivery",
            "prior_classification": "blocking_gap",
            "classification": "partial_gap",
            "admission_blocker": False,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "route_transport",
            "observed_behavior": "The composition validates and returns the same stored canonical bytes for execute and replay, while the current handler still returns a separately materialized response object.",
            "change_from_first_review": "The requested unmounted stored-receipt mapper now exists; only future transport delivery of those bytes remains.",
            "narrowest_prerequisite": "A later route-transport adapter must deliver composition.stored_response_bytes for both committed and replay results without reserialization drift.",
            "citations": [citation("app/services/appointment_status_composition.py", 334, 342), citation("app/services/appointment_status_composition.py", 433, 450), citation("app/routers/appointments.py", 3038, 3057)],
        },
        {
            "id": "physical_outcome_mapping",
            "title": "Physical outcome to public response mapping",
            "prior_classification": "blocking_gap",
            "classification": "satisfied",
            "admission_blocker": False,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": True,
            "dependency_type": "route_integration",
            "observed_behavior": "The accepted composition closes execute, replay, conflict, revoked-authority, unavailable-target, incomplete-scaffold, locked-admission and integrity outcomes into public responses without route execution.",
            "change_from_first_review": "The closed unmounted outcome mapper requested by the first review now exists and its twelve scenarios passed.",
            "narrowest_prerequisite": "No new mapping contract; later integration must preserve the accepted mapping exactly.",
            "citations": [citation("app/services/appointment_status_composition.py", 433, 466), citation("orchestration/continuity/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal/provider-free-composition-evidence.json", 20, 156)],
        },
        {
            "id": "proved_physical_foundation",
            "title": "Accepted physical durability foundation",
            "prior_classification": "satisfied",
            "classification": "satisfied",
            "admission_blocker": False,
            "unmounted_prerequisite_exists": True,
            "concrete_dependency_remains": False,
            "dependency_type": "none",
            "observed_behavior": "The exact PostgreSQL 16 rehearsal remains accepted over sixteen serial authority, receipt, revocation and rollback scenarios with complete cleanup.",
            "change_from_first_review": "None; the proof is consumed without reopening concurrency, restart or unknown-commit claims.",
            "narrowest_prerequisite": "None.",
            "citations": [citation("orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json", 3, 20)],
        },
    ]


def build_contract() -> dict[str, Any]:
    rows = dimensions()
    counts = {name: sum(row["classification"] == name for row in rows) for name in ("satisfied", "partial_gap", "blocking_gap")}
    return {
        "schema_version": "raisa.status-confirm-route-mounting-readiness-rereview-contract.v1",
        "source_head": "17add9baf2cc3616f7ee4fb8eda3481e2eb13715",
        "composition_source_head": "41f978ae9837cba50737cfb5f457ab62ac28dbdb",
        "review_mode": "provider_free_read_only_exact_file_text_only",
        "source_hashes": SOURCE_HASHES,
        "source_assertions": SOURCE_ASSERTIONS,
        "dimensions": rows,
        "dimension_counts": counts,
        "verdict": "composition_accepted_route_mounting_not_ready",
        "implementation_authorized": False,
        "next_candidate": {
            "id": "provider_free_unmounted_status_confirm_product_adapter_rehearsal",
            "scope": [
                "server_session_and_current_authority_ingress_adapter",
                "status_only_admission_adapter",
                "locked_state_policy_factory",
                "atomic_status_effect_and_audit_identity_adapter",
            ],
            "route_mount_or_call": False,
            "database_execution": False,
        },
        "forbidden": {
            "app_import": False,
            "route_edit_mount_or_call": False,
            "database_or_source_execution": False,
            "provider_network_or_credentials": False,
            "product_or_patient_data": False,
            "command_or_write": False,
            "deployment_release_pages_or_protected_ref": False,
        },
    }


def build_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version", "source_head", "composition_source_head", "review_mode",
            "source_hashes", "source_assertions", "dimensions", "dimension_counts",
            "verdict", "implementation_authorized", "next_candidate", "forbidden",
        ],
        "properties": {
            "schema_version": {"const": "raisa.status-confirm-route-mounting-readiness-rereview-contract.v1"},
            "source_head": {"const": "17add9baf2cc3616f7ee4fb8eda3481e2eb13715"},
            "composition_source_head": {"const": "41f978ae9837cba50737cfb5f457ab62ac28dbdb"},
            "review_mode": {"const": "provider_free_read_only_exact_file_text_only"},
            "source_hashes": {"type": "object", "minProperties": 14, "maxProperties": 14},
            "source_assertions": {"type": "object", "minProperties": 14, "maxProperties": 14},
            "dimensions": {"type": "array", "minItems": 10, "maxItems": 10},
            "dimension_counts": {
                "const": {"satisfied": 4, "partial_gap": 2, "blocking_gap": 4}
            },
            "verdict": {"const": "composition_accepted_route_mounting_not_ready"},
            "implementation_authorized": {"const": False},
            "next_candidate": {"type": "object"},
            "forbidden": {
                "type": "object",
                "minProperties": 7,
                "additionalProperties": {"const": False},
            },
        },
    }


def validate(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = sorted(error.message for error in Draft202012Validator(schema).iter_errors(contract))
    if contract != build_contract():
        errors.append("contract_differs_from_frozen_review")
    if schema != build_schema():
        errors.append("schema_differs_from_frozen_review")
    for path, expected_hash in SOURCE_HASHES.items():
        actual_hash = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"source_hash_mismatch:{path}")
        source_text = (ROOT / path).read_text(encoding="utf-8")
        for snippet in SOURCE_ASSERTIONS[path]:
            if snippet not in source_text:
                errors.append(f"source_assertion_missing:{path}:{snippet}")
    rows = contract.get("dimensions", [])
    if [row.get("id") for row in rows] != [row["id"] for row in dimensions()]:
        errors.append("dimension_order_mismatch")
    if any(row.get("admission_blocker") != (row.get("classification") == "blocking_gap") for row in rows):
        errors.append("blocker_classification_mismatch")
    if any(not row.get("unmounted_prerequisite_exists") for row in rows):
        errors.append("accepted_unmounted_prerequisite_lost")
    if any(contract.get("forbidden", {}).values()):
        errors.append("forbidden_authority_open")
    return sorted(set(errors))


def hostile_mutations(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def add(name: str, path: tuple[Any, ...], value: Any) -> None:
        changed = copy.deepcopy(contract)
        cursor: Any = changed
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = value
        mutations.append((name, changed))

    add("schema_version", ("schema_version",), "v2")
    add("source_head", ("source_head",), "0" * 40)
    add("composition_head", ("composition_source_head",), "0" * 40)
    add("review_mode", ("review_mode",), "runtime")
    add("verdict", ("verdict",), "ready_for_bounded_route_mounting_candidate")
    add("implementation", ("implementation_authorized",), True)
    add("next_route", ("next_candidate", "route_mount_or_call"), True)
    add("next_database", ("next_candidate", "database_execution"), True)
    for key in contract["forbidden"]:
        add(f"forbidden_{key}", ("forbidden", key), True)
    for index, row in enumerate(contract["dimensions"]):
        alternate = "satisfied" if row["classification"] != "satisfied" else "blocking_gap"
        add(f"dimension_class_{index}", ("dimensions", index, "classification"), alternate)
        add(f"dimension_blocker_{index}", ("dimensions", index, "admission_blocker"), not row["admission_blocker"])
        add(f"dimension_prerequisite_{index}", ("dimensions", index, "unmounted_prerequisite_exists"), False)
        add(f"dimension_dependency_{index}", ("dimensions", index, "dependency_type"), "none" if row["dependency_type"] != "none" else "product_adapter")
    for index, path in enumerate(contract["source_hashes"]):
        add(f"source_hash_{index}", ("source_hashes", path), "0" * 64)
    return mutations


def build_evidence(contract: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    canonical_errors = validate(contract, schema)
    admitted = [name for name, candidate in hostile_mutations(contract) if not validate(candidate, schema)]
    return {
        "schema_version": "raisa.status-confirm-route-mounting-readiness-rereview-evidence.v1",
        "date": "2026-08-13",
        "timestamp": f"{TIMESTAMP} (Australia/Brisbane)",
        "result": "raisa_provider_free_read_only_status_confirm_route_mounting_readiness_rereview_pass" if not canonical_errors and not admitted else "failed",
        "verdict": contract["verdict"],
        "canonical_errors": canonical_errors,
        "dimension_counts": contract["dimension_counts"],
        "hostile_mutations": {"attempted": len(hostile_mutations(contract)), "rejected": len(hostile_mutations(contract)) - len(admitted), "admitted": admitted},
        "source_hash_count": len(SOURCE_HASHES),
        "next_candidate": contract["next_candidate"],
        "forbidden": contract["forbidden"],
    }


def render_report(contract: dict[str, Any], evidence: dict[str, Any]) -> str:
    lines = [
        "# Status-confirm route-mounting readiness re-review",
        "",
        "Date: 2026-08-13",
        "",
        f"Timestamp: {TIMESTAMP} (Australia/Brisbane)",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Verdict: `{contract['verdict']}`",
        "",
        "## Dimension result",
        "",
        "| # | Dimension | Prior | Current | Remaining dependency |",
        "|---:|---|---|---|---|",
    ]
    for index, row in enumerate(contract["dimensions"], start=1):
        lines.append(
            f"| {index} | {row['title']} | `{row['prior_classification']}` | "
            f"`{row['classification']}` | `{row['dependency_type']}` |"
        )
    lines.extend([
        "",
        "Four dimensions are satisfied, two retain nonblocking partial gaps and four remain blocking product-adapter gaps. The route is not ready to mount onto the accepted composition.",
        "",
        "## Narrowest next tranche",
        "",
        "A single provider-free, unmounted status-confirm product-adapter rehearsal should close the four mutually dependent blockers together: server-session/current-authority ingress, status-only admission, locked-state policy reconstruction, and atomic status-effect/audit-identity staging. It must not edit, mount or call a route or execute a database.",
        "",
        "## Evidence boundary",
        "",
        f"All {evidence['source_hash_count']} frozen source hashes matched. "
        f"All {evidence['hostile_mutations']['attempted']} hostile contract mutations were rejected. "
        "The reviewer imported no application runtime and performed no route, database, provider, network, product-data or command action.",
        "",
    ])
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    contract = build_contract()
    schema = build_schema()
    evidence = build_evidence(contract, schema)
    if args.write:
        write_json(CONTRACT_PATH, contract)
        write_json(SCHEMA_PATH, schema)
        write_json(EVIDENCE_PATH, evidence)
        REPORT_PATH.write_text(render_report(contract, evidence), encoding="utf-8")
    else:
        print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["result"].endswith("_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
