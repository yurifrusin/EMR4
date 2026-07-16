"""Pre-seal structural checks for Sol-authored LC4V6 content.

These tests never execute the parser, policy resolver, or replay evaluator.
"""

from __future__ import annotations

import ast
from pathlib import Path

from app.services.bernie.lc4v6_content_blind_framework import validate_manifest
from app.services.bernie.lc4v6_corpus import (
    FAMILIES,
    LANGUAGE_FORMS,
    author_scenarios,
    corpus_hash,
    manifest_metadata,
)


def test_exact_fresh_population_and_manifest_shape() -> None:
    scenarios = author_scenarios()
    assert len(FAMILIES) == 24
    assert len(LANGUAGE_FORMS) == 12
    assert len(scenarios) == 288
    result = validate_manifest(manifest_metadata(), scenarios)
    assert result.valid, result.errors


def test_every_family_has_twelve_unique_variants_and_three_trajectories() -> None:
    scenarios = author_scenarios()
    for family in FAMILIES:
        selected = [item for item in scenarios if item.group == family.name]
        assert len(selected) == 12
        assert sum(item.is_multi_turn for item in selected) == 3
        assert len({item.utterances for item in selected}) == 12


def test_cells_ids_and_full_dialogues_are_unique() -> None:
    scenarios = author_scenarios()
    assert len({item.scenario_id for item in scenarios}) == 288
    assert len({item.coverage_cell for item in scenarios}) == 288
    assert len({item.utterances for item in scenarios}) == 288


def test_expected_contract_has_every_evaluator_field() -> None:
    required = {
        "intended_action",
        "action_semantics",
        "temporal_relation",
        "normalized_values",
        "entity_semantics",
        "requires_clarification",
        "interpretation_choices",
        "policy_choices",
        "interpretation_tools",
        "policy_tools",
        "interpretation_authority",
        "policy_authority",
        "downstream_outcome",
        "appointment_delta_count",
        "audit_delta_count",
        "simulated_write",
    }
    assert all(set(item.expected) == required for item in author_scenarios())


def test_corpus_hash_is_deterministic_and_bound_in_metadata() -> None:
    first = corpus_hash()
    second = corpus_hash()
    assert first == second
    assert first.startswith("sha256:") and len(first) == 71
    assert manifest_metadata()["corpus_hash"] == first


def test_content_is_fresh_relative_to_named_r1_development_personas() -> None:
    rendered = "\n".join(
        utterance
        for scenario in author_scenarios()
        for utterance in scenario.utterances
    )
    assert "Margaret Thompson" not in rendered
    assert "Dr Shera" not in rendered
    assert "Alice Nguyen" in rendered
    assert "Dr Patel" in rendered


def test_authorship_test_never_imports_or_executes_evaluator() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )
    assert not any("semantic_extraction" in name for name in imports)
    assert not any("lc4v6_evaluator" in name for name in imports)


def test_evaluator_does_not_pass_expected_values_to_product_interpretation() -> None:
    evaluator = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "bernie"
        / "lc4v6_evaluator.py"
    ).read_text(encoding="utf-8")
    extraction_call = evaluator.split("extract_semantics(", 1)[1].split(")", 1)[0]
    assert "expected" not in extraction_call
    assert "scenario.expected" not in extraction_call
