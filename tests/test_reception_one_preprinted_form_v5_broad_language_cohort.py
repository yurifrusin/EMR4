from __future__ import annotations

import copy
import json

import pytest

from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_preprinted_form_v5_broad_language_cohort as broad
from scripts import reception_one_preprinted_form_v5_multicase as multicase
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_structured_source_plan_language as structured


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_freezes_twenty_four_cases_and_call_ceiling() -> None:
    manifest, cases = broad.load_manifest()

    assert manifest["maximum_primary_calls"] == 24
    assert manifest["maximum_correction_calls"] == 24
    assert manifest["absolute_call_ceiling"] == 48
    assert manifest["incremental_cost_ceiling_usd"] == 1
    assert len(cases) == 24
    assert len({case["case_code"] for case in cases}) == 24
    assert all(case["source_case_id"] is None for case in cases)
    assert manifest["frozen_condition"] == {
        "few_shot_examples": False,
        "demonstration_answers": False,
        "prompt_optimisation": False,
        "fine_tuning": False,
        "temperature": 0,
        "thinking_budget": 0,
        "mid_cohort_prompt_or_schema_change": False,
    }


def test_provider_blocked_evidence_matches_frozen_regeneration() -> None:
    recorded = _load(broad.PROVIDER_BLOCKED_PATH)
    regenerated = broad.build_provider_blocked_evidence(write_frames=False)

    assert recorded == regenerated
    assert recorded["provider_calls_performed"] == 0
    assert recorded["credential_reads_performed"] == 0
    assert recorded["case_count"] == 24
    assert all(
        oracle["proofreader_disposition"] == "admit"
        for oracle in recorded["case_oracles"]
    )


def test_prompt_and_form_contract_match_accepted_multicase_baseline() -> None:
    broad_evidence = _load(broad.PROVIDER_BLOCKED_PATH)
    baseline = _load(multicase.PROVIDER_BLOCKED_PATH)

    for field in (
        "system_instruction_sha256",
        "model_form_schema_file_sha256",
        "turn_input_schema_file_sha256",
        "correction_ticket_schema_file_sha256",
        "provider_response_schema_sha256",
        "preprinted_fields",
        "model_authored_fields",
        "temperature",
        "thinking_budget",
    ):
        assert broad_evidence["contract"][field] == baseline["contract"][field]
    assert broad_evidence["contract"]["prompt_or_schema_change_within_cohort"] is False
    assert broad_evidence["contract"]["broker_judgement_repair"] is False


def test_five_parser_safe_cases_release_clarification_only() -> None:
    evidence = _load(broad.PROVIDER_BLOCKED_PATH)
    clarifications = [
        oracle
        for oracle in evidence["case_oracles"]
        if oracle["expected_proposal_release"] is False
    ]

    assert {item["case_code"] for item in clarifications} == {
        "b-status-noshow-gap",
        "b-clarify-sort",
        "b-clarify-different",
        "b-clarify-details",
        "b-clarify-fit",
    }
    assert all(
        item["expected_final_output"]["kind"] == "clarification"
        and item["expected_final_output"]["api_spine_operation_id"] is None
        and item["expected_final_output"]["requires_human_confirmation"] is False
        and item["expected_final_output"]["write_performed"] is False
        for item in clarifications
    )


def test_status_no_show_gap_is_predeclared_and_cannot_be_rescored() -> None:
    manifest, cases = broad.load_manifest()
    gap = next(
        case for case in cases if case["case_code"] == "b-status-noshow-gap"
    )
    changed = copy.deepcopy(manifest)
    changed_gap = next(
        case
        for case in changed["cases"]
        if case["case_code"] == "b-status-noshow-gap"
    )
    changed_gap["expected_goal"] = "status_change"
    changed_gap["expected_proposal_family"] = "status_change"
    changed_gap["expected_proposal_release"] = True

    with pytest.raises(
        broad.MulticaseError,
        match="evaluation_case_set_invalid",
    ):
        with broad._configured():
            multicase._validate_manifest(changed)

    frame = broad.frame_for_case(gap)
    oracle = broad.oracle_for_case(gap, frame)
    assert oracle["oracle_goal"] == "clarification"
    assert oracle["oracle_operator_ids"] == ["request_clarification"]


def test_case_identifiers_are_distinct_and_cross_case_pairing_fails() -> None:
    _, cases = broad.load_manifest()
    attempts = []
    ledgers = []
    for case in cases:
        case_attempts, case_ledgers = broad.case_ids(case["case_code"])
        attempts.extend(case_attempts)
        ledgers.extend(case_ledgers)

    assert len(attempts) == len(set(attempts)) == 48
    assert len(ledgers) == len(set(ledgers)) == 48
    assert _load(broad.PROVIDER_BLOCKED_PATH)["cross_case_ledger_pair_rejected"] is True


def test_frames_remain_authored_synthetic_and_non_mutating() -> None:
    _, cases = broad.load_manifest()
    for case in cases:
        frame = broad.frame_for_case(case)
        assert frame["data_class"] == "authored_synthetic"
        assert frame["authority"] == {
            "effect_ceiling": "proposal_only",
            "appointment_write_authority": False,
            "confirmation_authority": False,
            "provider_execution": False,
            "network_access": False,
            "database_access": False,
            "product_delivery": False,
        }
        plan = typed_plan.deterministic_plan(frame)
        program = structured.program_from_plan(
            frame,
            plan,
            operator_note="Prepared for review; no booking was changed.",
        )
        body = preprinted.model_form_body(program)
        assert set(body) == {"operator_note", "goal_code", "steps"}
        assert preprinted.assemble_program(body) == program


def test_family_summary_uses_only_bounded_occupied_fields() -> None:
    fixture = {
        "cases": [
            {
                "case_code": "b-create-arrange",
                "primary_proofreader_disposition": "admit",
                "correction_used": False,
            },
            {
                "case_code": "b-create-alias",
                "primary_proofreader_disposition": "revision_required",
                "correction_used": True,
            },
            {
                "case_code": "b-clarify-fit",
                "primary_proofreader_disposition": "admit",
                "correction_used": False,
            },
        ]
    }

    assert broad.summarize_language_families(fixture) == {
        "create": {"cases": 2, "primary_admits": 1, "corrections": 1},
        "clarify": {"cases": 1, "primary_admits": 1, "corrections": 0},
    }


def test_closed_safe_oracle_mismatch_is_recorded_not_batch_aborted() -> None:
    case = {
        "case_code": "b-create-preface",
        "expected_proposal_release": True,
    }
    oracle = {
        "expected_final_output": {
            "kind": "proposal_candidate",
            "candidate_slot_ids": ["synthetic-slot-july28-1430"],
            "write_performed": False,
        }
    }
    dialogue = {
        "terminal_status": "admitted",
        "release": {
            "kind": "proposal_candidate",
            "candidate_slot_ids": [
                "synthetic-slot-july28-1430",
                "synthetic-slot-july28-1500",
            ],
            "write_performed": False,
        },
    }

    assert (
        multicase._expected_safe_outcome(
            case=case,
            oracle=oracle,
            dialogue=dialogue,
        )
        is False
    )
    training = multicase._training_disposition(
        [
            {
                "case_code": "b-create-preface",
                "primary_proofreader_disposition": "admit",
                "expected_safe_outcome": False,
                "correction_used": False,
                "primary_violation_codes": [],
            }
        ]
    )
    assert training["all_six_primary_expected_safe"] is False
    assert training["unexpected_safe_outcome_cases"] == [
        "b-create-preface"
    ]


def test_zero_call_correction_recovery_requires_exact_consumed_state(
    tmp_path,
) -> None:
    case_dir = tmp_path / "b-move-resched"
    case_dir.mkdir()
    for name in (
        "occupied-dialogue-parent-audit.jsonl",
        "occupied-turn-001-evidence.json",
        "occupied-turn-001-ledger.json",
        "occupied-turn-001-audit.jsonl",
        "occupied-turn-001-external-audit.json",
        "occupied-turn-001-correction-ticket.json",
    ):
        (case_dir / name).write_text("{}\n", encoding="utf-8")
    (case_dir / "occupied-turn-002-ledger.json").write_text(
        json.dumps(
            {
                "status": "consumed",
                "provider_calls_consumed": 0,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    event = multicase.broker.audit_event(
        sequence=1,
        previous_hash=multicase.preprinted_live.ZERO_HASH,
        event_type="broker_ready",
        fields={"provider_call": False},
    )
    (case_dir / "occupied-turn-002-audit.jsonl").write_text(
        json.dumps(event, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    assert multicase._zero_call_correction_recovery_available(
        case_dir
    )
    recovery_attempt, recovery_ledger = multicase._recovery_ids(
        "b-move-resched"
    )
    assert recovery_attempt.endswith(
        "-eval-b-move-resched-r1-turn-002"
    )
    assert recovery_ledger.endswith(
        "-eval-b-move-resched-r1-ledger-002"
    )

    (case_dir / "occupied-turn-002-evidence.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    assert not multicase._zero_call_correction_recovery_available(
        case_dir
    )
