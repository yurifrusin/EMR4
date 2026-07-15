"""Content-blind LC4V3 framework tests using temporary synthetic data only."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from app.services.bernie.lc4v3_certification import (
    LC4V3_CORPUS_IDENTITY,
    LC4V3_EVALUATION_ID,
    LC4V3_EVALUATOR_VERSION,
    LC4V3_GROUP_COUNT,
    LC4V3_GROUP_PREFIX,
    LC4V3_MANIFEST_SCHEMA,
    LC4V3_MT_PER_GROUP,
    LC4V3_REPEAT_COUNT,
    LC4V3_REPORT_SCHEMA,
    LC4V3_SEAL_SCHEMA,
    LC4V3_SURFACE_PER_GROUP,
    LC4V3_TOTAL_SAMPLES,
    LC4V3_TOTAL_SCENARIOS,
    LC4V3_TOTAL_TRAJECTORIES,
    LC4V3_VARIANTS_PER_GROUP,
    PER_DIMENSION_NAMES,
    _canonical_json,
    _stable_hash,
    build_manifest,
    check_aggregate_report,
    check_forbidden_aggregate_keys,
    create_seal,
    evaluate_aggregate,
    get_source_commit,
    load_verified_scenarios,
    reconstruct_manifest,
    validate_lc4v3_isolation,
    validate_report_hash,
    verify_manifest_against_corpus,
    verify_seal,
)

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/bernie_lc4v3_certification.py"
MANIFEST_HASH = "sha256:" + "1" * 64
CORPUS_HASH = "sha256:" + "2" * 64
SOURCE_COMMIT = "3" * 40


def _scenario(
    scenario_id: str,
    *,
    multi_turn: bool = False,
    provenance: str = "gold",
    adjudication: str = "adjudicated",
) -> dict[str, Any]:
    utterance = "Book Margaret Thompson with Dr Shera tomorrow at 3pm for 15 minutes."
    turns = [{"turn": 1, "utterance": utterance}]
    if multi_turn:
        turns.append({"turn": 2, "utterance": "Yes, keep those exact details."})
    return {
        "spec_version": "lc1.v1",
        "scenario_id": scenario_id,
        "provenance": provenance,
        "adjudication": adjudication,
        "family": "lc4v3_content_blind_test",
        "description": "Temporary synthetic framework scenario",
        "dialogue_turns": turns,
        "reference_date": "2026-07-15",
        "clinic_clock": "2026-07-15T09:00:00+10:00",
        "intended_action": "create",
        "action_semantics": "intended",
        "temporal_relation": "exact",
        "earliest_time": "15:00",
        "latest_time": "15:00",
        "normalized_values": {
            "appointment_date": "2026-07-16",
            "duration_minutes": 15,
            "earliest_time": "15:00",
            "latest_time": "15:00",
        },
        "source_spans": {
            "appointment_date": [{"turn_index": 0, "start": 37, "end": 45, "text": "tomorrow"}],
            "earliest_time": [{"turn_index": 0, "start": 49, "end": 52, "text": "3pm"}],
            "latest_time": [{"turn_index": 0, "start": 49, "end": 52, "text": "3pm"}],
            "patient": [{"turn_index": 0, "start": 5, "end": 22, "text": "Margaret Thompson"}],
            "practitioner": [{"turn_index": 0, "start": 28, "end": 36, "text": "Dr Shera"}],
            "duration_minutes": [{"turn_index": 0, "start": 57, "end": 67, "text": "15 minutes"}],
            "temporal_relation": [{"turn_index": 0, "start": 49, "end": 52, "text": "3pm"}],
        },
        "duration_minutes": 15,
        "practitioner_semantics": "exact",
        "patient_semantics": "exact",
        "location_semantics": "omitted",
        "appointment_type_semantics": "omitted",
        "duration_semantics": "exact",
        "diary_state": "empty",
        "entity_state": "exact",
        "dialogue_form": "clarification" if multi_turn else "one_shot",
        "language_form": "plain",
        "initial_diary_state": {
            "synthetic": True,
            "reference_date": "2026-07-15",
            "diary_page_date": "2026-07-16",
            "seeded_appointments": [],
            "practitioners_available": ["pr-001"],
            "patients_booked_today": [],
        },
        "expected_outcome_kind": "appointment_created",
        "expected_tool_sequence": ["search_patients", "find_slots", "create_booking"],
        "expected_appointment_deltas": [{
            "appointment_id": "apt-001", "change_type": "created",
            "patient_id": "p-001", "practitioner_id": "pr-001",
            "date": "2026-07-16", "start_time": "15:00", "duration_minutes": 15,
        }],
        "expected_audit_deltas": [{"change_type": "created", "appointment_id": "apt-001", "count": 1}],
        "forbidden_outcomes": [],
        "forbidden_tool_calls": ["mutate_diary_direct", "override_confirmation"],
        "expected_clarification": None,
        "clarification_choices": [],
    }


def _group(index: int) -> dict[str, Any]:
    return {
        "group_id": f"{LC4V3_GROUP_PREFIX}{index:03d}",
        "surface_variants": [
            _scenario(f"lc4v3_var_{index:03d}_{position:02d}")
            for position in range(1, LC4V3_SURFACE_PER_GROUP + 1)
        ],
        "multi_turn_variants": [
            _scenario(f"lc4v3_mt_{index:03d}_{position:02d}", multi_turn=True)
            for position in range(1, LC4V3_MT_PER_GROUP + 1)
        ],
    }


def _write_corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "synthetic_corpus"
    corpus.mkdir()
    for index in range(1, LC4V3_GROUP_COUNT + 1):
        path = corpus / f"{LC4V3_GROUP_PREFIX}{index:03d}.json"
        path.write_text(json.dumps(_group(index), indent=2) + "\n", encoding="utf-8")
    return corpus


def _rewrite_group(corpus: Path, index: int, group: dict[str, Any]) -> None:
    path = corpus / f"{LC4V3_GROUP_PREFIX}{index:03d}.json"
    path.write_text(json.dumps(group, indent=2) + "\n", encoding="utf-8")


def _scenarios(corpus: Path) -> list[Any]:
    return load_verified_scenarios(corpus)


def _evaluate(corpus: Path) -> dict[str, Any]:
    return evaluate_aggregate(
        _scenarios(corpus),
        manifest_hash=MANIFEST_HASH,
        corpus_hash=CORPUS_HASH,
        source_commit=SOURCE_COMMIT,
    )


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=ROOT,
        capture_output=True, text=True, check=False,
    )


def test_frozen_shape_constants() -> None:
    assert (
        LC4V3_CORPUS_IDENTITY,
        LC4V3_GROUP_COUNT,
        LC4V3_VARIANTS_PER_GROUP,
        LC4V3_TOTAL_SCENARIOS,
        LC4V3_TOTAL_TRAJECTORIES,
        LC4V3_REPEAT_COUNT,
        LC4V3_TOTAL_SAMPLES,
    ) == ("lc4-holdout-v3", 24, 12, 288, 72, 2, 576)
    assert LC4V3_EVALUATION_ID == "lc4-holdout-v3-baseline-001"
    assert LC4V3_EVALUATOR_VERSION == "lc4v3.aggregate_evaluator.v1"


def test_build_and_reconstruct_manifest(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    manifest = build_manifest(corpus)
    assert manifest["schema_version"] == LC4V3_MANIFEST_SCHEMA
    assert manifest["group_count"] == 24
    assert manifest["total_scenarios"] == 288
    assert manifest["total_trajectories"] == 72
    assert len(manifest["files"]) == 24
    assert reconstruct_manifest(manifest) == manifest
    assert verify_manifest_against_corpus(corpus, manifest) == manifest


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda group: group.update({"unexpected": True}), "schema drift"),
        (lambda group: group.update({"group_id": "wrong"}), "identity drift"),
        (lambda group: group["surface_variants"].pop(), "surface variant count"),
        (lambda group: group["multi_turn_variants"].pop(), "multi-turn variant count"),
        (lambda group: group["surface_variants"][0].pop("expected_outcome_kind"), "explicit expected outcome"),
        (lambda group: group["surface_variants"][0].update({"source_spans": {}}), "source spans"),
        (lambda group: group["surface_variants"][0]["initial_diary_state"].update({"synthetic": False}), "explicitly synthetic"),
        (lambda group: group["surface_variants"][0].update({"provenance": "silver"}), "Gold/adjudicated"),
        (lambda group: group["surface_variants"][0].update({"adjudication": "pending"}), "Gold/adjudicated"),
        (lambda group: group["surface_variants"][0].update({"scenario_id": "not_namespaced"}), "identity drift"),
        (lambda group: group["multi_turn_variants"][0].update({"dialogue_turns": group["multi_turn_variants"][0]["dialogue_turns"][:1]}), "multiple turns"),
    ],
)
def test_manifest_rejects_invalid_scenario_contract(
    tmp_path: Path, mutation: Any, message: str,
) -> None:
    corpus = _write_corpus(tmp_path)
    group = _group(1)
    mutation(group)
    _rewrite_group(corpus, 1, group)
    with pytest.raises(ValueError, match=message):
        build_manifest(corpus)


def test_manifest_rejects_duplicate_identity(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    group = _group(2)
    group["surface_variants"][0]["scenario_id"] = "lc4v3_var_001_01"
    _rewrite_group(corpus, 2, group)
    with pytest.raises(ValueError, match="identity drift|duplicate"):
        build_manifest(corpus)


def test_manifest_rejects_lossy_span(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    group = _group(1)
    group["surface_variants"][0]["source_spans"]["patient"][0]["text"] = "wrong"
    _rewrite_group(corpus, 1, group)
    with pytest.raises(ValueError, match="does not match original text"):
        build_manifest(corpus)


def test_manifest_rejects_file_population_drift(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    (corpus / f"{LC4V3_GROUP_PREFIX}024.json").unlink()
    with pytest.raises(ValueError, match="Expected 24 group files"):
        build_manifest(corpus)


@pytest.mark.parametrize("field", ["schema_version", "corpus_identity", "group_count"])
def test_reconstruct_manifest_rejects_authority_drift(tmp_path: Path, field: str) -> None:
    manifest = build_manifest(_write_corpus(tmp_path))
    manifest[field] = "wrong"
    with pytest.raises(ValueError):
        reconstruct_manifest(manifest)


def test_reconstruct_manifest_rejects_extra_key_and_malformed_hash(tmp_path: Path) -> None:
    manifest = build_manifest(_write_corpus(tmp_path))
    extra = deepcopy(manifest)
    extra["unexpected"] = True
    with pytest.raises(ValueError, match="schema drift"):
        reconstruct_manifest(extra)
    malformed = deepcopy(manifest)
    malformed["files"][0]["file_hash"] = "sha256:short"
    malformed["corpus_hash"] = _stable_hash(_canonical_json(malformed["files"]))
    with pytest.raises(ValueError, match="canonical sha256"):
        reconstruct_manifest(malformed)


def test_manifest_exact_comparison_detects_file_change(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    manifest = build_manifest(corpus)
    group = _group(1)
    group["surface_variants"][0]["description"] = "changed after freeze"
    _rewrite_group(corpus, 1, group)
    with pytest.raises(ValueError, match="does not exactly match"):
        verify_manifest_against_corpus(corpus, manifest)


def test_seal_binds_manifest_corpus_and_full_commit(tmp_path: Path) -> None:
    manifest = build_manifest(_write_corpus(tmp_path))
    seal = create_seal(manifest, source_commit=SOURCE_COMMIT)
    assert seal["seal_version"] == LC4V3_SEAL_SCHEMA
    assert seal["corpus_hash"] == manifest["corpus_hash"]
    assert seal["source_commit"] == SOURCE_COMMIT
    assert seal["consumed"] is False
    assert verify_seal(seal, manifest, expected_source_commit=SOURCE_COMMIT) == seal


@pytest.mark.parametrize("commit", ["abc123", "g" * 40, "unknown-commit"])
def test_seal_rejects_noncanonical_source_commit(tmp_path: Path, commit: str) -> None:
    manifest = build_manifest(_write_corpus(tmp_path))
    with pytest.raises(ValueError, match="full 40-hex"):
        create_seal(manifest, source_commit=commit)


def test_verify_seal_rejects_consumed_stale_and_extra_state(tmp_path: Path) -> None:
    manifest = build_manifest(_write_corpus(tmp_path))
    seal = create_seal(manifest, source_commit=SOURCE_COMMIT)
    consumed = {**seal, "consumed": True}
    with pytest.raises(ValueError, match="already consumed"):
        verify_seal(consumed, manifest)
    with pytest.raises(ValueError, match="does not match frozen HEAD"):
        verify_seal(seal, manifest, expected_source_commit="4" * 40)
    extra = {**seal, "unexpected": True}
    with pytest.raises(ValueError, match="schema drift"):
        verify_seal(extra, manifest)


def test_get_source_commit_is_full_head() -> None:
    assert get_source_commit() == subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
    ).strip()


def test_aggregate_is_identity_bound_and_exact(tmp_path: Path) -> None:
    report = _evaluate(_write_corpus(tmp_path))
    assert report["schema_version"] == LC4V3_REPORT_SCHEMA
    assert report["manifest_hash"] == MANIFEST_HASH
    assert report["corpus_hash"] == CORPUS_HASH
    assert report["source_commit"] == SOURCE_COMMIT
    assert report["total_samples"] == 576
    assert set(PER_DIMENSION_NAMES) <= set(report["per_dimension"])
    assert all(report["per_dimension"][name]["total"] == 576 for name in PER_DIMENSION_NAMES)
    assert report["variance"] == {
        "variant_scenario_count": 0,
        "variant_sample_count": 0,
        "total_repeats": 2,
        "all_samples_deterministic": True,
    }
    assert validate_report_hash(report) is True
    assert check_aggregate_report(report) == {"valid": True, "errors": []}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"manifest_hash": "bad", "corpus_hash": CORPUS_HASH, "source_commit": SOURCE_COMMIT},
        {"manifest_hash": MANIFEST_HASH, "corpus_hash": "bad", "source_commit": SOURCE_COMMIT},
        {"manifest_hash": MANIFEST_HASH, "corpus_hash": CORPUS_HASH, "source_commit": "short"},
    ],
)
def test_aggregate_rejects_invalid_identity(tmp_path: Path, kwargs: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        evaluate_aggregate(_scenarios(_write_corpus(tmp_path)), **kwargs)


def test_aggregate_rejects_duplicate_ids_and_trajectory_drift(tmp_path: Path) -> None:
    scenarios = _scenarios(_write_corpus(tmp_path))
    duplicated = list(scenarios)
    duplicated[1] = duplicated[0]
    with pytest.raises(ValueError, match="unique"):
        evaluate_aggregate(
            duplicated, manifest_hash=MANIFEST_HASH,
            corpus_hash=CORPUS_HASH, source_commit=SOURCE_COMMIT,
        )
    one_turn = scenarios[0].model_copy(update={"dialogue_turns": scenarios[0].dialogue_turns * 2})
    drifted = list(scenarios)
    drifted[0] = one_turn
    with pytest.raises(ValueError, match="Trajectory population"):
        evaluate_aggregate(
            drifted, manifest_hash=MANIFEST_HASH,
            corpus_hash=CORPUS_HASH, source_commit=SOURCE_COMMIT,
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"utterances": ["secret"]},
        {"scenario_ids": ["secret"]},
        {"nested": {"expected_labels": ["secret"]}},
        {"nested": [{"source_spans_by_field": {"x": "secret"}}]},
        {"safe": "contains lc4v3_group_001"},
    ],
)
def test_recursive_leakage_lint_rejects_case_structures(payload: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        check_forbidden_aggregate_keys(payload)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda report: report.update({"unexpected": True}),
        lambda report: report["per_dimension"]["safety"].update({"passed": 577, "failed": 0}),
        lambda report: report["failure_layers"].update({"unknown": 1}),
        lambda report: report["variance"].update({"total_repeats": 3}),
        lambda report: report["critical_slices"]["by_action"][0].update({"slice_key": "unknown"}),
        lambda report: report["coverage_cells"].update({"distinct_cell_count": 0}),
        lambda report: report.update({"source_commit": "short"}),
    ],
)
def test_post_consumption_check_fails_closed(
    tmp_path: Path, mutate: Any,
) -> None:
    report = _evaluate(_write_corpus(tmp_path))
    mutate(report)
    report["report_hash"] = _stable_hash(_canonical_json({k: v for k, v in report.items() if k != "report_hash"}))
    result = check_aggregate_report(report)
    assert result["valid"] is False
    assert result["errors"]


def test_post_consumption_check_needs_no_corpus(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    report = _evaluate(corpus)
    before = deepcopy(report)
    shutil.rmtree(corpus)
    assert check_aggregate_report(report)["valid"] is True
    assert report == before


def test_cli_manifest_seal_and_one_shot_baseline(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    seal_path = tmp_path / "seal.json"
    report_path = tmp_path / "aggregate.json"
    consumed_path = tmp_path / "consumed.json"

    built = _run_cli("build-manifest", str(corpus), "--write", str(manifest_path))
    assert built.returncode == 0, built.stdout + built.stderr
    checked = _run_cli("check-manifest", str(corpus), str(manifest_path))
    assert checked.returncode == 0, checked.stdout + checked.stderr
    sealed = _run_cli("create-seal", str(corpus), str(manifest_path), "--write", str(seal_path))
    assert sealed.returncode == 0, sealed.stdout + sealed.stderr
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    assert seal["source_commit"] == get_source_commit()

    baseline = _run_cli(
        "baseline-once", str(corpus), str(manifest_path), str(seal_path),
        "--write", str(report_path), str(consumed_path),
    )
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    consumed = json.loads(consumed_path.read_text(encoding="utf-8"))
    assert check_aggregate_report(report)["valid"] is True
    assert consumed["consumed"] is True
    assert consumed["report_hash"] == report["report_hash"]

    second = _run_cli(
        "baseline-once", str(corpus), str(manifest_path), str(seal_path),
        "--write", str(report_path), str(tmp_path / "second-consumed.json"),
    )
    assert second.returncode != 0
    assert "already exists" in second.stderr


def test_cli_baseline_rejects_unbound_or_consumed_seal_without_output(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    manifest = build_manifest(corpus)
    manifest_path = tmp_path / "manifest.json"
    seal_path = tmp_path / "seal.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    seal = create_seal(manifest, source_commit=get_source_commit())
    seal["consumed"] = True
    seal_path.write_text(json.dumps(seal), encoding="utf-8")
    report_path = tmp_path / "report.json"
    consumed_path = tmp_path / "consumed.json"
    completed = _run_cli(
        "baseline-once", str(corpus), str(manifest_path), str(seal_path),
        "--write", str(report_path), str(consumed_path),
    )
    assert completed.returncode != 0
    assert not report_path.exists()
    assert not consumed_path.exists()


def test_cli_partial_failure_is_visible_and_not_repeatable(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    manifest = build_manifest(corpus)
    manifest_path = tmp_path / "manifest.json"
    seal_path = tmp_path / "seal.json"
    report_path = tmp_path / "report.json"
    impossible_consumed = tmp_path / "missing" / "consumed.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    seal_path.write_text(
        json.dumps(create_seal(manifest, source_commit=get_source_commit())),
        encoding="utf-8",
    )
    first = _run_cli(
        "baseline-once", str(corpus), str(manifest_path), str(seal_path),
        "--write", str(report_path), str(impossible_consumed),
    )
    assert first.returncode != 0
    assert report_path.exists()
    assert not impossible_consumed.exists()
    second = _run_cli(
        "baseline-once", str(corpus), str(manifest_path), str(seal_path),
        "--write", str(report_path), str(tmp_path / "other.json"),
    )
    assert second.returncode != 0
    assert "already exists" in second.stderr


def test_cli_rejects_path_aliasing(tmp_path: Path) -> None:
    corpus = _write_corpus(tmp_path)
    manifest = build_manifest(corpus)
    manifest_path = tmp_path / "manifest.json"
    seal_path = tmp_path / "seal.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    seal_path.write_text(
        json.dumps(create_seal(manifest, source_commit=get_source_commit())),
        encoding="utf-8",
    )
    completed = _run_cli(
        "baseline-once", str(corpus), str(manifest_path), str(seal_path),
        "--write", str(manifest_path), str(tmp_path / "consumed.json"),
    )
    assert completed.returncode != 0
    assert "must be distinct" in completed.stderr


def test_framework_import_isolation() -> None:
    validate_lc4v3_isolation()


def test_no_real_v3_artifact_exists_in_repository() -> None:
    for forbidden in (
        ROOT / "tests/fixtures/bernie_lc4_holdout_v3",
        ROOT / "docs/bernie-lc4v3-seal.json",
        ROOT / "docs/bernie-lc4v3-aggregate-report.json",
        ROOT / "scripts/bernie_lc4v3_authoring.py",
    ):
        assert not forbidden.exists()
