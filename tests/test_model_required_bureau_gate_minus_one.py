from __future__ import annotations

import json
from pathlib import Path

from scripts.model_required_bureau_gate_minus_one_acceptance import (
    ANALYSIS,
    EXPECTED_OPPORTUNITIES,
    INDEX_PATH,
    THREAT_PATH,
    build_evidence,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split()).lower()


def test_gate_minus_one_provider_free_acceptance_passes() -> None:
    evidence = build_evidence()
    assert evidence["passed"] is True
    assert evidence["result"] == (
        "model_required_bureau_gate_minus_one_provider_free_acceptance_pass"
    )
    assert evidence["evidence_collection"]["artifact_count"] == 21
    assert evidence["evidence_collection"]["local_artifact_count"] == 14
    assert evidence["evidence_collection"]["external_primary_source_count"] == 7


def test_two_selected_controls_and_all_alternatives_are_complete() -> None:
    evidence = build_evidence()["hardening_portfolio"]
    assert evidence["opportunity_count"] == 2
    assert evidence["option_count"] == 7
    assert evidence["diagram_count"] == 9
    assert evidence["selected"] == EXPECTED_OPPORTUNITIES


def test_source_collection_is_bound_to_exact_pre_review_revision() -> None:
    index = _json(INDEX_PATH)
    assert index["target_revision"] == "b09739183ddbe1a102086460749a84741a23b11b"
    assert index["collection_sha256"] == (
        "e3b6721331853ee41598c226139dc09820e308413322abc72b7a0762baa6fc70"
    )
    assert index["artifact_count"] == len(index["artifacts"]) == 21
    assert len({item["id"] for item in index["artifacts"]}) == 21


def test_model_and_cell_are_explicitly_untrusted() -> None:
    text = _normalized(THREAT_PATH)
    assert "deliberately hostile but schema-shaped output" in text
    assert "compromise of the local cognitive wrapper" in text
    assert "never security principals or authority evidence" in text


def test_label_and_sink_contract_is_complete_enough_for_gate_zero() -> None:
    path = (
        ANALYSIS / "proposals" / "deterministic-information-flow-confinement.md"
    )
    text = _normalized(path)
    for phrase in (
        "integrity principal set",
        "confidentiality/readers",
        "maximum authority/capability ceiling",
        "security-relevant argument",
        "joined reader set",
        "field-specific",
        "rest/openapi commands",
    ):
        assert phrase in text


def test_one_attempt_cell_has_no_ambient_authority_bridge() -> None:
    path = (
        ANALYSIS / "proposals" / "cognitive-cell-compromise-containment.md"
    )
    text = _normalized(path)
    for phrase in (
        "one bureau attempt",
        "no shell",
        "mount-free",
        "runtime socket",
        "metadata endpoint",
        "broker constructs one minimal labeled input, owns the provider request",
        "never evaluates",
        "teardown and residue",
    ):
        assert phrase in text


def test_no_implementation_or_runtime_authority_is_opened() -> None:
    assert not (ANALYSIS / "implementation").exists()
    side_effects = build_evidence()["authority_and_side_effects"]
    assert side_effects
    assert set(side_effects.values()) == {0}


def test_every_option_has_a_comparable_after_diagram() -> None:
    hardening = _json(ANALYSIS / "hardening.json")
    for opportunity in hardening["opportunities"]:
        for option in opportunity["options"]:
            before = ANALYSIS / option["diagramPaths"]["before"]
            after = ANALYSIS / option["diagramPaths"]["after"]
            assert before.is_file()
            assert after.is_file()
