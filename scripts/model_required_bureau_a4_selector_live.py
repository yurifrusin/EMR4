#!/usr/bin/env python3
"""Run the isolated provider-free or occupied A4 Rayleen selector cell."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import model_required_bureau_a3_b3_contracts as parent_contracts
from scripts import model_required_bureau_a3_b3_live as live
from scripts import model_required_bureau_a4_selector_contracts as contracts


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
CELL_REQUEST_SCHEMA = ARTIFACT_ROOT / "cell-request.schema.json"
ATTEMPT_LEDGER_SCHEMA = ARTIFACT_ROOT / "single-use-ledger.schema.json"
COST_LEDGER_SCHEMA = ARTIFACT_ROOT / "cost-ledger.schema.json"
SOURCE_REVIEW_RECEIPT = ROOT / (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-a4-selector-source-review-receipt.json"
)
RECOVERY_SOURCE_REVIEW_RECEIPT = ROOT / (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-a4-selector-recovery-source-review-receipt.json"
)
OCCUPIED_CONTEXT_PATH = (
    ARTIFACT_ROOT / "occupied-authored-synthetic-selector-context.json"
)
DRY_RUN_CONTEXT_PATH = (
    ARTIFACT_ROOT / "provider-free-materialized-selector-context.json"
)
RECOVERY_OCCUPIED_CONTEXT_PATH = (
    ARTIFACT_ROOT / "occupied-authored-synthetic-selector-context-recovery-2.json"
)
RECOVERY_DRY_RUN_CONTEXT_PATH = (
    ARTIFACT_ROOT / "provider-free-materialized-selector-context-recovery-2.json"
)
REVIEWED_SOURCE_PATHS = (
    ROOT / "scripts/model_required_bureau_a4_selector_contracts.py",
    ROOT / "scripts/model_required_bureau_a4_selector_broker.py",
    ROOT / "scripts/model_required_bureau_a4_selector_live.py",
    ROOT / "tests/test_model_required_bureau_a4_selector.py",
    CELL_REQUEST_SCHEMA,
    ATTEMPT_LEDGER_SCHEMA,
    COST_LEDGER_SCHEMA,
    ARTIFACT_ROOT / "selector-context.schema.json",
    ARTIFACT_ROOT / "selector-model-body.schema.json",
    ARTIFACT_ROOT / "selector-candidate.schema.json",
    ARTIFACT_ROOT / "authored-synthetic-selector-context.json",
)

_PARENT_RUN_ATTEMPT = live._run_attempt
_PARENT_POPEN = live.subprocess.Popen


def _names(_lane: str, attempt_number: int) -> dict[str, str]:
    suffix = f"rayleen-selector-{attempt_number}"
    return {
        "network": f"emr4-a4-{suffix}-internal",
        "relay_container": f"emr4-a4-{suffix}-relay",
        "cell_container": f"emr4-a4-{suffix}-cell",
        "relay_image": f"emr4-a4-{suffix}-relay:v1",
        "cell_image": f"emr4-a4-{suffix}-cell:v1",
    }


def _request_packet(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_of: str | None,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    if lane != contracts.LANE_RAYLEEN:
        raise live.LiveError("lane_invalid")
    kind = "primary" if attempt_number == 1 else "correction"
    request = contracts.provider_request_for_attempt(
        lane,
        context,
        attempt_number=attempt_number,
        correction_reason_code=correction_reason_code,
    )
    packet = {
        "schema_version": "emr4.model_required_bureau_a4.cell_request.v1",
        "lane": lane,
        "attempt_id": f"a4-rayleen-selector-{kind}-{attempt_number:03d}",
        "ledger_id": (
            f"ledger-a4-rayleen-selector-{kind}-{attempt_number:03d}"
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


def _attempt_ledger(
    packet: dict[str, Any], *, mode: str
) -> dict[str, Any]:
    live_mode = mode == "live"
    ledger = {
        "schema_version": "emr4.model_required_bureau_a4.single_use_ledger.v1",
        "ledger_id": packet["ledger_id"],
        "attempt_id": packet["attempt_id"],
        "lane": packet["lane"],
        "policy_id": packet["policy_id"],
        "status": "open",
        "maximum_provider_calls": 1 if live_mode else 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": (
            contracts.RESERVED_COST_PER_CALL_USD if live_mode else 0
        ),
        "fallback_permitted": False,
    }
    contracts.validate_instance(ATTEMPT_LEDGER_SCHEMA, ledger)
    return ledger


def _initial_cost_ledger() -> dict[str, Any]:
    ledger = {
        "schema_version": "emr4.model_required_bureau_a4.cost_ledger.v1",
        "tranche_id": "model-required-bureau-a4-occupied-selector-001",
        "status": "open",
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "provider_calls_reserved": 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": 0,
        "lane_calls": {contracts.LANE_RAYLEEN: 0},
        "fallback_permitted": False,
    }
    contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
    return ledger


def _a4_popen(
    arguments: Any, *positional: Any, **keywords: Any
) -> subprocess.Popen[bytes]:
    adjusted = list(arguments) if isinstance(arguments, (list, tuple)) else arguments
    if isinstance(adjusted, list):
        adjusted = [
            "scripts.model_required_bureau_a4_selector_broker"
            if item == "scripts.model_required_bureau_a3_b3_broker"
            else item
            for item in adjusted
        ]
    return _PARENT_POPEN(adjusted, *positional, **keywords)


def _run_attempt(**keywords: Any) -> dict[str, Any]:
    live.subprocess.Popen = _a4_popen
    try:
        evidence = _PARENT_RUN_ATTEMPT(**keywords)
    finally:
        live.subprocess.Popen = _PARENT_POPEN
    evidence["schema_version"] = (
        "emr4.model_required_bureau_a4.selector_attempt_evidence.v1"
    )
    evidence["evidence_mode"] = (
        "provider_free_authored_synthetic_selector"
        if evidence["mode"] == "dry-run"
        else "occupied_authored_synthetic_live_local_product_read_ui"
    )
    evidence["trusted_context_data_class"] = "authored_synthetic"
    evidence["provider_context_class"] = (
        "request_scoped_opaque_bounded_waiting_signals"
    )
    evidence["patient_or_clinical_data_count"] = 0
    evidence["provider_tool_call_count"] = 0
    evidence["fallback_count"] = 0
    evidence.pop("evidence_hash", None)
    evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
    path = live._attempt_paths(
        keywords["lane"], keywords["attempt_number"], mode=keywords["mode"]
    )["evidence"]
    live._write_json(path, evidence)
    return evidence


def _review_source_hashes() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): live._file_hash(path)
        for path in REVIEWED_SOURCE_PATHS
    }


def _validate_source_review(
    path: Path, *, expected_path: Path = SOURCE_REVIEW_RECEIPT
) -> dict[str, Any]:
    receipt = contracts.load_object(path)
    expected_hashes = _review_source_hashes()
    if (
        path.resolve() != expected_path.resolve()
        or receipt.get("schema_version")
        != "emr4.model_required_bureau_a4.selector_source_review.v1"
        or receipt.get("status") != "passed"
        or receipt.get("decision") != "pass"
        or receipt.get("independent_read_only_review") is not True
        or receipt.get("provider_called") is not False
        or receipt.get("source_hashes") != expected_hashes
        or receipt.get("closed_boundary_verified") is not True
    ):
        raise live.LiveError("independent_source_review_not_exact")
    return receipt


def _tranche_evidence(
    *,
    mode: str,
    lane_results: list[dict[str, Any]],
    ledger: dict[str, Any],
    review: dict[str, Any] | None,
    admitted: bool,
    execution_context_path: Path,
    review_path: Path | None = None,
) -> dict[str, Any]:
    result = (
        "model_required_bureau_a4_provider_free_selector_pass"
        if mode == "dry-run" and admitted
        else "model_required_bureau_a4_occupied_selector_pass"
        if admitted
        else "model_required_bureau_a4_occupied_selector_terminal_rejection"
    )
    evidence = {
        "schema_version": (
            "emr4.model_required_bureau_a4.selector_tranche_evidence.v1"
        ),
        "result": result,
        "evidence_label": (
            "provider_free_authored_synthetic_selector"
            if mode == "dry-run"
            else "occupied_authored_synthetic_live_local_product_read_ui"
        ),
        "mode": mode,
        "combined_pass": admitted,
        "selector_admitted": admitted,
        "lane_results": lane_results,
        "candidate_runtime_provider_call_count": ledger[
            "provider_calls_consumed"
        ],
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "reserved_cost_usd": ledger["reserved_cost_usd"],
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "source_review_transport_nonzero": review is not None,
        "source_review_receipt_hash": (
            live._file_hash(review_path) if review and review_path else None
        ),
        "source_hashes": _review_source_hashes(),
        "execution_context_path": execution_context_path.relative_to(ROOT).as_posix(),
        "execution_context_hash": live._file_hash(execution_context_path),
        "execution_context_materialized_fresh": True,
        "authored_synthetic_context_count": 1,
        "patient_or_clinical_data_count": 0,
        "database_access_count": 0,
        "command_count": 0,
        "write_count": 0,
        "actuator_count": 0,
        "provider_tool_call_count": 0,
        "fallback_count": 0,
        "cloud_or_iam_mutation_count": 0,
        "deployment_count": 0,
        "protected_ref_movement_count": 0,
        "raw_prompt_retained": False,
        "raw_provider_response_retained": False,
        "credential_or_token_retained": False,
    }
    evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
    return evidence


def _configure() -> None:
    live.contracts = contracts
    live.ARTIFACT_ROOT = ARTIFACT_ROOT
    live.DOCKERFILE = parent_contracts.ARTIFACT_ROOT / "Dockerfile"
    live.CELL_REQUEST_SCHEMA = CELL_REQUEST_SCHEMA
    live.ATTEMPT_LEDGER_SCHEMA = ATTEMPT_LEDGER_SCHEMA
    live.COST_LEDGER_SCHEMA = COST_LEDGER_SCHEMA
    live.PREPROOF_TERMINAL_REASON_CODES = frozenset(
        {
            "provider_candidate_count_invalid",
            "provider_parts_count_invalid",
            "provider_part_non_text_invalid",
            "provider_candidate_not_json",
            "provider_candidate_not_object",
        }
    )
    live._names = _names
    live._request_packet = _request_packet
    live._attempt_ledger = _attempt_ledger
    live._initial_cost_ledger = _initial_cost_ledger
    live._run_attempt = _run_attempt


def run_tranche(
    *,
    mode: str,
    output_path: Path,
    cost_ledger_path: Path,
    source_review_path: Path | None,
) -> dict[str, Any]:
    if output_path.exists() or cost_ledger_path.exists():
        raise live.LiveError("tranche_output_already_exists")
    lock_path = cost_ledger_path.with_suffix(cost_ledger_path.suffix + ".run.lock")
    try:
        lock_descriptor = os.open(
            lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
        )
    except FileExistsError as error:
        raise live.LiveError("tranche_run_already_active") from error
    try:
        review = None
        if mode == "live":
            if source_review_path is None:
                raise live.LiveError("source_review_required")
            review = _validate_source_review(source_review_path)
            execution_context_path = OCCUPIED_CONTEXT_PATH
        else:
            execution_context_path = DRY_RUN_CONTEXT_PATH
        if execution_context_path.exists():
            raise live.LiveError("execution_context_already_exists")
        execution_context = contracts.materialize_execution_context(
            contracts.load_object(contracts.CONTEXT_PATH),
            observed_at=datetime.now(timezone.utc),
        )
        live._write_json(execution_context_path, execution_context)
        contracts.CONTEXT_PATH = execution_context_path
        contracts.RAYLEEN_CONTEXT_PATH = execution_context_path
        ledger = _initial_cost_ledger()
        live._write_json(cost_ledger_path, ledger)
        lane_results: list[dict[str, Any]] = []
        correction_of: str | None = None
        correction_reason: str | None = None
        for attempt_number in (1, 2):
            if (
                attempt_number == 2
                and correction_reason not in contracts.CORRECTION_REASON_CODES
            ):
                break
            ledger = live._reserve_cost(
                ledger, contracts.LANE_RAYLEEN, mode=mode
            )
            live._write_json(cost_ledger_path, ledger)
            preflight = None
            if mode == "live":
                preflight = live._run_preflight(
                    live._attempt_paths(
                        contracts.LANE_RAYLEEN,
                        attempt_number,
                        mode=mode,
                    )["preflight"]
                )
            attempt = _run_attempt(
                lane=contracts.LANE_RAYLEEN,
                mode=mode,
                attempt_number=attempt_number,
                correction_of=correction_of,
                correction_reason_code=correction_reason,
                preflight=preflight,
            )
            lane_results.append(attempt)
            ledger = live._reconcile_parent_consumption(ledger, lane_results)
            live._write_json(cost_ledger_path, ledger)
            if attempt["proofreader_verdict"] == "admitted":
                break
            if attempt.get("correction_eligible") is True:
                correction_of = attempt["attempt_id"]
                correction_reason = attempt["proofreader_reason_code"]
                continue
            break
        admitted = bool(
            lane_results
            and lane_results[-1]["proofreader_verdict"] == "admitted"
        )
        if mode == "dry-run" and not admitted:
            raise live.LiveError("provider_free_selector_not_admitted")
        ledger["status"] = "consumed"
        contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
        live._write_json(cost_ledger_path, ledger)
        evidence = _tranche_evidence(
            mode=mode,
            lane_results=lane_results,
            ledger=ledger,
            review=review,
            admitted=admitted,
            execution_context_path=execution_context_path,
            review_path=source_review_path,
        )
        live._write_json(output_path, evidence)
        return evidence
    finally:
        os.close(lock_descriptor)
        lock_path.unlink(missing_ok=True)


def _validate_prior_occupied_failure(
    *, prior_evidence_path: Path, prior_cost_ledger_path: Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    expected_evidence_path = ARTIFACT_ROOT / "occupied-selector-evidence.json"
    expected_cost_path = ARTIFACT_ROOT / "occupied-selector-cost-ledger.json"
    if (
        prior_evidence_path.resolve() != expected_evidence_path.resolve()
        or prior_cost_ledger_path.resolve() != expected_cost_path.resolve()
    ):
        raise live.LiveError("recovery_predecessor_path_invalid")
    evidence = contracts.load_object(prior_evidence_path)
    cost = contracts.load_object(prior_cost_ledger_path)
    observed_hash = evidence.get("evidence_hash")
    material = {key: value for key, value in evidence.items() if key != "evidence_hash"}
    lane_results = evidence.get("lane_results")
    attempt = lane_results[-1] if isinstance(lane_results, list) and lane_results else None
    if (
        observed_hash != contracts.prefixed_sha256(material)
        or evidence.get("result")
        != "model_required_bureau_a4_occupied_selector_terminal_rejection"
        or evidence.get("selector_admitted") is not False
        or evidence.get("candidate_runtime_provider_call_count") != 1
        or evidence.get("maximum_provider_calls") != contracts.MAX_CALLS_TOTAL
        or evidence.get("reserved_cost_usd") != contracts.RESERVED_COST_PER_CALL_USD
        or evidence.get("maximum_cost_usd") != contracts.MAX_COST_USD
        or not isinstance(attempt, dict)
        or attempt.get("attempt_id") != "a4-rayleen-selector-primary-001"
        or attempt.get("provider_call_count") != 1
        or attempt.get("proofreader_verdict") != "rejected"
        or attempt.get("proofreader_reason_code") != "selector_not_grounded"
        or attempt.get("release") is not None
        or attempt.get("cleanup_passed") is not True
        or any(
            evidence.get(key) != 0
            for key in (
                "patient_or_clinical_data_count",
                "database_access_count",
                "command_count",
                "write_count",
                "actuator_count",
                "provider_tool_call_count",
                "fallback_count",
                "cloud_or_iam_mutation_count",
                "deployment_count",
                "protected_ref_movement_count",
            )
        )
        or evidence.get("raw_prompt_retained") is not False
        or evidence.get("raw_provider_response_retained") is not False
    ):
        raise live.LiveError("recovery_predecessor_evidence_invalid")
    contracts.validate_instance(COST_LEDGER_SCHEMA, cost)
    if cost != {
        "schema_version": "emr4.model_required_bureau_a4.cost_ledger.v1",
        "tranche_id": "model-required-bureau-a4-occupied-selector-001",
        "status": "consumed",
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "provider_calls_reserved": 1,
        "provider_calls_consumed": 1,
        "reserved_cost_usd": contracts.RESERVED_COST_PER_CALL_USD,
        "lane_calls": {contracts.LANE_RAYLEEN: 1},
        "fallback_permitted": False,
    }:
        raise live.LiveError("recovery_predecessor_cost_ledger_invalid")
    predecessor_context = ROOT / str(evidence.get("execution_context_path"))
    if (
        predecessor_context.resolve() != OCCUPIED_CONTEXT_PATH.resolve()
        or not predecessor_context.is_file()
        or evidence.get("execution_context_hash")
        != live._file_hash(predecessor_context)
    ):
        raise live.LiveError("recovery_predecessor_context_binding_invalid")
    return evidence, cost, attempt


def run_recovery(
    *,
    mode: str,
    output_path: Path,
    cost_ledger_path: Path,
    source_review_path: Path | None,
    prior_evidence_path: Path,
    prior_cost_ledger_path: Path,
) -> dict[str, Any]:
    if mode not in {"dry-run", "live"}:
        raise live.LiveError("recovery_mode_invalid")
    if output_path.exists() or cost_ledger_path.exists():
        raise live.LiveError("recovery_output_already_exists")
    predecessor, prior_cost, prior_attempt = _validate_prior_occupied_failure(
        prior_evidence_path=prior_evidence_path,
        prior_cost_ledger_path=prior_cost_ledger_path,
    )
    lock_path = cost_ledger_path.with_suffix(cost_ledger_path.suffix + ".run.lock")
    try:
        lock_descriptor = os.open(
            lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
        )
    except FileExistsError as error:
        raise live.LiveError("recovery_run_already_active") from error
    try:
        review = None
        if mode == "live":
            if source_review_path is None:
                raise live.LiveError("recovery_source_review_required")
            review = _validate_source_review(
                source_review_path,
                expected_path=RECOVERY_SOURCE_REVIEW_RECEIPT,
            )
            execution_context_path = RECOVERY_OCCUPIED_CONTEXT_PATH
        else:
            if source_review_path is not None:
                raise live.LiveError("provider_free_source_review_not_expected")
            execution_context_path = RECOVERY_DRY_RUN_CONTEXT_PATH
        if execution_context_path.exists():
            raise live.LiveError("recovery_execution_context_already_exists")
        execution_context = contracts.materialize_execution_context(
            contracts.load_object(contracts.CONTEXT_PATH),
            observed_at=datetime.now(timezone.utc),
        )
        live._write_json(execution_context_path, execution_context)
        contracts.CONTEXT_PATH = execution_context_path
        contracts.RAYLEEN_CONTEXT_PATH = execution_context_path
        if mode == "live":
            ledger = json.loads(json.dumps(prior_cost))
            ledger["status"] = "open"
        else:
            ledger = _initial_cost_ledger()
        ledger = live._reserve_cost(
            ledger, contracts.LANE_RAYLEEN, mode=mode
        )
        live._write_json(cost_ledger_path, ledger)
        preflight = None
        if mode == "live":
            preflight = live._run_preflight(
                live._attempt_paths(
                    contracts.LANE_RAYLEEN, 2, mode=mode
                )["preflight"]
            )
        attempt = _run_attempt(
            lane=contracts.LANE_RAYLEEN,
            mode=mode,
            attempt_number=2,
            correction_of=prior_attempt["attempt_id"],
            correction_reason_code="selector_not_grounded",
            preflight=preflight,
        )
        lane_results = (
            [prior_attempt, attempt] if mode == "live" else [attempt]
        )
        ledger = live._reconcile_parent_consumption(ledger, lane_results)
        ledger["status"] = "consumed"
        contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
        live._write_json(cost_ledger_path, ledger)
        admitted = attempt["proofreader_verdict"] == "admitted"
        if mode == "dry-run" and not admitted:
            raise live.LiveError("provider_free_selector_recovery_not_admitted")
        evidence = _tranche_evidence(
            mode=mode,
            lane_results=lane_results,
            ledger=ledger,
            review=review,
            admitted=admitted,
            execution_context_path=execution_context_path,
            review_path=source_review_path,
        )
        evidence["recovery_reason_code"] = "selector_not_grounded"
        evidence["predecessor_evidence_hash"] = live._file_hash(
            prior_evidence_path
        )
        evidence["predecessor_cost_ledger_hash"] = live._file_hash(
            prior_cost_ledger_path
        )
        evidence["predecessor_provider_calls_consumed"] = 1
        evidence["provider_calls_during_recovery"] = (
            attempt["provider_call_count"]
        )
        evidence.pop("evidence_hash", None)
        evidence["evidence_hash"] = contracts.prefixed_sha256(evidence)
        live._write_json(output_path, evidence)
        return evidence
    finally:
        os.close(lock_descriptor)
        lock_path.unlink(missing_ok=True)


def main() -> int:
    _configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("dry-run", "live", "recovery-dry-run", "recovery-live"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-ledger", type=Path, required=True)
    parser.add_argument("--source-review", type=Path)
    parser.add_argument("--prior-evidence", type=Path)
    parser.add_argument("--prior-cost-ledger", type=Path)
    args = parser.parse_args()
    try:
        if args.mode.startswith("recovery-"):
            if args.prior_evidence is None or args.prior_cost_ledger is None:
                raise live.LiveError("recovery_predecessor_required")
            evidence = run_recovery(
                mode=args.mode.removeprefix("recovery-"),
                output_path=args.output,
                cost_ledger_path=args.cost_ledger,
                source_review_path=args.source_review,
                prior_evidence_path=args.prior_evidence,
                prior_cost_ledger_path=args.prior_cost_ledger,
            )
        else:
            evidence = run_tranche(
                mode=args.mode,
                output_path=args.output,
                cost_ledger_path=args.cost_ledger,
                source_review_path=args.source_review,
            )
    except (live.LiveError, OSError, subprocess.SubprocessError) as error:
        print(
            json.dumps(
                {
                    "result": "model_required_bureau_a4_selector_blocked",
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
                "selector_admitted": evidence["selector_admitted"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
