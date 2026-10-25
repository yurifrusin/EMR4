"""Synthetic boundary checks for the exact G4 Clockwork reorientation."""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestration_harness import governance_clockwork_tick as tick
from scripts import ariadne_continuity as continuity


def _put(root: Path, relative: str, raw: bytes) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def _effect_manifest(root: Path, prepared: dict) -> dict:
    intent_relative = "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json"
    _put(root, intent_relative, b"synthetic-frozen-intent")
    metadata = {
        **prepared["metadata"],
        tick.GENERATION_NAME: tick._json_text(prepared["generation_manifest"]).encode(),
    }
    before, after = tick._g4_effect_images(
        root, prepared["contract"], prepared["canonical"], metadata,
        prepared["pointer"],
    )
    assert len(before) == len(after) == 12
    return {
        "before_sha256": before, "after_sha256": after,
        "lease_before": 247, "lease_after": 248,
        "mode": "reorient", "stage": "reconcile",
        "operation_id": tick.G4_ORIENTATION_OPERATION,
        "source_commit": prepared["source_commit"], "source_tree": "b" * 40,
        "intent_sha256": tick._hash_bytes((root / intent_relative).read_bytes()),
    }


def _synthetic_predecessor(tmp_path: Path, monkeypatch):
    contract = {
        "canonical_paths": {key: f"canon/{key}" for key in tick.CANONICAL_KEYS},
        "clockwork_root": "clock",
    }
    canonical = {key: key.encode() for key in tick.CANONICAL_KEYS}
    canonical["active_latch"] = json.dumps({
        "operation_id": "g1b2-pure-journal-replay-kernel", "status": "in_progress"
    }).encode()
    for key, raw in canonical.items():
        _put(tmp_path, contract["canonical_paths"][key], raw)
    metadata = {name: name.encode() for name in tick.METADATA_NAMES}
    generation = json.dumps({
        "generation_id": tick.G4_OLD_GENERATION_ID,
        "canonical_sha256s": tick.G4_OLD_CANONICAL_SHA256S,
        "metadata_sha256s": tick.G4_OLD_METADATA_SHA256S,
    }).encode()
    metadata[tick.GENERATION_NAME] = generation
    for name, raw in metadata.items():
        _put(tmp_path, f"clock/{name}", raw)
    pointer = {
        "schema_version": "ariadne.governance_live_pointer.v1",
        "phase": "clockwork_active", "writer": tick.WRITER,
        "selected_generation_id": tick.G4_OLD_GENERATION_ID,
        "selected_bundle_sha256": tick.G4_OLD_GENERATION_ID[4:],
        "previous_generation_id": "gen-previous",
        "previous_source_commit": "1d5ebbdff4f2c7d87e6b02b7b64eada675d3f815",
        "lease_sequence": 247,
    }
    pointer_raw = json.dumps(pointer).encode()
    _put(tmp_path, "clock/current.json", pointer_raw)
    _put(tmp_path, "orchestration/programme/current-state.json", b"state")
    _put(tmp_path, "orchestration/programme/gates.yaml", b"gates")
    digest = {raw: tick.G4_ACTUAL_CANONICAL_SHA256S[key]
              for key, raw in canonical.items()}
    digest.update({raw: tick.G4_OLD_METADATA_SHA256S[name]
                   for name, raw in metadata.items() if name in tick.METADATA_NAMES})
    digest[generation] = tick.G4_OLD_GENERATION_SHA256
    digest[pointer_raw] = tick.G4_OLD_POINTER_SHA256
    digest[b"state"] = tick.G4_STATE_SHA256
    digest[b"gates"] = tick.G4_GATES_SHA256
    monkeypatch.setattr(tick, "_hash_bytes",
                        lambda raw: digest.get(raw, hashlib.sha256(raw).hexdigest()))
    monkeypatch.setattr(tick, "_assert_git_state", lambda *_: "accepted-executing-head")
    monkeypatch.setattr(tick, "_assert_g4_git_state", lambda *_: "accepted-executing-head")
    monkeypatch.setattr(tick, "_git", lambda *_: tick.G4_ORIENTATION_TREE)
    monkeypatch.setattr(tick, "_source_bytes", lambda *_: canonical)
    monkeypatch.setattr(tick, "_source_pointer", lambda *_: pointer)
    monkeypatch.setattr(tick, "_git_bytes", lambda *_: pointer_raw)
    monkeypatch.setattr(tick, "validate_active_operation", lambda value: value)
    return contract, canonical, metadata, pointer


def test_only_the_declared_two_drift_predecessor_is_admitted(tmp_path, monkeypatch):
    contract, canonical, metadata, pointer = _synthetic_predecessor(tmp_path, monkeypatch)
    intent = tick.validate_g4_orientation_intent({
        "schema_version": tick.G4_ORIENTATION_INTENT_VERSION,
        "operation_id": tick.G4_ORIENTATION_OPERATION,
        "observed_baseline_commit": tick.G4_ORIENTATION_HEAD,
        "observed_baseline_tree": tick.G4_ORIENTATION_TREE,
        "programme_state_sha256": tick.G4_STATE_SHA256,
        "programme_gates_sha256": tick.G4_GATES_SHA256,
        "previous_generation_id": tick.G4_OLD_GENERATION_ID,
        "previous_bundle_sha256": tick.G4_OLD_GENERATION_ID[4:],
        "lease_sequence": 247,
        "old_canonical_sha256s": tick.G4_OLD_CANONICAL_SHA256S,
        "actual_canonical_sha256s": tick.G4_ACTUAL_CANONICAL_SHA256S,
        "metadata_sha256s": tick.G4_OLD_METADATA_SHA256S,
        "generation_manifest_sha256": tick.G4_OLD_GENERATION_SHA256,
        "pointer_sha256": tick.G4_OLD_POINTER_SHA256,
        "orientation_date": "2026-10-25",
        "acceptance_path": tick.G4_ORIENTATION_ACCEPTANCE,
    })
    assert tick._g4_orientation_baseline(tmp_path, contract, intent) == (
        canonical, metadata, pointer
    )
    _put(tmp_path, contract["canonical_paths"]["continuity"], b"third drift")
    with pytest.raises(tick.ClockworkTickRejection, match="physical_canonical"):
        tick._g4_orientation_baseline(tmp_path, contract, intent)


def test_ordinary_tick_still_rejects_the_two_drift_predecessor(tmp_path, monkeypatch):
    contract, _, _, _ = _synthetic_predecessor(tmp_path, monkeypatch)
    monkeypatch.setattr(tick, "_canonical_paths_match_source", lambda *_: False)
    with pytest.raises(tick.ClockworkTickRejection, match="tick_canonical_not_at_source"):
        tick._assert_clean_predecessor(tmp_path, contract, tick.G4_ORIENTATION_HEAD)


def test_g4_git_topology_requires_all_four_local_aliases_absent(tmp_path, monkeypatch):
    calls = []
    def git(_root, *args):
        if args == ("rev-parse", "HEAD"):
            return "a" * 40
        if args == ("rev-parse", "HEAD^{tree}"):
            return "b" * 40
        assert args[:2] == ("merge-base", "--is-ancestor")
        return ""
    def absent(command, **_kwargs):
        calls.append(command[-1])
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(tick, "_git", git)
    monkeypatch.setattr(tick.subprocess, "run", absent)
    contract = {"required_ancestor": "c" * 40,
                "accepted_rehearsal_source": "d" * 40}
    assert tick._assert_g4_git_state(tmp_path, contract, "a" * 40) == "a" * 40
    assert tuple(calls) == tick.G4_ABSENT_LOCAL_REFS
    def present(command, **_kwargs):
        return SimpleNamespace(returncode=0 if command[-1] == calls[1] else 1)
    monkeypatch.setattr(tick.subprocess, "run", present)
    with pytest.raises(tick.ClockworkTickRejection, match="local_protected_ref_topology"):
        tick._assert_g4_git_state(tmp_path, contract, "a" * 40)
    with pytest.raises(tick.ClockworkTickRejection, match="source_head_tree"):
        tick._assert_g4_git_state(tmp_path, contract, "e" * 40)


def test_g4_selected_live_state_checks_physical_images_and_ownership(tmp_path, monkeypatch):
    contract = {"canonical_paths": {key: f"canon/{key}" for key in tick.CANONICAL_KEYS},
                "clockwork_root": "clock"}
    canonical = {key: key.encode() for key in tick.CANONICAL_KEYS}
    for key, raw in canonical.items():
        _put(tmp_path, contract["canonical_paths"][key], raw)
    ownership = {"schema_version": tick.OWNERSHIP_VERSION,
                 "phase": "clockwork_active",
                 "surface_owners": {key: tick.WRITER for key in (
                     *tick.CANONICAL_KEYS, "command_manifest", "transaction", "ownership")},
                 "legacy_writers": {key: "retired" for key in (
                     "bespoke_continuity_updater", "manual_baton_editor",
                     "manual_latch_editor", "manual_register_fixture_editor")}}
    metadata = {"command-manifest.json": b"command",
                "transaction.json": b"transaction",
                "ownership.json": json.dumps(ownership).encode()}
    for name, raw in metadata.items():
        _put(tmp_path, f"clock/{name}", raw)
    canonical_hashes = {key: tick._hash_bytes(raw) for key, raw in canonical.items()}
    metadata_hashes = {name: tick._hash_bytes(raw) for name, raw in metadata.items()}
    monkeypatch.setattr(tick, "G4_OLD_METADATA_SHA256S", {
        **tick.G4_OLD_METADATA_SHA256S,
        "ownership.json": metadata_hashes["ownership.json"],
    })
    generation = {
        "schema_version": tick.GENERATION_VERSION,
        "canonical_sha256s": canonical_hashes,
        "metadata_sha256s": metadata_hashes,
        "bundle_sha256": tick._hash_json({"canonical": canonical_hashes,
                                         "metadata": metadata_hashes}),
        "source_commit": "a" * 40,
        "previous_generation": {},
        "g4_orientation": {"synthetic": True},
    }
    generation["generation_id"] = "gen-" + generation["bundle_sha256"]
    _put(tmp_path, "clock/generation-manifest.json", json.dumps(generation).encode())
    pointer = {"schema_version": tick.POINTER_VERSION,
               "phase": "clockwork_active", "writer": tick.WRITER,
               "selected_generation_id": generation["generation_id"],
               "selected_bundle_sha256": generation["bundle_sha256"],
               "previous_generation_id": tick.G4_OLD_GENERATION_ID,
               "previous_source_commit": tick.G4_ORIENTATION_HEAD,
               "lease_sequence": 248}
    _put(tmp_path, "clock/current.json", json.dumps(pointer).encode())
    monkeypatch.setattr(tick, "_assert_g4_git_state", lambda *_: "a" * 40)
    monkeypatch.setattr(tick, "_git", lambda *_: "")
    assert tick._validate_g4_selected_live_state(tmp_path, contract, generation)["clockwork_owned_surfaces"] == 10
    _put(tmp_path, "clock/current.json", json.dumps({
        **pointer, "selected_generation_id": "gen-unbound"}).encode())
    with pytest.raises(tick.ClockworkTickRejection, match="live_pointer"):
        tick._validate_g4_selected_live_state(
            tmp_path, contract, {**generation, "generation_id": "gen-unbound"})
    _put(tmp_path, "clock/current.json", json.dumps(pointer).encode())
    monkeypatch.setattr(tick, "_assert_g4_git_state", lambda *_: "c" * 40)
    advanced = tick._validate_g4_selected_live_state(tmp_path, contract, generation)
    assert advanced["head"] == "c" * 40
    assert advanced["source_commit"] == "a" * 40
    def reject_ancestry(*_args):
        raise tick.AdoptionRejection("git_read")
    monkeypatch.setattr(tick, "_git", reject_ancestry)
    with pytest.raises(tick.ClockworkTickRejection, match="live_source_not_ancestor"):
        tick._validate_g4_selected_live_state(tmp_path, contract, generation)
    monkeypatch.setattr(tick, "_git", lambda *_: "")
    _put(tmp_path, "canon/compass", b"unreviewed-change")
    with pytest.raises(tick.ClockworkTickRejection, match="live_physical_images"):
        tick._validate_g4_selected_live_state(tmp_path, contract, generation)


def test_postpublication_live_readback_keeps_generation_source(tmp_path, monkeypatch):
    source_head, published_head = "a" * 40, "b" * 40
    contract = {"canonical_paths": {key: f"canon/{key}" for key in tick.CANONICAL_KEYS},
                "clockwork_root": "clock"}
    canonical = {key: key.encode() for key in tick.CANONICAL_KEYS}
    canonical.update({
        "continuity": b'{"graph_revision": 463}',
        "compass": b'{"map_revision": 445}',
        "active_latch": b'{"protected_boundaries": []}',
    })
    for key, raw in canonical.items():
        _put(tmp_path, contract["canonical_paths"][key], raw)
    source_hashes = {key: tick._hash_bytes(raw) for key, raw in canonical.items()}
    monkeypatch.setattr(tick, "G4_ACTUAL_CANONICAL_SHA256S", source_hashes)
    ownership = {"schema_version": tick.OWNERSHIP_VERSION,
                 "phase": "clockwork_active",
                 "surface_owners": {key: tick.WRITER for key in (
                     *tick.CANONICAL_KEYS, "command_manifest", "transaction", "ownership")},
                 "legacy_writers": {key: "retired" for key in (
                     "bespoke_continuity_updater", "manual_baton_editor",
                     "manual_latch_editor", "manual_register_fixture_editor")}}
    intent = {"schema_version": tick.G4_ORIENTATION_INTENT_VERSION,
              "operation_id": tick.G4_ORIENTATION_OPERATION}
    _put(tmp_path, "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json",
         json.dumps(intent).encode())
    intent_sha = tick.tc.sha256(intent)
    prior_metadata = {
        **tick.G4_OLD_METADATA_SHA256S,
        "ownership.json": tick._hash_bytes(tick._json_text(ownership).encode()),
        tick.GENERATION_NAME: tick.G4_OLD_GENERATION_SHA256,
    }
    command = {
        "schema_version": "ariadne.g4_emr4_compass_command_manifest.v1",
        "profile": "g4_recovery_governance_orientation_only",
        "operation_id": tick.G4_ORIENTATION_OPERATION,
        "source_commit": source_head,
        "intent_sha256": intent_sha,
        "effect_boundary": "separately_reviewed_g4_reconcile_binding_required",
    }
    transaction = {key: None for key in tick.TRANSACTION_KEYS}
    transaction.update({
        "event_kind": tick.G4_ORIENTATION_EVENT,
        "operation_id": tick.G4_ORIENTATION_OPERATION,
        "source_commit": source_head,
        "previous_source_commit": tick.G4_ORIENTATION_HEAD,
        "previous_canonical_sha256s": source_hashes,
        "previous_metadata_sha256s": prior_metadata,
        "projection_sha256s": {
            "graph": tick.tc.sha256(json.loads(canonical["continuity"])),
            "compass": tick.tc.sha256(json.loads(canonical["compass"])),
            "latch": tick.tc.sha256(json.loads(canonical["active_latch"])),
        },
        "journal": [{"payload": {"intent_sha256": intent_sha}}],
    })
    metadata = {
        "command-manifest.json": tick._json_text(command).encode(),
        "transaction.json": tick._json_text(transaction).encode(),
        "ownership.json": tick._json_text(ownership).encode(),
    }
    for name, raw in metadata.items():
        _put(tmp_path, f"clock/{name}", raw)
    metadata_hashes = {name: tick._hash_bytes(raw) for name, raw in metadata.items()}
    monkeypatch.setattr(tick, "G4_OLD_METADATA_SHA256S", {
        **tick.G4_OLD_METADATA_SHA256S,
        "ownership.json": metadata_hashes["ownership.json"],
    })
    monkeypatch.setattr(tick, "G4_OLD_POINTER_SHA256",
                        tick._hash_bytes(b"observed-prior-pointer"))
    bundle = tick._hash_json({"canonical": source_hashes,
                             "metadata": metadata_hashes})
    generation = {
        "schema_version": tick.GENERATION_VERSION,
        "generation_id": "gen-" + bundle,
        "bundle_sha256": bundle,
        "source_commit": source_head,
        "previous_generation": {
            "generation_id": tick.G4_OLD_GENERATION_ID,
            "source_commit": tick.G4_ORIENTATION_HEAD,
            "bundle_sha256": tick.G4_OLD_GENERATION_ID[4:],
            "canonical_sha256s": source_hashes,
            "metadata_sha256s": prior_metadata,
            "pointer_sha256": tick.G4_OLD_POINTER_SHA256,
        },
        "canonical_sha256s": source_hashes,
        "metadata_sha256s": metadata_hashes,
        "g4_orientation": {"intent_sha256": intent_sha,
            "observed_baseline_sha256s": source_hashes,
            "recorded_generation_sha256s": tick.G4_OLD_CANONICAL_SHA256S},
    }
    _put(tmp_path, "clock/generation-manifest.json", tick._json_text(generation).encode())
    pointer = {"schema_version": tick.POINTER_VERSION,
               "phase": "clockwork_active", "writer": tick.WRITER,
               "selected_generation_id": generation["generation_id"],
               "selected_bundle_sha256": bundle,
               "previous_generation_id": tick.G4_OLD_GENERATION_ID,
               "previous_source_commit": tick.G4_ORIENTATION_HEAD,
               "lease_sequence": 248}
    _put(tmp_path, "clock/current.json", tick._json_text(pointer).encode())
    monkeypatch.setattr(tick, "validate_contract", lambda value: value)
    monkeypatch.setattr(tick, "validate_g4_orientation_intent", lambda value: value)
    monkeypatch.setattr(tick, "_assert_g4_git_state", lambda *_: published_head)
    monkeypatch.setattr(tick, "_git", lambda *_: "")
    monkeypatch.setattr(tick, "_source_bytes", lambda *_: canonical)
    monkeypatch.setattr(tick, "_git_bytes", lambda *_: b"observed-prior-pointer")
    monkeypatch.setattr(tick.tc, "validate_event_chain", lambda _events: None)
    projected_sources = []
    def projected(_repo, _source, _intent, *, source_head):
        projected_sources.append(source_head)
        return canonical
    monkeypatch.setattr(tick, "_g4_orientation_projections", projected)
    state = tick.validate_tick_live_state(tmp_path, contract)
    assert state["status"] == "passed"
    assert state["head"] == published_head
    assert state["source_commit"] == source_head
    assert projected_sources == [source_head]


def test_later_g4_command_readback_rejects_self_consistent_tampering():
    source = "a" * 40
    intent_sha = "b" * 64
    valid = {
        "schema_version": "ariadne.g4_emr4_compass_command_manifest.v1",
        "profile": "g4_recovery_governance_orientation_only",
        "operation_id": tick.G4_ORIENTATION_OPERATION,
        "source_commit": source,
        "intent_sha256": intent_sha,
        "effect_boundary": "separately_reviewed_g4_reconcile_binding_required",
    }
    tick._assert_g4_orientation_command_bytes(
        tick._json_text(valid).encode(), source, intent_sha)
    tampered = {**valid, "effect_boundary": "unreviewed_effect"}
    with pytest.raises(tick.ClockworkTickRejection, match="live_command_bytes"):
        tick._assert_g4_orientation_command_bytes(
            tick._json_text(tampered).encode(), source, intent_sha)


def test_compass_nested_audit_obeys_no_follow_flag(tmp_path, monkeypatch):
    evidence = "authored-synthetic/evidence.md"
    node_id = "synthetic-orientation"
    graph = {
        "project_id": "synthetic", "graph_revision": 1,
        "governance": {"closed_boundaries": []}, "contracts": [],
        "nodes": [{"id": node_id, "status": "accepted", "kind": "tooling",
                   "relationships": [], "contract_evidence": [],
                   "authority": {"authorized_openings": []}}],
    }
    compass = {
        "schema_version": tick.ariadne_compass.SCHEMA_VERSION,
        "project_id": "synthetic", "map_revision": 1, "source_graph_revision": 1,
        "updated_at": "2026-10-25", "orientation_statement": "Synthetic orientation",
        "north_star": {"title": "Synthetic", "summary": "Synthetic", "evidence": [evidence]},
        "programme": {"id": "synthetic", "title": "Synthetic",
                      "master_plan_phase": "G4", "summary": "Synthetic",
                      "evidence": [evidence]},
        "journey": [{"node_id": node_id, "lineage_parent": None,
                     "strategic_role": "Synthetic", "outcome": "Synthetic",
                     "evidence": [evidence]}],
        "current_position": {"node_id": node_id, "strategic_role": "Synthetic",
                             "why_now": "Synthetic", "outcome": "Synthetic",
                             "unlocks": ["Synthetic"], "does_not_solve": ["Synthetic"],
                             "evidence": [evidence]},
        "decision_horizon": [{"id": "synthetic-next", "status": "active",
                              "title": "Synthetic", "strategic_question": "Synthetic",
                              "why_it_matters": "Synthetic", "prerequisites": ["Synthetic"],
                              "boundary_changes": [], "evidence": [evidence]}],
        "programme_support_horizon": [],
        "user_owned_decisions": [{"id": "synthetic-decision", "question": "Synthetic",
                                  "required_before": "Synthetic", "evidence": [evidence]}],
        "map_limits": ["Synthetic"],
    }
    flags = []
    def synthetic_graph_validation(_graph, *, repo_root, require_evidence_files):
        flags.append(require_evidence_files)
        return continuity._reference_errors(
            [evidence], prefix="synthetic", repo_root=repo_root,
            require_exists=require_evidence_files,
        )
    monkeypatch.setattr(continuity, "validate_graph", synthetic_graph_validation)
    def forbidden_follow(path):
        raise AssertionError(f"synthetic evidence target followed: {path}")
    monkeypatch.setattr(Path, "is_file", forbidden_follow)
    assert tick.ariadne_compass.validate_compass(
        compass, graph, repo_root=tmp_path, require_evidence_files=False) == []
    assert flags == [False, False]
    touched = []
    def known_synthetic_follow(path):
        assert path == tmp_path / evidence
        touched.append(path)
        return True
    monkeypatch.setattr(Path, "is_file", known_synthetic_follow)
    assert tick.ariadne_compass.validate_compass(
        compass, graph, repo_root=tmp_path) == []
    assert flags == [False, False, True, True]
    assert touched


def test_external_controller_loader_uses_exact_source_in_fresh_process(tmp_path):
    """One -I -B child imports the capsule and checks scoped module origins only."""

    capsule_root = Path(__file__).resolve().parents[1]
    probe_root = tmp_path
    if configured_root := os.environ.get("EMR4_FOCUSED_PROBE_ROOT"):
        # The one-use runner owns this inherited-permission directory. Pytest's
        # private Windows temp directory is not readable by its restricted child.
        expected_root = tmp_path.parent.parent / "fresh-import-probe"
        probe_root = Path(configured_root).resolve(strict=True)
        assert probe_root == expected_root.resolve(strict=True), "probe_root_binding"
    external = probe_root / "external-source"
    target = probe_root / "synthetic-target"
    names = (
        "configuration_core", "raisa_policy", "trusted_git",
        "governance_clockwork_tick", "bounded_g1b",
    )
    for name in names:
        relative = f"orchestration_harness/{name}.py"
        raw = (capsule_root / relative).read_bytes()
        _put(external, relative, raw)
        _put(target, relative, raw)
    probe = r'''
import sys
from pathlib import Path
from types import SimpleNamespace
capsule, external, target = map(Path, sys.argv[1:])
sys.path.insert(0, str(capsule))
from scripts import ariadne_governance_clockwork_tick as entry
import orchestration_harness as package
names = ("configuration_core", "raisa_policy", "trusted_git", "governance_clockwork_tick", "bounded_g1b")
before = {name: getattr(package, name, None) for name in names}
aliases = {name: sys.modules.get("_ariadne_external_" + name) for name in names}
entry.ROOT = target
def installed_blob(command, **kwargs):
    assert command[:2] == ["git", "show"] and command[2].startswith("HEAD:")
    return SimpleNamespace(stdout=(target / command[2][5:]).read_bytes())
entry.subprocess.run = installed_blob
with entry._g4_external_controller(external) as controller:
    assert controller is package.bounded_g1b
    for name in names:
        assert Path(getattr(package, name).__file__).resolve() == external / "orchestration_harness" / (name + ".py")
    assert package.governance_clockwork_tick is not before["governance_clockwork_tick"]
for name in names:
    assert getattr(package, name, None) is before[name]
    assert sys.modules.get("_ariadne_external_" + name) is aliases[name]
'''
    completed = subprocess.run(
        [sys.executable, "-I", "-B", "-c", probe,
         str(capsule_root), str(external), str(target)],
        check=False, capture_output=True, text=True, timeout=30,
    )
    assert completed.returncode == 0, completed.stderr


def test_projection_is_deterministic_and_preserves_latch_and_agents(tmp_path, monkeypatch):
    parent = "raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review"
    governance = "ariadne-provider-free-clockwork-live-canonical-adoption-retirement"
    graph = {"nodes": [{"id": governance, "status": "accepted", "kind": "foundation"},
                       {"id": parent}], "graph_revision": 462}
    compass = {
        "current_position": {"node_id": parent},
        "journey": [{"node_id": governance}], "map_revision": 444,
        "decision_horizon": [
            {"id": "reception-one-delete-confirm-physical-design-architecture", "status": "active"},
            {"id": "reception-one-appointment-cancellation-direction", "status": "active"},
            {"id": "raisa-practice-context-fabric", "status": "active"},
            {"id": "future-anchor", "status": "candidate"},
        ],
        "programme_support_horizon": [{"id": "blocked-provider", "status": "blocked"}],
        "map_limits": [],
    }
    current = {key: key.encode() for key in tick.CANONICAL_KEYS}
    current["continuity"] = json.dumps(graph).encode()
    current["compass"] = json.dumps(compass).encode()
    monkeypatch.setattr(tick, "_git", lambda *_: "a" * 40)
    monkeypatch.setattr(tick.ariadne_compass, "build_compass_report",
                        lambda *_args, **_kwargs: {"status": "passed", "reasons": []})
    monkeypatch.setattr(tick.ariadne_compass, "render_markdown", lambda _report: "rendered\n")
    intent = {"orientation_date": "2026-10-25",
              "acceptance_path": tick.G4_ORIENTATION_ACCEPTANCE}
    first = tick._g4_orientation_projections(
        tmp_path, current, intent, source_head="a" * 40)
    monkeypatch.setattr(tick, "_git", lambda *_: "b" * 40)
    second = tick._g4_orientation_projections(
        tmp_path, current, intent, source_head="a" * 40)
    assert first == second
    assert all(first[key] == current[key] for key in (
        "active_latch", "current_baton", "error_register", "pattern_report"))
    projected_graph = json.loads(first["continuity"])
    projected_compass = json.loads(first["compass"])
    assert projected_graph["nodes"][-1]["id"] == tick.G4_ORIENTATION_NODE
    assert projected_graph["nodes"][-1]["relationships"] == [
        {"node_id": governance, "relation": "builds_on"}]
    assert projected_graph["nodes"][-1]["coordinates"]["source_head"] == "a" * 40
    assert projected_compass["current_position"]["node_id"] == tick.G4_ORIENTATION_NODE
    assert [h["status"] for h in projected_compass["decision_horizon"][:-1]] == [
        "deferred", "deferred", "active", "candidate"]
    assert projected_compass["programme_support_horizon"][0]["status"] == "blocked"
    assert projected_compass["decision_horizon"][-1]["status"] == "active"
    assert "same-appointment move" in projected_compass["decision_horizon"][-1]["strategic_question"]


def _publish_case(tmp_path, monkeypatch):
    contract = {"canonical_paths": {key: f"canon/{key}" for key in tick.CANONICAL_KEYS},
                "clockwork_root": "clock"}
    old_pointer = {"selected_generation_id": "gen-old", "lease_sequence": 247}
    new_pointer = {"selected_generation_id": "gen-new", "lease_sequence": 248,
                   "previous_generation_id": "gen-old"}
    for key, relative in contract["canonical_paths"].items():
        _put(tmp_path, relative, ("old-" + key).encode())
    for name in (*tick.METADATA_NAMES, tick.GENERATION_NAME):
        _put(tmp_path, f"clock/{name}", ("old-" + name).encode())
    _put(tmp_path, "clock/current.json", tick._json_text(old_pointer).encode())
    prepared = {
        "contract": contract, "intent": {"schema_version": tick.G4_ORIENTATION_INTENT_VERSION,
            "operation_id": tick.G4_ORIENTATION_OPERATION},
        "source_commit": "a" * 40, "base_pointer": old_pointer,
        "pointer": new_pointer,
        "canonical": {key: ("new-" + key).encode() for key in tick.CANONICAL_KEYS},
        "metadata": {name: ("new-" + name).encode() for name in tick.METADATA_NAMES},
        "generation_manifest": {"generation_id": "gen-new"},
    }
    monkeypatch.setattr(tick, "validate_prepared_tick", lambda *_: prepared)
    monkeypatch.setattr(tick, "_assert_git_state", lambda *_: "a" * 40)
    monkeypatch.setattr(tick, "_assert_g4_git_state", lambda *_: "a" * 40)
    monkeypatch.setattr(tick, "_git", lambda *_: "b" * 40)
    monkeypatch.setattr(tick, "_g4_orientation_baseline", lambda *_: None)
    monkeypatch.setattr(tick, "validate_tick_live_state", lambda *_: {"status": "passed"})
    manifest = _effect_manifest(tmp_path, prepared)
    return prepared, manifest


def test_pointer_last_and_pre_pointer_snapshot_rollback(tmp_path, monkeypatch):
    prepared, manifest = _publish_case(tmp_path, monkeypatch)
    contract = prepared["contract"]
    guard_calls: list[bool] = []
    def guard(**_kwargs):
        guard_calls.append((tmp_path / "clock/writer.lock").exists())
        return SimpleNamespace(execution_authorized=True)
    original = {p: p.read_bytes() for p in [
        *(tmp_path / relative for relative in contract["canonical_paths"].values()),
        *(tmp_path / "clock" / name for name in (*tick.METADATA_NAMES, tick.GENERATION_NAME)),
        tmp_path / "clock/current.json",
    ]}
    with pytest.raises(OSError, match="injected_tick_precommit_failure"):
        tick.publish_tick_generation(
            tmp_path, prepared, writer_id=tick.WRITER,
            fail_at="before_pointer_replace", g4_effect_checker=guard,
            g4_effect_context=object(), g4_effect_manifest=manifest,
        )
    assert all(path.read_bytes() == raw for path, raw in original.items())
    assert guard_calls == [False, True]
    replaced: list[Path] = []
    real_replace = os.replace
    def recording_replace(src, dst):
        replaced.append(dst)
        real_replace(src, dst)
    monkeypatch.setattr(tick.os, "replace", recording_replace)
    tick.publish_tick_generation(
        tmp_path, prepared, writer_id=tick.WRITER,
        g4_effect_checker=guard, g4_effect_context=object(), g4_effect_manifest=manifest,
    )
    assert replaced[-1] == tmp_path / "clock/current.json"
    assert tick._load(tmp_path / "clock/current.json")["lease_sequence"] == 248
    assert guard_calls == [False, True, False, True]


def test_effect_manifest_rejects_an_unreviewed_afterimage(tmp_path, monkeypatch):
    prepared, manifest = _publish_case(tmp_path, monkeypatch)
    wrong = {**manifest, "after_sha256": dict(manifest["after_sha256"])}
    first = next(iter(wrong["after_sha256"]))
    wrong["after_sha256"][first] = "0" * 64
    with pytest.raises(tick.ClockworkTickRejection, match="effect_manifest_images"):
        tick._verify_g4_effect_manifest_images(tmp_path, prepared, wrong)


def test_foreign_writer_lock_is_not_removed(tmp_path, monkeypatch):
    prepared, manifest = _publish_case(tmp_path, monkeypatch)
    lock = tmp_path / "clock/writer.lock"
    lock.write_bytes(b"other-writer")
    guard = lambda **_kwargs: SimpleNamespace(execution_authorized=True)
    with pytest.raises(tick.ClockworkTickRejection, match="tick_lease_occupied"):
        tick.publish_tick_generation(
            tmp_path, prepared, writer_id=tick.WRITER,
            g4_effect_checker=guard, g4_effect_context=object(),
            g4_effect_manifest=manifest,
        )
    assert lock.read_bytes() == b"other-writer"
    assert tick._load(tmp_path / "clock/current.json")["lease_sequence"] == 247


def test_under_lock_rejection_and_snapshot_failure_release_owned_lock(tmp_path, monkeypatch):
    prepared, manifest = _publish_case(tmp_path, monkeypatch)
    lock = tmp_path / "clock/writer.lock"
    calls: list[bool] = []
    def rejecting_guard(**_kwargs):
        calls.append(lock.exists())
        return SimpleNamespace(execution_authorized=len(calls) == 1)
    with pytest.raises(tick.ClockworkTickRejection, match="effect_not_authorized"):
        tick.publish_tick_generation(
            tmp_path, prepared, writer_id=tick.WRITER,
            g4_effect_checker=rejecting_guard, g4_effect_context=object(),
            g4_effect_manifest=manifest,
        )
    assert calls == [False, True]
    assert not lock.exists()
    assert tick._load(tmp_path / "clock/current.json")["lease_sequence"] == 247

    fail_snapshot = False
    original_read = Path.read_bytes
    def selected_read(path):
        if fail_snapshot and path == tmp_path / "canon/continuity":
            raise OSError("synthetic_snapshot_read_failure")
        return original_read(path)
    monkeypatch.setattr(Path, "read_bytes", selected_read)
    calls.clear()
    def approved_guard(**_kwargs):
        nonlocal fail_snapshot
        calls.append(lock.exists())
        if len(calls) == 2:
            fail_snapshot = True
        return SimpleNamespace(execution_authorized=True)
    with pytest.raises(OSError, match="synthetic_snapshot_read_failure"):
        tick.publish_tick_generation(
            tmp_path, prepared, writer_id=tick.WRITER,
            g4_effect_checker=approved_guard, g4_effect_context=object(),
            g4_effect_manifest=manifest,
        )
    fail_snapshot = False
    assert calls == [False, True]
    assert not lock.exists()
    assert tick._load(tmp_path / "clock/current.json")["lease_sequence"] == 247


def test_post_pointer_failure_is_committed_and_not_restored(tmp_path, monkeypatch):
    prepared, manifest = _publish_case(tmp_path, monkeypatch)
    guard = lambda **_kwargs: SimpleNamespace(execution_authorized=True)
    with pytest.raises(tick.CommittedClockworkTick, match="postcommit_failure"):
        tick.publish_tick_generation(
            tmp_path, prepared, writer_id=tick.WRITER,
            fail_at="after_pointer_replace", g4_effect_checker=guard,
            g4_effect_context=object(), g4_effect_manifest=manifest,
        )
    assert tick._load(tmp_path / "clock/current.json")["lease_sequence"] == 248
    assert not (tmp_path / "clock/writer.lock").exists()


def test_inverse_restores_observed_baseline_not_old_generation_bytes(tmp_path, monkeypatch):
    contract, canonical, metadata, old_pointer = _synthetic_predecessor(tmp_path, monkeypatch)
    for key, relative in contract["canonical_paths"].items():
        _put(tmp_path, relative, ("projected-" + key).encode())
    for name in (*tick.METADATA_NAMES, tick.GENERATION_NAME):
        _put(tmp_path, f"clock/{name}", ("projected-" + name).encode())
    current_pointer = {**old_pointer, "selected_generation_id": "gen-new",
                       "lease_sequence": 248}
    _put(tmp_path, "clock/current.json", tick._json_text(current_pointer).encode())
    monkeypatch.setattr(tick, "validate_contract", lambda value: value)
    monkeypatch.setattr(tick, "validate_tick_live_state", lambda *_: {
        "event_kind": tick.G4_ORIENTATION_EVENT,
        "generation_id": "gen-new", "source_commit": "accepted-executing-head",
        "head": "b" * 40,
    })
    head_checks = []
    def check_current_head(_root, _contract, expected_source=None):
        head_checks.append(((tmp_path / "clock/writer.lock").exists(), expected_source))
        assert expected_source in (None, "b" * 40)
        return "b" * 40
    monkeypatch.setattr(tick, "_assert_g4_git_state", check_current_head)
    monkeypatch.setattr(tick, "_source_bytes", lambda *_: canonical)
    monkeypatch.setattr(tick, "_source_metadata", lambda *_: metadata)
    monkeypatch.setattr(tick, "_source_pointer", lambda *_: old_pointer)
    restored_pointer = {**old_pointer, "phase": "recovery_baseline", "lease_sequence": 249}
    intent_relative = "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json"
    _put(tmp_path, intent_relative, b"synthetic-frozen-intent")
    before, after = tick._g4_effect_images(
        tmp_path, contract, canonical, metadata, restored_pointer)
    assert len(before) == len(after) == 12
    manifest = {
        "before_sha256": before, "after_sha256": after,
        "lease_before": 248, "lease_after": 249,
        "mode": "rollback", "stage": "reconcile",
        "operation_id": tick.G4_ORIENTATION_OPERATION,
        "source_commit": tick.G4_ORIENTATION_TREE,
        "source_tree": tick.G4_ORIENTATION_TREE,
        "intent_sha256": tick._hash_bytes((tmp_path / intent_relative).read_bytes()),
    }
    guard_calls: list[bool] = []
    def guard(**_kwargs):
        guard_calls.append((tmp_path / "clock/writer.lock").exists())
        return SimpleNamespace(execution_authorized=True)
    restored = tick.rollback_g4_orientation_generation(
        tmp_path, contract, writer_id=tick.WRITER,
        g4_effect_checker=guard, g4_effect_context=object(), g4_effect_manifest=manifest,
    )
    assert restored["byte_exact"] is True
    assert restored["status"] == "contained_recovery_baseline"
    assert restored["lease_sequence"] == 249
    assert guard_calls == [False, True]
    assert (True, "b" * 40) in head_checks
    assert all((tmp_path / contract["canonical_paths"][key]).read_bytes() == raw
               for key, raw in canonical.items())
    assert (tmp_path / contract["canonical_paths"]["active_latch"]).read_bytes() == canonical["active_latch"]
    assert (tmp_path / contract["canonical_paths"]["current_baton"]).read_bytes() == canonical["current_baton"]
