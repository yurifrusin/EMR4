"""Protected v5 evaluator adapter over the explicit Option A ordinary path."""

from app.services.bernie.composed_corpus_evaluator import PolicyVersion, compose_versioned
from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
from app.services.bernie.lc4v5_holdout_framework import EvaluationBatch
from app.services.bernie.scenario_spec import ReceptionScenarioSpec


def evaluate_v5(scenarios: list[ReceptionScenarioSpec]) -> EvaluationBatch:
    results = []
    for scenario in scenarios:
        for sample_index in (0, 1):
            composed = compose_versioned(
                scenario,
                sample_index=sample_index,
                policy_version=PolicyVersion.OPTION_A,
            )
            results.append(
                score_interpretation_replay_pair(
                    scenario,
                    composed.interpretation,
                    composed.replay,
                )
            )
    return EvaluationBatch(results=results, exception_count=0)


__all__ = ["evaluate_v5"]
