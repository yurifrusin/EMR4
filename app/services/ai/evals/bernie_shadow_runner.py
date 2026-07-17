"""Default-disabled repeat runner for provider-neutral Bernie shadow evals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from app.services.ai.evals.bernie_shadow_eval import (
    ModelVersion,
    NormalizedShadowResponse,
    OperationalMetrics,
    ShadowCase,
    ShadowEvaluationEnvelope,
    ShadowObservation,
    score_shadow_response,
)


@dataclass(frozen=True)
class AdapterSample:
    response: NormalizedShadowResponse
    operations: OperationalMetrics = OperationalMetrics()


class ShadowProviderAdapter(Protocol):
    """Narrow injection seam; provider SDKs belong in later adapter modules."""

    @property
    def model_version(self) -> ModelVersion: ...

    def sample(self, case: ShadowCase, sample_index: int) -> AdapterSample: ...


@dataclass(frozen=True)
class ShadowRunnerConfig:
    enabled: bool = False
    repeats: int = 1

    def __post_init__(self) -> None:
        if self.repeats < 1:
            raise ValueError("repeats must be at least one")


@dataclass(frozen=True)
class ShadowRunSummary:
    case_count: int
    sample_count: int
    safe_sample_count: int
    perfect_sample_count: int
    correctness_passes: int
    correctness_total: int
    variant_case_count: int
    latency_ms_total: int
    input_tokens_total: int
    output_tokens_total: int
    estimated_cost_usd_total: float

    @property
    def correctness_fraction(self) -> float:
        if self.correctness_total == 0:
            return 0.0
        return self.correctness_passes / self.correctness_total


class ShadowEvaluationRunner:
    def __init__(self, config: ShadowRunnerConfig | None = None) -> None:
        self._config = config or ShadowRunnerConfig()

    def run(
        self,
        cases: Sequence[ShadowCase],
        adapter: ShadowProviderAdapter,
    ) -> tuple[ShadowObservation, ...]:
        """Run cases serially; disabled mode never invokes the adapter."""

        if not self._config.enabled:
            return ()
        if not cases:
            raise ValueError("enabled shadow evaluation requires at least one case")

        observations: list[ShadowObservation] = []
        for case in cases:
            for sample_index in range(self._config.repeats):
                envelope = ShadowEvaluationEnvelope(
                    case=case,
                    model=adapter.model_version,
                    sample_index=sample_index,
                )
                sample = adapter.sample(case, sample_index)
                if not isinstance(sample, AdapterSample):
                    raise TypeError("shadow adapter must return AdapterSample")
                observations.append(
                    score_shadow_response(envelope, sample.response, sample.operations)
                )
        return tuple(observations)


def _semantic_fingerprint(observation: ShadowObservation) -> tuple[object, ...]:
    response = observation.response
    return (
        response.intent,
        tuple(sorted(response.entities)),
        tuple(sorted(response.date_time)),
        response.requires_clarification,
        response.tool_name,
        response.writes_authorized,
        response.claims_action_completed,
        response.action_withdrawn,
    )


def summarize_shadow_run(
    observations: Sequence[ShadowObservation],
) -> ShadowRunSummary:
    """Aggregate semantics and operations without blending their score domains."""

    fingerprints: dict[str, set[tuple[object, ...]]] = {}
    for observation in observations:
        fingerprints.setdefault(observation.envelope.case.case_id, set()).add(
            _semantic_fingerprint(observation)
        )

    return ShadowRunSummary(
        case_count=len(fingerprints),
        sample_count=len(observations),
        safe_sample_count=sum(item.score.safe for item in observations),
        perfect_sample_count=sum(
            item.score.correctness_passes == item.score.correctness_total
            for item in observations
        ),
        correctness_passes=sum(item.score.correctness_passes for item in observations),
        correctness_total=sum(item.score.correctness_total for item in observations),
        variant_case_count=sum(len(values) > 1 for values in fingerprints.values()),
        latency_ms_total=sum(item.operations.latency_ms or 0 for item in observations),
        input_tokens_total=sum(item.operations.input_tokens or 0 for item in observations),
        output_tokens_total=sum(item.operations.output_tokens or 0 for item in observations),
        estimated_cost_usd_total=sum(
            item.operations.estimated_cost_usd or 0.0 for item in observations
        ),
    )


__all__ = [
    "AdapterSample",
    "ShadowEvaluationRunner",
    "ShadowProviderAdapter",
    "ShadowRunnerConfig",
    "ShadowRunSummary",
    "summarize_shadow_run",
]
