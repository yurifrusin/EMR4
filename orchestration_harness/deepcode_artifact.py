"""Compatibility adapter for canonical Deep Code artifact verdict parsing."""

from __future__ import annotations

from typing import Any

from orchestration_harness.verdict import parse_artifact_verdict


def parse_artifact_marker(body: str, artifact_kind: str = "decision") -> dict[str, Any]:
    """Preserve the legacy dictionary shape while delegating all semantics."""

    assessment = parse_artifact_verdict(body, artifact_kind)
    return {
        "valid": assessment.artifact_valid,
        "marker": assessment.canonical_marker,
        "reason": assessment.reason_code,
        "artifact_valid": assessment.artifact_valid,
        "review_verdict": assessment.review_verdict.value
        if assessment.review_verdict
        else None,
        "integration_authorized": assessment.integration_authorized,
    }
