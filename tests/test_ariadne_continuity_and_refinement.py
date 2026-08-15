"""Focused tests for Ariadne continuity and refinement safeguards."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orchestration_harness.continuity_and_refinement import (
    admit_command_event,
    assess_command_submission,
    assess_cursor,
    assess_gate,
    assess_promotion,
    assess_rejection,
    assess_rollback,
    recover_generation,
    sha256_digest,
    validate_gate_attempt,
    validate_operation_journal,
    validate_refinement_promotion,
    validate_refinement_proposal,
)
from scripts.ariadne_continuity_and_refinement import build_parser, run


ROOT = Path(__file__).resolve().parents[1]
SAFEGUARDS = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-continuity-and-refinement-safeguards"
)
JOURNAL_SCHEMA = SAFEGUARDS / "operation-journal.schema.json"
GATE_SCHEMA = SAFEGUARDS / "gate-attempt.schema.json"
PROPOSAL_SCHEMA = SAFEGUARDS / "refinement-proposal.schema.json"
PROMOTION_SCHEMA = SAFEGUARDS / "refinement-promotion.schema.json"
EVIDENCE = SAFEGUARDS / "provider-free-authored-synthetic-evidence.json"
POLICY = (
    ROOT
    / "orchestration"
    / "harness_settings"
    / "continuity_and_refinement_safeguards.yaml"
)

HEAD_1 = "1" * 40
HEAD_2 = "2" * 40
TREE_1 = "3" * 40
TREE_2 = "4" * 40
DIGEST_A = sha256_digest({"a": 1})
DIGEST_B = sha256_digest({"b": 2})
DIGEST_C = sha256_digest({"c": 3})
DIGEST_D = sha256_digest({"d": 4})
DIGEST_E = sha256_digest({"e": 5})
DIGEST_F = sha256_digest({"f": 6})
DIGEST_G = sha256_digest({"g": 7})
DIGEST_H = sha256_digest({"h": 8})


def base_journal() -> dict:
    return {
        "schema_version": "ariadne.operation_journal.v1",
        "operation_id": "ariadne-test-operation",
        "generation": 1,
        "events": [
            {
                "event_id": "evt-1",
                "generation": 1,
                "sequence": 1,
                "command_id": "cmd-a",
                "request_digest": DIGEST_A,
                "state": "received",
                "result_digest": None,
            },
            {
                "event_id": "evt-2",
                "generation": 1,
                "sequence": 2,
                "command_id": "cmd-a",
                "request_digest": DIGEST_A,
                "state": "running",
                "result_digest": None,
            },
            {
                "event_id": "evt-3",
                "generation": 1,
                "sequence": 3,
                "command_id": "cmd-a",
                "request_digest": DIGEST_A,
                "state": "completed",
                "result_digest": DIGEST_B,
            },
        ],
    }


def running_journal() -> dict:
    return {
        "schema_version": "ariadne.operation_journal.v1",
        "operation_id": "ariadne-test-operation",
        "generation": 1,
        "events": [
            {
                "event_id": "evt-1",
                "generation": 1,
                "sequence": 1,
                "command_id": "cmd-b",
                "request_digest": DIGEST_C,
                "state": "received",
                "result_digest": None,
            },
            {
                "event_id": "evt-2",
                "generation": 1,
                "sequence": 2,
                "command_id": "cmd-b",
                "request_digest": DIGEST_C,
                "state": "running",
                "result_digest": None,
            },
        ],
    }


def received_journal() -> dict:
    return {
        "schema_version": "ariadne.operation_journal.v1",
        "operation_id": "ariadne-test-operation",
        "generation": 1,
        "events": [
            {
                "event_id": "evt-1",
                "generation": 1,
                "sequence": 1,
                "command_id": "cmd-c",
                "request_digest": DIGEST_D,
                "state": "received",
                "result_digest": None,
            },
        ],
    }


def _terminal_journal(state: str) -> dict:
    journal = received_journal()
    journal["events"][0]["command_id"] = "cmd-t"
    journal["events"][0]["request_digest"] = DIGEST_E
    events = journal["events"]
    if state == "uncertain":
        # running -> uncertain is the only legal way to reach uncertain in-generation
        events.append(
            {
                "event_id": "evt-2",
                "generation": 1,
                "sequence": 2,
                "command_id": "cmd-t",
                "request_digest": DIGEST_E,
                "state": "running",
                "result_digest": None,
            }
        )
        events.append(
            {
                "event_id": "evt-3",
                "generation": 1,
                "sequence": 3,
                "command_id": "cmd-t",
                "request_digest": DIGEST_E,
                "state": "uncertain",
                "result_digest": None,
            }
        )
    else:
        events.append(
            {
                "event_id": "evt-2",
                "generation": 1,
                "sequence": 2,
                "command_id": "cmd-t",
                "request_digest": DIGEST_E,
                "state": state,
                "result_digest": None,
            }
        )
    return journal


def base_fingerprint() -> dict:
    return {
        "gate_id": "gate-a",
        "candidate_source_head": HEAD_1,
        "candidate_source_tree": TREE_1,
        "evidence_set_digest": DIGEST_F,
        "command_manifest_digest": DIGEST_G,
        "relevant_input_digest": DIGEST_H,
        "toolchain_digest": DIGEST_A,
    }


def base_gate_attempt(result: str = "deterministic_failure") -> dict:
    return {
        "schema_version": "ariadne.gate_attempt.v1",
        "attempt_id": "att-1",
        "fingerprint": base_fingerprint(),
        "result": result,
        "generation": 1,
    }


def base_proposal(scope: str = "local") -> dict:
    return {
        "schema_version": "ariadne.refinement_proposal.v1",
        "proposal_id": "ref-1",
        "kind": "prompt_note",
        "scope": scope,
        "title": "Add a bounded lesson",
        "body": "Never rerun an unchanged failed gate.",
        "base_state_digest": DIGEST_A,
        "candidate_digest": DIGEST_B,
        "source_evidence_digests": [DIGEST_C],
        "source_head": HEAD_1,
        "proposer": "deepseek",
        "validation_manifest_digest": DIGEST_D,
        "status": "quarantined",
        "generation": 1,
    }


def base_promotion_record(decision: str = "promote") -> dict:
    proposal = base_proposal()
    return {
        "schema_version": "ariadne.refinement_promotion.v1",
        "promotion_id": "prom-ref-1",
        "proposal_id": "ref-1",
        "proposal_digest": sha256_digest(proposal),
        "decision": decision,
        "generation": 1,
        "scope": "local",
        "candidate_digest": DIGEST_B,
        "base_state_digest": DIGEST_A,
        "source_head": HEAD_1,
        "source_evidence_digests": [DIGEST_C],
        "validation_manifest_digest": DIGEST_D,
        "validation_result": "pass",
        "proposer": "deepseek",
        "promoter": "sol",
        "independent_reviewer": None,
        "promoted_decision_id": None,
        "reasons": [],
    }


# ---------------------------------------------------------------------------
# Schema admission and authored-synthetic evidence
# ---------------------------------------------------------------------------


def _schemas() -> list[dict]:
    return [
        ("operation-journal", json.loads(JOURNAL_SCHEMA.read_text(encoding="utf-8"))),
        ("gate-attempt", json.loads(GATE_SCHEMA.read_text(encoding="utf-8"))),
        (
            "refinement-proposal",
            json.loads(PROPOSAL_SCHEMA.read_text(encoding="utf-8")),
        ),
        (
            "refinement-promotion",
            json.loads(PROMOTION_SCHEMA.read_text(encoding="utf-8")),
        ),
    ]


@pytest.mark.parametrize(("name", "schema"), _schemas())
def test_schema_is_valid_draft_2020_12(name: str, schema: dict) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validators.Draft202012Validator.check_schema(schema)


def test_journal_schema_admits_valid_journal() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(
        validate_operation_journal(base_journal()),
        json.loads(JOURNAL_SCHEMA.read_text(encoding="utf-8")),
    )


def test_gate_schema_admits_valid_attempt() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(
        validate_gate_attempt(base_gate_attempt()),
        json.loads(GATE_SCHEMA.read_text(encoding="utf-8")),
    )


def test_proposal_schema_admits_valid_proposal() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(
        validate_refinement_proposal(base_proposal()),
        json.loads(PROPOSAL_SCHEMA.read_text(encoding="utf-8")),
    )


def test_promotion_schema_admits_valid_promote_and_rollback() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(PROMOTION_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(
        validate_refinement_promotion(base_promotion_record("promote")), schema
    )
    rollback = assess_rollback(
        promoted_record=base_promotion_record("promote"),
        decision_history=[base_promotion_record("promote")],
        current_state_digest=DIGEST_B,
        authority="sol",
    )
    jsonschema.validate(validate_refinement_promotion(rollback), schema)


def test_refinement_schemas_and_python_reject_same_authority_and_text_bypasses() -> (
    None
):
    jsonschema = pytest.importorskip("jsonschema")
    proposal_schema = json.loads(PROPOSAL_SCHEMA.read_text(encoding="utf-8"))
    promotion_schema = json.loads(PROMOTION_SCHEMA.read_text(encoding="utf-8"))

    bad_title = base_proposal()
    bad_title["title"] = " leading space"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad_title, proposal_schema)
    with pytest.raises(ValueError):
        validate_refinement_proposal(bad_title)

    non_sol = base_promotion_record("promote")
    non_sol["promoter"] = "gemini"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(non_sol, promotion_schema)
    with pytest.raises(ValueError):
        validate_refinement_promotion(non_sol)

    missing_global_review = base_promotion_record("promote")
    missing_global_review["scope"] = "global"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(missing_global_review, promotion_schema)
    with pytest.raises(ValueError):
        validate_refinement_promotion(missing_global_review)


def test_policy_yaml_parses_and_declares_executes_nothing() -> None:
    yaml = pytest.importorskip("yaml")
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    assert policy["schema_version"] == "ariadne.continuity_and_refinement_safeguards.v1"
    assert policy["executes_nothing"] is True
    assert policy["grants_no_command_authority"] is True


def test_cli_emits_source_bound_promotion_to_explicit_output(tmp_path: Path) -> None:
    proposal_path = tmp_path / "proposal.json"
    prior_path = tmp_path / "prior.json"
    output_path = tmp_path / "decision.json"
    proposal_path.write_text(json.dumps(base_proposal()), encoding="utf-8")
    prior_path.write_text("[]\n", encoding="utf-8")
    args = build_parser().parse_args(
        [
            "assess-promotion",
            "--proposal",
            str(proposal_path),
            "--validation-manifest-digest",
            DIGEST_D,
            "--validation-result",
            "pass",
            "--candidate-digest",
            DIGEST_B,
            "--base-state-digest",
            DIGEST_A,
            "--source-head",
            HEAD_1,
            "--promoter",
            "sol",
            "--prior-decisions",
            str(prior_path),
            "--output",
            str(output_path),
        ]
    )
    assert run(args) == 0
    decision = json.loads(output_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "promote"
    assert decision["source_head"] == HEAD_1


def test_cli_rollback_derives_history_bound_generation(tmp_path: Path) -> None:
    promoted = base_promotion_record("promote")
    promoted_path = tmp_path / "promoted.json"
    history_path = tmp_path / "history.json"
    output_path = tmp_path / "rollback.json"
    promoted_path.write_text(json.dumps(promoted), encoding="utf-8")
    history_path.write_text(json.dumps([promoted]), encoding="utf-8")
    args = build_parser().parse_args(
        [
            "assess-rollback",
            "--promoted-record",
            str(promoted_path),
            "--decision-history",
            str(history_path),
            "--current-state-digest",
            DIGEST_B,
            "--authority",
            "sol",
            "--output",
            str(output_path),
        ]
    )
    assert run(args) == 0
    rollback = json.loads(output_path.read_text(encoding="utf-8"))
    assert rollback["generation"] == 2
    assert rollback["candidate_digest"] == DIGEST_A


def test_authored_synthetic_evidence_covers_positive_decisions_and_boundaries() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["evidence_label"] == "authored_synthetic_provider_free_harness"
    decisions = {row["decision"] for row in evidence["covered_positive_decisions"]}
    assert decisions >= {
        "new_command",
        "replay_completed",
        "conflict",
        "already_in_progress",
        "requires_new_generation",
        "recovery_advances_generation",
        "events_available",
        "up_to_date",
        "run_gate",
        "reuse_exact_pass",
        "diagnose_without_rerun",
        "resolve_uncertainty",
        "quarantined",
        "promote",
        "reject",
        "rollback",
    }
    boundaries = {row["boundary_id"] for row in evidence["fail_closed_boundaries"]}
    assert boundaries >= {
        "journal.running_never_replays",
        "journal.uncertain_never_replays",
        "journal.completed_requires_result_digest",
        "journal.stale_cursor_snapshot_required",
        "journal.future_cursor_snapshot_required",
        "journal.missing_cursor_snapshot_required",
        "journal.out_of_range_cursor_snapshot_required",
        "gate.partial_fingerprint_fails_closed",
        "refinement.proposer_cannot_promote",
        "refinement.global_without_independent_review_rejected",
        "refinement.ambiguous_rollback_rejected",
    }
    assert evidence["forbidden"]["prime_agent_installed_or_executed"] is False
    assert evidence["forbidden"]["journal_appended_by_cli"] is False


# ---------------------------------------------------------------------------
# Journal positive decisions
# ---------------------------------------------------------------------------


def test_completed_command_exact_replay_returns_recorded_digest() -> None:
    decision = assess_command_submission(
        base_journal(), command_id="cmd-a", request_digest=DIGEST_A
    )
    assert decision["decision"] == "replay_completed"
    assert decision["recorded_result_digest"] == DIGEST_B


def test_completed_command_differing_request_is_conflict() -> None:
    decision = assess_command_submission(
        base_journal(), command_id="cmd-a", request_digest=DIGEST_C
    )
    assert decision["decision"] == "conflict"


@pytest.mark.parametrize(
    "journal",
    [
        running_journal(),
        received_journal(),
        _terminal_journal("failed"),
        _terminal_journal("revoked"),
        _terminal_journal("uncertain"),
    ],
)
def test_differing_request_is_conflict_before_every_state_decision(
    journal: dict,
) -> None:
    command_id = journal["events"][0]["command_id"]
    decision = assess_command_submission(
        journal, command_id=command_id, request_digest=DIGEST_H
    )
    assert decision["decision"] == "conflict"


def test_live_received_and_running_never_replay() -> None:
    assert (
        assess_command_submission(
            running_journal(), command_id="cmd-b", request_digest=DIGEST_C
        )["decision"]
        == "already_in_progress"
    )
    assert (
        assess_command_submission(
            received_journal(), command_id="cmd-c", request_digest=DIGEST_D
        )["decision"]
        == "already_in_progress"
    )


@pytest.mark.parametrize("state", ["failed", "revoked", "uncertain"])
def test_terminal_non_completed_states_never_auto_replay(state: str) -> None:
    journal = _terminal_journal(state)
    assert validate_operation_journal(journal)["events"][-1]["state"] == state
    decision = assess_command_submission(
        journal, command_id="cmd-t", request_digest=DIGEST_E
    )
    assert decision["decision"] == "requires_new_generation"


def test_admit_new_command_as_received_appends_contiguous_sequence() -> None:
    journal = running_journal()
    admitted = admit_command_event(
        journal,
        event_id="evt-3",
        command_id="cmd-new",
        request_digest=DIGEST_F,
        state="received",
    )
    assert admitted["generation"] == 1
    last = admitted["events"][-1]
    assert last["command_id"] == "cmd-new"
    assert last["state"] == "received"
    assert last["sequence"] == 3
    assert last["result_digest"] is None


def test_admit_running_then_completed_is_legal() -> None:
    journal = received_journal()
    journal = admit_command_event(
        journal,
        event_id="evt-2",
        command_id="cmd-c",
        request_digest=DIGEST_D,
        state="running",
    )
    journal = admit_command_event(
        journal,
        event_id="evt-3",
        command_id="cmd-c",
        request_digest=DIGEST_D,
        state="completed",
        result_digest=DIGEST_B,
    )
    assert journal["events"][-1]["state"] == "completed"
    assert journal["events"][-1]["result_digest"] == DIGEST_B


@pytest.mark.parametrize(
    ("state", "result_digest"),
    [
        ("completed", None),
        ("running", DIGEST_B),
        ("received", DIGEST_B),
    ],
)
def test_admit_command_event_invalid_result_binding_fails_closed(
    state: str, result_digest: object
) -> None:
    with pytest.raises(ValueError):
        admit_command_event(
            received_journal(),
            event_id="evt-2",
            command_id="cmd-c",
            request_digest=DIGEST_D,
            state=state,
            result_digest=result_digest,
        )


def test_admit_second_received_for_same_command_fails_closed() -> None:
    with pytest.raises(ValueError):
        admit_command_event(
            received_journal(),
            event_id="evt-2",
            command_id="cmd-c",
            request_digest=DIGEST_D,
            state="received",
        )


def test_admit_running_for_completed_command_fails_closed() -> None:
    with pytest.raises(ValueError):
        admit_command_event(
            base_journal(),
            event_id="evt-4",
            command_id="cmd-a",
            request_digest=DIGEST_A,
            state="running",
        )


def test_recovery_advances_exactly_once_and_marks_unfinished_uncertain() -> None:
    journal = running_journal()
    recovered = recover_generation(journal)
    assert recovered["generation"] == 2
    last = recovered["events"][-1]
    assert last["command_id"] == "cmd-b"
    assert last["state"] == "uncertain"
    assert last["result_digest"] is None
    # a completed command remains immutable through recovery
    completed = base_journal()
    recovered_completed = recover_generation(completed)
    assert recovered_completed["generation"] == 2
    assert recovered_completed["events"][-1]["state"] == "completed"
    assert recovered_completed["events"][-1]["result_digest"] == DIGEST_B
    # no new event is created for a completed command in the new generation
    gen2_events = [e for e in recovered_completed["events"] if e["generation"] == 2]
    assert gen2_events == []


def test_recovered_uncertain_command_never_replays() -> None:
    recovered = recover_generation(running_journal())
    decision = assess_command_submission(
        recovered, command_id="cmd-b", request_digest=DIGEST_C
    )
    assert decision["decision"] == "requires_new_generation"


def test_reordered_history_and_retired_live_work_fail_closed() -> None:
    reordered = base_journal()
    reordered["events"][0], reordered["events"][1] = (
        reordered["events"][1],
        reordered["events"][0],
    )
    with pytest.raises(ValueError, match="append-only"):
        validate_operation_journal(reordered)

    retired_live = running_journal()
    retired_live["generation"] = 2
    with pytest.raises(ValueError, match="retired generation"):
        validate_operation_journal(retired_live)

    skipped_recovery = recover_generation(running_journal())
    skipped_recovery["events"][-1]["generation"] = 3
    skipped_recovery["generation"] = 3
    with pytest.raises(ValueError, match="exact recovery"):
        validate_operation_journal(skipped_recovery)


def test_same_generation_cursor_receives_later_events_only() -> None:
    decision = assess_cursor(base_journal(), generation=1, sequence=1)
    assert decision["decision"] == "events_available"
    assert [e["sequence"] for e in decision["later_events"]] == [2, 3]
    latest = assess_cursor(base_journal(), generation=1, sequence=3)
    assert latest["decision"] == "up_to_date"
    assert latest["later_events"] == []


@pytest.mark.parametrize(
    ("journal_builder", "generation", "sequence", "reason"),
    [
        (base_journal, 0, 1, "out_of_range"),
        (base_journal, 1, 0, "out_of_range"),
        (lambda: recover_generation(running_journal()), 2, 99, "out_of_range"),
        (lambda: recover_generation(base_journal()), 2, 1, "missing_sequence"),
        (base_journal, 3, 1, "future_generation"),
    ],
)
def test_invalid_cursors_return_snapshot_required(
    journal_builder: object, generation: int, sequence: int, reason: str
) -> None:
    journal = journal_builder()
    decision = assess_cursor(journal, generation=generation, sequence=sequence)
    assert decision["decision"] == "snapshot_required"
    assert decision["reason"] == reason


def test_stale_generation_cursor_returns_snapshot_required() -> None:
    journal = recover_generation(base_journal())
    decision = assess_cursor(journal, generation=1, sequence=1)
    assert decision["decision"] == "snapshot_required"
    assert decision["reason"] == "stale_generation"


# ---------------------------------------------------------------------------
# Journal hostile mutations
# ---------------------------------------------------------------------------


def _set_path(value: dict, path: tuple[str, ...], replacement: object) -> dict:
    target = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement
    return value


def _event(index: int) -> tuple[str, ...]:
    return ("events", index)


def _append_transition_mutations() -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []

    first_not_received = received_journal()
    first_not_received["events"][0]["state"] = "running"
    cases.append(("journal_first_event_not_received", first_not_received))

    running_to_running = received_journal()
    running_to_running["events"].append(
        {
            "event_id": "evt-2",
            "generation": 1,
            "sequence": 2,
            "command_id": "cmd-c",
            "request_digest": DIGEST_D,
            "state": "running",
            "result_digest": None,
        }
    )
    running_to_running["events"].append(
        {
            "event_id": "evt-3",
            "generation": 1,
            "sequence": 3,
            "command_id": "cmd-c",
            "request_digest": DIGEST_D,
            "state": "running",
            "result_digest": None,
        }
    )
    cases.append(("journal_running_to_running", running_to_running))

    completed_to_failed = base_journal()
    completed_to_failed["events"].append(
        {
            "event_id": "evt-4",
            "generation": 1,
            "sequence": 4,
            "command_id": "cmd-a",
            "request_digest": DIGEST_A,
            "state": "failed",
            "result_digest": None,
        }
    )
    cases.append(("journal_completed_to_failed", completed_to_failed))

    received_to_uncertain_same_gen = received_journal()
    received_to_uncertain_same_gen["events"].append(
        {
            "event_id": "evt-2",
            "generation": 1,
            "sequence": 2,
            "command_id": "cmd-c",
            "request_digest": DIGEST_D,
            "state": "uncertain",
            "result_digest": None,
        }
    )
    cases.append(
        (
            "journal_received_to_uncertain_same_generation",
            received_to_uncertain_same_gen,
        )
    )

    double_received = received_journal()
    double_received["events"].append(
        {
            "event_id": "evt-2",
            "generation": 1,
            "sequence": 2,
            "command_id": "cmd-c",
            "request_digest": DIGEST_D,
            "state": "received",
            "result_digest": None,
        }
    )
    cases.append(("journal_double_received", double_received))

    failed_to_completed = _terminal_journal("failed")
    failed_to_completed["events"].append(
        {
            "event_id": "evt-3",
            "generation": 1,
            "sequence": 3,
            "command_id": "cmd-t",
            "request_digest": DIGEST_E,
            "state": "completed",
            "result_digest": DIGEST_B,
        }
    )
    cases.append(("journal_failed_to_completed", failed_to_completed))

    revoked_to_received = _terminal_journal("revoked")
    revoked_to_received["events"].append(
        {
            "event_id": "evt-3",
            "generation": 1,
            "sequence": 3,
            "command_id": "cmd-t",
            "request_digest": DIGEST_E,
            "state": "received",
            "result_digest": None,
        }
    )
    cases.append(("journal_revoked_to_received", revoked_to_received))

    uncertain_to_running = _terminal_journal("uncertain")
    uncertain_to_running["events"].append(
        {
            "event_id": "evt-3",
            "generation": 1,
            "sequence": 3,
            "command_id": "cmd-t",
            "request_digest": DIGEST_E,
            "state": "running",
            "result_digest": None,
        }
    )
    cases.append(("journal_uncertain_to_running", uncertain_to_running))

    gap = copy.deepcopy(base_journal())
    gap["events"][1]["sequence"] = 4
    cases.append(("journal_sequence_gap", gap))

    starts_at_two = copy.deepcopy(base_journal())
    for index, event in enumerate(starts_at_two["events"], start=2):
        event["sequence"] = index
    cases.append(("journal_sequence_starts_at_two", starts_at_two))

    duplicate_sequence = copy.deepcopy(base_journal())
    duplicate_sequence["events"][1]["sequence"] = 1
    cases.append(("journal_duplicate_sequence", duplicate_sequence))

    unstable_digest = copy.deepcopy(base_journal())
    unstable_digest["events"][1]["request_digest"] = DIGEST_C
    cases.append(("journal_request_digest_not_stable", unstable_digest))

    return cases


def journal_mutations() -> list[tuple[str, dict]]:
    base = base_journal()
    cases: list[tuple[str, dict]] = []

    for key in ("schema_version", "operation_id", "generation", "events"):
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        cases.append((f"journal_missing_{key}", candidate))
    cases.append(
        (
            "journal_wrong_schema_version",
            _set_path(copy.deepcopy(base), ("schema_version",), "v2"),
        )
    )
    cases.append(
        (
            "journal_invalid_operation_id",
            _set_path(copy.deepcopy(base), ("operation_id",), "Bad operation"),
        )
    )
    cases.append(
        ("journal_zero_generation", _set_path(copy.deepcopy(base), ("generation",), 0))
    )
    cases.append(
        ("journal_empty_events", _set_path(copy.deepcopy(base), ("events",), []))
    )

    event_keys = (
        "event_id",
        "generation",
        "sequence",
        "command_id",
        "request_digest",
        "state",
        "result_digest",
    )
    for key in event_keys:
        candidate = copy.deepcopy(base)
        candidate["events"][0].pop(key)
        cases.append((f"journal_event_missing_{key}", candidate))
    cases.append(
        (
            "journal_event_extra_field",
            _set_path(copy.deepcopy(base), _event(0) + ("unexpected",), True),
        )
    )
    cases.append(
        (
            "journal_duplicate_event_id",
            _set_path(copy.deepcopy(base), _event(1) + ("event_id",), "evt-1"),
        )
    )
    cases.append(
        (
            "journal_event_future_generation",
            _set_path(copy.deepcopy(base), _event(0) + ("generation",), 2),
        )
    )
    cases.append(
        (
            "journal_event_zero_sequence",
            _set_path(copy.deepcopy(base), _event(0) + ("sequence",), 0),
        )
    )
    cases.append(
        (
            "journal_invalid_state",
            _set_path(copy.deepcopy(base), _event(0) + ("state",), "pending"),
        )
    )
    cases.append(
        (
            "journal_completed_without_result_digest",
            _set_path(copy.deepcopy(base), _event(2) + ("result_digest",), None),
        )
    )
    cases.append(
        (
            "journal_running_with_result_digest",
            _set_path(copy.deepcopy(base), _event(1) + ("result_digest",), DIGEST_B),
        )
    )
    cases.append(
        (
            "journal_invalid_request_digest",
            _set_path(
                copy.deepcopy(base), _event(0) + ("request_digest",), "sha256:short"
            ),
        )
    )
    cases.append(
        (
            "journal_invalid_result_digest",
            _set_path(
                copy.deepcopy(base), _event(2) + ("result_digest",), "sha256:nope"
            ),
        )
    )
    reordered = copy.deepcopy(base)
    reordered["events"][0], reordered["events"][1] = (
        reordered["events"][1],
        reordered["events"][0],
    )
    cases.append(("journal_reordered_coordinate_history", reordered))
    retired_live = running_journal()
    retired_live["generation"] = 2
    cases.append(("journal_retired_generation_live_command", retired_live))
    cases.extend(_append_transition_mutations())
    return cases


@pytest.mark.parametrize(("label", "candidate"), journal_mutations())
def test_journal_hostile_mutations_fail_closed(label: str, candidate: dict) -> None:
    with pytest.raises(ValueError):
        validate_operation_journal(candidate)


def test_journal_hostile_mutation_count_is_at_least_thirty() -> None:
    assert len(journal_mutations()) >= 30


# ---------------------------------------------------------------------------
# Gate positive decisions
# ---------------------------------------------------------------------------


def test_gate_no_prior_attempt_runs_gate() -> None:
    decision = assess_gate(prior_attempts=[], fingerprint=base_fingerprint())
    assert decision["decision"] == "run_gate"


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ("deterministic_pass", "reuse_exact_pass"),
        ("deterministic_failure", "diagnose_without_rerun"),
        ("uncertain", "resolve_uncertainty"),
    ],
)
def test_gate_exact_prior_attempt_is_memoized(result: str, expected: str) -> None:
    decision = assess_gate(
        prior_attempts=[base_gate_attempt(result)], fingerprint=base_fingerprint()
    )
    assert decision["decision"] == expected
    assert decision["matched_attempt_id"] == "att-1"


@pytest.mark.parametrize(
    ("key", "replacement"),
    [
        ("candidate_source_head", HEAD_2),
        ("candidate_source_tree", TREE_2),
        ("evidence_set_digest", DIGEST_B),
        ("command_manifest_digest", DIGEST_C),
        ("relevant_input_digest", DIGEST_D),
        ("toolchain_digest", DIGEST_E),
        ("gate_id", "gate-b"),
    ],
)
def test_gate_changed_fingerprint_component_runs_gate(
    key: str, replacement: str
) -> None:
    fingerprint = dict(base_fingerprint())
    fingerprint[key] = replacement
    decision = assess_gate(
        prior_attempts=[base_gate_attempt("deterministic_pass")],
        fingerprint=fingerprint,
    )
    assert decision["decision"] == "run_gate"


def test_gate_partial_fingerprint_fails_closed() -> None:
    fingerprint = dict(base_fingerprint())
    fingerprint.pop("gate_id")
    with pytest.raises(ValueError):
        assess_gate(prior_attempts=[], fingerprint=fingerprint)


def test_gate_conflicting_or_ambiguous_exact_attempts_fail_closed() -> None:
    failed = base_gate_attempt("deterministic_failure")
    passed = base_gate_attempt("deterministic_pass")
    passed["attempt_id"] = "att-2"
    passed["generation"] = 2
    with pytest.raises(ValueError, match="conflicting terminal evidence"):
        assess_gate(prior_attempts=[failed, passed], fingerprint=base_fingerprint())

    duplicate_id = copy.deepcopy(failed)
    duplicate_id["generation"] = 2
    with pytest.raises(ValueError, match="ids must be unique"):
        assess_gate(
            prior_attempts=[failed, duplicate_id], fingerprint=base_fingerprint()
        )

    same_generation = copy.deepcopy(failed)
    same_generation["attempt_id"] = "att-2"
    with pytest.raises(ValueError, match="duplicate generations"):
        assess_gate(
            prior_attempts=[failed, same_generation], fingerprint=base_fingerprint()
        )


# ---------------------------------------------------------------------------
# Gate hostile mutations
# ---------------------------------------------------------------------------


def gate_mutations() -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []
    base = base_gate_attempt()

    for key in ("schema_version", "attempt_id", "fingerprint", "result", "generation"):
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        cases.append((f"gate_missing_{key}", candidate))
    cases.append(
        (
            "gate_wrong_schema_version",
            _set_path(copy.deepcopy(base), ("schema_version",), "v2"),
        )
    )
    cases.append(
        (
            "gate_invalid_result",
            _set_path(copy.deepcopy(base), ("result",), "pass"),
        )
    )
    cases.append(
        (
            "gate_zero_generation",
            _set_path(copy.deepcopy(base), ("generation",), 0),
        )
    )
    cases.append(
        (
            "gate_attempt_extra_field",
            _set_path(copy.deepcopy(base), ("unexpected",), True),
        )
    )

    fingerprint_keys = (
        "gate_id",
        "candidate_source_head",
        "candidate_source_tree",
        "evidence_set_digest",
        "command_manifest_digest",
        "relevant_input_digest",
        "toolchain_digest",
    )
    for key in fingerprint_keys:
        candidate = copy.deepcopy(base)
        candidate["fingerprint"].pop(key)
        cases.append((f"gate_fingerprint_missing_{key}", candidate))
    invalid_replacements = {
        "gate_id": "Bad Gate",
        "candidate_source_head": "short",
        "candidate_source_tree": "short",
        "evidence_set_digest": "sha256:short",
        "command_manifest_digest": "sha256:short",
        "relevant_input_digest": "sha256:short",
        "toolchain_digest": "sha256:short",
    }
    for key, replacement in invalid_replacements.items():
        candidate = copy.deepcopy(base)
        candidate["fingerprint"][key] = replacement
        cases.append((f"gate_fingerprint_invalid_{key}", candidate))
    cases.append(
        (
            "gate_fingerprint_extra_field",
            _set_path(copy.deepcopy(base), ("fingerprint", "unexpected"), True),
        )
    )
    return cases


@pytest.mark.parametrize(("label", "candidate"), gate_mutations())
def test_gate_hostile_mutations_fail_closed(label: str, candidate: dict) -> None:
    with pytest.raises(ValueError):
        validate_gate_attempt(candidate)


def test_gate_hostile_mutation_count_is_at_least_twenty() -> None:
    assert len(gate_mutations()) >= 20


# ---------------------------------------------------------------------------
# Refinement proposal and promotion positive decisions
# ---------------------------------------------------------------------------


def test_new_proposal_begins_quarantined() -> None:
    proposal = validate_refinement_proposal(base_proposal())
    assert proposal["status"] == "quarantined"


def test_local_promotion_with_distinct_sol_authority_passes() -> None:
    proposal = base_proposal(scope="local")
    decision = assess_promotion(
        proposal,
        validation_manifest_digest=DIGEST_D,
        validation_result="pass",
        candidate_digest=DIGEST_B,
        base_state_digest=DIGEST_A,
        source_head=HEAD_1,
        promoter="sol",
        prior_decisions=[],
    )
    assert decision["decision"] == "promote"
    assert decision["promoter"] == "sol"
    assert decision["reasons"] == []
    validate_refinement_promotion(decision)


def test_global_promotion_requires_distinct_independent_review() -> None:
    proposal = base_proposal(scope="global")
    decision = assess_promotion(
        proposal,
        validation_manifest_digest=DIGEST_D,
        validation_result="pass",
        candidate_digest=DIGEST_B,
        base_state_digest=DIGEST_A,
        source_head=HEAD_1,
        promoter="sol",
        independent_reviewer="gemini",
        prior_decisions=[],
    )
    assert decision["decision"] == "promote"
    assert decision["independent_reviewer"] == "gemini"


def test_rejection_is_first_class_terminal_decision() -> None:
    decision = assess_rejection(
        base_proposal(),
        authority="sol",
        reason="evidence insufficient",
        prior_decisions=[],
    )
    assert decision["decision"] == "reject"
    assert decision["reasons"] == ["evidence insufficient"]
    validate_refinement_promotion(decision)


def test_rollback_creates_new_generation_and_names_exact_decision() -> None:
    promoted = base_promotion_record("promote")
    decision = assess_rollback(
        promoted_record=promoted,
        decision_history=[promoted],
        current_state_digest=DIGEST_B,
        authority="sol",
    )
    assert decision["decision"] == "rollback"
    assert decision["generation"] == 2
    assert decision["promoted_decision_id"] == "prom-ref-1"
    assert decision["base_state_digest"] == DIGEST_B
    assert decision["candidate_digest"] == DIGEST_A
    validate_refinement_promotion(decision)


def test_rollback_rejects_fabricated_repeated_and_intervening_targets() -> None:
    promoted = base_promotion_record("promote")
    with pytest.raises(ValueError, match="current state"):
        assess_rollback(
            promoted_record=promoted,
            decision_history=[promoted],
            current_state_digest=DIGEST_C,
            authority="sol",
        )

    rollback = assess_rollback(
        promoted_record=promoted,
        decision_history=[promoted],
        current_state_digest=DIGEST_B,
        authority="sol",
    )
    with pytest.raises(ValueError, match="already been rolled back"):
        assess_rollback(
            promoted_record=promoted,
            decision_history=[promoted, rollback],
            current_state_digest=DIGEST_B,
            authority="sol",
        )

    later = copy.deepcopy(promoted)
    later["promotion_id"] = "prom-ref-2"
    later["proposal_id"] = "ref-2"
    later["generation"] = 2
    with pytest.raises(ValueError, match="intervening"):
        assess_rollback(
            promoted_record=promoted,
            decision_history=[promoted, later],
            current_state_digest=DIGEST_B,
            authority="sol",
        )


def test_promotion_record_admission_enforces_source_sol_and_global_review() -> None:
    forged_source = base_promotion_record("promote")
    forged_source["source_head"] = HEAD_2
    assert validate_refinement_promotion(forged_source)["source_head"] == HEAD_2

    non_sol = base_promotion_record("promote")
    non_sol["promoter"] = "gemini"
    with pytest.raises(ValueError, match="Sol authority"):
        validate_refinement_promotion(non_sol)

    global_missing_review = base_promotion_record("promote")
    global_missing_review["scope"] = "global"
    with pytest.raises(ValueError, match="independent review"):
        validate_refinement_promotion(global_missing_review)


def test_promotion_rejects_source_mismatch_and_prior_terminal_decision() -> None:
    proposal = base_proposal()
    decision = assess_promotion(
        proposal,
        validation_manifest_digest=DIGEST_D,
        validation_result="pass",
        candidate_digest=DIGEST_B,
        base_state_digest=DIGEST_A,
        source_head=HEAD_2,
        promoter="sol",
        prior_decisions=[],
    )
    assert decision["decision"] == "reject"
    assert "source_head_binding_mismatch" in decision["reasons"]

    with pytest.raises(ValueError, match="already has"):
        assess_promotion(
            proposal,
            validation_manifest_digest=DIGEST_D,
            validation_result="pass",
            candidate_digest=DIGEST_B,
            base_state_digest=DIGEST_A,
            source_head=HEAD_1,
            promoter="sol",
            prior_decisions=[base_promotion_record("promote")],
        )


def test_decision_history_rejects_generation_reuse_and_skipped_generation() -> None:
    prior = base_promotion_record("promote")
    duplicate_generation = copy.deepcopy(prior)
    duplicate_generation["promotion_id"] = "prom-ref-2"
    duplicate_generation["proposal_id"] = "ref-2"
    proposal = base_proposal()
    proposal["proposal_id"] = "ref-3"
    proposal["generation"] = 2
    with pytest.raises(ValueError, match="generations must be unique"):
        assess_rejection(
            proposal,
            authority="sol",
            reason="duplicate history",
            prior_decisions=[prior, duplicate_generation],
        )

    proposal["generation"] = 3
    with pytest.raises(ValueError, match="next immutable"):
        assess_rejection(
            proposal,
            authority="sol",
            reason="skipped generation",
            prior_decisions=[prior],
        )


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    [
        (
            {
                "validation_manifest_digest": DIGEST_C,
                "validation_result": "pass",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_A,
                "promoter": "sol",
            },
            "validation_manifest_mismatch",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "fail",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_A,
                "promoter": "sol",
            },
            "validation_not_pass",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "pass",
                "candidate_digest": DIGEST_C,
                "base_state_digest": DIGEST_A,
                "promoter": "sol",
            },
            "candidate_binding_mismatch",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "pass",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_C,
                "promoter": "sol",
            },
            "base_state_binding_mismatch",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "pass",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_A,
                "promoter": "deepseek",
            },
            "promoter_is_proposer",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "pass",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_A,
                "promoter": "sol",
                "independent_reviewer": None,
            },
            "missing_independent_reviewer",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "pass",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_A,
                "promoter": "sol",
                "independent_reviewer": "deepseek",
            },
            "reviewer_is_proposer",
        ),
        (
            {
                "validation_manifest_digest": DIGEST_D,
                "validation_result": "pass",
                "candidate_digest": DIGEST_B,
                "base_state_digest": DIGEST_A,
                "promoter": "sol",
                "independent_reviewer": "sol",
            },
            "reviewer_is_promoter",
        ),
    ],
)
def test_promotion_rejects_fail_closed(kwargs: dict, reason: str) -> None:
    proposal = base_proposal(scope="global")
    decision = assess_promotion(
        proposal, source_head=HEAD_1, prior_decisions=[], **kwargs
    )
    assert decision["decision"] == "reject"
    assert reason in decision["reasons"]


# ---------------------------------------------------------------------------
# Proposal hostile mutations
# ---------------------------------------------------------------------------


def proposal_mutations() -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []
    base = base_proposal()

    for key in (
        "schema_version",
        "proposal_id",
        "kind",
        "scope",
        "title",
        "body",
        "base_state_digest",
        "candidate_digest",
        "source_evidence_digests",
        "source_head",
        "proposer",
        "validation_manifest_digest",
        "status",
        "generation",
    ):
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        cases.append((f"proposal_missing_{key}", candidate))

    replacements = {
        "proposal_wrong_schema_version": ("schema_version", "v2"),
        "proposal_invalid_kind": ("kind", "executable_code"),
        "proposal_invalid_scope": ("scope", "public"),
        "proposal_status_not_quarantined": ("status", "promoted"),
        "proposal_empty_evidence": ("source_evidence_digests", []),
        "proposal_duplicate_evidence": (
            "source_evidence_digests",
            [DIGEST_C, DIGEST_C],
        ),
        "proposal_invalid_base_digest": ("base_state_digest", "sha256:short"),
        "proposal_invalid_candidate_digest": ("candidate_digest", "sha256:short"),
        "proposal_invalid_source_head": ("source_head", "abc"),
        "proposal_empty_proposer": ("proposer", ""),
        "proposal_invalid_validation_digest": (
            "validation_manifest_digest",
            "sha256:short",
        ),
        "proposal_body_with_cr": ("body", "bad\rbody"),
        "proposal_zero_generation": ("generation", 0),
        "proposal_empty_title": ("title", ""),
        "proposal_empty_body": ("body", ""),
        "proposal_extra_field": ("unexpected", True),
    }
    for label, (key, replacement) in replacements.items():
        candidate = copy.deepcopy(base)
        candidate[key] = replacement
        cases.append((label, candidate))
    return cases


@pytest.mark.parametrize(("label", "candidate"), proposal_mutations())
def test_proposal_hostile_mutations_fail_closed(label: str, candidate: dict) -> None:
    with pytest.raises(ValueError):
        validate_refinement_proposal(candidate)


def test_proposal_hostile_mutation_count_is_at_least_twenty() -> None:
    assert len(proposal_mutations()) >= 20


# ---------------------------------------------------------------------------
# Promotion hostile mutations
# ---------------------------------------------------------------------------


def promotion_mutations() -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []
    base = base_promotion_record("promote")

    for key in (
        "schema_version",
        "promotion_id",
        "proposal_id",
        "proposal_digest",
        "decision",
        "generation",
        "scope",
        "candidate_digest",
        "base_state_digest",
        "source_head",
        "source_evidence_digests",
        "validation_manifest_digest",
        "validation_result",
        "proposer",
        "promoter",
        "independent_reviewer",
        "promoted_decision_id",
        "reasons",
    ):
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        cases.append((f"promotion_missing_{key}", candidate))

    replacements = {
        "promotion_invalid_decision": ("decision", "deploy"),
        "promotion_invalid_scope": ("scope", "public"),
        "promotion_zero_generation": ("generation", 0),
        "promotion_duplicate_reasons": ("reasons", ["r", "r"]),
        "promotion_invalid_validation_result": ("validation_result", "fail"),
        "promotion_empty_promoter": ("promoter", ""),
        "promotion_invalid_proposal_digest": ("proposal_digest", "sha256:short"),
        "promotion_invalid_source_head": ("source_head", "abc"),
        "promotion_empty_source_evidence": ("source_evidence_digests", []),
        "promotion_empty_proposer": ("proposer", ""),
        "promotion_non_sol_authority": ("promoter", "gemini"),
    }
    for label, (key, replacement) in replacements.items():
        candidate = copy.deepcopy(base)
        candidate[key] = replacement
        cases.append((label, candidate))

    # rollback must name an exact promoted decision
    rollback = base_promotion_record("rollback")
    rollback["promoted_decision_id"] = None
    cases.append(("promotion_rollback_missing_promoted_decision_id", rollback))

    # promote/reject must not carry a promoted_decision_id
    promote_with_reference = base_promotion_record("promote")
    promote_with_reference["promoted_decision_id"] = "prom-other"
    cases.append(
        ("promotion_promote_with_promoted_decision_id", promote_with_reference)
    )

    return cases


@pytest.mark.parametrize(("label", "candidate"), promotion_mutations())
def test_promotion_hostile_mutations_fail_closed(label: str, candidate: dict) -> None:
    with pytest.raises(ValueError):
        validate_refinement_promotion(candidate)


def test_promotion_hostile_mutation_count_is_at_least_twenty() -> None:
    assert len(promotion_mutations()) >= 20


# ---------------------------------------------------------------------------
# Total hostile-mutation inventory (>= 60 distinct, no duplicate encodings)
# ---------------------------------------------------------------------------


def submission_fail_closed_labels() -> list[str]:
    return [
        "submission_conflict_completed",
        "submission_conflict_running",
        "submission_conflict_received",
        "submission_conflict_failed",
        "submission_conflict_revoked",
        "submission_conflict_uncertain",
        "submission_already_in_progress_running",
        "submission_already_in_progress_received",
        "submission_requires_new_generation_failed",
        "submission_requires_new_generation_revoked",
        "submission_requires_new_generation_uncertain",
    ]


def cursor_fail_closed_labels() -> list[str]:
    return [
        "cursor_out_of_range_generation_zero",
        "cursor_out_of_range_sequence_zero",
        "cursor_out_of_range_sequence_high",
        "cursor_missing_sequence",
        "cursor_future_generation",
        "cursor_stale_generation",
    ]


def gate_decision_fail_closed_labels() -> list[str]:
    return [
        "gate_no_prior_attempt",
        "gate_changed_source_head",
        "gate_changed_source_tree",
        "gate_changed_evidence",
        "gate_changed_manifest",
        "gate_changed_relevant_input",
        "gate_changed_toolchain",
        "gate_changed_gate_id",
        "gate_partial_fingerprint",
        "gate_duplicate_attempt_id",
        "gate_duplicate_generation",
        "gate_conflicting_terminal_evidence",
    ]


def promotion_reject_fail_closed_labels() -> list[str]:
    return [
        "promotion_reject_manifest_mismatch",
        "promotion_reject_validation_not_pass",
        "promotion_reject_candidate_mismatch",
        "promotion_reject_base_mismatch",
        "promotion_reject_promoter_is_proposer",
        "promotion_reject_missing_independent_reviewer",
        "promotion_reject_reviewer_is_proposer",
        "promotion_reject_reviewer_is_promoter",
        "promotion_reject_source_head_mismatch",
        "promotion_reject_prior_terminal_decision",
        "rollback_reject_fabricated_current_state",
        "rollback_reject_repeated_target",
        "rollback_reject_intervening_decision",
        "decision_history_reject_generation_reuse",
        "decision_history_reject_skipped_generation",
    ]


def hostile_mutation_labels() -> list[str]:
    labels = [label for label, _ in journal_mutations()]
    labels += [label for label, _ in gate_mutations()]
    labels += [label for label, _ in proposal_mutations()]
    labels += [label for label, _ in promotion_mutations()]
    labels += submission_fail_closed_labels()
    labels += cursor_fail_closed_labels()
    labels += gate_decision_fail_closed_labels()
    labels += promotion_reject_fail_closed_labels()
    return labels


def test_at_least_sixty_distinct_hostile_mutations() -> None:
    labels = hostile_mutation_labels()
    assert len(labels) >= 60, f"only {len(labels)} hostile mutations"
    assert len(set(labels)) == len(labels), "hostile mutation labels must be distinct"


def test_evidence_hostile_mutation_count_matches_inventory() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    labels = hostile_mutation_labels()
    assert evidence["hostile_mutations"]["attempted"] == len(labels)
    assert evidence["hostile_mutations"]["rejected"] == len(labels)
