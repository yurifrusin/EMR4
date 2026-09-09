"""Real small Git lifecycles; synthetic adapters do not prove EMR4 admission."""

from dataclasses import fields, replace
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestration_harness import pinned_programme_gatekeeper as pg
from orchestration_harness import trusted_git as git
from programme_maintenance_synthetic import (
    SyntheticGitError,
    _git,
    create_synthetic_graph,
    create_synthetic_repository,
)


@pytest.fixture
def operation(tmp_path, monkeypatch):
    def forbidden_loader(*_args, **_kwargs):
        raise AssertionError("Historical policy loader is not this synthetic adapter")

    monkeypatch.setattr(pg.admission, "load_programme_policy", forbidden_loader)
    graph = create_synthetic_graph(tmp_path / "graph", {"owned.py": b"one\n"})
    source = create_synthetic_repository(
        tmp_path / "source", {"controller.py": b"# inert authored source\n"}
    )
    source_head = source.head()
    source_identity = git.attest_repository(
        source.root,
        attested_paths=tuple(source.files),
        expected_commit=source_head,
        complete_tracked_tree=True,
    )
    original_head = graph.target.head()
    tree = graph.target.stage_files({"owned.py": b"two\n"})
    preservation = tmp_path / "preservation"
    preservation.mkdir()
    bundle = preservation / "bundle"
    bundle.write_bytes(b"authored preservation marker\n")
    sinks = {phase: tmp_path / (phase + "-receipts") for phase in ("commit", "push")}
    for sink in sinks.values():
        sink.mkdir()
    state = SimpleNamespace(
        graph=graph,
        source=source,
        original_head=original_head,
        tree=tree,
        committed=None,
        calls=[],
        deny_initial=False,
        deny_bound=False,
        deny_post=False,
        fail_final=False,
        before_push=None,
    )

    def observations(expected_head, expected_remote):
        current_source = git.attest_repository(
            source.root,
            attested_paths=tuple(source.files),
            expected_commit=source_head,
            complete_tracked_tree=True,
        )
        if current_source != source_identity:
            raise pg.admission.ProgrammeAdmissionError("synthetic_source_drift")
        target = git.attest_target_index(
            graph.target.root,
            attested_paths=tuple(graph.target.files),
            expected_head=expected_head,
            expected_index_tree=tree,
            scratch_parent=tmp_path,
        )
        if (
            graph.target.remote_head() != expected_remote
            or _git(graph.target.root, "symbolic-ref", "HEAD").decode().strip()
            != graph.target.branch_ref
            or _git(graph.target.root, "config", "--get", "remote.origin.url")
            .decode()
            .strip()
            != graph.origin.as_posix()
        ):
            raise pg.admission.ProgrammeAdmissionError(
                "synthetic_remote_or_branch_drift"
            )
        return target

    def evaluate(**kwargs):
        assert kwargs["gatekeeper_root"] == source.root
        assert kwargs["target_repo_root"] == graph.target.root
        assert kwargs["manifest"] == {"evidence": "synthetic shared-core exercise"}
        entrypoint, phase = kwargs["entrypoint"], kwargs["phase"]
        receipt = kwargs.get("receipt_sink_binding")
        state.calls.append(("evaluate", phase, receipt is not None))
        expected_head = (
            original_head if entrypoint == "task_branch_commit" else state.committed
        )
        if not expected_head:
            raise pg.admission.ProgrammeAdmissionError("synthetic_missing_commit")
        expected_remote = state.committed if phase == "post-push" else None
        target = observations(expected_head, expected_remote)
        binding = {
            "target_head": expected_head,
            "index_tree": tree,
            "branch_ref": graph.target.branch_ref,
            "explicit_destination": graph.origin.as_posix(),
            "force_with_lease": graph.target.branch_ref + ":",
            "exact_push_refspec": expected_head + ":" + graph.target.branch_ref,
            "receipt_sink": receipt,
        }
        values = {field.name: None for field in fields(pg.PinnedGatekeeperDecision)}
        values.update(
            schema_version=pg.PINNED_GATEKEEPER_DECISION_VERSION,
            admitted=not (
                state.deny_initial
                or (state.deny_bound and receipt is not None)
                or (state.deny_post and phase == "post-push")
            ),
            reason_codes=[],
            phase=phase,
            entrypoint=entrypoint,
            gatekeeper_commit=source_head,
            gatekeeper_tree=source_identity["head_tree"],
            gatekeeper_clean=True,
            target_branch=graph.target.branch_ref,
            target_head=expected_head,
            target_index_tree=tree,
            expected_origin_head=expected_remote,
            target_cleanliness={"trusted_git_identity": target["repository"]},
            source_trusted_git_identity=source_identity,
            operation_binding=binding,
            receipt_sink_binding=receipt,
            remote_identity={"normalized_push_url": graph.origin.as_posix()},
        )
        return pg.PinnedGatekeeperDecision(**values)

    def revalidate(**kwargs):
        prior = kwargs["prior_decision"]
        fresh = evaluate(
            gatekeeper_root=kwargs["gatekeeper_root"],
            target_repo_root=kwargs["target_repo_root"],
            manifest=kwargs["manifest"],
            entrypoint=prior.entrypoint,
            phase=prior.phase,
            receipt_sink_binding=prior.receipt_sink_binding,
        )
        if not prior.admitted or fresh.operation_binding != prior.operation_binding:
            return replace(fresh, admitted=False)
        return fresh

    def reserve(**kwargs):
        state.calls.append(("reserve", kwargs["operation"]))
        return pg._reserve_operation_receipt_core(
            **kwargs,
            preservation_paths=lambda _target: (bundle,),
        )

    def run_git(root, *args):
        assert root == graph.target.root
        state.calls.append(("git", args))
        if args[0] == "push" and state.before_push:
            state.before_push()
        return _git(root, *args).decode().strip()

    def commit(**kwargs):
        def bound(prior, target):
            return revalidate(
                prior_decision=prior,
                gatekeeper_root=source.root,
                target_repo_root=target,
                manifest=kwargs["manifest"],
            )

        result = pg._commit_exact_admitted_index_core(
            prior_decision=kwargs["prior_decision"],
            target_repo_root=kwargs["target_repo_root"],
            message=kwargs["message"],
            revalidate=bound,
            run_git=run_git,
        )
        state.committed = result
        return result

    def final_revalidation(**kwargs):
        state.calls.append(("final", kwargs["expected_remote_sha"]))
        observations(kwargs["result_sha"], kwargs["expected_remote_sha"])
        assert kwargs["result_tree"] == tree
        if state.fail_final:
            raise pg.admission.ProgrammeAdmissionError("synthetic_final_failure")
        return {
            "status": "passed",
            "evidence": "synthetic adapter",
            "result_sha": kwargs["result_sha"],
        }

    services = pg._OperationServices(
        evaluate=evaluate,
        reserve=reserve,
        revalidate=revalidate,
        commit=commit,
        final_revalidation=final_revalidation,
        run_git=run_git,
    )
    common = dict(
        gatekeeper_root=source.root,
        target_repo_root=graph.target.root,
        manifest={"evidence": "synthetic shared-core exercise"},
        services=services,
    )
    state.commit = lambda: pg._execute_exact_index_commit_core(
        **common,
        message="authored shared lifecycle",
        receipt_directory=sinks["commit"],
    )
    state.push = lambda: pg._execute_exact_sha_push_core(
        **common,
        receipt_directory=sinks["push"],
    )
    state.sinks = sinks
    return state


def _markers(sink):
    # This directory was created solely by the current synthetic fixture.
    return [path.read_bytes() for path in sink.iterdir()]


def test_shared_commit_and_push_complete_with_exact_receipts_and_remote_readback(
    operation,
):
    before_index = (operation.graph.target.root / ".git/index").read_bytes()
    committed = operation.commit()
    assert isinstance(committed["result_sha"], str)
    assert json.loads(Path(committed["receipt_path"]).read_bytes()) == committed
    assert (
        committed["admitted_operation_binding"]["receipt_sink"]
        == committed["receipt_sink"]
    )
    assert _git(
        operation.graph.target.root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        committed["result_sha"],
    ).decode().split() == [committed["result_sha"], operation.original_head]
    assert committed["result_tree"] == operation.tree
    assert operation.graph.target.remote_head() is None
    pushed = operation.push()
    assert json.loads(Path(pushed["receipt_path"]).read_bytes()) == pushed
    assert (
        pushed["result_sha"]
        == committed["result_sha"]
        == operation.graph.target.remote_head()
    )
    assert pushed["post_push_readback_sha"] == committed["result_sha"]
    assert pushed["post_push_decision_admitted"] is True
    assert (operation.graph.target.root / ".git/index").read_bytes() == before_index
    pushes = [
        row[1] for row in operation.calls if row[0] == "git" and row[1][0] == "push"
    ]
    assert pushes == [
        (
            "push",
            "--no-verify",
            "--force-with-lease=" + operation.graph.target.branch_ref + ":",
            operation.graph.origin.as_posix(),
            committed["result_sha"] + ":" + operation.graph.target.branch_ref,
        )
    ]


@pytest.mark.parametrize("phase", ["commit", "push"])
def test_initial_denial_precedes_reservation(operation, phase):
    if phase == "push":
        operation.commit()
    operation.deny_initial = True
    before = operation.graph.target.head()
    with pytest.raises(pg.admission.ProgrammeAdmissionError, match="not_admitted"):
        getattr(operation, phase)()
    assert _markers(operation.sinks[phase]) == []
    assert operation.graph.target.head() == before
    assert operation.graph.target.remote_head() is None


@pytest.mark.parametrize("phase", ["commit", "push"])
def test_receipt_bound_denial_retains_empty_marker_and_no_effect(operation, phase):
    if phase == "push":
        operation.commit()
    operation.deny_bound = True
    before = operation.graph.target.head()
    with pytest.raises(pg.admission.ProgrammeAdmissionError, match="not_admitted"):
        getattr(operation, phase)()
    assert _markers(operation.sinks[phase]) == [b""]
    assert operation.graph.target.head() == before
    assert operation.graph.target.remote_head() is None


@pytest.mark.parametrize("phase", ["commit", "push"])
def test_final_failure_retains_effect_evidence_without_completed_receipt(
    operation, phase
):
    if phase == "push":
        operation.commit()
    operation.fail_final = True
    with pytest.raises(
        pg.admission.ProgrammeAdmissionError, match="synthetic_final_failure"
    ):
        getattr(operation, phase)()
    assert _markers(operation.sinks[phase]) == [b""]
    assert (
        operation.graph.target.head() == operation.committed != operation.original_head
    )
    assert operation.graph.target.remote_head() == (
        operation.committed if phase == "push" else None
    )


def test_remote_movement_after_revalidation_is_rejected_by_actual_lease(operation):
    operation.commit()

    def move_remote():
        _git(
            operation.graph.target.root,
            "push",
            operation.graph.origin.as_posix(),
            operation.original_head + ":" + operation.graph.target.branch_ref,
        )

    operation.before_push = move_remote
    with pytest.raises(SyntheticGitError, match="synthetic_git_failed:push"):
        operation.push()
    assert operation.graph.target.remote_head() == operation.original_head
    assert _markers(operation.sinks["push"]) == [b""]


def test_post_push_denial_does_not_finalize_or_retry(operation):
    operation.commit()
    operation.deny_post = True
    with pytest.raises(
        pg.admission.ProgrammeAdmissionError,
        match="gatekeeper_exact_push_postcondition_failed",
    ):
        operation.push()
    assert operation.graph.target.remote_head() == operation.committed
    assert _markers(operation.sinks["push"]) == [b""]
    assert sum(row[0] == "git" and row[1][0] == "push" for row in operation.calls) == 1


def test_consumed_commit_cannot_create_another_commit(operation):
    operation.commit()
    with pytest.raises(
        git.TrustedGitError, match="trusted_git_expected_commit_mismatch"
    ):
        operation.commit()
    assert operation.graph.target.head() == operation.committed
    assert (
        sum(row[0] == "git" and row[1][0] == "commit-tree" for row in operation.calls)
        == 1
    )


@pytest.mark.parametrize(
    "name", ["execute_exact_index_commit", "execute_exact_sha_push"]
)
def test_public_operation_wrappers_reject_dependency_input(name):
    with pytest.raises(TypeError, match="services"):
        getattr(pg, name)(services=object())


def test_public_dependency_factory_uses_only_existing_owned_functions():
    services = pg._operation_services()
    assert services.evaluate is pg.evaluate_pinned_programme_operation
    assert services.reserve is pg.reserve_operation_receipt
    assert services.revalidate is pg.revalidate_pinned_operation_binding
    assert services.commit is pg.commit_exact_admitted_index
    assert services.final_revalidation is pg._final_operation_revalidation
    assert services.run_git is pg.admission._run_git
