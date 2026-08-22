from __future__ import annotations

import json
import subprocess
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
    TICK_INCIDENT_INTENT_VERSION,
    USER_DECISION_INTENT_VERSION,
    CommittedClockworkTick,
    ClockworkTickRejection,
    PREDECESSOR_METADATA_NAMES,
    build_blocked_tick_generation,
    build_checkpoint_tick_generation,
    build_tick_generation,
    build_user_decision_tick_generation,
    publish_tick_generation,
    rollback_tick_generation,
    validate_blocked_tick_intent,
    validate_checkpoint_tick_intent,
    validate_tick_intent,
    validate_tick_live_state,
    validate_user_decision_tick_intent,
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
    _is_exact_published_intent,
    _write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement/contract.json"
TOPIC = ROOT / "orchestration/continuity/raisa-provider-free-clockwork-governed-check-in-successor-resolution"
INTENT_PATH = TOPIC / "closeout-intent.json"
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
    }
    _write_outputs(tmp_path, result, prefix="clockwork-checkpoint-tick")
    assert (tmp_path / "clockwork-checkpoint-tick-evidence.json").is_file()
    report = tmp_path / "clockwork-checkpoint-tick-report.md"
    assert report.is_file()
    assert "Lease sequence: 8" in report.read_text(encoding="utf-8")


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
        "no_product_patient_appointment_clinical_historical_or_protected_data",
    ):
        underbounded = json.loads(json.dumps(baseline))
        underbounded["next_operation_protected_boundaries"].remove(boundary)
        with pytest.raises(
            ClockworkTickRejection, match="tick_next_boundaries_floor"
        ):
            validate_tick_intent(underbounded, contract)


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
