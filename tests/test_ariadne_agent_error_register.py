from __future__ import annotations

import copy
import json
from pathlib import Path

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


def test_committed_register_is_closed_and_semantically_valid() -> None:
    register = _register()

    validate_register(register, _schema())

    assert register["schema_version"] == "ariadne.agent-error-register.v1"
    assert register["register_revision"] == 4
    assert register["scope"]["coverage"] == "bounded_known_preserved_incidents"
    assert [row["incident_id"] for row in register["incidents"]] == [
        f"AER-{index:04d}" for index in range(1, 12)
    ]
    assert all(row["status"] != "open" for row in register["incidents"])


def test_seed_separates_agent_behavior_from_transport() -> None:
    incidents = _register()["incidents"]
    agent_incidents = [row for row in incidents if row["origin"] == "agent_behavior"]
    transport_incidents = [row for row in incidents if row["origin"] == "transport"]

    assert len(agent_incidents) == 9
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


def test_duplicate_decision_is_the_only_seeded_recurring_signature() -> None:
    report = build_pattern_report()

    assert report["incident_count"] == 11
    assert report["open_incident_ids"] == []
    assert report["counts"]["by_origin"] == {
        "agent_behavior": 9,
        "harness": 1,
        "transport": 1,
    }
    assert report["counts"]["by_category"] == {
        "command_scope_violation": 2,
        "evidence_misreport": 1,
        "harness_failure": 1,
        "output_contract_violation": 4,
        "read_only_violation": 1,
        "reasoning_claim_error": 1,
        "transport_timeout": 1,
    }
    assert report["counts"]["by_candidate_state"] == {
        "canonical_unchanged": 9,
        "untrusted_partial_worktree": 2,
    }
    assert report["recurring_patterns"] == [
        {
            "recurrence_signature": "verifier.multiple_terminal_decisions",
            "incident_count": 2,
            "incident_ids": ["AER-0004", "AER-0006"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "The verifier wrapper admits exactly one terminal decision and rejects zero or duplicate terminal envelopes before acceptance.",
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

    assert report["recurring_patterns"][0]["incident_ids"] == [
        "AER-0004",
        "AER-0006",
    ]
    assert report["recurring_patterns"][0]["incident_count"] == 2


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
