"""Acceptance tests for the Sol-authored LC4 protected holdout."""

from __future__ import annotations

import copy
import ast
import json
import shutil
from collections import Counter
from pathlib import Path

import pytest

from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from app.services.bernie.scaled_evaluator import (
    SealedHoldoutReceipt,
    SingleUseLedger,
    compute_sanitized_holdout_hash,
    sanitize_holdout_report,
)
from tests.lc4_holdout_support import (
    HOLDOUT_EVALUATION_ID,
    HOLDOUT_EVALUATOR_IDENTITY,
    HOLDOUT_GROUP_COUNT,
    HOLDOUT_MULTI_TURN_PER_GROUP,
    HOLDOUT_MT_PREFIX,
    HOLDOUT_PURPOSE,
    HOLDOUT_REPEATS,
    HOLDOUT_SURFACE_PER_GROUP,
    HOLDOUT_TOTAL_SAMPLES,
    HOLDOUT_TOTAL_TRAJECTORIES,
    HOLDOUT_TOTAL_VARIANTS,
    HOLDOUT_VARIANT_PREFIX,
    author_holdout_fixture,
    authored_blueprints,
    evaluate_once,
    load_sealed_holdout,
    verify_sealed_artifacts,
)


ROOT = Path(__file__).resolve().parent.parent
ACTUAL_FIXTURE_DIR = ROOT / "tests" / "fixtures" / "bernie_lc4_holdout"
ACTUAL_SEAL = ROOT / "docs" / "bernie-lc4-holdout-seal-receipt.json"
ACTUAL_REPORT = ROOT / "docs" / "bernie-lc4-holdout-aggregate-report.json"


@pytest.fixture(scope="module")
def authored_temp(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    root = tmp_path_factory.mktemp("lc4_holdout")
    fixture_dir = root / "fixture"
    seal = root / "seal.json"
    author_holdout_fixture(fixture_dir, seal)
    return fixture_dir, seal


def _capability_from_seal(seal: Path) -> tuple[SealedHoldoutReceipt, SingleUseLedger]:
    raw = json.loads(seal.read_text(encoding="utf-8"))
    capability = SealedHoldoutReceipt(
        manifest_hash=raw["manifest_hash"],
        evaluator_identity=raw["evaluator_identity"],
        evaluation_id=raw["evaluation_id"],
        is_sealed=raw["is_sealed"],
    )
    return capability, SingleUseLedger(capability)


def test_blueprints_are_balanced_and_gap_prioritised() -> None:
    blueprints = authored_blueprints()
    assert len(blueprints) == HOLDOUT_GROUP_COUNT
    assert Counter(item.action for item in blueprints) == {
        "create": 4,
        "move": 4,
        "resize": 4,
        "cancel": 4,
        "status_change": 4,
        "explain_schedule": 4,
    }
    assert set(item.temporal_relation for item in blueprints) == {
        "exact", "not_before", "not_after", "interval", "approximate", "unspecified"
    }
    assert len(set(item.diary_state for item in blueprints)) == 11
    assert len(set(item.entity_state for item in blueprints)) == 6
    assert len(set(item.dialogue_form for item in blueprints)) == 8
    assert len(set(item.language_form for item in blueprints)) == 8
    assert all(item.gap_targets for item in blueprints)


def test_authored_manifest_is_gold_sealed_and_provider_free(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, seal = authored_temp
    manifest = json.loads((fixture_dir / "lc4_holdout_manifest.json").read_text(encoding="utf-8"))
    receipt = json.loads(seal.read_text(encoding="utf-8"))
    assert manifest["total_groups"] == HOLDOUT_GROUP_COUNT
    assert manifest["total_variants"] == HOLDOUT_TOTAL_VARIANTS
    assert manifest["total_trajectories"] == HOLDOUT_TOTAL_TRAJECTORIES
    assert manifest["provenance"] == "gold"
    assert manifest["adjudication"] == "adjudicated"
    assert manifest["generator_identity"] is None
    assert set(manifest["authority_grant"].values()) == {False}
    assert receipt["manifest_hash"] == manifest["manifest_hash"]
    assert receipt["purpose"] == HOLDOUT_PURPOSE
    assert receipt["consumed"] is False


def test_exact_group_variant_and_trajectory_counts(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, seal = authored_temp
    capability, ledger = _capability_from_seal(seal)
    corpus = load_sealed_holdout(fixture_dir, capability=capability, ledger=ledger)
    assert len(corpus.groups) == HOLDOUT_GROUP_COUNT
    assert len(corpus.all_variants()) == HOLDOUT_TOTAL_VARIANTS
    assert sum(len(group.surface_variants) for group in corpus.groups) == (
        HOLDOUT_GROUP_COUNT * HOLDOUT_SURFACE_PER_GROUP
    )
    assert sum(len(group.multi_turn_variants) for group in corpus.groups) == (
        HOLDOUT_GROUP_COUNT * HOLDOUT_MULTI_TURN_PER_GROUP
    )
    assert all(
        len(scenario.dialogue_turns) > 1
        for group in corpus.groups for scenario in group.multi_turn_variants
    )


def test_all_variants_are_gold_adjudicated_and_lossless(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, seal = authored_temp
    capability, ledger = _capability_from_seal(seal)
    corpus = load_sealed_holdout(fixture_dir, capability=capability, ledger=ledger)
    for scenario in corpus.all_variants():
        assert scenario.provenance == "gold"
        assert scenario.adjudication == "adjudicated"
        assert "appointment_date" in scenario.normalized_values
        assert "duration_minutes" in scenario.normalized_values
        for spans in scenario.source_spans.values():
            for span in spans:
                utterance = scenario.dialogue_turns[span.turn_index]["utterance"]
                assert utterance[span.start:span.end] == span.text


def test_capability_is_single_use(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, seal = authored_temp
    capability, ledger = _capability_from_seal(seal)
    load_sealed_holdout(fixture_dir, capability=capability, ledger=ledger)
    with pytest.raises(ValueError, match="already consumed"):
        load_sealed_holdout(fixture_dir, capability=capability, ledger=ledger)


def test_wrong_evaluator_identity_fails_before_labels_load(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, seal = authored_temp
    raw = json.loads(seal.read_text(encoding="utf-8"))
    capability = SealedHoldoutReceipt(
        manifest_hash=raw["manifest_hash"],
        evaluator_identity="wrong-evaluator",
        evaluation_id=HOLDOUT_EVALUATION_ID,
        is_sealed=True,
    )
    ledger = SingleUseLedger(capability)
    with pytest.raises(ValueError, match="capability rejected"):
        load_sealed_holdout(fixture_dir, capability=capability, ledger=ledger)
    assert ledger.is_consumed is False


def test_tampered_variant_fails_closed(
    authored_temp: tuple[Path, Path], tmp_path: Path
) -> None:
    fixture_dir, seal = authored_temp
    copied = tmp_path / "fixture"
    shutil.copytree(fixture_dir, copied)
    manifest = json.loads((copied / "lc4_holdout_manifest.json").read_text(encoding="utf-8"))
    first_path = copied / manifest["groups"][0]["filename"]
    group = json.loads(first_path.read_text(encoding="utf-8"))
    group["surface_variants"][0]["description"] = "tampered"
    first_path.write_text(json.dumps(group, indent=2) + "\n", encoding="utf-8")
    capability, ledger = _capability_from_seal(seal)
    with pytest.raises(ValueError, match="variant hash mismatch"):
        load_sealed_holdout(copied, capability=capability, ledger=ledger)


def test_development_loader_rejects_holdout_path(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, _ = authored_temp
    with pytest.raises(ValueError, match="cannot access holdout"):
        DevelopmentOnlyLoader(fixture_dir)


def test_one_shot_evaluation_is_aggregate_only_and_non_reusable(
    authored_temp: tuple[Path, Path], tmp_path: Path
) -> None:
    fixture_dir, source_seal = authored_temp
    seal = tmp_path / "seal.json"
    report_path = tmp_path / "report.json"
    shutil.copy2(source_seal, seal)
    report = evaluate_once(fixture_dir, seal, report_path)
    assert report["total_samples"] == HOLDOUT_TOTAL_SAMPLES
    assert report["repeat_count"] == HOLDOUT_REPEATS
    assert report["aggregate"]["total"] == HOLDOUT_TOTAL_SAMPLES
    assert report["report_hash"] == compute_sanitized_holdout_hash(report)
    sanitize_holdout_report(report)
    encoded = json.dumps(report).lower()
    for forbidden in (
        "scenario_id", "utterance", "expected_outcome", "source_span",
        "case_findings", HOLDOUT_VARIANT_PREFIX.lower(), HOLDOUT_MT_PREFIX.lower(),
    ):
        assert forbidden not in encoded
    with pytest.raises(ValueError, match="already been consumed"):
        evaluate_once(fixture_dir, seal, report_path)
    verify_sealed_artifacts(fixture_dir, seal, report_path)


def test_holdout_report_hash_detects_aggregate_mutation(
    authored_temp: tuple[Path, Path], tmp_path: Path
) -> None:
    fixture_dir, source_seal = authored_temp
    seal = tmp_path / "seal.json"
    report_path = tmp_path / "report.json"
    shutil.copy2(source_seal, seal)
    report = evaluate_once(fixture_dir, seal, report_path)
    mutated = copy.deepcopy(report)
    mutated["aggregate"]["passed"] += 1
    assert compute_sanitized_holdout_hash(mutated) != report["report_hash"]


def test_combined_scale_contract(authored_temp: tuple[Path, Path]) -> None:
    fixture_dir, _ = authored_temp
    dev_manifest = json.loads(
        (ROOT / "tests" / "fixtures" / "bernie_lc4_development" /
         "lc4_development_manifest.json").read_text(encoding="utf-8")
    )
    holdout_manifest = json.loads(
        (fixture_dir / "lc4_holdout_manifest.json").read_text(encoding="utf-8")
    )
    assert dev_manifest["total_groups"] + holdout_manifest["total_groups"] == 120
    assert (
        dev_manifest["total_individual_records"] + holdout_manifest["total_variants"]
        == 1440
    )
    assert (
        dev_manifest["total_multi_turn_trajectories"]
        + holdout_manifest["total_trajectories"]
        == 360
    )


def test_product_modules_do_not_import_holdout_support() -> None:
    violations: list[str] = []
    for path in (ROOT / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            module_names: list[str] = []
            if isinstance(node, ast.Import):
                module_names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_names.append(node.module)
            if any("lc4_holdout" in name.lower() for name in module_names):
                violations.append(str(path.relative_to(ROOT)))
    assert violations == []


def test_actual_holdout_artifacts_verify_without_re_evaluation() -> None:
    if not (ACTUAL_FIXTURE_DIR.exists() and ACTUAL_SEAL.exists() and ACTUAL_REPORT.exists()):
        pytest.skip("Actual Sol holdout is not sealed yet")
    verify_sealed_artifacts(ACTUAL_FIXTURE_DIR, ACTUAL_SEAL, ACTUAL_REPORT)
