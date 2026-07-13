"""Deterministic in-memory multi-step receptionist workflow-chain harness.

This module chains single-utterance interpretation steps (from the provider-free
Bernie interpretation harness) into multi-step workflows with accumulated
in-memory context.  It is test-only; no route dispatch, provider call, database
access, or write authority is permitted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.services.bernie.interpretation_harness import (
    InterpretationDispatch,
    InterpretationResult,
    assert_interpretation_frame_consistency,
    assert_interpretation_result_consistency,
    interpret_receptionist_utterance,
    interpretation_result_to_frame,
)
from app.services.diary.action_route_contract import RouteAuthority

WORKFLOW_CHAIN_HARNESS_SCHEMA_VERSION = "bernie.workflow_chain_harness.v1"
WF_CHAIN_REPORT_SCHEMA_VERSION = "bernie.workflow_chain_report.v1"

_FORBIDDEN_REPORT_FRAGMENTS: tuple[str, ...] = (
    "patient_id",
    "practitioner_id",
    "appointment_id",
    "slot_id",
    "payload",
    "/api/",
    "local_data",
    "h15",
    "h_series",
)


class Resolution(str, Enum):
    """End-to-end resolution classification for a workflow chain step or chain."""

    resolved = "resolved"
    clarification_needed = "clarification_needed"
    refused_planned = "refused_planned"
    refused_unsafe = "refused_unsafe"
    refused_unknown = "refused_unknown"


_RESOLUTION_ORDER: dict[Resolution, int] = {
    Resolution.resolved: 0,
    Resolution.refused_unknown: 1,
    Resolution.clarification_needed: 2,
    Resolution.refused_planned: 3,
    Resolution.refused_unsafe: 4,
}


@dataclass(frozen=True)
class WorkflowStep:
    """One authored synthetic utterance step in a workflow chain fixture."""

    utterance: str
    step_label: str
    expected_verb: str | None = None
    expected_dispatch: str | None = None
    expected_frame_kind: str | None = None
    expected_resolution: str | None = None


@dataclass(frozen=True)
class WorkflowChain:
    """One authored synthetic multi-step receptionist workflow sequence."""

    chain_id: str
    label: str
    steps: tuple[WorkflowStep, ...]


@dataclass
class WorkflowContext:
    """In-memory context accumulated across a multi-step workflow chain.

    This is deliberately ephemeral and non-persistent: no database writes,
    memory/RAG/GraphRAG updates, or provider calls are involved.
    """

    resolved_patient_descriptor: str | None = None
    resolved_practitioner_descriptor: str | None = None
    time_window_descriptor: str | None = None
    accumulated_action_verbs: tuple[str, ...] = ()
    preceding_frame_kind: str | None = None
    chain_refusal_state: Resolution | None = None

    def copy(self) -> WorkflowContext:
        return WorkflowContext(
            resolved_patient_descriptor=self.resolved_patient_descriptor,
            resolved_practitioner_descriptor=self.resolved_practitioner_descriptor,
            time_window_descriptor=self.time_window_descriptor,
            accumulated_action_verbs=self.accumulated_action_verbs,
            preceding_frame_kind=self.preceding_frame_kind,
            chain_refusal_state=self.chain_refusal_state,
        )


@dataclass(frozen=True)
class WorkflowStepResult:
    """Result of one interpreted step in a workflow chain."""

    step_label: str
    interpretation_result: InterpretationResult | None
    projected_frame: dict[str, Any] | None
    step_resolution: Resolution
    context_after_step: WorkflowContext


def _resolution_from_dispatch(
    dispatch: InterpretationDispatch,
) -> Resolution:
    if dispatch is InterpretationDispatch.route_to_confirm:
        return Resolution.resolved
    if dispatch is InterpretationDispatch.route_read_only:
        return Resolution.resolved
    if dispatch is InterpretationDispatch.route_meta:
        return Resolution.resolved
    if dispatch is InterpretationDispatch.request_clarification:
        return Resolution.clarification_needed
    if dispatch is InterpretationDispatch.refuse_planned_not_implemented:
        return Resolution.refused_planned
    if dispatch is InterpretationDispatch.refuse_unsafe_instruction:
        return Resolution.refused_unsafe
    if dispatch is InterpretationDispatch.refuse_unknown_utterance:
        return Resolution.refused_unknown
    raise AssertionError(f"Unexpected dispatch: {dispatch!r}")


def _resolve_chain_classification(
    step_results: tuple[WorkflowStepResult, ...],
) -> Resolution:
    """Derive the end-to-end chain resolution from per-step results.

    The most restrictive resolution dominates: refused_unsafe >
    refused_planned > clarification_needed > refused_unknown > resolved.
    """
    if not step_results:
        return Resolution.resolved
    worst: Resolution = Resolution.resolved
    for step_result in step_results:
        current_order = _RESOLUTION_ORDER.get(step_result.step_resolution, 0)
        worst_order = _RESOLUTION_ORDER.get(worst, 0)
        if current_order > worst_order:
            worst = step_result.step_resolution
    return worst


def run_workflow_chain(
    chain: WorkflowChain,
    context: WorkflowContext | None = None,
) -> tuple[WorkflowContext, tuple[WorkflowStepResult, ...], Resolution]:
    """Run one authored workflow chain through the interpretation harness.

    Each step is interpreted and projected to a fake-provider frame. Context
    is carried between steps. Refusal propagation poisons subsequent steps.

    Returns (final_context, step_results, chain_classification).
    """
    ctx = (context or WorkflowContext()).copy()
    step_results: list[WorkflowStepResult] = []

    for step in chain.steps:
        # If the chain is already in a poisoned refusal state, short-circuit
        if ctx.chain_refusal_state is not None:
            poisoned = WorkflowStepResult(
                step_label=step.step_label,
                interpretation_result=None,
                projected_frame=None,
                step_resolution=ctx.chain_refusal_state,
                context_after_step=ctx.copy(),
            )
            step_results.append(poisoned)
            continue

        result = interpret_receptionist_utterance(step.utterance)
        assert_interpretation_result_consistency(result)

        frame = interpretation_result_to_frame(result)
        assert_interpretation_frame_consistency(frame)

        step_resolution = _resolution_from_dispatch(result.dispatch)

        # Update in-memory context
        verb = result.verb.value if result.verb else None
        resolved_action_verbs = list(ctx.accumulated_action_verbs)
        if verb and verb not in resolved_action_verbs:
            resolved_action_verbs.append(verb)

        ctx.resolved_patient_descriptor = ctx.resolved_patient_descriptor or (
            "synthetic_patient" if result.dispatch
            in (InterpretationDispatch.route_to_confirm, InterpretationDispatch.route_read_only)
            else None
        )
        ctx.resolved_practitioner_descriptor = (
            ctx.resolved_practitioner_descriptor or "synthetic_practitioner"
        )
        ctx.time_window_descriptor = ctx.time_window_descriptor or "synthetic_time_window"
        ctx.accumulated_action_verbs = tuple(resolved_action_verbs)
        ctx.preceding_frame_kind = frame.get("frame_kind", "unknown")

        # Propagate refusal state to subsequent steps
        if step_resolution in (
            Resolution.refused_unsafe,
            Resolution.refused_planned,
            Resolution.refused_unknown,
        ):
            ctx.chain_refusal_state = step_resolution

        step_results.append(
            WorkflowStepResult(
                step_label=step.step_label,
                interpretation_result=result,
                projected_frame=frame,
                step_resolution=step_resolution,
                context_after_step=ctx.copy(),
            )
        )

    chain_classification = _resolve_chain_classification(tuple(step_results))
    return ctx, tuple(step_results), chain_classification


def build_chain_report(
    chains: tuple[WorkflowChain, ...],
    chain_results: tuple[tuple[WorkflowStepResult, ...], ...],
    chain_classifications: tuple[Resolution, ...],
) -> dict[str, Any]:
    """Build a safe aggregate report from chain harness runs.

    Omits utterance text, payload IDs, patient/practitioner/appointment/slot
    identifiers, and all raw fixture content.
    """
    total_steps = sum(len(results) for results in chain_results)
    resolution_counts: dict[str, int] = {}
    frame_kind_counts: dict[str, int] = {}
    chain_resolution_counts: dict[str, int] = {}

    for results in chain_results:
        for step_result in results:
            res_key = step_result.step_resolution.value
            resolution_counts[res_key] = resolution_counts.get(res_key, 0) + 1

            if step_result.projected_frame:
                fk = step_result.projected_frame.get("frame_kind", "unknown")
                frame_kind_counts[fk] = frame_kind_counts.get(fk, 0) + 1

    for classification in chain_classifications:
        key = classification.value
        chain_resolution_counts[key] = chain_resolution_counts.get(key, 0) + 1

    return {
        "schema_version": WF_CHAIN_REPORT_SCHEMA_VERSION,
        "source": "authored_synthetic_aggregate",
        "chain_count": len(chains),
        "step_count": total_steps,
        "resolution_counts": dict(sorted(resolution_counts.items())),
        "frame_kind_counts": dict(sorted(frame_kind_counts.items())),
        "chain_resolution_counts": dict(sorted(chain_resolution_counts.items())),
        "omitted_fields": [
            "utterance",
            "patient_id",
            "practitioner_id",
            "appointment_id",
            "slot_id",
            "payload",
        ],
        "boundaries": {
            "provider_calls": "prohibited",
            "route_calls": "prohibited",
            "database_access": "prohibited",
            "raw_trove_access": "prohibited",
            "runtime_memory": "prohibited",
        },
    }


def _walk_report_values(value: Any) -> tuple[str, ...]:
    """Recursively extract all string-like leaf values from a report dict."""
    if isinstance(value, dict):
        parts: list[str] = []
        for key, child in value.items():
            parts.append(str(key))
            parts.extend(_walk_report_values(child))
        return tuple(parts)
    if isinstance(value, list):
        parts = []
        for child in value:
            parts.extend(_walk_report_values(child))
        return tuple(parts)
    return (str(value),)


def assert_workflow_chain_report_safety(
    report: dict[str, Any],
) -> None:
    """Assert a workflow chain report remains aggregate-only and non-authoritative."""
    assert report.get("schema_version") == WF_CHAIN_REPORT_SCHEMA_VERSION
    assert report.get("source") == "authored_synthetic_aggregate"
    assert isinstance(report.get("chain_count"), int)
    assert isinstance(report.get("step_count"), int)
    assert report["chain_count"] > 0
    assert report["step_count"] > 0

    boundaries = report.get("boundaries")
    assert boundaries == {
        "provider_calls": "prohibited",
        "route_calls": "prohibited",
        "database_access": "prohibited",
        "raw_trove_access": "prohibited",
        "runtime_memory": "prohibited",
    }
    omitted_fields = report.get("omitted_fields")
    assert omitted_fields == [
        "utterance",
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "slot_id",
        "payload",
    ]

    searchable_parts = tuple(
        part.casefold()
        for part in _walk_report_values(report)
        if part not in omitted_fields
    )
    for fragment in _FORBIDDEN_REPORT_FRAGMENTS:
        assert not any(fragment in part for part in searchable_parts), (
            f"Forbidden report fragment found: {fragment!r}"
        )


def assert_step_result_consistency(
    step_result: WorkflowStepResult,
    chain_classification: Resolution,
) -> None:
    """Assert one chain step result preserves invariants."""
    assert isinstance(step_result.step_label, str)
    assert step_result.step_label
    assert isinstance(step_result.step_resolution, Resolution)

    if step_result.context_after_step is not None:
        ctx = step_result.context_after_step
        if step_result.step_resolution is Resolution.resolved:
            assert ctx.chain_refusal_state is None
        elif step_result.step_resolution in (
            Resolution.refused_unsafe,
            Resolution.refused_planned,
            Resolution.refused_unknown,
        ):
            assert ctx.chain_refusal_state is not None
            assert ctx.chain_refusal_state is step_result.step_resolution

    if (
        step_result.context_after_step
        and step_result.context_after_step.chain_refusal_state
        and step_result.interpretation_result is None
        and step_result.projected_frame is None
    ):
        assert step_result.step_resolution == step_result.context_after_step.chain_refusal_state


def assert_chain_consistency(
    step_results: tuple[WorkflowStepResult, ...],
    classification: Resolution,
) -> None:
    """Assert cross-step invariants for one complete chain run."""
    assert isinstance(step_results, tuple)
    assert isinstance(classification, Resolution)
    assert step_results

    has_refused_unsafe = any(
        sr.step_resolution is Resolution.refused_unsafe for sr in step_results
    )
    has_refused_planned = any(
        sr.step_resolution is Resolution.refused_planned for sr in step_results
    )
    has_clarification = any(
        sr.step_resolution is Resolution.clarification_needed for sr in step_results
    )
    has_refused_unknown = any(
        sr.step_resolution is Resolution.refused_unknown for sr in step_results
    )

    if has_refused_unsafe:
        assert classification is Resolution.refused_unsafe
    elif has_refused_planned:
        assert classification is Resolution.refused_planned
    elif has_clarification:
        assert classification is Resolution.clarification_needed
    elif has_refused_unknown:
        assert classification is Resolution.refused_unknown
    else:
        assert classification is Resolution.resolved

    last_resolved_or_clarified = -1
    for i, sr in enumerate(step_results):
        if sr.step_resolution in (
            Resolution.resolved,
            Resolution.clarification_needed,
        ):
            last_resolved_or_clarified = i

    for i, sr in enumerate(step_results):
        if i <= last_resolved_or_clarified:
            continue
        if sr.step_resolution not in (
            Resolution.refused_unsafe,
            Resolution.refused_planned,
            Resolution.refused_unknown,
        ):
            continue
        assert sr.context_after_step.chain_refusal_state is sr.step_resolution, (
            f"Step {i} ({sr.step_label}) has resolution {sr.step_resolution.value} "
            f"but context refusal state is {sr.context_after_step.chain_refusal_state}"
        )


__all__ = [
    "WORKFLOW_CHAIN_HARNESS_SCHEMA_VERSION",
    "WF_CHAIN_REPORT_SCHEMA_VERSION",
    "Resolution",
    "WorkflowStep",
    "WorkflowChain",
    "WorkflowContext",
    "WorkflowStepResult",
    "assert_chain_consistency",
    "assert_step_result_consistency",
    "assert_workflow_chain_report_safety",
    "build_chain_report",
    "run_workflow_chain",
]
