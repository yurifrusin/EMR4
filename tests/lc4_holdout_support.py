"""Sol-owned LC4 protected-holdout authoring and one-shot evaluation support.

This module is deliberately test/tooling-only. Product modules and default
development loaders must never import it. The real holdout was authored only
after all external LC4 implementation and review lanes ended.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    score_interpretation_replay_pair,
)
from app.services.bernie.composed_evaluator import build_corpus_summary
from app.services.bernie.scale_corpus import (
    ALL_ACTIONS,
    ALL_DIALOGUE_FORMS,
    ALL_DIARY_STATES,
    ALL_ENTITY_SEMANTICS,
    ALL_LANGUAGE_FORMS,
    ALL_TEMPORAL_RELATIONS,
    DevelopmentGroupSpec,
    _apply_entity_semantics,
    _build_scenario,
    compute_group_hash,
    compute_variant_hash,
)
from app.services.bernie.scaled_evaluator import (
    EXPECTED_ADJUDICATED_GAPS,
    EXPECTED_LC1_GOLD_CELLS,
    SealedHoldoutReceipt,
    SingleUseLedger,
    _build_per_dimension_scores,
    _build_slices,
    compute_sanitized_holdout_hash,
    compute_variance,
    sanitize_holdout_report,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec


HOLDOUT_SCHEMA_VERSION = "lc4.holdout.corpus.v1"
HOLDOUT_REPORT_SCHEMA_VERSION = "lc4.holdout.aggregate.v1"
HOLDOUT_SEAL_SCHEMA_VERSION = "lc4.holdout.seal.v1"
HOLDOUT_VERSION = "lc4-holdout-v1"
HOLDOUT_GROUP_COUNT = 24
HOLDOUT_SURFACE_PER_GROUP = 9
HOLDOUT_MULTI_TURN_PER_GROUP = 3
HOLDOUT_VARIANTS_PER_GROUP = 12
HOLDOUT_TOTAL_VARIANTS = 288
HOLDOUT_TOTAL_TRAJECTORIES = 72
HOLDOUT_REPEATS = 2
HOLDOUT_TOTAL_SAMPLES = 576
HOLDOUT_PURPOSE = "sealed_baseline_evaluation"
HOLDOUT_EVALUATOR_IDENTITY = "protected-gpt-sol"
HOLDOUT_EVALUATION_ID = "lc4-holdout-v1-baseline-001"
HOLDOUT_GROUP_PREFIX = "lc4_sol_holdout_group"
HOLDOUT_VARIANT_PREFIX = "lc4_sol_holdout_var"
HOLDOUT_MT_PREFIX = "lc4_sol_holdout_mt"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _stable_hash(value: Any) -> str:
    encoded = value if isinstance(value, str) else _canonical_json(value)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class HoldoutBlueprint:
    index: int
    action: str
    temporal_relation: str
    diary_state: str
    entity_state: str
    dialogue_form: str
    language_form: str
    patient_name: str
    practitioner_name: str

    @property
    def group_id(self) -> str:
        return f"{HOLDOUT_GROUP_PREFIX}_{self.index:03d}"

    @property
    def patient_semantics(self) -> str:
        if self.action == "explain_schedule":
            return "omitted"
        return {
            "exact": "exact",
            "ambiguous": "ambiguous",
            "omitted": "omitted",
            "corrected": "corrected",
            "negated": "exact",
            "mismatched": "mismatched",
        }[self.entity_state]

    @property
    def practitioner_semantics(self) -> str:
        return "negated" if self.entity_state == "negated" else "exact"

    @property
    def gap_targets(self) -> tuple[str, ...]:
        targets = ["interpretation_replay_tool_selection"]
        if self.dialogue_form == "clarification":
            targets.append("clarification_dialogue")
        if self.temporal_relation in ("interval", "unspecified"):
            targets.append("interval_unspecified_temporal")
        if self.entity_state in ("ambiguous", "omitted", "corrected"):
            targets.append("entity_ambiguity_omission_correction")
        return tuple(targets)

    def development_spec(self) -> DevelopmentGroupSpec:
        return DevelopmentGroupSpec(
            group_index=self.index,
            intended_action=self.action,
            temporal_relation=self.temporal_relation,
            diary_state=self.diary_state,
            entity_state=self.entity_state,
            patient_semantics=self.patient_semantics,
            practitioner_semantics=self.practitioner_semantics,
            location_semantics="omitted",
            appointment_type_semantics="omitted",
            duration_semantics="exact",
            dialogue_form=self.dialogue_form,
            language_form=self.language_form,
            gap_targets=self.gap_targets,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "group_index": self.index,
            "intended_action": self.action,
            "temporal_relation": self.temporal_relation,
            "diary_state": self.diary_state,
            "entity_state": self.entity_state,
            "patient_semantics": self.patient_semantics,
            "practitioner_semantics": self.practitioner_semantics,
            "location_semantics": "omitted",
            "appointment_type_semantics": "omitted",
            "duration_semantics": "exact",
            "dialogue_form": self.dialogue_form,
            "language_form": self.language_form,
            "gap_targets": list(self.gap_targets),
            "patient_name": self.patient_name,
            "practitioner_name": self.practitioner_name,
        }


@dataclass(frozen=True)
class HoldoutGroup:
    blueprint: HoldoutBlueprint
    group_hash: str
    surface_variants: tuple[ReceptionScenarioSpec, ...]
    multi_turn_variants: tuple[ReceptionScenarioSpec, ...]

    @property
    def all_variants(self) -> tuple[ReceptionScenarioSpec, ...]:
        return self.surface_variants + self.multi_turn_variants


@dataclass(frozen=True)
class HoldoutCorpus:
    groups: tuple[HoldoutGroup, ...]
    corpus_hash: str
    manifest_hash: str

    def all_variants(self) -> list[ReceptionScenarioSpec]:
        return [variant for group in self.groups for variant in group.all_variants]


def authored_blueprints() -> tuple[HoldoutBlueprint, ...]:
    """Return the 24 Sol-authored semantic blueprints in stable order."""
    actions = [action for action in ALL_ACTIONS for _ in range(4)]
    temporals = list(ALL_TEMPORAL_RELATIONS) * 4
    names = (
        ("Aisha Rahman", "Dr Nguyen"),
        ("Leo Bennett", "Dr Okafor"),
        ("Mei Lin", "Dr Kovacs"),
        ("Noah Williams", "Dr Iqbal"),
        ("Priya Nair", "Dr Mensah"),
        ("Tom Alvarez", "Dr Chen"),
    )
    blueprints: list[HoldoutBlueprint] = []
    for offset in range(HOLDOUT_GROUP_COUNT):
        patient, practitioner = names[offset % len(names)]
        blueprints.append(HoldoutBlueprint(
            index=offset + 1,
            action=actions[offset],
            temporal_relation=temporals[(offset * 5) % len(temporals)],
            diary_state=ALL_DIARY_STATES[(offset * 7) % len(ALL_DIARY_STATES)],
            entity_state=ALL_ENTITY_SEMANTICS[(offset * 5) % len(ALL_ENTITY_SEMANTICS)],
            dialogue_form=ALL_DIALOGUE_FORMS[(offset * 3) % len(ALL_DIALOGUE_FORMS)],
            language_form=ALL_LANGUAGE_FORMS[(offset * 5) % len(ALL_LANGUAGE_FORMS)],
            patient_name=patient,
            practitioner_name=practitioner,
        ))
    return tuple(blueprints)


def _temporal_surface(relation: str) -> tuple[str, str | None, str | None]:
    return {
        "exact": ("Wednesday at 11am", "11:00", "11:00"),
        "not_before": ("Wednesday no earlier than 11am", "11:00", None),
        "not_after": ("Wednesday by 5pm", None, "17:00"),
        "interval": ("Wednesday between 10am and 1pm", "10:00", "13:00"),
        "approximate": ("Wednesday around 2pm", "14:00", "14:00"),
        "unspecified": ("sometime Wednesday", None, None),
    }[relation]


def _action_clause(
    blueprint: HoldoutBlueprint,
    temporal_text: str,
    duration_minutes: int,
) -> str:
    patient = blueprint.patient_name
    practitioner = blueprint.practitioner_name
    duration = f"{duration_minutes} minutes"
    action = blueprint.action
    if action == "create":
        clause = f"arrange a {duration} visit for {patient} with {practitioner} {temporal_text}"
    elif action == "move":
        clause = f"shift {patient}'s {duration} visit with {practitioner} to {temporal_text}"
    elif action == "resize":
        clause = f"change {patient}'s visit with {practitioner} to {duration} {temporal_text}"
    elif action == "cancel":
        clause = f"remove {patient}'s {duration} booking with {practitioner} {temporal_text}"
    elif action == "status_change":
        clause = f"record {patient} as arrived for the {duration} visit with {practitioner} {temporal_text}"
    else:
        clause = f"summarise {practitioner}'s diary {temporal_text}"

    clause = _apply_entity_semantics(
        clause,
        blueprint.patient_semantics,
        blueprint.practitioner_semantics,
        patient_name=patient,
        practitioner_name=practitioner,
    )
    if blueprint.entity_state == "corrected" and blueprint.action != "explain_schedule":
        clause = f"Correction noted: use {clause}"
    return clause


_SURFACE_FRAMES = (
    "Please {clause}.",
    "Could you {clause}, please?",
    "Reception note — {clause}.",
    "When you have a moment, {clause}.",
    "Quick diary job: {clause}.",
    "I need the diary updated to {clause}.",
    "For the front desk list, {clause}.",
    "Can we {clause}?",
    "Instruction: {clause}.",
)


def _make_surface_text(blueprint: HoldoutBlueprint, variant_index: int) -> str:
    temporal_text, _, _ = _temporal_surface(blueprint.temporal_relation)
    duration = 30 if blueprint.action == "resize" else 15
    clause = _action_clause(blueprint, temporal_text, duration)
    text = _SURFACE_FRAMES[variant_index - 1].format(clause=clause)
    if variant_index == 5:
        text = text.replace("appointment", "appt").replace("minutes", "mins")
    elif variant_index == 6:
        text = f"Um, {text[0].lower()}{text[1:]}"
    elif variant_index == 7:
        text = text.replace(" — ", ": ")
    elif variant_index == 8:
        text = text.replace("please", "pls")
    elif variant_index == 9:
        text = f"{text} Do not bypass staff confirmation."
    return text


def _make_multi_turns(blueprint: HoldoutBlueprint, variant_index: int) -> list[dict[str, Any]]:
    temporal_text, _, _ = _temporal_surface(blueprint.temporal_relation)
    duration = 30 if blueprint.action == "resize" else 15
    clause = _action_clause(blueprint, temporal_text, duration)
    patient = blueprint.patient_name
    practitioner = blueprint.practitioner_name
    if blueprint.action == "explain_schedule":
        context = f"{practitioner}'s diary"
    else:
        context = f"{patient}'s booking with {practitioner}"
        context = _apply_entity_semantics(
            context,
            blueprint.patient_semantics,
            blueprint.practitioner_semantics,
            patient_name=patient,
            practitioner_name=practitioner,
        )
        if blueprint.entity_state == "corrected":
            context = f"Robert Johnson's booking with {practitioner}"
    if variant_index == 1:
        return [
            {"turn": 1, "utterance": f"I need help with {context}."},
            {"turn": 2, "utterance": f"Specifically, please {clause}."},
        ]
    if variant_index == 2:
        return [
            {"turn": 1, "utterance": f"Please handle {context} Tuesday at 9am."},
            {"turn": 2, "utterance": f"Correction: {clause}, not the earlier detail."},
        ]
    return [
        {"turn": 1, "utterance": f"For {context}, I have a diary request."},
        {"turn": 2, "utterance": f"That one: {clause}."},
        {"turn": 3, "utterance": "Keep it as a proposal for staff review; do not claim it is completed."},
    ]


def _promote_to_authored_gold(
    scenario: ReceptionScenarioSpec,
    *,
    scenario_id: str,
    family: str,
    description: str,
) -> ReceptionScenarioSpec:
    payload = scenario.model_dump(mode="json")
    payload.update({
        "scenario_id": scenario_id,
        "provenance": "gold",
        "adjudication": "adjudicated",
        "family": family,
        "description": description,
    })
    return ReceptionScenarioSpec.model_validate(payload)


def _build_group(
    blueprint: HoldoutBlueprint,
    reference_date: date,
    clinic_clock: datetime,
) -> tuple[dict[str, Any], HoldoutGroup]:
    spec = blueprint.development_spec()
    temporal_text, earliest, latest = _temporal_surface(blueprint.temporal_relation)
    duration = 30 if blueprint.action == "resize" else 15
    appointment_date = (reference_date + timedelta(days=1)).isoformat()
    surface: list[ReceptionScenarioSpec] = []
    multi: list[ReceptionScenarioSpec] = []

    for variant_index in range(1, HOLDOUT_SURFACE_PER_GROUP + 1):
        text = _make_surface_text(blueprint, variant_index)
        base = _build_scenario(
            spec,
            f"temporary-surface-{blueprint.index}-{variant_index}",
            text,
            "one_shot",
            ALL_LANGUAGE_FORMS[(blueprint.index * 2 + variant_index) % len(ALL_LANGUAGE_FORMS)],
            reference_date,
            clinic_clock,
            earliest_time=earliest,
            latest_time=latest,
            duration_minutes=duration,
            appointment_date=appointment_date,
            patient_name=blueprint.patient_name,
            practitioner_name=blueprint.practitioner_name,
        )
        surface.append(_promote_to_authored_gold(
            base,
            scenario_id=f"{HOLDOUT_VARIANT_PREFIX}_{blueprint.index:03d}_{variant_index:02d}",
            family=blueprint.group_id,
            description=f"authored holdout surface {blueprint.index:03d}/{variant_index:02d}",
        ))

    multi_forms = ("clarification", "correction", "anaphora")
    for variant_index in range(1, HOLDOUT_MULTI_TURN_PER_GROUP + 1):
        turns = _make_multi_turns(blueprint, variant_index)
        combined = " ".join(turn["utterance"] for turn in turns)
        base = _build_scenario(
            spec,
            f"temporary-multi-{blueprint.index}-{variant_index}",
            combined,
            multi_forms[variant_index - 1],
            ALL_LANGUAGE_FORMS[(blueprint.index + variant_index * 3) % len(ALL_LANGUAGE_FORMS)],
            reference_date,
            clinic_clock,
            earliest_time=earliest,
            latest_time=latest,
            duration_minutes=duration,
            appointment_date=appointment_date,
            patient_name=blueprint.patient_name,
            practitioner_name=blueprint.practitioner_name,
            dialogue_turns=turns,
            expected_clarification=(
                "Please clarify the final diary instruction."
                if variant_index == 1 else None
            ),
            clarification_choices=(
                ["confirm the date", "confirm the time", "confirm the person"]
                if variant_index == 1 else None
            ),
        )
        multi.append(_promote_to_authored_gold(
            base,
            scenario_id=f"{HOLDOUT_MT_PREFIX}_{blueprint.index:03d}_{variant_index:02d}",
            family=blueprint.group_id,
            description=f"authored holdout trajectory {blueprint.index:03d}/{variant_index:02d}",
        ))

    surface_data = [scenario.model_dump(mode="json") for scenario in surface]
    multi_data = [scenario.model_dump(mode="json") for scenario in multi]
    surface_hashes = [compute_variant_hash(item) for item in surface_data]
    multi_hashes = [compute_variant_hash(item) for item in multi_data]
    for item, item_hash in zip(surface_data, surface_hashes):
        item["variant_hash"] = item_hash
    for item, item_hash in zip(multi_data, multi_hashes):
        item["variant_hash"] = item_hash

    group_hash_payload = {
        "group_id": blueprint.group_id,
        "spec": blueprint.as_dict(),
        "surface_count": len(surface_data),
        "multi_turn_count": len(multi_data),
        "surface_variant_hashes": surface_hashes,
        "multi_turn_variant_hashes": multi_hashes,
    }
    group_hash = compute_group_hash(group_hash_payload)
    fixture = {
        "schema_version": HOLDOUT_SCHEMA_VERSION,
        "holdout_version": HOLDOUT_VERSION,
        "group_id": blueprint.group_id,
        "group_hash": group_hash,
        "provenance": "gold",
        "adjudication": "adjudicated",
        "author_identity": HOLDOUT_EVALUATOR_IDENTITY,
        "generator_identity": None,
        "reference_date": reference_date.isoformat(),
        "clinic_clock": clinic_clock.isoformat(),
        "spec": blueprint.as_dict(),
        "variant_hashes": {"surface": surface_hashes, "multi_turn": multi_hashes},
        "surface_variants": surface_data,
        "multi_turn_variants": multi_data,
    }
    return fixture, HoldoutGroup(
        blueprint=blueprint,
        group_hash=group_hash,
        surface_variants=tuple(surface),
        multi_turn_variants=tuple(multi),
    )


def author_holdout_fixture(output_dir: Path, seal_receipt_path: Path) -> HoldoutCorpus:
    """Create and seal v1. Refuses to overwrite any existing holdout."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Refusing to overwrite an existing holdout fixture")
    if seal_receipt_path.exists():
        raise ValueError("Refusing to overwrite an existing holdout seal receipt")
    output_dir.mkdir(parents=True, exist_ok=False)
    seal_receipt_path.parent.mkdir(parents=True, exist_ok=True)
    reference_date = date(2026, 7, 14)
    clinic_clock = datetime(2026, 7, 14, 9, 0, tzinfo=timezone(timedelta(hours=10)))
    groups: list[HoldoutGroup] = []
    entries: list[dict[str, Any]] = []
    for blueprint in authored_blueprints():
        fixture, group = _build_group(blueprint, reference_date, clinic_clock)
        filename = f"{blueprint.group_id}.json"
        (output_dir / filename).write_text(
            json.dumps(fixture, indent=2) + "\n", encoding="utf-8"
        )
        groups.append(group)
        entries.append({
            "group_index": blueprint.index,
            "group_id": blueprint.group_id,
            "filename": filename,
            "group_hash": group.group_hash,
            "surface_variant_count": HOLDOUT_SURFACE_PER_GROUP,
            "multi_turn_count": HOLDOUT_MULTI_TURN_PER_GROUP,
        })

    corpus_hash = _stable_hash([entry["group_hash"] for entry in entries])
    manifest_without_hash = {
        "schema_version": HOLDOUT_SCHEMA_VERSION,
        "holdout_version": HOLDOUT_VERSION,
        "partition": "holdout",
        "provenance": "gold",
        "adjudication": "adjudicated",
        "author_identity": HOLDOUT_EVALUATOR_IDENTITY,
        "generator_identity": None,
        "authority_grant": {
            "provider_write": False,
            "diary_write": False,
            "confirmation": False,
            "override_authority": False,
        },
        "total_groups": HOLDOUT_GROUP_COUNT,
        "surface_variants_per_group": HOLDOUT_SURFACE_PER_GROUP,
        "multi_turn_per_group": HOLDOUT_MULTI_TURN_PER_GROUP,
        "total_variants": HOLDOUT_TOTAL_VARIANTS,
        "total_trajectories": HOLDOUT_TOTAL_TRAJECTORIES,
        "corpus_hash": corpus_hash,
        "groups": entries,
    }
    manifest_hash = _stable_hash(manifest_without_hash)
    manifest = {**manifest_without_hash, "manifest_hash": manifest_hash}
    (output_dir / "lc4_holdout_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    receipt = {
        "schema_version": HOLDOUT_SEAL_SCHEMA_VERSION,
        "holdout_version": HOLDOUT_VERSION,
        "manifest_hash": manifest_hash,
        "purpose": HOLDOUT_PURPOSE,
        "evaluator_identity": HOLDOUT_EVALUATOR_IDENTITY,
        "evaluation_id": HOLDOUT_EVALUATION_ID,
        "is_sealed": True,
        "consumed": False,
        "created_on": "2026-07-14",
        "consumed_on": None,
        "report_hash": None,
    }
    seal_receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return HoldoutCorpus(tuple(groups), corpus_hash, manifest_hash)


def _blueprint_from_dict(value: dict[str, Any]) -> HoldoutBlueprint:
    return HoldoutBlueprint(
        index=value["group_index"],
        action=value["intended_action"],
        temporal_relation=value["temporal_relation"],
        diary_state=value["diary_state"],
        entity_state=value["entity_state"],
        dialogue_form=value["dialogue_form"],
        language_form=value["language_form"],
        patient_name=value["patient_name"],
        practitioner_name=value["practitioner_name"],
    )


def _validate_holdout_variant(
    scenario: ReceptionScenarioSpec,
    blueprint: HoldoutBlueprint,
) -> None:
    expected = blueprint.development_spec()
    errors: list[str] = []
    if scenario.provenance != "gold" or scenario.adjudication != "adjudicated":
        errors.append("holdout variants must be Gold/adjudicated")
    if scenario.family != blueprint.group_id:
        errors.append("variant family does not match holdout group")
    invariants = {
        "intended_action": expected.intended_action,
        "temporal_relation": expected.temporal_relation,
        "diary_state": expected.diary_state,
        "entity_state": expected.entity_state,
        "patient_semantics": expected.patient_semantics,
        "practitioner_semantics": expected.practitioner_semantics,
        "location_semantics": expected.location_semantics,
        "appointment_type_semantics": expected.appointment_type_semantics,
        "duration_semantics": expected.duration_semantics,
    }
    for field_name, expected_value in invariants.items():
        if getattr(scenario, field_name) != expected_value:
            errors.append(f"{field_name} does not match authored blueprint")
    if "appointment_date" not in scenario.normalized_values:
        errors.append("normalized appointment date missing")
    if "duration_minutes" not in scenario.normalized_values:
        errors.append("normalized duration missing")
    if "appointment_date" not in scenario.source_spans:
        errors.append("appointment date has no lossless source span")
    if scenario.patient_semantics == "exact" and "patient" not in scenario.source_spans:
        errors.append("exact patient has no lossless source span")
    if scenario.patient_semantics == "omitted" and "patient" in scenario.source_spans:
        errors.append("omitted patient has a named source span")
    if scenario.practitioner_semantics == "exact" and "practitioner" not in scenario.source_spans:
        errors.append("exact practitioner has no lossless source span")
    if scenario.practitioner_semantics == "omitted" and "practitioner" in scenario.source_spans:
        errors.append("omitted practitioner has a named source span")
    if any(tool in scenario.expected_tool_sequence for tool in scenario.forbidden_tool_calls):
        errors.append("expected tool sequence intersects forbidden tools")
    if errors:
        raise ValueError(f"Invalid holdout variant {scenario.scenario_id}: {'; '.join(errors)}")


def load_sealed_holdout(
    fixture_dir: Path,
    *,
    capability: SealedHoldoutReceipt,
    ledger: SingleUseLedger,
) -> HoldoutCorpus:
    manifest_path = fixture_dir / "lc4_holdout_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    claimed_hash = manifest.get("manifest_hash", "")
    manifest_without_hash = {key: value for key, value in manifest.items() if key != "manifest_hash"}
    if claimed_hash != _stable_hash(manifest_without_hash):
        raise ValueError("Holdout manifest hash mismatch")
    if not ledger.consume(
        claimed_hash,
        HOLDOUT_PURPOSE,
        evaluator_identity=HOLDOUT_EVALUATOR_IDENTITY,
        evaluation_id=HOLDOUT_EVALUATION_ID,
    ):
        raise ValueError("Holdout capability rejected or already consumed")
    if capability != ledger.capability:
        raise ValueError("Holdout capability and ledger do not match")

    groups: list[HoldoutGroup] = []
    seen_group_ids: set[str] = set()
    seen_variant_ids: set[str] = set()
    referenced_files: set[str] = set()
    for entry in manifest.get("groups", []):
        filename = entry["filename"]
        referenced_files.add(filename)
        raw = json.loads((fixture_dir / filename).read_text(encoding="utf-8"))
        blueprint = _blueprint_from_dict(raw["spec"])
        if raw["group_id"] != blueprint.group_id or raw["group_id"] in seen_group_ids:
            raise ValueError("Duplicate or mismatched holdout group ID")
        seen_group_ids.add(raw["group_id"])
        if raw.get("generator_identity") is not None:
            raise ValueError("Holdout must not have a provider-model generator")
        if raw.get("provenance") != "gold" or raw.get("adjudication") != "adjudicated":
            raise ValueError("Holdout group must be Gold/adjudicated")

        surface: list[ReceptionScenarioSpec] = []
        multi: list[ReceptionScenarioSpec] = []
        for bucket_name, target in (("surface_variants", surface), ("multi_turn_variants", multi)):
            for encoded in raw[bucket_name]:
                claimed_variant_hash = encoded.get("variant_hash", "")
                if claimed_variant_hash != compute_variant_hash(encoded):
                    raise ValueError("Holdout variant hash mismatch")
                clean = {key: value for key, value in encoded.items() if key != "variant_hash"}
                scenario = ReceptionScenarioSpec.model_validate(clean)
                if scenario.scenario_id in seen_variant_ids:
                    raise ValueError("Duplicate holdout variant ID")
                seen_variant_ids.add(scenario.scenario_id)
                _validate_holdout_variant(scenario, blueprint)
                target.append(scenario)

        surface_hashes = [item["variant_hash"] for item in raw["surface_variants"]]
        multi_hashes = [item["variant_hash"] for item in raw["multi_turn_variants"]]
        group_hash_payload = {
            "group_id": raw["group_id"],
            "spec": raw["spec"],
            "surface_count": len(surface),
            "multi_turn_count": len(multi),
            "surface_variant_hashes": surface_hashes,
            "multi_turn_variant_hashes": multi_hashes,
        }
        if raw["group_hash"] != compute_group_hash(group_hash_payload):
            raise ValueError("Holdout group hash mismatch")
        if raw["group_hash"] != entry["group_hash"]:
            raise ValueError("Manifest/group hash mismatch")
        groups.append(HoldoutGroup(blueprint, raw["group_hash"], tuple(surface), tuple(multi)))

    actual_files = {
        path.name for path in fixture_dir.glob("*.json")
        if path.name != "lc4_holdout_manifest.json"
    }
    if actual_files != referenced_files:
        raise ValueError("Holdout contains missing or unreferenced group files")
    groups.sort(key=lambda group: group.blueprint.index)
    if len(groups) != HOLDOUT_GROUP_COUNT:
        raise ValueError("Holdout group count mismatch")
    if len(seen_variant_ids) != HOLDOUT_TOTAL_VARIANTS:
        raise ValueError("Holdout variant count mismatch")
    corpus_hash = _stable_hash([group.group_hash for group in groups])
    if corpus_hash != manifest["corpus_hash"]:
        raise ValueError("Holdout corpus hash mismatch")
    return HoldoutCorpus(tuple(groups), corpus_hash, claimed_hash)


def _coverage_lattice(scenarios: list[ReceptionScenarioSpec]) -> dict[str, int]:
    prior = {
        ("create", "exact_duplicate", "exact", "exact", "one_shot", "plain"),
        ("create", "overlap", "exact", "exact", "one_shot", "paraphrase"),
        ("explain_schedule", "empty", "exact", "unspecified", "clarification", "plain"),
    }
    holdout = {
        (
            scenario.intended_action,
            scenario.diary_state,
            scenario.entity_state,
            scenario.temporal_relation,
            scenario.dialogue_form,
            scenario.language_form,
        )
        for scenario in scenarios
    }
    total = 152064
    combined = prior | holdout
    return {
        "total_lattice_cells": total,
        "prior_adjudicated_covered_cell_count": len(prior),
        "holdout_covered_cell_count": len(holdout),
        "holdout_new_cell_count": len(holdout - prior),
        "combined_adjudicated_covered_cell_count": len(combined),
        "combined_adjudicated_empty_cell_count": total - len(combined),
    }


def evaluate_holdout_corpus(corpus: HoldoutCorpus) -> dict[str, Any]:
    scenarios = corpus.all_variants()
    results = []
    for scenario in scenarios:
        for sample_index in range(HOLDOUT_REPEATS):
            interpretation = deterministic_interpret(scenario)
            interpretation = interpretation.__class__(
                scenario_id=interpretation.scenario_id,
                sample_index=sample_index,
                intended_action=interpretation.intended_action,
                action_semantics=interpretation.action_semantics,
                temporal_relation=interpretation.temporal_relation,
                normalized_values=interpretation.normalized_values,
                entity_semantics=interpretation.entity_semantics,
                requires_clarification=interpretation.requires_clarification,
                clarification_choices=interpretation.clarification_choices,
                selected_tool_sequence=interpretation.selected_tool_sequence,
                authority_claim=interpretation.authority_claim,
                claims_action_completed=interpretation.claims_action_completed,
            )
            replay = deterministic_replay(scenario, interpretation)
            results.append(score_interpretation_replay_pair(scenario, interpretation, replay))
    if len(results) != HOLDOUT_TOTAL_SAMPLES:
        raise ValueError("Holdout sample count mismatch")
    summary = build_corpus_summary(results, scenarios)
    per_dimension = _build_per_dimension_scores(
        results, HOLDOUT_TOTAL_VARIANTS, HOLDOUT_TOTAL_SAMPLES, HOLDOUT_REPEATS
    )
    report = {
        "schema_version": HOLDOUT_REPORT_SCHEMA_VERSION,
        "sealed_receipt": {
            "manifest_hash": corpus.manifest_hash,
            "purpose": HOLDOUT_PURPOSE,
            "evaluator_identity": HOLDOUT_EVALUATOR_IDENTITY,
            "evaluation_id": HOLDOUT_EVALUATION_ID,
            "is_sealed": True,
        },
        "partition": "holdout",
        "corpus_hash": corpus.corpus_hash,
        "manifest_hash": corpus.manifest_hash,
        "total_groups": HOLDOUT_GROUP_COUNT,
        "total_variants": HOLDOUT_TOTAL_VARIANTS,
        "total_trajectories": HOLDOUT_TOTAL_TRAJECTORIES,
        "total_samples": HOLDOUT_TOTAL_SAMPLES,
        "repeat_count": HOLDOUT_REPEATS,
        "aggregate": copy.deepcopy(per_dimension["aggregate"]),
        "per_dimension": per_dimension,
        "critical_slices": _build_slices(results, scenarios, summary),
        "variance": compute_variance(results),
        "coverage_lattice": _coverage_lattice(scenarios),
    }
    sanitize_holdout_report(report)
    report["report_hash"] = compute_sanitized_holdout_hash(report)
    sanitize_holdout_report(report)
    return report


def evaluate_once(
    fixture_dir: Path,
    seal_receipt_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    receipt = json.loads(seal_receipt_path.read_text(encoding="utf-8"))
    if receipt.get("consumed") is not False:
        raise ValueError("Holdout baseline evaluation has already been consumed")
    capability = SealedHoldoutReceipt(
        manifest_hash=receipt["manifest_hash"],
        evaluator_identity=receipt["evaluator_identity"],
        evaluation_id=receipt["evaluation_id"],
        is_sealed=receipt["is_sealed"],
    )
    ledger = SingleUseLedger(capability)
    corpus = load_sealed_holdout(fixture_dir, capability=capability, ledger=ledger)
    report = evaluate_holdout_corpus(corpus)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    receipt.update({
        "consumed": True,
        "consumed_on": "2026-07-14",
        "report_hash": report["report_hash"],
    })
    seal_receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return report


def verify_sealed_artifacts(
    fixture_dir: Path,
    seal_receipt_path: Path,
    report_path: Path,
) -> None:
    """Verify committed hashes/aggregates without re-consuming or re-evaluating."""
    manifest = json.loads((fixture_dir / "lc4_holdout_manifest.json").read_text(encoding="utf-8"))
    manifest_without_hash = {key: value for key, value in manifest.items() if key != "manifest_hash"}
    if manifest["manifest_hash"] != _stable_hash(manifest_without_hash):
        raise ValueError("Committed holdout manifest hash mismatch")
    receipt = json.loads(seal_receipt_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if receipt.get("consumed") is not True:
        raise ValueError("Committed holdout receipt is not consumed")
    if receipt.get("manifest_hash") != manifest["manifest_hash"]:
        raise ValueError("Seal receipt manifest hash mismatch")
    if receipt.get("report_hash") != report.get("report_hash"):
        raise ValueError("Seal receipt report hash mismatch")
    claimed = report.get("report_hash")
    if claimed != compute_sanitized_holdout_hash(report):
        raise ValueError("Committed holdout report hash mismatch")
    sanitize_holdout_report(report)
    if report["total_groups"] != HOLDOUT_GROUP_COUNT:
        raise ValueError("Committed holdout group count mismatch")
    if report["total_variants"] != HOLDOUT_TOTAL_VARIANTS:
        raise ValueError("Committed holdout variant count mismatch")
    if report["total_trajectories"] != HOLDOUT_TOTAL_TRAJECTORIES:
        raise ValueError("Committed holdout trajectory count mismatch")
    if report["aggregate"]["total"] != HOLDOUT_TOTAL_SAMPLES:
        raise ValueError("Committed holdout sample count mismatch")


__all__ = [
    "HOLDOUT_EVALUATION_ID",
    "HOLDOUT_EVALUATOR_IDENTITY",
    "HOLDOUT_GROUP_COUNT",
    "HOLDOUT_MULTI_TURN_PER_GROUP",
    "HOLDOUT_REPEATS",
    "HOLDOUT_SCHEMA_VERSION",
    "HOLDOUT_SURFACE_PER_GROUP",
    "HOLDOUT_TOTAL_SAMPLES",
    "HOLDOUT_TOTAL_TRAJECTORIES",
    "HOLDOUT_TOTAL_VARIANTS",
    "HOLDOUT_VERSION",
    "HoldoutCorpus",
    "HoldoutGroup",
    "author_holdout_fixture",
    "authored_blueprints",
    "evaluate_holdout_corpus",
    "evaluate_once",
    "load_sealed_holdout",
    "verify_sealed_artifacts",
]
