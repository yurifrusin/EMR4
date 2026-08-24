"""Typed read-only utility review for one sanitised historical-derived check-in test."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "raisa.historical_derived_check_in_adapter_test_utility_gap_review_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "raisa.historical_derived_check_in_adapter_test_utility_gap_review_evidence.v1"
)
SUCCESSOR_SCHEMA_VERSION = (
    "raisa.authored_synthetic_time_ordered_check_in_context_axis_contract.v1"
)
PLANNING_SOURCE = "84ab32ccf2e309be532649d4526bea5d85556535"
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
DECISION = "accepted_read_only_utility_gap_review"
REVIEW_TIMESTAMP = "2026-08-24T15:12:00.0000000+10:00"
UTILITY_LABELS = (
    "digest_only_provenance",
    "synthetic_time_parameter_only",
    "independent_behavior_selector",
)
COVERAGE_LABELS = (
    "historical_derived_incremental_coverage",
    "already_covered_product_contract",
)

BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-historical-derived-"
    "check-in-context-adapter-test-utility-gap-review"
)
CONTRACT_PATH = f"{BASE}/contract.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"
SUCCESSOR_PATH = f"{BASE}/authored-synthetic-successor-axis-contract.json"

PARENT_BASE = (
    "orchestration/continuity/raisa-provider-free-exact-digest-historical-derived-"
    "minimised-check-in-context-adapter-test-consumption-rehearsal"
)
OCCUPIED_RESULT = f"{PARENT_BASE}/occupied-result.json"
EFFICACY = f"{PARENT_BASE}/efficacy-reading.json"
PARENT_SUCCESSOR = f"{PARENT_BASE}/next-tranche-contract.json"
CONSUMPTION_SOURCE = (
    "orchestration_harness/historical_diary_check_in_adapter_test_consumption.py"
)
CONSUMPTION_TEST = (
    "tests/test_raisa_provider_free_exact_digest_historical_derived_minimised_"
    "check_in_context_adapter_test_consumption_rehearsal.py"
)
ADAPTER_SOURCE = "app/services/appointment_check_in_product_adapter.py"
ADAPTER_TEST = "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py"
ROUTE_TEST = (
    "tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_"
    "convergence.py"
)
PLAN = (
    "docs/raisa-provider-free-read-only-historical-derived-check-in-context-"
    "adapter-test-utility-gap-review-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-historical-derived-check-in-context-"
    "adapter-test-utility-gap-review-threat-model-delta.md"
)

INPUT_PATHS = (
    OCCUPIED_RESULT,
    EFFICACY,
    PARENT_SUCCESSOR,
    CONSUMPTION_SOURCE,
    CONSUMPTION_TEST,
    ADAPTER_SOURCE,
    ADAPTER_TEST,
    ROUTE_TEST,
    PLAN,
    THREAT,
)
GIT_OBJECTS = {
    "occupied_candidate": "517fda26c5c7f46397acc91976bc97b0be3778ef",
    "sanitised_closeout": "6a1de186f096636402d50a89feae6a81953cd862",
    "accepted_adapter": "c82c3a741053a9c8da260aa62e1a968af22bb54e",
}
STRUCTURAL_AXES = (
    ("event_count", 6, "digest_only_provenance"),
    ("distinct_relative_minutes", 4, "digest_only_provenance"),
    ("relative_minute_span", 19, "synthetic_time_parameter_only"),
    ("distinct_event_kinds", 2, "digest_only_provenance"),
    ("synthetic_subject_slots", 1, "digest_only_provenance"),
    ("resource_slots", 1, "digest_only_provenance"),
)
OCCUPIED_BRANCH = {
    "source_status": "Booked",
    "waiting_area_mode": "none",
    "authority": "active_same_practice_receptionist",
    "freshness_and_evidence": "valid",
    "idempotency": "started",
    "transaction": "commit_and_readback_success",
    "expected_coverage": "already_covered_product_contract",
}
SUCCESSOR_AXES = (
    (
        "source_and_waiting_area_transition",
        (
            "eligible_none",
            "eligible_assign_valid",
            "eligible_preserve_valid",
            "intervening_state_change_rejected",
            "intervening_area_topology_change_rejected",
        ),
    ),
    (
        "authority_evidence_and_freshness_transition",
        (
            "unchanged_valid",
            "actor_revoked",
            "evidence_invalidated",
            "proposal_stale_after_intervening_update",
        ),
    ),
    (
        "idempotency_and_outcome_transition",
        (
            "first_execution",
            "exact_replay",
            "conflict_or_in_progress",
            "precommit_failure",
            "commit_outcome_unknown",
            "committed_readback_unavailable",
        ),
    ),
)
CLOSED_BOUNDARIES = (
    "no_local_data_fixture_control_or_archive_access",
    "no_provider_model_network_or_external_release",
    "no_product_database_route_client_runtime_or_configuration_change",
    "no_ordinary_practice_activation_or_product_validity_claim",
    "no_production_deployment_release_pages_or_protected_ref_movement",
    "preserve_docs_branding_and_all_unrelated_untracked_files",
)


class ReviewError(RuntimeError):
    """Frozen review contract or exact evidence changed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def canonical_text(root: Path, relative: str) -> str:
    require(relative in INPUT_PATHS or relative == CONTRACT_PATH, "path not allowlisted")
    require("local_data" not in relative.lower(), "local_data path forbidden")
    root = root.resolve()
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "path escapes repository")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReviewError(f"non-UTF-8 input: {relative}") from exc
    require("\r" not in text.replace("\r\n", ""), f"bare CR input: {relative}")
    return text.replace("\r\n", "\n")


def canonical_sha256(root: Path, relative: str) -> str:
    return hashlib.sha256(canonical_text(root, relative).encode("utf-8")).hexdigest()


def load_json(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads(canonical_text(root, relative))
    require(isinstance(value, dict), f"JSON object required: {relative}")
    return value


def git_object_is_ancestor(root: Path, object_id: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _axis_projection(value: object) -> tuple[tuple[str, int, str], ...]:
    require(isinstance(value, list), "structural axes must be a list")
    return tuple(
        (item.get("id"), item.get("value"), item.get("expected_utility"))
        for item in value
        if isinstance(item, dict)
    )


def _successor_projection(value: object) -> tuple[tuple[str, tuple[str, ...]], ...]:
    require(isinstance(value, list), "successor axes must be a list")
    return tuple(
        (item.get("id"), tuple(item.get("values", [])))
        for item in value
        if isinstance(item, dict)
    )


def validate_contract(
    contract: dict[str, Any], root: Path, *, check_git: bool = True
) -> None:
    require(
        set(contract)
        == {
            "schema_version",
            "planning_source",
            "input_hash_mode",
            "accepted_git_objects",
            "inputs",
            "utility_labels",
            "coverage_labels",
            "structural_axes",
            "occupied_branch",
            "successor_axis_families",
            "acceptance",
            "closed_boundaries",
        },
        "top-level keys changed",
    )
    require(contract["schema_version"] == SCHEMA_VERSION, "schema version changed")
    require(contract["planning_source"] == PLANNING_SOURCE, "planning source changed")
    require(contract["input_hash_mode"] == HASH_MODE, "hash mode changed")
    require(contract["accepted_git_objects"] == GIT_OBJECTS, "Git objects changed")
    for label, object_id in {
        "planning_source": contract["planning_source"],
        **contract["accepted_git_objects"],
    }.items():
        require(re.fullmatch(r"[0-9a-f]{40}", object_id) is not None, f"bad Git ID: {label}")
        if check_git:
            require(git_object_is_ancestor(root, object_id), f"non-ancestor Git ID: {label}")

    inputs = contract["inputs"]
    require(isinstance(inputs, list), "inputs must be a list")
    require(tuple(item.get("path") for item in inputs) == INPUT_PATHS, "input paths changed")
    for item in inputs:
        require(set(item) == {"path", "sha256"}, "input shape changed")
        require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, "bad SHA-256")
        require(canonical_sha256(root, item["path"]) == item["sha256"], f"hash changed: {item['path']}")

    require(tuple(contract["utility_labels"]) == UTILITY_LABELS, "utility labels changed")
    require(tuple(contract["coverage_labels"]) == COVERAGE_LABELS, "coverage labels changed")
    require(_axis_projection(contract["structural_axes"]) == STRUCTURAL_AXES, "structural axes changed")
    require(contract["occupied_branch"] == OCCUPIED_BRANCH, "occupied branch changed")
    require(
        _successor_projection(contract["successor_axis_families"]) == SUCCESSOR_AXES,
        "successor axes changed",
    )
    require(
        contract["acceptance"]
        == {
            "expected_decision": DECISION,
            "expected_historical_derived_incremental_branch_count": 0,
            "expected_new_business_rule_count": 0,
            "maximum_successor_axis_family_count": 3,
            "minimum_hostile_contract_mutations": 60,
        },
        "acceptance changed",
    )
    require(tuple(contract["closed_boundaries"]) == CLOSED_BOUNDARIES, "boundaries changed")


def _function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    node = next(
        (item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == name),
        None,
    )
    require(isinstance(node, ast.FunctionDef), f"function missing: {name}")
    return node


def _tuple_assignment_count(tree: ast.Module, name: str) -> int:
    for item in tree.body:
        if isinstance(item, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in item.targets
        ):
            require(isinstance(item.value, ast.Tuple), f"{name} is not a tuple")
            return len(item.value.elts)
    raise ReviewError(f"tuple missing: {name}")


def validate_sources(root: Path, texts: dict[str, str]) -> dict[str, Any]:
    occupied = json.loads(texts[OCCUPIED_RESULT])
    efficacy = json.loads(texts[EFFICACY])
    parent = json.loads(texts[PARENT_SUCCESSOR])
    require(occupied.get("reason_codes") == [], "occupied result has reasons")
    require(occupied.get("decision") == "consumed_for_exact_declared_local_adapter_test_only", "occupied decision changed")
    require(occupied.get("structural_utility") == {axis: value for axis, value, _ in STRUCTURAL_AXES}, "structural utility changed")
    require(occupied.get("adapter_test", {}).get("invocations") == 1, "adapter invocation changed")
    require(occupied["adapter_test"].get("status_before") == "Booked", "source status changed")
    require(occupied["adapter_test"].get("waiting_area_preserved_none") is True, "waiting-area branch changed")
    require(occupied.get("privacy", {}).get("fixture_rows_persisted") is False, "fixture rows persisted")
    require(occupied.get("privacy", {}).get("structural_slot_values_persisted") is False, "slot values persisted")
    require(occupied.get("authority", {}).get("provider_or_model_calls") == 0, "provider call recorded")
    require(efficacy.get("decision") == "effective_traceable_consumption_with_narrow_behavioral_utility", "efficacy decision changed")
    require(efficacy.get("behavioral_utility", {}).get("new_check_in_business_rule_discovered") is False, "new rule unexpectedly claimed")
    require(efficacy["behavioral_utility"].get("event_kinds_individual_minutes_and_slots_created_distinct_adapter_branches") is False, "distinct branches unexpectedly claimed")
    require(parent.get("operation_id") == "raisa-provider-free-read-only-historical-derived-check-in-context-adapter-test-utility-gap-review", "parent successor changed")
    require(parent.get("review_inputs", {}).get("local_data_path_access") is False, "local data authorized")

    consumption_tree = ast.parse(texts[CONSUMPTION_SOURCE])
    run_node = _function_node(consumption_tree, "_run_adapter_once")
    utility_keys = {
        node.slice.value
        for node in ast.walk(run_node)
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "utility"
        and isinstance(node.slice, ast.Constant)
        and isinstance(node.slice.value, str)
    }
    require(utility_keys == {"relative_minute_span"}, "independent utility selectors changed")
    compose_calls = sum(
        1
        for node in ast.walk(run_node)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "compose_product_check_in"
    )
    require(compose_calls == 1, "adapter call count changed")
    source = texts[CONSUMPTION_SOURCE]
    for marker in (
        'uuid5(SYNTHETIC_NAMESPACE, f"{structural_digest}:practice")',
        'f"{structural_digest}:actor"',
        'f"{structural_digest}:appointment"',
        'f"{structural_digest}:idempotency"',
        'f"{structural_digest}:evidence"',
        "status=AppointmentStatus.Booked",
        "waiting_area_id=None",
        "minutes=minute_span",
    ):
        require(marker in source, f"consumption marker missing: {marker}")

    adapter = texts[ADAPTER_SOURCE]
    for marker in (
        "CHECK_IN_SOURCE_STATUSES = {AppointmentStatus.Booked, AppointmentStatus.Confirmed}",
        'return "already_arrived"',
        'return "invalid_source_status"',
        'return "waiting_area_move_not_supported", None',
        'return _stop("stale_check_in_proposal_freshness_id", outcome="stale_precondition")',
        'return _stop("current_authority_revoked", outcome="authority_revoked")',
        '"commit_outcome_unknown"',
        '"committed_readback_unavailable"',
    ):
        require(marker in adapter, f"adapter marker missing: {marker}")

    adapter_test_tree = ast.parse(texts[ADAPTER_TEST])
    hostile_count = _tuple_assignment_count(adapter_test_tree, "HOSTILE_MUTATIONS")
    require(hostile_count >= 60, "accepted hostile matrix narrowed")
    adapter_test = texts[ADAPTER_TEST]
    for marker in (
        '@pytest.mark.parametrize("status", [AppointmentStatus.Booked, AppointmentStatus.Confirmed])',
        '@pytest.mark.parametrize("area_mode", ["none", "assign", "preserve"])',
        "test_same_key_replay_returns_exact_stored_result_before_lock_or_effect",
        "test_injected_failures_never_release_a_false_success",
    ):
        require(marker in adapter_test, f"adapter-test marker missing: {marker}")
    route_test = texts[ROUTE_TEST]
    require("test_route_delegates_once_after_the_unchanged_default_off_gate" in route_test, "route default-off marker missing")
    require("test_internal_adapter_stops_never_downgrade_to_a_false_client_success" in route_test, "route stop marker missing")

    return {
        "canonical_digest_influences": [
            "synthetic_practice_actor_appointment_command_audit_event_ids",
            "synthetic_idempotency_material",
            "synthetic_evidence_material",
        ],
        "direct_structural_selector_keys": ["relative_minute_span"],
        "adapter_invocations": 1,
        "existing_adapter_success_matrix_cases": 6,
        "existing_hostile_contract_mutations": hostile_count,
    }


def hostile_mutations(contract: dict[str, Any], root: Path) -> int:
    mutations: list[dict[str, Any]] = []
    for index in range(len(contract["inputs"])):
        candidate = copy.deepcopy(contract)
        del candidate["inputs"][index]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["inputs"][index]["path"] = "AGENTS.md"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        digest = candidate["inputs"][index]["sha256"]
        candidate["inputs"][index]["sha256"] = ("0" if digest[0] != "0" else "1") + digest[1:]
        mutations.append(candidate)
    for label, object_id in contract["accepted_git_objects"].items():
        candidate = copy.deepcopy(contract)
        candidate["accepted_git_objects"][label] = object_id[:7]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["accepted_git_objects"][label] = "0" * 40
        mutations.append(candidate)
    for index, axis in enumerate(contract["structural_axes"]):
        for key, value in (
            ("id", axis["id"] + "_drift"),
            ("value", axis["value"] + 1),
            ("expected_utility", "independent_behavior_selector"),
        ):
            candidate = copy.deepcopy(contract)
            candidate["structural_axes"][index][key] = value
            mutations.append(candidate)
    for index, axis in enumerate(contract["successor_axis_families"]):
        candidate = copy.deepcopy(contract)
        candidate["successor_axis_families"][index]["id"] += "_drift"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["successor_axis_families"][index]["values"] = []
        mutations.append(candidate)
    for key, value in (
        ("schema_version", "mutated"),
        ("planning_source", PLANNING_SOURCE[:7]),
        ("input_hash_mode", "mutated"),
        ("utility_labels", []),
        ("coverage_labels", []),
        ("occupied_branch", {}),
        ("acceptance", {}),
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
            validate_contract(candidate, root, check_git=False)
        except (ReviewError, OSError, KeyError, TypeError):
            rejected += 1
        else:
            raise ReviewError("hostile contract mutation escaped")
    return rejected


def build_successor(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SUCCESSOR_SCHEMA_VERSION,
        "status": "frozen_authored_synthetic_axes_no_execution_authority",
        "recorded_at": REVIEW_TIMESTAMP,
        "operation_id": (
            "raisa-provider-free-authored-synthetic-time-ordered-canonical-check-"
            "in-context-branch-composition-rehearsal"
        ),
        "source_review": PLANNING_SOURCE,
        "basis": {
            "historical_derived_incremental_branch_count": 0,
            "new_business_rule_count": 0,
            "digest_only_provenance_is_not_behavioral_coverage": True,
        },
        "axis_families": contract["successor_axis_families"],
        "composition_rule": {
            "strategy": "minimal_pairwise_time_ordered_authored_synthetic_scenarios",
            "full_cross_product_required": False,
            "requires_declared_initial_state_intervening_change_expected_adapter_outcome_and_readback": True,
        },
        "authority": {
            "authored_synthetic_only": True,
            "historical_fixture_control_archive_or_local_data_access": False,
            "product_adapter_route_database_client_runtime_or_configuration_change": False,
            "provider_model_network_or_external_release": False,
            "ordinary_practice_activation": False,
            "execution_authorized_by_this_contract": False,
        },
        "claim_ceiling": (
            "minimum_authored_synthetic_time_ordered_scenario_axes_only_no_claim_"
            "that_axes_occurred_historically_or_establish_product_truth"
        ),
    }


def build_evidence(
    contract: dict[str, Any], source_reading: dict[str, Any], rejected: int
) -> dict[str, Any]:
    require(rejected >= contract["acceptance"]["minimum_hostile_contract_mutations"], "too few hostile mutations")
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "decision": DECISION,
        "recorded_at": REVIEW_TIMESTAMP,
        "planning_source": PLANNING_SOURCE,
        "accepted_git_objects": GIT_OBJECTS,
        "source_bindings": {item["path"]: item["sha256"] for item in contract["inputs"]},
        "structural_influence": [
            {"id": axis, "value": value, "utility": utility}
            for axis, value, utility in STRUCTURAL_AXES
        ],
        "source_reading": source_reading,
        "coverage": {
            "occupied_branch": OCCUPIED_BRANCH,
            "historical_derived_incremental_branch_count": 0,
            "new_business_rule_count": 0,
            "existing_product_contract_coverage": [
                "booked_and_confirmed_success",
                "none_assign_and_preserve_waiting_area_success",
                "exact_replay_and_idempotency_stops",
                "authority_evidence_and_freshness_rejection",
                "precommit_failure_commit_unknown_and_readback_unknown",
                "default_off_route_delegation_and_fail_closed_response_mapping",
            ],
        },
        "utility_gap": (
            "no_time_ordered_context_change_selected_a_distinct_adapter_outcome"
        ),
        "successor_axis_family_count": len(SUCCESSOR_AXES),
        "hostile_contract_mutations_rejected": rejected,
        "closed_boundaries": {
            "local_data_accessed": False,
            "fixture_control_or_archive_accessed": False,
            "provider_model_or_network_used": False,
            "product_or_runtime_changed": False,
            "ordinary_practice_activated": False,
            "protected_ref_moved": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    lines = [
        "# Historical-derived check-in adapter-test utility gap review",
        "",
        "Date: 2026-08-24",
        "",
        f"Timestamp: {REVIEW_TIMESTAMP} (Australia/Brisbane)",
        "",
        f"Decision: `{evidence['decision']}`",
        "",
        "## Conclusion",
        "",
        "The trove-derived candidate supplied traceable provenance to one adapter test, but added zero incremental adapter branches and discovered zero new check-in business rules. Its canonical digest determined one-way synthetic identities, idempotency material and evidence material. Its nineteen-minute span shifted the injected synthetic clock. No event count, minute count, event-kind count or slot count independently changed the appointment state, authority, waiting-area, evidence, idempotency, transaction or readback branch.",
        "",
        "The occupied path was the already-covered `Booked`, no-waiting-area success. The accepted product suite already covers `Booked` and `Confirmed`, none/assign/preserve waiting areas, exact replay, fail-closed authority/evidence/freshness/idempotency paths and precommit/unknown-outcome failures.",
        "",
        "## Structural influence reading",
        "",
        "| Structural measurement | Value | Utility |",
        "|---|---:|---|",
    ]
    for item in evidence["structural_influence"]:
        lines.append(f"| `{item['id']}` | {item['value']} | `{item['utility']}` |")
    lines.extend(
        [
            "",
            "## Honest gap",
            "",
            "The missing utility is time-ordered composition: an initial synthetic context, an intervening state/authority/area/idempotency or transaction change, and the resulting adapter stop, replay, success or outcome-unknown reading. Repeating more isolated atomic branches would mostly duplicate existing coverage.",
            "",
            "The successor is therefore limited to three authored-synthetic axis families and may use a minimal pairwise set. The contract does not claim those axes occurred in the historical trove and authorises no further historical access or execution by itself.",
            "",
            "## Deterministic boundary",
            "",
            f"Rejected {evidence['hostile_contract_mutations_rejected']} hostile contract mutations with zero escape. Only ten exact tracked inputs were admitted. No `local_data`, fixture control, archive, provider, model, network, product runtime, database, route invocation or ordinary-practice surface was opened.",
            "",
        ]
    )
    return "\n".join(lines)


def run_review(root: Path | None = None, *, release: bool = True) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract, root)
    texts = {item["path"]: canonical_text(root, item["path"]) for item in contract["inputs"]}
    source_reading = validate_sources(root, texts)
    rejected = hostile_mutations(contract, root)
    evidence = build_evidence(contract, source_reading, rejected)
    successor = build_successor(contract)
    if release:
        (root / EVIDENCE_PATH).write_text(
            json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / SUCCESSOR_PATH).write_text(
            json.dumps(successor, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / REPORT_PATH).write_text(
            render_report(evidence), encoding="utf-8", newline="\n"
        )
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_review(args.repo_root, release=not args.no_write)
    except (ReviewError, OSError, json.JSONDecodeError, SyntaxError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
