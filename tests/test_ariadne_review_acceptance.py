"""Focused tests for the review-acceptance gate.

Uses temporary directories, synthetic artifacts/receipts, and temporary
Git repositories/worktrees. Does not weaken/remove/skip/xfail existing tests.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from orchestration_harness.review_acceptance import accept_review_artifact

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_worktree(tmp_path: Path) -> Path:
    """Create and return a temporary git repository to simulate a worktree."""
    repo = tmp_path / "review_worktree"
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@emr4.dev"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test Runner"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    (repo / "README.md").write_text("# worktree")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return repo


def _commit_file(repo: Path, rel_path: str, content: str, msg: str) -> str:
    """Create a file, commit it, return the commit SHA."""
    full = repo / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    subprocess.run(
        ["git", "add", rel_path], cwd=str(repo), check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _make_receipt(
    root: Path,
    *,
    artifact_rel: str = "artifact.md",
    artifact_kind: str = "completion",
    status: str = "completed",
    artifact_observed: bool = True,
    permission_prompt_observed: bool = False,
    process_cleanup_confirmed: bool = True,
    extra: dict | None = None,
) -> Path:
    data = {
        "status": status,
        "artifact": artifact_rel,
        "artifact_kind": artifact_kind,
        "artifact_observed": artifact_observed,
        "permission_prompt_observed": permission_prompt_observed,
        "process_cleanup_confirmed": process_cleanup_confirmed,
    }
    if extra:
        data.update(extra)
    p = root / "receipt.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _make_artifact(root: Path, content: str, *, name: str = "artifact.md") -> Path:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _make_collect_file(root: Path, content: str, *, name: str = "collect.txt") -> Path:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI (sys.path bootstrap handles repo root)."""
    script = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "ariadne_review_acceptance.py"
    )
    project_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _get_branch(repo: Path) -> str:
    return subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _get_head(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _run_acceptance_cli(
    *,
    artifact: Path,
    artifact_kind: str,
    receipt: Path,
    worktree: Path,
    branch: str,
    commit: str,
    collect: Path,
) -> subprocess.CompletedProcess:
    return _run_cli(
        "--artifact",
        str(artifact),
        "--artifact-kind",
        artifact_kind,
        "--receipt",
        str(receipt),
        "--worktree",
        str(worktree),
        "--expected-branch",
        branch,
        "--candidate-commit",
        commit,
        "--pytest-collect-output",
        str(collect),
        "--review-mode",
        "executable",
    )


def _check_json_contract(output: dict):
    """Assert the JSON contract includes schema_version, status, artifact, and artifact_kind."""
    assert "schema_version" in output
    assert output["schema_version"] == "ariadne.review_acceptance.v2"
    assert output["accepted_semantics"] == "operation_authorized"
    assert output["accepted"] is output["operation_authorized"]
    assert "status" in output
    if output["operation_authorized"]:
        assert output["status"] == "accepted"
    else:
        assert output["status"] == "rejected"
    # Contract requires artifact and artifact_kind
    assert "artifact" in output, "missing artifact in JSON contract"
    assert output["artifact"] is not None
    assert "artifact_kind" in output, "missing artifact_kind in JSON contract"
    assert output["artifact_kind"] in ("decision", "completion")
    for key in (
        "artifact_path_validation",
        "receipt_path_validation",
        "pytest_collect_path_validation",
    ):
        assert output[key]["label"]
        assert isinstance(output[key]["contained"], bool)
        assert isinstance(output[key]["ordinary_file"], bool)
        assert isinstance(output[key]["valid"], bool)


# ===================================================================
# Accepted -- decision and completion
# ===================================================================
# NOTE: Files must be INSIDE the worktree for acceptance. Tests use
# tmp_worktree for artifact/receipt/collect. Only explicit
# "outside-worktree" tests use tmp_path.


class TestAcceptDecision:
    def test_decision_pass_accepted(self, tmp_worktree: Path):
        """A valid decision artifact with DECISION: pass is accepted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "x", "add main")
        art = _make_artifact(tmp_worktree, "Some content\n\nDECISION: pass\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "139 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.artifact_valid is True
        assert result.evidence_valid is True
        assert result.review_verdict == "pass"
        assert result.integration_authorized is True
        assert result.operation_authorized is True
        assert result.canonical_marker == "DECISION: PASS"
        assert result.receipt_cross_check == "passed"
        assert result.authoritative_pytest_count == 139
        assert result.scratch_outputs_ignored is True
        assert result.review_mode == "executable"

        # JSON contract
        j = json.loads(result.to_json())
        _check_json_contract(j)
        assert j["accepted"] is True

    def test_completion_status_complete_accepted(self, tmp_worktree: Path):
        """A valid completion artifact with STATUS: complete is accepted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "y", "add main")
        art = _make_artifact(tmp_worktree, "All done\n\nSTATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="completion")
        collect = _make_collect_file(tmp_worktree, "review/test_diary_smoke.py: 139")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="static_evidence",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.artifact_valid is True
        assert result.evidence_valid is True
        assert result.review_verdict is None
        assert result.integration_authorized is False
        assert result.operation_authorized is True
        assert result.canonical_marker == "STATUS: COMPLETE"
        assert result.authoritative_pytest_count == 139

        # JSON contract
        j = json.loads(result.to_json())
        _check_json_contract(j)

    def test_decision_pass_table_cell(self, tmp_worktree: Path):
        """Decision marker inside a Markdown table cell is accepted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "tc1", "add main")
        art = _make_artifact(tmp_worktree, "| DECISION: pass |\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.canonical_marker == "DECISION: PASS"

    def test_decision_pass_bold_table_cell(self, tmp_worktree: Path):
        """Bold decision marker inside a Markdown table cell is accepted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "tc2", "add main")
        art = _make_artifact(tmp_worktree, "| **DECISION: pass** |\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.canonical_marker == "DECISION: PASS"

    def test_completion_table_cell_backtick(self, tmp_worktree: Path):
        """Completion marker inside a Markdown table cell with backticks."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "tc3", "add main")
        art = _make_artifact(tmp_worktree, "| `STATUS: complete` |\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="completion")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.canonical_marker == "STATUS: COMPLETE"

    def test_decision_case_insensitive(self, tmp_worktree: Path):
        """Case-insensitive marker matching."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "ci1", "add main")
        art = _make_artifact(tmp_worktree, "Decision: Pass\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.canonical_marker == "DECISION: PASS"

    def test_decision_underscore_formatting(self, tmp_worktree: Path):
        """Decision marker with underscore formatting."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "uf1", "add main")
        art = _make_artifact(tmp_worktree, "_DECISION: pass_\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.canonical_marker == "DECISION: PASS"

    def test_decision_multi_column_row_accepted(self, tmp_worktree: Path):
        """Decision marker in a multi-column table row is accepted.

        e.g.: | Verdict | **`DECISION: pass`** | Notes |
        This matches runner.mjs::validArtifact() behaviour.
        """
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "mcr1", "add main")
        art = _make_artifact(
            tmp_worktree, "| Verdict | **`DECISION: pass`** | Notes |\n"
        )
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.canonical_marker == "DECISION: PASS"

    def test_completion_multi_column_row_accepted(self, tmp_worktree: Path):
        """Completion marker in a multi-column table row is accepted.

        e.g.: | Status | STATUS: complete | Notes |
        """
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "mcr2", "add main")
        art = _make_artifact(tmp_worktree, "| Status | `STATUS: complete` | Notes |\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="completion")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.canonical_marker == "STATUS: COMPLETE"

    def test_multi_column_wrong_kind_rejected(self, tmp_worktree: Path):
        """Completion-kind finds DECISION in multi-column row (wrong kind).

        e.g.: | Verdict | **DECISION: pass** | Notes | with artifact_kind=completion
        """
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "mcr3", "add main")
        art = _make_artifact(tmp_worktree, "| Verdict | **DECISION: pass** | Notes |\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="completion")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("STATUS: COMPLETE" in r for r in result.reasons), (
            f"expected STATUS: COMPLETE rejection, got {result.reasons}"
        )


class TestRejectDecision:
    def test_decision_revision_required(self, tmp_worktree: Path):
        """Decision with revision_required: marker is valid, gate accepts."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "z", "add main")
        art = _make_artifact(tmp_worktree, "Issues\n\nDECISION: revision_required\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "1 test collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.artifact_valid is True
        assert result.evidence_valid is True
        assert result.review_verdict == "revision_required"
        assert result.canonical_marker == "DECISION: REVISION_REQUIRED"
        assert result.integration_authorized is False
        assert result.operation_authorized is False
        assert result.accepted is False
        assert result.reasons == []
        output = json.loads(result.to_json())
        _check_json_contract(output)
        assert output["accepted"] is False
        assert output["accepted"] is output["operation_authorized"]

    def test_pass_with_malformed_receipt_has_no_authority(self, tmp_worktree: Path):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "bad-receipt", "add main")
        art = _make_artifact(tmp_worktree, "DECISION: PASS\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision", status="failed")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )

        assert result.artifact_valid is True
        assert result.evidence_valid is False
        assert result.review_verdict == "pass"
        assert result.integration_authorized is False
        assert result.operation_authorized is False

    @pytest.mark.parametrize(
        "body",
        [
            "DECISION: PASS\nDECISION: PASS\n",
            "DECISION: PASS\nDECISION: REVISION_REQUIRED\n",
            "DECISION: PASS\n" + "\n".join(f"evidence {index}" for index in range(9)),
            "DECISION: INCONCLUSIVE\n",
        ],
    )
    def test_invalid_decision_marker_forms_never_authorize(
        self, tmp_worktree: Path, body: str
    ):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "invalid-marker", "add main")
        art = _make_artifact(tmp_worktree, body)
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )

        assert result.artifact_valid is False
        assert result.evidence_valid is True
        assert result.integration_authorized is False
        assert result.operation_authorized is False

    @pytest.mark.parametrize("indentation", [" ", "  ", "   "])
    def test_api_and_cli_reject_early_pass_followed_by_indented_visible_lines(
        self, tmp_worktree: Path, indentation: str
    ) -> None:
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(
            tmp_worktree, "src/main.py", f"terminal-{len(indentation)}", "add main"
        )
        body = "DECISION: PASS\n" + "\n".join(
            f"{indentation}visible evidence line {index}" for index in range(9)
        )
        art = _make_artifact(tmp_worktree, body)
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )

        assert result.artifact_valid is False
        assert result.artifact_reason_code == "terminal_marker_not_near_artifact_end"
        assert result.review_verdict is None
        assert result.evidence_valid is True
        assert result.integration_authorized is False
        assert result.operation_authorized is False

        cli = _run_acceptance_cli(
            artifact=art,
            artifact_kind="decision",
            receipt=receipt,
            worktree=tmp_worktree,
            branch=branch,
            commit=commit,
            collect=collect,
        )
        assert cli.returncode == 1, cli.stderr
        output = json.loads(cli.stdout)
        assert output["artifact_valid"] is False
        assert output["artifact_reason_code"] == (
            "terminal_marker_not_near_artifact_end"
        )
        assert output["review_verdict"] is None
        assert output["integration_authorized"] is False
        assert output["operation_authorized"] is False

    def test_verdict_only_rejected(self, tmp_worktree: Path):
        """VERDICT without DECISION is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "v", "add main")
        art = _make_artifact(tmp_worktree, "Some review\n\nVERDICT: pass\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="decision",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("VERDICT" in r for r in result.reasons)

    def test_wrong_kind_marker(self, tmp_worktree: Path):
        """Completion-kind with DECISION marker (wrong kind) fails."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "w", "add main")
        art = _make_artifact(tmp_worktree, "DECISION: pass\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="completion")
        collect = _make_collect_file(tmp_worktree, "10 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("STATUS: COMPLETE" in r for r in result.reasons)

    def test_wrong_kind_table_cell(self, tmp_worktree: Path):
        """Completion-kind with DECISION in table cell (wrong kind) fails."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "wk1", "add main")
        art = _make_artifact(tmp_worktree, "| DECISION: pass |\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="completion")
        collect = _make_collect_file(tmp_worktree, "10 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("STATUS: COMPLETE" in r for r in result.reasons)

    def test_receipt_status_mismatch(self, tmp_worktree: Path):
        """Receipt with wrong status is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "r", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, status="failed")
        collect = _make_collect_file(tmp_worktree, "3 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("status" in r for r in result.reasons)

    def test_receipt_artifact_kind_mismatch(self, tmp_worktree: Path):
        """Receipt with wrong artifact_kind is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "k", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "3 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("artifact_kind" in r for r in result.reasons)

    def test_receipt_artifact_observed_false(self, tmp_worktree: Path):
        """Receipt with artifact_observed: false is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "o", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, artifact_observed=False)
        collect = _make_collect_file(tmp_worktree, "3 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("artifact_observed" in r for r in result.reasons)

    def test_receipt_permission_prompt_observed_true(self, tmp_worktree: Path):
        """Receipt with permission_prompt_observed: true is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "p", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, permission_prompt_observed=True)
        collect = _make_collect_file(tmp_worktree, "3 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("permission_prompt_observed" in r for r in result.reasons)

    def test_receipt_cleanup_not_confirmed(self, tmp_worktree: Path):
        """Receipt with cleanup not confirmed is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "c", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, process_cleanup_confirmed=False)
        collect = _make_collect_file(tmp_worktree, "3 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("process_cleanup_confirmed" in r for r in result.reasons)

    def test_non_dict_receipt_rejected(self, tmp_worktree: Path):
        """Receipt JSON that is not an object (e.g. array) is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "nd1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        # Write a JSON array instead of an object
        receipt = tmp_worktree / "receipt.json"
        receipt.write_text('["not", "a", "dict"]')
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("must be an object" in r for r in result.reasons)

    def test_non_object_receipt_top_level_string_rejected(self, tmp_worktree: Path):
        """Receipt JSON that is a top-level string (not object) is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "nd2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = tmp_worktree / "receipt.json"
        receipt.write_text('"just a string"')
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("must be an object" in r for r in result.reasons)


class TestBranchAncestry:
    def test_wrong_branch_rejected(self, tmp_worktree: Path):
        """Wrong branch name is rejected."""
        _commit_file(tmp_worktree, "src/main.py", "a", "add main")
        head = _get_head(tmp_worktree)
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch="nonexistent-branch",
            candidate_commit=head,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("branch" in r.lower() for r in result.reasons)

    def test_non_ancestor_candidate_rejected(self, tmp_worktree: Path, tmp_path: Path):
        """A commit that is not an ancestor of HEAD is rejected."""
        branch = _get_branch(tmp_worktree)
        orphan = tmp_path / "orphan"
        orphan.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "init"], cwd=str(orphan), check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "t@t.com"],
            cwd=str(orphan),
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "T"],
            cwd=str(orphan),
            check=True,
            capture_output=True,
        )
        (orphan / "f.txt").write_text("orphan")
        subprocess.run(
            ["git", "add", "f.txt"], cwd=str(orphan), check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "orphan"],
            cwd=str(orphan),
            check=True,
            capture_output=True,
        )
        orphan_commit = _get_head(orphan)

        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=orphan_commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any(
            "ancestor" in r.lower()
            or "ancestry check" in r.lower()
            or "error" in r.lower()
            for r in result.reasons
        )


# ===================================================================
# Outside-worktree and missing paths
# ===================================================================
# These tests place files OUTSIDE the worktree (in tmp_path, the parent
# of tmp_worktree) to verify boundary checks.


class TestPathBoundaries:
    def test_artifact_outside_worktree_rejected(
        self, tmp_worktree: Path, tmp_path: Path
    ):
        """Artifact path outside the worktree is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "x", "add main")
        art = _make_artifact(tmp_path, "STATUS: complete\n")
        receipt = _make_receipt(tmp_path)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("outside" in r.lower() for r in result.reasons)

    def test_missing_artifact_rejected(self, tmp_worktree: Path):
        """A non-existent artifact path is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "m", "add main")
        missing = tmp_worktree / "nonexistent.md"
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=missing,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("not an ordinary file" in r.lower() for r in result.reasons)

    def test_scratch_substitute_not_accepted(self, tmp_worktree: Path, tmp_path: Path):
        """A valid scratch file at another path must not rescue an invalid
        declared artifact (policy enforcement via worktree check)."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "s", "add main")
        art = _make_artifact(tmp_path, "STATUS: complete\n", name="declared.md")
        (tmp_worktree / "scratch.md").write_text("STATUS: complete\n")
        receipt = _make_receipt(tmp_path)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False


class TestStructuredInvalidEvidence:
    @pytest.mark.parametrize(
        "invalid_case",
        [
            "outside_artifact",
            "outside_receipt",
            "outside_collect",
            "invalid_utf8_artifact",
            "invalid_utf8_receipt",
            "invalid_utf8_collect",
        ],
    )
    def test_api_and_cli_return_structured_rejection_and_exit_1(
        self, invalid_case: str, tmp_worktree: Path, tmp_path: Path
    ) -> None:
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", invalid_case, "evidence")
        art = _make_artifact(tmp_worktree, "STATUS: COMPLETE\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        surface = invalid_case.removeprefix("outside_").removeprefix("invalid_utf8_")
        if invalid_case == "outside_artifact":
            art = _make_artifact(
                tmp_path, "STATUS: COMPLETE\n", name="outside-artifact.md"
            )
        elif invalid_case == "outside_receipt":
            receipt = _make_receipt(tmp_path)
        elif invalid_case == "outside_collect":
            collect = _make_collect_file(
                tmp_path, "5 tests collected", name="outside-collect.txt"
            )
        elif invalid_case == "invalid_utf8_artifact":
            art.write_bytes(b"\xff\xfeDECISION")
        elif invalid_case == "invalid_utf8_receipt":
            receipt.write_bytes(b"\xff\xfe{")
        else:
            collect.write_bytes(b"\xff\xfe5")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )

        validation = getattr(
            result,
            {
                "artifact": "artifact_path_validation",
                "receipt": "receipt_path_validation",
                "collect": "pytest_collect_path_validation",
            }[surface],
        )
        assert result.evidence_valid is False
        assert result.operation_authorized is False
        assert result.integration_authorized is False
        if surface == "artifact":
            assert result.artifact_valid is False
        else:
            assert result.artifact_valid is True
        if invalid_case.startswith("outside_"):
            assert validation.contained is False
            assert validation.valid is False
            assert any("outside" in reason.lower() for reason in result.reasons)
        else:
            assert validation.contained is True
            assert validation.ordinary_file is True
            assert validation.valid is True
            assert any("decode" in reason.lower() for reason in result.reasons)

        cli = _run_acceptance_cli(
            artifact=art,
            artifact_kind="completion",
            receipt=receipt,
            worktree=tmp_worktree,
            branch=branch,
            commit=commit,
            collect=collect,
        )
        assert cli.returncode == 1, cli.stderr
        output = json.loads(cli.stdout)
        assert output["evidence_valid"] is False
        assert output["operation_authorized"] is False
        assert output["integration_authorized"] is False


class TestHostileMarkerContexts:
    @pytest.mark.parametrize(
        ("body", "kind", "reason_code"),
        [
            (
                "Example:\n```text\nDECISION: PASS\n```",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "~~~text\nSTATUS: COMPLETE\n~~~",
                "completion",
                "non_authoritative_marker_context",
            ),
            (
                "    DECISION: PASS",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "Human-visible revision required.\n<!-- DECISION: PASS -->",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: PASS\n<!-- DECISION: REVISION_REQUIRED -->",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: REVISION_REQUIRED\n```\nDECISION: PASS\n```",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "Example: `left | DECISION: PASS | right`",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "> | DECISION: PASS |",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "- | DECISION: PASS |",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "not a table | DECISION: PASS | quoted example",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                r"\| DECISION: PASS \|",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: PASS\nExample: `left | DECISION: REVISION_REQUIRED | right`",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: PASS\n> | DECISION: REVISION_REQUIRED |",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: PASS\n- | DECISION: REVISION_REQUIRED |",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: PASS\n"
                "not a table | DECISION: REVISION_REQUIRED | quoted example",
                "decision",
                "non_authoritative_marker_context",
            ),
            (
                "DECISION: PASS\n" + r"\| DECISION: REVISION_REQUIRED \|",
                "decision",
                "non_authoritative_marker_context",
            ),
            ("DECISıON: PASS", "decision", "non_ascii_marker_lexeme"),
            ("ſTATUS: COMPLETE", "completion", "non_ascii_marker_lexeme"),
        ],
    )
    def test_api_and_cli_never_authorize_hidden_or_non_ascii_markers(
        self,
        body: str,
        kind: str,
        reason_code: str,
        tmp_worktree: Path,
    ) -> None:
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", body, "marker case")
        art = _make_artifact(tmp_worktree, body)
        receipt = _make_receipt(tmp_worktree, artifact_kind=kind)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind=kind,
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )

        assert result.artifact_valid is False
        assert result.evidence_valid is True
        assert result.integration_authorized is False
        assert result.operation_authorized is False
        assert result.artifact_reason_code == reason_code

        cli = _run_acceptance_cli(
            artifact=art,
            artifact_kind=kind,
            receipt=receipt,
            worktree=tmp_worktree,
            branch=branch,
            commit=commit,
            collect=collect,
        )
        assert cli.returncode == 1, cli.stderr
        output = json.loads(cli.stdout)
        assert output["artifact_valid"] is False
        assert output["integration_authorized"] is False
        assert output["operation_authorized"] is False


class TestWorktreeRelativePaths:
    def test_relative_artifact_resolved_against_worktree(self, tmp_worktree: Path):
        """Artifact with relative path is resolved against the worktree."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "rp1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n", name="sub/artifact.md")
        receipt = _make_receipt(tmp_worktree, artifact_rel="sub/artifact.md")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        # Pass relative path "sub/artifact.md"
        result = accept_review_artifact(
            artifact_path="sub/artifact.md",
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"

    def test_relative_artifact_from_different_cwd(
        self, tmp_worktree: Path, tmp_path: Path
    ):
        """Relative paths are resolved against worktree, not caller cwd."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "rp2", "add main")
        # File is inside worktree at sub/artifact.md
        art = _make_artifact(tmp_worktree, "STATUS: complete\n", name="sub/artifact.md")
        receipt = _make_receipt(tmp_worktree, artifact_rel="sub/artifact.md")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        # Run from a different cwd
        other_dir = tmp_path / "other"
        other_dir.mkdir(parents=True, exist_ok=True)
        old_cwd = Path.cwd()
        try:
            os.chdir(str(other_dir))
            result = accept_review_artifact(
                artifact_path="sub/artifact.md",
                artifact_kind="completion",
                receipt_path=receipt,
                review_worktree=tmp_worktree,
                expected_branch=branch,
                candidate_commit=commit,
                pytest_collect_path=collect,
                review_mode="executable",
            )
        finally:
            os.chdir(str(old_cwd))

        assert result.accepted is True, f"reasons: {result.reasons}"

    def test_relative_receipt_resolved_against_worktree(self, tmp_worktree: Path):
        """Receipt with relative path is resolved against the worktree."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "rp3", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        _make_receipt(tmp_worktree)  # creates receipt.json in worktree

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path="receipt.json",
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=_make_collect_file(tmp_worktree, "5 tests collected"),
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"

    def test_relative_collect_resolved_against_worktree(self, tmp_worktree: Path):
        """Pytest collect path with relative path is resolved against worktree."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "rp4", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        _make_collect_file(tmp_worktree, "5 tests collected")  # creates collect.txt

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path="collect.txt",
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"


class TestPytestCollection:
    def test_single_test_collected(self, tmp_worktree: Path):
        """'1 test collected' parses correctly."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "t", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "1 test collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.authoritative_pytest_count == 1

    def test_review_diary_smoke_format(self, tmp_worktree: Path):
        """'review/test_diary_smoke.py: 139' format."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "d", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "review/test_diary_smoke.py: 139")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.authoritative_pytest_count == 139

    def test_missing_collect_output_rejected(self, tmp_worktree: Path):
        """Missing pytest collect file is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "m2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        missing = tmp_worktree / "does_not_exist.txt"

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=missing,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("read error" in r.lower() for r in result.reasons)

    def test_zero_collect_rejected(self, tmp_worktree: Path):
        """Zero tests collected is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "z2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "0 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert result.authoritative_pytest_count is None

    def test_conflicting_count_rejected(self, tmp_worktree: Path):
        """Conflicting collection counts are rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "c2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree, "139 tests collected\nreview/test_diary_smoke.py: 140"
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert result.authoritative_pytest_count is None

    def test_collect_file_with_spaces(self, tmp_worktree: Path):
        """Pytest collect file path with spaces is handled correctly."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "sp1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)

        # Create collect file with spaces in the path
        spaced_dir = tmp_worktree / "my collect"
        spaced_dir.mkdir(parents=True, exist_ok=True)
        collect = _make_collect_file(
            spaced_dir, "5 tests collected", name="output collection.txt"
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.authoritative_pytest_count == 5

    def test_arbitrary_colon_number_rejected(self, tmp_worktree: Path):
        """Arbitrary colon-number lines (not .py: N) are rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "an1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "total: 42")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        # "total: 42" is not .py: N and not "N test(s) collected"
        assert result.authoritative_pytest_count is None
        assert result.accepted is False

    def test_py_file_collect_format(self, tmp_worktree: Path):
        """'.py: N' format is accepted (pytest file output)."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "pf1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree, "tests/test_ariadne_review_acceptance.py: 47"
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True
        assert result.authoritative_pytest_count == 47

    # ------------------------------------------------------------------
    # Multi-file aggregation contract (S7 revision 3)
    # ------------------------------------------------------------------

    def test_two_files_aggregated_30_plus_52_equals_82(self, tmp_worktree: Path):
        """Two per-file lines 30 + 52 = 82 are accepted and summed."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "agg1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree,
            "tests/test_ariadne_deepcode_adapter_settings.py: 30\n"
            "tests/test_ariadne_review_acceptance.py: 52",
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.authoritative_pytest_count == 82

    def test_one_file_139_accepted(self, tmp_worktree: Path):
        """Single per-file line 139 -> 139 accepted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "agg2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree, "tests/test_ariadne_review_acceptance.py: 139"
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.authoritative_pytest_count == 139

    def test_two_files_plus_matching_summary_accepted(self, tmp_worktree: Path):
        """Two .py lines plus a matching summary count are accepted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "agg3", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree,
            "tests/test_ariadne_deepcode_adapter_settings.py: 30\n"
            "tests/test_ariadne_review_acceptance.py: 52\n"
            "82 tests collected",
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.authoritative_pytest_count == 82

    def test_two_files_plus_mismatching_summary_rejected(self, tmp_worktree: Path):
        """Two .py lines with a non-matching summary count are rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "agg4", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree,
            "tests/test_ariadne_deepcode_adapter_settings.py: 30\n"
            "tests/test_ariadne_review_acceptance.py: 52\n"
            "80 tests collected",
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert result.authoritative_pytest_count is None

    def test_duplicate_same_path_same_count_not_double_counted(
        self, tmp_worktree: Path
    ):
        """Same path with same count is not double-counted."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "agg5", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree,
            "tests/test_a.py: 10\ntests/test_a.py: 10",
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is True, f"reasons: {result.reasons}"
        assert result.authoritative_pytest_count == 10

    def test_duplicate_same_path_different_count_rejected(self, tmp_worktree: Path):
        """Same path with different counts is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "agg6", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(
            tmp_worktree,
            "tests/test_a.py: 10\ntests/test_a.py: 15",
        )

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert result.authoritative_pytest_count is None


class TestWorkerCountMismatch:
    def test_worker_count_mismatch_flagged(self, tmp_worktree: Path):
        """Worker-reported count that does not match collection is flagged."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "w2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "139 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
            worker_reported_count=135,
        )
        assert result.accepted is False
        assert result.worker_count_mismatch is True
        assert result.worker_reported_count == 135
        assert result.authoritative_pytest_count == 139
        assert any(
            "mismatch" in r.lower() or "worker reported" in r.lower()
            for r in result.reasons
        )

    def test_worker_count_matches(self, tmp_worktree: Path):
        """Worker-reported count matching collection does not cause mismatch."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "m3", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "139 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.worker_count_mismatch is False
        assert result.worker_reported_count is None
        assert not any(
            "mismatch" in r.lower() or "worker reported" in r.lower()
            for r in result.reasons
        )


class TestReceiptProhibition:
    def test_receipt_artifact_path_rejected(self, tmp_worktree: Path):
        """Receipt containing artifact_path is rejected."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "ap", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, extra={"artifact_path": "/some/path"})
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        assert any("artifact_path" in r for r in result.reasons)


class TestCLI:
    def test_cli_help(self):
        result = _run_cli("--help")
        assert result.returncode == 0
        assert "Deterministic review-acceptance gate" in result.stdout

    def test_cli_direct_invocation(self, tmp_worktree: Path):
        """Direct script invocation (without PYTHONPATH) works via sys.path bootstrap."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "di1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        script = (
            Path(__file__).resolve().parent.parent
            / "scripts"
            / "ariadne_review_acceptance.py"
        )
        # Run without PYTHONPATH — sys.path bootstrap in the script handles it
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--artifact",
                str(art),
                "--artifact-kind",
                "completion",
                "--receipt",
                str(receipt),
                "--worktree",
                str(tmp_worktree),
                "--expected-branch",
                branch,
                "--candidate-commit",
                commit,
                "--pytest-collect-output",
                str(collect),
                "--review-mode",
                "executable",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_cli_accepted_exit_0(self, tmp_worktree: Path):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "cli1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = _run_cli(
            "--artifact",
            str(art),
            "--artifact-kind",
            "completion",
            "--receipt",
            str(receipt),
            "--worktree",
            str(tmp_worktree),
            "--expected-branch",
            branch,
            "--candidate-commit",
            commit,
            "--pytest-collect-output",
            str(collect),
            "--review-mode",
            "executable",
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        output = json.loads(result.stdout)
        assert output["accepted"] is True
        _check_json_contract(output)

    def test_cli_rejected_exit_1(self, tmp_worktree: Path):
        _commit_file(tmp_worktree, "src/main.py", "cli2", "add main")
        head = _get_head(tmp_worktree)
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = _run_cli(
            "--artifact",
            str(art),
            "--artifact-kind",
            "completion",
            "--receipt",
            str(receipt),
            "--worktree",
            str(tmp_worktree),
            "--expected-branch",
            "nonexistent",
            "--candidate-commit",
            head,
            "--pytest-collect-output",
            str(collect),
            "--review-mode",
            "executable",
        )
        assert result.returncode == 1

    def test_cli_revision_required_exit_1_with_explicit_negative_verdict(
        self, tmp_worktree: Path
    ):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "cli-negative", "add main")
        art = _make_artifact(tmp_worktree, "DECISION: REVISION_REQUIRED\n")
        receipt = _make_receipt(tmp_worktree, artifact_kind="decision")
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = _run_cli(
            "--artifact",
            str(art),
            "--artifact-kind",
            "decision",
            "--receipt",
            str(receipt),
            "--worktree",
            str(tmp_worktree),
            "--expected-branch",
            branch,
            "--candidate-commit",
            commit,
            "--pytest-collect-output",
            str(collect),
            "--review-mode",
            "executable",
        )

        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["artifact_valid"] is True
        assert output["evidence_valid"] is True
        assert output["review_verdict"] == "revision_required"
        assert output["integration_authorized"] is False
        assert output["operation_authorized"] is False
        assert output["accepted"] is False

    def test_cli_missing_required_arg_exit_2(self):
        result = _run_cli("--artifact", "x.md")
        assert result.returncode == 2

    def test_cli_json_output_shape(self, tmp_worktree: Path):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "json1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = _run_cli(
            "--artifact",
            str(art),
            "--artifact-kind",
            "completion",
            "--receipt",
            str(receipt),
            "--worktree",
            str(tmp_worktree),
            "--expected-branch",
            branch,
            "--candidate-commit",
            commit,
            "--pytest-collect-output",
            str(collect),
            "--review-mode",
            "static_evidence",
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        for key in (
            "accepted",
            "reasons",
            "artifact",
            "artifact_kind",
            "observed_branch",
            "observed_head",
            "ancestry_result",
            "canonical_marker",
            "receipt_cross_check",
            "authoritative_pytest_count",
            "worker_reported_count",
            "worker_count_mismatch",
            "review_mode",
            "scratch_outputs_ignored",
            "schema_version",
            "status",
        ):
            assert key in output, f"missing key: {key}"
        assert output["review_mode"] == "static_evidence"
        assert output["scratch_outputs_ignored"] is True
        assert output["schema_version"] == "ariadne.review_acceptance.v2"
        assert output["status"] == "accepted"
        assert output["artifact"] is not None
        assert output["artifact_kind"] == "completion"


class TestReviewModes:
    def test_executable_mode(self, tmp_worktree: Path):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "em", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.review_mode == "executable"

    def test_static_evidence_mode(self, tmp_worktree: Path):
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "se", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="static_evidence",
        )
        assert result.review_mode == "static_evidence"


class TestStrictSettingsUnchanged:
    def test_reject_does_not_mutate_settings(self, tmp_worktree: Path):
        """Rejection is pure and does not mutate input files."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "pure", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree, status="failed")
        before = receipt.read_text()
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = accept_review_artifact(
            artifact_path=art,
            artifact_kind="completion",
            receipt_path=receipt,
            review_worktree=tmp_worktree,
            expected_branch=branch,
            candidate_commit=commit,
            pytest_collect_path=collect,
            review_mode="executable",
        )
        assert result.accepted is False
        after = receipt.read_text()
        assert before == after


class TestInvalidReviewMode:
    def test_invalid_mode_raises_value_error(self, tmp_worktree: Path):
        """A direct API call with invalid review_mode raises ValueError."""
        import pytest as _pytest

        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "inv1", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        with _pytest.raises(ValueError, match="invalid review_mode"):
            accept_review_artifact(
                artifact_path=art,
                artifact_kind="completion",
                receipt_path=receipt,
                review_worktree=tmp_worktree,
                expected_branch=branch,
                candidate_commit=commit,
                pytest_collect_path=collect,
                review_mode="invalid_mode",  # type: ignore[arg-type]
            )

    def test_cli_invalid_mode_rejected(self, tmp_worktree: Path):
        """CLI invocation with invalid review_mode exits 2 (argparse error)."""
        branch = _get_branch(tmp_worktree)
        commit = _commit_file(tmp_worktree, "src/main.py", "inv2", "add main")
        art = _make_artifact(tmp_worktree, "STATUS: complete\n")
        receipt = _make_receipt(tmp_worktree)
        collect = _make_collect_file(tmp_worktree, "5 tests collected")

        result = _run_cli(
            "--artifact",
            str(art),
            "--artifact-kind",
            "completion",
            "--receipt",
            str(receipt),
            "--worktree",
            str(tmp_worktree),
            "--expected-branch",
            branch,
            "--candidate-commit",
            commit,
            "--pytest-collect-output",
            str(collect),
            "--review-mode",
            "invalid_mode",
        )
        assert result.returncode == 2
