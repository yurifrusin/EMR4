"""Read-only comparison of an inert maintenance record and candidate bytes.

The expected digest is supplied by the caller and proves integrity only. This
module does not establish source/review acceptance, issue an admission token,
select executable code, contact a remote, or mutate the target repository.
"""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path

from orchestration_harness import trusted_git as git
from orchestration_harness.controller_maintenance_record import (
    parse_maintenance_record,
)


class MaintenanceCandidateError(ValueError):
    """The stated candidate does not match the observed bounded facts."""

    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


def _command(root: Path, *args: str) -> bytes:
    environment = git.closed_git_environment()
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    try:
        result = subprocess.run(  # noqa: S603
            [
                str(git.resolve_stock_git()),
                "--no-lazy-fetch",
                "--literal-pathspecs",
                *git.TRUSTED_GIT_COMMAND_OVERRIDES,
                *args,
            ],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise MaintenanceCandidateError("maintenance_git_comparison_failed") from error
    if result.returncode:
        raise MaintenanceCandidateError("maintenance_git_comparison_failed")
    return result.stdout


def _oid(payload: bytes) -> str:
    if (
        len(payload) != 41
        or payload[-1:] != b"\n"
        or any(byte not in b"0123456789abcdef" for byte in payload[:-1])
    ):
        raise MaintenanceCandidateError("maintenance_object_identity_invalid")
    return payload[:-1].decode("ascii")


def _reconstructed_trees(
    index: bytes,
    changes: tuple[tuple[str, str | None, str], ...],
    scratch: Path,
    *,
    scratch_identity: dict,
    excluded_roots: tuple[Path, ...],
) -> tuple[str, str]:
    """Return candidate with declared modes, then base with changes reversed."""

    def check_parent() -> None:
        if git._stable_path_identity(scratch, directory=True) != scratch_identity:
            raise MaintenanceCandidateError("maintenance_scratch_drift")
        if any(
            scratch == root or scratch.is_relative_to(root) for root in excluded_roots
        ):
            raise MaintenanceCandidateError("maintenance_scratch_not_isolated")

    check_parent()
    with tempfile.TemporaryDirectory(prefix="ariadne-delta-", dir=scratch) as name:
        owned = Path(name)
        owned_identity = git._stable_path_identity(owned, directory=True)

        def check_child() -> None:
            check_parent()
            if git._stable_path_identity(owned, directory=True) != owned_identity:
                raise MaintenanceCandidateError("maintenance_scratch_drift")
            if owned.parent != scratch or any(
                owned == root or owned.is_relative_to(root) for root in excluded_roots
            ):
                raise MaintenanceCandidateError("maintenance_scratch_not_isolated")

        def command(*args: str) -> bytes:
            check_child()
            return _command(owned, *args)

        command("init", "--quiet", "--template=", "--object-format=sha1", ".")
        check_child()
        (owned / ".git" / "index").write_bytes(index)
        for path, _before, after in changes:
            command("update-index", "--cacheinfo", "100644", after, path)
        candidate = _oid(command("write-tree", "--missing-ok"))
        for path, before, _after in changes:
            if before is None:
                command("update-index", "--force-remove", "--", path)
            else:
                command("update-index", "--cacheinfo", "100644", before, path)
        base = _oid(command("write-tree", "--missing-ok"))
        check_child()
    return candidate, base


def compare_maintenance_candidate(
    root: Path,
    payload: bytes,
    *,
    expected_manifest_sha256: str,
    scratch_parent: Path,
) -> dict:
    """Compare one pre-publication candidate; return evidence without authority.

    Whole staged-tree equality is proved by reversing the exact declared edits
    in an owned opaque index snapshot. Unselected physical files are not read.
    An externally accepted caller must separately bind all supplied identities.
    """
    return _compare_candidate_core(
        root,
        payload,
        expected_manifest_sha256=expected_manifest_sha256,
        scratch_parent=scratch_parent,
        expected_current_head=None,
    )


def _compare_candidate_core(
    root: Path,
    payload: bytes,
    *,
    expected_manifest_sha256: str,
    scratch_parent: Path,
    expected_current_head: str | None,
) -> dict:
    """Shared delta proof. A trusted caller binds committed-phase HEAD."""
    record = parse_maintenance_record(payload, expected_sha256=expected_manifest_sha256)
    paths = tuple(row.path for row in (*record.changed_files, *record.frozen_files))
    scratch_identity = git._stable_path_identity(scratch_parent, directory=True)
    scratch = Path(scratch_identity["resolved_path"])

    def observe() -> dict:
        return git.attest_target_index(
            root,
            attested_paths=paths,
            expected_head=record.base_commit
            if expected_current_head is None
            else expected_current_head,
            expected_index_tree=record.candidate_tree,
            scratch_parent=scratch,
        )

    before = observe()
    worktree = Path(before["repository"]["worktree"]["resolved_path"])
    if (
        _oid(_command(worktree, "rev-parse", f"{record.base_commit}^{{tree}}"))
        != record.base_tree
    ):
        raise MaintenanceCandidateError("maintenance_base_tree_mismatch")
    physical = {row["path"]: row for row in before["physical_paths"]}
    reversals = []
    for row in (*record.changed_files, *record.frozen_files):
        if physical[row.path]["physical"]["sha256"] != "sha256:" + row.after_sha256:
            raise MaintenanceCandidateError("maintenance_after_bytes_mismatch")
        old_oid = None
        if row.before_sha256 is not None:
            old = _command(
                worktree, "cat-file", "blob", f"{record.base_commit}:{row.path}"
            )
            if hashlib.sha256(old).hexdigest() != row.before_sha256:
                raise MaintenanceCandidateError("maintenance_before_bytes_mismatch")
            old_oid = git._git_blob_object_id(old, "sha1")
        # Include frozen entries to check their declared ordinary-file mode.
        reversals.append((row.path, old_oid, physical[row.path]["object_id"]))
    index_path = Path(before["index"]["resolved_path"])
    identity, snapshot = git._read_regular_snapshot(
        index_path, maximum_bytes=128 * 1024 * 1024
    )
    if identity != before["index"]:
        raise MaintenanceCandidateError("maintenance_index_drift")
    _metadata, uncached = git._index_metadata(snapshot, "sha1")
    candidate_tree, base_tree = _reconstructed_trees(
        uncached,
        tuple(reversals),
        scratch,
        scratch_identity=scratch_identity,
        excluded_roots=tuple(
            Path(before["repository"][name]["resolved_path"])
            for name in ("worktree", "gitdir", "commondir")
        ),
    )
    if candidate_tree != record.candidate_tree:
        raise MaintenanceCandidateError("maintenance_declared_mode_mismatch")
    if base_tree != record.base_tree:
        raise MaintenanceCandidateError("maintenance_undeclared_delta")
    if observe() != before:
        raise MaintenanceCandidateError("maintenance_candidate_drift")
    return {
        "schema_version": "ariadne.maintenance_candidate_comparison.v1",
        "manifest_sha256": expected_manifest_sha256,
        "generation_id": record.generation_id,
        "base_commit": record.base_commit,
        "base_tree": base_tree,
        "candidate_tree": candidate_tree,
        "observation_sha256": before["observation_sha256"],
        "changed_path_count": len(record.changed_files),
        "frozen_path_count": len(record.frozen_files),
        "operation_authority": False,
        "complete_physical_worktree_attested": False,
        "source_acceptance_verified": False,
        "review_acceptance_verified": False,
    }
