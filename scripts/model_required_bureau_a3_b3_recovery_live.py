#!/usr/bin/env python3
"""Run the isolated A3/B3 request-contract recovery tranche."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import model_required_bureau_a3_b3_contracts as parent_contracts
from scripts import model_required_bureau_a3_b3_live as live
from scripts import model_required_bureau_a3_b3_recovery_contracts as contracts


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
CELL_REQUEST_SCHEMA = ARTIFACT_ROOT / "cell-request.schema.json"
ATTEMPT_LEDGER_SCHEMA = ARTIFACT_ROOT / "single-use-ledger.schema.json"
COST_LEDGER_SCHEMA = ARTIFACT_ROOT / "cost-ledger.schema.json"
SOURCE_REVIEW_RECEIPT = ROOT / (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-a3-b3-request-contract-recovery-review-receipt.json"
)
_PARENT_RUN_ATTEMPT = live._run_attempt
_PARENT_TRANCHE_EVIDENCE = live._tranche_evidence
_PARENT_POPEN = live.subprocess.Popen


def _names(lane: str, attempt_number: int) -> dict[str, str]:
    short_lane = "rayleen" if lane == contracts.LANE_RAYLEEN else "davida"
    suffix = f"{short_lane}-{attempt_number}"
    return {
        "network": f"emr4-a3-b3-recovery-{suffix}-internal",
        "relay_container": f"emr4-a3-b3-recovery-{suffix}-relay",
        "cell_container": f"emr4-a3-b3-recovery-{suffix}-cell",
        "relay_image": f"emr4-a3-b3-recovery-{suffix}-relay:v1",
        "cell_image": f"emr4-a3-b3-recovery-{suffix}-cell:v1",
    }


def _request_packet(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_of: str | None,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    kind = "primary" if attempt_number == 1 else "correction"
    lane_id = "rayleen-a3" if lane == contracts.LANE_RAYLEEN else "davida-b3"
    request = contracts.provider_request_for_attempt(
        lane,
        context,
        attempt_number=attempt_number,
        correction_reason_code=correction_reason_code,
    )
    packet = {
        "schema_version": "emr4.model_required_bureau_a3_b3.cell_request.v1",
        "lane": lane,
        "attempt_id": (
            f"a3-b3-recovery-{lane_id}-{kind}-{attempt_number:03d}"
        ),
        "ledger_id": (
            f"ledger-a3-b3-recovery-{lane_id}-{kind}-{attempt_number:03d}"
        ),
        "policy_id": contracts.POLICY_ID,
        "context_hash": contracts.prefixed_sha256(context),
        "provider_request_hash": contracts.prefixed_sha256(request),
        "attempt_number": attempt_number,
        "correction_of": correction_of,
        "correction_reason_code": correction_reason_code,
    }
    contracts.validate_instance(CELL_REQUEST_SCHEMA, packet)
    return packet


def _initial_cost_ledger() -> dict[str, Any]:
    ledger = {
        "schema_version": "emr4.model_required_bureau_a3_b3.cost_ledger.v1",
        "tranche_id": "model-required-bureau-a3-b3-request-contract-recovery-001",
        "status": "open",
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "provider_calls_reserved": 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": 0,
        "lane_calls": {
            contracts.LANE_RAYLEEN: 0,
            contracts.LANE_DAVIDA: 0,
        },
        "fallback_permitted": False,
    }
    contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
    return ledger


def _recovery_popen(
    args: Any, *positional: Any, **keywords: Any
) -> subprocess.Popen[bytes]:
    adjusted = list(args) if isinstance(args, (list, tuple)) else args
    if isinstance(adjusted, list):
        adjusted = [
            "scripts.model_required_bureau_a3_b3_recovery_broker"
            if item == "scripts.model_required_bureau_a3_b3_broker"
            else item
            for item in adjusted
        ]
    return _PARENT_POPEN(adjusted, *positional, **keywords)


def _run_attempt(**kwargs: Any) -> dict[str, Any]:
    live.subprocess.Popen = _recovery_popen
    try:
        return _PARENT_RUN_ATTEMPT(**kwargs)
    finally:
        live.subprocess.Popen = _PARENT_POPEN


def _tranche_evidence(**kwargs: Any) -> dict[str, Any]:
    result_name = kwargs["result_name"]
    replacements = {
        "model_required_bureau_a3_b3_provider_free_dry_run_pass": (
            "model_required_bureau_a3_b3_request_contract_recovery_provider_free_pass"
        ),
        "model_required_bureau_a3_b3_occupied_advisory_rehearsal_pass": (
            "model_required_bureau_a3_b3_request_contract_recovery_pass"
        ),
        "model_required_bureau_a3_b3_occupied_terminal_rejection": (
            "model_required_bureau_a3_b3_request_contract_recovery_terminal_rejection"
        ),
    }
    kwargs["result_name"] = replacements.get(result_name, result_name)
    return _PARENT_TRANCHE_EVIDENCE(**kwargs)


def _configure() -> None:
    live.contracts = contracts
    live.ARTIFACT_ROOT = ARTIFACT_ROOT
    live.DOCKERFILE = parent_contracts.ARTIFACT_ROOT / "Dockerfile"
    live.CELL_REQUEST_SCHEMA = CELL_REQUEST_SCHEMA
    live.ATTEMPT_LEDGER_SCHEMA = ATTEMPT_LEDGER_SCHEMA
    live.COST_LEDGER_SCHEMA = COST_LEDGER_SCHEMA
    live.SOURCE_REVIEW_RECEIPT = SOURCE_REVIEW_RECEIPT
    live.PREPROOF_TERMINAL_REASON_CODES = frozenset(
        {
            "provider_candidate_count_invalid",
            "provider_content_missing",
            "provider_content_invalid",
            "provider_parts_invalid",
            "provider_parts_empty",
            "provider_parts_count_invalid",
            "provider_part_thought_invalid",
            "provider_part_non_text_invalid",
            "provider_candidate_not_json",
            "provider_candidate_not_object",
        }
    )
    live._names = _names
    live._request_packet = _request_packet
    live._initial_cost_ledger = _initial_cost_ledger
    live._run_attempt = _run_attempt
    live._tranche_evidence = _tranche_evidence


def main() -> int:
    _configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dry-run", "live"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-ledger", type=Path, required=True)
    parser.add_argument("--source-review", type=Path)
    args = parser.parse_args()
    try:
        evidence = live.run_tranche(
            mode=args.mode,
            output_path=args.output,
            cost_ledger_path=args.cost_ledger,
            source_review_path=args.source_review,
        )
    except (live.LiveError, OSError, subprocess.SubprocessError) as error:
        print(
            json.dumps(
                {
                    "result": "model_required_bureau_a3_b3_recovery_blocked",
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_call_count": evidence[
                    "candidate_runtime_provider_call_count"
                ],
                "lane_count": len(evidence["lane_results"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
