"""Focused admission and coherence tests for synthetic Silver v2 candidates."""

from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from app.services.bernie.synthetic_noise_v2 import build_v2_anchor_manifest
from app.services.bernie.synthetic_noise_v2_candidates import (
    AUTHORITY_ALL_FALSE,
    CANDIDATE_COUNT_V2,
    DEFAULT_ADMISSION_PATH_V2,
    DEFAULT_CANDIDATE_PATH_V2,
    build_v2_admission,
    build_v2_candidate_artifacts,
    build_v2_candidates,
    candidate_file_hash,
    candidate_records_hash,
    check_v2_candidate_artifacts,
    load_jsonl,
    validate_v2_candidates,
)


def _artifacts():
    return build_v2_candidate_artifacts()


def test_v2_candidate_population_and_balance() -> None:
    manifest, records, admission = _artifacts()
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    assert len(records) == CANDIDATE_COUNT_V2 == 192
    assert admission["accepted_count"] == 192
    assert admission["quarantine_count"] == admission["rejected_count"] == 0
    assert Counter(record["source_seed_id"] for record in records) == {
        seed_id: 2 for seed_id in anchors
    }
    assert Counter(
        anchors[record["source_seed_id"]]["semantic_contract"]["intended_action"]
        for record in records
    ) == {action: 32 for action in ("create", "move", "resize", "cancel", "status_change", "explain_schedule")}
    assert Counter(
        anchors[record["source_seed_id"]]["dialogue_form_contract"]["dialogue_form"]
        for record in records
    ) == {form: 24 for form in ("one_shot", "clarification", "correction", "reversal", "ellipsis", "anaphora", "repeated_request", "session_restart")}


def test_committed_candidates_and_admission_regenerate_exactly() -> None:
    manifest, records, admission = _artifacts()
    assert load_jsonl(DEFAULT_CANDIDATE_PATH_V2) == records
    assert json.loads(DEFAULT_ADMISSION_PATH_V2.read_text(encoding="utf-8")) == admission
    assert build_v2_candidates(manifest) == records
    assert check_v2_candidate_artifacts() == []


def test_exact_candidate_and_admission_hashes() -> None:
    _, records, admission = _artifacts()
    assert candidate_records_hash(records) == "sha256:634a7de32356d41232a279c335bcfb5e5a13cf6df884b8abf43e9769b7dc4cf9"
    assert candidate_file_hash(records) == admission["file_payload_hash"]
    assert admission["admission_hash"] == "sha256:a630151b011ae09b63ae6daee84aabefb4a4e913c514a13e918d68c570e80cce"


def test_all_candidate_evidence_spans_slice_exactly() -> None:
    manifest, records, _ = _artifacts()
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    for record in records:
        assert set(record["evidence_spans"]) == set(
            anchors[record["source_seed_id"]]["required_evidence_keys"]
        )
        for spans in record["evidence_spans"].values():
            for span in spans:
                utterance = record["dialogue_turns"][span["turn_index"]]["utterance"]
                assert utterance[span["start"] : span["end"]] == span["text"]


def test_all_candidate_authority_and_evidence_tier_are_closed() -> None:
    _, records, admission = _artifacts()
    assert all(record["authority_grant"] == AUTHORITY_ALL_FALSE for record in records)
    assert all(record["semantic_change"] == "none" for record in records)
    assert all(record["provenance"] == "silver" for record in records)
    assert all(record["adjudication"] == "pending" for record in records)
    assert admission["product_parser_used_for_admission"] is False
    assert admission["protected_holdout_access"] is False
    assert admission["historical_diary_access"] is False
    assert admission["external_corpus_access"] is False


def test_declared_core_noise_operations_are_surfaced() -> None:
    _, records, _ = _artifacts()
    for record in records:
        text = " ".join(turn["utterance"] for turn in record["dialogue_turns"])
        operations = set(record["noise_operations"])
        assert "appt" in text or "diary schedule" in text
        if record["variant_index"] == 1:
            assert {"staff_shorthand", "reordered_slots"}.issubset(operations)
            action = record["evidence_spans"]["intended_action"][0]["text"]
            appointment_date = record["evidence_spans"]["appointment_date"][0]["text"]
            assert text.rfind(action) > text.find(appointment_date)
        else:
            assert {"speech_disfluency", "dictation_artifact", "reordered_slots"}.issubset(operations)
            assert "uh" in text.lower() or "Dictated in short fragments" in text


def test_clarification_candidates_surface_unresolved_ambiguity() -> None:
    manifest, records, _ = _artifacts()
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    for record in records:
        anchor = anchors[record["source_seed_id"]]
        if anchor["dialogue_form_contract"]["dialogue_form"] != "clarification":
            continue
        text = " ".join(turn["utterance"] for turn in record["dialogue_turns"])
        target = anchor["dialogue_form_contract"]["ambiguity_target"]
        assert f"The {target} is unclear" in text
        assert "ask me to clarify" in text
        assert "either" in text


def test_correction_candidates_surface_prior_replacement_and_final_value() -> None:
    manifest, records, _ = _artifacts()
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    for record in records:
        if anchors[record["source_seed_id"]]["dialogue_form_contract"]["dialogue_form"] != "correction":
            continue
        assert "Dr Patel" in record["dialogue_turns"][0]["utterance"]
        final = record["dialogue_turns"][-1]["utterance"]
        assert "Correction" in final and "replace Dr Patel with Dr Shera" in final


def test_reversal_candidates_surface_whole_action_withdrawal() -> None:
    manifest, records, _ = _artifacts()
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    for record in records:
        if anchors[record["source_seed_id"]]["dialogue_form_contract"]["dialogue_form"] != "reversal":
            continue
        final = record["dialogue_turns"][-1]["utterance"]
        assert "disregard that" in final and "do not carry it out" in final


def test_local_recovery_repetition_and_restart_are_surfaced() -> None:
    manifest, records, _ = _artifacts()
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    for record in records:
        form = anchors[record["source_seed_id"]]["dialogue_form_contract"]["dialogue_form"]
        turns = [turn["utterance"] for turn in record["dialogue_turns"]]
        if form in {"ellipsis", "anaphora"}:
            assert len(turns) == 2 and "reference" in turns[0].lower()
        elif form == "repeated_request":
            assert turns[0] == turns[1]
        elif form == "session_restart":
            assert "Start over" in turns[-1]


def test_validator_rejects_tampered_span() -> None:
    manifest, records, _ = _artifacts()
    tampered = deepcopy(records)
    span = next(iter(tampered[0]["evidence_spans"].values()))[0]
    span["text"] = "wrong"
    assert any("evidence span mismatch" in error for error in validate_v2_candidates(tampered, manifest))


def test_validator_rejects_missing_reversal_marker() -> None:
    manifest, records, _ = _artifacts()
    tampered = deepcopy(records)
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    target = next(
        record for record in tampered
        if anchors[record["source_seed_id"]]["dialogue_form_contract"]["dialogue_form"] == "reversal"
    )
    target["dialogue_turns"][-1]["utterance"] = "Continue as requested."
    assert any("whole-action reversal" in error for error in validate_v2_candidates(tampered, manifest))


def test_validator_rejects_correction_without_explicit_replacement() -> None:
    manifest, records, _ = _artifacts()
    tampered = deepcopy(records)
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    target = next(
        record for record in tampered
        if anchors[record["source_seed_id"]]["dialogue_form_contract"]["dialogue_form"] == "correction"
    )
    target["dialogue_turns"][-1]["utterance"] = "Use Dr Shera."
    assert any("correction replacement" in error for error in validate_v2_candidates(tampered, manifest))


def test_validator_rejects_authority_or_seed_drift() -> None:
    manifest, records, _ = _artifacts()
    authority = deepcopy(records)
    authority[0]["authority_grant"]["diary_write"] = True
    assert any("authority grant" in error for error in validate_v2_candidates(authority, manifest))
    seed = deepcopy(records)
    seed[0]["source_seed_hash"] = "sha256:" + "0" * 64
    assert any("source seed hash" in error for error in validate_v2_candidates(seed, manifest))


def test_admission_rejects_any_invalid_candidate() -> None:
    manifest, records, _ = _artifacts()
    records[0]["semantic_change"] = "changed"
    try:
        build_v2_admission(records, manifest)
    except ValueError as error:
        assert "semantic change" in str(error)
    else:
        raise AssertionError("invalid candidate was admitted")


def test_candidate_admission_module_has_no_product_evaluator_import() -> None:
    path = Path("app/services/bernie/synthetic_noise_v2_candidates.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    forbidden = {
        module
        for module in modules
        if any(
            fragment in module
            for fragment in (
                "semantic_extraction",
                "composed_corpus_evaluator",
                "composed_evaluator",
                "synthetic_noise_robustness",
            )
        )
    }
    assert not forbidden
