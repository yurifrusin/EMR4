"""Bounded controller contracts; integration receives explicit ordinary assets.

Run build_integration_suite(asset_root) from the reviewed external source capsule.
No fixture reads the live repository or imports its conftest. Historical authority
is hash pinned, so a later active gate cannot silently change the test baseline.
"""
from __future__ import annotations

import copy
import ast
import builtins
import json
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
                         {"operation_kind": "accept_g1d"}, {"operation_kind": "assess_g1e"}, {"task_class": b.G1E_TASK},
                         {"operation_kind": "accept_g1e"}, {"operation_kind": "repair_g2_fixture"}, {"task_class": b.G2_TASK},
                         {"operation_kind": "enable_g2_batches"}, {"operation_kind": "extend_g2_catalogue"},
                         {"operation_kind": "repair_g2_batch"}, {"operation_kind": "enable_g2_migration"},
                         {"operation_kind": "repair_g2_migration"}, {"operation_kind": "align_g2_instructions"},
                         {"operation_kind": "enable_g2_audio_privacy"},
                         {"operation_kind": "repair_g2_audio_privacy"},
                         {"operation_kind": "enable_g2_patient_binding"},
                         {"operation_kind": "repair_g2_patient_binding"}):
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


class G2AudioSourceContractTests(unittest.TestCase):
    @staticmethod
    def prospective_sources():
        sources = copy.deepcopy(b.G2_AUDIO_PREDECESSOR["source_sha256"])
        sources["orchestration_harness/bounded_g1b.py"] = "1" * 64
        sources["orchestration_harness/raisa_policy.py"] = "2" * 64
        sources["tests/test_bounded_g1b.py"] = "3" * 64
        return sources

    def scope(self):
        return b.build_g2_audio_scope(
            "2026-09-14T14:00:00+00:00",
            b.G2_AUDIO_INSTRUCTIONS_PUBLICATION["commit"],
            self.prospective_sources(),
        )

    def test_v5_scope_is_exact_and_preserves_all_closures(self):
        scope = self.scope()
        self.assertEqual(scope["schema_version"], b.G2_AUDIO_SCOPE_VERSION)
        self.assertEqual(scope["transition_base_commit"], b.G2_AUDIO_INSTRUCTIONS_PUBLICATION["commit"])
        self.assertEqual(
            scope["current_instruction_policy"],
            {"path": b.AGENTS, "sha256": b.G2_AUDIO_INSTRUCTIONS_SHA256,
             "previous_sha256": b.G2_INSTRUCTIONS_SHA256,
             "publication": b.G2_AUDIO_INSTRUCTIONS_PUBLICATION},
        )
        self.assertEqual(scope["allowed_paths"], sorted(b.G2_AUDIO_PATHS))
        self.assertEqual(scope["allowed_additions"], [b.G2_AUDIO_ADDITION])
        self.assertEqual(scope["maximum_changed_files"], 4)
        self.assertEqual(scope["prior_instruction_alignment"]["commit"], b.G2_AUDIO_PREDECESSOR["commit"])
        self.assertEqual(scope["trusted_git_successor"],
                         {**b.G2_AUDIO_TRUSTED_GIT_PUBLICATION,
                          "source_sha256": b.G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256})
        self.assertEqual(scope["owner_test_runtime_exception"], rp.g2_test_exception())
        self.assertEqual(scope["claim_limits"], list(b.G2_AUDIO_LIMITS))
        self.assertFalse(scope["execution_authorized"])
        self.assertFalse(scope["feature_work_eligible"])
        self.assertFalse(scope["g2_complete"])
        b._validate_g2_batch_scope(scope)
        for mutate in (
            lambda s: s["allowed_paths"].append("app/not-reviewed.py"),
            lambda s: s["allowed_additions"].append("tests/not-reviewed.py"),
            lambda s: s.update(maximum_changed_files=5),
            lambda s: s["trusted_git_successor"].update(commit="0" * 40),
            lambda s: s["current_instruction_policy"].update(sha256="0" * 64),
            lambda s: s["current_instruction_policy"]["publication"].update(commit="0" * 40),
            lambda s: s["trusted_git_successor"]["source_sha256"].update(
                {"orchestration_harness/trusted_git.py": "0" * 64}),
            lambda s: s.update(execution_authorized=True),
            lambda s: s.update(g2_complete=True),
            lambda s: s["owner_test_runtime_exception"].update(admission_grants_runtime_authority=True),
            lambda s: s["claim_limits"].pop(),
        ):
            changed = copy.deepcopy(scope)
            mutate(changed)
            with self.subTest(changed=changed), self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_batch_scope(changed)
            self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_scope_invalid")

    def test_activation_owns_six_and_repair_owns_only_four(self):
        row = {"before_sha256": "4" * 64, "after_sha256": "5" * 64}
        activation = {
            "schema_version": b.G2_AUDIO_BINDING_VERSION,
            "operation_kind": "enable_g2_audio_privacy",
            "repair_sha256": {p: copy.deepcopy(row) for p in b.G2_AUDIO_MAINTENANCE_PATHS},
        }
        self.assertEqual(set(b._batch_changes(activation)), b.G2_AUDIO_MAINTENANCE_PATHS)
        self.assertEqual(len(b.G2_AUDIO_MAINTENANCE_PATHS), 6)
        missing = copy.deepcopy(activation)
        missing["repair_sha256"].pop(b.STATE)
        with self.assertRaises(b.BoundedG1BError) as caught:
            b._batch_changes(missing)
        self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_path_not_allowed")

        repair = {
            "schema_version": b.G2_AUDIO_BINDING_VERSION,
            "operation_kind": "repair_g2_audio_privacy",
            "repair_sha256": {p: copy.deepcopy(row) for p in b.G2_AUDIO_PATHS},
        }
        repair["repair_sha256"][b.G2_AUDIO_ADDITION]["before_sha256"] = None
        self.assertEqual(set(b._batch_changes(repair)), b.G2_AUDIO_PATHS)
        self.assertEqual(b.operation_paths("repair_g2_audio_privacy", repair), b.G2_AUDIO_PATHS)
        self.assertEqual(b.operation_effects("repair_g2_audio_privacy"), b.G2_AUDIO_EFFECTS)
        self.assertEqual(b._operation("repair_g2_audio_privacy", repair)["limits"], b.G2_AUDIO_LIMITS)

        invalid = copy.deepcopy(repair)
        invalid["repair_sha256"]["tests/not-reviewed.py"] = invalid["repair_sha256"].pop(b.G2_AUDIO_ADDITION)
        with self.assertRaises(b.BoundedG1BError) as caught:
            b._batch_changes(invalid)
        self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_path_not_allowed")
        invalid = copy.deepcopy(repair)
        invalid["repair_sha256"]["app/main.py"]["before_sha256"] = None
        with self.assertRaises(b.BoundedG1BError) as caught:
            b._batch_changes(invalid)
        self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_change_digest")

    def test_v4_cannot_be_relabelled_as_audio(self):
        for operation in ("enable_g2_audio_privacy", "repair_g2_audio_privacy"):
            binding = {
                "schema_version": b.G2_INSTRUCTIONS_BINDING_VERSION,
                "operation_kind": operation,
                "repair_sha256": {
                    "orchestration_harness/bounded_g1b.py":
                        {"before_sha256": "6" * 64, "after_sha256": "7" * 64},
                },
            }
            with self.subTest(operation=operation), self.assertRaises(b.BoundedG1BError) as caught:
                b._batch_changes(binding)
            self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_binding_version")

    def test_trusted_git_successor_commit_and_blobs_fail_closed(self):
        publication = b.G2_AUDIO_TRUSTED_GIT_PUBLICATION
        def observed_text(_root, *args, **_kwargs):
            if args == ("cat-file", "commit", publication["commit"]):
                return "tree " + publication["tree"] + "\nparent " + publication["parent"] + "\n\nauthored\n"
            if args == ("merge-base", "--is-ancestor", publication["commit"], "f" * 40):
                return ""
            raise AssertionError(args)

        def observed_bytes(_root, *args, **_kwargs):
            prefix = publication["commit"] + ":"
            path = args[2][len(prefix):]
            return b.G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256[path].encode()

        with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes), \
                patch.object(b, "_sha", side_effect=lambda raw: raw.decode()):
            b._validate_g2_audio_trusted_git_publication(Path("synthetic"), "f" * 40)

        with patch.object(b.trusted_git, "run_git", return_value="tree " + "0" * 40):
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_audio_trusted_git_publication(Path("synthetic"), "f" * 40)
        self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_publication_invalid")

        def changed_bytes(_root, *args, **_kwargs):
            return b"0" * 64
        with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                patch.object(b.trusted_git, "run_git_bytes", side_effect=changed_bytes), \
                patch.object(b, "_sha", side_effect=lambda raw: raw.decode()):
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_audio_trusted_git_publication(Path("synthetic"), "f" * 40)
        self.assertEqual(caught.exception.reason_code,
                         "bounded_g2_audio_trusted_git_publication_bytes_changed")

    def test_instruction_successor_preserves_previous_and_binds_current_bytes(self):
        publication = b.G2_AUDIO_INSTRUCTIONS_PUBLICATION

        def observed_text(_root, *args, **_kwargs):
            if args == ("cat-file", "commit", publication["commit"]):
                return "tree " + publication["tree"] + "\nparent " + publication["parent"] + "\n\nauthored\n"
            if args == ("merge-base", "--is-ancestor", publication["commit"], "f" * 40):
                return ""
            raise AssertionError(args)

        def observed_bytes(_root, *args, **_kwargs):
            commit = args[2].split(":", 1)[0]
            digest = (b.G2_INSTRUCTIONS_SHA256
                      if commit == publication["parent"] else b.G2_AUDIO_INSTRUCTIONS_SHA256)
            return digest.encode()

        with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes), \
                patch.object(b, "_sha", side_effect=lambda raw: raw.decode()):
            b._validate_g2_audio_instructions_publication(Path("synthetic"), "f" * 40)

        with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                patch.object(b.trusted_git, "run_git_bytes", return_value=b"0" * 64), \
                patch.object(b, "_sha", side_effect=lambda raw: raw.decode()):
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_audio_instructions_publication(Path("synthetic"), "f" * 40)
        self.assertEqual(caught.exception.reason_code,
                         "bounded_g2_audio_instructions_publication_bytes_changed")


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
        assert operation_kind in {"accept_g1b", "accept_g1c", "accept_g1d", "accept_g1e"}
        self.operation = b._operation(operation_kind)
        self.publication = self.operation["accepted_publication"]
        self.is_provenance = operation_kind == "accept_g1c"
        self.is_g2 = operation_kind == "accept_g1e"
        self.is_configuration = operation_kind in {"accept_g1d", "accept_g1e"}
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
        if self.is_g2:
            frozen_paths.update({b.G1D_SCOPE, *b.PROVENANCE_PINS, *b.G2_REPAIR_PINS})

        def frozen_input(path):
            if self.is_g2:
                if path in self.before:
                    return self.before[path]
                if path == b.G1D_SCOPE:
                    return (self.source / "g1d-baseline" / path).read_bytes()
                if path in b.PROVENANCE_PINS:
                    return (self.source / "g1d-accepted-source" / path).read_bytes()
                if path == b.G2_FIXTURE:
                    return (assets / "g2-fixture/before").read_bytes()
                if path == b.G2_COLD_IMPORT:
                    return (assets / "g2-cold-import/before").read_bytes()
            if self.is_configuration:
                if path == b.G1C_SCOPE:
                    return (self.source / "g1c-baseline" / path).read_bytes()
                if path in b.GOVERNOR_PINS:
                    return (self.source / "g1c-accepted-source" / path).read_bytes()
                if path in b.CONFIGURATION_PATHS:
                    return (assets / "configuration" / path).read_bytes()
            return (assets / "inputs" / path).read_bytes()

        self.frozen = {p: frozen_input(p) for p in frozen_paths}
        source_directory = "g1e-accepted-source" if self.is_g2 else "g1d-accepted-source" if self.is_configuration else "g1c-accepted-source" if self.is_provenance else "g1b-accepted-source"
        self.accepted_source = {p: (self.source / source_directory / p).read_bytes()
                                for p in self.operation["accepted_pins"]}
        initial_source, installed_source = {}, {}
        if self.is_configuration:
            installed_source = {p: (self.source / p).read_bytes() for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
            if self.is_g2:
                initial_source = {p: (self.source / "g1e-accepted-source" / p).read_bytes() for p in installed_source}
            else:
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
            changed_controller = b.CONTROLLER_PATHS - {"orchestration_harness/configuration_core.py"} if self.is_g2 else b.CONTROLLER_PATHS
            for path in changed_controller:
                self.write(path, installed_source[path])
            self.git("add", "--", *sorted(changed_controller))
            tree = self.git("write-tree")
            self.base = self.git("commit-tree", tree, "-p", parent, "-m", "authored controller installation")
            self.git("update-ref", "--no-deref", "HEAD", self.base, parent)
            self.controller = {"commit": self.base, "parent": parent, "tree": tree,
                               "source_sha256": {p: b._sha(installed_source[p]) for p in b.CONTROLLER_PATHS}}
            transition = b.build_g2_acceptance_transition if self.is_g2 else b.build_g1e_acceptance_transition
            scope = b.build_g2_repair_scope if self.is_g2 else b.build_configuration_scope
            self.after = transition(self.before, scope("2026-09-13T00:00:00+00:00", self.base, self.controller))
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
        self.accepted_activation_header = "tree " + b.G1E_ACTIVATION["tree"] + "\nparent " + b.G1E_ACTIVATION["parent"] + "\n\nauthored historical activation\n"
        self.accepted_activation_source = dict(self.before)

    @contextmanager
    def component_history(self):
        run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
        accepted = self.publication["commit"]

        def observed_text(root, *args, **kwargs):
            if self.is_g2 and root == self.root:
                if args == ("cat-file", "commit", b.G1E_ACTIVATION["commit"]):
                    return self.accepted_activation_header
                if args == ("merge-base", "--is-ancestor", b.G1E_ACTIVATION["commit"], self.q["base_commit"]):
                    return ""
            if root == self.root and args == ("cat-file", "commit", accepted):
                return self.component_header
            if root == self.root and args == ("merge-base", "--is-ancestor", accepted, self.q["base_commit"]):
                if self.component_ancestry_error:
                    raise b.trusted_git.TrustedGitError(self.component_ancestry_error)
                return ""
            return run(root, *args, **kwargs)

        def observed_bytes(root, *args, **kwargs):
            if self.is_g2:
                for path, raw in self.accepted_activation_source.items():
                    if root == self.root and args == ("cat-file", "blob", b.G1E_ACTIVATION["commit"] + ":" + path):
                        return raw
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
        assert self.is_g2 or not self.is_configuration, "installed G1E component is assessed, not republished"
        kind = "repair_g2_fixture" if self.is_g2 else "implement_g1d" if self.is_provenance else "implement_g1c"
        self.q.update(operation_kind=kind, phase="development", base_commit=activation,
                      base_tree=self.q["candidate_tree"], activation_commit=activation)
        for path in b.operation_paths(kind):
            if self.is_g2:
                folder = "g2-fixture" if path == b.G2_FIXTURE else "g2-cold-import"
                raw = (self.assets / folder / "after").read_bytes()
            else:
                raw = b"authored candidate; deliberately not importable Python\n"
            self.write(path, raw)
            if self.is_g2:
                self.q["payload_sha256"][path] = b._sha(raw)
        self.git("add", "--", *sorted(b.operation_paths(kind)))
        tree = self.git("write-tree")
        self.q.update(candidate_tree=tree, expected_index_tree=tree)

    def prepare_assessment(self, activation):
        assert self.is_configuration
        self.q.update(operation_kind="assess_g1e", phase="assessment", base_commit=activation,
                      base_tree=self.q["candidate_tree"], expected_head=activation,
                      expected_index_tree=self.q["candidate_tree"], activation_commit=activation)


class G2BatchFixture(SuccessorFixture):
    """Real candidate/index/history; fixed published history is authored data."""
    def __init__(self, assets):
        super().__init__(assets, "accept_g1e")
        self.initial_policy = {p: (assets / "g2-published-policy" / p).read_bytes()
                               for p in b.G2_INITIAL_POLICY_PINS}
        self.initial_source = {p: (self.source / "g2-initial-source" / p).read_bytes()
                               for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        pool = {p: b"# authored ordinary source; never imported\n" for p in b.G2_BATCH_PATHS}
        pool[b.G2_FIXTURE] = (assets / "g2-fixture/after").read_bytes()
        pool[b.G2_COLD_IMPORT] = (assets / "g2-cold-import/after").read_bytes()
        self.initial_pool = pool
        initial = {**self.initial_policy, **self.initial_source, **pool}
        for path, raw in initial.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(initial))
        base_tree = self.git("write-tree")
        base = self.git("commit-tree", base_tree, "-p", self.base, "-m", "authored first G2 repair baseline")
        self.git("update-ref", "--no-deref", "HEAD", base)
        self.base = base
        self.batch_scope = b.build_g2_batch_scope("2026-09-13T15:00:00+00:00", base,
            {p: b._sha((self.source / p).read_bytes()) for p in b.CONTROLLER_PATHS})
        after = b.build_g2_batch_transition({p: self.initial_policy[p] for p in b.G2_BATCH_CONTROL_PATHS},
                                          self.batch_scope)
        after.update({p: (self.source / p).read_bytes() for p in b.G2_BATCH_CODE_PATHS})
        changes = {p: {"before_sha256": b._sha((self.root / p).read_bytes()), "after_sha256": b._sha(raw)}
                   for p, raw in after.items()}
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        candidate_tree = self.git("write-tree")
        self.q = dict(schema_version=b.G2_BATCH_BINDING_VERSION, operation_id="authored-g2-batch-maintenance",
            operation_kind="enable_g2_batches", phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=candidate_tree, candidate_tree=candidate_tree,
            activation_commit=b.G2_INITIAL_ACTIVATION["commit"],
            installed_controller=copy.deepcopy(b.G2_INITIAL_CONTROLLER), repair_sha256=changes,
            source_sha256={p: b._sha((self.source / p).read_bytes()) for p in b.SOURCE_PATHS},
            payload_sha256={p: b._sha((self.root / p).read_bytes()) for p in b.G2_BATCH_INPUT_PATHS})

    def manifest(self, context):
        return {"schema_version": b.REQUEST_VERSION, "operation_id": self.q["operation_id"],
                "operation_kind": self.q["operation_kind"], "binding_sha256": context.expected_binding_sha256,
                "candidate_tree": self.q["candidate_tree"], "allowed_paths": sorted(self.q["repair_sha256"]),
                "intended_side_effect_classes": sorted(b.operation_effects(self.q["operation_kind"]))}

    @contextmanager
    def component_history(self):
        with super().component_history():
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            archives = ((b.G2_INITIAL_CONTROLLER, self.initial_source),
                        (b.G2_INITIAL_ACTIVATION, self.initial_policy),
                        (b.G2_INITIAL_REPAIR, self.initial_pool))

            def observed_text(root, *args, **kwargs):
                for publication, _files in archives:
                    if root == self.root and args == ("cat-file", "commit", publication["commit"]):
                        return "tree " + publication["tree"] + "\nparent " + publication["parent"] + "\n\nauthored history\n"
                    if root == self.root and args == ("merge-base", "--is-ancestor", publication["commit"], self.q["base_commit"]):
                        return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for publication, files in archives:
                    for path, raw in files.items():
                        if root == self.root and args == ("cat-file", "blob", publication["commit"] + ":" + path):
                            return raw
                return run_bytes(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                    patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
                yield

    def commit_current(self):
        parent = self.q["base_commit"]
        commit = self.git("commit-tree", self.q["candidate_tree"], "-p", parent, "-m", "authored reviewed batch")
        self.git("update-ref", "--no-deref", "HEAD", commit, parent)
        self.q.update(phase="pre-push", expected_head=commit)
        return commit

    def activate_batches(self):
        self.activation = self.commit_current()
        self.batch_controller = {"commit": self.activation, "parent": self.q["base_commit"],
                                 "tree": self.q["candidate_tree"],
                                 "source_sha256": copy.deepcopy(self.batch_scope["controller_source_sha256"])}

    def prepare_batch(self, changes):
        base = self.git("rev-parse", "HEAD")
        base_tree = self.git("rev-parse", "HEAD^{tree}")
        rows = {}
        for path, raw in changes.items():
            rows[path] = {"before_sha256": b._sha((self.root / path).read_bytes()), "after_sha256": b._sha(raw)}
            self.write(path, raw)
        self.git("add", "--", *sorted(changes))
        tree = self.git("write-tree")
        self.q.update(operation_kind="repair_g2_batch", operation_id="authored-g2-source-repair",
            phase="development", base_commit=base, base_tree=base_tree, expected_head=base,
            expected_index_tree=tree, candidate_tree=tree, activation_commit=self.activation,
            installed_controller=copy.deepcopy(self.batch_controller), repair_sha256=rows,
            payload_sha256={p: b._sha((self.root / p).read_bytes()) for p in b.G2_BATCH_INPUT_PATHS})


class G2CatalogueFixture(G2BatchFixture):
    """Current captured batch controller plus only two authored catalogue files."""
    AI = "app/services/ai/service.py"
    LATER = "app/services/ai/audit_store.py"

    def __init__(self, assets):
        super().__init__(assets)
        self.previous_policy = {p: (assets / "g2-batch-published-policy" / p).read_bytes()
                                for p in b.G2_CATALOGUE_PREDECESSOR_POLICY}
        self.previous_source = {p: (self.source / "g2-batch-installed-source" / p).read_bytes()
                                for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        previous = {**self.previous_policy, **self.previous_source,
                    self.AI: b"# authored AI baseline; never imported\n",
                    self.LATER: b"# authored later baseline; never imported\n"}
        for path, raw in previous.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(previous))
        base_tree = self.git("write-tree")
        base = self.git("commit-tree", base_tree, "-p", self.base, "-m", "authored installed batch baseline")
        self.git("update-ref", "--no-deref", "HEAD", base)
        self.base = base
        self.batch_scope = b.build_g2_catalogue_scope("2026-09-13T22:00:00+00:00", base,
            {p: b._sha((self.source / p).read_bytes()) for p in b.CONTROLLER_PATHS})
        after = b.build_g2_catalogue_transition({p: self.previous_policy[p] for p in b.G2_BATCH_CONTROL_PATHS},
                                               self.batch_scope)
        after.update({p: (self.source / p).read_bytes() for p in b.G2_BATCH_CODE_PATHS})
        changes = {p: {"before_sha256": b._sha((self.root / p).read_bytes()), "after_sha256": b._sha(raw)}
                   for p, raw in after.items()}
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(schema_version=b.G2_CATALOGUE_BINDING_VERSION, operation_id="authored-g2-catalogue-extension",
            operation_kind="extend_g2_catalogue", phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=tree, candidate_tree=tree,
            activation_commit=b.G2_CATALOGUE_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(b.G2_CATALOGUE_PREDECESSOR), repair_sha256=changes)
        self.q["payload_sha256"] = {p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}

    @contextmanager
    def component_history(self):
        with super().component_history():
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            publication = b.G2_CATALOGUE_PREDECESSOR
            files = {**self.previous_policy, **self.previous_source}

            def observed_text(root, *args, **kwargs):
                if root == self.root and args == ("cat-file", "commit", publication["commit"]):
                    return "tree " + publication["tree"] + "\nparent " + publication["parent"] + "\n\nauthored fixed history\n"
                if root == self.root and args == ("merge-base", "--is-ancestor", publication["commit"], self.q["base_commit"]):
                    return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for path, raw in files.items():
                    if root == self.root and args == ("cat-file", "blob", publication["commit"] + ":" + path):
                        return raw
                return run_bytes(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                    patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
                yield

    def prepare_batch(self, changes):
        super().prepare_batch(changes)
        self.q["payload_sha256"] = {p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}


class G2MigrationFixture(G2CatalogueFixture):
    """Fixed captured v2 authority, with a genuinely absent authored test file."""
    MIGRATION = "alembic/versions/d4787e8e3629_phase_0_baseline.py"
    TEST = "tests/test_phase0_migration_preservation.py"

    def __init__(self, assets):
        super().__init__(assets)
        self.migration_previous_policy = {
            p: (assets / "g2-catalogue-published-policy" / p).read_bytes()
            for p in b.G2_MIGRATION_PREDECESSOR_POLICY}
        self.migration_previous_source = {
            p: (self.source / "g2-catalogue-installed-source" / p).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        previous = {**self.migration_previous_policy, **self.migration_previous_source,
                    self.MIGRATION: b"# authored historical migration; never imported\n"}
        for path, raw in previous.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(previous))
        base_tree = self.git("write-tree")
        base = self.git("commit-tree", base_tree, "-p", self.base, "-m", "authored installed catalogue baseline")
        self.git("update-ref", "--no-deref", "HEAD", base)
        self.base = base
        self.batch_scope = b.build_g2_migration_scope("2026-09-14T01:00:00+00:00", base,
            {p: b._sha((self.source / p).read_bytes()) for p in b.CONTROLLER_PATHS})
        after = b.build_g2_migration_transition(
            {p: self.migration_previous_policy[p] for p in b.G2_BATCH_CONTROL_PATHS}, self.batch_scope)
        after.update({p: (self.source / p).read_bytes() for p in b.G2_BATCH_CODE_PATHS})
        changes = {p: {"before_sha256": b._sha((self.root / p).read_bytes()), "after_sha256": b._sha(raw)}
                   for p, raw in after.items()}
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(schema_version=b.G2_MIGRATION_BINDING_VERSION, operation_id="authored-g2-migration-enablement",
            operation_kind="enable_g2_migration", phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=tree, candidate_tree=tree,
            activation_commit=b.G2_MIGRATION_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(b.G2_MIGRATION_PREDECESSOR), repair_sha256=changes)
        self.q["payload_sha256"] = {p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}

    @contextmanager
    def component_history(self):
        with super().component_history():
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            publication = b.G2_MIGRATION_PREDECESSOR
            files = {**self.migration_previous_policy, **self.migration_previous_source}

            def observed_text(root, *args, **kwargs):
                if root == self.root and args == ("cat-file", "commit", publication["commit"]):
                    return "tree " + publication["tree"] + "\nparent " + publication["parent"] + "\n\nauthored fixed history\n"
                if root == self.root and args == ("merge-base", "--is-ancestor", publication["commit"], self.q["base_commit"]):
                    return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for path, raw in files.items():
                    if root == self.root and args == ("cat-file", "blob", publication["commit"] + ":" + path):
                        return raw
                return run_bytes(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                    patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
                yield

    def prepare_migration(self, changes):
        base = self.git("rev-parse", "HEAD")
        base_tree = self.git("rev-parse", "HEAD^{tree}")
        rows = {}
        for path, raw in changes.items():
            prior = self.root / path
            rows[path] = {"before_sha256": b._sha(prior.read_bytes()) if prior.is_file() else None,
                          "after_sha256": b._sha(raw)}
            self.write(path, raw)
        self.git("add", "--", *sorted(changes))
        tree = self.git("write-tree")
        self.q.update(operation_kind="repair_g2_migration", operation_id="authored-g2-migration-repair",
            phase="development", base_commit=base, base_tree=base_tree, expected_head=base,
            expected_index_tree=tree, candidate_tree=tree, activation_commit=self.activation,
            installed_controller=copy.deepcopy(self.batch_controller), repair_sha256=rows)
        self.q["payload_sha256"] = {p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}


class G2InstructionsFixture(G2MigrationFixture):
    """Captured migration controller and instruction publication, native candidate Git."""
    def __init__(self, assets):
        super().__init__(assets)
        self.instructions_previous_policy = {
            p: (assets / "g2-migration-published-policy" / p).read_bytes()
            for p in b.G2_INSTRUCTIONS_PREDECESSOR_POLICY}
        self.instructions_previous_source = {
            p: (self.source / "g2-migration-installed-source" / p).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        self.published_instructions = (assets / "g2-instructions-published-policy" / b.AGENTS).read_bytes()
        previous = {**self.instructions_previous_policy, **self.instructions_previous_source,
                    self.TEST: b"# authored previously published regression; never imported\n"}
        for path, raw in previous.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(previous))
        prior_tree = self.git("write-tree")
        prior = self.git("commit-tree", prior_tree, "-p", self.base, "-m", "authored published migration baseline")
        self.write(b.AGENTS, self.published_instructions)
        self.git("add", "--", b.AGENTS)
        base_tree = self.git("write-tree")
        base = self.git("commit-tree", base_tree, "-p", prior, "-m", "authored owner instruction publication")
        self.git("update-ref", "--no-deref", "HEAD", base)
        self.base = base
        self.batch_scope = b.build_g2_instructions_scope("2026-09-14T12:00:00+00:00", base,
            {p: b._sha((self.source / p).read_bytes()) for p in b.CONTROLLER_PATHS})
        after = b.build_g2_instructions_transition(
            {p: self.instructions_previous_policy[p] for p in b.G2_BATCH_CONTROL_PATHS}, self.batch_scope)
        after.update({p: (self.source / p).read_bytes()
                      for p in b.G2_INSTRUCTIONS_MAINTENANCE_PATHS - b.G2_BATCH_CONTROL_PATHS})
        after = {p: raw for p, raw in after.items() if p in b.G2_INSTRUCTIONS_MAINTENANCE_PATHS}
        changes = {p: {"before_sha256": b._sha((self.root / p).read_bytes()), "after_sha256": b._sha(raw)}
                   for p, raw in after.items()}
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(schema_version=b.G2_INSTRUCTIONS_BINDING_VERSION, operation_id="authored-g2-instruction-alignment",
            operation_kind="align_g2_instructions", phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=tree, candidate_tree=tree,
            activation_commit=b.G2_INSTRUCTIONS_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(b.G2_INSTRUCTIONS_PREDECESSOR), repair_sha256=changes)
        self.q["payload_sha256"] = {p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}

    @contextmanager
    def component_history(self):
        with super().component_history():
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            predecessor = b.G2_INSTRUCTIONS_PREDECESSOR
            publication = b.G2_INSTRUCTIONS_PUBLICATION
            files = {**self.instructions_previous_policy, **self.instructions_previous_source}

            def observed_text(root, *args, **kwargs):
                for declared in (predecessor, publication):
                    if root == self.root and args == ("cat-file", "commit", declared["commit"]):
                        return "tree " + declared["tree"] + "\nparent " + declared["parent"] + "\n\nauthored fixed history\n"
                    if root == self.root and args == ("merge-base", "--is-ancestor", declared["commit"], self.q["base_commit"]):
                        return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for path, raw in files.items():
                    if root == self.root and args == ("cat-file", "blob", predecessor["commit"] + ":" + path):
                        return raw
                if root == self.root and args == ("cat-file", "blob", publication["commit"] + ":" + b.AGENTS):
                    return self.published_instructions
                if root == self.root and args == ("cat-file", "blob", publication["parent"] + ":" + b.AGENTS):
                    return self.instructions_previous_policy[b.AGENTS]
                return run_bytes(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                    patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
                yield


class G2PatientSourceContractTests(unittest.TestCase):
    @staticmethod
    def prospective_sources():
        sources = copy.deepcopy(b.G2_PATIENT_PREDECESSOR["source_sha256"])
        sources["orchestration_harness/bounded_g1b.py"] = "8" * 64
        sources["orchestration_harness/raisa_policy.py"] = "9" * 64
        sources["tests/test_bounded_g1b.py"] = "a" * 64
        return sources

    def scope(self):
        return b.build_g2_patient_scope(
            "2026-09-15T00:00:00+00:00",
            b.G2_AUDIO_REPAIR_PUBLICATION["commit"],
            self.prospective_sources(),
        )

    def test_v6_scope_is_exact_and_keeps_runtime_and_acceptance_closed(self):
        scope = self.scope()
        self.assertEqual(scope["schema_version"], b.G2_PATIENT_SCOPE_VERSION)
        self.assertEqual(scope["transition_base_commit"], b.G2_AUDIO_REPAIR_PUBLICATION["commit"])
        self.assertEqual(scope["allowed_paths"], sorted(b.G2_PATIENT_PATHS))
        self.assertEqual(scope["allowed_additions"], [b.G2_PATIENT_ADDITION])
        self.assertEqual(scope["maximum_changed_files"], 4)
        self.assertEqual(scope["prior_audio_activation"],
                         {"commit": b.G2_PATIENT_PREDECESSOR["commit"],
                          "scope_sha256": b.G2_PATIENT_PREDECESSOR_POLICY[b.G2_SCOPE]})
        self.assertEqual(scope["published_audio_repair"],
                         {**b.G2_AUDIO_REPAIR_PUBLICATION,
                          "source_sha256": b.G2_AUDIO_REPAIR_SOURCE_SHA256})
        self.assertEqual(scope["claim_limits"], list(b.G2_PATIENT_LIMITS))
        self.assertFalse(scope["execution_authorized"])
        self.assertFalse(scope["feature_work_eligible"])
        self.assertFalse(scope["g2_complete"])
        b._validate_g2_batch_scope(scope)
        for mutate in (
            lambda s: s["allowed_paths"].append("app/not-reviewed.py"),
            lambda s: s["allowed_additions"].append("tests/not-reviewed.py"),
            lambda s: s.update(maximum_changed_files=5),
            lambda s: s["published_audio_repair"].update(commit="0" * 40),
            lambda s: s["published_audio_repair"]["source_sha256"].update(
                {"app/routers/consultation.py": "0" * 64}),
            lambda s: s.update(execution_authorized=True),
            lambda s: s.update(g2_complete=True),
            lambda s: s["owner_test_runtime_exception"].update(admission_grants_runtime_authority=True),
            lambda s: s["claim_limits"].pop(),
        ):
            changed = copy.deepcopy(scope)
            mutate(changed)
            with self.subTest(changed=changed), self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_batch_scope(changed)
            self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_scope_invalid")

    def test_activation_owns_six_and_repair_is_the_exact_four_path_lane(self):
        row = {"before_sha256": "b" * 64, "after_sha256": "c" * 64}
        activation = {
            "schema_version": b.G2_PATIENT_BINDING_VERSION,
            "operation_kind": "enable_g2_patient_binding",
            "repair_sha256": {p: copy.deepcopy(row) for p in b.G2_PATIENT_MAINTENANCE_PATHS},
        }
        self.assertEqual(set(b._batch_changes(activation)), b.G2_PATIENT_MAINTENANCE_PATHS)
        self.assertEqual(len(b.G2_PATIENT_MAINTENANCE_PATHS), 6)
        missing = copy.deepcopy(activation)
        missing["repair_sha256"].pop(b.STATE)
        with self.assertRaises(b.BoundedG1BError) as caught:
            b._batch_changes(missing)
        self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_path_not_allowed")
        repair = {
            "schema_version": b.G2_PATIENT_BINDING_VERSION,
            "operation_kind": "repair_g2_patient_binding",
            "repair_sha256": {p: copy.deepcopy(row) for p in b.G2_PATIENT_PATHS},
        }
        repair["repair_sha256"][b.G2_PATIENT_ADDITION]["before_sha256"] = None
        self.assertEqual(b.operation_paths("repair_g2_patient_binding", repair), b.G2_PATIENT_PATHS)
        self.assertEqual(b.operation_effects("repair_g2_patient_binding"), b.G2_PATIENT_EFFECTS)
        self.assertEqual(b._operation("repair_g2_patient_binding", repair)["limits"], b.G2_PATIENT_LIMITS)
        for path in ("app/main.py", "tests/not-reviewed.py", "../outside.py"):
            invalid = copy.deepcopy(repair)
            invalid["repair_sha256"][path] = invalid["repair_sha256"].pop(b.G2_PATIENT_ADDITION)
            with self.subTest(path=path), self.assertRaises(b.BoundedG1BError) as caught:
                b._batch_changes(invalid)
            self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_path_not_allowed")
        invalid = copy.deepcopy(repair)
        invalid["repair_sha256"]["tests/test_consultation_audio_privacy.py"]["before_sha256"] = None
        with self.assertRaises(b.BoundedG1BError) as caught:
            b._batch_changes(invalid)
        self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_change_digest")
        later_repair = copy.deepcopy(repair)
        later_repair["repair_sha256"][b.G2_PATIENT_ADDITION]["before_sha256"] = "f" * 64
        self.assertEqual(set(b._batch_changes(later_repair)), b.G2_PATIENT_PATHS)

    def test_v1_through_v5_dispatch_compatibility_matrix(self):
        row = {"before_sha256": "1" * 64, "after_sha256": "2" * 64}
        cases = (
            (b.G2_BATCH_BINDING_VERSION, "enable_g2_batches", b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_BATCH_BINDING_VERSION, "repair_g2_batch", {b.G2_FIXTURE}, b.G2_BATCH_EFFECTS),
            (b.G2_CATALOGUE_BINDING_VERSION, "extend_g2_catalogue", b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_CATALOGUE_BINDING_VERSION, "repair_g2_batch",
             {"app/services/ai/service.py"}, b.G2_BATCH_EFFECTS),
            (b.G2_MIGRATION_BINDING_VERSION, "enable_g2_migration", b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_MIGRATION_BINDING_VERSION, "repair_g2_migration",
             {"alembic/versions/d4787e8e3629_phase_0_baseline.py"}, b.G2_MIGRATION_EFFECTS),
            (b.G2_INSTRUCTIONS_BINDING_VERSION, "align_g2_instructions",
             b.G2_INSTRUCTIONS_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_INSTRUCTIONS_BINDING_VERSION, "repair_g2_migration",
             {"alembic/versions/d4787e8e3629_phase_0_baseline.py"}, b.G2_MIGRATION_EFFECTS),
            (b.G2_AUDIO_BINDING_VERSION, "enable_g2_audio_privacy", b.G2_AUDIO_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_AUDIO_BINDING_VERSION, "repair_g2_audio_privacy", {"app/main.py"}, b.G2_AUDIO_EFFECTS),
        )
        for version, kind, paths, effects in cases:
            binding = {"schema_version": version, "operation_kind": kind,
                       "repair_sha256": {p: copy.deepcopy(row) for p in paths}}
            with self.subTest(version=version, kind=kind):
                self.assertEqual(set(b._batch_changes(binding)), set(paths))
                self.assertEqual(set(b.operation_paths(kind, binding)), set(paths))
                self.assertEqual(b.operation_effects(kind), effects)

    def test_v5_cannot_be_relabelled_as_patient_binding(self):
        for operation in ("enable_g2_patient_binding", "repair_g2_patient_binding"):
            binding = {
                "schema_version": b.G2_AUDIO_BINDING_VERSION,
                "operation_kind": operation,
                "repair_sha256": {
                    "orchestration_harness/bounded_g1b.py":
                        {"before_sha256": "d" * 64, "after_sha256": "e" * 64},
                },
            }
            with self.subTest(operation=operation), self.assertRaises(b.BoundedG1BError) as caught:
                b._batch_changes(binding)
            self.assertEqual(caught.exception.reason_code, "bounded_g2_batch_binding_version")

    def test_exact_audio_repair_publication_headers_and_blobs_are_required(self):
        publication = b.G2_AUDIO_REPAIR_PUBLICATION
        raw_by_path = {path: ("authored:" + path).encode() for path in b.G2_AUDIO_REPAIR_SOURCE_SHA256}
        original_sha = b._sha

        def observed_text(_root, *args, **_kwargs):
            if args == ("cat-file", "commit", publication["commit"]):
                return "tree " + publication["tree"] + "\nparent " + publication["parent"] + "\n\nauthored\n"
            if args == ("merge-base", "--is-ancestor", publication["commit"], "f" * 40):
                return ""
            raise AssertionError(args)

        def observed_bytes(_root, *args, **_kwargs):
            prefix = publication["commit"] + ":"
            return raw_by_path[args[2][len(prefix):]]

        digest_by_raw = {raw: b.G2_AUDIO_REPAIR_SOURCE_SHA256[path] for path, raw in raw_by_path.items()}
        with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes), \
                patch.object(b, "_sha", side_effect=lambda raw: digest_by_raw.get(raw, original_sha(raw))):
            b._validate_g2_patient_audio_publication(Path("authored"), "f" * 40)
            raw_by_path["app/routers/consultation.py"] = b"changed"
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_patient_audio_publication(Path("authored"), "f" * 40)
            self.assertEqual(caught.exception.reason_code,
                             "bounded_g2_patient_audio_publication_bytes_changed")


class G2AtomicitySourceContractTests(unittest.TestCase):
    @staticmethod
    def prospective_sources():
        sources = copy.deepcopy(b.G2_ATOMICITY_PREDECESSOR["source_sha256"])
        sources["orchestration_harness/bounded_g1b.py"] = "b" * 64
        sources["orchestration_harness/raisa_policy.py"] = "c" * 64
        sources["tests/test_bounded_g1b.py"] = "d" * 64
        return sources

    def scope(self):
        return b.build_g2_atomicity_scope(
            "2026-09-15T03:00:00+00:00",
            b.G2_PATIENT_REPAIR_PUBLICATION["commit"],
            self.prospective_sources(),
        )

    def test_v7_scope_is_exact_and_keeps_runtime_and_attestation_closed(self):
        scope = self.scope()
        self.assertEqual(scope["schema_version"], b.G2_ATOMICITY_SCOPE_VERSION)
        self.assertEqual(
            scope["transition_base_commit"],
            b.G2_PATIENT_REPAIR_PUBLICATION["commit"],
        )
        self.assertEqual(scope["allowed_paths"], sorted(b.G2_ATOMICITY_PATHS))
        self.assertEqual(scope["allowed_additions"], [b.G2_ATOMICITY_ADDITION])
        self.assertEqual(scope["maximum_changed_files"], 4)
        self.assertEqual(
            scope["prior_patient_activation"],
            {
                "commit": b.G2_ATOMICITY_PREDECESSOR["commit"],
                "scope_sha256": b.G2_ATOMICITY_PREDECESSOR_POLICY[b.G2_SCOPE],
            },
        )
        self.assertEqual(
            scope["published_patient_repair"],
            {
                **b.G2_PATIENT_REPAIR_PUBLICATION,
                "source_sha256": b.G2_PATIENT_REPAIR_SOURCE_SHA256,
            },
        )
        self.assertEqual(scope["claim_limits"], list(b.G2_ATOMICITY_LIMITS))
        self.assertFalse(scope["execution_authorized"])
        self.assertFalse(scope["feature_work_eligible"])
        self.assertFalse(scope["g2_complete"])
        b._validate_g2_batch_scope(scope)
        for mutate in (
            lambda s: s["allowed_paths"].append("app/not-reviewed.py"),
            lambda s: s["allowed_additions"].append("tests/not-reviewed.py"),
            lambda s: s.update(maximum_changed_files=5),
            lambda s: s["prior_patient_activation"].update(commit="0" * 40),
            lambda s: s["published_patient_repair"].update(commit="0" * 40),
            lambda s: s["published_patient_repair"]["source_sha256"].update(
                {"app/routers/consultation.py": "0" * 64}
            ),
            lambda s: s.update(execution_authorized=True),
            lambda s: s.update(g2_complete=True),
            lambda s: s["owner_test_runtime_exception"].update(
                admission_grants_runtime_authority=True
            ),
            lambda s: s["claim_limits"].pop(),
        ):
            changed = copy.deepcopy(scope)
            mutate(changed)
            with self.subTest(changed=changed), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._validate_g2_batch_scope(changed)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_scope_invalid",
            )

    def test_activation_owns_six_and_repair_is_the_exact_four_path_lane(self):
        row = {"before_sha256": "1" * 64, "after_sha256": "2" * 64}
        activation = {
            "schema_version": b.G2_ATOMICITY_BINDING_VERSION,
            "operation_kind": "enable_g2_consultation_atomicity",
            "repair_sha256": {
                p: copy.deepcopy(row) for p in b.G2_ATOMICITY_MAINTENANCE_PATHS
            },
        }
        self.assertEqual(
            set(b._batch_changes(activation)),
            b.G2_ATOMICITY_MAINTENANCE_PATHS,
        )
        self.assertEqual(len(b.G2_ATOMICITY_MAINTENANCE_PATHS), 6)
        missing = copy.deepcopy(activation)
        missing["repair_sha256"].pop(b.STATE)
        with self.assertRaises(b.BoundedG1BError) as caught:
            b._batch_changes(missing)
        self.assertEqual(
            caught.exception.reason_code,
            "bounded_g2_batch_path_not_allowed",
        )

        repair = {
            "schema_version": b.G2_ATOMICITY_BINDING_VERSION,
            "operation_kind": "repair_g2_consultation_atomicity",
            "repair_sha256": {
                p: copy.deepcopy(row) for p in b.G2_ATOMICITY_PATHS
            },
        }
        repair["repair_sha256"][b.G2_ATOMICITY_ADDITION]["before_sha256"] = None
        self.assertEqual(
            set(b._batch_changes(repair)),
            b.G2_ATOMICITY_PATHS,
        )
        self.assertEqual(
            b.operation_paths("repair_g2_consultation_atomicity", repair),
            b.G2_ATOMICITY_PATHS,
        )
        self.assertEqual(
            b.operation_effects("repair_g2_consultation_atomicity"),
            b.G2_ATOMICITY_EFFECTS,
        )
        self.assertEqual(
            b._operation("repair_g2_consultation_atomicity", repair)["limits"],
            b.G2_ATOMICITY_LIMITS,
        )
        for path in ("app/main.py", "tests/not-reviewed.py", "../outside.py"):
            invalid = copy.deepcopy(repair)
            invalid["repair_sha256"][path] = invalid["repair_sha256"].pop(
                b.G2_ATOMICITY_ADDITION
            )
            with self.subTest(path=path), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._batch_changes(invalid)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_path_not_allowed",
            )
        for path in (
            "tests/test_consultation_audio_privacy.py",
            "tests/test_consultation_patient_binding.py",
        ):
            invalid = copy.deepcopy(repair)
            invalid["repair_sha256"][path]["before_sha256"] = None
            with self.subTest(path=path), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._batch_changes(invalid)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_change_digest",
            )

    def test_v1_through_v7_dispatch_compatibility_matrix(self):
        row = {"before_sha256": "3" * 64, "after_sha256": "4" * 64}
        cases = (
            (b.G2_BATCH_BINDING_VERSION, "enable_g2_batches",
             b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_BATCH_BINDING_VERSION, "repair_g2_batch",
             {b.G2_FIXTURE}, b.G2_BATCH_EFFECTS),
            (b.G2_CATALOGUE_BINDING_VERSION, "extend_g2_catalogue",
             b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_CATALOGUE_BINDING_VERSION, "repair_g2_batch",
             {"app/services/ai/service.py"}, b.G2_BATCH_EFFECTS),
            (b.G2_MIGRATION_BINDING_VERSION, "enable_g2_migration",
             b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_MIGRATION_BINDING_VERSION, "repair_g2_migration",
             {"alembic/versions/d4787e8e3629_phase_0_baseline.py"},
             b.G2_MIGRATION_EFFECTS),
            (b.G2_INSTRUCTIONS_BINDING_VERSION, "align_g2_instructions",
             b.G2_INSTRUCTIONS_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_INSTRUCTIONS_BINDING_VERSION, "repair_g2_migration",
             {"alembic/versions/d4787e8e3629_phase_0_baseline.py"},
             b.G2_MIGRATION_EFFECTS),
            (b.G2_AUDIO_BINDING_VERSION, "enable_g2_audio_privacy",
             b.G2_AUDIO_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_AUDIO_BINDING_VERSION, "repair_g2_audio_privacy",
             {"app/main.py"}, b.G2_AUDIO_EFFECTS),
            (b.G2_PATIENT_BINDING_VERSION, "enable_g2_patient_binding",
             b.G2_PATIENT_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_PATIENT_BINDING_VERSION, "repair_g2_patient_binding",
             {"app/routers/consultation.py"}, b.G2_PATIENT_EFFECTS),
            (b.G2_ATOMICITY_BINDING_VERSION,
             "enable_g2_consultation_atomicity",
             b.G2_ATOMICITY_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_ATOMICITY_BINDING_VERSION,
             "repair_g2_consultation_atomicity",
             {"app/routers/consultation.py"}, b.G2_ATOMICITY_EFFECTS),
        )
        for version, kind, paths, effects in cases:
            binding = {
                "schema_version": version,
                "operation_kind": kind,
                "repair_sha256": {
                    p: copy.deepcopy(row) for p in paths
                },
            }
            with self.subTest(version=version, kind=kind):
                self.assertEqual(set(b._batch_changes(binding)), set(paths))
                self.assertEqual(
                    set(b.operation_paths(kind, binding)),
                    set(paths),
                )
                self.assertEqual(b.operation_effects(kind), effects)

    def test_v6_cannot_be_relabelled_as_atomicity(self):
        for operation in (
            "enable_g2_consultation_atomicity",
            "repair_g2_consultation_atomicity",
        ):
            binding = {
                "schema_version": b.G2_PATIENT_BINDING_VERSION,
                "operation_kind": operation,
                "repair_sha256": {
                    "orchestration_harness/bounded_g1b.py": {
                        "before_sha256": "5" * 64,
                        "after_sha256": "6" * 64,
                    },
                },
            }
            with self.subTest(operation=operation), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._batch_changes(binding)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_binding_version",
            )

    def test_exact_patient_repair_publication_headers_and_blobs_are_required(self):
        publication = b.G2_PATIENT_REPAIR_PUBLICATION
        raw_by_path = {
            path: ("authored:" + path).encode()
            for path in b.G2_PATIENT_REPAIR_SOURCE_SHA256
        }
        original_sha = b._sha

        def observed_text(_root, *args, **_kwargs):
            if args == ("cat-file", "commit", publication["commit"]):
                return (
                    "tree " + publication["tree"] + "\nparent "
                    + publication["parent"] + "\n\nauthored\n"
                )
            if args == (
                "merge-base", "--is-ancestor", publication["commit"], "f" * 40
            ):
                return ""
            raise AssertionError(args)

        def observed_bytes(_root, *args, **_kwargs):
            prefix = publication["commit"] + ":"
            return raw_by_path[args[2][len(prefix):]]

        digest_by_raw = {
            raw: b.G2_PATIENT_REPAIR_SOURCE_SHA256[path]
            for path, raw in raw_by_path.items()
        }
        with patch.object(
            b.trusted_git, "run_git", side_effect=observed_text
        ), patch.object(
            b.trusted_git, "run_git_bytes", side_effect=observed_bytes
        ), patch.object(
            b, "_sha",
            side_effect=lambda raw: digest_by_raw.get(raw, original_sha(raw)),
        ):
            b._validate_g2_atomicity_patient_publication(
                Path("authored"), "f" * 40
            )

        with patch.object(
            b.trusted_git,
            "run_git",
            return_value="tree " + "0" * 40,
        ):
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_atomicity_patient_publication(
                    Path("authored"), "f" * 40
                )
        self.assertEqual(
            caught.exception.reason_code,
            "bounded_g2_batch_publication_invalid",
        )

        raw_by_path["app/routers/consultation.py"] = b"changed"
        with patch.object(
            b.trusted_git, "run_git", side_effect=observed_text
        ), patch.object(
            b.trusted_git, "run_git_bytes", side_effect=observed_bytes
        ), patch.object(
            b, "_sha",
            side_effect=lambda raw: digest_by_raw.get(raw, original_sha(raw)),
        ):
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_atomicity_patient_publication(
                    Path("authored"), "f" * 40
                )
        self.assertEqual(
            caught.exception.reason_code,
            "bounded_g2_atomicity_patient_publication_bytes_changed",
        )


class G2ClinicalSourceContractTests(unittest.TestCase):
    @staticmethod
    def prospective_sources():
        sources = copy.deepcopy(b.G2_CLINICAL_PREDECESSOR["source_sha256"])
        sources["orchestration_harness/bounded_g1b.py"] = "b" * 64
        sources["orchestration_harness/raisa_policy.py"] = "c" * 64
        sources["tests/test_bounded_g1b.py"] = "d" * 64
        return sources

    def scope(self):
        return b.build_g2_clinical_scope(
            "2026-09-15T06:00:00+00:00",
            b.G2_ATOMICITY_REPAIR_PUBLICATION["commit"],
            self.prospective_sources(),
        )

    def test_v8_scope_binds_owner_contract_and_published_atomicity_without_runtime(self):
        scope = self.scope()
        self.assertEqual(scope["schema_version"], b.G2_CLINICAL_SCOPE_VERSION)
        self.assertEqual(
            scope["transition_base_commit"],
            b.G2_ATOMICITY_REPAIR_PUBLICATION["commit"],
        )
        self.assertEqual(scope["allowed_paths"], sorted(b.G2_CLINICAL_PATHS))
        self.assertEqual(scope["allowed_additions"], [])
        self.assertEqual(scope["maximum_changed_files"], 6)
        self.assertEqual(
            scope["prior_atomicity_activation"],
            {
                "commit": b.G2_CLINICAL_PREDECESSOR["commit"],
                "scope_sha256": b.G2_CLINICAL_PREDECESSOR_POLICY[b.G2_SCOPE],
            },
        )
        self.assertEqual(
            scope["published_atomicity_repair"],
            {
                **b.G2_ATOMICITY_REPAIR_PUBLICATION,
                "source_sha256": b.G2_ATOMICITY_REPAIR_SOURCE_SHA256,
            },
        )
        self.assertEqual(
            scope["clinical_authority_contract"],
            rp.g2_clinical_authority_contract(),
        )
        self.assertEqual(scope["claim_limits"], list(b.G2_CLINICAL_LIMITS))
        self.assertFalse(scope["execution_authorized"])
        self.assertFalse(scope["feature_work_eligible"])
        self.assertFalse(scope["g2_complete"])
        b._validate_g2_batch_scope(scope)
        stale_contract = copy.deepcopy(scope["clinical_authority_contract"])
        stale_contract["source_revision"] = 2
        with patch.object(
            rp, "g2_clinical_authority_contract", return_value=stale_contract
        ), self.assertRaises(b.BoundedG1BError) as caught:
            self.scope()
        self.assertEqual(
            caught.exception.reason_code,
            "bounded_g2_clinical_source_revision",
        )
        for mutate in (
            lambda s: s["allowed_paths"].append("app/not-reviewed.py"),
            lambda s: s["allowed_additions"].append("tests/not-reviewed.py"),
            lambda s: s.update(maximum_changed_files=7),
            lambda s: s["prior_atomicity_activation"].update(commit="0" * 40),
            lambda s: s["published_atomicity_repair"].update(commit="0" * 40),
            lambda s: s["clinical_authority_contract"].update(
                roles=["GP", "NURSE"]
            ),
            lambda s: s["clinical_authority_contract"].update(source_revision=2),
            lambda s: s["clinical_authority_contract"]["typed_finalization_request"]["document_id"].update(
                distinct_from_word_document_identity=False
            ),
            lambda s: s["clinical_authority_contract"]["typed_finalization_request"]["document_context"].update(
                url_max_length=2049
            ),
            lambda s: s["clinical_authority_contract"]["typed_finalization_request"]["document_context"].update(
                strip_or_normalize_url=True
            ),
            lambda s: s["clinical_authority_contract"]["typed_finalization_request"]["declared_aliases"].update(
                both_present="prefer_canonical"
            ),
            lambda s: s["clinical_authority_contract"]["attestation_transport"].update(
                type="coerced_boolean"
            ),
            lambda s: s["clinical_authority_contract"]["authority_transaction"].update(
                postgresql_isolation_level="SERIALIZABLE"
            ),
            lambda s: s["clinical_authority_contract"]["authority_transaction"]["integrity_conflict_handling"].update(
                automatic_retry=True
            ),
            lambda s: s["clinical_authority_contract"]["practitioner_attribution"].update(
                **{"MbsClaim.practitioner_id": "client_practitioner_id"}
            ),
            lambda s: s["clinical_authority_contract"]["attestation_audit"]["metadata_keys"].remove(
                "reviewed_content_sha256"
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["storage"].update(
                existing_database_unique_constraint=False
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["event_id"].update(
                canonical_name="{canonical_practice_uuid}:{canonical_document_id_uuid}"
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["receipt_fields"]["metadata"].update(
                attested=1
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["target_validation"].update(
                status="draft"
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["matching_content_replay"].update(
                additional_audit_writes=True
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["mismatch_or_corruption"].update(
                status=200
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                bounded_finalization_path_never_updates_or_deletes_receipt=False
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                database_immutability_enforced=True
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                database_retention_enforced=True
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                receipt_retention_required_for_replay=False
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                receipt_loss_or_undetectable_mutation_outside_accepted_guarantee=False
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                detectable_receipt_or_target_corruption="accept"
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                known_receipt_loss_or_mutation="retry_automatically"
            ),
            lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(
                production_durable_idempotency_accepted=True
            ),
            lambda s: s["clinical_authority_contract"]["canonical_saved_projection"]["same_projection_for"].remove(
                "matching_replay_response"
            ),
            lambda s: s["clinical_authority_contract"]["canonical_saved_projection"]["successful_response"].update(
                matching_replay_is_exactly_equal=False
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["per_start_binding"]["boundary_markers"].update(
                uuid_bound_end_marker=False
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["per_start_binding"]["boundary_markers"].update(
                date_or_age_prose_is_never_a_boundary=False
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["per_start_binding"]["boundary_markers"].update(
                fail_closed_if_end_missing_duplicate_invalid_or_crosses_section=False
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["command_centre_interlock"].update(
                taskpane_finalization_blocked_while_command_centre_open=False
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["confirmed_response"].update(
                empty_or_arbitrary_string="accept"
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["patient_document_url_getter"].update(
                fallback_or_synthetic_url=True
            ),
            lambda s: s["clinical_authority_contract"]["taskpane_confirmation"]["ambiguous_retry"].update(
                fresh_confirmation_required=False
            ),
            lambda s: s["clinical_authority_contract"]["synthetic_staff_practitioners_and_patients_standing_authority"]["permitted_entities"].remove(
                "fictional_practitioners"
            ),
            lambda s: s.update(execution_authorized=True),
            lambda s: s["claim_limits"].pop(),
        ):
            changed = copy.deepcopy(scope)
            mutate(changed)
            with self.subTest(changed=changed), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._validate_g2_batch_scope(changed)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_scope_invalid",
            )

    def test_activation_and_repair_each_own_exactly_six_existing_paths(self):
        row = {"before_sha256": "1" * 64, "after_sha256": "2" * 64}
        activation = {
            "schema_version": b.G2_CLINICAL_BINDING_VERSION,
            "operation_kind": "enable_g2_clinical_authority",
            "repair_sha256": {
                p: copy.deepcopy(row)
                for p in b.G2_CLINICAL_MAINTENANCE_PATHS
            },
        }
        self.assertEqual(
            set(b._batch_changes(activation)),
            b.G2_CLINICAL_MAINTENANCE_PATHS,
        )
        self.assertEqual(len(b.G2_CLINICAL_MAINTENANCE_PATHS), 6)

        repair = {
            "schema_version": b.G2_CLINICAL_BINDING_VERSION,
            "operation_kind": "repair_g2_clinical_authority",
            "repair_sha256": {
                p: copy.deepcopy(row) for p in b.G2_CLINICAL_PATHS
            },
        }
        self.assertEqual(set(b._batch_changes(repair)), b.G2_CLINICAL_PATHS)
        self.assertEqual(len(b.G2_CLINICAL_PATHS), 6)
        self.assertEqual(
            b.operation_paths("repair_g2_clinical_authority", repair),
            b.G2_CLINICAL_PATHS,
        )
        self.assertEqual(
            b.operation_effects("repair_g2_clinical_authority"),
            b.G2_BATCH_EFFECTS,
        )
        self.assertEqual(
            b._operation("repair_g2_clinical_authority", repair)["limits"],
            b.G2_CLINICAL_LIMITS,
        )
        for path in b.G2_CLINICAL_PATHS:
            invalid = copy.deepcopy(repair)
            invalid["repair_sha256"][path]["before_sha256"] = None
            with self.subTest(path=path), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._batch_changes(invalid)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_change_digest",
            )

    def test_v1_through_v8_dispatch_remains_compatible(self):
        row = {"before_sha256": "3" * 64, "after_sha256": "4" * 64}
        cases = (
            (b.G2_BATCH_BINDING_VERSION, "enable_g2_batches",
             b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_BATCH_BINDING_VERSION, "repair_g2_batch",
             {b.G2_FIXTURE}, b.G2_BATCH_EFFECTS),
            (b.G2_CATALOGUE_BINDING_VERSION, "extend_g2_catalogue",
             b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_CATALOGUE_BINDING_VERSION, "repair_g2_batch",
             {"app/services/ai/service.py"}, b.G2_BATCH_EFFECTS),
            (b.G2_MIGRATION_BINDING_VERSION, "enable_g2_migration",
             b.G2_BATCH_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_MIGRATION_BINDING_VERSION, "repair_g2_migration",
             {"alembic/versions/d4787e8e3629_phase_0_baseline.py"},
             b.G2_MIGRATION_EFFECTS),
            (b.G2_INSTRUCTIONS_BINDING_VERSION, "align_g2_instructions",
             b.G2_INSTRUCTIONS_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_INSTRUCTIONS_BINDING_VERSION, "repair_g2_migration",
             {"alembic/versions/d4787e8e3629_phase_0_baseline.py"},
             b.G2_MIGRATION_EFFECTS),
            (b.G2_AUDIO_BINDING_VERSION, "enable_g2_audio_privacy",
             b.G2_AUDIO_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_AUDIO_BINDING_VERSION, "repair_g2_audio_privacy",
             {"app/main.py"}, b.G2_AUDIO_EFFECTS),
            (b.G2_PATIENT_BINDING_VERSION, "enable_g2_patient_binding",
             b.G2_PATIENT_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_PATIENT_BINDING_VERSION, "repair_g2_patient_binding",
             {"app/routers/consultation.py"}, b.G2_PATIENT_EFFECTS),
            (b.G2_ATOMICITY_BINDING_VERSION,
             "enable_g2_consultation_atomicity",
             b.G2_ATOMICITY_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_ATOMICITY_BINDING_VERSION,
             "repair_g2_consultation_atomicity",
             {"app/routers/consultation.py"}, b.G2_ATOMICITY_EFFECTS),
            (b.G2_CLINICAL_BINDING_VERSION,
             "enable_g2_clinical_authority",
             b.G2_CLINICAL_MAINTENANCE_PATHS, b.EFFECTS),
            (b.G2_CLINICAL_BINDING_VERSION,
             "repair_g2_clinical_authority",
             b.G2_CLINICAL_PATHS, b.G2_BATCH_EFFECTS),
        )
        for version, kind, paths, effects in cases:
            binding = {
                "schema_version": version,
                "operation_kind": kind,
                "repair_sha256": {
                    p: copy.deepcopy(row) for p in paths
                },
            }
            with self.subTest(version=version, kind=kind):
                self.assertEqual(set(b._batch_changes(binding)), set(paths))
                self.assertEqual(set(b.operation_paths(kind, binding)), set(paths))
                self.assertEqual(b.operation_effects(kind), effects)

    def test_v7_cannot_be_relabelled_as_clinical_authority(self):
        for operation in (
            "enable_g2_clinical_authority",
            "repair_g2_clinical_authority",
        ):
            binding = {
                "schema_version": b.G2_ATOMICITY_BINDING_VERSION,
                "operation_kind": operation,
                "repair_sha256": {
                    "orchestration_harness/bounded_g1b.py": {
                        "before_sha256": "5" * 64,
                        "after_sha256": "6" * 64,
                    },
                },
            }
            with self.subTest(operation=operation), self.assertRaises(
                b.BoundedG1BError
            ) as caught:
                b._batch_changes(binding)
            self.assertEqual(
                caught.exception.reason_code,
                "bounded_g2_batch_binding_version",
            )

    def test_owner_contract_and_atomicity_publication_are_exact(self):
        profile = rp.g2_clinical_authority_profile()
        contract = rp.g2_clinical_authority_contract()
        self.assertEqual(b.G2_CLINICAL_SOURCE_REVISION, 4)
        self.assertEqual(contract["semantic_version"], "v8")
        self.assertEqual(contract["source_revision"], 4)
        self.assertEqual(contract["roles"], ["GP"])
        for key in (
            "active_authenticated_user_required",
            "active_linked_same_practice_practitioner_required",
            "explicit_clinician_attestation_required",
            "server_owned_practitioner_and_prescriber_identity",
            "no_administrative_or_nurse_bypass",
            "fresh_command_transaction_authority_recheck_required",
            "clinical_rows_and_typed_attestation_audit_one_commit",
        ):
            self.assertIs(contract[key], True)
        for key in (
            "raw_clinical_text_in_audit_metadata",
            "admission_grants_runtime_authority",
            "real_clinical_operation_authorized",
            "g2_completion_claimed",
        ):
            self.assertIs(contract[key], False)
        self.assertEqual(contract["typed_finalization_request"], {
            "nested_dto_extra_fields": "forbid",
            "strings": "strict_nonblank_required_without_coercion",
            "declared_aliases": {
                "both_present": "require_exact_equal_values",
                "conflict": "reject_422",
                "implicit_or_undeclared_aliases": False,
            },
            "document_id": {
                "type": "canonical_uuid_string", "required": True,
                "client_generated_per_start": True,
                "distinct_from_word_document_identity": True,
                "word_identity_confers_command_authority": False,
            },
            "document_context": {
                "required": True, "extra_fields": "forbid",
                "url": "strict_nonblank_string", "url_scheme": "http_or_https",
                "url_max_length": 2048, "strip_or_normalize_url": False,
                "must_exactly_match_freshly_locked_Patient.document_url": True,
            },
            "maximum_lengths": {
                "clinical_text": 100000, "consultation_type": 255,
                "mbs_item_number": 10, "mbs_description": 2048,
                "diagnosis_term": 255, "diagnosis_code": 50,
                "medication_drug": 255, "medication_dose": 2048,
            },
            "maximum_items_per_nested_list": 100,
        })
        self.assertEqual(contract["attestation_transport"], {
            "field": "clinician_attested", "required": True,
            "type": "strict_json_boolean", "only_literal_true_authorizes": True,
            "missing_or_non_boolean": "reject_422", "false": "reject_403_before_clinical_writes",
            "client_role_or_practitioner_fields_confer_authority": False,
        })
        self.assertEqual(contract["authority_transaction"], {
            "fresh_command_owned_session": True,
            "postgresql_isolation_level": "READ COMMITTED",
            "transaction_local_practice_context": True,
            "lock_and_recheck_order": ["User", "Practitioner", "Patient"],
            "locks_held_through_receipt_clinical_and_audit_commit": True,
            "authorization_and_document_binding_before_writes": True,
            "preallocate_Encounter_uuid_before_receipt": True,
            "flush_unique_receipt_before_clinical_rows": True,
            "receipt_and_clinical_rows_one_transaction": True,
            "provider_or_await_work_inside_transaction": False,
            "integrity_conflict_handling": {
                "rollback_before_classification": True,
                "fresh_scope_recheck_after_rollback": True,
                "automatic_retry": False,
            },
        })
        self.assertEqual(contract["practitioner_attribution"], {
            "source": "fresh_active_same_practice_User.practitioner_id",
            "Encounter.practitioner_id": "server_resolved_Practitioner.id",
            "Prescription.prescribed_by": "server_resolved_Practitioner.id",
            "MbsClaim.practitioner_id": "server_resolved_Practitioner.id",
            "MbsClaim.Submitted": "internal_synthetic_database_state_only",
            "real_billing_submission_policy_accepted": False,
        })
        self.assertEqual(contract["attestation_audit"], {
            "event_type": "clinical.consultation.attested", "decision": "recorded",
            "source_surface": "api", "capability": None, "method": None,
            "ai_invocation_claimed": False,
            "typed_fields": ["event_id", "correlation_id", "actor_user_id", "actor_roles",
                             "practice_id", "event_timestamp", "event_type", "decision",
                             "source_surface", "capability", "method",
                             "target_resource_type", "target_resource_id"],
            "target_resource_type": "encounter",
            "metadata_keys": ["attested", "normalization_policy_id", "patient_id",
                              "practitioner_id", "reviewed_content_sha256", "server_policy_id"],
            "metadata_type_equality": "strict_including_attested_is_True_not_1_equals_True",
            "server_policy_id": "emr4.clinical-finalization.gp-linked-practitioner.v1",
            "normalization_policy_id": "emr4.clinical-finalization.saved-projection.v1",
            "content_hash": "server_sha256_sorted_compact_utf8_json_effective_saved_projection",
            "client_hash_accepted": False,
            "raw_clinical_text_or_document_url_metadata": False,
            "audit_failure_rolls_back_all_clinical_rows": True,
        })
        receipt = contract["idempotency_receipt"]
        self.assertEqual(receipt["storage"], {
            "model": "AccessAiAuditLog", "unique_column": "event_id",
            "existing_database_unique_constraint": True,
        })
        self.assertEqual(receipt["event_id"], {
            "algorithm": "server_uuidv5",
            "namespace_uuid": "7b56fb23-fdc5-5bd9-951f-80a7b9b94b2e",
            "name_prefix": "emr4.clinical-finalization.receipt.v1",
            "canonical_name": "{name_prefix}:{canonical_practice_uuid}:{canonical_document_id_uuid}",
            "client_event_id_accepted": False,
        })
        self.assertEqual(receipt["command_document_id"],
                         "canonical_uuid_distinct_from_word_identity")
        self.assertEqual(receipt["typed_field_requirements"], {
            "event_id": "UUID", "correlation_id": "UUID",
            "event_timestamp": "timezone_aware_datetime",
            "capability": None, "method": None,
        })
        self.assertEqual(receipt["receipt_fields"], {
            "event_id": "server_uuidv5_receipt_event_id",
            "correlation_id": "canonical_document_id_uuid",
            "actor_user_id": "fresh_authenticated_User.id",
            "actor_roles": ["GP"],
            "practice_id": "fresh_transaction_practice_id",
            "event_timestamp": "timezone_aware_server_timestamp",
            "event_type": "clinical.consultation.attested",
            "decision": "recorded", "source_surface": "api",
            "capability": None, "method": None,
            "target_resource_type": "encounter",
            "target_resource_id": "preallocated_Encounter.id",
            "metadata": {
                "attested": True,
                "normalization_policy_id": "emr4.clinical-finalization.saved-projection.v1",
                "patient_id": "freshly_locked_Patient.id",
                "practitioner_id": "freshly_locked_Practitioner.id",
                "reviewed_content_sha256": "server_computed_canonical_projection_hash",
                "server_policy_id": "emr4.clinical-finalization.gp-linked-practitioner.v1",
            },
        })
        self.assertEqual(receipt["target_validation"], {
            "resource_must_be_finalized_Encounter": True,
            "matched_core_fields": ["id", "practice_id", "patient_id",
                                    "practitioner_id", "status"],
            "status": "finalized",
            "command_id_must_match_correlation_id": True,
            "actor_practice_patient_practitioner_and_hash_must_match": True,
            "metadata_values_and_types_must_match": True,
        })
        self.assertEqual(receipt["matching_content_replay"], {
            "same_response_projection": True,
            "additional_clinical_writes": False,
            "additional_audit_writes": False,
        })
        self.assertEqual(receipt["mismatch_or_corruption"], {
            "status": 409, "generic_indistinguishable_response": True,
        })
        self.assertEqual(receipt["retention_and_schema"], {
            "bounded_finalization_path_never_updates_or_deletes_receipt": True,
            "database_immutability_enforced": False,
            "database_retention_enforced": False,
            "receipt_retention_required_for_replay": True,
            "receipt_loss_or_undetectable_mutation_outside_accepted_guarantee": True,
            "detectable_receipt_or_target_corruption": "generic_409_no_writes",
            "known_receipt_loss_or_mutation": "stop_no_retry_pending_separate_repair_and_review",
            "schema_migration_required": False,
            "guarantee_scope": "bounded_synthetic_retained_records_only",
            "production_durable_idempotency_accepted": False,
        })
        self.assertEqual(contract["canonical_saved_projection"], {
            "built_once_after_strict_validation": True,
            "normalization_policy_id": "emr4.clinical-finalization.saved-projection.v1",
            "hash_projection_fields": ["normalization_policy_id", "patient_id",
                                       "document_id", "exact_document_context",
                                       "effective_consultation_type", "clinical_text",
                                       "canonical_child_dtos"],
            "same_projection_for": ["clinical_row_values", "reviewed_content_sha256",
                                    "successful_response", "matching_replay_response"],
            "successful_response": {
                "_saved": True,
                "fields": ["encounter_id", "generated_clinical_note"],
                "matching_replay_is_exactly_equal": True,
            },
            "raw_clinical_text_or_document_url_in_audit": False,
        })
        self.assertEqual(contract["taskpane_confirmation"], {
            "explicit_personal_clinician_review_and_authorization": True,
            "ai_does_not_authorize": True,
            "invalidate_prior_binding_before_patient_await": True,
            "per_start_binding": {
                "new_full_canonical_document_id_uuid": True,
                "exact_document_context_url": True,
                "boundary_markers": {
                    "uuid_bound_start_marker": True,
                    "uuid_bound_end_marker": True,
                    "same_document_id_uuid_required": True,
                    "insert_both_for_each_new_consult": True,
                    "paragraph_selection": "all_and_only_strictly_between_exact_markers",
                    "date_or_age_prose_is_never_a_boundary": True,
                    "fail_closed_if_end_missing_duplicate_invalid_or_crosses_section": True,
                    "legacy_regex_fallback_for_new_consults": False,
                },
            },
            "command_centre_interlock": {
                "opening_blocked_while": ["consultation_start",
                                          "consultation_finalization",
                                          "ambiguous_submitted_snapshot"],
                "taskpane_finalization_blocked_while_command_centre_open": True,
            },
            "confirmed_response": {
                "encounter_id": "canonical_uuid_string",
                "empty_or_arbitrary_string": "reject",
            },
            "patient_document_url_getter": {
                "real_getter_required": True,
                "fallback_or_synthetic_url": False,
                "failure": "cancel_without_request",
            },
            "one_shot_confirmation_of_exact_request_snapshot": True,
            "second_word_and_form_read_after_confirmation": True,
            "second_read_mismatch": "cancel_without_request",
            "per_binding_in_flight_guard": True,
            "reusable_attestation_state": False,
            "patient_or_reviewed_content_change_requires_fresh_confirmation": True,
            "patient_or_session_change_during_word_read_cancels_request": True,
            "cancel_or_unavailable_confirmation_sends_nothing": True,
            "ambiguous_retry": {
                "same_exact_command_snapshot_required": True,
                "fresh_confirmation_required": True,
                "silent_or_automatic_retry": False,
            },
        })
        fixtures = contract["synthetic_staff_practitioners_and_patients_standing_authority"]
        self.assertIs(fixtures["persistent"], True)
        self.assertEqual(fixtures["permitted_entities"],
                         ["fictional_staff", "fictional_practitioners", "fictional_patients"])
        self.assertIs(fixtures["fictional_entities_only"], True)
        self.assertIs(fixtures["ai_is_clinician_or_attester"], False)
        self.assertIs(fixtures["real_identity_or_professional_credential_claim"], False)
        self.assertIs(fixtures["existing_independent_review_and_finite_runtime_budgets_preserved"], True)
        self.assertEqual(
            profile["scope_behavior"],
            "bounded_g2_clinical_authority_repair",
        )
        self.assertEqual(
            profile["allowed_paths"], sorted(b.G2_CLINICAL_PATHS)
        )
        self.assertEqual(
            contract["owner_decision"]["evidence_path"],
            rp.G2_CLINICAL_OWNER_RECORD,
        )
        self.assertEqual(
            contract["owner_decision"]["sha256"],
            rp.G2_CLINICAL_OWNER_SHA256,
        )

        original_sha = b._sha
        publication_raw = {
            p: ("publication:" + p).encode()
            for p in b.G2_ATOMICITY_REPAIR_SOURCE_SHA256
        }
        digest_by_raw = {
            raw: b.G2_ATOMICITY_REPAIR_SOURCE_SHA256[path]
            for path, raw in publication_raw.items()
        }

        def observed_text(_root, *args, **_kwargs):
            for declared in (b.G2_ATOMICITY_REPAIR_PUBLICATION,):
                if args == ("cat-file", "commit", declared["commit"]):
                    return (
                        "tree " + declared["tree"] + "\nparent "
                        + declared["parent"] + "\n\nauthored\n"
                    )
                if args == (
                    "merge-base", "--is-ancestor", declared["commit"], "f" * 40
                ):
                    return ""
            raise AssertionError(args)

        def observed_bytes(_root, *args, **_kwargs):
            commit_path = args[2]
            commit, path = commit_path.split(":", 1)
            if commit == b.G2_ATOMICITY_REPAIR_PUBLICATION["commit"]:
                return publication_raw[path]
            raise AssertionError(args)

        with patch.object(
            b.trusted_git, "run_git", side_effect=observed_text
        ), patch.object(
            b.trusted_git, "run_git_bytes", side_effect=observed_bytes
        ), patch.object(
            b, "_sha",
            side_effect=lambda raw: digest_by_raw.get(raw, original_sha(raw)),
        ):
            b._validate_g2_clinical_atomicity_publication(
                Path("authored"), "f" * 40
            )

        publication_raw["app/routers/consultation.py"] = b"changed"
        with patch.object(
            b.trusted_git, "run_git", side_effect=observed_text
        ), patch.object(
            b.trusted_git, "run_git_bytes", side_effect=observed_bytes
        ), patch.object(
            b, "_sha",
            side_effect=lambda raw: digest_by_raw.get(raw, original_sha(raw)),
        ):
            with self.assertRaises(b.BoundedG1BError) as caught:
                b._validate_g2_clinical_atomicity_publication(
                    Path("authored"), "f" * 40
                )
        self.assertEqual(
            caught.exception.reason_code,
            "bounded_g2_clinical_atomicity_publication_bytes_changed",
        )


class G2AudioFixture(G2MigrationFixture):
    """Authored v5 activation over exact v4, trusted-Git, and instruction history."""
    MAIN = "app/main.py"
    CONSULTATION = "app/routers/consultation.py"
    SIDEBAR = "EMR4 Sidebar/src/taskpane/taskpane.js"
    TEST = "tests/test_consultation_audio_privacy.py"

    def __init__(self, assets):
        super().__init__(assets)
        self.audio_previous_policy = {
            p: (assets / "g2-audio-predecessor-policy" / p).read_bytes()
            for p in b.G2_AUDIO_PREDECESSOR_POLICY}
        self.audio_previous_source = {
            p: (assets / "g2-audio-predecessor-source" / p).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        self.instruction_previous_policy = {
            p: (assets / "g2-migration-published-policy" / p).read_bytes()
            for p in b.G2_INSTRUCTIONS_PREDECESSOR_POLICY}
        self.instruction_previous_source = {
            p: (self.source / "g2-migration-installed-source" / p).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        self.old_published_instructions = (
            assets / "g2-instructions-published-policy" / b.AGENTS).read_bytes()
        self.current_instructions = (
            assets / "g2-audio-instructions-publication" / b.AGENTS).read_bytes()
        self.trusted_git_publication_source = {
            p: (assets / "g2-audio-trusted-git-publication" / p).read_bytes()
            for p in b.G2_AUDIO_TRUSTED_GIT_SOURCE_SHA256}
        product = {
            self.MAIN: b"# authored application baseline; never imported\n",
            self.CONSULTATION: b"# authored consultation baseline; never imported\n",
            self.SIDEBAR: b"// authored sidebar baseline; never executed\n",
        }
        previous = {**self.audio_previous_policy, **self.audio_previous_source, **product}
        for path, raw in previous.items():
            self.write(path, raw)
        test_path = self.root / self.TEST
        if test_path.exists():
            test_path.unlink()
        self.git("add", "--", *sorted(previous))
        self.git("rm", "--cached", "--ignore-unmatch", "--", self.TEST)
        prior_tree = self.git("write-tree")
        prior = self.git("commit-tree", prior_tree, "-p", self.base, "-m", "authored installed v4 baseline")
        for path, raw in self.trusted_git_publication_source.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(self.trusted_git_publication_source))
        trusted_tree = self.git("write-tree")
        trusted = self.git("commit-tree", trusted_tree, "-p", prior, "-m", "authored trusted Git successor")
        self.write(b.AGENTS, self.current_instructions)
        self.git("add", "--", b.AGENTS)
        base_tree = self.git("write-tree")
        base = self.git("commit-tree", base_tree, "-p", trusted, "-m", "authored current instructions")
        self.git("update-ref", "--no-deref", "HEAD", base)
        self.base = base
        sources = {p: b._sha((self.source / p).read_bytes()) for p in b.CONTROLLER_PATHS}
        self.batch_scope = b.build_g2_audio_scope("2026-09-14T14:30:00+00:00", base, sources)
        after = b.build_g2_audio_transition(
            {p: self.audio_previous_policy[p] for p in b.G2_BATCH_CONTROL_PATHS}, self.batch_scope)
        after.update({p: (self.source / p).read_bytes() for p in b.G2_BATCH_CODE_PATHS})
        changes = {p: {"before_sha256": b._sha((self.root / p).read_bytes()),
                       "after_sha256": b._sha(raw)} for p, raw in after.items()}
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(
            schema_version=b.G2_AUDIO_BINDING_VERSION,
            operation_id="authored-g2-audio-activation",
            operation_kind="enable_g2_audio_privacy",
            phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=tree, candidate_tree=tree,
            activation_commit=b.G2_AUDIO_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(b.G2_AUDIO_PREDECESSOR),
            repair_sha256=changes,
            source_sha256={p: b._sha((self.source / p).read_bytes()) for p in b.SOURCE_PATHS},
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}

    @contextmanager
    def component_history(self):
        with super().component_history():
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            declarations = (
                b.G2_INSTRUCTIONS_PREDECESSOR, b.G2_INSTRUCTIONS_PUBLICATION,
                b.G2_AUDIO_PREDECESSOR, b.G2_AUDIO_TRUSTED_GIT_PUBLICATION,
                b.G2_AUDIO_INSTRUCTIONS_PUBLICATION,
            )
            predecessor_files = {
                b.G2_INSTRUCTIONS_PREDECESSOR["commit"]:
                    {**self.instruction_previous_policy, **self.instruction_previous_source},
                b.G2_AUDIO_PREDECESSOR["commit"]:
                    {**self.audio_previous_policy, **self.audio_previous_source},
                b.G2_AUDIO_TRUSTED_GIT_PUBLICATION["commit"]: self.trusted_git_publication_source,
            }

            def observed_text(root, *args, **kwargs):
                for declared in declarations:
                    if root == self.root and args == ("cat-file", "commit", declared["commit"]):
                        return ("tree " + declared["tree"] + "\nparent " + declared["parent"]
                                + "\n\nauthored fixed history\n")
                    if root == self.root and args == (
                            "merge-base", "--is-ancestor", declared["commit"], self.q["base_commit"]):
                        return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for commit, files in predecessor_files.items():
                    for path, raw in files.items():
                        if root == self.root and args == ("cat-file", "blob", commit + ":" + path):
                            return raw
                publication = b.G2_INSTRUCTIONS_PUBLICATION
                if root == self.root and args == ("cat-file", "blob", publication["commit"] + ":" + b.AGENTS):
                    return self.old_published_instructions
                if root == self.root and args == ("cat-file", "blob", publication["parent"] + ":" + b.AGENTS):
                    return self.instruction_previous_policy[b.AGENTS]
                publication = b.G2_AUDIO_INSTRUCTIONS_PUBLICATION
                if root == self.root and args == ("cat-file", "blob", publication["parent"] + ":" + b.AGENTS):
                    return self.audio_previous_policy[b.AGENTS]
                if root == self.root and args == ("cat-file", "blob", publication["commit"] + ":" + b.AGENTS):
                    return self.current_instructions
                return run_bytes(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                    patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
                yield

    def prepare_audio(self, changes):
        base = self.git("rev-parse", "HEAD")
        base_tree = self.git("rev-parse", "HEAD^{tree}")
        rows = {}
        for path, raw in changes.items():
            prior = self.root / path
            rows[path] = {"before_sha256": b._sha(prior.read_bytes()) if prior.is_file() else None,
                          "after_sha256": b._sha(raw)}
            self.write(path, raw)
        self.git("add", "--", *sorted(changes))
        tree = self.git("write-tree")
        self.q.update(
            operation_kind="repair_g2_audio_privacy", operation_id="authored-g2-audio-repair",
            phase="development", base_commit=base, base_tree=base_tree, expected_head=base,
            expected_index_tree=tree, candidate_tree=tree, activation_commit=self.activation,
            installed_controller=copy.deepcopy(self.batch_controller), repair_sha256=rows)
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}


class G2PatientFixture(G2AudioFixture):
    """Authored v6 activation over exact v5 policy/source and published audio bytes."""
    PATIENT_TEST = "tests/test_consultation_patient_binding.py"
    AUDIO_TEST = "tests/test_consultation_audio_privacy.py"

    def __init__(self, assets):
        super().__init__(assets)
        self.patient_previous_policy = {
            p: (assets / "g2-patient-predecessor-policy" / p).read_bytes()
            for p in b.G2_PATIENT_PREDECESSOR_POLICY}
        self.patient_previous_source = {
            p: (assets / "g2-patient-predecessor-source" / p).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS}
        self.audio_publication_source = {
            p: (assets / "g2-patient-audio-publication" / p).read_bytes()
            for p in b.G2_AUDIO_REPAIR_SOURCE_SHA256}
        previous = {
            **self.patient_previous_policy,
            **self.patient_previous_source,
            **self.audio_publication_source,
        }
        for path, raw in previous.items():
            self.write(path, raw)
        patient_test = self.root / self.PATIENT_TEST
        if patient_test.exists():
            patient_test.unlink()
        self.git("add", "--", *sorted(previous))
        self.git("rm", "--cached", "--ignore-unmatch", "--", self.PATIENT_TEST)
        base_tree = self.git("write-tree")
        base = self.git("commit-tree", base_tree, "-p", self.base,
                        "-m", "authored exact published audio baseline")
        self.git("update-ref", "--no-deref", "HEAD", base, self.base)
        self.base = base
        sources = {p: b._sha((self.source / p).read_bytes()) for p in b.CONTROLLER_PATHS}
        self.batch_scope = b.build_g2_patient_scope("2026-09-15T00:00:00+00:00", base, sources)
        after = b.build_g2_patient_transition(
            {p: self.patient_previous_policy[p] for p in b.G2_BATCH_CONTROL_PATHS},
            self.batch_scope)
        after.update({p: (self.source / p).read_bytes() for p in b.G2_BATCH_CODE_PATHS})
        changes = {p: {"before_sha256": b._sha((self.root / p).read_bytes()),
                       "after_sha256": b._sha(raw)} for p, raw in after.items()}
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(
            schema_version=b.G2_PATIENT_BINDING_VERSION,
            operation_id="authored-g2-patient-activation",
            operation_kind="enable_g2_patient_binding",
            phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=tree, candidate_tree=tree,
            activation_commit=b.G2_PATIENT_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(b.G2_PATIENT_PREDECESSOR),
            repair_sha256=changes,
            source_sha256={p: b._sha((self.source / p).read_bytes()) for p in b.SOURCE_PATHS},
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}
        self.patient_predecessor_header = (
            "tree " + b.G2_PATIENT_PREDECESSOR["tree"] + "\nparent "
            + b.G2_PATIENT_PREDECESSOR["parent"] + "\n\nauthored v5 predecessor\n")
        self.audio_publication_header = (
            "tree " + b.G2_AUDIO_REPAIR_PUBLICATION["tree"] + "\nparent "
            + b.G2_AUDIO_REPAIR_PUBLICATION["parent"] + "\n\nauthored audio publication\n")

    @contextmanager
    def component_history(self):
        with super().component_history():
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            predecessor = b.G2_PATIENT_PREDECESSOR
            publication = b.G2_AUDIO_REPAIR_PUBLICATION

            def observed_text(root, *args, **kwargs):
                if root == self.root and args == ("cat-file", "commit", predecessor["commit"]):
                    return self.patient_predecessor_header
                if root == self.root and args == ("cat-file", "commit", publication["commit"]):
                    return self.audio_publication_header
                if root == self.root and args in (
                    ("merge-base", "--is-ancestor", predecessor["commit"], self.q["base_commit"]),
                    ("merge-base", "--is-ancestor", publication["commit"], self.q["base_commit"]),
                ):
                    return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for path, raw in {**self.patient_previous_policy,
                                  **self.patient_previous_source}.items():
                    if root == self.root and args == (
                            "cat-file", "blob", predecessor["commit"] + ":" + path):
                        return raw
                for path, raw in self.audio_publication_source.items():
                    if root == self.root and args == (
                            "cat-file", "blob", publication["commit"] + ":" + path):
                        return raw
                return run_bytes(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=observed_text), \
                    patch.object(b.trusted_git, "run_git_bytes", side_effect=observed_bytes):
                yield

    def prepare_patient(self, changes):
        base = self.git("rev-parse", "HEAD")
        base_tree = self.git("rev-parse", "HEAD^{tree}")
        rows = {}
        for path, raw in changes.items():
            prior = self.root / path
            rows[path] = {"before_sha256": b._sha(prior.read_bytes()) if prior.is_file() else None,
                          "after_sha256": b._sha(raw)}
            self.write(path, raw)
        self.git("add", "--", *sorted(changes))
        tree = self.git("write-tree")
        self.q.update(
            operation_kind="repair_g2_patient_binding",
            operation_id="authored-g2-patient-repair",
            phase="development", base_commit=base, base_tree=base_tree,
            expected_head=base, expected_index_tree=tree, candidate_tree=tree,
            activation_commit=self.activation,
            installed_controller=copy.deepcopy(self.batch_controller),
            repair_sha256=rows,
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes()) for p in b.batch_input_paths(self.q)}

    def restage(self, path, raw, *, repair_after=False):
        self.write(path, raw)
        self.git("add", "--", path)
        tree = self.git("write-tree")
        self.q.update(expected_index_tree=tree, candidate_tree=tree)
        self.q["payload_sha256"][path] = b._sha(raw)
        if repair_after:
            self.q["repair_sha256"][path]["after_sha256"] = b._sha(raw)


class G2AtomicityFixture(G2PatientFixture):
    """Authored v7 activation over exact v6 policy/source and patient repair."""

    ATOMICITY_TEST = "tests/test_consultation_finalize_atomicity.py"

    def __init__(self, assets):
        super().__init__(assets)
        self.atomicity_previous_policy = {
            p: (
                assets / "g2-atomicity-predecessor-policy" / p
            ).read_bytes()
            for p in b.G2_ATOMICITY_PREDECESSOR_POLICY
        }
        self.atomicity_previous_source = {
            p: (
                assets / "g2-atomicity-predecessor-source" / p
            ).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS
        }
        self.patient_publication_source = {
            p: (
                assets / "g2-atomicity-patient-publication" / p
            ).read_bytes()
            for p in b.G2_PATIENT_REPAIR_SOURCE_SHA256
        }

        predecessor = {
            **self.atomicity_previous_policy,
            **self.atomicity_previous_source,
        }
        for path, raw in predecessor.items():
            self.write(path, raw)
        atomicity_test = self.root / self.ATOMICITY_TEST
        if atomicity_test.exists():
            atomicity_test.unlink()
        self.git("add", "--", *sorted(predecessor))
        self.git(
            "rm", "--cached", "--ignore-unmatch", "--", self.ATOMICITY_TEST
        )
        predecessor_tree = self.git("write-tree")
        predecessor_base = self.git(
            "commit-tree",
            predecessor_tree,
            "-p",
            self.base,
            "-m",
            "authored exact v6 patient activation baseline",
        )
        self.git(
            "update-ref", "--no-deref", "HEAD", predecessor_base, self.base
        )

        for path, raw in self.patient_publication_source.items():
            self.write(path, raw)
        self.git(
            "add", "--", *sorted(self.patient_publication_source)
        )
        base_tree = self.git("write-tree")
        base = self.git(
            "commit-tree",
            base_tree,
            "-p",
            predecessor_base,
            "-m",
            "authored exact published patient repair baseline",
        )
        self.git(
            "update-ref", "--no-deref", "HEAD", base, predecessor_base
        )
        self.base = base

        sources = {
            p: b._sha((self.source / p).read_bytes())
            for p in b.CONTROLLER_PATHS
        }
        self.batch_scope = b.build_g2_atomicity_scope(
            "2026-09-15T03:00:00+00:00",
            base,
            sources,
        )
        after = b.build_g2_atomicity_transition(
            {
                p: self.atomicity_previous_policy[p]
                for p in b.G2_BATCH_CONTROL_PATHS
            },
            self.batch_scope,
        )
        after.update({
            p: (self.source / p).read_bytes()
            for p in b.G2_BATCH_CODE_PATHS
        })
        changes = {
            p: {
                "before_sha256": b._sha((self.root / p).read_bytes()),
                "after_sha256": b._sha(raw),
            }
            for p, raw in after.items()
        }
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(
            schema_version=b.G2_ATOMICITY_BINDING_VERSION,
            operation_id="authored-g2-atomicity-activation",
            operation_kind="enable_g2_consultation_atomicity",
            phase="development",
            base_commit=base,
            base_tree=base_tree,
            expected_head=base,
            expected_index_tree=tree,
            candidate_tree=tree,
            activation_commit=b.G2_ATOMICITY_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(
                b.G2_ATOMICITY_PREDECESSOR
            ),
            repair_sha256=changes,
            source_sha256={
                p: b._sha((self.source / p).read_bytes())
                for p in b.SOURCE_PATHS
            },
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes())
            for p in b.batch_input_paths(self.q)
        }
        self.atomicity_predecessor_header = (
            "tree " + b.G2_ATOMICITY_PREDECESSOR["tree"] + "\nparent "
            + b.G2_ATOMICITY_PREDECESSOR["parent"]
            + "\n\nauthored v6 predecessor\n"
        )
        self.patient_publication_header = (
            "tree " + b.G2_PATIENT_REPAIR_PUBLICATION["tree"] + "\nparent "
            + b.G2_PATIENT_REPAIR_PUBLICATION["parent"]
            + "\n\nauthored patient publication\n"
        )

    @contextmanager
    def component_history(self):
        with super().component_history():
            run = b.trusted_git.run_git
            run_bytes = b.trusted_git.run_git_bytes
            predecessor = b.G2_ATOMICITY_PREDECESSOR
            publication = b.G2_PATIENT_REPAIR_PUBLICATION

            def observed_text(root, *args, **kwargs):
                if root == self.root and args == (
                    "cat-file", "commit", predecessor["commit"]
                ):
                    return self.atomicity_predecessor_header
                if root == self.root and args == (
                    "cat-file", "commit", publication["commit"]
                ):
                    return self.patient_publication_header
                if root == self.root and args in (
                    (
                        "merge-base", "--is-ancestor",
                        predecessor["commit"], self.q["base_commit"],
                    ),
                    (
                        "merge-base", "--is-ancestor",
                        publication["commit"], self.q["base_commit"],
                    ),
                ):
                    return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for path, raw in {
                    **self.atomicity_previous_policy,
                    **self.atomicity_previous_source,
                }.items():
                    if root == self.root and args == (
                        "cat-file", "blob",
                        predecessor["commit"] + ":" + path,
                    ):
                        return raw
                for path, raw in self.patient_publication_source.items():
                    if root == self.root and args == (
                        "cat-file", "blob",
                        publication["commit"] + ":" + path,
                    ):
                        return raw
                return run_bytes(root, *args, **kwargs)

            with patch.object(
                b.trusted_git, "run_git", side_effect=observed_text
            ), patch.object(
                b.trusted_git, "run_git_bytes", side_effect=observed_bytes
            ):
                yield

    def prepare_atomicity(self, changes):
        base = self.git("rev-parse", "HEAD")
        base_tree = self.git("rev-parse", "HEAD^{tree}")
        rows = {}
        for path, raw in changes.items():
            prior = self.root / path
            rows[path] = {
                "before_sha256": (
                    b._sha(prior.read_bytes()) if prior.is_file() else None
                ),
                "after_sha256": b._sha(raw),
            }
            self.write(path, raw)
        self.git("add", "--", *sorted(changes))
        tree = self.git("write-tree")
        self.q.update(
            operation_kind="repair_g2_consultation_atomicity",
            operation_id="authored-g2-atomicity-repair",
            phase="development",
            base_commit=base,
            base_tree=base_tree,
            expected_head=base,
            expected_index_tree=tree,
            candidate_tree=tree,
            activation_commit=self.activation,
            installed_controller=copy.deepcopy(self.batch_controller),
            repair_sha256=rows,
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes())
            for p in b.batch_input_paths(self.q)
        }


class G2ClinicalFixture(G2AtomicityFixture):
    """Authored v8 activation over exact v7 policy and atomicity publication."""

    AUDIT_EVENTS = "app/services/ai/audit_events.py"

    def __init__(self, assets):
        super().__init__(assets)
        self.clinical_previous_policy = {
            p: (
                assets / "g2-clinical-predecessor-policy" / p
            ).read_bytes()
            for p in b.G2_CLINICAL_PREDECESSOR_POLICY
        }
        self.clinical_previous_source = {
            p: (
                assets / "g2-clinical-predecessor-source" / p
            ).read_bytes()
            for p in b.SOURCE_PATHS | b.CONTROLLER_PATHS
        }
        self.atomicity_publication_source = {
            p: (
                assets / "g2-clinical-atomicity-publication" / p
            ).read_bytes()
            for p in b.G2_ATOMICITY_REPAIR_SOURCE_SHA256
        }
        self.clinical_owner_record = (
            assets / "evidence" / rp.G2_CLINICAL_OWNER_RECORD
        ).read_bytes()

        predecessor = {
            **self.clinical_previous_policy,
            **self.clinical_previous_source,
        }
        for path, raw in predecessor.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(predecessor))
        predecessor_tree = self.git("write-tree")
        predecessor_base = self.git(
            "commit-tree",
            predecessor_tree,
            "-p",
            self.base,
            "-m",
            "authored exact v7 atomicity activation baseline",
        )
        self.git(
            "update-ref", "--no-deref", "HEAD", predecessor_base, self.base
        )

        for path, raw in self.atomicity_publication_source.items():
            self.write(path, raw)
        self.git(
            "add", "--", *sorted(self.atomicity_publication_source)
        )
        base_tree = self.git("write-tree")
        base = self.git(
            "commit-tree",
            base_tree,
            "-p",
            predecessor_base,
            "-m",
            "authored exact published atomicity and owner policy baseline",
        )
        self.git(
            "update-ref", "--no-deref", "HEAD", base, predecessor_base
        )
        self.base = base

        sources = {
            p: b._sha((self.source / p).read_bytes())
            for p in b.CONTROLLER_PATHS
        }
        self.batch_scope = b.build_g2_clinical_scope(
            "2026-09-15T06:00:00+00:00", base, sources
        )
        after = b.build_g2_clinical_transition(
            {
                p: self.clinical_previous_policy[p]
                for p in b.G2_BATCH_CONTROL_PATHS
            },
            self.batch_scope,
        )
        after.update({
            p: (self.source / p).read_bytes()
            for p in b.G2_BATCH_CODE_PATHS
        })
        changes = {
            p: {
                "before_sha256": b._sha((self.root / p).read_bytes()),
                "after_sha256": b._sha(raw),
            }
            for p, raw in after.items()
        }
        for path, raw in after.items():
            self.write(path, raw)
        self.git("add", "--", *sorted(after))
        tree = self.git("write-tree")
        self.q.update(
            schema_version=b.G2_CLINICAL_BINDING_VERSION,
            operation_id="authored-g2-clinical-authority-activation",
            operation_kind="enable_g2_clinical_authority",
            phase="development",
            base_commit=base,
            base_tree=base_tree,
            expected_head=base,
            expected_index_tree=tree,
            candidate_tree=tree,
            activation_commit=b.G2_CLINICAL_PREDECESSOR["commit"],
            installed_controller=copy.deepcopy(b.G2_CLINICAL_PREDECESSOR),
            repair_sha256=changes,
            source_sha256={
                p: b._sha((self.source / p).read_bytes())
                for p in b.SOURCE_PATHS
            },
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes())
            for p in b.batch_input_paths(self.q)
        }
        self.clinical_predecessor_header = (
            "tree " + b.G2_CLINICAL_PREDECESSOR["tree"] + "\nparent "
            + b.G2_CLINICAL_PREDECESSOR["parent"]
            + "\n\nauthored v7 predecessor\n"
        )
        self.atomicity_publication_header = (
            "tree " + b.G2_ATOMICITY_REPAIR_PUBLICATION["tree"] + "\nparent "
            + b.G2_ATOMICITY_REPAIR_PUBLICATION["parent"]
            + "\n\nauthored atomicity publication\n"
        )

    @contextmanager
    def component_history(self):
        with super().component_history():
            run = b.trusted_git.run_git
            run_bytes = b.trusted_git.run_git_bytes
            predecessor = b.G2_CLINICAL_PREDECESSOR
            publication = b.G2_ATOMICITY_REPAIR_PUBLICATION

            def observed_text(root, *args, **kwargs):
                if root == self.root and args == (
                    "cat-file", "commit", predecessor["commit"]
                ):
                    return self.clinical_predecessor_header
                if root == self.root and args == (
                    "cat-file", "commit", publication["commit"]
                ):
                    return self.atomicity_publication_header
                if root == self.root and args in (
                    (
                        "merge-base", "--is-ancestor",
                        predecessor["commit"], self.q["base_commit"],
                    ),
                    (
                        "merge-base", "--is-ancestor",
                        publication["commit"], self.q["base_commit"],
                    ),
                ):
                    return ""
                return run(root, *args, **kwargs)

            def observed_bytes(root, *args, **kwargs):
                for path, raw in {
                    **self.clinical_previous_policy,
                    **self.clinical_previous_source,
                }.items():
                    if root == self.root and args == (
                        "cat-file", "blob", predecessor["commit"] + ":" + path,
                    ):
                        return raw
                for path, raw in self.atomicity_publication_source.items():
                    if root == self.root and args == (
                        "cat-file", "blob", publication["commit"] + ":" + path,
                    ):
                        return raw
                return run_bytes(root, *args, **kwargs)

            with patch.object(
                b.trusted_git, "run_git", side_effect=observed_text
            ), patch.object(
                b.trusted_git, "run_git_bytes", side_effect=observed_bytes
            ):
                yield

    def prepare_clinical(self, changes):
        base = self.git("rev-parse", "HEAD")
        base_tree = self.git("rev-parse", "HEAD^{tree}")
        rows = {}
        for path, raw in changes.items():
            prior = self.root / path
            rows[path] = {
                "before_sha256": b._sha(prior.read_bytes()),
                "after_sha256": b._sha(raw),
            }
            self.write(path, raw)
        self.git("add", "--", *sorted(changes))
        tree = self.git("write-tree")
        self.q.update(
            operation_kind="repair_g2_clinical_authority",
            operation_id="authored-g2-clinical-authority-repair",
            phase="development",
            base_commit=base,
            base_tree=base_tree,
            expected_head=base,
            expected_index_tree=tree,
            candidate_tree=tree,
            activation_commit=self.activation,
            installed_controller=copy.deepcopy(self.batch_controller),
            repair_sha256=rows,
        )
        self.q["payload_sha256"] = {
            p: b._sha((self.root / p).read_bytes())
            for p in b.batch_input_paths(self.q)
        }


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
            for kind in ("accept_g2", "implement_g1e", None, []):
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

    class G2AdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = SuccessorFixture(assets, "accept_g1e")
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        def test_four_changed_files_authenticate_all_five_installed_components(self):
            f = self.fx
            result = f.decision()
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertEqual(result.current_gate, "G2")
            self.assertFalse(result.execution_authorized)
            changed = set(f.git("diff-tree", "--no-commit-id", "--name-only", "-r", f.base).splitlines())
            self.assertEqual(changed, b.CONTROLLER_PATHS - {"orchestration_harness/configuration_core.py"})
            self.assertEqual(set(f.controller["source_sha256"]), b.CONTROLLER_PATHS)
            original = copy.deepcopy(f.q["installed_controller"])
            del f.q["installed_controller"]["source_sha256"]["orchestration_harness/configuration_core.py"]
            self.assertEqual(f.decision().reason_codes, ("bounded_g1e_controller_source_paths",))
            f.q["installed_controller"] = original
            f.q["installed_controller"]["source_sha256"]["orchestration_harness/configuration_core.py"] = "0" * 64
            self.assertEqual(f.decision().reason_codes, ("bounded_g1e_installed_controller_changed",))

        def test_acceptance_preserves_prior_authority_and_all_g2_requirements(self):
            f = self.fx
            before, after = b._json(f.before[b.STATE]), b._json(f.after[b.STATE])
            changed_keys = {"current_gate", "active_correction", "active_profile", "observed_at", "g1e", "g2", "task_selection"}
            self.assertEqual({k:v for k,v in after.items() if k not in changed_keys},
                             {k:v for k,v in before.items() if k not in changed_keys})
            self.assertTrue(after["g1e"]["completion_accepted"])
            self.assertFalse(after["g2"]["completion_accepted"])
            self.assertEqual(after["g1e"]["current_operation"], before["g1e"]["current_operation"])
            self.assertEqual(after["global_checks"], before["global_checks"])
            gates = b._document(f.after[b.GATES], b.GATES)
            rows = {row["id"]:row for row in gates["gates"]}
            self.assertEqual(rows["G2"]["exit_checks"], list(b.G2_CRITERIA))
            self.assertEqual(len(rows["G2"]["exit_checks"]), 12)
            self.assertEqual(rows["G1E"]["status"], "passed")
            self.assertEqual(rows["G2"]["status"], "active")

        def test_historical_assessment_is_distinct_from_current_controller(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            scope = b._json(f.after[b.G2_SCOPE])
            self.assertEqual(scope["accepted_publication"], b.G1E_PUBLICATION)
            self.assertEqual(scope["accepted_activation"], b.G1E_ACTIVATION)
            self.assertNotEqual(scope["accepted_publication"]["commit"], f.controller["commit"])
            self.assertEqual(scope["accepted_source_sha256"], b.G1E_SOURCE_PINS)
            for path in b.CONTROLLER_PATHS - {"orchestration_harness/configuration_core.py"}:
                self.assertNotEqual(scope["accepted_source_sha256"][path], f.controller["source_sha256"][path])
            f.accepted_activation_header = f.accepted_activation_header.replace(b.G1E_ACTIVATION["tree"], "0" * 40)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_accepted_activation_invalid",))

        def test_assessed_source_and_historical_authority_cannot_be_substituted(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            path = "orchestration_harness/raisa_policy.py"
            original = f.accepted_source[path]
            f.accepted_source[path] = original + b"\n"
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_accepted_component_changed",))
            f.accepted_source[path] = original
            f.accepted_activation_source[b.STATE] += b"\n"
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_assessed_authority_changed",))

        def test_every_acceptance_and_owner_evidence_input_is_required(self):
            f = self.fx
            b.validate_g2_acceptance_transition(f.before, f.after, f.evidence)
            for path in b.G1E_EVIDENCE_PINS:
                with self.subTest(path=path):
                    with self.assertRaises(b.BoundedG1BError) as caught:
                        b.validate_g2_acceptance_transition(f.before, f.after, {k:v for k,v in f.evidence.items() if k != path})
                    self.assertEqual(caught.exception.reason_code, "bounded_g2_evidence_paths")
                    with self.assertRaises(b.BoundedG1BError) as caught:
                        b.validate_g2_acceptance_transition(f.before, f.after, {**f.evidence, path:f.evidence[path]+b"\n"})
                    self.assertEqual(caught.exception.reason_code, "bounded_g2_evidence_changed")

        def test_scope_cannot_expand_paths_outcomes_or_runtime_authority(self):
            f = self.fx
            original = b._json(f.after[b.G2_SCOPE])
            for field, value in (("allowed_paths", [b.G2_FIXTURE, "app/main.py"]),
                                 ("allowed_effects", ["repository_read", "database_runtime"]),
                                 ("execution_authorized", True), ("g2_complete", True),
                                 ("g2_exit_requirements", []), ("feature_work_eligible", True)):
                with self.subTest(field=field), self.assertRaises(b.BoundedG1BError) as caught:
                    b.build_g2_acceptance_transition(f.before, {**original, field:value})
                self.assertEqual(caught.exception.reason_code, "bounded_g2_scope_invalid")
            changed = copy.deepcopy(original)
            changed["owner_test_runtime_exception"]["admission_grants_runtime_authority"] = True
            with self.assertRaises(b.BoundedG1BError) as caught:
                b.build_g2_acceptance_transition(f.before, changed)
            self.assertEqual(caught.exception.reason_code, "bounded_g2_scope_invalid")

        def test_configuration_validation_and_general_runtime_closures_are_retained(self):
            f = self.fx
            calls = []
            validate = core.validate_configuration
            def observe(**kwargs):
                calls.append(set(kwargs["documents"]))
                return validate(**kwargs)
            with patch.object(core, "validate_configuration", side_effect=observe):
                self.assertTrue(f.decision().policy_admitted)
            self.assertEqual(calls, [{Path(p).name for p in b.CONFIGURATION_PATHS}])
            path = "orchestration/harness_settings/evidence_led_workflow.yaml"
            self.assertEqual(b._sha((f.root / path).read_bytes()), b.CONFIGURATION_LEAF_PINS[path])
            docs = {Path(p).name:(f.root / p).read_bytes() for p in b.CONFIGURATION_PATHS}
            original = b._document(docs["programme_recovery.yaml"], "programme_recovery.yaml")
            for key, value in (("independent_execution_binding_required", False), ("test_attempts", 999),
                               ("owner_approval_sha256", "0" * 64)):
                changed = copy.deepcopy(original)
                changed["profiles"][b.G2_PROFILE]["owner_test_runtime_exception"][key] = value
                docs["programme_recovery.yaml"] = b._canonical(changed)
                with self.subTest(key=key), self.assertRaises(rp.RaisaPolicyError) as caught:
                    rp.validate_recovery_configuration(documents=docs, expected_sha256={n:b._sha(v) for n,v in docs.items()},
                        agents_text=f.after[b.AGENTS].decode(), state=b._json(f.after[b.STATE]))
                self.assertEqual(caught.exception.reason_code, "configuration_g2_repair_profile_invalid")

        def test_exact_fixture_repair_requires_published_activation_and_both_hashes(self):
            f = self.fx
            activation = f.activate()
            f.prepare_implementation(activation)
            result = f.decision()
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertFalse(result.execution_authorized)
            self.assertEqual(b.operation_paths("repair_g2_fixture"), frozenset(b.G2_REPAIR_PINS))
            self.assertEqual(f.git("show", activation + ":" + b.G2_FIXTURE).strip(),
                             (assets / "g2-fixture/before").read_text().strip())
            raw = (f.root / b.G2_FIXTURE).read_bytes()
            f.write(b.G2_FIXTURE, raw + b"\n")
            f.q["payload_sha256"][b.G2_FIXTURE] = b._sha(raw + b"\n")
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_fixture_candidate_changed",))
            f.write(b.G2_FIXTURE, raw)
            f.q["payload_sha256"][b.G2_FIXTURE] = b._sha(raw)
            f.q["activation_commit"] = f.base
            self.assertFalse(f.decision().policy_admitted)

        def test_rebinding_scope_cannot_grant_application_effects(self):
            f = self.fx
            context = f.context()
            manifest = f.manifest(context)
            for key, value in (("intended_side_effect_classes", sorted(b.EFFECTS | {"database_runtime"})),
                               ("allowed_paths", sorted(b.G2_TRANSITION_PATHS | {b.G2_FIXTURE}))):
                result = b.evaluate_bounded_g1b_operation(context=context, manifest={**manifest, key:value},
                    entrypoint="task_branch_commit", phase="development")
                self.assertEqual(result.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
                self.assertFalse(result.execution_authorized)

        def test_committed_fixture_repair_keeps_activation_binding_and_scope(self):
            f = self.fx
            activation = f.activate()
            f.prepare_implementation(activation)
            self.assertTrue(f.decision().policy_admitted)
            commit = f.git("commit-tree", f.q["candidate_tree"], "-p", activation, "-m", "authored exact fixture repair")
            f.git("update-ref", "--no-deref", "HEAD", commit, activation)
            f.q.update(phase="pre-push", expected_head=commit)
            context = f.context()
            result = b.evaluate_bounded_g1b_operation(context=context, manifest=f.manifest(context),
                entrypoint="task_branch_push", phase="pre-push")
            self.assertTrue(result.policy_admitted, result.reason_codes)
            self.assertFalse(result.execution_authorized)
            self.assertEqual(f.q["activation_commit"], activation)
            self.assertEqual(f.q["base_commit"], activation)

        def test_cold_import_prerequisite_is_exact_and_only_delays_the_excluded_import(self):
            f = self.fx
            before = ast.parse((assets / "g2-cold-import/before").read_bytes())
            after = ast.parse((assets / "g2-cold-import/after").read_bytes())
            module = "reception_one_bureau_typed_plan_protocol"
            def moved(node):
                return isinstance(node, ast.ImportFrom) and node.module == "scripts" and any(a.name == module for a in node.names)
            self.assertEqual(sum(moved(node) for node in before.body), 1)
            self.assertFalse(any(moved(node) for node in after.body))
            owners = {node.name for node in after.body if isinstance(node, ast.FunctionDef)
                      and any(moved(child) for child in node.body)}
            self.assertEqual(owners, {"build_product_context_frame", "build_slot_search_input", "proofread_provider_blocked_plan"})
            class RemoveMoved(ast.NodeTransformer):
                def visit_ImportFrom(self, node):
                    return None if moved(node) else node
            self.assertEqual(ast.dump(RemoveMoved().visit(before), include_attributes=False),
                             ast.dump(RemoveMoved().visit(after), include_attributes=False))
            activation = f.activate()
            f.prepare_implementation(activation)
            self.assertTrue(f.decision().policy_admitted)
            raw = (f.root / b.G2_COLD_IMPORT).read_bytes() + b"\n"
            f.write(b.G2_COLD_IMPORT, raw)
            f.q["payload_sha256"][b.G2_COLD_IMPORT] = b._sha(raw)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_fixture_candidate_changed",))

        def test_every_g2_marker_closes_legacy_loading_before_observation(self):
            f = self.fx
            historical = b._json((f.source / "baseline" / b.STATE).read_bytes())
            for path in b.BOUNDED_SCOPE_PATHS:
                target = f.root / path
                if target.exists():
                    target.unlink()
            cases = [lambda s:s.update(active_profile=b.G2_PROFILE), lambda s:s.update(current_gate="G2"),
                     lambda s:s.update(active_correction="G2"), lambda s:s.update(g2=None),
                     lambda s:s["task_selection"].update(allowed_task_kinds=[b.G2_TASK])]
            for mutate in cases:
                state = copy.deepcopy(historical)
                mutate(state)
                f.write(b.STATE, b._canonical(state))
                with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                    pa.load_programme_policy(f.root)
                self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")
                self.assertEqual(pf.build_report(f.root)["status"], "blocked")
            f.write(b.STATE, b._canonical(historical))
            f.write(b.G2_SCOPE, b"malformed G2 scope marker")
            with self.assertRaises(pa.ProgrammeAdmissionError) as caught:
                pa.load_programme_policy(f.root)
            self.assertEqual(caught.exception.reason_code, "bounded_g1b_context_required")

    class G2BatchAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2BatchFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        def test_six_file_maintenance_uses_actual_callers_and_preserves_acceptance(self):
            f = self.fx
            context = f.context()
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            self.assertEqual(manifest, f.manifest(context))
            report = pf.build_report(f.root, manifest, bounded_context=context,
                                     phase="development", entrypoint="task_branch_commit")
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            self.assertFalse(report["feature_work_eligible"])
            self.assertEqual(len(manifest["allowed_paths"]), 6)
            self.assertEqual(b.G2_BATCH_TASK, b.G2_TASK)
            state = b._json((f.root / b.STATE).read_bytes())
            original = b._json(f.initial_policy[b.STATE])
            self.assertEqual(state["g1e"], original["g1e"])
            self.assertEqual((f.root / b.GATES).read_bytes(), f.initial_policy[b.GATES])
            self.assertEqual((f.root / b.AGENTS).read_bytes(), f.initial_policy[b.AGENTS])
            self.assertEqual(f.batch_scope["g2_exit_requirements"], list(b.G2_CRITERIA))
            self.assertEqual(f.batch_scope["owner_test_runtime_exception"], rp.g2_test_exception())
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)

        def test_two_successive_batches_keep_controller_state_and_scope_unchanged(self):
            f = self.fx
            f.activate_batches()
            preserved = {p: (f.root / p).read_bytes() for p in b.CONTROLLER_PATHS | b.G2_TRANSITION_PATHS}
            for number in (1, 2):
                f.prepare_batch({p: ("# authored repair batch " + str(number) + "\n").encode()
                                 for p in b.G2_BATCH_PATHS - {b.G2_COLD_IMPORT}})
                self.assertTrue(f.decision().policy_admitted)
                self.assertEqual(len(f.q["repair_sha256"]), 5)
                f.commit_current()
                self.assertTrue(f.decision().policy_admitted)
                f.q["phase"] = "post-push"
                self.assertTrue(f.decision().policy_admitted)
                for path, raw in preserved.items():
                    self.assertEqual((f.root / path).read_bytes(), raw)

        def test_unapproved_and_authority_paths_reject_before_selected_reads(self):
            f = self.fx
            f.activate_batches()
            f.prepare_batch({b.G2_FIXTURE: b"# authored candidate\n"})
            original = copy.deepcopy(f.q)
            read = b.trusted_git._read_regular_snapshot
            for path in ("../outside.py", ".git/config", b.STATE, b.G2_SCOPE,
                         "orchestration_harness/bounded_g1b.py", b.G2_FIXTURE.upper(),
                         "tests/not-reviewed.py"):
                f.q = copy.deepcopy(original)
                f.q["repair_sha256"] = {path: copy.deepcopy(original["repair_sha256"][b.G2_FIXTURE])}
                seen = []

                def observed(candidate, **kwargs):
                    seen.append(candidate)
                    return read(candidate, **kwargs)

                with self.subTest(path=path), patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                    decision = f.decision()
                self.assertEqual(decision.reason_codes, ("bounded_g2_batch_path_not_allowed",))
                self.assertNotIn(f.root / path, seen)
            f.q = original

        def test_exact_preimage_candidate_and_controller_bindings_are_required(self):
            f = self.fx
            f.activate_batches()
            f.prepare_batch({b.G2_FIXTURE: b"# authored candidate\n"})
            original = copy.deepcopy(f.q)
            cases = (
                (lambda q: q["repair_sha256"][b.G2_FIXTURE].update(before_sha256="0" * 64),
                 "bounded_g2_batch_preimage_changed"),
                (lambda q: q["repair_sha256"][b.G2_FIXTURE].update(after_sha256="0" * 64),
                 "bounded_g2_batch_candidate_changed"),
                (lambda q: q["installed_controller"]["source_sha256"].update(
                    {"orchestration_harness/raisa_policy.py": "0" * 64}),
                 "bounded_g2_batch_controller_disagreement"),
                (lambda q: q.update(activation_commit=b.G2_INITIAL_ACTIVATION["commit"]),
                 "bounded_g2_batch_activation_binding"),
            )
            for mutate, reason in cases:
                f.q = copy.deepcopy(original)
                mutate(f.q)
                with self.subTest(reason=reason):
                    self.assertEqual(f.decision().reason_codes, (reason,))
            f.q = original

        def test_maintenance_cannot_claim_prospective_source_as_already_installed(self):
            f = self.fx
            f.q["installed_controller"]["source_sha256"] = copy.deepcopy(f.batch_scope["controller_source_sha256"])
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_maintenance_predecessor",))
            f.q["installed_controller"] = copy.deepcopy(b.G2_INITIAL_CONTROLLER)
            f.q["repair_sha256"].pop("tests/test_bounded_g1b.py")
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_path_not_allowed",))

        def test_scope_cannot_weaken_runtime_or_completion_requirements(self):
            f = self.fx
            original = copy.deepcopy(f.q)
            for mutate in (
                lambda s: s.update(execution_authorized=True),
                lambda s: s.update(g2_complete=True),
                lambda s: s["g2_exit_requirements"].pop(),
                lambda s: s["owner_test_runtime_exception"].update(admission_grants_runtime_authority=True),
                lambda s: s["forbidden_effects"].remove("provider_invocation"),
            ):
                scope = copy.deepcopy(f.batch_scope)
                mutate(scope)
                raw = b._canonical(scope) + b"\n"
                f.write(b.G2_SCOPE, raw)
                f.q = copy.deepcopy(original)
                f.q["payload_sha256"][b.G2_SCOPE] = b._sha(raw)
                f.q["repair_sha256"][b.G2_SCOPE]["after_sha256"] = b._sha(raw)
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_scope_invalid",))

        def test_repair_cannot_change_unowned_policy_or_declare_runtime_effects(self):
            f = self.fx
            f.activate_batches()
            f.prepare_batch({b.G2_FIXTURE: b"# authored candidate\n"})
            context = f.context()
            manifest = f.manifest(context)
            manifest["intended_side_effect_classes"].append("provider_invocation")
            decision = b.evaluate_bounded_g1b_operation(context=context, manifest=manifest,
                entrypoint="task_branch_commit", phase="development")
            self.assertEqual(decision.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
            state = b._json((f.root / b.STATE).read_bytes())
            state["feature_work_eligible"] = True
            raw = b._canonical(state)
            f.write(b.STATE, raw)
            f.q["payload_sha256"][b.STATE] = b._sha(raw)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_unowned_input_changed",))

    class G2CatalogueAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2CatalogueFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        def test_extension_uses_current_predecessor_and_actual_admission(self):
            f = self.fx
            context = f.context()
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            report = pf.build_report(f.root, manifest, bounded_context=context,
                                     phase="development", entrypoint="task_branch_commit")
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            self.assertFalse(report["feature_work_eligible"])
            self.assertEqual(len(manifest["allowed_paths"]), 6)
            self.assertEqual(len(b.G2_CATALOGUE_PATHS), 148)
            self.assertEqual(len(b.batch_input_paths(f.q)), len(b.G2_CATALOGUE_POLICY_PATHS))
            old = b._json(f.previous_policy[b.STATE])
            current = b._json((f.root / b.STATE).read_bytes())
            self.assertEqual(old["g1e"], current["g1e"])
            self.assertEqual(old["task_selection"], current["task_selection"])
            self.assertEqual(f.batch_scope["g2_exit_requirements"], list(b.G2_CRITERIA))
            self.assertEqual(f.batch_scope["owner_test_runtime_exception"], rp.g2_test_exception())
            for path in (b.AGENTS, b.GATES):
                self.assertEqual((f.root / path).read_bytes(), f.previous_policy[path])
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)

        def test_different_successive_catalogue_repairs_need_no_controller_change(self):
            f = self.fx
            f.activate_batches()
            frozen = {p: (f.root / p).read_bytes() for p in b.CONTROLLER_PATHS | b.G2_TRANSITION_PATHS}
            for path in (f.AI, f.LATER):
                f.prepare_batch({path: b"# authored exact repair; never imported\n"})
                self.assertEqual(set(f.q["payload_sha256"]), b.G2_CATALOGUE_POLICY_PATHS | {path})
                self.assertTrue(f.decision().policy_admitted)
                f.commit_current()
                self.assertTrue(f.decision().policy_admitted)
                f.q["phase"] = "post-push"
                self.assertTrue(f.decision().policy_admitted)
                self.assertTrue(all((f.root / p).read_bytes() == raw for p, raw in frozen.items()))

        def test_membership_never_opens_unselected_catalogue_sources(self):
            f = self.fx
            f.activate_batches()
            f.prepare_batch({f.AI: b"# selected AI repair\n"})
            read = b.trusted_git._read_regular_snapshot
            selected = b.batch_input_paths(f.q)
            seen = []

            def observed(path, **kwargs):
                if path.is_relative_to(f.root):
                    relative = path.relative_to(f.root).as_posix()
                    if relative in b.G2_CATALOGUE_PATHS:
                        seen.append(relative)
                        self.assertIn(relative, selected)
                return read(path, **kwargs)

            with patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                self.assertTrue(f.decision().policy_admitted)
            self.assertEqual(set(seen), {f.AI})

        def test_unknown_protected_addition_and_oversized_batches_reject_before_reads(self):
            f = self.fx
            f.activate_batches()
            f.prepare_batch({f.AI: b"# selected AI repair\n"})
            original = copy.deepcopy(f.q)
            cases = []
            for path in ("app/not_reviewed.py", "../outside.py", ".git/config", b.STATE, b.G2_SCOPE, b.AGENTS):
                cases.append(({path: copy.deepcopy(original["repair_sha256"][f.AI])}, "bounded_g2_batch_path_not_allowed"))
            cases.append(({f.AI: {"before_sha256": None, "after_sha256": "0" * 64}}, "bounded_g2_batch_change_digest"))
            cases.append(({p: copy.deepcopy(original["repair_sha256"][f.AI])
                           for p in sorted(b.G2_CATALOGUE_PATHS)[:7]}, "bounded_g2_batch_changes_invalid"))
            for changes, reason in cases:
                f.q = copy.deepcopy(original)
                f.q["repair_sha256"] = changes
                with self.subTest(reason=reason, paths=sorted(changes)):
                    self.assertEqual(f.decision().reason_codes, (reason,))
            f.q = original

        def test_extra_observation_rejected_even_when_its_catalogue_path_is_valid(self):
            f = self.fx
            f.activate_batches()
            f.prepare_batch({f.AI: b"# selected AI repair\n"})
            f.q["payload_sha256"][f.LATER] = b._sha((f.root / f.LATER).read_bytes())
            read = b.trusted_git._read_regular_snapshot
            seen = []

            def observed(path, **kwargs):
                seen.append(path)
                return read(path, **kwargs)

            with patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_payload_paths",))
            self.assertNotIn(f.root / f.LATER, seen)

        def test_exact_before_after_and_installed_source_bindings_remain_required(self):
            f = self.fx
            f.q["installed_controller"]["source_sha256"] = copy.deepcopy(f.batch_scope["controller_source_sha256"])
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_maintenance_predecessor",))
            f.q["installed_controller"] = copy.deepcopy(b.G2_CATALOGUE_PREDECESSOR)
            f.activate_batches()
            f.prepare_batch({f.AI: b"# selected AI repair\n"})
            original = copy.deepcopy(f.q)
            for field, reason in (("before_sha256", "bounded_g2_batch_preimage_changed"),
                                  ("after_sha256", "bounded_g2_batch_candidate_changed")):
                f.q = copy.deepcopy(original)
                f.q["repair_sha256"][f.AI][field] = "0" * 64
                self.assertEqual(f.decision().reason_codes, (reason,))
            f.q = copy.deepcopy(original)
            f.q["installed_controller"]["source_sha256"].pop("orchestration_harness/configuration_core.py")
            self.assertFalse(f.decision().policy_admitted)
            f.q = original

        def test_catalogue_scope_keeps_all_closures_and_exact_membership(self):
            f = self.fx
            original = copy.deepcopy(f.q)
            for mutate in (lambda s: s.update(execution_authorized=True),
                           lambda s: s.update(g2_complete=True),
                           lambda s: s["g2_exit_requirements"].pop(),
                           lambda s: s["allowed_paths"].append("app/not_reviewed.py"),
                           lambda s: s["owner_test_runtime_exception"].update(admission_grants_runtime_authority=True)):
                scope = copy.deepcopy(f.batch_scope)
                mutate(scope)
                raw = b._canonical(scope) + b"\n"
                f.write(b.G2_SCOPE, raw)
                f.q = copy.deepcopy(original)
                f.q["payload_sha256"][b.G2_SCOPE] = b._sha(raw)
                f.q["repair_sha256"][b.G2_SCOPE]["after_sha256"] = b._sha(raw)
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_scope_invalid",))

        def test_legacy_transition_cannot_be_relabelled_for_catalogue_maintenance(self):
            f = self.fx
            f.q["operation_kind"] = "enable_g2_batches"
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_binding_version",))
            f.q["operation_kind"] = "extend_g2_catalogue"
            f.q["schema_version"] = b.G2_BATCH_BINDING_VERSION
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_binding_version",))

    class G2MigrationAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2MigrationFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        def test_enablement_preserves_gates_and_binds_owner_supported_paths(self):
            f = self.fx
            context = f.context()
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            report = pf.build_report(f.root, manifest, bounded_context=context,
                                     phase="development", entrypoint="task_branch_commit")
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            self.assertEqual(set(manifest["allowed_paths"]), b.G2_BATCH_MAINTENANCE_PATHS)
            self.assertEqual(set(manifest["intended_side_effect_classes"]), b.EFFECTS)
            before = b._json(f.migration_previous_policy[b.STATE])
            current = b._json((f.root / b.STATE).read_bytes())
            self.assertEqual(before["g1e"], current["g1e"])
            self.assertFalse(current["g2"]["completion_accepted"])
            for path in (b.AGENTS, b.GATES):
                self.assertEqual((f.root / path).read_bytes(), f.migration_previous_policy[path])
            self.assertEqual(f.batch_scope["allowed_paths"], sorted(b.G2_MIGRATION_PATHS))
            self.assertEqual(f.batch_scope["migration_supported_paths"], rp.g2_migration_contract())
            self.assertEqual(f.batch_scope["g2_exit_requirements"], list(b.G2_CRITERIA))
            self.assertEqual(f.batch_scope["owner_test_runtime_exception"], rp.g2_test_exception())
            self.assertNotIn("source_catalogue", f.batch_scope)
            self.assertFalse((f.root / f.TEST).exists())
            self.assertIn("migration_change", rp.g2_catalogue_profile()["forbidden_effects"])
            self.assertIn("migration_change", rp.g2_batch_profile()["forbidden_effects"])
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)

        def test_new_test_addition_uses_real_base_absence_in_all_phases(self):
            f = self.fx
            f.activate_batches()
            frozen = {p: (f.root / p).read_bytes() for p in b.CONTROLLER_PATHS | b.G2_TRANSITION_PATHS}
            f.prepare_migration({f.MIGRATION: b"# authored non-destructive repair\n",
                                  f.TEST: b"# authored preservation regression; never imported\n"})
            self.assertIsNone(f.q["repair_sha256"][f.TEST]["before_sha256"])
            self.assertEqual(set(f.q["payload_sha256"]), b.G2_CATALOGUE_POLICY_PATHS | b.G2_MIGRATION_PATHS)
            run = b.trusted_git.run_git_bytes
            absence_queries = []

            def observed(root, *args, **kwargs):
                if root == f.root and args[:2] == ("ls-tree", "-z"):
                    absence_queries.append(args)
                return run(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git_bytes", side_effect=observed):
                self.assertTrue(f.decision().policy_admitted)
            self.assertIn(("ls-tree", "-z", f.q["base_commit"], "--", f.TEST), absence_queries)
            self.assertEqual(b.operation_effects(f.q["operation_kind"]), b.G2_MIGRATION_EFFECTS)
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)
            f.q["phase"] = "post-push"
            self.assertTrue(f.decision().policy_admitted)
            self.assertTrue(all((f.root / p).read_bytes() == raw for p, raw in frozen.items()))

        def test_present_empty_file_cannot_be_relabelled_as_absent(self):
            f = self.fx
            f.activate_batches()
            f.write(f.TEST, b"")
            f.git("add", "--", f.TEST)
            tree = f.git("write-tree")
            parent = f.git("rev-parse", "HEAD")
            base = f.git("commit-tree", tree, "-p", parent, "-m", "authored existing empty test")
            f.git("update-ref", "--no-deref", "HEAD", base, parent)
            f.prepare_migration({f.TEST: b"# authored test update\n"})
            self.assertEqual(f.q["repair_sha256"][f.TEST]["before_sha256"], b._sha(b""))
            self.assertTrue(f.decision().policy_admitted)
            f.q["repair_sha256"][f.TEST]["before_sha256"] = None
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_migration_addition_already_exists",))

        def test_new_addition_requires_successful_git_absence_observation(self):
            f = self.fx
            f.activate_batches()
            f.prepare_migration({f.TEST: b"# authored new regression\n"})
            self.assertTrue(f.decision().policy_admitted)
            f.q["repair_sha256"][f.TEST]["before_sha256"] = b._sha(b"")
            self.assertEqual(f.decision().reason_codes, ("trusted_git_observation_failed",))
            f.q["repair_sha256"][f.TEST]["before_sha256"] = None
            run = b.trusted_git.run_git_bytes

            def failed(root, *args, **kwargs):
                if root == f.root and args == ("ls-tree", "-z", f.q["base_commit"], "--", f.TEST):
                    raise b.trusted_git.TrustedGitError("authored_absence_observation_failed")
                return run(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git_bytes", side_effect=failed):
                self.assertEqual(f.decision().reason_codes, ("authored_absence_observation_failed",))

        def test_wrong_lane_and_paths_reject_before_selected_reads(self):
            f = self.fx
            f.activate_batches()
            f.prepare_migration({f.MIGRATION: b"# authored repair\n"})
            original = copy.deepcopy(f.q)
            row = original["repair_sha256"][f.MIGRATION]
            cases = [
                (lambda q: q.update(schema_version=b.G2_CATALOGUE_BINDING_VERSION), "bounded_g2_batch_binding_version"),
                (lambda q: q.update(operation_kind="repair_g2_batch"), "bounded_g2_batch_binding_version"),
                (lambda q: q.update(repair_sha256={f.MIGRATION: {"before_sha256": None, "after_sha256": row["after_sha256"]}}),
                 "bounded_g2_batch_change_digest"),
                (lambda q: q.update(repair_sha256={f.TEST: {"before_sha256": None, "after_sha256": None}}),
                 "bounded_g2_batch_change_digest"),
            ]
            for path in ("alembic/env.py", "alembic/versions/unreviewed.py", "../outside.py",
                         "orchestration_harness/bounded_g1b.py", b.STATE, f.AI):
                cases.append((lambda q, path=path: q.update(repair_sha256={path: copy.deepcopy(row)}),
                              "bounded_g2_batch_path_not_allowed"))
            read = b.trusted_git._read_regular_snapshot
            for mutate, reason in cases:
                f.q = copy.deepcopy(original)
                mutate(f.q)
                seen = []

                def observed(path, **kwargs):
                    seen.append(path)
                    return read(path, **kwargs)

                with self.subTest(reason=reason, binding=f.q["repair_sha256"]), \
                        patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                    self.assertEqual(f.decision().reason_codes, (reason,))
                self.assertFalse(any(path.is_relative_to(f.root) for path in seen))
            f.q = original

        def test_unselected_files_are_not_read_and_extra_payload_is_rejected(self):
            f = self.fx
            f.activate_batches()
            f.prepare_migration({f.MIGRATION: b"# selected migration only\n"})
            self.assertNotIn(f.TEST, f.q["payload_sha256"])
            read = b.trusted_git._read_regular_snapshot
            seen = []

            def observed(path, **kwargs):
                seen.append(path)
                self.assertNotEqual(path, f.root / f.TEST)
                return read(path, **kwargs)

            with patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                self.assertTrue(f.decision().policy_admitted)
            self.assertIn(f.assets / "evidence" / rp.G2_MIGRATION_OWNER_RECORD, seen)
            f.q["payload_sha256"][f.TEST] = b._sha(b"unselected")
            with patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_payload_paths",))

        def test_exact_source_preimage_candidate_and_activation_bindings_remain_required(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            f.q["installed_controller"]["source_sha256"] = copy.deepcopy(f.batch_scope["controller_source_sha256"])
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_maintenance_predecessor",))
            f.q["installed_controller"] = copy.deepcopy(b.G2_MIGRATION_PREDECESSOR)
            f.activate_batches()
            f.prepare_migration({f.MIGRATION: b"# exact migration repair\n"})
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            for mutate, reason in (
                (lambda q: q["repair_sha256"][f.MIGRATION].update(before_sha256="0" * 64), "bounded_g2_batch_preimage_changed"),
                (lambda q: q["repair_sha256"][f.MIGRATION].update(after_sha256="0" * 64), "bounded_g2_batch_candidate_changed"),
                (lambda q: q["source_sha256"].update({"orchestration_harness/bounded_g1b.py": "0" * 64}),
                 "bounded_g1b_input_digest_changed"),
                (lambda q: q.update(activation_commit=b.G2_MIGRATION_PREDECESSOR["commit"]), "bounded_g2_batch_activation_binding"),
            ):
                f.q = copy.deepcopy(original)
                mutate(f.q)
                with self.subTest(reason=reason):
                    self.assertEqual(f.decision().reason_codes, (reason,))
            f.q = original

        def test_owner_interpretation_runtime_and_completion_cannot_be_weakened(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            for mutate in (
                lambda s: s["migration_supported_paths"]["owner_decision"].update(sha256="0" * 64),
                lambda s: s["migration_supported_paths"]["successful_paths"].append("populated_legacy_core_database"),
                lambda s: s["migration_supported_paths"]["refusal_preserves"].remove("alembic_revision"),
                lambda s: s["migration_supported_paths"]["directory_records_preserved"].pop(),
                lambda s: s["migration_supported_paths"].update(criterion_acceptance_claimed=True),
                lambda s: s.update(g2_complete=True),
                lambda s: s.update(execution_authorized=True),
                lambda s: s["owner_test_runtime_exception"].update(admission_grants_runtime_authority=True),
                lambda s: s["allowed_additions"].append("alembic/versions/another.py"),
                lambda s: s.update(source_catalogue={"source_binding_sha256": rp.G2_CATALOGUE_SOURCE_BINDING_SHA256}),
            ):
                scope = copy.deepcopy(f.batch_scope)
                mutate(scope)
                raw = b._canonical(scope) + b"\n"
                f.write(b.G2_SCOPE, raw)
                f.q = copy.deepcopy(original)
                f.q["payload_sha256"][b.G2_SCOPE] = b._sha(raw)
                f.q["repair_sha256"][b.G2_SCOPE]["after_sha256"] = b._sha(raw)
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_scope_invalid",))

        def test_owner_record_bytes_must_match_the_pinned_decision(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            read = b.trusted_git._read_regular_snapshot
            owner = f.assets / "evidence" / rp.G2_MIGRATION_OWNER_RECORD

            def changed(path, **kwargs):
                snapshot = read(path, **kwargs)
                return (snapshot[0], b"{}\n") if path == owner else snapshot

            with patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=changed):
                self.assertEqual(f.decision().reason_codes, ("bounded_g1b_input_digest_changed",))

        def test_repair_cannot_change_unowned_state_or_add_runtime_effects(self):
            f = self.fx
            f.activate_batches()
            f.prepare_migration({f.MIGRATION: b"# selected repair\n"})
            self.assertTrue(f.decision().policy_admitted)
            context = f.context()
            manifest = f.manifest(context)
            manifest["intended_side_effect_classes"].append("real_data_access")
            decision = b.evaluate_bounded_g1b_operation(context=context, manifest=manifest,
                entrypoint="task_branch_commit", phase="development")
            self.assertEqual(decision.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
            state = b._json((f.root / b.STATE).read_bytes())
            state["g2"]["completion_accepted"] = True
            raw = b._canonical(state)
            f.write(b.STATE, raw)
            f.q["payload_sha256"][b.STATE] = b._sha(raw)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_unowned_input_changed",))

    class G2InstructionsAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2InstructionsFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        def test_alignment_owns_four_files_and_preserves_migration_authority(self):
            f = self.fx
            context = f.context()
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            report = pf.build_report(f.root, manifest, bounded_context=context,
                                     phase="development", entrypoint="task_branch_commit")
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            self.assertEqual(set(manifest["allowed_paths"]), b.G2_INSTRUCTIONS_MAINTENANCE_PATHS)
            self.assertEqual(len(manifest["allowed_paths"]), 4)
            for path in (b.OVERLAY, b.GATES, "orchestration_harness/raisa_policy.py"):
                previous = {**f.instructions_previous_policy, **f.instructions_previous_source}[path]
                self.assertEqual((f.root / path).read_bytes(), previous)
            before = b._json(f.instructions_previous_policy[b.STATE])
            current = b._json((f.root / b.STATE).read_bytes())
            before["observed_at"] = current["observed_at"]
            before["g2"]["scope_sha256"] = current["g2"]["scope_sha256"]
            self.assertEqual(current, before)
            self.assertFalse(current["g2"]["completion_accepted"])
            self.assertEqual(f.batch_scope["allowed_paths"], sorted(b.G2_MIGRATION_PATHS))
            self.assertEqual(f.batch_scope["maximum_changed_files"], 2)
            self.assertEqual(f.batch_scope["migration_supported_paths"], rp.g2_migration_contract())
            self.assertEqual(f.batch_scope["owner_test_runtime_exception"], rp.g2_test_exception())
            self.assertEqual(f.batch_scope["g2_exit_requirements"], list(b.G2_CRITERIA))
            original = copy.deepcopy(f.q)
            f.q["activation_commit"] = b.G2_MIGRATION_PREDECESSOR["commit"]
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_maintenance_predecessor",))
            f.q["installed_controller"] = copy.deepcopy(b.G2_MIGRATION_PREDECESSOR)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_maintenance_predecessor",))
            f.q = original
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)

        def test_subsequent_two_file_migration_admits_in_all_phases(self):
            f = self.fx
            f.activate_batches()
            frozen = {p: (f.root / p).read_bytes() for p in b.CONTROLLER_PATHS | b.G2_TRANSITION_PATHS}
            f.prepare_migration({f.MIGRATION: b"# authored migration follow-up; never imported\n",
                                  f.TEST: b"# authored regression follow-up; never imported\n"})
            self.assertEqual(f.q["schema_version"], b.G2_INSTRUCTIONS_BINDING_VERSION)
            self.assertEqual(set(b.operation_paths(f.q["operation_kind"], f.q)), b.G2_MIGRATION_PATHS)
            self.assertEqual(set(f.q["payload_sha256"]), b.G2_CATALOGUE_POLICY_PATHS | b.G2_MIGRATION_PATHS)
            self.assertTrue(f.decision().policy_admitted)
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)
            f.q["phase"] = "post-push"
            self.assertTrue(f.decision().policy_admitted)
            self.assertTrue(all((f.root / p).read_bytes() == raw for p, raw in frozen.items()))

        def test_current_instructions_require_exact_published_bytes(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            for raw in (f.instructions_previous_policy[b.AGENTS], f.published_instructions + b"\nextra instruction\n"):
                f.write(b.AGENTS, raw)
                f.q = copy.deepcopy(original)
                f.q["payload_sha256"][b.AGENTS] = b._sha(raw)
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_frozen_input_changed",))

        def test_instruction_publication_and_historical_bytes_are_independently_required(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            run, run_bytes = b.trusted_git.run_git, b.trusted_git.run_git_bytes
            publication = b.G2_INSTRUCTIONS_PUBLICATION

            def missing_ancestor(root, *args, **kwargs):
                if root == f.root and args == ("merge-base", "--is-ancestor", publication["commit"], f.q["base_commit"]):
                    raise b.trusted_git.TrustedGitError("authored_instruction_publication_not_ancestor")
                return run(root, *args, **kwargs)

            with patch.object(b.trusted_git, "run_git", side_effect=missing_ancestor):
                self.assertEqual(f.decision().reason_codes, ("authored_instruction_publication_not_ancestor",))
            def wrong_tree(root, *args, **kwargs):
                if root == f.root and args == ("cat-file", "commit", publication["commit"]):
                    return "tree " + "0" * 40 + "\nparent " + publication["parent"] + "\n\nauthored wrong tree\n"
                return run(root, *args, **kwargs)
            with patch.object(b.trusted_git, "run_git", side_effect=wrong_tree):
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_publication_invalid",))
            for commit, reason in (
                (publication["commit"], "bounded_g2_instructions_publication_bytes_changed"),
                (publication["parent"], "bounded_g2_instructions_publication_bytes_changed"),
                (b.G2_INSTRUCTIONS_PREDECESSOR["commit"], "bounded_g2_instructions_predecessor_bytes_changed"),
                (b.G2_INITIAL_ACTIVATION["commit"], "bounded_g2_batch_historical_bytes_changed"),
            ):
                def changed(root, *args, **kwargs):
                    if root == f.root and args == ("cat-file", "blob", commit + ":" + b.AGENTS):
                        return b"# authored wrong historical instruction bytes\n"
                    return run_bytes(root, *args, **kwargs)
                with self.subTest(commit=commit), patch.object(b.trusted_git, "run_git_bytes", side_effect=changed):
                    self.assertEqual(f.decision().reason_codes, (reason,))

        def test_scope_cannot_generalize_instruction_hash_or_migration_limits(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            for mutate in (
                lambda s: s["current_instruction_policy"].update(sha256="0" * 64),
                lambda s: s["current_instruction_policy"].update(previous_sha256=b.G2_INSTRUCTIONS_SHA256),
                lambda s: s["current_instruction_policy"]["publication"].update(commit="0" * 40),
                lambda s: s["allowed_paths"].append(b.AGENTS),
                lambda s: s.update(maximum_changed_files=3),
                lambda s: s.update(g2_complete=True),
                lambda s: s.update(execution_authorized=True),
                lambda s: s["migration_supported_paths"]["successful_paths"].append("populated_legacy_core_database"),
            ):
                scope = copy.deepcopy(f.batch_scope)
                mutate(scope)
                raw = b._canonical(scope) + b"\n"
                f.write(b.G2_SCOPE, raw)
                f.q = copy.deepcopy(original)
                f.q["payload_sha256"][b.G2_SCOPE] = b._sha(raw)
                f.q["repair_sha256"][b.G2_SCOPE]["after_sha256"] = b._sha(raw)
                self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_scope_invalid",))

        def test_alignment_cannot_own_instructions_profile_or_other_repair_paths(self):
            f = self.fx
            original = copy.deepcopy(f.q)
            row = original["repair_sha256"][b.STATE]
            cases = [(lambda q: q["repair_sha256"].pop(b.STATE), "bounded_g2_batch_path_not_allowed"),
                     (lambda q: q.update(schema_version=b.G2_MIGRATION_BINDING_VERSION), "bounded_g2_batch_binding_version"),
                     (lambda q: q.update(operation_kind="enable_g2_migration"), "bounded_g2_batch_binding_version"),
                     (lambda q: q.update(operation_kind="repair_g2_batch"), "bounded_g2_batch_binding_version")]
            for path in (b.AGENTS, b.OVERLAY, "orchestration_harness/raisa_policy.py", f.MIGRATION):
                cases.append((lambda q, path=path: q["repair_sha256"].update({path: copy.deepcopy(row)}),
                              "bounded_g2_batch_path_not_allowed"))
            read = b.trusted_git._read_regular_snapshot
            for mutate, reason in cases:
                f.q = copy.deepcopy(original)
                mutate(f.q)
                seen = []
                def observed(path, **kwargs):
                    seen.append(path)
                    return read(path, **kwargs)
                with self.subTest(reason=reason), patch.object(b.trusted_git, "_read_regular_snapshot", side_effect=observed):
                    self.assertEqual(f.decision().reason_codes, (reason,))
                self.assertFalse(any(path.is_relative_to(f.root) for path in seen))

        def test_old_v3_does_not_gain_a_current_instruction_hash_exception(self):
            previous = G2MigrationFixture(assets)
            self.addCleanup(previous.close)
            with previous.component_history():
                self.assertTrue(previous.decision().policy_admitted)
                previous.write(b.AGENTS, self.fx.published_instructions)
                previous.q["payload_sha256"][b.AGENTS] = b.G2_INSTRUCTIONS_SHA256
                self.assertEqual(previous.decision().reason_codes, ("bounded_g2_batch_frozen_input_changed",))

    class G2AudioAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2AudioFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        def test_exact_activation_then_four_path_repair_admit_without_runtime_authority(self):
            f = self.fx
            context = f.context()
            manifest = pf.build_task_manifest(f.root, bounded_context=context)
            report = pf.build_report(
                f.root, manifest, bounded_context=context,
                phase="development", entrypoint="task_branch_commit")
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            self.assertEqual(set(manifest["allowed_paths"]), b.G2_AUDIO_MAINTENANCE_PATHS)
            self.assertEqual(len(manifest["allowed_paths"]), 6)
            self.assertEqual(f.batch_scope["allowed_paths"], sorted(b.G2_AUDIO_PATHS))
            self.assertEqual(f.batch_scope["allowed_additions"], [f.TEST])
            self.assertEqual(
                f.batch_scope["current_instruction_policy"]["sha256"],
                b.G2_AUDIO_INSTRUCTIONS_SHA256)
            self.assertEqual((f.root / b.AGENTS).read_bytes(), f.current_instructions)
            self.assertFalse(f.batch_scope["execution_authorized"])
            self.assertFalse(f.batch_scope["feature_work_eligible"])
            self.assertFalse(f.batch_scope["g2_complete"])
            self.assertTrue(f.decision().policy_admitted)

            f.activate_batches()
            changes = {
                f.MAIN: b"# authored main privacy repair; never imported\n",
                f.CONSULTATION: b"# authored consultation privacy repair; never imported\n",
                f.SIDEBAR: b"// authored object URL repair; never executed\n",
                f.TEST: b"# authored focused privacy regression; never imported\n",
            }
            f.prepare_audio(changes)
            self.assertEqual(set(f.q["repair_sha256"]), b.G2_AUDIO_PATHS)
            self.assertIsNone(f.q["repair_sha256"][f.TEST]["before_sha256"])
            self.assertIn(f.SIDEBAR, f.q["repair_sha256"])
            self.assertEqual(set(f.manifest(f.context())["allowed_paths"]), b.G2_AUDIO_PATHS)
            self.assertEqual(b.operation_effects(f.q["operation_kind"]), b.G2_AUDIO_EFFECTS)
            self.assertTrue(f.decision().policy_admitted)
            f.commit_current()
            self.assertTrue(f.decision().policy_admitted)
            f.q["phase"] = "post-push"
            self.assertTrue(f.decision().policy_admitted)

        def test_stale_current_instructions_and_trusted_git_source_are_denied(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            f.write(b.AGENTS, f.audio_previous_policy[b.AGENTS])
            f.q["payload_sha256"][b.AGENTS] = b._sha(f.audio_previous_policy[b.AGENTS])
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_frozen_input_changed",))
            f.write(b.AGENTS, f.current_instructions)
            f.q = copy.deepcopy(original)
            f.q["source_sha256"]["orchestration_harness/trusted_git.py"] = b._sha(
                f.audio_previous_source["orchestration_harness/trusted_git.py"])
            self.assertEqual(f.decision().reason_codes, ("bounded_g1b_git_source_changed",))

        def test_scope_addition_and_runtime_effect_expansion_are_denied(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            scope = copy.deepcopy(f.batch_scope)
            scope["allowed_paths"].append("app/not-reviewed.py")
            raw = b._canonical(scope) + b"\n"
            f.write(b.G2_SCOPE, raw)
            f.q["payload_sha256"][b.G2_SCOPE] = b._sha(raw)
            f.q["repair_sha256"][b.G2_SCOPE]["after_sha256"] = b._sha(raw)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_scope_invalid",))
            f.write(b.G2_SCOPE, b._canonical(f.batch_scope) + b"\n")
            f.q = original

            f.activate_batches()
            changes = {
                f.MAIN: b"# authored main repair\n",
                f.CONSULTATION: b"# authored consultation repair\n",
                f.SIDEBAR: b"// authored sidebar repair\n",
                f.TEST: b"# authored focused test\n",
            }
            f.prepare_audio(changes)
            saved_repair = copy.deepcopy(f.q)
            f.q["repair_sha256"]["tests/not-reviewed.py"] = f.q["repair_sha256"].pop(f.TEST)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_path_not_allowed",))
            f.q = saved_repair
            context = f.context()
            manifest = f.manifest(context)
            manifest["intended_side_effect_classes"].append("provider_invocation")
            decision = b.evaluate_bounded_g1b_operation(
                context=context, manifest=manifest,
                entrypoint="recovery_preflight", phase=f.q["phase"])
            self.assertFalse(decision.policy_admitted)
            self.assertEqual(decision.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))

    class G2PatientAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2PatientFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        @staticmethod
        def repair_changes(f):
            return {
                f.CONSULTATION: b"# authored explicit patient consultation repair; never imported\n",
                f.SIDEBAR: b"// authored explicit patient sidebar guard; never executed\n",
                f.AUDIO_TEST: b"# authored retained audio privacy regression with explicit patient\n",
                f.PATIENT_TEST: b"# authored patient binding regression; never imported\n",
            }

        def assert_full_admission(self, f):
            context = f.context()
            manifest = f.manifest(context)
            entrypoint = {
                "development": "task_branch_commit",
                "pre-push": "task_branch_push",
                "post-push": "task_branch_push",
            }[f.q["phase"]]
            report = pf.build_report(
                f.root, manifest, bounded_context=context,
                phase=f.q["phase"], entrypoint=entrypoint)
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            for decision in (
                pa.evaluate_programme_operation_admission(
                    repo_root=f.root, manifest=manifest, entrypoint=entrypoint,
                    phase=f.q["phase"], bounded_context=context),
                pg.evaluate_pinned_programme_operation(
                    gatekeeper_root=f.source, target_repo_root=f.root, manifest=manifest,
                    entrypoint=entrypoint, phase=f.q["phase"], bounded_context=context),
            ):
                self.assertTrue(decision.policy_admitted, decision.reason_codes)
                self.assertFalse(decision.execution_authorized)
                self.assertEqual(decision.candidate_tree, f.q["candidate_tree"])

        def test_exact_transition_then_activation_and_four_path_repair_lifecycle(self):
            f = self.fx
            before_state = b._json(f.patient_previous_policy[b.STATE])
            expected_state = copy.deepcopy(before_state)
            scope_raw = b._canonical(f.batch_scope) + b"\n"
            expected_state["observed_at"] = f.batch_scope["recorded_at"]
            expected_state["g2"].update(
                scope_sha256=b._sha(scope_raw),
                current_operation=copy.deepcopy(f.batch_scope["current_operation"]))
            expected_state["task_selection"]["next_eligibility_condition"] = (
                "bounded_G2_patient_binding_repair_active")
            self.assertEqual(b._json((f.root / b.STATE).read_bytes()), expected_state)
            before_overlay = b._document(f.patient_previous_policy[b.OVERLAY], b.OVERLAY)
            before_overlay["profiles"][b.G2_PROFILE] = rp.g2_patient_binding_profile()
            self.assertEqual(b._document((f.root / b.OVERLAY).read_bytes(), b.OVERLAY), before_overlay)
            self.assertEqual((f.root / b.G2_SCOPE).read_bytes(), scope_raw)
            self.assertEqual(set(f.q["repair_sha256"]), b.G2_PATIENT_MAINTENANCE_PATHS)
            self.assertEqual(len(f.q["repair_sha256"]), 6)
            self.assert_full_admission(f)

            f.activate_batches()
            f.prepare_patient(self.repair_changes(f))
            self.assertEqual(set(f.q["repair_sha256"]), b.G2_PATIENT_PATHS)
            self.assertIsNone(f.q["repair_sha256"][f.PATIENT_TEST]["before_sha256"])
            self.assertIsNotNone(f.q["repair_sha256"][f.AUDIO_TEST]["before_sha256"])
            self.assert_full_admission(f)
            f.commit_current()
            self.assertEqual(f.q["phase"], "pre-push")
            self.assert_full_admission(f)
            f.q["phase"] = "post-push"
            self.assert_full_admission(f)

        def test_stale_v5_controller_and_stale_patient_policy_are_denied(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            f.q["installed_controller"] = copy.deepcopy(b.G2_AUDIO_PREDECESSOR)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_maintenance_predecessor",))
            f.q = original
            state = b._json((f.root / b.STATE).read_bytes())
            state["task_selection"]["next_eligibility_condition"] = "bounded_G2_audio_privacy_repair_active"
            raw = (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode()
            f.restage(b.STATE, raw, repair_after=True)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_policy_delta_invalid",))

        def test_predecessor_and_audio_publication_history_are_exact(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original_header = f.audio_publication_header
            f.audio_publication_header = (
                "tree " + "0" * 40 + "\nparent " + b.G2_AUDIO_REPAIR_PUBLICATION["parent"]
                + "\n\nauthored wrong tree\n")
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_publication_invalid",))
            f.audio_publication_header = original_header
            path = "app/routers/consultation.py"
            original_audio = f.audio_publication_source[path]
            f.audio_publication_source[path] = b"# authored changed published audio blob\n"
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_patient_audio_publication_bytes_changed",))
            f.audio_publication_source[path] = original_audio
            source_path = "orchestration_harness/bounded_g1b.py"
            f.patient_previous_source[source_path] = b"# authored stale v5 controller bytes\n"
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_patient_predecessor_bytes_changed",))

        def test_scope_and_repair_path_or_runtime_effect_expansion_are_denied(self):
            f = self.fx
            scope = copy.deepcopy(f.batch_scope)
            scope["allowed_paths"].append("app/not-reviewed.py")
            raw = b._canonical(scope) + b"\n"
            f.restage(b.G2_SCOPE, raw, repair_after=True)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_scope_invalid",))

            other = G2PatientFixture(assets)
            self.addCleanup(other.close)
            with no_legacy_observation(), other.component_history():
                other.activate_batches()
                other.prepare_patient(self.repair_changes(other))
                original = copy.deepcopy(other.q)
                row = other.q["repair_sha256"].pop(other.PATIENT_TEST)
                other.q["repair_sha256"]["tests/not-reviewed.py"] = row
                self.assertEqual(other.decision().reason_codes, ("bounded_g2_batch_path_not_allowed",))
                other.q = original
                context = other.context()
                manifest = other.manifest(context)
                manifest["intended_side_effect_classes"].append("provider_invocation")
                decision = b.evaluate_bounded_g1b_operation(
                    context=context, manifest=manifest,
                    entrypoint="recovery_preflight", phase=other.q["phase"])
                self.assertEqual(
                    decision.reason_codes, ("bounded_g1b_manifest_binding_mismatch",))
                self.assertFalse(decision.execution_authorized)

        def test_wrong_addition_substitution_and_existing_audio_none_are_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_patient(self.repair_changes(f))
            original = copy.deepcopy(f.q)
            row = f.q["repair_sha256"].pop(f.PATIENT_TEST)
            f.q["repair_sha256"]["tests/not-reviewed.py"] = row
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_path_not_allowed",))
            f.q = copy.deepcopy(original)
            f.q["repair_sha256"][f.AUDIO_TEST]["before_sha256"] = None
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_change_digest",))

        def test_candidate_and_preimage_drift_are_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_patient(self.repair_changes(f))
            original = copy.deepcopy(f.q)
            f.q["repair_sha256"][f.CONSULTATION]["before_sha256"] = "0" * 64
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_preimage_changed",))
            f.q = copy.deepcopy(original)
            f.q["repair_sha256"][f.CONSULTATION]["after_sha256"] = "0" * 64
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_candidate_changed",))

        def test_unowned_input_drift_is_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_patient(self.repair_changes(f))
            state = b._json((f.root / b.STATE).read_bytes())
            state["observed_at"] = "2026-09-15T00:00:01+00:00"
            raw = (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode()
            f.restage(b.STATE, raw)
            self.assertEqual(f.decision().reason_codes, ("bounded_g2_batch_unowned_input_changed",))

    class G2AtomicityAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2AtomicityFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        @staticmethod
        def repair_changes(f):
            return {
                f.CONSULTATION: (
                    b"# authored atomic consultation transaction repair; never imported\n"
                ),
                f.AUDIO_TEST: (
                    b"# authored retained audio component with UUID return; never imported\n"
                ),
                f.PATIENT_TEST: (
                    b"# authored retained patient component with UUID assertion; never imported\n"
                ),
                f.ATOMICITY_TEST: (
                    b"# authored finalize atomicity regression; never imported\n"
                ),
            }

        def assert_full_admission(self, f):
            context = f.context()
            manifest = f.manifest(context)
            entrypoint = {
                "development": "task_branch_commit",
                "pre-push": "task_branch_push",
                "post-push": "task_branch_push",
            }[f.q["phase"]]
            report = pf.build_report(
                f.root,
                manifest,
                bounded_context=context,
                phase=f.q["phase"],
                entrypoint=entrypoint,
            )
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            for decision in (
                pa.evaluate_programme_operation_admission(
                    repo_root=f.root,
                    manifest=manifest,
                    entrypoint=entrypoint,
                    phase=f.q["phase"],
                    bounded_context=context,
                ),
                pg.evaluate_pinned_programme_operation(
                    gatekeeper_root=f.source,
                    target_repo_root=f.root,
                    manifest=manifest,
                    entrypoint=entrypoint,
                    phase=f.q["phase"],
                    bounded_context=context,
                ),
            ):
                self.assertTrue(decision.policy_admitted, decision.reason_codes)
                self.assertFalse(decision.execution_authorized)
                self.assertEqual(decision.candidate_tree, f.q["candidate_tree"])

        def test_exact_transition_then_activation_and_four_path_repair_lifecycle(self):
            f = self.fx
            before_state = b._json(f.atomicity_previous_policy[b.STATE])
            expected_state = copy.deepcopy(before_state)
            scope_raw = b._canonical(f.batch_scope) + b"\n"
            expected_state["observed_at"] = f.batch_scope["recorded_at"]
            expected_state["g2"].update(
                scope_sha256=b._sha(scope_raw),
                current_operation=copy.deepcopy(
                    f.batch_scope["current_operation"]
                ),
            )
            expected_state["task_selection"]["next_eligibility_condition"] = (
                "bounded_G2_consultation_atomicity_repair_active"
            )
            self.assertEqual(
                b._json((f.root / b.STATE).read_bytes()),
                expected_state,
            )
            before_overlay = b._document(
                f.atomicity_previous_policy[b.OVERLAY],
                b.OVERLAY,
            )
            before_overlay["profiles"][b.G2_PROFILE] = (
                rp.g2_consultation_atomicity_profile()
            )
            self.assertEqual(
                b._document((f.root / b.OVERLAY).read_bytes(), b.OVERLAY),
                before_overlay,
            )
            self.assertEqual((f.root / b.G2_SCOPE).read_bytes(), scope_raw)
            self.assertEqual(
                set(f.q["repair_sha256"]),
                b.G2_ATOMICITY_MAINTENANCE_PATHS,
            )
            self.assertEqual(len(f.q["repair_sha256"]), 6)
            self.assert_full_admission(f)

            f.activate_batches()
            f.prepare_atomicity(self.repair_changes(f))
            self.assertEqual(
                set(f.q["repair_sha256"]),
                b.G2_ATOMICITY_PATHS,
            )
            self.assertIsNone(
                f.q["repair_sha256"][f.ATOMICITY_TEST]["before_sha256"]
            )
            for path in (
                f.CONSULTATION,
                f.AUDIO_TEST,
                f.PATIENT_TEST,
            ):
                self.assertIsNotNone(
                    f.q["repair_sha256"][path]["before_sha256"]
                )
            self.assert_full_admission(f)
            f.commit_current()
            self.assertEqual(f.q["phase"], "pre-push")
            self.assert_full_admission(f)
            f.q["phase"] = "post-push"
            self.assert_full_admission(f)

        def test_stale_v6_controller_and_stale_atomicity_policy_are_denied(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            f.q["installed_controller"] = copy.deepcopy(
                b.G2_PATIENT_PREDECESSOR
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_maintenance_predecessor",),
            )
            f.q = original
            state = b._json((f.root / b.STATE).read_bytes())
            state["task_selection"]["next_eligibility_condition"] = (
                "bounded_G2_patient_binding_repair_active"
            )
            raw = (
                json.dumps(state, indent=2, ensure_ascii=False) + "\n"
            ).encode()
            f.restage(b.STATE, raw, repair_after=True)
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_policy_delta_invalid",),
            )

        def test_predecessor_and_patient_publication_history_are_exact(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original_header = f.patient_publication_header
            f.patient_publication_header = (
                "tree " + "0" * 40 + "\nparent "
                + b.G2_PATIENT_REPAIR_PUBLICATION["parent"]
                + "\n\nauthored wrong tree\n"
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_publication_invalid",),
            )
            f.patient_publication_header = original_header
            path = "app/routers/consultation.py"
            original_patient = f.patient_publication_source[path]
            f.patient_publication_source[path] = (
                b"# authored changed published patient blob\n"
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_atomicity_patient_publication_bytes_changed",),
            )
            f.patient_publication_source[path] = original_patient
            source_path = "orchestration_harness/bounded_g1b.py"
            original_source = f.atomicity_previous_source[source_path]
            f.atomicity_previous_source[source_path] = (
                b"# authored stale v6 controller bytes\n"
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_atomicity_predecessor_bytes_changed",),
            )
            f.atomicity_previous_source[source_path] = original_source

        def test_source_digest_and_scope_version_are_denied(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            source_path = "orchestration_harness/bounded_g1b.py"
            original = f.q["source_sha256"][source_path]
            f.q["source_sha256"][source_path] = "0" * 64
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g1b_input_digest_changed",),
            )
            f.q["source_sha256"][source_path] = original

            scope = copy.deepcopy(f.batch_scope)
            scope["schema_version"] = "ariadne.g2_reviewed_batch_scope.future"
            raw = b._canonical(scope) + b"\n"
            f.restage(b.G2_SCOPE, raw, repair_after=True)
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_atomicity_scope_binding_mismatch",),
            )

        def test_scope_path_and_runtime_effect_expansion_are_denied(self):
            f = self.fx
            scope = copy.deepcopy(f.batch_scope)
            scope["allowed_paths"].append("app/not-reviewed.py")
            raw = b._canonical(scope) + b"\n"
            f.restage(b.G2_SCOPE, raw, repair_after=True)
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_scope_invalid",),
            )

            other = G2AtomicityFixture(assets)
            self.addCleanup(other.close)
            with no_legacy_observation(), other.component_history():
                other.activate_batches()
                other.prepare_atomicity(self.repair_changes(other))
                original = copy.deepcopy(other.q)
                row = other.q["repair_sha256"].pop(other.ATOMICITY_TEST)
                other.q["repair_sha256"]["tests/not-reviewed.py"] = row
                self.assertEqual(
                    other.decision().reason_codes,
                    ("bounded_g2_batch_path_not_allowed",),
                )
                other.q = original
                context = other.context()
                manifest = other.manifest(context)
                manifest["intended_side_effect_classes"].append(
                    "provider_invocation"
                )
                decision = b.evaluate_bounded_g1b_operation(
                    context=context,
                    manifest=manifest,
                    entrypoint="recovery_preflight",
                    phase=other.q["phase"],
                )
                self.assertEqual(
                    decision.reason_codes,
                    ("bounded_g1b_manifest_binding_mismatch",),
                )
                self.assertFalse(decision.execution_authorized)

        def test_wrong_addition_substitution_and_existing_component_none_are_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_atomicity(self.repair_changes(f))
            original = copy.deepcopy(f.q)
            row = f.q["repair_sha256"].pop(f.ATOMICITY_TEST)
            f.q["repair_sha256"]["tests/not-reviewed.py"] = row
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_path_not_allowed",),
            )
            f.q = copy.deepcopy(original)
            f.q["repair_sha256"][f.AUDIO_TEST]["before_sha256"] = None
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_change_digest",),
            )

        def test_candidate_and_preimage_drift_are_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_atomicity(self.repair_changes(f))
            original = copy.deepcopy(f.q)
            f.q["repair_sha256"][f.CONSULTATION]["before_sha256"] = (
                "0" * 64
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_preimage_changed",),
            )
            f.q = copy.deepcopy(original)
            f.q["repair_sha256"][f.CONSULTATION]["after_sha256"] = (
                "0" * 64
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_candidate_changed",),
            )

        def test_unowned_input_drift_is_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_atomicity(self.repair_changes(f))
            state = b._json((f.root / b.STATE).read_bytes())
            state["observed_at"] = "2026-09-15T03:00:01+00:00"
            raw = (
                json.dumps(state, indent=2, ensure_ascii=False) + "\n"
            ).encode()
            f.restage(b.STATE, raw)
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_unowned_input_changed",),
            )


    class G2ClinicalAdmissionTests(unittest.TestCase):
        def setUp(self):
            self.fx = G2ClinicalFixture(assets)
            self.addCleanup(self.fx.close)
            self.stack = ExitStack()
            self.addCleanup(self.stack.close)
            self.stack.enter_context(no_legacy_observation())
            self.stack.enter_context(self.fx.component_history())

        @staticmethod
        def repair_changes(f):
            return {
                f.CONSULTATION: b"# authored GP authority repair; never imported\n",
                f.AUDIT_EVENTS: b"# authored attestation audit repair; never imported\n",
                f.SIDEBAR: b"// authored explicit attestation control; never executed\n",
                f.AUDIO_TEST: b"# authored retained audio privacy regression\n",
                f.PATIENT_TEST: b"# authored retained patient binding regression\n",
                f.ATOMICITY_TEST: b"# authored retained finalize atomicity regression\n",
            }

        def assert_full_admission(self, f):
            context = f.context()
            manifest = f.manifest(context)
            entrypoint = {
                "development": "task_branch_commit",
                "pre-push": "task_branch_push",
                "post-push": "task_branch_push",
            }[f.q["phase"]]
            report = pf.build_report(
                f.root,
                manifest,
                bounded_context=context,
                phase=f.q["phase"],
                entrypoint=entrypoint,
            )
            self.assertEqual(report["status"], "policy_eligible", report)
            self.assertFalse(report["execution_authorized"])
            for decision in (
                pa.evaluate_programme_operation_admission(
                    repo_root=f.root,
                    manifest=manifest,
                    entrypoint=entrypoint,
                    phase=f.q["phase"],
                    bounded_context=context,
                ),
                pg.evaluate_pinned_programme_operation(
                    gatekeeper_root=f.source,
                    target_repo_root=f.root,
                    manifest=manifest,
                    entrypoint=entrypoint,
                    phase=f.q["phase"],
                    bounded_context=context,
                ),
            ):
                self.assertTrue(decision.policy_admitted, decision.reason_codes)
                self.assertFalse(decision.execution_authorized)
                self.assertEqual(decision.candidate_tree, f.q["candidate_tree"])

        def test_exact_transition_then_six_file_repair_admits_in_all_phases(self):
            f = self.fx
            before_state = b._json(f.clinical_previous_policy[b.STATE])
            expected_state = copy.deepcopy(before_state)
            scope_raw = b._canonical(f.batch_scope) + b"\n"
            expected_state["observed_at"] = f.batch_scope["recorded_at"]
            expected_state["g2"].update(
                scope_sha256=b._sha(scope_raw),
                current_operation=copy.deepcopy(
                    f.batch_scope["current_operation"]
                ),
            )
            expected_state["task_selection"]["next_eligibility_condition"] = (
                "bounded_G2_clinical_authority_repair_active"
            )
            self.assertEqual(
                b._json((f.root / b.STATE).read_bytes()), expected_state
            )
            before_overlay = b._document(
                f.clinical_previous_policy[b.OVERLAY], b.OVERLAY
            )
            before_overlay["profiles"][b.G2_PROFILE] = (
                rp.g2_clinical_authority_profile()
            )
            self.assertEqual(
                b._document((f.root / b.OVERLAY).read_bytes(), b.OVERLAY),
                before_overlay,
            )
            self.assertEqual((f.root / b.G2_SCOPE).read_bytes(), scope_raw)
            self.assertEqual(
                set(f.q["repair_sha256"]),
                b.G2_CLINICAL_MAINTENANCE_PATHS,
            )
            self.assertEqual(len(f.q["repair_sha256"]), 6)
            self.assertFalse(f.batch_scope["execution_authorized"])
            self.assertFalse(f.batch_scope["g2_complete"])
            self.assert_full_admission(f)

            f.activate_batches()
            f.prepare_clinical(self.repair_changes(f))
            self.assertEqual(set(f.q["repair_sha256"]), b.G2_CLINICAL_PATHS)
            self.assertTrue(all(
                row["before_sha256"] is not None
                for row in f.q["repair_sha256"].values()
            ))
            self.assert_full_admission(f)
            f.commit_current()
            self.assertEqual(f.q["phase"], "pre-push")
            self.assert_full_admission(f)
            f.q["phase"] = "post-push"
            self.assert_full_admission(f)

        def test_current_operation_supersedes_atomicity_without_opening_global_gates(self):
            f = self.fx
            operation = f.batch_scope["current_operation"]
            self.assertEqual(
                operation["operation_id"], "g2-clinical-authority-repair"
            )
            self.assertEqual(
                operation["supersedes"]["operation_id"],
                "g2-consultation-atomicity-repair",
            )
            self.assertEqual(f.batch_scope["global_gate"], "red_repair_only")
            self.assertFalse(f.batch_scope["execution_authorized"])
            self.assertFalse(f.batch_scope["feature_work_eligible"])
            self.assertFalse(f.batch_scope["g2_complete"])
            self.assertEqual(
                f.batch_scope["clinical_authority_contract"],
                rp.g2_clinical_authority_contract(),
            )
            self.assertTrue(f.decision().policy_admitted)

        def test_stale_v7_controller_and_stale_clinical_policy_are_denied(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original = copy.deepcopy(f.q)
            f.q["installed_controller"] = copy.deepcopy(
                b.G2_ATOMICITY_PREDECESSOR
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_maintenance_predecessor",),
            )
            f.q = original
            state = b._json((f.root / b.STATE).read_bytes())
            state["task_selection"]["next_eligibility_condition"] = (
                "bounded_G2_consultation_atomicity_repair_active"
            )
            raw = (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode()
            f.restage(b.STATE, raw, repair_after=True)
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_policy_delta_invalid",),
            )

        def test_predecessor_and_atomicity_publication_are_independently_exact(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            original_header = f.atomicity_publication_header
            f.atomicity_publication_header = (
                "tree " + "0" * 40 + "\nparent "
                + b.G2_ATOMICITY_REPAIR_PUBLICATION["parent"]
                + "\n\nauthored wrong tree\n"
            )
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_publication_invalid",),
            )
            f.atomicity_publication_header = original_header
            path = "app/routers/consultation.py"
            original_publication = f.atomicity_publication_source[path]
            f.atomicity_publication_source[path] = b"# changed publication blob\n"
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_clinical_atomicity_publication_bytes_changed",),
            )
            f.atomicity_publication_source[path] = original_publication
            source_path = "orchestration_harness/bounded_g1b.py"
            original_source = f.clinical_previous_source[source_path]
            f.clinical_previous_source[source_path] = b"# stale v7 controller bytes\n"
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_clinical_predecessor_bytes_changed",),
            )
            f.clinical_previous_source[source_path] = original_source

        def test_owner_record_changed_or_missing_is_denied_as_authenticated_input(self):
            f = self.fx
            self.assertTrue(f.decision().policy_admitted)
            read = b.trusted_git._read_regular_snapshot
            owner = f.assets / "evidence" / rp.G2_CLINICAL_OWNER_RECORD

            def changed(path, **kwargs):
                snapshot = read(path, **kwargs)
                return (snapshot[0], b"{}\n") if path == owner else snapshot

            with patch.object(
                b.trusted_git, "_read_regular_snapshot", side_effect=changed
            ):
                self.assertEqual(
                    f.decision().reason_codes,
                    ("bounded_g1b_input_digest_changed",),
                )

            def missing(path, **kwargs):
                if path == owner:
                    raise FileNotFoundError(path)
                return read(path, **kwargs)

            with patch.object(
                b.trusted_git, "_read_regular_snapshot", side_effect=missing
            ):
                self.assertEqual(
                    f.decision().reason_codes,
                    ("bounded_g1b_invalid_input",),
                )

        def test_scope_drift_and_clinical_authority_expansion_are_denied(self):
            f = self.fx
            for mutate in (
                lambda s: s["allowed_paths"].append("app/not-reviewed.py"),
                lambda s: s["clinical_authority_contract"].update(
                    roles=["GP", "NURSE"]
                ),
                lambda s: s["clinical_authority_contract"]["owner_decision"].update(
                    sha256="0" * 64
                ),
                lambda s: s["clinical_authority_contract"]["attestation_transport"].update(only_literal_true_authorizes=False),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(bounded_finalization_path_never_updates_or_deletes_receipt=False),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(database_immutability_enforced=True),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(database_retention_enforced=True),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(receipt_retention_required_for_replay=False),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(receipt_loss_or_undetectable_mutation_outside_accepted_guarantee=False),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(detectable_receipt_or_target_corruption="accept"),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(known_receipt_loss_or_mutation="retry_automatically"),
                lambda s: s["clinical_authority_contract"]["idempotency_receipt"]["retention_and_schema"].update(production_durable_idempotency_accepted=True),
                lambda s: s["clinical_authority_contract"]["authority_transaction"].update(lock_and_recheck_order=["Patient"]),
                lambda s: s["clinical_authority_contract"]["practitioner_attribution"].update(source="client_practitioner_id"),
                lambda s: s["clinical_authority_contract"]["attestation_audit"].update(event_type="ai.invocation.allowed"),
                lambda s: s["clinical_authority_contract"]["attestation_audit"]["metadata_keys"].remove("reviewed_content_sha256"),
                lambda s: s["clinical_authority_contract"]["taskpane_confirmation"].update(patient_or_reviewed_content_change_requires_fresh_confirmation=False),
                lambda s: s["clinical_authority_contract"]["synthetic_staff_practitioners_and_patients_standing_authority"]["permitted_entities"].remove("fictional_practitioners"),
                lambda s: s.update(execution_authorized=True),
            ):
                scope = copy.deepcopy(f.batch_scope)
                mutate(scope)
                raw = b._canonical(scope) + b"\n"
                try:
                    f.restage(b.G2_SCOPE, raw, repair_after=True)
                    self.assertEqual(
                        f.decision().reason_codes,
                        ("bounded_g2_batch_scope_invalid",),
                    )
                finally:
                    f.restage(b.G2_SCOPE, b._canonical(f.batch_scope) + b"\n", repair_after=True)

        def test_changed_path_null_preimage_and_runtime_effect_are_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_clinical(self.repair_changes(f))
            original = copy.deepcopy(f.q)
            row = f.q["repair_sha256"].pop(f.AUDIT_EVENTS)
            f.q["repair_sha256"]["app/not-reviewed.py"] = row
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_path_not_allowed",),
            )
            f.q = copy.deepcopy(original)
            f.q["repair_sha256"][f.AUDIO_TEST]["before_sha256"] = None
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_change_digest",),
            )
            f.q = original
            context = f.context()
            manifest = f.manifest(context)
            manifest["intended_side_effect_classes"].append("provider_invocation")
            decision = b.evaluate_bounded_g1b_operation(
                context=context,
                manifest=manifest,
                entrypoint="task_branch_commit",
                phase=f.q["phase"],
            )
            self.assertEqual(
                decision.reason_codes,
                ("bounded_g1b_manifest_binding_mismatch",),
            )
            self.assertFalse(decision.execution_authorized)

        def test_candidate_preimage_and_unowned_input_drift_are_denied(self):
            f = self.fx
            f.activate_batches()
            f.prepare_clinical(self.repair_changes(f))
            original = copy.deepcopy(f.q)
            f.q["repair_sha256"][f.CONSULTATION]["before_sha256"] = "0" * 64
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_preimage_changed",),
            )
            f.q = copy.deepcopy(original)
            f.q["repair_sha256"][f.CONSULTATION]["after_sha256"] = "0" * 64
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_candidate_changed",),
            )
            f.q = copy.deepcopy(original)
            state = b._json((f.root / b.STATE).read_bytes())
            state["observed_at"] = "2026-09-15T06:00:01+00:00"
            raw = (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode()
            f.restage(b.STATE, raw)
            self.assertEqual(
                f.decision().reason_codes,
                ("bounded_g2_batch_unowned_input_changed",),
            )


    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClosedRequestTests)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2AudioSourceContractTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2PatientSourceContractTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2AtomicitySourceContractTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2ClinicalSourceContractTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(IntegratedTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SuccessorTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ProvenanceAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigurationTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigurationAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2AdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2BatchAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2CatalogueAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2MigrationAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2InstructionsAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2AudioAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2PatientAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2AtomicityAdmissionTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(G2ClinicalAdmissionTests))
    return suite
