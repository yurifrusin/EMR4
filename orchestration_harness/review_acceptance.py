"""Deterministic review-acceptance gate for Deep Code worker artifacts.

This module is standard-library-only. It validates that a worker's submitted
artifact, adapter receipt, worktree branch/ancestry, and pytest collection
output all satisfy the acceptance contract before the orchestrator integrates
the result.

Exported API
------------
- ``accept_review_artifact(...)`` — the single public validator.
- ``ReviewAcceptance`` dataclass — the structured result.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from orchestration_harness.verdict import (
    ArtifactKind,
    VerdictAssessment,
    parse_artifact_verdict,
)

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

ReviewMode = Literal["executable", "static_evidence"]

_VALID_REVIEW_MODES = frozenset({"executable", "static_evidence"})


@dataclass(frozen=True)
class DeclaredPathValidation:
    """Structured containment and ordinary-file state for declared evidence."""

    label: str
    resolved_path: Path
    contained: bool
    ordinary_file: bool
    valid: bool
    reason: str | None


@dataclass(frozen=True)
class ReviewAcceptance:
    """Deterministic, JSON-serialisable result of the acceptance gate."""

    artifact_valid: bool
    evidence_valid: bool
    review_verdict: str | None
    integration_authorized: bool
    operation_authorized: bool
    reasons: list[str]
    artifact: str | None
    artifact_kind: str | None
    observed_branch: str | None
    observed_head: str | None
    ancestry_result: str | None
    canonical_marker: str | None
    receipt_cross_check: str | None
    authoritative_pytest_count: int | None
    worker_reported_count: int | None
    worker_count_mismatch: bool
    review_mode: ReviewMode
    scratch_outputs_ignored: bool
    artifact_reason_code: str
    artifact_path_validation: DeclaredPathValidation
    receipt_path_validation: DeclaredPathValidation
    pytest_collect_path_validation: DeclaredPathValidation

    @property
    def accepted(self) -> bool:
        """Compatibility projection with operation-authorization semantics."""

        return self.operation_authorized

    def to_json(self) -> str:
        """Serialise to JSON with schema_version and status fields."""
        data = asdict(self)
        data["schema_version"] = "ariadne.review_acceptance.v2"
        data["accepted"] = self.accepted
        data["accepted_semantics"] = "operation_authorized"
        data["status"] = "accepted" if self.operation_authorized else "rejected"
        return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Receipt field contract
# ---------------------------------------------------------------------------

_REQUIRED_RECEIPT_FIELDS: dict[str, object] = {
    "status": "completed",
    "artifact": ...,  # dynamic key — must be present (value checked later)
    "artifact_kind": ...,  # dynamic key — must be present and match
    "artifact_observed": True,
    "permission_prompt_observed": False,
    "process_cleanup_confirmed": True,
}


def _check_receipt(
    receipt: dict, expected_kind: str, expected_artifact_rel: str | None
) -> str | None:
    """Return ``None`` if the receipt passes, or a reason string on failure.

    The receipt must NOT contain an ``artifact_path`` key.
    """
    # Prohibited key
    if "artifact_path" in receipt:
        return "receipt contains forbidden artifact_path key"

    # Required values
    for key, expected_val in _REQUIRED_RECEIPT_FIELDS.items():
        if key in ("artifact", "artifact_kind"):
            continue  # checked below
        actual = receipt.get(key)
        if actual != expected_val:
            return f"receipt.{key} expected {expected_val!r}, got {actual!r}"

    # Dynamic fields
    if expected_artifact_rel is None:
        return "receipt artifact binding unavailable because artifact path is invalid"

    actual_artifact = receipt.get("artifact")
    if actual_artifact != expected_artifact_rel:
        return (
            f"receipt.artifact expected {expected_artifact_rel!r}, "
            f"got {actual_artifact!r}"
        )

    actual_kind = receipt.get("artifact_kind")
    if actual_kind != expected_kind:
        return f"receipt.artifact_kind expected {expected_kind!r}, got {actual_kind!r}"

    return None


def _artifact_reason(assessment: VerdictAssessment) -> str:
    """Project a stable kernel reason into the retained human reason list."""

    expected = (
        "DECISION: PASS or DECISION: REVISION_REQUIRED"
        if assessment.artifact_kind is ArtifactKind.DECISION
        else "STATUS: COMPLETE"
    )
    messages = {
        "missing_authoritative_marker": f"missing authoritative {expected} marker in artifact",
        "duplicate_authoritative_markers": "duplicate authoritative artifact markers",
        "conflicting_decision_markers": "conflicting DECISION: PASS and DECISION: REVISION_REQUIRED markers",
        "terminal_marker_not_near_artifact_end": "authoritative marker is outside the bounded terminal window",
        "unsupported_decision_marker": "unsupported DECISION: value in artifact",
        "unsupported_status_marker": "unsupported STATUS: value in artifact",
        "wrong_artifact_kind_marker": f"wrong-kind artifact marker; expected {expected}",
        "legacy_verdict_marker": "legacy VERDICT: marker is not authoritative",
        "non_authoritative_marker_context": "marker-like authority appears in a non-authoritative Markdown context",
        "non_ascii_marker_lexeme": "marker-like authority contains non-ASCII protocol text",
    }
    return messages[assessment.reason_code]


# ---------------------------------------------------------------------------
# Pytest collection parsing
# ---------------------------------------------------------------------------
#
# Two distinct forms are accepted:
#   1. Per-file ".py: N" lines — normalised by file path, conflicting
#      duplicate counts for the same path are rejected, unique file counts
#      are summed.
#   2. Summary "N test(s) collected" lines — all summary counts must agree.
#
# If both forms are present the summary count must equal the per-file sum.
# If only one form is present, use it.
# Zero, missing, conflicting duplicate, or summary-versus-sum mismatch
# are rejected. Arbitrary colon-number patterns (e.g. "total: 42") are
# rejected because they don't match ".py: N".


def _parse_pytest_collect(text: str) -> int | None:
    """Return the collected test count, or ``None`` if parsing fails.

    Parses per-file ``.py: N`` entries and summary ``N test(s) collected``
    entries, aggregating them according to the contract documented above.
    """
    # -- Per-file .py: N entries (pytest file output form) -----------------
    file_counts: dict[str, int] = {}
    for m in re.finditer(r"^(.*?\.py):\s*(\d+)\s*$", text, re.MULTILINE):
        path = m.group(1).strip()
        count = int(m.group(2))
        if path in file_counts:
            if file_counts[path] != count:
                return None  # conflicting count for same path
        else:
            file_counts[path] = count

    # -- Summary N test(s) collected entries --------------------------------
    summary_counts: set[int] = set()
    for m in re.finditer(r"(\d+)\s+tests?\s+collected", text):
        summary_counts.add(int(m.group(1)))

    if len(summary_counts) > 1:
        return None  # conflicting summary counts

    file_sum = sum(file_counts.values()) if file_counts else None
    summary_val = next(iter(summary_counts)) if len(summary_counts) == 1 else None

    # -- Reconcile forms ----------------------------------------------------
    if file_sum is not None and summary_val is not None:
        # Both forms present — must agree
        if file_sum != summary_val:
            return None
        if file_sum <= 0:
            return None
        return file_sum

    if file_sum is not None:
        # Only per-file form
        if file_sum <= 0:
            return None
        return file_sum

    if summary_val is not None:
        # Only summary form
        if summary_val <= 0:
            return None
        return summary_val

    return None  # no recognised form


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git_command(args: list[str], cwd: Path) -> str | None:
    """Run ``git <args>`` in *cwd* with ``shell=False``.

    Returns stdout (stripped) on success, ``None`` on failure.
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (OSError, UnicodeError, subprocess.TimeoutExpired):
        return None


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def _resolve_relative_to_worktree(path: str | Path, worktree: Path) -> Path:
    """Resolve *path* relative to *worktree* if it is not absolute.

    Returns the resolved absolute Path.
    """
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (worktree / p).resolve()


def _validate_declared_path(
    path: str | Path, worktree: Path, label: str
) -> DeclaredPathValidation:
    """Resolve and validate one path without opening its declared content."""

    try:
        resolved = _resolve_relative_to_worktree(path, worktree)
    except (OSError, RuntimeError):
        unresolved = Path(path)
        return DeclaredPathValidation(
            label=label,
            resolved_path=unresolved,
            contained=False,
            ordinary_file=False,
            valid=False,
            reason=f"{label} path resolution error: {unresolved}",
        )

    try:
        resolved.relative_to(worktree)
        contained = True
    except ValueError:
        contained = False

    try:
        ordinary_file = resolved.is_file()
    except (OSError, RuntimeError):
        ordinary_file = False

    if not contained:
        reason = f"{label} is outside the review worktree: {resolved}"
    elif not ordinary_file:
        reason = f"{label} read error: path is not an ordinary file: {resolved}"
    else:
        reason = None
    return DeclaredPathValidation(
        label=label,
        resolved_path=resolved,
        contained=contained,
        ordinary_file=ordinary_file,
        valid=contained and ordinary_file,
        reason=reason,
    )


# ---------------------------------------------------------------------------
# Public validator
# ---------------------------------------------------------------------------


def accept_review_artifact(
    *,
    artifact_path: str | Path,
    artifact_kind: ArtifactKind | str,
    receipt_path: str | Path,
    review_worktree: str | Path,
    expected_branch: str,
    candidate_commit: str,
    pytest_collect_path: str | Path,
    review_mode: ReviewMode,
    worker_reported_count: int | None = None,
) -> ReviewAcceptance:
    """Deterministic acceptance gate for a worker review artifact.

    Parameters
    ----------
    artifact_path:
        Path to the worker's submitted review artifact. Relative paths are
        resolved against *review_worktree*.
    artifact_kind:
        ``"decision"`` or ``"completion"``.
    receipt_path:
        Path to the adapter receipt JSON file. Relative paths are resolved
        against *review_worktree*.
    review_worktree:
        Path to the review worktree (cwd for git commands).
    expected_branch:
        Exact branch name expected (e.g. ``"claude/current"``).
    candidate_commit:
        Full or abbreviated commit SHA that should be an ancestor of HEAD.
    pytest_collect_path:
        Path to a file containing captured ``pytest --collect-only -q`` output.
        Relative paths are resolved against *review_worktree*.
    review_mode:
        ``"executable"`` or ``"static_evidence"``.
    worker_reported_count:
        Optional ``N passed`` claim from the worker. Never replaces
        authoritative collection evidence.

    Returns
    -------
    ReviewAcceptance
        A frozen dataclass with explicit artifact, evidence, verdict and
        authorization fields plus the retained observational evidence.
    """
    worktree = Path(review_worktree).resolve()

    # -- Runtime validation (before any I/O or git calls) ------------------
    if review_mode not in _VALID_REVIEW_MODES:
        raise ValueError(
            f"invalid review_mode: {review_mode!r}; "
            f"must be one of {sorted(_VALID_REVIEW_MODES)}"
        )
    try:
        kind = (
            artifact_kind
            if isinstance(artifact_kind, ArtifactKind)
            else ArtifactKind(artifact_kind)
        )
    except ValueError as error:
        raise ValueError(f"invalid artifact_kind: {artifact_kind!r}") from error

    # Resolve and type-check each declaration independently before content I/O.
    artifact_path_validation = _validate_declared_path(
        artifact_path, worktree, "artifact"
    )
    receipt_path_validation = _validate_declared_path(receipt_path, worktree, "receipt")
    pytest_collect_path_validation = _validate_declared_path(
        pytest_collect_path, worktree, "pytest_collect"
    )
    art = artifact_path_validation.resolved_path
    receipt_file = receipt_path_validation.resolved_path
    collect = pytest_collect_path_validation.resolved_path

    evidence_reasons: list[str] = []
    artifact_reasons: list[str] = []
    observed_branch: str | None = None
    observed_head: str | None = None
    ancestry_result: str | None = None
    canonical_marker: str | None = None
    receipt_cross_check: str | None = None
    authoritative_pytest_count: int | None = None
    worker_count_mismatch = False
    assessment = parse_artifact_verdict("", kind)

    # -- Check: Artifact, receipt, and collect are ordinary files inside worktree
    for validation in (
        artifact_path_validation,
        receipt_path_validation,
        pytest_collect_path_validation,
    ):
        if validation.reason is not None:
            evidence_reasons.append(validation.reason)

    # -- Check: Never search other files for substitute --------------------
    # (Policy enforcement — if declared paths are outside/missing, we do not
    #  look elsewhere.)

    # -- Check: Receipt content --------------------------------------------
    if receipt_path_validation.valid:
        try:
            receipt_data = json.loads(receipt_file.read_text(encoding="utf-8"))
            if not isinstance(receipt_data, dict):
                msg = (
                    f"receipt JSON must be an object, got {type(receipt_data).__name__}"
                )
                evidence_reasons.append(msg)
                receipt_cross_check = msg
                # Skip further receipt checks; value is structurally wrong
            else:
                expected_rel = (
                    str(art.relative_to(worktree)).replace("\\", "/")
                    if artifact_path_validation.valid
                    else None
                )
                rc = _check_receipt(receipt_data, kind.value, expected_rel)
                receipt_cross_check = rc or "passed"
                if rc:
                    evidence_reasons.append(rc)
        except (json.JSONDecodeError, OSError, UnicodeError) as exc:
            msg = f"receipt read/parse error: {exc}"
            evidence_reasons.append(msg)
            receipt_cross_check = msg

    # -- Check: Artifact marker --------------------------------------------
    if artifact_path_validation.valid:
        try:
            art_text = art.read_text(encoding="utf-8")
            assessment = parse_artifact_verdict(art_text, kind)
            canonical_marker = assessment.canonical_marker
            if not assessment.artifact_valid:
                artifact_reasons.append(_artifact_reason(assessment))
        except (OSError, UnicodeError) as exc:
            evidence_reasons.append(f"artifact read/decode error: {exc}")

    # -- Check: Branch -----------------------------------------------------
    branch = _git_command(["branch", "--show-current"], worktree)
    observed_branch = branch
    if branch is None:
        evidence_reasons.append("could not determine current git branch")
    elif branch != expected_branch:
        evidence_reasons.append(
            f"expected branch {expected_branch!r}, observed {branch!r}"
        )

    # -- Check: HEAD / ancestry --------------------------------------------
    head = _git_command(["rev-parse", "HEAD"], worktree)
    observed_head = head
    if head is None:
        evidence_reasons.append("could not determine HEAD commit")
        ancestry_result = "failed_head"
    else:
        ancestor_check = _git_command(
            ["merge-base", "--is-ancestor", candidate_commit, "HEAD"],
            worktree,
        )
        if ancestor_check is not None:
            ancestry_result = "ancestor"
        else:
            try:
                check = subprocess.run(
                    ["git", "merge-base", "--is-ancestor", candidate_commit, "HEAD"],
                    cwd=str(worktree),
                    capture_output=True,
                    timeout=30,
                )
                if check.returncode == 1:
                    ancestry_result = f"{candidate_commit} is not an ancestor of HEAD"
                    evidence_reasons.append(ancestry_result)
                else:
                    ancestry_result = f"ancestry check failed (exit {check.returncode})"
                    evidence_reasons.append(ancestry_result)
            except (OSError, subprocess.TimeoutExpired) as exc:
                ancestry_result = f"ancestry check error: {exc}"
                evidence_reasons.append(ancestry_result)

    # -- Check: Pytest collection output ------------------------------------
    if pytest_collect_path_validation.valid:
        try:
            collect_text = collect.read_text(encoding="utf-8")
            authoritative_pytest_count = _parse_pytest_collect(collect_text)
            if authoritative_pytest_count is None:
                evidence_reasons.append(
                    "could not parse authoritative pytest collection count "
                    "(missing, zero, or ambiguous)"
                )
        except (OSError, UnicodeError) as exc:
            evidence_reasons.append(f"pytest collection file read/decode error: {exc}")

    # -- Worker reported count ------------------------------------------------
    if worker_reported_count is not None:
        if (
            authoritative_pytest_count is not None
            and worker_reported_count != authoritative_pytest_count
        ):
            worker_count_mismatch = True
            evidence_reasons.append(
                f"worker reported {worker_reported_count} passed but "
                f"collection shows {authoritative_pytest_count}"
            )

    # -- Final verdict --------------------------------------------------------
    artifact_valid = assessment.artifact_valid
    evidence_valid = len(evidence_reasons) == 0
    review_verdict = (
        assessment.review_verdict.value if assessment.review_verdict else None
    )
    integration_authorized = evidence_valid and assessment.integration_authorized
    operation_authorized = (
        integration_authorized
        if kind is ArtifactKind.DECISION
        else evidence_valid and artifact_valid
    )
    reasons = [*evidence_reasons, *artifact_reasons]

    return ReviewAcceptance(
        artifact_valid=artifact_valid,
        evidence_valid=evidence_valid,
        review_verdict=review_verdict,
        integration_authorized=integration_authorized,
        operation_authorized=operation_authorized,
        reasons=reasons,
        artifact=str(art),
        artifact_kind=kind.value,
        observed_branch=observed_branch,
        observed_head=observed_head,
        ancestry_result=ancestry_result,
        canonical_marker=canonical_marker,
        receipt_cross_check=receipt_cross_check,
        authoritative_pytest_count=authoritative_pytest_count,
        worker_reported_count=worker_reported_count,
        worker_count_mismatch=worker_count_mismatch,
        review_mode=review_mode,
        scratch_outputs_ignored=True,
        artifact_reason_code=assessment.reason_code,
        artifact_path_validation=artifact_path_validation,
        receipt_path_validation=receipt_path_validation,
        pytest_collect_path_validation=pytest_collect_path_validation,
    )
