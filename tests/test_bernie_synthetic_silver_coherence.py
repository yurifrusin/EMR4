import json

from app.services.bernie.synthetic_noise_coherence import (
    COHERENT_ADMISSION_PATH,
    COHERENT_CANDIDATE_PATH,
    DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH,
    DEFAULT_FINAL_REPORT_PATH,
    DEFAULT_PRE_REPORT_PATH,
    build_final_artifacts,
    build_accepted_robustness_report,
    build_pre_repair_report,
)
from app.services.bernie.synthetic_noise_corpus import load_jsonl


def test_pre_repair_audit_is_complete_and_parser_independent() -> None:
    report = build_pre_repair_report()
    assert report["decision"] == "audit_complete"
    assert report["population"]["candidates"] == 192
    assert report["boundaries"]["product_parser_used_for_decisions"] is False
    assert report["boundaries"]["protected_holdout_access"] is False
    assert len(report["cases"]) == 192


def test_final_artifacts_quarantine_oracle_conflicts_and_repair_only_text() -> None:
    candidates, report, admission = build_final_artifacts()
    assert len(candidates) == 192
    assert report["population"]["accepted"] == admission["accepted_count"]
    assert report["population"]["quarantined_or_rejected"] == admission["quarantine_count"]
    assert admission["decision"] == "partial_pass_with_quarantine"
    assert admission["rejected_count"] == 0
    assert admission["accepted_count"] + admission["quarantine_count"] == 192
    assert all(value is False for value in admission["authority_grant"].values())
    repaired = [
        candidate
        for candidate in candidates
        if candidate["source_seed_id"] == "bernie_noise_seed_094"
    ]
    assert len(repaired) == 2
    assert all(
        candidate["dialogue_turns"][-1]["utterance"]
        == "Use that diary request as the reference."
        for candidate in repaired
    )


def test_committed_coherence_artifacts_regenerate_exactly() -> None:
    candidates, final_report, admission = build_final_artifacts()
    assert json.loads(DEFAULT_PRE_REPORT_PATH.read_text(encoding="utf-8")) == build_pre_repair_report()
    assert json.loads(DEFAULT_FINAL_REPORT_PATH.read_text(encoding="utf-8")) == final_report
    assert json.loads(COHERENT_ADMISSION_PATH.read_text(encoding="utf-8")) == admission
    assert load_jsonl(COHERENT_CANDIDATE_PATH) == candidates


def test_accepted_population_runs_twice_with_closed_safety_and_variance() -> None:
    report = build_accepted_robustness_report()
    assert report["decision"] == "accepted_population_evaluation_complete"
    assert report["population"]["candidates"] == 90
    assert report["population"]["observations"] == 180
    assert report["variance"]["variant_candidate_count"] == 0
    assert report["safety"] == {"passed": 180, "failed": 0, "total": 180}
    assert report["boundaries"]["parser_or_policy_changes"] is False
    assert (
        json.loads(
            DEFAULT_ACCEPTED_ROBUSTNESS_REPORT_PATH.read_text(encoding="utf-8")
        )
        == report
    )
