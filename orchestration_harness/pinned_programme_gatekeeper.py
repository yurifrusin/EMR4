"""Immutable-source combined-operation gatekeeper for operational G1A.

The module is executed from the clean Git worktree named by the typed transition
record.  The candidate repository is inspected only as data; none of its Python
controller or preflight code is imported or executed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
            scope_decision=None,
        )

    transition = target_policy.state.get("gate_transition")
    if not isinstance(transition, dict):
        reasons.append("gatekeeper_transition_record_missing")
    else:
        transition_id = transition.get("transition_id")
        if gatekeeper_commit != transition.get(
            "reviewed_commit"
        ) or gatekeeper_tree != transition.get("reviewed_tree"):
            reasons.append("gatekeeper_source_not_transition_pinned")
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
        scope_decision=scope_decision,
    )
