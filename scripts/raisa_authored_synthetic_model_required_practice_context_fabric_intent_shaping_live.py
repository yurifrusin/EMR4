#!/usr/bin/env python3
"""Run the isolated provider-free or occupied model-required intent-shaping cell.

The live controller reuses the accepted A3/B3 and A4 one-shot transport and
ledger principles without modifying their modules or artifacts.  Later live
mode requires an exact reviewed-source hash map and one fresh source-review
receipt, runs the existing read-only preflight, reserves a single-use ledger
per call, admits exactly one response/candidate/non-thought part, consumes the
ledger after every provider call, and forbids any call after admission or any
fallback.  Dry-run makes zero provider calls and uses the canonical synthetic
provider packet through the identical parser, wrapper and proofreaders.
"""

from __future__ import annotations

import argparse
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
from scripts import (
    raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts as contracts,
)


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
CELL_REQUEST_SCHEMA = ARTIFACT_ROOT / "cell-request.schema.json"
ATTEMPT_LEDGER_SCHEMA = ARTIFACT_ROOT / "single-use-ledger.schema.json"
COST_LEDGER_SCHEMA = ARTIFACT_ROOT / "cost-ledger.schema.json"
OCCUPIED_EVIDENCE_SCHEMA = ARTIFACT_ROOT / "occupied-rehearsal-evidence.schema.json"
SOURCE_REVIEW_RECEIPT = ROOT / (
    "orchestration/agent_inbox/codex/"
    "raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-source-review-receipt.json"
)
OCCUPIED_CONTEXT_PATH = (
    ARTIFACT_ROOT / "occupied-authored-synthetic-intent-shaping-request.json"
)
DRY_RUN_CONTEXT_PATH = (
    ARTIFACT_ROOT / "provider-free-authored-synthetic-intent-shaping-request.json"
)

REVIEWED_SOURCE_PATHS = (
    ROOT / "scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts.py",
    ROOT / "scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_broker.py",
    ROOT / "scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_live.py",
    ROOT / "scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_acceptance.py",
    ROOT / "tests/test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal.py",
    ARTIFACT_ROOT / "intent-shaping-request.schema.json",
    ARTIFACT_ROOT / "provider-intent-body.schema.json",
    ARTIFACT_ROOT / "model-intent-candidate-envelope.schema.json",
    ARTIFACT_ROOT / "cell-request.schema.json",
    ARTIFACT_ROOT / "single-use-ledger.schema.json",
    ARTIFACT_ROOT / "cost-ledger.schema.json",
    ARTIFACT_ROOT / "occupied-rehearsal-evidence.schema.json",
    ARTIFACT_ROOT / "authored-synthetic-intent-shaping-request.json",
)

_PARENT_RUN_ATTEMPT = live._run_attempt
_PARENT_POPEN = live.subprocess.Popen


def _names(_lane: str, attempt_number: int) -> dict[str, str]:
    suffix = f"context-fabric-intent-shaping-{attempt_number}"
    return {
        "network": f"emr4-raisaintent-{suffix}-internal",
        "relay_container": f"emr4-raisaintent-{suffix}-relay",
        "cell_container": f"emr4-raisaintent-{suffix}-cell",
        "relay_image": f"emr4-raisaintent-{suffix}-relay:v1",
        "cell_image": f"emr4-raisaintent-{suffix}-cell:v1",
    }


def _request_packet(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_of: str | None,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    if lane != contracts.LANE:
        raise live.LiveError("lane_invalid")
    kind = "primary" if attempt_number == 1 else "correction"
    request = contracts.provider_request_for_attempt(
        context,
        attempt_number=attempt_number,
        correction_reason_code=correction_reason_code,
    )
    packet = {
        "schema_version": "emr4.raisa_intent_shaping.cell_request.v1",
        "lane": lane,
        "attempt_id": f"raisa-intent-shaping-{kind}-{attempt_number:03d}",
        "ledger_id": f"ledger-raisa-intent-shaping-{kind}-{attempt_number:03d}",
        "policy_id": contracts.POLICY_ID,
        "context_hash": contracts.prefixed_sha256(context),
        "provider_request_hash": contracts.prefixed_sha256(request),
        "attempt_number": attempt_number,
        "correction_of": correction_of,
        "correction_reason_code": correction_reason_code,
    }
    contracts.validate_instance(CELL_REQUEST_SCHEMA, packet)
    return packet


def _attempt_ledger(packet: dict[str, Any], *, mode: str) -> dict[str, Any]:
    live_mode = mode == "live"
    ledger = {
        "schema_version": "emr4.raisa_intent_shaping.single_use_ledger.v1",
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
        "schema_version": "emr4.raisa_intent_shaping.cost_ledger.v1",
        "tranche_id": "raisa-intent-shaping-occupied-001",
        "status": "open",
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "provider_calls_reserved": 0,
        "provider_calls_consumed": 0,
        "reserved_cost_usd": 0,
        "lane_calls": {contracts.LANE: 0},
        "fallback_permitted": False,
    }
    contracts.validate_instance(COST_LEDGER_SCHEMA, ledger)
    return ledger


def _intent_popen(
    arguments: Any, *positional: Any, **keywords: Any
) -> subprocess.Popen[bytes]:
    adjusted = (
        list(arguments) if isinstance(arguments, (list, tuple)) else arguments
    )
    if isinstance(adjusted, list):
        adjusted = [
            (
                "scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_broker"
                if item == "scripts.model_required_bureau_a3_b3_broker"
                else item
            )
            for item in adjusted
        ]
    return _PARENT_POPEN(adjusted, *positional, **keywords)


def _positive_thinking_evidence(metadata: dict[str, Any]) -> bool:
    return contracts.positive_thinking_evidence(metadata)


def _run_attempt(**keywords: Any) -> dict[str, Any]:
    live.subprocess.Popen = _intent_popen
    try:
        evidence = _PARENT_RUN_ATTEMPT(**keywords)
    finally:
        live.subprocess.Popen = _PARENT_POPEN
    # Positive-thinking enforcement is terminal and ledger-accountable inside
    # the broker ``_execute``: a missing/non-integer/non-positive reported
    # thinking count in live mode releases nothing, returns a structured
    # pre-proof ``positive_thinking_evidence_required`` result after the
    # provider call has consumed its single-use ledger, and is never
    # correction-eligible.  This wrapper therefore never raises after a release
    # has been created nor strands the tranche cost ledger before
    # reconciliation.  Provider-free dry-run remains eligible with zero tokens.
    evidence["schema_version"] = (
        "emr4.raisa_intent_shaping.attempt_evidence.v1"
    )
    evidence["evidence_mode"] = (
        contracts.EVIDENCE_LABEL_PROVIDER_FREE
        if evidence["mode"] == "dry-run"
        else contracts.EVIDENCE_LABEL_OCCUPIED
    )
    evidence["parent_retrieval_recomputed"] = True
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
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    ).stdout.strip()
    if (
        path.resolve() != expected_path.resolve()
        or receipt.get("schema_version")
        != "emr4.raisa_intent_shaping.source_review.v1"
        or receipt.get("status") != "passed"
        or receipt.get("decision") != "pass"
        or receipt.get("independent_read_only_review") is not True
        or receipt.get("provider_called") is not False
        or receipt.get("source_hashes") != expected_hashes
        or receipt.get("closed_boundary_verified") is not True
        # A passing review receipt must bind to exact equal
        # ``head_before``/``head_after``, ``dirty_after: false`` and the
        # current candidate HEAD.  This prevents an unreviewed accepted-parent
        # or transport edit from entering the occupied run.
        or not isinstance(receipt.get("head_before"), str)
        or receipt.get("head_before") != head
        or receipt.get("head_after") != receipt.get("head_before")
        or receipt.get("dirty_after") is not False
        # Occupied validation also requires the current tracked worktree to be
        # unchanged from HEAD while unrelated preserved untracked
        # receipt/evidence files remain permitted.
        or not live._tracked_worktree_clean()
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
        "raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal_pass"
        if admitted
        else "raisa_intent_shaping_occupied_terminal_rejection"
    )
    evidence = {
        "schema_version": "emr4.raisa_intent_shaping.tranche_evidence.v1",
        "result": result,
        "evidence_label": (
            contracts.EVIDENCE_LABEL_PROVIDER_FREE
            if mode == "dry-run"
            else contracts.EVIDENCE_LABEL_OCCUPIED
        ),
        "mode": mode,
        "combined_pass": admitted,
        "intent_admitted": admitted,
        "lane_results": lane_results,
        "candidate_runtime_provider_call_count": ledger[
            "provider_calls_consumed"
        ],
        "maximum_provider_calls": contracts.MAX_CALLS_TOTAL,
        "reserved_cost_usd": ledger["reserved_cost_usd"],
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "source_review_transport_nonzero": review is not None,
        "source_review_receipt_hash": (
            live._file_hash(review_path)
            if review and review_path
            else None
        ),
        "source_hashes": _review_source_hashes(),
        "execution_context_path": execution_context_path.relative_to(
            ROOT
        ).as_posix(),
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
    live.PREPROOF_TERMINAL_REASON_CODES = contracts.PREPROOF_TERMINAL_REASON_CODES
    live._names = _names
    live._request_packet = _request_packet
    live._attempt_ledger = _attempt_ledger
    live._initial_cost_ledger = _initial_cost_ledger
    live._run_attempt = _run_attempt
    # The A3/B3 live internals select the context by lane name.  Bind the
    # intent-shaping lane to the Rayleen branch and point both context paths
    # at the committed authored-synthetic request.
    contracts.LANE_RAYLEEN = contracts.LANE
    contracts.LANE_DAVIDA = "closed_not_allocated"
    contracts.RAYLEEN_CONTEXT_PATH = contracts.REQUEST_FIXTURE_PATH
    contracts.DAVIDA_CONTEXT_PATH = contracts.REQUEST_FIXTURE_PATH


def run_tranche(
    *,
    mode: str,
    output_path: Path,
    cost_ledger_path: Path,
    source_review_path: Path | None,
) -> dict[str, Any]:
    if mode not in {"dry-run", "live"}:
        raise live.LiveError("mode_invalid")
    if output_path.exists() or cost_ledger_path.exists():
        raise live.LiveError("tranche_output_already_exists")
    lock_path = cost_ledger_path.with_suffix(
        cost_ledger_path.suffix + ".run.lock"
    )
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
            if source_review_path is not None:
                raise live.LiveError("provider_free_source_review_not_expected")
            execution_context_path = DRY_RUN_CONTEXT_PATH
        if execution_context_path.exists():
            raise live.LiveError("execution_context_already_exists")
        execution_context = contracts.build_intent_shaping_request()
        live._write_json(execution_context_path, execution_context)
        contracts.RAYLEEN_CONTEXT_PATH = execution_context_path
        contracts.DAVIDA_CONTEXT_PATH = execution_context_path
        contracts.REQUEST_FIXTURE_PATH = execution_context_path
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
                ledger, contracts.LANE, mode=mode
            )
            live._write_json(cost_ledger_path, ledger)
            preflight = None
            if mode == "live":
                preflight = live._run_preflight(
                    live._attempt_paths(
                        contracts.LANE, attempt_number, mode=mode
                    )["preflight"]
                )
            attempt = _run_attempt(
                lane=contracts.LANE,
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
            raise live.LiveError("provider_free_intent_shaping_not_admitted")
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


def main() -> int:
    _configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=("dry-run", "live"), required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-ledger", type=Path, required=True)
    parser.add_argument("--source-review", type=Path)
    args = parser.parse_args()
    try:
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
                    "result": "raisa_intent_shaping_blocked",
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
                "intent_admitted": evidence["intent_admitted"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
