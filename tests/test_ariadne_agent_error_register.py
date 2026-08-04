from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest
import yaml
from jsonschema import ValidationError

from scripts.ariadne_agent_error_register import (
    REGISTER_PATH,
    ROOT,
    SCHEMA_PATH,
    build_pattern_report,
    validate_register,
    write_json_lf,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _register() -> dict:
    return _json(REGISTER_PATH)


def _schema() -> dict:
    return _json(SCHEMA_PATH)


def test_committed_register_is_semantically_valid_with_pending_checkout_fix() -> None:
    register = _register()

    validate_register(register, _schema())

    assert register["schema_version"] == "ariadne.agent-error-register.v1"
    assert register["register_revision"] == 11
    assert register["scope"]["coverage"] == "bounded_known_preserved_incidents"
    assert [row["incident_id"] for row in register["incidents"]] == [
        f"AER-{index:04d}" for index in range(1, 20)
    ]
    assert [
        row["incident_id"]
        for row in register["incidents"]
        if row["status"] == "open"
    ] == ["AER-0017", "AER-0019"]


def test_seed_separates_agent_behavior_from_transport() -> None:
    incidents = _register()["incidents"]
    agent_incidents = [row for row in incidents if row["origin"] == "agent_behavior"]
    transport_incidents = [row for row in incidents if row["origin"] == "transport"]

    assert len(agent_incidents) == 14
    assert len(transport_incidents) == 1
    assert transport_incidents[0]["incident_id"] == "AER-0007"
    assert transport_incidents[0]["category"] == "transport_timeout"
    assert transport_incidents[0]["role"] == "implementer"
    assert transport_incidents[0]["causal_claim_level"] == "observation_only"
    assert transport_incidents[0]["candidate_state"] == "untrusted_partial_worktree"


def test_davida_review_errors_match_preserved_evidence() -> None:
    register = _register()
    rows = {row["incident_id"]: row for row in register["incidents"]}
    first_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "davida-default-location-dry-run-gemini-review-receipt.json"
    )
    corrected_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "davida-default-location-dry-run-gemini-review-receipt-2.json"
    )
    evidence = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "davida-provider-free-practice-administration-default-location-dry-run"
        / "provider-free-acceptance-evidence.json"
    )

    assert "--output orchestration" in first_receipt["result"]
    assert "25/25 acceptance cases passed" in first_receipt["result"]
    assert evidence["case_count"] == 60
    assert evidence["passed_case_count"] == 60
    assert "Total Cases Recorded:** 60" in corrected_receipt["result"]
    assert rows["AER-0001"]["category"] == "command_scope_violation"
    assert rows["AER-0002"]["category"] == "evidence_misreport"
    assert rows["AER-0001"]["related_incident_ids"] == ["AER-0002"]
    assert rows["AER-0002"]["related_incident_ids"] == ["AER-0001"]


def test_pattern_report_detects_both_recurring_control_signals() -> None:
    report = build_pattern_report()

    assert report["incident_count"] == 19
    assert report["open_incident_ids"] == ["AER-0017", "AER-0019"]
    assert report["counts"]["by_origin"] == {
        "agent_behavior": 14,
        "harness": 3,
        "repository": 1,
        "transport": 1,
    }
    assert report["counts"]["by_category"] == {
        "command_scope_violation": 2,
        "evidence_misreport": 2,
        "harness_failure": 3,
        "output_contract_violation": 8,
        "read_only_violation": 1,
        "reasoning_claim_error": 1,
        "repository_defect": 1,
        "transport_timeout": 1,
    }
    assert report["counts"]["by_candidate_state"] == {
        "accepted_candidate_changed": 1,
        "canonical_unchanged": 16,
        "untrusted_partial_worktree": 2,
    }
    assert report["recurring_patterns"] == [
        {
            "recurrence_signature": "orchestrator.detached_verifier_branch",
            "incident_count": 2,
            "incident_ids": ["AER-0012", "AER-0014"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Verifier setup must validate a non-empty non-protected codex/review branch and exact candidate HEAD before issuing the pre-verifier receipt or invoking Antigravity.",
                "scripts/ariadne_verifier_worktree_preflight.py must pass on the exact candidate and codex/review branch before a pre-verifier receipt or Antigravity launch; policy ordering and tests enforce the gate."
            ],
        },
        {
            "recurrence_signature": "verifier.multiple_terminal_decisions",
            "incident_count": 3,
            "incident_ids": ["AER-0004", "AER-0006", "AER-0018"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "The verifier wrapper admits exactly one terminal decision and rejects zero or duplicate terminal envelopes before acceptance.",
                "The verifier wrapper must continue exact-single-decision admission; duplicate output never becomes a verdict, and bounded recovery uses a fresh project/worktree without changing candidate scope.",
                "The wrapper regex counts terminal decisions and rejects any count other than one; tests cover missing and duplicate decisions."
            ],
        }
    ]
    assert "do not prove model" in report["interpretation_boundary"]


def test_native_reviewer_environment_bootstrap_is_separate_and_contained() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0011"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["resource_id"] == "codex-native-independent-reviewer"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "verifier.unapproved_environment_bootstrap"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert incident["status"] == "contained"


def test_detached_antigravity_preflight_is_orchestrator_not_provider_error() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0012"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["resource_id"] == "codex-primary-orchestrator"
    assert incident["model"] is None
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.detached_verifier_branch"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_unapproved_acceptance_event_failed_closed_before_corrected_receipt() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0013"]
    failed_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-architecture-preacceptance-receipt.json"
    )
    corrected_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-architecture-pre-verifier-acceptance-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.unapproved_continuation_event"
    )
    assert failed_receipt["continuation_event"] == "pre_acceptance"
    assert failed_receipt["status"] == "revision_required"
    assert failed_receipt["worker_dispatch_permitted"] is False
    assert failed_receipt["rehydrated_from_receipt"] is False
    assert corrected_receipt["continuation_event"] == "pre_verifier_acceptance"
    assert corrected_receipt["status"] == "passed"
    assert corrected_receipt["rehydrated_from_receipt"] is True


def test_recurrent_detached_branch_activates_pre_receipt_control() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    first = incidents["AER-0012"]
    recurrence = incidents["AER-0014"]
    preflight = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-gate-minus-one-verifier-worktree-preflight.json"
    )
    policy = yaml.safe_load(
        (
            ROOT
            / "orchestration"
            / "harness_settings"
            / "verifier_execution_policy.yaml"
        ).read_text(encoding="utf-8")
    )

    assert first["recurrence_signature"] == recurrence["recurrence_signature"]
    assert recurrence["correction"]["status"] == "control_added"
    assert preflight["status"] == "passed"
    assert preflight["clean"] is True
    assert preflight["branch"].startswith("codex/review-")
    assert policy["execution_order"][0] == "verifier_worktree_preflight"
    assert policy["deterministic_gate"]["required_results"][
        "verifier_worktree_preflight"
    ] == "passed"


def test_gate_minus_one_review_transport_claim_is_corrected_fresh() -> None:
    incident = {
        row["incident_id"]: row for row in _register()["incidents"]
    }["AER-0015"]
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-gate-minus-one-review-claim-failure-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-gate-minus-one-review-2-receipt.json"
    )

    assert incident["category"] == "evidence_misreport"
    assert incident["recurrence_signature"] == (
        "verifier.review_transport_misreported_as_zero"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert failure["raw_receipt_sha256"] == (
        "9a5ed7c38fd21ddd2d9616730fc5fd584684e058c4021e6c3e405abe288e8ec5"
    )
    assert "review itself invoked Gemini" in failure["conflict"]
    assert failure["decision_admitted"] is False
    assert failure["candidate_changed"] is False
    assert corrected["decision"] == "pass"
    assert corrected["head_before"] == corrected["head_after"] == (
        "2b62f040bcc1c300dca6fb730e0f986d22f3be85"
    )
    assert corrected["dirty_after"] is False
    assert "Candidate Product/Runtime Side Effects (Observed): Exactly 0" in (
        corrected["result"]
    )
    assert "Development Review Transport (Observed): Non-Zero" in corrected["result"]
    assert "invoked `gemini-3.6-flash-high`" in corrected["result"]


def test_a3_b3_preflight_reservation_failure_has_hash_bound_resume_control() -> None:
    incident = {
        row["incident_id"]: row for row in _register()["incidents"]
    }["AER-0016"]
    blocked = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "model-required-bureau-a3-b3"
        / "occupied-preflight-blocked-evidence.json"
    )

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["recurrence_signature"] == (
        "harness.preflight_blocked_cost_reservation_orphaned"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"
    assert blocked["reason_code"] == "impersonated_adc_refresh_failed"
    assert blocked["provider_call_count"] == 0
    assert blocked["cost_reservation"]["provider_calls_reserved"] == 1
    assert blocked["cost_reservation"]["provider_calls_consumed"] == 0


def test_a3_b3_terminal_broker_failure_has_evidence_only_recovery() -> None:
    incident = {
        row["incident_id"]: row for row in _register()["incidents"]
    }["AER-0017"]
    interruption = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "model-required-bureau-a3-b3"
        / "occupied-terminal-interruption-evidence.json"
    )

    assert incident["origin"] == "harness"
    assert incident["model"] is None
    assert incident["category"] == "harness_failure"
    assert incident["recurrence_signature"] == (
        "harness.postcall_terminal_evidence_and_parent_consumption_split"
    )
    assert incident["status"] == "open"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert interruption["reason_code"] == "provider_content_invalid"
    assert interruption["provider_call_count"] == 1
    assert interruption["proofreader_reached"] is False
    assert interruption["correction_eligible"] is False
    assert interruption["release_created"] is False
    assert interruption["davida_b3_started"] is False
    assert interruption["cause_beyond_structural_failure_established"] is False


def test_a3_b3_review_7_duplicate_decision_is_contained() -> None:
    incident = {
        row["incident_id"]: row for row in _register()["incidents"]
    }["AER-0018"]
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-a3-b3-review-7-transport-failure.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == (
        "verifier.multiple_terminal_decisions"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert failure["observed_terminal_decision_count"] == 2
    assert failure["candidate_finding_established"] is False
    assert failure["candidate_runtime_provider_calls"] == 0
    assert failure["worktree_clean_after"] is True
    assert failure["worktree_head_after"] == failure["candidate_head"]
    assert failure["raw_verifier_output_retained"] is False


def test_a3_b3_hashed_audit_checkout_is_lf_pinned() -> None:
    relative = (
        "orchestration/continuity/model-required-bureau-a3-b3/"
        "rayleen-a3-attempt-1-occupied-audit.jsonl"
    )
    audit_bytes = (ROOT / relative).read_bytes()
    interruption = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "model-required-bureau-a3-b3"
        / "occupied-terminal-interruption-evidence.json"
    )
    attribute = subprocess.run(
        ["git", "check-attr", "eol", "--", relative],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )

    assert attribute.stdout.strip().endswith(": eol: lf")
    assert b"\r\n" not in audit_bytes
    assert "sha256:" + hashlib.sha256(audit_bytes).hexdigest() == (
        interruption["source_artifact_hashes"]["audit_chain"]
    )


def test_a3_b3_review_8_checkout_defect_is_registered() -> None:
    incident = {
        row["incident_id"]: row for row in _register()["incidents"]
    }["AER-0019"]
    review = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-a3-b3-review-8-receipt.json"
    )

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.hash_bound_jsonl_checkout_line_ending_drift"
    )
    assert incident["status"] == "open"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert review["decision"] == "revision_required"
    assert review["head_before"] == review["head_after"]
    assert review["dirty_after"] is False


def test_pattern_report_is_byte_deterministic(tmp_path: Path) -> None:
    first = build_pattern_report()
    second = build_pattern_report()
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    write_json_lf(first_path, first)
    write_json_lf(second_path, second)

    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes().endswith(b"\n")
    assert b"\r\n" not in first_path.read_bytes()


def test_register_hash_is_invariant_across_checkout_line_endings(
    tmp_path: Path,
) -> None:
    original = REGISTER_PATH.read_text(encoding="utf-8")
    crlf_path = tmp_path / "register-crlf.json"
    crlf_path.write_bytes(original.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))

    original_report = build_pattern_report()
    crlf_report = build_pattern_report(register_path=crlf_path)

    assert (
        original_report["canonical_register_sha256"]
        == crlf_report["canonical_register_sha256"]
    )


def test_committed_pattern_report_matches_fresh_build() -> None:
    committed = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "ariadne-agent-error-register"
        / "pattern-report.json"
    )

    assert committed == build_pattern_report()


def test_verifier_policy_requires_incident_learning_before_acceptance() -> None:
    policy = yaml.safe_load(
        (
            ROOT
            / "orchestration"
            / "harness_settings"
            / "verifier_execution_policy.yaml"
        ).read_text(encoding="utf-8")
    )
    learning = policy["incident_learning"]

    assert learning["register_before_corrected_attempt_acceptance"] is True
    assert learning["controls"] == {
        "immutable_failure_evidence": "required",
        "correction_linkage": "required",
        "recurrence_threshold": 2,
        "raw_prompts_secrets_and_sensitive_values": "forbidden",
        "model_provider_or_role_causal_claim_without_separate_evidence": "forbidden",
        "candidate_runtime_and_review_transport_claims": "separately_required",
    }
    assert set(learning["origin_classes"]) == {
        "agent_behavior",
        "transport",
        "harness",
        "repository",
        "operator",
    }


def test_duplicate_incident_id_fails_closed() -> None:
    register = _register()
    register["incidents"][1]["incident_id"] = "AER-0001"

    with pytest.raises(ValueError, match="duplicate incident_id"):
        validate_register(register, _schema())


def test_missing_or_out_of_scope_evidence_fails_closed() -> None:
    missing = _register()
    missing["incidents"][0]["evidence_paths"][0] = "docs/not-present.json"
    with pytest.raises(ValueError, match="evidence path is missing"):
        validate_register(missing, _schema())

    branding = _register()
    branding["incidents"][0]["evidence_paths"][0] = "docs/branding/README.md"
    with pytest.raises(ValidationError):
        validate_register(branding, _schema())

    mixed_case_branding = _register()
    mixed_case_branding["incidents"][0]["evidence_paths"][0] = (
        "DOCS/Branding/raisa/README.md"
    )
    with pytest.raises(ValidationError):
        validate_register(mixed_case_branding, _schema())


def test_origin_category_mismatch_fails_closed() -> None:
    register = _register()
    register["incidents"][6]["origin"] = "agent_behavior"

    with pytest.raises(ValueError, match="origin/category mismatch"):
        validate_register(register, _schema())


def test_unknown_sensitive_or_raw_prompt_field_fails_closed() -> None:
    register = _register()
    register["incidents"][0]["raw_prompt"] = "forbidden"

    with pytest.raises(ValidationError):
        validate_register(register, _schema())


def test_unknown_related_incident_and_attempt_peer_linkage_fail_closed() -> None:
    unknown = _register()
    unknown["incidents"][0]["related_incident_ids"] = ["AER-9999"]
    with pytest.raises(ValueError, match="unknown related incident"):
        validate_register(unknown, _schema())

    asymmetric = _register()
    asymmetric["incidents"][1].pop("related_incident_ids")
    with pytest.raises(ValidationError):
        validate_register(asymmetric, _schema())

    omitted = _register()
    omitted["incidents"][0]["related_incident_ids"] = []
    omitted["incidents"][1]["related_incident_ids"] = []
    with pytest.raises(ValueError, match="attempt peer linkage mismatch"):
        validate_register(omitted, _schema())


def test_same_signature_across_different_dimensions_does_not_merge(
    tmp_path: Path,
) -> None:
    register = _register()
    register["incidents"][0]["recurrence_signature"] = (
        "verifier.multiple_terminal_decisions"
    )
    register_path = tmp_path / "register.json"
    register_path.write_text(json.dumps(register), encoding="utf-8")

    report = build_pattern_report(register_path=register_path)

    duplicate_decisions = next(
        item
        for item in report["recurring_patterns"]
        if item["recurrence_signature"] == "verifier.multiple_terminal_decisions"
    )
    assert duplicate_decisions["incident_ids"] == [
        "AER-0004",
        "AER-0006",
        "AER-0018",
    ]
    assert duplicate_decisions["incident_count"] == 3


def test_v1_rejects_unproved_causal_claim_level() -> None:
    register = _register()
    register["incidents"][0]["causal_claim_level"] = "confirmed_process_cause"

    with pytest.raises(ValidationError):
        validate_register(register, _schema())


def test_extra_schema_leaf_is_rejected() -> None:
    register = copy.deepcopy(_register())
    register["scope"]["exhaustive"] = True

    with pytest.raises(ValidationError):
        validate_register(register, _schema())
