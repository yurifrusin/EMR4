from __future__ import annotations

import copy
import inspect
import json
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.bernie.lc4v7_content_blind_framework import (
    ACTIONS,
    CORPUS_SCHEMA,
    LANGUAGE_STYLES,
    MANIFEST_SCHEMA,
    PROVENANCE,
    REFERENCE_DATE,
    ROOT,
    SEAL_SCHEMA,
    canonical_sha256,
    consume_seal,
    expected_framework_hashes,
    file_sha256,
    population_summary,
    reject_protected_prior_paths,
    validate_consumed_binding,
    validate_corpus,
    validate_manifest,
    validate_population_summary,
)
from scripts.run_bernie_lc4v7_certification import (
    _observe,
    run,
    score_observation,
    validate_source_binding,
)


def _placeholder_scenario() -> dict:
    return {
        "scenario_id": "placeholder-scenario",
        "family_id": "placeholder-family",
        "action": "create",
        "language_style": "plain",
        "turn_count": 1,
        "coverage_cell": "placeholder-cell",
        "utterances": ["opaque"],
        "diary": {"state": "placeholder", "appointments": []},
        "extraction_gold": {
            "intended_action": None,
            "action_semantics": "placeholder",
            "temporal_relation": "placeholder",
            "earliest_time": None,
            "latest_time": None,
            "normalized_values": {},
            "entity_semantics": {},
            "source_spans": [{}],
            "requires_clarification": False,
            "clarification_choices": [],
            "authority": "read",
            "action_negated": False,
            "selected_tools": [],
        },
        "policy_gold": {
            "resolved_patient": None,
            "resolved_practitioner": None,
            "resolved_practitioner_id": None,
            "diary_relation": "no_conflict",
            "conflicting_fields": [],
            "requires_clarification": True,
            "clarification_choices": [],
            "authority": "clarify",
            "selected_tools": ["request_clarification"],
            "downstream_outcome": "clarification_required",
            "appointment_deltas": [],
            "audit_deltas": [],
            "simulated_write": False,
        },
        "composition_gold": {
            "terminal_class": "clarification_required",
            "semantic_lossless": True,
        },
    }


def _placeholder_corpus() -> dict:
    return {
        "schema_version": CORPUS_SCHEMA,
        "corpus_id": "placeholder-corpus",
        "reference_date": REFERENCE_DATE,
        "provenance": PROVENANCE,
        "scenarios": [_placeholder_scenario()],
    }


def _valid_population_summary() -> dict:
    return {
        "scenarios": 288,
        "families": {f"aggregate-family-{index:02d}": 12 for index in range(24)},
        "actions": {action: 48 for action in ACTIONS},
        "language_styles": {style: 48 for style in LANGUAGE_STYLES},
        "turns": {"multi": 72, "one": 216},
        "unique_coverage_cells": 288,
    }


def _seal(manifest_hash: str, corpus_hash: str, source_commit: str) -> dict:
    return {
        "schema_version": SEAL_SCHEMA,
        "attempt_id": "placeholder-attempt",
        "source_commit": source_commit,
        "manifest_hash": manifest_hash,
        "corpus_hash": corpus_hash,
        "state": "unconsumed",
        "consumed_at": None,
        "consumed_reason": None,
    }


def test_canonical_hash_is_order_independent_and_unicode_stable() -> None:
    assert canonical_sha256({"b": "é", "a": 1}) == canonical_sha256(
        {"a": 1, "b": "é"}
    )


def test_placeholder_scenario_has_exact_schema_but_not_real_population() -> None:
    errors = validate_corpus(_placeholder_corpus())
    assert errors
    assert all(
        marker in " ".join(errors)
        for marker in ("scenario population", "family population", "action population")
    )
    assert not any("field population" in error for error in errors)


@pytest.mark.parametrize(
    "mutation, marker",
    [
        (lambda value: value.update(schema_version="wrong"), "schema_version"),
        (lambda value: value.update(reference_date="2031-05-13"), "reference_date"),
        (lambda value: value["scenarios"][0].pop("policy_gold"), "field population"),
        (lambda value: value["scenarios"][0].update(turn_count=2), "turn_count"),
        (
            lambda value: value["scenarios"][0]["extraction_gold"].update(
                source_spans=[{"opaque": [0, 99]}]
            ),
            "source span",
        ),
    ],
)
def test_corpus_validation_fails_closed(mutation, marker: str) -> None:
    corpus = copy.deepcopy(_placeholder_corpus())
    mutation(corpus)
    assert any(marker in error for error in validate_corpus(corpus))


def test_frozen_population_summary_is_exact_without_constructing_a_corpus() -> None:
    summary = _valid_population_summary()
    assert validate_population_summary(summary) == ()
    summary["turns"] = {"multi": 71, "one": 217}
    assert "turn population" in " ".join(validate_population_summary(summary))


def test_population_summary_derives_only_aggregate_metadata() -> None:
    summary = population_summary([_placeholder_scenario()])
    assert summary == {
        "scenarios": 1,
        "families": {"placeholder-family": 1},
        "actions": {"create": 1},
        "language_styles": {"plain": 1},
        "turns": {"one": 1},
        "unique_coverage_cells": 1,
    }


def test_protected_prior_paths_are_refused_before_open() -> None:
    with pytest.raises(ValueError, match="protected prior-version"):
        reject_protected_prior_paths([Path("opaque-lc4v4-input.json")])


def test_seal_is_consumed_atomically_and_cannot_be_reused(tmp_path: Path) -> None:
    path = tmp_path / "seal.json"
    original = _seal("sha256:manifest", "sha256:corpus", "a" * 40)
    path.write_text(json.dumps(original), encoding="utf-8")
    consumed = consume_seal(path, original, consumed_at="2031-05-12T00:00:00Z")
    assert consumed["state"] == "consumed"
    assert json.loads(path.read_text(encoding="utf-8"))["state"] == "consumed"
    with pytest.raises(ValueError, match="already consumed"):
        consume_seal(path, consumed, consumed_at="later")


def test_manifest_and_consumed_seal_bind_exact_sources() -> None:
    source_commit = "a" * 40
    corpus_hash = "sha256:corpus"
    population = _valid_population_summary()
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "attempt_id": "placeholder-attempt",
        "source_commit": source_commit,
        "contract_hash": file_sha256(
            ROOT / "orchestration/agent_inbox/codex/lc4v7-sol-contract.md"
        ),
        "acceptance_rule_hash": file_sha256(
            ROOT
            / "orchestration/agent_inbox/codex/lc4v7-one-shot-acceptance-rule.md"
        ),
        "framework_hashes": expected_framework_hashes(),
        "corpus_hash": corpus_hash,
        "corpus_population": population,
        "created_by": "gpt_sol",
    }
    assert validate_manifest(
        manifest,
        corpus_hash=corpus_hash,
        source_commit=source_commit,
        population=population,
    ) == ()
    manifest_hash = canonical_sha256(manifest)
    seal = _seal(manifest_hash, corpus_hash, source_commit)
    seal.update(
        state="consumed",
        consumed_at="2031-05-12T00:00:00Z",
        consumed_reason="evaluation_started",
    )
    assert validate_consumed_binding(
        seal,
        manifest=manifest,
        manifest_hash=manifest_hash,
        corpus_hash=corpus_hash,
        source_commit=source_commit,
    ) == ()
    assert "source commit drift" in " ".join(
        validate_manifest(
            manifest,
            corpus_hash=corpus_hash,
            source_commit="b" * 40,
            population=population,
        )
    )
    changed = copy.deepcopy(manifest)
    changed["framework_hashes"][
        "scripts/run_bernie_lc4v7_certification.py"
    ] = "sha256:drift"
    assert "framework hash drift" in " ".join(
        validate_manifest(
            changed,
            corpus_hash=corpus_hash,
            source_commit=source_commit,
            population=population,
        )
    )


def test_layer_specific_scoring_allows_false_then_true_clarification() -> None:
    scenario = _placeholder_scenario()
    extraction = SimpleNamespace(
        intended_action=None,
        action_semantics="placeholder",
        temporal_relation="placeholder",
        earliest_time=None,
        latest_time=None,
        normalized_values={},
        entity_semantics={},
        normalized_turns=[
            SimpleNamespace(original="opaque", source_spans={})
        ],
        requires_clarification=False,
        clarification_choices=(),
        authority_claim="read",
        action_negated=False,
        selected_tool_sequence=(),
        claims_action_completed=False,
    )
    policy = SimpleNamespace(
        resolved_patient=None,
        resolved_practitioner=None,
        resolved_practitioner_id=None,
        diary_comparison=SimpleNamespace(
            relation="no_conflict", conflicting_fields=()
        ),
        requires_clarification=True,
        clarification_choices=(),
        authority="clarify",
        selected_tools=("request_clarification",),
        downstream_outcome="clarification_required",
        appointment_deltas=(),
        audit_deltas=(),
        is_simulated_confirmed_write=False,
        utterance_entity_semantics_unchanged=True,
    )
    scores = score_observation(scenario, extraction, policy)
    assert scores["extraction_clarification"] is True
    assert scores["policy_clarification"] is True
    assert scores["clarification_composition"] is True
    assert all(scores.values())


def test_runtime_boundary_cannot_receive_gold_or_identity() -> None:
    assert tuple(inspect.signature(_observe).parameters) == (
        "utterances",
        "diary",
        "reference_date",
    )
    source = inspect.getsource(_observe)
    assert "gold" not in source.casefold()
    assert "scenario_id" not in source


def test_source_binding_uses_an_ancestor_with_the_exact_committed_blob() -> None:
    import subprocess

    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    path = Path(
        "orchestration/agent_inbox/codex/lc4v7-post-compaction-receipt.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert validate_source_binding(
        source_commit, path, canonical_sha256(payload)
    ) == ()
    assert "blob hash drift" in " ".join(
        validate_source_binding(source_commit, path, "sha256:" + "0" * 64)
    )


def test_source_binding_refuses_uncommitted_external_paths(tmp_path: Path) -> None:
    assert validate_source_binding("a" * 40, tmp_path / "corpus.json", "hash") == (
        "corpus path is outside the repository",
    )


def test_invalid_attempt_consumes_seal_and_writes_aggregate_only(tmp_path: Path) -> None:
    corpus = _placeholder_corpus()
    manifest = {"schema_version": MANIFEST_SCHEMA}
    corpus_path = tmp_path / "fresh-corpus.json"
    manifest_path = tmp_path / "fresh-manifest.json"
    seal_path = tmp_path / "fresh-seal.json"
    report_path = tmp_path / "fresh-report.json"
    corpus_path.write_text(json.dumps(corpus), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    seal_path.write_text(
        json.dumps(
            _seal(canonical_sha256(manifest), canonical_sha256(corpus), "a" * 40)
        ),
        encoding="utf-8",
    )
    report = run(
        Namespace(
            corpus=corpus_path,
            manifest=manifest_path,
            seal=seal_path,
            report=report_path,
            source_commit="a" * 40,
        )
    )
    assert report["decision"] == "certification_invalid"
    assert json.loads(seal_path.read_text(encoding="utf-8"))["state"] == "consumed"
    rendered = report_path.read_text(encoding="utf-8")
    for forbidden in ("opaque", "scenario_id", "utterances", "extraction_gold"):
        assert forbidden not in rendered


def test_report_overwrite_is_refused_without_consuming_seal(tmp_path: Path) -> None:
    seal_path = tmp_path / "fresh-seal.json"
    original = _seal("sha256:manifest", "sha256:corpus", "a" * 40)
    seal_path.write_text(json.dumps(original), encoding="utf-8")
    report_path = tmp_path / "fresh-report.json"
    report_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="overwrite refused"):
        run(
            Namespace(
                corpus=tmp_path / "fresh-corpus.json",
                manifest=tmp_path / "fresh-manifest.json",
                seal=seal_path,
                report=report_path,
                source_commit="a" * 40,
            )
        )
    assert json.loads(seal_path.read_text(encoding="utf-8"))["state"] == "unconsumed"


def test_framework_sources_contain_no_real_v7_content() -> None:
    paths = [
        Path("app/services/bernie/lc4v7_content_blind_framework.py"),
        Path("app/services/bernie/lc4v7_acceptance_rule.py"),
        Path("scripts/run_bernie_lc4v7_certification.py"),
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "Margaret Thompson" not in joined
    assert "tests/fixtures" not in joined
