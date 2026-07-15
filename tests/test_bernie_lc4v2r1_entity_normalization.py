"""Focused tests for LC4V2R1 frozen entity/normalization fixture.

Validates the 21-case Sol-authored development matrix against the
deterministic extraction boundary, including schema, hash, entity
relations, normalized shapes, baseline counts, and safety invariants.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from app.services.bernie.semantic_extraction import (
    SemanticExtraction,
    extract_semantics,
)
from scripts.bernie_lc4v2r1_entity_normalization import (
    BASELINE_PATH,
    EXPECTED_BASELINE_COUNTS,
    REPORT_PATH,
    _compute_report_hash,
    _report_is_accepted,
    _selection_hash,
    _validate_baseline,
    build_report,
)

FIXTURE_PATH = Path(
    "tests/fixtures/bernie_lc4v2r1_development/entity_normalization_cases.json"
)

# Contract constants
EXPECTED_FIXTURE_SHA256 = (
    "0f957518d1481ce831a55ca8d12388f245ae89ae516e96ef1d5037080d925afd"
)
EXPECTED_CASE_COUNT = 21
EXPECTED_SCHEMA_VERSION = "lc4v2r1.entity_normalization_development.v1"
ALLOWED_RELATIONS = {"exact", "omitted", "ambiguous", "corrected", "negated"}

# Baseline pass counts (from committed baseline at 7abf3aa9)
BASELINE_PASS_COUNTS = {
    "normalized_values": 17,
    "entity_semantics": 5,
    "requires_clarification": 17,
    "authority": 17,
    "tool_safety": 17,
    "claims_action_completed": 21,
    "complete": 4,
}
BASELINE_FAILED_SELECTION_HASH = "ddfbc280bb822993"


# ---------------------------------------------------------------------------
# Fixture loading and validation
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def fixture_data() -> dict:
    """Load the frozen fixture once per session."""
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def fixture_hash() -> str:
    """Compute fixture SHA-256 once."""
    return hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()


@pytest.fixture
def ref_date(fixture_data: dict) -> str:
    return fixture_data.get("reference_date", "2026-07-15")


# ============================================================
# Fixture integrity tests
# ============================================================


class TestFixtureIntegrity:
    """The frozen fixture must match the contract exactly."""

    def test_fixture_sha256(self, fixture_hash: str):
        assert fixture_hash == EXPECTED_FIXTURE_SHA256, (
            f"Fixture hash mismatch: got {fixture_hash}, "
            f"expected {EXPECTED_FIXTURE_SHA256}"
        )

    def test_fixture_case_count(self, fixture_data: dict):
        assert len(fixture_data["cases"]) == EXPECTED_CASE_COUNT

    def test_fixture_schema_version(self, fixture_data: dict):
        assert fixture_data.get("schema_version") == EXPECTED_SCHEMA_VERSION

    def test_all_case_ids_unique(self, fixture_data: dict):
        ids = [c["case_id"] for c in fixture_data["cases"]]
        assert len(ids) == len(set(ids)), "Duplicate case IDs found"

    def test_all_relations_allowed(self, fixture_data: dict):
        for case in fixture_data["cases"]:
            for entity, relation in case.get(
                "expected_entity_semantics", {}
            ).items():
                assert relation in ALLOWED_RELATIONS, (
                    f"Case {case['case_id']}: unknown relation "
                    f"'{relation}' for entity '{entity}'"
                )

    def test_forbidden_expected_fields_absent(self):
        """Expected fields must never enter the extraction boundary."""
        with open(FIXTURE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for case in data["cases"]:
            extraction = extract_semantics(
                case["utterances"],
                data.get("reference_date", "2026-07-15"),
            )
            for forbidden in (
                "expected_normalized_values",
                "mutating_tools_allowed",
            ):
                assert not hasattr(extraction, forbidden), (
                    f"Case {case['case_id']}: forbidden field "
                    f"'{forbidden}' leaked into extraction"
                )

    def test_extraction_boundary_accepts_only_surface_and_reference_date(self):
        assert tuple(inspect.signature(extract_semantics).parameters) == (
            "utterances",
            "reference_date",
        )


# ============================================================
# Per-case extraction tests (parameterized)
# ============================================================


class TestEntityNormalizationCases:
    """Every fixture case must pass all contracted dimensions."""

    @pytest.mark.parametrize(
        ("case"),
        [
            pytest.param(c, id=c["case_id"])
            for c in json.loads(FIXTURE_PATH.read_bytes())["cases"]
        ],
    )
    def test_case_extraction(self, case: dict, ref_date: str):
        result = extract_semantics(case["utterances"], ref_date)
        _assert_case(case, result)


def _assert_case(case: dict, result: SemanticExtraction):
    """Assert all contracted dimensions for a single case."""
    case_id = case["case_id"]
    expected_nv = case.get("expected_normalized_values", {})
    expected_es = case.get("expected_entity_semantics", {})
    expected_clarify = case.get("expected_requires_clarification", False)
    expected_authority = case.get("expected_authority", "read")
    expected_mutation = case.get("mutating_tools_allowed", True)

    # --- Normalized values ---
    for key, expected_val in expected_nv.items():
        actual_val = result.normalized_values.get(key)
        assert actual_val == expected_val, (
            f"[{case_id}] normalized_values['{key}']: "
            f"expected {expected_val!r}, got {actual_val!r}"
        )

    # --- Entity semantics ---
    for entity, expected_rel in expected_es.items():
        actual_rel = result.entity_semantics.get(entity, "omitted")
        assert actual_rel == expected_rel, (
            f"[{case_id}] entity_semantics['{entity}']: "
            f"expected {expected_rel!r}, got {actual_rel!r}"
        )

    # --- Clarification ---
    assert result.requires_clarification is expected_clarify, (
        f"[{case_id}] requires_clarification: "
        f"expected {expected_clarify}, got {result.requires_clarification}"
    )

    # --- Authority ---
    assert result.authority_claim == expected_authority, (
        f"[{case_id}] authority_claim: expected {expected_authority!r}, "
        f"got {result.authority_claim!r}"
    )

    # --- claims_action_completed ---
    assert result.claims_action_completed is False, (
        f"[{case_id}] claims_action_completed must be False"
    )

    # --- Tool safety / mutation ---
    if not expected_mutation:
        for tool in (
            "create_booking",
            "update_appointment",
            "change_appointment_status",
        ):
            assert tool not in result.selected_tool_sequence, (
                f"[{case_id}] mutation tool {tool!r} selected despite "
                f"mutating_tools_allowed=False"
            )
        if result.requires_clarification:
            assert "request_clarification" in result.selected_tool_sequence, (
                f"[{case_id}] expected request_clarification in tools"
            )


# ============================================================
# Baseline immutability tests
# ============================================================


class TestBaselineImmutability:
    """The committed baseline counts must match known values."""

    def test_baseline_counts_preserved(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        _validate_baseline(baseline)
        assert baseline["pass_counts"] == BASELINE_PASS_COUNTS
        assert baseline["pass_counts"] == EXPECTED_BASELINE_COUNTS

    def test_baseline_selection_hash_preserved(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        failed_ids = [
            item["case_id"] for item in baseline["findings"]
            if item["failed_dimensions"]
        ]
        assert _selection_hash(failed_ids) == BASELINE_FAILED_SELECTION_HASH

    @pytest.mark.parametrize(
        ("field", "replacement"),
        [
            ("parser_source_commit", "0" * 40),
            ("failed_selection_hash", "0" * 16),
            ("failed_case_count", 16),
        ],
    )
    def test_baseline_metadata_drift_fails_closed(self, field, replacement):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        mutated = deepcopy(baseline)
        mutated[field] = replacement
        with pytest.raises(ValueError):
            _validate_baseline(mutated)

    def test_baseline_pass_count_drift_fails_closed(self):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        mutated = deepcopy(baseline)
        mutated["pass_counts"]["complete"] = 5
        with pytest.raises(ValueError):
            _validate_baseline(mutated)


# ============================================================
# False-positive protection tests
# ============================================================


class TestFalsePositiveProtection:
    """Entity extractors must not capture names as wrong entity types."""

    def test_patient_name_not_location(self):
        result = extract_semantics(
            [
                "Book Margaret Thompson with Dr Chen tomorrow at 3pm "
                "for 30 minutes."
            ],
            "2026-07-15",
        )
        assert result.entity_semantics["location"] == "omitted"

    def test_patient_name_not_appointment_type(self):
        result = extract_semantics(
            [
                "Book Margaret Thompson with Dr Chen tomorrow at 3pm "
                "for 30 minutes."
            ],
            "2026-07-15",
        )
        assert result.entity_semantics["appointment_type"] == "omitted"

    def test_practitioner_name_not_location(self):
        result = extract_semantics(
            [
                "Book Avery Quinn with Dr Chen tomorrow at 3pm "
                "for 30 minutes."
            ],
            "2026-07-15",
        )
        assert result.entity_semantics["location"] == "omitted"

    def test_numbered_room_not_patient(self):
        result = extract_semantics(
            [
                "Book Avery Quinn with Dr Chen tomorrow at 3pm "
                "for 30 minutes in Room 12."
            ],
            "2026-07-15",
        )
        assert result.entity_semantics["patient"] == "exact"

    def test_negated_action_does_not_negate_patient_entity(self):
        result = extract_semantics(
            ["Do not book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes."],
            "2026-07-15",
        )
        assert result.action_negated is True
        assert result.entity_semantics["patient"] == "exact"
        assert result.entity_semantics["duration"] == "exact"

    def test_negated_location_before_clause_does_not_negate_action(self):
        result = extract_semantics(
            ["Not Room 2; book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes."],
            "2026-07-15",
        )
        assert result.action_negated is False
        assert result.entity_semantics["location"] == "negated"
        assert result.entity_semantics["duration"] == "exact"

    def test_long_consultation_is_not_ambiguous_duration(self):
        result = extract_semantics(
            ["Book Avery Quinn with Dr Chen tomorrow at 3pm as a long consultation."],
            "2026-07-15",
        )
        assert result.entity_semantics["appointment_type"] == "exact"
        assert result.entity_semantics["duration"] == "omitted"


# ============================================================
# Temporal interval regression test
# ============================================================


class TestTemporalIntervalRegression:
    """Independent interval example plus existing time forms."""

    def test_after_3_before_4_30(self):
        result = extract_semantics(
            ["Book Margaret Thompson tomorrow after 3 but before 4:30"],
            "2026-07-15",
        )
        assert result.temporal_relation == "interval"
        assert result.earliest_time == "15:00"
        assert result.latest_time == "16:30"

    def test_decimal_time_within_interval(self):
        result = extract_semantics(
            [
                "Book Margaret Thompson tomorrow at 3.15pm "
                "for 30 minutes"
            ],
            "2026-07-15",
        )
        assert result.earliest_time == "15:15"

    def test_colon_time_within_interval(self):
        result = extract_semantics(
            [
                "Book Margaret Thompson tomorrow at 3:15pm "
                "for 30 minutes"
            ],
            "2026-07-15",
        )
        assert result.earliest_time == "15:15"


# ============================================================
# Deterministic repeat / zero variance
# ============================================================


class TestDeterministicRepeat:
    """Two runs of the full fixture must produce identical results."""

    def test_two_repeats_have_zero_variance(self, fixture_data: dict, ref_date: str):
        results_1: list[SemanticExtraction] = []
        for case in fixture_data["cases"]:
            results_1.append(extract_semantics(case["utterances"], ref_date))

        results_2: list[SemanticExtraction] = []
        for case in fixture_data["cases"]:
            results_2.append(extract_semantics(case["utterances"], ref_date))

        for i, (r1, r2) in enumerate(zip(results_1, results_2)):
            case_id = fixture_data["cases"][i]["case_id"]
            assert r1 == r2, (
                f"Variance detected in case {case_id}: "
                f"two identical runs differ"
            )


class TestAuditReceipt:
    def test_report_hash_and_all_dimensions_are_bound(self):
        report = build_report()
        assert report["report_hash"] == _compute_report_hash(report)
        assert report["assertions"]["baseline_is_exactly_bound"] is True
        assert report["assertions"]["all_dimensions_21_of_21"] is True
        assert report["failed_selection_hash"] == _selection_hash([])

    def test_report_hash_mutation_fails_closed(self):
        report = build_report()
        report["report_hash"] = "sha256:" + "0" * 64
        assert _report_is_accepted(report) is False

    def test_check_mode_is_non_mutating(self):
        before = REPORT_PATH.read_bytes()
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/bernie_lc4v2r1_entity_normalization.py",
                "--check",
            ],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert REPORT_PATH.read_bytes() == before
