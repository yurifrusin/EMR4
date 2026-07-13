"""ReceptionScenarioSpec contract — canonical scenario specification for Bernie.

This module defines the Pydantic model that serves as the single source of truth
for a receptionist-domain scenario.  Every test, coverage report, and evaluation
fixture should be expressible as a ``ReceptionScenarioSpec``.  The spec is a
pure-data contract: it does not import routers, providers, database models, or
live-interpreter code.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ReceptionScenarioSpec(BaseModel):
    """Canonical scenario specification for the LC1 semantic coverage lattice.

    Each spec describes one scenario that the Bernie reception-agent should be
    able to interpret correctly.  Fields capture the original dialogue, the
    expected temporal/practitioner/patient semantics, the expected tool
    sequence, and the outcomes that must or must not occur.
    """

    spec_version: str = Field(
        default="lc1.v1",
        description="Version marker for the spec schema.",
        pattern=r"^lc1\.v1$",
    )
    scenario_id: str = Field(
        description="Unique ID referencing the source T1/T2 scenario.",
    )
    provenance: str = Field(
        description="Evidence tier: gold, silver, or bronze.",
        pattern=r"^(gold|silver|bronze)$",
    )
    adjudication: str = Field(
        description="Review state: adjudicated, pending, or quarantine.",
        pattern=r"^(adjudicated|pending|quarantine)$",
    )
    family: str = Field(
        description="Scenario family label (e.g. 'booking_create', 'clarify_temporal').",
    )
    description: str = Field(
        description="Human-readable scenario description.",
    )
    dialogue_turns: List[Dict] = Field(
        description="Original receptionist utterances, one dict per turn.",
    )
    reference_date: date = Field(
        description="Deterministic clinic-local clock date for the scenario.",
    )
    intended_action: str = Field(
        description=(
            "Diary action verb: create, move, resize, cancel, status_change, "
            "or explain_schedule."
        ),
    )
    temporal_relation: str = Field(
        description=(
            "Temporal operator semantics: exact, not_before, not_after, "
            "interval, approximate, or unspecified."
        ),
        pattern=r"^(exact|not_before|not_after|interval|approximate|unspecified)$",
    )
    earliest_time: Optional[str] = Field(
        default=None,
        description="HH:MM normalized earliest time constraint.",
        pattern=r"^\d{2}:\d{2}$",
    )
    latest_time: Optional[str] = Field(
        default=None,
        description="HH:MM normalized latest time constraint.",
        pattern=r"^\d{2}:\d{2}$",
    )
    source_spans: Dict[str, str] = Field(
        description="Field -> original utterance substring evidence.",
    )
    duration_minutes: Optional[int] = Field(
        default=None,
        description="Appointment duration in minutes (may be absent).",
    )
    practitioner_semantics: str = Field(
        description="How practitioner is referenced: exact, ambiguous, omitted, or negated.",
        pattern=r"^(exact|ambiguous|omitted|negated)$",
    )
    patient_semantics: str = Field(
        description=(
            "How patient is referenced: exact, ambiguous, omitted, negated, "
            "or provisional."
        ),
        pattern=r"^(exact|ambiguous|omitted|negated|provisional)$",
    )
    initial_diary_state: Dict = Field(
        description="Synthetic diary state before interpretation.",
    )
    expected_outcome_kind: str = Field(
        description=(
            "The expected outcome kind, e.g. interpreted_ready, "
            "existing_booking_found, clarification_required."
        ),
    )
    expected_tool_sequence: List[str] = Field(
        description="Ordered list of tool calls expected during interpretation.",
    )
    expected_appointment_deltas: List[Dict] = Field(
        description="Appointment rows expected to change.",
    )
    forbidden_outcomes: List[str] = Field(
        description="Outcomes that must not occur (e.g. 'appointment_created').",
    )
    forbidden_tool_calls: List[str] = Field(
        description="Tool calls that must not occur.",
    )
    expected_clarification: Optional[str] = Field(
        default=None,
        description="Expected clarification question, if any.",
    )
    clarification_choices: List[str] = Field(
        default=[],
        description="Acceptable clarification responses.",
    )
