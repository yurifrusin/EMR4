"""Proposal surface guard tests for Bernie interpretation readiness."""

from pathlib import Path

from scripts.bernie_interpretation_proposal_surface_guard import (
    PROVIDER_BOUNDARY_COMMAND,
    PROVIDER_BOUNDARY_EXPECTED_VALUES,
    READINESS_COMMAND,
    files_missing_readiness_reference,
)


def test_proposal_surface_guard_accepts_h63_review_brief():
    missing = files_missing_readiness_reference(
        (Path("docs/adversarial/h63_interpretation_independent_review_brief.md"),)
    )

    assert missing == ()


def test_proposal_surface_guard_rejects_runtime_proposal_without_readiness(tmp_path):
    proposal = tmp_path / "proposal.md"
    proposal.write_text(
        "This runtime/provider/trove proposal discusses runtime route wiring.",
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == (proposal,)


def test_proposal_surface_guard_rejects_release_gate_route_integration_phrase(
    tmp_path,
):
    proposal = tmp_path / "route-integration.md"
    proposal.write_text(
        "This plan discusses interpretation harness runtime route integration.",
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == (proposal,)


def test_proposal_surface_guard_rejects_release_gate_memory_and_h_series_phrases(
    tmp_path,
):
    proposal = tmp_path / "memory-h-series.md"
    proposal.write_text(
        (
            "This proposal discusses memory/RAG/GraphRAG use, H15 runtime "
            "imports, H-series runtime imports, Access AI, historical diary "
            "access, historical diary trove, raw diary, and local data."
        ),
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == (proposal,)


def test_proposal_surface_guard_accepts_runtime_proposal_with_readiness(tmp_path):
    proposal = tmp_path / "proposal.md"
    proposal.write_text(
        "\n".join(
            [
                "This runtime/provider/trove proposal discusses runtime route wiring.",
                READINESS_COMMAND,
                "runtime_or_provider_wiring_ready=false",
                "raw_trove_access_ready=false",
                "runtime_gate_decision=blocked",
            ]
        ),
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == ()


def test_proposal_surface_guard_rejects_provider_boundary_without_report(tmp_path):
    proposal = tmp_path / "provider-boundary.md"
    proposal.write_text(
        "\n".join(
            [
                "This provider-boundary proposal discusses live-provider aliasing.",
                READINESS_COMMAND,
                "runtime_or_provider_wiring_ready=false",
                "raw_trove_access_ready=false",
                "runtime_gate_decision=blocked",
            ]
        ),
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == (proposal,)


def test_proposal_surface_guard_rejects_provider_integration_without_report(
    tmp_path,
):
    proposal = tmp_path / "provider-integration.md"
    proposal.write_text(
        "\n".join(
            [
                "This provider integration proposal discusses live provider enablement.",
                READINESS_COMMAND,
                "runtime_or_provider_wiring_ready=false",
                "raw_trove_access_ready=false",
                "runtime_gate_decision=blocked",
            ]
        ),
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == (proposal,)


def test_proposal_surface_guard_ignores_unrelated_aliasing(tmp_path):
    note = tmp_path / "aliasing.md"
    note.write_text(
        "This note discusses Python import aliasing in a helper module.",
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((note,)) == ()


def test_proposal_surface_guard_accepts_provider_boundary_with_both_reports(tmp_path):
    proposal = tmp_path / "provider-boundary.md"
    proposal.write_text(
        "\n".join(
            [
                "This provider-boundary proposal discusses live-provider aliasing.",
                READINESS_COMMAND,
                PROVIDER_BOUNDARY_COMMAND,
                "runtime_or_provider_wiring_ready=false",
                "raw_trove_access_ready=false",
                "runtime_gate_decision=blocked",
                "default_provider=disabled",
                "live_provider_enabled=false",
                "provider_calls_performed=false",
                "route_behavior_changed=false",
                "database_access_performed=false",
                "memory_or_rag_access_performed=false",
                "historical_diary_material_access_performed=false",
            ]
        ),
        encoding="utf-8",
    )

    assert files_missing_readiness_reference((proposal,)) == ()


def test_provider_boundary_expected_values_match_readiness_report():
    from scripts.bernie_provider_boundary_readiness_report import (
        PROVIDER_BOUNDARY_PROPOSAL_CITATION_FIELDS,
        build_provider_boundary_report,
    )

    report = build_provider_boundary_report()

    assert set(PROVIDER_BOUNDARY_EXPECTED_VALUES) == set(
        PROVIDER_BOUNDARY_PROPOSAL_CITATION_FIELDS
    )
    assert {
        key: str(report[key]).casefold()
        for key in PROVIDER_BOUNDARY_EXPECTED_VALUES
    } == PROVIDER_BOUNDARY_EXPECTED_VALUES


def test_proposal_surface_guard_ignores_unrelated_markdown(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("Ordinary implementation note.", encoding="utf-8")

    assert files_missing_readiness_reference((note,)) == ()
