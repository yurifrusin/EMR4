"""Real authored Git exercises the shared sequence, not historical policy admission."""

from dataclasses import fields, replace

import pytest

from orchestration_harness import pinned_programme_gatekeeper as gatekeeper
from orchestration_harness import trusted_git as git
from programme_maintenance_synthetic import (
    _git,
    create_synthetic_graph,
    create_synthetic_repository,
)


@pytest.fixture
def operation(tmp_path):
    graph = create_synthetic_graph(tmp_path / "graph", {"owned.py": b"VALUE = 1\n"})
    source = create_synthetic_repository(
        tmp_path / "source", {"controller.py": b"# authored inert source\n"}
    )
    source_head = source.head()
    source_identity = git.attest_repository(
        source.root,
        attested_paths=tuple(source.files),
        expected_commit=source_head,
        complete_tracked_tree=True,
    )
    head = graph.target.head()
    tree = graph.target.stage_files({"owned.py": b"VALUE = 2\n"})
    binding = {
        "target_head": head,
        "index_tree": tree,
        "branch_ref": graph.target.branch_ref,
    }
    values = {field.name: None for field in fields(gatekeeper.PinnedGatekeeperDecision)}
    values.update(
        schema_version=gatekeeper.PINNED_GATEKEEPER_DECISION_VERSION,
        admitted=True,
        reason_codes=[],
        phase="development",
        entrypoint="task_branch_commit",
        gatekeeper_clean=True,
        target_head=head,
        target_index_tree=tree,
        operation_binding=binding,
    )
    decision = gatekeeper.PinnedGatekeeperDecision(**values)
    calls = []
    after_commit_object = None
    after_ref_update = None

    def revalidate(prior, target):
        calls.append(("revalidate", target))
        admitted = prior.admitted and prior.operation_binding == binding
        try:
            if (
                git.attest_repository(
                    source.root,
                    attested_paths=tuple(source.files),
                    expected_commit=source_head,
                    complete_tracked_tree=True,
                )
                != source_identity
            ):
                admitted = False
            git.attest_target_index(
                target,
                attested_paths=tuple(graph.target.files),
                expected_head=head,
                expected_index_tree=tree,
                scratch_parent=tmp_path,
            )
        except git.TrustedGitError:
            admitted = False
        return replace(prior, admitted=admitted)

    def run_git(target, *args):
        assert target == graph.target.root
        calls.append(("git", args))
        result = _git(target, *args).decode().strip()
        if args[0] == "commit-tree" and after_commit_object is not None:
            after_commit_object()
        if args[0] == "update-ref" and after_ref_update is not None:
            after_ref_update()
        return result

    def commit(
        *,
        prior=decision,
        message="authored shared-core commit",
        after_object=None,
        after_update=None,
    ):
        nonlocal after_commit_object, after_ref_update
        after_commit_object = after_object
        after_ref_update = after_update
        return gatekeeper._commit_exact_admitted_index_core(
            prior_decision=prior,
            target_repo_root=graph.target.root,
            message=message,
            revalidate=revalidate,
            run_git=run_git,
        )

    return graph, source, decision, calls, commit


def test_shared_core_commits_the_exact_tree_and_sole_parent(operation):
    graph, _source, decision, calls, commit = operation
    index_before = (graph.target.root / ".git/index").read_bytes()
    result = commit()
    assert graph.target.head() == result
    assert _git(
        graph.target.root, "rev-list", "--parents", "-n", "1", result
    ).decode().split() == [result, decision.target_head]
    assert (
        _git(graph.target.root, "rev-parse", f"{result}^{{tree}}").decode().strip()
        == decision.target_index_tree
    )
    assert (graph.target.root / ".git/index").read_bytes() == index_before
    assert [kind if kind == "revalidate" else args[0] for kind, args in calls] == [
        "revalidate",
        "commit-tree",
        "revalidate",
        "update-ref",
        "rev-parse",
        "rev-parse",
    ]
    update = next(
        args for kind, args in calls if kind == "git" and args[0] == "update-ref"
    )
    assert update == (
        "update-ref",
        graph.target.branch_ref,
        result,
        decision.target_head,
    )
    assert graph.target.remote_head() is None


@pytest.mark.parametrize("message", ["", "   ", "x" * 501, None])
def test_invalid_message_fails_before_observation_or_mutation(operation, message):
    graph, _source, decision, calls, commit = operation
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_commit_message_invalid",
    ):
        commit(message=message)
    assert calls == []
    assert graph.target.head() == decision.target_head


@pytest.mark.parametrize("mutation", ["source", "index"])
def test_real_drift_before_branch_update_prevents_ref_advance(operation, mutation):
    graph, source, decision, calls, commit = operation

    def drift():
        if mutation == "source":
            (source.root / "controller.py").write_bytes(b"# changed authored source\n")
        else:
            graph.target.stage_files({"owned.py": b"VALUE = 3\n"})

    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_operation_binding_drift_before_commit",
    ):
        commit(after_object=drift)
    assert graph.target.head() == decision.target_head
    assert any(kind == "git" and args[0] == "commit-tree" for kind, args in calls)
    assert not any(kind == "git" and args[0] == "update-ref" for kind, args in calls)


def test_prior_denial_creates_no_commit_object_or_ref_update(operation):
    graph, _source, decision, calls, commit = operation
    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_exact_index_commit_not_admitted",
    ):
        commit(prior=replace(decision, admitted=False))
    assert all(kind == "revalidate" for kind, _args in calls)
    assert graph.target.head() == decision.target_head


def test_changed_result_head_is_reported_after_ref_update(operation):
    graph, _source, decision, calls, commit = operation

    def change_result():
        graph.target.commit_exact_index(
            expected_head=graph.target.head(),
            expected_tree=decision.target_index_tree,
            message="second authored commit for readback drift",
        )

    with pytest.raises(
        gatekeeper.admission.ProgrammeAdmissionError,
        match="gatekeeper_exact_index_commit_postcondition_failed",
    ):
        commit(after_update=change_result)
    assert graph.target.head() != decision.target_head
    assert sum(kind == "git" and args[0] == "update-ref" for kind, args in calls) == 1
    assert graph.target.remote_head() is None


def test_public_wrapper_owns_revalidation_and_git_selection(operation, monkeypatch):
    graph, source, decision, _calls, _commit = operation
    marker_manifest = {"synthetic": "wrapper wiring only"}
    observed = []

    def fixed_validator(**kwargs):
        observed.append(kwargs)
        return decision

    def core(**kwargs):
        assert kwargs["run_git"] is gatekeeper.admission._run_git
        assert kwargs["prior_decision"] is decision
        assert kwargs["message"] == "bound message"
        kwargs["revalidate"](decision, graph.target.root)
        return "wrapper-observation-only"

    monkeypatch.setattr(
        gatekeeper, "revalidate_pinned_operation_binding", fixed_validator
    )
    monkeypatch.setattr(gatekeeper, "_commit_exact_admitted_index_core", core)
    assert (
        gatekeeper.commit_exact_admitted_index(
            prior_decision=decision,
            gatekeeper_root=source.root,
            target_repo_root=graph.target.root,
            manifest=marker_manifest,
            message="bound message",
        )
        == "wrapper-observation-only"
    )
    assert observed == [
        {
            "prior_decision": decision,
            "gatekeeper_root": source.root,
            "target_repo_root": graph.target.root,
            "manifest": marker_manifest,
        }
    ]
