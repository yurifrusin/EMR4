"""Generic fail-closed certification decision taxonomy.

Evidence-procedure validity and product readiness are deliberately separate.
A valid run that misses a product gate is a certification failure, not invalid
evidence.  This module contains no corpus, scenario, or holdout knowledge.
"""

from __future__ import annotations

from collections.abc import Mapping


CERTIFICATION_INVALID = "certification_invalid"
CERTIFICATION_FAIL = "certification_fail"
CERTIFICATION_PASS = "certification_pass"


def _has_failures(counters: Mapping[str, int], *, label: str) -> bool:
    if not isinstance(counters, Mapping):
        raise TypeError(f"{label} must be a mapping")
    has_failures = False
    for name, count in counters.items():
        if not isinstance(name, str) or not name:
            raise ValueError(f"{label} names must be non-empty strings")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(
                f"{label}[{name!r}] must be a non-negative integer"
            )
        has_failures = has_failures or count > 0
    return has_failures


def classify_certification(
    *,
    evidence_failures: Mapping[str, int],
    product_gate_failures: Mapping[str, int],
) -> str:
    """Return the certification decision with evidence invalidity precedence."""
    if _has_failures(evidence_failures, label="evidence_failures"):
        return CERTIFICATION_INVALID
    if _has_failures(product_gate_failures, label="product_gate_failures"):
        return CERTIFICATION_FAIL
    return CERTIFICATION_PASS


__all__ = [
    "CERTIFICATION_FAIL",
    "CERTIFICATION_INVALID",
    "CERTIFICATION_PASS",
    "classify_certification",
]
