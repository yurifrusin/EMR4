from __future__ import annotations

import json

from app.services.bernie.synthetic_noise_corpus import (
    DEFAULT_SEED_PATH,
    SEED_COUNT,
    build_semantic_seed_manifest,
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
