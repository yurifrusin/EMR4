"""Native Git + fully isolated code capsule, on newly authored fixtures only."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from orchestration_harness import controller_maintenance_runner as runner
from orchestration_harness import controller_maintenance_journal as journal_scope
from orchestration_harness.controller_maintenance_request import canonical_bytes

from maintenance_runner_synthetic import build_fixture
from programme_maintenance_synthetic import _git


BOOTSTRAP = (
    Path(__file__).resolve().parents[1]
    / "scripts/raisa_ariadne_maintenance_bootstrap.py"
)
# This literal is the trusted outer launcher in these tests. It authenticates
# and compiles the same bootstrap bytes; no post-hash file reopening occurs.
LAUNCH = """import hashlib,sys,types
path,expected,*args=sys.argv[1:]
with open(path,'rb') as stream: raw=stream.read(1048577)
if len(raw)>1048576 or hashlib.sha256(raw).hexdigest()!=expected:
 raise SystemExit('bootstrap_source_digest_mismatch')
module=types.ModuleType('__main__');module.__file__=path;module.__package__=None
sys.modules['__main__']=module;sys.argv=[path,*args]
exec(compile(raw,path,'exec',dont_inherit=True),module.__dict__)
"""


def _invoke(fixture, *, bootstrap_digest=None, request_digest=None):
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper()
        in {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "TEMP", "TMP", "SYSTEMDRIVE"}
    }
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-S",
            "-c",
            LAUNCH,
            str(BOOTSTRAP),
            bootstrap_digest or hashlib.sha256(BOOTSTRAP.read_bytes()).hexdigest(),
            "--capsule",
            str(fixture.capsule_path),
            "--capsule-sha256",
            fixture.capsule_digest,
            "--request",
            str(fixture.request_path),
            "--request-sha256",
            request_digest or fixture.request_digest,
        ],
        cwd=fixture.target,
        env=environment,
        capture_output=True,
        text=True,
        timeout=240,
    )


def _success(result):
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_full_isolated_capsule_evaluates_without_loading_target_code(tmp_path):
    fixture = build_fixture(tmp_path)
    package = fixture.target / "orchestration_harness"
    package.mkdir()
    (package / "__init__.py").write_text(
        "raise RuntimeError('target package imported')\n"
    )
    (fixture.target / "sitecustomize.py").write_text(
        "raise RuntimeError('target hook imported')\n"
    )
    result = _success(_invoke(fixture))
    assert result["status"] == "evaluated"
    assert result["binding"]["target_head"] == fixture.base
    assert result["binding"]["index_tree"] == fixture.tree
    assert result["complete_physical_worktree_attested"] is False
    assert list(fixture.receipt_dir.iterdir()) == []
    assert _git(fixture.target, "rev-parse", "HEAD").decode().strip() == fixture.base


def test_exact_commit_push_activation_and_same_request_replay_denial(tmp_path):
    fixture = build_fixture(tmp_path, operation="execute")
    hooks = fixture.target / ".git/hooks"
    hooks.mkdir()
    for name in ("reference-transaction", "pre-push"):
        (hooks / name).write_text("#!/bin/sh\nexit 91\n")
    _git(
        fixture.target,
        "-c",
        "core.hooksPath=" + os.devnull,
        "tag",
        "-a",
        "authored-do-not-publish",
        fixture.base,
        "-m",
        "authored tag",
    )
    _git(fixture.target, "config", "core.hooksPath", str(hooks))
    _git(fixture.target, "config", "push.followTags", "true")
    index_before = (fixture.target / ".git/index").read_bytes()
    result = _success(_invoke(fixture))
    assert result["status"] == "activated"
    commit = result["commit_receipt"]["result_sha"]
    assert result["publication_receipt"]["result_sha"] == commit
    assert result["activation"]["journal_base_commit"] == commit
    assert _git(
        fixture.target, "rev-list", "--parents", "-n", "1", commit
    ).decode().split() == [commit, fixture.base]
    assert (
        _git(fixture.target, "rev-parse", "HEAD^{tree}").decode().strip()
        == fixture.tree
    )
    assert _git(fixture.target, "ls-remote", "--tags", str(fixture.origin)) == b""
    assert (
        _git(
            fixture.target,
            "ls-remote",
            "--refs",
            str(fixture.origin),
            fixture.request["manifest"]["destination_ref"],
        )
        .decode()
        .split()[0]
        == commit
    )
    activation_raw = Path(result["activation_path"]).read_bytes()
    assert json.loads(activation_raw) == result["activation"]
    assert (
        hashlib.sha256(activation_raw).hexdigest() == result["activation_file_sha256"]
    )
    publication_raw = Path(result["publication_receipt"]["receipt_path"]).read_bytes()
    assert (
        hashlib.sha256(publication_raw).hexdigest()
        == result["activation"]["publication_receipt_sha256"]
    )
    assert (fixture.target / ".git/index").read_bytes() == index_before
    receipts = {p.name: p.read_bytes() for p in fixture.receipt_dir.iterdir()}
    assert len(receipts) == 3 and all(receipts.values())
    retry = _invoke(fixture)
    assert retry.returncode != 0
    assert {p.name: p.read_bytes() for p in fixture.receipt_dir.iterdir()} == receipts
    assert _git(fixture.target, "rev-parse", "HEAD").decode().strip() == commit


def test_outer_launcher_rejects_wrong_bootstrap_digest_before_capsule_execution(
    tmp_path,
):
    fixture = build_fixture(tmp_path)
    result = _invoke(fixture, bootstrap_digest="0" * 64)
    assert result.returncode != 0
    assert "bootstrap_source_digest_mismatch" in result.stderr
    assert list(fixture.receipt_dir.iterdir()) == []


def _refresh_request(fixture):
    fixture.request["manifest_sha256"] = hashlib.sha256(
        canonical_bytes(fixture.request["manifest"])
    ).hexdigest()
    raw = canonical_bytes(fixture.request)
    fixture.request_path.write_bytes(raw)
    fixture.request_digest = hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize(
    "change,reason",
    [
        (
            lambda fx: fx.request["manifest"].update(source_commit="0" * 40),
            "maintenance_source_identity_mismatch",
        ),
        (
            lambda fx: fx.request["manifest"].update(generation_id="other-generation"),
            "maintenance_source_identity_mismatch",
        ),
        (
            lambda fx: fx.request["manifest"].update(
                destination_ref="refs/heads/master"
            ),
            "manifest_invalid",
        ),
        (
            lambda fx: fx.request["preserved_files"][0].update(
                path=(fx.target / "frozen.py").as_posix()
            ),
            "maintenance_preservation_overlaps_governed_root",
        ),
    ],
)
def test_bound_request_rejects_source_destination_and_preservation_substitutions(
    tmp_path, change, reason
):
    fixture = build_fixture(tmp_path, operation="execute")
    change(fixture)
    _refresh_request(fixture)
    result = _invoke(fixture)
    assert result.returncode != 0
    assert reason in result.stdout + result.stderr
    assert list(fixture.receipt_dir.iterdir()) == []
    assert _git(fixture.target, "rev-parse", "HEAD").decode().strip() == fixture.base


def test_changed_remote_lease_prevents_any_reservation_or_commit(tmp_path):
    fixture = build_fixture(tmp_path, operation="execute")
    competing = (
        _git(
            fixture.target,
            "commit-tree",
            fixture.tree,
            "-p",
            fixture.base,
            "-m",
            "authored competing remote update",
        )
        .decode()
        .strip()
    )
    _git(
        fixture.target,
        "push",
        str(fixture.origin),
        competing + ":" + fixture.request["manifest"]["destination_ref"],
    )
    result = _invoke(fixture)
    assert result.returncode != 0
    assert "maintenance_remote_lease_mismatch" in result.stdout + result.stderr
    assert list(fixture.receipt_dir.iterdir()) == []
    assert _git(fixture.target, "rev-parse", "HEAD").decode().strip() == fixture.base


def test_preexisting_journal_at_base_blocks_maintenance_before_effects(tmp_path):
    fixture = build_fixture(
        tmp_path,
        operation="execute",
        base_extra_files={
            journal_scope.JOURNAL_FILES[0][0]: b"authored preexisting marker\n"
        },
    )
    result = _invoke(fixture)
    assert result.returncode != 0
    assert "maintenance_journal_base_path_present" in result.stdout + result.stderr
    assert list(fixture.receipt_dir.iterdir()) == []
    assert _git(fixture.target, "rev-parse", "HEAD").decode().strip() == fixture.base


def _native_inputs(fixture):
    # Direct test seam for failure injection. The child-process tests above
    # independently exercise the complete isolated package without injection.
    spec = importlib.util.spec_from_file_location(
        "maintenance_failure_bootstrap", BOOTSTRAP
    )
    boot = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = boot
    spec.loader.exec_module(boot)
    source_file = boot._read_file(fixture.capsule_path, 4 * 1024 * 1024)
    return dict(
        verified_source=boot.verify_capsule(
            source_file.data, expected_sha256=fixture.capsule_digest
        ),
        source_file=source_file,
        request_file=boot._read_file(fixture.request_path, 65536),
    )


def test_lost_push_response_preserves_uncertain_receipts_and_denies_retry(
    tmp_path, monkeypatch
):
    fixture = build_fixture(tmp_path, operation="execute")
    inputs = _native_inputs(fixture)
    real_git = runner._git
    pushes = []

    def lose_push_response(root, *args):
        result = real_git(root, *args)
        if args[0] == "push":
            pushes.append(args)
            raise runner.MaintenanceOperationError("synthetic_push_response_lost")
        return result

    monkeypatch.setattr(runner, "_git", lose_push_response)
    with pytest.raises(
        runner.MaintenanceOperationError, match="synthetic_push_response_lost"
    ):
        runner.run_request(inputs["request_file"].data, **inputs)
    committed = real_git(fixture.target, "rev-parse", "HEAD")
    assert committed != fixture.base
    assert (
        real_git(
            fixture.target,
            "ls-remote",
            "--refs",
            str(fixture.origin),
            fixture.request["manifest"]["destination_ref"],
        ).split()[0]
        == committed
    )
    receipts = {p.name: p.read_bytes() for p in fixture.receipt_dir.iterdir()}
    assert len(receipts) == 3
    assert sum(bool(raw) for raw in receipts.values()) == 1
    with pytest.raises(ValueError):
        runner.run_request(inputs["request_file"].data, **inputs)
    assert len(pushes) == 1
    assert {p.name: p.read_bytes() for p in fixture.receipt_dir.iterdir()} == receipts


def test_old_policy_loaders_are_unreachable_in_native_maintenance_evaluation(
    tmp_path, monkeypatch
):
    fixture = build_fixture(tmp_path)
    inputs = _native_inputs(fixture)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("historical whole-tree policy loader executed")

    monkeypatch.setattr(runner.policy_functions, "load_programme_policy", forbidden)
    monkeypatch.setattr(runner.git, "attest_repository", forbidden)
    result = runner.run_request(inputs["request_file"].data, **inputs)
    assert result["status"] == "evaluated"


def test_journal_manifest_and_committed_scope_share_activation_base(
    tmp_path, monkeypatch
):
    fixture = build_fixture(tmp_path, operation="execute")
    inputs = _native_inputs(fixture)
    result = runner.run_request(inputs["request_file"].data, **inputs)
    activation_bytes = Path(result["activation_path"]).read_bytes()
    original = fixture.request["original_controller"]
    binding = journal_scope.bind_journal_base(
        activation_bytes,
        expected_activation_sha256=result["activation_file_sha256"],
        manifest_payload=canonical_bytes(fixture.request["manifest"]),
        original_commit=original["commit"],
        original_tree=original["tree"],
        governing_commit=fixture.base,
        governing_tree=fixture.request["manifest"]["base_tree"],
    )
    base = result["activation"]["maintenance_commit"]
    assert result["journal_manifest_base"] == base
    assert result["journal_implementation_accepted"] is False
    # This test exercises Git scope with authored marker bytes. It does not
    # execute or claim acceptance of the real frozen journal implementation.
    authored = {
        path: ("authored journal scope marker " + str(index)).encode()
        for index, (path, _) in enumerate(journal_scope.JOURNAL_FILES)
    }
    monkeypatch.setattr(
        journal_scope,
        "JOURNAL_FILES",
        tuple(
            (path, hashlib.sha256(raw).hexdigest()) for path, raw in authored.items()
        ),
    )
    tree = fixture.graph.target.stage_files(authored)
    manifest = {
        "schema_version": "ariadne.maintenance_journal_scope.v1",
        "phase": "development",
        "base_commit": base,
        "candidate_head": base,
        "candidate_tree": tree,
        "paths": list(authored),
    }
    normalized = journal_scope.validate_journal_manifest(manifest, binding=binding)
    evidence = journal_scope.validate_journal_committed_scope(
        fixture.target, manifest, binding=binding, scratch_parent=fixture.scratch
    )
    assert normalized["base_commit"] == evidence["journal_base_commit"] == base
    assert evidence["paths"] == list(authored)
    assert evidence["maintenance_history_preserved"] is True
    assert evidence["operation_authority"] is False
    stale = {**manifest, "base_commit": fixture.base}
    for validate in (
        lambda: journal_scope.validate_journal_manifest(stale, binding=binding),
        lambda: journal_scope.validate_journal_committed_scope(
            fixture.target, stale, binding=binding, scratch_parent=fixture.scratch
        ),
    ):
        with pytest.raises(
            journal_scope.MaintenanceJournalError,
            match="journal_manifest_base_mismatch",
        ):
            validate()
    commit = (
        _git(
            fixture.target,
            "commit-tree",
            tree,
            "-p",
            base,
            "-m",
            "authored two-file journal scope",
        )
        .decode()
        .strip()
    )
    _git(fixture.target, "update-ref", "HEAD", commit, base)
    committed = {**manifest, "phase": "committed", "candidate_head": commit}
    evidence = journal_scope.validate_journal_committed_scope(
        fixture.target, committed, binding=binding, scratch_parent=fixture.scratch
    )
    assert evidence["journal_base_commit"] == base
    assert evidence["candidate_head"] == commit
    fixture.graph.target.stage_files({"owned.py": b"unauthorized maintenance change\n"})
    with pytest.raises(ValueError):
        journal_scope.validate_journal_committed_scope(
            fixture.target, committed, binding=binding, scratch_parent=fixture.scratch
        )
