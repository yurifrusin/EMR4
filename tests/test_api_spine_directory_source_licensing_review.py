from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "docs" / "api-spine" / "directory-source-licensing-review.md"
GAP_PATH = ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
ROOT_INVENTORY_PATH = ROOT / "docs" / "api-spine" / "external-router-read-root-inventory.md"
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
COCHRANE_RESEARCH_PATH = ROOT / "orchestration" / "research" / "cochrane_cds_pipeline.md"
KNOWLEDGE_BASE_PATH = ROOT / "app" / "services" / "ai" / "knowledge_base.py"

EXPECTED_TARGET_ROWS = {
    "Query.directorySearch.RACGP_GUIDELINES": "blocked_pending_source_manifest",
    "Query.directorySearch.COCHRANE_LIBRARY": "blocked_pending_source_manifest",
}

REQUIRED_MANIFEST_FIELDS = {
    "source_name",
    "source_type",
    "licence_status",
    "permitted_use",
    "audience_policy",
    "phi_policy",
    "freshness_policy",
    "citation_shape",
    "storage_policy",
    "regulatory_notes",
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST directory source route",
    "adding GraphQL resolvers or GraphQL mutations",
    "adding Pydantic runtime schemas",
    "adding source manifests as approved runtime configuration",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "RACGP or Cochrane content ingestion, indexing, caching, scraping, or live",
    "appointment, reminder, message, practitioner, directory, billing, result, or clinical write authority",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _review_text() -> str:
    return REVIEW_PATH.read_text(encoding="utf-8")


def _target_rows() -> dict[str, dict[str, str]]:
    section = _review_text().split("## Target Read Surfaces", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `Query.directorySearch."):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "posture": cells[1].strip("`"),
            "future_prerequisite": cells[2],
            "runtime_status": cells[3].strip("`"),
        }
    return rows


def _source_landscape_rows() -> dict[str, dict[str, str]]:
    section = _review_text().split("## Source Landscape Posture", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "posture": cells[1],
            "readiness": cells[2].strip("`"),
        }
    return rows


def test_review_targets_only_racgp_and_cochrane_directory_gaps():
    rows = _target_rows()
    review = _review_text()
    gap_text = GAP_PATH.read_text(encoding="utf-8")
    root_inventory = ROOT_INVENTORY_PATH.read_text(encoding="utf-8")
    graphql = GRAPHQL_PATH.read_text(encoding="utf-8")

    assert set(rows) == set(EXPECTED_TARGET_ROWS)
    for surface in EXPECTED_TARGET_ROWS:
        assert rows[surface]["posture"] == "source_and_licensing_gap"
        assert rows[surface]["runtime_status"] == "not_implemented"
        assert surface in gap_text
        assert surface in root_inventory

    assert "directorySearch(query: String!, source: DirectorySource!" in graphql
    assert "RACGP_GUIDELINES" in graphql
    assert "COCHRANE_LIBRARY" in graphql
    assert "Query.practice.practitioners(activeOnly" not in review
    assert "Query.patient.messages` |" not in review
    assert "Query.patient.reminders` |" not in review


def test_review_keeps_both_sources_blocked_pending_source_manifest():
    rows = _source_landscape_rows()

    assert rows["RACGP_GUIDELINES"]["readiness"] == "blocked_pending_source_manifest"
    assert rows["COCHRANE_LIBRARY"]["readiness"] == "blocked_pending_source_manifest"
    assert "no local source manifest" in rows["RACGP_GUIDELINES"]["posture"]
    assert "historical Cochrane/Wiley research note exists" in rows["COCHRANE_LIBRARY"]["posture"]
    assert any(
        "not evidence for RACGP/Cochrane readiness" in row["readiness"]
        for row in rows.values()
    )


def test_review_references_existing_cochrane_and_access_ai_provenance_without_authority():
    review = _review_text()
    cochrane_note = COCHRANE_RESEARCH_PATH.read_text(encoding="utf-8")
    knowledge_base = KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")
    compact_review = " ".join(review.split())

    assert "Wiley Agent Knowledge Base: Cochrane Library" in cochrane_note
    assert "class KnowledgeBaseQuery" in knowledge_base
    assert "Access AI knowledge-base boundaries and historical Cochrane research are referenced only as provenance" in compact_review
    assert "not a source approval, licence approval, runtime adapter, or directory-search design" in compact_review
    assert "that boundary is not a directory-search source" in compact_review


def test_review_defines_source_manifest_minimum_fields_and_completion_criteria():
    review = _review_text()
    manifest_section = review.split("## Source Manifest Minimum Fields", 1)[1].split(
        "\n## ", 1
    )[0]
    criteria_section = review.split("## Completion Criteria", 1)[1].split(
        "\n## ", 1
    )[0]

    for field in REQUIRED_MANIFEST_FIELDS:
        assert f"`{field}`" in manifest_section
    for phrase in [
        "RACGP and Cochrane are both named with current repository posture",
        "source-manifest minimum field set is documented",
        "not runtime authority",
        "the readiness DAG still has `decision: blocked`",
        "all readiness values false",
        "downstream runtime gates blocked",
        "does not mean either source is licence-approved",
    ]:
        assert phrase in criteria_section


def test_review_excludes_unapproved_directory_authority_sources():
    review = _review_text()
    requirements = review.split("## Source Review Requirements", 1)[1].split(
        "\n## ", 1
    )[0]
    exclusions = review.split("## Deliberate Exclusions", 1)[1].split("\n## ", 1)[0]

    for phrase in [
        "provider prompts",
        "RAG",
        "GraphRAG",
        "raw web retrieval",
        "practice knowledge entry",
        "web search",
        "H15/H-series material",
        "patient-specific clinical advice",
        "autonomous clinical decision-making",
    ]:
        assert phrase in requirements or phrase in exclusions


def test_review_preserves_closed_gates_and_boundary():
    review = _review_text()
    compact = " ".join(review.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in review
    assert "does not authorize" in review
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "licence compliance" in review
    assert "patient-facing client readiness" in review
