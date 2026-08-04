#!/usr/bin/env python3
"""Provider-free acceptance for the model-required Bureau A3/B3 tranche."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import model_required_bureau_a3_b3_contracts as contracts
from scripts import model_required_bureau_a3_b3_live as live


ARTIFACT_ROOT = contracts.ARTIFACT_ROOT
DRY_RUN_EVIDENCE = ARTIFACT_ROOT / "provider-free-dry-run-evidence.json"


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
