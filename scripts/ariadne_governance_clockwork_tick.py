"""Check, publish or roll back one generic live governance clockwork tick."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.governance_clockwork_tick import (
    BLOCKED_INTENT_VERSION,
    CHECKPOINT_INTENT_VERSION,
    USER_DECISION_INTENT_VERSION,
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
        f"Lease sequence: {result['lease_sequence']}\n",
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
        tc.sha256(admitted),
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
        and event["payload"].get("intent_sha256") == intent_sha256
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
        result = rollback_tick_generation(ROOT, contract, writer_id="clockwork")
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
            result = validate_tick_live_state(ROOT, contract)
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
                result = {
                    "schema_version": "ariadne.governance_live_tick_dry_run.v1",
                    "status": "passed",
                    "source_commit": prepared["source_commit"],
                    "generation_id": prepared["generation_manifest"]["generation_id"],
                    "bundle_sha256": prepared["generation_manifest"]["bundle_sha256"],
                    "previous_generation_id": prepared["pointer"]["previous_generation_id"],
                    "lease_sequence": prepared["pointer"]["lease_sequence"],
                    "caller_authored_derived_fields": 0,
                    "live_publication_count": 0,
                }
            else:
                result = {
                    **publish_tick_generation(
                        ROOT, prepared, writer_id="clockwork"
                    ),
                    "caller_authored_derived_fields": 0,
                    "live_publication_count": 1,
                    "bespoke_updater_executions": 0,
                }
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


if __name__ == "__main__":
    raise SystemExit(main())
