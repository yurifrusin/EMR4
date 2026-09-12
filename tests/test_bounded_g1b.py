"""Bounded controller contracts; integration receives explicit ordinary assets.

Run build_integration_suite(asset_root) from the reviewed external source capsule.
No fixture reads the live repository or imports its conftest. Historical authority
is hash pinned, so a later active gate cannot silently change the test baseline.
"""
from __future__ import annotations

import copy
import ast
import builtins
import os
import subprocess
import tempfile
import unittest
import types
from contextlib import ExitStack, contextmanager
from pathlib import Path
from unittest.mock import patch

from orchestration_harness import bounded_g1b as b
from orchestration_harness import pinned_programme_gatekeeper as pg
from orchestration_harness import programme_admission as pa
from orchestration_harness import configuration_core as core
from orchestration_harness import raisa_policy as rp
from scripts import raisa_ariadne_recovery_preflight as pf


@contextmanager
def no_legacy_observation():
    with ExitStack() as stack:
        for owner, name in ((pa, "attest_programme_authority"),
                            (b.trusted_git, "attest_repository"),
                            (b.trusted_git, "indexed_paths_under")):
            stack.enter_context(patch.object(owner, name, side_effect=AssertionError("legacy observation: " + name)))
        yield


class ClosedRequestTests(unittest.TestCase):
    def test_malformed_recognised_requests_never_fall_through(self):
        for manifest in ({"schema_version": b.REQUEST_VERSION},
                         {"schema_version": "ariadne.bounded_g1b_request.future"},
                         {"schema_version": None, "operation_kind": "accept_journal"},
                         {"operation_kind": "accept_g1b"}, {"operation_kind": "implement_g1c"},
                         {"task_class": b.G1C_TASK}, {"operation_kind": "accept_g1c"},
                         {"operation_kind": "implement_g1d"}, {"task_class": b.G1D_TASK},
                         {"operation_kind": "accept_g1d"}, {"operation_kind": "assess_g1e"}, {"task_class": b.G1E_TASK}):
            with self.subTest(manifest=manifest), no_legacy_observation(), \
                    patch.object(pa, "load_programme_policy", side_effect=AssertionError("old loader")), \
                    patch.object(pf, "load_programme_policy", side_effect=AssertionError("old loader")):
                report = pf.build_report(Path("never-read"), manifest)
                self.assertEqual(report["reason_codes"], ["bounded_g1b_context_required"])
                for call in (
                    lambda: pa.evaluate_programme_operation_admission(repo_root=Path("never-read"),
                        manifest=manifest, entrypoint="task_branch_commit", phase="development"),
                    lambda: pg.evaluate_pinned_programme_operation(gatekeeper_root=Path("source"),
                        target_repo_root=Path("never-read"), manifest=manifest,
                        entrypoint="task_branch_commit", phase="development"),
                ):
                    decision = call()
                    self.assertIs(type(decision), b.BoundedG1BDecision)
                    self.assertFalse(decision.policy_admitted)
                    self.assertFalse(decision.execution_authorized)
                    self.assertFalse(hasattr(decision, "admitted"))
                for entrypoint in ("provider_invocation", "clockwork_tick_mutation", "recovery_preflight"):
                    decision = pa.evaluate_programme_admission(repo_root=Path("never-read"),
                                                               manifest=manifest, entrypoint=entrypoint)
                    self.assertFalse(decision.admitted)
                    self.assertEqual(decision.reason_codes, ["bounded_g1b_explicit_operation_context_required"])
                scope = pa.evaluate_committed_scope(repo_root=Path("never-read"), manifest=manifest, phase="development")
                self.assertFalse(scope.admitted)
                self.assertEqual(scope.reason_codes, ["bounded_g1b_explicit_operation_context_required"])
                with patch.object(pa, "strict_json_object", return_value=manifest):
                    for call in (
                        lambda: pa.require_programme_admission(repo_root=Path("never-read"),
                            manifest_path=Path("manifest"), entrypoint="provider_invocation"),
                        lambda: pa.require_programme_operation_admission(repo_root=Path("never-read"),
                            manifest_path=Path("manifest"), entrypoint="task_branch_commit", phase="development"),
                    ):
                        with self.assertRaises(pa.ProgrammeAdmissionError):
                            call()

    def test_legacy_effect_entrypoints_reject_bounded_requests(self):
        manifest = {"schema_version": b.REQUEST_VERSION}
        common = dict(gatekeeper_root=Path("source"), target_repo_root=Path("never-read"), manifest=manifest)
        calls = (
            lambda: pg.execute_exact_index_commit(**common, message="no", receipt_directory=Path("receipts")),
            lambda: pg.execute_exact_sha_push(**common, receipt_directory=Path("receipts")),
            lambda: pg.commit_exact_admitted_index(**common, message="no", prior_decision=None),
        )
        with no_legacy_observation(), patch.object(pg, "_operation_services", side_effect=AssertionError("effect")):
            for call in calls:
                with self.subTest(call=call), self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    call()
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_reviewed_publisher_required")

    def test_parsers_reject_ambiguous_or_nonfinite_values(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e999}', b'[]'):
            with self.subTest(raw=raw), self.assertRaises((ValueError, b.BoundedG1BError)):
                b._json(raw)
        for raw in (b'x: 1\nx: 2\n', b'x: .nan\n', b'x: 2026-09-12\n', b'x: &x [*x]\n'):
            with self.subTest(raw=raw), self.assertRaises((ValueError, b.BoundedG1BError)):
                b._document(raw, "fixture.yaml")
        self.assertNotEqual(b._canonical({"x": False}), b._canonical({"x": 0}))


class NativeFixture:
    def __init__(self, assets: Path):
        self.temporary = tempfile.TemporaryDirectory(prefix="g1b-contract-")
        self.home = Path(self.temporary.name)
        self.root = self.home / "target"
        self.root.mkdir()
        self.scratch = self.home / "index-scratch"
        self.scratch.mkdir()
        self.assets = assets
        self.source = Path(b.__file__).resolve().parents[1]
        self.before = {p: (self.source / "baseline" / p).read_bytes() for p in b.BASELINE_PINS}
        self.evidence = {p: (assets / "evidence" / p).read_bytes() for p in b.EVIDENCE_PINS}
        self.frozen = {p: (assets / "inputs" / p).read_bytes() for p in b.FROZEN_PINS}
        for path, raw in {**self.before, **self.frozen}.items():
            self.write(path, raw)
        self.git("init", "--quiet", "--template=", ".")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.filemode", "false")
        self.git("config", "index.version", "2")
        self.git("add", "--", *sorted({*self.before, *self.frozen}))
        tree = self.git("write-tree")
        self.base = self.git("commit-tree", tree, "-m", "authored ordinary baseline")
        self.git("update-ref", "--no-deref", "HEAD", self.base)
        self.after = b.build_g1b_acceptance_transition(self.before,
            b.build_completion_scope("2026-09-12T00:00:00+00:00", self.base))
        for path, raw in self.after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(b.TRANSITION_PATHS))
        candidate_tree = self.git("write-tree")
        self.q = dict(schema_version=b.BINDING_VERSION, operation_id="authored-g1b-acceptance",
            operation_kind="accept_journal", phase="development", base_commit=self.base, base_tree=tree,
            expected_head=self.base, expected_index_tree=candidate_tree, candidate_tree=candidate_tree,
            activation_commit=None, installed_controller=None,
            source_sha256={p: b._sha((self.source / p).read_bytes()) for p in b.SOURCE_PATHS},
            payload_sha256={p: b._sha((self.root / p).read_bytes()) for p in b.INPUT_PATHS})
        self.binding_path = self.home / "binding.json"

    def write(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def git(self, *args):
        env = b.trusted_git.closed_git_environment()
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="Synthetic", GIT_AUTHOR_EMAIL="test@invalid",
                   GIT_COMMITTER_NAME="Synthetic", GIT_COMMITTER_EMAIL="test@invalid")
        result = subprocess.run([str(b.trusted_git.resolve_stock_git()),
            *b.trusted_git.TRUSTED_GIT_COMMAND_OVERRIDES,
            "-c", "core.hooksPath=" + os.devnull, "-c", "gc.auto=0", "-c", "maintenance.auto=false", *args],
            cwd=self.root, env=env, capture_output=True, check=True, timeout=30)
        return result.stdout.decode().strip()

    def context(self):
        raw = b._canonical(self.q)
        self.binding_path.write_bytes(raw)
        return b.BoundedG1BContext(self.root, self.source, self.assets / "evidence",
                                  self.scratch, self.binding_path, b._sha(raw))

    def manifest(self, context):
        return {"schema_version": b.REQUEST_VERSION, "operation_id": self.q["operation_id"],
                "operation_kind": self.q["operation_kind"], "binding_sha256": context.expected_binding_sha256,
                "candidate_tree": self.q["candidate_tree"], "allowed_paths": sorted(b.operation_paths(self.q["operation_kind"])),
                "intended_side_effect_classes": ["repository_read"] if self.q["operation_kind"] == "assess_g1e" else sorted(b.EFFECTS)}

    def decision(self):
        context = self.context()
        return b.evaluate_bounded_g1b_operation(context=context, manifest=self.manifest(context),
            entrypoint="recovery_preflight", phase=self.q["phase"])

    def close(self):
        self.temporary.cleanup()


class SuccessorFixture(NativeFixture):
    """Native authored Git/index; only immutable component history is substituted.

    The accepted public commit cannot be recreated inside a tiny authored repo.
    Its literal commit/blob/ancestry observations are supplied explicitly below;
    all activation, candidate, predecessor, index and source checks use real Git.
    Production constants, pinned authority bytes and validators are unchanged.
    """
    def __init__(self, assets: Path, operation_kind="accept_g1b"):
        assert operation_kind in {"accept_g1b", "accept_g1c", "accept_g1d"}
        self.operation = b._operation(operation_kind)
        self.publication = self.operation["accepted_publication"]
        self.is_provenance = operation_kind == "accept_g1c"
        self.is_configuration = operation_kind == "accept_g1d"
        self.temporary = tempfile.TemporaryDirectory(prefix="g1c-contract-")
        self.home = Path(self.temporary.name)
        self.root = self.home / "target"
        self.root.mkdir()
        self.scratch = self.home / "index-scratch"
        self.scratch.mkdir()
        self.assets = assets
        self.source = Path(b.__file__).resolve().parents[1]
        self.before = {p: (self.source / self.operation["baseline_directory"] / p).read_bytes()
                       for p in self.operation["baseline_pins"]}
        self.evidence = {p: (assets / "evidence" / p).read_bytes() for p in self.operation["evidence_pins"]}
        frozen_paths = {*b.FROZEN_PINS, b.COST}
        if self.is_provenance or self.is_configuration:
            frozen_paths.update({b.SCOPE_PATH, *b.PROVENANCE_DEPENDENCY_PINS})
        if self.is_configuration:
            frozen_paths.update({b.G1C_SCOPE, *b.GOVERNOR_PINS, *b.CONFIGURATION_PATHS})

        def frozen_input(path):
            if self.is_configuration:
                if path == b.G1C_SCOPE:
                    return (self.source / "g1c-baseline" / path).read_bytes()
                if path in b.GOVERNOR_PINS:
                    return (self.source / "g1c-accepted-source" / path).read_bytes()
                if path in b.CONFIGURATION_PATHS:
                    return (assets / "configuration" / path).read_bytes()
            return (assets / "inputs" / path).read_bytes()

        self.frozen = {p: frozen_input(p) for p in frozen_paths}
        source_directory = "g1d-accepted-source" if self.is_configuration else "g1c-accepted-source" if self.is_provenance else "g1b-accepted-source"
        self.accepted_source = {p: (self.source / source_directory / p).read_bytes()
                                for p in self.operation["accepted_pins"]}
        initial_source, installed_source = {}, {}
        if self.is_configuration:
            installed_source = {p: (self.source / p).read_bytes() for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
            initial_source = {p: raw for p, raw in installed_source.items() if p not in b.CONTROLLER_PATHS}
            for p in ("orchestration_harness/bounded_g1b.py", "orchestration_harness/programme_admission.py", "tests/test_bounded_g1b.py"):
                initial_source[p] = (self.source.parent / "inputs" / p).read_bytes()
        initial = {**self.before, **self.frozen, **self.accepted_source, **initial_source}
        for path, raw in initial.items():
            self.write(path, raw)
        self.git("init", "--quiet", "--template=", ".")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.filemode", "false")
        self.git("config", "index.version", "2")
        self.git("add", "--", *sorted(initial))
        tree = self.git("write-tree")
        self.base = self.git("commit-tree", tree, "-m", "authored G1B component baseline")
        self.git("update-ref", "--no-deref", "HEAD", self.base)
        self.controller = None
        if self.is_configuration:
            parent = self.base
            for path in b.CONTROLLER_PATHS:
                self.write(path, installed_source[path])
            self.git("add", "--", *sorted(b.CONTROLLER_PATHS))
            tree = self.git("write-tree")
            self.base = self.git("commit-tree", tree, "-p", parent, "-m", "authored five-file controller installation")
            self.git("update-ref", "--no-deref", "HEAD", self.base, parent)
            self.controller = {"commit": self.base, "parent": parent, "tree": tree,
                               "source_sha256": {p: b._sha(installed_source[p]) for p in b.CONTROLLER_PATHS}}
            self.after = b.build_g1e_acceptance_transition(self.before,
                b.build_configuration_scope("2026-09-12T00:00:00+00:00", self.base, self.controller))
        else:
            transition = b.build_g1d_acceptance_transition if self.is_provenance else b.build_g1c_acceptance_transition
            scope = b.build_provenance_scope if self.is_provenance else b.build_governor_scope
            self.after = transition(self.before, scope("2026-09-12T00:00:00+00:00", self.base))
        for path, raw in self.after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(self.operation["transition_paths"]))
        candidate_tree = self.git("write-tree")
        self.q = dict(schema_version=b.BINDING_VERSION, operation_id="authored-g1c-acceptance",
            operation_kind=operation_kind, phase="development", base_commit=self.base, base_tree=tree,
            expected_head=self.base, expected_index_tree=candidate_tree, candidate_tree=candidate_tree,
            activation_commit=None, installed_controller=copy.deepcopy(self.controller),
            source_sha256={p: b._sha((self.source / p).read_bytes()) for p in b.SOURCE_PATHS},
            payload_sha256={p: b._sha((self.root / p).read_bytes()) for p in self.operation["input_paths"]})
        self.binding_path = self.home / "binding.json"
        self.component_header = ("tree " + self.publication["tree"] + "\nparent "
                                 + self.publication["parent"] + "\n\nauthored observation\n")
        self.component_ancestry_error = None

    @contextmanager
    def component_history(self):
        run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
        accepted = self.publication["commit"]

        def observed_text(root, *args, **kwargs):
            if root == self.root and args == ("cat-file", "commit", accepted):
                return self.component_header
            if root == self.root and args == ("merge-base", "--is-ancestor", accepted, self.q["base_commit"]):
                if self.component_ancestry_error:
                    raise b.trusted_git.TrustedGitError(self.component_ancestry_error)
                return ""
            return run(root, *args, **kwargs)

        def observed_bytes(root, *args, **kwargs):
            for path, raw in self.accepted_source.items():
                if root == self.root and args == ("cat-file", "blob", accepted + ":" + path):
                    return raw
            return run_bytes(root, *args, **kwargs)

        with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
            yield

    def activate(self):
        commit = self.git("commit-tree", self.q["candidate_tree"], "-p", self.base, "-m", "authored activate G1C")
        self.git("update-ref", "--no-deref", "HEAD", commit, self.base)
        self.q.update(phase="pre-push", expected_head=commit)
        return commit

    def prepare_implementation(self, activation):
        assert not self.is_configuration, "installed G1E component is assessed, not republished"
        kind = "implement_g1d" if self.is_provenance else "implement_g1c"
        self.q.update(operation_kind=kind, phase="development", base_commit=activation,
                      base_tree=self.q["candidate_tree"], activation_commit=activation)
        for path in b.operation_paths(kind):
            self.write(path, b"authored candidate; deliberately not importable Python\n")
        self.git("add", "--", *sorted(b.operation_paths(kind)))
        tree = self.git("write-tree")
        self.q.update(candidate_tree=tree, expected_index_tree=tree)

    def prepare_assessment(self, activation):
        assert self.is_configuration
        self.q.update(operation_kind="assess_g1e", phase="assessment", base_commit=activation,
                      base_tree=self.q["candidate_tree"], expected_head=activation,
                      expected_index_tree=self.q["candidate_tree"], activation_commit=activation)


def build_integration_suite(assets: Path) -> unittest.TestSuite:
    """Explicit external fixture input; never discover a live/historical checkout."""
    class IntegratedTests(unittest.TestCase):
        def setUp(self):
            self.fx = NativeFixture(assets)
            self.addCleanup(self.fx.close)

        def test_real_callers_and_loader_compose_without_legacy_observations(self):
            f = self.fx
            context = f.context()
            with no_legacy_observation():
                inputs = pa.load_programme_policy(f.root, bounded_context=context)
                self.assertIs(type(inputs), b.BoundedG1BInputs)
                manifest = pf.build_task_manifest(f.root, bounded_context=context)
                self.assertEqual(manifest, f.manifest(context))
                report = pf.build_report(f.root, manifest, bounded_context=context)
                self.assertEqual(report["status"], "policy_eligible")
                self.assertFalse(report["execution_authorized"])
                for decision in (
                    pa.evaluate_programme_operation_admission(repo_root=f.root, manifest=manifest,
                        entrypoint="task_branch_commit", phase="development", bounded_context=context),
                    pg.evaluate_pinned_programme_operation(gatekeeper_root=f.source, target_repo_root=f.root,
                        manifest=manifest, entrypoint="task_branch_commit", phase="development", bounded_context=context),
                ):
                    self.assertTrue(decision.policy_admitted, decision.reason_codes)
                    self.assertEqual(decision.candidate_tree, f.q["candidate_tree"])
                    self.assertFalse(decision.execution_authorized)
                with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa.load_programme_policy(f.root)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")
                legacy = pg.evaluate_pinned_programme_operation(gatekeeper_root=f.source,
                    target_repo_root=f.root, manifest=None, entrypoint="task_branch_commit", phase="development")
                self.assertFalse(legacy.admitted)
                self.assertIn("bounded_g1b_context_required", legacy.reason_codes)

        def test_changed_source_and_drift_during_observation_rejected(self):
            f = self.fx
            path = "orchestration_harness/bounded_g1b.py"
            old = f.q["source_sha256"][path]
            f.q["source_sha256"][path] = "0" * 64
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_input_digest_changed",))
            f.q["source_sha256"][path] = old
            attest = b.trusted_git.attest_target_index

            def drift(*args, **kwargs):
                result = attest(*args, **kwargs)
                f.write(b.AGENTS, f.after[b.AGENTS] + b"\n")
                return result

            with patch.object(b.trusted_git, "attest_target_index", side_effect=drift):
                self.assertEqual(f.decision().reason_codes, ("bounded_g1b_snapshot_drift",))

        def test_damaged_completion_state_stays_out_of_legacy_loader(self):
            f = self.fx
            state = b._json(f.after[b.STATE])
            for profile in (None, "G1B_COMPLETION_TYPO", b.OLD_PROFILE):
                changed = {**state, "active_profile": profile}
                f.write(b.STATE, b._canonical(changed))
                with self.subTest(profile=profile), no_legacy_observation():
                    report = pf.build_report(f.root)
                    self.assertEqual(report["status"], "blocked")
                    result = pg.evaluate_pinned_programme_operation(gatekeeper_root=f.source,
                        target_repo_root=f.root, manifest=None, entrypoint="task_branch_commit", phase="development")
                    self.assertFalse(result.admitted)
            # Missing/misspelled profiles in an otherwise historical-shaped input
            # are also rejected before any broad observation.
            state = b._json(f.before[b.STATE])
            (f.root / b.SCOPE_PATH).unlink()
            for profile in (None, "UNKNOWN"):
                f.write(b.STATE, b._canonical({**state, "active_profile": profile}))
                with no_legacy_observation(), self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa.load_programme_policy(f.root)
                self.assertEqual(caught.exception.reason_code, "programme_state_missing_or_invalid")

        def test_exact_transition_preserves_history_and_current_safeguards(self):
            f = self.fx
            b.validate_g1b_acceptance_transition(f.before, f.after, f.evidence)
            old, new = (b._json(raw) for raw in (f.before[b.STATE], f.after[b.STATE]))
            self.assertEqual(new["g1b"]["state_transition"], old["g1b"]["state_transition"])
            self.assertEqual(new["g1b"]["subgates"]["G1B.2"]["state_transition"],
                             old["g1b"]["subgates"]["G1B.2"]["state_transition"])
            self.assertEqual(new["actions_performed"], old["actions_performed"])
            pa._validate_precedence(b._document(f.frozen[b.PROJECT], b.PROJECT),
                b._document(f.frozen[b.CONTINUATION], b.CONTINUATION), f.after[b.AGENTS].decode(), new)
            for counter, value in new["actions_performed"].items():
                if type(value) is not int:
                    continue
                changed = copy.deepcopy(new)
                changed["actions_performed"][counter] = 1
                with self.subTest(counter=counter), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1b_acceptance_transition(f.before,
                        {**f.after, b.STATE: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_authority_delta_invalid")
            for name, value in (("feature_work_eligible", True), ("product_work_eligible", True),
                                ("current_gate", "G1C")):
                changed = {**new, name: value}
                with self.subTest(name=name), self.assertRaises(b.BoundedG1BError):
                    b.validate_g1b_acceptance_transition(f.before,
                        {**f.after, b.STATE: b._canonical(changed)}, f.evidence)

        def test_transition_rejects_changed_predecessor_review_and_scope(self):
            f = self.fx
            with self.assertRaises(b.BoundedG1BError) as caught:
                b.build_g1b_acceptance_transition({**f.before, b.AGENTS: b"changed"}, b._json(f.after[b.SCOPE_PATH]))
            self.assertEqual(caught.exception.reason_code, "bounded_g1b_predecessor_changed")
            for path in b.EVIDENCE_PINS:
                with self.subTest(path=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1b_acceptance_transition(f.before, f.after, {**f.evidence, path: b"changed"})
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_evidence_changed")
            for key, value in (("g1b_complete", True), ("g1c_eligible", 0),
                               ("feature_work_eligible", True), ("criteria", []),
                               ("publication", {"commit": "0" * 40})):
                changed = {**b._json(f.after[b.SCOPE_PATH]), key: value}
                with self.subTest(key=key), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1b_acceptance_transition(f.before,
                        {**f.after, b.SCOPE_PATH: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_acceptance_scope_invalid")

        def test_binding_input_and_index_drift_rejected(self):
            f = self.fx
            context = f.context()
            f.binding_path.write_bytes(b"{}")
            result = b.evaluate_bounded_g1b_operation(context=context, manifest=f.manifest(context),
                entrypoint="recovery_preflight", phase="development")
            self.assertEqual(result.reason_codes, ("bounded_g1b_input_digest_changed",))
            path = next(iter(b.KERNEL_PINS))
            f.write(path, f.frozen[path] + b"\n")
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_input_digest_changed",))
            f.write(path, f.frozen[path])
            f.q["expected_index_tree"] = f.q["base_tree"]
            self.assertEqual(f.decision().reason_codes, ("trusted_git_expected_index_tree_mismatch",))

        def test_manifest_effect_phase_and_caller_mismatch_rejected(self):
            f = self.fx
            context = f.context()
            manifest = f.manifest(context)
            with no_legacy_observation():
                for changed in ({**manifest, "intended_side_effect_classes": ["provider_invocation"]},
                                {**manifest, "candidate_tree": "0" * 40},
                                {**manifest, "allowed_paths": ["outside.py"]}):
                    with self.subTest(changed=changed):
                        result = b.evaluate_bounded_g1b_operation(context=context, manifest=changed,
                            entrypoint="recovery_preflight", phase="development")
                        self.assertEqual(result.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
                result = b.evaluate_bounded_g1b_operation(context=context, manifest=manifest,
                    entrypoint="task_branch_push", phase="development")
                self.assertEqual(result.reason_codes, ("bounded_g1b_push_phase",))
                result = pg.evaluate_pinned_programme_operation(gatekeeper_root=f.source,
                    target_repo_root=f.home / "different", manifest=manifest,
                    entrypoint="task_branch_commit", phase="development", bounded_context=context)
                self.assertEqual(result.reason_codes, ("bounded_g1b_caller_target_mismatch",))

        def test_actual_predecessor_and_missing_committed_activation_rejected(self):
            f = self.fx
            # A different real Git parent, despite a valid external baseline.
            f.git("read-tree", f.q["base_tree"])
            f.write(b.AGENTS, f.before[b.AGENTS] + b"\n")
            f.git("add", "--", b.AGENTS)
            tree = f.git("write-tree")
            other = f.git("commit-tree", tree, "-m", "wrong predecessor")
            f.git("update-ref", "--no-deref", "HEAD", other, f.base)
            f.q.update(base_commit=other, base_tree=tree, expected_head=other)
            f.after = b.build_g1b_acceptance_transition(f.before,
                b.build_completion_scope("2026-09-12T00:00:00+00:00", other))
            for path, raw in f.after.items():
                f.write(path, raw)
                f.q["payload_sha256"][path] = b._sha(raw)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_actual_predecessor_changed",))
            f.q.update(operation_kind="complete_g1b", activation_commit=None)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_binding_required",))

        def test_committed_activation_allows_completion_without_accepting_g1b(self):
            f = self.fx
            commit = f.git("commit-tree", f.q["candidate_tree"], "-p", f.base, "-m", "activate")
            f.git("update-ref", "--no-deref", "HEAD", commit, f.base)
            f.q.update(phase="pre-push", expected_head=commit)
            self.assertTrue(f.decision().policy_admitted)
            f.q.update(operation_kind="complete_g1b", phase="development", base_commit=commit,
                       base_tree=f.q["candidate_tree"], activation_commit=commit)
            result = f.decision()
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertFalse(result.execution_authorized)
            scope = b._json(f.after[b.SCOPE_PATH])
            self.assertFalse(scope["g1b_complete"])
            self.assertFalse(scope["g1c_eligible"])

    class SuccessorTests(unittest.TestCase):
        def setUp(self):
            self.fx = SuccessorFixture(assets)
            self.addCleanup(self.fx.close)
            self.enterContext(self.fx.component_history())
            self.enterContext(no_legacy_observation())

        def test_actual_callers_report_g1c_and_validate_its_actual_preamble(self):
            f = self.fx
            context = f.context()
            inputs = pa.load_programme_policy(f.root, bounded_context=context)
            self.assertIs(type(inputs), b.BoundedG1BInputs)
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            self.assertEqual(manifest, f.manifest(context))
            report = pf.build_report(f.root, manifest, bounded_context=context)
            self.assertEqual(report["status"], "policy_eligible")
            self.assertEqual(report["active_profile"], b.G1C_PROFILE)
            self.assertEqual(report["current_gate"], "G1C")
            self.assertFalse(report["execution_authorized"])
            self.assertIn("G1B component acceptance awaits reviewed transition publication", report["claim_limits"])
            for decision in (
                pa.evaluate_programme_operation_admission(repo_root=f.root, manifest=manifest,
                    entrypoint="task_branch_commit", phase="development", bounded_context=context),
                pg.evaluate_pinned_programme_operation(gatekeeper_root=f.source, target_repo_root=f.root,
                    manifest=manifest, entrypoint="task_branch_commit", phase="development", bounded_context=context),
            ):
                self.assertTrue(decision.policy_admitted, decision.reason_codes)
                self.assertFalse(decision.execution_authorized)
            state = b._json(f.after[b.STATE])
            for preamble in (b.NEW_PREAMBLE, b.OLD_PREAMBLE, "unrecognised"):
                wrong = f.after[b.AGENTS].decode().replace(b.G1C_PREAMBLE, preamble, 1)
                with self.subTest(preamble=preamble), self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa._validate_precedence(b._document(f.frozen[b.PROJECT], b.PROJECT),
                        b._document(f.frozen[b.CONTINUATION], b.CONTINUATION), wrong, state)
                self.assertEqual(caught.exception.reason_code, "agents_recovery_precedence_missing")

        def test_transition_preserves_old_operation_history_and_all_current_stops(self):
            f = self.fx
            b.validate_g1c_acceptance_transition(f.before, f.after, f.evidence)
            old, new = (b._json(raw) for raw in (f.before[b.STATE], f.after[b.STATE]))
            self.assertEqual(new["g1b"]["completion"], old["g1b"]["completion"])
            self.assertEqual(new["g1b"]["subgates"], old["g1b"]["subgates"])
            self.assertEqual(new["actions_performed"], old["actions_performed"])
            self.assertEqual(new["global_checks"], old["global_checks"])
            self.assertEqual((f.root / b.SCOPE_PATH).read_bytes(), f.before[b.SCOPE_PATH])
            self.assertEqual((f.root / b.LATCH).read_bytes(), f.frozen[b.LATCH])
            scope = b._json(f.after[b.G1C_SCOPE])
            self.assertEqual(scope["current_operation"]["supersedes"]["scope_sha256"], b._sha(f.before[b.SCOPE_PATH]))
            self.assertFalse(scope["g1c_complete"])
            self.assertFalse(scope["g1d_eligible"])
            for counter, value in new["actions_performed"].items():
                if type(value) is not int:
                    continue
                changed = copy.deepcopy(new)
                changed["actions_performed"][counter] = value + 1
                with self.subTest(counter=counter), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1c_acceptance_transition(f.before,
                        {**f.after, b.STATE: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1c_authority_delta_invalid")
            for path in (b.STATE, b.GATES, b.OVERLAY):
                changed = b._document(f.after[path], path)
                changed["unreviewed_permission"] = True
                with self.subTest(path=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1c_acceptance_transition(f.before, {**f.after, path: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1c_authority_delta_invalid")

        def test_changed_acceptance_evidence_and_predecessor_rejected(self):
            f = self.fx
            for path in b.G1B_EVIDENCE_PINS:
                with self.subTest(evidence=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1c_acceptance_transition(f.before, f.after, {**f.evidence, path: b"changed"})
                self.assertEqual(caught.exception.reason_code, "bounded_g1c_evidence_changed")
            for path in b.G1B_BASELINE_PINS:
                with self.subTest(predecessor=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g1c_acceptance_transition({**f.before, path: f.before[path] + b"\n"},
                                                      b._json(f.after[b.G1C_SCOPE]))
                self.assertEqual(caught.exception.reason_code, "bounded_g1c_predecessor_changed")

        def test_scope_cannot_activate_product_automatic_migration_or_dollar_policy(self):
            f = self.fx
            scope = b._json(f.after[b.G1C_SCOPE])
            for key, value in (("g1c_complete", True), ("g1d_eligible", True), ("feature_work_eligible", True),
                               ("existing_clockwork_writers_activated", True), ("automatic_v1_migration_permitted", True),
                               ("implementation_paths", sorted(b.GOVERNOR_PATHS | b.TRANSITION_PATHS)),
                               ("allowed_effects", ["provider_invocation"])):
                changed = {**scope, key: value}
                with self.subTest(key=key), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1c_acceptance_transition(f.before,
                        {**f.after, b.G1C_SCOPE: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1c_scope_invalid")
            for key, value in (("monetary_budget_enforcement", "active"), ("estimated_cost_reporting", "binding"),
                               ("estimated_cost_or_local_cap_triggers_fallback", True), ("global_defaults_changed", True)):
                changed = copy.deepcopy(scope)
                changed["budget_semantics"][key] = value
                with self.subTest(key=key), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g1c_acceptance_transition(f.before, changed)
                self.assertEqual(caught.exception.reason_code, "bounded_g1c_scope_invalid")
            # Even a caller-bound digest cannot authorise changed global policy or historical scope.
            for path, raw in ((b.COST, f.frozen[b.COST]), (b.SCOPE_PATH, f.before[b.SCOPE_PATH])):
                f.write(path, raw + b"\n")
                f.q["payload_sha256"][path] = b._sha(raw + b"\n")
                self.assertEqual(f.decision().reason_codes, ("bounded_g1b_frozen_input_changed",))
                f.write(path, raw)
                f.q["payload_sha256"][path] = b._sha(raw)

        def test_accepted_component_commit_tree_ancestry_and_source_are_checked(self):
            f = self.fx
            correct = f.component_header
            for wrong in (correct.replace(b.PERSISTENCE_PUBLICATION["parent"], "0" * 40),
                          correct.replace(b.PERSISTENCE_PUBLICATION["tree"], "0" * 40),
                          correct.replace("\n\n", "\nparent " + "1" * 40 + "\n\n")):
                f.component_header = wrong
                self.assertEqual(f.decision().reason_codes, ("bounded_g1c_component_publication_invalid",))
            f.component_header = correct
            f.component_ancestry_error = "trusted_git_command_failed"
            self.assertEqual(f.decision().reason_codes, ("trusted_git_command_failed",))
            f.component_ancestry_error = None
            for path, raw in list(f.accepted_source.items()):
                f.accepted_source[path] = raw + b"\n"
                self.assertEqual(f.decision().reason_codes, ("bounded_g1c_accepted_component_changed",))
                f.accepted_source[path] = raw
            self.assertTrue(f.decision().policy_admitted)

        def test_native_activation_then_versioned_implementation_remains_unaccepted(self):
            f = self.fx
            activation = f.activate()
            self.assertTrue(f.decision().policy_admitted)
            f.prepare_implementation(activation)
            result = f.decision()
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertFalse(result.execution_authorized)
            self.assertIn("G1B component accepted", result.claim_limits)
            self.assertEqual(b.operation_paths(f.q["operation_kind"]), b.GOVERNOR_PATHS)
            self.assertNotEqual(b._sha((f.root / "orchestration_harness/clockwork_persistence.py").read_bytes()),
                                b.PERSISTENCE_PINS["orchestration_harness/clockwork_persistence.py"])
            self.assertFalse(b._json(f.after[b.G1C_SCOPE])["g1c_complete"])
            f.q["activation_commit"] = None
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_binding_required",))
            f.q["activation_commit"] = f.base
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_parent_invalid",))

        def test_current_descendant_authority_cannot_drift_after_activation(self):
            f = self.fx
            activation = f.activate()
            f.prepare_implementation(activation)
            f.write(b.AGENTS, f.after[b.AGENTS] + b"\n")
            f.git("add", "--", b.AGENTS)
            tree = f.git("write-tree")
            descendant = f.git("commit-tree", tree, "-p", activation, "-m", "unaccepted authority drift")
            f.git("update-ref", "--no-deref", "HEAD", descendant, activation)
            f.write(b.AGENTS, f.after[b.AGENTS])
            f.q.update(base_commit=descendant, base_tree=tree, expected_head=descendant)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_not_committed",))

        def test_native_predecessor_and_transition_base_cannot_be_substituted(self):
            f = self.fx
            changed = b.build_g1c_acceptance_transition(f.before,
                b.build_governor_scope("2026-09-12T00:00:00+00:00", "0" * 40))
            for path, raw in changed.items():
                f.write(path, raw)
                f.q["payload_sha256"][path] = b._sha(raw)
            f.git("add", "--", *sorted(b.G1C_TRANSITION_PATHS))
            tree = f.git("write-tree")
            f.q.update(candidate_tree=tree, expected_index_tree=tree)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_transition_base_mismatch",))
            f.git("read-tree", f.q["base_tree"])
            f.write(b.AGENTS, f.before[b.AGENTS] + b"\n")
            f.git("add", "--", b.AGENTS)
            wrong_tree = f.git("write-tree")
            other = f.git("commit-tree", wrong_tree, "-m", "changed actual predecessor")
            f.git("update-ref", "--no-deref", "HEAD", other, f.base)
            f.write(b.AGENTS, changed[b.AGENTS])
            f.q.update(base_commit=other, base_tree=wrong_tree, expected_head=other)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_actual_predecessor_changed",))

        def test_legacy_routes_fail_closed_with_each_g1c_marker_or_scope_alone(self):
            f = self.fx
            historical = b._json((f.source / "baseline" / b.STATE).read_bytes())
            (f.root / b.SCOPE_PATH).unlink()
            (f.root / b.G1C_SCOPE).unlink()
            variants = []
            for key, value in (("active_profile", b.G1C_PROFILE), ("current_gate", "G1C"), ("g1c", None)):
                variants.append({**historical, key: value})
            variant = copy.deepcopy(historical)
            variant["g1b"]["acceptance"] = {}
            variants.append(variant)
            variant = copy.deepcopy(historical)
            variant["task_selection"]["allowed_task_kinds"] = [b.G1C_TASK]
            variants.append(variant)
            for state in variants:
                f.write(b.STATE, b._canonical(state))
                with self.subTest(state=state.get("active_profile")), self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa.load_programme_policy(f.root)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")
                self.assertEqual(pf.build_report(f.root)["status"], "blocked")
            f.write(b.STATE, b._canonical(historical))
            f.write(b.G1C_SCOPE, b"malformed scope still marks the closed route")
            with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                pa.load_programme_policy(f.root)
            self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")

        def test_unknown_operation_and_combined_publication_scope_are_rejected(self):
            f = self.fx
            context = f.context()
            manifest = f.manifest(context)
            combined = {**manifest, "allowed_paths": sorted(b.G1C_TRANSITION_PATHS | b.GOVERNOR_PATHS)}
            result = b.evaluate_bounded_g1b_operation(context=context, manifest=combined,
                entrypoint="task_branch_commit", phase="development")
            self.assertEqual(result.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
            for kind in ("complete_g1c", "anything", None, []):
                f.q["operation_kind"] = kind
                context = f.context()
                result = b.evaluate_bounded_g1b_operation(context=context, manifest=manifest,
                    entrypoint="task_branch_commit", phase="development")
                self.assertEqual(result.reason_codes, ("bounded_g1b_operation_kind",))

    class ProvenanceAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = SuccessorFixture(assets, "accept_g1c")
            self.addCleanup(self.fx.close)
            self.enterContext(self.fx.component_history())
            self.enterContext(no_legacy_observation())

        def test_native_transition_and_implementation_keep_acceptance_separate(self):
            f = self.fx
            result = f.decision()
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertFalse(result.execution_authorized)
            self.assertEqual((result.current_gate, result.active_profile), ("G1D", b.G1D_PROFILE))
            activation = f.activate()
            self.assertTrue(f.decision().policy_admitted)
            f.prepare_implementation(activation)
            result = f.decision()
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertFalse(result.execution_authorized)
            self.assertIn("G1C component accepted", result.claim_limits)
            self.assertEqual(b.operation_paths(f.q["operation_kind"]), b.PROVENANCE_PATHS)
            scope = b._json(f.after[b.G1D_SCOPE])
            self.assertFalse(scope["g1d_complete"])
            self.assertFalse(scope["g1e_eligible"])
            self.assertFalse(scope["operational_multi_task_control_accepted"])
            f.q["activation_commit"] = None
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_binding_required",))

        def test_historical_scopes_counters_and_global_closures_are_preserved(self):
            f = self.fx
            old, new = b._json(f.before[b.STATE]), b._json(f.after[b.STATE])
            self.assertEqual(new["g1b"], old["g1b"])
            self.assertEqual(new["g1c"]["current_operation"], old["g1c"]["current_operation"])
            self.assertEqual(new["actions_performed"], old["actions_performed"])
            self.assertEqual(new["global_checks"], old["global_checks"])
            for path, expected in ((b.G1C_SCOPE, f.before[b.G1C_SCOPE]),
                                    (b.SCOPE_PATH, f.frozen[b.SCOPE_PATH]), (b.LATCH, f.frozen[b.LATCH])):
                self.assertEqual((f.root / path).read_bytes(), expected)
            for counter, value in new["actions_performed"].items():
                if type(value) is not int:
                    continue
                changed = copy.deepcopy(new)
                changed["actions_performed"][counter] = value + 1
                with self.subTest(counter=counter), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1d_acceptance_transition(f.before, {**f.after, b.STATE: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1d_authority_delta_invalid")
            for path in (b.STATE, b.GATES, b.OVERLAY):
                changed = b._document(f.after[path], path)
                changed["unreviewed_permission"] = True
                with self.subTest(path=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1d_acceptance_transition(f.before, {**f.after, path: b._canonical(changed)}, f.evidence)
                self.assertEqual(caught.exception.reason_code, "bounded_g1d_authority_delta_invalid")

        def test_each_acceptance_evidence_and_predecessor_is_authenticated(self):
            f = self.fx
            for path in b.G1C_EVIDENCE_PINS:
                with self.subTest(evidence=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1d_acceptance_transition(f.before, f.after, {**f.evidence, path: b"changed"})
                self.assertEqual(caught.exception.reason_code, "bounded_g1d_evidence_changed")
            for path in b.G1C_BASELINE_PINS:
                with self.subTest(predecessor=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g1d_acceptance_transition({**f.before, path: f.before[path] + b"\n"},
                                                      b._json(f.after[b.G1D_SCOPE]))
                self.assertEqual(caught.exception.reason_code, "bounded_g1d_predecessor_changed")

        def test_scope_rejects_effect_expansion_and_declared_independence(self):
            f = self.fx
            scope = b._json(f.after[b.G1D_SCOPE])
            for key, value in (("g1d_complete", True), ("g1e_eligible", True), ("feature_work_eligible", True),
                               ("operational_multi_task_control_accepted", True),
                               ("existing_clockwork_writers_activated", True),
                               ("implementation_paths", sorted(b.PROVENANCE_PATHS | b.GOVERNOR_PATHS)),
                               ("allowed_effects", ["provider_invocation"])):
                with self.subTest(key=key), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g1d_acceptance_transition(f.before, {**scope, key: value})
                self.assertEqual(caught.exception.reason_code, "bounded_g1d_scope_invalid")
            for key, value in (("execution_profile", "live_models"), ("live_model_context_accepted", True),
                               ("worker_declarations_establish_independence", True),
                               ("control_and_publication_risk_floor", "routine_delta"),
                               ("replay_grants_execution_integration_or_usage_settlement_authority", True),
                               ("global_policy_and_existing_execution_defaults_changed", True)):
                changed = copy.deepcopy(scope)
                changed["verification_boundary"][key] = value
                with self.subTest(key=key), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g1d_acceptance_transition(f.before, changed)
                self.assertEqual(caught.exception.reason_code, "bounded_g1d_scope_invalid")

        def test_governor_publication_history_and_preserved_inputs_are_checked(self):
            f = self.fx
            correct = f.component_header
            for wrong in (correct.replace(b.GOVERNOR_PUBLICATION["parent"], "0" * 40),
                          correct.replace(b.GOVERNOR_PUBLICATION["tree"], "0" * 40),
                          correct.replace("\n\n", "\nparent " + "1" * 40 + "\n\n")):
                f.component_header = wrong
                self.assertEqual(f.decision().reason_codes, ("bounded_g1d_component_publication_invalid",))
            f.component_header = correct
            f.component_ancestry_error = "trusted_git_command_failed"
            self.assertEqual(f.decision().reason_codes, ("trusted_git_command_failed",))
            f.component_ancestry_error = None
            for path, raw in list(f.accepted_source.items()):
                f.accepted_source[path] = raw + b"\n"
                self.assertEqual(f.decision().reason_codes, ("bounded_g1d_accepted_component_changed",))
                f.accepted_source[path] = raw
            pins = {b.G1C_SCOPE: b.G1C_BASELINE_PINS[b.G1C_SCOPE], **b.GOVERNOR_PINS,
                    **b.PROVENANCE_DEPENDENCY_PINS, b.COST: b.COST_PIN}
            for path in pins:
                raw = (f.root / path).read_bytes()
                f.write(path, raw + b"\n")
                f.q["payload_sha256"][path] = b._sha(raw + b"\n")
                with self.subTest(path=path):
                    self.assertEqual(f.decision().reason_codes, ("bounded_g1b_frozen_input_changed",))
                f.write(path, raw)
                f.q["payload_sha256"][path] = b._sha(raw)
            self.assertTrue(f.decision().policy_admitted)

        def test_native_activation_and_current_authority_cannot_be_substituted(self):
            f = self.fx
            activation = f.activate()
            f.prepare_implementation(activation)
            f.q["activation_commit"] = f.base
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_parent_invalid",))
            f.q["activation_commit"] = activation
            f.write(b.AGENTS, f.after[b.AGENTS] + b"\n")
            f.git("add", "--", b.AGENTS)
            tree = f.git("write-tree")
            descendant = f.git("commit-tree", tree, "-p", activation, "-m", "unaccepted authority drift")
            f.git("update-ref", "--no-deref", "HEAD", descendant, activation)
            f.write(b.AGENTS, f.after[b.AGENTS])
            f.q.update(base_commit=descendant, base_tree=tree, expected_head=descendant)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_activation_not_committed",))

        def test_legacy_loader_rejects_each_g1d_marker_before_observation(self):
            f = self.fx
            historical = b._json((f.source / "baseline" / b.STATE).read_bytes())
            self.assertFalse((f.root / b.G1E_SCOPE).exists())
            for path in (b.SCOPE_PATH, b.G1C_SCOPE, b.G1D_SCOPE):
                (f.root / path).unlink()
            variants = [{**historical, key: value} for key, value in
                        (("active_profile", b.G1D_PROFILE), ("current_gate", "G1D"), ("g1d", None))]
            task = copy.deepcopy(historical)
            task["task_selection"]["allowed_task_kinds"] = [b.G1D_TASK]
            variants.append(task)
            for state in variants:
                f.write(b.STATE, b._canonical(state))
                with self.subTest(state=state.get("current_gate")), self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa.load_programme_policy(f.root)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")
                self.assertEqual(pf.build_report(f.root)["status"], "blocked")
            f.write(b.STATE, b._canonical(historical))
            f.write(b.G1D_SCOPE, b"malformed scope still closes legacy route")
            with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                pa.load_programme_policy(f.root)
            self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")

        def test_combined_scope_unknown_operations_and_transition_base_reject(self):
            f = self.fx
            context = f.context()
            manifest = f.manifest(context)
            result = b.evaluate_bounded_g1b_operation(context=context,
                manifest={**manifest, "allowed_paths": sorted(b.G1D_TRANSITION_PATHS | b.PROVENANCE_PATHS)},
                entrypoint="task_branch_commit", phase="development")
            self.assertEqual(result.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
            for kind in ("accept_g1e", "implement_g1e", None, []):
                f.q["operation_kind"] = kind
                result = b.evaluate_bounded_g1b_operation(context=f.context(), manifest=manifest,
                    entrypoint="task_branch_commit", phase="development")
                self.assertEqual(result.reason_codes, ("bounded_g1b_operation_kind",))
            f.q["operation_kind"] = "accept_g1c"
            changed = b.build_g1d_acceptance_transition(f.before,
                b.build_provenance_scope("2026-09-12T00:00:00+00:00", "0" * 40))
            for path, raw in changed.items():
                f.write(path, raw)
                f.q["payload_sha256"][path] = b._sha(raw)
            f.git("add", "--", *sorted(b.G1D_TRANSITION_PATHS))
            tree = f.git("write-tree")
            f.q.update(candidate_tree=tree, expected_index_tree=tree)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_transition_base_mismatch",))

    class ConfigurationTests(unittest.TestCase):
        def setUp(self):
            self.source = Path(b.__file__).resolve().parents[1]
            self.documents = {Path(p).name: (assets / "configuration" / p).read_bytes() for p in b.CONFIGURATION_PATHS}
            self.expected = {name: b._sha(raw) for name, raw in self.documents.items()}
            self.state = b._json((self.source / "g1d-baseline" / b.STATE).read_bytes())
            self.agents = (self.source / "g1d-baseline" / b.AGENTS).read_text()

        def validate(self):
            return rp.validate_recovery_configuration(documents=self.documents, expected_sha256=self.expected,
                                                     agents_text=self.agents, state=self.state)

        def mutate(self, name, fields, value):
            document = core.decode(self.documents[name], "yaml")
            target = document
            for field in fields[:-1]:
                target = target[field]
            target[fields[-1]] = value
            self.documents[name] = b._canonical(document)
            self.expected[name] = b._sha(self.documents[name])

        def test_actual_ten_policy_closure_is_pure_and_canonical(self):
            with patch.object(builtins, "open", side_effect=AssertionError("configuration observed filesystem")), \
                    patch.object(os, "listdir", side_effect=AssertionError("configuration discovered files")), \
                    patch.object(os, "scandir", side_effect=AssertionError("configuration discovered files")), \
                    patch.object(subprocess, "Popen", side_effect=AssertionError("configuration started process")):
                snapshot = self.validate()
            self.assertEqual(len(snapshot.documents), 10)
            self.assertEqual(dict(snapshot.source_sha256), self.expected)
            self.assertFalse(hasattr(snapshot, "execution_authorized"))
            reversed_documents = dict(reversed(list(self.documents.items())))
            equivalent = rp.validate_recovery_configuration(documents=reversed_documents, expected_sha256=self.expected,
                                                            agents_text=self.agents, state=self.state)
            self.assertEqual(snapshot, equivalent)

        def test_every_policy_is_required_and_exact_bytes_are_bound(self):
            self.validate()
            for name in tuple(self.documents):
                original = self.documents.pop(name)
                with self.subTest(missing=name), self.assertRaises(core.ConfigurationError) as caught:
                    self.validate()
                self.assertEqual(caught.exception.reason_code, "configuration_document_set")
                self.documents[name] = original + b"\n"
                with self.subTest(changed=name), self.assertRaises(core.ConfigurationError) as caught:
                    self.validate()
                self.assertEqual(caught.exception.reason_code, "configuration_document_changed")
                self.documents[name] = original

        def test_extra_documents_aliases_and_unregistered_fields_reject(self):
            self.validate()
            for name in ("extra.yaml", "./project.yaml", "PROJECT.yaml", "nested/project.yaml", "nested\\project.yaml"):
                self.documents[name] = self.documents["project.yaml"]
                self.expected[name] = b._sha(self.documents[name])
                with self.subTest(name=name), self.assertRaises(core.ConfigurationError) as caught:
                    self.validate()
                self.assertEqual(caught.exception.reason_code, "configuration_document_set")
                del self.documents[name], self.expected[name]
            self.mutate("project.yaml", ("unexpected_policy_file",), "unseen.yaml")
            with self.assertRaises(core.ConfigurationError) as caught:
                self.validate()
            self.assertEqual(caught.exception.reason_code, "configuration_schema_invalid")

        def test_every_declared_reference_is_checked_without_following_it(self):
            self.validate()
            originals, original_pins = dict(self.documents), dict(self.expected)
            for reference in rp.POLICY_REFERENCES:
                for target in ("missing.yaml", "../project.yaml", "security_review_protocol.yaml"
                               if reference.target != "security_review_protocol.yaml" else "project.yaml"):
                    self.documents, self.expected = dict(originals), dict(original_pins)
                    self.mutate(reference.source, reference.fields, target)
                    with self.subTest(source=reference.source, fields=reference.fields, target=target), \
                            self.assertRaises(core.ConfigurationError) as caught:
                        self.validate()
                    self.assertEqual(caught.exception.reason_code, "configuration_reference_invalid")

        def test_nested_shapes_and_authority_values_are_validated_after_rebinding(self):
            self.validate()
            originals, original_pins = dict(self.documents), dict(self.expected)
            cases = (
                ("project.yaml", ("master_authority", "conductor_can_commit"), 1, "configuration_schema_invalid"),
                ("project.yaml", ("master_authority", "conductor_can_commit"), True, "configuration_recovery_semantics_invalid"),
                ("operating_model.yaml", ("verifier", "deterministic_failure_action"), "continue", "configuration_recovery_semantics_invalid"),
                ("verifier_execution_policy.yaml", ("external_verifier", "decision_contract", "exact_terminal_decision_count"), 0,
                 "configuration_recovery_semantics_invalid"),
                ("security_review_protocol.yaml", ("independence", "workers_cannot_self_certify"), False,
                 "configuration_recovery_semantics_invalid"),
                ("security_review_protocol.yaml", ("risk_classification", "security_sensitive_tier"), "routine_delta",
                 "configuration_recovery_semantics_invalid"),
                ("security_review_protocol.yaml", ("risk_classification", "security_sensitive_triggers"), [],
                 "configuration_recovery_semantics_invalid"),
                ("direction_collaboration.yaml", ("dialogue", "maximum_orchestrator_rejoinders"), -1, "configuration_schema_invalid"),
                ("cost_controls.yaml", ("current_profile", "monetary_budget_enforcement"), "active", "configuration_recovery_semantics_invalid"),
                ("deepseek_cost_calibration.yaml", ("calibrations",), [{"sample_count": "one"}], "configuration_schema_invalid"),
                ("evidence_led_workflow.yaml", ("worker_environment", "package_or_environment_mutation"), [], "configuration_schema_invalid"),
            )
            for name, fields, value, reason in cases:
                self.documents, self.expected = dict(originals), dict(original_pins)
                self.mutate(name, fields, value)
                with self.subTest(name=name, fields=fields), self.assertRaises((core.ConfigurationError, rp.RaisaPolicyError)) as caught:
                    self.validate()
                self.assertEqual(caught.exception.reason_code, reason)

        def test_ambiguous_encodings_and_unknown_schemas_reject(self):
            for raw, encoding, reason in (
                (b'x: 1\nx: 2\n', "yaml", "configuration_duplicate_or_invalid_key"),
                (b'{"x":1,"x":2}', "json", "configuration_duplicate_or_invalid_key"),
                (b'x: &shared [1]\ny: *shared\n', "yaml", "configuration_alias_or_cycle"),
                (b'x: &unused 1\n', "yaml", "configuration_alias_or_cycle"),
                (b'x: .nan\n', "yaml", "configuration_nonfinite_number"),
                (b'{"x":Infinity}', "json", "configuration_nonfinite_number"),
                (b'x: 2026-09-12\n', "yaml", "configuration_value_type"),
                (b'\xef\xbb\xbf{}', "json", "configuration_encoding"),
            ):
                with self.subTest(raw=raw), self.assertRaises(core.ConfigurationError) as caught:
                    core.decode(raw, encoding)
                self.assertEqual(caught.exception.reason_code, reason)
            self.mutate("project.yaml", ("schema_version",), "ariadne.project_settings.future")
            with self.assertRaises(core.ConfigurationError) as caught:
                self.validate()
            self.assertEqual(caught.exception.reason_code, "configuration_schema_invalid")

        def test_core_interface_supports_an_unrelated_authored_consumer(self):
            docs = {"alpha.json": b'{"version":1,"next":"beta.json"}', "beta.json": b'{"enabled":false}'}
            schemas = {
                "alpha.json": ("json", ("object", (("version", ("literal", 1)), ("next", ("string", False))), ())),
                "beta.json": ("json", ("object", (("enabled", ("boolean",)),), ())),
            }
            pins = {name: b._sha(raw) for name, raw in docs.items()}
            reference = (core.Reference("alpha.json", ("next",), "beta.json"),)
            result = core.validate_configuration(documents=docs, expected_sha256=pins, schemas=schemas,
                                                 references=reference, roots=("alpha.json",))
            self.assertEqual(len(result.documents), 2)
            with self.assertRaises(core.ConfigurationError) as caught:
                core.validate_configuration(documents=docs, expected_sha256=pins, schemas=schemas,
                                            references=(), roots=("alpha.json",))
            self.assertEqual(caught.exception.reason_code, "configuration_reference_unreachable")

        def test_historical_precedence_matches_the_pinned_original_decision(self):
            raw = (self.source.parent / "inputs/orchestration_harness/programme_admission.py").read_bytes()
            self.assertEqual(b._sha(raw), "bcfd63edabd4b86bbbebbc3bb2ce5a1e52780eec4981156c7a571cff87147001")
            tree = ast.parse(raw)
            wanted = {"G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE", "G1B2_ACTIVE_PROFILE", "G1A_CLOSEOUT_REVIEW_PENDING_PROFILE",
                "G1B1_ACTIVE_PROFILE", "ADMITTED_PROGRAMME_GATE", "G1A3_ENABLEMENT_PENDING_PROFILE",
                "G1A3_R0_REVIEW_PENDING_PROFILE", "G1A3_R1_ACTIVE_PROFILE", "G1A3_ACTIVE_PROFILE",
                "SUBGATE_TRANSITION_TO_GATE", "G1A_CLOSEOUT_REPLACEMENT_TASK_GENERATION", "G1B1_CLOSEOUT_TASK_GENERATION"}
            class LegacyError(ValueError):
                def __init__(self, reason_code):
                    self.reason_code = reason_code
            namespace = {"Any": object, "ProgrammeAdmissionError": LegacyError,
                "bounded_g1b": types.SimpleNamespace(PROFILE_PREAMBLES={
                    "G1B_COMPLETION_ACTIVE": "Gate G1B is active only for bounded persistence, recovery, stale-lease protection and derived narrative",
                    "G1C_GOVERNOR_ACTIVE": "Gate G1C is active only for the bounded recovery governor and its versioned persistence integration",
                    "G1D_PROVENANCE_ACTIVE": "Gate G1D is active only for bounded observed provenance and independent local verification"})}
            for node in tree.body:
                if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in wanted:
                    namespace[node.targets[0].id] = ast.literal_eval(node.value)
            nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"_exact_keys", "_validate_precedence"}]
            self.assertEqual(len(nodes), 2)
            exec(compile(ast.Module(body=nodes, type_ignores=[]), "<pinned-pure-precedence>", "exec"), namespace)
            old = namespace["_validate_precedence"]
            project, continuation = (core.decode(self.documents[name], "yaml") for name in ("project.yaml", "autonomous_continuation.yaml"))
            rows = [
                ("authored_G0", "G0.8", "Gate G0.8 is the only authorised correction; G1A is", None),
                ("authored_G1A1", "G1A.1", "Gate G1A.1 is owner-accepted with residual risk; G1A.2", None),
                ("authored_G1A2", "G1A.2", "Gate G1A.2 is active only for its bounded verdict adapter; provider invocation", None),
                (namespace["G1A3_ENABLEMENT_PENDING_PROFILE"], "G1A.3", "Gate G1A.2 implementation is externally accepted. G1A.3 transition enablement", None),
                (namespace["G1A3_R0_REVIEW_PENDING_PROFILE"], "G1A.3", "Gate G1A.3-R0 is review-pending with no eligible implementation task", None),
                (namespace["G1A3_R1_ACTIVE_PROFILE"], "G1A.3", "Gate G1A.3-R1 is active only for complete review-byte binding", None),
                (namespace["G1A3_ACTIVE_PROFILE"], "G1A.3", "Gate G1A.3 is active only for its bounded integration-authority consumer", None),
                (namespace["G1A_CLOSEOUT_REVIEW_PENDING_PROFILE"], "G1A", "Gate G1A.3 implementation is externally accepted. G1A closeout and G1B transition enablement are review-pending; G1B remains closed.", namespace["G1A_CLOSEOUT_REPLACEMENT_TASK_GENERATION"]),
                (namespace["G1B1_ACTIVE_PROFILE"], "G1B.1", "Gate G1B.1 is active only for the bounded pure state/event kernel", None),
                (namespace["G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE"], "G1B.1", "Gate G1B.1 implementation is externally accepted; its closeout and G1B.2 transition enablement are review-pending, and G1B.2 remains closed.", namespace["G1B1_CLOSEOUT_TASK_GENERATION"]),
                (namespace["G1B2_ACTIVE_PROFILE"], "G1B.2", "Gate G1B.2 is active only for the pure versioned journal and deterministic replay kernel", None),
            ]
            rows.extend((profile, "authored", token, None) for profile, token in namespace["bounded_g1b"].PROFILE_PREAMBLES.items())
            for profile, correction, token, task in rows:
                state = {"active_profile": profile, "active_correction": correction}
                header = "# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n" + token + "\nMissing, malformed, stale, or contradictory programme state is a hard stop.\n"
                text = header + ("Task generation `" + task + "`" if task else "")
                with self.subTest(profile=profile):
                    self.assertIsNone(old(project, continuation, text, state))
                    self.assertIsNone(pa._validate_precedence(project, continuation, text, state))
                    cases = [({**project, "extra": True}, continuation, text, "project_settings_schema_invalid"),
                        (project, {**continuation, "extra": True}, text, "continuation_settings_schema_invalid"),
                        (project, continuation, "missing header", "agents_recovery_precedence_missing")]
                    changed_project = copy.deepcopy(project)
                    changed_project["autonomous_continuation"]["emergency_overlay"]["required"] = False
                    cases.append((changed_project, continuation, text, "recovery_precedence_invalid"))
                    if task:
                        cases.append((project, continuation, header, "agents_recovery_operation_identity_invalid"))
                    for first, second, agents, reason in cases:
                        for call, error in ((old, LegacyError), (pa._validate_precedence, pa.ProgrammeAdmissionError)):
                            with self.assertRaises(error) as caught:
                                call(first, second, agents, state)
                            self.assertEqual(caught.exception.reason_code, reason)

    class ConfigurationAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = SuccessorFixture(assets, "accept_g1d")
            self.addCleanup(self.fx.close)
            self.guard = no_legacy_observation()
            self.guard.__enter__()
            self.addCleanup(self.guard.__exit__, None, None, None)
            self.history = self.fx.component_history()
            self.history.__enter__()
            self.addCleanup(self.history.__exit__, None, None, None)

        def test_native_controller_installation_and_activation_are_distinct(self):
            f = self.fx
            decision = f.decision()
            self.assertTrue(decision.policy_admitted, decision.reason_codes)
            self.assertFalse(decision.execution_authorized)
            self.assertFalse(decision.assessment_passed)
            self.assertEqual(decision.current_gate, "G1E")
            state = b._json(f.after[b.STATE])
            self.assertTrue(state["g1d"]["completion_accepted"])
            self.assertFalse(state["g1e"]["completion_accepted"])
            for key in ("g1b", "g1c"):
                self.assertEqual(state[key], b._json(f.before[b.STATE])[key])
            self.assertEqual(state["g1d"]["current_operation"], b._json(f.before[b.STATE])["g1d"]["current_operation"])
            self.assertEqual(b.operation_paths("accept_g1d"), b.G1E_TRANSITION_PATHS)
            self.assertEqual(b.operation_paths("assess_g1e"), frozenset())

        def test_actual_read_only_assessment_cannot_grant_publication(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            activation = f.activate()
            f.prepare_assessment(activation)
            context = f.context()
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            report = pf.build_report(f.root, manifest, phase="assessment", entrypoint="recovery_preflight", bounded_context=context)
            self.assertEqual(report["status"], "assessment_pass", report)
            self.assertTrue(report["assessment_passed"])
            self.assertFalse(report["policy_eligible"])
            self.assertFalse(report["execution_authorized"])
            self.assertEqual(report["configuration_document_count"], 10)
            self.assertEqual(len(report["configuration_sha256"]), 64)
            self.assertEqual(f.git("rev-parse", "HEAD"), activation)
            self.assertEqual(f.git("write-tree"), f.q["candidate_tree"])
            for entrypoint, phase in (("task_branch_commit", "development"), ("task_branch_push", "pre-push"),
                                     ("task_branch_push", "post-push"), ("provider_invocation", "assessment")):
                with patch.object(b, "load_bounded_g1b_inputs", side_effect=AssertionError("effect request observed inputs")):
                    result = b.evaluate_bounded_g1b_operation(context=context, manifest=manifest, entrypoint=entrypoint, phase=phase)
                self.assertEqual(result.reason_codes, ("bounded_g1e_assessment_entrypoint_closed",))
                self.assertFalse(result.policy_admitted)
                self.assertFalse(result.assessment_passed)

        def test_complete_configuration_validation_is_on_the_actual_path(self):
            f = self.fx
            seen = []
            validate = core.validate_configuration
            def observed(**kwargs):
                seen.append((set(kwargs["documents"]), dict(kwargs["expected_sha256"])))
                return validate(**kwargs)
            with patch.object(core, "validate_configuration", side_effect=observed):
                self.assertTrue(f.decision().policy_admitted)
            self.assertEqual(len(seen), 1)
            self.assertEqual(seen[0][0], {Path(p).name for p in b.CONFIGURATION_PATHS})
            self.assertEqual(seen[0][1], {Path(p).name: f.q["payload_sha256"][p] for p in b.CONFIGURATION_PATHS})
            with patch.object(core, "validate_configuration", side_effect=core.ConfigurationError("authored_core_rejection")):
                self.assertEqual(f.decision().reason_codes, ("authored_core_rejection",))

        def test_bounded_precedence_never_imports_the_historical_module(self):
            f = self.fx
            context = f.context()
            inputs = b.load_bounded_g1b_inputs(context)
            original = builtins.__import__
            def no_history(name, globals=None, locals=None, fromlist=(), level=0):
                if name == "orchestration_harness.programme_admission" or (name == "orchestration_harness" and "programme_admission" in (fromlist or ())):
                    raise AssertionError("historical module imported by bounded policy")
                return original(name, globals, locals, fromlist, level)
            with patch.object(builtins, "__import__", side_effect=no_history):
                _after, snapshot = b._validate_loaded_policy(inputs)
            self.assertEqual(len(snapshot.documents), 10)

        def test_each_policy_leaf_is_bound_before_validation(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            for path in b.CONFIGURATION_LEAF_PINS:
                raw = (f.root / path).read_bytes()
                f.write(path, raw + b"\n")
                with self.subTest(path=path):
                    self.assertEqual(f.decision().reason_codes, ("bounded_g1b_input_digest_changed",))
                    f.q["payload_sha256"][path] = b._sha(raw + b"\n")
                    self.assertEqual(f.decision().reason_codes, ("bounded_g1b_frozen_input_changed",))
                f.write(path, raw)
                f.q["payload_sha256"][path] = b._sha(raw)

        def test_missing_extra_and_old_revision_bindings_reject(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            f.q["schema_version"] = "ariadne.bounded_g1b_binding.v1"
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_binding_version",))
            f.q = copy.deepcopy(original)
            del f.q["source_sha256"]["orchestration_harness/raisa_policy.py"]
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_source_paths",))
            f.q = copy.deepcopy(original)
            del f.q["payload_sha256"][next(iter(b.CONFIGURATION_LEAF_PINS))]
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_payload_paths",))
            f.q = copy.deepcopy(original)
            f.q["payload_sha256"]["unregistered.yaml"] = "0" * 64
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_payload_paths",))

        def test_installed_commit_parent_tree_and_source_are_authenticated(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            controller = copy.deepcopy(f.q["installed_controller"])
            for field in ("parent", "tree"):
                f.q["installed_controller"] = copy.deepcopy(controller)
                f.q["installed_controller"][field] = "0" * 40
                with self.subTest(field=field):
                    self.assertEqual(f.decision().reason_codes, ("bounded_g1e_controller_publication_invalid",))
            f.q["installed_controller"] = copy.deepcopy(controller)
            f.q["installed_controller"]["source_sha256"]["orchestration_harness/raisa_policy.py"] = "0" * 64
            self.assertEqual(f.decision().reason_codes, ("bounded_g1e_installed_controller_changed",))
            f.q["installed_controller"] = copy.deepcopy(controller)
            path = "orchestration_harness/configuration_core.py"
            raw = (f.root / path).read_bytes()
            f.write(path, raw + b"\n")
            f.q["payload_sha256"][path] = b._sha(raw + b"\n")
            self.assertEqual(f.decision().reason_codes, ("bounded_g1e_installed_controller_changed",))

        def test_assessment_rejects_stale_activation_and_different_current_tree(self):
            f = self.fx
            activation = f.activate()
            f.prepare_assessment(activation)
            self.assertTrue(f.decision().assessment_passed)
            current = copy.deepcopy(f.q)
            f.q["activation_commit"] = f.controller["commit"]
            self.assertFalse(f.decision().assessment_passed)
            f.q = copy.deepcopy(current)
            f.q["candidate_tree"] = "0" * 40
            self.assertEqual(f.decision().reason_codes, ("bounded_g1e_assessment_current_binding",))
            f.q = copy.deepcopy(current)
            child = f.git("commit-tree", f.q["base_tree"], "-p", activation, "-m", "authored later observation")
            f.git("update-ref", "--no-deref", "HEAD", child, activation)
            self.assertFalse(f.decision().assessment_passed)

        def test_activation_cannot_expand_configuration_or_execution_authority(self):
            f = self.fx
            original = b._json(f.after[b.G1E_SCOPE])
            cases = (
                ("g2_eligible", True), ("g1e_complete", True), ("feature_work_eligible", True),
                ("allowed_effects", ["repository_read", "task_branch_push"]),
                ("assessment_allowed_paths", ["orchestration_harness/configuration_core.py"]),
                ("configuration_paths", sorted(b.CONFIGURATION_PATHS) + ["unknown.yaml"]),
            )
            for key, value in cases:
                scope = copy.deepcopy(original)
                scope[key] = value
                with self.subTest(key=key), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g1e_acceptance_transition(f.before, scope)
                self.assertEqual(caught.exception.reason_code, "bounded_g1e_scope_invalid")

        def test_provenance_evidence_and_history_remain_required(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            for path in b.G1D_EVIDENCE_PINS:
                changed = dict(f.evidence)
                changed[path] += b"\n"
                with self.subTest(path=path), self.assertRaises(b.BoundedG1BError) as caught:
                    b.validate_g1e_acceptance_transition(f.before, f.after, changed)
                self.assertEqual(caught.exception.reason_code, "bounded_g1e_evidence_changed")
            f.component_header = f.component_header.replace(f.publication["tree"], "0" * 40)
            self.assertEqual(f.decision().reason_codes, ("bounded_g1e_component_publication_invalid",))

        def test_legacy_loading_rejects_each_g1e_marker(self):
            f = self.fx
            historical = b._json((f.source / "baseline" / b.STATE).read_bytes())
            cases = [lambda s: s.update(active_profile=b.G1E_PROFILE), lambda s: s.update(current_gate="G1E"),
                     lambda s: s.update(g1e={}), lambda s: s["task_selection"].update(allowed_task_kinds=[b.G1E_TASK])]
            for mutate in cases:
                state = copy.deepcopy(historical)
                mutate(state)
                f.write(b.STATE, b._canonical(state))
                with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa.load_programme_policy(f.root)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")
            f.write(b.STATE, b._canonical(historical))
            with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                pa.load_programme_policy(f.root)
            self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClosedRequestTests)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(IntegratedTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SuccessorTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ProvenanceAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigurationTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigurationAdmissionTests))
    return suite
