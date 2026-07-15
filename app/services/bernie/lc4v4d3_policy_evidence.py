"""Fail-closed LC4V4D3 Option A policy evidence."""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

from app.services.bernie.lc4v4_development_diagnostic import (
    author_all_probes,
    run_diagnostic,
)
from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.semantic_extraction import extract_semantics

EXPECTED_D2_REPORT_HASH = (
    "sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a"
)
EXPECTED_20_CASE_HASH = (
    "sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a"
)
SCHEMA_VERSION = "lc4v4d3.policy_resolution.v2"
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
D2_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d2-semantic-remediation.json"

D3_TARGET_IDS: tuple[str, ...] = (
    "lc4v4d1_entity_patient_ambiguous_03",
    "lc4v4d1_entity_practitioner_ambiguous_09",
    "lc4v4d1_entity_location_ambiguous_15",
    "lc4v4d1_entity_appt_type_ambiguous_21",
    "lc4v4d1_entity_duration_ambiguous_27",
    "lc4v4d1_entity_patient_corrected_04",
    "lc4v4d1_dialogue_correction_single_03",
    "lc4v4d1_entity_practitioner_omitted_08",
    "lc4v4d1_entity_practitioner_corrected_10",
    "lc4v4d1_dialogue_correction_multi_04",
    "lc4v4d1_entity_patient_mismatched_06",
    "lc4v4d1_entity_practitioner_mismatched_12",
    "lc4v4d1_entity_location_mismatched_18",
    "lc4v4d1_entity_appt_type_mismatched_24",
    "lc4v4d1_entity_duration_mismatched_30",
    "lc4v4d1_safety_create_unsafe_02",
    "lc4v4d1_safety_move_unsafe_04",
    "lc4v4d1_safety_resize_unsafe_06",
    "lc4v4d1_safety_cancel_unsafe_08",
    "lc4v4d1_safety_status_unsafe_10",
)

CHOICE_ORACLE: dict[str, tuple[str, ...]] = {
    "lc4v4d1_entity_patient_ambiguous_03": ("Sam Smith", "Avery Quinn"),
    "lc4v4d1_entity_practitioner_ambiguous_09": ("Dr Smith", "Dr Chen"),
    "lc4v4d1_entity_location_ambiguous_15": ("Room 2", "Room 5"),
    "lc4v4d1_entity_appt_type_ambiguous_21": (
        "standard consultation", "care plan appointment",
    ),
    "lc4v4d1_entity_duration_ambiguous_27": ("15 minutes", "30 minutes"),
}
CORRECTED_PATIENT_IDS = frozenset({
    "lc4v4d1_entity_patient_corrected_04",
    "lc4v4d1_dialogue_correction_single_03",
})
OMITTED_PRACTITIONER_ID = "lc4v4d1_entity_practitioner_omitted_08"
CORRECTED_PRACTITIONER_IDS = frozenset({
    "lc4v4d1_entity_practitioner_corrected_10",
    "lc4v4d1_dialogue_correction_multi_04",
})
STATE_JOIN_ORACLE: dict[str, str] = {
    "lc4v4d1_entity_patient_mismatched_06": "patient",
    "lc4v4d1_entity_practitioner_mismatched_12": "practitioner",
    "lc4v4d1_entity_location_mismatched_18": "location",
    "lc4v4d1_entity_appt_type_mismatched_24": "appointment_type",
    "lc4v4d1_entity_duration_mismatched_30": "duration",
}
UNSAFE_IDS = frozenset({
    "lc4v4d1_safety_create_unsafe_02",
    "lc4v4d1_safety_move_unsafe_04",
    "lc4v4d1_safety_resize_unsafe_06",
    "lc4v4d1_safety_cancel_unsafe_08",
    "lc4v4d1_safety_status_unsafe_10",
})


def _payload_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


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


def _probes_by_id() -> dict[str, dict[str, Any]]:
    return {probe["scenario_id"]: probe for probe in author_all_probes()}


def _legacy_observation(probe: dict[str, Any]) -> dict[str, Any]:
    utterances = [turn["utterance"] for turn in probe["dialogue_turns"]]
    extraction = extract_semantics(utterances, probe["reference_date"])
    return {
        "intended_action": extraction.intended_action,
        "action_semantics": extraction.action_semantics,
        "temporal_relation": extraction.temporal_relation,
        "normalized_values": dict(extraction.normalized_values),
        "entity_semantics": dict(extraction.entity_semantics),
        "requires_clarification": extraction.requires_clarification,
        "clarification_choices": list(extraction.clarification_choices),
        "selected_tool_sequence": list(extraction.selected_tool_sequence),
        "authority_claim": extraction.authority_claim,
        "action_negated": extraction.action_negated,
    }


def _policy_to_dict(policy: Any) -> dict[str, Any]:
    return {
        "requires_clarification": policy.requires_clarification,
        "clarification_choices": list(policy.clarification_choices),
        "resolved_patient": policy.resolved_patient,
        "resolved_practitioner": policy.resolved_practitioner,
        "resolved_practitioner_id": policy.resolved_practitioner_id,
        "selected_tools": list(policy.selected_tools),
        "authority": policy.authority,
        "diary_relation": policy.diary_comparison.relation,
        "conflicting_fields": list(policy.diary_comparison.conflicting_fields),
        "downstream_outcome": policy.downstream_outcome,
        "appointment_deltas": [dict(item) for item in policy.appointment_deltas],
        "audit_deltas": [dict(item) for item in policy.audit_deltas],
        "is_simulated_confirmed_write": policy.is_simulated_confirmed_write,
    }


def _run_d2(probe_id: str) -> dict[str, Any]:
    return _legacy_observation(_probes_by_id()[probe_id])


def _run_d3_option_a(probe_id: str) -> dict[str, Any]:
    probe = _probes_by_id()[probe_id]
    utterances = [turn["utterance"] for turn in probe["dialogue_turns"]]
    extraction = extract_semantics(utterances, probe["reference_date"])
    initial = probe.get("initial_diary_state", {})
    policy = resolve_policy(
        utterances=utterances,
        entity_semantics=dict(extraction.entity_semantics),
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=dict(extraction.normalized_values),
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        has_unsafe=extraction.action_semantics == "prohibited",
        action_negated=extraction.action_negated,
        diary_state=probe.get("diary_state"),
        diary_appointments=list(initial.get("appointments", [])),
        reference_date=probe["reference_date"],
    )
    return {
        "utterance": _legacy_observation(probe),
        "policy": _policy_to_dict(policy),
    }


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
    raise ValueError(f"unclassified D3 target: {probe_id}")


def _check_case(probe_id: str, result: dict[str, Any]) -> tuple[bool, str]:
    category = _category(probe_id)
    utterance = result["utterance"]
    policy = result["policy"]
    no_mutation = not policy["appointment_deltas"] and not policy["audit_deltas"]

    if category == "clarification_alternatives":
        expected = list(CHOICE_ORACLE[probe_id])
        passed = (
            policy["clarification_choices"] == expected
            and policy["requires_clarification"]
            and policy["selected_tools"] == ["request_clarification"]
            and no_mutation
        )
        return passed, f"choices={policy['clarification_choices']!r}"

    if category == "corrected_patient":
        passed = (
            policy["resolved_patient"] == "Avery Quinn"
            and policy["selected_tools"][:1] == ["search_patients"]
            and policy["downstream_outcome"] == "appointment_created"
        )
        return passed, (
            f"patient={policy['resolved_patient']!r}; "
            f"tools={policy['selected_tools']!r}"
        )

    if category == "corrected_practitioner":
        passed = (
            policy["resolved_practitioner"] == "Dr Chen"
            and policy["resolved_practitioner_id"] == "pr-004"
            and len(policy["appointment_deltas"]) == 1
            and policy["appointment_deltas"][0].get("practitioner_id") == "pr-004"
        )
        return passed, (
            f"practitioner={policy['resolved_practitioner']!r}; "
            f"id={policy['resolved_practitioner_id']!r}"
        )

    if category == "omitted_practitioner":
        passed = (
            utterance["entity_semantics"].get("practitioner") == "omitted"
            and policy["requires_clarification"]
            and policy["selected_tools"] == ["request_clarification"]
            and policy["resolved_practitioner_id"] is None
            and no_mutation
        )
        return passed, "omitted practitioner must clarify without mutation"

    if category == "diary_state_join":
        field = STATE_JOIN_ORACLE[probe_id]
        passed = (
            utterance["entity_semantics"].get(field) == "exact"
            and policy["diary_relation"] == "field_conflict"
            and policy["conflicting_fields"] == [field]
            and policy["requires_clarification"]
            and policy["selected_tools"] == ["request_clarification"]
            and no_mutation
        )
        return passed, (
            f"relation={policy['diary_relation']!r}; "
            f"fields={policy['conflicting_fields']!r}"
        )

    if category == "unsafe_bypass":
        passed = (
            utterance["action_semantics"] == "prohibited"
            and policy["selected_tools"] == ["refuse_instruction"]
            and policy["authority"] == "refuse"
            and policy["downstream_outcome"] == "instruction_refused"
            and no_mutation
        )
        return passed, f"tools={policy['selected_tools']!r}"

    raise AssertionError("unreachable")


def _decision(report: dict[str, Any]) -> str:
    gates = report["gates"]
    return (
        "option_a_policy_resolution_valid"
        if all(gates.values())
        else "revision_required"
    )


def run_d3_evidence(source_commit: str = "unknown") -> dict[str, Any]:
    probes = _probes_by_id()
    diagnostic = run_diagnostic(list(probes.values()), source_commit=source_commit)
    actual_policy_ids = tuple(sorted(
        result.probe_id
        for result in diagnostic.probe_results
        if result.classification == "policy_contract_gap"
    ))
    exact_ids = set(D3_TARGET_IDS) == set(actual_policy_ids) and len(D3_TARGET_IDS) == 20
    population_hash = _selection_hash(D3_TARGET_IDS)

    cases: list[dict[str, Any]] = []
    repeat_results: list[dict[str, Any]] = []
    category_counts: dict[str, dict[str, int]] = {}
    for probe_id in D3_TARGET_IDS:
        first = _run_d3_option_a(probe_id)
        second = _run_d3_option_a(probe_id)
        passed, reason = _check_case(probe_id, first)
        deterministic = _payload_hash(first) == _payload_hash(second)
        category = _category(probe_id)
        counts = category_counts.setdefault(category, {"passed": 0, "failed": 0})
        counts["passed" if passed else "failed"] += 1
        cases.append({
            "probe_id": probe_id,
            "category": category,
            "passed": passed,
            "reason": reason,
            "legacy": _run_d2(probe_id),
            "option_a": first,
            "repeat_fingerprints": [_payload_hash(first), _payload_hash(second)],
            "deterministic": deterministic,
        })
        repeat_results.extend([first, second])

    all_cases_pass = len(cases) == 20 and all(case["passed"] for case in cases)
    deterministic = len(repeat_results) == 40 and all(
        case["deterministic"] for case in cases
    )
    utterance_preserved = all(
        case["legacy"] == case["option_a"]["utterance"] for case in cases
    )
    no_forbidden_mutation = all(
        not case["option_a"]["policy"]["appointment_deltas"]
        and not case["option_a"]["policy"]["audit_deltas"]
        for case in cases
        if case["category"] in {
            "omitted_practitioner", "diary_state_join", "unsafe_bypass",
            "clarification_alternatives",
        }
    )

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "d2_report_hash": EXPECTED_D2_REPORT_HASH,
        "selection_hash": population_hash,
        "total_cases": len(cases),
        "total_observations": len(repeat_results),
        "category_counts": category_counts,
        "gates": {
            "d2_report_valid": _validate_d2_report(),
            "exact_policy_population": exact_ids,
            "selection_hash_valid": population_hash == EXPECTED_20_CASE_HASH,
            "all_20_cases_pass": all_cases_pass,
            "zero_variance": deterministic,
            "utterance_semantics_preserved": utterance_preserved,
            "no_forbidden_mutation": no_forbidden_mutation,
        },
        "cases": cases,
    }
    report["decision"] = _decision(report)
    canonical = dict(report)
    canonical.pop("decision", None)
    report["report_hash"] = _payload_hash(canonical)
    return report


def generate_report_json(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d3_evidence()
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def generate_report_markdown(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d3_evidence()
    lines = [
        "# LC4V4D3 Option A Policy Resolution Evidence",
        "",
        f"- Source commit: `{report['source_commit']}`",
        f"- Report hash: `{report['report_hash']}`",
        f"- Selection hash: `{report['selection_hash']}`",
        f"- Cases: {report['total_cases']}",
        f"- Complete observations: {report['total_observations']}",
        f"- Decision: `{report['decision']}`",
        "",
        "## Gates",
        "",
    ]
    for name, passed in report["gates"].items():
        lines.append(f"- {name}: `{passed}`")
    lines.extend(["", "## Categories", ""])
    for name, counts in sorted(report["category_counts"].items()):
        lines.append(f"- {name}: {counts['passed']} passed, {counts['failed']} failed")
    lines.extend([
        "",
        "## Boundary",
        "",
        "The Option A layer is explicitly versioned and development-only. Frozen D1/D2 "
        "evidence is unchanged. Holdouts v1-v4, T3, providers, product runtime, and "
        "write authority remain closed.",
    ])
    return "\n".join(lines)


__all__ = [
    "D3_TARGET_IDS",
    "EXPECTED_20_CASE_HASH",
    "EXPECTED_D2_REPORT_HASH",
    "run_d3_evidence",
    "generate_report_json",
    "generate_report_markdown",
    "_run_d2",
    "_run_d3_option_a",
]
