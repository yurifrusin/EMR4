"""Authored goal-event regression source; not executed by the author.

Synthetic file mechanics exercise the real lease/pointer/rollback engine. Git,
initial predecessor validation and full Compass rendering are explicit doubles;
these tests do not establish actual Git topology, real-map admission or schema.
Only the two previously pinned ordinary goal-data files are read as inputs.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestration_harness import governance_clockwork_tick as tick
from orchestration_harness import governance_goal_tick as goal
from orchestration_harness import governance_goal_update as goals


def _put(root, relative, raw):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def _fixture(root, monkeypatch):
    source, tree = "a" * 40, "b" * 40
    contract = {"canonical_paths": {key: f"canon/{key}" for key in tick.CANONICAL_KEYS},
                "clockwork_root": "clock"}
    intent = {"schema_version": goals.INTENT_VERSION, "operation_id": goals.OPERATION_ID,
        "recorded_at": "2026-10-26T00:00:00+00:00", "payload_sha256": goals.PAYLOAD_SHA256,
        "capability_dispositions_sha256": goals.DISPOSITIONS_SHA256,
        "effect": "goal_roadmap_only", "recommendation_selection_dispatch": "unchanged_not_enabled"}
    payload = Path("C:/Users/there/EMR4-tools/compass-gpms-goal-steering-preparation-v1/gpms-goal-update-payload-v2.json").read_bytes()
    dispositions = Path("C:/Users/there/EMR4-tools/compass-g4-reconnection-candidate-v1/capability-dispositions-v1.json").read_bytes()
    data = {goal.INTENT_PATH: tick._json_text(intent).encode(),
            goals.PAYLOAD_REFERENCE: payload, goal.DISPOSITIONS_PATH: dispositions}
    compass = {"map_revision": 17, "source_graph_revision": 29,
        "north_star": {"title": "old", "summary": "old", "evidence": ["docs/old.md"]},
        "orientation_statement": "old", "decision_horizon": [{"id": "retained", "status": "deferred"}],
        "map_limits": ["old qualification"], "current_position": {"node_id": "unchanged"},
        "programme": {"id": "unchanged"}, "journey": ["unchanged"]}
    canonical = {key: ("authored-" + key).encode() for key in tick.CANONICAL_KEYS}
    canonical["compass"] = tick._json_text(compass).encode()
    canonical["continuity"] = tick._json_text({"nodes": [], "graph_revision": 29}).encode()
    canonical["active_latch"] = tick._json_text({"operation_id": "retained-active",
        "status": "in_progress", "protected_boundaries": ["providers", "real_data"]}).encode()
    ownership = {"schema_version": tick.OWNERSHIP_VERSION, "phase": "clockwork_active",
        "surface_owners": {key: tick.WRITER for key in (*tick.CANONICAL_KEYS,
            "command_manifest", "transaction", "ownership")},
        "legacy_writers": {key: "retired" for key in ("bespoke_continuity_updater",
            "manual_baton_editor", "manual_latch_editor", "manual_register_fixture_editor")}}
    metadata = {"command-manifest.json": b"authored-command", "transaction.json": b"authored-transaction",
                "ownership.json": tick._json_text(ownership).encode()}
    canonical_sha = {key: tick._hash_bytes(raw) for key, raw in canonical.items()}
    metadata_sha = {key: tick._hash_bytes(raw) for key, raw in metadata.items()}
    bundle = tick._hash_json({"canonical": canonical_sha, "metadata": metadata_sha})
    generation = {"schema_version": tick.GENERATION_VERSION, "generation_id": "gen-" + bundle,
        "bundle_sha256": bundle, "canonical_sha256s": canonical_sha, "metadata_sha256s": metadata_sha}
    metadata[tick.GENERATION_NAME] = tick._json_text(generation).encode()
    pointer = {"schema_version": tick.POINTER_VERSION, "phase": "clockwork_active", "writer": tick.WRITER,
        "selected_generation_id": generation["generation_id"], "selected_bundle_sha256": bundle,
        "lease_sequence": 31, "previous_generation_id": "gen-authored-prior", "previous_source_commit": "c" * 40}
    pointer_raw = tick._json_text(pointer).encode()
    git_files = {**{contract["canonical_paths"][k]: v for k, v in canonical.items()},
        **{f"clock/{k}": v for k, v in metadata.items()}, "clock/current.json": pointer_raw, **data}
    for path, raw in git_files.items():
        _put(root, path, raw)
    monkeypatch.setattr(tick, "validate_contract", lambda value: value)
    monkeypatch.setattr(tick, "_assert_g4_git_state", lambda _root, _contract, expected=None: source)
    monkeypatch.setattr(tick, "_git", lambda _root, *args: tree if args == ("rev-parse", "HEAD^{tree}") else "")
    monkeypatch.setattr(tick, "_git_bytes", lambda _root, selected, path: git_files[path])
    monkeypatch.setattr(tick, "_source_bytes", lambda *_: dict(canonical))
    monkeypatch.setattr(tick, "validate_active_operation", lambda value: value)
    original_live = tick.validate_tick_live_state
    def live(repo, selected_contract):
        gen = tick._load(repo / "clock" / tick.GENERATION_NAME)
        return original_live(repo, selected_contract) if "goal_update" in gen else {"status": "passed"}
    monkeypatch.setattr(tick, "validate_tick_live_state", live)
    monkeypatch.setattr(tick.ariadne_compass, "build_compass_report",
        lambda compass, graph, **_: {"status": "passed", "compass": compass})
    monkeypatch.setattr(tick.ariadne_compass, "render_markdown",
        lambda report: tick._json_text(report["compass"]))
    return contract, intent, canonical, metadata, pointer, git_files


def _manifest(root, prepared):
    metadata = {**prepared["metadata"], tick.GENERATION_NAME:
                tick._json_text(prepared["generation_manifest"]).encode()}
    before, after = tick._g4_effect_images(root, prepared["contract"],
        prepared["canonical"], metadata, prepared["pointer"])
    return {"schema_version": "ariadne.g4_compass_goal_update_effect_manifest.v1",
        "before_sha256": before, "after_sha256": after,
        "lease_before": 31, "lease_after": 32, "mode": "publish", "stage": "goal_update",
        "operation_id": goals.OPERATION_ID, "source_commit": "a" * 40,
        "source_tree": "b" * 40, "intent_sha256": tick._hash_bytes((root / goal.INTENT_PATH).read_bytes())}


def test_prepare_recomputes_and_preserves_all_unowned_bytes(tmp_path, monkeypatch):
    contract, intent, before, _, pointer, _ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    assert tick.validate_prepared_tick(tmp_path, prepared) == prepared
    assert all(prepared["canonical"][key] == before[key] for key in goal.PRESERVED)
    assert prepared["pointer"]["lease_sequence"] == pointer["lease_sequence"] + 1
    assert prepared["generation_manifest"]["goal_update"]["intent"] == intent
    assert goal._physical(tmp_path, contract)[0] == before


@pytest.mark.parametrize("section", ["canonical", "metadata", "pointer", "generation_manifest"])
def test_prepared_tamper_rejected(tmp_path, monkeypatch, section):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    corrupt = copy.deepcopy(prepared)
    if section in ("canonical", "metadata"):
        corrupt[section][next(iter(corrupt[section]))] += b"unreviewed"
    else:
        corrupt[section]["unreviewed"] = True
    with pytest.raises(tick.ClockworkTickRejection, match="goal_update_prepared_semantics"):
        tick.validate_prepared_tick(tmp_path, corrupt)


def test_third_drift_and_ownership_change_fail_closed(tmp_path, monkeypatch):
    contract, intent, before, *_ = _fixture(tmp_path, monkeypatch)
    _put(tmp_path, "canon/current_baton", b"unreviewed drift")
    with pytest.raises(tick.ClockworkTickRejection, match="uncommitted_predecessor_drift"):
        goal.build(tmp_path, contract, intent)
    _put(tmp_path, "canon/current_baton", before["current_baton"])
    _put(tmp_path, "clock/ownership.json", b"unreviewed ownership")
    with pytest.raises(tick.ClockworkTickRejection, match="uncommitted_predecessor_drift"):
        goal.build(tmp_path, contract, intent)


def test_publish_requires_independent_effect_hook_before_any_write(tmp_path, monkeypatch):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    before = goal._physical(tmp_path, contract)
    with pytest.raises(tick.ClockworkTickRejection, match="effect_admission_required"):
        tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER)
    assert goal._physical(tmp_path, contract) == before
    assert not (tmp_path / "clock/writer.lock").exists()


def test_effect_checks_before_and_under_lease_pointer_last_and_idempotency(tmp_path, monkeypatch):
    contract, intent, before, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    manifest = _manifest(tmp_path, prepared)
    checks, replacements = [], []
    def checker(**_):
        checks.append((tmp_path / "clock/writer.lock").exists())
        return SimpleNamespace(execution_authorized=True)
    original_replace = tick.os.replace
    def replace(source, target):
        replacements.append(Path(target).name)
        return original_replace(source, target)
    monkeypatch.setattr(tick.os, "replace", replace)
    state = tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER,
        goal_effect_checker=checker, goal_effect_context=object(), goal_effect_manifest=manifest)
    assert checks == [False, True]
    assert replacements[-1] == "current.json"
    assert state["event_kind"] == "goal_update" and state["lease_sequence"] == 32
    assert all(goal._physical(tmp_path, contract)[0][key] == before[key] for key in goal.PRESERVED)
    committed = goal._physical(tmp_path, contract)
    assert tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER) == state
    assert goal._physical(tmp_path, contract) == committed
    assert checks == [False, True] and not (tmp_path / "clock/writer.lock").exists()


@pytest.mark.parametrize("failure", ["after:compass", "after:transaction.json", "before_pointer_replace"])
def test_pre_pointer_failure_restores_all_original_bytes(tmp_path, monkeypatch, failure):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    before = goal._physical(tmp_path, contract)
    with pytest.raises(OSError):
        tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER,
            goal_effect_checker=lambda **_: SimpleNamespace(execution_authorized=True),
            goal_effect_context=object(), goal_effect_manifest=_manifest(tmp_path, prepared), fail_at=failure)
    assert goal._physical(tmp_path, contract) == before
    assert not (tmp_path / "clock/writer.lock").exists()


def test_under_lease_denial_leaves_canonical_bytes_untouched(tmp_path, monkeypatch):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    before = goal._physical(tmp_path, contract)
    calls = []
    def checker(**_):
        calls.append(True)
        return SimpleNamespace(execution_authorized=len(calls) == 1)
    with pytest.raises(tick.ClockworkTickRejection, match="effect_not_authorized"):
        tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER,
            goal_effect_checker=checker, goal_effect_context=object(), goal_effect_manifest=_manifest(tmp_path, prepared))
    assert len(calls) == 2 and goal._physical(tmp_path, contract) == before
    assert not (tmp_path / "clock/writer.lock").exists()


@pytest.mark.parametrize("decision", [
    SimpleNamespace(execution_authorized=False),
    SimpleNamespace(execution_authorized=None),
    SimpleNamespace(),
    SimpleNamespace(execution_authorized=1),
    SimpleNamespace(execution_authorized="false"),
    None,
], ids=["literal-false", "none-value", "missing-attribute", "truthy-int", "truthy-string", "missing-decision"])
@pytest.mark.parametrize("location", ["before-lease", "under-lease"])
def test_only_literal_true_can_authorize_goal_effect(tmp_path, monkeypatch, decision, location):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    before = goal._physical(tmp_path, contract)
    calls, acquisitions, replacements = [], [], []
    original_lease, original_replace = tick._write_lease, tick.os.replace
    def lease(*args, **kwargs):
        acquisitions.append(True)
        return original_lease(*args, **kwargs)
    def replace(source, target):
        replacements.append(Path(target))
        return original_replace(source, target)
    def checker(**_):
        calls.append((tmp_path / "clock/writer.lock").exists())
        if location == "under-lease" and len(calls) == 1:
            return SimpleNamespace(execution_authorized=True)
        return decision
    monkeypatch.setattr(tick, "_write_lease", lease)
    monkeypatch.setattr(tick.os, "replace", replace)
    with pytest.raises(tick.ClockworkTickRejection, match="goal_update_effect_not_authorized"):
        tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER,
            goal_effect_checker=checker, goal_effect_context=object(),
            goal_effect_manifest=_manifest(tmp_path, prepared))
    assert calls == ([False] if location == "before-lease" else [False, True])
    assert acquisitions == ([] if location == "before-lease" else [True])
    assert replacements == []
    assert goal._physical(tmp_path, contract) == before
    assert not (tmp_path / "clock/writer.lock").exists()


def test_committed_exception_stays_committed_and_readback_detects_drift(tmp_path, monkeypatch):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    with pytest.raises(tick.CommittedClockworkTick):
        tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER,
            goal_effect_checker=lambda **_: SimpleNamespace(execution_authorized=True),
            goal_effect_context=object(), goal_effect_manifest=_manifest(tmp_path, prepared), fail_at="after_pointer_replace")
    assert tick.validate_tick_live_state(tmp_path, contract)["lease_sequence"] == 32
    _put(tmp_path, "canon/active_latch", b"forbidden latch drift")
    with pytest.raises(tick.ClockworkTickRejection, match="goal_update_live_semantics"):
        tick.validate_tick_live_state(tmp_path, contract)


def test_goal_generation_cannot_use_generic_rollback(tmp_path, monkeypatch):
    contract, intent, *_ = _fixture(tmp_path, monkeypatch)
    prepared = goal.build(tmp_path, contract, intent)
    tick.publish_tick_generation(tmp_path, prepared, writer_id=tick.WRITER,
        goal_effect_checker=lambda **_: SimpleNamespace(execution_authorized=True),
        goal_effect_context=object(), goal_effect_manifest=_manifest(tmp_path, prepared))
    with pytest.raises(tick.ClockworkTickRejection, match="separate_bound_inverse_required"):
        tick.rollback_tick_generation(tmp_path, contract, writer_id=tick.WRITER)
