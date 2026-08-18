from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_architecture import (
    BASE,
    CONTRACT_PATH,
    SCHEMA_PATH,
    build_evidence,
    canonical_gear_trace,
    load_json,
    run_hostile_mutations,
    validate_contract,
    validate_gear_trace,
    verify_source_bindings,
)


ROOT = Path(__file__).resolve().parents[1]


def test_normative_contract_and_schema_are_closed_and_valid() -> None:
    contract = load_json(CONTRACT_PATH)
    schema = load_json(SCHEMA_PATH)

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    validate_contract(contract)
    verify_source_bindings(contract)

    assert contract["caller_supplied_binding_fields"] == []
    assert len(contract["engine_owned_fields"]) == 15
    assert len(contract["acceptance_scenarios"]) == 48
    assert contract["work_order"]["occupied_enabled"] is False
    assert contract["projection_protocol"]["current_controls_retired"] is False


def test_only_read_and_private_shadow_generation_are_currently_admitted() -> None:
    contract = load_json(CONTRACT_PATH)

    assert contract["effect_classes"]["shadow_admitted"] == [
        "read_only",
        "shadow_generation_write",
    ]
    assert contract["effect_classes"]["represented"][2:] == [
        "candidate_workspace_write",
        "provider_request",
        "task_branch_git_write",
        "protected_ref_write",
        "product_runtime_effect",
    ]


@pytest.mark.parametrize("terminal", ["succeeded", "failed", "unknown_commit"])
def test_terminal_result_requires_ariadne_acknowledgement(terminal: str) -> None:
    trace = canonical_gear_trace(terminal=terminal)

    validate_gear_trace(trace)

    assert trace[-2]["event"] == terminal
    assert trace[-1]["event"] == "acknowledged"
    assert trace[-1]["terminal_result_sha256"] == trace[-2]["tick_sha256"]
    assert trace[-1]["writer"] == "ariadne"


@pytest.mark.parametrize(
    ("name", "mutator"),
    [
        ("stale_parent", lambda value: value[2].__setitem__("previous_tick_sha256", "sha256:" + "0" * 64)),
        ("sequence_gap", lambda value: value[2].__setitem__("sequence", 9)),
        ("concurrent_writer", lambda value: value[2].__setitem__("writer", "ariadne")),
        ("result_before_start", lambda value: value[2].__setitem__("event", "succeeded")),
        ("ack_before_terminal", lambda value: value[3].__setitem__("event", "acknowledged")),
        ("attempt_drift", lambda value: value[3].__setitem__("attempt_id", "attempt-foreign-002")),
        ("wrong_ack_digest", lambda value: value[4].__setitem__("terminal_result_sha256", "sha256:" + "0" * 64)),
        ("broker_ack", lambda value: value[4].__setitem__("writer", "deepseek_broker")),
    ],
)
def test_hostile_gear_traces_fail_closed(name: str, mutator: object) -> None:
    del name
    trace = canonical_gear_trace()
    mutator(trace)  # type: ignore[operator]

    with pytest.raises(ValueError):
        validate_gear_trace(trace)


def test_duplicate_terminal_and_post_acknowledgement_events_fail_closed() -> None:
    duplicate_terminal = canonical_gear_trace()
    duplicate_terminal.insert(4, copy.deepcopy(duplicate_terminal[3]))
    with pytest.raises(ValueError):
        validate_gear_trace(duplicate_terminal)

    post_acknowledgement = canonical_gear_trace()
    post_acknowledgement.append(copy.deepcopy(post_acknowledgement[-1]))
    with pytest.raises(ValueError):
        validate_gear_trace(post_acknowledgement)


def test_unknown_commit_is_no_success_readback_and_no_retry() -> None:
    lifecycle = load_json(CONTRACT_PATH)["attempt_lifecycle"]

    assert lifecycle["unknown_commit_releases_success"] is False
    assert lifecycle["unknown_commit_requires_readback"] is True
    assert lifecycle["unknown_commit_automatic_retry"] is False
    assert lifecycle["recovery_derives_new_attempt_ordinal"] is True


def test_profiles_presets_and_budget_boundary_remain_configuration_only() -> None:
    work_order = load_json(CONTRACT_PATH)["work_order"]

    assert work_order["profile_families"] == [
        "emr4-readonly-review",
        "emr4-bounded-worker",
        "emr4-provider-free",
    ]
    assert work_order["bounded_worker_tools"] == ["edit", "glob", "read"]
    assert work_order["automatic_retries"] == 0
    assert work_order["silent_fallbacks"] == 0
    assert work_order["financial_budget_mechanism_required"] is False
    assert work_order["financial_boundary"] == "yuri_prepaid_provider_balance"


def test_kernel_closeout_efficacy_baseline_is_exact() -> None:
    baseline = load_json(CONTRACT_PATH)["efficacy"]["kernel_closeout_baseline"]

    assert baseline == {
        "manual_binding_fields": None,
        "provider_retries": 1,
        "rejected_register_or_pre_verifier_drafts": 4,
        "failure_induced_closeout_or_transition_reruns": 4,
        "stale_mutable_latch_fixtures": 2,
        "uncaught_escapes": 0,
    }


def test_future_rehearsal_thresholds_measure_benefit_without_timing_claim() -> None:
    thresholds = load_json(CONTRACT_PATH)["efficacy"][
        "future_rehearsal_thresholds"
    ]

    assert thresholds["caller_supplied_derived_fields"] == 0
    assert thresholds["minimum_failure_induced_rerun_reduction_percent"] == 50
    assert thresholds["new_mutable_current_fixtures"] == 0
    assert thresholds["coverage_loss"] is False
    assert thresholds["partial_publications"] == 0
    assert thresholds["uncaught_escapes"] == 0
    assert thresholds["shared_engine_growth_reported"] is True
    assert thresholds["clean_run_overhead_reported"] is True
    assert thresholds["timing_acceptance_relevant"] is False


def test_256_independent_hostile_contract_mutations_have_zero_escape() -> None:
    result = run_hostile_mutations(load_json(CONTRACT_PATH), count=256)

    assert result == {"attempted": 256, "rejected": 256, "escaped": []}


def test_generated_evidence_is_current_and_has_zero_escape() -> None:
    expected = build_evidence()
    observed = json.loads(
        (BASE / "provider-free-architecture-evidence.json").read_text(
            encoding="utf-8"
        )
    )

    assert observed == expected
    assert observed["status"] == "passed"
    assert observed["uncaught_escapes"] == 0
    assert observed["source_bindings"] == {"expected": 10, "matched": 10}
    assert observed["acceptance_scenarios"]["passed"] == 48


def test_report_keeps_architecture_and_live_authority_distinct() -> None:
    report = (BASE / "architecture-report.md").read_text(encoding="utf-8")

    assert "48 passed" in report
    assert "256 rejected, 0 escaped" in report
    assert "caller-supplied binding fields: 0" in report
    assert "does not adopt a live clock" in report
    assert "call a provider" in report
    assert "move protected refs" in report


def test_architecture_artifacts_do_not_import_product_code() -> None:
    runner = (
        ROOT
        / "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_architecture.py"
    ).read_text(encoding="utf-8")

    assert "from app" not in runner
    assert "import app" not in runner
    assert "subprocess" not in runner
    assert "http" not in runner
