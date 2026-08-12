from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal import (
    EVIDENCE_PATH,
    EXPECTED_GAPS,
    EXPECTED_PROJECTION_FIELDS,
    EXPECTED_RECORD_FIELDS,
    EXPECTED_SEMANTIC_DIGESTS,
    EXPECTED_SOURCE_BINDINGS,
    EXPECTED_SOURCE_HEAD,
    SCENARIO_SPECS,
    SCHEMA_PATH,
    _canonical_digest,
    build_evidence,
    build_projection,
    build_report,
    expected_semantic_candidate,
    hostile_mutations,
    load_evidence,
    load_schema,
    validate_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-design.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal.py"


def _rows() -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in load_evidence()["scenario_results"]}


def test_closed_evidence_replays_exactly_and_report_passes() -> None:
    packet = load_evidence()
    Draft202012Validator(load_schema()).validate(packet)
    assert packet == build_evidence()
    assert validate_evidence(packet, verify_source_files=True) == []
    assert build_report(packet) == {
        "schema_version": "emr4.authored-synthetic-shadow-comparison-report.v1",
        "status": "passed",
        "reasons": [],
        "source_head": EXPECTED_SOURCE_HEAD,
        "scenario_count": 18,
        "disabled_count": 6,
        "admitted_count": 12,
        "primary_byte_equal_count": 18,
        "diagnostic_record_count": 9,
        "maximum_records_per_scenario": 1,
        "hostile_mutation_count": 51,
        "hostile_mutation_escape_count": 0,
        "application_route_imported_or_executed": False,
        "observer_runtime_created": False,
        "provider_call_count": 0,
        "command_or_write_performed": False,
    }


def test_source_bindings_are_exact_and_current() -> None:
    packet = load_evidence()
    assert packet["source_head"] == EXPECTED_SOURCE_HEAD
    assert {
        row["path"]: row["sha256"] for row in packet["source_bindings"]
    } == EXPECTED_SOURCE_BINDINGS
    assert validate_evidence(packet, verify_source_files=True) == []


def test_exact_eighteen_scenario_population_is_frozen() -> None:
    packet = load_evidence()
    assert len(SCENARIO_SPECS) == 18
    assert [row["scenario_id"] for row in packet["scenario_results"]] == [
        row["scenario_id"] for row in SCENARIO_SPECS
    ]
    assert packet["summary"]["disabled_count"] == 6
    assert packet["summary"]["admitted_count"] == 12


def test_six_default_denials_never_call_adapter_or_emit_record() -> None:
    denied = [
        row for row in load_evidence()["scenario_results"]
        if row["case_kind"] == "disabled"
    ]
    assert len(denied) == 6
    for row in denied:
        observed = row["observed"]
        assert observed["admission_decision"] == "disabled_no_observation"
        assert observed["adapter_called"] is False
        assert observed["comparison_class"] == "disabled_no_observation"
        assert observed["record_candidate_count"] == 0
        assert observed["diagnostic_records"] == []


def test_four_admitted_current_routes_reproduce_exact_parent_gaps() -> None:
    expected = [
        row for row in load_evidence()["scenario_results"]
        if row["case_kind"] == "admitted_expected_gap"
    ]
    assert {row["route_adapter_id"] for row in expected} == {
        "raw_compat_create",
        "raw_compat_update",
        "raw_compat_status",
        "raw_compat_delete",
    }
    for row in expected:
        assert row["controls"] == {
            "generation_status": "current",
            "global_state": "enabled",
            "practice_state": "enabled",
            "route_allowed": True,
            "externally_disabled": False,
        }
        observed = row["observed"]
        assert observed["adapter_called"] is True
        assert observed["adapter_result"] == "adapter_rejected"
        assert observed["gap_codes"] == EXPECTED_GAPS
        assert observed["comparison_class"] == "expected_current_gap_match"


def test_unexpected_gap_and_candidate_are_distinguished() -> None:
    rows = _rows()
    gap = rows["shd-011-unexpected-gap-set"]["observed"]
    assert gap["adapter_result"] == "adapter_rejected"
    assert gap["gap_codes"] == [
        "confirmation_evidence_missing",
        "idempotency_identity_missing",
    ]
    assert gap["comparison_class"] == "unexpected_gap_set"

    candidate = rows["shd-012-unexpected-candidate"]["observed"]
    assert candidate["adapter_result"] == "candidate_mapped"
    assert candidate["gap_codes"] == []
    assert candidate["comparison_class"] == "unexpected_candidate_mapped"


def test_equivalent_and_single_field_divergent_candidates_are_exact() -> None:
    rows = _rows()
    equivalent = rows["shd-013-candidate-equivalent"]["observed"]
    assert equivalent["comparison_class"] == "candidate_projection_equivalent"
    assert equivalent["mismatch_field_codes"] == []
    divergent = rows["shd-014-candidate-divergent"]["observed"]
    assert divergent["comparison_class"] == "candidate_projection_divergent"
    assert divergent["mismatch_field_codes"] == ["command_digest"]


def test_semantic_expectations_are_independently_digest_bound() -> None:
    packet = load_evidence()
    assert packet["semantic_expectation_digests"] == EXPECTED_SEMANTIC_DIGESTS
    for route_adapter_id, digest in EXPECTED_SEMANTIC_DIGESTS.items():
        assert _canonical_digest(expected_semantic_candidate(route_adapter_id)) == digest


def test_observer_timeout_overflow_and_sink_failures_are_contained() -> None:
    rows = _rows()
    observer = rows["shd-015-observer-failure"]["observed"]
    assert observer["adapter_called"] is False
    assert observer["comparison_class"] == "observer_failed"
    assert observer["record_candidate_count"] == 1
    assert observer["diagnostic_record_count"] == 1

    timeout = rows["shd-016-timeout-drop"]["observed"]
    overflow = rows["shd-017-overflow-drop"]["observed"]
    for observed, disposition in (
        (timeout, "timeout_dropped"),
        (overflow, "overflow_dropped"),
    ):
        assert observed["adapter_called"] is False
        assert observed["observation_disposition"] == disposition
        assert observed["record_candidate_count"] == 0
        assert observed["diagnostic_records"] == []

    sink = rows["shd-018-sink-failure-drop"]["observed"]
    assert sink["adapter_called"] is True
    assert sink["record_candidate_count"] == 1
    assert sink["diagnostic_record_count"] == 0
    assert sink["diagnostic_records"] == []
    assert sink["observation_disposition"] == "sink_failure_dropped"


def test_every_primary_result_is_byte_equal_and_no_retry_or_outcome_exists() -> None:
    for row in load_evidence()["scenario_results"]:
        observed = row["observed"]
        assert observed["primary_bytes_equal"] is True
        assert observed["primary_before_sha256"] == observed["primary_after_sha256"]
        assert observed["retry_count"] == 0
        assert observed["command_outcome"] is None


def test_records_are_exact_minimized_and_bounded_to_one() -> None:
    forbidden = {
        "raw_projection",
        "kernel_candidate",
        "raw_request_body",
        "raw_response_body",
        "direct_identifier",
        "patient_data",
        "free_text",
        "token",
        "credential",
        "source_state",
        "authority_decision",
        "command_outcome",
        "mutation_receipt",
        "audit_receipt",
    }
    for row in load_evidence()["scenario_results"]:
        observed = row["observed"]
        assert observed["diagnostic_record_count"] <= 1
        assert observed["record_candidate_count"] <= 1
        assert observed["diagnostic_record_count"] == len(
            observed["diagnostic_records"]
        )
        for record in observed["diagnostic_records"]:
            assert list(record) == EXPECTED_RECORD_FIELDS
            assert set(record).isdisjoint(forbidden)


def test_projection_is_exact_digest_only_and_never_enters_evidence_record() -> None:
    for route_adapter_id in EXPECTED_SEMANTIC_DIGESTS:
        projection = build_projection(route_adapter_id, "raw_future_complete")
        assert list(projection) == EXPECTED_PROJECTION_FIELDS
        assert projection["practice_scope_digest"].startswith("syn-")
        assert projection["actor_digest"].startswith("syn-")
        assert projection["session_digest"].startswith("syn-")
    evidence_text = EVIDENCE_PATH.read_text(encoding="utf-8")
    assert '"raw_projection"' not in evidence_text
    assert '"kernel_candidate"' not in evidence_text
    assert '"response_body"' not in evidence_text


def test_all_fifty_one_hostile_mutations_fail_closed() -> None:
    packet = load_evidence()
    mutants = hostile_mutations(packet)
    assert len(mutants) == 51
    assert [name for name, mutant in mutants if not validate_evidence(mutant)] == []


def test_schema_closes_every_declared_object() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                assert node.get("additionalProperties") is False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)


def test_evaluator_imports_no_application_database_network_provider_or_process() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imports: set[str] = set()
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
            imports.add(node.module.split(".")[0])
    assert imports <= {
        "__future__",
        "argparse",
        "copy",
        "hashlib",
        "json",
        "jsonschema",
        "pathlib",
        "scripts",
        "typing",
    }
    assert imports.isdisjoint(
        {"app", "sqlalchemy", "psycopg", "requests", "httpx", "google", "socket", "subprocess"}
    )
    assert all("app." not in module for module in imported_modules)


def test_plan_design_and_threat_freeze_unmounted_no_feedback_boundary() -> None:
    text = " ".join(
        " ".join(path.read_text(encoding="utf-8").lower().split())
        for path in (PLAN, DESIGN, THREAT)
    )
    for phrase in (
        "provider-free",
        "unmounted",
        "authored-synthetic",
        "byte-for-byte",
        "at most one",
        "no application",
        "no runtime",
        "no command outcome",
        "patient",
        "protected-ref",
    ):
        assert phrase in text


def test_all_owned_precloseout_artifacts_exist() -> None:
    for path in (EVIDENCE_PATH, SCHEMA_PATH, PLAN, DESIGN, THREAT, SCRIPT):
        assert path.is_file()
