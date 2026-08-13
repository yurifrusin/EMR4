from __future__ import annotations

import inspect
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal as rehearsal


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal"
)
CONTRACT = BASE / "admission-contract.json"
SCHEMA = BASE / "admission-contract.schema.json"
EVIDENCE = BASE / "provider-free-unmounted-admission-evidence.json"
PLAN = (
    ROOT
    / "docs"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal-plan.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal-threat-model-delta.md"
)
LATCH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-active-operation-latch"
    / "current.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_schema_semantics_and_parent_contract_pass() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    assert rehearsal.validate_contract(contract, schema) == []
    assert rehearsal._parent_errors() == []


def test_all_frozen_scenarios_pass_in_exact_order() -> None:
    contract = _load(CONTRACT)
    results = rehearsal.run_scenarios()
    assert list(results) == contract["scenario_ids"]
    assert len(results) == 22
    assert {result["status"] for result in results.values()} == {"passed"}


def test_report_and_committed_evidence_are_exact() -> None:
    report = rehearsal.build_report()
    assert report == _load(EVIDENCE)
    assert report["status"] == "passed"
    assert report["scenario_count"] == 22
    assert report["hostile_rejection_count"] == 60
    assert report["admitted_contract_mutations"] == []
    assert report["admitted_candidate_mutations"] == []
    assert report["parent_contract_errors"] == []
    assert report["scenario_evidence_digest"].startswith("sha256:")


def test_every_denied_hostile_candidate_preserves_complete_state() -> None:
    results = rehearsal.hostile_candidate_results()
    assert len(results) == 32
    for _, result in results:
        assert result["observed_status"] == result["expected_status"]
        assert result["state_unchanged"] is True


def test_every_hostile_contract_mutation_fails_closed() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    mutations = rehearsal.hostile_contract_mutations(contract)
    assert len(mutations) == 28
    assert all(rehearsal.validate_contract(value, schema) for _, value in mutations)


def test_duplicate_reuses_original_receipt_and_obligation() -> None:
    state = rehearsal.EventCueAdmissionState()
    first = state.observe(rehearsal.canonical_candidate(1))
    duplicate = state.observe(rehearsal.canonical_candidate(1))
    assert duplicate["status"] == "duplicate_reused"
    assert duplicate["receipt_id"] == first["receipt_id"]
    assert duplicate["obligation_id"] == first["obligation_id"]
    assert duplicate["state_unchanged"] is True


def test_divergence_and_stale_fencing_are_byte_stable_denials() -> None:
    state = rehearsal.EventCueAdmissionState()
    state.observe(rehearsal.canonical_candidate(1))
    before = state.digest()
    conflict = state.observe(
        rehearsal.canonical_candidate(1, fingerprint="sha256:different")
    )
    fenced = state.observe(rehearsal.canonical_candidate(2, lease_generation=6))
    assert conflict["status"] == "identity_conflict"
    assert fenced["status"] == "ownership_fenced"
    assert conflict["state_digest"] == fenced["state_digest"] == before


def test_checkpoint_holds_at_gap_then_advances_across_terminal_receipts() -> None:
    state = rehearsal.EventCueAdmissionState()
    state.observe(rehearsal.canonical_candidate(3))
    assert state.checkpoint_position == 0
    state.observe(
        rehearsal.canonical_candidate(
            1,
            classification="suppressed_irrelevant",
            reason_code=None,
            create_required_obligation=False,
        )
    )
    assert state.checkpoint_position == 1
    state.observe(
        rehearsal.canonical_candidate(
            2,
            classification="rejected_unsupported",
            reason_code="policy_rejected",
            create_required_obligation=False,
        )
    )
    assert state.checkpoint_position == 3


def test_missing_required_obligation_is_atomic_denial() -> None:
    state = rehearsal.EventCueAdmissionState()
    before = state.normalized()
    result = state.observe(
        rehearsal.canonical_candidate(1, create_required_obligation=False)
    )
    assert result["status"] == "obligation_gap"
    assert state.normalized() == before
    assert state.checkpoint_position == 0


def test_coalescing_is_pending_adjacent_and_reason_scoped() -> None:
    state = rehearsal.EventCueAdmissionState()
    first = state.observe(rehearsal.canonical_candidate(1))
    second = state.observe(rehearsal.canonical_candidate(2))
    assert first["obligation_id"] == second["obligation_id"]
    obligation = state.obligations[first["obligation_id"]]
    assert obligation["from_position"] == 1
    assert obligation["through_position"] == 2
    state.dispatch(first["obligation_id"], lease_generation=7, outcome="delivered")
    third = state.observe(rehearsal.canonical_candidate(3))
    fourth = state.observe(
        rehearsal.canonical_candidate(
            4, reason_code="diary_availability_may_have_changed"
        )
    )
    assert third["obligation_id"] != first["obligation_id"]
    assert fourth["obligation_id"] != third["obligation_id"]


def test_lag_never_aliases_unknown_or_epoch_mismatch_to_zero() -> None:
    state = rehearsal.EventCueAdmissionState()
    assert state.lag(source_head_epoch=None, source_head_position=None) == {
        "state": "unknown",
        "value": None,
    }
    assert state.lag(
        source_head_epoch="sha256:other", source_head_position=0
    ) == {"state": "epoch_mismatch", "value": None}
    assert state.lag(
        source_head_epoch=rehearsal.SOURCE_EPOCH, source_head_position=0
    ) == {"state": "exact", "value": 0}


def test_reconciliation_requires_delivery_scope_and_fresh_read() -> None:
    state = rehearsal.EventCueAdmissionState()
    observed = state.observe(rehearsal.canonical_candidate(1))
    obligation_id = observed["obligation_id"]
    premature = state.reconcile(
        obligation_id,
        lease_generation=7,
        outcome="projection_refreshed",
        scope_authorized=True,
        fresh_read_performed=True,
    )
    assert premature["status"] == "delivery_not_proved"
    state.dispatch(obligation_id, lease_generation=7, outcome="delivered")
    no_read = state.reconcile(
        obligation_id,
        lease_generation=7,
        outcome="projection_refreshed",
        scope_authorized=True,
        fresh_read_performed=False,
    )
    assert no_read["status"] == "fresh_read_required"
    accepted = state.reconcile(
        obligation_id,
        lease_generation=7,
        outcome="projection_refreshed",
        scope_authorized=True,
        fresh_read_performed=True,
    )
    assert accepted["status"] == "reconciliation_recorded"
    assert accepted["display_updated"] is True
    assert accepted["future_freshness_conferred"] is False


def test_failed_reconciliation_shapes_are_typed_and_fail_closed() -> None:
    state = rehearsal.EventCueAdmissionState()
    observed = state.observe(rehearsal.canonical_candidate(1))
    obligation_id = observed["obligation_id"]
    state.dispatch(obligation_id, lease_generation=7, outcome="delivered")
    before = state.digest()
    inconsistent = state.reconcile(
        obligation_id,
        lease_generation=7,
        outcome="authorization_rejected",
        scope_authorized=False,
        fresh_read_performed=True,
    )
    assert inconsistent["status"] == "authorization_result_inconsistent"
    assert inconsistent["state_digest"] == before
    accepted = state.reconcile(
        obligation_id,
        lease_generation=7,
        outcome="source_unavailable",
        scope_authorized=True,
        fresh_read_performed=False,
    )
    assert accepted["status"] == "reconciliation_recorded"
    assert accepted["display_updated"] is False


def test_state_machine_has_no_io_runtime_or_command_surface() -> None:
    source = inspect.getsource(rehearsal.EventCueAdmissionState).lower()
    for forbidden in (
        "open(",
        "read_text",
        "write_text",
        "subprocess",
        "socket",
        "requests",
        "sqlalchemy",
        "psycopg",
        "os.environ",
        "time.",
        "random",
        "def command",
    ):
        assert forbidden not in source


def test_plan_and_threat_model_freeze_exact_closed_boundary() -> None:
    text = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for phrase in (
        "pure, deterministic",
        "no clock, randomness",
        "watcher/listener/worker runtime",
        "database/source",
        "no new or changed route",
        "source truth and command-time current-authority",
        "22 named scenarios",
        "at least 40 hostile",
        "patient/product/clinical data",
        "docs/branding/",
        "explicit-path only",
    ):
        assert phrase in text


def test_plan_and_threat_model_have_brisbane_timestamps() -> None:
    for path in (PLAN, THREAT):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_active_latch_has_transferred_to_the_representation_descendant() -> None:
    latch = _load(LATCH)
    assert latch["status"] == "in_progress"
    assert (
        latch["operation_id"]
        == "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
    )
    assert "write_verify_commit_notify_and_publish_closeout" in latch[
        "checkpoint"
    ]["next_executable_stage"]
    assert latch["terminal_response"]["permitted"] is False
