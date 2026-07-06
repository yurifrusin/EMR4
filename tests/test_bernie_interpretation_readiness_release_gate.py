"""Release-gate documentation checks for the interpretation readiness command."""

from pathlib import Path

from scripts.bernie_provider_boundary_readiness_report import (
    PROVIDER_BOUNDARY_PROPOSAL_CITATION_FIELDS,
)


RELEASE_GATES = Path("orchestration/bernie_release_gates.md")


def test_release_gates_require_interpretation_readiness_command_before_wiring():
    text = RELEASE_GATES.read_text(encoding="utf-8")

    assert "Provider-Free Interpretation Harness Gate" in text
    assert "scripts\\bernie_interpretation_readiness_check.py" in text
    assert "runtime_or_provider_wiring_ready=false" in text
    assert "raw_trove_access_ready=false" in text
    assert "runtime_gate_decision=blocked" in text


def test_release_gates_require_provider_boundary_report_before_provider_changes():
    text = RELEASE_GATES.read_text(encoding="utf-8")

    assert "scripts\\bernie_provider_boundary_readiness_report.py" in text
    assert "default_provider=disabled" in text
    assert "live_provider_enabled=false" in text
    assert "provider_calls_performed=false" in text
    assert "route_behavior_changed=false" in text
    assert "database_access_performed=false" in text
    assert "memory_or_rag_access_performed=false" in text
    assert "historical_diary_material_access_performed=false" in text
    assert "proposal_citation_required_fields" in text
    for field in PROVIDER_BOUNDARY_PROPOSAL_CITATION_FIELDS:
        assert f"`{field}`" in text


def test_release_gates_pause_if_interpretation_readiness_changes():
    text = RELEASE_GATES.read_text(encoding="utf-8")

    assert "sprint engine must pause" in text
    assert "explicit review" in text
    assert "provider-boundary report fails" in text
    for forbidden_surface in [
        "runtime route wiring",
        "provider prompt wiring",
        "provider dry-run wiring",
        "memory/RAG/GraphRAG use",
        "historical diary material access",
    ]:
        assert forbidden_surface in text


def test_release_gates_document_proposal_surface_guard():
    text = RELEASE_GATES.read_text(encoding="utf-8")

    assert "Proposal Surface Guard" in text
    assert "scripts\\bernie_interpretation_proposal_surface_guard.py" in text
    assert "<proposal-path>" in text
