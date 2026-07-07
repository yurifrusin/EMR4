from __future__ import annotations

from pathlib import Path


PACKET = Path("orchestration/bernie_diary_review_readiness_sprint160.md")
ORDINARY_PROMPT = (
    "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm "
    "but before 3:45"
)


def _packet_text() -> str:
    return PACKET.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return text.casefold().replace("`", "").replace(" ", "")


def test_review_packet_recommends_yuri_pause_after_verification() -> None:
    text = " ".join(_packet_text().casefold().split())

    assert "pause after sprint 160" in text
    assert "meaningful hands-on diary/bernie review" in text
    assert "provided the verification commands below pass" in text
    assert "supervised receptionist workflow" in text


def test_review_packet_preserves_release_gate_prompt_and_route_label() -> None:
    text = _packet_text()
    folded = text.casefold()

    assert ORDINARY_PROMPT in text
    assert "--expect-result clarification_required" in text
    assert "--reference-date 2026-07-01" in text
    assert "test_bernie_route_intercepted_selected_slot_can_return_to_candidates" in text
    assert "route-intercepted" in folded
    assert "not prove live backend or live provider behavior" in folded
    assert "live_provider: true" in text


def test_review_packet_cites_required_blocked_readiness_values() -> None:
    compact = _compact(_packet_text())

    assert (
        ".venv\\scripts\\python.exescripts\\bernie_interpretation_readiness_check.py"
        in compact
    )
    assert "runtime_or_provider_wiring_ready=false" in compact
    assert "raw_trove_access_ready=false" in compact
    assert "runtime_gate_decision=blocked" in compact


def test_review_packet_cites_required_provider_boundary_values() -> None:
    compact = _compact(_packet_text())

    assert (
        ".venv\\scripts\\python.exescripts\\bernie_provider_boundary_readiness_report.py"
        in compact
    )
    assert "default_provider=disabled" in compact
    assert "live_provider_enabled=false" in compact
    assert "provider_calls_performed=false" in compact
    assert "route_behavior_changed=false" in compact
    assert "database_access_performed=false" in compact
    assert "memory_or_rag_access_performed=false" in compact
    assert "historical_diary_material_access_performed=false" in compact


def test_review_packet_keeps_closed_gates_closed() -> None:
    text = _packet_text().casefold()

    for phrase in (
        "runtime route wiring",
        "provider prompt wiring",
        "provider dry-run wiring",
        "live-provider enablement",
        "memory/rag/graphrag use",
        "h15/h-series runtime imports",
        "historical diary material access",
        "graphql mutations",
        "model-to-database writes",
    ):
        assert phrase in text
