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
    run_diagnostic,
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


def _accepted_d3_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(D3_REPORT_PATH.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        return {}
    by_id = {
        case.get("probe_id"): case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("probe_id"), str)
    }
    return by_id if len(by_id) == len(cases) else {}


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
        and oa.claims_action_completed == le.claims_action_completed
        and oa.action_negated == le.action_negated
    )


def _matches_accepted_d3_policy(
    result: VersionedComposedResult,
    accepted_case: dict[str, Any],
) -> tuple[bool, str]:
    """Compare the complete D4 typed result with frozen accepted D3 output."""
    option_a = accepted_case.get("option_a", {})
    utterance = option_a.get("utterance", {})
    policy = option_a.get("policy", {})
    if not isinstance(utterance, dict) or not isinstance(policy, dict):
        return False, "accepted D3 case is incomplete"

    interp = result.interpretation
    replay = result.replay
    checks = {
        "intended_action": interp.intended_action == utterance.get("intended_action"),
        "action_semantics": interp.action_semantics == utterance.get("action_semantics"),
        "temporal_relation": interp.temporal_relation == utterance.get("temporal_relation"),
        "normalized_values": interp.normalized_values == utterance.get("normalized_values"),
        "entity_semantics": interp.entity_semantics == utterance.get("entity_semantics"),
        "action_negated": interp.action_negated == utterance.get("action_negated"),
        "requires_clarification": (
            interp.requires_clarification == policy.get("requires_clarification")
            and replay.requires_clarification == policy.get("requires_clarification")
        ),
        "clarification_choices": (
            list(interp.clarification_choices) == policy.get("clarification_choices")
            and list(replay.clarification_choices) == policy.get("clarification_choices")
        ),
        "selected_tools": (
            list(interp.selected_tool_sequence) == policy.get("selected_tools")
            and list(replay.tools_used) == policy.get("selected_tools")
        ),
        "authority": interp.authority_claim == policy.get("authority"),
        "downstream_outcome": replay.downstream_outcome == policy.get("downstream_outcome"),
        "appointment_deltas": list(replay.appointment_deltas) == policy.get("appointment_deltas"),
        "audit_deltas": list(replay.audit_deltas) == policy.get("audit_deltas"),
        "simulated_write": (
            replay.is_simulated_confirmed_write
            == policy.get("is_simulated_confirmed_write")
        ),
        "diary_relation": result.diary_relation == policy.get("diary_relation"),
        "conflicting_fields": (
            list(result.conflicting_fields) == policy.get("conflicting_fields")
        ),
        "resolved_patient": result.resolved_patient == policy.get("resolved_patient"),
        "resolved_practitioner": (
            result.resolved_practitioner == policy.get("resolved_practitioner")
        ),
        "resolved_practitioner_id": (
            result.resolved_practitioner_id == policy.get("resolved_practitioner_id")
        ),
        "forbidden_observations": (
            not replay.forbidden_outcomes_observed
            and not replay.forbidden_tools_observed
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    return not failed, "complete accepted D3 policy match" if not failed else ", ".join(failed)


def _legacy_option_differences(
    legacy: VersionedComposedResult,
    option_a: VersionedComposedResult,
) -> list[str]:
    pairs = {
        "interpretation.requires_clarification": (
            legacy.interpretation.requires_clarification,
            option_a.interpretation.requires_clarification,
        ),
        "interpretation.clarification_choices": (
            legacy.interpretation.clarification_choices,
            option_a.interpretation.clarification_choices,
        ),
        "interpretation.selected_tool_sequence": (
            legacy.interpretation.selected_tool_sequence,
            option_a.interpretation.selected_tool_sequence,
        ),
        "interpretation.authority_claim": (
            legacy.interpretation.authority_claim,
            option_a.interpretation.authority_claim,
        ),
        "replay.downstream_outcome": (
            legacy.replay.downstream_outcome,
            option_a.replay.downstream_outcome,
        ),
        "replay.tools_used": (legacy.replay.tools_used, option_a.replay.tools_used),
        "replay.appointment_deltas": (
            legacy.replay.appointment_deltas,
            option_a.replay.appointment_deltas,
        ),
        "replay.audit_deltas": (legacy.replay.audit_deltas, option_a.replay.audit_deltas),
        "diary_relation": (legacy.diary_relation, option_a.diary_relation),
        "conflicting_fields": (legacy.conflicting_fields, option_a.conflicting_fields),
    }
    return [name for name, values in pairs.items() if values[0] != values[1]]


def _result_payload(result: VersionedComposedResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["policy_version"] = result.policy_version.value
    return payload


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
    probes = _probes_by_id()
    diagnostic = run_diagnostic(list(probes.values()), source_commit=source_commit)
    actual_policy_ids = tuple(sorted(
        item.probe_id
        for item in diagnostic.probe_results
        if item.classification == "policy_contract_gap"
    ))
    g_exact_population = (
        actual_policy_ids == tuple(sorted(D3_TARGET_IDS))
        and len(actual_policy_ids) == 20
    )
    current_selection_hash = _selection_hash(actual_policy_ids)
    g_selection_valid = current_selection_hash == EXPECTED_20_CASE_HASH
    accepted_cases = _accepted_d3_cases()
    g_d3_case_population = (
        set(accepted_cases) == set(D3_TARGET_IDS)
        and len(accepted_cases) == 20
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
    incompatible_differences: list[dict[str, Any]] = []

    for probe_id in D3_TARGET_IDS:
        spec = _spec_from_id(probe_id)
        legacy = compose_versioned(
            spec, sample_index=0, policy_version=PolicyVersion.LEGACY,
        )
        r1 = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        r2 = compose_versioned(spec, sample_index=0, policy_version=PolicyVersion.OPTION_A)
        first_payload = _result_payload(r1)
        second_payload = _result_payload(r2)
        fp1 = _payload_hash(first_payload)
        fp2 = _payload_hash(second_payload)
        target_fingerprints.extend([fp1, fp2])
        overlay_passed, overlay_reason = _check_option_a_overlay(probe_id, r1)
        accepted_passed, accepted_reason = _matches_accepted_d3_policy(
            r1, accepted_cases.get(probe_id, {}),
        )
        semantic_preserved = _check_utterance_fields_unchanged(r1, legacy)
        passed = overlay_passed and accepted_passed and semantic_preserved
        cat = _category(probe_id)
        differences = _legacy_option_differences(legacy, r1)
        if probe_id in INCOMPATIBLE_D1_CASES:
            incompatible_differences.append({
                "probe_id": probe_id,
                "differences": differences,
            })
        option_a_results.append({
            "probe_id": probe_id,
            "category": cat,
            "passed": passed,
            "overlay_passed": overlay_passed,
            "overlay_reason": overlay_reason,
            "accepted_d3_match": accepted_passed,
            "accepted_d3_reason": accepted_reason,
            "utterance_semantics_preserved": semantic_preserved,
            "legacy": _result_payload(legacy),
            "option_a": first_payload,
            "fingerprint_0": fp1,
            "fingerprint_1": fp2,
            "deterministic": fp1 == fp2,
        })

    g_all_pass = len(option_a_results) == 20 and all(r["passed"] for r in option_a_results)
    g_zero_variance = all(r["fingerprint_0"] == r["fingerprint_1"] for r in option_a_results)

    g_utterance_preserved = all(
        result["utterance_semantics_preserved"] for result in option_a_results
    )
    g_replay_exact = (
        g_d3_case_population
        and all(result["accepted_d3_match"] for result in option_a_results)
    )

    incompatible_by_id = {
        item["probe_id"]: item["differences"] for item in incompatible_differences
    }
    omitted_differences = set(incompatible_by_id.get(OMITTED_PRACTITIONER_ID, []))
    state_join_differences_valid = all(
        {"diary_relation", "conflicting_fields"}.issubset(
            set(incompatible_by_id.get(probe_id, []))
        )
        for probe_id in STATE_JOIN_ORACLE
    )
    g_incompatible_recorded = (
        set(incompatible_by_id) == set(INCOMPATIBLE_D1_CASES)
        and len(incompatible_by_id) == 6
        and {
            "interpretation.requires_clarification",
            "interpretation.selected_tool_sequence",
        }.issubset(omitted_differences)
        and state_join_differences_valid
    )

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
        "accepted_d3_case_population": g_d3_case_population,
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
        "current_policy_population_hash": current_selection_hash,
        "legacy_60_baseline_hash": EXPECTED_LEGACY_60_HASH,
        "total_cases": len(D3_TARGET_IDS),
        "total_observations": len(target_fingerprints),
        "category_counts": category_counts,
        "incompatible_d1_cases": sorted(INCOMPATIBLE_D1_CASES),
        "incompatible_d1_differences": incompatible_differences,
        "gates": gates,
        "cases": option_a_results,
    }
    report["decision"] = (
        "versioned_composed_integration_valid"
        if all(gates.values())
        else "revision_required"
    )
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
