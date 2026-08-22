"""Read-only canonical check-in environment/secret-posture gap decomposition."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "raisa.check_in_environment_secret_posture_gap_decomposition_contract.v1"
EVIDENCE_SCHEMA_VERSION = "raisa.check_in_environment_secret_posture_gap_decomposition_evidence.v1"
PLAN_SOURCE = "878c3b4ef9790ff876e877f69653e74f16056948"
CONTRACT_RAW_SHA256 = "adad1642e1de628246eb7e39263a381f837139eb662baeefe8b2873a71b56bc2"
CONTRACT_SEMANTIC_SHA256 = "e3c1434344346da282a6fe6d3d32f43767d7e56b046a85abfcdf34dd6b547961"
CONTRACT_SCHEMA_SHA256 = "18f2b3f9698d2e2df2f78198cc889cd67e0a31597f498e773d343bfada8bdcda"
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
RESULT = "raisa_provider_free_read_only_check_in_environment_secret_posture_gap_decomposition_pass"
VERDICT = "not_ready_for_ordinary_practice_admission"
GAP_ID = "environment_manifest_and_operational_secret_posture"
TIMESTAMP = "2026-08-23T08:26:00.0000000+10:00"

BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-"
    "environment-manifest-operational-secret-posture-evidence-gap-decomposition"
)
CONTRACT_PATH = f"{BASE}/contract.json"
SCHEMA_PATH = f"{BASE}/contract.schema.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"

MATRIX_BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-"
    "ordinary-practice-admission-readiness-post-attempt-008-convergence-review"
)
ARCH_BASE = (
    "orchestration/continuity/raisa-provider-free-default-off-check-in-"
    "environment-manifest-secret-posture-architecture"
)

INPUT_BINDINGS = (
    (f"{MATRIX_BASE}/evidence.json", "d2b6836a84465555e47ce97d66b3dddc0f866251bbf7cf53b73908103d7d7c46"),
    (f"{MATRIX_BASE}/report.md", "c93ab33095fc5be81a6e14a3eeb26ee402edd498ef8c8bdc2e435fda6c851a54"),
    (
        "docs/raisa-provider-free-read-only-canonical-check-in-ordinary-practice-"
        "admission-readiness-post-attempt-008-convergence-review-closeout.md",
        "f0dfeebd7f5ecafdc6ad2d63484e6ff83d515e4216107f990677947f28a82236",
    ),
    (
        "orchestration/agent_inbox/codex/raisa-post-attempt-008-check-in-"
        "admission-readiness-convergence-review-sol-acceptance.md",
        "f0624b93eee19275365e7dd1b813ca318b8bb4c1c775803fe80cab68322806dd",
    ),
    (f"{ARCH_BASE}/contract.json", "e9aab3504520d955a0ce2c94c32a5f9a6ae25d7bbf129c7f2bd21951201c34d8"),
    (
        f"{ARCH_BASE}/environment-manifest.schema.json",
        "786cab3b19231c391d281cf36568b4206fe5f11b2a2ac51469f0996c3e718e88",
    ),
    (
        f"{ARCH_BASE}/provider-free-architecture-evidence.json",
        "0f1b762f28247e5c9033cf377716b21a625080344c5996ea743d90b66b1eb32b",
    ),
    (f"{ARCH_BASE}/architecture-report.md", "35f09c1118734d6b40ae267732a168343e2b76ebd9dd00fd901a7d891a831018"),
    (
        "docs/raisa-provider-free-default-off-check-in-environment-manifest-"
        "secret-posture-architecture-closeout.md",
        "0858486ff6cd173a6b3b397585e7b1ff74c578b341a8e34b8425e114e0520b5e",
    ),
    (
        "orchestration/agent_inbox/codex/raisa-check-in-environment-manifest-"
        "secret-posture-architecture-sol-acceptance.md",
        "ecac18824503953828d876eda863f40c419af5d5b92b0ef1fd180730452570ea",
    ),
)

GIT_OBJECTS = {
    "post_attempt_008_convergence_closeout_source": "ca18d64052241cd07bc1ac73887f849e2d245f98",
    "post_attempt_008_convergence_candidate": "5e9bf951f3712c48cac32f240d78b2cb685cc93c",
    "environment_architecture_candidate": "a1f309a6d52d01f9866432f7e9abb8095788d023",
    "environment_architecture_closeout_source": "455e41b8b9038813b290e67c43ce0b3190120988",
}

NODE_CLASSES = (
    "accepted_foundation",
    "repository_engineering_prerequisite",
    "external_operational_fact",
    "human_owned_external_decision",
)
EXPECTED_CLASS_COUNTS = {
    "accepted_foundation": 4,
    "repository_engineering_prerequisite": 5,
    "external_operational_fact": 6,
    "human_owned_external_decision": 5,
}
EXPECTED_STATUS = {
    "accepted_foundation": ("accepted", True),
    "repository_engineering_prerequisite": ("pending", True),
    "external_operational_fact": ("absent", False),
    "human_owned_external_decision": ("unselected", False),
}
EXTERNAL_FACTS = (
    "live_runtime_role_binding_and_attestation",
    "three_current_opaque_secret_bindings",
    "three_current_rotation_custody_attestations",
    "current_deny_only_break_glass_posture",
    "one_current_environment_manifest_instance",
    "operational_uniqueness_and_freshness_readback",
)
NEXT_OWNED_NODES = (
    "closed_manifest_normalizer",
    "typed_operational_evidence_inputs",
    "pure_environment_evidence_gate_evaluator",
)
CLOSED_BOUNDARIES = (
    "no_operational_manifest_instance_or_activation",
    "no_secret_value_reference_resolution_credential_store_or_environment_variable_access",
    "no_live_role_rotation_infrastructure_database_docker_postgresql_or_sql",
    "no_app_import_route_product_api_openapi_graphql_client_or_configuration_change",
    "no_ordinary_practice_enablement_admission_record_or_command_mounting",
    "no_action_grammar_generic_status_arrived_or_waiting_area_change",
    "no_product_patient_appointment_clinical_historical_or_protected_data",
    "no_native_harness_worker_gemini_provider_or_network",
    "no_production_deployment_release_pages_or_protected_ref_movement",
    "preserve_docs_branding_and_all_unrelated_untracked_files",
)


class ContractError(RuntimeError):
    """The frozen contract or source binding changed."""


class EvidenceError(RuntimeError):
    """The accepted sources do not support the frozen decomposition."""


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


def semantic_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git_object_is_ancestor(root: Path, object_id: str) -> bool:
    process = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return process.returncode == 0


def validate_contract(contract: dict[str, Any], root: Path, *, check_sources: bool = True) -> None:
    require(contract.get("schema_version") == SCHEMA_VERSION, "schema version changed")
    require(contract.get("planning_source") == PLAN_SOURCE, "planning source changed")
    require(contract.get("input_hash_mode") == HASH_MODE, "hash mode changed")
    require(semantic_sha256(contract) == CONTRACT_SEMANTIC_SHA256, "contract semantics changed")
    require(contract.get("accepted_git_objects") == GIT_OBJECTS, "Git bindings changed")
    require(tuple(contract.get("node_classes", [])) == NODE_CLASSES, "node classes changed")
    require(tuple(contract.get("closed_boundaries", [])) == CLOSED_BOUNDARIES, "boundaries changed")
    if check_sources:
        require(canonical_sha256(root, CONTRACT_PATH) == CONTRACT_RAW_SHA256, "contract bytes changed")
        require(canonical_sha256(root, SCHEMA_PATH) == CONTRACT_SCHEMA_SHA256, "contract schema changed")
    for label, object_id in {"planning_source": PLAN_SOURCE, **GIT_OBJECTS}.items():
        require(re.fullmatch(r"[0-9a-f]{40}", object_id) is not None, f"invalid Git object: {label}")
        if check_sources:
            require(git_object_is_ancestor(root, object_id), f"non-ancestor Git object: {label}")
    observed_inputs = tuple(
        (item.get("path"), item.get("sha256"))
        for item in contract.get("inputs", [])
        if isinstance(item, dict) and set(item) == {"path", "sha256"}
    )
    require(observed_inputs == INPUT_BINDINGS, "input bindings changed")
    if check_sources:
        for relative, digest in INPUT_BINDINGS:
            require(canonical_sha256(root, relative) == digest, f"source hash changed: {relative}")


def validate_graph(contract: dict[str, Any]) -> tuple[dict[str, int], int]:
    nodes = contract["nodes"]
    require(isinstance(nodes, list) and len(nodes) == 20, "node count changed")
    ids = [item.get("id") for item in nodes]
    require(len(ids) == len(set(ids)), "duplicate node ID")
    require([item.get("order") for item in nodes] == list(range(1, 21)), "node order changed")
    known = set(ids)
    edge_count = 0
    graph: dict[str, tuple[str, ...]] = {}
    for item in nodes:
        require(
            set(item)
            == {"order", "id", "class", "status", "depends_on", "completion_evidence", "repository_only"},
            f"node shape changed: {item.get('id')}",
        )
        node_class = item["class"]
        require(node_class in NODE_CLASSES, f"node class changed: {item['id']}")
        expected_status, expected_repository_only = EXPECTED_STATUS[node_class]
        require(item["status"] == expected_status, f"node status changed: {item['id']}")
        require(item["repository_only"] is expected_repository_only, f"repository boundary changed: {item['id']}")
        require(
            isinstance(item["completion_evidence"], str)
            and re.fullmatch(r"[a-z0-9_]+", item["completion_evidence"]) is not None,
            f"completion evidence changed: {item['id']}",
        )
        dependencies = tuple(item["depends_on"])
        require(len(dependencies) == len(set(dependencies)), f"duplicate dependency: {item['id']}")
        require(set(dependencies).issubset(known), f"unknown dependency: {item['id']}")
        require(item["id"] not in dependencies, f"self dependency: {item['id']}")
        graph[item["id"]] = dependencies
        edge_count += len(dependencies)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        require(node_id not in visiting, "dependency cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in graph[node_id]:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in ids:
        visit(node_id)
    counts = Counter(item["class"] for item in nodes)
    observed_counts = {name: counts.get(name, 0) for name in NODE_CLASSES}
    require(observed_counts == EXPECTED_CLASS_COUNTS, "class counts changed")
    return observed_counts, edge_count


def validate_sources(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    matrix = load_json(root, INPUT_BINDINGS[0][0])
    require(matrix.get("dimension_counts") == {"blocking_gap": 0, "operational_evidence_gap": 1, "satisfied": 11}, "readiness counts changed")
    require(matrix.get("operational_evidence_gaps") == [GAP_ID], "remaining gap changed")
    require(matrix.get("verdict") == VERDICT, "readiness verdict changed")
    require(
        next(item for item in matrix["dimensions"] if item["id"] == GAP_ID)["classification"]
        == "operational_evidence_gap",
        "dimension 11 classification changed",
    )
    require(all(value is False for value in matrix.get("closed_boundaries", {}).values()), "matrix boundary opened")

    architecture = load_json(root, INPUT_BINDINGS[4][0])
    posture = architecture.get("current_posture", {})
    for field in (
        "ordinary_admission_records_present",
        "environment_manifest_instances_present",
        "selected_practice_bindings_present",
        "ordinary_runtime_role_bindings_present",
        "secret_reference_bindings_present",
        "operational_evidence_artifacts_present",
    ):
        require(posture.get(field) == 0, f"architecture posture changed: {field}")
    require(posture.get("default_result") == "deny_environment_manifest_absent", "default denial changed")
    role = architecture.get("runtime_role_profile", {})
    require(role.get("logical_role_id") == "appointment_check_in_ordinary_runtime_v1", "logical role changed")
    require(role.get("non_owner_required") is True, "non-owner requirement changed")
    require(role.get("nobypassrls_required") is True, "NOBYPASSRLS requirement changed")
    require(role.get("role_attested") is False and role.get("database_connected") is False, "architecture overclaimed role")
    secret = architecture.get("secret_reference_profile", {})
    require(
        [item["slot_id"] for item in secret.get("ordered_slots", [])]
        == [
            "database_connection_credential",
            "application_token_signing_key",
            "admission_snapshot_verification_key",
        ],
        "secret slots changed",
    )
    require(secret.get("current_reference_count") == 0, "secret reference exists")
    rotation = architecture.get("rotation_evidence_profile", {})
    require(rotation.get("current_evidence_count") == 0, "rotation evidence exists")
    require(rotation.get("independent_verifier_required") is True, "independent verifier changed")
    break_glass = architecture.get("break_glass_profile", {})
    require(break_glass.get("mode") == "deny_only", "break-glass mode changed")
    require(break_glass.get("only_state_allowing_evidence_evaluation_to_continue") == "inactive", "break-glass continuation changed")
    evaluator = architecture.get("evidence_gate_evaluator", {})
    for field in (
        "may_admit_ordinary_practice",
        "may_execute_check_in",
        "may_connect_database",
        "may_resolve_secret",
        "may_create_or_change_role",
        "may_mutate_product_configuration",
    ):
        require(evaluator.get(field) is False, f"evaluator capability opened: {field}")
    operational = architecture.get("operational_evidence_boundary", {})
    require(operational.get("architecture_portion_frozen") is True, "architecture not frozen")
    require(operational.get("environment_and_secret_posture_operational_gap_closed") is False, "architecture claims gap closure")
    require(operational.get("this_contract_is_operational_evidence") is False, "contract became operational evidence")

    manifest_schema = load_json(root, INPUT_BINDINGS[5][0])
    require(manifest_schema.get("additionalProperties") is False, "manifest schema opened")
    require(manifest_schema.get("properties", {}).get("authority_git_object", {}).get("$ref") == "#/$defs/fullGitObject", "manifest Git binding changed")
    require(manifest_schema.get("$defs", {}).get("fullGitObject", {}).get("pattern") == "^[0-9a-f]{40}$", "full Git pattern changed")
    require(
        manifest_schema.get("properties", {}).get("break_glass", {}).get("properties", {}).get("mode", {}).get("const")
        == "deny_only",
        "manifest break-glass mode changed",
    )

    arch_evidence = load_json(root, INPUT_BINDINGS[6][0])
    require(arch_evidence.get("status") == "passed", "architecture evidence failed")
    for field in ("canonical_manifest_instance_count", "current_rotation_evidence_count", "current_secret_reference_count"):
        require(arch_evidence.get(field) == 0, f"architecture evidence population changed: {field}")
    require(arch_evidence.get("database_or_role_used") is False, "architecture used database or role")
    require(arch_evidence.get("secret_value_used") is False, "architecture used secret")

    closure = contract["gap_closure_rule"]
    require(closure["dimension_id"] == GAP_ID, "closure dimension changed")
    require(tuple(closure["required_external_fact_ids"]) == EXTERNAL_FACTS, "external facts changed")
    require(closure["all_required"] is True, "all-required rule changed")
    require(closure["repository_documentation_or_synthetic_substitution_allowed"] is False, "synthetic substitution opened")
    require(closure["this_tranche_closes_gap"] is False, "decomposition claimed closure")
    require(
        contract["readiness_result"]
        == {
            "satisfied": 11,
            "blocking_gap": 0,
            "operational_evidence_gap": 1,
            "verdict": VERDICT,
            "result": "gap_decomposed_not_satisfied",
        },
        "readiness result changed",
    )
    require(contract["human_attention"]["required_now"] is False, "premature human pause")
    require(tuple(contract["next_operation"]["owned_node_ids"]) == NEXT_OWNED_NODES, "next scope changed")
    require(contract["next_operation"]["product_admission_seam_in_scope"] is False, "product seam opened")
    require(contract["next_operation"]["external_fact_or_human_decision_in_scope"] is False, "external scope opened")
    require(contract["workflow_control"]["git_acceptance_source"] == "preflight_git_refs_snapshot_only", "Git evidence source changed")
    require(contract["workflow_control"]["new_git_summary_control_layer_added"] is False, "extra workflow layer added")
    return {
        "readiness_counts_retained": True,
        "sole_gap_retained": True,
        "architecture_population_zero": True,
        "reference_only_secret_slots_retained": True,
        "deny_only_break_glass_retained": True,
        "evaluator_has_no_admission_or_runtime_capability": True,
        "synthetic_substitution_for_operational_fact_denied": True,
        "human_decisions_unselected": True,
    }


def hostile_mutations(contract: dict[str, Any], root: Path) -> int:
    mutations: list[dict[str, Any]] = []
    for index in range(len(contract["inputs"])):
        for field, value in (
            ("path", "AGENTS.md"),
            ("sha256", "0" * 64),
        ):
            candidate = copy.deepcopy(contract)
            candidate["inputs"][index][field] = value
            mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        del candidate["inputs"][index]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["inputs"][index]["extra"] = True
        mutations.append(candidate)
    for label, object_id in contract["accepted_git_objects"].items():
        for value in (object_id[:7], "0" * 40):
            candidate = copy.deepcopy(contract)
            candidate["accepted_git_objects"][label] = value
            mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        del candidate["accepted_git_objects"][label]
        mutations.append(candidate)
    for index, node in enumerate(contract["nodes"]):
        for field, value in (
            ("id", f"{node['id']}_drift"),
            ("class", next(item for item in NODE_CLASSES if item != node["class"])),
            ("status", "accepted" if node["status"] != "accepted" else "pending"),
            ("repository_only", not node["repository_only"]),
        ):
            candidate = copy.deepcopy(contract)
            candidate["nodes"][index][field] = value
            mutations.append(candidate)
    for key, value in (
        ("schema_version", "mutated"),
        ("planning_source", PLAN_SOURCE[:7]),
        ("node_classes", ["free_form"]),
        ("gap_closure_rule", {}),
        ("readiness_result", {}),
        ("human_attention", {}),
        ("next_operation", {}),
        ("workflow_control", {}),
        ("closed_boundaries", []),
    ):
        candidate = copy.deepcopy(contract)
        candidate[key] = value
        mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["extra"] = True
    mutations.append(candidate)
    rejected = 0
    for candidate in mutations:
        try:
            validate_contract(candidate, root, check_sources=False)
        except (ContractError, KeyError, TypeError):
            rejected += 1
        else:
            raise EvidenceError("hostile contract mutation escaped")
    return rejected


def build_evidence(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract, root)
    node_counts, edge_count = validate_graph(contract)
    source_findings = validate_sources(root, contract)
    rejected = hostile_mutations(contract, root)
    require(rejected >= 128, "too few hostile mutations")
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": RESULT,
        "planning_source": PLAN_SOURCE,
        "accepted_git_objects": GIT_OBJECTS,
        "source_bindings": {path: digest for path, digest in INPUT_BINDINGS},
        "contract_sha256": CONTRACT_RAW_SHA256,
        "contract_schema_sha256": CONTRACT_SCHEMA_SHA256,
        "source_findings": source_findings,
        "node_counts": node_counts,
        "node_count": len(contract["nodes"]),
        "dependency_edge_count": edge_count,
        "required_external_fact_ids": list(EXTERNAL_FACTS),
        "next_owned_node_ids": list(NEXT_OWNED_NODES),
        "readiness_result": contract["readiness_result"],
        "human_attention": contract["human_attention"],
        "hostile_mutations_rejected": rejected,
        "closed_boundaries": {
            "operational_manifest_created": False,
            "secret_or_reference_resolved": False,
            "credential_store_or_environment_read": False,
            "database_role_or_infrastructure_used": False,
            "application_or_product_surface_opened": False,
            "ordinary_practice_enabled": False,
            "provider_worker_or_network_used": False,
            "protected_evidence_or_ref_opened": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    counts = evidence["node_counts"]
    return "\n".join(
        [
            "# Canonical check-in environment and secret-posture gap-decomposition report",
            "",
            "Date: 2026-08-23",
            "",
            f"Timestamp: {TIMESTAMP} (Australia/Brisbane)",
            "",
            "Status: `frozen_evidence`",
            "",
            f"Result: `{RESULT}`",
            "",
            f"Verdict: `{VERDICT}`",
            "",
            "## Outcome",
            "",
            "The sole remaining readiness gap is now decomposed, not closed. The accepted reading remains exactly 11 satisfied / 0 blocking / 1 operational-evidence gap. No repository artifact, authored-synthetic rehearsal, model statement or secret reference can substitute for the missing live operational facts.",
            "",
            "## Dependency reading",
            "",
            f"The closed graph contains {evidence['node_count']} nodes and {evidence['dependency_edge_count']} dependency edges: {counts['accepted_foundation']} accepted foundations, {counts['repository_engineering_prerequisite']} repository engineering prerequisites, {counts['external_operational_fact']} external operational facts and {counts['human_owned_external_decision']} human-owned external decisions.",
            "",
            "The next dependency-satisfied tranche owns only `closed_manifest_normalizer`, `typed_operational_evidence_inputs` and `pure_environment_evidence_gate_evaluator`. It remains provider-free, unmounted and reference-only. The product admission seam, external facts and human decisions remain out of scope.",
            "",
            "## Irreducible external boundary",
            "",
            "Gap closure later requires all six current external facts: a live role attestation, three opaque secret bindings, three fresh rotation/custody attestations, inactive deny-only break-glass evidence, one current environment manifest and uniqueness/freshness readback. The target environment/practice, custody system and owners, rotation/verifier policy, lasting provisioning, and eventual ordinary activation remain explicit human decisions.",
            "",
            "Human attention is not required now. It becomes mandatory immediately before an external selection or lasting action is required; dimension 11 can never itself authorize ordinary activation.",
            "",
            "## Deterministic and workflow evidence",
            "",
            f"All ten input hashes, five full Git bindings and {evidence['hostile_mutations_rejected']} hostile contract mutations passed. The graph is acyclic and every node uses the closed class/status vocabulary.",
            "",
            "The preflight Git snapshot, not an ad hoc PowerShell composite, owns acceptance readings for Git and worktree state. No additional Git-summary control layer was added.",
            "",
            "## Closed authority",
            "",
            "No operational manifest, secret/reference resolution, credential-store or environment read, role/database/infrastructure action, app import, route/API/client/configuration change, ordinary admission, product data, provider, deployment, Pages or protected-ref action occurred.",
            "",
        ]
    )


def verify_released(root: Path, evidence: dict[str, Any]) -> None:
    observed_evidence = load_json(root, EVIDENCE_PATH)
    require(observed_evidence == evidence, "released evidence changed")
    require(canonical_text(root, REPORT_PATH) == render_report(evidence), "released report changed")


def run_review(root: Path | None = None, *, verify_outputs: bool = False) -> dict[str, Any]:
    resolved_root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    evidence = build_evidence(resolved_root)
    if verify_outputs:
        verify_released(resolved_root, evidence)
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--verify-released", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_review(args.repo_root, verify_outputs=args.verify_released)
    except (ContractError, EvidenceError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
