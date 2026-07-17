"""Development-only seed and candidate contracts for noisy Bernie language.

The module exposes semantic anchors from the ordinary LC4 development corpus
without exporting source utterances.  It never reads a protected holdout and
grants no provider, confirmation, diary-write, or runtime authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from app.services.bernie.corpus_tier import compute_scenario_hash
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader


SEED_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_seed.v1"
SEED_MANIFEST_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_seed_manifest.v1"
SEED_COUNT = 96
DEFAULT_SEED_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/semantic_seeds.json"
)
CANDIDATE_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_candidate.v1"
CANDIDATES_PER_LANE = 192
ALLOWED_NOISE_OPERATIONS = frozenset(
    {
        "filler",
        "abbreviation",
        "typo",
        "punctuation_case",
        "speech_disfluency",
        "reordered_slots",
        "ellipsis",
        "anaphora",
        "correction",
        "reversal",
        "temporal_surface",
        "staff_shorthand",
        "dictation_artifact",
        "distractor",
    }
)
_CANDIDATE_KEYS = frozenset(
    {
        "schema_version",
        "candidate_id",
        "source_seed_id",
        "source_seed_hash",
        "generator_identity",
        "variant_index",
        "noise_level",
        "noise_operations",
        "dialogue_turns",
        "evidence_spans",
        "semantic_change",
        "provenance",
        "adjudication",
        "authority_grant",
    }
)
_AUTHORITY_FALSE = {
    "provider_write": False,
    "diary_write": False,
    "confirmation": False,
    "override_authority": False,
}
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_URL_RE = re.compile(r"\b(?:https?://|www\.)\S+", re.I)
_AU_PHONE_RE = re.compile(r"(?<!\d)(?:\+?61\s?[2-478]|0[2-478])(?:[\s-]?\d){8}(?!\d)")
_LONG_IDENTIFIER_RE = re.compile(r"(?<!\d)\d{10,}(?!\d)")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _surface_evidence(scenario: Any) -> dict[str, list[str]]:
    """Return synthetic source tokens without returning source utterances."""

    evidence: dict[str, list[str]] = {}
    for field_name, spans in sorted(scenario.source_spans.items()):
        values: list[str] = []
        for span in spans:
            if span.text not in values:
                values.append(span.text)
        evidence[field_name] = values
    return evidence


def _representative_for_group(group: Any) -> Any:
    if group.spec.dialogue_form != "one_shot" and group.multi_turn_variants:
        return group.multi_turn_variants[0]
    return group.surface_variants[0]


def build_semantic_seed_manifest() -> dict[str, Any]:
    """Build 96 dialogue-free semantic anchors from ordinary development."""

    corpus = DevelopmentOnlyLoader().load_all()
    seeds: list[dict[str, Any]] = []

    for index, group in enumerate(corpus.groups, start=1):
        scenario = _representative_for_group(group)
        semantic_contract = {
            "reference_date": scenario.reference_date.isoformat(),
            "clinic_clock": scenario.clinic_clock.isoformat(),
            "intended_action": scenario.intended_action,
            "action_semantics": scenario.action_semantics,
            "temporal_relation": scenario.temporal_relation,
            "earliest_time": scenario.earliest_time,
            "latest_time": scenario.latest_time,
            "normalized_values": scenario.normalized_values,
            "duration_minutes": scenario.duration_minutes,
            "patient_semantics": scenario.patient_semantics,
            "practitioner_semantics": scenario.practitioner_semantics,
            "location_semantics": scenario.location_semantics,
            "appointment_type_semantics": scenario.appointment_type_semantics,
            "duration_semantics": scenario.duration_semantics,
            "diary_state": scenario.diary_state,
            "entity_state": scenario.entity_state,
            "dialogue_form": scenario.dialogue_form,
            "expected_outcome_kind": scenario.expected_outcome_kind,
            "expected_tool_sequence": scenario.expected_tool_sequence,
            "expected_appointment_deltas": scenario.expected_appointment_deltas,
            "expected_audit_deltas": scenario.expected_audit_deltas,
            "forbidden_outcomes": scenario.forbidden_outcomes,
            "forbidden_tool_calls": scenario.forbidden_tool_calls,
            "expected_clarification": scenario.expected_clarification,
            "clarification_choices": scenario.clarification_choices,
        }
        seed_without_hash = {
            "schema_version": SEED_SCHEMA_VERSION,
            "seed_id": f"bernie_noise_seed_{index:03d}",
            "source_group_id": group.group_id,
            "source_scenario_id": scenario.scenario_id,
            "source_scenario_hash": compute_scenario_hash(scenario),
            "semantic_contract": semantic_contract,
            "surface_evidence": _surface_evidence(scenario),
            "required_evidence_keys": sorted(scenario.source_spans),
            "authority_grant": {
                "provider_write": False,
                "diary_write": False,
                "confirmation": False,
                "override_authority": False,
            },
        }
        seeds.append({**seed_without_hash, "seed_hash": _sha256(seed_without_hash)})

    if len(seeds) != SEED_COUNT:
        raise RuntimeError(f"Expected {SEED_COUNT} semantic seeds, got {len(seeds)}")

    manifest_without_hash = {
        "schema_version": SEED_MANIFEST_SCHEMA_VERSION,
        "corpus": "bernie-receptionist-to-assistant-synthetic-noise",
        "tier": "silver",
        "adjudication": "pending",
        "source_corpus": "lc4-development",
        "source_corpus_hash": corpus.corpus_hash,
        "contains_source_utterances": False,
        "protected_holdout_access": False,
        "seed_count": len(seeds),
        "seeds": seeds,
    }
    return {
        **manifest_without_hash,
        "manifest_hash": _sha256(manifest_without_hash),
    }


def write_semantic_seed_manifest(path: Path = DEFAULT_SEED_PATH) -> dict[str, Any]:
    manifest = build_semantic_seed_manifest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def validate_semantic_seed_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seeds = manifest.get("seeds")
    if not isinstance(seeds, list) or len(seeds) != SEED_COUNT:
        errors.append(f"seed_count must be {SEED_COUNT}")
        return errors
    if manifest.get("contains_source_utterances") is not False:
        errors.append("contains_source_utterances must be false")
    if manifest.get("protected_holdout_access") is not False:
        errors.append("protected_holdout_access must be false")
    if manifest.get("seed_count") != len(seeds):
        errors.append("seed_count does not match seeds")

    seen_ids: set[str] = set()
    for seed in seeds:
        seed_id = seed.get("seed_id")
        if not isinstance(seed_id, str) or seed_id in seen_ids:
            errors.append(f"duplicate or invalid seed_id: {seed_id!r}")
        else:
            seen_ids.add(seed_id)
        supplied_hash = seed.get("seed_hash")
        seed_without_hash = {key: value for key, value in seed.items() if key != "seed_hash"}
        if supplied_hash != _sha256(seed_without_hash):
            errors.append(f"seed hash mismatch: {seed_id}")
        forbidden_keys = {"dialogue_turns", "utterance", "description"}
        if forbidden_keys.intersection(seed):
            errors.append(f"source dialogue field leaked into seed: {seed_id}")
        if any(seed.get("authority_grant", {}).values()):
            errors.append(f"authority grant must be false: {seed_id}")

    manifest_without_hash = {
        key: value for key, value in manifest.items() if key != "manifest_hash"
    }
    if manifest.get("manifest_hash") != _sha256(manifest_without_hash):
        errors.append("manifest hash mismatch")
    return errors


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {error}") from error
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(record)
    return records


def candidate_records_hash(records: list[dict[str, Any]]) -> str:
    return _sha256(records)


def validate_candidate_records(
    records: list[dict[str, Any]],
    seed_manifest: dict[str, Any],
    *,
    expected_generator_identity: dict[str, str],
    candidate_prefix: str,
) -> list[str]:
    """Mechanically validate one model lane without accepting semantics."""

    errors: list[str] = []
    seeds = {seed["seed_id"]: seed for seed in seed_manifest["seeds"]}
    if len(records) != CANDIDATES_PER_LANE:
        errors.append(
            f"candidate count must be {CANDIDATES_PER_LANE}, got {len(records)}"
        )

    seen_ids: set[str] = set()
    seen_dialogues: set[str] = set()
    variants_by_seed: dict[str, set[int]] = {seed_id: set() for seed_id in seeds}

    for record_index, record in enumerate(records, start=1):
        label = str(record.get("candidate_id") or f"record-{record_index}")
        if set(record) != _CANDIDATE_KEYS:
            errors.append(f"{label}: candidate fields do not match schema")
        if record.get("schema_version") != CANDIDATE_SCHEMA_VERSION:
            errors.append(f"{label}: invalid schema_version")

        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or candidate_id in seen_ids:
            errors.append(f"{label}: candidate_id must be a unique string")
        else:
            seen_ids.add(candidate_id)

        seed_id = record.get("source_seed_id")
        seed = seeds.get(seed_id)
        if seed is None:
            errors.append(f"{label}: unknown source_seed_id {seed_id!r}")
            continue
        if record.get("source_seed_hash") != seed["seed_hash"]:
            errors.append(f"{label}: source_seed_hash mismatch")
        if record.get("generator_identity") != expected_generator_identity:
            errors.append(f"{label}: generator_identity mismatch")

        variant_index = record.get("variant_index")
        if variant_index not in (1, 2):
            errors.append(f"{label}: variant_index must be 1 or 2")
        else:
            variants_by_seed[seed_id].add(variant_index)
            expected_id = f"{candidate_prefix}_{seed_id}_{variant_index:02d}"
            if candidate_id != expected_id:
                errors.append(f"{label}: expected candidate_id {expected_id!r}")

        expected_level = {1: "medium", 2: "high"}.get(variant_index)
        if record.get("noise_level") != expected_level:
            errors.append(f"{label}: noise_level must be {expected_level!r}")
        operations = record.get("noise_operations")
        minimum = 2 if variant_index == 1 else 3
        if not isinstance(operations, list) or len(operations) < minimum:
            errors.append(f"{label}: insufficient noise operations")
        elif len(operations) != len(set(operations)):
            errors.append(f"{label}: duplicate noise operation")
        elif not set(operations).issubset(ALLOWED_NOISE_OPERATIONS):
            errors.append(f"{label}: non-allowlisted noise operation")

        turns = record.get("dialogue_turns")
        if not isinstance(turns, list) or not 1 <= len(turns) <= 4:
            errors.append(f"{label}: dialogue_turns must contain 1-4 turns")
            turns = []
        utterances: list[str] = []
        for turn_index, turn in enumerate(turns):
            if not isinstance(turn, dict) or set(turn) != {"turn", "speaker", "utterance"}:
                errors.append(f"{label}: invalid turn {turn_index}")
                continue
            utterance = turn.get("utterance")
            if turn.get("turn") != turn_index + 1:
                errors.append(f"{label}: non-sequential turn number")
            if turn.get("speaker") != "receptionist":
                errors.append(f"{label}: only receptionist turns are permitted")
            if not isinstance(utterance, str) or not utterance.strip() or len(utterance) > 500:
                errors.append(f"{label}: invalid utterance")
            else:
                utterances.append(utterance)

        dialogue_key = _canonical_json(utterances)
        if dialogue_key in seen_dialogues:
            errors.append(f"{label}: duplicate dialogue payload")
        else:
            seen_dialogues.add(dialogue_key)
        joined_text = " ".join(utterances)
        if (
            _EMAIL_RE.search(joined_text)
            or _URL_RE.search(joined_text)
            or _AU_PHONE_RE.search(joined_text)
            or _LONG_IDENTIFIER_RE.search(joined_text)
        ):
            errors.append(f"{label}: contact detail or long identifier detected")

        spans_by_key = record.get("evidence_spans")
        required_keys = set(seed["required_evidence_keys"])
        if not isinstance(spans_by_key, dict) or set(spans_by_key) != required_keys:
            errors.append(f"{label}: evidence keys must exactly match seed")
            spans_by_key = {}
        for evidence_key, spans in spans_by_key.items():
            if not isinstance(spans, list) or not spans:
                errors.append(f"{label}: empty evidence spans for {evidence_key}")
                continue
            for span in spans:
                if not isinstance(span, dict) or set(span) != {
                    "turn_index",
                    "start",
                    "end",
                    "text",
                }:
                    errors.append(f"{label}: invalid evidence span for {evidence_key}")
                    continue
                turn_index = span.get("turn_index")
                start = span.get("start")
                end = span.get("end")
                text = span.get("text")
                if (
                    not isinstance(turn_index, int)
                    or not 0 <= turn_index < len(utterances)
                    or not isinstance(start, int)
                    or not isinstance(end, int)
                    or not isinstance(text, str)
                    or not 0 <= start < end
                ):
                    errors.append(f"{label}: invalid evidence coordinates for {evidence_key}")
                    continue
                utterance = utterances[turn_index]
                if end > len(utterance) or utterance[start:end] != text:
                    errors.append(f"{label}: evidence span mismatch for {evidence_key}")

        if record.get("semantic_change") != "none":
            errors.append(f"{label}: semantic_change must be none")
        if record.get("provenance") != "silver":
            errors.append(f"{label}: provenance must be silver")
        if record.get("adjudication") != "pending":
            errors.append(f"{label}: adjudication must be pending")
        if record.get("authority_grant") != _AUTHORITY_FALSE:
            errors.append(f"{label}: authority grant must be exactly false")

    for seed_id, variants in variants_by_seed.items():
        if variants != {1, 2}:
            errors.append(f"{seed_id}: expected variants 1 and 2, got {sorted(variants)}")
    return errors


__all__ = [
    "DEFAULT_SEED_PATH",
    "ALLOWED_NOISE_OPERATIONS",
    "CANDIDATES_PER_LANE",
    "CANDIDATE_SCHEMA_VERSION",
    "SEED_COUNT",
    "SEED_MANIFEST_SCHEMA_VERSION",
    "SEED_SCHEMA_VERSION",
    "build_semantic_seed_manifest",
    "candidate_records_hash",
    "load_jsonl",
    "validate_candidate_records",
    "validate_semantic_seed_manifest",
    "write_semantic_seed_manifest",
]
