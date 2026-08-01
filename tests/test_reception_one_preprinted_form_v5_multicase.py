"""Focused tests for the frozen v5 multi-case evaluation."""

from __future__ import annotations

import copy
import json

import pytest

from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_audit as turn_audit
from scripts import reception_one_preprinted_form_v5 as preprinted
from scripts import reception_one_preprinted_form_v5_live as preprinted_live
from scripts import reception_one_preprinted_form_v5_multicase as multicase


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_is_exact_frozen_six_case_descendant() -> None:
    manifest, cases = multicase.load_manifest()

    assert len(cases) == 6
    assert [case["case_code"] for case in cases] == [
        "create",
        "resize",
        "cancel",
        "status",
        "squeeze",
        "clarify",
    ]
    assert manifest["historical_anchor"]["case_id"] == "known-move"
    assert manifest["historical_anchor"]["replayed"] is False
    assert manifest["absolute_call_ceiling"] == 12
    assert manifest["incremental_cost_ceiling_usd"] == 1
    assert not any(manifest["frozen_condition"].values())
    assert manifest["provider_boundary"] == multicase.EXACT_PROVIDER_BOUNDARY


def test_all_provider_free_oracles_reach_expected_safe_typed_outcome() -> None:
    evidence = multicase.build_provider_blocked_evidence(
        write_frames=False
    )

    assert evidence["case_count"] == 6
    assert evidence["provider_calls_performed"] == 0
    assert evidence["credential_reads_performed"] == 0
    assert evidence["historical_anchor_replayed"] is False
    assert evidence["cross_case_ledger_pair_rejected"] is True
    assert {
        oracle["case_code"]: oracle["proofreader_disposition"]
        for oracle in evidence["case_oracles"]
    } == {
        "create": "admit",
        "resize": "admit",
        "cancel": "admit",
        "status": "admit",
        "squeeze": "admit",
        "clarify": "admit",
    }
    clarify = evidence["case_oracles"][-1]
    assert clarify["expected_proposal_release"] is False
    assert clarify["expected_final_output"] == {
        "kind": "clarification",
        "proposal_family": "clarification",
        "api_spine_operation_id": None,
        "patient_ref": None,
        "practitioner_ref": None,
        "appointment_ref": None,
        "candidate_slot_ids": [],
        "duration_minutes": None,
        "status": None,
        "warning_codes": [],
        "requires_human_confirmation": False,
        "write_performed": False,
    }


def test_recorded_provider_blocked_evidence_is_fresh_and_bound() -> None:
    recorded = _json(multicase.PROVIDER_BLOCKED_PATH)
    expected = multicase.build_provider_blocked_evidence(
        write_frames=False
    )

    assert recorded == expected
    assert recorded["evidence_hash"] == multicase._content_hash(recorded)


@pytest.mark.parametrize(
    "case_code",
    ["create", "resize", "cancel", "status", "squeeze", "clarify"],
)
def test_each_case_has_two_exact_single_use_identifiers(
    case_code: str,
) -> None:
    attempts, ledgers = multicase._case_ids(case_code)

    assert len(attempts) == len(ledgers) == 2
    for attempt_id, ledger_id in zip(attempts, ledgers, strict=True):
        broker.validate_attempt_ledger_pair(attempt_id, ledger_id)


def test_case_and_ledger_cannot_be_crossed() -> None:
    create_attempts, _ = multicase._case_ids("create")
    _, resize_ledgers = multicase._case_ids("resize")

    with pytest.raises(
        broker.BrokerError, match="cell_request_binding_invalid"
    ):
        broker.validate_attempt_ledger_pair(
            create_attempts[0], resize_ledgers[0]
        )


def test_custom_dialogue_ids_stop_after_first_admission() -> None:
    attempts, ledgers = multicase._case_ids("status")
    turn = {
        "provider_call_count": 1,
        "attempt_id": attempts[0],
        "ledger_id": ledgers[0],
        "ledger": {"status": "consumed"},
        "exchange": {
            "release": {"kind": "proposal_candidate"},
            "correction_ticket": None,
        },
    }

    decision = preprinted_live.decide_sequence(
        [turn],
        attempt_ids=attempts,
        ledger_ids=ledgers,
    )

    assert decision == {
        "status": "admitted",
        "next_turn_code": None,
        "actual_provider_calls": 1,
        "terminal": True,
    }


def test_frozen_provider_request_has_no_tool_or_fallback_surface() -> None:
    _, cases = multicase.load_manifest()
    for case in cases:
        frame = multicase.frame_for_case(case)
        request = preprinted.build_vertex_request(
            preprinted.build_turn_input(frame)
        )

        assert request["generationConfig"]["temperature"] == 0
        assert request["generationConfig"]["thinkingConfig"] == {
            "thinkingBudget": 0
        }
        assert not {
            "tools",
            "toolConfig",
            "cachedContent",
            "grounding",
            "retrieval",
            "candidateCount",
        }.intersection(request)
        assert set(preprinted.vertex_response_schema()["properties"]) == {
            "operator_note",
            "goal_code",
            "steps",
        }


def test_manifest_refuses_historical_move_replay() -> None:
    manifest = _json(multicase.MANIFEST_PATH)
    changed = copy.deepcopy(manifest)
    changed["cases"][0]["case_code"] = "move"

    with pytest.raises(
        multicase.MulticaseError, match="evaluation_case_set_invalid"
    ):
        multicase._validate_manifest(changed)


def test_multicase_external_audit_recognises_preprinted_form() -> None:
    case_dir = multicase.ARTIFACT_DIR / "cases" / "create"
    audit = turn_audit.build_external_audit(
        case_dir / "occupied-turn-001-evidence.json",
        case_dir / "occupied-turn-001-audit.jsonl",
        multicase.ARTIFACT_DIR / "occupied-preflight-evidence.json",
    )

    assert audit["attempt_id"].endswith("-eval-create-turn-001")
    assert audit["preprinted_form"]["broker_judgement_repair"] is False
    assert audit["preprinted_form"]["raw_model_form_body_recorded"] is False
    assert audit["typed_program"]["explicit_source_form"]


def test_occupied_cohort_passes_with_one_isolated_correction() -> None:
    evidence = _json(multicase.OCCUPIED_PATH)

    assert (
        evidence["result"]
        == "reception_one_preprinted_form_v5_multicase_occupied_pass"
    )
    assert evidence["capability_threshold_passed"] is True
    assert evidence["total_actual_provider_calls"] == 7
    assert evidence["all_ledgers_consumed"] is True
    assert evidence["all_cleanup_passed"] is True
    assert [case["actual_provider_calls"] for case in evidence["cases"]] == [
        1,
        1,
        1,
        1,
        1,
        2,
    ]
    assert [
        case["release"]["proposal_family"] for case in evidence["cases"]
    ] == [
        "create",
        "resize",
        "cancel",
        "status_change",
        "squeeze_in_assessment",
        "clarification",
    ]
    assert all(
        case["release"]["write_performed"] is False
        for case in evidence["cases"]
    )
    clarification = evidence["cases"][-1]
    assert clarification["primary_violation_codes"] == [
        "operator_arity_invalid"
    ]
    assert clarification["correction_used"] is True
    assert clarification["final_proofreader_disposition"] == "admit"
    assert clarification["release"]["kind"] == "clarification"
    assert clarification["release"]["api_spine_operation_id"] is None
    assert evidence["training_disposition"] == {
        "decision": "diagnose_without_teaching",
        "all_six_primary_expected_safe": False,
        "repeated_correctable_error_clusters": {},
        "isolated_correctable_error_clusters": {
            "operator_arity_invalid": ["clarify"]
        },
        "provider_contract_errors_are_training_evidence": False,
    }


def test_every_occupied_turn_has_consumed_ledger_and_valid_audit() -> None:
    evidence = _json(multicase.OCCUPIED_PATH)
    observed = 0
    for case in evidence["cases"]:
        case_dir = multicase.ARTIFACT_DIR / "cases" / case["case_code"]
        for index in range(1, case["actual_provider_calls"] + 1):
            ledger = _json(
                case_dir / f"occupied-turn-{index:03d}-ledger.json"
            )
            audit = _json(
                case_dir
                / f"occupied-turn-{index:03d}-external-audit.json"
            )
            assert ledger["status"] == "consumed"
            assert ledger["provider_calls_consumed"] == 1
            assert audit["durable_hash_chain"]["valid"] is True
            assert audit["provider_outcome"]["http_status"] == 200
            assert (
                audit["endpoint_hostname"]
                == "australia-southeast1-aiplatform.googleapis.com"
            )
            assert audit["api_key_authentication_used"] is False
            assert (
                audit["preprinted_form"]["broker_judgement_repair"]
                is False
            )
            assert all(
                value
                for key, value in audit["cleanup"].items()
                if key != "daemon_wide_prune_performed"
            )
            observed += 1
    assert observed == 7
