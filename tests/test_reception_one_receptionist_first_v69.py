from __future__ import annotations

import json

from scripts import reception_one_receptionist_first_v68 as frozen
from scripts import reception_one_receptionist_first_v69_cohort as cohort


def test_holdout_is_new_and_frozen_against_v68_contract() -> None:
    manifest, cases = cohort.load_source_manifest()
    assert len(cases) == 12
    assert manifest["holdout"]["previously_sent_to_provider"] is False
    assert manifest["holdout"]["may_be_used_for_prompt_or_proofreader_tuning"] is False
    assert manifest["holdout"]["sealed_before_first_provider_call"] is True
    assert manifest["absolute_call_ceiling"] == 24
    assert len({case["case_code"] for case in cases}) == 12
    assert all(case["case_code"].startswith("h-") for case in cases)


def test_all_holdout_oracles_admit_under_exact_frozen_v68_lane() -> None:
    evidence = cohort.build_provider_blocked_evidence(write_frames=False)
    assert evidence["provider_calls_performed"] == 0
    assert evidence["source_case_count"] == 12
    assert evidence["paired_development_not_holdout"] is False
    assert evidence["all_original_v6_cases_included"] is False
    assert evidence["contract"]["system_instruction_sha256"] == frozen.canonical_hash(
        {"text": frozen.SYSTEM_INSTRUCTION}
    )
    assert all(
        row["proofreader_disposition"] == "admit"
        for row in evidence["case_oracles"]
    )


def test_holdout_frames_remain_authored_synthetic_and_non_writing() -> None:
    _, cases = cohort.load_source_manifest()
    for case in cases:
        frame = cohort.frame_for_case(case)
        assert frame["data_class"] == "authored_synthetic"
        assert frame["authority"]["effect_ceiling"] == "proposal_only"
        assert frame["authority"]["database_access"] is False
        assert frame["authority"]["appointment_write_authority"] is False
        assert frame["authority"]["product_delivery"] is False


def test_closed_occupied_holdout_is_exact_and_all_ledgers_are_consumed() -> None:
    evidence = json.loads(cohort.OCCUPIED_PATH.read_text(encoding="utf-8"))
    assert evidence["evidence_hash"] == cohort.base._content_hash(evidence)
    assert (
        evidence["result"]
        == "reception_one_receptionist_first_v69_untouched_holdout_pass"
    )
    assert evidence["schema_version"] == (
        "reception.one.receptionist_first_v69.untouched_holdout.v1"
    )
    assert evidence["case_count"] == 12
    assert evidence["total_actual_provider_calls"] == 13
    assert evidence["capability_threshold_passed"] is True
    assert evidence["all_ledgers_consumed"] is True
    assert evidence["all_cleanup_passed"] is True
    assert evidence["holdout"] == {
        "evaluated_contract": "byte_frozen_v68",
        "provider_exposure_before_this_run": False,
        "sealed_before_first_provider_call": True,
        "used_for_prompt_schema_proofreader_or_oracle_tuning": False,
    }
    assert all(
        row["expected_safe_outcome"] and row["cleanup_passed"]
        for row in evidence["cases"]
    )
    ledger_paths = sorted(cohort.ARTIFACT_DIR.glob("cases/**/*-ledger.json"))
    assert len(ledger_paths) == 13
    assert all(
        json.loads(path.read_text(encoding="utf-8"))["status"] == "consumed"
        for path in ledger_paths
    )
