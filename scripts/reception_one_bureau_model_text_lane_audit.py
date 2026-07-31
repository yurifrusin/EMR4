#!/usr/bin/env python3
"""Build bounded external audit and provider-blocked diagnosis for model text lane."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as live


def _event_by_type(
    events: list[dict[str, Any]], event_type: str
) -> dict[str, Any] | None:
    return next(
        (event for event in events if event.get("event_type") == event_type),
        None,
    )


def build_external_audit(
    evidence_path: Path, audit_path: Path, preflight_path: Path
) -> dict[str, Any]:
    evidence = lane.load_object(evidence_path)
    preflight = lane.load_object(preflight_path)
    events = live._validate_audit(audit_path)
    constructed = _event_by_type(events, "provider_request_constructed")
    failed = _event_by_type(events, "provider_call_failed")
    received = _event_by_type(events, "provider_call_received")
    completed = _event_by_type(events, "provider_call_completed")
    rejected = _event_by_type(events, "broker_rejected")
    proof = _event_by_type(events, "proofreader_completed")
    release = _event_by_type(events, "release_committed")
    operator_note = _event_by_type(events, "operator_note_evaluated")
    receptionist_output = _event_by_type(
        events, "receptionist_response_evaluated"
    )
    correction_ticket = _event_by_type(events, "correction_ticket_issued")
    dialogue_match = broker.DIALOGUE_ATTEMPT_PATTERN.fullmatch(
        evidence["attempt_id"]
    )
    preprinted_standard_match = broker.PREPRINTED_ATTEMPT_PATTERN.fullmatch(
        evidence["attempt_id"]
    )
    preprinted_multicase_match = (
        broker.PREPRINTED_MULTICASE_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    preprinted_match = (
        preprinted_standard_match or preprinted_multicase_match
    )
    receptionist_v6_match = broker.RECEPTIONIST_V6_ATTEMPT_PATTERN.fullmatch(
        evidence["attempt_id"]
    )
    receptionist_v61_match = (
        broker.RECEPTIONIST_V61_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v62_match = (
        broker.RECEPTIONIST_V62_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v63_match = (
        broker.RECEPTIONIST_V63_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v64_match = (
        broker.RECEPTIONIST_V64_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v65_match = (
        broker.RECEPTIONIST_V65_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v66_match = (
        broker.RECEPTIONIST_V66_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v67_match = (
        broker.RECEPTIONIST_V67_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_v68_match = (
        broker.RECEPTIONIST_V68_ATTEMPT_PATTERN.fullmatch(
            evidence["attempt_id"]
        )
    )
    receptionist_match = (
        receptionist_v68_match
        or receptionist_v67_match
        or receptionist_v66_match
        or receptionist_v65_match
        or receptionist_v64_match
        or receptionist_v63_match
        or receptionist_v62_match
        or receptionist_v61_match
        or receptionist_v6_match
    )
    structured_match = broker.STRUCTURED_SOURCE_ATTEMPT_PATTERN.fullmatch(
        evidence["attempt_id"]
    )
    shared_match = broker.SHARED_TYPED_ATTEMPT_PATTERN.fullmatch(
        evidence["attempt_id"]
    )
    typed_match = (
        receptionist_match
        or preprinted_match
        or dialogue_match
        or structured_match
        or shared_match
    )
    typed_attempt_pattern = (
        broker.RECEPTIONIST_V68_ATTEMPT_PATTERN
        if receptionist_v68_match is not None
        else broker.RECEPTIONIST_V67_ATTEMPT_PATTERN
        if receptionist_v67_match is not None
        else broker.RECEPTIONIST_V66_ATTEMPT_PATTERN
        if receptionist_v66_match is not None
        else broker.RECEPTIONIST_V65_ATTEMPT_PATTERN
        if receptionist_v65_match is not None
        else broker.RECEPTIONIST_V64_ATTEMPT_PATTERN
        if receptionist_v64_match is not None
        else broker.RECEPTIONIST_V63_ATTEMPT_PATTERN
        if receptionist_v63_match is not None
        else broker.RECEPTIONIST_V62_ATTEMPT_PATTERN
        if receptionist_v62_match is not None
        else broker.RECEPTIONIST_V61_ATTEMPT_PATTERN
        if receptionist_v61_match is not None
        else broker.RECEPTIONIST_V6_ATTEMPT_PATTERN
        if receptionist_v6_match is not None
        else broker.PREPRINTED_ATTEMPT_PATTERN
        if preprinted_standard_match is not None
        else broker.PREPRINTED_MULTICASE_ATTEMPT_PATTERN
        if preprinted_multicase_match is not None
        else broker.DIALOGUE_ATTEMPT_PATTERN
        if dialogue_match is not None
        else broker.STRUCTURED_SOURCE_ATTEMPT_PATTERN
        if structured_match is not None
        else broker.SHARED_TYPED_ATTEMPT_PATTERN
    )
    lifecycle_sequence = (
        int(typed_match.group("sequence")) if typed_match is not None else None
    )
    typed_actual_call_ordinal = None
    if lifecycle_sequence is not None:
        typed_actual_call_ordinal = 0
        for ledger_path in evidence_path.parent.glob("*ledger.json"):
            try:
                ledger = lane.load_object(ledger_path)
            except lane.ModelLaneError:
                continue
            ledger_match = typed_attempt_pattern.fullmatch(
                str(ledger.get("attempt_id", ""))
            )
            if (
                ledger_match is not None
                and int(ledger_match.group("sequence")) <= lifecycle_sequence
                and ledger.get("status") == "consumed"
                and ledger.get("provider_calls_consumed") == 1
            ):
                typed_actual_call_ordinal += 1
    is_retry = (
        typed_actual_call_ordinal is not None
        and typed_actual_call_ordinal > 1
    ) or "-occupied-retry-" in evidence["attempt_id"]
    retry_count = (
        typed_actual_call_ordinal - 1
        if typed_actual_call_ordinal is not None
        else int(evidence["attempt_id"].rsplit("-", 1)[-1])
        if is_retry
        else 0
    )
    provider_status = (
        "completed"
        if completed
        else "failed_before_candidate"
        if failed
        else "response_rejected_before_candidate"
        if rejected
        and rejected["fields"].get("reason_code")
        in {
            "schema_invalid",
            "goal_not_allowlisted",
            "provider_candidate_count_invalid",
            "provider_content_invalid",
            "provider_text_missing",
            "provider_text_oversized",
            "provider_text_not_json",
            "provider_candidate_not_object",
            "provider_program_not_object",
            "provider_form_body_not_object",
            "wire_line_invalid",
            "wire_argument_invalid",
            "operator_arity_invalid",
            "required_source_omitted",
            "forward_or_self_reference",
            "output_index_invalid",
            "source_type_mismatch",
            "external_source_code_invalid",
            "binding_sentinel_invalid",
            "prior_output_sentinel_invalid",
            "omit_sentinel_invalid",
            "output_name_invalid",
            "external_binding_invalid",
        }
        else "not_observed"
    )
    bounded_rejection = (
        {
            "reason_code": rejected["fields"].get("reason_code"),
            "field_paths": rejected["fields"].get("field_paths", []),
        }
        if rejected and provider_status == "response_rejected_before_candidate"
        else None
    )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v68_runtime.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode")
            == "receptionist-v68-runtime"
            else "reception.one.receptionist_first_v68.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v68"
            else "reception.one.receptionist_first_v67.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v67"
            else "reception.one.receptionist_first_v66.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v66"
            else "reception.one.receptionist_first_v65.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v65"
            else "reception.one.receptionist_first_v64.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v64"
            else "reception.one.receptionist_first_v63.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v63"
            else "reception.one.receptionist_first_v62.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v62"
            else "reception.one.receptionist_first_v61.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v61"
            else "reception.one.receptionist_first_v6.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "receptionist-v6"
            else "reception.one.preprinted_form_v5.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "preprinted-v5"
            else "reception.one.proofreader_dialogue_v4.turn_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "dialogue-v4"
            else "reception.one.structured_source_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "structured-v3"
            else "reception.one.shared_typed_external_audit.v1"
            if evidence["exchange"].get("contract_mode") == "shared-v2"
            else "reception.one.bureau.model_text_external_audit.v1"
        ),
        "result": evidence["result"],
        "attempt_id": evidence["attempt_id"],
        "ledger_id": evidence["ledger_id"],
        "provider": evidence["exact_binding"]["provider"],
        "model_id": evidence["exact_binding"]["model_id"],
        "project": evidence["exact_binding"]["project"],
        "service_account": evidence["exact_binding"]["service_account"],
        "authentication": evidence["exact_binding"]["authentication"],
        "api_key_authentication_used": False,
        "location": evidence["exact_binding"]["location"],
        "endpoint_hostname": evidence["exact_binding"]["endpoint_hostname"],
        "request_hash": (
            constructed["fields"]["request_hash"] if constructed else None
        ),
        "schema_hash": (
            constructed["fields"]["schema_hash"] if constructed else None
        ),
        "model_input_hash": evidence["exchange"]["model_input_hash"],
        "event_sequence": [
            {
                "sequence": event["sequence"],
                "event_type": event["event_type"],
                "event_hash": event["event_hash"],
                "previous_hash": event["previous_hash"],
            }
            for event in events
        ],
        "durable_hash_chain": {
            "valid": True,
            "event_count": len(events),
            "terminal_hash": events[-1]["event_hash"],
        },
        "provider_outcome": {
            "status": provider_status,
            "http_status": (
                failed["fields"].get("http_status")
                if failed
                else completed["fields"].get("http_status")
                if completed
                else received["fields"].get("http_status")
                if received
                else None
            ),
            "latency_ms": (
                completed["fields"].get("latency_ms")
                if completed
                else received["fields"].get("latency_ms")
                if received
                else None
            ),
            "usage": (
                completed["fields"].get("usage", {})
                if completed
                else received["fields"].get("usage", {})
                if received
                else {}
            ),
            "bounded_completion_metadata": (
                {
                    "candidate_count": received["fields"].get(
                        "candidate_count"
                    ),
                    "candidate_count_truncated": received["fields"].get(
                        "candidate_count_truncated"
                    ),
                    "finish_reasons": received["fields"].get(
                        "finish_reasons", []
                    ),
                    "part_counts": received["fields"].get(
                        "part_counts", []
                    ),
                    "provider_text_retained": False,
                    "provider_text_inspected_for_diagnosis": False,
                }
                if received
                else None
            ),
            "bounded_error": (
                failed["fields"] if failed else bounded_rejection
            ),
        },
        "proofreader": (
            {
                "disposition": proof["fields"]["disposition"],
                "safe_repairs": proof["fields"]["safe_repairs"],
                "wire_safe_repairs": proof["fields"].get(
                    "wire_safe_repairs", []
                ),
                "violations": proof["fields"]["violations"],
                "admitted_operator_ids": proof["fields"][
                    "admitted_operator_ids"
                ],
                **(
                    {
                        "context_frame_review": proof["fields"][
                            "context_frame_review"
                        ]
                    }
                    if "context_frame_review" in proof["fields"]
                    else {}
                ),
            }
            if proof
            else {
                "disposition": "not_reached",
                "safe_repairs": [],
                "wire_safe_repairs": [],
                "violations": [],
                "admitted_operator_ids": [],
            }
        ),
        "operator_note": (
            {
                "disposition": operator_note["fields"].get("disposition"),
                "reason_codes": operator_note["fields"].get(
                    "reason_codes", []
                ),
                "note_sha256": operator_note["fields"].get("note_sha256"),
                "retained_utf8_bytes": operator_note["fields"].get(
                    "retained_utf8_bytes", 0
                ),
                "operator_note": operator_note["fields"].get("operator_note"),
                "audit_only": operator_note["fields"].get(
                    "audit_only", True
                ),
                "parsed_into_plan": operator_note["fields"].get(
                    "parsed_into_plan", False
                ),
                "product_delivered": operator_note["fields"].get(
                    "product_delivered", False
                ),
            }
            if operator_note
            else None
        ),
        "receptionist_output": (
            {
                "disposition": receptionist_output["fields"].get(
                    "disposition"
                ),
                "violations": receptionist_output["fields"].get(
                    "violations", []
                ),
                "receptionist_response": receptionist_output["fields"].get(
                    "receptionist_response"
                ),
                "decision_note": receptionist_output["fields"].get(
                    "decision_note"
                ),
                "evidence_utterance_indices": receptionist_output[
                    "fields"
                ].get("evidence_utterance_indices", []),
                "natural_response_parsed_into_form": False,
                "product_delivered": False,
                "raw_provider_response": False,
                "hidden_reasoning": False
            }
            if receptionist_output
            else None
        ),
        "typed_program": (
            {
                "program_hash": completed["fields"].get("program_hash"),
                (
                    "explicit_source_form"
                    if structured_match is not None
                    or dialogue_match is not None
                    or preprinted_match is not None
                    or receptionist_match is not None
                    else "closed_integer_form"
                ): completed["fields"].get("typed_program"),
                "operator_note_excluded": True,
                "raw_provider_response": False,
            }
            if completed and typed_match is not None
            else None
        ),
        "preprinted_form": (
            {
                "model_form_body_hash": completed["fields"].get(
                    "model_form_body_hash"
                ),
                "model_authored_field_manifest": completed["fields"].get(
                    "model_authored_field_manifest", []
                ),
                "preprinted_field_manifest_hash": completed["fields"].get(
                    "preprinted_field_manifest_hash"
                ),
                "broker_owned_field_manifest": completed["fields"].get(
                    "broker_owned_field_manifest", []
                ),
                "broker_judgement_repair": completed["fields"].get(
                    "broker_judgement_repair"
                ),
                "raw_model_form_body_recorded": False,
            }
            if completed
            and (
                preprinted_match is not None
                or receptionist_match is not None
            )
            else None
        ),
        "correction_ticket": (
            {
                "ticket_hash": correction_ticket["fields"].get(
                    "ticket_hash"
                ),
                "target_turn_code": correction_ticket["fields"].get(
                    "target_turn_code"
                ),
                "attempts_remaining": correction_ticket["fields"].get(
                    "attempts_remaining"
                ),
                "complete_replacement_required": correction_ticket[
                    "fields"
                ].get("complete_replacement_required"),
                "proofreader_selected_replacement": correction_ticket[
                    "fields"
                ].get("proofreader_selected_replacement"),
                "ticket": correction_ticket["fields"].get("ticket"),
            }
            if correction_ticket
            else None
        ),
        "release": release["fields"] if release else None,
        "retry": {
            "count": retry_count,
            "authorised": is_retry,
            "performed": is_retry,
            **(
                {
                    "lifecycle_sequence": lifecycle_sequence,
                    "actual_provider_call_ordinal": (
                        typed_actual_call_ordinal
                    ),
                }
                if typed_match is not None
                else {}
            ),
            "reason": (
                "sequence_stopped_after_first_admitted_result"
                if release
                and (
                    dialogue_match is not None
                    or preprinted_match is not None
                    or receptionist_match is not None
                )
                else "one_closed_correction_turn_authorised"
                if correction_ticket is not None
                else "terminal_second_turn_no_release"
                if (
                    dialogue_match is not None
                    or preprinted_match is not None
                    or receptionist_match is not None
                )
                and lifecycle_sequence == 2
                and release is None
                else
                "sequence_stopped_after_first_admitted_result"
                if release and structured_match is not None
                else "semantic_failure_not_retryable"
                if (
                    structured_match is not None
                    and proof is not None
                    and release is None
                )
                else "actual_call_ceiling_exhausted_no_release"
                if (
                    typed_actual_call_ordinal is not None
                    and typed_actual_call_ordinal >= 2
                )
                else "continuing_same_lane_authority_subject_to_all_gates"
                if is_retry
                else "primary_call_consumed_request_contract_review_required"
                if structured_match is not None
                else "single_call_ceiling_consumed"
            ),
        },
        "freshness": (
            proof["fields"].get("freshness") if proof else "not_evaluated_without_candidate"
        ),
        "supersession": (
            proof["fields"].get("supersession")
            if proof
            else "not_evaluated_without_candidate"
        ),
        "cleanup": evidence["cleanup"],
        "vertex_audit_control_posture": {
            "vertex_data_read_audit_enabled": preflight["checks"][
                "vertex_data_read_audit_enabled"
            ],
            "vertex_data_write_audit_enabled": preflight["checks"][
                "vertex_data_write_audit_enabled"
            ],
            "request_response_logging_disabled_or_absent": preflight["checks"][
                "request_response_logging_disabled_or_absent"
            ],
            "provider_in_memory_cache_disabled": preflight["checks"][
                "provider_in_memory_cache_disabled"
            ],
            "no_user_managed_service_account_key": preflight["checks"][
                "no_user_managed_service_account_key"
            ],
        },
        "explicit_exclusions": evidence["explicit_exclusions"],
        "candid_limit": (
            "The call proves the configured Sydney regional request path, "
            "one-use isolation lifecycle and admitted typed release; it does "
            "not prove Australian physical or sovereign processing, product "
            "suitability or safety for real data."
            if release
            else "The first call proves only the configured Sydney regional "
            "request path and a schema-admitted typed form that the "
            "proofreader rejected. One closed correction ticket was issued; "
            "nothing was released, and no claim of successful correction, "
            "general reliability, Australian physical or sovereign "
            "processing, product suitability or real-data safety is made."
            if correction_ticket
            else "The call proves the configured Sydney regional request path "
            "and fail-closed one-use isolation lifecycle. A schema-admitted "
            "typed program reached the proofreader but was rejected, so "
            "nothing was released. It proves no reliable model "
            "interpretation, Australian physical or sovereign processing, "
            "product suitability or safety for real data."
            if proof
            else "The call proves the configured Sydney regional request path "
            "and fail-closed one-use isolation lifecycle, but no generated "
            "candidate reached the proofreader. It proves no model "
            "interpretation, Australian physical or sovereign processing, "
            "product suitability or safety for real data."
        ),
    }


def build_diagnostic(
    external_audit: dict[str, Any],
) -> dict[str, Any]:
    error = external_audit["provider_outcome"]["bounded_error"] or {}
    message = error.get("sanitized_message", "")
    diagnosis_supported = (
        error.get("http_status") == 400
        and error.get("normalized_status") == "INVALID_ARGUMENT"
        and "too many states for serving" in message
    )
    wire_contract_mismatch = (
        external_audit["provider_outcome"]["status"]
        == "response_rejected_before_candidate"
        and error.get("reason_code") == "schema_invalid"
    )
    field_paths = error.get("field_paths", [])
    step_reference_mismatch = (
        wire_contract_mismatch
        and isinstance(field_paths, list)
        and bool(field_paths)
        and all(
            isinstance(path, str)
            and path.startswith("$.steps[")
            and path.endswith("].source")
            for path in field_paths
        )
    )
    repaired_schema = lane.vertex_response_schema()
    rendered = lane.canonical_json(repaired_schema)
    return {
        "schema_version": (
            "reception.one.bureau.model_text_provider_blocked_diagnostic.v1"
        ),
        "result": (
            "reception_one_bureau_model_text_schema_state_diagnostic_pass"
            if diagnosis_supported
            else "reception_one_bureau_model_text_step_reference_grammar_diagnostic_pass"
            if step_reference_mismatch
            else "reception_one_bureau_model_text_wire_normalization_diagnostic_pass"
            if wire_contract_mismatch
            else "reception_one_bureau_model_text_schema_state_diagnostic_revision_required"
        ),
        "historical_attempt_id": external_audit["attempt_id"],
        "historical_request_hash": external_audit["request_hash"],
        "historical_schema_hash": external_audit["schema_hash"],
        "bounded_provider_error": error,
        "diagnosis": (
            "The provider explicitly rejected the former deeply nested "
            "structured-output schema because its constraint generated too many "
            "serving states."
            if diagnosis_supported
            else (
                "The exact Sydney response passed the goal and compact-line "
                "framing but failed the closed candidate schema only at prior-"
                "step argument source paths. The discarded source values were "
                "not retained. The safe repair adds one canonical three-segment "
                "step-reference example and explicitly forbids omitted prefixes "
                "and dot notation; it does not transform or guess a reference."
            )
            if step_reference_mismatch
            else (
                "The provider returned a response through the exact lane, but "
                "the low-state provider schema allowed a string representation "
                "which the stricter local wire schema rejected before the "
                "proofreader. The exact discarded field value was not retained. "
                "The safe repair therefore only strengthens the exact-goal "
                "instruction and applies allowlisted enum-casing and separator-"
                "whitespace normalization before the unchanged strict schema."
            )
            if wire_contract_mismatch
            else "The bounded error does not support a deterministic diagnosis."
        ),
        "repository_local_repair": {
            "wire_contract": (
                "goal plus an array of compact typed plan-line strings"
            ),
            "new_schema_hash": lane.canonical_hash(repaired_schema),
            "array_schema_count": rendered.count('"type":"ARRAY"'),
            "enum_keyword_count": rendered.count('"enum"'),
            "nested_object_items": False,
            "local_wire_schema": (
                "orchestration/continuity/reception-one-bureau-model-text-lane/"
                "provider-wire-response.schema.json"
            ),
            "decoded_candidate_schema_unchanged": True,
            "deterministic_proofreader_unchanged": True,
            "provider_model_project_identity_region_unchanged": True,
            "mechanical_wire_normalization_only": wire_contract_mismatch,
            "step_reference_instruction_only": step_reference_mismatch,
            "source_reference_transformation_permitted": False,
            "semantic_reinterpretation_permitted": False,
        },
        "boundary": {
            "provider_calls_performed": 0,
            "credential_reads_performed": 0,
            "network_access_performed": False,
            "external_state_changed": False,
            "retry_authorised": wire_contract_mismatch,
            "retry_performed": False,
        },
    }


def build_iterative_sequence_analysis(
    external_audit_paths: list[Path],
    residue_path: Path,
) -> dict[str, Any]:
    audits = [lane.load_object(path) for path in external_audit_paths]
    residue = lane.load_object(residue_path)
    if len(audits) != 3:
        raise ValueError("iterative_audit_count_invalid")
    expected_attempts = [
        f"reception-one-model-text-occupied-retry-{index:03d}"
        for index in range(1, 4)
    ]
    expected_ledgers = [
        f"reception-one-model-text-ledger-retry-{index:03d}"
        for index in range(1, 4)
    ]
    if [item["attempt_id"] for item in audits] != expected_attempts:
        raise ValueError("iterative_attempt_sequence_invalid")
    if [item["ledger_id"] for item in audits] != expected_ledgers:
        raise ValueError("iterative_ledger_sequence_invalid")
    binding_fields = (
        "provider",
        "model_id",
        "project",
        "service_account",
        "authentication",
        "location",
        "endpoint_hostname",
    )
    binding = {field: audits[0][field] for field in binding_fields}
    if any(
        any(item[field] != binding[field] for field in binding_fields)
        for item in audits[1:]
    ):
        raise ValueError("iterative_binding_changed")
    if any(
        not item["durable_hash_chain"]["valid"]
        or not all(
            value
            for key, value in item["cleanup"].items()
            if key != "daemon_wide_prune_performed"
        )
        for item in audits
    ):
        raise ValueError("iterative_audit_or_cleanup_invalid")
    if any(item["release"] is not None for item in audits[:2]):
        raise ValueError("failed_attempt_release_present")
    success = audits[2]
    if (
        success["result"]
        != "reception_one_bureau_model_text_lane_occupied_pass"
        or success["proofreader"]["disposition"] != "admit"
        or success["release"] is None
        or success["release"]["write_performed"] is not False
        or success["release"]["human_gate"] is not True
        or residue.get("provider_calls_after_first_admitted_result") != 0
    ):
        raise ValueError("terminal_success_invalid")
    conservative_cost_upper_bound = round(
        len(audits)
        * (
            broker.MAX_PROVIDER_REQUEST_BYTES * 0.15 / 1_000_000
            + 1024 * 0.60 / 1_000_000
        ),
        8,
    )
    if conservative_cost_upper_bound >= 1:
        raise ValueError("cost_ceiling_not_preserved")
    return {
        "schema_version": (
            "reception.one.bureau.model_text_iterative_audit_analysis.v1"
        ),
        "result": "reception_one_bureau_model_text_iterative_retry_pass",
        "attempt_ids": expected_attempts,
        "ledger_ids": expected_ledgers,
        "provider_call_count": 3,
        "failed_closed_before_terminal_success": 2,
        "calls_after_first_admitted_result": 0,
        "exact_binding": binding,
        "terminal_proofreader": success["proofreader"],
        "terminal_release": success["release"],
        "cleanup_and_hash_chains_passed": True,
        "cost_guard": {
            "application_ceiling_usd": 1,
            "invoice_cost_observed": False,
            "conservative_upper_bound_usd": conservative_cost_upper_bound,
            "assumption": (
                "three calls, each charged as at most 65536 input tokens and "
                "1024 no-thinking output tokens"
            ),
            "official_pricing_basis": {
                "input_usd_per_million_tokens": 0.15,
                "output_no_thinking_usd_per_million_tokens": 0.60,
                "source": (
                    "https://cloud.google.com/vertex-ai/generative-ai/pricing"
                ),
            },
        },
        "explicit_exclusions": {
            "raw_prompt_or_response_retained": False,
            "credentials_or_tokens_retained": False,
            "chain_of_thought_retained": False,
            "product_or_database_access": False,
            "command_or_write_authority": False,
            "provider_or_regional_fallback": False,
        },
        "candid_limit": (
            "This proves the configured and observed Sydney locational request "
            "path, bounded model composition, deterministic proofreader "
            "admission and in-memory proposal release for one authored-synthetic "
            "case. It does not prove Australian physical or sovereign "
            "processing, product-data safety, production fitness or authority "
            "for any product or clinical write."
        ),
    }


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--audit-log", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--external-audit", type=Path, required=True)
    parser.add_argument("--diagnostic", type=Path)
    args = parser.parse_args()
    try:
        external = build_external_audit(
            args.evidence, args.audit_log, args.preflight
        )
        diagnostic = build_diagnostic(external) if args.diagnostic else None
    except (OSError, ValueError, json.JSONDecodeError, live.LiveError) as error:
        print(
            json.dumps(
                {
                    "status": "revision_required",
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    _write(args.external_audit, external)
    if args.diagnostic and diagnostic is not None:
        _write(args.diagnostic, diagnostic)
    print(
        json.dumps(
            {
                "external_audit_result": external["result"],
                "diagnostic_result": (
                    diagnostic["result"] if diagnostic is not None else None
                ),
            },
            sort_keys=True,
        )
    )
    if diagnostic is None:
        return 0
    return 0 if diagnostic["result"].endswith("_pass") else 2


if __name__ == "__main__":
    raise SystemExit(main())
