"""Fail-closed coherence audit for the admitted synthetic Silver corpus.

The audit uses only the accepted synthetic candidates, their dialogue-free
ordinary-development seeds, and the historical admission binding.  Product
parser output is deliberately not an input to any coherence decision.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
from app.services.bernie.synthetic_noise_codex import _temporal_phrase
from app.services.bernie.synthetic_noise_corpus import (
    DEFAULT_SEED_PATH,
    candidate_records_hash,
    load_jsonl,
    validate_candidate_records,
    validate_semantic_seed_manifest,
)
from app.services.bernie.synthetic_noise_robustness import (
    DIAGNOSTIC_PRIORITY,
    GENERATOR_IDENTITY,
    _candidate_scenario,
    _dimension_records,
    _observation_fingerprint,
    _source_scenario_lookup,
)


REPORT_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_coherence_audit.v1"
ADMISSION_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_coherence_admission.v1"
FROZEN_SOURCE_HEAD = "7c51e574930962ae83e721e3766fcbbee26d6013"
ORIGINAL_CANDIDATE_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl"
)
ORIGINAL_ADMISSION_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/admission.json"
)
COHERENT_CANDIDATE_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/candidates_sol_coherent.jsonl"
)
COHERENT_ADMISSION_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/admission_coherent.json"
)
DEFAULT_PRE_REPORT_PATH = Path(
    "docs/bernie-synthetic-silver-coherence-audit-pre-repair.json"
)
DEFAULT_FINAL_REPORT_PATH = Path(
    "docs/bernie-synthetic-silver-coherence-audit-final.json"
)
DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH = Path(
    "docs/bernie-synthetic-silver-coherence-accepted-robustness.json"
)
EXPECTED_ORIGINAL_CANONICAL_HASH = (
    "sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665"
)
EXPECTED_ORIGINAL_CANDIDATE_BLOB = "f0eadc06d8aa873b96eec77bcc94f305c0ad919b"
EXPECTED_SEED_BLOB = "38448ea31b001ade21e1953234695be789503c48"
EXPECTED_ADMISSION_BLOB = "162be3a0f1f9778b1b3e299115737fd31797809b"

DECISION_PRIORITY = (
    "reject_semantic_corruption",
    "quarantine_oracle_policy_conflict",
    "quarantine_entity_transition_conflict",
    "quarantine_replay_contract_conflict",
    "quarantine_missing_surfaced_evidence",
)
SUCCESS_OUTCOMES = frozenset(
    {
        "appointment_created",
        "appointment_moved",
        "appointment_resized",
        "appointment_cancelled",
        "appointment_status_changed",
        "schedule_explained",
    }
)
MUTATION_ACTIONS = frozenset(
    {"create", "move", "resize", "cancel", "status_change"}
)
EXPECTED_DELTA_TYPES = {
    "create": "created",
    "move": "moved",
    "resize": "resized",
    "cancel": "cancelled",
    "status_change": "status_changed",
}
ACTION_PATTERNS = {
    "create": re.compile(r"\b(?:book|booking|new\s+appt|create)\b", re.I),
    "move": re.compile(r"\b(?:move|shift|reschedul\w*)\b", re.I),
    "resize": re.compile(
        r"\b(?:resize|length\s+change|appt\s+length|make\b.{0,45}\b(?:mins?|minutes?))",
        re.I,
    ),
    "cancel": re.compile(r"\b(?:cancel|take\s+out|remove)\b", re.I),
    "status_change": re.compile(
        r"\b(?:status|arrived|completed|dna|no[- ]?show)\b", re.I
    ),
    "explain_schedule": re.compile(
        r"\b(?:diary|schedule|availability)\b.*\b(?:rundown|looking|view|through|got|availability)\b"
        r"|\b(?:rundown|looking|view|through|got|availability)\b.*\b(?:diary|schedule)\b",
        re.I,
    ),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _git_blob_hash(path: Path) -> str:
    # Git's text clean filter stores these fixtures with LF even when the
    # Windows worktree materializes CRLF.
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    header = f"blob {len(payload)}\0".encode("ascii")
    # Git object identity requires SHA-1 by protocol; this is not a security
    # digest or trust decision.
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def _file_payload_hash(records: Iterable[dict[str, Any]]) -> str:
    payload = "".join(_canonical_json(record) + "\n" for record in records)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_frozen_inputs() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    if _git_blob_hash(ORIGINAL_CANDIDATE_PATH) != EXPECTED_ORIGINAL_CANDIDATE_BLOB:
        raise ValueError("original candidate Git blob drift")
    if _git_blob_hash(DEFAULT_SEED_PATH) != EXPECTED_SEED_BLOB:
        raise ValueError("semantic seed Git blob drift")
    if _git_blob_hash(ORIGINAL_ADMISSION_PATH) != EXPECTED_ADMISSION_BLOB:
        raise ValueError("original admission Git blob drift")

    manifest = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))
    errors = validate_semantic_seed_manifest(manifest)
    if errors:
        raise ValueError("invalid semantic seed manifest: " + "; ".join(errors))
    candidates = load_jsonl(ORIGINAL_CANDIDATE_PATH)
    errors = validate_candidate_records(
        candidates,
        manifest,
        expected_generator_identity=GENERATOR_IDENTITY,
        candidate_prefix="sol",
    )
    if errors:
        raise ValueError("invalid original candidate corpus: " + "; ".join(errors))
    if candidate_records_hash(candidates) != EXPECTED_ORIGINAL_CANONICAL_HASH:
        raise ValueError("original candidate canonical hash drift")

    admission = json.loads(ORIGINAL_ADMISSION_PATH.read_text(encoding="utf-8"))
    if admission.get("canonical_candidate_hash") != EXPECTED_ORIGINAL_CANONICAL_HASH:
        raise ValueError("original admission candidate binding drift")
    if admission.get("accepted_count") != 192 or admission.get("candidate_count") != 192:
        raise ValueError("original admission population drift")
    if any(admission.get("authority_grant", {}).values()):
        raise ValueError("original admission grants authority")
    return manifest, candidates, admission


def _oracle_findings(seed: dict[str, Any]) -> list[dict[str, str]]:
    contract = seed["semantic_contract"]
    action = contract["intended_action"]
    tools = contract["expected_tool_sequence"]
    outcome = contract["expected_outcome_kind"]
    deltas = contract["expected_appointment_deltas"]
    findings: list[dict[str, str]] = []

    if tools == ["request_clarification"]:
        if contract.get("expected_clarification") is None:
            findings.append(
                {
                    "decision": "quarantine_oracle_policy_conflict",
                    "reason": "clarification_tool_without_clarification_contract",
                }
            )
        if deltas or outcome in SUCCESS_OUTCOMES:
            findings.append(
                {
                    "decision": "quarantine_oracle_policy_conflict",
                    "reason": "clarification_tool_with_success_or_mutation_delta",
                }
            )

    if action in MUTATION_ACTIONS and tools != ["request_clarification"]:
        if not outcome or not deltas:
            findings.append(
                {
                    "decision": "quarantine_replay_contract_conflict",
                    "reason": "mutation_tools_without_outcome_and_delta",
                }
            )
        expected_type = EXPECTED_DELTA_TYPES[action]
        observed_types = {delta.get("change_type") for delta in deltas}
        if deltas and observed_types != {expected_type}:
            findings.append(
                {
                    "decision": "quarantine_replay_contract_conflict",
                    "reason": "mutation_delta_type_disagrees_with_action",
                }
            )

    if outcome == "existing_booking_found" and deltas:
        findings.append(
            {
                "decision": "quarantine_replay_contract_conflict",
                "reason": "existing_booking_outcome_with_creation_delta",
            }
        )
    if action == "explain_schedule" and deltas:
        findings.append(
            {
                "decision": "quarantine_replay_contract_conflict",
                "reason": "schedule_explanation_has_appointment_delta",
            }
        )
    return findings


def _dialogue(candidate: dict[str, Any]) -> tuple[list[str], str]:
    turns = [turn["utterance"] for turn in candidate["dialogue_turns"]]
    return turns, " ".join(turns)


def _evidence_texts(candidate: dict[str, Any], key: str) -> list[str]:
    return [span["text"] for span in candidate["evidence_spans"].get(key, [])]


def _candidate_findings(
    candidate: dict[str, Any], seed: dict[str, Any]
) -> list[dict[str, str]]:
    contract = seed["semantic_contract"]
    turns, joined = _dialogue(candidate)
    lowered = joined.lower()
    findings: list[dict[str, str]] = []

    action = contract["intended_action"]
    if not ACTION_PATTERNS[action].search(joined):
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "intended_action_not_explicitly_surfaced",
            }
        )

    normalized = contract["normalized_values"]
    required = set(seed["required_evidence_keys"])
    if "appointment_date" in required and "tomorrow" not in _evidence_texts(
        candidate, "appointment_date"
    ):
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "appointment_date_does_not_surface_normalized_value",
            }
        )
    if "duration_minutes" in required:
        expected = f"{normalized['duration_minutes']} mins"
        if expected not in _evidence_texts(candidate, "duration_minutes"):
            findings.append(
                {
                    "decision": "quarantine_missing_surfaced_evidence",
                    "reason": "duration_does_not_surface_normalized_value",
                }
            )
    if "temporal_relation" in required:
        expected = _temporal_phrase(contract)
        if expected not in _evidence_texts(candidate, "temporal_relation"):
            findings.append(
                {
                    "decision": "quarantine_missing_surfaced_evidence",
                    "reason": "temporal_surface_disagrees_with_relation",
                }
            )

    patient_semantics = contract["patient_semantics"]
    if patient_semantics == "ambiguous" and "someone" not in lowered:
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "ambiguous_patient_not_surfaced",
            }
        )
    elif patient_semantics in {"exact", "corrected"}:
        expected = seed["surface_evidence"].get("patient", [None])[-1]
        if not expected or expected not in joined:
            findings.append(
                {
                    "decision": "quarantine_missing_surfaced_evidence",
                    "reason": "patient_semantics_not_surfaced",
                }
            )
        
    practitioner_semantics = contract["practitioner_semantics"]
    if practitioner_semantics == "ambiguous" and "a doctor" not in lowered:
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "ambiguous_practitioner_not_surfaced",
            }
        )
    elif practitioner_semantics in {"exact", "corrected"}:
        expected = seed["surface_evidence"].get("practitioner", [None])[-1]
        if not expected or expected not in joined:
            findings.append(
                {
                    "decision": "quarantine_missing_surfaced_evidence",
                    "reason": "practitioner_semantics_not_surfaced",
                }
            )

    if action == "status_change" and "arrived" not in lowered:
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "status_target_not_surfaced",
            }
        )

    form = contract["dialogue_form"]
    marker_checks = {
        "clarification": "details may need clarifying",
        "correction": "correction",
        "reversal": "actually, stop there",
        "ellipsis": "same details",
        "anaphora": "use that",
        "session_restart": "starting a fresh request",
    }
    marker = marker_checks.get(form)
    if marker and marker not in lowered:
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "dialogue_transition_not_surfaced",
            }
        )
    if form == "repeated" and (len(turns) < 2 or turns[-1] != turns[-2]):
        findings.append(
            {
                "decision": "quarantine_missing_surfaced_evidence",
                "reason": "repeated_request_not_repeated_exactly",
            }
        )

    if form == "reversal" and (
        contract["expected_tool_sequence"] != ["request_clarification"]
        or contract["expected_outcome_kind"] in SUCCESS_OUTCOMES
    ):
        findings.append(
            {
                "decision": "quarantine_entity_transition_conflict",
                "reason": "whole_action_withdrawn_but_oracle_expects_action",
            }
        )
    if form == "correction" and practitioner_semantics == "corrected":
        if "a doctor" not in turns[0].lower() or "dr shera" not in turns[-1].lower():
            findings.append(
                {
                    "decision": "quarantine_entity_transition_conflict",
                    "reason": "practitioner_correction_not_explicit",
                }
            )
    if action == "explain_schedule" and form == "anaphora" and "appointment" in turns[-1].lower():
        findings.append(
            {
                "decision": "reject_semantic_corruption",
                "reason": "schedule_request_anaphora_refers_to_appointment",
            }
        )
    return findings


def _primary_decision(findings: list[dict[str, str]]) -> str:
    decisions = {finding["decision"] for finding in findings}
    return next(
        (decision for decision in DECISION_PRIORITY if decision in decisions),
        "accept_coherent",
    )


def audit_records(
    manifest: dict[str, Any], candidates: list[dict[str, Any]], *, stage: str
) -> dict[str, Any]:
    seeds = {seed["seed_id"]: seed for seed in manifest["seeds"]}
    cases: list[dict[str, Any]] = []
    decision_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    by_action: dict[str, Counter[str]] = defaultdict(Counter)
    by_form: dict[str, Counter[str]] = defaultdict(Counter)
    by_noise: dict[str, Counter[str]] = defaultdict(Counter)

    for candidate in candidates:
        seed = seeds[candidate["source_seed_id"]]
        findings = _oracle_findings(seed) + _candidate_findings(candidate, seed)
        unique_findings = [
            dict(item)
            for item in {
                (finding["decision"], finding["reason"]): finding
                for finding in findings
            }.values()
        ]
        unique_findings.sort(key=lambda item: (item["decision"], item["reason"]))
        decision = _primary_decision(unique_findings)
        decision_counts[decision] += 1
        for finding in unique_findings:
            reason_counts[finding["reason"]] += 1
        contract = seed["semantic_contract"]
        by_action[contract["intended_action"]][decision] += 1
        by_form[contract["dialogue_form"]][decision] += 1
        by_noise[candidate["noise_level"]][decision] += 1
        cases.append(
            {
                "candidate_id": candidate["candidate_id"],
                "source_seed_id": candidate["source_seed_id"],
                "intended_action": contract["intended_action"],
                "dialogue_form": contract["dialogue_form"],
                "noise_level": candidate["noise_level"],
                "decision": decision,
                "findings": unique_findings,
            }
        )

    accepted_ids = sorted(
        case["candidate_id"] for case in cases if case["decision"] == "accept_coherent"
    )
    quarantine_ids = sorted(
        case["candidate_id"] for case in cases if case["decision"] != "accept_coherent"
    )
    report_without_hash = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "stage": stage,
        "decision": "audit_complete",
        "source_head": FROZEN_SOURCE_HEAD,
        "population": {
            "candidates": len(cases),
            "accepted": len(accepted_ids),
            "quarantined_or_rejected": len(quarantine_ids),
        },
        "input_bindings": {
            "candidate_canonical_hash": candidate_records_hash(candidates),
            "candidate_file_payload_hash": _file_payload_hash(candidates),
            "seed_manifest_hash": manifest["manifest_hash"],
        },
        "decision_counts": dict(sorted(decision_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "breakdown": {
            "by_action": {
                key: dict(sorted(value.items())) for key, value in sorted(by_action.items())
            },
            "by_dialogue_form": {
                key: dict(sorted(value.items())) for key, value in sorted(by_form.items())
            },
            "by_noise_level": {
                key: dict(sorted(value.items())) for key, value in sorted(by_noise.items())
            },
        },
        "accepted_selection_hash": _sha256(accepted_ids),
        "quarantine_selection_hash": _sha256(quarantine_ids),
        "cases": cases,
        "boundaries": {
            "protected_holdout_access": False,
            "historical_diary_access": False,
            "external_corpus_access": False,
            "product_parser_used_for_decisions": False,
            "product_write": False,
        },
    }
    return {**report_without_hash, "report_hash": _sha256(report_without_hash)}


def build_pre_repair_report() -> dict[str, Any]:
    manifest, candidates, _ = load_frozen_inputs()
    return audit_records(manifest, candidates, stage="pre_repair")


def repair_candidate_text(
    manifest: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Repair only independently identified candidate-text defects."""

    repaired = deepcopy(candidates)
    seeds = {seed["seed_id"]: seed for seed in manifest["seeds"]}
    for candidate in repaired:
        contract = seeds[candidate["source_seed_id"]]["semantic_contract"]
        turns, joined = _dialogue(candidate)
        if (
            contract["intended_action"] == "resize"
            and not ACTION_PATTERNS["resize"].search(joined)
        ):
            action_turn = next(
                (
                    turn
                    for turn in candidate["dialogue_turns"]
                    if "appt" in turn["utterance"].lower()
                    or "mins" in turn["utterance"].lower()
                ),
                None,
            )
            if action_turn is None:
                raise ValueError("missing resize action turn during repair")
            action_turn["utterance"] += " This is a resize request."
        if (
            contract["intended_action"] == "explain_schedule"
            and contract["dialogue_form"] == "anaphora"
        ):
            final_turn = candidate["dialogue_turns"][-1]
            if final_turn["utterance"] != "Use that appointment for the request.":
                raise ValueError("unexpected schedule-anaphora repair surface")
            final_turn["utterance"] = "Use that diary request as the reference."
    return repaired


def build_final_artifacts() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    manifest, original, _ = load_frozen_inputs()
    candidates = repair_candidate_text(manifest, original)
    mechanical_errors = validate_candidate_records(
        candidates,
        manifest,
        expected_generator_identity=GENERATOR_IDENTITY,
        candidate_prefix="sol",
    )
    if mechanical_errors:
        raise ValueError("invalid repaired candidate corpus: " + "; ".join(mechanical_errors))
    report = audit_records(manifest, candidates, stage="post_repair")
    cases = {case["candidate_id"]: case for case in report["cases"]}
    accepted_ids = sorted(
        candidate_id
        for candidate_id, case in cases.items()
        if case["decision"] == "accept_coherent"
    )
    quarantine_ids = sorted(set(cases) - set(accepted_ids))
    admission_without_hash = {
        "schema_version": ADMISSION_SCHEMA_VERSION,
        "decision": "partial_pass_with_quarantine",
        "candidate_path": COHERENT_CANDIDATE_PATH.as_posix(),
        "source_candidate_path": ORIGINAL_CANDIDATE_PATH.as_posix(),
        "candidate_count": len(candidates),
        "accepted_count": len(accepted_ids),
        "quarantine_count": len(quarantine_ids),
        "rejected_count": 0,
        "canonical_candidate_hash": candidate_records_hash(candidates),
        "file_payload_hash": _file_payload_hash(candidates),
        "audit_report_hash": report["report_hash"],
        "accepted_selection_hash": report["accepted_selection_hash"],
        "quarantine_selection_hash": report["quarantine_selection_hash"],
        "accepted_candidate_ids": accepted_ids,
        "quarantined_candidates": [
            {
                "candidate_id": candidate_id,
                "primary_decision": cases[candidate_id]["decision"],
                "reasons": [finding["reason"] for finding in cases[candidate_id]["findings"]],
            }
            for candidate_id in quarantine_ids
        ],
        "evidence_tier": "silver",
        "authorized_uses": [
            "ordinary_development_evaluation",
            "synthetic_noise_robustness_tests",
            "future_development_candidate_generation",
        ],
        "excluded_claims_and_authority": [
            "real_world_representativeness",
            "clinical_validation",
            "gold_evidence",
            "certification_evidence",
            "protected_holdout_evidence",
            "runtime_or_provider_activation",
            "confirmation_or_write_authority",
        ],
        "protected_holdout_access": False,
        "historical_diary_access": False,
        "external_corpus_access": False,
        "authority_grant": {
            "provider_write": False,
            "diary_write": False,
            "confirmation": False,
            "override_authority": False,
        },
    }
    admission = {**admission_without_hash, "admission_hash": _sha256(admission_without_hash)}
    return candidates, report, admission


def build_accepted_robustness_report() -> dict[str, Any]:
    """Evaluate only the rows admitted by the coherence audit, twice each."""

    manifest, _, _ = load_frozen_inputs()
    candidates, audit_report, admission = build_final_artifacts()
    accepted_ids = set(admission["accepted_candidate_ids"])
    selected = [
        candidate for candidate in candidates if candidate["candidate_id"] in accepted_ids
    ]
    if len(selected) != admission["accepted_count"]:
        raise ValueError("accepted robustness selection does not match admission")
    seeds = {seed["seed_id"]: seed for seed in manifest["seeds"]}
    sources = _source_scenario_lookup(manifest)
    dimension_counts: dict[str, Counter[str]] = defaultdict(Counter)
    primary_counts: Counter[str] = Counter()
    fingerprints: dict[str, set[str]] = defaultdict(set)
    candidate_cases: list[dict[str, Any]] = []

    for candidate in selected:
        seed = seeds[candidate["source_seed_id"]]
        scenario = _candidate_scenario(candidate, seed, sources[seed["seed_id"]])
        repeat_results = []
        first_primary: str | None = None
        for sample_index in range(2):
            interpretation = replace(
                deterministic_interpret(scenario), sample_index=sample_index
            )
            replay = deterministic_replay(scenario, interpretation)
            result = score_interpretation_replay_pair(scenario, interpretation, replay)
            repeat_results.append(result)
            fingerprints[candidate["candidate_id"]].add(
                _observation_fingerprint(result)
            )
            dimensions = _dimension_records(scenario, result)
            failed_categories = {
                item["category"] for item in dimensions if not item["passed"]
            }
            for item in dimensions:
                dimension_counts[item["name"]][
                    "passed" if item["passed"] else "failed"
                ] += 1
            primary = next(
                (
                    category
                    for category in DIAGNOSTIC_PRIORITY
                    if category in failed_categories
                ),
                None,
            )
            if primary is not None:
                primary_counts[primary] += 1
            if sample_index == 0:
                first_primary = primary
        candidate_cases.append(
            {
                "candidate_id": candidate["candidate_id"],
                "source_seed_id": candidate["source_seed_id"],
                "intended_action": seed["semantic_contract"]["intended_action"],
                "dialogue_form": seed["semantic_contract"]["dialogue_form"],
                "noise_level": candidate["noise_level"],
                "complete": all(result.all_passed for result in repeat_results),
                "primary_diagnostic_category": first_primary,
            }
        )

    variance_ids = sorted(
        candidate_id
        for candidate_id, values in fingerprints.items()
        if len(values) != 1
    )
    complete = sum(case["complete"] for case in candidate_cases)
    safety = dimension_counts["safety"]
    report_without_hash = {
        "schema_version": "emr4.bernie.synthetic_noise_coherence_robustness.v1",
        "decision": (
            "accepted_population_evaluation_complete"
            if (
                len(candidate_cases) == admission["accepted_count"]
                and not variance_ids
                and safety["failed"] == 0
            )
            else "revision_required"
        ),
        "input_bindings": {
            "candidate_canonical_hash": admission["canonical_candidate_hash"],
            "audit_report_hash": audit_report["report_hash"],
            "admission_hash": admission["admission_hash"],
            "accepted_selection_hash": admission["accepted_selection_hash"],
        },
        "population": {
            "candidates": len(candidate_cases),
            "repeats_per_candidate": 2,
            "observations": len(candidate_cases) * 2,
            "complete_candidates": complete,
            "failed_candidates": len(candidate_cases) - complete,
        },
        "variance": {
            "variant_candidate_count": len(variance_ids),
            "variant_candidate_ids": variance_ids,
        },
        "safety": {
            "passed": safety["passed"],
            "failed": safety["failed"],
            "total": safety["passed"] + safety["failed"],
        },
        "dimension_counts": {
            name: {
                "passed": counts["passed"],
                "failed": counts["failed"],
                "total": counts["passed"] + counts["failed"],
            }
            for name, counts in sorted(dimension_counts.items())
        },
        "primary_diagnostic_category_observations": dict(
            sorted(primary_counts.items())
        ),
        "candidate_cases": candidate_cases,
        "boundaries": {
            "protected_holdout_access": False,
            "historical_diary_access": False,
            "external_corpus_access": False,
            "provider_access": False,
            "product_write": False,
            "parser_or_policy_changes": False,
        },
    }
    return {**report_without_hash, "report_hash": _sha256(report_without_hash)}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(_canonical_json(record) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )


__all__ = [
    "COHERENT_ADMISSION_PATH",
    "COHERENT_CANDIDATE_PATH",
    "DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH",
    "DEFAULT_FINAL_REPORT_PATH",
    "DEFAULT_PRE_REPORT_PATH",
    "audit_records",
    "build_final_artifacts",
    "build_accepted_robustness_report",
    "build_pre_repair_report",
    "load_frozen_inputs",
    "repair_candidate_text",
    "write_json",
    "write_jsonl",
]
