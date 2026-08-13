from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

from scripts.raisa_provider_free_two_projection_truth_parity_conformance_rehearsal import (
    RENDERERS,
    SCENARIOS,
    build_trace,
    compare_paired_traces,
    expected_kernel_trace,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "orchestration/continuity/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal/projection-truth-trace.schema.json"


def _trace(renderer: str, scenario: str) -> dict:
    expected = expected_kernel_trace(scenario)
    return build_trace(
        renderer=renderer,
        scenario=scenario,
        observed=expected,
        renderer_local={
            "layout": f"{renderer}-layout",
            "wording": f"{renderer} administrative wording",
            "focus_target": f"{renderer}-status-control",
            "history_behavior": f"{renderer}-local-history",
        },
    )


def test_closed_schema_accepts_exact_twelve_trace_matrix() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    traces = [_trace(renderer, scenario) for renderer in RENDERERS for scenario in SCENARIOS]
    for trace in traces:
        validator.validate(trace)
    assert compare_paired_traces(traces) == [
        {"scenario": scenario, "kernel_fields_equal": True, "raw_compatibility_requests": 0}
        for scenario in SCENARIOS
    ]


def test_renderer_local_differences_do_not_change_kernel_projection() -> None:
    conventional = _trace("conventional_grid", "committed")
    reception = _trace("reception_one", "committed")
    assert conventional["renderer_local"] != reception["renderer_local"]
    assert compare_paired_traces(
        [
            _trace(renderer, scenario)
            for renderer in RENDERERS
            for scenario in SCENARIOS
        ]
    )[-1]["kernel_fields_equal"] is True


@pytest.mark.parametrize("field", [
    "selected_current_coordinate",
    "proposal_outcome",
    "confirmation_outcome",
    "kernel_result",
    "fresh_read_result",
    "displayed_terminal_state",
    "route_counts",
])
def test_each_kernel_field_mismatch_fails_closed(field: str) -> None:
    traces = [_trace(renderer, scenario) for renderer in RENDERERS for scenario in SCENARIOS]
    target = next(
        trace for trace in traces
        if trace["renderer"] == "reception_one" and trace["scenario"] == "safe"
    )
    if isinstance(target[field], dict):
        target[field] = {"tampered": True}
    else:
        target[field] = "tampered"
    with pytest.raises(ValueError):
        compare_paired_traces(traces)


def test_missing_duplicate_unknown_and_extra_trace_fields_fail_closed() -> None:
    traces = [_trace(renderer, scenario) for renderer in RENDERERS for scenario in SCENARIOS]
    with pytest.raises(ValueError, match="incomplete"):
        compare_paired_traces(traces[:-1])
    with pytest.raises(ValueError, match="duplicate"):
        compare_paired_traces([*traces, deepcopy(traces[0])])
    unknown = deepcopy(traces)
    unknown[0]["scenario"] = "other"
    with pytest.raises(ValueError, match="unknown"):
        compare_paired_traces(unknown)
    extra = deepcopy(traces)
    extra[0]["runtime_session"] = True
    with pytest.raises(ValueError, match="additional"):
        compare_paired_traces(extra)


def test_repository_product_source_does_not_import_evidence_helper() -> None:
    needle = "raisa_provider_free_two_projection_truth_parity_conformance_rehearsal"
    product_paths = [ROOT / "app", ROOT / "docs/diary"]
    matches: list[str] = []
    for base in product_paths:
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".js", ".html", ".css"}:
                if needle in path.read_text(encoding="utf-8", errors="ignore"):
                    matches.append(path.relative_to(ROOT).as_posix())
    assert matches == []
