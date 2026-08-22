from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis-plan.md"
THREAT = ROOT / "docs" / "security" / "raisa-provider-free-read-only-check-in-attempt-007-redaction-forbidden-field-and-cleanup-projection-coordinate-diagnosis-threat-model-delta.md"


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split()).lower()


def test_plan_freezes_two_deterministic_gears_and_no_attempt_008() -> None:
    text = _normalized(PLAN)
    assert "prospective-success projection gate" in text
    assert "typed post-finalization terminal bridge" in text
    assert "attempt 008 remains closed" in text
    assert "no docker object" in text
    assert "no retry, resume" in text


def test_plan_freezes_exact_conflict_and_cleanup_claim_boundary() -> None:
    text = _normalized(PLAN)
    assert "closed_boundaries.live_secret_existing_hosted_or_product_database_used" in text
    assert "cleanup_status=not_started" in text
    assert "transaction semantics" in text
    assert "unproved" in text


def test_threat_delta_forbids_weakening_and_reclassification() -> None:
    text = _normalized(THREAT)
    assert "may not alter redactor coverage" in text
    assert "preserve immutable `not_started`" in text
    assert "no database successor is authorised" in text
