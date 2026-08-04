#!/usr/bin/env python3
"""Provider-free acceptance for the A3/B3 request-contract recovery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import model_required_bureau_a3_b3_contracts as parent
from scripts import model_required_bureau_a3_b3_recovery_contracts as contracts


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
DRY_RUN_EVIDENCE = ARTIFACT_ROOT / "provider-free-dry-run-evidence.json"
DRY_RUN_COST_LEDGER = ARTIFACT_ROOT / "provider-free-dry-run-cost-ledger.json"
ZERO_COUNTERS = (
    "candidate_runtime_provider_call_count",
    "patient_or_clinical_data_count",
    "product_read_count",
    "database_access_count",
    "command_count",
    "write_count",
    "actuator_count",
    "cloud_or_iam_mutation_count",
    "deployment_count",
    "protected_ref_movement_count",
)


def _check(condition: bool, name: str, checks: dict[str, bool]) -> None:
    checks[name] = bool(condition)
    if not condition:
        raise contracts.ContractError(name)


def _read_events(path: Path) -> list[dict[str, Any]]:
    events = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    previous = "sha256:" + "0" * 64
    for sequence, event in enumerate(events, start=1):
        material = {key: value for key, value in event.items() if key != "event_hash"}
        if (
            event.get("sequence") != sequence
            or event.get("previous_hash") != previous
            or event.get("event_hash") != contracts.prefixed_sha256(material)
        ):
            raise contracts.ContractError("audit_hash_chain_invalid")
        previous = event["event_hash"]
    return events


def _evidence_hash_valid(value: dict[str, Any]) -> bool:
    expected = value.get("evidence_hash")
    material = {key: item for key, item in value.items() if key != "evidence_hash"}
    return expected == contracts.prefixed_sha256(material)


def run_acceptance(*, require_dry_run: bool) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    required = [
        ROOT / "docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-plan.md",
        ROOT / (
            "docs/security/"
            "emr4-model-required-bureau-a3-b3-request-contract-recovery-threat-model-delta.md"
        ),
        ARTIFACT_ROOT / "diagnosis-evidence.json",
        ARTIFACT_ROOT / "cell-request.schema.json",
        ARTIFACT_ROOT / "single-use-ledger.schema.json",
        ARTIFACT_ROOT / "cost-ledger.schema.json",
        ROOT / "scripts/model_required_bureau_a3_b3_recovery_contracts.py",
        ROOT / "scripts/model_required_bureau_a3_b3_recovery_broker.py",
        ROOT / "scripts/model_required_bureau_a3_b3_recovery_live.py",
        ROOT / "tests/test_model_required_bureau_a3_b3_request_contract_recovery.py",
    ]
    if require_dry_run:
        required.extend([DRY_RUN_EVIDENCE, DRY_RUN_COST_LEDGER])
        for lane in ("rayleen-a3", "davida-b3"):
            required.extend(
                [
                    ARTIFACT_ROOT / f"{lane}-attempt-1-ledger.json",
                    ARTIFACT_ROOT / f"{lane}-attempt-1-audit.jsonl",
                    ARTIFACT_ROOT / f"{lane}-attempt-1-dry-run-evidence.json",
                ]
            )
    _check(all(path.is_file() for path in required), "artifact_manifest_complete", checks)

    for name in (
        "cell-request.schema.json",
        "single-use-ledger.schema.json",
        "cost-ledger.schema.json",
    ):
        Draft202012Validator.check_schema(contracts.load_object(ARTIFACT_ROOT / name))
    _check(True, "draft_2020_12_schemas_valid", checks)

    for lane in sorted(contracts.LANES):
        context_path = (
            contracts.RAYLEEN_CONTEXT_PATH
            if lane == contracts.LANE_RAYLEEN
            else contracts.DAVIDA_CONTEXT_PATH
        )
        context = contracts.load_object(context_path)
        old = parent.build_vertex_request(lane, context)
        new = contracts.build_vertex_request(lane, context)
        expected = json.loads(json.dumps(old))
        expected["generationConfig"]["maxOutputTokens"] = 2048
        expected["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 1024}
        _check(new == expected, f"{lane}_bounded_reasoning_request_change", checks)
        _check(
            new["generationConfig"]["maxOutputTokens"] == 2048
            and new["generationConfig"]["thinkingConfig"]
            == {"thinkingBudget": 1024}
            and new["generationConfig"]["responseSchema"]
            == old["generationConfig"]["responseSchema"]
            and new["contents"] == old["contents"],
            f"{lane}_request_semantics_preserved",
            checks,
        )

    diagnosis = contracts.load_object(ARTIFACT_ROOT / "diagnosis-evidence.json")
    _check(
        diagnosis["inference"]["proven_cause"] is False
        and diagnosis["selected_first_change"]["policy"]
        == "bounded_positive_reasoning_with_visible_answer_headroom"
        and diagnosis["selected_first_change"]["reasoning_default_minimized"]
        is False
        and all(value == 0 for value in diagnosis["side_effects"].values()),
        "diagnosis_is_truthful_and_provider_free",
        checks,
    )

    if require_dry_run:
        tranche = contracts.load_object(DRY_RUN_EVIDENCE)
        cost = contracts.load_object(DRY_RUN_COST_LEDGER)
        contracts.validate_instance(ARTIFACT_ROOT / "cost-ledger.schema.json", cost)
        _check(
            tranche["result"]
            == "model_required_bureau_a3_b3_request_contract_recovery_provider_free_pass"
            and tranche["combined_pass"] is True
            and tranche["rayleen_a3_admitted"] is True
            and tranche["davida_b3_started"] is True
            and tranche["davida_b3_admitted"] is True
            and all(tranche[key] == 0 for key in ZERO_COUNTERS)
            and _evidence_hash_valid(tranche),
            "provider_free_tranche_exact",
            checks,
        )
        _check(
            cost["status"] == "consumed"
            and cost["provider_calls_reserved"] == 0
            and cost["provider_calls_consumed"] == 0
            and cost["reserved_cost_usd"] == 0,
            "provider_free_cost_zero",
            checks,
        )
        for lane_stem, lane in (
            ("rayleen-a3", contracts.LANE_RAYLEEN),
            ("davida-b3", contracts.LANE_DAVIDA),
        ):
            attempt = contracts.load_object(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-dry-run-evidence.json"
            )
            ledger = contracts.load_object(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-ledger.json"
            )
            events = _read_events(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-audit.jsonl"
            )
            contracts.validate_instance(
                ARTIFACT_ROOT / "single-use-ledger.schema.json", ledger
            )
            _check(
                attempt["lane"] == lane
                and attempt["result"] == "attempt_pass"
                and attempt["proofreader_verdict"] == "admitted"
                and attempt["provider_call_count"] == 0
                and attempt["cleanup_passed"] is True
                and attempt["cleanup"]["daemon_wide_prune_performed"] is False
                and all(
                    value
                    for key, value in attempt["cleanup"].items()
                    if key != "daemon_wide_prune_performed"
                )
                and _evidence_hash_valid(attempt)
                and "provider_call_started" not in {
                    event["event_type"] for event in events
                },
                f"{lane}_provider_free_attempt_exact",
                checks,
            )

    return {
        "schema_version": "emr4.model_required_bureau_a3_b3.recovery_acceptance.v1",
        "result": "model_required_bureau_a3_b3_request_contract_recovery_acceptance_pass",
        "passed": all(checks.values()),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = run_acceptance(require_dry_run=args.require_dry_run)
    except (OSError, json.JSONDecodeError, contracts.ContractError) as error:
        print(json.dumps({"passed": False, "reason_code": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
