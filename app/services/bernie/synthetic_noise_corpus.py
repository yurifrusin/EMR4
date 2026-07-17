"""Development-only seed and candidate contracts for noisy Bernie language.

The module exposes semantic anchors from the ordinary LC4 development corpus
without exporting source utterances.  It never reads a protected holdout and
grants no provider, confirmation, diary-write, or runtime authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from app.services.bernie.corpus_tier import compute_scenario_hash
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader


SEED_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_seed.v1"
SEED_MANIFEST_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_seed_manifest.v1"
SEED_COUNT = 96
DEFAULT_SEED_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/semantic_seeds.json"
)


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


__all__ = [
    "DEFAULT_SEED_PATH",
    "SEED_COUNT",
    "SEED_MANIFEST_SCHEMA_VERSION",
    "SEED_SCHEMA_VERSION",
    "build_semantic_seed_manifest",
    "validate_semantic_seed_manifest",
    "write_semantic_seed_manifest",
]
