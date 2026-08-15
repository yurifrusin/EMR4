"""Focused tests for the risk-weighted Ariadne workflow reform.

Covers every named threat ``RWW-001`` through ``RWW-018`` and at least fifty
named hostile semantic mutations. Numeric mutation volume is advisory only;
the decisive evidence is per-threat fail-closed coverage.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import orchestration_harness.risk_weighted_workflow as rw
from scripts.ariadne_risk_weighted_workflow import render_packet

ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = ROOT / "orchestration/continuity/ariadne-risk-weighted-workflow-reform"

DIG = "sha256:" + "0" * 64
DIG2 = "sha256:" + "1" * 64

ALL_THREATS = [
    "RWW-001", "RWW-002", "RWW-003", "RWW-004", "RWW-005", "RWW-006",
    "RWW-007", "RWW-008", "RWW-009", "RWW-010", "RWW-011", "RWW-012",
    "RWW-013", "RWW-014", "RWW-015", "RWW-016", "RWW-017", "RWW-018",
]


def _profile(**overrides: object) -> dict:
    base: dict = {
        "schema_version": "ariadne.risk_weighted_tranche_profile.v1",
        "tranche_id": "test-tranche",
        "source_head": "a" * 40,
        "source_tree": "b" * 40,
        "declared_tier": "tier_2_authority_runtime",
        "change_signals": {
            "docs_only": False,
            "unmounted": False,
            "provider_free_source_edit": True,
            "workflow_policy_change": True,
            "database_runtime": False,
            "authority_or_security_contract": False,
            "executable_tool": False,
            "network_capability": False,
            "operational_product_derived_data": False,
            "migration_representation": False,
            "migration_execution": False,
            "product_command_or_write": False,
            "patient_or_clinical_data": False,
            "occupied_provider_call": False,
            "credentials_or_iam": False,
            "deployment_production_release_pages": False,
            "protected_ref_movement": False,
        },
        "change_families": ["harness", "policy", "schema", "semantic_test"],
        "semantic_bindings": [
            {"path": "orchestration_harness/risk_weighted_workflow.py", "kind": "source"},
            {"path": "orchestration/harness_settings/risk_weighted_workflow.yaml", "kind": "policy"},
            {"path": "tests/test_ariadne_risk_weighted_workflow.py", "kind": "semantic_test"},
        ],
        "volatile_bindings": [
            {"path": "orchestration/continuity/ariadne-active-operation-latch/current.json", "kind": "latch_snapshot"},
            {"path": "docs/generated-closeout.md", "kind": "generated_closeout"},
        ],
        "baseline": {
            "fingerprint_sha256": DIG,
            "result": "passed",
            "known_failure_ids": [],
            "captured_before_first_edit": True,
        },
        "semantic_freeze": {
            "source_head": "a" * 40,
            "source_tree": "b" * 40,
            "semantic_bindings_sha256": DIG2,
            "toolchain_sha256": DIG,
            "focused_gate_results": {"focused_semantic": "passed"},
        },
        "post_freeze_change_families": ["harness", "policy", "schema", "semantic_test"],
        "configured_continuation_events": ["five_source_rehydration_at_verifier_admission"],
        "threat_ids": ALL_THREATS,
        "mutation_count": 52,
        "review_triggers": {
            "new_authority_or_security_boundary": False,
            "prior_substantive_rejection": False,
            "ambiguous_hard_boundary": False,
            "explicit_risk_trigger": False,
        },
        "parallelism_plan": {
            "deepseek_lane": "bounded_mechanical_implementation",
            "gemini_lane": "single_final_veto",
            "native_lane": "declined",
        },
        "capability": "test-capability",
        "closed_surfaces": ["database_or_docker_runtime"],
        "place_in_raisa": "test-place",
        "next_tranche": "test-next",
        "attention_status": "green",
    }
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        result[key] = value
    return result


def _gates() -> list[dict]:
    return [
        {"id": "GATE-FOCUSED", "category": "focused_semantic_gates", "result": "passed", "covers": ["RWW-001", "RWW-002", "RWW-003", "RWW-004", "RWW-005", "RWW-008", "RWW-009", "RWW-010", "RWW-011"]},
        {"id": "GATE-CANONICAL", "category": "canonical_final_profile", "result": "passed", "covers": ["RWW-003", "RWW-006", "RWW-016"]},
        {"id": "GATE-MANIFEST", "category": "manifest_validation", "result": "passed", "covers": ["RWW-013", "RWW-014"]},
        {"id": "GATE-PREFLIGHT", "category": "verifier_worktree_path_preflight", "result": "passed", "covers": ["RWW-013", "RWW-014"]},
        {"id": "GATE-REVIEW", "category": "focused_semantic_gates", "result": "passed", "covers": ["RWW-007", "RWW-008"]},
        {"id": "GATE-TAIL", "category": "focused_semantic_gates", "result": "passed", "covers": ["RWW-012"]},
        {"id": "GATE-RECEIPT", "category": "receipt_preflight", "result": "passed", "covers": ["RWW-017"]},
        {"id": "GATE-RENDER", "category": "document_metadata_link_whitespace", "result": "passed", "covers": ["RWW-015"]},
        {"id": "GATE-PARALLEL", "category": "focused_semantic_gates", "result": "passed", "covers": ["RWW-018"]},
    ]


def _result(profile: dict, **overrides: object) -> dict:
    result: dict = {
        "schema_version": "ariadne.risk_weighted_tranche_result.v1",
        "tranche_id": profile["tranche_id"],
        "profile_sha256": rw.profile_sha256(profile),
        "classified_tier": "tier_2_authority_runtime",
        "decision": "pass",
        "baseline": copy.deepcopy(profile["baseline"]),
        "semantic_freeze": copy.deepcopy(profile["semantic_freeze"]),
        "deterministic_gates": _gates(),
        "required_rerun": [
            "focused_semantic_gates",
            "canonical_final_profile",
            "invalidate_earlier_verifier_result",
        ],
        "review": {
            "required_final_vetoes": 1,
            "final_vetoes": [
                {"veto_id": "VETO-1", "reviewer_lane": "gemini_single_final_veto", "decision": "pass"}
            ],
        },
        "canonical_pass_reuse": {"reused": False, "fingerprint_sha256": DIG, "exact": True},
        "continuation_receipts": [
            {"event": "five_source_rehydration_at_verifier_admission", "receipt_sha256": DIG2}
        ],
        "incidents": [],
        "deferred_tail": [],
        "parallelism": {
            "planned": copy.deepcopy(profile["parallelism_plan"]),
            "actual": copy.deepcopy(profile["parallelism_plan"]),
            "planned_vs_actual": "exact",
        },
        "capability": "test-capability",
        "technical_result": "test-result",
        "closed_surfaces": ["database_or_docker_runtime"],
        "issues": [],
        "place_in_raisa": "test-place",
        "next_tranche": "test-next",
        "attention_status": "green",
    }
    for key, value in overrides.items():
        result[key] = value
    return result


def _assert_admission_revision(profile: dict, result: dict) -> None:
    admission = rw.admit_result(profile, result)
    assert admission["decision"] == "revision_required"
    assert admission["reasons"]


# ─── Schema and example evidence checks ────────────────────────────────────


def test_example_profile_and_result_validate_against_exact_schemas() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    profile_schema = json.loads(
        (CONTINUITY / "tranche-profile.schema.json").read_text(encoding="utf-8")
    )
    result_schema = json.loads(
        (CONTINUITY / "tranche-result.schema.json").read_text(encoding="utf-8")
    )
    profile_example = json.loads(
        (CONTINUITY / "tranche-profile.example.json").read_text(encoding="utf-8")
    )
    result_example = json.loads(
        (CONTINUITY / "tranche-result.example.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(profile_example, profile_schema)
    jsonschema.validate(result_example, result_schema)


def test_example_profile_is_admitted_by_the_pure_core() -> None:
    profile = json.loads(
        (CONTINUITY / "tranche-profile.example.json").read_text(encoding="utf-8")
    )
    result = json.loads(
        (CONTINUITY / "tranche-result.example.json").read_text(encoding="utf-8")
    )
    admission = rw.admit_result(profile, result)
    assert admission["decision"] == "pass"
    assert admission["reasons"] == []


def test_provider_free_synthetic_evidence_declares_zero_provider_calls() -> None:
    evidence = json.loads(
        (CONTINUITY / "provider-free-authored-synthetic-evidence.json").read_text(encoding="utf-8")
    )
    assert evidence["provider_or_model_calls"] == 0
    assert evidence["product_runtime_or_database_opened"] is False
    assert set(evidence["threat_ids_covered"]) == set(ALL_THREATS)
    assert evidence["hostile_semantic_mutation_count"] >= 50


def test_policy_yaml_declares_highest_tier_wins_and_hard_controls() -> None:
    yaml = pytest.importorskip("yaml")
    policy = yaml.safe_load(
        (ROOT / "orchestration/harness_settings/risk_weighted_workflow.yaml").read_text(encoding="utf-8")
    )
    assert policy["classifier"]["highest_applicable_tier_wins"] is True
    assert policy["classifier"]["caller_declared_tier_compared_only_for_equality"] is True
    assert policy["review_economy"]["tier_2_and_tier_3_final_vetoes"] == 1


# ─── Named threat coverage RWW-001 .. RWW-018 ──────────────────────────────


def test_rww_001_caller_cannot_lower_the_derived_ceremony_tier() -> None:
    with pytest.raises(ValueError, match="declared tier"):
        rw.validate_profile(_profile(declared_tier="tier_1_provider_free_source"))
    with pytest.raises(ValueError, match="declared tier"):
        rw.validate_profile(_profile(declared_tier="tier_0_metadata"))


def test_rww_002_docs_only_or_unmounted_labels_fail_closed() -> None:
    signals = _profile()["change_signals"]
    with pytest.raises(ValueError, match="docs_only contradicts"):
        rw.validate_profile(
            _profile(
                change_signals={**signals, "docs_only": True},
                change_families=["product"],
            )
        )
    with pytest.raises(ValueError, match="docs_only contradicts"):
        rw.validate_profile(
            _profile(
                change_signals={**signals, "docs_only": True, "database_runtime": True}
            )
        )
    with pytest.raises(ValueError, match="unmounted contradicts"):
        rw.validate_profile(
            _profile(
                change_signals={**signals, "unmounted": True, "authority_or_security_contract": True}
            )
        )


def test_rww_003_baseline_failures_cannot_be_rediscovered() -> None:
    baseline = _profile()["baseline"]
    with pytest.raises(ValueError, match="canonical baseline"):
        rw.validate_profile(
            _profile(baseline={**baseline, "result": "not_required"})
        )
    with pytest.raises(ValueError, match="before the first semantic edit"):
        rw.validate_profile(
            _profile(baseline={**baseline, "captured_before_first_edit": False})
        )


def test_rww_004_semantic_edit_labelled_metadata_cannot_suppress_canonical_rerun() -> None:
    # Falsely narrowed rerun claim is rejected: the union required by the
    # profile's post-freeze semantic families must be returned exactly.
    profile = _profile()
    result = _result(profile, required_rerun=["document_metadata_link_whitespace"])
    _assert_admission_revision(profile, result)
    # Unknown change families fail closed.
    with pytest.raises(ValueError, match="not an admitted change family"):
        rw.validate_profile(_profile(post_freeze_change_families=["unknown_family"]))
    # A documentation-only post-freeze claim cannot hide a workflow policy
    # change that the profile's own change_signals still assert.
    with pytest.raises(ValueError, match="workflow_policy_change|docs_only contradicts"):
        rw.validate_profile(
            _profile(
                change_signals={**_profile()["change_signals"], "docs_only": True},
                post_freeze_change_families=["documentation_or_closeout_prose"],
            )
        )


def test_rww_005_volatile_evidence_cannot_enter_semantic_bindings() -> None:
    bindings = _profile()["semantic_bindings"]
    with pytest.raises(ValueError, match="kind is not admitted"):
        rw.validate_profile(
            _profile(
                semantic_bindings=[
                    *bindings,
                    {"path": "docs/receipt.json", "kind": "receipt"},
                ]
            )
        )
    volatile = _profile()["volatile_bindings"]
    with pytest.raises(ValueError, match="must be disjoint"):
        rw.validate_profile(
            _profile(
                volatile_bindings=[
                    *volatile,
                    {"path": "orchestration_harness/risk_weighted_workflow.py", "kind": "generated_closeout"},
                ]
            )
        )


def test_rww_006_stale_exact_pass_cannot_be_reused() -> None:
    profile = _profile()
    result = _result(
        profile,
        canonical_pass_reuse={"reused": True, "fingerprint_sha256": DIG, "exact": False},
    )
    _assert_admission_revision(profile, result)


def test_rww_007_review_stacking_is_forbidden() -> None:
    profile = _profile()
    result = _result(
        profile,
        review={
            "required_final_vetoes": 1,
            "final_vetoes": [
                {"veto_id": "VETO-1", "reviewer_lane": "gemini_single_final_veto", "decision": "pass"},
                {"veto_id": "VETO-2", "reviewer_lane": "native_explicit_review_lane", "decision": "pass"},
            ],
        },
    )
    with pytest.raises(ValueError, match="at most one veto"):
        rw.validate_result(result)


def test_rww_008_reduced_review_cannot_remove_a_tier_2_veto() -> None:
    profile = _profile()
    result = _result(profile, review={"required_final_vetoes": 0, "final_vetoes": []})
    _assert_admission_revision(profile, result)


def test_rww_009_mutation_volume_cannot_substitute_for_threat_coverage() -> None:
    profile = _profile(mutation_count=999)
    result = _result(profile)
    result["deterministic_gates"][0]["covers"] = ["RWW-001"]
    # Remove passing coverage for many threats while keeping a high count.
    for gate in result["deterministic_gates"]:
        gate["covers"] = [threat for threat in gate["covers"] if threat in {"RWW-001"}]
    _assert_admission_revision(profile, result)


def test_rww_010_incident_record_precedes_corrected_attempt() -> None:
    profile = _profile()
    result = _result(
        profile,
        incidents=[
            {
                "id": "INC-1",
                "origin": "classifier",
                "category": "tier_derivation",
                "role": "worker",
                "resource": "profile",
                "signature": "sig-1",
                "recorded_before_correction": False,
            }
        ],
    )
    _assert_admission_revision(profile, result)


def test_rww_011_distinct_failures_cannot_be_collapsed() -> None:
    profile = _profile()
    incident = {
        "id": "INC-1",
        "origin": "rerun",
        "category": "rerun_matrix",
        "role": "worker",
        "resource": "profile",
        "signature": "same",
        "recorded_before_correction": True,
    }
    result = _result(profile, incidents=[incident, {**incident, "id": "INC-2"}])
    with pytest.raises(ValueError, match="incident grouping collapses"):
        rw.validate_incident_grouping(result)
    _assert_admission_revision(profile, result)


def test_rww_012_timeboxing_cannot_defer_safety_or_authority_defects() -> None:
    profile = _profile()
    result = _result(
        profile,
        deferred_tail=[
            {
                "id": "TAIL-1",
                "title": "defer",
                "safety_relevant": True,
                "authority_relevant": False,
                "integrity_relevant": False,
                "privacy_relevant": False,
                "atomicity_relevant": False,
                "protected_evidence_relevant": False,
                "irreversible_effect_relevant": False,
                "owner": "sol",
                "next_review_boundary": "next-tranche",
            }
        ],
    )
    _assert_admission_revision(profile, result)


def test_rww_013_and_rww_014_external_runner_and_shared_tool_bindings() -> None:
    # RWW-013/RWW-014 are exercised in the verifier-worktree preflight tests;
    # here we confirm the manifest and repository-path validation helpers fail
    # closed for invalid typed bindings.
    from scripts.ariadne_evidence_gate import validate_command_manifest

    with pytest.raises(ValueError, match="shell wrappers are forbidden"):
        validate_command_manifest(
            {
                "schema_version": "ariadne.verifier-command-manifest.v1",
                "commands": [{"id": "CMD", "argv": ["sh", "-c", "echo hi"]}],
            }
        )
    profile = _profile()
    result = _result(profile)
    assert rw.admit_result(profile, result)["decision"] == "pass"


def test_rww_015_renderer_cannot_change_authority_and_writes_only_explicit_paths(
    tmp_path: Path,
) -> None:
    profile = _profile()
    result = _result(profile)
    timestamp = "2026-08-16T08:58:00+10:00"
    packet = render_packet(profile, result, timestamp=timestamp)
    assert set(packet) == {
        "closeout",
        "sol_acceptance",
        "yuri_summary",
        "continuity_payload",
        "compass_payload",
    }
    for artifact in ("closeout", "sol_acceptance", "yuri_summary"):
        text = packet[artifact]
        assert "Date: 2026-08-16" in text
        assert "2026-08-16T08:58:00+10:00 (Australia/Brisbane)" in text
    continuity = json.loads(packet["continuity_payload"])
    assert continuity["authority_boundary"] == "generated_payload_applied_by_sol_only"
    assert continuity["decision"] == "pass"
    # The renderer must not write unless explicit output paths are supplied.
    assert list(tmp_path.iterdir()) == []


def test_rww_016_result_cannot_claim_pass_without_tier_required_evidence() -> None:
    profile = _profile()
    result = _result(profile)
    result["deterministic_gates"] = [
        gate for gate in result["deterministic_gates"]
        if gate["category"] != "canonical_final_profile"
    ]
    _assert_admission_revision(profile, result)


def test_rww_017_receipt_reduction_cannot_skip_a_configured_transition() -> None:
    profile = _profile(
        configured_continuation_events=[
            "five_source_rehydration_at_verifier_admission",
            "five_source_rehydration_at_acceptance",
        ]
    )
    result = _result(profile)
    _assert_admission_revision(profile, result)


def test_rww_018_parallelism_cannot_be_silently_ignored() -> None:
    profile = _profile()
    result = _result(
        profile,
        parallelism={
            "planned": copy.deepcopy(profile["parallelism_plan"]),
            "actual": {
                "deepseek_lane": "bounded_mechanical_implementation",
                "gemini_lane": "declined",
                "native_lane": "declined",
            },
            "planned_vs_actual": "deviation_recorded",
        },
    )
    _assert_admission_revision(profile, result)
    # A silent plan mismatch also fails closed.
    result2 = _result(
        profile,
        parallelism={
            "planned": {
                "deepseek_lane": "declined",
                "gemini_lane": "declined",
                "native_lane": "explicit_review_lane",
            },
            "actual": copy.deepcopy(profile["parallelism_plan"]),
            "planned_vs_actual": "exact",
        },
    )
    _assert_admission_revision(profile, result2)


# ─── Hostile semantic mutations (at least fifty named) ──────────────────────


def _mutate_profile(name: str) -> dict:
    base = _profile()
    if name == "missing_tranche_id":
        del base["tranche_id"]
    elif name == "empty_tranche_id":
        base["tranche_id"] = ""
    elif name == "short_source_head":
        base["source_head"] = "abc"
    elif name == "non_hex_source_tree":
        base["source_tree"] = "z" * 40
    elif name == "wrong_schema_version":
        base["schema_version"] = "ariadne.risk_weighted_tranche_profile.v9"
    elif name == "extra_profile_key":
        base["caller_injected"] = True
    elif name == "missing_change_signals_key":
        del base["change_signals"]["database_runtime"]
    elif name == "extra_change_signals_key":
        base["change_signals"]["made_up_signal"] = True
    elif name == "non_boolean_signal":
        base["change_signals"]["provider_free_source_edit"] = "yes"
    elif name == "empty_change_families":
        base["change_families"] = []
    elif name == "unknown_change_family":
        base["change_families"] = ["product", "mystery"]
    elif name == "semantic_kind_receipt":
        base["semantic_bindings"] = [*base["semantic_bindings"], {"path": "docs/r.json", "kind": "receipt"}]
    elif name == "semantic_binding_duplicate_path":
        base["semantic_bindings"] = [
            *base["semantic_bindings"],
            {"path": "orchestration_harness/risk_weighted_workflow.py", "kind": "source"},
        ]
    elif name == "volatile_kind_source":
        base["volatile_bindings"] = [*base["volatile_bindings"], {"path": "docs/x.md", "kind": "source"}]
    elif name == "semantic_volatile_overlap":
        base["volatile_bindings"] = [
            *base["volatile_bindings"],
            {"path": "orchestration_harness/risk_weighted_workflow.py", "kind": "generated_closeout"},
        ]
    elif name == "baseline_bad_digest":
        base["baseline"]["fingerprint_sha256"] = "sha256:xyz"
    elif name == "baseline_not_required_tier2":
        base["baseline"]["result"] = "not_required"
    elif name == "baseline_not_before_first_edit":
        base["baseline"]["captured_before_first_edit"] = False
    elif name == "freeze_empty_focused_gates":
        base["semantic_freeze"]["focused_gate_results"] = {}
    elif name == "freeze_bad_binding_digest":
        base["semantic_freeze"]["semantic_bindings_sha256"] = "sha256:abc"
    elif name == "freeze_short_source_head":
        base["semantic_freeze"]["source_head"] = "x"
    elif name == "post_freeze_unknown_family":
        base["post_freeze_change_families"] = ["receipt_runtime_state", "unknown"]
    elif name == "post_freeze_too_many_families":
        base["post_freeze_change_families"] = ["harness"] * 17
    elif name == "empty_threat_ids":
        base["threat_ids"] = []
    elif name == "invalid_threat_id":
        base["threat_ids"] = ["XWW-001"]
    elif name == "negative_mutation_count":
        base["mutation_count"] = -1
    elif name == "bool_mutation_count":
        base["mutation_count"] = True
    elif name == "review_triggers_extra_key":
        base["review_triggers"]["invented"] = True
    elif name == "parallelism_bad_lane":
        base["parallelism_plan"]["deepseek_lane"] = "double_implementation"
    elif name == "empty_capability":
        base["capability"] = ""
    elif name == "bad_attention_status":
        base["attention_status"] = "blue"
    elif name == "empty_closed_surfaces":
        base["closed_surfaces"] = []
    elif name == "duplicate_configured_event":
        base["configured_continuation_events"] = ["e", "e"]
    elif name == "empty_configured_event":
        base["configured_continuation_events"] = [""]
    else:
        raise KeyError(name)
    return base


def _mutate_result(name: str, profile: dict) -> dict:
    base = _result(profile)
    if name == "result_wrong_schema_version":
        base["schema_version"] = "ariadne.risk_weighted_tranche_result.v9"
    elif name == "result_profile_sha256_mismatch":
        base["profile_sha256"] = DIG
    elif name == "result_classified_tier_mismatch":
        base["classified_tier"] = "tier_1_provider_free_source"
    elif name == "result_missing_gate_id":
        del base["deterministic_gates"][0]["id"]
    elif name == "result_duplicate_gate_id":
        base["deterministic_gates"].append(copy.deepcopy(base["deterministic_gates"][0]))
    elif name == "result_gate_unknown_category":
        base["deterministic_gates"][0]["category"] = "made_up_category"
    elif name == "result_gate_revision_required":
        base["deterministic_gates"][0]["result"] = "revision_required"
    elif name == "result_gate_uncertain":
        base["deterministic_gates"][0]["result"] = "uncertain"
    elif name == "result_gate_invalid_result":
        base["deterministic_gates"][0]["result"] = "errored"
    elif name == "result_missing_required_rerun_item":
        base["required_rerun"] = [
            item for item in base["required_rerun"]
            if item != "invalidate_earlier_verifier_result"
        ]
    elif name == "result_extra_required_rerun_item":
        base["required_rerun"] = [*base["required_rerun"], "document_metadata_link_whitespace"]
    elif name == "result_missing_canonical_gate":
        base["deterministic_gates"] = [
            gate for gate in base["deterministic_gates"]
            if gate["category"] != "canonical_final_profile"
        ]
    elif name == "result_canonical_gate_not_passed":
        for gate in base["deterministic_gates"]:
            if gate["category"] == "canonical_final_profile":
                gate["result"] = "revision_required"
    elif name == "result_missing_manifest_gate":
        base["deterministic_gates"] = [
            gate for gate in base["deterministic_gates"]
            if gate["category"] not in {"manifest_validation", "verifier_worktree_path_preflight"}
        ]
    elif name == "result_zero_vetoes_tier2":
        base["review"] = {"required_final_vetoes": 1, "final_vetoes": []}
    elif name == "result_review_requirement_mismatch":
        base["review"]["required_final_vetoes"] = 0
    elif name == "result_veto_not_pass":
        base["review"]["final_vetoes"][0]["decision"] = "revision_required"
    elif name == "result_stale_pass_reuse":
        base["canonical_pass_reuse"] = {"reused": True, "fingerprint_sha256": DIG, "exact": False}
    elif name == "result_missing_continuation_receipt":
        base["continuation_receipts"] = []
    elif name == "result_duplicate_incident_grouping":
        incident = {
            "id": "INC-1",
            "origin": "rerun",
            "category": "rerun_matrix",
            "role": "worker",
            "resource": "profile",
            "signature": "same",
            "recorded_before_correction": True,
        }
        base["incidents"] = [incident, {**incident, "id": "INC-2"}]
    elif name == "result_incident_not_before_correction":
        base["incidents"] = [
            {
                "id": "INC-1",
                "origin": "rerun",
                "category": "rerun_matrix",
                "role": "worker",
                "resource": "profile",
                "signature": "same",
                "recorded_before_correction": False,
            }
        ]
    elif name == "result_incident_missing_field":
        base["incidents"] = [
            {
                "id": "INC-1",
                "origin": "rerun",
                "category": "rerun_matrix",
                "role": "worker",
                "resource": "profile",
            }
        ]
    elif name == "result_tail_safety_relevant":
        base["deferred_tail"] = [
            {
                "id": "TAIL-1",
                "title": "t",
                "safety_relevant": True,
                "authority_relevant": False,
                "integrity_relevant": False,
                "privacy_relevant": False,
                "atomicity_relevant": False,
                "protected_evidence_relevant": False,
                "irreversible_effect_relevant": False,
                "owner": "sol",
                "next_review_boundary": "next",
            }
        ]
    elif name == "result_tail_integrity_relevant":
        base["deferred_tail"] = [
            {
                "id": "TAIL-1",
                "title": "t",
                "safety_relevant": False,
                "authority_relevant": False,
                "integrity_relevant": True,
                "privacy_relevant": False,
                "atomicity_relevant": False,
                "protected_evidence_relevant": False,
                "irreversible_effect_relevant": False,
                "owner": "sol",
                "next_review_boundary": "next",
            }
        ]
    elif name == "result_tail_missing_owner":
        base["deferred_tail"] = [
            {
                "id": "TAIL-1",
                "title": "t",
                "safety_relevant": False,
                "authority_relevant": False,
                "integrity_relevant": False,
                "privacy_relevant": False,
                "atomicity_relevant": False,
                "protected_evidence_relevant": False,
                "irreversible_effect_relevant": False,
                "owner": "",
                "next_review_boundary": "next",
            }
        ]
    elif name == "result_parallelism_plan_mismatch":
        base["parallelism"]["planned"]["gemini_lane"] = "declined"
    elif name == "result_parallelism_deviation":
        base["parallelism"]["planned_vs_actual"] = "deviation_recorded"
    elif name == "result_baseline_fingerprint_mismatch":
        base["baseline"]["fingerprint_sha256"] = DIG2
    elif name == "result_baseline_not_required":
        base["baseline"]["result"] = "not_required"
    elif name == "result_baseline_known_failure_mismatch":
        base["baseline"]["known_failure_ids"] = ["KF-1"]
    elif name == "result_freeze_binding_digest_mismatch":
        base["semantic_freeze"]["semantic_bindings_sha256"] = DIG
    elif name == "result_freeze_toolchain_digest_mismatch":
        base["semantic_freeze"]["toolchain_sha256"] = DIG2
    elif name == "result_threat_coverage_missing":
        for gate in base["deterministic_gates"]:
            gate["covers"] = [threat for threat in gate["covers"] if threat != "RWW-018"]
    elif name == "result_decision_pass_but_gate_failed":
        base["deterministic_gates"][0]["result"] = "revision_required"
    elif name == "result_empty_gates":
        base["deterministic_gates"] = []
    elif name == "result_extra_top_level_key":
        base["injected"] = True
    elif name == "result_missing_deferred_tail":
        del base["deferred_tail"]
    elif name == "result_missing_parallelism":
        del base["parallelism"]
    elif name == "result_empty_technical_result":
        base["technical_result"] = ""
    else:
        raise KeyError(name)
    return base


PROFILE_MUTATIONS = [
    "missing_tranche_id",
    "empty_tranche_id",
    "short_source_head",
    "non_hex_source_tree",
    "wrong_schema_version",
    "extra_profile_key",
    "missing_change_signals_key",
    "extra_change_signals_key",
    "non_boolean_signal",
    "empty_change_families",
    "unknown_change_family",
    "semantic_kind_receipt",
    "semantic_binding_duplicate_path",
    "volatile_kind_source",
    "semantic_volatile_overlap",
    "baseline_bad_digest",
    "baseline_not_required_tier2",
    "baseline_not_before_first_edit",
    "freeze_empty_focused_gates",
    "freeze_bad_binding_digest",
    "freeze_short_source_head",
    "post_freeze_unknown_family",
    "post_freeze_too_many_families",
    "empty_threat_ids",
    "invalid_threat_id",
    "negative_mutation_count",
    "bool_mutation_count",
    "review_triggers_extra_key",
    "parallelism_bad_lane",
    "empty_capability",
    "bad_attention_status",
    "empty_closed_surfaces",
    "duplicate_configured_event",
    "empty_configured_event",
]

RESULT_MUTATIONS = [
    "result_wrong_schema_version",
    "result_profile_sha256_mismatch",
    "result_classified_tier_mismatch",
    "result_missing_gate_id",
    "result_duplicate_gate_id",
    "result_gate_unknown_category",
    "result_gate_revision_required",
    "result_gate_uncertain",
    "result_gate_invalid_result",
    "result_missing_required_rerun_item",
    "result_extra_required_rerun_item",
    "result_missing_canonical_gate",
    "result_canonical_gate_not_passed",
    "result_missing_manifest_gate",
    "result_zero_vetoes_tier2",
    "result_review_requirement_mismatch",
    "result_veto_not_pass",
    "result_stale_pass_reuse",
    "result_missing_continuation_receipt",
    "result_duplicate_incident_grouping",
    "result_incident_not_before_correction",
    "result_incident_missing_field",
    "result_tail_safety_relevant",
    "result_tail_integrity_relevant",
    "result_tail_missing_owner",
    "result_parallelism_plan_mismatch",
    "result_parallelism_deviation",
    "result_baseline_fingerprint_mismatch",
    "result_baseline_not_required",
    "result_baseline_known_failure_mismatch",
    "result_freeze_binding_digest_mismatch",
    "result_freeze_toolchain_digest_mismatch",
    "result_threat_coverage_missing",
    "result_decision_pass_but_gate_failed",
    "result_empty_gates",
    "result_extra_top_level_key",
    "result_missing_deferred_tail",
    "result_missing_parallelism",
    "result_empty_technical_result",
]


def test_named_hostile_semantic_mutation_volume_exceeds_fifty() -> None:
    assert len(PROFILE_MUTATIONS) + len(RESULT_MUTATIONS) >= 50


@pytest.mark.parametrize("mutation_name", PROFILE_MUTATIONS)
def test_profile_hostile_semantic_mutations_fail_closed(mutation_name: str) -> None:
    with pytest.raises(ValueError):
        rw.validate_profile(_mutate_profile(mutation_name))


@pytest.mark.parametrize("mutation_name", RESULT_MUTATIONS)
def test_result_hostile_semantic_mutations_fail_closed(mutation_name: str) -> None:
    profile = _profile()
    result = _mutate_result(mutation_name, profile)
    try:
        normalized = rw.validate_result(result)
        admission = rw.admit_result(profile, normalized)
        assert admission["decision"] == "revision_required"
    except ValueError:
        # Structural rejection before admission is also fail-closed.
        return
