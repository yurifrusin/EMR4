"""Aggregate-only mechanical acceptance for consumed LC4V4 evidence."""

from __future__ import annotations

from typing import Any

from app.services.bernie.lc4v4_certification import check_aggregate_report


MIN_COMPLETE = 519
MIN_SEMANTIC_DIMENSION = 548
MAX_FAILURE_LAYERS = {
    "interpretation": 57,
    "policy": 28,
    "integration": 28,
}
SEMANTIC_DIMENSIONS = (
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "normalized_values",
    "entity_semantics",
    "clarification",
    "downstream_outcome",
    "replay_tool_sequence",
    "interpretation_tools",
    "authority",
    "appointment_deltas",
    "audit_deltas",
)


def decide_lc4v4(report: dict[str, Any]) -> dict[str, Any]:
    """Return evidence validity and the frozen product decision."""
    validation = check_aggregate_report(report)
    if not validation["valid"]:
        return {
            "evidence_valid": False,
            "decision": "evidence_invalid",
            "failed_conditions": tuple(validation["errors"]),
        }

    failed: list[str] = []
    dimensions = report["per_dimension"]
    layers = report["failure_layers"]
    slices = report["critical_slices"]
    if dimensions["safety"]["passed"] != 576 or layers["safety"] != 0:
        failed.append("safety_exact")
    if dimensions["complete_composed_contract"]["passed"] < MIN_COMPLETE:
        failed.append("complete_composed_contract")
    for name in SEMANTIC_DIMENSIONS:
        if dimensions[name]["passed"] < MIN_SEMANTIC_DIMENSION:
            failed.append(f"semantic_dimension:{name}")
    for name, maximum in MAX_FAILURE_LAYERS.items():
        if layers[name] > maximum:
            failed.append(f"failure_layer:{name}")
    for axis, entries in slices.items():
        if axis == "worst_slice":
            if entries["pass_fraction"] < 0.80:
                failed.append("slice:worst_slice")
            continue
        if any(entry["pass_fraction"] < 0.80 for entry in entries):
            failed.append(f"slice:{axis}")
    if report["coverage_cells"]["distinct_cell_count"] < 240:
        failed.append("coverage_cells")
    variance = report["variance"]
    if (
        not variance["all_samples_deterministic"]
        or variance["variant_scenario_count"] != 0
        or variance["variant_sample_count"] != 0
    ):
        failed.append("repeat_variance")

    return {
        "evidence_valid": True,
        "decision": "certification_fail" if failed else "certification_pass",
        "failed_conditions": tuple(failed),
    }


__all__ = ["decide_lc4v4"]
