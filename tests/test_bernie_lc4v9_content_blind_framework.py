from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
)
from app.services.bernie.lc4v9_content_blind_framework import (
    ACTIONS,
    CANONICAL_PROJECTION_FIELDS,
    DEFAULT_THRESHOLDS,
    LANGUAGE_FORMS,
    SCORING_DIMENSIONS,
    BindingValidationError,
    GoldValidationError,
    ReportError,
    SchemaValidationError,
    ShapeValidationError,
    canonical_json_bytes,
    canonicalize_json,
    run_certification,
    validate_canonical_projection,
    validate_evaluator_result,
    validate_fixture_schema,
    validate_fixture_shape,
    validate_gold_cross_field_consistency,
    validate_manifest_schema,
    validate_report_schema,
    validate_threshold_schema,
)


FIXTURE_PATH = "protected/lc4v9_fixture.json"
FRAMEWORK_PATH = "app/services/bernie/lc4v9_content_blind_framework.py"
EVALUATOR_PATH = "tests/test_bernie_lc4v9_content_blind_framework.py"
THRESHOLD_PATH = "protected/lc4v9_thresholds.json"
MANIFEST_PATH = "protected/lc4v9_manifest.json"
SEAL_PATH = "protected/lc4v9_seal.json"
MARKER_PATH = "protected/lc4v9_attempt.marker"
REPORT_PATH = "protected/lc4v9_report.json"
ATTEMPT_ID = "lc4v9-one-shot-001"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _projection() -> dict[str, Any]:
    return {
        "requires_clarification": False,
        "clarification_choices": [],
        "resolved_patient": None,
        "resolved_practitioner": None,
        "resolved_practitioner_id": None,
        "selected_tools": [],
        "authority": "read",
        "diary_relation": "no_conflict",
        "conflicting_fields": [],
        "downstream_outcome": None,
        "appointment_delta_count": 0,
        "audit_delta_count": 0,
        "simulated_write": False,
        "entity_semantics_unchanged": True,
    }


def _gold(action: str) -> dict[str, Any]:
    return {
        "intended_action": action,
        "action_semantics": {"opaque": True},
        "temporal_relation": "unspecified",
        "temporal_bounds": {"earliest_time": None, "latest_time": None},
        "normalized_values": {},
        "entity_semantics": {
            "patient": None,
            "practitioner": None,
            "practitioner_id": None,
        },
        "lossless_source_spans": [],
        "extraction_clarification": None,
        "semantic_outcome": "no_action",
        "mutation_allowed": False,
        "safe": True,
        "canonical_projection": _projection(),
        "policy_clarification": None,
        "clarification_composition": None,
        "interpretation_tool": {"opaque": True},
        "replay": {"opaque": True},
    }


def make_fixture() -> dict[str, Any]:
    groups = []
    scenarios = []
    for action_index, action in enumerate(ACTIONS):
        for action_group in range(4):
            group_id = f"g-{action_index}-{action_group}"
            groups.append({"id": group_id, "action": action})
            for scenario_index in range(12):
                language_form = LANGUAGE_FORMS[scenario_index // 2]
                turn_count = 2 if scenario_index < 3 else 1
                scenario_id = f"s-{action_index}-{action_group}-{scenario_index}"
                scenarios.append(
                    {
                        "id": scenario_id,
                        "coverage_cell": f"cell-{scenario_id}",
                        "group": group_id,
                        "language_form": language_form,
                        "turn_count": turn_count,
                        "receptionist_utterances": [
                            f"opaque-{scenario_id}-{turn}" for turn in range(turn_count)
                        ],
                        "diary_state": {},
                        "gold": _gold(action),
                    }
                )
    return {
        "schema_version": "lc4v9-fixture.v1",
        "groups": groups,
        "scenarios": scenarios,
    }


def make_evaluator_result(
    fixture: dict[str, Any],
    *,
    failed: dict[str, set[str]] | None = None,
    validation_errors: int = 0,
    runtime_exceptions: int = 0,
    policy_failures: int = 0,
    integration_failures: int = 0,
) -> dict[str, Any]:
    failed = failed or {}
    results = []
    for scenario in fixture["scenarios"]:
        dimensions = {
            dimension: dimension not in failed.get(scenario["id"], set())
            for dimension in SCORING_DIMENSIONS
        }
        for repeat in (0, 1):
            results.append(
                {
                    "scenario_id": scenario["id"],
                    "repeat": repeat,
                    "dimensions": copy.deepcopy(dimensions),
                    "complete": all(dimensions.values()),
                }
            )
    return {
        "schema_version": "lc4v9-evaluator-result.v1",
        "results": results,
        "validation_errors": validation_errors,
        "runtime_exceptions": runtime_exceptions,
        "policy_failures": policy_failures,
        "integration_failures": integration_failures,
    }


class Harness:
    def __init__(self, repository_root: Path) -> None:
        self.root = repository_root
        self.fixture = make_fixture()
        self.evaluator_result = make_evaluator_result(self.fixture)
        self.raise_from_evaluator = False
        framework_source = Path(FRAMEWORK_PATH).read_bytes()
        evaluator_source = (
            "from __future__ import annotations\n"
            "import copy\n"
            "RESULT = None\n"
            "RAISE = False\n"
            "def evaluate(fixture):\n"
            "    if RAISE:\n"
            "        raise RuntimeError('opaque evaluator failure')\n"
            "    return copy.deepcopy(RESULT)\n"
        ).encode("utf-8")
        source_files = {
            FIXTURE_PATH: canonical_json_bytes(self.fixture),
            FRAMEWORK_PATH: framework_source,
            EVALUATOR_PATH: evaluator_source,
            THRESHOLD_PATH: canonical_json_bytes(DEFAULT_THRESHOLDS),
        }
        for relative_path, payload in source_files.items():
            target = self.root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

        self._git("init", "-q")
        self._git("config", "user.email", "lc4v9@example.invalid")
        self._git("config", "user.name", "LC4V9 Opaque Test")
        self._git("add", FIXTURE_PATH, FRAMEWORK_PATH, EVALUATOR_PATH, THRESHOLD_PATH)
        self._git("commit", "-q", "-m", "freeze opaque source")
        source_commit = self._git("rev-parse", "HEAD")
        self.manifest = {
            "schema_version": "lc4v9-manifest.v1",
            "source_commit": source_commit,
            "fixture_path": FIXTURE_PATH,
            "fixture_hash": _sha(source_files[FIXTURE_PATH]),
            "fixture_blob": self._git("rev-parse", f"{source_commit}:{FIXTURE_PATH}"),
            "framework_path": FRAMEWORK_PATH,
            "framework_hash": _sha(source_files[FRAMEWORK_PATH]),
            "framework_blob": self._git("rev-parse", f"{source_commit}:{FRAMEWORK_PATH}"),
            "evaluator_path": EVALUATOR_PATH,
            "evaluator_hash": _sha(source_files[EVALUATOR_PATH]),
            "evaluator_blob": self._git("rev-parse", f"{source_commit}:{EVALUATOR_PATH}"),
            "threshold_path": THRESHOLD_PATH,
            "threshold_hash": _sha(source_files[THRESHOLD_PATH]),
            "threshold_blob": self._git("rev-parse", f"{source_commit}:{THRESHOLD_PATH}"),
            "manifest_path": MANIFEST_PATH,
            "seal_path": SEAL_PATH,
            "marker_path": MARKER_PATH,
            "report_path": REPORT_PATH,
        }
        manifest_bytes = canonical_json_bytes(self.manifest)
        self._write(MANIFEST_PATH, manifest_bytes)
        self.seal = {
            "schema_version": "lc4v9-seal.v1",
            "manifest_hash": _sha(manifest_bytes),
            "attempt_id": ATTEMPT_ID,
            "status": "unconsumed",
        }
        self._write(SEAL_PATH, canonical_json_bytes(self.seal))
        self.framework_module = self._load_module(
            "lc4v9_opaque_framework", self.root / FRAMEWORK_PATH
        )
        self.evaluator_module = self._load_module(
            "lc4v9_opaque_evaluator", self.root / EVALUATOR_PATH
        )

    def _git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ("git", *arguments),
            cwd=self.root,
            capture_output=True,
            check=True,
            text=True,
        )
        return completed.stdout.strip()

    def _write(self, relative_path: str, payload: bytes) -> None:
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

    def _load_module(self, stem: str, path: Path):
        module_name = f"{stem}_{abs(hash(str(self.root)))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def mutate_json(self, relative_path: str, mutation) -> None:
        target = self.root / relative_path
        value = json.loads(target.read_bytes())
        mutation(value)
        target.write_bytes(canonical_json_bytes(value))

    def run(
        self,
        *,
        attempt_id: str = ATTEMPT_ID,
        marker_path: str = MARKER_PATH,
        report_path: str = REPORT_PATH,
    ):
        self.evaluator_module.RESULT = copy.deepcopy(self.evaluator_result)
        self.evaluator_module.RAISE = self.raise_from_evaluator
        return self.framework_module.run_certification(
            attempt_id=attempt_id,
            fixture_path=FIXTURE_PATH,
            framework_path=FRAMEWORK_PATH,
            evaluator=self.evaluator_module.evaluate,
            threshold_path=THRESHOLD_PATH,
            manifest_path=MANIFEST_PATH,
            seal_path=SEAL_PATH,
            marker_path=marker_path,
            report_path=report_path,
            repository_root=str(self.root),
        )


def test_valid_fixture_has_exact_comparable_shape() -> None:
    fixture = make_fixture()
    validate_fixture_schema(fixture)
    validate_fixture_shape(fixture)
    validate_gold_cross_field_consistency(fixture)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda fixture: fixture.pop("schema_version"),
        lambda fixture: fixture.__setitem__("unknown", True),
        lambda fixture: fixture["groups"][0].__setitem__("unknown", True),
        lambda fixture: fixture["scenarios"][0].pop("coverage_cell"),
        lambda fixture: fixture["scenarios"][0]["gold"].pop("replay"),
        lambda fixture: fixture["scenarios"][0]["gold"].__setitem__("unknown", True),
    ),
)
def test_fixture_schemas_reject_missing_or_unknown_fields(mutation) -> None:
    fixture = make_fixture()
    mutation(fixture)
    with pytest.raises(SchemaValidationError):
        validate_fixture_schema(fixture)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda fixture: fixture["groups"].pop(),
        lambda fixture: fixture["groups"][1].__setitem__("id", fixture["groups"][0]["id"]),
        lambda fixture: fixture["scenarios"].pop(),
        lambda fixture: fixture["scenarios"][1].__setitem__("id", fixture["scenarios"][0]["id"]),
        lambda fixture: fixture["scenarios"][1].__setitem__("coverage_cell", fixture["scenarios"][0]["coverage_cell"]),
        lambda fixture: fixture["scenarios"][0].__setitem__("turn_count", 3),
        lambda fixture: fixture["scenarios"][0].__setitem__("language_form", "other"),
        lambda fixture: fixture["scenarios"][0]["gold"].__setitem__("intended_action", "cancel"),
    ),
)
def test_shape_contract_fails_closed(mutation) -> None:
    fixture = make_fixture()
    mutation(fixture)
    with pytest.raises(ShapeValidationError):
        validate_fixture_shape(fixture)


def test_projection_canonicalizes_tuples_and_keeps_nulls() -> None:
    projection = _projection()
    projection["selected_tools"] = ("opaque-tool",)
    validated = validate_canonical_projection(projection)
    assert validated["selected_tools"] == ["opaque-tool"]
    assert validated["resolved_patient"] is None
    assert set(validated) == set(CANONICAL_PROJECTION_FIELDS)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda projection: projection.pop("authority"),
        lambda projection: projection.__setitem__("unknown", True),
        lambda projection: projection.__setitem__("simulated_write", 1),
        lambda projection: projection.__setitem__("appointment_delta_count", -1),
    ),
)
def test_projection_rejects_schema_and_type_drift(mutation) -> None:
    projection = _projection()
    mutation(projection)
    with pytest.raises(SchemaValidationError):
        validate_canonical_projection(projection)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda gold: gold.__setitem__("mutation_allowed", True),
        lambda gold: gold["canonical_projection"].__setitem__("simulated_write", True),
        lambda gold: gold["canonical_projection"].__setitem__("clarification_choices", ["opaque"]),
        lambda gold: gold["canonical_projection"].__setitem__("resolved_patient", "mismatch"),
        lambda gold: gold.__setitem__("temporal_relation", "after"),
    ),
)
def test_gold_cross_field_contradictions_are_rejected(mutation) -> None:
    fixture = make_fixture()
    mutation(fixture["scenarios"][0]["gold"])
    with pytest.raises(GoldValidationError):
        validate_gold_cross_field_consistency(fixture)


def test_valid_mutation_and_clarification_gold() -> None:
    fixture = make_fixture()
    mutation = fixture["scenarios"][0]["gold"]
    mutation["semantic_outcome"] = "propose_mutation"
    mutation["mutation_allowed"] = True
    mutation["canonical_projection"].update(
        {
            "selected_tools": ["create_booking"],
            "authority": "read",
            "appointment_delta_count": 1,
            "audit_delta_count": 1,
            "simulated_write": True,
            "downstream_outcome": "proposal_created",
        }
    )
    clarification = fixture["scenarios"][1]["gold"]
    clarification["semantic_outcome"] = "clarify"
    clarification["canonical_projection"].update(
        {
            "requires_clarification": True,
            "clarification_choices": ["opaque-choice"],
            "selected_tools": ["request_clarification"],
            "authority": "clarify",
            "downstream_outcome": "clarification_required",
        }
    )
    validate_gold_cross_field_consistency(fixture)


def test_refusal_tool_is_safe_nonmutation_not_hidden_write() -> None:
    fixture = make_fixture()
    refusal = fixture["scenarios"][0]["gold"]
    refusal["semantic_outcome"] = "refuse"
    refusal["canonical_projection"].update(
        {
            "selected_tools": ["refuse_instruction"],
            "authority": "refuse",
            "downstream_outcome": "instruction_refused",
        }
    )
    validate_gold_cross_field_consistency(fixture)


def test_temporal_relation_is_not_conflated_with_diary_relation() -> None:
    fixture = make_fixture()
    gold = fixture["scenarios"][0]["gold"]
    gold["temporal_relation"] = "interval"
    gold["temporal_bounds"] = {"earliest_time": "15:00", "latest_time": "16:30"}
    gold["canonical_projection"]["diary_relation"] = "no_conflict"
    validate_gold_cross_field_consistency(fixture)


def test_frozen_threshold_values_cannot_be_weakened() -> None:
    validate_threshold_schema(copy.deepcopy(DEFAULT_THRESHOLDS))
    weakened = copy.deepcopy(DEFAULT_THRESHOLDS)
    weakened["complete_min"] = 0
    with pytest.raises(SchemaValidationError):
        validate_threshold_schema(weakened)


def test_manifest_rejects_missing_unknown_and_absolute_paths(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    validate_manifest_schema(harness.manifest)
    for change in ("missing", "unknown", "absolute"):
        manifest = copy.deepcopy(harness.manifest)
        if change == "missing":
            manifest.pop("evaluator_path")
        elif change == "unknown":
            manifest["unknown"] = True
        else:
            manifest["evaluator_path"] = "C:/outside/evaluator.py"
        with pytest.raises((SchemaValidationError, BindingValidationError)):
            validate_manifest_schema(manifest)


def test_result_contract_binds_ids_repeats_dimensions_and_conjunction() -> None:
    fixture = make_fixture()
    valid = make_evaluator_result(fixture)
    validate_evaluator_result(valid, fixture)
    mutations = []
    unknown_id = copy.deepcopy(valid)
    unknown_id["results"][0]["scenario_id"] = "unknown"
    mutations.append(unknown_id)
    duplicate_repeat = copy.deepcopy(valid)
    duplicate_repeat["results"][1]["repeat"] = 0
    mutations.append(duplicate_repeat)
    false_complete = copy.deepcopy(valid)
    false_complete["results"][0]["dimensions"]["policy_behaviour"] = False
    mutations.append(false_complete)
    extra_field = copy.deepcopy(valid)
    extra_field["results"][0]["extra"] = True
    mutations.append(extra_field)
    variance = copy.deepcopy(valid)
    variance["results"][0]["dimensions"]["policy_behaviour"] = False
    variance["results"][0]["complete"] = False
    mutations.append(variance)
    for result in mutations:
        with pytest.raises((SchemaValidationError, ShapeValidationError)):
            validate_evaluator_result(result, fixture)


def test_marker_is_durably_consumed_before_any_protected_read(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_PASS
    assert outcome.attempt_consumed is True
    assert json.loads((tmp_path / MARKER_PATH).read_bytes())["status"] == "consumed"


def test_valid_pass_has_canonical_complete_report_hash(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_PASS
    report_bytes = (tmp_path / REPORT_PATH).read_bytes()
    assert outcome.report_hash == _sha(report_bytes)
    report = json.loads(report_bytes)
    validate_report_schema(report)
    assert report["aggregate_counts"]["complete"] == 576
    assert report["aggregate_counts"]["policy_failures"] == 0


def test_dimension_miss_is_not_automatically_a_policy_failure(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    scenario_id = harness.fixture["scenarios"][0]["id"]
    harness.evaluator_result = make_evaluator_result(
        harness.fixture,
        failed={scenario_id: {"policy_behaviour"}},
    )
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_PASS
    report = json.loads((tmp_path / REPORT_PATH).read_bytes())
    assert report["aggregate_counts"]["dimension_totals"]["policy_behaviour"] == 574
    assert report["aggregate_counts"]["policy_failures"] == 0


@pytest.mark.parametrize("counter", ("policy_failures", "integration_failures"))
def test_explicit_product_failure_counter_returns_certification_fail(counter: str, tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    harness.evaluator_result[counter] = 1
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_FAIL
    assert outcome.report_hash == _sha((tmp_path / REPORT_PATH).read_bytes())


def test_evidence_counter_returns_invalid_not_product_fail(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    harness.evaluator_result["validation_errors"] = 1
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is True


@pytest.mark.parametrize(
    "corrupt",
    (
        lambda harness: harness.mutate_json(FIXTURE_PATH, lambda value: value.pop("schema_version")),
        lambda harness: harness.mutate_json(THRESHOLD_PATH, lambda value: value.__setitem__("complete_min", 0)),
        lambda harness: harness.mutate_json(MANIFEST_PATH, lambda value: value.__setitem__("evaluator_path", "other.py")),
        lambda harness: harness.mutate_json(SEAL_PATH, lambda value: value.__setitem__("attempt_id", "other-attempt")),
        lambda harness: (harness.root / EVALUATOR_PATH).write_bytes(b"changed"),
    ),
)
def test_all_evidence_failures_after_consumption_return_invalid(corrupt, tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    corrupt(harness)
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is True
    assert json.loads((tmp_path / MARKER_PATH).read_bytes())["status"] == "consumed"


def test_marker_collision_stops_before_protected_reads(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    (tmp_path / MARKER_PATH).write_bytes(b"already consumed")
    (tmp_path / FIXTURE_PATH).unlink()
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is True
    assert outcome.evidence_error == "attempt_already_consumed"
    assert not (tmp_path / REPORT_PATH).exists()


def test_marker_creation_error_is_terminal_invalid_without_input_read(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    (tmp_path / "blocked").write_bytes(b"not a directory")
    outcome = harness.run(marker_path="blocked/marker")
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is False
    assert outcome.evidence_error == "marker_creation_error"


def test_invalid_launch_id_still_consumes_the_marker(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    outcome = harness.run(attempt_id="")
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is True
    marker = json.loads((tmp_path / MARKER_PATH).read_bytes())
    assert marker["status"] == "consumed"
    assert marker["attempt_id"] == "invalid-launch-attempt"


def test_unsealed_report_path_is_never_written(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    outcome = harness.run(report_path="protected/unsealed-report.json")
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is True
    assert not (tmp_path / "protected/unsealed-report.json").exists()


def test_evaluator_exception_returns_invalid_with_consumed_marker(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    harness.raise_from_evaluator = True
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.attempt_consumed is True
    assert outcome.evidence_error == "RuntimeError"


def test_report_write_or_readback_failure_cannot_return_pass(tmp_path: Path) -> None:
    harness = Harness(tmp_path)
    (tmp_path / REPORT_PATH).write_bytes(b"preexisting report")
    outcome = harness.run()
    assert outcome.decision == CERTIFICATION_INVALID
    assert outcome.report_hash is None
    assert outcome.attempt_consumed is True


def test_report_rejects_nested_oracle_content() -> None:
    report = {
        "schema_version": "lc4v9-report.v1",
        "decision": CERTIFICATION_INVALID,
        "aggregate_counts": {
            "total_samples": 0,
            "complete": 0,
            "safety": 0,
            "dimension_totals": {dimension: 0 for dimension in SCORING_DIMENSIONS},
            "interpretation_failures": 0,
            "policy_failures": 0,
            "integration_failures": 0,
            "validation_errors": 1,
            "runtime_exceptions": 0,
            "repeat_variance": 0,
        },
        "failing_gates": [{"oracle": "hidden"}],
        "failing_group_ids": [],
        "failing_form_labels": [],
    }
    with pytest.raises(ReportError):
        validate_report_schema(report)


def test_canonical_json_is_deterministic_and_lossless_for_nulls() -> None:
    assert canonicalize_json(("opaque", None)) == ["opaque", None]
    first = canonical_json_bytes({"b": None, "a": (1, 2)})
    second = canonical_json_bytes({"a": [1, 2], "b": None})
    assert first == second == b'{"a":[1,2],"b":null}\n'


def test_framework_contains_no_actual_v9_corpus_or_protected_import() -> None:
    source = Path("app/services/bernie/lc4v9_content_blind_framework.py").read_text(
        encoding="utf-8"
    ).casefold()
    assert "lc4v8" not in source
    assert "tomorrow at 3pm" not in source
    assert "receptionist_utterances" in source  # schema name only
