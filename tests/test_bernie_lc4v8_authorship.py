from __future__ import annotations

import inspect
import json
from pathlib import Path

from app.services.bernie.lc4v8_content_blind_framework import (
    DIMENSION_NAMES,
    FROZEN_THRESHOLDS,
    VALID_ACTIONS,
    VALID_LANGUAGE_FORMS,
    validate_fixed_shape,
    validate_fixture_schema,
    validate_threshold_schema,
)
from app.services.bernie.lc4v8_evaluator import evaluate
from scripts.author_lc4v8_corpus import MODES, build_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests/fixtures/bernie_lc4v8_certification/fixture.json"
THRESHOLDS_PATH = ROOT / "tests/fixtures/bernie_lc4v8_certification/thresholds.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_authored_fixture_is_exactly_reproducible_and_structurally_valid() -> None:
    fixture = _load(FIXTURE_PATH)
    assert fixture == build_fixture()
    assert validate_fixture_schema(fixture) == []
    assert validate_fixed_shape(fixture) == []


def test_frozen_threshold_file_is_exact() -> None:
    thresholds = _load(THRESHOLDS_PATH)
    assert thresholds == FROZEN_THRESHOLDS
    assert validate_threshold_schema(thresholds) == []


def test_authored_population_cross_product_is_exact() -> None:
    fixture = _load(FIXTURE_PATH)
    groups = fixture["groups"]
    assert isinstance(groups, list)
    observed = []
    for action in VALID_ACTIONS:
        for mode in MODES:
            observed.append((action, mode))
    actual = []
    for group in groups:
        assert isinstance(group, dict)
        scenarios = group["scenarios"]
        assert isinstance(scenarios, list)
        first = scenarios[0]
        assert isinstance(first, dict)
        cell = str(first["coverage_cell"])
        mode = next(mode for mode in MODES if f"-{mode}-" in cell)
        actual.append((group["action"], mode))
        forms = [scenario["language_form"] for scenario in scenarios]
        assert forms == [form for form in VALID_LANGUAGE_FORMS for _ in range(2)]
    assert actual == observed


def test_every_gold_contract_has_all_thirteen_dimensions() -> None:
    fixture = _load(FIXTURE_PATH)
    for group in fixture["groups"]:  # type: ignore[index]
        for scenario in group["scenarios"]:
            assert set(scenario["expected"]) == set(DIMENSION_NAMES)


def test_authorship_did_not_execute_product_semantics() -> None:
    source = (ROOT / "scripts/author_lc4v8_corpus.py").read_text(encoding="utf-8")
    assert "extract_semantics" not in source
    assert "resolve_policy" not in source
    assert "lc4v7" not in source.lower()
    assert "lc4v6" not in source.lower()


def test_evaluator_is_oracle_free_and_product_path_explicit() -> None:
    source = inspect.getsource(evaluate)
    assert "expected" not in source
    assert "coverage_cell" not in source
    assert "extract_semantics" in source
    assert "resolve_policy" in source
    assert tuple(inspect.signature(evaluate).parameters) == ("value",)
