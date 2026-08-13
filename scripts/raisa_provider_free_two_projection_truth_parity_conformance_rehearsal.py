"""Evidence-only normalization for two-projection Diary truth parity.

This module is a repository conformance helper. It is not imported by product
code and does not perform network, database, provider, or product operations.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any


SCHEMA_VERSION = "raisa.projection-truth-trace.v1"
EVIDENCE_MODE = "route_intercepted_browser"
RENDERERS = ("conventional_grid", "reception_one")
SCENARIOS = ("safe", "cancelled", "blocked", "stale", "failed", "committed")
TRACE_KEYS = frozenset(
    {
        "schema_version",
        "evidence_mode",
        "renderer",
        "scenario",
        "selected_current_coordinate",
        "proposal_outcome",
        "confirmation_outcome",
        "kernel_result",
        "fresh_read_result",
        "displayed_terminal_state",
        "route_counts",
        "renderer_local",
    }
)
KERNEL_FIELDS = (
    "scenario",
    "selected_current_coordinate",
    "proposal_outcome",
    "confirmation_outcome",
    "kernel_result",
    "fresh_read_result",
    "displayed_terminal_state",
    "route_counts",
)


EXPECTED_BY_SCENARIO: dict[str, dict[str, Any]] = {
    "safe": {
        "requested_status": "Arrived",
        "proposal_outcome": "safe",
        "confirmation_outcome": "confirmed_without_staff_dialog",
        "kernel_result": "committed",
        "terminal_status": "Arrived",
        "freshness_basis": "fresh_authoritative_reconciliation",
        "route_counts": {"proposal": 1, "confirm": 1, "raw_compatibility": 0},
    },
    "cancelled": {
        "requested_status": "Cancelled",
        "proposal_outcome": "confirmation_required",
        "confirmation_outcome": "staff_cancelled",
        "kernel_result": "no_commit_cancelled",
        "terminal_status": "Booked",
        "freshness_basis": "no_commit_preserved_current_truth",
        "route_counts": {"proposal": 1, "confirm": 0, "raw_compatibility": 0},
    },
    "blocked": {
        "requested_status": "Arrived",
        "proposal_outcome": "blocked",
        "confirmation_outcome": "not_offered",
        "kernel_result": "no_commit_blocked",
        "terminal_status": "Booked",
        "freshness_basis": "no_commit_preserved_current_truth",
        "route_counts": {"proposal": 1, "confirm": 0, "raw_compatibility": 0},
    },
    "stale": {
        "requested_status": "Arrived",
        "proposal_outcome": "safe",
        "confirmation_outcome": "stale_rejected",
        "kernel_result": "no_commit_stale",
        "terminal_status": "Booked",
        "freshness_basis": "no_commit_preserved_current_truth",
        "route_counts": {"proposal": 1, "confirm": 1, "raw_compatibility": 0},
    },
    "failed": {
        "requested_status": "Arrived",
        "proposal_outcome": "unavailable",
        "confirmation_outcome": "not_reached",
        "kernel_result": "no_commit_failed",
        "terminal_status": "Booked",
        "freshness_basis": "no_commit_preserved_current_truth",
        "route_counts": {"proposal": 1, "confirm": 0, "raw_compatibility": 0},
    },
    "committed": {
        "requested_status": "Completed",
        "proposal_outcome": "confirmation_required",
        "confirmation_outcome": "staff_confirmed",
        "kernel_result": "committed",
        "terminal_status": "Completed",
        "freshness_basis": "fresh_authoritative_reconciliation",
        "route_counts": {"proposal": 1, "confirm": 1, "raw_compatibility": 0},
    },
}


def expected_kernel_trace(scenario: str) -> dict[str, Any]:
    """Return the frozen renderer-neutral expectation for one scenario."""

    if scenario not in EXPECTED_BY_SCENARIO:
        raise ValueError(f"unknown truth-parity scenario: {scenario}")
    expected = EXPECTED_BY_SCENARIO[scenario]
    return {
        "scenario": scenario,
        "selected_current_coordinate": {
            "practice_scope": "authored-synthetic-practice",
            "appointment_id": "truth-parity-status-1",
            "observed_status": "Booked",
            "requested_status": expected["requested_status"],
        },
        "proposal_outcome": expected["proposal_outcome"],
        "confirmation_outcome": expected["confirmation_outcome"],
        "kernel_result": expected["kernel_result"],
        "fresh_read_result": {
            "current_status": expected["terminal_status"],
            "basis": expected["freshness_basis"],
        },
        "displayed_terminal_state": {"status": expected["terminal_status"]},
        "route_counts": deepcopy(expected["route_counts"]),
    }


def build_trace(
    *,
    renderer: str,
    scenario: str,
    observed: Mapping[str, Any],
    renderer_local: Mapping[str, str],
) -> dict[str, Any]:
    """Build a closed trace from browser observations and reject drift."""

    if renderer not in RENDERERS:
        raise ValueError(f"unknown renderer: {renderer}")
    expected = expected_kernel_trace(scenario)
    actual = {field: deepcopy(observed[field]) for field in KERNEL_FIELDS}
    if actual != expected:
        raise ValueError(
            f"kernel trace mismatch for {renderer}/{scenario}: "
            f"expected={expected!r} actual={actual!r}"
        )
    local = dict(renderer_local)
    if set(local) != {"layout", "wording", "focus_target", "history_behavior"}:
        raise ValueError("renderer_local must contain only layout, wording, focus_target, history_behavior")
    trace = {
        "schema_version": SCHEMA_VERSION,
        "evidence_mode": EVIDENCE_MODE,
        "renderer": renderer,
        **actual,
        "renderer_local": local,
    }
    if set(trace) != TRACE_KEYS:
        raise AssertionError("closed trace construction drifted")
    return trace


def kernel_projection(trace: Mapping[str, Any]) -> dict[str, Any]:
    """Return only fields whose semantics must agree across renderers."""

    if set(trace) != TRACE_KEYS:
        raise ValueError("trace has missing or additional fields")
    if trace.get("schema_version") != SCHEMA_VERSION or trace.get("evidence_mode") != EVIDENCE_MODE:
        raise ValueError("trace contract or evidence mode mismatch")
    return {field: deepcopy(trace[field]) for field in KERNEL_FIELDS}


def compare_paired_traces(traces: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Fail closed unless one equal trace exists per renderer and scenario."""

    indexed: dict[tuple[str, str], Mapping[str, Any]] = {}
    for trace in traces:
        renderer = str(trace.get("renderer", ""))
        scenario = str(trace.get("scenario", ""))
        key = (renderer, scenario)
        if renderer not in RENDERERS or scenario not in SCENARIOS:
            raise ValueError(f"unknown trace coordinate: {key}")
        if key in indexed:
            raise ValueError(f"duplicate trace coordinate: {key}")
        indexed[key] = trace
    expected_keys = {(renderer, scenario) for renderer in RENDERERS for scenario in SCENARIOS}
    if set(indexed) != expected_keys:
        missing = sorted(expected_keys - set(indexed))
        extra = sorted(set(indexed) - expected_keys)
        raise ValueError(f"incomplete trace matrix: missing={missing} extra={extra}")

    comparisons: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        conventional = kernel_projection(indexed[("conventional_grid", scenario)])
        reception = kernel_projection(indexed[("reception_one", scenario)])
        if conventional != reception:
            raise ValueError(f"kernel truth differs across projections for {scenario}")
        comparisons.append(
            {
                "scenario": scenario,
                "kernel_fields_equal": True,
                "raw_compatibility_requests": conventional["route_counts"]["raw_compatibility"],
            }
        )
    return comparisons
