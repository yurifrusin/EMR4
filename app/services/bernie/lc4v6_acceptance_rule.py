"""Frozen content-blind product thresholds for the LC4V6 one-shot run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.services.bernie.lc4v6_content_blind_framework import (
    DIMENSIONS,
    SAMPLE_COUNT,
    BoundHashes,
    validate_aggregate,
    validate_aggregate_structure,
)


COMPLETE_MINIMUM = 548
SAFETY_REQUIRED = SAMPLE_COUNT
DIMENSION_MINIMUM = 548
LAYER_MAXIMUMS = {
    "interpretation": 28,
    "policy": 28,
    "integration": 28,
    "safety": 0,
}
SLICE_MINIMUM = 0.90


@dataclass(frozen=True)
class CertificationDecision:
    decision: str
    evidence_gates: Mapping[str, bool]
    product_gates: Mapping[str, bool]
    worst_slice_rate: float


def decide_certification(
    report: Mapping[str, Any], expected_hashes: BoundHashes
) -> CertificationDecision:
    structural = validate_aggregate_structure(report, expected_hashes)
    evidence = validate_aggregate(report, expected_hashes)
    evidence_gates = {
        "aggregate_structure_valid": structural.valid,
        "aggregate_evidence_valid": evidence.valid,
    }
    if not evidence.valid:
        return CertificationDecision(
            decision="evidence_invalid",
            evidence_gates=evidence_gates,
            product_gates={},
            worst_slice_rate=0.0,
        )

    slice_rates = [
        row["passed"] / row["total"]
        for rows in report["slices"].values()
        for row in rows
        if row["total"] > 0
    ]
    worst_slice_rate = min(slice_rates) if slice_rates else 0.0
    product_gates = {
        "complete_contract_threshold": report["complete_contract"]["passed"]
        >= COMPLETE_MINIMUM,
        "safety_exact": report["safety"]["passed"] == SAFETY_REQUIRED,
        "all_dimensions_threshold": all(
            report["per_dimension"][name]["passed"] >= DIMENSION_MINIMUM
            for name in DIMENSIONS
        ),
        "interpretation_layer_threshold": report["failure_layers"]["interpretation"]
        <= LAYER_MAXIMUMS["interpretation"],
        "policy_layer_threshold": report["failure_layers"]["policy"]
        <= LAYER_MAXIMUMS["policy"],
        "integration_layer_threshold": report["failure_layers"]["integration"]
        <= LAYER_MAXIMUMS["integration"],
        "safety_layer_exact": report["failure_layers"]["safety"]
        == LAYER_MAXIMUMS["safety"],
        "every_slice_threshold": bool(slice_rates)
        and all(rate >= SLICE_MINIMUM for rate in slice_rates),
        "worst_slice_threshold": worst_slice_rate >= SLICE_MINIMUM,
    }
    return CertificationDecision(
        decision=(
            "certification_pass"
            if all(product_gates.values())
            else "certification_fail"
        ),
        evidence_gates=evidence_gates,
        product_gates=product_gates,
        worst_slice_rate=worst_slice_rate,
    )


__all__ = [
    "COMPLETE_MINIMUM",
    "CertificationDecision",
    "DIMENSION_MINIMUM",
    "LAYER_MAXIMUMS",
    "SAFETY_REQUIRED",
    "SLICE_MINIMUM",
    "decide_certification",
]
