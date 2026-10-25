"""Source-only G4 Compass entry checks; no Clockwork or product runtime."""

import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from orchestration_harness import bounded_g1b, programme_admission, raisa_policy


def _scope():
    return {
        "schema_version": bounded_g1b.G4_COMPASS_ENTRY_SCHEMA,
        "recorded_at": "2026-10-25T00:00:00+00:00",
        "selected_base": bounded_g1b.G4_COMPASS_ENTRY_BASE,
        "active_profile": raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE,
        "predecessor_scope_sha256": bounded_g1b.G4_COMPASS_ENTRY_PREDECESSOR_SHA,
        "control_paths": sorted(bounded_g1b.G4_COMPASS_ENTRY_CONTROL),
        "source_paths": sorted(bounded_g1b.G4_COMPASS_ENTRY_SOURCE),
        "allowed_effects": sorted(bounded_g1b.EFFECTS | {"product_behavior_change"}),
        "closed_entrypoints": ["clockwork_closeout_mutation", "clockwork_tick_mutation"],
        "canonical_effects_authorized": False,
        "runtime_authorized": False,
        "source_sha256": {p: "a" * 64 for p in
                          bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS},
        "control_sha256": {p: "a" * 64 for p in
                           bounded_g1b.G4_COMPASS_ENTRY_CONTROL -
                           {bounded_g1b.G4_COMPASS_ENTRY_SCOPE}},
    }


def _binding(stage):
    paths = (bounded_g1b.G4_COMPASS_ENTRY_CONTROL if stage == "enable"
             else bounded_g1b.G4_COMPASS_ENTRY_SOURCE)
    return {"schema_version": bounded_g1b.G4_COMPASS_ENTRY_SCHEMA,
            "operation_kind": bounded_g1b.G4_COMPASS_ENTRY_KIND,
            "stage": stage,
            "repair_sha256": {p: {} for p in paths}}


def test_source_entry_has_exact_distinct_stage_paths():
    enable = bounded_g1b.operation_paths(bounded_g1b.G4_COMPASS_ENTRY_KIND,
                                         _binding("enable"))
    apply = bounded_g1b.operation_paths(bounded_g1b.G4_COMPASS_ENTRY_KIND,
                                        _binding("apply"))
    assert enable == bounded_g1b.G4_COMPASS_ENTRY_CONTROL
    assert apply == bounded_g1b.G4_COMPASS_ENTRY_SOURCE
    assert len(apply) == 8
    assert not apply & enable
    assert not apply & set(raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS)
    assert len(raisa_policy.G4_STAGE1_SUCCESSOR_PRODUCT_PATHS) == 22
    assert bounded_g1b.operation_effects(bounded_g1b.G4_COMPASS_ENTRY_KIND) == (
        bounded_g1b.EFFECTS | {"product_behavior_change"})


def test_entry_scope_preserves_tick_and_canonical_closures():
    scope = _scope()
    bounded_g1b.validate_g4_compass_entry_scope(scope)
    for key, value in (("canonical_effects_authorized", True),
                       ("runtime_authorized", True),
                       ("closed_entrypoints", ["clockwork_closeout_mutation"]),
                       ("source_paths", []),
                       ("predecessor_scope_sha256", "b" * 64)):
        bad = copy.deepcopy(scope)
        bad[key] = value
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.validate_g4_compass_entry_scope(bad)


def test_entry_rejects_path_expansion_and_wrong_binding():
    for stage in ("enable", "apply"):
        bad = _binding(stage)
        bad["repair_sha256"]["AGENTS.md"] = {}
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.operation_paths(bounded_g1b.G4_COMPASS_ENTRY_KIND, bad)
    bad = _binding("apply")
    bad["schema_version"] = "ariadne.g4_stage1_intention_diary_operation_binding.v1"
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b.operation_paths(bounded_g1b.G4_COMPASS_ENTRY_KIND, bad)


def test_generic_tick_entry_does_not_inherit_g4_effect_authority(tmp_path):
    decision = programme_admission.evaluate_programme_admission(
        repo_root=tmp_path,
        manifest={"schema_version": bounded_g1b.G4_COMPASS_ENTRY_SCHEMA,
                  "operation_kind": bounded_g1b.G4_COMPASS_ENTRY_KIND},
        entrypoint="clockwork_tick_mutation")
    assert decision.admitted is False
    assert decision.reason_codes == [
        "bounded_g1b_explicit_operation_context_required"]


def test_effect_output_set_is_exact_and_acceptance_is_read_only_source():
    outputs = bounded_g1b.G4_COMPASS_EFFECT_OUTPUTS
    assert len(outputs) == 12
    assert bounded_g1b.G4_COMPASS_EFFECT_ACCEPTANCE in (
        bounded_g1b.G4_COMPASS_ENTRY_SOURCE)
    assert bounded_g1b.G4_COMPASS_EFFECT_ACCEPTANCE not in outputs
    assert bounded_g1b.G4_COMPASS_EFFECT_INTENT in (
        bounded_g1b.G4_COMPASS_ENTRY_SOURCE)
    assert bounded_g1b.G4_COMPASS_EFFECT_INTENT not in outputs
    assert "AGENTS.md" in outputs
    assert "orchestration/continuity/ariadne-governance-clockwork/current.json" in outputs


def _synthetic_enable(monkeypatch, tmp_path):
    """Supply only named ordinary bytes to the real bounded loader."""
    b = bounded_g1b
    target, source, evidence = (tmp_path / n for n in ("target", "source", "evidence"))
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    selected = b.G4_COMPASS_ENTRY_CONTROL
    inputs = (b.CONFIGURATION_PATHS | {b.STATE, b.GATES, b.OVERLAY, b.AGENTS,
              b.G4_STAGE1_INTERACTIVE_SCOPE, b.G4_STAGE1_SUCCESSOR_SCOPE,
              b.G4_STAGE1_SUCCESSOR_TEST, b.G4_COMPASS_ENTRY_SCOPE,
              b.G4_COMPASS_ENTRY_TEST} | b.SOURCE_PATHS | b.CONTROLLER_PATHS)
    baseline = {p: ("baseline:" + p).encode() for p in inputs -
                {b.G4_COMPASS_ENTRY_SCOPE, b.G4_COMPASS_ENTRY_TEST}}
    baseline[b.G4_STAGE1_SUCCESSOR_SCOPE] = (
        Path(__file__).resolve().parents[1] /
        b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes()
    payload = dict(baseline)
    payload[b.G4_AUDIT_CODE] = b"prospective-exact-controller"
    payload[b.G4_COMPASS_ENTRY_TEST] = b"prospective-exact-test"
    scope = _scope()
    scope["source_sha256"] = {p: sha(payload[p]) for p in
                              b.SOURCE_PATHS | b.CONTROLLER_PATHS}
    scope["control_sha256"] = {p: sha(payload[p]) for p in
                               selected - {b.G4_COMPASS_ENTRY_SCOPE}}
    payload[b.G4_COMPASS_ENTRY_SCOPE] = b._canonical(scope) + b"\n"
    q = {
        "schema_version": b.G4_COMPASS_ENTRY_SCHEMA,
        "operation_kind": b.G4_COMPASS_ENTRY_KIND,
        "operation_id": "synthetic-enable",
        "stage": "enable", "phase": "development",
        "base_commit": b.G4_COMPASS_ENTRY_BASE["commit"],
        "base_tree": b.G4_COMPASS_ENTRY_BASE["tree"],
        "expected_head": b.G4_COMPASS_ENTRY_BASE["commit"],
        "expected_index_tree": b.G4_COMPASS_ENTRY_BASE["tree"],
        "candidate_tree": "c" * 40,
        "source_sha256": scope["source_sha256"],
        "payload_sha256": {p: sha(raw) for p, raw in payload.items()},
        "repair_sha256": {p: {"before_sha256": sha(baseline[p]) if p in baseline else None,
                              "after_sha256": sha(payload[p])} for p in selected},
        "activation_acceptance": None,
    }
    review_path = (evidence / "g4-compass-reconnection-entry" /
                   "independent-enable-development-subject-review-v1.json")
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
              "verdict": "PASS_G4_COMPASS_ENTRY_EXACT_SOURCE_SUBJECT",
              "subject_sha256": b.g4_compass_entry_review_subject(q),
              "stage": "enable", "phase": "development",
              "reviewer_agent": "/root/frontier18_exact_metadata_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": []}
    review_raw = b._canonical(review) + b"\n"
    q["source_review"] = {"path": review_path.as_posix(),
                          "sha256": sha(review_raw)}
    files = {target / p: raw for p, raw in payload.items()}
    files.update({source / p: payload[p] for p in
                  b.SOURCE_PATHS | b.CONTROLLER_PATHS})
    files[review_path] = review_raw

    def read(path, digest):
        raw = files[path]
        if sha(raw) != digest:
            raise b.BoundedG1BError("synthetic_input_digest_changed")
        return raw

    def git(_target, *args):
        if args == ("rev-parse", b.G4_COMPASS_ENTRY_BASE["commit"] + "^{tree}"):
            return b.G4_COMPASS_ENTRY_BASE["tree"]
        if args == ("cat-file", "commit", "a" * 40):
            return ("tree " + "b" * 40 + "\nparent " +
                    b.G4_COMPASS_ENTRY_BASE["commit"] + "\n\n")
        raise AssertionError(args)

    def git_bytes(_target, *args):
        if args[:2] == ("ls-tree", "-z"):
            return b"row" if args[-1] in baseline else b""
        assert args[:2] == ("cat-file", "blob")
        return baseline[args[2].split(":", 1)[1]]

    monkeypatch.setattr(b.trusted_git, "run_git", git)
    monkeypatch.setattr(b.trusted_git, "run_git_bytes", git_bytes)
    monkeypatch.setattr(b.trusted_git, "attest_target_index",
                        lambda *_a, **_k: {"observation_sha256": "d" * 64})
    return (target, source, evidence, tmp_path / "scratch", q, read,
            files, baseline)


def test_real_loader_accepts_exact_synthetic_enable(monkeypatch, tmp_path):
    b = bounded_g1b
    target, source, evidence, scratch, q, read, _, _ = _synthetic_enable(
        monkeypatch, tmp_path)
    result = b._load_g4_compass_entry_inputs(
        None, target, source, evidence, scratch, q, read, {})
    assert result.binding == q
    assert set(result.evidence) == {"scope", "review"}
    assert result.before[b.AGENTS] == result.payloads[b.AGENTS]


def test_real_loader_rejects_source_or_review_drift(monkeypatch, tmp_path):
    b = bounded_g1b
    target, source, evidence, scratch, q, read, files, _ = _synthetic_enable(
        monkeypatch, tmp_path)
    files[source / b.G4_AUDIT_CODE] = b"unreviewed-controller"
    with pytest.raises(b.BoundedG1BError):
        b._load_g4_compass_entry_inputs(
            None, target, source, evidence, scratch, q, read, {})


def test_real_loader_accepts_exact_synthetic_apply(monkeypatch, tmp_path):
    b = bounded_g1b
    target, source, evidence, scratch, q, read, files, baseline = _synthetic_enable(
        monkeypatch, tmp_path)
    # An already published control commit is the apply preimage. The source
    # stage adds only the eight named writer/intent/acceptance files.
    for p in b.G4_COMPASS_ENTRY_CONTROL:
        baseline[p] = files[target / p]
    q["stage"] = "apply"
    q["base_commit"] = q["expected_head"] = "a" * 40
    q["base_tree"] = q["expected_index_tree"] = "b" * 40
    writer = {p: ("reviewed-writer:" + p).encode() for p in
              b.G4_COMPASS_ENTRY_SOURCE}
    for p, raw in writer.items():
        files[target / p] = files[source / p] = raw
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    q["payload_sha256"] = {p.relative_to(target).as_posix(): sha(raw)
                           for p, raw in files.items() if p.is_relative_to(target)}
    q["repair_sha256"] = {p: {"before_sha256": None,
                              "after_sha256": sha(raw)} for p, raw in writer.items()}
    activation_path = (evidence / "g4-compass-reconnection-entry" /
                       "independent-enable-push-effect-review-v1.json")
    activation = {"status": "PASS",
                  "verdict": "PASS_G4_COMPASS_ENTRY_CONTROL_PUBLICATION_EFFECT",
                  "independent": True, "implementation_authorship": False,
                  "blocking_findings": [],
                  "reviewer_agent": "/root/frontier18_exact_metadata_review",
                  "base": b.G4_COMPASS_ENTRY_BASE["commit"],
                  "commit": q["base_commit"], "candidate_tree": q["base_tree"],
                  "control_activation_accepted": True,
                  "same_attempt_remote_readback_verified": True,
                  "protected_refs_unchanged": True,
                  "whole_inverse_verified_same_attempt": True,
                  "published_ref": b.G4_STAGE1_INTERACTIVE_BACKEND_REF}
    activation_raw = b._canonical(activation) + b"\n"
    files[activation_path] = activation_raw
    q["activation_acceptance"] = {"path": activation_path.as_posix(),
                                  "sha256": sha(activation_raw)}
    review_path = (evidence / "g4-compass-reconnection-entry" /
                   "independent-apply-development-subject-review-v1.json")
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
              "verdict": "PASS_G4_COMPASS_ENTRY_EXACT_SOURCE_SUBJECT",
              "subject_sha256": b.g4_compass_entry_review_subject(q),
              "stage": "apply", "phase": "development",
              "reviewer_agent": "/root/frontier18_exact_metadata_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": []}
    review_raw = b._canonical(review) + b"\n"
    files[review_path] = review_raw
    q["source_review"] = {"path": review_path.as_posix(),
                          "sha256": sha(review_raw)}
    result = b._load_g4_compass_entry_inputs(
        None, target, source, evidence, scratch, q, read, {})
    assert result.binding["stage"] == "apply"
    assert set(q["repair_sha256"]) == b.G4_COMPASS_ENTRY_SOURCE
    one = sorted(b.G4_COMPASS_ENTRY_SOURCE)[0]
    q["repair_sha256"].pop(one)
    with pytest.raises(b.BoundedG1BError, match="actual_changed_subset"):
        b._load_g4_compass_entry_inputs(
            None, target, source, evidence, scratch, q, read, {})
    # A reviewed source that is byte-identical to its committed base is a
    # legitimate no-op: it remains in the eight-source payload and review.
    baseline[one] = files[target / one]
    review["subject_sha256"] = b.g4_compass_entry_review_subject(q)
    review_raw = b._canonical(review) + b"\n"
    files[review_path] = review_raw
    q["source_review"]["sha256"] = sha(review_raw)
    result = b._load_g4_compass_entry_inputs(
        None, target, source, evidence, scratch, q, read, {})
    assert one not in result.binding["repair_sha256"]
    files[source / b.G4_AUDIT_CODE] = files[target / b.G4_AUDIT_CODE]
    q["source_review"]["sha256"] = "0" * 64
    with pytest.raises(b.BoundedG1BError):
        b._load_g4_compass_entry_inputs(
            None, target, source, evidence, scratch, q, read, {})


def _synthetic_effect(monkeypatch, tmp_path):
    b = bounded_g1b
    from orchestration_harness import governance_clockwork_tick as writer_core
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    target = tmp_path / "target"
    source = Path(b.__file__).resolve().parents[1]
    evidence = tmp_path / "evidence"
    scratch = tmp_path / "scratch"
    for p in (target, evidence, scratch):
        p.mkdir()

    def put(root, name, raw):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return {"path": path.as_posix(), "sha256": sha(raw)}

    sources = {}
    for name in b.G4_COMPASS_ENTRY_SOURCE:
        raw = ((source / name).read_bytes() if name ==
               "orchestration_harness/governance_clockwork_tick.py" else
               ("reviewed-source:" + name).encode())
        sources[name] = sha(raw)
        put(target, name, raw)
    controller_raw = Path(b.__file__).read_bytes()
    put(target, b.G4_AUDIT_CODE, controller_raw)
    authority_raw = {
        b.STATE: b._canonical({"active_profile": raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE,
                                "current_gate": "G4", "active_correction": "G4",
                                "programme_mode": "convergence"}) + b"\n",
        b.GATES: b"reviewed-gates",
        b.OVERLAY: b"reviewed-overlay",
        b.G4_STAGE1_SUCCESSOR_SCOPE: (
            Path(__file__).resolve().parents[1] /
            b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes(),
    }
    authority_sha = {p: sha(raw) for p, raw in authority_raw.items()}
    for p, raw in authority_raw.items():
        put(target, p, raw)
    before, after, after_bytes = {}, {}, {}
    for name in b.G4_COMPASS_EFFECT_OUTPUTS:
        raw = ((b._canonical({"lease_sequence": 247}) + b"\n") if
               name.endswith("ariadne-governance-clockwork/current.json") else
               b"g" * 2363250 if name ==
               "orchestration/continuity/emr4-continuity-graph.json" else
               b"e" * 3025971 if name ==
               "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
               else ("current:" + name).encode())
        before[name] = sha(raw)
        next_raw = (raw if name == "AGENTS.md" else
                    b._canonical({"lease_sequence": 248}) + b"\n" if
                    name.endswith("ariadne-governance-clockwork/current.json") else
                    ("next:" + name).encode())
        after_bytes[name] = next_raw
        after[name] = sha(next_raw)
        put(target, name, raw)
    q = {
        "schema_version": b.G4_COMPASS_EFFECT_BINDING_SCHEMA,
        "operation_kind": b.G4_COMPASS_ENTRY_KIND,
        "operation_id": "synthetic-reconcile",
        "stage": "reconcile", "phase": "effect", "mode": "reorient",
        "source_commit": "a" * 40, "source_tree": "b" * 40,
        "source_sha256": sources,
        "controller_sha256": sha(controller_raw),
        "authority_sha256": authority_sha,
        "intent_sha256": sources[b.G4_COMPASS_EFFECT_INTENT],
        "acceptance_source": {"path": (target / b.G4_COMPASS_EFFECT_ACCEPTANCE).as_posix(),
                              "sha256": sources[b.G4_COMPASS_EFFECT_ACCEPTANCE]},
        "previous_effect_binding": None,
        "before_sha256": before, "after_sha256": after,
        "lease_before": 247, "lease_after": 248,
    }
    protected = dict(b.G4_COMPASS_REMOTE_PROTECTED)
    parent = "9" * 40
    pub = {"status": "PASS", "independent": True,
           "verdict": "PASS_G4_COMPASS_ENTRY_SOURCE_PUBLICATION_EFFECT",
           "reviewer_agent": "/root/frontier18_exact_metadata_review",
           "blocking_findings": [], "source_publication_accepted": True,
           "source_paths": sorted(b.G4_COMPASS_ENTRY_SOURCE),
           "source_sha256": sources,
           "implementation_authorship": False,
           "commit": q["source_commit"], "candidate_tree": q["source_tree"],
           "same_attempt_remote_readback_verified": True,
           "protected_refs_unchanged": True,
           "whole_inverse_verified_same_attempt": True,
           "base": parent,
           "remote_before": {**protected,
                             b.G4_STAGE1_INTERACTIVE_BACKEND_REF: parent},
           "remote_after": {**protected,
                            b.G4_STAGE1_INTERACTIVE_BACKEND_REF:
                                q["source_commit"]},
           "published_ref": b.G4_STAGE1_INTERACTIVE_BACKEND_REF}
    q["source_publication"] = put(
        evidence, "g4-compass-reconnection-entry/independent-apply-push-effect-review-v1.json",
        b._canonical(pub) + b"\n")
    grant = {"schema": "emr4.g4_compass_finite_effect_grant.v1",
             "status": "READY", "operation_id": q["operation_id"],
             "mode": "reorient", "lease_before": 247, "lease_after": 248,
             "maximum_effect_attempts": 1, "consumed_effect_attempts": 0,
             "effect_classes": ["existing_clockwork_runtime_mutation"],
             "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
    q["effect_grant"] = put(
        evidence, "g4-compass-reconnection-entry/finite-effect-grant-v1.json",
        b._canonical(grant) + b"\n")
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
              "verdict": "PASS_G4_COMPASS_RECONCILIATION_EFFECT_EXACT_SUBJECT",
              "subject_sha256": b.g4_compass_effect_review_subject(q),
              "reviewer_agent": "/root/frontier18_exact_metadata_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": []}
    q["effect_review"] = put(
        evidence, "g4-compass-reconnection-entry/independent-effect-subject-review-v1.json",
        b._canonical(review) + b"\n")
    binding = put(evidence, "binding.json", b._canonical(q) + b"\n")
    context = b.BoundedG1BContext(target, source, evidence, scratch,
                                  Path(binding["path"]), binding["sha256"])
    manifest = {key: q[key] for key in b.G4_COMPASS_EFFECT_MANIFEST_KEYS
                if key not in {"schema_version", "binding_sha256"}}
    manifest["schema_version"] = b.G4_COMPASS_EFFECT_MANIFEST_SCHEMA
    manifest["binding_sha256"] = binding["sha256"]
    monkeypatch.setattr(b.trusted_git, "_physical_git_administration",
                        lambda _p: {"gitdir": tmp_path / "admin",
                                    "commondir": tmp_path / "admin"})
    monkeypatch.setattr(b.trusted_git, "run_git",
                        lambda _p, *args: q["source_commit"] if args ==
                        ("rev-parse", "HEAD") else q["source_tree"] if args ==
                        ("rev-parse", "HEAD^{tree}") else
                        "tree " + q["source_tree"] + "\nparent " + parent + "\n\n"
                        if args == ("cat-file", "commit", q["source_commit"])
                        else "wrong")
    committed = {p: (target / p).read_bytes() for p in
                 (b.G4_COMPASS_ENTRY_SOURCE | b.G4_COMPASS_EFFECT_OUTPUTS |
                  set(authority_raw) | {b.G4_AUDIT_CODE})}
    monkeypatch.setattr(b.trusted_git, "run_git_bytes",
                        lambda _p, *_args: committed[
                            _args[-1].split(":", 1)[1]])
    monkeypatch.setattr(b.trusted_git, "run_git_optional_bytes",
                        lambda _p, *_args: (1, b""))
    monkeypatch.setattr(writer_core, "validate_prepared_tick",
                        lambda _root, row: row)
    monkeypatch.setattr(writer_core, "_verify_g4_effect_manifest_images",
                        lambda _root, _row, _manifest: None)
    monkeypatch.setattr(writer_core, "_verify_g4_rollback_manifest_images",
                        lambda _root, _row, _manifest: None)
    return context, manifest, q, target, committed, after_bytes


def test_effect_api_accepts_only_exact_reviewed_synthetic_binding(monkeypatch, tmp_path):
    b = bounded_g1b
    context, manifest, _, _, _, _ = _synthetic_effect(monkeypatch, tmp_path)
    decision = b.require_g4_compass_reconciliation_effect(
        context=context, manifest=manifest, prepared={})
    assert decision.policy_admitted is True
    assert decision.execution_authorized is True
    assert decision.entrypoint == "g4_compass_reconciliation_effect"


def _rebind_effect(context, q):
    b = bounded_g1b
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    review_path = Path(q["effect_review"]["path"])
    review = json.loads(review_path.read_bytes())
    review["subject_sha256"] = b.g4_compass_effect_review_subject(q)
    review_raw = b._canonical(review) + b"\n"
    review_path.write_bytes(review_raw)
    q["effect_review"]["sha256"] = sha(review_raw)
    binding_raw = b._canonical(q) + b"\n"
    context.binding_path.write_bytes(binding_raw)
    context = b.BoundedG1BContext(
        context.target_root, context.source_root, context.evidence_root,
        context.scratch_root, context.binding_path, sha(binding_raw))
    manifest = {key: q[key] for key in b.G4_COMPASS_EFFECT_MANIFEST_KEYS
                if key not in {"schema_version", "binding_sha256"}}
    manifest["schema_version"] = b.G4_COMPASS_EFFECT_MANIFEST_SCHEMA
    manifest["binding_sha256"] = context.expected_binding_sha256
    return context, manifest


@pytest.mark.parametrize("field,value", [
    ("verdict", "PASS_UNRELATED"),
    ("reviewer_agent", "/root/implementation-author"),
    ("blocking_findings", ["unresolved"]),
])
def test_effect_rejects_wrong_source_publication(monkeypatch, tmp_path,
                                                  field, value):
    b = bounded_g1b
    context, _, q, _, _, _ = _synthetic_effect(monkeypatch, tmp_path)
    publication_path = Path(q["source_publication"]["path"])
    publication = json.loads(publication_path.read_bytes())
    publication[field] = value
    raw = b._canonical(publication) + b"\n"
    publication_path.write_bytes(raw)
    q["source_publication"]["sha256"] = hashlib.sha256(raw).hexdigest()
    context, manifest = _rebind_effect(context, q)
    with pytest.raises(b.BoundedG1BError,
                       match="source_publication_result"):
        b.require_g4_compass_reconciliation_effect(
            context=context, manifest=manifest, prepared={})


def test_effect_rejects_third_image_drift_and_stale_head(monkeypatch, tmp_path):
    b = bounded_g1b
    context, manifest, _, target, _, _ = _synthetic_effect(monkeypatch, tmp_path)
    graph = target / "orchestration/continuity/emr4-continuity-graph.json"
    graph.write_bytes(b"third-party-drift")
    with pytest.raises(b.BoundedG1BError, match="effect_digest"):
        b.require_g4_compass_reconciliation_effect(
            context=context, manifest=manifest, prepared={})
    graph.write_bytes(b"g" * 2363250)
    monkeypatch.setattr(b.trusted_git, "run_git",
                        lambda *_a: "0" * 40)
    with pytest.raises(b.BoundedG1BError, match="source_identity"):
        b.require_g4_compass_reconciliation_effect(
            context=context, manifest=manifest, prepared={})


def test_effect_rejects_local_protected_alias(monkeypatch, tmp_path):
    b = bounded_g1b
    context, manifest, _, _, _, _ = _synthetic_effect(monkeypatch, tmp_path)
    monkeypatch.setattr(b.trusted_git, "run_git_optional_bytes",
                        lambda *_a: (0, b""))
    with pytest.raises(b.BoundedG1BError,
                       match="local_protected_alias"):
        b.require_g4_compass_reconciliation_effect(
            context=context, manifest=manifest, prepared={})


def test_exact_reviewed_rollback_uses_post_effect_preimage(monkeypatch,
                                                             tmp_path):
    b = bounded_g1b
    context, _, q, target, _, after_bytes = _synthetic_effect(
        monkeypatch, tmp_path)
    prior = copy.deepcopy(q)
    root = context.evidence_root / "g4-compass-reconnection-entry"
    prior_path = root / "effect-binding.json"
    prior_raw = b._canonical(prior) + b"\n"
    prior_path.write_bytes(prior_raw)
    for path, raw in after_bytes.items():
        (target / path).write_bytes(raw)
    q["phase"] = "rollback"
    q["mode"] = "rollback"
    q["before_sha256"] = prior["after_sha256"]
    q["after_sha256"] = dict(prior["before_sha256"])
    pointer = "orchestration/continuity/ariadne-governance-clockwork/current.json"
    recovery_pointer = b._canonical({"phase": "recovery_baseline",
                                     "lease_sequence": 249}) + b"\n"
    q["after_sha256"][pointer] = hashlib.sha256(recovery_pointer).hexdigest()
    q["lease_before"], q["lease_after"] = 248, 249
    q["previous_effect_binding"] = {
        "path": prior_path.as_posix(),
        "sha256": hashlib.sha256(prior_raw).hexdigest()}
    grant = json.loads(Path(q["effect_grant"]["path"]).read_bytes())
    grant.update(mode="rollback", lease_before=248, lease_after=249)
    grant_path = root / "finite-rollback-grant-v1.json"
    grant_raw = b._canonical(grant) + b"\n"
    grant_path.write_bytes(grant_raw)
    q["effect_grant"] = {"path": grant_path.as_posix(),
                         "sha256": hashlib.sha256(grant_raw).hexdigest()}
    review_path = root / "independent-rollback-subject-review-v1.json"
    old_review = json.loads(Path(q["effect_review"]["path"]).read_bytes())
    review_path.write_bytes(b._canonical(old_review) + b"\n")
    q["effect_review"] = {
        "path": review_path.as_posix(),
        "sha256": hashlib.sha256(review_path.read_bytes()).hexdigest()}
    context, manifest = _rebind_effect(context, q)
    decision = b.require_g4_compass_reconciliation_effect(
        context=context, manifest=manifest,
        prepared={"pointer": {"phase": "recovery_baseline",
                              "lease_sequence": 249}},
        phase="rollback")
    assert decision.execution_authorized is True


def test_publish_loader_derives_actual_changed_subset(monkeypatch, tmp_path):
    """The 12 attested images include no-op surfaces; only real deltas publish."""
    b = bounded_g1b
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    target, source, evidence = (tmp_path / name for name in
                                ("target", "source", "evidence"))
    root = evidence / "g4-compass-reconnection-entry"
    inputs = (b.CONFIGURATION_PATHS | {b.STATE, b.GATES, b.OVERLAY, b.AGENTS,
              b.G4_STAGE1_INTERACTIVE_SCOPE, b.G4_STAGE1_SUCCESSOR_SCOPE,
              b.G4_STAGE1_SUCCESSOR_TEST, b.G4_COMPASS_ENTRY_SCOPE,
              b.G4_COMPASS_ENTRY_TEST} | b.SOURCE_PATHS | b.CONTROLLER_PATHS |
              b.G4_COMPASS_ENTRY_SOURCE | b.G4_COMPASS_EFFECT_OUTPUTS)
    baseline = {p: ("base:" + p).encode() for p in inputs}
    baseline[b.G4_STAGE1_SUCCESSOR_SCOPE] = (
        Path(__file__).resolve().parents[1] /
        b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes()
    current = dict(baseline)
    changed = {"orchestration/continuity/emr4-continuity-graph.json",
               "orchestration/continuity/ariadne-governance-clockwork/current.json"}
    for p in changed:
        current[p] = ("after:" + p).encode()
    sources = {p: sha(current[p]) for p in
               b.SOURCE_PATHS | b.CONTROLLER_PATHS}
    scope = _scope()
    scope["source_sha256"] = sources
    scope["control_sha256"] = {p: sha(current[p]) for p in
                               b.G4_COMPASS_ENTRY_CONTROL -
                               {b.G4_COMPASS_ENTRY_SCOPE}}
    current[b.G4_COMPASS_ENTRY_SCOPE] = b._canonical(scope) + b"\n"
    baseline[b.G4_COMPASS_ENTRY_SCOPE] = current[b.G4_COMPASS_ENTRY_SCOPE]
    before = {p: sha(baseline[p]) for p in b.G4_COMPASS_EFFECT_OUTPUTS}
    after = {p: sha(current[p]) for p in b.G4_COMPASS_EFFECT_OUTPUTS}
    q = {
        "schema_version": b.G4_COMPASS_ENTRY_SCHEMA,
        "operation_kind": b.G4_COMPASS_ENTRY_KIND,
        "operation_id": "synthetic-publish", "stage": "publish",
        "phase": "development", "base_commit": "a" * 40,
        "base_tree": "b" * 40, "expected_head": "a" * 40,
        "expected_index_tree": "b" * 40, "candidate_tree": "c" * 40,
        "source_sha256": sources,
        "payload_sha256": {p: sha(raw) for p, raw in current.items()},
        "repair_sha256": {p: {"before_sha256": before[p],
                               "after_sha256": after[p]} for p in changed},
    }
    files = {target / p: raw for p, raw in current.items()}
    files.update({source / p: current[p] for p in sources})

    def evidence_row(name, row):
        path = root / name
        raw = b._canonical(row) + b"\n"
        files[path] = raw
        return {"path": path.as_posix(), "sha256": sha(raw)}

    protected = dict(b.G4_COMPASS_REMOTE_PROTECTED)
    parent = "9" * 40
    q["activation_acceptance"] = evidence_row(
        "independent-apply-push-effect-review-v1.json",
        {"status": "PASS", "verdict":
         "PASS_G4_COMPASS_ENTRY_SOURCE_PUBLICATION_EFFECT",
         "reviewer_agent": "/root/frontier18_exact_metadata_review",
         "independent": True, "implementation_authorship": False,
         "blocking_findings": [], "source_publication_accepted": True,
         "source_paths": sorted(b.G4_COMPASS_ENTRY_SOURCE),
         "source_sha256": {p: sha(current[p]) for p in
                           b.G4_COMPASS_ENTRY_SOURCE},
         "base": parent,
         "commit": q["base_commit"], "candidate_tree": q["base_tree"],
         "same_attempt_remote_readback_verified": True,
         "protected_refs_unchanged": True,
         "whole_inverse_verified_same_attempt": True,
         "remote_before": {**protected,
                           b.G4_STAGE1_INTERACTIVE_BACKEND_REF: parent},
         "remote_after": {**protected,
                          b.G4_STAGE1_INTERACTIVE_BACKEND_REF:
                              q["base_commit"]},
         "published_ref": b.G4_STAGE1_INTERACTIVE_BACKEND_REF})
    effect = {key: None for key in b.G4_COMPASS_EFFECT_BINDING_KEYS}
    effect.update(schema_version=b.G4_COMPASS_EFFECT_BINDING_SCHEMA,
                  operation_kind=b.G4_COMPASS_ENTRY_KIND, stage="reconcile",
                  phase="effect", mode="reorient",
                  source_commit=q["base_commit"],
                  source_tree=q["base_tree"], before_sha256=before,
                  after_sha256=after, lease_after=248)
    q["effect_binding"] = evidence_row("effect-binding.json", effect)
    q["effect_result"] = evidence_row("effect-result.json", {
        "schema_version": "ariadne.governance_live_tick_state.v1",
        "status": "passed", "source_commit": q["base_commit"],
        "lease_sequence": 248, "event_kind": "g4_reorientation",
        "operation_id": "g4-emr4-compass-reconnection",
        "canonical_drift": 0, "dual_owned_surfaces": 0})
    q["effect_result_review"] = evidence_row(
        "independent-effect-readback-review-v1.json",
        {"status": "PASS", "verdict":
         "PASS_G4_COMPASS_REORIENTATION_EFFECT_READBACK",
         "reviewer_agent": "/root/frontier18_exact_metadata_review",
         "independent": True, "implementation_authorship": False,
         "blocking_findings": [],
         "effect_binding_sha256": q["effect_binding"]["sha256"],
         "effect_result_sha256": q["effect_result"]["sha256"],
         "after_sha256": after})
    q["publication_lease"] = evidence_row("publication-lease-v1.json", {
        "schema": "emr4.g4_compass_publication_lease.v1",
        "status": "READY", "base_commit": q["base_commit"],
        "base_tree": q["base_tree"],
        "target_ref": b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
        "recovery_ref_before": q["base_commit"],
        "protected_remote_refs": protected,
        "maximum_publication_attempts": 1,
        "consumed_publication_attempts": 0})
    q["source_review"] = evidence_row(
        "independent-publish-development-subject-review-v1.json",
        {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
         "verdict": "PASS_G4_COMPASS_RECONCILED_OUTPUT_PUBLICATION_SUBJECT",
         "subject_sha256": b.g4_compass_entry_review_subject(q),
         "stage": "publish", "phase": "development",
         "reviewer_agent": "/root/frontier18_exact_metadata_review",
         "independent": True, "implementation_authorship": False,
         "blocking_findings": []})

    def read(path, digest):
        raw = files[path]
        if sha(raw) != digest:
            raise b.BoundedG1BError("synthetic_digest")
        return raw

    def git(_target, *args):
        if args == ("rev-parse", q["base_commit"] + "^{tree}"):
            return q["base_tree"]
        if args == ("cat-file", "commit", q["base_commit"]):
            return "tree " + q["base_tree"] + "\nparent " + parent + "\n\n"
        raise AssertionError(args)

    def git_bytes(_target, *args):
        assert args[:2] == ("cat-file", "blob")
        return baseline[args[2].split(":", 1)[1]]

    monkeypatch.setattr(b.trusted_git, "run_git", git)
    monkeypatch.setattr(b.trusted_git, "run_git_bytes", git_bytes)
    monkeypatch.setattr(b.trusted_git, "run_git_optional_bytes",
                        lambda *_a: (1, b""))
    monkeypatch.setattr(b.trusted_git, "attest_target_index",
                        lambda *_a, **_k: {"observation_sha256": "d" * 64})
    loaded = b._load_g4_compass_publish_inputs(
        None, target, source, evidence, tmp_path / "scratch", q, read, {})
    assert loaded.binding["repair_sha256"].keys() == changed
    assert len(after) == 12
    omitted = sorted(changed)[0]
    q["repair_sha256"].pop(omitted)
    with pytest.raises(b.BoundedG1BError,
                       match="actual_changed_subset"):
        b._load_g4_compass_publish_inputs(
            None, target, source, evidence, tmp_path / "scratch", q, read, {})


def test_effect_api_rejects_drift_and_protected_expansion(monkeypatch, tmp_path):
    b = bounded_g1b
    context, manifest, q, target, _, _ = _synthetic_effect(monkeypatch, tmp_path)
    pointer = target / "orchestration/continuity/ariadne-governance-clockwork/current.json"
    pointer.write_bytes(b._canonical({"lease_sequence": 248}) + b"\n")
    with pytest.raises(b.BoundedG1BError):
        b.require_g4_compass_reconciliation_effect(
            context=context, manifest=manifest, prepared={})
    pointer.write_bytes(b._canonical({"lease_sequence": 247}) + b"\n")
    bad = copy.deepcopy(manifest)
    bad["after_sha256"]["local_data/protected-holdouts/v10"] = "0" * 64
    with pytest.raises(b.BoundedG1BError):
        b.require_g4_compass_reconciliation_effect(context=context, manifest=bad,
                                                    prepared={})
    assert q["stage"] == "reconcile"


