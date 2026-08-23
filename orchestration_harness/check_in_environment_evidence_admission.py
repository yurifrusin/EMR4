"""Pure unmounted composition of evidence-gate and check-in admission readings."""

from __future__ import annotations

from dataclasses import replace
import re

from app.services.appointment_check_in_environment_evidence_gate import (
    EVIDENCE_GATE_READING_SCHEMA_VERSION,
    EnvironmentEvidenceGateReading,
)
from orchestration_harness.check_in_admission_control import (
    AdmissionDecision,
    AdmissionLane,
    AdmissionRequest,
    AdmissionSnapshot,
    DecisionReason,
    DecisionValue,
    REHEARSAL_PROFILE,
    RehearsalProfile,
    evaluate_admission,
)


_ENVIRONMENT_IDENTIFIER = re.compile(r"^env:[a-z0-9][a-z0-9._-]{2,95}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _reading_matches_snapshot(
    snapshot: AdmissionSnapshot,
    reading: object,
) -> bool:
    if type(reading) is not EnvironmentEvidenceGateReading:
        return False
    identifier = snapshot.environment_evidence_identifier
    manifest_digest = snapshot.environment_evidence_manifest_digest
    if (
        type(identifier) is not str
        or _ENVIRONMENT_IDENTIFIER.fullmatch(identifier) is None
        or type(manifest_digest) is not str
        or _SHA256.fullmatch(manifest_digest) is None
    ):
        return False
    return all(
        (
            type(reading.schema_version) is str,
            reading.schema_version == EVIDENCE_GATE_READING_SCHEMA_VERSION,
            type(reading.outcome) is str,
            reading.outcome == "satisfied",
            type(reading.reason_code) is str,
            reading.reason_code == "evidence_gate_satisfied",
            type(reading.environment_identifier) is str,
            reading.environment_identifier == identifier,
            type(snapshot.snapshot_generation) is int,
            type(reading.admission_snapshot_generation) is int,
            reading.admission_snapshot_generation == snapshot.snapshot_generation,
            type(reading.manifest_digest) is str,
            reading.manifest_digest == manifest_digest,
        )
    )


def evaluate_admission_with_environment_evidence(
    snapshot: AdmissionSnapshot | None,
    request: AdmissionRequest,
    environment_evidence_gate_reading: object,
    *,
    profile: RehearsalProfile = REHEARSAL_PROFILE,
) -> AdmissionDecision:
    """Add one mandatory ordinary-lane prerequisite without widening admission."""

    decision = evaluate_admission(snapshot, request, profile=profile)
    target = all(
        (
            decision.decision is DecisionValue.DENIED,
            decision.lane is AdmissionLane.ORDINARY_PRACTICE,
            decision.reason_code is DecisionReason.ORDINARY_ACTIVATION_CLOSED,
            snapshot is not None,
        )
    )
    if not target:
        return decision
    assert snapshot is not None
    if not _reading_matches_snapshot(snapshot, environment_evidence_gate_reading):
        return replace(decision, reason_code=DecisionReason.ORDINARY_EVIDENCE_MISSING)
    return decision
