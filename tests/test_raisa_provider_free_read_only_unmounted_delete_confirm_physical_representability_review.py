from __future__ import annotations

import copy

import pytest

from scripts.raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review import (
    EVIDENCE_PATH,
    _json,
    build_hostile_mutations,
    run_acceptance,
    validate_review,
)


def test_canonical_review_passes_with_closed_counts() -> None:
    result = run_acceptance()

    assert result == {
        "result": "raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass",
        "source_count": 13,
        "physical_source_count": 10,
        "observation_count": 26,
        "domain_count": 6,
        "hostile_mutations_rejected": 52,
        "implementation_authorized": False,
        "overall_verdict": "implementation_not_admitted",
        "next_gate": "provider_free_unmounted_delete_confirm_physical_design_architecture",
    }


def test_all_hostile_mutations_fail_closed() -> None:
    evidence = _json(EVIDENCE_PATH)
    mutations = build_hostile_mutations(evidence)

    assert len(mutations) == 52
    for candidate in mutations:
        with pytest.raises(Exception):
            validate_review(candidate)


def test_every_domain_is_positive_without_admitting_implementation() -> None:
    evidence = _json(EVIDENCE_PATH)
    verdicts = {row["domain_id"]: row for row in evidence["domain_verdicts"]}

    assert evidence["implementation_authorized"] is False
    assert evidence["overall_verdict"] == "implementation_not_admitted"
    assert verdicts["appointment_truth_and_lock"]["verdict"] == "already_represented"
    assert {
        row["verdict"] for row in evidence["domain_verdicts"]
    } <= {"already_represented", "representable_with_additive_change"}
    for row in evidence["domain_verdicts"]:
        assert row["unselected_design_choices"]


def test_route_order_and_status_only_receipt_cannot_be_overclaimed() -> None:
    evidence = _json(EVIDENCE_PATH)
    observations = {row["observation_id"]: row for row in evidence["observations"]}

    assert "before locking the appointment" in observations["OBS-15"]["claim"]
    assert "status-confirm rather than delete-confirm" in observations["OBS-10"]["claim"]
    assert "does not advance appointment_state_version" in observations["OBS-18"]["claim"]

    overstated = copy.deepcopy(evidence)
    ordered = next(
        row
        for row in overstated["domain_verdicts"]
        if row["domain_id"] == "ordered_atomic_boundary"
    )
    ordered["verdict"] = "already_represented"
    with pytest.raises(ValueError, match="already represented"):
        validate_review(overstated)


def test_reason_and_readback_gaps_remain_explicit() -> None:
    evidence = _json(EVIDENCE_PATH)
    verdicts = {row["domain_id"]: row for row in evidence["domain_verdicts"]}

    reason_gaps = " ".join(
        verdicts["attributable_audit_and_exact_reasons"]["additive_gaps"]
    )
    assert "mandatory structured reason" in reason_gaps
    assert "nullable bounded free text" in reason_gaps

    readback_gaps = " ".join(
        verdicts["fresh_readback_separation"]["additive_gaps"]
    )
    assert "explicit appointment read action/resource" in readback_gaps
    assert "stored command receipt" in readback_gaps
