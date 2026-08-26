"""Immutable-source combined-operation gatekeeper for operational G1A.

The module is executed from the clean Git worktree named by the typed transition
record.  The candidate repository is inspected only as data; none of its Python
controller or preflight code is imported or executed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from orchestration_harness import programme_admission as admission


PINNED_GATEKEEPER_DECISION_VERSION = "ariadne.pinned_programme_gatekeeper_decision.v1"


@dataclass(frozen=True)
class PinnedGatekeeperDecision:
    schema_version: str
    admitted: bool
    reason_codes: list[str]
    phase: str
    entrypoint: str
    gatekeeper_commit: str | None
    gatekeeper_tree: str | None
    gatekeeper_clean: bool
    target_branch: str | None
    target_head: str | None
    transition_id: str | None
    decisive_review_id: str | None
    decisive_review_verdict: str | None
    decisive_review_commit: str | None
    decisive_review_tree: str | None
    target_index_tree: str | None
    changed_paths_digest: str | None
    expected_origin_head: str | None
    target_cleanliness: dict[str, Any] | None
    operation_binding: dict[str, Any] | None
    scope_decision: dict[str, Any] | None


def _decision(
    *,
    reasons: list[str],
    phase: str,
    entrypoint: str,
    gatekeeper_commit: str | None,
    gatekeeper_tree: str | None,
    gatekeeper_clean: bool,
    target_branch: str | None,
    target_head: str | None,
    transition_id: str | None,
    decisive_review: dict[str, Any] | None,
    scope_decision: admission.ScopeDecision | None,
) -> PinnedGatekeeperDecision:
    unique_reasons = list(dict.fromkeys(reasons))
    return PinnedGatekeeperDecision(
        schema_version=PINNED_GATEKEEPER_DECISION_VERSION,
        admitted=not unique_reasons
        and bool(scope_decision and scope_decision.admitted),
        reason_codes=unique_reasons,
        phase=phase,
        entrypoint=entrypoint,
        gatekeeper_commit=gatekeeper_commit,
        gatekeeper_tree=gatekeeper_tree,
        gatekeeper_clean=gatekeeper_clean,
        target_branch=target_branch,
        target_head=target_head,
        transition_id=transition_id,
        decisive_review_id=(
            decisive_review.get("review_id") if decisive_review is not None else None
        ),
        decisive_review_verdict=(
            decisive_review.get("verdict") if decisive_review is not None else None
        ),
        decisive_review_commit=(
            decisive_review.get("reviewed_commit")
            if decisive_review is not None
            else None
        ),
        decisive_review_tree=(
            decisive_review.get("reviewed_tree")
            if decisive_review is not None
            else None
        ),
        target_index_tree=(scope_decision.index_tree if scope_decision else None),
        changed_paths_digest=(
            scope_decision.changed_paths_digest if scope_decision else None
        ),
        expected_origin_head=(
            scope_decision.expected_origin_head if scope_decision else None
        ),
        target_cleanliness=(
            scope_decision.target_cleanliness if scope_decision else None
        ),
        operation_binding=(
            scope_decision.operation_binding if scope_decision else None
        ),
        scope_decision=asdict(scope_decision) if scope_decision is not None else None,
    )


def evaluate_pinned_programme_operation(
    *,
    gatekeeper_root: Path,
    target_repo_root: Path,
    manifest: object | None,
    entrypoint: str,
    phase: str,
) -> PinnedGatekeeperDecision:
    """Evaluate one candidate commit/push from an exact clean trusted source."""
    source = gatekeeper_root.resolve()
    target = target_repo_root.resolve()
    reasons: list[str] = []
    gatekeeper_commit: str | None = None
    gatekeeper_tree: str | None = None
    target_branch: str | None = None
    target_head: str | None = None
    transition_id: str | None = None
    decisive_review: dict[str, Any] | None = None
    scope_decision: admission.ScopeDecision | None = None

    if source == target:
        reasons.append("gatekeeper_target_not_isolated")
    if entrypoint not in {"task_branch_commit", "task_branch_push"}:
        reasons.append("combined_operation_entrypoint_invalid")
    if phase not in {"development", "pre-push", "post-push"}:
        reasons.append("scope_phase_invalid")

    try:
        gatekeeper_commit = admission._run_git(source, "rev-parse", "HEAD")
        gatekeeper_tree = admission._run_git(source, "rev-parse", "HEAD^{tree}")
        source_status = admission._run_git(
            source, "status", "--porcelain", "--untracked-files=all"
        )
        gatekeeper_clean = not bool(source_status)
    except admission.ProgrammeAdmissionError:
        gatekeeper_clean = False
        reasons.append("gatekeeper_git_observation_failed")
    if not gatekeeper_clean:
        reasons.append("gatekeeper_worktree_not_clean")

    try:
        target_policy = admission.load_programme_policy(target)
        target_branch = admission._run_git(target, "branch", "--show-current")
        target_head = admission._run_git(target, "rev-parse", "HEAD")
    except admission.ProgrammeAdmissionError as error:
        return _decision(
            reasons=[*reasons, error.reason_code],
            phase=phase,
            entrypoint=entrypoint,
            gatekeeper_commit=gatekeeper_commit,
            gatekeeper_tree=gatekeeper_tree,
            gatekeeper_clean=gatekeeper_clean,
            target_branch=target_branch,
            target_head=target_head,
            transition_id=transition_id,
            decisive_review=decisive_review,
            scope_decision=None,
        )

    target_worktree_policy = target_policy.overlay["target_worktree_policy"]
    normalized_legacy = (
        str(target_worktree_policy["preserved_legacy_worktree"])
        .replace("\\", "/")
        .rstrip("/")
        .casefold()
    )
    if str(source).replace("\\", "/").rstrip("/").casefold() == normalized_legacy:
        reasons.append("gatekeeper_preserved_legacy_worktree_forbidden")
    if str(target).replace("\\", "/").rstrip("/").casefold() == normalized_legacy:
        reasons.append("gatekeeper_target_preserved_legacy_worktree_forbidden")

    acceptance = target_policy.state["g0_acceptance"]
    decisive_id = acceptance.get("decisive_review_id")
    history = acceptance.get("external_review_history")
    if isinstance(decisive_id, str) and isinstance(history, list):
        decisive_review = next(
            (
                row
                for row in history
                if isinstance(row, dict) and row.get("review_id") == decisive_id
            ),
            None,
        )
    if decisive_review is None:
        reasons.append("gatekeeper_decisive_review_missing")
    elif (
        decisive_review.get("verdict") != "PASS"
        or decisive_review.get("blocking_finding_count") != 0
        or decisive_review.get("g1a_authorized") is not True
    ):
        reasons.append("gatekeeper_decisive_review_not_pass")

    transition = target_policy.state.get("gate_transition")
    if not isinstance(transition, dict):
        reasons.append("gatekeeper_transition_record_missing")
    else:
        transition_id = transition.get("transition_id")
        if gatekeeper_commit != transition.get(
            "reviewed_commit"
        ) or gatekeeper_tree != transition.get("reviewed_tree"):
            reasons.append("gatekeeper_source_not_transition_pinned")
        if decisive_review is not None and (
            transition.get("transition_id") != decisive_review.get("review_id")
            or gatekeeper_commit != decisive_review.get("reviewed_commit")
            or gatekeeper_tree != decisive_review.get("reviewed_tree")
        ):
            reasons.append("gatekeeper_source_not_decisive_review_pinned")
        if target_policy.state.get("active_profile") != admission.G1A_ACTIVE_PROFILE:
            reasons.append("gatekeeper_target_profile_not_g1a")

    artifact: dict[str, Any] | None = None
    if isinstance(transition_id, str):
        artifact_path = (
            target / admission.TRANSITION_ARTIFACT_ROOT / f"{transition_id}.json"
        )
        try:
            artifact = admission.strict_json_object(artifact_path)
        except admission.ProgrammeAdmissionError as error:
            reasons.append(error.reason_code)
        if artifact is not None:
            expected_artifact_fields = {
                "schema_version",
                "transition_id",
                "recorded_at",
                "transition_manifest",
                "transition_manifest_sha256",
                "reviewed_commit",
                "reviewed_tree",
                "external_review_record_sha256",
                "state_digest_before",
                "state_digest_after",
                "policy_digest_before",
                "policy_digest_after",
                "changed_semantic_pointers",
                "scope_result",
                "target_cleanliness_contract",
            }
            if set(artifact) != expected_artifact_fields:
                reasons.append("gatekeeper_transition_artifact_schema_invalid")
            elif (
                artifact["schema_version"] != "raisa-ariadne.g0-to-g1a-transition.v1"
                or artifact["transition_id"] != transition_id
                or artifact["reviewed_commit"] != gatekeeper_commit
                or artifact["reviewed_tree"] != gatekeeper_tree
                or artifact["state_digest_after"] != target_policy.state_digest
                or artifact["policy_digest_after"] != target_policy.policy_digest
            ):
                reasons.append("gatekeeper_target_not_transition_version")

    if isinstance(manifest, dict) and artifact is not None:
        if manifest.get("schema_version") == admission.TRANSITION_MANIFEST_VERSION:
            if artifact.get("transition_manifest") != manifest:
                reasons.append("gatekeeper_transition_manifest_not_bound")
        elif manifest.get("state_digest") != artifact.get(
            "state_digest_after"
        ) or manifest.get("policy_digest") != artifact.get("policy_digest_after"):
            reasons.append("gatekeeper_task_manifest_not_transition_bound")

    if not reasons:
        scope_decision = admission._evaluate_programme_operation_admission_core(
            repo_root=target,
            manifest=manifest,
            entrypoint=entrypoint,
            phase=phase,
        )
        reasons.extend(scope_decision.reason_codes)
        if scope_decision.admitted and entrypoint == "task_branch_commit":
            if phase != "development":
                reasons.append("gatekeeper_commit_phase_invalid")
            if admission.git_change_inventory(target):
                reasons.append("gatekeeper_commit_unstaged_changes_present")
            try:
                untracked = admission.git_untracked_inventory(target)
            except admission.ProgrammeAdmissionError as error:
                reasons.append(error.reason_code)
                untracked = []
            if untracked:
                reasons.append("gatekeeper_commit_untracked_files_present")
            try:
                head_tree = admission._run_git(target, "rev-parse", "HEAD^{tree}")
            except admission.ProgrammeAdmissionError:
                head_tree = None
                reasons.append("gatekeeper_commit_head_tree_observation_failed")
            if scope_decision.index_tree == head_tree:
                reasons.append("gatekeeper_commit_index_unchanged")
        if scope_decision.admitted and entrypoint == "task_branch_push":
            if phase not in {"pre-push", "post-push"}:
                reasons.append("gatekeeper_push_phase_invalid")
            binding = scope_decision.operation_binding or {}
            try:
                committed_tree = admission._run_git(target, "rev-parse", "HEAD^{tree}")
            except admission.ProgrammeAdmissionError:
                committed_tree = None
                reasons.append("gatekeeper_push_head_tree_observation_failed")
            if (
                binding.get("target_head") != target_head
                or binding.get("index_tree") != committed_tree
                or binding.get("expected_origin_head") is None
                or binding.get("force_with_lease") is None
                or binding.get("exact_push_refspec") is None
            ):
                reasons.append("gatekeeper_push_binding_invalid")

    return _decision(
        reasons=reasons,
        phase=phase,
        entrypoint=entrypoint,
        gatekeeper_commit=gatekeeper_commit,
        gatekeeper_tree=gatekeeper_tree,
        gatekeeper_clean=gatekeeper_clean,
        target_branch=target_branch,
        target_head=target_head,
        transition_id=transition_id,
        decisive_review=decisive_review,
        scope_decision=scope_decision,
    )


def revalidate_pinned_operation_binding(
    *,
    prior_decision: PinnedGatekeeperDecision,
    gatekeeper_root: Path,
    target_repo_root: Path,
    manifest: object | None,
) -> PinnedGatekeeperDecision:
    """Fail closed when HEAD, index, change inventory, or origin moved after admission."""
    fresh = evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target_repo_root,
        manifest=manifest,
        entrypoint=prior_decision.entrypoint,
        phase=prior_decision.phase,
    )
    if not prior_decision.admitted:
        return replace(
            fresh,
            admitted=False,
            reason_codes=list(
                dict.fromkeys(
                    [*fresh.reason_codes, "gatekeeper_prior_decision_not_admitted"]
                )
            ),
        )
    if fresh.operation_binding != prior_decision.operation_binding:
        return replace(
            fresh,
            admitted=False,
            reason_codes=list(
                dict.fromkeys(
                    [*fresh.reason_codes, "gatekeeper_operation_binding_drift"]
                )
            ),
        )
    return fresh


def exact_push_argv(decision: PinnedGatekeeperDecision) -> list[str]:
    """Return the only push argv admitted by a current pre-push decision."""
    binding = decision.operation_binding or {}
    if (
        not decision.admitted
        or decision.entrypoint != "task_branch_push"
        or decision.phase != "pre-push"
        or not isinstance(binding.get("force_with_lease"), str)
        or not isinstance(binding.get("exact_push_refspec"), str)
    ):
        raise admission.ProgrammeAdmissionError("gatekeeper_exact_push_not_admitted")
    return [
        "git",
        "push",
        f"--force-with-lease={binding['force_with_lease']}",
        "origin",
        binding["exact_push_refspec"],
    ]


def commit_exact_admitted_index(
    *,
    prior_decision: PinnedGatekeeperDecision,
    gatekeeper_root: Path,
    target_repo_root: Path,
    manifest: object | None,
    message: str,
) -> str:
    """Commit the exact admitted index tree and CAS-update only its task branch."""
    if not isinstance(message, str) or not message.strip() or len(message) > 500:
        raise admission.ProgrammeAdmissionError("gatekeeper_commit_message_invalid")
    fresh = revalidate_pinned_operation_binding(
        prior_decision=prior_decision,
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target_repo_root,
        manifest=manifest,
    )
    binding = fresh.operation_binding or {}
    if (
        not fresh.admitted
        or fresh.entrypoint != "task_branch_commit"
        or fresh.phase != "development"
        or not isinstance(binding.get("target_head"), str)
        or not isinstance(binding.get("index_tree"), str)
        or not isinstance(binding.get("branch_ref"), str)
    ):
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_exact_index_commit_not_admitted"
        )
    target = target_repo_root.resolve()
    candidate = admission._run_git(
        target,
        "commit-tree",
        binding["index_tree"],
        "-p",
        binding["target_head"],
        "-m",
        message.strip(),
    )
    final = revalidate_pinned_operation_binding(
        prior_decision=fresh,
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target,
        manifest=manifest,
    )
    if not final.admitted:
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_operation_binding_drift_before_commit"
        )
    admission._run_git(
        target,
        "update-ref",
        binding["branch_ref"],
        candidate,
        binding["target_head"],
    )
    if (
        admission._run_git(target, "rev-parse", "HEAD") != candidate
        or admission._run_git(target, "rev-parse", "HEAD^{tree}")
        != binding["index_tree"]
    ):
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_exact_index_commit_postcondition_failed"
        )
    return candidate
