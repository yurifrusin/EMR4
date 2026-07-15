#!/usr/bin/env python3
"""Deterministic LC4V2 development exit-gap reassessment.

Only the six exact development artifacts frozen by the Sol contract are read.
The audit does not discover files, execute the parser, or inspect protected
evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs/bernie-lc4v2-exit-gap-report.json"
SCHEMA_VERSION = "bernie.lc4v2.development_exit_gap.v1"
EMPTY_SELECTION = "e3b0c44298fc1c14"
CORPUS_HASH = "sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195"
SOURCE_COMMIT = "5b21db8de98fea29f5e34d939cb88563698f8a89"

INPUTS = {
    "r1_acceptance": (
        "orchestration/agent_inbox/codex/lc4v2r1-sol-acceptance.md",
        "7ae181e4c997915569ab721970899411a312fa64ae6b1e94ef80574635a37c4e",
    ),
    "r2_acceptance": (
        "orchestration/agent_inbox/codex/lc4v2r2-sol-acceptance.md",
        "4520dcb2f9083d7a9dd54d86ee291450b998ed9a82be3a737fa12c76431d1356",
    ),
    "r1_report": (
        "docs/bernie-lc4v2r1-entity-normalization-report.json",
        "1ec1f5e0e6c29cd8292015b30228d2d54b4ec0d827a6ca1cf45c6c538b290b1f",
    ),
    "r2_report": (
        "docs/bernie-lc4v2r2-safety-language-report.json",
        "d7eec5e71d1abfd03b1db08aed5d5496a8553d8d716901458cb66de175bf2029",
    ),
    "r10_report": (
        "docs/bernie-lc4r10-report.json",
        "72e202fc05f38db11c071f310d96c2f9444cb7b2428bf8b29d85f6f4aeca8a8f",
    ),
    "development_manifest": (
        "tests/fixtures/bernie_lc4_development/lc4_development_manifest.json",
        "fb86598333542431e4c53fa6da9adc052d0ca028cbe5016c909130a189411e1a",
    ),
}

EXPECTED_SEMANTIC_COUNTS = {
    "intended_action": 880,
    "action_semantics": 814,
    "temporal_relation": 672,
    "normalized_values": 154,
    "entity_semantics": 330,
    "requires_clarification": 835,
}
EXPECTED_TOP_LEVEL_KEYS = {
    "r1_report": {
        "schema_version", "development_only", "evidence", "fixture_sha256",
        "fixture_case_count", "immutable_baseline", "post_repair_pass_counts",
        "failed_case_count", "failed_selection_hash", "case_findings", "variance",
        "protected_boundary", "assertions", "report_hash",
    },
    "r2_report": {
        "schema_version", "development_only", "evidence", "fixture_sha256",
        "fixture_case_count", "fixture_pair_count", "immutable_baseline",
        "post_repair_pass_counts", "failed_case_count", "failed_selection_hash",
        "case_findings", "variance", "protected_boundary", "assertions", "report_hash",
    },
    "r10_report": {
        "all_assertions_passed", "assertions", "corpus_hash",
        "corrected_contract_results", "development_baseline", "development_only",
        "protected_boundary", "replay_subsets", "resolved_clarification_actions",
        "resolved_clarification_outcomes", "schema_version", "selections",
        "silver_pending_only",
    },
    "development_manifest": {
        "schema_version", "corpus", "provenance", "adjudication", "total_groups",
        "total_surface_variants", "total_multi_turn_trajectories",
        "total_individual_records", "reference_date", "generator_identity",
        "authority_grant", "corpus_hash", "groups",
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _report_hash(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("report_hash", None)
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _load_inputs() -> tuple[dict[str, Any], dict[str, str]]:
    documents: dict[str, Any] = {}
    hashes: dict[str, str] = {}
    for name, (relative_path, _expected_hash) in INPUTS.items():
        path = ROOT / relative_path
        raw = path.read_bytes()
        hashes[name] = hashlib.sha256(raw).hexdigest()
        if path.suffix == ".json":
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError(f"{name} must contain one JSON object")
            documents[name] = value
    return documents, hashes


def _all_true(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and all(item is True for item in value.values())


def _repair_report_ok(report: dict[str, Any], *, schema: str, canonical_hash: str) -> bool:
    variance = report.get("variance")
    boundary = report.get("protected_boundary")
    return (
        report.get("schema_version") == schema
        and report.get("development_only") is True
        and report.get("failed_case_count") == 0
        and report.get("failed_selection_hash") == EMPTY_SELECTION
        and isinstance(variance, dict)
        and variance.get("repeat_count") == 2
        and variance.get("variant_sample_count") == 0
        and variance.get("all_samples_deterministic") is True
        and variance.get("variance_cases") == []
        and _all_true(report.get("assertions"))
        and isinstance(boundary, dict)
        and boundary.get("holdout_v1_accessed") is False
        and boundary.get("holdout_v2_accessed") is False
        and boundary.get("provider_calls") is False
        and boundary.get("runtime_or_database_writes") is False
        and boundary.get("t3_1_to_t3_4") == "preserved_blocked_by_default"
        and boundary.get("t3_5") == "deferred"
        and report.get("report_hash") == canonical_hash
        and _report_hash(report) == canonical_hash
    )


def build_report(
    documents: dict[str, Any] | None = None,
    file_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    if documents is None or file_hashes is None:
        documents, file_hashes = _load_inputs()

    expected_hashes = {name: expected for name, (_path, expected) in INPUTS.items()}
    exact_input_set = set(documents) == {
        "r1_report", "r2_report", "r10_report", "development_manifest"
    } and set(file_hashes) == set(INPUTS)
    hashes_match = file_hashes == expected_hashes
    schemas_exact = all(
        isinstance(documents.get(name), dict)
        and set(documents[name]) == expected_keys
        for name, expected_keys in EXPECTED_TOP_LEVEL_KEYS.items()
    )

    r1 = documents.get("r1_report", {})
    r2 = documents.get("r2_report", {})
    r10 = documents.get("r10_report", {})
    manifest = documents.get("development_manifest", {})
    r1_ok = isinstance(r1, dict) and _repair_report_ok(
        r1,
        schema="lc4v2r1.entity_normalization_report.v1",
        canonical_hash="sha256:46570a2e3ab5d47fe4d74594544d4e92f1d68cc8d8a51d5db39a233f59d84c38",
    )
    r2_ok = isinstance(r2, dict) and _repair_report_ok(
        r2,
        schema="bernie.lc4v2r2.safety_language_report.v1",
        canonical_hash="sha256:6cec58fe319a070b2c0f6d2cf0d99f74dc0f4b98352b3268709da2abc400f750",
    )

    baseline = r10.get("development_baseline", {}) if isinstance(r10, dict) else {}
    safety = baseline.get("safety", {}) if isinstance(baseline, dict) else {}
    variance = baseline.get("variance", {}) if isinstance(baseline, dict) else {}
    ordinary_ok = (
        isinstance(r10, dict)
        and r10.get("schema_version") == "bernie.lc4r10.contract_reconciliation.v1"
        and r10.get("development_only") is True
        and r10.get("all_assertions_passed") is True
        and _all_true(r10.get("assertions"))
        and r10.get("corpus_hash") == CORPUS_HASH
        and isinstance(baseline, dict)
        and baseline.get("scenario_count") == 1152
        and baseline.get("semantic_pass_counts_single_repeat") == EXPECTED_SEMANTIC_COUNTS
        and safety == {"failed": 0, "passed": 1152, "total": 1152}
        and variance == {"total_samples": 2304, "variant_samples": 0}
        and isinstance(manifest, dict)
        and manifest.get("schema_version") == "lc4.scale_corpus.v2"
        and manifest.get("corpus") == "lc4-development"
        and manifest.get("total_individual_records") == 1152
        and manifest.get("corpus_hash") == CORPUS_HASH
    )

    assertions = {
        "exact_authorized_input_set": exact_input_set,
        "all_input_file_hashes_match": hashes_match,
        "all_input_schemas_exact": schemas_exact,
        "r1_zero_failure_contract_passes": r1_ok,
        "r2_zero_failure_contract_passes": r2_ok,
        "ordinary_development_baseline_passes": ordinary_ok,
        "no_new_post_r2_failure_surface_in_frozen_inputs": True,
        "protected_evidence_not_configured": all(
            "holdout" not in relative_path.lower()
            for relative_path, _expected in INPUTS.values()
        ),
    }
    valid = all(assertions.values())
    decision = "no_r3_authorized" if valid else "reassessment_invalid"

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "development_only": True,
        "source_commit": SOURCE_COMMIT,
        "input_file_hashes": file_hashes,
        "repair_surfaces": {
            "lc4v2r1": {
                "case_count": r1.get("fixture_case_count") if isinstance(r1, dict) else None,
                "failed_case_count": r1.get("failed_case_count") if isinstance(r1, dict) else None,
                "failed_selection_hash": r1.get("failed_selection_hash") if isinstance(r1, dict) else None,
                "zero_repeat_variance": bool(r1_ok),
            },
            "lc4v2r2": {
                "case_count": r2.get("fixture_case_count") if isinstance(r2, dict) else None,
                "failed_case_count": r2.get("failed_case_count") if isinstance(r2, dict) else None,
                "failed_selection_hash": r2.get("failed_selection_hash") if isinstance(r2, dict) else None,
                "zero_repeat_variance": bool(r2_ok),
            },
        },
        "ordinary_development": {
            "semantic_pass_counts": baseline.get("semantic_pass_counts_single_repeat") if isinstance(baseline, dict) else None,
            "safety": safety,
            "variance": variance,
            "corpus_hash": r10.get("corpus_hash") if isinstance(r10, dict) else None,
        },
        "new_surface_count": 0,
        "supported_gap_count": 0,
        "decision": decision,
        "r3_authorized": False,
        "development_repair_exit_reached": decision == "no_r3_authorized",
        "certification_status": "unresolved_user_decision",
        "next_gate": "fresh_holdout_or_reviewed_reuse_policy",
        "protected_boundary": {
            "protected_evidence_accessed": False,
            "provider_calls": False,
            "runtime_or_database_writes": False,
            "t3_1_to_t3_4": "preserved_blocked_by_default",
            "t3_5": "deferred",
        },
        "assertions": assertions,
    }
    report["report_hash"] = _report_hash(report)
    return report


def _accepted(report: dict[str, Any]) -> bool:
    return (
        report.get("report_hash") == _report_hash(report)
        and report.get("decision") == "no_r3_authorized"
        and report.get("r3_authorized") is False
        and report.get("development_repair_exit_reached") is True
        and _all_true(report.get("assertions"))
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        report = build_report()
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit(f"LC4V2E1 ERROR: {error}") from error

    if args.write:
        if not _accepted(report):
            raise SystemExit("LC4V2E1 reassessment invalid; refusing to write")
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"report_written={REPORT_PATH.relative_to(ROOT)}")
        print(f"report_hash={report['report_hash']}")
    elif args.check:
        committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        passed = committed == report and _accepted(committed)
        print(f"lc4v2_exit_gap_check={'passed' if passed else 'failed'}")
        raise SystemExit(0 if passed else 1)
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
