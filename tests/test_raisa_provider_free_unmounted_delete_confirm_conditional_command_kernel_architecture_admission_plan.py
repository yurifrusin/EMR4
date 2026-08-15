from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-plan.md"
)
ARCHITECTURE = (
    ROOT
    / "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-threat-model-delta.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(value: str) -> str:
    return " ".join(value.split())


def test_frozen_timestamp_is_present_in_all_tranche_documents() -> None:
    timestamp = "2026-08-15T11:50:49+10:00"
    for doc in (PLAN, ARCHITECTURE, THREAT):
        assert timestamp in _text(doc)


def test_exact_lock_order_and_skipped_schedule_domain_boundary() -> None:
    combined = _flat("\n".join((_text(PLAN), _text(ARCHITECTURE))))
    for required in (
        "practice -> appointment -> idempotency_record",
        "schedule-domain",
        "skipped, not moved",
        "confirmAppointmentDeleteProposal",
        "delete-confirm",
    ):
        assert required in combined


def test_confirmation_evidence_reason_and_optional_text_boundaries() -> None:
    combined = _flat("\n".join((_text(PLAN), _text(ARCHITECTURE), _text(THREAT))))
    for required in (
        "confirmed=true",
        "warning acknowledgements",
        "LEGACY_UNCLASSIFIED",
        "at most 500 characters",
        "authentic",
        "unexpired",
        "Cancelled",
    ):
        assert required in combined


def test_acceptance_counts_and_effect_boundary_claim() -> None:
    plan = _flat(_text(PLAN))
    threat = _flat(_text(THREAT))
    architecture = _flat(_text(ARCHITECTURE))
    assert "at least 40 independent hostile mutations fail closed" in plan
    assert "effect-boundary flag remains false" in threat
    assert "command/write" in plan
    assert "no command" in architecture


def test_next_gate_and_claim_calibration() -> None:
    plan = _flat(_text(PLAN))
    architecture = _flat(_text(ARCHITECTURE))
    threat = _flat(_text(THREAT))
    for required in (
        "physical representability review",
        "does not prove PostgreSQL",
        "cannot prove a SQL schema",
    ):
        assert required in plan or required in architecture or required in threat


def test_forbidden_surfaces_are_explicit() -> None:
    plan = _flat(_text(PLAN))
    architecture = _flat(_text(ARCHITECTURE))
    threat = _flat(_text(THREAT))
    combined = plan + " " + architecture + " " + threat
    for required in (
        "protected refs",
        "docs/branding",
        "provider",
        "deployment",
        "Pages",
        "watcher",
        "patient",
    ):
        assert required in combined
