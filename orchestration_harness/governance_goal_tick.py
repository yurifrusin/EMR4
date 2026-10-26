"""Goal-only event implementation inside the existing Clockwork sole writer.

No alternate writer, controller, selector or automatic runtime is introduced.
All source reads are the existing contract's selected surfaces or three closed
ordinary goal inputs. Source/effect admission remains separately required.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestration_harness import governance_clockwork_tick as tick
from orchestration_harness import governance_goal_update as goals

INTENT_PATH = "orchestration/continuity/compass-gpms-goal-update/goal-intent.json"
DISPOSITIONS_PATH = "orchestration/continuity/compass-gpms-goal-update/capability-dispositions-v1.json"
DATA_PATHS = (INTENT_PATH, goals.PAYLOAD_REFERENCE, DISPOSITIONS_PATH)
PRESERVED = ("continuity", "active_latch", "current_baton", "error_register", "pattern_report")
EVENT = "goal_update"


def _intent(value):
    try:
        return goals.validate_goal_intent(value)
    except goals.GoalUpdateRejection as error:
        raise tick.ClockworkTickRejection(str(error)) from error


def _snapshot(repo_root, contract, source):
    canonical = tick._source_bytes(repo_root, contract, source)
    metadata = {name: tick._git_bytes(repo_root, source, f"{contract['clockwork_root']}/{name}")
                for name in tick.PREDECESSOR_METADATA_NAMES}
    pointer_raw = tick._git_bytes(repo_root, source, f"{contract['clockwork_root']}/{tick.POINTER_NAME}")
    data = {path: tick._git_bytes(repo_root, source, path) for path in DATA_PATHS}
    # Installed goal source must remain identical even after a committed effect.
    if any((repo_root / path).read_bytes() != raw for path, raw in data.items()):
        tick._reject("goal_update_installed_input_drift")
    return canonical, metadata, pointer_raw, data


def _physical(repo_root, contract):
    canonical = {key: (repo_root / path).read_bytes()
                 for key, path in contract["canonical_paths"].items()}
    metadata = {name: (repo_root / contract["clockwork_root"] / name).read_bytes()
                for name in tick.PREDECESSOR_METADATA_NAMES}
    pointer_raw = (repo_root / contract["clockwork_root"] / tick.POINTER_NAME).read_bytes()
    return canonical, metadata, pointer_raw


def _validate_snapshot(canonical, metadata, pointer_raw):
    generation = json.loads(metadata[tick.GENERATION_NAME].decode("utf-8"))
    pointer = json.loads(pointer_raw.decode("utf-8"))
    ownership = json.loads(metadata["ownership.json"].decode("utf-8"))
    canonical_sha = {key: tick._hash_bytes(raw) for key, raw in canonical.items()}
    metadata_sha = {name: tick._hash_bytes(metadata[name]) for name in tick.METADATA_NAMES}
    bundle = tick._hash_json({"canonical": canonical_sha, "metadata": metadata_sha})
    if (set(canonical) != set(tick.CANONICAL_KEYS)
        or set(metadata) != set(tick.PREDECESSOR_METADATA_NAMES)
        or generation.get("schema_version") != tick.GENERATION_VERSION
        or generation.get("canonical_sha256s") != canonical_sha
        or generation.get("metadata_sha256s") != metadata_sha
        or generation.get("bundle_sha256") != bundle
        or generation.get("generation_id") != "gen-" + bundle
        or pointer.get("selected_generation_id") != generation.get("generation_id")
        or pointer.get("selected_bundle_sha256") != bundle
        or pointer.get("schema_version") != tick.POINTER_VERSION
        or pointer.get("phase") != "clockwork_active" or pointer.get("writer") != tick.WRITER
        or type(pointer.get("lease_sequence")) is not int or pointer["lease_sequence"] < 0
        or ownership.get("schema_version") != tick.OWNERSHIP_VERSION
        or ownership.get("phase") != "clockwork_active"
        or set(ownership.get("surface_owners", {})) != set(tick.CANONICAL_KEYS)
            | {"command_manifest", "transaction", "ownership"}
        or set(ownership.get("surface_owners", {}).values()) != {tick.WRITER}
        or set(ownership.get("legacy_writers", {})) != {
            "bespoke_continuity_updater", "manual_baton_editor",
            "manual_latch_editor", "manual_register_fixture_editor"}
        or set(ownership.get("legacy_writers", {}).values()) != {"retired"}):
        tick._reject("goal_update_predecessor_images_or_ownership")
    if generation.get("goal_update") is not None:
        tick._reject("goal_update_already_recorded")
    return pointer


def baseline(repo_root: Path, contract: dict, expected_source=None):
    """No drift exception: all twelve physical preimages equal committed HEAD."""
    source = tick._assert_g4_git_state(repo_root, contract, expected_source)
    tick.validate_tick_live_state(repo_root, contract)
    canonical, metadata, pointer_raw, data = _snapshot(repo_root, contract, source)
    if _physical(repo_root, contract) != (canonical, metadata, pointer_raw):
        tick._reject("goal_update_uncommitted_predecessor_drift")
    _validate_snapshot(canonical, metadata, pointer_raw)
    return source, canonical, metadata, pointer_raw, data


def _derive(repo_root, contract, intent, source, canonical_before, metadata_before, pointer_raw, data):
    base_pointer = _validate_snapshot(canonical_before, metadata_before, pointer_raw)
    if _intent(json.loads(data[INTENT_PATH].decode("utf-8"))) != intent:
        tick._reject("goal_update_intent_not_installed")
    try:
        compass = goals.project_goal_update(
            json.loads(canonical_before["compass"].decode("utf-8")), intent,
            payload_raw=data[goals.PAYLOAD_REFERENCE], dispositions_raw=data[DISPOSITIONS_PATH])
    except goals.GoalUpdateRejection as error:
        raise tick.ClockworkTickRejection(str(error)) from error
    graph = json.loads(canonical_before["continuity"].decode("utf-8"))
    report = tick.ariadne_compass.build_compass_report(
        compass, graph, repo_root=repo_root, require_evidence_files=False)
    if report["status"] != "passed":
        tick._reject("goal_update_compass_validation")
    canonical = dict(canonical_before)
    canonical["compass"] = tick._json_text(compass).encode("utf-8")
    canonical["compass_markdown"] = tick.ariadne_compass.render_markdown(report).encode("utf-8")
    if any(canonical[key] != canonical_before[key] for key in PRESERVED):
        tick._reject("goal_update_byte_preservation")
    intent_sha = tick.tc.sha256(intent)
    transaction_id = "txn-" + tick.tc.sha256({"goal_update": intent_sha, "source": source})[7:31]
    events, previous = [], tick.tc.ZERO_DIGEST
    for event_type, payload in (
        ("goal-update-intent-accepted", {"intent_sha256": intent_sha}),
        ("goal-update-predecessor-bound", {"pointer_sha256": tick._hash_bytes(pointer_raw)}),
        ("goal-update-projected", {"goal_roadmap_only": True, "dispatch_enabled": False}),
        ("transaction-prepared", {"publication_mode": "lease_bound_pointer_last_live_tick"}),
    ):
        event = tick.tc._event(journal_id="journal-" + transaction_id[4:],
            transaction_id=transaction_id, operation_id=goals.OPERATION_ID,
            sequence=len(events) + 1, previous=previous, event_type=event_type, payload=payload)
        events.append(event)
        previous = event["event_sha256"]
    tick.tc.validate_event_chain(events)
    latch = tick.validate_active_operation(json.loads(canonical_before["active_latch"].decode("utf-8")))
    transaction = {
        "schema_version": tick.TRANSACTION_VERSION, "event_kind": EVENT,
        "operation_id": goals.OPERATION_ID, "transaction_id": transaction_id,
        "source_commit": source, "previous_source_commit": source,
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_bundle_sha256": base_pointer["selected_bundle_sha256"],
        "previous_canonical_sha256s": {key: tick._hash_bytes(raw) for key, raw in canonical_before.items()},
        "previous_metadata_sha256s": {key: tick._hash_bytes(raw) for key, raw in metadata_before.items()},
        "projection_sha256s": {"graph": tick.tc.sha256(graph), "compass": tick.tc.sha256(compass),
                              "latch": tick.tc.sha256(latch)},
        "journal": events, "publication_mode": "lease_bound_pointer_last_live_tick",
        "next_boundaries_sha256": tick.tc.sha256(latch["protected_boundaries"]),
        "register_bytes_preserved": True, "pattern_bytes_preserved": True,
    }
    command = {"schema_version": "ariadne.goal_update_command_manifest.v1",
        "profile": "goal_roadmap_only", "operation_id": goals.OPERATION_ID,
        "source_commit": source, "intent_sha256": intent_sha,
        "effect_boundary": "separate_exact_goal_update_effect_admission_required"}
    metadata = {"command-manifest.json": tick._json_text(command).encode("utf-8"),
        "transaction.json": tick._json_text(transaction).encode("utf-8"),
        "ownership.json": metadata_before["ownership.json"]}
    canonical_sha = {key: tick._hash_bytes(raw) for key, raw in canonical.items()}
    metadata_sha = {key: tick._hash_bytes(raw) for key, raw in metadata.items()}
    bundle = tick._hash_json({"canonical": canonical_sha, "metadata": metadata_sha})
    generation = {"schema_version": tick.GENERATION_VERSION,
        "generation_id": "gen-" + bundle, "bundle_sha256": bundle, "source_commit": source,
        "previous_generation": {"generation_id": base_pointer["selected_generation_id"],
            "bundle_sha256": base_pointer["selected_bundle_sha256"], "source_commit": source,
            "canonical_sha256s": transaction["previous_canonical_sha256s"],
            "metadata_sha256s": transaction["previous_metadata_sha256s"],
            "pointer_sha256": tick._hash_bytes(pointer_raw)},
        "canonical_sha256s": canonical_sha, "metadata_sha256s": metadata_sha,
        "goal_update": {"intent": intent, "intent_sha256": intent_sha}}
    pointer = {**base_pointer, "selected_generation_id": generation["generation_id"],
        "selected_bundle_sha256": bundle, "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_source_commit": source, "lease_sequence": base_pointer["lease_sequence"] + 1}
    return {"schema_version": tick.PREPARED_VERSION, "contract": contract, "intent": intent,
        "source_commit": source, "base_pointer": base_pointer, "canonical": canonical,
        "metadata": metadata, "generation_manifest": generation, "pointer": pointer}


def build(repo_root: Path, contract_value: object, intent_value: object):
    contract, intent = tick.validate_contract(contract_value), _intent(intent_value)
    source, canonical, metadata, pointer_raw, data = baseline(repo_root, contract)
    return _derive(repo_root, contract, intent, source, canonical, metadata, pointer_raw, data)


def validate_prepared(repo_root: Path, prepared: dict):
    expected = build(repo_root, prepared["contract"], prepared["intent"])
    if prepared != expected:
        tick._reject("goal_update_prepared_semantics")
    return prepared


def validate_live(repo_root: Path, contract: dict, generation: dict):
    """Recompute the committed event from its exact selected Git predecessor."""
    source = generation.get("source_commit")
    if not isinstance(source, str) or tick.HEX40.fullmatch(source) is None:
        tick._reject("goal_update_live_source")
    head = tick._assert_g4_git_state(repo_root, contract)
    tick._git(repo_root, "merge-base", "--is-ancestor", source, head)
    marker = generation.get("goal_update")
    if not isinstance(marker, dict) or set(marker) != {"intent", "intent_sha256"}:
        tick._reject("goal_update_live_marker")
    intent = _intent(marker["intent"])
    canonical, metadata, pointer_raw, data = _snapshot(repo_root, contract, source)
    expected = _derive(repo_root, contract, intent, source, canonical, metadata, pointer_raw, data)
    actual_canonical, actual_metadata, actual_pointer = _physical(repo_root, contract)
    expected_metadata = {**expected["metadata"], tick.GENERATION_NAME:
                         tick._json_text(expected["generation_manifest"]).encode("utf-8")}
    if (generation != expected["generation_manifest"] or actual_canonical != expected["canonical"]
        or actual_metadata != expected_metadata
        or actual_pointer != tick._json_text(expected["pointer"]).encode("utf-8")):
        tick._reject("goal_update_live_semantics")
    return {"schema_version": "ariadne.governance_live_tick_state.v1", "status": "passed",
        "head": head, "source_commit": source, "generation_id": generation["generation_id"],
        "bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": expected["base_pointer"]["selected_generation_id"],
        "previous_source_commit": source, "lease_sequence": expected["pointer"]["lease_sequence"],
        "operation_id": goals.OPERATION_ID, "event_kind": EVENT, "canonical_drift": 0,
        "clockwork_owned_surfaces": 10, "dual_owned_surfaces": 0,
        "retired_legacy_writer_classes": 4, "previous_metadata_files": 4}


def verify_effect(repo_root: Path, prepared: dict, manifest: dict):
    # Recheck the exact committed predecessor both before and under the lease.
    baseline(repo_root, prepared["contract"], prepared["source_commit"])
    metadata = {**prepared["metadata"], tick.GENERATION_NAME:
                tick._json_text(prepared["generation_manifest"]).encode("utf-8")}
    before, after = tick._g4_effect_images(repo_root, prepared["contract"],
                                          prepared["canonical"], metadata, prepared["pointer"])
    if (manifest.get("schema_version") != "ariadne.g4_compass_goal_update_effect_manifest.v1"
        or manifest.get("before_sha256") != before or manifest.get("after_sha256") != after
        or manifest.get("lease_before") != prepared["base_pointer"]["lease_sequence"]
        or manifest.get("lease_after") != prepared["pointer"]["lease_sequence"]
        or manifest.get("mode") != "publish" or manifest.get("stage") != EVENT
        or manifest.get("operation_id") != goals.OPERATION_ID
        or manifest.get("source_commit") != prepared["source_commit"]
        or manifest.get("source_tree") != tick._git(repo_root, "rev-parse", "HEAD^{tree}")
        or manifest.get("intent_sha256") != tick._hash_bytes((repo_root / INTENT_PATH).read_bytes())):
        tick._reject("goal_update_effect_manifest_images")


def idempotent_readback(repo_root: Path, prepared: dict, writer_id: str):
    if writer_id != tick.WRITER:
        tick._reject("tick_writer_not_clockwork")
    contract = tick.validate_contract(prepared["contract"])
    state = tick.validate_tick_live_state(repo_root, contract)
    generation = tick._load(repo_root / contract["clockwork_root"] / tick.GENERATION_NAME)
    if (state.get("event_kind") != EVENT
        or generation.get("goal_update", {}).get("intent") != _intent(prepared["intent"])
        or generation.get("generation_id") != prepared["generation_manifest"].get("generation_id")
        or prepared["pointer"].get("selected_generation_id") != state.get("generation_id")):
        tick._reject("goal_update_idempotent_collision")
    return state
