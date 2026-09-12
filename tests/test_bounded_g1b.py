"""Bounded controller contracts; integration receives explicit ordinary assets.

Run build_integration_suite(asset_root) from the reviewed external source capsule.
No fixture reads the live repository or imports its conftest. Historical authority
is hash pinned, so a later active gate cannot silently change the test baseline.
"""
from __future__ import annotations

import copy
import os
import subprocess
import tempfile
import unittest
from contextlib import ExitStack, contextmanager
from pathlib import Path
from unittest.mock import patch

from orchestration_harness import bounded_g1b as b
from orchestration_harness import pinned_programme_gatekeeper as pg
from orchestration_harness import programme_admission as pa
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
                         {"task_class": b.G1C_TASK}):
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
            activation_commit=None,
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
                "intended_side_effect_classes": sorted(b.EFFECTS)}

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
    def __init__(self, assets: Path):
        self.temporary = tempfile.TemporaryDirectory(prefix="g1c-contract-")
        self.home = Path(self.temporary.name)
        self.root = self.home / "target"
        self.root.mkdir()
        self.scratch = self.home / "index-scratch"
        self.scratch.mkdir()
        self.assets = assets
        self.source = Path(b.__file__).resolve().parents[1]
        self.before = {p: (self.source / "g1b-baseline" / p).read_bytes() for p in b.G1B_BASELINE_PINS}
        self.evidence = {p: (assets / "evidence" / p).read_bytes() for p in b.G1B_EVIDENCE_PINS}
        self.frozen = {p: (assets / "inputs" / p).read_bytes() for p in (*b.FROZEN_PINS, b.COST)}
        self.accepted_source = {p: (self.source / "g1b-accepted-source" / p).read_bytes()
                                for p in b.PERSISTENCE_PINS}
        for path, raw in {**self.before, **self.frozen, **self.accepted_source}.items():
            self.write(path, raw)
        self.git("init", "--quiet", "--template=", ".")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.filemode", "false")
        self.git("config", "index.version", "2")
        self.git("add", "--", *sorted({*self.before, *self.frozen, *self.accepted_source}))
        tree = self.git("write-tree")
        self.base = self.git("commit-tree", tree, "-m", "authored G1B component baseline")
        self.git("update-ref", "--no-deref", "HEAD", self.base)
        self.after = b.build_g1c_acceptance_transition(self.before,
            b.build_governor_scope("2026-09-12T00:00:00+00:00", self.base))
        for path, raw in self.after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(b.G1C_TRANSITION_PATHS))
        candidate_tree = self.git("write-tree")
        self.q = dict(schema_version=b.BINDING_VERSION, operation_id="authored-g1c-acceptance",
            operation_kind="accept_g1b", phase="development", base_commit=self.base, base_tree=tree,
            expected_head=self.base, expected_index_tree=candidate_tree, candidate_tree=candidate_tree,
            activation_commit=None,
            source_sha256={p: b._sha((self.source / p).read_bytes()) for p in b.SOURCE_PATHS},
            payload_sha256={p: b._sha((self.root / p).read_bytes()) for p in b.G1C_INPUT_PATHS})
        self.binding_path = self.home / "binding.json"
        self.component_header = ("tree " + b.PERSISTENCE_PUBLICATION["tree"] + "\nparent "
                                 + b.PERSISTENCE_PUBLICATION["parent"] + "\n\nauthored observation\n")
        self.component_ancestry_error = None

    @contextmanager
    def component_history(self):
        run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
        accepted = b.PERSISTENCE_PUBLICATION["commit"]

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
        self.q.update(operation_kind="implement_g1c", phase="development", base_commit=activation,
                      base_tree=self.q["candidate_tree"], activation_commit=activation)
        for path in b.GOVERNOR_PATHS:
            self.write(path, b"authored candidate; deliberately not importable Python\n")
        self.git("add", "--", *sorted(b.GOVERNOR_PATHS))
        tree = self.git("write-tree")
        self.q.update(candidate_tree=tree, expected_index_tree=tree)


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

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClosedRequestTests)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(IntegratedTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SuccessorTests))
    return suite
