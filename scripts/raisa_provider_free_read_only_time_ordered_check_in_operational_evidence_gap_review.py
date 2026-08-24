"""Join accepted check-in temporal and operational evidence without execution."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-authored-synthetic-"
    "time-ordered-canonical-check-in-context-operational-evidence-gap-review"
)
CONTRACT_PATH = f"{BASE}/contract.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"
RESULT = (
    "raisa_provider_free_read_only_time_ordered_check_in_operational_"
    "evidence_gap_review_pass"
)
SCHEMA_VERSION = "raisa.time_ordered_check_in_operational_gap_review_contract.v1"
EVIDENCE_SCHEMA_VERSION = (
    "raisa.time_ordered_check_in_operational_gap_review_evidence.v1"
)
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
SOURCE_IDS = (
    "temporal_composition_evidence",
    "default_off_route_closeout",
    "rollback_unknown_response_attestation",
    "runtime_role_tenant_attestation",
    "admission_blocker_priority_evidence",
)
CLASSIFICATIONS = (
    "accepted_route_and_database_evidence",
    "accepted_route_evidence_and_in_memory_composition_only",
    "accepted_database_evidence_and_in_memory_composition_only",
    "in_memory_composition_only",
)
RECOMMENDATIONS = (
    "no_incremental_operational_rehearsal_justified",
    "one_incremental_provider_free_operational_rehearsal_justified",
)
NEXT_OPERATION = (
    "raisa-provider-free-database-backed-default-off-canonical-check-in-"
    "post-proposal-revalidation-rehearsal"
)


class ContractError(RuntimeError):
    """The frozen contract or one of its accepted sources changed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def canonical_text(root: Path, relative: str) -> str:
    root = root.resolve()
    path = (root / relative).resolve()
    require(path.is_relative_to(root), f"path escapes repository: {relative}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"non-UTF-8 source: {relative}") from exc
    require("\r" not in text.replace("\r\n", ""), f"bare CR source: {relative}")
    return text.replace("\r\n", "\n")


def canonical_sha256(root: Path, relative: str) -> str:
    return hashlib.sha256(canonical_text(root, relative).encode("utf-8")).hexdigest()


def load_json(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads(canonical_text(root, relative))
    require(isinstance(value, dict), f"JSON object required: {relative}")
    return value


def git_object_is_ancestor(root: Path, object_id: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
            cwd=root,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def validate_contract(
    contract: dict[str, Any], root: Path, *, check_git: bool = True
) -> None:
    require(
        set(contract)
        == {
            "schema_version",
            "operation_id",
            "planning_source",
            "hash_mode",
            "accepted_sources",
            "expected_temporal_scenario_count",
            "expected_cross_family_pair_count",
            "expected_temporal_claim_ceiling",
            "physical_classification_vocabulary",
            "recommendation_vocabulary",
            "expected_admission_readiness",
            "expected_repository_prerequisites_remaining",
            "minimum_hostile_mutations",
        },
        "contract keys changed",
    )
    require(contract["schema_version"] == SCHEMA_VERSION, "schema changed")
    require(contract["hash_mode"] == HASH_MODE, "hash mode changed")
    require(contract["expected_temporal_scenario_count"] == 30, "temporal scenario count changed")
    require(contract["expected_cross_family_pair_count"] == 74, "cross-family pair count changed")
    require(
        contract["expected_temporal_claim_ceiling"]
        == "minimum_pairwise_authored_synthetic_in_memory_adapter_composition_and_precedence_only",
        "temporal claim ceiling changed",
    )
    require(tuple(contract["physical_classification_vocabulary"]) == CLASSIFICATIONS, "classification vocabulary changed")
    require(tuple(contract["recommendation_vocabulary"]) == RECOMMENDATIONS, "recommendation vocabulary changed")
    require(contract["expected_admission_readiness"] == "11_0_1", "readiness changed")
    require(contract["expected_repository_prerequisites_remaining"] == 0, "admission prerequisite reopened")
    planning_source = contract["planning_source"]
    require(re.fullmatch(r"[0-9a-f]{40}", planning_source) is not None, "short planning source")
    if check_git:
        require(git_object_is_ancestor(root, planning_source), "planning source not ancestral")

    sources = contract["accepted_sources"]
    require(isinstance(sources, list) and len(sources) == 5, "source count changed")
    require(tuple(item.get("id") for item in sources) == SOURCE_IDS, "source order changed")
    for item in sources:
        require(set(item) == {"id", "git_object", "path", "sha256"}, "source shape changed")
        require(re.fullmatch(r"[0-9a-f]{40}", item["git_object"]) is not None, "short Git object")
        require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, "invalid source hash")
        require(canonical_sha256(root, item["path"]) == item["sha256"], f"source changed: {item['id']}")
        if check_git:
            require(git_object_is_ancestor(root, item["git_object"]), f"non-ancestor source: {item['id']}")


def validate_sources(
    contract: dict[str, Any], root: Path
) -> tuple[dict[str, Any], str, dict[str, Any], dict[str, Any], dict[str, Any]]:
    sources = {item["id"]: item["path"] for item in contract["accepted_sources"]}
    temporal = load_json(root, sources["temporal_composition_evidence"])
    route = canonical_text(root, sources["default_off_route_closeout"])
    transaction = load_json(root, sources["rollback_unknown_response_attestation"])
    role = load_json(root, sources["runtime_role_tenant_attestation"])
    blocker = load_json(root, sources["admission_blocker_priority_evidence"])

    require(temporal.get("claim_ceiling") == contract["expected_temporal_claim_ceiling"], "temporal ceiling changed")
    require(temporal.get("pairwise_coverage", {}).get("scenario_count") == 30, "scenario count changed")
    require(temporal.get("pairwise_coverage", {}).get("required_cross_family_pair_count") == 74, "pair count changed")
    require(len(temporal.get("scenario_results", [])) == 30, "scenario result count changed")
    require(all(temporal.get("unmasked_witnesses", {}).values()), "masked temporal witness")

    route_prose = " ".join(route.split())
    for marker in (
        "feature flag and exact authored-synthetic practice allowlist still deny",
        "35/35 database-backed A5.1 runtime checks pass",
        "in-transaction Receptionist",
        "commit/rollback and exact committed readback",
        "does not prove an ordinary product command",
    ):
        require(marker in route_prose, f"route marker changed: {marker}")

    rollback = transaction.get("explicit_rollback", {})
    require(
        rollback.get("readback_counts") == {"audit": 0, "effect": 0, "receipt": 0},
        "rollback reading changed",
    )
    unknown = transaction.get("ambiguous_response", {})
    require(unknown.get("success_released") is False, "unknown response released success")
    require(unknown.get("retry_count") == 0, "unknown response retried")
    readback = transaction.get("authoritative_readback", {})
    require(readback.get("counts", {}).get("effect") == 1, "unknown response effect changed")
    require(
        readback.get("counts", {}).get("audit") == 1
        and readback.get("counts", {}).get("receipt") == 1,
        "unknown response packet changed",
    )

    catalogue = role.get("role_catalogue", {})
    require(catalogue.get("superuser") is False and catalogue.get("bypass_rls") is False, "role bypass posture changed")
    require(catalogue.get("product_relation_privileges") == 0, "role product privilege changed")
    require(len(role.get("scenarios", [])) == 12 and all(item.get("status") == "passed" for item in role["scenarios"]), "role scenarios changed")

    readiness = blocker.get("readiness_reconciliation", {})
    require(readiness.get("current") == {"satisfied": 11, "blocking_gap": 0, "operational_evidence_gap": 1}, "11/0/1 reading changed")
    require(readiness.get("repository_prerequisites_remaining") == 0, "repository prerequisite reopened")
    require(readiness.get("ordinary_admission_releases") == 0, "ordinary admission released")
    require(len(blocker.get("external_facts", [])) == 6, "external fact count changed")
    require(all(item.get("status") == "absent" for item in blocker["external_facts"]), "external fact inferred")
    return temporal, route, transaction, role, blocker


def hostile_mutations(contract: dict[str, Any], root: Path) -> int:
    candidates: list[dict[str, Any]] = []
    for index in range(5):
        for key, value in (
            ("git_object", contract["accepted_sources"][index]["git_object"][:7]),
            ("sha256", "0" * 64),
            ("path", "AGENTS.md"),
        ):
            candidate = copy.deepcopy(contract)
            candidate["accepted_sources"][index][key] = value
            candidates.append(candidate)
    for key, value in (
        ("planning_source", contract["planning_source"][:7]),
        ("hash_mode", "ambient"),
        ("expected_temporal_scenario_count", 29),
        ("expected_cross_family_pair_count", 73),
        ("expected_temporal_claim_ceiling", "physical"),
        ("expected_admission_readiness", "12_0_0"),
        ("expected_repository_prerequisites_remaining", 1),
    ):
        candidate = copy.deepcopy(contract)
        candidate[key] = value
        candidates.append(candidate)
    for index in range(4):
        candidate = copy.deepcopy(contract)
        candidate["physical_classification_vocabulary"][index] += "_drift"
        candidates.append(candidate)
    for index in range(2):
        candidate = copy.deepcopy(contract)
        candidate["recommendation_vocabulary"][index] += "_drift"
        candidates.append(candidate)
    for index in range(5):
        candidate = copy.deepcopy(contract)
        del candidate["accepted_sources"][index]
        candidates.append(candidate)
    while len(candidates) < contract["minimum_hostile_mutations"]:
        candidate = copy.deepcopy(contract)
        candidate[f"extra_{len(candidates)}"] = True
        candidates.append(candidate)

    rejected = 0
    for candidate in candidates:
        try:
            validate_contract(candidate, root, check_git=False)
        except (ContractError, KeyError, OSError, TypeError):
            rejected += 1
        else:
            raise ContractError("hostile contract mutation escaped")
    require(rejected >= contract["minimum_hostile_mutations"], "hostile matrix too small")
    return rejected


def build_evidence(contract: dict[str, Any], root: Path) -> dict[str, Any]:
    temporal, _route, _transaction, _role, blocker = validate_sources(contract, root)
    rejected = hostile_mutations(contract, root)
    transitions = [
        ("unchanged_valid_first_execution", CLASSIFICATIONS[0]),
        ("eligible_waiting_area_assign_or_preserve", CLASSIFICATIONS[0]),
        ("proposal_stale_after_intervening_state_update", CLASSIFICATIONS[0]),
        ("signed_evidence_invalidated", CLASSIFICATIONS[0]),
        ("exact_replay_conflict_and_in_progress", CLASSIFICATIONS[0]),
        ("precommit_composition_failure_and_rollback", CLASSIFICATIONS[0]),
        ("commit_outcome_unknown_and_authoritative_readback", CLASSIFICATIONS[2]),
        ("current_receptionist_revoked_after_proposal", CLASSIFICATIONS[1]),
        ("assigned_waiting_area_became_inactive_after_proposal", CLASSIFICATIONS[1]),
        ("restricted_role_and_cross_tenant_denial", CLASSIFICATIONS[2]),
    ]
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operation_id": contract["operation_id"],
        "result": RESULT,
        "review_baseline": contract["planning_source"],
        "source_bindings": contract["accepted_sources"],
        "temporal_reading": {
            "scenario_count": temporal["pairwise_coverage"]["scenario_count"],
            "cross_family_pair_count": temporal["pairwise_coverage"]["required_cross_family_pair_count"],
            "claim_ceiling": temporal["claim_ceiling"],
            "unmasked_witness_count": sum(temporal["unmasked_witnesses"].values()),
            "physical_capability_claimed": False,
        },
        "physical_evidence_inventory": [
            {"property": "default_off_and_authored_synthetic_allowlist_denial", "route": True, "database": False},
            {"property": "eligible_write_and_waiting_area_assignment_or_preservation", "route": True, "database": True},
            {"property": "locked_source_state_and_freshness_revalidation", "route": True, "database": True},
            {"property": "signed_evidence_verification", "route": True, "database": True},
            {"property": "idempotency_replay_conflict_and_in_progress", "route": True, "database": True},
            {"property": "atomic_precommit_rollback", "route": True, "database": True},
            {"property": "unknown_response_authoritative_readback", "route": False, "database": True},
            {"property": "restricted_role_and_cross_tenant_denial", "route": False, "database": True},
        ],
        "temporal_transition_classification": [
            {"transition": transition, "classification": classification}
            for transition, classification in transitions
        ],
        "gap_classification": {
            "recommendation": RECOMMENDATIONS[1],
            "gap_id": "post_proposal_current_authority_and_waiting_area_revalidation_through_database_backed_route",
            "gap_kind": "non_admission_product_assurance",
            "unbacked_temporal_transition_count": 2,
            "next_operation": NEXT_OPERATION,
            "next_scope": [
                "receptionist_role_revoked_after_proposal_before_confirmation",
                "assigned_waiting_area_deactivated_after_proposal_before_confirmation",
            ],
            "ordinary_admission_prerequisite_reopened": False,
            "unknown_response_rehearsal_repeated": False,
            "runtime_role_tenant_rehearsal_repeated": False,
        },
        "admission_boundary": {
            "readiness": blocker["readiness_reconciliation"]["current"],
            "repository_prerequisites_remaining": 0,
            "external_facts_absent": 6,
            "ordinary_admission_releases": 0,
            "verdict": blocker["readiness_reconciliation"]["verdict"],
        },
        "parallelism": {
            "deepseek": "declined_negative_no_bounded_work_package",
            "gemini": "not_applicable_neutral_closed_predicates",
            "native_subagents": "declined_negative_serial_boundary",
            "serial_owner": "gpt_sol",
        },
        "verification": {
            "source_hashes_matched": 5,
            "full_git_bindings_matched": 5,
            "hostile_mutations_rejected": rejected,
            "temporal_scenarios_joined": 30,
            "external_facts_inferred": 0,
        },
        "closed_boundaries": {
            "historical_or_local_data_accessed": False,
            "route_database_client_or_runtime_executed": False,
            "provider_model_network_or_harness_used": False,
            "product_api_schema_client_or_configuration_changed": False,
            "ordinary_practice_enabled": False,
            "product_patient_appointment_clinical_or_protected_data_used": False,
            "production_deployment_release_pages_or_protected_ref_moved": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    transition_lines = [
        f"| `{item['transition']}` | `{item['classification']}` |"
        for item in evidence["temporal_transition_classification"]
    ]
    return "\n".join(
        [
            "# Time-ordered canonical check-in operational-evidence gap report",
            "",
            "Date: 2026-08-24",
            "",
            "Status: `frozen_evidence`",
            "",
            f"Result: `{evidence['result']}`",
            "",
            "Verdict: `one_incremental_provider_free_operational_rehearsal_justified`",
            "",
            "## Outcome",
            "",
            "The 30-scenario, 74-pair temporal composition adds useful precedence evidence but remains in-memory. Accepted route and database evidence already covers default denial, successful writes, source/freshness and signed-evidence rejection, idempotency stops, atomic rollback, unknown-response readback, and restricted-role tenant denial.",
            "",
            "Exactly two temporal transitions lack a database-backed route witness: current Receptionist authority revoked after proposal but before confirmation, and the selected waiting area becoming inactive in the same interval. One narrow provider-free database-backed default-off route rehearsal is justified for those two transitions. It is product assurance, not an ordinary-admission prerequisite, and it repeats neither attempt-008 unknown-response work nor the runtime-role/tenant attestation.",
            "",
            "## Transition classification",
            "",
            "| Transition | Physical evidence classification |",
            "|---|---|",
            *transition_lines,
            "",
            "## Admission and API boundary",
            "",
            "The accepted admission posture stays 11/0/1 with zero repository prerequisites and zero releases. Six external facts remain absent. The REST command remains confirmed, practice-scoped, idempotent and audited; GraphQL remains read-only, authoritative readback owns unknown responses, and events remain non-actuating.",
            "",
            "Five source hashes and five full Git bindings matched. No historical data, route, database, client, runtime, provider, model, Harness, network, product, deployment, Pages or protected-ref surface was opened.",
            "",
        ]
    )


def run_review(root: Path | None = None, *, release: bool = True) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract, root)
    evidence = build_evidence(contract, root)
    if release:
        (root / EVIDENCE_PATH).write_text(
            json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / REPORT_PATH).write_text(
            render_report(evidence), encoding="utf-8", newline="\n"
        )
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_review(args.repo_root, release=not args.no_write)
    except (
        ContractError,
        OSError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
