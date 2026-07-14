"""Tests for the bernie_coverage_lattice CLI script.

Covers:
    1. Running against the committed fixturres produces valid JSON.
    2. JSON has required top-level keys.
    3. Empty cells list is non-empty (proves the lattice shows gaps).
    4. Each empty cell has the required dimension fields.
    5. Missing fixture directory produces non-zero exit.
    6. Empty fixture directory produces non-zero exit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
FIXTURE_DIR = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "bernie_scenario_spec"
)
CANDIDATE_DIR = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "bernie_corpus_candidates"
)
LATTICE_SCRIPT = SCRIPTS_DIR / "bernie_coverage_lattice.py"
PYTHON = sys.executable


def _run_lattice(
    fixture_dir: str | None = None,
    candidate_dir: str | None = None,
) -> subprocess.CompletedProcess:
    cmd = [PYTHON, str(LATTICE_SCRIPT)]
    if fixture_dir is not None:
        cmd.extend(["--fixture-dir", fixture_dir])
    if candidate_dir is not None:
        cmd.extend(["--candidate-dir", candidate_dir])
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=SCRIPTS_DIR.parent,
    )


# ---------------------------------------------------------------------------
# 1.  Script runs and produces valid JSON
# ---------------------------------------------------------------------------

class TestRunsSuccessfully:
    """The script runs and emits valid JSON."""

    def test_script_runs_and_returns_zero(self) -> None:
        result = _run_lattice()
        assert result.returncode == 0, (
            f"Non-zero exit {result.returncode}: stderr={result.stderr}"
        )

    def test_output_is_valid_json(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_output_has_expected_structure(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        assert "schema_version" in data
        assert data["schema_version"] == "lc1.coverage_lattice.v1"


# ---------------------------------------------------------------------------
# 2.  Required top-level keys
# ---------------------------------------------------------------------------

class TestRequiredKeys:
    """JSON output contains the required top-level keys."""

    def _get_report(self) -> Dict[str, Any]:
        result = _run_lattice()
        return json.loads(result.stdout)

    def test_has_scenario_count(self) -> None:
        report = self._get_report()
        assert "scenario_count" in report

    def test_has_dimensions(self) -> None:
        report = self._get_report()
        assert "dimensions" in report

    def test_has_empty_cells(self) -> None:
        report = self._get_report()
        assert "empty_cells" in report

    def test_has_family_summary(self) -> None:
        report = self._get_report()
        assert "family_summary" in report

    def test_has_covered_cell_count(self) -> None:
        report = self._get_report()
        assert "covered_cell_count" in report

    def test_has_total_cell_count(self) -> None:
        report = self._get_report()
        assert "total_cell_count" in report

    def test_has_complete_gap_summary_and_empty_count(self) -> None:
        report = self._get_report()
        assert report["empty_cell_count"] > 0
        assert set(report["gap_summary"]) == {
            "diary_action",
            "diary_state",
            "entity_state",
            "temporal_form",
            "dialogue_form",
            "language_form",
        }


# ---------------------------------------------------------------------------
# 3.  Empty cells list is non-empty
# ---------------------------------------------------------------------------

class TestEmptyCells:
    """The lattice shows gaps (empty cells are non-empty)."""

    def test_empty_cells_is_non_empty(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        empty = data.get("empty_cells", [])
        assert len(empty) > 0, (
            "Expected empty cells (gaps) in the coverage lattice, "
            "but the list is empty"
        )

    def test_covered_less_than_total(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        assert data["covered_cell_count"] < data["total_cell_count"], (
            "Covered cells should be less than total in a sparse lattice"
        )


# ---------------------------------------------------------------------------
# 4.  Empty cell structure
# ---------------------------------------------------------------------------

class TestEmptyCellStructure:
    """Each empty cell has the required dimension fields."""

    def test_empty_cell_has_diary_action(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        cell = data["empty_cells"][0]
        assert "diary_action" in cell

    def test_empty_cell_has_diary_state(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        cell = data["empty_cells"][0]
        assert "diary_state" in cell

    def test_empty_cell_has_temporal_form(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        cell = data["empty_cells"][0]
        assert "temporal_form" in cell

    def test_empty_cell_has_entity_state(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        assert "entity_state" in data["empty_cells"][0]

    def test_empty_cell_has_dialogue_form(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        cell = data["empty_cells"][0]
        assert "dialogue_form" in cell

    def test_empty_cell_has_language_form(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        cell = data["empty_cells"][0]
        assert "language_form" in cell

    def test_empty_cell_values_are_strings(self) -> None:
        result = _run_lattice()
        data = json.loads(result.stdout)
        cell = data["empty_cells"][0]
        for key in ("diary_action", "diary_state", "entity_state", "temporal_form",
                    "dialogue_form", "language_form"):
            assert isinstance(cell[key], str), (
                f"{key} is not a string: {type(cell[key])}"
            )


# ---------------------------------------------------------------------------
# 5.  Missing fixture directory
# ---------------------------------------------------------------------------

class TestMissingDirectory:
    """Missing fixture directory produces non-zero exit."""

    def test_missing_dir_returns_nonzero(self) -> None:
        result = _run_lattice(fixture_dir="/tmp/nonexistent-bernie-fixtures-xyz")
        assert result.returncode != 0

    def test_missing_dir_prints_error(self) -> None:
        result = _run_lattice(fixture_dir="/tmp/nonexistent-bernie-fixtures-xyz")
        assert "ERROR" in result.stderr


# ---------------------------------------------------------------------------
# 6.  Empty fixture directory
# ---------------------------------------------------------------------------

class TestEmptyDirectory:
    """Empty fixture directory produces non-zero exit."""

    @pytest.fixture
    def empty_dir(self, tmp_path: Path) -> str:
        d = tmp_path / "empty_fixtures"
        d.mkdir(parents=True)
        return str(d)

    def test_empty_dir_returns_nonzero(self, empty_dir: str) -> None:
        result = _run_lattice(fixture_dir=empty_dir)
        assert result.returncode != 0

    def test_empty_dir_prints_error(self, empty_dir: str) -> None:
        result = _run_lattice(fixture_dir=empty_dir)
        assert "ERROR" in result.stderr


# ---------------------------------------------------------------------------
# 7.  Strict loading rejects unknown fixture files
# ---------------------------------------------------------------------------

class TestStrictLoading:
    """The CLI must reject unknown files (strict canonical loader)."""

    def test_unknown_fixture_rejected(self, tmp_path: Path) -> None:
        """A directory with an unknown JSON file is rejected."""
        d = tmp_path / "bad_fixtures"
        d.mkdir(parents=True)
        # Create an unknown fixture file
        (d / "unknown_file.json").write_text(
            json.dumps({"spec_version": "lc1.v1", "description": "bad"}),
            encoding="utf-8",
        )
        result = _run_lattice(fixture_dir=str(d))
        assert result.returncode != 0
        assert "ERROR" in result.stderr or "Unknown fixture file" in result.stderr

    def test_non_list_payload_rejected(self, tmp_path: Path) -> None:
        """A non-list payload in the fixture directory is rejected."""
        d = tmp_path / "bad_payload"
        d.mkdir(parents=True)
        (d / "booking_create_then_exact_duplicate.json").write_text(
            json.dumps({"not": "a list"}),
            encoding="utf-8",
        )
        result = _run_lattice(fixture_dir=str(d))
        assert result.returncode != 0
        assert "ERROR" in result.stderr or "Unknown fixture file" in result.stderr

    @staticmethod
    def _copy_candidate_manifest(target: Path) -> None:
        target.mkdir(parents=True)
        for source in CANDIDATE_DIR.glob("*.json"):
            (target / source.name).write_text(
                source.read_text(encoding="utf-8"), encoding="utf-8"
            )

    def test_candidate_unknown_file_rejected(self, tmp_path: Path) -> None:
        candidate_dir = tmp_path / "candidates"
        self._copy_candidate_manifest(candidate_dir)
        (candidate_dir / "unexpected.json").write_text("[]", encoding="utf-8")

        result = _run_lattice(candidate_dir=str(candidate_dir))

        assert result.returncode != 0
        assert "ERROR: Unknown family file" in result.stderr

    def test_candidate_non_list_payload_rejected(self, tmp_path: Path) -> None:
        candidate_dir = tmp_path / "candidates"
        self._copy_candidate_manifest(candidate_dir)
        (candidate_dir / "paraphrase_family.json").write_text(
            json.dumps({"not": "an array"}), encoding="utf-8"
        )

        result = _run_lattice(candidate_dir=str(candidate_dir))

        assert result.returncode != 0
        assert "ERROR: LC2 family file paraphrase_family.json must contain a JSON array" in result.stderr

    def test_candidate_wrong_tier_rejected(self, tmp_path: Path) -> None:
        candidate_dir = tmp_path / "candidates"
        self._copy_candidate_manifest(candidate_dir)
        path = candidate_dir / "paraphrase_family.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[0]["provenance"] = "gold"
        path.write_text(json.dumps(payload), encoding="utf-8")

        result = _run_lattice(candidate_dir=str(candidate_dir))

        assert result.returncode != 0
        assert "ERROR:" in result.stderr
