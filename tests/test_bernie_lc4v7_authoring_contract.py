from __future__ import annotations

import inspect

from app.services.bernie.lc4v7_content_blind_framework import (
    ACTIONS,
    LANGUAGE_STYLES,
    validate_corpus,
)
from scripts.author_bernie_lc4v7_corpus import build_corpus, build_metadata


CORPUS = build_corpus()
METADATA = build_metadata(CORPUS)


def test_authored_corpus_has_exact_schema_and_frozen_shape() -> None:
    assert validate_corpus(CORPUS) == ()
    assert len(CORPUS["scenarios"]) == 288
    assert METADATA["population"]["scenarios"] == 288
    assert METADATA["population"]["turns"] == {"multi": 72, "one": 216}
    assert set(METADATA["population"]["actions"]) == set(ACTIONS)
    assert set(METADATA["population"]["language_styles"]) == set(LANGUAGE_STYLES)


def test_each_family_style_and_action_balance_is_exact() -> None:
    assert len(METADATA["population"]["families"]) == 24
    assert set(METADATA["population"]["families"].values()) == {12}
    assert set(METADATA["population"]["actions"].values()) == {48}
    assert set(METADATA["population"]["language_styles"].values()) == {48}
    assert METADATA["population"]["unique_coverage_cells"] == 288


def test_layer_divergence_and_guardrail_overlays_are_non_vacuous() -> None:
    overlays = METADATA["semantic_overlays"]
    assert overlays == {
        "known": 72,
        "unknown_practitioner": 72,
        "ambiguous_practitioner": 72,
        "guardrail_polarity": 72,
        "unsafe_demand": 36,
        "explicit_safe_negation": 36,
        "extraction_policy_clarification_divergence": 72,
    }


def test_authorship_never_imports_or_executes_product_interpretation() -> None:
    source = inspect.getsource(
        __import__("scripts.author_bernie_lc4v7_corpus", fromlist=["build_corpus"])
    )
    assert "semantic_extraction" not in source
    assert "resolve_policy" not in source
    assert "extract_semantics" not in source
    assert METADATA["parser_or_policy_executed_during_authorship"] is False


def test_unknown_practitioner_layer_divergence_is_explicit() -> None:
    selected = [
        case
        for case in CORPUS["scenarios"]
        if case["family_id"].endswith("unknown_practitioner")
    ]
    assert len(selected) == 72
    for case in selected:
        assert case["extraction_gold"]["requires_clarification"] is False
        assert case["policy_gold"]["requires_clarification"] is True
        assert case["composition_gold"]["terminal_class"] == "clarification_required"


def test_source_spans_are_bounded_and_turn_aligned() -> None:
    for case in CORPUS["scenarios"]:
        spans_by_turn = case["extraction_gold"]["source_spans"]
        assert len(spans_by_turn) == len(case["utterances"])
        for utterance, spans in zip(case["utterances"], spans_by_turn, strict=True):
            for start, end in spans.values():
                assert 0 <= start <= end <= len(utterance)
