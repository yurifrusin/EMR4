"""Tiny authored fixture for the maintenance runner's local lifecycle tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from orchestration_harness.controller_maintenance_request import canonical_bytes
from orchestration_harness.programme_admission import (
    build_synthetic_remote_identity_policy,
)
from programme_maintenance_synthetic import (
    _git,
    create_synthetic_graph,
    create_synthetic_repository,
)
from maintenance_capsule_synthetic import archive_entries, capsule_entries


_CAPSULE_PATHS = (
    "orchestration_harness/__init__.py",
    "orchestration_harness/models.py",
    "orchestration_harness/allocation.py",
    "orchestration_harness/allocator.py",
    "orchestration_harness/trusted_git.py",
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "orchestration_harness/controller_maintenance_record.py",
    "orchestration_harness/controller_maintenance_candidate.py",
    "orchestration_harness/controller_maintenance_activation.py",
    "orchestration_harness/controller_maintenance_request.py",
    "orchestration_harness/controller_maintenance_runner.py",
    "orchestration_harness/controller_maintenance_journal.py",
)
_YAML_PATHS = (
    "__init__.py",
    "composer.py",
    "constructor.py",
    "dumper.py",
    "emitter.py",
    "error.py",
    "events.py",
    "loader.py",
    "nodes.py",
    "parser.py",
    "reader.py",
    "representer.py",
    "resolver.py",
    "scanner.py",
    "serializer.py",
    "tokens.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_fixture(
    tmp_path: Path, operation: str = "evaluate", *, base_extra_files=None
) -> SimpleNamespace:
    """Create only new authored repositories and capsule/request bytes."""
    graph = create_synthetic_graph(
        tmp_path / "target-graph",
        {"owned.py": b"one\n", "frozen.py": b"frozen\n", **(base_extra_files or {})},
        branch="codex/raisa-ariadne-recovery-g0",
    )
    target, origin = graph.target, graph.origin
    base = target.head()
    base_tree = target.index_tree()
    recovery_ref = target.branch_ref
    for ref in (recovery_ref, "refs/heads/master", "refs/heads/handoff/current"):
        _git(target.root, "push", origin.as_posix(), f"{base}:{ref}")
    for ref in (
        "refs/heads/master",
        "refs/heads/handoff/current",
        "refs/remotes/origin/master",
        "refs/remotes/origin/handoff/current",
        "refs/remotes/origin/codex/raisa-ariadne-recovery-g0",
    ):
        _git(target.root, "update-ref", ref, base)
    _git(target.root, "checkout", "--detach", base)
    target.stage_files({"owned.py": b"two\n"})
    candidate_tree = target.index_tree()

    controller = create_synthetic_repository(
        tmp_path / "controller", {"controller.py": b"# authored controller\n"}
    )
    preservation = tmp_path / "preservation"
    preservation.mkdir()
    marker = preservation / "journal-marker"
    marker.write_bytes(b"authored journal marker\n")
    capsule_source = tmp_path / "capsule-source"
    workspace = Path(__file__).resolve().parents[1]
    source_files = {path: (workspace / path).read_bytes() for path in _CAPSULE_PATHS}
    yaml_root = Path("C:/Users/sarashera/emr4/.venv/Lib/site-packages/yaml")
    source_files.update(
        {f"yaml/{path}": (yaml_root / path).read_bytes() for path in _YAML_PATHS}
    )
    entries = capsule_entries(capsule_source, source_files)
    source_zip = archive_entries(entries)
    capsule_path = tmp_path / "capsule" / "source.zip"
    capsule_path.parent.mkdir()
    capsule_path.write_bytes(source_zip)
    capsule = json.loads(entries["capsule.json"].decode("utf-8"))
    review = {
        "schema_version": "ariadne.maintenance_operational_review.v1",
        "review_id": "synthetic-maintenance-review-v1",
        "verdict": "PASS",
        "findings": [],
        "subject_sha256": "1" * 64,
    }
    manifest = {
        "schema_version": "ariadne.g1b2_controller_maintenance_manifest.v1",
        "generation_id": "synthetic-maintenance-v1",
        "base_commit": base,
        "base_tree": base_tree,
        "source_commit": capsule["source_commit"],
        "source_tree": capsule["source_tree"],
        "candidate_tree": candidate_tree,
        "destination_ref": recovery_ref,
        "review_record_sha256": _sha(canonical_bytes(review)),
        "review_subject_sha256": review["subject_sha256"],
        "changed_files": [
            {
                "path": "owned.py",
                "mode": "100644",
                "before_sha256": _sha(b"one\n"),
                "after_sha256": _sha(b"two\n"),
            }
        ],
        "frozen_files": [
            {
                "path": "frozen.py",
                "mode": "100644",
                "before_sha256": _sha(b"frozen\n"),
                "after_sha256": _sha(b"frozen\n"),
            }
        ],
    }
    request = {
        "schema_version": "ariadne.maintenance_operation_request.v1",
        "operation": operation,
        "target_root": target.root.as_posix(),
        "scratch_parent": (tmp_path / "scratch").as_posix(),
        "receipt_directory": (tmp_path / "receipts").as_posix(),
        "manifest": manifest,
        "manifest_sha256": _sha(canonical_bytes(manifest)),
        "review": review,
        "owner_approval_sha256": "2" * 64,
        "remote_policy": build_synthetic_remote_identity_policy(origin),
        "protected_refs": {
            ref: base
            for ref in (
                "refs/heads/master",
                "refs/heads/handoff/current",
                "refs/remotes/origin/master",
                "refs/remotes/origin/handoff/current",
            )
        },
        "preservation_paths": [marker.as_posix()],
        "original_controller": {
            "root": controller.root.as_posix(),
            "commit": controller.head(),
            "tree": controller.index_tree(),
            "files": [
                {"path": "controller.py", "sha256": _sha(b"# authored controller\n")}
            ],
        },
        "preserved_files": [
            {"path": marker.as_posix(), "sha256": _sha(marker.read_bytes())}
        ],
    }
    request_path = tmp_path / "request" / "request.json"
    request_path.parent.mkdir()
    request_path.write_bytes(canonical_bytes(request))
    (tmp_path / "receipts").mkdir()
    (tmp_path / "scratch").mkdir()
    return SimpleNamespace(
        graph=graph,
        target=target.root,
        origin=origin,
        base=base,
        tree=candidate_tree,
        source_zip=source_zip,
        capsule_path=capsule_path,
        request_path=request_path,
        request=request,
        capsule_digest=_sha(source_zip),
        request_digest=_sha(request_path.read_bytes()),
        receipt_dir=tmp_path / "receipts",
        scratch=tmp_path / "scratch",
        controller=controller.root,
        journal_marker=marker,
    )
