#!/usr/bin/env python3
"""Provider-free acceptance for the model-required Bureau A3/B3 tranche."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import model_required_bureau_a3_b3_contracts as contracts
from scripts import model_required_bureau_a3_b3_live as live


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
DRY_RUN_EVIDENCE = ARTIFACT_ROOT / "provider-free-dry-run-evidence.json"
TERMINAL_INTERRUPTION_SCHEMA = (
    ARTIFACT_ROOT / "occupied-terminal-interruption.schema.json"
)
TERMINAL_INTERRUPTION_EVIDENCE = (
    ARTIFACT_ROOT / "occupied-terminal-interruption-evidence.json"
)
OCCUPIED_COST_LEDGER = ARTIFACT_ROOT / "occupied-rehearsal-cost-ledger.json"
OCCUPIED_TRANCHE_EVIDENCE = ARTIFACT_ROOT / "occupied-rehearsal-evidence.json"
SOURCE_REVIEW_RECEIPT = (
    ROOT
    / "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-a3-b3-review-6-receipt.json"
)


def _check(condition: bool, name: str, checks: dict[str, bool]) -> None:
    checks[name] = bool(condition)
    if not condition:
        raise contracts.ContractError(name)


def _model_body(lane: str, candidate: dict[str, object]) -> dict[str, object]:
    broker_owned = {
        "schema_version",
        "case_id",
        "candidate_provenance",
        "context_revision",
        "content_revision",
        "risk_tier",
        "human_confirmation_required",
        "confirmation_authorized",
        "apply_authorized",
        "writes_authorized",
        "success_claimed",
    }
    body = {key: value for key, value in candidate.items() if key not in broker_owned}
    schema = (
        contracts.RAYLEEN_MODEL_BODY_SCHEMA_PATH
        if lane == contracts.LANE_RAYLEEN
        else contracts.DAVIDA_MODEL_BODY_SCHEMA_PATH
    )
    contracts.validate_instance(schema, body)
    return body


def run_acceptance(*, require_dry_run: bool) -> dict[str, object]:
    checks: dict[str, bool] = {}
    required_paths = [
        ROOT / "docs/emr4-model-required-bureau-a3-b3-occupied-rehearsal-plan.md",
        ROOT / "docs/security/emr4-model-required-bureau-a3-b3-threat-model-delta.md",
        ARTIFACT_ROOT / "a3-b3-contract.json",
        ARTIFACT_ROOT / "a3-b3-contract.schema.json",
        ARTIFACT_ROOT / "occupied-authority.json",
        ARTIFACT_ROOT / "occupied-authority.schema.json",
        contracts.RAYLEEN_CONTEXT_PATH,
        contracts.RAYLEEN_CONTEXT_SCHEMA_PATH,
        contracts.RAYLEEN_MODEL_BODY_SCHEMA_PATH,
        contracts.RAYLEEN_CANDIDATE_PATH,
        contracts.RAYLEEN_CANDIDATE_SCHEMA_PATH,
        contracts.RAYLEEN_RELEASE_SCHEMA_PATH,
        contracts.DAVIDA_CONTEXT_PATH,
        contracts.DAVIDA_CONTEXT_SCHEMA_PATH,
        contracts.DAVIDA_MODEL_BODY_SCHEMA_PATH,
        contracts.DAVIDA_CANDIDATE_PATH,
        contracts.DAVIDA_CANDIDATE_SCHEMA_PATH,
        contracts.DAVIDA_RELEASE_SCHEMA_PATH,
        ARTIFACT_ROOT / "cell-request.schema.json",
        ARTIFACT_ROOT / "single-use-ledger.schema.json",
        ARTIFACT_ROOT / "cost-ledger.schema.json",
        ARTIFACT_ROOT / "occupied-preflight-blocked.schema.json",
        ARTIFACT_ROOT / "occupied-preflight-blocked-evidence.json",
        TERMINAL_INTERRUPTION_SCHEMA,
        TERMINAL_INTERRUPTION_EVIDENCE,
        OCCUPIED_COST_LEDGER,
        SOURCE_REVIEW_RECEIPT,
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-preflight.json",
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-occupied-ledger.json",
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-occupied-audit.jsonl",
        ARTIFACT_ROOT / "Dockerfile",
        ROOT / "scripts/model_required_bureau_a3_b3_broker.py",
        ROOT / "scripts/model_required_bureau_a3_b3_live.py",
        ROOT / "tests/test_model_required_bureau_a3_b3.py",
    ]
    _check(all(path.is_file() for path in required_paths), "artifact_manifest_complete", checks)

    for schema_path in (
        ARTIFACT_ROOT / "a3-b3-contract.schema.json",
        ARTIFACT_ROOT / "occupied-authority.schema.json",
        contracts.RAYLEEN_CONTEXT_SCHEMA_PATH,
        contracts.RAYLEEN_MODEL_BODY_SCHEMA_PATH,
        contracts.RAYLEEN_CANDIDATE_SCHEMA_PATH,
        contracts.RAYLEEN_RELEASE_SCHEMA_PATH,
        contracts.DAVIDA_CONTEXT_SCHEMA_PATH,
        contracts.DAVIDA_MODEL_BODY_SCHEMA_PATH,
        contracts.DAVIDA_CANDIDATE_SCHEMA_PATH,
        contracts.DAVIDA_RELEASE_SCHEMA_PATH,
        ARTIFACT_ROOT / "cell-request.schema.json",
        ARTIFACT_ROOT / "single-use-ledger.schema.json",
        ARTIFACT_ROOT / "cost-ledger.schema.json",
        ARTIFACT_ROOT / "occupied-preflight-blocked.schema.json",
        TERMINAL_INTERRUPTION_SCHEMA,
    ):
        Draft202012Validator.check_schema(contracts.load_object(schema_path))
    _check(True, "draft_2020_12_schemas_valid", checks)

    contract = contracts.load_object(contracts.CONTRACT_PATH)
    authority = contracts.load_object(ARTIFACT_ROOT / "occupied-authority.json")
    contracts.validate_instance(
        ARTIFACT_ROOT / "a3-b3-contract.schema.json", contract
    )
    contracts.validate_instance(
        ARTIFACT_ROOT / "occupied-authority.schema.json", authority
    )
    blocked_preflight = contracts.load_object(
        ARTIFACT_ROOT / "occupied-preflight-blocked-evidence.json"
    )
    blocked_cost_ledger_path = (
        OCCUPIED_COST_LEDGER
    )
    contracts.validate_instance(
        ARTIFACT_ROOT / "occupied-preflight-blocked.schema.json",
        blocked_preflight,
    )
    current_cost_ledger = contracts.load_object(blocked_cost_ledger_path)
    contracts.validate_instance(
        ARTIFACT_ROOT / "cost-ledger.schema.json", current_cost_ledger
    )
    terminal_interruption = contracts.load_object(
        TERMINAL_INTERRUPTION_EVIDENCE
    )
    contracts.validate_instance(
        TERMINAL_INTERRUPTION_SCHEMA, terminal_interruption
    )
    original_parent_hash = terminal_interruption["source_artifact_hashes"][
        "parent_cost_ledger"
    ]
    initial_reserved = live._reserve_cost(
        live._initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
    )
    terminal_consumed = deepcopy(initial_reserved)
    terminal_consumed["provider_calls_consumed"] = 1
    terminal_consumed["status"] = "consumed"
    parent_state = (
        "interruption_preserved"
        if current_cost_ledger == initial_reserved
        else "terminal_reconciled"
        if current_cost_ledger == terminal_consumed
        else "invalid"
    )
    _check(
        blocked_preflight["cost_ledger_sha256"]
        == original_parent_hash
        and blocked_preflight["provider_call_count"] == 0
        and blocked_preflight["provider_prompt_transmitted"] is False
        and blocked_preflight["runtime_residue_absent"] is True
        and parent_state != "invalid"
        and (
            parent_state == "terminal_reconciled"
            or live._file_hash(blocked_cost_ledger_path) == original_parent_hash
        ),
        "occupied_preflight_blocked_evidence_exact",
        checks,
    )
    _check(
        authority["exact_boundary"]["model"] == contracts.MODEL
        and authority["exact_boundary"]["project"] == contracts.PROJECT
        and authority["exact_boundary"]["service_account"] == contracts.SERVICE_ACCOUNT
        and authority["exact_boundary"]["location"] == contracts.LOCATION
        and authority["exact_boundary"]["endpoint_hostname"] == contracts.HOSTNAME,
        "authority_exact_provider_binding",
        checks,
    )

    ray_context = contracts.load_object(contracts.RAYLEEN_CONTEXT_PATH)
    ray_candidate = contracts.load_object(contracts.RAYLEEN_CANDIDATE_PATH)
    davida_context = contracts.load_object(contracts.DAVIDA_CONTEXT_PATH)
    davida_candidate = contracts.load_object(contracts.DAVIDA_CANDIDATE_PATH)
    contracts.validate_rayleen_context(ray_context)
    contracts.validate_davida_context(davida_context)

    rayleen_packet = live._request_packet(
        contracts.LANE_RAYLEEN,
        ray_context,
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    occupied_preflight_path = (
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-preflight.json"
    )
    occupied_attempt_ledger_path = (
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-occupied-ledger.json"
    )
    occupied_audit_path = (
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-occupied-audit.jsonl"
    )
    occupied_attempt_evidence_path = (
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-occupied-evidence.json"
    )
    occupied_attempt_ledger = contracts.load_object(
        occupied_attempt_ledger_path
    )
    contracts.validate_instance(
        ARTIFACT_ROOT / "single-use-ledger.schema.json",
        occupied_attempt_ledger,
    )
    expected_attempt_ledger = live._attempt_ledger(
        rayleen_packet, mode="live"
    )
    expected_attempt_ledger["status"] = "consumed"
    expected_attempt_ledger["provider_calls_consumed"] = 1
    occupied_events = live._read_events(occupied_audit_path)
    occupied_classification = live._classify_attempt_events(
        occupied_events, mode="live"
    )
    admitted_event = next(
        event
        for event in occupied_events
        if event.get("event_type") == "request_admitted"
    )
    admitted_fields = admitted_event.get("fields")
    _check(
        occupied_attempt_ledger == expected_attempt_ledger
        and occupied_classification
        == {
            "terminal_preproof_rejection": True,
            "reason_code": "provider_content_invalid",
            "correction_eligible": False,
            "provider_metadata": None,
        }
        and isinstance(admitted_fields, dict)
        and all(
            admitted_fields.get(key) == rayleen_packet[key]
            for key in (
                "lane",
                "attempt_id",
                "ledger_id",
                "policy_id",
                "context_hash",
                "provider_request_hash",
            )
        )
        and terminal_interruption["source_artifact_hashes"]
        == {
            "parent_cost_ledger": original_parent_hash,
            "read_only_preflight": live._file_hash(occupied_preflight_path),
            "attempt_ledger": live._file_hash(occupied_attempt_ledger_path),
            "audit_chain": live._file_hash(occupied_audit_path),
        }
        and terminal_interruption["provider_call_count"] == 1
        and terminal_interruption["proofreader_reached"] is False
        and terminal_interruption["correction_eligible"] is False
        and terminal_interruption["release_created"] is False
        and terminal_interruption["davida_b3_started"] is False,
        "occupied_terminal_interruption_exact",
        checks,
    )

    permitted_occupied_attempt_paths = {
        occupied_preflight_path,
        occupied_attempt_ledger_path,
        occupied_audit_path,
        occupied_attempt_evidence_path,
    }
    observed_occupied_attempt_paths = {
        *ARTIFACT_ROOT.glob("*-attempt-*-occupied-*"),
        *ARTIFACT_ROOT.glob("*-attempt-*-preflight.json"),
    }
    _check(
        not (
            observed_occupied_attempt_paths
            - permitted_occupied_attempt_paths
        )
        and not OCCUPIED_COST_LEDGER.with_suffix(
            OCCUPIED_COST_LEDGER.suffix + ".run.lock"
        ).exists(),
        "no_rayleen_correction_or_davida_attempt",
        checks,
    )

    terminal_summary: dict[str, object]
    if parent_state == "interruption_preserved":
        _check(
            not occupied_attempt_evidence_path.exists()
            and not OCCUPIED_TRANCHE_EVIDENCE.exists(),
            "terminal_reconciliation_not_partially_written",
            checks,
        )
        terminal_summary = {
            "state": parent_state,
            "candidate_runtime_provider_call_count": 1,
            "terminal_reason_code": "provider_content_invalid",
            "reconciliation_was_provider_free": None,
        }
    else:
        _check(
            occupied_attempt_evidence_path.is_file()
            and OCCUPIED_TRANCHE_EVIDENCE.is_file(),
            "terminal_reconciliation_artifacts_present",
            checks,
        )
        occupied_attempt_evidence = contracts.load_object(
            occupied_attempt_evidence_path
        )
        occupied_tranche_evidence = contracts.load_object(
            OCCUPIED_TRANCHE_EVIDENCE
        )
        runtime_absence = live._exact_runtime_absence(
            contracts.LANE_RAYLEEN, 1
        )
        source_artifact_hashes = {
            "preflight": live._file_hash(occupied_preflight_path),
            "attempt_ledger": live._file_hash(
                occupied_attempt_ledger_path
            ),
            "audit": live._file_hash(occupied_audit_path),
            "prior_parent_cost_ledger": original_parent_hash,
            "blocked_preflight_evidence": live._file_hash(
                ARTIFACT_ROOT / "occupied-preflight-blocked-evidence.json"
            ),
            "terminal_interruption_evidence": live._file_hash(
                TERMINAL_INTERRUPTION_EVIDENCE
            ),
        }
        expected_attempt_evidence = {
            "schema_version": (
                "emr4.model_required_bureau_a3_b3.attempt_evidence.v1"
            ),
            "result": "attempt_terminal_rejection",
            "mode": "live",
            "lane": contracts.LANE_RAYLEEN,
            "attempt_id": rayleen_packet["attempt_id"],
            "attempt_number": 1,
            "provider_contacted": True,
            "provider_call_count": 1,
            "request_binding": {
                key: rayleen_packet[key]
                for key in (
                    "policy_id",
                    "context_hash",
                    "provider_request_hash",
                )
            },
            "preflight_hash": source_artifact_hashes["preflight"],
            "proofreader_verdict": "not_reached",
            "proofreader_reason_code": "provider_content_invalid",
            "correction_eligible": False,
            "release": None,
            "provider_metadata": None,
            "provider_metadata_status": "not_durably_recorded",
            "current_runtime_absence": {
                **runtime_absence,
                "daemon_wide_prune_performed": False,
            },
            "current_runtime_residue_absent": True,
            "original_attempt_cleanup_evidence_status": (
                "not_durably_recorded_beyond_immutable_interruption_assertion"
            ),
            "reconciled_after_interrupted_harness": True,
            "source_artifact_hashes": source_artifact_hashes,
            "raw_prompt_retained": False,
            "raw_provider_response_retained": False,
            "credential_or_token_retained": False,
            "product_read_count": 0,
            "database_access_count": 0,
            "command_count": 0,
            "write_count": 0,
            "actuator_count": 0,
        }
        expected_attempt_evidence["evidence_hash"] = (
            contracts.prefixed_sha256(expected_attempt_evidence)
        )
        current_head = live._git_head()
        review = live._historical_source_review(
            SOURCE_REVIEW_RECEIPT, current_head=current_head
        )
        reconciliation_source_head = occupied_tranche_evidence.get(
            "reconciliation_source_head"
        )
        reconciliation_source_is_ancestor = False
        if isinstance(reconciliation_source_head, str):
            ancestry = subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    reconciliation_source_head,
                    current_head,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                shell=False,
            )
            reconciliation_source_is_ancestor = ancestry.returncode == 0
        expected_tranche_evidence = live._tranche_evidence(
            mode="live",
            result_name=(
                "model_required_bureau_a3_b3_occupied_terminal_rejection"
            ),
            lane_results=[expected_attempt_evidence],
            ledger=terminal_consumed,
            review=review,
            combined_pass=False,
        )
        expected_tranche_evidence.update(
            {
                "terminal_lane": contracts.LANE_RAYLEEN,
                "terminal_reason_code": "provider_content_invalid",
                "correction_eligible": False,
                "provider_call_source_head": review["head_before"],
                "reconciliation_source_head": reconciliation_source_head,
                "reconciliation_was_provider_free": True,
                "source_artifact_hashes": source_artifact_hashes,
                "reconciliation_source_hashes": (
                    live._reconciliation_source_hashes()
                ),
            }
        )
        expected_tranche_evidence.pop("evidence_hash")
        expected_tranche_evidence["evidence_hash"] = (
            contracts.prefixed_sha256(expected_tranche_evidence)
        )
        _check(
            reconciliation_source_is_ancestor
            and occupied_attempt_evidence == expected_attempt_evidence
            and occupied_tranche_evidence == expected_tranche_evidence,
            "terminal_reconciliation_exact",
            checks,
        )
        terminal_summary = {
            "state": parent_state,
            "candidate_runtime_provider_call_count": 1,
            "terminal_reason_code": "provider_content_invalid",
            "reconciliation_was_provider_free": True,
            "attempt_evidence_hash": occupied_attempt_evidence[
                "evidence_hash"
            ],
            "tranche_evidence_hash": occupied_tranche_evidence[
                "evidence_hash"
            ],
        }
    _check(
        contracts.proofread_rayleen(ray_candidate, ray_context)["verdict"] == "admitted"
        and contracts.proofread_davida(davida_candidate, davida_context)["verdict"] == "admitted",
        "canonical_candidates_admitted",
        checks,
    )

    for lane, context, candidate in (
        (contracts.LANE_RAYLEEN, ray_context, ray_candidate),
        (contracts.LANE_DAVIDA, davida_context, davida_candidate),
    ):
        body = _model_body(lane, candidate)
        wrapped = contracts.wrap_provider_body(lane, body, context)
        _check(
            wrapped == candidate and contracts.proofread(lane, wrapped, context)["verdict"] == "admitted",
            f"{lane}_selector_wrapper_exact",
            checks,
        )
        request = contracts.build_vertex_request(lane, context)
        serialized = contracts.canonical_bytes(request)
        _check(
            set(request) == {"contents", "generationConfig"}
            and b'"tools"' not in serialized
            and b'"cachedContent"' not in serialized
            and b'"grounding"' not in serialized
            and b'"functionCall"' not in serialized,
            f"{lane}_provider_request_closed",
            checks,
        )

    wrong_focus = deepcopy(ray_candidate)
    wrong_focus["focus_appointment_id"] = ray_candidate["evidence_appointment_ids"][1]
    _check(
        contracts.proofread_rayleen(wrong_focus, ray_context)["verdict"] == "rejected",
        "rayleen_wrong_focus_rejected",
        checks,
    )
    forged_authority = _model_body(contracts.LANE_RAYLEEN, ray_candidate)
    forged_authority["writes_authorized"] = True
    try:
        contracts.wrap_provider_body(contracts.LANE_RAYLEEN, forged_authority, ray_context)
    except contracts.ContractError:
        pass
    else:
        raise contracts.ContractError("model_authority_forgery_not_rejected")
    checks["model_authority_forgery_rejected"] = True

    wrong_kind = deepcopy(davida_candidate)
    wrong_kind["practitioner_ref"] = "location-south"
    _check(
        contracts.proofread_davida(wrong_kind, davida_context)["reason_code"] == "wrong_resource_kind",
        "davida_cross_kind_rejected",
        checks,
    )
    wrong_dry_run = deepcopy(davida_candidate)
    wrong_dry_run["dry_run_proposal_hash"] = "0" * 64
    _check(
        contracts.proofread_davida(wrong_dry_run, davida_context)["reason_code"] == "dry_run_hash_mismatch",
        "davida_dry_run_forgery_rejected",
        checks,
    )

    source_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "scripts/model_required_bureau_a3_b3_contracts.py",
            "scripts/model_required_bureau_a3_b3_broker.py",
            "scripts/model_required_bureau_a3_b3_live.py",
        )
    )
    _check(
        "from app." not in source_text
        and "import app." not in source_text
        and "sqlalchemy" not in source_text.lower(),
        "no_product_or_database_imports",
        checks,
    )

    dry_run_summary: dict[str, object] | None = None
    if require_dry_run:
        dry_run = contracts.load_object(DRY_RUN_EVIDENCE)
        lane_results = dry_run.get("lane_results")
        audit_paths = sorted(ARTIFACT_ROOT.glob("*-attempt-1-audit.jsonl"))
        audit_events = [live._read_events(path) for path in audit_paths]
        _check(
            dry_run.get("result") == "model_required_bureau_a3_b3_provider_free_dry_run_pass"
            and isinstance(lane_results, list)
            and len(lane_results) == 2
            and all(item.get("provider_contacted") is False for item in lane_results)
            and all(item.get("proofreader_verdict") == "admitted" for item in lane_results)
            and all(item.get("cleanup_passed") is True for item in lane_results),
            "provider_free_broker_cell_dry_run_passed",
            checks,
        )
        _check(
            len(audit_events) == 2
            and all(
                [event["event_type"] for event in events].count(
                    "provider_call_started"
                )
                == 0
                and [event["event_type"] for event in events].count(
                    "provider_fixture_completed"
                )
                == 1
                and [event["event_type"] for event in events].count(
                    "proofreader_completed"
                )
                == 1
                for events in audit_events
            ),
            "provider_free_audit_chains_valid_and_zero_call",
            checks,
        )
        dry_run_summary = {
            "evidence_hash": dry_run.get("evidence_hash"),
            "provider_call_count": 0,
        }

    return {
        "schema_version": "emr4.model_required_bureau_a3_b3.provider_free_acceptance.v1",
        "result": "model_required_bureau_a3_b3_provider_free_acceptance_pass",
        "checks": checks,
        "provider_call_count": 0,
        "patient_or_clinical_data_count": 0,
        "product_read_count": 0,
        "database_access_count": 0,
        "command_count": 0,
        "write_count": 0,
        "actuator_count": 0,
        "deployment_count": 0,
        "protected_ref_movement_count": 0,
        "dry_run": dry_run_summary,
        "occupied_terminal_state": terminal_summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-dry-run", action="store_true")
    args = parser.parse_args()
    result = run_acceptance(require_dry_run=args.require_dry_run)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
