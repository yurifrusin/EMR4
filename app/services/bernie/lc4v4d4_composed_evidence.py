"""LC4V4D4 — Evidence-only exact-20 overlay oracle for versioned composed
integration.

This module maps the exact accepted 20 D3 development IDs to an explicit
Option A expectation overlay.  The overlay scores complete typed observations
for Option A, including unchanged utterance semantic fields, clarification
requirement and choices, resolved identities, policy/replay tool sequence and
authority, downstream outcome, separate diary relation and conflicting fields,
appointment/audit deltas, simulated-confirmed-write flag, and refusal/no-mutation
safety.

The ID mapping belongs only to this evidence/scoring oracle, never to the
composed runner or policy resolver.

Protected holdouts v1-v4 remain sealed.  No parser, policy, replay, scorer,
route, provider, or runtime code is modified.
"""

from __future__ import annotations

import enum
import hashlib
import json
import pathlib
from dataclasses import asdict
from typing import Any

from app.services.bernie.composed_corpus_evaluator import (
    PolicyVersion,
    VersionedComposedResult,
    compose_versioned,
)
from app.services.bernie.composed_evaluator import (
    InterpretationObservation,
    ReplayObservation,
)
from app.services.bernie.lc4v4_development_diagnostic import (
    author_all_probes,
    dict_to_spec,
)
from app.services.bernie.lc4v4d3_policy_evidence import (
    D3_TARGET_IDS,
    EXPECTED_20_CASE_HASH,
    EXPECTED_D2_REPORT_HASH,
    CHOICE_ORACLE,
    CORRECTED_PATIENT_IDS,
    OMITTED_PRACTITIONER_ID,
    CORRECTED_PRACTITIONER_IDS,
    STATE_JOIN_ORACLE,
    UNSAFE_IDS,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

SCHEMA_VERSION = "lc4v4d4.composed_integration.v1"

EXPECTED_D3_REPORT_HASH = (
    "sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8"
)
EXPECTED_LEGACY_60_HASH = (
    "sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27"
)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
D2_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d2-semantic-remediation.json"
D3_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d3-policy-resolution.json"

INCOMPATIBLE_D1_CASES: frozenset[str] = frozenset({
    OMITTED_PRACTITIONER_ID,
    "lc4v4d1_entity_patient_mismatched_06",
    "lc4v4d1_entity_practitioner_mismatched_12",
    "lc4v4d1_entity_location_mismatched_18",
    "lc4v4d1_entity_appt_type_mismatched_24",
    "lc4v4d1_entity_duration_mismatched_30",
})


def _payload_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        default=_json_default,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, enum.Enum):
        return obj.value
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _selection_hash(ids: tuple[str, ...] | list[str]) -> str:
    raw = json.dumps(sorted(ids), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _validate_d2_report() -> bool:
    payload = json.loads(D2_REPORT_PATH.read_text(encoding="utf-8"))
    embedded = payload.pop("report_hash", None)
    payload.pop("decision", None)
    return (
        embedded == EXPECTED_D2_REPORT_HASH
        and _payload_hash(payload) == EXPECTED_D2_REPORT_HASH
    )


def _validate_d3_report() -> bool:
    payload = json.loads(D3_REPORT_PATH.read_text(encoding="utf-8"))
    embedded = payload.pop("report_hash", None)
    payload.pop("decision", None)
    return (
        embedded == EXPECTED_D3_REPORT_HASH
        and _payload_hash(payload) == EXPECTED_D3_REPORT_HASH
    )


def _validate_selection_hash() -> bool:
    return EXPECTED_20_CASE_HASH == _selection_hash(D3_TARGET_IDS)


def _probes_by_id() -> dict[str, dict[str, Any]]:
    return {probe["scenario_id"]: probe for probe in author_all_probes()}


def _spec_from_id(probe_id: str) -> ReceptionScenarioSpec:
    probes = _probes_by_id()
    probe = probes[probe_id]
    return dict_to_spec(probe)


def _legacy_baseline_60() -> list[dict[str, Any]]:
    probes = author_all_probes()
    rows: list[dict[str, Any]] = []
    for probe in probes:
        spec = dict_to_spec(probe)
        interp = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.LEGACY)
        rows.append({
            "scenario_id": spec.scenario_id,
            "interpretation": asdict(interp.interpretation),
            "replay": asdict(interp.replay),
        })
    return rows


def _compute_legacy_60_hash() -> str:
    rows = _legacy_baseline_60()
    return _payload_hash(rows)


def _category(probe_id: str) -> str:
    if probe_id in CHOICE_ORACLE:
        return "clarification_alternatives"
    if probe_id in CORRECTED_PATIENT_IDS:
        return "corrected_patient"
    if probe_id == OMITTED_PRACTITIONER_ID:
        return "omitted_practitioner"
    if probe_id in CORRECTED_PRACTITIONER_IDS:
        return "corrected_practitioner"
    if probe_id in STATE_JOIN_ORACLE:
        return "diary_state_join"
    if probe_id in UNSAFE_IDS:
        return "unsafe_bypass"
    raise ValueError(f"unclassified D4 target: {probe_id}")


def _check_legacy_equivalence(
    legacy: VersionedComposedResult,
    direct_interp: InterpretationObservation,
    direct_replay: ReplayObservation,
) -> bool:
    return (
        asdict(legacy.interpretation) == asdict(direct_interp)
        and asdict(legacy.replay) == asdict(direct_replay)
    )


def _check_utterance_fields_unchanged(
    option_a: VersionedComposedResult,
    legacy: VersionedComposedResult,
) -> bool:
    oa = option_a.interpretation
    le = legacy.interpretation
    return (
        oa.intended_action == le.intended_action
        and oa.action_semantics == le.action_semantics
        and oa.temporal_relation == le.temporal_relation
        and oa.normalized_values == le.normalized_values
        and oa.entity_semantics == le.entity_semantics
        and oa.requires_clarification == le.requires_clarification
        and oa.clarification_choices == le.clarification_choices
        and oa.selected_tool_sequence == le.selected_tool_sequence
        and oa.authority_claim == le.authority_claim
        and oa.action_negated == le.action_negated
    )


def _check_option_a_overlay(
    probe_id: str,
    result: VersionedComposedResult,
) -> tuple[bool, str]:
    cat = _category(probe_id)
    policy = result
    no_mutation = (
        not policy.replay.appointment_deltas
        and not policy.replay.audit_deltas
        and not policy.replay.is_simulated_confirmed_write
    )
    if cat == "clarification_alternatives":
        expected = list(CHOICE_ORACLE[probe_id])
        passed = (
            list(policy.replay.clarification_choices) == expected
            and policy.replay.requires_clarification
            and list(policy.replay.tools_used) == ["request_clarification"]
            and no_mutation
        )
        return passed, f"choices={policy.replay.clarification_choices!r}"
    if cat == "corrected_patient":
        passed = (
            policy.resolved_patient == "Avery Quinn"
            and policy.resolved_practitioner_id is not None
            and policy.replay.downstream_outcome == "appointment_created"
        )
        return passed, (
            f"patient={policy.resolved_patient!r}; "
            f"tools={policy.replay.tools_used!r}"
        )
    if cat == "corrected_practitioner":
        passed = (
            policy.resolved_practitioner == "Dr Chen"
            and policy.resolved_practitioner_id == "pr-004"
            and len(policy.replay.appointment_deltas) == 1
            and policy.replay.appointment_deltas[0].get("practitioner_id") == "pr-004"
        )
        return passed, (
            f"practitioner={policy.resolved_practitioner!r}; "
            f"id={policy.resolved_practitioner_id!r}"
        )
    if cat == "omitted_practitioner":
        passed = (
            policy.interpretation.entity_semantics.get("practitioner") == "omitted"
            and policy.replay.requires_clarification
            and list(policy.replay.tools_used) == ["request_clarification"]
            and policy.resolved_practitioner_id is None
            and no_mutation
        )
        return passed, "omitted practitioner must clarify without mutation"
    if cat == "diary_state_join":
        field = STATE_JOIN_ORACLE[probe_id]
        passed = (
            policy.interpretation.entity_semantics.get(field) == "exact"
            and policy.diary_relation == "field_conflict"
            and list(policy.conflicting_fields) == [field]
            and policy.replay.requires_clarification
            and list(policy.replay.tools_used) == ["request_clarification"]
            and no_mutation
        )
        return passed, (
            f"relation={policy.diary_relation!r}; "
            f"fields={policy.conflicting_fields!r}"
        )
    if cat == "unsafe_bypass":
        passed = (
            policy.interpretation.action_semantics == "prohibited"
            and list(policy.replay.tools_used) == ["refuse_instruction"]
            and policy.replay.downstream_outcome == "instruction_refused"
            and no_mutation
        )
        return passed, f"tools={policy.replay.tools_used!r}"
    raise AssertionError("unreachable")


def run_d4_evidence(source_commit: str = "unknown") -> dict[str, Any]:
    g_d2_valid = _validate_d2_report()
    g_d3_valid = _validate_d3_report()
    g_selection_valid = _validate_selection_hash()
    probes = _probes_by_id()
    g_exact_population = (
        set(tuple(sorted(probes.keys()))).issuperset(set(D3_TARGET_IDS))
        and len(D3_TARGET_IDS) == 20
    )
    g_legacy_hash = _compute_legacy_60_hash() == EXPECTED_LEGACY_60_HASH

    g_legacy_equivalence = True
    for probe in probes.values():
        spec = dict_to_spec(probe)
        legacy_result = compose_versioned(
            spec, sample_index=0, policy_version=PolicyVersion.LEGACY,
        )
        from app.services.bernie.composed_corpus_evaluator import (
            deterministic_interpret,
            deterministic_replay,
        )
        direct_interp = deterministic_interpret(spec)
        direct_replay = deterministic_replay(spec, direct_interp)
        if not _check_legacy_equivalence(legacy_result, direct_interp, direct_replay):
            g_legacy_equivalence = False
            break

    option_a_results: list[dict[str, Any]] = []
    target_fingerprints: list[str] = []

    for probe_id in D3_TARGET_IDS:
        spec = _spec_from_id(probe_id)
        r1 = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        r2 = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        fp1 = _payload_hash(asdict(r1))
        fp2 = _payload_hash(asdict(r2))
        target_fingerprints.extend([fp1, fp2])
        passed, reason = _check_option_a_overlay(probe_id, r1)
        cat = _category(probe_id)
        option_a_results.append({
            "probe_id": probe_id,
            "category": cat,
            "passed": passed,
            "reason": reason,
            "fingerprint_0": fp1,
            "fingerprint_1": fp2,
            "deterministic": fp1 == fp2,
        })

    g_all_pass = len(option_a_results) == 20 and all(r["passed"] for r in option_a_results)
    g_zero_variance = all(r["fingerprint_0"] == r["fingerprint_1"] for r in option_a_results)

    g_utterance_preserved = True
    for probe_id in D3_TARGET_IDS:
        spec = _spec_from_id(probe_id)
        legacy_result = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.LEGACY)
        opt_a_result = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        if not _check_utterance_fields_unchanged(opt_a_result, legacy_result):
            g_utterance_preserved = False
            break

    g_replay_exact = True
    for probe_id in D3_TARGET_IDS:
        spec = _spec_from_id(probe_id)
        r1 = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        r2 = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        if not (
            asdict(r1.replay) == asdict(r2.replay)
            and r1.diary_relation == r2.diary_relation
            and r1.conflicting_fields == r2.conflicting_fields
            and r1.resolved_patient == r2.resolved_patient
            and r1.resolved_practitioner == r2.resolved_practitioner
            and r1.resolved_practitioner_id == r2.resolved_practitioner_id
        ):
            g_replay_exact = False
            break

    g_incompatible_recorded = len(INCOMPATIBLE_D1_CASES) == 6

    g_no_forbidden_mutation = True
    for probe_id in D3_TARGET_IDS:
        cat = _category(probe_id)
        if cat in ("omitted_practitioner", "diary_state_join", "unsafe_bypass", "clarification_alternatives"):
            spec = _spec_from_id(probe_id)
            result = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
            has_deltas = (
                bool(result.replay.appointment_deltas)
                or bool(result.replay.audit_deltas)
                or result.replay.is_simulated_confirmed_write
            )
            if has_deltas:
                g_no_forbidden_mutation = False
                break

    category_counts: dict[str, dict[str, int]] = {}
    for r in option_a_results:
        cat = r["category"]
        counts = category_counts.setdefault(cat, {"passed": 0, "failed": 0})
        counts["passed" if r["passed"] else "failed"] += 1

    gates: dict[str, bool] = {
        "d2_report_valid": g_d2_valid,
        "d3_report_valid": g_d3_valid,
        "selection_hash_valid": g_selection_valid,
        "exact_20_case_population": g_exact_population,
        "legacy_60_baseline_hash_exact": g_legacy_hash,
        "legacy_runner_equivalence": g_legacy_equivalence,
        "all_20_option_a_pass": g_all_pass,
        "zero_variance": g_zero_variance,
        "utterance_semantics_preserved": g_utterance_preserved,
        "replay_fields_exact": g_replay_exact,
        "incompatible_d1_recorded": g_incompatible_recorded,
        "no_forbidden_mutation": g_no_forbidden_mutation,
    }

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "d2_report_hash": EXPECTED_D2_REPORT_HASH,
        "d3_report_hash": EXPECTED_D3_REPORT_HASH,
        "d3_selection_hash": EXPECTED_20_CASE_HASH,
        "legacy_60_baseline_hash": EXPECTED_LEGACY_60_HASH,
        "total_cases": len(D3_TARGET_IDS),
        "total_observations": len(target_fingerprints),
        "category_counts": category_counts,
        "incompatible_d1_cases": sorted(INCOMPATIBLE_D1_CASES),
        "gates": gates,
        "cases": option_a_results,
    }
    report["decision"] = "candidate_complete" if all(gates.values()) else "revision_required"
    canonical = dict(report)
    canonical.pop("decision", None)
    report["report_hash"] = _payload_hash(canonical)
    return report


def generate_report_json(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d4_evidence()
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def generate_report_markdown(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d4_evidence()
    lines = [
        "# LC4V4D4 Composed Integration Evidence",
        "",
        f"- Source commit: `{report["source_commit"]}`",
        f"- Report hash: `{report["report_hash"]}`",
        f"- D2 report hash: `{report["d2_report_hash"]}`",
        f"- D3 report hash: `{report["d3_report_hash"]}`",
        f"- D3 selection hash: `{report["d3_selection_hash"]}`",
        f"- Legacy 60-probe baseline hash: `{report["legacy_60_baseline_hash"]}`",
        f"- Cases: {report["total_cases"]}",
        f"- Complete observations: {report["total_observations"]}",
        f"- Decision: `{report["decision"]}`",
        "",
        "## Gates",
        "",
    ]
    for name, passed in report["gates"].items():
        lines.append(f"- {name}: `{passed}`")
    lines.extend(["", "## Categories", ""])
    for name, counts in sorted(report["category_counts"].items()):
        lines.append(f"- {name}: {counts["passed"]} passed, {counts["failed"]} failed")
    lines.extend(["", "## Incompatible D1 cases (versioned overlay differences)", ""])
    for case_id in report.get("incompatible_d1_cases", []):
        lines.append(f"- {case_id}")
    lines.extend(["", "## Boundary", "",
        "D4 is an explicitly versioned overlay on the composed deterministic ",
        "development harness.  Frozen D1/D2/D3 evidence is unchanged.  ",
        "Holdouts v1-v4, T3, providers, product runtime, and write authority ",
        "remain closed.  The evidence overlay maps only the exact 20 accepted ",
        "development IDs."])
    return "\n".join(lines)


__all__ = [
    "SCHEMA_VERSION",
    "D3_TARGET_IDS",
    "EXPECTED_D2_REPORT_HASH",
    "EXPECTED_D3_REPORT_HASH",
    "EXPECTED_20_CASE_HASH",
    "EXPECTED_LEGACY_60_HASH",
    "run_d4_evidence",
    "generate_report_json",
    "generate_report_markdown",
]
