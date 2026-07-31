#!/usr/bin/env python3
"""Hash-chained cumulative cost gate for bounded Reception One Vertex calls."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from typing import Any


ZERO_HASH = "sha256:" + "0" * 64


class CostBudgetError(RuntimeError):
    """A pricing, usage, reservation or cumulative-budget rejection."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_object(path: Path, *, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CostBudgetError(code) from error
    if not isinstance(value, dict):
        raise CostBudgetError(code)
    return value


def _write_object(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _money(value: Any, *, code: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise CostBudgetError(code) from error
    if not result.is_finite() or result < 0:
        raise CostBudgetError(code)
    return result


def _integer(value: Any, *, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CostBudgetError(code)
    return value


def _money_json(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.0000000001")))


def _validate_policy(policy: dict[str, Any]) -> dict[str, Decimal | int]:
    rates = policy.get("rates_per_million_tokens")
    maxima = policy.get("bounded_request_maximums")
    pricing = policy.get("pricing_source")
    if (
        policy.get("schema_version") != "reception.one.vertex_cost_policy.v1"
        or not isinstance(rates, dict)
        or not isinstance(maxima, dict)
        or not isinstance(pricing, dict)
        or pricing.get("publisher") != "Google Cloud"
        or pricing.get("service_class") != "Gemini 2.5 Flash Standard"
        or pricing.get("only_http_200_token_billed") is not True
    ):
        raise CostBudgetError("cost_policy_invalid")
    values: dict[str, Decimal | int] = {
        "ceiling": _money(
            policy.get("cumulative_ceiling"),
            code="cost_ceiling_invalid",
        ),
        "reservation": _money(
            policy.get("pre_call_reservation"),
            code="cost_reservation_invalid",
        ),
        "input_rate": _money(
            rates.get("input_text_image_video"),
            code="cost_input_rate_invalid",
        ),
        "output_rate": _money(
            rates.get("output_response_and_reasoning"),
            code="cost_output_rate_invalid",
        ),
        "max_input": _integer(
            maxima.get("input_tokens"),
            code="cost_max_input_invalid",
        ),
        "max_output": _integer(
            maxima.get("output_response_and_reasoning_tokens"),
            code="cost_max_output_invalid",
        ),
    }
    if (
        values["ceiling"] != Decimal("1.0")
        or values["reservation"] != Decimal("0.02")
        or values["input_rate"] != Decimal("0.3")
        or values["output_rate"] != Decimal("2.5")
        or values["max_input"] != 16384
        or values["max_output"] != 3072
    ):
        raise CostBudgetError("cost_policy_not_frozen")
    maximum_cost = (
        Decimal(values["max_input"]) * Decimal(values["input_rate"])
        + Decimal(values["max_output"]) * Decimal(values["output_rate"])
    ) / Decimal(1_000_000)
    if maximum_cost > Decimal(values["reservation"]):
        raise CostBudgetError("cost_reservation_insufficient")
    return values


def estimate_http_200_cost(
    *,
    input_tokens: int,
    response_tokens: int,
    reasoning_tokens: int,
    policy: dict[str, Any],
) -> Decimal:
    values = _validate_policy(policy)
    prompt = _integer(input_tokens, code="usage_input_invalid")
    response = _integer(response_tokens, code="usage_response_invalid")
    reasoning = _integer(reasoning_tokens, code="usage_reasoning_invalid")
    output = response + reasoning
    if prompt > values["max_input"]:
        raise CostBudgetError("usage_input_exceeds_bound")
    if output > values["max_output"]:
        raise CostBudgetError("usage_output_exceeds_bound")
    return (
        Decimal(prompt) * Decimal(values["input_rate"])
        + Decimal(output) * Decimal(values["output_rate"])
    ) / Decimal(1_000_000)


def _append_event(
    ledger: dict[str, Any],
    event_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    events = ledger.get("events")
    if not isinstance(events, list):
        raise CostBudgetError("cost_ledger_events_invalid")
    previous_hash = events[-1]["event_hash"] if events else ZERO_HASH
    event = {
        "sequence": len(events) + 1,
        "event_type": event_type,
        "previous_hash": previous_hash,
        **payload,
    }
    event["event_hash"] = _canonical_hash(event)
    events.append(event)
    ledger["terminal_event_hash"] = event["event_hash"]
    return event


def initialize_ledger(*, policy_path: Path, ledger_path: Path) -> dict[str, Any]:
    if ledger_path.exists():
        raise CostBudgetError("cost_ledger_preexisted")
    policy = _load_object(policy_path, code="cost_policy_invalid")
    values = _validate_policy(policy)
    predecessor = policy.get("predecessor_accounting")
    if not isinstance(predecessor, dict):
        raise CostBudgetError("predecessor_cost_accounting_missing")
    cost = estimate_http_200_cost(
        input_tokens=_integer(
            predecessor.get("input_tokens"),
            code="predecessor_input_invalid",
        ),
        response_tokens=_integer(
            predecessor.get("response_tokens"),
            code="predecessor_response_invalid",
        ),
        reasoning_tokens=_integer(
            predecessor.get("reasoning_tokens"),
            code="predecessor_reasoning_invalid",
        ),
        policy=policy,
    )
    if cost != _money(
        predecessor.get("estimated_cost"),
        code="predecessor_cost_invalid",
    ):
        raise CostBudgetError("predecessor_cost_mismatch")
    ledger: dict[str, Any] = {
        "schema_version": "reception.one.vertex_cumulative_cost_ledger.v1",
        "currency": "USD",
        "cost_policy_sha256": _canonical_hash(policy),
        "ceiling": _money_json(Decimal(values["ceiling"])),
        "reservation_per_call": _money_json(
            Decimal(values["reservation"])
        ),
        "accounted_cost": _money_json(cost),
        "outstanding_reservation": 0.0,
        "calls_accounted": 1,
        "fresh_calls_accounted": 0,
        "terminal_success": False,
        "blocked": False,
        "events": [],
        "terminal_event_hash": ZERO_HASH,
    }
    _append_event(
        ledger,
        "predecessor_http_200_accounted",
        {
            "attempt_id": predecessor.get("attempt_id"),
            "http_status": 200,
            "usage": {
                "input_tokens": predecessor.get("input_tokens"),
                "response_tokens": predecessor.get("response_tokens"),
                "reasoning_tokens": predecessor.get("reasoning_tokens"),
            },
            "estimated_cost": _money_json(cost),
        },
    )
    carried = policy.get("carried_forward_accounting")
    if carried is not None:
        if not isinstance(carried, dict):
            raise CostBudgetError(
                "carried_forward_accounting_invalid"
            )
        amount = _money(
            carried.get("amount"),
            code="carried_forward_amount_invalid",
        )
        source_hash = carried.get("source_ledger_terminal_hash")
        if (
            amount != Decimal("0.02")
            or carried.get("provider_call_observed") is not False
            or carried.get("reservation_refunded") is not False
            or not isinstance(source_hash, str)
            or not source_hash.startswith("sha256:")
            or len(source_hash) != 71
        ):
            raise CostBudgetError(
                "carried_forward_accounting_invalid"
            )
        cost += amount
        if cost > Decimal(values["ceiling"]):
            raise CostBudgetError(
                "carried_forward_cost_exceeds_ceiling"
            )
        ledger["accounted_cost"] = _money_json(cost)
        ledger["calls_accounted"] = 2
        ledger["fresh_calls_accounted"] = 1
        _append_event(
            ledger,
            "preprovider_reservation_conservatively_carried_forward",
            {
                "source_attempt_id": carried.get(
                    "source_attempt_id"
                ),
                "source_ledger_terminal_hash": source_hash,
                "reason_code": carried.get("reason_code"),
                "provider_call_observed": False,
                "reservation_refunded": False,
                "amount": _money_json(amount),
                "accounted_cost_after": _money_json(cost),
            },
        )
    _write_object(ledger_path, ledger)
    return ledger


def validate_ledger(
    *,
    policy_path: Path,
    ledger_path: Path,
) -> dict[str, Any]:
    policy = _load_object(policy_path, code="cost_policy_invalid")
    values = _validate_policy(policy)
    ledger = _load_object(ledger_path, code="cost_ledger_invalid")
    if (
        ledger.get("schema_version")
        != "reception.one.vertex_cumulative_cost_ledger.v1"
        or ledger.get("cost_policy_sha256") != _canonical_hash(policy)
    ):
        raise CostBudgetError("cost_ledger_policy_mismatch")
    events = ledger.get("events")
    if not isinstance(events, list) or not events:
        raise CostBudgetError("cost_ledger_events_invalid")
    previous = ZERO_HASH
    for sequence, event in enumerate(events, start=1):
        if (
            not isinstance(event, dict)
            or event.get("sequence") != sequence
            or event.get("previous_hash") != previous
        ):
            raise CostBudgetError("cost_ledger_hash_chain_invalid")
        claimed = event.get("event_hash")
        unsigned = dict(event)
        unsigned.pop("event_hash", None)
        if claimed != _canonical_hash(unsigned):
            raise CostBudgetError("cost_ledger_hash_chain_invalid")
        previous = claimed
    if ledger.get("terminal_event_hash") != previous:
        raise CostBudgetError("cost_ledger_hash_chain_invalid")
    accounted = _money(
        ledger.get("accounted_cost"),
        code="cost_ledger_accounted_invalid",
    )
    outstanding = _money(
        ledger.get("outstanding_reservation"),
        code="cost_ledger_reservation_invalid",
    )
    if accounted + outstanding > Decimal(values["ceiling"]):
        raise CostBudgetError("cumulative_cost_ceiling_exceeded")
    return ledger


def reserve_call(
    *,
    policy_path: Path,
    ledger_path: Path,
    reservation_id: str,
    purpose_hash: str,
) -> dict[str, Any]:
    if not ledger_path.exists():
        initialize_ledger(policy_path=policy_path, ledger_path=ledger_path)
    policy = _load_object(policy_path, code="cost_policy_invalid")
    values = _validate_policy(policy)
    ledger = validate_ledger(
        policy_path=policy_path,
        ledger_path=ledger_path,
    )
    if (
        ledger.get("terminal_success") is True
        or ledger.get("blocked") is True
        or _money(
            ledger.get("outstanding_reservation"),
            code="cost_ledger_reservation_invalid",
        )
        != 0
    ):
        raise CostBudgetError("cost_ledger_not_reservable")
    if not isinstance(reservation_id, str) or not reservation_id:
        raise CostBudgetError("reservation_id_invalid")
    if not isinstance(purpose_hash, str) or not purpose_hash.startswith(
        "sha256:"
    ):
        raise CostBudgetError("reservation_purpose_hash_invalid")
    accounted = _money(
        ledger.get("accounted_cost"),
        code="cost_ledger_accounted_invalid",
    )
    reservation = Decimal(values["reservation"])
    if accounted + reservation > Decimal(values["ceiling"]):
        raise CostBudgetError("cumulative_cost_reservation_denied")
    ledger["outstanding_reservation"] = _money_json(reservation)
    _append_event(
        ledger,
        "fresh_call_reserved",
        {
            "reservation_id": reservation_id,
            "purpose_hash": purpose_hash,
            "reservation": _money_json(reservation),
            "accounted_cost_before": _money_json(accounted),
            "maximum_after_reservation": _money_json(
                accounted + reservation
            ),
        },
    )
    _write_object(ledger_path, ledger)
    return ledger


def _usage_from_audit(
    audit: dict[str, Any],
    *,
    policy: dict[str, Any],
) -> tuple[dict[str, int], Decimal]:
    outcome = audit.get("provider_outcome")
    if not isinstance(outcome, dict):
        raise CostBudgetError("provider_outcome_missing")
    status = outcome.get("http_status")
    if isinstance(status, bool) or not isinstance(status, int):
        raise CostBudgetError("provider_http_status_invalid")
    if status != 200:
        return {
            "input_tokens": 0,
            "response_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0,
        }, Decimal("0")
    usage = outcome.get("usage")
    if not isinstance(usage, dict):
        raise CostBudgetError("provider_usage_missing")
    prompt = _integer(
        usage.get("promptTokenCount"),
        code="provider_usage_input_invalid",
    )
    response = _integer(
        usage.get("candidatesTokenCount"),
        code="provider_usage_response_invalid",
    )
    reasoning = _integer(
        usage.get("thoughtsTokenCount", 0),
        code="provider_usage_reasoning_invalid",
    )
    total = _integer(
        usage.get("totalTokenCount"),
        code="provider_usage_total_invalid",
    )
    if total != prompt + response + reasoning:
        raise CostBudgetError("provider_usage_total_mismatch")
    cost = estimate_http_200_cost(
        input_tokens=prompt,
        response_tokens=response,
        reasoning_tokens=reasoning,
        policy=policy,
    )
    return {
        "input_tokens": prompt,
        "response_tokens": response,
        "reasoning_tokens": reasoning,
        "total_tokens": total,
    }, cost


def settle_call(
    *,
    policy_path: Path,
    ledger_path: Path,
    reservation_id: str,
    external_audit_path: Path,
    admitted: bool,
) -> dict[str, Any]:
    policy = _load_object(policy_path, code="cost_policy_invalid")
    values = _validate_policy(policy)
    ledger = validate_ledger(
        policy_path=policy_path,
        ledger_path=ledger_path,
    )
    outstanding = _money(
        ledger.get("outstanding_reservation"),
        code="cost_ledger_reservation_invalid",
    )
    if outstanding != Decimal(values["reservation"]):
        raise CostBudgetError("cost_reservation_missing")
    audit = _load_object(
        external_audit_path,
        code="provider_external_audit_invalid",
    )
    usage, cost = _usage_from_audit(audit, policy=policy)
    if cost > outstanding:
        raise CostBudgetError("observed_cost_exceeds_reservation")
    accounted = _money(
        ledger.get("accounted_cost"),
        code="cost_ledger_accounted_invalid",
    )
    if accounted + cost > Decimal(values["ceiling"]):
        raise CostBudgetError("cumulative_cost_ceiling_exceeded")
    ledger["accounted_cost"] = _money_json(accounted + cost)
    ledger["outstanding_reservation"] = 0.0
    ledger["calls_accounted"] = _integer(
        ledger.get("calls_accounted"),
        code="cost_calls_accounted_invalid",
    ) + 1
    ledger["fresh_calls_accounted"] = _integer(
        ledger.get("fresh_calls_accounted"),
        code="cost_fresh_calls_accounted_invalid",
    ) + 1
    ledger["terminal_success"] = bool(admitted)
    _append_event(
        ledger,
        "fresh_call_settled",
        {
            "reservation_id": reservation_id,
            "attempt_id": audit.get("attempt_id"),
            "ledger_id": audit.get("ledger_id"),
            "http_status": audit.get("provider_outcome", {}).get(
                "http_status"
            ),
            "usage": usage,
            "estimated_cost": _money_json(cost),
            "accounted_cost_after": _money_json(accounted + cost),
            "admitted": bool(admitted),
        },
    )
    _write_object(ledger_path, ledger)
    return ledger


def block_unknown_usage(
    *,
    policy_path: Path,
    ledger_path: Path,
    reservation_id: str,
    reason_code: str,
) -> dict[str, Any]:
    policy = _load_object(policy_path, code="cost_policy_invalid")
    values = _validate_policy(policy)
    ledger = validate_ledger(
        policy_path=policy_path,
        ledger_path=ledger_path,
    )
    reservation = _money(
        ledger.get("outstanding_reservation"),
        code="cost_ledger_reservation_invalid",
    )
    if reservation != Decimal(values["reservation"]):
        raise CostBudgetError("cost_reservation_missing")
    accounted = _money(
        ledger.get("accounted_cost"),
        code="cost_ledger_accounted_invalid",
    )
    if accounted + reservation > Decimal(values["ceiling"]):
        raise CostBudgetError("cumulative_cost_ceiling_exceeded")
    ledger["accounted_cost"] = _money_json(accounted + reservation)
    ledger["outstanding_reservation"] = 0.0
    ledger["calls_accounted"] = _integer(
        ledger.get("calls_accounted"),
        code="cost_calls_accounted_invalid",
    ) + 1
    ledger["fresh_calls_accounted"] = _integer(
        ledger.get("fresh_calls_accounted"),
        code="cost_fresh_calls_accounted_invalid",
    ) + 1
    ledger["blocked"] = True
    _append_event(
        ledger,
        "unknown_usage_reservation_consumed_and_blocked",
        {
            "reservation_id": reservation_id,
            "reason_code": reason_code,
            "estimated_cost": _money_json(reservation),
            "accounted_cost_after": _money_json(
                accounted + reservation
            ),
        },
    )
    _write_object(ledger_path, ledger)
    return ledger


__all__ = [
    "CostBudgetError",
    "block_unknown_usage",
    "estimate_http_200_cost",
    "initialize_ledger",
    "reserve_call",
    "settle_call",
    "validate_ledger",
]
