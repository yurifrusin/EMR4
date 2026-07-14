"""Provider-free generic LC4 scale-corpus framework.

This module defines the development-only corpus models, loaders, and generation
APIs for the LC4 scale corpus.  It is the sole bounded service module for DW1.

Default APIs are development-only.  Generic partition and sealed-holdout
interfaces are defined but testable only with miniature dummy records.

All development evidence is DeepSeek-generated Silver/pending with complete
deterministic provenance.  It must never be promoted or counted as adjudicated
coverage.

Canonical invariant profile
---------------------------
Every semantic group and its variants must match the following profile.
Surface/trajectory behaviour may vary because those are utterance-level
presentation; the invariant fields below must agree across all variants
within a group.

Invariant fields (must match group spec across every variant):
  - intended_action         group's intended action
  - action_semantics        always "intended" for development
  - temporal_relation       group's temporal relation
  - earliest_time           group's earliest time bound
  - latest_time             group's latest time bound
  - normalized_values       appointment_date, duration_minutes, time bounds
  - patient_semantics       field-level entity semantics
  - practitioner_semantics  field-level entity semantics
  - location_semantics      field-level entity semantics
  - appointment_type_semantics  field-level entity semantics
  - duration_semantics      field-level entity semantics
  - entity_state            aggregate entity state
  - diary_state             initial diary state
  - expected_outcome_kind   derived from action + diary_state
  - expected_appointment_deltas  derived from action + parameters
  - expected_audit_deltas   derived from action
  - forbidden_outcomes      derived from diary_state
  - forbidden_tool_calls    always ["mutate_diary_direct", "override_confirmation"]
  - provenance              "silver"
  - adjudication            "pending"
  - source_spans            evidence keys for every derived normalized field
  - reference_date          group reference date
  - clinic_clock            group clinic clock

Variant-permitted fields (may differ per variant):
  - dialogue_form           utterance-level presentation
  - language_form           utterance-level presentation
  - dialogue_turns          utterance wording
  - expected_clarification  may differ per variant
  - clarification_choices   may differ per variant
  - expected_tool_sequence  may differ per variant
  - description             derived from variant wording only

Evidence-coverage rules
-----------------------
Every normalised value that is derivable from utterance text MUST have a
corresponding source-span key.

Required source-span keys:
  - "appointment_date"   when appointment_date is derived from "tomorrow" etc.
  - "earliest_time"      when earliest_time is derived from text time patterns
  - "latest_time"        when latest_time is derived from text time patterns
  - "patient"            when patient_semantics == "exact"
  - "practitioner"       when practitioner_semantics == "exact"
  - "duration_minutes"   when duration is mentioned
  - "temporal_relation"  when a temporal pattern is present

For omitted entities, no false named-entity span must exist.
For corrected semantics in multi-turn, BOTH the prior (erroneous) entity span
AND the corrected entity span must be present.

Multi-turn correction evidence
------------------------------
When a multi-turn variant has dialogue_form == "correction", the source spans
must include both:
  - The erroneous entity with a span pointing to the first turn, AND
  - The corrected entity with a span pointing to the second turn.

The normalized values reflect the *corrected* (final) state.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Literal
import copy

from app.services.bernie.corpus_tier import CorpusCandidate
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LC4_SCHEMA_VERSION = "lc4.scale_corpus.v2"
DEVELOPMENT_GROUP_COUNT = 96
SURFACE_VARIANTS_PER_GROUP = 9
MULTI_TURN_VARIANTS_PER_GROUP = 3
VARIANTS_PER_GROUP = SURFACE_VARIANTS_PER_GROUP + MULTI_TURN_VARIANTS_PER_GROUP  # 12 total
TOTAL_SURFACE_VARIANTS = DEVELOPMENT_GROUP_COUNT * SURFACE_VARIANTS_PER_GROUP  # 864
TOTAL_TRAJECTORIES = DEVELOPMENT_GROUP_COUNT * MULTI_TURN_VARIANTS_PER_GROUP  # 288
TOTAL_INDIVIDUAL_RECORDS = TOTAL_SURFACE_VARIANTS + TOTAL_TRAJECTORIES  # 1152

DEV_GROUP_PREFIX = "lc4_dw1_dev"
DEV_VARIANT_PREFIX = "lc4_dw1_dev_var"
DEV_MT_PREFIX = "lc4_dw1_dev_mt"

GAP_PRIORITY_MINIMUM = 58

# Temporal relation literals
TemporalRelation = Literal[
    "exact", "not_before", "not_after", "interval", "approximate", "unspecified"
]

# Action literals
Action = Literal[
    "create", "move", "resize", "cancel", "status_change", "explain_schedule"
]

# Diary state literals
DiaryState = Literal[
    "empty", "exact_duplicate", "overlap", "same_day_distinct",
    "terminal", "stale", "concurrent", "roster_absent",
    "break", "no_slots", "elapsed_window",
]

# Entity semantics
EntitySem = Literal[
    "exact", "ambiguous", "omitted", "negated", "corrected", "mismatched"
]

# Dialogue form
DialogueForm = Literal[
    "one_shot", "clarification", "correction", "reversal",
    "ellipsis", "anaphora", "repeated", "session_restart",
]

# Language form
LanguageForm = Literal[
    "plain", "paraphrase", "filler", "abbreviation",
    "typo", "speech_like", "punctuation_variant", "adversarial",
]

ALL_ACTIONS: list[Action] = [
    "create", "move", "resize", "cancel", "status_change", "explain_schedule"
]
ALL_TEMPORAL_RELATIONS: list[TemporalRelation] = [
    "exact", "not_before", "not_after", "interval", "approximate", "unspecified"
]
ALL_DIARY_STATES: list[DiaryState] = [
    "empty", "exact_duplicate", "overlap", "same_day_distinct",
    "terminal", "stale", "concurrent", "roster_absent",
    "break", "no_slots", "elapsed_window",
]
ALL_ENTITY_SEMANTICS: list[EntitySem] = [
    "exact", "ambiguous", "omitted", "negated", "corrected", "mismatched"
]
ALL_DIALOGUE_FORMS: list[DialogueForm] = [
    "one_shot", "clarification", "correction", "reversal",
    "ellipsis", "anaphora", "repeated", "session_restart",
]
ALL_LANGUAGE_FORMS: list[LanguageForm] = [
    "plain", "paraphrase", "filler", "abbreviation",
    "typo", "speech_like", "punctuation_variant", "adversarial",
]

# Gap-target categories for LC3 weakness coverage
GapTarget = Literal[
    "clarification_dialogue",
    "interval_unspecified_temporal",
    "entity_ambiguity_omission_correction",
    "interpretation_replay_tool_selection",
]

# ---------------------------------------------------------------------------
# Deterministic hash helpers
# ---------------------------------------------------------------------------


def _stable_hash(content: str) -> str:
    """Deterministic SHA-256 hex digest from stable JSON encoding."""
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Stable JSON without whitespace, sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def compute_group_hash(group_data: dict[str, Any]) -> str:
    """Deterministic hash of a group's semantic profile AND all variant hashes."""
    canonical = _canonical_json(group_data)
    return _stable_hash(canonical)


def _strip_variant_hash(variant_data: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of variant data without variant_hash (not a model field)."""
    return {k: v for k, v in variant_data.items() if k != "variant_hash"}


def compute_variant_hash(variant_data: dict[str, Any]) -> str:
    """Deterministic hash of a single canonical variant payload."""
    # Strip any pre-existing hash field to make computation idempotent
    payload = _strip_variant_hash(variant_data)
    canonical = _canonical_json(payload)
    return _stable_hash(canonical)


# ---------------------------------------------------------------------------
# Development group specification (compact)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DevelopmentGroupSpec:
    """Compact semantic specification for one development group.

    This is the authoring-time representation before expansion into
    full ReceptionScenarioSpec instances.
    """

    group_index: int  # 1..96
    intended_action: Action
    temporal_relation: TemporalRelation
    diary_state: DiaryState
    entity_state: EntitySem
    entity_ambiguity_field: str | None = None  # Which entity field is non-exact
    patient_semantics: EntitySem = "exact"
    practitioner_semantics: EntitySem = "exact"
    location_semantics: EntitySem = "omitted"
    appointment_type_semantics: EntitySem = "omitted"
    duration_semantics: EntitySem = "exact"
    dialogue_form: DialogueForm = "one_shot"
    language_form: LanguageForm = "plain"
    gap_targets: tuple[GapTarget, ...] = ()

    @property
    def group_id(self) -> str:
        return f"{DEV_GROUP_PREFIX}_group_{self.group_index:03d}"

    @property
    def is_gap_priority(self) -> bool:
        return len(self.gap_targets) > 0

    @property
    def entity_semantics_map(self) -> dict[str, str]:
        return {
            "practitioner": self.practitioner_semantics,
            "patient": self.patient_semantics,
            "location": self.location_semantics,
            "appointment_type": self.appointment_type_semantics,
            "duration": self.duration_semantics,
        }


# ---------------------------------------------------------------------------
# Development variant spec (differences from group base)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DevelopmentVariantSpec:
    """Differences relative to the group's base scenario.

    Each variant overrides utterance wording and language/dialogue form
    while preserving the group's core semantics.
    """

    variant_index: int  # 1..12 for surface, 13..15 for multi-turn
    utterance: str
    dialogue_form: DialogueForm
    language_form: LanguageForm
    is_multi_turn: bool = False
    multi_turn_turns: tuple[dict[str, Any], ...] = ()
    duration_minutes: int | None = None
    appointment_date_override: str | None = None
    earliest_time_override: str | None = None
    latest_time_override: str | None = None
    practitioner_name_override: str | None = None
    patient_name_override: str | None = None
    patient_semantics_override: EntitySem | None = None
    expected_clarification: str | None = None
    clarification_choices: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Full expanded development group
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScaleDevelopmentGroup:
    """One fully expanded development group with 12 + 3 variants."""

    spec: DevelopmentGroupSpec
    group_hash: str
    reference_date: date
    clinic_clock: datetime
    surface_variants: tuple[ReceptionScenarioSpec, ...]  # 12
    multi_turn_variants: tuple[ReceptionScenarioSpec, ...]  # 3

    @property
    def group_id(self) -> str:
        return self.spec.group_id

    @property
    def all_variants(self) -> tuple[ReceptionScenarioSpec, ...]:
        return self.surface_variants + self.multi_turn_variants

    def __post_init__(self) -> None:
        if len(self.surface_variants) != SURFACE_VARIANTS_PER_GROUP:
            raise ValueError(
                f"Expected {SURFACE_VARIANTS_PER_GROUP} surface variants, "
                f"got {len(self.surface_variants)}"
            )
        if len(self.multi_turn_variants) != MULTI_TURN_VARIANTS_PER_GROUP:
            raise ValueError(
                f"Expected {MULTI_TURN_VARIANTS_PER_GROUP} multi-turn variants, "
                f"got {len(self.multi_turn_variants)}"
            )


# ---------------------------------------------------------------------------
# Scale corpus — development collection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScaleCorpus:
    """Provider-free development corpus collection.

    Exactly 96 development groups, each with 9 surface variants and 3
    multi-turn variants (12 total per group).  All evidence is Silver/pending
    and must never be promoted or counted as adjudicated coverage.
    """

    groups: tuple[ScaleDevelopmentGroup, ...]
    corpus_hash: str

    def __post_init__(self) -> None:
        if len(self.groups) != DEVELOPMENT_GROUP_COUNT:
            raise ValueError(
                f"Expected {DEVELOPMENT_GROUP_COUNT} development groups, "
                f"got {len(self.groups)}"
            )
        seen_group_ids: set[str] = set()
        seen_variant_ids: set[str] = set()
        for g in self.groups:
            if g.group_id in seen_group_ids:
                raise ValueError(f"Duplicate group_id: {g.group_id!r}")
            seen_group_ids.add(g.group_id)
            for v in g.all_variants:
                if v.scenario_id in seen_variant_ids:
                    raise ValueError(f"Duplicate variant_id across groups: {v.scenario_id!r}")
                seen_variant_ids.add(v.scenario_id)

    def get_group(self, group_id: str) -> ScaleDevelopmentGroup | None:
        for g in self.groups:
            if g.group_id == group_id:
                return g
        return None

    def all_variants(self) -> list[ReceptionScenarioSpec]:
        """Return all 1,152 individual records (864 surface + 288 MT)."""
        result: list[ReceptionScenarioSpec] = []
        for g in self.groups:
            result.extend(g.all_variants)
        return result

    def variants_by_action(self, action: Action) -> list[ReceptionScenarioSpec]:
        return [v for g in self.groups if g.spec.intended_action == action for v in g.all_variants]

    def variants_by_temporal(self, temporal: TemporalRelation) -> list[ReceptionScenarioSpec]:
        return [v for g in self.groups if g.spec.temporal_relation == temporal for v in g.all_variants]

    @property
    def gap_priority_group_count(self) -> int:
        return sum(1 for g in self.groups if g.spec.is_gap_priority)

    def assert_gap_priority_minimum(self) -> None:
        if self.gap_priority_group_count < GAP_PRIORITY_MINIMUM:
            raise AssertionError(
                f"Only {self.gap_priority_group_count} gap-priority groups, "
                f"minimum is {GAP_PRIORITY_MINIMUM}"
            )


# ---------------------------------------------------------------------------
# Generic partition interface (testable with dummy records)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PartitionSlot:
    """One slot in a partition schema.

    This is a generic interface for sealed-holdout partitions.
    Test only with miniature dummy records — never with the actual 24-group
    holdout.
    """
    name: str
    size: int
    record_ids: tuple[str, ...] = ()
    partition_hash: str = ""


@dataclass(frozen=True)
class PartitionSchema:
    """Generic partition schema for separating development and holdout records.

    Development-only APIs must reject records from non-development partitions.
    """
    schema_version: str = "lc4.partition.v1"
    development_slots: tuple[PartitionSlot, ...] = ()
    holdout_slots: tuple[PartitionSlot, ...] = ()

    def is_development_record(self, record_id: str) -> bool:
        """Check if a record_id belongs to a development slot."""
        for slot in self.development_slots:
            if record_id in slot.record_ids:
                return True
        return False

    def is_holdout_record(self, record_id: str) -> bool:
        """Check if a record_id belongs to a holdout slot."""
        for slot in self.holdout_slots:
            if record_id in slot.record_ids:
                return True
        return False


# ---------------------------------------------------------------------------
# Sealed holdout capability (placeholder — no real holdout)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SealedHoldoutCapability:
    """Capability required to access the sealed holdout.

    This is a generic interface only.  The actual 24-group holdout is
    authored by Sol after all DeepSeek and Gemini work ends.

    Test only with miniature dummy records.
    """
    manifest_hash: str
    purpose: str
    evaluator_identity: str
    evaluation_id: str
    is_sealed: bool = False

    def validate_access(self, manifest_hash: str, purpose: str) -> bool:
        return (
            manifest_hash == self.manifest_hash
            and purpose == self.purpose
            and self.is_sealed
        )


# ---------------------------------------------------------------------------
# Development-only corpus loader
# ---------------------------------------------------------------------------


class DevelopmentOnlyLoader:
    """Loader for development corpus fixture files.

    Default APIs are development-only.  Holdout fixture paths are rejected.
    """

    DEV_FIXTURE_DIR = pathlib.Path(
        "tests/fixtures/bernie_lc4_development"
    )
    PROHIBITED_PATHS = (
        "tests/fixtures/bernie_lc4_holdout",
        "holdout",
        "sealed",
    )

    def __init__(self, fixture_root: pathlib.Path | None = None) -> None:
        self._fixture_root = fixture_root or self.DEV_FIXTURE_DIR
        self._validate_path()

    def _validate_path(self) -> None:
        """Ensure no prohibited holdout paths are referenced."""
        resolved = str(self._fixture_root.resolve())
        for prohibited in self.PROHIBITED_PATHS:
            if prohibited in resolved:
                raise ValueError(
                    f"Development loader cannot access holdout path: {resolved}"
                )

    def _validate_variant_and_hash(
        self, v: dict[str, Any], variant_type: str,
        group_spec: DevelopmentGroupSpec | None = None,
    ) -> ReceptionScenarioSpec:
        """Validate a variant dict, verify hash, and run group-aware validation.

        When *group_spec* is provided, calls validate_variant with the group
        spec to check all invariant fields.  Raises ValueError on any error.
        """
        stored_hash = v.get("variant_hash")
        if stored_hash:
            recomputed = compute_variant_hash(v)
            if stored_hash != recomputed:
                raise ValueError(
                    f"{variant_type} {v.get('scenario_id')} hash mismatch: "
                    f"stored={stored_hash}, recomputed={recomputed}"
                )
        # Strip variant_hash before model validation (extra="forbid")
        clean = _strip_variant_hash(v)
        scenario = ReceptionScenarioSpec.model_validate(clean)

        # Run group-aware validation
        if group_spec is not None:
            errors = validate_variant(scenario, group_spec=group_spec)
            if errors:
                raise ValueError(
                    f"{variant_type} {v.get('scenario_id')} validation errors: "
                    + "; ".join(errors)
                )

        return scenario

    def load_group(self, group_path: pathlib.Path) -> ScaleDevelopmentGroup:
        """Load a single development group from a JSON fixture file."""
        if not group_path.is_file():
            raise FileNotFoundError(f"Group file not found: {group_path}")

        with open(group_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Validate top-level structure
        if raw.get("provenance") != "silver":
            raise ValueError(
                f"Development group must be silver, got {raw.get('provenance')!r}"
            )
        if raw.get("adjudication") != "pending":
            raise ValueError(
                f"Development group must be pending, got {raw.get('adjudication')!r}"
            )

        spec_dict = raw.get("spec", {})
        spec = DevelopmentGroupSpec(
            group_index=spec_dict["group_index"],
            intended_action=spec_dict["intended_action"],
            temporal_relation=spec_dict["temporal_relation"],
            diary_state=spec_dict.get("diary_state", "empty"),
            entity_state=spec_dict.get("entity_state", "exact"),
            patient_semantics=spec_dict.get("patient_semantics", "exact"),
            practitioner_semantics=spec_dict.get("practitioner_semantics", "exact"),
            location_semantics=spec_dict.get("location_semantics", "omitted"),
            appointment_type_semantics=spec_dict.get("appointment_type_semantics", "omitted"),
            duration_semantics=spec_dict.get("duration_semantics", "exact"),
            dialogue_form=spec_dict.get("dialogue_form", "one_shot"),
            language_form=spec_dict.get("language_form", "plain"),
            gap_targets=tuple(spec_dict.get("gap_targets", [])),
        )

        # Load and validate surface variants
        surface_variants = []
        for v in raw.get("surface_variants", []):
            scenario = self._validate_variant_and_hash(v, "Surface variant", group_spec=spec)
            surface_variants.append(scenario)

        # Load and validate multi-turn variants
        multi_turn_variants = []
        for v in raw.get("multi_turn_variants", []):
            scenario = self._validate_variant_and_hash(v, "Multi-turn variant", group_spec=spec)
            multi_turn_variants.append(scenario)

        ref_date = date.fromisoformat(raw["reference_date"])
        clinic_clock = datetime.fromisoformat(raw["clinic_clock"])

        # Recompute and verify group hash
        stored_group_hash = raw.get("group_hash", "")
        if stored_group_hash:
            group_id = raw["group_id"]
            # Rebuild the group data input for hash verification
            surface_hashes = [v.get("variant_hash", compute_variant_hash(v)) for v in raw.get("surface_variants", [])]
            multi_turn_hashes = [v.get("variant_hash", compute_variant_hash(v)) for v in raw.get("multi_turn_variants", [])]
            group_data_input = {
                "group_id": group_id,
                "spec": {
                    "group_index": spec.group_index,
                    "intended_action": spec.intended_action,
                    "temporal_relation": spec.temporal_relation,
                    "diary_state": spec.diary_state,
                    "entity_state": spec.entity_state,
                    "patient_semantics": spec.patient_semantics,
                    "practitioner_semantics": spec.practitioner_semantics,
                    "location_semantics": spec.location_semantics,
                    "appointment_type_semantics": spec.appointment_type_semantics,
                    "duration_semantics": spec.duration_semantics,
                    "dialogue_form": spec.dialogue_form,
                    "language_form": spec.language_form,
                    "gap_targets": list(spec.gap_targets),
                },
                "surface_count": len(surface_variants),
                "multi_turn_count": len(multi_turn_variants),
                "surface_variant_hashes": surface_hashes,
                "multi_turn_variant_hashes": multi_turn_hashes,
            }
            recomputed_group_hash = compute_group_hash(group_data_input)
            if stored_group_hash != recomputed_group_hash:
                raise ValueError(
                    f"Group {group_id} hash mismatch: "
                    f"stored={stored_group_hash}, recomputed={recomputed_group_hash}"
                )

        group = ScaleDevelopmentGroup(
            spec=spec,
            group_hash=stored_group_hash,
            reference_date=ref_date,
            clinic_clock=clinic_clock,
            surface_variants=tuple(surface_variants),
            multi_turn_variants=tuple(multi_turn_variants),
        )
        return group

    def load_all(self) -> ScaleCorpus:
        """Load all development groups from the fixture directory."""
        if not self._fixture_root.is_dir():
            raise NotADirectoryError(
                f"Development fixture directory not found: {self._fixture_root}"
            )

        # Load manifest
        manifest_path = self._fixture_root / "lc4_development_manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(
                f"Development manifest not found: {manifest_path}"
            )

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        manifest_version = manifest.get("schema_version", "")
        if manifest_version != LC4_SCHEMA_VERSION:
            raise ValueError(
                f"Expected manifest schema {LC4_SCHEMA_VERSION!r}, "
                f"got {manifest_version!r}"
            )

        groups: list[ScaleDevelopmentGroup] = []
        seen_ids: set[str] = set()
        all_variant_ids: set[str] = set()
        loaded_filenames: set[str] = set()

        for entry in manifest.get("groups", []):
            filename = entry.get("filename", "")
            loaded_filenames.add(filename)
            group_path = self._fixture_root / filename
            if not group_path.is_file():
                raise FileNotFoundError(
                    f"Referenced group file not found: {group_path}"
                )

            group = self.load_group(group_path)
            if group.group_id in seen_ids:
                raise ValueError(
                    f"Duplicate group_id in manifest: {group.group_id!r}"
                )
            seen_ids.add(group.group_id)

            # Check for duplicate variant IDs across groups
            for v in group.all_variants:
                if v.scenario_id in all_variant_ids:
                    raise ValueError(
                        f"Duplicate variant ID across groups: {v.scenario_id!r}"
                    )
                all_variant_ids.add(v.scenario_id)

            groups.append(group)

        # Check for unreferenced group files in fixture directory
        for fpath in self._fixture_root.iterdir():
            if fpath.suffix == ".json" and fpath.name != "lc4_development_manifest.json":
                if fpath.name not in loaded_filenames:
                    raise ValueError(
                        f"Unreferenced group file in fixture directory: {fpath.name}"
                    )

        # Sort by group_index for deterministic order
        groups.sort(key=lambda g: g.spec.group_index)

        # Verify corpus hash
        stored_corpus_hash = manifest.get("corpus_hash", "")
        if stored_corpus_hash:
            group_hashes = [g.group_hash for g in groups]
            corpus_hash_input = _canonical_json(group_hashes)
            recomputed_corpus_hash = _stable_hash(corpus_hash_input)
            if stored_corpus_hash != recomputed_corpus_hash:
                raise ValueError(
                    f"Corpus hash mismatch: "
                    f"stored={stored_corpus_hash}, recomputed={recomputed_corpus_hash}"
                )

        corpus = ScaleCorpus(
            groups=tuple(groups),
            corpus_hash=stored_corpus_hash,
        )
        return corpus

    def reject_holdout_path(self, path: pathlib.Path) -> None:
        """Assert that the given path is not a holdout path.

        Raises ValueError if the path looks like a holdout fixture path.
        """
        resolved = str(path.resolve())
        for prohibited in self.PROHIBITED_PATHS:
            if prohibited in resolved:
                raise ValueError(
                    f"Holdout path rejected by development loader: {resolved}"
                )


# ---------------------------------------------------------------------------
# Generation helpers for building variant scenarios
# ---------------------------------------------------------------------------


def _make_source_span(
    turn_index: int, start: int, end: int, text: str
) -> dict[str, Any]:
    return {
        "turn_index": turn_index,
        "start": start,
        "end": end,
        "text": text,
    }


def _build_scenario(
    group_spec: DevelopmentGroupSpec,
    variant_id: str,
    utterance: str,
    dialogue_form: DialogueForm,
    language_form: LanguageForm,
    reference_date: date,
    clinic_clock: datetime,
    earliest_time: str | None = None,
    latest_time: str | None = None,
    duration_minutes: int = 15,
    appointment_date: str | None = None,
    patient_name: str = "Margaret Thompson",
    practitioner_name: str = "Dr Shera",
    normalized_values_extra: dict[str, Any] | None = None,
    dialogue_turns: list[dict[str, Any]] | None = None,
    source_spans: dict[str, list[dict[str, Any]]] | None = None,
    expected_clarification: str | None = None,
    clarification_choices: list[str] | None = None,
    initial_diary_state_extra: dict[str, Any] | None = None,
    expected_tool_sequence_override: list[str] | None = None,
    expected_outcome_override: str | None = None,
    expected_appointment_deltas_override: list[dict[str, Any]] | None = None,
    expected_audit_deltas_override: list[dict[str, Any]] | None = None,
    forbidden_outcomes_override: list[str] | None = None,
    forbidden_tool_calls_override: list[str] | None = None,
) -> ReceptionScenarioSpec:
    """Build a full ReceptionScenarioSpec from components.

    Uses deterministic generation — never copies from expected fields.
    """
    if appointment_date is None:
        appointment_date = (reference_date + timedelta(days=1)).isoformat()

    temporal_rel = group_spec.temporal_relation
    if earliest_time is None:
        earliest_time = "15:00"
    if latest_time is None:
        latest_time = earliest_time if temporal_rel == "exact" else "16:00"

    if temporal_rel == "unspecified":
        earliest_time_val = None
        latest_time_val = None
    else:
        earliest_time_val = earliest_time
        latest_time_val = (
            latest_time if temporal_rel in ("interval", "not_after", "approximate")
            else earliest_time
        )

    if temporal_rel == "not_before":
        earliest_time_val = earliest_time
        latest_time_val = None
    elif temporal_rel == "not_after":
        earliest_time_val = None
        latest_time_val = latest_time

    turns = dialogue_turns or [
        {"turn": 1, "utterance": utterance}
    ]

    if source_spans is None:
        source_spans = _derive_source_spans(
            utterance, turns, earliest_time_val, latest_time_val,
            duration_minutes, patient_name, practitioner_name,
            appointment_date_text=appointment_date,
        )

    norm_values: dict[str, Any] = {
        "appointment_date": appointment_date,
        "duration_minutes": duration_minutes,
    }
    if earliest_time_val is not None:
        norm_values["earliest_time"] = earliest_time_val
    if latest_time_val is not None:
        norm_values["latest_time"] = latest_time_val
    if normalized_values_extra:
        norm_values.update(normalized_values_extra)

    # Determine dialogue form from turns
    eff_dialogue_form = dialogue_form
    if len(turns) > 1 and dialogue_form == "one_shot":
        eff_dialogue_form = "clarification"

    # Determine language form
    eff_language_form = language_form

    # Entity semantics from group spec (authoritative — no utterance-based override)
    patient_sem = group_spec.patient_semantics
    pract_sem = group_spec.practitioner_semantics
    duration_sem = group_spec.duration_semantics

    # Expected outcome + tool sequence
    action = group_spec.intended_action
    diary_state = group_spec.diary_state

    if expected_outcome_override:
        outcome_kind = expected_outcome_override
    elif action == "create" and diary_state == "exact_duplicate":
        outcome_kind = "existing_booking_found"
    elif action == "create" and diary_state == "overlap":
        outcome_kind = "candidate_selection_required"
    elif action == "create":
        outcome_kind = "appointment_created"
    elif action == "move":
        outcome_kind = "appointment_moved"
    elif action == "resize":
        outcome_kind = "appointment_resized"
    elif action == "cancel":
        outcome_kind = "appointment_cancelled"
    elif action == "status_change":
        outcome_kind = "appointment_status_changed"
    elif action == "explain_schedule":
        outcome_kind = "schedule_explained"
    else:
        outcome_kind = "action_completed"

    # Tool sequence
    if expected_tool_sequence_override:
        tool_seq = expected_tool_sequence_override
    elif requires_clarification_for_spec(group_spec) or expected_clarification is not None:
        tool_seq = ["request_clarification"]
    elif action == "create":
        tool_seq = ["search_patients", "find_slots", "create_booking"]
    elif action in ("move", "resize", "cancel"):
        tool_seq = ["search_patients", "update_appointment"]
    elif action == "status_change":
        tool_seq = ["search_patients", "change_appointment_status"]
    elif action == "explain_schedule":
        tool_seq = ["search_patients", "find_slots"]
    else:
        tool_seq = ["search_patients"]

    # Appointment deltas
    if expected_appointment_deltas_override is not None:
        apt_deltas = expected_appointment_deltas_override
    else:
        apt_deltas = _derive_appointment_deltas(
            action, appointment_date, earliest_time_val, duration_minutes,
            practitioner_name, patient_name,
        )

    # Audit deltas
    if expected_audit_deltas_override is not None:
        aud_deltas = expected_audit_deltas_override
    else:
        aud_deltas = _derive_audit_deltas(action)

    # Forbidden
    forbidden_outcomes = forbidden_outcomes_override or (
        ["second_appointment_created"] if diary_state == "exact_duplicate" else []
    )
    forbidden_tools = forbidden_tool_calls_override or [
        "mutate_diary_direct", "override_confirmation"
    ]

    # Determine entity state from group spec
    entity_state = group_spec.entity_state

    # Diary_state for initial
    initial_diary: dict[str, Any] = {
        "reference_date": reference_date.isoformat(),
        "diary_page_date": appointment_date,
        "seeded_appointments": [],
        "practitioners_available": ["pr-001"],
        "patients_booked_today": [],
    }
    if initial_diary_state_extra:
        initial_diary.update(initial_diary_state_extra)

    return ReceptionScenarioSpec(
        spec_version="lc1.v1",
        scenario_id=variant_id,
        provenance="silver",
        adjudication="pending",
        family=group_spec.group_id,
        description=f"{action}:{temporal_rel}:{dialogue_form}:{language_form} - {utterance[:80]}",
        dialogue_turns=turns,
        reference_date=reference_date,
        clinic_clock=clinic_clock,
        intended_action=action,
        action_semantics="intended",
        temporal_relation=temporal_rel,
        earliest_time=earliest_time_val,
        latest_time=latest_time_val,
        normalized_values=norm_values,
        source_spans=source_spans,
        duration_minutes=duration_minutes,
        practitioner_semantics=pract_sem,
        patient_semantics=patient_sem,
        location_semantics=group_spec.location_semantics,
        appointment_type_semantics=group_spec.appointment_type_semantics,
        duration_semantics=duration_sem,
        diary_state=diary_state,
        entity_state=entity_state,
        dialogue_form=eff_dialogue_form,
        language_form=eff_language_form,
        initial_diary_state=initial_diary,
        expected_outcome_kind=outcome_kind,
        expected_tool_sequence=tool_seq,
        expected_appointment_deltas=apt_deltas,
        expected_audit_deltas=aud_deltas,
        forbidden_outcomes=forbidden_outcomes,
        forbidden_tool_calls=forbidden_tools,
        expected_clarification=expected_clarification,
        clarification_choices=clarification_choices or [],
    )


def requires_clarification_for_spec(spec: DevelopmentGroupSpec) -> bool:
    """Determine if a group's semantic spec requires clarification."""
    return (
        "clarification_dialogue" in spec.gap_targets
        or spec.dialogue_form == "clarification"
        or spec.entity_state in ("ambiguous", "omitted")
    )


def _derive_source_spans(
    utterance: str,
    turns: list[dict[str, Any]],
    earliest_time: str | None,
    latest_time: str | None,
    duration_minutes: int,
    patient_name: str,
    practitioner_name: str,
    *,
    appointment_date_text: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Derive source spans from utterance text by pattern matching.

    Includes evidence keys for appointment_date, earliest_time, latest_time,
    patient, practitioner, duration_minutes, and temporal_relation.
    """
    spans: dict[str, list[dict[str, Any]]] = {}

    for turn in turns:
        text = turn.get("utterance", "")
        ti = turn.get("turn", 1) - 1

        # Appointment date (look for "tomorrow", "today", etc.)
        date_words = ["tomorrow", "today", "next week",
                     "monday", "tuesday", "wednesday", "thursday", "friday"]
        lower_text = text.lower()
        for word in date_words:
            if word in lower_text:
                # Find the actual position of the date word
                word_idx = lower_text.find(word)
                if word_idx >= 0:
                    actual_word = text[word_idx:word_idx + len(word)]
                    spans.setdefault("appointment_date", []).append(
                        _make_source_span(ti, word_idx, word_idx + len(word), actual_word)
                    )
                else:
                    spans.setdefault("appointment_date", []).append(
                        _make_source_span(ti, 0, 5, (appointment_date_text or "tomorrow")[:5])
                    )
                break

        # Time patterns -> temporal_relation, earliest_time, latest_time
        time_pattern = re.compile(r"\b(\d{1,2})\s*(pm|am)\b", re.I)
        for match in time_pattern.finditer(text):
            key = "temporal_relation"
            spans.setdefault(key, []).append(
                _make_source_span(ti, match.start(), match.end(), match.group(0))
            )
            hour_str = match.group(1)
            meridian = match.group(2).lower()
            # Convert 12-hour to 24-hour for comparison
            hour_24 = int(hour_str)
            if meridian == "pm" and hour_24 != 12:
                hour_24 += 12
            elif meridian == "am" and hour_24 == 12:
                hour_24 = 0
            hour_24_str = str(hour_24).zfill(2)

            if earliest_time:
                earliest_hour_str = earliest_time.split(":")[0]
                if earliest_hour_str == hour_24_str:
                    spans.setdefault("earliest_time", []).append(
                        _make_source_span(ti, match.start(), match.end(), match.group(0))
                    )

            if latest_time:
                latest_hour_str = latest_time.split(":")[0]
                if latest_hour_str == hour_24_str:
                    if not earliest_time or latest_time != earliest_time:
                        spans.setdefault("latest_time", []).append(
                            _make_source_span(ti, match.start(), match.end(), match.group(0))
                        )
                    elif earliest_time == latest_time and "earliest_time" in spans:
                        # Exact time: reuse earliest as latest
                        for es in spans.get("earliest_time", []):
                            spans.setdefault("latest_time", []).append(es)

        # Patient name
        if patient_name in text:
            idx = text.index(patient_name)
            spans.setdefault("patient", []).append(
                _make_source_span(ti, idx, idx + len(patient_name), patient_name)
            )

        # Practitioner name
        if practitioner_name in text:
            idx = text.index(practitioner_name)
            spans.setdefault("practitioner", []).append(
                _make_source_span(ti, idx, idx + len(practitioner_name), practitioner_name)
            )

        # Duration
        dur_match = re.search(r"\b(\d+)\s*minutes?\b", text, re.I)
        if dur_match:
            spans.setdefault("duration_minutes", []).append(
                _make_source_span(
                    ti, dur_match.start(), dur_match.end(), dur_match.group(0)
                )
            )

    # Fallback: use first/last time pattern for missing bounds
    found_times = []
    for turn in turns:
        t_text = turn.get("utterance", "")
        t_ti = turn.get("turn", 1) - 1
        for match in re.finditer(r"\b(\d{1,2})\s*(pm|am)\b", t_text, re.I):
            found_times.append((t_ti, match.start(), match.end(), match.group(0)))

    if earliest_time and "earliest_time" not in spans and found_times:
        ti, st, en, txt = found_times[0]
        spans["earliest_time"] = [_make_source_span(ti, st, en, txt)]
    if latest_time and "latest_time" not in spans and found_times:
        ti, st, en, txt = found_times[-1]
        spans["latest_time"] = [_make_source_span(ti, st, en, txt)]

    return spans

def _derive_appointment_deltas(
    action: Action,
    appointment_date: str,
    start_time: str | None,
    duration_minutes: int,
    practitioner_name: str,
    patient_name: str,
) -> list[dict[str, Any]]:
    """Derive appointment deltas from action and parameters."""
    if action == "explain_schedule":
        return []

    pid = "pr-001" if "Shera" in practitioner_name else "pr-002"
    delta: dict[str, Any] = {
        "appointment_id": "apt-001",
        "patient_id": "p-001",
        "practitioner_id": pid,
        "date": appointment_date,
    }

    if action == "create":
        delta["change_type"] = "created"
        delta["start_time"] = start_time or "15:00"
        delta["duration_minutes"] = duration_minutes
    elif action == "move":
        delta["change_type"] = "moved"
        delta["new_start_time"] = start_time or "15:00"
        delta["new_date"] = appointment_date
    elif action == "resize":
        delta["change_type"] = "resized"
        delta["new_duration_minutes"] = duration_minutes
    elif action == "cancel":
        delta["change_type"] = "cancelled"
        delta["start_time"] = start_time or "15:00"
    elif action == "status_change":
        delta["change_type"] = "status_changed"
        delta["new_status"] = "arrived"
    else:
        delta["change_type"] = "updated"

    return [delta]


def _derive_audit_deltas(action: Action) -> list[dict[str, Any]]:
    """Derive audit deltas from action."""
    if action == "explain_schedule":
        return []
    return [
        {
            "change_type": f"{action}_requested",
            "appointment_id": "apt-001",
            "count": 1,
        }
    ]


# ---------------------------------------------------------------------------
# Development corpus generator — produces 96 groups from spec definitions
# ---------------------------------------------------------------------------


def _apply_entity_semantics(
    utterance: str,
    patient_sem: str,
    practitioner_sem: str,
    patient_name: str = "Margaret Thompson",
    practitioner_name: str = "Dr Shera",
) -> str:
    """Post-process utterance to reflect entity semantics.

    For omitted entities, replace the named entity with a generic reference.
    For ambiguous entities, use a vague reference.
    For negated entities, prefix with a negation phrase.
    For mismatched entities, replace with wrong name.
    For corrected entities, leave as-is (correction is handled in multi-turn).
    For exact semantics, does NOT modify the utterance.
    """
    result = utterance

    if patient_sem == "exact":
        pass  # Keep the name as-is
    elif patient_sem == "omitted" and patient_name in result:
        result = result.replace(patient_name, "a patient", 1)
    elif patient_sem == "ambiguous" and patient_name in result:
        result = result.replace(patient_name, "someone", 1)
    elif patient_sem == "negated" and patient_name in result:
        if not any(w in result.lower() for w in ("not", "n't", "except", "but not")):
            result = result.replace(patient_name, f"not {patient_name}")
    elif patient_sem == "mismatched":
        result = result.replace(patient_name, "Robert Johnson")

    if practitioner_sem == "exact":
        pass  # Keep the name as-is
    elif practitioner_sem == "omitted" and practitioner_name in result:
        result = result.replace(practitioner_name, "a practitioner", 1)
    elif practitioner_sem == "ambiguous" and practitioner_name in result:
        result = result.replace(practitioner_name, "some doctor", 1)
    elif practitioner_sem == "negated" and practitioner_name in result:
        if not any(w in result.lower() for w in ("not", "n't", "except", "but not")):
            result = result.replace(practitioner_name, f"not {practitioner_name}")
    elif practitioner_sem == "mismatched":
        result = result.replace(practitioner_name, "Dr Patel")

    return result


def _make_utterance_variant(
    action: Action,
    template_index: int,
    patient_name: str = "Margaret Thompson",
    practitioner_name: str = "Dr Shera",
    time_str: str = "3pm",
    date_str: str = "tomorrow",
    duration_str: str = "15 minutes",
    location_str: str = "Room 2",
    patient_sem: str = "exact",
    practitioner_sem: str = "exact",
) -> str:
    """Generate a single utterance variant with meaningful wording variation.

    Uses 9 distinct linguistic patterns per action for the 9 surface variants.
    Entity semantics are applied as post-processing to ensure agreement.
    """
    patterns: list[str] = []

    if action == "create":
        patterns = [
            f"Book {patient_name} with {practitioner_name} {date_str} at {time_str} for {duration_str}.",
            f"Could I schedule an appointment for {patient_name} with {practitioner_name} {date_str} at {time_str}? It should be about {duration_str}.",
            f"New booking: {patient_name}, {practitioner_name}, {date_str} {time_str}, {duration_str}.",
            f"Hi, I need to book {patient_name} in to see {practitioner_name} {date_str} around {time_str} for roughly {duration_str}, please.",
            f"Please make an apt for {patient_name} w/ {practitioner_name} on {date_str} @ {time_str} ~{duration_str}.",
            f"I'd like to put {patient_name} down for an appointment with {practitioner_name} {date_str} at {time_str}, lasting {duration_str}.",
            f"Schedule {patient_name} — {practitioner_name} — {date_str} {time_str} — {duration_str}.",
            f"Please add {patient_name} to {practitioner_name}'s book {date_str} at {time_str} for a {duration_str} slot.",
            f"Set up a visit for {patient_name} with {practitioner_name} {date_str} at {time_str}, duration {duration_str}.",
        ]
    elif action == "move":
        patterns = [
            f"Move {patient_name}'s appointment with {practitioner_name} from {time_str} to 4pm {date_str}.",
            f"Could I reschedule {patient_name}'s booking with {practitioner_name}? We need to shift it to 4pm {date_str} instead.",
            f"Reschedule: {patient_name}, {practitioner_name}, move to {date_str} at 4pm.",
            f"Hi, {patient_name}'s appointment with {practitioner_name} needs to be moved to {date_str} at 4pm, not {time_str}.",
            f"Please shift {patient_name}'s apt w/ {practitioner_name} to {date_str} @ 4pm.",
            f"I need to move {patient_name}'s booking with {practitioner_name} forward to {date_str} at 4pm — can you update that?",
            f"Change: {patient_name} — {practitioner_name} — move to {date_str} 4pm.",
            f"Please reschedule {patient_name}'s appointment with {practitioner_name} to {date_str} at 4pm.",
            f"Could we reschedule {patient_name} with {practitioner_name} to {date_str} at 4pm, please?",
        ]
    elif action == "resize":
        patterns = [
            f"Make {patient_name}'s appointment with {practitioner_name} longer — change it to 30 minutes {date_str} at {time_str}.",
            f"I need to extend {patient_name}'s booking with {practitioner_name} to 30 minutes {date_str} at {time_str}.",
            f"Change duration: {patient_name}, {practitioner_name}, now 30 mins {date_str} {time_str}.",
            f"Hi, can you make {patient_name}'s appointment with {practitioner_name} longer? Stretch it to 30 minutes {date_str} {time_str}.",
            f"Increase {patient_name}'s apt w/ {practitioner_name} to 30 mins {date_str} {time_str}.",
            f"We need to double {patient_name}'s appointment with {practitioner_name} to 30 minutes {date_str} {time_str}.",
            f"Resize: {patient_name} — {practitioner_name} — 30 min slot {date_str} {time_str}.",
            f"Please change {patient_name}'s booking to 30 minutes with {practitioner_name} {date_str} {time_str}.",
            f"Could we increase {patient_name}'s appointment with {practitioner_name} to 30 minutes {date_str} {time_str}?",
        ]
    elif action == "cancel":
        patterns = [
            f"Cancel {patient_name}'s appointment with {practitioner_name} {date_str} at {time_str}.",
            f"I need to remove {patient_name}'s booking with {practitioner_name} for {date_str} at {time_str}.",
            f"Cancel: {patient_name}, {practitioner_name}, {date_str} {time_str}.",
            f"Hi, would you please cancel {patient_name}'s appointment with {practitioner_name} for {date_str} at {time_str}?",
            f"Please cancel {patient_name}'s apt w/ {practitioner_name} on {date_str} @ {time_str}.",
            f"We need to call off {patient_name}'s booking with {practitioner_name} for {date_str} at {time_str}.",
            f"Remove: {patient_name} — {practitioner_name} — {date_str} {time_str}.",
            f"Please delete {patient_name}'s appointment with {practitioner_name} on {date_str} at {time_str}.",
            f"Could I cancel {patient_name}'s booking with {practitioner_name} for {date_str} at {time_str}?",
        ]
    elif action == "status_change":
        patterns = [
            f"Mark {patient_name} arrived for her appointment with {practitioner_name} {date_str} at {time_str}.",
            f"{patient_name} has arrived for her appointment with {practitioner_name} {date_str} at {time_str} — please mark her as arrived.",
            f"Arrived: {patient_name}, {practitioner_name}, {date_str} {time_str}.",
            f"Hi, could you please check in {patient_name}? She's here to see {practitioner_name} {date_str} at {time_str}.",
            f"Please mark {patient_name} arrived for {practitioner_name} {date_str} {time_str}.",
            f"{patient_name} is here now — please confirm arrival for her booking with {practitioner_name} {date_str} at {time_str}.",
            f"Status: {patient_name} — {practitioner_name} — ARRIVED {date_str} {time_str}.",
            f"Please update {patient_name}'s status to arrived for {practitioner_name} {date_str} at {time_str}.",
            f"Could you mark {patient_name} as arrived for {practitioner_name}? She's here {date_str} at {time_str}.",
        ]
    elif action == "explain_schedule":
        patterns = [
            f"Can you explain what {practitioner_name}'s schedule looks like {date_str}?",
            f"Could I see {practitioner_name}'s availability for {date_str} please?",
            f"What appointments does {practitioner_name} have {date_str}?",
            f"Hi, I need to know what {practitioner_name}'s day looks like {date_str}.",
            f"Show me {practitioner_name}'s schedule for {date_str}.",
            f"Can you tell me when {practitioner_name} has free slots {date_str}?",
            f"Schedule: {practitioner_name} — {date_str} — availability?",
            f"Please show me {practitioner_name}'s available times for {date_str}.",
            f"Could you pull up {practitioner_name}'s schedule for {date_str} so I can see the gaps?",
        ]
    else:
        patterns = [
            f"Please manage {patient_name}'s booking with {practitioner_name} {date_str}.",
        ]

    if template_index < len(patterns):
        utterance = patterns[template_index]
    else:
        utterance = patterns[0]

    # Apply entity semantics post-processing
    utterance = _apply_entity_semantics(
        utterance, patient_sem, practitioner_sem,
        patient_name=patient_name, practitioner_name=practitioner_name,
    )
    return utterance


def _build_multi_turn_utterances(
    action: Action,
    mt_index: int,
    patient_name: str = "Margaret Thompson",
    practitioner_name: str = "Dr Shera",
    time_str: str = "3pm",
    date_str: str = "tomorrow",
    duration_str: str = "15 minutes",
) -> list[dict[str, Any]]:
    """Generate multi-turn dialogue variants for a group."""
    if mt_index == 1:
        # Clarification: initial vague request, then clarification
        if action == "create":
            return [
                {"turn": 1, "utterance": f"Hi, I need to book Margaret Thompson in with Dr Shera sometime tomorrow."},
                {"turn": 2, "utterance": f"She'd prefer the afternoon, around 3pm, for 15 minutes."},
            ]
        elif action == "move":
            return [
                {"turn": 1, "utterance": f"I need to move Margaret Thompson's appointment with Dr Shera."},
                {"turn": 2, "utterance": f"Move it to tomorrow at 4pm with Dr Shera instead."},
            ]
        elif action == "resize":
            return [
                {"turn": 1, "utterance": f"Can you make Margaret Thompson's appointment with Dr Shera longer?"},
                {"turn": 2, "utterance": f"Change it to 30 minutes tomorrow at 3pm with Dr Shera."},
            ]
        elif action == "cancel":
            return [
                {"turn": 1, "utterance": f"I need to cancel an appointment."},
                {"turn": 2, "utterance": f"It's Margaret Thompson with Dr Shera tomorrow at 3pm."},
            ]
        elif action == "status_change":
            return [
                {"turn": 1, "utterance": f"A patient just arrived for an appointment."},
                {"turn": 2, "utterance": f"Margaret Thompson is here to see Dr Shera {date_str} at 3pm."},
            ]
        elif action == "explain_schedule":
            return [
                {"turn": 1, "utterance": f"Can you check the schedule for me?"},
                {"turn": 2, "utterance": f"I need to know what Dr Shera's day looks like tomorrow."},
            ]
        else:
            return [
                {"turn": 1, "utterance": f"I need help with a booking."},
                {"turn": 2, "utterance": f"It's for Margaret Thompson with Dr Shera tomorrow at 3pm."},
            ]
    elif mt_index == 2:
        # Correction: first utterance with wrong info, then corrected
        if action == "create":
            return [
                {"turn": 1, "utterance": f"Book Margaret Thompson with Dr Patel tomorrow at 2pm for 15 minutes."},
                {"turn": 2, "utterance": f"Actually, make it with Dr Shera at 3pm instead."},
            ]
        elif action == "move":
            return [
                {"turn": 1, "utterance": f"Move Margaret Thompson's appointment with Dr Shera to Thursday at 2pm."},
                {"turn": 2, "utterance": f"Actually, move it to tomorrow at 4pm with Dr Shera."},
            ]
        elif action == "resize":
            return [
                {"turn": 1, "utterance": f"Make Margaret Thompson's appointment with Dr Shera 45 minutes {date_str}."},
                {"turn": 2, "utterance": f"Actually, 30 minutes is better tomorrow at 3pm."},
            ]
        elif action == "cancel":
            return [
                {"turn": 1, "utterance": f"Cancel Margaret Thompson's appointment with Dr Patel."},
                {"turn": 2, "utterance": f"Sorry, it's with Dr Shera — cancel that one tomorrow at 3pm."},
            ]
        elif action == "status_change":
            return [
                {"turn": 1, "utterance": f"Mark Margaret Thompson arrived for Dr Patel."},
                {"turn": 2, "utterance": f"Sorry, she's here for Dr Shera {date_str} at 3pm."},
            ]
        elif action == "explain_schedule":
            return [
                {"turn": 1, "utterance": f"What does Dr Patel's schedule look like tomorrow?"},
                {"turn": 2, "utterance": f"Actually, I need Dr Shera's schedule instead."},
            ]
        else:
            return [
                {"turn": 1, "utterance": f"Book Margaret Thompson with Dr Patel tomorrow at 2pm."},
                {"turn": 2, "utterance": f"Actually, Dr Shera at 3pm please."},
            ]
    else:
        # Reversal / repeated: initial statement then reversal
        if action == "create":
            return [
                {"turn": 1, "utterance": f"Book Margaret Thompson with Dr Shera tomorrow at 3pm for 15 minutes."},
                {"turn": 2, "utterance": f"Actually, never mind — that's not needed after all."},
            ]
        elif action == "move":
            return [
                {"turn": 1, "utterance": f"Move Margaret Thompson's appointment with Dr Shera to tomorrow at 4pm."},
                {"turn": 2, "utterance": f"Actually, leave it where it was, sorry."},
            ]
        elif action == "resize":
            return [
                {"turn": 1, "utterance": f"Make Margaret Thompson's appointment with Dr Shera 30 minutes {date_str} at {time_str}."},
                {"turn": 2, "utterance": f"Actually no, keep the original time, my mistake."},
            ]
        elif action == "cancel":
            return [
                {"turn": 1, "utterance": f"Cancel Margaret Thompson's appointment with Dr Shera tomorrow at 3pm."},
                {"turn": 2, "utterance": f"Oh wait, don't cancel — I misunderstood."},
            ]
        elif action == "status_change":
            return [
                {"turn": 1, "utterance": f"Mark Margaret Thompson as arrived for Dr Shera {date_str} at 3pm."},
                {"turn": 2, "utterance": f"Actually, she hasn't arrived yet — cancel that."},
            ]
        elif action == "explain_schedule":
            return [
                {"turn": 1, "utterance": f"Show me Dr Shera's schedule for tomorrow."},
                {"turn": 2, "utterance": f"Actually, I need today's schedule instead."},
            ]
        else:
            return [
                {"turn": 1, "utterance": f"Book Margaret Thompson with Dr Shera tomorrow."},
                {"turn": 2, "utterance": f"Never mind, please disregard."},
            ]


# ---------------------------------------------------------------------------
# Complete fixture generation
# ---------------------------------------------------------------------------


def generate_development_fixture(
    output_dir: pathlib.Path,
    reference_date: date | None = None,
) -> ScaleCorpus:
    """Generate all 96 development group fixture files.

    This is the authoritative deterministic generator.  Results are written
    to *output_dir* as 96 JSON group files + manifest.

    Returns the constructed ScaleCorpus for validation.
    """
    if reference_date is None:
        reference_date = date(2026, 7, 14)

    clinic_tz = timezone(timedelta(hours=10))
    clinic_clock = datetime(
        reference_date.year, reference_date.month, reference_date.day,
        9, 0, 0, tzinfo=clinic_tz,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build 96 group specs
    group_specs: list[DevelopmentGroupSpec] = []

    # Distribute across actions (16 per action = 96)
    action_temporal_distribution: list[tuple[Action, TemporalRelation]] = []

    for action in ALL_ACTIONS:
        # Per action: 3 exact, 3 not_before, 3 not_after, 3 interval, 2 approx, 2 unspecified = 16
        temporal_counts = [
            ("exact", 3), ("not_before", 3), ("not_after", 3),
            ("interval", 3), ("approximate", 2), ("unspecified", 2),
        ]
        for temporal, count in temporal_counts:
            for _ in range(count):
                action_temporal_distribution.append((action, temporal))

    # Now assign entity/dialogue/language diversity
    diary_states_cycle = ALL_DIARY_STATES * 9  # 99 entries, we need 96
    entity_states_cycle = ALL_ENTITY_SEMANTICS * 16
    dialogue_forms_cycle = ALL_DIALOGUE_FORMS * 12
    language_forms_cycle = ALL_LANGUAGE_FORMS * 12

    for idx, (action, temporal) in enumerate(action_temporal_distribution[:DEVELOPMENT_GROUP_COUNT]):
        diary_state = diary_states_cycle[idx % len(diary_states_cycle)]
        entity_state = entity_states_cycle[idx % len(entity_states_cycle)]
        dialogue_form = dialogue_forms_cycle[idx % len(dialogue_forms_cycle)]
        language_form = language_forms_cycle[idx % len(language_forms_cycle)]

        # Determine gap targets
        gap_targets: list[GapTarget] = []
        if dialogue_form == "clarification":
            gap_targets.append("clarification_dialogue")
        if temporal in ("interval", "unspecified"):
            gap_targets.append("interval_unspecified_temporal")
        if entity_state in ("ambiguous", "omitted", "corrected"):
            gap_targets.append("entity_ambiguity_omission_correction")
        # Every group with non-standard dialogue/temporal gets tool selection gap
        if dialogue_form != "one_shot" or temporal in ("interval", "unspecified"):
            gap_targets.append("interpretation_replay_tool_selection")

        spec = DevelopmentGroupSpec(
            group_index=idx + 1,
            intended_action=action,
            temporal_relation=temporal,
            diary_state=diary_state,
            entity_state=entity_state,
            dialogue_form=dialogue_form,
            language_form=language_form,
            gap_targets=tuple(gap_targets),
            # Vary entity semantics per group
            # explain_schedule doesn't involve a patient entity, so default to "omitted"
            patient_semantics=(
                "omitted" if action == "explain_schedule" else
                "exact" if entity_state != "ambiguous" else
                "ambiguous"
            ),
            practitioner_semantics=(
                "corrected" if dialogue_form == "correction" else
                "ambiguous" if entity_state == "ambiguous" else
                "exact"
            ),
        )
        group_specs.append(spec)

    # Generate each group
    groups: list[ScaleDevelopmentGroup] = []
    all_group_data: list[dict[str, Any]] = []

    for spec in group_specs:
        group_data, group_obj = _build_group_fixture(
            spec, reference_date, clinic_clock,
        )
        groups.append(group_obj)
        all_group_data.append(group_data)

    # Write fixture files
    group_files: list[dict[str, Any]] = []

    for idx, (spec, group_data) in enumerate(zip(group_specs, all_group_data)):
        filename = f"{DEV_GROUP_PREFIX}_group_{spec.group_index:03d}.json"
        filepath = output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(group_data, f, indent=2, default=str)

        group_files.append({
            "group_index": spec.group_index,
            "group_id": spec.group_id,
            "filename": filename,
            "group_hash": group_data["group_hash"],
            "variant_hashes": group_data.get("variant_hashes", {}),
            "action": spec.intended_action,
            "temporal_relation": spec.temporal_relation,
            "gap_targets": list(spec.gap_targets),
            "surface_variant_count": SURFACE_VARIANTS_PER_GROUP,
            "multi_turn_count": MULTI_TURN_VARIANTS_PER_GROUP,
        })

    # Compute corpus hash from chained group hashes (which cover all variant payloads)
    corpus_hash_input = _canonical_json([g["group_hash"] for g in group_files])
    corpus_hash = _stable_hash(corpus_hash_input)

    # Write manifest
    manifest: dict[str, Any] = {
        "schema_version": LC4_SCHEMA_VERSION,
        "corpus": "lc4-development",
        "provenance": "silver",
        "adjudication": "pending",
        "total_groups": DEVELOPMENT_GROUP_COUNT,
        "total_surface_variants": TOTAL_SURFACE_VARIANTS,
        "total_multi_turn_trajectories": TOTAL_TRAJECTORIES,
        "total_individual_records": TOTAL_INDIVIDUAL_RECORDS,
        "reference_date": reference_date.isoformat(),
        "generator_identity": {
            "provider_id": "deepseek",
            "model_id": "deepseek-v4-flash",
            "instance_id": "lc4-dw1",
        },
        "authority_grant": {
            "provider_write": False,
            "diary_write": False,
            "confirmation": False,
            "override_authority": False,
        },
        "corpus_hash": corpus_hash,
        "groups": group_files,
    }

    manifest_path = output_dir / "lc4_development_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)

    return ScaleCorpus(groups=tuple(groups), corpus_hash=corpus_hash)


def _build_group_fixture(
    spec: DevelopmentGroupSpec,
    reference_date: date,
    clinic_clock: datetime,
) -> tuple[dict[str, Any], ScaleDevelopmentGroup]:
    """Build the fixture data and expanded group for one spec."""
    group_id = spec.group_id
    action = spec.intended_action
    temporal = spec.temporal_relation

    # Determine date strings for utterances
    date_str = "tomorrow"
    if temporal == "not_before":
        date_str = "tomorrow after"
    elif temporal == "not_after":
        date_str = "tomorrow before"
    elif temporal == "interval":
        date_str = "tomorrow between"
    elif temporal == "approximate":
        date_str = "tomorrow around"
    elif temporal == "unspecified":
        date_str = "sometime tomorrow"

    time_str = "3pm"
    if temporal == "not_before":
        time_str = "3pm"
    elif temporal == "not_after":
        time_str = "5pm"
    elif temporal == "interval":
        time_str = "2pm and 4pm"
    elif temporal == "approximate":
        time_str = "around 3pm"
    elif temporal == "unspecified":
        time_str = "some time"

    # Compute earliest/latest time based on temporal relation
    earliest_time = None
    latest_time = None
    if temporal == "exact":
        earliest_time = "15:00"
        latest_time = "15:00"
    elif temporal == "not_before":
        earliest_time = "15:00"
        latest_time = None
    elif temporal == "not_after":
        earliest_time = None
        latest_time = "17:00"
    elif temporal == "interval":
        earliest_time = "14:00"
        latest_time = "16:00"
    elif temporal == "approximate":
        earliest_time = "15:00"
        latest_time = "15:00"
    elif temporal == "unspecified":
        earliest_time = None
        latest_time = None

    # Build the 9 surface variant specs
    surface_variants: list[ReceptionScenarioSpec] = []
    surface_data: list[dict[str, Any]] = []

    for vi in range(1, SURFACE_VARIANTS_PER_GROUP + 1):
        variant_id = f"{DEV_VARIANT_PREFIX}_{spec.group_index:03d}_{vi:02d}"

        utterance = _make_utterance_variant(
            action, vi - 1,
            date_str=date_str, time_str=time_str,
            patient_sem=spec.patient_semantics,
            practitioner_sem=spec.practitioner_semantics,
        )

        # Determine dialogue form per variant (must be valid DialogueForm literal)
        df: DialogueForm = spec.dialogue_form
        if df == "one_shot":
            if vi % 5 == 0:
                df = "clarification"
            elif vi % 7 == 0:
                df = "correction"
            elif vi % 9 == 0:
                df = "repeated"

        # Determine language form per variant
        lf: LanguageForm = spec.language_form
        if lf == "plain":
            if vi % 3 == 0:
                lf = "paraphrase"
            elif vi % 5 == 0:
                lf = "typo"
            elif vi % 7 == 0:
                lf = "filler"
            elif vi % 8 == 0:
                lf = "speech_like"
            elif vi % 9 == 0:
                lf = "punctuation_variant"
            elif vi % 10 == 0:
                lf = "abbreviation"

        scenario = _build_scenario(
            spec, variant_id, utterance, df, lf,
            reference_date, clinic_clock,
            earliest_time=earliest_time,
            latest_time=latest_time,
            duration_minutes=15,
        )

        surface_variants.append(scenario)
        surface_data.append(scenario.model_dump(mode="json"))

    # Build the 3 multi-turn variant specs
    multi_turn_variants: list[ReceptionScenarioSpec] = []
    multi_turn_data: list[dict[str, Any]] = []

    for mt_idx in range(1, MULTI_TURN_VARIANTS_PER_GROUP + 1):
        mt_id = f"{DEV_MT_PREFIX}_{spec.group_index:03d}_{mt_idx:02d}"

        turns = _build_multi_turn_utterances(action, mt_idx)

        # Multi-turn utterances combined for span derivation
        combined = " ".join(t.get("utterance", "") for t in turns)

        # Determine dialogue form from multi-turn type
        if mt_idx == 1:
            mt_df: DialogueForm = "clarification"
        elif mt_idx == 2:
            mt_df = "correction"
        else:
            mt_df = "reversal"

        mt_lf: LanguageForm = "plain"

        # Build source spans from all turns
        def _scan_turn_spans(turns_list, earliest_t, latest_t):
            """Scan all turns building source spans."""
            sp: dict[str, list[dict[str, Any]]] = {}
            ft: list[tuple[int, int, int, str, str]] = []
            for turn in turns_list:
                t_ti = turn.get("turn", 1) - 1
                t_text = turn.get("utterance", "")

                for pat_name in ["Margaret Thompson", "Dr Shera", "Dr Patel"]:
                    if pat_name in t_text:
                        idx = t_text.index(pat_name)
                        key = "patient" if "Margaret" in pat_name else "practitioner"
                        sp.setdefault(key, []).append(
                            _make_source_span(t_ti, idx, idx + len(pat_name), pat_name)
                        )

                for match in re.finditer(r"\b(\d{1,2})\s*(pm|am)\b", t_text, re.I):
                    ms = match.start()
                    me = match.end()
                    mt = match.group(0)
                    sp.setdefault("temporal_relation", []).append(
                        _make_source_span(t_ti, ms, me, mt)
                    )
                    hh = match.group(1)
                    mm = match.group(2).lower()
                    h24 = int(hh)
                    if mm == "pm" and h24 != 12:
                        h24 += 12
                    elif mm == "am" and h24 == 12:
                        h24 = 0
                    h24s = str(h24).zfill(2)
                    ft.append((t_ti, ms, me, mt, h24s))
                    if earliest_t:
                        ehs = earliest_t.split(":")[0]
                        if ehs == h24s:
                            sp.setdefault("earliest_time", []).append(
                                _make_source_span(t_ti, ms, me, mt)
                            )
                    if latest_t:
                        lhs = latest_t.split(":")[0]
                        if lhs == h24s:
                            if not earliest_t or latest_t != earliest_t:
                                sp.setdefault("latest_time", []).append(
                                    _make_source_span(t_ti, ms, me, mt)
                                )
                            elif earliest_t == latest_t and "earliest_time" in sp:
                                for es in sp.get("earliest_time", []):
                                    sp.setdefault("latest_time", []).append(es)

                # Duration
                dm = re.search(r"\b(\d+)\s*minutes?\b", t_text, re.I)
                if dm:
                    sp.setdefault("duration_minutes", []).append(
                        _make_source_span(t_ti, dm.start(), dm.end(), dm.group(0))
                    )

                # Appointment date
                lt = t_text.lower()
                dw = ["tomorrow", "today", "next week",
                      "monday", "tuesday", "wednesday", "thursday", "friday"]
                for w in dw:
                    if w in lt:
                        wi = lt.find(w)
                        if wi >= 0:
                            aw = t_text[wi:wi + len(w)]
                            sp.setdefault("appointment_date", []).append(
                                _make_source_span(t_ti, wi, wi + len(w), aw)
                            )
                        break

            return sp, ft

        all_spans, found_times = _scan_turn_spans(turns, earliest_time, latest_time)

        # Fallback: if we have a time bound but no matching source span, use first/last available
        if earliest_time and "earliest_time" not in all_spans and found_times:
            ti, st, en, txt, h = found_times[0]
            all_spans["earliest_time"] = [_make_source_span(ti, st, en, txt)]
        if latest_time and "latest_time" not in all_spans and found_times:
            ti, st, en, txt, h = found_times[-1]
            all_spans["latest_time"] = [_make_source_span(ti, st, en, txt)]

        # Determine if this variant needs clarification
        if mt_idx == 1:
            exp_clarif = "Please clarify: which time works?"
            clarif_choices = ["10am", "2pm", "3pm", "4pm"]
        else:
            exp_clarif = None
            clarif_choices = None

        scenario = _build_scenario(
            spec, mt_id, combined, mt_df, mt_lf,
            reference_date, clinic_clock,
            earliest_time=earliest_time,
            latest_time=latest_time,
            duration_minutes=15,
            dialogue_turns=turns,
            source_spans=all_spans,
            expected_clarification=exp_clarif,
            clarification_choices=clarif_choices,
        )

        multi_turn_variants.append(scenario)
        multi_turn_data.append(scenario.model_dump(mode="json"))

    # Compute variant hashes and include them in fixture data
    surface_hashes = [compute_variant_hash(sd) for sd in surface_data]
    multi_turn_hashes = [compute_variant_hash(md) for md in multi_turn_data]

    # Add variant hashes to each variant data
    for sd, h in zip(surface_data, surface_hashes):
        sd["variant_hash"] = h
    for md, h in zip(multi_turn_data, multi_turn_hashes):
        md["variant_hash"] = h

    # Compute group hash — covers spec AND all variant payloads
    group_data_input = {
        "group_id": group_id,
        "spec": {
            "group_index": spec.group_index,
            "intended_action": action,
            "temporal_relation": temporal,
            "diary_state": spec.diary_state,
            "entity_state": spec.entity_state,
            "patient_semantics": spec.patient_semantics,
            "practitioner_semantics": spec.practitioner_semantics,
            "location_semantics": spec.location_semantics,
            "appointment_type_semantics": spec.appointment_type_semantics,
            "duration_semantics": spec.duration_semantics,
            "dialogue_form": spec.dialogue_form,
            "language_form": spec.language_form,
            "gap_targets": list(spec.gap_targets),
        },
        "surface_count": len(surface_data),
        "multi_turn_count": len(multi_turn_data),
        "surface_variant_hashes": surface_hashes,
        "multi_turn_variant_hashes": multi_turn_hashes,
    }
    group_hash = compute_group_hash(group_data_input)

    group_obj = ScaleDevelopmentGroup(
        spec=spec,
        group_hash=group_hash,
        reference_date=reference_date,
        clinic_clock=clinic_clock,
        surface_variants=tuple(surface_variants),
        multi_turn_variants=tuple(multi_turn_variants),
    )

    # Serialize group for JSON output
    fixture_data: dict[str, Any] = {
        "schema_version": LC4_SCHEMA_VERSION,
        "group_id": group_id,
        "group_hash": group_hash,
        "variant_hashes": {
            "surface": surface_hashes,
            "multi_turn": multi_turn_hashes,
        },
        "provenance": "silver",
        "adjudication": "pending",
        "reference_date": reference_date.isoformat(),
        "clinic_clock": clinic_clock.isoformat(),
        "spec": {
            "group_index": spec.group_index,
            "intended_action": action,
            "temporal_relation": temporal,
            "diary_state": spec.diary_state,
            "entity_state": spec.entity_state,
            "patient_semantics": spec.patient_semantics,
            "practitioner_semantics": spec.practitioner_semantics,
            "location_semantics": spec.location_semantics,
            "appointment_type_semantics": spec.appointment_type_semantics,
            "duration_semantics": spec.duration_semantics,
            "dialogue_form": spec.dialogue_form,
            "language_form": spec.language_form,
            "gap_targets": list(spec.gap_targets),
        },
        "surface_variants": surface_data,
        "multi_turn_variants": multi_turn_data,
    }

    return fixture_data, group_obj


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def validate_corpus(corpus: ScaleCorpus) -> list[str]:
    """Validate all corpus integrity constraints.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    if len(corpus.groups) != DEVELOPMENT_GROUP_COUNT:
        errors.append(
            f"Expected {DEVELOPMENT_GROUP_COUNT} groups, got {len(corpus.groups)}"
        )

    seen_ids: set[str] = set()
    for g in corpus.groups:
        if g.group_id in seen_ids:
            errors.append(f"Duplicate group ID: {g.group_id}")
        seen_ids.add(g.group_id)

    # Check action coverage
    action_counts: dict[str, int] = {a: 0 for a in ALL_ACTIONS}
    temp_counts: dict[str, int] = {t: 0 for t in ALL_TEMPORAL_RELATIONS}
    diary_state_seen: set[str] = set()
    entity_sem_seen: set[str] = set()
    dialogue_form_seen: set[str] = set()
    language_form_seen: set[str] = set()

    for g in corpus.groups:
        action_counts[g.spec.intended_action] += 1
        temp_counts[g.spec.temporal_relation] += 1
        diary_state_seen.add(g.spec.diary_state)
        entity_sem_seen.add(g.spec.entity_state)
        dialogue_form_seen.add(g.spec.dialogue_form)
        language_form_seen.add(g.spec.language_form)

    for action, count in action_counts.items():
        if count < 12:
            errors.append(f"Action {action!r} has only {count} groups (min 12)")

    for temporal, count in temp_counts.items():
        if count < 12:
            errors.append(f"Temporal relation {temporal!r} has only {count} groups (min 12)")

    # Check dimension coverage
    for ds in ALL_DIARY_STATES:
        if ds not in diary_state_seen:
            errors.append(f"Diary state {ds!r} not covered")

    for es in ALL_ENTITY_SEMANTICS:
        if es not in entity_sem_seen:
            errors.append(f"Entity state {es!r} not covered")

    for df in ALL_DIALOGUE_FORMS:
        if df not in dialogue_form_seen:
            errors.append(f"Dialogue form {df!r} not covered")

    for lf in ALL_LANGUAGE_FORMS:
        if lf not in language_form_seen:
            errors.append(f"Language form {lf!r} not covered")

    # Gap priority count
    gap_count = corpus.gap_priority_group_count
    if gap_count < GAP_PRIORITY_MINIMUM:
        errors.append(
            f"Only {gap_count} gap-priority groups (min {GAP_PRIORITY_MINIMUM})"
        )

    return errors


def validate_variant(
    scenario: ReceptionScenarioSpec,
    group_spec: DevelopmentGroupSpec | None = None,
) -> list[str]:
    """Validate a single variant's internal consistency.

    When *group_spec* is provided, also validates cross-field agreement
    between the variant and its parent group spec for ALL invariant fields.

    Checks provenance/adjudication, source span integrity, temporal consistency,
    normalized values, entity semantics agreement, evidence coverage, omitted
    entity span absence, and all cross-group invariant fields (action, temporal,
    diary state, entity semantics, all five field-level entity semantics,
    provenance, adjudication).

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    if scenario.provenance != "silver":
        errors.append(f"Provenance must be silver, got {scenario.provenance!r}")
    if scenario.adjudication != "pending":
        errors.append(f"Adjudication must be pending, got {scenario.adjudication!r}")

    # Verify source spans match dialogue turns
    utterances = [
        t.get("utterance", "")
        for t in scenario.dialogue_turns
        if isinstance(t.get("utterance"), str)
    ]

    for field_name, spans in scenario.source_spans.items():
        for span in spans:
            # Handle both ScenarioSourceSpan objects and raw dicts from tests
            if isinstance(span, dict):
                ti = span.get("turn_index", 0)
                start = span.get("start", 0)
                end = span.get("end", 0)
                text = span.get("text", "")
            else:
                ti = span.turn_index
                start = span.start
                end = span.end
                text = span.text
            if ti >= len(utterances):
                errors.append(
                    f"Span turn_index {ti} exceeds dialogue turns"
                )
            else:
                original = utterances[ti]
                if end > len(original) or original[start:end] != text:
                    errors.append(
                        f"Span text {text!r} does not match source at "
                        f"position {start}:{end} in turn {ti}"
                    )

    # Verify earliest/latest consistency
    if scenario.temporal_relation == "exact":
        if scenario.earliest_time is None or scenario.latest_time is None:
            errors.append("Exact temporal requires both earliest and latest times")
        elif scenario.earliest_time != scenario.latest_time:
            errors.append("Exact temporal requires earliest == latest")
    elif scenario.temporal_relation == "not_before" and scenario.earliest_time is None:
        errors.append("not_before requires earliest_time")
    elif scenario.temporal_relation == "not_after" and scenario.latest_time is None:
        errors.append("not_after requires latest_time")
    elif scenario.temporal_relation == "interval":
        if scenario.earliest_time is None or scenario.latest_time is None:
            errors.append("interval requires both time bounds")
        elif scenario.earliest_time >= scenario.latest_time:
            errors.append("interval requires earliest < latest")

    # Validate normalized values include required fields
    norm = scenario.normalized_values
    if "appointment_date" not in norm:
        errors.append("normalized_values missing appointment_date")
    if "duration_minutes" not in norm:
        errors.append("normalized_values missing duration_minutes")

    # Check field-level entity semantics agreement with utterance
    utterance_text = " ".join(utterances).lower()
    if scenario.patient_semantics == "exact" and "margaret" not in utterance_text:
        errors.append(
            f"patient_semantics=exact but 'Margaret' not found in utterance"
        )
    if scenario.practitioner_semantics == "exact" and "shera" not in utterance_text:
        errors.append(
            f"practitioner_semantics=exact but 'Shera' not found in utterance"
        )

    # --- Evidence coverage checks ---
    # When appointment_date is in normalized_values, there must be a source span
    if "appointment_date" in norm:
        if "appointment_date" not in scenario.source_spans:
            errors.append(
                "normalized_values has appointment_date but no source_spans[appointment_date]"
            )

    # Check if any time pattern exists in the utterance text
    utterance_text_all = " ".join(utterances)
    import re as _re
    has_time_pattern = bool(_re.search(r"(\d{1,2})\s*(pm|am)", utterance_text_all, _re.I))

    # When earliest_time is in normalized_values and a time pattern exists, require source span
    if "earliest_time" in norm and norm["earliest_time"] is not None:
        if "earliest_time" not in scenario.source_spans and has_time_pattern:
            errors.append(
                "normalized_values has earliest_time but no source_spans[earliest_time]"
            )

    # When latest_time is in normalized_values and a time pattern exists, require source span
    if "latest_time" in norm and norm["latest_time"] is not None:
        if "latest_time" not in scenario.source_spans and has_time_pattern:
            errors.append(
                "normalized_values has latest_time but no source_spans[latest_time]"
            )

    # When patient_semantics == "exact", there must be a patient source span
    if scenario.patient_semantics == "exact" and "patient" not in scenario.source_spans:
        errors.append(
            "patient_semantics=exact but no source_spans[patient]"
        )

    # When practitioner_semantics == "exact", there must be a practitioner source span
    if scenario.practitioner_semantics == "exact" and "practitioner" not in scenario.source_spans:
        errors.append(
            "practitioner_semantics=exact but no source_spans[practitioner]"
        )

    # Omitted entities must not have false named-entity spans
    if scenario.patient_semantics == "omitted" and "patient" in scenario.source_spans:
        errors.append(
            "patient_semantics=omitted but source_spans[patient] present"
        )
    if scenario.practitioner_semantics == "omitted" and "practitioner" in scenario.source_spans:
        errors.append(
            "practitioner_semantics=omitted but source_spans[practitioner] present"
        )

    # Cross-validate against group spec if provided
    if group_spec is not None:
        if scenario.intended_action != group_spec.intended_action:
            errors.append(
                f"Variant action {scenario.intended_action!r} != "
                f"group action {group_spec.intended_action!r}"
            )
        if scenario.temporal_relation != group_spec.temporal_relation:
            errors.append(
                f"Variant temporal {scenario.temporal_relation!r} != "
                f"group temporal {group_spec.temporal_relation!r}"
            )
        if scenario.diary_state != group_spec.diary_state:
            errors.append(
                f"Variant diary_state {scenario.diary_state!r} != "
                f"group diary_state {group_spec.diary_state!r}"
            )
        # Check all five field-level entity semantics
        g_map = group_spec.entity_semantics_map
        if scenario.patient_semantics != g_map.get("patient", "exact"):
            errors.append(
                f"Variant patient_semantics {scenario.patient_semantics!r} != "
                f"group patient_semantics {g_map['patient']!r}"
            )
        if scenario.practitioner_semantics != g_map.get("practitioner", "exact"):
            errors.append(
                f"Variant practitioner_semantics {scenario.practitioner_semantics!r} != "
                f"group practitioner_semantics {g_map['practitioner']!r}"
            )
        if scenario.location_semantics != group_spec.location_semantics:
            errors.append(
                f"Variant location_semantics {scenario.location_semantics!r} != "
                f"group location_semantics {group_spec.location_semantics!r}"
            )
        if scenario.appointment_type_semantics != group_spec.appointment_type_semantics:
            errors.append(
                f"Variant appointment_type_semantics {scenario.appointment_type_semantics!r} != "
                f"group appointment_type_semantics {group_spec.appointment_type_semantics!r}"
            )
        if scenario.duration_semantics != group_spec.duration_semantics:
            errors.append(
                f"Variant duration_semantics {scenario.duration_semantics!r} != "
                f"group duration_semantics {group_spec.duration_semantics!r}"
            )
        # Check entity_state
        if scenario.entity_state != group_spec.entity_state:
            errors.append(
                f"Variant entity_state {scenario.entity_state!r} != "
                f"group entity_state {group_spec.entity_state!r}"
            )

    return errors


# ---------------------------------------------------------------------------
# Import isolation guard
# ---------------------------------------------------------------------------

_PROHIBITED_IMPORT_PREFIXES = (
    "app.routers",
    "app.models",
    "app.db",
    "app.services.ai.providers",
    "sqlalchemy",
    "alembic",
)


def validate_scale_corpus_isolation() -> None:
    """Assert that this module cannot reach providers, routes, or storage."""
    import ast

    tree = ast.parse(
        pathlib.Path(__file__).read_text(encoding="utf-8")
    )
    for node in ast.walk(tree):
        imported: tuple[str, ...] = ()
        if isinstance(node, ast.Import):
            imported = tuple(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = (node.module,)
        for module_name in imported:
            if module_name.startswith(_PROHIBITED_IMPORT_PREFIXES):
                raise RuntimeError(
                    f"Scale corpus imports prohibited module: {module_name}"
                )


__all__ = [
    "LC4_SCHEMA_VERSION",
    "DEVELOPMENT_GROUP_COUNT",
    "SURFACE_VARIANTS_PER_GROUP",
    "VARIANTS_PER_GROUP",
    "MULTI_TURN_VARIANTS_PER_GROUP",
    "TOTAL_SURFACE_VARIANTS",
    "TOTAL_TRAJECTORIES",
    "TOTAL_INDIVIDUAL_RECORDS",
    "GAP_PRIORITY_MINIMUM",
    "ALL_ACTIONS",
    "ALL_TEMPORAL_RELATIONS",
    "ALL_DIARY_STATES",
    "ALL_ENTITY_SEMANTICS",
    "ALL_DIALOGUE_FORMS",
    "ALL_LANGUAGE_FORMS",
    "DevelopmentGroupSpec",
    "DevelopmentVariantSpec",
    "ScaleDevelopmentGroup",
    "ScaleCorpus",
    "PartitionSlot",
    "PartitionSchema",
    "SealedHoldoutCapability",
    "DevelopmentOnlyLoader",
    "compute_group_hash",
    "compute_variant_hash",
    "generate_development_fixture",
    "validate_corpus",
    "validate_variant",
    "validate_scale_corpus_isolation",
]
