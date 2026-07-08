from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_PATH = ROOT / "docs" / "api-spine" / "directory-read-shape-design.md"
SOURCE_REVIEW_PATH = ROOT / "docs" / "api-spine" / "directory-source-licensing-review.md"
GAP_PATH = ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
DAG_PATH = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"
COCHRANE_RESEARCH_PATH = ROOT / "orchestration" / "research" / "cochrane_cds_pipeline.md"
KNOWLEDGE_BASE_PATH = ROOT / "app" / "services" / "ai" / "knowledge_base.py"

EXPECTED_FIELD_MAPPINGS = {
    "DirectorySearchResult.source": ("request `DirectorySource` plus approved source manifest", "manifest_required"),
    "DirectorySearchResult.query": ("normalized user query", "sanitize_required"),
    "DirectorySearchResult.items": (
        "approved local curated snapshot or approved external retrieval result",
        "source_manifest_required",
    ),
    "DirectorySearchResult.evidenceMode": (
        "source manifest evidence policy",
        "manifest_policy_default",
    ),
    "DirectoryEntry.id": ("synthetic stable directory ID", "synthetic_id_required"),
    "DirectoryEntry.code": ("approved source code, guideline code, or null", "optional_map"),
    "DirectoryEntry.title": ("approved source title metadata", "citation_required"),
    "DirectoryEntry.summary": ("approved snippet or curated summary", "bounded_summary_required"),
    "DirectoryEntry.citation": ("approved citation metadata", "citation_required"),
    "Citation.title": ("approved citation title", "citation_required"),
    "Citation.url": ("approved source URL or null", "optional_map"),
    "Citation.accessedAt": ("retrieval or snapshot timestamp", "freshness_required"),
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST directory search route",
    "adding GraphQL resolvers or GraphQL mutations",
    "adding Pydantic runtime schemas",
    "approving source manifests as runtime configuration",
    "RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "Access AI invocation wiring",
    "memory/RAG/GraphRAG runtime wiring",
    "practice-knowledge facts as directory authority",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "broad historical diary trove mining",
    "patient-specific clinical advice or autonomous clinical decision-making",
    "appointment, reminder, message, practitioner, directory, billing, result, or clinical write authority",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _design_text() -> str:
    return DESIGN_PATH.read_text(encoding="utf-8")


def _mapping_rows() -> dict[str, dict[str, str]]:
    section = _design_text().split("## Display-Safe Field Mapping", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `Directory") and not line.startswith("| `Citation"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "source": cells[1].strip("`"),
            "posture": cells[2].strip("`"),
            "notes": cells[3],
        }
    return rows


def test_design_targets_only_racgp_and_cochrane_directory_search():
    design = _design_text()
    compact_design = " ".join(design.split())
    source_review = SOURCE_REVIEW_PATH.read_text(encoding="utf-8")
    gap_text = GAP_PATH.read_text(encoding="utf-8")

    for surface in [
        "Query.directorySearch.RACGP_GUIDELINES",
        "Query.directorySearch.COCHRANE_LIBRARY",
    ]:
        assert surface in source_review
        assert surface in gap_text

    assert "source=RACGP_GUIDELINES" in design
    assert "source=COCHRANE_LIBRARY" in design
    assert "source_review_complete_source_manifest_blocked" in design
    assert "Query.practice.practitioners" not in design
    assert "Query.patient.messages" not in design
    assert "Query.patient.reminders" not in design


def test_directory_field_mapping_matches_graphql_sdl():
    rows = _mapping_rows()
    graphql = GRAPHQL_PATH.read_text(encoding="utf-8")

    assert set(rows) == set(EXPECTED_FIELD_MAPPINGS)
    for field, (source, posture) in EXPECTED_FIELD_MAPPINGS.items():
        assert rows[field]["source"] == source
        assert rows[field]["posture"] == posture

    for fragment in [
        "type DirectorySearchResult {",
        "source: DirectorySource!",
        "query: String!",
        "items: [DirectoryEntry!]!",
        "evidenceMode: EvidenceMode!",
        "type DirectoryEntry {",
        "id: ID!",
        "code: String",
        "title: String!",
        "summary: String!",
        "citation: Citation",
        "type Citation {",
        "url: String",
        "accessedAt: DateTime",
        "MANIFEST_POLICY",
        "LIVE_API_FACT",
    ]:
        assert fragment in graphql


def test_design_consumes_source_review_without_claiming_licence_or_runtime_ready():
    design = _design_text()
    compact_design = " ".join(design.split())
    source_review = SOURCE_REVIEW_PATH.read_text(encoding="utf-8")
    cochrane_note = COCHRANE_RESEARCH_PATH.read_text(encoding="utf-8")
    knowledge_base = KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")
    compact_source_review = " ".join(source_review.split())

    assert "source-manifest minimum field set" in compact_source_review
    assert "does not mean either source is licence-approved" in source_review
    assert "Wiley Agent Knowledge Base: Cochrane Library" in cochrane_note
    assert "class AccessAiKnowledgeBaseService" in knowledge_base
    assert "current RACGP/Cochrane manifests do not exist" in design
    assert "not `Query.directorySearch` implementation evidence" in design
    assert "does not approve a source manifest" in compact_design
    assert "does not approve either source for runtime, licence, clinical, or patient-facing use" in compact_design


def test_known_shape_gaps_keep_source_and_runtime_unavailable():
    section = _design_text().split("## Known Shape Gaps", 1)[1].split("\n## ", 1)[0]
    compact = " ".join(section.split())

    for phrase in [
        "No source manifest exists",
        "No licensing decision",
        "No route path, response schema, pagination model, empty-result shape, error shape, or entitlement policy",
        "`Citation` lacks fields for source label, evidence type, publication date, DOI, licence scope, and version",
        "`EvidenceMode.LIVE_API_FACT` would imply a live source path",
        "deny PHI-bearing directory queries",
        "Summary text cannot be designed as raw retrieved passages",
    ]:
        assert phrase in compact


def test_future_route_requirements_remain_read_only_cited_and_fail_closed():
    section = _design_text().split("## Future Route Requirements", 1)[1].split(
        "\n## ", 1
    )[0]
    compact = " ".join(section.split())

    for phrase in [
        "read-only GET surface",
        "must not expose patient identity or accept PHI unless a source manifest explicitly approves it",
        "deny unknown, unmanifested, expired, blocked, or out-of-scope source manifests by default",
        "only `source`, sanitized `query`, bounded `items`, and `evidenceMode`",
        "citation-backed results must include title and freshness metadata",
        "stable IDs must be synthetic",
        "must honor the requested `limit` only within a reviewed maximum",
        "ordering must be deterministic",
        "must not silently fall back to LLM text, practice knowledge, RAG, GraphRAG, or raw web search",
        "must not be used as provider, RAG, GraphRAG, Access AI, clinical decision-making, patient-facing advice, or external patient-client authority",
    ]:
        assert phrase in compact


def test_design_updates_dag_artifact_and_preserves_blocked_runtime_posture():
    dag = DAG_PATH.read_text(encoding="utf-8")

    assert '"id": "directory_read_shape_design"' in dag
    assert '"status": "design_complete_no_runtime"' in dag
    assert '"artifact": "docs/api-spine/directory-read-shape-design.md"' in dag
    assert (
        '"artifact": "docs/api-spine/external-read-model-combined-readiness-review.md"'
        in dag
    )
    for fragment in [
        '"external_read_model_runtime_ready": false',
        '"graphql_resolver_ready": false',
        '"rest_route_ready": false',
        '"provider_or_directory_runtime_ready": false',
        '"runtime_or_memory_ready": false',
        '"write_authority_ready": false',
    ]:
        assert fragment in dag


def test_design_preserves_closed_gates_and_boundary():
    design = _design_text()
    compact = " ".join(design.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in design
    assert "does not authorize" in design
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "licence compliance" in compact
    assert "patient-facing client readiness" in design
