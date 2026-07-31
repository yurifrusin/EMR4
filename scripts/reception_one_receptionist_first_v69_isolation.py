#!/usr/bin/env python3
"""Real-isolation proof for the frozen v6.8 lane before v6.9 holdout use."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_receptionist_first_v68_isolation as base


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v69"
    / "real-isolation-evidence.json"
)


def run_isolation() -> dict:
    evidence = base.run_isolation()
    return {
        **evidence,
        "schema_version": (
            "reception.one.receptionist_first_v69."
            "holdout_isolation_evidence.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v69_"
            "holdout_real_isolation_pass"
        ),
        "frozen_v68_contract": True,
        "holdout_payload_sent_to_provider": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        evidence = run_isolation()
    except Exception as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_receptionist_first_v69_"
                        "holdout_real_isolation_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"result": evidence["result"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
