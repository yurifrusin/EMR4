"""Focused goal route tests; authored, not executed by the source author.

Only newly authored dictionary/byte fixtures are used. The enable-loader case
substitutes literal Git blobs and index observations; it does not attest a real
repository, configuration, current lease, source publication or canonical map.
"""
import copy
from pathlib import Path

import pytest

from orchestration_harness import bounded_g1b as admission


def _digest(raw):
    return admission._sha(raw)


def _scope(source_sha=None, controls=None):
    sources = source_sha or {p: "a" * 64 for p in admission.SOURCE_PATHS | admission.CONTROLLER_PATHS}
    controls = controls or {
        admission.G4_AUDIT_CODE: sources[admission.G4_AUDIT_CODE],
        admission.G4_GOAL_ENTRY_TEST: "b" * 64,
    }
    return {
        "schema_version": admission.G4_GOAL_ENTRY_SCHEMA,
        "recorded_at": "2026-10-26T00:00:00+00:00",
        "selected_base": dict(admission.G4_GOAL_ENTRY_BASE),
        "active_profile": admission.raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE,
        "predecessor_scope_sha256": admission.G4_GOAL_ENTRY_PREDECESSOR_SHA,
        "control_paths": sorted(admission.G4_GOAL_ENTRY_CONTROL),
        "source_paths": sorted(admission.G4_GOAL_ENTRY_SOURCE),
        "allowed_effects": sorted(admission.EFFECTS),
        "closed_entrypoints": ["clockwork_closeout_mutation", "clockwork_tick_mutation"],
        "canonical_effects_authorized": False, "runtime_authorized": False,
        "source_sha256": sources, "control_sha256": controls,
        "goal_source_sha256": {p: "c" * 64 for p in admission.G4_GOAL_ENTRY_SOURCE},
        "goal_source_preimages": copy.deepcopy(admission.G4_GOAL_SOURCE_PREIMAGES),
    }


def _binding(stage="apply"):
    selected = admission.G4_GOAL_ENTRY_CONTROL if stage == "enable" else admission.G4_GOAL_ENTRY_SOURCE
    return {"schema_version": admission.G4_GOAL_ENTRY_SCHEMA,
        "operation_kind": admission.G4_GOAL_ENTRY_KIND, "stage": stage,
        "repair_sha256": {p: {} for p in selected}}


def _effect():
    before = {p: "a" * 64 for p in admission.G4_GOAL_EFFECT_OUTPUTS}
    after = dict(before)
    after["orchestration/continuity/emr4-compass.json"] = "b" * 64
    after["orchestration/continuity/ariadne-governance-clockwork/current.json"] = "c" * 64
    q = {key: None for key in admission.G4_GOAL_EFFECT_BINDING_KEYS}
    q.update(schema_version=admission.G4_GOAL_EFFECT_BINDING_SCHEMA,
        operation_kind=admission.G4_GOAL_ENTRY_KIND, operation_id="compass-gpms-goal-update-v1",
        stage="goal_update", phase="effect", mode="publish", source_commit="d" * 40,
        source_tree="e" * 40, controller_sha256="f" * 64, intent_sha256="9" * 64,
        source_sha256={p: "9" * 64 for p in admission.G4_GOAL_ENTRY_SOURCE},
        authority_sha256={admission.G4_GOAL_ENTRY_SCOPE: "8" * 64},
        before_sha256=before, after_sha256=after, lease_before=7, lease_after=8)
    manifest = {k: copy.deepcopy(q[k]) for k in admission.G4_GOAL_EFFECT_MANIFEST_KEYS
                if k != "schema_version"}
    manifest["schema_version"] = admission.G4_GOAL_EFFECT_MANIFEST_SCHEMA
    return q, manifest


def _grant(q):
    return {
        "schema": "emr4.g4_goal_finite_effect_grant.v1", "issuer": "/root", "status": "READY",
        "operation_id": q["operation_id"], "mode": q["mode"],
        "source_commit": q["source_commit"], "source_tree": q["source_tree"],
        "intent_sha256": q["intent_sha256"], "scope_sha256": q["authority_sha256"][admission.G4_GOAL_ENTRY_SCOPE],
        "before_sha256": copy.deepcopy(q["before_sha256"]), "after_sha256": copy.deepcopy(q["after_sha256"]),
        "lease_before": q["lease_before"], "lease_after": q["lease_after"],
        "maximum_effect_attempts": 1, "consumed_effect_attempts": 0, "automatic_retry": False,
        "effect_classes": ["existing_clockwork_runtime_mutation"], "expires_at": "2099-01-01T00:00:00+00:00"}


def test_goal_route_is_distinct_source_only_and_keeps_legacy_registration():
    q = _binding("enable")
    assert admission.operation_paths(admission.G4_GOAL_ENTRY_KIND, q) == admission.G4_GOAL_ENTRY_CONTROL
    assert admission._operation(admission.G4_GOAL_ENTRY_KIND, q)["g4_goal_entry_source"] is True
    assert admission.operation_effects(admission.G4_GOAL_ENTRY_KIND) == admission.EFFECTS
    assert admission.G4_COMPASS_ENTRY_BASE["commit"] == "6bdf6a2fcd69dc937f1844c59a4296d0c1b8bde9"
    assert admission.G4_GOAL_ENTRY_BASE["commit"] == "b1dca5ad1f1c0cd13dc6b739d1d5c2755c0c5abd"
    assert admission.G4_COMPASS_ENTRY_KIND in admission.OPERATION_PATHS
    assert admission.G4_GOAL_ENTRY_KIND != admission.G4_COMPASS_ENTRY_KIND


@pytest.mark.parametrize("change", [
    lambda s: s.update(runtime_authorized=True),
    lambda s: s.update(canonical_effects_authorized=True),
    lambda s: s.update(predecessor_scope_sha256="0" * 64),
    lambda s: s["source_paths"].append("app/main.py"),
    lambda s: s["control_sha256"].update({admission.G4_AUDIT_CODE: "0" * 64}),
    lambda s: s["selected_base"].update(commit="0" * 40),
])
def test_scope_cannot_reopen_runtime_expand_paths_or_substitute_authority(change):
    valid = _scope()
    admission.validate_g4_goal_entry_scope(valid)
    changed = copy.deepcopy(valid)
    change(changed)
    with pytest.raises(admission.BoundedG1BError):
        admission.validate_g4_goal_entry_scope(changed)


def test_paths_reject_enable_omission_and_canonical_input_as_source_change():
    q = _binding("enable")
    q["repair_sha256"].pop(admission.G4_GOAL_ENTRY_SCOPE)
    with pytest.raises(admission.BoundedG1BError, match="changed_paths"):
        admission.operation_paths(admission.G4_GOAL_ENTRY_KIND, q)
    q = _binding()
    q["repair_sha256"]["AGENTS.md"] = {}
    with pytest.raises(admission.BoundedG1BError, match="changed_paths"):
        admission.operation_paths(admission.G4_GOAL_ENTRY_KIND, q)


def test_manifest_matches_finished_writer_abi_without_invented_binding_fields():
    q, manifest = _effect()
    assert len(manifest) == 11
    assert admission._g4_goal_effect_contract(q, manifest) == (q["before_sha256"], q["after_sha256"])
    manifest["binding_sha256"] = "0" * 64
    with pytest.raises(admission.BoundedG1BError, match="manifest_schema"):
        admission._g4_goal_effect_contract(q, manifest)


@pytest.mark.parametrize("path", sorted(admission.G4_GOAL_PRESERVED_OUTPUTS))
def test_goal_effect_rejects_each_preserved_surface_drift(path):
    q, manifest = _effect()
    q["after_sha256"][path] = "0" * 64
    manifest["after_sha256"][path] = "0" * 64
    with pytest.raises(admission.BoundedG1BError, match="changed_set"):
        admission._g4_goal_effect_contract(q, manifest)


@pytest.mark.parametrize("field,value,reason", [
    ("phase", "rollback", "binding_version"), ("mode", "reorient", "binding_version"),
    ("stage", "reconcile", "binding_version"), ("lease_before", True, "effect_lease"),
    ("lease_after", 9, "effect_lease"), ("intent_sha256", "0" * 64, "intent_pin"),
])
def test_effect_refuses_old_lane_inverse_stale_lease_and_wrong_raw_intent(field, value, reason):
    q, manifest = _effect()
    q[field] = value
    if field in manifest:
        manifest[field] = value
    with pytest.raises(admission.BoundedG1BError, match=reason):
        admission._g4_goal_effect_contract(q, manifest)


@pytest.mark.parametrize("field,value", [
    ("issuer", "/root/worker"), ("consumed_effect_attempts", 1), ("automatic_retry", True),
    ("source_commit", "0" * 40), ("intent_sha256", "0" * 64),
    ("scope_sha256", "0" * 64), ("expires_at", "2000-01-01T00:00:00+00:00"),
])
def test_root_effect_grant_is_finite_fresh_and_exact_to_source_scope_intent(field, value):
    q, _ = _effect()
    grant = _grant(q)
    admission._g4_goal_validate_effect_grant(grant, q)
    grant[field] = value
    with pytest.raises(admission.BoundedG1BError, match="finite_grant"):
        admission._g4_goal_validate_effect_grant(grant, q)


def test_effect_review_subject_excludes_own_review_but_binds_grant_and_all_images():
    q, _ = _effect()
    before = admission.g4_goal_effect_review_subject(q)
    q["effect_review"] = {"path": "/new-review", "sha256": "1" * 64}
    assert admission.g4_goal_effect_review_subject(q) == before
    q["effect_grant"] = {"path": "/new-grant", "sha256": "2" * 64}
    assert admission.g4_goal_effect_review_subject(q) != before


def test_implementation_authors_cannot_accept_their_own_goal_subject():
    assert admission._g4_goal_reviewer({"reviewer_agent": "/root/independent_reviewer"}) is True
    for author in admission.G4_GOAL_IMPLEMENTATION_AUTHORS | {None, ""}:
        assert admission._g4_goal_reviewer({"reviewer_agent": author}) is False


def test_effect_hook_refuses_missing_context_and_inverse_before_any_io():
    with pytest.raises(admission.BoundedG1BError, match="effect_context"):
        admission.require_g4_compass_goal_update_effect(context=None, manifest={}, prepared={})
    with pytest.raises(admission.BoundedG1BError, match="effect_context"):
        admission.require_g4_compass_goal_update_effect(context=None, manifest={}, prepared={}, phase="rollback")


def test_exact_enable_loader_uses_candidate_controller_and_preserves_synthetic_v10(monkeypatch):
    target, source, evidence, scratch = map(Path, ("/target", "/source", "/evidence", "/scratch"))
    legacy_v10 = b'{"synthetic":"unchanged-v10"}'
    monkeypatch.setattr(admission, "G4_GOAL_ENTRY_PREDECESSOR_SHA", _digest(legacy_v10))
    input_paths = (admission.CONFIGURATION_PATHS | admission.SOURCE_PATHS | admission.CONTROLLER_PATHS
        | {admission.STATE, admission.GATES, admission.OVERLAY, admission.AGENTS,
           admission.G4_STAGE1_INTERACTIVE_SCOPE, admission.G4_STAGE1_SUCCESSOR_SCOPE,
           admission.G4_STAGE1_SUCCESSOR_TEST, admission.G4_GOAL_ENTRY_SCOPE, admission.G4_GOAL_ENTRY_TEST})
    blobs = {p: ("installed:" + p).encode() for p in input_paths}
    blobs[admission.G4_STAGE1_SUCCESSOR_SCOPE] = legacy_v10
    git_blobs = dict(blobs)
    git_blobs.update({p: ("existing ordinary:" + p).encode() for p in admission.G4_GOAL_ENTRY_SOURCE})
    blob_ids = {_digest(raw)[:40]: raw for raw in git_blobs.values()}
    monkeypatch.setattr(admission, "G4_GOAL_SOURCE_PREIMAGES",
        {p: _digest(git_blobs[p]) for p in admission.G4_GOAL_ENTRY_SOURCE})
    candidate = dict(blobs)
    candidate[admission.G4_AUDIT_CODE] = b"reviewed synthetic candidate controller"
    candidate[admission.G4_GOAL_ENTRY_TEST] = b"new focused test"
    sources = {p: _digest(candidate[p]) for p in admission.SOURCE_PATHS | admission.CONTROLLER_PATHS}
    scope = _scope(sources, {p: _digest(candidate[p])
        for p in admission.G4_GOAL_ENTRY_CONTROL - {admission.G4_GOAL_ENTRY_SCOPE}})
    candidate[admission.G4_GOAL_ENTRY_SCOPE] = admission._canonical(scope) + b"\n"
    absent = {admission.G4_GOAL_ENTRY_SCOPE, admission.G4_GOAL_ENTRY_TEST}
    q = _binding("enable")
    q.update(operation_id="compass-gpms-goal-update-v1", phase="development",
        base_commit=admission.G4_GOAL_ENTRY_BASE["commit"], base_tree=admission.G4_GOAL_ENTRY_BASE["tree"],
        expected_head=admission.G4_GOAL_ENTRY_BASE["commit"],
        expected_index_tree=admission.G4_GOAL_ENTRY_BASE["tree"], candidate_tree="c" * 40,
        source_sha256=sources,
        source_preimages={p: {"classification": "existing_ordinary", "sha256": _digest(git_blobs[p])}
                          for p in admission.G4_GOAL_ENTRY_SOURCE}, payload_sha256={p: _digest(candidate[p]) for p in input_paths},
        repair_sha256={p: {"before_sha256": None if p in absent else _digest(blobs[p]),
                          "after_sha256": _digest(candidate[p])} for p in admission.G4_GOAL_ENTRY_CONTROL},
        activation_acceptance=None)
    review_path = evidence / "compass-gpms-goal-entry/independent-enable-development-subject-review-v1.json"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS",
        "verdict": "PASS_G4_GOAL_ENTRY_EXACT_SOURCE_SUBJECT", "stage": "enable", "phase": "development",
        "reviewer_agent": "/root/independent_reviewer", "independent": True,
        "implementation_authorship": False, "blocking_findings": [],
        "subject_sha256": admission.g4_goal_entry_review_subject(q)}
    review_raw = admission._canonical(review)
    q["source_review"] = {"path": str(review_path), "sha256": _digest(review_raw)}
    values = {target / p: raw for p, raw in candidate.items()}
    values.update({source / p: candidate[p] for p in sources})
    values[review_path] = review_raw

    def read(path, digest):
        raw = values[path]
        assert _digest(raw) == digest
        return raw

    def git_bytes(_, *args):
        if args[0] == "ls-tree":
            path = args[-1]
            return b"" if path in absent else (
                b"100644 blob " + _digest(git_blobs[path])[:40].encode() + b"\t" + path.encode() + b"\0")
        assert args[:2] == ("cat-file", "blob")
        if ":" not in args[2]:
            return blob_ids[args[2]]
        path = args[2].split(":", 1)[1]
        return blobs[path]

    monkeypatch.setattr(admission.trusted_git, "run_git_bytes", git_bytes)
    monkeypatch.setattr(admission.trusted_git, "run_git", lambda *_: admission.G4_GOAL_ENTRY_BASE["tree"])
    monkeypatch.setattr(admission.trusted_git, "attest_target_index",
        lambda *_args, **_kwargs: {"observation_sha256": "7" * 64})
    loaded = admission._load_g4_goal_entry_inputs(
        None, target, source, evidence, scratch, q, read, {})
    assert loaded.payloads[admission.G4_STAGE1_SUCCESSOR_SCOPE] == legacy_v10
    assert loaded.before[admission.STATE] == blobs[admission.STATE]
    assert loaded.evidence["review"]["independent"] is True
    q["repair_sha256"][admission.G4_AUDIT_CODE]["before_sha256"] = "0" * 64
    with pytest.raises(admission.BoundedG1BError, match="change_preimage"):
        admission._load_g4_goal_entry_inputs(None, target, source, evidence, scratch, q, read, {})


@pytest.mark.parametrize("tree_row", [
    b"120000 blob " + b"a" * 40 + b"\torchestration_harness/governance_goal_tick.py\0",
    b"040000 tree " + b"a" * 40 + b"\torchestration_harness/governance_goal_tick.py\0",
    b"100644 blob " + b"a" * 40 + b"\twrong-path.py\0",
])
def test_selected_preimage_rejects_symlink_tree_and_wrong_path_before_blob_read(monkeypatch, tree_row):
    calls = []
    def git_bytes(*args):
        calls.append(args)
        assert args[1] == "ls-tree"
        return tree_row
    monkeypatch.setattr(admission.trusted_git, "run_git_bytes", git_bytes)
    with pytest.raises(admission.BoundedG1BError, match="preimage"):
        admission._g4_goal_committed_preimage(Path("/target"), "a" * 40,
                                             "orchestration_harness/governance_goal_tick.py")
    assert len(calls) == 1


def test_missing_preimage_classification_is_not_assumed_absence(monkeypatch):
    q = _binding()
    q.update(base_commit="a" * 40, source_preimages={
        p: {"classification": "unresolved", "sha256": None} for p in admission.G4_GOAL_ENTRY_SOURCE})
    monkeypatch.setattr(admission.trusted_git, "run_git_bytes", lambda *_: b"")
    with pytest.raises(admission.BoundedG1BError, match="source_preimage"):
        admission._g4_goal_source_preimages(Path("/target"), q)
