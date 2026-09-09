"""Filesystem-only tests for the shared receipt reservation core."""

from __future__ import annotations

import json
import os
from dataclasses import fields, replace
from pathlib import Path

import pytest

from orchestration_harness import pinned_programme_gatekeeper as gatekeeper


def _decision(source: Path, target: Path) -> gatekeeper.PinnedGatekeeperDecision:
    values = {field.name: None for field in fields(gatekeeper.PinnedGatekeeperDecision)}
    values.update(
        schema_version=gatekeeper.PINNED_GATEKEEPER_DECISION_VERSION,
        admitted=True,
        reason_codes=[],
        phase="development",
        entrypoint="task_branch_commit",
        gatekeeper_clean=True,
        gatekeeper_commit="a" * 40,
        gatekeeper_tree="b" * 40,
        target_branch="refs/heads/synthetic",
        target_head="c" * 40,
        target_index_tree="d" * 40,
        target_cleanliness={
            "trusted_git_identity": {
                "gitdir": {"resolved_path": (target / ".git").as_posix()},
                "commondir": {"resolved_path": (target / ".git").as_posix()},
            }
        },
        source_trusted_git_identity={
            "gitdir": {"resolved_path": (source / ".git").as_posix()},
            "commondir": {"resolved_path": (source / ".git").as_posix()},
        },
        operation_binding={"target_head": "c" * 40},
    )
    return gatekeeper.PinnedGatekeeperDecision(**values)


@pytest.fixture
def receipt_case(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    sink = tmp_path / "receipts"
    preserve = tmp_path / "preserve" / "bundle.tar"
    for path in (source / ".git", target / ".git", sink, preserve.parent):
        path.mkdir(parents=True)
    preserve.write_bytes(b"preserved")
    decision = _decision(source, target)
    source_admin = tmp_path / "source-admin"
    target_common = tmp_path / "target-common"
    source_admin.mkdir()
    target_common.mkdir()
    decision.source_trusted_git_identity["gitdir"]["resolved_path"] = (
        source_admin.as_posix()
    )
    decision.target_cleanliness["trusted_git_identity"]["commondir"][
        "resolved_path"
    ] = target_common.as_posix()

    def callback(_target):
        return (preserve,)

    return source, target, sink, decision, callback


def _reserve(case, *, sink=None, callback=None):
    source, target, default_sink, decision, default_callback = case
    return gatekeeper._reserve_operation_receipt_core(
        receipt_directory=sink or default_sink,
        operation="commit",
        decision=decision,
        gatekeeper_root=source,
        target_repo_root=target,
        preservation_paths=callback or default_callback,
    )


def test_shared_receipt_success_finalizes_durably_and_reads_back(receipt_case):
    reservation = _reserve(receipt_case)
    payload = {"status": "completed", "value": "authored"}
    reservation.finalize(payload)
    assert reservation.finalized is True
    assert json.loads(reservation.path.read_bytes()) == payload
    assert reservation.descriptor == -1
    if os.name != "nt":
        assert reservation.path.stat().st_mode & 0o777 == 0o600


def test_shared_receipt_collision_never_overwrites(receipt_case):
    first = _reserve(receipt_case)
    first.close_unfinalized()
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_collision",
    ):
        _reserve(receipt_case)
    assert first.path.read_bytes() == b""


@pytest.mark.parametrize(
    "location",
    ["source", "target", "gitdir", "commondir", "preserve", "preserve_parent"],
)
def test_shared_receipt_excludes_governed_and_preservation_locations(
    receipt_case, location
):
    source, target, sink, decision, callback = receipt_case
    roots = {
        "source": source,
        "target": target,
        "gitdir": Path(decision.source_trusted_git_identity["gitdir"]["resolved_path"]),
        "commondir": Path(
            decision.target_cleanliness["trusted_git_identity"]["commondir"][
                "resolved_path"
            ]
        ),
        "preserve": callback(target)[0],
        "preserve_parent": callback(target)[0].parent,
    }
    reason = (
        "gatekeeper_receipt_directory_invalid"
        if location == "preserve"
        else "gatekeeper_receipt_directory_forbidden"
    )
    with pytest.raises(gatekeeper.admission.ProgrammeAdmissionError, match=reason):
        _reserve(receipt_case, sink=roots[location])


@pytest.mark.parametrize("missing", ["source", "target"])
def test_shared_receipt_rejects_absent_trusted_identities(receipt_case, missing):
    source, target, sink, decision, callback = receipt_case
    denied = replace(
        decision,
        **(
            {"source_trusted_git_identity": None}
            if missing == "source"
            else {"target_cleanliness": None}
        ),
    )
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_repository_identity_missing",
    ):
        gatekeeper._reserve_operation_receipt_core(
            receipt_directory=sink,
            operation="commit",
            decision=denied,
            gatekeeper_root=source,
            target_repo_root=target,
            preservation_paths=callback,
        )


def test_shared_receipt_rejects_nonexistent_sink(receipt_case, tmp_path):
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_directory_invalid",
    ):
        _reserve(receipt_case, sink=tmp_path / "does-not-exist")


def test_shared_receipt_double_finalize_is_rejected(receipt_case):
    reservation = _reserve(receipt_case)
    reservation.finalize({"status": "completed"})
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_already_finalized",
    ):
        reservation.finalize({"status": "again"})


def test_shared_receipt_abandoned_marker_remains_empty_and_exclusive(receipt_case):
    reservation = _reserve(receipt_case)
    marker = reservation.path
    reservation.close_unfinalized()
    assert marker.exists() and marker.read_bytes() == b""
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_collision",
    ):
        _reserve(receipt_case)


def test_shared_receipt_failed_write_preserves_collision_marker(
    receipt_case, monkeypatch
):
    reservation = _reserve(receipt_case)
    monkeypatch.setattr(gatekeeper.os, "write", lambda _fd, _data: 0)
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_write_failed",
    ):
        reservation.finalize({"status": "completed"})
    assert reservation.finalized is False
    assert reservation.descriptor == -1
    assert reservation.path.read_bytes() == b""
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_receipt_collision",
    ):
        _reserve(receipt_case)


def test_public_wrapper_preserves_policy_loader_boundary(receipt_case, monkeypatch):
    source, target, sink, decision, _callback = receipt_case
    observed = []
    preserve_root = sink.parent / "policy-preserve"
    preserve_root.mkdir()

    def loader(root):
        observed.append(root)
        return type(
            "Policy",
            (),
            {
                "state": {
                    "clockwork_snapshot": {
                        "git_bundle": {"path": str(preserve_root / "bundle")},
                        "pre_g0_untracked_archive": {
                            "path": str(preserve_root / "archive")
                        },
                    }
                }
            },
        )()

    monkeypatch.setattr(gatekeeper.admission, "load_programme_policy", loader)
    (preserve_root / "bundle").write_bytes(b"bundle")
    (preserve_root / "archive").write_bytes(b"archive")
    reservation = gatekeeper.reserve_operation_receipt(
        receipt_directory=sink,
        operation="commit",
        decision=decision,
        gatekeeper_root=source,
        target_repo_root=target,
    )
    reservation.close_unfinalized()
    assert observed == [target]
