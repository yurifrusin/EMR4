from __future__ import annotations

import json

from app.services.bernie.synthetic_noise_action_temporal import (
    BASELINE_REPORT_PATH,
    EXPECTED_SELECTED_CANDIDATES,
    FINAL_REPORT_PATH,
    SELECTION_PATH,
    build_tranche_report,
)
from app.services.bernie.synthetic_noise_robustness import _sha256


def test_action_temporal_selection_is_exact_and_closed() -> None:
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    selected = selection["selected_candidates"]
    assert len(selected) == EXPECTED_SELECTED_CANDIDATES
    assert len({item["candidate_id"] for item in selected}) == 24
    assert selection["selection_counts"] == {
        "total": 24,
        "action_extraction": 12,
        "temporal_normalization": 10,
        "replay_controls": 2,
    }
    assert not any(selection["boundaries"].values())


def test_action_temporal_pre_repair_report_is_immutable() -> None:
    report = json.loads(BASELINE_REPORT_PATH.read_text(encoding="utf-8"))
    without_hash = {key: value for key, value in report.items() if key != "report_hash"}
    assert report["report_hash"] == (
        "sha256:1bf572c3906fe108cd81332953ae3333d033b6afc2f34827b2cdd0f1154e3822"
    )
    assert _sha256(without_hash) == report["report_hash"]
    assert report["population"] == {
        "candidates": 24,
        "repeats_per_candidate": 2,
        "observations": 48,
        "complete_candidates": 0,
        "failed_candidates": 24,
    }
    assert report["variance"] == {
        "variant_candidate_count": 0,
        "variant_candidate_ids": [],
    }
    assert report["dimension_counts"]["safety"] == {
        "passed": 48,
        "failed": 0,
        "total": 48,
    }
    assert report["primary_diagnostic_candidate_counts"] == {
        "action_extraction": 12,
        "replay_integration": 2,
        "temporal_normalization": 10,
    }


def test_action_temporal_post_repair_report_is_complete_and_deterministic() -> None:
    report = build_tranche_report()
    assert report["decision"] == "tranche_evaluation_complete"
    assert report["population"] == {
        "candidates": 24,
        "repeats_per_candidate": 2,
        "observations": 48,
        "complete_candidates": 2,
        "failed_candidates": 22,
    }
    assert report["variance"] == {
        "variant_candidate_count": 0,
        "variant_candidate_ids": [],
    }
    assert report["dimension_counts"]["safety"] == {
        "passed": 48,
        "failed": 0,
        "total": 48,
    }


def test_action_temporal_final_report_regenerates_without_utterances() -> None:
    report = build_tranche_report()
    committed = json.loads(FINAL_REPORT_PATH.read_text(encoding="utf-8"))
    assert committed == report

    def keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value) | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value))
        return set()

    assert {"utterance", "dialogue_turns", "source_spans"}.isdisjoint(keys(report))
    assert report["boundaries"]["scorer_oracle_used_by_interpreter"] is False
