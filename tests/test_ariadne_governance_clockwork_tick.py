from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

from orchestration_harness.governance_clockwork_tick import (
    BLOCKED_INTENT_VERSION,
    CHECKPOINT_INTENT_VERSION,
    INCIDENT_CANDIDATE_STATES,
    INCIDENT_CAUSAL_CLAIM_LEVEL,
    INCIDENT_CORRECTION_STATUSES,
    INCIDENT_RECURRENCE,
    INCIDENT_RESOURCE,
    INCIDENT_ROLES,
    INCIDENT_SEVERITIES,
    INCIDENT_STAGES,
    INCIDENT_TRANSPORT,
    INCIDENT_TRANCHE,
    INCIDENT_WORKFLOW_DISPOSITIONS,
    HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_ACCESS_BOUNDARY,
    HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES,
    HISTORICAL_DIARY_ACCESS_BOUNDARY,
    HISTORICAL_DIARY_SUBGATE_BOUNDARIES,
    HISTORICAL_FIRST_USE_MATERIALISATION_ACCESS_BOUNDARY,
    HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES,
    LEGACY_FULL_DATA_DENIAL_BOUNDARY,
    REQUIRED_NEXT_BOUNDARIES,
    SEMANTIC_BATON_LABEL,
    SEMANTIC_BATON_SLOT,
    SEMANTIC_PROFILE,
    SEMANTIC_TICK_INTENT_VERSION,
    SEMANTIC_VERIFICATION_PROFILE,
    TICK_INCIDENT_INTENT_VERSION,
    TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY,
    TYPED_PRODUCT_DATA_DENIAL_BOUNDARY,
    USER_DECISION_INTENT_VERSION,
    CommittedClockworkTick,
    ClockworkTickRejection,
    PREDECESSOR_METADATA_NAMES,
    build_blocked_tick_generation,
    build_checkpoint_tick_generation,
    build_tick_generation,
    build_user_decision_tick_generation,
    expand_semantic_tick_intent,
    materialize_semantic_evidence_headers,
    publish_tick_generation,
    prospective_current_node_human_evidence_errors,
    rollback_tick_generation,
    semantic_scalar_leaf_count,
    validate_blocked_tick_intent,
    validate_checkpoint_tick_intent,
    validate_tick_intent,
    validate_tick_live_state,
    validate_user_decision_tick_intent,
    validate_next_operation_protected_boundaries,
    _validate_commands,
    _compact_rendered_baton,
    _load_baton_compaction_manifest,
)
from orchestration_harness.governance_live_adoption import (
    CANONICAL_KEYS,
    METADATA_NAMES,
    validate_contract,
    validate_live_state,
)
from scripts.ariadne_governance_clockwork_tick import (
    SemanticVerificationRejection,
    _command_result,
    _idempotent_transaction_facts,
    _is_exact_published_intent,
    _output_prefix,
    _prepared_transaction_facts,
    _prospective_rejection_result,
    _rollback_transaction_facts,
    _run_semantic_verification,
    _write_idempotent_readback,
    _write_outputs,
)
from scripts.ariadne_governance_clockwork_closeout import (
    POSTPUBLICATION_TESTS,
    CloseoutDriverRejection,
    build_stage_manifest,
    capture_tick_reading,
    derive_allowlist,
    resolve_full_head,
    resolve_repository_interpreter,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement/contract.json"
TOPIC = ROOT / "orchestration/continuity/raisa-provider-free-clockwork-governed-check-in-successor-resolution"
INTENT_PATH = TOPIC / "closeout-intent.json"
HISTORICAL_DIARY_SUBGATE_CONTRACT = ROOT / (
    "orchestration/continuity/raisa-local-only-historical-diary-snapshot-"
    "privacy-feasibility-review/real-access-subgate-contract.json"
)
HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_CONTRACT = ROOT / (
    "orchestration/continuity/raisa-provider-free-historical-derived-scenario-"
    "first-use-candidate-gate-evaluator-rehearsal/next-tranche-contract.json"
)
HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_CONTRACT = ROOT / (
    "orchestration/continuity/raisa-local-only-historical-derived-minimised-"
    "check-in-context-scenario-first-use-materialisation-rehearsal/"
    "next-tranche-contract.json"
)
DECISION_INTENT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-default-off-check-in-relay-free-"
    "unknown-response-transport-redesign/closeout-intent.json"
)
REPLAY_FIXTURE_SOURCE = "f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e"
BLOCKED_REPLAY_FIXTURE_SOURCE = "1f6009943fcc2e8478511b95c85bf50388e3a634"
CHECKPOINT_REPLAY_FIXTURE_SOURCE = "dcb5093a61f0365aeb2651e3bcfd87a36fe0c438"
REDESIGN_OPERATION_ID = (
    "raisa-provider-free-default-off-check-in-relay-free-unknown-response-"
    "transport-redesign"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _replay_intent(worktree: Path) -> dict:
    intent = _json(worktree / INTENT_PATH.relative_to(ROOT))
    evidence = intent["transaction_manifest"]["node"]["evidence"]
    fixture_paths = {
        "plans": "docs/clockwork-prospective-plan-fixture.md",
        "closeouts": "docs/clockwork-prospective-closeout-fixture.md",
        "acceptances": (
            "orchestration/agent_inbox/codex/"
            "clockwork-prospective-fixture-acceptance.md"
        ),
    }
    for category, relative in fixture_paths.items():
        (worktree / relative).write_text(
            "# Prospective clockwork fixture\n\n"
            "Date: 2026-08-19\n\n"
            "Timestamp: 2026-08-19T14:26:41+10:00 (Australia/Brisbane)\n",
            encoding="utf-8",
            newline="\n",
        )
        evidence[category] = [relative]
    compaction = _json(
        worktree
        / "docs/handover-ledgers/current-baton-acceptance-index.manifest.json"
    )
    active_labels = compaction["active_labels"]
    for rolling_label in (
        "Current DeepSeek native Harness acceptance",
        "DeepSeek native Harness authored-synthetic traceability micro-rehearsal acceptance",
    ):
        if rolling_label in active_labels:
            intent["baton_acceptance"]["label"] = rolling_label
            return intent
    raise AssertionError("replay fixture has no admitted native-Harness rolling label")


def _semantic_intent(worktree: Path) -> dict:
    latch = _json(
        worktree
        / "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    contract = _json(worktree / CONTRACT_PATH.relative_to(ROOT))
    graph = _json(worktree / contract["canonical_paths"]["continuity"])
    artifact_slug = "ariadne-clockwork-typed-semantic-builder"
    plan_path = f"docs/{artifact_slug}-plan.md"
    fixture_digest = hashlib.sha256(
        latch["operation_id"].encode("utf-8")
    ).hexdigest()[:16]
    fixture_successor = f"fixture-successor-{fixture_digest}"
    return {
        "schema_version": SEMANTIC_TICK_INTENT_VERSION,
        "profile": SEMANTIC_PROFILE,
        "artifact_slug": artifact_slug,
        "recorded_at": "2026-08-23T17:17:00.4614783+10:00",
        "closeout": {
            "operation_id": latch["operation_id"],
            "title": "Provider-free governance clockwork typed semantic closeout builder and command registry rehearsal",
            "builds_on": [
                graph["nodes"][-1]["id"]
            ],
            "authority_notes": [
                "Yuri requested an evidence-backed clockwork ergonomics improvement.",
                "GPT Sol owns the serial provider-free tooling rehearsal.",
                "No Harness, product, provider or protected surface opens.",
            ],
            "decisions": [
                {
                    "id": "compile-repository-known-closeout-fields",
                    "source": plan_path,
                    "summary": "Compile fixed governance mechanics from one closed semantic profile.",
                },
                {
                    "id": "materialize-one-shared-human-header-reading",
                    "source": plan_path,
                    "summary": "Derive every prospective human evidence header from one Brisbane timestamp.",
                },
                {
                    "id": "execute-one-closed-verification-profile",
                    "source": plan_path,
                    "summary": "Run exact repository-owned verification commands before semantic publication.",
                },
            ],
            "claim_scope": [
                "One provider-free tooling closeout compiles through the existing tick.",
                "Closed selectors replace caller-authored command, label and path shapes.",
                "One recorded timestamp derives every prospective human evidence header.",
                "Legacy v1 and v2 intent semantics remain unchanged.",
            ],
            "additional_receipts": [],
            "additional_artifacts": [],
            "unresolved_gates": [
                "Arbitrary semantic profiles and commands remain closed.",
                "Native useful-completion reliability remains unproved.",
                "Product, provider, deployment and protected refs remain closed.",
            ],
            "journey": {
                "strategic_role": "Move repository-known clerical work from the orchestrator into the existing clock.",
                "outcome": "One compact semantic request expands to the complete legacy governance meaning.",
            },
            "current_position": {
                "strategic_role": "Retain fail-closed governance while reducing operator choices.",
                "why_now": "The matched first repair passed and a restored-session Git-object lapse exposed the next free-form trap.",
                "outcome": "Typed selectors, derived headers and exact commands replace repeated form filling.",
                "unlocks": [
                    "A matched operator-leaf efficacy review.",
                    "Future eligible tooling closeouts with fewer caller choices.",
                ],
                "does_not_solve": [
                    "It does not author semantic narrative.",
                    "It does not qualify a worker transport.",
                    "It does not open product or protected integration.",
                ],
                "orientation_statement": "Compile mechanics; retain human and model judgment only for semantic meaning.",
            },
            "next_operation": {
                "operation_id": fixture_successor,
                "active_tranche": "Provider-free semantic builder test-only successor",
                "objective": "Prove the semantic fixture can derive one unrecorded successor from its isolated latch.",
                "authority_source": "The test fixture derives a non-published successor and grants no continuing authority.",
                "next_stage": "stop_after_test_only_successor_projection",
            },
        },
        "verification_profile": SEMANTIC_VERIFICATION_PROFILE,
        "baton_slot": SEMANTIC_BATON_SLOT,
        "next_operation_protected_boundaries": list(latch["protected_boundaries"]),
    }


def _write_semantic_human_bodies(worktree: Path, intent: dict) -> list[str]:
    artifact_slug = intent["artifact_slug"]
    operation_id = intent["closeout"]["operation_id"]
    day = intent["recorded_at"][:10]
    paths = [
        f"docs/{artifact_slug}-plan.md",
        f"docs/security/{artifact_slug}-threat-model-delta.md",
        f"docs/{artifact_slug}-closeout.md",
        f"orchestration/human_inbox/yuri/{day}--{artifact_slug}.md",
        f"orchestration/agent_inbox/codex/{artifact_slug}-sol-acceptance.md",
    ]
    for relative in paths:
        target = worktree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"# Semantic fixture for {operation_id}\n\nBody remains semantic.\n",
            encoding="utf-8",
            newline="\n",
        )
    return paths


def test_cli_idempotency_requires_exact_intent_digest() -> None:
    transaction = {
        "operation_id": REDESIGN_OPERATION_ID,
        "event_kind": "checkpoint_transition",
        "journal": [
            {
                "payload": {
                    "intent_sha256": "sha256:" + "a" * 64,
                }
            }
        ],
    }
    assert _is_exact_published_intent(
        transaction,
        operation_id=REDESIGN_OPERATION_ID,
        event_kind="checkpoint_transition",
        intent_sha256="sha256:" + "a" * 64,
    )
    assert not _is_exact_published_intent(
        transaction,
        operation_id=REDESIGN_OPERATION_ID,
        event_kind="checkpoint_transition",
        intent_sha256="sha256:" + "b" * 64,
    )
    clean_transaction = {
        "operation_id": REDESIGN_OPERATION_ID,
        "event_kind": "clean_closeout",
        "journal": [
            {
                "payload": {
                    "manifest_sha256": "sha256:" + "c" * 64,
                }
            }
        ],
    }
    assert _is_exact_published_intent(
        clean_transaction,
        operation_id=REDESIGN_OPERATION_ID,
        event_kind="clean_closeout",
        intent_sha256="sha256:" + "c" * 64,
    )


def test_cli_output_pair_is_written_together(tmp_path: Path) -> None:
    result = {
        "status": "passed",
        "operation_id": REDESIGN_OPERATION_ID,
        "source_commit": "a" * 40,
        "generation_id": "gen-" + "b" * 64,
        "previous_generation_id": "gen-" + "c" * 64,
        "lease_sequence": 8,
        "transaction_facts": {
            "command_disposition": "publication_committed",
            "published_generations": 1,
            "byte_exact_rollbacks": 0,
        },
    }
    _write_outputs(tmp_path, result, prefix="clockwork-checkpoint-tick")
    assert (tmp_path / "clockwork-checkpoint-tick-evidence.json").is_file()
    report = tmp_path / "clockwork-checkpoint-tick-report.md"
    assert report.is_file()
    report_text = report.read_text(encoding="utf-8")
    assert "Lease sequence: 8" in report_text
    assert "Command disposition: `publication_committed`" in report_text
    assert "Published generations: 1" in report_text


def test_idempotent_readback_preserves_publication_pair_and_is_byte_idempotent(
    tmp_path: Path,
) -> None:
    publication = {
        "status": "passed",
        "operation_id": REDESIGN_OPERATION_ID,
        "source_commit": "a" * 40,
        "generation_id": "gen-" + "b" * 64,
        "previous_generation_id": "gen-" + "c" * 64,
        "lease_sequence": 8,
        "transaction_facts": {
            "command_disposition": "publication_committed",
            "published_generations": 1,
            "byte_exact_rollbacks": 0,
        },
    }
    readback = {
        **publication,
        "transaction_facts": {
            "command_disposition": "idempotent_readback",
            "published_generations": 0,
            "byte_exact_rollbacks": 0,
            "idempotent_readbacks": 1,
            "committed_lease_advance": 0,
        },
        "verification_facts": {
            "executed_command_count": 0,
            "passed_command_count": 0,
        },
    }
    _write_outputs(tmp_path, publication)
    evidence = tmp_path / "clockwork-tick-evidence.json"
    report = tmp_path / "clockwork-tick-report.md"
    before = (evidence.read_bytes(), report.read_bytes())

    target = _write_idempotent_readback(
        tmp_path,
        readback,
        prefix="clockwork-tick",
    )
    first_readback = target.read_bytes()

    assert (evidence.read_bytes(), report.read_bytes()) == before
    assert json.loads(first_readback) == readback
    assert target.name == "clockwork-tick-idempotent-readback.json"

    _write_idempotent_readback(
        tmp_path,
        readback,
        prefix="clockwork-tick",
    )
    assert target.read_bytes() == first_readback
    assert (evidence.read_bytes(), report.read_bytes()) == before


@pytest.mark.parametrize("missing_name", ["evidence", "report"])
def test_idempotent_readback_rejects_missing_publication_pair(
    tmp_path: Path,
    missing_name: str,
) -> None:
    publication = {
        "status": "passed",
        "operation_id": REDESIGN_OPERATION_ID,
        "source_commit": "a" * 40,
        "generation_id": "gen-" + "b" * 64,
        "previous_generation_id": "gen-" + "c" * 64,
        "lease_sequence": 8,
        "transaction_facts": {
            "command_disposition": "publication_committed",
            "published_generations": 1,
            "byte_exact_rollbacks": 0,
        },
    }
    readback = {
        **publication,
        "transaction_facts": {
            "command_disposition": "idempotent_readback",
            "published_generations": 0,
        },
    }
    _write_outputs(tmp_path, publication)
    (tmp_path / f"clockwork-tick-{missing_name}.json").unlink(missing_ok=True)
    if missing_name == "report":
        (tmp_path / "clockwork-tick-report.md").unlink()

    with pytest.raises(
        ClockworkTickRejection,
        match="tick_publication_evidence_preservation",
    ):
        _write_idempotent_readback(
            tmp_path,
            readback,
            prefix="clockwork-tick",
        )

    assert not (tmp_path / "clockwork-tick-idempotent-readback.json").exists()


def test_idempotent_readback_rejects_mismatched_publication(tmp_path: Path) -> None:
    publication = {
        "status": "passed",
        "operation_id": REDESIGN_OPERATION_ID,
        "source_commit": "a" * 40,
        "generation_id": "gen-" + "b" * 64,
        "previous_generation_id": "gen-" + "c" * 64,
        "lease_sequence": 8,
        "transaction_facts": {
            "command_disposition": "publication_committed",
            "published_generations": 1,
            "byte_exact_rollbacks": 0,
        },
    }
    _write_outputs(tmp_path, publication)
    before = {
        path.name: path.read_bytes()
        for path in (
            tmp_path / "clockwork-tick-evidence.json",
            tmp_path / "clockwork-tick-report.md",
        )
    }
    readback = {
        **publication,
        "generation_id": "gen-" + "d" * 64,
        "transaction_facts": {
            "command_disposition": "idempotent_readback",
            "published_generations": 0,
        },
    }

    with pytest.raises(
        ClockworkTickRejection,
        match="publication_evidence_generation_id_mismatch",
    ):
        _write_idempotent_readback(
            tmp_path,
            readback,
            prefix="clockwork-tick",
        )

    assert {
        path.name: path.read_bytes()
        for path in (
            tmp_path / "clockwork-tick-evidence.json",
            tmp_path / "clockwork-tick-report.md",
        )
    } == before
    assert not (tmp_path / "clockwork-tick-idempotent-readback.json").exists()


def test_output_prefix_is_closed_by_intent_schema() -> None:
    assert _output_prefix({"schema_version": CHECKPOINT_INTENT_VERSION}) == (
        "clockwork-checkpoint-tick"
    )
    assert _output_prefix({"schema_version": SEMANTIC_TICK_INTENT_VERSION}) == (
        "clockwork-tick"
    )


def test_prospective_human_evidence_returns_the_complete_ordered_error_set(
    tmp_path: Path,
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "plan.md").write_text(
        "# Plan\n\nDate: not-a-date\n",
        encoding="utf-8",
        newline="\n",
    )
    (docs / "closeout.md").write_text(
        "# Closeout\n\n"
        "Date: 2026-08-22\n\n"
        "Timestamp: 2026-08-23T00:00:00+11:00 (Australia/Brisbane)\n",
        encoding="utf-8",
        newline="\n",
    )
    node = {
        "evidence": {
            "plans": ["docs/plan.md"],
            "closeouts": ["docs/closeout.md"],
            "acceptances": [
                "docs/closeout.md",
                "docs/missing.md",
                "docs/not-markdown.json",
                "../escape.md",
            ],
        }
    }

    assert prospective_current_node_human_evidence_errors(tmp_path, node) == (
        "docs/plan.md:date_invalid",
        "docs/plan.md:timestamp_count",
        "docs/closeout.md:offset_not_brisbane",
        "docs/closeout.md:calendar_date_mismatch",
        "acceptances[0]:duplicate_path",
        "docs/closeout.md:offset_not_brisbane",
        "docs/closeout.md:calendar_date_mismatch",
        "acceptances[1]:file_missing",
        "acceptances[2]:markdown_path_required",
        "acceptances[3]:unsafe_path",
    )

    node["evidence"]["acceptances"] = []
    assert prospective_current_node_human_evidence_errors(tmp_path, node)[-1] == (
        "acceptances:nonempty_list_required"
    )


def test_command_local_transaction_facts_are_derived_for_every_disposition() -> None:
    prepared = {
        "base_pointer": {
            "lease_sequence": 7,
            "selected_generation_id": "gen-base",
        },
        "pointer": {"lease_sequence": 8},
        "generation_manifest": {"generation_id": "gen-prepared"},
    }
    dry = _prepared_transaction_facts(prepared, published=False)
    assert dry["command_disposition"] == "dry_preparation"
    assert dry["preparations"] == 1
    assert dry["preparation_rejections"] == 0
    assert dry["publication_attempts"] == 0
    assert dry["base_lease_sequence"] == 7
    assert dry["prospective_lease_sequence"] == 8
    assert dry["result_lease_sequence"] == 7
    assert dry["committed_lease_advance"] == 0
    assert dry["result_generation_id"] == "gen-base"

    published = _prepared_transaction_facts(prepared, published=True)
    assert published["command_disposition"] == "publication_committed"
    assert published["publication_attempts"] == 1
    assert published["published_generations"] == 1
    assert published["result_lease_sequence"] == 8
    assert published["committed_lease_advance"] == 1
    assert published["result_generation_id"] == "gen-prepared"

    readback = _idempotent_transaction_facts(
        {"lease_sequence": 8, "generation_id": "gen-prepared"}
    )
    assert readback["command_disposition"] == "idempotent_readback"
    assert readback["idempotent_readbacks"] == 1
    assert readback["preparations"] == 0
    assert readback["preparation_rejections"] == 0
    assert readback["publication_attempts"] == 0
    assert readback["committed_lease_advance"] == 0

    rollback = _rollback_transaction_facts(
        {
            "lease_sequence": 9,
            "rolled_back_from_generation_id": "gen-prepared",
            "selected_generation_id": "gen-base",
            "byte_exact": True,
        }
    )
    assert rollback["command_disposition"] == "byte_exact_rollback"
    assert rollback["rollback_attempts"] == 1
    assert rollback["byte_exact_rollbacks"] == 1
    assert rollback["base_lease_sequence"] == 8
    assert rollback["result_lease_sequence"] == 9
    assert rollback["committed_lease_advance"] == 1
    assert rollback["base_generation_id"] == "gen-prepared"
    assert rollback["result_generation_id"] == "gen-base"

    command_result = _command_result(
        {"status": "passed"}, published
    )
    assert command_result["live_publication_count"] == 1
    assert command_result["caller_authored_derived_fields"] == 0
    assert command_result["bespoke_updater_executions"] == 0

    rejected = _prospective_rejection_result(
        ClockworkTickRejection(
            "tick_prospective_current_node_evidence:"
            "docs/plan.md:timestamp_count,docs/closeout.md:date_count"
        )
    )
    assert rejected["status"] == "revision_required"
    assert rejected["error_count"] == 2
    assert rejected["errors"] == [
        "docs/plan.md:timestamp_count",
        "docs/closeout.md:date_count",
    ]
    assert rejected["transaction_facts"]["preparation_rejections"] == 1
    assert rejected["transaction_facts"]["publication_attempts"] == 0
    assert rejected["transaction_facts"]["committed_lease_advance"] == 0


def _blocked_intent(worktree: Path) -> dict:
    latch = _json(
        worktree
        / "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    commands = _json(worktree / INTENT_PATH.relative_to(ROOT))["command_manifest"]
    return {
        "schema_version": BLOCKED_INTENT_VERSION,
        "operation_id": latch["operation_id"],
        "completed_stage": "Bounded recovery exhausted with exact cleanup.",
        "user_attention_reason": "Choose a new recovery design or defer the gap.",
        "terminal_reason": "bounded_recovery_exhausted",
        "command_manifest": commands,
    }


def _user_decision_intent(worktree: Path) -> dict:
    latch = _json(
        worktree
        / "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    commands = _json(
        worktree
        / "orchestration/continuity/ariadne-governance-clockwork/command-manifest.json"
    )
    return {
        "schema_version": USER_DECISION_INTENT_VERSION,
        "blocked_operation_id": latch["operation_id"],
        "selected_outcome": "replace_with_newly_frozen_transport_redesign",
        "next_operation": {
            "operation_id": REDESIGN_OPERATION_ID,
            "active_tranche": "Raisa provider-free default-off check-in relay-free unknown-response transport redesign",
            "objective": "Freeze and provider-free prove a relay-free caller/result transport without a disposable PostgreSQL execution.",
            "authority_source": "Yuri's explicit transport-redesign selection and the blocked predecessor's immutable negative evidence.",
            "completed_stage": "Yuri selected transport redesign after the predecessor exhausted three fail-closed attempts.",
            "next_executable_stage": "freeze_relay_free_contract_without_database_execution",
        },
        "next_operation_protected_boundaries": [
            *latch["protected_boundaries"],
            "no_disposable_postgresql_execution_before_new_plan_and_preexecution_receipt",
        ],
        "command_manifest": commands,
    }


def _checkpoint_intent(worktree: Path) -> dict:
    latch = _json(
        worktree
        / "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    commands = _json(
        worktree
        / "orchestration/continuity/ariadne-governance-clockwork/command-manifest.json"
    )
    return {
        "schema_version": CHECKPOINT_INTENT_VERSION,
        "operation_id": latch["operation_id"],
        "completed_stage": "Relay-free contract, schemas, harness and deterministic static gates passed at an exact full-Git candidate.",
        "next_executable_stage": "run_one_no_database_relay_free_oci_result_channel_proof_then_stop_on_any_mismatch",
        "command_manifest": commands,
    }


def _incident_intent(worktree: Path) -> dict:
    intent = _replay_intent(worktree)
    intent["schema_version"] = TICK_INCIDENT_INTENT_VERSION
    intent["agent_error_observations"] = [
        {
            "attempt_key": "clockwork-test-review-packet-count",
            "observed_on": "2026-08-19",
            "tranche": "raisa-provider-free-clockwork-governed-check-in-successor-resolution",
            "role": "orchestrator",
            "resource_id": "codex-primary-orchestrator",
            "model": None,
            "reasoning_level": "high",
            "transport": "codex_primary_session",
            "stage": "independent_review",
            "category": "evidence_misreport",
            "process_severity": "moderate",
            "expected_invariant": "A review packet exact test count must equal mechanical collection of its exact command manifest.",
            "observed_error": "The first packet stated a count that did not equal the mechanically collected exact command.",
            "detection_method": "The orchestrator compared the packet statement with the exact command collection before acceptance.",
            "evidence_paths": [
                "docs/raisa-provider-free-clockwork-governed-check-in-successor-resolution-plan.md",
                "docs/security/raisa-provider-free-clockwork-governed-check-in-successor-resolution-threat-model-delta.md",
            ],
            "candidate_state": "canonical_unchanged",
            "workflow_disposition": "revision_required",
            "recurrence_signature": "orchestrator.review_packet_test_count_mismatch",
            "causal_claim_level": "observation_only",
            "correction": {
                "status": "control_added",
                "action": "Correct the packet count and require mechanical collection before dispatch.",
                "prevention_control": "Clockwork closeout admits the corrected review only after the rejected packet incident is canonically recorded.",
                "evidence_paths": [
                    "docs/raisa-provider-free-clockwork-governed-check-in-successor-resolution-plan.md",
                ],
            },
            "baton_summary": "preserves the rejected packet-count conflict and its mechanical-count correction.",
        }
    ]
    return intent


def _commit_incident_revision_artifact(
    worktree: Path, intent: dict, *, incident_count_adjustment: int = 0
) -> None:
    register_path = (
        worktree
        / "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    register = _json(register_path)
    revision = register["register_revision"] + 1
    first_number = int(register["incidents"][-1]["incident_id"].split("-")[1]) + 1
    incident_ids = [
        f"AER-{number:04d}"
        for number in range(
            first_number,
            first_number + len(intent["agent_error_observations"]),
        )
    ]
    relative = f"docs/ariadne-agent-error-correction-register-revision-{revision}.md"
    intent["baton_acceptance"]["paths"].append(relative)
    reading = "\n".join(
        [
            f"# Ariadne agent error and correction register — revision {revision}",
            "",
            "<!-- ariadne-agent-error-register-reading",
            f"revision: {revision}",
            (
                "incident_count: "
                f"{len(register['incidents']) + len(incident_ids) + incident_count_adjustment}"
            ),
            f"new_incident_ids: {','.join(incident_ids)}",
            "open_incident_count: 0",
            "-->",
            "",
            *[f"## {incident_id} — bounded test incident" for incident_id in incident_ids],
            "",
        ]
    )
    (worktree / relative).write_text(reading, encoding="utf-8")
    subprocess.run(
        ["git", "add", "--", relative],
        cwd=worktree,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add incident revision test artifact"],
        cwd=worktree,
        check=True,
        capture_output=True,
    )


@contextmanager
def _worktree(path: Path, source_ref: str = REPLAY_FIXTURE_SOURCE):
    source = subprocess.run(
        ["git", "rev-parse", f"{source_ref}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    branch = f"codex/clockwork-tick-test-{path.name[-12:]}"
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(path), source],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    try:
        yield path
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(path)],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )


def _paths(worktree: Path, contract: dict) -> tuple[dict[str, Path], dict[str, Path], Path]:
    canonical = {
        key: worktree / relative for key, relative in contract["canonical_paths"].items()
    }
    root = worktree / contract["clockwork_root"]
    metadata = {name: root / name for name in PREDECESSOR_METADATA_NAMES}
    return canonical, metadata, root / "current.json"


def test_semantic_builder_compiles_repository_owned_mechanics_with_fewer_leaves(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "semantic-expand", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        intent = _semantic_intent(worktree)

        scalar_leaves = semantic_scalar_leaf_count(intent)
        assert scalar_leaves == 44 + len(
            intent["next_operation_protected_boundaries"]
        )
        assert scalar_leaves <= 100
        admitted = expand_semantic_tick_intent(worktree, intent, contract)

        manifest = admitted["transaction_manifest"]
        node = manifest["node"]
        evidence = node["evidence"]
        commands = admitted["command_manifest"]["commands"]
        assert admitted["schema_version"] == "ariadne.governance_live_tick_intent.v1"
        assert manifest["source_anchor"] == "current_head"
        assert manifest["broker"] == {
            "enabled": False,
            "posture": "provider_free_shadow",
        }
        assert node["kind"] == "tooling"
        assert node["authority"]["authorized_openings"] == []
        assert {decision["status"] for decision in node["decisions"]} == {
            "accepted"
        }
        assert evidence["plans"] == [
            "docs/ariadne-clockwork-typed-semantic-builder-plan.md",
            "docs/security/ariadne-clockwork-typed-semantic-builder-threat-model-delta.md",
        ]
        assert evidence["closeouts"] == [
            "docs/ariadne-clockwork-typed-semantic-builder-closeout.md",
            "orchestration/human_inbox/yuri/2026-08-23--ariadne-clockwork-typed-semantic-builder.md",
        ]
        assert evidence["acceptances"] == [
            "orchestration/agent_inbox/codex/ariadne-clockwork-typed-semantic-builder-sol-acceptance.md"
        ]
        assert admitted["baton_acceptance"]["label"] == SEMANTIC_BATON_LABEL
        assert [command["command_id"] for command in commands] == [
            "semantic-closeout-evidence-json",
            "semantic-closeout-ruff",
            "semantic-closeout-governance-tests",
        ]
        assert {command["executable"] for command in commands} == {
            ".venv/Scripts/python.exe"
        }
        assert commands[2]["arguments"][-4:] == [
            "tests/test_current_baton_consistency.py",
            "tests/test_ariadne_active_operation_latch.py",
            "tests/test_ariadne_governance_clockwork_tick.py",
            "tests/test_ariadne_transactional_closeout.py",
        ]


def test_semantic_builder_rejects_hostile_selectors_paths_and_leaf_overflow(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "semantic-hostile", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        baseline = _semantic_intent(worktree)
        hostile: list[tuple[dict, str]] = []

        wrong_profile = json.loads(json.dumps(baseline))
        wrong_profile["profile"] = "arbitrary"
        hostile.append((wrong_profile, "tick_semantic_profile"))

        wrong_verification = json.loads(json.dumps(baseline))
        wrong_verification["verification_profile"] = "arbitrary"
        hostile.append(
            (wrong_verification, "tick_semantic_verification_profile")
        )

        wrong_baton = json.loads(json.dumps(baseline))
        wrong_baton["baton_slot"] = "arbitrary"
        hostile.append((wrong_baton, "tick_semantic_baton_slot"))

        unknown_key = json.loads(json.dumps(baseline))
        unknown_key["command_manifest"] = {}
        hostile.append((unknown_key, "tick_semantic_intent_keys"))

        branding_path = json.loads(json.dumps(baseline))
        branding_path["closeout"]["additional_artifacts"] = [
            "docs/branding/untouchable.svg"
        ]
        hostile.append((branding_path, "tick_semantic_additional_artifact"))

        too_many_leaves = json.loads(json.dumps(baseline))
        too_many_leaves["closeout"]["authority_notes"] = [
            f"Bounded authority note {index}." for index in range(101)
        ]
        hostile.append((too_many_leaves, "tick_semantic_scalar_leaf_budget"))

        for candidate, reason in hostile:
            with pytest.raises(ClockworkTickRejection, match=reason):
                expand_semantic_tick_intent(worktree, candidate, contract)


def test_semantic_header_materializer_derives_ten_values_and_is_idempotent(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "semantic-header", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        intent = _semantic_intent(worktree)
        paths = _write_semantic_human_bodies(worktree, intent)

        result = materialize_semantic_evidence_headers(
            worktree, intent, contract
        )
        first_bytes = {
            relative: (worktree / relative).read_bytes() for relative in paths
        }
        assert result["document_count"] == 5
        assert result["materialized_documents"] == paths
        assert result["unchanged_documents"] == []
        assert result["derived_header_scalar_values"] == 10
        assert result["caller_timestamp_values"] == 1
        for relative in paths:
            text = first_bytes[relative].decode("utf-8")
            assert text.count("Date: 2026-08-23") == 1
            assert text.count(
                "Timestamp: 2026-08-23T17:17:00.4614783+10:00 "
                "(Australia/Brisbane)"
            ) == 1

        repeated = materialize_semantic_evidence_headers(
            worktree, intent, contract
        )
        assert repeated["materialized_documents"] == []
        assert repeated["unchanged_documents"] == paths
        assert {
            relative: (worktree / relative).read_bytes() for relative in paths
        } == first_bytes


def test_semantic_header_materializer_returns_all_defects_before_any_write(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "semantic-conflict", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        intent = _semantic_intent(worktree)
        paths = _write_semantic_human_bodies(worktree, intent)
        targets = [worktree / relative for relative in paths]
        targets[0].write_text(
            "# Partial\n\nDate: 2026-08-23\n\nBody.\n",
            encoding="utf-8",
            newline="\n",
        )
        targets[1].write_text(
            "# Conflict\n\nDate: 2026-08-22\n\n"
            "Timestamp: 2026-08-22T17:17:00+10:00 (Australia/Brisbane)\n",
            encoding="utf-8",
            newline="\n",
        )
        targets[2].unlink()
        targets[3].write_text("No heading.\n", encoding="utf-8", newline="\n")
        targets[4].write_bytes(b"\xff")
        before = {
            target: target.read_bytes() if target.exists() else None
            for target in targets
        }

        with pytest.raises(ClockworkTickRejection) as caught:
            materialize_semantic_evidence_headers(worktree, intent, contract)

        assert str(caught.value).split(":", 1)[0] == (
            "tick_semantic_evidence_materialization"
        )
        errors = str(caught.value).split(":", 1)[1].split(",")
        assert errors == [
            f"{paths[0]}:derived_header_conflict",
            f"{paths[1]}:derived_header_conflict",
            f"{paths[2]}:file_missing",
            f"{paths[3]}:h1_required",
            f"{paths[4]}:file_unreadable",
        ]
        assert {
            target: target.read_bytes() if target.exists() else None
            for target in targets
        } == before


def test_semantic_header_materializer_restores_every_byte_on_midwrite_failure(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "semantic-rollback", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        intent = _semantic_intent(worktree)
        paths = _write_semantic_human_bodies(worktree, intent)
        before = {
            relative: (worktree / relative).read_bytes() for relative in paths
        }

        with pytest.raises(
            ClockworkTickRejection,
            match="tick_semantic_materialization_write",
        ):
            materialize_semantic_evidence_headers(
                worktree, intent, contract, fail_at="after_replace_1"
            )

        assert {
            relative: (worktree / relative).read_bytes() for relative in paths
        } == before


def test_semantic_intent_builds_without_canonical_mutation(tmp_path: Path) -> None:
    with _worktree(tmp_path / "semantic-build", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        intent = _semantic_intent(worktree)
        _write_semantic_human_bodies(worktree, intent)
        materialize_semantic_evidence_headers(worktree, intent, contract)
        admitted = expand_semantic_tick_intent(worktree, intent, contract)
        evidence = admitted["transaction_manifest"]["node"]["evidence"]
        for relative in [*evidence["findings"], *evidence["receipts"]]:
            target = worktree / relative
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "{}\n" if target.suffix == ".json" else "# Fixture evidence\n",
                encoding="utf-8",
                newline="\n",
            )
        canonical, metadata, pointer = _paths(worktree, contract)
        protected_paths = [*canonical.values(), *metadata.values(), pointer]
        before = {path: path.read_bytes() for path in protected_paths}

        prepared = build_tick_generation(worktree, contract, intent)

        assert prepared["intent"]["transaction_manifest"]["operation_id"] == (
            intent["closeout"]["operation_id"]
        )
        assert prepared["intent"]["schema_version"] == (
            "ariadne.governance_live_tick_intent.v1"
        )
        assert {path: path.read_bytes() for path in protected_paths} == before


def test_semantic_verification_executes_exact_commands_and_fails_closed(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "semantic-commands", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        admitted = expand_semantic_tick_intent(
            worktree, _semantic_intent(worktree), contract
        )
        manifest = admitted["command_manifest"]

        calls: list[list[str]] = []

        def passing_runner(arguments: list[str], **_: object) -> subprocess.CompletedProcess:
            calls.append(arguments)
            return subprocess.CompletedProcess(
                arguments, 0, stdout=f"passed-{len(calls)}", stderr=""
            )

        facts = _run_semantic_verification(
            worktree,
            manifest,
            command_runner=passing_runner,
            tracked_reader=lambda _: "",
            interpreter=Path(sys.executable),
        )
        assert calls == [
            [str(Path(sys.executable).resolve()), *command["arguments"]]
            for command in manifest["commands"]
        ]
        assert facts["disposition"] == "verification_passed"
        assert facts["executed_command_count"] == 3
        assert facts["passed_command_count"] == 3
        assert len(facts["commands"]) == 3
        assert all(len(row["stdout_sha256"]) == 64 for row in facts["commands"])

        failed_calls = 0

        def failing_runner(arguments: list[str], **_: object) -> subprocess.CompletedProcess:
            nonlocal failed_calls
            failed_calls += 1
            return subprocess.CompletedProcess(
                arguments,
                1 if failed_calls == 2 else 0,
                stdout="bounded",
                stderr="failed" if failed_calls == 2 else "",
            )

        with pytest.raises(SemanticVerificationRejection) as command_failure:
            _run_semantic_verification(
                worktree,
                manifest,
                command_runner=failing_runner,
                tracked_reader=lambda _: "",
                interpreter=Path(sys.executable),
            )
        assert command_failure.value.facts["reason"] == "command_failed"
        assert command_failure.value.facts["executed_command_count"] == 2
        assert command_failure.value.facts["passed_command_count"] == 1

        statuses = iter(["", "", " M controlled.py\n"])
        with pytest.raises(SemanticVerificationRejection) as drift_failure:
            _run_semantic_verification(
                worktree,
                manifest,
                command_runner=passing_runner,
                tracked_reader=lambda _: next(statuses),
                interpreter=Path(sys.executable),
            )
        assert drift_failure.value.facts["reason"] == "tracked_worktree_drift"
        assert drift_failure.value.facts["tracked_drift"] == 1
        assert drift_failure.value.facts["executed_command_count"] == 2


def _driver_tick_result(*, published: bool) -> dict:
    command_count = 3
    return {
        "status": "passed",
        "source_commit": "a" * 40,
        "generation_id": "gen-" + "b" * 64,
        "lease_sequence": 220 if published else 219,
        "live_publication_count": int(published),
        "transaction_facts": {
            "command_disposition": (
                "publication_committed" if published else "dry_preparation"
            ),
            "published_generations": int(published),
            "committed_lease_advance": int(published),
        },
        "verification_facts": {
            "disposition": "verification_passed",
            "command_count": command_count,
            "executed_command_count": command_count,
            "passed_command_count": command_count,
            "tracked_drift": 0,
        },
    }


def test_bound_closeout_captures_only_exact_tick_dispositions() -> None:
    rehearsal = capture_tick_reading(
        _driver_tick_result(published=False),
        mode="rehearse",
        semantic_command_count=3,
    )
    assert rehearsal["status"] == "not_executed_rehearsal"
    assert rehearsal["source_commit"] == "a" * 40

    publication = capture_tick_reading(
        _driver_tick_result(published=True),
        mode="publish",
        semantic_command_count=3,
    )
    assert publication == {
        "status": "passed",
        "captured_from": "tick_publish_return_after_validate_tick_live_state",
        "source_commit": "a" * 40,
        "generation_id": "gen-" + "b" * 64,
        "lease_sequence": 220,
    }

    idempotent = _driver_tick_result(published=True)
    idempotent["transaction_facts"]["command_disposition"] = "idempotent_readback"
    with pytest.raises(
        CloseoutDriverRejection, match="committed_publication_result_required"
    ):
        capture_tick_reading(
            idempotent,
            mode="publish",
            semantic_command_count=3,
        )

    short_source = _driver_tick_result(published=False)
    short_source["source_commit"] = "abcdef0"
    with pytest.raises(CloseoutDriverRejection, match="tick_source_not_full_git_id"):
        capture_tick_reading(
            short_source,
            mode="rehearse",
            semantic_command_count=3,
        )


def test_bound_closeout_resolves_full_head_and_repository_interpreter() -> None:
    head = resolve_full_head(ROOT)
    interpreter, attested = resolve_repository_interpreter(ROOT)

    assert len(head) == 40
    assert Path(attested).resolve() == interpreter
    assert interpreter == (ROOT / ".venv/Scripts/python.exe").resolve()

    def abbreviated_runner(
        arguments: list[str], **_: object
    ) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(arguments, 0, stdout="abcdef0\n", stderr="")

    with pytest.raises(CloseoutDriverRejection, match="full_head_resolution_failed"):
        resolve_full_head(ROOT, runner=abbreviated_runner)


def test_bound_closeout_allowlist_derives_fixed_outputs_and_excludes_branding(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "closeout-allowlist", source_ref="HEAD") as worktree:
        contract = validate_contract(
            _json(worktree / CONTRACT_PATH.relative_to(ROOT))
        )
        intent = _semantic_intent(worktree)
        intent_path = (
            worktree
            / "orchestration/continuity/"
            "ariadne-clockwork-typed-semantic-builder/closeout-intent.json"
        )
        intent_path.parent.mkdir(parents=True, exist_ok=True)
        intent_path.write_text(json.dumps(intent), encoding="utf-8")
        admitted = expand_semantic_tick_intent(worktree, intent, contract)

        allowlist = derive_allowlist(
            worktree,
            intent_path=intent_path,
            admitted=admitted,
            contract=contract,
        )

        assert (
            "orchestration/continuity/ariadne-clockwork-typed-semantic-builder/"
            "closeout-driver-result.json"
        ) in allowlist
        assert (
            "orchestration/continuity/ariadne-clockwork-typed-semantic-builder/"
            "explicit-stage-manifest.json"
        ) in allowlist
        assert "AGENTS.md" in allowlist
        assert not any(path.startswith("docs/branding/") for path in allowlist)


def test_explicit_stage_manifest_intersects_git_inventory_without_index_mutation(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "stage-manifest"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "clockwork@example.invalid"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Clockwork Test"], cwd=repo, check=True
    )
    (repo / "allowed.txt").write_text("before\n", encoding="utf-8")
    (repo / "unexpected-tracked.txt").write_text("before\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "--", "allowed.txt", "unexpected-tracked.txt"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True
    )
    (repo / "allowed.txt").write_text("after\n", encoding="utf-8")
    (repo / "allowed-untracked.txt").write_text("new\n", encoding="utf-8")
    (repo / "other-untracked.txt").write_text("preserve\n", encoding="utf-8")
    branding = repo / "docs/branding"
    branding.mkdir(parents=True)
    (branding / "logo.svg").write_text("preserve\n", encoding="utf-8")
    topic = repo / "orchestration/continuity/topic"
    topic.mkdir(parents=True)
    result_path = topic / "closeout-driver-result.json"
    manifest_path = topic / "explicit-stage-manifest.json"
    allowlist = {
        "allowed.txt",
        "allowed-untracked.txt",
        "orchestration/continuity/topic/closeout-driver-result.json",
        "orchestration/continuity/topic/explicit-stage-manifest.json",
    }

    manifest = build_stage_manifest(
        repo,
        head="a" * 40,
        allowlist=allowlist,
        result_path=result_path,
        manifest_path=manifest_path,
    )

    assert manifest["paths"] == [
        "allowed-untracked.txt",
        "allowed.txt",
        "orchestration/continuity/topic/closeout-driver-result.json",
        "orchestration/continuity/topic/explicit-stage-manifest.json",
    ]
    assert manifest["excluded_untracked_path_count"] == 2
    assert manifest["git_add_invocations"] == 0
    assert manifest["git_index_mutations"] == 0
    assert not subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    (repo / "unexpected-tracked.txt").write_text("after\n", encoding="utf-8")
    with pytest.raises(
        CloseoutDriverRejection, match="unexpected_tracked_stage_path"
    ):
        build_stage_manifest(
            repo,
            head="a" * 40,
            allowlist=allowlist,
            result_path=result_path,
            manifest_path=manifest_path,
        )


def test_bound_closeout_retains_the_exact_postpublication_file_selection() -> None:
    assert POSTPUBLICATION_TESTS == (
        "tests/test_current_baton_consistency.py",
        "tests/test_ariadne_active_operation_latch.py",
        "tests/test_ariadne_governance_clockwork_tick.py",
        "tests/test_ariadne_transactional_closeout.py",
        "tests/test_ariadne_orchestrator_preflight.py",
    )
    source = (
        ROOT / "scripts/ariadne_governance_clockwork_closeout.py"
    ).read_text(encoding="utf-8")
    assert "git add" not in source
    assert "--cached" in source


def test_plan_and_intent_freeze_the_unrepeated_successor() -> None:
    plan = (ROOT / "docs/raisa-provider-free-clockwork-governed-check-in-successor-resolution-plan.md").read_text(encoding="utf-8")
    report = (TOPIC / "successor-resolution-report.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/raisa-provider-free-clockwork-governed-check-in-successor-resolution-threat-model-delta.md").read_text(encoding="utf-8")
    contract = validate_contract(_json(CONTRACT_PATH))
    intent = validate_tick_intent(_json(INTENT_PATH), contract)
    manifest = intent["transaction_manifest"]
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    assert "Timestamp: 2026-08-19T" in threat
    assert "environment-manifest posture is first" in report
    assert manifest["node"]["relationships"] == [{
        "node_id": "ariadne-provider-free-clockwork-live-canonical-adoption-retirement",
        "relation": "builds_on",
    }]
    assert manifest["next_operation"]["operation_id"] == "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture"
    assert "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting" in intent["next_operation_protected_boundaries"]


def _rolling_slot_baton() -> str:
    return (ROOT / "AGENTS.md").read_text(encoding="utf-8").replace(
        "| DeepSeek native Harness authored-synthetic traceability micro-rehearsal acceptance |",
        "| Current DeepSeek native Harness acceptance |",
        1,
    )


def test_clockwork_compacts_the_rendered_baton_from_the_closed_index() -> None:
    manifest = _load_baton_compaction_manifest(ROOT)
    compacted = _compact_rendered_baton(
        _rolling_slot_baton(),
        manifest,
        acceptance_label="Current DeepSeek native Harness acceptance",
    )
    assert len(compacted.encode("utf-8")) < 80_000
    assert len(compacted.splitlines()) < 500
    assert compacted.count("| Current DeepSeek native Harness acceptance |") == 1
    assert "| DeepSeek native Harness authored-synthetic traceability micro-rehearsal acceptance |" not in compacted
    assert compacted.count("| Current Baton acceptance index |") == 1
    assert compacted.count("| Current clockwork relation |") == 1


def test_clockwork_compaction_rejects_an_unindexed_live_row() -> None:
    manifest = _load_baton_compaction_manifest(ROOT)
    hostile = _rolling_slot_baton().replace(
        "### Compact historical evaluation and transition state",
        "| Unregistered future acceptance | caller-authored |\n"
        "### Compact historical evaluation and transition state",
        1,
    )
    with pytest.raises(
        ClockworkTickRejection, match="tick_baton_compaction_unindexed"
    ):
        _compact_rendered_baton(
            hostile,
            manifest,
            acceptance_label="Current DeepSeek native Harness acceptance",
        )


def test_clockwork_compaction_rejects_an_unregistered_acceptance_label() -> None:
    manifest = _load_baton_compaction_manifest(ROOT)
    with pytest.raises(
        ClockworkTickRejection, match="tick_baton_compaction_unindexed"
    ):
        _compact_rendered_baton(
            _rolling_slot_baton(),
            manifest,
            acceptance_label="Caller-authored duplicate acceptance",
        )


def test_intent_rejects_derived_unsafe_and_underbounded_input() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    baseline = _json(INTENT_PATH)
    derived = json.loads(json.dumps(baseline))
    derived["transaction_manifest"]["source_commit"] = "a" * 40
    with pytest.raises(ClockworkTickRejection, match="caller_authored_derived_binding"):
        validate_tick_intent(derived, contract)
    unsafe = json.loads(json.dumps(baseline))
    unsafe["baton_acceptance"]["paths"][0] = "docs/branding/escape.md"
    with pytest.raises(ClockworkTickRejection, match="tick_baton_path"):
        validate_tick_intent(unsafe, contract)
    shell = json.loads(json.dumps(baseline))
    shell["command_manifest"]["commands"][0]["arguments"].append("value;unsafe")
    with pytest.raises(ClockworkTickRejection, match="tick_command_contract"):
        validate_tick_intent(shell, contract)
    for boundary in (
        "explicit_path_staging_only",
        "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting",
    ):
        underbounded = json.loads(json.dumps(baseline))
        underbounded["next_operation_protected_boundaries"].remove(boundary)
        with pytest.raises(
            ClockworkTickRejection, match="tick_next_boundaries_floor"
        ):
            validate_tick_intent(underbounded, contract)


def _typed_boundaries(*historical: str) -> list[str]:
    return [
        *sorted(REQUIRED_NEXT_BOUNDARIES),
        TYPED_PRODUCT_DATA_DENIAL_BOUNDARY,
        *historical,
    ]


def test_historical_boundary_modes_are_closed_and_mutually_exclusive() -> None:
    legacy = [*sorted(REQUIRED_NEXT_BOUNDARIES), LEGACY_FULL_DATA_DENIAL_BOUNDARY]
    typed_denial = _typed_boundaries(TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY)
    bounded_probe = _typed_boundaries(*sorted(HISTORICAL_DIARY_SUBGATE_BOUNDARIES))
    materialisation = _typed_boundaries(
        *sorted(HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES)
    )
    consumption = _typed_boundaries(
        *sorted(
            HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES
        )
    )

    assert validate_next_operation_protected_boundaries(legacy) == legacy
    assert validate_next_operation_protected_boundaries(typed_denial) == typed_denial
    assert validate_next_operation_protected_boundaries(bounded_probe) == bounded_probe
    assert (
        validate_next_operation_protected_boundaries(materialisation)
        == materialisation
    )
    assert validate_next_operation_protected_boundaries(consumption) == consumption

    for conflicting in (
        [*bounded_probe, TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY],
        [*bounded_probe, LEGACY_FULL_DATA_DENIAL_BOUNDARY],
        [*legacy, HISTORICAL_DIARY_ACCESS_BOUNDARY],
        [*materialisation, TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY],
        [*materialisation, LEGACY_FULL_DATA_DENIAL_BOUNDARY],
        [*bounded_probe, *HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES],
        [*consumption, TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY],
        [*consumption, LEGACY_FULL_DATA_DENIAL_BOUNDARY],
        [*bounded_probe, *HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES],
        [*materialisation, *HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES],
    ):
        with pytest.raises(
            ClockworkTickRejection, match="historical_mode_conflict"
        ):
            validate_next_operation_protected_boundaries(conflicting)


def test_historical_boundary_rejects_missing_broad_denial_and_partial_subgate() -> None:
    bounded_probe = _typed_boundaries(*sorted(HISTORICAL_DIARY_SUBGATE_BOUNDARIES))
    missing_product_floor = [
        item for item in bounded_probe if item != TYPED_PRODUCT_DATA_DENIAL_BOUNDARY
    ]
    with pytest.raises(ClockworkTickRejection, match="product_data_floor"):
        validate_next_operation_protected_boundaries(missing_product_floor)

    for member in HISTORICAL_DIARY_SUBGATE_BOUNDARIES:
        partial = [item for item in bounded_probe if item != member]
        with pytest.raises(
            ClockworkTickRejection, match="historical_subgate_incomplete"
        ):
            validate_next_operation_protected_boundaries(partial)

    materialisation = _typed_boundaries(
        *sorted(HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES)
    )
    for member in HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES:
        partial = [item for item in materialisation if item != member]
        with pytest.raises(
            ClockworkTickRejection, match="historical_subgate_incomplete"
        ):
            validate_next_operation_protected_boundaries(partial)

    consumption = _typed_boundaries(
        *sorted(
            HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES
        )
    )
    for member in HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES:
        partial = [item for item in consumption if item != member]
        with pytest.raises(
            ClockworkTickRejection, match="historical_subgate_incomplete"
        ):
            validate_next_operation_protected_boundaries(partial)


def test_historical_boundary_rejects_unknown_digest_and_overbroad_allowance() -> None:
    bounded_probe = _typed_boundaries(*sorted(HISTORICAL_DIARY_SUBGATE_BOUNDARIES))
    contract_token = next(
        item for item in bounded_probe if "contract_sha256" in item
    )
    altered_digest = [
        (item[:-1] + ("0" if item[-1] != "0" else "1"))
        if item == contract_token
        else item
        for item in bounded_probe
    ]
    with pytest.raises(ClockworkTickRejection, match="historical_vocabulary"):
        validate_next_operation_protected_boundaries(altered_digest)

    overbroad = _typed_boundaries("allow_all_historical_archive_access")
    with pytest.raises(ClockworkTickRejection, match="access_vocabulary"):
        validate_next_operation_protected_boundaries(overbroad)

    unknown_historical = _typed_boundaries("no_historical_data_access_except_local")
    with pytest.raises(ClockworkTickRejection, match="historical_vocabulary"):
        validate_next_operation_protected_boundaries(unknown_historical)

    materialisation = _typed_boundaries(
        *sorted(HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES)
    )
    for selected in (
        next(
            item
            for item in materialisation
            if "materialisation_subgate_contract_sha256" in item
        ),
        next(
            item
            for item in materialisation
            if "historical_first_use_candidate_gate_source" in item
        ),
    ):
        altered_materialisation_coordinate = [
            (item[:-1] + ("0" if item[-1] != "0" else "1"))
            if item == selected
            else item
            for item in materialisation
        ]
        with pytest.raises(ClockworkTickRejection, match="historical_vocabulary"):
            validate_next_operation_protected_boundaries(
                altered_materialisation_coordinate
            )

    consumption = _typed_boundaries(
        *sorted(
            HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES
        )
    )
    for coordinate_fragment in (
        "consumption_subgate_contract_sha256",
        "consumption_first_use_source",
        "consumption_fixture_sha256",
    ):
        selected = next(item for item in consumption if coordinate_fragment in item)
        altered_consumption_coordinate = [
            (item[:-1] + ("0" if item[-1] != "0" else "1"))
            if item == selected
            else item
            for item in consumption
        ]
        with pytest.raises(ClockworkTickRejection, match="historical_vocabulary"):
            validate_next_operation_protected_boundaries(
                altered_consumption_coordinate
            )


def test_historical_diary_subgate_is_byte_and_semantically_bound() -> None:
    contract_bytes = HISTORICAL_DIARY_SUBGATE_CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)
    digest = hashlib.sha256(contract_bytes).hexdigest()
    assert (
        "historical_diary_privacy_subgate_contract_sha256_" + digest
        in HISTORICAL_DIARY_SUBGATE_BOUNDARIES
    )
    assert contract["schema_version"] == "historical_diary.real_access_subgate.v1"
    assert contract["executable_in_this_tranche"] is False
    assert contract["actual_path_bound"] is False
    assert contract["real_archive_accessed"] is False
    assert contract["scope"] == {
        "exact_ignored_local_readback_required": True,
        "explicitly_nominated_leaf_root_count": 1,
        "maximum_file_count": 80,
        "maximum_per_file_bytes": 8388608,
        "maximum_total_bytes": 134217728,
        "nominated_dense_day_count": 1,
        "recursive_access_allowed": False,
        "symlink_or_reparse_traversal_allowed": False,
    }
    assert not any(contract["capabilities"].values())
    assert contract["retention"] == {
        "aggregate_non_phi_commit_only": True,
        "automatic_failure_cleanup_required": True,
        "ephemeral_in_memory_key_required": True,
        "ignored_new_output_root_required": True,
        "key_or_mapping_persistence_allowed": False,
    }
    assert contract["decision_vocabulary"] == [
        "blocked",
        "revision_required",
        "locally_restricted_candidate",
    ]
    assert contract["strongest_decision_meaning"] == (
        "ignored_local_research_retention_only_no_downstream_authority"
    )


def test_historical_first_use_materialisation_subgate_is_byte_and_semantically_bound() -> None:
    contract_bytes = HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)
    digest = hashlib.sha256(contract_bytes).hexdigest()
    assert (
        "historical_first_use_materialisation_subgate_contract_sha256_" + digest
        in HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES
    )
    assert contract["schema_version"] == (
        "raisa.governance_clockwork_historical_first_use_materialisation_"
        "subgate_contract.v1"
    )
    assert contract["status"] == "frozen_fail_closed_successor_contract"
    assert contract["builds_on_reviewed_source"] == (
        "abcd4206a363b0c565c070e0f2cb9c54d627b3b3"
    )
    assert (
        "historical_first_use_candidate_gate_source_"
        + contract["builds_on_reviewed_source"]
        in HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES
    )
    assert contract["source_boundary"] == {
        "historical_archive_access": False,
        "ignored_attempt_output_access": False,
        "authored_synthetic_boundary_tests_only": True,
        "provider_network_model_calls": False,
        "product_database_client_or_runtime": False,
    }
    assert contract["implementation"] == {
        "add_one_closed_historical_first_use_materialisation_mode": True,
        "preserve_legacy_denial_measurement_subgate_and_conflict_rules": True,
        "reject_partial_mixed_or_unknown_historical_modes": True,
        "bind_exact_candidate_gate_source": (
            "abcd4206a363b0c565c070e0f2cb9c54d627b3b3"
        ),
        "maximum_reusable_fixtures": 1,
        "exact_gate_receipt_before_write": True,
        "blocked_or_revision_required_writes_fixture": False,
        "authority_non_transitive": True,
    }
    assert contract["verification"]["historical_content_runs"] == 0
    assert not any(contract["authority_ceiling"].values())
    assert (
        HISTORICAL_FIRST_USE_MATERIALISATION_ACCESS_BOUNDARY
        in HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES
    )


def test_historical_derived_minimised_scenario_consumption_subgate_is_bound() -> None:
    contract_bytes = (
        HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_CONTRACT.read_bytes()
    )
    contract = json.loads(contract_bytes)
    digest = hashlib.sha256(contract_bytes).hexdigest()
    boundaries = (
        HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES
    )

    assert (
        "historical_derived_minimised_scenario_consumption_subgate_contract_"
        "sha256_" + digest
        in boundaries
    )
    assert contract["schema_version"] == (
        "raisa.historical_derived_minimised_scenario_consumption_subgate_"
        "successor_contract.v1"
    )
    assert contract["status"] == "frozen_fail_closed_successor_contract"
    accepted = contract["accepted_first_use"]
    assert accepted == {
        "reviewed_source": "4740813d53ebbc4872fe8c0c08ce2578b1982770",
        "candidate_gate_source": "abcd4206a363b0c565c070e0f2cb9c54d627b3b3",
        "fixture_sha256": (
            "2205ab83cec7c5639d39cc563cee80eec825ac33f17571151571d325e74f2dfe"
        ),
        "fixture_class": "minimised_structural_scenario",
        "fixture_location": (
            "local_data/historical-diary-trove/derived-scenarios/"
            "2026-08-24-first-use-check-in-context-v1/scenario.json"
        ),
        "fixture_committed": False,
        "authority_non_transitive": True,
    }
    assert (
        "historical_derived_minimised_scenario_consumption_first_use_source_"
        + accepted["reviewed_source"]
        in boundaries
    )
    assert (
        "historical_derived_minimised_scenario_consumption_fixture_sha256_"
        + accepted["fixture_sha256"]
        in boundaries
    )
    assert contract["clockwork_objective"] == {
        "new_mode": "exact_digest_bound_local_test_fixture_consumption",
        "fixture_reads_during_clockwork_tranche": 0,
        "historical_archive_reads": 0,
        "product_or_adapter_invocations": 0,
        "partial_mixed_unknown_or_altered_forms_fail_closed": True,
    }
    ceiling = contract["eventual_consumption_ceiling"]
    assert ceiling["exact_fixture_digest_required"] is True
    assert ceiling["local_provider_free_authored_synthetic_test_context_only"] is True
    assert ceiling["maximum_fixture_reads"] == 1
    assert ceiling["raw_archive_access"] is False
    assert ceiling["provider_model_network_prompt_telemetry_clipboard_or_external_release"] is False
    assert ceiling["product_patient_appointment_clinical_or_protected_data"] is False
    assert ceiling["database_route_client_runtime_or_configuration"] is False
    assert ceiling["ordinary_practice_activation"] is False
    assert HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_ACCESS_BOUNDARY in boundaries
    assert contract["claim_ceiling"] == (
        "the_next_tranche_only_adds_a_closed_clockwork_form_and_does_not_read_"
        "or_consume_the_fixture"
    )


def test_closeout_and_user_decision_paths_share_the_typed_boundary_control() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    bounded_probe = _typed_boundaries(*sorted(HISTORICAL_DIARY_SUBGATE_BOUNDARIES))
    materialisation = _typed_boundaries(
        *sorted(HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES)
    )
    consumption = _typed_boundaries(
        *sorted(
            HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES
        )
    )

    for boundaries in (bounded_probe, materialisation, consumption):
        closeout = _json(INTENT_PATH)
        closeout["next_operation_protected_boundaries"] = boundaries
        assert validate_tick_intent(closeout, contract)[
            "next_operation_protected_boundaries"
        ] == boundaries

        decision = _user_decision_intent(ROOT)
        decision["next_operation_protected_boundaries"] = boundaries
        assert validate_user_decision_tick_intent(decision, contract)[
            "next_operation_protected_boundaries"
        ] == boundaries

    for boundaries, access_boundary in (
        (bounded_probe, HISTORICAL_DIARY_ACCESS_BOUNDARY),
        (materialisation, HISTORICAL_FIRST_USE_MATERIALISATION_ACCESS_BOUNDARY),
        (
            consumption,
            HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_ACCESS_BOUNDARY,
        ),
    ):
        incomplete = [item for item in boundaries if item != access_boundary]
        closeout = _json(INTENT_PATH)
        closeout["next_operation_protected_boundaries"] = incomplete
        with pytest.raises(
            ClockworkTickRejection,
            match="tick_next_boundaries_historical_subgate_incomplete",
        ):
            validate_tick_intent(closeout, contract)
        decision = _user_decision_intent(ROOT)
        decision["next_operation_protected_boundaries"] = incomplete
        with pytest.raises(
            ClockworkTickRejection,
            match="user_decision_next_boundaries_historical_subgate_incomplete",
        ):
            validate_user_decision_tick_intent(decision, contract)


def _governance_v2_manifest() -> dict:
    return {
        "schema_version": "ariadne.governance_command_manifest.v2",
        "database_authority": "closed",
        "commands": [
            {
                "command_id": "provider-free-prepublication",
                "executable": ".venv/Scripts/python.exe",
                "arguments": [
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "tests/test_ariadne_governance_clockwork_tick.py",
                ],
                "completion_contract": "final_exit_code_zero_required",
                "verification_phase": "prepublication",
            },
            {
                "command_id": "provider-free-postpublication",
                "executable": ".venv/Scripts/python.exe",
                "arguments": [
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "tests/test_current_baton_consistency.py",
                ],
                "completion_contract": "final_exit_code_zero_required",
                "verification_phase": "postpublication",
            },
        ],
    }


def test_governance_v2_admits_closed_provider_free_phases() -> None:
    admitted = _validate_commands(_governance_v2_manifest())

    assert admitted["database_authority"] == "closed"
    assert [row["verification_phase"] for row in admitted["commands"]] == [
        "prepublication",
        "postpublication",
    ]


@pytest.mark.parametrize(
    "module",
    ["pytest", "scripts.ariadne_serial_pytest"],
)
def test_governance_v2_rejects_database_capable_pytest(module: str) -> None:
    manifest = _governance_v2_manifest()
    manifest["commands"][0]["arguments"][1] = module

    with pytest.raises(
        ClockworkTickRejection, match="tick_database_closed_pytest_runner"
    ):
        _validate_commands(manifest)


def test_governance_v2_rejects_unknown_and_reversed_phase() -> None:
    unknown = _governance_v2_manifest()
    unknown["commands"][0]["verification_phase"] = "before_publish"
    with pytest.raises(ClockworkTickRejection, match="tick_verification_phase"):
        _validate_commands(unknown)

    reversed_order = _governance_v2_manifest()
    reversed_order["commands"][0]["verification_phase"] = "postpublication"
    reversed_order["commands"][1]["verification_phase"] = "prepublication"
    with pytest.raises(
        ClockworkTickRejection, match="tick_verification_phase_order"
    ):
        _validate_commands(reversed_order)


def test_intent_rejects_non_object_contract_evidence_before_projection() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    malformed = _json(INTENT_PATH)
    malformed["transaction_manifest"]["node"]["contract_evidence"] = [
        "docs/not-a-contract-evidence-object.md"
    ]
    with pytest.raises(
        ClockworkTickRejection, match="tick_transaction_manifest"
    ):
        validate_tick_intent(malformed, contract)


def test_incident_intent_rejects_derived_identity_and_unsafe_evidence() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    baseline = _incident_intent(ROOT)
    observed = validate_tick_intent(baseline, contract)
    assert observed["schema_version"] == TICK_INCIDENT_INTENT_VERSION
    assert "incident_id" not in observed["agent_error_observations"][0]
    derived = json.loads(json.dumps(baseline))
    derived["agent_error_observations"][0]["incident_id"] = "AER-9999"
    with pytest.raises(
        ClockworkTickRejection, match="tick_incident_observation_keys"
    ):
        validate_tick_intent(derived, contract)
    unsafe = json.loads(json.dumps(baseline))
    unsafe["agent_error_observations"][0]["evidence_paths"] = [
        "docs/branding/escape.md"
    ]
    with pytest.raises(ClockworkTickRejection, match="tick_incident_evidence_path"):
        validate_tick_intent(unsafe, contract)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("observed_on", "2026-02-30", "tick_incident_observed_on"),
        ("tranche", "Invalid Tranche", "tick_incident_tranche"),
        ("role", "planner", "tick_incident_role"),
        ("resource_id", "invalid_resource", "tick_incident_resource_id"),
        ("transport", "invalid.transport", "tick_incident_transport"),
        ("stage", "post_closeout_rehydration", "tick_incident_stage"),
        ("process_severity", "high", "tick_incident_severity"),
        ("candidate_state", "clean", "tick_incident_candidate_state"),
        ("workflow_disposition", "corrected", "tick_incident_workflow_disposition"),
        (
            "recurrence_signature",
            "invalid signature",
            "tick_incident_recurrence_signature",
        ),
        ("causal_claim_level", "root_cause_confirmed", "tick_incident_causal_claim"),
    ],
)
def test_incident_intent_rejects_register_schema_vocabulary_before_projection(
    field: str, value: str, reason: str
) -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    intent = _incident_intent(ROOT)
    intent["agent_error_observations"][0][field] = value
    with pytest.raises(ClockworkTickRejection, match=reason):
        validate_tick_intent(intent, contract)


def test_incident_intent_rejects_correction_status_before_projection() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    intent = _incident_intent(ROOT)
    intent["agent_error_observations"][0]["correction"]["status"] = "corrected"
    with pytest.raises(
        ClockworkTickRejection, match="tick_incident_correction_status"
    ):
        validate_tick_intent(intent, contract)


def test_incident_intent_vocabulary_is_bound_to_register_schema() -> None:
    schema = _json(
        ROOT
        / "orchestration/continuity/ariadne-agent-error-register/agent-error-register.schema.json"
    )
    properties = schema["$defs"]["incident"]["properties"]
    correction = schema["$defs"]["correction"]["properties"]
    assert INCIDENT_ROLES == frozenset(properties["role"]["enum"])
    assert INCIDENT_STAGES == frozenset(properties["stage"]["enum"])
    assert INCIDENT_SEVERITIES == frozenset(properties["process_severity"]["enum"])
    assert INCIDENT_CANDIDATE_STATES == frozenset(
        properties["candidate_state"]["enum"]
    )
    assert INCIDENT_WORKFLOW_DISPOSITIONS == frozenset(
        properties["workflow_disposition"]["enum"]
    )
    assert INCIDENT_CORRECTION_STATUSES == frozenset(correction["status"]["enum"])
    assert INCIDENT_CAUSAL_CLAIM_LEVEL == properties["causal_claim_level"]["const"]
    assert INCIDENT_TRANCHE.pattern == properties["tranche"]["pattern"]
    assert INCIDENT_RESOURCE.pattern == properties["resource_id"]["pattern"]
    assert INCIDENT_TRANSPORT.pattern == properties["transport"]["pattern"]
    assert (
        INCIDENT_RECURRENCE.pattern
        == properties["recurrence_signature"]["pattern"]
    )


def test_blocked_intent_is_closed_and_rejects_hostile_fields() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    baseline = _blocked_intent(ROOT)
    assert validate_blocked_tick_intent(baseline, contract) == baseline
    derived = json.loads(json.dumps(baseline))
    derived["source_commit"] = "a" * 40
    with pytest.raises(ClockworkTickRejection, match="blocked_tick_intent_keys"):
        validate_blocked_tick_intent(derived, contract)
    wrong_operation = json.loads(json.dumps(baseline))
    wrong_operation["operation_id"] = "INVALID"
    with pytest.raises(ClockworkTickRejection, match="blocked_tick_operation_id"):
        validate_blocked_tick_intent(wrong_operation, contract)
    blank_reason = json.loads(json.dumps(baseline))
    blank_reason["user_attention_reason"] = ""
    with pytest.raises(ClockworkTickRejection, match="blocked_tick_attention_reason"):
        validate_blocked_tick_intent(blank_reason, contract)


def test_user_decision_intent_is_closed_and_rejects_derived_or_underbounded_input() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    baseline = _json(DECISION_INTENT_PATH)
    assert validate_user_decision_tick_intent(baseline, contract) == baseline
    generic_descendant = json.loads(json.dumps(baseline))
    generic_descendant["selected_outcome"] = "replace_with_newly_frozen_descendant"
    assert (
        validate_user_decision_tick_intent(generic_descendant, contract)
        == generic_descendant
    )
    derived = json.loads(json.dumps(baseline))
    derived["source_head"] = "a" * 40
    with pytest.raises(
        ClockworkTickRejection, match="user_decision_tick_intent_keys"
    ):
        validate_user_decision_tick_intent(derived, contract)
    wrong_outcome = json.loads(json.dumps(baseline))
    wrong_outcome["selected_outcome"] = "repeat_blocked_transport"
    with pytest.raises(
        ClockworkTickRejection, match="user_decision_selected_outcome"
    ):
        validate_user_decision_tick_intent(wrong_outcome, contract)
    underbounded = json.loads(json.dumps(baseline))
    underbounded["next_operation_protected_boundaries"].remove(
        "explicit_path_staging_only"
    )
    with pytest.raises(
        ClockworkTickRejection, match="user_decision_next_boundaries_floor"
    ):
        validate_user_decision_tick_intent(underbounded, contract)


def test_checkpoint_intent_is_closed_and_rejects_derived_or_no_progress_input() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    baseline = _checkpoint_intent(ROOT)
    assert validate_checkpoint_tick_intent(baseline, contract) == baseline
    derived = json.loads(json.dumps(baseline))
    derived["source_head"] = "a" * 40
    with pytest.raises(ClockworkTickRejection, match="checkpoint_tick_intent_keys"):
        validate_checkpoint_tick_intent(derived, contract)
    invalid = json.loads(json.dumps(baseline))
    invalid["operation_id"] = "INVALID"
    with pytest.raises(ClockworkTickRejection, match="checkpoint_tick_operation_id"):
        validate_checkpoint_tick_intent(invalid, contract)


def test_generation_rejects_all_prospective_header_defects_before_mutation(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "prospective-errors") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _replay_intent(worktree)
        evidence = intent["transaction_manifest"]["node"]["evidence"]
        plan_path = worktree / evidence["plans"][0]
        closeout_path = worktree / evidence["closeouts"][0]
        plan_path.write_text(
            "# Plan\n\nDate: not-a-date\n",
            encoding="utf-8",
            newline="\n",
        )
        closeout_path.write_text(
            "# Closeout\n\n"
            "Date: 2026-08-22\n\n"
            "Timestamp: 2026-08-23T00:00:00+11:00 (Australia/Brisbane)\n",
            encoding="utf-8",
            newline="\n",
        )
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {
            key: path.read_bytes() for key, path in canonical_paths.items()
        }
        before_metadata = {
            key: path.read_bytes() for key, path in metadata_paths.items()
        }
        before_pointer = pointer_path.read_bytes()

        with pytest.raises(
            ClockworkTickRejection,
            match="tick_prospective_current_node_evidence",
        ) as caught:
            build_tick_generation(worktree, contract, intent)

        rejection = str(caught.value)
        assert f"{evidence['plans'][0]}:date_invalid" in rejection
        assert f"{evidence['plans'][0]}:timestamp_count" in rejection
        assert f"{evidence['closeouts'][0]}:offset_not_brisbane" in rejection
        assert f"{evidence['closeouts'][0]}:calendar_date_mismatch" in rejection
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata
        assert pointer_path.read_bytes() == before_pointer


def test_reviewed_fixture_generation_is_preparable(tmp_path: Path) -> None:
    with _worktree(tmp_path / "selected-or-prepared") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        before = validate_live_state(worktree, contract)
        prepared = build_tick_generation(
            worktree, contract, _replay_intent(worktree)
        )
        graph = json.loads(prepared["canonical"]["continuity"].decode("utf-8"))
        compass = json.loads(prepared["canonical"]["compass"].decode("utf-8"))
        latch = json.loads(prepared["canonical"]["active_latch"].decode("utf-8"))
        assert prepared["pointer"]["previous_generation_id"] == before["generation_id"]
        assert prepared["pointer"]["lease_sequence"] == before["lease_sequence"] + 1
        assert graph["graph_revision"] == 332
        assert compass["map_revision"] == 314
        assert latch["operation_id"] == "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture"
        assert latch["protected_boundaries"] == prepared["intent"]["next_operation_protected_boundaries"]
        assert prepared["generation_manifest"]["source_commit"] == REPLAY_FIXTURE_SOURCE


def test_clean_closeout_rejects_a_successor_already_recorded_in_graph(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "recorded-successor") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _replay_intent(worktree)
        graph = _json(
            worktree / "orchestration/continuity/emr4-continuity-graph.json"
        )
        intent["transaction_manifest"]["next_operation"]["operation_id"] = graph[
            "nodes"
        ][-1]["id"]
        with pytest.raises(
            ClockworkTickRejection,
            match="tick_next_operation_already_recorded",
        ):
            build_tick_generation(worktree, contract, intent)


def test_incident_tick_derives_register_pattern_and_rolls_back_atomically(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "incident-intake") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _incident_intent(worktree)
        _commit_incident_revision_artifact(worktree, intent)
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {
            key: path.read_bytes() for key, path in canonical_paths.items()
        }
        before_metadata = {
            key: path.read_bytes() for key, path in metadata_paths.items()
        }
        before_pointer = pointer_path.read_bytes()
        previous_register = json.loads(before_canonical["error_register"])
        prepared = build_tick_generation(worktree, contract, intent)
        register = json.loads(prepared["canonical"]["error_register"])
        pattern = json.loads(prepared["canonical"]["pattern_report"])
        transaction = json.loads(prepared["metadata"]["transaction.json"])
        baton = prepared["canonical"]["current_baton"].decode("utf-8")
        next_number = int(
            previous_register["incidents"][-1]["incident_id"].split("-")[1]
        ) + 1
        assert register["register_revision"] == previous_register["register_revision"] + 1
        assert len(register["incidents"]) == len(previous_register["incidents"]) + 1
        assert register["incidents"][-1]["incident_id"] == f"AER-{next_number:04d}"
        assert register["incidents"][-1]["origin"] == "agent_behavior"
        assert register["incidents"][-1]["related_incident_ids"] == []
        assert pattern["register_revision"] == register["register_revision"]
        assert pattern["incident_count"] == len(register["incidents"])
        assert transaction["register_bytes_preserved"] is False
        assert transaction["pattern_bytes_preserved"] is False
        assert f"AER-{next_number:04d} preserves the rejected" in baton
        with pytest.raises(OSError, match="injected_tick_precommit_failure"):
            publish_tick_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="after:error_register",
            )
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata
        assert pointer_path.read_bytes() == before_pointer
        active = publish_tick_generation(worktree, prepared, writer_id="clockwork")
        assert active["status"] == "passed"
        assert validate_tick_live_state(worktree, contract)["status"] == "passed"
        rolled_back = rollback_tick_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical


def test_incident_tick_rejects_stale_human_revision_reading(tmp_path: Path) -> None:
    with _worktree(tmp_path / "stale-incident-revision") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _incident_intent(worktree)
        _commit_incident_revision_artifact(
            worktree, intent, incident_count_adjustment=-1
        )
        with pytest.raises(
            ClockworkTickRejection, match="tick_incident_revision_reading"
        ):
            build_tick_generation(worktree, contract, intent)


def test_blocked_tick_preserves_every_non_latch_surface_and_rolls_back(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "blocked-transition") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _blocked_intent(worktree)
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {
            key: path.read_bytes() for key, path in canonical_paths.items()
        }
        before_metadata = {
            key: path.read_bytes() for key, path in metadata_paths.items()
        }
        before_pointer = pointer_path.read_bytes()
        prepared = build_blocked_tick_generation(worktree, contract, intent)
        latch = json.loads(
            prepared["canonical"]["active_latch"].decode("utf-8")
        )
        assert latch["status"] == "blocked"
        assert latch["source_head"] == _json(
            worktree
            / "orchestration/continuity/ariadne-active-operation-latch/current.json"
        )["source_head"]
        assert latch["checkpoint"]["next_executable_stage"] is None
        assert latch["user_attention"]["required"] is True
        assert latch["terminal_response"]["permitted"] is True
        assert {
            key
            for key in CANONICAL_KEYS
            if prepared["canonical"][key] != before_canonical[key]
        } == {"active_latch"}
        with pytest.raises(OSError, match="injected_tick_precommit_failure"):
            publish_tick_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="before_pointer_replace",
            )
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata
        assert pointer_path.read_bytes() == before_pointer
        active = publish_tick_generation(
            worktree, prepared, writer_id="clockwork"
        )
        assert active["event_kind"] == "blocked_transition"
        assert active["operation_id"] == intent["operation_id"]
        assert publish_tick_generation(
            worktree, prepared, writer_id="clockwork"
        )["generation_id"] == active["generation_id"]
        rolled_back = rollback_tick_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata
        restored_pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        original_pointer = json.loads(before_pointer.decode("utf-8"))
        assert restored_pointer["selected_generation_id"] == original_pointer[
            "selected_generation_id"
        ]
        assert restored_pointer["selected_bundle_sha256"] == original_pointer[
            "selected_bundle_sha256"
        ]
        assert restored_pointer["lease_sequence"] == (
            original_pointer["lease_sequence"] + 2
        )


def test_user_decision_tick_replaces_blocked_latch_and_only_updates_baton(
    tmp_path: Path,
) -> None:
    with _worktree(
        tmp_path / "user-decision-transition", BLOCKED_REPLAY_FIXTURE_SOURCE
    ) as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _user_decision_intent(worktree)
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {
            key: path.read_bytes() for key, path in canonical_paths.items()
        }
        before_metadata = {
            key: path.read_bytes() for key, path in metadata_paths.items()
        }
        before_pointer = pointer_path.read_bytes()
        prepared = build_user_decision_tick_generation(worktree, contract, intent)
        latch = json.loads(prepared["canonical"]["active_latch"].decode("utf-8"))
        baton = prepared["canonical"]["current_baton"].decode("utf-8")
        assert latch["operation_id"] == REDESIGN_OPERATION_ID
        assert latch["status"] == "in_progress"
        assert latch["source_head"] == BLOCKED_REPLAY_FIXTURE_SOURCE
        assert latch["user_attention"] == {"required": False, "reason": None}
        assert latch["terminal_response"] == {
            "permitted": False,
            "reason": "unfinished_authorized_operation",
        }
        assert REDESIGN_OPERATION_ID in baton
        assert "user-decision transition" in baton
        assert {
            key
            for key in CANONICAL_KEYS
            if prepared["canonical"][key] != before_canonical[key]
        } == {"active_latch", "current_baton"}
        with pytest.raises(OSError, match="injected_tick_precommit_failure"):
            publish_tick_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="before_pointer_replace",
            )
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata


        assert pointer_path.read_bytes() == before_pointer
        active = publish_tick_generation(
            worktree, prepared, writer_id="clockwork"
        )
        assert active["event_kind"] == "user_decision_transition"
        assert active["operation_id"] == REDESIGN_OPERATION_ID
        assert publish_tick_generation(
            worktree, prepared, writer_id="clockwork"
        )["generation_id"] == active["generation_id"]
        rolled_back = rollback_tick_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata


def test_checkpoint_tick_advances_stage_and_is_pointer_last_recoverable(
    tmp_path: Path,
) -> None:
    with _worktree(
        tmp_path / "checkpoint-transition", CHECKPOINT_REPLAY_FIXTURE_SOURCE
    ) as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _checkpoint_intent(worktree)
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {
            key: path.read_bytes() for key, path in canonical_paths.items()
        }
        before_metadata = {
            key: path.read_bytes() for key, path in metadata_paths.items()
        }
        before_pointer = pointer_path.read_bytes()
        prepared = build_checkpoint_tick_generation(worktree, contract, intent)
        latch = json.loads(prepared["canonical"]["active_latch"].decode("utf-8"))
        baton = prepared["canonical"]["current_baton"].decode("utf-8")
        assert latch["operation_id"] == REDESIGN_OPERATION_ID
        assert latch["status"] == "in_progress"
        assert latch["source_head"] == CHECKPOINT_REPLAY_FIXTURE_SOURCE
        assert (
            latch["checkpoint"]["next_executable_stage"]
            == intent["next_executable_stage"]
        )
        assert "in-progress checkpoint" in baton
        assert {
            key
            for key in CANONICAL_KEYS
            if prepared["canonical"][key] != before_canonical[key]
        } == {"active_latch", "current_baton"}
        with pytest.raises(OSError, match="injected_tick_precommit_failure"):
            publish_tick_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="before_pointer_replace",
            )
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata
        assert pointer_path.read_bytes() == before_pointer
        active = publish_tick_generation(
            worktree, prepared, writer_id="clockwork"
        )
        assert active["event_kind"] == "checkpoint_transition"
        assert active["operation_id"] == REDESIGN_OPERATION_ID
        assert publish_tick_generation(
            worktree, prepared, writer_id="clockwork"
        )["generation_id"] == active["generation_id"]
        rolled_back = rollback_tick_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {
            key: path.read_bytes() for key, path in canonical_paths.items()
        } == before_canonical
        assert {
            key: path.read_bytes() for key, path in metadata_paths.items()
        } == before_metadata


def test_git_clean_line_ending_variation_does_not_change_tick(tmp_path: Path) -> None:
    with _worktree(tmp_path / "line-endings") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _replay_intent(worktree)
        expected = build_tick_generation(worktree, contract, intent)
        baton = worktree / contract["canonical_paths"]["current_baton"]
        baton.write_bytes(baton.read_bytes().replace(b"\n", b"\r\n"))
        assert subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(baton)], cwd=worktree
        ).returncode == 0
        observed = build_tick_generation(worktree, contract, intent)
        assert observed["generation_manifest"] == expected["generation_manifest"]
        assert observed["canonical"] == expected["canonical"]


def test_all_pre_pointer_faults_restore_and_rollback_is_exact(tmp_path: Path) -> None:
    with _worktree(tmp_path / "faults") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _replay_intent(worktree)
        prepared = build_tick_generation(worktree, contract, intent)
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {key: path.read_bytes() for key, path in canonical_paths.items()}
        before_metadata = {key: path.read_bytes() for key, path in metadata_paths.items()}
        before_pointer = pointer_path.read_bytes()
        checkpoints = [
            point
            for key in CANONICAL_KEYS
            for point in (f"before:{key}", f"after:{key}")
        ] + [
            point
            for name in (*METADATA_NAMES, "generation-manifest.json")
            for point in (f"before:{name}", f"after:{name}")
        ] + ["before_pointer_replace"]
        for checkpoint in checkpoints:
            with pytest.raises(OSError, match="injected_tick_precommit_failure"):
                publish_tick_generation(
                    worktree,
                    prepared,
                    writer_id="clockwork",
                    fail_at=checkpoint,
                )
            assert {key: path.read_bytes() for key, path in canonical_paths.items()} == before_canonical
            assert {key: path.read_bytes() for key, path in metadata_paths.items()} == before_metadata
            assert pointer_path.read_bytes() == before_pointer
            assert not (pointer_path.parent / "writer.lock").exists()
        active = publish_tick_generation(worktree, prepared, writer_id="clockwork")
        assert active["operation_id"] == "raisa-provider-free-clockwork-governed-check-in-successor-resolution"
        assert publish_tick_generation(worktree, prepared, writer_id="clockwork")["generation_id"] == active["generation_id"]
        rolled_back = rollback_tick_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {key: path.read_bytes() for key, path in canonical_paths.items()} == before_canonical
        assert {key: path.read_bytes() for key, path in metadata_paths.items()} == before_metadata
        assert validate_live_state(worktree, contract)["generation_id"] == prepared["base_pointer"]["selected_generation_id"]


def test_post_pointer_failure_is_committed_and_stale_predecessor_fails(tmp_path: Path) -> None:
    with _worktree(tmp_path / "post-pointer") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        prepared = build_tick_generation(
            worktree, contract, _replay_intent(worktree)
        )
        stale = json.loads(json.dumps(prepared["base_pointer"]))
        pointer_path = worktree / contract["clockwork_root"] / "current.json"
        stale["lease_sequence"] += 1
        pointer_path.write_text(json.dumps(stale, indent=2) + "\n", encoding="utf-8", newline="\n")
        with pytest.raises(ClockworkTickRejection, match="tick_stale_predecessor"):
            publish_tick_generation(worktree, prepared, writer_id="clockwork")
        pointer_path.write_text(json.dumps(prepared["base_pointer"], indent=2) + "\n", encoding="utf-8", newline="\n")
        with pytest.raises(ClockworkTickRejection, match="tick_writer_not_clockwork"):
            publish_tick_generation(worktree, prepared, writer_id="legacy", fail_at=None)
        with pytest.raises(CommittedClockworkTick, match="injected_tick_postcommit_failure"):
            publish_tick_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="after_pointer_replace",
            )
        assert validate_tick_live_state(worktree, contract)["status"] == "passed"
