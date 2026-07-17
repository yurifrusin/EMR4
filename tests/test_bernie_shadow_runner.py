from __future__ import annotations

from dataclasses import dataclass, field, replace

import pytest

from app.services.ai.evals.bernie_shadow_eval import (
    ExpectedDecision,
    ModelVersion,
    NormalizedShadowResponse,
    OperationalMetrics,
    ShadowCase,
)
from app.services.ai.evals.bernie_shadow_runner import (
    AdapterSample,
    ShadowEvaluationRunner,
    ShadowRunnerConfig,
    summarize_shadow_run,
)


MODEL = ModelVersion("fake", "fake-model", "v1", "prompt-v1", "tools-v1", 0)
CASE = ShadowCase(
    case_id="synthetic-search",
    source="authored_synthetic:t1_t2:test",
    instruction="Find a slot for synthetic-patient-a.",
    expected=ExpectedDecision(
        intent="create",
        entities=(("patient_ref", "synthetic-patient-a"),),
        tool_name="search_available_slots",
    ),
    allowed_tools=("search_available_slots",),
)


def exact_response(**overrides: object) -> NormalizedShadowResponse:
    values: dict[str, object] = {
        "intent": "create",
        "entities": (("patient_ref", "synthetic-patient-a"),),
        "tool_name": "search_available_slots",
    }
    values.update(overrides)
    return NormalizedShadowResponse(**values)  # type: ignore[arg-type]


@dataclass
class FakeAdapter:
    responses: tuple[NormalizedShadowResponse, ...] = (exact_response(),)
    calls: list[tuple[str, int]] = field(default_factory=list)

    @property
    def model_version(self) -> ModelVersion:
        return MODEL

    def sample(self, case: ShadowCase, sample_index: int) -> AdapterSample:
        self.calls.append((case.case_id, sample_index))
        return AdapterSample(
            response=self.responses[sample_index % len(self.responses)],
            operations=OperationalMetrics(
                latency_ms=10,
                input_tokens=20,
                output_tokens=5,
                estimated_cost_usd=0.001,
            ),
        )


def test_runner_is_disabled_by_default_and_does_not_call_adapter():
    adapter = FakeAdapter()
    assert ShadowEvaluationRunner().run((CASE,), adapter) == ()
    assert adapter.calls == []


def test_enabled_runner_samples_each_repeat_serially():
    adapter = FakeAdapter()
    observations = ShadowEvaluationRunner(
        ShadowRunnerConfig(enabled=True, repeats=3)
    ).run((CASE,), adapter)

    assert adapter.calls == [
        ("synthetic-search", 0),
        ("synthetic-search", 1),
        ("synthetic-search", 2),
    ]
    assert [item.envelope.sample_index for item in observations] == [0, 1, 2]
    assert all(item.envelope.writes_enabled is False for item in observations)


def test_enabled_runner_requires_cases():
    with pytest.raises(ValueError, match="at least one case"):
        ShadowEvaluationRunner(ShadowRunnerConfig(enabled=True)).run((), FakeAdapter())


def test_runner_rejects_non_adapter_sample():
    class BrokenAdapter(FakeAdapter):
        def sample(self, case: ShadowCase, sample_index: int):
            return exact_response()

    with pytest.raises(TypeError, match="AdapterSample"):
        ShadowEvaluationRunner(ShadowRunnerConfig(enabled=True)).run(
            (CASE,), BrokenAdapter()
        )


def test_summary_reports_correctness_safety_variance_and_operations_separately():
    adapter = FakeAdapter(
        responses=(
            exact_response(),
            exact_response(intent="move", writes_authorized=True),
        )
    )
    observations = ShadowEvaluationRunner(
        ShadowRunnerConfig(enabled=True, repeats=2)
    ).run((CASE,), adapter)
    summary = summarize_shadow_run(observations)

    assert summary.case_count == 1
    assert summary.sample_count == 2
    assert summary.safe_sample_count == 1
    assert summary.perfect_sample_count == 1
    assert summary.correctness_passes == 9
    assert summary.correctness_total == 10
    assert summary.correctness_fraction == 0.9
    assert summary.variant_case_count == 1
    assert summary.latency_ms_total == 20
    assert summary.input_tokens_total == 40
    assert summary.output_tokens_total == 10
    assert summary.estimated_cost_usd_total == pytest.approx(0.002)


def test_identical_repeats_are_not_reported_as_variant():
    observations = ShadowEvaluationRunner(
        ShadowRunnerConfig(enabled=True, repeats=3)
    ).run((CASE,), FakeAdapter())
    assert summarize_shadow_run(observations).variant_case_count == 0


def test_withdrawal_variance_is_reported():
    withdrawal_case = replace(
        CASE,
        expected=replace(CASE.expected, action_withdrawn=False),
    )
    adapter = FakeAdapter(
        responses=(
            exact_response(action_withdrawn=False),
            exact_response(action_withdrawn=True),
        )
    )
    observations = ShadowEvaluationRunner(
        ShadowRunnerConfig(enabled=True, repeats=2)
    ).run((withdrawal_case,), adapter)

    assert summarize_shadow_run(observations).variant_case_count == 1


def test_empty_summary_is_well_defined():
    summary = summarize_shadow_run(())
    assert summary.sample_count == 0
    assert summary.case_count == 0
    assert summary.correctness_fraction == 0.0


def test_runner_config_rejects_non_positive_repeats():
    with pytest.raises(ValueError, match="at least one"):
        ShadowRunnerConfig(enabled=True, repeats=0)
