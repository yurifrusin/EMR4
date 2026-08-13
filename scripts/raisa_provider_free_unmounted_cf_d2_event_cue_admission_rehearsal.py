"""Pure provider-free admission rehearsal for the accepted CF-D2 cue contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import raisa_provider_free_cf_d2_observability_first_event_cue_acceptance


PACKET_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal"
)
CONTRACT_PATH = PACKET_DIR / "admission-contract.json"
SCHEMA_PATH = PACKET_DIR / "admission-contract.schema.json"
PARENT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-cf-d2-observability-first-event-cue"
)
PARENT_CONTRACT_PATH = PARENT_DIR / "observability-contract.json"
PARENT_SCHEMA_PATH = PARENT_DIR / "observability-contract.schema.json"
API_SPINE_PATH = (
    ROOT / "docs" / "api-spine" / "async" / "durable-diary-event-cue-observability.yaml"
)

PARTITION = {
    "source_system": "authored-synthetic-diary",
    "practice_scope_digest": "sha256:practice-alpha",
    "event_family": "diary.appointment_status_changed",
}
SOURCE_EPOCH = "sha256:epoch-one"
CONSUMER_SCOPE = "reception_one_diary_projection"
CUE_REASONS = {
    "diary_status_may_have_changed",
    "diary_availability_may_have_changed",
}
REJECTION_REASONS = {
    "unsupported_event_schema",
    "unsupported_event_family",
    "policy_rejected",
}
CLASSIFICATIONS = {
    "cue_required",
    "suppressed_irrelevant",
    "rejected_unsupported",
}
RECONCILIATION_OUTCOMES = {
    "projection_unchanged",
    "projection_refreshed",
    "local_selection_or_proposal_cleared",
    "authorization_rejected",
    "source_unavailable",
    "stale_session",
}
SUCCESSFUL_RECONCILIATIONS = {
    "projection_unchanged",
    "projection_refreshed",
    "local_selection_or_proposal_cleared",
}
CANDIDATE_FIELDS = {
    "source_system",
    "practice_scope_digest",
    "event_family",
    "source_epoch",
    "source_position",
    "event_fingerprint",
    "classification",
    "reason_code",
    "create_required_obligation",
    "lease_generation",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _stable_id(prefix: str, *parts: object) -> str:
    return f"{prefix}:" + hashlib.sha256(
        "|".join(str(part) for part in parts).encode("utf-8")
    ).hexdigest()[:24]


class EventCueAdmissionState:
    """Ephemeral state model with no I/O, clock, environment or command surface."""

    def __init__(
        self,
        *,
        partition: dict[str, str] | None = None,
        source_epoch: str = SOURCE_EPOCH,
        lease_generation: int = 7,
    ) -> None:
        if lease_generation < 1:
            raise ValueError("lease_generation_must_be_positive")
        self.partition = dict(partition or PARTITION)
        self.source_epoch = source_epoch
        self.lease_generation = lease_generation
        self.observed_position = 0
        self.checkpoint_position = 0
        self.receipts: dict[int, dict[str, Any]] = {}
        self.obligations: dict[str, dict[str, Any]] = {}
        self.last_dispatch_state: str | None = None
        self.last_reconciliation_state: str | None = None

    def normalized(self) -> dict[str, Any]:
        return {
            "partition": dict(sorted(self.partition.items())),
            "source_epoch": self.source_epoch,
            "lease_generation": self.lease_generation,
            "observed_position": self.observed_position,
            "checkpoint_position": self.checkpoint_position,
            "receipts": [copy.deepcopy(self.receipts[key]) for key in sorted(self.receipts)],
            "obligations": [
                copy.deepcopy(self.obligations[key]) for key in sorted(self.obligations)
            ],
            "last_dispatch_state": self.last_dispatch_state,
            "last_reconciliation_state": self.last_reconciliation_state,
        }

    def digest(self) -> str:
        return _canonical_digest(self.normalized())

    def _result(
        self,
        status: str,
        *,
        before_digest: str,
        receipt_id: str | None = None,
        obligation_id: str | None = None,
        display_updated: bool = False,
    ) -> dict[str, Any]:
        after_digest = self.digest()
        return {
            "status": status,
            "receipt_id": receipt_id,
            "obligation_id": obligation_id,
            "checkpoint_position": self.checkpoint_position,
            "state_digest": after_digest,
            "state_unchanged": after_digest == before_digest,
            "display_updated": display_updated,
            "future_freshness_conferred": False,
        }

    def _advance_checkpoint(self) -> None:
        candidate = self.checkpoint_position + 1
        while candidate in self.receipts:
            receipt = self.receipts[candidate]
            if receipt["classification"] == "cue_required":
                obligation_id = receipt["obligation_id"]
                if not obligation_id or obligation_id not in self.obligations:
                    break
            self.checkpoint_position = candidate
            candidate += 1

    def observe(self, candidate: dict[str, Any]) -> dict[str, Any]:
        before = self.digest()
        if set(candidate) != CANDIDATE_FIELDS:
            return self._result("candidate_shape_rejected", before_digest=before)
        if any(
            not isinstance(candidate[field], str) or not candidate[field]
            for field in (
                "source_system",
                "practice_scope_digest",
                "event_family",
                "source_epoch",
                "event_fingerprint",
            )
        ):
            return self._result("candidate_value_rejected", before_digest=before)
        if any(candidate[field] != value for field, value in self.partition.items()):
            return self._result("partition_mismatch", before_digest=before)
        if candidate["source_epoch"] != self.source_epoch:
            return self._result("epoch_mismatch", before_digest=before)
        lease = candidate["lease_generation"]
        if not isinstance(lease, int) or isinstance(lease, bool) or lease < 1:
            return self._result("lease_generation_invalid", before_digest=before)
        if lease != self.lease_generation:
            return self._result("ownership_fenced", before_digest=before)
        position = candidate["source_position"]
        if not isinstance(position, int) or isinstance(position, bool) or position < 1:
            return self._result("source_position_invalid", before_digest=before)
        classification = candidate["classification"]
        if classification is None:
            return self._result("classification_gap", before_digest=before)
        if classification not in CLASSIFICATIONS:
            return self._result("classification_rejected", before_digest=before)
        reason = candidate["reason_code"]
        create_obligation = candidate["create_required_obligation"]
        if not isinstance(create_obligation, bool):
            return self._result("obligation_flag_invalid", before_digest=before)
        if classification == "cue_required":
            if reason not in CUE_REASONS:
                return self._result("reason_code_rejected", before_digest=before)
            if create_obligation is not True:
                return self._result("obligation_gap", before_digest=before)
        elif classification == "rejected_unsupported":
            if reason not in REJECTION_REASONS or create_obligation:
                return self._result("rejection_receipt_invalid", before_digest=before)
        elif reason is not None or create_obligation:
            return self._result("suppression_receipt_invalid", before_digest=before)

        occupied = self.receipts.get(position)
        identity = {
            "event_fingerprint": candidate["event_fingerprint"],
            "classification": classification,
            "reason_code": reason,
        }
        if occupied is not None:
            if all(occupied[key] == value for key, value in identity.items()):
                return self._result(
                    "duplicate_reused",
                    before_digest=before,
                    receipt_id=occupied["receipt_id"],
                    obligation_id=occupied["obligation_id"],
                )
            return self._result("identity_conflict", before_digest=before)

        receipt_id = _stable_id(
            "receipt",
            *self.partition.values(),
            self.source_epoch,
            position,
            candidate["event_fingerprint"],
        )
        obligation_id: str | None = None
        if classification == "cue_required":
            adjacent = [
                obligation
                for obligation in self.obligations.values()
                if obligation["state"] == "pending"
                and obligation["reason_code"] == reason
                and obligation["source_epoch"] == self.source_epoch
                and obligation["through_position"] + 1 == position
            ]
            if adjacent:
                obligation = sorted(adjacent, key=lambda item: item["from_position"])[-1]
                obligation["through_position"] = position
                obligation_id = obligation["obligation_id"]
            else:
                obligation_id = _stable_id(
                    "obligation",
                    *self.partition.values(),
                    self.source_epoch,
                    position,
                    reason,
                )
                self.obligations[obligation_id] = {
                    "cue_schema_version": "durable-diary-refresh-cue.v1",
                    "obligation_id": obligation_id,
                    "practice_scope_digest": self.partition["practice_scope_digest"],
                    "consumer_scope": CONSUMER_SCOPE,
                    "event_family": self.partition["event_family"],
                    "source_epoch": self.source_epoch,
                    "from_position": position,
                    "through_position": position,
                    "reason_code": reason,
                    "fresh_authorized_read_required": True,
                    "state": "pending",
                    "dispatch_attempt_count": 0,
                    "reconciliation": None,
                }
        self.receipts[position] = {
            "receipt_id": receipt_id,
            "source_position": position,
            "event_fingerprint": candidate["event_fingerprint"],
            "classification": classification,
            "reason_code": reason,
            "obligation_id": obligation_id,
        }
        self.observed_position = max(self.observed_position, position)
        self._advance_checkpoint()
        return self._result(
            "admitted",
            before_digest=before,
            receipt_id=receipt_id,
            obligation_id=obligation_id,
        )

    def dispatch(
        self, obligation_id: str, *, lease_generation: int, outcome: str
    ) -> dict[str, Any]:
        before = self.digest()
        if lease_generation != self.lease_generation:
            return self._result("ownership_fenced", before_digest=before)
        obligation = self.obligations.get(obligation_id)
        if obligation is None:
            return self._result("obligation_unknown", before_digest=before)
        if outcome not in {"delivered", "failed"}:
            return self._result("dispatch_outcome_rejected", before_digest=before)
        if obligation["state"] == "delivered":
            return self._result(
                "duplicate_delivery_reused",
                before_digest=before,
                obligation_id=obligation_id,
            )
        obligation["dispatch_attempt_count"] += 1
        self.last_dispatch_state = outcome
        if outcome == "delivered":
            obligation["state"] = "delivered"
        return self._result(
            "dispatch_recorded", before_digest=before, obligation_id=obligation_id
        )

    def reconcile(
        self,
        obligation_id: str,
        *,
        lease_generation: int,
        outcome: str,
        scope_authorized: bool,
        fresh_read_performed: bool,
    ) -> dict[str, Any]:
        before = self.digest()
        if lease_generation != self.lease_generation:
            return self._result("ownership_fenced", before_digest=before)
        obligation = self.obligations.get(obligation_id)
        if obligation is None or obligation["state"] != "delivered":
            return self._result("delivery_not_proved", before_digest=before)
        if outcome not in RECONCILIATION_OUTCOMES:
            return self._result("reconciliation_outcome_rejected", before_digest=before)
        if outcome in SUCCESSFUL_RECONCILIATIONS and not (
            scope_authorized and fresh_read_performed
        ):
            return self._result("fresh_read_required", before_digest=before)
        if outcome == "authorization_rejected" and (
            scope_authorized or fresh_read_performed
        ):
            return self._result("authorization_result_inconsistent", before_digest=before)
        if outcome == "source_unavailable" and (
            not scope_authorized or fresh_read_performed
        ):
            return self._result("fresh_read_failure_inconsistent", before_digest=before)
        if outcome == "stale_session" and (
            scope_authorized or fresh_read_performed
        ):
            return self._result("fresh_read_failure_inconsistent", before_digest=before)
        existing = obligation["reconciliation"]
        record = {
            "outcome": outcome,
            "scope_authorized": scope_authorized,
            "fresh_read_performed": fresh_read_performed,
            "acknowledgement": "one_fresh_read_attempt_only",
        }
        if existing is not None:
            if existing == record:
                return self._result(
                    "duplicate_reconciliation_reused",
                    before_digest=before,
                    obligation_id=obligation_id,
                )
            return self._result(
                "reconciliation_conflict",
                before_digest=before,
                obligation_id=obligation_id,
            )
        obligation["reconciliation"] = record
        self.last_reconciliation_state = outcome
        display_updated = outcome in {
            "projection_refreshed",
            "local_selection_or_proposal_cleared",
        }
        return self._result(
            "reconciliation_recorded",
            before_digest=before,
            obligation_id=obligation_id,
            display_updated=display_updated,
        )

    def lag(
        self, *, source_head_epoch: str | None, source_head_position: int | None
    ) -> dict[str, Any]:
        if source_head_epoch is None or source_head_position is None:
            return {"state": "unknown", "value": None}
        if source_head_epoch != self.source_epoch:
            return {"state": "epoch_mismatch", "value": None}
        if source_head_position < self.checkpoint_position:
            raise ValueError("source_head_before_checkpoint")
        return {
            "state": "exact",
            "value": source_head_position - self.checkpoint_position,
        }


def canonical_candidate(
    position: int,
    *,
    classification: str | None = "cue_required",
    reason_code: str | None = "diary_status_may_have_changed",
    create_required_obligation: bool = True,
    lease_generation: int = 7,
    fingerprint: str | None = None,
) -> dict[str, Any]:
    return {
        **PARTITION,
        "source_epoch": SOURCE_EPOCH,
        "source_position": position,
        "event_fingerprint": (
            fingerprint if fingerprint is not None else f"sha256:event-{position}"
        ),
        "classification": classification,
        "reason_code": reason_code,
        "create_required_obligation": create_required_obligation,
        "lease_generation": lease_generation,
    }


def _scenario(assertions: Callable[[], None]) -> dict[str, Any]:
    try:
        assertions()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        return {"status": "failed", "reason": str(error)}
    return {"status": "passed"}


def run_scenarios() -> dict[str, dict[str, Any]]:
    scenarios: dict[str, Callable[[], None]] = {}

    def scenario(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def register(function: Callable[[], None]) -> Callable[[], None]:
            scenarios[name] = function
            return function

        return register

    @scenario("contiguous_required")
    def _contiguous_required() -> None:
        state = EventCueAdmissionState()
        result = state.observe(canonical_candidate(1))
        assert result["status"] == "admitted"
        assert state.checkpoint_position == 1
        assert len(state.obligations) == 1

    @scenario("duplicate_reuses_receipt")
    def _duplicate_reuses_receipt() -> None:
        state = EventCueAdmissionState()
        first = state.observe(canonical_candidate(1))
        duplicate = state.observe(canonical_candidate(1))
        assert duplicate["status"] == "duplicate_reused"
        assert duplicate["receipt_id"] == first["receipt_id"]
        assert duplicate["obligation_id"] == first["obligation_id"]
        assert duplicate["state_unchanged"] is True

    @scenario("divergent_duplicate_conflicts")
    def _divergent_duplicate_conflicts() -> None:
        state = EventCueAdmissionState()
        state.observe(canonical_candidate(1))
        result = state.observe(canonical_candidate(1, fingerprint="sha256:divergent"))
        assert result["status"] == "identity_conflict"
        assert result["state_unchanged"] is True

    @scenario("out_of_order_gap_holds")
    def _out_of_order_gap_holds() -> None:
        state = EventCueAdmissionState()
        state.observe(canonical_candidate(3))
        assert state.observed_position == 3
        assert state.checkpoint_position == 0

    @scenario("gap_fill_advances")
    def _gap_fill_advances() -> None:
        state = EventCueAdmissionState()
        state.observe(canonical_candidate(3))
        state.observe(canonical_candidate(1))
        assert state.checkpoint_position == 1
        state.observe(canonical_candidate(2))
        assert state.checkpoint_position == 3

    @scenario("suppressed_terminal_advances")
    def _suppressed_terminal_advances() -> None:
        state = EventCueAdmissionState()
        state.observe(
            canonical_candidate(
                1,
                classification="suppressed_irrelevant",
                reason_code=None,
                create_required_obligation=False,
            )
        )
        assert state.checkpoint_position == 1
        assert not state.obligations

    @scenario("rejected_terminal_advances_without_cue")
    def _rejected_terminal_advances_without_cue() -> None:
        state = EventCueAdmissionState()
        state.observe(
            canonical_candidate(
                1,
                classification="rejected_unsupported",
                reason_code="unsupported_event_schema",
                create_required_obligation=False,
            )
        )
        assert state.checkpoint_position == 1
        assert not state.obligations

    @scenario("classification_gap_denied")
    def _classification_gap_denied() -> None:
        state = EventCueAdmissionState()
        result = state.observe(
            canonical_candidate(1, classification=None, reason_code=None)
        )
        assert result["status"] == "classification_gap"
        assert result["state_unchanged"] is True

    @scenario("obligation_gap_denied_atomically")
    def _obligation_gap_denied_atomically() -> None:
        state = EventCueAdmissionState()
        result = state.observe(
            canonical_candidate(1, create_required_obligation=False)
        )
        assert result["status"] == "obligation_gap"
        assert result["state_unchanged"] is True
        assert state.checkpoint_position == 0

    @scenario("contiguous_same_reason_coalesces")
    def _contiguous_same_reason_coalesces() -> None:
        state = EventCueAdmissionState()
        first = state.observe(canonical_candidate(1))
        second = state.observe(canonical_candidate(2))
        assert first["obligation_id"] == second["obligation_id"]
        obligation = state.obligations[first["obligation_id"]]
        assert (obligation["from_position"], obligation["through_position"]) == (1, 2)

    @scenario("different_reason_does_not_coalesce")
    def _different_reason_does_not_coalesce() -> None:
        state = EventCueAdmissionState()
        first = state.observe(canonical_candidate(1))
        second = state.observe(
            canonical_candidate(2, reason_code="diary_availability_may_have_changed")
        )
        assert first["obligation_id"] != second["obligation_id"]
        assert len(state.obligations) == 2

    @scenario("delivered_obligation_does_not_coalesce")
    def _delivered_obligation_does_not_coalesce() -> None:
        state = EventCueAdmissionState()
        first = state.observe(canonical_candidate(1))
        state.dispatch(first["obligation_id"], lease_generation=7, outcome="delivered")
        second = state.observe(canonical_candidate(2))
        assert first["obligation_id"] != second["obligation_id"]

    @scenario("stale_generation_fenced")
    def _stale_generation_fenced() -> None:
        state = EventCueAdmissionState()
        result = state.observe(canonical_candidate(1, lease_generation=6))
        assert result["status"] == "ownership_fenced"
        assert result["state_unchanged"] is True

    @scenario("current_generation_admitted")
    def _current_generation_admitted() -> None:
        state = EventCueAdmissionState()
        assert state.observe(canonical_candidate(1))["status"] == "admitted"

    @scenario("source_head_unknown_lag")
    def _source_head_unknown_lag() -> None:
        state = EventCueAdmissionState()
        assert state.lag(source_head_epoch=None, source_head_position=None) == {
            "state": "unknown",
            "value": None,
        }

    @scenario("source_epoch_mismatch_lag")
    def _source_epoch_mismatch_lag() -> None:
        state = EventCueAdmissionState()
        assert state.lag(
            source_head_epoch="sha256:epoch-two", source_head_position=4
        ) == {"state": "epoch_mismatch", "value": None}

    @scenario("exact_lag")
    def _exact_lag() -> None:
        state = EventCueAdmissionState()
        state.observe(canonical_candidate(1))
        assert state.lag(
            source_head_epoch=SOURCE_EPOCH, source_head_position=4
        ) == {"state": "exact", "value": 3}

    def _delivered_state() -> tuple[EventCueAdmissionState, str]:
        state = EventCueAdmissionState()
        observed = state.observe(canonical_candidate(1))
        obligation_id = observed["obligation_id"]
        state.dispatch(obligation_id, lease_generation=7, outcome="delivered")
        return state, obligation_id

    @scenario("projection_refresh_requires_fresh_read")
    def _projection_refresh_requires_fresh_read() -> None:
        state, obligation_id = _delivered_state()
        denied = state.reconcile(
            obligation_id,
            lease_generation=7,
            outcome="projection_refreshed",
            scope_authorized=True,
            fresh_read_performed=False,
        )
        assert denied["status"] == "fresh_read_required"
        assert denied["state_unchanged"] is True
        accepted = state.reconcile(
            obligation_id,
            lease_generation=7,
            outcome="projection_refreshed",
            scope_authorized=True,
            fresh_read_performed=True,
        )
        assert accepted["status"] == "reconciliation_recorded"
        assert accepted["display_updated"] is True

    @scenario("authorization_rejected_retains_display")
    def _authorization_rejected_retains_display() -> None:
        state, obligation_id = _delivered_state()
        result = state.reconcile(
            obligation_id,
            lease_generation=7,
            outcome="authorization_rejected",
            scope_authorized=False,
            fresh_read_performed=False,
        )
        assert result["status"] == "reconciliation_recorded"
        assert result["display_updated"] is False

    @scenario("source_unavailable_retains_display")
    def _source_unavailable_retains_display() -> None:
        state, obligation_id = _delivered_state()
        result = state.reconcile(
            obligation_id,
            lease_generation=7,
            outcome="source_unavailable",
            scope_authorized=True,
            fresh_read_performed=False,
        )
        assert result["status"] == "reconciliation_recorded"
        assert result["display_updated"] is False

    @scenario("stale_session_retains_display")
    def _stale_session_retains_display() -> None:
        state, obligation_id = _delivered_state()
        result = state.reconcile(
            obligation_id,
            lease_generation=7,
            outcome="stale_session",
            scope_authorized=False,
            fresh_read_performed=False,
        )
        assert result["status"] == "reconciliation_recorded"
        assert result["display_updated"] is False

    @scenario("payload_field_rejected")
    def _payload_field_rejected() -> None:
        state = EventCueAdmissionState()
        candidate = canonical_candidate(1)
        candidate["appointment_id"] = "forbidden"
        result = state.observe(candidate)
        assert result["status"] == "candidate_shape_rejected"
        assert result["state_unchanged"] is True

    return {name: _scenario(function) for name, function in scenarios.items()}


def semantic_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract["execution"] != {
        "pure_in_memory_state_only": True,
        "clock_or_randomness": False,
        "environment_or_credential_lookup": False,
        "filesystem_from_state_machine": False,
        "database_source_or_network": False,
        "process_listener_worker_or_queue": False,
        "provider_call": False,
        "command_or_write": False,
    }:
        errors.append("execution_boundary_mismatch")
    if contract["authority"] != {
        "source_owns_current_truth": True,
        "event_and_cue_are_acceleration_hints_only": True,
        "cue_may_update_display_directly": False,
        "fresh_authorized_scoped_read_required": True,
        "command_rechecks_current_authority_and_source_truth": True,
    }:
        errors.append("authority_boundary_mismatch")
    candidate = contract["candidate"]
    if set(candidate["exact_fields"]) != CANDIDATE_FIELDS:
        errors.append("candidate_field_census_mismatch")
    if set(candidate["terminal_classifications"]) != CLASSIFICATIONS:
        errors.append("classification_census_mismatch")
    if set(candidate["reason_codes"]) != CUE_REASONS:
        errors.append("cue_reason_census_mismatch")
    if set(candidate["rejection_reason_codes"]) != REJECTION_REASONS:
        errors.append("rejection_reason_census_mismatch")
    if len(candidate["prohibited_fields"]) != 18:
        errors.append("prohibited_field_census_mismatch")
    invariants = contract["invariants"]
    expected_invariants = {
        "source_position_minimum": 1,
        "duplicate_returns_original_receipt_and_obligation": True,
        "divergent_identity_result": "identity_conflict",
        "denial_preserves_complete_state": True,
        "checkpoint_requires_contiguous_terminal_receipts": True,
        "cue_required_requires_atomic_obligation": True,
        "delivery_required_before_checkpoint": False,
        "rejected_event_creates_obligation": False,
        "coalescing": "contiguous_pending_same_partition_consumer_and_reason_only",
        "stale_generation_result": "ownership_fenced",
        "lag_states": ["exact", "unknown", "epoch_mismatch"],
        "acknowledgement_confers_future_freshness": False,
    }
    if invariants != expected_invariants:
        errors.append("invariant_boundary_mismatch")
    scenario_ids = contract["scenario_ids"]
    if len(scenario_ids) != 22 or len(set(scenario_ids)) != 22:
        errors.append("scenario_census_mismatch")
    if contract["evidence"] != {
        "normalized_state_only": True,
        "patient_or_product_payload": False,
        "operational_state_persisted": False,
        "denied_transition_state_digest_required": True,
        "scenario_count": 22,
        "minimum_hostile_rejections": 40,
    }:
        errors.append("evidence_boundary_mismatch")
    if len(contract["forbidden_effects"]) != 10:
        errors.append("forbidden_effect_census_mismatch")
    if contract["next_descendant"] != {
        "id": "provider-free-unmounted-event-cue-representation-architecture",
        "architecture_only": True,
        "database_connection": False,
        "migration_execution": False,
        "watcher_or_source": False,
        "restart_or_delivery": False,
    }:
        errors.append("next_descendant_broadens_authority")
    return errors


def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    Draft202012Validator.check_schema(schema)
    return sorted(
        error.message for error in Draft202012Validator(schema).iter_errors(contract)
    ) + semantic_errors(contract)


def _mutate(
    contract: dict[str, Any], path: tuple[Any, ...], value: Any
) -> dict[str, Any]:
    changed = copy.deepcopy(contract)
    cursor: Any = changed
    for component in path[:-1]:
        cursor = cursor[component]
    cursor[path[-1]] = value
    return changed


def hostile_contract_mutations(
    contract: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    cases: list[tuple[str, tuple[Any, ...], Any]] = [
        ("opens_clock", ("execution", "clock_or_randomness"), True),
        ("opens_environment", ("execution", "environment_or_credential_lookup"), True),
        ("opens_filesystem", ("execution", "filesystem_from_state_machine"), True),
        ("opens_database", ("execution", "database_source_or_network"), True),
        ("opens_worker", ("execution", "process_listener_worker_or_queue"), True),
        ("opens_provider", ("execution", "provider_call"), True),
        ("opens_command", ("execution", "command_or_write"), True),
        ("source_loses_truth", ("authority", "source_owns_current_truth"), False),
        ("cue_claims_truth", ("authority", "event_and_cue_are_acceleration_hints_only"), False),
        ("cue_updates_display", ("authority", "cue_may_update_display_directly"), True),
        ("fresh_read_optional", ("authority", "fresh_authorized_scoped_read_required"), False),
        ("command_skips_recheck", ("authority", "command_rechecks_current_authority_and_source_truth"), False),
        ("position_zero", ("invariants", "source_position_minimum"), 0),
        ("duplicate_new_identity", ("invariants", "duplicate_returns_original_receipt_and_obligation"), False),
        ("conflict_admitted", ("invariants", "divergent_identity_result"), "admitted"),
        ("denial_mutates", ("invariants", "denial_preserves_complete_state"), False),
        ("checkpoint_crosses_gap", ("invariants", "checkpoint_requires_contiguous_terminal_receipts"), False),
        ("obligation_non_atomic", ("invariants", "cue_required_requires_atomic_obligation"), False),
        ("delivery_gates_checkpoint", ("invariants", "delivery_required_before_checkpoint"), True),
        ("reject_creates_cue", ("invariants", "rejected_event_creates_obligation"), True),
        ("coalescing_broad", ("invariants", "coalescing"), "all_pending"),
        ("stale_owner_admitted", ("invariants", "stale_generation_result"), "admitted"),
        ("ack_confers_freshness", ("invariants", "acknowledgement_confers_future_freshness"), True),
        ("evidence_persists_state", ("evidence", "operational_state_persisted"), True),
        ("next_opens_database", ("next_descendant", "database_connection"), True),
        ("next_executes_migration", ("next_descendant", "migration_execution"), True),
        ("next_opens_watcher", ("next_descendant", "watcher_or_source"), True),
        ("next_claims_restart", ("next_descendant", "restart_or_delivery"), True),
    ]
    return [(name, _mutate(contract, path, value)) for name, path, value in cases]


def hostile_candidate_results() -> list[tuple[str, dict[str, Any]]]:
    cases: list[tuple[str, dict[str, Any], str]] = []
    for field in _load_json(CONTRACT_PATH)["candidate"]["prohibited_fields"]:
        candidate = canonical_candidate(1)
        candidate[field] = "forbidden"
        cases.append((f"prohibited:{field}", candidate, "candidate_shape_rejected"))
    malformed: list[tuple[str, dict[str, Any], str]] = [
        ("zero_position", canonical_candidate(0), "source_position_invalid"),
        ("boolean_position", canonical_candidate(True), "source_position_invalid"),
        ("stale_generation", canonical_candidate(1, lease_generation=6), "ownership_fenced"),
        ("invalid_classification", canonical_candidate(1, classification="accepted"), "classification_rejected"),
        ("classification_missing", canonical_candidate(1, classification=None, reason_code=None), "classification_gap"),
        ("required_reason_missing", canonical_candidate(1, reason_code=None), "reason_code_rejected"),
        ("required_obligation_missing", canonical_candidate(1, create_required_obligation=False), "obligation_gap"),
        ("reject_reason_missing", canonical_candidate(1, classification="rejected_unsupported", reason_code=None, create_required_obligation=False), "rejection_receipt_invalid"),
        ("suppression_has_reason", canonical_candidate(1, classification="suppressed_irrelevant", create_required_obligation=False), "suppression_receipt_invalid"),
        ("fingerprint_empty", canonical_candidate(1, fingerprint=""), "candidate_value_rejected"),
        ("epoch_wrong", {**canonical_candidate(1), "source_epoch": "sha256:other"}, "epoch_mismatch"),
        ("practice_wrong", {**canonical_candidate(1), "practice_scope_digest": "sha256:other"}, "partition_mismatch"),
        ("family_wrong", {**canonical_candidate(1), "event_family": "other.family"}, "partition_mismatch"),
        ("source_wrong", {**canonical_candidate(1), "source_system": "other-source"}, "partition_mismatch"),
    ]
    cases.extend(malformed)
    results: list[tuple[str, dict[str, Any]]] = []
    for name, candidate, expected_status in cases:
        state = EventCueAdmissionState()
        result = state.observe(candidate)
        results.append(
            (
                name,
                {
                    "expected_status": expected_status,
                    "observed_status": result["status"],
                    "state_unchanged": result["state_unchanged"],
                },
            )
        )
    return results


def _parent_errors() -> list[str]:
    parent = _load_json(PARENT_CONTRACT_PATH)
    schema = _load_json(PARENT_SCHEMA_PATH)
    api_contract = (
        raisa_provider_free_cf_d2_observability_first_event_cue_acceptance._load_yaml(
            API_SPINE_PATH
        )
    )
    return raisa_provider_free_cf_d2_observability_first_event_cue_acceptance.validate_contract(
        parent, schema, api_contract
    )


def build_report() -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    contract_errors = validate_contract(contract, schema)
    parent_errors = _parent_errors()
    scenarios = run_scenarios()
    scenario_ids = list(scenarios)
    scenario_errors = [
        name for name, result in scenarios.items() if result["status"] != "passed"
    ]
    if scenario_ids != contract["scenario_ids"]:
        scenario_errors.append("scenario_order_or_census_mismatch")
    admitted_contract_mutations = [
        name
        for name, mutation in hostile_contract_mutations(contract)
        if not validate_contract(mutation, schema)
    ]
    candidate_results = hostile_candidate_results()
    admitted_candidate_mutations = [
        name
        for name, result in candidate_results
        if result["observed_status"] != result["expected_status"]
        or result["state_unchanged"] is not True
    ]
    hostile_count = len(hostile_contract_mutations(contract)) + len(candidate_results)
    errors = contract_errors + parent_errors + scenario_errors
    if hostile_count < contract["evidence"]["minimum_hostile_rejections"]:
        errors.append("hostile_rejection_floor_not_met")
    return {
        "schema_version": "raisa.context_fabric.unmounted_event_cue_admission.evidence.v1",
        "status": "passed"
        if not errors
        and not admitted_contract_mutations
        and not admitted_candidate_mutations
        else "failed",
        "accepted_architecture_source": contract["accepted_architecture_source"],
        "planning_baseline": contract["planning_baseline"],
        "contract_errors": contract_errors,
        "parent_contract_errors": parent_errors,
        "scenario_count": len(scenarios),
        "scenario_errors": scenario_errors,
        "scenario_evidence_digest": _canonical_digest(scenarios),
        "hostile_rejection_count": hostile_count,
        "admitted_contract_mutations": admitted_contract_mutations,
        "admitted_candidate_mutations": admitted_candidate_mutations,
        "runtime_started": False,
        "database_or_source_opened": False,
        "operational_state_persisted": False,
        "provider_calls": 0,
        "product_patient_or_clinical_data": False,
        "command_or_write": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
