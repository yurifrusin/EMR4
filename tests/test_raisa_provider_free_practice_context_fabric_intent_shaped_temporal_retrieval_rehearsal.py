from __future__ import annotations

import ast
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal import (
    COMPONENT_VOCABULARY,
    IntentRetrievalViolation,
    build_authored_synthetic_sources,
    build_intent_authority_binding,
    build_intent_candidate,
    build_intent_packet,
    build_source_catalog,
    proofread_intent_packet,
)
from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal_acceptance import (
    ACCEPTANCE_PATH,
    DESIGN_PATH,
    ENGINE_PATH,
    EVIDENCE_PATH,
    EXAMPLE_PATH,
    PLAN_PATH,
    RESULT,
    SCHEMA_PATH,
    THREAT_PATH,
    build_evidence,
    build_example,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(instance: dict) -> list:
    return list(
        Draft202012Validator(
            _load(SCHEMA_PATH), format_checker=FormatChecker()
        ).iter_errors(instance)
    )


def _inputs() -> tuple[dict, dict, dict]:
    sources = build_authored_synthetic_sources()
    catalog = build_source_catalog(sources)
    binding = build_intent_authority_binding(sources, catalog=catalog)
    return sources, catalog, binding


def _packet(
    intent: str,
    *,
    bureau: str = "RAYLEEN",
    valid_at: str | None = "2026-08-06T00:30:00Z",
    known_at: str | None = "2026-08-06T02:30:00Z",
    sources: dict | None = None,
) -> dict:
    source_bundle = sources or build_authored_synthetic_sources()
    catalog = build_source_catalog(source_bundle)
    binding = build_intent_authority_binding(source_bundle, catalog=catalog)
    candidate = build_intent_candidate(
        intent,
        requesting_bureau=bureau,
        valid_at=valid_at,
        known_at=known_at,
    )
    return build_intent_packet(candidate, binding, catalog)


def _bare(packet: dict) -> dict:
    return {
        key: deepcopy(value)
        for key, value in packet.items()
        if key not in {"proofreader_trace", "contract_digest"}
    }


def test_nominal_packet_and_committed_example_validate() -> None:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    packet = build_example()
    assert _errors(packet) == []
    assert _load(EXAMPLE_PATH) == packet
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"
    assert packet["frame_set"]["disposition"] == "ADMIT"
    assert [
        item["component_code"] for item in packet["frame_set"]["components"]
    ] == ["CURRENT_OPERATIONAL", "HISTORICAL_OPERATIONAL"]


@pytest.mark.parametrize(
    ("intent", "expected"),
    [
        ("CURRENT_OPERATIONAL_STATUS", ["CURRENT_OPERATIONAL"]),
        ("RECENT_PRACTICE_WORK", ["BUREAU_MEMORY"]),
        ("HISTORICAL_OPERATIONAL_STATE", ["HISTORICAL_OPERATIONAL"]),
        (
            "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON",
            ["CURRENT_OPERATIONAL", "HISTORICAL_OPERATIONAL"],
        ),
    ],
)
def test_closed_intent_selects_only_required_components(
    intent: str, expected: list[str]
) -> None:
    packet = _packet(intent)
    assert packet["frame_set"]["disposition"] == "ADMIT"
    assert [
        item["component_code"] for item in packet["frame_set"]["components"]
    ] == expected


def test_current_component_preserves_four_source_coherence_with_minimal_facts() -> None:
    packet = _packet("CURRENT_OPERATIONAL_STATUS")
    component = packet["frame_set"]["components"][0]
    assert len(component["upstream_frame_digests"]) == 4
    assert [fact["fact_code"] for fact in component["facts"]] == [
        "CURRENT_APPOINTMENT_STATUS",
        "CURRENT_WAIT_MINUTES",
        "CURRENT_PRACTITIONER_ROLE",
        "CURRENT_SESSION_PROPOSAL_STATE",
    ]
    assert len({fact["source_class"] for fact in component["facts"]}) == 4


def test_overbroad_candidate_is_narrowed_to_fixed_intent_template() -> None:
    sources, catalog, binding = _inputs()
    candidate = build_intent_candidate(
        "CURRENT_OPERATIONAL_STATUS",
        requested_components=[
            "CURRENT_OPERATIONAL",
            "BUREAU_MEMORY",
            "HISTORICAL_OPERATIONAL",
        ],
        requested_field_profiles=[
            "CURRENT_MINIMAL",
            "MEMORY_MINIMAL",
            "HISTORICAL_MINIMAL",
        ],
    )
    packet = build_intent_packet(candidate, binding, catalog)
    assert packet["intent_plan"]["required_components"] == ["CURRENT_OPERATIONAL"]
    assert "COMPONENTS_NARROWED_TO_INTENT" in packet["intent_plan"][
        "reduction_reason_codes"
    ]
    assert len(packet["frame_set"]["components"]) == 1
    assert sources["current_packet"]["frame_set"]["frames"]


@pytest.mark.parametrize(
    "field",
    [
        "principal_ref",
        "practice_id",
        "role_codes",
        "location_refs",
        "retention_days",
        "raw_prompt",
        "sql_query",
        "vector_query",
        "patient_id",
        "command",
    ],
)
def test_candidate_authority_query_or_patient_injection_is_rejected(field: str) -> None:
    _, catalog, binding = _inputs()
    candidate = build_intent_candidate("CURRENT_OPERATIONAL_STATUS")
    candidate[field] = "forbidden"
    candidate.pop("candidate_digest")
    candidate = seal(candidate, "candidate_digest")
    with pytest.raises(IntentRetrievalViolation, match="candidate_shape_invalid"):
        build_intent_packet(candidate, binding, catalog)


def test_explicit_vocabulary_mapping_is_not_implicit_case_folding() -> None:
    assert COMPONENT_VOCABULARY == {
        "CURRENT_OPERATIONAL": {
            "canonical_bureau": "RAYLEEN",
            "upstream_bureau": "RAYLEEN",
            "upstream_purpose": "CURRENT_OPERATIONAL_AWARENESS",
            "shareability": "SAME_BUREAU_ONLY",
        },
        "BUREAU_MEMORY": {
            "canonical_bureau": "RAYLEEN",
            "upstream_bureau": "rayleen",
            "upstream_purpose": "recent_practice_work",
            "shareability": "BILATERAL_ONLY",
        },
        "HISTORICAL_OPERATIONAL": {
            "canonical_bureau": "RAYLEEN",
            "upstream_bureau": "RAYLEEN",
            "upstream_purpose": "TEMPORAL_OPERATIONAL_RECALL",
            "shareability": "BILATERAL_ONLY",
        },
    }


def test_bilateral_memory_share_is_admitted_but_private_current_is_not() -> None:
    shared = _packet("RECENT_PRACTICE_WORK", bureau="BERNIE")
    assert shared["frame_set"]["disposition"] == "ADMIT"
    private = _packet("CURRENT_OPERATIONAL_STATUS", bureau="BERNIE")
    assert private["frame_set"]["disposition"] == "NOT_AVAILABLE"
    assert private["frame_set"]["components"] == []
    assert "PRIVATE_SESSION_NOT_SHAREABLE" in private["frame_set"][
        "omission_reason_codes"
    ]


def test_missing_bilateral_share_fails_uniformly_without_component_counts() -> None:
    _, catalog, binding = _inputs()
    binding["bilateral_shares"] = []
    binding.pop("binding_digest")
    binding = seal(binding, "binding_digest")
    candidate = build_intent_candidate(
        "RECENT_PRACTICE_WORK", requesting_bureau="BERNIE"
    )
    packet = build_intent_packet(candidate, binding, catalog)
    assert packet["frame_set"]["disposition"] == "NOT_AVAILABLE"
    assert packet["frame_set"]["components"] == []
    assert packet["selection_trace"]["fact_count"] == 0
    assert packet["selection_trace"]["disclosed_bytes"] == 0


def test_ambiguous_recent_reference_returns_opaque_alternatives_without_identity() -> None:
    packet = _packet("RECENT_OPERATIONAL_REFERENCE")
    assert packet["frame_set"]["disposition"] == "ALTERNATIVES"
    assert packet["frame_set"]["components"] == []
    assert [
        item["opaque_subject_ref"] for item in packet["frame_set"]["alternatives"]
    ] == [
        "synthetic:opaque-operational-ref:one",
        "synthetic:opaque-operational-ref:two",
    ]
    assert all(
        item["identity_asserted"] is False
        for item in packet["frame_set"]["alternatives"]
    )


def test_reassembly_required_current_state_blocks_old_frame_set() -> None:
    sources = build_authored_synthetic_sources()
    sources["current_state"] = sources["temporal_packet"]["frame_set_state"]
    packet = _packet("CURRENT_OPERATIONAL_STATUS", sources=sources)
    assert packet["frame_set"]["disposition"] == "NOT_AVAILABLE"
    assert packet["frame_set"]["components"] == []
    assert "CURRENT_COMPONENT_REASSEMBLY_REQUIRED" in packet["frame_set"][
        "omission_reason_codes"
    ]


def test_catalog_is_bound_to_backend_authority_and_resealed_substitution_fails() -> None:
    _, catalog, binding = _inputs()
    catalog["components"][0]["upstream_packet_digest"] = "sha256:" + "0" * 64
    catalog["components"][0].pop("component_digest")
    catalog["components"][0] = seal(
        catalog["components"][0], "component_digest"
    )
    catalog.pop("catalog_digest")
    catalog = seal(catalog, "catalog_digest")
    candidate = build_intent_candidate("CURRENT_OPERATIONAL_STATUS")
    packet = build_intent_packet(candidate, binding, catalog)
    assert packet["frame_set"]["disposition"] == "NOT_AVAILABLE"
    assert packet["frame_set"]["components"] == []
    assert "CATALOG_BINDING_MISMATCH" in packet["frame_set"][
        "omission_reason_codes"
    ]


def test_catalog_recomputes_upstream_proofreader_before_projecting_facts() -> None:
    sources = build_authored_synthetic_sources()
    sources["current_packet"]["source_envelopes"][0]["payload"]["appointments"][0][
        "status"
    ] = "COMPLETED"
    with pytest.raises(
        IntentRetrievalViolation, match="current_upstream_not_released"
    ):
        build_source_catalog(sources)


def test_bitemporal_known_then_and_corrected_later_are_distinct() -> None:
    old = _packet(
        "HISTORICAL_OPERATIONAL_STATE", known_at="2026-08-06T01:00:00Z"
    )
    corrected = _packet(
        "HISTORICAL_OPERATIONAL_STATE", known_at="2026-08-06T02:30:00Z"
    )
    assert old["frame_set"]["components"][0]["facts"][0]["value"] == 2
    assert corrected["frame_set"]["components"][0]["facts"][0]["value"] == 3
    assert (
        old["frame_set"]["components"][0]["facts"][0]["upstream_digest"]
        != corrected["frame_set"]["components"][0]["facts"][0][
            "upstream_digest"
        ]
    )


def test_historical_gap_is_not_absence_evidence() -> None:
    packet = _packet(
        "HISTORICAL_OPERATIONAL_STATE",
        valid_at="2026-08-06T02:15:00Z",
        known_at="2026-08-06T02:30:00Z",
    )
    assert packet["frame_set"]["disposition"] == "NOT_AVAILABLE"
    assert packet["frame_set"]["components"] == []
    assert "HISTORICAL_NO_COVERAGE" in packet["frame_set"][
        "omission_reason_codes"
    ]


def test_same_packet_proofreader_blocks_content_and_provenance_tamper() -> None:
    packet = build_example()
    content_tamper = _bare(packet)
    content_tamper["frame_set"]["components"][0]["facts"][0]["value"] = "OTHER"
    assert (
        proofread_intent_packet(
            content_tamper, checked_at="2026-08-06T03:01:01Z"
        )["release_decision"]
        == "BLOCK"
    )
    provenance_tamper = _bare(packet)
    provenance_tamper["frame_set"]["components"][0][
        "upstream_packet_digest"
    ] = "sha256:" + "0" * 64
    assert (
        proofread_intent_packet(
            provenance_tamper, checked_at="2026-08-06T03:01:01Z"
        )["release_decision"]
        == "BLOCK"
    )


def test_expired_component_produces_safe_not_available() -> None:
    sources, catalog, binding = _inputs()
    candidate = build_intent_candidate("CURRENT_OPERATIONAL_STATUS")
    packet = build_intent_packet(
        candidate,
        binding,
        catalog,
        assembled_at="2026-08-06T03:02:00Z",
        checked_at="2026-08-06T03:02:01Z",
    )
    assert packet["frame_set"]["disposition"] == "NOT_AVAILABLE"
    assert packet["proofreader_trace"]["release_decision"] == "BLOCK"
    assert sources["current_packet"]["frame_set"]["expires_at"] == (
        "2026-08-06T03:02:00Z"
    )


def test_evidence_passes_and_engine_side_effects_are_zero() -> None:
    evidence = build_evidence()
    assert evidence["result"] == RESULT
    assert evidence["passed"] is True
    assert set(evidence["authority_and_side_effects"].values()) == {0}
    assert evidence["source_binding"]["artifact_count"] == 7
    assert _load(EVIDENCE_PATH) == evidence


def test_engine_has_no_application_provider_io_or_command_surface() -> None:
    tree = ast.parse(ENGINE_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {
        "app",
        "boto3",
        "google",
        "httpx",
        "os",
        "pathlib",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
    }
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imports.intersection(forbidden_imports)
    text = ENGINE_PATH.read_text(encoding="utf-8")
    assert "Mutation" not in text
    assert "Subscription" not in text


def test_plan_design_threat_and_api_boundary_language_is_present() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    design = DESIGN_PATH.read_text(encoding="utf-8")
    threat = THREAT_PATH.read_text(encoding="utf-8")
    for token in [
        "Clinician One",
        "Requests",
        "prescribing",
        "billing",
        "atomic Bureau capability",
    ]:
        assert token.lower() in (plan + design + threat).lower()
    assert "adds no API surface" in design
    assert ACCEPTANCE_PATH.exists()
