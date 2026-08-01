"""Regression checks for narrowly scoped security-tool exceptions."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_bandit_baseline_contains_only_reviewed_git_identity_findings() -> None:
    baseline = json.loads(
        (REPO_ROOT / ".bandit-baseline.json").read_text(encoding="utf-8")
    )
    assert baseline["schema_version"] == "emr4.bandit-reviewed-baseline.v1"
    results = baseline["reviewed_findings"]

    assert len(results) == 2
    assert {result["test_id"] for result in results} == {"B324"}
    assert {Path(result["path"]).name for result in results} == {
        "lc4v10_content_blind_framework.py",
        "lc4v10_protected_sealing.py",
    }
    assert all(len(result["code_sha256"]) == 64 for result in results)
    assert all("Git blob identity" in result["rationale"] for result in results)


def test_python_security_workflow_runs_bandit_after_other_failures() -> None:
    workflow = (REPO_ROOT / ".github/workflows/python-security.yml").read_text(
        encoding="utf-8"
    )
    assert "if: ${{ always() }}" in workflow
    assert "python scripts/verify_repository.py --profile ci-bandit" in workflow
