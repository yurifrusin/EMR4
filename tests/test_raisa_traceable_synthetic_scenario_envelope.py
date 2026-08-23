"""Hostile tests for the provider-free synthetic scenario traceability layer."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from orchestration_harness.synthetic_scenario_envelope import (
    ActorKind,
    ArtifactReference,
    CalibrationEvidenceRef,
    EvidenceLabel,
    LEGACY_RECEPTION_BINDINGS,
    OracleEligibility,
    SourceType,
    TraceableScenarioManifest,
    TraceableSyntheticScenarioEnvelope,
    validate_legacy_binding,
    validate_legacy_binding_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "raisa_synthetic_scenario_envelope"
    / "legacy_reception_bindings.json"
)


def _raw_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _manifest() -> TraceableScenarioManifest:
    return TraceableScenarioManifest.model_validate(_raw_manifest())


def _first_envelope(raw: dict | None = None) -> dict:
    value = _raw_manifest() if raw is None else raw
    return value["envelopes"][0]


def test_manifest_is_strict_and_contains_exactly_the_two_legacy_pairs() -> None:
    manifest = _manifest()
    assert {item.scenario_id for item in manifest.envelopes} == set(
        LEGACY_RECEPTION_BINDINGS
    )
    assert all(
        item.evidence_label == EvidenceLabel.WHOLLY_AUTHORED_SYNTHETIC
        for item in manifest.envelopes
    )


def test_both_existing_pairs_validate_through_their_own_contract_loaders() -> None:
    results = validate_legacy_binding_manifest(REPO_ROOT, _manifest())
    assert len(results) == 2
    assert {result.scenario_id for result in results} == set(
        LEGACY_RECEPTION_BINDINGS
    )
    assert all(result.status == "passed" for result in results)
    assert all(result.relationship == "complementary_shared_identity" for result in results)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("version", "schema_version"),
        ("extra", "extra"),
        ("evidence_label", "evidence_label"),
        ("coverage_kind", "kind"),
    ],
)
def test_closed_schema_and_vocabularies_reject_free_form_values(
    mutation: str,
    message: str,
) -> None:
    raw = _raw_manifest()
    envelope = _first_envelope(raw)
    if mutation == "version":
        envelope["schema_version"] = "raisa.traceable_synthetic_scenario_envelope.v2"
    elif mutation == "extra":
        envelope["free_form_authority"] = "approved"
    elif mutation == "evidence_label":
        envelope["evidence_label"] = "probably_synthetic"
    else:
        envelope["coverage_claims"][0]["kind"] = "looks_covered"
    with pytest.raises(ValidationError, match=message):
        TraceableScenarioManifest.model_validate(raw)


def test_source_oracle_eligibility_cannot_self_promote() -> None:
    raw = _raw_manifest()
    source = _first_envelope(raw)["sources"][0]
    source["oracle_eligibility"] = OracleEligibility.AUTHORITATIVE_AFTER_SCOPE_REVIEW.value
    with pytest.raises(ValidationError, match="cannot self-promote"):
        TraceableScenarioManifest.model_validate(raw)


@pytest.mark.parametrize(
    "field",
    ["locator", "rights_posture", "transformation", "limitations"],
)
def test_source_records_require_traceability_and_limitations(field: str) -> None:
    raw = _raw_manifest()
    del _first_envelope(raw)["sources"][0][field]
    with pytest.raises(ValidationError, match=field):
        TraceableScenarioManifest.model_validate(raw)


@pytest.mark.parametrize(
    ("source_type", "eligibility"),
    [
        (
            SourceType.VENDOR_ADVERTISED_CAPABILITY.value,
            OracleEligibility.DESIGN_INPUT_ONLY.value,
        ),
        (
            SourceType.VENDOR_OPERATIONAL_DOCUMENTATION.value,
            OracleEligibility.DESIGN_INPUT_ONLY.value,
        ),
        (SourceType.FICTION_PROMPT_ONLY.value, OracleEligibility.PROMPT_ONLY.value),
    ],
)
def test_vendor_and_fiction_sources_cannot_bind_authoritative_oracles(
    source_type: str,
    eligibility: str,
) -> None:
    raw = _raw_manifest()
    source = _first_envelope(raw)["sources"][0]
    source["source_type"] = source_type
    source["oracle_eligibility"] = eligibility
    with pytest.raises(ValidationError, match="non-authoritative source"):
        TraceableScenarioManifest.model_validate(raw)


def test_normative_source_requires_scope_review_before_oracle_use() -> None:
    raw = _raw_manifest()
    source = _first_envelope(raw)["sources"][0]
    source["source_type"] = SourceType.NORMATIVE_OR_CLINICAL_GUIDANCE.value
    source["oracle_eligibility"] = (
        OracleEligibility.AUTHORITATIVE_AFTER_SCOPE_REVIEW.value
    )
    source["scope_reviewed"] = False
    with pytest.raises(ValidationError, match="non-authoritative source"):
        TraceableScenarioManifest.model_validate(raw)

    source["scope_reviewed"] = True
    TraceableScenarioManifest.model_validate(raw)


@pytest.mark.parametrize("role", ["author", "adjudicator", "reviewer"])
def test_model_output_cannot_control_an_oracle(role: str) -> None:
    raw = _raw_manifest()
    _first_envelope(raw)["roles"][role]["actor_kind"] = ActorKind.MODEL.value
    with pytest.raises(ValidationError, match="model or tool output"):
        TraceableScenarioManifest.model_validate(raw)


def test_distinct_model_extractor_is_representable_but_gains_no_oracle_role() -> None:
    raw = _raw_manifest()
    _first_envelope(raw)["roles"]["extractor"] = {
        "actor_kind": ActorKind.MODEL.value,
        "actor_id": "bounded-model-extractor",
    }
    manifest = TraceableScenarioManifest.model_validate(raw)
    assert manifest.envelopes[0].roles.extractor.actor_kind == ActorKind.MODEL


def test_role_identity_reuse_is_rejected() -> None:
    raw = _raw_manifest()
    roles = _first_envelope(raw)["roles"]
    roles["reviewer"] = copy.deepcopy(roles["author"])
    with pytest.raises(ValidationError, match="must differ"):
        TraceableScenarioManifest.model_validate(raw)


@pytest.mark.parametrize(
    "reference_id",
    [
        "https://private.example/archive",
        "calref-private/diary",
        "calref-private\\diary",
        "calref-private.json",
        "calref-" + "a" * 40,
        "calref-" + "b" * 64,
        "calref-sha256-private",
    ],
)
def test_calibration_reference_is_opaque_and_non_resolving(reference_id: str) -> None:
    with pytest.raises(ValidationError):
        CalibrationEvidenceRef(reference_id=reference_id)


@pytest.mark.parametrize(
    "claim",
    [
        {"resolvable": True},
        {"deidentification_claimed": True},
    ],
)
def test_calibration_reference_cannot_resolve_or_claim_deidentification(
    claim: dict[str, bool],
) -> None:
    with pytest.raises(ValidationError):
        CalibrationEvidenceRef(reference_id="calref-private-calibration-one", **claim)


def test_private_calibration_can_be_labelled_but_not_executably_bound() -> None:
    raw = copy.deepcopy(_first_envelope())
    raw["evidence_label"] = (
        EvidenceLabel.SYNTHETIC_CALIBRATED_FROM_PRIVATE_AGGREGATES.value
    )
    raw["calibration_evidence_ref"] = {
        "schema_version": "raisa.calibration_evidence_ref.v1",
        "reference_id": "calref-private-calibration-one",
        "resolvable": False,
        "deidentification_claimed": False,
    }
    with pytest.raises(ValidationError, match="executable bindings require"):
        TraceableSyntheticScenarioEnvelope.model_validate(raw)

    raw["execution_binding"] = None
    parsed = TraceableSyntheticScenarioEnvelope.model_validate(raw)
    assert parsed.calibration_evidence_ref is not None
    assert parsed.calibration_evidence_ref.resolvable is False


@pytest.mark.parametrize(
    "path",
    [
        "../protected.json",
        "/absolute/protected.json",
        "C:/private/archive.json",
        "tests\\fixtures\\private.json",
    ],
)
def test_artifact_reference_rejects_traversal_and_non_relative_paths(path: str) -> None:
    with pytest.raises(ValidationError):
        ArtifactReference(
            contract_id="test.contract.v1",
            path=path,
            sha256="a" * 64,
        )


def test_safe_but_non_allowlisted_binding_path_is_rejected_before_open() -> None:
    raw = copy.deepcopy(_first_envelope())
    raw["execution_binding"]["semantic_artifact"]["path"] = (
        "tests/fixtures/bernie_scenario_spec/not_allowlisted.json"
    )
    envelope = TraceableSyntheticScenarioEnvelope.model_validate(raw)
    with pytest.raises(ValueError, match="exact allowlist"):
        validate_legacy_binding(REPO_ROOT, envelope)


def test_digest_mutation_is_rejected() -> None:
    raw = copy.deepcopy(_first_envelope())
    raw["execution_binding"]["semantic_artifact"]["sha256"] = "0" * 64
    envelope = TraceableSyntheticScenarioEnvelope.model_validate(raw)
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_legacy_binding(REPO_ROOT, envelope)


def test_binding_identity_mismatch_is_rejected_by_the_envelope() -> None:
    raw = copy.deepcopy(_first_envelope())
    raw["execution_binding"]["scenario_id"] = "another-scenario"
    with pytest.raises(ValidationError, match="identity mismatch"):
        TraceableSyntheticScenarioEnvelope.model_validate(raw)


def test_execution_evidence_cannot_promote_a_source_or_evidence_label() -> None:
    raw = copy.deepcopy(_first_envelope())
    raw["execution_result"] = {
        "source_tier": "authoritative",
        "evidence_label": "wholly_authored_synthetic",
    }
    with pytest.raises(ValidationError, match="extra"):
        TraceableSyntheticScenarioEnvelope.model_validate(raw)


def test_manifest_copies_no_dialogue_state_or_known_synthetic_person_names() -> None:
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    forbidden = (
        '"dialogue_turns"',
        '"turns"',
        '"initial_diary_state"',
        '"initial_state"',
        '"expected_outcome_kind"',
        '"expected_tool_sequence"',
        "Margaret Thompson",
        "Dr Shera",
    )
    assert all(value not in text for value in forbidden)
