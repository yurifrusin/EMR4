"""One externally authenticated maintenance generation; target code is data.

Only the isolated bootstrap calls run_request. Its accepted capsule and request
pins are owned by the external invocation, not by a target or activation file.
Private shared cores supply effect/receipt ordering, not admission authority.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import fields, replace
from pathlib import Path

from orchestration_harness import pinned_programme_gatekeeper as pg
from orchestration_harness import programme_admission as policy_functions
from orchestration_harness import trusted_git as git
from orchestration_harness.controller_maintenance_candidate import (
    compare_maintenance_candidate,
)
from orchestration_harness.controller_maintenance_activation import (
    _parse_maintenance_activation_core,
)
from orchestration_harness.controller_maintenance_request import (
    canonical_bytes,
    parse_request,
)
from orchestration_harness.controller_maintenance_journal import (
    JOURNAL_FILES,
    bind_journal_base,
    validate_journal_manifest,
)


class MaintenanceOperationError(ValueError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


def _fail(reason):
    raise MaintenanceOperationError(reason)


def _digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _overlap(left, right):
    return left == right or left.is_relative_to(right) or right.is_relative_to(left)


def _git(root, *args):
    """Fixed Git transport. No hooks, target executable, lazy fetch or prompt."""
    environment = git.closed_git_environment()
    environment.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(  # noqa: S603
            [
                str(git.resolve_stock_git()),
                "--no-lazy-fetch",
                "--literal-pathspecs",
                *git.TRUSTED_GIT_COMMAND_OVERRIDES,
                "-c",
                "core.hooksPath=" + os.devnull,
                "-c",
                "gc.auto=0",
                "-c",
                "maintenance.auto=false",
                "-c",
                "push.followTags=false",
                "-c",
                "push.recurseSubmodules=no",
                "-c",
                "push.gpgSign=false",
                "-c",
                "commit.gpgSign=false",
                *args,
            ],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise MaintenanceOperationError(
            "maintenance_git_operation_uncertain"
        ) from error
    if result.returncode:
        _fail("maintenance_git_operation_failed")
    return result.stdout.decode("utf-8", errors="strict").strip()


class _Execution:
    def __init__(self, request, source, source_file, request_file):
        self.request = request
        self.record = request.manifest
        self.source = source
        self.source_file = source_file
        self.request_file = request_file
        self.target = request.target_root
        self.source_root = source_file.path.parent
        self.committed = None
        self.initial_observation = None
        self.preserved_observation = None
        self.remote_identity = None
        self.root_identities = None
        self.source_identity = {
            "format": "complete_verified_code_capsule",
            "archive_sha256": source.archive_sha256,
            "source_commit": source.source_commit,
            "source_tree": source.source_tree,
        }
        self.source_identity["trusted_git_identity_sha256"] = _digest(
            self.source_identity
        )

    def _inputs(self):
        self.source_file.revalidate()
        self.request_file.revalidate()
        request, record = self.request, self.record
        if (
            self.source.source_commit != record.source_commit
            or self.source.source_tree != record.source_tree
            or self.source.generation_id != record.generation_id
        ):
            _fail("maintenance_source_identity_mismatch")
        if any(
            row.path in {path for path, _digest in JOURNAL_FILES}
            for row in (*record.changed_files, *record.frozen_files)
        ):
            _fail("maintenance_journal_paths_forbidden")
        roots = (
            self.target,
            request.scratch_parent,
            request.receipt_directory,
            self.source_root,
            self.request_file.path.parent,
            request.original_controller.root,
        )
        identities = tuple(
            git._stable_path_identity(root, directory=True) for root in roots
        )
        if self.root_identities is None:
            self.root_identities = identities
        elif self.root_identities != identities:
            _fail("maintenance_root_identity_drift")
        for external in roots[1:]:
            if external == self.target or external.is_relative_to(self.target):
                _fail("maintenance_external_root_inside_target")
        if self.target.is_relative_to(request.original_controller.root):
            _fail("maintenance_target_inside_original_controller")
        original = request.original_controller
        admin = git._physical_git_administration(self.target)
        governed = (self.target, admin["gitdir"], admin["commondir"], original.root)
        for external in (
            request.scratch_parent,
            request.receipt_directory,
            self.source_root,
            self.request_file.path.parent,
        ):
            if any(_overlap(external, root) for root in governed):
                _fail("maintenance_external_root_overlaps_governed_root")
        for preservation in (
            *request.preservation_paths,
            *(Path(row.path) for row in request.preserved_files),
        ):
            if any(
                _overlap(preservation, root) for root in (*governed, self.source_root)
            ):
                _fail("maintenance_preservation_overlaps_governed_root")
        if (
            _git(original.root, "rev-parse", "HEAD") != original.commit
            or _git(original.root, "rev-parse", "HEAD^{tree}") != original.tree
        ):
            _fail("maintenance_original_controller_changed")
        preserved = []
        for root, row in (
            *((original.root, row) for row in original.files),
            *((Path(), row) for row in request.preserved_files),
        ):
            identity, raw = git._read_regular_snapshot(
                root / row.path, maximum_bytes=2 * 1024 * 1024
            )
            if hashlib.sha256(raw).hexdigest() != row.sha256:
                _fail("maintenance_preserved_file_changed")
            preserved.append(identity)
        if self.preserved_observation is None:
            self.preserved_observation = preserved
        elif preserved != self.preserved_observation:
            _fail("maintenance_preservation_identity_drift")

    def _remote(self, expected):
        request = self.request
        remote = policy_functions.observe_remote_identity(
            self.target, dict(request.remote_policy)
        )
        if self.remote_identity is None:
            self.remote_identity = remote
        elif remote != self.remote_identity:
            _fail("maintenance_remote_identity_drift")
        protected = dict(request.protected_refs)
        if any(
            _git(self.target, "rev-parse", ref) != value
            for ref, value in protected.items()
        ):
            _fail("maintenance_protected_ref_drift")
        expected_remote = {
            "refs/heads/master": protected["refs/heads/master"],
            "refs/heads/handoff/current": protected["refs/heads/handoff/current"],
            self.record.destination_ref: expected,
        }
        output = _git(
            self.target,
            "ls-remote",
            "--refs",
            remote["normalized_push_url"],
            *expected_remote,
        )
        observed = {}
        for line in output.splitlines():
            parts = line.split("\t")
            if len(parts) != 2 or parts[1] in observed:
                _fail("maintenance_remote_readback_invalid")
            observed[parts[1]] = parts[0]
        if observed != expected_remote:
            _fail("maintenance_remote_lease_mismatch")
        return remote

    def observe(self, expected_head, expected_remote):
        self._inputs()
        paths = tuple(
            row.path for row in (*self.record.changed_files, *self.record.frozen_files)
        )
        observation = git.attest_target_index(
            self.target,
            attested_paths=paths,
            expected_head=expected_head,
            expected_index_tree=self.record.candidate_tree,
            scratch_parent=self.request.scratch_parent,
        )
        gitdir = Path(observation["repository"]["gitdir"]["resolved_path"])
        _head_identity, head_bytes = git._read_regular_snapshot(
            gitdir / "HEAD", maximum_bytes=128
        )
        if head_bytes != (expected_head + "\n").encode("ascii"):
            _fail("maintenance_detached_head_required")
        for external in (
            self.source_root,
            self.request_file.path.parent,
            self.request.scratch_parent,
            self.request.receipt_directory,
        ):
            for key in ("gitdir", "commondir"):
                root = Path(observation["repository"][key]["resolved_path"])
                if external == root or external.is_relative_to(root):
                    _fail("maintenance_external_root_inside_git")
        if self.initial_observation is None:
            for path, _digest in JOURNAL_FILES:
                if _git(
                    self.target,
                    "ls-tree",
                    "--format=%(objecttype)",
                    self.record.base_commit,
                    "--",
                    path,
                ):
                    _fail("maintenance_journal_base_path_present")
            comparison = compare_maintenance_candidate(
                self.target,
                self.request.manifest_payload,
                expected_manifest_sha256=self.request.manifest_sha256,
                scratch_parent=self.request.scratch_parent,
            )
            if comparison["observation_sha256"] != observation["observation_sha256"]:
                _fail("maintenance_initial_observation_drift")
            self.initial_observation = observation
        else:
            invariant = {
                key: value
                for key, value in observation.items()
                if key not in {"head", "observation_sha256"}
            }
            prior = {
                key: value
                for key, value in self.initial_observation.items()
                if key not in {"head", "observation_sha256"}
            }
            if invariant != prior:
                _fail("maintenance_target_observation_drift")
        if expected_head != self.record.base_commit:
            if _git(
                self.target, "rev-list", "--parents", "-n", "1", expected_head
            ).split() != [expected_head, self.record.base_commit]:
                _fail("maintenance_commit_parent_mismatch")
            if (
                _git(self.target, "rev-parse", expected_head + "^{tree}")
                != self.record.candidate_tree
            ):
                _fail("maintenance_commit_tree_mismatch")
        self._remote(expected_remote)
        self._inputs()
        return observation

    def evaluate(self, **kwargs):
        entrypoint, phase = kwargs["entrypoint"], kwargs["phase"]
        receipt = kwargs.get("receipt_sink_binding")
        committing = entrypoint == "task_branch_commit" and phase == "development"
        if not committing and not (
            entrypoint == "task_branch_push" and phase in {"pre-push", "post-push"}
        ):
            _fail("maintenance_phase_invalid")
        head = self.record.base_commit if committing else self.committed
        if head is None:
            _fail("maintenance_commit_receipt_required")
        remote_head = head if phase == "post-push" else self.record.base_commit
        observed = self.observe(head, remote_head)
        binding = {
            "generation_id": self.record.generation_id,
            "request_sha256": hashlib.sha256(self.request_file.data).hexdigest(),
            "accepted_manifest_sha256": self.request.manifest_sha256,
            "source_archive_sha256": self.source.archive_sha256,
            "review_record_sha256": self.record.review_record_sha256,
            "target_head": head,
            "index_tree": self.record.candidate_tree,
            "observation_sha256": observed["observation_sha256"],
            "branch_ref": "HEAD",
            "expected_origin_head": remote_head,
            "explicit_destination": self.remote_identity["normalized_push_url"],
            "force_with_lease": self.record.destination_ref
            + ":"
            + self.record.base_commit,
            "exact_push_refspec": head + ":" + self.record.destination_ref,
            "receipt_sink": receipt,
            "complete_physical_worktree_attested": False,
        }
        values = {field.name: None for field in fields(pg.PinnedGatekeeperDecision)}
        values.update(
            schema_version="ariadne.maintenance_operation_decision.v1",
            admitted=True,
            reason_codes=[],
            phase=phase,
            entrypoint=entrypoint,
            gatekeeper_commit=self.source.source_commit,
            gatekeeper_tree=self.source.source_tree,
            gatekeeper_clean=True,
            target_branch=self.record.destination_ref,
            target_head=head,
            target_index_tree=self.record.candidate_tree,
            transition_id=self.record.generation_id,
            decisive_review_id=self.request.review_id,
            decisive_review_verdict="PASS",
            expected_origin_head=remote_head,
            target_cleanliness={
                "trusted_git_identity": observed["repository"],
                "complete_physical_worktree_attested": False,
            },
            source_trusted_git_identity=self.source_identity,
            operation_binding=binding,
            receipt_sink_binding=receipt,
            remote_identity=self.remote_identity,
        )
        return pg.PinnedGatekeeperDecision(**values)

    def revalidate(self, **kwargs):
        prior = kwargs["prior_decision"]
        fresh = self.evaluate(
            entrypoint=prior.entrypoint,
            phase=prior.phase,
            receipt_sink_binding=prior.receipt_sink_binding,
        )
        if not prior.admitted or fresh.operation_binding != prior.operation_binding:
            return replace(
                fresh,
                admitted=False,
                reason_codes=["maintenance_operation_binding_drift"],
            )
        return fresh

    def reserve(self, **kwargs):
        self._inputs()
        if kwargs["receipt_directory"] != self.request.receipt_directory:
            _fail("maintenance_receipt_directory_mismatch")
        return pg._reserve_operation_receipt_core(
            **kwargs,
            preservation_paths=lambda _target: (
                *self.request.preservation_paths,
                self.request.original_controller.root / "preservation-boundary",
                *(Path(row.path) for row in self.request.preserved_files),
            ),
        )

    def commit(self, **kwargs):
        result = pg._commit_exact_admitted_index_core(
            prior_decision=kwargs["prior_decision"],
            target_repo_root=self.target,
            message=kwargs["message"],
            revalidate=lambda prior, _target: self.revalidate(prior_decision=prior),
            run_git=_git,
        )
        self.committed = result
        return result

    def final(self, **kwargs):
        observed = self.observe(kwargs["result_sha"], kwargs["expected_remote_sha"])
        if kwargs["result_tree"] != self.record.candidate_tree:
            _fail("maintenance_final_tree_mismatch")
        return {
            "status": "passed",
            "schema_version": "ariadne.maintenance_final_revalidation.v1",
            "source_archive_sha256": self.source.archive_sha256,
            "target_observation_sha256": observed["observation_sha256"],
            "result_sha": kwargs["result_sha"],
            "result_tree": kwargs["result_tree"],
            "remote_readback_sha": kwargs["expected_remote_sha"],
            "complete_physical_worktree_attested": False,
        }

    def execute(self):
        services = pg._OperationServices(
            evaluate=self.evaluate,
            reserve=self.reserve,
            revalidate=self.revalidate,
            commit=self.commit,
            final_revalidation=self.final,
            run_git=_git,
        )
        common = dict(
            gatekeeper_root=self.source_root,
            target_repo_root=self.target,
            manifest=self.request.manifest_payload,
            receipt_directory=self.request.receipt_directory,
            services=services,
        )
        decision = self.evaluate(entrypoint="task_branch_commit", phase="development")
        activation_sink = self.reserve(
            receipt_directory=self.request.receipt_directory,
            operation="controller_activation",
            decision=decision,
            gatekeeper_root=self.source_root,
            target_repo_root=self.target,
        )
        try:
            committed = pg._execute_exact_index_commit_core(
                **common,
                message="Activate reviewed G1B.2 controller maintenance "
                + self.record.generation_id,
            )
            pushed = pg._execute_exact_sha_push_core(**common)
            self.observe(self.committed, self.committed)
            receipt_identity, receipt_bytes = git._read_regular_snapshot(
                Path(pushed["receipt_path"]),
                maximum_bytes=2 * 1024 * 1024,
            )
            if (
                receipt_bytes
                != (json.dumps(pushed, indent=2, sort_keys=True) + "\n").encode("utf-8")
                or any(
                    receipt_identity[key]
                    != pushed["receipt_sink"]["reservation_file_identity"][key]
                    for key in ("device", "inode", "mode")
                )
                or committed["result_sha"] != pushed["result_sha"]
                or pushed["result_tree"] != self.record.candidate_tree
                or pushed["post_push_readback_sha"] != self.committed
                or pushed["post_push_decision_admitted"] is not True
            ):
                _fail("maintenance_publication_receipt_mismatch")
            activation = {
                "schema_version": "ariadne.g1b2_controller_activation.v1",
                "status": "activated",
                "generation_id": self.record.generation_id,
                "accepted_manifest_sha256": self.request.manifest_sha256,
                "original_controller_commit": self.request.original_controller.commit,
                "original_controller_tree": self.request.original_controller.tree,
                "governing_transition_commit": self.record.base_commit,
                "maintenance_commit": self.committed,
                "maintenance_tree": self.record.candidate_tree,
                "maintenance_parent": self.record.base_commit,
                "source_commit": self.source.source_commit,
                "source_tree": self.source.source_tree,
                "journal_base_commit": self.committed,
                "publication_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
                "review_record_sha256": self.record.review_record_sha256,
                "review_subject_sha256": self.record.review_subject_sha256,
            }
            raw = canonical_bytes(activation)
            _parse_maintenance_activation_core(
                raw,
                expected_sha256=hashlib.sha256(raw).hexdigest(),
                manifest_payload=self.request.manifest_payload,
                original_commit=self.request.original_controller.commit,
                original_tree=self.request.original_controller.tree,
                governing_commit=self.record.base_commit,
                governing_tree=self.record.base_tree,
            )
            activation_sink.finalize(activation)
            activation_identity, activation_bytes = git._read_regular_snapshot(
                activation_sink.path,
                maximum_bytes=65536,
            )
            if activation_bytes != (
                json.dumps(activation, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8") or any(
                activation_identity[key] != activation_sink.file_identity[key]
                for key in ("device", "inode", "mode")
            ):
                _fail("maintenance_activation_readback_mismatch")
            journal_binding = bind_journal_base(
                activation_bytes,
                expected_activation_sha256=hashlib.sha256(activation_bytes).hexdigest(),
                manifest_payload=self.request.manifest_payload,
                original_commit=self.request.original_controller.commit,
                original_tree=self.request.original_controller.tree,
                governing_commit=self.record.base_commit,
                governing_tree=self.record.base_tree,
            )
            journal_manifest = validate_journal_manifest(
                {
                    "schema_version": "ariadne.maintenance_journal_scope.v1",
                    "phase": "development",
                    "base_commit": self.committed,
                    "candidate_head": self.committed,
                    "candidate_tree": self.record.candidate_tree,
                    "paths": [path for path, _digest in JOURNAL_FILES],
                },
                binding=journal_binding,
            )
            return {
                "status": "activated",
                "commit_receipt": committed,
                "publication_receipt": pushed,
                "activation": activation,
                "activation_path": activation_sink.path.as_posix(),
                "activation_file_sha256": hashlib.sha256(activation_bytes).hexdigest(),
                "journal_manifest_base": journal_manifest["base_commit"],
                "journal_scope_paths": list(journal_manifest["paths"]),
                "journal_implementation_accepted": False,
                "complete_physical_worktree_attested": False,
            }
        except Exception:
            activation_sink.close_unfinalized()
            raise


def run_request(payload, *, verified_source, source_file, request_file):
    """Called only with the isolated bootstrap's authenticated memory objects."""
    if payload != request_file.data:
        _fail("maintenance_request_snapshot_mismatch")
    request = parse_request(payload)
    execution = _Execution(request, verified_source, source_file, request_file)
    if request.operation == "evaluate":
        decision = execution.evaluate(
            entrypoint="task_branch_commit", phase="development"
        )
        return {
            "status": "evaluated",
            "binding": decision.operation_binding,
            "complete_physical_worktree_attested": False,
        }
    return execution.execute()
