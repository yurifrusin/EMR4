"""Deterministic acceptance for the Davida practice-administration boundary.

Architecture-only, provider-free, non-executing. Mirrors the accepted
Bernie/Davida parallel seam test style: reads public docs, contract JSON and
read-only application sources; never opens a database or imports app runtime.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "orchestration/continuity/davida-practice-administration-boundary/capability-contract.json"
)
SCHEMA = (
    ROOT
    / "orchestration/continuity/davida-practice-administration-boundary/capability-contract.schema.json"
)
PLAN = ROOT / "docs/davida-practice-administration-boundary-plan.md"
DESIGN = ROOT / "docs/davida-practice-administration-boundary-design.md"
THREAT = (
    ROOT
    / "docs/security/davida-practice-administration-boundary-threat-model-delta.md"
)
DIARY_ROUTER = ROOT / "app/routers/diary.py"
PRACTITIONER_READ = (
    ROOT / "app/services/practice/practitioner_directory_read.py"
)

KNOWN_OPERATION_CODES = {
    "ADVISORY_EXPLAIN_DIRECTORY",
    "ADVISORY_SUMMARIZE_DIRECTORY",
    "PROPOSE_DEACTIVATE_PRACTITIONER",
    "PROPOSE_REACTIVATE_PRACTITIONER",
    "PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
    "PROPOSE_UPDATE_PRACTITIONER_PROFILE",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _function_body(source: str, name: str) -> str:
    start = source.find(f"def {name}(")
    assert start != -1, f"def {name}( not found in source"
    end = source.find("\ndef ", start + 1)
    if end == -1:
        end = source.find("\n@router", start + 1)
    if end == -1:
        end = len(source)
    return source[start:end]


def _is_known_operation(code: str) -> bool:
    # Deterministic mirror of the fail-closed rule: an operation outside the
    # closed enum is never admitted.
    return code in KNOWN_OPERATION_CODES


def test_contract_validates_against_draft_2020_12_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_json(CONTRACT))


def test_davida_is_separate_identity_with_shared_kernel_and_no_crossing() -> None:
    identity = _json(CONTRACT)["identity_and_topology"]

    assert identity["agent_id"] == "davida"
    assert identity["separate_from_bernie"] is True
    assert identity["separate_runtime_identity"] is True
    assert identity["combined_probabilistic_container"] is False
    assert identity["shared_provider_neutral_mechanical_kernel"] is True
    assert identity["shared_typed_envelopes"] is True
    assert identity["shared_deterministic_proofreader_primitives"] is True
    assert identity["shared_audit_vocabulary"] is True
    assert identity["policies_do_not_cross"] is True
    assert identity["scopes_do_not_cross"] is True
    assert identity["memory_does_not_cross"] is True
    assert identity["credentials_do_not_cross"] is True
    assert identity["proofreader_outside_probabilistic_work_cell"] is True
    assert identity["backend_is_sole_database_and_command_authority"] is True


def test_forbidden_authorities_are_absent() -> None:
    forbidden = _json(CONTRACT)["forbidden_authorities"]

    for key in (
        "database_credential",
        "orm_session",
        "generic_database_client",
        "graphql_mutation",
        "rest_command_credential",
        "event_actuator",
        "model_to_database_path",
    ):
        assert forbidden[key] is False
    assert forbidden["confirmation_envelope_emission"] is False
    assert forbidden["writes_authorized_true_emission"] is False
    assert forbidden["mutating_release_envelope"] is False
    assert forbidden["signed_command_emission"] is False


def test_four_state_classes_are_distinct() -> None:
    assert _json(CONTRACT)["state_classes"] == [
        "authoritative_structured_practice_state",
        "advisory_provenance_bearing_institutional_knowledge",
        "bounded_expiring_session_context_state",
        "declarative_manifest_policy",
    ]


def test_context_desk_blocks_room_and_waiting_area_get_paths() -> None:
    desk = _json(CONTRACT)["context_desk"]

    assert desk["pattern"] == "read_desk_typed_read_intent_pure_projection_only"
    assert desk["eligible_active_practitioner_read_contract"] == "Query.practice.practitioners"
    assert desk["eligible_active_practitioner_service"] == "list_practitioner_directory"
    assert desk["active_practitioner_projection_pure"] is True
    assert desk["future_location_source_requires_pure_projection"] is True
    assert desk["blocked_room_get_path"] == "GET /api/v1/diary/rooms"
    assert desk["blocked_room_get_reason"] == "normalizes_and_commits_during_nominal_read"
    assert desk["blocked_waiting_area_get_path"] == "GET /api/v1/diary/waiting-areas"
    assert (
        desk["blocked_waiting_area_get_reason"]
        == "normalizes_and_commits_during_nominal_read"
    )
    assert desk["blocked_waiting_room_get_path"] == "GET /api/v1/appointments/waiting-room"
    assert desk["context_frames_minimal"] is True
    assert desk["context_frames_non_authoritative"] is True


def test_room_and_waiting_area_get_handlers_normalize_and_commit() -> None:
    source = DIARY_ROUTER.read_text(encoding="utf-8")

    for name in ("get_rooms", "get_waiting_areas"):
        body = _function_body(source, name)
        assert "db.commit()" in body, f"{name} must commit during nominal read"
        assert "_normalize_resource_order" in body, (
            f"{name} must normalize during nominal read"
        )


def test_active_practitioner_projection_is_pure_read() -> None:
    source = PRACTITIONER_READ.read_text(encoding="utf-8")
    body = _function_body(source, "list_practitioner_directory")

    assert "db.commit(" not in body
    assert "db.flush(" not in body
    assert "db.add(" not in body
    assert "db.delete(" not in body


def test_closed_operation_enum_fails_closed_on_unknown() -> None:
    ops = _json(CONTRACT)["operation_enum"]

    assert ops["domain"] == "practitioner_lifecycle_administration"
    assert ops["closed"] is True
    assert ops["fail_closed_on_unknown"] is True
    codes = {item["code"] for item in ops["operations"]}
    assert codes == KNOWN_OPERATION_CODES
    assert all(item["mutable"] is False for item in ops["operations"])

    # Fail-closed: an unknown operation is never admitted.
    assert _is_known_operation("APPLY_PRACTITIONER_DEACTIVATE") is False
    assert _is_known_operation("PROPOSE_OPENING_HOURS_CHANGE") is False
    assert _is_known_operation("anything/open-string") is False


def test_emission_ceiling_excludes_confirmation_and_write_authority() -> None:
    ceiling = _json(CONTRACT)["emission_ceiling"]

    assert ceiling["typed_advisory_drafts"] is True
    assert ceiling["typed_proposal_candidates"] is True
    assert ceiling["human_confirmation"] is False
    assert ceiling["signed_command"] is False
    assert ceiling["writes_authorized_true"] is False
    assert ceiling["mutating_release_envelope"] is False
    assert ceiling["proofreader_release"] == "typed_grounded_draft_evidence_only"


def test_future_command_envelope_is_backend_owned_after_human_confirmation() -> None:
    envelope = _json(CONTRACT)["future_backend_owned_command_envelope"]

    assert envelope["owner"] == "trusted_backend_code"
    assert envelope["constructed_after_explicit_human_confirmation"] is True
    required = {
        "practice_id",
        "actor_context",
        "idempotency_key",
        "intent_or_proposal_hash",
        "expected_aggregate_version_or_etag",
        "expires_at",
        "correlation_id",
        "source_surface",
    }
    assert required <= set(envelope["proposal_fields"])
    assert {
        "confirmation_evidence",
        "resulting_revision",
        "audit_event_id",
        "outbox_event_id",
    } <= set(envelope["confirmation_fields"])


def test_event_semantics_are_hints_requiring_fresh_read() -> None:
    events = _json(CONTRACT)["event_semantics"]

    assert events["role"] == "hint"
    assert events["payload_is_truth"] is False
    assert events["payload_is_command"] is False
    assert events["may_request_fresh_authorized_read"] is True
    assert events["event_actuator_present"] is False


def test_four_tranche_sequence_is_present() -> None:
    tranches = _json(CONTRACT)["tranches"]

    assert [item["tranche"] for item in tranches] == [1, 2, 3, 4]
    assert [item["name"] for item in tranches] == [
        "pure_read_projections",
        "provider_free_typed_interpretation_proofreading",
        "one_bounded_proposal_path",
        "separately_authorised_confirmed_write_vertical",
    ]


def test_api_spine_planes_remain_distinct() -> None:
    spine = _json(CONTRACT)["api_spine"]

    assert spine["read_context"] == "graphql_named_scoped_read_only"
    assert spine["mutation"] == "rest_openapi_single_purpose_command"
    assert spine["event"] == "committed_signal_requires_fresh_read_never_command"
    assert spine["manifest"] == "declarative_input_runtime_enforced"
    assert spine["context_frames_minimal"] is True
    assert spine["context_frames_non_authoritative"] is True


def test_public_artifacts_state_non_authority_and_branding_exclusion() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (PLAN, DESIGN, THREAT)
    )

    assert "backend remains the sole database and command authority" in combined or (
        "database truth" in combined and "command authority" in combined
    )
    assert "provider-free" in combined
    assert "no runtime claim" in combined
    assert "docs/branding/" in combined
    assert "writes_authorized" in combined
    assert "fail closed" in combined
