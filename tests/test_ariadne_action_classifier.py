"""Replay tests for Ariadne's advisory observable-artifact classifier."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from orchestration_harness.classifier import (
    PATH_POLICY_SCHEMA_VERSION,
    ObservableAction,
    PathBoundaryPolicy,
    classify_observable_action,
)
from orchestration_harness.models import ActionClassification, BoundaryClass, Evidence

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "orchestration" / "harness_policies" / "ariadne-sidecar-path-boundaries.json"
CORPUS_PATH = REPO_ROOT / "tests" / "fixtures" / "ariadne_harness" / "historical_action_replay.json"


def load_policy() -> PathBoundaryPolicy:
    return PathBoundaryPolicy.from_dict(json.loads(POLICY_PATH.read_text(encoding="utf-8")))


def load_corpus() -> dict[str, object]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_historical_corpus_replays_fifteen_hand_labelled_observable_actions():
    policy = load_policy()
    corpus = load_corpus()

    assert corpus["schema_version"] == "ariadne.historical_action_replay.v1"
    cases = corpus["cases"]
    assert isinstance(cases, list)
    assert len(cases) == 15
    for case in cases:
        assert isinstance(case, dict)
        action = ObservableAction.from_dict(case["action"])
        result = classify_observable_action(action, policy)
        assert result.boundary_class.value == case["expected"]["boundary_class"]
        assert result.classification.value == case["expected"]["classification"]


def test_corpus_paths_are_exact_historical_commit_artifacts():
    corpus = load_corpus()
    for case in corpus["cases"]:
        completed = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", case["source_commit"]],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        historical_paths = completed.stdout.splitlines()
        assert historical_paths == case["action"]["changed_paths"]


@pytest.mark.parametrize(
    ("paths", "boundary", "classification"),
    [
        (["docs/plan.md"], "green", "allowed"),
        (["docs/plan.md", "app/main.py"], "red", "requires_user_approval"),
        (["local_data/private.json"], "black", "blocked"),
        (["unknown-root/file.txt"], "amber", "underspecified"),
    ],
)
def test_classifier_uses_path_observations_and_chooses_the_stricter_boundary(
    paths: list[str], boundary: str, classification: str
):
    result = classify_observable_action(
        ObservableAction.from_dict({"action_id": "synthetic", "changed_paths": paths}),
        load_policy(),
    )

    assert result.boundary_class.value == boundary
    assert result.classification.value == classification


def test_policy_and_evidence_schemas_reject_ambiguous_or_shell_like_contracts():
    assert json.loads(POLICY_PATH.read_text(encoding="utf-8"))["schema_version"] == PATH_POLICY_SCHEMA_VERSION
    with pytest.raises(ValueError):
        ObservableAction.from_dict({"action_id": "bad", "changed_paths": ["..\\app\\main.py"]})
    with pytest.raises(ValueError):
        Evidence.from_dict(
            {
                "evidence_id": "bad",
                "state_fingerprint": "abc",
                "command": ["git status && git push"],
                "scope": [],
                "recorded_by": "test",
                "limitations": [],
            }
        )


def test_evidence_round_trip_preserves_command_as_argument_array():
    evidence = Evidence.from_dict(
        {
            "evidence_id": "fixture-test",
            "state_fingerprint": "abc123",
            "command": ["python", "-m", "pytest", "tests/test_ariadne_action_classifier.py"],
            "scope": ["tests/test_ariadne_action_classifier.py"],
            "recorded_by": "codex",
            "limitations": ["provider_free"],
        }
    )

    assert Evidence.from_dict(evidence.to_dict()) == evidence
    assert evidence.command[0] == "python"
    assert ActionClassification.REQUIRES_USER_APPROVAL.value == "requires_user_approval"
    assert BoundaryClass.BLACK.value == "black"
