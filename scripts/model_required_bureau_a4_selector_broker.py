#!/usr/bin/env python3
"""Run the one-use host broker for the bounded A4 Rayleen selector."""

from __future__ import annotations

from typing import Any, Mapping

from scripts import model_required_bureau_a3_b3_broker as broker
from scripts import model_required_bureau_a4_selector_contracts as contracts


def _expected_open_ledger(
    state: broker.BrokerState,
) -> dict[str, Any]:
    request = state.expected_request
    live = state.mode == "live"
    return {
        "schema_version": "emr4.model_required_bureau_a4.single_use_ledger.v1",
        "ledger_id": request["ledger_id"],
        "attempt_id": request["attempt_id"],
        "lane": request["lane"],
        "policy_id": contracts.POLICY_ID,
        "status": "open",
        "maximum_provider_calls": 1 if live else 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": (
            contracts.RESERVED_COST_PER_CALL_USD if live else 0
        ),
        "fallback_permitted": False,
    }


def _append_event(
    state: broker.BrokerState,
    event_type: str,
    fields: Mapping[str, Any],
) -> None:
    previous_hash = (
        state.events[-1]["event_hash"] if state.events else broker.ZERO_HASH
    )
    event_without_hash = {
        "schema_version": "emr4.model_required_bureau_a4.broker_audit_event.v1",
        "sequence": len(state.events) + 1,
        "previous_hash": previous_hash,
        "event_type": event_type,
        "fields": dict(fields),
    }
    event = {
        **event_without_hash,
        "event_hash": contracts.prefixed_sha256(event_without_hash),
    }
    state.events.append(event)
    with state.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(contracts.canonical_bytes(event).decode("utf-8") + "\n")


def _base_metadata(state: broker.BrokerState) -> dict[str, Any]:
    request = state.expected_request
    return {
        "schema_version": "emr4.model_required_bureau_a4.broker_result.v1",
        "mode": state.mode,
        "lane": request["lane"],
        "attempt_id": request["attempt_id"],
        "ledger_id": request["ledger_id"],
        "attempt_number": request["attempt_number"],
        "correction_of": request["correction_of"],
        "correction_reason_code": request["correction_reason_code"],
        "policy_id": request["policy_id"],
        "context_hash": request["context_hash"],
        "provider_request_hash": request["provider_request_hash"],
        "provider_binding": broker._provider_binding(),
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "credential_or_token_retained": False,
        "product_or_database_access": False,
        "command_or_write_performed": False,
        "fallback_used": False,
    }


_PARENT_SAFE_PROVIDER_METADATA = broker._safe_provider_metadata


def _safe_provider_metadata(value: Any) -> dict[str, Any]:
    safe = _PARENT_SAFE_PROVIDER_METADATA(value)
    if not isinstance(value, dict):
        return safe
    for key in ("content_present",):
        if type(value.get(key)) is bool:
            safe[key] = value[key]
    for key in ("parts_count", "text_utf8_bytes"):
        item = value.get(key)
        if type(item) is int and item >= 0:
            safe[key] = item
    kinds = value.get("part_kinds")
    allowed_kinds = {
        "text",
        "thought",
        "function_call",
        "function_response",
        "data",
        "non_object",
        "unknown",
    }
    if (
        isinstance(kinds, list)
        and len(kinds) <= 32
        and all(
            isinstance(item, str) and item in allowed_kinds for item in kinds
        )
    ):
        safe["part_kinds"] = kinds
    return safe


def _configure() -> None:
    broker.contracts = contracts
    broker.REQUEST_SCHEMA_PATH = contracts.ARTIFACT_ROOT / "cell-request.schema.json"
    broker.LEDGER_SCHEMA_PATH = (
        contracts.ARTIFACT_ROOT / "single-use-ledger.schema.json"
    )
    broker.BrokerState._expected_open_ledger = _expected_open_ledger
    broker.BrokerState.append_event = _append_event
    broker._base_metadata = _base_metadata
    broker._safe_provider_metadata = _safe_provider_metadata


def main() -> int:
    _configure()
    return broker.main()


if __name__ == "__main__":
    raise SystemExit(main())
