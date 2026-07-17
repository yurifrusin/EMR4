from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "bernie-synthetic-silver-coherence-audit-contract.md"


def test_coherence_contract_freezes_exact_inputs_and_population() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "7c51e574930962ae83e721e3766fcbbee26d6013" in text
    assert "sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665" in text
    assert "f0eadc06d8aa873b96eec77bcc94f305c0ad919b" in text
    assert "38448ea31b001ade21e1953234695be789503c48" in text
    assert "162be3a0f1f9778b1b3e299115737fd31797809b" in text
    assert "exactly the 192 records" in text


def test_coherence_contract_is_corpus_only_and_fail_closed() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    for decision in (
        "accept_coherent",
        "quarantine_missing_surfaced_evidence",
        "quarantine_oracle_policy_conflict",
        "quarantine_entity_transition_conflict",
        "quarantine_replay_contract_conflict",
        "reject_semantic_corruption",
    ):
        assert decision in text
    assert "Current parser output is diagnostic only" in compact
    assert "feeding expected fields into the interpreter" in compact
    assert "Protected V1-V10 remain sealed" in compact
    assert "does not authorize parser" in compact
