"""Immutable-source combined-operation gatekeeper for operational G1A.

The module is executed from the clean Git worktree named by the typed transition
record.  The candidate repository is inspected only as data; none of its Python
controller or preflight code is imported or executed.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestration_harness import programme_admission as admission


PINNED_GATEKEEPER_DECISION_VERSION = "ariadne.pinned_programme_gatekeeper_decision.v1"
PINNED_OPERATION_RECEIPT_VERSION = "ariadne.pinned_programme_operation_receipt.v1"
PINNED_RECEIPT_SINK_VERSION = "ariadne.pinned_receipt_sink.v1"
G0_CORRECTION_STATE_KEY = "g0_8_correction"
G0_REVIEWED_TREE_FIELD = "reviewed_g0_7_tree"
PINNED_SOURCE_PATHS = (
    "orchestration_harness/__init__.py",
    "orchestration_harness/models.py",
    "orchestration_harness/allocation.py",
    "orchestration_harness/allocator.py",
    "orchestration_harness/trusted_git.py",
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/settings_fingerprint.py",
    "orchestration_harness/active_operation.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
    "scripts/raisa_ariadne_pinned_gatekeeper.py",
)


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
    remote_identity: dict[str, Any] | None
    source_trusted_git_identity: dict[str, Any] | None
    receipt_sink_binding: dict[str, Any] | None
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
    source_trusted_git_identity: dict[str, Any] | None = None,
    receipt_sink_binding: dict[str, Any] | None = None,
) -> PinnedGatekeeperDecision:
    unique_reasons = list(dict.fromkeys(reasons))
    operation_binding = (
        dict(scope_decision.operation_binding or {}) if scope_decision else None
    )
    if operation_binding is not None and source_trusted_git_identity is not None:
        operation_binding["source_trusted_git_identity_sha256"] = (
            source_trusted_git_identity["trusted_git_identity_sha256"]
        )
    if operation_binding is not None and receipt_sink_binding is not None:
        operation_binding["receipt_sink"] = receipt_sink_binding
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
        remote_identity=(scope_decision.remote_identity if scope_decision else None),
        source_trusted_git_identity=source_trusted_git_identity,
        receipt_sink_binding=receipt_sink_binding,
        operation_binding=operation_binding,
        scope_decision=asdict(scope_decision) if scope_decision is not None else None,
    )


def evaluate_pinned_programme_operation(
    *,
    gatekeeper_root: Path,
    target_repo_root: Path,
    manifest: object | None,
    entrypoint: str,
    phase: str,
    receipt_sink_binding: dict[str, Any] | None = None,
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
    source_trusted_git_identity: dict[str, Any] | None = None

    if source == target:
        reasons.append("gatekeeper_target_not_isolated")
    if entrypoint not in {"task_branch_commit", "task_branch_push"}:
        reasons.append("combined_operation_entrypoint_invalid")
    if phase not in {"development", "pre-push", "post-push"}:
        reasons.append("scope_phase_invalid")

    try:
        gatekeeper_commit = admission._run_git(source, "rev-parse", "HEAD")
        gatekeeper_tree = admission._run_git(source, "rev-parse", "HEAD^{tree}")
        source_trusted_git_identity = admission.trusted_git.attest_repository(
            source,
            attested_paths=PINNED_SOURCE_PATHS,
            expected_commit=gatekeeper_commit,
        )
        source_status = admission._run_git(
            source, "status", "--porcelain", "--untracked-files=no"
        )
        source_inventory = admission.git_all_file_inventory(source)
        gatekeeper_clean = not bool(source_status) and not source_inventory
    except (
        admission.ProgrammeAdmissionError,
        admission.trusted_git.TrustedGitError,
    ) as error:
        gatekeeper_clean = False
        reasons.append(
            error.reason_code
            if hasattr(error, "reason_code")
            else "gatekeeper_git_observation_failed"
        )
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
            source_trusted_git_identity=source_trusted_git_identity,
            receipt_sink_binding=receipt_sink_binding,
        )

    target_worktree_policy = target_policy.overlay["target_worktree_policy"]
    g0_recovery_push = (
        target_policy.state.get("active_correction")
        == admission.ADMITTED_PROGRAMME_GATE
        and target_policy.state.get("active_profile") == admission.G0_CONTROLLER_PROFILE
    )
    g1a2_active = (
        target_policy.state.get("active_correction")
        == admission.SUBGATE_TRANSITION_TO_GATE
        and target_policy.state.get("active_profile") == admission.G1A2_ACTIVE_PROFILE
    )
    g1a3_active = (
        target_policy.state.get("active_correction")
        == admission.G1A3_TRANSITION_TO_GATE
        and target_policy.state.get("active_profile") == admission.G1A3_ACTIVE_PROFILE
    )
    normalized_legacy = (
        str(target_worktree_policy["preserved_legacy_worktree"])
        .replace("\\", "/")
        .rstrip("/")
        .casefold()
    )
    if str(source).replace("\\", "/").rstrip("/").casefold() == normalized_legacy:
        reasons.append("gatekeeper_preserved_legacy_worktree_forbidden")
    if (
        not g0_recovery_push
        and str(target).replace("\\", "/").rstrip("/").casefold() == normalized_legacy
    ):
        reasons.append("gatekeeper_target_preserved_legacy_worktree_forbidden")

    if g1a3_active:
        acceptance = target_policy.state["g1a_subgate_authority"]
        decisive_id = acceptance.get("decisive_g1a3_transition_enablement_review_id")
        history = acceptance.get("g1a3_transition_enablement_review_history")
    elif g1a2_active:
        acceptance = target_policy.state["g1a_subgate_authority"]
        decisive_id = acceptance.get("decisive_transition_enablement_review_id")
        history = acceptance.get("external_review_history")
    else:
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
    if g0_recovery_push:
        correction = target_policy.state[G0_CORRECTION_STATE_KEY]
        if entrypoint != "task_branch_push" or phase not in {"pre-push", "post-push"}:
            reasons.append("gatekeeper_g0_correction_push_only")
        if decisive_review is None:
            reasons.append("gatekeeper_decisive_review_missing")
        elif (
            decisive_review.get("verdict") != "REVISION_REQUIRED"
            or decisive_review.get("blocking_finding_count")
            != correction["review_finding_count"]
            or decisive_review.get("g1a_authorized") is not False
            or decisive_review.get("reviewed_commit")
            != correction["authorized_parent_commit"]
            or decisive_review.get("reviewed_tree")
            != correction[G0_REVIEWED_TREE_FIELD]
        ):
            reasons.append("gatekeeper_g0_correction_review_binding_invalid")
        try:
            target_tree = admission._run_git(target, "rev-parse", "HEAD^{tree}")
            parent_row = admission._run_git(
                target, "rev-list", "--parents", "-n", "1", "HEAD"
            ).split()
        except admission.ProgrammeAdmissionError:
            target_tree = None
            parent_row = []
            reasons.append("gatekeeper_g0_candidate_binding_observation_failed")
        if (
            gatekeeper_commit != target_head
            or gatekeeper_tree != target_tree
            or len(parent_row) != 2
            or parent_row[1] != correction["authorized_parent_commit"]
            or correction["status"] != "review_pending"
            or correction["external_review_status"] != "pending"
            or correction["g1a_authorized"] is not False
            or target_policy.state.get("gate_transition") is not None
        ):
            reasons.append("gatekeeper_source_not_g0_candidate_pinned")
    elif g1a3_active:
        if decisive_review is None:
            reasons.append("gatekeeper_g1a3_decisive_review_missing")
        elif (
            decisive_review.get("verdict") != "PASS"
            or decisive_review.get("blocking_finding_count") != 0
            or decisive_review.get("g1a3_state_transition_authorized") is not True
            or decisive_review.get("g1a3_implementation_authorized") is not False
            or decisive_review.get("provider_invocation_authorized") is not False
            or decisive_review.get("integration_authorized") is not False
        ):
            reasons.append("gatekeeper_g1a3_decisive_review_not_pass")
        authority = target_policy.state["g1a_subgate_authority"]
        implementation = authority["implementation_review_history"][0]
        if (
            implementation.get("verdict") != "PASS"
            or implementation.get("blocking_finding_count") != 0
            or implementation.get("reviewed_commit")
            != "37e2d6f51ebbdb281771f922a5f460fd23e2571b"
            or implementation.get("reviewed_tree")
            != "798a2eda11438fe05da2528298006775774ccfc4"
            or implementation.get("g1a3_transition_enablement_authorized") is not True
            or implementation.get("provider_invocation_authorized") is not False
            or implementation.get("integration_authorized") is not False
        ):
            reasons.append("gatekeeper_g1a2_implementation_review_invalid")
        g1a3 = authority["subgates"]["G1A.3"]
        transition = g1a3.get("state_transition")
        if not isinstance(transition, dict):
            reasons.append("gatekeeper_g1a3_transition_record_missing")
        else:
            transition_id = transition.get("transition_id")
            if gatekeeper_commit != transition.get(
                "enablement_controller_commit"
            ) or gatekeeper_tree != transition.get("enablement_controller_tree"):
                reasons.append("gatekeeper_source_not_g1a3_transition_pinned")
            if decisive_review is not None and (
                transition.get("external_review_id") != decisive_review.get("review_id")
                or gatekeeper_commit != decisive_review.get("reviewed_commit")
                or gatekeeper_tree != decisive_review.get("reviewed_tree")
            ):
                reasons.append("gatekeeper_source_not_g1a3_review_pinned")
            if (
                g1a3.get("state_transition_status") != "complete"
                or g1a3.get("implementation_authorized") is not True
                or g1a3.get("implementation_started") is not False
                or g1a3.get("integration_execution_authorized") is not False
                or g1a3.get("provider_invocation_authorized") is not False
            ):
                reasons.append("gatekeeper_target_g1a3_state_invalid")
    elif g1a2_active:
        if decisive_review is None:
            reasons.append("gatekeeper_subgate_decisive_review_missing")
        elif (
            decisive_review.get("verdict") != "PASS"
            or decisive_review.get("blocking_finding_count") != 0
            or decisive_review.get("g1a2_state_transition_authorized") is not True
            or decisive_review.get("g1a2_implementation_authorized") is not False
            or decisive_review.get("provider_invocation_authorized") is not False
        ):
            reasons.append("gatekeeper_subgate_decisive_review_not_pass")

        g1a2 = target_policy.state["g1a_subgate_authority"]["subgates"]["G1A.2"]
        transition = g1a2.get("state_transition")
        if not isinstance(transition, dict):
            reasons.append("gatekeeper_subgate_transition_record_missing")
        else:
            transition_id = transition.get("transition_id")
            if gatekeeper_commit != transition.get(
                "enablement_controller_commit"
            ) or gatekeeper_tree != transition.get("enablement_controller_tree"):
                reasons.append("gatekeeper_source_not_subgate_transition_pinned")
            if decisive_review is not None and (
                transition_id != decisive_review.get("review_id")
                or gatekeeper_commit != decisive_review.get("reviewed_commit")
                or gatekeeper_tree != decisive_review.get("reviewed_tree")
            ):
                reasons.append("gatekeeper_source_not_subgate_review_pinned")
            if (
                g1a2.get("state_transition_status") != "complete"
                or g1a2.get("implementation_authorized") is not True
                or g1a2.get("implementation_started") is not False
                or g1a2.get("provider_invocation_authorized") is not False
            ):
                reasons.append("gatekeeper_target_subgate_state_invalid")
    else:
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
            if (
                target_policy.state.get("active_profile")
                != admission.G1A_ACTIVE_PROFILE
            ):
                reasons.append("gatekeeper_target_profile_not_g1a")

    artifact: dict[str, Any] | None = None
    if not g0_recovery_push and isinstance(transition_id, str):
        artifact_root = (
            admission.SUBGATE_TRANSITION_ARTIFACT_ROOT
            if g1a2_active or g1a3_active
            else admission.TRANSITION_ARTIFACT_ROOT
        )
        artifact_path = target / artifact_root / f"{transition_id}.json"
        try:
            artifact = admission.strict_json_object(artifact_path)
        except admission.ProgrammeAdmissionError as error:
            reasons.append(error.reason_code)
        if artifact is not None:
            expected_artifact_fields = (
                {
                    "schema_version",
                    "transition_id",
                    "recorded_at",
                    "transition_manifest",
                    "transition_manifest_sha256",
                    "g1a2_implementation_review_record_sha256",
                    "external_review_record_sha256",
                    "enablement_controller_commit",
                    "enablement_controller_tree",
                    "state_digest_before",
                    "state_digest_after",
                    "policy_digest_before",
                    "policy_digest_after",
                    "changed_semantic_pointers",
                    "scope_result",
                    "g1a3_profile_contract",
                }
                if g1a3_active
                else {
                    "schema_version",
                    "transition_id",
                    "recorded_at",
                    "transition_manifest",
                    "transition_manifest_sha256",
                    "owner_disposition_record_sha256",
                    "external_review_record_sha256",
                    "enablement_controller_commit",
                    "enablement_controller_tree",
                    "state_digest_before",
                    "state_digest_after",
                    "policy_digest_before",
                    "policy_digest_after",
                    "changed_semantic_pointers",
                    "scope_result",
                    "g1a2_profile_contract",
                }
                if g1a2_active
                else {
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
            )
            if set(artifact) != expected_artifact_fields:
                reasons.append("gatekeeper_transition_artifact_schema_invalid")
            elif g1a3_active and (
                artifact["schema_version"] != "ariadne.g1a2-to-g1a3-transition.v1"
                or artifact["transition_id"] != transition_id
                or artifact["enablement_controller_commit"] != gatekeeper_commit
                or artifact["enablement_controller_tree"] != gatekeeper_tree
                or artifact["state_digest_after"] != target_policy.state_digest
                or artifact["policy_digest_after"] != target_policy.policy_digest
            ):
                reasons.append("gatekeeper_target_not_g1a3_transition_version")
            elif g1a2_active and (
                artifact["schema_version"] != "ariadne.g1a1-to-g1a2-transition.v1"
                or artifact["transition_id"] != transition_id
                or artifact["enablement_controller_commit"] != gatekeeper_commit
                or artifact["enablement_controller_tree"] != gatekeeper_tree
                or artifact["state_digest_after"] != target_policy.state_digest
                or artifact["policy_digest_after"] != target_policy.policy_digest
            ):
                reasons.append("gatekeeper_target_not_subgate_transition_version")
            elif (
                not g1a2_active
                and not g1a3_active
                and (
                    artifact["schema_version"]
                    != "raisa-ariadne.g0-to-g1a-transition.v1"
                    or artifact["transition_id"] != transition_id
                    or artifact["reviewed_commit"] != gatekeeper_commit
                    or artifact["reviewed_tree"] != gatekeeper_tree
                    or artifact["state_digest_after"] != target_policy.state_digest
                    or artifact["policy_digest_after"] != target_policy.policy_digest
                )
            ):
                reasons.append("gatekeeper_target_not_transition_version")

    if isinstance(manifest, dict) and artifact is not None:
        if manifest.get("schema_version") in {
            admission.TRANSITION_MANIFEST_VERSION,
            admission.SUBGATE_TRANSITION_MANIFEST_VERSION,
            admission.G1A3_TRANSITION_MANIFEST_VERSION,
        }:
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
                or binding.get("remote_identity_sha256") is None
                or binding.get("git_administrative_identity_sha256") is None
                or binding.get("trusted_git_identity_sha256") is None
                or source_trusted_git_identity is None
                or binding.get("explicit_destination") is None
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
        source_trusted_git_identity=source_trusted_git_identity,
        receipt_sink_binding=receipt_sink_binding,
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
        receipt_sink_binding=prior_decision.receipt_sink_binding,
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
        or not isinstance(binding.get("explicit_destination"), str)
    ):
        raise admission.ProgrammeAdmissionError("gatekeeper_exact_push_not_admitted")
    return [
        "git",
        "push",
        "--no-verify",
        f"--force-with-lease={binding['force_with_lease']}",
        binding["explicit_destination"],
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


def _operation_receipt(
    *,
    operation: str,
    decision: PinnedGatekeeperDecision,
    result_sha: str,
    result_tree: str,
    reservation: "OperationReceiptReservation",
    final_revalidation: dict[str, Any],
    post_push_decision: PinnedGatekeeperDecision | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": PINNED_OPERATION_RECEIPT_VERSION,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "status": "completed",
        "gatekeeper_commit": decision.gatekeeper_commit,
        "gatekeeper_tree": decision.gatekeeper_tree,
        "target_branch": decision.target_branch,
        "admitted_operation_binding": decision.operation_binding,
        "remote_identity": decision.remote_identity,
        "result_sha": result_sha,
        "result_tree": result_tree,
        "post_push_readback_sha": (
            post_push_decision.expected_origin_head if post_push_decision else None
        ),
        "post_push_decision_admitted": (
            post_push_decision.admitted if post_push_decision else None
        ),
        "receipt_sink": reservation.binding,
        "receipt_path": reservation.path.as_posix(),
        "final_revalidation": final_revalidation,
    }
    payload["operation_receipt_sha256"] = admission._sha256_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return payload


def _canonical_digest(value: object) -> str:
    return admission._sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _path_within(candidate: Path, root: Path) -> bool:
    try:
        return candidate.resolve(strict=True).is_relative_to(root.resolve(strict=True))
    except (OSError, ValueError):
        return False


def _same_file_identity(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(left.get(key) == right.get(key) for key in ("device", "inode", "mode"))


@dataclass
class OperationReceiptReservation:
    """Exclusive, identity-stable reservation for one internally named receipt."""

    path: Path
    descriptor: int
    directory_identity: dict[str, Any]
    file_identity: dict[str, Any]
    binding: dict[str, Any]
    finalized: bool = False

    def _assert_identity(self) -> None:
        try:
            current_directory = admission.trusted_git._path_identity(  # noqa: SLF001
                self.path.parent, directory=True
            )
            current_file = os.fstat(self.descriptor)
            path_file = self.path.lstat()
        except OSError as error:
            raise admission.ProgrammeAdmissionError(
                "gatekeeper_receipt_identity_drift"
            ) from error
        current_file_identity = {
            "device": int(current_file.st_dev),
            "inode": int(current_file.st_ino),
            "mode": int(current_file.st_mode),
        }
        path_file_identity = {
            "device": int(path_file.st_dev),
            "inode": int(path_file.st_ino),
            "mode": int(path_file.st_mode),
        }
        if (
            not _same_file_identity(self.directory_identity, current_directory)
            or not _same_file_identity(self.file_identity, current_file_identity)
            or not _same_file_identity(self.file_identity, path_file_identity)
        ):
            raise admission.ProgrammeAdmissionError("gatekeeper_receipt_identity_drift")

    def finalize(self, payload: dict[str, Any]) -> None:
        if self.finalized or self.descriptor < 0:
            raise admission.ProgrammeAdmissionError(
                "gatekeeper_receipt_already_finalized"
            )
        self._assert_identity()
        encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        try:
            offset = 0
            while offset < len(encoded):
                written = os.write(self.descriptor, encoded[offset:])
                if written <= 0:
                    raise OSError("short receipt write")
                offset += written
            os.fsync(self.descriptor)
            self._assert_identity()
            os.close(self.descriptor)
            self.descriptor = -1
            self.finalized = True
            try:
                directory_handle = os.open(
                    self.path.parent,
                    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
                )
            except OSError:
                directory_handle = -1
            if directory_handle >= 0:
                try:
                    os.fsync(directory_handle)
                finally:
                    os.close(directory_handle)
            if self.path.read_bytes() != encoded:
                raise OSError("receipt readback mismatch")
        except OSError as error:
            if self.descriptor >= 0:
                os.close(self.descriptor)
                self.descriptor = -1
            raise admission.ProgrammeAdmissionError(
                "gatekeeper_receipt_write_failed"
            ) from error

    def close_unfinalized(self) -> None:
        """Close an unsuccessful reservation while preserving the collision marker."""
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1


def reserve_operation_receipt(
    *,
    receipt_directory: Path,
    operation: str,
    decision: PinnedGatekeeperDecision,
    gatekeeper_root: Path,
    target_repo_root: Path,
) -> OperationReceiptReservation:
    """Reserve one internally named receipt outside every governed repository."""
    try:
        directory_identity = admission.trusted_git._path_identity(  # noqa: SLF001
            receipt_directory.absolute(), directory=True
        )
        directory = Path(directory_identity["resolved_path"])
    except (OSError, admission.trusted_git.TrustedGitError) as error:
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_receipt_directory_invalid"
        ) from error
    target = target_repo_root.resolve(strict=True)
    source = gatekeeper_root.resolve(strict=True)
    target_identity = (decision.target_cleanliness or {}).get("trusted_git_identity")
    source_identity = decision.source_trusted_git_identity
    if not isinstance(target_identity, dict) or not isinstance(source_identity, dict):
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_receipt_repository_identity_missing"
        )
    forbidden_roots = [source, target]
    for identity in (source_identity, target_identity):
        for key in ("gitdir", "commondir"):
            value = identity.get(key, {}).get("resolved_path")
            if isinstance(value, str):
                forbidden_roots.append(Path(value))
    policy = admission.load_programme_policy(target)
    snapshot = policy.state["clockwork_snapshot"]
    for key in ("git_bundle", "pre_g0_untracked_archive"):
        preservation = Path(snapshot[key]["path"]).resolve(strict=True)
        forbidden_roots.extend((preservation, preservation.parent))
    if any(_path_within(directory, root) for root in forbidden_roots):
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_receipt_directory_forbidden"
        )
    stable_directory_identity = {
        key: directory_identity[key]
        for key in ("resolved_path", "device", "inode", "mode")
    }
    operation_basis = {
        "schema_version": PINNED_RECEIPT_SINK_VERSION,
        "operation": operation,
        "gatekeeper_commit": decision.gatekeeper_commit,
        "target_head": decision.target_head,
        "target_index_tree": decision.target_index_tree,
        "operation_binding": decision.operation_binding,
        "directory_identity": stable_directory_identity,
    }
    operation_identifier = _canonical_digest(operation_basis).removeprefix("sha256:")
    filename = f"ariadne-{operation}-{operation_identifier}.json"
    destination = directory / filename
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(destination, flags, 0o600)
        observed = os.fstat(descriptor)
    except FileExistsError as error:
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_receipt_collision"
        ) from error
    except OSError as error:
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_receipt_reservation_failed"
        ) from error
    file_identity = {
        "device": int(observed.st_dev),
        "inode": int(observed.st_ino),
        "mode": int(observed.st_mode),
    }
    binding = {
        "schema_version": PINNED_RECEIPT_SINK_VERSION,
        "directory": directory.as_posix(),
        "directory_identity_sha256": _canonical_digest(stable_directory_identity),
        "operation_identifier": operation_identifier,
        "filename": filename,
        "reservation_file_identity": file_identity,
    }
    return OperationReceiptReservation(
        path=destination,
        descriptor=descriptor,
        directory_identity=directory_identity,
        file_identity=file_identity,
        binding=binding,
    )


def _identity_without_head(identity: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in identity.items()
        if key not in {"head", "head_tree", "trusted_git_identity_sha256"}
    }


def _final_operation_revalidation(
    *,
    decision: PinnedGatekeeperDecision,
    gatekeeper_root: Path,
    target_repo_root: Path,
    result_sha: str,
    result_tree: str,
    expected_remote_sha: str | None,
) -> dict[str, Any]:
    source = gatekeeper_root.resolve()
    target = target_repo_root.resolve()
    try:
        source_identity = admission.trusted_git.attest_repository(
            source,
            attested_paths=PINNED_SOURCE_PATHS,
            expected_commit=decision.gatekeeper_commit,
        )
    except admission.trusted_git.TrustedGitError as error:
        raise admission.ProgrammeAdmissionError(error.reason_code) from error
    if source_identity != decision.source_trusted_git_identity:
        raise admission.ProgrammeAdmissionError("gatekeeper_source_identity_drift")
    policy = admission.load_programme_policy(target)
    prior_target_identity = (decision.target_cleanliness or {}).get(
        "trusted_git_identity"
    )
    if not isinstance(prior_target_identity, dict) or _identity_without_head(
        policy.trusted_git_identity
    ) != _identity_without_head(prior_target_identity):
        raise admission.ProgrammeAdmissionError("gatekeeper_target_identity_drift")
    if (
        admission._run_git(target, "rev-parse", "HEAD") != result_sha
        or admission._run_git(target, "rev-parse", "HEAD^{tree}") != result_tree
        or admission._run_git(target, "write-tree") != result_tree
    ):
        raise admission.ProgrammeAdmissionError("gatekeeper_result_binding_drift")
    remote_identity = admission.observe_remote_identity(
        target, policy.overlay["remote_identity_policy"]
    )
    if remote_identity != decision.remote_identity:
        raise admission.ProgrammeAdmissionError("gatekeeper_remote_identity_drift")
    branch = decision.target_branch
    remote_head = (
        admission._fresh_remote_head(
            target, remote_identity["normalized_push_url"], branch
        )
        if isinstance(branch, str)
        else None
    )
    if remote_head != expected_remote_sha:
        raise admission.ProgrammeAdmissionError("gatekeeper_remote_readback_drift")
    expected_protected = policy.state["protected_refs"]["expected_sha"]
    protected_refs = {
        ref: admission._run_git(target, "rev-parse", ref)
        for ref in policy.state["protected_refs"]["refs"]
    }
    if any(value != expected_protected for value in protected_refs.values()):
        raise admission.ProgrammeAdmissionError("gatekeeper_protected_ref_drift")
    payload = {
        "schema_version": "ariadne.pinned_operation_final_revalidation.v1",
        "source_trusted_git_identity_sha256": source_identity[
            "trusted_git_identity_sha256"
        ],
        "target_trusted_git_identity_sha256": policy.trusted_git_identity[
            "trusted_git_identity_sha256"
        ],
        "result_sha": result_sha,
        "result_tree": result_tree,
        "remote_readback_sha": remote_head,
        "protected_refs": protected_refs,
        "status": "passed",
    }
    payload["final_revalidation_sha256"] = _canonical_digest(payload)
    return payload


def execute_exact_index_commit(
    *,
    gatekeeper_root: Path,
    target_repo_root: Path,
    manifest: object | None,
    message: str,
    receipt_directory: Path,
) -> dict[str, Any]:
    """Reserve, commit the exact index tree, revalidate, and finalize evidence."""
    base_decision = evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target_repo_root,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    if not base_decision.admitted:
        raise admission.ProgrammeAdmissionError(
            "gatekeeper_exact_index_commit_not_admitted"
        )
    reservation = reserve_operation_receipt(
        receipt_directory=receipt_directory,
        operation="exact_index_commit",
        decision=base_decision,
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target_repo_root,
    )
    try:
        decision = evaluate_pinned_programme_operation(
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target_repo_root,
            manifest=manifest,
            entrypoint="task_branch_commit",
            phase="development",
            receipt_sink_binding=reservation.binding,
        )
        if not decision.admitted:
            raise admission.ProgrammeAdmissionError(
                "gatekeeper_exact_index_commit_not_admitted"
            )
        candidate = commit_exact_admitted_index(
            prior_decision=decision,
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target_repo_root,
            manifest=manifest,
            message=message,
        )
        tree = admission._run_git(
            target_repo_root.resolve(), "rev-parse", "HEAD^{tree}"
        )
        final_revalidation = _final_operation_revalidation(
            decision=decision,
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target_repo_root,
            result_sha=candidate,
            result_tree=tree,
            expected_remote_sha=decision.expected_origin_head,
        )
        payload = _operation_receipt(
            operation="exact_index_commit",
            decision=decision,
            result_sha=candidate,
            result_tree=tree,
            reservation=reservation,
            final_revalidation=final_revalidation,
        )
        reservation.finalize(payload)
        return payload
    except Exception:
        reservation.close_unfinalized()
        raise


def execute_exact_sha_push(
    *,
    gatekeeper_root: Path,
    target_repo_root: Path,
    manifest: object | None,
    receipt_directory: Path,
) -> dict[str, Any]:
    """Reserve, push one exact SHA, revalidate, and finalize evidence."""
    base_decision = evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target_repo_root,
        manifest=manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    if not base_decision.admitted:
        raise admission.ProgrammeAdmissionError("gatekeeper_exact_push_not_admitted")
    reservation = reserve_operation_receipt(
        receipt_directory=receipt_directory,
        operation="exact_sha_push",
        decision=base_decision,
        gatekeeper_root=gatekeeper_root,
        target_repo_root=target_repo_root,
    )
    try:
        decision = evaluate_pinned_programme_operation(
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target_repo_root,
            manifest=manifest,
            entrypoint="task_branch_push",
            phase="pre-push",
            receipt_sink_binding=reservation.binding,
        )
        fresh = revalidate_pinned_operation_binding(
            prior_decision=decision,
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target_repo_root,
            manifest=manifest,
        )
        argv = exact_push_argv(fresh)
        target = target_repo_root.resolve()
        admission._run_git(target, *argv[1:])
        post_push = evaluate_pinned_programme_operation(
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target,
            manifest=manifest,
            entrypoint="task_branch_push",
            phase="post-push",
            receipt_sink_binding=reservation.binding,
        )
        if (
            not post_push.admitted
            or post_push.expected_origin_head != fresh.target_head
        ):
            raise admission.ProgrammeAdmissionError(
                "gatekeeper_exact_push_postcondition_failed"
            )
        result_sha = fresh.target_head or ""
        result_tree = admission._run_git(target, "rev-parse", "HEAD^{tree}")
        final_revalidation = _final_operation_revalidation(
            decision=fresh,
            gatekeeper_root=gatekeeper_root,
            target_repo_root=target,
            result_sha=result_sha,
            result_tree=result_tree,
            expected_remote_sha=result_sha,
        )
        payload = _operation_receipt(
            operation="exact_sha_push",
            decision=fresh,
            result_sha=result_sha,
            result_tree=result_tree,
            reservation=reservation,
            final_revalidation=final_revalidation,
            post_push_decision=post_push,
        )
        reservation.finalize(payload)
        return payload
    except Exception:
        reservation.close_unfinalized()
        raise
