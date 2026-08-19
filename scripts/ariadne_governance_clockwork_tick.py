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
    build_tick_generation,
    publish_tick_generation,
    rollback_tick_generation,
    validate_tick_live_state,
)
from orchestration_harness.governance_live_adoption import validate_contract


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
    if not path.is_file() or path.name != "closeout-intent.json":
        raise ValueError("closeout_intent_required")
    return path


def _write_outputs(topic: Path, result: dict) -> None:
    evidence = topic / "clockwork-tick-evidence.json"
    report = topic / "clockwork-tick-report.md"
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
        operation_id = intent.get("transaction_manifest", {}).get("operation_id")
        if arguments.check and transaction.get("operation_id") == operation_id:
            result = validate_tick_live_state(ROOT, contract)
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
                _write_outputs(intent_path.parent, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
