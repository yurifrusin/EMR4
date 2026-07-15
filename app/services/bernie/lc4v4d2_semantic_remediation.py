"""LC4V4D2 ordinary-development semantic remediation evidence.

The D1 report is immutable historical evidence.  D2 validates that artifact,
quarantines three independently proved D1 authoring defects, and measures the
remaining twenty valid parser targets against the current deterministic path.
No holdout, replay policy, scorer policy, or write surface is opened here.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, replace
from typing import Any, Literal

from app.services.bernie.lc4v4_development_diagnostic import (
    EXPECTED_PROBE_COUNT,
    EXPECTED_REPEATS,
    author_all_probes,
    compute_fixture_hash,
    report_to_dict as d1_report_to_dict,
    run_diagnostic,
)

EXPECTED_FIXTURE_HASH = (
    "sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269"
)
EXPECTED_D1_REPORT_HASH = (
    "sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d"
)
EXPECTED_D1_SELECTION_HASH = (
    "sha256:1b254ae627e26b1b301b660628d90f39dce5e0364afc0cfcf4c4855fb6531f02"
)
EXPECTED_VALID_SELECTION_HASH = (
    "sha256:0badec28ad533b630786d245e5ab47dee5655b83239869f7d0a2d12a8935d105"
)

TARGET_23_IDS: tuple[str, ...] = (
    "lc4v4d1_entity_patient_omitted_02",
    "lc4v4d1_entity_patient_ambiguous_03",
    "lc4v4d1_entity_patient_negated_05",
    "lc4v4d1_entity_practitioner_ambiguous_09",
    "lc4v4d1_entity_practitioner_negated_11",
    "lc4v4d1_entity_location_ambiguous_15",
    "lc4v4d1_entity_location_negated_17",
    "lc4v4d1_entity_appt_type_ambiguous_21",
    "lc4v4d1_entity_appt_type_negated_23",
    "lc4v4d1_entity_duration_ambiguous_27",
    "lc4v4d1_entity_duration_corrected_28",
    "lc4v4d1_entity_duration_negated_29",
    "lc4v4d1_dialogue_clarification_multi_02",
    "lc4v4d1_dialogue_correction_single_03",
    "lc4v4d1_dialogue_reversal_single_05",
    "lc4v4d1_dialogue_ellipsis_multi_08",
    "lc4v4d1_dialogue_session_restart_multi_12",
    "lc4v4d1_safety_move_safe_03",
    "lc4v4d1_safety_move_unsafe_04",
    "lc4v4d1_safety_resize_safe_05",
    "lc4v4d1_safety_resize_unsafe_06",
    "lc4v4d1_safety_explain_safe_11",
    "lc4v4d1_safety_explain_unsafe_12",
)

QUARANTINED_D1_AUTHORING_IDS: tuple[str, ...] = (
    "lc4v4d1_entity_duration_corrected_28",
    "lc4v4d1_entity_duration_negated_29",
    "lc4v4d1_dialogue_ellipsis_multi_08",
)

VALID_TARGET_IDS: tuple[str, ...] = tuple(
    probe_id
    for probe_id in TARGET_23_IDS
    if probe_id not in frozenset(QUARANTINED_D1_AUTHORING_IDS)
)

MISMATCHED_DIARY_JOIN_IDS: tuple[str, ...] = (
    "lc4v4d1_entity_patient_mismatched_06",
    "lc4v4d1_entity_practitioner_mismatched_12",
    "lc4v4d1_entity_location_mismatched_18",
    "lc4v4d1_entity_appt_type_mismatched_24",
    "lc4v4d1_entity_duration_mismatched_30",
)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
D1_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d1-development-diagnostic.json"

Classification = Literal[
    "authoring_invalid",
    "parser_gap",
    "policy_contract_gap",
    "scorer_gap",
    "planned_unavailable",
    "supported_pass",
]


@dataclass(frozen=True)
class Transition:
    probe_id: str
    family: str
    before_classification: Classification
    after_classification: Classification
    before_mismatch_fields: tuple[str, ...]
    after_mismatch_fields: tuple[str, ...]
    semantic_fields_fixed: tuple[str, ...]


@dataclass(frozen=True)
class AuthoringQuarantine:
    probe_id: str
    defect: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class D2Report:
    source_commit: str
    report_hash: str
    d1_fixture_hash: str
    d1_report_hash: str
    d1_selection_hash: str
    valid_selection_hash: str
    total_probes: int
    total_observations: int
    raw_before_classifications: dict[str, int]
    adjusted_before_classifications: dict[str, int]
    raw_after_classifications: dict[str, int]
    adjusted_after_classifications: dict[str, int]
    transitions: tuple[Transition, ...]
    quarantines: tuple[AuthoringQuarantine, ...]
    valid_target_fixed_count: int
    remaining_valid_parser_ids: tuple[str, ...]
    quarantined_authoring_ids: tuple[str, ...]
    new_parser_gap_ids: tuple[str, ...]
    supported_regression_ids: tuple[str, ...]
    mismatched_join_regression_ids: tuple[str, ...]
    variance_count: int
    remediation_authorized_for_policy: bool = False


def _payload_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _selection_hash(ids: tuple[str, ...] | list[str]) -> str:
    # D1 deliberately used json.dumps' default separators for selection hashes.
    # Preserve that historical encoding instead of reusing the compact report
    # hash encoding.
    raw = json.dumps(sorted(ids), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _load_and_validate_d1_report() -> dict[str, Any]:
    payload = json.loads(D1_REPORT_PATH.read_text(encoding="utf-8"))
    embedded_hash = payload.get("report_hash")
    canonical = dict(payload)
    canonical.pop("report_hash", None)
    computed_hash = _payload_hash(canonical)
    if embedded_hash != EXPECTED_D1_REPORT_HASH or computed_hash != embedded_hash:
        raise ValueError("frozen D1 report hash validation failed")
    if payload.get("fixture_hash") != EXPECTED_FIXTURE_HASH:
        raise ValueError("frozen D1 fixture hash binding failed")
    if payload.get("candidate_selection_hash") != EXPECTED_D1_SELECTION_HASH:
        raise ValueError("frozen D1 selection hash binding failed")
    if tuple(payload.get("parser_gap_ids", ())) != TARGET_23_IDS:
        raise ValueError("frozen D1 parser ID population drifted")
    if payload.get("classifications") != {
        "authoring_invalid": 0,
        "parser_gap": 23,
        "policy_contract_gap": 12,
        "scorer_gap": 0,
        "planned_unavailable": 0,
        "supported_pass": 25,
    }:
        raise ValueError("frozen D1 classification population drifted")
    return payload


def _prove_authoring_quarantines(
    probes_by_id: dict[str, dict[str, Any]],
) -> tuple[AuthoringQuarantine, ...]:
    corrected = probes_by_id[QUARANTINED_D1_AUTHORING_IDS[0]]
    corrected_spans = corrected["source_spans"].get("duration", [])
    if not (
        corrected["duration_semantics"] == "corrected"
        and corrected["normalized_values"].get("duration_minutes") == 30
        and any(span["turn_index"] == 1 and span["text"] == "45" for span in corrected_spans)
        and corrected["source_spans"].get("correction_cue")
    ):
        raise ValueError("corrected-duration quarantine evidence drifted")

    negated = probes_by_id[QUARANTINED_D1_AUTHORING_IDS[1]]
    negated_spans = negated["source_spans"].get("duration", [])
    if not (
        negated["duration_semantics"] == "negated"
        and negated["normalized_values"].get("duration_minutes") == 30
        and any(span["text"] == "30" for span in negated_spans)
        and negated["source_spans"].get("negation_cue")
    ):
        raise ValueError("negated-duration quarantine evidence drifted")

    ellipsis = probes_by_id[QUARANTINED_D1_AUTHORING_IDS[2]]
    ellipsis_spans = ellipsis["source_spans"].get("duration", [])
    if not (
        ellipsis["duration_semantics"] == "omitted"
        and ellipsis["normalized_values"].get("duration_minutes") == 30
        and any(span["turn_index"] == 1 and span["text"] == "30" for span in ellipsis_spans)
    ):
        raise ValueError("ellipsis-duration quarantine evidence drifted")

    return (
        AuthoringQuarantine(
            probe_id=corrected["scenario_id"],
            defect="final corrected duration contradicts the frozen normalized value",
            evidence=(
                "surface correction supplies 45 minutes in turn 1",
                "oracle retains duration_minutes=30",
            ),
        ),
        AuthoringQuarantine(
            probe_id=negated["scenario_id"],
            defect="excluded duration is retained as the frozen normalized value",
            evidence=(
                "surface explicitly negates 30 minutes",
                "oracle retains duration_minutes=30 without a replacement",
            ),
        ),
        AuthoringQuarantine(
            probe_id=ellipsis["scenario_id"],
            defect="explicit second-turn duration is labelled omitted",
            evidence=(
                "turn 1 explicitly supplies 30 minutes",
                "oracle duration_semantics is omitted",
            ),
        ),
    )


def _interpretation_fields(result: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        field
        for field, layer in zip(
            result.get("mismatch_fields", ()), result.get("mismatch_layers", ()), strict=True,
        )
        if layer == "interpretation"
    )


def _decision(report: D2Report) -> str:
    valid = (
        report.total_probes == EXPECTED_PROBE_COUNT
        and report.total_observations
        == (EXPECTED_PROBE_COUNT - len(QUARANTINED_D1_AUTHORING_IDS)) * EXPECTED_REPEATS
        and len(report.quarantines) == 3
        and report.valid_target_fixed_count == len(VALID_TARGET_IDS)
        and not report.remaining_valid_parser_ids
        and set(report.quarantined_authoring_ids) == set(QUARANTINED_D1_AUTHORING_IDS)
        and not report.new_parser_gap_ids
        and not report.supported_regression_ids
        and not report.mismatched_join_regression_ids
        and report.variance_count == 0
        and not report.remediation_authorized_for_policy
    )
    return "semantic_remediation_valid_with_d1_quarantine" if valid else "revision_required"


def run_semantic_remediation(source_commit: str = "unknown") -> D2Report:
    baseline = _load_and_validate_d1_report()
    probes = author_all_probes()
    fixture_hash = compute_fixture_hash(probes)
    if fixture_hash != EXPECTED_FIXTURE_HASH or len(probes) != EXPECTED_PROBE_COUNT:
        raise ValueError("D1 fixture population or hash drifted")
    if _selection_hash(TARGET_23_IDS) != EXPECTED_D1_SELECTION_HASH:
        raise ValueError("D1 target selection hash drifted")
    if _selection_hash(VALID_TARGET_IDS) != EXPECTED_VALID_SELECTION_HASH:
        raise ValueError("valid target selection hash drifted")

    probes_by_id = {probe["scenario_id"]: probe for probe in probes}
    quarantines = _prove_authoring_quarantines(probes_by_id)
    after = run_diagnostic(probes, source_commit=source_commit)
    after_by_id = {result.probe_id: result for result in after.probe_results}
    before_by_id = {
        result["probe_id"]: result for result in baseline["probe_results"]
    }

    transitions: list[Transition] = []
    remaining_valid: list[str] = []
    for probe_id in VALID_TARGET_IDS:
        before = before_by_id[probe_id]
        current = after_by_id[probe_id]
        before_semantic = _interpretation_fields(before)
        after_semantic = tuple(
            field
            for field, layer in zip(
                current.mismatch_fields, current.mismatch_layers, strict=True,
            )
            if layer == "interpretation"
        )
        if after_semantic:
            remaining_valid.append(probe_id)
        transitions.append(Transition(
            probe_id=probe_id,
            family=current.family,
            before_classification=before["classification"],
            after_classification=current.classification,
            before_mismatch_fields=tuple(before["mismatch_fields"]),
            after_mismatch_fields=current.mismatch_fields,
            semantic_fields_fixed=tuple(
                field for field in before_semantic if field not in after_semantic
            ),
        ))

    raw_gap_ids = set(after.parser_gap_ids)
    quarantine_set = set(QUARANTINED_D1_AUTHORING_IDS)
    valid_set = set(VALID_TARGET_IDS)
    new_gap_ids = tuple(sorted(raw_gap_ids - quarantine_set - valid_set))
    quarantined_authoring_ids = tuple(sorted(
        probe_id
        for probe_id in quarantine_set
        if after_by_id[probe_id].classification == "authoring_invalid"
    ))

    historical_supported = {
        result["probe_id"]
        for result in baseline["probe_results"]
        if result["classification"] == "supported_pass"
    }
    supported_regressions = tuple(sorted(
        probe_id
        for probe_id in historical_supported
        if after_by_id[probe_id].classification != "supported_pass"
    ))
    join_regressions = tuple(sorted(
        probe_id
        for probe_id in MISMATCHED_DIARY_JOIN_IDS
        if after_by_id[probe_id].classification != "policy_contract_gap"
    ))

    raw_after = dict(after.classifications)
    adjusted_after = dict(raw_after)
    adjusted_before = dict(baseline["classifications"])
    adjusted_before["parser_gap"] -= len(quarantines)
    adjusted_before["authoring_invalid"] += len(quarantines)

    report = D2Report(
        source_commit=source_commit,
        report_hash="",
        d1_fixture_hash=fixture_hash,
        d1_report_hash=EXPECTED_D1_REPORT_HASH,
        d1_selection_hash=EXPECTED_D1_SELECTION_HASH,
        valid_selection_hash=EXPECTED_VALID_SELECTION_HASH,
        total_probes=len(probes),
        total_observations=after.total_observations,
        raw_before_classifications=dict(baseline["classifications"]),
        adjusted_before_classifications=adjusted_before,
        raw_after_classifications=raw_after,
        adjusted_after_classifications=adjusted_after,
        transitions=tuple(transitions),
        quarantines=quarantines,
        valid_target_fixed_count=len(VALID_TARGET_IDS) - len(remaining_valid),
        remaining_valid_parser_ids=tuple(sorted(remaining_valid)),
        quarantined_authoring_ids=quarantined_authoring_ids,
        new_parser_gap_ids=new_gap_ids,
        supported_regression_ids=supported_regressions,
        mismatched_join_regression_ids=join_regressions,
        variance_count=after.variance_count,
    )
    canonical = d2_report_to_dict(report)
    canonical.pop("report_hash", None)
    canonical.pop("decision", None)
    return replace(report, report_hash=_payload_hash(canonical))


def d2_report_to_dict(report: D2Report) -> dict[str, Any]:
    return {
        "schema_version": "lc4v4d2.semantic_remediation.v2",
        "source_commit": report.source_commit,
        "report_hash": report.report_hash,
        "d1_fixture_hash": report.d1_fixture_hash,
        "d1_report_hash": report.d1_report_hash,
        "d1_selection_hash": report.d1_selection_hash,
        "valid_selection_hash": report.valid_selection_hash,
        "total_probes": report.total_probes,
        "total_observations": report.total_observations,
        "raw_before_classifications": dict(report.raw_before_classifications),
        "adjusted_before_classifications": dict(report.adjusted_before_classifications),
        "raw_after_classifications": dict(report.raw_after_classifications),
        "adjusted_after_classifications": dict(report.adjusted_after_classifications),
        "transitions": [
            {
                "probe_id": item.probe_id,
                "family": item.family,
                "before_classification": item.before_classification,
                "after_classification": item.after_classification,
                "before_mismatch_fields": list(item.before_mismatch_fields),
                "after_mismatch_fields": list(item.after_mismatch_fields),
                "semantic_fields_fixed": list(item.semantic_fields_fixed),
            }
            for item in report.transitions
        ],
        "quarantines": [
            {
                "probe_id": item.probe_id,
                "defect": item.defect,
                "evidence": list(item.evidence),
            }
            for item in report.quarantines
        ],
        "valid_target_fixed_count": report.valid_target_fixed_count,
        "remaining_valid_parser_ids": list(report.remaining_valid_parser_ids),
        "quarantined_authoring_ids": list(report.quarantined_authoring_ids),
        "new_parser_gap_ids": list(report.new_parser_gap_ids),
        "supported_regression_ids": list(report.supported_regression_ids),
        "mismatched_join_regression_ids": list(report.mismatched_join_regression_ids),
        "variance_count": report.variance_count,
        "remediation_authorized_for_policy": report.remediation_authorized_for_policy,
        "decision": _decision(report),
    }


def d2_report_to_markdown(report: D2Report) -> str:
    lines = [
        "# LC4V4D2 Semantic Remediation Report",
        "",
        f"- Source commit: `{report.source_commit}`",
        f"- Report hash: `{report.report_hash}`",
        f"- Frozen D1 report hash: `{report.d1_report_hash}`",
        f"- Valid 20-case selection hash: `{report.valid_selection_hash}`",
        f"- Valid parser targets fixed: {report.valid_target_fixed_count}/{len(VALID_TARGET_IDS)}",
        f"- Two-repeat variance: {report.variance_count}",
        f"- Decision: `{_decision(report)}`",
        "",
        "## Classification reconciliation",
        "",
        "| View | Authoring invalid/quarantine | Parser gap | Policy gap | Supported |",
        "|---|---:|---:|---:|---:|",
        (
            f"| D1 raw | {report.raw_before_classifications['authoring_invalid']} | "
            f"{report.raw_before_classifications['parser_gap']} | "
            f"{report.raw_before_classifications['policy_contract_gap']} | "
            f"{report.raw_before_classifications['supported_pass']} |"
        ),
        (
            f"| D1 adjudicated | {report.adjusted_before_classifications['authoring_invalid']} | "
            f"{report.adjusted_before_classifications['parser_gap']} | "
            f"{report.adjusted_before_classifications['policy_contract_gap']} | "
            f"{report.adjusted_before_classifications['supported_pass']} |"
        ),
        (
            f"| D2 raw | {report.raw_after_classifications['authoring_invalid']} | "
            f"{report.raw_after_classifications['parser_gap']} | "
            f"{report.raw_after_classifications['policy_contract_gap']} | "
            f"{report.raw_after_classifications['supported_pass']} |"
        ),
        (
            f"| D2 adjudicated | {report.adjusted_after_classifications['authoring_invalid']} | "
            f"{report.adjusted_after_classifications['parser_gap']} | "
            f"{report.adjusted_after_classifications['policy_contract_gap']} | "
            f"{report.adjusted_after_classifications['supported_pass']} |"
        ),
        "",
        "## D1 authoring quarantine",
        "",
    ]
    for item in report.quarantines:
        lines.append(f"- `{item.probe_id}` — {item.defect}.")
    lines.extend([
        "",
        "The three frozen cases remain unchanged and are not counted as parser failures. "
        "A future versioned fixture correction requires a separate contract.",
        "",
        "## Valid target transitions",
        "",
    ])
    for item in report.transitions:
        lines.append(
            f"- `{item.probe_id}`: {item.before_classification} -> "
            f"{item.after_classification}; fixed semantic fields: "
            f"{', '.join(item.semantic_fields_fixed) or 'none'}"
        )
    lines.extend([
        "",
        "## Boundaries",
        "",
        "Policy/state-join remediation is not authorized. Holdouts v1-v4 remain sealed; "
        "no protected content, provider, route, database, UI, deployment, or write surface "
        "was opened.",
    ])
    return "\n".join(lines)


__all__ = [
    "D2Report",
    "Transition",
    "AuthoringQuarantine",
    "TARGET_23_IDS",
    "VALID_TARGET_IDS",
    "QUARANTINED_D1_AUTHORING_IDS",
    "EXPECTED_FIXTURE_HASH",
    "EXPECTED_D1_REPORT_HASH",
    "EXPECTED_D1_SELECTION_HASH",
    "EXPECTED_VALID_SELECTION_HASH",
    "run_semantic_remediation",
    "d2_report_to_dict",
    "d2_report_to_markdown",
]
