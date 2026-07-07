from pathlib import Path

import pytest

OPENAPI_PATH = Path("docs/api-spine/openapi/appointment-commands.yaml")
INDEX_PATH = Path("docs/api-spine/idempotency-continuity-index.md")

STATUS_COUNTS = {
    "ledger_wired": 4,
    "documented_gap": 4,
    "read_no_idempotency": 3,
}

REQUIRED_BLOCKED_GATE_PHRASES = {
    "proposal-only route idempotency enforcement",
    "raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement",
    "slot-search reservation or replay semantics",
    "provider calls or live provider gates",
    "runtime FGA clients",
    "external patient clients",
    "GraphQL mutations",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "model-to-database writes outside REST command handlers",
}


def _load_openapi() -> dict:
    pytest.importorskip("yaml", reason="PyYAML not installed.")
    import yaml

    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))


def _index_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in INDEX_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `/appointments/"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 5
        assert cells[0].startswith("`/appointments/")
        assert cells[0].endswith("`")
        assert cells[2].startswith("`")
        assert cells[2].endswith("`")
        rows.append(
            {
                "path": cells[0].strip("`"),
                "kind": cells[1],
                "runtime_status": cells[2].strip("`"),
                "source_sprint": cells[3],
                "source_test": cells[4].strip("`"),
            }
        )
    return rows


def test_idempotency_continuity_index_covers_openapi_command_paths():
    spec = _load_openapi()
    openapi_paths = set(spec["paths"])
    indexed_paths = {row["path"] for row in _index_rows()}

    assert indexed_paths == openapi_paths


def test_idempotency_continuity_index_pins_status_counts():
    rows = _index_rows()

    for status, expected_count in STATUS_COUNTS.items():
        actual_count = sum(row["runtime_status"] == status for row in rows)
        assert actual_count == expected_count

    assert {row["runtime_status"] for row in rows} == set(STATUS_COUNTS)


def test_idempotency_continuity_index_status_matches_path_kind():
    for row in _index_rows():
        path = row["path"]
        if path.startswith("/appointments/proposals/slot-search"):
            assert row["kind"] == "read"
            assert row["runtime_status"] == "read_no_idempotency"
            assert row["source_sprint"] == "199"
            continue
        if path.endswith("/confirm"):
            assert row["kind"] == "confirm"
            assert row["runtime_status"] == "ledger_wired"
            assert row["source_sprint"] == "145"
            continue

        assert row["kind"] == "proposal"
        assert row["runtime_status"] == "documented_gap"
        assert row["source_sprint"] == "124"


def test_idempotency_continuity_index_cites_guard_sources():
    rows = _index_rows()

    source_tests = {row["source_test"] for row in rows}
    assert "tests/test_api_spine_idempotency_audit_metadata.py" in source_tests
    assert (
        "tests/test_api_spine_confirmation_family_idempotency_checkpoint.py"
        in source_tests
    )
    assert "tests/test_api_spine_appointment_idempotency_gap.py" in source_tests
    for source_test in source_tests:
        assert Path(source_test).is_file()


def test_idempotency_continuity_index_preserves_closed_gate_boundary():
    text = INDEX_PATH.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for phrase in REQUIRED_BLOCKED_GATE_PHRASES:
        assert phrase in text
    assert "does not authorize" in text
    assert "does not prove runtime concurrency behavior" in compact
    assert "GraphQL mutations" in text
