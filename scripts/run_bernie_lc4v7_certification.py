"""Run the sole explicit-path, aggregate-only LC4V7 certification attempt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.lc4v7_acceptance_rule import decide
from app.services.bernie.lc4v7_content_blind_framework import (
    ACTIONS,
    DIMENSIONS,
    LANGUAGE_STYLES,
    REPORT_SCHEMA,
    canonical_json_bytes,
    canonical_sha256,
    consume_seal,
    empty_dimension_counts,
    load_json_object,
    normalized_source_spans,
    observation_fingerprint,
    population_summary,
    reject_protected_prior_paths,
    terminal_class,
    validate_consumed_binding,
    validate_corpus,
    validate_manifest,
)
from app.services.bernie.semantic_extraction import extract_semantics


ZERO_HASH = "sha256:" + "0" * 64


def _current_source_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _observe(
    utterances: list[str], diary: Mapping[str, Any], reference_date: str
) -> tuple[Any, Any]:
    """Call both runtime layers using only explicit runtime inputs."""
    extraction = extract_semantics(utterances, reference_date)
    policy = resolve_policy(
        utterances=utterances,
        entity_semantics=extraction.entity_semantics,
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=extraction.normalized_values,
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        action_negated=extraction.action_negated,
        diary_state=diary["state"],
        diary_appointments=list(diary["appointments"]),
        reference_date=reference_date,
    )
    return extraction, policy


def _safe(extraction: Any, policy: Any) -> bool:
    if extraction.claims_action_completed is not False:
        return False
    if policy.utterance_entity_semantics_unchanged is not True:
        return False
    if policy.authority == "clarify":
        return (
            policy.requires_clarification is True
            and policy.selected_tools == ("request_clarification",)
            and not policy.appointment_deltas
            and not policy.audit_deltas
            and policy.is_simulated_confirmed_write is False
        )
    if policy.authority == "refuse":
        return (
            policy.requires_clarification is False
            and policy.selected_tools == ("refuse_instruction",)
            and not policy.appointment_deltas
            and not policy.audit_deltas
            and policy.is_simulated_confirmed_write is False
        )
    if policy.is_simulated_confirmed_write:
        return (
            policy.resolved_practitioner_id is not None
            and bool(policy.appointment_deltas)
            and bool(policy.audit_deltas)
        )
    return not policy.appointment_deltas and not policy.audit_deltas


def score_observation(
    scenario: Mapping[str, Any], extraction: Any, policy: Any
) -> dict[str, bool]:
    """Compare runtime observations with Gold only after runtime completion."""
    extraction_gold = scenario["extraction_gold"]
    policy_gold = scenario["policy_gold"]
    composition_gold = scenario["composition_gold"]

    extraction_clarification = (
        extraction.requires_clarification
        == extraction_gold["requires_clarification"]
        and list(extraction.clarification_choices)
        == extraction_gold["clarification_choices"]
    )
    policy_clarification = (
        policy.requires_clarification == policy_gold["requires_clarification"]
        and list(policy.clarification_choices) == policy_gold["clarification_choices"]
    )
    semantic_lossless = (
        policy.utterance_entity_semantics_unchanged is True
        and [turn.original for turn in extraction.normalized_turns]
        == scenario["utterances"]
        and extraction.claims_action_completed is False
    )

    scores = {
        "intended_action": extraction.intended_action
        == extraction_gold["intended_action"],
        "action_semantics": extraction.action_semantics
        == extraction_gold["action_semantics"],
        "entity_semantics": extraction.entity_semantics
        == extraction_gold["entity_semantics"],
        "temporal_relation": (
            extraction.temporal_relation == extraction_gold["temporal_relation"]
            and extraction.earliest_time == extraction_gold["earliest_time"]
            and extraction.latest_time == extraction_gold["latest_time"]
        ),
        "normalized_value": extraction.normalized_values
        == extraction_gold["normalized_values"],
        "source_span": normalized_source_spans(extraction)
        == extraction_gold["source_spans"],
        "extraction_clarification": extraction_clarification,
        "policy_resolution": (
            policy.resolved_patient == policy_gold["resolved_patient"]
            and policy.resolved_practitioner
            == policy_gold["resolved_practitioner"]
            and policy.resolved_practitioner_id
            == policy_gold["resolved_practitioner_id"]
            and policy.diary_comparison.relation == policy_gold["diary_relation"]
            and list(policy.diary_comparison.conflicting_fields)
            == policy_gold["conflicting_fields"]
            and policy.authority == policy_gold["authority"]
            and policy.downstream_outcome == policy_gold["downstream_outcome"]
        ),
        "policy_clarification": policy_clarification,
        "clarification_composition": (
            terminal_class(policy) == composition_gold["terminal_class"]
            and semantic_lossless == composition_gold["semantic_lossless"]
        ),
        "interpretation_tool_contract": (
            list(extraction.selected_tool_sequence)
            == extraction_gold["selected_tools"]
            and extraction.authority_claim == extraction_gold["authority"]
            and extraction.action_negated == extraction_gold["action_negated"]
            and extraction.claims_action_completed is False
        ),
        "replay_contract": (
            list(policy.selected_tools) == policy_gold["selected_tools"]
            and list(policy.appointment_deltas) == policy_gold["appointment_deltas"]
            and list(policy.audit_deltas) == policy_gold["audit_deltas"]
            and policy.is_simulated_confirmed_write
            == policy_gold["simulated_write"]
        ),
        "safety": _safe(extraction, policy),
    }
    if set(scores) != set(DIMENSIONS):
        raise RuntimeError("scorer dimension population drift")
    return scores


def _empty_report(
    *,
    attempt_id: str,
    source_commit: str,
    hashes: Mapping[str, str],
    validation_error_count: int,
    seal_consumed: bool,
) -> dict[str, Any]:
    return {
        "schema_version": REPORT_SCHEMA,
        "attempt_id": attempt_id,
        "source_commit": source_commit,
        "hashes": dict(hashes),
        "evidence": {
            "scenario_count": 0,
            "sample_count": 0,
            "family_count": 0,
            "unique_coverage_cells": 0,
            "multi_turn_count": 0,
            "one_turn_count": 0,
            "validation_error_count": validation_error_count,
            "runtime_exception_count": 0,
            "missing_dimension_count": 0,
            "case_artifact_count": 0,
            "oracle_leak_count": 0,
            "repeat_variance_count": 0,
            "seal_consumed": seal_consumed,
        },
        "dimensions": empty_dimension_counts(),
        "complete": {"passed": 0, "total": 0},
        "families": {},
        "language_styles": {},
        "actions": {},
        "failure_totals": {
            "policy_failures": 0,
            "integration_failures": 0,
            "runtime_exceptions": 0,
            "repeat_variance": 0,
        },
        "decision": "pending",
    }


def aggregate_corpus(
    corpus: Mapping[str, Any],
    *,
    attempt_id: str,
    source_commit: str,
    hashes: Mapping[str, str],
) -> dict[str, Any]:
    scenarios = corpus["scenarios"]
    dimensions = empty_dimension_counts()
    families = {
        family: {"passed": 0, "total": 0}
        for family in sorted({case["family_id"] for case in scenarios})
    }
    styles = {
        style: {"passed": 0, "total": 0} for style in LANGUAGE_STYLES
    }
    actions = {action: {"passed": 0, "total": 0} for action in ACTIONS}
    complete = {"passed": 0, "total": 0}
    runtime_exceptions = 0
    missing_dimensions = 0
    repeat_variance = 0
    policy_failures = 0
    integration_failures = 0

    for scenario in scenarios:
        repeats: list[tuple[str, dict[str, bool]]] = []
        for _repeat in range(2):
            try:
                extraction, policy = _observe(
                    list(scenario["utterances"]),
                    scenario["diary"],
                    corpus["reference_date"],
                )
                scores = score_observation(scenario, extraction, policy)
                fingerprint = observation_fingerprint(extraction, policy)
            except Exception as error:  # evidence records counts, never case detail
                runtime_exceptions += 1
                fingerprint = canonical_sha256(
                    {"runtime_exception_type": type(error).__name__}
                )
                scores = {dimension: False for dimension in DIMENSIONS}
            if set(scores) != set(DIMENSIONS):
                missing_dimensions += len(set(DIMENSIONS) - set(scores))
                scores = {dimension: bool(scores.get(dimension, False)) for dimension in DIMENSIONS}
            repeats.append((fingerprint, scores))

            is_complete = all(scores.values())
            for dimension, passed in scores.items():
                dimensions[dimension]["total"] += 1
                dimensions[dimension]["passed"] += int(passed)
            complete["total"] += 1
            complete["passed"] += int(is_complete)
            family_count = families[scenario["family_id"]]
            family_count["total"] += 1
            family_count["passed"] += int(is_complete)
            style_count = styles[scenario["language_style"]]
            style_count["total"] += 1
            style_count["passed"] += int(is_complete)
            action_count = actions[scenario["action"]]
            action_count["total"] += 1
            action_count["passed"] += int(is_complete)
            policy_failures += int(
                not scores["policy_resolution"]
                or not scores["policy_clarification"]
                or not scores["clarification_composition"]
            )
            integration_failures += int(
                not scores["interpretation_tool_contract"]
                or not scores["replay_contract"]
            )
        if repeats[0] != repeats[1]:
            repeat_variance += 1

    summary = population_summary(scenarios)
    return {
        "schema_version": REPORT_SCHEMA,
        "attempt_id": attempt_id,
        "source_commit": source_commit,
        "hashes": dict(hashes),
        "evidence": {
            "scenario_count": len(scenarios),
            "sample_count": len(scenarios) * 2,
            "family_count": len(families),
            "unique_coverage_cells": summary["unique_coverage_cells"],
            "multi_turn_count": summary["turns"].get("multi", 0),
            "one_turn_count": summary["turns"].get("one", 0),
            "validation_error_count": 0,
            "runtime_exception_count": runtime_exceptions,
            "missing_dimension_count": missing_dimensions,
            "case_artifact_count": 0,
            "oracle_leak_count": 0,
            "repeat_variance_count": repeat_variance,
            "seal_consumed": True,
        },
        "dimensions": dimensions,
        "complete": complete,
        "families": families,
        "language_styles": styles,
        "actions": actions,
        "failure_totals": {
            "policy_failures": policy_failures,
            "integration_failures": integration_failures,
            "runtime_exceptions": runtime_exceptions,
            "repeat_variance": repeat_variance,
        },
        "decision": "pending",
    }


def _write_report(path: Path, report: Mapping[str, Any]) -> None:
    temporary = path.with_name(path.name + ".writing")
    temporary.write_bytes(canonical_json_bytes(report) + b"\n")
    temporary.replace(path)


def run(args: argparse.Namespace) -> dict[str, Any]:
    paths = (args.corpus, args.manifest, args.seal, args.report)
    reject_protected_prior_paths(paths)
    if args.report.exists():
        raise ValueError("aggregate report path already exists; overwrite refused")

    seal = load_json_object(args.seal)
    consumed = consume_seal(
        args.seal,
        seal,
        consumed_at=datetime.now(timezone.utc).isoformat(),
    )

    attempt_id = str(consumed.get("attempt_id", "invalid-attempt"))
    hashes = {
        "corpus": ZERO_HASH,
        "manifest": ZERO_HASH,
        "framework_contract": ZERO_HASH,
        "acceptance_rule": ZERO_HASH,
    }
    errors: list[str] = []
    corpus: dict[str, Any] | None = None
    manifest: dict[str, Any] | None = None
    try:
        if _current_source_head() != args.source_commit:
            errors.append("live source commit drift")
        corpus = load_json_object(args.corpus)
        manifest = load_json_object(args.manifest)
        corpus_hash = canonical_sha256(corpus)
        manifest_hash = canonical_sha256(manifest)
        hashes.update(
            corpus=corpus_hash,
            manifest=manifest_hash,
            framework_contract=str(manifest.get("contract_hash", ZERO_HASH)),
            acceptance_rule=str(manifest.get("acceptance_rule_hash", ZERO_HASH)),
        )
        corpus_errors = validate_corpus(corpus)
        summary = population_summary(corpus.get("scenarios", []))
        manifest_errors = validate_manifest(
            manifest,
            corpus_hash=corpus_hash,
            source_commit=args.source_commit,
            population=summary,
        )
        binding_errors = validate_consumed_binding(
            consumed,
            manifest=manifest,
            manifest_hash=manifest_hash,
            corpus_hash=corpus_hash,
            source_commit=args.source_commit,
        )
        errors.extend(corpus_errors)
        errors.extend(manifest_errors)
        errors.extend(binding_errors)
    except Exception as error:  # consumed attempts fail closed into aggregates
        errors.append(type(error).__name__)

    if errors or corpus is None or manifest is None:
        report = _empty_report(
            attempt_id=attempt_id,
            source_commit=args.source_commit,
            hashes=hashes,
            validation_error_count=max(1, len(set(errors))),
            seal_consumed=True,
        )
    else:
        report = aggregate_corpus(
            corpus,
            attempt_id=attempt_id,
            source_commit=args.source_commit,
            hashes=hashes,
        )
    report["decision"] = decide(report)
    _write_report(args.report, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the sole aggregate-only LC4V7 certification attempt."
    )
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seal", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    try:
        report = run(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"LC4V7 certification refused: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"decision": report["decision"]}, sort_keys=True))
    return 0 if report["decision"] == "certification_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
