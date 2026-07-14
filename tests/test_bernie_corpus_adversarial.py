"""Executable acceptance for the six LC2 independent adversarial probes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.bernie.corpus_tier import (
    AdjudicationRecord,
    CorpusCandidate,
    promote_candidate,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "bernie_corpus_adversarial"
EXPECTED_FILES = {
    "adversarial_probes_authority_breach.json": "authority_breach",
    "adversarial_probes_quarantine_bypass.json": "quarantine_bypass",
    "adversarial_probes_schema_violation.json": "schema_violation",
    "adversarial_probes_self_certification.json": "self_certification",
    "adversarial_probes_semantic_drift.json": "semantic_drift",
    "adversarial_probes_tier_escalation.json": "tier_escalation",
}


def _load(name: str) -> dict[str, object]:
    payload = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_probe_manifest_is_bounded_and_never_self_certifies() -> None:
    files = {path.name for path in FIXTURE_DIR.glob("*.json")}
    assert files == set(EXPECTED_FILES)

    for name, attack_class in EXPECTED_FILES.items():
        probe = _load(name)
        assert probe["attack_class"] == attack_class
        assert probe["expected_disposition"] == "quarantine"
        assert probe["generator_identity"]["model_id"] == "gemini-3.5-flash"  # type: ignore[index]
        assert probe["candidate_payload"]["judge_identity"] is None  # type: ignore[index]


@pytest.mark.parametrize(
    ("name", "expected_reason"),
    [
        ("adversarial_probes_self_certification.json", "self_certification"),
        ("adversarial_probes_semantic_drift.json", "adjudication_rejected"),
    ],
)
def test_executable_promotion_probes_quarantine(
    name: str, expected_reason: str
) -> None:
    probe = _load(name)
    candidate = CorpusCandidate.model_validate(probe["candidate_payload"])
    adjudication = AdjudicationRecord.model_validate(
        probe["attempted_adjudication_record"]
    )

    outcome = promote_candidate(candidate, adjudication)

    assert outcome.outcome == "quarantined"
    assert outcome.quarantine.reason.value == expected_reason


@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("adversarial_probes_tier_escalation.json", "promotion evidence"),
        ("adversarial_probes_authority_breach.json", "empty authority grant"),
        ("adversarial_probes_schema_violation.json", "reference_date"),
    ],
)
def test_invalid_candidate_payloads_fail_closed(name: str, message: str) -> None:
    probe = _load(name)

    with pytest.raises(ValueError, match=message):
        CorpusCandidate.model_validate(probe["candidate_payload"])


def test_quarantine_bypass_adjudication_fails_closed() -> None:
    probe = _load("adversarial_probes_quarantine_bypass.json")
    CorpusCandidate.model_validate(probe["candidate_payload"])

    with pytest.raises(ValueError, match="complete semantic scope"):
        AdjudicationRecord.model_validate(probe["attempted_adjudication_record"])
