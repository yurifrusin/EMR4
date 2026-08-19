"""Run the provider-free single-owner governance migration rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from orchestration_harness.governance_migration import (
    WRITER, assess_rehearsal, build_clockwork_generation, initialize_mirror,
    publish_generation, validate_contract, validate_intent, _load,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal"
CONTRACT = TOPIC / "contract.json"
INTENT = TOPIC / "closeout-intent.json"


def _report(evidence: dict) -> str:
    return (
        "# Clockwork single-owner migration rehearsal\n\n"
        f"Status: **{evidence['status']}**\n\n"
        f"Source: `{evidence['source_commit']}`\n\n"
        f"Clockwork generation: `{evidence['clockwork_generation_id']}`\n\n"
        f"Bundle: `{evidence['bundle_sha256']}`\n\n"
        f"All {evidence['ownership']['clockwork_owned_after_cutover']} surfaces have one clockwork owner; "
        f"{evidence['fault_injection']['passed']}/{evidence['fault_injection']['checkpoints']} fault checkpoints passed, "
        f"rollback was byte-exact and projected steady-state corrective reruns are "
        f"{evidence['projected_steady_state_corrective_reruns']}. Construction reruns: {evidence['construction_reruns']}.\n\n"
        "Canonical controls were not adopted, retired or mutated by this rehearsal.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--construction-reruns", type=int, default=0)
    args = parser.parse_args()
    evidence = assess_rehearsal(ROOT, CONTRACT, INTENT, construction_reruns=args.construction_reruns)
    if args.publish:
        contract = validate_contract(_load(CONTRACT))
        intent = validate_intent(_load(INTENT), contract)
        mirror = ROOT / contract["mirror_root"]
        initialized = initialize_mirror(ROOT, mirror, contract)
        generation = build_clockwork_generation(ROOT, contract, intent, initialized["oracle"]["generation_id"])
        publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER)
        (TOPIC / "provider-free-migration-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
        (TOPIC / "migration-report.md").write_text(_report(evidence), encoding="utf-8", newline="\n")
    print(json.dumps(evidence, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
