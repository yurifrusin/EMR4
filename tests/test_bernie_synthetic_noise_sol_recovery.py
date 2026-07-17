from __future__ import annotations

import json
from collections import Counter

from app.services.bernie.synthetic_noise_codex import (
    AUTHORITY_GRANT,
    CANDIDATE_COUNT,
    GENERATOR_IDENTITY,
    OUTPUT_PATH,
    SEED_PATH,
    build_candidates,
    validate_candidates,
)
from app.services.bernie.synthetic_noise_corpus import validate_candidate_records


def _inputs() -> tuple[dict[str, object], list[dict[str, object]]]:
    manifest = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in OUTPUT_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return manifest, records


def test_recovered_candidates_match_deterministic_regeneration() -> None:
    manifest, committed = _inputs()

    assert committed == build_candidates(manifest)
    assert len(committed) == CANDIDATE_COUNT
    assert validate_candidates(committed, manifest) == []
    assert validate_candidate_records(
        committed,
        manifest,
        expected_generator_identity=GENERATOR_IDENTITY,
        candidate_prefix="sol",
    ) == []


def test_recovered_candidates_preserve_dialogue_form_and_closed_authority() -> None:
    manifest, records = _inputs()
    seeds = {seed["seed_id"]: seed for seed in manifest["seeds"]}
    form_counts: Counter[str] = Counter()

    for record in records:
        seed = seeds[record["source_seed_id"]]
        form = seed["semantic_contract"]["dialogue_form"]
        form_counts[form] += 1
        turn_count = len(record["dialogue_turns"])
        assert turn_count == (1 if form == "one_shot" else 2)
        assert record["authority_grant"] == AUTHORITY_GRANT
        assert not any(record["authority_grant"].values())
        assert record["provenance"] == "silver"
        assert record["adjudication"] == "pending"
        assert record["semantic_change"] == "none"

    assert form_counts == {
        "one_shot": 24,
        "clarification": 24,
        "correction": 24,
        "reversal": 24,
        "ellipsis": 24,
        "anaphora": 24,
        "repeated": 24,
        "session_restart": 24,
    }


def test_recovered_correction_forms_replace_generic_practitioner() -> None:
    manifest, records = _inputs()
    seeds = {seed["seed_id"]: seed for seed in manifest["seeds"]}

    corrections = [
        record
        for record in records
        if seeds[record["source_seed_id"]]["semantic_contract"]["dialogue_form"]
        == "correction"
    ]
    assert len(corrections) == 24
    for record in corrections:
        first, final = record["dialogue_turns"]
        assert "a doctor" in first["utterance"]
        assert "Dr Shera" in final["utterance"]
