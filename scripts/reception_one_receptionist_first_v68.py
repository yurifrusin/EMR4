#!/usr/bin/env python3
"""Exact move-response-pattern descendant of receptionist-first v6.7."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sys
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_receptionist_first_v67 as v67


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v68"
)
DESK_CONTEXT_SCHEMA_PATH = v67.DESK_CONTEXT_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
MODEL_FORM_BODY_SCHEMA_PATH = v67.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v67.CORRECTION_TICKET_SCHEMA_PATH
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.8"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.8"
CONTRACT_MODE = "receptionist-v68"
POLICY_ID = "reception-one-receptionist-first-v68-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.8"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v68.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v68.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v68_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v68_occupied_no_release"
)
MAX_PROVIDER_CALLS = v67.MAX_PROVIDER_CALLS
MAX_CORRECTION_TURNS = v67.MAX_CORRECTION_TURNS
TEMPERATURE = v67.TEMPERATURE
THINKING_BUDGET = v67.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v67.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v67.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v67.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v67.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v67.TYPED_FORM_FIELDS
RECOGNIZED_CONSTRAINT_CODE = v67.RECOGNIZED_CONSTRAINT_CODE
RECOGNIZED_CONSTRAINT_PATH_CODE = v67.RECOGNIZED_CONSTRAINT_PATH_CODE
CORRECTION_ELIGIBLE_CODES = v67.CORRECTION_ELIGIBLE_CODES
EXACT_MOVE_RESPONSE = (
    "I can prepare a move proposal for the requested appointment and time "
    "for staff review. No booking was changed."
)
BASELINE_METADATA = {
    **v67.BASELINE_METADATA,
    "exact_move_response_pattern_taught": True,
    "proofreader_move_markers_changed": False,
}
SYSTEM_INSTRUCTION = (
    v67.SYSTEM_INSTRUCTION
    + f"""

For a move goal, receptionist_response must be exactly:
"{EXACT_MOVE_RESPONSE}"

If a correction ticket reports receptionist_response_goal_mismatch and the
required goal is move, replace the complete receptionist_response with that
exact sentence. Do not preserve or paraphrase the rejected response."""
)

ReceptionistFirstError = v67.ReceptionistFirstError
canonical_json = v67.canonical_json
canonical_hash = v67.canonical_hash
validate_exact = v67.validate_exact
assemble_program = v67.assemble_program
model_form_body = v67.model_form_body
vertex_response_schema = v67.vertex_response_schema
review_receptionist_output = v67.review_receptionist_output
parse_vertex_output = v67.parse_vertex_output
parse_vertex_program = v67.parse_vertex_program
evaluate_program = v67.evaluate_program
build_correction_ticket = v67.build_correction_ticket
build_desk_context = v67.build_desk_context
build_model_task = v67.build_model_task


@contextmanager
def _configured_v67() -> Iterator[None]:
    overrides = {
        "ARTIFACT_DIR": ARTIFACT_DIR,
        "TURN_INPUT_SCHEMA_PATH": TURN_INPUT_SCHEMA_PATH,
        "DIALOGUE_PROTOCOL": DIALOGUE_PROTOCOL,
        "PROTOCOL_VERSION": PROTOCOL_VERSION,
        "CONTRACT_MODE": CONTRACT_MODE,
        "POLICY_ID": POLICY_ID,
        "MODEL_RESPONSE_CONTRACT": MODEL_RESPONSE_CONTRACT,
        "PARENT_EVIDENCE_SCHEMA_VERSION": PARENT_EVIDENCE_SCHEMA_VERSION,
        "PARENT_AUDIT_EVENT_SCHEMA_VERSION": PARENT_AUDIT_EVENT_SCHEMA_VERSION,
        "PARENT_RESULT_PASS": PARENT_RESULT_PASS,
        "PARENT_RESULT_NO_RELEASE": PARENT_RESULT_NO_RELEASE,
        "BASELINE_METADATA": BASELINE_METADATA,
        "SYSTEM_INSTRUCTION": SYSTEM_INSTRUCTION,
    }
    previous = {name: getattr(v67, name) for name in overrides}
    for name, value in overrides.items():
        setattr(v67, name, value)
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(v67, name, value)


def build_turn_input(
    frame: dict[str, Any],
    *,
    correction_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with _configured_v67():
        return v67.build_turn_input(
            frame,
            correction_ticket=correction_ticket,
        )


def validate_turn_input(frame: dict[str, Any], value: dict[str, Any]) -> None:
    with _configured_v67():
        v67.validate_turn_input(frame, value)


def build_vertex_request(turn_input: dict[str, Any]) -> dict[str, Any]:
    with _configured_v67():
        return v67.build_vertex_request(turn_input)


def evaluate_output(
    frame: dict[str, Any],
    program: dict[str, Any],
    body: dict[str, Any],
    *,
    turn_code: int,
    turn_input: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    captured_at = turn_input["task"]["desk_context"]["freshness"][
        "observed_at"
    ]
    if captured_at != frame.get("observed_at"):
        raise ReceptionistFirstError("proofreader_observed_at_mismatch")
    try:
        captured_datetime = datetime.fromisoformat(
            captured_at.replace("Z", "+00:00")
        )
    except (AttributeError, ValueError) as error:
        raise ReceptionistFirstError(
            "proofreader_observed_at_invalid"
        ) from error
    proofreader_now = now or captured_datetime
    if proofreader_now.tzinfo is None:
        raise ReceptionistFirstError("proofreader_now_timezone_required")
    with _configured_v67():
        return v67.evaluate_output(
            frame,
            program,
            body,
            turn_code=turn_code,
            turn_input=turn_input,
            now=proofreader_now,
        )


def build_provider_blocked_evidence() -> dict[str, Any]:
    with _configured_v67():
        evidence = v67.build_provider_blocked_evidence()
    return {
        **evidence,
        "schema_version": (
            "reception.one.receptionist_first_v68.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v68_provider_blocked_pass"
        ),
        "repair": {
            **evidence["repair"],
            "exact_move_response_pattern_taught": True,
            "proofreader_move_markers_changed": False,
        },
    }


__all__ = [
    "ARTIFACT_DIR",
    "BASELINE_METADATA",
    "CONTRACT_MODE",
    "CORRECTION_ELIGIBLE_CODES",
    "CORRECTION_TICKET_SCHEMA_PATH",
    "DESK_CONTEXT_SCHEMA_PATH",
    "DIALOGUE_PROTOCOL",
    "EXACT_MOVE_RESPONSE",
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
    "RECOGNIZED_CONSTRAINT_CODE",
    "RECOGNIZED_CONSTRAINT_PATH_CODE",
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
    "build_provider_blocked_evidence",
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
