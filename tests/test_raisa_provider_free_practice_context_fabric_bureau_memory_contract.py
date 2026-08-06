from __future__ import annotations

import ast
import json
from copy import deepcopy
from pathlib import Path

import pytest
from graphql import build_schema
from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_acceptance import (
    BASE_GRAPHQL_PATH,
    EVIDENCE_PATH,
    EXAMPLE_PATH,
    GRAPHQL_PATH,
    RESULT,
    SCHEMA_PATH,
    authored_synthetic_inputs,
    build_evidence,
    build_example,
)
from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    build_context_need,
    canonical_sha256,
    intersect_context_scope,
    proofread_same_packet,
    seal,
    select_bureau_memory_items,
)


ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "scripts/raisa_provider_free_practice_context_fabric_bureau_memory_contract.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(instance: dict) -> list:
    schema = _load(SCHEMA_PATH)
    return list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(instance)
    )


def _reseal(value: dict, field: str) -> dict:
    value.pop(field, None)
    return seal(value, field)


def test_nominal_packet_and_committed_example_validate() -> None:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    packet = build_example()
    assert _errors(packet) == []
    assert _load(EXAMPLE_PATH) == packet
    assert packet["scope_grant"]["decision"] == "ADMIT"
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"


def test_evidence_passes_and_all_engine_side_effects_are_zero() -> None:
    evidence = build_evidence()
    assert evidence["result"] == RESULT
    assert evidence["passed"] is True
    assert evidence["schema_version"].endswith(".v2")
    assert "source_head" not in evidence
    assert evidence["source_binding"] == {
        "mode": "canonical_lf_artifact_hashes_with_external_exact_head_receipt",
        "artifact_count": 8,
        "git_head_self_reference_forbidden": True,
        "checkout_line_endings_normalized": True,
    }
    assert {
        "scripts/raisa_provider_free_practice_context_fabric_bureau_memory_acceptance.py",
        "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
    }.issubset(evidence["artifact_hashes"])
    assert set(evidence["authority_and_side_effects"].values()) == {0}
    committed = _load(EVIDENCE_PATH)
    assert committed == evidence


def test_candidate_schema_has_no_authority_identity_or_retention_fields() -> None:
    schema = _load(SCHEMA_PATH)["$defs"]["context_need_candidate"]
    fields = set(schema["properties"])
    assert not fields.intersection(
        {
            "principal_ref",
            "role_codes",
            "practice_ref",
            "location_refs",
            "consent_codes",
            "retention_days",
            "authority_binding",
            "command",
            "write",
        }
    )
    assert schema["additionalProperties"] is False


@pytest.mark.parametrize(
    "field",
    [
        "principal_ref",
        "practice_ref",
        "role_codes",
        "retention_days",
        "raw_audit_query",
        "sql_predicate",
        "command",
    ],
)
def test_candidate_authority_or_audit_expansion_fails_schema(field: str) -> None:
    packet = build_example()
    packet["candidate"][field] = "forbidden"
    packet = _reseal(packet, "contract_digest")
    assert _errors(packet)


def test_unknown_requested_field_fails_closed_schema_admission() -> None:
    packet = build_example()
    packet["candidate"]["requested_fields"] = ["request_label_code", "raw_payload"]
    packet["candidate"] = _reseal(packet["candidate"], "candidate_digest")
    packet = _reseal(packet, "contract_digest")
    assert _errors(packet)


@pytest.mark.parametrize(
    "field",
    [
        "raw_prompt",
        "raw_response",
        "before_payload",
        "after_payload",
        "actor_id",
        "database_key",
        "command_payload",
        "user_agent",
        "ip_address",
    ],
)
def test_memory_item_forbidden_disclosure_fails_schema(field: str) -> None:
    packet = build_example()
    packet["available_memory_items"][0][field] = "forbidden"
    packet = _reseal(packet, "contract_digest")
    assert _errors(packet)


def test_scope_intersection_only_narrows_fields_time_and_cardinality() -> None:
    candidate, binding, _ = authored_synthetic_inputs()
    need = build_context_need(
        candidate, binding, assembled_at="2026-08-06T08:02:00Z"
    )
    grant = intersect_context_scope(
        candidate, need, binding, assembled_at="2026-08-06T08:02:00Z"
    )
    assert set(grant["allowed_fields"]) < set(candidate["requested_fields"])
    assert grant["effective_time_window"] == {
        "starts_at": "2026-08-06T07:00:00Z",
        "ends_at": "2026-08-06T09:00:00Z",
    }
    assert grant["maximum_results"] == 2
    assert {
        "FIELDS_NARROWED",
        "TIME_WINDOW_NARROWED",
        "RESULT_LIMIT_NARROWED",
    } <= set(grant["reduction_reason_codes"])
    assert grant["read_only"] is True
    assert grant["command_authority"] is False
    assert grant["provider_authority"] is False


def test_cross_scope_denial_is_uniform_not_available_without_counts() -> None:
    candidate, binding, _ = authored_synthetic_inputs()
    binding["allowed_bureaus"] = ["davida"]
    binding = _reseal(binding, "binding_digest")
    need = build_context_need(
        candidate, binding, assembled_at="2026-08-06T08:02:00Z"
    )
    grant = intersect_context_scope(
        candidate, need, binding, assembled_at="2026-08-06T08:02:00Z"
    )
    assert grant["decision"] == "NOT_AVAILABLE"
    assert grant["requesting_bureau"] == "NOT_AVAILABLE"
    assert grant["maximum_results"] == 0
    assert grant["allowed_fields"] == []
    assert grant["reduction_reason_codes"] == ["SCOPE_NOT_AVAILABLE"]


def test_half_open_window_excludes_end_boundary_and_superseded_items() -> None:
    candidate, binding, items = authored_synthetic_inputs()
    need = build_context_need(
        candidate, binding, assembled_at="2026-08-06T08:02:00Z"
    )
    grant = intersect_context_scope(
        candidate, need, binding, assembled_at="2026-08-06T08:02:00Z"
    )
    at_end = deepcopy(items[0])
    at_end["memory_item_id"] = "memory:end-boundary-001"
    at_end["completed_at"] = grant["effective_time_window"]["ends_at"]
    at_end = _reseal(at_end, "memory_item_digest")
    selected, trace = select_bureau_memory_items(
        candidate["bureau_memory_selector"], [*items, at_end], grant
    )
    assert [item["memory_item_id"] for item in selected] == [
        "memory:rayleen-001",
        "memory:bernie-001",
    ]
    assert "ITEM_NOT_ADMITTED" in trace["exclusion_reason_codes"]


def test_memory_is_historical_read_context_not_current_truth_or_command() -> None:
    packet = build_example()
    frame = packet["frame_set"]["frames"][0]
    assert frame["source_class"] == "recent_collective_work"
    assert frame["frame_type"] == "bureau_memory_item_set"
    assert frame["read_only"] is True
    assert frame["command_authority"] is False
    assert frame["coverage_complete"] is False
    assert "opaque_target_ref" not in frame["items"][0]
    assert {item["authority_ceiling"] for item in frame["items"]} == {
        "read_context_only"
    }


def test_same_packet_tamper_and_expiry_block_release() -> None:
    packet = build_example()
    tampered = deepcopy(packet["frame_set"])
    tampered["frames"][0]["items"][0]["outcome_code"] = "blocked"
    with pytest.raises(ContractViolation, match="frame_set_digest_mismatch"):
        proofread_same_packet(
            packet["context_need"],
            packet["scope_grant"],
            packet["memory_selector"],
            tampered,
            packet["selector_trace"],
            packet["weave_trace"],
            proofread_at="2026-08-06T08:02:01Z",
        )
    expired = proofread_same_packet(
        packet["context_need"],
        packet["scope_grant"],
        packet["memory_selector"],
        packet["frame_set"],
        packet["selector_trace"],
        packet["weave_trace"],
        proofread_at="2026-08-06T08:04:00Z",
    )
    assert expired["release_decision"] == "BLOCK"
    assert expired["reason_codes"] == ["FRAME_SET_EXPIRED"]


def test_selector_digest_is_bound_through_grant_weave_and_proofreader() -> None:
    packet = build_example()
    selector = deepcopy(packet["memory_selector"])
    selector["maximum_results"] = 1
    selector = _reseal(selector, "selector_digest")
    trace = proofread_same_packet(
        packet["context_need"],
        packet["scope_grant"],
        selector,
        packet["frame_set"],
        packet["selector_trace"],
        packet["weave_trace"],
        proofread_at="2026-08-06T08:02:01Z",
    )
    assert trace["release_decision"] == "BLOCK"
    assert {
        "FRAME_SET_SELECTOR_DIGEST_MISMATCH",
        "GRANT_SELECTOR_DIGEST_MISMATCH",
        "SELECTOR_TRACE_SELECTOR_DIGEST_MISMATCH",
        "WEAVE_SELECTOR_DIGEST_MISMATCH",
    } <= set(trace["reason_codes"])


def test_resealed_out_of_scope_item_is_blocked_by_independent_proofreading() -> None:
    packet = build_example()
    frame_set = deepcopy(packet["frame_set"])
    item = frame_set["frames"][0]["items"][0]
    item["outcome_code"] = "blocked"
    frame_set["frames"][0]["items"][0] = _reseal(
        item, "memory_item_digest"
    )
    frame_set["frames"][0] = _reseal(
        frame_set["frames"][0], "content_digest"
    )
    frame_set = _reseal(frame_set, "frame_set_digest")
    weave = deepcopy(packet["weave_trace"])
    weave["frame_set_digest"] = frame_set["frame_set_digest"]
    weave = _reseal(weave, "trace_digest")
    trace = proofread_same_packet(
        packet["context_need"],
        packet["scope_grant"],
        packet["memory_selector"],
        frame_set,
        packet["selector_trace"],
        weave,
        proofread_at="2026-08-06T08:02:01Z",
    )
    assert trace["release_decision"] == "BLOCK"
    assert "ITEM_OUTCOME_SCOPE_INVALID" in trace["reason_codes"]


def test_canonical_digest_is_stable_and_mutation_sensitive() -> None:
    left = {"b": [2, 1], "a": "value"}
    right = {"a": "value", "b": [2, 1]}
    assert canonical_sha256(left) == canonical_sha256(right)
    right["b"] = [1, 2]
    assert canonical_sha256(left) != canonical_sha256(right)


def test_graphql_extension_composes_and_has_one_candidate_only_read_root() -> None:
    schema = build_schema(
        BASE_GRAPHQL_PATH.read_text(encoding="utf-8")
        + "\n"
        + GRAPHQL_PATH.read_text(encoding="utf-8")
    )
    query = schema.query_type
    assert query is not None
    assert "practiceContextFabric" in query.fields
    field = query.fields["practiceContextFabric"]
    assert set(field.args) == {"candidate"}
    candidate_fields = set(schema.get_type("ContextNeedCandidateInput").fields)
    assert not candidate_fields.intersection(
        {"principal", "role", "practice", "location", "consent", "authority"}
    )
    assert schema.mutation_type is None
    assert schema.subscription_type is None
    assert "bureauMemory" not in query.fields


def test_engine_has_no_product_network_database_subprocess_or_filesystem_write_surface() -> None:
    tree = ast.parse(ENGINE_PATH.read_text(encoding="utf-8"))
    modules = set()
    attributes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Attribute):
            attributes.add(node.attr)
    assert not modules.intersection(
        {
            "app",
            "sqlalchemy",
            "requests",
            "httpx",
            "socket",
            "subprocess",
            "pathlib",
            "google",
            "boto3",
            "os",
        }
    )
    assert not attributes.intersection(
        {"write_text", "write_bytes", "connect", "execute", "commit"}
    )


def test_contract_artifacts_are_repository_local_and_exclude_branding() -> None:
    paths = [
        SCHEMA_PATH,
        EXAMPLE_PATH,
        EVIDENCE_PATH,
        GRAPHQL_PATH,
        ENGINE_PATH,
        ROOT / "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-plan.md",
        ROOT / "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-design.md",
        ROOT / "docs/security/raisa-provider-free-practice-context-fabric-bureau-memory-contract-threat-model-delta.md",
    ]
    for path in paths:
        assert path.is_file()
        assert ROOT in path.parents
        assert not path.is_relative_to(ROOT / "docs/branding")
        text = path.read_text(encoding="utf-8")
        assert "C:\\Users\\" not in text
        assert "C:/Users/" not in text
