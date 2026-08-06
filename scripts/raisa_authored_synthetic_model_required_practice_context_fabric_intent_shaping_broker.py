#!/usr/bin/env python3
"""Run the one-use host broker for the model-required intent-shaping cell.

The intent-shaping cell is a single-lane, one-use rehearsal over the accepted
Context Fabric retrieval contract.  This broker reuses the accepted A3/B3
one-shot transport boundary (bearer-token HTTP, exact cell request, single-use
ledger, sanitized provider metadata and a chained audit) without modifying the
A3/B3 modules or artifacts.  ``dry-run`` exercises the identical parser,
wrapper and proofreader path with the canonical synthetic provider packet and
makes zero provider calls.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hmac
from typing import Any, Mapping

from scripts import model_required_bureau_a3_b3_broker as broker
from scripts import (
    raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts as contracts,
)


def _expected_open_ledger(state: broker.BrokerState) -> dict[str, Any]:
    request = state.expected_request
    live = state.mode == "live"
    return {
        "schema_version": "emr4.raisa_intent_shaping.single_use_ledger.v1",
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
        "schema_version": "emr4.raisa_intent_shaping.broker_audit_event.v1",
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
        "schema_version": "emr4.raisa_intent_shaping.broker_result.v1",
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


def _provider_request(self: broker.BrokerState) -> dict[str, Any]:
    return contracts.provider_request_for_attempt(
        self.context,
        attempt_number=self.expected_request["attempt_number"],
        correction_reason_code=self.expected_request[
            "correction_reason_code"
        ],
    )


def _validate_live_request_freshness(
    request: dict[str, Any],
    *,
    now: datetime,
) -> None:
    """Require the exact short-lived occupied request window.

    Provider-free fixtures remain deterministic and may carry their committed
    synthetic issuance window. Only live broker admission applies wall-clock
    freshness, independently of the controller that materialised the request.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise broker.BrokerError("live_request_clock_invalid")
    try:
        issued_at = datetime.fromisoformat(
            request["issued_at"].replace("Z", "+00:00")
        )
        expires_at = datetime.fromisoformat(
            request["expires_at"].replace("Z", "+00:00")
        )
    except (KeyError, TypeError, ValueError) as error:
        raise broker.BrokerError("live_request_window_invalid") from error
    now_utc = now.astimezone(timezone.utc)
    lifetime_seconds = int((expires_at - issued_at).total_seconds())
    if lifetime_seconds != contracts.LIVE_REQUEST_TTL_SECONDS:
        raise broker.BrokerError("live_request_lifetime_invalid")
    if not issued_at <= now_utc < expires_at:
        raise broker.BrokerError("live_request_not_fresh")


def _validate_request_and_context(self: broker.BrokerState) -> None:
    try:
        contracts.validate_instance(
            broker.REQUEST_SCHEMA_PATH, self.expected_request
        )
    except contracts.ContractError as error:
        raise broker.BrokerError("cell_request_schema_invalid") from error
    if self.expected_request["lane"] != self.lane:
        raise broker.BrokerError("lane_argument_mismatch")
    try:
        contracts.validate_intent_shaping_request(self.context)
    except contracts.ContractError as error:
        raise broker.BrokerError("context_invalid") from error
    if self.mode == "live":
        _validate_live_request_freshness(
            self.context,
            now=datetime.now(timezone.utc),
        )
    context_hash = contracts.prefixed_sha256(self.context)
    if not hmac.compare_digest(
        self.expected_request["context_hash"], context_hash
    ):
        raise broker.BrokerError("context_hash_mismatch")
    provider_request = self._provider_request()
    provider_hash = contracts.prefixed_sha256(provider_request)
    provider_request.clear()
    if not hmac.compare_digest(
        self.expected_request["provider_request_hash"], provider_hash
    ):
        raise broker.BrokerError("provider_request_hash_mismatch")


def _dry_run_packet(self: broker.BrokerState) -> dict[str, Any]:
    return contracts.build_dry_run_provider_packet()


def _execute(
    self: broker.BrokerState,
    request_packet: dict[str, Any],
) -> dict[str, Any]:
    self.claim_once()
    if request_packet != self.expected_request:
        raise broker.BrokerError("cell_request_not_exact")
    self.append_event(
        "request_admitted",
        {
            "lane": request_packet["lane"],
            "attempt_id": request_packet["attempt_id"],
            "ledger_id": request_packet["ledger_id"],
            "attempt_number": request_packet["attempt_number"],
            "correction_of": request_packet["correction_of"],
            "correction_reason_code": request_packet[
                "correction_reason_code"
            ],
            "policy_id": request_packet["policy_id"],
            "cell_request_hash": contracts.prefixed_sha256(request_packet),
            "context_hash": request_packet["context_hash"],
            "provider_request_hash": request_packet[
                "provider_request_hash"
            ],
        },
    )
    self.consume_ledger()
    provider_request = self._provider_request()
    actual_hash = contracts.prefixed_sha256(provider_request)
    if not hmac.compare_digest(
        actual_hash, request_packet["provider_request_hash"]
    ):
        provider_request.clear()
        raise broker.BrokerError("provider_request_hash_mismatch")
    self.append_event(
        "provider_request_constructed",
        {
            **broker._provider_binding(),
            "provider_request_hash": actual_hash,
            "response_schema_hash": contracts.prefixed_sha256(
                contracts.provider_response_schema()
            ),
            "raw_prompt_retained": False,
        },
    )

    if self.mode == "dry-run":
        provider_packet = self._dry_run_packet()
        call_metadata: dict[str, Any] = {
            "provider_contacted": False,
            "http_status": None,
            "latency_ms": 0,
            "discarded_provider_response_sha256": None,
            "provider_response_bytes": 0,
            "raw_provider_response_retained": False,
            "fixture_used": True,
        }
        self.append_event(
            "provider_call_simulated",
            {
                "provider_contacted": False,
                "fixture": "committed_selector_only_candidate",
            },
        )
    else:
        provider_packet, call_metadata = self._provider_call(provider_request)
        call_metadata["fixture_used"] = False
    provider_request.clear()

    bounded_metadata = contracts.bounded_provider_metadata(provider_packet)
    model_version = broker._safe_model_version(
        provider_packet.get("modelVersion")
    )
    sanitized_provider = {
        **call_metadata,
        **bounded_metadata,
        "model_version": model_version,
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
    }
    self.append_event(
        (
            "provider_call_completed"
            if self.mode == "live"
            else "provider_fixture_completed"
        ),
        sanitized_provider,
    )
    expected_model = (
        contracts.DRY_RUN_MODEL_VERSION
        if self.mode == "dry-run"
        else contracts.MODEL
    )
    if model_version != expected_model:
        provider_packet.clear()
        raise broker.BrokerError(
            "provider_model_version_mismatch",
            metadata={
                **call_metadata,
                "provider_metadata": sanitized_provider,
                "model_version": model_version,
            },
        )
    # Positive reported thinking-token use is acceptance evidence of the frozen
    # intelligence posture.  Missing, non-integer or non-positive counts in
    # live mode are a terminal pre-proof failure: the single-use ledger is
    # already consumed, nothing may be released, and the tranche cost ledger
    # reconciles the consumed call.  Dry-run remains eligible with zero tokens.
    if (
        self.mode == "live"
        and not contracts.positive_thinking_evidence(bounded_metadata)
    ):
        provider_packet.clear()
        raise broker.BrokerError(
            "positive_thinking_evidence_required",
            metadata={
                **call_metadata,
                "provider_metadata": sanitized_provider,
                "model_version": model_version,
            },
        )
    try:
        body = contracts.extract_provider_candidate(provider_packet)
    except contracts.ContractError as error:
        provider_packet.clear()
        raise broker.BrokerError(
            str(error).split(":", 1)[0],
            metadata={
                **call_metadata,
                "provider_metadata": sanitized_provider,
                "model_version": model_version,
            },
        )
    provider_packet.clear()
    model_authored_field_labels = contracts.bounded_body_field_labels(body)
    if self.mode == "dry-run":
        response_hash = contracts.prefixed_sha256(
            contracts.build_dry_run_provider_packet()
        )
    else:
        response_hash = call_metadata.get(
            "discarded_provider_response_sha256"
        ) or ("sha256:" + "0" * 64)
    provider_response_shape = {
        "candidate_count": bounded_metadata.get("candidate_count", 0),
        "finish_reason": bounded_metadata.get("finish_reason", "UNRECOGNIZED"),
        "parts_count": bounded_metadata.get("parts_count", 0),
    }
    try:
        envelope = contracts.wrap_provider_body(
            self.context,
            body,
            attempt_id=request_packet["attempt_id"],
            ledger_id=request_packet["ledger_id"],
            provider_request_hash=request_packet["provider_request_hash"],
            provider_response_hash=response_hash,
            provider_response_shape=provider_response_shape,
        )
    except contracts.ContractError as error:
        # A JSON object that fails the closed provider-body schema must reach
        # the structured proofreader so the single allowed
        # ``provider_body_schema_invalid`` correction stays eligible.  The
        # invalid object is hashed for the candidate digest and discarded.
        reason = str(error).split(":", 1)[0]
        proof = contracts.provider_body_rejection(body, reason)
        body.clear()
    else:
        proof = contracts.proofread(
            self.context, envelope, ground_to_case=True
        )
        body.clear()
        envelope.clear()

    proof_metadata = {
        "verdict": proof["verdict"],
        "reason_code": proof["reason_code"],
        "candidate_hash": proof["candidate_hash"],
        "correction_eligible": proof["correction_eligible"],
        "model_authored_field_labels": model_authored_field_labels,
    }
    self.append_event("proofreader_completed", proof_metadata)

    release = proof["released"] if proof["verdict"] == "admitted" else None
    if release is not None:
        self.append_event(
            "release_committed",
            {
                "release_hash": contracts.prefixed_sha256(release),
                "released_field_manifest": sorted(release),
                "atomic_release": True,
                "advisory_only": True,
                "product_read": False,
                "command": False,
                "write": False,
                "success": False,
            },
        )
    return {
        "status": "completed",
        "release": release,
        "proofreader": proof_metadata,
        "provider_metadata": sanitized_provider,
        "metadata": {
            **_base_metadata(self),
            "provider": sanitized_provider,
            "proofreader": proof_metadata,
        },
    }


def _configure() -> None:
    broker.contracts = contracts
    broker.REQUEST_SCHEMA_PATH = contracts.ARTIFACT_ROOT / "cell-request.schema.json"
    broker.LEDGER_SCHEMA_PATH = (
        contracts.ARTIFACT_ROOT / "single-use-ledger.schema.json"
    )
    broker.BrokerState._expected_open_ledger = _expected_open_ledger
    broker.BrokerState.append_event = _append_event
    broker.BrokerState._provider_request = _provider_request
    broker.BrokerState._validate_request_and_context = _validate_request_and_context
    broker.BrokerState._dry_run_packet = _dry_run_packet
    broker.BrokerState.execute = _execute
    broker._base_metadata = _base_metadata
    broker._safe_provider_metadata = _safe_provider_metadata


def main() -> int:
    _configure()
    return broker.main()


if __name__ == "__main__":
    raise SystemExit(main())
