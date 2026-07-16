from __future__ import annotations

import copy
import inspect
import json

import pytest

from app.services.bernie.lc4v4d3_policy_resolution import (
    extract_final_practitioner,
    map_practitioner_id,
)
from app.services.bernie.lc4v6d1_development_evidence import (
    EXPECTED_FAMILY_COUNTS,
    TOTAL_EXPECTED,
    compute_fixture_hash,
    load_fixture,
    run_lc4v6d1_evidence,
    validate_fixture,
)


FIXTURE = load_fixture()
EVIDENCE = run_lc4v6d1_evidence()


def test_fixture_is_exact_and_frozen() -> None:
    assert validate_fixture(FIXTURE) == ()
    assert len(FIXTURE["cases"]) == TOTAL_EXPECTED
    assert EVIDENCE["fixture_hash"] == compute_fixture_hash(FIXTURE)
    assert EVIDENCE["fixture_hash"] == (
        "sha256:cee606a54a6b508e4d7b8f1a9ce1e6e4a0a905373deadce71c995901b1645ebc"
    )


@pytest.mark.parametrize(
    "mutation, expected_error",
    [
        (lambda value: value.update(schema_version="wrong"), "schema_version"),
        (lambda value: value.update(reference_date="2026-07-17"), "reference_date"),
        (lambda value: value.update(provenance="unknown"), "provenance"),
        (lambda value: value["cases"].pop(), "case population"),
        (lambda value: value["cases"][1].update(probe_id=value["cases"][0]["probe_id"]), "unique"),
        (lambda value: value["cases"][0].pop("policy"), "field population"),
        (lambda value: value["cases"][0]["extraction"].pop("tools"), "extraction field"),
        (lambda value: value["cases"][0]["policy"].pop("tools"), "policy field"),
    ],
)
def test_fixture_validation_fails_closed(mutation, expected_error: str) -> None:
    changed = copy.deepcopy(FIXTURE)
    mutation(changed)
    assert any(expected_error in error for error in validate_fixture(changed))


def test_family_population_is_exact() -> None:
    actual: dict[str, int] = {}
    for case in FIXTURE["cases"]:
        actual[case["family"]] = actual.get(case["family"], 0) + 1
    assert actual == EXPECTED_FAMILY_COUNTS


def test_layer_specific_baseline_is_complete_safe_and_deterministic() -> None:
    assert EVIDENCE["fixture_valid"] is True
    assert EVIDENCE["aggregate"] == {
        "total": 24,
        "extraction_pass": 24,
        "policy_pass": 24,
        "composed_pass": 24,
        "safe": 24,
        "variance": 0,
    }
    assert EVIDENCE["classifications"] == {
        "pass": 24,
        "authoring_invalid": 0,
        "parser_gap": 0,
        "policy_gap": 0,
        "contract_layer_gap": 0,
    }


@pytest.mark.parametrize("result", EVIDENCE["cases"], ids=lambda item: item["probe_id"])
def test_each_probe_matches_both_layers(result: dict) -> None:
    assert result["classification"] == "pass"
    assert result["extraction_mismatches"] == ()
    assert result["policy_mismatches"] == ()
    assert result["safe"] is True
    assert result["variance"] is False


def test_unknown_practitioner_divergence_is_expected_and_safe() -> None:
    selected = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "move_unknown_practitioner"
    ]
    assert len(selected) == 12
    assert EVIDENCE["conflated_clarification_failure_count"] == 12
    for item in selected:
        first = item["observations"][0]
        assert item["expected_layer_divergence"] is True
        assert item["observed_layer_divergence"] is True
        assert first["extraction"]["practitioner_semantics"] == "exact"
        assert first["extraction"]["requires_clarification"] is False
        assert first["policy"] == {
            "requires_clarification": True,
            "clarification_choices": (),
            "authority": "clarify",
            "tools": ("request_clarification",),
            "downstream_outcome": "clarification_required",
            "resolved_practitioner_id": None,
            "appointment_delta_count": 0,
            "audit_delta_count": 0,
            "simulated_write": False,
        }


def test_unknown_names_are_genuinely_unmapped_and_known_controls_are_mapped() -> None:
    for case in FIXTURE["cases"]:
        name = extract_final_practitioner(case["utterances"])
        assert name is not None
        practitioner_id = map_practitioner_id(name)
        if case["family"] == "move_unknown_practitioner":
            assert practitioner_id is None
        else:
            assert practitioner_id == case["policy"]["resolved_practitioner_id"]


def test_normalized_temporal_bounds_and_durations_are_lossless() -> None:
    by_id = {item["probe_id"]: item for item in EVIDENCE["cases"]}
    for case in FIXTURE["cases"]:
        actual = by_id[case["probe_id"]]["observations"][0]["extraction"]
        expected = case["extraction"]
        assert actual["normalized_earliest_time"] == expected["earliest_time"]
        assert actual["normalized_latest_time"] == expected["latest_time"]
        assert actual["duration_minutes"] == expected.get("duration_minutes")


def test_runner_never_branches_on_probe_identity_or_passes_expectations_downstream() -> None:
    source = inspect.getsource(__import__(
        "app.services.bernie.lc4v6d1_development_evidence",
        fromlist=["run_lc4v6d1_evidence"],
    ))
    assert "if probe_id" not in source
    observe_source = inspect.getsource(__import__(
        "app.services.bernie.lc4v6d1_development_evidence",
        fromlist=["_observe"],
    )._observe)
    assert "expected" not in observe_source
    assert "probe_id" not in observe_source


def test_committed_report_matches_live_aggregate() -> None:
    report = json.loads((
        __import__(
            "app.services.bernie.lc4v6d1_development_evidence",
            fromlist=["ROOT"],
        ).ROOT
        / "docs"
        / "bernie-lc4v6d1-development-report.json"
    ).read_text(encoding="utf-8"))
    assert report["fixture_hash"] == EVIDENCE["fixture_hash"]
    assert report["fixture_valid"] == EVIDENCE["fixture_valid"]
    assert report["aggregate"] == EVIDENCE["aggregate"]
    assert report["classifications"] == EVIDENCE["classifications"]
    assert report["layer_diagnosis"]["conflated_clarification_failure_count"] == (
        EVIDENCE["conflated_clarification_failure_count"]
    )
    assert report["selection"]["remediation_authorized"] is False
