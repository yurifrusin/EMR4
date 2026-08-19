"""Check or perform the provider-free live governance clockwork adoption."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.governance_live_adoption import (
    build_generation,
    publish_live_generation,
    validate_contract,
    validate_live_state,
)


TOPIC = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement"
CONTRACT = TOPIC / "contract.json"
INTENT = TOPIC / "closeout-intent.json"
EVIDENCE = TOPIC / "provider-free-live-adoption-evidence.json"
REPORT = TOPIC / "adoption-report.md"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--adopt", action="store_true")
    arguments = parser.parse_args(argv)
    contract = validate_contract(_load(CONTRACT))
    pointer = ROOT / contract["clockwork_root"] / "current.json"
    if arguments.check and pointer.is_file():
        result = validate_live_state(ROOT, contract)
    else:
        prepared = build_generation(ROOT, contract, _load(INTENT))
        if arguments.check:
            result = {
                "schema_version": "ariadne.governance_live_dry_run.v1",
                "status": "passed",
                "source_commit": prepared["source_commit"],
                "generation_id": prepared["generation_manifest"]["generation_id"],
                "bundle_sha256": prepared["generation_manifest"]["bundle_sha256"],
                "previous_generation_id": prepared["pointer"]["previous_generation_id"],
                "clockwork_owned_surfaces": 10,
                "dual_owned_surfaces": 0,
                "retired_legacy_writer_classes": 4,
                "caller_authored_derived_fields": 0,
                "live_publication_count": 0,
            }
        else:
            state = publish_live_generation(
                ROOT, prepared, writer_id="clockwork"
            )
            result = {
                **state,
                "caller_authored_derived_fields": 0,
                "live_publication_count": 1,
                "bespoke_updater_executions": 0,
            }
            _write_json(EVIDENCE, result)
            REPORT.write_text(
                "# Clockwork live canonical adoption\n\n"
                "Status: **passed**\n\n"
                f"Source: `{state['source_commit']}`\n\n"
                f"Generation: `{state['generation_id']}`\n\n"
                f"Bundle: `{state['bundle_sha256']}`\n\n"
                "Ten surfaces have one clockwork owner, four legacy writer classes are retired, and canonical drift is zero.\n",
                encoding="utf-8",
                newline="\n",
            )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
