from __future__ import annotations

import json

from app.services.bernie.synthetic_noise_corpus import (
    CANDIDATE_SCHEMA_VERSION,
    DEFAULT_SEED_PATH,
    SEED_COUNT,
    build_semantic_seed_manifest,
    candidate_records_hash,
    validate_candidate_records,
    validate_semantic_seed_manifest,
)


def test_semantic_seed_manifest_is_deterministic_and_valid() -> None:
    first = build_semantic_seed_manifest()
    second = build_semantic_seed_manifest()

    assert first == second
    assert first["seed_count"] == SEED_COUNT
    assert validate_semantic_seed_manifest(first) == []


def test_committed_semantic_seed_manifest_matches_regeneration() -> None:
    committed = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))

    assert committed == build_semantic_seed_manifest()


def test_semantic_seed_manifest_contains_no_source_dialogue_or_authority() -> None:
    manifest = build_semantic_seed_manifest()
    serialized = json.dumps(manifest, sort_keys=True)

    assert '"dialogue_turns"' not in serialized
    assert '"utterance"' not in serialized
    assert '"description"' not in serialized
    assert manifest["contains_source_utterances"] is False
    assert manifest["protected_holdout_access"] is False
    assert all(not any(seed["authority_grant"].values()) for seed in manifest["seeds"])


def test_semantic_seed_manifest_covers_all_implemented_actions() -> None:
    manifest = build_semantic_seed_manifest()
    actions = {
        seed["semantic_contract"]["intended_action"] for seed in manifest["seeds"]
    }

    assert actions == {
        "create",
        "move",
        "resize",
        "cancel",
        "status_change",
        "explain_schedule",
    }


def _valid_candidate(seed: dict[str, object]) -> dict[str, object]:
    tokens = []
    for values in seed["surface_evidence"].values():
        tokens.extend(values)
    prefix = f"please {seed['seed_id']} "
    utterance = prefix + " ".join(tokens)
    spans: dict[str, list[dict[str, object]]] = {}
    cursor = len(prefix)
    for evidence_key, values in seed["surface_evidence"].items():
        spans[evidence_key] = []
        for value in values:
            start = utterance.index(value, cursor)
            end = start + len(value)
            spans[evidence_key].append(
                {"turn_index": 0, "start": start, "end": end, "text": value}
            )
            cursor = end + 1
    return {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "candidate_id": f"test_{seed['seed_id']}_01",
        "source_seed_id": seed["seed_id"],
        "source_seed_hash": seed["seed_hash"],
        "generator_identity": {
            "provider_id": "test",
            "model_id": "test-model",
            "lane_id": "test-lane",
        },
        "variant_index": 1,
        "noise_level": "medium",
        "noise_operations": ["filler", "reordered_slots"],
        "dialogue_turns": [
            {"turn": 1, "speaker": "receptionist", "utterance": utterance}
        ],
        "evidence_spans": spans,
        "semantic_change": "none",
        "provenance": "silver",
        "adjudication": "pending",
        "authority_grant": {
            "provider_write": False,
            "diary_write": False,
            "confirmation": False,
            "override_authority": False,
        },
    }


def test_candidate_validator_accepts_mechanical_contract() -> None:
    seeds = build_semantic_seed_manifest()
    records = []
    for seed in seeds["seeds"]:
        medium = _valid_candidate(seed)
        high = json.loads(json.dumps(medium))
        high["candidate_id"] = f"test_{seed['seed_id']}_02"
        high["variant_index"] = 2
        high["noise_level"] = "high"
        high["noise_operations"] = ["filler", "reordered_slots", "staff_shorthand"]
        high["dialogue_turns"][0]["utterance"] += " thanks"
        records.extend([medium, high])

    assert validate_candidate_records(
        records,
        seeds,
        expected_generator_identity={
            "provider_id": "test",
            "model_id": "test-model",
            "lane_id": "test-lane",
        },
        candidate_prefix="test",
    ) == []
    assert candidate_records_hash(records).startswith("sha256:")


def test_candidate_validator_rejects_authority_and_bad_span() -> None:
    seeds = build_semantic_seed_manifest()
    records = []
    for seed in seeds["seeds"]:
        for variant_index in (1, 2):
            record = _valid_candidate(seed)
            record["candidate_id"] = f"test_{seed['seed_id']}_{variant_index:02d}"
            record["variant_index"] = variant_index
            record["noise_level"] = "medium" if variant_index == 1 else "high"
            if variant_index == 2:
                record["noise_operations"] = [
                    "filler",
                    "reordered_slots",
                    "staff_shorthand",
                ]
                record["dialogue_turns"][0]["utterance"] += " thanks"
            records.append(record)
    records[0]["authority_grant"]["diary_write"] = True
    first_key = next(iter(records[1]["evidence_spans"]))
    records[1]["evidence_spans"][first_key][0]["start"] += 1

    errors = validate_candidate_records(
        records,
        seeds,
        expected_generator_identity={
            "provider_id": "test",
            "model_id": "test-model",
            "lane_id": "test-lane",
        },
        candidate_prefix="test",
    )

    assert any("authority grant" in error for error in errors)
    assert any("evidence span mismatch" in error for error in errors)
