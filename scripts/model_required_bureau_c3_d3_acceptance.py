"""Provider-free deterministic acceptance for Bureau C3/D3 architecture."""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "orchestration/continuity/model-required-bureau-c3-d3"
PARENT_ROOT = (
    ROOT
    / "orchestration/continuity/model-required-bureau-provider-free-successor-lanes"
)
CONTRACT = ARTIFACT_ROOT / "c3-d3-contract.json"
CONTRACT_SCHEMA = ARTIFACT_ROOT / "c3-d3-contract.schema.json"
ANATOMY = PARENT_ROOT / "technical-anatomy-frame.example.json"
DIAGNOSIS = PARENT_ROOT / "technical-diagnosis-candidate.example.json"
DESIGN = ROOT / "docs/emr4-model-required-bureau-c3-d3-provider-free-architecture.md"
THREAT = ROOT / "docs/security/emr4-model-required-bureau-c3-d3-threat-model-delta.md"
C3_ANALYSIS = (
    ROOT / "orchestration/agent_inbox/codex/model-required-bureau-c3-native-analysis.md"
)
D3_ANALYSIS = (
    ROOT / "orchestration/agent_inbox/codex/model-required-bureau-d3-native-analysis.md"
)
DEFAULT_OUTPUT = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
EXPECTED_HEAD = "3008cdb4d7b5801c45024f7361fb4294aa76fc48"
EXPECTED_RESULT = "model_required_bureau_c3_d3_provider_free_architecture_pass"
SCHEMA_EXAMPLES = {
    "recovery_plan": (
        ARTIFACT_ROOT / "recovery-plan-candidate.schema.json",
        ARTIFACT_ROOT / "recovery-plan-candidate.example.json",
    ),
    "recovery_authority": (
        ARTIFACT_ROOT / "recovery-authority-decision.schema.json",
        ARTIFACT_ROOT / "recovery-authority-decision.example.json",
    ),
    "update_promotion": (
        ARTIFACT_ROOT / "update-promotion-rollback-plan.schema.json",
        ARTIFACT_ROOT / "update-promotion-rollback-plan.example.json",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be an object")
    return value


def validate(schema_path: Path, instance: dict[str, Any]) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(instance),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise ValueError(f"{schema_path.name}: {errors[0].message}")


def canonical_sha256(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def effective_recovery_expiry(
    plan: dict[str, Any], anatomy: dict[str, Any]
) -> str:
    observation_by_id = {
        item["observation_id"]: item for item in anatomy["observations"]
    }
    values = [_parse_time(plan["expires_at"]), _parse_time(anatomy["expires_at"])]
    values.extend(
        _parse_time(observation_by_id[item["observation_id"]]["expires_at"])
        for item in plan["preconditions"]
        if item["observation_id"] in observation_by_id
    )
    return min(values).isoformat().replace("+00:00", "Z")


def proofread_recovery_plan(
    plan: dict[str, Any], *, now: str = "2026-08-04T08:00:30Z"
) -> str | None:
    try:
        validate(SCHEMA_EXAMPLES["recovery_plan"][0], plan)
    except ValueError:
        return "SCHEMA_REJECTED"
    anatomy = load_json(ANATOMY)
    diagnosis = load_json(DIAGNOSIS)
    if (
        plan["diagnosis_candidate_id"] != diagnosis["candidate_id"]
        or plan["anatomy_frame_id"] != anatomy["frame_id"]
        or plan["anatomy_version"] != anatomy["anatomy_version"]
        or plan["context_sha256"] != diagnosis["context_sha256"]
    ):
        return "STALE_OR_SUPERSEDED"
    runbooks = {item["runbook_id"] for item in anatomy["signed_runbook_catalog"]}
    if plan["runbook_id"] not in runbooks:
        return "UNKNOWN_RUNBOOK"
    observations = {
        item["observation_id"]: item for item in anatomy["observations"]
    }
    for precondition in plan["preconditions"]:
        source = observations.get(precondition["observation_id"])
        if source is None or source["content_sha256"] != precondition["expected_sha256"]:
            return "UNKNOWN_EVIDENCE"
    forbidden = (
        "powershell",
        "cmd.exe",
        "http://",
        "https://",
        "kubectl",
        "invoke-expression",
        "drop table",
        "successfully recovered",
    )
    rendered = json.dumps(plan, sort_keys=True).lower()
    if any(token in rendered for token in forbidden):
        return "EXECUTABLE_CONTENT"
    if _parse_time(now) >= _parse_time(effective_recovery_expiry(plan, anatomy)):
        return "STALE_OR_SUPERSEDED"
    return None


def classify_recovery(plan: dict[str, Any]) -> str:
    operation = plan["operation_class"]
    target = plan["target"]["kind"]
    blast = plan["maximum_blast_radius"]
    reversibility = plan["reversibility"]
    forbidden = {
        "generic_shell",
        "generic_sql",
        "generic_cloud",
        "credential_change",
        "authority_policy_change",
        "unallowlisted_operation",
    }
    if (
        operation in forbidden
        or target in {"multi_environment", "unknown"}
        or blast == "multi_environment_or_unknown"
        or reversibility in {"conditional_or_unknown", "irreversible"}
    ):
        return "forbidden_autonomous_action"
    if (
        operation == "observe"
        and target == "observation"
        and blast == "observation_only"
        and reversibility == "not_applicable"
    ):
        return "observe_explain_only"
    if operation in {
        "database_operation",
        "security_operation",
        "data_supply_operation",
    } or target in {"database", "security_control", "data_supply"}:
        return "dual_review_database_security_or_data_supply"
    if operation in {"rollback", "failover"}:
        return "human_approved_rollback_or_failover"
    if (
        operation == "scoped_service_recovery"
        and target in {"service", "component"}
        and blast in {"single_process", "single_service"}
        and reversibility == "deterministic_rollback_proven"
        and plan["rollback"]["kind"] != "none"
    ):
        return "reversible_scoped_service_recovery"
    return "forbidden_autonomous_action"


def authority_decision(plan: dict[str, Any]) -> dict[str, Any]:
    contract = load_json(CONTRACT)
    tiers = {item["id"]: item for item in contract["c3"]["tiers"]}
    computed = classify_recovery(plan)
    tier = tiers[computed]
    state = (
        "observe_release"
        if computed == "observe_explain_only"
        else "denied"
        if computed == "forbidden_autonomous_action"
        else "review_required"
    )
    return {
        "schema_version": "emr4.recovery_authority_decision.v1",
        "decision_id": "71000000-0000-4000-8000-000000000001",
        "plan_id": plan["plan_id"],
        "plan_revision": 1,
        "plan_sha256": canonical_sha256(plan),
        "policy_version": contract["c3"]["risk_policy_version"],
        "computed_risk_tier": computed,
        "required_authority": tier["required_authority"],
        "minimum_reviewer_count": tier["minimum_reviewer_count"],
        "required_roles": tier["required_roles"],
        "separation_of_duties": tier["separation_of_duties"],
        "candidate_risk_overridden": plan["proposed_risk_tier"] != computed,
        "future_one_use_execution_evidence": tier[
            "future_one_use_execution_evidence"
        ],
        "effective_expiry": effective_recovery_expiry(plan, load_json(ANATOMY)),
        "plan_change_invalidates_reviews": True,
        "current_state": state,
        "denial_codes": (
            ["OPERATION_FORBIDDEN"]
            if computed == "forbidden_autonomous_action"
            else []
        ),
        "command_envelope_issued": False,
        "actuator_gate": "closed",
        "execution_authorized": False,
    }


def _promotion_mapping() -> dict[str, dict[str, Any]]:
    return {
        item["update_class"]: item for item in load_json(CONTRACT)["d3"]["classes"]
    }


def promotion_plan_for_class(
    base: dict[str, Any], update_class: str
) -> dict[str, Any]:
    value = deepcopy(base)
    mapping = _promotion_mapping()[update_class]
    value["update_class"] = update_class
    value["future_command_family"] = mapping["future_command_family"]
    value["canary"]["kind"] = mapping["canary_kind"]
    value["review"]["required_authority"] = mapping["required_authority"]
    value["review"]["minimum_reviewer_count"] = mapping[
        "minimum_reviewer_count"
    ]
    value["review"]["required_roles"] = mapping["required_roles"]
    value["review"]["distinct_reviewers_required"] = (
        mapping["minimum_reviewer_count"] > 1
    )
    value["activation"]["future_command_family"] = mapping[
        "future_command_family"
    ]
    barriers = {
        "application_dependency_build": "release_pointer_compare_and_swap",
        "database_schema_migration": "migration_transaction_or_maintenance_barrier",
        "reference_dataset": "immutable_dataset_pointer_compare_and_swap",
        "operational_clinical_policy": "versioned_policy_pointer_compare_and_swap",
    }
    value["activation"]["class_specific_barrier"] = barriers[update_class]
    value["last_known_good_rollback"]["kind"] = mapping["rollback_kind"]
    value["last_known_good_rollback"]["source_lifecycle"] = (
        "active"
        if update_class in {"reference_dataset", "operational_clinical_policy"}
        else "not_applicable"
    )
    if update_class == "database_schema_migration":
        for check in ("backup_restore_evidence", "rollback_feasibility"):
            if check not in value["validation"]["required_checks"]:
                value["validation"]["required_checks"].append(check)
    return value


def _validate_contract_and_examples() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    validate(CONTRACT_SCHEMA, contract)
    if contract["source_head"] != EXPECTED_HEAD:
        raise ValueError("source HEAD drift")
    tier_ids = [item["id"] for item in contract["c3"]["tiers"]]
    if len(tier_ids) != 5 or len(set(tier_ids)) != 5:
        raise ValueError("C3 risk tier duplication")
    if contract["c3"]["candidate_may_set_final_risk"]:
        raise ValueError("candidate acquired risk authority")
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        validate(schema_path, load_json(example_path))
    plan = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    if proofread_recovery_plan(plan) is not None:
        raise ValueError("nominal recovery plan was denied")
    decision = authority_decision(plan)
    expected_decision = load_json(SCHEMA_EXAMPLES["recovery_authority"][1])
    if decision != expected_decision:
        raise ValueError("recovery authority decision example drift")
    base_promotion = load_json(SCHEMA_EXAMPLES["update_promotion"][1])
    class_plans: dict[str, str] = {}
    for update_class, mapping in _promotion_mapping().items():
        candidate = promotion_plan_for_class(base_promotion, update_class)
        validate(SCHEMA_EXAMPLES["update_promotion"][0], candidate)
        class_plans[update_class] = mapping["future_command_family"]
    return {
        "closed_schema_count": 1 + len(SCHEMA_EXAMPLES),
        "canonical_example_count": len(SCHEMA_EXAMPLES),
        "risk_tier_count": len(tier_ids),
        "update_class_count": len(class_plans),
        "class_specific_command_families": class_plans,
        "computed_nominal_risk": decision["computed_risk_tier"],
        "candidate_risk_overridden": decision["candidate_risk_overridden"],
        "effective_expiry": decision["effective_expiry"],
    }


def _validate_recovery_denials_and_tiers() -> dict[str, Any]:
    base = load_json(SCHEMA_EXAMPLES["recovery_plan"][1])
    denial_cases: dict[str, str] = {}
    changed = deepcopy(base)
    changed["runbook_id"] = "unknown-runbook"
    denial_cases["unknown_runbook"] = proofread_recovery_plan(changed) or ""
    changed = deepcopy(base)
    changed["preconditions"][0]["expected_sha256"] = "0" * 64
    denial_cases["unknown_evidence"] = proofread_recovery_plan(changed) or ""
    changed = deepcopy(base)
    changed["expected_effect"] = "Use https://example.invalid/run"
    denial_cases["executable_content"] = proofread_recovery_plan(changed) or ""
    denial_cases["expired"] = (
        proofread_recovery_plan(base, now="2026-08-04T08:01:00Z") or ""
    )
    expected = {
        "unknown_runbook": "UNKNOWN_RUNBOOK",
        "unknown_evidence": "UNKNOWN_EVIDENCE",
        "executable_content": "EXECUTABLE_CONTENT",
        "expired": "STALE_OR_SUPERSEDED",
    }
    if denial_cases != expected:
        raise ValueError(f"C3 denial drift: {denial_cases}")

    tiers: dict[str, str] = {"scoped": classify_recovery(base)}
    observe = deepcopy(base)
    observe["operation_class"] = "observe"
    observe["target"]["kind"] = "observation"
    observe["maximum_blast_radius"] = "observation_only"
    observe["reversibility"] = "not_applicable"
    observe["rollback"] = {"kind": "none", "runbook_id": None, "target_sha256": None}
    tiers["observe"] = classify_recovery(observe)
    rollback = deepcopy(base)
    rollback["operation_class"] = "rollback"
    rollback["maximum_blast_radius"] = "single_environment"
    tiers["rollback"] = classify_recovery(rollback)
    database = deepcopy(base)
    database["operation_class"] = "database_operation"
    database["target"]["kind"] = "database"
    database["maximum_blast_radius"] = "single_environment"
    tiers["database"] = classify_recovery(database)
    forbidden = deepcopy(base)
    forbidden["operation_class"] = "generic_shell"
    tiers["forbidden"] = classify_recovery(forbidden)
    expected_tiers = {
        "scoped": "reversible_scoped_service_recovery",
        "observe": "observe_explain_only",
        "rollback": "human_approved_rollback_or_failover",
        "database": "dual_review_database_security_or_data_supply",
        "forbidden": "forbidden_autonomous_action",
    }
    if tiers != expected_tiers:
        raise ValueError(f"C3 risk classification drift: {tiers}")
    return {"denials": denial_cases, "risk_cases": tiers}


def _validate_promotion_denials() -> dict[str, str]:
    schema_path = SCHEMA_EXAMPLES["update_promotion"][0]
    base = load_json(SCHEMA_EXAMPLES["update_promotion"][1])
    mutations: dict[str, dict[str, Any]] = {}
    changed = deepcopy(base)
    changed["future_command_family"] = "application_build_promotion"
    mutations["cross_class_command"] = changed
    changed = deepcopy(base)
    changed["canary"]["kind"] = "single_disposable_instance"
    mutations["cross_class_canary"] = changed
    changed = deepcopy(base)
    changed["review"]["minimum_reviewer_count"] = 1
    mutations["review_downgrade"] = changed
    changed = deepcopy(base)
    changed["shadow"]["authoritative_reads"] = True
    mutations["shadow_serving"] = changed
    changed = deepcopy(base)
    changed["readback"]["success_claimed"] = True
    mutations["unread_success"] = changed
    changed = deepcopy(base)
    changed["last_known_good_rollback"]["source_lifecycle"] = "withdrawn"
    mutations["withdrawn_lkg"] = changed
    denials: dict[str, str] = {}
    for case_id, value in mutations.items():
        try:
            validate(schema_path, value)
        except ValueError:
            denials[case_id] = "SCHEMA_REJECTED"
        else:
            denials[case_id] = "UNEXPECTED_ADMISSION"
    if set(denials.values()) != {"SCHEMA_REJECTED"}:
        raise ValueError(f"D3 denial drift: {denials}")
    return denials


def _validate_documents() -> dict[str, Any]:
    paths = (DESIGN, THREAT, C3_ANALYSIS, D3_ANALYSIS)
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    required = (
        "provider_free_c3_d3_architecture_and_proof",
        "there is no generic update command",
        "execution_authorized: false",
        "fresh authoritative readback",
        "last-known-good",
        "access ai remains closed",
        "docs/branding/",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise ValueError(f"document boundary missing: {missing}")
    return {"document_count": len(paths), "required_boundary_count": len(required)}


def build_evidence() -> dict[str, Any]:
    contract_and_examples = _validate_contract_and_examples()
    recovery = _validate_recovery_denials_and_tiers()
    promotion = _validate_promotion_denials()
    documents = _validate_documents()
    contract = load_json(CONTRACT)
    side_effects = contract["authority_and_side_effects"]
    if set(side_effects.values()) != {0}:
        raise ValueError("candidate side-effect accounting is not zero")
    artifacts = [CONTRACT, CONTRACT_SCHEMA, DESIGN, THREAT, C3_ANALYSIS, D3_ANALYSIS]
    artifacts.extend(path for pair in SCHEMA_EXAMPLES.values() for path in pair)
    return {
        "schema_version": "emr4.model_required_bureau_c3_d3_acceptance.v1",
        "passed": True,
        "result": EXPECTED_RESULT,
        "source_head": EXPECTED_HEAD,
        "contract_and_examples": contract_and_examples,
        "recovery_policy": recovery,
        "promotion_denials": promotion,
        "documents": documents,
        "authority_and_side_effects": side_effects,
        "artifact_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in artifacts
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = build_evidence()
    if args.check:
        if load_json(args.output) != evidence:
            raise SystemExit("acceptance evidence is stale")
    else:
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {"passed": True, "result": EXPECTED_RESULT, "source_head": EXPECTED_HEAD}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
