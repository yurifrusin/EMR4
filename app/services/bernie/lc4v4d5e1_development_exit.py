"""LC4V4D5E1 development-only exit reassessment.

This binder validates committed D4, D5, and D5R1 reports without executing the
parser or discovering fixtures. It authorizes no certification or runtime
behavior.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import pathlib
from typing import Any

from app.services.bernie.composed_corpus_evaluator import PolicyVersion, compose_versioned


SCHEMA_VERSION = "lc4v4d5e1.development_exit.v1"
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
D4_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d4-composed-integration.json"
D5_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d5-option-a-adoption-audit.json"
D5R1_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d5r1-exact-four-remediation.json"
D5R1_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "orchestration" / "agent_inbox" / "codex"
    / "lc4v4d5r1-sol-acceptance.md"
)

EXPECTED_D4_HASH = "sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653"
EXPECTED_D5_HASH = "sha256:e2c461ee3b1821c94574b33693efa88d21b99ecf9a95b1ac723b24a933c50564"
EXPECTED_D5R1_HASH = "sha256:0cb444d1aeba82a80f5a16170b30b8ea203842dec4af81b768a688e5aae9bcdf"
EXPECTED_LEGACY_60_HASH = "sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27"
EXPECTED_EMPTY_BLOCKER_HASH = "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"


def _payload_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _read_report(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _hash_valid(payload: dict[str, Any] | None, expected_hash: str) -> bool:
    if payload is None:
        return False
    canonical = dict(payload)
    embedded = canonical.pop("report_hash", None)
    canonical.pop("decision", None)
    return embedded == expected_hash and _payload_hash(canonical) == expected_hash


def _all_gates(payload: dict[str, Any] | None, expected_count: int) -> bool:
    if payload is None or not isinstance(payload.get("gates"), dict):
        return False
    gates = payload["gates"]
    return len(gates) == expected_count and all(value is True for value in gates.values())


def run_d5e1_exit(
    source_commit: str = "unknown",
    *,
    d4_path: pathlib.Path = D4_PATH,
    d5_path: pathlib.Path = D5_PATH,
    d5r1_path: pathlib.Path = D5R1_PATH,
    acceptance_path: pathlib.Path = D5R1_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Bind immutable development evidence and fail closed on any drift."""
    d4 = _read_report(d4_path)
    d5 = _read_report(d5_path)
    d5r1 = _read_report(d5r1_path)
    try:
        acceptance = acceptance_path.read_text(encoding="utf-8")
    except OSError:
        acceptance = ""

    d4_counts = d4.get("category_counts", {}) if d4 else {}
    d5_counts = d5.get("classification_counts", {}) if d5 else {}
    d5r1_counts = d5r1.get("classification_counts", {}) if d5r1 else {}

    default_policy = inspect.signature(compose_versioned).parameters[
        "policy_version"
    ].default

    gates: dict[str, bool] = {
        "d4_hash_valid": _hash_valid(d4, EXPECTED_D4_HASH),
        "d4_schema_and_decision_exact": bool(
            d4
            and d4.get("schema_version") == "lc4v4d4.composed_integration.v1"
            and d4.get("decision") == "versioned_composed_integration_valid"
            and d4.get("total_cases") == 20
            and d4.get("total_observations") == 40
        ),
        "d4_all_13_gates_pass": _all_gates(d4, 13),
        "d4_categories_complete": bool(
            d4
            and sum(item.get("passed", 0) for item in d4_counts.values()) == 20
            and sum(item.get("failed", 0) for item in d4_counts.values()) == 0
        ),
        "d5_hash_valid": _hash_valid(d5, EXPECTED_D5_HASH),
        "d5_schema_and_decision_exact": bool(
            d5
            and d5.get("schema_version") == "lc4v4d5.adoption_audit.v1"
            and d5.get("decision") == "option_a_adoption_audit_valid_with_4_blockers"
            and d5.get("total_probes") == 60
            and d5.get("total_legacy_observations") == 120
            and d5.get("total_option_a_observations") == 120
        ),
        "d5_all_27_gates_pass": _all_gates(d5, 27),
        "d5_diagnostic_taxonomy_exact": bool(
            d5_counts.get("legacy_equivalent") == 35
            and d5_counts.get("accepted_d4_versioned_change") == 20
            and d5_counts.get("expected_versioned_relation") == 1
            and d5_counts.get("adoption_blocker_missing_mutation_deltas") == 3
            and d5_counts.get("adoption_blocker_target_field_conflict_and_missing_mutation_deltas") == 1
        ),
        "d5r1_hash_valid": _hash_valid(d5r1, EXPECTED_D5R1_HASH),
        "d5r1_schema_and_decision_exact": bool(
            d5r1
            and d5r1.get("schema_version") == "lc4v4d5r1.remediation_evidence.v1"
            and d5r1.get("decision") == "d5r1_taxonomy_valid"
            and d5r1.get("total_probes") == 60
            and d5r1.get("total_legacy_observations") == 120
            and d5r1.get("total_option_a_observations") == 120
        ),
        "d5r1_all_28_gates_pass": _all_gates(d5r1, 28),
        "d5r1_taxonomy_exact": bool(
            d5r1_counts.get("legacy_equivalent") == 37
            and d5r1_counts.get("accepted_d4_versioned_change") == 20
            and d5r1_counts.get("expected_versioned_relation") == 3
            and d5r1_counts.get("adoption_blocker_missing_mutation_deltas") == 0
            and d5r1_counts.get("adoption_blocker_target_field_conflict_and_missing_mutation_deltas") == 0
            and d5r1_counts.get("unexpected_difference") == 0
            and d5r1_counts.get("option_a_failed") == 0
        ),
        "d5r1_empty_blocker_selection": bool(
            d5r1
            and d5r1.get("blocker_ids") == []
            and d5r1.get("empty_blocker_selection_hash") == EXPECTED_EMPTY_BLOCKER_HASH
        ),
        "d5r1_zero_forbidden_observations": bool(
            d5r1 and d5r1.get("forbidden_observations") == []
        ),
        "legacy_and_d4_chain_unchanged": bool(
            d4
            and d5
            and d5r1
            and d4.get("legacy_60_baseline_hash") == EXPECTED_LEGACY_60_HASH
            and d5.get("legacy_60_baseline_hash") == EXPECTED_LEGACY_60_HASH
            and d5r1.get("legacy_60_baseline_hash") == EXPECTED_LEGACY_60_HASH
            and d5.get("d4_report_hash") == EXPECTED_D4_HASH
            and d5r1.get("d4_report_hash") == EXPECTED_D4_HASH
            and d5r1.get("d5_report_hash") == EXPECTED_D5_HASH
        ),
        "d5r1_acceptance_exact": (
            "Decision: `exact_four_remediation_accepted`" in acceptance
            and "report hash is\n`sha256:0cb444d1" in acceptance
        ),
        "legacy_default_option_a_explicit": (
            default_policy is PolicyVersion.LEGACY
            and PolicyVersion.OPTION_A.value == "option_a"
        ),
    }

    decision = (
        "development_exit_valid_holdout_decision_required"
        if all(gates.values())
        else "reassessment_invalid"
    )
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "input_report_hashes": {
            "d4": EXPECTED_D4_HASH,
            "d5": EXPECTED_D5_HASH,
            "d5r1": EXPECTED_D5R1_HASH,
        },
        "development_taxonomy": {
            "legacy_equivalent": d5r1_counts.get("legacy_equivalent"),
            "accepted_d4_versioned_change": d5r1_counts.get("accepted_d4_versioned_change"),
            "expected_versioned_relation": d5r1_counts.get("expected_versioned_relation"),
            "remaining_blockers": len(d5r1.get("blocker_ids", [])) if d5r1 else None,
        },
        "gates": gates,
        "recommendation": "authorize_genuinely_fresh_certification_holdout",
        "requires_user_decision": True,
        "certification_claimed": False,
    }
    report["report_hash"] = _payload_hash(report)
    report["decision"] = decision
    return report


def generate_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def generate_report_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# Bernie LC4V4D5E1 Development Exit",
        "",
        f"Decision: `{report['decision']}`",
        "",
        f"Report hash: `{report['report_hash']}`",
        "",
        "All ordinary development evidence is internally consistent and no supported remediation blocker remains.",
        "This is not product certification. Yuri must choose a genuinely fresh certification holdout (recommended)",
        "or approve an explicit reviewed reuse policy before any certification evaluation.",
        "",
        "Holdouts v1-v4 remain sealed; T3 and provider/product/write gates remain closed.",
        "",
    ])


__all__ = [
    "SCHEMA_VERSION",
    "EXPECTED_D4_HASH",
    "EXPECTED_D5_HASH",
    "EXPECTED_D5R1_HASH",
    "run_d5e1_exit",
    "generate_report_json",
    "generate_report_markdown",
]
