from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_authored_synthetic_time_ordered_canonical_check_in_context_branch_composition_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def evidence() -> dict:
    return rehearsal.run_rehearsal(ROOT)


def _contract() -> dict:
    return json.loads((ROOT / rehearsal.CONTRACT_PATH).read_text(encoding="utf-8"))


def test_frozen_exact_contract_and_product_bindings_pass() -> None:
    contract = _contract()

    rehearsal.validate_contract(contract, ROOT)

    assert contract["exact_bindings"] == rehearsal.EXACT_BINDINGS
    assert rehearsal._git_blob(ROOT, rehearsal.ADAPTER_PATH) == rehearsal.EXACT_BINDINGS["adapter_git_blob"]
    assert rehearsal._git_blob(ROOT, rehearsal.ADAPTER_TEST_PATH) == rehearsal.EXACT_BINDINGS["accepted_adapter_test_git_blob"]


def test_thirty_cases_are_the_pairwise_lower_bound_and_cover_all_74_pairs() -> None:
    pairs = rehearsal.pairwise_sets()

    assert len(pairs["source_authority"]) == 20
    assert len(pairs["source_outcome"]) == 30
    assert len(pairs["authority_outcome"]) == 24
    assert sum(map(len, pairs.values())) == 74
    assert len(rehearsal.SOURCE_AXIS) * len(rehearsal.OUTCOME_AXIS) == 30
    assert len(rehearsal.SOURCE_AXIS) * len(rehearsal.AUTHORITY_AXIS) * len(rehearsal.OUTCOME_AXIS) == 120
    assert all(set(row) == set(range(4)) for row in rehearsal.AUTHORITY_MATRIX)
    assert all(
        {rehearsal.AUTHORITY_MATRIX[row][column] for row in range(5)} == set(range(4))
        for column in range(6)
    )


def test_all_scenarios_match_typed_results_callbacks_and_readback(evidence: dict) -> None:
    assert evidence["decision"] == rehearsal.DECISION
    assert evidence["pairwise_coverage"]["scenario_count"] == 30
    assert evidence["pairwise_coverage"]["required_cross_family_pair_count"] == 74
    assert len(evidence["scenario_results"]) == 30
    assert all(
        item["expected_adapter_result"] == item["observed_adapter_result"]
        for item in evidence["scenario_results"]
    )
    assert all(item["initial_state"] and item["intervening_changes"] for item in evidence["scenario_results"])


def test_every_axis_and_outcome_has_an_unmasked_witness(evidence: dict) -> None:
    assert evidence["unmasked_witnesses"] == {
        key: True for key in rehearsal.WITNESS_CELLS
    }
    assert evidence["idempotency_submode_counts"] == {
        "conflict": 3,
        "in_progress": 2,
    }


def test_replay_precommit_and_uncertain_outcomes_remain_fail_closed(evidence: dict) -> None:
    by_cell = {tuple(item["cell"]): item for item in evidence["scenario_results"]}

    replay = by_cell[rehearsal.WITNESS_CELLS["exact_replay"]]
    assert replay["callback_sequence"] == ["claim"]
    assert replay["replay_seed_created_through_same_adapter"] is True
    assert replay["readback_disposition"] == "exact_replay_without_lock_or_readback"

    precommit = by_cell[rehearsal.WITNESS_CELLS["precommit_failure"]]
    assert precommit["callback_sequence"][-1] == "rollback"
    assert precommit["readback_disposition"] == "rolled_back_to_transaction_entry"

    for key, reason in (
        ("commit_outcome_unknown", "commit_outcome_unknown"),
        ("committed_readback_unavailable", "committed_readback_unavailable"),
    ):
        item = by_cell[rehearsal.WITNESS_CELLS[key]]
        assert item["observed_adapter_result"] == {
            "kind": "stopped",
            "outcome": "outcome_unknown",
            "reason": reason,
            "committed": None,
        }


def test_all_hostile_contract_mutations_are_rejected(evidence: dict) -> None:
    contract = _contract()
    mutations = rehearsal.hostile_contract_mutations(contract)

    assert len(mutations) == 72
    assert evidence["hostile_contract_mutations_rejected"] == len(mutations)
    for mutation in mutations:
        with pytest.raises(rehearsal.RehearsalError):
            rehearsal.validate_contract(mutation, ROOT, check_git=False)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("exact_bindings", "planning_baseline"), rehearsal.EXACT_BINDINGS["planning_baseline"][:7]),
        (("exact_bindings", "accepted_predecessor_review_source"), "0" * 40),
        (("pairwise_proof", "scenario_count"), 31),
        (("axis_families", "source_and_waiting_area_transition"), ["free_form"]),
        (("closed_boundaries", "historical_fixture_control_archive_or_local_data_access"), True),
    ],
)
def test_selected_contract_drift_fails_closed(path: tuple[str, str], value: object) -> None:
    contract = copy.deepcopy(_contract())
    contract[path[0]][path[1]] = value

    with pytest.raises(rehearsal.RehearsalError):
        rehearsal.validate_contract(contract, ROOT, check_git=False)


def test_rehearsal_reads_no_historical_or_local_data(monkeypatch: pytest.MonkeyPatch) -> None:
    original = Path.read_bytes
    observed: list[str] = []

    def guarded(path: Path) -> bytes:
        relative = str(path.resolve())
        assert "local_data" not in relative.lower()
        assert "historical-diary-trove" not in relative.lower()
        observed.append(relative)
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)

    evidence = rehearsal.run_rehearsal(ROOT)

    assert evidence["closed_boundaries"]["historical_or_local_data_accessed"] is False
    assert any(path.endswith("scenario-contract.json") for path in observed)
    assert any(path.endswith("authored-synthetic-successor-axis-contract.json") for path in observed)


def test_released_outputs_are_byte_deterministic_and_patient_free(evidence: dict) -> None:
    assert json.loads((ROOT / rehearsal.EVIDENCE_PATH).read_text(encoding="utf-8")) == evidence
    assert json.loads((ROOT / rehearsal.EFFICACY_PATH).read_text(encoding="utf-8")) == rehearsal.build_efficacy_reading(evidence)
    assert (ROOT / rehearsal.REPORT_PATH).read_text(encoding="utf-8") == rehearsal.render_report(evidence)

    serialized = json.dumps(evidence, sort_keys=True)
    for forbidden in rehearsal.FORBIDDEN_RELEASE_VALUES:
        assert forbidden not in serialized
    assert "historical_or_local_data_accessed" in serialized
    assert "result_reason_counts" in serialized


def test_closed_boundaries_and_zero_new_product_rules_are_explicit(evidence: dict) -> None:
    assert all(value is False for value in evidence["closed_boundaries"].values())
    efficacy = rehearsal.build_efficacy_reading(evidence)
    assert efficacy["utility"]["new_check_in_business_rules"] == 0
    assert efficacy["utility"]["product_files_changed"] == 0
    assert efficacy["utility"]["historical_data_reads"] == 0
    assert efficacy["utility"]["full_cross_product_avoided_cases"] == 90
