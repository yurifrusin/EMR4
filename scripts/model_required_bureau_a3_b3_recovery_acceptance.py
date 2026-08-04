#!/usr/bin/env python3
"""Acceptance for the A3/B3 request-contract recovery."""

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
OCCUPIED_EVIDENCE = ARTIFACT_ROOT / "occupied-rehearsal-evidence.json"
OCCUPIED_COST_LEDGER = ARTIFACT_ROOT / "occupied-rehearsal-cost-ledger.json"
SOURCE_REVIEW = ROOT / (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-a3-b3-request-contract-recovery-review-2-receipt.json"
)
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


def run_acceptance(
    *, require_dry_run: bool, require_occupied: bool = False
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    required = [
        ROOT
        / "docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-plan.md",
        ROOT
        / (
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
    if require_occupied:
        required.extend([OCCUPIED_EVIDENCE, OCCUPIED_COST_LEDGER, SOURCE_REVIEW])
        for lane in ("rayleen-a3", "davida-b3"):
            required.extend(
                [
                    ARTIFACT_ROOT / f"{lane}-attempt-1-occupied-ledger.json",
                    ARTIFACT_ROOT / f"{lane}-attempt-1-occupied-audit.jsonl",
                    ARTIFACT_ROOT / f"{lane}-attempt-1-occupied-evidence.json",
                    ARTIFACT_ROOT / f"{lane}-attempt-1-preflight.json",
                ]
            )
    _check(
        all(path.is_file() for path in required), "artifact_manifest_complete", checks
    )

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
            and new["generationConfig"]["thinkingConfig"] == {"thinkingBudget": 1024}
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
        and diagnosis["selected_first_change"]["reasoning_default_minimized"] is False
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
            events = _read_events(ARTIFACT_ROOT / f"{lane_stem}-attempt-1-audit.jsonl")
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
                and "provider_call_started"
                not in {event["event_type"] for event in events},
                f"{lane}_provider_free_attempt_exact",
                checks,
            )

    if require_occupied:
        source_review = contracts.load_object(SOURCE_REVIEW)
        _check(
            source_review["status"] == "completed"
            and source_review["transport"]
            == "antigravity_new_project_bound_readonly_worktree"
            and source_review["model"] == "gemini-3.6-flash-high"
            and source_review["reasoning_effort"] == "high"
            and source_review["decision"] == "pass"
            and source_review["head_before"] == source_review["head_after"]
            and source_review["dirty_after"] is False
            and source_review["result"].count("DECISION: pass") == 1
            and "DECISION: revision_required" not in source_review["result"],
            "occupied_source_review_exact",
            checks,
        )

        tranche = contracts.load_object(OCCUPIED_EVIDENCE)
        cost = contracts.load_object(OCCUPIED_COST_LEDGER)
        contracts.validate_instance(ARTIFACT_ROOT / "cost-ledger.schema.json", cost)
        _check(
            tranche["result"]
            == "model_required_bureau_a3_b3_request_contract_recovery_pass"
            and tranche["mode"] == "live"
            and tranche["combined_pass"] is True
            and tranche["rayleen_a3_admitted"] is True
            and tranche["davida_b3_started"] is True
            and tranche["davida_b3_admitted"] is True
            and tranche["candidate_runtime_provider_call_count"] == 2
            and tranche["reserved_cost_usd"] == 0.5
            and tranche["maximum_cost_usd"] == 1.0
            and tranche["source_review_model"] == "gemini-3.6-flash-high"
            and tranche["source_review_transport_nonzero"] is True
            and all(tranche[key] == 0 for key in ZERO_COUNTERS[1:])
            and _evidence_hash_valid(tranche),
            "occupied_tranche_exact",
            checks,
        )
        _check(
            cost["status"] == "consumed"
            and cost["maximum_provider_calls"] == 4
            and cost["provider_calls_reserved"] == 2
            and cost["provider_calls_consumed"] == 2
            and cost["lane_calls"] == {"rayleen_a3": 1, "davida_b3": 1}
            and cost["reserved_cost_usd"] == 0.5
            and cost["maximum_cost_usd"] == 1.0
            and cost["fallback_permitted"] is False,
            "occupied_cost_consumed_once_per_lane",
            checks,
        )

        lane_results = {item["lane"]: item for item in tranche["lane_results"]}
        _check(
            list(item["lane"] for item in tranche["lane_results"])
            == [contracts.LANE_RAYLEEN, contracts.LANE_DAVIDA],
            "rayleen_release_precedes_davida",
            checks,
        )
        for lane_stem, lane in (
            ("rayleen-a3", contracts.LANE_RAYLEEN),
            ("davida-b3", contracts.LANE_DAVIDA),
        ):
            attempt = contracts.load_object(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-occupied-evidence.json"
            )
            ledger = contracts.load_object(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-occupied-ledger.json"
            )
            preflight = contracts.load_object(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-preflight.json"
            )
            events = _read_events(
                ARTIFACT_ROOT / f"{lane_stem}-attempt-1-occupied-audit.jsonl"
            )
            contracts.validate_instance(
                ARTIFACT_ROOT / "single-use-ledger.schema.json", ledger
            )
            metadata = attempt["provider_metadata"]
            _check(
                lane_results[lane] == attempt
                and attempt["mode"] == "live"
                and attempt["result"] == "attempt_pass"
                and attempt["proofreader_verdict"] == "admitted"
                and attempt["proofreader_reason_code"] == "proofreader_admitted"
                and attempt["provider_call_count"] == 1
                and attempt["provider_contacted"] is True
                and attempt["correction_eligible"] is False
                and attempt["cleanup_passed"] is True
                and attempt["cleanup"]["daemon_wide_prune_performed"] is False
                and all(
                    value
                    for key, value in attempt["cleanup"].items()
                    if key != "daemon_wide_prune_performed"
                )
                and attempt["credential_or_token_retained"] is False
                and attempt["raw_prompt_retained"] is False
                and attempt["raw_provider_response_retained"] is False
                and attempt["request_binding"]["policy_id"] == contracts.POLICY_ID
                and all(
                    attempt[key] == 0
                    for key in (
                        "product_read_count",
                        "database_access_count",
                        "command_count",
                        "write_count",
                        "actuator_count",
                    )
                )
                and _evidence_hash_valid(attempt),
                f"{lane}_occupied_attempt_exact",
                checks,
            )
            _check(
                metadata["provider_contacted"] is True
                and metadata["fixture_used"] is False
                and metadata["http_status"] == 200
                and metadata["model_version"] == "gemini-2.5-flash"
                and metadata["candidate_count"] == 1
                and metadata["finish_reason"] == "STOP"
                and metadata["content_present"] is True
                and metadata["parts_count"] == 1
                and metadata["part_kinds"] == ["text"]
                and metadata["text_utf8_bytes"] > 0
                and metadata["usage"]["thoughtsTokenCount"] > 0
                and metadata["provider_text_retained"] is False
                and metadata["raw_prompt_retained"] is False
                and metadata["raw_provider_response_retained"] is False
                and metadata["raw_response_retained"] is False,
                f"{lane}_positive_reasoning_safe_metadata",
                checks,
            )
            _check(
                preflight["result"]
                == "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
                and preflight["project"] == "bernie-emr4-dev"
                and preflight["service_account"]
                == "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
                and preflight["location"] == "australia-southeast1"
                and preflight["endpoint_hostname"]
                == "australia-southeast1-aiplatform.googleapis.com"
                and preflight["model_id"] == "gemini-2.5-flash"
                and preflight["external_state_changed"] is False
                and preflight["model_inference_called"] is False
                and preflight["provider_prompt_transmitted"] is False
                and all(preflight["checks"].values()),
                f"{lane}_read_only_preflight_exact",
                checks,
            )
            _check(
                ledger["status"] == "consumed"
                and ledger["provider_calls_consumed"] == 1
                and ledger["maximum_provider_calls"] == 1
                and ledger["reserved_cost_usd"] == 0.25
                and ledger["fallback_permitted"] is False
                and ledger["policy_id"] == contracts.POLICY_ID,
                f"{lane}_single_use_ledger_consumed",
                checks,
            )
            _check(
                [event["event_type"] for event in events]
                == [
                    "broker_ready",
                    "request_admitted",
                    "ledger_consumed",
                    "provider_request_constructed",
                    "provider_call_started",
                    "provider_call_completed",
                    "proofreader_completed",
                    "release_committed",
                ],
                f"{lane}_occupied_audit_sequence_exact",
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
    parser.add_argument("--require-occupied", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run_acceptance(
            require_dry_run=args.require_dry_run,
            require_occupied=args.require_occupied,
        )
    except (OSError, json.JSONDecodeError, contracts.ContractError) as error:
        print(json.dumps({"passed": False, "reason_code": str(error)}, sort_keys=True))
        return 2
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
