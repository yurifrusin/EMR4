#!/usr/bin/env python3
"""Run distinct cost-bounded Bureau retry 002 after pre-call repair."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    reception_one_bureau_cost_bounded_occupied_retry as predecessor,
)


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry-002"
)
CONTROL_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry"
)
AUTHORITY_PATH = OUTPUT / "occupied-authority.json"
PREFLIGHT_PATH = OUTPUT / "occupied-preflight-evidence.json"
PROVIDER_FREE_PATH = CONTROL_ROOT / "provider-free-evidence.json"
ISOLATION_PATH = CONTROL_ROOT / "real-isolation-evidence.json"
PRE_RESIDUE_PATH = OUTPUT / "pre-attempt-residue-evidence.json"
EVIDENCE_PATH = OUTPUT / "occupied-ui-route-evidence.json"
FAILURE_PATH = OUTPUT / "occupied-ui-route-failure-evidence.json"
CLEANUP_PATH = OUTPUT / "occupied-ui-cleanup-evidence.json"
POST_RESIDUE_PATH = OUTPUT / "occupied-final-residue-evidence.json"
SCREENSHOT_PATH = OUTPUT / "occupied-explicit-selection-result.png"
COST_POLICY_PATH = OUTPUT / "cost-policy.json"
COST_LEDGER_PATH = OUTPUT / "cumulative-cost-ledger.json"
RESULT_PATH = OUTPUT / "occupied-cost-bounded-result.json"
LOCKED_DATABASE = (
    "gp_pms_reception_one_cost_retry_002_7d6ab342_20260731"
)
RUNTIME_TAG = "reception-one-cost-retry-002-7d6ab342"
GRAPH_REVISION = 164
COMPASS_REVISION = 145
RESERVATION_ID = "bureau-cost-bounded-occupied-retry-002"


def configure_successor() -> None:
    predecessor.OUTPUT = OUTPUT
    predecessor.AUTHORITY_PATH = AUTHORITY_PATH
    predecessor.PREFLIGHT_PATH = PREFLIGHT_PATH
    predecessor.PROVIDER_FREE_PATH = PROVIDER_FREE_PATH
    predecessor.ISOLATION_PATH = ISOLATION_PATH
    predecessor.PRE_RESIDUE_PATH = PRE_RESIDUE_PATH
    predecessor.EVIDENCE_PATH = EVIDENCE_PATH
    predecessor.FAILURE_PATH = FAILURE_PATH
    predecessor.CLEANUP_PATH = CLEANUP_PATH
    predecessor.POST_RESIDUE_PATH = POST_RESIDUE_PATH
    predecessor.SCREENSHOT_PATH = SCREENSHOT_PATH
    predecessor.COST_POLICY_PATH = COST_POLICY_PATH
    predecessor.COST_LEDGER_PATH = COST_LEDGER_PATH
    predecessor.RESULT_PATH = RESULT_PATH
    predecessor.LOCKED_DATABASE = LOCKED_DATABASE
    predecessor.RUNTIME_TAG = RUNTIME_TAG
    predecessor.GRAPH_REVISION = GRAPH_REVISION
    predecessor.COMPASS_REVISION = COMPASS_REVISION
    predecessor.RESERVATION_ID = RESERVATION_ID


def main() -> int:
    configure_successor()
    return predecessor.main()


if __name__ == "__main__":
    raise SystemExit(main())
