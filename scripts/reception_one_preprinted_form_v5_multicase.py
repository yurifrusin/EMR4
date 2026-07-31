#!/usr/bin/env python3
"""Evaluate the frozen Reception One v5 form across six synthetic cases."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_audit as turn_audit
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_preprinted_form_v5_live as preprinted_live
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-preprinted-form-v5-multicase"
)
MANIFEST_PATH = ARTIFACT_DIR / "evaluation-manifest.json"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-cohort-evidence.json"
EXPECTED_CASES = (
    ("create", "known-create", "create", "create", True),
    ("resize", "known-resize", "resize", "resize", True),
    ("cancel", "known-cancel", "cancel", "cancel", True),
    ("status", "known-status", "status_change", "status_change", True),
    (
        "squeeze",
        "novel-squeeze-in",
        "squeeze_in_assessment",
        "squeeze_in_assessment",
        True,
    ),
    ("clarify", None, "clarification", "clarification", False),
)
MANIFEST_SCHEMA_VERSION = (
    "reception.one.preprinted_form_v5.multicase_manifest.v1"
)
PROVIDER_BLOCKED_SCHEMA_VERSION = (
    "reception.one.preprinted_form_v5.multicase_provider_blocked.v1"
)
PROVIDER_BLOCKED_RESULT = (
    "reception_one_preprinted_form_v5_multicase_provider_blocked_pass"
)
OCCUPIED_SCHEMA_VERSION = (
    "reception.one.preprinted_form_v5.multicase_occupied.v1"
)
OCCUPIED_PASS_RESULT = (
    "reception_one_preprinted_form_v5_multicase_occupied_pass"
)
OCCUPIED_FAIL_RESULT = (
    "reception_one_preprinted_form_v5_multicase_occupied_fail"
)
BLOCKED_RESULT = "reception_one_preprinted_form_v5_multicase_blocked"
HISTORICAL_ANCHOR = {
    "case_id": "known-move",
    "source_result": "reception_one_preprinted_form_v5_occupied_pass",
    "replayed": False,
}
EXPECTED_PRIMARY_CALLS = 6
EXPECTED_CORRECTION_CALLS = 6
EXPECTED_ABSOLUTE_CALL_CEILING = 12
CANDID_LIMIT = (
    "This cohort measures only six frozen authored-synthetic form tasks "
    "through the configured and observed Sydney Vertex locational request "
    "path. It does not prove Australian physical or sovereign processing, "
    "general model reliability, production fitness or safety for real, "
    "product, patient, health, clinical or historical data."
)
EXACT_PROVIDER_BOUNDARY = {
    "provider": "google_cloud_vertex_ai",
    "model": broker.MODEL,
    "project": broker.PROJECT,
    "service_account": broker.SERVICE_ACCOUNT,
    "authentication": "keyless_impersonated_service_account_adc",
    "location": broker.LOCATION,
    "endpoint_hostname": broker.HOSTNAME,
    "fallback_permitted": False,
}


class MulticaseError(RuntimeError):
    """A frozen-cohort contract or lifecycle rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MulticaseError("json_object_unreadable") from error
    if not isinstance(value, dict):
        raise MulticaseError("json_object_required")
    return value


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _text_hash(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _content_hash(value: dict[str, Any]) -> str:
    without_hash = copy.deepcopy(value)
    without_hash.pop("evidence_hash", None)
    return preprinted.canonical_hash(without_hash)


def _validate_manifest(document: dict[str, Any]) -> list[dict[str, Any]]:
    if (
        document.get("schema_version")
        != MANIFEST_SCHEMA_VERSION
        or document.get("data_class") != "authored_synthetic"
        or document.get("effect_ceiling") != "proposal_only"
        or document.get("historical_anchor") != HISTORICAL_ANCHOR
        or document.get("provider_boundary") != EXACT_PROVIDER_BOUNDARY
        or document.get("maximum_primary_calls") != EXPECTED_PRIMARY_CALLS
        or document.get("maximum_correction_calls")
        != EXPECTED_CORRECTION_CALLS
        or document.get("absolute_call_ceiling")
        != EXPECTED_ABSOLUTE_CALL_CEILING
        or document.get("incremental_cost_ceiling_usd") != 1
    ):
        raise MulticaseError("evaluation_manifest_boundary_invalid")
    frozen = document.get("frozen_condition")
    if frozen != {
        "few_shot_examples": False,
        "demonstration_answers": False,
        "prompt_optimisation": False,
        "fine_tuning": False,
        "temperature": 0,
        "thinking_budget": 0,
        "mid_cohort_prompt_or_schema_change": False,
    }:
        raise MulticaseError("evaluation_manifest_not_frozen")
    authority = document.get("authority")
    if authority != {
        "product_or_database_access": False,
        "patient_health_or_clinical_data": False,
        "confirmation_authority": False,
        "appointment_write_authority": False,
        "provider_tools": False,
        "product_delivery": False,
    }:
        raise MulticaseError("evaluation_manifest_authority_open")
    cases = document.get("cases")
    if not isinstance(cases, list) or len(cases) != len(EXPECTED_CASES):
        raise MulticaseError("evaluation_case_set_invalid")
    observed = [
        (
            case.get("case_code"),
            case.get("source_case_id"),
            case.get("expected_goal"),
            case.get("expected_proposal_family"),
            case.get("expected_proposal_release"),
        )
        for case in cases
        if isinstance(case, dict)
    ]
    if observed != list(EXPECTED_CASES):
        raise MulticaseError("evaluation_case_set_invalid")
    if any(case["case_code"] == "move" for case in cases):
        raise MulticaseError("historical_anchor_replay_forbidden")
    return cases


def load_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    document = _load_object(MANIFEST_PATH)
    return document, _validate_manifest(document)


def frame_for_case(
    case: dict[str, Any],
    cases_document: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = cases_document or typed_plan.load_json(typed_plan.CASES_PATH)
    source_case_id = case.get("source_case_id")
    if source_case_id is not None:
        source_case = next(
            (
                item
                for item in source["cases"]
                if item.get("case_id") == source_case_id
            ),
            None,
        )
        if source_case is None:
            raise MulticaseError("source_case_missing")
        frame = typed_plan.expand_case(source, source_case)
    else:
        frame = copy.deepcopy(source["shared_input"])
        frame["request_id"] = case["request_id"]
        frame["correlation_id"] = case["correlation_id"]
        frame["utterances"] = copy.deepcopy(case["utterances"])
        typed_plan.validate_schema(frame, "input")
    if (
        frame.get("data_class") != "authored_synthetic"
        or frame.get("authority", {}).get("effect_ceiling")
        != "proposal_only"
        or any(
            frame.get("authority", {}).get(field) is not False
            for field in (
                "appointment_write_authority",
                "confirmation_authority",
                "provider_execution",
                "network_access",
                "database_access",
                "product_delivery",
            )
        )
    ):
        raise MulticaseError("case_frame_boundary_invalid")
    return frame


def _operator_note(goal: str) -> str:
    subject = (
        "clarification request"
        if goal == "clarification"
        else goal.replace("_", "-") + " proposal"
    )
    return f"Prepared a {subject} for review; no booking was changed."


def oracle_for_case(
    case: dict[str, Any],
    frame: dict[str, Any],
) -> dict[str, Any]:
    plan = typed_plan.deterministic_plan(frame)
    if plan["goal"] != case["expected_goal"]:
        raise MulticaseError("oracle_goal_mismatch")
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=_operator_note(plan["goal"]),
    )
    body = preprinted.model_form_body(program)
    if preprinted.assemble_program(body) != program:
        raise MulticaseError("oracle_preprinted_assembly_mismatch")
    turn_input = preprinted.build_turn_input(frame)
    request = preprinted.build_vertex_request(turn_input)
    evaluation = preprinted.evaluate_program(frame, program, turn_code=1)
    violation_codes = sorted(
        {item["code"] for item in evaluation["violations"]}
    )
    release = None
    if evaluation["disposition"] == "admit":
        release = typed_plan.execute_plan(
            frame,
            evaluation["normalized_plan"],
            evaluation["semantic_review"],
        )["final_output"]
    if case["expected_proposal_release"]:
        if (
            evaluation["disposition"] != "admit"
            or release is None
            or release["proposal_family"]
            != case["expected_proposal_family"]
            or release["api_spine_operation_id"]
            != case["expected_api_spine_operation_id"]
            or release["requires_human_confirmation"] is not True
            or release["write_performed"] is not False
        ):
            raise MulticaseError("actionable_oracle_not_admitted")
    elif (
        evaluation["disposition"] != "admit"
        or evaluation["correction_eligible"] is not False
        or release is None
        or release["kind"] != case["expected_typed_output_kind"]
        or release["proposal_family"] != "clarification"
        or release["api_spine_operation_id"] is not None
        or release["requires_human_confirmation"] is not False
        or release["write_performed"] is not False
    ):
        raise MulticaseError("clarification_oracle_not_safe")
    return {
        "case_code": case["case_code"],
        "frame_sha256": preprinted.canonical_hash(frame),
        "task_sha256": turn_input["task_sha256"],
        "model_input_sha256": preprinted.canonical_hash(turn_input),
        "provider_request_sha256": preprinted.canonical_hash(request),
        "provider_response_schema_sha256": preprinted.canonical_hash(
            preprinted.vertex_response_schema()
        ),
        "oracle_goal": plan["goal"],
        "oracle_program_sha256": preprinted.canonical_hash(program),
        "oracle_model_form_body_sha256": preprinted.canonical_hash(body),
        "oracle_operator_ids": [
            step["operator"] for step in plan["steps"]
        ],
        "proofreader_disposition": evaluation["disposition"],
        "proofreader_violation_codes": violation_codes,
        "correction_eligible": evaluation["correction_eligible"],
        "expected_proposal_release": case["expected_proposal_release"],
        "expected_final_output": release,
    }


def _case_ids(case_code: str) -> tuple[tuple[str, str], tuple[str, str]]:
    attempts = tuple(
        f"reception-one-preprinted-form-v5-eval-{case_code}-turn-{index:03d}"
        for index in (1, 2)
    )
    ledgers = tuple(
        f"reception-one-preprinted-form-v5-eval-{case_code}-ledger-{index:03d}"
        for index in (1, 2)
    )
    for attempt_id, ledger_id in zip(attempts, ledgers, strict=True):
        try:
            broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
        except broker.BrokerError as error:
            raise MulticaseError("case_identifier_pair_invalid") from error
    return attempts, ledgers


def build_provider_blocked_evidence(
    *,
    write_frames: bool,
) -> dict[str, Any]:
    manifest, cases = load_manifest()
    source = typed_plan.load_json(typed_plan.CASES_PATH)
    oracles: list[dict[str, Any]] = []
    identifiers: list[dict[str, Any]] = []
    for case in cases:
        frame = frame_for_case(case, source)
        if write_frames:
            _write_json(FRAMES_DIR / f"{case['case_code']}.json", frame)
        oracles.append(oracle_for_case(case, frame))
        attempts, ledgers = _case_ids(case["case_code"])
        identifiers.append(
            {
                "case_code": case["case_code"],
                "attempt_ids": list(attempts),
                "ledger_ids": list(ledgers),
            }
        )
    cross_case_pair_rejected = False
    try:
        broker.validate_attempt_ledger_pair(
            identifiers[0]["attempt_ids"][0],
            identifiers[1]["ledger_ids"][0],
        )
    except broker.BrokerError:
        cross_case_pair_rejected = True
    if not cross_case_pair_rejected:
        raise MulticaseError("cross_case_ledger_pair_admitted")
    result: dict[str, Any] = {
        "schema_version": PROVIDER_BLOCKED_SCHEMA_VERSION,
        "result": PROVIDER_BLOCKED_RESULT,
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "historical_anchor_replayed": False,
        "case_count": len(oracles),
        "contract": {
            "manifest_file_sha256": _file_hash(MANIFEST_PATH),
            "manifest_content_sha256": preprinted.canonical_hash(manifest),
            "system_instruction_sha256": _text_hash(
                preprinted.SYSTEM_INSTRUCTION
            ),
            "model_form_schema_file_sha256": _file_hash(
                preprinted.MODEL_FORM_BODY_SCHEMA_PATH
            ),
            "turn_input_schema_file_sha256": _file_hash(
                preprinted.TURN_INPUT_SCHEMA_PATH
            ),
            "correction_ticket_schema_file_sha256": _file_hash(
                preprinted.CORRECTION_TICKET_SCHEMA_PATH
            ),
            "provider_response_schema_sha256": preprinted.canonical_hash(
                preprinted.vertex_response_schema()
            ),
            "preprinted_fields": preprinted.PREPRINTED_FIELDS,
            "model_authored_fields": list(
                preprinted.MODEL_AUTHORED_FIELDS
            ),
            "temperature": 0,
            "thinking_budget": 0,
            "prompt_or_schema_change_within_cohort": False,
            "broker_judgement_repair": False,
        },
        "case_oracles": oracles,
        "single_use_identifiers": identifiers,
        "cross_case_ledger_pair_rejected": cross_case_pair_rejected,
        "training_condition": {
            "few_shot_examples": False,
            "demonstration_answers": False,
            "prompt_optimisation": False,
            "fine_tuning": False,
            "weight_change": False,
        },
        "boundary": {
            "raw_provider_request_retained": False,
            "raw_provider_response_retained": False,
            "credentials_or_tokens_retained": False,
            "api_key_information_retained": False,
            "database_access": False,
            "appointment_write": False,
            "product_delivery": False,
            "provider_tools": False,
            "fallback": False,
        },
    }
    result["evidence_hash"] = _content_hash(result)
    return result


def _validate_provider_blocked_evidence(
    recorded: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    expected = build_provider_blocked_evidence(write_frames=False)
    if recorded != expected or recorded.get("evidence_hash") != _content_hash(
        recorded
    ):
        raise MulticaseError("provider_blocked_binding_changed")
    return {
        item["case_code"]: item for item in recorded["case_oracles"]
    }


def _cleanup_passed(cleanup: dict[str, Any]) -> bool:
    return bool(cleanup) and all(
        value
        for key, value in cleanup.items()
        if key != "daemon_wide_prune_performed"
    )


def _violations_from_turn(turn_path: Path) -> list[str]:
    turn = _load_object(turn_path)
    proofreader = turn.get("exchange", {}).get("proofreader") or {}
    return sorted(
        {
            item.get("code")
            for item in proofreader.get("violations", [])
            if isinstance(item, dict) and isinstance(item.get("code"), str)
        }
    )


def _case_observation(
    *,
    case: dict[str, Any],
    oracle: dict[str, Any],
    case_dir: Path,
    dialogue: dict[str, Any],
) -> dict[str, Any]:
    actual_calls = dialogue["actual_provider_call_count"]
    if actual_calls not in {1, 2}:
        raise MulticaseError("case_call_budget_invalid")
    turns = dialogue["turns"]
    if len(turns) != actual_calls or not all(
        _cleanup_passed(turn["cleanup"]) for turn in turns
    ):
        raise MulticaseError("case_cleanup_invalid")
    audits: list[dict[str, Any]] = []
    for index in range(1, actual_calls + 1):
        audit = _load_object(
            case_dir / f"occupied-turn-{index:03d}-external-audit.json"
        )
        if (
            audit.get("durable_hash_chain", {}).get("valid") is not True
            or audit.get("preprinted_form", {}).get(
                "broker_judgement_repair"
            )
            is not False
            or audit.get("api_key_authentication_used") is not False
        ):
            raise MulticaseError("case_external_audit_invalid")
        audits.append(audit)
    first_violations = _violations_from_turn(
        case_dir / "occupied-turn-001-evidence.json"
    )
    final_violations = _violations_from_turn(
        case_dir
        / f"occupied-turn-{actual_calls:03d}-evidence.json"
    )
    release = dialogue.get("release")
    expected_safe = _expected_safe_outcome(
        case=case,
        oracle=oracle,
        dialogue=dialogue,
    )
    exact_binding = dialogue.get("exact_binding") or {}
    if (
        exact_binding.get("model_id") != broker.MODEL
        or exact_binding.get("project") != broker.PROJECT
        or exact_binding.get("service_account") != broker.SERVICE_ACCOUNT
        or exact_binding.get("location") != broker.LOCATION
        or exact_binding.get("endpoint_hostname") != broker.HOSTNAME
        or exact_binding.get("api_key_authentication_used") is not False
    ):
        raise MulticaseError("case_provider_binding_invalid")
    provider_outcomes = [audit["provider_outcome"] for audit in audits]
    return {
        "case_code": case["case_code"],
        "source_case_id": case.get("source_case_id"),
        "expected_goal": case["expected_goal"],
        "expected_proposal_family": case["expected_proposal_family"],
        "expected_proposal_release": case["expected_proposal_release"],
        "expected_safe_outcome": expected_safe,
        "primary_exact_body_accepted": (
            audits[0]["provider_outcome"]["status"] == "completed"
            and audits[0]["preprinted_form"]["raw_model_form_body_recorded"]
            is False
        ),
        "primary_proofreader_disposition": turns[0][
            "proofreader_disposition"
        ],
        "primary_violation_codes": first_violations,
        "correction_used": actual_calls == 2,
        "final_proofreader_disposition": turns[-1][
            "proofreader_disposition"
        ],
        "final_violation_codes": final_violations,
        "terminal_status": dialogue["terminal_status"],
        "actual_provider_calls": actual_calls,
        "provider_outcomes": provider_outcomes,
        "admitted_operator_ids": (
            audits[-1].get("proofreader", {}).get(
                "admitted_operator_ids", []
            )
        ),
        "operator_note": audits[-1].get("operator_note"),
        "typed_program": audits[-1].get("typed_program"),
        "release": release,
        "parent_audit_chain": dialogue["parent_audit_chain"],
        "cleanup_passed": all(
            _cleanup_passed(turn["cleanup"]) for turn in turns
        ),
        "exact_binding": exact_binding,
    }


def _expected_safe_outcome(
    *,
    case: dict[str, Any],
    oracle: dict[str, Any],
    dialogue: dict[str, Any],
) -> bool:
    """Score a closed safe case without aborting the remaining cohort."""

    release = dialogue.get("release")
    if case["expected_proposal_release"]:
        return (
            release == oracle["expected_final_output"]
            and dialogue["terminal_status"]
            in {"admitted", "admitted_after_correction"}
        )
    return bool(
        isinstance(release, dict)
        and release == oracle["expected_final_output"]
        and dialogue["terminal_status"]
        in {"admitted", "admitted_after_correction"}
        and release["kind"] == case["expected_typed_output_kind"]
        and release["api_spine_operation_id"] is None
        and release["write_performed"] is False
    )


def _training_disposition(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    primary_expected_safe = all(
        observation["primary_proofreader_disposition"] == "admit"
        and observation["expected_safe_outcome"]
        for observation in observations
    )
    clusters: dict[str, list[str]] = {}
    for observation in observations:
        if observation["correction_used"]:
            signature = ",".join(observation["primary_violation_codes"])
            clusters.setdefault(signature, []).append(
                observation["case_code"]
            )
    repeated = {
        signature: cases
        for signature, cases in clusters.items()
        if signature and len(cases) >= 2
    }
    isolated = {
        signature: cases
        for signature, cases in clusters.items()
        if signature and len(cases) == 1
    }
    if primary_expected_safe:
        decision = "keep_untaught_prompt"
    elif repeated:
        decision = "nominate_minimal_prompt_context_teaching"
    else:
        decision = "diagnose_without_teaching"
    result = {
        "decision": decision,
        "all_six_primary_expected_safe": primary_expected_safe,
        "repeated_correctable_error_clusters": repeated,
        "isolated_correctable_error_clusters": isolated,
        "provider_contract_errors_are_training_evidence": False,
    }
    unexpected_safe_outcome_cases = [
        observation["case_code"]
        for observation in observations
        if not observation["expected_safe_outcome"]
    ]
    if unexpected_safe_outcome_cases:
        result["unexpected_safe_outcome_cases"] = (
            unexpected_safe_outcome_cases
        )
    return result


def _recovery_ids(
    case_code: str,
    recovery_sequence: int = 1,
) -> tuple[str, str]:
    if recovery_sequence < 1 or recovery_sequence > 8:
        raise MulticaseError("zero_call_recovery_ceiling_exceeded")
    recovery_case = f"{case_code}-r{recovery_sequence}"
    attempt_id = (
        "reception-one-preprinted-form-v5-eval-"
        f"{recovery_case}-turn-002"
    )
    ledger_id = (
        "reception-one-preprinted-form-v5-eval-"
        f"{recovery_case}-ledger-002"
    )
    broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
    return attempt_id, ledger_id


def _load_parent_events(path: Path) -> list[dict[str, Any]]:
    events = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    previous = preprinted_live.ZERO_HASH
    for index, event in enumerate(events, start=1):
        if (
            event.get("sequence") != index
            or event.get("previous_hash") != previous
        ):
            raise MulticaseError("partial_parent_audit_chain_invalid")
        without_hash = {
            key: value
            for key, value in event.items()
            if key != "event_hash"
        }
        if event.get("event_hash") != lane.canonical_hash(without_hash):
            raise MulticaseError("partial_parent_audit_chain_invalid")
        previous = event["event_hash"]
    if not events:
        raise MulticaseError("partial_parent_audit_chain_invalid")
    return events


def _zero_call_recovery_records(
    case_dir: Path,
) -> list[dict[str, Any]]:
    required = (
        "occupied-dialogue-parent-audit.jsonl",
        "occupied-turn-001-evidence.json",
        "occupied-turn-001-ledger.json",
        "occupied-turn-001-audit.jsonl",
        "occupied-turn-001-external-audit.json",
        "occupied-turn-001-correction-ticket.json",
        "occupied-turn-002-ledger.json",
        "occupied-turn-002-audit.jsonl",
    )
    forbidden = (
        "occupied-dialogue-evidence.json",
        "occupied-turn-002-evidence.json",
        "occupied-turn-002-external-audit.json",
    )
    if not all((case_dir / name).exists() for name in required):
        return []
    if any((case_dir / name).exists() for name in forbidden):
        return []
    original_attempts, original_ledgers = _case_ids(case_dir.name)
    candidates = [
        {
            "attempt_id": original_attempts[1],
            "ledger_id": original_ledgers[1],
            "ledger_path": (
                case_dir / "occupied-turn-002-ledger.json"
            ),
            "audit_path": (
                case_dir / "occupied-turn-002-audit.jsonl"
            ),
        }
    ]
    def recovery_sequence(path: Path) -> int:
        if path.name == "occupied-turn-002-recovery-ledger.json":
            return 1
        marker = "occupied-turn-002-recovery-"
        suffix = path.name.removeprefix(marker).removesuffix(
            "-ledger.json"
        )
        if not suffix.isdigit():
            raise MulticaseError("invalid_zero_call_recovery_ledger")
        return int(suffix)

    recovery_ledgers = sorted(
        case_dir.glob("occupied-turn-002-recovery*-ledger.json"),
        key=recovery_sequence,
    )
    for sequence, ledger_path in enumerate(
        recovery_ledgers,
        start=1,
    ):
        attempt_id, ledger_id = _recovery_ids(
            case_dir.name,
            sequence,
        )
        audit_name = ledger_path.name.replace(
            "-ledger.json",
            "-audit.jsonl",
        )
        candidates.append(
            {
                "attempt_id": attempt_id,
                "ledger_id": ledger_id,
                "ledger_path": ledger_path,
                "audit_path": case_dir / audit_name,
            }
        )
    for candidate in candidates:
        if not candidate["audit_path"].exists():
            return []
        ledger = _load_object(candidate["ledger_path"])
        events = preprinted_live.live._validate_audit(
            candidate["audit_path"]
        )
        if (
            ledger.get("status") != "consumed"
            or ledger.get("provider_calls_consumed") != 0
            or [event["event_type"] for event in events]
            != ["broker_ready"]
        ):
            return []
    return candidates


def _zero_call_correction_recovery_available(
    case_dir: Path,
) -> bool:
    return bool(_zero_call_recovery_records(case_dir))


def _resume_zero_call_correction(
    *,
    case_code: str,
    case_dir: Path,
    preflight_path: Path,
    authority_path: Path,
    expected_graph_revision: int,
    expected_compass_revision: int,
    frame_path: Path,
) -> dict[str, Any]:
    if not _zero_call_correction_recovery_available(case_dir):
        raise MulticaseError("partial_case_resume_forbidden")
    zero_call_records = _zero_call_recovery_records(case_dir)
    first = _load_object(
        case_dir / "occupied-turn-001-evidence.json"
    )
    first_external = _load_object(
        case_dir / "occupied-turn-001-external-audit.json"
    )
    ticket_path = (
        case_dir / "occupied-turn-001-correction-ticket.json"
    )
    ticket = _load_object(ticket_path)
    preprinted.validate_exact(
        ticket,
        preprinted.CORRECTION_TICKET_SCHEMA_PATH,
    )
    if (
        first.get("provider_call_count") != 1
        or first.get("exchange", {}).get("release") is not None
        or first.get("exchange", {}).get("correction_ticket") != ticket
        or first_external.get("durable_hash_chain", {}).get("valid")
        is not True
    ):
        raise MulticaseError("partial_case_first_turn_invalid")

    original_attempts, original_ledgers = _case_ids(case_code)
    if (
        first.get("attempt_id") != original_attempts[0]
        or first.get("ledger_id") != original_ledgers[0]
    ):
        raise MulticaseError("partial_case_first_turn_binding_invalid")
    recovery_sequence = len(zero_call_records)
    recovery_attempt, recovery_ledger = _recovery_ids(
        case_code,
        recovery_sequence,
    )
    evidence_path = case_dir / "occupied-turn-002-evidence.json"
    recovery_stem = "occupied-turn-002-recovery"
    if recovery_sequence > 1:
        recovery_stem += f"-{recovery_sequence:03d}"
    recovery_ledger_path = case_dir / f"{recovery_stem}-ledger.json"
    recovery_audit_path = case_dir / f"{recovery_stem}-audit.jsonl"
    external_path = (
        case_dir / "occupied-turn-002-external-audit.json"
    )

    parent_path = case_dir / "occupied-dialogue-parent-audit.jsonl"
    parent_events = _load_parent_events(parent_path)
    preprinted_live._append_parent_event(
        parent_path,
        parent_events,
        "turn_zero_call_aborted",
        {
            "turn_code": 2,
            "attempt_id": zero_call_records[-1]["attempt_id"],
            "ledger_id": zero_call_records[-1]["ledger_id"],
            "provider_calls_consumed": 0,
            "reason_code": "broker_did_not_exit_after_cell_relay_miss",
            "ledger_consumed": True,
            "retry_reuses_ledger": False,
        },
    )
    preprinted_live._append_parent_event(
        parent_path,
        parent_events,
        "turn_opened",
        {
            "turn_code": 2,
            "attempt_id": recovery_attempt,
            "ledger_id": recovery_ledger,
            "actual_call_ordinal": 2,
            "correction_ticket_hash": preprinted.canonical_hash(ticket),
            "zero_call_recovery": True,
        },
    )
    second = preprinted_live.live.run_live(
        evidence_path=evidence_path,
        ledger_path=recovery_ledger_path,
        audit_path=recovery_audit_path,
        attempt_id=recovery_attempt,
        ledger_id=recovery_ledger,
        preflight_path=preflight_path,
        authority_path=authority_path,
        expected_graph_revision=expected_graph_revision,
        expected_compass_revision=expected_compass_revision,
        frame_path=frame_path,
        contract_mode=preprinted.CONTRACT_MODE,
        correction_ticket_path=ticket_path,
    )
    second_external = turn_audit.build_external_audit(
        evidence_path,
        recovery_audit_path,
        preflight_path,
    )
    _write_json(external_path, second_external)
    preprinted_live._append_parent_event(
        parent_path,
        parent_events,
        "turn_closed",
        {
            "turn_code": 2,
            "attempt_id": second["attempt_id"],
            "ledger_id": second["ledger_id"],
            "result": second["result"],
            "audit_terminal_hash": second["exchange"][
                "audit_terminal_hash"
            ],
            "proofreader_disposition": (
                second["exchange"].get("proofreader") or {}
            ).get("disposition"),
            "correction_ticket_hash": second["exchange"].get(
                "correction_ticket_hash"
            ),
            "released": second["exchange"].get("release") is not None,
            "cleanup_passed": all(
                value
                for key, value in second["cleanup"].items()
                if key != "daemon_wide_prune_performed"
            ),
            "zero_call_recovery": True,
        },
    )
    preprinted_live._append_parent_event(
        parent_path,
        parent_events,
        "dialogue_closed",
        {
            "status": (
                "admitted_after_correction"
                if second["exchange"].get("release") is not None
                else "terminal_no_release"
            ),
            "actual_provider_calls": 2,
            "zero_call_attempts": 1,
            "third_provider_call_performed": False,
            "fallback_performed": False,
        },
    )
    evidence = preprinted_live.build_parent_evidence(
        turns=[first, second],
        external_audits=[first_external, second_external],
        parent_events=parent_events,
        attempt_ids=(original_attempts[0], recovery_attempt),
        ledger_ids=(original_ledgers[0], recovery_ledger),
    )
    evidence["zero_call_recovery"] = {
        "reason_code": "broker_did_not_exit_after_cell_relay_miss",
        "consumed_zero_call_attempt_ids": [
            record["attempt_id"] for record in zero_call_records
        ],
        "consumed_zero_call_ledger_ids": [
            record["ledger_id"] for record in zero_call_records
        ],
        "recovery_attempt_id": recovery_attempt,
        "recovery_ledger_id": recovery_ledger,
        "recovery_audit_file": recovery_audit_path.name,
        "provider_calls_added": 1,
        "provider_call_ceiling_changed": False,
        "prompt_or_schema_changed": False,
        "prior_call_replayed": False,
        "ledger_reused": False,
    }
    evidence["evidence_hash"] = _content_hash(evidence)
    _write_json(
        case_dir / "occupied-dialogue-evidence.json",
        evidence,
    )
    return evidence


def run_occupied(
    *,
    preflight_path: Path,
    authority_path: Path,
    expected_graph_revision: int,
    expected_compass_revision: int,
) -> dict[str, Any]:
    manifest, cases = load_manifest()
    recorded_provider_blocked = _load_object(PROVIDER_BLOCKED_PATH)
    oracles = _validate_provider_blocked_evidence(
        recorded_provider_blocked
    )
    if OCCUPIED_PATH.exists():
        raise MulticaseError("occupied_cohort_output_already_exists")
    observations: list[dict[str, Any]] = []
    total_calls = 0
    for case in cases:
        case_code = case["case_code"]
        case_dir = ARTIFACT_DIR / "cases" / case_code
        attempts, ledgers = _case_ids(case_code)
        parent_path = case_dir / "occupied-dialogue-evidence.json"
        if parent_path.exists():
            dialogue = _load_object(parent_path)
            recovery = dialogue.get("zero_call_recovery")
            expected_attempts = list(
                attempts[: dialogue.get("actual_provider_call_count")]
            )
            expected_ledgers = list(
                ledgers[: dialogue.get("actual_provider_call_count")]
            )
            if isinstance(recovery, dict):
                expected_attempts = [
                    attempts[0],
                    recovery.get("recovery_attempt_id"),
                ]
                expected_ledgers = [
                    ledgers[0],
                    recovery.get("recovery_ledger_id"),
                ]
            if (
                dialogue.get("attempt_ids") != expected_attempts
                or dialogue.get("ledger_ids") != expected_ledgers
                or dialogue.get("parent_audit_chain", {}).get("valid")
                is not True
            ):
                raise MulticaseError("closed_case_resume_binding_invalid")
            for index in range(
                1, dialogue["actual_provider_call_count"] + 1
            ):
                audit_path = (
                    case_dir
                    / f"occupied-turn-{index:03d}-audit.jsonl"
                )
                if isinstance(recovery, dict) and index == 2:
                    audit_path = (
                        case_dir
                        / recovery["recovery_audit_file"]
                    )
                regenerated = turn_audit.build_external_audit(
                    case_dir
                    / f"occupied-turn-{index:03d}-evidence.json",
                    audit_path,
                    preflight_path,
                )
                _write_json(
                    case_dir
                    / f"occupied-turn-{index:03d}-external-audit.json",
                    regenerated,
                )
        else:
            if case_dir.exists() and any(case_dir.iterdir()):
                dialogue = _resume_zero_call_correction(
                    case_code=case_code,
                    case_dir=case_dir,
                    preflight_path=preflight_path,
                    authority_path=authority_path,
                    expected_graph_revision=expected_graph_revision,
                    expected_compass_revision=expected_compass_revision,
                    frame_path=FRAMES_DIR / f"{case_code}.json",
                )
            else:
                dialogue = preprinted_live.run_dialogue(
                    artifact_dir=case_dir,
                    preflight_path=preflight_path,
                    authority_path=authority_path,
                    expected_graph_revision=expected_graph_revision,
                    expected_compass_revision=expected_compass_revision,
                    frame_path=FRAMES_DIR / f"{case_code}.json",
                    attempt_ids=attempts,
                    ledger_ids=ledgers,
                )
        observation = _case_observation(
            case=case,
            oracle=oracles[case_code],
            case_dir=case_dir,
            dialogue=dialogue,
        )
        observations.append(observation)
        total_calls += observation["actual_provider_calls"]
        if total_calls > manifest["absolute_call_ceiling"]:
            raise MulticaseError("cohort_call_ceiling_exceeded")
    training = _training_disposition(observations)
    passed = all(
        observation["expected_safe_outcome"]
        and observation["cleanup_passed"]
        for observation in observations
    )
    result: dict[str, Any] = {
        "schema_version": OCCUPIED_SCHEMA_VERSION,
        "result": OCCUPIED_PASS_RESULT if passed else OCCUPIED_FAIL_RESULT,
        "capability_threshold_passed": passed,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "historical_anchor_replayed": False,
        "case_count": len(observations),
        "total_actual_provider_calls": total_calls,
        "absolute_provider_call_ceiling": manifest[
            "absolute_call_ceiling"
        ],
        "incremental_cost_ceiling_usd": manifest[
            "incremental_cost_ceiling_usd"
        ],
        "provider_blocked_evidence_hash": recorded_provider_blocked[
            "evidence_hash"
        ],
        "continuity_binding": {
            "graph_revision": expected_graph_revision,
            "compass_revision": expected_compass_revision,
            "prompt_or_schema_change_within_cohort": False,
        },
        "cases": observations,
        "training_disposition": training,
        "all_ledgers_consumed": all(
            all(
                _load_object(path).get("status") == "consumed"
                for path in (
                    ARTIFACT_DIR
                    / "cases"
                    / observation["case_code"]
                ).glob("*-ledger.json")
            )
            for observation in observations
        ),
        "all_cleanup_passed": all(
            observation["cleanup_passed"]
            for observation in observations
        ),
        "explicit_exclusions": {
            "raw_prompt_recorded": False,
            "raw_provider_response_recorded": False,
            "credential_or_token_recorded": False,
            "api_key_information_recorded": False,
            "chain_of_thought_recorded": False,
            "broker_judgement_repair": False,
            "semantic_safe_repair": False,
            "product_or_database_access": False,
            "appointment_write": False,
            "human_or_product_delivery": False,
            "provider_or_regional_fallback": False,
        },
        "candid_limit": CANDID_LIMIT,
    }
    if (
        result["all_ledgers_consumed"] is not True
        or result["all_cleanup_passed"] is not True
    ):
        raise MulticaseError("cohort_cleanup_or_ledger_failure")
    result["evidence_hash"] = _content_hash(result)
    _write_json(OCCUPIED_PATH, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    blocked = subparsers.add_parser("provider-blocked")
    blocked.add_argument("--output", type=Path, default=PROVIDER_BLOCKED_PATH)
    occupied = subparsers.add_parser("occupied")
    occupied.add_argument("--preflight", type=Path, required=True)
    occupied.add_argument("--authority", type=Path, default=AUTHORITY_PATH)
    occupied.add_argument("--graph-revision", type=int, required=True)
    occupied.add_argument("--compass-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == "provider-blocked":
            evidence = build_provider_blocked_evidence(write_frames=True)
            _write_json(args.output, evidence)
        else:
            evidence = run_occupied(
                preflight_path=args.preflight,
                authority_path=args.authority,
                expected_graph_revision=args.graph_revision,
                expected_compass_revision=args.compass_revision,
            )
    except (
        MulticaseError,
        preprinted_live.PreprintedLiveError,
        lane.ModelLaneError,
        ValueError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": (
                        BLOCKED_RESULT
                    ),
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
                "case_count": evidence["case_count"],
                "provider_calls": evidence.get(
                    "total_actual_provider_calls", 0
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
