"""Fail-closed evidence checks for the appointment-call quarantine pilot."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "bernie-appointment-call-quarantine-pilot-evidence.json"


def _evidence() -> dict[str, object]:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_pilot_stopped_before_content_download() -> None:
    payload = _evidence()
    assert payload["decision"] == "stop_before_content_download"
    assert payload["admission_status"] == "rejected_pending_verifiable_provenance_package"

    actions = payload["actions"]
    assert isinstance(actions, dict)
    assert actions["public_metadata_read"] is True
    assert actions["public_file_listing_first_page_read"] is True
    for forbidden_action in (
        "corpus_file_downloaded",
        "corpus_content_opened",
        "local_quarantine_root_created",
        "provider_or_model_transmission",
        "development_corpus_deduplication",
        "protected_holdout_access",
        "training_or_tuning",
        "gold_authoring",
        "runtime_or_product_use",
    ):
        assert actions[forbidden_action] is False


def test_preliminary_gate_records_every_required_blocker() -> None:
    payload = _evidence()
    blockers = payload["unresolved_required_evidence"]
    assert isinstance(blockers, list)
    assert len(blockers) == 9
    joined = "\n".join(str(blocker) for blocker in blockers)
    for required_concept in (
        "data controller",
        "jurisdiction",
        "consent",
        "uploader authority",
        "rights chain",
        "redaction method",
        "residual direct and quasi-identifier audit",
        "database and content rights",
    ):
        assert required_concept in joined


def test_live_baton_and_closeout_preserve_stop_decision() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    closeout = (
        ROOT / "docs" / "bernie-appointment-call-quarantine-pilot-closeout.md"
    ).read_text(encoding="utf-8")
    acceptance = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "appointment-call-quarantine-pilot-sol-acceptance.md"
    ).read_text(encoding="utf-8")

    assert "stop_before_content_download" in handover
    assert "Decision: `stop_before_content_download`" in closeout
    assert "Decision: `pass_stop_before_content_download`" in acceptance
    assert "no corpus content was downloaded" in handover.lower()
