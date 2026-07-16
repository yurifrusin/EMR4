"""LC4V8 content-blind certification framework.

Standalone, product-runtime-isolated module providing fail-closed
schema validators, fixed-shape validation, deterministic hashing,
immutable source verification, exclusive attempt consumption, evaluator
boundary, aggregation, product-gate counter construction, and final
certification decision via the generic decision taxonomy.

This module contains no V8 corpus content, receptionist utterances,
expected contracts, or protected V1-V7 evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)

# ---------------------------------------------------------------------------
# Constants — exact fixed shape
# ---------------------------------------------------------------------------

TOTAL_GROUPS = 24
TOTAL_SCENARIOS = 288
TOTAL_ACTIONS = 6
GROUPS_PER_ACTION = 4
TOTAL_LANGUAGE_FORMS = 6
SCENARIOS_PER_GROUP = 12
SCENARIOS_PER_FORM = 48
MULTI_TURN_PER_GROUP = 3
ONE_TURN_PER_GROUP = 9
TOTAL_MULTI_TURN = 72
TOTAL_ONE_TURN = 216
TOTAL_COVERAGE_CELLS = 288
REPEATS_PER_SCENARIO = 2
TOTAL_SAMPLES = 576

DIMENSION_NAMES: tuple[str, ...] = (
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

VALID_ACTIONS: frozenset[str] = frozenset({
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
})

VALID_LANGUAGE_FORMS: frozenset[str] = frozenset({
    "plain",
    "paraphrase",
    "speech_like",
    "word_order",
    "correction",
    "interval",
})

# Schema field allowlists for unknown-field rejection
FIXTURE_SCHEMA_FIELDS: frozenset[str] = frozenset({
    "groups",
    "total_groups",
    "total_scenarios",
})
MANIFEST_SCHEMA_FIELDS: frozenset[str] = frozenset({
    "fixture_blob_hash",
    "framework_blob_hash",
    "corpus_source_commit",
})
SEAL_SCHEMA_FIELDS: frozenset[str] = frozenset({
    "manifest_hash",
    "attempt_id",
    "state",
})
THRESHOLD_SCHEMA_FIELDS: frozenset[str] = frozenset({
    "complete_min",
    "safety_exact",
    "dimension_min",
    "interpretation_failures_max",
    "policy_failures_exact",
    "integration_failures_exact",
    "group_complete_min",
    "language_form_complete_min",
})
REPORT_SCHEMA_FIELDS: frozenset[str] = frozenset({
    "complete_count",
    "total_samples",
    "dimension_counts",
    "group_counts",
    "language_form_counts",
    "interpretation_failures",
    "policy_failures",
    "integration_failures",
    "repeat_variance",
    "report_hash",
})

# ---------------------------------------------------------------------------
# SHA-256 helpers — deterministic compact sorted UTF-8
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    """Return lowercase hex SHA-256 of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Return lowercase hex SHA-256 of UTF-8-encoded *text*."""
    return sha256_bytes(text.encode("utf-8"))


def deterministic_hash(obj: object) -> str:
    """Return SHA-256 of compact sorted UTF-8 JSON representation."""
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(raw)


# ---------------------------------------------------------------------------
# Schema validators — fail closed with unknown-field rejection
# ---------------------------------------------------------------------------

_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")


def _check_unknown_fields(
    obj: Mapping[str, object],
    allowed: frozenset[str],
    label: str,
) -> list[str]:
    errors: list[str] = []
    unknown = set(obj.keys()) - allowed
    if unknown:
        errors.append(f"{label}: unknown field(s) {sorted(unknown)}")
    return errors


def _check_type(
    obj: Mapping[str, object],
    field_name: str,
    expected: type,
    label: str,
) -> list[str]:
    errors: list[str] = []
    if field_name not in obj:
        errors.append(f"{label}: missing required field {field_name!r}")
        return errors
    val = obj[field_name]
    # Boolean is never an integer count
    if expected is int and isinstance(val, bool):
        errors.append(f"{label}.{field_name}: must be int, got bool")
        return errors
    if not isinstance(val, expected):
        errors.append(
            f"{label}.{field_name}: expected {expected.__name__}, "
            f"got {type(val).__name__}"
        )
    return errors


# -- Fixture ----------------------------------------------------------------


def validate_fixture_schema(fixture: Mapping[str, object]) -> list[str]:
    """Validate fixture schema. Return list of errors (empty = valid)."""
    errors: list[str] = []
    errors.extend(_check_unknown_fields(fixture, FIXTURE_SCHEMA_FIELDS, "fixture"))
    errors.extend(_check_type(fixture, "total_groups", int, "fixture"))
    errors.extend(_check_type(fixture, "total_scenarios", int, "fixture"))
    errors.extend(_check_type(fixture, "groups", dict, "fixture"))

    if "groups" in fixture and isinstance(fixture["groups"], dict):
        groups: dict[str, object] = fixture["groups"]  # type: ignore[assignment]
        if len(groups) != TOTAL_GROUPS:
            errors.append(
                f"fixture: expected {TOTAL_GROUPS} groups, got {len(groups)}"
            )
        for gid, group_val in groups.items():
            if not isinstance(group_val, dict):
                errors.append(f"fixture.groups[{gid!r}]: expected dict")
                continue
            group: dict[str, object] = group_val
            # Check required group fields exist (but don't recurse into
            # scenario structure — that is validated by validate_fixed_shape)
            for gf in ("action", "scenarios", "language_forms"):
                if gf not in group:
                    errors.append(f"fixture.groups[{gid!r}]: missing {gf!r}")
            if "action" in group and group["action"] not in VALID_ACTIONS:
                errors.append(
                    f"fixture.groups[{gid!r}].action: invalid {group['action']!r}"
                )
            if "scenarios" in group and isinstance(group["scenarios"], dict):
                scens: dict[str, object] = group["scenarios"]  # type: ignore[assignment]
                if len(scens) != SCENARIOS_PER_GROUP:
                    errors.append(
                        f"fixture.groups[{gid!r}]: expected {SCENARIOS_PER_GROUP} "
                        f"scenarios, got {len(scens)}"
                    )
    # Top-level count checks
    tg = fixture.get("total_groups")
    if isinstance(tg, int) and not isinstance(tg, bool) and tg != TOTAL_GROUPS:
        errors.append(f"fixture.total_groups: expected {TOTAL_GROUPS}, got {tg}")
    ts = fixture.get("total_scenarios")
    if isinstance(ts, int) and not isinstance(ts, bool) and ts != TOTAL_SCENARIOS:
        errors.append(f"fixture.total_scenarios: expected {TOTAL_SCENARIOS}, got {ts}")

    return errors


# -- Manifest ----------------------------------------------------------------


def validate_manifest_schema(manifest: Mapping[str, object]) -> list[str]:
    """Validate manifest schema."""
    errors: list[str] = []
    errors.extend(_check_unknown_fields(manifest, MANIFEST_SCHEMA_FIELDS, "manifest"))
    for fld in ("fixture_blob_hash", "framework_blob_hash", "corpus_source_commit"):
        errors.extend(_check_type(manifest, fld, str, "manifest"))
    return errors


# -- Seal -------------------------------------------------------------------


def validate_seal_schema(seal: Mapping[str, object]) -> list[str]:
    """Validate seal schema."""
    errors: list[str] = []
    errors.extend(_check_unknown_fields(seal, SEAL_SCHEMA_FIELDS, "seal"))
    errors.extend(_check_type(seal, "manifest_hash", str, "seal"))
    errors.extend(_check_type(seal, "attempt_id", str, "seal"))
    errors.extend(_check_type(seal, "state", str, "seal"))
    if "state" in seal and seal["state"] not in ("unconsumed", "consumed"):
        errors.append(
            f"seal.state: expected 'unconsumed' or 'consumed', "
            f"got {seal['state']!r}"
        )
    return errors


# -- Thresholds --------------------------------------------------------------


def validate_threshold_schema(threshold: Mapping[str, object]) -> list[str]:
    """Validate threshold schema."""
    errors: list[str] = []
    errors.extend(
        _check_unknown_fields(threshold, THRESHOLD_SCHEMA_FIELDS, "threshold")
    )
    for fld in (
        "complete_min",
        "safety_exact",
        "dimension_min",
        "interpretation_failures_max",
        "policy_failures_exact",
        "integration_failures_exact",
        "group_complete_min",
        "language_form_complete_min",
    ):
        errors.extend(_check_type(threshold, fld, int, "threshold"))
    return errors


# -- Aggregate report --------------------------------------------------------


def validate_report_schema(report: Mapping[str, object]) -> list[str]:
    """Validate aggregate report schema."""
    errors: list[str] = []
    errors.extend(_check_unknown_fields(report, REPORT_SCHEMA_FIELDS, "report"))
    for fld in (
        "complete_count",
        "total_samples",
        "interpretation_failures",
        "policy_failures",
        "integration_failures",
        "repeat_variance",
    ):
        errors.extend(_check_type(report, fld, int, "report"))
    for fld in ("dimension_counts", "group_counts", "language_form_counts"):
        errors.extend(_check_type(report, fld, dict, "report"))
    errors.extend(_check_type(report, "report_hash", str, "report"))
    return errors


# ---------------------------------------------------------------------------
# Fixed-shape validation
# ---------------------------------------------------------------------------


def validate_fixed_shape(fixture: Mapping[str, object]) -> list[str]:
    """Validate the exact fixed shape of a fixture (counts / distribution)."""
    errors: list[str] = []
    groups_raw = fixture.get("groups")
    if not isinstance(groups_raw, dict):
        errors.append("fixture.groups: expected dict")
        return errors
    groups: dict[str, object] = groups_raw

    if len(groups) != TOTAL_GROUPS:
        errors.append(f"expected {TOTAL_GROUPS} groups, got {len(groups)}")

    action_counts: dict[str, int] = {a: 0 for a in VALID_ACTIONS}
    form_counts: dict[str, int] = {f: 0 for f in VALID_LANGUAGE_FORMS}
    coverage_cells: set[str] = set()
    total_scens = 0
    total_mt = 0
    total_ot = 0

    for gid, group_val in groups.items():
        if not isinstance(group_val, dict):
            errors.append(f"group {gid!r}: not a dict")
            continue
        group: dict[str, object] = group_val

        action = group.get("action")
        if action in VALID_ACTIONS:
            action_counts[action] += 1

        forms_list = group.get("language_forms")
        if isinstance(forms_list, list):
            for lf in forms_list:
                if lf in VALID_LANGUAGE_FORMS:
                    form_counts[lf] += 2  # 2 scenarios per form per group

        scens_raw = group.get("scenarios")
        if not isinstance(scens_raw, dict):
            errors.append(f"group {gid!r}: scenarios not a dict")
            continue
        scens: dict[str, object] = scens_raw

        for sid, scen_val in scens.items():
            total_scens += 1
            coverage_cells.add(sid)
            if isinstance(scen_val, dict):
                scen: dict[str, object] = scen_val
                mt = scen.get("multi_turn", False)
                if isinstance(mt, bool) and mt:
                    total_mt += 1
                else:
                    total_ot += 1

    # Action distribution
    for action, count in action_counts.items():
        if count != GROUPS_PER_ACTION:
            errors.append(
                f"action {action!r}: expected {GROUPS_PER_ACTION} groups, "
                f"got {count}"
            )

    # Scenario totals
    if total_scens != TOTAL_SCENARIOS:
        errors.append(f"expected {TOTAL_SCENARIOS} scenarios, got {total_scens}")

    # Coverage cell uniqueness
    if len(coverage_cells) != TOTAL_COVERAGE_CELLS:
        errors.append(
            f"expected {TOTAL_COVERAGE_CELLS} unique coverage cells, "
            f"got {len(coverage_cells)}"
        )

    # Multi-turn / one-turn
    if total_mt != TOTAL_MULTI_TURN:
        errors.append(f"expected {TOTAL_MULTI_TURN} multi-turn, got {total_mt}")
    if total_ot != TOTAL_ONE_TURN:
        errors.append(f"expected {TOTAL_ONE_TURN} one-turn, got {total_ot}")

    # Language form distribution
    for form, count in form_counts.items():
        if count != SCENARIOS_PER_FORM:
            errors.append(
                f"language form {form!r}: expected {SCENARIOS_PER_FORM} scenarios, "
                f"got {count}"
            )

    return errors


# ---------------------------------------------------------------------------
# Domain data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScenarioInput:
    """Opaque scenario input passed to the evaluation callback.

    No expected contract, no scenario ID, no oracle content.
    """

    utterance: str
    diary_state: Mapping[str, object]


@dataclass(frozen=True)
class ScenarioExpected:
    """Expected contract.  Never passed to the evaluation callback."""

    intended_action: str = ""
    action_semantics: str = ""
    temporal_relation: str = ""
    normalized_values: str = ""
    entity_semantics: str = ""
    lossless_source_spans: str = ""
    extraction_clarification: str = ""
    policy_resolution: str = ""
    policy_clarification: str = ""
    clarification_composition: str = ""
    interpretation_tool: str = ""
    replay: str = ""
    safety: str = ""


@dataclass(frozen=True)
class Scenario:
    """Complete scenario with opaque input and hidden expected contract."""

    input: ScenarioInput
    expected: ScenarioExpected

    @property
    def scenario_id(self) -> str:
        """Deterministic opaque ID derived from input (not for callback)."""
        return deterministic_hash({
            "utterance": self.input.utterance,
            "expected": {
                "intended_action": self.expected.intended_action,
                "action_semantics": self.expected.action_semantics,
                "temporal_relation": self.expected.temporal_relation,
                "normalized_values": self.expected.normalized_values,
                "entity_semantics": self.expected.entity_semantics,
                "lossless_source_spans": self.expected.lossless_source_spans,
                "extraction_clarification": self.expected.extraction_clarification,
                "policy_resolution": self.expected.policy_resolution,
                "policy_clarification": self.expected.policy_clarification,
                "clarification_composition": self.expected.clarification_composition,
                "interpretation_tool": self.expected.interpretation_tool,
                "replay": self.expected.replay,
                "safety": self.expected.safety,
            },
        })


@dataclass(frozen=True)
class ScenarioOutput:
    """Product output from one evaluation callback invocation."""

    intended_action: str = ""
    action_semantics: str = ""
    temporal_relation: str = ""
    normalized_values: str = ""
    entity_semantics: str = ""
    lossless_source_spans: str = ""
    extraction_clarification: str = ""
    policy_resolution: str = ""
    policy_clarification: str = ""
    clarification_composition: str = ""
    interpretation_tool: str = ""
    replay: str = ""
    safety: str = ""


@dataclass(frozen=True)
class DimensionScore:
    """Score for a single dimension on one repeat."""

    passed: bool
    details: str = ""


@dataclass(frozen=True)
class ScenarioScore:
    """All dimension scores for one repeat of one scenario."""

    dimensions: Mapping[str, DimensionScore]

    @property
    def complete(self) -> bool:
        return all(d.passed for d in self.dimensions.values())

    def as_dict(self) -> dict[str, bool]:
        return {k: v.passed for k, v in self.dimensions.items()}


# ---------------------------------------------------------------------------
# Source binding — immutable source verification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceBindingObservation:
    """Injected Git / blob observations.

    Every field is validated independently — the framework never trusts a
    caller-supplied ``valid=True``.
    """

    source_commit: str
    is_ancestor: bool
    fixture_blob_hash: str
    framework_blob_hash: str
    current_fixture_bytes: bytes
    current_framework_bytes: bytes
    manifest: Mapping[str, object]
    manifest_hash: str
    seal: Mapping[str, object]
    seal_state: str


def validate_source_binding(obs: SourceBindingObservation) -> list[str]:
    """Validate every named observation field independently."""
    errors: list[str] = []

    # 1. source_commit is 40-char hex
    if not _HEX40_RE.match(obs.source_commit):
        errors.append(
            f"source_commit: expected 40-char hex, got {obs.source_commit!r}"
        )

    # 2. is_ancestor is a bool and is True
    if not isinstance(obs.is_ancestor, bool):
        errors.append(
            f"is_ancestor: expected bool, got {type(obs.is_ancestor).__name__}"
        )
    elif not obs.is_ancestor:
        errors.append("is_ancestor: must be True")

    # 3. fixture blob hash matches actual bytes
    actual_fh = sha256_bytes(obs.current_fixture_bytes)
    if actual_fh != obs.fixture_blob_hash:
        errors.append(
            f"fixture_blob_hash mismatch: expected {obs.fixture_blob_hash}, "
            f"computed {actual_fh}"
        )

    # 4. framework blob hash matches actual bytes
    actual_fwh = sha256_bytes(obs.current_framework_bytes)
    if actual_fwh != obs.framework_blob_hash:
        errors.append(
            f"framework_blob_hash mismatch: expected {obs.framework_blob_hash}, "
            f"computed {actual_fwh}"
        )

    # 5. manifest hash matches deterministic hash of manifest content
    computed_mh = deterministic_hash(obs.manifest)
    if computed_mh != obs.manifest_hash:
        errors.append(
            f"manifest_hash mismatch: expected {obs.manifest_hash}, "
            f"computed {computed_mh}"
        )

    # 6. seal binds the correct manifest_hash
    seal_mh = obs.seal.get("manifest_hash")
    if seal_mh != obs.manifest_hash:
        errors.append(
            f"seal.manifest_hash {seal_mh!r} != manifest_hash {obs.manifest_hash!r}"
        )

    # 7. seal state is unconsumed
    if not isinstance(obs.seal_state, str):
        errors.append(
            f"seal_state: expected str, got {type(obs.seal_state).__name__}"
        )
    elif obs.seal_state != "unconsumed":
        errors.append(f"seal_state: expected 'unconsumed', got {obs.seal_state!r}")

    # 8. manifest corpus_source_commit matches source_commit
    manifest_commit = obs.manifest.get("corpus_source_commit")
    if manifest_commit != obs.source_commit:
        errors.append(
            f"manifest.corpus_source_commit {manifest_commit!r} != "
            f"source_commit {obs.source_commit!r}"
        )

    # 9. manifest blob hashes match observation
    m_fb = obs.manifest.get("fixture_blob_hash")
    if m_fb != obs.fixture_blob_hash:
        errors.append(
            f"manifest.fixture_blob_hash {m_fb!r} != "
            f"fixture_blob_hash {obs.fixture_blob_hash!r}"
        )
    m_fwb = obs.manifest.get("framework_blob_hash")
    if m_fwb != obs.framework_blob_hash:
        errors.append(
            f"manifest.framework_blob_hash {m_fwb!r} != "
            f"framework_blob_hash {obs.framework_blob_hash!r}"
        )

    return errors


# ---------------------------------------------------------------------------
# Attempt marker — exclusive consumption via O_EXCL
# ---------------------------------------------------------------------------


class AttemptMarker:
    """Exclusive attempt marker with O_EXCL creation semantics.

    Usage::

        marker = AttemptMarker(path)
        marker.create_exclusive()   # raises FileExistsError if present
        try:
            ...  # run evaluation
        finally:
            marker.consume()        # every exit path
    """

    def __init__(self, marker_path: str | Path) -> None:
        self._marker_path = Path(marker_path)
        self._consumed = False

    def create_exclusive(self) -> None:
        """Create the marker file atomically.

        Raises *FileExistsError* if the marker already exists (protecting
        against a second attempt before the evaluator runs).
        """
        self._marker_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self._marker_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)

    def consume(self) -> None:
        """Mark the attempt as consumed."""
        self._consumed = True

    @property
    def is_consumed(self) -> bool:
        return self._consumed

    def cleanup(self) -> None:
        """Remove the marker file if present."""
        if self._marker_path.exists():
            self._marker_path.unlink()


# ---------------------------------------------------------------------------
# Evaluator boundary
# ---------------------------------------------------------------------------


def _score_output(
    output: ScenarioOutput, expected: ScenarioExpected
) -> dict[str, DimensionScore]:
    """Compare product output against the expected contract."""
    scores: dict[str, DimensionScore] = {}
    for dim in DIMENSION_NAMES:
        actual = getattr(output, dim)
        want = getattr(expected, dim)
        passed = actual == want
        details = "" if passed else f"expected {want!r}, got {actual!r}"
        scores[dim] = DimensionScore(passed=passed, details=details)
    return scores


def evaluate_scenario(
    callback: Callable[[ScenarioInput], ScenarioOutput],
    scenario: Scenario,
) -> tuple[ScenarioScore, ScenarioScore]:
    """Evaluate one scenario with two repeats.

    The *callback* receives **only** ``scenario.input`` — never the expected
    contract or scenario ID.  Both repeats are scored against the expected
    contract *after* the callback returns.
    """
    output1 = callback(scenario.input)
    output2 = callback(scenario.input)

    score1 = ScenarioScore(dimensions=_score_output(output1, scenario.expected))
    score2 = ScenarioScore(dimensions=_score_output(output2, scenario.expected))
    return score1, score2


# ---------------------------------------------------------------------------
# Fixture conversion helper
# ---------------------------------------------------------------------------


def convert_fixture_to_scenarios(
    fixture: Mapping[str, object],
) -> list[Scenario]:
    """Convert a validated fixture dict into a list of ``Scenario`` objects."""
    scenarios: list[Scenario] = []
    groups_raw = fixture.get("groups")
    if not isinstance(groups_raw, dict):
        return scenarios
    groups: dict[str, object] = groups_raw

    for gid, group_val in groups.items():
        if not isinstance(group_val, dict):
            continue
        group: dict[str, object] = group_val
        scens_raw = group.get("scenarios")
        if not isinstance(scens_raw, dict):
            continue
        scens: dict[str, object] = scens_raw

        for sid, scen_val in scens.items():
            if not isinstance(scen_val, dict):
                continue
            scen: dict[str, object] = scen_val

            inp = ScenarioInput(
                utterance=str(scen.get("utterance", "")),
                diary_state=dict(scen.get("diary_state", {})),
            )
            exp_raw = scen.get("expected")
            if isinstance(exp_raw, dict):
                exp: dict[str, object] = exp_raw
                expected = ScenarioExpected(
                    intended_action=str(exp.get("intended_action", "")),
                    action_semantics=str(exp.get("action_semantics", "")),
                    temporal_relation=str(exp.get("temporal_relation", "")),
                    normalized_values=str(exp.get("normalized_values", "")),
                    entity_semantics=str(exp.get("entity_semantics", "")),
                    lossless_source_spans=str(
                        exp.get("lossless_source_spans", "")
                    ),
                    extraction_clarification=str(
                        exp.get("extraction_clarification", "")
                    ),
                    policy_resolution=str(exp.get("policy_resolution", "")),
                    policy_clarification=str(exp.get("policy_clarification", "")),
                    clarification_composition=str(
                        exp.get("clarification_composition", "")
                    ),
                    interpretation_tool=str(exp.get("interpretation_tool", "")),
                    replay=str(exp.get("replay", "")),
                    safety=str(exp.get("safety", "")),
                )
            else:
                expected = ScenarioExpected()
            scenarios.append(Scenario(input=inp, expected=expected))
    return scenarios


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _raw_scenario_id(scen: Mapping[str, object]) -> str:
    """Compute the deterministic hash for a raw scenario dict.

    Must match ``Scenario.scenario_id`` so that assignments extracted
    from a raw fixture can be looked up with ``scenario.scenario_id``.
    """
    exp_raw = scen.get("expected", {})
    exp = exp_raw if isinstance(exp_raw, dict) else {}
    return deterministic_hash({
        "utterance": str(scen.get("utterance", "")),
        "expected": {
            dim: str(exp.get(dim, ""))
            for dim in (
                "intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "lossless_source_spans",
                "extraction_clarification", "policy_resolution",
                "policy_clarification", "clarification_composition",
                "interpretation_tool", "replay", "safety",
            )
        },
    })


def _extract_assignments(
    fixture: Mapping[str, object],
) -> tuple[dict[str, str], dict[str, str]]:
    """Extract group and language-form assignments from fixture structure.

    Returns ``(group_assignments, form_assignments)`` dicts mapping each
    scenario's opaque ID to its group label and language-form label.
    """
    group_assignments: dict[str, str] = {}
    form_assignments: dict[str, str] = {}
    groups_raw = fixture.get("groups")
    if not isinstance(groups_raw, dict):
        return group_assignments, form_assignments
    groups: dict[str, object] = groups_raw

    for gid, group_val in groups.items():
        if not isinstance(group_val, dict):
            continue
        group: dict[str, object] = group_val
        forms_list: list[str] = []
        raw_forms = group.get("language_forms")
        if isinstance(raw_forms, list):
            forms_list = [f for f in raw_forms if isinstance(f, str)]

        scens_raw = group.get("scenarios")
        if not isinstance(scens_raw, dict):
            continue
        scens: dict[str, object] = scens_raw

        # Build a list of (scenario_dict, idx) pairs for deterministic ordering
        items = list(scens.items())
        for idx, (_sid, scen_val) in enumerate(items):
            if not isinstance(scen_val, dict):
                continue
            sid_hash = _raw_scenario_id(scen_val)
            group_assignments[sid_hash] = str(gid)
            # Each form appears twice per group; cycle through forms.
            if forms_list:
                fidx = (idx % len(forms_list))
                form_assignments[sid_hash] = forms_list[fidx]
            else:
                form_assignments[sid_hash] = list(VALID_LANGUAGE_FORMS)[
                    idx % TOTAL_LANGUAGE_FORMS
                ]

    return group_assignments, form_assignments


def aggregate_scores(
    scenario_scores: Sequence[tuple[Scenario, ScenarioScore, ScenarioScore]],
    fixture: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Aggregate scenario scores into an anonymous aggregate report.

    The returned dict contains **only** aggregate keys — no scenario IDs,
    utterances, expected values, per-case results, or oracle content.
    """
    total_samples = len(scenario_scores) * REPEATS_PER_SCENARIO
    complete_count = 0
    dim_counts: dict[str, int] = {d: 0 for d in DIMENSION_NAMES}
    repeat_variance = 0
    interpret_failures = 0
    policy_failures = 0
    integration_failures = 0

    group_complete: dict[str, int] = {}
    group_total: dict[str, int] = {}
    form_complete: dict[str, int] = {}
    form_total: dict[str, int] = {}

    # Resolve group/form assignments
    if fixture is not None:
        group_assignments, form_assignments = _extract_assignments(fixture)
    else:
        group_assignments, form_assignments = {}, {}

    for scenario, score1, score2 in scenario_scores:
        sid = scenario.scenario_id
        gid = group_assignments.get(sid, "unknown")
        fid = form_assignments.get(sid, "unknown")

        for score in (score1, score2):
            if score.complete:
                complete_count += 1
            for dim in DIMENSION_NAMES:
                if score.dimensions[dim].passed:
                    dim_counts[dim] += 1
            # Repeat variance detection
            if score is score2:
                for dim in DIMENSION_NAMES:
                    if (
                        score1.dimensions[dim].passed
                        != score2.dimensions[dim].passed
                    ):
                        repeat_variance += 1
                        break
            # Product failure tracking
            if not score.dimensions["interpretation_tool"].passed:
                interpret_failures += 1
            if not score.dimensions["policy_resolution"].passed:
                policy_failures += 1
            if not score.dimensions["replay"].passed:
                integration_failures += 1

        # Group / form counts
        for score in (score1, score2):
            group_total[gid] = group_total.get(gid, 0) + 1
            form_total[fid] = form_total.get(fid, 0) + 1
            if score.complete:
                group_complete[gid] = group_complete.get(gid, 0) + 1
                form_complete[fid] = form_complete.get(fid, 0) + 1

    # Build aggregate-only report dict
    report: dict[str, object] = {
        "complete_count": complete_count,
        "total_samples": total_samples,
        "dimension_counts": dict(sorted(dim_counts.items())),
        "group_counts": {
            k: group_complete.get(k, 0) for k in sorted(group_total)
        },
        "language_form_counts": {
            k: form_complete.get(k, 0) for k in sorted(form_total)
        },
        "interpretation_failures": interpret_failures,
        "policy_failures": policy_failures,
        "integration_failures": integration_failures,
        "repeat_variance": repeat_variance,
        "report_hash": "",
    }

    # Deterministic hash over everything except the hash field itself
    hash_input = {k: v for k, v in report.items() if k != "report_hash"}
    report["report_hash"] = deterministic_hash(hash_input)

    return report


# ---------------------------------------------------------------------------
# Product-gate counter construction
# ---------------------------------------------------------------------------


def build_product_gate_counters(
    report: Mapping[str, object],
    thresholds: Mapping[str, int],
) -> tuple[dict[str, int], dict[str, int]]:
    """Build evidence and product-gate failure counters.

    Returns ``(evidence_failures, product_gate_failures)`` for direct use
    with ``classify_certification``.

    Evidence defects (repeat variance, schema failures) go into
    *evidence_failures*.  Product misses (below-threshold dimensions,
    policy/integration failures) go into *product_gate_failures* — they
    must never make evidence invalid.
    """
    evidence_failures: dict[str, int] = {}
    product_failures: dict[str, int] = {}

    repeat_var = int(report.get("repeat_variance", 0))
    if repeat_var > 0:
        evidence_failures["repeat_variance"] = repeat_var

    complete = int(report.get("complete_count", 0))
    total = int(report.get("total_samples", 0))
    dim_counts: dict[str, int] = dict(
        report.get("dimension_counts", {})  # type: ignore[arg-type]
    )
    group_counts: dict[str, int] = dict(
        report.get("group_counts", {})  # type: ignore[arg-type]
    )
    form_counts: dict[str, int] = dict(
        report.get("language_form_counts", {})  # type: ignore[arg-type]
    )
    interpret_fails = int(report.get("interpretation_failures", 0))
    policy_fails = int(report.get("policy_failures", 0))
    integ_fails = int(report.get("integration_failures", 0))

    complete_min = int(thresholds.get("complete_min", 548))
    safety_exact = int(thresholds.get("safety_exact", 576))
    dimension_min = int(thresholds.get("dimension_min", 548))
    interpret_max = int(thresholds.get("interpretation_failures_max", 28))
    policy_exact = int(thresholds.get("policy_failures_exact", 0))
    integ_exact = int(thresholds.get("integration_failures_exact", 0))
    group_min = int(thresholds.get("group_complete_min", 22))
    form_min = int(thresholds.get("language_form_complete_min", 91))

    # -- Product gates (never invalid) --
    if complete < complete_min:
        product_failures["complete_below_threshold"] = complete_min - complete

    safety_val = dim_counts.get("safety", 0)
    if safety_val < safety_exact:
        product_failures["safety_below_exact"] = safety_exact - safety_val

    for dim in DIMENSION_NAMES:
        if dim == "safety":
            continue
        dv = dim_counts.get(dim, 0)
        if dv < dimension_min:
            product_failures[f"{dim}_below_threshold"] = dimension_min - dv

    if interpret_fails > interpret_max:
        product_failures["interpretation_failures_exceeded"] = (
            interpret_fails - interpret_max
        )
    if policy_fails != policy_exact:
        product_failures["policy_failures_mismatch"] = policy_fails - policy_exact
    if integ_fails != integ_exact:
        product_failures["integration_failures_mismatch"] = (
            integ_fails - integ_exact
        )

    for gid, count in group_counts.items():
        if count < group_min:
            product_failures[f"group_{gid}_below_threshold"] = group_min - count

    for fid, count in form_counts.items():
        if count < form_min:
            product_failures[f"form_{fid}_below_threshold"] = form_min - count

    return evidence_failures, product_failures


# ---------------------------------------------------------------------------
# Certification decision
# ---------------------------------------------------------------------------


def certify(
    report: Mapping[str, object],
    thresholds: Mapping[str, int],
) -> str:
    """Return the certification decision via the generic taxonomy.

    Delegates to :func:`classify_certification` with evidence and
    product-gate failure counters built from *report* and *thresholds*.
    """
    evidence_failures, product_failures = build_product_gate_counters(
        report, thresholds
    )
    return classify_certification(
        evidence_failures=evidence_failures,
        product_gate_failures=product_failures,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "AttemptMarker",
    "DimensionScore",
    "Scenario",
    "ScenarioExpected",
    "ScenarioInput",
    "ScenarioOutput",
    "ScenarioScore",
    "SourceBindingObservation",
    "aggregate_scores",
    "build_product_gate_counters",
    "certify",
    "convert_fixture_to_scenarios",
    "deterministic_hash",
    "evaluate_scenario",
    "sha256_bytes",
    "sha256_text",
    "validate_fixture_schema",
    "validate_fixed_shape",
    "validate_manifest_schema",
    "validate_report_schema",
    "validate_seal_schema",
    "validate_source_binding",
    "validate_threshold_schema",
    # Exported constants
    "DIMENSION_NAMES",
    "GROUPS_PER_ACTION",
    "MULTI_TURN_PER_GROUP",
    "ONE_TURN_PER_GROUP",
    "REPEATS_PER_SCENARIO",
    "SCENARIOS_PER_FORM",
    "SCENARIOS_PER_GROUP",
    "TOTAL_ACTIONS",
    "TOTAL_COVERAGE_CELLS",
    "TOTAL_GROUPS",
    "TOTAL_LANGUAGE_FORMS",
    "TOTAL_MULTI_TURN",
    "TOTAL_ONE_TURN",
    "TOTAL_SAMPLES",
    "TOTAL_SCENARIOS",
    "VALID_ACTIONS",
    "VALID_LANGUAGE_FORMS",
]
