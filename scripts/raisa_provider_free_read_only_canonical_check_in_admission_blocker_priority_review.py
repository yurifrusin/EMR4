"""Rank the accepted remaining canonical check-in admission dependencies."""

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
    "orchestration/continuity/raisa-provider-free-read-only-canonical-check-in-"
    "ordinary-practice-admission-blocker-priority-review"
)
CONTRACT_PATH = f"{BASE}/contract.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"
RESULT = (
    "raisa_provider_free_read_only_canonical_check_in_ordinary_practice_"
    "admission_blocker_priority_review_pass"
)
SCHEMA_VERSION = "raisa.check_in_admission_blocker_priority_contract.v1"
EVIDENCE_SCHEMA_VERSION = "raisa.check_in_admission_blocker_priority_evidence.v1"
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
RANKS = (
    "select_target_environment_and_practice_scope",
    "approve_operational_custody_rotation_and_break_glass_governance",
    "authorize_and_perform_live_evidence_provisioning",
    "perform_independent_uniqueness_and_freshness_readback",
    "confirm_ordinary_activation_separately",
)
EXTERNAL_FACT_IDS = (
    "live_runtime_role_binding_and_attestation",
    "three_current_opaque_secret_bindings",
    "three_current_rotation_custody_attestations",
    "current_deny_only_break_glass_posture",
    "one_current_environment_manifest_instance",
    "operational_uniqueness_and_freshness_readback",
)
HUMAN_CHOICE_IDS = (
    "select_target_environment_and_practice_scope",
    "approve_secret_custody_and_operational_owners",
    "approve_rotation_policy_and_independent_verifiers",
    "authorize_live_role_secret_and_manifest_provisioning",
    "confirm_ordinary_activation_separately",
)
NEXT_OPERATION = (
    "raisa-provider-free-read-only-canonical-check-in-operational-evidence-"
    "root-decision-brief"
)


class ContractError(RuntimeError):
    """The frozen contract or a bound accepted source changed."""


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


def current_head(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    ).stdout.strip()


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
            "expected_prior_readiness",
            "expected_current_readiness",
            "remaining_dimension",
            "repository_prerequisites_remaining",
            "external_fact_status",
            "human_choice_status",
            "ranked_groups",
            "next_operation",
            "terminal_after_next_operation",
            "minimum_hostile_mutations",
        },
        "contract keys changed",
    )
    require(contract["schema_version"] == SCHEMA_VERSION, "schema changed")
    require(contract["hash_mode"] == HASH_MODE, "hash mode changed")
    require(contract["expected_prior_readiness"] == "6_3_3", "prior reading changed")
    require(contract["expected_current_readiness"] == "11_0_1", "current reading changed")
    require(contract["repository_prerequisites_remaining"] == 0, "repository work reopened")
    require(contract["external_fact_status"] == "absent", "external fact promoted")
    require(contract["human_choice_status"] == "unselected", "human choice inferred")
    require(tuple(contract["ranked_groups"]) == RANKS, "ranking changed")
    require(contract["next_operation"] == NEXT_OPERATION, "successor changed")
    require(
        contract["terminal_after_next_operation"] == "pause_for_user_attention",
        "attention boundary changed",
    )
    sources = contract["accepted_sources"]
    require(isinstance(sources, list) and len(sources) == 5, "source count changed")
    require(len({item.get("id") for item in sources}) == 5, "source IDs duplicated")
    for item in sources:
        require(set(item) == {"id", "git_object", "path", "sha256"}, "source shape changed")
        require(re.fullmatch(r"[0-9a-f]{40}", item["git_object"]) is not None, "short Git object")
        require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, "invalid source hash")
        require(canonical_sha256(root, item["path"]) == item["sha256"], f"source changed: {item['path']}")
        if check_git:
            require(git_object_is_ancestor(root, item["git_object"]), f"non-ancestor source: {item['id']}")
    planning_source = contract["planning_source"]
    require(re.fullmatch(r"[0-9a-f]{40}", planning_source) is not None, "short planning source")
    if check_git:
        require(git_object_is_ancestor(root, planning_source), "planning source not ancestor")


def validate_accepted_evidence(contract: dict[str, Any], root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    sources = {item["id"]: item for item in contract["accepted_sources"]}
    original = canonical_text(root, sources["original_readiness_report"]["path"])
    require("Verdict: `not_ready_for_ordinary_practice_admission`" in original, "original verdict changed")
    require("Satisfied: 6; blocking gaps: 3; operational-evidence gaps: 3." in original, "original 6/3/3 changed")

    post = load_json(root, sources["post_evidence_seam_readiness"]["path"])
    require(post.get("verdict") == "not_ready_for_ordinary_practice_admission", "post-seam verdict changed")
    require(
        post.get("readiness")
        == {
            "satisfied": 11,
            "blocking_gap": 0,
            "operational_evidence_gap": 1,
            "remaining_dimension": "environment_manifest_and_operational_secret_posture",
            "changed_dimension_count": 0,
            "ordinary_admission_release_count": 0,
        },
        "post-seam 11/0/1 reading changed",
    )
    require(
        tuple(item.get("id") for item in post.get("external_facts", [])) == EXTERNAL_FACT_IDS
        and all(item.get("status") == "absent" for item in post["external_facts"]),
        "post-seam external facts changed",
    )
    require(
        tuple(item.get("id") for item in post.get("human_owned_decisions", [])) == HUMAN_CHOICE_IDS
        and all(item.get("status") == "unselected" for item in post["human_owned_decisions"]),
        "post-seam human decisions changed",
    )

    packet = load_json(root, sources["reference_only_conformance_evidence"]["path"])
    require(
        packet.get("readiness")
        == {
            "blocking_gap": 0,
            "operational_evidence_gap": 1,
            "repository_prerequisites_remaining": 0,
            "satisfied": 11,
            "verdict": "not_ready_for_ordinary_practice_admission",
        },
        "reference packet readiness changed",
    )
    require(packet.get("counts", {}).get("external_facts_established") == 0, "packet established external fact")
    require(packet.get("counts", {}).get("human_choices_selected") == 0, "packet selected human choice")
    require(packet.get("counts", {}).get("ordinary_admission_releases") == 0, "packet released ordinary admission")
    require(
        tuple(item.get("id") for item in packet.get("external_facts", [])) == EXTERNAL_FACT_IDS
        and all(item.get("status") == "absent" for item in packet["external_facts"]),
        "packet external facts changed",
    )
    require(
        tuple(item.get("id") for item in packet.get("human_choices", [])) == HUMAN_CHOICE_IDS
        and all(item.get("status") == "unselected" for item in packet["human_choices"]),
        "packet human choices changed",
    )
    closeout = canonical_text(root, sources["reference_only_conformance_closeout"]["path"])
    acceptance = canonical_text(root, sources["reference_only_conformance_acceptance"]["path"])
    for text in (closeout, acceptance):
        prose = " ".join(text.split())
        require("11 satisfied" in prose, "accepted 11/0/1 prose changed")
        require("zero blocking" in prose or "0 blocking" in prose, "accepted zero-blocking prose changed")
        require("one operational-evidence gap" in prose or "1 operational" in prose, "accepted remaining-gap prose changed")
        require("zero repository prerequisites remaining" in prose or "last repository-only" in prose, "accepted repository-complete prose changed")
    return post, packet


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
    for index in range(5):
        candidate = copy.deepcopy(contract)
        candidate["ranked_groups"][index] += "_drift"
        candidates.append(candidate)
        candidate = copy.deepcopy(contract)
        del candidate["ranked_groups"][index]
        candidates.append(candidate)
    for key, value in (
        ("expected_prior_readiness", "11_0_1"),
        ("expected_current_readiness", "12_0_0"),
        ("repository_prerequisites_remaining", 1),
        ("external_fact_status", "present"),
        ("human_choice_status", "selected"),
        ("next_operation", "activation"),
        ("terminal_after_next_operation", "continue"),
        ("planning_source", contract["planning_source"][:7]),
        ("hash_mode", "ambient"),
    ):
        candidate = copy.deepcopy(contract)
        candidate[key] = value
        candidates.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["extra"] = True
    candidates.append(candidate)

    rejected = 0
    for candidate in candidates:
        try:
            validate_contract(candidate, root, check_git=False)
        except (ContractError, OSError, KeyError, TypeError):
            rejected += 1
        else:
            raise ContractError("hostile contract mutation escaped")
    require(rejected >= contract["minimum_hostile_mutations"], "hostile matrix too small")
    return rejected


def build_evidence(contract: dict[str, Any], root: Path) -> dict[str, Any]:
    post, packet = validate_accepted_evidence(contract, root)
    rejected = hostile_mutations(contract, root)
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operation_id": contract["operation_id"],
        "result": RESULT,
        "candidate_source": current_head(root),
        "source_bindings": contract["accepted_sources"],
        "readiness_reconciliation": {
            "original": {"satisfied": 6, "blocking_gap": 3, "operational_evidence_gap": 3},
            "current": {"satisfied": 11, "blocking_gap": 0, "operational_evidence_gap": 1},
            "remaining_dimension": contract["remaining_dimension"],
            "repository_prerequisites_remaining": 0,
            "verdict": post["verdict"],
            "ordinary_admission_releases": packet["counts"]["ordinary_admission_releases"],
        },
        "external_facts": post["external_facts"],
        "human_choices": post["human_owned_decisions"],
        "ranked_groups": [
            {"rank": 1, "id": RANKS[0], "depends_on": [], "kind": "human_root_decision"},
            {"rank": 2, "id": RANKS[1], "depends_on": [RANKS[0]], "kind": "human_governance_decisions"},
            {"rank": 3, "id": RANKS[2], "depends_on": [RANKS[0], RANKS[1]], "kind": "external_operational_work"},
            {"rank": 4, "id": RANKS[3], "depends_on": [RANKS[2]], "kind": "independent_operational_evidence"},
            {"rank": 5, "id": RANKS[4], "depends_on": [RANKS[3]], "kind": "separate_lasting_impact_confirmation"},
        ],
        "next_operation": {
            "operation_id": NEXT_OPERATION,
            "kind": "provider_free_read_only_decision_brief",
            "asks_only_root_decision": True,
            "creates_control_layer": False,
            "user_attention_required_after_closeout": True,
        },
        "parallelism": {
            "deepseek": "declined_negative_no_work_package",
            "gemini": "declined_neutral_closed_deterministic_evidence",
            "native_subagents": "declined_negative_serial_policy",
            "serial_owner": "gpt_sol",
        },
        "verification": {
            "source_hashes_matched": 5,
            "full_git_bindings_matched": 5,
            "hostile_mutations_rejected": rejected,
            "external_facts_inferred": 0,
            "human_choices_inferred": 0,
        },
        "closed_boundaries": {
            "provider_or_harness_called": False,
            "environment_credential_secret_or_network_accessed": False,
            "database_or_infrastructure_accessed": False,
            "product_source_route_api_client_configuration_or_runtime_changed": False,
            "ordinary_practice_enabled": False,
            "product_or_protected_data_used": False,
            "deployment_release_pages_or_protected_ref_changed": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    lines = [
        "# Canonical check-in admission blocker-priority report",
        "",
        "Date: 2026-08-23",
        "",
        f"Result: `{evidence['result']}`",
        "",
        "Verdict: `repository_work_exhausted_root_user_decision_required`",
        "",
        "## Outcome",
        "",
        "The original 6/3/3 readiness posture has converged through accepted descendants to 11/0/1. No design blocker and no repository engineering prerequisite remains. The sole gap is live environment, role, opaque-reference custody, rotation, break-glass, manifest and independent freshness evidence.",
        "",
        "Another implementation tranche would add ceremony without closing that gap. The only useful provider-free successor is a concise root-decision brief; after it, the workflow must pause for Yuri to choose whether to commence operational evidence acquisition and, if so, the target environment and practice scope.",
        "",
        "## Dependency order",
        "",
        "| Rank | Gate | Kind | Depends on |",
        "|---:|---|---|---|",
    ]
    for item in evidence["ranked_groups"]:
        dependencies = ", ".join(f"`{value}`" for value in item["depends_on"]) or "none"
        lines.append(f"| {item['rank']} | `{item['id']}` | `{item['kind']}` | {dependencies} |")
    lines.extend(
        [
            "",
            "## Preserved denial",
            "",
            "All six external facts remain absent, all five human choices remain unselected, and ordinary admission releases remain zero. Activation stays a separate final confirmation after independent readback.",
            "",
            "Five source hashes and five full Git bindings matched. No worker, Harness, provider, environment, credential, secret, network, database, infrastructure, product, runtime, deployment, Pages or protected-ref surface was opened.",
            "",
        ]
    )
    return "\n".join(lines)


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
        (root / REPORT_PATH).write_text(render_report(evidence), encoding="utf-8", newline="\n")
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_review(args.repo_root, release=not args.no_write)
    except (ContractError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
