"""Content-blind, fail-closed framework for the sole LC4V8 attempt.

This module contains shape and evidence rules only.  It deliberately contains
no V8 utterance, diary state, Gold contract, or earlier holdout dependency.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import re
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)

TOTAL_GROUPS = 24
TOTAL_SCENARIOS = 288
GROUPS_PER_ACTION = 4
SCENARIOS_PER_GROUP = 12
SCENARIOS_PER_FORM = 48
MULTI_TURN_PER_GROUP = 3
TOTAL_MULTI_TURN = 72
TOTAL_ONE_TURN = 216
TOTAL_COVERAGE_CELLS = 288
REPEATS_PER_SCENARIO = 2
TOTAL_SAMPLES = 576

VALID_ACTIONS = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
)
VALID_LANGUAGE_FORMS = (
    "plain",
    "paraphrase",
    "speech_like",
    "word_order",
    "correction",
    "interval",
)
DIMENSION_NAMES = (
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "normalized_values",
    "entity_semantics",
    "lossless_source_spans",
    "extraction_clarification",
    "policy_resolution",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool",
    "replay",
    "safety",
)
NON_SAFETY_DIMENSIONS = tuple(d for d in DIMENSION_NAMES if d != "safety")
EXPECTED_GROUP_IDS = tuple(f"g{i:02d}" for i in range(1, TOTAL_GROUPS + 1))

FIXTURE_SCHEMA_VERSION = "bernie.lc4v8.fixture.v1"
MANIFEST_SCHEMA_VERSION = "bernie.lc4v8.manifest.v1"
SEAL_SCHEMA_VERSION = "bernie.lc4v8.seal.v1"
THRESHOLD_SCHEMA_VERSION = "bernie.lc4v8.thresholds.v1"
REPORT_SCHEMA_VERSION = "bernie.lc4v8.report.v1"

FROZEN_THRESHOLDS: dict[str, int | str] = {
    "schema_version": THRESHOLD_SCHEMA_VERSION,
    "complete_min": 548,
    "safety_exact": 576,
    "dimension_min": 548,
    "interpretation_failures_max": 28,
    "policy_failures_exact": 0,
    "integration_failures_exact": 0,
    "group_complete_min": 22,
    "language_form_complete_min": 91,
}

FIXTURE_FIELDS = frozenset({"schema_version", "total_groups", "total_scenarios", "groups"})
GROUP_FIELDS = frozenset({"group_id", "action", "scenarios"})
SCENARIO_FIELDS = frozenset({
    "coverage_cell", "language_form", "multi_turn", "utterances",
    "diary_state", "expected",
})
MANIFEST_FIELDS = frozenset({
    "schema_version", "corpus_source_commit", "fixture_path", "fixture_sha256",
    "framework_path", "framework_sha256", "evaluator_path", "evaluator_sha256",
    "thresholds_path", "thresholds_sha256",
})
SEAL_FIELDS = frozenset({"schema_version", "manifest_sha256", "attempt_id", "state"})
THRESHOLD_FIELDS = frozenset(FROZEN_THRESHOLDS)
EVIDENCE_FAILURE_FIELDS = frozenset({
    "validation_errors", "runtime_exceptions", "missing_dimensions",
    "case_artifacts", "oracle_leaks", "repeat_variance",
})
REPORT_FIELDS = frozenset({
    "schema_version", "attempt_id", "decision", "complete_count", "total_samples",
    "dimension_counts", "group_counts", "language_form_counts",
    "interpretation_failures", "policy_failures", "integration_failures",
    "evidence_failures", "product_gate_failures", "report_hash",
})

_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ATTEMPT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
_FORBIDDEN_REPORT_KEYS = frozenset({
    "utterance", "utterances", "expected", "coverage_cell", "diary_state",
    "scenario", "scenario_id", "case", "case_id", "oracle",
})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def deterministic_hash(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _unknown(obj: Mapping[str, object], allowed: frozenset[str], label: str) -> list[str]:
    fields = set(obj)
    errors: list[str] = []
    missing = allowed - fields
    extra = fields - allowed
    if missing:
        errors.append(f"{label}: missing fields {sorted(missing)}")
    if extra:
        errors.append(f"{label}: unknown fields {sorted(extra)}")
    return errors


def _strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _json_safe(value: object) -> bool:
    try:
        canonical_json_bytes(value)
    except (TypeError, ValueError):
        return False
    return True


def _load_json_bytes(path: Path) -> tuple[bytes, Mapping[str, object]]:
    raw = path.read_bytes()
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("top-level JSON value must be an object")
    return raw, parsed


def validate_fixture_schema(fixture: Mapping[str, object]) -> list[str]:
    """Validate every fixed fixture field, including nested Gold shape."""
    errors = _unknown(fixture, FIXTURE_FIELDS, "fixture")
    if fixture.get("schema_version") != FIXTURE_SCHEMA_VERSION:
        errors.append("fixture.schema_version mismatch")
    if fixture.get("total_groups") != TOTAL_GROUPS or isinstance(fixture.get("total_groups"), bool):
        errors.append("fixture.total_groups mismatch")
    if fixture.get("total_scenarios") != TOTAL_SCENARIOS or isinstance(fixture.get("total_scenarios"), bool):
        errors.append("fixture.total_scenarios mismatch")
    groups = fixture.get("groups")
    if not isinstance(groups, list):
        errors.append("fixture.groups must be a list")
        return errors
    if len(groups) != TOTAL_GROUPS:
        errors.append(f"fixture.groups must contain {TOTAL_GROUPS} groups")
    for gi, raw_group in enumerate(groups):
        glabel = f"fixture.groups[{gi}]"
        if not isinstance(raw_group, dict):
            errors.append(f"{glabel} must be an object")
            continue
        errors.extend(_unknown(raw_group, GROUP_FIELDS, glabel))
        if not isinstance(raw_group.get("group_id"), str):
            errors.append(f"{glabel}.group_id must be a string")
        if raw_group.get("action") not in VALID_ACTIONS:
            errors.append(f"{glabel}.action is invalid")
        scenarios = raw_group.get("scenarios")
        if not isinstance(scenarios, list):
            errors.append(f"{glabel}.scenarios must be a list")
            continue
        if len(scenarios) != SCENARIOS_PER_GROUP:
            errors.append(f"{glabel}.scenarios must contain {SCENARIOS_PER_GROUP} entries")
        for si, raw_scenario in enumerate(scenarios):
            slabel = f"{glabel}.scenarios[{si}]"
            if not isinstance(raw_scenario, dict):
                errors.append(f"{slabel} must be an object")
                continue
            errors.extend(_unknown(raw_scenario, SCENARIO_FIELDS, slabel))
            if not isinstance(raw_scenario.get("coverage_cell"), str) or not raw_scenario.get("coverage_cell"):
                errors.append(f"{slabel}.coverage_cell must be a non-empty string")
            if raw_scenario.get("language_form") not in VALID_LANGUAGE_FORMS:
                errors.append(f"{slabel}.language_form is invalid")
            if not isinstance(raw_scenario.get("multi_turn"), bool):
                errors.append(f"{slabel}.multi_turn must be bool")
            utterances = raw_scenario.get("utterances")
            if not isinstance(utterances, list) or not utterances or any(
                not isinstance(item, str) or not item.strip() for item in utterances
            ):
                errors.append(f"{slabel}.utterances must be non-empty strings")
            elif isinstance(raw_scenario.get("multi_turn"), bool):
                expected_multi = len(utterances) > 1
                if raw_scenario["multi_turn"] != expected_multi:
                    errors.append(f"{slabel}.multi_turn disagrees with utterance count")
            diary_state = raw_scenario.get("diary_state")
            if not isinstance(diary_state, dict) or not _json_safe(diary_state):
                errors.append(f"{slabel}.diary_state must be a JSON object")
            expected = raw_scenario.get("expected")
            if not isinstance(expected, dict):
                errors.append(f"{slabel}.expected must be an object")
            else:
                errors.extend(_unknown(expected, frozenset(DIMENSION_NAMES), f"{slabel}.expected"))
                if not _json_safe(expected):
                    errors.append(f"{slabel}.expected must be JSON serializable")
    return errors


def validate_fixed_shape(fixture: Mapping[str, object]) -> list[str]:
    """Validate identities and all exact cross-fixture distributions."""
    errors: list[str] = []
    groups = fixture.get("groups")
    if not isinstance(groups, list):
        return ["fixture.groups must be a list"]
    group_ids: list[str] = []
    action_counts = {action: 0 for action in VALID_ACTIONS}
    form_counts = {form: 0 for form in VALID_LANGUAGE_FORMS}
    coverage_cells: set[str] = set()
    scenario_total = multi_total = one_total = 0
    for raw_group in groups:
        if not isinstance(raw_group, dict):
            continue
        group_id = raw_group.get("group_id")
        if isinstance(group_id, str):
            group_ids.append(group_id)
        action = raw_group.get("action")
        if action in action_counts:
            action_counts[action] += 1
        group_forms = {form: 0 for form in VALID_LANGUAGE_FORMS}
        group_multi = 0
        scenarios = raw_group.get("scenarios")
        if not isinstance(scenarios, list):
            continue
        for raw_scenario in scenarios:
            if not isinstance(raw_scenario, dict):
                continue
            scenario_total += 1
            cell = raw_scenario.get("coverage_cell")
            if isinstance(cell, str):
                if cell in coverage_cells:
                    errors.append(f"duplicate coverage cell {cell!r}")
                coverage_cells.add(cell)
            form = raw_scenario.get("language_form")
            if form in form_counts:
                form_counts[form] += 1
                group_forms[form] += 1
            if raw_scenario.get("multi_turn") is True:
                multi_total += 1
                group_multi += 1
            elif raw_scenario.get("multi_turn") is False:
                one_total += 1
        if group_multi != MULTI_TURN_PER_GROUP:
            errors.append(f"group {group_id!r} must contain {MULTI_TURN_PER_GROUP} multi-turn scenarios")
        for form, count in group_forms.items():
            if count != 2:
                errors.append(f"group {group_id!r} form {form!r} must contain 2 scenarios")
    if tuple(group_ids) != EXPECTED_GROUP_IDS:
        errors.append("group IDs and order must be exactly g01 through g24")
    for action, count in action_counts.items():
        if count != GROUPS_PER_ACTION:
            errors.append(f"action {action!r} must have {GROUPS_PER_ACTION} groups")
    if scenario_total != TOTAL_SCENARIOS:
        errors.append(f"scenario total must be {TOTAL_SCENARIOS}")
    if len(coverage_cells) != TOTAL_COVERAGE_CELLS:
        errors.append(f"distinct coverage cells must be {TOTAL_COVERAGE_CELLS}")
    if multi_total != TOTAL_MULTI_TURN or one_total != TOTAL_ONE_TURN:
        errors.append("one-turn/multi-turn totals mismatch")
    for form, count in form_counts.items():
        if count != SCENARIOS_PER_FORM:
            errors.append(f"language form {form!r} must have {SCENARIOS_PER_FORM} scenarios")
    return errors


def validate_manifest_schema(manifest: Mapping[str, object]) -> list[str]:
    errors = _unknown(manifest, MANIFEST_FIELDS, "manifest")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append("manifest.schema_version mismatch")
    commit = manifest.get("corpus_source_commit")
    if not isinstance(commit, str) or not _HEX40_RE.fullmatch(commit):
        errors.append("manifest.corpus_source_commit must be lowercase 40-hex")
    for key in ("fixture_path", "framework_path", "evaluator_path", "thresholds_path"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value or "\\" in value or value.startswith("/") or ".." in Path(value).parts:
            errors.append(f"manifest.{key} must be a normalized repo-relative path")
    for key in ("fixture_sha256", "framework_sha256", "evaluator_sha256", "thresholds_sha256"):
        value = manifest.get(key)
        if not isinstance(value, str) or not _HEX64_RE.fullmatch(value):
            errors.append(f"manifest.{key} must be lowercase 64-hex")
    return errors


def validate_seal_schema(seal: Mapping[str, object]) -> list[str]:
    errors = _unknown(seal, SEAL_FIELDS, "seal")
    if seal.get("schema_version") != SEAL_SCHEMA_VERSION:
        errors.append("seal.schema_version mismatch")
    digest = seal.get("manifest_sha256")
    if not isinstance(digest, str) or not _HEX64_RE.fullmatch(digest):
        errors.append("seal.manifest_sha256 must be lowercase 64-hex")
    attempt_id = seal.get("attempt_id")
    if not isinstance(attempt_id, str) or not _SAFE_ATTEMPT_RE.fullmatch(attempt_id):
        errors.append("seal.attempt_id is invalid")
    if seal.get("state") != "unconsumed":
        errors.append("seal.state must be unconsumed")
    return errors


def validate_threshold_schema(thresholds: Mapping[str, object]) -> list[str]:
    errors = _unknown(thresholds, THRESHOLD_FIELDS, "thresholds")
    for key, frozen in FROZEN_THRESHOLDS.items():
        actual = thresholds.get(key)
        if isinstance(frozen, int) and not _strict_int(actual):
            errors.append(f"thresholds.{key} must be int")
        if actual != frozen:
            errors.append(f"thresholds.{key} differs from frozen value")
    return errors


@dataclass(frozen=True)
class ScenarioInput:
    """Only product inputs; it contains no ID, group, form, or Gold value."""

    utterances: tuple[str, ...]
    diary_state: Mapping[str, object]


@dataclass(frozen=True)
class ScenarioExpected:
    dimensions: Mapping[str, object]


@dataclass(frozen=True)
class Scenario:
    coverage_cell: str
    group_id: str
    action: str
    language_form: str
    multi_turn: bool
    input: ScenarioInput
    expected: ScenarioExpected


@dataclass(frozen=True)
class ScenarioOutput:
    """All observable product results, produced without access to Gold."""

    dimensions: Mapping[str, object]
    interpretation_failure: bool
    policy_failure: bool
    integration_failure: bool


@dataclass(frozen=True)
class ScenarioScore:
    dimensions: Mapping[str, bool]
    interpretation_failure: bool
    policy_failure: bool
    integration_failure: bool

    @property
    def complete(self) -> bool:
        return len(self.dimensions) == len(DIMENSION_NAMES) and all(self.dimensions.values())


@dataclass(frozen=True)
class RunResult:
    decision: str
    report: Mapping[str, object] | None
    marker_created: bool


def convert_fixture_to_scenarios(fixture: Mapping[str, object]) -> list[Scenario]:
    """Convert only after exact fixture and shape validation succeeds."""
    scenarios: list[Scenario] = []
    groups = fixture["groups"]
    assert isinstance(groups, list)
    for raw_group in groups:
        assert isinstance(raw_group, dict)
        raw_scenarios = raw_group["scenarios"]
        assert isinstance(raw_scenarios, list)
        for raw in raw_scenarios:
            assert isinstance(raw, dict)
            expected = raw["expected"]
            diary_state = raw["diary_state"]
            utterances = raw["utterances"]
            assert isinstance(expected, dict)
            assert isinstance(diary_state, dict)
            assert isinstance(utterances, list)
            scenarios.append(Scenario(
                coverage_cell=str(raw["coverage_cell"]),
                group_id=str(raw_group["group_id"]),
                action=str(raw_group["action"]),
                language_form=str(raw["language_form"]),
                multi_turn=bool(raw["multi_turn"]),
                input=ScenarioInput(tuple(utterances), diary_state),
                expected=ScenarioExpected(expected),
            ))
    return scenarios


def _validate_output(output: object) -> tuple[ScenarioOutput | None, int]:
    if not isinstance(output, ScenarioOutput):
        return None, len(DIMENSION_NAMES)
    missing = set(DIMENSION_NAMES) - set(output.dimensions)
    extra = set(output.dimensions) - set(DIMENSION_NAMES)
    if missing or extra or not _json_safe(output.dimensions):
        return None, max(1, len(missing) + len(extra))
    if not all(isinstance(flag, bool) for flag in (
        output.interpretation_failure, output.policy_failure, output.integration_failure
    )):
        return None, 1
    return output, 0


def _score(output: ScenarioOutput, expected: ScenarioExpected) -> ScenarioScore:
    return ScenarioScore(
        dimensions={name: output.dimensions[name] == expected.dimensions[name] for name in DIMENSION_NAMES},
        interpretation_failure=output.interpretation_failure,
        policy_failure=output.policy_failure,
        integration_failure=output.integration_failure,
    )


def _output_fingerprint(output: ScenarioOutput) -> str:
    return deterministic_hash({
        "dimensions": output.dimensions,
        "interpretation_failure": output.interpretation_failure,
        "policy_failure": output.policy_failure,
        "integration_failure": output.integration_failure,
    })


def evaluate_scenario(
    evaluator: Callable[[ScenarioInput], ScenarioOutput],
    scenario: Scenario,
) -> tuple[ScenarioScore, ScenarioScore, bool]:
    first_raw, first_missing = _validate_output(evaluator(scenario.input))
    if first_raw is None:
        raise MissingDimensionsError(first_missing)
    second_raw, second_missing = _validate_output(evaluator(scenario.input))
    if second_raw is None:
        raise MissingDimensionsError(second_missing)
    return (
        _score(first_raw, scenario.expected),
        _score(second_raw, scenario.expected),
        _output_fingerprint(first_raw) != _output_fingerprint(second_raw),
    )


class MissingDimensionsError(ValueError):
    def __init__(self, count: int) -> None:
        super().__init__("evaluator output did not supply the exact dimension contract")
        self.count = count


def _git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def validate_source_binding(
    *,
    repo_root: Path,
    manifest: Mapping[str, object],
    current_bytes: Mapping[str, bytes],
) -> list[str]:
    """Verify ancestry and committed blobs directly through Git."""
    errors: list[str] = []
    commit = manifest.get("corpus_source_commit")
    if not isinstance(commit, str) or not _HEX40_RE.fullmatch(commit):
        return ["source commit is unavailable"]
    ancestor = _git(repo_root, "merge-base", "--is-ancestor", commit, "HEAD", check=False)
    if ancestor.returncode != 0:
        errors.append("corpus source commit is not an ancestor of execution HEAD")
    for prefix in ("fixture", "framework", "evaluator", "thresholds"):
        path = manifest.get(f"{prefix}_path")
        expected_hash = manifest.get(f"{prefix}_sha256")
        if not isinstance(path, str) or not isinstance(expected_hash, str):
            errors.append(f"{prefix} binding fields are invalid")
            continue
        try:
            committed = _git(repo_root, "show", f"{commit}:{path}").stdout
        except subprocess.CalledProcessError:
            errors.append(f"{prefix} blob is absent from corpus source commit")
            continue
        current = current_bytes.get(prefix)
        if current is None:
            errors.append(f"current {prefix} bytes are absent")
            continue
        if committed != current:
            errors.append(f"current {prefix} bytes differ from committed source blob")
        if sha256_bytes(committed) != expected_hash:
            errors.append(f"{prefix} SHA-256 differs from manifest binding")
    return errors


class AttemptMarker:
    """Persistent exclusive marker.  It has intentionally no deletion API."""

    def __init__(self, path: Path, attempt_id: str) -> None:
        self.path = path
        self.attempt_id = attempt_id
        self.created = False
        self.consumed = False

    def create_exclusive(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = canonical_json_bytes({"attempt_id": self.attempt_id, "state": "started"})
        fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        self.created = True

    def consume(self, *, decision: str, report_hash: str | None) -> None:
        if not self.created or self.consumed or not self.path.exists():
            raise RuntimeError("attempt marker was not created")
        payload = canonical_json_bytes({
            "attempt_id": self.attempt_id,
            "decision": decision,
            "report_hash": report_hash,
            "state": "consumed",
        })
        fd = os.open(str(self.path), os.O_WRONLY | os.O_TRUNC)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        self.consumed = True


def _empty_evidence() -> dict[str, int]:
    return {key: 0 for key in sorted(EVIDENCE_FAILURE_FIELDS)}


def _aggregate(
    observations: Sequence[tuple[Scenario, ScenarioScore, ScenarioScore, bool]],
    evidence: Mapping[str, int],
) -> dict[str, object]:
    dim_counts = {name: 0 for name in DIMENSION_NAMES}
    group_counts = {group_id: 0 for group_id in EXPECTED_GROUP_IDS}
    form_counts = {form: 0 for form in VALID_LANGUAGE_FORMS}
    complete = interpretation = policy = integration = 0
    for scenario, first, second, _variance in observations:
        for score in (first, second):
            if score.complete:
                complete += 1
                group_counts[scenario.group_id] += 1
                form_counts[scenario.language_form] += 1
            for name, passed in score.dimensions.items():
                if passed:
                    dim_counts[name] += 1
            interpretation += int(score.interpretation_failure)
            policy += int(score.policy_failure)
            integration += int(score.integration_failure)
    return {
        "complete_count": complete,
        "total_samples": len(observations) * REPEATS_PER_SCENARIO,
        "dimension_counts": dim_counts,
        "group_counts": group_counts,
        "language_form_counts": form_counts,
        "interpretation_failures": interpretation,
        "policy_failures": policy,
        "integration_failures": integration,
        "evidence_failures": dict(evidence),
    }


def build_product_gate_counters(
    report: Mapping[str, object], thresholds: Mapping[str, object]
) -> dict[str, int]:
    failures: dict[str, int] = {}
    complete = int(report["complete_count"])
    dimension_counts = report["dimension_counts"]
    group_counts = report["group_counts"]
    form_counts = report["language_form_counts"]
    assert isinstance(dimension_counts, dict)
    assert isinstance(group_counts, dict)
    assert isinstance(form_counts, dict)
    if complete < int(thresholds["complete_min"]):
        failures["complete"] = int(thresholds["complete_min"]) - complete
    safety = int(dimension_counts["safety"])
    if safety != int(thresholds["safety_exact"]):
        failures["safety"] = abs(int(thresholds["safety_exact"]) - safety)
    for name in NON_SAFETY_DIMENSIONS:
        count = int(dimension_counts[name])
        if count < int(thresholds["dimension_min"]):
            failures[f"dimension:{name}"] = int(thresholds["dimension_min"]) - count
    interpretation = int(report["interpretation_failures"])
    if interpretation > int(thresholds["interpretation_failures_max"]):
        failures["interpretation_failures"] = interpretation - int(thresholds["interpretation_failures_max"])
    for key in ("policy_failures", "integration_failures"):
        expected = int(thresholds[f"{key}_exact"])
        actual = int(report[key])
        if actual != expected:
            failures[key] = abs(actual - expected)
    for group_id in EXPECTED_GROUP_IDS:
        count = int(group_counts[group_id])
        if count < int(thresholds["group_complete_min"]):
            failures[f"group:{group_id}"] = int(thresholds["group_complete_min"]) - count
    for form in VALID_LANGUAGE_FORMS:
        count = int(form_counts[form])
        if count < int(thresholds["language_form_complete_min"]):
            failures[f"language_form:{form}"] = int(thresholds["language_form_complete_min"]) - count
    return failures


def _contains_forbidden_report_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            (isinstance(key, str) and key.lower() in _FORBIDDEN_REPORT_KEYS)
            or _contains_forbidden_report_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_report_key(child) for child in value)
    return False


def _finalize_report(
    *, attempt_id: str, aggregate: Mapping[str, object], thresholds: Mapping[str, object]
) -> dict[str, object]:
    evidence = dict(aggregate["evidence_failures"])  # type: ignore[arg-type]
    if aggregate["total_samples"] != TOTAL_SAMPLES:
        evidence["validation_errors"] += 1
    product = build_product_gate_counters(aggregate, thresholds)
    decision = classify_certification(
        evidence_failures=evidence, product_gate_failures=product
    )
    report: dict[str, object] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "attempt_id": attempt_id,
        "decision": decision,
        "complete_count": aggregate["complete_count"],
        "total_samples": aggregate["total_samples"],
        "dimension_counts": aggregate["dimension_counts"],
        "group_counts": aggregate["group_counts"],
        "language_form_counts": aggregate["language_form_counts"],
        "interpretation_failures": aggregate["interpretation_failures"],
        "policy_failures": aggregate["policy_failures"],
        "integration_failures": aggregate["integration_failures"],
        "evidence_failures": evidence,
        "product_gate_failures": product,
        "report_hash": "",
    }
    if _contains_forbidden_report_key(report):
        evidence["case_artifacts"] += 1
        report["decision"] = CERTIFICATION_INVALID
    report["report_hash"] = deterministic_hash({key: value for key, value in report.items() if key != "report_hash"})
    return report


def validate_report_schema(report: Mapping[str, object]) -> list[str]:
    errors = _unknown(report, REPORT_FIELDS, "report")
    if report.get("schema_version") != REPORT_SCHEMA_VERSION:
        errors.append("report.schema_version mismatch")
    if report.get("decision") not in (CERTIFICATION_INVALID, CERTIFICATION_FAIL, CERTIFICATION_PASS):
        errors.append("report.decision is invalid")
    attempt = report.get("attempt_id")
    if not isinstance(attempt, str) or not _SAFE_ATTEMPT_RE.fullmatch(attempt):
        errors.append("report.attempt_id is invalid")
    for key in ("complete_count", "total_samples", "interpretation_failures", "policy_failures", "integration_failures"):
        if not _strict_int(report.get(key)) or int(report[key]) < 0:
            errors.append(f"report.{key} must be a non-negative int")
    exact_maps = (
        ("dimension_counts", frozenset(DIMENSION_NAMES)),
        ("group_counts", frozenset(EXPECTED_GROUP_IDS)),
        ("language_form_counts", frozenset(VALID_LANGUAGE_FORMS)),
        ("evidence_failures", EVIDENCE_FAILURE_FIELDS),
    )
    for key, expected_keys in exact_maps:
        value = report.get(key)
        if not isinstance(value, dict) or set(value) != set(expected_keys):
            errors.append(f"report.{key} keys mismatch")
        elif any(not _strict_int(item) or item < 0 for item in value.values()):
            errors.append(f"report.{key} values must be non-negative ints")
    product = report.get("product_gate_failures")
    if not isinstance(product, dict) or any(
        not isinstance(key, str) or not key or not _strict_int(value) or value <= 0
        for key, value in product.items()
    ):
        errors.append("report.product_gate_failures is invalid")
    digest = report.get("report_hash")
    if not isinstance(digest, str) or not _HEX64_RE.fullmatch(digest):
        errors.append("report.report_hash must be lowercase 64-hex")
    else:
        expected = deterministic_hash({key: value for key, value in report.items() if key != "report_hash"})
        if digest != expected:
            errors.append("report.report_hash mismatch")
    if _contains_forbidden_report_key(report):
        errors.append("report contains a case-level or oracle key")
    return errors


def certify(report: Mapping[str, object]) -> str:
    """Reclassify only a complete, valid aggregate report."""
    errors = validate_report_schema(report)
    if errors:
        return CERTIFICATION_INVALID
    evidence = report["evidence_failures"]
    product = report["product_gate_failures"]
    assert isinstance(evidence, dict)
    assert isinstance(product, dict)
    return classify_certification(evidence_failures=evidence, product_gate_failures=product)


def _write_exclusive_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)


def run_one_shot(
    *,
    repo_root: Path,
    fixture_path: Path,
    manifest_path: Path,
    seal_path: Path,
    thresholds_path: Path,
    framework_path: Path,
    evaluator_path: Path,
    marker_path: Path,
    report_path: Path,
    expected_attempt_id: str,
    evaluator: Callable[[ScenarioInput], ScenarioOutput],
) -> RunResult:
    """Execute the complete sole-attempt lifecycle with invalidity precedence."""
    marker = AttemptMarker(marker_path, expected_attempt_id)
    try:
        marker.create_exclusive()
    except FileExistsError:
        return RunResult(CERTIFICATION_INVALID, None, False)

    evidence = _empty_evidence()
    observations: list[tuple[Scenario, ScenarioScore, ScenarioScore, bool]] = []
    thresholds: Mapping[str, object] = dict(FROZEN_THRESHOLDS)
    report: dict[str, object] | None = None
    decision = CERTIFICATION_INVALID
    try:
        try:
            fixture_bytes, fixture = _load_json_bytes(fixture_path)
            manifest_bytes, manifest = _load_json_bytes(manifest_path)
            _seal_bytes, seal = _load_json_bytes(seal_path)
            threshold_bytes, thresholds = _load_json_bytes(thresholds_path)
            framework_bytes = framework_path.read_bytes()
            evaluator_bytes = evaluator_path.read_bytes()
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            evidence["validation_errors"] += 1
            fixture = manifest = seal = {}
            fixture_bytes = threshold_bytes = framework_bytes = evaluator_bytes = manifest_bytes = b""

        validation_errors: list[str] = []
        validation_errors.extend(validate_fixture_schema(fixture))
        validation_errors.extend(validate_fixed_shape(fixture))
        validation_errors.extend(validate_manifest_schema(manifest))
        validation_errors.extend(validate_seal_schema(seal))
        validation_errors.extend(validate_threshold_schema(thresholds))
        if seal.get("attempt_id") != expected_attempt_id:
            validation_errors.append("seal attempt ID mismatch")
        if seal.get("manifest_sha256") != sha256_bytes(manifest_bytes):
            validation_errors.append("seal manifest binding mismatch")
        expected_paths = {
            "fixture_path": fixture_path.resolve().relative_to(repo_root.resolve()).as_posix(),
            "framework_path": framework_path.resolve().relative_to(repo_root.resolve()).as_posix(),
            "evaluator_path": evaluator_path.resolve().relative_to(repo_root.resolve()).as_posix(),
            "thresholds_path": thresholds_path.resolve().relative_to(repo_root.resolve()).as_posix(),
        }
        for key, expected_path in expected_paths.items():
            if manifest.get(key) != expected_path:
                validation_errors.append(f"manifest {key} mismatch")
        callable_source = inspect.getsourcefile(evaluator)
        if callable_source is None or Path(callable_source).resolve() != evaluator_path.resolve():
            validation_errors.append("evaluator callable source mismatch")
        validation_errors.extend(validate_source_binding(
            repo_root=repo_root,
            manifest=manifest,
            current_bytes={
                "fixture": fixture_bytes,
                "framework": framework_bytes,
                "evaluator": evaluator_bytes,
                "thresholds": threshold_bytes,
            },
        ))
        evidence["validation_errors"] += len(validation_errors)

        if evidence["validation_errors"] == 0:
            for scenario in convert_fixture_to_scenarios(fixture):
                try:
                    first, second, variance = evaluate_scenario(evaluator, scenario)
                except MissingDimensionsError as exc:
                    evidence["missing_dimensions"] += exc.count
                    break
                except Exception:
                    evidence["runtime_exceptions"] += 1
                    break
                observations.append((scenario, first, second, variance))
                evidence["repeat_variance"] += int(variance)

        aggregate = _aggregate(observations, evidence)
        report = _finalize_report(
            attempt_id=expected_attempt_id, aggregate=aggregate, thresholds=thresholds
        )
        report_errors = validate_report_schema(report)
        if report_errors:
            report_evidence = report["evidence_failures"]
            assert isinstance(report_evidence, dict)
            report_evidence["validation_errors"] += len(report_errors)
            report["decision"] = CERTIFICATION_INVALID
            report["report_hash"] = deterministic_hash({key: value for key, value in report.items() if key != "report_hash"})
        decision = certify(report)
        if decision != report["decision"]:
            report["decision"] = CERTIFICATION_INVALID
            report_evidence = report["evidence_failures"]
            assert isinstance(report_evidence, dict)
            report_evidence["validation_errors"] += 1
            report["report_hash"] = deterministic_hash({key: value for key, value in report.items() if key != "report_hash"})
            decision = CERTIFICATION_INVALID
        try:
            _write_exclusive_json(report_path, report)
        except OSError:
            report_evidence = report["evidence_failures"]
            assert isinstance(report_evidence, dict)
            report_evidence["validation_errors"] += 1
            report["decision"] = CERTIFICATION_INVALID
            report["report_hash"] = deterministic_hash({
                key: value for key, value in report.items() if key != "report_hash"
            })
            decision = CERTIFICATION_INVALID
    except Exception:
        evidence["runtime_exceptions"] += 1
        aggregate = _aggregate(observations, evidence)
        report = _finalize_report(
            attempt_id=expected_attempt_id,
            aggregate=aggregate,
            thresholds=dict(FROZEN_THRESHOLDS),
        )
        decision = CERTIFICATION_INVALID
    finally:
        marker.consume(
            decision=decision,
            report_hash=None if report is None else str(report.get("report_hash")),
        )
    return RunResult(decision, report, True)


__all__ = [
    "AttemptMarker", "DIMENSION_NAMES", "EXPECTED_GROUP_IDS", "FROZEN_THRESHOLDS",
    "GROUPS_PER_ACTION", "MANIFEST_SCHEMA_VERSION", "MULTI_TURN_PER_GROUP",
    "REPEATS_PER_SCENARIO", "REPORT_SCHEMA_VERSION", "RunResult",
    "SCENARIOS_PER_FORM", "SCENARIOS_PER_GROUP", "SEAL_SCHEMA_VERSION",
    "Scenario", "ScenarioExpected", "ScenarioInput", "ScenarioOutput", "ScenarioScore",
    "THRESHOLD_SCHEMA_VERSION", "TOTAL_COVERAGE_CELLS", "TOTAL_GROUPS",
    "TOTAL_MULTI_TURN", "TOTAL_ONE_TURN", "TOTAL_SAMPLES", "TOTAL_SCENARIOS",
    "VALID_ACTIONS", "VALID_LANGUAGE_FORMS", "build_product_gate_counters",
    "canonical_json_bytes", "certify", "convert_fixture_to_scenarios",
    "deterministic_hash", "evaluate_scenario", "run_one_shot", "sha256_bytes",
    "validate_fixture_schema", "validate_fixed_shape", "validate_manifest_schema",
    "validate_report_schema", "validate_seal_schema", "validate_source_binding",
    "validate_threshold_schema",
]
