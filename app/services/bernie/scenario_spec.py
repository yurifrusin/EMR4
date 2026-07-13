"""Canonical, provider-free scenario contract for Bernie language coverage."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


TemporalRelation = Literal[
    "exact",
    "not_before",
    "not_after",
    "interval",
    "approximate",
    "unspecified",
]
EntitySemantics = Literal[
    "exact",
    "ambiguous",
    "omitted",
    "negated",
    "provisional",
    "corrected",
    "mismatched",
]


class ScenarioSourceSpan(BaseModel):
    """Exact evidence coordinates in one original dialogue turn."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    turn_index: int = Field(ge=0)
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_order(self) -> "ScenarioSourceSpan":
        if self.end <= self.start:
            raise ValueError("source span end must be greater than start")
        return self


class ReceptionScenarioSpec(BaseModel):
    """Versioned semantic oracle for one synthetic receptionist scenario.

    The model contains evidence and expected deterministic behaviour only. It
    grants neither provider authority nor diary write authority.
    """

    model_config = ConfigDict(extra="forbid")

    spec_version: Literal["lc1.v1"] = "lc1.v1"
    scenario_id: str = Field(min_length=1)
    provenance: Literal["gold", "silver", "bronze"]
    adjudication: Literal["adjudicated", "pending", "quarantine"]
    family: str = Field(min_length=1)
    description: str = Field(min_length=1)

    dialogue_turns: list[dict[str, Any]] = Field(min_length=1)
    reference_date: date
    clinic_clock: datetime

    intended_action: Literal[
        "create", "move", "resize", "cancel", "status_change", "explain_schedule"
    ]
    action_semantics: Literal["intended", "ambiguous", "prohibited"]
    temporal_relation: TemporalRelation
    earliest_time: str | None = None
    latest_time: str | None = None
    normalized_values: dict[str, Any]
    source_spans: dict[str, list[ScenarioSourceSpan]]
    duration_minutes: int | None = Field(default=None, gt=0)

    practitioner_semantics: EntitySemantics
    patient_semantics: EntitySemantics
    location_semantics: EntitySemantics
    appointment_type_semantics: EntitySemantics
    duration_semantics: EntitySemantics

    diary_state: Literal[
        "empty",
        "exact_duplicate",
        "overlap",
        "same_day_distinct",
        "terminal",
        "stale",
        "concurrent",
        "roster_absent",
        "break",
        "no_slots",
        "elapsed_window",
    ]
    entity_state: Literal[
        "exact", "omitted", "ambiguous", "corrected", "negated", "mismatched"
    ]
    dialogue_form: Literal[
        "one_shot",
        "clarification",
        "correction",
        "reversal",
        "ellipsis",
        "anaphora",
        "repeated",
        "session_restart",
    ]
    language_form: Literal[
        "plain",
        "paraphrase",
        "filler",
        "abbreviation",
        "typo",
        "speech_like",
        "punctuation_variant",
        "adversarial",
    ]

    initial_diary_state: dict[str, Any]
    expected_outcome_kind: str = Field(min_length=1)
    expected_tool_sequence: list[str]
    expected_appointment_deltas: list[dict[str, Any]]
    expected_audit_deltas: list[dict[str, Any]]
    forbidden_outcomes: list[str]
    forbidden_tool_calls: list[str]
    expected_clarification: str | None = None
    clarification_choices: list[str] = Field(default_factory=list)

    @field_validator("clinic_clock")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clinic_clock must include a clinic-local UTC offset")
        return value

    @field_validator("earliest_time", "latest_time")
    @classmethod
    def validate_hhmm(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            parsed = time.fromisoformat(value)
        except ValueError as error:
            raise ValueError("time values must use valid HH:MM form") from error
        canonical = parsed.strftime("%H:%M")
        if value != canonical:
            raise ValueError("time values must use canonical HH:MM form")
        return value

    @model_validator(mode="after")
    def validate_temporal_relation(self) -> "ReceptionScenarioSpec":
        if self.clinic_clock.date() != self.reference_date:
            raise ValueError("clinic_clock date must equal reference_date")
        if self.temporal_relation == "exact":
            if self.earliest_time is None or self.latest_time != self.earliest_time:
                raise ValueError("exact requires equal, populated earliest/latest times")
        elif self.temporal_relation == "not_before" and self.earliest_time is None:
            raise ValueError("not_before requires earliest_time")
        elif self.temporal_relation == "not_after" and self.latest_time is None:
            raise ValueError("not_after requires latest_time")
        elif self.temporal_relation == "interval":
            if (
                self.earliest_time is None
                or self.latest_time is None
                or self.earliest_time >= self.latest_time
            ):
                raise ValueError("interval requires increasing earliest/latest times")
        utterances = [
            turn.get("utterance")
            for turn in self.dialogue_turns
            if isinstance(turn.get("utterance"), str)
        ]
        for field_name, spans in self.source_spans.items():
            if not spans:
                raise ValueError(f"source_spans[{field_name!r}] cannot be empty")
            for span in spans:
                if span.turn_index >= len(utterances):
                    raise ValueError(
                        f"source_spans[{field_name!r}] references a missing turn"
                    )
                original = utterances[span.turn_index]
                if span.end > len(original) or original[span.start:span.end] != span.text:
                    raise ValueError(
                        f"source_spans[{field_name!r}] does not match original text"
                    )
        return self


__all__ = [
    "EntitySemantics",
    "ReceptionScenarioSpec",
    "ScenarioSourceSpan",
    "TemporalRelation",
]
