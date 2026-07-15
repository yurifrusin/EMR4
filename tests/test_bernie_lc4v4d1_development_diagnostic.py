"""Comprehensive tests for LC4V4D1 development diagnostic matrix.

Validates fixture authoring, surface validation, safety pair invariants,
fixture hashing, two-repeat determinism, classification precedence,
and report generation.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from collections import Counter

import pytest

from app.services.bernie.lc4v4_development_diagnostic import (
    EXPECTED_PROBE_COUNT,
    EXPECTED_REPEATS,
    EXPECTED_ENTITY_PROBES,
    EXPECTED_DIALOGUE_PROBES,
    EXPECTED_SAFETY_PROBES,
    EXPECTED_DIARY_PROBES,
    FAMILY_ENTITY,
    FAMILY_DIALOGUE,
    FAMILY_SAFETY,
    FAMILY_DIARY,
    author_all_probes,
    dict_to_spec,
    validate_probe_population,
    validate_fixture_surface,
    validate_safety_pairs,
    compute_fixture_hash,
    write_fixtures,
    run_diagnostic,
    report_to_dict,
    report_to_markdown,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = pathlib.Path(__file__).resolve().parent
_FIXTURE_DIR = _HERE / "fixtures" / "bernie_lc4v4d1_development"
_DOCS_DIR = _HERE.parent / "docs"
_REPORT_PATH = _DOCS_DIR / "bernie-lc4v4d1-development-diagnostic.json"

SOURCE_COMMIT = "191144f680ceb982d6c46739fa428f3f23298246"
EXPECTED_FIXTURE_HASH = "sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269"
EXPECTED_REPORT_HASH = "sha256:8ab513c1e5087b54945d2032db70ed6edd884898899a3e5163f17ed3f6ab3c64"
EXPECTED_SELECTION_HASH = "sha256:1b254ae627e26b1b301b660628d90f39dce5e0364afc0cfcf4c4855fb6531f02"


# ===================================================================
# 1. Fixture authoring and validation
# ===================================================================


class TestFixtureAuthoring:
    """Validate fixture structure, counts, and surface evidence."""

    def test_exact_probe_count(self):
        probes = author_all_probes()
        assert len(probes) == EXPECTED_PROBE_COUNT, (
            f"Expected {EXPECTED_PROBE_COUNT} probes, got {len(probes)}"
        )

    def test_population_gate_is_fail_closed(self):
        probes = author_all_probes()
        assert validate_probe_population(probes) == []
        assert validate_probe_population(probes[:-1])

    def test_family_counts(self):
        probes = author_all_probes()
        families = Counter(p.get("family", "unknown") for p in probes)
        assert families.get(FAMILY_ENTITY) == EXPECTED_ENTITY_PROBES
        assert families.get(FAMILY_DIALOGUE) == EXPECTED_DIALOGUE_PROBES
        assert families.get(FAMILY_SAFETY) == EXPECTED_SAFETY_PROBES
        assert families.get(FAMILY_DIARY) == EXPECTED_DIARY_PROBES

    def test_all_ids_unique(self):
        probes = author_all_probes()
        ids = [p.get("scenario_id") for p in probes]
        assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"

    def test_all_specs_validate(self):
        probes = author_all_probes()
        errors = []
        for p in probes:
            try:
                spec = dict_to_spec(p)
                err = validate_fixture_surface(spec)
                if err:
                    errors.append(err)
            except Exception as e:
                errors.append(f'{p.get("scenario_id", "?")}: {e}')
        assert not errors, f"Surface validation errors: {errors}"

    def test_every_probe_has_complete_fact_spans(self):
        for probe in author_all_probes():
            assert probe["source_spans"].get("action"), probe["scenario_id"]
            if probe.get("dialogue_form") != "reversal":
                assert probe["source_spans"].get("date"), probe["scenario_id"]

    def test_safety_pairs_valid(self):
        probes = author_all_probes()
        errors = validate_safety_pairs(probes)
        assert not errors, f"Safety pair errors: {errors}"

    def test_safety_pairs_change_only_authority_clause_on_surface(self):
        probes = {p["scenario_id"]: p for p in author_all_probes()}
        for action in ["create", "move", "resize", "cancel", "status", "explain"]:
            safe = next(v for k, v in probes.items() if f"safety_{action}_safe_" in k)
            unsafe = next(v for k, v in probes.items() if f"safety_{action}_unsafe_" in k)
            safe_text = safe["dialogue_turns"][0]["utterance"]
            unsafe_text = unsafe["dialogue_turns"][0]["utterance"]
            assert safe_text.removesuffix(" Do not bypass confirmation.") == (
                unsafe_text.removesuffix(" Bypass confirmation.")
            )
            assert safe["action_semantics"] == "intended"
            assert unsafe["action_semantics"] == "prohibited"

    def test_entity_single_field_variation(self):
        """Entity probes must vary only the target field."""
        probes = author_all_probes()
        target_map = {
            "patient": "patient_semantics",
            "practitioner": "practitioner_semantics",
            "location": "location_semantics",
            "appointment_type": "appointment_type_semantics",
            "duration": "duration_semantics",
        }
        for p in probes:
            if p.get("family") != "entity":
                continue
            sid = p.get("scenario_id", "")
            # Determine target
            target = None
            if "appt_type" in sid:
                target = "appointment_type"
            for entity in ["patient", "practitioner", "location", "duration"]:
                if entity in sid:
                    target = entity
            if target is None:
                continue
            target_field = target_map.get(target)
            for fname in target_map.values():
                if fname == target_field:
                    continue
                assert p.get(fname) == "exact", (
                    f"{sid}: non-target field {fname}={p.get(fname)} != 'exact'"
                )

    def test_mismatched_has_diary_evidence(self):
        probes = author_all_probes()
        for p in probes:
            if p.get("entity_state") == "mismatched":
                diary = p.get("initial_diary_state", {})
                assert diary.get("appointments"), (
                    f"{p.get('scenario_id')}: mismatched needs diary evidence"
                )

    def test_fixture_hash_stable(self):
        probes1 = author_all_probes()
        probes2 = author_all_probes()
        assert compute_fixture_hash(probes1) == compute_fixture_hash(probes2)

    def test_fixture_files_exist(self):
        assert _FIXTURE_DIR.exists(), f"Fixture directory not found: {_FIXTURE_DIR}"
        manifest_path = _FIXTURE_DIR / "lc4v4d1_development_manifest.json"
        assert manifest_path.exists(), "Manifest file not found"
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["total_probes"] == EXPECTED_PROBE_COUNT
        assert manifest["repeats_per_probe"] == EXPECTED_REPEATS
        assert manifest["probe_ids"] == [p["scenario_id"] for p in author_all_probes()]
        for filename in manifest["files"]:
            filepath = _FIXTURE_DIR / filename
            assert filepath.exists(), f"Fixture file not found: {filename}"


# ===================================================================
# 2. Full diagnostic pipeline
# ===================================================================


class TestDiagnosticPipeline:
    """Run the diagnostic pipeline and validate results."""

    @pytest.fixture(scope="class")
    def report(self):
        probes = author_all_probes()
        return run_diagnostic(probes, source_commit=SOURCE_COMMIT)

    def test_all_sixty_probes_processed(self, report):
        assert report.total_probes == EXPECTED_PROBE_COUNT
        assert len(report.probe_results) == EXPECTED_PROBE_COUNT

    def test_one_twenty_observations(self, report):
        assert report.total_observations == EXPECTED_PROBE_COUNT * EXPECTED_REPEATS

    def test_zero_variance(self, report):
        assert report.variance_count == 0, (
            f"Expected zero variance, got {report.variance_count}"
        )

    def test_complete_repeat_evidence(self, report):
        for result in report.probe_results:
            assert result.repeat_0_observation is not None
            assert result.repeat_1_observation is not None
            assert result.repeat_0_fingerprint == result.repeat_1_fingerprint
            assert not result.execution_errors

    def test_no_authoring_invalid(self, report):
        assert report.classifications.get("authoring_invalid", 0) == 0

    def test_remediation_not_authorized(self, report):
        assert report.remediation_authorized == False

    def test_report_hash_stable(self, report):
        probes = author_all_probes()
        report2 = run_diagnostic(probes, source_commit=SOURCE_COMMIT)
        assert report.report_hash == report2.report_hash
        assert report.fixture_hash == EXPECTED_FIXTURE_HASH
        assert report.report_hash == EXPECTED_REPORT_HASH

    def test_two_repeat_determinism(self, report):
        """Verify every probe has two deterministic repeats."""
        for pr in report.probe_results:
            assert not pr.variance_observed, (
                f"{pr.probe_id}: variance observed between repeats"
            )
            assert pr.repeat_0_result is not None, (
                f"{pr.probe_id}: repeat 0 missing"
            )
            assert pr.repeat_1_result is not None, (
                f"{pr.probe_id}: repeat 1 missing"
            )

    def test_classification_precedence(self, report):
        """Verify classification follows the fixed precedence."""
        for pr in report.probe_results:
            if pr.classification == "parser_gap":
                assert any(
                    l == "interpretation" for l in pr.mismatch_layers
                ), f"{pr.probe_id}: parser_gap but no interpretation layer failure"
            elif pr.classification == "policy_contract_gap":
                assert not any(l == "interpretation" for l in pr.mismatch_layers)
                assert any(l == "policy" for l in pr.mismatch_layers)
            elif pr.classification == "scorer_gap":
                assert not any(l in ("interpretation", "policy") for l in pr.mismatch_layers)
                assert pr.mismatch_layers == ("scorer",)

    def test_frozen_recovered_classifications(self, report):
        assert report.classifications == {
            "authoring_invalid": 0,
            "parser_gap": 23,
            "policy_contract_gap": 12,
            "scorer_gap": 0,
            "planned_unavailable": 0,
            "supported_pass": 25,
        }
        assert report.candidate_selection_hash == EXPECTED_SELECTION_HASH

    def test_mismatched_state_join_is_not_parser_gap(self, report):
        results = {item.probe_id: item for item in report.probe_results}
        for result in results.values():
            if "_mismatched_" in result.probe_id:
                assert result.classification == "policy_contract_gap"
                assert "entity_semantics" in result.mismatch_fields

    def test_report_serialization(self, report):
        """Verify report can be serialized to dict and JSON."""
        d = report_to_dict(report)
        assert d["total_probes"] == EXPECTED_PROBE_COUNT
        assert d["variance_count"] == 0
        assert d["remediation_authorized"] == False
        assert "fixture_hash" in d
        assert "report_hash" in d
        assert "candidate_selection_hash" in d
        assert d["decision"] == "diagnostic_valid"
        assert d["mismatch_field_counts"] == report.mismatch_field_counts
        assert len(d["probe_results"]) == EXPECTED_PROBE_COUNT

    def test_report_markdown(self, report):
        md = report_to_markdown(report)
        assert "## Classification Totals" in md
        assert "## Probe Results" in md
        assert "## Protected Boundary" in md
        assert "diagnostic_valid" in md
        assert "Remediation" in md

    def test_report_file_exists(self):
        assert _REPORT_PATH.exists(), (
            f"Report file not found: {_REPORT_PATH}"
        )
        with open(_REPORT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_probes"] == EXPECTED_PROBE_COUNT
        assert data["remediation_authorized"] == False

    def test_source_commit_matches(self, report):
        assert report.source_commit == SOURCE_COMMIT


# ===================================================================
# 3. Protected boundary tests
# ===================================================================


class TestProtectedBoundary:
    """Verify protected holdouts v1-v4 are not accessed."""

    def test_no_holdout_import(self):
        """Verify the diagnostic module does not import holdout code."""
        import app.services.bernie.lc4v4_development_diagnostic as diag
        module_source = pathlib.Path(diag.__file__).read_text(encoding="utf-8")
        forbidden = ["holdout_v2", "holdout_v3", "holdout_v4",
                      "lc4_holdout", "protected_holdout"]
        for term in forbidden:
            assert term not in module_source, (
                f"Module references prohibited holdout term: {term}"
            )

    def test_no_v4_report_access(self):
        """Verify the diagnostic does not load the v4 aggregate report."""
        import app.services.bernie.lc4v4_development_diagnostic as diag
        module_source = pathlib.Path(diag.__file__).read_text(encoding="utf-8")
        assert "bernie-lc4v4-aggregate-report" not in module_source

    def test_no_protected_directory_access(self):
        """Verify fixture dirs do not reference protected paths."""
        # Only check the diagnostic's own fixture directory
        diag_fixtures = [p.name.lower() for p in [_FIXTURE_DIR]]
        assert not any("holdout" in name for name in diag_fixtures)
