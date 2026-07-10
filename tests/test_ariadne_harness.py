"""Provider-free tests for the Ariadne schema spine and rehydration gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestration_harness.models import ActionClassification, BoundaryClass, Mandate
from orchestration_harness.rehydration import GitState, build_rehydration_status
from scripts.ariadne_context_rehydration_check import (
    DEFAULT_CHECKPOINT_PATH,
    DEFAULT_EVIDENCE_PATH,
    DEFAULT_MANDATE_PATH,
    build_status,
    load_mandate,
)


def test_current_sidecar_mandate_is_schema_valid_and_round_trips():
    mandate = load_mandate(DEFAULT_MANDATE_PATH)

    assert mandate is not None
    assert Mandate.from_dict(json.loads(json.dumps(mandate.to_dict()))) == mandate
    assert "runtime_wiring" in mandate.requires_user_approval


def test_boundary_and_action_vocabularies_are_stable():
    assert [item.value for item in BoundaryClass] == ["green", "blue", "amber", "red", "black"]
    assert [item.value for item in ActionClassification] == [
        "allowed",
        "allowed_with_evidence",
        "requires_user_approval",
        "blocked",
        "underspecified",
    ]


def test_clean_state_passes_rehydration_gate():
    mandate = load_mandate(DEFAULT_MANDATE_PATH)
    checkpoint = json.loads(DEFAULT_CHECKPOINT_PATH.read_text(encoding="utf-8"))

    status = build_rehydration_status(
        git_state=GitState(branch="master", head="abc123", dirty=False),
        mandate=mandate,
        checkpoint=checkpoint,
        evidence_ledger_readable=True,
    )

    assert status["rehydration_status"] == "passed"
    assert status["reasons"] == []
    assert status["next_action"]["boundary_class"] == "green"


@pytest.mark.parametrize(
    ("git_state", "mandate", "checkpoint", "evidence_readable", "reason"),
    [
        (GitState(branch="master", head="abc123", dirty=True), "valid", "valid", True, "dirty_worktree_present"),
        (GitState(branch="master", head="abc123", dirty=False), None, "valid", True, "active_mandate_missing"),
        (GitState(branch="master", head="abc123", dirty=False), "valid", None, True, "checkpoint_missing"),
        (GitState(branch="master", head="abc123", dirty=False), "valid", "unclassified", True, "next_action_not_classified"),
        (GitState(branch="master", head="abc123", dirty=False), "valid", "valid", False, "evidence_ledger_missing_or_unreadable"),
    ],
)
def test_rehydration_gate_pauses_for_missing_or_uncertain_state(
    git_state: GitState,
    mandate: str | None,
    checkpoint: str | None,
    evidence_readable: bool,
    reason: str,
):
    valid_mandate = load_mandate(DEFAULT_MANDATE_PATH)
    valid_checkpoint = json.loads(DEFAULT_CHECKPOINT_PATH.read_text(encoding="utf-8"))
    if checkpoint == "unclassified":
        valid_checkpoint = {"next_action": {"kind": "unknown"}}

    status = build_rehydration_status(
        git_state=git_state,
        mandate=valid_mandate if mandate == "valid" else None,
        checkpoint=valid_checkpoint if checkpoint is not None else None,
        evidence_ledger_readable=evidence_readable,
    )

    assert status["rehydration_status"] == "pause_required"
    assert reason in status["reasons"]
    assert status["remediations"]


def test_portable_core_has_no_emr4_runtime_or_os_specific_dependency():
    core_root = Path(__file__).resolve().parents[1] / "orchestration_harness"
    source = "\n".join(path.read_text(encoding="utf-8") for path in core_root.glob("*.py"))

    assert "import app" not in source
    assert "from app" not in source
    assert "os.path" not in source
    assert "subprocess" not in source


def test_cli_build_status_reads_real_paths_without_mutation(tmp_path: Path):
    status = build_status(
        repo_root=Path(__file__).resolve().parents[1],
        mandate_path=DEFAULT_MANDATE_PATH,
        checkpoint_path=DEFAULT_CHECKPOINT_PATH,
        evidence_path=DEFAULT_EVIDENCE_PATH,
    )

    assert status["repo_state"]["branch"]
    assert status["repo_state"]["head"]
    assert DEFAULT_EVIDENCE_PATH.exists()
