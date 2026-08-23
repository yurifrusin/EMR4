"""Check, publish or roll back one generic live governance clockwork tick."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.governance_clockwork_tick import (
    BLOCKED_INTENT_VERSION,
    CHECKPOINT_INTENT_VERSION,
    USER_DECISION_INTENT_VERSION,
    ClockworkTickRejection,
    build_checkpoint_tick_generation,
    build_user_decision_tick_generation,
    build_tick_generation,
    build_blocked_tick_generation,
    publish_tick_generation,
    rollback_tick_generation,
    validate_blocked_tick_intent,
    validate_checkpoint_tick_intent,
    validate_tick_intent,
    validate_tick_live_state,
    validate_user_decision_tick_intent,
)
from orchestration_harness.governance_live_adoption import validate_contract
from orchestration_harness import transactional_closeout as tc


CONTRACT = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement/contract.json"
TRANSACTION_FACTS_VERSION = "ariadne.governance_command_transaction_facts.v1"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def _intent_path(raw: Path) -> Path:
    path = (ROOT / raw).resolve() if not raw.is_absolute() else raw.resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError("intent_path_escape") from error
    if not path.is_file() or path.name not in {
        "closeout-intent.json",
        "checkpoint-intent.json",
    }:
        raise ValueError("closed_tick_intent_required")
    return path


def _transaction_facts(
    *,
    disposition: str,
    preparations: int,
    preparation_rejections: int,
    publication_attempts: int,
    published_generations: int,
    rollback_attempts: int,
    byte_exact_rollbacks: int,
    idempotent_readbacks: int,
    base_lease_sequence: int,
    prospective_lease_sequence: int | None,
    result_lease_sequence: int,
    base_generation_id: str,
    prepared_generation_id: str | None,
    result_generation_id: str,
) -> dict[str, Any]:
    return {
        "schema_version": TRANSACTION_FACTS_VERSION,
        "command_disposition": disposition,
        "invocations": 1,
        "preparations": preparations,
        "preparation_rejections": preparation_rejections,
        "publication_attempts": publication_attempts,
        "published_generations": published_generations,
        "rollback_attempts": rollback_attempts,
        "byte_exact_rollbacks": byte_exact_rollbacks,
        "idempotent_readbacks": idempotent_readbacks,
        "base_lease_sequence": base_lease_sequence,
        "prospective_lease_sequence": prospective_lease_sequence,
        "result_lease_sequence": result_lease_sequence,
        "committed_lease_advance": result_lease_sequence - base_lease_sequence,
        "base_generation_id": base_generation_id,
        "prepared_generation_id": prepared_generation_id,
        "result_generation_id": result_generation_id,
    }


def _prepared_transaction_facts(
    prepared: dict[str, Any], *, published: bool
) -> dict[str, Any]:
    base = prepared["base_pointer"]
    target = prepared["pointer"]
    generation_id = prepared["generation_manifest"]["generation_id"]
    return _transaction_facts(
        disposition="publication_committed" if published else "dry_preparation",
        preparations=1,
        preparation_rejections=0,
        publication_attempts=int(published),
        published_generations=int(published),
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=0,
        base_lease_sequence=base["lease_sequence"],
        prospective_lease_sequence=target["lease_sequence"],
        result_lease_sequence=(
            target["lease_sequence"] if published else base["lease_sequence"]
        ),
        base_generation_id=base["selected_generation_id"],
        prepared_generation_id=generation_id,
        result_generation_id=(
            generation_id if published else base["selected_generation_id"]
        ),
    )


def _idempotent_transaction_facts(state: dict[str, Any]) -> dict[str, Any]:
    return _transaction_facts(
        disposition="idempotent_readback",
        preparations=0,
        preparation_rejections=0,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=1,
        base_lease_sequence=state["lease_sequence"],
        prospective_lease_sequence=None,
        result_lease_sequence=state["lease_sequence"],
        base_generation_id=state["generation_id"],
        prepared_generation_id=None,
        result_generation_id=state["generation_id"],
    )


def _rollback_transaction_facts(result: dict[str, Any]) -> dict[str, Any]:
    result_lease = result["lease_sequence"]
    return _transaction_facts(
        disposition="byte_exact_rollback",
        preparations=0,
        preparation_rejections=0,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=1,
        byte_exact_rollbacks=int(result["byte_exact"] is True),
        idempotent_readbacks=0,
        base_lease_sequence=result_lease - 1,
        prospective_lease_sequence=result_lease,
        result_lease_sequence=result_lease,
        base_generation_id=result["rolled_back_from_generation_id"],
        prepared_generation_id=None,
        result_generation_id=result["selected_generation_id"],
    )


def _command_result(
    result: dict[str, Any], transaction_facts: dict[str, Any]
) -> dict[str, Any]:
    return {
        **result,
        "transaction_facts": transaction_facts,
        "caller_authored_derived_fields": 0,
        "live_publication_count": transaction_facts["published_generations"],
        "bespoke_updater_executions": 0,
    }


def _prospective_rejection_result(
    error: ClockworkTickRejection,
) -> dict[str, Any]:
    prefix = "tick_prospective_current_node_evidence:"
    message = str(error)
    if not message.startswith(prefix):
        raise error
    state = validate_tick_live_state(ROOT, validate_contract(_load(CONTRACT)))
    transaction_facts = _transaction_facts(
        disposition="prospective_evidence_rejected",
        preparations=1,
        preparation_rejections=1,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=0,
        base_lease_sequence=state["lease_sequence"],
        prospective_lease_sequence=None,
        result_lease_sequence=state["lease_sequence"],
        base_generation_id=state["generation_id"],
        prepared_generation_id=None,
        result_generation_id=state["generation_id"],
    )
    errors = message.removeprefix(prefix).split(",")
    return _command_result(
        {
            "schema_version": (
                "ariadne.governance_prospective_evidence_rejection.v1"
            ),
            "status": "revision_required",
            "reason": "tick_prospective_current_node_evidence",
            "errors": errors,
            "error_count": len(errors),
            "source_commit": state["source_commit"],
            "generation_id": state["generation_id"],
            "previous_generation_id": state["previous_generation_id"],
            "lease_sequence": state["lease_sequence"],
        },
        transaction_facts,
    )


def _write_outputs(topic: Path, result: dict, *, prefix: str = "clockwork-tick") -> None:
    evidence = topic / f"{prefix}-evidence.json"
    report = topic / f"{prefix}-report.md"
    evidence.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report.write_text(
        "# Governance clockwork tick\n\n"
        f"Status: **{result['status']}**\n\n"
        f"Operation: `{result.get('operation_id', 'not-published')}`\n\n"
        f"Source: `{result['source_commit']}`\n\n"
        f"Generation: `{result['generation_id']}`\n\n"
        f"Previous generation: `{result['previous_generation_id']}`\n\n"
        f"Lease sequence: {result['lease_sequence']}\n\n"
        f"Command disposition: `{result['transaction_facts']['command_disposition']}`\n\n"
        f"Published generations: {result['transaction_facts']['published_generations']}\n\n"
        f"Byte-exact rollbacks: {result['transaction_facts']['byte_exact_rollbacks']}\n",
        encoding="utf-8",
        newline="\n",
    )


def _intent_identity(
    intent: dict, contract: dict
) -> tuple[str | None, str, str]:
    version = intent.get("schema_version")
    if version == BLOCKED_INTENT_VERSION:
        admitted = validate_blocked_tick_intent(intent, contract)
        return admitted["operation_id"], "blocked_transition", tc.sha256(admitted)
    if version == CHECKPOINT_INTENT_VERSION:
        admitted = validate_checkpoint_tick_intent(intent, contract)
        return admitted["operation_id"], "checkpoint_transition", tc.sha256(admitted)
    if version == USER_DECISION_INTENT_VERSION:
        admitted = validate_user_decision_tick_intent(intent, contract)
        return (
            admitted["next_operation"]["operation_id"],
            "user_decision_transition",
            tc.sha256(admitted),
        )
    admitted = validate_tick_intent(intent, contract)
    return (
        admitted["transaction_manifest"]["operation_id"],
        "clean_closeout",
        tc.sha256(admitted["transaction_manifest"]),
    )


def _is_exact_published_intent(
    transaction: dict,
    *,
    operation_id: str | None,
    event_kind: str,
    intent_sha256: str,
) -> bool:
    if (
        transaction.get("operation_id") != operation_id
        or transaction.get("event_kind") != event_kind
    ):
        return False
    return any(
        isinstance(event, dict)
        and isinstance(event.get("payload"), dict)
        and (
            event["payload"].get("intent_sha256") == intent_sha256
            or event["payload"].get("manifest_sha256") == intent_sha256
        )
        for event in transaction.get("journal", [])
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--intent", type=Path)
    arguments = parser.parse_args(argv)
    contract = validate_contract(_load(CONTRACT))
    if arguments.rollback:
        if arguments.intent is not None:
            parser.error("--rollback does not accept --intent")
        rollback = rollback_tick_generation(ROOT, contract, writer_id="clockwork")
        result = _command_result(rollback, _rollback_transaction_facts(rollback))
    else:
        if arguments.intent is None:
            parser.error("--check and --publish require --intent")
        intent_path = _intent_path(arguments.intent)
        intent = _load(intent_path)
        transaction = _load(ROOT / contract["clockwork_root"] / "transaction.json")
        operation_id, event_kind, intent_sha256 = _intent_identity(intent, contract)
        if _is_exact_published_intent(
            transaction,
            operation_id=operation_id,
            event_kind=event_kind,
            intent_sha256=intent_sha256,
        ):
            state = validate_tick_live_state(ROOT, contract)
            result = _command_result(state, _idempotent_transaction_facts(state))
            if arguments.publish:
                _write_outputs(
                    intent_path.parent,
                    result,
                    prefix=(
                        "clockwork-checkpoint-tick"
                        if intent.get("schema_version") == CHECKPOINT_INTENT_VERSION
                        else "clockwork-tick"
                    ),
                )
        else:
            if intent.get("schema_version") == BLOCKED_INTENT_VERSION:
                prepared = build_blocked_tick_generation(ROOT, contract, intent)
            elif intent.get("schema_version") == CHECKPOINT_INTENT_VERSION:
                prepared = build_checkpoint_tick_generation(ROOT, contract, intent)
            elif intent.get("schema_version") == USER_DECISION_INTENT_VERSION:
                prepared = build_user_decision_tick_generation(
                    ROOT, contract, intent
                )
            else:
                prepared = build_tick_generation(ROOT, contract, intent)
            if arguments.check:
                result = _command_result(
                    {
                        "schema_version": "ariadne.governance_live_tick_dry_run.v1",
                        "status": "passed",
                        "source_commit": prepared["source_commit"],
                        "generation_id": prepared["generation_manifest"]["generation_id"],
                        "bundle_sha256": prepared["generation_manifest"]["bundle_sha256"],
                        "previous_generation_id": prepared["pointer"]["previous_generation_id"],
                        "lease_sequence": prepared["pointer"]["lease_sequence"],
                    },
                    _prepared_transaction_facts(prepared, published=False),
                )
            else:
                published = publish_tick_generation(
                    ROOT, prepared, writer_id="clockwork"
                )
                result = _command_result(
                    published,
                    _prepared_transaction_facts(prepared, published=True),
                )
                _write_outputs(
                    intent_path.parent,
                    result,
                    prefix=(
                        "clockwork-checkpoint-tick"
                        if intent.get("schema_version") == CHECKPOINT_INTENT_VERSION
                        else "clockwork-tick"
                    ),
                )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cli(argv: list[str] | None = None) -> int:
    try:
        return main(argv)
    except ClockworkTickRejection as error:
        result = _prospective_rejection_result(error)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
