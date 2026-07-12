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
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

ArtifactKind = Literal["decision", "completion"]
ReviewMode = Literal["executable", "static_evidence"]

_VALID_REVIEW_MODES = frozenset({"executable", "static_evidence"})


@dataclass(frozen=True)
class ReviewAcceptance:
    """Deterministic, JSON-serialisable result of the acceptance gate."""

    accepted: bool
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

    def to_json(self) -> str:
        """Serialise to JSON with schema_version and status fields."""
        data = asdict(self)
        data["schema_version"] = "ariadne.review_acceptance.v1"
        data["status"] = "accepted" if self.accepted else "rejected"
        return json.dumps(data, indent=2, default=str)


# ---------------------------------------------------------------------------
# Receipt field contract
# ---------------------------------------------------------------------------

_REQUIRED_RECEIPT_FIELDS: dict[str, object] = {
    "status": "completed",
    "artifact": ...,            # dynamic key — must be present (value checked later)
    "artifact_kind": ...,       # dynamic key — must be present and match
    "artifact_observed": True,
    "permission_prompt_observed": False,
    "process_cleanup_confirmed": True,
}


def _check_receipt(
    receipt: dict, expected_kind: str, expected_artifact_rel: str
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
            return (
                f"receipt.{key} expected {expected_val!r}, "
                f"got {actual!r}"
            )

    # Dynamic fields
    actual_artifact = receipt.get("artifact")
    if actual_artifact != expected_artifact_rel:
        return (
            f"receipt.artifact expected {expected_artifact_rel!r}, "
            f"got {actual_artifact!r}"
        )

    actual_kind = receipt.get("artifact_kind")
    if actual_kind != expected_kind:
        return (
            f"receipt.artifact_kind expected {expected_kind!r}, "
            f"got {actual_kind!r}"
        )

    return None


# ---------------------------------------------------------------------------
# Artifact marker parsing — matches runner.mjs::validArtifact()
# ---------------------------------------------------------------------------
#
# The reference JS implementation:
#   body.split(/\r?\n/).some((line) => {
#     const cells = line.includes("|") ? line.split("|") : [line];
#     return cells.some((cell) => {
#       const normalized = cell.trim().replace(/^[*`_]+|[*`_]+$/g, "").trim();
#       if (artifactKind === "completion") return /^STATUS:\s*complete$/i.test(normalized);
#       return /^DECISION:\s*(pass|revision_required)$/i.test(normalized);
#     });
#   });
#
# This Python implementation mirrors that exact logic: iterate each line,
# split on ``|`` when present, trim each cell, strip markdown formatting,
# then apply the exact case-insensitive decision/completion regex.


_DECISION_CELL_RE = re.compile(r"^decision:\s*(pass|revision_required)$", re.IGNORECASE)
_COMPLETION_CELL_RE = re.compile(r"^status:\s*complete$", re.IGNORECASE)
_VERDICT_CELL_RE = re.compile(r"^verdict\b", re.IGNORECASE)


def _normalise_marker_cell(cell: str) -> str:
    """Trim a cell and strip surrounding ``*``, ``_``, `` ` `` formatting.

    Returns the normalised cell content (lowered) for matching.
    """
    stripped = cell.strip()
    # Strip leading/trailing markdown formatting exactly as JS regex:
    #   /^[*`_]+|[*`_]+$/g
    while stripped and stripped[0] in ("*", "`", "_"):
        stripped = stripped[1:]
    while stripped and stripped[-1] in ("*", "`", "_"):
        stripped = stripped[:-1]
    return stripped.strip()


def _parse_artifact_marker(
    text: str, expected_kind: ArtifactKind
) -> tuple[str | None, str | None]:
    """Return ``(canonical_marker, reason)``.

    * ``canonical_marker`` is the canonicalised marker (e.g. ``DECISION: pass``)
      or ``None`` if no valid marker is found.
    * ``reason`` is ``None`` on success, or an error description on failure.
    """
    lines = text.splitlines()
    has_verdict = False
    for line in lines:
        cells = line.split("|") if "|" in line else [line]
        for cell in cells:
            normalised = _normalise_marker_cell(cell)
            if _VERDICT_CELL_RE.search(normalised):
                has_verdict = True
            if expected_kind == "decision":
                m = _DECISION_CELL_RE.match(normalised)
                if m:
                    value = m.group(1).lower()
                    return f"DECISION: {value}", None
            elif expected_kind == "completion":
                if _COMPLETION_CELL_RE.match(normalised):
                    return "STATUS: complete", None

    if expected_kind == "decision":
        if has_verdict:
            return None, "found VERDICT without DECISION; VERDICT alone is rejected"
        return None, "missing DECISION: pass|revision_required in artifact"
    elif expected_kind == "completion":
        return None, "missing STATUS: complete in artifact"
    else:
        return None, f"unknown artifact_kind: {expected_kind}"


# ---------------------------------------------------------------------------
# Pytest collection parsing
# ---------------------------------------------------------------------------

# Tight patterns:
#   "139 tests collected"
#   "1 test collected"
#   "review/test_diary_smoke.py: 139"            (pytest file output form)
#   "tests/test_foo.py: 47"                       (pytest file output form)
_COLLECT_PATTERNS = [
    re.compile(r"(\d+)\s+tests?\s+collected"),
    # Only match .py: N (pytest file output), not arbitrary colon-number patterns
    re.compile(r"^.*?\.py:\s*(\d+)\s*$", re.MULTILINE),
]


def _parse_pytest_collect(text: str) -> int | None:
    """Return the collected test count, or ``None`` if parsing fails.

    Accepts multiple matches as long as they agree (conflicting = ``None``).
    """
    counts: set[int] = set()
    for pat in _COLLECT_PATTERNS:
        for m in pat.finditer(text):
            try:
                counts.add(int(m.group(1)))
            except ValueError:
                continue

    if len(counts) == 0:
        return None
    if len(counts) > 1:
        return None  # conflicting counts
    (val,) = counts
    if val <= 0:
        return None
    return val


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
    except (OSError, subprocess.TimeoutExpired):
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


def _check_inside_worktree(resolved: Path, worktree: Path, label: str) -> str | None:
    """Return ``None`` if *resolved* is inside *worktree*, else a reason string."""
    try:
        is_inside = worktree in resolved.parents or worktree == resolved.parent
    except (OSError, RuntimeError):
        return f"{label} path resolution error: {resolved}"
    if not is_inside:
        return f"{label} is outside the review worktree: {resolved}"
    if not resolved.is_file():
        return f"{label} is not an ordinary file: {resolved}"
    return None


# ---------------------------------------------------------------------------
# Public validator
# ---------------------------------------------------------------------------


def accept_review_artifact(
    *,
    artifact_path: str | Path,
    artifact_kind: ArtifactKind,
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
        A frozen dataclass with ``accepted=True/False``, reasons, and all
        observed fields.
    """
    worktree = Path(review_worktree).resolve()

    # -- Runtime validation (before any I/O or git calls) ------------------
    if review_mode not in _VALID_REVIEW_MODES:
        raise ValueError(
            f"invalid review_mode: {review_mode!r}; "
            f"must be one of {sorted(_VALID_REVIEW_MODES)}"
        )

    # Resolve all paths relative to the declared worktree, not caller cwd
    art = _resolve_relative_to_worktree(artifact_path, worktree)
    receipt_file = _resolve_relative_to_worktree(receipt_path, worktree)
    collect = _resolve_relative_to_worktree(pytest_collect_path, worktree)

    reasons: list[str] = []
    observed_branch: str | None = None
    observed_head: str | None = None
    ancestry_result: str | None = None
    canonical_marker: str | None = None
    receipt_cross_check: str | None = None
    authoritative_pytest_count: int | None = None
    worker_count_mismatch = False

    # -- Check: Artifact, receipt, and collect are ordinary files inside worktree
    for label, p in [("artifact", art), ("receipt", receipt_file), ("pytest_collect", collect)]:
        err = _check_inside_worktree(p, worktree, label)
        if err:
            reasons.append(err)

    # -- Check: Never search other files for substitute --------------------
    # (Policy enforcement — if declared paths are outside/missing, we do not
    #  look elsewhere.)

    # -- Check: Receipt content --------------------------------------------
    if not reasons or all(
        "receipt" not in r for r in reasons
    ):
        try:
            receipt_data = json.loads(receipt_file.read_text(encoding="utf-8"))
            if not isinstance(receipt_data, dict):
                msg = (
                    f"receipt JSON must be an object, "
                    f"got {type(receipt_data).__name__}"
                )
                reasons.append(msg)
                receipt_cross_check = msg
                # Skip further receipt checks; value is structurally wrong
            else:
                expected_rel = str(
                    art.relative_to(worktree)
                ).replace("\\", "/")
                rc = _check_receipt(receipt_data, artifact_kind, expected_rel)
                receipt_cross_check = rc or "passed"
                if rc:
                    reasons.append(rc)
        except (json.JSONDecodeError, OSError) as exc:
            msg = f"receipt read/parse error: {exc}"
            reasons.append(msg)
            receipt_cross_check = msg

    # -- Check: Artifact marker --------------------------------------------
    try:
        art_text = art.read_text(encoding="utf-8")
        marker, marker_reason = _parse_artifact_marker(art_text, artifact_kind)
        canonical_marker = marker
        if marker_reason:
            reasons.append(marker_reason)
    except OSError as exc:
        reasons.append(f"artifact read error: {exc}")

    # -- Check: Branch -----------------------------------------------------
    branch = _git_command(["branch", "--show-current"], worktree)
    observed_branch = branch
    if branch is None:
        reasons.append("could not determine current git branch")
    elif branch != expected_branch:
        reasons.append(
            f"expected branch {expected_branch!r}, observed {branch!r}"
        )

    # -- Check: HEAD / ancestry --------------------------------------------
    head = _git_command(["rev-parse", "HEAD"], worktree)
    observed_head = head
    if head is None:
        reasons.append("could not determine HEAD commit")
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
                    reasons.append(ancestry_result)
                else:
                    ancestry_result = f"ancestry check failed (exit {check.returncode})"
                    reasons.append(ancestry_result)
            except (OSError, subprocess.TimeoutExpired) as exc:
                ancestry_result = f"ancestry check error: {exc}"
                reasons.append(ancestry_result)

    # -- Check: Pytest collection output ------------------------------------
    try:
        collect_text = collect.read_text(encoding="utf-8")
        authoritative_pytest_count = _parse_pytest_collect(collect_text)
        if authoritative_pytest_count is None:
            reasons.append(
                "could not parse authoritative pytest collection count "
                "(missing, zero, or ambiguous)"
            )
    except OSError as exc:
        reasons.append(f"pytest collection file read error: {exc}")

    # -- Worker reported count ------------------------------------------------
    if worker_reported_count is not None:
        if (
            authoritative_pytest_count is not None
            and worker_reported_count != authoritative_pytest_count
        ):
            worker_count_mismatch = True
            reasons.append(
                f"worker reported {worker_reported_count} passed but "
                f"collection shows {authoritative_pytest_count}"
            )

    # -- Final verdict --------------------------------------------------------
    accepted = len(reasons) == 0

    return ReviewAcceptance(
        accepted=accepted,
        reasons=reasons,
        artifact=str(art),
        artifact_kind=artifact_kind,
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
    )
