from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from scripts import reception_one_vertex_cost_budget as budget


ROOT = Path(__file__).resolve().parents[1]
POLICY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry"
    / "cost-policy.json"
)


def _write(path: Path, value: dict[str, object]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _audit(
    path: Path,
    *,
    prompt: int = 4633,
    candidates: int = 147,
    thoughts: int = 819,
) -> None:
    _write(
        path,
        {
            "attempt_id": "fresh-attempt-001",
            "ledger_id": "fresh-ledger-001",
            "provider_outcome": {
                "http_status": 200,
                "usage": {
                    "promptTokenCount": prompt,
                    "candidatesTokenCount": candidates,
                    "thoughtsTokenCount": thoughts,
                    "totalTokenCount": prompt + candidates + thoughts,
                },
            },
        },
    )


def test_predecessor_cost_is_exact() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    assert (
        budget.estimate_http_200_cost(
            input_tokens=4633,
            response_tokens=147,
            reasoning_tokens=819,
            policy=policy,
        )
        == Decimal("0.0038049")
    )


def test_reserve_and_settle_hash_chained_call(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    audit = tmp_path / "audit.json"
    _audit(audit, prompt=5000, candidates=200, thoughts=800)
    budget.reserve_call(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        purpose_hash="sha256:" + "1" * 64,
    )
    settled = budget.settle_call(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        external_audit_path=audit,
        admitted=True,
    )
    assert settled["terminal_success"] is True
    assert settled["fresh_calls_accounted"] == 1
    assert settled["calls_accounted"] == 2
    assert settled["outstanding_reservation"] == 0
    assert settled["accounted_cost"] == pytest.approx(0.0078049)
    budget.validate_ledger(policy_path=POLICY, ledger_path=ledger)


def test_second_reservation_after_admission_is_denied(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "ledger.json"
    audit = tmp_path / "audit.json"
    _audit(audit)
    budget.reserve_call(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        purpose_hash="sha256:" + "2" * 64,
    )
    budget.settle_call(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        external_audit_path=audit,
        admitted=True,
    )
    with pytest.raises(
        budget.CostBudgetError,
        match="cost_ledger_not_reservable",
    ):
        budget.reserve_call(
            policy_path=POLICY,
            ledger_path=ledger,
            reservation_id="retry-002",
            purpose_hash="sha256:" + "3" * 64,
        )


def test_usage_above_frozen_output_bound_is_rejected(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "ledger.json"
    audit = tmp_path / "audit.json"
    _audit(audit, prompt=5000, candidates=2049, thoughts=1024)
    budget.reserve_call(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        purpose_hash="sha256:" + "4" * 64,
    )
    with pytest.raises(
        budget.CostBudgetError,
        match="usage_output_exceeds_bound",
    ):
        budget.settle_call(
            policy_path=POLICY,
            ledger_path=ledger,
            reservation_id="retry-001",
            external_audit_path=audit,
            admitted=False,
        )


def test_unknown_usage_consumes_reservation_and_blocks(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "ledger.json"
    budget.reserve_call(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        purpose_hash="sha256:" + "5" * 64,
    )
    blocked = budget.block_unknown_usage(
        policy_path=POLICY,
        ledger_path=ledger,
        reservation_id="retry-001",
        reason_code="external_audit_missing",
    )
    assert blocked["blocked"] is True
    assert blocked["accounted_cost"] == pytest.approx(0.0238049)
    with pytest.raises(
        budget.CostBudgetError,
        match="cost_ledger_not_reservable",
    ):
        budget.reserve_call(
            policy_path=POLICY,
            ledger_path=ledger,
            reservation_id="retry-002",
            purpose_hash="sha256:" + "6" * 64,
        )


def test_successor_carries_preprovider_reservation_without_refund(
    tmp_path: Path,
) -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    policy["carried_forward_accounting"] = {
        "source_attempt_id": "preprovider-failure-001",
        "source_ledger_terminal_hash": "sha256:" + "7" * 64,
        "reason_code": "occupied_authority_missing",
        "provider_call_observed": False,
        "reservation_refunded": False,
        "amount": 0.02,
    }
    policy_path = tmp_path / "policy.json"
    ledger_path = tmp_path / "ledger.json"
    _write(policy_path, policy)

    reserved = budget.reserve_call(
        policy_path=policy_path,
        ledger_path=ledger_path,
        reservation_id="retry-002",
        purpose_hash="sha256:" + "8" * 64,
    )

    assert reserved["accounted_cost"] == pytest.approx(0.0238049)
    assert reserved["outstanding_reservation"] == 0.02
    assert reserved["calls_accounted"] == 2
    assert reserved["fresh_calls_accounted"] == 1
    assert [event["event_type"] for event in reserved["events"]] == [
        "predecessor_http_200_accounted",
        "preprovider_reservation_conservatively_carried_forward",
        "fresh_call_reserved",
    ]
