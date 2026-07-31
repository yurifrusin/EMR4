#!/usr/bin/env python3
"""Generate the fresh provider-blocked gate for the cost-bounded Bureau retry."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_receptionist_first_v68 as v68


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry"
    / "provider-blocked-evidence-rerun-001.json"
)
GRAPH_REVISION = 163
COMPASS_REVISION = 144


def main() -> int:
    if OUTPUT.exists():
        print(
            json.dumps(
                {
                    "result": "provider_blocked_gate_refused",
                    "reason_code": "provider_blocked_output_preexisted",
                    "provider_calls": 0,
                },
                sort_keys=True,
            )
        )
        return 2
    value = v68.build_provider_blocked_evidence()
    if (
        value.get("result")
        != "reception_one_receptionist_first_v68_provider_blocked_pass"
        or value.get("provider_calls_performed") != 0
        or value.get("credential_reads_performed") != 0
    ):
        print(
            json.dumps(
                {
                    "result": "provider_blocked_gate_failed",
                    "reason_code": "provider_blocked_contract_invalid",
                    "provider_calls": 0,
                },
                sort_keys=True,
            )
        )
        return 2
    wrapped = {
        **value,
        "schema_version": (
            "reception.one.bureau.cost_bounded_retry."
            "provider_blocked_evidence.v1"
        ),
        "result": (
            "reception_one_bureau_cost_bounded_retry_"
            "provider_blocked_pass"
        ),
        "continuity_binding": {
            "graph_revision": GRAPH_REVISION,
            "compass_revision": COMPASS_REVISION,
            "compass_source_graph_revision": GRAPH_REVISION,
        },
        "cumulative_cost_contract_exercised": False,
        "provider_call_authority_consumed": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(wrapped, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "result": wrapped["result"],
                "provider_calls": 0,
                "credential_reads": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
