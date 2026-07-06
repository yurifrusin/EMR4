"""Checks for the post-Sprint-118 API Spine checkpoint artifact."""

from pathlib import Path


CHECKPOINT = Path("orchestration/api_spine_post_sprint118_checkpoint.md")


def _text() -> str:
    return CHECKPOINT.read_text(encoding="utf-8")


def test_api_spine_checkpoint_exists_and_records_required_source_pass():
    text = _text()

    assert "Post-Sprint-118 API Spine Checkpoint" in text
    for required_source in [
        "orchestration/api_spine_adr.md",
        "orchestration/api_spine_programme.md",
        "orchestration/access_ai_api_design.md",
        "orchestration/bernie_release_gates.md",
        "docs/api-spine/graphql/appointment-diary-read.graphql",
        "docs/api-spine/openapi/appointment-commands.yaml",
        "docs/api-spine/async/integration-events.yaml",
        "docs/api-spine/manifests/agent-capability-charters.yaml",
        "docs/api-spine/manifests/practice-onboarding-example.yaml",
        "docs/api-spine/security/permission-matrix.yaml",
        "tests/test_api_spine_artifacts.py",
    ]:
        assert required_source in text


def test_api_spine_checkpoint_preserves_mixed_spine_boundaries():
    text = _text()

    assert "GraphQL remains a read/context graph only" in text
    assert "no `type Mutation`" in text
    assert "REST/OpenAPI command endpoints remain the only place" in text
    assert "Async contracts observe or ingest typed events" in text
    assert "YAML manifests declare setup, policy, capability" in text
    assert "Access AI remains the only intended provider invocation boundary" in text


def test_api_spine_checkpoint_records_provider_boundary_guard_stack():
    text = _text()

    assert "Sprints 110-118" in text
    assert "scripts/bernie_provider_boundary_readiness_report.py" in text
    assert "proposal_citation_required_fields" in text
    assert "scripts/bernie_interpretation_proposal_surface_guard.py" in text
    assert "default-disabled" in text


def test_api_spine_checkpoint_names_next_non_invasive_slice_and_closed_gates():
    text = _text()

    assert "Recommended Sprint 121" in text
    assert "Appointment command envelope alignment inventory" in text
    assert "maps current FastAPI appointment proposal" in text
    for closed_gate in [
        "live providers",
        "runtime FGA clients",
        "external patient clients",
        "GraphQL mutations",
        "broad historical diary trove mining",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ]:
        assert closed_gate in text
