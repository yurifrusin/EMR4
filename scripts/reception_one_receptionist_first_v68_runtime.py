#!/usr/bin/env python3
"""Wall-clock-bound runtime wrapper around the frozen v6.8 contract."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator

from scripts import reception_one_receptionist_first_v68 as v68


ARTIFACT_DIR = v68.ARTIFACT_DIR
DESK_CONTEXT_SCHEMA_PATH = v68.DESK_CONTEXT_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = v68.TURN_INPUT_SCHEMA_PATH
MODEL_FORM_BODY_SCHEMA_PATH = v68.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v68.CORRECTION_TICKET_SCHEMA_PATH
# The occupied runtime reuses the frozen v6.8 packet and response schemas
# exactly. Its distinct admission boundary is the policy/contract mode plus
# the wall-clock-bound proofreader, not a silently divergent form.
DIALOGUE_PROTOCOL = v68.DIALOGUE_PROTOCOL
PROTOCOL_VERSION = v68.PROTOCOL_VERSION
CONTRACT_MODE = "receptionist-v68-runtime"
POLICY_ID = "reception-one-receptionist-first-v68-runtime-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = v68.MODEL_RESPONSE_CONTRACT
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v68_runtime.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v68_runtime.parent_audit_event.v1"
)
PARENT_RESULT_PASS = (
    "reception_one_receptionist_first_v68_runtime_occupied_pass"
)
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v68_runtime_occupied_no_release"
)
MAX_PROVIDER_CALLS = v68.MAX_PROVIDER_CALLS
MAX_CORRECTION_TURNS = v68.MAX_CORRECTION_TURNS
TEMPERATURE = v68.TEMPERATURE
THINKING_BUDGET = v68.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v68.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v68.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v68.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v68.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v68.TYPED_FORM_FIELDS
CORRECTION_ELIGIBLE_CODES = v68.CORRECTION_ELIGIBLE_CODES
BASELINE_METADATA = {
    **v68.BASELINE_METADATA,
    "runtime_wall_clock_proofreader": True,
    "frozen_v68_prompt_or_schema_changed": False,
    "frozen_v68_packet_contract_reused": True,
}
SYSTEM_INSTRUCTION = v68.SYSTEM_INSTRUCTION

ReceptionistFirstError = v68.ReceptionistFirstError
canonical_json = v68.canonical_json
canonical_hash = v68.canonical_hash
validate_exact = v68.validate_exact
assemble_program = v68.assemble_program
model_form_body = v68.model_form_body
vertex_response_schema = v68.vertex_response_schema
review_receptionist_output = v68.review_receptionist_output
parse_vertex_output = v68.parse_vertex_output
parse_vertex_program = v68.parse_vertex_program
evaluate_program = v68.evaluate_program
build_correction_ticket = v68.build_correction_ticket
build_desk_context = v68.build_desk_context
build_model_task = v68.build_model_task


@contextmanager
def _configured_v68() -> Iterator[None]:
    overrides = {
        "DIALOGUE_PROTOCOL": DIALOGUE_PROTOCOL,
        "PROTOCOL_VERSION": PROTOCOL_VERSION,
        "CONTRACT_MODE": CONTRACT_MODE,
        "POLICY_ID": POLICY_ID,
        "PARENT_EVIDENCE_SCHEMA_VERSION": PARENT_EVIDENCE_SCHEMA_VERSION,
        "PARENT_AUDIT_EVENT_SCHEMA_VERSION": (
            PARENT_AUDIT_EVENT_SCHEMA_VERSION
        ),
        "PARENT_RESULT_PASS": PARENT_RESULT_PASS,
        "PARENT_RESULT_NO_RELEASE": PARENT_RESULT_NO_RELEASE,
        "BASELINE_METADATA": BASELINE_METADATA,
    }
    previous = {name: getattr(v68, name) for name in overrides}
    for name, value in overrides.items():
        setattr(v68, name, value)
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(v68, name, value)


def build_turn_input(
    frame: dict[str, Any],
    *,
    correction_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with _configured_v68():
        return v68.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )


def validate_turn_input(frame: dict[str, Any], value: dict[str, Any]) -> None:
    with _configured_v68():
        v68.validate_turn_input(frame, value)


def build_vertex_request(turn_input: dict[str, Any]) -> dict[str, Any]:
    with _configured_v68():
        return v68.build_vertex_request(turn_input)


def evaluate_output(
    frame: dict[str, Any],
    program: dict[str, Any],
    body: dict[str, Any],
    *,
    turn_code: int,
    turn_input: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    if now.tzinfo is None:
        raise ReceptionistFirstError("proofreader_now_timezone_required")
    with _configured_v68():
        return v68.evaluate_output(
            frame,
            program,
            body,
            turn_code=turn_code,
            turn_input=turn_input,
            now=now,
        )


__all__ = [
    "ARTIFACT_DIR",
    "BASELINE_METADATA",
    "CONTRACT_MODE",
    "CORRECTION_ELIGIBLE_CODES",
    "CORRECTION_TICKET_SCHEMA_PATH",
    "DESK_CONTEXT_SCHEMA_PATH",
    "DIALOGUE_PROTOCOL",
    "INCLUDE_THOUGHTS",
    "MAX_CORRECTION_TURNS",
    "MAX_OUTPUT_TOKENS",
    "MAX_PROVIDER_CALLS",
    "MODEL_AUTHORED_FIELDS",
    "MODEL_FORM_BODY_SCHEMA_PATH",
    "MODEL_RESPONSE_CONTRACT",
    "PARENT_AUDIT_EVENT_SCHEMA_VERSION",
    "PARENT_EVIDENCE_SCHEMA_VERSION",
    "PARENT_RESULT_NO_RELEASE",
    "PARENT_RESULT_PASS",
    "POLICY_ID",
    "PREPRINTED_FIELDS",
    "PROTOCOL_VERSION",
    "SYSTEM_INSTRUCTION",
    "TEMPERATURE",
    "THINKING_BUDGET",
    "TURN_INPUT_SCHEMA_PATH",
    "TYPED_FORM_FIELDS",
    "ReceptionistFirstError",
    "assemble_program",
    "build_correction_ticket",
    "build_desk_context",
    "build_model_task",
    "build_turn_input",
    "build_vertex_request",
    "canonical_hash",
    "canonical_json",
    "evaluate_output",
    "evaluate_program",
    "model_form_body",
    "parse_vertex_output",
    "parse_vertex_program",
    "review_receptionist_output",
    "validate_exact",
    "validate_turn_input",
    "vertex_response_schema",
]
