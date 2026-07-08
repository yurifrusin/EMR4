from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = (
    ROOT / "docs" / "api-spine" / "blueprint-first-model-second-boundary.md"
)


REQUIRED_PHRASES = {
    "Bernie interprets; the backend blueprint decides; signed command routes",
    "Workflow path is code-owned.",
    "Model output is interpretation, not authority.",
    "Tools are purpose-built controls, not raw database levers.",
    "GraphQL remains a scoped read/context graph only.",
    "REST/OpenAPI command routes own irreversible, high-risk, external, or",
    "Confirmation commands echo signed evidence/freshness and revalidate before",
}


REQUIRED_CLOSED_GATES = {
    "provider prompt wiring or live provider calls",
    "provider dry-run wiring",
    "GraphQL mutations",
    "memory/RAG/GraphRAG runtime wiring",
    "H15/H-series runtime imports",
    "historical diary material access",
    "broad historical diary trove mining",
    "external patient clients",
    "runtime FGA clients",
    "raw route mutation authority",
    "direct database writes by model output",
    "model-to-database writes outside REST command handlers",
}


FORBIDDEN_AUTHORITY_CLAIMS = {
    "this note authorizes",
    "model may authorize writes",
    "model can authorize writes",
    "model owns the workflow",
    "model decides the workflow",
    "Bernie owns the workflow",
    "Bernie may bypass confirmation",
    "Bernie should get a generic",
    "Bernie may write appointment rows",
    "Bernie can write appointment rows",
    "GraphQL mutation is allowed",
    "live provider calls are authorized",
}


def _text() -> str:
    return BOUNDARY_PATH.read_text(encoding="utf-8")


def test_blueprint_first_boundary_note_exists():
    assert BOUNDARY_PATH.is_file()
    assert _text().startswith("# Blueprint First, Model Second Boundary")


def test_blueprint_first_boundary_records_core_api_spine_mapping():
    text = _text()

    for phrase in REQUIRED_PHRASES:
        assert phrase in text


def test_blueprint_first_boundary_preserves_closed_gates():
    text = _text()

    assert "This note does not authorize:" in text
    for gate in REQUIRED_CLOSED_GATES:
        assert gate in text


def test_blueprint_first_boundary_does_not_claim_model_write_authority():
    normalized = _text().lower()

    for phrase in FORBIDDEN_AUTHORITY_CLAIMS:
        assert phrase.lower() not in normalized


def test_blueprint_first_boundary_requires_future_runtime_preflight():
    text = _text()

    assert "Name the deterministic blueprint that owns the workflow path." in text
    assert "Name the exact bounded model subtask." in text
    assert "Name the typed validation that accepts or rejects the model output." in text
    assert "Re-run the relevant readiness/provider boundary command" in text
