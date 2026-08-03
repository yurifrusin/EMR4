"""Deterministic acceptance for the Bernie/Davida parallel architecture seam."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.json"
)
SCHEMA = (
    ROOT
    / "orchestration/continuity/bernie-davida-parallel-seam/parallel-lane-contract.schema.json"
)
PLAN = ROOT / "docs/bernie-davida-parallel-seam-plan.md"
DESIGN = ROOT / "docs/bernie-davida-shared-agent-boundary.md"
THREAT = ROOT / "docs/security/bernie-davida-parallel-seam-threat-model-delta.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_validates_against_draft_2020_12_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_json(CONTRACT))


def test_two_probabilistic_work_cells_are_separate_and_database_free() -> None:
    topology = _json(CONTRACT)["topology"]

    assert topology["probabilistic_work_cells"] == ["bernie", "davida"]
    assert topology["combined_probabilistic_container"] is False
    assert topology["separate_runtime_identities"] is True
    assert topology["shared_deterministic_kernel_code"] is True
    assert topology["separate_immutable_agent_policies"] is True
    assert topology["proofreader_outside_probabilistic_work_cell"] is True
    assert (
        topology["native_diary_application_session_composition_is_deterministic"]
        is True
    )
    assert topology["native_diary_depends_on_probabilistic_work_cell"] is False
    assert topology["native_diary_uses_agent_proofreader"] is False
    assert topology["office_terminal_lifecycle_reused_by_native_diary"] is False
    assert (
        topology["existing_native_diary_bearer_path_unchanged_when_feature_off"] is True
    )
    assert topology["probabilistic_database_credentials"] is False
    assert topology["probabilistic_database_session"] is False
    assert topology["model_to_database_path"] is False
    assert topology["backend_is_sole_database_and_command_authority"] is True


def test_authoritative_advisory_and_session_state_are_distinct() -> None:
    assert _json(CONTRACT)["state_classes"] == [
        "authoritative_structured_practice_state",
        "advisory_provenance_bearing_institutional_knowledge",
        "bounded_expiring_agent_session_state",
    ]


def test_active_practitioner_truth_has_one_backend_owner() -> None:
    projection = _json(CONTRACT)["active_practitioner_projection"]

    assert projection["truth_owner"] == "backend_practice_domain"
    assert projection["read_contract"] == "Query.practice.practitioners"
    assert projection["agent_owned_truth"] is False
    assert projection["authoritative_agent_cache"] is False
    assert projection["lifecycle_change_requires_rest_command"] is True
    assert projection["event_requires_fresh_read"] is True


def test_api_spine_planes_remain_distinct() -> None:
    spine = _json(CONTRACT)["api_spine"]

    assert spine["read_context"] == "graphql_named_scoped_read_only"
    assert spine["mutation"] == "rest_openapi_single_purpose_command"
    assert spine["event"] == "committed_signal_requires_fresh_read_never_command"
    assert spine["manifest"] == "declarative_input_runtime_enforced"
    assert spine["proofreader_release"] == "typed_grounded_draft_evidence_only"
    assert spine["davida_emits_confirmation_envelope"] is False
    assert spine["davida_emits_writes_authorized_envelope"] is False
    assert spine["davida_operation_vocabulary"] == "closed_enum_required"
    assert (
        spine["davida_location_context_requires_pure_side_effect_free_projection"]
        is True
    )
    assert {
        "practice_id",
        "actor_context",
        "correlation_id",
        "idempotency_key",
        "expected_aggregate_version_or_etag",
        "confirmation_evidence",
    } <= set(spine["required_future_command_fields"])


def test_lanes_have_disjoint_product_ownership_and_shared_forbidden_paths() -> None:
    lanes = {item["lane_id"]: item for item in _json(CONTRACT)["lanes"]}
    diary = lanes["diary_native_consumer"]
    davida = lanes["davida_practice_operations"]

    assert set(diary["owned_surfaces"]).isdisjoint(davida["owned_surfaces"])
    assert "davida_practice_operations_contracts" in diary["forbidden_surfaces"]
    assert (
        "probabilistic_work_cell_or_agent_proofreader_dependency"
        in diary["forbidden_surfaces"]
    )
    assert "office_terminal_consumer_lifecycle" in diary["forbidden_surfaces"]
    assert (
        "existing_native_diary_bearer_path_when_feature_off"
        in diary["forbidden_surfaces"]
    )
    assert "diary_native_consumer_composition" in davida["forbidden_surfaces"]
    for lane in lanes.values():
        assert "shared_handover_and_continuity" in lane["forbidden_surfaces"]
        assert "docs_branding" in lane["forbidden_surfaces"]
        assert "protected_refs" in lane["forbidden_surfaces"]


def test_parallelism_keeps_mutable_shared_resources_serial_or_root_owned() -> None:
    controls = _json(CONTRACT)["execution_controls"]

    assert controls["repository_conftest_pytest"] == "serial"
    assert controls["shared_postgresql"] == "serial"
    assert controls["antigravity_gemini_reviewer"] == "one_fresh_project_at_a_time"
    assert controls["integration"] == "root_sol_serial"
    assert controls["deterministic_before_external_review"] is True
    assert controls["harness_code_change_required_before_dispatch"] is False
    assert controls["explicit_path_staging_only"] is True
    assert controls["git_add_all_or_dot_forbidden"] is True
    assert controls["agent_worktrees_commit_message_path_forbidden"] is True
    assert controls["reviewer_selection_source"] == "verifier_execution_policy.yaml"
    assert controls["legacy_allocation_plan_reviewer_selection_forbidden"] is True
    assert controls["review_decisions"] == ["pass", "revision_required"]
    assert controls["exact_terminal_review_decision_count"] == 1
    assert "docs/branding" in controls["root_only_shared_paths"]


def test_standing_authority_preserves_material_fork_and_external_gates() -> None:
    payload = _json(CONTRACT)
    authority = payload["authority"]

    assert authority["standing_lane_progression"] is True
    assert authority["material_fork_returns_to_yuri"] is True
    assert authority["manual_intervention_when_materially_more_economical"] is True
    assert authority["worker_acceptance_authority"] is False
    assert authority["reviewer_acceptance_authority"] is False
    assert authority["protected_ref_authority"] is False
    assert authority["deployment_authority"] is False
    assert {
        "live_provider_runtime",
        "memory_rag_graphrag_runtime",
        "real_identity",
        "patient_clinical_document_data",
        "model_to_database_writes",
        "deployment",
        "protected_refs",
    } <= set(payload["blocked_gates"])


def test_public_artifacts_state_non_authority_and_branding_exclusion() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower() for path in (PLAN, DESIGN, THREAT)
    )

    assert "backend remains the sole database and command authority" in combined
    assert "proofreader" in combined
    assert "model-to-database" in combined
    assert "docs/branding/" in combined
    assert "no product runtime" in combined
