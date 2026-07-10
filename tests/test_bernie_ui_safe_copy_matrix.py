"""Sprint 291 contract checks for Bernie UI derived-state safe copy."""

import json
from pathlib import Path


MATRIX_PATH = Path("docs/bernie-ui-derived-state-safe-copy-matrix.json")
DOC_PATH = Path("docs/bernie-ui-derived-state-safe-copy-matrix.md")
FIXTURE_PATH = Path("tests/fixtures/bernie_ui_view_model/cases.json")


def _matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def test_safe_copy_matrix_is_docs_tests_only_and_keeps_d5_closed():
    matrix = _matrix()

    assert matrix["schema_version"] == "bernie.ui_dag.safe_copy_matrix.v1"
    assert matrix["sprint"] == 291
    assert matrix["decision"] == "docs_tests_only_safe_copy_matrix"
    assert all(value is False for value in matrix["scope"].values())


def test_matrix_rows_match_canonical_view_model_fixture_state_and_flags():
    matrix = _matrix()
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixture_by_id = {item["id"]: item["expected"] for item in fixtures["cases"]}

    assert len(matrix["rows"]) == len(fixture_by_id) == 10
    for row in matrix["rows"]:
        expected = fixture_by_id[row["source_fixture_id"]]
        assert row["copy_mode"] == expected["copy_mode"]
        assert row["confirmation_state"] == expected["confirmation_state"]
        for flag, value in row["required_flags"].items():
            if flag in expected:
                assert expected[flag] is value


def test_success_and_preconfirm_copy_boundaries_are_explicit():
    matrix = _matrix()

    for row in matrix["rows"]:
        if row["confirmation_state"] == "confirmed":
            assert row["copy_mode"] == "success"
            assert row["required_flags"]["show_success_copy"] is True
            assert "backend_confirmed" in row["evidence_requirement"]
        else:
            assert row["required_flags"]["show_success_copy"] is False
            forbidden = " ".join(row["forbidden_fragments"]).lower()
            assert "booked" in forbidden
            assert "confirmed" in forbidden


def test_matrix_records_green_ariadne_shadow_classification_with_matching_human_outcome():
    matrix = _matrix()
    shadow = matrix["ariadne_s3_shadow_classification"]

    assert shadow["mode"] == "advisory_only"
    assert shadow["boundary_class"] == "green"
    assert shadow["classification"] == "allowed"
    assert shadow["human_boundary_outcome"] == "green_docs_tests_only"
    assert all(
        path == "AGENTS.md" or path.startswith(("docs/", "orchestration/", "tests/"))
        for path in shadow["observed_changed_paths"]
    )


def test_safe_copy_matrix_markdown_preserves_display_only_boundary():
    text = " ".join(DOC_PATH.read_text(encoding="utf-8").split()).lower()

    for fragment in (
        "docs/tests-only",
        "does not change diary javascript",
        "success copy is reserved for `confirmation_state=confirmed`",
        "copy is display-only, never write authority",
        "d5 runtime remains closed",
    ):
        assert fragment in text
