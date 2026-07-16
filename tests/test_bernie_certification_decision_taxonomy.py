from __future__ import annotations

import pytest

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)


def test_evidence_failure_has_precedence_over_product_gates() -> None:
    assert classify_certification(
        evidence_failures={"runtime_exceptions": 1},
        product_gate_failures={"complete": 0},
    ) == CERTIFICATION_INVALID
    assert classify_certification(
        evidence_failures={"runtime_exceptions": 1},
        product_gate_failures={"complete": 4},
    ) == CERTIFICATION_INVALID


@pytest.mark.parametrize("gate", ["complete", "policy_failures", "integration_failures"])
def test_valid_evidence_with_any_product_failure_is_certification_fail(
    gate: str,
) -> None:
    assert classify_certification(
        evidence_failures={"runtime_exceptions": 0, "variance": 0},
        product_gate_failures={gate: 1},
    ) == CERTIFICATION_FAIL


def test_valid_evidence_with_all_product_gates_clear_is_certification_pass() -> None:
    assert classify_certification(
        evidence_failures={"runtime_exceptions": 0, "variance": 0},
        product_gate_failures={
            "complete": 0,
            "policy_failures": 0,
            "integration_failures": 0,
        },
    ) == CERTIFICATION_PASS


@pytest.mark.parametrize(
    "bad_count",
    [-1, True, False, 1.5, "1", None],
)
def test_invalid_counts_fail_closed(bad_count: object) -> None:
    with pytest.raises(ValueError):
        classify_certification(
            evidence_failures={"variance": 0},
            product_gate_failures={"complete": bad_count},  # type: ignore[dict-item]
        )


def test_invalid_counter_collections_fail_closed() -> None:
    with pytest.raises(TypeError):
        classify_certification(
            evidence_failures=[],  # type: ignore[arg-type]
            product_gate_failures={},
        )
    with pytest.raises(ValueError):
        classify_certification(
            evidence_failures={"": 0},
            product_gate_failures={},
        )
