"""Strict, provider-free traceability for authored synthetic scenarios.

The envelope binds provenance and oracle authority to existing domain-owned
scenario representations.  It deliberately contains no scenario payload and
does not execute a replay, provider, route, database, or product service.
"""

from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.bernie.scenario_spec import ReceptionScenarioSpec
from tests.bernie_scenarios.loader import load_scenario_yaml


TOKEN_PATTERN = r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$"
SHA256_PATTERN = r"^[0-9a-f]{64}$"


class SourceType(str, Enum):
    NORMATIVE_OR_CLINICAL_GUIDANCE = "normative_or_clinical_guidance"
    ACCEPTED_EMR4_CONTRACT = "accepted_emr4_contract"
    METHOD_OR_INTEROPERABILITY_STANDARD = "method_or_interoperability_standard"
    VENDOR_OPERATIONAL_DOCUMENTATION = "vendor_operational_documentation"
    VENDOR_ADVERTISED_CAPABILITY = "vendor_advertised_capability"
    FICTION_PROMPT_ONLY = "fiction_prompt_only"
    PRIVATE_OBSERVED_CALIBRATION = "private_observed_calibration"
    LOCAL_DESIGN_ASSUMPTION = "local_design_assumption"


class OracleEligibility(str, Enum):
    AUTHORITATIVE_AFTER_SCOPE_REVIEW = "authoritative_after_scope_review"
    ACCEPTED_CONTRACT = "accepted_contract"
    DESIGN_INPUT_ONLY = "design_input_only"
    PROMPT_ONLY = "prompt_only"
    CALIBRATION_ONLY = "calibration_only"
    ASSUMPTION_ONLY = "assumption_only"


SOURCE_ORACLE_ELIGIBILITY = {
    SourceType.NORMATIVE_OR_CLINICAL_GUIDANCE:
        OracleEligibility.AUTHORITATIVE_AFTER_SCOPE_REVIEW,
    SourceType.ACCEPTED_EMR4_CONTRACT: OracleEligibility.ACCEPTED_CONTRACT,
    SourceType.METHOD_OR_INTEROPERABILITY_STANDARD:
        OracleEligibility.DESIGN_INPUT_ONLY,
    SourceType.VENDOR_OPERATIONAL_DOCUMENTATION:
        OracleEligibility.DESIGN_INPUT_ONLY,
    SourceType.VENDOR_ADVERTISED_CAPABILITY:
        OracleEligibility.DESIGN_INPUT_ONLY,
    SourceType.FICTION_PROMPT_ONLY: OracleEligibility.PROMPT_ONLY,
    SourceType.PRIVATE_OBSERVED_CALIBRATION: OracleEligibility.CALIBRATION_ONLY,
    SourceType.LOCAL_DESIGN_ASSUMPTION: OracleEligibility.ASSUMPTION_ONLY,
}


class EvidenceLabel(str, Enum):
    WHOLLY_AUTHORED_SYNTHETIC = "wholly_authored_synthetic"
    SYNTHETIC_CALIBRATED_FROM_PRIVATE_AGGREGATES = (
        "synthetic_calibrated_from_private_aggregates"
    )
    DEIDENTIFIED_OBSERVED_SEQUENCE = "deidentified_observed_sequence"
    RAW_PRIVATE_OBSERVATION = "raw_private_observation"


class CoverageKind(str, Enum):
    REQUIREMENT = "requirement"
    HAZARD = "hazard"
    FEATURE = "feature"
    WORKFLOW_STATE = "workflow_state"
    INTERACTION = "interaction"
    METAMORPHIC_RELATION = "metamorphic_relation"
    MUTATION_TARGET = "mutation_target"
    EVIDENCE_LEVEL = "evidence_level"


class ActorKind(str, Enum):
    HUMAN = "human"
    ORCHESTRATOR = "orchestrator"
    MODEL = "model"
    DETERMINISTIC_TOOL = "deterministic_tool"


class StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceRecord(StrictFrozenModel):
    source_id: str = Field(pattern=TOKEN_PATTERN)
    source_type: SourceType
    oracle_eligibility: OracleEligibility
    scope_reviewed: bool = False
    issuer: str = Field(min_length=1)
    title: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=1)
    version_or_retrieved_on: str = Field(min_length=1)
    rights_posture: str = Field(min_length=1)
    transformation: str = Field(min_length=1)
    supported_claims: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(min_length=1)

    @field_validator(
        "issuer",
        "title",
        "locator",
        "jurisdiction",
        "version_or_retrieved_on",
        "rights_posture",
        "transformation",
    )
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source metadata must not be blank")
        return value

    @field_validator("supported_claims", "limitations")
    @classmethod
    def reject_blank_sequence_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item.strip() for item in value):
            raise ValueError("source claim and limitation values must not be blank")
        return value

    @model_validator(mode="after")
    def enforce_derived_oracle_eligibility(self) -> "SourceRecord":
        expected = SOURCE_ORACLE_ELIGIBILITY[self.source_type]
        if self.oracle_eligibility != expected:
            raise ValueError("source oracle eligibility cannot self-promote")
        if (
            self.scope_reviewed
            and self.source_type != SourceType.NORMATIVE_OR_CLINICAL_GUIDANCE
        ):
            raise ValueError("scope_reviewed applies only to normative sources")
        return self


class ActorIdentity(StrictFrozenModel):
    actor_kind: ActorKind
    actor_id: str = Field(pattern=TOKEN_PATTERN)

    @property
    def stable_key(self) -> str:
        return f"{self.actor_kind.value}:{self.actor_id}"


class RoleSeparation(StrictFrozenModel):
    author: ActorIdentity
    extractor: ActorIdentity
    adjudicator: ActorIdentity
    reviewer: ActorIdentity

    @model_validator(mode="after")
    def enforce_independence_and_authority(self) -> "RoleSeparation":
        identities = (
            self.author,
            self.extractor,
            self.adjudicator,
            self.reviewer,
        )
        if len({identity.stable_key for identity in identities}) != len(identities):
            raise ValueError("author, extractor, adjudicator and reviewer must differ")
        controlled_roles = (self.author, self.adjudicator, self.reviewer)
        if any(
            identity.actor_kind not in {ActorKind.HUMAN, ActorKind.ORCHESTRATOR}
            for identity in controlled_roles
        ):
            raise ValueError(
                "model or tool output cannot author, adjudicate or review an oracle"
            )
        return self


class OracleClaim(StrictFrozenModel):
    oracle_id: str = Field(pattern=TOKEN_PATTERN)
    claim_locator: str = Field(min_length=1)
    source_ids: tuple[str, ...] = Field(min_length=1)

    @field_validator("source_ids")
    @classmethod
    def validate_source_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("oracle source_ids must be unique")
        if any(re.fullmatch(TOKEN_PATTERN, item) is None for item in value):
            raise ValueError("oracle source_ids must use canonical tokens")
        return value


class OracleBundle(StrictFrozenModel):
    schema_version: Literal["raisa.oracle_bundle.v1"] = "raisa.oracle_bundle.v1"
    deterministic_truth: tuple[OracleClaim, ...] = Field(min_length=1)
    authority_safety_rules: tuple[OracleClaim, ...] = Field(min_length=1)
    model_quality_rubrics: tuple[OracleClaim, ...] = ()

    @model_validator(mode="after")
    def require_unique_oracle_ids(self) -> "OracleBundle":
        claims = (
            self.deterministic_truth
            + self.authority_safety_rules
            + self.model_quality_rubrics
        )
        oracle_ids = [claim.oracle_id for claim in claims]
        if len(set(oracle_ids)) != len(oracle_ids):
            raise ValueError("oracle ids must be unique across the bundle")
        return self


class CoverageClaim(StrictFrozenModel):
    coverage_id: str = Field(pattern=TOKEN_PATTERN)
    kind: CoverageKind
    target_ref: str = Field(min_length=1)
    source_ids: tuple[str, ...] = Field(min_length=1)

    @field_validator("source_ids")
    @classmethod
    def validate_source_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("coverage source_ids must be unique")
        if any(re.fullmatch(TOKEN_PATTERN, item) is None for item in value):
            raise ValueError("coverage source_ids must use canonical tokens")
        return value


class CalibrationEvidenceRef(StrictFrozenModel):
    schema_version: Literal["raisa.calibration_evidence_ref.v1"] = (
        "raisa.calibration_evidence_ref.v1"
    )
    reference_id: str = Field(
        min_length=8,
        max_length=96,
        pattern=r"^calref-[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    resolvable: Literal[False] = False
    deidentification_claimed: Literal[False] = False

    @field_validator("reference_id")
    @classmethod
    def reject_hash_shaped_reference(cls, value: str) -> str:
        suffix = value.removeprefix("calref-")
        if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", suffix):
            raise ValueError("calibration reference must not encode an object hash")
        if "sha" in suffix:
            raise ValueError("calibration reference must not claim a content hash")
        return value


class ArtifactReference(StrictFrozenModel):
    contract_id: str = Field(pattern=TOKEN_PATTERN)
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=SHA256_PATTERN)

    @field_validator("path")
    @classmethod
    def require_safe_repository_relative_path(cls, value: str) -> str:
        if "\\" in value or ":" in value:
            raise ValueError("artifact path must use repository-relative POSIX form")
        path = PurePosixPath(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise ValueError("artifact path must be a safe repository-relative path")
        if path.as_posix() != value:
            raise ValueError("artifact path must use canonical POSIX form")
        return value


class ExecutionBinding(StrictFrozenModel):
    schema_version: Literal["raisa.execution_binding.v1"] = (
        "raisa.execution_binding.v1"
    )
    binding_kind: Literal["reception_semantic_to_stateful_replay"]
    scenario_id: str = Field(pattern=TOKEN_PATTERN)
    relationship: Literal["complementary_shared_identity"]
    semantic_artifact: ArtifactReference
    replay_artifact: ArtifactReference

    @model_validator(mode="after")
    def require_distinct_artifacts(self) -> "ExecutionBinding":
        if self.semantic_artifact.path == self.replay_artifact.path:
            raise ValueError("semantic and replay artifacts must be distinct")
        return self


class TraceableSyntheticScenarioEnvelope(StrictFrozenModel):
    schema_version: Literal["raisa.traceable_synthetic_scenario_envelope.v1"] = (
        "raisa.traceable_synthetic_scenario_envelope.v1"
    )
    scenario_id: str = Field(pattern=TOKEN_PATTERN)
    scenario_version: str = Field(pattern=r"^[1-9][0-9]*\.[0-9]+\.[0-9]+$")
    domain: str = Field(pattern=TOKEN_PATTERN)
    practice_context: str = Field(min_length=1)
    evidence_label: EvidenceLabel
    sources: tuple[SourceRecord, ...] = Field(min_length=1)
    roles: RoleSeparation
    oracle_bundle: OracleBundle
    coverage_claims: tuple[CoverageClaim, ...] = Field(min_length=1)
    execution_binding: ExecutionBinding | None = None
    calibration_evidence_ref: CalibrationEvidenceRef | None = None

    @model_validator(mode="after")
    def enforce_traceability_policy(self) -> "TraceableSyntheticScenarioEnvelope":
        source_by_id = {source.source_id: source for source in self.sources}
        if len(source_by_id) != len(self.sources):
            raise ValueError("source ids must be unique")

        authoritative_claims = (
            self.oracle_bundle.deterministic_truth
            + self.oracle_bundle.authority_safety_rules
        )
        for claim in authoritative_claims:
            self._validate_claim_sources(claim, source_by_id, authoritative=True)
        for claim in self.oracle_bundle.model_quality_rubrics:
            self._validate_claim_sources(claim, source_by_id, authoritative=False)

        for coverage in self.coverage_claims:
            missing = set(coverage.source_ids) - set(source_by_id)
            if missing:
                raise ValueError("coverage claim references an unknown source")
        coverage_ids = [coverage.coverage_id for coverage in self.coverage_claims]
        if len(set(coverage_ids)) != len(coverage_ids):
            raise ValueError("coverage ids must be unique")

        if self.execution_binding is not None:
            if self.evidence_label != EvidenceLabel.WHOLLY_AUTHORED_SYNTHETIC:
                raise ValueError(
                    "executable bindings require wholly_authored_synthetic evidence"
                )
            if self.execution_binding.scenario_id != self.scenario_id:
                raise ValueError("execution binding scenario identity mismatch")

        if self.evidence_label == EvidenceLabel.WHOLLY_AUTHORED_SYNTHETIC:
            if self.calibration_evidence_ref is not None:
                raise ValueError("wholly authored scenarios cannot claim calibration")
        elif self.calibration_evidence_ref is None:
            raise ValueError("private-derived labels require an opaque calibration ref")
        return self

    @staticmethod
    def _validate_claim_sources(
        claim: OracleClaim,
        source_by_id: dict[str, SourceRecord],
        *,
        authoritative: bool,
    ) -> None:
        missing = set(claim.source_ids) - set(source_by_id)
        if missing:
            raise ValueError("oracle claim references an unknown source")
        locator_parts = claim.claim_locator.split("#", maxsplit=1)
        if (
            len(locator_parts) != 2
            or locator_parts[0] not in claim.source_ids
            or not locator_parts[1]
        ):
            raise ValueError("oracle claim locator must bind one declared source id")
        for source_id in claim.source_ids:
            source = source_by_id[source_id]
            if authoritative:
                accepted = source.oracle_eligibility == OracleEligibility.ACCEPTED_CONTRACT
                scoped = (
                    source.oracle_eligibility
                    == OracleEligibility.AUTHORITATIVE_AFTER_SCOPE_REVIEW
                    and source.scope_reviewed
                )
                if not (accepted or scoped):
                    raise ValueError(
                        "non-authoritative source cannot bind an authoritative oracle"
                    )
            elif source.oracle_eligibility in {
                OracleEligibility.PROMPT_ONLY,
                OracleEligibility.CALIBRATION_ONLY,
            }:
                raise ValueError("prompt or calibration source cannot bind an oracle")


class TraceableScenarioManifest(StrictFrozenModel):
    schema_version: Literal["raisa.traceable_scenario_manifest.v1"] = (
        "raisa.traceable_scenario_manifest.v1"
    )
    envelopes: tuple[TraceableSyntheticScenarioEnvelope, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def require_unique_scenario_ids(self) -> "TraceableScenarioManifest":
        ids = [envelope.scenario_id for envelope in self.envelopes]
        if len(set(ids)) != len(ids):
            raise ValueError("manifest scenario ids must be unique")
        return self


class LegacyBindingValidationResult(StrictFrozenModel):
    schema_version: Literal["raisa.legacy_binding_validation.v1"] = (
        "raisa.legacy_binding_validation.v1"
    )
    scenario_id: str
    relationship: Literal["complementary_shared_identity"]
    semantic_sha256: str = Field(pattern=SHA256_PATTERN)
    replay_sha256: str = Field(pattern=SHA256_PATTERN)
    status: Literal["passed"] = "passed"


LEGACY_RECEPTION_BINDINGS = {
    "booking_create_then_exact_duplicate": (
        "tests/fixtures/bernie_scenario_spec/booking_create_then_exact_duplicate.json",
        "tests/fixtures/bernie_scenarios/booking_create_then_exact_duplicate.yaml",
    ),
    "booking_overlap_not_exact_duplicate": (
        "tests/fixtures/bernie_scenario_spec/booking_overlap_not_exact_duplicate.json",
        "tests/fixtures/bernie_scenarios/booking_overlap_not_exact_duplicate.yaml",
    ),
}
LEGACY_SEMANTIC_CONTRACT_ID = "emr4.reception_scenario_spec.lc1.v1"
LEGACY_REPLAY_CONTRACT_ID = "emr4.bernie_stateful_replay.v1"


def _allowed_path(repo_root: Path, artifact: ArtifactReference) -> Path:
    root = repo_root.resolve(strict=True)
    candidate = repo_root.joinpath(*PurePosixPath(artifact.path).parts)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("artifact path escapes the repository or is not a file")
    if candidate.is_symlink():
        raise ValueError("artifact path must not be a symbolic link")
    return resolved


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_legacy_binding(
    repo_root: Path,
    envelope: TraceableSyntheticScenarioEnvelope,
) -> LegacyBindingValidationResult:
    """Validate one exact allowlisted pair without discovering other files."""

    binding = envelope.execution_binding
    if binding is None:
        raise ValueError("legacy envelope requires an execution binding")
    expected_paths = LEGACY_RECEPTION_BINDINGS.get(envelope.scenario_id)
    if expected_paths is None:
        raise ValueError("scenario is not in the legacy reception allowlist")
    observed_paths = (
        binding.semantic_artifact.path,
        binding.replay_artifact.path,
    )
    if observed_paths != expected_paths:
        raise ValueError("legacy artifact paths do not match the exact allowlist")
    if (
        binding.semantic_artifact.contract_id != LEGACY_SEMANTIC_CONTRACT_ID
        or binding.replay_artifact.contract_id != LEGACY_REPLAY_CONTRACT_ID
    ):
        raise ValueError("legacy artifact contract ids do not match their owners")
    accepted_contract_locators = {
        source.locator
        for source in envelope.sources
        if source.source_type == SourceType.ACCEPTED_EMR4_CONTRACT
    }
    if accepted_contract_locators != set(expected_paths):
        raise ValueError("legacy accepted-contract locators do not match both artifacts")

    semantic_path = _allowed_path(repo_root, binding.semantic_artifact)
    replay_path = _allowed_path(repo_root, binding.replay_artifact)
    semantic_digest = _digest(semantic_path)
    replay_digest = _digest(replay_path)
    if semantic_digest != binding.semantic_artifact.sha256:
        raise ValueError("semantic artifact digest mismatch")
    if replay_digest != binding.replay_artifact.sha256:
        raise ValueError("replay artifact digest mismatch")

    semantic = ReceptionScenarioSpec.model_validate(
        json.loads(semantic_path.read_text(encoding="utf-8"))
    )
    replay = load_scenario_yaml(replay_path)
    if semantic.scenario_id != envelope.scenario_id:
        raise ValueError("semantic fixture scenario identity mismatch")
    if replay.id != envelope.scenario_id:
        raise ValueError("replay fixture scenario identity mismatch")

    return LegacyBindingValidationResult(
        scenario_id=envelope.scenario_id,
        relationship=binding.relationship,
        semantic_sha256=semantic_digest,
        replay_sha256=replay_digest,
    )


def validate_legacy_binding_manifest(
    repo_root: Path,
    manifest: TraceableScenarioManifest,
) -> tuple[LegacyBindingValidationResult, ...]:
    """Require and validate the complete two-pair legacy rehearsal manifest."""

    observed = {envelope.scenario_id for envelope in manifest.envelopes}
    if observed != set(LEGACY_RECEPTION_BINDINGS):
        raise ValueError("legacy manifest must contain exactly the two accepted pairs")
    return tuple(validate_legacy_binding(repo_root, item) for item in manifest.envelopes)


__all__ = [
    "ActorIdentity",
    "ActorKind",
    "ArtifactReference",
    "CalibrationEvidenceRef",
    "CoverageClaim",
    "CoverageKind",
    "EvidenceLabel",
    "ExecutionBinding",
    "LEGACY_RECEPTION_BINDINGS",
    "LEGACY_REPLAY_CONTRACT_ID",
    "LEGACY_SEMANTIC_CONTRACT_ID",
    "LegacyBindingValidationResult",
    "OracleBundle",
    "OracleClaim",
    "OracleEligibility",
    "RoleSeparation",
    "SOURCE_ORACLE_ELIGIBILITY",
    "SourceRecord",
    "SourceType",
    "TraceableScenarioManifest",
    "TraceableSyntheticScenarioEnvelope",
    "validate_legacy_binding",
    "validate_legacy_binding_manifest",
]
