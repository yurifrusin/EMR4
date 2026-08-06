from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
    "signal-rehearsal-plan.md"
)
DESIGN = ROOT / "docs" / (
    "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
    "signal-rehearsal-design.md"
)
THREAT = ROOT / "docs" / "security" / (
    "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
    "signal-rehearsal-threat-model-delta.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).split())


def test_plan_freezes_exact_parent_result_and_claim() -> None:
    text = _flat(PLAN)
    assert "raisa_provider_free_default_off_live_source_observation_boundary_architecture_pass" in text
    assert "raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_pass" in text
    assert "provider_free_authored_synthetic_unmounted_observation_to_temporal_signal_rehearsal" in text
    assert "does not prove live event" in text


def test_plan_preserves_authority_and_api_spine_separation() -> None:
    text = _flat(PLAN)
    for phrase in (
        "GraphQL remains the read/context graph",
        "REST/OpenAPI remains the command plane",
        "enabled_by_default: false",
        "current `enabled: false`",
        "source input may contain a selector",
        "domain-separated keyed",
        "ObservationPriorCoordinate",
        "AUTHORED_SYNTHETIC_SOURCE_HARNESS",
        "diary.appointment_rescheduled.v1",
        "emr4.diary.appointment_rescheduled.v1",
        "current_diary_projection`, `current_waiting_room_projection",
        "practice-binding digest, source-system id",
        "activation_mode: AUTHORED_SYNTHETIC_REHEARSAL",
        "evidence_mode: AUTHORED_SYNTHETIC",
        "present full-invalidation claim is admission-only",
        "FULL_INVALIDATION_REQUIRED",
        "Only `ADMIT_SIGNAL` emits exactly one existing temporal signal",
        "docs/branding/",
    ):
        assert phrase in text


def test_design_and_threat_delta_preserve_observer_non_authority() -> None:
    design = _flat(DESIGN)
    threat = _flat(THREAT)
    for phrase in (
        "neither observes a source nor owns context truth",
        "policy is and remains disabled",
        "no live source, database, event delivery",
    ):
        assert phrase in design.lower()
    for phrase in (
        "Source-shaped metadata is untrusted",
        "Unknown impact becomes silent irrelevance",
        "checkpoint_persisted: false",
        "cross-scope collision",
        "Prior cursor/revision state is ambiguous",
        "No protected evidence",
    ):
        assert phrase.lower() in threat.lower()


def test_plan_owns_only_pure_rehearsal_artifacts() -> None:
    text = _flat(PLAN)
    for forbidden in (
        "No `app/**`",
        "No `app/**`, `docs/diary/**`",
        "No `app/**`, `docs/diary/**`, API schema",
    ):
        if forbidden in text:
            break
    else:
        raise AssertionError("forbidden runtime surfaces were not frozen")
    for phrase in (
        "zero filesystem, network, database, subprocess",
        "No `app/**`, `docs/diary/**`",
    ):
        assert phrase.lower() in text.lower()
